import os
import re
import shutil
import subprocess
import sys

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QTableView, QApplication
from construct import Struct, Bytes, Int32ul, Int64ul, PaddedString, StreamError
from qfluentwidgets import ProgressBar, qconfig

from misc.Config import cfg, LogLevel
from model.PreviewTableModel import FileEntry


def is_ignored(file):
    # File is the full path to the file, so we need to perform a full matching and a partial matching based
    # on the file name
    # Case 1 - Full path matching
    if os.path.abspath(file) in cfg.ignored.value:
        return True
    # Case 2 - Partial matching
    base_name = os.path.basename(file)
    for ignored in qconfig.get(cfg.ignored):
        if '{' in ignored and '}' in ignored:
            # Regex pattern
            pattern = ignored.split('{')[1].split('}')[0]
            if re.fullmatch(pattern, base_name):
                return True
        if ignored in base_name:
            return True
    return False


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


header_struct = Struct(
    'magic' / Bytes(4),
    'version' / Int32ul,
    'type' / PaddedString(4, 'utf8'),
    'file_count' / Int32ul,
    'names_offset' / Int64ul,
)

units = {'B': 1, 'KB': 1000, 'MB': 1000 ** 2, 'GB': 1000 ** 3, 'TB': 1000 ** 4}


def parse_size(size):
    if not (size[-1] == 'b' or size[-1] == 'B'):
        size = size + 'B'
    size = size.upper()
    if not re.match(r' ', size):
        size = re.sub(r'([KMGT]?B)', r' \1', size)
    try:
        number, unit = [string.strip() for string in size.split()]
        return int(float(number) * units[unit])
    except ValueError:
        return -1


# Return all ba2 in the folder that contain one of the given postfixes
# Note: it scans for exactly the second-tier directories under the given directory (aka the mod folders)
# This is to avoid scanning for ba2 that will not be loaded to the game anyways
def scan_for_ba2(path, postfixes):
    all_ba2 = []
    for d in os.listdir(path):
        full_path = os.path.join(path, d)
        # Skip files
        if not os.path.isdir(full_path):
            continue
        # List all files under the mod
        for ba2 in os.listdir(full_path):
            fpath = os.path.join(full_path, ba2)
            # Add only *.ba2 archives that contains one of the specified postfixes
            if any([postfix in ba2.lower() for postfix in postfixes]):
                all_ba2.append(fpath)

    return all_ba2


# A convenience function to return the number of files in a ba2 archive
def num_files_in_ba2(file):
    with open(file, 'rb') as fs:
        try:
            result = header_struct.parse_stream(fs)
            return result.file_count
        except StreamError as e:
            QApplication.instance().log_view.add_log(f'Error parsing {file}: {e}', LogLevel.WARNING)
            return -1


def extract_ba2(file, bsab_exe_path):
    cfg_path = qconfig.get(cfg.extraction_path_card)
    if cfg_path:
        if os.path.isabs(cfg_path):
            extraction_path = cfg_path
        else:
            extraction_path = os.path.join(os.path.dirname(file), cfg_path)
    else:
        extraction_path = os.path.dirname(file)

    if not os.path.isdir(extraction_path):
        os.makedirs(extraction_path)

    args = [
        bsab_exe_path,
        '-e',
        file,
        extraction_path
    ]
    proc = subprocess.run(args, text=True, capture_output=True)
    if proc.returncode != 0:
        QApplication.instance().log_view.add_log(f'Error extracting {file}', LogLevel.WARNING)
        return -1
    else:
        QApplication.instance().log_view.add_log(f'{proc.stdout}', LogLevel.INFO)
        return 0


# A function-turned-thread to prevent main UI lockup
class BsaProcessor(QThread):
    done_processing = Signal(list)

    def __init__(self, mod_folder, _parent):
        super().__init__()

        self._path = mod_folder
        self._parent = _parent

    def run(self):
        ba2_paths = scan_for_ba2(self._path, cfg.postfixes.value)

        num_failed = 0
        num_ignored = 0
        num_success = 0
        temp = []
        # Populate ba2 files and their properties
        for f in ba2_paths:
            _dir = os.path.basename(os.path.dirname(f))
            name = os.path.basename(f)
            size = os.stat(f).st_size
            num_files = num_files_in_ba2(f)
            # Auto ignore the blacklisted file if set so
            if is_ignored(f):
                num_ignored += 1
                QApplication.instance().log_view.add_log(f'Ignoring {f}', LogLevel.INFO)
            elif num_files == -1:
                num_failed += 1
                if cfg.ignore_bad_files:
                    self._parent.failed.add(os.path.abspath(f))
            else:
                num_success += 1
                temp.append(FileEntry(name, size, num_files, _dir, f))

        temp = sorted(temp, key=lambda entry: entry.file_size)
        self._parent.file_data = temp
        self.done_processing.emit([self._parent, num_success, num_failed, num_ignored])


class BsaExtractor(QThread):
    done_processing = Signal(list)

    def __init__(self, parent):
        super().__init__()
        self._parent = parent

    def run(self):
        table: QTableView = self._parent.preview_table
        progress: ProgressBar = self._parent.preview_progress
        failed: set = self._parent.failed

        progress.show()
        progress.setMaximum(table.model().rowCount())

        table_idx = 0
        ok_count = 0
        failed_count = 0

        for i in range(table.model().rowCount()):
            path = table.model().sourceModel().raw_data()[table_idx].full_path
            if extract_ba2(path, resource_path('bin/bsab.exe')) == -1:
                if cfg.ignore_bad_files.value:
                    failed.add(os.path.abspath(path))
                # Highlight the failed files in the table
                source_idx = table.model().mapToSource(table.model().index(table_idx, 0))
                table.model().sourceModel().add_bad_file(source_idx.row())
                progress.error()
                failed_count += 1
            else:
                # Back up the file if user requests so
                if cfg.auto_backup.value:
                    cfg_path = qconfig.get(cfg.backup_path_card)
                    if cfg_path:
                        if os.path.isabs(cfg_path):
                            backup_path = cfg_path
                        else:
                            backup_path = os.path.join(os.path.dirname(path), cfg_path)
                    else:
                        backup_path = os.path.join(os.path.dirname(path), 'backup')

                    if not os.path.isdir(backup_path):
                        os.makedirs(backup_path)
                    shutil.move(path, os.path.join(backup_path, os.path.basename(path)))
                else:
                    os.remove(path)
                # Remove the row from the preview
                table.hideRow(table_idx)
                ok_count += 1
            table_idx += 1
            progress.setValue(progress.value() + 1)

        self.done_processing.emit([ok_count, failed_count])

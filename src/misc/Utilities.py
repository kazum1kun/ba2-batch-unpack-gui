import os
import re
import subprocess

from PySide6.QtWidgets import QApplication, QTableView
from PySide6.QtGui import QBrush, QColor
from construct import Struct, Bytes, Int32ul, Int64ul, PaddedString

from misc.Config import cfg

from PySide6.QtCore import QThread, QSortFilterProxyModel, Qt, Signal
from qfluentwidgets import TableView, qconfig, ProgressBar, InfoBar, InfoBarPosition

from model.PreviewTableModel import PreviewTableModel, FileEntry


units = {'B': 1, 'KB': 1000, 'MB': 1000 ** 2, 'GB': 1000 ** 3, 'TB': 1000 ** 4}


header_struct = Struct(
    "magic" / Bytes(4),
    "version" / Int32ul,
    "type" / PaddedString(4, "utf8"),
    "file_count" / Int32ul,
    "names_offset" / Int64ul,
)


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
        result = header_struct.parse_stream(fs)
        return result.file_count
    # args = [
    #     bsab_path,
    #     '-l:N',
    #     file
    # ]
    # proc = subprocess.run(args, capture_output=True)
    # if proc.returncode == 0:
    #     results = proc.stdout
    #     return str(results).count('\\n') - 1
    # else:
    #     print(f'{file} fails to open!')
    #     return -1


def extract_ba2(file, bsab_exe_path):
    base_path = os.path.dirname(file)
    args = [
        bsab_exe_path,
        '-e',
        file,
        base_path
    ]
    proc = subprocess.run(args)
    if proc.returncode != 0:
        print(f'{file} fails to open!')
        return -1
    else:
        return 0


# A function-turned-thread to prevent main UI lockup
class BsaProcessor(QThread):
    done_processing = Signal(list)

    def __init__(self, mod_folder, bsab_path, _parent):
        super().__init__()

        self._path = mod_folder
        self._bsab_path = bsab_path
        self._view = _parent.preview_table
        self._prog_bar = _parent.preview_progress
        self._parent = _parent

    def run(self):
        ba2_paths = scan_for_ba2(self._path, cfg.postfixes.value)
        self._prog_bar.setHidden(False)
        self._prog_bar.setRange(0, len(ba2_paths))

        num_fail = 0
        num_success = 0
        temp = []
        # Populate ba2 files and their properties
        for f in ba2_paths:
            _dir = os.path.basename(os.path.dirname(f))
            name = os.path.basename(f)
            size = os.stat(f).st_size
            num_files = num_files_in_ba2(f)
            # Auto ignore the broken file if set so
            if name.lower() in cfg.ignored.value:
                # temp = cfg.ignored.value
                # temp.append(name.lower())
                # qconfig.set(cfg.ignored, temp)

                # Update the ignored items accordingly
                # QApplication.instance().ignore_changed.emit()
                # self._prog_bar.error()
                num_fail += 1

                # Add the failed item for display
                self._parent.failed_files.append(name)
            else:
                num_success += 1
                temp.append(FileEntry(name, size, num_files, _dir, f))

            # Update the progress bar
            # self._prog_bar.setValue(self._prog_bar.value()+1)

        temp = sorted(temp, key=lambda entry: entry.file_size)
        self._parent.file_data = temp
        self.done_processing.emit([num_success, num_fail])


class BsaExtractor(QThread):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent

    def run(self):
        table: QTableView = self._parent.preview_table
        progress: ProgressBar = self._parent.preview_progress
        failed: list = self._parent.failed

        progress.setMaximum(table.model().rowCount())

        relative_idx = 0
        absolute_idx = 0
        for i in range(table.model().rowCount()):
            path = table.model().index(absolute_idx, 4).data()
            if extract_ba2(path, './bin/bsab.exe') == -1:
                failed.append(os.path.abspath(path))
                for j in range(table.model().columnCount()):
                    table.model().setData(table.model().index(absolute_idx, j), QColor(Qt.GlobalColor.darkRed),
                                          Qt.ItemDataRole.BackgroundRole)
                table.hideRow(relative_idx)
                relative_idx += 1
            absolute_idx += 1
            progress.setValue(progress.value()+1)

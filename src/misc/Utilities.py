import os
import re
import subprocess

from PySide6.QtWidgets import QApplication

from misc.Config import cfg

from PySide6.QtCore import QThread, QSortFilterProxyModel, Qt, Signal
from qfluentwidgets import TableView, qconfig, ProgressBar, InfoBar, InfoBarPosition

from model.PreviewTableModel import PreviewTableModel


units = {'B': 1, 'KB': 2 ** 10, 'MB': 2 ** 20, 'GB': 2 ** 30, 'TB': 2 ** 40}


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
def num_files_in_ba2(bsab_path, file):
    args = [
        bsab_path,
        '-l:N',
        file
    ]
    proc = subprocess.run(args, capture_output=True)
    if proc.returncode == 0:
        results = proc.stdout
        return str(results).count('\\n') - 1
    else:
        print(f'{file} fails to open!')
        return -1


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

        model = PreviewTableModel()

        proxy_model = QSortFilterProxyModel(model)
        proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        proxy_model.setSourceModel(model)

        self._view.setModel(proxy_model)

        # Clear the cached "bad files" in main screen
        self._parent.failed_files.clear()

        num_fail = 0
        num_success = 0
        # Populate ba2 files and their properties
        for f in ba2_paths:
            _dir = os.path.basename(os.path.dirname(f))
            name = os.path.basename(f)
            size = os.stat(f).st_size
            num_files = num_files_in_ba2('./bin/bsab.exe', f)
            # Auto ignore the broken file if set so
            if num_files == -1 and name.lower() not in cfg.ignored.value:
                temp = cfg.ignored.value
                temp.append(name.lower())
                qconfig.set(cfg.ignored, temp)

                # Update the ignored items accordingly
                QApplication.instance().ignore_changed.emit()
                self._prog_bar.error()
                num_fail += 1

                # Add the failed item for display
                self._parent.failed_files.append(name)
            else:
                num_success += 1
            model.append_row([_dir, name, size, num_files])


            # Update the progress bar
            self._prog_bar.setValue(self._prog_bar.value()+1)

        self.done_processing.emit([num_success, num_fail])
        # ba2_dirs = [os.path.basename(os.path.dirname(f)) for f in ba2_paths]
        # ba2_filenames = [os.path.basename(f) for f in ba2_paths]
        # ba2_sizes = [os.stat(f).st_size for f in ba2_paths]
        # ba2_num_files = [num_files_in_ba2('./bin/bsab.exe', f) for f in ba2_paths]
        # ba2_ignored = [False for f in ba2_paths]

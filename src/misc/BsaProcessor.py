import os

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication

from misc.Config import cfg, LogLevel
from misc.Utilities import scan_for_ba2, num_files_in_ba2, is_ignored
from model.PreviewTableModel import FileEntry


class BsaProcessor(QThread):
    done_processing = Signal(list)

    def __init__(self, mod_folder, _parent):
        super().__init__()

        self._path = mod_folder
        self._parent = _parent

    def run(self):
        ba2_paths = scan_for_ba2(self._path, cfg.get(cfg.postfixes))

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

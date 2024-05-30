import os.path

from PySide6.QtCore import QThread, Signal

from misc.Utilities import scan_for_ba2, list_ba2, resource_path, extract_ba2


class BsaChecker(QThread):
    done_processing = Signal(list)
    issue_found = Signal(str)

    def __init__(self, parent, path, deep_scan=False):
        super().__init__()
        self._parent = parent
        # self.progress = self._parent.preview_progress
        self.path = path
        self.deep_scan = deep_scan

    def run(self):
        ba2_paths = scan_for_ba2(self.path, ['.ba2'])
        num_failed = 0
        num_ok = 0

        # self.progress.setMaximum(len(ba2_paths))

        for f in ba2_paths:
            if not self.deep_scan:
                result = list_ba2(f, resource_path('bin/BSArch.exe'))
            else:
                result = extract_ba2(f, resource_path('bin/BSArch.exe'), use_temp=True)
            if result != 0:
                num_failed += 1
                self.issue_found.emit(os.path.abspath(f))
                # self.progress.error()
            else:
                num_ok += 1
            # self.progress.setValue(self.progress.value() + 1)

        self.done_processing.emit([self._parent, num_ok, num_failed])

import os
import shutil

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QTableView
from qfluentwidgets import ProgressBar

from misc.Config import cfg
from misc.Utilities import extract_ba2, resource_path


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
            if extract_ba2(path, resource_path('bin/BSArch.exe')) == -1:
                if cfg.get(cfg.ignore_bad_files):
                    failed.add(os.path.abspath(path))
                # Highlight the failed files in the table
                source_idx = table.model().mapToSource(table.model().index(table_idx, 0))
                table.model().sourceModel().add_bad_file(source_idx.row())
                progress.error()
                failed_count += 1
            else:
                # Back up the file if user requests so
                if cfg.get(cfg.auto_backup):
                    cfg_path = cfg.get(cfg.backup_path)
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

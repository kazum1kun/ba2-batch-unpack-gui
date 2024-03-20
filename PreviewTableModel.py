from PySide6 import QtCore
from PySide6.QtCore import Qt


class PreviewTableModel(QtCore.QAbstractTableModel):
    def __init__(self, ba2_dirs, ba2_filenames, ba2_sizes, ba2_num_files, ba2_ignored):
        super(PreviewTableModel, self).__init__()
        self._ba2_dirs = ba2_dirs
        self._ba2_filenames = ba2_filenames
        self._ba2_sizes = ba2_sizes
        self._ba2_num_files = ba2_num_files
        self._ba2_ignored = ba2_ignored

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            # Assumes the following layout
            # File Name, File Size, # Files, Path, Ignored
            if index.column() == 0:
                return self._ba2_filenames[index.row()]
            elif index.column() == 1:
                return self._ba2_sizes[index.row()]
            elif index.column() == 2:
                return self._ba2_num_files[index.row()]
            elif index.column() == 3:
                return self._ba2_dirs[index.row()]
            elif index.column() == 4:
                return ''
        elif role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 4:
                if self._ba2_ignored[index.row()]:
                    return Qt.CheckState.Checked
                else:
                    return Qt.CheckState.Unchecked

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 4:
            if Qt.CheckState(value) == Qt.CheckState.Checked:
                self._ba2_ignored[index.row()] = True
            else:
                self._ba2_ignored[index.row()] = False
        return True

    def flags(self, index):
        if not index.isValid():
            return None

        if index.column() == 4:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, _parent=None):
        # The length of the outer list.
        return len(self._ba2_filenames)

    def columnCount(self, _parent=None):
        return 5

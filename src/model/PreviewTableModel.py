from typing import NamedTuple

from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QBrush, QColor

from humanize import naturalsize


class FileEntry(NamedTuple):
    file_name: str
    file_size: int
    num_files: int
    dir_name: str


class PreviewTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data: list[FileEntry]):
        super(PreviewTableModel, self).__init__()
        self.files: list[FileEntry] = data
        self.bad_ba2_idx: list[int] = []
        self.horizontalHeader = ['File Name', 'File Size', '# Files', 'Mod']

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole or role == Qt.ItemDataRole.UserRole:
            # Assumes the following layout
            # File Name, File Size, # Files, Path, Ignored
            if index.column() == 0:
                return self.files[index.row()].file_name
            elif index.column() == 1:
                if role == Qt.ItemDataRole.UserRole:
                    return self.files[index.row()].file_size
                return naturalsize(self.files[index.row()].file_size)
            elif index.column() == 2:
                return self.files[index.row()].num_files
            elif index.column() == 3:
                return self.files[index.row()].dir_name
            elif index.column() == 4:
                return ''
        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.row() in self.bad_ba2_idx:
                # Dark red
                return QBrush(QColor(139, 0, 0))
        # elif role == Qt.ItemDataRole.CheckStateRole:
        #     if index.column() == 4:
        #         if self._ba2_ignored[index.row()]:
        #             return Qt.CheckState.Checked
        #         else:
        #             return Qt.CheckState.Unchecked
        # elif role == Qt.ItemDataRole.TextAlignmentRole:
        #     if index.column() == 4:
        #         return Qt.AlignmentFlag.AlignCenter

        return None

    # def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
    #     if not index.isValid():
    #         return False
    #     if role == Qt.ItemDataRole.CheckStateRole and index.column() == 4:
    #         if Qt.CheckState(value) == Qt.CheckState.Checked:
    #             self._ba2_ignored[index.row()] = True
    #         else:
    #             self._ba2_ignored[index.row()] = False
    #     return True


    # def delete_row(self, index: QModelIndex):
    #     self.beginRemoveRows(index.parent(), index.row(), index.row())
    #     del self._ba2_dirs[index.row()]
    #     del self._ba2_filenames[index.row()]
    #     del self._ba2_sizes[index.row()]
    #     del self._ba2_num_files[index.row()]
    #     self.endRemoveRows()

    # def size_at(self, index):
    #     if len(self._ba2_sizes) > index:
    #         return self._ba2_sizes[index]
    #     else:
    #         return -1

    def flags(self, index):
        if not index.isValid():
            return None

        if index.column() == 4:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, _parent=None):
        # The length of the outer list.
        return len(self.files)

    def columnCount(self, _parent=None):
        return 4

    def headerData(self, section, orientation, role=...):
        if role == Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
            return self.horizontalHeader[section]
        return None

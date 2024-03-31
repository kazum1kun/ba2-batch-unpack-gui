from PySide6 import QtCore
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QBrush, QColor

from humanize import naturalsize


class PreviewTableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super(PreviewTableModel, self).__init__()
        self._ba2_dirs = []
        self._ba2_filenames = []
        self._ba2_sizes = []
        self._ba2_num_files = []
        self.bad_ba2_idx = []
        # self._ba2_ignored = ba2_ignored
        # self.horizontalHeader = ['File Name', 'File Size', '# Files', 'Mod', 'Ignored']
        self.horizontalHeader = ['File Name', 'File Size', '# Files', 'Mod']

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole or role == Qt.ItemDataRole.UserRole:
            # Assumes the following layout
            # File Name, File Size, # Files, Path, Ignored
            if index.column() == 0:
                return self._ba2_filenames[index.row()]
            elif index.column() == 1:
                if role == Qt.ItemDataRole.UserRole:
                    return self._ba2_sizes[index.row()]
                return naturalsize(self._ba2_sizes[index.row()])
            elif index.column() == 2:
                return self._ba2_num_files[index.row()]
            elif index.column() == 3:
                return self._ba2_dirs[index.row()]
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

    # data=[ba2_dir, ba2_filename, ba2_size, ba2_num_file]
    def append_row(self, data):
        target_row = len(self._ba2_dirs)
        self.beginInsertRows(QModelIndex(), target_row, target_row)
        self._ba2_dirs.append(data[0])
        self._ba2_filenames.append(data[1])
        self._ba2_sizes.append(data[2])
        self._ba2_num_files.append(data[3])
        if data[3] == -1:
            self.bad_ba2_idx.append(target_row)
        self.endInsertRows()

    def delete_row(self, index: QModelIndex):
        self.beginRemoveRows(index.parent(), index.row(), index.row())
        del self._ba2_dirs[index.row()]
        del self._ba2_filenames[index.row()]
        del self._ba2_sizes[index.row()]
        del self._ba2_num_files[index.row()]
        self.endRemoveRows()

    def size_at(self, index):
        if len(self._ba2_sizes) > index:
            return self._ba2_sizes[index]
        else:
            return -1

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
        return 4

    def headerData(self, section, orientation, role=...):
        if role == Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
            return self.horizontalHeader[section]
        return None

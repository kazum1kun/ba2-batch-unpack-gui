from typing import NamedTuple

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from humanize import naturalsize


class FileEntry(NamedTuple):
    file_name: str
    file_size: int
    num_files: int
    dir_name: str
    full_path: str


class PreviewTableModel(QtCore.QAbstractTableModel):
    # Data is assumed to be sorted according to their file size
    def __init__(self, data: list[FileEntry]):
        super(PreviewTableModel, self).__init__()
        self.files: list[FileEntry] = data
        self.bad_ba2_idx: list[int] = []
        self.horizontalHeader = [self.tr('File Name'), self.tr('File Size'), self.tr('# Files'), self.tr('Mod')]

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
                return self.files[index.row()].full_path
        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.row() in self.bad_ba2_idx:
                # Dark red
                return QBrush(QColor(139, 0, 0))
        return None

    def raw_data(self):
        return self.files

    def add_bad_file(self, index):
        self.bad_ba2_idx.append(index)

    def size_at(self, index):
        if len(self.files) > index:
            return self.files[index].file_size
        else:
            return -1

    def flags(self, index):
        if not index.isValid():
            return None

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def rowCount(self, _parent=None):
        # The length of the outer list.
        return len(self.files)

    def columnCount(self, _parent=None):
        return 4

    def headerData(self, section, orientation, role=...):
        if role == Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
            return self.horizontalHeader[section]
        return None

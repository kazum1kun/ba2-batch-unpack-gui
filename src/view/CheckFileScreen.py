import os.path

from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QFileDialog, QHeaderView, QBoxLayout, QAbstractItemView
from qfluentwidgets import FluentIcon as Fi, TableView, PrimaryPushButton, \
    StrongBodyLabel, RoundMenu, Action, BodyLabel
from qfluentwidgets import (SubtitleLabel, LineEdit, ToolButton,
                            TogglePushButton, ToolTipFilter)


class CheckFileScreen(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('CheckFileScreen')
        self.layout = QVBoxLayout(self)


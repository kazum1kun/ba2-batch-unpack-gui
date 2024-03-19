from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout
from qfluentwidgets import (SubtitleLabel, setFont)


class SettingsScreen(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel('Settings', self)
        self.layout = QHBoxLayout(self)
        self.setObjectName('SettingsScreen')

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label, 1, Qt.AlignCenter)

        self.layout.setContentsMargins(0, 32, 0, 0)

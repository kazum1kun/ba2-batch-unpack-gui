from typing import List, Union

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QLabel,
                               QHBoxLayout, QSizePolicy, QFileDialog)
from qfluentwidgets import ExpandSettingCard, ConfigItem, FluentIconBase, PushButton, qconfig, LineEdit, TeachingTip, \
    InfoBarIcon, TeachingTipTailPosition, ToolButton, ToolTipFilter, SettingCard
from qfluentwidgets import FluentIcon as Fi


class InputSettingCard(SettingCard):
    """ A setting card with a line input """

    def __init__(self, config_item: ConfigItem, icon: Union[str, QIcon, FluentIconBase], title: str,
                 content: str = None, parent=None):
        """
        Parameters
        ----------
        config_item: ConfigItem
            configuration item operated by the card

        icon:
            card icon

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        content: str
            the content of card
        """
        super().__init__(icon, title, content, parent)

        self.input = LineEdit(self)
        self.button = ToolButton(Fi.FOLDER, self)

        self.hBoxLayout.addWidget(self.input)
        self.hBoxLayout.addSpacing(10)
        self.hBoxLayout.addWidget(self.button)
        self.hBoxLayout.addSpacing(16)

        self.config_item = config_item
        if config_item:
            self.setValue(qconfig.get(config_item))

        self.input.setMinimumWidth(250)
        self.input.setText(qconfig.get(config_item))
        self.input.setPlaceholderText(self.tr('Enter or choose a folder'))
        self.button.setToolTip(self.tr('Choose a folder'))

        self.input.textChanged.connect(lambda: self.setValue(self.input.text()))
        self.button.clicked.connect(self.__open_folder)

    def setValue(self, value):
        if self.config_item:
            qconfig.set(self.config_item, value)

    def __open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr('Choose a folder'),
                                                  options=QFileDialog.Option.ShowDirsOnly |
                                                  QFileDialog.Option.DontResolveSymlinks)
        if folder:
            self.input.setText(folder)

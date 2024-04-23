from typing import Union

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QFileDialog)
from qfluentwidgets import ConfigItem, FluentIconBase, qconfig, LineEdit, ToolButton, SettingCard
from qfluentwidgets import FluentIcon as Fi


class InputSettingCard(SettingCard):
    """ A setting card with a line input """

    def __init__(self, config_item: ConfigItem, icon: Union[str, QIcon, FluentIconBase], title: str,
                 content: str = None, parent=None, extensions=None, folder=True,
                 options=QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks):
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

        self.extensions = extensions
        self.input = LineEdit(self)
        self.button = ToolButton(Fi.FOLDER, self)

        self.hBoxLayout.addWidget(self.input)
        self.hBoxLayout.addSpacing(10)
        self.hBoxLayout.addWidget(self.button)
        self.hBoxLayout.addSpacing(16)

        self.options = options

        self.config_item = config_item
        if config_item:
            self.setValue(qconfig.get(config_item))

        self.input.setText(qconfig.get(config_item))
        self.input.setPlaceholderText(self.tr('Enter or choose a folder'))
        self.button.setToolTip(self.tr('Choose a folder'))

        self.input.textChanged.connect(lambda: self.setValue(self.input.text()))

        if folder:
            self.button.clicked.connect(self.__open_folder)
        else:
            self.button.clicked.connect(self.__open_file)

    def setValue(self, value):
        if self.config_item:
            qconfig.set(self.config_item, value)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.input.setMinimumWidth(self.width() - 450)

    def __open_file(self):
        _filter = ';;'.join([f'{ext} files (*.{ext})' for ext in self.extensions] + ['All files (*)'])
        file, _ = QFileDialog.getOpenFileName(self, self.tr('Choose a ba2 utility'), filter=_filter)
        if file:
            self.input.setText(file)

    def __open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr('Choose a folder'), options=self.options)
        if folder:
            self.input.setText(folder)

from typing import List, Union

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QLabel,
                               QHBoxLayout, QSizePolicy)
from qfluentwidgets import ExpandSettingCard, ConfigItem, FluentIconBase, PushButton, qconfig, LineEdit, TeachingTip, \
    InfoBarIcon, TeachingTipTailPosition, ToolButton, ToolTipFilter
from qfluentwidgets import FluentIcon as Fi


class IgnoredItem(QWidget):
    """ Ignored item """
    removed = Signal(QWidget)

    def __init__(self, ignored: str, parent=None):
        super().__init__(parent=parent)
        self.ignored = ignored
        self.item_layout = QHBoxLayout(self)
        self.ignored_label = QLabel(ignored, self)
        self.remove_button = ToolButton(Fi.CLOSE, self)

        self.remove_button.setFixedSize(39, 29)
        self.remove_button.setIconSize(QSize(12, 12))

        self.setFixedHeight(53)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.item_layout.setContentsMargins(48, 0, 60, 0)

        self.item_layout.addWidget(self.ignored_label, 0, Qt.AlignLeft)
        self.item_layout.addSpacing(16)
        self.item_layout.addStretch(1)
        self.item_layout.addWidget(self.remove_button, 0, Qt.AlignRight)
        self.item_layout.setAlignment(Qt.AlignVCenter)

        self.remove_button.clicked.connect(
            lambda: self.removed.emit(self))


class IgnoredSettingCard(ExpandSettingCard):
    """ Ignored files setting card """

    ignored_changed = Signal(list)

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

        parent: QWidget
            parent widget
        """

        super().__init__(icon, title, content, parent)
        self.config_item = config_item
        self.clear_ignored_button = ToolButton(Fi.BROOM, self)
        self.new_ignored_input = LineEdit(self)
        self.add_ignored_button = PushButton(self.tr('Add'), self, Fi.ADD)

        self.ignored = qconfig.get(config_item).copy()  # type:List[str]
        self.ignored_cards = []

        self.__initWidget()

    def __initWidget(self):
        self.setExpand(True)

        # initialize layout
        self.addWidget(self.clear_ignored_button)
        self.addWidget(self.new_ignored_input)
        self.addWidget(self.add_ignored_button)

        self.viewLayout.setSpacing(0)
        self.viewLayout.setAlignment(Qt.AlignTop)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        for i in self.ignored:
            self.__add_ignored_item(i)

        self.clear_ignored_button.setToolTip(self.tr('Clear all'))
        self.clear_ignored_button.installEventFilter(ToolTipFilter(self.clear_ignored_button))
        self.clear_ignored_button.clicked.connect(self.__clear_ignored)
        self.new_ignored_input.setPlaceholderText(self.tr('Ignored file'))
        self.add_ignored_button.clicked.connect(self.__add_ignored)

    def __add_ignored(self, name=None):
        if not name:
            # Validate input
            new_ignored = self.new_ignored_input.text()
            if len(new_ignored) <= 0:
                self.__show_ignore_failed_tip()
                return
            if new_ignored in self.ignored:
                self.__show_ignore_duplicate_tip()
                return
            name = new_ignored

        self.__add_ignored_item(name)
        self.ignored.append(name)
        self.new_ignored_input.clear()
        qconfig.set(self.config_item, self.ignored)
        self.ignored_changed.emit(self.ignored)

    def __add_ignored_item(self, ignored: str):
        """ add folder item """
        item = IgnoredItem(ignored, self.view)
        item.removed.connect(lambda: self.__remove_ignored(item))
        self.viewLayout.addWidget(item)
        self.ignored_cards.append(item)
        item.show()
        self._adjustViewSize()

    def __ignored_updated(self):
        ignore_backup = qconfig.get(self.config_item).copy()

        self.__clear_ignored()

        self.ignored = ignore_backup.copy()
        for i in self.ignored:
            self.__add_ignored_item(i)
        qconfig.set(self.config_item, ignore_backup)

    # def __show_confirm_dialog(self, item: PostfixItem):
    #     """ show confirm dialog """
    #     name = Path(item.folder).name
    #     title = self.tr('Are you sure you want to delete the folder?')
    #     content = self.tr("If you delete the ") + f'"{name}"' + \
    #         self.tr(" folder and remove it from the list, the folder will no "
    #                 "longer appear in the list, but will not be deleted.")
    #     w = Dialog(title, content, self.window())
    #     w.yesSignal.connect(lambda: self.__removeFolder(item))
    #     w.exec_()

    def __remove_ignored(self, item: IgnoredItem):
        """ remove ignored """
        if item.ignored not in self.ignored:
            return

        self.ignored.remove(item.ignored)
        self.ignored_cards.remove(item)
        self.viewLayout.removeWidget(item)
        item.deleteLater()
        self._adjustViewSize()

        self.ignored_changed.emit(self.ignored)
        qconfig.set(self.config_item, self.ignored)

    def __clear_ignored(self):
        for card in self.ignored_cards[:]:
            self.__remove_ignored(card)

    def __show_ignore_failed_tip(self):
        TeachingTip.create(
            target=self.new_ignored_input,
            icon=InfoBarIcon.ERROR,
            title=self.tr('Check your input'),
            content=self.tr('Please enter something'),
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def __show_ignore_duplicate_tip(self):
        TeachingTip.create(
            target=self.new_ignored_input,
            icon=InfoBarIcon.ERROR,
            title=self.tr('Duplicate'),
            content=self.tr('Your input is a duplicate of an existing ignore'),
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

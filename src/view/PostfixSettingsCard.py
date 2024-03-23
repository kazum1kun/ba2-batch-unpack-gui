from typing import List, Union

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtWidgets import (QPushButton, QFileDialog, QWidget, QLabel,
                               QHBoxLayout, QToolButton, QSizePolicy)
from qfluentwidgets import ExpandSettingCard, ConfigItem, FluentIconBase, PushButton, qconfig, LineEdit, TeachingTip, \
    InfoBarIcon, TeachingTipTailPosition, ToolButton
from qfluentwidgets import FluentIcon as Fi


class PostfixItem(QWidget):
    """ Postfix item """
    removed = Signal(QWidget)

    def __init__(self, postfix: str, parent=None):
        super().__init__(parent=parent)
        self.postfix = postfix
        self.item_layout = QHBoxLayout(self)
        self.postfix_label = QLabel(postfix, self)
        self.remove_button = ToolButton(Fi.CLOSE, self)

        self.remove_button.setFixedSize(39, 29)
        self.remove_button.setIconSize(QSize(12, 12))

        self.setFixedHeight(53)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.item_layout.setContentsMargins(48, 0, 60, 0)
        self.item_layout.addWidget(self.postfix_label, 0, Qt.AlignLeft)
        self.item_layout.addSpacing(16)
        self.item_layout.addStretch(1)
        self.item_layout.addWidget(self.remove_button, 0, Qt.AlignRight)
        self.item_layout.setAlignment(Qt.AlignVCenter)

        self.remove_button.clicked.connect(
            lambda: self.removed.emit(self))


class PostfixSettingCard(ExpandSettingCard):
    """ Postfix list setting card """

    postfix_changed = Signal(list)

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
        self.postfix_reset_button = ToolButton(Fi.CANCEL, self)
        self.postfix_input = LineEdit(self)
        self.add_postfix_button = PushButton(self.tr('Add'), self, Fi.ADD)

        self.postfixes = qconfig.get(config_item).copy()   # type:List[str]
        self.postfixes_cards = []
        self.__initWidget()

    def __initWidget(self):
        self.setExpand(True)

        # initialize layout
        self.addWidget(self.postfix_reset_button)
        self.addWidget(self.postfix_input)
        self.addWidget(self.add_postfix_button)

        self.viewLayout.setSpacing(0)
        self.viewLayout.setAlignment(Qt.AlignTop)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        for postfix in self.postfixes:
            self.__add_postfix_item(postfix)

        self.postfix_input.setPlaceholderText(self.tr('New postfix'))
        self.postfix_reset_button.setToolTip('Reset to default')
        self.add_postfix_button.clicked.connect(self.__add_postfix)
        self.postfix_reset_button.clicked.connect(self.__reset_postfix)

    def __add_postfix(self):
        # Validate input
        user_postfix = self.postfix_input.text()
        if len(user_postfix) < 4 or user_postfix[-4:] != '.ba2':
            self.__show_ba2_failed_tip()

        self.__add_postfix_item(user_postfix.lower())
        self.postfixes.append(user_postfix.lower())
        self.postfix_input.clear()
        qconfig.set(self.config_item, self.postfixes)
        self.postfix_changed.emit(self.postfixes)

    def __add_postfix_item(self, postfix: str):
        """ add postfix item """
        item = PostfixItem(postfix, self.view)
        item.removed.connect(lambda: self.__remove_postfix(item))
        self.viewLayout.addWidget(item)
        item.show()
        self.postfixes_cards.append(item)
        self._adjustViewSize()

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

    def __remove_postfix(self, item: PostfixItem):
        """ remove folder """
        if item.postfix not in self.postfixes:
            return

        self.postfixes.remove(item.postfix)
        self.viewLayout.removeWidget(item)
        item.deleteLater()
        self._adjustViewSize()

        self.postfix_changed.emit(self.postfixes)
        qconfig.set(self.config_item, self.postfixes)

    def __reset_postfix(self):
        for card in self.postfixes_cards[:]:
            self.__remove_postfix(card)
        for postfix in self.config_item.defaultValue:
            self.__add_postfix_item(postfix)
            self.postfixes.append(postfix)
            qconfig.set(self.config_item, self.postfixes)
            self.postfix_changed.emit(self.postfixes)

    def __show_ba2_failed_tip(self):
        TeachingTip.create(
            target=self.postfix_input,
            icon=InfoBarIcon.ERROR,
            title=self.tr('Check your input'),
            content=self.tr('Make sure your input contains \".ba2\" in the end'),
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def __show_ba2_duplicate_tip(self):
        TeachingTip.create(
            target=self.postfix_input,
            icon=InfoBarIcon.ERROR,
            title=self.tr('Duplicate'),
            content=self.tr('Your input is a duplicate of an existing postfix'),
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

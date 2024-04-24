from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QApplication
from qfluentwidgets import FluentIcon as Fi
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, HyperlinkCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, isDarkTheme, setThemeColor)

from misc.Config import cfg, FEEDBACK_URL, CREDITS_URL, KOFI_URL
from misc.Utilities import resource_path, get_default_windows_app
from prefab.CustomIcon import CustomIcon
from view.setting_card.AboutSettingCard import AboutSettingCard
from view.setting_card.IgnoredSettingCard import IgnoredSettingCard
from view.setting_card.InputSettingCard import InputSettingCard
from view.setting_card.PostfixSettingCard import PostfixSettingCard


class SettingScreen(ScrollArea):
    checkUpdateSig = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setObjectName('SettingScreen')

        self.scroll_widget = QWidget()
        self.expand_layout = ExpandLayout(self.scroll_widget)

        # setting label
        self.setting_label = QLabel(self.tr("Settings"), self)

        # extraction
        self.extraction_group = SettingCardGroup(
            self.tr('Extraction'), self.scroll_widget
        )
        self.postfixes_card = PostfixSettingCard(
            cfg.postfixes,
            Fi.TAG,
            self.tr('Postfixes'),
            self.tr('File postfixes to extract from. Example: \"main.ba2\" matches files like\n'
                    '\"xyzmod - Main.ba2\" and \"abcmod - main.BA2\". Must end in \".ba2\"'),
            parent=self.extraction_group
        )
        self.ignored_card = IgnoredSettingCard(
            cfg.ignored,
            Fi.REMOVE_FROM,
            self.tr('Ignored files'),
            self.tr('Any file with filename containing them will not be extracted.\n'
                    'To use regex, wrap the pattern inside {}, e.g. \"{.*[dD]iamond.*}\"'),
            parent=self.extraction_group
        )
        self.ignore_bad_card = SwitchSettingCard(
            Fi.DICTIONARY_ADD,
            self.tr('Ignore bad files'),
            self.tr('Automatically ignore ba2 files that cannot be opened'),
            cfg.ignore_bad_files,
            parent=self.extraction_group
        )
        self.auto_backup_card = SwitchSettingCard(
            Fi.COPY,
            self.tr('Automatic backup'),
            self.tr('Automatically back up ba2 files extracted'),
            cfg.auto_backup,
            parent=self.extraction_group
        )

        # personalization
        self.personal_group = SettingCardGroup(self.tr('Personalization'), self.scroll_widget)
        self.theme_card = ComboBoxSettingCard(
            cfg.themeMode,
            Fi.BRUSH,
            self.tr('Theme'),
            self.tr("Change the theme of the app"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personal_group
        )
        self.theme_color_card = CustomColorSettingCard(
            cfg.themeColor,
            Fi.PALETTE,
            self.tr('Color'),
            self.tr('Change the theme color of the app'),
            self.personal_group
        )
        self.language_card = ComboBoxSettingCard(
            cfg.language,
            Fi.LANGUAGE,
            self.tr('Language'),
            self.tr('Select your preferred language'),
            texts=[self.tr('Use system setting'), 'English', '简体中文', '繁體中文', 'English'],
            parent=self.personal_group
        )

        # update software
        self.update_group = SettingCardGroup(self.tr("Update"), self.scroll_widget)
        self.update_card = SwitchSettingCard(
            Fi.UPDATE,
            self.tr('Check for updates'),
            self.tr('Automatically check and notify you of updates'),
            configItem=cfg.check_update_at_start_up,
            parent=self.update_group
        )

        # Advanced
        self.advanced_group = SettingCardGroup(self.tr('Advanced'), self.scroll_widget)
        self.show_debug_card = SwitchSettingCard(
            Fi.COMMAND_PROMPT,
            self.tr('Show log output'),
            self.tr('Show a separate window with debugging information'),
            cfg.show_debug,
            parent=self.advanced_group
        )

        self.extraction_path_card = InputSettingCard(
            cfg.extraction_path,
            CustomIcon.FOLDER_ARROW_UP,
            self.tr('Extraction path'),
            self.tr('The folder where ba2 files are extracted\n'
                    '(leave empty to extract to the same folder)'),
            self.advanced_group
        )

        self.backup_path_card = InputSettingCard(
            cfg.backup_path,
            Fi.DOCUMENT,
            self.tr('Backup path'),
            self.tr('The folder where ba2 files are backed up\n'
                    '(leave empty to back up to \"backup\" folder in the mod)'),
            self.advanced_group
        )

        self.ext_ba2_card = InputSettingCard(
            cfg.ext_ba2_exe,
            Fi.APPLICATION,
            self.tr('External ba2 tool'),
            self.tr('Path to an external ba2 tool that\'s used for the\n'
                    '\"Open\" command in the table context menu'),
            self.advanced_group,
            ['exe'],
            False
        )

        # application
        self.about_group = SettingCardGroup(self.tr('About'), self.scroll_widget)
        self.about_setting_card = AboutSettingCard(self.about_group)

        self.kofi_card = HyperlinkCard(
            KOFI_URL,
            self.tr('Buy me a coffee'),
            Fi.HEART,
            self.tr('Support me'),
            self.tr('If you like Unpackrr, consider supporting me by buying me a coffee'),
            self.about_group
        )

        self.credits_card = HyperlinkCard(
            CREDITS_URL,
            self.tr('View'),
            Fi.BOOK_SHELF,
            self.tr('Credits'),
            self.tr('Open source software that made Unpackrr possible'),
            self.about_group
        )

        self.pending_update = False

        self.__init_widget()

    def __init_widget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)

        self.ext_ba2_card.input.setPlaceholderText(self.tr('Choose your external ba2 tool'))
        # Not ideal, but doing it in the Config will result in a circular import
        if cfg.get(cfg.first_launch):
            self.ext_ba2_card.input.setText(get_default_windows_app('.ba2'))

        # initialize style sheet
        self.__set_qss()

        # initialize layout
        self.__init_layout()
        self.__connect_signal_to_slot()

    def __init_layout(self):
        self.setting_label.move(60, 63)

        self.extraction_group.addSettingCard(self.postfixes_card)
        self.extraction_group.addSettingCard(self.ignored_card)
        self.extraction_group.addSettingCard(self.ignore_bad_card)
        self.extraction_group.addSettingCard(self.auto_backup_card)

        # add cards to group
        self.personal_group.addSettingCard(self.theme_card)
        self.personal_group.addSettingCard(self.theme_color_card)
        self.personal_group.addSettingCard(self.language_card)

        self.update_group.addSettingCard(self.update_card)

        self.advanced_group.addSettingCard(self.show_debug_card)
        self.advanced_group.addSettingCard(self.extraction_path_card)
        self.advanced_group.addSettingCard(self.backup_path_card)
        self.advanced_group.addSettingCard(self.ext_ba2_card)

        self.about_group.addSettingCard(self.about_setting_card)
        self.about_group.addSettingCard(self.kofi_card)
        self.about_group.addSettingCard(self.credits_card)

        # add setting card group to layout
        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(60, 10, 60, 0)

        self.expand_layout.addWidget(self.extraction_group)
        self.expand_layout.addWidget(self.personal_group)
        self.expand_layout.addWidget(self.update_group)
        self.expand_layout.addWidget(self.advanced_group)
        self.expand_layout.addWidget(self.about_group)

    def showEvent(self, event):
        super().showEvent(event)
        if self.pending_update:
            self.ignored_card.ignored_updated()
            self.pending_update = False

    def notify_ignore(self):
        self.pending_update = True

    def __set_qss(self):
        """ set style sheet """
        self.scroll_widget.setObjectName('scrollWidget')
        self.setting_label.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(resource_path(f'resources/qss/{theme}/setting_interface.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __show_restart_tooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            duration=3000,
            parent=self.window()
        )

    def __on_theme_changed(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__set_qss()

    def __on_theme_color_changed(self, color: str):
        """ theme color changed slot """
        setThemeColor(color)

    def __on_debug_changed(self):
        if cfg.get(cfg.show_debug):
            QApplication.instance().log_view.show()
        else:
            QApplication.instance().log_view.hide()

    def __connect_signal_to_slot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__show_restart_tooltip)
        cfg.themeChanged.connect(self.__on_theme_changed)
        cfg.themeColorChanged.connect(self.__on_theme_color_changed)

        self.show_debug_card.checkedChanged.connect(self.__on_debug_changed)

        # about
        # self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.about_setting_card.feedback_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

        QApplication.instance().ignore_changed.connect(self.notify_ignore)

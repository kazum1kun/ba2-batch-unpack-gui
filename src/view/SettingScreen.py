from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QLabel, QApplication
from qfluentwidgets import FluentIcon as Fi, PushSettingCard
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, isDarkTheme)

from misc.Config import cfg, HELP_URL, CREDITS_URL, AUTHOR, VERSION, YEAR
from view.IgnoredSettingCard import IgnoredSettingCard
from view.PostfixSettingCard import PostfixSettingCard
from view.AboutSettingCard import AboutSettingCard


class SettingsScreen(ScrollArea):
    checkUpdateSig = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setObjectName('SettingsScreen')

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # extraction
        self.extraction_group = SettingCardGroup(
            self.tr('Extraction'), self.scrollWidget
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
            self.tr('Any file with filename containing them will not be extracted'),
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
        self.personalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.themeCard = ComboBoxSettingCard(
            cfg.themeMode,
            Fi.BRUSH,
            self.tr('Theme'),
            self.tr("Change the theme of the app"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            Fi.PALETTE,
            self.tr('Color'),
            self.tr('Change the theme color of the app'),
            self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            Fi.LANGUAGE,
            self.tr('Language'),
            self.tr('Select your preferred language'),
            texts=[self.tr('Use system setting'), 'English', '简体中文', '繁體中文', 'English'],
            parent=self.personalGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(self.tr("Update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            Fi.UPDATE,
            self.tr('Check for updates'),
            self.tr('Automatically check and notify you of updates'),
            configItem=cfg.check_update_at_start_up,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.aboutSettingCard = AboutSettingCard(self.aboutGroup)

        self.credits_card = HyperlinkCard(
            CREDITS_URL,
            self.tr('View'),
            Fi.HEART,
            self.tr('Credits'),
            self.tr('Acknowledgements to those who helped make Unpackrr possible'),
            self.aboutGroup
        )

        # self.feedbackCard = PrimaryPushSettingCard(
        #     self.tr('Provide feedback'),
        #     Fi.FEEDBACK,
        #     self.tr('Provide feedback'),
        #     self.tr('Help us improve Unpackrr by providing feedback'),
        #     self.aboutGroup
        # )
        #
        # self.helpCard = HyperlinkCard(
        #     HELP_URL,
        #     self.tr('Open Nexus'),
        #     Fi.INFO,
        #     self.tr('Nexus'),
        #     self.tr('Check out Unpackrr on Nexus'),
        #     self.aboutGroup
        # )
        # self.aboutCard = HyperlinkCard(
        #     '',
        #     self.tr('Source code'),
        #     Fi.GITHUB,
        #     self.tr('About'),
        #     '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
        #     self.tr('Version') + f" {VERSION}",
        #     self.aboutGroup
        # )

        self.pending_update = False
        self.credits_window = None

        self.__init_widget()

    def __init_widget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__set_qss()

        # initialize layout
        self.__init_layout()
        self.__connect_signal_to_slot()

    def __init_layout(self):
        self.settingLabel.move(60, 63)

        self.extraction_group.addSettingCard(self.postfixes_card)
        self.extraction_group.addSettingCard(self.ignored_card)
        self.extraction_group.addSettingCard(self.ignore_bad_card)
        self.extraction_group.addSettingCard(self.auto_backup_card)

        # add cards to group
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.aboutSettingCard)
        self.aboutGroup.addSettingCard(self.credits_card)
        # self.aboutGroup.addSettingCard(self.helpCard)
        # self.aboutGroup.addSettingCard(self.feedbackCard)
        # self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)

        self.expandLayout.addWidget(self.extraction_group)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def showEvent(self, event):
        super().showEvent(event)
        if self.pending_update:
            self.ignored_card.ignored_updated()
            self.pending_update = False

    def notify_ignore(self):
        self.pending_update = True

    def __set_qss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
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

    def __show_credits_window(self):
        if not self.credits_window:
            self.credits_window = CreditsWindow()
            self.credits_window.show()
        else:
            self.credits_window.close()
            self.credits_window = None

    def __connect_signal_to_slot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__show_restart_tooltip)
        cfg.themeChanged.connect(self.__on_theme_changed)

        # about
        # self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.aboutSettingCard.feedback_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

        QApplication.instance().ignore_changed.connect(self.notify_ignore)

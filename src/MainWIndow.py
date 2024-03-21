import sys

from PySide6.QtCore import QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as Fi, NavigationItemPosition, FluentTranslator
from qfluentwidgets import (setTheme, Theme, SplitFluentWindow)

from view.MainScreen import MainScreen
from view.SettingsScreen import SettingsScreen

from misc.Config import cfg, Language


class MainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()

        # Create split tabs
        self.mainScreen = MainScreen(self)
        self.settingsScreen = SettingsScreen(self)

        self.init_navigation()

        self.resize(900, 700)

    def init_navigation(self):
        self.addSubInterface(self.mainScreen, Fi.HOME, 'Main')
        self.addSubInterface(self.settingsScreen, Fi.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


if __name__ == '__main__':
    # setTheme(Theme.AUTO)

    app = QApplication(sys.argv)

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, "settings", ".", "resource/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    w = MainWindow()
    w.show()
    app.exec()

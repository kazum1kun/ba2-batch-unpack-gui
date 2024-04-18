import faulthandler
import os.path
import sys
import ctypes

from PySide6.QtCore import QTranslator, Signal
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
        self.init_window()
        self.setMinimumSize(800, 500)
        self.resize(1000, 700)

    def init_navigation(self):
        self.addSubInterface(self.mainScreen, Fi.HOME, 'Main')
        self.addSubInterface(self.settingsScreen, Fi.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

    def init_window(self):
        self.setWindowTitle(u'Unpackrr')
        self.setWindowIcon(QIcon('resource/image/unpackrr.png'))
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width(), h // 2 - self.height() // 2)


# Hack to install a "global" signal/slot
class Unpackrr(QApplication):
    ignore_changed = Signal()


if __name__ == '__main__':
    app = Unpackrr(sys.argv)
    faulthandler.enable()

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, "settings", ".", "resource/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    # Required to display icons correctly
    app_id = 'unpackrr'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    w = MainWindow()
    w.show()

    app.exec()

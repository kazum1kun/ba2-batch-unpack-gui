import ctypes
import faulthandler
import os
import sys

from PySide6.QtCore import QTranslator, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as Fi, NavigationItemPosition, FluentTranslator
from qfluentwidgets import (SplitFluentWindow)

from misc.Config import cfg
from misc.Utilities import resource_path
from view.LogView import LogView
from view.MainScreen import MainScreen
from view.SettingScreen import SettingScreen

basedir = os.path.dirname(__file__)


class MainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()

        # Create split tabs
        self.mainScreen = MainScreen(self)
        self.settingsScreen = SettingScreen(self)

        self.init_navigation()
        self.init_window()
        self.setMinimumSize(800, 500)
        self.resize(1000, 700)

    def init_navigation(self):
        self.navigationInterface.setReturnButtonVisible(False)
        self.addSubInterface(self.mainScreen, Fi.HOME, self.tr('Extraction'))
        self.addSubInterface(self.settingsScreen, Fi.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def init_window(self):
        self.setWindowTitle(u'Unpackrr')
        self.setWindowIcon(QIcon(resource_path('resources/images/unpackrr.png')))
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width(), h // 2 - self.height() // 2)


# Hack to install a "global" signal/slot
class Unpackrr(QApplication):
    ignore_changed = Signal()

    # log_view = LogView()
    # log_view.resize(640, 480)
    # log_view.setWindowTitle('Unpackrr Logs')
    # log_view.setWindowIcon(QIcon('resources/images/unpackrr.png'))


if __name__ == '__main__':
    app = Unpackrr(sys.argv)
    faulthandler.enable()

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    app.installTranslator(fluentTranslator)

    if locale.language().name != 'English':
        unpackrrTranslator = QTranslator()
        unpackrrTranslator.load(locale, 'unpackrr', '.', resource_path('resources/i18n'))
        app.installTranslator(unpackrrTranslator)

    # Required to display icons correctly
    app_id = 'unpackrr'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())

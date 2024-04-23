import ctypes
import os
import sys

from PySide6.QtCore import QTranslator, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as Fi, NavigationItemPosition, FluentTranslator, qconfig, SplashScreen, Theme
from qfluentwidgets import (SplitFluentWindow)

from misc.Config import cfg
from misc.Utilities import resource_path
from view.LogView import LogView, LogLevel
from view.MainScreen import MainScreen
from view.SettingScreen import SettingScreen

basedir = os.path.dirname(__file__)


class MainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()

        self.splash = SplashScreen(QIcon(resource_path('resources/images/unpackrr.png')), self)
        self.init_window()
        self.show()

        # Create split tabs
        self.mainScreen = MainScreen(self)
        self.settingsScreen = SettingScreen(self)

        self.init_navigation()

        self.splash.finish()

    def init_navigation(self):
        self.navigationInterface.setReturnButtonVisible(False)
        self.addSubInterface(self.mainScreen, Fi.HOME, self.tr('Extraction'))
        self.addSubInterface(self.settingsScreen, Fi.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def init_window(self):
        self.setWindowTitle(u'Unpackrr')
        self.setWindowIcon(QIcon(resource_path('resources/images/unpackrr.png')))
        # Center window
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width(), h // 2 - self.height() // 2)
        # Set size
        self.setMinimumSize(800, 500)
        self.resize(1000, 700)


# Hack to install a "global" signal/slot
class Unpackrr(QApplication):
    ignore_changed = Signal()

    def __init__(self, argv):
        super().__init__(argv)
        self.log_view = LogView()
        self.log_view.resize(640, 480)
        self.log_view.setWindowTitle('Unpackrr Logs')
        self.log_view.setWindowIcon(QIcon(resource_path('resources/images/unpackrr.png')))

        self.log_view.add_log('Unpackrr started', LogLevel.INFO)

        self.old_hook = sys.excepthook
        sys.excepthook = self.log_view.catch_exception


if __name__ == '__main__':
    app = Unpackrr(sys.argv)

    # internationalization
    locale = qconfig.get(cfg.language)
    fluentTranslator = FluentTranslator(locale)
    app.installTranslator(fluentTranslator)

    if locale.language().name != 'English':
        unpackrrTranslator = QTranslator()
        unpackrrTranslator.load(locale, 'unpackrr', '.', resource_path('resources/i18n'))
        app.installTranslator(unpackrrTranslator)

    if qconfig.get(cfg.show_debug):
        app.log_view.show()

    # Required to display icons correctly
    app_id = 'unpackrr'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    # Set the default theme to Auto
    if qconfig.get(cfg.first_launch):
        qconfig.set(cfg.themeMode, Theme.AUTO)

    w = MainWindow()
    ret = app.exec()

    qconfig.set(cfg.first_launch, False)

    sys.exit(ret)

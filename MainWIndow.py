import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as Fi
from qfluentwidgets import (setTheme, Theme, SplitFluentWindow)

from MainScreen import MainScreen
from SettingsScreen import SettingsScreen


class MainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()
        setTheme(Theme.AUTO)

        # Create split tabs
        self.mainScreen = MainScreen(self)
        self.settingsScreen = SettingsScreen(self)

        self.init_navigation()

    def init_navigation(self):
        self.addSubInterface(self.mainScreen, Fi.HOME, 'Main')
        self.addSubInterface(self.settingsScreen, Fi.SETTING, 'Settings')

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


if __name__ == '__main__':
    setTheme(Theme.AUTO)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()

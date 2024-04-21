from PySide6 import QtWidgets, QtCore


# Credits to eyllanesc from StackOverflow. Original post at https://stackoverflow.com/a/63853259
class LogView(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self._process = QtCore.QProcess()
        self._process.readyReadStandardOutput.connect(self.handle_stdout)
        self._process.readyReadStandardError.connect(self.handle_stderr)

    def start_log(self, program, arguments=None):
        if arguments is None:
            arguments = []
        self._process.start(program, arguments)

    def add_log(self, message):
        self.appendPlainText(message.rstrip())

    def handle_stdout(self):
        message = self._process.readAllStandardOutput().data().decode()
        self.add_log(message)

    def handle_stderr(self):
        message = self._process.readAllStandardError().data().decode()
        self.add_log(message)

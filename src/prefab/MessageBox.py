from qfluentwidgets import MessageBox
from PySide6.QtWidgets import QApplication


def show_failed_files(parent):
    failed_files_text = '\n'.join(parent.failed)
    box = MessageBox('The following files could not be loaded', failed_files_text, parent=parent)
    box.yesButton.setText('Ok')
    box.cancelButton.setText('Copy to clipboard')
    box.yesSignal.connect(box.deleteLater)
    box.cancelSignal.connect(
        lambda: QApplication.clipboard().setText(failed_files_text)
    )
    box.cancelSignal.connect(box.deleteLater)
    box.exec()


def auto_not_available(parent):
    w = MessageBox('No unpacking necessary',
                   'It appears that you are not over the ba2 limit (yet). No ba2 unpacking is necessary. '
                   'To proceed please manually set a threshold.',
                   parent)
    w.yesSignal.connect(parent.threshold_button.click)
    w.yesButton.setText('Ok')
    w.cancelSignal.connect(QApplication.quit)
    w.cancelButton.setText('Exit Unpackrr')

    w.exec()

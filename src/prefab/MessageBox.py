from PySide6.QtWidgets import QApplication
from qfluentwidgets import MessageBox


def __tr(txt, disambiguation=None, n=-1):
    return QApplication.translate('MassageBox', txt, disambiguation, n)


def show_failed_files(parent):
    failed_files_text = '\n'.join(parent.failed)
    box = MessageBox(__tr('The following files could not be loaded'), failed_files_text, parent=parent)
    box.yesButton.setText(__tr('Ok'))
    box.cancelButton.setText(__tr('Copy to clipboard'))
    box.yesSignal.connect(box.deleteLater)
    box.cancelSignal.connect(
        lambda: QApplication.clipboard().setText(failed_files_text)
    )
    box.cancelSignal.connect(box.deleteLater)
    box.exec()


def auto_not_available(parent):
    w = MessageBox(__tr('No unpacking necessary'),
                   __tr('It appears that you are not over the ba2 limit (yet). No ba2 unpacking is necessary. '
                        'To proceed please manually set a threshold.'),
                   parent)
    w.yesSignal.connect(parent.threshold_button.click)
    w.yesButton.setText(__tr('Ok'))
    w.cancelSignal.connect(QApplication.quit)
    w.cancelButton.setText(__tr('Exit Unpackrr'))

    w.exec()

from PySide6.QtWidgets import QApplication
from qfluentwidgets import InfoBar, InfoBarIcon, InfoBarPosition, PushButton

from misc.Config import cfg
from prefab.MessageBox import show_failed_files


def show_result_toast(results, _type='scan'):
    num_success = results[1]
    num_fail = results[2]
    auto_ignore = cfg.ignore_bad_files.value
    if _type == 'scan':
        verb = QApplication.translate('InfoBar', 'scanning')
    else:
        verb = QApplication.translate('InfoBar', 'extracting')
    fail_message = QApplication.translate(
        'InfoBar', 'Finished {0} ba2. Could not open {1} files').format(verb, num_fail)
    if auto_ignore:
        fail_message += QApplication.translate('InfoBar', ' and they will be ignored in the future.')
    else:
        fail_message += QApplication.translate('InfoBar', '.')
    if _type == 'scan':
        fail_message += QApplication.translate('InfoBar', '\nProcessed {0} files.').format(num_success)
    else:
        fail_message += QApplication.translate('InfoBar', '\nExtracted {0} files.').format(num_success)

    if _type == 'scan':
        fail_title = QApplication.translate('InfoBar', 'Failed to load some files')
    else:
        fail_title = QApplication.translate('InfoBar', 'Failed to extract some files')
    if num_fail > 0:
        warning_info = InfoBar(
            icon=InfoBarIcon.WARNING,
            title=fail_title,
            content=fail_message,
            duration=-1,
            position=InfoBarPosition.BOTTOM,
            parent=results[0]
        )
        more_info_button = PushButton(QApplication.translate('InfoBar', 'Details'), warning_info)
        more_info_button.clicked.connect(lambda: show_failed_files(results[0]))
        warning_info.addWidget(more_info_button)
        warning_info.show()
    else:
        if _type == 'scan':
            success_title = QApplication.translate('InfoBar', 'Ready')
            success_message = QApplication.translate(
                'InfoBar', 'Finished scanning ba2. Processed {0} files.').format(num_success)
            num_ignored = results[3]
            if num_ignored > 0:
                success_message += QApplication.translate(
                    'InfoBar', ' Skipped {0} ignored files.').format(num_ignored)
        else:
            success_title = QApplication.translate('InfoBar', 'All done')
            success_message = QApplication.translate(
                'InfoBar', 'Finished extracting ba2. Extracted {0} files.').format(num_success)
        InfoBar.success(
            title=success_title,
            content=success_message,
            duration=5000,
            position=InfoBarPosition.BOTTOM,
            parent=results[0]
        )

from PySide6.QtWidgets import QApplication
from qfluentwidgets import InfoBar, InfoBarIcon, InfoBarPosition, PushButton, HyperlinkButton

from misc.Config import cfg
from misc.Config import VERSION, NEXUS_URL
from prefab.MessageBox import show_failed_files


def show_result_toast(results, _type='scan'):
    num_success = results[1]
    num_fail = results[2]
    auto_ignore = cfg.get(cfg.ignore_bad_files)
    if _type == 'scan':
        verb = QApplication.translate('InfoBar', 'scanning')
    elif _type == 'check':
        verb = QApplication.translate('InfoBar', 'checking')
    else:
        verb = QApplication.translate('InfoBar', 'extracting')
    fail_message = QApplication.translate(
        'InfoBar', 'Finished {0} ba2. Could not open {1} files').format(verb, num_fail)
    if auto_ignore and _type != 'check':
        fail_message += QApplication.translate('InfoBar', ' and they will be ignored in the future.')
    elif _type == 'check':
        fail_message += QApplication.translate('InfoBar', '. Please check the output above.')
    else:
        fail_message += QApplication.translate('InfoBar', '.')
    if _type == 'scan':
        fail_message += QApplication.translate('InfoBar', '\nProcessed {0} files.').format(num_success)
    elif _type == 'check':
        fail_message += QApplication.translate('InfoBar', '\nChecked {0} files.').format(num_success)
    else:
        fail_message += QApplication.translate('InfoBar', '\nExtracted {0} files.').format(num_success)

    if _type == 'scan':
        fail_title = QApplication.translate('InfoBar', 'Failed to load some files')
    elif _type == 'check':
        fail_title = QApplication.translate('InfoBar', 'Some files did not pass the check')
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

        if _type != 'check':
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
        elif _type == 'check':
            success_title = QApplication.translate('InfoBar', 'All good')
            success_message = QApplication.translate(
                'InfoBar', 'Finished checking ba2. Checked {0} files.').format(num_success)
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


def show_update_available(parent, new_ver):
    if 'v' in new_ver:
        new_ver = new_ver[1:]
    update_info = InfoBar(
        icon=InfoBarIcon.INFORMATION,
        title=QApplication.translate('InfoBar', 'Update available'),
        content=QApplication.translate('InfoBar',
                                       'A new version of Unpackrr is available.\n'
                                       'Current: {0}, latest: {1}').format(VERSION, new_ver),
        duration=-1,
        position=InfoBarPosition.BOTTOM,
        parent=parent
    )
    download_button = HyperlinkButton(NEXUS_URL+'?tab=files', QApplication.translate('InfoBar', 'Download'))
    update_info.addWidget(download_button)
    update_info.show()

from qfluentwidgets import InfoBar, InfoBarIcon, InfoBarPosition, PushButton


from prefab.MessageBox import show_failed_files
from misc.Config import cfg


def show_result_toast(results, _type='scan'):
    num_success = results[1]
    num_fail = results[2]
    auto_ignore = cfg.ignore_bad_files.value
    if _type == 'scan':
        verb = 'scanning'
    else:
        verb = 'extracting'
    fail_message = f'Finished {verb} ba2. Could not open {num_fail} files'
    if auto_ignore:
        fail_message += ' and they will be ignored in the future.'
    else:
        fail_message += '.'
    if _type == 'scan':
        fail_message += f'\nProcessed {num_success} files.'
    else:
        fail_message += f'\nExtracted {num_success} files.'

    if _type == 'scan':
        fail_title = 'Failed to load some files'
    else:
        fail_title = 'Failed to extract some files'
    if num_fail > 0:
        warning_info = InfoBar(
            icon=InfoBarIcon.WARNING,
            title=fail_title,
            content=fail_message,
            duration=-1,
            position=InfoBarPosition.BOTTOM,
            parent=results[0]
        )
        more_info_button = PushButton('Details', warning_info)
        more_info_button.clicked.connect(lambda: show_failed_files(results[0]))
        warning_info.addWidget(more_info_button)
        warning_info.show()
    else:
        if _type == 'scan':
            success_title = 'Ready'
            success_message = f'Finished scanning ba2. Processed {num_success} files.'
            num_ignored = results[3]
            if num_ignored > 0:
                success_message += f' Skipped {num_ignored} ignored files.'
        else:
            success_title = 'All set'
            success_message = f'Finished extracting ba2. Extracted {num_success} files.'
        InfoBar.success(
            title=success_title,
            content=success_message,
            duration=5000,
            position=InfoBarPosition.BOTTOM,
            parent=results[0]
        )


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
    fail_message = f'Finished {verb} ba2. {num_fail} files could not be opened'
    if _type == 'scan':
        if auto_ignore:
            fail_message += ' and were automatically ignored.'
        else:
            fail_message += ' but will be processed anyways.'
        fail_message += f'\n{num_success} files were processed and ready to be extracted.'
    else:
        if auto_ignore:
            fail_message += ' and were automatically ignored.'
        else:
            fail_message += ' but were not ignored.'
        fail_message += f'\n{num_success} files were successfully extracted.'

    if _type == 'scan':
        fail_title = 'Some files could not be loaded'
    else:
        fail_title = 'Some files could not be extracted'
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
        more_info_button.clicked.connect(lambda x: show_failed_files(results[0]))
        warning_info.addWidget(more_info_button)
        warning_info.show()
    else:
        if _type == 'scan':
            success_title = 'Ready'
            success_message = f'Finished scanning ba2. {num_success} files were processed and ready to be extracted.'
        else:
            success_title = 'All set'
            success_message = f'Finished extracting ba2. {num_success} files were extracted.'
        InfoBar.success(
            title=success_title,
            content=success_message,
            duration=5000,
            position=InfoBarPosition.BOTTOM,
            parent=results[0]
        )

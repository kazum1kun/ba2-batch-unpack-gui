from enum import Enum

from qfluentwidgets import Theme, FluentIconBase, isDarkTheme

from misc.Utilities import resource_path


class CustomIcon(FluentIconBase, Enum):
    """ Custom icons """
    FOLDER_ARROW_UP = 'FolderArrowUp'
    STETHOSCOPE = 'Stethoscope'

    def path(self, theme=Theme.AUTO):
        if theme == Theme.DARK:
            theme_str = 'dark'
        elif theme == Theme.LIGHT:
            theme_str = 'light'
        else:
            theme_str = 'dark' if isDarkTheme() else 'light'
        return resource_path(f'resources/images/{self.value}_{theme_str}.png')

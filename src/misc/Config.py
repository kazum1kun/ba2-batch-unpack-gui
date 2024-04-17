import datetime
from enum import Enum

from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QGuiApplication, QFont
from PySide6.QtWidgets import QDialog
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator, ConfigSerializer, __version__,
                            ConfigValidator)


class Ba2ListValidator(ConfigValidator):
    def validate(self, value):
        return all((len(postfix) >= 4 and postfix[-4:] == '.ba2') for postfix in value)

    def correct(self, value):
        postfixes = []
        for postfix in value:
            if len(postfix) >= 4 and postfix[-4:] == '.ba2':
                postfixes.append(postfix)

        return postfixes


class IntValidator(ConfigValidator):
    def validate(self, value):
        return value > 0

    def correct(self, value):
        return 0


class Language(Enum):
    CHINESE_SIMP = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    CHINESE_TRAD = QLocale(QLocale.Language.Chinese, QLocale.Country.Taiwan)
    ENGLISH_US = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    # Extraction
    postfixes = ConfigItem(
        'Extraction', 'Postfixes',
        ['main.ba2', 'materials.ba2', 'misc.ba2', 'scripts.ba2'], Ba2ListValidator()
    )
    ignored = ConfigItem('Extraction', 'IgnoredFiles', [])
    ignore_bad_files = ConfigItem('Extraction', 'IgnoreBadFiles', True, BoolValidator())
    auto_backup = ConfigItem('Extraction', 'AutoBackup', True, BoolValidator())

    # Saved settings
    saved_dir = ConfigItem('Saved', 'Directory', '')
    saved_threshold = ConfigItem('Saved', 'Threshold', 0, IntValidator())

    # Appearance
    enable_acrylic_background = ConfigItem(
        "Appearance", "EnableAcrylicBackground", True, BoolValidator())
    dpi_scale = OptionsConfigItem(
        "Appearance", "DpiScale", "Auto", OptionsValidator(["Auto", 1, 1.25, 1.5, 1.75, 2]), restart=True)
    language = OptionsConfigItem(
        "Appearance", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # software update
    check_update_at_start_up = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())


YEAR = datetime.date.today().year
AUTHOR = "KazumaKuun"
VERSION = 0.1
HELP_URL = "https://pyqt-fluent-widgets.readthedocs.io"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"

cfg = Config()
qconfig.load('config/config.json', cfg)

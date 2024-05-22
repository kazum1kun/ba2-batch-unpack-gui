from enum import Enum

from PySide6.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, ConfigSerializer, ConfigValidator)


class LogLevel(Enum):
    FATAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5


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
    AUTO = QLocale().system()
    ENGLISH_US = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
    CHINESE_SIMP = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    CHINESE_TRAD = QLocale(QLocale.Language.Chinese, QLocale.Country.HongKong)


class LanguageSerializer(ConfigSerializer):
    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class LogLevelSerializer(ConfigSerializer):
    def serialize(self, level):
        return level.name

    def deserialize(self, value: str):
        try:
            return LogLevel[value]
        except KeyError:
            return LogLevel.WARNING


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
    language = OptionsConfigItem(
        "Appearance", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(),
        restart=True)

    # Advanced
    show_debug = ConfigItem('Advanced', 'ShowDebug', False, BoolValidator())
    extraction_path = ConfigItem('Advanced', 'ExtractionPath', '')
    backup_path = ConfigItem('Advanced', 'BackupPath', '')
    ext_ba2_exe = ConfigItem('Advanced', 'ExtBa2Exe', '')

    # Hidden config items
    log_level = ConfigItem('Advanced', 'DebugLevel', LogLevel.WARNING, serializer=LogLevelSerializer())
    first_launch = ConfigItem('Advanced', 'FirstLaunch', True, BoolValidator())

    # software update
    check_update_at_start_up = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())


YEAR = 2024
AUTHOR = 'KazumaKuun / Southwest Codeworks'
VERSION = '0.2.2'
FEEDBACK_URL = 'https://www.nexusmods.com/fallout4/mods/82082?tab=posts'
NEXUS_URL = 'https://www.nexusmods.com/fallout4/mods/82082'
GITHUB_URL = 'https://github.com/kazum1kun/ba2-batch-unpack-gui'
GITHUB_RELEASE_URL = 'https://github.com/kazum1kun/ba2-batch-unpack-gui/releases/latest'
CREDITS_URL = 'https://github.com/kazum1kun/ba2-batch-unpack-gui/blob/master/CREDITS.md'
SWC_URL = 'https://codes.llc/projects/unpackrr'
KOFI_URL = 'https://ko-fi.com/kazblog'

cfg = Config()
qconfig.load('config/config.json', cfg)

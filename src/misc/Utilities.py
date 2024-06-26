import os
import re
import shlex
import subprocess
import sys
import tempfile
import winreg

import requests
from packaging.version import Version
from PySide6.QtWidgets import QApplication
from construct import Struct, Bytes, Int32ul, Int64ul, PaddedString, StreamError

from misc.Config import cfg, LogLevel, GITHUB_RELEASE_URL, VERSION


def is_ignored(file):
    # File is the full path to the file, so we need to perform a full matching and a partial matching based
    # on the file name
    # Case 1 - Full path matching
    if os.path.abspath(file) in cfg.get(cfg.ignored):
        return True
    # Case 2 - Partial matching
    base_name = os.path.basename(file)
    for ignored in cfg.get(cfg.ignored):
        if '{' in ignored and '}' in ignored:
            # Regex pattern
            pattern = ignored.split('{')[1].split('}')[0]
            if re.fullmatch(pattern, base_name):
                return True
        if ignored in base_name:
            return True
    return False


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_default_windows_app(suffix):
    try:
        class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, suffix)
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)) as key:
            command = winreg.QueryValueEx(key, '')[0]
            return shlex.split(command)[0]
    except FileNotFoundError:
        return ''


header_struct = Struct(
    'magic' / Bytes(4),
    'version' / Int32ul,
    'type' / PaddedString(4, 'utf8'),
    'file_count' / Int32ul,
    'names_offset' / Int64ul,
)

units = {'B': 1, 'KB': 1000, 'MB': 1000 ** 2, 'GB': 1000 ** 3, 'TB': 1000 ** 4}


def parse_size(size):
    if not (size[-1] == 'b' or size[-1] == 'B'):
        size = size + 'B'
    size = size.upper()
    if not re.match(r' ', size):
        size = re.sub(r'([KMGT]?B)', r' \1', size)
    try:
        number, unit = [string.strip() for string in size.split()]
        return int(float(number) * units[unit])
    except ValueError:
        return -1


# Return all ba2 in the folder that contain one of the given postfixes
# Note: it scans for exactly the second-tier directories under the given directory (aka the mod folders)
# This is to avoid scanning for ba2 that will not be loaded to the game anyways
def scan_for_ba2(path, postfixes):
    all_ba2 = []
    for d in os.listdir(path):
        full_path = os.path.join(path, d)
        # Skip files
        if not os.path.isdir(full_path):
            continue
        # List all files under the mod
        for ba2 in os.listdir(full_path):
            fpath = os.path.join(full_path, ba2)
            # Add only *.ba2 archives that contains one of the specified postfixes
            if any([postfix in ba2.lower() for postfix in postfixes]):
                all_ba2.append(fpath)

    return all_ba2


# A convenience function to return the number of files in a ba2 archive
def num_files_in_ba2(file):
    with open(file, 'rb') as fs:
        try:
            result = header_struct.parse_stream(fs)
            return result.file_count
        except StreamError as e:
            QApplication.instance().log_view.add_log(f'Error parsing {file}: {e}', LogLevel.WARNING)
            return -1


def extract_ba2(file, bsab_exe_path, use_temp=False):
    tmp_dir = None
    if use_temp:
        tmp_dir = tempfile.TemporaryDirectory()
        extraction_path = tmp_dir.name
    else:
        cfg_path = cfg.get(cfg.extraction_path)
        if cfg_path:
            if os.path.isabs(cfg_path):
                extraction_path = cfg_path
            else:
                extraction_path = os.path.join(os.path.dirname(file), cfg_path)
        else:
            extraction_path = os.path.dirname(file)

        if not os.path.isdir(extraction_path):
            os.makedirs(extraction_path)

    # Hide the console window
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    args = [
        bsab_exe_path,
        'unpack',
        file,
        extraction_path
    ]
    proc = subprocess.run(args, text=True, capture_output=True, startupinfo=si)

    if use_temp:
        tmp_dir.cleanup()
    results = proc.stdout.strip().split('\n')
    if 'Error:' in results[-1] or 'error:' in results[-1]:
        QApplication.instance().log_view.add_log(f'Error reading {file}', LogLevel.WARNING)
        return -1
    else:
        return 0
    # if proc.returncode != 0:
    #     QApplication.instance().log_view.add_log(f'Error extracting {file}', LogLevel.WARNING)
    #     return -1
    # else:
    #     QApplication.instance().log_view.add_log(f'{proc.stdout}', LogLevel.INFO)
    #     return 0


def list_ba2(file, bsab_exe_path):
    # Hide the console window
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    args = [
        bsab_exe_path,
        file,
        '-list'
    ]
    proc = subprocess.run(args, text=True, capture_output=True, startupinfo=si)
    results = proc.stdout.strip().split('\n')
    if 'Error:' in results[-1] or 'error:' in results[-1]:
        QApplication.instance().log_view.add_log(f'Error reading {file}', LogLevel.WARNING)
        return -1
    else:
        return 0

    # # BSArch does not return the status code correctly, we have to check for the error message
    # if proc.returncode != 0:
    #     QApplication.instance().log_view.add_log(f'Error reading {file}', LogLevel.WARNING)
    #     return -1
    # else:
    #     return 0


def check_latest_version():
    r = requests.get(GITHUB_RELEASE_URL)
    version = r.url.split('/')[-1]
    if Version(version) > Version(VERSION):
        return version
    else:
        return None

import os
import subprocess


def readable_size(size):
    units = ('KB', 'MB', 'GB', 'TB')
    size_list = [f'{int(size):,} B'] + [f'{int(size) / 1024 ** (i + 1):,.1f*} {u}' for i, u in enumerate(units)]
    return [size for size in size_list if not size.startswith('0.')][-1]


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
def num_files_in_ba2(bsab_path, file):
    args = [
        bsab_path,
        '-l:N',
        file
    ]
    proc = subprocess.run(args, capture_output=True)
    if proc.returncode == 0:
        results = proc.stdout
        return results.count('\n')
    else:
        print(f'{file} fails to open!')
        return -1

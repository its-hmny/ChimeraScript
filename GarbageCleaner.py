"""
garbageCleaner.py is a simple script that I use to clean the location in which I
usually save my temporary and/or garbage file, wipeDir() works recursively so
everything inside that dir will be deleted (I warned you).

Created by Enea Guidi on 1/1/20. Please check the README.md for further information.
"""

import os
import sys
import platform
from chimera_utils import Log

log = Log()

if (platform.system() == "Windows"):
    homePath = "C:/Users/eneag/"
    # This is the amount of shit that Windows has by default
    dirsToClean = [
        "Documents/odelli di Office personalizzati",
        "Documents/WindowsPowerShell",
        "Documents/Zoom"
        "Videos/Captures",
        "Pictures/Saved Pictures",
        "Pictures/Camera Roll",
    ]
elif (platform.system() == "Linux"):
    homePath = "/home/hmny/"
    dirsToClean = [".cache", "Downloads", "tmp"]
else:
    log.error("This OS is not supported yet")
    sys.exit(-1)


def wipeDir(path: str) -> None:
    dir_content = os.listdir(path)
    for entry in dir_content:
        toRemove = os.path.join(path, entry)
        # Works recursively and deletes the subdirectory
        if os.path.isdir(toRemove):
            wipeDir(toRemove)
            os.rmdir(toRemove)
        # Normal file case, should work for every type of file
        else:
            os.remove(toRemove)


def GarbageCleaner() -> None:
    global dirsToClean
    # The user can specify his own directories
    user_given_dir = bool(len(sys.argv[1:]))
    # Eventually set the new dirs to clean
    if user_given_dir:
        dirsToClean = sys.argv[1:]

    for directory in dirsToClean:
        resolver = os.path.abspath if user_given_dir else os.path.join
        # Set up the Current Cleaning Directory based on the input
        if user_given_dir:
            ccd = resolver(directory)
        else:
            ccd = resolver(homePath, directory)
        # Ignored the case of an already empty directory (warning given)
        if os.path.isdir(ccd) and len(os.listdir(ccd)):
            wipeDir(ccd)
            log.success(f"Cleaned {ccd}")
        else:
            log.warning(f"{ccd} not found or already empty")


if __name__ == "__main__":
    GarbageCleaner()

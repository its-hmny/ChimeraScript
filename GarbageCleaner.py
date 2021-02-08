"""
garbageCleaner.py is a simple script that I use to clean the location in which I usually save my temporary and/or garbage file,
wipeDir() works recursively so everything inside that dir will be deleted (I warned you).
Created by Enea Guidi on 1/1/20. Please check the README.md for further information.
"""

import os
from chimera_utils import Log

homePath = "/home/its-hmny/"
dirsToClean = [".cache", "Downloads", "Temporary", "Public"]


def wipeDir(path):
    contents = os.listdir(path)
    for toDelete in contents:
        tmp = f"{path}/{toDelete}"
        # Works recursively and deletes the subdirectory
        if os.path.isdir(tmp):
            wipeDir(tmp)
            os.rmdir(tmp)
        # Normal file case, should work for every type of file
        else:
            os.remove(tmp)


def garbageCleaner():
    log = Log()

    for directory in dirsToClean:
        # Setting up the Current Cleaning Directory
        ccd = homePath + directory
        # Ignored the case of an already empty directory (warning given to
        # user)
        if os.path.isdir(ccd) and os.listdir(ccd) != []:
            wipeDir(ccd)
            log.success(f"Cleaned {ccd}")
        else:
            log.warning(f"{ccd} not found or already empty")


garbageCleaner()

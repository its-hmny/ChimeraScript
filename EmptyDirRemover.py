"""
EmptyDirRemover is a simple Python script used for deleting my old/empty folder.
The script works recursivly from the input directory to all the subdirectories and
so on so use it only in directories where you're sure to not delete nothing important.

Created by Enea Guidi on 20/09/2019. Please check the README.md for more informations
"""

import os
import sys
from chimera_utils import Log, exception_handler

log = Log()


def recursiveClean(toClean: str) -> None:
    # List of all the path inside the current directory
    dirContent = os.listdir(toClean)

    # Check that also the subdirectory have files in it and calls the clean
    # function on them
    for contained in dirContent:
        newPath = os.path.join(toClean, contained)
        if (os.path.isdir(newPath)):
            recursiveClean(newPath)

    # Refresh the content list and the eliminates if empty
    dirContent = os.listdir(toClean)
    if (len(dirContent) == 0):
        os.rmdir(toClean)


@exception_handler
def EmptyDirRemover() -> None:
    if len(sys.argv[1:]):
        startingDir = os.path.abspath(sys.argv[1])
    else:
        startingDir = "/home/its-hmny/"

    if (os.path.isdir(startingDir)):
        recursiveClean(startingDir)
    else:
        log.error("The input given is not a directory")


if __name__ == "__main__":
    EmptyDirRemover()

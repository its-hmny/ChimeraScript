"""
This utility module containes a basics class that are used all over this project.
The Compressor class implements a simple zip archiver (in future maybe I will work on a more memory efficient implementation),
it has some operator overloads to keep code simple.
"""

import zipfile
import os


class Compressor():
    def __init__(self, filename="dump.zip", tmp=False):
        self.dump = zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED, True)
        self.location = filename
        self.isTemporary = tmp

    def compressDir(self, source_dir, blacklist=[]):
        if os.path.isdir(source_dir) and self.dump is not None:
            # Get abspath of the parent directory of source_dir
            abspath = os.path.abspath(os.path.join(source_dir, os.pardir))
            # Iterates through directories and files in source_dir adding all
            # recursively
            for root, dirs, files in os.walk(source_dir):
                dirs[:] = [d for d in dirs if d not in blacklist]
                # Create the current directory in the dump
                self.dump.write(root, os.path.relpath(root, abspath))
                # Then puts all the files contained in the newly created
                # directory
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.isfile(filepath):
                        arcname = os.path.join(
                            os.path.relpath(root, abspath), file)
                        self.dump.write(filepath, arcname)
        else:
            raise NotADirectoryError

    def compressFile(self, file, path="./"):
        if os.path.isfile(file) and self.dump is not None:
            # Get abspath of the parent directory of source_dir
            abspath = os.path.abspath(os.path.join(file, os.pardir))
            # Then writes the file in the desired place
            self.dump.write(os.path.relpath(file, abspath), path + file)
        else:
            raise FileNotFoundError

    def runChecks(self):
        return self.dump.testzip()

    def __bool__(self):
        return self.dump is not None

    def __lshift__(self, other):
        if os.path.isfile(other):
            self.compressFile(other)
        elif os.path.isdir(other):
            self.compressDir(other)
        else:
            raise TypeError(
                "Invalid argument, check that the path is correct or that a path string was given"
            )

    def __del__(self):
        self.dump.close()
        if self.isTemporary:
            os.remove(self.location)

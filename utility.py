"""
This utility module containes two basics class that are used all over this project.
The Log class is a basic wrapper to print function, it has also the option to set personal codes.
The Compressor class implements a simple zip archiver (in future maybe I will implement a more efficient implementation),
it has some operator overloads to keep code simple.
"""

import zipfile, os

class Log():
    def __init__(self, success="\033[92m", error="\033[91m", warning="\033[93m"):
        self.clearCode = "\033[0m"
        self.errorCode = error
        self.successCode = success
        self.warningCode = warning

    def success(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self.successCode, msg, self.clearCode))

    def error(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self.errorCode, msg, self.clearCode))

    def warning(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self.warningCode, msg, self.clearCode))


class Compressor():
    def __init__(self, filename="dump.zip", tmp=False):
        self.dump = zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED, True)
        self.location = filename
        self.isTemporary = tmp

    def compressDir(self, source_dir, blacklist=[]):
        if os.path.isdir(source_dir) and self.dump != None:
            # Get abspath of the parent directory of source_dir
            abspath = os.path.abspath(os.path.join(source_dir, os.pardir))
            # Iterates through directories and files in source_dir adding all recursively
            for root, dirs, files in os.walk(source_dir):
                # Create the current directory in the dump
                self.dump.write(root, os.path.relpath(root, abspath))
                # Then puts all the files contained in the newly created directory
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.isfile(filepath):
                        arcname = os.path.join(os.path.relpath(root, abspath), file)
                        self.dump.write(filepath, arcname)
        else:
            raise NotADirectoryError

    def compressFile(self, file, path="./"):
        if os.path.isfile(file) and self.dump != None:
            # Get abspath of the parent directory of source_dir
            abspath = os.path.abspath(os.path.join(file, os.pardir))
            # Then writes the file in the desired place
            self.dump.write(os.path.relpath(file, abspath), path + file)
        else:
            raise FileNotFoundError

    def runChecks(self):
        return self.dump.testzip()

    def __bool__(self):
        return self.dump != None

    def __lshift__(self, other):
        if os.path.isfile(other):
            self.compressFile(other)
        elif os.path.isdir(other):
            self.compressDir(other)
        else:
            raise TypeError("Invalid argument, check that the path is correct or that a path string was given")

    def __del__(self):
        self.dump.close()
        if self.isTemporary:
            os.remove(self.location)

        

# Test section
if __name__ == "__main__":
    log = Log()
    print("\nTest Log class...")
    log.error("This is an error message")
    log.warning("This is an warning message")
    log.success("This is an success message")

    print("\nTest Compressor class...")
    dump = Compressor("test.zip", True)
    if not dump:
        log.error("Dump couldn't be initialized")

    log.warning("Compressing some random files to test Compressor")
    dump.compressDir(".")
    dump.compressDir("../BiKayaOS")
    dump.compressFile("utility.py")
    dump.compressFile("utility.py", "BiKayaOS/")
    dump << "GitPuller.py"
    log.success("Completed random file compression")

    log.warning("Running some checks on the archive...")
    try:
        testOutcome = dump.runChecks()
    except RuntimeError:
        log.error("Seems like the dump is closed")
    if testOutcome == None:
        log.success("No file result damaged")
    else:
        log.error("Here's a list of files badly compressed: {}".format(testOutcome))

    log.warning("Closing the archive, this will delete it")
    del dump
    if os.path.isfile("test.zip"):
        log.error("The test dump is still here!")
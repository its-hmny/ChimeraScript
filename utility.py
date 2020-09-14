
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
    def __init__(self, filename="dump.zip"):
        self.dump = zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED)

    def compressDir(self, source_dir):
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
        if os.path.isfile(file):
            # Get abspath of the parent directory of source_dir
            abspath = os.path.abspath(os.path.join(file, os.pardir))
            # Then writes the file in the desired place
            self.dump.write(os.path.relpath(file, abspath), path + file)
        else:
            raise FileNotFoundError



if __name__ == "__main__":
    log = Log()
    log.error("This is an error message")
    log.warning("This is an warning message")
    log.success("This is an success message")

    dump = Compressor("test.zip")
    dump.compressDir(".")
    dump.compressDir("../BiKayaOS")
    dump.compressFile("utility.py")
    dump.compressFile("utility.py", "BiKayaOS/")
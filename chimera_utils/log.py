"""
This utility module containes a basics class that are used all over this project.
The Log class is a basic wrapper to print function, it has also the option to set personal codes.
"""


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


# Test section
if __name__ == "__main__":
    log = Log()
    print("\nTest Log class...")
    log.error("This is an error message")
    log.warning("This is an warning message")
    log.success("This is an success message")
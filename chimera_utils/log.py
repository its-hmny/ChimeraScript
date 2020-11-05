"""
This utility module containes a basics class that are used all over this project.
The Log class is a basic wrapper to print function, it has also the option to set personal codes.
"""


class Log():
    def __init__(self, success="\033[92m", error="\033[91m", warning="\033[93m"):
        self._clearCode = "\033[0m"
        self._errorCode = error
        self._successCode = success
        self._warningCode = warning

    def success(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self._successCode, msg, self._clearCode))

    def error(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self._errorCode, msg, self._clearCode))

    def warning(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self._warningCode, msg, self._clearCode))


# Test section
if __name__ == "__main__":
    log = Log()
    log._clearCode = True
    print("\nTest Log class...")
    log.error("This is an error message")
    log.warning("This is an warning message")
    log.success("This is an success message")


class Log():
    def __init__(self, success="\033[92m", error="\033[91m", warning="\033[93m"):
        self.clear = "\033[0m"
        self.error = error
        self.success = success
        self.warning = warning

    def successMsg(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self.success, msg, self.clear))

    def errorMsg(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self.error, msg, self.clear))

    def warningMsg(self, msg="YOU must provide a message"):
        print("{}{}{}".format(self.warning, msg, self.clear))
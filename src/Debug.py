import pathlib

class Debug:
    def __init__(self):
        self.log_file = pathlib.Path("log.txt")
        self.DEBUG = False

    def set_debug_file(self, file):
        self.log_file = file
        return self

    def debug_on(self):
        self.DEBUG = True
        return self

    def debug(self, msg):
        if self.log_file is None:
            return
        if self.DEBUG:
            print(msg)
        # write into a log file
        with open(self.log_file, "a") as f:
            f.write(msg + "\n")

Dbg = Debug()
DEBUG = False
def debug(msg):
    if DEBUG:
        print(msg)
    # write into a log file
    with open("log.txt", "a") as f:
        f.write(msg + "\n")
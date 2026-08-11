import os

def checkDisk(path=".", space=100):
    """
    Checks IF some space is still available on device storage
    Intended use: "if checkDisk(): sys.exit(-1)"
    :param path: str, path to folder to check, default="."
    :param space: scalar, minimum space to be available in MB
    :returns: bool, True if space is NOT available
    """
    statvfs = os.statvfs(path=path)
    return statvfs.f_frsize * statvfs.f_bavail < space*2**20: # 100 MB

class Bookkeeping:
    def __init__(self, new, rts, mfd):
        self.fnew = new
        self.frts = rts
        self.fmfd = mfd

    def getNew(self, i)
        with open(self.fnew) as f:
            data = f.read().split(",")
        if len(data) != 3:
            return -1
        r = [int(e) for e in data]
        r[i] += 1
        with open(self.fnew, "w") as f:
            f.write(f"{},{},{}".format(*r))
        return r[i]-1

    def getNewData(self):
        return self.getNew(0)
    def getNewHK(self):
        return self.getNew(1)
    def getNewLog(self):
        return self.getNew(2)

    def __mark(self, i, run, mfile):
        with open(mfile) as f:
            data = f.read().split(",")
        r = [int(e) for e in data]
        if len(data) != 3:
            return -1
        r[i] = run
        with open(mfile, "w") as f:
            f.write(f"{},{},{}".format(*r))

    def markRTS(self, i, run):
        self.__mark(i, run, self.frts)

    def markRTSData(self, run):
        self.markRTS(0, run)
    def markRTSHK(self, run):
        self.markRTS(1, run)
    def markRTSLog(self, run):
        self.markRTS(2, run)

    def markfordel(self, i, run):
        self.__mark(i, run, self.fmfd)

    def markfordelData(self, run):
        self.markfordel(0, run)
    def markfordelHK(self, run):
        self.markfordel(1, run)
    def markfordelLog(self, run):
        self.markfordel(2, run)





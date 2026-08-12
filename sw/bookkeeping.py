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
    return statvfs.f_frsize * statvfs.f_bavail < space*2**20 # 100 MB

class Bookkeeping:
    def __init__(self, new, rts, mfd, **kwargs):
        self.fnew = new
        self.frts = rts
        self.fmfd = mfd
        wronglength, wrongvalue = [], []
        with open(self.fnew) as f:
            dnew = f.read().split(",")
        if len(dnew) != 3: wronglength.append(self.fnew)
        try:
            _ = [int(e) for e in dnew]
        except ValueError:
            wrongvalue.append(self.fnew)
        with open(self.frts) as f:
            drts = f.read().split(",")
        if len(drts) != 3: wronglength.append(self.frts)
        try:
            _ = [int(e) for e in drts]
        except ValueError:
            wrongvalue.append(self.frts)
        with open(self.fmfd) as f:
            dmfd = f.read().split(",")
        if len(dmfd) != 3: wronglength.append(self.fmfd)
        try:
            _ = [int(e) for e in dmfd]
        except ValueError:
            wrongvalue.append(self.fmfd)
        if len(wronglength) > 0 or len(wrongvalue) > 0:
            raise RuntimeError(f"Bookkeeping files invalid: Wrong number of fields={wronglength}; Int conversion failed={wrongvalue}")

    def __get(self, mfile):
        with open(mfile) as f:
            data = f.read().split(",")
        if len(data) != 3:
            raise RuntimeError(f"{mfile} does not contain 3 fields - it may be corrupted.")
        return [int(e) for e in data]

    def getNew(self, i):
        r = self.__get(self.fnew)
        r[i] += 1
        with open(self.fnew, "w") as f:
            f.write("{},{},{}".format(*r))
        return r[i]-1

    def getNewAll(self):
        r = self.__get(self.fnew)
        s = [e+1 for e in r]
        with open(self.fnew) as f:
            f.write("{},{},{}".format(*s))
        return r

    def getNewData(self):
        return self.getNew(0)
    def getNewHK(self):
        return self.getNew(1)
    def getNewLog(self):
        return self.getNew(2)

    def __mark(self, i, run, mfile):
        r = self.__get(mfile)
        r[i] = int(run)
        with open(mfile, "w") as f:
            f.write("{},{},{}".format(*r))

    def markRTSAll(self, datan, hkn, logn):
        with open(self.frts) as f:
            f.write("{},{},{}".format(int(datan), int(hkn), int(logn)))

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

    def getRTSData(self):
        return self.__get(self.frts)[0]
    def getRTSHK(self):
        return self.__get(self.frts)[1]
    def getRTSLog(self):
        return self.__get(self.frts)[2]

    def getMFDData(self):
        return self.__get(self.fmfd)[0]
    def getMFDHK(self):
        return self.__get(self.fmfd)[1]
    def getMFDDLog(self):
        return self.__get(self.fmfd)[2]


import logging
import os
import time

import bookkeeping

user = "bbdebian"
ip = "[fe80::df62:1759:93d4:cc23%eth0]"
dest = "ASTEP_networking/data/"
key = "~/.ssh/id_ed25519"

def rsync(fname):
    """
    Send a file to FFR via rsync
    :param fname: str, filename in sw/
    """
    os.system(f"rsync --rsh='ssh -i {key}' /home/debian/astep-fw/sw/{fname} {user}@{ip}:{dest}")
    return True

def waitForFSW(timeout):
    elapsed = 0
    while not(os.path.isfile("/tmp/bookkeeping.txt")) and elapsed < timeout:
        time.sleep(1); elapsed += 1
    if os.path.isfile("/tmp/bookkeeping.txt"):
        logger.info("Found /tmp/bookkeeping.txt")
        with open("/tmp/bookkeeping.txt") as f:
            data = f.read().split(";")
        os.remove("/tmp/bookkeeping.txt")
        try:
            bookkeeper = bookkeeping.Bookkeeping(new=data[0], rts=data[1], mfd=data[2])
            logger.info("Bookkeper initialized.")
            logn = int(data[3])
            logger.info(f"Recovered log number {logn}")
        except Exception as e:
            logger.error(e)
            return False, None, None
        return True, bookkeeper, logn
    else: return False, None, None

def main(timeout):
    fswok, bookkeeper, mylog = waitForFSW(timeout)
    if fswok:
        os.rename("bookkeeper.log", f"data/log{mylog:05d}.log")
        while True:
            # Listing files
            filelist = os.listdir("data/")
            datafiles, hkfiles, logfiles = [], [], []
            for f in filelist:
                if f.startswith("data") and f.endswith(".bin") and os.path.isfile("data/"+f) and len(f) == 13 and f[4:9].isdigit(): datafiles.append(f)
                elif f.startswith("hk") and f.endswith(".bin") and os.path.isfile("data/"+f) and len(f) == 11 and f[2:7].isdigit(): hkfiles.append(f)
                elif f.startswith("log") and f.endswith(".log") and os.path.isfile("data/"+f) and len(f) == 12 and f[3:8].isdigit(): logfiles.append(f)
            datan = [int(f[4:9]) for f in datafiles]
            hkn = [int(f[2:7]) for f in hkfiles]
            logn = [int(f[3:8]) for f in logfiles]
            print(logn, hkn, datan)
            # Send logs
            if len(logn) > 0 and (number := min(logn)) <= bookkeeper.getRTSLog():
                logger.info(f"Attempting to send log{number:05d}.log")
                rsync(f"data/log{number:05d}.log")
                bookkeeper.markfordelLog(number)
            # Send housekeeping
            if len(hkn) > 0 and (number := min(hkn)) <= bookkeeper.getRTSHK():
                logger.info(f"Attempting to send hk{number:05d}.bin")
                rsync(f"data/hk{number:05d}.bin")
                bookkeeper.markfordelHK(number)
            # Send data
            if len(datan) > 0 and (number := min(datan)) <= bookkeeper.getRTSData():
                logger.info(f"Attempting to send data{number:05d}.bin")
                rsync(f"data/data{number:05d}.bin")
                bookkeeper.markfordelData(number)
            # Del log
            if len(logn) > 0 and (number := min(logn)) <= bookkeeper.getMFDDLog():
                os.remove(f"data/log{number:05d}.log")
            # Del hk
            if len(hkn) > 0 and (number := min(hkn)) <= bookkeeper.getMFDHK():
                os.remove(f"data/hk{number:05d}.bin")
            # Del data
            if len(datan) > 0 and (number := min(datan)) <= bookkeeper.getMFDData():
                os.remove(f"data/data{number:05d}.bin")
            time.sleep(2)
    else:
        logger.error("Problem during filesender initialization. Sending logs.")
        if os.path.isfile("run.log"):
            logger.info("Found run.log - sending.")
            rsync("run.log")
        if os.path.isfile("bookkeeper.log"):
            logger.info("Found bookkeeper.log - sending.")
            rsync("bookkeeper.log")


if __name__ == "__main__":
    formatter = logging.Formatter(
        "%(created)s:%(name)s.%(lineno)d.%(levelname)s:%(message)s"
    )
    fh = logging.FileHandler("bookkeeper.log")
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)
    logging.getLogger().setLevel(logging.INFO)
    global logger
    logger = logging.getLogger(__name__)
    logger.info("Setup bookkeeper logger")
    main(timeout = 10)


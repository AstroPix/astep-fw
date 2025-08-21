"""
Test program to run the A-STEP test bench.

Author: Adrien Laviron, adrien.laviron@nasa.gov
"""

import asyncio
import os
import time
import xml.etree.ElementTree as ET
import socket

# Logging stuff
import logging

# AstroPix drivers
from astropixrun import AstropixRun
import bookkeeping

#async def interpretCommands(boardDriver, cmds):
#    CI = ComsInterpreter()#To access the dictionaries
#    if not CI.checkCodes():
#        logger.error("Interpreter dictionaries invalid.")
#        return
#    CI.setBytes(cmds)
#    #while (cmd:=CI.getCmd()):
#    #    if cmd[0] == "DRO":
#    #        pass
#    #    elif cmd[0] == "HKD":
#    #        pass
#    #    #elif cmd[0]

def parseFSW(fname):
    """
    Loads content of an xml fsw config file into a dictionary
    :param fname: str, path to fsw config xml file
    :returns: dict
    """
    cfgroot = ET.parse(fname).getroot()
    cfg = dict()
    cfg["fpgaxml"] = cfgroot.find("fpga_config").attrib["value"]
    cfg["HVup"] = float(cfgroot.find("HV_set").attrib["value"])
    cfg["yaml"] = [cfgroot.find("chipconfig").attrib["layer0"], cfgroot.find("chipconfig").attrib["layer1"], cfgroot.find("chipconfig").attrib["layer2"]]
    cfg["chipsPerRow"] = [cfgroot.find("chipsPerRow").attrib["layer0"], cfgroot.find("chipsPerRow").attrib["layer1"], cfgroot.find("chipsPerRow").attrib["layer2"]]
    #cfg["cfgcommands"] = cfgroot.find("configupdate").attrib["value"]
    cfg["uselayer"] = [cfgroot.find("uselayer").attrib["layer0"] != "False", cfgroot.find("uselayer").attrib["layer1"] != "False", cfgroot.find("uselayer").attrib["layer2"] != "False"]
    cfg["readout"] = cfgroot.find("readout").attrib["value"]
    if cfgroot.find("onepixelonly").attrib["value"] == "True":
        cfg["yaml"] = ["quadchip_allOff", "quadchip_allOff", "quadchip_allOff"]
        cfg["inject"] = [int(cfgroot.find("onepixellocation").attrib["layer"]), int(cfgroot.find("onepixellocation").attrib["chip"]), int(cfgroot.find("onepixellocation").attrib["row"]), int(cfgroot.find("onepixellocation").attrib["col"])]
    else:
        cfg["inject"] = None
    if cfgroot.find("inject").attrib["voltage"] == "None":
        cfg["vinj"] = None
    else:
        cfg["vinj"] = int(cfgroot.find("inject").attrib["voltage"])
    cfg["hkPeriod"] = float(cfgroot.find("housekeeping_period").attrib["value"])
    cfg["loglevel"] = cfgroot.find("loglevel").attrib["value"]
    cfg["bookkeeping"] = cfgroot.find("bookkeeping").attrib
    cfg["limits"] = cfgroot.find("watcher").attrib
    return cfg


def getxmlcfg():
    """
    Checks scripts/config for a valid config dictionary
    scripts/config should contain fsw000.xml, fsw001.xml, etc. and the higher number one will be loaded.
    If it fails, the next higher number will be loaded,
    :returns: dict
    """
    # Check available files
    cfgfiles = os.listdir("scripts/config")
    ymlfiles, fswfiles, xmlfiles = [], [], []
    for f in cfgfiles:
        if f.endswith(".yml") and os.path.isfile(f"scripts/config/{f}"): ymlfiles.append(f)
        if f.endswith(".xml") and os.path.isfile(f"scripts/config/{f}"):
            if f.startswith("fsw") and len(f) == 10 and f[3:6].isdigit(): fswfiles.append(f)
            if f.startswith("astep"): xmlfiles.append(f)
    # Attempt loading FSW configs in reverse order
    fswnlist = sorted([int(f[3:6]) for f in fswfiles], reverse=True)
    for fswn in fswnlist:
        goodfsw = True
        logger.info(f"Loading fsw{fswn:03d}.xml")
        try:
            cfg = parseFSW("scripts/config/fsw{:03d}.xml".format(fswn))
        except Exception as e:
            logger.error(f"While parsing fsw: {e}")
            goodfsw = False
        if fswn >= 900:
            logger.info(f"fsw{fswn:03d}.xml is single-use - deleting")
            os.remove(f"scripts/config/fsw{fswn:03d}.xml")
        if not goodfsw:
            continue
        # Attempt loading bookkeeping mechanism
        bookkeepingKeys = cfg["bookkeeping"].keys()
        if "new" not in bookkeepingKeys or "rts" not in bookkeepingKeys or "mfd" not in bookkeepingKeys:
            logger.error(f"Invalid bookkeeping arguments: {bookkeepingKeys}")
            goodfsw = False
        if "new" in bookkeepingKeys and not(os.path.isfile(cfg["bookkeeping"]["new"])):
            logger.error(f"File not found: {cfg['bookkeeping']['new']}")
            goodfsw = False
        if "rts" in bookkeepingKeys and not(os.path.isfile(cfg["bookkeeping"]["rts"])):
            logger.error(f"File not found: {cfg['bookkeeping']['rts']}")
            goodfsw = False
        if "mfd" in bookkeepingKeys and not(os.path.isfile(cfg["bookkeeping"]["mfd"])):
            logger.error(f"File not found: {cfg['bookkeeping']['mfd']}")
            goodfsw = False
        if goodfsw:
            logger.info("Instanciating Bookkeeping")
            try:
                cfg["bookkeeper"] = bookkeeping.Bookkeeping(**cfg["bookkeeping"])
            except Exception as e:
                logger.error(f"While instanciating Bookkeeping: {e}")
                goodfsw = False
        # Check fpga xml and yaml files are present
        if cfg["fpgaxml"] not in xmlfiles:
            logger.error(f"{cfg['fpgaxml']} not found")
            goodfsw = False
        for i, y in enumerate(cfg["yaml"]):
            if y+".yml" not in ymlfiles:
                logger.error(f"{y}.yml not found")
                goodfsw = False
            else:
                cfg["yaml"][i] = f"scripts/config/{y}.yml"
        if goodfsw: break
    if not(goodfsw):
        logger.error("No valid fsw config file found")
        raise RuntimeError("No valid fsw config file found")
    logger.info(f"Setting log level to {cfg["loglevel"]}")
    if cfg["loglevel"] == "I": logger.setLevel(logging.INFO)
    elif cfg["loglevel"] == "W": logger.setLevel(logging.WARNING)
    elif cfg["loglevel"] == "E": logger.setLevel(logging.ERROR)
    elif cfg["loglevel"] == "C": logger.setLevel(logging.CRITICAL)
    else: logger.warning(f"Invalid log level: {cfg["loglevel"]}")
    if cfg["readout"] == "None": cfg["readout"] = None
    elif cfg["readout"].isdigit(): cfg["readout"] = int(cfg["readout"])
    else:
        logger.warning(f"{cfg["readout"]} is not int or None - defaults to None")
        cfg["readout"] = None
    if cfg["inject"] is not None and (len(cfg["inject"]) != 4 or 
            cfg["inject"][0] < 0 or cfg["inject"][0] > 2 or cfg["inject"][1] < 0 or cfg["inject"][1] > 3 or 
            cfg["inject"][2] < 0 or cfg["inject"][2] > 34 or cfg["inject"][3] < 0 or cfg["inject"][3] > 34):
        logger.error(f"One-pixel parameters {cfg["inject"]} invalid. All pixels are deactivated with no injection.")
        cfg["inject"] = None
    try:
        cfg["limits"]["maxframes"] = int(cfg["limits"]["maxframes"])
        cfg["limits"]["maxwrong"] = int(cfg["limits"]["maxwrong"])
        cfg["limits"]["period"] = int(cfg["limits"]["period"])
    except Exception as e:
        logger.error(f"While converting limits to int (defaults to 1e9, period=5): {e}")
        cfg["limits"]["maxframes"] = 1e9
        cfg["limits"]["maxwrong"] = 1e9
        cfg["limits"]["period"] = 5
    logger.info(f"Loaded: fsw{fswn:03d}.xml")
    return cfg


async def TCPlistener(port: int = 1025):
    """
    Instantiate TCP/IP socket and 
    """
    await asyncio.Event().wait()
    return # Placeholder while I figure out this part
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('::', port))
    sock.listen(1)
    logger.info('TCP listener: Waiting for connection...')
    conn, addr = sock.accept()
    logger.info(f'TCPlistener: Connected by {addr}')
    listen = True
    while listen:
        data = conn.recv(1024)
        if not data:
            break
        logger.info('TCP listener recieved:', data.decode('ascii'))
        if data=='shutdown'.encode('ascii'):
            listen = False
    conn.close()
    return
    #if not listen: raise KeyboardInterrupt


def poweroff(error):
    """
    Powers off the BB.
    """
    if error:
        logger.info("Flight software errored. Waiting 20 s. to give filesender time.")
        time.sleep(20)
    logger.info("Flight software completed. Shutting down ...")
    print("I'm not running the shutdown command for dev pruposes, but it works.")
    #os.system("sudo systemctl poweroff")
    #Needs to have the following command (or equivalent) ran once to disable sudo asking password:
    #  `sudo echo "debian ALL=(ALL) NOPASSWD: /usr/bin/systemctl poweroff, 
    #               /usr/bin/systemctl halt, /usr/bin/systemctl reboot" > /etc/sudoers.d/shutdown`


#######################################################
#################### MAIN FUNCTION ####################

async def main():
    args = getxmlcfg()
    datan, hkn, logn = args["bookkeeper"].getNewAll() #FSW gets its log number first
    bookkeeperlog = args["bookkeeper"].getNewLog()
    with open("/tmp/bookkeeping.txt", "w") as f:
        f.write("{new};{rts};{mfd};{bookkeeperlog}".format(bookkeeperlog=bookkeeperlog, **args["bookkeeping"])) #Now filesender can get moving
    logger.info(f"File numbers data={datan} hk={hkn} log={logn}")
    args["bookkeeper"].markRTSAll(datan-1, hkn-1, logn-1)
    os.rename("run.log", f"data/log{logn:05d}.log")
    if bookkeeping.checkDisk("data/", 100):
        logger.critical("Less than 100 MB available in data folder - aborting run.")
        raise RuntimeError("Not enough disk space left.")
    arun = AstropixRun(f"scripts/config/{args['fpgaxml']}")
    # Open connexion to FPGA board
    await arun.open_fpga() # Gecco or CMOD selected from the fpgaxml config file
    #arun.boardDriver.rfg.io.spi.warning()
    # Ramp up HV
    hvup_task = asyncio.create_task(arun.rampHV(args["HVup"], timeout = 5))
    await hvup_task
    # Configure detectors
    await arun.fpga_configure_clocks()
    arun.load_yaml(args["yaml"], args["chipsPerRow"])
    logger.info("Chips configuration loaded.")
    arun.layerlst = []
    for i, layer in enumerate(args["uselayer"]):
        if layer: arun.layerlst.append(i)
        else: arun.boardDriver.asics.pop(i, None)
    logger.info(f"Enabled layers: {arun.layerlst}")
    #arun.applyCommands(args["cfgcommands"])
    await arun.fpga_configure_autoread_keepalive()
    if args["inject"] is not None:
        arun.cfg_enable_pixel(*args["inject"])
    if args["vinj"] is not None:
        arun.cfg_enable_injection(*args["inject"])
        await arun.init_injection(layer=args["inject"][0], chip=args["inject"][1], inj_voltage=args["vinj"])
    logger.info("Uploading chips configuration.")
    await arun.chips_reset_configure()
    await arun.buffer_flush()

    await arun.chips_enable_readout() #By default uses fpgaxml and arun.layerlst
    if args["vinj"] is not None: await arun.start_injection()
    # Configure and start housekeeping
    await arun.config_adchk()
    await arun.config_fpgahk()
    ofile_hk = open("data/hk{:05d}.bin".format(hkn),"wb")
    hk_task = asyncio.create_task(arun.housekeeping(ofile=ofile_hk, hk_period=args["hkPeriod"], terminalPrint=False))
    # Start data acquisition
    ofile = open("data/data{:05d}.bin".format(datan), "wb")
    data_task = asyncio.create_task(arun.readout_loop(args["readout"], ofile))
    watcher_task = asyncio.create_task(arun.watcher(args["limits"]))
    listen_task = asyncio.create_task(TCPlistener())

    # # Runtime
    try:
        print("Running, Ctrl+C to stop.")
        #await asyncio.Event().wait()
        await listen_task
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("[Ctrl+C] while collecting data - exiting.")
    except Exception as e:
        logger.info(f"Unexpected error while colleting data: {e}")
    
    # # Finish data collection
    listen_task.cancel()
    hk_task.cancel()
    data_task.cancel()
    watcher_task.cancel()
    logger.info("Finished data collection")

    # Closeout
    await arun.chips_disable_readout()
    if args["vinj"]: await arun.stop_injection()
    hvdown_task = asyncio.create_task(arun.rampHV(0.))
    ofile.close()
    ofile_hk.close()
    await hvdown_task
    await arun.fpga_close_connection()


#######################################################
#################### TOP LEVEL ########################

if __name__ == "__main__":
    formatter = logging.Formatter(
        "%(created)s:%(name)s.%(lineno)d.%(levelname)s:%(message)s"
    )
    fh = logging.FileHandler("run.log")
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)
    logging.getLogger().setLevel(logging.INFO)
    global logger
    logger = logging.getLogger(__name__)
    logger.info("Setup logger")
    error = False

    try:
        asyncio.run(main())
        logger.info("Finished Main")
    except KeyboardInterrupt:
        logger.info("SIGINT received")
        error = True
    except Exception as e:
        logger.error(f"Error during main: {e}")
        error = True
    poweroff(error)

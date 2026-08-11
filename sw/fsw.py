"""
Test program to run the A-STEP test bench.

Author: Adrien Laviron, adrien.laviron@nasa.gov
"""

import asyncio
import os, sys
import time
import xml.etree.ElementTree as ET

# Logging stuff
import logging

# AstroPix drivers
from astropixrun import AstropixRun
import bookkeeping


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
    cfg["autoread"] = [cfgroot.find("autoread").attrib["layer0"] != "False", cfgroot.find("autoread").attrib["layer1"] != "False", cfgroot.find("autoread").attrib["layer2"] != "False"]
    if cfgroot.find("onepixelonly").attrib["value"] == "True":
        cfg["yaml"] = ["allOff", "allOff", "allOff"]
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
    return cfg


def getxmlcfg():
    """
    Checks scripts/config for a valid config dictionary
    scripts/config should contain fsw000.xml, fsw001.xml, etc. and the higher number one will be loaded.
    If it fails, the next higher number will be loaded,
    :returns: dict
    """
    cfgfiles = os.listdir("scripts/config")
    ymlfiles, fswfiles, xmlfiles = [], [], []
    for f in cfgfiles:
        if f.endswith(".yml") and os.path.isfile(f"scripts/config/{f}"): ymlfiles.append(f)
        if f.endswith(".xml") and os.path.isfile(f"scripts/config/{f}"):
            if f.startswith("fsw") and len(f) == 10: fswfiles.append(f)
            if f.startswith("astep"): xmlfiles.append(f)
    fswnlist = sorted([int(f[3:6]) for f in fswfiles], reverse=True)
    for fswn in fswnlist:
        logger.info(f"Loading fsw{fswn:03d}.xml")
        try:
            cfg = parseFSW("scripts/config/fsw{:03d}.xml".format(fswn))
        except Exception as e:
            logger.error(f"While parsing fsw: {e}")
            continue
        nextfsw = False
        if cfg["fpgaxml"] not in xmlfiles:
            logger.error(f"{cfg['fpgaxml']} not found")
            nextfsw = True
        for y in cfg["yaml"]:
            if y+".yml" not in ymlfiles:
                logger.error(f"{y}.yml not found"); nextfsw=True
        bookkeepingKeys = cfg["bookkeeping"].keys()
        if "new" not in bookkeepingKeys or "rts" not in bookkeepingKeys or "mfd" not in bookkeepingKeys:
            logger.error(f"Invalid bookkeeping arguments")
            nextfsw = True
        if "new" in bookkeepingKeys and not(os.path.isfile(cfg["bookkeeping"]["new"])):
            logger.error(f"File not found: {cfg['bookkeeping']['new']}")
            nextfsw = True
        if "rts" in bookkeepingKeys and not(os.path.isfile(cfg["bookkeeping"]["rts"])):
            logger.error(f"File not found: {cfg['bookkeeping']['rts']}")
            nextfsw = True
        if "mfd" in bookkeepingKeys and not(os.path.isfile(cfg["bookkeeping"]["mfd"])):
            logger.error(f"File not found: {cfg['bookkeeping']['mfd']}")
            nextfsw = True
        if nextfsw: continue
        else: break
    if nextfsw:
        logger.critical("No valid fsw config file found")
        sys.exit(-1)
    logger.info(f"Setting log level to {cfg["loglevel"]}")
    if cfg["loglevel"] == "I": logger.setLevel(logging.INFO)
    elif cfg["loglevel"] == "W": logger.setLevel(logging.WARNING)
    elif cfg["loglevel"] == "E": logger.setLevel(logging.ERROR)
    elif cfg["loglevel"] == "C": logger.setLevel(logging.CRITICAL)
    else: logger.warning(f"Invalid log level: {cfg["loglevel"]}")
    if cfg["inject"] is not None and (len(cfg["inject"]) != 4 or 
            cfg["inject"][0] < 0 or cfg["inject"][0] > 2 or cfg["inject"][1] < 0 or cfg["inject"][1] > 3 or 
            cfg["inject"][2] < 0 or cfg["inject"][2] > 34 or cfg["inject"][3] < 0 or cfg["inject"][3] > 34):
        logger.error(f"One-pixel parameters {cfg["inject"]} invalid. Skipping injection.")
        cfg["inject"] = None
    return cfg


def getOutputName():
    """
    Checks output file location and bookkeeping files to determine the name of the next data, hk and log files to be generated.
    """
    datalist = os.listdir("data")
    dataf = []
    hkf = []
    logf = []
    for f in datalist:
        if f.startswith("data_") and f.endswith(".bin") and os.path.isfile(f): dataf.append(f)
        if f.startswith("hk_") and f.endswith(".bin") and os.path.isfile(f): hkf.append(f)
        if f.endswith(".log") and os.path.isfile(f): logf.append(f)
    


#######################################################
#################### MAIN FUNCTION ####################

async def main():
    args = getxmlcfg()
    arun = AstropixRun(f"scripts/config/{args['fpgaxml']}")
    # Open connexion to FPGA board
    await arun.open_fpga() # Gecco or CMOD selected from the fpgaxml config file
    # Ramp up HV
    hvup_task = asyncio.create_task(arun.rampHV(args["HVup"], timeout = 5))
    await hvup_task
    # Configure detectors
    await arun.fpga_configure_clocks()
    arun.load_yaml(args["yaml"], args["chipsPerRow"])
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

    await arun.chips_enable_readout()
    if args["vinj"] is not None: await arun.start_injection()
    # Configure and start housekeeping
    await arun.config_adchk()
    await arun.config_fpgahk()
    ofile_hk = open("{}_hk.bin".format(args.outputPrefix),"wb")
    hk_task = asyncio.create_task(arun.housekeeping(ofile=ofile_hk, hk_period=args["hk_period"], terminalPrint=False))
    # Start data acquisition
    ofile = open("{}.bin".format(args.outputPrefix), "wb")
    data_task = asyncio.create_task(arun.readout_loop(args.readout,ofile))

    # # Runtime
    try:
        if args.runTime: await asyncio.sleep(args.runTime * 60.0)
        else: await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("[Ctrl+C] while collecting data - exiting.")
    
    # # Finish data collection
    hk_task.cancel()
    data_task.cancel()

    # Closeout
    await arun.chips_disable_readout()
    if args.vinj: await arun.stop_injection()
    if args.HVdown: hvdown_task = asyncio.create_task(arun.rampHV(0.))
    ofile.close()
    ofile_hk.close()
    if args.HVdown: await hvdown_task
    await arun.fpga_close_connection()

#######################################################
#################### TOP LEVEL ########################

if __name__ == "__main__":
    formatter = logging.Formatter(
        "%(asctime)s:%(msecs)d.%(name)s.%(levelname)s:%(message)s"
    )
    fh = logging.FileHandler("run.log")
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)
    logging.getLogger().setLevel(logging.info)
    global logger
    logger = logging.getLogger(__name__)
    logger.info("Setup logger")

    try:
        asyncio.run(main())
        logger.info("Finished Main")

    except KeyboardInterrupt:
        logger.info("SIGINT received")
    except Exception as e:
        logger.error(f"Error during main: {e}")

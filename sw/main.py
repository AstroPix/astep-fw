"""
Test program to run the A-STEP test bench.

Author: Adrien Laviron, adrien.laviron@nasa.gov
"""

import argparse
import asyncio
import os
import sys
import time

# Logging stuff
import logging

# AstroPix drivers
from astropixrun import AstropixRun


import rfg.io.spi
import rfg.io.spidev
if (magic:=False):
    rfg.io.spi.debug()
    rfg.io.spidev.debug()
else:
    rfg.io.spi.warning()

#######################################################
#################### MAIN FUNCTION ####################
"""
async def testmain(args):
    arun = AstropixRun(args.fpgaxml)
    # Open connexion to FPGA board
    await arun.open_fpga() # Gecco or CMOD selected from the fpgaxml config file
    ## Start with non-thread-safe configs
    # Configure detectors
    await arun.fpga_configure_clocks()
    arun.load_yaml(args.yaml, args.chipsPerRow)
    print("1")
    await arun.fpga_configure_autoread_keepalive(flush=True)
    print("2")
    await arun.update_pixThreshold(vthreshold=args.threshold)
    print("3")
    if args.inject:
        arun.cfg_enable_pixel(*args.inject)
        arun.cfg_enable_injection(*args.inject)
        await arun.init_injection(layer=args.inject[0], chip=args.inject[1], inj_voltage=args.vinj)
    print("4")
    if args.analog:
        arun.cfg_enable_analog(*args.analog)  # Also turn that pixel on (just in case)
    print("5")
    await arun.chips_reset_configure()
    print("6")
    await arun.buffer_flush()
    print("7")
    await arun.chips_enable_readout()
    if args.inject: await arun.start_injection()
    print("8")
    # Configure and start housekeeping
    #await arun.config_adchk()
    #await arun.config_fpgahk()
    print("9")
    #hk_period = 1 if args.hkPeriod is None else int(args.hkPeriod) # in seconds
    #ofile_hk = open("{}_hk.bin".format(args.outputPrefix),"wb")
    print(args.outputPrefix)
    ofile = open("{}.bin".format(args.outputPrefix), "wb")
    res = ofile.write(int.to_bytes(12))
    ofile.flush()
    print(res)

    ## Start multithreading
    #hk_task = asyncio.create_task(arun.housekeeping(ofile=ofile_hk, hk_period=hk_period, terminalPrint=True))
    data_task = asyncio.create_task(arun.readout_loop(args.readout,ofile))
    # # Runtime
    try:
        if args.runTime: await asyncio.sleep(args.runTime * 60.0)
        else: await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("[Ctrl+C] while collecting data - exiting.")
    
    # # Finish data collection
    #hk_task.cancel()
    data_task.cancel()

    # Closeout
    if args.HVdown: hvdown_task = asyncio.create_task(arun.rampHV(0.))
    await arun.chips_disable_readout()
    if args.inject: await arun.stop_injection()
    if args.HVdown: await hvdown_task
    ofile.close()
    #ofile_hk.close()
    await arun.fpga_close_connection()
"""

async def main(args):
    arun = AstropixRun(args.fpgaxml)
    # Open connexion to FPGA board
    await arun.open_fpga() # Gecco or CMOD selected from the fpgaxml config file
    print("1")
    # Ramp up HV
    #await arun.rampHV(args.HVup)
    if args.HVup is not None: #arun.rampHV(args.HVup)
        hvup_task = asyncio.create_task(arun.rampHV(args.HVup, timeout = 5))
    if args.HVup is not None: await hvup_task
    print("2")
    # Configure detectors
    await arun.fpga_configure_clocks()
    arun.load_yaml(args.yaml, args.chipsPerRow)
    await arun.fpga_configure_autoread_keepalive()
    await arun.update_pixThreshold(vthreshold=args.threshold)
    print("3")
    if args.inject:
        arun.cfg_enable_pixel(*args.inject)
        arun.cfg_enable_injection(*args.inject)
        await arun.init_injection(layer=args.inject[0], chip=args.inject[1], inj_voltage=args.vinj)
    if args.analog:
        arun.cfg_enable_analog(*args.analog)  # Also turn that pixel on (just in case)
    print("4")
    await arun.chips_reset_configure()
    await arun.buffer_flush()
    print("5")

    if True:
        # Wait for HV before starting data acquisition
        #if args.HVup is not None: await hvup_task
        #while hvup_task is not None and not hvup_task.done():
            #logging.info("Waiting for HV ...")
            #await asyncio.sleep(.5)
        #if hvup_task is not None: hvup_task.cancel()
        #while not hvup_task.done(): time.sleep(.1)
        await arun.chips_enable_readout()
        if args.inject: await arun.start_injection()
        # Configure and start housekeeping
        await arun.config_adchk()
        await arun.config_fpgahk()
        hk_period = 1 if args.hkPeriod is None else int(args.hkPeriod) # in seconds
        ofile_hk = open("{}_hk.bin".format(args.outputPrefix),"wb")
        hk_task = asyncio.create_task(arun.housekeeping(ofile=ofile_hk, hk_period=hk_period, terminalPrint=True))
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
    if args.inject: await arun.stop_injection()
    if args.HVdown: hvdown_task = asyncio.create_task(arun.rampHV(0.))
    ofile.close()
    ofile_hk.close()
    if args.HVdown: await hvdown_task
    await arun.fpga_close_connection()

#######################################################
#################### TOP LEVEL ########################

if __name__ == "__main__":
    start_time = time.strftime("%Y%m%d-%H%M%S")
    parser = argparse.ArgumentParser(
        description="Test program to run the A-STEP test bench.",
        formatter_class=argparse.RawTextHelpFormatter,  # allow formatting of the epilog
        epilog="""""",
    )

    # Options related to outputs
    parser.add_argument(
        "-o",
        "--outputPrefix",
        type=str,
        default="{0}{1}data{1}".format(
            os.getcwd(), os.path.sep
        ),
        help="Path to and beginning of the name of the data file(s) and log file, default: data/YYYYMMDD-HHMMSS",
    )

    # Options related to software run settings
    parser.add_argument(
        "-L",
        "--loglevel",
        type=str,
        choices=["D", "I", "E", "W", "C"],
        action="store",
        default="I",
        help="Set loglevel used. Options: D - debug, I - info, E - error, W - warning, C - critical. DEFAULT: I",
    )
    parser.add_argument(
        "-T",
        "--runTime",
        type=float,
        action="store",
        default=None,
        help="Maximum run time (in minutes). Default: NONE (run until user CTL+C)",
    )
    parser.add_argument(
        "-r",
        "--readout",
        default=0,
        type=int,
        help="Number of bytes of FPGA buffer to read for each readout (1 to 4098, 0->As much as buffer contains, other->4096). Default: 0",
    )

    # Options related to Setup / Configuration of system
    parser.add_argument(
        "-x",
        "--fpgaxml",
        type=str,
        default="gecco",
        help="filepath (in scripts/config/ directory) .xml file containing fpga configuration. \
                                Default: config/gecco.xml (default parameters for the Gecco board)",
    )
    parser.add_argument(
        "-y",
        "--yaml",
        action="store",
        required=False,
        type=str,
        default=["quadchip_allOff"],
        nargs="+",
        help="filepath (in scripts/config/ directory) .yml file containing chip configuration. \
                                One file must be passed for each layer, from layer #0 to layer #2. \
                                Default: config/quadChip_allOff (All pixels off, only fisrt layer is configured)",
    )
    parser.add_argument(
        "-c",
        "--chipsPerRow",
        action="store",
        required=False,
        type=int,
        default=[4],
        nargs="+",
        help="Number of chips per SPI bus to enable. Can provide a single number or one number per bus. Default: 4",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        action="store",
        default=None,
        help="Threshold voltage for digital ToT (in mV). DEFAULT: 150",
    )
    parser.add_argument(
        "-a",
        "--analog",
        action="store",
        required=False,
        type=int,
        default=None,
        nargs=3,
        help="Turn on analog output in the given column. Can only enable one analog pixel per layer. \
                        Requires input in the form {layer, chip, col} (no wrapping brackets). \
                        Default: None",
    )
    # Default: layer 1, chip 0, col 0')

    # Options related to chip injection
    parser.add_argument(
        "-i",
        "--inject",
        action="store",
        default=None,
        type=int,
        nargs=4,
        help="Turn on injection in the given layer, chip, row, and column. Default: No injection",
    )
    parser.add_argument(
        "-v",
        "--vinj",
        action="store",
        default=None,
        type=int,
        help="Specify injection voltage (in mV). DEFAULT: value in config ",
    )

    # Options related to housekeeping
    parser.add_argument(
        "-hk",
        "--hkPeriod",
        action="store",
        default=None,
        type=int,
        help="Set period of housekeeping loop output in seconds. Default: 1 second",
    )

    parser.add_argument(
        "--HVup",
        action="store",
        type=float,
        default=None,
        help="Ramp HV up to set voltage before acquiring data. Default: None"
    )
    parser.add_argument(
        "--HVdown",
        action="store_true",
        default=False,
        help="Ramp HV down after data acquisition. Default: False"
    )

    args = parser.parse_args()

    if args.outputPrefix==f"{os.getcwd()}{os.path.sep}data{os.path.sep}":
        args.outputPrefix=args.outputPrefix+start_time
    else:
        args.outputPrefix=f"{args.outputPrefix}_{start_time}"

    # Define the loglevel
    ll = args.loglevel
    if ll == "D":
        loglevel = logging.DEBUG  ## DAN - not working! Causes runs to crash and read in tons of railed buffers after the alloted time???
    elif ll == "I":
        loglevel = logging.INFO
    elif ll == "E":
        loglevel = logging.ERROR
    elif ll == "W":
        loglevel = logging.WARNING
    elif ll == "C":
        loglevel = logging.CRITICAL
    logname = args.outputPrefix + "_run.log"
    formatter = logging.Formatter(
        "%(asctime)s:%(msecs)d.%(name)s.%(levelname)s:%(message)s"
    )

    # Richard 17/11/25 Create Loggin File Handle, make sure containing folder exists
    os.makedirs(os.path.dirname(os.path.abspath(logname)), exist_ok=True)
    fh = logging.FileHandler(logname)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logging.getLogger().addHandler(sh)
    logging.getLogger().addHandler(fh)
    logging.getLogger().setLevel(loglevel)
    global logger
    logger = logging.getLogger(__name__)
    logger.info("Setup logger")

    # Layer counting begins at 0.
    # Make sure config arguments make sense
    if len(args.yaml) > len(args.chipsPerRow):
        if len(args.chipsPerRow) > 1:
            logger.warning(
                f"Number of chips per row not provided for every layer - default to {args.chipsPerRow[0]} for all {len(args.yaml)} layers."
            )
        args.chipsPerRow = [args.chipsPerRow[0]] * len(args.yaml)
    elif len(args.yaml) < len(args.chipsPerRow):
        raise ValueError(
            "You need to provide one yaml configuration file for every chipsPerRow argument."
        )

    # Make sure analog/inject arguments make sense
    if args.analog is not None and (
        len(args.analog) != 3
        or args.analog[0] < 0
        or args.analog[0] > 2
        or args.analog[1] < 0
        or args.analog[1] > 3
        or args.analog[2] < 0
    ):
        raise ValueError(
            "Incorrect analog argument layer={0[0]},chip={0[1]},column={0[2]}".format(
                args.analog
            )
        )
    if args.inject is not None and (
        len(args.inject) != 4
        or args.inject[0] < 0
        or args.inject[0] > 2
        or args.inject[1] < 0
        or args.inject[1] > 3
        or args.inject[2] < 0
        or args.inject[3] < 0
    ):
        raise ValueError(
            "Incorrect analog argument layer={0[0]},chip={0[1]},row={0[2]},column={0[3]}".format(
                args.inject
            )
        )

    # Sanitizing args.readout
    if args.readout == 0:
        args.readout = None
    elif args.readout < 0 or args.readout > 4098:
        args.readout = 4096

    pathdelim = os.path.sep  # determine if Mac or Windows separators in path name    
    # Sanitizing args.fpgaxml
    args.fpgaxml = os.getcwd() + pathdelim + "scripts" + pathdelim + "config" + pathdelim + args.fpgaxml + ".xml"
    assert os.path.exists(args.fpgaxml), f"FPGA config file {args.fpgaxml} not found"
    # Sanitizing args.yaml
    args.yaml = [
        os.getcwd()
        + pathdelim
        + "scripts"
        + pathdelim
        + "config"
        + pathdelim
        + y
        + ".yml"
        for y in args.yaml
    ]  # Define YAML path variables
    for y in args.yaml:
        assert os.path.exists(y) , f"Config File {y} was not found, pass the name of a config file from the scripts/config folder"


    try:
        asyncio.run(main(args))
        logger.info("Finished Main")

    except KeyboardInterrupt:
        logger.info("Stopping due to CTRL-C")
        sys.exit(-1)
    except Exception as e:
        logger.error(f"Error during main: {e}")

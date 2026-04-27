"""
Test program to run the A-STEP test bench.

Author: Adrien Laviron, adrien.laviron@nasa.gov
"""

import argparse
import asyncio
from bitstring import BitArray
import os
import sys
import time

# Logging stuff
import logging

# AstroPix drivers
from astropixrun import AstropixRun

#import drivers.astep.serial
#import drivers.astropix.decode
#import drivers.boards




#######################################################
#################### MAIN FUNCTION ####################


async def main(args):
    arun = AstropixRun(args.fpgaxml)
    # Open connexion to FPGA board
    await arun.open_fpga() # Gecco or CMOD selected from the fpgaxml config file
    await arun.fpga_configure_clocks()
    arun.load_yaml(args.yaml, args.chipsPerRow)
    await arun.fpga_configure_autoread_keepalive()
    await arun.chips_reset_configure()
    await arun.buffer_flush()

    # Setup chip geometry
    chipversion = arun.config.find("chipversion").attrib["value"]
    if chipversion == 3: n_rows, n_cols = 35, 35
    if chipversion == 4: n_rows, n_cols = 13, 16
    if chipversion == 5: n_rows, n_cols = 34, 36
    first_col = 3 if chipversion==3 else 0

    # Iterate over injection runs
    ofile = open("{}.bin".format(args.outputPrefix), "wb")
    for vinj in [100]:
        for chip in range(args.chipsPerRow[0]):

            # Set vinj and row here
            for layer in range(args.layers):
                await arun.init_injection(layer=layer, chip=chip, inj_voltage=vinj)
                for row in range(n_rows):
                    arun.boardDriver.asics[layer].enable_inj_row(chip=chip, row=row)

            # Iterate over columns here
            for col in range(first_col, n_cols):
                #Turn on correct column here
                await arun.boardDriver.layersSelectSPI(flush=True)
                for layer in range(args.layers):
                    arun.boardDriver.asics[layer].enable_inj_col(chip=chip, col=col)
                    for row in range(n_rows):
                        arun.boardDriver.asics[layer].enable_pixel(chip=chip, col=col, row=row)
                    await arun.boardDriver.writeSPIAsicConfig(lane=layer, targetChip=chip)
                await arun.boardDriver.layersDeselectSPI(flush=True)

                logger.info(f"FPGA_TS={await arun.boardDriver.rfg.read_layers_fpga_timestamp_counter(count= \
                                            arun.boardDriver.fpgaTimeStampBytesCount)}: Injecting {vinj} mV in column {col} of chip {chip}")

                # Main loop here
                end_time = float("inf") if args.runTime is None else time.time() + args.runTime
                run = time.time() < end_time

                await arun.chips_enable_readout() 
                await arun.start_injection()
                
                while run:
                    try:
                        # Read data
                        buff, readout = await arun.get_readout()
                        # Output data
                        if buff > 0:
                            ofile.write(readout)
                        print(f"  {buff:04d}  ", end="\r")
                        # Check time
                        run = time.time() < end_time
                    except (KeyboardInterrupt, asyncio.CancelledError):
                        logger.info("[Ctrl+C] while in main loop - exiting.")
                        run = False
                
                await arun.stop_injection()
                await arun.chips_disable_readout()
                print("\n")
                
                #Turn off correct column here
                for layer in range(args.layers):
                    arun.boardDriver.asics[layer].disable_inj_col(chip=chip, col=col)
                    for row in range(n_rows):
                        arun.boardDriver.asics[layer].disable_pixel(chip=chip, col=col, row=row)

            # Turn off chip here
            await arun.boardDriver.layersSelectSPI(flush=True)
            for layer in range(args.layers):
                for row in range(n_rows):
                    arun.boardDriver.asics[layer].disable_inj_row(chip=chip, row=row)
                await arun.boardDriver.writeSPIAsicConfig(lane=layer, targetChip=chip)
            await arun.boardDriver.layersDeselectSPI(flush=True)


    await arun.fpga_close_connection()
    ofile.close()



#######################################################
#################### TOP LEVEL ########################

if __name__ == "__main__":
    start_time = time.strftime("%Y%m%d-%H%M%S")
    parser = argparse.ArgumentParser(
        description="Runs injector on all chips, one column at a time. All lanes run in parallel.",
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
        default=30,
        help="Maximum run time (in seconds) for one column and one injection voltage. Default: 30 (run until user CTL+C)",
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
        "-l",
        "--layers",
        action="store",
        required=False,
        type=int,
        default=1,
        help="Layers to run injection scan on \
                                Default: 1 (only layer 0)",
    )
    parser.add_argument(
        "-c",
        "--chipsPerRow",
        action="store",
        required=False,
        type=int,
        default=4,
        help="Maximum number of chips per SPI bus to enable. Can provide a single number or one number per bus. Default: 4",
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

    args.yaml = ["quadchip_allOff" for _ in range(args.layers)]
    args.chipsPerRow = [args.chipsPerRow for _ in range(args.layers)]
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

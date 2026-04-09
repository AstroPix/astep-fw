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


async def callHK(boardDriver, lsbFirst=False):
    """
    Calls housekeeping from TI ADC128S102 ADC. Loops over each of the 8 input channels.
    Input is two bytes:
    First 2 bits: ignored
    Next 3 bits: Set Channel #
    Last 11 bits: ignored

    Shift register input style requires bytes to be read in left to right. May be changed in future versions
    """
    ## Configure Housekeeping SPI Frequency.
    ## ADC Datasheet recommends > 8MHz (and < 16 MHz) and default is 10MHz. #DV Check this I actually think it defaults to 4MHz
    ## DAC Datasheet claims < 30 MHz works
    await boardDriver.configureHKSPIFrequency(targetFrequencyHz=10000000,flush=True)
    await boardDriver.houseKeeping.configureSPI(adc=1,dac=0)    
    
    ## Select and Set ADC. Comment -- in the future may be able to skip configuration w/in this step
    await boardDriver.houseKeeping.selectSPI(adc=1,dac=0)

    ## Loop over ADC Settings
    for chan in range(8):
        bits = format(chan<<3,'08b')
        if lsbFirst == True:
            byte1 = int(bits[::-1],2)
        else:
            byte1 = int(bits,2)

        print('CHANNEL ', chan)

        #read same channel a few extra times to confirm value comes through
        for _ in range(3):

            await boardDriver.houseKeeping.writeADCDACBytes([byte1,0x00])
            adcBytesCount = await boardDriver.houseKeeping.getADCBytesCount()
            adcBytes = await boardDriver.houseKeeping.readADCBytes(adcBytesCount)
            adcBits = BitArray(bytes=adcBytes)
            

            #reverse bit order and swap bytes if needed
            if lsbFirst == True:
                adcBits.reverse()
                adcBits.byteswap()

            print(f"Got ADC bytes {int(adcBits.bin,2)/4096*3.3}")

    await boardDriver.houseKeeping.selectSPI(adc=0,dac=0)




#######################################################
#################### MAIN FUNCTION ####################


async def main(args):
    arun = AstropixRun(args.fpgaxml)
    # Open connexion to FPGA board
    await arun.open_fpga() # Gecco or CMOD selected from the fpgaxml config file
    await arun.fpga_configure_clocks()
    arun.load_yaml(args.yaml, args.chipsPerRow)
    await arun.fpga_configure_autoread_keepalive()
    await arun.update_pixThreshold(vthreshold=args.threshold)
    if args.inject:
        arun.cfg_enable_pixel(*args.inject)
        arun.cfg_enable_injection(*args.inject)
        await arun.init_injection(layer=args.inject[0], chip=args.inject[1], inj_voltage=args.vinj)
    if args.analog:
        arun.cfg_enable_analog(*args.analog)  # Also turn that pixel on (just in case)
    await arun.chips_reset_configure()
    await arun.buffer_flush()
    await arun.chips_enable_readout()

    # Configure housekeeping
    await arun.config_hk()

    # Main loop here
    end_time = float("inf") if args.runTime is None else time.time() + (args.runTime * 60.0)
    run = time.time() < end_time
    ofile = open("{}.bin".format(args.outputPrefix), "wb")
    if args.inject: await arun.start_injection()

    # Begin housekeeping
    hk_timeout = 1 if args.hkloop is None else int(args.hkloop)
    hktask = asyncio.create_task(arun.housekeeping(hk_timeout))
    
    while run:
        try:
            # Read data
            buff, readout = await arun.get_readout(args.readout)
            # Output data
            if buff > 0:
                ofile.write(readout)
            print(f"  {buff:04d}  ", end="\r")
            # Check time
            run = time.time() < end_time
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("[Ctrl+C] while in main loop - exiting.")
            run = False

    await arun.chips_disable_readout()
    if args.inject: await arun.stop_injection()
    hktask.cancel()
    await arun.fpga_close_connection()
    ofile.close()



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
        "--hkloop",
        action="store",
        default=None,
        type=int,
        help="Set cadence of housekeeping loop output in seconds. Default: 1s",
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

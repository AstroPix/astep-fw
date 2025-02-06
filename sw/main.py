"""
Test program to run the A-STEP test bench.

Author: Adrien Laviron, adrien.laviron@nasa.gov
"""
# Needed modules. They all import their own suppourt libraries, 
# and eventually there will be a list of which ones are needed to run
import pandas as pd
import asyncio
import time, os, sys, binascii
from tqdm import tqdm
import argparse

import drivers.boards
import drivers.astep.serial
#import drivers.astropix.decode Not needed yet, maybe later

# Logging stuff
import logging

# progress bar - Usefull to wait for humans to read oscilloscopes 
def _wait_progress(seconds:float=2):
    try:
        for _ in tqdm(range(int(10*seconds)), desc=f'Wait {int(10*seconds)/10} s.'):
            try:
                time.sleep(.1)
            except KeyboardInterrupt:
                break
    except KeyboardInterrupt:
        pass

async def buffer_flush(boardDriver, layer):
    """This method will ensure the layer interrupt is not low and flush buffer, and reset counters"""
    #Flush data from sensor
    logger.info("Flush chip before data collection")
    status = await boardDriver.getLayerStatus(layer)
    interruptn = status & 0x1
    #deassert hold
    await boardDriver.holdLayer(layer, hold=False)
    interupt_counter=0
    while interruptn == 0 and interupt_counter<20:
        logger.info("interrupt low")
        await boardDriver.writeLayerBytes(layer = layer, bytes = [0x00] * 128, flush=True)
        nmbBytes = await boardDriver.readoutGetBufferSize()
        if nmbBytes > 0:
                await boardDriver.readoutReadBytes(1024)
        status = await boardDriver.getLayerStatus(layer)
        interruptn = status & 0x1 
        interupt_counter+=1
    #reassert hold to be safe
    await boardDriver.holdLayer(layer, hold=True) 
    logger.info("interrupt recovered, ready to collect data, resetting stat counters")

    await boardDriver.resetLayerStatCounters(layer)

#######################################################
#################### MAIN FUNCTION ####################

async def main(args):
    # Welcome to the main (and only) function of this script!
    print(args) # Soon to be removed
    logger.debug("Start main()")
    # Setup FPGA communications
    boardDriver = drivers.boards.getCMODUartDriver("COM6")
    logger.debug(f"boardDriver instanciated: {boardDriver}")
    await boardDriver.open()
    logger.info("Opened FPGA, testing...")
    try:
        fwid = await boardDriver.readFirmwareID()
        logger.debug(f"FW ID: {fwid}")
    except Exception: 
        raise RuntimeError("Could not read or write from astropix!")
    logger.info("FPGA test successful.")
    logger.debug("Set sensor clocks.")
    await boardDriver.enableSensorClocks(flush = True)
    # Setup FPGA timestamps
    logger.debug("Configure FPGA TS freq.")
    await boardDriver.layersConfigFPGATimestampFrequency(targetFrequencyHz = 1000000, flush = True)
    logger.debug("Enable FPGA TS.")
    await boardDriver.layersConfigFPGATimestamp(enable = True, force = False, source_match_counter = True, source_external = False, flush = True)
    logger.debug("Configure SPI frequency.")
    await boardDriver.configureLayerSPIFrequency(targetFrequencyHz = 1000000, flush = True)
    logger.debug("Instanciate ASIC drivers ...")
    # Configure chips
    pathdelim = os.path.sep #determine if Mac or Windows separators in path name
    ymlpath = [os.getcwd()+pathdelim+"scripts"+pathdelim+"config"+pathdelim+ y +".yml" for y in args.yaml] # Define YAML path variables
    try:
        for layer, (nchips, yml) in enumerate(zip(args.chipsPerRow, ymlpath)):
            boardDriver.setupASIC(version = 3, row = layer, chipsPerRow = nchips , configFile = yml )
    except FileNotFoundError as e :
        logger.error(f'Config File {ymlpath} was not found, pass the name of a config file from the scripts/config folder')
        raise e
    logger.info(f"{len(boardDriver.asics)} ASIC drivers instanciated.")
    # Setup / configure injection
    if args.inject:
        logger.debug("Enable injection pixel")
        await astro.enable_injection(*args.inject)
        await astro.enable_pixel(*args.inject)
        logger.debug("Set injection voltage")
        # Priority to command line, defaults to yaml - already in vdac units
        try:
            if args.vinj is None:
                args.vinj = astro.boardDriver.asics[args.inject[0]].asic_config[f'config_{args.inject[1]}']['vdacs']['vinj'][1]
                await astro.init_injection(args.inject[0], args.inject[1], inj_voltage=args.vinj, is_mV=False)
            else:
                await astro.init_injection(args.inject[0], args.inject[1], inj_voltage=args.vinj)
        except (KeyError, IndexError):
            logger.error(f"Injection arguments layer={args.inject[0]}, chip={args.inject[1]} invalid. Cannot initialize injection.")
            args.inject = None
    # Setup / configure analog
    if args.analog:
        logger.debug("enable analog")
        await astro.enable_analog(*args.analog)
    # Reset chips
    #for i in range(5):
    #    print(f"Reset #{i}/5")
    #    _wait_progress(10)
    await boardDriver.setLayerConfig(layer=0, reset=True, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)#Reset is shared
    await asyncio.sleep(.5)
    await boardDriver.setLayerConfig(layer=0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # Set routing
    logger.info(f"Writting SPI Routing frame for layers {range(len(args.yaml))}")
    for layer in range(len(args.yaml)):
        await boardDriver.setLayerConfig(layer=layer, reset=False , autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)
    for layer in range(len(args.yaml)):
        _wait_progress(20)
        await boardDriver.asics[layer].writeSPIRoutingFrame()
    _wait_progress(30)
    await boardDriver.layersDeselectSPI(flush=True)
    
    # Write configuration to chips





#######################################################
#################### TOP LEVEL ########################

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Test program to run the A-STEP test bench.',
                                     formatter_class=argparse.RawTextHelpFormatter, #allow formatting of the epilog
                                     epilog="""""") 

    # Options related to outputs
    parser.add_argument('-o', '--outputPrefix', type=str, default="{0}{2}data{2}{1}".format(os.getcwd(), time.strftime("%Y%m%d-%H%M%S"), os.path.sep), 
                        help="Path to and beginning of the name of the data file(s) and log file, default: data/YYYYMMDD-HHMMSS")

    # Options related to software run settings
    parser.add_argument('-L', '--loglevel', type=str, choices = ['D', 'I', 'E', 'W', 'C'], action="store", default='I',
                        help='Set loglevel used. Options: D - debug, I - info, E - error, W - warning, C - critical. DEFAULT: I')
    parser.add_argument('-T', '--runTime', type=float, action='store',  default=None,
                        help = 'Maximum run time (in minutes). Default: NONE (run until user CTL+C)')
    
    # Options related to Setup / Configuration of system
    parser.add_argument('-y', '--yaml', action='store', required=False, type=str, default = ['quadChip_allOff'], nargs="+", 
                        help = 'filepath (in scripts/config/ directory) .yml file containing chip configuration. \
                                One file must be passed for each layer, from layer #0 to layer #2. \
                                Default: config/quadChip_allOff (All pixels off, only fisrt layer is configured)')
    parser.add_argument('-c', '--chipsPerRow', action='store', required=False, type=int, default = [4], nargs="+", 
                        help = 'Number of chips per SPI bus to enable. Can provide a single number or one number per bus. Default: 4')
    
    # Options related to Setup / Configuration of the chip in data collection run
    parser.add_argument('-na', '--noAutoread', action='store_true', required=False, 
                        help='If passed, does not enable autoread features off chip. If not passed, read data with autoread. Default: autoread')
    parser.add_argument('-t', '--threshold', type = int, action='store', default=100,
                        help = 'Threshold voltage for digital ToT (in mV). DEFAULT: 100')
    parser.add_argument('-a', '--analog', action='store', required=False, type=int, default = None, nargs=3,
                        help = 'Turn on analog output in the given column. Can only enable one analog pixel per layer. \
                        Requires input in the form {layer, chip, col} (no wrapping brackets). \
                        Default: None')
                        #Default: layer 1, chip 0, col 0')
    
    # Options related to chip injection
    ## DAN - this isn't working. Pixel response to "any" injected amplitude always the same 17 us ToT
    parser.add_argument('-i', '--inject', action='store', default=None, type=int, nargs=4,
                    help =  'Turn on injection in the given layer, chip, row, and column. Default: No injection')
    parser.add_argument('-v','--vinj', action='store', default = None,  type=int,
                        help = 'Specify injection voltage (in mV). DEFAULT: value in config ')

    args = parser.parse_args()
    
    # Define the loglevel
    ll = args.loglevel
    if ll == 'D':
        loglevel = logging.DEBUG ## DAN - not working! Causes runs to crash and read in tons of railed buffers after the alloted time???
    elif ll == 'I':
        loglevel = logging.INFO
    elif ll == 'E':
        loglevel = logging.ERROR
    elif ll == 'W':
        loglevel = logging.WARNING
    elif ll == 'C':
        loglevel = logging.CRITICAL
    logname = args.outputPrefix+"_run.log"
    formatter = logging.Formatter('%(asctime)s:%(msecs)d.%(name)s.%(levelname)s:%(message)s')
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

    #Layer counting begins at 0.
    #Make sure config arguments make sense
    if len(args.yaml) > len(args.chipsPerRow):
        if len(args.chipsPerRow) > 1:
            logger.warning(f"Number of chips per row not provided for every layer - default to {args.chipsPerRow[0]} for all {len(args.yaml)} layers.")
        args.chipsPerRow = [args.chipsPerRow[0]]*len(args.yaml)
    elif len(args.yaml) < len(args.chipsPerRow):
        raise ValueError("You need to provide one yaml configuration file for every chipsPerRow argument.")

    #Make sure analog/inject arguments make sense
    if args.analog is not None and (len(args.analog)!=3 or args.analog[0]<0 or args.analog[0]>2 or args.analog[1]<0 or args.analog[1]>3 or args.analog[2]<0):
        raise ValueError("Incorrect analog argument layer={0[0]},chip={0[1]},column={0[2]}".format(args.analog))
    if args.inject is not None and (len(args.inject)!=4 or args.inject[0]<0 or args.inject[0]>2 or args.inject[1]<0 or args.inject[1]>3 or args.inject[2]<0 or args.inject[3]<0):
        raise ValueError("Incorrect analog argument layer={0[0]},chip={0[1]},row={0[2]},column={0[3]}".format(args.inject))


    asyncio.run(main(args))

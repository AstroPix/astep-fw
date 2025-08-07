"""
Test program to run the A-STEP test bench.
First prototype of the A-STEP Detector flight software.

Author: Adrien Laviron (adrien.laviron@nasa.gov)
"""
import asyncio
import time, os
from tqdm import tqdm
import argparse

import drivers.boards
import drivers.astep.serial
import drivers.astropix.decode

# Logging stuff
import logging

async def buffer_flush(boardDriver, layerlst = range(3)):
    """This method flushes data from SPI lanes then from FPGA buffer, and resets counters"""
    logger.info("Flush chips before data collection")
    await boardDriver.holdLayers(hold=False, flush=True)
    for layer in layerlst:
        interrupt_counter=0
        interrupt = await boardDriver.getLayerStatus(layer)
        while interrupt&1 == 0 and interrupt_counter<20:
            logger.info("interrupt low")
            await boardDriver.layersSelectSPI(flush=True)
            await boardDriver.writeLayerBytes(layer = layer, bytes = [0x00] * 128, flush=True)
            await boardDriver.layersDeselectSPI(flush=True)
            interrupt_counter+=1
            interrupt = await boardDriver.getLayerStatus(layer)
    # Reassert hold to be safe
    await boardDriver.holdLayers(hold=True, flush=True)
    # Now all interrupts are high, empty FPGA buffer
    logger.info("Flush FPGA buffer before data collection")
    await(boardDriver.readoutReadBytes(4098))
    await boardDriver.resetLayerStatCounters(layer)

async def getBuffer(boardDriver):
  bufferSize = await boardDriver.readoutGetBufferSize()
  readout = await boardDriver.readoutReadBytes(bufferSize)
  return bufferSize, readout

#######################################################
#################### MAIN FUNCTION ####################

async def main(args):
    # Setup FPGA communications
    boardDriver = drivers.boards.getCMODUartDriver("COM6")
    await boardDriver.open()
    logger.info("Opened FPGA, testing...")
    try:
        fwid = await boardDriver.readFirmwareID()
        logger.info(f"FW ID: {fwid}")
    except Exception: 
        raise RuntimeError("Could not read or write from astropix!")
    await boardDriver.enableSensorClocks(flush = True)
    await boardDriver.layersConfigFPGATimestampFrequency(targetFrequencyHz = 1000000, flush = True)
    await boardDriver.layersConfigFPGATimestamp(enable = True, force = False, source_match_counter = True, source_external = False, flush = True)

    await boardDriver.configureLayerSPIDivider(20, flush = True)
    await boardDriver.rfg.write_layers_cfg_nodata_continue(value=8, flush=True)
    # Configure chips in memory
    pathdelim = os.path.sep #determine if Mac or Windows separators in path name
    ymlpath = [os.getcwd()+pathdelim+"scripts"+pathdelim+"config"+pathdelim+ y +".yml" for y in args.yaml] # Define YAML path variables
    try:
        for layer, (nchips, yml) in enumerate(zip(args.chipsPerRow, ymlpath)):
            boardDriver.setupASIC(version = 3, row = layer, chipsPerRow = nchips , configFile = yml )
    except FileNotFoundError as e :
        logger.error(f'Config File {ymlpath} was not found, pass the name of a config file from the scripts/config folder')
        raise e

    # Set multi-pix injection chip
    if args.confOverride:
        boardDriver.asics[1].asic_config["config_3"] = boardDriver.asics[1].asic_config["config_4"]

    logger.info(f"{len(boardDriver.asics)} ASIC drivers instanciated.")
    # Setup / configure injection
    if args.inject:
        boardDriver.asics[args.inject[0]].enable_inj_col(args.inject[1], args.inject[3], inplace=False)
        boardDriver.asics[args.inject[0]].enable_inj_row(args.inject[1], args.inject[2], inplace=False)
        boardDriver.asics[args.inject[0]].enable_pixel(chip=args.inject[1], col=args.inject[3], row=args.inject[2], inplace=False)
        # Priority to command line, defaults to yaml - already in vdac units
        try:
            if args.vinj is not None:
                boardDriver.asics[args.inject[0]].asic_config[f"config_{args.inject[1]}"]["vdacs"]["vinj"][1] = int(args.vinj/1000*1024/1.8)#1.8 V coded on 10 bits
            injector = boardDriver.getInjectionBoard(slot = 3)#ShortHand to configure on-chip injector
            injector.period, injector.clkdiv, injector.initdelay, injector.cycle, injector.pulsesperset = 100, 300, 100, 0, 1#Default set of parameters
            await boardDriver.ioSetInjectionToGeccoInjBoard(enable = False, flush = True)#ShortHand for writing the correct registers on-chip, ignore reference to Gecco
        except (KeyError, IndexError):
            logger.error(f"Injection arguments layer={args.inject[0]}, chip={args.inject[1]} invalid. Cannot initialize injection.")
            args.inject = None

    layerlst = range(len(args.yaml))
    await boardDriver.disableLayersReadout(flush=True)#Hold, disableMISO, disableAutoread, CS=inactive
    await boardDriver.resetLayersFull()

    # Set chip IDs
    await boardDriver.layersSelectSPI(flush=True)
    for layer in layerlst:
        await boardDriver.asics[layer].writeSPIRoutingFrame(0)
    await boardDriver.layersDeselectSPI(flush=True)
    
    for i in range(args.chipsPerRow[layer]):
        await boardDriver.layersSelectSPI(flush=True)
        for layer in layerlst:
            if i < args.chipsPerRow[layer]:
                payload = boardDriver.asics[layer].createSPIConfigFrame(load=True, n_load=10, broadcast=False, targetChip=i)
                await boardDriver.asics[layer].writeSPI(payload)
        await boardDriver.layersDeselectSPI(flush=True)
    # Flush old data
    await buffer_flush(boardDriver, layerlst)

    # Final setup
    if args.inject:
        await injector.start()
        dataStream_lst = []
        bufferLength_lst = []
    else:
        ofile = open("{}.bin".format(args.outputPrefix), "wb")
    if args.runTime is not None: 
        end_time=time.time()+(args.runTime*60.)
    else:
        end_time = float('inf')
    
    # Enable readout
    await boardDriver.enableLayersReadout(layerlst, autoread=not(args.noAutoread), flush=True)
    
    # Main loop
    run = time.time() < end_time
    while run:
        try:
            if args.noAutoread:
                for layer in layerlst:
                    await boardDriver.writeLayerBytes(layer = layer, bytes = [0x00] * 255, flush=True)
            # Read data
            task = asyncio.create_task(getBuffer(boardDriver))
            await task
            buff, readout = task.result()
            if args.inject:
                # Store data
                dataStream_lst.append(readout)
                bufferLength_lst.append(buff)
                await printStatus(boardDriver, time.time()-end_time, buff=buff)
            else:
                if buff > 0:
                    ofile.write(readout)
            run = time.time() < end_time
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("[Ctrl+C] while in main loop - exiting.")
            run=False
    await printStatus(boardDriver, time.time()-end_time)
    # Pause readout
    await boardDriver.disableLayersReadout(flush=True)
    
    # End injection
    if args.inject: await injector.stop()
    else: ofile.close()
    
    # End connection
    await boardDriver.close()






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
    parser.add_argument('-r', '--readout', default=0, type=int,
                        help = 'Number of bytes of FPGA buffer to read for each readout (1 to 4098, 0->As much as buffer contains, other->4096). Default: 0')
    
    # Options related to Setup / Configuration of system
    parser.add_argument('-y', '--yaml', action='store', required=False, type=str, default = ['quadchip_allOff'], nargs="+", 
                        help = 'filepath (in scripts/config/ directory) .yml file containing chip configuration. \
                                One file must be passed for each layer, from layer #0 to layer #2. \
                                Default: config/quadChip_allOff (All pixels off, only fisrt layer is configured)')
    parser.add_argument('-c', '--chipsPerRow', action='store', required=False, type=int, default = [4], nargs="+", 
                        help = 'Number of chips per SPI bus to enable. Can provide a single number or one number per bus. Default: 4')
    parser.add_argument('--config-override', dest='confOverride', action='store_true',
                        help = "Execute a special line of code that applies hard-coded configuration changes - do not use unless you have read the code and know what you are doing!")
    
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

    #Sanitizing args.readout
    if args.readout == 0: args.readout = None
    elif args.readout < 0 or args.readout > 4098: args.readout = 4096


    asyncio.run(main(args))


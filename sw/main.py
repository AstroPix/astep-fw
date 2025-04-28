"""
Test program to run the A-STEP test bench.

Author: Adrien Laviron, adrien.laviron@nasa.gov
"""
# Needed modules. They all import their own suppourt libraries, 
# and eventually there will be a list of which ones are needed to run
import pandas as pd
import asyncio
import time, os, sys, binascii, math
from tqdm import tqdm
import argparse

import drivers.boards
import drivers.astep.serial
import drivers.astropix.decode

# Logging stuff
import logging


async def buffer_flush(boardDriver):
    """This method will ensure the layer interrupt is not low and flush buffer, and reset counters"""
    # Flush data from sensor
    logger.info("Flush chip before data collection")
    # Deassert hold
    await boardDriver.holdLayers(hold=False, flush=True)
    # Flush chips and SPI lines
    interruptn = [1, 1, 1]
    for layer in range(3):
        await boardDriver.writeLayerBytes(layer=layer, bytes=[0x00]*128, flush=True)
        interruptn[layer] &= await boardDriver.getLayerStatus(layer)
    # Keep flushing until interrupt is high
    interupt_counter=0
    while 0 in interruptn and interupt_counter<20:
        logger.info("interrupt low")
        for layer, i in enumerate(interruptn):
            if i == 0:#if interrupt low
                await boardDriver.writeLayerBytes(layer = layer, bytes = [0x00] * 128, flush=True)
        nmbBytes = await boardDriver.readoutGetBufferSize()
        if nmbBytes > 0:
            await boardDriver.readoutReadBytes(1024)
        interruptn = [1, 1, 1]
        for layer in range(3):
            interruptn[layer] &= await boardDriver.getLayerStatus(layer)
        interupt_counter+=1
        logger.info(f"Buffer size = {nmbBytes} B")
    # Now all interrupts are high, empty FPGA buffer
    buff, readout = await get_readout(boardDriver)
    # Reassert hold to be safe
    await boardDriver.holdLayers(hold=True, flush=True)
    if buff > 0:
        logger.info(binascii.hexlify(readout))
        logger.info(f"Buffer size = {buff} B")
    logger.info("interrupt recovered, ready to collect data, resetting stat counters")
    await boardDriver.resetLayerStatCounters(layer)

async def get_readout(boardDriver, counts:int = 4096):
    bufferSize = await(boardDriver.readoutGetBufferSize())
    readout = await(boardDriver.readoutReadBytes(counts))
    return bufferSize, readout

async def getBuffer(boardDriver):
  bufferSize = await boardDriver.readoutGetBufferSize()
  readout = await boardDriver.readoutReadBytes(bufferSize)
  return bufferSize, readout

#Parse raw data readouts to remove railing. Moved to postprocessing method to avoid SW slowdown when using autoread
def dataParse_autoread(data_lst, buffer_lst, bitfile:str = None):
    allData = b''
    for i, buff in enumerate(buffer_lst):
        if buff>0:
            readout_data = data_lst[i][:buff]
            #logger.info(binascii.hexlify(readout_data))
            allData+=readout_data
            if bitfile:
                bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")
    ## DAN - could also return buffer index to keep track of whether multiple hits occur in the same readout. Would need to propagate forward
    return allData

async def printStatus(boardDriver, time=0., buff=0):
    status = [await boardDriver.getLayerStatus(layer) for layer in range(3)]
    ctrl = [await boardDriver.getLayerControl(layer) for layer in range(3)]
    wrongl = [await boardDriver.getLayerWrongLength(layer) for layer in range(3)]
    logger.info("[{time:04.2} s] buff={0:04d} status: 0={1[0]:02b}-{2[0]:06b}-{3[0]:04d} 1={1[1]:02b}-{2[1]:06b}-{3[1]:04d} 2={1[2]:02b}-{2[2]:06b}-{3[1]:04d}"\
                .format(buff, status, ctrl, wrongl, time=time))

# Needed to decode data
class myhack:
    def __init__(self):
        self.sampleclock_period_ns = 10

def bin2csv(fprefix):
    with open("{}.bin".format(fprefix), "rb") as ofile:
        datalst = []
        i = 0
        while (data := ofile.read(4096)):
            datalst.append( drivers.astropix.decode.decode_readout(myhack(), logger, data, i=i, printer=False) )
            i += 1
    csvframe = ['readout', 'layer', 'chipID', 'payload', 'location', 'isCol', 'timestamp', 'tot_msb', 'tot_lsb', 'tot_total', 'tot_us', 'fpga_ts']
    df = pd.concat(datalst)
    df.columns = csvframe
    df.to_csv(fprefix+".csv")

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
    # await boardDriver.ioSetTimestampClock(enable=False, flush=True)
    # Setup FPGA timestamps
    # logger.debug("Configure FPGA TS freq.")
    # await boardDriver.layersConfigFPGATimestampFrequency(targetFrequencyHz = 1000000, flush = True)
    # logger.debug("Enable FPGA TS.")
    # await boardDriver.layersConfigFPGATimestamp(enable = True, force = False, source_match_counter = True, source_external = False, flush = True)
    logger.debug("Configure SPI readout")
    await boardDriver.configureLayerSPIDivider(20, flush = True)
    await boardDriver.rfg.write_layers_cfg_nodata_continue(value=8, flush=True)
    logger.debug("Instanciate ASIC drivers ...")
    # Configure chips in memory
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
        boardDriver.asics[args.inject[0]].enable_inj_col(args.inject[1], args.inject[3], inplace=False)
        boardDriver.asics[args.inject[0]].enable_inj_row(args.inject[1], args.inject[2], inplace=False)
        boardDriver.asics[args.inject[0]].enable_pixel(chip=args.inject[1], col=args.inject[3], row=args.inject[2], inplace=False)
        logger.debug("Set injection voltage")
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
    # Setup / configure analog
    if args.analog:
        logger.debug("enable analog")
        boardDriver.asics[args.analog[0]].enable_ampout_col(args.analog[1], args.analog[2], inplace=False)

    await printStatus(boardDriver)
    for layer in range(3): await boardDriver.zeroLayerWrongLength(layer, flush=True)

    layerlst = range(len(args.yaml))
    await boardDriver.disableLayersReadout(flush=True)#Hold, disableMISO, disableAutoread, CS=inactive
    await boardDriver.resetLayersFull()#Toggle RST

    # Set chip IDs
    await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
    for layer in layerlst:
        await boardDriver.asics[layer].writeSPIRoutingFrame(0)
    await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect
        
    #for layer in layerlst:
    for i in range(args.chipsPerRow[layer]):
        await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
        for layer in layerlst:
            if i < args.chipsPerRow[layer]:
                payload = boardDriver.asics[layer].createSPIConfigFrame(load=True, n_load=10, broadcast=False, targetChip=i)
                await boardDriver.asics[layer].writeSPI(payload)
        await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect
    # Flush old data
    await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
    await buffer_flush(boardDriver)#Exit with hold active
    await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect

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
    await boardDriver.enableLayersReadout(layerlst, autoread=True, flush=True)
    
    # Main loop
    run = time.time() < end_time
    while run:
        try:
            # Read data
            task = asyncio.create_task(get_readout(boardDriver))
            await task
            buff, readout = task.result()
            if args.inject:
                # Store data
                dataStream_lst.append(readout)
                bufferLength_lst.append(buff)
                await printStatus(boardDriver, time.time()-end_time, buff=buff)
            else:
                ofile.write(readout)
            print(f"  {buff:04d}  ", end="\r")
            # logger.info(binascii.hexlify(readout[:buff]))
            # Check time
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

    #Process data
    if args.inject:
        print(len(bufferLength_lst), max(bufferLength_lst))
        dataStream = dataParse_autoread(dataStream_lst, bufferLength_lst, None)
        df = drivers.astropix.decode.decode_readout(myhack(), logger, dataStream, i=0, printer=True)
        if len(df) > 0:
            csvframe = ['readout', 'layer', 'chipID', 'payload', 'location', 'isCol', 'timestamp', 'tot_msb', 'tot_lsb', 'tot_total', 'tot_us', 'fpga_ts']
            df.columns = csvframe
            df.to_csv(args.outputPrefix+".csv")
        else:
            logger.warning("No data written to disk because none have been received.")
    else:
        bin2csv(args.outputPrefix)
        






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
    parser.add_argument('-y', '--yaml', action='store', required=False, type=str, default = ['quadchip_allOff'], nargs="+", 
                        help = 'filepath (in scripts/config/ directory) .yml file containing chip configuration. \
                                One file must be passed for each layer, from layer #0 to layer #2. \
                                Default: config/quadChip_allOff (All pixels off, only fisrt layer is configured)')
    parser.add_argument('-c', '--chipsPerRow', action='store', required=False, type=int, default = [4], nargs="+", 
                        help = 'Number of chips per SPI bus to enable. Can provide a single number or one number per bus. Default: 4')
    
    # Options related to Setup / Configuration of the chip in data collection run
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


    asyncio.run(main(args))


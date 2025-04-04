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
    if interruptn == 0: await boardDriver.holdLayers(hold=False, flush=True)
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
    await boardDriver.holdLayers(hold=True, flush=True) 
    logger.info("interrupt recovered, ready to collect data, resetting stat counters")
    await boardDriver.resetLayerStatCounters(layer)

async def get_readout(boardDriver, counts:int = 4096):
    bufferSize = await(boardDriver.readoutGetBufferSize())
    readout = await(boardDriver.readoutReadBytes(counts))
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

async def printStatus(boardDriver, time=0, buff=0):
    status = [await boardDriver.getLayerStatus(layer) for layer in range(3)]
    ctrl = [await boardDriver.getLayerControl(layer) for layer in range(3)]
    print("[{time:04.2} s] buff={0:04d} status: 0={1[0]:02b}-{2[0]:06b} 1={1[1]:02b}-{2[1]:06b} 2={1[2]:02b}-{2[2]:06b}".format(buff, status, ctrl, time=time), flush=True)



# Needed to decode data
class myhack:
    def __init__(self):
        self.sampleclock_period_ns = 10

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
    # logger.debug("Configure FPGA TS freq.")
    # await boardDriver.layersConfigFPGATimestampFrequency(targetFrequencyHz = 1000000, flush = True)
    # logger.debug("Enable FPGA TS.")
    # await boardDriver.layersConfigFPGATimestamp(enable = True, force = False, source_match_counter = True, source_external = False, flush = True)
    logger.debug("Configure SPI frequency.")
    await boardDriver.configureLayerSPIDivider(20, flush = True)
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
    #_wait_progress(3)
    # Reset layers without any other changes
    #await boardDriver.resetLayers()

    # TEST RANGE
    #cycle CS to trigger oscilloscope
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=True, disableMISO=True, flush=True)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=True, disableMISO=True, flush=True)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # for layer in range(3):
    #     await boardDriver.setLayerConfig(layer=layer, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=False, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=False, hold=False, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=True, autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=True, autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=True, autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.2)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=False, hold=False, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=False, chipSelect=True, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=True, hold=False, chipSelect=True, disableMISO=False, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=True, hold=False, chipSelect=True, disableMISO=False, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=True, hold=False, chipSelect=True, disableMISO=False, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=False, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(1, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=False, flush=True)
    # time.sleep(.1)
    # await boardDriver.setLayerConfig(2, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=False, flush=True)
    # time.sleep(.1)
    # buff, readout = await(get_readout(boardDriver))
    # readout_data = readout[:buff]
    # logger.info(f"{buff} bytes in buffer")
    # logger.info(binascii.hexlify(readout_data)) 
    # df = drivers.astropix.decode.decode_readout(myhack(), logger, readout_data, 0, printer=True)
    # time.sleep(.1)
    # time.sleep(.1)
    # for layer in range(3):
    #     print("layer {}: {}".format(layer, bin(await getattr(boardDriver.rfg, f"read_layer_{layer}_cfg_ctrl")())))
    # time.sleep(.1)
    # return


    layerlst = range(len(args.yaml))
    #layerlst=[1]
    # for layer in range(3):
    #     await boardDriver.setLayerConfig(layer=layer, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    # await boardDriver.holdLayers(hold=True, flush=True)
    # for layer in range(3):
    #     regval = await getattr(boardDriver.rfg, f"read_layer_{layer}_cfg_ctrl")()
    #     print(bin(regval))
    await boardDriver.disableLayersReadout(flush=True)#Hold, disableMISO, disableAutoread, CS=inactive
    await boardDriver.resetLayers()#Toggle RST
    #await asyncio.sleep(0.2)
    # for layer in layerlst:
    #     await boardDriver.setLayerConfig(layer=layer, reset=False , autoread=False, hold=True, chipSelect=False, disableMISO=True, flush=True)

    # Set chip IDs
    # for layer in range(3):
    #     regval = await getattr(boardDriver.rfg, f"read_layer_{layer}_cfg_ctrl")()
    #     print(bin(regval))
    for layer in layerlst:
        #await boardDriver.setLayerConfig(layer=layer, reset=False , autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)#Set chipSelect
        #await boardDriver.layerSelectSPI(layer, True, flush=True)
        await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
        # print("layer {}: {}".format(layer, bin(await getattr(boardDriver.rfg, f"read_layer_{layer}_cfg_ctrl")())))
    #for layer in layerlst:
        await boardDriver.asics[layer].writeSPIRoutingFrame(0)
        await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect
        #await boardDriver.layerSelectSPI(layer, False, flush=True)#Unset chipSelect
        
        #await asyncio.sleep(0.2)
    # Set layer configs
    #for layer in layerlst:
    #for i in range(max(args.chipsPerRow)):
        for i in range(args.chipsPerRow[layer]):
            #_wait_progress(2)
            #await boardDriver.setLayerConfig(layer=layer, reset=False , autoread=False, hold=True, chipSelect=True, disableMISO=True, flush=True)#Set chipSelect
            #await boardDriver.layerSelectSPI(layer, True, flush=True)
            await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
            # print("layer {}, chip {}: {}".format(layer, i, bin(await getattr(boardDriver.rfg, f"read_layer_{layer}_cfg_ctrl")())))
        #for layer in layerlst:
        #    if i < args.chipsPerRow[layer]:
            payload = boardDriver.asics[layer].createSPIConfigFrame(load=True, n_load=10, broadcast=False, targetChip=i)
            await boardDriver.asics[layer].writeSPI(payload)
            #await boardDriver.layerSelectSPI(layer, False, flush=True)#Unset chipSelect
            await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect
        #await asyncio.sleep(0.1)
    # for layer in range(3):
        # regval = await getattr(boardDriver.rfg, f"read_layer_{layer}_cfg_ctrl")()
        # print(bin(regval))
    # Flush old data
    #for layer in layerlst:
    await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
    for layer in layerlst:
        await buffer_flush(boardDriver, layer=layer)#Exit with hold active

# Atten-tchun: hold is shared so interrupt can go back up in th e layer we're not flushing ...

    await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect
    #await asyncio.sleep(0.2)
    # Final setup
    if args.inject: await injector.start()
    dataStream_lst = []
    bufferLength_lst = []
    if args.runTime is not None: 
        end_time=time.time()+(args.runTime*60.)
    else:
        end_time = float('inf')
    
    await boardDriver.enableLayersReadout(layerlst, autoread=not(args.noAutoread), flush=True)
    # for layer in layerlst:
    #     #await asyncio.sleep(0.5)
    #     await boardDriver.setLayerConfig(layer=layer, reset=False, autoread=not(args.noAutoread), hold=False, chipSelect=False, disableMISO=False, flush=True)#Enable readout
    # await boardDriver.layersSelectSPI()
    # await boardDriver.holdLayers(hold=False, flush=True)
    #     #await boardDriver.setLayerConfig(layer=layer, reset=False , autoread=True, hold=False, chipSelect=True, disableMISO=False, flush=)#Flush once
    
    # Main loop
    run = time.time() < end_time
    while run:
        try:
            if args.noAutoread:#Manually pull data out of chips - not very stable
                task = asyncio.create_task(asyncio.sleep(1))
                await task
                # for layer in layerlst:
                #     await boardDriver.writeLayerBytes(layer = layer, bytes = [0x00] * 10, flush=True)
                #     buff = await boardDriver.readoutGetBufferSize()
                #     #if buff > 0:
                #     readout = await boardDriver.readoutReadBytes(22)
                #     # Store data
                #     dataStream_lst.append(readout)
                #     bufferLength_lst.append(buff)
                #     print(f"{buff}    ", end='\r', flush=True)
            else:
                # Read data
                task = asyncio.create_task(get_readout(boardDriver))
                await task
                buff, readout = task.result()
                # Store data
                dataStream_lst.append(readout)
                bufferLength_lst.append(buff)
                await printStatus(boardDriver, time.time()-end_time, buff=buff)
            # Check time
            run = time.time() < end_time
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("[Ctrl+C] while in main loop - exiting.")
            run=False
    await printStatus(boardDriver, time.time()-end_time)
    # Pause readout
    await boardDriver.disableLayersReadout(flush=True)
    # for layer in range(3):
    #     await boardDriver.setLayerConfig(layer=layer, reset=False , autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)
    
    await printStatus(boardDriver, time.time()-end_time)
    # End injection
    if args.inject: await injector.stop()
    
    await printStatus(boardDriver, time.time()-end_time)
    # End connection
    await boardDriver.close()

    #Process data
    if args.noAutoread:
    #if was not autoreading, process the info that was collected
        # logger.debug("read out buffer")
        buff, readout = await(get_readout(boardDriver))
        readout_data = readout[:buff]
        # logger.info(binascii.hexlify(readout_data))
        logger.info(f"{buff} bytes in buffer")
        df = drivers.astropix.decode.decode_readout(myhack(), logger, readout_data, 0, printer=True)
    else:
        print(len(bufferLength_lst), max(bufferLength_lst))
        # Save data
        # for d in dataStream_lst:
        #     logger.info(binascii.hexlify(d))
        if args.inject or False:
            dataStream = dataParse_autoread(dataStream_lst, bufferLength_lst, None)
            df = drivers.astropix.decode.decode_readout(myhack(), logger, dataStream, i=0, printer=True)
            if len(df) > 0:
                csvframe = ['readout', 'layer', 'chipID', 'payload', 'location', 'isCol', 'timestamp', 'tot_msb', 'tot_lsb', 'tot_total', 'tot_us', 'fpga_ts']
                df.columns = csvframe
                df.to_csv(args.outputPrefix+".csv")
            else:
                logger.warning("No data written to disk because none have been received.")
        else: # TBC
            csvframe = ['readout', 'layer', 'chipID', 'payload', 'location', 'isCol', 'timestamp', 'tot_msb', 'tot_lsb', 'tot_total', 'tot_us', 'fpga_ts']
            datalst = []
            for i, (buff, data) in enumerate(zip(bufferLength_lst, dataStream_lst)):
                if buff > 0:
                    datalst.append( drivers.astropix.decode.decode_readout(myhack(), logger, data, i=i, printer=False) )
            df = pd.concat(datalst)
            df.columns = csvframe
            df.to_csv(args.outputPrefix+".csv")
        






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



"""

    # Check chips ID here?
    
    # Write configuration to chips
    #_wait_progress(5)
    #for layer in range(len(args.yaml)):#set everytinhg but chipSelect
    #    await boardDriver.setLayerConfig(layer=layer, reset=False , autoread=False, hold=True, chipSelect=False, disableMISO=True, flush=True)
    
    # Automated procedure (not working?)
    #boardDriver.asics[0].writeConfigSPI()
    
    # Inspect frame of a single chip config
    #for b in boardDriver.asics[0].gen_config_vector_SPI(targetChip=0):
    #        print(int(b), end="")
    #print(flush=True)
    #payload = boardDriver.asics[0].createSPIConfigFrame(load=True, n_load=5, broadcast=False, targetChip=1)
    #for b in payload:
    #    print(int(b), end="")
    #step  = 256
    #steps = int(math.ceil(len(payload)/step))
    #for chunk in range(0, len(payload), step):
    #    chunkBytes = payload[chunk:chunk+step]
    #    for b in chunkBytes:
    #        print(int(b), end=" ")
    #    print("{}/{} len={}".format((chunk/step+1),steps,len(chunkBytes)))
    #print(flush=True)
    #await boardDriver.asics[0].writeSPI(payload)
    
    # Loop over N chips
    #for i in range(args.chipsPerRow[0]-1, -1, -1):
    
    # With broadcast
    #_wait_progress(20)
    #await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
    #await boardDriver.asics[0].writeConfigSPI(broadcast = True, targetChip = 1)
    #await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect

    if False:
        # This is the current test zone
        layer = 0
        payload0 = boardDriver.asics[layer].createSPIConfigFrame(load=True, n_load=10, broadcast=False, targetChip=0) # Will set injector ON in command line
        payload1 = boardDriver.asics[layer].createSPIConfigFrame(load=True, n_load=10, broadcast=False, targetChip=1) # Injector OFF by default
        #for i, (b0, b1) in enumerate(zip(payload0, payload1)):
        #    print("{}\t{} {}".format(i, b0, b1))
        route = payload0[0]
        
        for chip in [0, 1, 2, 3]:  #   Change number and ID of chips to configure HERE
            await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
            if chip == 3:   #   Change chip ID whose injector is ON HERE
                payload0[0]=route+chip
                await boardDriver.asics[layer].writeSPI(payload0)
            else:
                payload1[0]=route+chip
                await boardDriver.asics[layer].writeSPI(payload1)
            await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect
            #_wait_progress(1)

    if 0:# True to reset and re-send routing frame - necessary when configuring >2 chips - not anymore
        await boardDriver.setLayerConfig(layer=0, reset=True, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)#Reset is shared
        await asyncio.sleep(.5)
        await boardDriver.setLayerConfig(layer=0, reset=False, autoread=False, hold=False, chipSelect=False, disableMISO=True, flush=True)

        await boardDriver.layersSelectSPI(flush=True)#Set chipSelect
        await boardDriver.asics[layer].writeSPIRoutingFrame(0)
        await boardDriver.layersDeselectSPI(flush=True)#Unset chipSelect



"""
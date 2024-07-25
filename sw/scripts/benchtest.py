import asyncio
from astep import astepRun
import pandas as pd
import binascii
import logging
import time
import argparse
import os

#######################################################
############## USER DEFINED VARIABLES #################
layer, chip = 0,1
pixel = [layer, chip, 0, 30] #layer, chip, row, column
configViaSR = False #if False, config with SPI
inj_voltage = 300 #injection amplitude in mV
threshold = 200 #global comparator threshold level in mV
runTime = 5 #duration of run in s
chipsPerRow = 2 #number of arrays per SPI bus to configure
gecco = True
logLevel = logging.INFO #DEBUG, INFO, WARNING, ERROR, CRITICAL
injection = True
debug = False #If true, print data to screen in real time even if it results in a SW slowdown. Use False for efficient data collection mode
#######################################################

async def main(args, saveName):

    # Define outputs
    bitpath = args.outdir+saveName+".txt"
    csvpath = args.outdir+saveName+".csv"
    if not args.dumpOutput:
        bitfile = open(bitpath,'w')    

    logger.debug("creating object")
    astro = astepRun(inject=pixel,SR=configViaSR)

    logger.debug("opening fpga")
    cmod = False if gecco else True
    uart = False if gecco else True
    await astro.open_fpga(cmod=cmod, uart=uart)

    logger.debug("setup clocks")
    await astro.setup_clocks()

    logger.debug("setup spi")
    await astro.enable_spi()
    
    logger.debug("initializing asic")
    await astro.asic_init(yaml="quadchip_allOff", chipsPerRow=chipsPerRow, analog_col=[layer, chip, pixel[3]])
    logger.debug(f"Header: {astro.get_log_header(layer, chip)}")

    if gecco:
        logger.debug("initializing voltage")
        await astro.init_voltages(vthreshold=threshold) ## th in mV

    #loger.debug("FUNCTIONALITY CHECK")
    #await astro.functionalityCheck(holdBool=True)

    ## DAN - confirm functionality
    #logger.debug("update threshold")
    #await astro.update_pixThreshold(layer, chip, 100)

    logger.debug("enable pixel")
    await astro.enable_pixel(layer, chip, pixel[2], pixel[3])  

    if gecco and injection:
        ## DAN - implement injection for CMOD without using injectioncard/voltagecard methods unique to GECCO
        logger.debug("init injection")
        await astro.init_injection(layer, chip, inj_voltage=inj_voltage)

    logger.debug("final configs")
    for l in range(layer+1):
        logger.debug(f"Header: {astro.get_log_header(l, chip)}")
        await astro.asic_configure(l)
    
        logger.debug("setup readout")
        #pass layer number
        await astro.setup_readout(l, autoread=int(autoread_int)) 

    if gecco and injection:
        logger.debug("start injection")
        #await astro.checkInjBits()
        await astro.start_injection()
        #await astro.checkInjBits()

    #collect data
    if args.noAutoread:
        astro._wait_progress(runTime)
    else:    
        t0 = time.time()
        dataStream = b''
        dataStream_lst = []
        bufferLength_lst = []

        # WARNING - live string parsing causes SW-induced slowdown and results in lower overall data rate. Enabled in "debug" mode
        # Efficient data collection strategy = collect full buffers during running and process after the run. Default when not in "debug" mode
        while (time.time() < t0+runTime):
            buff, readout = await(astro.get_readout())
            if debug:
                if buff>0:
                    readout_data = readout[:buff]
                    logger.info(binascii.hexlify(readout_data))
                    logger.info(f"{buff} bytes in buffer")
                    dataStream+=readout_data
                    if not args.dumpOutput:
                        bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")
            else:
                dataStream_lst.append(readout)
                bufferLength_lst.append(buff)

        if not debug:
            #AFTER data collection, parse the raw data and save to file
            txtOut = None if args.dumpOutput else bitfile
            dataStream = await astro.dataParse_autoread(dataStream_lst, bufferLength_lst, bitfile=txtOut)
            if not args.dumpOutput:
                bitfile.write(str(binascii.hexlify(dataStream)))

        #wait to decode until the very end so that all readouts can be appended together and headers re-attached
        #loose info about which hit comes from which readout buffer
            ## DAN - consider whether readout buffer number is worth saving. 
            ## DAN - Think about way to break up how much is stored in memory at one time before storing somewhere. Should still decode at the end (of some interval of time) but not save to store all in dynamic RAM the whole time
        df = astro.decode_readout(dataStream,i=0) #i is meant to be readout stream increment

    if gecco and injection:
        logger.debug("stop injection")
        #await astro.checkInjBits()
        await astro.stop_injection()
        #await astro.checkInjBits()

    #if was not autoreading, process the info that was collected
    if args.noAutoread:
        logger.debug("read out buffer")
        buff, readout = await(astro.get_readout())
        readout_data = readout[:buff]
        logger.info(binascii.hexlify(readout_data))
        logger.info(f"{buff} bytes in buffer")
        df = astro.decode_readout(readout_data, 0)
        if not args.dumpOutput:
            bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")
         
    if not args.dumpOutput:    
        bitfile.close()  
        csvframe = [
                'readout',
                'layer',
                'chipID',
                'payload',
                'location',
                'isCol',
                'timestamp',
                'tot_msb',
                'tot_lsb',
                'tot_total',
                'tot_us',
                'fpga_ts'
        ]
        try:
            df.columns = csvframe
            df.to_csv(csvpath)
        except ValueError: #no data returned so empty DF of decoded hits
            logger.Error(f"No data recorded - no CSV generated")
            raise

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A-STEP Bench Testing Code for chip configuration and data collection')

    parser.add_argument('-n', '--name', default='', required=False,
                    help='Option to give additional name to output files upon running. Default: NONE')

    parser.add_argument('-o', '--outdir', default='data/', required=False,
                    help='Output Directory for all datafiles, as a subdir within data/. Default: data/')

    ## DAN - I hate this saving strategy. Should think of a better way. Implementation is backwards and messy
    parser.add_argument('-d', '--dumpOutput', action='store_true', 
                default=False, required=False, 
                help='If passed, do not save raw data *.txt or decoded *.csv. If not passed, save the outputs. Log always saved. Default: FALSE')
    
    parser.add_argument('-na', '--noAutoread', action='store_true', 
                default=False, required=False, 
                help='If passed, does not enable autoread features off chip. If not passed, read data with autoread. Default: FALSE')

    """
    parser.add_argument('-y', '--yaml', action='store', required=False, type=str, default = 'testconfig',
                    help = 'filepath (in config/ directory) .yml file containing chip configuration. Default: config/testconfig.yml (All pixels off)')
    
    parser.add_argument('-i', '--inject', action='store', default=None, type=int, nargs=2,
                    help =  'Turn on injection in the given row and column. Default: No injection')

    parser.add_argument('-v','--vinj', action='store', default = None, type=float,
                    help = 'Specify injection voltage (in mV). DEFAULT 300 mV')

    parser.add_argument('-a', '--analog', action='store', required=False, type=int, default = 0,
                    help = 'Turn on analog output in the given column. Default: Column 0.')

    parser.add_argument('-t', '--threshold', type = float, action='store', default=None,
                    help = 'Threshold voltage for digital ToT (in mV). DEFAULT 100mV')
    
    parser.add_argument('-E', '--errormax', action='store', type=int, default='100', 
                    help='Maximum index errors allowed during decoding. DEFAULT 100')

    parser.add_argument('-r', '--maxruns', type=int, action='store', default=None,
                    help = 'Maximum number of readouts')

    parser.add_argument('-M', '--maxtime', type=float, action='store', default=None,
                    help = 'Maximum run time (in minutes)')

    parser.add_argument('-L', '--loglevel', type=str, choices = ['D', 'I', 'E', 'W', 'C'], action="store", default='I',
                    help='Set loglevel used. Options: D - debug, I - info, E - error, W - warning, C - critical. DEFAULT: D')
    """

    args = parser.parse_args()

    #Checks for outdir path
    if args.outdir != "data/":
            args.outdir = "data/"+args.outdir
    #check 'outdir' argument and add '/' if necessary
    if args.outdir[-1]!="/":
            args.outdir+="/"
    # Ensures output directory exists
    if os.path.exists(args.outdir) == False:
        os.mkdir(args.outdir)

    """
    # Sets the loglevel
    ll = args.loglevel
    if ll == 'D':
        loglevel = logging.DEBUG
    elif ll == 'I':
        loglevel = logging.INFO
    elif ll == 'E':
        loglevel = logging.ERROR
    elif ll == 'W':
        loglevel = logging.WARNING
    elif ll == 'C':
        loglevel = logging.CRITICAL
    """
    
    #Define output save name for all files
    fname="" if not args.name else args.name+"_"
    saveName = fname + time.strftime("%Y%m%d-%H%M%S") 

    # Logging 
    logname = args.outdir+saveName+"_run.log"
    formatter = logging.Formatter('%(asctime)s:%(msecs)d.%(name)s.%(levelname)s:%(message)s')
    fh = logging.FileHandler(logname)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logging.getLogger().addHandler(sh) 
    logging.getLogger().addHandler(fh)
    logging.getLogger().setLevel(logLevel)
    global logger 
    logger = logging.getLogger(__name__)
    logger.info("Setup logger")

    #Define autoread bool
    autoread_int = 0 if args.noAutoread else 1

    asyncio.run(main(args, saveName))
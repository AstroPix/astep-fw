import asyncio
from astep import astepRun
import sys
import pandas as pd
import binascii
import logging
import time
import argparse
from argparse import RawTextHelpFormatter
import os, serial


#######################################################
############## USER DEFINED VARIABLES #################
#layer, chip = 0, 0


#######################################################
###################### MAIN ###########################
async def main(args, saveName):

    # Define outputs
    bitpath = args.outdir+saveName+".txt"
    csvpath = args.outdir+saveName+".csv"
    if not args.dumpOutput:
        bitfile = open(bitpath,'w')    

    # Setup and configure chip
    logger.debug("creating object")
    astro = astepRun(SR=args.shiftRegister)

    
    cmod = False if args.gecco else True
    uart = False if args.gecco else True

    logger.info(f"opening fpga,cmod={cmod},uart={uart}")
    try:
        await astro.open_fpga(cmod=cmod, uart=uart)
    except serial.SerialException: 
        logger.error("Cannot find Serial Port to open to CMOD/UART. If using GECCO setup, make sure to pass -g argument.")
        return

    logger.debug("setup clocks")
    await astro.setup_clocks()
    # enabling fpga tag disabled until tested
    #await astro.setup_fpgatag()
    #await astro.enable_fpgatag()

    logger.debug("setup spi")
    await astro.enable_spi()
    logger.info(f"initializing asic,config={args.yaml},chips={args.chipsPerRow}")
    ## DAN - all config dictionaries in one file. May want to separate into individual files for each chip and/or only input vdacs/idacs/etc one time and apply to all chips
    await astro.asic_init(yaml=args.yaml, chipsPerRow=args.chipsPerRow)
#    logger.debug(f"Header: {astro.get_log_header(layer, chip)}")

    if args.gecco:
        logger.debug("initializing voltage")
        await astro.init_voltages(vthreshold=args.threshold) ## th in mV

    ## 12/17 Test: Configure FPGA TS "Tag" Rate
    

    #logger.debug("FUNCTIONALITY CHECK")
    #await astro.functionalityCheck(holdBool=True)

    ## DAN - confirm functionality
    #logger.debug("update threshold")
    #await astro.update_pixThreshold(layer, chip, args.threshold)

    # Setup / configure injection
    if args.inject:
        logger.debug("enable injection pixel")
        await astro.enable_injection(*args.inject)
        await astro.enable_pixel(*args.inject) #assume that you'd like to read out the pixel you're injecting into
        #await astro.enable_analog(args.inject[0], args.inject[1], args.inject[3]) #assume that you'd like to read out the column pixel you're injecting into  
        
        ##DAN - allow option to enable a pixel for a noise scan in command line 

        if args.gecco:
            logger.debug("init injection (gecco)")
            await astro.init_injection(args.inject[0], args.inject[1], inj_voltage=args.vinj)
        else:
            if args.vinj is None:
                # Priority to command line, defaults to yaml - already in vdac units
                try:
                    args.vinj = astro.boardDriver.getAsic(row=args.inject[0]).asic_config[f'config_{args.inject[1]}']['vdacs']['vinj'][1]
                except (KeyError, IndexError):
                    logger.error(f"Injection arguments layer={args.inject[0]-1}, chip={args.inject[1]} invalid. Cannot initialize injection.")
                    args.inject = None
                await astro.init_injection(args.inject[0], args.inject[1], inj_voltage=args.vinj, is_mV=False)
            else:
                await astro.init_injection(args.inject[0], args.inject[1], inj_voltage=args.vinj)
    if args.analog:
        logger.debug("enable analog")
        await astro.enable_analog(*args.analog)
    else:
        pass#Smtg needed here?

    # Send final config to chips
    logger.debug("final configs")
    for layer in range(len(args.yaml)):
        #logger.debug(f"Header: {astro.get_log_header(l, chip)}")
        await astro.asic_configure(layer)
    
        logger.debug("setup readout")
        #pass layer number
        await astro.setup_readout(layer, autoread=not(args.noAutoread)) 

    # Prepare for run
    if args.runTime is not None: 
        end_time=time.time()+(args.runTime*60.)
    else:
        end_time = float('inf')
    
    if not args.noAutoread:
        dataStream = b''
        dataStream_lst = []
        bufferLength_lst = []

    # Start injection
    if args.inject:
        logger.debug("start injection")
        #await astro.checkInjBits()
        await astro.start_injection()
        #await astro.checkInjBits()
    
    #Collect data
    logger.debug("Collecting data")
    break_condition=False
    try: # By enclosing the main loop in try/except we are able to capture keyboard interupts cleanly
        while True:
            #timing break condition
            if (time.time() >= end_time) or break_condition:
                break

            if args.noAutoread:
                try:
                    task = asyncio.create_task(asyncio.sleep(1))
                    await task
                except KeyboardInterrupt:
                    logger.info("asyncio received exit from keyboard, exiting")
                    break_condition=True
                except asyncio.CancelledError:
                    logger.info("asyncio received exit from cancellation, exiting")
                    break_condition=True
            else:    

                # WARNING - live string parsing causes SW-induced slowdown and results in lower overall data rate. Enabled in "debug" mode
                # Efficient data collection strategy = collect full buffers during running and process after the run. Default when not in "debug" mode

                #define asyncio task to enable graceful exit
                try:
                    task = asyncio.create_task(astro.get_readout())
                    await task
                    buff, readout = task.result()
                except KeyboardInterrupt:
                    logger.info("asyncio received exit from keyboard, exiting")
                    break_condition=True
                except asyncio.CancelledError:
                    logger.info("asyncio received exit from cancellation, exiting")
                    break_condition=True
                
                if args.printHits:
                #live printout of data packet in terminal
                    if buff>0:
                        readout_data = readout[:buff]
                        logger.info(binascii.hexlify(readout_data))
                        logger.info(f"{buff} bytes in buffer")
                        dataStream+=readout_data
                        if not args.dumpOutput:
                            bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")
                
                #HK
                #if not args.gecco:
                    #sleep to give it time between read/writes, maybe not needed for asyncio?
                    #task = asyncio.create_task(astro.callHK()) 
                #    task_hk = asyncio.create_task(astro.every(astro.callHK()))
                #    await task_hk

                #Append full readout and buffer length to appropriate arrays
                dataStream_lst.append(readout)
                bufferLength_lst.append(buff)
    except KeyboardInterrupt: # Ends program cleanly when a keyboard interupt is sent (for no autoread case).
        logger.info("Keyboard interupt. Program halt!")
    except Exception as e: # Catches other exceptions
        logger.exception(f"Encountered Unexpected Exception! \n{e}")

    
    # End injection
    if args.inject:
        logger.debug("stop injection")
        #await astro.checkInjBits()
        await astro.stop_injection()
        #await astro.checkInjBits()

    #wait to decode until the very end so that all readouts can be appended together and headers re-attached
    if not args.noAutoread:
        #AFTER data collection, parse autoread raw data and save to file
        txtOut = None if args.dumpOutput else bitfile
        dataStream = await astro.dataParse_autoread(dataStream_lst, bufferLength_lst, bitfile=txtOut)
        if not args.dumpOutput:
            bitfile.write(str(binascii.hexlify(dataStream)))
        #lose info about which hit comes from which readout buffer
        ## DAN - consider whether readout buffer number is worth saving. 
        ## DAN - Think about way to break up how much is stored in memory at one time before storing somewhere. 
        # Should still decode at the end (of some interval of time) but not save to store all in dynamic RAM the whole time
        df = astro.decode_readout(dataStream,i=0) #i is meant to be readout stream increment


    ## DAN - after autoread mode, get one single big dump of data after this point. 
    # May want to clear/dump buffer along with the 'stop injection' command so it's not read out either here or in the beginning of the next run. 
    # Or maybe it needs to be parsed out and is the "missing" data (like if it's included then the data length of autoread vs no autoread would be equal)

    #Process data
    if args.noAutoread:
    #if was not autoreading, process the info that was collected
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
            logger.error(f"No data recorded - no CSV generated")
            return 
    



#######################################################
################## TOP LEVEL ##########################
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A-STEP Bench Testing Code for chip configuration and data collection.', 
                                     formatter_class=RawTextHelpFormatter, #allow formatting of the epilog
                                     epilog=""" 
                                        \nDefault run conditions: 
                                        \n\u2022 Save outputs (*.log, *.txt, *.csv) of the form DATETIME.* to folder data/ 
                                        \n\u2022 Logger level INFO 
                                        \n\u2022 Board drivers for CMOD HW setup 
                                        \n\u2022 Load configuration file quadChip_allOff 
                                        \n\u2022 Configure 4 chips per bus via SPI 
                                        \n\u2022 Readoff chip with autoread and no live printing of streams 
                                        \n\u2022 100 mV comparator threshold 
                                        \n\u2022 Analog readout from layer 1, chip 0, row 0, col 0
                                        \n\u2022 No injection/enabled pixels for digital output (only settings in yml) 
                                        \n\u2022 Collect data until user ends run gracefully with CNTL+C""")

    # Options related to outputs
    parser.add_argument('-n', '--name', default='', required=False,
                        help='Option to give additional name to output files upon running. Default: NONE')
    parser.add_argument('-o', '--outdir', default='data/', required=False,
                        help='Output Directory for all datafiles, as a subdir within data/. Default: data/')
    ## DAN - I hate this saving strategy. Should think of a better way. Implementation is backwards and messy
    parser.add_argument('-d', '--dumpOutput', action='store_true', required=False, 
                        help='If passed, do not save raw data *.txt or decoded *.csv. If not passed, save the outputs. Log always saved. Default: save all')
    parser.add_argument('-p', '--printHits', action='store_true', required=False, 
                        help = 'Can only be used in autoread mode. If passed, print readout streams in real time to terminal, accepting potential data slowdown penalty. \
                                If not passed, no printouts during data collection. Default: post-collection printout') 

    # Options related to software run settings
    parser.add_argument('-L', '--loglevel', type=str, choices = ['D', 'I', 'E', 'W', 'C'], action="store", default='I',
                        help='Set loglevel used. Options: D - debug, I - info, E - error, W - warning, C - critical. DEFAULT: I')
    parser.add_argument('-T', '--runTime', type=float, action='store',  default=None,
                        help = 'Maximum run time (in minutes). Default: NONE (run until user CTL+C)')
    
    # Options related to Setup / Configuration of system
    parser.add_argument('-g', '--gecco', action='store_true', required=False, 
                        help='If passed, configure for GECCO HW. If not passed, configure for CMOD HW. Default: CMOD') 
    parser.add_argument('-y', '--yaml', action='store', required=False, type=str, default = ['quadChip_allOff'], nargs="+", 
                        help = 'filepath (in scripts/config/ directory) .yml file containing chip configuration. \
                                One file must be passed for each layer, from layer #0 to layer #2. \
                                Default: config/quadChip_allOff (All pixels off, only fisrt layer is configured)')
    parser.add_argument('-c', '--chipsPerRow', action='store', required=False, type=int, default = [4], nargs="+", 
                        help = 'Number of chips per SPI bus to enable. Can provide a single number or one number per bus. Default: 4')
    parser.add_argument('-sr', '--shiftRegister', action='store_true', required=False, 
                        help='If passed, configures chips via Shift Registers (SR). If not passed, configure chips via SPI. Default: SPI')
    
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


    #Checks for outdir path
    if args.outdir != "data/":
            args.outdir = "data/"+args.outdir
    #check 'outdir' argument and add '/' if necessary
    if args.outdir[-1]!="/":
            args.outdir+="/"
    # Ensures output directory exists
    if os.path.exists(args.outdir) == False:
        os.mkdir(args.outdir)


    #Define output save name for all files
    fname="" if not args.name else args.name+"_"
    saveName = fname + time.strftime("%Y%m%d-%H%M%S") 

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
    logname = args.outdir+saveName+"_run.log"
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


    #Live readout printing option only possible in autoread mode
    if args.printHits and args.noAutoread:
        logger.warning("Live readout printing is only possible when chip read in autoread mode. Live readout printing is now disabled and code will run in non-autoread mode.")


    #print(args.yaml)
    #print(args.chipsPerRow)
    #Layer counting begins at 0.
    #Make sure config arguments make sense
    if len(args.yaml) > len(args.chipsPerRow):
        args.chipsPerRow = [args.chipsPerRow[0]]*len(args.yaml)
        if len(args.chipsPerRow) > 1:
            logger.warning(f"Number of chips per row not provided for every layer - default to {args.chipsPerRow[0]} for all {len(args.yaml)} layers.")
    elif len(args.yaml) < len(args.chipsPerRow):
        raise ValueError("You need to provide one yaml configuration file for every chipsPerRow argument.")

    #Make sure analog/inject arguments make sense
    if args.analog is not None and (len(args.analog)!=3 or args.analog[0]<0 or args.analog[0]>2 or args.analog[1]<0 or args.analog[1]>3 or args.analog[2]<0):
        raise ValueError("Incorrect analog argument layer={0[0]},chip={0[1]},column={0[2]}".format(args.analog))
    if args.inject is not None and (len(args.inject)!=4 or args.inject[0]<0 or args.inject[0]>2 or args.inject[1]<0 or args.inject[1]>3 or args.inject[2]<0 or args.inject[3]<0):
        raise ValueError("Incorrect analog argument layer={0[0]},chip={0[1]},row={0[2]},column={0[3]}".format(args.inject))

    asyncio.run(main(args, saveName))

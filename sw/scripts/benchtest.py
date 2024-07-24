import asyncio
from astep import astepRun
import pandas as pd
import binascii
import logging
import time

#######################################################
############## USER DEFINED VARIABLES #################
layer, chip = 0,1
pixel = [layer, chip, 0, 30] #layer, chip, row, column
configViaSR = False #if False, config with SPI
inj_voltage = 300 #injection amplitude in mV
threshold = 200 #global comparator threshold level in mV
runTime = 5 #duration of run in s
chipsPerRow = 2 #number of arrays per SPI bus to configure
autoread = True 
gecco = True
logLevel = logging.INFO #DEBUG, INFO, WARNING, ERROR, CRITICAL
saveOutput = True
saveName = "data/new"
injection = True
debug = False #If true, print data to screen in real time even if it results in a SW slowdown. Use False for efficient data collection mode
#######################################################

#always save log
print("setup logger")
logname = saveName+"_run.log"
formatter = logging.Formatter('%(asctime)s:%(msecs)d.%(name)s.%(levelname)s:%(message)s')
fh = logging.FileHandler(logname)
fh.setFormatter(formatter)
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logging.getLogger().addHandler(sh) 
logging.getLogger().addHandler(fh)
logging.getLogger().setLevel(logLevel)
logger = logging.getLogger(__name__)

#optionally save *txt of raw data and decoded data in CSV
if saveOutput:
    bitpath = saveName+".txt"
    csvpath = saveName+".csv"
    bitfile = open(bitpath,'w')     

logger.debug("creating object")
astro = astepRun(inject=pixel,SR=configViaSR)

async def main():
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
        await astro.setup_readout(l, autoread=int(autoread)) 

    #write layer bytes with some zeros - send 1/2 the amount that you want to read

    if gecco and injection:
        logger.debug("start injection")
        #await astro.checkInjBits()
        await astro.start_injection()
        #await astro.checkInjBits()

    #collect data
    if autoread:    
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
                    if saveOutput:
                        bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")
            else:
                dataStream_lst.append(readout)
                bufferLength_lst.append(buff)

        if not debug:
            #AFTER data collection, parse the raw data and save to file
            txtOut = bitfile if saveOutput else None
            dataStream = await astro.dataParse_autoread(dataStream_lst, bufferLength_lst, bitfile=txtOut)
            bitfile.write(str(binascii.hexlify(dataStream)))

        #wait to decode until the very end so that all readouts can be appended together and headers re-attached
        #loose info about which hit comes from which readout buffer
            ## DAN - consider whether readout buffer number is worth saving. 
            ## DAN - Think about way to break up how much is stored in memory at one time before storing somewhere. Should still decode at the end (of some interval of time) but not save to store all in dynamic RAM the whole time
        df = astro.decode_readout(dataStream,i=0) #i is meant to be readout stream increment
    else:
        astro._wait_progress(runTime)

    if gecco and injection:
        logger.debug("stop injection")
        #await astro.checkInjBits()
        await astro.stop_injection()
        #await astro.checkInjBits()

    #if was not autoreading, process the info that was collected
    if not autoread:
        logger.debug("read out buffer")
        buff, readout = await(astro.get_readout())
        readout_data = readout[:buff]
        logger.info(binascii.hexlify(readout_data))
        logger.info(f"{buff} bytes in buffer")
        df = astro.decode_readout(readout_data, 0)
        if saveOutput:
            bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")

    if saveOutput:               
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
        df.columns = csvframe
        df.to_csv(csvpath)
        

asyncio.run(main())
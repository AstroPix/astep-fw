import asyncio
from astep import astepRun
import pandas as pd
import binascii
import logging

#######################################################
############## USER DEFINED VARIABLES #################
layer, chip = 0,0
pixel = [layer, chip, 0, 10] #layer, chip, row, column
configViaSR = False #if False, config with SPI
inj_voltage = 300 #injection amplitude in mV
threshold = 100 #global comparator threshold level in mV
runTime = 5 #duration of run in s
chipsPerRow = 2 #number of arrays per SPI bus to configure
gecco = True
logLevel = logging.INFO #DEBUG, INFO, WARNING, ERROR, CRITICAL
saveOutput = True
saveName = "data/test"
#######################################################

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

if saveOutput:
    bitpath = saveName+".log"
    csvpath = saveName+".csv"

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
    await astro.asic_init(yaml="test_quadchip_new", chipsPerRow=chipsPerRow, analog_col=[layer, chip, pixel[3]])
    logger.debug(f"Header: {astro.get_log_header(layer, chip)}")

    if gecco:
        logger.debug("initializing voltage")
        await astro.init_voltages(vthreshold=threshold) ## th in mV

    #loger.debug("FUNCTIONALITY CHECK")
    #await astro.functionalityCheck(holdBool=True)

    #logger.debug("update threshold")
    #await astro.update_pixThreshold(layer, chip, 100)

    logger.debug("enable pixel")
    await astro.enable_pixel(layer, chip, pixel[2], pixel[3])  

    if gecco:
        logger.debug("init injection")
        await astro.init_injection(layer, chip, inj_voltage=inj_voltage)

    logger.debug("final configs")
    for l in range(layer+1):
        logger.debug(f"Header: {astro.get_log_header(l, chip)}")
        await astro.asic_configure(l)
    
        logger.debug("setup readout")
        #pass layer number
        await astro.setup_readout(l, autoread=0) #disable autoread

    #write layer bytes with some zeros - send 1/2 the amount that you want to read

    if gecco:
        logger.debug("start injection")
        await astro.checkInjBits()
        await astro.start_injection()
        await astro.checkInjBits()

    astro._wait_progress(runTime)
    if gecco:
        logger.debug("stop injection")
        await astro.checkInjBits()
        await astro.stop_injection()
        await astro.checkInjBits()


    logger.debug("read out buffer")
    buff, readout = await(astro.get_readout())
    readout_data = readout[:buff]
    logger.info(binascii.hexlify(readout_data))
    logger.info(f"{buff} bytes in buffer")
    df = astro.decode_readout(readout_data, 0)

    if saveOutput:      
        bitfile = open(bitpath,'w')              
        bitfile.write(f"{str(binascii.hexlify(readout_data))}\n")
        bitfile.close()
        
        csvframe =pd.DataFrame(columns = [
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
        ]) 
        csv_out = pd.concat([csvframe, df])
        csv_out.to_csv(csvpath)
        

asyncio.run(main())
import asyncio
from astep import astepRun
import time
import binascii
import logging

print("setup logger")
logname = "run.log"
formatter = logging.Formatter('%(asctime)s:%(msecs)d.%(name)s.%(levelname)s:%(message)s')
fh = logging.FileHandler(logname)
fh.setFormatter(formatter)
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logging.getLogger().addHandler(sh) 
logging.getLogger().addHandler(fh)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

#######################################################
############## USER DEFINED VARIABLES #################
layer, chip = 0,0
pixel = [layer, chip, 0, 15] #layer, chip, row, column
configViaSR = True #if False, config with SPI
inj_voltage = 400 #injection amplitude in mV
threshold = 200 #global comparator threshold level in mV
runTime = 5 #duration of run in s
chipsPerRow = 1 #number of arrays per SPI bus to configure
#######################################################


print("creating object")
astro = astepRun(inject=pixel,SR=configViaSR)

async def main():
    print("opening fpga")
    await astro.open_fpga(cmod=False, uart=False)

    print("setup clocks")
    await astro.setup_clocks()

    print("setup spi")
    await astro.enable_spi()
    
    print("initializing asic")
    await astro.asic_init(yaml="config_quad_v3_opt", analog_col=[layer, chip ,pixel[3]], chipsPerRow=chipsPerRow)
    print(f"Header: {astro.get_log_header(layer, chip)}")

    print("initializing voltage")
    await astro.init_voltages(vthreshold=threshold) ## th in mV

    print("FUNCTIONALITY CHECK")
    await astro.functionalityCheck(holdBool=True)

    #print("update threshold")
    #await astro.update_pixThreshold(layer, chip, 100)

    print("enable pixel")
    await astro.enable_pixel(layer, chip, pixel[2], pixel[3])  

    print("init injection")
    await astro.init_injection(layer, chip, inj_voltage=inj_voltage)

    print("final configs")
    for l in range(layer+1):
        print(f"Header: {astro.get_log_header(l, chip)}")
        await astro.asic_configure(l)
    
        print("setup readout")
        #pass layer number
        await astro.setup_readout(layer, autoread=0) #disable autoread

    print("start injection")
    await astro.checkInjBits()
    await astro.start_injection()
    await astro.checkInjBits()

    """
    t0 = time.time()
    inc = -2
    while (time.time() < t0+5):
        
        buff, readout = await(astro.get_readout())
        if buff>4:
            inc += 1
            if inc<0:
                continue
            hit = readout[:buff]
            print(binascii.hexlify(hit))
            #print(hex(readout[:buff]))
            astro.decode_readout(hit, inc) 
        
        #await(astro.print_status_reg())
    """
    astro._wait_progress(runTime)
    print("stop injection")
    await astro.checkInjBits()
    await astro.stop_injection()
    await astro.checkInjBits()


    print("read out buffer")
    buff, readout = await(astro.get_readout())
    readout_data = readout[:buff]
    print(binascii.hexlify(readout_data))
    print(f"{buff} bytes in buffer")
    astro.decode_readout(readout_data, 0)


asyncio.run(main())
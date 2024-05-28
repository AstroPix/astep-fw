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

layer, chip = 0,0
pixel = [layer, chip, 0, 15] #layer, chip, row, column

print("creating object")
astro = astepRun(inject=pixel)

async def main():
    print("opening fpga")
    await astro.open_fpga(cmod=False, uart=False)

    print("setup clocks")
    await astro.setup_clocks()

    print("setup spi")
    await astro.enable_spi()
    
    print("initializing asic")
    await astro.asic_init(yaml="test_quadchip", analog_col=[layer, chip ,pixel[3]])
    print(f"Header: {astro.get_log_header(layer, chip)}")

    print("initializing voltage")
    await astro.init_voltages() ## th in mV

    #print("FUNCTIONALITY CHECK")
    #await astro.functionalityCheck(holdBool=True)

    print("update threshold")
    await astro.update_pixThreshold(layer, chip, 100)

    print("enable pixel")
    await astro.enable_pixel(layer, chip, pixel[2], pixel[3])

    #print("init injection")
    #await astro.init_injection(inj_voltage=300)

    print("final configs")
    print(f"Header: {astro.get_log_header(layer, chip)}")
    await astro.asic_configure(layer)
    
    print("setup readout")
    #pass layer number
    await astro.setup_readout(layer, autoread=0) #disable autoread

    #print("start injection")
    #await astro.start_injection()

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
    astro._wait_progress(5)
    #print("stop injection")
    #await astro.stop_injection()


    print("read out buffer")
    buff, readout = await(astro.get_readout())
    print(binascii.hexlify(readout))
    print(f"{buff} bytes in buffer")


asyncio.run(main())
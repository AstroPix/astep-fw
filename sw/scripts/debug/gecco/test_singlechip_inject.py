

import asyncio

import logging

import drivers.boards
from astep import AstepRun


import binascii

async def print_layers_stats(driver):
    for i in range(1):
        logger.info(f"-- Layer {i} stats")
        idle = await driver.getLayerStatIDLECounter(i)
        frames = await driver.getLayerStatFRAMECounter(i)
        errors = await driver.getLayerWrongLength(i)
        logger.info(f"---> IDLE={idle} bytes")
        logger.info(f"---> Frames={frames}")
        logger.info(f"---> Errors={errors}")



async def main():
    ## Open Board
    ############
    #
    #

    #
    # astro = AstepRun(SR=False)
    astro = AstepRun(chipversion=4, SR=True)

    logger.info(f"opening fpga")

    driver =    await astro.open_fpga(cmod=False, uart=False)


    fwid = await driver.readFirmwareID()
    version = await driver.readFirmwareVersion()

    logger.info(f"FW ID={hex(fwid)},build={version}")
    
   

    ## Open Config File and Configure astropix
    #astro.load_yaml("./scripts/config/singlechip_testconfig_v3.yml")
    #astro.load_yaml("./scripts/config/singlechip_r0c10.yml")
    # 
    # 
    
    # astro.load_yaml("singlechip_allOff")
    astro.load_yaml("singlechip_v4")
    
    ## Configure
    await astro.fpga_configure_clocks()
    
    astro.cfg_enable_injection(layer = 0, chip = 0, row = 0, col=5)
    astro.cfg_enable_pixel(layer = 0, chip = 0, row = 0, col=5)
    astro.cfg_enable_analog(layer = 0, chip = 0, col=5)
    
    
    # 1=thpmos (comparator threshold voltage), 3 = Vcasc2, 4=BL, 7=Vminuspix, 8=Thpix
    await astro.init_voltages(vsupply = 3.3,dacvals=(8, [1.1, 0, 1.1, 1, 0, 0, 0.7, 1.01]))
    await astro.init_injection(layer = 0 ,
                            chip = 0,
                            inj_voltage = 800,
                            inj_period = 100,
                            clkdiv = 300,
                            initdelay = 100, # Delay between cycles too, needs way higher value of roughly 200 * period to make cycles not restart too fast
                            cycle = 0,
                            pulseperset = 1,
                            dac_config = None,
                            onchip = True,
                            is_mV = True)
    
    
    ## Configure and Flush
    await astro.chips_reset_configure()
    astro.boardDriver.asics[0].ram_set_all(0b00001)
    await astro.boardDriver.writeSRAsicConfig(tdac=True)
    
    
    await driver.rfg.write_layers_cfg_nodata_continue(
        value=32, flush=True
    )
    
    
    
    logger.info("Before Run stats")
    await print_layers_stats(driver)
    
    
    await astro.chips_flush()
    await astro.buffer_flush()
    await astro.chips_enable_readout(autoread = True)
    
    
    await driver.resetLayerStatCounters(0)
    
    logger.info("Reset Run stats")
    await print_layers_stats(driver)
    await astro.print_status_reg()
    logger.info(f"Buffer size={await driver.readoutGetBufferSize()}")
    
    
    ## Run
    await astro.start_injection()
    await asyncio.sleep(2)
    await astro.stop_injection()
    await asyncio.sleep(2)
    
    
    logger.info("End of Run stats")
    await print_layers_stats(driver)
    logger.info(f"Buffer size={await driver.readoutGetBufferSize()}")
    await astro.print_status_reg()
    
    bytes = await driver.readoutReadBytes(await driver.readoutGetBufferSize())
    if len(bytes)>0:
       print(f"A: {binascii.hexlify(bytes).decode()}")
    #    astro.decode_readout(bytes,10)
    #    astro.decode_readout(bytes,13)
    await astro.print_status_reg()
    await astro.buffer_flush()
    logger.info(f"Buffer size={await driver.readoutGetBufferSize()}")
    
    await astro.chips_reset()
    #await astro.update_injection(layer = 0 ,
    #                            chip = 0 ,
    #                            inj_voltage = 0.1,
    #                            inj_period = None,
    #                            clkdiv = None,
    #                            initdelay = None,
    #                            cycle = None,
    #                            pulseperset = None)
    
    # COnfigure Voltage Board for injection
    #vboard = driver.geccoGetVoltageBoard()
    #vboard.dacvalues = (8, [1.1, 0, 1.1, 1.2, 0, 0, 1, 1.100])
    #vboard.vcal = 0.989
    #vboard.vsupply = 3.3
    
    #await vboard.update(ckdiv = 32)
    
    #await astrop.
    
    
    return 
    


if __name__ == "__main__":
    global logger
    logger = logging.getLogger(__name__)
    logging.getLogger().setLevel(logging.INFO)
    logger.info("Setup logger")
    asyncio.run(main( ))


import asyncio

import logging

import drivers.boards
from astep import AstepRun


async def main():
    ## Open Board
    ############
    #
    #

    #
    astro = AstepRun(SR=False)

    logger.info(f"opening fpga")

    driver =    await astro.open_fpga(cmod=False, uart=False)


    fwid = await driver.readFirmwareID()
    version = await driver.readFirmwareVersion()

    logger.info(f"FW ID={hex(fwid)},build={version}")
    
   

    ## Open Config File and Configure astropix
    astro.load_yaml("./scripts/config/singlechip_testconfig_v3.yml")
    
    ## Configure
    await astro.fpga_configure_clocks()
    await astro.chips_reset_configure()
    
    # 
    vboard = driver.geccoGetVoltageBoard()
    vboard.dacvalues = (8, [1.1, 0, 1.1, 1.2, 0, 0, 1, 1.100])
    vboard.vcal = 0.989
    vboard.vsupply = 3.3
    
    await vboard.update(ckdiv = 32)
    
    
    return 
    


if __name__ == "__main__":
    global logger
    logger = logging.getLogger(__name__)
    logging.getLogger().setLevel(logging.INFO)
    logger.info("Setup logger")
    asyncio.run(main( ))
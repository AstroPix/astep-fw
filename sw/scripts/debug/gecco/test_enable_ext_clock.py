

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
    
    ## 
    await driver.layersConfigFPGATimestamp(
        enable=True,
        use_divider=False,
        use_tlu=False,
        flush=True,
    )
    
    await driver.setExternalClock(enable=True)
    
    
    return 
    
    ## Readback
    await driver.writeSRReadback(lane = 0 )
    ## Get the bits
    (readBits,expectedBits) = await driver.readSRReadbackBits(lane=0)
    
    logger.info(f"Expected Bits: {expectedBits.bin}")
    logger.info(f"Read Bits    : {readBits.bin}")
    logger.info(f"Match: {expectedBits==readBits}")

    pass


if __name__ == "__main__":
    global logger
    logger = logging.getLogger(__name__)
    logging.getLogger().setLevel(logging.INFO)
    logger.info("Setup logger")
    asyncio.run(main( ))
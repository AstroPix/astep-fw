import asyncio
from astep import astepRun
import pandas as pd
import binascii
import logging
import time
import argparse
from argparse import RawTextHelpFormatter
import os, serial


#######################################################
############## USER DEFINED VARIABLES #################
layer, chip = 0, 0


#######################################################
###################### MAIN ###########################
async def main():
    astro = astepRun(SR=False)

    await astro.open_fpga(cmod=False, uart=False)


    ## Enable Clocks
    await astro.setup_clocks()
    await astro.enable_spi()

    ## Configure
    await astro.asic_init(yaml="singlechip_r0c10", chipsPerRow=1)
    await astro.enable_injection(layer = 0 , chip = 0, row = 0 , col = 10 )
    await astro.enable_pixel(layer = 0 , chip = 0, row = 0 , col = 10)
    await astro.asic_configure(layer = 0 )

    ## Check IDLE byte is working
    await astro.sanity_check_idle(layer = 0)

    ## Enable one pixel

    ## Make one Digital Injection
    

asyncio.run(main())

    
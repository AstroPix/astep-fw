"""
Test program to run the A-STEP test bench.
First prototype of the A-STEP Detector flight software.

Author: Adrien Laviron (adrien.laviron@nasa.gov)
"""
import asyncio
import time, os
from tqdm import tqdm
import argparse

import drivers.boards
import drivers.astep.serial
import drivers.astropix.decode

# Logging stuff
import logging


#######################################################
#################### BUFFER MANAGEMENT ################

async def buffer_flush(boardDriver, layerlst):
    """This method flushes data from SPI lanes then from FPGA buffer, and resets counters"""
    logger.info("Flush chips before data collection")
    await boardDriver.holdLayers(hold=False, flush=True)
    for layer in layerlst:
        interrupt_counter=0
        interrupt = await boardDriver.getLayerStatus(layer)
        while interrupt&1 == 0 and interrupt_counter<20:
            logger.info("interrupt low")
            await boardDriver.layersSelectSPI(flush=True)
            await boardDriver.writeLayerBytes(layer = layer, bytes = [0x00] * 128, flush=True)
            await boardDriver.layersDeselectSPI(flush=True)
            interrupt_counter+=1
            interrupt = await boardDriver.getLayerStatus(layer)
    # Reassert hold to be safe
    await boardDriver.holdLayers(hold=True, flush=True)
    # Now all interrupts are high, empty FPGA buffer
    logger.info("Flush FPGA buffer before data collection")
    await(boardDriver.readoutReadBytes(4098))
    await boardDriver.resetLayerStatCounters(layer)

async def getBuffer(boardDriver):
    bufferSize = await boardDriver.readoutGetBufferSize()
    readout = await boardDriver.readoutReadBytes(bufferSize)
    return bufferSize, readout


#######################################################
#################### COMMUNICATIONS ###################

def downlinkDataFile(data, outputfile):
    with open(outputfile, "ab") as ofile:
        ofile.write(data)#add flush here

def downlinkData(buff, readout):
    pass # Implement here

def getCmdsFile():
    with open("upcmds.bin", "rb") as cmdsfile:
        cmds = cmdsfile.read()
    return cmds

def getCmds():
  pass # Implement here

#######################################################
#################### HOUSEKEEPING #####################

async def getHousekeeping():
    return 0 ## Implement reading housekeeping here


#######################################################
#################### COMMAND INTERPRETER ##############

def setInjector(boardDriver):
    # Setup / configure injection
    boardDriver.asics[args.inject[0]].enable_inj_col(args.inject[1], args.inject[3], inplace=False)
    boardDriver.asics[args.inject[0]].enable_inj_row(args.inject[1], args.inject[2], inplace=False)
    boardDriver.asics[args.inject[0]].enable_pixel(chip=args.inject[1], col=args.inject[3], row=args.inject[2], inplace=False)
    # Priority to command line, defaults to yaml - already in vdac units
    try:
        logger.debug("Set injection voltage")
        # Priority to command line, defaults to yaml - already in vdac units
        if args.vinj is not None:
            boardDriver.asics[args.inject[0]].asic_config[f"config_{args.inject[1]}"]["vdacs"]["vinj"][1] = int(args.vinj/1000*1024/1.8)#1.8 V coded on 10 bits
    except (KeyError, IndexError):
        logger.error(f"Injection arguments layer={args.inject[0]}, chip={args.inject[1]} invalid. Cannot initialize injection.")
        args.inject = None

async def interpretCommands(cmds):
    pass

#######################################################
#################### MAIN FUNCTION ####################

async def setup(qcsn):
    """
    :param qcsn: list of the quadchip serial numbers (WxxQxx) in use.
    """
    # Setup FPGA communications
    boardDriver = drivers.boards.getCMODUartDriver("COM6")
    await boardDriver.open()
    logger.info("Opened FPGA, testing...")
    try:
        fwid = await boardDriver.readFirmwareID()
        logger.info(f"FW ID: {fwid}")
    except Exception: 
        raise RuntimeError("Could not read or write from astropix!")
    await boardDriver.enableSensorClocks(flush = True)
    await boardDriver.layersConfigFPGATimestampFrequency(targetFrequencyHz = 1000000, flush = True)
    await boardDriver.layersConfigFPGATimestamp(enable = True, force = False, source_match_counter = True, source_external = False, flush = True)

    await boardDriver.configureLayerSPIDivider(20, flush = True)
    await boardDriver.rfg.write_layers_cfg_nodata_continue(value=8, flush=True)
    await boardDriver.ioSetInjectionToChip(enable = True, flush = True) # Routes injection pattern to on-chip injector
    # Configure chips in memory
    pathdelim = os.path.sep #determine if Mac or Windows separators in path name
    ymlpath = [os.getcwd()+pathdelim+"scripts"+pathdelim+"config"+pathdelim+ y +".yml" for y in qcsn] # Define list of yaml cfg files
    try:
        for layer, yml in enumerate(ymlpath):
            boardDriver.setupASIC(version = 3, row = layer, chipsPerRow = 4 , configFile = yml)
    except FileNotFoundError as e :
        logger.error(f'Config File {ymlpath} was not found, pass the name of a config file from the scripts/config folder')
        raise e
    logger.info(f"{len(boardDriver.asics)} ASIC drivers instanciated.")

    await boardDriver.disableLayersReadout(flush=True)#Hold, disableMISO, disableAutoread, CS=inactive
    await boardDriver.resetLayersFull()

    # Set chip IDs
    await boardDriver.layersSelectSPI(flush=True)
    for layer in range(len(qcsn)):
        await boardDriver.asics[layer].writeSPIRoutingFrame(0)
    await boardDriver.layersDeselectSPI(flush=True)
    
    for i in range(4):
        await boardDriver.layersSelectSPI(flush=True)
        for layer in range(len(qcsn)):
            payload = boardDriver.asics[layer].createSPIConfigFrame(load=True, n_load=10, broadcast=False, targetChip=i)
            await boardDriver.asics[layer].writeSPI(payload)
        await boardDriver.layersDeselectSPI(flush=True)
    # Flush old data
    # Is it even needed here?
    await buffer_flush(boardDriver, range(len(qcsn)))
    return boardDriver


def main(boardDriver, qcsn):
    """
    :param qcsn: list of the quadchip serial numbers (WxxQxx) in use.
    """
    await boardDriver.enableLayersReadout(range(len(qcsn)), autoread=True, flush=True)
    ofile = "{}.bin".format(time.strftime("%Y%m%d-%H%M%S"))
    # Main loop
    run = True
    while run:
        try:
            # Housekeeping
            hkdata = await getHousekeeping()
            downlinkDataFile(hkdata, ofile)
            #downlinkData(hkdata)
            # Check commands
            cmds = getCmdsFile()
            #cmds = getCmds()
            await interpretCmds(cmds)
            # Scientific data
            for i in range(10):#10 should be changed depending on downlink rates
                task = asyncio.create_task(getBuffer(boardDriver))
                await task
                buff, readout = task.result()
                if buff > 0:
                    downlinkDataFile(readout, ofile)
                #downlinkData(readout)
                time.sleep(0.1)# Same comment on downlink rates
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("[Ctrl+C] while in main loop - exiting.")
            run=False
    # Pause readout
    await boardDriver.disableLayersReadout(flush=True)
    ofile.close()
    await boardDriver.close()


#######################################################
#################### TOP LEVEL ########################

if __name__ == "__main__":
    qcsn = ["W08Q05", "W101Q8"]
    boardDriver = asyncio.run(setup(qcsn))
    asyncio.run(main(boardDriver, qcsn))


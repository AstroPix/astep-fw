""" 
Boards Module 

This Module contains the Board Driver class which is the entry point to drive the Firmware functionalities.

This module init script contains factory methods to create a Board Driver instance based on the target configuration. 

For Example:

- getGeccoUARTDriver() returns a Driver configured for the Gecco Target connected via UART
- getGeccoNODriver() returns a Board Driver without I/O, or a dummy IO layer - useful to test scripts without a Hardware connected

"""
import sys
import os
import rfg.io
import rfg.core
import rfg.discovery

## Firmware Support Register File Definition will be loaded by the discovery method
## This is one way to do things, we could also make a release from firmware with the RFG Python part and copy it locally as a module
sys.path.append(os.environ["BASE"]+"/fw/astep24-3l/common/")

################
## Constructors to get a Board driver with RFG loaded for each config
####################

def getCMODDriver():
    import drivers.cmod
    firmwareRF  = rfg.discovery.loadOneFSPRFGOrFail()
    boardDriver = drivers.cmod.CMODBoard(firmwareRF)
    
    return boardDriver

def getCMODUartDriver(portPath : str | None = None):
    return getCMODDriver().selectUARTIO(portPath)

def getCMODSPIDriver():
    raise NotImplementedError



import importlib.util
import sys
import os.path 

import logging 


def listFirmwarePackages():
    logging.info("Discovering FSP")
    spec = importlib.util.find_spec("fsp")
    logging.debug("Found: ",spec)
    foundFSP = []
    if spec is not None:
        #module = importlib.util.module_from_spec(spec)
        logging.debug("Subpath: ",spec.submodule_search_locations)
        for subModule in spec.submodule_search_locations:
            logging.debug("-> Possible Firmware: ",subModule)
            tops = next(os.walk(os.path.normpath(subModule)))[1]
            for top in tops: 
                logging.debug("-> Candidate Firmware top: ",top)
                subSpec = importlib.util.find_spec("fsp."+top)
                if subSpec is not None:
                    logging.debug("--> Loading: ",subSpec)
                    #subModule = importlib.util.module_from_spec(subSpec)
                    foundFSP.append(subSpec)
                    #subSpec.loader.exec_module(subModule)
    return foundFSP

def loadOneFSPOrFail():
    foundFSP = listFirmwarePackages()
    if len(foundFSP) == 0:
        raise RuntimeError("No FSP found")
    elif len(foundFSP) > 1:
        print("FSPs: ",foundFSP)
        raise RuntimeError("More than one FSP Found ")
    else: 
        fspToLoad = foundFSP[0]
        subModule = importlib.util.module_from_spec(fspToLoad)
        fspToLoad.loader.exec_module(subModule)
        return subModule

def loadOneFSPRFGOrFail():
    module = loadOneFSPOrFail()
    return module.load_rfg()

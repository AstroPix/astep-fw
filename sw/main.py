"""
Test program to run the A-STEP test bench.

Author: Adrien Laviron, adrien.laviron@nasa.gov
"""
# Needed modules. They all import their own suppourt libraries, 
# and eventually there will be a list of which ones are needed to run
import pandas as pd
import asyncio
import time, os, sys, binascii

import drivers.boards
import drivers.astep.serial
import drivers.astropix.decode

# Logging stuff
import logging



#######################################################
#################### MAIN FUNCTION ####################

def main(args):
    print("This is fine.")




#######################################################
#################### TOP LEVEL ########################

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A-STEP Bench Testing Code for chip configuration and data collection.', 
                                     formatter_class=argparse.RawTextHelpFormatter, #allow formatting of the epilog
                                     epilog="""""") 

    # Options related to outputs
    parser.add_argument('-n', '--name', default='', required=False,
                        help='Option to give additional name to output files upon running. Default: NONE')
    parser.add_argument('-o', '--outdir', default='data/', required=False,
                        help='Output Directory for all datafiles, as a subdir within data/. Default: data/')
    ## DAN - I hate this saving strategy. Should think of a better way. Implementation is backwards and messy
    parser.add_argument('-d', '--dumpOutput', action='store_true', required=False, 
                        help='If passed, do not save raw data *.txt or decoded *.csv. If not passed, save the outputs. Log always saved. Default: save all')
    parser.add_argument('-p', '--printHits', action='store_true', required=False, 
                        help='Can only be used in autoread mode. If passed, print readout streams in real time to terminal, accepting potential data slowdown penalty. If not passed, no printouts during data collection. Default: post-collection printout') 

    # Options related to software run settings
    parser.add_argument('-L', '--loglevel', type=str, choices = ['D', 'I', 'E', 'W', 'C'], action="store", default='I',
                        help='Set loglevel used. Options: D - debug, I - info, E - error, W - warning, C - critical. DEFAULT: I')
    parser.add_argument('-T', '--runTime', type=float, action='store',  default=None,
                        help = 'Maximum run time (in minutes). Default: NONE (run until user CTL+C)')
    
    # Options related to Setup / Configuration of system
    parser.add_argument('-g', '--gecco', action='store_true', required=False, 
                        help='If passed, configure for GECCO HW. If not passed, configure for CMOD HW. Default: CMOD') 
    parser.add_argument('-y', '--yaml', action='store', required=False, type=str, default = ['quadChip_allOff'], nargs="+", 
                        help = 'filepath (in scripts/config/ directory) .yml file containing chip configuration. \
                                One file must be passed for each layer, from layer #0 to layer #2. \
                                Default: config/quadChip_allOff (All pixels off, only fisrt layer is configured)')
    parser.add_argument('-c', '--chipsPerRow', action='store', required=False, type=int, default = [4], nargs="+", 
                        help = 'Number of chips per SPI bus to enable. Can provide a single number or one number per bus. Default: 4')
    parser.add_argument('-sr', '--shiftRegister', action='store_true', required=False, 
                        help='If passed, configures chips via Shift Registers (SR). If not passed, configure chips via SPI. Default: SPI')
    
    # Options related to Setup / Configuration of the chip in data collection run
    parser.add_argument('-na', '--noAutoread', action='store_true', required=False, 
                        help='If passed, does not enable autoread features off chip. If not passed, read data with autoread. Default: autoread')
    parser.add_argument('-t', '--threshold', type = int, action='store', default=100,
                        help = 'Threshold voltage for digital ToT (in mV). DEFAULT: 100')
    parser.add_argument('-a', '--analog', action='store', required=False, type=int, default = None, nargs=3,
                        help = 'Turn on analog output in the given column. Can only enable one analog pixel per layer. 
                        Requires input in the form {layer, chip, col} (no wrapping brackets). 
                        Default: None')
                        #Default: layer 1, chip 0, col 0')
    
    # Options related to chip injection
    ## DAN - this isn't working. Pixel response to "any" injected amplitude always the same 17 us ToT
    parser.add_argument('-i', '--inject', action='store', default=None, type=int, nargs=4,
                    help =  'Turn on injection in the given layer, chip, row, and column. Default: No injection')
    parser.add_argument('-v','--vinj', action='store', default = None,  type=int,
                        help = 'Specify injection voltage (in mV). DEFAULT: value in config ')




    args = parser.parse_args()


    #Checks for outdir path
    if args.outdir != "data/":
            args.outdir = "data/"+args.outdir
    #check 'outdir' argument and add '/' if necessary
    if args.outdir[-1]!="/":
            args.outdir+="/"
    # Ensures output directory exists
    if os.path.exists(args.outdir) == False:
        os.mkdir(args.outdir)


    #Define output save name for all files
    fname="" if not args.name else args.name+"_"
    saveName = fname + time.strftime("%Y%m%d-%H%M%S") 

    # Define the loglevel
    ll = args.loglevel
    if ll == 'D':
        loglevel = logging.DEBUG ## DAN - not working! Causes runs to crash and read in tons of railed buffers after the alloted time???
    elif ll == 'I':
        loglevel = logging.INFO
    elif ll == 'E':
        loglevel = logging.ERROR
    elif ll == 'W':
        loglevel = logging.WARNING
    elif ll == 'C':
        loglevel = logging.CRITICAL
    logname = args.outdir+saveName+"_run.log"
    formatter = logging.Formatter('%(asctime)s:%(msecs)d.%(name)s.%(levelname)s:%(message)s')
    fh = logging.FileHandler(logname)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logging.getLogger().addHandler(sh) 
    logging.getLogger().addHandler(fh)
    logging.getLogger().setLevel(loglevel)
    global logger 
    logger = logging.getLogger(__name__)
    logger.info("Setup logger")


    #Live readout printing option only possible in autoread mode
    if args.printHits and args.noAutoread:
        logger.warning("Live readout printing is only possible when chip read in autoread mode. Live readout printing is now disabled and code will run in non-autoread mode.")

    #print(args.analog)
    #print(args.inject)

    #print(args.yaml)
    #print(args.chipsPerRow)
    #Layer counting begins at 0.
    #Make sure config arguments make sense
    if len(args.yaml) > len(args.chipsPerRow):
        args.chipsPerRow = [args.chipsPerRow[0]]*len(args.yaml)
        if len(args.chipsPerRow) > 1:
            logger.warning(f"Number of chips per row not provided for every layer - default to {args.chipsPerRow[0]} for all {len(args.yaml)} layers.")
    elif len(args.yaml) < len(args.chipsPerRow):
        raise ValueError("You need to provide one yaml configuration file for every chipsPerRow argument.")

    #Make sure analog/inject arguments make sense
    if args.analog is not None and (len(args.analog)!=3 or args.analog[0]<0 or args.analog[0]>2 or args.analog[1]<0 or args.analog[1]>3 or args.analog[2]<0):
        raise ValueError("Incorrect analog argument layer={0[0]},chip={0[1]},column={0[2]}".format(args.analog))
    if args.inject is not None and (len(args.inject)!=4 or args.inject[0]<0 or args.inject[0]>2 or args.inject[1]<0 or args.inject[1]>3 or args.inject[2]<0 or args.inject[3]<0):
        raise ValueError("Incorrect analog argument layer={0[0]},chip={0[1]},row={0[2]},column={0[3]}".format(args.inject))


    #sys.exit(0)



    asyncio.run(main(args, saveName))

import asyncio
import rfg.asyncio

import sys
import signal
from os import listdir
from os.path import isfile, join

import threading

import time
from time import sleep
import queue

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QRunnable, Slot, QThreadPool
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QLabel, QLayout, QMainWindow,
    QMenuBar, QSizePolicy, QStatusBar, QVBoxLayout,
    QWidget)
from pyqtgraph import PlotWidget
import pyqtgraph as pg

from plot import MplCanvas
from ui_layer_stats import UILayerStats

# This project common classes
import drivers.boards
from   drivers.boards.board_driver import BoardDriver


# Logging
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.info("Starting ui control v1b")

## IO Utility -> Run a coroutine for IO access on asyncio, this just helps make code readable and thread-safe (if needed)
#############
ioLock = threading.Lock()
def onIO(coro):
    with ioLock:
        return asyncio.run(coro)

## Load UI and Main Interfaces in async IO 
########
count = 0 
window : QMainWindow | None = None
uiStop       = threading.Event()
uiRunning    = threading.Event()
uiUpdateRegs = threading.Event()

def uiListConfigFiles():
    mypath = "./configs"
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def uiOpenConfigFile():
    configFile = window.configFilesList.currentText()
    print(f"Opening Config {configFile}")
    asic = onIO(window.boardDriver.setupASICSAuto(f"./configs/{configFile}"))
    window.configLoadedRows.setText(f"{asic.num_rows}")
    window.configLoadedColumns.setText(f"{asic.num_cols}")
    window.configLoadedChipVersion.setText(f"{asic.chipversion}")


def uiReadoutBufferDump():
    """This method dumps the readot buffer to file, in blocks of 11 bytes as it is an expected frame length (Chip Frame + FPGA framing)"""
    fileName = "readout-dump-"+ time.strftime("%Y%m%d-%H%M%S") + ".raw"
    numberOfBytes = onIO(window.boardDriver.readoutGetBufferSize())
    if numberOfBytes > 0:
        readBytes = onIO(window.boardDriver.readoutReadBytes(count = numberOfBytes))
        bitfile = open(fileName,'w')
        bitfile.write(f"Size={hex(numberOfBytes)}\n")

        n = 11 
        split = [readBytes[i:i + n] for i in range(0, len(readBytes), n)] 
        
        for chunck in split:
            bitfile.write(''.join('{:02X}'.format(a) for a in chunck))
            bitfile.write("\n")
        bitfile.close()

class FunWinWorker(QRunnable):

    def __init__(self,app,window,fun):
        super(FunWinWorker, self).__init__()
        self.app = app
        self.window = window
        self._fun = fun

    @Slot()  # QtCore.Slot
    def run(self):
        self._fun(self.app,self.window)


def uiStartup(app,window):
    logger.info("Startup...")

    ## Open Board driver
    boardDriver = drivers.boards.getGeccoFTDIDriver()
    
    window.deviceStatus.setText(f"Opening")
    window.deviceStatus.setStyleSheet(u"background-color:yellow;color:black;font-weight:bold;padding:2px;")

    try:
        sleep(1)
        asyncio.run(boardDriver.open())
        window.boardDriver = boardDriver

        window.deviceStatus.setText(f"Opened")
        window.deviceStatus.setStyleSheet(u"background-color:green;color:white;font-weight:bold;padding:2px;")

        ## Read FPGA Firmware version and ID
        fversion = asyncio.run(boardDriver.readFirmwareVersion())
        fid = asyncio.run(boardDriver.readFirmwareIDName())

        window.firmwareVersion.setText(f"{fid}, version: {fversion}")

        ## List Config Files
        ##################
        cfgFiles = uiListConfigFiles()
        for f in cfgFiles:
            window.configFilesList.addItem(f)

        ## Update things
        ############
        uiRunning.set()
        uiUpdateRegs.set()



    except Exception as e:
        window.deviceStatus.setText(f"{e}")
        window.deviceStatus.setStyleSheet(u"background-color:rgb(255,0,0);color:white;font-weight:bold;padding:2px;")
        raise e

    pass

def uiUpdater(app,window):
    """This method runs in a thread with a 1s sleep, it updates all the fields that should be monitored"""
    while not uiStop.is_set():
        
        # Wait for UI Running
        if not uiRunning.is_set() and not uiStop.is_set():
            try:
                uiRunning.wait(timeout = .5)
            except:
                pass
        
        # Read and update
        if  uiRunning.is_set():
            boardDriver = window.boardDriver

            ## FPGA values
            temp = onIO(window.boardDriver.houseKeeping.readFPGATemperature())
            window.fpgaTemperatureCanvas.addPoint(temp)
            window.fpgaTemperatureText.setText(f"{temp} °C")

            ## Main Buffer
            window.readoutBufferSize.setText(f"{onIO(window.boardDriver.readoutGetBufferSize())} bytes")

            ## Layers: MISO Bytes count, interrupt status
            for i in range(3):

                bytesCount = onIO(window.boardDriver.getLayerMISOBytesCount(i))
                layerInfoWidget = window.leftLayerBoxesLayout.itemAt(i).widget()
                layerInfoWidget.setMISOBytesCount(bytesCount)

                layerStatus = onIO(boardDriver.getLayerStatus(i))
                layerInfoWidget.setStatusInterrupt(False if layerStatus & 0x1 != 0 else True) # Interrupt is negactive, so interrupt is true if bit is 0

            ## Update status registers which are not always updated on request
            if uiUpdateRegs.is_set() is True:
                uiUpdateRegs.clear()

                ## IO Control
                ioCtrl = onIO(boardDriver.getIOControlRegister())
                window.ioSampleClockEnBox.blockSignals(True)
                window.ioTimestampClockEnBox.blockSignals(True)
                window.ioSampleClockSEBox.blockSignals(True)
                window.ioInjToCardEnBox.blockSignals(True)

                window.ioSampleClockEnBox.setChecked(ioCtrl & 0x1)
                window.ioTimestampClockEnBox.setChecked(ioCtrl & 0x2)
                window.ioSampleClockSEBox.setChecked(ioCtrl & 0x4)
                window.ioInjToCardEnBox.setChecked(ioCtrl & 0x8)

                window.ioSampleClockEnBox.blockSignals(False)
                window.ioTimestampClockEnBox.blockSignals(False)
                window.ioSampleClockSEBox.blockSignals(False)
                window.ioInjToCardEnBox.blockSignals(False)

                ## Layer Status
                for i in range(3):

                    layerStatus = onIO(boardDriver.getLayerStatus(i))
                    layerControl = onIO(boardDriver.getLayerControl(i))
                    layerStatIDLECounter = onIO(boardDriver.getLayerStatIDLECounter(i))
                    layerStatFRAMECounter = onIO(boardDriver.getLayerStatFRAMECounter(i))
                    
                    layerInfoWidget = window.leftLayerBoxesLayout.itemAt(i).widget()
                    layerInfoWidget.boardDriver = boardDriver
                    layerInfoWidget.setHold(True if layerControl & 0x1 != 0 else False)
                    layerInfoWidget.setReset(True if layerControl & 0x2 != 0 else False)
                    layerInfoWidget.setAutoread(False if layerControl & 0x4 != 0 else True)
                    layerInfoWidget.setIDLECounter(layerStatIDLECounter)
                    layerInfoWidget.setFRAMECounter(layerStatFRAMECounter)

                    layerInfoWidget.setStatusInterrupt(False if layerStatus & 0x1 != 0 else True) # Interrupt is negactive, so interrupt is true if bit is 0
                    layerInfoWidget.setStatusDecoding(True if layerStatus & 0x2 != 0 else False)
        # Wait
        sleep(1)


def uiRequestUpdate():
    uiUpdateRegs.set()


def mainUI():
    global window 
    loader = QUiLoader()
    app = QtWidgets.QApplication(sys.argv)
    window = loader.load("mainwindow.ui", None)
    
    ## Add Plots
    window.fpgaTemperatureCanvas  = MplCanvas( width=5, height=4, dpi=100,title = "FPGA Temperature")
    window.fpgaTemperatureCanvas.setRange(20,50)
    window.hkFPGATempWidgetLayout.addWidget(window.fpgaTemperatureCanvas)
    
    ## Add Layer stats
    for i in range(3):
        layerUI = UILayerStats(layerID = i)
        window.leftLayerBoxesLayout.addWidget(layerUI)
        layerUI.requestUpdateStats.connect(uiRequestUpdate)
    
    ## Connect Signals
    #############
    window.updateLayerStatsButton.clicked.connect(uiRequestUpdate)
    # v =  True if state is QtCore.Qt.Checked.value else False; 
    window.ioSampleClockEnBox.stateChanged.connect(lambda state,window=window: onIO(window.boardDriver.ioSetSampleClock(True if state is QtCore.Qt.Checked.value else False,True)))
    window.ioTimestampClockEnBox.stateChanged.connect(lambda state,window=window: onIO(window.boardDriver.ioSetTimestampClock(True if state is QtCore.Qt.Checked.value else False,True)))
    window.ioSampleClockSEBox.stateChanged.connect(lambda state,window=window: onIO(window.boardDriver.ioSetSampleClockSingleEnded(True if state is QtCore.Qt.Checked.value else False,True)))
    window.ioInjToCardEnBox.stateChanged.connect(lambda state,window=window: onIO(window.boardDriver.ioSetInjectionToGeccoInjBoard(True if state is QtCore.Qt.Checked.value else False,True)))

    window.configFileOpenButton.clicked.connect(uiOpenConfigFile)

    ## Readout Dump
    window.readoutBufferDump.clicked.connect(uiReadoutBufferDump)

    ## Run and stop after window closed
    ############
    window.show()

    ## Open Startup thread and regular updating
    startupWorker = FunWinWorker(app,window,uiStartup)
    regularUpdateWorker = FunWinWorker(app,window,uiUpdater)

    threadpool = QThreadPool()
    threadpool.start(startupWorker)
    threadpool.start(regularUpdateWorker)

    ## App is running here until the window is closed
    app.exec()

    ## Closing ->  Forbid UI updates and signal stop requested
    ##         ->  Wait for Threadpool to be done -> If a thread is not stopping properly, this will wait forever (then CTRL+C to stop)
    uiRunning.clear()
    uiStop.set()
    threadpool.waitForDone();
   


mainUI()



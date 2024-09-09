import asyncio
import sys
import signal

# Driver or RFG
import drivers.boards
import rfg.asyncio

from PySide6 import  QtCore, QtGui, QtWidgets

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QLabel, QLayout, QMainWindow,
    QMenuBar, QSizePolicy, QStatusBar, QVBoxLayout, QStackedLayout,
    QWidget)

class UILayerStats(QWidget):

    ## Custom Signals
    ##############
    requestUpdateStats = QtCore.Signal(int)

    def __init__(self,layerID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loader = QUiLoader()
        layout = QStackedLayout()
        self.setLayout(layout)

        self.layerID = layerID

        ## Load widget layout from ui file, then add to this widget layout
        self.widgetContent = loader.load("ui_layer_stats.ui", None)
        layout.addWidget(self.widgetContent)

        ## Customize
        self.widgetContent.topBox.setTitle(f"Layer {layerID}")

        

        ## Signals connections
        #############

        self.widgetContent.resetBox.stateChanged.connect(self.evtReset)
        self.widgetContent.holdBox.stateChanged.connect(self.evtHold)
        self.widgetContent.csBox.stateChanged.connect(self.evtChipSelect)

        self.widgetContent.resetCountersButton.clicked.connect(self.evtResetCounters)

        self.widgetContent.writeDummyBytesButton.clicked.connect(self.evtWriteDummyBytes)
        #self.widgetContent.resetBox.stateChanged.connect(self.evtReset)

        

    ## Events
    ############
    def evtReset(self,state):
        v =  True if state is QtCore.Qt.Checked.value else False
        asyncio.run(self.boardDriver.setLayerReset(self.layerID,reset = v, modify = True, flush = True))

    def evtHold(self,state):
        v =  True if state is QtCore.Qt.Checked.value else False
        asyncio.run(self.boardDriver.holdLayer(self.layerID,hold = v, flush = True))

    def evtChipSelect(self,state):
        v =  True if state is QtCore.Qt.Checked.value else False
        asyncio.run(self.boardDriver.layersSetSPICSN(cs = v, flush = True))
            
    def evtResetCounters(self):
        asyncio.run(self.boardDriver.resetLayerStatCounters(self.layerID))
        self.requestUpdateStats.emit(0)

    def evtWriteDummyBytes(self):
        print(f"Write {self.widgetContent.dummyBytesCount.value()}")
        asyncio.run(self.boardDriver.writeLayerBytes(self.layerID,[0x00]*self.widgetContent.dummyBytesCount.value(),True))
        self.requestUpdateStats.emit(0)

    ## UI Updates
    #################
    def setReset(self,v:bool) -> None:
        self.widgetContent.resetBox.blockSignals(True)
        self.widgetContent.resetBox.setChecked(v)
        self.widgetContent.resetBox.blockSignals(False)
    def setHold(self,v:bool) -> None:
        self.widgetContent.holdBox.blockSignals(True)
        self.widgetContent.holdBox.setChecked(v)
        self.widgetContent.holdBox.blockSignals(False)

    def setAutoread(self,v:bool) -> None:
        self.widgetContent.autoReadBox.blockSignals(True)
        self.widgetContent.autoReadBox.setChecked(v)
        self.widgetContent.autoReadBox.blockSignals(False)

    def setIDLECounter(self,v:int) ->None:
        self.widgetContent.idleCounterText.blockSignals(True)
        self.widgetContent.idleCounterText.setText(f"{v}")
        self.widgetContent.idleCounterText.blockSignals(False)

    def setFRAMECounter(self,v:int) ->None:
        self.widgetContent.frameCounterText.blockSignals(True)
        self.widgetContent.frameCounterText.setText(f"{v}")
        self.widgetContent.frameCounterText.blockSignals(False)

    def setStatusInterrupt(self,v:bool) ->None:
        self.widgetContent.interruptBox.blockSignals(True)
        self.widgetContent.interruptBox.setChecked(v)
        self.widgetContent.interruptBox.blockSignals(False)

    def setStatusDecoding(self,v:bool) ->None:
        self.widgetContent.decodingBox.blockSignals(True)
        self.widgetContent.decodingBox.setChecked(v)
        self.widgetContent.decodingBox.blockSignals(False)

    def setMISOBytesCount(self,v:int) -> None:
        self.widgetContent.misoBytesCount.setText(f"{v}")



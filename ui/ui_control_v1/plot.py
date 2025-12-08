
import sys
import matplotlib

#matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
#from matplotlib.backends.backend_qtcairo import FigureCanvasQTCairo 
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100, maxData : int = 50, title: str | None = None ):
        fig = Figure(figsize=(width, height), dpi=dpi)
        
        super(MplCanvas, self).__init__(fig)
        self.axes = fig.add_subplot(111)
        self.maxData = maxData
        self.xdata = list()
        self.ydata = []

        self._plot_ref = None

        if title is not None:
            self.axes.set_title(title)

    def setRange(self,min:int,max:int):
        self.axes.set_ylim(bottom=min,top=max,auto = False)
        #self.axes.autoscale(enable=None, axis="y", tight=True)

    def resetAxesSettings(self):
        lim = self.axes.get_ylim()
        autoscale = self.axes.get_autoscale_on()
        if autoscale is False:
            self.setRange(lim[0],lim[1])

    def addPoint(self,x:float):

        # Append up to max length, after that append and drop first
        maxNotReached = len(self.ydata) < self.maxData
        if maxNotReached:
            self.ydata = self.ydata + [x]
            self.xdata = list(range(len(self.ydata)))
        else:
            self.ydata = self.ydata[1:] + [x]
        

        # Update or  len(self.ydata) < self.maxData self._plot_ref is None 
        if maxNotReached:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
      
            ## Clear old 
            if self._plot_ref is not None:
                line = self._plot_ref.pop(0)
                line.remove()

            #self.axes.clear()
            self._plot_ref = self.axes.plot(self.ydata,color='r')

        
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref[0].set_xdata(list(range(len(self.ydata))))
            self._plot_ref[0].set_ydata(self.ydata)
            #self._plot_ref.draw()

        # Trigger the canvas to update and redraw.
        self.draw()

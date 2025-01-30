from tkinter import *
import tkinter.ttk
from tkinter.ttk import *

"""
Utility to make a Scrollable Widget
Brutally copied from: https://blog.teclado.com/tkinter-scrollable-frames/ by Jose Salvatierra

"""


def rfgScrollableFrame(parent):
    sf =  ScrollableFrame(parent)
    #sf.pack(fill = X,side=TOP,padx = 10, pady=10)
    return (sf,sf.scrollable_frame)
    #return ScrollableFrame(parent)


class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self)
        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)

        #  print("Canvas Configured: "+str(self.winfo_width())
        self.bind(
            "<Configure>",
            lambda e: canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw",width=self.winfo_width()-10)
        )

        ## Content will be in here
        self.scrollable_frame = Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.updateCanvas(canvas) 
        )
        self.scrollable_frame.pack(fill = X,side=TOP,expand=True)

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill=BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

    def updateCanvas(self,canvas):
        canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        #print("Test: "+str(self.bbox("all")))
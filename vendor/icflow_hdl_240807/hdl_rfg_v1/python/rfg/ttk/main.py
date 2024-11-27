


from tkinter import *
import tkinter.ttk
from tkinter.ttk import *

uiVariables = {}
def createUIString(name,default:str): 
    v = StringVar(value = default)
    uiVariables[name] = v
    return v

def createUIInt(name,default:int): 
    v = IntVar(value = default)
    uiVariables[name] = v
    return v

def createUIFloat(name,default:float): 
    v = DoubleVar(value = default)
    uiVariables[name] = v
    return v

def updateUIInt(name:str,v:int):
    uiVariables[name].set(v)

def updateUIFloat(name:str,v:float):
    uiVariables[name].set(v)

def rfgFloatLabel(parent,id: str, labelText: str,default:float,suffix:str | None = None):
    """Create a Label"""
    # Create row
    frame = Frame(parent)
    # Create label
    lbl = Label(frame,text=labelText)
    # Create value holder
    valHolder = Label(frame)
    # Create variable
    var = createUIFloat(id, default)
    valHolder['textvariable'] = var
    # Create suffix
    if suffix is not None:
        s = Label(frame,text = suffix)
        s.grid(row = 0, column = 2)

    lbl.grid(row = 0, column = 0)
    valHolder.grid(row = 0, column = 1)

    return frame 

def rfgIntLabel(parent,id: str, labelText: str,default:int):
    """Create a Label"""
    # Create row
    frame = Frame(parent)
    # Create label
    lbl = Label(frame,text=labelText)
    # Create value holder
    valHolder = Label(frame)
    # Create variable
    var = createUIInt(id, default)
    valHolder['textvariable'] = var

    lbl.grid(row = 0, column = 0)
    valHolder.grid(row = 0, column = 1)

    return frame 

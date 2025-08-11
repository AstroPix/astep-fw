
import serial 
import serial.tools.list_ports_linux
import serial.tools.list_ports

import sys

#for port in serial.tools.list_ports_linux.comports():
#    print("Port: ",port.manufacturer, port.device)

def listLinuxFTDIPorts():
    return filter(lambda port: port.manufacturer == "FTDI" , serial.tools.list_ports_linux.comports())

def selectFirstLinuxFTDIPort():
    return next(iter(listLinuxFTDIPorts()), None)

def getFirstCOMPort():
    """Returns the first COM Port name to be passed as opening argument to board Driver - returns None if none"""
    ports = serial.tools.list_ports.comports()
    return ports[0][0] if len(ports) > 0 else None

def getFTDICOMPort():
    """Returns one FTDI COM port on windows (the last one, hopefully the second one)"""
    ports = serial.tools.list_ports.comports()
    ftdiport = None
    for port in ports:
        if port.manufacturer == "FTDI":
            ftdiport = port
    return ftdiport

def getSerialPort():
    if sys.platform.startswith("win"):
        return getFTDICOMPort()
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        return selectFirstLinuxFTDIPort()
    else:
        raise NotImplementedError("Automatic serial port selection not implemented for platform {}".format(sys.platform))
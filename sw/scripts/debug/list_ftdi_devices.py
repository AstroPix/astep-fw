import rfg.io.ftdi

for i,d in rfg.io.ftdi.listFTDIDevices():
    print(f"Device: {d}")
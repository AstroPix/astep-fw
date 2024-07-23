import serial.tools.list_ports 


ports = serial.tools.list_ports.comports()
print("Number of ports = %d" % len(ports))
for port,desc,hw in ports:
    print("- Port = %s" % port)
    print("- Desc = %s" % desc)
    print("- HW = %s" % hw)
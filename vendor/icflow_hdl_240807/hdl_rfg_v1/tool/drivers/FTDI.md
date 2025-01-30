


Download  from https://ftdichip.com/drivers/d2xx-drivers/

https://ftdichip.com/wp-content/uploads/2022/07/libftd2xx-x86_64-1.4.27.tgz

In this section the driver statically linked libraries and shared objects are copied to the
/usr/local/lib area for use by the native compiler.
All driver files are copied and symbolic links created using the Linux sudo command for root
permissions.
sudo cp /releases/build/lib* /usr/local/lib
Make the following symbolic links and permission modifications in /usr/local/lib:
cd /usr/local/lib
sudo ln –s libftd2xx.so.1.1.12 libftd2xx.so
sudo chmod 0755 libftd2xx.so.1.1.12
The symbolic link is used to select a default driver file. Any program can be linked against a
specific version of the library by using a version numbered library file.


From Nicolas:

Install D2XX driver: [Installation Guide](https://ftdichip.com/wp-content/uploads/2020/08/AN_220_FTDI_Drivers_Installation_Guide_for_Linux-1.pdf)

Check if VCP driver gets loaded:
    
    sudo lsmod | grep -a "ftdi_sio"

If yes, create a rule e.g., 99-ftdi-nexys.rules in /etc/udev/rules.d/ with the following content to unbid the VCP driver and make the device accessible for non-root users:

    ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010",\
    PROGRAM="/bin/sh -c '\
        echo -n $id:1.0 > /sys/bus/usb/drivers/ftdi_sio/unbind;\
        echo -n $id:1.1 > /sys/bus/usb/drivers/ftdi_sio/unbind\
    '"

    ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010",\
    MODE="0666"

Reload rules with:

    sudo udevadm trigger

Create links to shared lib:

    sudo ldconfig
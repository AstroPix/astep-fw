# Layer Interface

## Architecture and Clocking

The following figure presents an overview of the Layer interfaces blocks:


<figure markdown>
  ![block-layer-arch](./astep-fw-drawings.drawio)
  <figcaption>Block overview of Layer Interface</figcaption>
</figure>

The main identifial functionalities are:

- Shift Register Control: This Register File register controls the Shift Register Outputs to configure the Sensors
- QSPI I/O: This SPI Master module drives bytes to the Sensor from the MOSI Fifo, and writes read bytes to the MISO FIFO.
- Layer Frame Driver: This Module processes the data from sensors by discarding IDLE bytes and encapsulating data frames into layer frames, which are then written to the common readout.

The modules are all featuring AXI-Stream data interfaces, which are connected to the data FIFOs and to the layers readout switch, which grants transfer times to all layer interfaces sources in a round-robin fashion.

The AXI-Stream Data FIFO are dual clock FIFOS, through which the clock domain crossing from the fast core clock to the divided SPI Lock is operated

The SPI Clock divider is provided by the register file through the [spi_layers_ckdivider](main_rfg.md#spi_layers_ckdivider) register.




## Shift Register Configuration

Each Layer can be configured using a Shift Register Interface mapped to discrete I/Os:

<script type="WaveDrom">
{% include "../wavedrom/wd_layer_config_sr.json" %}
</script>

Each bit is set on the sin output, followed by two distinct clock cycles on ck1/ck2, then after all bits have been shifted, the ld0/ld1/ld3 is cycled.

There are 3 Load signals, one for each Layer. It means the layers cannot be independently configured in parallel, but if the configuration is the same for all layers, the user  can just shift all the bits then toggle the loads.

The Shift Register I/O are set through the register file, using the [Shift Register Output Register](./main_rfg#layers_sr_out)

## QSPI I/O

The QSPI Module is an SPI master which provides following functionalities:

- Outputs SPI Clock and Chip Select whenever a byte is available at the slave axi-stream interface is available (Clock output is the main input clock gated )
- Supports Sensor's two bit MOSI lines: Two bytes are read from the sensor while one byte is written to the interface
- Data is written to the sensor on Positive Edge, and Read on negative edge
- Module is instantiated in LSB first mode to match Sensor's LSB first output
- A force enable bit can be used to force writting NULL bytes to the sensor and read bytes from the sensor (used to trigger reading data when the sensor signals interruptn)
- Read Bytes are written to an AXIS Master interface
- If the Master output interface is stalling (full), the module will automatically stop the SPI interface to avoid loosing data to a full interface.


This module's data path is connected to AXIS Data Fifo providing the clock domain crossing between the fast core clock used to process data, and the configurable SPI I/O clock, which determines the speed of the SPI interface.

## Chip Select behavior

On the ASTEP hardware, we are sharing the Chip Select line betwenn all layers to save on I/O counts. Moreover, since the Layer Interface can automatically read data from the layers, the chip select line is controlled both by the firmware and the software so that configuration frames and readout can both be send with proper Chip Select driver.

The Chip Select line is driven in the following way:

- If Autoread is disabled, i.e SPI in Software driven:
    - Chip Select is 1 by default after FW reset
    - Each Layer has a bit called "cs", if set to 1, chip select is lowered, if 0, chip select is set back to 1.
        - For example for layer 0: [CTRL Register](./main_rfg.md#layer_0_cfg_ctrl)
    - The user is responsible for setting Chip Select before sending bytes to the layer, otherwise Chip Select will stay 1
    - The shared Chip Select Line will be lowered anytime the Chip Select bit of any layer is asserted
- If any Autoread is enabled, the Shared Chip Select is lowered by default and will stay low until all Autoread are disabled

The Python Board Driver allows setting the value of Chip Select using the layers control register: ["setLayerConfig"](../sw/reference.md#drivers.boards.board_driver.BoardDriver.setLayerConfig)

There is also a helper method to globally set the Chip Select by setting it in Layer 0, this helps simplify scripts.
For example:

~~~~python
# Configure Layer, just leave Chip Select to False
await driver.setLayerConfig(0, ... , chipSelect = False)
await driver.setLayerConfig(1, ... , chipSelect = False)
await driver.setLayerConfig(2, ... , chipSelect = False)

# Send some bytes to layer, select SPI before, and deselect after
await driver.layersSelectSPI(flush=True)
await driver.writeLayerBytes(layer = 0 , bytes = [0x01,0x02],flush=True)
await driver.layersDeselectSPI(flush=True)

# Same goes for Configuration via SPI, select SPI before
await driver.layersSelectSPI(flush=True)
await asic.writeSPIConfig(...)
await driver.layersDeselectSPI(flush=True)
~~~~

## MISO Disable

It can happen that some undesired data is read from the SPI while writing data to Astropix, for example during configuration, which can cause readout buffers to fill up and stall the SPI interface.

To help with this case if it happens, it is possible to deactivate the SPI read path of the Astropix interfaces by setting the disable_miso bit in the control register to 1. For Layer 0: [CTRL Register](./main_rfg.md#layer_0_cfg_ctrl)

The Python Driver can set this bit via **setLayerConfig**:

~~~~python
# Configure Layer, disable MISO and set Chip Select
await driver.setLayerConfig(0, ..., hold=True, chipSelect = True , disableMISO = True)

# Now configure the Chip without fearing any data can stall the SPI interface
await asic.writeSPIConfig(...)

# Don't forget to reenable MISO before reading data
await driver.setLayerConfig(0, ..., hold=False, chipSelect = True , disableMISO = False)

~~~~

!!! warning
    Using Disable MISO doesn't stop Astropix from sending frames if it has any, thus after enabling it back, the user must be certain that the next read byte is not
    a paylad byte from a data frame.
    To do this, make sure to keep hold to True when using disableMISO, then flush all data by activating the SPI in Hold mode until the Layer interrupt is 1.
    Then MISO can be enabled again and it is certain that the next data from Astropix will be IDLE or a Frame start.

## Layer Driver

The Layer driver receives bytes from the QSPI module through the axis Data FIFO, and processes them:

- IDLE bytes with value 0x3D which are returned by the sensor whenever there is no data are discarded.
- Upon detection of a Sensor Frame Header, the module will forward the sensor data in a layer frame format described below to its master interface.
- IDLE bytes and Frame detection trigger the increment of a statistics counter in the register file, which users can use to get information about the behavior of the module.

Additionally, if the module's **autoread** feature is enabled in the register file (For example for [Layer 0](main_rfg.md#layer_0_cfg_ctrl)), and the Layer interruptn is asserted by the sensor, it will automatically force the QSPI module into writting NULL bytes so that bytes are read from the sensor.

The Automatic Reading disables the SPI interface after the interrupt has been deasserted, and a configurable amount of IDLE bytes have been received. This value is configured through the [layers_cfg_nodata_continue][main_rfg.md#layers_cfg_nodata_continue] register.

Setting the automatic stop delay properly is important, because the Sensors Chain might de-assert the interrupt signal, which a data frame is still being propagated through the daisy chain. A good value could be 4 bytes stop delay per Chip in the Daisy Chain (16 for a Quad-Chip)

### Packet Framing

#### Frame Format

The Layer interface encapsulates data from the sensor in a layer frame format, made of:

- **Byte 0**: The Length of trailing data (up to 255 bytes, which could allow merging multiple sensor data frames)
- **Byte 1**: The ID of the layer - This value is fixed in fpga code via a parameter, but could be made software configurable
- **Bytes 2 : n - 4**: The Sensor data, n represents the number of bytes from the sensor. 5 Bytes for V2/V3 or 8 Bytes for V4
- **Bytes n-4 : end**: An FPGA Timestamp counter value captured when the first sensor data byte has been detected

<figure markdown>
  ![block-layer-packet](./astep-fw-drawings.drawio)
  <figcaption>Sensor and Layer Packet formats</figcaption>
</figure>

At the moment each Sensor Data Frame is encapsulated in a Layer Frame, which represents following overhead:

- **Astropix v2/v3**: 6 Bytes for the Layer Frame, 5 bytes for the Sensor Payload, 120% overhead
- **Astropix v4**: 6 Bytes for the Layer Frame, 8 bytes for the Sensor Payload, 37% overhead

These values are not very optimal, but considering the expected rates not critical.

Some improvement options that we can study:

- Astropix v2/v3 always send 2 Payload frames, the layer interface could frame at least two sensor frames, with a watchdog counter to prevent deadlocks. That would mean 6 bytes of framing for 10 bytes of payload, 60% overhead
- Astropix v4 sends frames per pixel, so that a hit normally only produces one data frame. In that case we could add a packet buffering stage that will buffer up sensor data frames with a time window and/or until a maximal length has been reached. This method increases latency but could potentially reduce overhead if needed.




#### Decoding

A typical Layer frame read from the buffers will look like following:

    0A 01 XXXXXXXXXX TTTT

- **0A**   : 10 Bytes following
- **01**   : Layer ID 1
- **XXXX** : The Sensor's 5 Bytes (v2/v3)
- **TTTT** : The 32 to 64 bits FPGA timestamp (Default: 32 bits)

For a V4 chip, this frame would change with a first byte set to **0D** (13 bytes)

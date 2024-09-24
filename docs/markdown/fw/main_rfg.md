

# Register File Reference
| Address | Name | Size | Features | Description |
|---------|------|------|-------|-------------|
|0x0 | [hk_firmware_id](#hk_firmware_id) | 32 |  | ID to identify the Firmware|
|0x4 | [hk_firmware_version](#hk_firmware_version) | 32 |  | Date based Build version: YEARMONTHDAYCOUNT|
|0x8 | [hk_xadc_temperature](#hk_xadc_temperature) | 16 |  | XADC FPGA temperature (automatically updated by firmware)|
|0xa | [hk_xadc_vccint](#hk_xadc_vccint) | 16 |  | XADC FPGA VCCINT (automatically updated by firmware)|
|0xc | [hk_conversion_trigger](#hk_conversion_trigger) | 32 | Counter w/ Interrupt | This register is a counter that generates regular interrupts to fetch new XADC values|
|0x10 | [hk_stat_conversions_counter](#hk_stat_conversions_counter) | 32 | Counter w/o Interrupt | Counter increased after each XADC conversion (for information) |
|0x14 | [hk_ctrl](#hk_ctrl) | 8 |  | Controls for HK modules|
|0x15 | [hk_adcdac_mosi_fifo](#hk_adcdac_mosi_fifo) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to ADC or DAC|
|0x16 | [hk_adc_miso_fifo](#hk_adc_miso_fifo) | 8 | AXIS FIFO Slave (read) | FIFO with read bytes from ADC|
|0x17 | [hk_adc_miso_fifo_read_size](#hk_adc_miso_fifo_read_size) | 32 |  | Number of entries in hk_adc_miso_fifo fifo|
|0x1b | [spi_layers_ckdivider](#spi_layers_ckdivider) | 8 |  | This clock divider provides the clock for the Layer SPI interfaces|
|0x1c | [spi_hk_ckdivider](#spi_hk_ckdivider) | 8 |  | This clock divider provides the clock for the Housekeeping ADC/DAC SPI interfaces|
|0x1d | [layer_0_cfg_ctrl](#layer_0_cfg_ctrl) | 8 |  | Layer 0 control bits|
|0x1e | [layer_1_cfg_ctrl](#layer_1_cfg_ctrl) | 8 |  | Layer 1 control bits|
|0x1f | [layer_2_cfg_ctrl](#layer_2_cfg_ctrl) | 8 |  | Layer 2 control bits|
|0x20 | [layer_0_status](#layer_0_status) | 8 |  | Layer 0 status bits|
|0x21 | [layer_1_status](#layer_1_status) | 8 |  | Layer 1 status bits|
|0x22 | [layer_2_status](#layer_2_status) | 8 |  | Layer 2 status bits|
|0x23 | [layer_0_stat_frame_counter](#layer_0_stat_frame_counter) | 32 | Counter w/o Interrupt | Counts the number of data frames|
|0x27 | [layer_1_stat_frame_counter](#layer_1_stat_frame_counter) | 32 | Counter w/o Interrupt | Counts the number of data frames|
|0x2b | [layer_2_stat_frame_counter](#layer_2_stat_frame_counter) | 32 | Counter w/o Interrupt | Counts the number of data frames|
|0x2f | [layer_0_stat_idle_counter](#layer_0_stat_idle_counter) | 32 | Counter w/o Interrupt | Counts the number of Idle bytes|
|0x33 | [layer_1_stat_idle_counter](#layer_1_stat_idle_counter) | 32 | Counter w/o Interrupt | Counts the number of Idle bytes|
|0x37 | [layer_2_stat_idle_counter](#layer_2_stat_idle_counter) | 32 | Counter w/o Interrupt | Counts the number of Idle bytes|
|0x3b | [layer_0_mosi](#layer_0_mosi) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 0 Astropix|
|0x3c | [layer_0_mosi_write_size](#layer_0_mosi_write_size) | 32 |  | Number of entries in layer_0_mosi fifo|
|0x40 | [layer_1_mosi](#layer_1_mosi) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 1 Astropix|
|0x41 | [layer_1_mosi_write_size](#layer_1_mosi_write_size) | 32 |  | Number of entries in layer_1_mosi fifo|
|0x45 | [layer_2_mosi](#layer_2_mosi) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 2 Astropix|
|0x46 | [layer_2_mosi_write_size](#layer_2_mosi_write_size) | 32 |  | Number of entries in layer_2_mosi fifo|
|0x4a | [layer_0_loopback_miso](#layer_0_loopback_miso) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 0 Astropix throug internal slave loopback|
|0x4b | [layer_0_loopback_miso_write_size](#layer_0_loopback_miso_write_size) | 32 |  | Number of entries in layer_0_loopback_miso fifo|
|0x4f | [layer_1_loopback_miso](#layer_1_loopback_miso) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 1 Astropix throug internal slave loopback|
|0x50 | [layer_1_loopback_miso_write_size](#layer_1_loopback_miso_write_size) | 32 |  | Number of entries in layer_1_loopback_miso fifo|
|0x54 | [layer_2_loopback_miso](#layer_2_loopback_miso) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 2 Astropix throug internal slave loopback|
|0x55 | [layer_2_loopback_miso_write_size](#layer_2_loopback_miso_write_size) | 32 |  | Number of entries in layer_2_loopback_miso fifo|
|0x59 | [layer_0_loopback_mosi](#layer_0_loopback_mosi) | 8 | AXIS FIFO Slave (read) | FIFO to read bytes received by internal slave loopback|
|0x5a | [layer_0_loopback_mosi_read_size](#layer_0_loopback_mosi_read_size) | 32 |  | Number of entries in layer_0_loopback_mosi fifo|
|0x5e | [layer_1_loopback_mosi](#layer_1_loopback_mosi) | 8 | AXIS FIFO Slave (read) | FIFO to read bytes received by internal slave loopback|
|0x5f | [layer_1_loopback_mosi_read_size](#layer_1_loopback_mosi_read_size) | 32 |  | Number of entries in layer_1_loopback_mosi fifo|
|0x63 | [layer_2_loopback_mosi](#layer_2_loopback_mosi) | 8 | AXIS FIFO Slave (read) | FIFO to read bytes received by internal slave loopback|
|0x64 | [layer_2_loopback_mosi_read_size](#layer_2_loopback_mosi_read_size) | 32 |  | Number of entries in layer_2_loopback_mosi fifo|
|0x68 | [layers_cfg_frame_tag_counter_ctrl](#layers_cfg_frame_tag_counter_ctrl) | 8 |  | A few bits to control the Frame Tagging Counter|
|0x69 | [layers_cfg_frame_tag_counter_trigger](#layers_cfg_frame_tag_counter_trigger) | 32 | Counter w/ Interrupt | This Interrupt Counter provides the enable signal for the frame tag counter|
|0x6d | [layers_cfg_frame_tag_counter](#layers_cfg_frame_tag_counter) | 32 | Counter w/o Interrupt | Counter to tag frames upon detection (Counter value added to frame output)|
|0x71 | [layers_cfg_nodata_continue](#layers_cfg_nodata_continue) | 8 |  | Number of IDLE Bytes until stopping readout|
|0x72 | [layers_sr_out](#layers_sr_out) | 8 |  | Shift Register Configuration I/O Control register|
|0x73 | [layers_sr_in](#layers_sr_in) | 8 |  | Shift Register Configuration Input control (Readback enable and layers inputs)|
|0x74 | [layers_inj_ctrl](#layers_inj_ctrl) | 8 |  | Control bits for the Injection Pattern Generator|
|0x75 | [layers_inj_waddr](#layers_inj_waddr) | 4 |  | Address for register to write in Injection Pattern Generator|
|0x76 | [layers_inj_wdata](#layers_inj_wdata) | 8 |  | Data for register to write in Injection Pattern Generator|
|0x77 | [layers_readout](#layers_readout) | 8 | AXIS FIFO Slave (read) | Reads from the readout data fifo|
|0x78 | [layers_readout_read_size](#layers_readout_read_size) | 32 |  | Number of entries in layers_readout fifo|
|0x7c | [io_ctrl](#io_ctrl) | 8 |  | Configuration register for I/O multiplexers and gating.|
|0x7d | [io_led](#io_led) | 8 |  | This register is connected to the Board's LED. See target documentation for detailed connection information.|
|0x7e | [gecco_sr_ctrl](#gecco_sr_ctrl) | 8 |  | Shift Register Control for Gecco Cards|
|0x7f | [hk_conversion_trigger_match](#hk_conversion_trigger_match) | 32 |  | |
|0x83 | [layers_cfg_frame_tag_counter_trigger_match](#layers_cfg_frame_tag_counter_trigger_match) | 32 |  | |


## <a id='hk_firmware_id'></a>hk_firmware_id


> ID to identify the Firmware


**Address**: 0x0


**Reset Value**: `RFG_FW_ID




## <a id='hk_firmware_version'></a>hk_firmware_version


> Date based Build version: YEARMONTHDAYCOUNT


**Address**: 0x4


**Reset Value**: `RFG_FW_BUILD




## <a id='hk_xadc_temperature'></a>hk_xadc_temperature


> XADC FPGA temperature (automatically updated by firmware)


**Address**: 0x8






## <a id='hk_xadc_vccint'></a>hk_xadc_vccint


> XADC FPGA VCCINT (automatically updated by firmware)


**Address**: 0xa






## <a id='hk_conversion_trigger'></a>hk_conversion_trigger


> This register is a counter that generates regular interrupts to fetch new XADC values


**Address**: 0xc






## <a id='hk_stat_conversions_counter'></a>hk_stat_conversions_counter


> Counter increased after each XADC conversion (for information) 


**Address**: 0x10






## <a id='hk_ctrl'></a>hk_ctrl


> Controls for HK modules


**Address**: 0x14




|[7:1] |0 |
|--|-- |
|RSVD |select_adc|

- select_adc: Selects ADC SPI Output. 0 selects DAC, 1 selects ADC


## <a id='hk_adcdac_mosi_fifo'></a>hk_adcdac_mosi_fifo


> FIFO to send bytes to ADC or DAC


**Address**: 0x15






## <a id='hk_adc_miso_fifo'></a>hk_adc_miso_fifo


> FIFO with read bytes from ADC


**Address**: 0x16






## <a id='hk_adc_miso_fifo_read_size'></a>hk_adc_miso_fifo_read_size


> Number of entries in hk_adc_miso_fifo fifo


**Address**: 0x17






## <a id='spi_layers_ckdivider'></a>spi_layers_ckdivider


> This clock divider provides the clock for the Layer SPI interfaces


**Address**: 0x1b


**Reset Value**: 8'h4




## <a id='spi_hk_ckdivider'></a>spi_hk_ckdivider


> This clock divider provides the clock for the Housekeeping ADC/DAC SPI interfaces


**Address**: 0x1c


**Reset Value**: 8'h4




## <a id='layer_0_cfg_ctrl'></a>layer_0_cfg_ctrl


> Layer 0 control bits


**Address**: 0x1d


**Reset Value**: 8'b00000111


|[7:6] |5 |4 |3 |2 |1 |0 |
|--|-- |-- |-- |-- |-- |-- |
|RSVD |loopback|disable_miso|cs|disable_autoread|reset|hold|

- hold: Hold Layer
- reset: Active High Layer Reset (Inverted before output to Sensor)
- disable_autoread: 1: Layer doesn't read frames if the interrupt is low, 0: Layer reads frames upon interrupt trigger
- cs: Chip Select, active high (inverted in firmware) - Set to 1 to force chip select low - if autoread is active, chip select is automatically 1
- disable_miso: If 1, the SPI interface won't read bytes from MOSI
- loopback: If 1, the Layer SPI Master is connected to the matching internal SPI Slave


## <a id='layer_1_cfg_ctrl'></a>layer_1_cfg_ctrl


> Layer 1 control bits


**Address**: 0x1e


**Reset Value**: 8'b00000111


|[7:6] |5 |4 |3 |2 |1 |0 |
|--|-- |-- |-- |-- |-- |-- |
|RSVD |loopback|disable_miso|cs|disable_autoread|reset|hold|

- hold: Hold Layer
- reset: Active High Layer Reset (Inverted before output to Sensor)
- disable_autoread: 1: Layer doesn't read frames if the interrupt is low, 0: Layer reads frames upon interrupt trigger
- cs: Chip Select, active high (inverted in firmware) - Set to 1 to force chip select low - if autoread is active, chip select is automatically 1
- disable_miso: If 1, the SPI interface won't read bytes from MOSI
- loopback: If 1, the Layer SPI Master is connected to the matching internal SPI Slave


## <a id='layer_2_cfg_ctrl'></a>layer_2_cfg_ctrl


> Layer 2 control bits


**Address**: 0x1f


**Reset Value**: 8'b00000111


|[7:6] |5 |4 |3 |2 |1 |0 |
|--|-- |-- |-- |-- |-- |-- |
|RSVD |loopback|disable_miso|cs|disable_autoread|reset|hold|

- hold: Hold Layer
- reset: Active High Layer Reset (Inverted before output to Sensor)
- disable_autoread: 1: Layer doesn't read frames if the interrupt is low, 0: Layer reads frames upon interrupt trigger
- cs: Chip Select, active high (inverted in firmware) - Set to 1 to force chip select low - if autoread is active, chip select is automatically 1
- disable_miso: If 1, the SPI interface won't read bytes from MOSI
- loopback: If 1, the Layer SPI Master is connected to the matching internal SPI Slave


## <a id='layer_0_status'></a>layer_0_status


> Layer 0 status bits


**Address**: 0x20




|[7:2] |1 |0 |
|--|-- |-- |
|RSVD |frame_decoding|interruptn|

- interruptn: -
- frame_decoding: -


## <a id='layer_1_status'></a>layer_1_status


> Layer 1 status bits


**Address**: 0x21




|[7:2] |1 |0 |
|--|-- |-- |
|RSVD |frame_decoding|interruptn|

- interruptn: -
- frame_decoding: -


## <a id='layer_2_status'></a>layer_2_status


> Layer 2 status bits


**Address**: 0x22




|[7:2] |1 |0 |
|--|-- |-- |
|RSVD |frame_decoding|interruptn|

- interruptn: -
- frame_decoding: -


## <a id='layer_0_stat_frame_counter'></a>layer_0_stat_frame_counter


> Counts the number of data frames


**Address**: 0x23






## <a id='layer_1_stat_frame_counter'></a>layer_1_stat_frame_counter


> Counts the number of data frames


**Address**: 0x27






## <a id='layer_2_stat_frame_counter'></a>layer_2_stat_frame_counter


> Counts the number of data frames


**Address**: 0x2b






## <a id='layer_0_stat_idle_counter'></a>layer_0_stat_idle_counter


> Counts the number of Idle bytes


**Address**: 0x2f






## <a id='layer_1_stat_idle_counter'></a>layer_1_stat_idle_counter


> Counts the number of Idle bytes


**Address**: 0x33






## <a id='layer_2_stat_idle_counter'></a>layer_2_stat_idle_counter


> Counts the number of Idle bytes


**Address**: 0x37






## <a id='layer_0_mosi'></a>layer_0_mosi


> FIFO to send bytes to Layer 0 Astropix


**Address**: 0x3b






## <a id='layer_0_mosi_write_size'></a>layer_0_mosi_write_size


> Number of entries in layer_0_mosi fifo


**Address**: 0x3c






## <a id='layer_1_mosi'></a>layer_1_mosi


> FIFO to send bytes to Layer 1 Astropix


**Address**: 0x40






## <a id='layer_1_mosi_write_size'></a>layer_1_mosi_write_size


> Number of entries in layer_1_mosi fifo


**Address**: 0x41






## <a id='layer_2_mosi'></a>layer_2_mosi


> FIFO to send bytes to Layer 2 Astropix


**Address**: 0x45






## <a id='layer_2_mosi_write_size'></a>layer_2_mosi_write_size


> Number of entries in layer_2_mosi fifo


**Address**: 0x46






## <a id='layer_0_loopback_miso'></a>layer_0_loopback_miso


> FIFO to send bytes to Layer 0 Astropix throug internal slave loopback


**Address**: 0x4a






## <a id='layer_0_loopback_miso_write_size'></a>layer_0_loopback_miso_write_size


> Number of entries in layer_0_loopback_miso fifo


**Address**: 0x4b






## <a id='layer_1_loopback_miso'></a>layer_1_loopback_miso


> FIFO to send bytes to Layer 1 Astropix throug internal slave loopback


**Address**: 0x4f






## <a id='layer_1_loopback_miso_write_size'></a>layer_1_loopback_miso_write_size


> Number of entries in layer_1_loopback_miso fifo


**Address**: 0x50






## <a id='layer_2_loopback_miso'></a>layer_2_loopback_miso


> FIFO to send bytes to Layer 2 Astropix throug internal slave loopback


**Address**: 0x54






## <a id='layer_2_loopback_miso_write_size'></a>layer_2_loopback_miso_write_size


> Number of entries in layer_2_loopback_miso fifo


**Address**: 0x55






## <a id='layer_0_loopback_mosi'></a>layer_0_loopback_mosi


> FIFO to read bytes received by internal slave loopback


**Address**: 0x59






## <a id='layer_0_loopback_mosi_read_size'></a>layer_0_loopback_mosi_read_size


> Number of entries in layer_0_loopback_mosi fifo


**Address**: 0x5a






## <a id='layer_1_loopback_mosi'></a>layer_1_loopback_mosi


> FIFO to read bytes received by internal slave loopback


**Address**: 0x5e






## <a id='layer_1_loopback_mosi_read_size'></a>layer_1_loopback_mosi_read_size


> Number of entries in layer_1_loopback_mosi fifo


**Address**: 0x5f






## <a id='layer_2_loopback_mosi'></a>layer_2_loopback_mosi


> FIFO to read bytes received by internal slave loopback


**Address**: 0x63






## <a id='layer_2_loopback_mosi_read_size'></a>layer_2_loopback_mosi_read_size


> Number of entries in layer_2_loopback_mosi fifo


**Address**: 0x64






## <a id='layers_cfg_frame_tag_counter_ctrl'></a>layers_cfg_frame_tag_counter_ctrl


> A few bits to control the Frame Tagging Counter


**Address**: 0x68


**Reset Value**: 8'h1


|[7:2] |1 |0 |
|--|-- |-- |
|RSVD |force_count|enable|

- enable: If 1, the counter will increment after the trigger counter reached its match value
- force_count: If 1, the counter will increment at each core clock cycle. If you flush a write with this value 1 then 0 in two data words, you can increment by 1 manually


## <a id='layers_cfg_frame_tag_counter_trigger'></a>layers_cfg_frame_tag_counter_trigger


> This Interrupt Counter provides the enable signal for the frame tag counter


**Address**: 0x69






## <a id='layers_cfg_frame_tag_counter'></a>layers_cfg_frame_tag_counter


> Counter to tag frames upon detection (Counter value added to frame output)


**Address**: 0x6d






## <a id='layers_cfg_nodata_continue'></a>layers_cfg_nodata_continue


> Number of IDLE Bytes until stopping readout


**Address**: 0x71


**Reset Value**: 8'd5




## <a id='layers_sr_out'></a>layers_sr_out


> Shift Register Configuration I/O Control register


**Address**: 0x72




|[7:6] |5 |4 |3 |2 |1 |0 |
|--|-- |-- |-- |-- |-- |-- |
|RSVD |ld2|ld1|ld0|sin|ck2|ck1|

- ck1: CK1 I/O for Shift Register Configuration
- ck2: CK2 I/O for Shift Register Configuration
- sin: SIN I/O for Shift Register Configuration
- ld0: Load signal for Layer 0
- ld1: Load signal for Layer 1
- ld2: Load signal for Layer 2


## <a id='layers_sr_in'></a>layers_sr_in


> Shift Register Configuration Input control (Readback enable and layers inputs)


**Address**: 0x73




|[7:4] |3 |2 |1 |0 |
|--|-- |-- |-- |-- |
|RSVD |sout2|sout1|sout0|rb|

- rb: Set to 1 to activate Shift Register Read back from layers
- sout0: -
- sout1: -
- sout2: -


## <a id='layers_inj_ctrl'></a>layers_inj_ctrl


> Control bits for the Injection Pattern Generator


**Address**: 0x74


**Reset Value**: 8'b00000110


|[7:7] |6 |5 |4 |3 |2 |1 |0 |
|--|-- |-- |-- |-- |-- |-- |-- |
|RSVD |running|done|write|trigger|synced|suspend|reset|

- reset: Reset for Pattern Generator - must be set to 1 after writing registers for config to be read
- suspend: Suspend module from running
- synced: -
- trigger: -
- write: Write Register value at address set by WADDR/WDATA registers
- done: Pattern generator finished configured sequence
- running: Pattern generator is running generating injection pulses


## <a id='layers_inj_waddr'></a>layers_inj_waddr


> Address for register to write in Injection Pattern Generator


**Address**: 0x75






## <a id='layers_inj_wdata'></a>layers_inj_wdata


> Data for register to write in Injection Pattern Generator


**Address**: 0x76






## <a id='layers_readout'></a>layers_readout


> Reads from the readout data fifo


**Address**: 0x77






## <a id='layers_readout_read_size'></a>layers_readout_read_size


> Number of entries in layers_readout fifo


**Address**: 0x78






## <a id='io_ctrl'></a>io_ctrl


> Configuration register for I/O multiplexers and gating.


**Address**: 0x7c


**Reset Value**: 8'b00001000


|[7:4] |3 |2 |1 |0 |
|--|-- |-- |-- |-- |
|RSVD |gecco_inj_enable|gecco_sample_clock_se|timestamp_clock_enable|sample_clock_enable|

- sample_clock_enable: Sample clock output enable. Sample clock output is 0 if this bit is set to 0
- timestamp_clock_enable: Timestamp clock output enable. Timestamp clock output is 0 if this bit is set to 0
- gecco_sample_clock_se: Selects the Single Ended output for the sample clock on Gecco.
- gecco_inj_enable: Selects the Gecco Injection to Injection Card output for the injection patterns. Set to 0 to route the injection pattern directly to the chip carrier


## <a id='io_led'></a>io_led


> This register is connected to the Board's LED. See target documentation for detailed connection information.


**Address**: 0x7d






## <a id='gecco_sr_ctrl'></a>gecco_sr_ctrl


> Shift Register Control for Gecco Cards


**Address**: 0x7e




|[7:3] |2 |1 |0 |
|--|-- |-- |-- |
|RSVD |ld|sin|ck|

- ck: -
- sin: -
- ld: -


## <a id='hk_conversion_trigger_match'></a>hk_conversion_trigger_match


> 


**Address**: 0x7f


**Reset Value**: 32'd10




## <a id='layers_cfg_frame_tag_counter_trigger_match'></a>layers_cfg_frame_tag_counter_trigger_match


> 


**Address**: 0x83


**Reset Value**: 32'd4



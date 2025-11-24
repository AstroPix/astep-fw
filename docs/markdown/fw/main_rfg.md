

# Register File Reference

| Address | Name | Size (bits) | Features | Description |
|---------|------|------|-------|-------------|
|0x0 | [hk_firmware_id](#hk_firmware_id) | 32 |  | ID to identify the Firmware |
|0x4 | [hk_firmware_version](#hk_firmware_version) | 32 |  | Date based Build version: YEARMONTHDAYCOUNT |
|0x8 | [clock_ctrl](#clock_ctrl) | 8 |  | Clock Control Register for the Firmware and Astropix |
|0x9 | [hk_xadc_temperature](#hk_xadc_temperature) | 16 |  | XADC FPGA temperature (automatically updated by firmware) |
|0xb | [hk_xadc_vccint](#hk_xadc_vccint) | 16 |  | XADC FPGA VCCINT (automatically updated by firmware) |
|0xd | [hk_conversion_trigger](#hk_conversion_trigger) | 32 | Counter w/ Interrupt | This register is a counter that generates regular interrupts to fetch new XADC values |
|0x11 | [hk_stat_conversions_counter](#hk_stat_conversions_counter) | 32 | Counter w/o Interrupt | Counter increased after each XADC conversion (for information)  |
|0x15 | [hk_ctrl](#hk_ctrl) | 8 |  | Controls for HK modules |
|0x16 | [hk_adcdac_mosi_fifo](#hk_adcdac_mosi_fifo) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to ADC or DAC |
|0x17 | [hk_adc_miso_fifo](#hk_adc_miso_fifo) | 8 | AXIS FIFO Slave (read) | FIFO with read bytes from ADC |
|0x18 | [hk_adc_miso_fifo_read_size](#hk_adc_miso_fifo_read_size) | 32 |  | Number of entries in hk_adc_miso_fifo fifo |
|0x1c | [spi_layers_ckdivider](#spi_layers_ckdivider) | 8 |  | This clock divider provides the clock for the Layer SPI interfaces |
|0x1d | [spi_hk_ckdivider](#spi_hk_ckdivider) | 8 |  | This clock divider provides the clock for the Housekeeping ADC/DAC SPI interfaces |
|0x1e | [layer_0_cfg_ctrl](#layer_0_cfg_ctrl) | 8 |  | Layer 0 control bits |
|0x1f | [layer_1_cfg_ctrl](#layer_1_cfg_ctrl) | 8 |  | Layer 1 control bits |
|0x20 | [layer_2_cfg_ctrl](#layer_2_cfg_ctrl) | 8 |  | Layer 2 control bits |
|0x21 | [layer_0_status](#layer_0_status) | 8 |  | Layer 0 status bits |
|0x22 | [layer_1_status](#layer_1_status) | 8 |  | Layer 1 status bits |
|0x23 | [layer_2_status](#layer_2_status) | 8 |  | Layer 2 status bits |
|0x24 | [layer_0_stat_frame_counter](#layer_0_stat_frame_counter) | 32 | Counter w/o Interrupt | Counts the number of data frames |
|0x28 | [layer_1_stat_frame_counter](#layer_1_stat_frame_counter) | 32 | Counter w/o Interrupt | Counts the number of data frames |
|0x2c | [layer_2_stat_frame_counter](#layer_2_stat_frame_counter) | 32 | Counter w/o Interrupt | Counts the number of data frames |
|0x30 | [layer_0_stat_idle_counter](#layer_0_stat_idle_counter) | 32 | Counter w/o Interrupt | Counts the number of Idle bytes |
|0x34 | [layer_1_stat_idle_counter](#layer_1_stat_idle_counter) | 32 | Counter w/o Interrupt | Counts the number of Idle bytes |
|0x38 | [layer_2_stat_idle_counter](#layer_2_stat_idle_counter) | 32 | Counter w/o Interrupt | Counts the number of Idle bytes |
|0x3c | [layer_0_stat_wronglength_counter](#layer_0_stat_wronglength_counter) | 32 | Counter w/o Interrupt | Counts the number of Astropix frames that have a length different than 4 (bytes) |
|0x40 | [layer_1_stat_wronglength_counter](#layer_1_stat_wronglength_counter) | 32 | Counter w/o Interrupt | Counts the number of Astropix frames that have a length different than 4 (bytes) |
|0x44 | [layer_2_stat_wronglength_counter](#layer_2_stat_wronglength_counter) | 32 | Counter w/o Interrupt | Counts the number of Astropix frames that have a length different than 4 (bytes) |
|0x48 | [layer_0_mosi](#layer_0_mosi) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 0 Astropix |
|0x49 | [layer_0_mosi_write_size](#layer_0_mosi_write_size) | 32 |  | Number of entries in layer_0_mosi fifo |
|0x4d | [layer_1_mosi](#layer_1_mosi) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 1 Astropix |
|0x4e | [layer_1_mosi_write_size](#layer_1_mosi_write_size) | 32 |  | Number of entries in layer_1_mosi fifo |
|0x52 | [layer_2_mosi](#layer_2_mosi) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 2 Astropix |
|0x53 | [layer_2_mosi_write_size](#layer_2_mosi_write_size) | 32 |  | Number of entries in layer_2_mosi fifo |
|0x57 | [layer_0_loopback_miso](#layer_0_loopback_miso) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 0 Astropix throug internal slave loopback |
|0x58 | [layer_0_loopback_miso_write_size](#layer_0_loopback_miso_write_size) | 32 |  | Number of entries in layer_0_loopback_miso fifo |
|0x5c | [layer_1_loopback_miso](#layer_1_loopback_miso) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 1 Astropix throug internal slave loopback |
|0x5d | [layer_1_loopback_miso_write_size](#layer_1_loopback_miso_write_size) | 32 |  | Number of entries in layer_1_loopback_miso fifo |
|0x61 | [layer_2_loopback_miso](#layer_2_loopback_miso) | 8 | AXIS FIFO Master (write) | FIFO to send bytes to Layer 2 Astropix throug internal slave loopback |
|0x62 | [layer_2_loopback_miso_write_size](#layer_2_loopback_miso_write_size) | 32 |  | Number of entries in layer_2_loopback_miso fifo |
|0x66 | [layer_0_loopback_mosi](#layer_0_loopback_mosi) | 8 | AXIS FIFO Slave (read) | FIFO to read bytes received by internal slave loopback |
|0x67 | [layer_0_loopback_mosi_read_size](#layer_0_loopback_mosi_read_size) | 32 |  | Number of entries in layer_0_loopback_mosi fifo |
|0x6b | [layer_1_loopback_mosi](#layer_1_loopback_mosi) | 8 | AXIS FIFO Slave (read) | FIFO to read bytes received by internal slave loopback |
|0x6c | [layer_1_loopback_mosi_read_size](#layer_1_loopback_mosi_read_size) | 32 |  | Number of entries in layer_1_loopback_mosi fifo |
|0x70 | [layer_2_loopback_mosi](#layer_2_loopback_mosi) | 8 | AXIS FIFO Slave (read) | FIFO to read bytes received by internal slave loopback |
|0x71 | [layer_2_loopback_mosi_read_size](#layer_2_loopback_mosi_read_size) | 32 |  | Number of entries in layer_2_loopback_mosi fifo |
|0x75 | [layers_fpga_timestamp_ctrl](#layers_fpga_timestamp_ctrl) | 16 |  | Register to control the FPGA Timestamp Behavior |
|0x77 | [layers_fpga_timestamp_divider](#layers_fpga_timestamp_divider) | 32 | Counter w/ Interrupt | This Counter interrupts on match, the interrupt output can be used to increment the FPGA Timestamp counter (dividing core clock) |
|0x7b | [layers_fpga_timestamp_counter](#layers_fpga_timestamp_counter) | 64 |  | FPGA Timestamp Counter added to data frames - reads the counter output of the TLU |
|0x83 | [layers_fpga_timestamp_forced](#layers_fpga_timestamp_forced) | 64 |  | FPGA Timestamp Counter added to data frames - forced value used if force_value is true in control register. Useful for debugging or software based TS |
|0x8b | [layers_tlu_trigger_delay](#layers_tlu_trigger_delay) | 16 |  | Delay to freeze counter after Trigger  |
|0x8d | [layers_tlu_busy_duration](#layers_tlu_busy_duration) | 16 |  | Number of clock cycle busy is active when a trigger comes in |
|0x8f | [layers_cfg_nodata_continue](#layers_cfg_nodata_continue) | 8 |  | Number of IDLE Bytes until stopping readout |
|0x90 | [layers_sr_out](#layers_sr_out) | 8 |  | Shift Register Configuration I/O Control register |
|0x91 | [layers_sr_in](#layers_sr_in) | 8 |  | Shift Register Configuration Input control (Readback enable and layers inputs) |
|0x92 | [layers_sr_rb_ctrl](#layers_sr_rb_ctrl) | 8 |  | Shift Register CRC and bits Readback control |
|0x93 | [layers_sr_crc](#layers_sr_crc) | 48 |  | CRC Output of readback module |
|0x99 | [layers_sr_bytes](#layers_sr_bytes) | 8 | AXIS FIFO Slave (read) | Readback SR bits packed as bytes |
|0x9a | [layers_sr_bytes_read_size](#layers_sr_bytes_read_size) | 32 |  | Number of entries in layers_sr_bytes fifo |
|0x9e | [layers_inj_ctrl](#layers_inj_ctrl) | 8 |  | Control bits for the Injection Pattern Generator |
|0x9f | [layers_inj_waddr](#layers_inj_waddr) | 4 |  | Address for register to write in Injection Pattern Generator |
|0xa0 | [layers_inj_wdata](#layers_inj_wdata) | 8 |  | Data for register to write in Injection Pattern Generator |
|0xa1 | [layers_readout_ctrl](#layers_readout_ctrl) | 8 |  |  |
|0xa2 | [layers_readout](#layers_readout) | 8 | AXIS FIFO Slave (read) | Reads from the readout data fifo |
|0xa3 | [layers_readout_read_size](#layers_readout_read_size) | 32 |  | Number of entries in layers_readout fifo |
|0xa7 | [io_ctrl](#io_ctrl) | 8 |  | Configuration register for I/O multiplexers and gating. |
|0xa8 | [io_led](#io_led) | 8 |  | This register is connected to the Board's LED. See target documentation for detailed connection information. |
|0xa9 | [gecco_sr_ctrl](#gecco_sr_ctrl) | 8 |  | Shift Register Control for Gecco Cards |
|0xaa | [hk_conversion_trigger_match](#hk_conversion_trigger_match) | 32 |  |  |
|0xae | [layers_fpga_timestamp_divider_match](#layers_fpga_timestamp_divider_match) | 32 |  |  |


## <a id='hk_firmware_id'></a>hk_firmware_id


> ID to identify the Firmware


**Address**: 0x0


**Reset Value**: `RFG_FW_ID




## <a id='hk_firmware_version'></a>hk_firmware_version


> Date based Build version: YEARMONTHDAYCOUNT


**Address**: 0x4


**Reset Value**: `RFG_FW_BUILD




## <a id='clock_ctrl'></a>clock_ctrl


> Clock Control Register for the Firmware and Astropix


**Address**: 0x8




| [7:5] | 4 | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |-- |
| RSVD |timestamp_clock_enable |sample_clock_enable |current_clk |ext_clk_differential |ext_clk_enable |

- ext_clk_enable : If 1, the external clock switchover mechanism is allowed
- ext_clk_differential : If 1, the external FPGA timestamp clock is differential - see target hardware to check for compatibility
- current_clk : If 1, the external clock is used for clocking. If this is 1 and ext_clk_enable is 0, it means a correct clock switching happened
- sample_clock_enable : Sample clock output enable. Sample clock output is 0 if this bit is set to 0
- timestamp_clock_enable : Timestamp clock output enable. Timestamp clock output is 0 if this bit is set to 0


## <a id='hk_xadc_temperature'></a>hk_xadc_temperature


> XADC FPGA temperature (automatically updated by firmware)


**Address**: 0x9






## <a id='hk_xadc_vccint'></a>hk_xadc_vccint


> XADC FPGA VCCINT (automatically updated by firmware)


**Address**: 0xb






## <a id='hk_conversion_trigger'></a>hk_conversion_trigger


> This register is a counter that generates regular interrupts to fetch new XADC values


**Address**: 0xd






## <a id='hk_stat_conversions_counter'></a>hk_stat_conversions_counter


> Counter increased after each XADC conversion (for information) 


**Address**: 0x11






## <a id='hk_ctrl'></a>hk_ctrl


> Controls for HK modules


**Address**: 0x15




| [7:4] | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |
| RSVD |spi_cpha |spi_cpol |select_dac |select_adc |

- select_adc : Selects ADC SPI Output. 0 selects DAC, 1 selects ADC
- select_dac : Selects DAC SPI Output. If ADC is also selected, only ADC is selected
- spi_cpol : Sets SPI Master CPOL mode
- spi_cpha : Sets SPI Master CPHA mode


## <a id='hk_adcdac_mosi_fifo'></a>hk_adcdac_mosi_fifo


> FIFO to send bytes to ADC or DAC


**Address**: 0x16






## <a id='hk_adc_miso_fifo'></a>hk_adc_miso_fifo


> FIFO with read bytes from ADC


**Address**: 0x17






## <a id='hk_adc_miso_fifo_read_size'></a>hk_adc_miso_fifo_read_size


> Number of entries in hk_adc_miso_fifo fifo


**Address**: 0x18






## <a id='spi_layers_ckdivider'></a>spi_layers_ckdivider


> This clock divider provides the clock for the Layer SPI interfaces


**Address**: 0x1c


**Reset Value**: 8'h4




## <a id='spi_hk_ckdivider'></a>spi_hk_ckdivider


> This clock divider provides the clock for the Housekeeping ADC/DAC SPI interfaces


**Address**: 0x1d


**Reset Value**: 8'h4




## <a id='layer_0_cfg_ctrl'></a>layer_0_cfg_ctrl


> Layer 0 control bits


**Address**: 0x1e


**Reset Value**: 8'b00000111


| [7:6] | 5 | 4 | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |-- |-- |
| RSVD |loopback |disable_miso |cs |disable_autoread |reset |hold |

- hold : Hold Layer
- reset : Active High Layer Reset (Inverted before output to Sensor)
- disable_autoread : 1: Layer doesn't read frames if the interrupt is low, 0: Layer reads frames upon interrupt trigger
- cs : Chip Select, active high (inverted in firmware) - Set to 1 to force chip select low - if autoread is active, chip select is automatically 1
- disable_miso : If 1, the SPI interface won't read bytes from MOSI
- loopback : If 1, the Layer SPI Master is connected to the matching internal SPI Slave


## <a id='layer_1_cfg_ctrl'></a>layer_1_cfg_ctrl


> Layer 1 control bits


**Address**: 0x1f


**Reset Value**: 8'b00000111


| [7:6] | 5 | 4 | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |-- |-- |
| RSVD |loopback |disable_miso |cs |disable_autoread |reset |hold |

- hold : Hold Layer
- reset : Active High Layer Reset (Inverted before output to Sensor)
- disable_autoread : 1: Layer doesn't read frames if the interrupt is low, 0: Layer reads frames upon interrupt trigger
- cs : Chip Select, active high (inverted in firmware) - Set to 1 to force chip select low - if autoread is active, chip select is automatically 1
- disable_miso : If 1, the SPI interface won't read bytes from MOSI
- loopback : If 1, the Layer SPI Master is connected to the matching internal SPI Slave


## <a id='layer_2_cfg_ctrl'></a>layer_2_cfg_ctrl


> Layer 2 control bits


**Address**: 0x20


**Reset Value**: 8'b00000111


| [7:6] | 5 | 4 | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |-- |-- |
| RSVD |loopback |disable_miso |cs |disable_autoread |reset |hold |

- hold : Hold Layer
- reset : Active High Layer Reset (Inverted before output to Sensor)
- disable_autoread : 1: Layer doesn't read frames if the interrupt is low, 0: Layer reads frames upon interrupt trigger
- cs : Chip Select, active high (inverted in firmware) - Set to 1 to force chip select low - if autoread is active, chip select is automatically 1
- disable_miso : If 1, the SPI interface won't read bytes from MOSI
- loopback : If 1, the Layer SPI Master is connected to the matching internal SPI Slave


## <a id='layer_0_status'></a>layer_0_status


> Layer 0 status bits


**Address**: 0x21




| [7:2] | 1 | 0 |
| --|-- |-- |
| RSVD |frame_decoding |interruptn |

- interruptn : -
- frame_decoding : -


## <a id='layer_1_status'></a>layer_1_status


> Layer 1 status bits


**Address**: 0x22




| [7:2] | 1 | 0 |
| --|-- |-- |
| RSVD |frame_decoding |interruptn |

- interruptn : -
- frame_decoding : -


## <a id='layer_2_status'></a>layer_2_status


> Layer 2 status bits


**Address**: 0x23




| [7:2] | 1 | 0 |
| --|-- |-- |
| RSVD |frame_decoding |interruptn |

- interruptn : -
- frame_decoding : -


## <a id='layer_0_stat_frame_counter'></a>layer_0_stat_frame_counter


> Counts the number of data frames


**Address**: 0x24






## <a id='layer_1_stat_frame_counter'></a>layer_1_stat_frame_counter


> Counts the number of data frames


**Address**: 0x28






## <a id='layer_2_stat_frame_counter'></a>layer_2_stat_frame_counter


> Counts the number of data frames


**Address**: 0x2c






## <a id='layer_0_stat_idle_counter'></a>layer_0_stat_idle_counter


> Counts the number of Idle bytes


**Address**: 0x30






## <a id='layer_1_stat_idle_counter'></a>layer_1_stat_idle_counter


> Counts the number of Idle bytes


**Address**: 0x34






## <a id='layer_2_stat_idle_counter'></a>layer_2_stat_idle_counter


> Counts the number of Idle bytes


**Address**: 0x38






## <a id='layer_0_stat_wronglength_counter'></a>layer_0_stat_wronglength_counter


> Counts the number of Astropix frames that have a length different than 4 (bytes)


**Address**: 0x3c






## <a id='layer_1_stat_wronglength_counter'></a>layer_1_stat_wronglength_counter


> Counts the number of Astropix frames that have a length different than 4 (bytes)


**Address**: 0x40






## <a id='layer_2_stat_wronglength_counter'></a>layer_2_stat_wronglength_counter


> Counts the number of Astropix frames that have a length different than 4 (bytes)


**Address**: 0x44






## <a id='layer_0_mosi'></a>layer_0_mosi


> FIFO to send bytes to Layer 0 Astropix


**Address**: 0x48






## <a id='layer_0_mosi_write_size'></a>layer_0_mosi_write_size


> Number of entries in layer_0_mosi fifo


**Address**: 0x49






## <a id='layer_1_mosi'></a>layer_1_mosi


> FIFO to send bytes to Layer 1 Astropix


**Address**: 0x4d






## <a id='layer_1_mosi_write_size'></a>layer_1_mosi_write_size


> Number of entries in layer_1_mosi fifo


**Address**: 0x4e






## <a id='layer_2_mosi'></a>layer_2_mosi


> FIFO to send bytes to Layer 2 Astropix


**Address**: 0x52






## <a id='layer_2_mosi_write_size'></a>layer_2_mosi_write_size


> Number of entries in layer_2_mosi fifo


**Address**: 0x53






## <a id='layer_0_loopback_miso'></a>layer_0_loopback_miso


> FIFO to send bytes to Layer 0 Astropix throug internal slave loopback


**Address**: 0x57






## <a id='layer_0_loopback_miso_write_size'></a>layer_0_loopback_miso_write_size


> Number of entries in layer_0_loopback_miso fifo


**Address**: 0x58






## <a id='layer_1_loopback_miso'></a>layer_1_loopback_miso


> FIFO to send bytes to Layer 1 Astropix throug internal slave loopback


**Address**: 0x5c






## <a id='layer_1_loopback_miso_write_size'></a>layer_1_loopback_miso_write_size


> Number of entries in layer_1_loopback_miso fifo


**Address**: 0x5d






## <a id='layer_2_loopback_miso'></a>layer_2_loopback_miso


> FIFO to send bytes to Layer 2 Astropix throug internal slave loopback


**Address**: 0x61






## <a id='layer_2_loopback_miso_write_size'></a>layer_2_loopback_miso_write_size


> Number of entries in layer_2_loopback_miso fifo


**Address**: 0x62






## <a id='layer_0_loopback_mosi'></a>layer_0_loopback_mosi


> FIFO to read bytes received by internal slave loopback


**Address**: 0x66






## <a id='layer_0_loopback_mosi_read_size'></a>layer_0_loopback_mosi_read_size


> Number of entries in layer_0_loopback_mosi fifo


**Address**: 0x67






## <a id='layer_1_loopback_mosi'></a>layer_1_loopback_mosi


> FIFO to read bytes received by internal slave loopback


**Address**: 0x6b






## <a id='layer_1_loopback_mosi_read_size'></a>layer_1_loopback_mosi_read_size


> Number of entries in layer_1_loopback_mosi fifo


**Address**: 0x6c






## <a id='layer_2_loopback_mosi'></a>layer_2_loopback_mosi


> FIFO to read bytes received by internal slave loopback


**Address**: 0x70






## <a id='layer_2_loopback_mosi_read_size'></a>layer_2_loopback_mosi_read_size


> Number of entries in layer_2_loopback_mosi fifo


**Address**: 0x71






## <a id='layers_fpga_timestamp_ctrl'></a>layers_fpga_timestamp_ctrl


> Register to control the FPGA Timestamp Behavior


**Address**: 0x75


**Reset Value**: 8'h0010


| [15:8] | 7 | 6 | [5:4] | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |-- |-- |-- |
| RSVD |force_lsb_0 |force_value |timestamp_size |tlu_busy_on_t0 |use_tlu |use_divider |enable |

- enable : -
- use_divider : If 1, the FGPA Timestamp will increment after the matching counter reached its match value, otherwise will increment on each core clock cycle
- use_tlu : If 1, the TLU module will be used
- tlu_busy_on_t0 : If 1, the busy signal out of TLU will be asserted after t0 initial
- timestamp_size : 16/32/48/64 bits Timestamp width
- force_value : If set to 1, the Timestamp will be forced to the value of the LAYERS_FPGA_TIMESTAMP_FORCED register
- force_lsb_0 : If set to 1, the Timestamp lsb will be forced to 1, effectively dividing counting by 2 and preventing the last byte of Timestamp to be 0xFF if in MSB first


## <a id='layers_fpga_timestamp_divider'></a>layers_fpga_timestamp_divider


> This Counter interrupts on match, the interrupt output can be used to increment the FPGA Timestamp counter (dividing core clock)


**Address**: 0x77






## <a id='layers_fpga_timestamp_counter'></a>layers_fpga_timestamp_counter


> FPGA Timestamp Counter added to data frames - reads the counter output of the TLU


**Address**: 0x7b






## <a id='layers_fpga_timestamp_forced'></a>layers_fpga_timestamp_forced


> FPGA Timestamp Counter added to data frames - forced value used if force_value is true in control register. Useful for debugging or software based TS


**Address**: 0x83






## <a id='layers_tlu_trigger_delay'></a>layers_tlu_trigger_delay


> Delay to freeze counter after Trigger 


**Address**: 0x8b


**Reset Value**: 16'd2




## <a id='layers_tlu_busy_duration'></a>layers_tlu_busy_duration


> Number of clock cycle busy is active when a trigger comes in


**Address**: 0x8d


**Reset Value**: 16'd16




## <a id='layers_cfg_nodata_continue'></a>layers_cfg_nodata_continue


> Number of IDLE Bytes until stopping readout


**Address**: 0x8f


**Reset Value**: 8'd5




## <a id='layers_sr_out'></a>layers_sr_out


> Shift Register Configuration I/O Control register


**Address**: 0x90




| [7:6] | 5 | 4 | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |-- |-- |
| RSVD |ld2 |ld1 |ld0 |sin |ck2 |ck1 |

- ck1 : CK1 I/O for Shift Register Configuration
- ck2 : CK2 I/O for Shift Register Configuration
- sin : SIN I/O for Shift Register Configuration
- ld0 : Load signal for Layer 0
- ld1 : Load signal for Layer 1
- ld2 : Load signal for Layer 2


## <a id='layers_sr_in'></a>layers_sr_in


> Shift Register Configuration Input control (Readback enable and layers inputs)


**Address**: 0x91




| [7:3] | 2 | 1 | 0 |
| --|-- |-- |-- |
| RSVD |sout2 |sout1 |sout0 |

- sout0 : -
- sout1 : -
- sout2 : -


## <a id='layers_sr_rb_ctrl'></a>layers_sr_rb_ctrl


> Shift Register CRC and bits Readback control


**Address**: 0x92




| [7:7] | [6:2] | 1 | 0 |
| --|-- |-- |-- |
| RSVD |sout_select |crc_enable |rb |

- rb : Set to 1 to activate Shift Register Read back from layers
- crc_enable : Set to 1 to enable CRC Module
- sout_select : Set to configure which SOUT is used - up to 32


## <a id='layers_sr_crc'></a>layers_sr_crc


> CRC Output of readback module


**Address**: 0x93






## <a id='layers_sr_bytes'></a>layers_sr_bytes


> Readback SR bits packed as bytes


**Address**: 0x99






## <a id='layers_sr_bytes_read_size'></a>layers_sr_bytes_read_size


> Number of entries in layers_sr_bytes fifo


**Address**: 0x9a






## <a id='layers_inj_ctrl'></a>layers_inj_ctrl


> Control bits for the Injection Pattern Generator


**Address**: 0x9e


**Reset Value**: 8'b00000110


| [7:7] | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |-- |-- |-- |
| RSVD |running |done |write |trigger |synced |suspend |reset |

- reset : Reset for Pattern Generator - must be set to 1 after writing registers for config to be read
- suspend : Suspend module from running
- synced : -
- trigger : -
- write : Write Register value at address set by WADDR/WDATA registers
- done : Pattern generator finished configured sequence
- running : Pattern generator is running generating injection pulses


## <a id='layers_inj_waddr'></a>layers_inj_waddr


> Address for register to write in Injection Pattern Generator


**Address**: 0x9f






## <a id='layers_inj_wdata'></a>layers_inj_wdata


> Data for register to write in Injection Pattern Generator


**Address**: 0xa0






## <a id='layers_readout_ctrl'></a>layers_readout_ctrl


> 


**Address**: 0xa1


**Reset Value**: 8'h01


| [7:1] | 0 |
| --|-- |
| RSVD |packet_mode |

- packet_mode : If 1, the Readout FIFO data will be filled only with full data frames


## <a id='layers_readout'></a>layers_readout


> Reads from the readout data fifo


**Address**: 0xa2






## <a id='layers_readout_read_size'></a>layers_readout_read_size


> Number of entries in layers_readout fifo


**Address**: 0xa3






## <a id='io_ctrl'></a>io_ctrl


> Configuration register for I/O multiplexers and gating.


**Address**: 0xa7


**Reset Value**: 8'b00011000


| [7:6] | 5 | 4 | 3 | 2 | 1 | 0 |
| --|-- |-- |-- |-- |-- |-- |
| RSVD |reserved5 |reserved4 |gecco_inj_enable |gecco_sample_clock_se |reserved1 |reserved0 |

- reserved0 : Sample clock output enable. Sample clock output is 0 if this bit is set to 0
- reserved1 : Timestamp clock output enable. Timestamp clock output is 0 if this bit is set to 0
- gecco_sample_clock_se : Selects the Single Ended output for the sample clock on Gecco.
- gecco_inj_enable : Selects the Gecco Injection to Injection Card output for the injection patterns. Set to 0 to route the injection pattern directly to the chip carrier
- reserved4 : -
- reserved5 : -


## <a id='io_led'></a>io_led


> This register is connected to the Board's LED. See target documentation for detailed connection information.


**Address**: 0xa8






## <a id='gecco_sr_ctrl'></a>gecco_sr_ctrl


> Shift Register Control for Gecco Cards


**Address**: 0xa9




| [7:3] | 2 | 1 | 0 |
| --|-- |-- |-- |
| RSVD |ld |sin |ck |

- ck : -
- sin : -
- ld : -


## <a id='hk_conversion_trigger_match'></a>hk_conversion_trigger_match


> 


**Address**: 0xaa


**Reset Value**: 32'd10




## <a id='layers_fpga_timestamp_divider_match'></a>layers_fpga_timestamp_divider_match


> 


**Address**: 0xae


**Reset Value**: 32'd4



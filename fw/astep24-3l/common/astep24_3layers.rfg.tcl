
## Sets the toplevel name only if not set already
icSetParameter IC_RFG_TARGET astep24_3l_top
icSetParameter IC_RFG_NAME   main_rfg

# This utility function replicates a list passed with an i index n times
proc rrepeat {count lst} {
    set range {}
    for {set i 0} {$i < $count} {incr i} {
        lappend range $i
    }
    set res  [lmap i $range {
         subst  $lst
    }]

    return [concat $res]
}

proc rrepeat {count lst} {
    set range {}
    set res {}
    for {set i 0} {$i < $count} {incr i} {
        set _def [subst $lst]
        lappend res [lindex ${_def} 0] [lindex ${_def} 1]
    }
    return $res

}

 #[rrepeat 3 {LAYER_${i}_IDLE_COUNTER   -size 16 -sw_read_only -counter -enable}]
icDefineParameter RFG_FW_ID "FW ID for the target"
if {[catch {set ::RFG_FW_ID}]} {
    #set ::RFG_FW_ID 32'h0000ff00
    set ::RFG_FW_ID `RFG_FW_ID
}
if {[catch {set ::RFG_EXTRA_BOARD_REGS}]} {
    set ::RFG_EXTRA_BOARD_REGS {}
}

## Build version, taken from define set in simulation or fpga project
set ::RFG_FW_BUILD `RFG_FW_BUILD

## Main registers definition
######################
#use_trigger_reset    { -doc "If 1, the FGPA Timestamp will reset upon external trigger reset input falling edge "}
#use_trigger_freeze   { -doc "If 1, the FGPA Timestamp output will be updated only on falling edge of the external trigger input"}
set baseRegisters {
    HK_FIRMWARE_ID         {-size 32 -reset ${::RFG_FW_ID}    -sw_read_only -hw_ignore -doc "ID to identify the Firmware"}
    HK_FIRMWARE_VERSION    {-size 32 -reset ${::RFG_FW_BUILD} -sw_read_only -hw_ignore -doc "Date based Build version: YEARMONTHDAYCOUNT"}
    CLOCK_CTRL {
        -size 8 -doc "Clock Control Register for the Firmware and Astropix"
        -reset 8'h2
        -bits {
            ext_clk_enable             {-doc "If 1, the external clock switchover mechanism is allowed"}
            ext_clk_differential       {-doc "If 1, the external FPGA timestamp clock is differential - see target hardware to check for compatibility"}
            current_clk                {-input  -doc "If 1, the external clock is used for clocking. If this is 1 and ext_clk_enable is 0, it means a correct clock switching happened"}
            sample_clock_enable        {-doc "Sample clock output enable. Sample clock output is 0 if this bit is set to 0"}
            timestamp_clock_enable     {-doc "Timestamp clock output enable. Timestamp clock output is 0 if this bit is set to 0"}
            
        }   
    }
    HK_XADC_TEMPERATURE    {-size 16 -sw_read_only -hw_write -doc "XADC FPGA temperature (automatically updated by firmware)"}
    HK_XADC_VCCINT         {-size 16 -sw_read_only -hw_write -doc "XADC FPGA VCCINT (automatically updated by firmware)"}
    HK_CONVERSION_TRIGGER  { -counter -interrupt -size 32 -match_reset 32'd10 -updown -doc "This register is a counter that generates regular interrupts to fetch new XADC values"}
    HK_STAT_CONVERSIONS_COUNTER {-size 32 -sw_read_only -counter -enable -hw_ignore -doc "Counter increased after each XADC conversion (for information) "}
    HK_CTRL {
        -doc "Controls for HK modules"
        -bits {
            select_adc { -doc "Selects ADC SPI Output. 0 selects DAC, 1 selects ADC"}
            select_dac { -doc "Selects DAC SPI Output. If ADC is also selected, only ADC is selected"}
            spi_cpol   { -doc "Sets SPI Master CPOL mode"}
            spi_cpha   { -doc "Sets SPI Master CPHA mode"}
        }
    }
    HK_ADCDAC_MOSI_FIFO  { -fifo_axis_master -with_tlast -doc "FIFO to send bytes to ADC or DAC"}
    HK_ADC_MISO_FIFO     { -fifo_axis_slave  -read_count -doc "FIFO with read bytes from ADC"}
    SPI_LAYERS_CKDIVIDER { -clock_divider spi_layers -reset 8'h4 -async_reset -doc "This clock divider provides the clock for the Layer SPI interfaces"}
    SPI_HK_CKDIVIDER     { -clock_divider spi_hk     -reset 8'h4 -async_reset -doc "This clock divider provides the clock for the Housekeeping ADC/DAC SPI interfaces"}

    [rrepeat 3 {LAYER_${i}_CFG_CTRL {
        -reset 8'b00000111
        -bits {
            hold             {-doc "Hold Layer"}
            reset            {-doc "Active High Layer Reset (Inverted before output to Sensor)"}
            disable_autoread {-doc "1: Layer doesn't read frames if the interrupt is low, 0: Layer reads frames upon interrupt trigger"}
            cs               {-doc "Chip Select, active high (inverted in firmware) - Set to 1 to force chip select low - if autoread is active, chip select is automatically 1"}
            disable_miso     {-doc "If 1, the SPI interface won't read bytes from MOSI"}
            loopback         {-doc "If 1, the Layer SPI Master is connected to the matching internal SPI Slave"}
        }
        -doc "Layer $i control bits"
    }}]
    [rrepeat 3 {LAYER_${i}_STATUS                   {-sw_read_only  -bits { interruptn {-input} frame_decoding {-input} } -doc "Layer $i status bits"}} ]
    [rrepeat 3 {LAYER_${i}_STAT_FRAME_COUNTER       {-size 32  -counter -enable -hw_ignore -doc "Counts the number of data frames"}}]
    [rrepeat 3 {LAYER_${i}_STAT_IDLE_COUNTER        {-size 32  -counter -enable -hw_ignore -doc "Counts the number of Idle bytes"}}]
    [rrepeat 3 {LAYER_${i}_STAT_WRONGLENGTH_COUNTER {-size 32  -counter -enable -hw_ignore -doc "Counts the number of Astropix frames that have a length different than 4 (bytes)"}}]
    [rrepeat 3 {LAYER_${i}_MOSI                     {-fifo_axis_master -with_tlast  -write_count -doc "FIFO to send bytes to Layer $i Astropix"}}]
    [rrepeat 3 {LAYER_${i}_LOOPBACK_MISO            {-fifo_axis_master -write_count -doc "FIFO to send bytes to Layer $i Astropix throug internal slave loopback"}}]
    [rrepeat 3 {LAYER_${i}_LOOPBACK_MOSI            {-fifo_axis_slave -read_count -doc "FIFO to read bytes received by internal slave loopback"}}]

    LAYERS_FPGA_TIMESTAMP_CTRL {
        -reset 8'h0010
        -size 16
        -bits {
            enable {}
            use_divider          { -doc "If 1, the FGPA Timestamp will increment after the matching counter reached its match value, otherwise will increment on each core clock cycle"}
            use_tlu              { -doc "If 1, the TLU module will be used"}
            tlu_busy_on_t0       { -doc "If 1, the busy signal out of TLU will be asserted after t0 initial"}
            timestamp_size       { -size 2 -doc "16/32/48/64 bits Timestamp width"}
            force_value {-doc "If set to 1, the Timestamp will be forced to the value of the LAYERS_FPGA_TIMESTAMP_FORCED register"}
            force_lsb_0 {-doc "If set to 1, the Timestamp lsb will be forced to 1, effectively dividing counting by 2 and preventing the last byte of Timestamp to be 0xFF if in MSB first"}
        }  -doc "Register to control the FPGA Timestamp Behavior"
    }
    LAYERS_FPGA_TIMESTAMP_DIVIDER {
        -size 32
        -counter
        -enable
        -interrupt
        -updown
        -match_reset 32'd4
        -doc "This Counter interrupts on match, the interrupt output can be used to increment the FPGA Timestamp counter (dividing core clock)"
    }
    LAYERS_FPGA_TIMESTAMP_COUNTER       {
        -size 64
        -hw_no_local_reg
        -sw_read_only
        -hw_write
        -doc "FPGA Timestamp Counter added to data frames - reads the counter output of the TLU"
    }
    LAYERS_FPGA_TIMESTAMP_FORCED       {
        -size 64
        -doc "FPGA Timestamp Counter added to data frames - forced value used if force_value is true in control register. Useful for debugging or software based TS"
    }
    LAYERS_TLU_TRIGGER_DELAY       {
        -reset 16'd2
        -size 16
        -doc "Delay to freeze counter after Trigger "
    }
    LAYERS_TLU_BUSY_DURATION       {
        -reset 16'd16
        -size 16
        -doc "Number of clock cycle busy is active when a trigger comes in"
    }

    LAYERS_CFG_NODATA_CONTINUE          {-reset 8'd5 -doc "Number of IDLE Bytes until stopping readout"}
    LAYERS_SR_OUT {
        -doc "Shift Register Configuration I/O Control register"
        -bits {
            CK1 {-doc "CK1 I/O for Shift Register Configuration"}
            CK2 {-doc "CK2 I/O for Shift Register Configuration"}
            SIN {-doc "SIN I/O for Shift Register Configuration"}
            LD0 {-doc "Load signal for Layer 0"}
            LD1 {-doc "Load signal for Layer 1"}
            LD2 {-doc "Load signal for Layer 2"}
            
        }
    }
    LAYERS_SR_IN {
        -doc "Shift Register Configuration Input control (Readback enable and layers inputs)"
        -bits {
            SOUT0 {-input}
            SOUT1 {-input}
            SOUT2 {-input}
            
        }
    }
    
    LAYERS_SR_RB_CTRL {
        -doc "Shift Register CRC and bits Readback control"
        -bits {
            RB    {-doc "Set to 1 to activate Shift Register Read back from layers"}
            CRC_ENABLE  { -doc "Set to 1 to enable CRC Module"}
            SOUT_SELECT { -size 5 -doc "Set to configure which SOUT is used - up to 32"}
        }
    }

    LAYERS_SR_CRC {
        -doc "CRC Output of readback module"
        -size 48
        -sw_read_only
        -hw_write
    }
    LAYERS_SR_BYTES {
        -doc "Readback SR bits packed as bytes"
        -fifo_axis_slave -read_count
    }
    LAYERS_INJ_CTRL {
        -reset 8'b00000110
        -doc "Control bits for the Injection Pattern Generator"
        -bits {
            reset   {-doc "Reset for Pattern Generator - must be set to 1 after writing registers for config to be read"}
            suspend {-doc "Suspend module from running"}
            synced  {}
            trigger {}
            write   {-doc "Write Register value at address set by WADDR/WDATA registers"}
            done    {-input -doc "Pattern generator finished configured sequence"}
            running {-input -doc "Pattern generator is running generating injection pulses"}
        }
    }
    LAYERS_INJ_WADDR {-size 4 -doc "Address for register to write in Injection Pattern Generator"  }
    LAYERS_INJ_WDATA {-doc "Data for register to write in Injection Pattern Generator" }
    LAYERS_READOUT_CTRL {
        -reset 8'h01
        -bits {
            packet_mode {-doc "If 1, the Readout FIFO data will be filled only with full data frames"}
        }
    }
    LAYERS_READOUT   {-fifo_axis_slave -read_count -doc "Reads from the readout data fifo"}
    IO_CTRL {
        -doc "Configuration register for I/O multiplexers and gating."
        -reset 8'b00011000
        -bits {
            reserved0        {-doc "Sample clock output enable. Sample clock output is 0 if this bit is set to 0"}
            reserved1     {-doc "Timestamp clock output enable. Timestamp clock output is 0 if this bit is set to 0"}
            gecco_sample_clock_se      {-doc "Selects the Single Ended output for the sample clock on Gecco." }
            gecco_inj_enable           {-doc "Selects the Gecco Injection to Injection Card output for the injection patterns. Set to 0 to route the injection pattern directly to the chip carrier"}
            reserved4         { }
            reserved5 { }
        }
    }
    IO_LED          {
        -doc "This register is connected to the Board's LED. See target documentation for detailed connection information."
    }
    GECCO_SR_CTRL   {
        -bits {ck {} sin {}  ld {}}
        -doc "Shift Register Control for Gecco Cards"
    }

}
return [concat $baseRegisters ${::RFG_EXTRA_BOARD_REGS} ]

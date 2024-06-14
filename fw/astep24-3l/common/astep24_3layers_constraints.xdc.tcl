## I/O Delays

#[Synth 8-3917] design astep24_3l_multitarget_top has port vadj_en driven by constant 1
# -id "Synth 8-3917"
set_msg_config -string vadj_en -suppress 
set_msg_config -string set_vadj -suppress

## Async inputs: First constraint to dummy virtual clock, then set falsepath so that warnings go away from reports
create_clock -name async_io_dummy_clk -period 10

# Uart I/O Delay can be ignored
# Interrupt is fully async, synced internally layers_sr_ld*
set async_in {uart_tx_in layer_*_interruptn cpu_resetn *resn layers_sr_sout* sw* btn*}
set async_out {uart_rx_out layers_sr_sin* layers_sr_ck* layers_sr_ld* *_hold  layers_sr_rb led* layer*_inj layer*_resn gecco_inj* gecco_sr*}

set_output_delay -max -clock async_io_dummy_clk 1.0 [get_ports $async_out ]
set_output_delay -min -clock async_io_dummy_clk 0.5 [get_ports $async_out ]

set_input_delay  -max -clock async_io_dummy_clk 1.0 [get_ports -filter {DIRECTION == IN} $async_in  ]
set_input_delay  -min -clock async_io_dummy_clk 0.5 [get_ports -filter {DIRECTION == IN} $async_in  ]

set_false_path -from [get_ports -filter {DIRECTION == IN} $async_in  ]
set_false_path -to   [get_ports $async_out ]


## SPI SW IF Clock
if {[llength [get_ports -quiet spi_clk]]>0} {
    set spi_min_period 20
    set spi_io_delay [expr $spi_min_period * 0.25]
    create_clock -period $spi_min_period -name sw_spi_clk [get_ports spi_clk]
    
    set_input_delay -max -clock sw_spi_clk $spi_io_delay  [get_ports spi_csn]
    set_input_delay -min -clock sw_spi_clk 1              [get_ports spi_csn]

    set_input_delay -max -clock sw_spi_clk $spi_io_delay  [get_ports spi_mosi] 
    set_input_delay -min -clock sw_spi_clk 1              [get_ports spi_mosi] 

    set_output_delay  -max -clock sw_spi_clk $spi_io_delay  [get_ports spi_miso] 
    set_output_delay  -min -clock sw_spi_clk 1              [get_ports spi_miso]
}

## Layers SPI Clocks
###############

## Generated Clock for SPI divided clock output
create_generated_clock -name layers_spi_divided -source [get_pins -of_objects [get_clocks -of_objects [get_pins -hierarchical *spi_layers_ckdivider_divided_clk*]]] -divide_by 2 [get_pins -hierarchical *spi_layers_ckdivider_divided_clk*/Q]

set hkDividedPin [get_pins -quiet -hierarchical *spi_hk_ckdivider_divided_clk*]
if {[llength $hkDividedPin]>0} {
    create_generated_clock -name hk_spi_divided     -source [get_pins -of_objects [get_clocks -of_objects [get_pins -hierarchical *spi_hk_ckdivider_divided_clk*]]] -divide_by 2 [get_pins -hierarchical *spi_hk_ckdivider_divided_clk*/Q]
}

#create_generated_clock -name spi_layer0_clock -source [get_pins -of_objects [get_clocks layers_spi_divided]] -divide_by 1 -combinational [get_ports layer_0_spi_clk]
#create_generated_clock -name spi_layer1_clock -source [get_pins -of_objects [get_clocks layers_spi_divided]] -divide_by 1 -combinational [get_ports layer_1_spi_clk]
#create_generated_clock -name spi_layer2_clock -source [get_pins -of_objects [get_clocks layers_spi_divided]] -divide_by 1 -combinational [get_ports layer_2_spi_clk]

#### Layer SPI delays, assume maximum 20 Mhz (50ns) - reserve 75% of period
set layer_spi_min_period 50
set layer_spi_io_delay [expr $layer_spi_min_period * 0.25]

## Common csn - remove timing, signal is sw driven
set_false_path -to [get_ports layers_spi_csn ]


## Layers SPI Constraints
for {set i 0} {$i < 3} {incr i} {

    ## Layer 1
    set layerPorts [get_ports -quiet layer_${i}*]
    if {[llength $layerPorts]>0} {
        
        #set_false_path -through [get_ports [list layer_${i}_inj layer_${i}_resn] ]
 
        set_output_delay -max -clock layers_spi_divided $layer_spi_io_delay    [get_ports layer_${i}_spi_mosi ]
        set_output_delay -min -clock layers_spi_divided 1                      [get_ports layer_${i}_spi_mosi ]
       
        set_input_delay  -max -clock layers_spi_divided  $layer_spi_io_delay   [get_ports layer_${i}_spi_miso* ] -clock_fall
        set_input_delay  -min -clock layers_spi_divided  1                     [get_ports layer_${i}_spi_miso* ] -clock_fall

    }

}


## ADC + DAC
if {[llength [get_ports -quiet ext_spi*]]>0} {

    # CSN is sw driven, deactivate timing
    set_false_path -to [get_ports {ext_spi_dac_csn ext_spi_adc_csn} ]
    set_output_delay -max -clock hk_spi_divided $layer_spi_io_delay  [get_ports {ext_spi_mosi}  ]
    set_output_delay -min -clock hk_spi_divided 1                    [get_ports {ext_spi_mosi}]

    set_input_delay  -max -clock hk_spi_divided  $layer_spi_io_delay [get_ports ext_spi_adc_miso ] -clock_fall
    set_input_delay  -min -clock hk_spi_divided  1                   [get_ports ext_spi_adc_miso ] -clock_fall
}




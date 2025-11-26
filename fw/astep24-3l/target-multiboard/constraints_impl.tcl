## This File is an Implementation level constraints
## It is only read after synthesis

## No Dedicated route to spi clock host interface, this avoids hard errors
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets spi_clk_IBUF]
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_ext_IBUF]


## Multi Cycle Paths
##########

## False Paths between clocks
########

# Exclude core to sample clock timing - there's no logic here appart from enable/disale gating from RFG
# Removed spurious timing errors
#set_false_path -from [get_clocks clk_core_top_clocking_core_io_uart] -to [get_clocks clk_sample_top_clocking_core_io_uart]
set_false_path -from [get_clocks clk_80_clk_core_extorint_40] -to [get_clocks clk_100_clk_core_extorint_40]
set_false_path -from [get_clocks clk_80_clk_core_extorint_40_1] -to [get_clocks clk_100_clk_core_extorint_40_1]


if {$::IC_BOARD == "astropix-nexys"} {

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_ext_diff]

    set_false_path -from [get_clocks clk_80_clk_core_extorint_40_2] -to [get_clocks clk_100_clk_core_extorint_40_2]

    set_clock_groups -physically_exclusive -group clk_out1_clk_sys_to_40 -group [get_clocks {ext_clk_se ext_clk_diff}]

} else {
    set_clock_groups -physically_exclusive -group clk_out1_clk_sys_to_40 -group [get_clocks {ext_clk_se}]
}



## Exclude Secondary and Primary clock paths from each other to avoid multiple clocked analyses and common timing of independent clock sources
##########

## First case are boards with both SE and DIFF ext clock
if {$::IC_BOARD=="astropix-nexys"} {


    # SPI divided clocks are not async to primary clock_core
    set_clock_groups -asynchronous -group {
        hk_spi_divided
        layers_spi_divided
        spi_layer0_clock_internal
        spi_layer1_clock_internal
        spi_layer2_clock_internal
    } -group {
            ext_clk_se
            ext_clk_diff

            clk_100_clk_core_extorint_40_1
            clk_80_clk_core_extorint_40_1
            clk_10_clk_core_extorint_40_1

            clk_100_clk_core_extorint_40_2
            clk_80_clk_core_extorint_40_2
            clk_10_clk_core_extorint_40_2
    }

    set_clock_groups -physically_exclusive -group {
        ext_clk_se
        ext_clk_diff
    } -group {
        clk_100_clk_core_extorint_40
        clk_80_clk_core_extorint_40
        clk_10_clk_core_extorint_40

        clk_100_clk_core_extorint_40_1
        clk_80_clk_core_extorint_40_1
        clk_10_clk_core_extorint_40_1

        clk_100_clk_core_extorint_40_2
        clk_80_clk_core_extorint_40_2
        clk_10_clk_core_extorint_40_2
    }

    set_clock_groups -physically_exclusive -group {
        clk_100_clk_core_extorint_40
        clk_80_clk_core_extorint_40
        clk_10_clk_core_extorint_40
        clk_out1_clk_sys_to_40
    } -group {


        clk_100_clk_core_extorint_40_1
        clk_80_clk_core_extorint_40_1
        clk_10_clk_core_extorint_40_1

        clk_100_clk_core_extorint_40_2
        clk_80_clk_core_extorint_40_2
        clk_10_clk_core_extorint_40_2
    }

    set_clock_groups -physically_exclusive -group {
        clk_100_clk_core_extorint_40_1
        clk_80_clk_core_extorint_40_1
        clk_10_clk_core_extorint_40_1
    } -group {
        clk_100_clk_core_extorint_40_2
        clk_80_clk_core_extorint_40_2
        clk_10_clk_core_extorint_40_2
    }


} else {


    # SPI divided clocks are not async to primary clock_core
    set_clock_groups -asynchronous -group {
        hk_spi_divided
        layers_spi_divided
        spi_layer0_clock_internal
        spi_layer1_clock_internal
        spi_layer2_clock_internal
    } -group {
            ext_clk_se

            clk_100_clk_core_extorint_40_1
            clk_80_clk_core_extorint_40_1
            clk_10_clk_core_extorint_40_1

    }

    set_clock_groups -physically_exclusive -group {
        ext_clk_se
        clk_out1_clk_sys_to_40
    } -group {
        clk_100_clk_core_extorint_40
        clk_80_clk_core_extorint_40
        clk_10_clk_core_extorint_40

        clk_100_clk_core_extorint_40_1
        clk_80_clk_core_extorint_40_1
        clk_10_clk_core_extorint_40_1

    }

    set_clock_groups -physically_exclusive -group {
        clk_100_clk_core_extorint_40
        clk_80_clk_core_extorint_40
        clk_10_clk_core_extorint_40
    } -group {


        clk_100_clk_core_extorint_40_1
        clk_80_clk_core_extorint_40_1
        clk_10_clk_core_extorint_40_1

    }

}
## IO False paths
###################

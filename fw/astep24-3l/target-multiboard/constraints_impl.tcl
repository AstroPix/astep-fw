## This File is an Implementation level constraints
## It is only read after synthesis

## No Dedicated route to spi clock host interface, this avoids hard errors
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets spi_clk_IBUF]

## Multi Cycle Paths
##########

## False Paths between clocks
########

# Exclude core to sample clock timing - there's no logic here appart from enable/disale gating from RFG
# Removed spurious timing errors
set_false_path -from [get_clocks clk_core_top_clocking_core_io_uart] -to [get_clocks clk_sample_top_clocking_core_io_uart]

## IO False paths
###################

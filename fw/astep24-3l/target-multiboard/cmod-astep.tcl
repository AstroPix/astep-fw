## Load main functions
source ../flow.tcl

## Open (see make.tcl for options)
#           board name	       Version    Defines             constraints file
run_bit     astropix-cmod      3          {CONFIG_SE}          [list $firmware_dir/../common/astep24_3layers_constraints.xdc.tcl $firmware_dir/constraints.cmod.tcl $firmware_dir/constraints_impl.tcl ]

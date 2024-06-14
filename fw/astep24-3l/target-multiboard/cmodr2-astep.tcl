## Load main functions
source ../flow.tcl

## Open (see make.tcl for options)
#           board name	       Version    Defines             constraints file
run_bit     astropix-cmodr2      3          {CONFIG_SE}          [list $firmware_dir/constraints.cmodr2.tcl $firmware_dir/constraints_impl.tcl $firmware_dir/../common/astep24_3layers_constraints.xdc.tcl]

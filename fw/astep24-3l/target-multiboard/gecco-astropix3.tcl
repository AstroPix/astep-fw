## Load main functions
source ../flow.tcl

## Open (see make.tcl for options)
#           board name	       Version    Defines                   constraints file
run_bit     astropix-nexys     3          {SINGLE_LAYER  SCLOCK_SE_DIFF}          [list $firmware_dir/../common/astep24_3layers_constraints.xdc.tcl $firmware_dir/constraints.tcl $firmware_dir/constraints_impl.tcl ]
run_bit     astropix-nexys     3          {SINGLE_LAYER  SCLOCK_SE_DIFF REVERSEADAPTER}          [list $firmware_dir/../common/astep24_3layers_constraints.xdc.tcl $firmware_dir/constraints_reverse_adapter.tcl $firmware_dir/constraints_impl.tcl ]
#run_bit     astropix-nexys     3          {SINGLE_LAYER SCLOCK_SE_DIFF}          [list $firmware_dir/constraints.tcl $firmware_dir/constraints_impl.tcl $firmware_dir/../common/astep24_3layers_constraints.xdc.tcl]

if {$ciMode} {

   ## Config as LVDS not Single ended
   run_bit     astropix-nexys     3          {SINGLE_LAYER CONFIG_SE SCLOCK_SE_DIFF}          [list $firmware_dir/../common/astep24_3layers_constraints.xdc.tcl $firmware_dir/constraints.tcl $firmware_dir/constraints_impl.tcl ]
   run_bit     astropix-nexys     3          {SINGLE_LAYER CONFIG_SE SCLOCK_SE_DIFF REVERSEADAPTER}          [list $firmware_dir/../common/astep24_3layers_constraints.xdc.tcl $firmware_dir/constraints_reverse_adapter.tcl $firmware_dir/constraints_impl.tcl ]

}

# set_property PROCESSING_ORDER EARLY [get_files -all /home/rleys/git/astep-fw/fw/astep24-3l/common/astep24_3layers_constraints.xdc.tcl]

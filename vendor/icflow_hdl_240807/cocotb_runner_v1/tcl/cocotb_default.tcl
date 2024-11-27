package require cocotb 1.0

set args [icflow::args::toDict $::argv]

icCheckParameters

## GUi
if {[icflow::args::contains $args -ui] || [icflow::args::contains $args -gui]} {
    set ::IC_SIM_UI 1
}

## Search for Sim File
############
if {[icflow::args::contains $args -f]} {
    set ::IC_NETLIST_F  [icflow::args::getValue $args -f -1]
    set ::IC_TOP        [lindex [split [file tail ${::IC_NETLIST_F}] .] 0]
} else {
    set fFileSuffix .sim.f
    if {[icflow::args::contains $args -sim_synth]} {
        set fFileSuffix .sim_synth.f
    }
    set fFile [lindex [concat [glob -nocomplain ./*$fFileSuffix] [glob -nocomplain ../*$fFileSuffix]  ] 0]
    if {[file exists $fFile]} {
        set ::IC_NETLIST_F     [file normalize $fFile]
        set ::IC_TOP           [lindex [split [file tail $fFile] .] 0]
    }
}



## If TB is defined, take it, otherwise add all py files
icSetParameter IC_SIM_TB_BASE [file normalize [pwd]]
if {[icIsParameterSet IC_SIM_TB] == false} {
    icSetParameter IC_SIM_TB [join [lsort [lmap pyFile [glob -nocomplain ./*.py] { string map {.py ""} [file tail $pyFile] }]] ,]
} 
#set pyFile [lindex  0]
#if {[file exists $pyFile]} {
#    set ::IC_SIM_TB         [file normalize $pyFile]
#}


set ::IC_SIM_WORKDIR .icflow/coco
coco_sim
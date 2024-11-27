package provide cocotb 1.0
package require icflow

icInfo "Loading Cocotb Helper package"

icDefineParameter IC_TOP            "Top Level Name"
icDefineParameter IC_NETLIST_F      "F File" {}
icDefineParameter IC_NETLIST_VLOG   "Verilog Files" {}
icDefineParameter IC_SIM_BUILD      "Default Simulation build work folder" .icflow/sim
icDefineParameter IC_SIM_SIMULATOR  "Selected Simulator" icarus
icDefineParameter IC_SIM_UI         "Try to open simulator UI" 0
icDefineParameter IC_SIM_EXTRA_ARGS "Extra arguments for sim" {}
icDefineParameter IC_SIM_TB         "Name of the python module to be used as testbench"
icDefineParameter IC_SIM_WORKDIR    "Folder to use to run stuff, to control where outputs are written and keep code folders clean" .icflow/coco

proc coco_parameters args {

    ## Parameters adaption
    ######################


    ## Force UI to 0 if no display
    if {![icflow::utils::icIsDisplayPresent]} {
        set ::IC_SIM_UI 0
    }

    ## Autoselect Simulator
    if {[icflow::utils::icIsToolPresent xrun]} {
        icInfo "XRun detected, switching to xcelium simulator"
        set ::IC_SIM_SIMULATOR xcelium

        
        ## F File support
        if {[llength $::IC_NETLIST_F]>0} {
            icInfo "Using F File for Xcelium"
            set ::IC_SIM_EXTRA_ARGS [list -f [join $::IC_NETLIST_F -f] ]
            set ::IC_NETLIST_VLOG {}

            if {${::IC_SIM_UI}==1} {
                lappend ::IC_SIM_EXTRA_ARGS -gui
            }
        }

        ## INDAGO
        if {[icflow::utils::icIsToolPresent indago]} {
            lappend ::IC_SIM_EXTRA_ARGS -debug_opts indago_pp -input probes.tcl
        }
    }

    icCheckParameters


}

proc coco_setup args {
    coco_parameters

    ## USe target Work Dir to move all file operations to this folder and avoid issues
    set targetWorkDir $::IC_SIM_WORKDIR

    ## Adapt Environment to find python module for tests 
    #set ::env(PYTHONPATH) $::mainFolder
    set ::env(PYTHONPATH) $::IC_SIM_TB_BASE:${::env(PYTHONPATH)}

    set ::env(PYTHONPYCACHEPREFIX) $::PWD/.icflow/pycache

    ## netlist   [list $simBuildDir/cocotb_iverilog_dump.v]
    #set simBuildDir .icflow/sim 
   

    ## Use vlog for now
    icInfo "Using simulator: ${::IC_SIM_SIMULATOR} "
    icInfo "Current Python Path: $::env(PYTHONPATH)"
    icInfo "Current run folder: $::PWD"


    ## Run WAVES=1
   
    exec mkdir -p $::env(PYTHONPYCACHEPREFIX)
    exec mkdir -p $::IC_SIM_BUILD
    exec rm -Rf $::IC_SIM_BUILD/*
    #exec cp $::env(CCTBV1_HOME)/setup/Makefile.run Makefile 
    exec cp $::env(CCTBV1_HOME)/setup/Makefile.setup   $::IC_SIM_BUILD/Makefile.setup
    exec cp $::env(CCTBV1_HOME)/setup/Makefile.run     $::IC_SIM_BUILD/Makefile.run

    
    icInfo "Setting up COCOTB"
    exec rm -f $::IC_SIM_BUILD/sim_requirements.txt
    if {[file exists requirements.txt]} {
        exec cat requirements.txt >> $::IC_SIM_BUILD/sim_requirements.txt
    }
    if {[file exists ../requirements.txt]} {
        exec cat ../requirements.txt >> $::IC_SIM_BUILD/sim_requirements.txt
    }
    
    exec make -C $::IC_SIM_BUILD/ SRCBASE=$::PWD -f Makefile.setup setup >@ stdout 2>@ stdout

}
proc coco_sim args {
    
    coco_setup


    icInfo "Running simulation"

    set netlist [concat $::IC_NETLIST_VLOG]
    icInfo "Using verilog Sources: $netlist"
 
    # SIM_BUILD=$::IC_SIM_BUILD \
    ## We are writing the command to a shell file so we can source the python env before calling make
    ## This is the only way at the moment to run cocotb from tcl script without requiring python env to be sourced by the user externally
    #set moduleName [lindex [split [file tail $::IC_SIM_TB] .] 0]
    set commandString "source .venv/bin/activate && make -f Makefile.run \
                COCOTB_ANSI_OUTPUT=1 \
                SIM=$::IC_SIM_SIMULATOR \
                EXTRA_ARGS='[join $::IC_SIM_EXTRA_ARGS " "]' \
                GUI=$::IC_SIM_UI WAVES=1 MODULE=$::IC_SIM_TB TOPLEVEL=$::IC_TOP VERILOG_SOURCES=[join $netlist " "] sim"
    set runScript [open $::IC_SIM_BUILD/run_simulation.sh w+]
    puts $runScript "#!/bin/bash"
    puts $runScript $commandString
    #puts $runScript "npm run report"
    close $runScript


    exec chmod +x ./$::IC_SIM_BUILD/run_simulation.sh
    try {
        cd $::IC_SIM_BUILD/
        exec ./run_simulation.sh  >@ stdout 2>@ stdout
    }
}

proc coco_waves args {

    exec gtkwave $::IC_SIM_BUILD/${::IC_TOP}.fst
}
#!/usr/bin/tclsh

# This script creates Vivado projects and bitfiles for the supported hardware platforms

## This method used to generate a Date version for RFG, so that SW can read a build version to easily check which firmware is flashed
proc getDateVersion args {
    set date [clock seconds]
    return   [clock format $date -format "%y%m%d"]01   
}

# Get project file dir
variable myLocation [file normalize [info script]]
proc getResourceDirectory {} {
    variable myLocation
    return [file dirname $myLocation]
}

## Directories
#########

## firmware_dir is the directory where the tcl and fpga top level is located
global firmware_dir
set firmware_dir [getResourceDirectory]
puts "Firware directory: $firmware_dir"

set commonSrcDir [file normalize $firmware_dir/../../common]
set astep3lSrcDir [file normalize $firmware_dir/../]

set include_dirs [list $firmware_dir/src $commonSrcDir/includes]

file mkdir reports
file mkdir bitstreams

## Config from Env 
set ciMode [expr [catch {set ::env(CI)}] == 1 ? 0 : 1]

proc add_files_no_simulation path {
    if {[file isdirectory $path]} {
        set addedFiles  [add_files -norecurse $path]
    } else {
        read_verilog    $path
        set addedFiles  [list $path]
    }
    if {[llength [get_files $addedFiles]]>0} {
        set_property -dict {used_in_synthesis true used_in_simulation true used_in_implementation true} [get_files $addedFiles]
    }
    
    
}
proc read_design_files {} {

    global firmware_dir
    global commonSrcDir
    global astep3lSrcDir

    add_files_no_simulation $firmware_dir/astep24_3l_multitarget_top.v
    
    add_files_no_simulation $astep3lSrcDir/common

    add_files_no_simulation $commonSrcDir/rtl/host/sw_ftdi245_spi_uart
    add_files_no_simulation $commonSrcDir/rtl/rfg/protocol
    add_files_no_simulation $commonSrcDir/rtl/rfg/spi
    add_files_no_simulation $commonSrcDir/rtl/rfg/ftdi
    add_files_no_simulation $commonSrcDir/rtl/rfg/uart

    add_files_no_simulation $commonSrcDir/rtl/housekeeping/
    add_files_no_simulation $commonSrcDir/rtl/layers/
    add_files_no_simulation $commonSrcDir/rtl/spi/

    add_files_no_simulation $commonSrcDir/rtl/utilities/
}

proc read_syn_ip {} {

    puts "Read and Synth IP"
    global firmware_dir
    global commonSrcDir
    global astep3lSrcDir
    global target_board

    set projectFiles [get_files]
    ## Go through IP directories from IP project and load all the XCI files found
    foreach ipDir [glob -nocomplain -type d $commonSrcDir/xilinx-ip/*] {
        set sourceIPFile $ipDir/[file tail $ipDir].xci
        if {[file exists $sourceIPFile]} {
            #set ip [import_ip  $ipPath]

            ##  Try to find IP in existing file set, and if source is newer, overwrite
            ##  If not newer, don't do anything
            set ipInProject [lsearch -glob -inline $projectFiles */[file tail $ipDir].xci]
            if {$ipInProject=="" || ([file mtime $sourceIPFile]>[file mtime $ipInProject])} {
                ## IF is not in project, just import
                ## First delete local srcs if present to ensure proper import
                ## If not and a local xci files exists, the source IP will be added and not imported :(
                puts "INFO: (Re)Importing, will delete: vivado-project/[get_projects].srcs/sources_1/ip/[file tail $ipDir]"
                if {$ipInProject!=""} {
                    catch {remove_files [get_files $ipInProject]}
                }
                catch {file delete -force vivado-project/[get_projects].srcs/sources_1/ip/[file tail $ipDir]}
                catch {import_ip $sourceIPFile}
            } 
            
            
        }
    }

    ## Upgrade IP for vivado version or target board, this should unlock the ips
    upgrade_ip [get_ips]

    ## Set Synthesis checkpoint request to true so that that ips are build with main synthesis command
    foreach srcFile [get_files] {
        if {[string match *.xci $srcFile]} {
            set_property generate_synth_checkpoint true $srcFile
        }
    }

    ## Update Buffer sizes
    ########

    # Readout buffer -> 4kB
    set_property -dict [list CONFIG.FIFO_DEPTH 4096] [get_ips fifo_axis_1clk_1kB]

    # Layers SPI Fifo -> 1kB
    set_property -dict [list CONFIG.FIFO_DEPTH 1024] [get_ips fifo_axis_2clk_spi_layer]
    
    ## On CMOD, update core clock to 20.00000
    ########
    if {$target_board=="astropix-cmod"} {
        set_property -dict [list CONFIG.CLKOUT3_REQUESTED_OUT_FREQ {20.000} ] [get_ips top_clocking_core_io_uart]
    }
    
}


proc run_bit {board version defines constraints_file} {

    global defines_list
    global chipversion
    global include_dirs
    global firmware_dir
    global commonSrcDir
    global astep3lSrcDir
    global target_board 

    
    

    ## Test if in open mode, if env(OPEN) is NOT set, catch returns 1
    set openMode [expr [catch {set ::env(OPEN)}] == 1 ? 0 : 1]
    set supported_chipversions [list 2 3 4]
    set supported_defines [list SCLOCK_SE_DIFF CONFIG_SE TELESCOPE SINGLE_LAYER]

    ## Check chip version
    if {$version in $supported_chipversions} {
        set chipversion $version
        puts "INFO: Valid chipversion $chipversion specified!"
    } else {
        puts "ERROR: Invalid chipversion $version specified!"
        return -level 1 -code error
    }

    
    set target_board $board
    array set supported_boards [list \
        astropix-nexys  [list xc7a200tsbg484-1 digilentinc.com:nexys_video:part0:1.2 [list RFG_FW_ID=32'h0000AB0${chipversion} TARGET_NEXYS] ] \
        astropix-cmod   [list xc7a35tcpg236-1  digilentinc.com:cmod_a7-35t:part0:1.2 [list RFG_FW_ID=32'h0000AC0${chipversion} TARGET_CMOD] ] \
    ]


    if {[info exists supported_boards($board)]} {
        set part           [lindex $supported_boards($board)  0]
        set board_name     [lindex $supported_boards($board)  1]
        ## Board defines are added to project after main project defines
        set board_defines  [lindex $supported_boards($board)  2]
        
    } else {
        puts "ERROR: Unsupported board $board specified!"
        return -level 1 -code error
    }

    

    foreach item $defines {
        if {$item ni $supported_defines} {
            puts "ERROR: Invalid define $item specified! Valid defines are: $supported_defines"
            return -level 1 -code error
        }
    }

    if {("CLOCK_SE_SE" in $defines) && ("CLOCK_SE_DIFF" in $defines)} {
        puts "ERROR: CLOCK_SE cannot be both single-ended and differential"
        return -level 1 -code error
    } else {
        puts "INFO: CLOCK_SE config valid!"
    }

    if {"TELESCOPE" in $defines} {
        puts "INFO: Configured for telescope setup!"
    } else {
        puts "INFO: Not configured for telescope setup!"
    }

    set defines_list $defines
    puts "INFO: Set verilog defines $defines_list"

    set defines_string [join $defines _]
    append design_name "$board\_$chipversion\_$defines_string"

    ## Project Creation
    ############

    # Close project if opened, helps resourcing the script from active vivado
    catch {close_project}

    # Set board file
    set_param board.repoPaths $firmware_dir/../../../vendor/digilent-vivado-boards/board_files
    set REPOPATH [get_param board.repoPaths]
    puts $REPOPATH

    # Start Flow
    ## Create Project: in Open mode, try to reopen existing project
    if {$openMode && [file exists ${design_name}.xpr]} {
        puts "INFO: Reopening project, to recreate delete this file: vivado-run/${design_name}.xpr"
        open_project ${design_name}.xpr
    } else {
        create_project -force -part $part $design_name .
        set_property board_part $board_name [current_project]
    }
    

    read_design_files
    read_syn_ip

    ## TCL constraints
    ###############

    # Read constraints
    read_xdc -unmanaged $constraints_file

    ## If we are in OPEN mode, Vivado GUI will start various steps in new processes, which causes Configurations used in constraints to be not available
    ## In OPEN mode, we are then writing the important configs to a new constraints file that will be loaded first
    if {$openMode} {
        set   openConstraintsFile   ".openMode.xdc.tcl"
        set   out                   [open $openConstraintsFile w+]

        puts  $out "global chipversion"
        puts  $out "global defines_list"
        puts  $out [subst {set chipversion $chipversion}]
        puts  $out [subst -nocommand {set defines_list [list $defines_list]}]
        close $out 
      
        read_xdc -unmanaged [file normalize $openConstraintsFile]
        reorder_files -fileset constrs_1 -before [lindex $constraints_file 0] [file normalize $openConstraintsFile]

    }

    
    # If a TCL file ends with "_impl.tcl", it is used only in implementation
    foreach constraintFile $constraints_file {
        if {[string match "*_impl.tcl" $constraintFile]} {
                set_property -dict {used_in_synthesis false used_in_simulation false used_in_implementation true} [get_files  $constraintFile]
        }
    }

    # Set Defines and inc dirs: Config defines + Board specific static defines + Dynamically created build version    
    #########
    set buildVersion  [getDateVersion]
    set final_defines [lsort [concat $board_defines $defines_list RFG_FW_BUILD=32'd$buildVersion SYNTHESIS=1 ASTROPIX${chipversion}]]
    puts "Final Defines: $final_defines"

    foreach fileSet [list [current_fileset] [get_fileset sim_1]] {
        set_property verilog_define $final_defines $fileSet
        set_property include_dirs   $include_dirs  $fileSet
    }
    

    ## Only Run Implementatino if no project opening is requested
    if {!$openMode} {
        #generate_target -verbose -force all [get_ips]
        synth_ip [get_ips]
        synth_design -top astep24_3l_multitarget_top
        opt_design
        place_design
        phys_opt_design
        route_design
        report_utilization -file "reports/report_utilization.$design_name.log"
        report_timing      -file "reports/report_timing.$design_name.log"
        report_timing_summary -file "reports/report_timing_summary.$design_name.log"
        
        set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design] 
        write_bitstream -force -bin_file bitstreams/${design_name}_${buildVersion} 
        if {$board=="astropix-cmod"} {
             write_cfgmem  -force -format mcs -size 32 -interface SPIx1 -loadbit [list up 0x00000000 bitstreams/${design_name}_${buildVersion}.bit  ] -file bitstreams/${design_name}_${buildVersion}.mcs
        } else {
             write_cfgmem  -force -format mcs -size 32 -interface SPIx4 -loadbit [list up 0x00000000 bitstreams/${design_name}_${buildVersion}.bit  ] -file bitstreams/${design_name}_${buildVersion}.mcs
        }
       close_project
    }

    
}

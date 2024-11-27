
## This script should be sourced from a main caller script that drives the flow
#package unknown icSearchFlow
source [file dirname [info script]]/helpers.tcl
lappend auto_path [file dirname [info script]]
package require icflow 

## Create reload function to reload calling script
icInfo "Running in tool $tool"
#set frameCount [info frame]
#for {set i 0} {$i < $frameCount} {incr i} {
#    puts "-> -$î: [info frame -$i]"
#}
#puts "[info frame]"

if {$tool == "genus"} {
     set ::mainScript $::rc::cdn_init_file
} else {

    if {$tool == "innovus"} {
        set mainFrame [info frame -4]
    } else {
        set mainFrame [info frame -1]
    } 
    set ::mainScript [dict get $mainFrame file]
} 

set mainFolder [file dirname $mainScript]

icInfo "Main script $::mainScript"
proc icf_reload args {
    icReload $::mainScript
}
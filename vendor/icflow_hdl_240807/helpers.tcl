
## Determine tool
#########

## Determine exe
set ::tool [lindex [split [info nameofexecutable] /] end]
set ::icScriptFolder ""

proc sourceFile fl {
    foreach f $fl {
        set exe [info nameofexecutable]
        set scriptFolderbackup $::icScriptFolder
        set ::icScriptFolder [file dirname $f]
        try {
            puts "\[ICF\] Sourcing script $f (exe: $exe)"
            if {[string match *tclsh* $exe]} {
                uplevel #0 [list source $f ]
            } else {
                uplevel #0 [list source -quiet $f]
                #uplevel #0 [list source -quiet $f ]
            }
        } finally {
            set ::icScriptFolder $scriptFolderbackup
        }
    }
}

proc icSource f {
    sourceFile $::env(ICFLOW_HOME)/$f
}

proc icSourcePath f { 
    return $::env(ICFLOW_HOME)/$f
}

proc icSourceFlow {name version} {

   
    set searchVersion v[string map {. _} $version]
    set searchName flow_[string map {. _} $name]
    set shortName  $name
    set searchPath [file normalize $::icflowFolder/../$searchName/$searchVersion/$shortName.$searchVersion.tcl]
    icInfo "Trying to autoload a flow from $searchPath"
    if {[file exists $searchPath]} {
        icInfo "- Found"
        package provide $name $version 
        sourceFile $searchPath
    }

   
}
proc icSearchFlow {name version} {
    sourceFile $::env(ICFLOW_HOME)/common_icflow_v1/icflow.common.tcl
    package require icflow 1.0 
    icInfo "Could not find package $name $version"
    if {[string match flow.* $name]} {
        set searchVersion v[string map {. _} $version]
        set searchName [string map {. _} $name]
        set shortName  [string map {flow_ ""} $searchName]
        set searchPath [file normalize $::icflowFolder/../$searchName/$searchVersion/$shortName.$searchVersion.tcl]
        icInfo "Trying to autoload a flow from $searchPath"
        if {[file exists $searchPath]} {
            icInfo "- Found"
            package provide $name $version 
            sourceFile $searchPath
        }

    }
}

proc icSourceScripts {glob args} {
    set args [icflow::args::toDict $args]
    if {[icflow::args::contains $args -workdir]} {
        set base [pwd]
    } elseif {[icflow::args::contains $args -maindir]} {
        set base [file dirname $::IC_MAIN_SCRIPT]
    } else {
        set base [file dirname [info script]]
    }
    puts "Sourcing from: $base, args=$args"
    foreach f [lsort [glob -nocomplain -directory $base $glob]] {
        sourceFile $f
    }
}
set pkgName    icflow
set pkgVersion 1.0
package provide $pkgName $pkgVersion
catch {package require term::ansi::send}

#package unknown ::icSearchFlow

#set script [file normalize  [uplevel #0 info script]]
#puts "Caller script 2 $script" 
set ::icflowFolder [file normalize [file dirname [info script]]]
set ::PWD $::env(PWD)
if {[llength [array names ::env BASE]]>0} {
    set ::BASE $::env(BASE)
}

## Utilities
###############
proc repeat {count script} {
    for {set i 0} {$i < $count} {incr i} {
        uplevel [list set i $i]
        uplevel $script
    }
}

## Base
###############
proc icReload file {
    icForget
    source -quiet $file
    return ""
    #uplevel #0 [list ::source -quiet $file]
}

proc icf_reload args {
    icInfo "Main script $::IC_MAIN_SCRIPT"
    icReload $::IC_MAIN_SCRIPT
}

proc icForget args {
    foreach n [lsearch -all -inline -glob [package names] icflow* ] {
        icInfo "Forgetting package $n for reload"
        package forget $n
    }
    foreach v [uplevel #0 {info vars ::IC_*}] {
        icInfo "Forgetting parameter $v" 
        unset $v
    }
}

## Parameters
############
set ::icflow_params [dict create]



proc icDefineParameter {name description args} {
    icInfo "Defined Parameter for Flow: $name,description=$description,default=$args"
    dict append ::icflow_params $name [list $description {*}$args ]
    # {*}$args
    if {[catch [list set ::$name] ]} {
        if {$args!=""} {
            set ::$name {*}$args
        } else {
           # icCheckEnvVariables $name -quiet
        }
        # Always check env variables for overwrites
        icCheckEnvVariables $name -quiet
    }
      
}

proc icCheckParameters args {
    icCheckParametersFromGlobalVariables
}
proc icCheckParametersFromGlobalVariables args {

    dict for {paramName spec} $::icflow_params {
        icFine "Checking parameter $paramName"
        icCheckGVariable $paramName
    } 
    
}

## Won't override existing values
proc icSetParameter {name value args} {
    if {[catch [list set ::$name] ]} {
        set ::$name $value
    }
   
}

proc icIsParameterSet {name} {
    if {[catch [list set ::$name]]} {
        return false
    } else {
        return true 
    }
   
}

## Standard definition of methods for the Steps
#########
set ::icflow_steps [dict create]

proc icDefineStep {step doc} {

    ## Step can be a list with the first element being the base name and the other the actual sub-sets
    if {[llength $step]>1} {
        set stepName [lindex $step 0]
        set stepList [lmap currentStepName [lrange $step 1 end] {  string cat "$stepName.$currentStepName" } ]
    } else {
        set stepName $step
        set stepList [list $stepName]
    }

    dict append ::icflow_steps $stepName.pre   {}
    foreach currentStep $stepList {
        dict append ::icflow_steps $currentStep       {}
    }
    dict append ::icflow_steps $stepName.post  {}
    dict append ::icflow_steps doc.$stepName   [list $doc]
    icInfo "Defined step $stepName with steps $stepList $doc"
}
proc icApply {step script} {

    icFine "Loading script for step $step"
    dict lappend ::icflow_steps $step $script
}

## Run
###########
set ::icflow_running 0
proc icRun {globs args} {
    incr ::icflow_running
    try {
        foreach glob $globs {

        
            set stepsToRun [dict filter ${::icflow_steps} key $glob*]
            set i 0 
    
            if {[llength $stepsToRun]==0} {
                icWarn "Cannot find any step(s) matching $glob"
            }
            dict for {k v} $stepsToRun {
                #icInfo "Going to run $k (size=[llength $v])"
                if {[llength $v]>0} {
                    icInfo "Running $k with [llength $v] script(s)"
                    icCheckResetErrors

                    ## Prepare a report output folder 
                    set reportFolder icflow/reports/$k 
                    exec mkdir -p $reportFolder

                    ## Run 
                    if {${::icflow_running}==1} {
                        puts "============================================================"
                        puts "========== BEGIN: $i-$k =============================="
                        puts "============================================================"
                        flush stdout
                    }
                    
                    try {
                        foreach s $v {
                            ## Run script
                            eval $s

                            ## Stop here if we have some errors
                            if {[icCheckHasErrors]} {
                                icWarn "Some errors were detected, stopping script here"
                                throw BREAK "Some errors were detected, stopping script here"
                            }
                        }
                    } trap {*} {} {
                        puts "ERROR during run"
                    } finally {

                        if {${::icflow_running}==1} {
                            puts "============================================================"
                            puts "========== END: $i-$k, errors=$::icflow_errCount =============================="
                            puts "============================================================"
                        }
                        icCheckResetErrors
                    }
                    incr i
                    
                    
                }
            }
        }
    } finally {
        incr ::icflow_running -1
    }

    

}

## Generate Flow
#############

proc icFlowStepsToMethods args {

    set result {}
    set i 0 
    dict for {k scripts} ${::icflow_steps} {
        set baseName "icflow_${i}_$k"
        if {[llength $scripts]>0} {
            set j 0 
            foreach s $scripts {
                set finalName ${baseName}_$j
                icInfo "Generating Flow function $finalName"
                lappend result [list $finalName $s]
                proc $finalName args $s
                incr j
            }
            incr i 
        }
        
    } 
    return $result

}

proc icFlowStepsToSingleScript file {

    set out [open $file w+]
    puts $out "package require $::pkgName $::pkgVersion"
    puts $out "" 

    ## Parameters
    #############
    set icVars [info vars ::IC*]
    foreach varName $icVars {
        puts $out "set $varName [set ::$varName]"
    }
    puts $out "" 

    ## Flow Methods
    ##########
    set methods [icFlowStepsToMethods]
    foreach method $methods {
        set name    [lindex $method 0]
        set script  [lindex $method 1]

        puts -nonewline $out  "proc $name args {"
        puts -nonewline $out  "$script"
        puts $out  "}"
    }

    #set i 0 
    #dict for {k scripts} ${::icflow_steps} {
    #    set baseName "icflow_${i}_$k"
    #    if {[llength $scripts]>0} {
    #        set j 0 
    #        foreach s $scripts {
    #            set finalName ${baseName}_$j
    #            icInfo "Writing out Flow function $finalName"
    #            puts $out "proc $finalName { $s }"
    #            
    #            incr j
    #        }
    #        incr i 
    #    }
    #    
    #} 
    close $out

}

## Checks 
##############
set ::icflow_errCount 0

proc icCheckGVariable name {
    if {[catch [list set ::$name]]==1} {
        icError "!! Global ::$name does not exist"
    } else {
        set v [set ::$name]
        # (list length=[llength $v], string length=[string length $v],file exists=[file exists $v])
        icInfo  "OK: Global variable $name set to $v"
        foreach checkFile $v {
            if {[string match /* $checkFile] && [file exists $checkFile]==0} {
                icWarn "File $checkFile seems not to exist"
            }
        }
        
    }
}

## Method sets the passed variable name from env variable, if -silent passed, don't warn if not existing
proc icCheckEnvVariables {vars args} {
    foreach v $vars { 
        
        if {[llength [array names ::env -exact $v]]==0} {
            if {[lindex $args end]!="-quiet"} {
                icError "Cannot find Environment variable $v"
                uplevel 1 return
            } else {
                icWarn "WARN: No Environment variable $v presence"
            }
        }  else {
            icInfo "OK: Checking for Environment variable $v presence -> $::env($v)"
            set ::$v $::env($v)
            #uplevel #1 [list set $v $::env($v)]
            #icInfo "\u270C  OK: Environment variable $v was correctly set"
        }
    }
}

## If an Error was logged, this will return true. User should reset the error counter
proc icCheckHasErrors args {
    
    return [expr $::icflow_errCount > 0 ? true : false]
}

proc icCheckResetErrors args {
    set ::icflow_errCount 0 
}
## Utils
## Hex codes for emoji: https://dev.to/rodrigoodhin/list-of-emojis-hex-codes-35ma
#############
set ::icflow_log INFO 

proc icLogSetFINE args {
    set ::icflow_log FINE
}
proc icLogSetINFO args {
    set ::icflow_log INFO 
}
proc withLogFine script {
    icLogSetFINE
    try {
        uplevel $script
    } finally {
        icLogSetINFO
    }
}
proc icLog {level message} {
    puts "\[ICF:$level\] $message"
}
proc isColorTerm args {
    set sendPresent [::catch {package present term::ansi::send}]
    if {$sendPresent} {
        return 0
    } else {
        return 1
    }
}
proc icFatal message {
    try {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgred} }
        icLog FATA $message
        #::exit -1
        error $message  $message
    } finally {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgdefault} }
    }
    
}
proc icError message {
    
    try {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgred} }
        icLog ERRO $message
        incr ::icflow_errCount
    } finally {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgdefault} }
    }
    
}
proc icWarn message {
    try {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgyellow} }
        icLog WARN $message
    } finally {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgdefault} }
    }
    
}
proc icInfo message {

    try {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgcyan} }
        icLog INFO $message
    } finally {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgdefault} }
    }
    
}
proc icFine message {
    if {$::icflow_log == "FINE"} {
        icLog FINE $message
    }   
}
proc icSuccess message {
    try {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fggreen} }
        icLog SUCC $message
    } finally {
        if {[isColorTerm]} { catch {::term::ansi::send::sda_fgdefault} }
    }
    
}



proc icPrintSteps args {
    dict for {k v} ${::icflow_steps} {
        icInfo "IC Flow step: $k with [llength $v] scripts"
    } 
}
proc icDelimiter args {
    puts "##########\[ICF\]##############"
}

proc icIgnoreError script {
    puts ">>>> Please ignore *Error message below if any"
    uplevel 1 $script
    puts "<<<<" 
}

namespace eval icflow {
    namespace eval utils {

        proc icIsDisplayPresent args {
            return [expr [llength [array names ::env DISPLAY]] > 0 ? true : false]
        }

        proc icIsToolPresent name {
            if {[catch [list exec which $name ]]} {
                return false 
            } else {
                return true 
            }
        }

        ## This method replaces all ${VAR} bash-like env variable with the $::env(VAR) TCL syntax
        proc resolveEnvVariable src {

            global env

            set res [regsub -all {\$\{?([A-Z_0-9]*)\}?} $src {$::env(\1)}]

            subst $res
        }

        proc replaceEnvVariable {str vars {suffix /}} {
            #set envValue $::env($var)
            set replaceMap {}
            foreach envName $vars {
                lappend replaceMap   $::env($envName) \$::env($envName)$suffix
            }
            #puts "Replace map $replaceMap"
            set res [string map $replaceMap $str] 
            #puts "Res: $res " 
            return $res
        }

        proc insertEnvVariable {str vars {suffix ""}} {
            #set envValue $::env($var)
            set replaceMap {}
            foreach envName $vars {
                lappend replaceMap   $::env($envName) \$\{$envName\}$suffix
            }
            #puts "Replace map $replaceMap"
            set res [string map $replaceMap $str] 
            #puts "Res: $res " 
            return $res
        }
    }

    namespace eval report {

        proc resetSummaryMD args {

            set out [open icflow_summary.md w+]

            puts $out "# IC Flow Run Summary"
            puts $out ""

            ## Print Parameters
            puts $out "## Initially defined parameters"
            puts $out ""

            puts $out "| Name | Description | Default | Current Value"
            puts $out "|- | - | -  | - |"
            dict for {paramName spec} $::icflow_params {
                if {[catch [list set ::$paramName]]} {
                    set paramValue "!!UNDEFINED!!"
                } else {
                    set paramValue [set ::$paramName]
                }
                puts $out "| $paramName | [lindex $spec 0] | [lindex $spec 1]  | $paramValue"
            }

            ## All Steps
            ##############
            puts $out "## Steps"
            puts $out ""
            
          
            ## Links
            set methods [icFlowStepsToMethods]
            foreach method $methods {
                set name    [lindex $method 0]
                set script  [lindex $method 1]

                puts $out "- \[$name\](#$name)"
                
            }
            puts $out ""

            ## Content
            foreach method $methods {
                set name    [lindex $method 0]
                set script  [lindex $method 1]

                puts $out "### $name" 

                puts $out "~~~~tcl"
                puts $out "$script"
                puts $out "~~~~"
            }


            close $out

        }

        proc summaryToHTML args {

            icInfo "Generating Summary HTML"
            exec pandoc --standalone icflow_summary.md --template $::icflowFolder/reports/pandoc_html_template.html -o icflow_summary.html  >@ stdout 2>@ stdout
            #exec pandoc --standalone icflow_summary.md -o icflow_summary2.html -M document-css=false  >@ stdout 2>@ stdout

        }

    }
}
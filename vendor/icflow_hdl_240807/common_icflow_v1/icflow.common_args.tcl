namespace eval icflow::args  {

    proc toDict arguments {
        set resDict [dict create]
        set lastArg ""
        foreach arg $arguments {
            if {[string match "-*" $arg]} {
                #puts "Setting $arg to true"
                dict append resDict $arg true 
                set lastArg $arg 
            } else {
                #puts "Setting $lastArg to $arg"
                dict set resDict $lastArg  $arg 
                set lastArg "" 
                 
            }
        }

        return $resDict
    }

    ## Contains all
    proc contains {iDict args} {
        set res true 
        foreach search $args {

            if {[llength [dict keys  $iDict $search]]==0} {
                set res false 
                break
            }
        }
        return $res
       
    }
    proc containsNot {iDict args} {
        set res true 
        foreach search $args {
            if {[llength [dict keys  $iDict $search]]>0} {
                set res false 
                break
            }
        }
        return $res
    }

    proc getValue {iDict name default} {
        if {[icflow::args::contains $iDict $name]} {
            return [dict get $iDict $name] 
        } else {
            return $default
        }
    }

}
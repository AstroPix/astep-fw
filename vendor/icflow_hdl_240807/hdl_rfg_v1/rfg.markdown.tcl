package provide icflow::rfg::markdown 1.0
package require icflow::rfg

namespace eval icflow::rfg::markdown {

    proc generate {registerDefs outFile args} {

        ## Markdown base level
        set level [icflow::args::getValue $args -level 1]
        set headerPrefix [join [lrepeat $level #] ""]

        set registerDefs [uplevel [list subst $registerDefs]]

        ## Target File 
        ####################
        set targetFolder [file dirname $outFile]
        file mkdir $targetFolder

        set o [open $outFile w+]
        icflow::generate::writeEmptyLines $o 2
        puts "Generating MD Documentation to $outFile" 

        icflow::generate::writeLine $o "$headerPrefix Register File Reference"
        icflow::generate::writeLine $o ""

        ## Table
        ##########################

        ## Extra columns
        set extraColumns [icflow::args::getValue $args -columns {}]

        icflow::generate::write $o "| Address | Name | Size (bits) | Features | Description "
        foreach {col colOps} $extraColumns {
            icflow::generate::write $o "| [icflow::args::getValue $colOps name -] "
        }
        icflow::generate::writeLine $o "|"

        icflow::generate::write $o "|---------|------|------|-------|-------------"
        foreach {col colOps} $extraColumns {
            icflow::generate::write $o "| ---- "
        }
        icflow::generate::writeLine $o "|"

        set registers [icflow::rfg::registersToDict $registerDefs]
        #puts "Regdef: $registerDefs"
        #puts "Registers for MD: $registers"
        foreach {name opts} $registers {
            #set params [dict get $register parameters]
            #set name   [dict get $register name]

            set doc    [icflow::args::getValue $opts -doc ""]

            
            set registerSize [dict get $opts size]
            set byteCount    [expr ceil($registerSize / 8.0)]
            set partAddress [expr [dict get $opts address] ]


            ## Set Features Information
            set features {}
            if {[icflow::args::contains $opts -fifo_axis_master]} {
                lappend features "AXIS FIFO Master (write)"
            }
            if {[icflow::args::contains $opts -fifo_axis_slave]} {
                lappend features "AXIS FIFO Slave (read)"
            }
            if {[icflow::args::contains $opts -counter]} {
                if {[icflow::args::contains $opts -interrupt]} {
                    lappend features "Counter w/ Interrupt"
                } else {
                    lappend features "Counter w/o Interrupt"
                }
                
            }

            set mdNameLink "\[$name\](#$name)"

            # Default column params
            icflow::generate::write $o "|0x[format %x $partAddress] | $mdNameLink | $registerSize | [join $features ,] | $doc "
            
            # extra columns
            foreach {col colOps} $extraColumns {
                icflow::generate::write $o "| [string map [icflow::args::getValue $colOps map {}] [icflow::args::getValue $opts $col -]]"
            }
            icflow::generate::writeLine $o "|"

            #for {set i 0} {$i < $byteCount} {incr i} {
            #    set partAddress [expr [dict get $register address] + $i  ]
            #    puts "@0x$partAddress    $name, bytes=$byteCount"
            #}
            
        }


        ## Details
        ##########################
        foreach {name opts} $registers {
            #set params          [dict get $register parameters]
            set address         [dict get $opts address]
            #set name            [dict get $register name]
            set registerSize    [dict get $opts size]

            set doc    [icflow::args::getValue $opts -doc ""]
            set bits   [icflow::args::getValue $opts bits {}]

            icflow::generate::writeEmptyLines $o 2

            icflow::generate::writeLine $o "${headerPrefix}# <a id='$name'></a>$name"
            icflow::generate::writeEmptyLines $o 2

            # Basic doc for the register
            icflow::generate::writeLine $o "> $doc"
            icflow::generate::writeEmptyLines $o 2

            ## Address 
            icflow::generate::writeLine $o "**Address**: 0x[format %x $address]"
            icflow::generate::writeEmptyLines $o 2

            ## Reset value
            if {[icflow::args::contains $opts -reset]} {
                icflow::generate::writeLine $o "**Reset Value**: [icflow::args::getValue $opts -reset {}]"
            }
            icflow::generate::writeEmptyLines $o 2

            ## Bits Table
            if {[llength $bits]>0} {

                ## Calculate number of bits used in the register
                set bitsCount 0
                set fieldCount 0
                foreach {bitName bitOpts} $bits {
                    incr bitsCount [icflow::args::getValue $bitOpts -size 1]
                    incr fieldCount
                }
                #set bitsCount  [expr [llength $bits]/2]
                set unusedBits [expr $registerSize - $bitsCount ]
                

                ## Header
                ## Write bits indexes for each bit definition
                icflow::generate::write $o "|"
                if {$unusedBits>0} {
                    icflow::generate::write $o " \[[expr $registerSize-1]:$bitsCount\] |" 
                }

                set bitIndex [expr $registerSize - $unusedBits - 1]
                foreach {bitOpts bitName } [lreverse $bits] {
                    set fieldSize [icflow::args::getValue $bitOpts -size 1]
                    if {$fieldSize==1} {
                        icflow::generate::write $o " $bitIndex |"
                    } else {
                        icflow::generate::write $o " \[$bitIndex:[expr $bitIndex-$fieldSize+1]\] |"
                    }
                    incr bitIndex [expr -$fieldSize]
                    
                }
                #repeat $bitsCount {
                #    icflow::generate::write $o "[expr $bitsCount-$i-1] |" 
                #}
                icflow::generate::writeEmptyLines $o 1

                ## Delimiter
                icflow::generate::write $o "|"
                if {$unusedBits>0} {
                    icflow::generate::write $o " --|" 
                }
                repeat $fieldCount {
                    icflow::generate::write $o "-- |" 
                }
                icflow::generate::writeEmptyLines $o 1

                ## Content
                icflow::generate::write $o "|"
                if {$unusedBits>0} {
                    icflow::generate::write $o " RSVD |" 
                }
                #puts "getting names: $bits (count=$bitsCount,unused=$unusedBits)"
                foreach {bitOpts bitName } [lreverse $bits] {
                    icflow::generate::write $o "$bitName |" 
                }
                #repeat $fieldCount  {
                #    set bitName [lindex $bits [expr $bitsCount *2 - ($i +1)*2]]
                #    icflow::generate::write $o "$bitName |" 
                #}
                icflow::generate::writeEmptyLines $o 2

                ## Bits Documentations
                foreach {bitName bitOpts} $bits {
                    #set bitParameters [icflow::args::getValue $bit parameters {}]
                    icflow::generate::writeLine $o "- $bitName : [icflow::args::getValue $bitOpts -doc -]"
                }

                #icflow::generate::writeLine $o "| Address | Name | Size | Features | Description |" 
            }


        }
        close $o 
        #exit

    }
}

package provide icflow::rfg::markdown 1.0
package require icflow::rfg

namespace eval icflow::rfg::markdown {

    proc generate {registerDefs outFile} {

        ## Target File 
        ####################
        set targetFolder [file dirname $outFile]
        file mkdir $targetFolder

        set o [open $outFile w+]
        icflow::generate::writeEmptyLines $o 2
        puts "Generating MD Documentation to $outFile" 

        icflow::generate::writeLine $o "# Register File Reference"

        ## Table
        ##########################
        icflow::generate::writeLine $o "| Address | Name | Size | Features | Description |" 
        icflow::generate::writeLine $o "|---------|------|------|-------|-------------|"

        set registers [icflow::rfg::registersToDict $registerDefs]
        foreach register $registers {
            set params [dict get $register parameters]
            set name   [dict get $register name]

            set doc    [icflow::args::getValue $params -doc ""]

            set registerSize [dict get $register size]
            set byteCount    [expr ceil($registerSize / 8.0)]
            set partAddress [expr [dict get $register address] ]


            ## Set Features Information
            set features {}
            if {[icflow::args::contains $params -fifo_axis_master]} {
                lappend features "AXIS FIFO Master (write)"
            }
            if {[icflow::args::contains $params -fifo_axis_slave]} {
                lappend features "AXIS FIFO Slave (read)"
            }
            if {[icflow::args::contains $params -counter]} {
                if {[icflow::args::contains $params -interrupt]} {
                    lappend features "Counter w/ Interrupt"
                } else {
                    lappend features "Counter w/o Interrupt"
                }
                
            }

            set mdNameLink "\[$name\](#$name)"

            icflow::generate::writeLine $o "|0x[format %x $partAddress] | $mdNameLink | $registerSize | [join $features ,] | $doc|"
            

            #for {set i 0} {$i < $byteCount} {incr i} {
            #    set partAddress [expr [dict get $register address] + $i  ]
            #    puts "@0x$partAddress    $name, bytes=$byteCount"
            #}
            
        }


        ## Details
        ##########################
        foreach register $registers {
            set params          [dict get $register parameters]
            set address         [dict get $register address]
            set name            [dict get $register name]
            set registerSize    [dict get $register size]

            set doc    [icflow::args::getValue $params -doc ""]
            set bits   [icflow::args::getValue $params -bits {}]

            icflow::generate::writeEmptyLines $o 2

            icflow::generate::writeLine $o "## <a id='$name'></a>$name"
            icflow::generate::writeEmptyLines $o 2

            # Basic doc for the register
            icflow::generate::writeLine $o "> $doc"
            icflow::generate::writeEmptyLines $o 2

            ## Address 
            icflow::generate::writeLine $o "**Address**: 0x[format %x $address]"
            icflow::generate::writeEmptyLines $o 2

            ## Reset value
            if {[icflow::args::contains $params -reset]} {
                icflow::generate::writeLine $o "**Reset Value**: [icflow::args::getValue $params -reset {}]"
            }
            icflow::generate::writeEmptyLines $o 2

            ## Bits Table
            if {[llength $bits]>0} {
                set unusedBits [expr $registerSize - [llength bits] ]
                set bitsCount  [llength $bits]
                ## Header
                icflow::generate::write $o "|\[[expr $registerSize-1]:$bitsCount\] |" 
                repeat $bitsCount {
                    icflow::generate::write $o "[expr $bitsCount-$i-1] |" 
                }
                icflow::generate::writeEmptyLines $o 1

                ## Delimiter
                icflow::generate::write $o "|--|" 
                repeat $bitsCount {
                    icflow::generate::write $o "-- |" 
                }
                icflow::generate::writeEmptyLines $o 1

                ## Content
                icflow::generate::write $o "|RSVD |" 
                repeat $bitsCount {
                    set bit [lindex $bits [expr $bitsCount-$i-1]]
                    icflow::generate::write $o "[icflow::args::getValue $bit name -]|" 
                }
                icflow::generate::writeEmptyLines $o 2

                ## Bits Documentations
                foreach bit $bits {
                    set bitParameters [icflow::args::getValue $bit parameters {}]
                    icflow::generate::writeLine $o "- [icflow::args::getValue $bit name -]: [icflow::args::getValue $bitParameters -doc -]"
                }

                #icflow::generate::writeLine $o "| Address | Name | Size | Features | Description |" 
            }


        }
        close $o 
        #exit

    }
}

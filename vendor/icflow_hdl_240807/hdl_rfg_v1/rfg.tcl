package provide icflow::rfg 1.0
package require icflow


namespace eval icflow::generate  {

    icDefineParameter IC_FSP_OUTPUTS    "Output for Firmware support"   ./fsp
    icDefineParameter IC_RFG_NAME       "Name for RFG module" main_rfg
    icDefineParameter IC_RFG_TARGET     "Top level name for target, Python module named after this parameter"

    variable indent       0
    variable indentString ""

    proc indent args {

        incr icflow::generate::indent
        set icflow::generate::indentString ""
        for {set i 0} {$i < ${icflow::generate::indent}} {incr i} {
            set icflow::generate::indentString "${icflow::generate::indentString}    "
        }
    }

    proc outdent args {
        incr icflow::generate::indent -1
        set icflow::generate::indentString ""
        for {set i 0} {$i < ${icflow::generate::indent}} {incr i} {
            set icflow::generate::indentString "${icflow::generate::indentString}    "
        }
    }

    proc write {out line args} {
        puts -nonewline $out ${icflow::generate::indentString}$line
    }

    proc writeLine {out line args} {
        if {[lsearch $args -outdent]!=-1} {
            outdent
        }
        puts $out ${icflow::generate::indentString}$line
        if {[lsearch $args -indent]!=-1} {
            indent
        }
        if {[lsearch $args -outdent_after]!=-1} {
            outdent
        }

    }

    proc writeEmptyLines {out {count 1}} {

        for {set i 0} {$i < ${count}} {incr i} {
            puts $out "${icflow::generate::indentString}"
        }

    }

    proc writeLines {out lines separator} {
        for {set i 0} {$i < [llength $lines]} {incr i} {
            set line [lindex $lines $i]
            #set line [regsub -expanded -- \|((\w|:)+)\| $line \[\1\]]
            if {$line==""} {
                puts $out ""
            } else {
                if {$i==[llength $lines]-1} {
                 puts $out ${icflow::generate::indentString}$line
                } else  {
                    puts $out ${icflow::generate::indentString}$line$separator
                }
            }


        }
    }

 }

namespace eval icflow::rfg {


    proc registersToDict {registers args} {

        ## Params
        ################

        ## Default size of registers
        set defaultSize [icflow::args::getValue $args -defaultSize 8]


        #puts "Converting $registers"
        #exit
        ## Read registers definitions to a reusable form
        #########
        set dictRegisters {}
        set address 0
        set index 0
        set remaining [expr [llength $registers]/2]
        for {set index 0} { $index < [llength $registers]} {incr index 2} {
        #while {$remaining >= 0 }
            #puts "Remaining now $remaining,index=$index"

            set name [string tolower [lindex $registers $index]]
            set args [lindex $registers [expr $index +1]]
            set args [icflow::args::toDict $args]
            #puts "Register: $name, args:$args"

            #set register [lindex $registers $index]


            set rDict [dict create]
            #set name [string tolower [lindex $register 0]]
            #set args [icflow::args::toDict [lrange $register 1 end]]

            ## Add Fifo read/write sizes
            if {[icflow::args::contains $args -fifo*slave] && [icflow::args::contains $args -read_count]} {
                set registers [linsert $registers [expr $index+2] ${name}_read_size [list  -size 32 -sw_read_only -hw_write -doc "Number of entries in ${name} fifo"]]
                incr remaining 2
            }

            if {[icflow::args::contains $args -fifo*master] && [icflow::args::contains $args -write_count]} {
                set registers [linsert $registers [expr $index+2] ${name}_write_size [list  -size 32 -sw_read_only -hw_write -doc "Number of entries in ${name} fifo"]]
                incr remaining 2
            }



            #dict set rDict name         $name
            #dict set rDict parameters   $args
            dict set rDict address      $address
            #puts "reg args: $args"
            #dict append rDict {*}$args

            ## Parse bits -> parse bits size like a register
            if {[icflow::args::contains $args -bits]} {
                #puts "Found bits for $name -> [dict get $args -bits]"
                set parsedBits [registersToDict [dict get $args -bits] -defaultSize 1]
                #dict set args -bits $parsedBits
                dict set rDict bits $parsedBits
            }

            ## Pass parameters
            set allowedParameters {
                -doc val
                -reset val
                -hw_write bool
                -hw_ignore bool
                -hw_no_local_reg bool
                -sw_read_only bool
                -clock_divider bool
                -fifo_axis_slave bool
                -fifo_axis_master bool
                -with_tlast bool
                -write_count bool
                -counter bool
                -updown bool
                -interrupt bool
                -clear bool
                -enable bool
                -input bool
                -written bool
                -tmr bool
                -size val
            }
            foreach {p type} $allowedParameters {
                if {[icflow::args::contains $args $p]} {
                    if {$type=="val"} {
                        dict set rDict $p [icflow::args::getValue $args $p "-"]
                    } elseif {$type=="bool"} {
                        dict set rDict $p 1
                    }
                }
            }


            set registerSize            [icflow::args::getValue $args -size $defaultSize]
            dict set rDict size         $registerSize

            ## Increment address
            set byteCount       [expr int(ceil($registerSize / 8.0))]
            incr address        $byteCount

            lappend dictRegisters $name $rDict

            ## Special cases
            ###########

            ## Counter with interrupt parameter should add a match register
            if {[icflow::args::contains $args -counter -interrupt]} {
                set regArgs [list -size $registerSize -reset [icflow::args::getValue $args -match_reset 0]]
                lappend registers  ${name}_match $regArgs
                incr remaining
            }

            ## next
            ##########


        }
        #exit
        return $dictRegisters
    }

    proc generate {registers {outputFile ""} args} {

        set registerDefs [uplevel [list subst $registers]]
        puts "Registers base def: $registerDefs"

        ## Target File
        ####################
        if {$outputFile==""} {
            set targetFile ${::IC_RFG_NAME}.sv
        } else {
            set targetFile ${outputFile}
        }
        #set targetFile ${::IC_RFG_NAME}.sv
        set o [open $targetFile w+]
        puts "Generating $targetFile"

        #icflow::generate::writeLine $o "`include \"rfg_axis_ifs.sv\""
        #icflow::generate::writeLine $o "`include \"rfg_types.sv\""
        icflow::generate::writeLine $o "module ${::IC_RFG_NAME}("
        icflow::generate::indent
        icflow::generate::writeLine $o "// IO"

        ## Read registers definitions to a reusable form
        #########
        set dictRegisters [registersToDict $registerDefs]

        ## IO Lines
        ##############
        set ioLines {}

        ## RFG main interface
        lappend ioLines "// RFG R/W Interface"
        lappend ioLines "// --------------------"
        lappend ioLines "input  wire                  clk"
        lappend ioLines "input  wire                  resn"
        lappend ioLines "input  wire  \[15:0\]          rfg_address"
        lappend ioLines "output reg                   rfg_address_valid"
        lappend ioLines "input  wire  \[7:0\]           rfg_write_value"
        lappend ioLines "output reg                   rfg_write_valid"
        lappend ioLines "input  wire                  rfg_write"
        lappend ioLines "input  wire                  rfg_write_last"
        lappend ioLines "input  wire                  rfg_read"
        lappend ioLines "output reg                   rfg_read_valid"
        lappend ioLines "output reg  \[7:0\]            rfg_read_value"
        lappend ioLines ""

        ## I/O for registers
        puts "registers: $dictRegisters"
        foreach {name params} $dictRegisters {

            set size [icflow::args::getValue $params size 8]

            if {[icflow::args::contains $params -fifo_axis_slave]} {

                lappend ioLines "// AXIS Slave interface to read from FIFO ${name}"
                lappend ioLines "// --------------------"
                lappend ioLines "input  wire \[[expr {$size-1}]:0\]            ${name}_s_axis_tdata"
                lappend ioLines "input  wire                  ${name}_s_axis_tvalid"
                lappend ioLines "output wire                  ${name}_s_axis_tready"

            } elseif {[icflow::args::contains $params -fifo_axis_master]} {

                lappend ioLines "// AXIS Master interface to write to FIFO ${name}"
                lappend ioLines "// --------------------"
                lappend ioLines "output logic \[7:0\]             ${name}_m_axis_tdata"
                lappend ioLines "output logic                   ${name}_m_axis_tvalid"
                lappend ioLines "input  wire                  ${name}_m_axis_tready"
                if {[icflow::args::contains $params -with_tlast]} {
                    lappend ioLines "output reg            ${name}_m_axis_tlast"
                }

            } elseif {[icflow::args::contains $params -clock_divider]} {

                lappend ioLines "input  wire            ${name}_source_clk"
                lappend ioLines "input  wire            ${name}_source_resn"
                lappend ioLines "output logic           ${name}_divided_clk"
                lappend ioLines "output wire            ${name}_divided_resn"

            } else {

                ## I/O for software/hardware readonly and write
                if {[icflow::args::contains $params -hw_write]} {
                    lappend ioLines "input  wire \[[expr $size-1]:0\]            $name"
                    if {[icflow::args::containsNot $params -hw_no_local_reg]} {
                        lappend ioLines "input  wire                  ${name}_write"
                    }

                } elseif {[icflow::args::containsNot $params -hw_ignore]} {

                    ## Main Reg output
                    lappend ioLines "output wire \[[expr $size-1]:0\]           $name"

                    ## Single bits
                    if {[icflow::args::contains $params bits]} {
                        #puts "Reg has bits"
                        foreach {bName bOpts} [dict get $params bits] {
                            #puts "Bit: $bit"
                            #set bName   [dict get $bOpts name]
                            #set bParams [dict get $bOpts parameters]
                            set bitSize [dict get $bOpts size]
                            if {$bitSize > 1} {
                                set bitSize " \[[expr $bitSize-1]:0\]"
                            } else {
                                set bitSize ""
                            }
                            if {[icflow::args::contains $bOpts -input]} {
                                lappend ioLines "input  wire$bitSize                  ${name}_$bName"
                            } else {
                                lappend ioLines "output wire$bitSize                  ${name}_$bName"
                            }

                        }
                    }
                }

                ## I/O for special types
                if {[icflow::args::contains $params -counter -interrupt]} {
                    lappend ioLines "output reg                   ${name}_interrupt"
                }
                if {[icflow::args::contains $params -counter -enable]} {
                    lappend ioLines "input  wire                  ${name}_enable"
                }
                if {[icflow::args::contains $params -counter -clear]} {
                    lappend ioLines "input  wire                  ${name}_clear"
                }
                if {[icflow::args::contains $params -written]} {
                    lappend ioLines "output reg                   ${name}_written"
                }




            }
        }
        icflow::generate::writeLines $o $ioLines ","


        icflow::generate::writeLine $o ");"
        icflow::generate::writeEmptyLines $o 2

        ## Internal registers
        #################
        foreach {name params} $dictRegisters {
            #set name   [dict get $register name]
            #set params [dict get $register parameters]
            set size   [dict get $params size]

            ## Clock Divider types
            if {[icflow::args::contains $params -clock_divider]} {
                icflow::generate::writeLine $o "// Clock Divider ${name}"
                icflow::generate::writeLine $o "logic \[7:0\] ${name}_counter;"
                icflow::generate::writeLine $o "logic \[7:0\] ${name}_reg;"
            }

            ## Registers that are written locally
            if {[icflow::args::contains $params -hw_write -sw_read_only] && [icflow::args::containsNot $params -hw_no_local_reg] } {
                icflow::generate::writeLine $o "logic \[[expr $size-1]:0\] ${name}_reg;"
            }

            ## Extra up/down counter
            if {[icflow::args::contains $params -updown -counter]} {
                icflow::generate::writeLine $o "logic ${name}_up;"
            }

        }
        icflow::generate::writeEmptyLines $o 2

        ## Register I/O Assignments
        ################
        icflow::generate::writeLine $o "// Registers I/O assignments"
        icflow::generate::writeLine $o "// ---------------"
        foreach {name params} $dictRegisters {
            #set name   [dict get $register name]
            #set params [dict get $register parameters]
            set size   [dict get $params size]
            if {[icflow::args::containsNot $params -clock_divider -fifo* -hw_write]} {

                icflow::generate::writeLine $o "logic \[[expr $size-1]:0\] ${name}_reg;"

                if {[icflow::args::contains $params -read_clock]} {
                    icflow::generate::writeLine $o "(* ASYNC_REG = \"TRUE\" *) reg \[7:0\] ${name}_reg_target_clock;"
                    icflow::generate::writeLine $o "assign ${name} = ${name}_reg_target_clock;"
                } elseif {[icflow::args::containsNot $params -hw_ignore]}  {
                    icflow::generate::writeLine $o "assign ${name} = ${name}_reg;"
                }
                icflow::generate::writeEmptyLines $o 1
            }


        }
        icflow::generate::writeEmptyLines $o 2

        ## Register bits assignments
        ##############
        icflow::generate::writeLine $o "// Register Bits assignments"
        icflow::generate::writeLine $o "// ---------------"
        foreach {name params} $dictRegisters {

            if {[icflow::args::contains $params bits]} {
                set bi 0
                foreach {bName bParams} [dict get $params bits] {

                    set bitSize [dict get $bParams size]
                    set regIndex $bi
                    if {$bitSize>1} {
                        set regIndex [expr $bi + $bitSize -1]:$bi
                    }
                    incr bi $bitSize
                    if {[icflow::args::containsNot $bParams -input]} {
                        icflow::generate::writeLine $o "assign ${name}_$bName = ${name}_reg\[$regIndex\];"
                    }

                }
            }
        }
        icflow::generate::writeEmptyLines $o 2

        ## TMR Registers
        ######################
        icflow::generate::writeLine $o "// TMR Registers (if any)"
        icflow::generate::writeLine $o "// ---------------"
        foreach {name params} $dictRegisters {
            if {[icflow::args::contains $params -tmr]} {


                icflow::generate::writeLine $o "TMRRegATMR #(.RESET_VAL([icflow::args::getValue $params -reset 'd0])) ${name}_tmr_reg_I  (.clk(clk),.resn(resn),.write_value(rfg_write_value),.write(rfg_write && rfg_address==16'h[format %x [dict get $params address]]),.reg_value_tmr(${name}_reg));"

            }
        }

        icflow::generate::writeLine $o ""

        ## Write Stage
        #####################


        icflow::generate::writeLine $o "// Register Writes"
        icflow::generate::writeLine $o "// ---------------"
        icflow::generate::writeLine $o "always_ff @(posedge clk) begin" -indent


            icflow::generate::writeLine $o "if (!resn) begin" -indent

            icflow::generate::writeLine $o "rfg_write_valid <= 'd0;"


            ## Resets for registers
            ###################
            foreach {name params} $dictRegisters {
                #set name   [dict get $register name]
                #set params [dict get $register parameters]
                if {[icflow::args::contains $params -fifo_axis_master]} {

                    icflow::generate::writeLine $o "${name}_m_axis_tvalid <= 1'b0;"
                    if {[icflow::args::contains $params -with_tlast]} {
                        icflow::generate::writeLine $o "${name}_m_axis_tlast  <= 1'b0;"
                    }

                } elseif {[icflow::args::containsNot $params  -fifo_axis_slave -hw_no_local_reg -tmr]} {
                    ## Plain registers
                    icflow::generate::writeLine $o "${name}_reg <= [icflow::args::getValue $params -reset '0];"
                }

                if {[icflow::args::contains $params -updown -counter]} {
                    icflow::generate::writeLine $o "${name}_up <= 1'b1;"
                }
                if {[icflow::args::contains $params -written]} {
                    icflow::generate::writeLine $o "${name}_written <= 1'b0;"
                }
            }
            icflow::generate::writeLine $o "end else begin" -outdent -indent
                icflow::generate::writeEmptyLines $o 2

                ## Input bits are always sampled
                icflow::generate::writeLine $o "// Single in bits are always sampled"
                foreach {name params} $dictRegisters {
                    #set params [dict get $register parameters]
                    #set name   [dict get $register name]
                    if {[icflow::args::contains $params bits]} {
                        set bi 0
                        foreach {bName bParams} [dict get $params bits] {
                            #set bName [dict get $bit name]
                            #set bParams [dict get $bit parameters]
                            if {[icflow::args::contains $bParams -input]} {
                                icflow::generate::writeLine $o "${name}_reg\[$bi\] <= ${name}_$bName;"
                            }
                            incr bi [icflow::args::getValue $bParams -size 1]
                        }
                    }
                }
                icflow::generate::writeEmptyLines $o 2

                ## Write Case  for registers
                icflow::generate::writeLine $o "// Write for simple registers"
                icflow::generate::writeLine $o "case({rfg_write,rfg_address})" -indent
                    foreach {name params} $dictRegisters {
                        #set params [dict get $register parameters]
                        #set name   [dict get $register name]
                        set address     [dict get $params address]
                        if {[icflow::args::contains $params -clock_divider]} {

                            icflow::generate::writeLine $o "{1'b1,16'h[format %x $address]}: begin" -indent
                                icflow::generate::writeLine $o "${name}_reg <= rfg_write_value;"
                            icflow::generate::writeLine $o "end" -outdent

                        }  elseif {[icflow::args::containsNot $params -fifo* -sw_read_only -tmr]} {
                            ## Standard registers
                            set registerSize [dict get $params size]
                            set byteCount    [expr ceil($registerSize / 8.0)]
                            #puts "base address [dict get $register address]"
                            for {set i 0} {$i < $byteCount} {incr i} {
                                set partAddress [expr $address + $i  ]
                                icflow::generate::writeLine $o "{1'b1,16'h[format %x $partAddress]}: begin" -indent
                                    set lowBit  [expr $i*8]
                                    set highBit [expr $lowBit + [expr $registerSize<8 ? $registerSize - 1 : 7]]
                                    if {$highBit<7} {
                                        icflow::generate::writeLine $o "${name}_reg\[$highBit:$lowBit\] <= rfg_write_value\[$highBit:$lowBit\];"
                                    } else {
                                        icflow::generate::writeLine $o "${name}_reg\[$highBit:$lowBit\] <= rfg_write_value;"
                                    }
                                    icflow::generate::writeLine $o "rfg_write_valid <= 'd1;"

                                icflow::generate::writeLine $o "end" -outdent
                            }

                        }
                    }
                    icflow::generate::writeLine $o "default: begin"
                    icflow::generate::writeLine $o "    rfg_write_valid <= 'd0 ;"
                    icflow::generate::writeLine $o "end"

                icflow::generate::writeLine $o "endcase" -outdent
                icflow::generate::writeLine $o ""

                ## Written Registers
                ## If register is more than 8bits, trigger written for last byte
                foreach {name params} $dictRegisters {

                    if {[icflow::args::contains $params -written]} {
                        set address      [dict get $params address]
                        set registerSize [dict get $params size]
                        set byteCount    [expr int(ceil($registerSize / 8.0))]
                        set lastAddress  [expr $address + ($byteCount -1)  ]
                        icflow::generate::writeLine $o "${name}_written <= rfg_write && rfg_address==16'h[format %x $lastAddress];"
                    }
                }


                ## Write case for FIFO
                icflow::generate::writeLine $o "// Write for FIFO Master"
                foreach {name params} $dictRegisters {
                    #set name        [dict get $register name]
                    set address     [dict get $params address]
                    #set parameters  [dict get $register parameters]

                    if {[icflow::args::contains $params -fifo*master]} {
                        icflow::generate::writeLine $o "if(rfg_write && rfg_address==16'h[format %x $address]) begin" -indent

                            icflow::generate::writeLine $o "${name}_m_axis_tvalid <= 1'b1;"
                            icflow::generate::writeLine $o "${name}_m_axis_tdata  <= rfg_write_value;"
                            if {[icflow::args::contains $params -with_tlast]} {
                                icflow::generate::writeLine $o "${name}_m_axis_tlast  <= rfg_write_last;"
                            }

                        icflow::generate::writeLine $o "end else begin" -outdent -indent

                            icflow::generate::writeLine $o "${name}_m_axis_tvalid <= 1'b0;"
                            if {[icflow::args::contains $params -with_tlast]} {
                                icflow::generate::writeLine $o "${name}_m_axis_tlast  <= 1'b0;"
                            }
                        icflow::generate::writeLine $o "end" -outdent
                    }
                }
                icflow::generate::writeLine $o ""

                ## Write case for HW Write only
                icflow::generate::writeLine $o "// Writes for HW Write only"
                foreach {name params} $dictRegisters {
                    #set params [dict get $register parameters]
                    #set name   [dict get $register name]
                    if {[icflow::args::contains $params -hw_write -sw_read_only] && [icflow::args::containsNot $params -hw_no_local_reg]} {
                        icflow::generate::writeLine $o "if(${name}_write) begin" -indent
                            icflow::generate::writeLine $o "${name}_reg <= ${name} ;"
                        icflow::generate::writeLine $o "end" -outdent
                    }
                }

                ## Write case for counter
                icflow::generate::writeLine $o "// Writes for Counter"
                foreach {name params} $dictRegisters {
                    #set params [dict get $register parameters]
                    #set name   [dict get $register name]
                    set address [dict get $params address]
                    if {[icflow::args::contains $params -counter]} {

                        # Count condition set by this line
                        set countLine "${name}_reg <= ${name}_reg + 1 ;"
                        if {[icflow::args::contains $params -updown]} {
                            set countLine "${name}_reg <= ${name}_up ? ${name}_reg + 'd1 : ${name}_reg - 'd1 ;"
                        }

                        ## If counter is in interrupt with match register, also reset it when match is changed
                        set ifprefix ""
                        if {[icflow::args::contains $params -interrupt]} {
                            set ifprefix "else "
                            set matchRegIndex   [lsearch $dictRegisters  ${name}_match]
                            set matchReg        [lindex $dictRegisters ${matchRegIndex}+1]
                            #puts "dict: $matchReg"
                            #set matchReg [dict get $dictRegisters name ${name}_match]

                            ## IF counter has clear option, also reset
                            set ifArgs "(rfg_write && rfg_address==16'h[format %x [dict get $matchReg address]])"
                            if {[icflow::args::contains $params -clear]} {
                                #set ifArgs "${ifArgs} || ${name}_clear"
                            }

                            icflow::generate::writeLine $o "// Counter with interrupt on matching register: If the match register is written, reset the counter"
                            icflow::generate::writeLine $o "if($ifArgs) begin" -indent
                                icflow::generate::writeLine $o "${name}_reg <= 'd0;"
                            icflow::generate::writeLine $o "end" -outdent
                        }

                        ## Counter Clear if case
                        if {[icflow::args::contains $params -clear]} {
                            icflow::generate::writeLine $o "${ifprefix}if(${name}_clear) begin" -indent
                                icflow::generate::writeLine $o "${name}_reg <= 'd0;"
                            icflow::generate::writeLine $o "end" -outdent
                            set ifprefix "else "
                        }

                        if {[icflow::args::contains $params -sw_read_only -enable]} {
                             ## SW Readonlu and enable -> count on enable
                            icflow::generate::writeLine $o "${ifprefix}if(${name}_enable) begin" -indent
                                icflow::generate::writeLine $o $countLine
                            icflow::generate::writeLine $o "end" -outdent
                        } elseif {[icflow::args::containsNot $params -sw_read_only] && [icflow::args::contains $params -enable]} {

                            ## SW Write allowed and enable -> count on enable and not write
                            icflow::generate::writeLine $o "${ifprefix}if(!(rfg_write && rfg_address==16'h[format %x $address]) && ${name}_enable) begin" -indent
                                icflow::generate::writeLine $o $countLine
                            icflow::generate::writeLine $o "end" -outdent

                        } elseif {[icflow::args::containsNot $params -sw_read_only]} {

                            ## SW Write and no other options, always count
                            icflow::generate::writeLine $o "${ifprefix}if(!(rfg_write && rfg_address==16'h[format %x $address])) begin" -indent
                                icflow::generate::writeLine $o $countLine
                            icflow::generate::writeLine $o "end" -outdent
                            icflow::generate::writeLine $o ""
                        }


                        ## Match Counter for Interrupt of main counter
                        if {[icflow::args::contains $params -interrupt]} {

                            icflow::generate::writeLine $o "// Counter with interrupt on matching register: Enable counting when match counter is reached, and set up-down to change counting direction"
                            set matchCondition "${name}_reg == (${name}_match_reg - 1)"
                            if {[icflow::args::contains $params -updown]} {
                                set matchCondition "( (${name}_up && ${matchCondition}) || (!${name}_up && ${name}_reg==1 ))"
                            }
                            set enableCondition ""
                            if {[icflow::args::contains $params -enable]} {
                                set enableCondition "&& ${name}_enable"
                            }
                            icflow::generate::writeLine $o "if($matchCondition $enableCondition) begin" -indent
                                icflow::generate::writeLine $o "${name}_interrupt <= 1'b1;"
                                if {[icflow::args::contains $params -updown]} {
                                icflow::generate::writeLine $o "${name}_up <= !${name}_up;"
                                }
                            icflow::generate::writeLine $o "end else begin" -indent -outdent
                                icflow::generate::writeLine $o "${name}_interrupt <= 1'b0;"
                            icflow::generate::writeLine $o "end" -outdent
                            icflow::generate::writeLine $o ""

                        }
                    }
                }


            icflow::generate::writeLine $o "end" -outdent


        icflow::generate::writeLine $o "end" -outdent
        icflow::generate::writeEmptyLines $o 2


        ## Read Stage
        #####################

        #### Read ready case for FIFO
        #### If the fifo size is not 8 bit, read first parts of the fifo bus, then only when all read we can assert ready to get the next word
        ################
        icflow::generate::writeLine $o "// Read for FIFO Slave"
        icflow::generate::writeLine $o "// ---------------"
        foreach {name params} $dictRegisters {

             if {[icflow::args::contains $params -fifo*slave]} {
                set address [dict get $params address]
                set fifoWidth [icflow::args::getValue $params size 8]

                ## Part Read
                if {$fifoWidth>8} {

                    icflow::generate::writeLine $o "//--- FIFO asymetric read for ${name}"

                    set numberOfSegments [expr int(ceil($fifoWidth/8.0))]
                    set counterSize [expr int(ceil(  log10($numberOfSegments)/log10(2) ) )]
                    set partReadCounterName ${name}_partread_counter
                    set partReadMemName     ${name}_partread_mem

                    icflow::generate::writeLine $o "reg \[[expr $counterSize-1]:0\] ${partReadCounterName};"
                    icflow::generate::writeLine $o "reg \[7:0\] ${partReadMemName}\[[expr $numberOfSegments-1]\];"

                    icflow::generate::writeLine $o "wire ${name}_read_valid = rfg_read && rfg_address==16'h[format %x $address] ; // A read to this fifo is requested in the current cycle"

                    icflow::generate::writeLine $o "assign ${name}_s_axis_tready = ${name}_read_valid && ${partReadCounterName}=='d[expr int(pow(2,$counterSize)-1)];"

                    icflow::generate::writeLine $o "always_ff@(posedge clk) begin" -indent
                        icflow::generate::writeLine $o "if (!resn) begin" -indent
                            icflow::generate::writeLine $o "${partReadCounterName} <= 'd0;"
                        icflow::generate::writeLine $o "end else begin" -outdent -indent

                            icflow::generate::writeLine $o "// On each read, increment counter to select next bus part, reset to 0 when number of segments reached"
                            icflow::generate::writeLine $o "${partReadCounterName} <= ${name}_read_valid ? ( ${partReadCounterName} == 'd[expr $numberOfSegments-1] ? 'd0 : ${partReadCounterName} + 'd1) : ${partReadCounterName};"

                        icflow::generate::writeLine $o "end" -outdent
                    icflow::generate::writeLine $o "end" -outdent

                    icflow::generate::writeEmptyLines $o 1

                    icflow::generate::writeLine $o "always_ff@(posedge clk) begin" -indent

                        icflow::generate::writeLine $o "if (${partReadCounterName}=='d0 && ${name}_read_valid) begin" -indent
                            for {set pi 0} {$pi < [expr {$numberOfSegments-1}]} {incr pi} {
                                icflow::generate::writeLine $o "${partReadMemName}\[$pi\] <= ${name}_s_axis_tvalid ? ${name}_s_axis_tdata\[[expr {15+$pi*8}]:[expr {8+$pi*8}]\] : 8'hff;"
                            }

                        icflow::generate::writeLine $o "end" -outdent
                    icflow::generate::writeLine $o "end" -outdent

                } else {
                    icflow::generate::writeLine $o "assign ${name}_s_axis_tready = rfg_read && rfg_address==16'h[format %x $address];"
                }

            }
        }
        icflow::generate::writeEmptyLines $o 2

        icflow::generate::writeLine $o "// Register Read"
        icflow::generate::writeLine $o "// ---------------"
        icflow::generate::writeLine $o "always_ff@(posedge clk) begin" -indent


            icflow::generate::writeLine $o "if (!resn) begin" -indent
                icflow::generate::writeLine $o "rfg_read_valid <= 0;"
                icflow::generate::writeLine $o "rfg_read_value <= 0;"
            icflow::generate::writeLine $o "end else begin" -outdent -indent

                ## Read Case  for registers
                icflow::generate::writeLine $o "// Read for simple registers"
                icflow::generate::writeLine $o "case({rfg_read,rfg_address})" -indent
                    foreach {name params} $dictRegisters {
                        #set params [dict get $register parameters]
                        #set name   [dict get $register name]
                        set address [dict get $params address]
                        #if {[icflow::args::contains $params -clock_divider]} {

                         #   icflow::generate::writeLine $o "{1'b1,16'h[dict get $register address]}: begin" -indent
                         #       icflow::generate::writeLine $o "rfg_read_value <= ${name}_reg ;"
                         #       icflow::generate::writeLine $o "rfg_read_valid <= 1 ;"
                         #   icflow::generate::writeLine $o "end" -outdent

                        #} else
                        #if {![icflow::args::contains $params -fifo*]} {
                        #    icflow::generate::writeLine $o "{1'b1,16'h[dict get $register address]}: begin" -indent
                        #        icflow::generate::writeLine $o "rfg_read_value <= ${name}_reg;"
                        #        icflow::generate::writeLine $o "rfg_read_valid <= 1 ;"
                        #    icflow::generate::writeLine $o "end" -outdent
                        #}  else
                        if {[icflow::args::contains $params -fifo*slave]} {

                            set fifoWidth [icflow::args::getValue $params size 8]

                            icflow::generate::writeLine $o "{1'b1,16'h[format %x $address]}: begin" -indent

                                set partReadCounterName ${name}_partread_counter
                                set partReadMemName     ${name}_partread_mem

                                if {$fifoWidth>8} {
                                    icflow::generate::writeLine $o "rfg_read_value <= ${partReadCounterName} == 'd0 ? (${name}_s_axis_tvalid ? ${name}_s_axis_tdata\[7:0\] : 16'hff) : ${partReadMemName}\[${partReadCounterName}-1\] ;"
                                } else {
                                    icflow::generate::writeLine $o "rfg_read_value <= ${name}_s_axis_tvalid ? ${name}_s_axis_tdata : 16'hff;"
                                }

                                icflow::generate::writeLine $o "rfg_read_valid <= 1 ;"
                            icflow::generate::writeLine $o "end" -outdent
                        } elseif {[icflow::args::containsNot $params -fifo*master]} {
                            ## Standard registers
                            set registerSize [dict get $params size]
                            set byteCount    [expr ceil($registerSize / 8.0 )]
                            #puts "base address [dict get $register address]"
                            for {set i 0} {$i < $byteCount} {incr i} {
                                set partAddress [expr [dict get $params address] + $i  ]
                                icflow::generate::writeLine $o "{1'b1,16'h[format %x $partAddress]}: begin" -indent
                                    set lowBit  [expr $i*8]
                                    set highBit [expr $lowBit +7 > $registerSize - 1 ? $registerSize - 1 : $lowBit +7  ]

                                    set regName ${name}_reg
                                    if {[icflow::args::contains $params -hw_no_local_reg]} {
                                        set regName ${name}
                                    }

                                    # First case: Normal 8 bit read
                                    # Second case, source register has not enough bits, concatenate 0
                                    if {$lowBit +7 > $registerSize - 1} {
                                        icflow::generate::writeLine $o "rfg_read_value <= {[expr int( ($byteCount*8 - $registerSize))]'d0,${regName}\[$highBit:$lowBit\]};"
                                    } else {
                                        icflow::generate::writeLine $o "rfg_read_value <= ${regName}\[$highBit:$lowBit\];"
                                    }

                                    icflow::generate::writeLine $o "rfg_read_valid <= 1 ;"

                                icflow::generate::writeLine $o "end" -outdent
                            }
                        }


                    }
                    icflow::generate::writeLine $o "default: begin"
                        icflow::generate::writeLine $o "    rfg_read_valid <= 0 ;"
                    icflow::generate::writeLine $o "end"

                icflow::generate::writeLine $o "endcase" -outdent
                icflow::generate::writeLine $o ""

            icflow::generate::writeLine $o "end" -outdent


        icflow::generate::writeLine $o "end" -outdent
        icflow::generate::writeEmptyLines $o 2

        ## Clock Divider
        ################
        foreach {name params} $dictRegisters {
            #set name   [dict get $register name]
            #set params [dict get $register parameters]
            if {[icflow::args::contains $params -clock_divider]} {


                icflow::generate::writeLine $o "always_ff@(posedge ${name}_source_clk) begin" -indent
                    icflow::generate::writeLine $o "if (!${name}_source_resn) begin" -indent

                        icflow::generate::writeLine $o "${name}_divided_clk <= 1'b0;"
                        icflow::generate::writeLine $o "${name}_counter <= 16'h00;"


                    icflow::generate::writeLine $o "end else begin" -indent -outdent

                       # icflow::generate::writeLine $o "${name}_divided_resn <= 1'b1;"

                        icflow::generate::writeLine $o "if (${name}_counter==${name}_reg) begin" -indent
                            icflow::generate::writeLine $o "${name}_divided_clk <= !${name}_divided_clk;"
                            icflow::generate::writeLine $o "${name}_counter <= 16'h00;"

                        icflow::generate::writeLine $o "end else begin" -indent -outdent
                            icflow::generate::writeLine $o "${name}_counter <= ${name}_counter+1;"


                        icflow::generate::writeLine $o "end" -outdent


                    icflow::generate::writeLine $o "end" -outdent

                icflow::generate::writeLine $o "end" -outdent

                ## Sync bloc for reset -> Make it long so that IP blocks like fifo are always properly reset
                set resetEdge ""
                if {[icflow::args::contains $params -async_reset]} {
                    set resetEdge " or negedge ${name}_source_resn"
                }
                icflow::generate::writeLine $o "reg \[7:0\] ${name}_divided_resn_delay;"
                icflow::generate::writeLine $o "assign ${name}_divided_resn = ${name}_divided_resn_delay\[7\];"
                icflow::generate::writeLine $o "always_ff@(posedge ${name}_divided_clk$resetEdge or negedge ${name}_source_resn) begin" -indent
                    icflow::generate::writeLine $o "if (!${name}_source_resn) begin" -indent
                        icflow::generate::writeLine $o "${name}_divided_resn_delay <= 16'h00;"
                    icflow::generate::writeLine $o "end else begin" -indent -outdent
                        icflow::generate::writeLine $o "${name}_divided_resn_delay <= {${name}_divided_resn_delay\[6:0\],1'b1};"
                    icflow::generate::writeLine $o "end" -outdent
                icflow::generate::writeLine $o "end" -outdent
                icflow::generate::writeEmptyLines $o 2

            }
        }

        ## Registers to be synched in another clock domain
        #################
        foreach {name params} $dictRegisters {
            #set name   [dict get $register name]
            #set params [dict get $register parameters]

            if {[icflow::args::contains $params -read_clock]} {
                set targetClock [dict get $params -read_clock]
                icflow::generate::writeLine $o "// Synchronisation of $name into read clock domain"
                icflow::generate::writeLine $o "always_ff@(posedge ${targetClock}_clk) begin" -indent
                    icflow::generate::writeLine $o "if (!${targetClock}_resn) begin" -indent
                        icflow::generate::writeLine $o "${name}_reg_target_clock <= 16'h00;"
                    icflow::generate::writeLine $o "end else begin" -indent -outdent
                        icflow::generate::writeLine $o "${name}_reg_target_clock <= ${name}_reg;"
                    icflow::generate::writeLine $o "end" -outdent
                icflow::generate::writeLine $o "end" -outdent
                icflow::generate::writeEmptyLines $o 2
            }

        }


        ## Address valid
        #####################

        ## Calculate last address
        set lastRegParams [lindex $dictRegisters end]
        set lastAddress   [dict get $lastRegParams address]
        set registerSize  [dict get $lastRegParams size]
        set byteCount     [expr ceil($registerSize / 8.0 )]
        set lastAddress   [expr int($lastAddress + $byteCount -1)]

        icflow::generate::writeEmptyLines $o 2
        icflow::generate::writeLine $o "// Simple Address valid bit out"
        icflow::generate::writeLine $o "always_ff@(posedge clk) begin" -indent
            icflow::generate::writeLine $o "if (!resn) begin" -indent
                icflow::generate::writeLine $o "rfg_address_valid <= 'd0;"
            icflow::generate::writeLine $o "end else begin" -indent -outdent
                icflow::generate::writeLine $o "rfg_address_valid <= rfg_address >= 'd0 && rfg_address <= 'h[format %x $lastAddress];"
            icflow::generate::writeLine $o "end" -outdent
        icflow::generate::writeLine $o "end" -outdent
        icflow::generate::writeEmptyLines $o 2


        ## End of module
        icflow::generate::outdent
        icflow::generate::writeLine $o "endmodule"


        close $o

        ## Wrapper
        ####################

    }


    proc generateSVPackage {registersDefs {targetFolder .}} {

        #puts "gen sv: $registersDefs"
        set registers [uplevel [list subst $registersDefs]]


        ## Target File
        ####################
        set targetFile $targetFolder/${::IC_RFG_NAME}_pkg.sv
        set o [open $targetFile w+]
        puts "Generating $targetFile"

        ## Parse registers
        ##########
        set registers [registersToDict $registers]


        ## Write
        ################
        set packageName [string tolower ${::IC_RFG_NAME}]_pkg
        set ifdefName   [string toupper $packageName]
        icflow::generate::writeLine $o "`ifndef $ifdefName"
            icflow::generate::writeLine $o "`define $ifdefName"
            icflow::generate::writeLine $o "package ${packageName};" -indent

            icflow::generate::writeLine $o "enum logic \[15:0\] {"
            set enumLines {}
            foreach {name params} $registers {
                #set name [dict get $register name]
                set addr [dict get $params address]
                lappend enumLines "[string toupper $name] = 16'h[format %x $addr]"
            }
            icflow::generate::writeLines $o $enumLines ,

            icflow::generate::writeLine $o "} addresses;"

        icflow::generate::writeLine $o "endpackage" -outdent
        icflow::generate::writeLine $o "`endif"

    }




}

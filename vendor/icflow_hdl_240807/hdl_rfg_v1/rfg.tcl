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


    proc registersToDict registers {

        #puts "Converting $registers"
        #exit
        ## Read registers definitions to a reusable form
        #########
        set dictRegisters {}
        set address 0
        set index 0
        set remaining [llength $registers]
        for {set index 0} { $index < [llength $registers]} {incr index} {
        #while {$remaining >= 0 } 
            #puts "Remaining now $remaining,index=$index"
            set register [lindex $registers $index]


            set rDict [dict create]
            set name [string tolower [lindex $register 0]]
            set args [icflow::args::toDict [lrange $register 1 end]]

            ## Add Fifo read/write sizes
            if {[icflow::args::contains $args -fifo*slave] && [icflow::args::contains $args -read_count]} {
                set registers [linsert $registers [expr $index+1] [list ${name}_read_size -size 32 -sw_read_only -hw_write -doc "Number of entries in ${name} fifo"]]
                incr remaining 1
            } 

            if {[icflow::args::contains $args -fifo*master] && [icflow::args::contains $args -write_count]} {
                set registers [linsert $registers [expr $index+1] [list ${name}_write_size -size 32 -sw_read_only -hw_write -doc "Number of entries in ${name} fifo"]]
                incr remaining 1
            }    

            ## Parse bits 
            if {[icflow::args::contains $args -bits]} {
                #puts "Found bits for $name -> [dict get $args -bits]"
                set parsedBits [registersToDict [dict get $args -bits]]
                dict set args -bits $parsedBits
            }


            dict set rDict name         $name
            dict set rDict parameters   $args
            dict set rDict address      $address 

            set registerSize            [icflow::args::getValue $args -size 8]
            dict set rDict size         $registerSize

            ## Increment address
            set byteCount       [expr int(ceil($registerSize / 8.0))]
            incr address        $byteCount
  
            lappend dictRegisters $rDict

            ## Special cases
            ###########

            ## Counter with interrupt parameter should add a match register
            if {[icflow::args::contains $args -counter -interrupt]} {
                set regArgs [list -size $registerSize -reset [icflow::args::getValue $args -match_reset 0]]
                lappend registers [concat ${name}_match $regArgs]
                incr remaining
            }

            ## next
            ##########
            

        }
        #exit
        return $dictRegisters
    }

    proc generate {registers {outputFile ""}} {

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
        set dictRegisters [registersToDict $registers]

        ## IO Lines
        ##############
        set ioLines {}

        ## RFG main interface
        lappend ioLines "// RFG R/W Interface"
        lappend ioLines "// --------------------"
        lappend ioLines "input  wire                clk"
        lappend ioLines "input  wire                resn"
        lappend ioLines "input  wire  \[7:0\]         rfg_address"
        lappend ioLines "input  wire  \[7:0\]         rfg_write_value"
        lappend ioLines "input  wire                rfg_write"
        lappend ioLines "input  wire                rfg_write_last"
        lappend ioLines "input  wire                rfg_read"
        lappend ioLines "output reg                 rfg_read_valid"
        lappend ioLines "output reg  \[7:0\]          rfg_read_value"
        lappend ioLines ""

        ## I/O for registers
        foreach register $dictRegisters {
            set name   [dict get $register name]
            set params [dict get $register parameters]
            if {[icflow::args::contains $params -fifo_axis_slave]} {
                lappend ioLines "// AXIS Slave interface to read from FIFO ${name}"
                lappend ioLines "// --------------------"
                lappend ioLines "input  wire \[7:0\]            ${name}_s_axis_tdata"
                lappend ioLines "input  wire                  ${name}_s_axis_tvalid"
                lappend ioLines "output wire                  ${name}_s_axis_tready"
                #lappend ioLines "input  wire                    ${name}_s_axis_tlast"
                #lappend ioLines "input  wire \[7:0\]            ${name}_s_axis_tid"
                #lappend ioLines "input  wire \[7:0\]            ${name}_s_axis_tdest"
                #lappend ioLines "input  wire \[0:0\]            ${name}_s_axis_tuser"
                #lappend ioLines "input  wire \[31:0\]           ${name}_read_count"
                #lappend ioLines "input  wire                    ${name}_almost_empty"
                #lappend ioLines "input  wire                    ${name}_almost_full"
                #lappend ioLines ""
            } elseif {[icflow::args::contains $params -fifo_axis_master]} {
                lappend ioLines "// AXIS Master interface to write to FIFO ${name}"
                lappend ioLines "// --------------------"
                lappend ioLines "output reg \[7:0\]             ${name}_m_axis_tdata"
                lappend ioLines "output reg                   ${name}_m_axis_tvalid"
                lappend ioLines "input  wire                  ${name}_m_axis_tready"
                if {[icflow::args::contains $params -with_tlast]} {
                    lappend ioLines "output reg            ${name}_m_axis_tlast"
                }
                #lappend ioLines "output wire            ${name}_m_axis_tlast"
                #lappend ioLines "output wire \[7:0\]            ${name}_m_axis_tid"
                #lappend ioLines "output wire \[7:0\]            ${name}_m_axis_tdest"
                #lappend ioLines "output wire \[0:0\]            ${name}_m_axis_tuser"
                #lappend ioLines "input  wire            ${name}_almost_empty"
                #lappend ioLines "input  wire            ${name}_almost_full"
                #lappend ioLines ""
            } elseif {[icflow::args::contains $params -clock_divider]} {
                
                lappend ioLines "input  wire            ${name}_source_clk"
                lappend ioLines "input  wire            ${name}_source_resn"
                lappend ioLines "output reg             ${name}_divided_clk"
                lappend ioLines "output wire            ${name}_divided_resn"

            } else {

                ## I/O for software/hardware readonly and write
                set size [icflow::args::getValue $params -size 8]
                if {[icflow::args::contains $params -hw_write]} {
                    lappend ioLines "input  wire \[[expr $size-1]:0\]            $name"
                    lappend ioLines "input  wire                  ${name}_write"
                } elseif {![icflow::args::contains $params -hw_ignore]} {
                    lappend ioLines "output wire \[[expr $size-1]:0\]            $name"
                        if {[icflow::args::contains $params -bits]} {
                        #puts "Reg has bits"
                        foreach bit [dict get $params -bits] {
                            #puts "Bit: $bit"
                            set bName   [dict get $bit name]
                            set bParams [dict get $bit parameters]
                            if {[icflow::args::contains $bParams -input]} {
                                lappend ioLines "input  wire                  ${name}_$bName"
                            } else {
                                lappend ioLines "output wire                  ${name}_$bName"
                            }
                            
                        }
                    } 
                } 

                ## I/O for special types
                if {[icflow::args::contains $params -counter -interrupt]} {
                    lappend ioLines "output  reg                  ${name}_interrupt"
                }
                if {[icflow::args::contains $params -counter -enable]} {
                    lappend ioLines "input   wire                  ${name}_enable"
                }

                
                

            }
        }
        icflow::generate::writeLines $o $ioLines ","
        

        icflow::generate::writeLine $o ");"
        icflow::generate::writeEmptyLines $o 2

        ## Internal registers
        #################
        foreach register $dictRegisters {
            set name   [dict get $register name]
            set params [dict get $register parameters]
            set size   [dict get $register size]
            if {[icflow::args::contains $params -clock_divider]} {
                icflow::generate::writeLine $o "// Clock Divider ${name}"
                icflow::generate::writeLine $o "reg \[7:0\] ${name}_counter;"
                icflow::generate::writeLine $o "reg \[7:0\] ${name}_reg;"
            }

            if {[icflow::args::contains $params -hw_write -sw_read_only]} {
                icflow::generate::writeLine $o "reg \[[expr $size-1]:0\] ${name}_reg;"
            }

            if {[icflow::args::contains $params -updown -counter]} {
                icflow::generate::writeLine $o "reg ${name}_up;"
            }
            
        }
        icflow::generate::writeEmptyLines $o 2
        
        ## Register I/O Assignments
        ################
        icflow::generate::writeLine $o "// Registers I/O assignments"
        icflow::generate::writeLine $o "// ---------------"
        foreach register $dictRegisters {
            set name   [dict get $register name]
            set params [dict get $register parameters]
            set size   [dict get $register size]
            if {[icflow::args::containsNot $params -clock_divider -fifo* -hw_write]} {

                icflow::generate::writeLine $o "reg \[[expr $size-1]:0\] ${name}_reg;"

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
        foreach register $dictRegisters {
            set name   [dict get $register name]
            set params [dict get $register parameters]
            if {[icflow::args::contains $params -bits]} {
                set bi 0
                foreach bit [dict get $params -bits] {
                    set bName [dict get $bit name]
                    set bParams [dict get $bit parameters]
                    if {[icflow::args::containsNot $bParams -input]} {
                        icflow::generate::writeLine $o "assign ${name}_$bName = ${name}_reg\[$bi\];"
                    } 
                    incr bi
                }
            }
        }
        icflow::generate::writeEmptyLines $o 2

        ## Write Stage
        #####################
        

        icflow::generate::writeLine $o "// Register Writes"
        icflow::generate::writeLine $o "// ---------------"
        icflow::generate::writeLine $o "always@(posedge clk) begin" -indent
   

            icflow::generate::writeLine $o "if (!resn) begin" -indent
            ## Resets for registers
            foreach register $dictRegisters {
                set name   [dict get $register name]
                set params [dict get $register parameters]
                if {[icflow::args::contains $params -fifo_axis_master]} {

                    icflow::generate::writeLine $o "${name}_m_axis_tvalid <= 1'b0;"
                    if {[icflow::args::contains $params -with_tlast]} {
                        icflow::generate::writeLine $o "${name}_m_axis_tlast  <= 1'b0;"
                    }

                }  elseif {[icflow::args::containsNot $params  -fifo_axis_slave ]} {
                    icflow::generate::writeLine $o "${name}_reg <= [icflow::args::getValue $params -reset 0];"
                } 

                if {[icflow::args::contains $params -updown -counter]} {
                    icflow::generate::writeLine $o "${name}_up <= 1'b1;"
                }
                #icflow::generate::writeLine $o "// ${name}_reg;"
            }
            icflow::generate::writeLine $o "end else begin" -outdent -indent
                icflow::generate::writeEmptyLines $o 2

                ## Input bits are always sampled
                icflow::generate::writeLine $o "// Single in bits are always sampled"
                foreach register $dictRegisters {
                    set params [dict get $register parameters]
                    set name   [dict get $register name]
                    if {[icflow::args::contains $params -bits]} {
                        set bi 0
                        foreach bit [dict get $params -bits] {
                            set bName [dict get $bit name]
                            set bParams [dict get $bit parameters]
                            if {[icflow::args::contains $bParams -input]} {
                                icflow::generate::writeLine $o "${name}_reg\[$bi\] <= ${name}_$bName;"
                            } 
                            incr bi
                        }
                    }
                }
                icflow::generate::writeEmptyLines $o 2

                ## Write Case  for registers
                icflow::generate::writeLine $o "// Write for simple registers"
                icflow::generate::writeLine $o "case({rfg_write,rfg_address})" -indent
                    foreach register $dictRegisters {
                        set params [dict get $register parameters]
                        set name   [dict get $register name]

                        if {[icflow::args::contains $params -clock_divider]} {

                            icflow::generate::writeLine $o "{1'b1,8'h[format %x [dict get $register address]]}: begin" -indent
                                icflow::generate::writeLine $o "${name}_reg <= rfg_write_value;"
                            icflow::generate::writeLine $o "end" -outdent

                        }  elseif {[icflow::args::containsNot $params -fifo* -sw_read_only]} {
                            ## Standard registers
                            set registerSize [dict get $register size]
                            set byteCount    [expr ceil($registerSize / 8.0)]
                            #puts "base address [dict get $register address]"
                            for {set i 0} {$i < $byteCount} {incr i} {
                                set partAddress [expr [dict get $register address] + $i  ]
                                icflow::generate::writeLine $o "{1'b1,8'h[format %x $partAddress]}: begin" -indent
                                    set lowBit  [expr $i*8]
                                    set highBit [expr $lowBit + [expr $registerSize<8 ? $registerSize - 1 : 7]]
                                    if {$highBit<7} {
                                        icflow::generate::writeLine $o "${name}_reg\[$highBit:$lowBit\] <= rfg_write_value\[$highBit:$lowBit\];"
                                    } else {    
                                        icflow::generate::writeLine $o "${name}_reg\[$highBit:$lowBit\] <= rfg_write_value;"
                                    }
                                    
                                icflow::generate::writeLine $o "end" -outdent
                            }
                            
                        }  
                    }
                    icflow::generate::writeLine $o "default: begin"
                    icflow::generate::writeLine $o "end"
                    
                icflow::generate::writeLine $o "endcase" -outdent
                icflow::generate::writeLine $o ""

                ## Write case for FIFO
                icflow::generate::writeLine $o "// Write for FIFO Master"
                foreach register $dictRegisters {
                    set name        [dict get $register name]
                    set address     [dict get $register address]
                    set parameters  [dict get $register parameters]

                    if {[icflow::args::contains $parameters -fifo*master]} {
                        icflow::generate::writeLine $o "if(rfg_write && rfg_address==8'h[format %x $address]) begin" -indent
                            
                            icflow::generate::writeLine $o "${name}_m_axis_tvalid <= 1'b1;"
                            icflow::generate::writeLine $o "${name}_m_axis_tdata  <= rfg_write_value;"
                            if {[icflow::args::contains $parameters -with_tlast]} {
                                icflow::generate::writeLine $o "${name}_m_axis_tlast  <= rfg_write_last;"
                            }
                        
                        icflow::generate::writeLine $o "end else begin" -outdent -indent
                            
                            icflow::generate::writeLine $o "[dict get $register name]_m_axis_tvalid <= 1'b0;"
                            if {[icflow::args::contains $parameters -with_tlast]} {
                                icflow::generate::writeLine $o "${name}_m_axis_tlast  <= 1'b0;"
                            }
                        icflow::generate::writeLine $o "end" -outdent
                    }
                }
                icflow::generate::writeLine $o ""

                ## Write case for HW Write only
                icflow::generate::writeLine $o "// Write for HW Write only"
                foreach register $dictRegisters {
                    set params [dict get $register parameters]
                    set name   [dict get $register name]
                    if {[icflow::args::contains $params -hw_write -sw_read_only]} {
                        icflow::generate::writeLine $o "if(${name}_write) begin" -indent
                            icflow::generate::writeLine $o "${name}_reg <= ${name} ;"
                        icflow::generate::writeLine $o "end" -outdent
                    }
                }

                ## Write case for counter
                icflow::generate::writeLine $o "// Write for Counter"
                foreach register $dictRegisters {
                    set params [dict get $register parameters]
                    set name   [dict get $register name]
                    if {[icflow::args::contains $params -counter]} {
                        
                        set countLine "${name}_reg <= ${name}_reg + 1 ;"
                        if {[icflow::args::contains $params -updown]} {
                            set countLine "${name}_reg <= ${name}_up ? ${name}_reg + 1 : ${name}_reg -1 ;"
                        }

                        if {[icflow::args::contains $params -sw_read_only -enable]} {
                             ## SW Readonlu and enable -> count on enable
                            icflow::generate::writeLine $o "if(${name}_enable) begin" -indent
                                icflow::generate::writeLine $o $countLine
                            icflow::generate::writeLine $o "end" -outdent
                        } elseif {[icflow::args::containsNot $params -sw_read_only] && [icflow::args::contains $params -enable]} {
                            ## SW Write allowed and enable -> count on enable and not write
                            icflow::generate::writeLine $o "if(!(rfg_write && rfg_address==8'h[format %x [dict get $register address]]) && ${name}_enable) begin" -indent
                                icflow::generate::writeLine $o $countLine
                            icflow::generate::writeLine $o "end" -outdent
                        } elseif {[icflow::args::containsNot $params -sw_read_only]} {
                            ## SW Write enable, just write
                            icflow::generate::writeLine $o "if(!(rfg_write && rfg_address==8'h[format %x [dict get $register address]])) begin" -indent
                                icflow::generate::writeLine $o $countLine
                            icflow::generate::writeLine $o "end" -outdent
                        }

                

                        if {[icflow::args::contains $params -interrupt]} {
                            
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
                           
                            #icflow::generate::writeLine $o "${name}_interrupt <= ${name}_match_reg == ${name}_reg ;"
                         
                        }
                    }
                }
                

            icflow::generate::writeLine $o "end" -outdent

 
        icflow::generate::writeLine $o "end" -outdent
        icflow::generate::writeEmptyLines $o 2


        ## Read Stage
        #####################

        ## Read ready case for FIFO
        icflow::generate::writeLine $o "// Read for FIFO Slave"
        foreach register $dictRegisters {
            set name    [dict get $register name]
            set address [dict get $register address]
            if {[icflow::args::contains [dict get $register parameters] -fifo*slave]} {
                icflow::generate::writeLine $o "assign ${name}_s_axis_tready = rfg_read && rfg_address==8'h[format %x $address];"
            }
        }
        icflow::generate::writeEmptyLines $o 2
        
        icflow::generate::writeLine $o "// Register Read"
        icflow::generate::writeLine $o "// ---------------"
        icflow::generate::writeLine $o "always@(posedge clk) begin" -indent
   

            icflow::generate::writeLine $o "if (!resn) begin" -indent
                icflow::generate::writeLine $o "rfg_read_valid <= 0;"
                icflow::generate::writeLine $o "rfg_read_value <= 0;"
            icflow::generate::writeLine $o "end else begin" -outdent -indent

                ## Read Case  for registers
                icflow::generate::writeLine $o "// Read for simple registers"
                icflow::generate::writeLine $o "case({rfg_read,rfg_address})" -indent
                    foreach register $dictRegisters {
                        set params [dict get $register parameters]
                        set name   [dict get $register name]

                        #if {[icflow::args::contains $params -clock_divider]} {

                         #   icflow::generate::writeLine $o "{1'b1,8'h[dict get $register address]}: begin" -indent
                         #       icflow::generate::writeLine $o "rfg_read_value <= ${name}_reg ;"
                         #       icflow::generate::writeLine $o "rfg_read_valid <= 1 ;"
                         #   icflow::generate::writeLine $o "end" -outdent

                        #} else
                        #if {![icflow::args::contains $params -fifo*]} {
                        #    icflow::generate::writeLine $o "{1'b1,8'h[dict get $register address]}: begin" -indent
                        #        icflow::generate::writeLine $o "rfg_read_value <= ${name}_reg;"
                        #        icflow::generate::writeLine $o "rfg_read_valid <= 1 ;"
                        #    icflow::generate::writeLine $o "end" -outdent
                        #}  else
                        if {[icflow::args::contains $params -fifo*slave]} {
                            icflow::generate::writeLine $o "{1'b1,8'h[format %x [dict get $register address]]}: begin" -indent
                                icflow::generate::writeLine $o "rfg_read_value <= ${name}_s_axis_tvalid ? ${name}_s_axis_tdata : 8'hff;"
                                icflow::generate::writeLine $o "rfg_read_valid <= 1 ;"
                            icflow::generate::writeLine $o "end" -outdent
                        } elseif {[icflow::args::containsNot $params -fifo*master]} {
                            ## Standard registers
                            set registerSize [dict get $register size]
                            set byteCount    [expr $registerSize / 8 ]
                            #puts "base address [dict get $register address]"
                            for {set i 0} {$i < $byteCount} {incr i} {
                                set partAddress [expr [dict get $register address] + $i  ]
                                icflow::generate::writeLine $o "{1'b1,8'h[format %x $partAddress]}: begin" -indent
                                    set lowBit  [expr $i*8]
                                    set highBit [expr $lowBit +7]
                                    icflow::generate::writeLine $o "rfg_read_value <= ${name}_reg\[$highBit:$lowBit\];"
                                    icflow::generate::writeLine $o "rfg_read_valid <= 1 ;"
                                icflow::generate::writeLine $o "end" -outdent
                            }
                        }

                        
                    }
                    icflow::generate::writeLine $o "default: begin"
                        icflow::generate::writeLine $o "rfg_read_valid <= 0 ;"
                    icflow::generate::writeLine $o "end"
                    
                icflow::generate::writeLine $o "endcase" -outdent
                icflow::generate::writeLine $o ""

            icflow::generate::writeLine $o "end" -outdent

 
        icflow::generate::writeLine $o "end" -outdent
        icflow::generate::writeEmptyLines $o 2

        ## Clock Divider
        ################
        foreach register $dictRegisters {
            set name   [dict get $register name]
            set params [dict get $register parameters]
            if {[icflow::args::contains $params -clock_divider]} {

                      
                icflow::generate::writeLine $o "always@(posedge ${name}_source_clk) begin" -indent     
                    icflow::generate::writeLine $o "if (!${name}_source_resn) begin" -indent     
                    
                        icflow::generate::writeLine $o "${name}_divided_clk <= 1'b0;"     
                        icflow::generate::writeLine $o "${name}_counter <= 8'h00;"  
                         
                        
                    icflow::generate::writeLine $o "end else begin" -indent -outdent  

                       # icflow::generate::writeLine $o "${name}_divided_resn <= 1'b1;"     

                        icflow::generate::writeLine $o "if (${name}_counter==${name}_reg) begin" -indent 
                            icflow::generate::writeLine $o "${name}_divided_clk <= !${name}_divided_clk;"     
                            icflow::generate::writeLine $o "${name}_counter <= 8'h00;"     
                        
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
                icflow::generate::writeLine $o "always@(posedge ${name}_divided_clk$resetEdge) begin" -indent 
                    icflow::generate::writeLine $o "if (!${name}_source_resn) begin" -indent 
                        icflow::generate::writeLine $o "${name}_divided_resn_delay <= 8'h00;"    
                    icflow::generate::writeLine $o "end else begin" -indent -outdent 
                        icflow::generate::writeLine $o "${name}_divided_resn_delay <= {${name}_divided_resn_delay\[6:0\],1'b1};"    
                    icflow::generate::writeLine $o "end" -outdent  
                icflow::generate::writeLine $o "end" -outdent
                icflow::generate::writeEmptyLines $o 2

            }
        }

        ## Registers to be synched in another clock domain
        #################
        foreach register $dictRegisters {
            set name   [dict get $register name]
            set params [dict get $register parameters]

            if {[icflow::args::contains $params -read_clock]} {
                set targetClock [dict get $params -read_clock]
                icflow::generate::writeLine $o "// Synchronisation of $name into read clock domain" 
                icflow::generate::writeLine $o "always@(posedge ${targetClock}_clk) begin" -indent 
                    icflow::generate::writeLine $o "if (!${targetClock}_resn) begin" -indent 
                        icflow::generate::writeLine $o "${name}_reg_target_clock <= 8'h00;"    
                    icflow::generate::writeLine $o "end else begin" -indent -outdent 
                        icflow::generate::writeLine $o "${name}_reg_target_clock <= ${name}_reg;"    
                    icflow::generate::writeLine $o "end" -outdent  
                icflow::generate::writeLine $o "end" -outdent
                icflow::generate::writeEmptyLines $o 2
            }   
            
        }
        
       

        ## End of module 
        icflow::generate::outdent
        icflow::generate::writeLine $o "endmodule"


        close $o

        ## Wrapper
        ####################

    }


    proc generateSVPackage {registersDefs {targetFolder .}} {

        ## Target File 
        ####################
        set targetFile $targetFolder/${::IC_RFG_NAME}_pkg.sv
        set o [open $targetFile w+]
        puts "Generating $targetFile" 

        ## Parse registers
        ##########
        set registers [registersToDict $registersDefs]
        
        
        ## Write
        ################
        set packageName [string tolower ${::IC_RFG_NAME}]_pkg
        set ifdefName   [string toupper $packageName]
        icflow::generate::writeLine $o "`ifndef $ifdefName"
            icflow::generate::writeLine $o "`define $ifdefName"
            icflow::generate::writeLine $o "package ${packageName};" -indent
            
            icflow::generate::writeLine $o "enum {"
            set enumLines {}
            foreach register $registers {
                set name [dict get $register name]
                set addr [dict get $register address]
                lappend enumLines "[string toupper $name] = 8'h[format %x $addr]"
            }
            icflow::generate::writeLines $o $enumLines ,

            icflow::generate::writeLine $o "} addresses;"

        icflow::generate::writeLine $o "endpackage" -outdent
        icflow::generate::writeLine $o "`endif"

    }


    proc generatePythonPackage {registersDefs {targetFolder .}} {

        ## Target File 
        ####################
        file mkdir $targetFolder
        #set targetFile $targetFolder/[string tolower ${::IC_RFG_NAME}].py
        set targetFile $targetFolder/__init__.py
        set o [open $targetFile w+]
        icflow::generate::writeEmptyLines $o 2
        puts "Generating Python package to $targetFile" 

        ## Write python init in folder
        #if {![file exists $targetFolder/__init__.py]} {
        #    set initFile [open $targetFolder/__init__.py w+]
        #    close $initFile
        #}

        ## Parse registers
        ##########
        set registers [registersToDict $registersDefs]

        set className [string tolower ${::IC_RFG_NAME}]
        
        ## Write imports
        ############
        icflow::generate::writeLine $o "import logging"
        icflow::generate::writeLine $o "from rfg.core import AbstractRFG"
        icflow::generate::writeLine $o "from rfg.core import RFGRegister"

        
        icflow::generate::writeLine $o "logger = logging.getLogger(__name__)"
        icflow::generate::writeEmptyLines $o 2

        ## Write RFG Loading helper
        ############
        icflow::generate::writeLine $o "def load_rfg():" -indent
            icflow::generate::writeLine $o "return ${className}()" -outdent_after  
        icflow::generate::writeEmptyLines $o 2
        

        ## Write addresses of registers
        #################
        foreach register $registers {
            set name   [dict get $register name]
            icflow::generate::writeLine $o "[string toupper $name] = 0x[format %x [dict get $register address]]"
        }
        icflow::generate::writeEmptyLines $o 2

       

        ## Write Class
        ################
        
        
        
        icflow::generate::writeEmptyLines $o 2
        icflow::generate::writeLine $o "class ${className}(AbstractRFG):" -indent
            icflow::generate::writeLine $o {"""Register File Entry Point Class"""}
            icflow::generate::writeEmptyLines $o 2

            icflow::generate::writeLine $o "class Registers(RFGRegister):" -indent 
            foreach register $registers {
                set name   [dict get $register name]
                    icflow::generate::writeLine $o "[string toupper $name] = 0x[format %x [dict get $register address]]"
            }
            icflow::generate::writeLine $o "" -outdent
            icflow::generate::writeEmptyLines $o 2

            ## Constructor
            icflow::generate::writeLine $o "def __init__(self):" -indent 
                icflow::generate::writeLine $o "super().__init__()" -outdent_after

            icflow::generate::writeEmptyLines $o 2
            icflow::generate::writeLine $o "def hello(self):" -indent 
                icflow::generate::writeLine $o "logger.info(\"Hello World\")" -outdent_after
               
        ## Generate single writes for registers
        foreach register $registers {
            set name   [dict get $register name]
            set params [dict get $register parameters]
            set rSize  [dict get $register size]
            set bytesCount [expr int(ceil($rSize / 8.0))]
            icflow::generate::writeEmptyLines $o 2

            ## Write is not possible on FIFO slave interfaceand read only
            if {[icflow::args::containsNot $params -fifo*slave -sw_read_only]} {
                set increment "False"
                if {$bytesCount>1} {
                    set increment "True"
                }
                icflow::generate::writeEmptyLines $o 1
                icflow::generate::writeLine $o "async def write_${name}(self,value : int,flush = False):" -indent
                    icflow::generate::writeLine $o "self.addWrite(register = self.Registers\['[string toupper $name]'\],value = value,increment = $increment,valueLength=$bytesCount)" 
                    icflow::generate::writeLine $o "if flush == True:" -indent
                        icflow::generate::writeLine $o "await self.flush()" -outdent_after
                    icflow::generate::writeLine $o "" -outdent_after
            }

            ## Write to FIFO master should offer a bytes write function
            if {[icflow::args::contains $params -fifo*master]} {

                icflow::generate::writeEmptyLines $o 1
                icflow::generate::writeLine $o "async def write_${name}_bytes(self,values : bytearray,flush = False):" -indent 
                    icflow::generate::writeLine $o "for b in values:" -indent
                        icflow::generate::writeLine $o "self.addWrite(register = self.Registers\['[string toupper $name]'\],value = b,increment = False,valueLength=1)" -outdent_after
                    icflow::generate::writeLine $o "if flush == True:" -indent
                        icflow::generate::writeLine $o "await self.flush()" -outdent_after
                    icflow::generate::writeLine $o "" -outdent_after
            }

            ## Read is not possible on FIFO master interface
            if {[icflow::args::containsNot $params -fifo*master]} {

                set increment "False"
                if {$bytesCount>1} {
                    set increment "True"
                }

                icflow::generate::writeEmptyLines $o 1
                    icflow::generate::writeLine $o "async def read_${name}(self, count : int = [expr $rSize/8] , targetQueue: str | None = None) -> int: " -indent 
                icflow::generate::writeLine $o "return  int.from_bytes(await self.syncRead(register = self.Registers\['[string toupper $name]'\],count = count, increment = $increment , targetQueue = targetQueue), 'little') " 
                icflow::generate::writeLine $o "" -outdent_after
                icflow::generate::writeEmptyLines $o 1
                    icflow::generate::writeLine $o "async def read_${name}_raw(self, count : int = [expr $rSize/8] ) -> bytes: " -indent 
                icflow::generate::writeLine $o "return  await self.syncRead(register = self.Registers\['[string toupper $name]'\],count = count, increment = $increment)" 
                icflow::generate::writeLine $o "" -outdent_after
            }  
            
            #
        }

        icflow::generate::writeLine $o "" -outdent_after

    }

}

package provide icflow::rfg::hdl 1.0
package require icflow::rfg
package require icflow::hdlbuild
package require icflow::hdlbuild::verilog 

namespace eval icflow::rfg::hdlbuild {

    oo::class create HRFGMixin {
       
       method register_file {name registers script} {

            set ::IC_RFG_NAME $name
            set targetFile "./${::IC_HDLBUILD_OUTPUTS}/${name}.sv"
            exec mkdir -p [file dirname $targetFile]

            #exec mkdir -p ${::IC_FSP_OUTPUTS}/sv
            exec mkdir -p ${::IC_FSP_OUTPUTS}/${::IC_TOP}

            ::icflow::rfg::generate               $registers $targetFile
            ::icflow::rfg::generateSVPackage      $registers ${::IC_HDLBUILD_OUTPUTS}/
            ::icflow::rfg::generatePythonPackage  $registers ${::IC_FSP_OUTPUTS}/${::IC_TOP}

            ## Parse Output and register as module
            set rfgmodule [icflow::hdlbuild::verilog::loadFile $targetFile]

            my instance [$rfgmodule getName] $script

       }
    }

    oo::define icflow::hdlbuild::HModule mixin -append [namespace current]::HRFGMixin

    proc build {registers script} {
        
        

    }

    ## Register HDL
    icflow::hdlbuild::registerModule rfg:spi:slave:axis:igress {
        ## Load function
        icflow::hdlbuild::verilog::loadFile $::env(RFGV1_HOME)/rtl/spi/spi_slave_axis_igress.sv
    }
    icflow::hdlbuild::registerModule rfg:spi:slave:axis:igress:to_clk {
        ## Load function
        icflow::hdlbuild::verilog::loadFile $::env(RFGV1_HOME)/rtl/spi/spi_slave_axis_igress_to_clk.sv
    }

    
    icflow::hdlbuild::registerModule rfg:spi:slave:axis:egress {
        ## Load function
        icflow::hdlbuild::verilog::loadFile $::env(RFGV1_HOME)/rtl/spi/spi_slave_axis_egress.sv
    }
    icflow::hdlbuild::registerModule rfg:axis:readout_framing {
        ## Load function
        icflow::hdlbuild::verilog::loadFile $::env(RFGV1_HOME)/rtl/protocol/rfg_axis_readout_framing.sv
    }
    icflow::hdlbuild::registerModule rfg:axis:protocol {
        ## Load function
        icflow::hdlbuild::verilog::loadFile $::env(RFGV1_HOME)/rtl/protocol/rfg_axis_protocol.sv
    }

}

## Select version
if {"-v2" in $::argv} {
    package require icflow::rfg 2.0
    package require icflow::rfg::python 2.0
} else {
    package require icflow::rfg 1.0
    package require icflow::rfg::python 1.0
}


package require icflow::rfg::markdown


set registersFile [lindex $argv end]


if {![file exists $registersFile]} {
    icError "RFG Script containing registers doesn't exist: $registersFile"
} else {

    set args [icflow::args::toDict [lrange $argv 0 end-1]]

    icInfo "Generating RFG using config from $registersFile, args=$args"


    ## Source Registers
    set registers [source $registersFile]

    ## Address space mapping
    set addr_space_offset [icflow::args::getValue $args -addr_space_offset 0x0]

    ## Generate locally
    icCheckGVariable IC_RFG_NAME
    icCheckGVariable IC_RFG_TARGET
    if {[icCheckHasErrors]} {
        exit -1
    }

    #set ::IC_RFG_NAME $name
    set targetFile "./${::IC_RFG_NAME}.sv"

    ::icflow::rfg::generate               $registers $targetFile -addr_space_offset $addr_space_offset

    ::icflow::rfg::python::generatePythonPackage  $registers ${::IC_FSP_OUTPUTS}/${::IC_RFG_TARGET}

    set targetMd [icflow::args::getValue $args -md "./${::IC_RFG_NAME}.md"]

    ::icflow::rfg::markdown::generate $registers $targetMd

}

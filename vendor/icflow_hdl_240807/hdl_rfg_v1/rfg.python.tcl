package provide icflow::rfg::python 1.0

namespace eval icflow::rfg::python {


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
        set registerDefs [uplevel [list subst $registersDefs]]
        #puts "registers: $registerDefs"
        set registers [::icflow::rfg::registersToDict $registerDefs]

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
        foreach {name params} $registers {
            #set name   [dict get $register name]
            icflow::generate::writeLine $o "[string toupper $name] = 0x[format %x [dict get $params address]]"
        }
        icflow::generate::writeEmptyLines $o 2



        ## Write Class
        ################



        icflow::generate::writeEmptyLines $o 2
        icflow::generate::writeLine $o "class ${className}(AbstractRFG):" -indent
            icflow::generate::writeLine $o {"""Register File Entry Point Class"""}
            icflow::generate::writeEmptyLines $o 2

            icflow::generate::writeLine $o "class Registers(RFGRegister):" -indent
            foreach {name params} $registers {
                #set name   [dict get $register name]
                icflow::generate::writeLine $o "[string toupper $name] = 0x[format %x [dict get $params address]]"
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
        foreach {name params} $registers {
            #set name   [dict get $register name]
            #set params [dict get $register parameters]
            set rSize  [dict get $params size]
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

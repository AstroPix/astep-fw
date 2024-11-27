
## Main ICFLOW 
############
export ICFLOW_HOME="$(dirname "$(readlink -f ${BASH_SOURCE[0]})")"
export PATH="$ICFLOW_HOME/common_icflow_v1/bin:$ICFLOW_HOME/common_doc_v1/bin:$PATH"
export TCLLIBPATH="$ICFLOW_HOME $TCLLIBPATH"

#source $ICFLOW_HOME/cocotb_runner_v1/load.sh
#source $ICFLOW_HOME/common_fastflow_v1/load.sh

## Load all sub projects load.sh
##########
for loadFile in $(ls $ICFLOW_HOME/*/load.sh)
do
    source $loadFile
done

## Project Stuff
#############

#if [[ -z $BASE ]]
#then 
#    export BASE="$(dirname "$(readlink -f ${ICFLOW_HOME}/..)")"
#    echo "[ICF] No BASE environment variable set, setting to: $BASE"
#fi

## If no ADL_TECH, offer sourcing the design kit
if [[ -z $ADL_TECH && ! -z $DESIGN_KIT ]]
then
    echo "[ICF] It looks like no technology is loaded. Remember to load the design kit"
    echo "Would you like to load the default design kit $DEFAULT_KIT (y for yes)?"
    read load_kit
    if  [[ $load_kit == "y" ]] 
    then 
         source $DEFAULT_KIT; 
    fi
    	
fi
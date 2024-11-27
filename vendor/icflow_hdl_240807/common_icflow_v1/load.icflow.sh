BASE="$(dirname "$(readlink -f ${BASH_SOURCE[0]})")"
echo "LIb: $BASE"
export TCLLIBPATH="$BASE $TCLLIBPATH"
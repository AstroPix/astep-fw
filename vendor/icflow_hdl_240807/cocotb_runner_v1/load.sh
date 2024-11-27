
export CCTBV1_HOME="$(dirname "$(readlink -f ${BASH_SOURCE[0]})")"
export PATH="$CCTBV1_HOME/bin:$CCTBV1_HOME/node_modules/.bin:$PATH"

export PYTHONPATH="$CCTBV1_HOME/python:$PYTHONPATH"
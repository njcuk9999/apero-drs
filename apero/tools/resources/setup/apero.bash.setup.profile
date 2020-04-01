#!/bin/bash
# bash setup file

# setup paths
export PATH={PATH}:$PATH

# setup up python path
export PYTHONPATH={PYTHONPATH}:$PYTHONPATH

# setup aliases
alias gointroot="cd {ROOT_PATH}"

# setup drs config path
export DRS_UCONFIG="{USER_CONFIG}"

# force numpy  to only use 1 core max
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

# =======================
# COLOURED PROMPT
# =======================
RED="\e[1;31m"
BLUE="\e[1;34m"
YELLOW="\e[0;33m"
WHITE="\e[0;37m"
END="\e[m"
export PS1=" ${{YELLOW}}{NAME} ${{WHITE}}\d \t ${{BLUE}}\u@\h: ${{RED}}\w${{END}}\n>>   "
unset RED BLUE YELLOW WHITE END
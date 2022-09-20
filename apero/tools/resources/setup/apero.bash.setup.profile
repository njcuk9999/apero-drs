#!/bin/bash
# bash setup file

# setup aliases
alias gointroot="cd {ROOT_PATH}"
alias gosetup="cd {USER_CONFIG}"

# setup drs config path
export DRS_UCONFIG="{USER_CONFIG}"

# force numpy  to only use 1 core max
export MKL_DYNAMIC=FALSE
export MKL_CBWR=COMPATIBLE
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

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

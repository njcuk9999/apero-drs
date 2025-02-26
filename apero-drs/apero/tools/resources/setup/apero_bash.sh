#!/bin/bash
# bash setup file

# setup aliases
alias gointroot="cd {ROOT_PATH}"
alias gosetup="cd {USER_CONFIG}"

# setup drs config path
export DRS_UCONFIG="{USER_CONFIG}"
# Check if DRS_PS1 is undefined (and set if not)
if [ -z "${DRS_PS1+x}" ]; then
    export DRS_PS1="$PS1"
fi

# force numpy  to only use 1 core max
export MKL_DYNAMIC=FALSE
export MKL_CBWR=COMPATIBLE
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# Echo command complete
echo "Successfully activated {APERO_PROFILE}"
# Set the command prompt
export PS1="[{NAME}] $DRS_PS1"

# run apero validate
apero_validate.py
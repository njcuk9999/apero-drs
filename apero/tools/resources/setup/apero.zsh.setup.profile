#!/bin/zsh
# zsh setup file

# setup paths
export PATH={PATH}:$PATH

# setup up python path
export PYTHONPATH={PYTHONPATH}:$PYTHONPATH

# setup aliases
alias gointroot="cd {ROOT_PATH}"
alias gosetup="cd {USER_CONFIG}"

# setup drs config path
export DRS_UCONFIG="{USER_CONFIG}"

# force numpy to only use 1 core max
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
export PS1=" %F{{yellow}}{NAME} %F{{white}}%D{{%a %b %d}} %* %B%F{{blue}}%n@%m: %F{{red}}%~%f%b"$'\n'">>   "

#!/bin/tcsh/
# tcsh setup file

# setup paths
setenv PATH {PATH}:$PATH

# setup up python path
setenv PYTHONPATH {PYTHONPATH}:$PYTHONPATH

# setup aliases
alias gointroot "cd {ROOT_PATH}"
alias gosetup "cd {USER_CONFIG}"

# setup drs config path
setenv DRS_UCONFIG "{USER_CONFIG}"

# force numpy  to only use 1 core max
setenv MKL_DYNAMIC=FALSE
setenv MKL_CBWR=COMPATIBLE
setenv OMP_NUM_THREADS=1
setenv OPENBLAS_NUM_THREADS=1
setenv MKL_NUM_THREADS=1
setenv VECLIB_MAXIMUM_THREADS=1
setenv NUMEXPR_NUM_THREADS=1

# =======================
# COLOURED PROMPT
# =======================
set     red="%{{\033[1;31m%}}"
set  yellow="%{{\033[1;33m%}}"
set    blue="%{{\033[1;34m%}}"
set   white="%{{\033[0;37m%}}"
set     end="%{{\033[0m%}}"

# Set prompt
set prompt = " ${{yellow}}{NAME}${{white}} %d %w %D %P ${{blue}}%n@%m: ${{red}}%~${{white}} \n>>  ${{end}} "

# Clean up after ourselves...
unset red yellow blue white end
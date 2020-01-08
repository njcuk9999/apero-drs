#!/bin/tcsh/
# tcsh setup file

# setup paths
setenv PATH "{ROOT_PATH}":"{BIN_PATH}":"{TOOL_PATH}":$PATH

# setup up python path
setenv PYTHONPATH "{ROOT_PATH}":"{BIN_PATH}":"{TOOL_PATH}":$PYTHONPATH

# setup aliases
alias gointroot "cd {ROOT_PATH}"

# setup drs config path
setenv DRS_UCONFIG "{USER_CONFIG}"

# force numpy  to only use 1 core max
setenv OPENBLAS_NUM_THREADS 1
setenv MKL_NUM_THREADS 1

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
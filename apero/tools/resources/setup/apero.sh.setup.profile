#!/bin/tcsh/
# tcsh setup file

# setup paths
setenv PATH "{TOOL_PATH}":$PATH
setenv PATH "{BIN_PATH}":$PATH
setenv PATH "{ROOT_PATH}":$PATH

# setup up python path
setenv PYTHONPATH "{TOOL_PATH}":$PYTHONPATH
setenv PYTHONPATH "{BIN_PATH}":$PYTHONPATH
setenv PYTHONPATH "{ROOT_PATH}":$PYTHONPATH

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
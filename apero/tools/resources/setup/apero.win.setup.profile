# Windows setup file

# setup path
set PATH="{ROOT_PATH}";"{BIN_PATH}";"{TOOL_PATH}";%PATH%

# setup up python path
set PYTHONPATH="{ROOT_PATH}";"{BIN_PATH}";"{TOOL_PATH}";%PYTHONPATH%

# setup drs config path
export DRS_UCONFIG="{USER_CONFIG}"

# force numpy  to only use 1 core max
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
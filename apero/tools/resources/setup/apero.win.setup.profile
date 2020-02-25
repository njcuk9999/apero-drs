# Windows setup file

# setup path
set PATH={PATH};%PATH%

# setup up python path
set PYTHONPATH={PYTHONPATH};%PYTHONPATH%

# setup drs config path
export DRS_UCONFIG="{USER_CONFIG}"

# force numpy  to only use 1 core max
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
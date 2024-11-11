@echo off
:: Windows batch setup file

:: setup aliases (Windows doesn't have aliases like bash, so we use a workaround with environment variables)
set GOINTROOT=cd {ROOT_PATH}
set GOSETUP=cd {USER_CONFIG}

:: setup drs config path
set DRS_UCONFIG={USER_CONFIG}

:: force numpy to only use 1 core max
set MKL_DYNAMIC=FALSE
set MKL_CBWR=COMPATIBLE
set OMP_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1
set MKL_NUM_THREADS=1
set VECLIB_MAXIMUM_THREADS=1
set NUMEXPR_NUM_THREADS=1

:: Set the CMD prompt
prompt [{NAME}] $P$G
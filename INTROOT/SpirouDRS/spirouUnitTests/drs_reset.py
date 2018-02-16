#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs_reset.py

Reset the DRS to a clean build start (basically destroys all changes in the
data directory (except the raw directory)
- currently this includes setting up a new calibDB with wave keys (as we do not
calculate them in the DRS)

Created on 2018-02-16 at 11:20

@author: cook
"""

import numpy as np
import os
import shutil
import glob
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings
from SpirouDRS import spirouStartup
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_reset.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()

# =============================================================================
# Define functions
# =============================================================================
def reset_reduced_folders(p):

    # log progress
    WLOG('', DPROG, 'Resetting reduced directory')
    # remove files from reduced folder
    red_dir = p['DRS_DATA_REDUC']
    # loop around files and folders in calib_dir
    remove_all(red_dir)


def reset_calibdb(p):
    # TODO: eventually the calibDB should be reset to empty
    # TODO:    Thus this function will not be needed

    # log progress
    WLOG('', DPROG, 'Resetting calibration database')

    # remove files currently in calibDB
    calib_dir = p['DRS_CALIB_DB']
    # loop around files and folders in calib_dir
    remove_all(calib_dir)

    # -------------------------------------------------------------------------
    # get reset directory location
    # get package name and relative path
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.CDATA_FOLDER()
    # get absolute folder path from package and relfolder
    absfolder = spirouConfig.GetAbsFolderPath(package, relfolder)
    # -------------------------------------------------------------------------
    # define needed files:
    files = ['2017-10-11_21-32-17_hcone_hcone02c406_wave_AB.fits',
             '2017-10-11_21-32-17_hcone_hcone02c406_wave_C.fits',
             'spirou_wave_ini3.fits',
             'tapas_combined_za=20.000000.fits',
             'TAPAS_X_axis_speed_dv=0.5.fits',
             'master_calib_SPIROU.txt']
    # -------------------------------------------------------------------------
    # copy required calibDB files to DRS_CALIB_DB path
    for f in files:
        # get old and new paths
        oldpath = os.path.join(absfolder, f)
        newpath = os.path.join(calib_dir, f)
        # check that old path exists
        if os.path.exists(oldpath):
            # log progress
            wmsg = 'Adding file: {0} to {1}'
            WLOG('', DPROG, wmsg.format(f, p['DRS_CALIB_DB']))
            # remove the old file
            if os.path.exists(newpath):
                os.remove(newpath)
            # copy over the new file
            shutil.copy(oldpath, newpath)
        else:
            wmsg = 'File {0} does not exists in {1} - cannot add'
            WLOG('warning', DPROG, wmsg.format(f, absfolder))
    # -------------------------------------------------------------------------



def reset_log(p):
    # log progress
    WLOG('', DPROG, 'Resetting log directory')
    # remove files from reduced folder
    log_dir = p['DRS_DATA_MSG']
    # loop around files and folders in reduced dir
    remove_all(log_dir)

def remove_all(path):
    # loop around files and folders in calib_dir
    files = glob.glob(path + '/*')
    # loop around all files (adding all files from sub directories
    while len(files) > 0:
        f = files[0]
        files = remove(f, files)
        files.remove(f)


def remove(path, list_of_files):
    """
    Remove a file or add files to list_of_files
    :param path:
    :param list_of_files: list of strings, list of files
    :return:
    """
    # check if directory
    if os.path.isdir(path):
        # if directory add contents to list of files
        list_of_files += glob.glob(path + '/*')
    else:
        # log removal
        WLOG('', DPROG, '    Removing file: {0}'.format(path))
        # remove
        os.remove(path)
    # return list of files
    return list_of_files

def main():
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # ----------------------------------------------------------------------
    # Perform resets
    # ----------------------------------------------------------------------
    reset_reduced_folders(p)
    reset_calibdb(p)
    # reset_log(p)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', DPROG, wmsg.format(DPROG))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================

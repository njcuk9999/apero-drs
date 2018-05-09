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
from __future__ import division
import os
import shutil
import glob
import sys

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
printc = spirouCore.PrintColour
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()


# =============================================================================
# Define functions
# =============================================================================
def reset_confirmation(called=False):

    # get the warning and error colours
    w1, w2 = printc('warning')
    e1, e2 = printc('error')
    # confirm reset
    print(w1 + '\nAre you sure you wish to reset the DRS?' + w2)
    print(w1 + '\tThis will remove all files in the reduced/calibDB '
          'directories' + w2)
    print(w1 + '\tIf you are sure you want to reset type "yes"\n' + w2)
    # user input
    if sys.version_info.major < 3:
        # noinspection PyUnresolvedReferences
        uinput = raw_input(e1 + 'Reset the DRS?\t' + e2)
    else:
        uinput = input(e1 + 'Reset the DRS?\t' + e2)

    if uinput.upper() != "YES" and (not called):
        print(e1 + '\nResetting DRS aborted.' + e2)
        # noinspection PyProtectedMember
        os._exit(0)


def reset_reduced_folders(p, log=True):

    # log progress
    WLOG('', DPROG, 'Resetting reduced directory')
    # remove files from reduced folder
    red_dir = p['DRS_DATA_REDUC']
    # loop around files and folders in calib_dir
    remove_all(red_dir, log)


def reset_calibdb(p, log=True):
    # TODO: eventually the calibDB should be reset to empty
    # TODO:    Thus this function will not be needed

    # log progress
    WLOG('', DPROG, 'Resetting calibration database')

    # remove files currently in calibDB
    calib_dir = p['DRS_CALIB_DB']
    # loop around files and folders in calib_dir
    remove_all(calib_dir, log)

    # -------------------------------------------------------------------------
    # get reset directory location
    # get package name and relative path
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.CDATA_REL_FOLDER()
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
            if log:
                wmsg = 'Adding file: {0} to {1}'
                WLOG('', DPROG, wmsg.format(f, p['DRS_CALIB_DB']))
            # remove the old file
            if os.path.exists(newpath):
                os.remove(newpath)
            # copy over the new file
            shutil.copy(oldpath, newpath)
        else:
            if log:
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


def remove_all(path, log=True):
    # loop around files and folders in calib_dir
    files = glob.glob(path + '/*')
    # loop around all files (adding all files from sub directories
    while len(files) > 0:
        f = files[0]
        files = remove(f, files, log)
        files.remove(f)


def remove(path, list_of_files, log=True):
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
        if log:
            WLOG('', DPROG, '    Removing file: {0}'.format(path))
        # remove
        os.remove(path)
    # return list of files
    return list_of_files


def main(return_locals=False, warn=True, log=True, called=False):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(quiet=log)
    # ----------------------------------------------------------------------
    # Perform resets
    # ----------------------------------------------------------------------
    if warn:
        reset_confirmation(called=called)
    reset_reduced_folders(p, log)
    reset_calibdb(p, log)
    # reset_log(p)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    if log:
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG('info', DPROG, wmsg.format(DPROG))
    # return a copy of locally defined variables in the memory
    if return_locals:
        return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main(return_locals=True)
    # exit message
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================

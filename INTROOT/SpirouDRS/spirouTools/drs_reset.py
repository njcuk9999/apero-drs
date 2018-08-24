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
def reset_confirmation(name, called=False):

    # get the warning and error colours
    w1, w2 = printc('warning')
    e1, e2 = printc('error')
    # confirm reset
    wargs = [w1, name, w2]
    print('{0}\nAre you sure you wish to reset the {1} directory?{2}'
          ''.format(*wargs))
    print('{0}\tIf you are sure you want to reset type "yes"\n{2}'
          ''.format(*wargs))
    # user input
    eargs = [e1, name, e2]

    if sys.version_info.major < 3:
        # noinspection PyUnresolvedReferences
        uinput = raw_input('{0}\tReset the {1} directory?\t{2}'.format(*eargs))
    else:
        uinput = input('{0}\tReset the {1} directory?\t{2}'.format(*eargs))
    # line break
    print('\n')

    if uinput.upper() != "YES" and (not called):
        return False
    elif uinput.upper() == "YES":
        return True
    else:
        return False


def custom_confirmation(messages, inputmessage, response='Y'):
    # line break
    print('\n')
    # get the warning and error colours
    w1, w2 = printc('warning')
    e1, e2 = printc('error')
    # confirm reset
    for message in messages:
        print('{0}{1}{2}'.format(w1, message, w2))
    # user input
    eargs = [e1, inputmessage, e2]

    if sys.version_info.major < 3:
        # noinspection PyUnresolvedReferences
        uinput = raw_input('{0}{1}{2}'.format(*eargs))
    else:
        uinput = input('{0}{1}{2}'.format(*eargs))
    # line break
    print('\n')

    if uinput.upper() == response.upper():
        return True
    else:
        return False


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
    relfolder = spirouConfig.Constants.RESET_CALIBDB_DIR()
    # get absolute folder path from package and relfolder
    absfolder = spirouConfig.GetAbsFolderPath(package, relfolder)
    # check that absfolder exists
    if not os.path.exists(absfolder):
        emsg = 'Error {0} directory does not exist'
        WLOG('error', DPROG, emsg.format(absfolder))
    # -------------------------------------------------------------------------
    # define needed files:
    files = os.listdir(absfolder)
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


def reset_telludb(p, log=True):
    # TODO: eventually the telluDB should be reset to empty
    # TODO:    Thus this function will not be needed

    # log progress
    WLOG('', DPROG, 'Resetting telluric database')

    # remove files currently in telluDB
    tellu_dir = p['DRS_TELLU_DB']

    # loop around files and folders in tellu_dir
    remove_all(tellu_dir, log)

    # -------------------------------------------------------------------------
    # get reset directory location
    # get package name and relative path
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.RESET_TELLUDB_DIR()
    # get absolute folder path from package and relfolder
    absfolder = spirouConfig.GetAbsFolderPath(package, relfolder)
    # check that absfolder exists
    if not os.path.exists(absfolder):
        emsg = 'Error {0} directory does not exist'
        WLOG('error', DPROG, emsg.format(absfolder))
    # -------------------------------------------------------------------------
    # define needed files:
    files = os.listdir(absfolder)
    # -------------------------------------------------------------------------
    # copy required telluDB files to DRS_TELLU_DB path
    for f in files:
        # get old and new paths
        oldpath = os.path.join(absfolder, f)
        newpath = os.path.join(tellu_dir, f)
        # check that old path exists
        if os.path.exists(oldpath):
            # log progress
            if log:
                wmsg = 'Adding file: {0} to {1}'
                WLOG('', DPROG, wmsg.format(f, p['DRS_TELLU_DB']))
            # remove the old file
            if os.path.exists(newpath):
                os.remove(newpath)
            # copy over the new file
            shutil.copy(oldpath, newpath)
        else:
            if log:
                wmsg = 'File {0} does not exists in {1} - cannot add'
                WLOG('warning', DPROG, wmsg.format(f, absfolder))


def reset_log(p):
    # log progress
    WLOG('', DPROG, 'Resetting log directory')
    # remove files from reduced folder
    log_dir = p['DRS_DATA_MSG']
    # loop around files and folders in reduced dir
    remove_all(log_dir)


def remove_all(path, log=True):

    # Check that directory exists
    if not os.path.exists(path):
        # get the warning and error colours
        e1, e2 = printc('error')
        eargs = [e1, path, e2]
        # display error and ask to create directory
        print('{0}\nError {0} directory does not exist. Should we create it?{2}'
              ''.format(*eargs))
        # user input
        if sys.version_info.major < 3:
            # noinspection PyUnresolvedReferences
            uinput = raw_input('{0}\tCreate directory {1}?\t{2}'.format(*eargs))
        else:
            uinput = input('{0}\tCreate directory {1}?\t{2}'.format(*eargs))
        # check user input
        if 'Y' in uinput.upper():
            # make directories
            os.makedirs(path)
        else:
            emsg = 'Error {0} directory does not exist'
            WLOG('error', DPROG, emsg.format(path))

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
    p = spirouStartup.Begin(recipe=__NAME__, quiet=log)
    # set log_opt
    p['LOG_OPT'] = __NAME__.split('.py')[0]
    p.set_source('LOG_OPT', __NAME__ + '.main()')
    # ----------------------------------------------------------------------
    # Perform resets
    # ----------------------------------------------------------------------
    reset1, reset2, reset3 = True, True, True
    if warn:
        reset1 = reset_confirmation('Reduced', called=called)
    if reset1:
        reset_reduced_folders(p, log)
    else:
        WLOG('', p['LOG_OPT'], 'Not resetting reduced folders.')
    if warn:
        reset2 = reset_confirmation('CalibDB', called=called)
    if reset2:
        reset_calibdb(p, log)
    else:
        WLOG('', p['LOG_OPT'], 'Not resetting CalibDB files.')
    if warn:
        reset3 = reset_confirmation('TelluDB', called=called)
    if reset3:
        reset_telludb(p, log)
    else:
        WLOG('', p['LOG_OPT'], 'Not resetting TelluDB files.')
    if warn:
        reset4 = reset_confirmation('Log', called=called)
    if reset4:
        reset_log(p)
    else:
        WLOG('', p['LOG_OPT'], 'Not resetting Log files.')
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    if log:
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG('info', __NAME__, wmsg.format(__NAME__))
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

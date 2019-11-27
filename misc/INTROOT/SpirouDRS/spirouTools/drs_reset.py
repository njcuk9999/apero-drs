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
# debug mode
DEBUG = False


# =============================================================================
# Define functions
# =============================================================================
def reset_confirmation(p, name, called=False):

    # get the warning and error colours
    w1, w2 = printc(p, 'warning')
    e1, e2 = printc(p, 'error')
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


def custom_confirmation(p, messages, inputmessage, response='Y'):
    # line break
    print('\n')
    # get the warning and error colours
    w1, w2 = printc(p, 'warning')
    e1, e2 = printc(p, 'error')
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


def reset_tmp_folders(p, log=True):
    # log progress
    WLOG(p, '', 'Resetting reduced directory')
    # remove files from reduced folder
    tmp_dir = p['DRS_DATA_WORKING']
    # loop around files and folders in calib_dir
    remove_all(p, tmp_dir, log)


def reset_reduced_folders(p, log=True):

    # log progress
    WLOG(p, '', 'Resetting reduced directory')
    # remove files from reduced folder
    red_dir = p['DRS_DATA_REDUC']
    # loop around files and folders in calib_dir
    remove_all(p, red_dir, log)


def reset_calibdb(p, log=True):
    # log progress
    WLOG(p, '', 'Resetting calibration database')

    # remove files currently in calibDB
    calib_dir = p['DRS_CALIB_DB']
    # loop around files and folders in calib_dir
    remove_all(p, calib_dir, log)

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
        WLOG(p, 'error', emsg.format(absfolder))
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
                WLOG(p, '', wmsg.format(f, p['DRS_CALIB_DB']))
            # remove the old file
            if os.path.exists(newpath):
                os.remove(newpath)
            # copy over the new file
            shutil.copy(oldpath, newpath)
        else:
            if log:
                wmsg = 'File {0} does not exists in {1} - cannot add'
                WLOG(p, 'warning', wmsg.format(f, absfolder))


def reset_telludb(p, log=True):
    # log progress
    WLOG(p, '', 'Resetting telluric database')

    # remove files currently in telluDB
    tellu_dir = p['DRS_TELLU_DB']

    # loop around files and folders in tellu_dir
    remove_all(p, tellu_dir, log)

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
        WLOG(p, 'error', emsg.format(absfolder))
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
                WLOG(p, '', wmsg.format(f, p['DRS_TELLU_DB']))
            # remove the old file
            if os.path.exists(newpath):
                os.remove(newpath)
            # copy over the new file
            shutil.copy(oldpath, newpath)
        else:
            if log:
                wmsg = 'File {0} does not exists in {1} - cannot add'
                WLOG(p, 'warning', wmsg.format(f, absfolder))


def reset_log(p):
    # log progress
    WLOG(p, '', 'Resetting log directory')
    # remove files from reduced folder
    log_dir = p['DRS_DATA_MSG']
    # get current log file (must be skipped)
    current_logfile = spirouConfig.Constants.LOG_FILE_NAME(p, p['DRS_DATA_MSG'])
    # loop around files and folders in reduced dir
    remove_all(p, log_dir, skipfiles=[current_logfile])


def reset_plot(p):
    # log progress
    WLOG(p, '', 'Resetting log directory')
    # remove files from reduced folder
    log_dir = p['DRS_DATA_PLOT']
    # loop around files and folders in reduced dir
    remove_all(p, log_dir)


def remove_all(p, path, log=True, skipfiles=None):

    if skipfiles is None:
        skipfiles = []

    # Check that directory exists
    if not os.path.exists(path):
        # get the warning and error colours
        e1, e2 = printc(p, 'error')
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
            WLOG(p, 'error', emsg.format(path))

    # loop around files and folders in calib_dir

    allfiles = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            allfiles.append(os.path.join(root, filename))

    # loop around all files (adding all files from sub directories
    for filename in allfiles:
        remove_files(p, filename, log, skipfiles)
    # remove dirs
    remove_subdirs(p, path, log, skipfiles)


def remove_subdirs(p, path, log=True, skipfiles=None):

    if skipfiles is None:
        skipfiles = []

    subdirs = glob.glob(os.path.join(path, '*'))

    for subdir in subdirs:
        if subdir in skipfiles:
            continue

        if os.path.islink(subdir):
            WLOG(p, '', '\tSkipping link: {0}'.format(subdir))
            continue
        if os.path.isfile(subdir):
            WLOG(p, '', '\tRemoving file: {0}'.format(subdir))
            # remove
            if DEBUG:
                print('\tRemoved {0}'.format(subdir))
            else:
                os.remove(subdir)
        if log:
            WLOG(p, '', '\tRemoving dir: {0}'.format(subdir))
        # remove
        if DEBUG:
            print('\tRemoved {0}'.format(subdir))
        else:
            shutil.rmtree(subdir)


def remove_files(p, path, log=True, skipfiles=None):
    """
    Remove a file or add files to list_of_files
    :param path: string, the path to remove (file or directory)
    :param list_of_files: list of strings, list of files
    :param log: bool, if True logs the removal of files

    :return list_of_files: returns the list of files removes (if it was a
            directory this adds the files to the list)
    """

    if skipfiles is None:
        skipfiles = []

    if path in skipfiles:
        return

    # log removal
    if log:
        WLOG(p, '', '\tRemoving file: {0}'.format(path))
    # remove
    if DEBUG:
        print('\tRemoved {0}'.format(path))
    else:
        os.remove(path)


def main(return_locals=False, warn=True, log=True, called=False):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__, quiet=log)
    # set log_opt
    p['LOG_OPT'] = __NAME__.split('.py')[0]
    p.set_source('LOG_OPT', __NAME__ + '.main()')
    # set DB_MAX_WAIT
    p['DB_MAX_WAIT'] = 3600
    # ----------------------------------------------------------------------
    # Perform resets
    # ----------------------------------------------------------------------
    reset1, reset2, reset3 = True, True, True
    reset4, reset5, reset6 = True, True, True

    if warn:
        reset1 = reset_confirmation(p, 'Tmp', called=called)
    if reset1:
        reset_tmp_folders(p, log)
    else:
        WLOG(p, '', 'Not resetting tmp folders.')
    if warn:
        reset2 = reset_confirmation(p, 'Reduced', called=called)
    if reset2:
        reset_reduced_folders(p, log)
    else:
        WLOG(p, '', 'Not resetting reduced folders.')
    if warn:
        reset3 = reset_confirmation(p, 'CalibDB', called=called)
    if reset3:
        reset_calibdb(p, log)
    else:
        WLOG(p, '', 'Not resetting CalibDB files.')
    if warn:
        reset4 = reset_confirmation(p, 'TelluDB', called=called)
    if reset4:
        reset_telludb(p, log)
    else:
        WLOG(p, '', 'Not resetting TelluDB files.')
    if warn:
        reset5 = reset_confirmation(p, 'Log', called=called)
    if reset5:
        reset_log(p)
    if warn:
        reset6 = reset_confirmation(p, 'Plot', called=called)
    if reset6:
        reset_plot(p)
    else:
        WLOG(p, '', 'Not resetting Log files.')
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    if log:
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG(p, 'info', wmsg.format(__NAME__))
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

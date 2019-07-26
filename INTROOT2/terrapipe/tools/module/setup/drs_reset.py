#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-07 at 15:22

@author: cook
"""
from __future__ import division
import os
import shutil
import glob
import sys

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'setup.drs_reset.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict



# =============================================================================
# Define functions
# =============================================================================
def reset_confirmation(params, name, called=False):

    # get the warning and error colours
    w1, w2 = printc(p, 'warning')
    e1, e2 = printc(p, 'error')
    # confirm reset
    wargs = [w1, name, w2]

    WLOG(params, '', TextEntry(''))

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



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

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

from apero import core
from apero.core import drs_log
from apero import locale
from apero.core import constants
from apero.io import drs_data

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
# debug mode (test)
DEBUG = False


# =============================================================================
# Define functions
# =============================================================================
def is_empty(directory):
    if os.path.exists(directory):
        files = os.listdir(directory)
        if len(files) == 0:
            return True
    return False


def reset_confirmation(params, name, directory=None):
    # ----------------------------------------------------------------------
    if directory is not None:
        # test if empty
        empty = is_empty(params['DRS_DATA_WORKING'])
        if empty:
            return True
    # ----------------------------------------------------------------------
    # get the text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # ----------------------------------------------------------------------
    # Ask if user wants to reset
    WLOG(params, '', TextEntry('40-502-00001', args=[name]), colour='yellow')
    if directory is not None:
        WLOG(params, '', '\t({0})'.format(directory), colour='yellow')
    # ----------------------------------------------------------------------
    # line break
    print('\n')
    # user input
    if sys.version_info.major < 3:
        # noinspection PyUnresolvedReferences
        uinput = raw_input(textdict['40-502-00002'].format(name))
    else:
        uinput = input(textdict['40-502-00002'].format(name))
    # line break
    print('\n')
    # ----------------------------------------------------------------------
    # deal with user input
    if uinput.upper() == "YES":
        return True
    else:
        return False


def reset_tmp_folders(params, log=True):
    # log progress
    WLOG(params, '', TextEntry('40-502-00003', args=['tmp']))
    # remove files from reduced folder
    tmp_dir = params['DRS_DATA_WORKING']
    # loop around files and folders in calib_dir
    remove_all(params, tmp_dir, log)


def reset_reduced_folders(params, log=True):
    # log progress
    WLOG(params, '', TextEntry('40-502-00003', args=['reduced']))
    # remove files from reduced folder
    red_dir = params['DRS_DATA_REDUC']
    # loop around files and folders in calib_dir
    remove_all(params, red_dir, log)


def reset_calibdb(params, log=True):
    """
    Wrapper for reset_dbdir - specifically for calibdb
    :param params:
    :param log:
    :return:
    """
    name = 'calibration database'
    calib_dir = params['DRS_CALIB_DB']
    reset_path = params['DRS_RESET_CALIBDB_PATH']
    reset_dbdir(params, name, calib_dir, reset_path, log=log)


def reset_telludb(params, log=True):
    """
    Wrapper for reset_dbdir - specifically for calibdb
    :param params:
    :param log:
    :return:
    """
    name = 'tellruic database'
    tellu_dir = params['DRS_TELLU_DB']
    reset_path = params['DRS_RESET_TELLUDB_PATH']
    reset_dbdir(params, name, tellu_dir, reset_path, log=log)


def reset_dbdir(params, name, db_dir, reset_path, log=True):
    # log progress
    WLOG(params, '', TextEntry('40-502-00003', args=[name]))
    # loop around files and folders in calib_dir
    remove_all(params, db_dir, log)
    # copy default data back
    copy_default_db(params, name, db_dir, reset_path, log)


def copy_default_db(params, name, db_dir, reset_path, log=True):
    # -------------------------------------------------------------------------
    # get reset directory location
    # -------------------------------------------------------------------------
    # get absolute folder path from package and relfolder
    absfolder = drs_data.construct_path(params, directory=reset_path)
    # check that absfolder exists
    if not os.path.exists(absfolder):
        eargs = [name, absfolder]
        WLOG(params, 'error', TextEntry('00-502-00001', args=eargs))
    # -------------------------------------------------------------------------
    # define needed files:
    files = os.listdir(absfolder)
    # -------------------------------------------------------------------------
    # copy required calibDB files to DRS_CALIB_DB path
    for filename in files:
        # get old and new paths
        oldpath = os.path.join(absfolder, filename)
        newpath = os.path.join(db_dir, filename)
        # check that old path exists
        if os.path.exists(oldpath):
            # log progress
            if log:
                wargs = [filename, db_dir]
                WLOG(params, '', TextEntry('40-502-00007', args=wargs))
            # remove the old file
            if os.path.exists(newpath):
                os.remove(newpath)
            # copy over the new file
            shutil.copy(oldpath, newpath)
        else:
            if log:
                wargs = [filename, absfolder]
                WLOG(params, 'warning', TextEntry('10-502-00001', args=wargs))


def reset_log(params):
    # log progress
    WLOG(params, '', TextEntry('40-502-00003', args=['log']))
    # remove files from reduced folder
    log_dir = params['DRS_DATA_MSG']
    # get current log file (must be skipped)
    current_logfile = drs_log.get_logfilepath(WLOG, params)
    # loop around files and folders in reduced dir
    remove_all(params, log_dir, skipfiles=[current_logfile])


def reset_plot(params):
    # log progress
    WLOG(params, '', TextEntry('40-502-00003', args=['plot']))
    # remove files from reduced folder
    plot_dir = params['DRS_DATA_PLOT']
    # loop around files and folders in reduced dir
    remove_all(params, plot_dir)


def remove_all(params, path, log=True, skipfiles=None):
    # get the text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # deal with no skipfiles being defined
    if skipfiles is None:
        skipfiles = []
    # Check that directory exists
    if not os.path.exists(path):
        # display error and ask to create directory
        WLOG(params, 'warning', TextEntry('40-502-00005', args=[path]))
        # user input
        if sys.version_info.major < 3:
            # noinspection PyUnresolvedReferences
            uinput = raw_input(textdict['40-502-00006'].format(path))
        else:
            uinput = input(textdict['40-502-00006'].format(path))
        # check user input
        if 'Y' in uinput.upper():
            # make directories
            os.makedirs(path)
        else:
            WLOG(params, 'error', TextEntry('00-502-00002', args=[path]))
    # loop around files and folders in calib_dir
    allfiles = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            allfiles.append(os.path.join(root, filename))
    # loop around all files (adding all files from sub directories
    for filename in allfiles:
        remove_files(params, filename, log, skipfiles)
    # remove dirs
    remove_subdirs(params, path, log, skipfiles)


def remove_subdirs(params, path, log=True, skipfiles=None):
    # deal with no skip files
    if skipfiles is None:
        skipfiles = []
    # get all sub-directories within path
    subdirs = glob.glob(os.path.join(path, '*'))
    # loop around each sub directory
    for subdir in subdirs:
        # if in skip files then skip
        if subdir in skipfiles:
            continue
        # if path is link skip
        if os.path.islink(subdir):
            WLOG(params, '', TextEntry('40-502-00008', args=[subdir]))
            continue
        # if path is file delete file
        if os.path.isfile(subdir):
            WLOG(params, '', TextEntry('40-502-00009', args=[subdir]))
            # if debug just print that we are removing file
            if DEBUG:
                if not log:
                    WLOG(params, '', TextEntry('40-502-00009', args=[subdir]))
            # remove file
            else:
                os.remove(subdir)
        # if there is no file remove tree of empty directories
        if log:
            WLOG(params, '', TextEntry('40-502-00010', args=[subdir]))
        # if debug just print that we are removing file
        if DEBUG:
            print('\t\tRemoved {0}'.format(subdir))
        # remove directories
        else:
            shutil.rmtree(subdir)


def remove_files(params, path, log=True, skipfiles=None):
    """
    Remove a file or add files to list_of_files
    :param path: string, the path to remove (file or directory)
    :param list_of_files: list of strings, list of files
    :param log: bool, if True logs the removal of files

    :return list_of_files: returns the list of files removes (if it was a
            directory this adds the files to the list)
    """
    # deal with no skipped files
    if skipfiles is None:
        skipfiles = []
    # if we have a skipped file skip removing
    if path in skipfiles:
        return
    # log removal
    if log:
        WLOG(params, '', TextEntry('40-502-00004', args=[path]))
    # if in debug mode just log
    if DEBUG:
        print('\t\tRemoved {0}'.format(path))
    # else remove file
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

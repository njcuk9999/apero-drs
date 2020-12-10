#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-07 at 15:22

@author: cook
"""
import glob
import os
import sys

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero import lang
from apero.io import drs_lock
from apero.io import drs_path
from apero.core.utils import drs_data
from apero.tools.module.database import manage_databases

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.setup.drs_reset.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# debug mode (test)
DEBUG = False


# =============================================================================
# Define functions
# =============================================================================
def is_empty(directory, exclude_files=None):
    if os.path.exists(directory):
        # get a raw list of files
        rawfiles = glob.glob(os.path.join(directory, '**'), recursive=True)
        # deal with excluded files
        if exclude_files is not None:
            files = []
            for rawfile in rawfiles:
                if rawfile not in exclude_files:
                    files.append(rawfile)
        else:
            files = list(rawfiles)
        # exclude directories
        files1 = []
        for file1 in files:
            if not os.path.isdir(file1):
                files1.append(file1)
        if len(files1) == 0:
            return True

    return False


def reset_title(params, name):
    # blank lines
    print()
    print()
    WLOG(params, 'info', '='*50)
    WLOG(params, 'info', textentry('40-502-00012', args=[name]))
    WLOG(params, 'info', '='*50)


def reset_confirmation(params, name, directory=None,
                       exclude_files=None):
    # ----------------------------------------------------------------------
    if directory is not None:
        # test if empty
        empty = is_empty(directory, exclude_files)
        if empty:
            WLOG(params, '', textentry('40-502-00011'))
            return True
    # ----------------------------------------------------------------------
    # Ask if user wants to reset
    WLOG(params, '', textentry('40-502-00001', args=[name]),
         colour='yellow')
    if directory is not None:
        WLOG(params, '', '\t({0})'.format(directory), colour='yellow')
    # ----------------------------------------------------------------------
    # line break
    print('\n')
    # user input
    if sys.version_info.major < 3:
        # noinspection PyUnresolvedReferences
        uinput = raw_input(textentry('40-502-00002', args=name))
    else:
        uinput = input(textentry('40-502-00002', args=name))
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
    WLOG(params, '', textentry('40-502-00003', args=['tmp']))
    # remove files from reduced folder
    tmp_dir = params['DRS_DATA_WORKING']
    # loop around files and folders in calib_dir
    remove_all(params, tmp_dir, log)
    # remake path
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)


def reset_reduced_folders(params, log=True):
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=['reduced']))
    # remove files from reduced folder
    red_dir = params['DRS_DATA_REDUC']
    # loop around files and folders in calib_dir
    remove_all(params, red_dir, log)
    # remake path
    if not os.path.exists(red_dir):
        os.makedirs(red_dir)


def reset_calibdb(params, log=True):
    """
    Wrapper for reset_dbdir - specifically for calibdb
    :param params:
    :param log:
    :return:
    """
    # get database paths
    databases = manage_databases.list_databases(params)
    # load pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # name the database
    name = 'calibration database'
    # get the calibration database file directory
    calib_dir = params['DRS_CALIB_DB']
    # get the reset path
    reset_path = params['DRS_RESET_CALIBDB_PATH']
    # reset files
    reset_dbdir(params, name, calib_dir, reset_path, log=log)
    # create calibration database
    manage_databases.create_calibration_database(params, pconst, databases)


def reset_telludb(params, log=True):
    """
    Wrapper for reset_dbdir - specifically for calibdb
    :param params:
    :param log:
    :return:
    """
    # get database paths
    databases = manage_databases.list_databases(params)
    # load pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # name the database
    name = 'tellruic database'
    # get the telluric database file directory
    tellu_dir = params['DRS_TELLU_DB']
    # get the reset path
    reset_path = params['DRS_RESET_TELLUDB_PATH']
    # reset files
    reset_dbdir(params, name, tellu_dir, reset_path, log=log)
    # create telluric database
    manage_databases.create_telluric_database(pconst, databases)


def reset_dbdir(params, name, db_dir, reset_path, log=True,
                empty_first=True, relative_path=None):
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=[name]))
    # loop around files and folders in calib_dir
    if empty_first:
        remove_all(params, db_dir, log)
    # remake path
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    # construct relative path if None given
    if relative_path is None:
        reset_path = os.path.join(params['DRS_DATA_ASSETS'], reset_path)
    else:
        reset_path = os.path.abspath(reset_path)
    # copy default data back
    copy_default_db(params, name, db_dir, reset_path)


def copy_default_db(params, name, db_dir, reset_path):
    # -------------------------------------------------------------------------
    # get reset directory location
    # -------------------------------------------------------------------------
    # check that absfolder exists
    if not os.path.exists(reset_path):
        eargs = [name, reset_path]
        WLOG(params, 'error', textentry('00-502-00001', args=eargs))
    # -------------------------------------------------------------------------
    # copy required calibDB files to DRS_CALIB_DB path
    drs_path.copytree(reset_path, db_dir)


def reset_log(params, exclude_files=None, log=True):
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=['log']))
    # remove files from reduced folder
    log_dir = params['DRS_DATA_MSG']
    # get current log file (must be skipped)
    current_logfile = drs_log.get_logfilepath(WLOG, params)
    # deal with no exclude files
    if exclude_files is None:
        exclude_files = []
    # deal with current log file not in exclude files
    if current_logfile not in exclude_files:
        exclude_files.append(current_logfile)
    # loop around files and folders in reduced dir
    remove_all(params, log_dir, skipfiles=exclude_files, log=log)
    # remake path
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


def reset_plot(params, log=True):
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=['plot']))
    # remove files from reduced folder
    plot_dir = params['DRS_DATA_PLOT']
    # loop around files and folders in reduced dir
    remove_all(params, plot_dir, log=log)
    # remake path
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)


def reset_run(params, log=True):
    name = 'run files'
    run_dir = params['DRS_DATA_RUN']
    reset_path = params['DRS_RESET_RUN_PATH']
    # loop around files and folders in reduced dir
    reset_dbdir(params, name, run_dir, reset_path, log=log, empty_first=False)


def reset_assets(params, log=True):
    name = 'assets'
    # get database paths
    databases = manage_databases.list_databases(params)
    # load pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # TODO: deal with getting online
    asset_path = params['DRS_DATA_ASSETS']
    reset_path = os.path.join(params['DRS_RESET_ASSETS_PATH'],
                              params['INSTRUMENT'].lower())
    # get reset_path from apero module dir
    abs_reset_path = drs_data.construct_path(params, '', reset_path)

    # loop around files and folders in reduced dir
    reset_dbdir(params, name, asset_path, abs_reset_path, log=log,
                empty_first=False, relative_path='MODULE')
    # create index database
    manage_databases.create_index_database(pconst, databases)
    # create log database
    manage_databases.create_log_database(pconst, databases)
    # create object database
    manage_databases.create_object_database(params, pconst, databases)
    # create params database
    # manage_databases.create_params_database(pconst, databases)
    # create language database
    manage_databases.create_lang_database(databases)


def remove_all(params, path, log=True, skipfiles=None):
    # deal with no skipfiles being defined
    if skipfiles is None:
        skipfiles = []
    # Check that directory exists
    if not os.path.exists(path):
        # display error and ask to create directory
        WLOG(params, 'warning', textentry('40-502-00005', args=[path]))
        # user input
        if sys.version_info.major < 3:
            # noinspection PyUnresolvedReferences
            uinput = raw_input(textentry('40-502-00006', args=path))
        else:
            uinput = input(textentry('40-502-00006', args=path))
        # check user input
        if 'Y' in uinput.upper():
            # make directories
            os.makedirs(path)
        else:
            WLOG(params, 'error', textentry('00-502-00002', args=[path]))
    # loop around files and folders in calib_dir
    allfiles = []
    for root, dirs, files in os.walk(path, followlinks=True):
        for filename in files:
            allfiles.append(os.path.join(root, filename))
    # loop around all files (adding all files from sub directories
    for filename in allfiles:
        remove_files(params, filename, log, skipfiles)
    # remove dirs
    drs_lock.__remove_empty__(params, path, log=True, remove_head=False)


def remove_files(params, path, log=True, skipfiles=None):
    """
    Remove a file or add files to list_of_files

    :param params: ParamDict, the parameter dictionary of constants
    :param path: string, the path to remove (file or directory)
    :param log: bool, if True logs the removal of files
    :param skipfiles:

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
        WLOG(params, '', textentry('40-502-00004', args=[path]))
    # if in debug mode just log
    if DEBUG:
        WLOG(params, '', '\t\tRemoved {0}'.format(path))
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

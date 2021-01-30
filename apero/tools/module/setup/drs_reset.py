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
from typing import Dict, List, Union

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.instruments.default import pseudo_const
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
# get param dict
ParamDict = constants.ParamDict
PseudoConst = pseudo_const.PseudoConstants
DatabaseM = drs_database.DatabaseManager
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# debug mode (test)
DEBUG = False


# =============================================================================
# Define functions
# =============================================================================
def is_empty(directory: str,
             exclude_files: Union[List[str], None] = None) -> bool:
    """
    Find whether a directory is empty (exluding files is "exclude_files" is set)

    :param directory: str, the directory to check
    :param exclude_files: list or strings or None - the files to exlucde from
                          a directory
    :return: bool, True if empty or False otherwise
    """
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


def reset_title(params: ParamDict, name: str):
    """
    print / log the reset title

    :param params: ParamDict, parameter dictionary of constants
    :param name: str, the name to add to the reset title

    :return: None just prints / logs
    """
    # blank lines
    print()
    print()
    WLOG(params, 'info', '='*50)
    WLOG(params, 'info', textentry('40-502-00012', args=[name]))
    WLOG(params, 'info', '='*50)


def reset_confirmation(params: ParamDict, name: str,
                       directory: Union[str, None] = None,
                       exclude_files: Union[List[str], None] = None) -> bool:
    """
    Ask the user to confirm they want to reset this "name"

    :param params: ParamDict, parameter dictionary of constants
    :param name: str, the name of the reset parameter
    :param directory: str or None - the directory we would reset
    :param exclude_files: list of strings or None - if set the list of files
                          to exclude
    :return: bool, True if we should reset, False otherwise
    """
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


def reset_tmp_folders(params: ParamDict, log: bool = True):
    """
    Reset the "tmp" (preprocessed directories)

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal

    :return: None - resets tmp (preprocessed) directory
    """
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=['tmp']))
    # remove files from reduced folder
    tmp_dir = params['DRS_DATA_WORKING']
    # loop around files and folders in calib_dir
    remove_all(params, tmp_dir, log)
    # remake path
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    # -------------------------------------------------------------------------
    # remove entries from index database
    # -------------------------------------------------------------------------
    # get index database
    indexdb = drs_database.IndexDatabase(params)
    # load index database
    indexdb.load_db()
    # check that table is in database
    if not indexdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload(params['INSTRUMENT'])
        # create index database
        manage_databases.create_index_database(pconst, databases)
        # get index database
        indexdb = drs_database.IndexDatabase(params)
        # load index database
        indexdb.load_db()
    # set up condition
    condition = 'KIND="tmp"'
    # remove entries
    indexdb.remove_entries(condition=condition)
    # -------------------------------------------------------------------------
    # remove entries from log database
    # -------------------------------------------------------------------------
    # get log database
    logdb = drs_database.LogDatabase(params)
    # load index database
    logdb.load_db()
    # check that table is in database
    if not logdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload(params['INSTRUMENT'])
        # create index database
        manage_databases.create_log_database(pconst, databases)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'RTYPE="tmp"'
    # remove entries
    logdb.remove_entries(condition=condition)


def reset_reduced_folders(params: ParamDict, log: bool = True):
    """
    Resets the reduced directory

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal

    :return: None - resets reduced directory
    """
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=['reduced']))
    # remove files from reduced folder
    red_dir = params['DRS_DATA_REDUC']
    # loop around files and folders in calib_dir
    remove_all(params, red_dir, log)
    # remake path
    if not os.path.exists(red_dir):
        os.makedirs(red_dir)
    # -------------------------------------------------------------------------
    # remove entries from index database
    # -------------------------------------------------------------------------
    # get index database
    indexdb = drs_database.IndexDatabase(params)
    # load index database
    indexdb.load_db()
    # check that table is in database
    if not indexdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload(params['INSTRUMENT'])
        # create index database
        manage_databases.create_index_database(pconst, databases)
        # get index database
        indexdb = drs_database.IndexDatabase(params)
        # load index database
        indexdb.load_db()
    # set up condition
    condition = 'KIND="red"'
    # remove entries
    indexdb.remove_entries(condition=condition)
    # -------------------------------------------------------------------------
    # remove entries from log database
    # -------------------------------------------------------------------------
    # get log database
    logdb = drs_database.LogDatabase(params)
    # load index database
    logdb.load_db()
    # check that table is in database
    if not logdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload(params['INSTRUMENT'])
        # create index database
        manage_databases.create_log_database(pconst, databases)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'RTYPE="red"'
    # remove entries
    logdb.remove_entries(condition=condition)


def reset_calibdb(params: ParamDict, log: bool = True):
    """
    Wrapper for reset_dbdir - specifically for calibDB

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal

    :return: None - resets telluDB
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
    # -------------------------------------------------------------------------
    # remove entries from calibration database
    # -------------------------------------------------------------------------
    calibdb = drs_database.CalibrationDatabase(params)
    # load index database
    calibdb.load_db()
    # set up condition
    condition = 'UNIXTIME != 0'
    # remove entries
    calibdb.remove_entries(condition=condition)


def reset_telludb(params: ParamDict, log: bool = True):
    """
    Wrapper for reset_dbdir - specifically for telluDB

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal

    :return: None - resets telluDB
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
    # -------------------------------------------------------------------------
    # remove entries from telluric database
    # -------------------------------------------------------------------------
    telludb = drs_database.TelluricDatabase(params)
    # load index database
    telludb.load_db()
    # set up condition
    condition = 'UNIXTIME != 0'
    # remove entries
    telludb.remove_entries(condition=condition)


def reset_dbdir(params: ParamDict, name: str, db_dir: str,
                reset_path: str, log: bool = True,
                empty_first: bool = True,
                relative_path: Union[str, None] = None):
    """
    Resets a database file directory (i.e. calibDB or telluDB)

    :param params: ParamDict, the parameter dictionary of constants
    :param name: str, the name of the database file directory
    :param db_dir: str, the database file directory path
    :param reset_path: str, the reset path for file directory
    :param log: bool, if True logs the removal
    :param empty_first: bool, if True deletes contents first
    :param relative_path: str or None if set this mean the reset path is inside
                          the ASSETS directory

    :return: None copys files to database file directory
    """
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


def copy_default_db(params: ParamDict, name: str, db_dir: str,
                    reset_path: str):
    """
    Copies reset files to a database file directory (i.e. calibDB or telluDB)

    :param params: ParamDict, the parameter dictionary of constants
    :param name: str, the name of the database file directory
    :param db_dir: str, the database file directory path
    :param reset_path: str, the reset path for file directory

    :return: None - copied reset files into database file directory
    """
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


def reset_log(params: ParamDict, exclude_files: Union[List[str], None] = None,
              log: bool = True):
    """
    Resets the plot directory

    :param params: ParamDict, the parameter dictionary of constants
    :param exclude_files: list of strings or None, if set files to exclude from
                          reset
    :param log: boo, if True logs resetting

    :return: None, resets log directory
    """
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


def reset_plot(params: ParamDict, log: bool = True):
    """
    Resets the plot directory

    :param params: ParamDict, the parameter dictionary of constants
    :param log: boo, if True logs resetting

    :return: None, resets plot directory
    """
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=['plot']))
    # remove files from reduced folder
    plot_dir = params['DRS_DATA_PLOT']
    # loop around files and folders in reduced dir
    remove_all(params, plot_dir, log=log)
    # remake path
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)


def reset_run(params: ParamDict, log: bool = True):
    """
    Resets the run directory (but does not empty first)

    :param params: ParamDict, the parameter dictionary of constants
    :param log: boo, if True logs resetting

    :return: None, resets run directory
    """
    name = 'run files'
    run_dir = params['DRS_DATA_RUN']
    reset_path = params['DRS_RESET_RUN_PATH']
    # loop around files and folders in reduced dir
    reset_dbdir(params, name, run_dir, reset_path, log=log, empty_first=False)


def reset_assets(params: ParamDict, log: bool = True):
    """
    Reset the Assets directory (including re-creating databases)

    :param params: ParamDict, parameter dictionary of constants
    :param log: bool - if True logs process

    :return: None - resets assets dir and databases
    """
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

    # loop around files and folders in assets dir
    reset_dbdir(params, name, asset_path, abs_reset_path, log=log,
                empty_first=False, relative_path='MODULE')
    # create index databases
    manage_databases.create_index_database(pconst, databases)
    # create log database
    manage_databases.create_log_database(pconst, databases)
    # create object database
    manage_databases.create_object_database(params, pconst, databases)
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

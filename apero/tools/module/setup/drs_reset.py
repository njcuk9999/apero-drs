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
import shutil
import sys
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from astropy.table import Table

from apero.base import base
from apero.core.base.drs_base_classes import Printer
from apero.core.constants import param_functions
from apero.core.constants import load_functions
from apero.core import lang
from apero.core.constants import path_definitions
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.instruments.default import instrument as instrument_mod
from apero.core.utils import drs_data
from apero.io import drs_lock
from apero.io import drs_path
from apero.tools.module.database import manage_databases
from apero.tools.module.setup import drs_assets

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
ParamDict = param_functions.ParamDict
Instrument = instrument_mod.Instrument
DatabaseM = drs_database.DatabaseManager
# Get Logging function
WLOG = drs_log.wlog
TLOG = Printer
# Get the text types
textentry = lang.textentry
# debug mode (test)
DEBUG = False


# =============================================================================
# Define reset functions
# =============================================================================
def check_cwd(params: ParamDict):
    """
    Check whether we are currently in a block path

    :param params: ParamDict, parameter dictioary of constnats

    :return: None, raises error if currently in a block path
    """
    # get current working directory
    cwd = os.getcwd()
    # get block definitions
    blocks = path_definitions.BLOCKS
    # loop around blocks and check path
    for block in blocks:
        # get this blocks path
        block_path = block(params).path
        # if it is in current working path we have a problem
        if str(os.path.realpath(block_path)) in str(os.path.realpath(cwd)):
            # raise error
            emsg = ('Current working directory within paths to be reset. '
                    'Please change directory\n\tCurrent dir: {0}\n\tBlock: {1}')
            eargs = [cwd, block_path]
            WLOG(params, 'error', emsg.format(*eargs))


def is_empty(params: ParamDict, directory: str,
             exclude_files: Union[List[str], None] = None) -> bool:
    """
    Find whether a directory is empty (exluding files is "exclude_files" is set)

    :param params: ParamDict, parameter dictionary of constants
    :param directory: str, the directory to check
    :param exclude_files: list or strings or None - the files to exlucde from
                          a directory

    :return: bool, True if empty or False otherwise
    """
    if os.path.exists(directory):
        # get a raw list of files
        rawfiles = []
        for root, dirs, files in os.walk(os.path.join(directory)):
            # give root dir
            TLOG(params, '', f'Processing {root}...')
            # deal with excluded files
            if exclude_files is not None:
                for rawfile in files:
                    if rawfile not in exclude_files:
                        rawfiles.append(os.path.join(root, rawfile))
            else:
                for rawfile in files:
                    rawfiles.append(os.path.join(root, rawfile))
        # exclude directories
        files1 = []
        for file1 in rawfiles:
            if not os.path.isdir(file1):
                files1.append(file1)
        if len(files1) == 0:
            # clear loading message
            TLOG(params, '', '')
            # empty
            return True

    # clear loading message
    TLOG(params, '', '')
    # not empty
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
    WLOG(params, 'info', '=' * 50)
    WLOG(params, 'info', textentry('40-502-00012', args=[name]))
    WLOG(params, 'info', '=' * 50)


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
        empty = is_empty(params, directory, exclude_files)
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
    findexdb = drs_database.FileIndexDatabase(params)
    # load index database
    findexdb.load_db()
    # check that table is in database
    if not findexdb.database.has_table(findexdb.database.tablename):
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = load_functions.load_pconfig()
        # create index database
        manage_databases.create_fileindex_database(params, pconst, databases)
        # get index database
        findexdb = drs_database.FileIndexDatabase(params)
        # load index database
        findexdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="tmp"'
    # remove entries
    findexdb.remove_entries(condition=condition)
    # -------------------------------------------------------------------------
    # remove entries from log database
    # -------------------------------------------------------------------------
    # get log database
    logdb = drs_database.LogDatabase(params)
    # load index database
    logdb.load_db()
    # check that table is in database
    if not logdb.database.has_table(logdb.database.tablename):
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = load_functions.load_pconfig()
        # create index database
        manage_databases.create_log_database(params, pconst, databases)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="tmp"'
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
    indexdb = drs_database.FileIndexDatabase(params)
    # load index database
    indexdb.load_db()
    # check that table is in database
    if not indexdb.database.has_table(indexdb.database.tablename):
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = load_functions.load_pconfig()
        # create index database
        manage_databases.create_fileindex_database(params, pconst, databases)
        # get index database
        indexdb = drs_database.FileIndexDatabase(params)
        # load index database
        indexdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="red"'
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
    if not logdb.database.has_table(logdb.database.tablename):
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = load_functions.load_pconfig()
        # create index database
        manage_databases.create_log_database(params, pconst, databases)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="red"'
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
    pconst = load_functions.load_pconfig()
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
    pconst = load_functions.load_pconfig()
    # name the database
    name = 'tellruic database'
    # get the telluric database file directory
    tellu_dir = params['DRS_TELLU_DB']
    # get the reset path
    reset_path = params['DRS_RESET_TELLUDB_PATH']
    # reset files
    reset_dbdir(params, name, tellu_dir, reset_path, log=log)
    # create telluric database
    manage_databases.create_telluric_database(params, pconst, databases)
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
                relative_path: Union[str, None] = None,
                backup: bool = False):
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
    :param backup: bool, if True we backup the files to a sub-directory
                   before resetting (only if files wouldn't have been
                   originally overwritten)

    :return: None copys files to database file directory
    """
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=[name]))
    # construct relative path if None given
    if relative_path is None:
        reset_path = os.path.join(params['DRS_DATA_ASSETS'], reset_path)
    else:
        reset_path = os.path.abspath(reset_path)
    # loop around files and folders in calib_dir
    if backup:
        # find files that aren't common between reset_path we backup
        # then we remove all
        backup_all_diff(params, reset_path, db_dir)

    elif empty_first:
        remove_all(params, db_dir, log)
    # remake path
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
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


def reset_lbl_folders(params: ParamDict, log: bool = True):
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=['lbl']))
    # remove files from reduced folder
    lbl_dir = params['LBL_PATH']
    # loop around files and folders in reduced dir
    remove_all(params, lbl_dir, log=log)
    # remake path
    if not os.path.exists(lbl_dir):
        os.makedirs(lbl_dir)
    # -------------------------------------------------------------------------
    # remove entries from index database
    # -------------------------------------------------------------------------
    # get index database
    findexdb = drs_database.FileIndexDatabase(params)
    # load index database
    findexdb.load_db()
    # check that table is in database
    if not findexdb.database.has_table(findexdb.database.tablename):
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = load_functions.load_pconfig()
        # create index database
        manage_databases.create_fileindex_database(params, pconst, databases)
        # get index database
        indexdb = drs_database.FileIndexDatabase(params)
        # load index database
        indexdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="lbl"'
    # remove entries
    findexdb.remove_entries(condition=condition)
    # -------------------------------------------------------------------------
    # remove entries from log database
    # -------------------------------------------------------------------------
    # get log database
    logdb = drs_database.LogDatabase(params)
    # load index database
    logdb.load_db()
    # check that table is in database
    if not logdb.database.has_table(logdb.database.tablename):
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = load_functions.load_pconfig()
        # create index database
        manage_databases.create_log_database(params, pconst, databases)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="lbl"'
    # remove entries
    logdb.remove_entries(condition=condition)


def reset_out_folders(params: ParamDict, log: bool = True):
    """
    Resets the reduced directory

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal

    :return: None - resets reduced directory
    """
    # log progress
    WLOG(params, '', textentry('40-502-00003', args=['out']))
    # remove files from reduced folder
    red_dir = params['DRS_DATA_OUT']
    # loop around files and folders in calib_dir
    remove_all(params, red_dir, log)
    # remake path
    if not os.path.exists(red_dir):
        os.makedirs(red_dir)
    # -------------------------------------------------------------------------
    # remove entries from index database
    # -------------------------------------------------------------------------
    # get index database
    findexdb = drs_database.FileIndexDatabase(params)
    # load index database
    findexdb.load_db()
    # check that table is in database
    if not findexdb.database.has_table(findexdb.database.tablename):
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = load_functions.load_pconfig()
        # create index database
        manage_databases.create_fileindex_database(params, pconst, databases)
        # get index database
        findexdb = drs_database.FileIndexDatabase(params)
        # load index database
        findexdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="out"'
    # remove entries
    findexdb.remove_entries(condition=condition)
    # -------------------------------------------------------------------------
    # remove entries from log database
    # -------------------------------------------------------------------------
    # get log database
    logdb = drs_database.LogDatabase(params)
    # load index database
    logdb.load_db()
    # check that table is in database
    if not logdb.database.has_table(logdb.database.tablename):
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = load_functions.load_pconfig()
        # create index database
        manage_databases.create_log_database(params, pconst, databases)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="out"'
    # remove entries
    logdb.remove_entries(condition=condition)


def reset_assets(params: ParamDict, log: bool = True, reset_dbs: bool = True):
    """
    Reset the Assets directory (including re-creating databases)

    :param params: ParamDict, parameter dictionary of constants
    :param log: bool - if True logs process
    :param reset_dbs: bool - if True resets all databases

    :return: None - resets assets dir and databases
    """
    name = 'assets'
    # get database paths
    databases = manage_databases.list_databases(params)

    # now check whether we need to download the assets
    update_assets = drs_assets.check_local_assets(params)
    if update_assets:
        drs_assets.update_local_assets(params)

    # load pseudo constants
    pconst = load_functions.load_pconfig()
    # TODO: deal with getting online
    asset_path1 = params['DRS_DATA_ASSETS']
    reset_path1 = os.path.join(params['DRS_RESET_ASSETS_PATH'],
                               params['INSTRUMENT'].lower())
    asset_path2 = os.path.join(params['DRS_DATA_ASSETS'], 'core')
    reset_path2 = os.path.join(params['DRS_RESET_ASSETS_PATH'], 'core')
    # get reset_path from apero module dir
    abs_reset_path1 = drs_data.construct_path(params, '', str(reset_path1))
    abs_reset_path2 = drs_data.construct_path(params, '', str(reset_path2))
    # loop around files and folders in assets dir
    #   we want to backup any new files the user as copied
    #   i.e. new masks etc
    reset_dbdir(params, name, asset_path1, abs_reset_path1, log=log,
                relative_path='MODULE', backup=True)
    # also copy the core files into the same path
    reset_dbdir(params, name, asset_path2, abs_reset_path2, log=log,
                relative_path='CORE')
    # if user wants to reset all databases we do this here
    if reset_dbs:
        # create index databases
        manage_databases.create_fileindex_database(params, pconst, databases)
        # create log database
        manage_databases.create_log_database(params, pconst, databases)
        # create object database
        manage_databases.create_object_database(params, pconst, databases)
        # create reject database
        manage_databases.create_reject_database(params, pconst, databases)


def reset_other_folder(params: ParamDict, log: bool = True):
    """
    Reset the Assets directory (including re-creating databases)

    :param params: ParamDict, parameter dictionary of constants
    :param log: bool - if True logs process

    :return: None - resets assets dir and databases
    """
    _ = log
    # Get the other data directory (place to copy to)
    other_path = params['DRS_DATA_OTHER']
    # get the reset dictionary
    #    key = tuple
    #    1: relative (to APERO) in directory
    #    2: out file/dir name to add to other_path
    reset_dict = params['ARI_RESET_DICT']
    # copy over files/directories to the other directory
    for path_name in list(reset_dict.keys()):
        # get original path
        rel_old_path = reset_dict[path_name][0]
        # construct path (assuming it is relative
        old_path = drs_path.get_relative_folder(base.__PACKAGE__, rel_old_path)
        # construct new path
        new_path = str(os.path.join(other_path, reset_dict[path_name][1]))
        # try to copy the file
        try:
            drs_path.copy_element(old_path, new_path)
        except Exception as e:
            emsg = 'Error copying {0} to other directory {1}. \n\t {2}: {3}'
            eargs = [path_name, other_path, type(e), str(e)]
            WLOG(params, '', emsg.format(*eargs))


def remove_all(params, path, log=True, skipfiles=None):
    # deal with no skipfiles being defined
    if skipfiles is None:
        skipfiles = []
    # Check that directory exists
    if not os.path.exists(path):
        # display error and ask to create directory
        WLOG(params, 'warning', textentry('40-502-00005', args=[path]),
             sublevel=2)
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
    # if we have access to rm and skip files is empty we can do this quickly
    if len(skipfiles) > 0:
        success = fast_remove_skip_files(path, skipfiles)
    else:
        # remove tree (minus head)
        success = fast_rm_remove(path)
    if success:
        return
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


def backup_all_diff(params, old_path, new_path):
    """
    Back up all files that are different between paths (based on filename)

    :param params: ParamDict, parameter dictionary of constants
    :param old_path: str, the old path (things to compare to)
    :param new_path: str, the new path (things to back up)
    :return:
    """
    # get all files in old_path
    old_basenames = []
    for root, dirs, files in os.walk(old_path):
        for filename in files:
            old_basenames.append(os.path.basename(filename))

    # find all files in new_path that aren't in old path
    diff_files = []
    for root, dirs, files in os.walk(new_path):
        for filename in files:
            if os.path.basename(filename) not in old_basenames:
                diff_files.append(os.path.join(root, filename))
    # construct backup dir
    backup_dir = os.path.join(new_path, 'backup')
    # make a backup dir in the new path
    if not os.path.exists(backup_dir):
        os.mkdir(os.path.join(backup_dir))
    # move all files to here
    for filename in diff_files:
        # construct new path
        new_filename = os.path.join(backup_dir, os.path.basename(filename))
        # move files
        print(f'Backing up {filename}')
        shutil.move(filename, new_filename)
    # now remove everything in new_path other than backup
    files = glob.glob(new_path + '/*')
    # loop around files/directories in new_path
    for filename in files:
        # if it is a directory empty it
        if os.path.isdir(filename):
            # unless it is the backup directory
            if filename != backup_dir:
                remove_all(params, filename)
        else:
            print(f'Removing {filename}')
            os.remove(filename)


# noinspection PyBroadException
def fast_remove_skip_files(path: str, skipfiles: List[str],
                           maxfiles: int = 10) -> bool:
    """
    If we have a less than "maxfiles" we copy these file to a temporary
    directory and remove the content (quicker than search directory)

    :param path: str, the path to remove
    :param skipfiles: list of strings, the file paths to skip
    :param maxfiles: int, the max number of files to copy (otherwise we do
                     things a different way)
    :return: bool, True if successful, False otherwise
    """
    if len(skipfiles) > maxfiles:
        return False
    # storage of new skip files
    newskipfiles = []
    # loop around files
    for skipfile in skipfiles:
        # get a temporary location for file
        newskipdir = os.path.expanduser('~/.apero/tmp/')
        newskipfile = os.path.join(newskipdir, os.path.basename(skipfile))
        # make temporary location
        if not os.path.exists(newskipdir):
            try:
                os.makedirs(newskipdir)
            except Exception as _:
                return False
        # if the skip file exists move it to the new skip dir
        if os.path.exists(skipfile):
            shutil.move(skipfile, newskipfile)
        # store newskipfiles
        newskipfiles.append(newskipfile)
    # remove tree (minus head)
    success = fast_rm_remove(path)
    # loop around skip files
    for it in range(len(newskipfiles)):
        # get this iterations values
        skipfile, newskipfile = skipfiles[it], newskipfiles[it]
        # make all paths required for file
        try:
            os.makedirs(os.path.dirname(skipfile))
            # move file
            shutil.move(newskipfile, skipfile)
        except Exception as _:
            success = False
    # return success (this may break the next step if files were partial
    #     removed)
    return success


# noinspection PyBroadException
def fast_rm_remove(path: str) -> bool:
    """
    Remove files in the fastest possible way
    :param path:
    :return:
    """
    # -------------------------------------------------------------------------
    # if empty skip
    if len(os.listdir(path)) == 0:
        return True
    # -------------------------------------------------------------------------
    # try doing an rm (quicker than rmtree)
    try:
        os.system('rm -rfv {0}/*'.format(path))
    except Exception as _:
        pass
    # -------------------------------------------------------------------------
    # if empty we are done
    if len(os.listdir(path)) == 0:
        return True
    # -------------------------------------------------------------------------
    try:
        # try to remove using shutil if rm not available
        shutil.rmtree(path, ignore_errors=False)
        # remake the path (empty)
        os.mkdir(path)
        # return that we were successful
        return True
    except Exception as _:
        # return that we were not successful
        return False


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
        TLOG(params, '', textentry('40-502-00004', args=[path]))
    # if in debug mode just log
    if DEBUG:
        TLOG(params, '', '\t\tRemoved {0}'.format(path))
    # else remove file
    else:
        try:
            os.remove(path)
        except Exception as e:
            # Log warning: Cannot remove path: {0} \n\t {1}: {2}'
            wargs = [path, type(e), str(e)]
            WLOG(params, 'warning', textentry('10-502-00002', args=wargs),
                 sublevel=2)
    # clear loading message
    TLOG(params, '', '')


# =============================================================================
# Define remove functions
# =============================================================================
def get_filelist(params: ParamDict,
                 obsdir: Optional[Union[str, List[str]]] = None,
                 blocks: Optional[List[str]] = None,
                 fileprefix: Optional[str] = None,
                 filesuffix: Optional[str] = None,
                 objnames: Optional[List[str]] = None) -> Tuple[Table, str]:
    """
    Get a list of files from the index database that match either the obsdir
    and/or the file prefix/file suffix

    :param params: ParamDict, the parameter dictionary of constants
    :param obsdir: string or list of strings, the obs directory to search for
    :param blocks: list of strings, the blocks to search for
    :param fileprefix: string, the file prefix to search for
    :param filesuffix: string, the file suffix to search for
    :param objnames: list of strings, the object names to search for
    :return:
    """
    # get index database
    indexdbm = drs_database.FileIndexDatabase(params)
    # load if required
    indexdbm.load_db()
    # -------------------------------------------------------------------------
    # set up condition (do not remove raw files)
    condition = 'BLOCK_KIND!="raw" AND '
    # -------------------------------------------------------------------------
    # construct condition
    subconditions = []
    # -------------------------------------------------------------------------
    # construct condition
    if obsdir is not None:
        if isinstance(obsdir, str):
            subconditions.append('OBS_DIR="{0}"'.format(obsdir))
        elif isinstance(obsdir, list):
            dsubconditions = []
            for obsdir_it in obsdir:
                dsubconditions.append('OBS_DIR="{0}"'.format(obsdir_it))
            dsubcond = (' OR '.join(dsubconditions))
            subconditions.append('({0})'.format(dsubcond))
    # -------------------------------------------------------------------------
    # add the blocks
    if blocks is not None and len(blocks) > 0:
        bsubconditions = []
        for block in blocks:
            bsubconditions.append('BLOCK_KIND="{0}"'.format(block))
        bsubcond = (' OR '.join(bsubconditions))
        subconditions.append('({0})'.format(bsubcond))
    # -------------------------------------------------------------------------
    # add the file prefix condition
    if fileprefix is not None:
        subconditions.append('FILENAME LIKE "{0}%"'.format(fileprefix))
    # -------------------------------------------------------------------------
    # add the file suffix condition
    if filesuffix is not None:
        subconditions.append('FILENAME LIKE "%{0}"'.format(filesuffix))
    # -------------------------------------------------------------------------
    # add the objects conditions
    if objnames is not None and len(objnames) > 0:
        osubconditions = []
        for objname in objnames:
            osubconditions.append('KW_OBJNAME="{0}"'.format(objname))
        osubcond = (' OR '.join(osubconditions))
        subconditions.append('({0})'.format(osubcond))
    # -------------------------------------------------------------------------
    # if we have no subconditions return empty list
    if len(subconditions) == 0:
        wmsg = ('obsdir, blocks, fileprefix, filesuffix or objnames must '
                'be defined. No files added')
        WLOG(params, 'warning', wmsg)
        return Table(), condition
    # -------------------------------------------------------------------------
    # join subconditions
    condition += ' AND '.join(subconditions)
    # -------------------------------------------------------------------------
    # print progress
    msg = 'Querying index database for files with condition: \n\t{0}'
    WLOG(params, '', msg.format(condition))
    # columns required
    columns = 'ABSPATH, FILENAME, KW_PID'
    # run query
    findex_table = indexdbm.get_entries(columns, condition=condition)
    # print how many files found that match condition
    msg = 'Found {0} files that match condition'
    WLOG(params, '', msg.format(len(findex_table)))
    # convert to astropy table
    findex_table = Table.from_pandas(findex_table)
    # return list of files
    return findex_table, condition


def remove_files_from_disk(params: ParamDict, filetable: Table) -> int:
    # get the test criteria
    test = params['INPUTS']['test']
    # deal with tqdm and print outs
    tqdm = base.tqdm_module(use=not test)
    # get absolute file list from table
    absfilelist = filetable['ABSPATH']
    # file count
    filecount = 0
    # loop around each file
    for absfile in tqdm(absfilelist):
        # if in debug mode just log
        if test:
            WLOG(params, '', '\t\tWould have removed {0}'.format(absfile))
            # count as file removed
            filecount += 1
        # else remove file
        else:
            try:
                os.remove(absfile)
                # count as file removed
                filecount += 1
            except Exception as e:
                # Log warning: Cannot remove path: {0} \n\t {1}: {2}'
                wargs = [absfile, type(e), str(e)]
                WLOG(params, 'warning', textentry('10-502-00002', args=wargs),
                     sublevel=2)
    # return count
    return filecount


def remove_files_from_databases(params: ParamDict, filetable: Table,
                                file_cond: str) -> Dict[str, int]:
    # get the test criteria
    test = params['INPUTS']['test']
    # set up a dictionary of ints to count how many files removed from each
    db_counts: Dict[str, int] = dict()
    # deal with tqdm and print outs
    tqdm = base.tqdm_module(use=not test)
    # -------------------------------------------------------------------------
    # get unique filenames
    ufilenames = set(np.array(filetable['FILENAME']).astype(str))
    # remove None (this should not happen)
    if None in ufilenames:
        ufilenames.remove(None)
    if 'None' in ufilenames:
        ufilenames.remove('None')
    # -------------------------------------------------------------------------
    # get unique pids
    upids = set(np.array(filetable['KW_PID']).astype(str))
    # remove "None" from upids
    if None in upids:
        upids.remove(None)
    if 'None' in upids:
        upids.remove('None')
    # -------------------------------------------------------------------------
    # then deal with the calibration database --> remove entries with the
    # same filename)
    calibdbm = drs_database.CalibrationDatabase(params)
    # load if required
    calibdbm.load_db()
    # log removal
    if test:
        WLOG(params, '', 'Would have removed entries from calibration database')
    else:
        WLOG(params, '', 'Removing entries from calibration database')
    # start counter
    db_counts['calibdb'] = 0
    # we need to loop over all files and remove them one by one from the
    # database
    for ufilename in tqdm(ufilenames):
        # construct condition
        cal_cond = 'FILENAME="{0}"'.format(ufilename)
        # add to db counts
        db_counts['calibdb'] += calibdbm.database.count(condition=cal_cond)
        # remove entry
        if not test:
            calibdbm.remove_entries(condition=cal_cond)
        else:
            # log removal
            WLOG(params, '', '\tWould have removed file: {0}'.format(ufilename))

    # -------------------------------------------------------------------------
    # then deal with the telluric database --> remove entries with the
    # same filename)
    telludbm = drs_database.TelluricDatabase(params)
    # load if required
    telludbm.load_db()
    # log removal
    if test:
        WLOG(params, '', 'Would have removed entries from telluric database')
    else:
        WLOG(params, '', 'Removing entries from telluric database')
    # start counter
    db_counts['telludb'] = 0
    # we need to loop over all files and remove them one by one from the
    # database
    for ufilename in tqdm(ufilenames):
        # construct condition
        tel_cond = 'FILENAME="{0}"'.format(ufilename)
        # add to db counts
        db_counts['telludb'] += telludbm.database.count(condition=tel_cond)
        # remove entry
        if not test:
            telludbm.remove_entries(condition=tel_cond)
        else:
            # log removal
            WLOG(params, '', '\tWould have removed file: {0}'.format(ufilename))

    # -------------------------------------------------------------------------
    # for the log database we remove entries with the same PIDs
    logdbm = drs_database.LogDatabase(params)
    # load if required
    logdbm.load_db()
    # log removal
    if test:
        WLOG(params, '', 'Would have removed entries from log database')
    else:
        WLOG(params, '', 'Removing entries from log database')
    # start counter
    db_counts['logdb'] = 0
    # we need to loop over all pids and remove them one by one from the
    # database
    for upid in tqdm(upids):
        # construct condition
        log_cond = 'PID="{0}"'.format(upid)
        # add to db counts
        db_counts['logdb'] += logdbm.database.count(condition=log_cond)
        # remove entry
        if not test:
            logdbm.remove_entries(condition=log_cond)
        else:
            # log removal
            WLOG(params, '', '\tWould have removed PID: {0}'.format(upid))

    # -------------------------------------------------------------------------
    # last deal with index database (easy --> remove entries with the same
    # condition we used to find files)
    findexdb = drs_database.FileIndexDatabase(params)
    # load index database
    findexdb.load_db()
    # log removal
    if test:
        WLOG(params, '', 'Would have removed entries from index database '
                         'with condition: \n\t{0}'.format(file_cond))
    else:
        WLOG(params, '', 'Removing entries from index database with condition: '
                         '\n\t{0}'.format(file_cond))
    # add to db counts
    db_counts['findexdb'] = findexdb.database.count(condition=file_cond)
    # remove entries
    if not test:
        findexdb.remove_entries(condition=file_cond)
    # return counts
    return db_counts


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

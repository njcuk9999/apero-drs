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
from typing import List, Union

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.constants import path_definitions
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.utils import drs_data
from apero.io import drs_lock
from apero.io import drs_path
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
PseudoConst = constants.PseudoConstants
DatabaseM = drs_database.DatabaseManager
# Get Logging function
WLOG = drs_log.wlog
TLOG = drs_log.Printer
# Get the text types
textentry = lang.textentry
# debug mode (test)
DEBUG = False


# =============================================================================
# Define functions
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


def reset_tmp_folders(params: ParamDict, log: bool = True, dtimeout: int = 20):
    """
    Reset the "tmp" (preprocessed directories)

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal
    :param dtimeout: int, number of tries to access the index database

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
    if not findexdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload()
        # create index database
        manage_databases.create_fileindex_database(params, pconst, databases,
                                                   tries=dtimeout)
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
    if not logdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload()
        # create index database
        manage_databases.create_log_database(params, pconst, databases,
                                             tries=dtimeout)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="tmp"'
    # remove entries
    logdb.remove_entries(condition=condition)


def reset_reduced_folders(params: ParamDict, log: bool = True,
                          dtimeout: int = 20):
    """
    Resets the reduced directory

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal
    :param dtimeout: int, number of tries to access the index database

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
    if not indexdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload()
        # create index database
        manage_databases.create_fileindex_database(params, pconst, databases,
                                                   tries=dtimeout)
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
    if not logdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload()
        # create index database
        manage_databases.create_log_database(params, pconst, databases,
                                             tries=dtimeout)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="red"'
    # remove entries
    logdb.remove_entries(condition=condition)


def reset_calibdb(params: ParamDict, log: bool = True, dtimeout: int = 20):
    """
    Wrapper for reset_dbdir - specifically for calibDB

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal
    :param dtimeout: int, number of tries to access the index database

    :return: None - resets telluDB
    """
    # get database paths
    databases = manage_databases.list_databases(params)
    # load pseudo constants
    pconst = constants.pload()
    # name the database
    name = 'calibration database'
    # get the calibration database file directory
    calib_dir = params['DRS_CALIB_DB']
    # get the reset path
    reset_path = params['DRS_RESET_CALIBDB_PATH']
    # reset files
    reset_dbdir(params, name, calib_dir, reset_path, log=log)
    # create calibration database
    manage_databases.create_calibration_database(params, pconst, databases,
                                                 tries=dtimeout)
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


def reset_telludb(params: ParamDict, log: bool = True, dtimeout: int = 20):
    """
    Wrapper for reset_dbdir - specifically for telluDB

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal
    :param dtimeout: int, number of tries to access the index database

    :return: None - resets telluDB
    """
    # get database paths
    databases = manage_databases.list_databases(params)
    # load pseudo constants
    pconst = constants.pload()
    # name the database
    name = 'tellruic database'
    # get the telluric database file directory
    tellu_dir = params['DRS_TELLU_DB']
    # get the reset path
    reset_path = params['DRS_RESET_TELLUDB_PATH']
    # reset files
    reset_dbdir(params, name, tellu_dir, reset_path, log=log)
    # create telluric database
    manage_databases.create_telluric_database(params, pconst, databases,
                                              tries=dtimeout)
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


def reset_lbl_folders(params: ParamDict, log: bool = True, dtimeout: int = 20):
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
    indexdb = drs_database.FileIndexDatabase(params)
    # load index database
    indexdb.load_db()
    # check that table is in database
    if not indexdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload()
        # create index database
        manage_databases.create_fileindex_database(params, pconst, databases,
                                                   tries=dtimeout)
        # get index database
        indexdb = drs_database.FileIndexDatabase(params)
        # load index database
        indexdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="lbl"'
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
        pconst = constants.pload()
        # create index database
        manage_databases.create_log_database(params, pconst, databases,
                                             tries=dtimeout)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="lbl"'
    # remove entries
    logdb.remove_entries(condition=condition)


def reset_out_folders(params: ParamDict, log: bool = True, dtimeout: int = 20):
    """
    Resets the reduced directory

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs the removal
    :param dtimeout: int, number of tries to access the index database

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
    indexdb = drs_database.FileIndexDatabase(params)
    # load index database
    indexdb.load_db()
    # check that table is in database
    if not indexdb.database.tname_in_db():
        # get database paths
        databases = manage_databases.list_databases(params)
        # load pseudo constants
        pconst = constants.pload()
        # create index database
        manage_databases.create_fileindex_database(params, pconst, databases,
                                                   tries=dtimeout)
        # get index database
        indexdb = drs_database.FileIndexDatabase(params)
        # load index database
        indexdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="out"'
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
        pconst = constants.pload()
        # create index database
        manage_databases.create_log_database(params, pconst, databases,
                                             tries=dtimeout)
        # get log database
        logdb = drs_database.LogDatabase(params)
        # load index database
        logdb.load_db()
    # set up condition
    condition = 'BLOCK_KIND="out"'
    # remove entries
    logdb.remove_entries(condition=condition)


def reset_assets(params: ParamDict, log: bool = True, dtimeout: int = 0,
                 reset_dbs: bool = True):
    """
    Reset the Assets directory (including re-creating databases)

    :param params: ParamDict, parameter dictionary of constants
    :param log: bool - if True logs process
    :param dtimeout: int, number of tries to access the index database

    :return: None - resets assets dir and databases
    """
    name = 'assets'
    # get database paths
    databases = manage_databases.list_databases(params)
    # load pseudo constants
    pconst = constants.pload()
    # TODO: deal with getting online
    asset_path = params['DRS_DATA_ASSETS']
    reset_path = os.path.join(params['DRS_RESET_ASSETS_PATH'],
                              params['INSTRUMENT'].lower())

    # get reset_path from apero module dir
    abs_reset_path = drs_data.construct_path(params, '', reset_path)

    # loop around files and folders in assets dir
    #   we want to backup any new files the user as copied
    #   i.e. new masks etc
    reset_dbdir(params, name, asset_path, abs_reset_path, log=log,
                relative_path='MODULE', backup=True)
    # if user wants to reset all databases we do this here
    if reset_dbs:
        # create index databases
        manage_databases.create_fileindex_database(params, pconst, databases,
                                                   tries=dtimeout)
        # create log database
        manage_databases.create_log_database(params, pconst, databases,
                                             tries=dtimeout)
        # create object database
        manage_databases.create_object_database(params, pconst, databases,
                                                tries=dtimeout)
        # create reject database
        manage_databases.create_reject_database(params, pconst, databases,
                                                tries=dtimeout)
        # create language database
        manage_databases.create_lang_database(params, databases, tries=dtimeout)


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
    # try doing an rm
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

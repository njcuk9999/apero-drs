#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Completely recreate database from scratch

Created on 2020-08-2020-08-18 17:13

@author: cook
"""
import os
import shutil
from typing import Any, Dict, List, Literal, Union

import numpy as np
import pandas as pd
from astropy.table import Table, MaskedColumn

from apero.base import base as apero_base
from apero.core import drs_database
from apero.core import drs_astrometrics
from apero.instruments import select
from apero.instruments.default import instrument as instrument_mod
from apero.utils import drs_recipe
from aperocore import drs_lang
from aperocore.base import base
from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.core import drs_db
from aperocore.core import drs_log
from aperocore.io import drs_io

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.database.create_database.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get tqdm from base
tqdm = base.TQDM
# Get database definition
Database = drs_db.AperoDatabase
DatabaseM = drs_database.DatabaseManager
# Get ParamDict
ParamDict = param_functions.ParamDict
Instrument = instrument_mod.Instrument
DrsRecipe = drs_recipe.DrsRecipe
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# get textentry
textentry = drs_lang.textentry
# define reject column datatypes (force consistency)
REJECT_DATA_TYPES = dict()
REJECT_DATA_TYPES['IDENTIFIER'] = str
REJECT_DATA_TYPES['PP'] = int
REJECT_DATA_TYPES['TEL'] = int
REJECT_DATA_TYPES['RV'] = int
REJECT_DATA_TYPES['USED'] = int
REJECT_DATA_TYPES['COMMENT'] = str


# =============================================================================
# Define general functions
# =============================================================================
def kill(params: ParamDict, timeout: int = 60):
    """
    Kill all processes that are in the database yaml database from the specified
    user that are greater than timeout

    :param params: ParamDict, the parameter dictionary of constants
    :param timeout: time in seconds, the minimum time a sql process has been
                    running to kill it (if this is too low it will try to kill
                    itself which isn't recommended)
    :return:
    """
    # get database parameters from base
    dparams = base.DPARAMS
    # construct a generic database manager
    dbm = DatabaseM(params)
    dbm.kind = None
    dbm.dbtable = 'processlist'
    # set the database url
    dbm.load_db(dparams=dparams)
    # wrap in a try (this may not always work
    # noinspection PyBroadException
    try:
        # set update a database
        database = dbm.database
        # set up condition: only this users processes and only from the
        #   required database and that have been active for more than
        #   60 seconds
        cargs = [dbm.dbuser, dbm.dbname, timeout]
        condition = 'USER="{0}" AND DB="{1}" AND TIME > {2}'.format(*cargs)
        # log condition
        WLOG(params, '', 'Condition')
        WLOG(params, '', '\t' + condition)
        # get all processes that were started by user
        table = database.get('*', condition=condition, return_pandas=True)
        # get ids from table
        ids = table['ID'].to_list()
        # log how many ids found
        WLOG(params, '', 'Found {0} processes'.format(len(ids)))
        # try to kill processes
        for _id in ids:
            # set up command
            command = 'kill {0}'.format(_id)
            # execute command
            # noinspection PyBroadException
            try:
                with database.engine.connect() as connection:
                    connection.execute(command)
                # log killing
                WLOG(params, '', '\t' + command)
            except Exception as _:
                continue

    # just return if there is an exception
    except Exception as _:
        return


def export_database(params: ParamDict, recipe: DrsRecipe,
                    database_name: str, outfilename: str):
    """
    Exports a given database "database_name" to "outfilename" (csv file)

    :param params: ParamDict, parameter dictionary of constants
    :param database_name: str, the database name (calib, tellu, index, log,
                          object, lang)
    :param outfilename: str, the output filepath for the csv file

    :return: None, writes outfilename
    """
    # ----------------------------------------------------------------------
    # get database list
    databases = list_databases(params, recipe.shortname)
    # ----------------------------------------------------------------------
    # make sure database_name is lower case
    database_name = database_name.lower()
    # -------------------------------------------------------------------
    # deal with calibration database
    if database_name in apero_base.DATABASE_NAMES:
        db = databases[database_name]
    # else log error
    else:
        # log error: Argument Error: EXPORTDB must be
        eargs = [' or '.join(apero_base.DATABASE_NAMES)]
        raise AperoCodedException(params, '09-506-00001', targs=eargs)
    # -------------------------------------------------------------------
    # load database
    db.load_db()
    # -------------------------------------------------------------------
    # deal with no database
    if db.database is None:
        # log error: Database Error: Cannot load "{0}" database
        eargs = [database_name]
        raise AperoCodedException(params, '09-506-00002', targs=eargs)
    # -------------------------------------------------------------------
    # get all rows as a pandas data frame
    df = db.database.get('*', return_pandas=True)
    # -------------------------------------------------------------------
    # print that we are saving csv file
    WLOG(params, '', textentry('40-507-00001', args=[outfilename]))
    # save to csv file
    df.to_csv(outfilename)


def import_database(params: ParamDict, recipe: DrsRecipe,
                    database_name: str, infilename: str,
                    joinmode: Literal["fail", "replace", "append"] = 'replace'):
    """
    Imports a given csv file "infilename" to database "database_name"

    :param params: ParamDict, parameter dictionary of constants
    :param database_name: str, the database name (calib, tellu, index, log,
                          object, lang)
    :param infilename: str, the input filepath for the csv file
    :param joinmode: str, the way to join current database and input fiile
                     - if 'replace' then current database is deleted first,
                     - if 'append' adds the infile to bottom of current database

    :return: None, writes to database
    """
    # ----------------------------------------------------------------------
    # get database list
    databases = list_databases(params, recipe.shortname)
    # ----------------------------------------------------------------------
    # make sure database_name is lower case
    database_name = database_name.lower()
    # -------------------------------------------------------------------
    # deal with joinmode
    if joinmode not in ['append', 'replace']:
        # log error: Join mode = "{0}" is invalid. Must be either "append"
        #            or "replace"
        raise AperoCodedException(params, '09-506-00004', targs=[joinmode])
    # -------------------------------------------------------------------
    # deal with calibration database
    if database_name in apero_base.DATABASE_NAMES:
        db = databases[database_name]
    # else log error
    else:
        # log error Argument Error: EXPORTDB must be {0}
        eargs = [' or '.join(apero_base.DATABASE_NAMES)]
        raise AperoCodedException(params, '09-506-00003', targs=eargs)
    # -------------------------------------------------------------------
    # load database
    # -------------------------------------------------------------------
    db.load_db()
    # deal with no database
    if db.database is None:
        # get a list of all other database
        other_databases = list(apero_base.DATABASE_NAMES).remove(database_name)
        # install database
        install_databases(params, skip=other_databases)
        # load database
        db.load_db()
    # -------------------------------------------------------------------
    # load csv file
    # -------------------------------------------------------------------
    # print that we are saving csv file
    WLOG(params, '', textentry('40-507-00002', args=[infilename]))
    # load csv file into pandas table
    df = pd.read_csv(infilename)
    # -------------------------------------------------------------------
    # Push into database
    # -------------------------------------------------------------------
    # print log
    if joinmode == 'replace':
        wmsg = textentry('40-507-00003')
    else:
        wmsg = textentry('40-507-00004')
    # log
    WLOG(params, '', wmsg)
    # add pandas table to database
    db.database.add_from_pandas(df, if_exists=joinmode)


def list_databases(params: ParamDict,
                   shortname: str) -> Dict[str, DatabaseM]:
    # set up storage
    databases = dict()
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get databases from managers (later databases)
    calibdbm = drs_database.CalibrationDatabase(params, shortname, pconst)
    telludbm = drs_database.TelluricDatabase(params, shortname, pconst)
    findexdbm = drs_database.FileIndexDatabase(params, shortname, pconst)
    logdbm = drs_database.LogDatabase(params, shortname, pconst)
    objectdbm = drs_astrometrics.AstrometricDatabase(params, shortname)
    rejectdbm = drs_database.RejectDatabase(params, shortname, pconst)
    # add to storage
    databases['calib'] = calibdbm
    databases['tellu'] = telludbm
    databases['findex'] = findexdbm
    databases['log'] = logdbm
    databases['astrom'] = objectdbm
    databases['reject'] = rejectdbm
    # return the databases
    return databases


def install_databases(params: ParamDict, skip: Union[List[str], None] = None,
                      dbkind: Union[str, List[str]] = 'all',
                      verbose: bool = False):
    # deal with skip
    if skip is None:
        skip = []
    # deal with dbkind == 'all'
    if dbkind == 'all':
        runs = ['calib', 'tellu', 'findex', 'log', 'astrom', 'reject', 'lang']
    elif isinstance(dbkind, str):
        runs = [dbkind]
    else:
        runs = dbkind
    # get database paths
    databases = list_databases(params, 'MAN_DB')
    # load pseudo constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # -------------------------------------------------------------------------
    # create calibration database
    if 'calib' not in skip and 'calib' in runs:
        _ = create_calibration_database(params, pconst, databases,
                                        verbose=verbose)
    # -------------------------------------------------------------------------
    # create telluric database
    if 'tellu' not in skip and 'tellu' in runs:
        _ = create_telluric_database(params, pconst, databases,
                                     verbose=verbose)
    # -------------------------------------------------------------------------
    # create index database
    if 'findex' not in skip and 'findex' in runs:
        _ = create_fileindex_database(params, pconst, databases,
                                      verbose=verbose)
    # -------------------------------------------------------------------------
    # create log database
    if 'log' not in skip and 'log' in runs:
        _ = create_log_database(params, pconst, databases, verbose=verbose)
    # -------------------------------------------------------------------------
    # create object database
    if 'astrom' not in skip and 'astrom' in runs:
        _ = create_object_database(params, pconst, databases, verbose=verbose)
    # -------------------------------------------------------------------------
    # create reject database
    if 'reject' not in skip and 'reject' in runs:
        _ = create_reject_database(params, pconst, databases, verbose=verbose)


# =============================================================================
# Define calibration database functions
# =============================================================================
def create_calibration_database(params: ParamDict, pconst: Instrument,
                                databases: Dict[str, DatabaseM],
                                verbose: bool = False) -> Database:
    """
    Setup for the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get parameters from params
    asset_dir = params['PATH.ASSETS']
    reset_path = params['DB.DIR']
    # get columns and ctypes from pconst
    cdb_cols = pconst.CALIBRATION_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    calibdbm = databases['calib']
    # -------------------------------------------------------------------------
    # make database
    calibdb = drs_db.AperoDatabase(calibdbm.dburl, tablename=calibdbm.dbtable,
                                   connect_args=calibdbm.connect_args)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if calibdb.tablename in calibdb.get_tables():
        calibdb.backup()
        calibdb.delete_table(calibdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted calibration database')
    # add main table
    calibdb.add_table(calibdb.tablename,
                      columns=cdb_cols.columns,
                      indexes=cdb_cols.indexes,
                      uniques=cdb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created calibration database')
    # -------------------------------------------------------------------------
    return calibdb


# =============================================================================
# Define telluric database functions
# =============================================================================
def create_telluric_database(params: ParamDict, pconst: Instrument,
                             databases: Dict[str, DatabaseM],
                             verbose: bool = False) -> Database:
    """
    Setup for the telluric database

    :param params: ParamDict, parmaeter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get parameters from params
    asset_dir = params['PATH.ASSETS']
    reset_path = params['DB.DIR']
    # get columns and ctypes from pconst
    tdb_cols = pconst.TELLURIC_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    telludbm = databases['tellu']
    # -------------------------------------------------------------------------
    # make database
    telludb = drs_db.AperoDatabase(telludbm.dburl, tablename=telludbm.dbtable,
                                    connect_args=telludbm.connect_args)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if telludb.tablename in telludb.get_tables():
        telludb.backup()
        telludb.delete_table(telludb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted telluric database')
    # add main table
    telludb.add_table(telludb.tablename,
                      columns=tdb_cols.columns,
                      indexes=tdb_cols.indexes,
                      uniques=tdb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created telluric database')
    # ---------------------------------------------------------------------
    return telludb


# =============================================================================
# Define index database functions
# =============================================================================
def create_fileindex_database(params: ParamDict, pconst: Instrument,
                              databases: Dict[str, DatabaseM],
                              verbose: bool = False) -> Database:
    """
    Setup for the file index database

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    idb_cols = pconst.FILEINDEX_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    findexdbm = databases['findex']
    # -------------------------------------------------------------------------
    # make database
    indexdb = drs_db.AperoDatabase(findexdbm.dburl, tablename=findexdbm.dbtable,
                                   connect_args=findexdbm.connect_args)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if indexdb.tablename in indexdb.get_tables():
        indexdb.backup()
        indexdb.delete_table(indexdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted file index database')
    # add main table
    indexdb.add_table(indexdb.tablename,
                      columns=idb_cols.columns,
                      indexes=idb_cols.indexes,
                      uniques=idb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created file index database')
    # -------------------------------------------------------------------------
    return indexdb


# =============================================================================
# Define log database functions
# =============================================================================
def create_log_database(params: ParamDict, pconst: Instrument,
                        databases: Dict[str, DatabaseM],
                        verbose: bool = False) -> Database:
    """
    Setup for the index database

    :param params: ParamDict, parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    ldb_cols = pconst.LOG_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    logdbm = databases['log']
    # -------------------------------------------------------------------------
    # make database
    logdb = drs_db.AperoDatabase(logdbm.dburl, tablename=logdbm.dbtable,
                                 connect_args=logdbm.connect_args)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if logdb.tablename in logdb.get_tables():
        logdb.backup()
        logdb.delete_table(logdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted recipe log database')
    # add main table
    logdb.add_table(logdb.tablename,
                    columns=ldb_cols.columns,
                    indexes=ldb_cols.indexes,
                    uniques=ldb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created recipe log database')
    # -------------------------------------------------------------------------
    return logdb


# =============================================================================
# Define object database functions
# =============================================================================
def create_object_database(params: ParamDict, pconst: Instrument,
                           databases: Dict[str, DatabaseM],
                           verbose: bool = False) -> 'DatabaseM':
    """
    Setup for the astrometric (object) database.

    The astrometric catalogue is now yaml-backed (one file per object
    under DRS_DATA_ASSETS/astrometrics) so there is no SQL table to
    create. This function only ensures the directory exists and validates
    that entries are readable.

    :param params: ParamDict, the parameter dictionary of constants
    :param pconst: Pseudo constants (unused, kept for API parity)
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: the (yaml-backed) astrometric database manager.
    """
    # unused kwargs (kept for API parity with the other create_* funcs)
    _ = pconst
    # the yaml-backed manager from the databases dict
    objectdbm = databases['astrom']
    # ensure the on-disk directory exists
    objectdbm._ensure_loaded()
    if verbose:
        WLOG(params, '', 'Astrometric database is yaml-backed (no SQL '
             'table to create)')
    # ---------------------------------------------------------------------
    # validate yaml-backed archive readability
    validate_astrometric_yaml_archive(params, shortname='MAN_DB',
                                      log=verbose)
    # ---------------------------------------------------------------------
    return objectdbm


def object_db_populated(params: ParamDict, shortname: str) -> bool:
    """
    Check that the (yaml-backed) astrometric database is populated.
    """
    # load the yaml-backed database manager
    objdbm = drs_astrometrics.AstrometricDatabase(params, shortname)
    objdbm.load_db()
    # count entries on disk
    count = objdbm.count()
    # return a boolean for object database populated
    return count > 0


def validate_astrometric_yaml_archive(params: ParamDict,
                                      shortname: str = 'MAN_DB',
                                      log: bool = True) -> Dict[str, int]:
    """
    Validate readability of yaml-backed astrometric entries on disk.

    Before validating yaml readability we synchronise the local assets from
    the packaged defaults (and remote tar, if needed), mirroring the
    ``reset_assets`` logic for the ``astrometrics`` directory but without
    deleting the existing directory content first.

    :param params: ParamDict, the parameter dictionary of constants
    :param shortname: str, recipe shortname used for manager construction
    :param log: bool, if True logs validation summary/errors

    :return: dict with ``total``, ``valid`` and ``invalid`` counts
    """
    # keep setup imports local to avoid circular imports at module load time
    from apero.tools.module.setup import drs_assets
    from apero.tools.module.setup import drs_reset
    from apero.utils import drs_data
    # ---------------------------------------------------------------------
    # ensure local assets are current before validating yaml files
    update_assets = drs_assets.check_local_assets(params)
    if update_assets:
        drs_assets.update_local_assets(params)
    # copy default astrometric yaml files back into PATH.ASSETS/astrometrics
    # without emptying first (non-destructive reset behavior)
    reset_name = 'astrometric assets'
    asset_path = os.path.join(params['PATH.ASSETS'], 'astrometrics')
    reset_relpath = os.path.join(params['IPATH.RESET_ASSETS'], 'astrometrics')
    reset_abspath = drs_data.construct_path(params, '', str(reset_relpath))
    drs_reset.reset_dbdir(params, reset_name, asset_path, reset_abspath,
                          log=log, empty_first=False,
                          relative_path='astrometrics')
    # ---------------------------------------------------------------------
    # build manager and ensure path exists
    objdbm = drs_astrometrics.AstrometricDatabase(params, shortname)
    objdbm._ensure_loaded()
    astrom_dir = objdbm.path
    # gather yaml files (exclude reject list)
    yaml_files = []
    for name in sorted(os.listdir(astrom_dir)):
        if not name.endswith('.yaml'):
            continue
        if name == 'reject_list.yaml':
            continue
        yaml_files.append(os.path.join(astrom_dir, name))
    # validate files one-by-one
    bad_files = []
    for yfile in yaml_files:
        try:
            entry = drs_astrometrics.AstrometricDatabase._read_yaml(yfile)
            if not isinstance(entry, dict):
                raise TypeError('entry is not a dict')
            apero_name = entry.get('APERO_NAME', None)
            cleaned = drs_astrometrics.clean_object(apero_name)
            if cleaned in ['Null', '']:
                emsg = 'entry missing valid APERO_NAME'
                raise ValueError(emsg)
        except Exception as e:
            bad_files.append((yfile, type(e).__name__, str(e)))
    # summary counts
    total = len(yaml_files)
    invalid = len(bad_files)
    valid = total - invalid
    # log summary and fail on invalid entries
    if log:
        msg = 'Astrometric yaml validation: total={0} valid={1} invalid={2}'
        WLOG(params, 'info', msg.format(total, valid, invalid))
    if invalid > 0:
        yfile, etype, emsg = bad_files[0]
        eargs = [yfile, etype, emsg]
        full = ('Invalid astrometric yaml entry in {0} (error {1}: {2}). '
                'Fix yaml files under DRS_DATA_ASSETS/astrometrics.')
        raise AperoCodedException(params, message=full.format(*eargs),
                                  targs=eargs)
    return dict(total=total, valid=valid, invalid=invalid)


# =============================================================================
# Define reject database functions
# =============================================================================
def create_reject_database(params: ParamDict, pconst: Instrument,
                           databases: Dict[str, DatabaseM],
                           verbose: bool = False) -> Database:
    """
    Setup for the reject database

    :param params: ParamDict, the parameter dictionary of constants
    :param pconst: Pseudo constants
    :param databases: dictionary of database managers
    :param verbose: bool, if True print more messages

    :returns: database - the telluric database
    """
    # get columns and ctypes from pconst
    rejectdb_cols = pconst.REJECT_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    rejectdbm = databases['reject']
    # -------------------------------------------------------------------------
    # make database
    rejectdb = drs_db.AperoDatabase(rejectdbm.dburl,
                                    tablename=rejectdbm.dbtable,
                                    connect_args=rejectdbm.connect_args)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if rejectdb.tablename in rejectdb.get_tables():
        rejectdb.backup()
        rejectdb.delete_table(rejectdb.tablename)
        if verbose:
            WLOG(params, '', 'Deleted reject database')
    # add main table
    rejectdb.add_table(rejectdb.tablename,
                       columns=rejectdb_cols.columns,
                       indexes=rejectdb_cols.indexes,
                       uniques=rejectdb_cols.uniques)
    if verbose:
        WLOG(params, '', 'Created reject database')
    # ---------------------------------------------------------------------
    # update object database from google sheet(s)
    update_reject_database(params)
    # -------------------------------------------------------------------------
    return rejectdb


def reject_db_populated(params: ParamDict, recipe: DrsRecipe) -> bool:
    """
    Check that reject database is populated
    """
    # need to load database
    rejectdbm = drs_database.RejectDatabase(params, recipe.shortname)
    rejectdbm.load_db()
    # count rows in database
    count = rejectdbm.database.count()
    # return a boolean for object database populated
    return count > 0


def update_reject_database(params: ParamDict, log: bool = True):
    """
    Update the local reject database - note this overwrites all entries in the
    local database

    By default this uses a googlesheet URL (REJECT_LIST_GOOGLE_SHEET_URL)

    however if REJECT_LIST_GOOGLE_SHEET_URL is a local directory one can set the
    REJECT_LIST_GSHEET_MAIN_LIST_ID to a csv file for a complete offline 
    reduction

    :param params: ParamDict, the parameter dictionary of constants
    :param log: bool, if True logs update

    :return: None, updates local object database
    """
    # get pconst
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get list of databases
    databases = list_databases(params, 'MAN_DB')
    # get the object database (combined with pending + user table)
    maintable = get_reject_database(params, log=log)
    # -------------------------------------------------------------------------
    # convert main table to a pandas dataframe
    df = maintable.to_pandas()
    # -------------------------------------------------------------------------
    # get columns and ctypes from pconst
    rejectdb_cols = pconst.REJECT_DB_COLUMNS()
    # -------------------------------------------------------------------------
    # construct directory
    rejectdbm = databases['reject']
    # -------------------------------------------------------------------------
    # make database
    rejectdb = drs_db.AperoDatabase(rejectdbm.dburl, tablename=rejectdbm.dbtable)
    # -------------------------------------------------------------------------
    # remove table if it already exists
    if rejectdb.tablename in rejectdb.get_tables():
        rejectdb.backup()
        rejectdb.delete_table(rejectdb.tablename)
    # add main table
    rejectdb.add_table(rejectdb.tablename,
                       columns=rejectdb_cols.columns,
                       indexes=rejectdb_cols.indexes,
                       uniques=rejectdb_cols.uniques)
    # ---------------------------------------------------------------------
    # add rows from pandas dataframe
    rejectdb.add_from_pandas(df)


def get_reject_database(params: ParamDict, log: bool = True) -> Table:
    """
    Get the reject database from google sheet (or file)
    and combine with pending / user table if required and found

    :param params: ParamDict, parameter dictionary of constants
    :param log: whether to log table read

    :return: astropy table, the object database
    """
    # set function name
    func_name = __NAME__ + '.get_reject_database()'
    # get parameters from params
    gsheet_url = params['OBJ.LIST.RLIST_GSHEET_URL']
    main_id = params['OBJ.LIST.RLIST_GSHEET_MAINLIST_ID']
    # print that we are updating object database
    if log:
        WLOG(params, 'info', textentry('40-503-00046'))
    # -------------------------------------------------------------------------
    # load pseudo constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get reject database column data types
    reject_data_types = dict()
    reject_cols = pconst.REJECT_DB_COLUMNS()
    # loop around columns and get data type
    for col in reject_cols.columns:
        reject_data_types[col.name] = reject_cols.get_datatype(col.name)
    # -------------------------------------------------------------------------
    # deal with gsheet_url being local csv file
    if os.path.exists(gsheet_url):
        mainpath = os.path.join(gsheet_url, main_id)
        try:
            maintable = drs_io.no_mask_table(Table.read(mainpath, format='csv'))
        except Exception as e:
            # error msg: if REJECT_LIST_GOOGLE_SHEET_URL is local directory
            #            main_id must be a valid csv file
            eargs = [mainpath, type(e), str(e), func_name]
            raise AperoCodedException(params, '09-002-00006', targs=eargs)
    else:
        # get google sheets
        maintable = drs_database.get_google_sheet(params, gsheet_url, main_id)
    # force types in main table and pend table (so we can join them)
    maintable = _force_column_dtypes(maintable, reject_data_types)
    # -------------------------------------------------------------------------
    # return the main table
    return maintable


# =============================================================================
# Define misc functions
# =============================================================================
def reset_db_pending(params):
    """
    Reset the pending object database - this is for testing purposes only

    :param params: ParamDict, the parameter dictionary of constants

    :return: None, updates local object database
    """
    # get the path to the database
    db_pend = str(os.path.join(params['PATH.OTHER'], params['DB.PENDING_PATH']))
    # remove everything
    if os.path.exists(db_pend):
        # walk around the directory and delete all files
        for root, dirs, files in os.walk(db_pend):
            for file in files:
                print('Removing file: {0}'.format(os.path.join(root, file)))
                os.remove(os.path.join(root, file))
        # finally clean all sub-directories
        shutil.rmtree(db_pend)
    # re-create the directory if it doesn't exist
    if not os.path.exists(db_pend):
        # re-create this directory
        os.makedirs(db_pend)


def _force_column_dtypes(table: Table, coltype: Dict[str, type]) -> Table:
    """
    Force a table to have specific data types

    :param table: astropy.table.Table instance
    :param coltype: list of types to force columns to
    :return:
    """
    # loop around columns and force types
    for col in table.colnames:
        # if we do not define this column remove it
        if col not in coltype:
            del table[col]
            continue
        # strings are a pain have to do them manually
        if hasattr(table[col], 'mask'):
            mask = table[col].mask
            values = np.array(table[col]).astype(coltype[col])
            table[col] = MaskedColumn(values, mask=mask)

        else:
            table[col] = np.array(table[col]).astype(coltype[col])
    # return the new table
    return table



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # test with spirou
    _params = load_functions.load_config(select.INSTRUMENTS)
    # install database
    install_databases(_params)

# =============================================================================
# End of code
# =============================================================================
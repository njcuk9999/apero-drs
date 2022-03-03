#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-12 at 09:45

@author: cook
"""
from astropy import units as uu
from astropy.io.ascii.core import InconsistentTableError
from astropy.table import Table
import numpy as np
import pandas as pd
import requests
import time
from typing import Any, List, Tuple, Union
import warnings

from apero.base import base
from apero.core.core import drs_text
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_database
from apero.core.instruments.default import pseudo_const
from apero import lang
from apero.core.core import drs_log
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'preprocessing.gen_pp.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get time
Time = base.Time
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# Get database
ObjectDatabase = drs_database.ObjectDatabase
# get param dict
ParamDict = constants.ParamDict
PseudoConst = pseudo_const.PseudoConstants

# cache for google sheet
GOOGLE_TABLES = dict()
# define standard google base url
GOOGLE_BASE_URL = ('https://docs.google.com/spreadsheets/d/{}/gviz/'
                   'tq?tqx=out:csv&gid={}')
# unit aliases
masyr = uu.mas / uu.yr
# Define columns which cannot be null
NON_NULL_OBJ_COLS = ['OBJNAME', 'RA_DEG', 'DEC_DEG', 'PMRA', 'PMDE', 'EPOCH']


# =============================================================================
# Define object resolution functions
# =============================================================================
def resolve_target(params: ParamDict, pconst: PseudoConst,
                   objname: Union[str, None] = None,
                   database: Union[ObjectDatabase, None] = None,
                   header: Union[drs_fits.Header, None] = None
                   ) -> Union[drs_fits.Header, None]:
    """
    Resolve a target against the local object database

    :param params: parameter dictionary of constants
    :param pconst: psuedo constants from this instrument
    :param objname: str, the object names to resolve - if you have the header
                    use header instead of objname (overrides objname any way)
    :param database: ObjectDatabase or None, object database instance so we
                     don't load more times than needed
    :param header: if objname is not set get parameters via fits header
                   (recommended over objname as fills in ra/dec/pmra/pmde for
                   targets that are not found)

    :return: None - updates object database
    """
    # get the null rv criteria
    null_rv = params['OBJRV_NULL_VAL']
    # get object name in header keyword
    hdr_objname = params['KW_OBJNAME'][0]
    # load database
    if database is None:
        database = ObjectDatabase(params)
        database.load_db()
    # -------------------------------------------------------------------------
    # deal with no objname and no header
    if objname is None and header is None:
        # TODO: add to language database
        WLOG(params, 'error', 'Must define "objname" or "header"')
    elif objname is None:
        if hdr_objname in header:
            objname = header[hdr_objname]
        else:
            # TODO: add to language database
            emsg = 'Header must be fixed ({0} missing)'
            eargs = [hdr_objname]
            WLOG(params, 'error', emsg.format(*eargs))
            return
    # -------------------------------------------------------------------------
    # find correct name in the database (via objname or aliases)
    correct_objname, found = database.find_objname(pconst, objname)
    # -------------------------------------------------------------------------
    # update the sql object condition
    sql_obj_cond = 'OBJNAME="{0}"'.format(correct_objname)
    # get the full entry for this cobjname
    table = database.get_entries('*', condition=sql_obj_cond)
    # -------------------------------------------------------------------------
    # check if key columns have null values - if they do remove these rows
    #   from the table
    if len(table) != 0:
        nullmask = np.zeros(len(table), dtype=bool)
        # loop around columns and look for nulls
        for col in NON_NULL_OBJ_COLS:
            nullmask |= table[col].isnull()
        # filter table
        table = pd.DataFrame(table[~nullmask])
    # -------------------------------------------------------------------------
    # now re-test table length and then use from table
    if len(table) != 0:
        # ---------------------------------------------------------------------
        # try to use table
        try:
            # get properties from parameters
            # object name is the cleaned object name
            objname = str(table['OBJNAME'].iloc[0])
            original_name = str(table['ORIGINAL_NAME'].iloc[0])
            # right ascension and declination in degrees
            ra_deg = float(table['RA_DEG'].iloc[0])
            ra_source = str(table['RA_SOURCE'].iloc[0])
            dec_deg = float(table['DEC_DEG'].iloc[0])
            dec_source = str(table['DEC_SOURCE'].iloc[0])
            # epoch in JD
            epoch = float(table['EPOCH'].iloc[0])
            # pmra and pmde in mas/yr
            pmra = float(table['PMRA'].iloc[0])
            pmra_source = str(table['PMRA_SOURCE'].iloc[0])
            pmde = float(table['PMDE'].iloc[0])
            pmde_source = str(table['PMDE_SOURCE'].iloc[0])
            # parallax in mas (may not be present)
            plx = float(_target_set_value(table, 'PLX', null_value=np.nan))
            plx_source = str(table['PLX_SOURCE'].iloc[0])
            # RV in km/s (may not be present)
            rv = float(_target_set_value(table, 'RV', null_value=np.nan))
            rv_source = str(table['RV_SOURCE'].iloc[0])
            # Teff in K (may not be present)
            teff = float(_target_set_value(table, 'TEFF', null_value=np.nan))
            teff_source = str(table['TEFF_SOURCE'].iloc[0])
            # spectral type (may not be present)
            sp_type = str(table['SP_TYPE'].iloc[0])
            sp_source = str(table['SP_SOURCE'].iloc[0])
            # data source is "database" and no date is the date the database
            #   was last updated (times added when database downloaded last)
            data_source = 'database'
            data_date = str(table['DATE_ADDED'].iloc[0])
            # mark resolved as complete
            resolved = True

        except Exception as e:
            # TODO: move to lanugage database
            emsg = 'Cannot use object database entry for {0}.\n\t{1}: {2}'
            eargs = [correct_objname, type(e), str(e)]
            WLOG(params, 'warning', emsg.format(*eargs))
            # mark resolved as not complete
            resolved = False
            # placeholders to be filled below
            objname, original_name = '', ''
            ra_deg, dec_deg, epoch = np.nan, np.nan, np.nan
            pmra, pmde, plx, rv, teff = np.nan, np.nan, np.nan, np.nan, np.nan
            ra_source, dec_source, pmra_source, pmde_source, = '', '', '', ''
            plx_source, rv_source, teff_source = '', '', ''
            sp_type, sp_source, data_source, data_date = '', '', '', ''
    else:
        # mark resolved as not complete
        resolved = False
        # placeholders to be filled below
        objname, original_name = '', ''
        ra_deg, dec_deg, epoch = np.nan, np.nan, np.nan
        pmra, pmde, plx, rv, teff = np.nan, np.nan, np.nan, np.nan, np.nan
        ra_source, dec_source, pmra_source, pmde_source, = '', '', '', ''
        plx_source, rv_source, teff_source = '', '', ''
        sp_type, sp_source, data_source, data_date = '', '', '', ''
    # -------------------------------------------------------------------------
    # if we still do not have a value use the header values (or default values)
    if not resolved:
        # print warning that we are using the header not the database
        # TODO: add to language database
        wmsg = ('Object {0} is not in the object database. Using header values'
                ' for astrometric parameters')
        wargs = [correct_objname]
        WLOG(params, 'warning', wmsg.format(*wargs), sublevel=7)
        # get properties from parameters
        # object name is the cleaned object name to be inline database sources
        objname = str(correct_objname)
        original_name = str(header[params['KW_OBJECTNAME'][0]])
        # right ascension and declination in degrees
        ra_deg = float(header[params['KW_OBJRA'][0]])
        ra_source = 'header'
        dec_deg = float(header[params['KW_OBJDEC'][0]])
        dec_source = 'header'
        # epoch needs to be converted based on instrument (should be in JD)
        epoch = float(pconst.GET_EPOCH(params, header))
        # pmra and pmde
        pmra = float(header[params['KW_OBJRAPM'][0]])
        pmra = _convert_units(params, 'KW_OBJRAPM', pmra, uu.mas/uu.yr)
        pmra_source = 'header'
        pmde = float(header[params['KW_OBJDECPM'][0]])
        pmde = _convert_units(params, 'KW_OBJDECPM', pmde, uu.mas/uu.yr)
        pmde_source = 'header'
        # parallax in mas (may not be present)
        plx = float(header.get(params['KW_PLX'][0], np.nan))
        plx = _convert_units(params, 'KW_PLX', plx, uu.mas)
        plx_source = 'header'
        # RV in km/s (may not be present)
        rv = float(header.get(params['KW_INPUTRV'][0], np.nan))
        rv = _convert_units(params, 'KW_INPUTRV', rv, uu.km / uu.s)
        rv_source = 'header'
        # Teff in K (may not be present)
        teff = float(header.get(params['KW_OBJ_TEMP'][0], np.nan))
        teff_source = 'header'
        # spectral type (not present but required for KW_DRS_SPTYPE)
        sp_type = ''
        sp_source = 'header'
        # data source is just "header" and no associated date
        data_source = 'header'
        data_date = ''
    # -------------------------------------------------------------------------
    # deal with bad values here
    #   We trust RA/Dec/PMRA/PMDE have been entered correctly
    #     - if any of these values are missing they should not be in the
    #       database / we assume they are in the header
    # -------------------------------------------------------------------------
    # parallax - if non-finite or negative - set to zero
    if not np.isfinite(plx) or plx < 0:
        plx = 0.0
    # rv - if non-finite or out of bounds (>1000) - set to zero
    if not np.isfinite(rv) or np.abs(rv) > null_rv:
        rv = 0.0
    # BERV must be in m/s [header and database values in km/s]
    rv = rv * 1000
    # -------------------------------------------------------------------------
    # update header
    header = drs_fits.Header(header)
    # add object name and source
    header.set_key(params, 'KW_DRS_OBJNAME', value=objname)
    header.set_key(params, 'KW_DRS_OBJNAME_S', value=original_name)
    # add the ra and source
    header.set_key(params, 'KW_DRS_RA', value=ra_deg)
    header.set_key(params, 'KW_DRS_RA_S', value=ra_source)
    # add the dec and source
    header.set_key(params, 'KW_DRS_DEC', value=dec_deg)
    header.set_key(params, 'KW_DRS_DEC_S', value=dec_source)
    # add the epoch
    header.set_key(params, 'KW_DRS_EPOCH', value=epoch)
    # add the pmra
    header.set_key(params, 'KW_DRS_PMRA', value=pmra)
    header.set_key(params, 'KW_DRS_PMRA_S', value=pmra_source)
    # add the pmde
    header.set_key(params, 'KW_DRS_PMDE', value=pmde)
    header.set_key(params, 'KW_DRS_PMDE_S', value=pmde_source)
    # add the plx
    header.set_key(params, 'KW_DRS_PLX', value=plx)
    header.set_key(params, 'KW_DRS_PLX_S', value=plx_source)
    # add the rv
    header.set_key(params, 'KW_DRS_RV', value=rv)
    header.set_key(params, 'KW_DRS_RV_S', value=rv_source)
    # add the teff
    header.set_key(params, 'KW_DRS_TEFF', value=teff)
    header.set_key(params, 'KW_DRS_TEFF_S', value=teff_source)
    # add the spectral type key
    header.set_key(params, 'KW_DRS_SPTYPE', value=sp_type)
    header.set_key(params, 'KW_DRS_SPTYPE_S', value=sp_source)
    # add the data source / time added key
    header.set_key(params, 'KW_DRS_DSOURCE', value=data_source)
    header.set_key(params, 'KW_DRS_DDATE', value=data_date)
    # -------------------------------------------------------------------------
    # must update DRSOBJN
    header.set_key(params, 'KW_OBJNAME', value=objname)
    # -------------------------------------------------------------------------
    # return the header
    return header


def get_obj_reject_list(params: ParamDict) -> np.ndarray:
    """
    Get a list of rejected object names from the googlesheet object database

    :param params: ParamDict, parameter dictionary of constants

    :return: np.array 1D, the list of reject object names
    """
    # get psuedo constants
    pconst = constants.pload()
    # get parameters from params
    gsheet_url = params['OBJ_LIST_GOOGLE_SHEET_URL']
    reject_id = params['OBJ_LIST_GSHEET_REJECT_LIST_ID']
    # get reject list google sheets
    try:
        rejecttable = get_google_sheet(params, gsheet_url, reject_id)
    # any exception here should return a warning and a empty array
    except Exception as e:
        # TODO: move to language database
        wmsg = ('Cannot read reject list {0}. Skipping rejection'
                '\n\tError {1}: {2}')
        wargs = [GOOGLE_BASE_URL.format(gsheet_url, reject_id),
                 type(e), str(e)]
        WLOG(params, 'warning', wmsg.format(*wargs))
        # return empty array
        return np.array([])
    # if we have reject entries deal with them (and their aliases)
    if len(rejecttable) > 0:
        # only keep rows which should be used
        mask = rejecttable['USED'] == 1
        # cut down the reject table
        rejecttable = rejecttable[mask]
        # start the reject list with all object names in the reject list
        reject_objs = list(rejecttable['OBJNAME'])
        # loop around rows in the reject table
        for row in range(len(rejecttable)):
            # add all objects in the alias list
            aliaslist = rejecttable['ALIASES'][row]
            # loop around invidiual alias names
            for alias in aliaslist.split('|'):
                # clean alias name and add to reject list
                reject_objs.append(pconst.DRS_OBJ_NAME(alias))
        # return any unique rows in reject object list
        return np.unique(reject_objs)
    # else if we have no objects to reject just return an empty array
    else:
        return np.array([])


def reject_infile(params: ParamDict, header: drs_fits.Header,
                  bad_kind: str = 'pp') -> bool:
    """
    Using params and the header identify whether this file should be rejected
    (uses a googlesheet of True and False along with a key from the header

    :param params: ParamDict, the parameter dictionary of constants
    :param header: Header, the fits header of the file
    :param bad_kind: str, for now just 'pp' - changes the column that is used
    :return: True if file is bad (and should be skipped) or False if file is
             good
    """
    # set function name
    func_name = display_func('get_bad_list', __NAME__)
    # -------------------------------------------------------------------------
    # get parameters from params
    sheet_id = params['PP_BADLIST_SSID']
    worksheet = params['PP_BADLIST_SSWB']
    # TODO: Add in RV kind?
    if bad_kind == 'pp':
        header_col = params['PP_BADLIST_DRS_HKEY']
        value_col = params['PP_BADLIST_SS_VALCOL']
        mask_col = params['PP_BADLIST_SS_MASKCOL']
    else:
        header_col = params['PP_BADLIST_DRS_HKEY']
        value_col = params['PP_BADLIST_SS_VALCOL']
        mask_col = params['PP_BADLIST_SS_MASKCOL']
    # -------------------------------------------------------------------------
    # deal with no bad list
    cond1 = drs_text.null_text(header_col, ['None', ''])
    cond2 = drs_text.null_text(value_col, ['None', ''])
    cond3 = drs_text.null_text(mask_col, ['None', ''])
    # no header, value or mask column --> do not skip
    if cond1 or cond2 or cond3:
        return False
    # -------------------------------------------------------------------------
    # get header key
    if header_col in params:
        kw_header = params[header_col][0]
    else:
        wargs = [header_col]
        WLOG(params, 'warning', textentry('10-503-00019', args=wargs),
             sublevel=4)
        return False
    # -------------------------------------------------------------------------
    # get header key value
    if kw_header in header:
        value = header[kw_header]
    else:
        wargs = [kw_header, header_col]
        WLOG(params, 'warning', textentry('10-503-00020', args=wargs),
             sublevel=4)
        return False
    # -------------------------------------------------------------------------
    # get bad list table
    try:
        table = get_google_sheet(params, sheet_id, worksheet, cached=True)
    except Exception as e:
        # construct url for worksheet
        url = GOOGLE_BASE_URL.format(sheet_id, worksheet)
        wargs = [url, type(e), str(e), func_name]
        WLOG(params, 'warning', textentry('10-503-00021', args=wargs),
             sublevel=4)
        return False
    # if we have no entries return False
    if len(table[mask_col]) == 0:
        return False
    # convert mask column to bool
    if isinstance(table[mask_col][0], str):
        mask = np.array(table[mask_col]) == 'True'
    # if it is cached it wont be strings it will be bools
    else:
        mask = np.array(table[mask_col])
    # get value column
    values = np.array(table[value_col])
    # -------------------------------------------------------------------------
    # deal with no files being rejected
    if np.sum(mask) == 0:
        return False
    # if value is in values mask then we return True
    if value in values[mask]:
        return True
    else:
        return False


def get_google_sheet(params: ParamDict, sheet_id: str, worksheet: int = 0,
                     cached: bool = True) -> Table:
    """
    Load a google sheet from url using a sheet id (if cached = True and
    previous loaded - just loads from memory)

    :param params: ParamDict, parameter dictionary of constants
    :param sheet_id: str, the google sheet id
    :param worksheet: int, the worksheet id (defaults to 0)
    :param cached: bool, if True and previous loaded, loads from memory

    :return: Table, astropy table representation of google sheet
    """
    # set google cache table as global
    global GOOGLE_TABLES
    # set function name
    func_name = display_func('get_google_sheet', __NAME__)
    # construct url for worksheet
    url = GOOGLE_BASE_URL.format(sheet_id, worksheet)
    # deal with table existing
    if url in GOOGLE_TABLES and cached:
        return GOOGLE_TABLES[url]
    # get data using a request
    try:
        rawdata = requests.get(url)
    except Exception as e:
        # log error: Could not load table from url
        eargs = [url, type(e), str(e), func_name]
        WLOG(params, 'error', textentry('00-010-00009', args=eargs))
        return Table()
    # convert rawdata input table
    with warnings.catch_warnings(record=True) as _:
        tries = 0
        while tries < 10:
            # try to open table
            try:
                table = Table.read(rawdata.text, format='ascii')
                break
            # if this fails try again (but with a limit
            except InconsistentTableError as _:
                tries += 1
                # lets wait a little bit to try again
                time.sleep(2)
            # deal with no rows in table - assume this always gives a
            #   FileNotFoundErorr
            except FileNotFoundError:
                table = Table()
                break
    # need to deal with too many tries
    if tries >= 10:
        # log error: Could not load table from url: (Tried 10 times)
        eargs = [url, func_name]
        WLOG(params, 'error', textentry('00-010-00010', args=eargs))
    # add to cached storage
    GOOGLE_TABLES[url] = table
    # return table
    return table


def get_file_reject_list(params: ParamDict, column: str = 'PP') -> np.ndarray:
    """
    Query the googlesheet for rejection odometer codes and return
    an array of odometer codes to reject

    :param params: ParamDict, the parameter dictionary of constants
    :param column: str, the column to use for rejection (must be filled with
                   "TRUE"/"FALSE")

    :return: list of strings, the list of odometer codes for kind
    """
    # set function name
    func_name = display_func('get_reject_list', __NAME__)
    # get sheet id and worksheet number
    sheet_id = params['ODOCODE_REJECT_GSHEET_ID']
    workbook_id = params['ODOCODE_REJECT_GSHEET_NUM']
    # get column names
    ppcol = params['GL_R_PP_COL']
    rvcol = params['GL_R_RV_COL']
    odocol = params['GL_R_ODO_COL']
    # get reject table
    reject_table = get_google_sheet(params, sheet_id, workbook_id)
    # convert masks to boolean
    if ppcol in reject_table.colnames:
        reject_table[ppcol] = reject_table[ppcol] == 'TRUE'
    if rvcol in reject_table.colnames:
        reject_table[rvcol] = reject_table[rvcol] == 'TRUE'
    # deal with bad kind
    if column not in reject_table.colnames:
        # log error
        eargs = [column, func_name]
        WLOG(params, 'error', textentry('00-010-00008', args=eargs))
        # return empty array if error does not exit
        return np.array([])
    else:
        # get odocodes to be rejected
        odocodes = np.array(reject_table[odocol][reject_table[column]])
        # return rejection list
        return odocodes


# =============================================================================
# Define other functions
# =============================================================================
def quality_control1(params, snr_hotpix, infile, rms_list, log=True):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # ----------------------------------------------------------------------
    # print out SNR hotpix value
    WLOG(params, '', textentry('40-010-00006', args=[snr_hotpix]))
    # get snr_threshold
    snr_threshold = params['PP_CORRUPT_SNR_HOTPIX']
    # deal with printing corruption message
    if snr_hotpix < snr_threshold:
        # add failed message to fail message list
        fargs = [snr_hotpix, snr_threshold, infile.filename]
        fail_msg.append(textentry('40-010-00007', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(snr_hotpix)
    qc_names.append('snr_hotpix')
    qc_logic.append('snr_hotpix < {0:.5e}'.format(snr_threshold))
    # ----------------------------------------------------------------------
    # get rms threshold
    rms_threshold = params['PP_CORRUPT_RMS_THRES']
    # check
    if mp.nanmax(rms_list) > rms_threshold:
        # add failed message to fail message list
        fargs = [mp.nanmax(rms_list), rms_threshold, infile.filename]
        fail_msg.append(textentry('40-010-00008', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mp.nanmax(rms_list))
    qc_names.append('max(rms_list)')
    qc_logic.append('max(rms_list) > {0:.4e}'.format(rms_threshold))
    # ----------------------------------------------------------------------
    # check required exposure time
    exptime_frac = params['PP_BAD_EXPTIME_FRACTION']
    # get required exposure time
    required_exptime = infile.get_hkey('KW_EXPREQ')
    # get exposure time
    actual_exptime = infile.get_hkey('KW_EXPTIME')
    # calculate minimum required exposure time
    min_req_exptime = required_exptime * exptime_frac
    # check if actual exptime is good
    if actual_exptime < min_req_exptime:
        # add failed message
        fargs = [actual_exptime, min_req_exptime]
        fail_msg.append(textentry('40-010-00017', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(actual_exptime)
    qc_names.append('EXPTIME')
    qc_logic.append('EXPTIME < {0:.4e}'.format(min_req_exptime))
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        if log:
            WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        if log:
            for farg in fail_msg:
                WLOG(params, 'warning', textentry('40-005-10002') + farg,
                     sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def quality_control2(params: ParamDict, qc_params: list, image: np.ndarray,
                     dprtype: str) -> Tuple[list, int]:
    """
    Second quality control on preprocessing after correction

    :param params: ParamDict, parameter dictionary of constants
    :param qc_params: list of lists for quality control
    :param image: np.array (2D), the image to test
    :param dprtype: str, the DPRTYPE to test

    :return: tuple, 1. updated quality control, 2. int pass/fail
    """
    # set passed variable and fail message list
    fail_msg = []
    qc_values, qc_names, qc_logic, qc_pass = qc_params
    # get paramters from params
    dark_types = params.listp('PP_DARK_DPRTYPES', dtype=str)
    dark_thres = params['PP_DARK_THRES']
    # ----------------------------------------------------------------------
    # check if dark dark it is not science
    if dprtype in dark_types:
        # get the 90th percentile for this image
        value = mp.nanpercentile(image, 90)
        # if above threshold this is not a valid dark
        if value > dark_thres:
            qc_pass.append(0)
            margs = [dprtype, value, dark_thres]
            fail_msg.append(textentry('40-010-00023', args=margs))
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(value)
        qc_names.append('DARK_DPRTYPE_P90')
        qc_logic.append('DARK_DPRTYPE_P90 > {0:.3f}'.format(dark_thres))
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def _target_set_value(table, column, pos: int = 0,
                      null_value: Any = np.nan) -> Any:
    """
    Set a target value dealing with Null values
    """
    null_values = ['None', 'Null', '', '--']
    # get value
    value = table[column].iloc[pos]
    # test for null values
    if drs_text.null_text(value, null_values):
        return null_value
    else:
        return value


def _convert_units(params: ParamDict, key: str, value: float,
                   desired_unit: uu.Unit) -> float:
    """
    Convert units via params.instances[key].unit

    :param params:
    :param key:
    :param value:
    :param desired_unit:
    :return:
    """
    # get current units
    current_unit = params.instances[key].unit
    # if value is not finite don't worry about the units
    if not np.isfinite(value):
        return value
    # if our units are None don't worry about units
    if drs_text.null_text(current_unit, ['None', 'Null', '']):
        return value
    # get value with current units
    value = value * current_unit
    # try to convert units
    try:
        value = value.to(desired_unit)
    except Exception as _:
        # log error
        # TODO: move to language database
        emsg = 'Units for {0} to not match \nCurrent: {1} Desired: {2}'
        eargs = [key, current_unit, desired_unit]
        WLOG(params, 'error', emsg.format(*eargs))
    # return the updated value
    return float(value.value)

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # no main code
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================

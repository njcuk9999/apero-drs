#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-12 at 09:45

@author: cook
"""
import os
import warnings
from typing import Any, Tuple, Union

import numpy as np
import pandas as pd
from astropy import units as uu
from astropy.coordinates import EarthLocation, AltAz, ICRS
from astropy.coordinates import SkyCoord, Distance
from astropy.table import Table

from apero.base import base as apero_base
from apero.core import drs_database
from apero.core import drs_astrometrics
from apero.core import drs_rejection
from apero.instruments import select
from apero.instruments.default import instrument as instrument_mod
from apero.io import drs_fits
from apero.utils import drs_recipe
from aperocore import drs_lang
from aperocore import math as mp
from aperocore.base import base
from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc
from aperocore.core import drs_text
from aperocore.io import drs_io

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'preprocessing.gen_pp.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get time
Time, TimeDelta = base.Time, base.TimeDelta
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get function string
display_func = drs_misc.display_func
# Get the text types
textentry = drs_lang.textentry
# Get database
ObjectDatabase = drs_astrometrics.AstrometricDatabase
# get param dict
ParamDict = param_functions.ParamDict
Instrument = instrument_mod.Instrument
DrsRecipe = drs_recipe.DrsRecipe
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
def resolve_target(params: ParamDict, pconst: Instrument, shortname: str,
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
    null_rv = params['OBJ.CCF.RV_NULL_VAL']
    # get object name in header keyword
    hdr_objname = params['KW_OBJNAME'][0]
    # load database
    if database is None:
        database = ObjectDatabase(params, shortname)
        database.load_db()
    # -------------------------------------------------------------------------
    # deal with no objname and no header
    if objname is None and header is None:
        # print error: Must define ‘objname’ or ‘header’
        raise AperoCodedException(params, '00-010-00011')
    elif objname is None:
        if hdr_objname in header:
            objname = header[hdr_objname]
        else:
            # print error: Header must be fixed (header must contain {0})
            eargs = [hdr_objname]
            raise AperoCodedException(params, '00-010-00012', targs=eargs)
    # -------------------------------------------------------------------------
    # find correct name in the database (via objname or aliases)
    correct_objname, found = database.find_objname(objname)
    # -------------------------------------------------------------------------
    # get the full yaml entry for this cleaned objname (resolves any name)
    entry = database.get_entry(correct_objname)
    # flatten the yaml entry into a {legacy_col: value} dict so the existing
    # extraction logic below keeps working unchanged. Returns None if entry
    # was not found.
    legacy = drs_astrometrics.legacy_view(entry)
    # -------------------------------------------------------------------------
    # check if key columns have null values - if they do treat the entry as
    #   missing (matches the old behaviour where NULL OBJNAME/RA/DEC/PMRA/
    #   PMDE/EPOCH would drop the row)
    if legacy is not None:
        # if any of the required columns is null, drop the entry entirely
        for col in NON_NULL_OBJ_COLS:
            if drs_text.null_text(legacy.get(col), ['None', '', 'Null']):
                legacy = None
                break
    # -------------------------------------------------------------------------
    # now extract values from the legacy dict (or fall through to header)
    if legacy is not None:
        # ---------------------------------------------------------------------
        # try to use the yaml entry
        try:
            # get properties from parameters
            # object name is the cleaned object name
            objname = str(legacy['OBJNAME'])
            original_name = str(legacy['ORIGINAL_NAME'])
            # right ascension and declination in degrees
            ra_deg = float(legacy['RA_DEG'])
            ra_source = str(legacy['RA_SOURCE'])
            dec_deg = float(legacy['DEC_DEG'])
            dec_source = str(legacy['DEC_SOURCE'])
            # epoch in JD
            epoch = float(legacy['EPOCH'])
            # pmra and pmde in mas/yr
            pmra = float(legacy['PMRA'])
            pmra_source = str(legacy['PMRA_SOURCE'])
            pmde = float(legacy['PMDE'])
            pmde_source = str(legacy['PMDE_SOURCE'])
            # parallax in mas (may not be present)
            plx_val = legacy.get('PLX')
            plx = float(plx_val) if plx_val is not None else np.nan
            plx_source = str(legacy.get('PLX_SOURCE') or '')
            # RV in km/s (may not be present)
            rv_val = legacy.get('RV')
            rv = float(rv_val) if rv_val is not None else np.nan
            rv_source = str(legacy.get('RV_SOURCE') or '')
            # Teff in K (may not be present)
            teff_val = legacy.get('TEFF')
            teff = float(teff_val) if teff_val is not None else np.nan
            teff_source = str(legacy.get('TEFF_SOURCE') or '')
            # spectral type (may not be present)
            sp_type = str(legacy.get('SP_TYPE') or '')
            sp_source = str(legacy.get('SP_SOURCE') or '')
            # data source is "database" and the data_date column has no yaml
            # equivalent yet (DATE_ADDED is not stored)
            data_source = 'database'
            data_date = str(legacy.get('DATE_ADDED') or '')
            # mark resolved as complete
            resolved = True

        except Exception as e:
            # warn msg: Cannot use object database entry for {0}.\n\t{1}: {2}'
            eargs = [correct_objname, type(e), str(e)]
            WLOG(params, 'warning', textentry('10-010-00008', args=eargs))
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
        wargs = [correct_objname]
        WLOG(params, 'warning', textentry('10-010-00005', args=wargs),
             sublevel=7)
        # get properties from parameters
        # object name is the cleaned object name to be inline database sources
        objname = str(correct_objname)
        original_name = str(header[params['KW_OBJECTNAME'][0]])
        # right ascension and declination in degrees
        ra_deg = float(header[params['KW_OBJRA'][0]])
        ra_source = 'header'
        dec_deg = float(header[params['KW_OBJDEC'][0]])
        dec_source = 'header'
        # ---------------------------------------------------------------------
        # epoch needs to be converted based on instrument (should be in JD)
        epoch = float(pconst.GET_EPOCH(params, header))
        # ---------------------------------------------------------------------
        # pmra
        kw_pmra = params['KW_OBJRAPM'][0]
        # make sure RA is in header
        if kw_pmra in header:
            pmra = float(header[params['KW_OBJRAPM'][0]])
            pmra = _convert_units(params, 'KW_OBJRAPM', pmra, uu.mas/uu.yr)
            pmra_source = 'header'
        else:
            pmra = 0.0
            pmra_source = 'null'
        # ---------------------------------------------------------------------
        # pmde
        kw_pmdec = params['KW_OBJDECPM'][0]
        if kw_pmdec in header:
            pmde = float(header[params['KW_OBJDECPM'][0]])
            pmde = _convert_units(params, 'KW_OBJDECPM', pmde, uu.mas/uu.yr)
            pmde_source = 'header'
        else:
            pmde = 0.0
            pmde_source = 'null'
        # ---------------------------------------------------------------------
        # parallax in mas (may not be present)
        plx = float(header.get(params['KW_PLX'][0], np.nan))
        plx = _convert_units(params, 'KW_PLX', plx, uu.mas)
        plx_source = 'header'
        # ---------------------------------------------------------------------
        # RV in km/s (may not be present)
        rv = float(header.get(params['KW_INPUTRV'][0], np.nan))
        rv = _convert_units(params, 'KW_INPUTRV', rv, uu.km / uu.s)
        rv_source = 'header'
        # ---------------------------------------------------------------------
        # Teff in K (may not be present)
        teff = float(header.get(params['KW_OBJ_TEMP'][0], np.nan))
        teff_source = 'header'
        # ---------------------------------------------------------------------
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
    # add a geometric airmass
    airmass = get_geometric_airmass(ra_deg, dec_deg, plx, pmra, pmde, epoch,
                                    params['OBS.LAT'], params['OBS.LONG'],
                                    params['OBS.ALT'],
                                    header[params['KW_MID_OBS_TIME'][0]])
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
    # add the geometric airmass
    header.set_key(params, 'KW_DRS_AIRMASS', value=airmass)
    # -------------------------------------------------------------------------
    # must update DRSOBJN
    header.set_key(params, 'KW_OBJNAME', value=objname)
    # -------------------------------------------------------------------------
    # return the header
    return header


def propagate_coords(ra: float, dec: float, plx: float, pmra: float,
                     pmde: float, epoch: float, obs_time: Time) -> SkyCoord:
    """
    Propagate coordinates to the observation time (from the epoch time)

    :param ra: float, right ascension in degrees
    :param dec: float, declination in degrees
    :param plx: float, parallax in mas
    :param pmra: float, proper motion in RA in mas/yr
    :param pmde: float, proper motion in Dec in mas/yr
    :param epoch: float, the epoch of the coordinates
    :param obs_time: astropy.time.Time, the observation time

    :return: astropy.coordinates.SkyCoord, the propagated coordinates
    """
    # deal with distance
    if plx <= 0:
        distance = None
    else:
        distance = Distance(parallax=plx * uu.mas)
    # need to propagate ra and dec to J2000
    coords = SkyCoord(ra=ra * uu.deg,
                      dec=dec * uu.deg,
                      distance=distance,
                      pm_ra_cosdec=pmra * uu.mas / uu.yr,
                      pm_dec=pmde * uu.mas / uu.yr,
                      obstime=Time(epoch, format='jd'))
    # work out the delta time between epoch and J2000.0
    with warnings.catch_warnings(record=True) as _:
        jepoch = Time(epoch, format='jd')
        delta_time = (obs_time.jd - jepoch.jd) * uu.day
    # get the coordinates
    with warnings.catch_warnings(record=True) as _:
        # center the image on the current coordinates
        curr_coords = coords.apply_space_motion(dt=delta_time)
    # return some stuff
    return curr_coords


def get_geometric_airmass(ra: float, dec: float, plx: float, pmra: float,
                          pmde: float, epoch: float,
                          lat: float, lon: float,
                          alt: float, mjd_mid: float) -> float:
    """
    Get the geometric airmass for a given object

    :param ra: float, right ascension in degrees
    :param dec: float, declination in degrees
    :param plx: float, parallax in mas
    :param pmra: float, proper motion in RA in mas/yr
    :param pmde: float, proper motion in Dec in mas/yr
    :param epoch: float, the epoch of the coordinates
    :param lat: float, latitude in degrees
    :param lon: float, longitude in degrees
    :param alt: float, altitude in meters
    :param mjd_mid: float, the mid point of the observation in MJD

    :return: float, the geometric airmass
    """
    # deal with no ra or dec
    if not np.isfinite(ra) or not np.isfinite(dec):
        return np.nan
    # get the earth location using predefined values
    loc = EarthLocation(lat=lat * uu.deg, lon=lon * uu.deg,
                        height=alt * uu.m)
    time = Time(mjd_mid, format='mjd')
    # get the AltAz frame for the telescope if looking at this object
    aa = AltAz(location=loc, obstime=time)
    # update the coordinates to the observation time (tiny affect)
    skycoord = propagate_coords(ra, dec, plx, pmra, pmde, epoch, time)
    # get the coordinates in IRCS frame
    icrs_coord = ICRS(ra=skycoord.ra, dec=skycoord.dec)
    # account for proper motion and parallax
    aa_coord = icrs_coord.transform_to(aa)
    # get the airmass from the sec(z) of the coords
    airmass = aa_coord.secz.value
    # return the updated airmass
    return airmass


def get_obj_reject_list(params: ParamDict) -> np.ndarray:
    """
    Get object names to reject from the local astrometric reject list.

    This reads ``reject_list.yaml`` from the astrometric assets directory
    and returns the union of object names and aliases (cleaned).

    :param params: ParamDict, parameter dictionary of constants

    :return: np.array 1D, the list of reject object names
    """
    # load the astrometric database to discover the local path
    objdbm = ObjectDatabase(params, shortname='OBJ-REJECT')
    objdbm.load_db()
    reject_path = os.path.join(objdbm.path, 'reject_list.yaml')
    # no reject list file means no rejected objects
    if not os.path.exists(reject_path):
        return np.array([])
    # read yaml reject list
    try:
        reject_data = drs_astrometrics.AstrometricDatabase._read_yaml(
            reject_path)
    except Exception as e:
        wmsg = 'Cannot read object reject list: {0}. {1}: {2}'
        wargs = [reject_path, type(e).__name__, str(e)]
        WLOG(params, 'warning', wmsg.format(*wargs), sublevel=3)
        return np.array([])
    objects = reject_data.get('OBJECTS', dict())
    if not isinstance(objects, dict) or len(objects) == 0:
        return np.array([])
    reject_objs = []
    for apero_name, entry in objects.items():
        clean_name = drs_astrometrics.clean_object(apero_name)
        if clean_name not in ['', 'Null']:
            reject_objs.append(clean_name)
        aliases = ''
        if isinstance(entry, dict):
            aliases = entry.get('ALIASES', '')
        if isinstance(aliases, list):
            alias_list = aliases
        else:
            alias_list = str(aliases).split('|')
        for alias in alias_list:
            clean_alias = drs_astrometrics.clean_object(alias)
            if clean_alias not in ['', 'Null']:
                reject_objs.append(clean_alias)
    if len(reject_objs) == 0:
        return np.array([])
    return np.unique(np.array(reject_objs, dtype=str))


def reject_infile(params: ParamDict, recipe: DrsRecipe,
                  header: drs_fits.Header, bad_kind: str = 'pp') -> bool:
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
    # func_name = display_func('get_bad_list', __NAME__)
    # -------------------------------------------------------------------------
    # get parameters from params
    if bad_kind == 'pp':
        header_col = params['OBJ.LIST.REJECT_DRS_HKEY']
        value_col = params['OBJ.LIST.REJECT_VALCOL']
        mask_col = params['OBJ.LIST.REJECT_MASKCOL']
    else:
        header_col = params['OBJ.LIST.REJECT_DRS_HKEY']
        value_col = params['OBJ.LIST.REJECT_VALCOL']
        mask_col = params['OBJ.LIST.REJECT_MASKCOL']
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
    # get reject database
    rejectdbm = drs_rejection.RejectDatabase(params, recipe.shortname)
    rejectdbm.load_db()
    # get reject table
    rtable = rejectdbm.get_entries('*')
    if not isinstance(rtable, pd.DataFrame):
        return False
    if mask_col not in list(rtable.columns):
        return False
    if value_col not in list(rtable.columns):
        return False
    # -------------------------------------------------------------------------
    # if we have no entries return False
    if len(rtable[mask_col]) == 0:
        return False
    # convert mask column to bool
    mask = np.array(rtable[mask_col], dtype=bool)
    # get value column
    values = np.array(rtable[value_col])
    # -------------------------------------------------------------------------
    # deal with no files being rejected
    if np.sum(mask) == 0:
        return False
    # if value is in values mask then we return True
    if value in values[mask]:
        return True
    else:
        return False


def get_file_reject_list(params: ParamDict, recipe: DrsRecipe,
                         column: str = 'PP') -> np.ndarray:
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
    # get reject database
    rejectdbm = drs_rejection.RejectDatabase(params, recipe.shortname)
    rejectdbm.load_db()
    # get reject table
    rtable = rejectdbm.get_entries('*')
    if not isinstance(rtable, pd.DataFrame):
        return np.array([])
    if len(rtable) == 0:
        return np.array([])
    # deal with bad kind
    if column not in list(rtable.columns):
        # log error
        eargs = [column, func_name]
        raise AperoCodedException(params, '00-010-00008', targs=eargs)
    else:
        # get the reject mask for the column
        idmask = np.array(rtable[column], dtype=bool)
        # get the reject list
        _reject_list = np.array(rtable['IDENTIFIER'], dtype=str)[idmask]
        # storage for return
        reject_list = drs_misc.clean_reject_list(_reject_list)
        # return rejection list
        return np.array(reject_list)


def get_areldate(params: ParamDict, header: drs_fits.Header,
                 release_type: str = 'apero') -> str:
    """
    Get the APERO release date from:

    Option 1. The google sheet (based on run id)
    Option 2. The pseudo const (raw + time delta)

    :param params: ParamDict, parameter dictionary of constants
    :param header: Header, fits header (required for KW_RUN_ID and KW_IRELDATE)

    :return: str, the YYYY-MM-DD hh:mm:ss.ss representation of the apero
             release date
    """
    # set function name
    func_name = display_func('get_areldate', __NAME__)
    # get psuedo constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # set apero release date to None to start
    areldate = None
    # get header key
    run_id = header.get(params['KW_RUN_ID'][0], None)
    # -------------------------------------------------------------------------
    # deal with release type
    if release_type == 'apero':
        gsheet_acol = params['DATA.AREL_GSHEET_ACOL']
        delta_key = 'DATA.AREL_ADELTA'
    elif release_type == 'lbl':
        gsheet_acol = params['DATA.AREL_GSHEET_LCOL']
        delta_key = 'DATA.AREL_LDELTA'
    else:
        emsg = 'Invalid release type = {0} (function = {1})'
        eargs = [release_type, func_name]
        raise AperoCodedException(params, None, targs=eargs,
                                  message=emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # option 1: Check the google sheet for an entry
    # -------------------------------------------------------------------------
    # if we have no run id we can't do this
    if run_id is not None:
        # clean run id
        run_id = str(run_id).strip()
        # get parameters from params
        gsheet_url = params['DATA.AREL_GSHEET_URL']
        gsheet_id = params['DATA.AREL_GSHEET_ID']
        # get areldate list google sheets
        try:
            adate_table = drs_database.get_google_sheet(params, gsheet_url,
                                                        gsheet_id)
            # set areldate if in table
            if run_id in list(adate_table['RUN_ID']):
                # get positions in table
                mask = adate_table['RUN_ID'] == str(run_id)
                # deal with astropy table being masked (and apply this mask)
                if hasattr(adate_table[gsheet_acol], 'mask'):
                    mask &= ~adate_table[gsheet_acol].mask
                # don't try if the mask is empty
                if not np.sum(mask) == 0:
                    # get the last appearing row in googlesheet
                    areldate = adate_table[gsheet_acol][mask][-1]

        # any exception here should return a warning and a empty array
        except Exception as e:
            wmsg = 'Cannot read areldate list {0}.'
            wargs = [GOOGLE_BASE_URL.format(gsheet_url, gsheet_id),
                     type(e), str(e)]
            WLOG(params, 'warning', wmsg.format(*wargs), sublevel=3)

    # -------------------------------------------------------------------------
    # option 2: If we have apero areldate + time delta
    # -------------------------------------------------------------------------
    if areldate is None:
        areldate = reldate_convert(params, header, delta_key)

    # -------------------------------------------------------------------------
    # option 3: if not set from googlesheet set from raw areldate + time delta
    # -------------------------------------------------------------------------
    if areldate is None:
        areldate = pconst.GET_AREL_DATE(params, header, delta_key=delta_key)

    # -------------------------------------------------------------------------
    # return the apero release date
    return areldate


def reldate_convert(params: ParamDict, header: drs_fits.Header,
                    delta_key: str) -> Union[str, None]:
    """
    Take an APERO release date and push it to the new format

    (back to raw then forward to new format) using the time delta

    :param params: ParamDict, parameter dictionary of constants
    :param header: fits header, to test for key frmo
    :param delta_key: str, the constant containing the time delta required

    :return:
    """
    # get keyword
    kw_reldate = params['KW_ARELDATE'][0]
    kw_areldate_datatype = 'iso'
    # get the time delta from APERO
    tdelta_in = params['DATA.AREL_ADELTA']
    tdelta_out = params[delta_key]
    # deal with no areldate in header --> return
    if kw_reldate not in header:
        return None
    # deal with tdelta_in the same as tdelta_out (just return the current value)
    if tdelta_in == tdelta_out:
        return header[kw_reldate]
    # get and convert reldate
    _areldate = Time(header[kw_reldate], format=kw_areldate_datatype)
    # get the default time to add to instrument release date
    time_delta_in = TimeDelta(tdelta_in * uu.year)
    time_delta_out = TimeDelta(tdelta_out * uu.year)
    # convert the areldate to the new time delta
    areldate = _areldate - time_delta_in + time_delta_out
    # return the areldate in ISO format
    return areldate.iso


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
    snr_threshold = params['PP.CORRUPT_SNR_HOTPIX']
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
    rms_threshold = params['PP.CORRUPT_RMS_THRES']
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
    exptime_frac = params['PP.BAD_EXPTIME_FRACTION']
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
    qc_names, qc_values, qc_logic, qc_pass = qc_params
    # get paramters from params
    dark_types = params['PP.DARK_DPRTYPES']
    dark_thres = params['PP.DARK_THRES']
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
    # noinspection PyBroadException
    try:
        value = value.to(desired_unit)
    except Exception as _:
        # log error: Units for {0} do not match Current: {1} Desired: {2}
        eargs = [key, current_unit, desired_unit]
        raise AperoCodedException(params, '00-001-00059', targs=eargs)
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
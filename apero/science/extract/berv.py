#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-10-2020-10-29 15:40

@author: cook
"""
from astropy import units as uu
import numpy as np
import os
from typing import List, Tuple, Union
import warnings

from apero.base import base
from apero.core.core import drs_exceptions
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core import math as mp
from apero.io import drs_lock
from apero.io import drs_path
from apero.io import drs_fits
from apero.science.extract import bervest


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.berv.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Astropy Time and Time Delta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# get param dict
ParamDict = constants.ParamDict
# get drs file
DrsFitsFile = drs_file.DrsFitsFile
# Get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
class BaryCorrpyException(Exception):
    """Raised when config file is incorrect"""
    pass


def get_berv(params: ParamDict, infile: Union[DrsFitsFile, None] = None,
             header: Union[drs_fits.Header, None] = None, log: bool = True,
             warn: bool = False, force: bool = False,
             dprtypes: Union[List[str], None] = None,
             kind: Union[str, None] = None) -> ParamDict:
    """
    Get the BERV (either from header or calculate it using header parameters)
    must define either 'infile' (with a header) or a 'header' directly.

    :param params: ParamDict, parameter dictionary of constants
    :param infile: DrsFitsFile with a valid header - if set uses parameters
                   from this header
    :param header: Header, drs_fits.Header instance - if infile not set uses
                   parameters from this header
    :param log: bool, if True logs calculation of BERV
    :param warn: bool, if True add warnings about BERV correction
    :param force: bool, if True will calculate BERV even when found in the
                  if False (default) uses BERV in header if found
    :param dprtypes: list of strings or None, overrides
                     EXT_ALLOWED_BERV_DPRTYPES if set (this is the dprtypes
                     for which a BERV should be calculated)
    :param kind: str, either 'barycorrpy' or 'pyasl' or 'None' - the mode
                 by which to calculate BERV

    :return: ParamDict of BERV parameters
    """
    # set function name
    func_name = __NAME__ + '.get_berv()'
    # log progress
    if log:
        WLOG(params, 'info', textentry('40-016-00017'))
    # get parameters from params and kwargs
    dprtypes = pcheck(params, 'EXT_ALLOWED_BERV_DPRTYPES', func=func_name,
                      mapf='list', dtype=str, override=dprtypes)
    kind = pcheck(params, 'EXT_BERV_KIND', func=func_name, override=kind)
    # lets store properties in a param dict
    bprops = ParamDict()
    # -------------------------------------------------------------------------
    # get header
    # -------------------------------------------------------------------------
    if infile is not None:
        header = infile.header
    if header is None:
        WLOG(params, 'error', 'Either header or infile must be defined')
    # -------------------------------------------------------------------------
    # get current properties from header
    # -------------------------------------------------------------------------
    bprops = get_keys_from_header(params, header, bprops)
    # -------------------------------------------------------------------------
    # Deal with wrong BERV type
    # -------------------------------------------------------------------------
    # do not try to calculate berv for specific DPRTYPES
    if bprops['DPRTYPE'] not in dprtypes:
        # log that we are skipping due to dprtype
        WLOG(params, '', textentry('40-016-00018', args=[bprops['DPRTYPE']]))
        # all entries returns are empty
        bprops = assign_use_berv(bprops, use=False)
        # return bprops
        return bprops
    if kind not in ['pyasl', 'barycorrpy']:
        # log that we are skipping due to user
        WLOG(params, '', textentry('40-016-00019'))
        # all entries returns are empty
        return assign_use_berv(params, use=False)
    # -------------------------------------------------------------------------
    # Check if we already have BERV
    # -------------------------------------------------------------------------
    # check if we have berv
    bprops = assign_use_berv(bprops)
    # if we have a berv and we are not forcing then return values from header
    if bprops['USE_BERV'] is not None and not force:
        if np.isfinite(bprops['USE_BERV']):
            return bprops
    # -------------------------------------------------------------------------
    # Set up times
    # -------------------------------------------------------------------------
    # get observation time
    obstime = Time(bprops['MJDMID'], format=bprops['MJDMID_FMT'])
    # for the maximum peak to peak need an array of times
    times = obstime.jd + np.arange(0, 365, 5.0 / 3.0)
    # update OBS_TIME
    bprops['OBS_TIME'] = obstime.jd
    bprops['OBS_TIME_METHOD'] = 'header[MJDMID]'
    bprops['OBS_TIMES'] = times
    # ----------------------------------------------------------------------
    # try to run barcorrpy
    # ----------------------------------------------------------------------
    if kind == 'barycorrpy':
        try:
            # --------------------------------------------------------------
            # calculate berv/bjd
            bervs, bjds = use_barycorrpy(params, bprops['OBS_TIME'], bprops,
                                         iteration=0)
            # --------------------------------------------------------------
            # calculate max berv (using pyasl as it is faster)
            bervs_, bjds_ = use_pyasl(params, bprops['OBS_TIMES'],
                                      bprops, quiet=True)
            bervmax = mp.nanmax(np.abs(bervs_))
            # --------------------------------------------------------------
            # calculate berv derivative (add 1 second)
            deltat = (1*uu.s).to(uu.day).value
            berv1, bjd1 = use_barycorrpy(params, bprops['OBS_TIME'] + deltat,
                                         bprops, iteration=1)
            dberv = np.abs(berv1[0] - bervs[0])
            # --------------------------------------------------------------
            # update parameters
            bprops['BERV'] = bervs[0]
            bprops['BJD'] = bjds[0]
            bprops['BERV_MAX'] = bervmax
            bprops['DBERV'] = dberv
            # set source
            bprops['BERVSOURCE'] = 'barycorrpy'
            bprops.set_sources(['BERV', 'BJD', 'BERV_MAX', 'DBERV',
                                'BERVSOURCE'], func_name)

        except BaryCorrpyException as bce:
            if warn:
                WLOG(params, 'warning', str(bce))
            else:
                pass
        # check if we have berv a good berv
        bprops = assign_use_berv(bprops)
        if bprops['USE_BERV'] is not None:
            if np.isfinite(bprops['USE_BERV']):
                return bprops
    # -------------------------------------------------------------------------
    # if we are still here must use pyasl BERV estimate
    # -------------------------------------------------------------------------
    # calculate berv/bjd
    bervs, bjds = use_pyasl(params, bprops['OBS_TIMES'], props=bprops)
    # --------------------------------------------------------------
    # calculate max berv
    bervmax = mp.nanmax(np.abs(bervs))
    # --------------------------------------------------------------
    # calculate berv derivative (add 1 second)
    deltat = (1 * uu.s).to(uu.day).value
    berv1, bjd1 = use_pyasl(params, [bprops['OBS_TIME'] + deltat], bprops)
    dberv = np.abs(berv1[0] - bervs[0])
    # --------------------------------------------------------------
    # update parameters
    bprops['BERV_EST'] = bervs[0]
    bprops['BJD_EST'] = bjds[0]
    bprops['BERV_MAX_EST'] = bervmax
    bprops['DBERV_EST'] = dberv
    # set source
    bprops['BERVSOURCE'] = 'pyasl'
    bprops.set_sources(['BERV_EST', 'BJD_EST', 'BERV_MAX_EST', 'DBERV_EST',
                        'BERVSOURCE'], func_name)
    # check if we have berv a good berv
    bprops = assign_use_berv(bprops)
    # return bprops
    return bprops


def get_keys_from_header(params: ParamDict, header: drs_fits.Header,
                         bprops: ParamDict) -> ParamDict:
    """
    Get all keys currently in the header related to the BERV calculation

    :param params: ParamDict, the parameter dictionary of constants
    :param header: drs_fits.Header - the header instance
    :param bprops: ParamDict, the BERV properties already loaded

    :return: ParamDict, the updated BERV properties
    """
    # make sure header is drs_fits.header
    if not isinstance(header, drs_fits.Header):
        header = drs_fits.Header(header)
    # get dprtype
    bprops['DPRTYPE'] = header.get(params['KW_DPRTYPE'][0], None)
    bprops.set_source('DPRTYPE', 'header')
    # get the mid exposure time
    bprops['MJDMID'] = header.get(params['KW_MID_OBS_TIME'][0], np.nan)
    bprops.set_source('MJDMID', 'header')
    bprops['MJDMID_FMT'] = params.instances['KW_MID_OBS_TIME'].datatype
    bprops.set_source('MJDMID_FMT', 'KW_MID_OBS_TIME')
    # get longitude, latitude, altitude of the telescope
    bprops['DRS_LONG'] = params['OBS_LONG']
    bprops.set_source('DRS_LONG', 'params[OBS_LONG]')
    bprops['DRS_LAT'] = params['OBS_LAT']
    bprops.set_source('DRS_LAT', 'params[OBS_LAT]')
    bprops['DRS_ALT'] = params['OBS_ALT']
    bprops.set_source('DRS_ALT', 'params[OBS_ALT]')
    # get barycorrpy berv measurement (or set NaN)
    bprops['BERV'] = header.get(params['KW_BERV'][0], np.nan)
    bprops.set_source('BERV', 'header')
    # get barycorrpy BJD measurment (or set NaN)
    bprops['BJD'] = header.get(params['KW_BJD'][0], np.nan)
    bprops.set_source('BJD', 'header')
    # get barycorrpy BERVMAX (or set NaN)
    bprops['BERV_MAX'] = header.get(params['KW_BERVMAX'][0], np.nan)
    bprops.set_source('BERV_MAX', 'header')
    # get barycorrpy berv diff (or set NaN)
    bprops['DBERV'] = header.get(params['KW_DBERV'][0], np.nan)
    bprops.set_source('DBERV', 'header')
    # get berv source
    bprops['BERVSOURCE'] = header.get(params['KW_BERVSOURCE'][0], 'None')
    bprops.set_source('BERVSOURCE', 'header')
    # get pyasl (berv estimate) BERV measurement (or set NaN)
    bprops['BERV_EST'] = header.get(params['KW_BERV_EST'][0], np.nan)
    bprops.set_source('BERV_EST', 'header')
    # get pyasl (berv estimate) BJD measurement (or set NaN)
    bprops['BJD_EST'] = header.get(params['KW_BJD_EST'][0], np.nan)
    bprops.set_source('BJD_EST', 'header')
    # get pyasl (berv estimate) BJD measurement (or set NaN)
    bprops['BERV_MAX_EST'] = header.get(params['KW_BERVMAX_EST'][0], np.nan)
    bprops.set_source('BERV_MAX_EST', 'header')
    # get the berv diff from pyasl (or set NaN)
    bprops['DBERV_EST'] = header.get(params['KW_DBERV_EST'][0], np.nan)
    bprops.set_source('DBERV_EST', 'header')
    # get the observation time and method parameters
    bprops['OBSTIME'] = header.get(params['KW_BERV_OBSTIME'][0], np.nan)
    bprops['OBSTIMEMETHOD'] = header.get(params['KW_BERV_OBSTIME_METHOD'][0],
                                         'None')
    bprops.set_source('OBSTIME', 'header')
    bprops.set_source('OBSTIMEMETHOD', 'header')
    # get object name and source
    bprops['DRS_OBJNAME'] = header.get(params['KW_DRS_OBJNAME'][0], np.nan)
    bprops.set_source('DRS_OBJNAME',
                      header.get(params['KW_DRS_OBJNAME_S'][0], 'None'))
    # get gaia id and source
    bprops['DRS_GAIAID'] = header.get(params['KW_DRS_GAIAID'][0], np.nan)
    bprops.set_source('DRS_GAIAID',
                      header.get(params['KW_DRS_GAIAID_S'][0], 'None'))
    # add the ra and source
    bprops['DRS_RA'] = header.get(params['KW_DRS_RA'][0], np.nan)
    bprops.set_source('DRS_RA', header.get(params['KW_DRS_RA_S'][0], 'None'))
    # add the dec and source
    bprops['DRS_DEC'] = header.get(params['KW_DRS_DEC'][0], np.nan)
    bprops.set_source('DRS_DEC', header.get(params['KW_DRS_DEC_S'][0], 'None'))
    # add the pmra
    bprops['DRS_PMRA'] = header.get(params['KW_DRS_PMRA'][0], np.nan)
    bprops.set_source('DRS_PMRA',
                      header.get(params['KW_DRS_PMRA_S'][0], 'None'))
    if not np.isfinite(bprops['DRS_PMRA']):
        bprops['DRS_PMRA'] = 0.0
        bprops.set_source('DRS_PMRA', 'func-default')
    # add the pmde
    bprops['DRS_PMDE'] = header.get(params['KW_DRS_PMDE'][0], np.nan)
    bprops.set_source('DRS_PMDE',
                      header.get(params['KW_DRS_PMDE_S'][0], 'None'))
    if not np.isfinite(bprops['DRS_PMDE']):
        bprops['DRS_PMDE'] = 0.0
        bprops.set_source('DRS_PMDE', 'func-default')
    # add the plx
    bprops['DRS_PLX'] = header.get(params['KW_DRS_PLX'][0], np.nan)
    bprops.set_source('DRS_PLX', header.get(params['KW_DRS_PLX_S'][0], 'None'))
    if not np.isfinite(bprops['DRS_PLX']):
        bprops['DRS_PLX'] = 0.0
        bprops.set_source('DRS_PLX', 'func-default')
    # add the rv
    bprops['DRS_RV'] = header.get(params['KW_DRS_RV'][0], np.nan)
    bprops.set_source('DRS_RV', header.get(params['KW_DRS_RV_S'][0], 'None'))
    if not np.isfinite(bprops['DRS_RV']):
        bprops['DRS_RV'] = 0.0
        bprops.set_source('DRS_RV', 'func-default')
    # add the gmag
    bprops['DRS_GMAG'] = header.get(params['KW_DRS_GMAG'][0], np.nan)
    bprops.set_source('DRS_GMAG',
                      header.get(params['KW_DRS_GMAG_S'][0], 'None'))
    # add the bpmag
    bprops['DRS_BPMAG'] = header.get(params['KW_DRS_BPMAG'][0], np.nan)
    bprops.set_source('DRS_BPMAG',
                      header.get(params['KW_DRS_BPMAG_S'][0], 'None'))
    # add the rpmag
    bprops['DRS_RPMAG'] = header.get(params['KW_DRS_RPMAG'][0], np.nan)
    bprops.set_source('DRS_RPMAG',
                      header.get(params['KW_DRS_RPMAG_S'][0], 'None'))
    # add the epoch
    bprops['DRS_EPOCH'] = header.get(params['KW_DRS_EPOCH'][0], np.nan)
    bprops.set_source('DRS_EPOCH',
                      header.get(params['KW_DRS_EPOCH_S'][0], 'None'))
    # add the teff
    bprops['DRS_TEFF'] = header.get(params['KW_DRS_TEFF'][0], np.nan)
    bprops.set_source('DRS_TEFF',
                      header.get(params['KW_DRS_TEFF_S'][0], 'None'))

    # return bprops
    return bprops


def assign_use_berv(bprops: ParamDict, use=True) -> ParamDict:
    """
    Assigns the USE_BERV keywords (based on whether pyasl was used (EST) or
    barycorrypy was used)

    :param bprops: ParamDict, the BERV properties already loaded
    :param use: bool, if False - then sets all USE_BERV parameters to None
                else decides whether pyasl was used (EST) or barycorrypy was
                used

    :return: ParamDict, the updated BERV properties
    """
    # set function name
    func_name = __NAME__ + '.assign_use_berv()'
    # -------------------------------------------------------------------------
    # need to decide which values should be used (and report if we are using
    #   estimate)
    cond = (bprops['BERV'] is not None and np.isfinite(bprops['BERV']))
    cond &= (bprops['BJD'] is not None and np.isfinite(bprops['BJD']))
    cond &= (bprops['BERV_MAX'] is not None and np.isfinite(bprops['BERV_MAX']))
    # Case 1: Not BERV used
    if not use:
        bprops['USE_BERV'] = None
        bprops['USE_BJD'] = None
        bprops['USE_BERV_MAX'] = None
        bprops['USED_ESTIMATE'] = None
        psource = '{0} [{1}]'.format(func_name, 'None')
    # Case 2: pyasl used
    elif (not cond) or bprops['BERVSOURCE'] == 'pyasl':
        bprops['USE_BERV'] = bprops['BERV_EST']
        bprops['USE_BJD'] = bprops['BJD_EST']
        bprops['USE_BERV_MAX'] = bprops['BERV_MAX_EST']
        bprops['USED_ESTIMATE'] = True
        psource = '{0} [{1}]'.format(func_name, 'pyasl')
    # Case 3: Barycorrpy used
    else:
        # set parameters
        bprops['USE_BERV'] = bprops['BERV']
        bprops['USE_BJD'] = bprops['BJD']
        bprops['USE_BERV_MAX'] = bprops['BERV_MAX']
        bprops['USED_ESTIMATE'] = False
        psource = '{0} [{1}]'.format(func_name, 'barycorrpy')
    # set source
    keys = ['USE_BERV', 'USE_BJD', 'USE_BERV_MAX', 'USED_ESTIMATE']
    bprops.set_sources(keys, psource)
    # return updated bprops
    return bprops


def use_barycorrpy(params: ParamDict, times: np.ndarray, props: ParamDict,
                   iteration: int = 0, berv_est: Union[float, None] = None,
                   bc_dir: Union[str, None] = None,
                   iersfile: Union[str, None] = None,
                   package: Union[str, None] = None
                   ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Use the barycorrpy module to calculate BERV/BJD

    :param params: ParamDict - parameter dictionary of constants
    :param times: numpy array, the list of times [in julien date]
    :param props: ParamDict - the berv input parameters (ra/dec/pmra/pmde etc)
    :param iteration: int, which iteration of the barycorrpy calculation it is
                      (for logging)
    :param berv_est: float, an estimate of the pyasl BERV uncertainties
                     (for logging)
    :param bc_dir: str, the berv directory where the IERSFILE should be located
    :param iersfile: str, the IERSFILE - if using a custom file
    :param package: str, the package name (APERO)

    :return: two numpy arrays, the array of bervs for the times [km/s], and
             array of bjds [julien date]
    """
    # set function name
    func_name = __NAME__ + '.use_barycorrpy()'
    # get estimate accuracy
    estimate = pcheck(params, 'EXT_BERV_EST_ACC', func=func_name,
                      override=berv_est)
    # get barycorrpy directory
    bc_dir = pcheck(params, 'EXT_BERV_BARYCORRPY_DIR', func=func_name,
                    override=bc_dir)
    iersfile = pcheck(params, 'EXT_BERV_IERSFILE', func=func_name,
                      override=iersfile)
    package = pcheck(params, 'DRS_PACKAGE', func=func_name, override=package)
    # make barycorrpy directory an absolute path
    bc_dir = drs_path.get_relative_folder(params, package, bc_dir)
    # if we don't have an epoch at this point in time we assume the
    #    epoch is the time of observation (i.e. the RA and DEC are where the
    #    telescope was pointing)
    if props['DRS_EPOCH'] in ['None', 'Null', '', np.nan]:
        epoch = Time(props['OBS_TIME'], format='jd')
    # epoch must be in jd
    else:
        epoch_fmt = params.instances['KW_DRS_EPOCH'].unit
        if epoch_fmt == uu.yr:
            epoch_fmt = 'decimalyear'
        epoch = Time(props['DRS_EPOCH'], format=epoch_fmt)
    # get args
    # TODO: Add back in leap seconds (when barycorrpy works)
    bkwargs = dict(ra=props['DRS_RA'], dec=props['DRS_DEC'],
                   epoch=epoch.jd, px=props['DRS_PLX'],
                   pmra=props['DRS_PMRA'], pmdec=props['DRS_PMDE'],
                   lat=props['DRS_LAT'], longi=props['DRS_LONG'],
                   alt=props['DRS_ALT'], rv=props['DRS_RV'] * 1000,
                   leap_update=False)
    # try to set iers file
    try:
        from astropy.utils import iers
        # iers.IERS_A_URL = iers_a_url
        iers_a_file = os.path.join(bc_dir, iersfile)
        iers.IERS.iers_table = iers.IERS_A.open(iers_a_file)
    except Exception as e:
        WLOG(params, 'warning', 'IERS_A_FILE Warning:' + str(e))
    # try to import barycorrpy
    try:
        with warnings.catch_warnings(record=True) as _:
            import barycorrpy
    except Exception as _:
        wargs = [estimate, func_name]
        WLOG(params, 'warning', textentry('10-016-00003', args=wargs))
        raise BaryCorrpyException(textentry('10-016-00003', args=wargs))
    # must lock here (barcorrpy is not parallisable yet)
    lpath = params['DRS_DATA_REDUC']
    lfilename = os.path.join(lpath, 'barycorrpy')
    # ----------------------------------------------------------------------
    # define a synchoronized lock for indexing (so multiple instances do not
    #  run at the same time)
    lockfile = os.path.basename('{0}_{1}'.format(lfilename, iteration))
    # start a lock
    lock = drs_lock.Lock(params, lockfile)

    # make locked bervcalc function
    @drs_lock.synchronized(lock, params['PID'])
    def locked_bervcalc() -> Tuple[np.ndarray, np.ndarray]:
        # try to calculate bervs and bjds
        try:
            out1 = barycorrpy.get_BC_vel(JDUTC=times, zmeas=0.0, **bkwargs)
            out2 = barycorrpy.utc_tdb.JDUTC_to_BJDTDB(times, **bkwargs)
        except Exception as e:
            # log error
            wargs = [type(e), str(e), estimate, func_name]
            WLOG(params, 'warning', textentry('10-016-00004', args=wargs))
            raise BaryCorrpyException(textentry('10-016-00004', args=wargs))
        # return the bervs and bjds
        bervs = out1[0] / 1000.0
        bjds = out2[0]
        return bervs, bjds
    # -------------------------------------------------------------------------
    # try to run locked makedirs
    try:
        return locked_bervcalc()
    except KeyboardInterrupt as e:
        lock.reset()
        raise e
    except Exception as e:
        # reset lock
        lock.reset()
        raise e


def use_pyasl(params: ParamDict, times: Union[np.ndarray, list],
              props: ParamDict, quiet: bool = False,
              berv_est: Union[float, None] = None
              ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Use the pyasl module to calculate BERV/BJD

    :param params: ParamDict - parameter dictionary of constants
    :param times: numpy array, the list of times [in julien date]
    :param props: ParamDict - the berv input parameters (ra/dec/pmra/pmde etc)
    :param berv_est: float, an estimate of the pyasl BERV uncertainties
                     (for logging)

    :return: two numpy arrays, the array of bervs for the times [km/s], and
             array of bjds [julien date]
    """
    # set the function name
    func_name = __NAME__ + '.use_pyasl()'
    # get estimate accuracy
    estimate = pcheck(params, 'EXT_BERV_EST_ACC', func=func_name,
                      override=berv_est)
    # print warning that we are using estimate
    if not quiet:
        WLOG(params, 'warning', textentry('10-016-00005', args=[estimate]))
    # get args
    bkwargs = dict(ra2000=props['DRS_RA'], dec2000=props['DRS_DEC'],
                   obs_long=props['DRS_LONG'], obs_lat=props['DRS_LAT'],
                   obs_alt=props['DRS_ALT'])
    # set up storage
    bervs, bjds = [], []

    # loop around each time
    for jdtime in times:
        try:
            # calculate estimate of berv
            berv, bjd = bervest.helcorr(jd=jdtime, **bkwargs)
            # append to lists
            bervs.append(berv)
            bjds.append(bjd)
        except Exception as e:
            wargs = [jdtime, type(e), e, func_name]
            WLOG(params, 'error', textentry('00-016-00017', args=wargs))
    # convert lists to numpy arrays and return
    return np.array(bervs), np.array(bjds)


def add_berv_keys(params: ParamDict, infile: DrsFitsFile,
                  props: ParamDict) -> DrsFitsFile:
    # make sure infile has params
    infile.params = params
    # add berv keys
    infile.add_hkey('KW_BERVLONG', value=props['DRS_LONG'])
    infile.add_hkey('KW_BERVLAT', value=props['DRS_LAT'])
    infile.add_hkey('KW_BERVALT', value=props['DRS_ALT'])
    infile.add_hkey('KW_BERV', value=props['BERV'])
    infile.add_hkey('KW_BJD', value=props['BJD'])
    infile.add_hkey('KW_BERVMAX', value=props['BERV_MAX'])
    infile.add_hkey('KW_DBERV', value=props['DBERV'])
    infile.add_hkey('KW_BERVSOURCE', value=props['BERVSOURCE'])
    infile.add_hkey('KW_BERV_EST', value=props['BERV_EST'])
    infile.add_hkey('KW_BJD_EST', value=props['BJD_EST'])
    infile.add_hkey('KW_BERVMAX_EST', value=props['BERV_MAX_EST'])
    infile.add_hkey('KW_DBERV_EST', value=props['DBERV_EST'])
    infile.add_hkey('KW_BERV_OBSTIME', value=props['OBSTIME'])
    infile.add_hkey('KW_BERV_OBSTIME_METHOD', value=props['OBSTIMEMETHOD'])
    # return infile
    return infile


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

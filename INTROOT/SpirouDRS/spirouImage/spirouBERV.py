#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-15 04:58
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
import os
import dbm
import time
from astropy.time import Time, TimeDelta
from astropy import units as uu

from SpirouDRS import spirouCore
from SpirouDRS import spirouConfig
from . import spirouImage
from . import spirouBERVest
from . import spirouFITS

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouBERV.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog


# =============================================================================
# Define functions
# =============================================================================
# =============================================================================
# Addition non-extraction function
# =============================================================================
def get_earth_velocity_correction(p, loc, hdr):
    func_name = __NAME__ + '.get_earth_velocity_correction()'
    if p['KW_BERV'][0] in hdr:
        loc['BERV'] = float(hdr[p['KW_BERV'][0]])
        loc['BJD'] = float(hdr[p['KW_BJD'][0]])
        loc['BERV_MAX'] = float(hdr[p['KW_BERV_MAX'][0]])
        return p, loc

    # Get the OBSTYPE for file (from hdr)
    p = spirouImage.get_param(p, hdr, 'KW_OBSTYPE', dtype=str)
    # -----------------------------------------------------------------------
    #  Earth Velocity calculation only if OBSTYPE = OBJECT (NOT A CALIBRATION)
    # -----------------------------------------------------------------------
    if p['OBSTYPE'] == 'OBJECT':
        # ----------------------------------------------------------------------
        # Read star parameters
        # ----------------------------------------------------------------------
        p = spirouImage.get_param(p, hdr, 'KW_OBJRA', dtype=str)
        p = spirouImage.get_param(p, hdr, 'KW_OBJDEC', dtype=str)
        p = spirouImage.get_param(p, hdr, 'KW_OBJEQUIN')
        p = spirouImage.get_param(p, hdr, 'KW_OBJRAPM')
        p = spirouImage.get_param(p, hdr, 'KW_OBJDECPM')
        p = spirouImage.get_param(p, hdr, 'KW_DATE_OBS', dtype=str)
        p = spirouImage.get_param(p, hdr, 'KW_UTC_OBS', dtype=str)
        # ----------------------------------------------------------------------
        loc = earth_velocity_correction(p, loc, method=p['BERVMODE'])
    else:
        loc = earth_velocity_correction(p, loc, method='off')

    # return loc
    return p, loc


def earth_velocity_correction(p, loc, method):
    func_name = __NAME__ + '.earth_velocity_correction()'

    if method == 'off':
        # not an estimate
        loc['BERV'], loc['BJD'], loc['BERV_MAX'] = np.nan, np.nan, np.nan
        loc.set_sources(['BERV', 'BJD', 'BERV_MAX'], func_name)
        # store the obs_hour
        loc['BERVHOUR'], loc['BERVHOUR_EST'] = np.nan, np.nan
        loc.set_sources(['BERVHOUR', 'BERVHOUR_EST'], func_name)
        # set estimate measurements to nan
        loc['BERV_EST'], loc['BJD_EST'] = np.nan, np.nan
        loc['BERV_MAX_EST'] = np.nan
        loc.set_sources(['BERV_EST', 'BJD_EST', 'BERV_MAX_EST'], func_name)
        return loc

    # get the observation date
    obs_year = int(p['DATE-OBS'][0:4])
    obs_month = int(p['DATE-OBS'][5:7])
    obs_day = int(p['DATE-OBS'][8:10])
    # get the UTC observation time
    utc = p['UTC-OBS'].split(':')
    # convert to hours
    hourpart = float(utc[0])
    minpart = float(utc[1]) / 60.
    secondpart = float(utc[2]) / 3600.
    exptimehours = (p['EXPTIME'] / 3600.) / 2.
    obs_hour = hourpart + minpart + secondpart + exptimehours

    # get the RA in hours
    objra = p['OBJRA'].split(':')
    ra_hour = float(objra[0])
    ra_min = float(objra[1]) / 60.
    ra_second = float(objra[2]) / 3600.
    target_alpha = (ra_hour + ra_min + ra_second) * 15
    # get the DEC in degrees
    objdec = p['OBJDEC'].split(':')
    dec_hour = float(objdec[0])
    dec_min = np.sign(float(objdec[0])) * float(objdec[1]) / 60.
    dec_second = np.sign(float(objdec[0])) * float(objdec[2]) / 3600.
    target_delta = dec_hour + dec_min + dec_second
    # set the proper motion and equinox
    target_pmra = p['OBJRAPM']
    target_pmde = p['OBJDECPM']
    target_equinox = p['OBJEQUIN']

    # --------------------------------------------------------------------------
    #  Earth Velocity calculation
    # --------------------------------------------------------------------------

    WLOG(p, '', 'Computing Earth RV correction')
    args = [p, target_alpha, target_delta, target_equinox, obs_year,
            obs_month, obs_day, obs_hour, p['IC_LONGIT_OBS'],
            p['IC_LATIT_OBS'], p['IC_ALTIT_OBS'], target_pmra, target_pmde]
    # calculate BERV
    if p['DRS_MODE'].upper() == 'QUICK':
        WLOG(p, 'warning', 'DRS in QUICK MODE - BERV is only an estimate')
        berv, bjd, bervmax = newbervmain(*args, method='estimate')
        estimate = True
    else:
        try:
            berv, bjd, bervmax = newbervmain(*args, method=method)
            estimate = False
        except Exception as e:
            emsg1 = 'BERV Calculation failed, falling back to estimate'
            emsg2 = '\tError {0}: {1}'.format(type(e), e)
            WLOG(p, 'warning', [emsg1, emsg2])
            berv, bjd, bervmax = newbervmain(*args, method='estimate')
            estimate = True

    # finally save berv, bjd, bervmax to p
    if estimate:
        # log output
        wmsg = 'ESTIMATED Barycentric Earth RV correction: {0:.3f} km/s'
        WLOG(p, 'info', wmsg.format(berv))
        # estimate
        loc['BERV'], loc['BJD'], loc['BERV_MAX'] = np.nan, np.nan, np.nan
        loc.set_sources(['BERV', 'BJD', 'BERV_MAX'], func_name)
        # store the obs_hour
        loc['BERVHOUR'], loc['BERVHOUR_EST'] = np.nan, obs_hour
        loc.set_sources(['BERVHOUR', 'BERVHOUR_EST'], func_name)
        # set estimate measurements to nan
        loc['BERV_EST'], loc['BJD_EST'] = berv, bjd
        loc['BERV_MAX_EST'] = bervmax
        loc.set_sources(['BERV_EST', 'BJD_EST', 'BERV_MAX_EST'], func_name)
    else:
        # log output
        wmsg = 'Barycentric Earth RV correction: {0:.3f} km/s'
        WLOG(p, 'info', wmsg.format(berv))
        # not an estimate
        loc['BERV'], loc['BJD'], loc['BERV_MAX'] = berv, bjd, bervmax
        loc.set_sources(['BERV', 'BJD', 'BERV_MAX'], func_name)
        # store the obs_hour
        loc['BERVHOUR'], loc['BERVHOUR_EST'] = obs_hour, np.nan
        loc.set_sources(['BERVHOUR', 'BERVHOUR_EST'], func_name)
        # set estimate measurements to nan
        loc['BERV_EST'], loc['BJD_EST'] = np.nan, np.nan
        loc['BERV_MAX_EST'] = np.nan
        loc.set_sources(['BERV_EST', 'BJD_EST', 'BERV_MAX_EST'], func_name)


    # return p
    return loc


def newbervmain(p, ra, dec, equinox, year, month, day, hour, obs_long,
                obs_lat, obs_alt, pmra, pmde, method='new'):
    # if method is off return zeros
    if method == 'off':
        WLOG(p, 'warning', 'BERV not calculated.')
        return np.nan, np.nan, np.nan

    # estimate method using helcorr from pyastronomy
    if method == 'estimate':

        tstr = '{0} {1}'.format(p['DATE-OBS'], p['UTC-OBS'])
        t = Time(tstr, scale='utc')
        # add exposure time
        tdelta = TimeDelta(((p['EXPTIME'] / 3600.) / 2.) * uu.s)
        t1 = t + tdelta
        # storage for bervs
        bervs, bjds = [], []
        # loop around every 1.5 days in a year
        for dayit in np.arange(0., 365., 1.5):
            # get julien date for this day iteration
            jdi = t1.jd + dayit
            # calculate estimate of berv
            bargs = [obs_long, obs_lat, obs_alt, ra, dec, jdi]
            berv, bjd = spirouBERVest.helcorr(*bargs)
            # append to lists
            bervs.append(berv)
            bjds.append(bjd)
        # convert lists to numpy arrays
        bervs = np.array(bervs)
        bjds = np.array(bjds)
        # get berv
        berv2 = bervs[0]
        # bjd2 = bresults2[0].jd
        bjd2 = bjds[0]
        # work ou the maximum barycentric correction
        bervmax2 = np.max(abs(bervs))
        # return results
        return berv2, bjd2, bervmax2

    # calculation method using barycorrpy
    if method == 'new':
        # calculate JD time (as Astropy.Time object)
        tstr = '{0} {1}'.format(p['DATE-OBS'], p['UTC-OBS'])
        t = Time(tstr, scale='utc')
        # add exposure time
        tdelta = TimeDelta(((p['EXPTIME'] / 3600.) / 2.) * uu.s)
        t1 = t + tdelta
        # ---------------------------------------------------------------------
        # get reset directory location
        # get package name and relative path
        package = spirouConfig.Constants.PACKAGE()
        relfolder = spirouConfig.Constants.BARYCORRPY_DIR()
        # get absolute folder path from package and relfolder
        absfolder = spirouConfig.GetAbsFolderPath(package, relfolder)
        # get barycorrpy folder
        data_folder = os.path.join(absfolder, '')
        # ---------------------------------------------------------------------
        # need to import barycorrpy which required online files (astropy iers)
        #  therefore provide a way to set offline version first
        # noinspection PyBroadException
        try:
            # file at: http://maia.usno.navy.mil/ser7/finals2000A.all
            from astropy.utils import iers
            # get package name and relative path
            package = spirouConfig.Constants.PACKAGE()
            iers_dir = spirouConfig.Constants.ASTROPY_IERS_DIR()
            # get absolute folder path from package and relfolder
            absfolder = spirouConfig.GetAbsFolderPath(package, iers_dir)
            # get file name
            file_a = os.path.basename(iers.iers.IERS_A_FILE)
            path_a = os.path.join(absfolder, file_a)
            # set table
            iers.IERS.iers_table = iers.IERS_A.open(path_a)
            import barycorrpy
        except Exception as _:
            emsg1 = 'For method="new" must have barcorrpy installed '
            emsg2 = '\ti.e. ">>> pip install barycorrpy'
            WLOG(p, 'warning', [emsg1, emsg2])
            raise ImportError(emsg1 + '\n' + emsg2)
        # set up the barycorr arguments
        bkwargs = dict(ra=ra, dec=dec, epoch=equinox, pmra=pmra,
                       pmdec=pmde, px=0.0, rv=0.0, lat=obs_lat,
                       longi=obs_long * -1, alt=obs_alt * 1000.,
                       leap_dir=data_folder)
        # get the julien UTC date for observation and obs + 1 year
        jdutc = list(t1.jd + np.arange(0., 365., 1.5))
        # construct lock filename
        lfilename = os.path.join(p['DRS_DATA_REDUC'], 'BERV_lockfile')
        # add a wait for parallelisation
        lock, lfile = spirouFITS.check_fits_lock_file(p, lfilename)
        # calculate barycorrpy
        try:
            bresults1 = barycorrpy.get_BC_vel(JDUTC=jdutc, zmeas=0.0, **bkwargs)
        except Exception as e:
            # close lock
            spirouFITS.close_fits_lock_file(p, lock, lfile, lfilename)
            # re-raise exception to catch later
            raise e
        # end wait for parallelisation
        spirouFITS.close_fits_lock_file(p, lock, lfile, lfilename)
        # convert JDUTC to BJDTDB
        bresults2 = barycorrpy.utc_tdb.JDUTC_to_BJDTDB(t1, **bkwargs)
        # get berv
        berv2 = bresults1[0][0] / 1000.0
        # get bjd
        bjd2 = bresults2[0][0]
        # work ou the maximum barycentric correction
        bervmax2 = np.max(abs(bresults1[0] / 1000.))
        # return results
        return berv2, bjd2, bervmax2


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================

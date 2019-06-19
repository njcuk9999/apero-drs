#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-05 at 09:05

@author: cook
"""
from __future__ import division
import numpy as np
from astropy.time import Time, TimeDelta
from astropy import units as uu
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup

from SpirouDRS.spirouImage import spirouBERV
from SpirouDRS.spirouImage import spirouImage
from SpirouDRS.spirouImage import spirouFITS

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_extract_RAW_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# debug (skip ic_ff_extract_type = ic_extract_type)
DEBUG = False
# define ll extract types
EXTRACT_LL_TYPES = ['3c', '3d', '4a', '4b', '5a', '5b']
EXTRACT_SHAPE_TYPES = ['4a', '4b', '5a', '5b']


def etiennes_code(ra, dec, epoch, lat, longi, alt, pmra, pmdec, px, rv, mjdate):

    from barycorrpy import get_BC_vel
    from barycorrpy import utc_tdb

    obsname = ''
    zmeas = 0.0
    ephemeris = 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de405.bsp'

    JDUTC = Time(mjdate, format='mjd', scale='utc')

    bjd = utc_tdb.JDUTC_to_BJDTDB(JDUTC, ra=ra, dec=dec, obsname=obsname,
                                  lat=lat, longi=longi, alt=alt, pmra=pmra,
                                  pmdec=pmdec, px=px, rv=rv, epoch=epoch,
                                  ephemeris=ephemeris, leap_update=True)

    results = get_BC_vel(JDUTC=JDUTC, ra=ra, dec=dec, obsname=obsname, lat=lat,
                         longi=longi, alt=alt, pmra=pmra, pmdec=pmdec, px=px,
                         rv=rv, zmeas=zmeas, epoch=epoch, ephemeris=ephemeris,
                         leap_update=True)

    return results[0][0]/1000, bjd[0][0], np.nan

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":

    path = '/Data/projects/spirou/data_dev/reduced'

    night_name = 'TEST1/20180805'
    files = ['2295545o_pp.fits']

    night_name = '2019-01-17'
    files = ['2368959o_pp.fits']

    night_name = 'TEST2/20180805'
    files = ['2295547o_pp_e2dsff_AB.fits']

    filename = os.path.join(path, night_name, files[0])
    filename = os.path.join(path, 'TEST4/20180527/2279540o_pp_e2dsff_AB.fits')

    filename = '/Data/projects/spirou/data_dev/reduced/from_ea/2294341o_pp_e2dsff_AB_tellu_corrected.fits'

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, None,
                                    require_night_name=False)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, _, _ = spirouFITS.read_raw_data(p, filename)
    # ----------------------------------------------------------------------
    # Read star parameters
    # ----------------------------------------------------------------------
    p = spirouImage.get_sigdet(p, hdr, name='sigdet')
    p = spirouImage.get_exptime(p, hdr, name='exptime')
    p = spirouImage.get_gain(p, hdr, name='gain')
    p = spirouImage.get_param(p, hdr, 'KW_OBSTYPE', dtype=str)
    p = spirouImage.get_param(p, hdr, 'KW_OBJRA', dtype=str)
    p = spirouImage.get_param(p, hdr, 'KW_OBJDEC', dtype=str)
    p = spirouImage.get_param(p, hdr, 'KW_OBJEQUIN')
    p = spirouImage.get_param(p, hdr, 'KW_OBJRAPM')
    p = spirouImage.get_param(p, hdr, 'KW_OBJDECPM')
    p = spirouImage.get_param(p, hdr, 'KW_DATE_OBS', dtype=str)
    p = spirouImage.get_param(p, hdr, 'KW_UTC_OBS', dtype=str)
    p = spirouImage.get_param(p, hdr, 'KW_ACQTIME', dtype=float)

    # ----------------------------------------------------------------------
    # Get berv parameters
    # ----------------------------------------------------------------------
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
    # target_equinox = 2451545.0

    # calculate JD time (as Astropy.Time object)
    tstr = '{0} {1}'.format(p['DATE-OBS'], p['UTC-OBS'])
    t = Time(tstr, scale='utc')
    tdelta = TimeDelta(((p['EXPTIME'] / 3600.) / 2.) * uu.s)
    t1 = t + tdelta

    # ----------------------------------------------------------------------
    # BERV TEST
    # ----------------------------------------------------------------------

    args = [p, target_alpha, target_delta, target_equinox, obs_year,
            obs_month, obs_day, obs_hour, p['IC_LONGIT_OBS'] * -1,
            p['IC_LATIT_OBS'], p['IC_ALTIT_OBS'] * 1000, target_pmra,
            target_pmde]
    # get berv measurements
    results1 = spirouBERV.newbervmain(*args, method='estimate')


    args = [p, target_alpha, target_delta, target_equinox, obs_year,
            obs_month, obs_day, obs_hour, p['IC_LONGIT_OBS'],
            p['IC_LATIT_OBS'], p['IC_ALTIT_OBS'], target_pmra,
            target_pmde]

    results2 = spirouBERV.newbervmain(*args, method='new')

    results3 = etiennes_code(target_alpha, target_delta, target_equinox,
                             p['IC_LATIT_OBS'], p['IC_LONGIT_OBS'] * -1,
                             p['IC_ALTIT_OBS'] * 1000,
                             target_pmra, target_pmde, 0.0, 0.0, t1.mjd)

    print('OBJECT = {0}'.format(hdr['OBJECT']))
    print('{0:25s}'.format('ESTIMATE (PYASL)'), results1)
    print('{0:25s}'.format('SPIROU DRS (BARYCORRPY)'), results2)
    print('{0:25s}'.format('ETIENNE (BARYCORRPY)'), results3)

    print('{0:25s}'.format('HEADER'), (hdr['BERV'], hdr['BJD'], hdr['BERVMAX']))


# =============================================================================
# End of code
# =============================================================================

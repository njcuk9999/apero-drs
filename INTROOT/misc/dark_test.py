#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-02 at 18:32

@author: cook
"""
from __future__ import division
import numpy as np

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DARK_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt

NIGHT_NAME = 'engineering/Tests/Darks/2018-10-01_17-30-47'
FILES = ['dark_dark_NormalUSB_001d_pp.fits',
         'dark_dark_NormalUSB_002d_pp.fits',
         'dark_dark_NormalUSB_003d_pp.fits',
         'dark_dark_NormalUSB_004d_pp.fits',
         'dark_dark_NormalUSB_005d_pp.fits']


def dark_setup(night_name, files):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, data, hdr, cdr = spirouImage.ReadImageAndCombine(p, framemath='average')

    # ----------------------------------------------------------------------
    # fix for un-preprocessed files
    # ----------------------------------------------------------------------
    data = spirouImage.FixNonPreProcess(p, data)

    # ----------------------------------------------------------------------
    # Get basic image properties
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')

    # ----------------------------------------------------------------------
    # Dark exposure time check
    # ----------------------------------------------------------------------
    # log the Dark exposure time
    WLOG(p, 'info', 'Dark Time = {0:.3f} s'.format(p['EXPTIME']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if p['EXPTIME'] < p['QC_DARK_TIME']:
        emsg = 'Dark exposure time too short (< {0:.1f} s)'
        WLOG(p, 'error', emsg.format(p['QC_DARK_TIME']))

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # # rotate the image and conver from ADU/s to e-
    # data = data[::-1, ::-1] * p['exptime'] * p['gain']
    # convert NaN to zeros
    nanmask = ~np.isfinite(data)
    data = np.where(nanmask, np.zeros_like(data), data)
    # resize blue image
    bkwargs = dict(xlow=p['IC_CCDX_BLUE_LOW'], xhigh=p['IC_CCDX_BLUE_HIGH'],
                   ylow=p['IC_CCDY_BLUE_LOW'], yhigh=p['IC_CCDY_BLUE_HIGH'])
    datablue, nx2, ny2 = spirouImage.ResizeImage(p, data, **bkwargs)
    # Make sure we have data in the blue image
    if nx2 == 0 or ny2 == 0:
        WLOG(p, 'error', ('IC_CCD(X/Y)_BLUE_(LOW/HIGH) remove '
                                     'all pixels from image.'))
    # resize red image
    rkwargs = dict(xlow=p['IC_CCDX_RED_LOW'], xhigh=p['IC_CCDX_RED_HIGH'],
                   ylow=p['IC_CCDY_RED_LOW'], yhigh=p['IC_CCDY_RED_HIGH'])
    datared, nx3, ny3 = spirouImage.ResizeImage(p, data, **rkwargs)
    # Make sure we have data in the red image
    if nx3 == 0 or ny3 == 0:
        WLOG(p, 'error', ('IC_CCD(X/Y)_RED_(LOW/HIGH) remove '
                                     'all pixels from image.'))

    # ----------------------------------------------------------------------
    # Dark Measurement
    # ----------------------------------------------------------------------
    # Log that we are doing dark measurement
    WLOG(p, '', 'Doing Dark measurement')
    # measure dark for whole frame
    p = spirouImage.MeasureDark(p, data, 'Whole det', 'full')
    # measure dark for blue part
    p = spirouImage.MeasureDark(p, datablue, 'Blue part', 'blue')
    # measure dark for rede part
    p = spirouImage.MeasureDark(p, datared, 'Red part', 'red')

    # get stats
    stats1 = [data.size, np.nansum(~np.isfinite(data)),
              np.nanmedian(data),
              np.nansum(~np.isfinite(data)) * 100 / np.product(data.shape),
              p['DADEAD_FULL'],
              datablue.size, np.nansum(~np.isfinite(datablue)),
              np.nanmedian(datablue),
              np.nansum(~np.isfinite(datablue)) * 100 / np.product(datablue.shape),
              p['DADEAD_BLUE'], datared.size, np.nansum(~np.isfinite(datared)),
              np.nanmedian(datared),
              np.nansum(~np.isfinite(datared)) * 100 / np.product(datared.shape),
              p['DADEAD_RED']]

    return stats1


# generate stats
stats = dict()
for FILE in FILES:
    stats[FILE] = dark_setup(NIGHT_NAME, FILE)

# print stats
print('\n\n\n\n')
for FILE in FILES:
    print('\n\n' + '=' * 25 + '\n' + FILE + '\n' + '=' * 25 + '\n')

    print('FULL')
    print('\tSIZE = {0}'.format(stats[FILE][0]))
    print('\tnumber of NaNs = {0}'.format(stats[FILE][1]))
    print('\tMedian pixel value = {0}'.format(stats[FILE][2]))
    print('\tpercentage (manual) = {0}'.format(stats[FILE][3]))
    print('\tpercentage (DRS) = {0}'.format(stats[FILE][4]))

    print('BLUE')
    print('\tSIZE = {0}'.format(stats[FILE][5]))
    print('\tnumber of NaNs = {0}'.format(stats[FILE][6]))
    print('\tMedian pixel value = {0}'.format(stats[FILE][7]))
    print('\tpercentage (manual) = {0}'.format(stats[FILE][8]))
    print('\tpercentage (DRS) = {0}'.format(stats[FILE][9]))

    print('RED')
    print('\tSIZE = {0}'.format(stats[FILE][10]))
    print('\tnumber of NaNs = {0}'.format(stats[FILE][11]))
    print('\tMedian pixel value = {0}'.format(stats[FILE][12]))
    print('\tpercentage (manual) = {0}'.format(stats[FILE][13]))
    print('\tpercentage (DRS) = {0}'.format(stats[FILE][14]))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-03 at 13:21

@author: cook
"""

from __future__ import division
import numpy as np
import os
from astropy.io import fits
import matplotlib.pyplot as plt

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'visu_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt

night_name = '18BQ08-Sep21'
reffile = '2305120o_pp_e2dsff_AB_tellu_corrected.fits'

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    customargs = spirouStartup.GetCustomFromRuntime(p, [0], [str], ['reffile'],
                                                    [True], [reffile])
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='reffile',
                                    mainfitsdir='reduced')
    p['FIBER'] = 'AB'
    # load the calibDB
    p = spirouStartup.LoadCalibDB(p)

    # load ref spectrum
    e2ds, hdr, nx, ny = spirouImage.ReadImage(p)
    # get blaze
    blaze = spirouImage.ReadBlazeFile(p)
    # get wave image
    _, wave, _ = spirouImage.GetWaveSolution(p, hdr=hdr, return_wavemap=True)

    # get files
    files = os.listdir('.')
    fluxes = []
    times = []

    fig1, frame1 = plt.subplots(ncols=1, nrows=1)

    # loop around files and sum flux
    for filename in files:

        if 'corrected.fits' not in filename:
            continue

        print('Processing file {0}'.format(filename))

        # noinspection PyBroadException
        try:
            data = fits.getdata(filename, ext=0)
            header = fits.getheader(filename, ext=0)
        except:
            continue

        # correct for blaze
        data = data/blaze

        # get flux
        flux = np.nansum(data[np.isfinite(data)])
        fluxes.append(flux)

        # get time
        time = header['MJDATE']
        times.append(time)

        # fluxes
        data = data/np.nanpercentile(data, 90)

        # plot fig1
        for order_num in range(data.shape[0]):
            frame1.plot(wave[order_num], data[order_num])

    fig2, frame2 = plt.subplots(ncols=1, nrows=1)
    frame2.scatter(times, fluxes)
    frame2.set(xlabel='MJDate', ylabel='Sum of flux')

    plt.show()
    plt.close()


# =============================================================================
# End of code
# =============================================================================

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
import itertools
from tqdm import tqdm
import matplotlib.pyplot as plt

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


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":

    night_name = 'TEST1/20180805'
    files = ['2295545o_pp.fits']
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, data, hdr = spirouFITS.readimage_and_combine(p, framemath='add')
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

    # ----------------------------------------------------------------------
    # BERV TEST
    # ----------------------------------------------------------------------
    # set up grid of ra and decs
    ra_grid = np.arange(0, 360.0, 10.0)
    dec_grid = np.arange(-90.0, 90.0, 10.0)

    grid = list(itertools.product(ra_grid, dec_grid))

    # storage
    bervs1, bjds1, bervs2, bjds2, ras, decs = [], [], [], [], [], []

    # loop around grid parameters
    for ra, dec in tqdm(grid):
        args = [p, ra, dec, target_equinox, obs_year,
                obs_month, obs_day, obs_hour, p['IC_LONGIT_OBS'],
                p['IC_LATIT_OBS'], p['IC_ALTIT_OBS'], target_pmra,
                target_pmde]
        # get berv measurements
        results1 = spirouBERV.newbervmain(*args, method='estimate')
        results2 = spirouBERV.newbervmain(*args, method='new')

        # append to storage
        bervs1.append(results1[0]), bervs2.append(results2[0])
        bjds1.append(results1[1]), bjds2.append(results2[1])
        ras.append(ra), decs.append(dec)

    diff = np.array(bervs1) - np.array(bervs2)


    X, Y = np.meshgrid(ra_grid, dec_grid)
    Z = diff.reshape(X.shape) * 1000

    plt.ioff()
    plt.figure()
    im = plt.contourf(X, Y, Z, 100)
    cb = plt.colorbar(im)
    cb.set_label('BERV difference [m/s]')
    plt.title('Comparison between Barycorrpy and BERV Estimate')
    # plt.scatter(X.flatten(), Y.flatten(), marker='x', color='k')

    plt.xlabel('Right Ascension')
    plt.ylabel('Declination')
    plt.xlim(0, 360)
    plt.ylim(-90, 90)
    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================

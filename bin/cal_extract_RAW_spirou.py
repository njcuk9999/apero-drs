#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_extract_RAW_spirou

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""

import numpy as np
import time

from SpirouDRS import spirouBACK
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup

neilstart = time.time()

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_extract_RAW_spirou.py'
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# -----------------------------------------------------------------------------
# Remove this for final (only for testing)
import sys
if len(sys.argv) == 1:
    sys.argv = ['test: ' + __NAME__, '20170710', 'hcone_dark02c61.fits',
                'hcone_dark03c61.fits', 'hcone_dark04c61.fits',
                'hcone_dark05c61.fits', 'hcone_dark06c61.fits']

# =============================================================================
# Define functions
# =============================================================================



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    p = spirouStartup.RunInitialStartup()
    # run specific start up
    p = spirouStartup.RunStartup(p, kind='Flat-field', calibdb=True)
    # log processing image type
    p['dprtype'] = spirouImage.GetTypeFromHeader(p, p['kw_DPRTYPE'])
    p.set_source('dprtype', __NAME__ + '/__main__')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['log_opt'], wmsg.format(p['dprtype'], p['program']))

    fib_typ = ['AB', 'A', 'B', 'C']
    p['fib_type'] = ['AB']

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImage(p, framemath='add')

    # ----------------------------------------------------------------------
    # Get basic image properties
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')
    # set sigdet and conad keywords (sigdet is changed later)
    p['kw_CCD_SIGDET'][1] = p['sigdet']
    p['kw_CCD_CONAD'][1] = p['gain']

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToADU(spirouImage.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], ('Image format changed to '
                            '{0}x{1}').format(*data2.shape[::-1]))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 == 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['log_opt'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get the miny, maxy and max_signal for the central column
    # ----------------------------------------------------------------------
    # get the central column
    y = data2[p['IC_CENT_COL'], :]
    # get the min max and max signal using box smoothed approach
    miny, maxy, max_signal, diff_maxmin = spirouBACK.MeasureMinMax(p, y)
    # Log max average flux/pixel
    wmsg = 'Maximum average flux/pixel in the spectrum: {0:.1f} [ADU]'
    WLOG('info', p['log_opt'], wmsg.format(max_signal/p['nbframes']))

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG('', p['log_opt'], 'Doing background measurement on raw frame')
        # get the bkgr measurement
        background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(p, data2)
    else:
        background = np.zeros_like(data2)

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # define loc storage parameter dictionary
    loc = ParamDict()
    # get tilts
    loc['tilt'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('tilt', __NAME__ + '/__main__ + /spirouImage.ReadTiltFile')

    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    loc['wave'] = spirouImage.ReadWaveFile(p, hdr)
    loc.set_source('wave', __NAME__ + '/__main__ + /spirouImage.ReadWaveFile')

    # ----------------------------------------------------------------------
    # Fiber loop
    # ----------------------------------------------------------------------
    # loop around fiber types
    for fiber in p['fib_type']:
        # ------------------------------------------------------------------
        # Get localisation coefficients
        # ------------------------------------------------------------------
        # get this fibers parameters
        p = spirouLOCOR.FiberParams(p, fiber, merge=True)
        # get localisation fit coefficients
        loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
        # ------------------------------------------------------------------
        # Read image order profile
        # ------------------------------------------------------------------
        order_profile, _, _, nx, ny = spirouImage.ReadOrderProfile(p, hdr)
        # ------------------------------------------------------------------
        # Average AB into one fiber for AB, A and B
        # ------------------------------------------------------------------
        # if we have an AB fiber merge fit coefficients by taking the average
        # of the coefficients
        # (i.e. average of the 1st and 2nd, average of 3rd and 4th, ...)
        if fiber in ['A', 'B', 'AB']:
            # merge
            loc['acc'] = spirouLOCOR.MergeCoefficients(loc, loc['acc'], step=2)
            loc['ass'] = spirouLOCOR.MergeCoefficients(loc, loc['ass'], step=2)
            # set the number of order to half of the original
            loc['number_orders'] = int(loc['number_orders'] / 2)
        # ------------------------------------------------------------------
        # Set up Extract storage
        # ------------------------------------------------------------------
        # Create array to store extraction (for each order and each pixel
        # along order)
        loc['e2ds'] = np.zeros((loc['number_orders'], data2.shape[1]))
        # Create array to store the signal to noise ratios for each order
        loc['SNR'] = np.zeros(loc['number_orders'])

        # Manually set the sigdet to be used in extraction weighting
        if p['IC_FF_SIGDET'] > 0:
            p['sigdet'] = float(p['IC_FF_SIGDET'])
        # ------------------------------------------------------------------
        # Extract orders
        # ------------------------------------------------------------------
        # loop around each order
        for order_num in range(loc['number_orders']):
            # extract this order

            # -------------------------------------------------------------
            # Extract
            # -------------------------------------------------------------
            eargs = [p, loc, data2, order_num]
            spe1, cpt = spirouEXTOR.ExtractOrder(*eargs)

            # -------------------------------------------------------------
            # Extract
            # -------------------------------------------------------------
            eargs = [p, loc, data2, order_num]
            spe2, cpt = spirouEXTOR.ExtractOrder0(*eargs)

            # -------------------------------------------------------------
            # Extract with Tilt
            # -------------------------------------------------------------
            eargs = [p, loc, data2, order_profile, order_num]
            spe3, cpt = spirouEXTOR.ExtractTiltOrder(*eargs)

            # -------------------------------------------------------------
            # Extract with Tilt + Weight
            # -------------------------------------------------------------
            eargs = [p, loc, data2, order_profile, order_num]
            spe4, cpt = spirouEXTOR.ExtractTiltWeightOrder(*eargs)

            # -------------------------------------------------------------
            # Extract with Weight
            # -------------------------------------------------------------
            eargs = [p, loc, data2, order_profile, order_num]
            e2ds, cpt = spirouEXTOR.ExtractWeightOrder(*eargs)

            # calculate the noise
            range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
            noise = p['sigdet'] * np.sqrt(range1 + range2)
            # get window size
            blaze_win1 = int(data2.shape[0]/2) - p['IC_EXTFBLAZ']
            blaze_win2 = int(data2.shape[0]/2) + p['IC_EXTFBLAZ']
            # get average flux per pixel
            flux = np.sum(e2ds[blaze_win1:blaze_win2])/ (2*p['IC_EXTFBLAZ'])
            # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
            snr = flux / np.sqrt(flux + noise**2)
            # log the SNR RMS
            wmsg = 'On fiber {0} order {1}: S/N= {2:.1f}  - FF rms={3:.2f} %'
            wargs = [fiber, order_num, snr, rms * 100.0]
            WLOG('', p['log_opt'], wmsg.format(*wargs))
            # add calculations to storage
            loc['e2ds'][order_num] = e2ds
            loc['SNR'][order_num] = snr
            # set sources
            source = __NAME__ + '/__main__()'
            loc.set_sources(['e2ds', 'SNR', 'RMS', 'blaze', 'flat'], source)
            # Log if saturation level reached
            satvalue = (flux/p['gain'])/(range1 + range2)
            if satvalue > (p['QC_LOC_FLUMAX'] * p['nbframes']):
                wmsg = 'SATURATION LEVEL REACHED on Fiber {0}'
                WLOG('warning', p['log_opt'], wmsg.format(fiber))

        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------

        # ------------------------------------------------------------------
        # Store extraction in file
        # ------------------------------------------------------------------




    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    # saturation check: check that the max_signal is lower than qc_max_signal
    if max_signal > (p['QC_MAX_SIGNAL'] * p['nbframes']):
        fmsg = 'Too much flux in the image (max authorized={0})'
        fail_msg.append(fmsg.format(p['QC_MAX_SIGNAL'] * p['nbframes']))
        passed = False
        # Question: Why is this test ignored?
        # For some reason this test is ignored in old code
        passed = True
        WLOG('info', p['log_opt'], fail_msg[-1])

    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['log_opt'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/__main__')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('info', p['log_opt'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/__main__')


    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                '').format(p['program']))

    neilend = time.time()
    print('Time taken (py3) = {0}'.format(neilend - neilstart))
# =============================================================================
# End of code
# =============================================================================

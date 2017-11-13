#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_SLIT_spirou

Flat Field

Created on 2017-11-06 11:32

@author: cook

Version 0.0.1
"""
import numpy as np
import time

from SpirouDRS import spirouBACK
from SpirouDRS import spirouCDB
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS.spirouCore import spirouPlot as sPlt

neilstart = time.time()

# =============================================================================
# Define variables
# =============================================================================
# Get Logging function
WLOG = spirouCore.wlog
# Name of program
__NAME__ = 'cal_SLIT_spirou.py'
# -----------------------------------------------------------------------------
# Remove this for final (only for testing)
import sys
if len(sys.argv) == 1:
    sys.argv = ['test.py', '20170710', 'flat_dark02f10.fits',
                'flat_dark03f10.fits', 'flat_dark04f10.fits',
                'flat_dark05f10.fits', 'flat_dark06f10.fits']

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
    p = spirouCore.RunInitialStartup()
    # run specific start up
    params2add = dict()
    params2add['dark_flat'] = spirouLOCOR.FiberParams(p, 'C')
    params2add['flat_dark'] = spirouLOCOR.FiberParams(p, 'AB')
    p = spirouCore.RunStartup(p, kind='Flat-field',
                              prefixes=['dark_flat', 'flat_dark'],
                              add_to_p=params2add, calibdb=True)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImage(p, framemath='add')
    # get ccd sig det value
    p['sigdet'] = float(spirouImage.GetKey(p, hdr, 'RDNOISE', hdr['@@@hname']))
    p.set_source('sigdet', __NAME__ + '/__main__')
    # get exposure time
    p['exptime'] = float(spirouImage.GetKey(p, hdr, 'EXPTIME', hdr['@@@hname']))
    p.set_source('exptime', __NAME__ + '/__main__')
    # get gain
    p['gain'] = float(spirouImage.GetKey(p, hdr, 'GAIN', hdr['@@@hname']))
    p.set_source('gain', __NAME__ + '/__main__')

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToE(spirouImage.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], ('Image format changed to '
                            '{0}x{1}').format(*data2.shape))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 <= 0)
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
    tilt = spirouImage.ReadTiltFile(p, hdr)




    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    # saturation check: check that the max_signal is lower than qc_max_signal
    if max_signal > (p['QC_MAX_SIGNAL'] * p['nbframes']):
        fmsg = 'Too much flux in the image (max authorized={0})'
        fail_msg.append(fmsg.format(p['QC_MAX_SIGNAL'] * p['nbframes']))
        passed = False

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

# =============================================================================
# End of code
# =============================================================================

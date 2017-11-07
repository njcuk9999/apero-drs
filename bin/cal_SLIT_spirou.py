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

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR

# =============================================================================
# Define variables
# =============================================================================
# Get Logging function
WLOG = spirouCore.wlog
# Name of program
__NAME__ = 'cal_SLIT_spirou.py'
# -----------------------------------------------------------------------------
# whether to use plt.ion or plt.show
INTERACTIVE_PLOTS = spirouConfig.spirouConfig.INTERACTIVE_PLOTS
# -----------------------------------------------------------------------------
# import sys
# sys.argv += ['20170710', 'fp_fp02a203.fits', 'fp_fp03a203.fits',
#              'fp_fp04a203.fits']

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
    p = spirouCore.RunStartup(p, kind='slit', prefixes='fp_fp',
                              calibdb=True)
    # set the fiber type
    p['fib_typ'] = ['AB']
    p.set_source('fib_typ', __NAME__ + '/__main__')
    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImage(p, framemath='add')
    # get ccd sig det value
    p['ccdsigdet'] = float(spirouImage.GetKey(p, hdr, 'RDNOISE',
                                              hdr['@@@hname']))
    p.set_source('ccdsigdet', __NAME__ + '/__main__')
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
    n_bad_pix_frac = n_bad_pix * 100/ np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['log_opt'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get coefficients
    # ----------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p['fiber'] = p['fib_typ'][0]
    p.set_source('fiber', __NAME__ + '/__main__')
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr)


    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                '').format(p['program']))

# =============================================================================
# End of code
# =============================================================================

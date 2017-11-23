#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_SLIT_spirou

Flat Field

Created on 2017-11-06 11:32

@author: cook

Version 0.0.1
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_SLIT_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    p = spirouStartup.RunInitialStartup(night_name, files)
    # run specific start up
    p = spirouStartup.RunStartup(p, kind='slit', prefixes='fp_fp',
                                 calibdb=True)
    # set the fiber type
    p['fib_typ'] = ['AB']
    p.set_source('fib_typ', __NAME__ + '/__main__')

    # log processing image type
    p['dprtype'] = spirouImage.GetTypeFromHeader(p, p['kw_DPRTYPE'])
    p.set_source('dprtype', __NAME__ + '/__main__')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['log_opt'], wmsg.format(p['dprtype'], p['program']))

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImageAndCombine(p, framemath='add')

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
    # Get localisation coefficients
    # ----------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p = spirouLOCOR.FiberParams(p, p['fib_typ'][0], merge=True)
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr)

    # ----------------------------------------------------------------------
    # Calculating the tilt
    # ----------------------------------------------------------------------
    # get the tilt by extracting the AB fibers and correlating them
    loc = spirouImage.GetTilt(p, loc, data2)
    # fit the tilt with a polynomial
    loc = spirouImage.FitTilt(p, loc)
    # log the tilt dispersion
    wmsg = 'Tilt dispersion = {0:.3f} deg'
    WLOG('info', p['log_opt'] + p['fiber'], wmsg.format(loc['rms_tilt']))

    # ----------------------------------------------------------------------
    # Plotting
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # plots setup: start interactive plot
        sPlt.start_interactive_session()
        # plot image with selected order shown
        sPlt.slit_sorder_plot(p, loc, data2)
        # plot slit tilt angle and fit
        sPlt.slit_tilt_angle_and_fit_plot(p, loc)
        # end interactive section
        sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Replace tilt by the global fit
    # ----------------------------------------------------------------------
    loc['tilt'] = loc['yfit_tilt']
    oldsource = loc.get_source('tilt')
    loc.set_source('tilt', oldsource + '+{0}/__main__'.format(__NAME__))

    # ----------------------------------------------------------------------
    # Save and record of tilt table
    # ----------------------------------------------------------------------
    # copy the tilt along the orders
    tiltima = np.ones((int(loc['number_orders']/2), data2.shape[1]))
    tiltima *= loc['tilt'][:, None]
    # construct file name and path
    tiltfits = p['arg_file_names'][0].replace('.fits', '_tilt.fits')
    reduced_dir = p['reduced_dir']
    # Log that we are saving tilt file
    wmsg = 'Saving tilt  information in file: {0}'
    WLOG('', p['log_opt'], wmsg.format(tiltfits))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # add version number
    hdict = spirouImage.AddKey(hdict, p['kw_Version'])
    # add the tilt parameters
    for order_num in range(0, int(loc['number_orders']/2)):
        # modify name and comment for keyword
        tilt_keywordstore = list(p['kw_TILT'])
        tilt_keywordstore[0] += str(order_num)
        tilt_keywordstore[2] += str(order_num)
        # add keyword to hdict
        hdict = spirouImage.AddKey(hdict, tilt_keywordstore,
                                   value=loc['tilt'][order_num])
    # write tilt file to file
    spirouImage.WriteImage(os.path.join(reduced_dir, tiltfits), tiltima, hdict)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # to be done
    p['QC'] = 1

    # ----------------------------------------------------------------------
    # Update the calibration data base
    # ----------------------------------------------------------------------
    if p['QC']:
        keydb = 'TILT'
        # copy localisation file to the calibDB folder
        spirouCDB.PutFile(p, os.path.join(reduced_dir, tiltfits))
        # update the master calib DB file with new key
        spirouCDB.UpdateMaster(p, keydb, tiltfits, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been succesfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    main()

# =============================================================================
# End of code
# =============================================================================

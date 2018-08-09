#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_SLIT_spirou.py [night_directory] [files]

Fabry-Perot exposures in which the three fibres are simultaneously fed by light
from the Fabry-Perot filter. Each exposure is used to build the slit
orientation. Finds the tilt of the orders.

Created on 2017-11-06 11:32

@author: cook

Last modified: 2017-12-11 at 15:09

Up-to-date with cal_SLIT_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouBACK
from SpirouDRS import spirouDB
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
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    """
    cal_SLIT_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_SLIT_spirou.py [night_directory] [files]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
    # set the fiber type
    p['FIB_TYP'] = ['AB']
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, data, hdr, cdr = spirouImage.ReadImageAndCombine(p, framemath='add')

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
    WLOG('', p['LOG_OPT'], ('Image format changed to '
                            '{0}x{1}').format(*data2.shape))

    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    # TODO: Remove H2RG compatibility
    if p['IC_IMAGE_TYPE'] == 'H4RG':
        data2 = spirouImage.CorrectForBadPix(p, data2, hdr)

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG('', p['LOG_OPT'], 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bdata = spirouBACK.MeasureBackgroundFF(p, data2)
        background, gridx, gridy, minlevel = bdata
    else:
        background = np.zeros_like(data2)

    # data2=data2-background
    # correct data2 with background (where positive)
    data2 = np.where(data2 > 0, data2 - background, 0)

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 <= 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    loc = ParamDict()

    # ----------------------------------------------------------------------
    # Loop around fiber types
    # ----------------------------------------------------------------------

    for fiber in p['FIB_TYP']:
        # set fiber
        p['FIBER'] = fiber
        # ------------------------------------------------------------------
        # Get localisation coefficients
        # ------------------------------------------------------------------
        # original there is a loop but it is not used --> removed
        p = spirouImage.FiberParams(p, p['FIBER'], merge=True)
        # get localisation fit coefficients
        loc = spirouLOCOR.GetCoeffs(p, hdr, loc)

        # ------------------------------------------------------------------
        # Calculating the tilt
        # ------------------------------------------------------------------
        # get the tilt by extracting the AB fibers and correlating them
        loc = spirouImage.GetTilt(p, loc, data2)

    # Question: if we loop around fib_typ - loc is overwritten
    # Question:     (tilt overwritten in original)
    # Question:   I.E.  looping around fib_typ is USELESS
    # TODO: Remove fiber type for loop - or use it properly!!
    # fit the tilt with a polynomial
    loc = spirouImage.FitTilt(p, loc)
    # log the tilt dispersion
    wmsg = 'Tilt dispersion = {0:.3f} deg'
    WLOG('info', p['LOG_OPT'] + p['FIBER'], wmsg.format(loc['RMS_TILT']))

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # plots setup: start interactive plot
        sPlt.start_interactive_session()
        # plot image with selected order shown
        sPlt.slit_sorder_plot(p, loc, data2)
        # plot slit tilt angle and fit
        sPlt.slit_tilt_angle_and_fit_plot(p, loc)
        # end interactive section
        sPlt.end_interactive_session()

    # ------------------------------------------------------------------
    # Replace tilt by the global fit
    # ------------------------------------------------------------------
    loc['TILT'] = loc['YFIT_TILT']
    oldsource = loc.get_source('tilt')
    loc.set_source('TILT', oldsource + '+{0}/main()'.format(__NAME__))

    # ----------------------------------------------------------------------
    # Save and record of tilt table
    # ----------------------------------------------------------------------
    # copy the tilt along the orders
    tiltima = np.ones((int(loc['NUMBER_ORDERS']/2), data2.shape[1]))
    tiltima *= loc['TILT'][:, None]
    # construct file name and path
    tiltfits = spirouConfig.Constants.SLIT_TILT_FILE(p)
    tiltfitsname = os.path.split(tiltfits)[-1]
    # Log that we are saving tilt file
    wmsg = 'Saving tilt  information in file: {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(tiltfitsname))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # add version number
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    # add tilt parameters as 1d list
    hdict = spirouImage.AddKey1DList(hdict, p['KW_TILT'], values=loc['TILT'])
    # write tilt file to file
    spirouImage.WriteImage(tiltfits, tiltima, hdict)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # check that tilt rms is below required
    if loc['RMS_TILT'] > p['QC_SLIT_RMS']:
        # add failed message to fail message list
        fmsg = 'abnormal RMS of SLIT angle ({0:.2f} > {1:.2f} deg)'
        fail_msg.append(fmsg.format(loc['RMS_TILT'], p['QC_SLIT_RMS']))
        passed = False
    # check that tilt is less than max tilt required
    max_tilt = np.max(loc['TILT'])
    if max_tilt > p['QC_SLIT_MAX']:
        # add failed message to fail message list
        fmsg = 'abnormal SLIT angle ({0:.2f} > {1:.2f} deg)'
        fail_msg.append(fmsg.format(max_tilt, p['QC_SLIT_MAX']))
        passed = False
    # check that tilt is greater than min tilt required
    min_tilt = np.min(loc['TILT'])
    if min_tilt < p['QC_SLIT_MIN']:
        # add failed message to fail message list
        fmsg = 'abnormal SLIT angle ({0:.2f} < {1:.2f} deg)'
        fail_msg.append(fmsg.format(max_tilt, p['QC_SLIT_MIN']))
        passed = False
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['LOG_OPT'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Update the calibration data base
    # ----------------------------------------------------------------------
    if p['QC']:
        keydb = 'TILT'
        # copy localisation file to the calibDB folder
        spirouDB.PutCalibFile(p, tiltfits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, tiltfitsname, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================

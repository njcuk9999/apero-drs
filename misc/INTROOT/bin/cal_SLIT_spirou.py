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
__args__ = ['night_name', 'files']
__required__ = [True, True]
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
    p['FIB_TYP'] = 'AB'
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, data, hdr = spirouImage.ReadImageAndCombine(p, framemath='add')

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
    p, datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToE(spirouImage.FlipImage(p, datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(p, data0, **bkwargs)
    # log change in data size
    WLOG(p, '', ('Image format changed to '
                            '{0}x{1}').format(*data2.shape))

    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    p, data2 = spirouImage.CorrectForBadPix(p, data2, hdr)

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG(p, '', 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bargs = [p, data2, hdr]
        # background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(*bargs)
        p, background = spirouBACK.MeasureBackgroundMap(*bargs)
    else:
        background = np.zeros_like(data2)
        p['BKGRDFILE'] = 'None'
        p.set_source('BKGRDFILE', __NAME__ + '.main()')

    # correct data2 with background
    data2 = data2 - background

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.nansum(~np.isfinite(data2))
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG(p, 'info', wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    loc = ParamDict()

    # ----------------------------------------------------------------------
    # Loop around fiber types
    # ----------------------------------------------------------------------
    # set fiber
    p['FIBER'] = p['FIB_TYP']
    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p = spirouImage.FiberParams(p, p['FIBER'], merge=True)
    # get localisation fit coefficients
    p, loc = spirouLOCOR.GetCoeffs(p, hdr, loc)

    # ------------------------------------------------------------------
    # Calculating the tilt
    # ------------------------------------------------------------------
    # get the tilt by extracting the AB fibers and correlating them
    loc = spirouImage.GetTilt(p, loc, data2)

    # fit the tilt with a polynomial
    loc = spirouImage.FitTilt(p, loc)
    # log the tilt dispersion
    wmsg = 'Tilt dispersion = {0:.3f} deg'
    WLOG(p, 'info', wmsg.format(loc['RMS_TILT']))

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # plots setup: start interactive plot
        sPlt.start_interactive_session(p)
        # plot image with selected order shown
        sPlt.slit_sorder_plot(p, loc, data2)
        # plot slit tilt angle and fit
        sPlt.slit_tilt_angle_and_fit_plot(p, loc)
        # end interactive section
        sPlt.end_interactive_session(p)

    # ------------------------------------------------------------------
    # Replace tilt by the global fit
    # ------------------------------------------------------------------
    loc['TILT'] = loc['YFIT_TILT']
    oldsource = loc.get_source('tilt')
    loc.set_source('TILT', oldsource + '+{0}/main()'.format(__NAME__))

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # check that tilt rms is below required
    if loc['RMS_TILT'] > p['QC_SLIT_RMS']:
        # add failed message to fail message list
        fmsg = 'abnormal RMS of SLIT angle ({0:.2f} > {1:.2f} deg)'
        fail_msg.append(fmsg.format(loc['RMS_TILT'], p['QC_SLIT_RMS']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(loc['RMS_TILT'])
    qc_names.append('RMS_TILT')
    qc_logic.append('RMS_TILT > {0:.2f}'.format(p['QC_SLIT_RMS']))
    # ----------------------------------------------------------------------
    # check that tilt is less than max tilt required
    max_tilt = np.max(loc['TILT'])
    if max_tilt > p['QC_SLIT_MAX']:
        # add failed message to fail message list
        fmsg = 'abnormal SLIT angle ({0:.2f} > {1:.2f} deg)'
        fail_msg.append(fmsg.format(max_tilt, p['QC_SLIT_MAX']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(max_tilt)
    qc_names.append('max_tilt')
    qc_logic.append('max_tilt > {0:.2f}'.format(p['QC_SLIT_MAX']))
    # ----------------------------------------------------------------------
    # check that tilt is greater than min tilt required
    min_tilt = np.min(loc['TILT'])
    if min_tilt < p['QC_SLIT_MIN']:
        # add failed message to fail message list
        fmsg = 'abnormal SLIT angle ({0:.2f} < {1:.2f} deg)'
        fail_msg.append(fmsg.format(max_tilt, p['QC_SLIT_MIN']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(min_tilt)
    qc_names.append('min_tilt')
    qc_logic.append('min_tilt > {0:.2f}'.format(p['QC_SLIT_MIN']))
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG(p, 'info', 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG(p, 'warning', wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # ----------------------------------------------------------------------
    # Save and record of tilt table
    # ----------------------------------------------------------------------
    # copy the tilt along the orders
    tiltima = np.ones((int(loc['NUMBER_ORDERS']/2), data2.shape[1]))
    tiltima *= loc['TILT'][:, None]
    # get the raw tilt file name
    raw_tilt_file = os.path.basename(p['FITSFILENAME'])
    # construct file name and path
    tiltfits, tag = spirouConfig.Constants.SLIT_TILT_FILE(p)
    tiltfitsname = os.path.basename(tiltfits)
    # Log that we are saving tilt file
    wmsg = 'Saving tilt information in file: {0}'
    WLOG(p, '', wmsg.format(tiltfitsname))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'],
                               value=p['DARKFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'],
                               value=p['BADPFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBLOCO'], value=p['LOCOFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBACK'],
                               value=p['BKGRDFILE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['ARG_FILE_NAMES'])
    # add qc parameters
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # add tilt parameters as 1d list
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_TILT'], values=loc['TILT'])
    # write tilt file to file
    p = spirouImage.WriteImage(p, tiltfits, tiltima, hdict)

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

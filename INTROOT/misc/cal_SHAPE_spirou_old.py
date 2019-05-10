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
__NAME__ = 'cal_SHAPE_spirou.py'
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
    p['FIBER'] = 'AB'
    p.set_source('FIBER', __NAME__ + '/main()')

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
    datac = data

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
    p, badpixmap = spirouImage.CorrectForBadPix(p, data2, hdr, return_map=True)

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG(p, '', 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bargs = [p, data2, hdr, badpixmap]
        # background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(*bargs)
        background = spirouBACK.MeasureBackgroundMap(*bargs)
    else:
        background = np.zeros_like(data2)
    # apply background correction to data (and set to zero where negative)
    # TODO: Etienne --> Francois - Cannot set negative flux to zero!
    # data2 = np.where(data2 > 0, data2 - background, 0)
    data2 = data2 - background

    # save data to loc
    loc = ParamDict()
    loc['DATA'] = data2
    loc.set_source('DATA', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.nansum(data2 <= 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG(p, 'info', wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p = spirouImage.FiberParams(p, p['FIBER'], merge=True)
    # get localisation fit coefficients
    p, loc = spirouLOCOR.GetCoeffs(p, hdr, loc)

    # ------------------------------------------------------------------
    # Calculate shape map
    # ------------------------------------------------------------------
    loc = spirouImage.GetShapeMap(p, loc)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # plots setup: start interactive plot
        sPlt.start_interactive_session(p)
        # plot the shape process for each order
        sPlt.slit_shape_angle_plot(p, loc)
        # end interactive section
        sPlt.end_interactive_session(p)

    # ------------------------------------------------------------------
    # Writing to file
    # ------------------------------------------------------------------
    # get the raw tilt file name
    raw_shape_file = os.path.basename(p['FITSFILENAME'])
    # construct file name and path
    shapefits, tag = spirouConfig.Constants.SLIT_SHAPE_FILE(p)
    shapefitsname = os.path.basename(shapefits)
    # Log that we are saving tilt file
    wmsg = 'Saving shape information in file: {0}'
    WLOG(p, '', wmsg.format(shapefitsname))
    # Copy keys from fits file
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'], value=p['DARKFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'], value=p['BADPFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBLOCO'], value=p['LOCOFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBSHAPE'], value=raw_shape_file)
    # write tilt file to file
    p = spirouImage.WriteImage(p, shapefits, loc['DXMAP'], hdict)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # TODO: Decide on some quality control criteria?
    # set passed variable and fail message list
    passed, fail_msg = True, []
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

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        keydb = 'SHAPE'
        # copy shape file to the calibDB folder
        spirouDB.PutCalibFile(p, shapefits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, shapefitsname, hdr)

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

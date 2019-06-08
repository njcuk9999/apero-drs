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
import warnings

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS import spirouEXTOR


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_shape_spirou.py'
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
# force plot off
PLOT_PER_ORDER = False


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    """
    cal_shape_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_shape_spirou.py [night_directory] [fitsfilename]

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
    p = spirouStartup.InitialFileSetup(p)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, data, hdr = spirouImage.ReadImageAndCombine(p, framemath='add')

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Get basic image properties for FP file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')

    # ----------------------------------------------------------------------
    # Correction of reference FP
    # ----------------------------------------------------------------------
    # set the number of frames
    p['NBFRAMES'] = 1
    p.set_source('NBFRAMES', __NAME__ + '.main()')
    # Correction of DARK
    p, datac = spirouImage.CorrectForDark(p, data, hdr)
    # Resize hc data
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToE(spirouImage.FlipImage(p, datac), p=p)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data1 = spirouImage.ResizeImage(p, data, **bkwargs)
    # log change in data size
    WLOG(p, '',
         ('FPref Image format changed to {0}x{1}').format(*data1.shape))
    # Correct for the BADPIX mask (set all bad pixels to zero)
    bargs = [p, data1, hdr]
    p, data1 = spirouImage.CorrectForBadPix(*bargs)
    p, badpixmask = spirouImage.CorrectForBadPix(*bargs, return_map=True)
    # log progress
    WLOG(p, '', 'Cleaning FPref hot pixels')
    # correct hot pixels
    data1 = spirouEXTOR.CleanHotpix(data1, badpixmask)
    # Log the number of dead pixels
    # get the number of bad pixels
    with warnings.catch_warnings(record=True) as _:
        n_bad_pix = np.nansum(data1 <= 0)
        n_bad_pix_frac = n_bad_pix * 100 / np.product(data1.shape)
    # Log number
    wmsg = 'Nb FPref dead pixels = {0} / {1:.2f} %'
    WLOG(p, 'info', wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get master FP file
    # ----------------------------------------------------------------------
    # log progress
    WLOG(p, '', 'Getting FP Master from calibDB')
    # get master fp
    p, masterfp = spirouImage.GetFPMaster(p, hdr)

    # ----------------------------------------------------------------------
    # Get transform parameters
    # ----------------------------------------------------------------------
    # log progress
    wargs = [p['ARG_FILE_NAMES'][0], p['FPMASTERFILE']]
    WLOG(p, 'info', 'Calculating transforming for {0} onto {1}'.format(*wargs))

    gout = spirouImage.GetLinearTransformParams(p, masterfp, data1)
    transform, xres, yres = gout

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
    # if transform is None means the fp image quality was too poor
    if transform is None:
        fail_msg.append('FP Image quality too poor (sigma clip failed)')
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    qc_values.append('None')
    qc_names.append('Image Quality')
    qc_logic.append('Image too poor')
    # ----------------------------------------------------------------------
    # get residual qc parameter
    qc_res = p['SHAPE_QC_LINEAR_TRANS_RES_THRES']
    # assess quality of x residuals
    if xres > qc_res:
        fail_msg.append('x-resdiuals too high {0} > {1}'.format(xres, qc_res))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    qc_values.append(xres)
    qc_names.append('XRES')
    qc_logic.append('XRES > {0}'.format(qc_res))
    # assess quality of x residuals
    if yres > qc_res:
        fail_msg.append('y-resdiuals too high {0} > {1}'.format(yres, qc_res))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    qc_values.append(yres)
    qc_names.append('YRES')
    qc_logic.append('YRES > {0}'.format(qc_res))

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

    # ------------------------------------------------------------------
    # Writing shape to file
    # ------------------------------------------------------------------
    # get the raw tilt file name
    raw_shape_file = os.path.basename(p['FITSFILENAME'])
    # construct file name and path
    shapefits, tag = spirouConfig.Constants.SLIT_SHAPE_LOCAL_FILE(p)
    shapefitsname = os.path.basename(shapefits)
    # Log that we are saving tilt file
    wmsg = 'Saving shape information in file: {0}'
    WLOG(p, '', wmsg.format(shapefitsname))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'], value=p['DARKFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'], value=p['BADPFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBFPMASTER'],
                               value=p['FPMASTERFILE'])

    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['ARG_FILE_NAMES'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # add the transform parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_SHAPE_DX'], value=transform[0])
    hdict = spirouImage.AddKey(p, hdict, p['KW_SHAPE_DY'], value=transform[1])
    hdict = spirouImage.AddKey(p, hdict, p['KW_SHAPE_A'], value=transform[2])
    hdict = spirouImage.AddKey(p, hdict, p['KW_SHAPE_B'], value=transform[3])
    hdict = spirouImage.AddKey(p, hdict, p['KW_SHAPE_C'], value=transform[4])
    hdict = spirouImage.AddKey(p, hdict, p['KW_SHAPE_D'], value=transform[5])
    # write tilt file to file
    p = spirouImage.WriteImage(p, shapefits, [transform], hdict)

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        # add shape
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

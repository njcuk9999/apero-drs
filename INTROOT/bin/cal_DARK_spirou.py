#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_DARK_spirou.py [night_directory] [fitsfilename]

Dark with short exposure time (~5min, to be defined during AT-4) to check
if read-out noise, dark current and hot pixel mask are consistent with the
ones obtained during technical night. Quality control is done automatically
by the pipeline

Created on 2017-10-11 at 10:45

@author: cook

Last modified: 2017-12-11 at 15:08

Up-to-date with cal_DARK_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os
import warnings

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DARK_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    """
    cal_DARK_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_DARK_spirou.py [night_directory] [fitsfilename]

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
    p, data, hdr = spirouImage.ReadImageAndCombine(p, framemath='average')

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
    # Dark exposure time check
    # ----------------------------------------------------------------------
    # log the Dark exposure time
    WLOG(p, 'info', 'Dark Time = {0:.3f} s'.format(p['EXPTIME']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if p['EXPTIME'] < p['QC_DARK_TIME']:
        emsg = 'Dark exposure time too short (< {0:.1f} s)'
        WLOG(p, 'error', emsg.format(p['QC_DARK_TIME']))

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # # rotate the image and conver from ADU/s to e-
    # data = data[::-1, ::-1] * p['exptime'] * p['gain']
    # convert NaN to zeros
    nanmask = ~np.isfinite(data)
    data0 = np.where(nanmask, np.zeros_like(data), data)
    # resize blue image
    bkwargs = dict(xlow=p['IC_CCDX_BLUE_LOW'], xhigh=p['IC_CCDX_BLUE_HIGH'],
                   ylow=p['IC_CCDY_BLUE_LOW'], yhigh=p['IC_CCDY_BLUE_HIGH'])
    datablue, nx2, ny2 = spirouImage.ResizeImage(p, data, **bkwargs)
    # Make sure we have data in the blue image
    if nx2 == 0 or ny2 == 0:
        WLOG(p, 'error', ('IC_CCD(X/Y)_BLUE_(LOW/HIGH) remove '
                                     'all pixels from image.'))
    # resize red image
    rkwargs = dict(xlow=p['IC_CCDX_RED_LOW'], xhigh=p['IC_CCDX_RED_HIGH'],
                   ylow=p['IC_CCDY_RED_LOW'], yhigh=p['IC_CCDY_RED_HIGH'])
    datared, nx3, ny3 = spirouImage.ResizeImage(p, data, **rkwargs)
    # Make sure we have data in the red image
    if nx3 == 0 or ny3 == 0:
        WLOG(p, 'error', ('IC_CCD(X/Y)_RED_(LOW/HIGH) remove '
                                     'all pixels from image.'))

    # ----------------------------------------------------------------------
    # Dark Measurement
    # ----------------------------------------------------------------------
    # Log that we are doing dark measurement
    WLOG(p, '', 'Doing Dark measurement')
    # measure dark for whole frame
    p = spirouImage.MeasureDark(p, data, 'Whole det', 'full')
    # measure dark for blue part
    p = spirouImage.MeasureDark(p, datablue, 'Blue part', 'blue')
    # measure dark for rede part
    p = spirouImage.MeasureDark(p, datared, 'Red part', 'red')

    # ----------------------------------------------------------------------
    # Identification of bad pixels
    # ----------------------------------------------------------------------
    # get number of bad dark pixels (as a fraction of total pixels)
    with warnings.catch_warnings(record=True) as w:
        baddark = 100.0 * np.sum(data0 > p['DARK_CUTLIMIT'])
        baddark /= np.product(data0.shape)
    # log the fraction of bad dark pixels
    wmsg = 'Frac pixels with DARK > {0:.2f} ADU/s = {1:.3f} %'
    WLOG(p, 'info', wmsg.format(p['DARK_CUTLIMIT'], baddark))

    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as w:
        datacutmask = ~((data0 > p['DARK_CUTLIMIT']) | (~np.isfinite(data)))
    spirouCore.spirouLog.warninglogger(p, w)
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.product(data.shape) - np.nansum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    p['DADEADALL'] = n_bad_pix * 100 / np.product(data.shape)
    p.set_source('DADEADALL', __NAME__ + '/main()')
    # log fraction of dead pixels + dark > cut
    logargs = [p['DARK_CUTLIMIT'], p['DADEADALL']]
    WLOG(p, 'info', ('Total Frac dead pixels (N.A.N) + DARK > '
                                '{0:.2f} ADU/s = {1:.3f} %').format(*logargs))

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive plot
        sPlt.start_interactive_session(p)
        # plot the image with blue and red regions
        sPlt.darkplot_image_and_regions(p, data)
        # plot histograms
        sPlt.darkplot_histograms(p)
        # end interactive session
        sPlt.end_interactive_session(p)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
    # check that med < qc_max_darklevel
    if p['MED_FULL'] > p['QC_MAX_DARKLEVEL']:
        # add failed message to fail message list
        fmsg = 'Unexpected Median Dark level  ({0:5.2f} > {1:5.2f} ADU/s)'
        fail_msg.append(fmsg.format(p['MED_FULL'], p['QC_MAX_DARKLEVEL']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(p['MED_FULL'])
    qc_names.append('MED_FULL')
    qc_logic.append('MED_FULL > {0:.2f}'.format(p['QC_MAX_DARKLEVEL']))
    # ----------------------------------------------------------------------
    # check that fraction of dead pixels < qc_max_dead
    if p['DADEADALL'] > p['QC_MAX_DEAD']:
        # add failed message to fail message list
        fmsg = 'Unexpected Fraction of dead pixels ({0:5.2f} > {1:5.2f} %)'
        fail_msg.append(fmsg.format(p['DADEADALL'], p['QC_MAX_DEAD']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(p['DADEADALL'])
    qc_names.append('DADEADALL')
    qc_logic.append('DADEADALL > {0:.2f}'.format(p['QC_MAX_DEAD']))
    # ----------------------------------------------------------------------
    # checl that the precentage of dark pixels < qc_max_dark
    if baddark > p['QC_MAX_DARK']:
        fmsg = ('Unexpected Fraction of dark pixels > {0:.2f} ADU/s '
                '({1:.2f} > {2:.2f}')
        fail_msg.append(fmsg.format(p['DARK_CUTLIMIT'], baddark,
                                    p['QC_MAX_DARK']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(baddark)
    qc_names.append('baddark')
    qc_logic.append('baddark > {0:.2f}'.format(p['QC_MAX_DARK']))
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
    # Save dark to file
    # ----------------------------------------------------------------------
    # get raw dark filename
    rawdarkfile = os.path.basename(p['FITSFILENAME'])
    # construct folder and filename
    darkfits, tag = spirouConfig.Constants.DARK_FILE(p)
    darkfitsname = os.path.basename(darkfits)
    # log saving dark frame
    WLOG(p, '', 'Saving Dark frame in ' + darkfitsname)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    # define new keys to add
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['ARG_FILE_NAMES'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DARK_DEAD'],
                               value=p['DADEAD_FULL'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DARK_MED'], value=p['MED_FULL'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DARK_B_DEAD'],
                               value=p['DADEAD_BLUE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DARK_B_MED'],
                               value=p['MED_BLUE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DARK_R_DEAD'],
                               value=p['DADEAD_RED'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DARK_R_MED'], value=p['MED_RED'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DARK_CUT'],
                               value=p['DARK_CUTLIMIT'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)

    # Set to zero dark value > dark_cutlimit
    cutmask = data0 > p['DARK_CUTLIMIT']
    data0c = np.where(cutmask, np.zeros_like(data0), data0)
    # write image and add header keys (via hdict)
    p = spirouImage.WriteImage(p, darkfits, data0c, hdict)

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # construct bad pixel file name
    badpixelfits, tag = spirouConfig.Constants.DARK_BADPIX_FILE(p)
    badpixelfitsname = os.path.split(badpixelfits)[-1]
    # log that we are saving bad pixel map in dir
    WLOG(p, '', 'Saving Bad Pixel Map in ' + badpixelfitsname)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    # define new keys to add
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)

    hdict['DACUT'] = (p['DARK_CUTLIMIT'],
                      'Threshold of dark level retain [ADU/s]')
    # write to file
    datacutmask = np.array(datacutmask, dtype=float)
    p = spirouImage.WriteImage(p, badpixelfits, datacutmask, hdict,
                               dtype='float64')

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        # set dark key
        if p['DPRTYPE'] == 'DARK_DARK':
            keydb = 'DARK'
        elif p['USE_SKYDARK_CORRECTION']:
            keydb = 'SKYDARK'
        else:
            emsg = 'Error: Currently {0} only supports DARK_DARK and OBJ_DARK'
            WLOG(p, 'error', emsg.format(__NAME__))
        # copy dark fits file to the calibDB folder
        spirouDB.PutCalibFile(p, darkfits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, darkfitsname, hdr)

        # # set badpix key
        # keydb = 'BADPIX_OLD'
        # # copy badpix fits file to calibDB folder
        # spirouDB.PutCalibFile(p, badpixelfits)
        # # update the master calib DB file with new key
        # spirouDB.UpdateCalibMaster(p, keydb, badpixelfitsname, hdr)

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

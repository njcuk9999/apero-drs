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

from SpirouDRS import spirouCDB
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
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, kind='dark', prefixes=['dark_dark'])

    # log processing image type
    p['dprtype'] = spirouImage.GetTypeFromHeader(p, p['kw_DPRTYPE'])
    p.set_source('dprtype', __NAME__ + '/main()')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['log_opt'], wmsg.format(p['dprtype'], p['program']))

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    rout = spirouImage.ReadImageAndCombine(p, framemath='average')
    data, hdr, cdr, nx, ny = rout

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
    WLOG('info', p['log_opt'], 'Dark Time = {0:.3f} s'.format(p['exptime']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if p['exptime'] < p['QC_DARK_TIME']:
        emsg = 'Dark exposure time too short (< {0:.1f} s)'
        WLOG('error', p['log_opt'], emsg.format(p['QC_DARK_TIME']))

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
    datablue, nx2, ny2 = spirouImage.ResizeImage(data, **bkwargs)
    # Make sure we have data in the blue image
    if nx2 == 0 or ny2 == 0:
        WLOG('error', p['log_opt'], ('IC_CCD(X/Y)_BLUE_(LOW/HIGH) remove '
                                     'all pixels from image.'))
    # resize red image
    rkwargs = dict(xlow=p['IC_CCDX_RED_LOW'], xhigh=p['IC_CCDX_RED_HIGH'],
                   ylow=p['IC_CCDY_RED_LOW'], yhigh=p['IC_CCDY_RED_HIGH'])
    datared, nx3, ny3 = spirouImage.ResizeImage(data, **rkwargs)
    # Make sure we have data in the red image
    if nx3 == 0 or ny3 == 0:
        WLOG('error', p['log_opt'], ('IC_CCD(X/Y)_RED_(LOW/HIGH) remove '
                                     'all pixels from image.'))

    # ----------------------------------------------------------------------
    # Dark Measurement
    # ----------------------------------------------------------------------
    # Log that we are doing dark measurement
    WLOG('', p['log_opt'], 'Doing Dark measurement')
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
        baddark = 100.0 * np.sum(data > p['DARK_CUTLIMIT'])
        baddark /= np.product(data.shape)
    # log the fraction of bad dark pixels
    wmsg = 'Frac pixels with DARK > {0:.1f} ADU/s = {1:.1f} %'
    WLOG('info', p['log_opt'], wmsg.format(p['DARK_CUTLIMIT'], baddark))

    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as w:
        datacutmask = ~((data > p['DARK_CUTLIMIT']) | (~np.isfinite(data)))
    spirouCore.spirouLog.warninglogger(w)
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.product(data.shape) - np.sum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    p['dadeadall'] = n_bad_pix * 100 / np.product(data.shape)
    p.set_source('dadeadall', __NAME__ + '/main()')
    # log fraction of dead pixels + dark > cut
    logargs = [p['DARK_CUTLIMIT'], p['dadeadall']]
    WLOG('info', p['log_opt'], ('Total Frac dead pixels (N.A.N) + DARK > '
                                '{0:.1f} ADU/s = {1:.1f} %').format(*logargs))

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()
        # plot the image with blue and red regions
        sPlt.darkplot_image_and_regions(p, data)
        # plot the data cut
        sPlt.darkplot_datacut(datacutmask)
        # plot histograms
        sPlt.darkplot_histograms(p)
        # end interactive session
        sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # check that med < qc_max_darklevel
    if p['med_full'] > p['QC_MAX_DARKLEVEL']:
        # add failed message to fail message list
        fmsg = 'Unexpected Median Dark level  ({0:5.2f} > {1:5.2f} ADU/s)'
        fail_msg.append(fmsg.format(p['med_full'], p['QC_MAX_DARKLEVEL']))
        passed = False

    # check that fraction of dead pixels < qc_max_dead
    if p['dadeadall'] > p['QC_MAX_DEAD']:
        # add failed message to fail message list
        fmsg = 'Unexpected Fraction of dead pixels ({0:5.2f} > {1:5.2f} %)'
        fail_msg.append(fmsg.format(p['dadeadall'], p['QC_MAX_DEAD']))
        passed = False

    # checl that the precentage of dark pixels < qc_max_dark
    if baddark > p['QC_MAX_DARK']:
        fmsg = ('Unexpected Fraction of dark pixels > {0:.2f} ADU/s '
                '({1:.2f} > {2:.2f}')
        fail_msg.append(fmsg.format(p['DARK_CUTLIMIT'], baddark,
                                    p['QC_MAX_DARK']))
        passed = False

    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['log_opt'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('info', p['log_opt'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Save dark to file
    # ----------------------------------------------------------------------

    # construct folder and filename
    darkfits = spirouConfig.Constants.DARK_FILE(p)
    darkfitsname = os.path.split(darkfits)[-1]
    # log saving dark frame
    WLOG('', p['log_opt'], 'Saving Dark frame in ' + darkfitsname)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict = spirouImage.AddKey(hdict, p['kw_DARK_DEAD'],
                               value=p['dadead_full'])
    hdict = spirouImage.AddKey(hdict, p['kw_DARK_MED'],
                               value=p['med_full'])
    hdict = spirouImage.AddKey(hdict, p['kw_DARK_B_DEAD'],
                               value=p['dadead_blue'])
    hdict = spirouImage.AddKey(hdict, p['kw_DARK_B_MED'],
                               value=p['med_blue'])
    hdict = spirouImage.AddKey(hdict, p['kw_DARK_R_DEAD'],
                               value=p['dadead_red'])
    hdict = spirouImage.AddKey(hdict, p['kw_DARK_R_MED'],
                               value=p['med_red'])
    hdict = spirouImage.AddKey(hdict, p['kw_DARK_CUT'],
                               value=p['DARK_CUTLIMIT'])
    # write image and add header keys (via hdict)
    spirouImage.WriteImage(darkfits, data0, hdict)

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # construct bad pixel file name
    badpixelfits = spirouConfig.Constants.DARK_BADPIX_FILE(p)
    badpixelfitsname = os.path.split(badpixelfits)[-1]
    # log that we are saving bad pixel map in dir
    WLOG('', p['log_opt'], 'Saving Bad Pixel Map in ' + badpixelfitsname)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict['DACUT'] = (p['DARK_CUTLIMIT'],
                      'Threshold of dark level retain [ADU/s]')
    # write to file
    datacutmask = np.array(datacutmask, dtype=float)
    spirouImage.WriteImage(badpixelfits, datacutmask, hdict, dtype='float64')

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        # set dark key
        keydb = 'DARK'
        # copy dark fits file to the calibDB folder
        spirouCDB.PutFile(p, darkfits)
        # update the master calib DB file with new key
        spirouCDB.UpdateMaster(p, keydb, darkfitsname, hdr)
        # set badpix key
        keydb = 'BADPIX_OLD'
        # copy badpix fits file to calibDB folder
        spirouCDB.PutFile(p, badpixelfits)
        # update the master calib DB file with new key
        spirouCDB.UpdateMaster(p, keydb, badpixelfitsname, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))
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

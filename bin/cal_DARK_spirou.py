#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DARK_spirou.py [night_directory] [fitsfilename]

Prepares the dark files for SPIRou

Created on 2017-10-11 at 10:45

@author: cook

Version 0.0.1

Last modified: 2017-10-11 at 10:49
"""

import numpy as np
import os
import warnings

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

import time
neilstart = time.time()

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DARK_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt

# -----------------------------------------------------------------------------
# Remove this for final (only for testing)
import sys
if len(sys.argv) == 1:
    sys.argv = ['test: ' + __NAME__, '20170710', 'dark_dark02d406.fits']

# =============================================================================
# Define functions
# =============================================================================
def measure_dark(pp, image, image_name, short_name):
    """
    Measure the dark pixels in "image"

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :param image_name: string, the name of the image (for logging)
    :param short_name: string, suffix (for parameter naming -
                        parmaeters added to pp with suffix i)
    :return pp: dictionary, parameter dictionary
    """

    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = np.median(fimage)
    # get the 5th and 95h percentile qmin
    qmin, qmax = np.percentile(fimage, [pp['DARK_QMIN'], pp['DARK_QMAX']])
    # get the histogram for flattened data
    histo = np.histogram(fimage, bins=p['HISTO_BINS'],
                         range=(pp['HISTO_RANGE_LOW'], pp['HISTO_RANGE_HIGH']))
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    largs = ['In {0}'.format(image_name), dadead, med, pp['DARK_QMIN'],
             pp['DARK_QMAX'], qmin, qmax]
    WLOG('info', pp['log_opt'], ('{0:12s}: Frac dead pixels= {1:.1f} % - '
                                 'Median= {2:.2f} ADU/s - '
                                 'Percent[{3}:{4}]= {5:.2f}-{6:.2f} ADU/s'
                                 '').format(*largs))
    # add required variables to pp
    source = '{0}/{1}'.format(__NAME__, 'measure_dark()')
    pp['histo_{0}'.format(short_name)] = histo
    pp.set_source('histo_{0}'.format(short_name), source)
    pp['med_{0}'.format(short_name)] = med
    pp.set_source('med_{0}'.format(short_name), source)
    pp['dadead_{0}'.format(short_name)] = dadead
    pp.set_source('dadead_{0}'.format(short_name), source)

    return pp


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
    p = spirouStartup.RunStartup(p, kind='dark', prefixes=['dark_dark'])
    # log processing image type
    p['dprtype'] = spirouImage.GetTypeFromHeader(p, p['kw_DPRTYPE'])
    p.set_source('dprtype', __NAME__ + '/__main__')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['log_opt'], wmsg.format(p['dprtype'], p['program']))

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImageAndCombine(p, framemath='average')

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
    WLOG('info', p['log_opt'], 'Dark Time = {0:.3f} [s]'.format(p['exptime']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if p['exptime'] < p['QC_DARK_TIME']:
        WLOG('error', p['log_opt'], 'Dark exposure time too short')

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
    p = measure_dark(p, data, 'Whole det', 'full')
    # measure dark for blue part
    p = measure_dark(p, datablue, 'Blue part', 'blue')
    # measure dark for rede part
    p = measure_dark(p, datared, 'Red part', 'red')

    # ----------------------------------------------------------------------
    # Identification of bad pixels
    # ----------------------------------------------------------------------
    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as w:
        datacutmask = ~((data > p['DARK_CUTLIMIT']) | (~np.isfinite(data)))
    spirouCore.spirouLog.warninglogger(w)
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.product(data.shape) - np.sum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    p['dadeadall'] = n_bad_pix * 100 / np.product(data.shape)
    p.set_source('dadeadall', __NAME__ + '/__main__')
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
        fmsg = 'Unexpected Dark level  ({0:5.2f} > {1:5.2f} ADU/s)'
        fail_msg.append(fmsg.format(p['med_full'], p['QC_MAX_DARKLEVEL']))
        passed = False
    # check that fraction of dead pixels < qc_max_dead
    if p['dadeadall'] > p['QC_MAX_DEAD']:
        # add failed message to fail message list
        fmsg = 'Unexpected Fraction of dead pixels ({0:5.2f} > {1:5.2f} %)'
        fail_msg.append(fmsg.format(p['dadeadall'], p['QC_MAX_DEAD']))
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
    # Save dark to file
    # ----------------------------------------------------------------------

    # construct folder and filename
    reducedfolder = p['reduced_dir']
    darkfits = p['arg_file_names'][0]
    # log saving dark frame
    WLOG('', p['log_opt'], 'Saving Dark frame in ' + darkfits)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    spirouImage.AddKey(hdict, p['kw_DARK_DEAD'], value=p['dadead_full'])
    spirouImage.AddKey(hdict, p['kw_DARK_MED'], value=p['med_full'])
    spirouImage.AddKey(hdict, p['kw_DARK_B_DEAD'], value=p['dadead_blue'])
    spirouImage.AddKey(hdict, p['kw_DARK_B_MED'], value=p['med_blue'])
    spirouImage.AddKey(hdict, p['kw_DARK_R_DEAD'], value=p['dadead_red'])
    spirouImage.AddKey(hdict, p['kw_DARK_R_MED'], value=p['med_red'])
    spirouImage.AddKey(hdict, p['kw_DARK_CUT'], value=p['DARK_CUTLIMIT'])
    # write image and add header keys (via hdict)
    spirouImage.WriteImage(os.path.join(reducedfolder, darkfits), data0, hdict)

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # construct bad pixel file name
    badpixelfits = p['arg_file_names'][0].replace('.fits', '_badpixel.fits')
    # log that we are saving bad pixel map in dir
    WLOG('', p['log_opt'], 'Saving Bad Pixel Map in ' + badpixelfits)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict['DACUT'] = (p['DARK_CUTLIMIT'],
                      'Threshold of dark level retain [ADU/s]')
    # write to file
    datacutmask = np.array(datacutmask, dtype=int)
    spirouImage.WriteImage(os.path.join(reducedfolder, badpixelfits),
                           datacutmask, hdict)

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        keydb = 'DARK'
        # copy dark fits file to the calibDB folder
        spirouCDB.PutFile(p, os.path.join(reducedfolder, darkfits))
        # update the master calib DB file with new key
        spirouCDB.UpdateMaster(p, keydb, darkfits, hdr)

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

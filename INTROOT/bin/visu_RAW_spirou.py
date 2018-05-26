#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
visu_RAW_spirou.py [night_directory] [*.fits]

Recipe to display raw frame + cut across orders + statistics

Created on 2017-12-06 at 14:50

@author: cook

Last modified: 2017-12-11 at 15:23

Up-to-date with cal_BADPIX_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'visu_RAW_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    p = spirouStartup.LoadArguments(p)
    p = spirouStartup.InitialFileSetup(p, kind=None, calibdb=False)
     # log processing image type
    p['DPRTYPE'] = spirouImage.GetTypeFromHeader(p, p['KW_DPRTYPE'])
    p.set_source('DPRTYPE', __NAME__ + '/main()')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'

    WLOG('info', p['LOG_OPT'], wmsg.format(p['DPRTYPE'], p['PROGRAM']))


    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cmt, nx, ny = spirouImage.ReadImage(p)
    # ----------------------------------------------------------------------
    # Get basic image properties
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # now change the value of sigdet if require
    if p['IC_EXT_SIGDET'] > 0:
        p['SIGDET'] = float(p['IC_EXT_SIGDET'])

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToADU(spirouImage.FlipImage(data), p=p)
    # convert NaN to zeros
    data2 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
#    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
#                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
#                   getshape=False)
#    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
#    WLOG('', p['log_opt'], ('Image format changed to '
#                            '{0}x{1}').format(*data2.shape[::-1]))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 == 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    satseuil = 64536.
    col = 2100
    seuil = 10000
    slice = 20

    plt.ion()
    plt.clf()
    plt.imshow(data2, origin='lower', clim=(1., seuil))
    plt.colorbar()
    plt.axis([0, nx, 0, ny])
    plt.plot(np.ones(4096) * col, np.arange(4096), c='red')

    plt.figure()
    plt.clf()

    centpart = data2[:, col - 10:col + 10]
#    centpart = data2[col - slice:col + slice,:]
    weights = np.where((centpart < satseuil) & (centpart > 0), 1, 0.0001)
    y = np.average(centpart, axis=1, weights=weights)  ## weighted average
    # y=average(centpart,axis=1,weights=where((centpart>0),1,0.0001))   ## weighted average
    plt.plot(np.arange(ny), y)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================







#data2 = where(np.isnan(data), 0., data)  # conversion des Not.A.Number par 0.

#fdata = array(data2.flat)
#fdata.sort()
#imax = sum(where(fdata > satseuil, 1, 0))
#imin = sum(where(fdata == 0, 1, 0))


# output=plt.hist(fdata,65.535)

# histo=np.histogram(fdata,bins=100,range=(1,20000))

#mean = Numeric.mean(fdata)
#rms = Numeric.std(fdata)

#WLOG('', log_opt, 'Exptime= %.1f sec - Saturation limit= %.1f e-' % (exptime, 64536 * gain))

#WLOG('', log_opt, 'Full image : MEAN= %.1f e- / RMS= %.1f e- / Frac>Saturation= %.1f %% / Frac bad pixels= %.1f %%' \
#     % (mean, rms, imax * 100. / (nx * ny), imin * 100. / (nx * ny)))

#WLOG('info', log_opt, 'Recipe ' + process_running + ' has been succesfully completed')

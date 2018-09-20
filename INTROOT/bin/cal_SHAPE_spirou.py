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
    p['FIBER'] = 'AB'
    p.set_source('FIBER', __NAME__ + '/main()')

    # TODO: Add these to constants_H4RG_spirou.py

    # The number of iterations to run the shape finding out to
    p['SHAPE_NUM_ITERATIONS'] = 3
    # width of the ABC fibers
    p['SHAPE_ABC_WIDTH'] = 53



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

    # save data to loc
    loc = ParamDict()
    loc['DATA'] = data2
    loc.set_source('DATA', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 <= 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p = spirouImage.FiberParams(p, p['FIBER'], merge=True)
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr, loc)

    # ------------------------------------------------------------------
    # Calculate shape map
    # ------------------------------------------------------------------
    get_shape_map(p, loc)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------



def get_shape_map(p, loc):


    from SpirouDRS import spirouEXTOR

    # get constants from p
    shape_it = p['SHAPE_NUM_ITERATIONS']
    width = p['SHAPE_ABC_WIDTH']
    p_edge = p['SHAPE_PROFILE_EDGE']

    # get data from loc
    data1 = np.array(loc['DATA'])
    nbo = loc['NUMBER_ORDERS']
    acc = loc['ACC']

    # get the dimensions
    dim0, dim1 = loc['DATA'].shape[1]


    master_dxmap = np.zeros_like(data1)

    # loop around orders
    for order_num in range(nbo):
        # create the x pixel vector (used with polynomials to find
        #    order center)
        xpix = np.arange(dim1)
        # y order center positions
        ypix = np.polyval(acc[:, order_num][::-1], xpix)
        # top and bottom pixels that encompass all 3 fibers
        ytop = np.array(ypix + width / 2, dtype=int)
        ybottom = np.array(ypix - width / 2, dtype=int)

        # loop around the number of iterations
        for banana_num in range(shape_it):

            # straighten the image with the current master_dump
            data2 = spirouEXTOR.DeBananafication(data1, master_dxmap)
            # we put NaNs on all pixels outside of the order box
            for i in range(len(xpix)):
                data2[0:ybottom[i], xpix[i]] = np.nan
                data2[ytop[i]:, xpix[i]] = np.nan
            # we do a "dump" extraction by collapsing the order
            # along the y axis to find the highest peak
            profile = np.nanmedian(data2, axis=0)
            # no peaks too close to the edges
            profile[:p_edge] = 0.0
            profile[-p_edge:] = 0.0
            # brightest peak, should be an FP line will be used afterward
            # for the thresholding of peak finding. We only search for
            # peaks that are more than 0.3*maxpeak
            maxpeak = np.nanmax(profile)
            # get the current maximum peak
            current_max = float(maxpeak)
            # set up the current shape map (NaN array)
            dxmap = np.repeat(np.nan, width*dim1).reshape(width, dim1)
            # set up the x position peaks
            xpospeak = np.zeros(dim1)
            # set up the slopes
            allslopes


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

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

from SpirouDRS import spirouEXTOR
from SpirouDRS.spirouCore import spirouMath

from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline
from scipy.ndimage import filters
from scipy.stats import stats
import warnings

import time

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
    p['SHAPE_ABC_WIDTH'] = 55
    # the range of angles (in degrees) for the first iteration (large)
    # and subsequent iterations (small)
    p['SHAPE_LARGE_ANGLE_RANGE'] = [-12.0, 0.0]
    p['SHAPE_SMALL_ANGLE_RANGE'] = [-1.0, 1.0]
    # number of sections per order to split the order into
    p['SHAPE_NSECTIONS'] = 32
    # max sigma clip (in sigma) on points within a section
    p['SHAPE_SIGMACLIP_MAX'] = 4
    # the size of the median filter to apply along the order (in pixels)
    p['SHAPE_MEDIAN_FILTER_SIZE'] = 51
    # The minimum value for the cross-correlation to be deemed good
    p['SHAPE_MIN_GOOD_CORRELATION'] = 0.1

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
    # p, datac = spirouImage.CorrectForDark(p, data, hdr)
    datac = data

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
    # p, data2 = spirouImage.CorrectForBadPix(p, data2, hdr)

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
    # data2 = np.where(data2 > 0, data2 - background, 0)

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
    p, loc = spirouLOCOR.GetCoeffs(p, hdr, loc)

    # ------------------------------------------------------------------
    # Calculate shape map
    # ------------------------------------------------------------------
    loc = get_shape_map(p, loc)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    # TODO: Decide which plots to take from new_bananarama.py

    # ------------------------------------------------------------------
    # Writing to file
    # ------------------------------------------------------------------
    # get the raw tilt file name
    raw_shape_file = os.path.basename(p['FITSFILENAME'])
    # construct file name and path
    shapefits, tag = spirouConfig.Constants.SLIT_TILT_FILE(p)
    shapefitsname = os.path.basename(shapefits)
    # Log that we are saving tilt file
    wmsg = 'Saving shape information in file: {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(shapefitsname))
    # Copy keys from fits file
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # add version number
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey(hdict, p['KW_DARKFILE'], value=p['DARKFILE'])
    hdict = spirouImage.AddKey(hdict, p['KW_BADPFILE1'], value=p['BADPFILE1'])
    hdict = spirouImage.AddKey(hdict, p['KW_BADPFILE2'], value=p['BADPFILE2'])
    hdict = spirouImage.AddKey(hdict, p['KW_LOCOFILE'], value=p['LOCOFILE'])
    hdict = spirouImage.AddKey(hdict, p['KW_SHAPEFILE'], value=raw_shape_file)
    # write tilt file to file
    p = spirouImage.WriteImage(p, shapefits, loc['DXMAP'], hdict)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # TODO: Decide on some quality control criteria?

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    # TODO: Move to calibDB under key = SHAPE

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())



# TODO: Move to SpirouDRS
def get_shape_map(p, loc):

    # get constants from p
    nbanana = p['SHAPE_NUM_ITERATIONS']
    width = p['SHAPE_ABC_WIDTH']
    nsections = p['SHAPE_NSECTIONS']
    large_angle_range = p['SHAPE_LARGE_ANGLE_RANGE']
    small_angle_range = p['SHAPE_SMALL_ANGLE_RANGE']
    sigclipmax = p['SHAPE_SIGMACLIP_MAX']
    med_filter_size = p['SHAPE_MEDIAN_FILTER_SIZE']
    min_good_corr = p['SHAPE_MIN_GOOD_CORRELATION']

    # get data from loc
    data1 = np.array(loc['DATA'])
    nbo = loc['NUMBER_ORDERS'] // 2
    acc = loc['ACC']

    # get the dimensions
    dim0, dim1 = loc['DATA'].shape
    master_dxmap = np.zeros_like(data1)
    # -------------------------------------------------------------------------
    # iterating the correction, from coarser to finer
    for banana_num in range(nbanana):
        # ---------------------------------------------------------------------
        # we use the code that will be used by the extraction to ensure
        # that slice images are as straight as can be
        # ---------------------------------------------------------------------
        # if the map is not zeros, we use it as a starting point
        if np.sum(master_dxmap != 0) != 0:
            data2 = spirouEXTOR.DeBananafication(data1, master_dxmap)
            # if this is not the first iteration, then we must be really close
            # to a slope of 0
            range_slopes_deg = small_angle_range
        else:
            data2 = np.array(data1)
            # starting point for slope exploration
            range_slopes_deg = large_angle_range
        # expressed in pixels, not degrees
        range_slopes = np.tan(np.deg2rad(np.array(range_slopes_deg)))
        # ---------------------------------------------------------------------
        # loop around orders
        for order_num in range(nbo):
            # -----------------------------------------------------------------
            # Log progress
            wmsg = 'Banana iteration: {0}: Order {1}/{2} '
            wargs = [banana_num + 1, order_num + 1, nbo]
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
            # -----------------------------------------------------------------
            # create the x pixel vector (used with polynomials to find
            #    order center)
            xpix = np.arange(dim1)
            # y order center positions (every other one)
            ypix = np.polyval(acc[order_num * 2][::-1], xpix)
            # defining a ribbon that will contain the straightened order
            ribbon = np.zeros([width, dim1])
            # splitting the original image onto the ribbon
            for ix in range(dim1):
                # define bottom and top that encompasses all 3 fibers
                bottom = int(ypix[ix] - width/2 - 2)
                top = int(ypix[ix] + width/2 + 2)
                sx = np.arange(bottom, top)
                widths = np.arange(width) - width/2.0
                # calculate spline interpolation and ribbon values
                if bottom > 0:
                    spline = IUVSpline(sx, data2[bottom:top, ix], ext=1, k=1)
                    ribbon[:, ix] = spline(ypix[ix] + widths)
            # normalizing ribbon stripes to their median abs dev
            for iw in range(width):
                norm = np.nanmedian(np.abs(ribbon[iw, :]))
                ribbon[iw, :] = ribbon[iw, :] / norm
            # range explored in slopes
            # TODO: Question: Where does the /8.0 come from?
            sfactor = (range_slopes[1] - range_slopes[0]) / 8.0
            slopes = (np.arange(9) * sfactor) + range_slopes[0]
            # log the range slope exploration
            wmsg = '\tRange slope exploration: {0:.3f} -> {1:.3f} deg'
            wargs = [range_slopes_deg[0], range_slopes_deg[1]]
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
            # -------------------------------------------------------------
            # the domain is sliced into a number of sections, then we
            # find the tilt that maximizes the RV content
            xsection = dim1 * (np.arange(nsections) + 0.5) / nsections
            dxsection = np.repeat([np.nan], len(xsection))
            keep = np.zeros(len(dxsection), dtype=bool)
            ribbon2 = np.array(ribbon)
            # RV content per slice and per slope
            rvcontent = np.zeros([len(slopes), nsections])
            # loop around the slopes
            for islope, slope in enumerate(slopes):
                # copy the ribbon
                ribbon2 = np.array(ribbon)
                # interpolate new slope-ed ribbon
                for iw in range(width):
                    # get the ddx value
                    ddx = (iw - width/2.0) * slope
                    # get the spline
                    spline = IUVSpline(xpix, ribbon[iw, :], ext=1)
                    # calculate the new ribbon values
                    ribbon2[iw, :] = spline(xpix + ddx)
                # record the profile of the ribbon
                profile = np.nanmedian(ribbon2, axis=0)
                # loop around the sections to record rv content
                for nsection in range(nsections):
                    # sum of integral of derivatives == RV content.
                    # This should be maximal when the angle is right
                    start = nsection * dim1//nsections
                    end = (nsection + 1) * dim1//nsections
                    grad = np.gradient(profile[start:end])
                    rvcontent[islope, nsection] = np.nansum(grad ** 2)
            # -------------------------------------------------------------
            # we find the peak of RV content and fit a parabola to that peak
            for nsection in range(nsections):
                # we must have some RV content (i.e., !=0)
                if np.nanmax(rvcontent[:, nsection]) != 0:
                    vec = np.ones_like(slopes)
                    vec[0], vec[-1] = 0, 0
                    # get the max pixel
                    maxpix = np.nanargmax(rvcontent[:, nsection] * vec)
                    # max RV and fit on the neighbouring pixels
                    xff = slopes[maxpix - 1: maxpix + 2]
                    yff = rvcontent[maxpix - 1: maxpix + 2, nsection]
                    coeffs = np.polyfit(xff, yff, 2)
                    # if peak within range, then its fine
                    dcoeffs = -0.5 * coeffs[1] / coeffs[0]
                    if np.abs(dcoeffs) < 1:
                        dxsection[nsection] = dcoeffs
                # we sigma-clip the dx[x] values relative to a linear fit
                keep = np.isfinite(dxsection)
            # -------------------------------------------------------------
            # sigma clip
            sigmax = np.inf
            while sigmax > sigclipmax:
                # recalculate the fit
                coeffs = np.polyfit(xsection[keep], dxsection[keep], 2)
                # get the residuals
                res = dxsection - np.polyval(coeffs, xsection)
                # normalise residuals
                res = res - np.nanmedian(res[keep])
                res = res / np.nanmedian(np.abs(res[keep]))
                # calculate the sigma
                sigmax = np.nanmax(np.abs(res[keep]))
                # do not keep bad residuals
                with warnings.catch_warnings(record=True) as _:
                    keep &= np.abs(res) < sigclipmax
            # -------------------------------------------------------------
            # fit a 2nd order polynomial to the slope vx position
            #    along order
            coeffs = np.polyfit(xsection[keep], dxsection[keep], 2)
            # log slope at center
            s_xpix = dim1//2
            s_ypix = np.rad2deg(np.arctan(np.polyval(coeffs, s_xpix)))
            wmsg = '\tSlope at pixel {0}: {1:.5f} deg'
            wargs = [s_xpix, s_ypix]
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
            # get slope for full range
            slope = np.polyval(coeffs, np.arange(dim1))
            # -------------------------------------------------------------
            # TODO: plots
            # -------------------------------------------------------------
            # correct for the slope the ribbons and look for the
            yfit = np.polyval(coeffs, xpix)
            #    slicer profile
            for iw in range(width):
                # get the x shift
                ddx = (iw - width/2.0) * yfit
                # calculate the spline at this width
                spline = IUVSpline(xpix, ribbon[iw, :], ext=1)
                # push spline values with shift into ribbon2
                ribbon2[iw, :] = spline(xpix + ddx)

            # median FP peak profile. We will cross-correlate each
            # row of the ribbon with this
            profile = np.nanmedian(ribbon2, axis=0)
            medianprofile = filters.median_filter(profile, med_filter_size)
            profile = profile - medianprofile

            # -------------------------------------------------------------
            # cross-correlation peaks of median profile VS position
            #    along ribbon
            # reset dx and ddx
            dx = np.repeat([np.nan], width)
            # TODO: Question: Why -3 to 4 where does this come from?
            ddx = np.arange(-3, 4)
            # set up cross-correlation storage
            ccor = np.zeros([width, len(ddx)], dtype=float)
            # loop around widths
            for iw in range(width):
                for jw in range(len(ddx)):
                    # calculate the peasron r coefficient
                    xff = ribbon2[iw, :]
                    yff = np.roll(profile, ddx[jw])
                    pearsonr_value = stats.pearsonr(xff, yff)[0]
                    # push into cross-correlation storage
                    ccor[iw, jw] = pearsonr_value
                # fit a gaussian to the cross-correlation peak
                xvec = ddx
                yvec = ccor[iw, :]
                with warnings.catch_warnings(record=True) as _:
                    gcoeffs, _ = spirouMath.gauss_fit_nn(xvec, yvec, 4)
                # check that max value is good
                if np.nanmax(ccor[iw, :]) > min_good_corr:
                    dx[iw] = gcoeffs[1]
            # -------------------------------------------------------------
            # remove any offset in dx, this would only shift the spectra
            dx = dx - np.nanmedian(dx)
            dypix = np.arange(len(dx))
            with warnings.catch_warnings(record=True):
                keep = np.abs(dx) < 1
            keep &= np.isfinite(dx)
            # -------------------------------------------------------------
            # if the first pixel is nan and the second is OK,
            #    then for continuity, pad
            if (not keep[0]) and keep[1]:
                keep[0] = True
                dx[0] = dx[1]
            # same at the other end
            if (not keep[-1]) and keep[-2]:
                keep[-1] = True
                dx[-1] = dx[-2]
            # -------------------------------------------------------------
            # TODO: plots
            # -------------------------------------------------------------
            # spline everything onto the master DX map
            spline = IUVSpline(dypix[keep], dx[keep], ext=0)
            # for all field positions along the order, we determine the
            #    dx+rotation values and update the master DX map
            for ix in range(dim1):
                # get the fraction missed
                frac = ypix[ix] - np.fix(ypix[ix])
                # get dx0 with slope factor added
                dx0 = (np.arange(width) - width // 2 + (1 - frac)) * slope[ix]
                # get the ypix at this value
                ypix2 = int(ypix[ix]) + np.arange(-width//2, width//2)
                # get the ddx
                ddx = spline(np.arange(width) - frac)
                # set the zero shifts to NaNs
                ddx[ddx == 0] = np.nan
                # only set positive ypixels
                pos_y_mask = ypix2 >= 0
                # if we have some values add to master DX map
                if np.sum(pos_y_mask) != 0:
                    # get positions in y
                    positions = ypix2[pos_y_mask]
                    # get shifts combination od ddx and dx0 correction
                    shifts = (ddx + dx0)[pos_y_mask]
                    # apply shifts to master dx map at correct positions
                    master_dxmap[positions, ix] += shifts

    # finally add DXMAP to loc
    loc['DXMAP'] = master_dxmap
    # return loc
    return loc


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

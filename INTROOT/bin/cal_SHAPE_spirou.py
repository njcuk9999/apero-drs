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
import warnings

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

    p['SHAPE_LARGE_ANGLE_RANGE'] = [-11/30.0, 5/30.0, 1/30.0]
    p['SHAPE_SMALL_ANGLE_RANGE'] = [-1/30.0, 2/30.0, 1/30.0]

    p['SHAPE_LARGE_ANGLE_NUM'] = 20

    p['SHAPE_TRACK_NPEAKS'] = 300

    p['SHAPE_SIGCUT_SLOPE'] = 10

    p['SHAPE_GFIT_EWMIN'] = 0.5
    p['SHAPE_GFIT_EWMAX'] = 1.5
    p['SHAPE_GFIT_DXMAX'] = 1.5


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

    # get constants from p
    nbanana = p['SHAPE_NUM_ITERATIONS']
    width = p['SHAPE_ABC_WIDTH']
    sig_cut = p['SHAPE_SIGCUT_SLOPE']
    ew_min, ew_max = p['SHAPE_GFIT_EWMIN'], p['SHAPE_GFIT_EWMAX']
    dx_max = p['SHAPE_GFIT_DXMAX']

    # get data from loc
    data1 = np.array(loc['DATA'])
    nbo = loc['NUMBER_ORDERS']
    acc = loc['ACC']

    # get the dimensions
    dim0, dim1 = loc['DATA'].shape[1]


    master_dxmap = np.zeros_like(data1)

    xpospeak_all = []
    allslopes_all = []

    # iterating the correction, from coarser to finer
    for banana_num in range(nbanana):

        # we use the code that will be used by the extraction to ensure
        # that slice images are as straight as can be

        # if the map is not zeros, we use it as a starting point
        if np.sum(master_dxmap != 0) != 0:
            data2 = spirouEXTOR.DeBananafication(data1, master_dxmap)
            flag_start_slope = False
        else:
            data2 = np.array(data1)
            flag_start_slope = True




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

        for banana_num in range(nbanana):
            # straighten the image with the current master_dump
            data2 = spirouEXTOR.DeBananafication(data1, master_dxmap)
            # we put NaNs on all pixels outside of the order box
            for ix in range(len(xpix)):
                data2[0:ybottom[ix], xpix[ix]] = np.nan
                data2[ytop[ix]:, xpix[ix]] = np.nan
            # find all slopes/slices and positions of peaks
            fargs = [p, loc, data2, order_num, banana_num, xpix,
                     ytop, ybottom]
            allslopes, allslices, xpospeak = find_peaks(*fargs)

            # keep all valid slopes and peak positions
            keep = np.isfinite(allslopes)
            # no slope can be a >sigcut simga outlier
            kvalue = np.abs(allslopes - np.nanmedian(allslopes))
            keep &= kvalue < (sig_cut * np.nanmedian(kvalue))

            # apply keep cut to xposspeak and allslopes
            xpospeak = xpospeak[keep]
            allslopes = allslopes[keep]

            # median trace of the brightest p['SHAPE_TRACK_NPEAKS'] peaks
            #     after de-rotation
            bigtrace = np.nanmedian(allslices, axis=2)

            # get storage for profiles
            dx, ew = np.zeros(width), np.zeros(width)
            # loop around with and fill
            for it in range(width):
                bigtrace[it, :] -= np.nanmin(bigtrace[it, :])
                bigtrace[it, :] /= np.nanmin(bigtrace[it, :])

                xvec, yvec = np.arange(6), bigtrace[it, :]
                gcoeffs, a = spirouMath.gauss_fit_nn(xvec, yvec, 4)
                ew[it] = gcoeffs[2] # gaussian width, must be reasonable
                dx[it] = gcoeffs[1] # center of gaussian

            # some sanity checks
            keep1 = np.isfinite(dx)
            keep1 &= ew < ew_max
            keep1 &= ew > ew_min
            keep1 &= np.abs(dx - np.nanmedian(dx) < dx_max)


            # get dy pixel vector
            dypix = np.arange(width)



def find_peaks(p, loc, data2, order_num, banana_num, xpix, ytop, ybottom):

    # get constants from p
    width = p['SHAPE_ABC_WIDTH']
    p_edge = p['SHAPE_PROFILE_EDGE']
    n_peaks = p['SHAPE_TRACK_NPEAKS']

    # get the dimensions
    dim0, dim1 = loc['DATA'].shape[1]

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
    # set up the x position peaks
    xpospeak = np.zeros(dim1)
    # set up the slopes
    allslopes = np.repeat([np.nan], dim1)
    # set up the slices
    allslices = np.zeros([width, 6, 10]) # TODO: Why 6? Why 10?

    # we iteratively find the peaks and set them to NaN afterward
    # for each FP peak, we loop through a range of slit angles
    # to determine its amplitude as a function of angle. We
    # assume that the angle that corresponds to the brightest
    # peak corresponds to the rotation of the slicer
    num_it = 0
    while current_max > (0.3 * maxpeak):
        # find the peak
        peak_id = np.nanargmax(profile)
        # set the current maximum
        current_max = profile[peak_id]
        # set the xpospeak
        xpospeak[num_it] = peak_id

        # a condition to avoid running off the edge of the image
        if ybottom[peak_id] <= 1:
            # we NaN the peak so that the code can move to the next peak
            # TODO: Why +/- 2?
            profile[xpix[peak_id] - 2:xpix[peak_id] + 2] = np.nan

        # box centered on the peak. This box will be "sheared"
        # until the y-collapsed profile is maximal
        ystart, yend = ybottom[peak_id], ytop[peak_id]
        xstart, xend = xpix[peak_id] - p_edge, xpix[peak_id] + p_edge
        box = data2[ystart:yend, xstart:xend]
        # calculate slopes
        slopes = get_slopes(p, allslopes, banana_num, num_it)
        # max peak value of the collapsed profile as a function of angle
        medmax = np.zeros_like(slopes)
        wbox = box.shape[1]
        # copy the box
        box1 = np.array(box)
        # take one slice of the box and normalize it
        for it in range(width):
            tmp = box[it] - np.nanmedian(box[it])
            tmp = tmp / np.nansum(tmp)
            box1[it] = tmp
        # get box 2
        box2 = np.zeros([len(slopes), box.shape[1], box.shape[0]])
        # get the x values for box2
        xx = np.arange(box.shape[1])
        # loop around the width
        for it in range(width):
            # calculate the spline fit for the original box
            spline = IUVSpline(xx, box1[it, :], ext=1, k=1)
            # loop around the slopes
            for islope, slope in enumerate(slopes):
                # work out the dx
                dx = (np.arange(width) - width//2) * slope
                # apply the y-dependent shift in x
                box2[islope, :, it] = spline(xx + dx[it])
        # loop around the slopes and calculate the medmax
        for islope, slope in enumerate(slopes):
            medmax[islope] = np.nanmax(np.nanmedian(box2[islope], axis=1))


        # as we fit a second-order polynomial to the peak pixel, we can't
        # have the peak value at the either end of the vector.
        vec = np.ones_like(medmax)
        vec[0], vec[-1] = 0.0, 0.0
        pixmax = np.argmax(medmax)
        # check that pixmax is zero # TODO: Why?
        if pixmax == 0:
            pixmax = 1

        # we fit a parabolla to the max pixel and its 2 neighbours
        with warnings.catch_warnings(record=True) as _:
            p_start, p_end = pixmax - 1, pixmax + 2

            coeffs = np.polyfit(slopes[p_start:p_end], medmax[p_start:p_end], 2)

        # the deriv=0 point of the parabola is taken to be the position
        # of the peak. This is the "best" estimate for the slope
        factor = 0.5 * coeffs[1]/coeffs[0]
        allslopes[num_it] = allslopes[num_it] - factor

        # some output for the overeager
        if (num_it % 10) == 0:
            wmsg = 'Order number={0}, p ratio={1} num={2}, slope={3}'
            wargs = [order_num, current_max/maxpeak, num_it, allslopes[num_it]]
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

        # for first "n_peaks" peaks, we keep track of the box shape at the
        #    "best" angle
        if num_it < n_peaks:
            # get a new box2
            box2 = np.zeros_like(box)
            # get dx
            dx = (np.arange(width) - width//2) * allslopes[num_it]
            # get the x pixels for box
            xx = np.arange(box.shape[1])
            # loop around the width
            for it in range(width):
                # take one slice of the box and normalize it
                tmp = box[it] - np.nanmedian(box[it])
                tmp = tmp / np.nansum(tmp)
                # calcualte the spline
                spline = IUVSpline(xx, tmp, ext=1)
                # push into the box
                box2[it] = spline(xx + dx[it])
            # set up the vector
            vec = np.zeros(width)
            vec[5:width - 5] = 1    # TODO: Why +/- 5?
            # get the max pixel
            maxpix = np.argmax(np.nanmedian(box2, axis=0) * vec)
            # if maxpix > 5 add to all_slices
            if maxpix > 5:
                # TODO: Why  "% 10" why +/- 3?
                allslices[:, :, num_it % 10] += box2[:, maxpix-3, maxpix +3]

        # we NaN the peak so that the code can move to the next peak
        # TODO: Why +/- 2?
        profile[xpix[peak_id] - 2:xpix[peak_id] + 2] = np.nan
        # add to the iterator
        num_it += 1
    # return
    return allslopes, allslices, xpospeak


def get_slopes(p, allslopes, banana_num, num_it):

    large_angle_list = p['SHAPE_LARGE_ANGLE_RANGE']
    small_angle_list = p['SHAPE_SMALL_ANGLE_RANGE']
    large_angle_num = p['SHAPE_LARGE_ANGLE_NUM']

    # if this is the first iteration, then we loop
    # though a larger set of angles
    if banana_num == 0:
        # we have >"large_angle_num" measurements... lets just
        # focus on angle values close to the median
        if num_it > large_angle_num:
            # get the median and RMS
            med = np.nanmedian(allslopes)
            rms = np.nanmedian(np.abs(allslopes - med))
            # work out the slopes
            slopes = (np.arange(-2, 3) * rms) + med
        else:
            slopes = np.arange(*large_angle_list)
    # if not, we just look for a small update to the angle
    else:
        slopes = np.arange(*small_angle_list)

    # return slopes
    return slopes


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

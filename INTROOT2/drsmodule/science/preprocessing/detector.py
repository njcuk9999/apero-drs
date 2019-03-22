#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:37
@author: ncook
Version 0.0.1
"""
import numpy as np
import os
import warnings
from scipy import ndimage

from drsmodule import constants
from drsmodule import config
from drsmodule import locale
from drsmodule.io import drs_path
from drsmodule.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'preprocessing.detector.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = config.wlog
# get param dict
ParamDict = constants.ParamDict
# Get the text types
ErrorEntry = locale.drs_text.ErrorEntry


# =============================================================================
# Define functions
# =============================================================================
def get_hot_pixels(params):
    """
    Get the positions of the hot pixels from a full flat image (engineering)

    :param params: parameter dictionary, ParamDict containing constants

    :type params: ParamDict

    :return: The hot pixesl locations in y and x
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    # get full badpixel file
    full_badpix = get_full_flat(params)
    # get shape of full badpixel file
    dim1, dim2 = full_badpix.shape

    # get the med_size
    med_size = params['PP_CORRUPT_MED_SIZE']
    # get the hot pix threshold
    hot_thres = params['PP_CORRUPT_HOT_THRES']

    # get size of dark region
    pixels_per_amp = dim2 // params['PP_TOTAL_AMP_NUM']
    dark_size = params['PP_NUM_DARK_AMP'] * pixels_per_amp

    # mask the full_badpix (do not include dark area or edges)
    full_badpix[:, dark_size:] = np.nan
    full_badpix[:med_size, :] = np.nan
    full_badpix[:, :med_size] = np.nan
    full_badpix[-med_size:, :] = np.nan
    full_badpix[:, -med_size:] = np.nan

    # median out full band structures
    with warnings.catch_warnings(record=True) as _:
        for ix in range(med_size, dark_size):
            full_badpix[:, ix] -= np.nanmedian(full_badpix[:, ix])
        for iy in range(dim1):
            full_badpix[iy, :] -= np.nanmedian(full_badpix[iy, :])

    full_badpix[~np.isfinite(full_badpix)] = 0.0

    # locate hot pixels in the full bad pix
    yhot, xhot = np.where(full_badpix > hot_thres)

    # return the hot pixel indices
    return [yhot, xhot]


def get_full_flat(params):
    """
    Get the full flat image using constants in parameter dictionary

    :param params: parameter dictionary, ParamDict containing constants

    :type params: ParamDict

    :return: numpy array (2D): the full flat image
    :rtype: np.ndarray
    """
    # get filename from parameters
    filename = params['PP_FULL_FLAT']
    # get the drs package name from parameters
    package = params['DRS_PACKAGE']
    # get the engineering data path from parameters
    relfolder = params['DATA_ENGINEERING']
    # construct the data directory
    datadir = drs_path.get_relative_folder(params, package, relfolder)
    # construct the absolute file path
    absfilename = os.path.join(datadir, filename)
    # check that filepath exists
    if not os.path.exists(absfilename):
        eargs = [filename, datadir]
        WLOG(params, 'error', ErrorEntry('00-010-00002', args=eargs))
    # read the image
    mdata = drs_fits.read(params, absfilename)
    # return the image
    return mdata


def ref_top_bottom(params, image):
    """
    Correction for the top and bottom reference pixels

    :param params: parameter dictionary, ParamDict containing constants
    :param image: numpy array (2D), the image

    :type params: ParamDict
    :type image: np.ndarray

    :return image: numpy array (2D), the corrected image
    :rtype: np.ndarray
    """
    # get the image size
    dim1, dim2 = image.shape
    # get constants from p
    tamp = params['PP_TOTAL_AMP_NUM']
    ntop = params['PP_NUM_REF_TOP']
    nbottom = params['PP_NUM_REF_BOTTOM']
    # get number of pixels in amplifier
    pix_in_amp = dim2 // tamp
    pix_in_amp_2 = pix_in_amp // 2
    # work out the weights for y pixels
    weight = np.arange(dim1)/(dim1-1)
    # pipe into array to cover odd pixels and even pixels
    weightarr = np.repeat(weight, dim2 // pix_in_amp_2)
    # reshape
    weightarr = weightarr.reshape(dim1, pix_in_amp_2)
    # loop around each amplifier
    for amp_num in range(tamp):
        # get the pixel mask for this amplifier
        pixmask = (amp_num * dim2 // tamp) + 2 * np.arange(pix_in_amp_2)
        # loop around the even and then the odd pixels
        for oddeven in range(2):
            # work out the median of the bottom pixels for this amplifier
            bottom = np.nanmedian(image[:nbottom, pixmask + oddeven])
            top = np.nanmedian(image[dim1 - ntop:, pixmask + oddeven])
            # work out contribution to subtract from top and bottom
            contrib = (top * weightarr) + (bottom * (1 - weightarr))
            # subtraction contribution from image for this amplifier
            image[:, pixmask+oddeven] -= contrib
    # return corrected image
    return image


def median_filter_dark_amp(params, image):
    """
    Use the dark amplifiers to produce a median pattern and apply this to the
    image

    :param p: parameter dictionary, ParamDict containing constants
    :param image: numpy array (2D), the image

    :type params: ParamDict
    :type image: np.ndarray

    :return image: numpy array (2D), the corrected image
    :rtype: np.ndarray
    """
    # get the image size
    dim1, dim2 = image.shape
    # get constants from p
    namp = params['PP_NUM_DARK_AMP']
    tamp = params['PP_TOTAL_AMP_NUM']
    ybinnum = params['PP_DARK_MED_BINNUM']
    # get number of pixels in amplifier
    pix_in_amp = dim2 // tamp
    # ----------------------------------------------------------------------
    # extract the dark amplifiers + one for the median filtering
    image2 = image[:, : pix_in_amp * (namp + 1)]
    # there are ribbons every two amplifiers covering two pixels
    xribbon = []
    for pix in range(pix_in_amp * 2, pix_in_amp * namp, pix_in_amp * 2):
        xribbon = np.append(xribbon, pix - 1)
        xribbon = np.append(xribbon, pix)
    # create a copy of the dark amplifiers and set the ribbons to NaN
    image2b = image2.copy()
    image2b[:, xribbon.astype(int)] = np.nan
    # ----------------------------------------------------------------------
    # produce the median-binned image
    binstep = dim1 // ybinnum
    xbinnum = (namp + 1) * pix_in_amp // binstep
    # create an array to hold binned image
    imagebin = np.zeros([ybinnum, xbinnum])
    # bin image using a median (loop around bins)
    for i in range(ybinnum):
        for j in range(xbinnum):
            # get iteration bin pposition
            x0, y0 = i * binstep, j * binstep
            x1, y1 = i * binstep + binstep, j * binstep + binstep
            # calculate value at this position
            imagebin[i, j] = np.nanmedian(image2b[x0:x1, y0:y1])
    # apply a cubic spline onto the binned image
    image3 = ndimage.zoom(imagebin, binstep, order=2)
    # ----------------------------------------------------------------------
    # subtract the low-frequency part of the image
    #    this leaves the common structures
    diffimage = image2 - image3
    # create a cube that contains the dark amplifiers
    darkamps = np.zeros([namp, dim1, pix_in_amp])
    # loop around each amplifier and add the diff image for this amplifier
    # into the common storage cube
    for amp in range(namp):
        # amplifiers are flipped for odd numbered amplifiers
        if (amp % 2) == 1:
            # work out pixel positions for this amplifier
            firstpixel = (amp * pix_in_amp) + (pix_in_amp - 1)
            lastpixel = (amp * pix_in_amp) - 1
            # add diff image (flipped as amp is odd)
            darkamps[amp, :, :] = diffimage[:, firstpixel:lastpixel:-1]
        else:
            # work out pixel positions
            firstpixel = (amp * pix_in_amp)
            lastpixel = firstpixel + pix_in_amp
            # add diff image
            darkamps[amp, :, :] = diffimage[:, firstpixel:lastpixel]
    # from the cube that contains all dark amplifiers construct the
    #    median dark amplifier
    refamp = np.nanmedian(darkamps, axis=0)
    # ----------------------------------------------------------------------
    # subtract the median dark amp from each amplifier in the image
    for amp in range(tamp):
        # if odd flip
        if (amp % 2) == 1:
            # work out pixel positions for this amplifier
            firstpixel = (amp * pix_in_amp) + (pix_in_amp - 1)
            lastpixel = (amp * pix_in_amp) - 1
            # subtract off refamp
            image[:, firstpixel:lastpixel:-1] -= refamp
        else:
            # work out pixel positions
            firstpixel = (amp * pix_in_amp)
            lastpixel = firstpixel + pix_in_amp
            # subtract off refamp
            image[:, firstpixel:lastpixel] -= refamp
    # ----------------------------------------------------------------------
    # finally return corrected image
    return image


def median_one_over_f_noise(params, image):
    """
    Use the dark amplifiers to create a map of the 1/f (residual) noise and
    apply it to the image

    :param p: parameter dictionary, ParamDict containing constants
    :param image: numpy array (2D), the image

    :type params: ParamDict
    :type image: np.ndarray

    :return image: numpy array (2D), the corrected image
    :rtype: np.ndarray
    """
    # get the image size
    dim1, dim2 = image.shape
    # get constants from p
    total_amps = params['PP_TOTAL_AMP_NUM']
    n_dark_amp = params['PP_NUM_DARK_AMP']
    # width of an amplifier
    amp_width = dim1 // total_amps
    # set up a residual low frequency array
    residual_low_f = np.zeros(dim1)
    # loop around the dark amplifiers
    for amp in range(n_dark_amp):
        # define the start and end points of this amplifier
        start = amp * amp_width
        end = amp * amp_width + amp_width
        # median this amplifier across the x axis
        residual_low_f_tmp = np.nanmedian(image[:, start:end], axis=1)
        # if this is the first amplifier just set it equal to the median
        if amp == 0:
            residual_low_f = np.array(residual_low_f_tmp)
        # else only set values if they are less than the previous amplifier(s)
        else:
            smaller = residual_low_f_tmp < residual_low_f
            residual_low_f[smaller] = residual_low_f_tmp[smaller]
    # subtract the 1/f noise from the image
    for pixel in range(dim2):
        image[:, pixel] -= residual_low_f
    # return the corrected image
    return image


def test_for_corrupt_files(params, image, hotpix):
    """
    Test for corrupted files by using the hotpix map and generate some
    quality control criteria (SNR_HOTPIX, RMS0, RMS1, RMS2, RMS3)

    :param p: parameter dictionary, ParamDict containing constants
    :param image: numpy array (2D), the image
    :param hotpix: tuple of numpy arrays, the y and x (2d numpy array)
                   positions of the hot pixels

    :type params: ParamDict
    :type image: np.ndarray
    :type hotpix: tuple[np.ndarray, np.ndarray]

    :returns: quality control values to test
    :rtype: tuple[float, float, float, float, float]
    """
    # get the med_size
    med_size = params['PP_CORRUPT_MED_SIZE']
    # get hte percentile values
    rms_percentile = params['PP_RMS_PERCENTILE']
    percent_thres = params['PP_LOWEST_RMS_PERCENTILE']
    # get shape of full badpixel file
    dim1, dim2 = image.shape
    # get size of dark region
    pixels_per_amp = dim2 // params['PP_TOTAL_AMP_NUM']
    dark_size = params['PP_NUM_DARK_AMP'] * pixels_per_amp
    # get the x and y hot pixel values
    yhot, xhot = hotpix
    # get median hot pixel box
    med_hotpix = np.zeros([2 * med_size + 1, 2 * med_size + 1])
    # loop around x
    for dx in range(-med_size, med_size + 1):
        # loop around y
        for dy in range(-med_size, med_size + 1):
            # define position in median box
            posx = dx + med_size
            posy = dy + med_size
            # get the hot pixel values at position in median box
            data_hot = np.array(image[yhot + dx, xhot + dy])
            # median the data_hot for this box position
            med_hotpix[posx, posy] = np.nanmedian(data_hot)
    # get dark ribbon
    dark_ribbon = image[:, 0:dark_size]
    # you should not have an excess in odd/even RMS of pixels
    rms2 = np.nanmedian(np.abs(dark_ribbon[0:-1, :] - dark_ribbon[1:, :]))
    rms3 = np.nanmedian(np.abs(dark_ribbon[:, 0:-1] - dark_ribbon[:, 1:]))
    med0 = np.nanmedian(dark_ribbon, axis=0)
    med1 = np.nanmedian(dark_ribbon, axis=1)
    # work out the remaining two rms values
    rms0 = np.nanmedian(np.abs(med0 - np.nanmedian(med0)))
    rms1 = np.nanmedian(np.abs(med1 - np.nanmedian(med1)))
    # get the 'rms_percentile' percentile value
    percentile_cut = np.nanpercentile(image, rms_percentile)
    # make sure the percentile does not fall below a lower level
    if percentile_cut < percent_thres:
        percentile_cut = percent_thres
    # normalise the rms by the percentile cut
    rms0 = rms0 / percentile_cut
    rms1 = rms1 / percentile_cut
    rms2 = rms2 / percentile_cut
    rms3 = rms3 / percentile_cut
    # normalise med_hotpix to it's own median
    res = med_hotpix - np.nanmedian(med_hotpix)
    # work out an rms
    rms = np.nanmedian(np.abs(res))
    # signal to noise = res / rms
    snr_hotpix = res[med_size, med_size] / rms
    # return test values
    return snr_hotpix, rms0, rms1, rms2, rms3


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================
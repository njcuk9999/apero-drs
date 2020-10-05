#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:37
@author: ncook
Version 0.0.1
"""
import numpy as np
import warnings
from scipy import ndimage

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_data
from apero.core.utils import drs_database
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'preprocessing.detector.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get param dict
ParamDict = constants.ParamDict


# =============================================================================
# Define spirou detector functions
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
    hotpix_table = drs_data.load_hotpix(params)
    # load pixel values
    yhot = np.array(hotpix_table['ypix']).astype(int)
    xhot = np.array(hotpix_table['xpix']).astype(int)
    # return the hot pixel indices
    return [yhot, xhot]


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
    weight = np.arange(dim1) / (dim1 - 1)
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
            bottom = mp.nanmedian(image[:nbottom, pixmask + oddeven])
            top = mp.nanmedian(image[dim1 - ntop:, pixmask + oddeven])
            # work out contribution to subtract from top and bottom
            contrib = (top * weightarr) + (bottom * (1 - weightarr))
            # subtraction contribution from image for this amplifier
            image[:, pixmask + oddeven] -= contrib
    # return corrected image
    return image


def median_filter_dark_amp(params, image):
    """
    Use the dark amplifiers to produce a median pattern and apply this to the
    image

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
            imagebin[i, j] = mp.nanmedian(image2b[x0:x1, y0:y1])
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
    with warnings.catch_warnings(record=True) as _:
        refamp = mp.nanmedian(darkamps, axis=0)
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
        with warnings.catch_warnings(record=True) as _:
            residual_low_f_tmp = mp.nanmedian(image[:, start:end], axis=1)
        # if this is the first amplifier just set it equal to the median
        if amp == 0:
            residual_low_f = np.array(residual_low_f_tmp)
        # else only set values if they are less than the previous amplifier(s)
        else:
            with warnings.catch_warnings(record=True) as _:
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

    :param params: parameter dictionary, ParamDict containing constants
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
    # mask pixels around the edges
    bmask = np.ones_like(yhot).astype(bool)
    bmask &= yhot > med_size
    bmask &= yhot < (dim1 - med_size)
    bmask &= xhot > med_size
    bmask &= xhot < (dim2 - med_size)
    # apply boundary mask to xhot and yhot
    xhot = xhot[bmask]
    yhot = yhot[bmask]
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
            med_hotpix[posx, posy] = mp.nanmedian(data_hot)
    # get dark ribbon
    dark_ribbon = image[:, 0:dark_size]
    # you should not have an excess in odd/even RMS of pixels
    rms2 = mp.nanmedian(np.abs(dark_ribbon[0:-1, :] - dark_ribbon[1:, :]))
    rms3 = mp.nanmedian(np.abs(dark_ribbon[:, 0:-1] - dark_ribbon[:, 1:]))
    with warnings.catch_warnings(record=True) as _:
        med0 = mp.nanmedian(dark_ribbon, axis=0)
        med1 = mp.nanmedian(dark_ribbon, axis=1)
    # work out the remaining two rms values
    rms0 = mp.nanmedian(np.abs(med0 - mp.nanmedian(med0)))
    rms1 = mp.nanmedian(np.abs(med1 - mp.nanmedian(med1)))
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
    res = med_hotpix - mp.nanmedian(med_hotpix)

    dy = med_size - (mp.nanargmax(res) // (2 * med_size + 1))
    dx = med_size - (mp.nanargmax(res) % (2 * med_size + 1))

    # work out an rms
    rms = mp.nanmedian(np.abs(res))
    # signal to noise = res / rms
    snr_hotpix = res[med_size, med_size] / rms
    # return test values
    return snr_hotpix, [rms0, rms1, rms2, rms3], dx, dy


# =============================================================================
# Define nirps detector functions
# =============================================================================
def nirps_correction(params, image, mask=None, header=None, database=None):
    # define the bin size for low level frequencies
    binsize = params['PP_MEDAMP_BINSIZE']
    # number of amplifiers in total
    namps = params['PP_TOTAL_AMP_NUM']
    # deal with not having a mask
    if mask is None:
        # get pp mask file
        mask, pfile = get_pp_mask(params, header, database=database)
    else:
        pfile = 'user'
    # get image shape
    dim1, dim2 = image.shape
    # create masked version of data
    image2 = np.array(image)
    image2[mask] = np.nan
    # low frequency correction
    # median-bin and expand back to original size
    medbin_image = mp.medbin(image2, binsize, binsize)
    lowf = ndimage.zoom(medbin_image, dim1 // binsize)
    # subtract low-frequency from masked image
    image2 = image2 - lowf
    # find the amplifier cross-talk map
    crosstalk = med_amplifiers(image, namps)
    # subtract low-frequency from masked image
    image2 = image2 - crosstalk
    # subtract both low-frequency and cross-talk from input image
    image = image - (lowf + crosstalk)
    # calculate the median of the masked image (to calculate scattered light?
    med_image2 = mp.nanmedian(image2, axis=0)
    # subtract off the masked image (scattered light correction?)
    image = image - np.tile(med_image2, dim1).reshape(dim1, dim2)
    # return corrected image
    return image, pfile


def get_pp_mask(params, header, database=None):
    _ = __NAME__ + '.get_pp_mask()'
    # get file instance
    ppmstr = drs_startup.get_file_definition('PPMSTR', params['INSTRUMENT'],
                                             kind='red')
    # get calibration key
    ppkey = ppmstr.get_dbkey()
    # ---------------------------------------------------------------------
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ---------------------------------------------------------------------
    # load filename from database
    ppfile = calibdbm.get_calib_file(ppkey, header=header, nentries=1,
                                     required=True)
    # ---------------------------------------------------------------------
    # read file
    mask = drs_fits.readfits(params, ppfile)
    # return use_file
    return mask, ppfile


def med_amplifiers(image, namps):
    """
    Perform a median image over NAMPS amplifiers with a mirror
    odd/even symmetry.
    dim1 = cross amplifier dimension
    dim2 = along amplifier dimension

    We fold the image into a namps x dim2 x (namps/dim1) cube

    :param image:
    :param namps:
    :return:
    """
    # TODO: Question: which way round is the detector right now compared to
    # TODO: Question:    compared to the amplifiers?

    # get image dimensions
    dim1, dim2 = image.shape
    # get number of pixels per amplifier
    nbpix = dim1 // namps
    # cube to contain orders in an easily managed form
    cube = np.zeros([namps, dim2, nbpix])
    # loop around each amplifier and push into cube
    for amp in range(namps):
        # TODO: Question: can/should we make this an option?
        # deal with left/right flipping (assumed to always happen)
        if (amp % 2) == 0:
            i1 = amp * nbpix
            i2 = (amp * nbpix) + nbpix
            sign = 1
        else:
            i1 = (amp * nbpix) + (nbpix - 1)
            i2 = (amp * nbpix) - 1
            sign = -1
        # add to cube (slice image)
        cube[amp] = image[:, i1:i2:sign]
    # derive median amplifier structure
    med = mp.nanmedian(cube, axis=0)
    # pad back onto the output image
    image2 = np.zeros_like(image)
    # loop around each amplifier
    for amp in range(namps):
        # deal with left/right flipping (assumed to always happen)
        if (amp % 2) == 0:
            i1 = amp * nbpix
            i2 = (amp * nbpix) + nbpix
            sign = 1
        else:
            i1 = (amp * nbpix) + (nbpix - 1)
            i2 = (amp * nbpix) - 1
            sign = -1
        # add to cube (slice image)
        image2[:, i1:i2:sign] = med
    # return the new image
    return image2


def nirps_order_mask(params, mask_image):
    """
    Calculate the mask used for removing the orders (preprocessing correction)
    for NIRPS

    :param params:
    :param mask_image:
    :return:
    """
    # set function name
    func_name = __NAME__ + '.nirps_order_mask()'
    # get nsig value
    nsig = params['PPM_MASK_NSIG']
    # normalise by the median
    image = mask_image - mp.nanmedian(mask_image)
    # calculate the sigma array (distance away from median)
    sig_image = mp.nanmedian(np.abs(image))
    # find pixels that are more than nsig absolute deviations from the image
    # median
    with warnings.catch_warnings(record=True):
        mask = image > nsig * sig_image
    # correct the image (as in preprocessing)
    image, _ = nirps_correction(params, image, mask)
    # generate a better estimate of the mask (after correction)
    with warnings.catch_warnings(record=True):
        mask = image > nsig * sig_image
    # set properties
    props = ParamDict()
    props['PPM_MASK_NSIG'] = nsig
    props.set_source('PPM_MASK_NSIG', func_name)
    # return mask
    return mask, props


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

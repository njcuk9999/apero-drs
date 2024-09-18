#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO background functionality

Created on 2019-05-13 at 12:40

@author: cook
"""
import warnings
from typing import List, Optional

import numpy as np
from scipy.ndimage import map_coordinates as mapc
from scipy.ndimage import zoom
from scipy.signal import convolve2d

from apero.base import base
from apero.core.constants import param_functions
from apero.core import lang
from apero.core import math as mp
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.background.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
def create_background_map(params: ParamDict, image: np.ndarray,
                          badpixmask: np.ndarray,
                          bkgr_boxsize: Optional[int] = None,
                          bkgr_percentage: Optional[float] = None,
                          bkgr_mask_conv_size: Optional[int] = None,
                          bkgr_n_bad: Optional[int] = None) -> np.ndarray:
    """
    Create background map mask

    :param params: ParamDict, parameter dictionary of constants
    :param image: numpy (2D) array, the image to calculate the background from
    :param badpixmask: numpy (2D) array, a map of bad pixels
    :param bkgr_boxsize: int or None, optional, Width of the box to produce the
                         background mask, if provided overrides
                         params['BKGR_BOXSIZE']
    :param bkgr_percentage: float or None, optional, the background percentile
                            to compute minimum value (%), if provided overrides
                            params['BKGR_PERCENTAGE']
    :param bkgr_mask_conv_size: int or None, optional, size in pixels of to
                                convolve tophat for the background mask, if
                                provided overrides
                                params['BKGR_MASK_CONVOLVE_SIZE']
    :param bkgr_n_bad: int or None, optional, If a pixel has this or more
                       "dark" neighbours, we consider it dark regardless of
                       its initial value, overrides
                       params['BKGR_N_BAD_NEIGHBOURS']

    :return: numpy (2D) array, the background map (same shape as input image)
    """
    func_name = __NAME__ + '.create_background_map()'
    # get constants
    width = pcheck(params, 'BKGR_BOXSIZE', func=func_name,
                   override=bkgr_boxsize)
    percent = pcheck(params, 'BKGR_PERCENTAGE', func=func_name,
                     override=bkgr_percentage)
    csize = pcheck(params, 'BKGR_MASK_CONVOLVE_SIZE', func=func_name,
                   override=bkgr_mask_conv_size)
    nbad = pcheck(params, 'BKGR_N_BAD_NEIGHBOURS', func=func_name,
                  override=bkgr_n_bad)
    # set image bad pixels to NaN
    image0 = np.array(image)
    badmask = np.array(badpixmask, dtype=bool)
    image0[badmask] = np.nan
    # image that will contain the background estimate
    backest = np.zeros_like(image0)
    # we slice the image in ribbons of width "width".
    # The slicing is done in the cross-dispersion direction, so we
    # can simply take a median along the "fast" dispersion to find the
    # order profile. We pick width to be small enough for the orders not
    # to show a significant curvature within w pixels

    # width in fast dispersion axis - smaller so there is no blur due to the
    # curvature of orders
    width2 = width // 4
    # loop around this regions (per region)
    for x_it in range(0, image0.shape[1], width2):
        # ribbon to find the order profile
        ribbon = mp.nanmedian(image0[:, x_it:x_it + width2], axis=1)
        # loop around the columns (per pixel)
        for y_it in range(image0.shape[0]):
            # we perform a running Nth percentile filter along the
            # order profile. The box of the filter is w. Note that it could
            # differ in princile from w, its just the same for the sake of
            # simplicity.
            ystart = y_it - width // 2
            yend = y_it + width // 2
            if ystart < 0:
                ystart = 0
            if yend > image0.shape[0] - 1:
                yend = image0.shape[0] - 1
            # background estimate
            backest_pix = mp.nanpercentile(ribbon[ystart:yend], percent)
            backest[y_it, x_it: x_it + width2] = backest_pix
    # the mask is the area that is below then Nth percentile threshold
    with warnings.catch_warnings(record=True) as _:
        backmask = np.array(image0 < backest, dtype=float)
    # we take advantage of the order geometry and for that the "dark"
    # region of the array be continuous in the "fast" dispersion axis
    nribbon = convolve2d(backmask, np.ones([1, csize]), mode='same')
    # we remove from the binary mask all isolated (within 1x7 ribbon)
    # dark pixels
    backmask[nribbon == 1] = 0
    # If a pixel has 3 or more "dark" neighbours, we consider it dark
    # regardless of its initial value
    backmask[nribbon >= nbad] = 1
    # return the background mask
    return backmask


def correct_local_background(params: ParamDict, image: np.ndarray,
                             bkgr_ker_wx: Optional[int] = None,
                             bkgr_ker_wy: Optional[int] = None,
                             bkgr_ker_sig: Optional[int] = None) -> np.ndarray:
    """
    determine the scattering from an imput image. To speed up the code,
    do the following steps rather than a simple convolution with the
    scattering kernel.

    :param params: ParamDict, parameter dictionary of constants
    :param image: np.array, image to correct local background
    :param bkgr_ker_wx: int or None, optional, Background kernel width in
                        x [pixels], overrides params['BKGR_KER_WX']
    :param bkgr_ker_wy: int or None, optional, Background kernel width in
                        y [pixels], overrides params['BKGR_KER_WX']
    :param bkgr_ker_sig: int or None, optional, convolution kernel sigma range
                        overrides params['BKGR_KER_SIG']

    Logical (slow) steps -->

    -- create a kernel of a 2D gaussian with a width in X and Y defined
    from the BKGR_KER_WX and BKGR_KER_WY keywords
    this kernel is typically much larger on one axis than on the other
    (typically 1 vs 9 pixels 1/e width)
    -- convolve the image by the kernel

    Faster (but less intuitive) steps that we do -->

    - Downsize (simple binning) the image to dimensions for which the
    convolution kernel is (barely) Nyquist. These dimensions are selected
    to be the smallest integer dimensions where there are integer pixel
    bins while remaining above Nyquist. If we have a 9 pixel 1/e width,
    then we bin by a factor of 8 an 4088 image to a 511 pixel size, and
    the 1/e width in that new reference frame becomes 9/8 ~ 1.1
    - Convolve the binned-down image with the kernel in the down-sized
    reference frame. Here, a 1x9 1/e 2-D gaussian becomes a 1x1.1 1/e
    gaussian. The kernel is smaller and the input image is also similarly
    smaller, so there is a N^2 gain.
    - Upscale the convolved image to the input dimensions

    :returns: np.ndarray, the local background (scattered_light), same size
              as input image
    """
    func_name = __NAME__ + '.correct_local_background()'
    # get constants from parameter dictionary
    wx_ker = pcheck(params, 'BKGR_KER_WX', func=func_name, override=bkgr_ker_wx)
    wy_ker = pcheck(params, 'BKGR_KER_WY', func=func_name, override=bkgr_ker_wy)
    sig_ker = pcheck(params, 'BKGR_KER_SIG', func=func_name,
                     override=bkgr_ker_sig)
    # log process
    WLOG(params, '', textentry('40-012-00010'))
    # Remove NaNs from image
    image1 = mp.nanpad(image)
    # size if input image
    sz = image1.shape
    # size of the smaller image. It is an integer divider of the input image
    # 4088 on an axis and wN_ker = 9 would lead to an 8x scale-down (8*511)
    sz_small = [sz[0] // mp.largest_divisor_below(sz[0], wy_ker),
                sz[1] // mp.largest_divisor_below(sz[1], wx_ker)]

    # downsizing image prior to convolution
    # bins an image from its shape down to a smaller shape, say 4096x4096 to
    # 512x512. Before/after axis ratio must be integers in all dims.
    #
    shape = (sz_small[0], image1.shape[0] // sz_small[0],
             sz_small[1], image1.shape[1] // sz_small[1])
    image2 = np.array(image1).reshape(shape).mean(-1).mean(1)

    # downsizing ratio to properly scale convolution kernel
    downsize_ratio = np.array(sz) / np.array(sz_small)

    # convolution kernel in the downsized domain
    ker_sigx = int((wx_ker * sig_ker * 2) / downsize_ratio[1] + 1)
    ker_sigy = int((wy_ker * sig_ker * 2) / downsize_ratio[0] + 1)
    kery, kerx = np.indices([ker_sigy, ker_sigx], dtype=float)
    # this normalises kernal x and y between +1 and -1
    kery = kery - np.mean(kery)
    kerx = kerx - np.mean(kerx)
    # calculate 2D gaussian kernel
    ker = np.exp(-0.5 * ((kerx / wx_ker * downsize_ratio[1]) ** 2
                         + (kery / wy_ker * downsize_ratio[0]) ** 2))

    # we normalize the integral of the kernel to 1 so that the AMP factor
    #    corresponds to the fraction of scattered light and therefore has a
    #    physical meaning.
    ker = ker / np.sum(ker)

    # upscale image back to original dimensions
    image3 = convolve2d(image2, ker, mode='same')
    image4 = np.array(image1.shape) / np.array(image2.shape)
    scattered_light = zoom(image3, image4, output=None, order=1,
                           mode='constant', cval=0.0)
    # returned the scattered light
    return scattered_light


def correction(recipe: DrsRecipe, params: ParamDict, infile: DrsFitsFile,
               image: np.ndarray, bkgrdfile: str, return_map: bool = False,
               bkgr_no_sub: Optional[bool] = None,
               bkgr_boxsize: Optional[int] = None,
               bkgr_ker_amp: Optional[int] = None) -> np.ndarray:
    """
    Background correct an image

    :param recipe: DrsRecipe, used for producing the DEBUG output
    :param params: ParamDict, parameter dictionary of constants
    :param infile: DrsFitsFile, input file
    :param image: np.ndarray, the input image
    :param bkgrdfile: str, the background calibration absolute filename
    :param return_map: bool, if True, return the full background image
    :param bkgr_no_sub: bool or None, optional, whether to do the background
                        measurement (True or False), overrides
                        params['BKGR_NO_SUBTRACTION']
    :param bkgr_boxsize: int, optional, width of the box to produce the
                         background mask, overrides params['BKGR_BOXSIZE']
    :param bkgr_ker_amp: int, optional, kernel amplitude , overrides
                         params['BKGR_KER_AMP']

    :return: numpy array, either the corrected image, or the full background
             map (if return_map is True)
    """
    func_name = __NAME__ + '.correction()'
    # get constants from params/kwargs
    no_sub = pcheck(params, 'BKGR_NO_SUBTRACTION', 'no_sub', func=func_name,
                    override=bkgr_no_sub)
    width = pcheck(params, 'BKGR_BOXSIZE', 'width', func=func_name,
                   override=bkgr_boxsize)
    amp_ker = pcheck(params, 'BKGR_KER_AMP', 'amp_ker', func=func_name,
                     override=bkgr_ker_amp)
    # deal with no correction needed
    if no_sub:
        background = np.zeros_like(image)
        # if return map just return the bad pixel map
        if return_map:
            return background
        else:
            return np.array(image)
    else:
        # ------------------------------------------------------------------
        if amp_ker > 0:
            # measure local background
            scattered_light = correct_local_background(params, image)
            # we extract a median order profile for the center of the image
            local_background_correction = scattered_light / amp_ker
            # correct the image for local background
            image1 = image - local_background_correction
        else:
            image1 = np.array(image)
            local_background_correction = np.zeros_like(image)
        # ------------------------------------------------------------------
        # log process
        WLOG(params, '', textentry('40-012-00009', args=[bkgrdfile]))
        # ------------------------------------------------------------------
        # get bad pixel file
        bkgrdimage = drs_fits.readfits(params, bkgrdfile)
        # create mask from badpixmask
        bmap = np.array(bkgrdimage, dtype=bool)
        # copy image
        image2 = np.array(image1)
        # set to NAN all "illuminated" (non-background) pixels
        image2[~bmap] = np.nan
        # ------------------------------------------------------------------
        # create the box centers
        #     we construct a binned-down version of the full image with the
        #     estimate of the background for each x+y "center". This image
        #     will be up-scaled to the size of the full science image and
        #     subtracted
        xc = np.arange(0, image2.shape[0])
        yc = np.arange(width // 4, image2.shape[1], width // 4)

        imageshape = image2.shape

        background_image = np.zeros((len(xc), len(yc)))
        background_image_offset = np.zeros((len(xc), len(yc)))
        background_image_full = np.zeros_like(image2)
        gridshape = background_image.shape

        # get fractional positions of the full image
        indices = np.indices(imageshape)
        fypix = indices[0] / imageshape[0]
        fxpix = indices[1] / imageshape[1]
        # scalge fraction positions to size of background image
        sypix = (gridshape[0] - 1) * fypix
        sxpix = (gridshape[1] - 1) * fxpix
        # coords for mapping
        coords = np.array([sypix, sxpix])

        for ite in range(3):
            image2b = np.array(image2 - background_image_full)
            #     # loop around all boxes with centers xc and yc
            #     # and find pixels within a given widths
            #     # around these centers in the full image
            for ii, icol in enumerate(yc):
                i0 = np.max([icol - width // 2, 0])
                i1 = np.min([icol + width // 2, image2.shape[1]])
                with warnings.catch_warnings(record=True) as _:
                    medcol = np.nanmedian(image2b[:, i0:i1], axis=1)
                background_image_offset[:, ii] = mp.lowpassfilter(medcol, width)

            background_image_full += mapc(background_image_offset, coords,
                                          order=2, cval=np.nan, output=float,
                                          mode='constant')
            background_image += background_image_offset
            # print(np.nanstd(background_image_offset),np.nanstd(background_image))

        # ------------------------------------------------------------------
        # create the box centers
        #     we construct a binned-down version of the full image with the
        #     estimate of the background for each x+y "center". This image
        #     will be up-scaled to the size of the full science image and
        #     subtracted
        # # x and y centers for each background calculation
        # xc = np.arange(width, image2.shape[0], width)
        # yc = np.arange(width, image2.shape[1], width)
        # # full background map
        # background_image_full = np.zeros_like(image2)
        # # background map (binned-down for now)
        # background_image = np.zeros((len(xc), len(yc)))
        # # iterate round the background image
        # for biteration in range(5):
        #     image3 = np.array(image2) - background_image_full
        #     # loop around all boxes with centers xc and yc
        #     # and find pixels within a given widths
        #     # around these centers in the full image
        #     for i_it in range(len(xc)):
        #         for j_it in range(len(yc)):
        #             xci, yci = xc[i_it], yc[j_it]
        #             # get the pixels for this box
        #             subframe = image3[xci - width:xci + width,
        #                               yci - width:yci + width]
        #             subframe = subframe.ravel()
        #             # get the (2*size)th minimum pixel
        #             with warnings.catch_warnings(record=True) as _:
        #                 # do not use the nanpercentile, just a median
        #                 # as we masked non-background pixels with NaNs
        #                 value = mp.nanmedian(subframe)
        #             # if we have value use it in the background map
        #             if np.isfinite(value):
        #                 background_image[i_it, j_it] = value
        #             # otherwise background is zero
        #             else:
        #                 background_image[i_it, j_it] = 0.0
        #     # ------------------------------------------------------------------
        #     # define a mapping grid from size of background_image
        #     #     (image1[0]/width) by (image1[1]/width)
        #     # get shapes
        #     gridshape = background_image.shape
        #     imageshape = image3.shape
        #     # get fractional positions of the full image
        #     indices = np.indices(imageshape)
        #     fypix = indices[0] / imageshape[0]
        #     fxpix = indices[1] / imageshape[1]
        #     # scalge fraction positions to size of background image
        #     sypix = (gridshape[0] - 1) * fypix
        #     sxpix = (gridshape[1] - 1) * fxpix
        #     # coords for mapping
        #     coords = np.array([sypix, sxpix])
        #
        #     delta_background_full = mapc(background_image, coords,
        #                                  order=2, cval=np.nan, output=float,
        #                                  mode='constant')
        #
        #     brms = np.nanstd(delta_background_full)
        #     msg = 'Background Iteration {0}: delta background rms={1:.3f}'
        #     WLOG(params, '', msg.format(biteration, brms))
        #     # expand image onto the grid that matches the size of the input
        #    # image
        #    background_image_full += mapc(background_image, coords,
        #                                  order=2, cval=np.nan, output=float,
        #                                  mode='constant')
        # ------------------------------------------------------------------
        # correct image
        corrected_image = image - background_image_full
        # ------------------------------------------------------------------
        # produce debug file
        dimages = [corrected_image, image, image1, image2,
                   local_background_correction, background_image_full,
                   background_image]
        # save debug file
        if params['DEBUG_BACKGROUND_FILE']:
            debug_file(recipe, params, infile, dimages)
        # ------------------------------------------------------------------
        # if return map just return the bad pixel map
        if return_map:
            return background_image_full
        else:
            return corrected_image


def debug_file(recipe: DrsRecipe, params: ParamDict, infile: DrsFitsFile,
               dlist: List[np.ndarray]):
    """
    Produce the background DEBUG file

    :param recipe: DrsRecipe, the recipe that called this function
    :param params: ParamDict, parameter dictionary of constants
    :param infile: DrsFitsFile, the input file class
    :param dlist: list of numpy array, the images for each extension:
                  1. corrected image
                  2. original image
                  3. locally corrected image
                  4. locally corrected NaN filled image
                  5. Local Background image
                  6. Global Background image
                  7. Global binned background image

    :return: None, writes debug file to disk
    """
    # debug output
    debug_back = recipe.outputs['DEBUG_BACK'].newcopy(params=params)
    # construct the filename from file instance
    debug_back.construct_filename(infile=infile, check=False)
    # copy keys from input file
    debug_back.copy_original_keys(infile)
    # add core values (that should be in all headers)
    debug_back.add_core_hkeys(params)
    # add extention info
    kws1 = ['EXTDESC1', 'CORRECTED', 'Corrected image']
    kws2 = ['EXTDESC2', 'ORIGINAL', 'Original image']
    kws3 = ['EXTDESC3', 'LOCAL_CORR', 'Locally corrected image']
    kws4 = ['EXTDESC4', 'LC_NAN_FILLED', 'Locally corrected NaN filled image']
    kws5 = ['EXTDESC5', 'LC_BKGRD', 'Local Background image']
    kws6 = ['EXTDESC6', 'GLOB_BKGRD', 'Global Background image']
    kws7 = ['EXTDESC7', 'GLOB_BINNED', 'Global binned background image']
    # add to hdict
    debug_back.add_hkey(key=kws1)
    debug_back.add_hkey(key=kws2)
    debug_back.add_hkey(key=kws3)
    debug_back.add_hkey(key=kws4)
    debug_back.add_hkey(key=kws5)
    debug_back.add_hkey(key=kws6)
    debug_back.add_hkey(key=kws7)
    # add primage data to debug_back file
    debug_back.data = dlist[0]
    # print progress: saving file
    WLOG(params, '', textentry('40-013-00025', args=debug_back.filename))
    # define name of extensions
    name_list = ['CORRECTED', 'ORIGINAL', 'LOCAL_CORR',
                 'LC_NAN_FILLED', 'LC_BKGRD', 'GLOB_BKGRD',
                 'GLOB_BINNED']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        dlist += [params.snapshot_table(recipe, drsfitsfile=debug_back)]
        name_list += ['PARAM_TABLE']
    # write multiple to file
    debug_back.write_multi(block_kind=recipe.out_block_str, name_list=name_list,
                           data_list=dlist[1:], runstring=recipe.runstring)


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

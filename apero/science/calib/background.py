#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-13 at 12:40

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings
from scipy.signal import convolve2d
from scipy.ndimage import map_coordinates as mapc
from scipy.ndimage import zoom

from apero import core
from apero.core import constants
from apero import locale
from apero.core import math as mp
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_database
from apero.core.instruments.default import file_definitions
from apero.io import drs_fits


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.background.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def create_background_map(params, image, badpixmask, **kwargs):
    func_name = __NAME__ + '.create_background_map()'
    # get constants
    width = pcheck(params, 'BKGR_BOXSIZE', 'width', kwargs, func_name)
    percent = pcheck(params, 'BKGR_PERCENTAGE', 'percent', kwargs, func_name)
    csize = pcheck(params, 'BKGR_MASK_CONVOLVE_SIZE', 'csize', kwargs,
                   func_name)
    nbad = pcheck(params, 'BKGR_N_BAD_NEIGHBOURS', 'nbad', kwargs, func_name)
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
    for x_it in range(0, image0.shape[1], width):
        # ribbon to find the order profile
        ribbon = mp.nanmedian(image0[:, x_it:x_it + width], axis=1)

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
            backest_pix = np.nanpercentile(ribbon[ystart:yend], percent)
            backest[y_it, x_it: x_it + width] = backest_pix
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


def correct_local_background(params, image, **kwargs):
    """
    determine the scattering from an imput image. To speed up the code,
    do the following steps rather than a simple convolution with the
    scattering kernel.

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
    """
    func_name = __NAME__ + '.correct_local_background()'
    # get constants from parameter dictionary
    wx_ker = pcheck(params, 'BKGR_KER_WX', 'wx_ker', kwargs, func_name)
    wy_ker = pcheck(params, 'BKGR_KER_WY', 'wy_ker', kwargs, func_name)
    sig_ker = pcheck(params, 'BKGR_KER_SIG', 'sig_ker', kwargs, func_name)
    # log process
    WLOG(params, '', TextEntry('40-012-00010'))

    # Remove NaNs from image
    image1 = mp.nanpad(image)

    # size if input image
    sz = image1.shape
    # size of the smaller image. It is an integer divider of the input image
    # 4088 on an axis and wN_ker = 9 would lead to an 8x scale-down (8*511)
    sz_small = [sz[0] // largest_divisor_below(sz[0], wy_ker),
                sz[1] // largest_divisor_below(sz[1], wx_ker)]

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


def largest_divisor_below(n1, n2):
    """
    finds the largest divisor of a large number below a certain limit
    for 4088 and 9, we would get 8 (511*8 = 4088)
    Useful to downsize images.

    :param n1:
    :param n2:
    :return:
    """
    for i in range(n2, 0, -1):
        if n1 % i == 0:
            return i
    # if there is a problem return NaN
    return np.nan


def correction(recipe, params, infile, image, header, return_map=False,
               **kwargs):
    func_name = __NAME__ + '.correction()'
    # get constants from params/kwargs
    no_sub = pcheck(params, 'BKGR_NO_SUBTRACTION', 'no_sub', kwargs, func_name)
    width = pcheck(params, 'BKGR_BOXSIZE', 'width', kwargs, func_name)
    amp_ker = pcheck(params, 'BKGR_KER_AMP', 'amp_ker', kwargs, func_name)
    # check kwargs for filename
    filename = kwargs.get('filename', None)
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')
    # get filename col
    filecol = cdb.file_col
    # deal with no correction needed
    if no_sub:
        background = np.zeros_like(image)
        # get background file
        params['BADPFILE'] = 'None'
        params.set_source('BADPFILE', func_name)
        # if return map just return the bad pixel map
        if return_map:
            return params, background
        else:
            return params, np.array(image)
    else:
        # ------------------------------------------------------------------
        # measure local background
        scattered_light = correct_local_background(params, image)
        # we extract a median order profile for the center of the image
        local_background_correction = scattered_light / amp_ker
        # correct the image for local background
        image1 = image - local_background_correction
        # get file instance
        backinst = core.get_file_definition('BKGRD_MAP', params['INSTRUMENT'],
                                            kind='red')
        # get calibration key
        backkey = backinst.get_dbkey(func=func_name)
        # --------------------------------------------------------------------
        # get filename
        if filename is not None:
            bkgrdfile = filename
        else:
            # get background entries
            bkgrdentries = drs_database.get_key_from_db(params, backkey, cdb,
                                                        header, n_ent=1)
            # get background map filename
            bkgrdfilename = bkgrdentries[filecol][0]
            bkgrdfile = os.path.join(params['DRS_CALIB_DB'], bkgrdfilename)
        # ------------------------------------------------------------------
        # log process
        WLOG(params, '', TextEntry('40-012-00009', args=[bkgrdfile]))
        # ------------------------------------------------------------------
        # get bad pixel file
        bkgrdimage = drs_fits.read(params, bkgrdfile)
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
        # x and y centers for each background calculation
        xc = np.arange(width, image2.shape[0], width)
        yc = np.arange(width, image2.shape[1], width)
        # background map (binned-down for now)
        background_image = np.zeros((len(xc), len(yc)))
        # loop around all boxes with centers xc and yc
        # and find pixels within a given widths
        # around these centers in the full image
        for i_it in range(len(xc)):
            for j_it in range(len(yc)):
                xci, yci = xc[i_it], yc[j_it]
                # get the pixels for this box
                subframe = image2[xci - width:xci + width,
                                  yci - width:yci + width]
                subframe = subframe.ravel()
                # get the (2*size)th minimum pixel
                with warnings.catch_warnings(record=True) as _:
                    # do not use the nanpercentile, just a median
                    # as we masked non-background pixels with NaNs
                    value = mp.nanmedian(subframe)

                if np.isfinite(value):
                    background_image[i_it, j_it] = value
                else:
                    background_image[i_it, j_it] = 0.0
        # ------------------------------------------------------------------
        # define a mapping grid from size of background_image
        #     (image1[0]/width) by (image1[1]/width)
        # get shapes
        gridshape = background_image.shape
        imageshape = image2.shape
        # get fractional positions of the full image
        indices = np.indices(imageshape)
        fypix = indices[0] / imageshape[0]
        fxpix = indices[1] / imageshape[1]
        # scalge fraction positions to size of background image
        sypix = (gridshape[0] - 1) * fypix
        sxpix = (gridshape[1] - 1) * fxpix
        # coords for mapping
        coords = np.array([sypix, sxpix])
        # expand image onto the grid that matches the size of the input image
        background_image_full = mapc(background_image, coords,
                                     order=2, cval=np.nan, output=float,
                                     mode='constant')
        # ------------------------------------------------------------------
        # correct image
        corrected_image = image - background_image_full
        # ------------------------------------------------------------------
        # produce debug file
        dimages = [corrected_image, image, image1, image2,
                   local_background_correction, background_image_full,
                   background_image]
        # save debug file
        debug_file(recipe, params, infile, dimages)
        # ------------------------------------------------------------------
        # if return map just return the bad pixel map
        if return_map:
            return bkgrdfile, background_image_full
        else:
            return bkgrdfile, corrected_image


def debug_file(recipe, params, infile, dlist):
    # debug output
    debug_back = recipe.outputs['DEBUG_BACK'].newcopy(recipe=recipe)
    # construct the filename from file instance
    debug_back.construct_filename(params, infile=infile, check=False)
    # copy keys from input file
    debug_back.copy_original_keys(infile)
    # add version
    debug_back.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add process id
    debug_back.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    debug_back.add_hkey('KW_OUTPUT', value=debug_back.name)
    # add extention info
    kws1 = ['EXTDESC1', 'Corrected', 'Extension 1 description']
    kws2 = ['EXTDESC2', 'Original', 'Extension 2 description']
    kws3 = ['EXTDESC3', 'Locally corrected', 'Extension 3 description']
    kws4 = ['EXTDESC4', 'LC NaN filled', 'Extension 4 description']
    kws5 = ['EXTDESC5', 'Local Background', 'Extension 5 description']
    kws6 = ['EXTDESC6', 'Global Background', 'Extension 6 description']
    kws7 = ['EXTDESC7', 'Global binned background', 'Extension 7 description']
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
    WLOG(params, '', TextEntry('40-013-00025', args=debug_back.filename))
    # write multiple to file
    debug_back.write_multi(data_list=dlist[1:])


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

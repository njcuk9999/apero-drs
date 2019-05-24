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

from terrapipe import config
from terrapipe import constants
from terrapipe import locale
from terrapipe.config import drs_log
from terrapipe.config import drs_file
from terrapipe.config import math
from terrapipe.config.core import drs_database
from terrapipe.config.core.default import file_definitions
from terrapipe.io import drs_fits


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.background.py'
__INSTRUMENT__ = None
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
pcheck = config.pcheck
# Define output files
DEBUG_BACK = file_definitions.debug_back


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
        ribbon = np.nanmedian(image0[:, x_it:x_it + width], axis=1)

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
    func_name = __NAME__ + '.correct_local_background()'
    # get constants from parameter dictionary
    wx_ker = pcheck(params, 'BKGR_KER_WX', 'wx_ker', kwargs, func_name)
    wy_ker = pcheck(params, 'BKGR_KER_WY', 'wy_ker', kwargs, func_name)
    sig_ker = pcheck(params, 'BKGR_KER_SIG', 'sig_ker', kwargs, func_name)
    # log process
    WLOG(params, '', TextEntry('40-012-00010'))
    # construct a convolution kernel. We go from -"sig_ker" to +"sig_ker" sigma
    #   in each direction. Its important no to make the kernel too big
    #   as this slows-down the 2D convolution. Do NOT make it a -10 to
    #   +10 sigma gaussian!
    ker_sigx = int((wx_ker * sig_ker * 2) + 1)
    ker_sigy = int((wy_ker * sig_ker * 2) + 1)
    kery, kerx = np.indices([ker_sigy, ker_sigx], dtype=float)
    # this normalises kernal x and y between +1 and -1
    kery = kery - np.mean(kery)
    kerx = kerx - np.mean(kerx)
    # calculate 2D gaussian kernel
    ker = np.exp(-0.5 * ((kerx / wx_ker)**2 + (kery / wy_ker)**2))
    # we normalize the integral of the kernel to 1 so that the AMP factor
    #    corresponds to the fraction of scattered light and therefore has a
    #    physical meaning.
    ker = ker / np.sum(ker)
    # we need to remove NaNs from image
    WLOG(params, '', TextEntry('40-012-00011'))
    image1 = math.nanpad(image)
    # we determine the scattered light image by convolving our image by
    #    the kernel
    WLOG(params, '', TextEntry('40-012-00012'))
    scattered_light = convolve2d(image1, ker, mode='same')
    # returned the scattered light
    return scattered_light


def correction(recipe, params, infile, image, header, return_map=False,
               **kwargs):
    func_name = __NAME__ + '.correction()'
    # get constants from params/kwargs
    no_sub = pcheck(params, 'BKGR_NO_SUBTRACTION', 'no_sub', kwargs, func_name)
    width = pcheck(params, 'BKGR_BOXSIZE', 'width', kwargs, func_name)
    amp_ker = pcheck(params, 'BKGR_KER_AMP', 'amp_ker', kwargs, func_name)
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
        # --------------------------------------------------------------------

        # TODO: check whether we have bad pixel file set from input arguments

        # get background entries
        bkgrdentries = drs_database.get_key_from_db(params, 'BKGRDMAP', cdb,
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
                    value = np.nanmedian(subframe)

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
        # get background file
        params['BADPFILE'] = bkgrdfilename
        params.set_source('BADPFILE', func_name)
        # if return map just return the bad pixel map
        if return_map:
            return params, background_image_full
        else:
            return params, corrected_image


def debug_file(recipe, params, infile, dlist):
    # debug output
    debug_back = DEBUG_BACK.newcopy(recipe=recipe)
    # construct the filename from file instance
    debug_back.construct_filename(params, infile=infile)
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
    # construct header list
    hlist = [drs_fits.Header.copy(debug_back.hdict)] * (len(dlist) - 1)
    # construct data type list
    datatypelist = ['image'] * (len(dlist) - 1)
    dtypelist = [None] * (len(dlist) - 1)
    # write multiple to file
    debug_back.write_multi(dlist[1:], hlist, datatypelist, dtypelist)


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

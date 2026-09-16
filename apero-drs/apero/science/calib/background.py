#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO background functionality

Created on 2019-05-13 at 12:40

@author: cook
"""
from typing import List, Optional, Union

import numpy as np

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore import drs_lang
from aperocore import math as mp
from aperocore.science.calib import background_core as background_mod
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.io import drs_fits
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.background.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the text types
textentry = drs_lang.textentry
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
                         params['CAL.BCORR.BKGR_BOXSIZE']
    :param bkgr_percentage: float or None, optional, the background percentile
                            to compute minimum value (%), if provided overrides
                            params['CAL.BCORR.BKGR_PERCENTAGE']
    :param bkgr_mask_conv_size: int or None, optional, size in pixels of to
                                convolve tophat for the background mask, if
                                provided overrides
                                params['CAL.BCORR.BKGR_MASK_CSIZE']
    :param bkgr_n_bad: int or None, optional, If a pixel has this or more
                       "dark" neighbours, we consider it dark regardless of
                       its initial value, overrides
                       params['CAL.BCORR.NBAD_NEIGHBOURS']

    :return: numpy (2D) array, the background map (same shape as input image)
    """
    func_name = __NAME__ + '.create_background_map()'
    # get constants
    width = pcheck(params, 'CAL.BCORR.BKGR_BOXSIZE', func=func_name,
                   override=bkgr_boxsize)
    percent = pcheck(params, 'CAL.BCORR.BKGR_PERCENTAGE', func=func_name,
                     override=bkgr_percentage)
    csize = pcheck(params, 'CAL.BCORR.BKGR_MASK_CSIZE', func=func_name,
                   override=bkgr_mask_conv_size)
    nbad = pcheck(params, 'CAL.BCORR.NBAD_NEIGHBOURS', func=func_name,
                  override=bkgr_n_bad)
    # delegate numerical work to the profile-independent core module
    args = [image, badpixmask, width, percent, csize, nbad]
    return background_mod.create_background_map(*args)


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
                        x [pixels], overrides params['CAL.BCORR.KER_WX']
    :param bkgr_ker_wy: int or None, optional, Background kernel width in
                        y [pixels], overrides params['CAL.BCORR.KER_WX']
    :param bkgr_ker_sig: int or None, optional, convolution kernel sigma range
                        overrides params['CAL.BCORR.KER_SIG']

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
    wx_ker = pcheck(params, 'CAL.BCORR.KER_WX', func=func_name, override=bkgr_ker_wx)
    wy_ker = pcheck(params, 'CAL.BCORR.KER_WY', func=func_name, override=bkgr_ker_wy)
    sig_ker = pcheck(params, 'CAL.BCORR.KER_SIG', func=func_name,
                     override=bkgr_ker_sig)
    # log process
    WLOG(params, '', textentry('40-012-00010'))
    # delegate numerical work to the profile-independent core module
    args = [image, wx_ker, wy_ker, sig_ker]
    return background_mod.correct_local_background(*args)


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
                         background mask, overrides params['CAL.BCORR.BKGR_BOXSIZE']
    :param bkgr_ker_amp: int, optional, kernel amplitude , overrides
                         params['CAL.BCORR.KER_AMP']

    :return: numpy array, either the corrected image, or the full background
             map (if return_map is True)
    """
    func_name = __NAME__ + '.correction()'
    # get constants from params/kwargs
    no_sub = pcheck(params, 'CAL.BCORR.NO_CORR', 'no_sub', func=func_name,
                    override=bkgr_no_sub)
    width = pcheck(params, 'CAL.BCORR.BKGR_BOXSIZE', 'width', func=func_name,
                   override=bkgr_boxsize)
    amp_ker = pcheck(params, 'CAL.BCORR.KER_AMP', 'amp_ker', func=func_name,
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
        # delegate numerical work to the profile-independent core module
        args = [image2, width]
        kwargs = dict(niter=3)
        outs = background_mod.iterative_box_background(*args, **kwargs)
        background_image_full, background_image = outs

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
        if params['DEBUG.OUTFILE.BCKGRD_FILE']:
            debug_file(recipe, params, infile, dimages)
        # ------------------------------------------------------------------
        # if return map just return the bad pixel map
        if return_map:
            return background_image_full
        else:
            return corrected_image


def correction_lower_envelope(recipe: DrsRecipe, params: ParamDict,
                              infile: DrsFitsFile, image: np.ndarray,
                              bkgrdfile: str, return_map: bool = False,
                              bkgr_no_sub: Optional[bool] = None,
                              bkgr_boxsize: Optional[int] = None,
                              bkgr_ker_amp: Optional[int] = None,
                              env_xorder: Optional[int] = None,
                              env_yorder: Optional[int] = None,
                              env_fpos: Optional[Union[float, str]] = None,
                              env_fbad: Optional[float] = None,
                              env_anneal: Optional[List[float]] = None,
                              env_niter: Optional[int] = None,
                              env_start_q: Optional[float] = None,
                              env_nbin: Optional[List[int]] = None,
                              env_tol: Optional[float] = None,
                              env_bin_size: Optional[int] = None
                              ) -> np.ndarray:
    """
    Background correct an image using a 2D polynomial fit to the lower
    envelope of the background pixels (see
    aperocore.science.calib.background_core.fit_lower_envelope_2d)

    Unlike `correction`, the background level is not estimated with a
    running-median box filter, but with a smooth 2D polynomial that is
    fitted to sit under the background pixels (never above them), which
    removes the box-size/percentile tuning `correction` needs.

    :param recipe: DrsRecipe, used for producing the DEBUG output
    :param params: ParamDict, parameter dictionary of constants
    :param infile: DrsFitsFile, input file
    :param image: np.ndarray, the input image
    :param bkgrdfile: str, the background calibration absolute filename
    :param return_map: bool, if True, return the full background image
    :param bkgr_no_sub: bool or None, optional, whether to do the background
                        measurement (True or False), overrides
                        params['BKGR_NO_SUBTRACTION']
    :param bkgr_boxsize: int, optional, width of the box used for the local
                         (scattered light) background correction, overrides
                         params['CAL.BCORR.BKGR_BOXSIZE']
    :param bkgr_ker_amp: int, optional, kernel amplitude, overrides
                         params['CAL.BCORR.KER_AMP']
    :param env_xorder: int or None, optional, degree of the 2D background
                       polynomial along the columns, overrides
                       params['CAL.BCORR.ENV_XORDER']
    :param env_yorder: int or None, optional, degree of the 2D background
                       polynomial along the rows, overrides
                       params['CAL.BCORR.ENV_YORDER']
    :param env_fpos: float, str or None, optional, what a pixel above the
                     fitted surface costs relative to one below it,
                     overrides params['CAL.BCORR.ENV_FPOS']
    :param env_fbad: float or None, optional, prior on a pixel being bad
                     rather than noise, overrides
                     params['CAL.BCORR.ENV_FBAD']
    :param env_anneal: list of float or None, optional, sigma inflation
                       factors of the first passes, overrides
                       params['CAL.BCORR.ENV_ANNEAL']
    :param env_niter: int or None, optional, maximum number of passes after
                      the annealing, overrides params['CAL.BCORR.ENV_NITER']
    :param env_start_q: float or None, optional, the quantile taken in each
                        tile for the first guess of the surface, overrides
                        params['CAL.BCORR.ENV_START_Q']
    :param env_nbin: list of int or None, optional, number of tiles (in y,
                     in x) used for the first guess of the surface,
                     overrides params['CAL.BCORR.ENV_NBIN']
    :param env_tol: float or None, optional, convergence tolerance,
                    overrides params['CAL.BCORR.ENV_TOL']
    :param env_bin_size: int or None, optional, median-binning factor used
                         for the fit, overrides
                         params['CAL.BCORR.ENV_BIN_SIZE']

    :return: numpy array, either the corrected image, or the full background
             map (if return_map is True)
    """
    func_name = __NAME__ + '.correction_lower_envelope()'
    # get constants from params/kwargs
    no_sub = pcheck(params, 'CAL.BCORR.NO_CORR', 'no_sub', func=func_name,
                    override=bkgr_no_sub)
    # amp_ker = pcheck(params, 'CAL.BCORR.KER_AMP', 'amp_ker', func=func_name,
    #                  override=bkgr_ker_amp)
    # get the 2D lower envelope fit constants
    xorder = pcheck(params, 'CAL.BCORR.ENV_XORDER', 'env_xorder',
                    func=func_name, override=env_xorder)
    yorder = pcheck(params, 'CAL.BCORR.ENV_YORDER', 'env_yorder',
                    func=func_name, override=env_yorder)
    f_pos = pcheck(params, 'CAL.BCORR.ENV_FPOS', 'env_fpos', func=func_name,
                   override=env_fpos)
    f_bad = pcheck(params, 'CAL.BCORR.ENV_FBAD', 'env_fbad', func=func_name,
                   override=env_fbad)
    anneal = pcheck(params, 'CAL.BCORR.ENV_ANNEAL', 'env_anneal',
                    func=func_name, override=env_anneal)
    niter = pcheck(params, 'CAL.BCORR.ENV_NITER', 'env_niter',
                   func=func_name, override=env_niter)
    start_q = pcheck(params, 'CAL.BCORR.ENV_START_Q', 'env_start_q',
                     func=func_name, override=env_start_q)
    nbin = pcheck(params, 'CAL.BCORR.ENV_NBIN', 'env_nbin', func=func_name,
                  override=env_nbin)
    tol = pcheck(params, 'CAL.BCORR.ENV_TOL', 'env_tol', func=func_name,
                 override=env_tol)
    bin_size = pcheck(params, 'CAL.BCORR.ENV_BIN_SIZE', 'env_bin_size',
                      func=func_name, override=env_bin_size)
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
        # if amp_ker > 0:
        #     # measure local background
        #     scattered_light = correct_local_background(params, image)
        #     # we extract a median order profile for the center of the image
        #     local_background_correction = scattered_light / amp_ker
        #     # correct the image for local background
        #     image1 = image - local_background_correction
        # else:
        # copy the image (don't change the original)
        image1 = np.array(image)
        # ------------------------------------------------------------------
        # log process
        msg = 'Background correction [fit lower envelope 2d]'
        WLOG(params, '', msg)
        # # ------------------------------------------------------------------
        # # get background mask file (defines the background-only pixels)
        # bkgrdimage = drs_fits.readfits(params, bkgrdfile)
        # # create mask from badpixmask
        # bmap = np.array(bkgrdimage, dtype=bool)
        # # copy image
        # image2 = np.array(image1)
        # # set to NAN all "illuminated" (non-background) pixels
        # image2[~bmap] = np.nan
        # ------------------------------------------------------------------
        # estimate a (constant) per-pixel noise from the pixel-to-pixel
        #    scatter of the background pixels, used to weight the envelope
        #    fit
        noise = mp.robust_nanstd(np.diff(image1, axis=1))
        errimg = np.full_like(image1, noise)
        # ------------------------------------------------------------------
        # fit a smooth 2D polynomial to the lower envelope of the
        #    background pixels (never fits above the background)
        kwargs = dict(xorder=xorder, yorder=yorder, f_pos=f_pos,
                      f_bad=f_bad, anneal=tuple(anneal), niter=niter,
                      start_q=start_q, nbin=tuple(nbin), tol=tol,
                      bin_size=bin_size)
        envelope = background_mod.fit_lower_envelope_2d(image1, errimg,
                                                        **kwargs)
        # ------------------------------------------------------------------
        # correct image
        corrected_image = image - envelope['fit']
        # ------------------------------------------------------------------
        # produce debug file
        dimages = [corrected_image, image, envelope['fit'],
                   envelope['nsig']]
        # save debug file
        if params['DEBUG.OUTFILE.BCKGRD_FILE']:
            debug_file_envelope(recipe, params, infile, dimages)
        # ------------------------------------------------------------------
        # if return map just return the bad pixel map
        if return_map:
            return envelope['fit']
        else:
            return corrected_image


def debug_file_envelope(recipe: DrsRecipe, params: ParamDict,
                        infile: DrsFitsFile, dlist: List[np.ndarray]):
    """
    Produce the background DEBUG file for `correction_lower_envelope`

    :param recipe: DrsRecipe, the recipe that called this function
    :param params: ParamDict, parameter dictionary of constants
    :param infile: DrsFitsFile, the input file class
    :param dlist: list of numpy array, the images for each extension:
                  1. corrected image
                  2. original image
                  3. Global (2D lower envelope) Background image
                  4. Deviation of each background pixel from the envelope,
                     in units of sigma

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
    kws3 = ['EXTDESC3', 'GLOB_BKGRD', 'Global (lower envelope) Background '
           'image']
    kws4 = ['EXTDESC4', 'GLOB_NSIG', 'Deviation from lower envelope '
           '(sigma)']
    # add to hdict
    debug_back.add_hkey(key=kws1)
    debug_back.add_hkey(key=kws2)
    debug_back.add_hkey(key=kws3)
    debug_back.add_hkey(key=kws4)
    # add primage data to debug_back file
    debug_back.data = dlist[0]
    # print progress: saving file
    WLOG(params, '', textentry('40-013-00025', args=debug_back.filename))
    # define name of extensions
    name_list = ['CORRECTED', 'ORIGINAL', 'GLOB_BKGRD', 'GLOB_NSIG']
    # snapshot of parameters
    if params['GLOBAL.PSNAPSHOT']:
        dlist += [params.snapshot_table(recipe, drsfitsfile=debug_back)]
        name_list += ['PARAM_TABLE']
    # write multiple to file
    debug_back.write_multi(block_kind=recipe.out_block_str,
                           name_list=name_list, data_list=dlist[1:],
                           runstring=recipe.runstring)


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
    if params['GLOBAL.PSNAPSHOT']:
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
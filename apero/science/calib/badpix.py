#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO bad pixel functionality

Created on 2019-05-13 at 11:28

@author: cook
"""
import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
from scipy.ndimage import filters

from apero.base import base
from apero.core.constants import param_functions
from apero.base import drs_lang
from apero.core import math as mp
from apero.core.base import drs_log, drs_file
from apero.core.utils import drs_data
from apero.core.utils import drs_recipe
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.badpix.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the input fits file class
DrsFitsFile = drs_file.DrsFitsFile
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
def normalise_median_flat(params: ParamDict, image: np.ndarray,
                          method: str = 'new',
                          wmed: Optional[float] = None,
                          percentile: Optional[float] = None
                          ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Applies a median filter and normalises. Median filter is applied with width
    "wmed" or p["BADPIX_FLAT_MED_WID"] if wmed is None) and then normalising by
    the 90th percentile

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
                BADPIX_FLAT_MED_WID: float, the median image in the x
                                     dimension over a boxcar of this width
                BADPIX_NORM_PERCENTILE: float, the percentile to normalise
                                        to when normalising and median
                                        filtering image
                log_opt: string, log option, normally the program name

    :param image: numpy array (2D), the iamge to median filter and normalise
    :param method: string, "new" or "old" if "new" uses np.nanpercentile else
                   sorts the flattened image and takes the "percentile" (i.e.
                   90th) pixel value to normalise
    :param wmed: float or None, if not None defines the median filter width
                 if None uses p["BADPIX_MED_WID", see
                 scipy.ndimage.filters.median_filter "size" for more details
    :param percentile: float or None, if not None degines the percentile to
                       normalise the image at, if None used from
                       p["BADPIX_NORM_PERCENTILE"]

    :returns: tuple, 1. norm_med_image: numpy array (2D), the median filtered
                        and normalised image
                     2. norm_image: numpy array (2D), the normalised image
    """
    func_name = __NAME__ + '.normalise_median_flat()'
    # log that we are normalising the flat
    WLOG(params, '', textentry('40-012-00001'))

    # get used percentile
    percentile = pcheck(params, 'BADPIX_NORM_PERCENTILE', func=func_name,
                        override=percentile)

    # wmed: We construct a "simili" flat by taking the running median of the
    # flag in the x dimension over a boxcar width of wmed (suggested
    # value of ~7 pix). This assumes that the flux level varies only by
    # a small amount over wmed pixels and that the badpixels are
    # isolated enough that the median along that box will be representative
    # of the flux they should have if they were not bad
    wmed = pcheck(params, 'BADPIX_FLAT_MED_WID', func=func_name,
                  override=wmed)

    # create storage for median-filtered flat image
    image_med = np.zeros_like(image)

    # loop around x axis
    for i_it in range(image.shape[1]):
        # x-spatial filtering and insert filtering into image_med array
        image_med[i_it, :] = filters.median_filter(image[i_it, :], wmed)

    if method == 'new':
        # get the 90th percentile of median image
        norm = mp.nanpercentile(image_med[np.isfinite(image_med)], percentile)
    else:
        v = image_med.reshape(np.product(image.shape))
        v = np.sort(v)
        norm = v[int(np.product(image.shape) * percentile / 100.0)]

    # apply to flat_med and flat_ref
    return image_med / norm, image / norm


def locate_bad_pixels(params: ParamDict, fimage: np.ndarray,
                      fmed: np.ndarray, dimage: np.ndarray,
                      wmed: Optional[float] = None,
                      cut_ratio: Optional[float] = None,
                      illum_cut: Optional[float] = None,
                      max_hotpix: Optional[float] = None
                      ) -> Tuple[np.ndarray, List[float]]:
    """
    Locate the bad pixels in the flat image and the dark image

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                BADPIX_FLAT_MED_WID: float, the median image in the x
                                     dimension over a boxcar of this width
                BADPIX_FLAT_CUT_RATIO: float, the maximum differential pixel
                                       cut ratio
                BADPIX_ILLUM_CUT: float, the illumination cut parameter
                BADPIX_MAX_HOTPIX: float, the maximum flux in ADU/s to be
                                   considered too hot to be used

    :param fimage: numpy array (2D), the flat normalised image
    :param fmed: numpy array (2D), the flat median normalised image
    :param dimage: numpy array (2D), the dark image
    :param wmed: float or None, if not None defines the median filter width
                 if None uses p["BADPIX_MED_WID", see
                 scipy.ndimage.filters.median_filter "size" for more details
    :param cut_ratio: float or None, optional, the maximum differential pixel
                      cut ratio, overrides params['BADPIX_FLAT_CUT_RATIO']
    :param illum_cut: float or None, optional, the illumination cut parameter,
                      overrides params['BADPIX_ILLUM_CUT']
    :param max_hotpix: float or None, optional, the maximum flux in ADU/s to
                       be considered too hot to be used, overrides
                       params['BADPIX_MAX_HOTPIX']

    :returns: tuple, 1. bad_pix_mask: numpy array (2D), the bad pixel mask
                        image
                     2. badpix_stats: list of floats, the statistics array:
                            Fraction of hot pixels from dark [%]
                            Fraction of bad pixels from flat [%]
                            Fraction of NaN pixels in dark [%]
                            Fraction of NaN pixels in flat [%]
                            Fraction of bad pixels with all criteria [%]
    """
    # set the function name
    func_name = __NAME__ + '.locate_bad_pixels()'
    # log that we are looking for bad pixels
    WLOG(params, '', textentry('40-012-00005'))
    # -------------------------------------------------------------------------
    # wmed: We construct a "simili" flat by taking the running median of the
    # flag in the x dimension over a boxcar width of wmed (suggested
    # value of ~7 pix). This assumes that the flux level varies only by
    # a small amount over wmed pixels and that the badpixels are
    # isolated enough that the median along that box will be representative
    # of the flux they should have if they were not bad
    wmed = pcheck(params, 'BADPIX_FLAT_MED_WID', func=func_name,
                  override=wmed)
    # maxi differential pixel response relative to the expected value
    cut_ratio = pcheck(params, 'BADPIX_FLAT_CUT_RATIO', func=func_name,
                       override=cut_ratio)
    # illumination cut parameter. If we only cut the pixels that
    # fractionnally deviate by more than a certain amount, we are going
    # to have lots of bad pixels in unillumnated regions of the array.
    # We therefore need to set a threshold below which a pixels is
    # considered unilluminated. First of all, the flat field image is
    # normalized by its 90th percentile. This sets the brighter orders
    # to about 1. We then set an illumination threshold below which
    # only the dark current will be a relevant parameter to decide that
    #  a pixel is "bad"
    illum_cut = pcheck(params, 'BADPIX_ILLUM_CUT', func=func_name,
                       override=illum_cut)
    # hotpix. Max flux in ADU/s to be considered too hot to be used
    max_hotpix = pcheck(params, 'BADPIX_MAX_HOTPIX', func=func_name,
                        override=max_hotpix)
    # -------------------------------------------------------------------------
    # create storage for ratio of flat_ref to flat_med
    fratio = np.zeros_like(fimage)
    # create storage for bad dark pixels
    badpix_dark = np.zeros_like(dimage, dtype=bool)
    # -------------------------------------------------------------------------
    # complain if the flat image and dark image do not have the same dimensions
    if dimage.shape != fimage.shape:
        eargs = [fimage.shape, dimage.shape, func_name]
        WLOG(params, 'error', textentry('09-012-00002', args=eargs))
    # -------------------------------------------------------------------------
    # as there may be a small level of scattered light and thermal
    # background in the dark  we subtract the running median to look
    # only for isolate hot pixels
    for i_it in range(fimage.shape[1]):
        dimage[i_it, :] -= filters.median_filter(dimage[i_it, :], wmed)
    # work out how much do flat pixels deviate compared to expected value
    zmask = fmed != 0
    fratio[zmask] = fimage[zmask] / fmed[zmask]
    # catch the warnings
    with warnings.catch_warnings(record=True) as _:
        # if illumination is low, then consider pixel valid for this criterion
        fratio[fmed < illum_cut] = 1
    # catch the warnings
    with warnings.catch_warnings(record=True) as _:
        # where do pixels deviate too much
        badpix_flat = (np.abs(fratio - 1)) > cut_ratio
    # -------------------------------------------------------------------------
    # get finite flat pixels
    valid_flat = np.isfinite(fimage)
    # -------------------------------------------------------------------------
    # get finite dark pixels
    valid_dark = np.isfinite(dimage)
    # -------------------------------------------------------------------------
    # select pixels that are hot
    badpix_dark[valid_dark] = dimage[valid_dark] > max_hotpix
    # -------------------------------------------------------------------------
    # construct the bad pixel mask
    badpix_map = badpix_flat | badpix_dark | ~valid_flat | ~valid_dark
    # -------------------------------------------------------------------------
    # log results
    badpix_stats = [(np.sum(badpix_dark) / np.array(badpix_dark).size) * 100,
                    (np.sum(badpix_flat) / np.array(badpix_flat).size) * 100,
                    (np.sum(~valid_dark) / np.array(valid_dark).size) * 100,
                    (np.sum(~valid_flat) / np.array(valid_flat).size) * 100,
                    (np.sum(badpix_map) / np.array(badpix_map).size) * 100]
    WLOG(params, '', textentry('40-012-00006', args=badpix_stats))
    # -------------------------------------------------------------------------
    # return bad pixel map
    return badpix_map, badpix_stats


def locate_bad_pixels_full(params: ParamDict, image: np.ndarray,
                           threshold: Optional[float] = None,
                           rotnum: Optional[int] = None,
                           assetsdir: Optional[str] = None,
                           badpix_dir: Optional[str] = None,
                           filename: Optional[str] = None
                           ) -> Tuple[np.ndarray, List[float]]:
    """
    Locate the bad pixels identified from the full engineering flat image
    (location defined from p['BADPIX_FULL_FLAT'])

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_IMAGE_TYPE: string, the detector type (this step is only for
                           H4RG)
            LOG_OPT: string, log option, normally the program name
            BADPIX_FULL_FLAT: string, the full engineering flat filename
            BADPIX_FULL_THRESHOLD: float, the threshold on the engineering
                                   above which the data is good
    :param image: numpy array (2D), the image to correct (for size only)
    :param threshold:
    :param rotnum:
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param badpix_dir: str, where the badpix file is stored (within assets
                      directory) -- overrides params['DRS_BADPIX_DATA']
    :param filename: str, the badpix file name
                     -- overrides params['BADPIX_FULL_FLAT']

    :returns: tuple, 1. newimage: numpy array (2D), the mask of the bad pixels
                     2. stats: float, the fraction of un-illuminated pixels
                        (percentage)
    """
    func_name = __NAME__ + '.locate_bad_pixels_full()'
    # log that we are looking for bad pixels
    WLOG(params, '', textentry('40-012-00002'))
    # get parameters from params/kwargs
    threshold = pcheck(params, 'BADPIX_FULL_THRESHOLD', func=func_name,
                       override=threshold)
    rotnum = pcheck(params, 'RAW_TO_PP_ROTATION', func=func_name,
                    override=rotnum)
    assetsdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                       override=assetsdir)
    badpix_dir = pcheck(params, 'DRS_BADPIX_DATA', func=func_name,
                        override=badpix_dir)
    filename = pcheck(params, 'BADPIX_FULL_FLAT', func=func_name,
                      override=filename)
    # get full flat
    mdata = drs_data.load_full_flat_badpix(params, assetsdir=assetsdir,
                                           badpix_dir=badpix_dir,
                                           filename=filename)
    # check if the shape of the image and the full flat match
    if image.shape != mdata.shape:
        eargs = [mdata.shape, image.shape, func_name]
        WLOG(params, 'error', textentry('09-012-00001', args=eargs))
    # apply threshold
    mask = np.abs(mp.rot8(mdata, rotnum) - 1) > threshold
    # -------------------------------------------------------------------------
    # log results
    badpix_stats = [100.0 * (np.sum(mask) / np.array(mask).size)]
    WLOG(params, '', textentry('40-012-00004', args=[badpix_stats[0]]))
    # return mask
    # noinspection PyTypeChecker
    return mask, badpix_stats


def correction(params: ParamDict, image: Union[np.ndarray, None],
               badpixfile: str, return_map: bool = False) -> np.ndarray:
    """
    Corrects "image" for bad pixels using badpixfile

    :param params: ParamDict, parameter dictionary of constants
    :param image: numpy array (2D), the image
    :param badpixfile: str, the bad pixel calibration file
    :param return_map: bool, if True returns bad pixel map else returns
                       corrected image

    :returns: numpy array (2D), the corrected image where all bad pixels are
              set to zeros or the bad pixel map (if return_map = True)
    """
    _ = __NAME__ + '.correct_for_baxpix()'
    # -------------------------------------------------------------------------
    # get bad pixel file
    badpiximage = drs_fits.readfits(params, badpixfile)
    # create mask from badpixmask
    mask = np.array(badpiximage, dtype=bool)
    # -------------------------------------------------------------------------
    if image is None and not return_map:
        # TODO: Add to language database
        emsg = ('Image cannot be None if we are not just returning the map'
                ' please set "image" or set "return_map=True"')
        WLOG(params, 'error', emsg)
    # if return map just return the bad pixel map
    if return_map:
        return mask
    # else put NaNs into the image
    else:
        # log that we are setting background pixels to NaN
        WLOG(params, '', textentry('40-012-00008', args=[badpixfile]))
        # correct image (set bad pixels to zero)
        corrected_image = np.array(image)
        corrected_image[mask] = np.nan
        # finally return corrected_image
        return corrected_image


# =============================================================================
# write files and qc functions
# =============================================================================
def quality_control(params: ParamDict) -> Tuple[List[list], int]:
    """
    Quality control for bad pixel correction

    :param params: ParamDict, parameter dictionary of constants

    :return: tuple, 1. the qc lists, 2. int 1 if passed 0 if failed
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # ------------------------------------------------------------------
    # add to qc header lists
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # return qc_params and passed
    return qc_params, passed


def write_files(params: ParamDict, recipe: DrsRecipe, flatfile: DrsFitsFile,
                darkfile: DrsFitsFile, backmap: np.ndarray, combine: bool,
                rawflatfiles: List[str], rawdarkfiles: List[str],
                bstats_a: List[float], bstats_b: List[float], btotal: float,
                bad_pixel_map1: np.ndarray, qc_params: List[list]
                ) -> Tuple[DrsFitsFile, DrsFitsFile]:
    """
    Write the bad pixel and background files to disk

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
    :param flatfile: DrsFitsFile, the input flat file class
    :param darkfile: DrsFitsFile, the input dark file class
    :param backmap: numpy (2D) array, the background map
    :param combine: bool, if True inputs were combined, otherwise they weren't
    :param rawflatfiles: list of strings, the raw flat file names
    :param rawdarkfiles: list of strings, the raw dark file names
    :param bstats_a: list of floats, stats from the bad pixel finding
    :param bstats_b: list of floats, stats from the full bad pixel finding
    :param btotal: float, total number of bad pixels as a percentage
    :param bad_pixel_map1: numpy (2D) array, the bad pixel map
    :param qc_params: list of lists, the quality control lists

    :return: tuple, 1. the bad pixel file class, 2. the background file class
    """
    badpixfile = recipe.outputs['BADPIX'].newcopy(params=params)
    # construct the filename from file instance
    badpixfile.construct_filename(infile=flatfile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    badpixfile.copy_original_keys(flatfile)
    # add core values (that should be in all headers)
    badpixfile.add_core_hkeys(params)
    # add input files
    if combine:
        hfiles1, hfiles2 = rawflatfiles, rawdarkfiles
    else:
        hfiles1, hfiles2 = [flatfile.basename], [darkfile.basename]
    badpixfile.add_hkey_1d('KW_INFILE1', values=hfiles1,
                           dim1name='flatfile')
    badpixfile.add_hkey_1d('KW_INFILE2', values=hfiles2,
                           dim1name='darkfile')
    # add infiles
    badpixfile.infiles = list(hfiles1) + list(hfiles2)
    # add qc parameters
    badpixfile.add_qckeys(qc_params)
    # add background statistics
    badpixfile.add_hkey('KW_BHOT', value=bstats_a[0])
    badpixfile.add_hkey('KW_BBFLAT', value=bstats_a[1])
    badpixfile.add_hkey('KW_BNDARK', value=bstats_a[2])
    badpixfile.add_hkey('KW_BNFLAT', value=bstats_a[3])
    badpixfile.add_hkey('KW_BBAD', value=bstats_a[4])
    badpixfile.add_hkey('KW_BNILUM', value=bstats_b[0])
    badpixfile.add_hkey('KW_BTOT', value=btotal)
    # write to file
    bad_pixel_map1 = np.array(bad_pixel_map1, dtype=int)
    # copy data
    badpixfile.data = bad_pixel_map1
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-012-00013', args=[badpixfile.filename]))
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list = [params.snapshot_table(recipe, drsfitsfile=badpixfile)]
        name_list = ['PARAM_TABLE']
    else:
        data_list, name_list = [], []
    # write image to file
    badpixfile.write_multi(data_list=data_list, name_list=name_list,
                           block_kind=recipe.out_block_str,
                           runstring=recipe.runstring)

    # add to output files (for indexing)
    recipe.add_output_file(badpixfile)
    # ----------------------------------------------------------------------
    # Save background map file
    # ----------------------------------------------------------------------
    backmapfile = recipe.outputs['BACKMAP'].newcopy(params=params)
    # construct the filename from file instance
    backmapfile.construct_filename(infile=flatfile)
    # ------------------------------------------------------------------
    # define header keys for output file (copy of badpixfile)
    backmapfile.copy_hdict(badpixfile)
    # add output tag
    backmapfile.add_hkey('KW_OUTPUT', value=backmapfile.name)
    # add infiles
    backmapfile.infiles = list(hfiles1) + list(hfiles2)
    # write to file
    backmap = np.array(backmap, dtype=int)
    # copy data
    backmapfile.data = backmap
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-012-00014', args=[backmapfile.filename]))
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list = [params.snapshot_table(recipe, drsfitsfile=backmapfile)]
        name_list = ['PARAM_TABLE']
    else:
        data_list, name_list = [], []
    # write image to file
    backmapfile.write_multi(data_list=data_list, name_list=name_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(backmapfile)
    # return output files
    return badpixfile, backmapfile


def summary(recipe: DrsRecipe, it: int, params: ParamDict,
            bstats_a: List[float], bstats_b: List[float], btotal: float):
    """

    :param recipe: DrsRecipe, the recipe that called this function
    :param it: int, the iteration
    :param params: ParamDict, parameter dictionary of constants
    :param bstats_a: list of floats, stats from the bad pixel finding
    :param bstats_b: list of floats, stats from the full bad pixel finding
    :param btotal: float, total number of bad pixels as a percentage

    :return: None, produces summary document
    """
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_BHOT', value=bstats_a[0])
    recipe.plot.add_stat('KW_BBFLAT', value=bstats_a[1])
    recipe.plot.add_stat('KW_BNDARK', value=bstats_a[2])
    recipe.plot.add_stat('KW_BNFLAT', value=bstats_a[3])
    recipe.plot.add_stat('KW_BBAD', value=bstats_a[4])
    recipe.plot.add_stat('KW_BNILUM', value=bstats_b[0])
    recipe.plot.add_stat('KW_BTOT', value=btotal)
    # construct summary
    recipe.plot.summary_document(it)


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

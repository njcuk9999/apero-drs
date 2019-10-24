#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-13 at 11:28

@author: cook
"""
from __future__ import division
import numpy as np
import warnings
import os
from scipy.ndimage import filters

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.core.core import drs_database
from terrapipe.io import drs_fits
from terrapipe.io import drs_data

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.badpix.py'
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
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def normalise_median_flat(params, image, method='new', **kwargs):
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
    :param kwargs: keyword arguments

    :keyword wmed: float or None, if not None defines the median filter width
                 if None uses p["BADPIX_MED_WID", see
                 scipy.ndimage.filters.median_filter "size" for more details
    :keyword percentile: float or None, if not None degines the percentile to
                       normalise the image at, if None used from
                       p["BADPIX_NORM_PERCENTILE"]

    :return norm_med_image: numpy array (2D), the median filtered and normalised
                            image
    :return norm_image: numpy array (2D), the normalised image
    """
    func_name = __NAME__ + '.normalise_median_flat()'
    # log that we are normalising the flat
    WLOG(params, '', TextEntry('40-012-00001'))

    # get used percentile
    percentile = pcheck(params, 'BADPIX_NORM_PERCENTILE', 'percentile', kwargs,
                        func_name)

    # wmed: We construct a "simili" flat by taking the running median of the
    # flag in the x dimension over a boxcar width of wmed (suggested
    # value of ~7 pix). This assumes that the flux level varies only by
    # a small amount over wmed pixels and that the badpixels are
    # isolated enough that the median along that box will be representative
    # of the flux they should have if they were not bad
    wmed = pcheck(params, 'BADPIX_FLAT_MED_WID', 'wmed', kwargs, func_name)

    # create storage for median-filtered flat image
    image_med = np.zeros_like(image)

    # loop around x axis
    for i_it in range(image.shape[1]):
        # x-spatial filtering and insert filtering into image_med array
        image_med[i_it, :] = filters.median_filter(image[i_it, :], wmed)

    if method == 'new':
        # get the 90th percentile of median image
        norm = np.nanpercentile(image_med[np.isfinite(image_med)], percentile)
    else:
        v = image_med.reshape(np.product(image.shape))
        v = np.sort(v)
        norm = v[int(np.product(image.shape) * percentile/100.0)]

    # apply to flat_med and flat_ref
    return image_med/norm, image/norm


def locate_bad_pixels(params, fimage, fmed, dimage, **kwargs):
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

    :return bad_pix_mask: numpy array (2D), the bad pixel mask image
    :return badpix_stats: list of floats, the statistics array:
                            Fraction of hot pixels from dark [%]
                            Fraction of bad pixels from flat [%]
                            Fraction of NaN pixels in dark [%]
                            Fraction of NaN pixels in flat [%]
                            Fraction of bad pixels with all criteria [%]
    """
    func_name = __NAME__ + '.locate_bad_pixels()'
    # log that we are looking for bad pixels
    WLOG(params, '', TextEntry('40-012-00005'))
    # -------------------------------------------------------------------------
    # wmed: We construct a "simili" flat by taking the running median of the
    # flag in the x dimension over a boxcar width of wmed (suggested
    # value of ~7 pix). This assumes that the flux level varies only by
    # a small amount over wmed pixels and that the badpixels are
    # isolated enough that the median along that box will be representative
    # of the flux they should have if they were not bad
    wmed = pcheck(params, 'BADPIX_FLAT_MED_WID', 'wmed', kwargs, func_name)

    # maxi differential pixel response relative to the expected value
    cut_ratio = pcheck(params, 'BADPIX_FLAT_CUT_RATIO', 'cut_ratio', kwargs,
                       func_name)
    # illumination cut parameter. If we only cut the pixels that
    # fractionnally deviate by more than a certain amount, we are going
    # to have lots of bad pixels in unillumnated regions of the array.
    # We therefore need to set a threshold below which a pixels is
    # considered unilluminated. First of all, the flat field image is
    # normalized by its 90th percentile. This sets the brighter orders
    # to about 1. We then set an illumination threshold below which
    # only the dark current will be a relevant parameter to decide that
    #  a pixel is "bad"
    illum_cut = pcheck(params, 'BADPIX_ILLUM_CUT', 'illum_cut', kwargs,
                       func_name)
    # hotpix. Max flux in ADU/s to be considered too hot to be used
    max_hotpix = pcheck(params, 'BADPIX_MAX_HOTPIX', 'max_hotpix', kwargs,
                        func_name)
    # -------------------------------------------------------------------------
    # create storage for ratio of flat_ref to flat_med
    fratio = np.zeros_like(fimage)
    # create storage for bad dark pixels
    badpix_dark = np.zeros_like(dimage, dtype=bool)
    # -------------------------------------------------------------------------
    # complain if the flat image and dark image do not have the same dimensions
    if dimage.shape != fimage.shape:
        eargs = [fimage.shape, dimage.shape, func_name]
        WLOG(params, 'error', TextEntry('09-012-00002', args=eargs))
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
    WLOG(params, '', TextEntry('40-012-00006', args=badpix_stats))
    # -------------------------------------------------------------------------
    # return bad pixel map
    return badpix_map, badpix_stats


def locate_bad_pixels_full(params, image, **kwargs):
    """
    Locate the bad pixels identified from the full engineering flat image
    (location defined from p['BADPIX_FULL_FLAT'])

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_IMAGE_TYPE: string, the detector type (this step is only for
                           H4RG)
            LOG_OPT: string, log option, normally the program name
            BADPIX_FULL_FLAT: string, the full engineering flat filename
            BADPIX_FULL_THRESHOLD: float, the threshold on the engineering
                                   above which the data is good
    :param image: numpy array (2D), the image to correct (for size only)

    :return newimage: numpy array (2D), the mask of the bad pixels
    :return stats: float, the fraction of un-illuminated pixels (percentage)
    """
    func_name = __NAME__ + '.locate_bad_pixels_full()'
    # log that we are looking for bad pixels
    WLOG(params, '', TextEntry('40-012-00002'))
    # get parameters from params/kwargs
    threshold = pcheck(params, 'BADPIX_FULL_THRESHOLD', 'threshold', kwargs,
                       func_name)
    # get full flat
    mdata = drs_data.load_full_flat_badpix(params, **kwargs)
    # check if the shape of the image and the full flat match
    if image.shape != mdata.shape:
        eargs = [mdata.shape, image.shape, func_name]
        WLOG(params, 'error', TextEntry('09-012-00001', args=eargs))
    # apply threshold
    # mask = np.rot90(mdata, -1) < threshold
    mask = np.abs(np.rot90(mdata, -1)-1) > threshold
    # -------------------------------------------------------------------------
    # log results
    badpix_stats = (np.sum(mask) / np.array(mask).size) * 100
    WLOG(params, '', TextEntry('40-012-00004', args=[badpix_stats]))
    # return mask
    return mask, badpix_stats


def correction(params, image=None, header=None, return_map=False, **kwargs):
    """
    Corrects "image" for "BADPIX" using calibDB file (header must contain
    value of p['ACQTIME_KEY'] as a keyword) - sets all bad pixels to zeros

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                calibDB: dictionary, the calibration database dictionary
                         (if not in "p" we construct it and need "max_time_unix"
                max_time_unix: float, the unix time to use as the time of
                                reference (used only if calibDB is not defined)
                log_opt: string, log option, normally the program name
                DRS_CALIB_DB: string, the directory that the calibration
                              files should be saved to/read from

    :param image: numpy array (2D), the image
    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage
    :param return_map: bool, if True returns bad pixel map else returns
                       corrected image

    :returns: numpy array (2D), the corrected image where all bad pixels are
              set to zeros or the bad pixel map (if return_map = True)
    """
    func_name = __NAME__ + '.correct_for_baxpix()'
    # check for filename in kwargs
    filename = kwargs.get('filename', None)
    # deal with no header
    if header is None:
        WLOG(params, 'error', TextEntry('00-012-00002', args=[func_name]))
    # deal with no image (when return map is False)
    if (not return_map) and (image is None):
        WLOG(params, 'error', TextEntry('00-012-00003', args=[func_name]))
    # -------------------------------------------------------------------------
    # get filename
    if filename is not None:
        badpixfile = filename
    else:
        # get calibDB
        cdb = drs_database.get_full_database(params, 'calibration')
        # get filename col
        filecol = cdb.file_col
        # get the badpix entries
        badpixentries = drs_database.get_key_from_db(params, 'BADPIX', cdb,
                                                     header, n_ent=1)
        # get badpix filename
        badpixfilename = badpixentries[filecol][0]
        badpixfile = os.path.join(params['DRS_CALIB_DB'], badpixfilename)
    # -------------------------------------------------------------------------
    # get bad pixel file
    badpiximage = drs_fits.read(params, badpixfile)
    # create mask from badpixmask
    mask = np.array(badpiximage, dtype=bool)
    # -------------------------------------------------------------------------
    # if return map just return the bad pixel map
    if return_map:
        return badpixfile, mask
    # else put NaNs into the image
    else:
        # log that we are setting background pixels to NaN
        WLOG(params, '', TextEntry('40-012-00008', args=[badpixfile]))
        # correct image (set bad pixels to zero)
        corrected_image = np.array(image)
        corrected_image[mask] = np.nan
        # finally return corrected_image
        return badpixfile, corrected_image


# =============================================================================
# write files and qc functions
# =============================================================================
def quality_control(params):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # ------------------------------------------------------------------
    # TODO: Needs quality control doing
    # add to qc header lists
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # return qc_params and passed
    return qc_params, passed


def write_files(params, recipe, flatfile, darkfile, backmap, combine,
                       rawflatfiles, rawdarkfiles, bstats_a, bstats_b, btotal,
                       bad_pixel_map1, qc_params):
    badpixfile = recipe.outputs['BADPIX'].newcopy(recipe=recipe)
    # construct the filename from file instance
    badpixfile.construct_filename(params, infile=flatfile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    badpixfile.copy_original_keys(flatfile)
    # add version
    badpixfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    badpixfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    badpixfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    badpixfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    badpixfile.add_hkey('KW_OUTPUT', value=badpixfile.name)
    # add input files
    if combine:
        hfiles1, hfiles2 = rawflatfiles, rawdarkfiles
    else:
        hfiles1, hfiles2 = [flatfile.basename], [darkfile.basename]
    badpixfile.add_hkey_1d('KW_INFILE1', values=hfiles1,
                           dim1name='flatfile')
    badpixfile.add_hkey_1d('KW_INFILE2', values=hfiles2,
                           dim1name='darkfile')
    # add qc parameters
    badpixfile.add_qckeys(qc_params)
    # add background statistics
    badpixfile.add_hkey('KW_BHOT', value=bstats_a[0])
    badpixfile.add_hkey('KW_BBFLAT', value=bstats_a[1])
    badpixfile.add_hkey('KW_BNDARK', value=bstats_a[2])
    badpixfile.add_hkey('KW_BNFLAT', value=bstats_a[3])
    badpixfile.add_hkey('KW_BBAD', value=bstats_a[4])
    badpixfile.add_hkey('KW_BNILUM', value=bstats_b)
    badpixfile.add_hkey('KW_BTOT', value=btotal)
    # write to file
    bad_pixel_map1 = np.array(bad_pixel_map1, dtype=int)
    # copy data
    badpixfile.data = bad_pixel_map1
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', TextEntry('40-012-00013', args=[badpixfile.filename]))
    # write image to file
    badpixfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(badpixfile)
    # ----------------------------------------------------------------------
    # Save background map file
    # ----------------------------------------------------------------------
    backmapfile = recipe.outputs['BACKMAP'].newcopy(recipe=recipe)
    # construct the filename from file instance
    backmapfile.construct_filename(params, infile=flatfile)
    # ------------------------------------------------------------------
    # define header keys for output file (copy of badpixfile)
    backmapfile.copy_hdict(badpixfile)
    # add output tag
    backmapfile.add_hkey('KW_OUTPUT', value=backmapfile.name)
    # write to file
    backmap = np.array(backmap, dtype=int)
    # copy data
    backmapfile.data = backmap
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', TextEntry('40-012-00014', args=[backmapfile.filename]))
    # write image to file
    backmapfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(backmapfile)
    # return output files
    return badpixfile, backmapfile


def summary(recipe, it, params, bstats_a, bstats_b, btotal):
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_BHOT', value=bstats_a[0])
    recipe.plot.add_stat('KW_BBFLAT', value=bstats_a[1])
    recipe.plot.add_stat('KW_BNDARK', value=bstats_a[2])
    recipe.plot.add_stat('KW_BNFLAT', value=bstats_a[3])
    recipe.plot.add_stat('KW_BBAD', value=bstats_a[4])
    recipe.plot.add_stat('KW_BNILUM', value=bstats_b)
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

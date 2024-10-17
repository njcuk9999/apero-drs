#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-07-2020-07-15 17:58

@author: cook
"""
import os
from typing import List, Optional, Tuple, Union

import numpy as np
from astropy import constants as cc
from astropy import units as uu
from astropy.table import Table
from scipy.ndimage import binary_erosion, binary_dilation
from scipy.optimize import curve_fit

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore import drs_lang
from aperocore import math as mp
from aperocore.core import drs_misc
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_utils
from apero.io import drs_fits
from apero.science.calib import wave
from apero.science.telluric import gen_tellu
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.sky_corr.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get Astropy Time and Time Delta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# get param dict
ParamDict = param_functions.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsRecipe = drs_recipe.DrsRecipe
# get databases
CalibrationDatabase = drs_database.CalibrationDatabase
TelluricDatabase = drs_database.TelluricDatabase
# Get function string
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value

# =============================================================================
# Reference sky-corr functions
# =============================================================================
skyfile_return = Tuple[Union[List[str], None], Union[DrsFitsFile, None]]


def find_night_skyfiles(params: ParamDict, fiber: Union[str, None],
                        filetype: str) -> skyfile_return:
    """
    Find night sky files and push into list. Also load last night sky file
    as the reference night sky file

    fiber can be None only in the case of a calibration fiber

    :param params: ParamDict, parameter dictionary of constants
    :param fiber: str or None, if str the fiber to use to find files
    :param filetype: str, the file type (KW_OUTPUT) of the files to find
                     (i.e. for e2dsff use EXT_E2DS_FF)

    :raises: Drs Exception if no files found (and fiber was not None)
    :return: tuple 1: None, 2: None if fiber was None, otherwise a tuple
             1: list of night sky files found, 2: reference infile
    """
    # set function name
    func_name = display_func('find_night_skyfiles', __NAME__)
    # return None if fiber is None (should only be the case for cal fiber)
    if fiber is None:
        return None, None
    # get the science fiber files for "SKY" files (which are night files)
    #    for the specific filetype
    sky_files = drs_utils.find_files(params, block_kind='red',
                                     filters=dict(KW_TARGET_TYPE='SKY',
                                                  KW_NIGHT_OBS='1',
                                                  KW_OUTPUT=filetype,
                                                  KW_FIBER=fiber))
    # deal with no science files
    if len(sky_files) == 0:
        emsg = ('No night SKY files found (KW_OUTPUT={0} KW_FIBER={1})'
                '\n\tFunction = {2}')
        eargs = [filetype, fiber, func_name]
        # log error
        WLOG(params, 'error', emsg.format(*eargs))
        return None, None
    else:
        sky_files = list(np.sort(sky_files))
    # Get filetype definition
    infiletype = drs_file.get_file_definition(params, filetype,
                                              block_kind='red')
    # get new copy of file definition
    infile = infiletype.newcopy(params=params, fiber=fiber)
    # set reference filename
    infile.set_filename(sky_files[-1])
    # read data
    infile.read_file()
    # return list of files and infile
    return sky_files, infile


def skymodel_matchfiles(sky_files_sci: List[str], sky_files_cal: List[str],
                        sci_fiber: str, cal_fiber: str):
    """
    Only keep files that match in both fibers

    :param sky_files_sci:
    :param sky_files_cal:
    :param sci_fiber:
    :param cal_fiber:

    :return:
    """
    # lists for keeping
    keep_sci_files = []
    keep_cal_files = []
    # loop around science fiber filers
    for sci_file in sky_files_sci:
        # science fiber files must have _{fiber} in their name
        basename_sci = sci_file.replace(f'_{sci_fiber}', '')
        for cal_file in sky_files_cal:
            # calibration fiber files must have _{fiber} in their name
            basename_cal = cal_file.replace(f'_{cal_fiber}', '')
            # test whether "de-fibered" name matches
            if basename_sci == basename_cal:
                # add to keep lists
                keep_sci_files.append(sci_file)
                keep_cal_files.append(cal_file)
                # break here: we don't need to continue looking through
                #             cal_files
                break
    # return new list of science and calib fiber files
    return keep_sci_files, keep_cal_files


def skymodel_table(params: ParamDict, sky_files: Union[List[str], None],
                   reffile: DrsFitsFile, snr_order: Optional[int] = None,
                   min_exptime: Optional[float] = None,
                   max_files: Optional[int] = None,
                   ) -> Tuple[Union[Table, None], Union[DrsFitsFile, None], int]:
    # set function name
    func_name = display_func('skymodel_table', __NAME__)
    # -------------------------------------------------------------------------
    # deal with sky_files being None
    if sky_files is None:
        return None, None, 0
    # -------------------------------------------------------------------------
    # get parameters from parameter dictionary
    snr_order = pcheck(params, 'SKYMODEL_EXT_SNR_ORDERNUM', func=func_name,
                       override=snr_order)
    min_exptime = pcheck(params, 'SKYMODEL_MIN_EXPTIME', func=func_name,
                         override=min_exptime)
    max_files = pcheck(params, 'SKYMODEL_MAX_OPEN_FILES', func=func_name,
                       override=max_files)
    # get fiber from ref file
    fiber = reffile.fiber
    # -------------------------------------------------------------------------
    # storage for table dictionary columns
    table_dict = dict()
    # define columns for table
    table_dict['FILENAME'] = []
    table_dict['DPRTYPE'] = []
    table_dict['EXPTIME'] = []
    table_dict['AIRMASS'] = []
    table_dict['SUN_ALT'] = []
    table_dict['MJDMID'] = []
    table_dict[f'SNR_{snr_order}'] = []
    table_dict['USED'] = []
    # -------------------------------------------------------------------------
    # loop around sky files
    for sky_file in sky_files:
        # get new copy of file definition - do not copy the data as it is
        #   already loaded in reffile (set to empty array for now)
        infile = reffile.newcopy(params=params, fiber=fiber,
                                 data=np.array([]))
        # set filename
        infile.set_filename(sky_file)
        # read header only
        infile.read_header()
        # get dprtype
        dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
        # get exptime
        exptime = infile.get_hkey('KW_EXPTIME', dtype=float)
        # get airmass
        airmass = infile.get_hkey('KW_AIRMASS', dtype=float)
        # get sun elevation
        sun_elev = infile.get_hkey('KW_SUN_ELEV', dtype=float)
        # get mid exposure time
        mjdmid = infile.get_hkey('KW_MID_OBS_TIME', dtype=float)
        # get number of orders
        nbo = infile.get_hkey('KW_WAVE_NBO', dtype=int)
        # get snr
        snr = infile.get_hkey_1d('KW_EXT_SNR', nbo, dtype=float)
        # add values to table_dict
        table_dict['FILENAME'].append(sky_file)
        table_dict['DPRTYPE'].append(dprtype)
        table_dict['EXPTIME'].append(exptime)
        table_dict['AIRMASS'].append(airmass)
        table_dict['SUN_ALT'].append(sun_elev)
        table_dict['MJDMID'].append(mjdmid)
        table_dict[f'SNR_{snr_order}'].append(snr[snr_order])
        # deal with exposure time cut off
        if exptime < min_exptime:
            table_dict['USED'].append(False)
        else:
            table_dict['USED'].append(True)
    # -------------------------------------------------------------------------
    # convert dictionary to table
    sky_table = Table(table_dict)
    # mask by exposure time
    use_mask = sky_table['USED'] == 1
    sky_table = sky_table[use_mask]
    # -------------------------------------------------------------------------
    # sort by MJDMID
    sortmask = np.argsort(sky_table['MJDMID'])
    sky_table = sky_table[sortmask]
    # -------------------------------------------------------------------------
    # calculate bin number and assign bin for all remaining objects
    nfiles = len(sky_table)
    # work out the maximum number of bins given the maximum number of files
    nbins = np.max([nfiles // max_files, 1])
    # assign bin number
    sky_table['BIN_NUM'] = (nbins * np.arange(nfiles)) // nfiles
    # -------------------------------------------------------------------------
    # update ref infile (use the latest file)
    reffile2 = reffile.newcopy(params=params, fiber=fiber,
                               data=np.array([]))
    # set reference filename
    reffile2.set_filename(sky_table['FILENAME'][-1])
    # read data
    reffile2.read_file()
    # -------------------------------------------------------------------------
    # return filled table
    return sky_table, reffile2, nbins


# define function to act on image
def skymodel_combine_func(image: np.ndarray, hdr: drs_fits.Header,
                          params: ParamDict, recipe: DrsRecipe,
                          refwavemap: np.ndarray, fiber: str) -> np.ndarray:
    """
    Modification of the original image to add to median "cube"

    :param image: np.ndarray, image to update - passed from
                  large_image_combine
    :param hdr: fits.Header - header associated with image passed
                from large_image_combine
    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, recipe calling this function
    :param refwavemap: np.ndarray, reference night wavelength solution
    :param fiber: str, the fiber this image is associated with

    :return: np.ndarray, the updated image
    """
    # avoid NaNs for the spline later
    image[~np.isfinite(image)] = 0.0
    # load wavelength solution for this image
    mkwargs = dict(header=hdr, ref=True, fiber=fiber)
    wprops = wave.get_wavesolution(params, recipe, **mkwargs)
    wavemap = wprops['WAVEMAP']
    # loop around each order and low pass
    for order_num in range(image.shape[0]):
        # calculate the low pass filter
        lowpass = mp.lowpassfilter(image[order_num], 101)
        # apply this to the image
        limage = image[order_num] - lowpass
        # spline on the reference wave grid
        ispline = mp.iuv_spline(wavemap[order_num], limage,
                                ext=1, k=3)
        # get image on reference wave grid
        image[order_num] = np.array(ispline(refwavemap[order_num]))
    # return the image
    return np.array(image)


def skymodel_cube(recipe: DrsRecipe, params: ParamDict,
                  sky_table: Union[Table, None], nbins: int,
                  fiber: str, refwavemap: np.ndarray) -> ParamDict:
    """
    Product a cube and median of all sky_table files (binned by BIN_NUM)
    to downsample cube (otherwise we open all files and have to store a
    potential very large cube)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, recipe calling this function
    :param sky_table: astropy.Table - the sky files table
    :param nbins: int, the number of bins
    :param fiber: str, the fiber type
    :param refwavemap: np.ndarray, the reference night wavelength solution

    :return: ParamDict, the sky model parameters
    """
    # set function name
    func_name = display_func('skymodel_cube', __NAME__)
    # output parameter dictionary storage
    sky_props = ParamDict()
    # deal with no sky_table
    if sky_table is None:
        # set values for sky props
        sky_props['HAS_SKY'] = False
        sky_props['MED'] = None
        sky_props['TABLE'] = None
    else:
        # print progress
        # TODO: Add to language database
        msg = 'Building sky model cubes fiber={0}'
        margs = [fiber]
        WLOG(params, '', msg.format(*margs))
        # get sky filenames
        sky_files = np.array(sky_table['FILENAME'])
        # get bins
        sky_bins = np.array(sky_table['BIN_NUM'])
        # set up median storage
        cube = np.zeros([nbins, np.product(refwavemap.shape)])
        # loop around files
        for it in range(len(sky_files)):
            # print analysing file
            msg = '\tAdding sky file {0}/{1}'
            margs = [it + 1, len(sky_files)]
            WLOG(params, '', msg.format(*margs))
            # read image and header
            image, hdr = drs_fits.readfits(params, sky_files[it], gethdr=True)
            # lowpass + shift image
            cimage = skymodel_combine_func(image, hdr, params, recipe,
                                           refwavemap, fiber)
            # sum to the binned image ravelled into 1D
            cube[sky_bins[it]] += cimage.ravel()
            # remove image and header
            del image, cimage, hdr
        # get median sky spectrum, only used for identification of lines
        med = np.nanmedian(cube, axis=0)
        # set values for sky props
        sky_props['HAS_SKY'] = True
        sky_props['MED'] = med
        sky_props['WAVEMAP'] = refwavemap
        sky_props['WAVEMAPR'] = refwavemap.ravel()
        sky_props['CUBE'] = cube
        sky_props['TABLE'] = sky_table
    # set source
    keys = ['HAS_SKY', 'MED', 'CUBE', 'WAVEMAP', 'WAVEMAPR', 'TABLE']
    sky_props.set_sources(keys, func_name)
    # return updated sky props parameter dictionary
    return sky_props


def identify_sky_line_regions(params: ParamDict, sky_props: ParamDict,
                              line_sigma: Optional[float] = None,
                              erode_size: Optional[int] = None,
                              dilate_size: Optional[int] = None,
                              wavestart: Optional[float] = None,
                              waveend: Optional[float] = None,
                              binvelo: Optional[float] = None,
                              ) -> np.ndarray:
    # set function name
    func_name = display_func('identify_sky_line_regions', __NAME__)
    # get parameters from parameter dictionary
    line_sigma = pcheck(params, 'SKYMODEL_LINE_SIGMA', func=func_name,
                        override=line_sigma)
    erode_size = pcheck(params, 'SKYMODEL_LINE_ERODE_SIZE', func=func_name,
                        override=erode_size)
    dilate_size = pcheck(params, 'SKYMODEL_LINE_DILATE_SIZE', func=func_name,
                         override=dilate_size)
    wavestart = pcheck(params, 'EXT_S1D_WAVESTART', func=func_name,
                       override=wavestart)
    waveend = pcheck(params, 'EXT_S1D_WAVEEND', 'waveend', func=func_name,
                     override=waveend)
    binvelo = pcheck(params, 'EXT_S1D_BIN_UVELO', func=func_name,
                     override=binvelo)
    # ravel e2ds wavemap (for dilation stuff later)
    wave1d = sky_props['WAVEMAPR']
    # get the median sky spectrum
    sky_med = sky_props['MED']
    # set all NaN values to zero
    sky_med[~np.isfinite(sky_med)] = 0.0
    # find positive excursions in sky signal
    nsig = sky_med / mp.estimate_sigma(sky_med)
    # identify lines that are n sigma positive excursions
    line = np.array(nsig > line_sigma, dtype=int)
    # erode features that are too narrow
    line = binary_erosion(line, structure=np.ones(erode_size))
    # dilate to get wings of lines
    line = binary_dilation(line, structure=np.ones(dilate_size))
    # build the region mask
    regions = np.cumsum(line != np.roll(line, 1))
    # set all the even regions to zero
    regions[(regions % 2) == 0] = 0
    # re-number all non-zero regions to produce labels from 1--> N
    #   (original were all the odd numbers)
    non_zero = regions != 0
    regions[non_zero] = (regions[non_zero] + 1) // 2
    # velocity grid in round numbers of m / s
    magic_grid = mp.get_magic_grid(wavestart, waveend, binvelo * 1000)
    # put the line mask onto the magic grid to avoid errors at order overlaps
    magic_mask = np.zeros_like(magic_grid, dtype=bool)
    # find unique valid regions
    valid_regions = set(regions)
    valid_regions.remove(0)
    # loop around regions and fill magic mask
    for region in valid_regions:
        # find pixels that are in this region
        good = regions == region
        # find mask of minimum and maximum wavelength for this region
        minmask = magic_grid > np.min(wave1d[good])
        maxmask = magic_grid < np.max(wave1d[good])
        magic_mask[minmask & maxmask] = True
    # now in the space of magic grid work out the regions
    # build the region mask
    regions_magic = np.cumsum(magic_mask != np.roll(magic_mask, 1))
    # set all the even regions to zero
    regions_magic[(regions_magic % 2) == 0] = 0
    # re-number all non-zero regions to produce labels from 1--> N
    #   (original were all the odd numbers)
    non_zero_magic = regions_magic != 0
    regions_magic[non_zero_magic] = (regions_magic[non_zero_magic] + 1) // 2
    # fill the original map with unique values and common ID for overlapping
    #   orders
    regions = np.zeros_like(regions, dtype=int)
    # find unique valid regions
    valid_regions = set(regions_magic)
    valid_regions.remove(0)
    # loop around regions and fill
    for region in valid_regions:
        wave_min = np.min(magic_grid[regions_magic == region])
        wave_max = np.max(magic_grid[regions_magic == region])
        # find valid pixels in wavelength
        good = (wave1d > wave_min) & (wave1d < wave_max)
        # update the region id for these good pixels
        regions[good] = region
    # return updated sky props parameter dictionary
    return regions


def calc_skymodel(params: ParamDict, sky_props_sci: ParamDict,
                  sky_props_cal: ParamDict, regions: np.ndarray,
                  witerations: Optional[int] = None,
                  erode_size: Optional[int] = None) -> ParamDict:
    # set function name
    func_name = display_func('calc_skymodel', __NAME__)
    # -------------------------------------------------------------------------
    # get values from parameters
    weight_iterations = pcheck(params, 'SKYMODEL_WEIGHT_ITERS', func=func_name,
                               override=witerations)
    erode_size = pcheck(params, 'SKYMODEL_WEIGHT_ERODE_SIZE', func=func_name,
                        override=erode_size)
    # get cubes
    sci_cube = sky_props_sci['CUBE']
    cal_cube = sky_props_cal['CUBE']
    # get the reference wavelength solution
    waveref = sky_props_sci['WAVEMAP']
    # get the number of binned files
    nbins = sci_cube.shape[0]
    # deal with no calibration fiber data
    if cal_cube is None:
        cal_cube = np.zeros_like(sci_cube)
        has_cal = False
    else:
        has_cal = True
    # assume we always have sci
    has_sci = True
    # -------------------------------------------------------------------------
    # get pixel positions
    order_pix, x_pix = np.indices(waveref.shape)
    # ravel 2D arrays
    regions_rav = regions.ravel()
    # order_pix_rav = order_pix.ravel()
    x_pix_rav = x_pix.ravel()
    waveref_rav = waveref.ravel()
    # get unique regions
    unique_regions = set(regions)
    unique_regions.remove(0)
    # storage for the line fit
    fwhm_all, xpix_all, nsig_all = [], [], []
    model_sci = np.zeros_like(sky_props_sci['MED'])
    model_cal = np.zeros_like(sky_props_sci['MED'])
    all_sci_dict = dict()
    all_cal_dict = dict()
    # -------------------------------------------------------------------------
    # loop  around regions
    for region in unique_regions:
        # find pixels in this region
        region_mask = regions_rav == region
        # get length of the region
        region_length = np.sum(region_mask)
        # get the wavelength for this region
        region_wave = waveref_rav[region_mask]
        # make lists for this region
        all_sci, all_cal = [], []
        # construct new cubes by loop around all binned files
        for bin_it in range(nbins):
            # get this bins data (for this region)
            tmp_sci = sci_cube[bin_it][region_mask]
            tmp_cal = cal_cube[bin_it][region_mask]
            # work out the amplitude of the science fiber
            amp = np.nansum(tmp_sci)
            # add to list for this region
            all_sci.append(tmp_sci / amp)
            all_cal.append(tmp_cal / amp)
        # convert to numpy array and reshape
        all_sci = np.array(all_sci).reshape(nbins, region_length)
        all_cal = np.array(all_cal).reshape(nbins, region_length)
        # perform medians along axis 0
        med_sci = mp.nanmedian(all_sci, axis=0)
        med_cal = mp.nanmedian(all_cal, axis=0)
        # push medians into models
        model_sci[region_mask] = med_sci
        model_cal[region_mask] = med_cal
        # save all_sci and all_cal
        all_sci_dict[region] = all_sci
        all_cal_dict[region] = all_cal
        # calculate the line fit (if possible)
        # noinspection PyBroadException
        try:
            # calculate the dv step in km/s
            wavestep = (region_wave / np.mean(region_wave)) - 1
            dvstep = wavestep * speed_of_light
            # get the fwhm of the line
            guess = [0, np.max(med_sci), 4.0, 2.0, 0.0]
            # fit using curve fit
            # noinspection PyTupleAssignmentBalance
            fitcoeffs, _ = curve_fit(mp.super_gauss, dvstep, med_sci, p0=guess)
            # get the fwhm
            fwhm_all.append(fitcoeffs[2])
            # get the mean pixel position for this region
            xpix_all.append(np.mean(x_pix_rav[region_mask]))
            # work out fit using fit coefficients
            model = mp.super_gauss(dvstep, *fitcoeffs)
            # get the number of sigma this fit has away from the data
            nsig = fitcoeffs[1] / mp.nanstd(med_sci - model)
            nsig_all.append(nsig)
        # if we can't fit this region we skip it
        except:
            pass
    # -------------------------------------------------------------------------
    # only keep lines more prominent than 5 sigma
    keep = np.array(nsig_all) > 5
    xpix_all = np.array(xpix_all)[keep]
    fwhm_all = np.array(fwhm_all)[keep]
    nsig_all = np.array(nsig_all)[keep]
    # -------------------------------------------------------------------------
    # calculates weights given to each line
    weights = np.array(regions != 0, dtype=float)
    weights2 = np.array(weights)
    # iterate a few times to produce weights
    for _ in range(weight_iterations):
        # erode the weights
        weights2 = binary_erosion(weights2, structure=np.ones(erode_size))
        # add these to the final weights
        weights += np.array(weights2)
    # normalize weights
    weights = weights / np.max(weights)
    # -------------------------------------------------------------------------
    # reshape models and regions back to e2ds format
    model_sci = model_sci.reshape(waveref.shape)
    model_cal = model_cal.reshape(waveref.shape)
    regions = regions.reshape(waveref.shape)
    weights = weights.reshape(waveref.shape)
    # set to 0 negative values that are spuriuous for a sky flux
    model_sci[model_sci < 0] = 0.0
    model_cal[model_cal < 0] = 0.0
    # work out gradient of the science fiber model
    gradient = np.gradient(model_sci, axis=1)
    # -------------------------------------------------------------------------
    # create sky props
    sky_props = ParamDict()
    # add parameters to sky_props
    sky_props['HAS_SCI'] = has_sci
    sky_props['HAS_CAL'] = has_cal
    sky_props['SKYMODEL_SCI'] = model_sci
    sky_props['SKYMODEL_CAL'] = model_cal
    sky_props['WAVEMAP'] = waveref
    sky_props['REGION_ID'] = regions
    sky_props['WEIGHTS'] = weights
    sky_props['GRADIENT'] = gradient
    sky_props['SKYTABLE_SCI'] = sky_props_sci['TABLE']
    sky_props['SKYTABLE_CAL'] = sky_props_cal['TABLE']
    sky_props['ALL_SCI'] = all_sci_dict
    sky_props['ALL_CAL'] = all_cal_dict
    sky_props['XPIX_ALL'] = xpix_all
    sky_props['FWHM_ALL'] = fwhm_all
    sky_props['NSIG_ALL'] = nsig_all
    # set the source of sky_props to this function name
    keys = ['SKYMODEL_SCI', 'SKYMODEL_CAL', 'WAVEMAP', 'REGION_ID',
            'WEIGHTS', 'GRADIENT', 'SKYTABLE_SCI', 'SKYTABLE_CAL',
            'ALL_SCI', 'ALL_CAL', 'XPIX_ALL', 'FWHM_ALL', 'NSIG_ALL']
    sky_props.set_sources(keys, func_name)
    # return updated sky props parameter dictionary
    return sky_props


def mk_skymodel_qc(params: ParamDict, sky_props: ParamDict
                   ) -> Tuple[List[list], int]:
    # TODO: Fill out QC
    _ = sky_props
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # no quality control currently
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
    # return qc params and passed
    return qc_params, passed


def write_skymodel(recipe: DrsRecipe, params: ParamDict,
                   infile: DrsFitsFile, sky_props: ParamDict) -> DrsFitsFile:
    # ------------------------------------------------------------------
    # write the sky model file (SKYMODEL)
    # ------------------------------------------------------------------
    # get copy of instance of file
    skymodel_file = recipe.outputs['SKYMODEL'].newcopy(params=params)
    # construct the filename from file instance
    skymodel_file.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # copy keys from input file
    skymodel_file.copy_original_keys(infile, exclude_groups='wave')
    # ------------------------------------------------------------------
    # add version
    skymodel_file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    skymodel_file.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    skymodel_file.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    skymodel_file.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    skymodel_file.add_hkey('KW_OUTPUT', value=skymodel_file.name)

    # TODO: Add keys for valid SKY MODEL
    skymodel_file.add_hkey('KW_HAS_SKY_SCI', value=sky_props['HAS_SCI'])
    skymodel_file.add_hkey('KW_HAS_SKY_CAL', value=sky_props['HAS_CAL'])

    # ------------------------------------------------------------------
    # set data = sky
    skymodel_file.data = sky_props['SKYMODEL_SCI']
    # log that we are saving s1d table
    msg = 'Saving sky model file to: {0}'
    margs = [skymodel_file.filename]
    WLOG(params, '', msg.format(*margs))
    # define multi lists
    data_list = [sky_props['SKYMODEL_CAL'], sky_props['WAVEMAP'],
                 sky_props['REGION_ID'], sky_props['WEIGHTS'],
                 sky_props['GRADIENT'], sky_props['SKYTABLE_SCI'],
                 sky_props['SKYTABLE_CAL']]
    datatype_list = ['image', 'image', 'image', 'image', 'image',
                     'table', 'table']
    name_list = ['SCI_SKY', 'CAL_SKY', 'WAVE', 'REG_ID', 'WEIGHTS',
                 'GRADIENT', 'SKYTAB_SCI', 'SKYTAB_CAL']
    # ------------------------------------------------------------------
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=skymodel_file)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write multi
    skymodel_file.write_multi(data_list=data_list, name_list=name_list,
                              datatype_list=datatype_list,
                              block_kind=recipe.out_block_str,
                              runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(skymodel_file)
    # return sky model
    return skymodel_file


def mk_skymodel_summary(recipe, params, sky_props: ParamDict, qc_params):
    # TODO: Write skymodel summary
    _ = sky_props
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('', value=None)
    # construct summary
    recipe.plot.summary_document(0, qc_params)


# =============================================================================
# Correction skycorr functions
# =============================================================================
def correct_sky_with_ref(params: ParamDict, recipe: DrsRecipe,
                         infile: DrsFitsFile, wprops: ParamDict,
                         rawfiles: List[str], combine: bool,
                         calibdbm: Optional[CalibrationDatabase] = None,
                         telludbm: Optional[TelluricDatabase] = None
                         ) -> ParamDict:
    """
    Correct a observation for sky-lines when observation has a sky in the
    reference fiber

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe class that called this function
    :param infile: DrsFitsFile, the fits file instance to correct sky on
    :param wprops: ParamDict, the wave solution associated with infile
    :param rawfiles: List[str], list of raw filenames
    :param combine: bool, if True input has been combined
    :param calibdbm: CalibrationDatabase instance (if none is reloaded)
    :param telludbm: TelluricDatabase instance (if none is reloaded)
    :return:
    """
    # set function name
    func_name = display_func('correct_sky', __NAME__)
    # get parameters from Params
    # weight_iters = pcheck(params, 'SKYCORR_WEIGHT_ITERATIONS')  # = 5
    lowpass_size1 = pcheck(params, 'SKYCORR_LOWPASS_SIZE1')  # = 51
    lowpass_size2 = pcheck(params, 'SKYCORR_LOWPASS_SIZE2')  # = 101
    lowpass_itrs = pcheck(params, 'SKYCORR_LOWPASS_ITERATIONS')  # = 2
    nsig_thres = pcheck(params, 'SKYCORR_NSIG_THRES')  # = 3
    # -------------------------------------------------------------------------
    # deal with no calibration database
    if calibdbm is None:
        calibdbm = CalibrationDatabase(params)
        calibdbm.load_db()
    # deal with no telluric database
    if telludbm is None:
        telludbm = TelluricDatabase(params)
        telludbm.load_db()
    # -------------------------------------------------------------------------
    # load psuedo constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get the science and calib fiber names
    sci_fibers, calib_fiber = pconst.FIBER_KINDS()
    # find the reference (calibration) fiber file
    infile_calib = drs_file.locate_calibfiber_file(params, infile)
    # get the wave solution associated with this file
    wprops_calib = wave.get_wavesolution(params, recipe, fiber=calib_fiber,
                                         infile=infile_calib,
                                         database=calibdbm)
    # -------------------------------------------------------------------------
    # copy the science image
    image_sci = np.array(infile.data)
    # copy the reference image
    image_calib = np.array(infile_calib.data)
    # -------------------------------------------------------------------------
    # load sky model from telluric database
    sc_props = get_sky_model(params, infile.header, infile.fiber,
                             telludbm)
    # extract properties from sky model (and deep copy)
    sky_wavemap = np.array(sc_props['SKY_WAVEMAP'])
    sky_model_sci = np.array(sc_props['SKY_MODEL_SCI'])
    sky_model_ref = np.array(sc_props['SKY_MODEL_REF'])
    reg_id = np.array(sc_props['SKY_REG_ID'])
    weights = np.array(sc_props['SKY_WEIGHTS'])
    # record the shape of e2ds
    nbo, nbxpix = sky_model_sci.shape
    # -------------------------------------------------------------------------
    # loop around orders and map the calib fiber on to the reference calib fiber
    for order_num in range(nbo):
        # get the calib image for this order
        spord = image_calib[order_num]
        wave_ord = wprops_calib['WAVEMAP'][order_num]
        # low pass the calib fiber image
        lowpass1 = mp.lowpassfilter(spord, lowpass_size1)
        spord = spord - lowpass1
        # perform a sigma clipping and low pass more times
        for _ in range(lowpass_itrs):
            # calculate the number of sigmas away from median
            nsig = spord / mp.estimate_sigma(spord)
            # mask those values more than nsig_thres away in sigma away from
            #   the median
            sigmask = np.zeros_like(nsig)
            sigmask[nsig > nsig_thres] = np.nan
            # low pass filter given this sig mask
            lowpass2 = mp.lowpassfilter(spord + sigmask, lowpass_size2)
            spord = spord - lowpass2
        # map image calib onto reference wave solution grid
        ord_spline = mp.iuv_spline(wave_ord, spord)
        # overwrite image_calib with updated values
        image_calib[order_num] = ord_spline(sky_wavemap[order_num])
    # -------------------------------------------------------------------------
    # create a model scaled to the image calib fiber data
    # -------------------------------------------------------------------------
    # create vectors for the sky correction
    sky_corr_sci = np.zeros_like(image_sci)
    sky_corr_ref = np.zeros_like(image_calib)
    # find unique region ids
    region_ids = set(np.unique(reg_id))
    # remove 0 (this means no line)
    region_ids.remove(0)
    # create a finite mask
    finite_mask = np.isfinite(image_calib)
    finite_mask &= np.isfinite(sky_model_ref)
    # loop around each line
    for region_id in region_ids:
        # mask all areas with this region id
        reg_mask = reg_id == region_id
        # make sure calib and model are finite
        reg_maskf = reg_mask & finite_mask
        # fit amplitude in calib fiber and apply to science fiber
        amp_num = np.sum(image_calib[reg_maskf] * sky_model_ref[reg_maskf])
        amp_den = np.sum(sky_model_ref[reg_maskf] ** 2)
        amp = amp_num / amp_den
        # negative amps should be set to zero
        if amp < 0:
            amp = 0
        # apply to weights and scale (including areas with nans)
        sfactor = amp * weights[reg_mask]
        sky_corr_sci[reg_mask] = sky_model_sci[reg_mask] * sfactor
        sky_corr_ref[reg_mask] = sky_model_ref[reg_mask] * sfactor
    # -------------------------------------------------------------------------
    # spline back to the input files wavelength grid
    for order_num in range(nbo):
        # keyword arguments for splines
        spkwargs_s = dict(x=sky_wavemap[order_num], y=sky_corr_sci[order_num],
                          ext=1, k=3)
        spkwargs_c = dict(x=sky_wavemap[order_num], y=sky_corr_ref[order_num],
                          ext=1, k=3)
        # make splines
        sci_spline = mp.iuv_spline(**spkwargs_s)
        ref_spline = mp.iuv_spline(**spkwargs_c)
        # update sky_corr for science and calibration
        sky_corr_sci[order_num] = sci_spline(wprops['WAVEMAP'][order_num])
        sky_corr_ref[order_num] = ref_spline(wprops_calib['WAVEMAP'][order_num])
    # -------------------------------------------------------------------------
    # re-copy the science image
    image_sci = np.array(infile.data)
    # copy the reference image
    image_calib = np.array(infile_calib.data)
    # save to dict
    sc_props[f'CORR_EXT_{infile.fiber}'] = image_sci - sky_corr_sci
    sc_props[f'CORR_EXT_{calib_fiber}'] = image_calib - sky_corr_ref
    sc_props[f'UNCORR_EXT_{infile.fiber}'] = image_sci
    sc_props[f'UNCORR_EXT_{calib_fiber}'] = image_calib
    sc_props['SKY_CORR_SCI'] = sky_corr_sci
    sc_props['SKY_CORR_REF'] = sky_corr_ref
    sc_props['SCI_FIBER'] = infile.fiber
    sc_props['REF_FIBER'] = calib_fiber
    sc_props['WAVE_SCI'] = wprops['WAVEMAP']
    sc_props['WAVE_REF'] = wprops_calib['WAVEMAP']
    # set source
    keys = [f'CORR_EXT_{infile.fiber}', f'CORR_EXT_{calib_fiber}',
            f'UNCORR_EXT_{infile.fiber}', f'UNCORR_EXT_{calib_fiber}',
            'SKY_CORR_SCI', 'SKY_CORR_REF', 'SCI_FIBER', 'REF_FIBER',
            'WAVE_SCI', 'WAVE_REF']
    sc_props.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    objname = infile.get_hkey('KW_OBJNAME')
    dprtype = infile.get_hkey('KW_DPRTYPE')
    # plot
    recipe.plot('TELLU_SKY_CORR_PLOT', props=sc_props, objname=objname,
                dprtype=dprtype)
    # -------------------------------------------------------------------------
    # write debug file
    skyclean_write(params, recipe, infile, rawfiles, combine, wprops, sc_props)
    # -------------------------------------------------------------------------
    # return sky parameter dictionary
    return sc_props


def correct_sky_no_ref(params: ParamDict, recipe: DrsRecipe,
                       infile: DrsFitsFile, wprops: ParamDict,
                       rawfiles: List[str], combine: bool,
                       calibdbm: Optional[CalibrationDatabase] = None,
                       telludbm: Optional[TelluricDatabase] = None
                       ) -> ParamDict:
    """
    Correct a observation for sky-lines when observation has a sky in the
    reference fiber

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe class that called this function
    :param infile: DrsFitsFile, the fits file instance to correct sky on
    :param wprops: ParamDict, the wave solution associated with infile
    :param rawfiles: List[str], list of raw filenames
    :param combine: bool, if True input has been combined
    :param calibdbm: CalibrationDatabase instance (if none is reloaded)
    :param telludbm: TelluricDatabase instance (if none is reloaded)
    :return:
    """
    # set function name
    func_name = display_func('correct_sky', __NAME__)
    # -------------------------------------------------------------------------
    # deal with no calibration database
    if calibdbm is None:
        calibdbm = CalibrationDatabase(params)
        calibdbm.load_db()
    # deal with no telluric database
    if telludbm is None:
        telludbm = TelluricDatabase(params)
        telludbm.load_db()
    # -------------------------------------------------------------------------
    # load psuedo constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get the science and calib fiber names
    sci_fibers, calib_fiber = pconst.FIBER_KINDS()
    # -------------------------------------------------------------------------
    # copy the science image
    image = np.array(infile.data)
    # copy the science wave map
    wavemap = np.array(wprops['WAVEMAP'])
    # -------------------------------------------------------------------------
    # load sky model from telluric database
    sc_props = get_sky_model(params, infile.header, infile.fiber,
                             telludbm)
    # extract properties from sky model (and deep copy)
    sky_wavemap = np.array(sc_props['SKY_WAVEMAP'])
    sky_model_sci = np.array(sc_props['SKY_MODEL_SCI'])
    sky_model_ref = np.array(sc_props['SKY_MODEL_REF'])
    reg_id = np.array(sc_props['SKY_REG_ID'])
    weights = np.array(sc_props['SKY_WEIGHTS'])
    gradient = np.array(sc_props['SKY_GRADIENT'])
    # -------------------------------------------------------------------------
    # shift the image on to the sky wave grid
    image1 = gen_tellu.wave_to_wave(params, image, wavemap, sky_wavemap,
                                    reshape=True)

    # TODO subtract template here. Each order is scaled to its median. OH lines
    # TODO contribute very little to the median flux, so this is fine

    # find the gradients of this image
    grad = np.gradient(image1, axis=1)
    # -------------------------------------------------------------------------
    # create a model scaled to the image calib fiber data
    # -------------------------------------------------------------------------
    # create vectors for the sky correction
    sky_corr_sci1 = np.zeros_like(image1)
    # find unique region ids
    region_ids = set(np.unique(reg_id))
    # remove 0 (this means no line)
    region_ids.remove(0)
    # create a finite mask
    finite_mask = np.isfinite(image1)
    finite_mask &= np.isfinite(sky_model_ref)
    # loop around each line
    for region_id in region_ids:
        # mask all areas with this region id
        reg_mask = reg_id == region_id
        # make sure calib and model are finite
        reg_maskf = reg_mask & finite_mask
        # get the gradients for this region
        grad1 = grad[reg_maskf]
        grad1_ref = gradient[reg_maskf]
        # dot product of the gradients
        amp = np.nansum(grad1 * grad1_ref) / np.nansum(grad1_ref ** 2)
        # negative amps should be set to zero
        if amp < 0:
            amp = 0
        # apply to weights and scale (including areas with nans)
        sfactor = amp * weights[reg_mask]
        sky_corr_sci1[reg_mask] = sky_model_sci[reg_mask] * sfactor
    # -------------------------------------------------------------------------
    # shift the image back to the original wave grid
    sky_corr_sci = gen_tellu.wave_to_wave(params, sky_corr_sci1, sky_wavemap,
                                          wavemap, reshape=True)
    # set nans to zeros
    sky_corr_sci[np.isnan(sky_corr_sci)] = 0.0
    # -------------------------------------------------------------------------
    # re-copy the science image
    image_sci = np.array(infile.data)
    # save to dict
    sc_props[f'CORR_EXT_{infile.fiber}'] = image_sci - sky_corr_sci
    sc_props[f'CORR_EXT_{calib_fiber}'] = None
    sc_props[f'UNCORR_EXT_{infile.fiber}'] = image_sci
    sc_props[f'UNCORR_EXT_{calib_fiber}'] = None
    sc_props['SKY_CORR_SCI'] = sky_corr_sci
    sc_props['SKY_CORR_REF'] = None
    sc_props['SCI_FIBER'] = infile.fiber
    sc_props['REF_FIBER'] = calib_fiber
    sc_props['WAVE_SCI'] = wprops['WAVEMAP']
    sc_props['WAVE_REF'] = sky_wavemap
    # set source
    keys = [f'CORR_EXT_{infile.fiber}', f'CORR_EXT_{calib_fiber}',
            f'UNCORR_EXT_{infile.fiber}', f'UNCORR_EXT_{calib_fiber}',
            'SKY_CORR_SCI', 'SKY_CORR_REF', 'SCI_FIBER', 'REF_FIBER',
            'WAVE_SCI', 'WAVE_REF']
    sc_props.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # plot sky correction plot
    recipe.plot('TELLU_SKY_CORR_PLOT', props=sc_props,
                objname=infile.get_hkey('KW_OBJNAME'),
                dprtype=infile.get_hkey('KW_DPRTYPE'))
    # -------------------------------------------------------------------------
    # write debug file
    skyclean_write(params, recipe, infile, rawfiles, combine, wprops, sc_props)
    # -------------------------------------------------------------------------
    # return sky parameter dictionary
    return sc_props


def get_sky_model(params: ParamDict, header: drs_fits.Header, fiber: str,
                  database: Optional[drs_database.TelluricDatabase] = None
                  ) -> ParamDict:
    """
    Get the sky model from the telluric database

    :param params: ParamDict, parameter dictionary of constants
    :param header: fits.Header, header of input file
    :param fiber: str, the fiber name
    :param database: telluric database instance or None, if None
                     reloads database

    :return: sky correction parameter dictionary
    """
    # set function name
    func_name = display_func('get_sky_model', __NAME__)
    # get file definition
    out_sky_model = drs_file.get_file_definition(params, 'SKY_MODEL',
                                                 block_kind='red', fiber=fiber)
    # get key
    sky_key = out_sky_model.get_dbkey()
    # log status
    WLOG(params, '', textentry('40-019-00046', args=[sky_key]))
    # load tellu file, header and abspaths
    sky_model = gen_tellu.load_tellu_file(params, sky_key, header,
                                          fiber=fiber, n_entries=1,
                                          get_image=False, database=database,
                                          return_filename=True)
    # load extensions
    exts, extnames = drs_fits.readfits(params, sky_model, getdata=True,
                                       fmt='fits-multi', return_names=True)
    # push into dictionary
    extdict = dict(zip(extnames, exts))
    # push into parameter dictionary
    props = ParamDict()
    props['SKY_MODEL_SCI'] = extdict['SCI_SKY']
    props['SKY_MODEL_REF'] = extdict['CAL_SKY']
    props['SKY_REG_ID'] = extdict['REG_ID']
    props['SKY_WAVEMAP'] = extdict['WAVE']
    props['SKY_WEIGHTS'] = extdict['WEIGHTS']
    props['SKY_GRADIENT'] = extdict['GRADIENT']
    props['SKY_MODEL_FILE'] = sky_model
    # set source
    keys = ['SKY_MODEL_SCI', 'SKY_MODEL_REF', 'SKY_REG_ID', 'SKY_WAVEMAP',
            'SKY_MODEL_FILE', 'SKY_WEIGHTS', 'SKY_GRADIENT']
    props.set_sources(keys, func_name)
    # return all valid sorted in time
    return props


def skyclean_write(params: ParamDict, recipe: DrsRecipe, infile: DrsFitsFile,
                   rawfiles: List[str],
                   combine: bool, wprops: ParamDict, props: ParamDict):
    """
    Write the sky cleaning file to disk

    :param params: ParamDict, parameter dictionary on constants
    :param recipe: DrsRecipe, recipe instance that called this function
    :param infile: DrsFitsFile, the input fits file that was corrected
    :param rawfiles: list of strings, list of input files
    :param combine: bool, if True combined inputs
    :param wprops: Wave solution (science fiber) parameter dictionary
    :param props: Sky Correction parameter dictionary

    :return: None, writes file to disk
    """
    # get fibers
    sci_fiber = props['SCI_FIBER']
    calib_fiber = props['REF_FIBER']
    # -------------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    skyfile = recipe.outputs['TELLU_SCLEAN'].newcopy(params=params,
                                                     fiber=sci_fiber)
    # construct the filename from file instance
    skyfile.construct_filename(infile=infile)
    # -------------------------------------------------------------------------
    # copy keys from input file
    skyfile.copy_original_keys(infile)
    # add core values (that should be in all headers)
    skyfile.add_core_hkeys(params)
    # add input files (and deal with combining or not combining)
    if combine:
        infiles = rawfiles
    else:
        infiles = [infile.basename]
    skyfile.add_hkey_1d('KW_INFILE1', values=infiles, dim1name='file')
    # add infiles to outfile
    skyfile.infiles = list(infiles)
    # add  calibration files used
    skyfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    skyfile.add_hkey('KW_TDBSKY',
                     value=os.path.basename(props['SKY_MODEL_FILE']))
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', textentry('40-019-00044', args=[skyfile.filename]))
    # define multi lists
    data_list = [props[f'CORR_EXT_{calib_fiber}'],
                 props[f'UNCORR_EXT_{sci_fiber}'],
                 props[f'UNCORR_EXT_{calib_fiber}'],
                 props['SKY_CORR_SCI'],
                 props['SKY_CORR_REF']]
    name_list = [f'CORR_EXT_{sci_fiber}', f'CORR_EXT_{calib_fiber}',
                 f'UNCORR_EXT_{sci_fiber}', f'UNCORR_EXT_{calib_fiber}',
                 f'SKY_{sci_fiber}', f'SKY_{calib_fiber}']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=skyfile)]
        name_list += ['PARAM_TABLE']
    # write to file
    skyfile.data = props[f'CORR_EXT_{sci_fiber}']
    skyfile.write_multi(data_list=data_list, name_list=name_list,
                        block_kind=recipe.out_block_str,
                        runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(skyfile)


# =============================================================================
# Worker functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

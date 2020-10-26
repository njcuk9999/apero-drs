#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:16

@author: cook
"""
from astropy import constants as cc
from astropy import units as uu
from astropy.table import Table
import numpy as np
import os
from scipy.optimize import curve_fit
from typing import List, Tuple, Union
import warnings

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_startup
from apero.core.utils import drs_data
from apero.core.utils import drs_utils
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.science.calib import flat_blaze

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.general.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# get calibration database
TelluDatabase = drs_database.TelluricDatabase
IndexDatabase = drs_database.IndexDatabase
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define functions
# =============================================================================
def get_whitelist(params: ParamDict, **kwargs) -> List[str]:
    func_name = __NAME__ + '.get_whitelist()'
    # get pseudo constants
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_WHITELIST_NAME', 'filename', kwargs,
                      func_name)
    # get absolulte filename
    whitelistfile = os.path.join(assetdir, relfolder, filename)
    # load the white list
    whitelist = drs_data.load_text_file(params, whitelistfile, func_name,
                                        dtype=str)
    # must clean names
    whitelist = list(map(pconst.DRS_OBJ_NAME, whitelist))
    # return the whitelist
    return whitelist


def get_blacklist(params, **kwargs):
    func_name = __NAME__ + '.get_blacklist()'
    # get pseudo constants
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_BLACKLIST_NAME', 'filename', kwargs,
                      func_name)
    # get absolulte filename
    blacklistfile = os.path.join(assetdir, relfolder, filename)
    # load the white list
    blacklist = drs_data.load_text_file(params, blacklistfile, func_name,
                                        dtype=str)
    # must clean names
    blacklist = list(map(pconst.DRS_OBJ_NAME, blacklist))
    # return the whitelist
    return blacklist, blacklistfile


def normalise_by_pblaze(params, image, header, fiber, **kwargs):
    func_name = __NAME__ + '.normalise_by_pblaze()'
    # get properties from params/kwargs
    blaze_p = pcheck(params, 'MKTELLU_BLAZE_PERCENTILE', 'blaze_p', kwargs,
                     func_name)
    cut_blaze_norm = pcheck(params, 'MKTELLU_CUT_BLAZE_NORM', 'cut_blaze_norm',
                            kwargs, func_name)
    # ----------------------------------------------------------------------
    # copy the image
    image1 = np.array(image)
    # ----------------------------------------------------------------------
    # load the blaze file for this fiber
    blaze_file, blaze = flat_blaze.get_blaze(params, header, fiber)
    # copy blaze
    blaze_norm = np.array(blaze)
    # loop through blaze orders, normalize blaze by its peak amplitude
    for order_num in range(image1.shape[0]):
        # normalize the spectrum
        spo, bzo = image1[order_num], blaze[order_num]
        # normalise image
        image1[order_num] = spo / np.nanpercentile(spo, blaze_p)
        # normalize the blaze
        blaze_norm[order_num] = bzo / np.nanpercentile(bzo, blaze_p)
    # ----------------------------------------------------------------------
    # find where the blaze is bad
    with warnings.catch_warnings(record=True) as _:
        badblaze = blaze_norm < cut_blaze_norm
    # ----------------------------------------------------------------------
    # set bad blaze to NaN
    blaze_norm[badblaze] = np.nan
    # set to NaN values where spectrum is zero
    zeromask = image1 == 0
    image1[zeromask] = np.nan
    # divide spectrum by blaze
    with warnings.catch_warnings(record=True) as _:
        image1 = image1 / blaze_norm
    # ----------------------------------------------------------------------
    # parameter dictionary
    nprops = ParamDict()
    nprops['BLAZE'] = blaze
    nprops['NBLAZE'] = blaze_norm
    nprops['BLAZE_PERCENTILE'] = blaze_p
    nprops['BLAZE_CUT_NORM'] = cut_blaze_norm
    nprops['BLAZE_FILE'] = blaze_file
    # set sources
    keys = ['BLAZE', 'NBLAZE', 'BLAZE_PERCENTILE', 'BLAZE_CUT_NORM',
            'BLAZE_FILE']
    nprops.set_sources(keys, func_name)
    # return the normalised image and the properties
    return image1, nprops


def get_non_tellu_objs(params: ParamDict, recipe, fiber, filetype=None,
                       dprtypes=None, robjnames: List[str] = None,
                       indexdbm: Union[IndexDatabase, None] = None):
    """
    Get the objects of "filetype" and that are not telluric objects
    :param params: ParamDict - the parameter dictionary of constants
    :param recipe: DrsRecipe
    :param fiber:
    :param filetype:
    :param dprtypes:
    :param robjnames: list of strings - a list of all object names (only return
                      if found and in this list

    :return:
    """
    # get the telluric star names (we don't want to process these)
    objnames = get_whitelist(params)
    objnames = list(objnames)
    # deal with filetype being string
    if isinstance(filetype, str):
        filetype = filetype.split(',')
        filetype = np.char.array(filetype).strip()
    # deal with dprtypes being string
    if isinstance(dprtypes, str):
        dprtypes = dprtypes.split(',')
        dprtypes = np.char.array(dprtypes).strip()
    # construct kwargs
    fkwargs = dict()
    if filetype is not None:
        fkwargs['KW_OUTPUT'] = filetype
    if dprtypes is not None:
        fkwargs['KW_DPRTYPE'] = dprtypes
    if fiber is not None:
        fkwargs['KW_FIBER'] = fiber
    # find files (and return pandas dataframe of all columns
    dataframe = drs_utils.find_files(params, kind='red', filters=fkwargs,
                                     columns='*', indexdbm=indexdbm)
    # convert data frame to table
    obj_table = Table.from_pandas(dataframe)
    obj_filenames = obj_table['PATH']
    # filter out telluric stars
    obj_stars, obj_names = [], []
    # loop around object table and only keep non-telluric stars
    for row in range(len(obj_table)):
        # get object name
        iobjname = obj_table['KW_OBJNAME'][row]
        # if required object name is set
        if robjnames is not None:
            if iobjname in robjnames:
                obj_stars.append(obj_filenames[row])
                if iobjname not in obj_names:
                    obj_names.append(iobjname)
        # if in telluric list skip
        elif iobjname not in objnames:
            obj_stars.append(obj_filenames[row])
            if iobjname not in obj_names:
                obj_names.append(iobjname)
    # return absolute path names and object names
    return obj_stars, obj_names


def get_tellu_objs(params: ParamDict, key: str,
                   objnames: Union[List[str], str, None] = None,
                   database: Union[TelluDatabase, None] = None) -> List[str]:
    """
    Get objects defined by "key" from telluric database (in list objname)

    :param params: ParamDict, the parameter dictionary of constants
    :param key: str, the database key to filter telluric database entries by
    :param objnames: str or list of strings, the object names to filter
                     the telluric database 'OBJECT' column by
    :param database: TelluricDatabase instance or None, if set does not have to
                     load database

    :return: list of strings, the absolute filenames for database entries of
             KEY == 'key' and OBJECT in 'objnames'
    """
    _ = display_func(params, 'get_tellu_objs', __NAME__)
    # ----------------------------------------------------------------------
    # deal with objnames
    if objnames is None:
        objnames = []
    if isinstance(objnames, str):
        objnames = [objnames]
    # ----------------------------------------------------------------------
    # deal with not having database
    if database is None:
        database = TelluDatabase(params)
        # load database
        database.load_db()
    # ----------------------------------------------------------------------
    # get all obj_entries from the telluric database
    table = database.get_tellu_entry('FILENAME, OBJECT', key=key)
    # ----------------------------------------------------------------------
    # deal with no objects found
    if len(table) == 0:
        return []
    # ----------------------------------------------------------------------
    # filter by objnames (set by input)
    mask = np.zeros(len(table)).astype(bool)
    for objname in objnames:
        mask |= np.array(table['OBJECT'] == objname)
    # get base filenames with this mask
    # noinspection PyTypeChecker
    filenames = list(table['FILENAME'][mask])
    # ----------------------------------------------------------------------
    # make path absolute
    absfilenames = []
    for filename in filenames:
        # construct absolute path
        absfilename = database.filedir.joinpath(filename)
        # check exists
        if absfilename.exists():
            absfilenames.append(str(absfilename))
    # ----------------------------------------------------------------------
    # display how many files found
    margs = [len(absfilenames), key]
    WLOG(params, '', TextEntry('40-019-00039', args=margs))
    return absfilenames


def get_sp_linelists(params, **kwargs):
    func_name = __NAME__ + '.get_sp_linelists()'
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    othersfile = pcheck(params, 'TELLUP_OTHERS_CCF_FILE', 'filename', kwargs,
                        func_name)
    waterfile = pcheck(params, 'TELLUP_H2O_CCF_FILE', 'filename', kwargs,
                       func_name)
    # load the others file list
    mask_others, _ = drs_data.load_ccf_mask(params, directory=relfolder,
                                            filename=othersfile)
    mask_water, _ = drs_data.load_ccf_mask(params, directory=relfolder,
                                           filename=waterfile)
    # return masks
    return mask_others, mask_water


# =============================================================================
# pre-cleaning functions
# =============================================================================
def tellu_preclean(params, recipe, infile, wprops, fiber, rawfiles, combine,
                   database: Union[TelluDatabase, None] = None, **kwargs):
    """
    Main telluric pre-cleaning functionality.

    Pass an e2ds  image and return the telluric-corrected data.
    This is a rough model fit and we will need to perform PCA correction on
    top of it.

    Will fit both water and all dry components of the absorption separately.

    Underlying idea: We correct with a super naive tapas fit and iterate
    until the CCF of the telluric absorption falls to zero. We have 2 degrees
    of freedom, the dry and water components of the atmosphere.
    The instrument profile is defined by two additional parameters
    [ww -> FWHM, ex_gau -> kernel shape parameter].

    Again, this is just a cleanup PRIOR to PCA correction, so if the code is
    not perfect in it's correction, this is fine as we will empirically
    determine the residuals and fit them in a subsequent step.

    we set bounds to the limits of the reasonable domain for both parameters.

    :param params:
    :param recipe:
    :param infile:
    :param wprops:
    :param fiber:
    :param rawfiles:
    :param combine:
    :param database:

    :return:
    """
    # set the function name
    func_name = __NAME__ + '.tellu_preclean()'
    # ----------------------------------------------------------------------
    # look for precleaned file
    loadprops = read_tellu_preclean(params, recipe, infile, fiber,
                                    database=database)
    # if precleaned load and return
    if loadprops is not None:
        return loadprops
    # ----------------------------------------------------------------------
    # get parameters from parameter dictionary
    do_precleaning = pcheck(params, 'TELLUP_DO_PRECLEANING', 'do_precleaning',
                            kwargs, func_name)
    default_water_abso = pcheck(params, 'TELLUP_D_WATER_ABSO',
                                'default_water_abso', kwargs, func_name)
    ccf_scan_range = pcheck(params, 'TELLUP_CCF_SCAN_RANGE', 'ccf_scan_range',
                            kwargs, func_name)
    clean_ohlines = pcheck(params, 'TELLUP_CLEAN_OH_LINES', 'clean_ohlines',
                           kwargs, func_name)

    remove_orders = pcheck(params, 'TELLUP_REMOVE_ORDS', 'remove_orders',
                           kwargs, func_name, mapf='list', dtype=int)
    snr_min_thres = pcheck(params, 'TELLUP_SNR_MIN_THRES', 'snr_min_thres',
                           kwargs, func_name)
    dexpo_thres = pcheck(params, 'TELLUP_DEXPO_CONV_THRES', 'dexpo_thres',
                         kwargs, func_name)
    max_iterations = pcheck(params, 'TELLUP_DEXPO_MAX_ITR', 'max_iterations',
                            kwargs, func_name)
    ker_width = pcheck(params, 'TELLUP_ABSO_EXPO_KWID', 'ker_width', kwargs,
                       func_name)
    ker_shape = pcheck(params, 'TELLUP_ABSO_EXPO_KEXP', 'ker_shape', kwargs,
                       func_name)
    trans_thres = pcheck(params, 'TELLUP_TRANS_THRES', 'trans_thres', kwargs,
                         func_name)
    trans_siglim = pcheck(params, 'TELLUP_TRANS_SIGLIM', 'trans_siglim', kwargs,
                          func_name)
    force_airmass = pcheck(params, 'TELLUP_FORCE_AIRMASS', 'force_airmass',
                           kwargs, func_name)
    others_bounds = pcheck(params, 'TELLUP_OTHER_BOUNDS', 'others_bounds',
                           kwargs, func_name, mapf='list', dtype=float)
    water_bounds = pcheck(params, 'TELLUP_WATER_BOUNDS', 'water_bounds', kwargs,
                          func_name, mapf='list', dtype=float)
    ker_thres = pcheck(params, 'TELLUP_ABSO_EXPO_KTHRES', 'ker_thres', kwargs,
                       func_name)
    wavestart = pcheck(params, 'EXT_S1D_WAVESTART', 'wavestart', kwargs,
                       func_name)
    waveend = pcheck(params, 'EXT_S1D_WAVEEND', 'waveend', kwargs, func_name)
    dvgrid = pcheck(params, 'EXT_S1D_BIN_UVELO', 'dvgrid', kwargs, func_name)
    # ----------------------------------------------------------------------
    # get image and header from infile
    header = infile.get_header()
    # get airmass from header
    hdr_airmass = infile.get_hkey('KW_AIRMASS', dtype=float)
    # copy e2ds input image
    image_e2ds_ini = infile.get_data(copy=True)
    # get shape of the e2ds
    nbo, nbpix = image_e2ds_ini.shape
    # get wave map for the input e2ds
    wave_e2ds = wprops['WAVEMAP']
    # ----------------------------------------------------------------------
    # define storage of quality control
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # need to add dummy values for these qc

    # 1. snr < snr_min_thres (pos = 0)
    qc_values.append(np.nan)
    qc_names.append('EXTSNR')
    qc_logic.append('EXTSNR < {0}'.format(snr_min_thres))
    qc_pass.append(np.nan)
    # 2. ccf is NaN (pos = 1)
    qc_values.append(np.nan)
    qc_names.append('NUM_NAN_CCF')
    qc_logic.append('NUM_NAN_CCF > 0')
    qc_pass.append(np.nan)
    # 3. exponent for others out of bounds (pos = 2 and 3)
    qc_values += [np.nan, np.nan]
    qc_names += ['EXPO_OTHERS L', 'EXPO_OTHERS U']
    qc_logic += ['EXPO_OTHERS L < {0}'.format(others_bounds[0]),
                 'EXPO_OTHERS U > {0}'.format(others_bounds[1])]
    qc_pass += [np.nan, np.nan]
    # 4. exponent for water  out of bounds (pos 4 and 5)
    qc_values += [np.nan, np.nan]
    qc_names += ['EXPO_WATER L', 'EXPO_WATER U']
    qc_logic += ['EXPO_WATER L < {0}'.format(water_bounds[0]),
                 'EXPO_WATER U > {0}'.format(water_bounds[1])]
    qc_pass += [np.nan, np.nan]
    # 5. max iterations exceeded (pos = 6)
    qc_values.append(np.nan)
    qc_names.append('ITERATIONS')
    qc_logic.append('ITERATIONS = {0}'.format(max_iterations - 1))
    qc_pass.append(np.nan)
    # dev note: if adding a new one must add tfailmsgs for all uses in qc
    #  (mk_tellu and fit_tellu)
    # ----------------------------------------------------------------------
    # remove OH lines if required
    if clean_ohlines:
        image_e2ds, sky_model = clean_ohline_pca(params, image_e2ds_ini,
                                                 wave_e2ds)
    # else just copy the image and set the sky model to zeros
    else:
        image_e2ds = np.array(image_e2ds_ini)
        sky_model = np.zeros_like(image_e2ds_ini)
    # ----------------------------------------------------------------------
    if not do_precleaning:
        # log progress
        WLOG(params, '', TextEntry('10-019-00008'))
        # populate qc params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # populate parameter dictionary
        props = ParamDict()
        props['CORRECTED_E2DS'] = image_e2ds
        props['TRANS_MASK'] = np.ones_like(image_e2ds_ini).astype(bool)
        props['ABSO_E2DS'] = np.ones_like(image_e2ds_ini)
        props['SKY_MODEL'] = sky_model
        props['EXPO_WATER'] = np.nan
        props['EXPO_OTHERS'] = np.nan
        props['DV_WATER'] = np.nan
        props['DV_OTHERS'] = np.nan
        props['CCFPOWER_WATER'] = np.nan
        props['CCFPOWER_OTHERS'] = np.nan
        props['QC_PARAMS'] = qc_params
        # set sources
        keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
                'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'CCFPOWER_WATER',
                'CCFPOWER_OTHERS', 'QC_PARAMS', 'SKY_MODEL']
        props.set_sources(keys, func_name)
        # ------------------------------------------------------------------
        # add constants used (can come from kwargs)
        props['TELLUP_DO_PRECLEANING'] = do_precleaning
        props['TELLUP_D_WATER_ABSO'] = default_water_abso
        props['TELLUP_CCF_SCAN_RANGE'] = ccf_scan_range
        props['TELLUP_CLEAN_OH_LINES'] = clean_ohlines
        props['TELLUP_REMOVE_ORDS'] = remove_orders
        props['TELLUP_SNR_MIN_THRES'] = snr_min_thres
        props['TELLUP_DEXPO_CONV_THRES'] = dexpo_thres
        props['TELLUP_DEXPO_MAX_ITR'] = max_iterations
        props['TELLUP_ABSO_EXPO_KWID'] = ker_width
        props['TELLUP_ABSO_EXPO_KEXP'] = ker_shape
        props['TELLUP_TRANS_THRES'] = trans_thres
        props['TELLUP_TRANS_SIGLIM'] = trans_siglim
        props['TELLUP_FORCE_AIRMASS'] = force_airmass
        props['TELLUP_OTHER_BOUNDS'] = others_bounds
        props['TELLUP_WATER_BOUNDS'] = water_bounds
        props['TELLUP_ABSO_EXPO_KTHRES'] = ker_thres
        props['TELLUP_WAVE_START'] = wavestart
        props['TELLUP_WAVE_END'] = waveend
        props['TELLUP_DVGRID'] = dvgrid
        # set sources
        keys = ['TELLUP_D_WATER_ABSO', 'TELLUP_CCF_SCAN_RANGE',
                'TELLUP_CLEAN_OH_LINES', 'TELLUP_REMOVE_ORDS',
                'TELLUP_SNR_MIN_THRES', 'TELLUP_DEXPO_CONV_THRES',
                'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KWID',
                'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
                'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS',
                'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS',
                'TELLUP_ABSO_EXPO_KTHRES', 'TELLUP_WAVE_START',
                'TELLUP_WAVE_END', 'TELLUP_DVGRID', 'TELLUP_DO_PRECLEANING']
        props.set_sources(keys, func_name)
        # ------------------------------------------------------------------
        # return props
        return props
    # ----------------------------------------------------------------------
    # we ravel the wavelength grid to make it a 1d array of increasing
    #     wavelength. We will trim the overlapping domain between orders
    keep = np.ones_like(wave_e2ds).astype(bool)
    # keep track of where orders are
    orders, _ = np.indices(wave_e2ds.shape)
    # loop around 2nd to last-1 order and compare -1th and +1th order
    for order_num in range(1, nbo - 1):
        # get wavelengths not in order beforetellu_preclean
        before = wave_e2ds[order_num] > wave_e2ds[order_num - 1][::-1]
        # get wavelengths not in order after
        after = wave_e2ds[order_num] < wave_e2ds[order_num + 1][::-1]
        # combine mask
        keep[order_num] = before & after
    # set whole first order to zeros (rejected)
    keep[0] = np.zeros(nbpix).astype(bool)
    # set whole last order to zeros (rejected)
    keep[-1] = np.zeros(nbpix).astype(bool)
    # ----------------------------------------------------------------------
    # force into 1D and apply keep map
    flatkeep = keep.ravel()
    wavemap = wave_e2ds.ravel()[flatkeep]
    spectrum = image_e2ds.ravel()[flatkeep]
    spectrum_ini = image_e2ds_ini.ravel()[flatkeep]
    orders = orders.ravel()[flatkeep]
    # ----------------------------------------------------------------------
    # load tapas in correct format
    spl_others, spl_water = load_tapas_spl(params, recipe, header,
                                           database=database)
    # ----------------------------------------------------------------------
    # load the snr from e2ds file
    snr = infile.get_hkey_1d('KW_EXT_SNR', nbo, dtype=float)
    # remove infinite / NaN snr
    snr[~np.isfinite(snr)] = 0.0
    # remove snr from these orders (due to thermal background)
    for order_num in remove_orders:
        snr[order_num] = 0.0
    # make sure we have at least one order above the min snr requiredment
    if np.nanmax(snr) < snr_min_thres:
        # update qc params
        qc_values[0] = np.nanmax(snr)
        qc_pass[0] = 0
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # return qc_exit_tellu_preclean
        return qc_exit_tellu_preclean(params, recipe, image_e2ds, infile,
                                      wave_e2ds, qc_params, sky_model,
                                      database=database)
    else:
        qc_values[0] = np.nanmax(snr)
        qc_pass[0] = 1
    # mask all orders below min snr
    for order_num in range(nbo):
        # only mask if snr below threshold
        if snr[order_num] < snr_min_thres:
            # find order mask (we only want to remove values in this order
            order_mask = orders == order_num
            # apply low snr mask to spectrum
            spectrum[order_mask] = np.nan
    # for numerical stabiility, remove NaNs. Setting to zero biases a bit
    # the CCF, but this should be OK after we converge
    spectrum[~np.isfinite(spectrum)] = 0.0
    spectrum[spectrum < 0.0] = 0.0
    # ----------------------------------------------------------------------
    # scanning range for the ccf computations
    drange = np.arange(-ccf_scan_range, ccf_scan_range + 1.0, 1.0)
    # get species line lists from file
    mask_others, mask_water = get_sp_linelists(params)
    # storage for the ccfs
    ccf_others = np.zeros_like(drange, dtype=float)
    ccf_water = np.zeros_like(drange, dtype=float)
    # start with no correction of abso to get the CCF
    expo_water = 0.0
    # we start at zero to get a velocity mesaurement even if we may force
    #   to the airmass
    expo_others = 0.0
    # keep track of consecutive exponents and test convergence
    expo_water_prev = np.inf
    expo_others_prev = np.inf
    dexpo = np.inf
    # storage for the amplitude from fit
    amp_water_list = []
    amp_others_list = []
    # storage for the exponential from fit
    expo_water_list = []
    expo_others_list = []
    # storage for plotting
    dd_iterations = []
    ccf_water_iterations = []
    ccf_others_iterations = []
    # ----------------------------------------------------------------------
    # first guess at the velocity of absoprtion is 0 km/s
    dv_abso = 0.0
    # set the iteration number
    iteration = 0
    # just so we have outputs
    dv_water, dv_others = np.nan, np.nan
    trans = np.ones_like(wavemap)
    # set up a qc flag
    flag_qc = False
    # log progress
    WLOG(params, '', TextEntry('40-019-00040'))
    # loop around until convergence or 20th iteration
    while (dexpo > dexpo_thres) and (iteration < max_iterations):
        # set up a qc flag
        flag_qc = False
        # log progress
        args = [iteration, dexpo, expo_water, expo_others, dv_abso * 1000]
        WLOG(params, '', TextEntry('40-019-00041', args=args))
        # get the absorption spectrum
        trans = get_abso_expo(params, wavemap, expo_others, expo_water,
                              spl_others, spl_water, ww=ker_width,
                              ex_gau=ker_shape, dv_abso=dv_abso,
                              ker_thres=ker_thres, wavestart=wavestart,
                              waveend=waveend, dvgrid=dvgrid)
        # divide spectrum by transmission
        spectrum_tmp = spectrum / trans
        # ------------------------------------------------------------------
        # only keep valid pixels (non NaNs)
        valid = np.isfinite(spectrum_tmp)
        # transmission with the exponent value
        valid &= (trans > np.exp(trans_thres))
        # ------------------------------------------------------------------
        # apply some cuts to very discrepant points. These will be set to zero
        #   not to bias the CCF too much
        cut = np.nanmedian(np.abs(spectrum_tmp)) * trans_siglim
        # set NaN and infinite values to zero
        spectrum_tmp[~np.isfinite(spectrum_tmp)] = 0.0
        # apply cut and set values to zero
        spectrum_tmp[spectrum_tmp > cut] = 0.0
        # set negative values to zero
        spectrum_tmp[spectrum_tmp < 0.0] = 0.0
        # ------------------------------------------------------------------
        # get the CCF of the test spectrum
        # first spline onto the wave grid
        spline = mp.iuv_spline(wavemap[valid], spectrum_tmp[valid], k=1, ext=1)
        # loop around all scanning points in d
        for d_it in range(len(drange)):
            # computer rv scaling factor
            scaling = (1 + drange[d_it] / speed_of_light)
            # we compute the ccf_others all the time, even when forcing the
            # airmass, just to look at its structure and potential residuals
            # compute for others
            lothers = np.array(mask_others['ll_mask_s']) * scaling
            tmp_others = spline(lothers) * np.array(mask_others['w_mask'])
            ccf_others[d_it] = np.nanmean(tmp_others[tmp_others != 0.0])
            # computer for water
            lwater = np.array(mask_water['ll_mask_s']) * scaling
            tmp_water = spline(lwater) * mask_water['w_mask']
            ccf_water[d_it] = np.nanmean(tmp_water[tmp_water != 0.0])
        # ------------------------------------------------------------------
        # subtract the median of the ccf outside the core of the gaussian.
        #     We take this to be the 'external' part of of the scan range
        # work out the external part mask
        with warnings.catch_warnings(record=True) as _:
            external_mask = np.abs(drange) > ccf_scan_range / 2
        # calculate and subtract external part
        external_water = np.nanmedian(ccf_water[external_mask])
        ccf_water = ccf_water - external_water
        external_others = np.nanmedian(ccf_others[external_mask])
        ccf_others = ccf_others - external_others
        # ------------------------------------------------------------------
        # get the amplitude of the middle of the CCF
        # work out the internal part mask
        internal_mask = np.abs(drange) < ccf_scan_range / 4
        amp_water = np.nansum(ccf_water[internal_mask])
        if not force_airmass:
            amp_others = np.nansum(ccf_others[internal_mask])
        else:
            amp_others = 0.0
        # ------------------------------------------------------------------
        # count the number of NaNs in the CCF
        num_nan_ccf = np.sum(~np.isfinite(ccf_water))
        # if CCF is NaN do not continue
        if num_nan_ccf > 0:
            # update qc params
            qc_values[1] = num_nan_ccf
            qc_pass[1] = 0
            # flag qc as failed and break
            flag_qc = True
            break
        else:
            qc_values[1] = num_nan_ccf
            qc_pass[1] = 1
        # ------------------------------------------------------------------
        # we measure absorption velocity by fitting a gaussian to the
        #     absorption profile. This updates the dv_abso value for the
        #     next steps.
        # if this is the first iteration then fit the  absorption velocity
        if iteration == 0:
            # make a guess for the water fit parameters (for curve fit)
            water_guess = [np.nanmin(ccf_water), 0, 4]
            # fit the ccf_water with a guassian
            popt, pcov = curve_fit(mp.gauss_function_nodc, drange, ccf_water,
                                   p0=water_guess)
            # store the velocity of the water
            dv_water = popt[1]
            # make a guess of the others fit parameters (for curve fit)
            others_guess = [np.nanmin(ccf_water), 0, 4]
            # fit the ccf_others with a gaussian
            popt, pconv = curve_fit(mp.gauss_function_nodc, drange, ccf_others,
                                    p0=others_guess)
            # store the velocity of the other species
            dv_others = popt[1]
            # store the mean velocity of water and others
            dv_abso = np.mean([dv_water, dv_others])
        # ------------------------------------------------------------------
        # store the amplitudes of current exponent values
        # for other species
        if not force_airmass:
            amp_others_list.append(amp_others)
            expo_others_list.append(expo_others)
        # for water
        amp_water_list.append(amp_water)
        expo_water_list.append(expo_water)
        # ------------------------------------------------------------------
        # if this is the first iteration force the values of
        # expo_others and expo water
        if iteration == 0:
            # header value to be used
            expo_others = float(hdr_airmass)
            # default value for water
            expo_water = float(default_water_abso)
        # ------------------------------------------------------------------
        # else we fit the amplitudes with polynomial fits
        else:
            # --------------------------------------------------------------
            # set value for fit_others
            fit_others = [np.nan, hdr_airmass, np.nan]
            # convert lists to arrays
            amp_others_arr = np.array(amp_others_list)
            expo_others_arr = np.array(expo_others_list)
            amp_water_arr = np.array(amp_water_list)
            expo_water_arr = np.array(expo_water_list)

            # if we have over 5 iterations we fit a 2nd order polynomial
            # to the lowest 5 amplitudes
            if iteration > 5:
                if not force_airmass:
                    # get others lists as array and sort them
                    sortmask = np.argsort(np.abs(amp_others_arr))
                    amp_others_arr = amp_others_arr[sortmask]
                    expo_others_arr = expo_others_arr[sortmask]
                    # polyfit lowest 5 others terms
                    fit_others = np.polyfit(amp_others_arr[0: 4],
                                            expo_others_arr[0:4], 1)
                # get water lists as arrays and sort them
                sortmask = np.argsort(np.abs(amp_water_arr))
                amp_water_arr = amp_water_arr[sortmask]
                expo_water_arr = expo_water_arr[sortmask]
                # polyfit lowest 5 water terms
                fit_water = np.polyfit(amp_water_arr[0:4],
                                       expo_water_arr[0:4], 1)
            # else just fit a line
            else:
                if not force_airmass:
                    fit_others = np.polyfit(amp_others_arr, expo_others_arr, 1)
                fit_water = np.polyfit(amp_water_arr, expo_water_arr, 1)
            # --------------------------------------------------------------
            # find best guess for other species exponent
            expo_others = float(fit_others[1])
            # deal with lower bounds for other species
            if expo_others < others_bounds[0]:
                # update qc params
                qc_values[2] = float(fit_others[1])
                qc_pass[2] = 0
                # set expo_others to lower others bound
                expo_others = float(others_bounds[0])
                # flag qc as failed and break
                flag_qc = True
            else:
                qc_values[2] = float(fit_others[1])
                qc_pass[2] = 1
            # deal with upper bounds for other species
            if expo_others > others_bounds[1]:
                # update qc params
                qc_values[3] = float(fit_others[1])
                qc_pass[3] = 0
                # set the expo_others to the upper others bound
                expo_others = float(others_bounds[1])
                # flag qc as failed and break
                flag_qc = True
            else:
                qc_values[3] = float(fit_others[1])
                qc_pass[3] = 1
            # --------------------------------------------------------------
            # find best guess for water exponent
            expo_water = float(fit_water[1])
            # deal with lower bounds for water
            if expo_water < water_bounds[0]:
                # update qc params
                qc_values[4] = float(fit_water[1])
                qc_pass[4] = 0
                # set the expo_water to the lower water bound
                expo_water = float(water_bounds[0])
                # flag qc as failed and break
                flag_qc = True
            else:
                qc_values[4] = float(fit_water[1])
                qc_pass[4] = 1
            # deal with upper bounds for water
            if expo_water > water_bounds[1]:
                # update qc params
                qc_values[5] = float(fit_water[1])
                qc_pass[5] = 0
                # set the expo_water to the upper water bound
                expo_water = float(water_bounds[1])
                # flag qc as failed and break
                flag_qc = True
            else:
                qc_values[5] = float(fit_water[1])
                qc_pass[5] = 1
            # --------------------------------------------------------------
            # check whether we have converged yet (by updating dexpo)
            if force_airmass:
                dexpo = np.abs(expo_water_prev - expo_water)
            else:
                part1 = expo_water_prev - expo_water
                part2 = expo_others_prev - expo_others
                dexpo = np.sqrt(part1 ** 2 + part2 ** 2)
            # break if qc flag True don't try to converge
            if flag_qc:
                break
        # --------------------------------------------------------------
        # keep track of the convergence params
        expo_water_prev = float(expo_water)
        expo_others_prev = float(expo_others)
        # ------------------------------------------------------------------
        # storage for plotting
        dd_iterations.append(drange)
        ccf_water_iterations.append(np.array(ccf_water))
        ccf_others_iterations.append(np.array(ccf_others))
        # ------------------------------------------------------------------
        # finally add one to the iterator
        iteration += 1
    # ----------------------------------------------------------------------
    # deal with iterations hitting the max (no convergence)
    if iteration == max_iterations - 1:
        # update qc params
        qc_values[6] = iteration
        qc_pass[6] = 0
        flag_qc = True
    else:
        qc_values[6] = iteration
        qc_pass[6] = 1
    # ----------------------------------------------------------------------
    # deal with the qc flags
    if flag_qc:
        # log that qc flagged
        for qit in range(len(qc_pass)):
            if qc_pass[qit] == 0:
                wargs = [qc_logic[qit], qc_names[qit], qc_values[qit]]
                WLOG(params, 'warning', TextEntry('10-019-00010', args=wargs))

        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # return qc_exit_tellu_preclean
        return qc_exit_tellu_preclean(params, recipe, image_e2ds, infile,
                                      wave_e2ds, qc_params, sky_model,
                                      database=database)
    # ----------------------------------------------------------------------
    # show CCF plot to see if correlation peaks have been killed
    recipe.plot('TELLUP_WAVE_TRANS', dd_arr=dd_iterations,
                ccf_water_arr=ccf_water_iterations,
                ccf_others_arr=ccf_others_iterations)
    recipe.plot('SUM_TELLUP_WAVE_TRANS', dd_arr=dd_iterations,
                ccf_water_arr=ccf_water_iterations,
                ccf_others_arr=ccf_others_iterations)
    # plot to show absorption spectrum
    recipe.plot('TELLUP_ABSO_SPEC', trans=trans, wave=wavemap,
                thres=trans_thres, spectrum=spectrum, spectrum_ini=spectrum_ini,
                objname=infile.get_hkey('KW_OBJNAME', dtype=str),
                clean_ohlines=clean_ohlines)
    recipe.plot('SUM_TELLUP_ABSO_SPEC', trans=trans, wave=wavemap,
                thres=trans_thres, spectrum=spectrum, spectrum_ini=spectrum_ini,
                objname=infile.get_hkey('KW_OBJNAME', dtype=str),
                clean_ohlines=clean_ohlines)
    # ----------------------------------------------------------------------
    # create qc_params (all passed now but we have updated values)
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # ----------------------------------------------------------------------
    # get the final absorption spectrum to be used on the science data.
    #     No trimming done on the wave grid
    abso_e2ds = get_abso_expo(params, wave_e2ds, expo_others, expo_water,
                              spl_others, spl_water, ww=ker_width,
                              ex_gau=ker_shape, dv_abso=0.0,
                              ker_thres=ker_thres, wavestart=wavestart,
                              waveend=waveend, dvgrid=dvgrid)
    # all absorption deeper than exp(trans_thres) is considered too deep to
    #    be corrected. We set values there to NaN
    mask = abso_e2ds < np.exp(2 * trans_thres)
    # set deep lines to NaN
    abso_e2ds[mask] = np.nan
    # ----------------------------------------------------------------------
    # now correct the original e2ds file
    corrected_e2ds = (image_e2ds_ini - sky_model) / abso_e2ds
    # ----------------------------------------------------------------------
    # calculate CCF power
    keep = np.abs(drange) < (ccf_scan_range / 4)
    water_ccfpower = np.nansum(np.gradient(ccf_water[keep] ** 2))
    others_ccfpower = np.nansum(np.gradient(ccf_others)[keep] ** 2)
    # ----------------------------------------------------------------------
    # populate parameter dictionary
    props = ParamDict()
    props['CORRECTED_E2DS'] = corrected_e2ds
    props['TRANS_MASK'] = mask
    props['ABSO_E2DS'] = abso_e2ds
    props['SKY_MODEL'] = sky_model
    props['EXPO_WATER'] = expo_water
    props['EXPO_OTHERS'] = expo_others
    props['DV_WATER'] = dv_water
    props['DV_OTHERS'] = dv_others
    props['CCFPOWER_WATER'] = water_ccfpower
    props['CCFPOWER_OTHERS'] = others_ccfpower
    props['QC_PARAMS'] = qc_params
    # set sources
    keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
            'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'CCFPOWER_WATER',
            'CCFPOWER_OTHERS', 'QC_PARAMS', 'SKY_MODEL']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    props['TELLUP_DO_PRECLEANING'] = do_precleaning
    props['TELLUP_D_WATER_ABSO'] = default_water_abso
    props['TELLUP_CCF_SCAN_RANGE'] = ccf_scan_range
    props['TELLUP_CLEAN_OH_LINES'] = clean_ohlines
    props['TELLUP_REMOVE_ORDS'] = remove_orders
    props['TELLUP_SNR_MIN_THRES'] = snr_min_thres
    props['TELLUP_DEXPO_CONV_THRES'] = dexpo_thres
    props['TELLUP_DEXPO_MAX_ITR'] = max_iterations
    props['TELLUP_ABSO_EXPO_KWID'] = ker_width
    props['TELLUP_ABSO_EXPO_KEXP'] = ker_shape
    props['TELLUP_TRANS_THRES'] = trans_thres
    props['TELLUP_TRANS_SIGLIM'] = trans_siglim
    props['TELLUP_FORCE_AIRMASS'] = force_airmass
    props['TELLUP_OTHER_BOUNDS'] = others_bounds
    props['TELLUP_WATER_BOUNDS'] = water_bounds
    props['TELLUP_ABSO_EXPO_KTHRES'] = ker_thres
    props['TELLUP_WAVE_START'] = wavestart
    props['TELLUP_WAVE_END'] = waveend
    props['TELLUP_DVGRID'] = dvgrid
    # set sources
    keys = ['TELLUP_D_WATER_ABSO', 'TELLUP_CCF_SCAN_RANGE',
            'TELLUP_CLEAN_OH_LINES', 'TELLUP_REMOVE_ORDS',
            'TELLUP_SNR_MIN_THRES', 'TELLUP_DEXPO_CONV_THRES',
            'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KWID',
            'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
            'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS',
            'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS',
            'TELLUP_ABSO_EXPO_KTHRES', 'TELLUP_WAVE_START',
            'TELLUP_WAVE_END', 'TELLUP_DVGRID', 'TELLUP_DO_PRECLEANING']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # save pre-cleaned file
    tellu_preclean_write(params, recipe, infile, rawfiles, fiber, combine,
                         props, wprops, database=database)
    # ----------------------------------------------------------------------
    # return props
    return props


def clean_ohline_pca(params, image, wavemap, **kwargs):
    # load ohline principle components
    func_name = __NAME__ + '.clean_ohline_pca()'
    # ----------------------------------------------------------------------
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLUP_OHLINE_PCA_FILE', 'filename', kwargs,
                      func_name)
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', TextEntry('40-019-00042'))
    # ----------------------------------------------------------------------
    # get shape of the e2ds
    nbo, nbpix = image.shape
    # ----------------------------------------------------------------------
    # load principle components data file
    ohfile = os.path.join(assetdir, relfolder, filename)
    ohpcdata = drs_data.load_fits_file(params, ohfile, func_name)
    # ----------------------------------------------------------------------
    # get the number of components
    n_components = ohpcdata.shape[1] - 1
    # get the ohline wave grid
    ohwave = ohpcdata[:, 0].reshape(nbo, nbpix)
    # get the principle components
    ohpcas = ohpcdata[:, 1:].reshape(nbo, nbpix, n_components)
    # ----------------------------------------------------------------------
    # replace NaNs in the science data with zeros to avoid problems in the
    #   fitting below
    ribbon_e2ds = np.array(image).ravel()
    ribbon_e2ds[~np.isfinite(ribbon_e2ds)] = 0
    # make the PCs a ribbon that is N_pc * (nbo  * nbpix)
    ribbons_pcs = np.zeros([n_components, len(ribbon_e2ds)])

    # lead the PCs and transform to the night grid
    for ncomp in range(n_components):
        # shift the principle component from ohwave grid to input e2ds wave grid
        ohpcshift = wave_to_wave(params, ohpcas[:, :, ncomp], ohwave, wavemap)
        # push into ribbons
        ribbons_pcs[ncomp] = ohpcshift.ravel()
    # ----------------------------------------------------------------------
    # output for the sky model
    sky_model = np.zeros_like(ribbon_e2ds)
    # here we could have a loop, that's why the sky_model is within the
    #    fitting function.
    # work out the grad of the diff
    vector = np.gradient(ribbon_e2ds - sky_model)
    sample = np.gradient(ribbons_pcs, axis=1)
    # linear minimisation of the ribbon's derivative to the science
    #     data derivative
    amps, model = mp.linear_minimization(vector, sample)
    # ----------------------------------------------------------------------
    # reconstruct the sky model with the amplitudes derived above
    for ncomp in range(n_components):
        sky_model += ribbons_pcs[ncomp] * amps[ncomp]
    # sky model cannot be negative
    with warnings.catch_warnings(record=True) as _:
        sky_model[sky_model < 0] = 0
    # push sky_model into correct shape
    sky_model = sky_model.reshape(nbo, nbpix)
    # ----------------------------------------------------------------------
    # return the cleaned image and sky model
    return image - sky_model, sky_model


def get_abso_expo(params, wavemap, expo_others, expo_water, spl_others,
                  spl_water, ww, ex_gau, dv_abso, ker_thres, wavestart,
                  waveend, dvgrid):
    """
    Returns an absorption spectrum from exponents describing water and 'others'
    in absorption

    :param params: ParamDict, parameter dictionary of constants
    :param wavemap: numpy nd array, wavelength grid onto which the spectrum is
                    splined
    :param expo_others: float, optical depth of all species other than water
    :param expo_water: float, optical depth of water
    :param spl_others: spline function from tapas of other species
    :param spl_water: spline function from tapas of water
    :param ww: gaussian width of the kernel
    :param ex_gau: exponent of the gaussian (ex_gau = 2 is a gaussian, >2
                   is boxy)
    :param dv_abso: velocity of the absorption
    :param ker_thres:
    :param wavestart:
    :param waveend:
    :param dvgrid:
    :return:
    """
    # set the function name
    _ = display_func(params, 'get_abso_expo', __NAME__)
    # ----------------------------------------------------------------------
    # for some test one may give 0 as exponents and for this we just return
    #    a flat vector
    if (expo_others == 0) and (expo_water == 0):
        return np.ones_like(wavemap)
    # ----------------------------------------------------------------------
    # define the convolution kernel for the model. This shape factor can be
    #    modified if needed
    #   divide by fwhm of a gaussian of exp = 2.0
    width = ww / mp.fwhm()
    # defining the convolution kernel x grid, defined over 4 fwhm
    kernel_width = int(ww * 4)
    dd = np.arange(-kernel_width, kernel_width + 1.0, 1.0)
    # normalization of the kernel
    ker = np.exp(-0.5 * np.abs(dd / width) ** ex_gau)
    # shorten then kernel to keep only pixels that are more than 1e-6 of peak
    ker = ker[ker > ker_thres * np.max(ker)]
    # normalize the kernel
    ker /= np.sum(ker)
    # ----------------------------------------------------------------------
    # create a magic grid onto which we spline our transmission, same as
    #   for the s1d_v
    logwratio = np.log(waveend / wavestart)
    len_magic = int(np.ceil(logwratio * speed_of_light / dvgrid))
    magic_grid = np.exp(np.arange(len_magic) / len_magic * logwratio)
    magic_grid = magic_grid * wavestart
    # spline onto magic grid
    sp_others = spl_others(magic_grid)
    sp_water = spl_water(magic_grid)
    # ----------------------------------------------------------------------
    # for numerical stability, we may have values very slightly below 0 from
    #     the spline above. negative values don't work with fractional exponents
    sp_others[sp_others < 0.0] = 0.0
    sp_water[sp_water < 0.0] = 0.0
    # ----------------------------------------------------------------------
    # applying optical depths
    trans_others = sp_others ** expo_others
    trans_water = sp_water ** expo_water
    # getting the full absorption at full resolution
    trans = trans_others * trans_water
    # convolving after product (to avoid the infamous commutativity problem
    trans_convolved = np.convolve(trans, ker, mode='same')
    # ----------------------------------------------------------------------
    # spline that onto the input grid and allow a velocity shift
    magic_shift = magic_grid * (1 + dv_abso / speed_of_light)
    magic_spline = mp.iuv_spline(magic_shift, trans_convolved)
    # if this is a 2d array from an e2ds we loop on the orders
    if len(wavemap.shape) == 2:
        out_vector = np.zeros(wavemap.shape)
        # loop around orders and populate
        for order_num in range(wavemap.shape[0]):
            out_vector[order_num] = magic_spline(wavemap[order_num])
    # else just spline the full wave grid
    else:
        out_vector = magic_spline(wavemap)
    # ----------------------------------------------------------------------
    # cannot spline outside magic grid
    # ----------------------------------------------------------------------
    # get bounds of magic grid
    min_magic = np.nanmin(magic_grid)
    max_magic = np.nanmax(magic_grid)
    # set all out of bound values to NaN
    mask = (wavemap < min_magic) | (wavemap > max_magic)
    out_vector[mask] = np.nan
    # ----------------------------------------------------------------------
    # return out vector
    return out_vector


def qc_exit_tellu_preclean(params, recipe, image, infile, wavemap,
                           qc_params, sky_model, database=None, **kwargs):
    """
    Provides an exit point for tellu_preclean via a quality control failure

    :param params:
    :param image:
    :param infile:
    :param wavemap:
    :param qc_params:
    :param sky_model:
    :param database:

    :return:
    """
    # set the function name
    func_name = __NAME__ + '.qc_exit_tellu_preclean()'
    # ----------------------------------------------------------------------
    # get parameters from parameter dictionary
    do_precleaning = pcheck(params, 'TELLUP_DO_PRECLEANING', 'do_precleaning',
                            kwargs, func_name)
    default_water_abso = pcheck(params, 'TELLUP_D_WATER_ABSO',
                                'default_water_abso', kwargs, func_name)
    ccf_scan_range = pcheck(params, 'TELLUP_CCF_SCAN_RANGE', 'ccf_scan_range',
                            kwargs, func_name)
    clean_ohlines = pcheck(params, 'TELLUP_CLEAN_OH_LINES', 'clean_ohlines',
                           kwargs, func_name)

    remove_orders = pcheck(params, 'TELLUP_REMOVE_ORDS', 'remove_orders',
                           kwargs, func_name, mapf='list', dtype=int)
    snr_min_thres = pcheck(params, 'TELLUP_SNR_MIN_THRES', 'snr_min_thres',
                           kwargs, func_name)
    dexpo_thres = pcheck(params, 'TELLUP_DEXPO_CONV_THRES', 'dexpo_thres',
                         kwargs, func_name)
    max_iterations = pcheck(params, 'TELLUP_DEXPO_MAX_ITR', 'max_iterations',
                            kwargs, func_name)
    ker_width = pcheck(params, 'TELLUP_ABSO_EXPO_KWID', 'ker_width', kwargs,
                       func_name)
    ker_shape = pcheck(params, 'TELLUP_ABSO_EXPO_KEXP', 'ker_shape', kwargs,
                       func_name)
    qc_ker_width = pcheck(params, 'TELLUP_ABSO_EXPO_KWID', 'qc_ker_width',
                          kwargs, func_name)
    qc_ker_shape = pcheck(params, 'TELLUP_ABSO_EXPO_KEXP', 'qc_ker_shape',
                          kwargs, func_name)
    trans_thres = pcheck(params, 'TELLUP_TRANS_THRES', 'trans_thres', kwargs,
                         func_name)
    trans_siglim = pcheck(params, 'TELLUP_TRANS_SIGLIM', 'trans_siglim', kwargs,
                          func_name)
    force_airmass = pcheck(params, 'TELLUP_FORCE_AIRMASS', 'force_airmass',
                           kwargs, func_name)
    others_bounds = pcheck(params, 'TELLUP_OTHER_BOUNDS', 'others_bounds',
                           kwargs, func_name, mapf='list', dtype=float)
    water_bounds = pcheck(params, 'TELLUP_WATER_BOUNDS', 'water_bounds', kwargs,
                          func_name, mapf='list', dtype=float)
    ker_thres = pcheck(params, 'TELLUP_ABSO_EXPO_KTHRES', 'ker_thres', kwargs,
                       func_name)
    wavestart = pcheck(params, 'EXT_S1D_WAVESTART', 'wavestart', kwargs,
                       func_name)
    waveend = pcheck(params, 'EXT_S1D_WAVEEND', 'waveend', kwargs, func_name)
    dvgrid = pcheck(params, 'EXT_S1D_BIN_UVELO', 'dvgrid', kwargs, func_name)
    # ----------------------------------------------------------------------
    # get image and header from infile
    image_e2ds = np.array(image)
    header = infile.get_header()
    # get airmass from header
    hdr_airmass = infile.get_hkey('KW_AIRMASS', dtype=float)
    # ----------------------------------------------------------------------
    # load tapas in correct format
    spl_others, spl_water = load_tapas_spl(params, recipe, header,
                                           database=database)
    # ----------------------------------------------------------------------
    # force expo values
    expo_others = float(hdr_airmass)
    expo_water = float(default_water_abso)
    # get the absorption
    abso_e2ds = get_abso_expo(params, wavemap, expo_others, expo_water,
                              spl_others, spl_water, ww=qc_ker_width,
                              ex_gau=qc_ker_shape, dv_abso=0.0,
                              ker_thres=ker_thres, wavestart=wavestart,
                              waveend=waveend, dvgrid=dvgrid)
    # mask transmission below certain threshold
    mask = abso_e2ds < np.exp(trans_thres)
    # correct e2ds
    corrected_e2ds = image_e2ds / abso_e2ds
    # mask poor tranmission regions
    corrected_e2ds[mask] = np.nan
    # ----------------------------------------------------------------------
    # populate parameter dictionary
    props = ParamDict()
    props['CORRECTED_E2DS'] = corrected_e2ds
    props['TRANS_MASK'] = mask
    props['ABSO_E2DS'] = abso_e2ds
    props['SKY_MODEL'] = sky_model
    props['EXPO_WATER'] = expo_water
    props['EXPO_OTHERS'] = expo_others
    props['DV_WATER'] = np.nan
    props['DV_OTHERS'] = np.nan
    props['CCFPOWER_WATER'] = np.nan
    props['CCFPOWER_OTHERS'] = np.nan
    props['QC_PARAMS'] = qc_params
    # set sources
    keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
            'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'CCFPOWER_WATER',
            'CCFPOWER_OTHERS', 'QC_PARAMS', 'SKY_MODEL']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    props['TELLUP_DO_PRECLEANING'] = do_precleaning
    props['TELLUP_D_WATER_ABSO'] = default_water_abso
    props['TELLUP_CCF_SCAN_RANGE'] = ccf_scan_range
    props['TELLUP_CLEAN_OH_LINES'] = clean_ohlines
    props['TELLUP_REMOVE_ORDS'] = remove_orders
    props['TELLUP_SNR_MIN_THRES'] = snr_min_thres
    props['TELLUP_DEXPO_CONV_THRES'] = dexpo_thres
    props['TELLUP_DEXPO_MAX_ITR'] = max_iterations
    props['TELLUP_ABSO_EXPO_KWID'] = ker_width
    props['TELLUP_ABSO_EXPO_KEXP'] = ker_shape
    props['TELLUP_TRANS_THRES'] = trans_thres
    props['TELLUP_TRANS_SIGLIM'] = trans_siglim
    props['TELLUP_FORCE_AIRMASS'] = force_airmass
    props['TELLUP_OTHER_BOUNDS'] = others_bounds
    props['TELLUP_WATER_BOUNDS'] = water_bounds
    props['TELLUP_ABSO_EXPO_KTHRES'] = ker_thres
    props['TELLUP_WAVE_START'] = wavestart
    props['TELLUP_WAVE_END'] = waveend
    props['TELLUP_DVGRID'] = dvgrid
    # set sources
    keys = ['TELLUP_D_WATER_ABSO', 'TELLUP_CCF_SCAN_RANGE',
            'TELLUP_CLEAN_OH_LINES', 'TELLUP_REMOVE_ORDS',
            'TELLUP_SNR_MIN_THRES', 'TELLUP_DEXPO_CONV_THRES',
            'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KWID',
            'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
            'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS',
            'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS',
            'TELLUP_ABSO_EXPO_KTHRES', 'TELLUP_WAVE_START',
            'TELLUP_WAVE_END', 'TELLUP_DVGRID', 'TELLUP_DO_PRECLEANING']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return props
    return props


def tellu_preclean_write(params, recipe, infile, rawfiles, fiber, combine,
                         props, wprops,
                         database: Union[TelluDatabase, None] = None):
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    tpclfile = recipe.outputs['TELLU_PCLEAN'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    tpclfile.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # copy keys from input file
    tpclfile.copy_original_keys(infile)
    # add version
    tpclfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    tpclfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    tpclfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    tpclfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    tpclfile.add_hkey('KW_OUTPUT', value=tpclfile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        infiles = rawfiles
    else:
        infiles = [infile.basename]
    tpclfile.add_hkey_1d('KW_INFILE1', values=infiles, dim1name='file')
    # add  calibration files used
    tpclfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    # ----------------------------------------------------------------------
    # set images
    dimages = [props['CORRECTED_E2DS'], props['TRANS_MASK'].astype(float),
               props['ABSO_E2DS'], props['SKY_MODEL']]
    # add extention info
    kws1 = ['EXTDESC1', 'Corrected', 'Extension 1 description']
    kws2 = ['EXTDESC2', 'Trans Mask', 'Extension 2 description']
    kws3 = ['EXTDESC3', 'ABSO E2DS', 'Extension 3 description']
    kws4 = ['EXTDESC4', 'Sky model', 'Extension 4 description']
    # add to hdict
    tpclfile.add_hkey(key=kws1)
    tpclfile.add_hkey(key=kws2)
    tpclfile.add_hkey(key=kws3)
    tpclfile.add_hkey(key=kws4)
    # ----------------------------------------------------------------------
    # need to write these as header keys
    tpclfile.add_hkey('KW_TELLUP_EXPO_WATER', value=props['EXPO_WATER'])
    tpclfile.add_hkey('KW_TELLUP_EXPO_OTHERS', value=props['EXPO_OTHERS'])
    tpclfile.add_hkey('KW_TELLUP_DV_WATER', value=props['DV_WATER'])
    tpclfile.add_hkey('KW_TELLUP_DV_OTHERS', value=props['DV_OTHERS'])
    tpclfile.add_hkey('KW_TELLUP_CCFP_WATER', value=props['CCFPOWER_WATER'])
    tpclfile.add_hkey('KW_TELLUP_CCFP_OTHERS', value=props['CCFPOWER_OTHERS'])
    # ----------------------------------------------------------------------
    # get qc names/values/logic/pass from qc params
    qc_names, qc_values, qc_logic, qc_pass = props['QC_PARAMS']
    # first add number of QCs
    qkw = ['TQCCNUM', len(qc_names), 'Number of tellu pre-clean qcs']
    tpclfile.add_hkey(key=qkw)
    # now add the keys
    for qc_it in range(len(qc_names)):
        # add name
        qkwn = ['TQCCN{0}'.format(qc_it), qc_names[qc_it],
                'Name {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwn)
        # add value
        qkwv = ['TQCCV{0}'.format(qc_it), qc_values[qc_it],
                'Value {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwv)
        # add logic
        qkwl = ['TQCCL{0}'.format(qc_it), qc_logic[qc_it],
                'Logic {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwl)
        # add pass
        qkwp = ['TQCCP{0}'.format(qc_it), qc_pass[qc_it],
                'Pass {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwp)
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    tpclfile.add_hkey('KW_TELLUP_DO_PRECLEAN',
                      value=props['TELLUP_DO_PRECLEANING'])
    tpclfile.add_hkey('KW_TELLUP_DFLT_WATER',
                      value=props['TELLUP_D_WATER_ABSO'])
    tpclfile.add_hkey('KW_TELLUP_CCF_SRANGE',
                      value=props['TELLUP_CCF_SCAN_RANGE'])
    tpclfile.add_hkey('KW_TELLUP_CLEAN_OHLINES',
                      value=props['TELLUP_CLEAN_OH_LINES'])
    tpclfile.add_hkey('KW_TELLUP_REMOVE_ORDS',
                      value=props['TELLUP_REMOVE_ORDS'], mapf='list')
    tpclfile.add_hkey('KW_TELLUP_SNR_MIN_THRES',
                      value=props['TELLUP_SNR_MIN_THRES'])
    tpclfile.add_hkey('KW_TELLUP_DEXPO_CONV_THRES',
                      value=props['TELLUP_DEXPO_CONV_THRES'])
    tpclfile.add_hkey('KW_TELLUP_DEXPO_MAX_ITR',
                      value=props['TELLUP_DEXPO_MAX_ITR'])
    tpclfile.add_hkey('KW_TELLUP_ABSOEXPO_KTHRES',
                      value=props['TELLUP_ABSO_EXPO_KTHRES'])
    tpclfile.add_hkey('KW_TELLUP_WAVE_START', value=props['TELLUP_WAVE_START'])
    tpclfile.add_hkey('KW_TELLUP_WAVE_END', value=props['TELLUP_WAVE_END'])
    tpclfile.add_hkey('KW_TELLUP_DVGRID', value=props['TELLUP_DVGRID'])
    tpclfile.add_hkey('KW_TELLUP_ABSOEXPO_KWID',
                      value=props['TELLUP_ABSO_EXPO_KWID'])
    tpclfile.add_hkey('KW_TELLUP_ABSOEXPO_KEXP',
                      value=props['TELLUP_ABSO_EXPO_KEXP'])
    tpclfile.add_hkey('KW_TELLUP_TRANS_THRES',
                      value=props['TELLUP_TRANS_THRES'])
    tpclfile.add_hkey('KW_TELLUP_TRANS_SIGL',
                      value=props['TELLUP_TRANS_SIGLIM'])
    tpclfile.add_hkey('KW_TELLUP_FORCE_AIRMASS',
                      value=props['TELLUP_FORCE_AIRMASS'])
    tpclfile.add_hkey('KW_TELLUP_OTHER_BOUNDS',
                      value=props['TELLUP_OTHER_BOUNDS'], mapf='list')
    tpclfile.add_hkey('KW_TELLUP_WATER_BOUNDS',
                      value=props['TELLUP_WATER_BOUNDS'], mapf='list')
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, '', TextEntry('40-019-00044', args=[tpclfile.filename]))
    # write to file
    tpclfile.data = dimages[0]
    tpclfile.write_multi(data_list=dimages[1:], kind=recipe.outputtype,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(tpclfile)
    # ----------------------------------------------------------------------
    # load database only if not already loaded
    if database is None:
        database = TelluDatabase(params)
        # load the database
        database.load_db()
    # ----------------------------------------------------------------------
    # copy the pre-cleaned file to telluDB
    database.add_tellu_file(tpclfile)


def read_tellu_preclean(params, recipe, infile, fiber, database=None):
    """
    Read all TELLU_PCLEAN files and if infile is one of them load the images
    and properties, else return None

    :param params:
    :param recipe:
    :param infile:
    :param fiber:
    :param database:

    :return:
    """

    # get infile object name
    objname = infile.get_hkey('KW_OBJNAME')

    # ------------------------------------------------------------------
    # get the tellu preclean map key
    # ----------------------------------------------------------------------
    out_pclean = drs_startup.get_file_definition('TELLU_PCLEAN',
                                                 params['INSTRUMENT'],
                                                 kind='red', fiber=fiber)
    # get key
    pclean_key = out_pclean.get_dbkey()
    # load tellu file, header and abspaths
    pclean_filenames = load_tellu_file(params, pclean_key,
                                       infile.get_header(),
                                       n_entries='*', get_image=False,
                                       required=False, fiber=fiber,
                                       objname=objname, return_filename=True,
                                       database=database)
    # if we don't have the file return None
    if pclean_filenames is None:
        return None
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    tpclfile = recipe.outputs['TELLU_PCLEAN'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    tpclfile.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # only keep basenames
    pclean_basenames = []
    for pclean_filename in pclean_filenames:
        pclean_basenames.append(os.path.basename(pclean_filename))
    # see if file is in database
    if tpclfile.basename not in pclean_basenames:
        return None
    # else we need the location of the file
    else:
        # find the first occurance of this basename in the list
        pos = np.where(tpclfile.basename == np.array(pclean_basenames))[0][0]
        # use this to set the absolute path of the filename (as this file
        #  must be from the telluric database)
        tpclfile.set_filename(pclean_filenames[pos])
    # ----------------------------------------------------------------------
    # log progress
    # log: Reading pre-cleaned file from: {0}
    WLOG(params, '', TextEntry('40-019-00043', args=[tpclfile.filename]))
    # ----------------------------------------------------------------------
    # start a parameter dictionary
    props = ParamDict()
    # else we read the multi-fits file
    tpclfile.read_multi()
    # ----------------------------------------------------------------------
    # read qc parameters
    qc_names, qc_values, qc_logic, qc_pass = [], [], [], []
    # first add number of QCs
    num_qcs = tpclfile.get_hkey('TQCCNUM', dtype=int)
    # now add the keys
    for qc_it in range(num_qcs):
        # add name
        qc_names.append(tpclfile.get_hkey('TQCCN{0}'.format(qc_it), dtype=str))
        # add value
        value = tpclfile.get_hkey('TQCCV{0}'.format(qc_it), dtype=str)
        # evaluate vaule
        # noinspection PyBroadException
        try:
            qc_values.append(eval(value))
        except Exception as _:
            qc_values.append(value)
        # add logic
        qc_logic.append(tpclfile.get_hkey('TQCCL{0}'.format(qc_it), dtype=str))
        # add pass
        qc_pass.append(tpclfile.get_hkey('TQCCP{0}'.format(qc_it), dtype=int))
    # push into props
    props['QC_PARAMS'] = [qc_names, qc_values, qc_logic, qc_pass]
    # ----------------------------------------------------------------------
    # push arrays into parameter dictionary
    props['CORRECTED_E2DS'] = tpclfile.data_array[0]
    props['TRANS_MASK'] = tpclfile.data_array[1].astype(bool)
    props['ABSO_E2DS'] = tpclfile.data_array[2]
    props['SKY_MODEL'] = tpclfile.data_array[3]
    # ----------------------------------------------------------------------
    # push into props
    props['EXPO_WATER'] = tpclfile.get_hkey('KW_TELLUP_EXPO_WATER', dtype=float)
    props['EXPO_OTHERS'] = tpclfile.get_hkey('KW_TELLUP_EXPO_OTHERS',
                                             dtype=float)
    props['DV_WATER'] = tpclfile.get_hkey('KW_TELLUP_DV_WATER', dtype=float)
    props['DV_OTHERS'] = tpclfile.get_hkey('KW_TELLUP_DV_OTHERS', dtype=float)
    props['CCFPOWER_WATER'] = tpclfile.get_hkey('KW_TELLUP_CCFP_WATER',
                                                dtype=float)
    props['CCFPOWER_OTHERS'] = tpclfile.get_hkey('KW_TELLUP_CCFP_OTHERS',
                                                 dtype=float)
    # set sources
    keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
            'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'CCFPOWER_WATER',
            'CCFPOWER_OTHERS', 'QC_PARAMS', 'SKY_MODEL']
    props.set_sources(keys, 'header')
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    props['TELLUP_DO_PRECLEANING'] = tpclfile.get_hkey('KW_TELLUP_DO_PRECLEAN',
                                                       dtype=bool)
    props['TELLUP_D_WATER_ABSO'] = tpclfile.get_hkey('KW_TELLUP_DFLT_WATER',
                                                     dtype=float)
    props['TELLUP_CCF_SCAN_RANGE'] = tpclfile.get_hkey('KW_TELLUP_CCF_SRANGE',
                                                       dtype=float)
    kw_clean_oh = 'KW_TELLUP_CLEAN_OHLINES'
    props['TELLUP_CLEAN_OH_LINES'] = tpclfile.get_hkey(kw_clean_oh, dtype=bool)
    props['TELLUP_REMOVE_ORDS'] = tpclfile.get_hkey('KW_TELLUP_REMOVE_ORDS',
                                                    dtype=list, listtype=int)
    props['TELLUP_SNR_MIN_THRES'] = tpclfile.get_hkey('KW_TELLUP_SNR_MIN_THRES',
                                                      dtype=float)
    kw_dexpo = 'KW_TELLUP_DEXPO_CONV_THRES'
    props['TELLUP_DEXPO_CONV_THRES'] = tpclfile.get_hkey(kw_dexpo, dtype=float)
    props['TELLUP_DEXPO_MAX_ITR'] = tpclfile.get_hkey('KW_TELLUP_DEXPO_MAX_ITR',
                                                      dtype=int)
    kw_kthres = 'KW_TELLUP_ABSOEXPO_KTHRES'
    props['TELLUP_ABSO_EXPO_KTHRES'] = tpclfile.get_hkey(kw_kthres, dtype=float)
    props['TELLUP_WAVE_START'] = tpclfile.get_hkey('KW_TELLUP_WAVE_START',
                                                   dtype=float)
    props['TELLUP_WAVE_END'] = tpclfile.get_hkey('KW_TELLUP_WAVE_END',
                                                 dtype=float)
    props['TELLUP_DVGRID'] = tpclfile.get_hkey('KW_TELLUP_DVGRID', dtype=float)
    kw_ae_kwid = 'KW_TELLUP_ABSOEXPO_KWID'
    props['TELLUP_ABSO_EXPO_KWID'] = tpclfile.get_hkey(kw_ae_kwid, dtype=float)
    kw_ae_kexp = 'KW_TELLUP_ABSOEXPO_KEXP'
    props['TELLUP_ABSO_EXPO_KEXP'] = tpclfile.get_hkey(kw_ae_kexp, dtype=float)
    props['TELLUP_TRANS_THRES'] = tpclfile.get_hkey('KW_TELLUP_TRANS_THRES',
                                                    dtype=float)
    props['TELLUP_TRANS_SIGLIM'] = tpclfile.get_hkey('KW_TELLUP_TRANS_SIGL',
                                                     dtype=float)
    props['TELLUP_FORCE_AIRMASS'] = tpclfile.get_hkey('KW_TELLUP_FORCE_AIRMASS',
                                                      dtype=bool)
    props['TELLUP_OTHER_BOUNDS'] = tpclfile.get_hkey('KW_TELLUP_OTHER_BOUNDS',
                                                     dtype=list, listtype=float)
    props['TELLUP_WATER_BOUNDS'] = tpclfile.get_hkey('KW_TELLUP_WATER_BOUNDS',
                                                     dtype=list, listtype=float)
    # set the source from header
    keys = ['TELLUP_D_WATER_ABSO', 'TELLUP_CCF_SCAN_RANGE',
            'TELLUP_CLEAN_OH_LINES', 'TELLUP_REMOVE_ORDS',
            'TELLUP_SNR_MIN_THRES', 'TELLUP_DEXPO_CONV_THRES',
            'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KWID',
            'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
            'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS',
            'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS',
            'TELLUP_ABSO_EXPO_KTHRES', 'TELLUP_WAVE_START',
            'TELLUP_WAVE_END', 'TELLUP_DVGRID', 'TELLUP_DO_PRECLEANING']
    props.set_sources(keys, 'header')
    # ----------------------------------------------------------------------
    # return props
    return props


# =============================================================================
# Database functions
# =============================================================================

# for: load_tellu_file
LoadTelluFileReturn = Union[  # if return filename
    str,
    # if return_filename + return_source
    Tuple[str, str],
    # default
    Tuple[Union[np.ndarray, Table, None],
          Union[drs_fits.Header, None],
          str],
    # if return_source
    Tuple[Union[np.ndarray, Table, None],
          Union[drs_fits.Header, None],
          str, str],
    # if nentries > 1
    List[str],
    # if nentries > 1 + return source
    Tuple[List[str], str],
    # if nentries > 1 + default
    Tuple[List[Union[np.ndarray, Table, None]],
          List[Union[drs_fits.Header, None]],
          List[str]],
    # if nentries > 1 + return source
    Tuple[List[Union[np.ndarray, None]],
          List[Union[drs_fits.Header, None]],
          List[str], str]
]


def load_tellu_file(params: ParamDict, key: str,
                    inheader: Union[drs_fits.Header, None] = None,
                    filename: Union[str, None] = None,
                    get_image: bool = True, get_header: bool = False,
                    fiber: Union[str, None] = None,
                    userinputkey: Union[str, None] = None,
                    database: Union[TelluDatabase, None] = None,
                    return_filename: bool = False, return_source: bool = False,
                    mode: Union[str, None] = None,
                    n_entries: Union[int, str] = 1,
                    objname: Union[str, None] = None,
                    tau_water: Union[Tuple[float, float], None] = None,
                    tau_others: Union[Tuple[float, float], None] = None,
                    no_times: bool = False,
                    required: bool = True, ext: int = 0, fmt: str = 'fits',
                    kind: str = 'image') -> LoadTelluFileReturn:
    """
    Load one or many telluric files

    :param params: ParamDict, the parameter dictionary of constants
    :param key: str, the key from the telluric database to select a
                specific telluric with
    :param inheader: fits.Header - the header file (required to match by time)
                     if None does not match by a 'zero point' time)

    :param filename: str or None, if set overrides filename from database
    :param get_image: bool, if True loads image (or images if nentries > 1),
                      if False image is None (or list of Nones if nentries > 1)
    :param get_header: bool, if True loads header (or headers if nentries > 1)
                       if False header is None (or list of Nones if
                       nentries > 1)
    :param fiber: str or None, if set must be the fiber type - all returned
                  calibrations are filtered by this fiber type
    :param userinputkey: str or None, if set checks params['INPUTS'] for this
                         key and sets filename from here - note params['INPUTS']
                         is where command line arguments are stored
    :param database: drs telluric database instance - set this if calibration
                     database already loaded (if unset will reload the database)
    :param return_filename: bool, if True returns the filename only
    :param return_source: bool, if True returns the source of the calib file(s)
    :param mode: str or None, the time mode for getting from sql
                 ('closest'/'newer'/'older')
    :param n_entries: int or str, maximum number of calibration files to return
                      for all entries use '*'
    :param objname: str or None, if set OBJECT=="fiber"
    :param tau_water: tuple or None, if set sets the lower and upper
                      bounds for tau water i.e.
                      TAU_WATER > tau_water[0]
                      TAU_WATER < tau_water[1]
    :param tau_others: tuple or None, if set sets the lower and upper bounds
                       for tau others  i.e.
                       TAU_OTHERS > tau_others[0]
                       TAU_OTHERS < tau_others[1]
    :param no_times: bool, if True does not use times to choose correct
                 files
    :param required: bool, whether we require an entry - will raise exception
                     if required=True and no entries found
    :param ext: int, valid extension (zero by default) when kind='image'
    :param fmt: str, astropy.table.Table valid format (when kind='table')
    :param kind: str, either 'image' for fits image or 'table' for table

    :return:
             if get_image, also returns image/table or list of images/tables
             if get_header, also returns header or list of headers
             if return_filename, returns filename or list of filenames
             if return_source, also returns source

             i.e. possible returns are:
                 filename
                 filename, source
                 image, header, filename
                 image, header, filename, source
                 List[filename]
                 List[filename], source
                 List[image], List[header], List[filename]
                 List[image], List[header], List[filename], source

    """
    # set function
    _ = display_func(params, 'load_tellu_file', __NAME__)
    # ------------------------------------------------------------------------
    # first try to get file from inputs
    fout = drs_data.get_file_from_inputs(params, 'telluric', userinputkey,
                                         filename, return_source=return_source)
    if return_source:
        filename, source = fout
    else:
        filename, source = fout, 'None'
    # ------------------------------------------------------------------------
    # if filename is defined this is the filename we should return
    if filename is not None and return_filename:
        if return_source:
            return str(filename), source
        else:
            return str(filename)
    # -------------------------------------------------------------------------
    # else we have to load from database
    if filename is None:
        # check if we have the database
        if database is None:
            # construct a new database instance
            database = TelluDatabase(params)
            # load the database
            database.load_db()
        # load filename from database
        filename = database.get_tellu_file(key, header=inheader,
                                           timemode=mode, nentries=n_entries,
                                           required=required, fiber=fiber,
                                           objname=objname, tau_water=tau_water,
                                           tau_others=tau_others,
                                           no_times=no_times)
        source = 'telluDB'
    # -------------------------------------------------------------------------
    # deal with filename being a path --> string (unless None)
    if filename is not None:
        if isinstance(filename, list):
            filename = list(map(lambda strfile: str(strfile), filename))
        else:
            filename = str(filename)
    # -------------------------------------------------------------------------
    # if we are just returning filename return here
    if return_filename:
        if return_source:
            return filename, source
        else:
            return filename
    # -------------------------------------------------------------------------
    # need to deal with a list of files
    if isinstance(filename, list):
        # storage for images and headres
        images, headers = [], []
        # loop around files
        for file_it in filename:
            # now read the calibration file
            image, header = drs_data.read_db_file(params, file_it, get_image,
                                                  get_header, kind, fmt, ext)
            # append to storage
            images.append(image)
            headers.append(headers)
        # return all
        if return_source:
            return images, headers, filename, source
        else:
            return images, headers, filename
    # -------------------------------------------------------------------------
    else:
        # now read the calibration file
        image, header = drs_data.read_db_file(params, filename, get_image,
                                              get_header, kind, fmt, ext)
        # return all
        if return_source:
            return image, header, filename, source
        else:
            return image, header, filename


# def load_tellu_file(params, key=None, inheader=None, filename=None,
#                     get_image=True, get_header=False, return_entries=False,
#                     **kwargs):
#     # get keys from params/kwargs
#     n_entries = kwargs.get('n_entries', 1)
#     required = kwargs.get('required', True)
#     mode = kwargs.get('mode', None)
#     # valid extension (zero by default)
#     ext = kwargs.get('ext', 0)
#     # fmt = valid astropy table format
#     fmt = kwargs.get('fmt', 'fits')
#     # kind = 'image' or 'table'
#     kind = kwargs.get('kind', 'image')
#     # ----------------------------------------------------------------------
#     # deal with filename set
#     if filename is not None:
#         # get db fits file
#         abspath = drs_database.get_db_abspath(params, filename, where='guess')
#         image, header = drs_database.get_db_file(params, abspath, ext, fmt,
#                                                  kind, get_image, get_header)
#         # return here
#         if get_header:
#             return [image], [header], [abspath]
#         else:
#             return [image], [abspath]
#     # ----------------------------------------------------------------------
#     # get telluDB
#     tdb = drs_database.get_full_database(params, 'telluric')
#     # get calibration entries
#     entries = drs_database.get_key_from_db(params, key, tdb, inheader,
#                                            n_ent=n_entries, mode=mode,
#                                            required=required)
#     # ----------------------------------------------------------------------
#     # deal with return entries
#     if return_entries:
#         return entries
#     # ----------------------------------------------------------------------
#     # get filename col
#     filecol = tdb.file_col
#     # ----------------------------------------------------------------------
#     # storage
#     images, headers, abspaths = [], [], []
#     # ----------------------------------------------------------------------
#     # loop around entries
#     for it, entry in enumerate(entries):
#         # get entry filename
#         filename = entry[filecol]
#         # ------------------------------------------------------------------
#         # get absolute path
#         abspath = drs_database.get_db_abspath(params, filename,
#                                               where='telluric')
#         # append to storage
#         abspaths.append(abspath)
#         # load image/header
#         image, header = drs_database.get_db_file(params, abspath, ext, fmt,
#                                                  kind, get_image, get_header)
#         # append to storage
#         images.append(image)
#         # append to storage
#         headers.append(header)
#     # ----------------------------------------------------------------------
#     # deal with returns with and without header
#     if get_header:
#         if not required and len(images) == 0:
#             return None, None, None
#         # deal with if n_entries is 1 (just return file not list)
#         if n_entries == 1:
#             return images[-1], headers[-1], abspaths[-1]
#         else:
#             return images, headers, abspaths
#     else:
#         if not required and len(images) == 0:
#             return None, None
#         # deal with if n_entries is 1 (just return file not list)
#         if n_entries == 1:
#             return images[-1], abspaths[-1]
#         else:
#             return images, abspaths


def load_templates(params: ParamDict,
                   header: Union[drs_fits.Header, None] = None,
                   objname: Union[str, None] = None,
                   fiber: Union[str, None] = None,
                   database: Union[TelluDatabase, None] = None
                   ) -> Tuple[Union[np.ndarray, None], Union[str, None]]:
    """
    Load the most recent template from the telluric database for 'objname'

    :param params: ParamDict, the parameter dictionary of constnats
    :param header: fits.Header or None -
    :param objname:
    :param fiber:
    :param database:
    :return:
    """
    # get file definition
    out_temp = drs_startup.get_file_definition('TELLU_TEMP',
                                               params['INSTRUMENT'],
                                               kind='red', fiber=fiber)
    # -------------------------------------------------------------------------
    # deal with user not using template
    if 'USE_TEMPLATE' in params['INPUTS']:
        if not params['INPUTS']['USE_TEMPLATE']:
            return None, None
    # -------------------------------------------------------------------------
    # get key
    temp_key = out_temp.get_dbkey()
    # -------------------------------------------------------------------------
    # log status
    WLOG(params, '', TextEntry('40-019-00045', args=[temp_key]))
    # load tellu file, header and abspaths
    temp_out = load_tellu_file(params, temp_key, header,
                               n_entries=1, required=False, fiber=fiber,
                               objname=objname, database=database,
                               mode=None)
    temp_image, temp_header, temp_filename = temp_out
    # -------------------------------------------------------------------------
    # deal with no files in database
    if temp_image is None:
        # log that we found no templates in database
        WLOG(params, '', TextEntry('40-019-00003'))
        return None, None
    # -------------------------------------------------------------------------
    # log which template we are using
    wargs = [temp_filename]
    WLOG(params, 'info', TextEntry('40-019-00005', args=wargs))
    # only return most recent template
    return temp_image, temp_filename


def get_transmission_files(params, header, fiber, database=None):
    # get file definition
    out_trans = drs_startup.get_file_definition('TELLU_TRANS',
                                                params['INSTRUMENT'],
                                                kind='red', fiber=fiber)
    # get key
    trans_key = out_trans.get_dbkey()
    # log status
    WLOG(params, '', TextEntry('40-019-00046', args=[trans_key]))
    # load tellu file, header and abspaths
    trans_filenames = load_tellu_file(params, trans_key, header, fiber=fiber,
                                      n_entries='*', get_image=False,
                                      database=database, return_filename=True)
    # storage for valid files/images/times
    valid_filenames = np.unique(trans_filenames)
    # return all valid sorted in time
    return list(valid_filenames)


# =============================================================================
# Tapas functions
# =============================================================================
def load_conv_tapas(params, recipe, header, mprops, fiber, database=None,
                    absorbers: Union[List[str], None] = None,
                    fwhm_lsf: Union[float, None] = None):
    func_name = __NAME__ + '.load_conv_tapas()'
    # get parameters from params/kwargs
    tellu_absorbers = pcheck(params, 'TELLU_ABSORBERS', func=func_name,
                             mapf='list', dtype=str, override=absorbers)
    fwhm_pixel_lsf = pcheck(params, 'FWHM_PIXEL_LSF', func=func_name,
                            override=fwhm_lsf)
    # ----------------------------------------------------------------------
    # deal with database not being loaded
    if database is None:
        database = TelluDatabase(params)
        # load database
        database.load_db()
    # ----------------------------------------------------------------------
    # Load any convolved files from database
    # ----------------------------------------------------------------------
    # get file definition
    if 'TELLU_CONV' in recipe.outputs:
        # get file definition
        out_tellu_conv = recipe.outputs['TELLU_CONV'].newcopy(params=params,
                                                              fiber=fiber)
        # get key
        conv_key = out_tellu_conv.get_dbkey()
    else:
        # get file definition
        out_tellu_conv = drs_startup.get_file_definition('TELLU_CONV',
                                                         params['INSTRUMENT'],
                                                         kind='red',
                                                         fiber=fiber)
        out_tellu_conv.params = params
        # get key
        conv_key = out_tellu_conv.get_dbkey()
    # load tellu file
    conv_paths = load_tellu_file(params, conv_key, header, n_entries='*',
                                 get_image=False, required=False,
                                 fiber=fiber, return_filename=True,
                                 database=database)
    if conv_paths is None:
        conv_paths = []
    # construct the filename from file instance
    out_tellu_conv.construct_filename(infile=mprops['WAVEINST'],
                                      path=params['DRS_TELLU_DB'],
                                      fiber=fiber)
    # if our npy file already exists then we just need to read it
    if out_tellu_conv.filename in conv_paths:
        # log that we are loading tapas convolved file
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00001', args=wargs))
        # ------------------------------------------------------------------
        # Load the convolved TAPAS atmospheric transmission from file
        # ------------------------------------------------------------------
        # load npy file
        out_tellu_conv.read_file(params)
        # push data into array
        tapas_all_species = out_tellu_conv.get_data(copy=True)
    # else we need to load tapas and generate the convolution
    else:
        # ------------------------------------------------------------------
        # Load the raw TAPAS atmospheric transmission
        # ------------------------------------------------------------------
        tapas_raw_table, tapas_raw_filename = drs_data.load_tapas(params)
        # ------------------------------------------------------------------
        # Convolve with master wave solution
        # ------------------------------------------------------------------
        tapas_all_species = _convolve_tapas(params, tapas_raw_table, mprops,
                                            tellu_absorbers, fwhm_pixel_lsf)
        # ------------------------------------------------------------------
        # Save convolution for later use
        # ------------------------------------------------------------------
        out_tellu_conv.data = tapas_all_species
        # log saving
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00002', args=wargs))
        # save
        out_tellu_conv.write_file(kind=recipe.outputtype,
                                  runstring=recipe.runstring)
        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
        # npy file must set header/hdict (to update)
        out_tellu_conv.header = header
        out_tellu_conv.hdict = header
        # copy the order profile to the calibDB
        database.add_tellu_file(out_tellu_conv)

    # ------------------------------------------------------------------
    # get the tapas_water and tapas_others data
    # ------------------------------------------------------------------
    # water is the second column
    tapas_water = tapas_all_species[1, :]
    # other is defined as the product of the other columns
    tapas_other = np.prod(tapas_all_species[2:, :], axis=0)

    # return the tapas info in a ParamDict
    tapas_props = ParamDict()
    tapas_props['TAPAS_ALL_SPECIES'] = tapas_all_species
    tapas_props['TAPAS_WATER'] = tapas_water
    tapas_props['TAPAS_OTHER'] = tapas_other
    tapas_props['TAPAS_FILE'] = out_tellu_conv.filename
    tapas_props['TELLU_ABSORBERS'] = tellu_absorbers
    tapas_props['FWHM_PIXEL_LSF'] = fwhm_pixel_lsf
    # set source
    keys = ['TAPAS_ALL_SPECIES', 'TAPAS_WATER', 'TAPAS_OTHER',
            'TAPAS_FILE', 'TELLU_ABSORBERS', 'FWHM_PIXEL_LSF']
    tapas_props.set_sources(keys, func_name)
    # return tapas props
    return tapas_props


def load_tapas_spl(params, recipe, header, database=None):
    # get file definition
    tellu_tapas = drs_startup.get_file_definition('TELLU_TAPAS',
                                                  params['INSTRUMENT'],
                                                  kind='red')
    # make new copy of the file definition
    out_tellu_tapas = tellu_tapas.newcopy(params=params)
    # get key
    conv_key = out_tellu_tapas.get_dbkey()
    # load tellu file
    conv_paths = load_tellu_file(params, conv_key, n_entries='*',
                                 get_image=False, required=False,
                                 return_filename=True)
    # construct the filename from file instance
    out_tellu_tapas.construct_filename(path=params['DRS_TELLU_DB'])
    # ----------------------------------------------------------------------
    # if our npy file already exists then we just need to read it
    if (conv_paths is not None) and (out_tellu_tapas.filename in conv_paths):
        out_tellu_tapas.read_file()
        # push into arrays
        tmp_tapas = out_tellu_tapas.get_data(copy=True)
        tapas_wave = tmp_tapas[0]
        trans_others = tmp_tapas[1]
        trans_water = tmp_tapas[2]
    # else we need to load it from file
    else:
        # ------------------------------------------------------------------
        # Load the raw TAPAS atmospheric transmission
        # ------------------------------------------------------------------
        tapas_raw, tapas_raw_filename = drs_data.load_tapas(params)
        # push into arrays
        tapas_wave = tapas_raw['wavelength']
        trans_others = (tapas_raw['trans_ch4'] * tapas_raw['trans_o3'] *
                        tapas_raw['trans_n2o'] * tapas_raw['trans_o2'] *
                        tapas_raw['trans_co2'])
        trans_water = tapas_raw['trans_h2o']
        # push into numpy array
        tmp_tapas = np.zeros([3, len(tapas_wave)])
        tmp_tapas[0] = tapas_wave
        tmp_tapas[1] = trans_others
        tmp_tapas[2] = trans_water
        # ------------------------------------------------------------------
        # Save tapas file for later use
        # ------------------------------------------------------------------
        # log saving
        args = [out_tellu_tapas.filename]
        WLOG(params, '', TextEntry('40-019-00047', args=[args]))
        # save to disk
        out_tellu_tapas.data = tmp_tapas
        out_tellu_tapas.write_file(kind=recipe.outputtype,
                                   runstring=recipe.runstring)
        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
        # npy file must set header/hdict (to update)
        out_tellu_tapas.header = header
        out_tellu_tapas.hdict = header
        # deal with no database
        if database is None:
            database = TelluDatabase(params)
            # load the database
            database.load_db()
        # copy the order profile to the telluDB
        database.add_tellu_file(out_tellu_tapas, copy_files=False,
                                objname='None', airmass='None',
                                tau_water='None', tau_others='None')
    # ----------------------------------------------------------------------
    # need to spline others and water
    spl_others = mp.iuv_spline(tapas_wave, trans_others, k=1, ext=3)
    spl_water = mp.iuv_spline(tapas_wave, trans_water, k=1, ext=3)
    # return splines
    return spl_others, spl_water


# =============================================================================
# Worker functions
# =============================================================================
def _convolve_tapas(params, tapas_table, mprops, tellu_absorbers,
                    fwhm_pixel_lsf):
    # get master wave data
    masterwave = mprops['WAVEMAP']
    ydim = mprops['NBO']
    xdim = mprops['NBPIX']
    # ----------------------------------------------------------------------
    # generate kernel for convolution
    # ----------------------------------------------------------------------
    # get the number of kernal pixels
    npix_ker = int(np.ceil(3 * fwhm_pixel_lsf * 3.0 / 2) * 2 + 1)
    # set up the kernel exponent
    kernel = np.arange(npix_ker) - npix_ker // 2
    # kernal is the a gaussian
    kernel = np.exp(-0.5 * (kernel / (fwhm_pixel_lsf / mp.fwhm())) ** 2)
    # we only want an approximation of the absorption to find the continuum
    #    and estimate chemical abundances.
    #    there's no need for a varying kernel shape
    kernel /= mp.nansum(kernel)
    # ----------------------------------------------------------------------
    # storage for output
    tapas_all_species = np.zeros([len(tellu_absorbers), xdim * ydim])
    # ----------------------------------------------------------------------
    # loop around each molecule in the absorbers list
    #    (must be in
    for n_species, molecule in enumerate(tellu_absorbers):
        # log process
        wmsg = 'Processing molecule: {0}'
        WLOG(params, '', wmsg.format(molecule))
        # get wavelengths
        lam = tapas_table['wavelength']
        # get molecule transmission
        trans = tapas_table['trans_{0}'.format(molecule)]
        # interpolate with Univariate Spline
        tapas_spline = mp.iuv_spline(lam, trans)
        # log the mean transmission level
        wmsg = '\tMean Trans level: {0:.3f}'.format(np.mean(trans))
        WLOG(params, '', wmsg)
        # convolve all tapas absorption to the SPIRou approximate resolution
        for iord in range(ydim):
            # get the order position
            start = iord * xdim
            end = (iord * xdim) + xdim
            # interpolate the values at these points
            svalues = tapas_spline(masterwave[iord, :])
            # convolve with a gaussian function
            nvalues = np.convolve(np.ones_like(svalues), kernel, mode='same')
            cvalues = np.convolve(svalues, kernel, mode='same') / nvalues
            # add to storage
            tapas_all_species[n_species, start: end] = cvalues
    # deal with non-real values (must be between 0 and 1
    tapas_all_species[tapas_all_species > 1] = 1
    tapas_all_species[tapas_all_species < 0] = 0

    # return tapas_all_species
    return tapas_all_species


def wave_to_wave(params, spectrum, wave1, wave2, reshape=False):
    """
    Shifts a "spectrum" at a given wavelength solution (map), "wave1", to
    another wavelength solution (map) "wave2"

    :param params: ParamDict, the parameter dictionary
    :param spectrum: numpy array (2D),  flux in the reference frame of the
                     file wave1
    :param wave1: numpy array (2D), initial wavelength grid
    :param wave2: numpy array (2D), destination wavelength grid
    :param reshape: bool, if True try to reshape spectrum to the shape of
                    the output wave solution

    :return output_spectrum: numpy array (2D), spectrum resampled to "wave2"
    """
    func_name = __NAME__ + '._wave_to_wave()'
    # deal with reshape
    if reshape or (spectrum.shape != wave2.shape):
        try:
            spectrum = spectrum.reshape(wave2.shape)
        except ValueError:
            # log that we cannot reshape spectrum
            eargs = [spectrum.shape, wave2.shape, func_name]
            WLOG(params, 'error', TextEntry('09-019-00004', args=eargs))
    # if they are the same
    if mp.nansum(wave1 != wave2) == 0:
        return spectrum
    # size of array, assumes wave1, wave2 and spectrum have same shape
    sz = np.shape(spectrum)
    # create storage for the output spectrum
    output_spectrum = np.zeros(sz) + np.nan
    # looping through the orders to shift them from one grid to the other
    for iord in range(sz[0]):
        # only interpolate valid pixels
        g = np.isfinite(spectrum[iord, :])
        # if not enough valid pixel, then skip order (need k+1 points)
        if mp.nansum(g) > 6:
            # spline the spectrum
            spline = mp.iuv_spline(wave1[iord, g], spectrum[iord, g],
                                   k=5, ext=1)
            # keep track of pixels affected by NaNs
            splinemask = mp.iuv_spline(wave1[iord, :], g, k=5, ext=1)
            # spline the input onto the output
            output_spectrum[iord, :] = spline(wave2[iord, :])
            # find which pixels are not NaNs
            mask = splinemask(wave2[iord, :])
            # set to NaN pixels outside of domain
            bad = (output_spectrum[iord, :] == 0)
            output_spectrum[iord, bad] = np.nan
            # affected by a NaN value
            # normally we would use only pixels ==1, but we get values
            #    that are not exactly one due to the interpolation scheme.
            #    We just set that >50% of the
            # flux comes from valid pixels
            bad = (mask <= 0.5)
            # mask pixels affected by nan
            output_spectrum[iord, bad] = np.nan
    # return the filled output spectrum
    return output_spectrum


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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:16

@author: cook
"""
import numpy as np
from astropy import constants as cc
from astropy import units as uu
from scipy.optimize import curve_fit
import warnings

from apero import core
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_database
from apero.io import drs_data
from apero.io import drs_fits
from apero.science.calib import flat_blaze


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.general.py'
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
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define functions
# =============================================================================
def get_whitelist(params, **kwargs):
    func_name = __NAME__ + '.get_whitelist()'
    # get pseudo constants
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_WHITELIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    wout = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                   func_name, dtype=str)
    whitelist, whitelistfile = wout
    # must clean names
    whitelist = list(map(pconst.DRS_OBJ_NAME, whitelist))
    # return the whitelist
    return whitelist, whitelistfile


def get_blacklist(params, **kwargs):
    func_name = __NAME__ + '.get_blacklist()'
    # get pseudo constants
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_BLACKLIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    bout = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                   func_name, dtype=str)
    blacklist, blacklistfile = bout
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


def get_non_tellu_objs(params, recipe, fiber, filetype=None, dprtypes=None,
                       robjnames=None):
    """
    Get the objects of "filetype" and "
    :param params:
    :param fiber:
    :param filetype:
    :return:
    """
    # get the telluric star names (we don't want to process these)
    objnames, _ = get_whitelist(params)
    objnames = list(objnames)
    # deal with filetype being string
    if isinstance(filetype, str):
        filetype = filetype.split(',')
    # deal with dprtypes being string
    if isinstance(dprtypes, str):
        dprtypes = dprtypes.split(',')
    # construct kwargs
    fkwargs = dict()
    if filetype is not None:
        fkwargs['KW_OUTPUT'] = filetype
    if dprtypes is not None:
        fkwargs['KW_DPRTYPE'] = dprtypes
    # # find files
    out = drs_fits.find_files(params, recipe, kind='red', return_table=True,
                              fiber=fiber, **fkwargs)
    obj_filenames, obj_table = out
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


def get_tellu_objs(params, key, objnames=None, **kwargs):
    """
    Get objects defined be "key" from telluric database (in list objname)

    :param params:
    :param key:
    :param objnames:
    :param kwargs:
    :return:
    """
    # deal with column to select from entries
    column = kwargs.get('column', 'filename')
    objcol = kwargs.get('objcol', 'objname')
    # ----------------------------------------------------------------------
    # deal with objnames
    if isinstance(objnames, str):
        objnames = [objnames]
    # ----------------------------------------------------------------------
    # load telluric obj entries (based on key)
    obj_entries = load_tellu_file(params, key=key, inheader=None, mode='ALL',
                                  return_entries=True, n_entries='all',
                                  required=False)
    # add to type
    typestr = str(key)
    # ----------------------------------------------------------------------
    # keep only objects with objnames
    mask = np.zeros(len(obj_entries)).astype(bool)
    # deal with no object found
    if len(obj_entries) == 0:
        return []
    elif objnames is not None:
        # storage for found objects
        found_objs = []
        # loop around objnames
        for objname in objnames:
            # update the mask
            mask |= obj_entries[objcol] == objname
            # only add to the mask if objname found
            if objname in obj_entries[objcol]:
                # update the found objs
                found_objs.append(objname)
        # update type string
        typestr += ' OBJNAME={0}'.format(', '.join(found_objs))
    # ----------------------------------------------------------------------
    # deal with all entries / one column return
    if column in [None, 'None', '', 'ALL']:
        outputs =  obj_entries[mask]
    else:
        outputs = np.unique(obj_entries[column][mask])
    # ----------------------------------------------------------------------
    # deal with getting absolute paths
    if column == 'filename':
        abspaths = []
        # loop around filenames
        for filename in outputs:
            # get absolute path
            abspath = drs_database.get_db_abspath(params, filename,
                                                  where='telluric')
            # append to list
            abspaths.append(abspath)
        # push back into outputs
        outputs = list(abspaths)
    # ----------------------------------------------------------------------
    # display how many files found
    margs = [len(outputs),  typestr]
    WLOG(params, '', TextEntry('40-019-00039', args=margs))
    return outputs


def get_sp_linelists(params, **kwargs):
    func_name = __NAME__ + '.get_sp_linelists()'
    # get pseudo constants
    pconst = constants.pload(instrument=params['INSTRUMENT'])
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
                   **kwargs):
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
    :param image:
    :param wprops:
    :param mprops:
    :return:
    """
    # set the function name
    func_name = __NAME__ + '.tellu_preclean()'
    # ----------------------------------------------------------------------
    # look for precleaned file
    loadprops = read_tellu_preclean(params, recipe, infile, fiber)
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
    image = infile.data
    header = infile.header
    # get airmass from header
    hdr_airmass = infile.get_key('KW_AIRMASS', dtype=float)
    # copy e2ds input image
    image_e2ds_ini = np.array(image)
    # get shape of the e2ds
    nbo, nbpix = image.shape
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
    qc_pass.append(1)
    # 2. ccf is NaN (pos = 1)
    qc_values.append(np.nan)
    qc_names.append('NUM_NAN_CCF')
    qc_logic.append('NUM_NAN_CCF > 0')
    qc_pass.append(1)
    # 3. exponent for others out of bounds (pos = 2 and 3)
    qc_values += [np.nan, np.nan]
    qc_names += ['EXPO_OTHERS', 'EXPO_OTHERS']
    qc_logic += ['EXPO_OTHERS < {0}'.format(others_bounds[0]),
                 'EXPO_OTHERS > {0}'.format(others_bounds[1])]
    qc_pass += [1, 1]
    # 4. exponent for water  out of bounds (pos 4 and 5)
    qc_values += [np.nan, np.nan]
    qc_names += ['EXPO_WATER', 'EXPO_WATER']
    qc_logic += ['EXPO_WATER < {0}'.format(water_bounds[0]),
                 'EXPO_WATER > {0}'.format(water_bounds[1])]
    qc_pass += [1, 1]
    # 5. max iterations exceeded (pos = 6)
    qc_values.append(np.nan)
    qc_names.append('ITERATIONS')
    qc_logic.append('ITERATIONS = {0}'.format(max_iterations - 1))
    qc_pass.append(1)
    # dev note: if adding a new one must add tfailmsgs for all uses in qc
    #  (mk_tellu and fit_tellu)
    # ----------------------------------------------------------------------
    # remove OH lines if required
    if clean_ohlines:
        image_e2ds, sky_model = clean_ohline_pca(params, image_e2ds_ini,
                                                 wave_e2ds)
    # else just copy the image and set the sky model to zeros
    else:
        image_e2ds, sky_model = np.array(image), np.zeros_like(image)
    # ----------------------------------------------------------------------
    if not do_precleaning:
        # populate qc params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # populate parameter dictionary
        props = ParamDict()
        props['CORRECTED_E2DS'] = image_e2ds
        props['TRANS_MASK'] = np.ones_like(image).astype(bool)
        props['ABSO_E2DS'] = np.ones_like(image)
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
    spl_others, spl_water = load_tapas_spl(params, recipe, header)
    # ----------------------------------------------------------------------
    # load the snr from e2ds file
    snr = infile.read_header_key_1d_list('KW_EXT_SNR', nbo, dtype=float)
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
                                      wave_e2ds, qc_params, sky_model)
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
    ccf_others_iteations = []
    # ----------------------------------------------------------------------
    # first guess at the velocity of absoprtion is 0 km/s
    dv_abso = 0.0
    # set the iteration number
    iteration = 0
    # just so we have outputs
    dv_water, dv_others = np.nan, np.nan
    trans = np.ones_like(wavemap)
    # loop around until convergence or 20th iteration
    while (dexpo > dexpo_thres) and (iteration < max_iterations):
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
            lothers = mask_others['ll_mask_s'] * scaling * mask_others['w_mask']
            tmp_others = spline(lothers)
            ccf_others[d_it] = np.nanmean(tmp_others[tmp_others != 0.0])
            # computer for water
            lwater = mask_water['ll_mask_s'] * scaling * mask_water['w_mask']
            tmp_water = spline(lwater)
            ccf_water[d_it] = np.nanmean(tmp_water[tmp_water != 0.0])
        # ------------------------------------------------------------------
        # subtract the median of the ccf outside the core of the gaussian.
        #     We take this to be the 'external' part of of the scan range
        # work out the external part mask
        external_mask = np.abs(drange) > ccf_scan_range / 2
        # calculate and subtract external part
        external_water = np.nanmedian(ccf_water[external_mask])
        ccf_water = ccf_water - external_water
        if not force_airmass:
            external_others = np.nanmedian(ccf_others[external_others])
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
            qc_params = [qc_names, qc_values, qc_logic, qc_pass]
            # return qc_exit_tellu_preclean
            return qc_exit_tellu_preclean(params, recipe, image_e2ds,
                                          infile, wave_e2ds, qc_params,
                                          sky_model)
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
            water_guess = [0, 4, np.nanmin(ccf_water)]
            # fit the ccf_water with a guassian
            popt, pcov = curve_fit(mp.gauss_function_nodc, drange, ccf_water,
                                   p0=water_guess)
            # store the velocity of the water
            dv_water = popt[0]
            # make a guess of the others fit parameters (for curve fit)
            others_guess = [0, 4, np.nanmin(ccf_others)]
            # fit the ccf_others with a gaussian
            popt, pconv = curve_fit(mp.gauss_function_nodc, drange, ccf_others,
                                    p0=others_guess)
            # store the velocity of the other species
            dv_others = popt[0]
            # store the mean velocity of water and others
            dv_abso = np.mean([dv_water, dv_others])
        # ------------------------------------------------------------------
        # store the amplitudes of current exponent values
        # for other species
        if force_airmass:
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
            # get others lists as array and sort them
            amp_others_arr = np.array(amp_others_list)
            expo_others_arr = np.array(expo_others_list)
            sortmask = np.argsort(np.abs(amp_others_arr))
            amp_others_arr = amp_others_arr[sortmask]
            expo_others_arr = expo_others_arr[sortmask]
            # get water lists as arrays and sort them
            amp_water_arr = np.array(amp_water_list)
            expo_water_arr = np.array(expo_water_list)
            sortmask = np.argsort(np.abs(amp_water_arr))
            amp_water_arr = amp_water_arr[sortmask]
            expo_water_arr = expo_water_arr[sortmask]
            # --------------------------------------------------------------
            # set value for fit_others
            fit_others = [np.nan, hdr_airmass, np.nan]

            # if we have over 5 iterations we fit a 2nd order polynomial
            # to the lowest 5 amplitudes
            if iteration > 5:
                if not force_airmass:
                    fit_others = np.polyfit(amp_others_arr[0: 4],
                                            expo_others_arr[0:4], 1)
                fit_water = np.polyfit(amp_water_arr[0:4],
                                       expo_water_arr[0:4], 1)
            # else just fit a line
            else:
                if not force_airmass:
                    fit_others = np.polyfit(amp_others_arr, expo_others_arr, 1)
                fit_water = np.polyfit(amp_water_arr, expo_water_arr, 1)
            # --------------------------------------------------------------
            # find best guess for other species exponent
            expo_others = fit_others[1]
            # deal with lower bounds for other species
            if expo_others < others_bounds[0]:
                # set expo_others to others bounds
                expo_others = others_bounds[0]
                # update qc params
                qc_values[2] = expo_others
                qc_pass[2] = 0
                qc_params = [qc_names, qc_values, qc_logic, qc_pass]
                # return qc_exit_tellu_preclean
                return qc_exit_tellu_preclean(params, recipe, image_e2ds,
                                              infile, wave_e2ds, qc_params,
                                              sky_model)
            else:
                qc_values[2] = expo_others
                qc_pass[2] = 1
            # deal with upper bounds for other species
            if expo_others > others_bounds[1]:
                expo_others = others_bounds[1]
                # update qc params
                qc_values[3] = expo_others
                qc_pass[3] = 0
                qc_params = [qc_names, qc_values, qc_logic, qc_pass]
                # return qc_exit_tellu_preclean
                return qc_exit_tellu_preclean(params, recipe, image_e2ds,
                                              infile, wave_e2ds, qc_params,
                                              sky_model)
            else:
                qc_values[3] = expo_others
                qc_pass[3] = 1
            # --------------------------------------------------------------
            # find best guess for water exponent
            expo_water = fit_water[1]
            # deal with lower bounds for water
            if expo_water < water_bounds[0]:
                expo_water = water_bounds[0]
                # update qc params
                qc_values[4] = expo_water
                qc_pass[4] = 0
                qc_params = [qc_names, qc_values, qc_logic, qc_pass]
                # return qc_exit_tellu_preclean
                return qc_exit_tellu_preclean(params, recipe, image_e2ds,
                                              infile, wave_e2ds, qc_params,
                                              sky_model)
            else:
                qc_values[4] = expo_others
                qc_pass[4] = 1
            # deal with upper bounds for water
            if expo_water > water_bounds[1]:
                expo_water = water_bounds[1]
                # update qc params
                qc_values[5] = expo_water
                qc_pass[5] = 0
                qc_params = [qc_names, qc_values, qc_logic, qc_pass]
                # return qc_exit_tellu_preclean
                return qc_exit_tellu_preclean(params, recipe, image_e2ds,
                                              infile, wave_e2ds, qc_params,
                                              sky_model)
            else:
                qc_values[5] = expo_water
                qc_pass[5] = 1
            # --------------------------------------------------------------
            # check whether we have converged yet (by updating dexpo)
            if force_airmass:
                dexpo = np.abs(expo_water_prev - expo_water)
            else:
                part1 = expo_water_prev - expo_water
                part2 = expo_others_prev - expo_others
                dexpo = np.sqrt(part1**2 + part2**2)
        # --------------------------------------------------------------
        # keep track of the convergence params
        expo_water_prev = float(expo_water)
        expo_others_prev = float(expo_others)
        # ------------------------------------------------------------------
        # storage for plotting
        dd_iterations.append(drange)
        ccf_water_iterations.append(ccf_water)
        ccf_others_iteations.append(ccf_others)
        # ------------------------------------------------------------------
        # finally add one to the iterator
        iteration += 1
    # ----------------------------------------------------------------------
    # deal with iterations hitting the max (no convergence)
    if iteration == max_iterations - 1:
        # update qc params
        qc_values[6] = iteration
        qc_pass[6] = 0
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # return qc_exit_tellu_preclean
        return qc_exit_tellu_preclean(params, recipe, image_e2ds, infile,
                                      wave_e2ds, qc_params, sky_model)
    else:
        qc_values[6] = iteration
        qc_pass[6] = 1
    # ----------------------------------------------------------------------
    # show CCF plot to see if correlation peaks have been killed
    recipe.plot('TELLUP_WAVE_TRANS', dd_arr=dd_iterations,
                ccf_water_arr=ccf_water_iterations,
                ccf_others_arr=ccf_water_iterations)
    recipe.plot('SUM_TELLUP_WAVE_TRANS', dd_arr=dd_iterations,
                ccf_water_arr=ccf_water_iterations,
                ccf_others_arr=ccf_water_iterations)
    # plot to show absorption spectrum
    recipe.plot('TELLUP_ABSO_SPEC', trans=trans, wave=wavemap,
                thres=trans_thres, spectrum=spectrum, spectrum_ini=spectrum_ini,
                objname=infile.get_key('KW_OBJNAME', dtype=str),
                clean_ohlines=clean_ohlines)
    recipe.plot('SUM_TELLUP_ABSO_SPEC', trans=trans, wave=wavemap,
                thres=trans_thres, spectrum=spectrum, spectrum_ini=spectrum_ini,
                objname=infile.get_key('KW_OBJNAME', dtype=str),
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
    mask = abso_e2ds < np.exp(trans_thres)
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
                         props, wprops)
    # ----------------------------------------------------------------------
    # return props
    return props


def clean_ohline_pca(params, image, wavemap, **kwargs):
    # load ohline principle components
    func_name = __NAME__ + '.clean_ohline_pca()'
    # ----------------------------------------------------------------------
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLUP_OHLINE_PCA_FILE', 'filename', kwargs,
                      func_name)
    # ----------------------------------------------------------------------
    # get shape of the e2ds
    nbo, nbpix = image.shape
    # ----------------------------------------------------------------------
    # load principle components data file
    ohpcdata, ohfile = drs_data.load_fits_file(params, filename, relfolder,
                                               func_name)
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
    :return:
    """
    # set the function name
    func_name = __NAME__ + '.get_abso_expo()'
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
    # return out vector
    return out_vector


def qc_exit_tellu_preclean(params, recipe, image, infile, wavemap,
                           qc_params, sky_model, **kwargs):
    """
    Provides an exit point for tellu_preclean via a quality control failure

    :param params:
    :param image:
    :param wavemap:
    :param qc_value:
    :param qc_name:
    :param qc_logic:
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
    header = infile.header
    # get airmass from header
    hdr_airmass = infile.get_key('KW_AIRMASS', dtype=float)
    # ----------------------------------------------------------------------
    # load tapas in correct format
    spl_others, spl_water = load_tapas_spl(params, recipe, header)
    # ----------------------------------------------------------------------
    # force expo values
    expo_others = float(hdr_airmass)
    expo_water = float(default_water_abso)
    # get the absorption
    abso_e2ds = get_abso_expo(wavemap, expo_others, expo_water, spl_others,
                              spl_water, ww=qc_ker_width, ex_gau=qc_ker_shape,
                              dv_abso=0.0, ker_thres=ker_thres,
                              wavestart=wavestart, waveend=waveend,
                              dvgrid=dvgrid)
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
                         props, wprops):
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    tpclfile = recipe.outputs['TELLU_PCLEAN'].newcopy(recipe=recipe,
                                                      fiber=fiber)
    # construct the filename from file instance
    tpclfile.construct_filename(params, infile=infile)
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
    dimages = [props['CORRECTED_E2DS'], props['TRANS_MASK'],
               props['ABSO_E2DS'], props['SKY_MODEL'], props['CCFPOWER_WATER'],
               props['CCFPOWER_OTHERS']]
    # add extention info
    kws1 = ['EXTDESC1', 'Corrected', 'Extension 1 description']
    kws2 = ['EXTDESC2', 'Trans Mask', 'Extension 2 description']
    kws3 = ['EXTDESC3', 'ABSO E2DS', 'Extension 3 description']
    kws4 = ['EXTDESC4', 'Sky model', 'Extension 4 description']
    kws5 = ['EXTDESC5', 'CCF power water', 'Extension 5 description']
    kws6 = ['EXTDESC6', 'CCF power others', 'Extension 6 description']
    # add to hdict
    tpclfile.add_hkey(key=kws1)
    tpclfile.add_hkey(key=kws2)
    tpclfile.add_hkey(key=kws3)
    tpclfile.add_hkey(key=kws4)
    tpclfile.add_hkey(key=kws5)
    tpclfile.add_hkey(key=kws6)
    # ----------------------------------------------------------------------
    # need to write these as header keys
    tpclfile.add_hkey('KW_TELLUP_EXPO_WATER', value=props['EXPO_WATER'])
    tpclfile.add_hkey('KW_TELLUP_EXPO_OTHERS', value=props['EXPO_OTHERS'])
    tpclfile.add_hkey('KW_TELLUP_DV_WATER', value=props['DV_WATER'])
    tpclfile.add_hkey('KW_TELLUP_DV_OTHERS', value=props['DV_OTHERS'])
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
        qkwl = ['TQCCL{0}'.format(qc_it), qc_values[qc_it],
               'Logic {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwl)
        # add pass
        qkwp = ['TQCCP{0}'.format(qc_it), qc_values[qc_it],
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
    # TODO: move to language database
    WLOG(params, '', 'Writing file: {0}'.format(tpclfile.filename))
    # write to file
    tpclfile.data = dimages[0]
    tpclfile.write_multi(data_list=dimages[1:])
    # ----------------------------------------------------------------------
    # copy the pre-cleaned file to telluDB
    drs_database.add_file(params, tpclfile)


def read_tellu_preclean(params, recipe, infile, fiber):
    """
    Read all TELLU_PCLEAN files and if infile is one of them load the images
    and properties, else return None

    :param params:
    :param recipe:
    :param infile:
    :param fiber:
    :return:
    """

    # ------------------------------------------------------------------
    # get the tellu preclean map key
    # ----------------------------------------------------------------------
    out_pclean = core.get_file_definition('TELLU_PCLEAN', params['INSTRUMENT'],
                                          kind='red', fiber=fiber)
    # get key
    pclean_key = out_pclean.get_dbkey(fiber=fiber)

    # load tellu file, header and abspaths
    _, pclean_filenames = load_tellu_file(params, pclean_key, infile.header,
                                          n_entries='all', get_image=False,
                                          required=False)
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    tpclfile = recipe.outputs['TELLU_PCLEAN'].newcopy(recipe=recipe,
                                                      fiber=fiber)
    # construct the filename from file instance
    tpclfile.construct_filename(params, infile=infile)

    # if we don't have the file return None
    if pclean_filenames is None:
        return None
    if not tpclfile.basename in pclean_filenames:
        return None
    # ----------------------------------------------------------------------
    # start a parameter dictionary
    props = ParamDict()
    # else we read the multi-fits file
    tpclfile.read_multi()
    # ----------------------------------------------------------------------
    # read qc parameters
    qc_names, qc_values, qc_logic, qc_pass = [], [], [], []
    # first add number of QCs
    num_qcs = tpclfile.get_key('TQCCNUM', dtype=int)
    # now add the keys
    for qc_it in range(num_qcs):
        # add name
        qc_names.append(tpclfile.get_key('TQCCN{0}'.format(qc_it), dtype=str))
        # add value
        value = tpclfile.get_key('TQCCV{0}'.format(qc_it), dtype=str)
        # evaluate vaule
        try:
            qc_values.append(eval(value))
        except:
            qc_values.append(value)
        # add logic
        qc_logic.append(tpclfile.get_key('TQCCL{0}'.format(qc_it), dtype=str))
        # add pass
        qc_pass.append(tpclfile.get_key('TQCCP{0}'.format(qc_it), dtype=int))
    # push into props
    props['QC_PARAMS'] = [qc_names, qc_values, qc_logic, qc_pass]
    # ----------------------------------------------------------------------
    # push arrays into parameter dictionary
    props['CORRECTED_E2DS'] = tpclfile.data_array[0]
    props['TRANS_MASK'] = tpclfile.data_array[1]
    props['ABSO_E2DS'] = tpclfile.data_array[2]
    props['SKY_MODEL'] = tpclfile.data_array[3]
    props['CCFPOWER_WATER'] = tpclfile.data_array[4]
    props['CCFPOWER_OTHERS'] =tpclfile.data_array[5]
    # ----------------------------------------------------------------------
    # get header keys
    tpclfile.add_hkey('KW_TELLUP_EXPO_WATER', value=props['EXPO_WATER'])
    tpclfile.add_hkey('KW_TELLUP_EXPO_OTHERS', value=props['EXPO_OTHERS'])
    tpclfile.add_hkey('KW_TELLUP_DV_WATER', value=props['DV_WATER'])
    tpclfile.add_hkey('KW_TELLUP_DV_OTHERS', value=props['DV_OTHERS'])
    # push into props
    props['EXPO_WATER'] = tpclfile.get_key('KW_TELLUP_EXPO_WATER', dtype=float)
    props['EXPO_OTHERS'] = tpclfile.get_key('KW_TELLUP_EXPO_OTHERS',
                                            dtype=float)
    props['DV_WATER'] = tpclfile.get_key('KW_TELLUP_DV_WATER', dtype=float)
    props['DV_OTHERS'] = tpclfile.get_key('KW_TELLUP_DV_OTHERS', dtype=float)
    # set sources
    keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
            'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'CCFPOWER_WATER',
            'CCFPOWER_OTHERS', 'QC_PARAMS', 'SKY_MODEL']
    props.set_sources(keys, 'header')
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    props['TELLUP_DO_PRECLEANING'] = tpclfile.get_key('KW_TELLUP_DO_PRECLEAN',
                                                      dtype=bool)
    props['TELLUP_D_WATER_ABSO'] = tpclfile.get_key('KW_TELLUP_DFLT_WATER',
                                                    dtype=float)
    props['TELLUP_CCF_SCAN_RANGE'] = tpclfile.get_key('KW_TELLUP_CCF_SRANGE',
                                                      dtype=float)
    props['TELLUP_CLEAN_OH_LINES'] = tpclfile.get_key('KW_TELLUP_CLEAN_OHLINES',
                                                      dtype=bool)
    props['TELLUP_REMOVE_ORDS'] = tpclfile.get_key('KW_TELLUP_REMOVE_ORDS',
                                                   dtype=list, listtype=int)
    props['TELLUP_SNR_MIN_THRES'] = tpclfile.get_key('KW_TELLUP_SNR_MIN_THRES',
                                                     dtype=float)
    kw_dexpo = 'KW_TELLUP_DEXPO_CONV_THRES'
    props['TELLUP_DEXPO_CONV_THRES'] = tpclfile.get_key(kw_dexpo, dtype=float)
    props['TELLUP_DEXPO_MAX_ITR'] = tpclfile.get_key('KW_TELLUP_DEXPO_MAX_ITR',
                                                     dtype=int)
    kw_kthres = 'KW_TELLUP_ABSOEXPO_KTHRES'
    props['TELLUP_ABSO_EXPO_KTHRES'] = tpclfile.get_key(kw_kthres, dtype=float)
    props['TELLUP_WAVE_START'] = tpclfile.get_key('KW_TELLUP_WAVE_START',
                                                  dtype=float)
    props['TELLUP_WAVE_END'] = tpclfile.get_key('KW_TELLUP_WAVE_END',
                                                dtype=float)
    props['TELLUP_DVGRID'] = tpclfile.get_key('KW_TELLUP_DVGRID', dtype=float)
    props['TELLUP_ABSO_EXPO_KWID'] = tpclfile.get_key('KW_TELLUP_ABSOEXPO_KWID',
                                                      dtype=float)
    props['TELLUP_ABSO_EXPO_KEXP'] = tpclfile.get_key('KW_TELLUP_ABSOEXPO_KEXP',
                                                      dtype=float)
    props['TELLUP_TRANS_THRES'] = tpclfile.get_key('KW_TELLUP_TRANS_THRES',
                                                   dtype=float)
    props['TELLUP_TRANS_SIGLIM'] = tpclfile.get_key('TELLUP_TRANS_SIGLIM',
                                                    dtype=float)
    props['TELLUP_FORCE_AIRMASS'] = tpclfile.get_key('KW_TELLUP_FORCE_AIRMASS',
                                                     dtype=bool)
    props['TELLUP_OTHER_BOUNDS'] = tpclfile.get_key('KW_TELLUP_OTHER_BOUNDS',
                                                    dtype=list, listtype=float)
    props['TELLUP_WATER_BOUNDS']  = tpclfile.get_key('KW_TELLUP_WATER_BOUNDS',
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
def load_tellu_file(params, key=None, inheader=None, filename=None,
                    get_image=True, get_header=False, return_entries=False,
                    **kwargs):
    # get keys from params/kwargs
    n_entries = kwargs.get('n_entries', 1)
    required = kwargs.get('required', True)
    mode = kwargs.get('mode', None)
    # valid extension (zero by default)
    ext = kwargs.get('ext', 0)
    # fmt = valid astropy table format
    fmt = kwargs.get('fmt', 'fits')
    # kind = 'image' or 'table'
    kind = kwargs.get('kind', 'image')
    # ----------------------------------------------------------------------
    # deal with filename set
    if filename is not None:
        # get db fits file
        abspath = drs_database.get_db_abspath(params, filename, where='guess')
        image, header = drs_database.get_db_file(params, abspath, ext, fmt,
                                                 kind, get_image, get_header)
        # return here
        if get_header:
            return [image], [header], [abspath]
        else:
            return [image], [abspath]
    # ----------------------------------------------------------------------
    # get telluDB
    tdb = drs_database.get_full_database(params, 'telluric')
    # get calibration entries
    entries = drs_database.get_key_from_db(params, key, tdb, inheader,
                                           n_ent=n_entries, mode=mode,
                                           required=required)
    # ----------------------------------------------------------------------
    # deal with return entries
    if return_entries:
        return entries
    # ----------------------------------------------------------------------
    # get filename col
    filecol = tdb.file_col
    # ----------------------------------------------------------------------
    # storage
    images, headers, abspaths = [], [], []
    # ----------------------------------------------------------------------
    # loop around entries
    for it, entry in enumerate(entries):
        # get entry filename
        filename = entry[filecol]
        # ------------------------------------------------------------------
        # get absolute path
        abspath = drs_database.get_db_abspath(params, filename,
                                              where='telluric')
        # append to storage
        abspaths.append(abspath)
        # load image/header
        image, header = drs_database.get_db_file(params, abspath, ext, fmt,
                                                 kind, get_image, get_header)
        # append to storage
        images.append(image)
        # append to storage
        headers.append(header)
    # ----------------------------------------------------------------------
    # deal with returns with and without header
    if get_header:
        if not required and len(images) == 0:
            return None, None, None
        # deal with if n_entries is 1 (just return file not list)
        if n_entries == 1:
            return images[-1], headers[-1], abspaths[-1]
        else:
            return images, headers, abspaths
    else:
        if not required and len(images) == 0:
            return None, None
        # deal with if n_entries is 1 (just return file not list)
        if n_entries == 1:
            return images[-1], abspaths[-1]
        else:
            return images, abspaths


def load_templates(params, header, objname, fiber):

    # TODO: update - bad loads all files just to get one header
    #   OBJNAME in database --> select most recent and only load that file
    # get file definition
    out_temp = core.get_file_definition('TELLU_TEMP', params['INSTRUMENT'],
                                        kind='red', fiber=fiber)
    # deal with user not using template
    if 'USE_TEMPLATE' in params['INPUTS']:
        if not params['INPUTS']['USE_TEMPLATE']:
            return None, None
    # get key
    temp_key = out_temp.get_dbkey(fiber=fiber)
    # log status
    # TODO: move to language database
    WLOG(params, '', 'Loading {0} files'.format(temp_key))
    # load tellu file, header and abspaths
    temp_out = load_tellu_file(params, temp_key, header, get_header=True,
                               n_entries='all', required=False)
    temp_images, temp_headers, temp_filenames = temp_out

    # deal with no files in database
    if temp_images is None:
        # log that we found no templates in database
        WLOG(params, '', TextEntry('40-019-00003'))
        return None, None
    if len(temp_images) == 0:
        # log that we found no templates in database
        WLOG(params, '', TextEntry('40-019-00003'))
        return None, None
    # storage of valid files
    valid_images, valid_filenames, valid_times = [], [], []
    # loop around header and filter by objname
    for it, temp_header in enumerate(temp_headers):
        # get objname
        temp_objname = temp_header[params['KW_OBJNAME'][0]]
        # if temp_objname is the same as objname (input) then we have a
        #   valid template
        if temp_objname.upper().strip() == objname.upper().strip():
            valid_images.append(temp_images[it])
            valid_filenames.append(temp_filenames[it])

    # deal with no files for this object name
    if len(valid_images) == 0:
        # log that we found no templates for this object
        wargs = [params['KW_OBJNAME'][0], objname]
        WLOG(params, 'info', TextEntry('40-019-00004', args=wargs))
        return None, None
    # log which template we are using
    wargs = [valid_filenames[-1]]
    WLOG(params, 'info', TextEntry('40-019-00005', args=wargs))
    # only return most recent template
    return valid_images[-1], valid_filenames[-1]


def get_transmission_files(params, recipe, header, fiber):
    # get file definition
    out_trans = core.get_file_definition('TELLU_TRANS', params['INSTRUMENT'],
                                         kind='red', fiber=fiber)
    # get key
    trans_key = out_trans.get_dbkey(fiber=fiber)

    # log status
    # TODO: move to language database
    WLOG(params, '', 'Loading {0} files'.format(trans_key))
    # load tellu file, header and abspaths
    _, trans_filenames = load_tellu_file(params, trans_key, header,
                                         n_entries='all', get_image=False)
    # storage for valid files/images/times
    valid_filenames = []
    # loop around header and get times
    for filename in trans_filenames:
        # only add if filename not in list already (files will be overwritten
        #   but we can have multiple entries in database)
        if filename not in valid_filenames:
            # append to list
            valid_filenames.append(filename)
    # convert arrays
    valid_filenames = np.array(valid_filenames)
    # return all valid sorted in time
    return valid_filenames


# =============================================================================
# Tapas functions
# =============================================================================
def load_conv_tapas(params, recipe, header, mprops, fiber, **kwargs):
    func_name = __NAME__ + '.load_conv_tapas()'
    # get parameters from params/kwargs
    tellu_absorbers = pcheck(params, 'TELLU_ABSORBERS', 'absorbers', kwargs,
                             func_name, mapf='list', dtype=str)
    fwhm_pixel_lsf = pcheck(params, 'FWHM_PIXEL_LSF', 'fwhm_lsf', kwargs,
                            func_name)
    # ----------------------------------------------------------------------
    # Load any convolved files from database
    # ----------------------------------------------------------------------
    # get file definition
    if 'TELLU_CONV' in recipe.outputs:
        # get file definition
        out_tellu_conv = recipe.outputs['TELLU_CONV'].newcopy(recipe=recipe,
                                                              fiber=fiber)
        # get key
        conv_key = out_tellu_conv.get_dbkey()
    else:
        # get file definition
        out_tellu_conv = core.get_file_definition('TELLU_CONV',
                                                  params['INSTRUMENT'],
                                                  kind='red', fiber=fiber)
        # get key
        conv_key = out_tellu_conv.get_dbkey(fiber=fiber)
    # load tellu file
    _, conv_paths = load_tellu_file(params, conv_key, header, n_entries='all',
                                    get_image=False, required=False)
    if conv_paths is None:
        conv_paths = []
    # construct the filename from file instance
    out_tellu_conv.construct_filename(params, infile=mprops['WAVEINST'],
                                      path=params['DRS_TELLU_DB'])
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
        tapas_all_species = np.array(out_tellu_conv.data)
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
        out_tellu_conv.write_file(params)

        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
        # npy file must set header/hdict (to update)
        out_tellu_conv.header = header
        out_tellu_conv.hdict = header
        # copy the order profile to the calibDB
        drs_database.add_file(params, out_tellu_conv)

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


def load_tapas_convolved(params, recipe, header, mprops, fiber, **kwargs):
    func_name = __NAME__ + '.load_conv_tapas()'
    # get parameters from params/kwargs
    tellu_absorbers = pcheck(params, 'TELLU_ABSORBERS', 'absorbers', kwargs,
                             func_name)
    fwhm_pixel_lsf = pcheck(params, 'FWHM_PIXEL_LSF', 'fwhm_lsf', kwargs,
                            func_name)
    # ----------------------------------------------------------------------
    # Load any convolved files from database
    # ----------------------------------------------------------------------
    # get file definition
    tellu_conv = core.get_file_definition('TELLU_CONV',
                                              params['INSTRUMENT'],
                                              kind='red', fiber=fiber)
    # make new copy of the file definition
    out_tellu_conv = tellu_conv.newcopy(recipe=recipe)
    # get key
    conv_key = out_tellu_conv.get_dbkey(fiber=fiber)
    # load tellu file
    _, conv_paths = load_tellu_file(params, conv_key, header, n_entries='all',
                                    get_image=False, required=False)
    # construct the filename from file instance
    out_tellu_conv.construct_filename(params, infile=mprops['WAVEINST'],
                                      path=params['DRS_TELLU_DB'])
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
        tapas_all_species = np.array(out_tellu_conv.data)
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
    # else we generate an error
    else:
        # log that no matching tapas convolved file exists
        wargs = [conv_key, out_tellu_conv.filename, func_name]
        WLOG(params, 'error', TextEntry('09-019-00002', args=wargs))


def load_tapas_spl(params, recipe, header):

    # get file definition
    tellu_tapas = core.get_file_definition('TELLU_TAPAS', params['INSTRUMENT'],
                                           kind='red')
    # make new copy of the file definition
    out_tellu_tapas = tellu_tapas.newcopy(recipe=recipe)
    # get key
    conv_key = out_tellu_tapas.get_dbkey()
    # load tellu file
    _, conv_paths = load_tellu_file(params, conv_key, header, n_entries='all',
                                    get_image=False, required=False)
    # construct the filename from file instance
    out_tellu_tapas.construct_filename(params,
                                       path=params['DRS_TELLU_DB'])
    # ----------------------------------------------------------------------
    # if our npy file already exists then we just need to read it
    if (conv_paths is not None) and (out_tellu_tapas.filename in conv_paths):
        out_tellu_tapas.read_file(params)
        # push into arrays
        tmp_tapas = np.array(out_tellu_tapas.data)
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
        # TODO: add to language database
        WLOG(params, '', 'Writing file: {0}'.format(out_tellu_tapas.filename))
        # save to disk
        out_tellu_tapas.data = tmp_tapas
        out_tellu_tapas.write_file(params)
        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
        # npy file must set header/hdict (to update)
        out_tellu_tapas.header = header
        out_tellu_tapas.hdict = header
        # copy the order profile to the telluDB
        drs_database.add_file(params, out_tellu_tapas)
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
        # if no valid pixel, thn skip order
        if mp.nansum(g) != 0:
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

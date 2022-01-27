#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-01-26

@author: cook
"""
import numpy as np
from astropy import constants as cc
from astropy import units as uu
import os
from typing import Optional
import warnings

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.core.core import drs_database
from apero.science.calib import wave
from apero.science.calib import gen_calib
from apero.science.calib import flat_blaze
from apero.science.extract import gen_ext


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.leak.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsNpyFile = drs_file.DrsNpyFile
DrsRecipe = drs_recipe.DrsRecipe
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# -----------------------------------------------------------------------------
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light_kms = cc.c.to(uu.km / uu.s).value
# Get function string
display_func = drs_log.display_func


# =============================================================================
# Define leakage functions
# =============================================================================
def correct_master_dark_fp(params, extractdict, **kwargs):
    # set function name
    func_name = __NAME__ + '.correct_master_dark_fp'

    # load parameters from params/kwargs
    bckgrd_percentile = pcheck(params, 'LEAK_BCKGRD_PERCENTILE',
                               'bckgrd_percentile', kwargs, func_name)
    norm_percentile = pcheck(params, 'LEAK_NORM_PERCENTILE', 'norm_percentile',
                             kwargs, func_name)
    w_smooth = pcheck(params, 'LEAKM_WSMOOTH', 'w_smooth', kwargs, func_name)
    ker_size = pcheck(params, 'LEAKM_KERSIZE', 'ker_size', kwargs, func_name)

    # define a gaussian kernel that goes from +/- ker_size * w_smooth
    xkernel = np.arange(-ker_size * w_smooth, ker_size * w_smooth)
    ykernel = np.exp(-0.5 * (xkernel / w_smooth) ** 2)

    # get this instruments science fibers and reference fiber
    pconst = constants.pload()
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber = pconst.FIBER_KINDS()
    # output storage (dictionary of corrected extracted files)
    outputs = dict()
    # ----------------------------------------------------------------------
    # Deal with loading the reference fiber image props
    # ----------------------------------------------------------------------
    # check for reference fiber in extract dict
    if ref_fiber not in extractdict:
        eargs = [ref_fiber, ', '.join(extractdict.keys()), func_name]
        WLOG(params, 'error', textentry('00-016-00024', args=eargs))
    # get the reference file
    reffile = extractdict[ref_fiber]
    # get dprtype
    dprtype = reffile.get_hkey('KW_DPRTYPE')
    # get dpr type for ref image
    refdpr = pconst.FIBER_DPR_POS(dprtype, ref_fiber)
    # check that refdpr is FP (must be an FP)
    if refdpr != 'FP':
        # log and raise error
        eargs = [ref_fiber, dprtype, func_name]
        WLOG(params, 'error', textentry('00-016-00025', args=eargs))

    # get the data for the reference image
    refimage = reffile.get_data(copy=True)
    # get reference image size
    nord, nbpix = refimage.shape
    # ----------------------------------------------------------------------
    # remove the pedestal from the reference image and work out the amplitude
    #   of the leak from the reference fiber
    # ----------------------------------------------------------------------
    # storage
    ref_amps = np.zeros_like(refimage)
    # loop around the orders
    for order_num in range(nord):
        # remove the pedestal from the FP to avoid an offset from
        #     thermal background
        background = np.nanpercentile(refimage[order_num], bckgrd_percentile)
        refimage[order_num] = refimage[order_num] - background
        # get the amplitudes
        amplitude = np.nanpercentile(refimage[order_num], norm_percentile)
        ref_amps[order_num] = amplitude
        # normalize the reference image by this amplitude
        refimage[order_num] = refimage[order_num] / amplitude

    # save corrected refimage into output storage
    reffile.data = refimage
    outputs[ref_fiber] = reffile

    # ----------------------------------------------------------------------
    # process the science fibers
    # ----------------------------------------------------------------------
    for sci_fiber in sci_fibers:
        # check that science fiber is in extraction dictionary
        if sci_fiber not in extractdict:
            eargs = [sci_fiber, ', '.join(extractdict.keys()), func_name]
            WLOG(params, 'error', textentry('00-016-00026', args=eargs))
        # get the science image
        scifile = extractdict[sci_fiber]
        # get the data for the reference image
        sciimage = scifile.get_data(copy=True)
        # get the science image size
        nord, nbpix = sciimage.shape
        # loop around orders
        for order_num in range(nord):
            # median filtering has to be an odd number
            medfac = 2 * (w_smooth // 2) + 1
            # calculate median filter
            tmpimage = mp.medfilt_1d(sciimage[order_num], medfac)
            # set NaN pixels to zero
            tmpimage[np.isnan(tmpimage)] = 0
            # find a proxy for the low-frequency in the science channel
            mask = np.ones_like(tmpimage)
            mask[tmpimage == 0] = 0
            # calculate low-frequency
            part1 = np.convolve(tmpimage, ykernel, mode='same')
            part2 = np.convolve(mask, ykernel, mode='same')
            with warnings.catch_warnings(record=True) as _:
                low_f = part1 / part2
            # remove the low-frequencies from science image
            sciimage[order_num] = sciimage[order_num] - low_f
            # normalize by the reference amplitudes
            sciimage[order_num] = sciimage[order_num] / ref_amps[order_num]
        # save corrected science image into output storage
        scifile.data = sciimage
        outputs[sci_fiber] = scifile
    # ----------------------------------------------------------------------
    # Make properties dictionary
    props = ParamDict()
    props['LEAK_BCKGRD_PERCENTILE'] = bckgrd_percentile
    props['LEAK_NORM_PERCENTILE'] = norm_percentile
    props['LEAKM_WSMOOTH'] = w_smooth
    props['LEAKM_KERSIZE'] = ker_size
    # set sources
    keys = ['LEAK_BCKGRD_PERCENTILE', 'LEAK_NORM_PERCENTILE',
            'LEAKM_WSMOOTH', 'LEAKM_KERSIZE']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return output dictionary with corrected extracted files
    return outputs, props


def manage_leak_correction(params: ParamDict, recipe: DrsRecipe,
                           eprops: ParamDict, infile: DrsFitsFile,
                           fiber: str,
                           ref_e2ds: Optional[np.ndarray] = None) -> ParamDict:
    """
    Manage the leak correction

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe instance that called this function
    :param eprops: ParamDict, parameter dictionary of extraction data
    :param infile: DrsFitsFile, the input drs file instance (for header)
    :param ref_e2ds: np.ndarray, the reference fiber e2ds
    :param fiber: str, the fiber we are correcting (we only correct science
                  fibers)

    :return: ParamDict, the updated extraction data parameter dictionary
    """
    # set the function name
    func_name = __NAME__ + '.manage_leak_correction()'
    # get dprtype
    dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
    # get the ut file header
    inheader = infile.header
    # get this instruments science fibers and reference fiber
    pconst = constants.pload()
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber = pconst.FIBER_KINDS()
    # get the type of data for each fiber
    ref_type = pconst.FIBER_DATA_TYPE(dprtype, ref_fiber)
    # get vectors from eprops
    uncorr_e2ds = np.array(eprops['E2DS'])
    e2ds = np.array(eprops['E2DS'])
    # ----------------------------------------------------------------------
    # set reason not corrected
    reason = ''
    # deal with quick look
    quicklook = params['EXT_QUICK_LOOK']
    # add to reason
    if quicklook:
        reason += 'QUICKLOOK=True '
    # deal with wanting to do leak correction
    cond1 = not params['INPUTS']['LEAKCORR']
    # add to reason
    if cond1:
        if params['CORRECT_LEAKAGE']:
            reason += '--leakcorr=False '
        else:
            reason += 'CORRECT_LEAKAGE=False '
    # deal with correct fiber
    cond2 = fiber not in sci_fibers
    # add to reason
    if cond2:
        reason += 'FIBER={0} '.format(fiber)
    # make sure reference fiber is an FP
    cond3 = ref_type not in params.listp('LEAKAGE_REF_TYPES', dtype=str)
    # add to reason
    if cond3:
        reason += 'REFTYPE={0} '.format(ref_type)
    # deal with no reference image
    cond4 = ref_e2ds is None
    if cond4:
        reason += 'REF_E2DS=None '
    # if any of these conditions are true do not correct for dark_fp
    if quicklook or cond1 or cond2 or cond3 or cond4:
        # add used parametersLEAK_CORRECTED
        eprops['LEAK_2D_EXTRACT_FILES_USED'] = 'No leak'
        eprops['LEAK_EXTRACT_FILE_USED'] = 'No leak'
        eprops['LEAK_BCKGRD_PERCENTILE_USED'] = 'No leak'
        eprops['LEAK_NORM_PERCENTILE_USED'] = 'No leak'
        eprops['LEAK_LOW_PERCENTILE_USED'] = 'No leak'
        eprops['LEAK_HIGH_PERCENTILE_USED'] = 'No leak'
        eprops['LEAK_BAD_RATIO_OFFSET_USED'] = 'No leak'
        eprops['LEAK_CORRECTED'] = False
        eprops['LEAKM_FILE'] = 'No leak'
        eprops['LEAKM_TIME'] = 'No leak'
        eprops['LEAKM_REFFILE'] = 'No leak'
        eprops['LEAKM_REFTIME'] = 'No leak'
        # set sources
        keys = ['LEAK_2D_EXTRACT_FILES_USED', 'LEAK_EXTRACT_FILE_USED',
                'LEAK_BCKGRD_PERCENTILE_USED', 'LEAK_NORM_PERCENTILE_USED',
                'LEAK_LOW_PERCENTILE_USED', 'LEAK_HIGH_PERCENTILE_USED',
                'LEAK_BAD_RATIO_OFFSET_USED', 'LEAKM_FILE', 'LEAKM_TIME',
                'LEAKM_REFFILE', 'LEAKM_REFTIME']
        eprops.set_sources(keys, func_name)
        # add updated e2ds
        eprops['UNCORR_E2DS'] = uncorr_e2ds
        eprops['E2DS'] = e2ds
        eprops['LEAKCORR'] = np.full_like(e2ds.shape, np.nan)
        # print progress
        WLOG(params, 'info', textentry('40-016-00034', args=[reason]))
        # return update extraction properties
        return eprops
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', textentry('40-016-00033', args=[fiber, dprtype]))
    # correct for leak
    e2ds, leakcorr, props = correct_ext_dark_fp(params, e2ds, ref_e2ds,
                                                inheader, fiber,
                                                database=None)
    # add used parameters
    for key in props:
        eprops.set(key, props[key], source=props.sources[key])
    # add updated e2ds
    eprops['UNCORR_E2DS'] = uncorr_e2ds
    eprops['E2DS'] = e2ds
    eprops['LEAKCORR'] = leakcorr
    eprops['LEAK_CORRECTED'] = True

    # ------------------------------------------------------------------
    # Add debugs for all uncorrected file
    # ------------------------------------------------------------------
    save_uncorrected_ext_fp(params, recipe, infile, eprops, fiber)

    # return update extraction properties
    return eprops


def correct_ext_dark_fp(params, sciimage, refimage, header, fiber,
                        database=None, **kwargs):
    # set the function name
    func_name = __NAME__ + '.correct_ext_dark_fp()'
    # get properties from parameters
    leak2dext = pcheck(params, 'LEAK_2D_EXTRACT_FILES', 'leak2dext', kwargs,
                       func_name, mapf='list')
    extfiletype = pcheck(params, 'LEAK_EXTRACT_FILE', 'extfiletype', kwargs,
                         func_name)
    bckgrd_percentile = pcheck(params, 'LEAK_BCKGRD_PERCENTILE',
                               'bckgrd_percentile', kwargs, func_name)
    norm_percentile = pcheck(params, 'LEAK_NORM_PERCENTILE', 'norm_percentile',
                             kwargs, func_name)
    low_percentile = pcheck(params, 'LEAK_LOW_PERCENTILE', 'low_percentile',
                            kwargs, func_name)
    high_percentile = pcheck(params, 'LEAK_HIGH_PERCENTILE', 'high_percentile',
                             kwargs, func_name)
    bad_ratio = pcheck(params, 'LEAK_BAD_RATIO_OFFSET', 'bad_ratio')
    # group bounding percentiles
    bpercents = [low_percentile, high_percentile]
    # get size of reference image
    nbo, nbpix = sciimage.shape
    # copy images
    refimage = np.array(refimage)
    sciimage = np.array(sciimage)
    # ----------------------------------------------------------------------
    # get this instruments science fibers and reference fiber
    pconst = constants.pload()
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber = pconst.FIBER_KINDS()
    # ----------------------------------------------------------------------
    # get ref leak master for file
    lmout = get_leak_master(params, header, ref_fiber, 'LEAKM_E2DS',
                            database=database)
    rleakfile, rleakmaster, rleaktime = lmout
    # get leak master for fiber
    lmout = get_leak_master(params, header, fiber, 'LEAKM_E2DS',
                            database=database)
    leakfile, leakmaster, leaktime = lmout
    # ----------------------------------------------------------------------
    # store the ratio of observe to master reference
    ref_ratio_arr = np.zeros(nbo)
    dot_ratio_arr = np.zeros(nbo)
    approx_ratio_arr = np.zeros(nbo)
    # store the method used (either "dot" or "approx")
    method = []
    # loop around reference image orders and normalise by percentile
    for order_num in range(nbo):
        # get order values for master
        master_ref_ord = rleakmaster[order_num]
        # remove the pedestal from the FP to avoid an offset from
        #     thermal background
        background = np.nanpercentile(refimage[order_num], bckgrd_percentile)
        refimage[order_num] = refimage[order_num] - background
        # only perform the measurement of the amplitude of the leakage signal
        #  on the lower and upper percentiles. This allows for a small number
        #  of hot/dark pixels along the order. Without this, we end up with
        #  some spurious amplitude values in the frames
        with warnings.catch_warnings(record=True) as _:
            # get percentiles
            low, high = np.nanpercentile(refimage[order_num], bpercents)
            lowm, highm = np.nanpercentile(master_ref_ord, bpercents)
            # translate this into a mask
            mask = refimage[order_num] > low
            mask &= refimage[order_num] < high
            mask &= master_ref_ord > lowm
            mask &= master_ref_ord < highm
        # approximate ratio, we know that frames were normalized with their
        #  "norm_percentile" percentile prior to median combining
        amplitude = np.nanpercentile(refimage[order_num], norm_percentile)
        approx_ratio = 1 / amplitude
        # save to storage
        approx_ratio_arr[order_num] = float(approx_ratio)
        # much more accurate ratio from a dot product
        part1 = mp.nansum(master_ref_ord[mask] * refimage[order_num][mask])
        part2 = mp.nansum(refimage[order_num][mask] ** 2)
        ratio = part1 / part2
        # save to storage
        dot_ratio_arr[order_num] = float(ratio)
        # deal with spurious ref FP ratio
        cond1 = (ratio / approx_ratio) < (1 - bad_ratio)
        cond2 = (ratio / approx_ratio) > (1 + bad_ratio)
        # Ratio must be within (1-badratio) to (1+badratio) of the approximate
        #   ratio -- otherwise ratio is bad
        if cond1 or cond2:
            # log warning that ref FP ratio is spurious
            wargs = [order_num, ratio, approx_ratio, ratio / approx_ratio,
                     1 - bad_ratio, 1 + bad_ratio]
            WLOG(params, 'warning', textentry('10-016-00024', args=wargs),
                 sublevel=4)
            # set the ratio to the approx ratio
            ratio = float(approx_ratio)
            # set the ratio method
            method.append('approx')
        else:
            # set method
            method.append('dot')
        # save ratios to storage
        ref_ratio_arr[order_num] = float(ratio)
    # --------------------------------------------------------------
    # storage for the ratio of leakage
    ratio_leak = np.zeros(nbo)
    # loop around orders
    for order_num in range(nbo):
        # scale the leakage for that order to the observed amplitude
        scale = leakmaster[order_num] / ref_ratio_arr[order_num]
        # apply leakage scaling
        sciimage[order_num] = sciimage[order_num] - scale
        # calculate the ratio of the leakage
        rpart1 = np.nanpercentile(sciimage[order_num], norm_percentile)
        rpart2 = mp.nanmedian(sciimage[order_num])
        ratio_leak[order_num] = rpart1 / rpart2

    # ----------------------------------------------------------------------
    # generate a properties dictionary
    props = ParamDict()
    # ----------------------------------------------------------------------
    # add used parameters
    props['LEAK_2D_EXTRACT_FILES_USED'] = leak2dext
    props['LEAK_EXTRACT_FILE_USED'] = extfiletype
    props['LEAK_BCKGRD_PERCENTILE_USED'] = bckgrd_percentile
    props['LEAK_NORM_PERCENTILE_USED'] = norm_percentile
    props['LEAK_LOW_PERCENTILE_USED'] = low_percentile
    props['LEAK_HIGH_PERCENTILE_USED'] = high_percentile
    props['LEAK_BAD_RATIO_OFFSET_USED'] = bad_ratio
    props['LEAKM_FILE'] = leakfile
    props['LEAKM_TIME'] = leaktime
    props['LEAKM_REFFILE'] = rleakfile
    props['LEAKM_REFTIME'] = rleaktime
    # set sources
    keys = ['LEAK_2D_EXTRACT_FILES_USED', 'LEAK_EXTRACT_FILE_USED',
            'LEAK_BCKGRD_PERCENTILE_USED', 'LEAK_NORM_PERCENTILE_USED',
            'LEAK_LOW_PERCENTILE_USED', 'LEAK_HIGH_PERCENTILE_USED',
            'LEAK_BAD_RATIO_OFFSET_USED', 'LEAKM_FILE', 'LEAKM_TIME',
            'LEAKM_REFFILE', 'LEAKM_REFTIME']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return properties
    return sciimage, ratio_leak, props


def correct_dark_fp(params, extractdict, database=None, **kwargs):
    # set the function name
    func_name = __NAME__ + '.correct_dark_fp()'
    # get properties from parameters
    leak2dext = pcheck(params, 'LEAK_2D_EXTRACT_FILES', 'leak2dext', kwargs,
                       func_name, mapf='list')
    extfiletype = pcheck(params, 'LEAK_EXTRACT_FILE', 'extfiletype', kwargs,
                         func_name)
    bckgrd_percentile = pcheck(params, 'LEAK_BCKGRD_PERCENTILE',
                               'bckgrd_percentile', kwargs, func_name)
    norm_percentile = pcheck(params, 'LEAK_NORM_PERCENTILE', 'norm_percentile',
                             kwargs, func_name)
    low_percentile = pcheck(params, 'LEAK_LOW_PERCENTILE', 'low_percentile',
                            kwargs, func_name)
    high_percentile = pcheck(params, 'LEAK_HIGH_PERCENTILE', 'high_percentile',
                             kwargs, func_name)
    bad_ratio = pcheck(params, 'LEAK_BAD_RATIO_OFFSET', 'bad_ratio')
    # group bounding percentiles
    bpercents = [low_percentile, high_percentile]
    # ----------------------------------------------------------------------
    # get this instruments science fibers and reference fiber
    pconst = constants.pload()
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber = pconst.FIBER_KINDS()
    all_fibers = sci_fibers + [ref_fiber]
    # ----------------------------------------------------------------------
    # get reference file
    ref_file = extractdict[ref_fiber][extfiletype]
    refimage = ref_file.get_data(copy=True)
    ref_header = ref_file.get_header()
    # get size of reference image
    nbo, nbpix = refimage.shape
    # ----------------------------------------------------------------------
    # storage for master files
    master_leaks = dict()
    # load master data
    for fiber in all_fibers:
        # get leak master for file
        _, leakmaster, _ = get_leak_master(params, ref_header, fiber,
                                           'LEAKM_E2DS', database=database)
        # append to storage
        master_leaks[fiber] = leakmaster
    # ----------------------------------------------------------------------
    # store the ratio of observe to master reference
    ref_ratio_arr = np.zeros(nbo)
    dot_ratio_arr = np.zeros(nbo)
    approx_ratio_arr = np.zeros(nbo)
    # store the method used (either "dot" or "approx")
    method = []
    # loop around reference image orders and normalise by percentile
    for order_num in range(nbo):
        # get order values for master
        master_ref_ord = master_leaks[ref_fiber][order_num]
        # remove the pedestal from the FP to avoid an offset from
        #     thermal background
        background = np.nanpercentile(refimage[order_num], bckgrd_percentile)
        refimage[order_num] = refimage[order_num] - background
        # only perform the measurement of the amplitude of the leakage signal
        #  on the lower and upper percentiles. This allows for a small number
        #  of hot/dark pixels along the order. Without this, we end up with
        #  some spurious amplitude values in the frames
        with warnings.catch_warnings(record=True) as _:
            # get percentiles
            low, high = np.nanpercentile(refimage[order_num], bpercents)
            lowm, highm = np.nanpercentile(master_ref_ord, bpercents)
            # translate this into a mask
            mask = refimage[order_num] > low
            mask &= refimage[order_num] < high
            mask &= master_ref_ord > lowm
            mask &= master_ref_ord < highm
        # approximate ratio, we know that frames were normalized with their
        #  "norm_percentile" percentile prior to median combining
        amplitude = np.nanpercentile(refimage[order_num], norm_percentile)
        approx_ratio = 1 / amplitude
        # save to storage
        approx_ratio_arr[order_num] = float(approx_ratio)
        # much more accurate ratio from a dot product
        part1 = mp.nansum(master_ref_ord[mask] * refimage[order_num][mask])
        part2 = mp.nansum(refimage[order_num][mask] ** 2)
        ratio = part1 / part2
        # save to storage
        dot_ratio_arr[order_num] = float(ratio)
        # deal with spurious ref FP ratio
        cond1 = (ratio / approx_ratio) < (1 - bad_ratio)
        cond2 = (ratio / approx_ratio) > (1 + bad_ratio)
        # Ratio must be within (1-badratio) to (1+badratio) of the approximate
        #   ratio -- otherwise ratio is bad
        if cond1 or cond2:
            # log warning that ref FP ratio is spurious
            wargs = [order_num, ratio, approx_ratio, ratio / approx_ratio,
                     1 - bad_ratio, 1 + bad_ratio]
            WLOG(params, 'warning', textentry('10-016-00024', args=wargs),
                 sublevel=4)
            # set the ratio to the approx ratio
            ratio = float(approx_ratio)
            # set the ratio method
            method.append('approx')
        else:
            # set method
            method.append('dot')
        # save ratios to storage
        ref_ratio_arr[order_num] = float(ratio)

    # ----------------------------------------------------------------------
    # storage for extraction outputs
    outputs = dict()
    leakage = dict()
    # ----------------------------------------------------------------------
    # loop around science fibers
    for fiber in sci_fibers:
        # storage for fiber outputs
        outputs[fiber] = dict()
        leakage[fiber] = dict()
        # get the master for this fiber
        master_sci = master_leaks[fiber]
        # loop around extraction types
        for extfiletype in leak2dext:
            # log progress
            wargs = [fiber, extfiletype]
            WLOG(params, 'info', textentry('40-016-00029', args=wargs))
            # get extfile
            extfile = extractdict[fiber][extfiletype]
            # get the extraction image
            extimage = extfile.get_data(copy=True)
            # --------------------------------------------------------------
            # if we are dealing with the E2DS we need the flat
            if extfiletype == 'E2DS_FILE':
                # load the flat file for this fiber
                flat_file, flat = flat_blaze.get_flat(params,
                                                      extfile.get_header(),
                                                      fiber, quiet=True)
            # else we set it to None
            else:
                flat = np.ones_like(extimage)
            # --------------------------------------------------------------
            # storage for the ratio of leakage
            ratio_leak = np.zeros(nbo)
            # loop around orders
            for order_num in range(nbo):
                # scale the leakage for that order to the observed amplitude
                scale = master_sci[order_num] / ref_ratio_arr[order_num]
                # correct for the flat (in E2DS case) - master is E2DSFF
                scale = scale * flat[order_num]
                # apply leakage scaling
                extimage[order_num] = extimage[order_num] - scale
                # calculate the ratio of the leakage
                rpart1 = np.nanpercentile(refimage[order_num], norm_percentile)
                rpart2 = mp.nanmedian(extimage[order_num])
                ratio_leak[order_num] = rpart1 / rpart2
            # update ext file
            extfile.data = extimage
            # add to output
            outputs[fiber][extfiletype] = extfile
            leakage[fiber][extfiletype] = ratio_leak
    # ----------------------------------------------------------------------
    # generate a properties dictionary
    props = ParamDict()
    # ----------------------------------------------------------------------
    # add outputs
    props['OUTPUTS'] = outputs
    props['LEAKAGE'] = leakage
    # set sources
    props.set_sources(['OUTPUTS', 'LEAKAGE'], func_name)
    # ----------------------------------------------------------------------
    # add used parameters
    props['LEAK_2D_EXTRACT_FILES_USED'] = leak2dext
    props['LEAK_EXTRACT_FILE_USED'] = extfiletype
    props['LEAK_BCKGRD_PERCENTILE_USED'] = bckgrd_percentile
    props['LEAK_NORM_PERCENTILE_USED'] = norm_percentile
    props['LEAK_LOW_PERCENTILE_USED'] = low_percentile
    props['LEAK_HIGH_PERCENTILE_USED'] = high_percentile
    props['LEAK_BAD_RATIO_OFFSET_USED'] = bad_ratio
    # set sources
    keys = ['LEAK_2D_EXTRACT_FILES_USED', 'LEAK_EXTRACT_FILE_USED',
            'LEAK_BCKGRD_PERCENTILE_USED', 'LEAK_NORM_PERCENTILE_USED',
            'LEAK_LOW_PERCENTILE_USED', 'LEAK_HIGH_PERCENTILE_USED',
            'LEAK_BAD_RATIO_OFFSET_USED']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return properties
    return props


def dark_fp_regen_s1d(params, recipe, props, database=None, **kwargs):
    # set function name
    func_name = __NAME__ + '.dark_fp_regen_s1d()'
    # get outputs from props
    outputs = props['OUTPUTS']
    # get the leak extract file type
    s1dextfile = pcheck(params, 'EXT_S1D_INFILE', 's1dextfile', kwargs,
                        func_name)
    # leak2dext = params.listp('LEAK_2D_EXTRACT_FILES', dtype=str)
    # storage for s1d outputs
    s1dv_outs = dict()
    s1dw_outs = dict()
    # loop around fibers
    for fiber in outputs:
        # get the e2ds in file type
        extfile = outputs[fiber][s1dextfile]
        # --------------------------------------------------------------
        # load the blaze file for this fiber
        bout = flat_blaze.get_blaze(params, extfile.header, fiber)
        blaze_file, blaze_time, blaze = bout
        # --------------------------------------------------------------
        # load wavelength solution for this fiber (must be from the e2ds file)
        wprops = wave.get_wavesolution(params, recipe, infile=extfile,
                                       fiber=fiber, database=database)
        # --------------------------------------------------------------
        # create 1d spectra (s1d) of the e2ds file
        sargs = [wprops['WAVEMAP'], extfile.get_data(), blaze]
        swprops = gen_ext.e2ds_to_s1d(params, recipe, *sargs, wgrid='wave',
                                      fiber=fiber, s1dkind=s1dextfile)
        svprops = gen_ext.e2ds_to_s1d(params, recipe, *sargs, wgrid='velocity',
                                      fiber=fiber, s1dkind=s1dextfile)
        # add to outputs
        s1dw_outs[fiber] = swprops
        s1dv_outs[fiber] = svprops
    # push updated outputs into props
    props['S1DW'] = s1dw_outs
    props['S1DV'] = s1dv_outs
    props.set_sources(['S1DW', 'S1DV'], func_name)
    # return outputs
    return props


def get_leak_master(params, header, fiber, kind, filename=None,
                    database=None):
    # get file definition
    out_leak = drs_file.get_file_definition(params, kind, block_kind='red')
    # get key
    key = out_leak.get_dbkey()
    # ----------------------------------------------------------------------
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------------
    # load calib file
    ckwargs = dict(key=key, inheader=header, filename=filename, fiber=fiber,
                   userinputkey='LEAKFILE', database=calibdbm)

    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, **ckwargs)
    # get properties from calibration file
    leak = cfile.data
    leak_file = cfile.filename
    leak_time = cfile.mjdmid
    # ------------------------------------------------------------------------
    # log which fpmaster file we are using
    WLOG(params, '', textentry('40-016-00028', args=[leak_file]))
    # return the master image
    return leak_file, leak, leak_time


def master_dark_fp_cube(params, recipe, extractdict):
    # median cube storage dictionary
    medcubedict = dict()
    # loop around fibers
    for fiber in extractdict:
        # get the file list for this fiber
        extfiles = extractdict[fiber]
        # get the first file as reference
        extfile = extfiles[0]
        # construct the leak master file instance
        outfile = recipe.outputs['LEAK_MASTER'].newcopy(params=params,
                                                        fiber=fiber)
        # construct the filename from file instance
        outfile.construct_filename(infile=extfile)
        # copy keys from input file
        outfile.copy_original_keys(extfile)
        # storage for cube
        cube = []
        # loop around files and get data cube
        for it in range(len(extfiles)):
            # add to cube
            cube.append(extfiles[it].get_data())
        # make cube a numpy array
        cube = np.array(cube)
        # produce super dark using median
        medcube = mp.nanmedian(cube, axis=0)
        # delete cube
        del cube
        # add median cube to outfile instance
        outfile.data = medcube
        # add to median cube storage
        medcubedict[fiber] = outfile
    # return median cube storage dictionary
    return medcubedict


def get_extraction_files(params, recipe, infile, extname):
    # get properties from parameters
    leak2dext = params.listp('LEAK_2D_EXTRACT_FILES', dtype=str)
    leak1dext = params.listp('LEAK_1D_EXTRACT_FILES', dtype=str)
    # get this instruments science fibers and reference fiber
    pconst = constants.pload()
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber = pconst.FIBER_KINDS()
    all_fibers = sci_fibers + [ref_fiber]
    # get the input pp list
    rawfiles = infile.get_hkey_1d('KW_INFILE1', dtype=str)
    # get the preprocessed file
    ppfile = infile.intype.newcopy(params=params)
    # get the preprocessed file path
    pppath = os.path.join(params['DRS_DATA_WORKING'], params['OBS_DIR'])
    # get the pp filename
    ppfile.set_filename(os.path.join(pppath, rawfiles[0]))
    # ------------------------------------------------------------------
    # find the extraction recipe
    extrecipe, _ = drs_startup.find_recipe(extname, params['INSTRUMENT'],
                                           mod=recipe.recipemod)
    extrecipe.params = params
    # ------------------------------------------------------------------
    # storage for outputs
    extouts = recipe.outputs.keys()
    outputs = dict()
    for fiber in all_fibers:
        outputs[fiber] = dict()
    # ------------------------------------------------------------------
    # loop around fibers
    for fiber in all_fibers:
        # loop around extraction outputs
        for extout in extouts:
            # get extraction file instance
            outfile = extrecipe.outputs[extout].newcopy(params=params,
                                                        fiber=fiber)
            # construct filename
            outfile.construct_filename(infile=ppfile)
            # read 2D image (not 1D images -- these will be re-generated)
            if extout in leak2dext:
                outfile.read_file()
                # push to storage
                outputs[fiber][extout] = outfile
            # puash 1D images to storage
            if extout in leak1dext:
                # push to storage
                outputs[fiber][extout] = outfile
    # return outputs
    return outputs


def save_uncorrected_ext_fp(params: ParamDict, recipe: DrsRecipe,
                            infile: DrsFitsFile, eprops: ParamDict,
                            fiber: str):
    # -------------------------------------------------------------------------
    # check we want to save uncorrected
    if not params['DEBUG_UNCORR_EXT_FILES']:
        return
    # check that we have corrected leak
    if not eprops['LEAK_CORRECTED']:
        return
    # get a new copy of the e2ds file
    e2dsfile = recipe.outputs['E2DS_FILE'].newcopy(params=params,
                                                   fiber=fiber)
    # construct the filename from file instance
    e2dsfile.construct_filename(infile=infile)
    # define header keys for output file
    # copy keys from input file (excluding loc)
    e2dsfile.copy_original_keys(infile, exclude_groups=['loc'])
    # add version
    e2dsfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    e2dsfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    e2dsfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    e2dsfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    e2dsfile.add_hkey('KW_OUTPUT', value=e2dsfile.name)
    e2dsfile.add_hkey('KW_FIBER', value=fiber)
    # copy data
    e2dsfile.data = eprops['LEAKCORR']
    # -----------------------------------------------------------------
    # get basename
    infile = e2dsfile.basename
    inpath = e2dsfile.filename
    indir = inpath.split(infile)[0]
    # add prefix
    outfile = 'DEBUG-uncorr-{0}'.format(infile)
    # construct full path
    outpath = os.path.join(indir, outfile)
    # set filename
    e2dsfile.set_filename(outpath)
    # log that we are saving e2ds uncorrected debug file
    wargs = [e2dsfile.filename]
    WLOG(params, '', textentry('40-016-00005', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    e2dsfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(e2dsfile)


def ref_fplines(params, recipe, e2dsfile, wavemap, fiber, database=None,
                **kwargs):
    # set up function name
    func_name = display_func('ref_fplines', __NAME__)
    # get constant from params
    allowtypes = pcheck(params, 'WAVE_FP_DPRLIST', 'fptypes', kwargs, func_name,
                        mapf='list')
    # get dprtype
    dprtype = e2dsfile.get_hkey('KW_DPRTYPE', dtype=str)
    # get psuedo constants
    pconst = constants.pload()
    sfibers, rfiber = pconst.FIBER_KINDS()
    # ----------------------------------------------------------------------
    # deal with fiber being the reference fiber
    if fiber != rfiber:
        # Skipping FPLINES (Fiber = {0})'
        WLOG(params, 'debug', textentry('90-016-00003', args=[fiber]))
        return None
    # ----------------------------------------------------------------------
    # deal with allowed dprtypes
    if dprtype not in allowtypes:
        # Skipping FPLINES (DPRTYPE = {0})
        WLOG(params, 'debug', textentry('90-016-000034', args=[dprtype]))
        return None
    # ----------------------------------------------------------------------
    # get master hc lines and fp lines from calibDB
    wout = wave.get_wavelines(params, fiber, infile=e2dsfile,
                              database=database)
    mhclines, mhclsource, mfplines, mfplsource = wout
    # deal with no fplines found
    if mfplines is None:
        return None
    # ----------------------------------------------------------------------
    # generate the fp reference lines
    fpargs = dict(e2dsfile=e2dsfile, wavemap=wavemap, fplines=mfplines)
    rfpl = wave.calc_wave_lines(params, recipe, **fpargs)
    # ----------------------------------------------------------------------
    # return fp lines for e2ds file
    return rfpl


def qc_leak_master(params, medcubes):
    # output storage
    qc_params = dict()
    passed = True
    # loop around fibers
    for fiber in medcubes:
        # log that we are doing qc for a specific fiber
        WLOG(params, 'info', textentry('40-016-00026', args=[fiber]))
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
            passed_fiber = 1
        else:
            for farg in fail_msg:
                WLOG(params, 'warning', textentry('40-005-10002') + farg,
                     sublevel=6)
            passed_fiber = 0
        # store in qc_params
        qc_params_fiber = [qc_names, qc_values, qc_logic, qc_pass]
        # append to storage
        qc_params[fiber] = qc_params_fiber
        passed &= passed_fiber
    # return qc_params and passed
    return qc_params, passed


def qc_leak(params, props, **kwargs):
    # set function name
    func_name = __NAME__ + '.qc_leak()'
    # get outputs from props
    outputs = props['OUTPUTS']
    # get leak extract file
    extname = pcheck(params, 'LEAK_EXTRACT_FILE', 'extname', kwargs,
                     func_name)
    # output storage
    qc_params = dict()
    passed = True
    # loop around fibers
    for fiber in outputs:
        # log that we are doing qc for a specific fiber
        WLOG(params, 'info', textentry('40-016-00026', args=[fiber]))
        # set passed variable and fail message list
        fail_msg = []
        # ------------------------------------------------------------------
        # deal with old qc params
        # ------------------------------------------------------------------
        # get extfile
        extfile = outputs[fiber][extname]
        # copy the quality control from header
        qc_names, qc_values, qc_logic, qc_pass = extfile.get_qckeys()
        # ------------------------------------------------------------------
        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if np.sum(qc_pass) == len(qc_pass):
            WLOG(params, 'info', textentry('40-005-10001'))
            passed_fiber = 1
        else:
            for farg in fail_msg:
                WLOG(params, 'warning', textentry('40-005-10002') + farg,
                     sublevel=6)
            passed_fiber = 0
        # store in qc_params
        qc_params_fiber = [qc_names, qc_values, qc_logic, qc_pass]
        # append to storage
        qc_params[fiber] = qc_params_fiber
        passed &= passed_fiber
    # return qc_params and passed
    return qc_params, passed


def write_leak_master(params, recipe, rawfiles, medcubes, qc_params, props):
    # loop around fibers
    for fiber in medcubes:
        # get outfile for this fiber
        outfile = medcubes[fiber]
        # get qc_params for this fiber
        qc_params_fiber = qc_params[fiber]
        # ------------------------------------------------------------------
        # have already copied original keys in master_dark_fp_cube function
        # data is already added as well
        # so just need other keys
        # ------------------------------------------------------------------
        # add version
        outfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add dates
        outfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
        outfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
        # add process id
        outfile.add_hkey('KW_PID', value=params['PID'])
        # add output tag
        outfile.add_hkey('KW_OUTPUT', value=outfile.name)
        # add input files
        outfile.add_hkey_1d('KW_INFILE1', values=rawfiles, dim1name='file')
        # add input files to outfile
        outfile.infiles = list(rawfiles)
        # add qc parameters
        outfile.add_qckeys(qc_params_fiber)
        # add leak parameters from props (if set)
        if props is not None:
            outfile.add_hkey('KW_LEAK_BP_U',
                             value=props['LEAK_BCKGRD_PERCENTILE'])
            outfile.add_hkey('KW_LEAK_NP_U',
                             value=props['LEAK_NORM_PERCENTILE'])
            outfile.add_hkey('KW_LEAK_WSMOOTH', value=props['LEAKM_WSMOOTH'])
            outfile.add_hkey('KW_LEAK_KERSIZE', value=props['LEAKM_KERSIZE'])
        # log that we are saving rotated image
        wargs = [fiber, outfile.filename]
        WLOG(params, '', textentry('40-016-00025', args=wargs))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=outfile)]
            name_list += ['PARAM_TABLE']
        # write image to file
        outfile.write_multi(data_list=data_list, name_list=name_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(outfile)
        # update med cubes (as it was shallow copied this is just for sanity
        #    check)
        medcubes[fiber] = outfile
    # return medcubes
    return medcubes


def write_leak(params, recipe, inputs, props, qc_params, **kwargs):
    # set function name
    func_name = __NAME__ + '.write_leak()'
    # get outputs from props
    outputs = props['OUTPUTS']
    s1dw_outs = props['S1DW']
    s1dv_outs = props['S1DV']
    # set header keys to add
    keys = ['KW_LEAK_BP_U', 'KW_LEAK_NP_U', 'KW_LEAK_LP_U', 'KW_LEAK_UP_U',
            'KW_LEAK_BADR_U']
    values = ['LEAK_BCKGRD_PERCENTILE_USED', 'LEAK_NORM_PERCENTILE_USED',
              'LEAK_LOW_PERCENTILE_USED', 'LEAK_HIGH_PERCENTILE_USED',
              'LEAK_BAD_RATIO_OFFSET_USED']

    # ----------------------------------------------------------------------
    # 2D files
    # ----------------------------------------------------------------------
    # loop around fibers
    for fiber in outputs:
        # loop around files
        for extname in outputs[fiber]:
            # get the s1d in file type
            extfile = outputs[fiber][extname]
            # add infiles to out file
            extfile.infiles = [extfile.basename]
            # add leak corr key
            extfile.add_hkey('KW_LEAK_CORR', value=True)
            # loop around leak keys to add
            for it in range(len(keys)):
                extfile.add_hkey(keys[it], value=props[values[it]])
            # add qc parameters
            extfile.add_qckeys(qc_params[fiber])
            # log that we are saving file
            wargs = [fiber, extname, extfile.filename]
            WLOG(params, '', textentry('40-016-00030', args=wargs))
            # define multi lists
            data_list, name_list = [], []
            # snapshot of parameters
            if params['PARAMETER_SNAPSHOT']:
                data_list += [params.snapshot_table(recipe,
                                                    drsfitsfile=extfile)]
                name_list += ['PARAM_TABLE']
            # write image to file
            extfile.write_multi(data_list=data_list, name_list=name_list,
                                block_kind=recipe.out_block_str,
                                runstring=recipe.runstring)
            # add back to outputs dictionary (used for s1d)
            outputs[fiber][extname] = extfile
            # add to output files (for indexing)
            recipe.add_output_file(extfile)

    # ----------------------------------------------------------------------
    # S1D files
    # ----------------------------------------------------------------------
    # get the leak extract file type
    s1dextfile = pcheck(params, 'EXT_S1D_INFILE', 's1dextfile', kwargs,
                        func_name)
    # loop around fibers
    for fiber in outputs:
        # get extfile
        extfile = outputs[fiber][s1dextfile]
        # get s1d props for this fiber
        swprops = s1dw_outs[fiber]
        svprops = s1dv_outs[fiber]
        # get input extraction file (1D case)
        s1dwfile = inputs[fiber]['S1D_W_FILE']
        s1dvfile = inputs[fiber]['S1D_V_FILE']
        # ------------------------------------------------------------------
        # Store S1D_W in file
        # ------------------------------------------------------------------
        # copy header from e2dsff file
        s1dwfile.copy_header(extfile)
        # set output key
        s1dwfile.add_hkey('KW_OUTPUT', value=s1dwfile.name)
        # add new header keys
        s1dwfile = gen_ext.add_s1d_keys(s1dwfile, swprops)
        # copy in files
        s1dwfile.infiles = list(extfile.infiles)
        # copy data
        s1dwfile.data = swprops['S1DTABLE']
        # must change the datatype to 'table'
        s1dwfile.datatype = 'table'
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        wargs = [fiber, 'wave', s1dwfile.filename]
        WLOG(params, '', textentry('40-016-00031', args=wargs))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=s1dwfile)]
            name_list += ['PARAM_TABLE']
        # write image to file
        s1dwfile.write_multi(data_list=data_list, name_list=name_list,
                             block_kind=recipe.out_block_str,
                             runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(s1dwfile)
        # ------------------------------------------------------------------
        # Store S1D_V in file
        # ------------------------------------------------------------------
        # copy header from e2dsff file
        s1dvfile.copy_header(extfile)
        # add new header keys
        s1dvfile = gen_ext.add_s1d_keys(s1dvfile, svprops)
        # copy in files
        s1dvfile.infiles = list(extfile.infiles)
        # set output key
        s1dvfile.add_hkey('KW_OUTPUT', value=s1dvfile.name)
        # copy data
        s1dvfile.data = svprops['S1DTABLE']
        # must change the datatype to 'table'
        s1dvfile.datatype = 'table'
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        wargs = [fiber, 'velocity', s1dvfile.filename]
        WLOG(params, '', textentry('40-016-00031', args=wargs))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=s1dvfile)]
            name_list += ['PARAM_TABLE']
        # write image to file
        s1dvfile.write_multi(data_list=data_list, name_list=name_list,
                             block_kind=recipe.out_block_str,
                             runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(s1dvfile)
        # ------------------------------------------------------------------


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

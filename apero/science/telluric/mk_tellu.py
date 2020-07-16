#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-07-2020-07-15 17:56

@author: cook
"""
from astropy.table import Table
import numpy as np
from astropy.time import Time
from scipy.ndimage import filters
from scipy.optimize import curve_fit
import os
import warnings
from collections import OrderedDict

from apero import core
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.science.calib import wave
from apero.science.telluric import gen_tellu


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.mk_tellu.py'
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

# =============================================================================
# General functions
# =============================================================================
# TODO: move to math
from scipy.interpolate import InterpolatedUnivariateSpline
# TODO: move to math
def lowpassfilter(v, w=101):
    # provide a low-pass filter of the spectrum by performing a running median.
    # To speed things up and
    # avoid discontinuies, we take the median in steps of 1/4th of the filter
    # size and spline afterward
    # indices along input vector
    index = np.arange(len(v))
    # placeholders for x and y position along vector
    xmed = []
    ymed = []
    for i in np.arange(0,len(v),w//4):
        pixval = index[i:i+w]
        # if no finite value, continue
        if np.max(np.isfinite(v[pixval])) == 0:
            continue
        pixval = pixval[np.isfinite(v[pixval])]
        if np.max(np.isfinite(v[pixval])) == 0:
            continue
        xmed.append(np.nanmean(pixval))
        ymed.append(np.nanmedian(v[pixval]))
    xmed = np.array(xmed,dtype = float)
    ymed = np.array(ymed,dtype = float)
    #print(xmed)
    if len(xmed) < 3:
        return np.zeros_like(v)+np.nan
    if len(xmed) != len(np.unique(xmed)):
        xmed2 = np.unique(xmed)
        ymed2 = np.zeros_like(xmed2)
        for i in range(len(xmed2)):
            ymed2[i] = np.mean(ymed[xmed == xmed2[i]])
        xmed = xmed2
        ymed = ymed2
    spline = InterpolatedUnivariateSpline(xmed,ymed, k=1, ext=3)
    return spline(np.arange(len(v)))



def calculate_telluric_absorption(params, recipe, image, template,
                                  template_file, header, mprops, wprops,
                                  tapas_props, bprops, **kwargs):
    func_name = __NAME__ + '.calculate_telluric_absoprtion()'
    # get constatns from params/kwargs
    default_conv_width = pcheck(params, 'MKTELLU_DEFAULT_CONV_WIDTH',
                                'default_conv_width', kwargs, func_name)
    finer_conv_width = pcheck(params, 'MKTELLU_FINER_CONV_WIDTH',
                              'finer_conv_width', kwargs, func_name)
    clean_orders = pcheck(params, 'MKTELLU_CLEAN_ORDERS', 'clean_orders',
                          kwargs, func_name, mapf='list', dtype=int)
    med_filt1 = pcheck(params, 'MKTELLU_TEMP_MED_FILT', 'med_filt', kwargs,
                       func_name)

    # TODO: remove unused parameters
    dparam_threshold = pcheck(params, 'MKTELLU_DPARAMS_THRES',
                              'dparam_threshold', kwargs, func_name)
    max_iteration = pcheck(params, 'MKTELLU_MAX_ITER', 'max_iteration',
                           kwargs, func_name)
    threshold_transmission_fit = pcheck(params, 'MKTELLU_THRES_TRANSFIT',
                                        'treshold_transmission_fit', kwargs,
                                        func_name)
    transfit_upper_bad = pcheck(params, 'MKTELLU_TRANS_FIT_UPPER_BAD',
                                'transfit_upper_bad', kwargs, func_name)
    min_watercol = pcheck(params, 'MKTELLU_TRANS_MIN_WATERCOL', 'min_watercol',
                          kwargs, func_name)
    max_watercol = pcheck(params, 'MKTELLU_TRANS_MAX_WATERCOL', 'max_watercol',
                          kwargs, func_name)
    min_number_good_points = pcheck(params, 'MKTELLU_TRANS_MIN_NUM_GOOD',
                                    'min_number_good_points', kwargs, func_name)
    btrans_percentile = pcheck(params, 'MKTELLU_TRANS_TAU_PERCENTILE',
                               'btrans_percentile', kwargs, func_name)
    nsigclip = pcheck(params, 'MKTELLU_TRANS_SIGMA_CLIP', 'nsigclip',
                      kwargs, func_name)
    med_filt2 = pcheck(params, 'MKTELLU_TRANS_TEMPLATE_MEDFILT',
                       'med_filt', kwargs, func_name)
    small_weight = pcheck(params, 'MKTELLU_SMALL_WEIGHTING_ERROR',
                          'small_weight', kwargs, func_name)
    tellu_med_sampling = pcheck(params, 'IMAGE_PIXEL_SIZE', 'med_sampling',
                                kwargs, func_name)
    plot_order_nums = pcheck(params, 'MKTELLU_PLOT_ORDER_NUMS',
                             'plot_order_nums', kwargs, func_name,
                             mapf='list', dtype=int)
    tau_water_upper = pcheck(params, 'MKTELLU_TAU_WATER_ULIMIT',
                             'tau_water_upper', kwargs, func_name)
    tau_others_lower = pcheck(params, 'MKTELLU_TAU_OTHER_LLIMIT',
                              'tau_water_lower', kwargs, func_name)
    tau_others_upper = pcheck(params, 'MKTELLU_TAU_OTHER_ULIMIT',
                              'tau_others_upper', kwargs, func_name)
    tapas_small_number = pcheck(params, 'MKTELLU_SMALL_LIMIT',
                                'tapas_small_number', kwargs, func_name)
    hbandlower = pcheck(params, 'MKTELLU_HBAND_LOWER', 'hbandlower', kwargs,
                        func_name)
    hbandupper = pcheck(params, 'MKTELLU_HBAND_UPPER', 'hbandupper', kwargs,
                        func_name)
    # ------------------------------------------------------------------
    # copy image
    image1 = np.array(image)
    # get berv from bprops
    berv = bprops['USE_BERV']
    # deal with bad berv (nan or None)
    if berv in [np.nan, None] or not isinstance(berv, (int, float)):
        eargs = [berv, func_name]
        WLOG(params, 'error', TextEntry('09-016-00004', args=eargs))
    # get airmass from header
    airmass = header[params['KW_AIRMASS'][0]]
    # get master wave map
    mwavemap = mprops['WAVEMAP']
    # get wave map
    wavemap = wprops['WAVEMAP']
    # get dimensions of data
    nbo, nbpix = image1.shape
    # get the tapas data
    tapas_water = tapas_props['TAPAS_WATER']
    tapas_others = tapas_props['TAPAS_OTHER']

    # ------------------------------------------------------------------
    # Shift the image to the master grid
    # ------------------------------------------------------------------
    image1 = gen_tellu.wave_to_wave(params, image1, wavemap, mwavemap)

    # ------------------------------------------------------------------
    # Apply template
    # ------------------------------------------------------------------
    # set the default convolution width for each order
    wconv = np.repeat(default_conv_width, nbo).astype(float)
    # deal with no template
    if template is None:
        # set a flag to tell us that we didn't start with a template
        template_flag = True
        # assume template is ones everywhere
        template = np.ones_like(image1).astype(float)
        # check that clean orders are valid
        for clean_order in clean_orders:
            if (clean_order < 0) or (clean_order >= nbo):
                # log error: one of the orders is out of bounds
                wargs = ['MKTELLU_CLEAN_ORDERS', clean_order, func_name]
                WLOG(params, 'error', TextEntry('09-019-00001', args=wargs))
        # make clean_orders a numpy array
        clean_orders = np.array(clean_orders).astype(int)
        # if we don't have a template then we use a small kernel on only
        #    relatively clean orders
        wconv[clean_orders] = finer_conv_width
    # else we need to divide by template (after shifting)
    else:
        # set a flag to tell us that we didn't start with a template
        template_flag = False
        # wavelength offset from BERV
        dvshift = mp.relativistic_waveshift(berv, units='km/s')
        # median-filter the template. we know that stellar features
        #    are very broad. this avoids having spurious noise in our templates
        # loop around each order
        for order_num in range(nbo):
            # only keep non NaNs
            keep = np.isfinite(template[order_num])
            # apply median filter
            mfargs = [template[order_num, keep], med_filt1]
            # TODO: move lowpassfilter to math
            template[order_num, keep] = lowpassfilter(*mfargs)

        # loop around each order again
        for order_num in range(nbo):
            # only keep non NaNs
            keep = np.isfinite(template[order_num])
            # if less than 50% of the order is considered valid, then set
            #     template value to 1 this only apply to the really contaminated
            #     orders
            if mp.nansum(keep) > nbpix // 2:
                # get the wave and template masked arrays
                keepwave = mwavemap[order_num, keep]
                keeptmp = template[order_num, keep]
                # spline the good values
                spline = mp.iuv_spline(keepwave * dvshift, keeptmp, k=1,
                                       ext=3)
                # interpolate good values onto full array
                template[order_num] = spline(mwavemap[order_num])
            else:
                template[order_num] = np.repeat(1.0, nbpix)

        # divide observed spectrum by template. This gets us close to the
        #    actual sky transmission. We will iterate on the exact shape of the
        #    SED by finding offsets of sp relative to 1 (after correcting form
        #    the TAPAS).
        image1 = image1 / template

    # ------------------------------------------------------------------
    # Low pass filtering of hot star (create SED)
    # ------------------------------------------------------------------

    # first guess at the SED estimate for the hot start (we guess with a
    #   spectrum full of ones
    sed = np.ones_like(mwavemap)
    # then we correct with out first estimate of the absorption
    for order_num in range(image1.shape[0]):
        # get the smoothing size from wconv
        smooth = int(wconv[order_num])
        # median filter
        # TODO: move lowpassfilter to math
        sed[order_num] = lowpassfilter(image1[order_num], smooth)
    # ---------------------------------------------------------------------
    # plot mk tellu wave flux plot for specified orders
    for order_num in plot_order_nums:
        # TODO: remove tau1 from plots
        tau1 = np.ones_like(image1)
        keep = np.ones_like(image1).astype(bool)
        # plot debug plot
        recipe.plot('MKTELLU_WAVE_FLUX2', keep=keep, wavemap=mwavemap,
                    tau1=tau1, sp=image, oimage=image1, sed=sed,
                    order=order_num, has_template=(not template_flag),
                    template=template)
        # plot summary plot
        recipe.plot('SUM_MKTELLU_WAVE_FLUX', keep=keep, wavemap=mwavemap,
                    tau1=tau1, sp=image, oimage=image1, sed=sed,
                    order=order_num, has_template=(not template_flag),
                    template=template)
    # ---------------------------------------------------------------------
    # calculate transmission map
    transmission_map = image1 / sed
    # ---------------------------------------------------------------------
    # add output dictionary
    tprops = ParamDict()
    # TODO: passed is not used recov airmass + recov water from EA clean function
    tprops['PASSED'] = True
    tprops['RECOV_AIRMASS'] = airmass
    tprops['RECOV_WATER'] = 1.5
    tprops['AIRMASS'] = airmass


    tprops['IMAGE_OUT'] = image1
    tprops['SED_OUT'] = sed
    tprops['TEMPLATE'] = template
    tprops['TEMPLATE_FLAG'] = template_flag
    tprops['TRANMISSION_MAP'] = transmission_map
    tprops['TEMPLATE_FILE'] = template_file
    # set sources
    keys = ['PASSED', 'RECOV_AIRMASS', 'RECOV_WATER', 'IMAGE_OUT', 'SED_OUT',
            'TEMPLATE', 'TEMPLATE_FLAG', 'TRANMISSION_MAP', 'AIRMASS',
            'TEMPLATE_FILE']
    tprops.set_sources(keys, func_name)
    # add constants
    tprops['DEFAULT_CWIDTH'] = default_conv_width
    tprops['FINER_CWIDTH'] = finer_conv_width
    tprops['TEMP_MED_FILT'] = med_filt1

    # TODO: remove unused
    tprops['DPARAM_THRES'] = np.nan
    tprops['MAX_ITERATIONS'] = np.nan
    tprops['THRES_TRANSFIT'] = np.nan
    tprops['MIN_WATERCOL'] = np.nan
    tprops['MAX_WA   TERCOL'] = np.nan
    tprops['MIN_NUM_GOOD'] = np.nan
    tprops['BTRANS_PERCENT'] = np.nan
    tprops['NSIGCLIP'] = np.nan
    tprops['TRANS_TMEDFILT'] = np.nan
    tprops['SMALL_W_ERR'] = np.nan
    tprops['IMAGE_PIXEL_SIZE'] = np.nan
    tprops['TAU_WATER_UPPER'] = np.nan
    tprops['TAU_OTHER_LOWER'] = np.nan
    tprops['TAU_OTHER_UPPER'] = np.nan
    tprops['TAPAS_SMALL_NUM'] = np.nan
    # set sources
    keys = ['DEFAULT_CWIDTH', 'FINER_CWIDTH', 'TEMP_MED_FILT',
            'DPARAM_THRES', 'MAX_ITERATIONS', 'THRES_TRANSFIT', 'MIN_WATERCOL',
            'MAX_WATERCOL', 'MIN_NUM_GOOD', 'BTRANS_PERCENT', 'NSIGCLIP',
            'TRANS_TMEDFILT', 'SMALL_W_ERR', 'IMAGE_PIXEL_SIZE',
            'TAU_WATER_UPPER', 'TAU_OTHER_LOWER', 'TAU_OTHER_UPPER',
            'TAPAS_SMALL_NUM']

    keys = ['DEFAULT_CWIDTH', 'FINER_CWIDTH', 'TEMP_MED_FILT']

    tprops.set_sources(keys, func_name)
    # return tprops
    return tprops


# =============================================================================
# QC and summary functions
# =============================================================================
def mk_tellu_quality_control(params, tprops, infile, **kwargs):
    func_name = __NAME__ + '.mk_tellu_quality_control()'
    # get parameters from params/kwargs
    snr_order = pcheck(params, 'MKTELLU_QC_SNR_ORDER', 'snr_order', kwargs,
                       func_name)
    qc_snr_min = pcheck(params, 'MKTELLU_QC_SNR_MIN', 'qc_snr_min', kwargs,
                        func_name)
    qc_airmass_diff = pcheck(params, 'MKTELLU_QC_AIRMASS_DIFF',
                             'qc_airmass_diff', kwargs, func_name)
    qc_min_watercol = pcheck(params, 'MKTELLU_TRANS_MIN_WATERCOL',
                             'qc_min_watercol', kwargs, func_name)
    qc_max_watercol = pcheck(params, 'MKTELLU_TRANS_MAX_WATERCOL',
                             'qc_min_watercol', kwargs, func_name)
    # get the text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # get data from tprops
    transmission_map = tprops['TRANMISSION_MAP']
    image1 = tprops['IMAGE_OUT']
    calc_passed = tprops['PASSED']
    airmass = tprops['AIRMASS']
    recovered_airmass = tprops['RECOV_AIRMASS']
    recovered_water = tprops['RECOV_WATER']
    # set passed variable and fail message list
    fail_msg = []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
    # if array is completely NaNs it shouldn't pass
    if np.sum(np.isfinite(transmission_map)) == 0:
        fail_msg.append(textdict['40-019-00006'])
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append('NaN')
    qc_names.append('image')
    qc_logic.append('image is all NaN')
    # ----------------------------------------------------------------------
    # get SNR for each order from header
    nbo, nbpix = image1.shape
    snr = infile.read_header_key_1d_list('KW_EXT_SNR', nbo, dtype=float)
    # check that SNR is high enough
    if snr[snr_order] < qc_snr_min:
        fargs = [snr_order, snr[snr_order], qc_snr_min]
        fail_msg.append(textdict['40-019-00007'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(snr[snr_order])
    qc_name_str = 'SNR[{0}]'.format(snr_order)
    qc_names.append(qc_name_str)
    qc_logic.append('{0} < {1:.2f}'.format(qc_name_str, qc_snr_min))
    # ----------------------------------------------------------------------
    # check that the file passed the CalcTelluAbsorption sigma clip loop
    if not calc_passed:
        fargs = [infile.basename]
        fail_msg.append(textdict['40-019-00008'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(infile.basename)
    qc_names.append('FILE')
    qc_logic.append('FILE did not converge')
    # ----------------------------------------------------------------------
    # check that the airmass is not too different from input airmass
    airmass_diff = np.abs(recovered_airmass - airmass)
    if airmass_diff > qc_airmass_diff:
        fargs = [recovered_airmass, airmass, qc_airmass_diff]
        fail_msg.append(textdict['40-019-00009'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(airmass_diff)
    qc_names.append('airmass_diff')
    qc_logic.append('airmass_diff > {0:.2f}'.format(qc_airmass_diff))
    # ----------------------------------------------------------------------
    # check that the water vapor is within limits
    water_cond1 = recovered_water < qc_min_watercol
    water_cond2 = recovered_water > qc_max_watercol
    # check both conditions
    if water_cond1 or water_cond2:
        fargs = [qc_min_watercol, qc_max_watercol, recovered_water]
        fail_msg.append(textdict['40-019-00010'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # get args for qc_logic
    fargs = [qc_min_watercol, qc_max_watercol]
    # add to qc header lists
    qc_values.append(recovered_water)
    qc_names.append('RECOV_WATER')
    qc_msg = 'RECOV_WATER not between {0:.3f} and {1:.3f}'
    qc_logic.append(qc_msg.format(*fargs))
    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #     quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params, passed


def mk_tellu_summary(recipe, it, params, qc_params, tellu_props, fiber):
    # add qc params (fiber specific)
    recipe.plot.add_qc_params(qc_params, fiber=fiber)
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_MKTELL_DEF_CONV_WID',
                         value=tellu_props['DEFAULT_CWIDTH'])
    recipe.plot.add_stat('KW_MKTELL_FIN_CONV_WID',
                         value=tellu_props['FINER_CWIDTH'])
    recipe.plot.add_stat('KW_MKTELL_TEMP_MEDFILT',
                         value=tellu_props['TEMP_MED_FILT'])
    recipe.plot.add_stat('KW_MKTELL_DPARAM_THRES',
                         value=tellu_props['DPARAM_THRES'])
    recipe.plot.add_stat('KW_MKTELL_MAX_ITER',
                         value=tellu_props['MAX_ITERATIONS'])
    recipe.plot.add_stat('KW_MKTELL_THRES_TFIT',
                         value=tellu_props['THRES_TRANSFIT'])
    recipe.plot.add_stat('KW_MKTELL_MIN_WATERCOL',
                         value=tellu_props['MIN_WATERCOL'])
    recipe.plot.add_stat('KW_MKTELL_MAX_WATERCOL',
                         value=tellu_props['MAX_WATERCOL'])
    recipe.plot.add_stat('KW_MKTELL_MIN_NUM_GOOD',
                         value=tellu_props['MIN_NUM_GOOD'])
    recipe.plot.add_stat('KW_MKTELL_BTRANS_PERC',
                         value=tellu_props['BTRANS_PERCENT'])
    recipe.plot.add_stat('KW_MKTELL_NSIGCLIP',
                         value=tellu_props['NSIGCLIP'])
    recipe.plot.add_stat('KW_MKTELL_TRANS_TMFILT',
                         value=tellu_props['TRANS_TMEDFILT'])
    recipe.plot.add_stat('KW_MKTELL_SMALL_W_ERR',
                         value=tellu_props['SMALL_W_ERR'])
    recipe.plot.add_stat('KW_MKTELL_IM_PSIZE',
                         value=tellu_props['IMAGE_PIXEL_SIZE'])
    recipe.plot.add_stat('KW_MKTELL_TAU_WATER_U',
                         value=tellu_props['TAU_WATER_UPPER'])
    recipe.plot.add_stat('KW_MKTELL_TAU_OTHER_L',
                         value=tellu_props['TAU_OTHER_LOWER'])
    recipe.plot.add_stat('KW_MKTELL_TAU_OTHER_U',
                         value=tellu_props['TAU_OTHER_UPPER'])
    recipe.plot.add_stat('KW_MKTELL_TAPAS_SNUM',
                         value=tellu_props['TAPAS_SMALL_NUM'])
    recipe.plot.add_stat('KW_MKTELL_AIRMASS',
                         value=tellu_props['RECOV_AIRMASS'])
    recipe.plot.add_stat('KW_MKTELL_WATER',
                         value=tellu_props['RECOV_WATER'])
    # construct summary (outside fiber loop)
    recipe.plot.summary_document(it)


# =============================================================================
# Write functions
# =============================================================================
def mk_tellu_write_trans_file(params, recipe, infile, rawfiles, fiber, combine,
                              tapas_props, mprops, nprops, tprops, qc_params):
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    transfile = recipe.outputs['TELLU_TRANS'].newcopy(recipe=recipe,
                                                      fiber=fiber)
    # construct the filename from file instance
    transfile.construct_filename(params, infile=infile)
    # ------------------------------------------------------------------
    # copy keys from input file
    transfile.copy_original_keys(infile, exclude_groups='wave')
    # add wave keys
    transfile = wave.add_wave_keys(params, transfile, mprops)
    # add version
    transfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    transfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    transfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    transfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    transfile.add_hkey('KW_OUTPUT', value=transfile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    transfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add  calibration files used
    transfile.add_hkey('KW_CDBBLAZE', value=nprops['BLAZE_FILE'])
    transfile.add_hkey('KW_CDBWAVE', value=mprops['WAVEFILE'])
    # ----------------------------------------------------------------------
    # add qc parameters
    transfile.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # add telluric constants used
    if tprops['TEMPLATE_FLAG']:
        transfile.add_hkey('KW_MKTELL_TEMP_FILE', value=tprops['TEMPLATE_FILE'])
    else:
        transfile.add_hkey('KW_MKTELL_TEMP_FILE', value='None')
    # add blaze parameters
    transfile.add_hkey('KW_MKTELL_BLAZE_PRCT', value=nprops['BLAZE_PERCENTILE'])
    transfile.add_hkey('KW_MKTELL_BLAZE_CUT', value=nprops['BLAZE_CUT_NORM'])
    # add tapas parameteres
    transfile.add_hkey('KW_MKTELL_TAPASFILE', value=tapas_props['TAPAS_FILE'])
    transfile.add_hkey('KW_MKTELL_FWHMPLSF',
                       value=tapas_props['FWHM_PIXEL_LSF'])
    # add tprops parameters
    transfile.add_hkey('KW_MKTELL_DEF_CONV_WID', value=tprops['DEFAULT_CWIDTH'])
    transfile.add_hkey('KW_MKTELL_FIN_CONV_WID', value=tprops['FINER_CWIDTH'])
    transfile.add_hkey('KW_MKTELL_TEMP_MEDFILT', value=tprops['TEMP_MED_FILT'])
    transfile.add_hkey('KW_MKTELL_DPARAM_THRES', value=tprops['DPARAM_THRES'])
    transfile.add_hkey('KW_MKTELL_MAX_ITER', value=tprops['MAX_ITERATIONS'])
    transfile.add_hkey('KW_MKTELL_THRES_TFIT', value=tprops['THRES_TRANSFIT'])
    transfile.add_hkey('KW_MKTELL_MIN_WATERCOL', value=tprops['MIN_WATERCOL'])
    transfile.add_hkey('KW_MKTELL_MAX_WATERCOL', value=tprops['MAX_WATERCOL'])
    transfile.add_hkey('KW_MKTELL_MIN_NUM_GOOD', value=tprops['MIN_NUM_GOOD'])
    transfile.add_hkey('KW_MKTELL_BTRANS_PERC', value=tprops['BTRANS_PERCENT'])
    transfile.add_hkey('KW_MKTELL_NSIGCLIP', value=tprops['NSIGCLIP'])
    transfile.add_hkey('KW_MKTELL_TRANS_TMFILT', value=tprops['TRANS_TMEDFILT'])
    transfile.add_hkey('KW_MKTELL_SMALL_W_ERR', value=tprops['SMALL_W_ERR'])
    transfile.add_hkey('KW_MKTELL_IM_PSIZE', value=tprops['IMAGE_PIXEL_SIZE'])
    transfile.add_hkey('KW_MKTELL_TAU_WATER_U', value=tprops['TAU_WATER_UPPER'])
    transfile.add_hkey('KW_MKTELL_TAU_OTHER_L', value=tprops['TAU_OTHER_LOWER'])
    transfile.add_hkey('KW_MKTELL_TAU_OTHER_U', value=tprops['TAU_OTHER_UPPER'])
    transfile.add_hkey('KW_MKTELL_TAPAS_SNUM', value=tprops['TAPAS_SMALL_NUM'])
    # ----------------------------------------------------------------------
    # save recovered airmass and water vapor
    transfile.add_hkey('KW_MKTELL_AIRMASS', value=tprops['RECOV_AIRMASS'])
    transfile.add_hkey('KW_MKTELL_WATER', value=tprops['RECOV_WATER'])
    # ----------------------------------------------------------------------
    # copy data
    transfile.data = tprops['TRANMISSION_MAP']
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', TextEntry('40-019-00011', args=[transfile.filename]))
    # write image to file
    transfile.write_file()
    # add to output files (for indexing)
    recipe.add_output_file(transfile)
    # ------------------------------------------------------------------
    # return transmission file instance
    return transfile


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

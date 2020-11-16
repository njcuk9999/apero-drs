#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-07-2020-07-15 17:56

@author: cook
"""
import numpy as np

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log, drs_file
from apero.science.calib import wave
from apero.science.telluric import gen_tellu


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.mk_tellu.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# General functions
# =============================================================================
def calculate_tellu_res_absorption(params, recipe, image, template,
                                   template_file, header, mprops, wprops,
                                   bprops, tpreprops, **kwargs):
    func_name = __NAME__ + '.calculate_telluric_absoprtion()'
    # get constatns from params/kwargs
    default_conv_width = pcheck(params, 'MKTELLU_DEFAULT_CONV_WIDTH',
                                'default_conv_width', kwargs, func_name)
    med_filt1 = pcheck(params, 'MKTELLU_TEMP_MED_FILT', 'med_filt', kwargs,
                       func_name)
    plot_order_nums = pcheck(params, 'MKTELLU_PLOT_ORDER_NUMS',
                             'plot_order_nums', kwargs, func_name,
                             mapf='list', dtype=int)
    # ------------------------------------------------------------------
    # copy image
    image1 = np.array(image)
    # get berv from bprops
    berv = bprops['USE_BERV']
    # deal with bad berv (nan or None)
    if berv in [np.nan, None] or not isinstance(berv, (int, float)):
        eargs = [berv, func_name]
        WLOG(params, 'error', textentry('09-016-00004', args=eargs))
    # get airmass from header
    airmass = header[params['KW_AIRMASS'][0]]
    # get master wave map
    mwavemap = mprops['WAVEMAP']
    # get wave map
    wavemap = wprops['WAVEMAP']
    # get dimensions of data
    nbo, nbpix = image1.shape

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
            template[order_num, keep] = mp.lowpassfilter(*mfargs)
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
                spline = mp.iuv_spline(keepwave * dvshift, keeptmp, k=1, ext=3)
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
        sed[order_num] = mp.lowpassfilter(image1[order_num], smooth)
    # ---------------------------------------------------------------------
    # plot mk tellu wave flux plot for specified orders
    for order_num in plot_order_nums:
        # plot debug plot
        recipe.plot('MKTELLU_WAVE_FLUX2', wavemap=mwavemap, sp=image,
                    oimage=image1, sed=sed, order=order_num,
                    has_template=(not template_flag), template=template)
        # plot summary plot
        recipe.plot('SUM_MKTELLU_WAVE_FLUX', wavemap=mwavemap, sp=image,
                    oimage=image1, sed=sed, order=order_num,
                    has_template=(not template_flag), template=template)
    # ---------------------------------------------------------------------
    # calculate transmission map
    transmission_map = image1 / sed
    # ---------------------------------------------------------------------
    # add output dictionary
    tprops = ParamDict()
    tprops['PASSED'] = True
    tprops['RECOV_AIRMASS'] = tpreprops['EXPO_OTHERS']
    tprops['RECOV_WATER'] = tpreprops['EXPO_WATER']
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
    tprops['TEMP_MED_FILT'] = med_filt1
    # set sources
    keys = ['DEFAULT_CWIDTH', 'TEMP_MED_FILT']
    tprops.set_sources(keys, func_name)
    # return tprops
    return tprops


# =============================================================================
# QC and summary functions
# =============================================================================
def mk_tellu_quality_control(params, tprops, infile, tpreprops, **kwargs):
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
    # deal with tellu precleaning qc params - just add them correctly
    tqc_names, tqc_values, tqc_logic, tqc_pass = tpreprops['QC_PARAMS']
    # loop around all tqc
    for qc_it in range(len(tqc_names)):
        # if tqc_pass failed (zero) make fail message
        if tqc_pass[qc_it] == 0:
            fail_msg.append(tqc_logic[qc_it].lower())
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(tqc_values[qc_it])
        qc_names.append(tqc_names[qc_it])
        qc_logic.append(tqc_logic[qc_it])
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
    snr = infile.get_hkey_1d('KW_EXT_SNR', nbo, dtype=float)
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
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
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
    recipe.plot.add_stat('KW_MKTELL_TEMP_MEDFILT',
                         value=tellu_props['TEMP_MED_FILT'])
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
                              mprops, nprops, tprops, tpreprops, qc_params):
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    transfile = recipe.outputs['TELLU_TRANS'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    transfile.construct_filename(infile=infile)
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
    # add tprops parameters
    transfile.add_hkey('KW_MKTELL_DEF_CONV_WID', value=tprops['DEFAULT_CWIDTH'])
    transfile.add_hkey('KW_MKTELL_TEMP_MEDFILT', value=tprops['TEMP_MED_FILT'])
    # ----------------------------------------------------------------------
    # add tellu pre-clean keys
    transfile.add_hkey('KW_TELLUP_EXPO_WATER', value=tpreprops['EXPO_WATER'])
    transfile.add_hkey('KW_TELLUP_EXPO_OTHERS', value=tpreprops['EXPO_OTHERS'])
    transfile.add_hkey('KW_TELLUP_DV_WATER', value=tpreprops['DV_WATER'])
    transfile.add_hkey('KW_TELLUP_DV_OTHERS', value=tpreprops['DV_OTHERS'])
    transfile.add_hkey('KW_TELLUP_DO_PRECLEAN',
                      value=tpreprops['TELLUP_DO_PRECLEANING'])
    transfile.add_hkey('KW_TELLUP_DFLT_WATER',
                      value=tpreprops['TELLUP_D_WATER_ABSO'])
    transfile.add_hkey('KW_TELLUP_CCF_SRANGE',
                      value=tpreprops['TELLUP_CCF_SCAN_RANGE'])
    transfile.add_hkey('KW_TELLUP_CLEAN_OHLINES',
                      value=tpreprops['TELLUP_CLEAN_OH_LINES'])
    transfile.add_hkey('KW_TELLUP_REMOVE_ORDS',
                      value=tpreprops['TELLUP_REMOVE_ORDS'], mapf='list')
    transfile.add_hkey('KW_TELLUP_SNR_MIN_THRES',
                      value=tpreprops['TELLUP_SNR_MIN_THRES'])
    transfile.add_hkey('KW_TELLUP_DEXPO_CONV_THRES',
                      value=tpreprops['TELLUP_DEXPO_CONV_THRES'])
    transfile.add_hkey('KW_TELLUP_DEXPO_MAX_ITR',
                      value=tpreprops['TELLUP_DEXPO_MAX_ITR'])
    transfile.add_hkey('KW_TELLUP_ABSOEXPO_KTHRES',
                      value=tpreprops['TELLUP_ABSO_EXPO_KTHRES'])
    transfile.add_hkey('KW_TELLUP_WAVE_START',
                      value=tpreprops['TELLUP_WAVE_START'])
    transfile.add_hkey('KW_TELLUP_WAVE_END',
                      value=tpreprops['TELLUP_WAVE_END'])
    transfile.add_hkey('KW_TELLUP_DVGRID',
                      value=tpreprops['TELLUP_DVGRID'])
    transfile.add_hkey('KW_TELLUP_ABSOEXPO_KWID',
                      value=tpreprops['TELLUP_ABSO_EXPO_KWID'])
    transfile.add_hkey('KW_TELLUP_ABSOEXPO_KEXP',
                      value=tpreprops['TELLUP_ABSO_EXPO_KEXP'])
    transfile.add_hkey('KW_TELLUP_TRANS_THRES',
                      value=tpreprops['TELLUP_TRANS_THRES'])
    transfile.add_hkey('KW_TELLUP_TRANS_SIGL',
                      value=tpreprops['TELLUP_TRANS_SIGLIM'])
    transfile.add_hkey('KW_TELLUP_FORCE_AIRMASS',
                      value=tpreprops['TELLUP_FORCE_AIRMASS'])
    transfile.add_hkey('KW_TELLUP_OTHER_BOUNDS',
                      value=tpreprops['TELLUP_OTHER_BOUNDS'], mapf='list')
    transfile.add_hkey('KW_TELLUP_WATER_BOUNDS',
                      value=tpreprops['TELLUP_WATER_BOUNDS'], mapf='list')
    # ----------------------------------------------------------------------
    # save recovered airmass and water vapor
    transfile.add_hkey('KW_MKTELL_AIRMASS', value=tprops['RECOV_AIRMASS'])
    transfile.add_hkey('KW_MKTELL_WATER', value=tprops['RECOV_WATER'])
    # ----------------------------------------------------------------------
    # copy data
    transfile.data = tprops['TRANMISSION_MAP']
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-019-00011', args=[transfile.filename]))
    # write image to file
    transfile.write_file(kind=recipe.outputtype, runstring=recipe.runstring)
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

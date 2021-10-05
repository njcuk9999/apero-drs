#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-07-2020-07-15 17:56

@author: cook
"""
import warnings

import numpy as np
from typing import List, Tuple

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core import math as mp
from apero.io import drs_fits
from apero.io import drs_table
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
def make_trans_cube(params: ParamDict, transfiles: List[str]
                    ) -> Tuple[np.ndarray, drs_fits.Table]:
    # -------------------------------------------------------------------------
    # print progress
    # TODO: move to language database
    WLOG(params, '', 'Making Transmission cube')
    # get parameters from params
    snr_order = params['MKTELLU_QC_SNR_ORDER']
    water_key = params['KW_TELLUP_EXPO_WATER'][0]
    others_key = params['KW_TELLUP_EXPO_OTHERS'][0]
    snr_key = params['KW_EXT_SNR'][0].format(snr_order)
    objname_key = params['KW_OBJNAME'][0]
    mjdmid_key = params['KW_MID_OBS_TIME'][0]
    # load first transfile as reference
    refimage, refhdr = drs_fits.readfits(params, transfiles[0], gethdr=True)
    # set up storage for the absorption
    trans_cube = np.zeros([refimage.shape[0], refimage.shape[1],
                           len(transfiles)])
    # get vectors
    expo_water = np.zeros(len(transfiles), dtype=float)
    expo_others = np.zeros(len(transfiles), dtype=float)
    snr = np.zeros(len(transfiles), dtype=float)
    mjdmids = np.zeros(len(transfiles), dtype=float)
    objnames = np.array(['NULL'] * len(transfiles))
    # load all the trans files
    for it, filename in enumerate(transfiles):
        # load trans image
        tout = drs_fits.readfits(params, filename, gethdr=True)
        transimage, transhdr = tout
        # make sure we have required header key for expo_water
        if water_key not in transhdr:
            wargs = [water_key, transfiles[it]]
            WLOG(params, '', textentry('40-019-00050', args=wargs))
        # make sure we have required header key for expo_others
        elif others_key not in transhdr:
            wargs = [others_key, transfiles[it]]
            WLOG(params, '', textentry('40-019-00050', args=wargs))
        else:
            # push data into abso array
            with warnings.catch_warnings(record=True) as _:
                trans_cube[:, :, it] = np.log(transimage)
            # get header keys
            expo_water[it] = float(transhdr[water_key])
            expo_others[it] = float(transhdr[others_key])
            snr[it] = float(transhdr[snr_key])
            objnames[it] = str(transhdr[objname_key])
            mjdmids[it] = float(transhdr[mjdmid_key])
    # -------------------------------------------------------------------------
    # setup table
    columns = ['TRANS_FILE', 'EXPO_H2O', 'EXPO_OTHERS', 'SNR', 'OBJNAME',
               'MJDMID']
    values = [transfiles, expo_water, expo_others, snr, objnames, mjdmids]
    # construct table
    trans_table = drs_table.make_table(params, columns=columns, values=values)
    # -------------------------------------------------------------------------
    # return the vectors
    return trans_cube, trans_table



def make_trans_model(params: ParamDict, transcube: np.ndarray,
                     transtable: drs_fits.Table) -> ParamDict:
    # set function name
    func_name = display_func('make_trans_model', __NAME__)
    # get values from params
    sigma_cut = params['TELLU_TRANS_MODEL_SIG']
    # get the minimum number of trans files required
    min_trans_files = len(transtable) // 10
    # get vectors from table
    expo_water = transtable['EXPO_H2O']
    expo_others = transtable['EXPO_OTHERS']
    # get a reference trans file from cube (first trans file)
    ref_trans = transcube[:, :, 0]
    # -------------------------------------------------------------------------
    # print progress
    # TODO: move to language database
    WLOG(params, '', 'Calculating Transmission model')
    # -------------------------------------------------------------------------
    # sample vectors for the reconstruction
    sample = np.zeros([3, len(expo_water)])
    # bias level of the residual
    sample[0] = 1
    # water abso
    sample[1] = expo_water
    # dry abso
    sample[2] = expo_others
    # -------------------------------------------------------------------------
    # create the reference vectors
    zero_residual = np.full_like(ref_trans, np.nan)
    expo_water_residual = np.full_like(ref_trans, np.nan)
    expo_others_residual = np.full_like(ref_trans, np.nan)
    # loop around all orders
    for order_num in range(ref_trans.shape[0]):
        # print progress
        # TODO: move to language database
        margs = [order_num, ref_trans.shape[0]]
        WLOG(params, '', '\tProcessing order {0} / {1}'.format(*margs))
        # loop around all pixels in order
        for ix in range(ref_trans.shape[1]):
            # get one pixel of the trans_cube for all observations
            trans_slice = transcube[order_num, ix, :]
            # deal with not having enough pixels (skip)
            if np.sum(np.isfinite(trans_slice)) < min_trans_files:
                continue
            # construct a linear model with offset and water+dry components
            worst_offender = np.inf
            # loop until no point is an outlier beyond "sigma cut" sigma
            while worst_offender > sigma_cut:
                # get the linear minimization between trans files and our sample
                amp, recon = mp.linear_minimization(trans_slice, sample)
                # work out the sigma between trans slice and recon
                res = trans_slice - recon
                sigma = res / mp.estimate_sigma(res)
                # re-calculate worst offender
                worst_pos = np.nanargmax(sigma)
                worst_offender = sigma[worst_pos]
                # deal with worst offender - remove worst
                if worst_offender > sigma_cut:
                    trans_slice[worst_pos] = np.nan
                # else we are good - push values into output vectors
                else:
                    zero_residual[order_num, ix] = amp[0]
                    expo_water_residual[order_num, ix] = amp[1]
                    expo_others_residual[order_num, ix] = amp[2]
                # if we have less than the minimum number of points left
                #   stop here
                if np.sum(np.isfinite(trans_slice)) < min_trans_files:
                    break
    # -------------------------------------------------------------------------
    # return e2ds shaped vectors in props
    props = ParamDict()
    props['ZERO_RES'] = zero_residual
    props['WATER_RES'] = expo_water_residual
    props['OTHERS_RES'] = expo_others_residual
    props['N_TRANS_FILES'] = len(transtable)
    props['MIN_TRANS_FILES'] = min_trans_files
    props['SIGMA_CUT'] = sigma_cut
    # set source
    keys = ['ZERO_RES', 'WATER_RES', 'OTHERS_RES', 'N_TRANS_FILES',
            'MIN_TRANS_FILES', 'SIGMA_CUT']
    props.set_sources(keys, func_name)
    # return parameter dictionary
    return props


def calculate_tellu_res_absorption(params, recipe, image, template,
                                   template_props, header, mprops, wprops,
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
    tprops['TEMP_FILE'] = template_props['TEMP_FILE']
    tprops['TEMP_NUM'] = template_props['TEMP_NUM']
    tprops['TEMP_HASH'] = template_props['TEMP_HASH']
    tprops['TEMP_TIME'] = template_props['TEMP_TIME']
    # set sources
    keys = ['PASSED', 'RECOV_AIRMASS', 'RECOV_WATER', 'IMAGE_OUT', 'SED_OUT',
            'TEMPLATE', 'TEMPLATE_FLAG', 'TRANMISSION_MAP', 'AIRMASS',
            'TEMP_FILE', 'TEMP_NUM', 'TEMP_HASH']
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
        fail_msg.append(textentry('40-019-00006'))
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
        fail_msg.append(textentry('40-019-00007', args=fargs))
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
        fail_msg.append(textentry('40-019-00008', args=fargs))
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
        fail_msg.append(textentry('40-019-00009', args=fargs))
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
        fail_msg.append(textentry('40-019-00010', args=fargs))
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


def mk_model_qc(params: ParamDict) -> Tuple[list, int]:
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # no quality control currently
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc params and passed
    return qc_params, passed


def mk_model_summary(recipe, params, qc_params, tprops):
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])

    recipe.plot.add_stat('KW_MKMODEL_NFILES', value=tprops['N_TRANS_FILES'])
    recipe.plot.add_stat('KW_MKMODEL_MIN_FILES',
                         value=tprops['MIN_TRANS_FILES'])
    recipe.plot.add_stat('KW_MKMODEL_SIGCUT', value=tprops['SIGMA_CUT'])
    # construct summary (outside fiber loop)
    recipe.plot.summary_document(0, qc_params)


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
    transfile = wave.add_wave_keys(transfile, mprops)
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
    # add infiles to outfile
    transfile.infiles = list(hfiles)
    # add  calibration files used
    transfile.add_hkey('KW_CDBBLAZE', value=nprops['BLAZE_FILE'])
    transfile.add_hkey('KW_CDTBLAZE', value=nprops['BLAZE_TIME'])
    transfile.add_hkey('KW_CDBWAVE', value=mprops['WAVEFILE'])
    transfile.add_hkey('KW_CDTWAVE', value=mprops['WAVETIME'])
    # ----------------------------------------------------------------------
    # add qc parameters
    transfile.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # add telluric constants used
    if tprops['TEMPLATE_FLAG']:
        transfile.add_hkey('KW_MKTELL_TEMP_FILE', value=tprops['TEMP_FILE'])
        transfile.add_hkey('KW_MKTELL_TEMPNUM', value=tprops['TEMP_NUM'])
        transfile.add_hkey('KW_MKTELL_TEMPHASH', value=tprops['TEMP_HASH'])
        transfile.add_hkey('KW_MKTELL_TEMPTIME', value=tprops['TEMP_TIME'])
    else:
        transfile.add_hkey('KW_MKTELL_TEMP_FILE', value='None')
        transfile.add_hkey('KW_MKTELL_TEMPNUM', value=0)
        transfile.add_hkey('KW_MKTELL_TEMPHASH', value='None')
        transfile.add_hkey('KW_MKTELL_TEMPTIME', value='None')
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
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=transfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    transfile.write_multi(data_list=data_list, name_list=name_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(transfile)
    # ------------------------------------------------------------------
    # return transmission file instance
    return transfile


def mk_write_model(params, recipe, tprops, transtable, fiber, qc_params):
        # ------------------------------------------------------------------
        # write the template file (TELLU_TEMP)
        # ------------------------------------------------------------------
        # get copy of instance of file
        model_file = recipe.outputs['TRANS_MODEL'].newcopy(params=params,
                                                           fiber=fiber)
        # construct the filename from file instance
        filename = model_file.basename.format(fiber)
        model_file.construct_filename(filename=filename)
        # ------------------------------------------------------------------
        # add version
        model_file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add dates
        model_file.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
        model_file.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
        # add process id
        model_file.add_hkey('KW_PID', value=params['PID'])
        # add output tag
        model_file.add_hkey('KW_OUTPUT', value=model_file.name)
        # add qc parameters
        model_file.add_qckeys(qc_params)
        # add constants
        model_file.add_hkeys('KW_MKMODEL_NFILES', value=tprops['N_TRANS_FILES'])
        model_file.add_hkeys('KW_MKMODEL_MIN_FILES',
                             value=tprops['MIN_TRANS_FILES'])
        model_file.add_hkeys('KW_MKMODEL_SIGCUT', value=tprops['SIGMA_CUT'])
        # set data
        model_file.data = tprops['ZERO_RES']
        # log that we are saving s1d table
        WLOG(params, '', textentry('40-019-00029', args=[model_file.filename]))
        # define multi lists
        data_list = [tprops['WATER_RES'], tprops['OTHERS_RES'], transtable]
        datatype_list = ['image', 'image', 'table']
        name_list = ['ZERO_RES', 'H2O_RES', 'DRY_RES', 'TRANS_TABLE']
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=model_file)]
            name_list += ['PARAM_TABLE']
            datatype_list += ['table']
        # write multi
        model_file.write_multi(data_list=data_list, name_list=name_list,
                                  datatype_list=datatype_list,
                                  block_kind=recipe.out_block_str,
                                  runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(model_file)
        # return the template file
        return model_file


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

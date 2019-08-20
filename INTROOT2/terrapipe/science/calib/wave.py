#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-27 at 13:54

@author: cook
"""
from __future__ import division
from astropy import constants as cc
from astropy import units as uu
import itertools
import numpy as np
import os
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe.core import math
from terrapipe import locale
from terrapipe.core.core import drs_database
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.io import drs_data
from terrapipe.io import drs_table
from . import general

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.wave.py'
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
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define user functions
# =============================================================================
def get_masterwave_filename(params, fiber):
    func_name = __NAME__ + '.get_masterwave_filename()'
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # deal with fibers that we don't have
    usefiber = pconst.FIBER_WAVE_TYPES(fiber)
    # ------------------------------------------------------------------------
    # get file definition
    out_wave = core.get_file_definition('WAVEM', params['INSTRUMENT'],
                                        kind='red')
    # get calibration key
    key = out_wave.get_dbkey(fiber=usefiber)
    # ------------------------------------------------------------------------
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')
    # get filename col
    filecol = cdb.file_col
    # get the badpix entries
    waveentries = cdb.get_entry(key)
    # get filename
    filename = waveentries[filecol][-1]
    # get absolute path
    abspath = os.path.join(params['DRS_CALIB_DB'], filename)
    # return the last valid wave entry
    return abspath


def get_wavesolution(params, recipe, header=None, infile=None, fiber=None,
                     **kwargs):
    """
    Get the wavelength solution

    Wavelength solution will come from "filename" if keyword argument is set

    Wavelength solution will come from calibration database if:

    1) params['CALIB_DB_FORCE_WAVESOL'] is True
    2) keyword argument "force" is True
    3) header and infile.header are not defined (None)

    Otherwise wavelength solution will come from header

    :param params: parameter dictionary, ParamDict containing constants
    :param recipe: DrsRecipe instance, the recipe instance used
    :param header: FitsHeader or None, the header to use
    :param infile: DrsFitsFile or None, the infile associated with the header
                   can be used instead of header
    :param fiber: str, the fiber to get the wave solution for
    :param kwargs: keyword arguments passed to function

    :keyword force: bool, if True forces wave solution to come from calibDB
    :keyword filename: str or None, the filename to get wave solution from
                       this will overwrite all other options
    :return:
    """
    func_name = __NAME__ + '.get_wavesolution()'
    # get parameters from params/kwargs
    filename = kwargs.get('filename', None)
    # ------------------------------------------------------------------------
    # check for filename in inputs
    filename = general.get_input_files(params, 'WAVEFILE', filename)
    # ------------------------------------------------------------------------
    force = pcheck(params, 'CALIB_DB_FORCE_WAVESOL', 'force', kwargs,
                   func_name)
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # deal with fibers that we don't have
    usefiber = pconst.FIBER_WAVE_TYPES(fiber)
    # ------------------------------------------------------------------------
    # get file definition
    out_wave = core.get_file_definition('WAVE', params['INSTRUMENT'],
                                        kind='red')
    # get calibration key
    key = out_wave.get_dbkey(fiber=usefiber)
    # ------------------------------------------------------------------------
    # check infile is instance of DrsFitsFile
    if infile is not None:
        if isinstance(infile, drs_file.DrsFitsFile):
            eargs = [type(infile), func_name]
            WLOG(params, 'error', TextEntry('00-017-00001', args=eargs))
    # ------------------------------------------------------------------------
    # deal with no header but an infile
    if header is None and infile is not None:
        header = infile.header
    # ------------------------------------------------------------------------
    # check whether we need to force from database
    if header is None:
        force = True
    else:
        # force to calibDB if not in the header
        force = force or (params['KW_WAVE_NBO'][0] not in header)
        force = force or (params['KW_WAVE_DEG'][0] not in header)
        force = force or (params['KW_CDBWAVE'][0] not in header)
    # ------------------------------------------------------------------------
    # Mode 1: wave filename defined
    # ------------------------------------------------------------------------
    # if filename is defined get wave file from this file
    if filename is not None:
        # construct new infile instance and read data/header
        wavefile = out_wave.newcopy(filename=filename, recipe=recipe,
                                    fiber=usefiber)
        wavefile.read()
        # get wave map
        wavemap = np.array(wavefile.data)
        # set wave source of wave file
        wavesource = 'filename'
    # ------------------------------------------------------------------------
    # Mode 2: force from calibDB
    # ------------------------------------------------------------------------
    # if we are forcing from calibDB get the wave file from calibDB
    elif force:
        # get calibDB
        cdb = drs_database.get_full_database(params, 'calibration')
        # get filename col
        filecol = cdb.file_col
        # get the badpix entries
        waveentries = drs_database.get_key_from_db(params, key, cdb, header,
                                                   n_ent=1, required=False)
        # if there are no wave entries use master wave file
        if len(waveentries) == 0:
            # log warning that no entries were found so using master
            WLOG(params, 'warning', TextEntry('10-017-00001', args=[key]))
            # get master path
            wavefilepath = get_masterwave_filename(params, fiber=usefiber)
        else:
            # get badpix filename
            wavefilename = waveentries[filecol][0]
            wavefilepath = os.path.join(params['DRS_CALIB_DB'], wavefilename)
        # construct new infile instance and read data/header
        wavefile = out_wave.newcopy(filename=wavefilepath, recipe=recipe,
                                    fiber=usefiber)
        wavefile.read()
        # get wave map
        wavemap = np.array(wavefile.data)
        # set source of wave file
        wavesource = 'calibDB'
    # ------------------------------------------------------------------------
    # Mode 3: using header only
    # ------------------------------------------------------------------------
    # else we are using the header only
    elif infile is None:
        # get filetype from header (dprtype)
        filetype = header[params['KW_DPRTYPE'][0]]
        # get wave file instance
        wavefile = core.get_file_definition(filetype, params['INSTRUMENT'],
                                            kind='red')
        # set wave file properties (using header)
        wavefile.recipe = recipe
        wavefile.header = header
        wavefile.filename = header[params['KW_WAVEFILE'][0]]
        wavefile.data = np.zeros((header['NAXIS2'], header['NAXIS1']))
        wavesource = 'header'
        # get wave map
        wavemap = None
    # ------------------------------------------------------------------------
    # Mode 4: using infile (DrsFitsFile)
    # ------------------------------------------------------------------------
    # else we are using the infile
    else:
        wavefile = infile
        wavesource = 'header'
        # get wave map
        wavemap = None
    # ------------------------------------------------------------------------
    # Now deal with using wavefile
    # -------------------------------------------------------------------------
    # extract keys from header
    nbo = wavefile.read_header_key('KW_WAVE_NBO', dtype=int)
    deg = wavefile.read_header_key('KW_WAVE_DEG', dtype=int)
    # get the wfp keys
    wfp_drift = wavefile.read_header_key('KW_WFP_DRIFT', dtype=float,
                                         required=False)
    wfp_fwhm = wavefile.read_header_key('KW_WFP_FWHM', dtype=float,
                                        required=False)
    wfp_contrast = wavefile.read_header_key('KW_WFP_CONTRAST', dtype=float,
                                            required=False)
    wfp_maxcpp = wavefile.read_header_key('KW_WFP_MAXCPP', dtype=float,
                                          required=False)
    wfp_mask = wavefile.read_header_key('KW_WFP_MASK', dtype=float,
                                        required=False)
    wfp_lines = wavefile.read_header_key('KW_WFP_LINES', dtype=float,
                                         required=False)
    wfp_target_rv = wavefile.read_header_key('KW_TARG_RV', dtype=float,
                                             required=False)
    wfp_width = wavefile.read_header_key('KW_WFP_WIDTH', dtype=float,
                                         required=False)
    wfp_step = wavefile.read_header_key('KW_WFP_STEP', dtype=float,
                                        required=False)
    # extract cofficients from header
    wave_coeffs = wavefile.read_header_key_2d_list('KW_WAVECOEFFS',
                                                   dim1=nbo, dim2=deg + 1)
    # -------------------------------------------------------------------------
    # if wavemap is unset create it from wave coefficients
    if wavemap is None:
        # get image dimensions
        nby, nbx = infile.data.shape
        # set up storage
        wavemap = np.zeros((nbo, nbx))
        xpixels = np.arange(nbx)
        # loop aroun each order
        for order_num in range(nbo):
            # get this order coefficients
            ocoeffs = wave_coeffs[order_num][::-1]
            # calculate polynomial values and push into wavemap
            wavemap[order_num] = np.polyval(ocoeffs, xpixels)
    # -------------------------------------------------------------------------
    # store wave properties in parameter dictionary
    wprops = ParamDict()
    wprops['WAVEFILE'] = wavefile.filename
    wprops['WAVESOURCE'] = wavesource
    wprops['NBO'] = nbo
    wprops['DEG'] = deg
    wprops['COEFFS'] = wave_coeffs
    wprops['WAVEMAP'] = wavemap
    # add the wfp keys
    wprops['WFP_DRIFT'] = wfp_drift
    wprops['WFP_FWHM'] = wfp_fwhm
    wprops['WFP_CONTRAST'] = wfp_contrast
    wprops['WFP_MAXCPP'] = wfp_maxcpp
    wprops['WFP_MASK'] = wfp_mask
    wprops['WFP_LINES'] = wfp_lines
    wprops['WFP_TARG_RV'] = wfp_target_rv
    wprops['WFP_WIDTH'] = wfp_width
    wprops['WFP_STEP'] = wfp_step
    # set the source
    keys = ['WAVEMAP', 'WAVEFILE', 'WAVESOURCE', 'NBO', 'DEG', 'COEFFS',
            'WFP_DRIFT', 'WFP_FWHM', 'WFP_CONTRAST', 'WFP_MAXCPP', 'WFP_MASK',
            'WFP_LINES', 'WFP_TARG_RV', 'WFP_WIDTH', 'WFP_STEP']
    wprops.set_sources(keys, func_name)

    # -------------------------------------------------------------------------
    # return the map and properties
    return wprops


def add_wave_keys(infile, props):
    # add wave parameters
    infile.add_hkey('KW_WAVEFILE', value=props['WAVEFILE'])
    infile.add_hkey('KW_WAVESOURCE', value=props['WAVESOURCE'])
    infile.add_hkey('KW_WAVE_NBO', value=props['NBO'])
    infile.add_hkey('KW_WAVE_DEG', value=props['DEG'])
    infile.add_hkeys_2d('KW_WAVECOEFFS', values=props['COEFFS'],
                        dim1name='order', dim2name='coeffs')
    # add wave fp parameters
    infile.add_hkey('KW_WFP_FILE', value=props['WAVEFILE'])
    infile.add_hkey('KW_WFP_DRIFT', value=props['WFP_DRIFT'])
    infile.add_hkey('KW_WFP_FWHM', value=props['WFP_FWHM'])
    infile.add_hkey('KW_WFP_CONTRAST', value=props['WFP_CONTRAST'])
    infile.add_hkey('KW_WFP_MAXCPP', value=props['WFP_MAXCPP'])
    infile.add_hkey('KW_WFP_MASK', value=props['WFP_MASK'])
    infile.add_hkey('KW_WFP_LINES', value=props['WFP_LINES'])
    infile.add_hkey('KW_WFP_TARG_RV', value=props['WFP_TARG_RV'])
    infile.add_hkey('KW_WFP_WIDTH', value=props['WFP_WIDTH'])
    infile.add_hkey('KW_WFP_STEP', value=props['WFP_STEP'])
    # return infile
    return infile


def check_wave_consistency(params, props, **kwargs):
    func_name = __NAME__ + '.check_wave_consistency()'
    # get constants from params/kwargs
    required_deg = pcheck(params, 'WAVE_FIT_DEGREE', 'num_coeffs', kwargs,
                          func_name)
    # get dimension from data
    nbo, ncoeffs = props['COEFFS'].shape
    # get the fit degree from dimensions
    deg = ncoeffs - 1
    # check dimensions
    if required_deg == deg:
        # log that fit degrees match
        WLOG(params, '', TextEntry('40-017-00002', args=[deg]))
    # if not correct remap coefficients
    else:
        # log that fit degrees don't match
        wargs = [deg, required_deg]
        WLOG(params, 'warning', TextEntry('10-017-00003', args=wargs))
        # setup output storage
        output_coeffs = np.zeros_like(props['COEFFS'])
        output_map = np.zeros_like(props['WAVEMAP'])
        # define pixel array
        xfit = np.arange(output_map.shape[1])
        # loop around each order
        for order_num in range(nbo):
            # get the wave map for this order
            yfit = np.polyval(props['COEFFS'][order_num][::-1], xfit)
            # get the new coefficients based on a fit to this wavemap
            coeffs = math.nanpolyfit(xfit, yfit, required_deg)[::-1]
            # push into storage
            output_coeffs[order_num] = coeffs
            output_map[order_num] = yfit
        # update props
        props['WAVEMAP'] = output_map
        props['COEFFS'] = output_map
        props['DEG'] = required_deg
        props.set_sources(['WAVEMAP', 'COEFFS', 'DEG'], func_name)
    # return props
    return props


# =============================================================================
# Define wave solution functions
# =============================================================================
def hc_wavesol(params, recipe, iprops, e2dsfile, fiber, **kwargs):
    func_name = __NAME__ + '.hc_wavesol()'
    # get parameters from params / kwargs
    wave_mode_hc = pcheck(params, 'WAVE_MODE_HC', 'wave_mode_hc', kwargs,
                          func_name)

    # log the mode which is being used
    WLOG(params, 'info', TextEntry('40-017-00014', args=[wave_mode_hc]))

    # ----------------------------------------------------------------------
    # Read UNe solution
    # ----------------------------------------------------------------------
    wavell, ampll = drs_data.load_linelist(params, **kwargs)
    # ----------------------------------------------------------------------
    # Generate wave map from wave solution
    #     (with possible intercept/slope shift)
    # ----------------------------------------------------------------------
    iprops = generate_shifted_wave_map(params, iprops, **kwargs)
    # ----------------------------------------------------------------------
    # Create new wavelength solution (method 0, old cal_HC_E2DS_EA)
    # ----------------------------------------------------------------------
    if wave_mode_hc == 0:
        llprops =  hc_wavesol_ea(params, recipe, iprops, e2dsfile, fiber,
                                 wavell, ampll)
    else:
        # log that mode is not currently supported
        WLOG(params, 'error', TextEntry('09-017-00001', args=[wave_mode_hc]))
        llprops = None
    # ----------------------------------------------------------------------
    # add mode to llprops
    llprops['WAVE_MODE_HC'] = wave_mode_hc
    llprops.set_source('WAVE_MODE_HC', func_name)
    # ------------------------------------------------------------------
    # LITTROW SECTION - common to all methods
    # ------------------------------------------------------------------
    # set up hc specific terms
    start = pcheck(params, 'WAVE_LITTROW_ORDER_INIT_1')
    end = pcheck(params, 'WAVE_LITTROW_ORDER_FINAL_1')
    wavell = llprops['LL_OUT_1'][start:end, :]
    # run littrow test
    llprops = littrow(params, llprops, start, end, wavell, e2dsfile,
                      iteration=1)
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    wavefile = recipe.outputs['WAVE_HCMAP'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    wavefile.construct_filename(params, infile=e2dsfile)
    # ----------------------------------------------------------------------
    # set wprops values (expected for output)
    wprops = ParamDict()
    wprops['WAVEFILE'] = wavefile.filename
    wprops['WAVESOURCE'] = recipe.name
    wprops['COEFFS'] = llprops['POLY_WAVE_SOL']
    wprops['WAVEMAP'] = llprops['WAVE_MAP2']
    wprops['NBO'] = llprops['NBO']
    wprops['DEG'] = llprops['WAVE_FIT_DEGREE']
    wprops['NBPIX'] = llprops['NBPIX']
    # FP values (set to None for HC)
    wprops['WFP_DRIFT'] = None
    wprops['WFP_FWHM'] = None
    wprops['WFP_CONTRAST'] = None
    wprops['WFP_MAXCPP'] = None
    wprops['WFP_MASK'] = None
    wprops['WFP_LINES'] = None
    wprops['WFP_TARG_RV'] = None
    wprops['WFP_WIDTH'] = None
    wprops['WFP_STEP'] = None
    # set the source
    keys = ['WAVEMAP', 'WAVEFILE', 'WAVESOURCE', 'NBO', 'DEG', 'NBPIX',
            'COEFFS',
            'WFP_DRIFT', 'WFP_FWHM', 'WFP_CONTRAST', 'WFP_MAXCPP', 'WFP_MASK',
            'WFP_LINES', 'WFP_TARG_RV', 'WFP_WIDTH', 'WFP_STEP']
    wprops.set_sources(keys, func_name)

    # ------------------------------------------------------------------
    # return llprops
    # ------------------------------------------------------------------
    return llprops, wprops


def hc_wavesol_ea(params, recipe, iprops, e2dsfile, fiber, wavell, ampll):
    # ------------------------------------------------------------------
    # Find Gaussian Peaks in HC spectrum
    # ------------------------------------------------------------------
    llprops = find_hc_gauss_peaks(params, recipe, e2dsfile, fiber)

    # ------------------------------------------------------------------
    # Start plotting session
    # ------------------------------------------------------------------
    # TODO: Add plotting
    if params['DRS_PLOT'] > 0:
        # # start interactive plot
        # sPlt.start_interactive_session(p)
        pass
    # ------------------------------------------------------------------
    # Fit Gaussian peaks (in triplets) to
    # ------------------------------------------------------------------
    llprops = fit_gaussian_triplets(params, llprops, iprops, wavell, ampll)
    # ------------------------------------------------------------------
    # Generate Resolution map and line profiles
    # ------------------------------------------------------------------
    llprops = generate_resolution_map(params, llprops, e2dsfile)
    # ------------------------------------------------------------------
    # End plotting session
    # ------------------------------------------------------------------
    # TODO: Add plotting
    # end interactive session
    if params['DRS_PLOT'] > 0:
        # sPlt.end_interactive_session(p)
        pass
    # ------------------------------------------------------------------
    # Set up all_lines storage
    # ------------------------------------------------------------------
    llprops = all_line_storage(params, llprops)
    # ------------------------------------------------------------------
    # return llprops
    # ------------------------------------------------------------------
    return llprops


def fp_wavesol(params, e2dsfile, **kwargs):
    func_name = __NAME__ + '.fp_wavesol()'
    # get parameters from params / kwargs
    wave_mode_fp = pcheck(params, 'WAVE_MODE_FP', 'wave_mode_fp', kwargs,
                          func_name)

    # ------------------------------------------------------------------
    # Incorporate FP into solution
    # ------------------------------------------------------------------
    if wave_mode_fp == 0:
        # ------------------------------------------------------------------
        # Using the Bauer15 (WAVE_E2DS_EA) method:
        # ------------------------------------------------------------------
        llprops = fp_wavesol_bauer()
    elif wave_mode_fp == 1:
        # ------------------------------------------------------------------
        # Using the C Lovis (WAVE_NEW_2) method:
        # ------------------------------------------------------------------
        llprops = fp_wavesol_lovis()
    else:
        # log that mode is not currently supported
        WLOG(params, 'error', TextEntry('09-017-00003', args=[wave_mode_fp]))
        llprops = None

    # ----------------------------------------------------------------------
    # LITTROW SECTION - common to all methods
    # ----------------------------------------------------------------------
    # set up hc specific terms
    start = pcheck(params, 'WAVE_LITTROW_ORDER_INIT_2')
    end = pcheck(params, 'WAVE_LITTROW_ORDER_FINAL_2')
    wavell = llprops['LL_OUT_1']
    # run littrow test
    llprops = littrow(params, llprops, start, end, wavell, e2dsfile,
                      iteration=2)

    # ------------------------------------------------------------------
    # Join 0-47 and 47-49 solutions
    # ------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # FP CCF COMPUTATION - common to all methods
    # ----------------------------------------------------------------------

    # ------------------------------------------------------------------
    # return llprops
    # ------------------------------------------------------------------
    return llprops


def fp_wavesol_bauer():
    return 0


def fp_wavesol_lovis():
    return 0


# =============================================================================
# Define hc aux functions
# =============================================================================
def hc_quality_control(params, hcprops, e2dsfile):
    # set passed variable and fail message list
    fail_msg = []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # --------------------------------------------------------------
    # quality control on sigma clip (sig1 > qc_hc_wave_sigma_max
    hc_wave_sigma = params['WAVE_HC_QC_SIGMA_MAX']
    # find if sigma is greater than limit
    if hcprops['SIG1'] > hc_wave_sigma:
        fargs = [hcprops['SIG1'], hc_wave_sigma]
        fail_msg.append(textdict['40-017-00015'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(hcprops['SIG1'])
    qc_names.append('SIG1 HC')
    qc_logic.append('SIG1 > {0:.2f}'.format(hc_wave_sigma))
    # --------------------------------------------------------------
    # check the difference between consecutive orders is always
    #     positive
    # get the differences
    wave_diff = hcprops['WAVE_MAP2'][1:] - hcprops['WAVE_MAP2'][:-1]
    if np.min(wave_diff) < 0:
        fail_msg.append(textdict['40-017-00016'])
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(np.min(wave_diff))
    qc_names.append('MIN WAVE DIFF HC')
    qc_logic.append('MIN WAVE DIFF < 0')
    # --------------------------------------------------------------
    # check the difference between consecutive pixels along an
    #     order is always positive
    # loop through the orders
    ord_check = np.zeros(e2dsfile.data.shape[0], dtype=bool)
    for order in range(e2dsfile.data.shape[0]):
        wave0 = hcprops['WAVE_MAP2'][order, :-1]
        wave1 = hcprops['WAVE_MAP2'][order, 1:]
        ord_check[order] = np.all(wave1 > wave0)
    if np.all(ord_check):
        qc_pass.append(1)
        qc_values.append('None')
    else:
        fail_msg.append(textdict['40-017-00017'])
        qc_pass.append(0)
        badvalues = list(np.where(~ord_check)[0])
        qc_values.append(','.join(list(badvalues)))
    # add to qc header lists
    qc_names.append('WAVE DIFF ALONG ORDER HC')
    qc_logic.append('WAVE DIFF ALONG ORDER < 0')
    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #     quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
        params['QC'] = 1
        params.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
        params['QC'] = 0
        params.set_source('QC', __NAME__ + '/main()')
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params


def hc_log_global_stats(params, hcprops, e2dsfile, fiber):
    # calculate catalog-fit residuals in km/s
    res_hc = []
    sumres_hc = 0.0
    sumres2_hc = 0.0
    # loop around orders
    for order in range(e2dsfile.data.shape[0]):
        # get HC line wavelengths for the order
        order_mask = hcprops['ORD_T'] == order
        hc_x_ord = hcprops['XGAU_T'][order_mask]
        hc_ll_ord = np.polyval(hcprops['POLY_WAVE_SOL'][order][::-1], hc_x_ord)
        hc_ll_cat = hcprops['WAVE_CATALOG'][order_mask]
        hc_ll_diff = hc_ll_ord - hc_ll_cat
        res_hc.append(hc_ll_diff*speed_of_light/hc_ll_cat)
        sumres_hc += np.nansum(res_hc[order])
        sumres2_hc += np.nansum(res_hc[order] ** 2)
    # get the total number of lines
    total_lines_hc = len(np.concatenate(res_hc))
    # get the final mean and varianace
    final_mean_hc = sumres_hc/total_lines_hc
    final_var_hc = (sumres2_hc/total_lines_hc) - (final_mean_hc ** 2)
    # log global hc stats
    wargs = [fiber, final_mean_hc * 1000.0, np.sqrt(final_var_hc) * 1000.0,
              total_lines_hc, 1000.0 * np.sqrt(final_var_hc / total_lines_hc)]
    WLOG(params, 'info', TextEntry('40-017-00018', args=wargs))


def hc_write_wavesolution(params, recipe, llprops, infile, fiber, combine,
                          rawhcfiles, qc_params, iwprops):

    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    wavefile = recipe.outputs['WAVE_HCMAP'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    wavefile.construct_filename(params, infile=infile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    wavefile.copy_original_keys(infile)
    # add version
    wavefile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add output tag
    wavefile.add_hkey('KW_OUTPUT', value=wavefile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawhcfiles
    else:
        hfiles = [infile.basename]
    wavefile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add initial wavelength solution used
    wavefile.add_hkey('KW_INIT_WAVE', value=iwprops['WAVEFILE'])
    # ------------------------------------------------------------------
    # add the order num, fit degree and fit coefficients
    wavefile.add_hkey('KW_WAVE_NBO', value=iwprops['NBO'])
    wavefile.add_hkey('KW_WAVE_DEG', value=iwprops['DEG'])
    wavefile.add_hkeys_2d('KW_WAVECOEFFS', values=llprops['POLY_WAVE_SOL'],
                          dim1name='order', dim2name='coeffs')
    # ------------------------------------------------------------------
    # add constants used (for reproduction)
    wavefile.add_hkey('KW_WAVE_FITDEG', value=llprops['WAVE_FIT_DEGREE'])
    wavefile.add_hkey('KW_WAVE_MODE_HC', value=llprops['WAVE_MODE_HC'])
    wavefile.add_hkey('KW_WAVE_MODE_FP', value='None')
    # - from find_hc_gauss_peaks
    wavefile.add_hkey('KW_WAVE_HCG_WSIZE', value=llprops['HCG_WSIZE'])
    wavefile.add_hkey('KW_WAVE_HCG_SIGPEAK', value=llprops['HCG_SIGPEAK'])
    wavefile.add_hkey('KW_WAVE_HCG_GFITMODE', value=llprops['HCG_GFITMODE'])
    wavefile.add_hkey('KW_WAVE_HCG_FB_RMSMIN',
                      value=llprops['HCG_FITBOX_RMSMIN'])
    wavefile.add_hkey('KW_WAVE_HCG_FB_RMSMAX',
                      value=llprops['HCG_FITBOX_RMSMAX'])
    wavefile.add_hkey('KW_WAVE_HCG_EWMIN', value=llprops['HCG_EWMIN'])
    wavefile.add_hkey('KW_WAVE_HCG_EWMAX', value=llprops['HCG_EWMAX'])
    # - from load_hc_init_linelist
    wavefile.add_hkey('KW_WAVE_HCLL_FILE', value=llprops['HCLLBASENAME'])
    # - from fit_gaussian_triplets
    wavefile.add_hkey('KW_WAVE_TRP_NBRIGHT', value=llprops['NMAX_BRIGHT'])
    wavefile.add_hkey('KW_WAVE_TRP_NITER', value=llprops['N_ITER'])
    wavefile.add_hkey('KW_WAVE_TRP_CATGDIST', value=llprops['CAT_GUESS_DIST'])
    wavefile.add_hkey('KW_WAVE_TRP_FITDEG', value=llprops['TRIPLET_DEG'])
    wavefile.add_hkey('KW_WAVE_TRP_MIN_NLINES', value=llprops['MIN_NUM_LINES'])
    wavefile.add_hkey('KW_WAVE_TRP_TOT_NLINES', value=llprops['MIN_TOT_LINES'])
    wavefile.add_hkey_1d('KW_WAVE_TRP_ORDER_FITCONT',
                       values=llprops['ORDER_FIT_CONT'], dim1name='fit')
    wavefile.add_hkey('KW_WAVE_TRP_SCLIPNUM', value=llprops['SIGMA_CLIP_NUM'])
    wavefile.add_hkey('KW_WAVE_TRP_SCLIPTHRES',
                      value=llprops['SIGMA_CLIP_THRES'])
    wavefile.add_hkey('KW_WAVE_TRP_DVCUTORD', value=llprops['DVCUT_ORDER'])
    wavefile.add_hkey('KW_WAVE_TRP_DVCUTALL', value=llprops['DVCUT_ALL'])
    # - from generate res map
    wavefile.add_hkey_1d('KW_WAVE_RES_MAPSIZE', dim1name='dim',
                         values=llprops['RES_MAP_SIZE'])
    wavefile.add_hkey('KW_WAVE_RES_WSIZE', value=llprops['RES_WSIZE'])
    wavefile.add_hkey('KW_WAVE_RES_MAXDEVTHRES', value=llprops['MAX_DEV_THRES'])
    # - from littrow
    wavefile.add_hkey('KW_WAVE_LIT_START_1', value=llprops['LITTROW_START_1'])
    wavefile.add_hkey('KW_WAVE_LIT_END_1', value=llprops['LITTROW_END_1'])
    wavefile.add_hkey('KW_WAVE_ECHELLE_START', value=llprops['T_ORDER_START'])
    # - from calculate littrow solution
    wavefile.add_hkey_1d('KW_WAVE_LIT_RORDERS', dim1name='rorder',
                         values=llprops['LITTROW_REMOVE_ORDERS'])
    wavefile.add_hkey('KW_WAVE_LIT_ORDER_INIT_1',
                      value=llprops['LITTROW_ORDER_INIT_1'])
    wavefile.add_hkey('KW_WAVE_LIT_ORDER_START_1',
                      value=llprops['LITTROW_ORDER_START_1'])
    wavefile.add_hkey('KW_WAVE_LIT_ORDER_END_1',
                      value=llprops['LITTROW_ORDER_END_1'])
    wavefile.add_hkey('KW_WAVE_LITT_XCUTSTEP_1',
                      value=llprops['LITTROW_X_CUT_STEP_1'])
    wavefile.add_hkey('KW_WAVE_LITT_FITDEG_1',
                      value=llprops['LITTROW_FIT_DEG_1'])
    # - from extrapolate littrow solution
    wavefile.add_hkey('KW_WAVE_LITT_EXT_FITDEG_1',
                      value=llprops['LITTROW_EXT_FITDEG_1'])
    wavefile.add_hkey('KW_WAVE_LITT_EXT_ORD_START_1',
                      value=llprops['LITTROW_EXT_ORD_START_1'])
    # add qc parameters
    wavefile.add_qckeys(qc_params)
    # copy data
    wavefile.data = llprops['WAVE_MAP2']
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [fiber, wavefile.filename]
    WLOG(params, '', TextEntry('40-017-00019', args=wargs))
    # write image to file
    wavefile.write()
    # ------------------------------------------------------------------
    # return hc wavefile
    return wavefile


def hc_write_resmap(params, recipe, llprops, infile, wavefile, fiber):
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    resfile = recipe.outputs['WAVE_HCRES'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    resfile.construct_filename(params, infile=infile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from wavefile
    resfile.copy_hdict(wavefile)
    # ------------------------------------------------------------------
    datalist, headerlist = generate_res_files(params, llprops, resfile)
    # ------------------------------------------------------------------
    # set data to an empty list
    resfile.data = []
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [fiber, resfile.filename]
    WLOG(params, '', TextEntry('40-017-00020', args=wargs))
    # write image to file
    resfile.write_multi(data_list=datalist, header_list=headerlist)


# =============================================================================
# Define hc worker functions
# =============================================================================
def generate_shifted_wave_map(params, props, **kwargs):
    func_name = __NAME__ + '.generate_wave_map()'
    # get constants from p
    pixel_shift_inter = pcheck(params, 'WAVE_PIXEL_SHIFT_INTER', 'pixelshifti',
                               kwargs, func_name)
    pixel_shift_slope = pcheck(params, 'WAVE_PIXEL_SHIFT_SLOPE', 'pixelshifts',
                               kwargs, func_name)
    # get data from loc
    poly_wave_sol = props['COEFFS']
    nbo, nbpix = props['WAVEMAP'].shape
    # print a warning if pixel_shift is not 0
    if pixel_shift_slope != 0 or pixel_shift_inter != 0:
        wargs = [pixel_shift_slope, pixel_shift_inter]
        WLOG(params, 'warning', TextEntry('10-017-00004', args=wargs))
    else:
        return props
    # generate wave map with shift
    wave_map = np.zeros([nbo, nbpix])
    shift = pixel_shift_inter + pixel_shift_slope
    xpix = np.arange(nbpix) + shift * np.arange(nbpix)
    for iord in range(nbo):
        wave_map[iord, :] = np.polyval((poly_wave_sol[iord, :])[::-1], xpix)
    # save wave map to loc
    props['WAVEMAP'] = wave_map
    props.set_source('WAVEMAP', func_name)
    # return loc
    return props


def find_hc_gauss_peaks(params, recipe, e2dsfile, fiber, **kwargs):
    """
    Find the first guess at the guass peaks in the HC image

    :param params:
    :param recipe:
    :param e2dsfile:
    :param fiber:
    :param kwargs:
    :return:
    """
    func_name = __NAME__ + '.find_hc_gauss_peaks()'
    # get constants from params/kwargs
    wsize = pcheck(params, 'WAVE_HC_FITBOX_SIZE', 'wsize', kwargs,
                   func_name)
    sigma_peak = pcheck(params, 'WAVE_HC_FITBOX_SIGMA', 'sigma_peak', kwargs,
                        func_name)
    gfitmode = pcheck(params, 'WAVE_HC_FITBOX_GFIT_DEG', 'gfitmode', kwargs,
                      func_name)
    gauss_rms_dev_min = pcheck(params, 'WAVE_HC_FITBOX_RMS_DEVMIN',
                               'grms_devmin', kwargs, func_name)
    gauss_rms_dev_max = pcheck(params, 'wAVE_HC_FITBOX_RMS_DEVMAX',
                               'grms_devmax', kwargs, func_name)
    ew_min = pcheck(params, 'WAVE_HC_FITBOX_EWMIN', 'ew_min', kwargs,
                    func_name)
    ew_max = pcheck(params, 'WAVE_HC_FITBOX_EWMAX', 'ew_max', kwargs,
                    func_name)
    filefmt = pcheck(params, 'WAVE_HCLL_FILE_FMT', 'filefmt', kwargs, func_name)
    # get image
    hc_sp = e2dsfile.data
    # get dimensions from image
    nbo, nbpix = e2dsfile.data.shape
    # print process
    WLOG(params, '', TextEntry('40-017-00003'))
    # get initial line list
    llprops, exists = load_hc_init_linelist(params, recipe, e2dsfile, fiber)
    # if we dont have line list need to generate it
    if not exists:
        # ------------------------------------------------------------------
        # else we need to populate llprops
        # ------------------------------------------------------------------
        # set the first "previous peak" to -1
        xprev = -1
        # loop around orders
        for order_num in range(nbo):
            # print progress for user: processing order N of M
            wargs = [order_num, nbo - 1]
            WLOG(params, '', TextEntry('40-017-00004', args=wargs))
            # set number of peaks found
            npeaks = 0
            # extract this orders spectrum
            hc_sp_order = np.array(hc_sp[order_num, :])
            # loop around boxes in each order 1/3rd of wsize at a time
            bstart, bend = wsize * 2, hc_sp.shape[1] - wsize * 2 - 1
            bstep = wsize // 3
            for indmax in range(bstart, bend, bstep):
                # get this iterations start and end
                istart, iend = indmax - wsize, indmax + wsize
                # get the pixels for this iteration
                xpix = np.arange(istart, iend, 1)
                # get the spectrum at these points
                segment = np.array(hc_sp_order[istart:iend])
                # check there are not too many nans in segment:
                # if total not-nans is smaller than gaussian params +1
                if np.sum(~np.isnan(segment)) < gfitmode + 1:
                    # continue to next segment
                    continue
                # calculate the RMS
                rms = np.nanmedian(np.abs(segment[1:] - segment[:-1]))
                # find the peak pixel value
                peak = np.nanmax(segment) - np.nanmedian(segment)
                # ----------------------------------------------------------
                # keep only peaks that are well behaved:
                # RMS not zero
                keep = rms != 0
                # peak not zero
                keep &= peak != 0
                # peak at least a few sigma from RMS
                with warnings.catch_warnings(record=True) as _:
                    keep &= (peak / rms > sigma_peak)
                # ----------------------------------------------------------
                # position of peak within segement - it needs to be close
                #   enough to the center of the segment if it is at the edge
                #   we'll catch it in the following iteration
                imax = np.argmax(segment) - wsize
                # keep only if close enough to the center
                keep &= np.abs(imax) < wsize // 3
                # ----------------------------------------------------------
                # if keep is still True we have a good peak worth fitting
                #    a Gaussian
                if keep:
                    # fit a gaussian with a slope
                    gargs = [xpix, segment, gfitmode]
                    popt_left, g2 = math.gauss_fit_nn(*gargs)
                    # residual of the fit normalized by peak value similar to
                    #    an 1/SNR value
                    gauss_rms_dev0 = np.std(segment - g2) / popt_left[0]
                    # all values that will be added (if keep_peak=True) to the
                    #    vector of all line parameters
                    zp0 = popt_left[3]
                    slope0 = popt_left[4]
                    ew0 = popt_left[2]
                    xgau0 = popt_left[1]
                    peak0 = popt_left[0]
                    # test whether we will add peak to our master list of peak
                    keep_peak = gauss_rms_dev0 > gauss_rms_dev_min
                    keep_peak &= gauss_rms_dev0 < gauss_rms_dev_max
                    keep_peak &= ew0 > ew_min
                    keep_peak &= ew0 < ew_max
                    # must be > 1 pix from previous peak
                    keep_peak &= np.abs(xgau0 - xprev) > 1
                    # if all if fine, we keep the value of the fit
                    if keep_peak:
                        # update number of peaks
                        npeaks += 1
                        # update the value of previous peak
                        xprev = xgau0
                        # append values
                        llprops['ZP_INI'].append(zp0)
                        llprops['SLOPE_INI'].append(slope0)
                        llprops['EW_INI'].append(ew0)
                        llprops['XGAU_INI'].append(xgau0)
                        llprops['PEAK_INI'].append(peak0)
                        llprops['ORD_INI'].append(order_num)
                        llprops['GAUSS_RMS_DEV_INI'].append(gauss_rms_dev0)
                        # add values for plotting
                        llprops['XPIX_INI'].append(xpix)
            # display the number of peaks found
            WLOG(params, '', TextEntry('40-017-00005', args=[npeaks]))

            # debug plot
            if params['DRS_PLOT'] and params['DRS_DEBUG'] == 2:
                # TODO: Add plot later
                # if p['HC_EA_PLOT_PER_ORDER']:
                #     sPlt.wave_ea_plot_per_order_hcguess(p, loc, order_num)
                pass
        # ------------------------------------------------------------------
        # construct column names/values
        columnnames, columnvalues = llprops['HCLLCOLUMNS'], []
        for colname in columnnames:
            columnvalues.append(llprops[colname])
        # construct table
        ini_table = drs_table.make_table(params, columnnames, columnvalues)
        # log that we are saving hc line-list to file
        wargs = [llprops['HCLLBASENAME']]
        WLOG(params, '', TextEntry('40-017-00006', args=wargs))
        # save the table to file
        drs_table.write_table(params, ini_table, llprops['HCLLFILENAME'],
                              fmt=filefmt)
        # plot all orders w/fitted gaussians
        if params['DRS_PLOT'] > 0:
            # TODO: Add plotting
            # sPlt.wave_ea_plot_allorder_hcguess(p, loc)
            pass
    # ----------------------------------------------------------------------
    # add constants to llprops
    llprops['NBO'] = nbo
    llprops['NBPIX'] = nbpix
    llprops['HCG_WSIZE'] = wsize
    llprops['HCG_SIGPEAK'] = sigma_peak
    llprops['HCG_GFITMODE'] = gfitmode
    llprops['HCG_FITBOX_RMSMIN'] = gauss_rms_dev_min
    llprops['HCG_FITBOX_RMSMAX'] = gauss_rms_dev_max
    llprops['HCG_EWMIN'] = ew_min
    llprops['HCG_EWMAX'] = ew_max
    # set sources
    keys = ['NBO', 'NBPIX', 'HCG_WSIZE', 'HCG_SIGPEAK', 'HCG_GFITMODE',
            'HCG_FITBOX_RMSMIN', 'HCG_FITBOX_RMSMAX', 'HCG_EWMIN', 'HCG_EWMAX']
    llprops.set_sources(keys, func_name)
    # ------------------------------------------------------------------
    # return lprops
    return llprops


def load_hc_init_linelist(params, recipe, e2dsfile, fiber, **kwargs):
    """
    Load the initial guess at the gaussian positions (if file already exists)
    else the llprops returned in an empty placeholder waiting to be filled

    :param params:
    :param recipe:
    :param e2dsfile:
    :param fiber:
    :param kwargs:
    :return:
    """
    func_name = __NAME__ + '.load_hc_init_linelist()'
    # get parameters from params/kwargs
    filefmt = pcheck(params, 'WAVE_HCLL_FILE_FMT', 'filefmt', kwargs, func_name)

    # construct hcll file
    hcllfile = recipe.outputs['WAVE_HCLL'].newcopy(recipe=recipe)
    hcllfile.construct_filename(params, infile=e2dsfile, fiber=fiber)
    # get filename
    hcllfilename = hcllfile.filename
    # define columns for hc line list
    columns = ['ZP_INI', 'SLOPE_INI', 'EW_INI', 'XGAU_INI', 'PEAK_INI',
               'ORD_INI', 'GAUSS_RMS_DEV_INI']
    # set up storage of properties
    llprops = ParamDict()
    # find if file exists
    if os.path.exists(hcllfile.filename):
        # read table
        initable = drs_table.read_table(params, hcllfilename, fmt=filefmt,
                                        colnames=columns)
        # push values into llprops
        for col in columns:
            llprops[col] = np.array(initable[col])
        # set source
        tsource = '{0} [{1}]'.format(func_name, hcllfile.basename)
        llprops.set_sources(columns, tsource)
        # set exists
        exists = True
    # if we have no initial values just set them empty
    else:
        # loop around columns
        for col in columns:
            llprops[col] = []
        # set the source
        tsource = '{0} [{1}]'.format(func_name, 'Empty')
        llprops.set_sources(columns, tsource)
        # set exists
        exists = False
    # add filename to llprops
    llprops['HCLLFILENAME'] = hcllfile.filename
    llprops['HCLLBASENAME'] = hcllfile.basename
    llprops['HCLLCOLUMNS'] = columns
    # set source
    keys = ['HCLLFILENAME', 'HCLLBASENAME', 'HCLLCOLUMNS']
    llprops.set_sources(keys, func_name)
    # add additional properties (for plotting)
    llprops['XPIX_INI'] = []
    llprops['G2_INI'] = []
    llprops.set_sources(['XPIX_INI', 'G2_INI'], func_name)
    # return properties param dict
    return llprops, exists


def fit_gaussian_triplets(params, llprops, iprops, wavell, ampll, **kwargs):
    """
    Fits the Gaussian peaks with sigma clipping

    fits a second-order xpix vs wavelength polynomial and test it against
    all other fitted lines along the order we keep track of the best fit for
    the order, i.e., the fit that provides a solution with the largest number
    of lines within +-500 m/s

    We then assume that the fit is fine, we keep the lines that match the
    "best fit" and we move to the next order.

    Once we have "valid" lines for most/all orders, we attempt to fit a
    5th order polynomial of the xpix vs lambda for all orders.
    The coefficient of the fit must be continuous from one order to the next

    we perform the fit twice, once to get a coarse solution, once to refine
    as we will trim some variables, we define them on each loop
    not 100% elegant, but who cares, it takes 5µs ...

    :param params:
    :param llprops:
    :param iprops:
    :param wavell:
    :param ampll:
    :param kwargs:
    :return:
    """
    func_name = __NAME__ + '.fit_gaussian_triplets()'
    # get constants from params/kwargs
    nmax_bright = pcheck(params, 'WAVE_HC_NMAX_BRIGHT', 'nmax_bright', kwargs,
                         func_name)
    n_iterations = pcheck(params, 'WAVE_HC_NITER_FIT_TRIPLET', 'n_iterations',
                          kwargs, func_name)
    cat_guess_dist = pcheck(params, 'WAVE_HC_MAX_DV_CAT_GUESS',
                            'cat_guess_dist', kwargs, func_name)
    triplet_deg = pcheck(params, 'WAVE_HC_TFIT_DEG', 'triplet_deg', kwargs,
                         func_name)
    cut_fit_threshold = pcheck(params, 'WAVE_HC_TFIT_CUT_THRES',
                               'cut_fit_thres', kwargs, func_name)
    min_num_lines = pcheck(params, 'WAVE_HC_TFIT_MINNUM_LINES', 'min_num_lines',
                           kwargs, func_name)
    min_tot_num_lines = pcheck(params, 'WAVE_HC_TFIT_MINTOT_LINES',
                               'min_tot_lines', kwargs, func_name)
    order_fit_cont = pcheck(params, 'WAVE_HC_TFIT_ORDER_FIT_CONT',
                            'order_fit_cont', kwargs, func_name, mapf='list',
                            dtype=int)
    sigma_clip_num = pcheck(params, 'WAVE_HC_TFIT_SIGCLIP_NUM',
                            'sigma_clip_num', kwargs, func_name)
    sigma_clip_thres = pcheck(params, 'WAVE_HC_TFIT_SIGCLIP_THRES',
                              'sigma_clip_thres', kwargs, func_name)
    dvcut_order = pcheck(params, 'WAVE_HC_TFIT_DVCUT_ORDER', 'dvcut_order',
                         kwargs, func_name)
    dvcut_all = pcheck(params, 'WAVE_HC_TFIT_DVCUT_ALL', 'dvcut_all',
                       kwargs, func_name)
    # get poly_wave_sol from iprops
    poly_wave_sol = iprops['COEFFS']
    # get dimensions
    nbo, nbpix = llprops['NBO'], llprops['NBPIX']

    # set up storage
    wave_catalog = []
    amp_catalog = []
    wave_map2 = np.zeros((nbo, nbpix))
    sig = np.nan
    # get coefficients
    xgau = np.array(llprops['XGAU_INI'])
    orders = np.array(llprops['ORD_INI'])
    gauss_rms_dev = np.array(llprops['GAUSS_RMS_DEV_INI'])
    ew = np.array(llprops['EW_INI'])
    peak2 = np.array(llprops['PEAK_INI'])
    dv = np.array([])
    lin_mod_slice = []
    recon0 = []

    # ------------------------------------------------------------------
    # triplet loop
    # ------------------------------------------------------------------
    for sol_iteration in range(n_iterations):
        # log that we are fitting triplet N of M
        wargs = [sol_iteration + 1, n_iterations]
        WLOG(params, 'info', TextEntry('40-017-00007', args=wargs))
        # get coefficients
        xgau = np.array(llprops['XGAU_INI'])
        orders = np.array(llprops['ORD_INI'])
        gauss_rms_dev = np.array(llprops['GAUSS_RMS_DEV_INI'])
        ew = np.array(llprops['EW_INI'])
        peak = np.array(llprops['PEAK_INI'])
        # get peak again for saving (to make sure nothing goes wrong
        #     in selection)
        peak2 = np.array(llprops['PEAK_INI'])
        # --------------------------------------------------------------
        # find the brightest lines for each order, only those lines will
        #     be used to derive the first estimates of the per-order fit
        # ------------------------------------------------------------------
        brightest_lines = np.zeros(len(xgau), dtype=bool)
        # loop around order
        for order_num in set(orders):
            # find all order_nums that belong to this order
            good = orders == order_num
            # get the peaks for this order
            order_peaks = peak[good]
            # we may have fewer lines within the order than nmax_bright
            if np.nansum(good) <= nmax_bright:
                nmax = np.nansum(good) - 1
            else:
                nmax = nmax_bright
            # Find the "nmax" brightest peaks
            smallest_peak = np.sort(order_peaks)[::-1][nmax]
            good &= (peak > smallest_peak)
            # apply good mask to brightest_lines storage
            brightest_lines[good] = True
        # ------------------------------------------------------------------
        # Calculate wave solution at each x gaussian center
        # ------------------------------------------------------------------
        ini_wave_sol = np.zeros_like(xgau)
        # get wave solution for these xgau values
        for order_num in set(orders):
            # find all order_nums that belong to this order
            good = orders == order_num
            # get the xgau for this order
            xgau_order = xgau[good]
            # get wave solution for this order
            pargs = poly_wave_sol[order_num][::-1], xgau_order
            wave_sol_order = np.polyval(*pargs)
            # pipe wave solution for order into full wave_sol
            ini_wave_sol[good] = wave_sol_order
        # ------------------------------------------------------------------
        # match gaussian peaks
        # ------------------------------------------------------------------
        # keep track of the velocity offset between predicted and observed
        #    line centers
        dv = np.repeat(np.nan, len(ini_wave_sol))
        # wavelength given in the catalog for the matched line
        wave_catalog = np.repeat(np.nan, len(ini_wave_sol))
        # amplitude given in the catolog for the matched lines
        amp_catalog = np.zeros(len(ini_wave_sol))
        # loop around all lines in ini_wave_sol
        for w_it, wave0 in enumerate(ini_wave_sol):
            # find closest catalog line to the line considered
            id_match = np.argmin(np.abs(wavell - wave0))
            # find distance between catalog and ini solution  in m/s
            distv = ((wavell[id_match] / wave0) - 1) * speed_of_light_ms
            # check that distance is below threshold
            if np.abs(distv) < cat_guess_dist:
                wave_catalog[w_it] = wavell[id_match]
                amp_catalog[w_it] = ampll[id_match]
                dv[w_it] = distv
        # ------------------------------------------------------------------
        # loop through orders and reject bright lines not within
        #     +- HC_TFIT_DVCUT km/s histogram peak
        # ------------------------------------------------------------------
        # width in dv [km/s] - though used for number of bins?
        # TODO: Question: Why km/s --> number
        nbins = 2 * int(cat_guess_dist) // 1000
        # loop around all order
        for order_num in set(orders):
            # get the good pixels in this order
            good = (orders == order_num) & (np.isfinite(dv))
            # get histogram of points for this order
            histval, histcenters = np.histogram(dv[good], bins=nbins)
            # get the center of the distribution
            dv_cen = histcenters[np.argmax(histval)]
            # define a mask to remove points away from center of histogram
            with warnings.catch_warnings(record=True) as _:
                mask = (np.abs(dv - dv_cen) > dvcut_order) & good
            # apply mask to dv and to brightest lines
            dv[mask] = np.nan
            brightest_lines[mask] = False
        # re-get the histogram of points for whole image
        histval, histcenters = np.histogram(dv[np.isfinite(dv)], bins=nbins)
        # re-find the center of the distribution
        dv_cen = histcenters[np.argmax(histval)]
        # re-define the mask to remove poitns away from center of histogram
        with warnings.catch_warnings(record=True) as _:
            mask = (np.abs(dv - dv_cen) > dvcut_all)
        # re-apply mask to dv and to brightest lines
        dv[mask] = np.nan
        brightest_lines[mask] = False
        # ------------------------------------------------------------------
        # Find best trio of lines
        # ------------------------------------------------------------------
        for order_num in set(orders):
            # find this order's lines
            good = orders == order_num
            # find all usable lines in this order
            good_all = good & (np.isfinite(wave_catalog))
            # good_all = good & (np.isfinite(dv))
            # find all bright usable lines in this order
            good_bright = good_all & brightest_lines
            # get the positions of lines
            pos_bright = np.where(good_bright)[0]
            pos = np.where(good)[0]
            # get number of good_bright
            num_gb = int(np.nansum(good_bright))
            bestn = 0
            best_coeffs = np.zeros(triplet_deg + 1)
            # get the indices of the triplets of bright lines
            indices = itertools.combinations(range(num_gb), 3)
            # loop around triplets
            for index in indices:
                # get this iterations positions
                pos_it = pos_bright[np.array(index)]
                # get the x values for this iterations position
                xx = xgau[pos_it]
                # get the y values for this iterations position
                yy = wave_catalog[pos_it]
                # fit this position's lines and take it as the best-guess
                #    solution
                coeffs = math.nanpolyfit(xx, yy, triplet_deg)
                # extrapolate out over all lines
                fit_all = np.polyval(coeffs, xgau[good_all])
                # work out the error in velocity
                ev = ((wave_catalog[good_all] / fit_all) - 1) * speed_of_light
                # work out the number of lines to keep
                nkeep = np.nansum(np.abs(ev) < cut_fit_threshold)
                # if number of lines to keep largest seen --> store
                if nkeep > bestn:
                    bestn = nkeep
                    best_coeffs = np.array(coeffs)
            # Log the total number of valid lines found
            wargs = [order_num, bestn, np.nansum(good_all)]
            WLOG(params, '', TextEntry('40-017-00008', args=wargs))
            # if we have the minimum number of lines check that we satisfy
            #   the cut_fit_threshold for all good lines and reject outliers
            if bestn >= min_num_lines:
                # extrapolate out best fit coefficients over all lines in
                #    this order
                fit_best = np.polyval(best_coeffs, xgau[good])
                # work out the error in velocity
                ev = ((wave_catalog[good] / fit_best) - 1) * speed_of_light
                abs_ev = np.abs(ev)
                # if max error in velocity greater than threshold, remove
                #    those greater than cut_fit_threshold
                if np.nanmax(abs_ev) > cut_fit_threshold:
                    # get outliers
                    with warnings.catch_warnings(record=True) as _:
                        outliers = pos[abs_ev > cut_fit_threshold]
                    # set outliers to NaN in wave catalog
                    wave_catalog[outliers] = np.nan
                    # set dv of outliers to NaN
                    dv[outliers] = np.nan
            # else set everything to NaN
            else:
                wave_catalog[good] = np.nan
                dv[good] = np.nan
        # ------------------------------------------------------------------
        # Plot wave catalogue all lines and brightest lines
        # ------------------------------------------------------------------
        if params['DRS_PLOT'] > 0:
            # TODO: Add plots
            # pargs = [wave_catalog, dv, brightest_lines, sol_iteration]
            # sPlt.wave_ea_plot_wave_cat_all_and_brightest(p, *pargs)
            pass

        # ------------------------------------------------------------------
        # Keep only wave_catalog where values are finite
        # -----------------------------------------------------------------
        # create mask
        good = np.isfinite(wave_catalog)
        # apply mask
        wave_catalog = wave_catalog[good]
        amp_catalog = amp_catalog[good]
        xgau = xgau[good]
        orders = orders[good]
        dv = dv[good]
        ew = ew[good]
        gauss_rms_dev = gauss_rms_dev[good]
        peak2 = peak2[good]
        # ------------------------------------------------------------------
        # Quality check on the total number of lines found
        # ------------------------------------------------------------------
        if np.nansum(good) < min_tot_num_lines:
            # log error that we have insufficient lines found
            eargs = [np.nansum(good), min_tot_num_lines, func_name]
            WLOG(params, 'error', TextEntry('00-017-00003', args=eargs))

        # ------------------------------------------------------------------
        # Linear model slice generation
        # ------------------------------------------------------------------
        # storage for the linear model slice
        lin_mod_slice = np.zeros((len(xgau), np.nansum(order_fit_cont)))

        # construct the unit vectors for wavelength model
        # loop around order fit continuity values
        ii = 0
        for expo_xpix in range(len(order_fit_cont)):
            # loop around orders
            for expo_order in range(order_fit_cont[expo_xpix]):
                part1 = orders ** expo_order
                part2 = np.array(xgau) ** expo_xpix
                lin_mod_slice[:, ii] = part1 * part2
                # iterate
                ii += 1

        # ------------------------------------------------------------------
        # Sigma clipping
        # ------------------------------------------------------------------
        # storage for arrays
        recon0 = np.zeros_like(wave_catalog)
        amps0 = np.zeros(np.nansum(order_fit_cont))

        # Loop sigma_clip_num times for sigma clipping and numerical
        #    convergence. In most cases ~10 iterations would be fine but this
        #    is fast
        for sigma_it in range(sigma_clip_num):
            # calculate the linear minimization
            largs = [wave_catalog - recon0, lin_mod_slice]
            with warnings.catch_warnings(record=True) as _:
                amps, recon = math.linear_minimization(*largs)
            # add the amps and recon to new storage
            amps0 = amps0 + amps
            recon0 = recon0 + recon
            # loop around the amplitudes and normalise
            for a_it in range(len(amps0)):
                # work out the residuals
                res = (wave_catalog - recon0)
                # work out the sum of residuals
                sum_r = np.nansum(res * lin_mod_slice[:, a_it])
                sum_l2 = np.nansum(lin_mod_slice[:, a_it] ** 2)
                # normalise by sum squared
                ampsx = sum_r / sum_l2
                # add this contribution on
                amps0[a_it] += ampsx
                recon0 += (ampsx * lin_mod_slice[:, a_it])
            # recalculate dv [in km/s]
            dv = ((wave_catalog / recon0) - 1) * speed_of_light
            # calculate the standard deviation
            sig = np.std(dv)
            absdev = np.abs(dv / sig)

            # initialize lists for saving
            recon0_aux = []
            lin_mod_slice_aux = []
            wave_catalog_aux = []
            amp_catalog_aux = []
            xgau_aux = []
            orders_aux = []
            dv_aux = []
            ew_aux = []
            gauss_rms_dev_aux = []
            peak2_aux = []

            # Sigma clip worst line per order
            for order_num in set(orders):
                # mask for order
                omask = orders == order_num
                # get abs dev for order
                absdev_ord = absdev[omask]
                # check if above threshold
                if np.max(absdev_ord) > sigma_clip_thres:
                    # create mask for worst line
                    sig_mask = absdev_ord < np.max(absdev_ord)
                    # apply mask
                    recon0_aux.append(recon0[omask][sig_mask])
                    lin_mod_slice_aux.append(lin_mod_slice[omask][sig_mask])
                    wave_catalog_aux.append(wave_catalog[omask][sig_mask])
                    amp_catalog_aux.append(amp_catalog[omask][sig_mask])
                    xgau_aux.append(xgau[omask][sig_mask])
                    orders_aux.append(orders[omask][sig_mask])
                    dv_aux.append(dv[omask][sig_mask])
                    ew_aux.append(ew[omask][sig_mask])
                    gauss_rms_dev_aux.append(gauss_rms_dev[omask][sig_mask])
                    peak2_aux.append(peak2[omask][sig_mask])
                # if all below threshold keep all
                else:
                    recon0_aux.append(recon0[omask])
                    lin_mod_slice_aux.append(lin_mod_slice[omask])
                    wave_catalog_aux.append(wave_catalog[omask])
                    amp_catalog_aux.append(amp_catalog[omask])
                    xgau_aux.append(xgau[omask])
                    orders_aux.append(orders[omask])
                    dv_aux.append(dv[omask])
                    ew_aux.append(ew[omask])
                    gauss_rms_dev_aux.append(gauss_rms_dev[omask])
                    peak2_aux.append(peak2[omask])
            # save aux lists to initial arrays
            orders = np.concatenate(orders_aux)
            recon0 = np.concatenate(recon0_aux)
            lin_mod_slice = np.concatenate(lin_mod_slice_aux)
            wave_catalog = np.concatenate(wave_catalog_aux)
            amp_catalog = np.concatenate(amp_catalog_aux)
            xgau = np.concatenate(xgau_aux)
            dv = np.concatenate(dv_aux)
            ew = np.concatenate(ew_aux)
            gauss_rms_dev = np.concatenate(gauss_rms_dev_aux)
            peak2 = np.concatenate(peak2_aux)

            # Log stats RMS/SIG/N
            sig1 = sig * 1000 / np.sqrt(len(wave_catalog))
            wargs = [sigma_it, sig, sig1, len(wave_catalog)]
            WLOG(params, '', TextEntry('40-017-00009', args=wargs))
        # ------------------------------------------------------------------
        # Plot wave catalogue all lines and brightest lines
        # ------------------------------------------------------------------
        if params['DRS_PLOT'] > 0:
            # TODO: Add plots
            # pargs = [orders, wave_catalog, recon0, gauss_rms_dev, xgau, ew,
            #          sol_iteration]
            # sPlt.wave_ea_plot_tfit_grid(p, *pargs)
            pass

        # ------------------------------------------------------------------
        # Construct wave map
        # ------------------------------------------------------------------
        xpix = np.arange(nbpix)
        wave_map2 = np.zeros((nbo, nbpix))
        poly_wave_sol = np.zeros_like(iprops['COEFFS'])

        # loop around the orders
        for order_num in range(nbo):
            order_mask = orders == order_num
            if np.nansum(order_mask) == 0:
                # log that no values were found
                wargs = [order_num]
                WLOG(params, 'warning', TextEntry('10-017-00005', args=wargs))
            # loop around order fit continuum to propagate new coefficients
            ii = 0
            for expo_xpix in range(len(order_fit_cont)):
                for expo_order in range(order_fit_cont[expo_xpix]):
                    # calculate new coefficient
                    new_coeff = (order_num ** expo_order) * amps0[ii]
                    # add to poly wave solution
                    poly_wave_sol[order_num, expo_xpix] += new_coeff
                    # iterate
                    ii += 1
            # add to wave_map2
            wcoeffs = poly_wave_sol[order_num, :][::-1]
            wave_map2[order_num, :] = np.polyval(wcoeffs, xpix)
    # save parameters to llprops
    llprops['WAVE_CATALOG'] = wave_catalog
    llprops['AMP_CATALOG'] = amp_catalog
    llprops['SIG'] = sig
    llprops['SIG1'] = sig * 1000 / np.sqrt(len(wave_catalog))
    llprops['POLY_WAVE_SOL'] = poly_wave_sol
    llprops['WAVE_MAP2'] = wave_map2
    llprops['XGAU_T'] = xgau
    llprops['ORD_T'] = orders
    llprops['GAUSS_RMS_DEV_T'] = gauss_rms_dev
    llprops['DV_T'] = dv
    llprops['EW_T'] = ew
    llprops['PEAK_T'] = peak2
    llprops['LIN_MOD_SLICE'] = lin_mod_slice
    llprops['RECON0'] = recon0
    # set sources
    keys = ['WAVE_CATALOG', 'AMP_CATALOG', 'SIG', 'SIG1', 'POLY_WAVE_SOL',
            'WAVE_MAP2', 'XGAU_T', 'ORD_T', 'GAUSS_RMS_DEV_T', 'DV_T',
            'EW_T', 'PEAK_T', 'LIN_MOD_SLICE', 'RECON0']
    llprops.set_sources(keys, func_name)
    # save constants to llprops (required for reproduction)
    llprops['WAVE_FIT_DEGREE'] = iprops['DEG']
    llprops['NMAX_BRIGHT'] = nmax_bright
    llprops['N_ITER'] = n_iterations
    llprops['CAT_GUESS_DIST'] = cat_guess_dist
    llprops['TRIPLET_DEG'] = triplet_deg
    llprops['CUT_FIT_THRES'] = cut_fit_threshold
    llprops['MIN_NUM_LINES'] = min_num_lines
    llprops['MIN_TOT_LINES'] = min_tot_num_lines
    llprops['ORDER_FIT_CONT'] = order_fit_cont
    llprops['SIGMA_CLIP_NUM'] = sigma_clip_num
    llprops['SIGMA_CLIP_THRES'] = sigma_clip_thres
    llprops['DVCUT_ORDER'] = dvcut_order
    llprops['DVCUT_ALL'] = dvcut_all
    llprops['INIT_WAVEFILE'] = iprops['WAVEFILE']
    # set sources
    keys = ['WAVE_FIT_DEGREE', 'NMAX_BRIGHT', 'N_ITER', 'CAT_GUESS_DIST',
            'TRIPLET_DEG', 'CUT_FIT_THRES', 'MIN_NUM_LINES', 'MIN_TOT_LINES',
            'ORDER_FIT_CONT', 'SIGMA_CLIP_NUM', 'SIGMA_CLIP_THRES',
            'DVCUT_ORDER', 'DVCUT_ALL', 'INIT_WAVEFILE']
    llprops.set_sources(keys, func_name)
    # return llprops
    return llprops


def generate_resolution_map(params, llprops, e2dsfile, **kwargs):
    func_name = __NAME__ + '.generate_resolution_map()'

    # get constants from params / kwargs
    resmap_size = pcheck(params, 'WAVE_HC_RESMAP_SIZE', 'resmap_size',
                         kwargs, func_name, mapf='list', dtype=int)
    wsize = pcheck(params, 'WAVE_HC_FITBOX_SIZE', 'wsize', kwargs,
                   func_name)
    max_dev_thres = pcheck(params, 'WAVE_HC_RES_MAXDEV_THRES', 'max_dev_thres',
                           kwargs, func_name)
    # get image
    hc_sp = np.array(e2dsfile.data)
    xgau = np.array(llprops['XGAU_T'])
    orders = np.array(llprops['ORD_T'])
    gauss_rms_dev = np.array(llprops['GAUSS_RMS_DEV_T'])
    wave_catalog = np.array(llprops['WAVE_CATALOG'])
    wave_map2 = np.array(llprops['WAVE_MAP2'])
    # get dimensions from image
    nbo, nbpix = hc_sp.shape

    # log progress
    WLOG(params, '', TextEntry('40-017-00010'))

    # storage of resolution map
    resolution_map = np.zeros(resmap_size)
    map_dvs = []
    map_lines = []
    map_params = []

    # bin size in order direction
    bin_order = int(np.ceil(nbo / resmap_size[0]))
    bin_x = int(np.ceil(nbpix / resmap_size[1]))

    # determine the line spread function

    # loop around the order bins
    for order_num in range(0, nbo, bin_order):
        # storage of map parameters
        order_dvs = []
        order_lines = []
        order_params = []
        # loop around the x position
        for xpos in range(0, nbpix // bin_x):
            # we verify that the line is well modelled by a gaussian
            # fit. If the RMS to the fit is small enough, we include
            # the line in the profile measurement
            mask = gauss_rms_dev < 0.05
            # the line must fall in the right part of the array
            # in both X and cross-dispersed directions. The
            # resolution is expected to change slightly
            mask &= (orders // bin_order) == (order_num // bin_order)
            mask &= (xgau // bin_x) == xpos
            mask &= np.isfinite(wave_catalog)

            # get the x centers for this bin
            b_xgau = xgau[mask]
            b_orders = orders[mask]
            b_wave_catalog = wave_catalog[mask]

            # set up storage for lines and dvs
            all_lines = np.zeros((np.nansum(mask), 2 * wsize + 1))
            all_dvs = np.zeros((np.nansum(mask), 2 * wsize + 1))

            # set up base
            base = np.zeros(2 * wsize + 1, dtype=bool)
            base[0:3] = True
            base[2 * wsize - 2: 2 * wsize + 1] = True

            # loop around all good lines
            # we express everything in velocity space rather than
            # pixels. This allows us to merge all lines in a single
            # profile and removes differences in pixel sampling and
            # resolution.
            for it in range(int(np.nansum(mask))):
                # get limits
                border = int(b_orders[it])
                start = int(b_xgau[it] + 0.5) - wsize
                end = int(b_xgau[it] + 0.5) + wsize + 1
                # get line
                line = np.array(hc_sp)[border, start:end]
                # subtract median base and normalise line
                line -= np.nanmedian(line[base])
                line /= np.nansum(line)
                # calculate velocity... express things in velocity
                ratio = wave_map2[border, start:end] / b_wave_catalog[it]
                dv = -speed_of_light * (ratio - 1)
                # store line and dv
                all_lines[it, :] = line
                all_dvs[it, :] = dv

            # flatten all lines and dvs
            all_dvs = all_dvs.ravel()
            all_lines = all_lines.ravel()
            # define storage for keep mask
            # keep = np.ones(len(all_dvs), dtype=bool)
            # TODO New hack: Do not keep as hardcoded
            keep = np.abs(all_lines) < 5

            # set an initial maximum deviation
            maxdev = np.inf
            # set up the fix parameters and initial guess parameters
            popt = np.zeros(5)
            init_guess = [0.3, 0.0, 1.0, 0.0, 0.0]
            # loop around until criteria met
            n_it = 0

            # fit the merged line profile and do some sigma-clipping
            while maxdev > max_dev_thres:
                # fit with a guassian with a slope
                fargs = dict(x=all_dvs[keep], y=all_lines[keep],
                             guess=init_guess)
                # do curve fit on point
                try:
                    popt, pcov = math.fit_gauss_with_slope(**fargs)
                except Exception as e:
                    # log error: Resolution map curve_fit error
                    eargs = [type(e), e, func_name]
                    WLOG(params, 'error', TextEntry('09-017-00002', args=eargs))
                # calculate residuals for full line list
                res = all_lines - math.gauss_fit_s(all_dvs, *popt)
                # calculate RMS of residuals
                rms = res / np.nanmedian(np.abs(res))
                # calculate max deviation
                maxdev = np.nanmax(np.abs(rms[keep]))
                # re-calculate the keep mask
                keep[np.abs(rms) > max_dev_thres] = False
                # increase value of iterator
                n_it += 1
            # calculate resolution
            resolution = popt[2] * math.general.fwhm()
            # store order criteria
            order_dvs.append(all_dvs[keep])
            order_lines.append(all_lines[keep])
            order_params.append(popt)
            # push resolution into resolution map
            resolution1 = speed_of_light / resolution
            resolution_map[order_num // bin_order, xpos] = resolution1
            # log resolution output
            wargs = [order_num, order_num + bin_order, np.nansum(mask), xpos,
                     resolution,
                     resolution1]
            WLOG(params, '', TextEntry('40-017-00011', args=wargs))
        # store criteria. All lines are kept for reference
        map_dvs.append(order_dvs)
        map_lines.append(order_lines)
        map_params.append(order_params)

    # push to llprops
    llprops['RES_MAP_DVS'] = map_dvs
    llprops['RES_MAP_LINES'] = map_lines
    llprops['RES_MAP_PARAMS'] = map_params
    llprops['RES_MAP'] = resolution_map
    # set source
    keys = ['RES_MAP_DVS', 'RES_MAP_LINES', 'RES_MAP_PARAMS', 'RES_MAP']
    llprops.set_sources(keys, func_name)

    # add constants to llprops
    llprops['RES_MAP_SIZE'] = resmap_size
    llprops['RES_WSIZE'] = wsize
    llprops['MAX_DEV_THRES'] = max_dev_thres
    keys = ['RES_MAP_SIZE', 'RES_WSIZE', 'MAX_DEV_THRES']
    llprops.set_sources(keys, func_name)

    # print stats
    wargs = [np.nanmean(resolution_map), np.nanmedian(resolution_map),
             np.nanstd(resolution_map)]
    WLOG(params, '', TextEntry('40-017-00012', args=wargs))

    # map line profile map
    if params['DRS_PLOT'] > 0:
        # TODO: Add plotting
        # sPlt.wave_ea_plot_line_profiles(p, loc)
        pass

    # return loc
    return llprops


def all_line_storage(params, llprops, **kwargs):
    func_name = __NAME__ + '.all_line_storage()'
    # initialise up all_lines storage
    all_lines_1 = []
    # get parameters from p
    n_ord_start = pcheck(params, 'WAVE_N_ORD_START', 'n_ord_start', kwargs,
                         func_name)
    n_ord_final = pcheck(params, 'WAVE_N_ORD_FINAL', 'n_ord_final', kwargs,
                         func_name)

    # get values from loc:
    # line centers in pixels
    xgau = np.array(llprops['XGAU_T'])
    # distance from catalogue in km/s - used for sanity checks
    dv = np.array(llprops['DV_T'])
    # fitted polynomials per order
    fit_per_order = np.array(llprops['POLY_WAVE_SOL'])
    # equivalent width of fitted gaussians to each line (in pixels)
    ew = np.array(llprops['EW_T'])
    # amplitude  of fitted gaussians to each line
    peak = np.array(llprops['PEAK_T'])
    # catalogue line amplitude
    amp_catalog = np.array(llprops['AMP_CATALOG'])
    # catalogue line wavelength
    wave_catalog = np.array(llprops['WAVE_CATALOG'])
    # spectral order for each line
    ord_t = np.array(llprops['ORD_T'])

    # loop through orders
    for iord in range(n_ord_start, n_ord_final):
        # keep relevant lines
        # -> right order
        # -> finite dv
        gg = (ord_t == iord) & (np.isfinite(dv))
        # put lines into ALL_LINES structure
        # reminder:
        # gparams[0] = output wavelengths
        # gparams[1] = output sigma(gauss fit width)
        # gparams[2] = output amplitude(gauss fit)
        # gparams[3] = difference in input / output wavelength
        # gparams[4] = input amplitudes
        # gparams[5] = output pixel positions
        # gparams[6] = output pixel sigma width (gauss fit width in pixels)
        # gparams[7] = output weights for the pixel position

        # dummy array for weights
        test = np.ones(np.shape(xgau[gg]), 'd') * 1e4
        # get the final wavelength value for each peak in the order
        output_wave_1 = np.polyval(fit_per_order[iord][::-1], xgau[gg])
        # convert the pixel equivalent width to wavelength units
        xgau_ew_ini = xgau[gg] - ew[gg] / 2
        xgau_ew_fin = xgau[gg] + ew[gg] / 2
        ew_ll_ini = np.polyval(fit_per_order[iord, :], xgau_ew_ini)
        ew_ll_fin = np.polyval(fit_per_order[iord, :], xgau_ew_fin)
        ew_ll = ew_ll_fin - ew_ll_ini
        # put all lines in the order into single array
        gau_params = np.column_stack((output_wave_1, ew_ll, peak[gg],
                                      wave_catalog[gg] - output_wave_1,
                                      amp_catalog[gg],
                                      xgau[gg], ew[gg], test))
        # append the array for the order into a list
        all_lines_1.append(gau_params)
    # add to loc
    llprops['ALL_LINES_1'] = all_lines_1
    llprops['LL_PARAM_1'] = np.array(fit_per_order)
    llprops['LL_OUT_1'] = np.array(llprops['WAVE_MAP2'])
    # set sources
    keys = ['ALL_LINES_1', 'LL_PARAM_1', 'LL_OUT_1']
    llprops.set_sources(keys, func_name)

    # For compatibility with already defined functions, I need to save
    # here all_lines_2
    llprops['ALL_LINES_2'] = list(all_lines_1)
    llprops.set_source('ALL_LINES_2', func_name)

    # return llprops
    return llprops


def generate_res_files(params, llprops, outfile, **kwargs):

    func_name = __NAME__ + '.generate_res_files()'
    # get constants from p
    resmap_size = pcheck(params, 'WAVE_HC_RESMAP_SIZE', 'resmap_size',
                         kwargs, func_name, mapf='list', dtype=int)
    # get data from loc
    map_dvs = np.array(llprops['RES_MAP_DVS'])
    map_lines = np.array(llprops['RES_MAP_LINES'])
    map_params = np.array(llprops['RES_MAP_PARAMS'])
    resolution_map = np.array(llprops['RES_MAP'])
    # get dimensions
    nbo, nbpix = llprops['NBO'], llprops['NBPIX']
    # bin size in order direction
    bin_order = int(np.ceil(nbo / resmap_size[0]))
    bin_x = int(np.ceil(nbpix / resmap_size[1]))
    # get ranges of values
    order_range = np.arange(0, nbo, bin_order)
    x_range = np.arange(0, nbpix // bin_x)
    # loop around the order bins
    resdata, hdicts = [], []
    for order_num in order_range:
        # loop around the x position
        for xpos in x_range:
            # set up tmp file
            tmpfile = outfile.completecopy(outfile)
            # get the correct data
            all_dvs = map_dvs[order_num // bin_order][xpos]
            all_lines = map_lines[order_num // bin_order][xpos]
            gparams = map_params[order_num // bin_order][xpos]
            resolution = resolution_map[order_num // bin_order][xpos]
            # get start and end order
            start_order = order_num
            end_order = start_order + bin_order - 1
            # generate header keywordstores
            kw_startorder = ['ORDSTART', '', 'First order covered in res map']
            kw_endorder = ['ORDEND', '', 'Last order covered in res map']
            kw_region = ['REGION', '', 'Region along x-axis in res map']
            largs = [order_num, order_num + bin_order - 1, xpos]
            comment = 'Resolution: order={0}-{1} r={2}'
            kw_res = ['RESOL', '', comment.format(*largs)]
            comment = 'Gaussian params: order={0}-{1} r={2}'
            kw_params = ['GPARAMS', '', comment.format(*largs)]
            # add keys to headed
            tmpfile.add_hkey(kw_startorder, value=start_order)
            tmpfile.add_hkey(kw_endorder, value=end_order)
            tmpfile.add_hkey(kw_region, value=xpos)
            tmpfile.add_hkey(kw_res, value=resolution)
            tmpfile.add_hkey_1d(kw_params, dim1name='coeff', values=gparams)
            # append this hdict to hicts
            hdicts.append(tmpfile.hdict.to_fits_header())
            # push data into correct columns
            resdata.append(np.array(list(zip(all_dvs, all_lines))))
    # return data list and header list
    return resdata, hdicts


# =============================================================================
# Define littrow worker functions
# =============================================================================
def littrow(params, llprops, start, end, wavell, infile, iteration=1,
            **kwargs):
    func_name = __NAME__ + '.littrow_test()'
    # get parameters from params/kwargs
    t_order_start = pcheck(params, 'WAVE_HC_T_ORDER_START', 't_order_start',
                           kwargs, func_name)

    # ------------------------------------------------------------------
    # Littrow test
    # ------------------------------------------------------------------
    # calculate echelle orders
    o_orders = np.arange(start, end)
    echelle_order = t_order_start - o_orders

    # Do Littrow check
    ckwargs = dict(infile=infile, wavell=wavell, iteration=iteration, log=True)
    llprops = calculate_littrow_sol(params, llprops, echelle_order, **ckwargs)
    # ------------------------------------------------------------------
    # Littrow test plot
    # ------------------------------------------------------------------
    # Plot wave solution littrow check
    if params['DRS_PLOT'] > 0:
        # TODO: Add plot
        # plot littrow x pixels against fitted wavelength solution
        # sPlt.wave_littrow_check_plot(p, loc, iteration=1)
        pass
    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------
    ekwargs = dict(infile=infile, wavell=wavell, iteration=1)
    llprops = extrapolate_littrow_sol(params, llprops, **ekwargs)

    # ------------------------------------------------------------------
    # Plot littrow solution
    # ------------------------------------------------------------------
    if params['DRS_PLOT'] > 0:
        # TODO: Add plot
        # plot littrow x pixels against fitted wavelength solution
        # sPlt.wave_littrow_extrap_plot(p, loc, iteration=1)
        pass

    # ------------------------------------------------------------------
    # add parameters to llprops
    llprops['LITTROW_START_{0}'.format(iteration)] = start
    llprops['LITTROW_END_{0}'.format(iteration)] = end
    llprops['T_ORDER_START'] = t_order_start
    # add source
    keys = ['LITTROW_START_{0}'.format(iteration),
            'LITTROW_END_{0}'.format(iteration), 'T_ORDER_START']
    llprops.set_sources(keys, func_name)

    # ------------------------------------------------------------------
    # return props
    return llprops


def calculate_littrow_sol(params, llprops, echelle_order, wavell, infile,
                          iteration=1, log=False, **kwargs):
    """
    Calculate the Littrow solution for this iteration for a set of cut points

    Uses ALL_LINES_i  where i = iteration to calculate the littrow solutions
    for defined cut points (given a cut_step and fit_deg of
    IC_LITTROW_CUT_STEP_i and IC_LITTROW_FIT_DEG_i where i = iteration)

    :param params: parameter dictionary, ParamDict containing constants

    :param llprops: parameter dictionary, ParamDict containing data
        Must contain at least:
            ECHELLE_ORDERS: numpy array (1D), the echelle order numbers
            HCDATA: numpy array (2D), the image data (used for shape)
            ALL_LINES_i: list of numpy arrays, length = number of orders
                         each numpy array contains gaussian parameters
                         for each found line in that order

            where i = iteration

    :param echelle_order: numpy array (1D), the orders (labeled by echelle
                          diffraction number not position)

    :param wavell: numpy array (1D), the initial guess wavelengths for each line

    :param infile: DrsFitsFile, drs fits file instance containing the data
                   for the hc or file file (i.e. must have infile.data) -
                   used only to work out the number of orders and number of
                   pixels

    :param iteration: int, the iteration number (used so we can store multiple
                      calculations in loc, defines "i" in input and outputs
                      from p and loc
    :param log: bool, if True will print a final log message on completion with
                some stats

    :return llprops: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                X_CUT_POINTS_i: numpy array (1D), the x pixel cut points
                LITTROW_MEAN_i: list, the mean position of each cut point
                LITTROW_SIG_i: list, the mean FWHM of each cut point
                LITTROW_MINDEV_i: list, the minimum deviation of each cut point
                LITTROW_MAXDEV_i: list, the maximum deviation of each cut point
                LITTROW_PARAM_i: list of numpy arrays, the gaussian fit
                                 coefficients of each cut point
                LITTROW_XX_i: list, the order positions of each cut point
                LITTROW_YY_i: list, the residual fit of each cut point

                where i = iteration

    ALL_LINES_i definition:
        ALL_LINES_i[row] = [gparams1, gparams2, ..., gparamsN]

                    where:
                        gparams[0] = output wavelengths
                        gparams[1] = output sigma (gauss fit width)
                        gparams[2] = output amplitude (gauss fit)
                        gparams[3] = difference in input/output wavelength
                        gparams[4] = input amplitudes
                        gparams[5] = output pixel positions
                        gparams[6] = output pixel sigma width
                                          (gauss fit width in pixels)
                        gparams[7] = output weights for the pixel position
    """
    func_name = __NAME__ + '.calculate_littrow_sol()'
    # get parameters from params/kwrags
    remove_orders = pcheck(params, 'WAVE_LITTROW_REMOVE_ORDERS',
                           'remove_orders', kwargs, func_name, mapf='list',
                           dtype=int)
    # TODO: Fudge factor - Melissa will fix this :)
    n_order_init = pcheck(params, 'WAVE_LITTROW_ORDER_INIT_{0}'.format(1),
                          'n_order_init', kwargs, func_name)
    n_order_start = pcheck(params, 'WAVE_N_ORD_START', 'n_order_start', kwargs,
                           func_name)
    n_order_final = pcheck(params, 'WAVE_N_ORD_FINAL', 'n_order_final', kwargs,
                           func_name)
    x_cut_step = pcheck(params, 'WAVE_LITTROW_CUT_STEP_{0}'.format(iteration),
                        'x_cut_step', kwargs, func_name)
    fit_degree = pcheck(params, 'WAVE_LITTROW_FIG_DEG_{0}'.format(iteration),
                        'fit_degree', kwargs, func_name)
    # get parameters from loc
    torder = echelle_order
    ll_out = wavell
    # get the total number of orders to fit
    num_orders = len(echelle_order)
    # get dimensions from image
    ydim, xdim = infile.data.shape
    # ----------------------------------------------------------------------
    # test if n_order_init is in remove_orders
    if n_order_init in remove_orders:
        # TODO: Fudge factor - Melissa will fix this
        wargs = ['WAVE_LITTROW_ORDER_INIT_{0}'.format(1),
                 params['WAVE_LITTROW_ORDER_INIT_{0}'.format(1)],
                 "WAVE_LITTROW_REMOVE_ORDERS", func_name]
        WLOG(params, 'error', TextEntry('00-017-00004', args=wargs))
    # ----------------------------------------------------------------------
    # test if n_order_init is in remove_orders
    if n_order_final in remove_orders:
        wargs = ["IC_HC_N_ORD_FINAL", params['IC_HC_N_ORD_FINAL'],
                 "IC_LITTROW_REMOVE_ORDERS", func_name]
        WLOG(params, 'error', TextEntry('00-017-00004', args=wargs))
    # ----------------------------------------------------------------------
    # check that all remove orders exist
    for remove_order in remove_orders:
        if remove_order not in np.arange(n_order_final):
            wargs = [remove_order, 'IC_LITTROW_REMOVE_ORDERS', n_order_init,
                     n_order_final, func_name]
            WLOG(params, 'error', TextEntry('00-017-00005', args=wargs))
    # ----------------------------------------------------------------------
    # check to make sure we have some orders left
    if len(np.unique(remove_orders)) == n_order_final - n_order_start:
        # log littrow error
        eargs = ['WAVE_LITTROW_REMOVE_ORDERS', func_name]
        WLOG(params, 'error', TextEntry('00-017-00006', args=eargs))
    # ----------------------------------------------------------------------
    # deal with removing orders (via weighting stats)
    rmask = np.ones(num_orders, dtype=bool)
    if len(remove_orders) > 0:
        rmask[np.array(remove_orders)] = False
    # storage of results
    keys = ['LITTROW_MEAN', 'LITTROW_SIG', 'LITTROW_MINDEV',
            'LITTROW_MAXDEV', 'LITTROW_PARAM', 'LITTROW_XX', 'LITTROW_YY',
            'LITTROW_INVORD', 'LITTROW_FRACLL', 'LITTROW_PARAM0',
            'LITTROW_MINDEVORD', 'LITTROW_MAXDEVORD']
    for key in keys:
        nkey = key + '_{0}'.format(iteration)
        llprops[nkey] = []
        llprops.set_source(nkey, func_name)
    # construct the Littrow cut points
    x_cut_points = np.arange(x_cut_step, xdim - x_cut_step, x_cut_step)
    # save to storage
    llprops['X_CUT_POINTS_{0}'.format(iteration)] = x_cut_points
    llprops.set_source('X_CUT_POINTS_{0}'.format(iteration), func_name)
    # get the echelle order values
    # TODO check if mask needs resizing
    orderpos = torder[rmask]
    # get the inverse order number
    inv_orderpos = 1.0 / orderpos
    # loop around cut points and get littrow parameters and stats
    for it in range(len(x_cut_points)):
        # this iterations x cut point
        x_cut_point = x_cut_points[it]
        # get the fractional wavelength contrib. at each x cut point
        ll_point = ll_out[:, x_cut_point][rmask]
        ll_start_point = ll_out[n_order_init, x_cut_point]
        frac_ll_point = ll_point / ll_start_point
        # fit the inverse order numbers against the fractional
        #    wavelength contrib.
        coeffs = math.nanpolyfit(inv_orderpos, frac_ll_point, fit_degree)[::-1]
        coeffs0 = math.nanpolyfit(inv_orderpos, frac_ll_point, fit_degree)[::-1]
        # calculate the fit values
        cfit = np.polyval(coeffs[::-1], inv_orderpos)
        # calculate the residuals
        res = cfit - frac_ll_point
        # find the largest residual
        largest = np.max(abs(res))
        sigmaclip = abs(res) != largest
        # remove the largest residual
        inv_orderpos_s = inv_orderpos[sigmaclip]
        frac_ll_point_s = frac_ll_point[sigmaclip]
        # refit the inverse order numbers against the fractional
        #    wavelength contrib. after sigma clip
        coeffs = math.nanpolyfit(inv_orderpos_s, frac_ll_point_s, fit_degree)
        coeffs = coeffs[::-1]
        # calculate the fit values (for all values - including sigma clipped)
        cfit = np.polyval(coeffs[::-1], inv_orderpos)
        # calculate residuals (in km/s) between fit and original values
        respix = speed_of_light * (cfit - frac_ll_point) / frac_ll_point
        # calculate stats
        mean = np.nansum(respix) / len(respix)
        mean2 = np.nansum(respix ** 2) / len(respix)
        rms = np.sqrt(mean2 - mean ** 2)
        mindev = np.min(respix)
        maxdev = np.max(respix)
        mindev_ord = np.argmin(respix)
        maxdev_ord = np.argmax(respix)
        # add to storage
        llprops['LITTROW_INVORD_{0}'.format(iteration)].append(inv_orderpos)
        llprops['LITTROW_FRACLL_{0}'.format(iteration)].append(frac_ll_point)
        llprops['LITTROW_MEAN_{0}'.format(iteration)].append(mean)
        llprops['LITTROW_SIG_{0}'.format(iteration)].append(rms)
        llprops['LITTROW_MINDEV_{0}'.format(iteration)].append(mindev)
        llprops['LITTROW_MAXDEV_{0}'.format(iteration)].append(maxdev)
        llprops['LITTROW_MINDEVORD_{0}'.format(iteration)].append(mindev_ord)
        llprops['LITTROW_MAXDEVORD_{0}'.format(iteration)].append(maxdev_ord)
        llprops['LITTROW_PARAM_{0}'.format(iteration)].append(coeffs)
        llprops['LITTROW_PARAM0_{0}'.format(iteration)].append(coeffs0)
        llprops['LITTROW_XX_{0}'.format(iteration)].append(orderpos)
        llprops['LITTROW_YY_{0}'.format(iteration)].append(respix)
        # if log then log output
        if log:
            # log: littrow check at X={0} mean/rms/min/max/frac
            eargs = [x_cut_point, mean * 1000, rms * 1000, mindev * 1000,
                     maxdev * 1000, mindev / rms, maxdev / rms]
            WLOG(params, '', TextEntry('40-017-00013', args=eargs))

    # add constants
    llprops['LITTROW_REMOVE_ORDERS'] = remove_orders
    llprops['LITTROW_ORDER_INIT_{0}'.format(iteration)] = n_order_init
    llprops['LITTROW_ORDER_START_{0}'.format(iteration)] = n_order_start
    llprops['LITTROW_ORDER_END_{0}'.format(iteration)] = n_order_final
    llprops['LITTROW_X_CUT_STEP_{0}'.format(iteration)] = x_cut_step
    llprops['LITTROW_FIT_DEG_{0}'.format(iteration)] = fit_degree
    # set sources
    keys = ['LITTROW_REMOVE_ORDERS',
            'LITTROW_ORDER_INIT_{0}'.format(iteration),
            'LITTROW_ORDER_START_{0}'.format(iteration),
            'LITTROW_ORDER_END_{0}'.format(iteration),
            'LITTROW_X_CUT_STEP_{0}'.format(iteration),
            'LITTROW_FIT_DEG_{0}'.format(iteration)]
    llprops.set_sources(keys, func_name)

    # return loc
    return llprops


def extrapolate_littrow_sol(params, llprops, wavell, infile, iteration=0,
                            **kwargs):
    """
    Extrapolate and fit the Littrow solution at defined points and return
    the wavelengths, solutions, and cofficients of the littorw fits

    :param params: parameter dictionary, ParamDict containing constants

    :param llprops: parameter dictionary, ParamDict containing data

    :param wavell: numpy array (1D), the initial guess wavelengths for each line

    :param infile: DrsFitsFile, drs fits file instance containing the data
                   for the hc or file file (i.e. must have infile.data) -
                   used only to work out the number of orders and number of
                   pixels

    :param iteration: int, the iteration number (used so we can store multiple
                      calculations in loc, defines "i" in input and outputs
                      from p and loc

    :return llprops: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                LITTROW_EXTRAP_i: numpy array (2D),
                                  size=([no. orders] by [no. cut points])
                                  the wavelength values at each cut point for
                                  each order
                LITTROW_EXTRAP_SOL_i: numpy array (2D),
                                  size=([no. orders] by [no. cut points])
                                  the wavelength solution at each cut point for
                                  each order
                LITTROW_EXTRAP_PARAM_i: numy array (2D),
                                  size=([no. orders] by [the fit degree +1])
                                  the coefficients of the fits for each cut
                                  point for each order

                where i = iteration
    """
    func_name = __NAME__ + '.extrapolate_littrow_sol()'
    # get parameters from p
    fit_degree = pcheck(params, 'WAVE_LITTROW_EXT_ORDER_FIT_DEG', 'fig_degree',
                        kwargs, func_name)
    t_order_start = pcheck(params, 'WAVE_HC_T_ORDER_START', 't_order_start',
                           kwargs, func_name)
    ikey = 'WAVE_LITTROW_ORDER_INIT_{0}'
    n_order_init = pcheck(params, ikey.format(iteration), 'n_order_init',
                          kwargs, func_name)
    # get parameters from llprop
    litt_param = llprops['LITTROW_PARAM_{0}'.format(iteration)]
    # get the dimensions of the data
    ydim, xdim = infile.data.shape
    # get the pixel positions
    x_points = np.arange(xdim)
    # construct the Littrow cut points (in pixels)
    x_cut_points = llprops['X_CUT_POINTS_{0}'.format(iteration)]
    # construct the Littrow cut points (in wavelength)
    ll_cut_points = wavell[n_order_init][x_cut_points]
    # set up storage
    littrow_extrap = np.zeros((ydim, len(x_cut_points)), dtype=float)
    littrow_extrap_sol = np.zeros_like(infile.data)
    littrow_extrap_param = np.zeros((ydim, fit_degree + 1), dtype=float)
    # calculate the echelle order position for this order
    echelle_order_nums = t_order_start - np.arange(ydim)
    # calculate the inverse echelle order nums
    inv_echelle_order_nums = 1.0 / echelle_order_nums
    # loop around the x cut points
    for it in range(len(x_cut_points)):
        # evaluate the fit for this x cut (fractional wavelength contrib.)
        cfit = np.polyval(litt_param[it][::-1], inv_echelle_order_nums)
        # evaluate littrow fit for x_cut_points on each order (in wavelength)
        litt_extrap_o = cfit * ll_cut_points[it]
        # add to storage
        littrow_extrap[:, it] = litt_extrap_o
    # loop around orders and extrapolate
    for order_num in range(ydim):
        # fit the littrow extrapolation
        param = math.nanpolyfit(x_cut_points, littrow_extrap[order_num],
                                fit_degree)[::-1]
        # add to storage
        littrow_extrap_param[order_num] = param
        # evaluate the polynomial for all pixels in data
        littrow_extrap_sol[order_num] = np.polyval(param[::-1], x_points)

    # add to storage
    llprops['LITTROW_EXTRAP_{0}'.format(iteration)] = littrow_extrap
    llprops['LITTROW_EXTRAP_SOL_{0}'.format(iteration)] = littrow_extrap_sol
    llprops['LITTROW_EXTRAP_PARAM_{0}'.format(iteration)] = littrow_extrap_param

    sources = ['LITTROW_EXTRAP_{0}'.format(iteration),
               'LITTROW_EXTRAP_SOL_{0}'.format(iteration),
               'LITTROW_EXTRAP_PARAM_{0}'.format(iteration)]
    llprops.set_sources(sources, func_name)

    # add constants
    llprops['LITTROW_EXT_FITDEG_{0}'.format(iteration)] = fit_degree
    llprops['LITTROW_EXT_ORD_START_{0}'.format(iteration)] = n_order_init
    # set source
    keys = ['LITTROW_EXT_FITDEG_{0}'.format(iteration),
            'LITTROW_EXT_ORD_START_{0}'.format(iteration)]
    llprops.set_sources(keys, func_name)

    # return loc
    return llprops


# =============================================================================
# Define fp worker functions
# =============================================================================


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

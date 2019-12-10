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
import copy

from apero import core
from apero.core import constants
from apero.core import math as mp
from apero import locale
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.io import drs_data
from apero.io import drs_table
from apero.science import velocity
from apero.science.calib import general

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.wave.py'
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
                     master=False, **kwargs):
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
    :param master: bool, if True forces use of the master wavelength solution
    :param kwargs: keyword arguments passed to function

    :keyword force: bool, if True forces wave solution to come from calibDB
    :keyword filename: str or None, the filename to get wave solution from
                       this will overwrite all other options
    :return:
    """
    func_name = __NAME__ + '.get_wavesolution()'
    # get parameters from params/kwargs
    filename = kwargs.get('filename', None)
    force = pcheck(params, 'CALIB_DB_FORCE_WAVESOL', 'force', kwargs,
                   func_name)


    # ------------------------------------------------------------------------
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])

    # deal with fibers that we don't have
    usefiber = pconst.FIBER_WAVE_TYPES(fiber)
    # ------------------------------------------------------------------------
    # get file definitions (wave solution FP and wave solution HC)
    out_wave_fp = core.get_file_definition('WAVE_FP', params['INSTRUMENT'],
                                           kind='red')
    out_wave_hc = core.get_file_definition('WAVE_HC', params['INSTRUMENT'],
                                           kind='red')
    # get calibration key
    key_fp = out_wave_fp.get_dbkey(fiber=usefiber)
    key_hc = out_wave_hc.get_dbkey(fiber=usefiber)
    # ------------------------------------------------------------------------
    # check for filename in inputs
    filename = general.get_input_files(params, 'WAVEFILE', key_fp, header,
                                       filename)
    # then check hc solution (if we don't have an fp solution filename
    if filename is None:
        filename = general.get_input_files(params, 'WAVEFILE', key_hc, header,
                                           filename)
    # ------------------------------------------------------------------------
    # check infile is instance of DrsFitsFile
    if infile is not None:
        if not isinstance(infile, drs_file.DrsFitsFile):
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
    # deal with header having different fiber value that usefiber
    if not force and (params['KW_FIBER'][0] in header):
        if header[params['KW_FIBER'][0]] != usefiber:
            force = True
    # ------------------------------------------------------------------------
    # deal with master = True
    if master is True:
        # get master path
        filename = get_masterwave_filename(params, fiber=usefiber)
    # ------------------------------------------------------------------------
    # Mode 1: wave filename defined
    # ------------------------------------------------------------------------
    # if filename is defined get wave file from this file
    if filename is not None:
        # construct new infile instance (first fp solution then hc solutions)
        if out_wave_fp.suffix in filename:
            wavefile = out_wave_fp.newcopy(filename=filename, recipe=recipe,
                                           fiber=usefiber)
        else:
            wavefile = out_wave_hc.newcopy(filename=filename, recipe=recipe,
                                           fiber=usefiber)
        # read data/header
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
        # get the wave entries
        waveentries = drs_database.get_key_from_db(params, key_fp, cdb, header,
                                                   n_ent=1, required=False)
        # if there are no fp wave solutions use wave hc
        if len(waveentries) == 0:
            waveentries = drs_database.get_key_from_db(params, key_hc, cdb,
                                                       header, n_ent=1,
                                                       required=False)
        # if there are still no wave entries use master wave file
        if len(waveentries) == 0:
            # log warning that no entries were found so using master
            if key_fp == key_hc:
                wargs = [key_fp]
            else:
                wargs = ['{0} or {1}'.format(key_fp, key_hc)]
            WLOG(params, 'warning', TextEntry('10-017-00001', args=wargs))
            # get master path
            wavefilepath = get_masterwave_filename(params, fiber=usefiber)
        else:
            # get badpix filename
            wavefilename = waveentries[filecol][0]
            wavefilepath = os.path.join(params['DRS_CALIB_DB'], wavefilename)
        # construct new infile instance (first fp solution then hc solutions)
        if out_wave_fp.suffix in os.path.basename(wavefilepath):
            wavefile = out_wave_fp.newcopy(filename=wavefilepath, recipe=recipe,
                                           fiber=usefiber)
        else:
            wavefile = out_wave_hc.newcopy(filename=wavefilepath, recipe=recipe,
                                           fiber=usefiber)
        # read data/header
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
        # get keywords from params
        outputkey = params['KW_OUTPUT'][0]
        dprtypekey = params['KW_DPRTYPE'][0]
        # first see if we are dealing with a reduced file
        if outputkey in header:
            # get filetype from header (KW_OUTPUT)
            filetype = header[outputkey]
            # set kind
            kind = 'red'
        # else we can't have a wavelength solution
        else:
            # get filetype from header (dprtype)
            filetype = header[dprtypekey]
            # log error
            eargs = [outputkey, dprtypekey, filetype, func_name]
            WLOG(params, 'error', TextEntry('00-017-00008', args=eargs))
            kind = None
        # get wave file instance
        wavefile = core.get_file_definition(filetype, params['INSTRUMENT'],
                                            kind=kind, fiber=usefiber)
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
    # Log progress
    # -------------------------------------------------------------------------
    wargs = [wavesource, wavefile.filename]
    WLOG(params, '', TextEntry('40-017-00036', args=wargs))

    # ------------------------------------------------------------------------
    # Now deal with using wavefile
    # -------------------------------------------------------------------------
    # extract keys from header
    nbo = wavefile.read_header_key('KW_WAVE_NBO', dtype=int)
    deg = wavefile.read_header_key('KW_WAVE_DEG', dtype=int)
    wavetime = wavefile.read_header_key('KW_MID_OBS_TIME', dtype=float,
                                        has_default=True, default=0.0)
    # get the wfp keys
    wfp_drift = wavefile.read_header_key('KW_WFP_DRIFT', dtype=float,
                                         required=False)
    wfp_fwhm = wavefile.read_header_key('KW_WFP_FWHM', dtype=float,
                                        required=False)
    wfp_contrast = wavefile.read_header_key('KW_WFP_CONTRAST', dtype=float,
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
        if infile is not None:
            nby, nbx = infile.data.shape
        else:
            nby, nbx = header['NAXIS2'], header['NAXIS1']
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
    if wavemap is not None:
        wprops['NBPIX'] = wavemap.shape[1]
    else:
        wprops['NBPIX'] = None
    wprops['DEG'] = deg
    wprops['COEFFS'] = wave_coeffs
    wprops['WAVEMAP'] = wavemap
    wprops['WAVEINST'] = wavefile.completecopy(wavefile)
    wprops['WAVETIME'] = wavetime
    # add the wfp keys
    wfp_keys = ['WFP_DRIFT', 'WFP_FWHM', 'WFP_CONTRAST', 'WFP_MASK',
                'WFP_LINES', 'WFP_TARG_RV', 'WFP_WIDTH', 'WFP_STEP']
    wfp_values = [wfp_drift, wfp_fwhm, wfp_contrast, wfp_mask,
                  wfp_lines, wfp_target_rv, wfp_width, wfp_step]
    # add keys accounting for 'None' and blanks
    for wfpi in range(len(wfp_keys)):
        if wfp_values[wfpi] == '' or wfp_values[wfpi] == 'None':
            wprops[wfp_keys[wfpi]] = None
        else:
            wprops[wfp_keys[wfpi]] = wfp_values[wfpi]
    # set the source
    keys = ['WAVEMAP', 'WAVEFILE', 'WAVESOURCE', 'NBO', 'DEG', 'COEFFS',
            'WAVETIME',  'WAVEINST', 'NBPIX'] + wfp_keys
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
    infile.add_hkey('KW_WFP_MASK', value=props['WFP_MASK'])
    # WFP_LINES should be a list of ints or None or 'None'
    #     (deal with it either way)
    if props['WFP_LINES'] is None:
        infile.add_hkey('KW_WFP_LINES', None)
    elif isinstance(props['WFP_LINES'], str):
        infile.add_hkey('KW_WFP_LINES', value=props['WFP_LINES'])
    else:
        infile.add_hkey('KW_WFP_LINES', value=mp.nansum(props['WFP_LINES']))
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
            coeffs = mp.nanpolyfit(xfit, yfit, required_deg)[::-1]
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
    try:
        wave_mode_hc = int(wave_mode_hc)
    except ValueError:
        pass
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
    # TODO: Revisit use of this
    iprops = generate_shifted_wave_map(params, iprops, **kwargs)
    # ----------------------------------------------------------------------
    # Create new wavelength solution (method 0, old cal_HC_E2DS_EA)
    # ----------------------------------------------------------------------
    if wave_mode_hc == 0:
        llprops = hc_wavesol_ea(params, recipe, iprops, e2dsfile, fiber,
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
    wavell = llprops['LL_OUT_1']
    # run littrow test
    llprops = littrow(params, recipe, llprops, start, end, wavell, e2dsfile,
                      iteration=1, fiber=fiber)
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
    wprops['WFP_MASK'] = None
    wprops['WFP_LINES'] = None
    wprops['WFP_TARG_RV'] = None
    wprops['WFP_WIDTH'] = None
    wprops['WFP_STEP'] = None
    # set the source
    keys = ['WAVEMAP', 'WAVEFILE', 'WAVESOURCE', 'NBO', 'DEG', 'NBPIX',
            'COEFFS',
            'WFP_DRIFT', 'WFP_FWHM', 'WFP_CONTRAST', 'WFP_MASK',
            'WFP_LINES', 'WFP_TARG_RV', 'WFP_WIDTH', 'WFP_STEP']
    wprops.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # Add constants to llprops
    # ----------------------------------------------------------------------
    llprops['USED_N_INIT'] = start
    llprops['USED_N_FIN'] = end
    # define keys
    keys = ['USED_N_INIT', 'USED_N_FIN', 'USED_BLAZE_THRES', 'USED_CAVFIT_DEG',
            'USED_XDIFF_MIN', 'USED_XDIFF_MAX', 'USED_DOPD0', 'USED_LARGE_JUMP',
            'USED_LL_OFFSET', 'USED_DV_MAX', 'USED_LL_FIT_DEG', 'USED_CM_INDEX',
            'USED_BORDER', 'USED_BOX_SIZE', 'USED_SIGLIM', 'USED_LAMP',
            'USED_IPEAK_SPACE', 'USED_EXPWIDTH', 'USED_CUTWIDTH',
            'USED_DV_MAX', 'USED_LL_FIT_DEG', 'USED_UPDATE_CAV',
            'USED_FP_CAV_MODE', 'USED_LL_FIT_MODE', 'USED_ERRX_MIN',
            'USED_MAX_LL_FIT_RMS', 'USED_T_ORD_START', 'USED_WEIGHT_THRES',
            'CCF_SIGDET', 'CCF_BOXSIZE', 'CCF_MAXFLUX', 'CCF_NMAX', 'MASK_MIN',
            'MASK_WIDTH', 'MASK_UNITS']

    # deal with fp keys (that arent used in hcwave sol)
    for key in keys:
        if key not in llprops:
            llprops[key] = 'None'
    llprops.set_sources(keys, func_name)
    # ------------------------------------------------------------------
    # return llprops
    # ------------------------------------------------------------------
    return llprops, wprops


def hc_wavesol_ea(params, recipe, iprops, e2dsfile, fiber, wavell, ampll):
    # ------------------------------------------------------------------
    # Find Gaussian Peaks in HC spectrum
    # ------------------------------------------------------------------
    llprops = find_hc_gauss_peaks(params, recipe, iprops, e2dsfile, fiber)
    # ------------------------------------------------------------------
    # Fit Gaussian peaks (in triplets) to
    # ------------------------------------------------------------------
    llprops = fit_gaussian_triplets(params, recipe, llprops, iprops, wavell,
                                    ampll)
    # ------------------------------------------------------------------
    # Generate Resolution map and line profiles
    # ------------------------------------------------------------------
    llprops = generate_resolution_map(params, recipe, llprops, e2dsfile)
    # ------------------------------------------------------------------
    # Set up all_lines storage
    # ------------------------------------------------------------------
    llprops = all_line_storage(params, llprops)
    # ------------------------------------------------------------------
    # return llprops
    # ------------------------------------------------------------------
    return llprops


def fp_wavesol(params, recipe, hce2dsfile, fpe2dsfile, hcprops, wprops,
               blaze, fiber, **kwargs):
    func_name = __NAME__ + '.fp_wavesol()'
    # get parameters from params / kwargs
    wave_mode_fp = pcheck(params, 'WAVE_MODE_FP', 'wave_mode_fp', kwargs,
                          func_name)
    try:
        wave_mode_fp = int(wave_mode_fp)
    except ValueError:
        pass
    # ----------------------------------------------------------------------
    # deep copy hcprops into llprops
    llprops = ParamDict()
    for key in hcprops.keys():
        llprops[key] = copy.deepcopy(hcprops[key])
        llprops.set_source(key, hcprops.sources[key])

    # ----------------------------------------------------------------------
    # Incorporate FP into solution
    # ----------------------------------------------------------------------
    if wave_mode_fp == 0:
        # ------------------------------------------------------------------
        # Using the Bauer15 (WAVE_E2DS_EA) method:
        # ------------------------------------------------------------------
        # log progress
        wargs = [wave_mode_fp, 'Bauer 2015']
        WLOG(params, 'info', TextEntry('40-017-00021', args=wargs))
        # calculate wave solution
        llprops = fp_wavesol_bauer(params, recipe, llprops, fpe2dsfile, blaze,
                                   fiber)
    elif wave_mode_fp == 1:
        # ------------------------------------------------------------------
        # Using the C Lovis (WAVE_NEW_2) method:
        # ------------------------------------------------------------------
        # log progress
        wargs = [wave_mode_fp, 'Lovis Method']
        WLOG(params, 'info', TextEntry('40-017-00021', args=wargs))
        # calculate wave solution
        llprops = fp_wavesol_lovis(params, recipe, llprops, fpe2dsfile,
                                   hce2dsfile, blaze, fiber)
    else:
        # log that mode is not currently supported
        WLOG(params, 'error', TextEntry('09-017-00003', args=[wave_mode_fp]))
        llprops = None

    # ----------------------------------------------------------------------
    # LITTROW SECTION - common to all methods
    # ----------------------------------------------------------------------
    # set up hc specific terms
    start = pcheck(params, 'WAVE_LITTROW_ORDER_INIT_2', 'littrow_start',
                   kwargs, func_name)
    end = pcheck(params, 'WAVE_LITTROW_ORDER_FINAL_2', 'littrow_end', kwargs,
                 func_name)
    # Copy LL_OUT_1 and LL_PARAM_1 into new constants (for FP integration)
    llprops['LTTROW_EXTRAP_SOL_1'] = np.array(llprops['LL_OUT_1'])
    llprops['LITTORW_EXTRAP_PARAM_1'] = np.array(llprops['LL_PARAM_1'])
    # set wavell
    wavell = llprops['LL_OUT_2']
    # run littrow test
    llprops = littrow(params, recipe, llprops, start, end, wavell, fpe2dsfile,
                      iteration=2, fiber=fiber)
    # ------------------------------------------------------------------
    # Join 0-47 and 47-49 solutions
    # ------------------------------------------------------------------
    start = pcheck(params, 'WAVE_N_ORD_START', 'n_ord_start', kwargs, func_name)
    end = pcheck(params, 'WAVE_N_ORD_FINAL', 'n_ord_fin', kwargs, func_name)
    llprops = join_orders(llprops, start, end)
    # ------------------------------------------------------------------
    # Plot single order, wavelength-calibrated, with found lines
    # ------------------------------------------------------------------
    recipe.plot('WAVE_FP_SINGLE_ORDER', order=None, llprops=llprops,
                hcdata=hce2dsfile.data)
    # ----------------------------------------------------------------------
    # FP CCF COMPUTATION - common to all methods
    # ----------------------------------------------------------------------
    # get the FP (reference) fiber
    pconst = constants.pload(params['INSTRUMENT'])
    sfiber, rfiber = pconst.FIBER_CCF()
    # compute the ccf
    ccfargs = [fpe2dsfile, fpe2dsfile.data, blaze, llprops['LL_FINAL'], rfiber]
    rvprops = velocity.compute_ccf_fp(params, recipe, *ccfargs)
    # merge rvprops into llprops (shallow copy)
    llprops.merge(rvprops)
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    wavefile = recipe.outputs['WAVE_FPMAP'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    wavefile.construct_filename(params, infile=hce2dsfile)
    # ----------------------------------------------------------------------
    # Update wprops
    # ----------------------------------------------------------------------
    wprops['WAVEFILE'] = wavefile.filename
    wprops['WAVESOURCE'] = recipe.name
    wprops['COEFFS'] = llprops['LL_PARAM_FINAL']
    wprops['WAVEMAP'] = llprops['LL_FINAL']
    wprops['NBO'] = llprops['LL_PARAM_FINAL'].shape[0]
    wprops['DEG'] = llprops['LL_PARAM_FINAL'].shape[1] - 1
    # set source
    keys = ['WAVEMAP', 'WAVEFILE', 'WAVESOURCE', 'NBO', 'DEG', 'COEFFS']
    wprops.set_sources(keys, func_name)
    # update ccf properties
    wprops['WFP_DRIFT'] = rvprops['MEAN_RV']
    wprops['WFP_FWHM'] = rvprops['MEAN_FWHM']
    wprops['WFP_CONTRAST'] = rvprops['MEAN_CONTRAST']
    wprops['WFP_MASK'] = rvprops['CCF_MASK']
    wprops['WFP_LINES'] = rvprops['TOT_LINE']
    wprops['WFP_TARG_RV'] = rvprops['TARGET_RV']
    wprops['WFP_WIDTH'] = rvprops['CCF_WIDTH']
    wprops['WFP_STEP'] = rvprops['CCF_STEP']
    # set sources
    keys = ['WFP_DRIFT', 'WFP_FWHM', 'WFP_CONTRAST', 'WFP_MASK', 'WFP_LINES',
            'WFP_TARG_RV', 'WFP_WIDTH', 'WFP_STEP']
    wprops.set_sources(keys, func_name)

    # ------------------------------------------------------------------
    # return llprops
    # ------------------------------------------------------------------
    return llprops, wprops


def fp_wavesol_bauer(params, recipe, llprops, fpe2dsfile, blaze, fiber,
                     **kwargs):
    func_name = __NAME__ + '.fp_wavesol_bauer()'
    # get parameters from params/kwargs
    start = pcheck(params, 'WAVE_N_ORD_START')
    end = pcheck(params, 'WAVE_N_ORD_FINAL')
    dopd0 = pcheck(params, 'WAVE_FP_DOPD0', 'dopd0', kwargs, func_name)
    fit_deg = pcheck(params, 'WAVE_FP_CAVFIT_DEG', 'fit_deg', kwargs, func_name)
    fp_large_jump = pcheck(params, 'WAVE_FP_LARGE_JUMP', 'fp_large_jump',
                           kwargs, func_name)
    ll_fit_degree = pcheck(params, 'WAVE_FP_LL_DEGR_FIT', 'll_fit_degree',
                           kwargs, func_name)
    cm_ind = pcheck(params, 'WAVE_FP_CM_IND', 'cm_ind', kwargs, func_name)
    errx_min = pcheck(params, 'WAVE_FP_ERRX_MIN', 'errx_min', kwargs, func_name)
    max_ll_fit_rms = pcheck(params, 'WAVE_FP_MAX_LLFIT_RMS', 'max_ll_fit_rms',
                            kwargs, func_name)
    t_order_start = pcheck(params, 'WAVE_T_ORDER_START', 't_order_start',
                           kwargs, func_name)
    weight_thres = pcheck(params, 'WAVE_FP_WEIGHT_THRES', 'weight_thres',
                          kwargs, func_name)

    # Log the file we are using
    wargs = [fpe2dsfile.filename]
    WLOG(params, '', TextEntry('40-017-00022', args=wargs))
    # ------------------------------------------------------------------
    # Find the fp lines and measure the cavity width dependency
    # ------------------------------------------------------------------
    llprops = add_fpline_calc_cwid(params, llprops, fpe2dsfile, blaze, dopd0,
                                   fit_deg, fp_large_jump, start, end, cm_ind)
    # ------------------------------------------------------------------
    # FP solution plots
    # ------------------------------------------------------------------
    recipe.plot('WAVE_FP_FINAL_ORDER', llprops=llprops, fiber=fiber,
                iteration=1, end=end, fpdata=fpe2dsfile.data)
    recipe.plot('WAVE_FP_LWID_OFFSET', llprops=llprops)
    recipe.plot('WAVE_FP_WAVE_RES', llprops=llprops)

    # ------------------------------------------------------------------
    # Create new wavelength solution
    # ------------------------------------------------------------------
    # get wavelengths for 1d fit
    wavell = llprops['LITTROW_EXTRAP_SOL_1'][start:end]
    # fit the 1d solution
    llprops = fit_1d_solution(params, llprops, wavell, start, end, fiber,
                              errx_min, ll_fit_degree, max_ll_fit_rms,
                              t_order_start, weight_thres, iteration=2)
    # ----------------------------------------------------------------------
    # Add constants to llprops
    # ----------------------------------------------------------------------
    llprops['USED_N_INIT'] = start
    llprops['USED_N_FIN'] = end
    llprops['USED_BLAZE_THRES'] = 'None'
    llprops['USED_XDIFF_MIN'] = 'None'
    llprops['USED_XDIFF_MAX'] = 'None'
    llprops['USED_DOPD0'] = dopd0
    llprops['USED_LL_OFFSET'] = 'None'
    llprops['USED_DV_MAX'] = 'None'
    llprops['USED_LL_FIT_DEG'] = ll_fit_degree
    llprops['USED_UPDATE_CAV'] = 'None'
    llprops['USED_FP_CAV_MODE'] = 'None'
    llprops['USED_LL_FIT_MODE'] = 'None'
    llprops['USED_ERRX_MIN'] = errx_min
    llprops['USED_MAX_LL_FIT_RMS'] = max_ll_fit_rms
    llprops['USED_T_ORD_START'] = t_order_start
    llprops['USED_WEIGHT_THRES'] = weight_thres
    llprops['USED_CAVFIT_DEG'] = fit_deg
    llprops['USED_LARGE_JUMP'] = fp_large_jump
    llprops['USED_CM_INDEX'] = cm_ind

    keys = ['USED_N_INIT', 'USED_N_FIN', 'USED_BLAZE_THRES', 'USED_CAVFIT_DEG',
            'USED_XDIFF_MIN', 'USED_XDIFF_MAX', 'USED_DOPD0', 'USED_LARGE_JUMP',
            'USED_LL_OFFSET', 'USED_DV_MAX', 'USED_LL_FIT_DEG', 'USED_CM_INDEX',
            'USED_DV_MAX', 'USED_LL_FIT_DEG', 'USED_UPDATE_CAV',
            'USED_FP_CAV_MODE', 'USED_LL_FIT_MODE', 'USED_ERRX_MIN',
            'USED_MAX_LL_FIT_RMS', 'USED_T_ORD_START', 'USED_WEIGHT_THRES']
    llprops.set_sources(keys, func_name)
    # ------------------------------------------------------------------
    return llprops


def fp_wavesol_lovis(params, recipe, llprops, fpe2dsfile, hce2dsfile,
                     blaze, fiber, **kwargs):
    func_name = __NAME__ + '.fp_wavesol_lovis()'
    # get parameters from params/kwargs
    n_init = pcheck(params, 'WAVE_N_ORD_START', 'n_init', kwargs, func_name)
    n_fin = pcheck(params, 'WAVE_N_ORD_FINAL', 'n_fin', kwargs, func_name)
    wave_blaze_thres = pcheck(params, 'WAVE_FP_BLAZE_THRES', 'wave_blaze_thres',
                              kwargs, func_name)
    xdiff_min = pcheck(params, 'WAVE_FP_XDIF_MIN', 'xdiff_min', kwargs,
                       func_name)
    xdiff_max = pcheck(params, 'WAVE_FP_XDIF_MAX', 'xdiff_max', kwargs,
                       func_name)
    dopd0 = pcheck(params, 'WAVE_FP_DOPD0', 'dopd0', kwargs, func_name)
    ll_offset = pcheck(params, 'WAVE_FP_LL_OFFSET', 'll_offset', kwargs,
                       func_name)
    dv_max = pcheck(params, 'WAVE_FP_DV_MAX', 'dv_max', kwargs, func_name)
    ll_fit_degree = pcheck(params, 'WAVE_FP_LL_DEGR_FIT', 'll_fit_degree',
                           kwargs, func_name)
    update_cavity = pcheck(params, 'WAVE_FP_UPDATE_CAVITY', 'update_cavity',
                           kwargs, func_name)
    fp_cavfit_mode = pcheck(params, 'WAVE_FP_CAVFIT_MODE', 'fp_cavfit_mode',
                            kwargs, func_name)
    fp_llfit_mode = pcheck(params, 'WAVE_FP_LLFIT_MODE', 'ff_llfit_mode',
                           kwargs, func_name)
    errx_min = pcheck(params, 'WAVE_FP_ERRX_MIN', 'errx_min', kwargs, func_name)
    max_ll_fit_rms = pcheck(params, 'WAVE_FP_MAX_LLFIT_RMS', 'max_ll_fit_rms',
                            kwargs, func_name)
    t_order_start = pcheck(params, 'WAVE_T_ORDER_START', 't_order_start',
                           kwargs, func_name)
    weight_thres = pcheck(params, 'WAVE_FP_WEIGHT_THRES', 'weight_thres',
                          kwargs, func_name)

    # Log the file we are using
    wargs = [fpe2dsfile.filename]
    WLOG(params, '', TextEntry('40-017-00022', args=wargs))

    # ------------------------------------------------------------------
    # Find FP lines
    # ------------------------------------------------------------------
    # find the fp lines
    llprops = find_fp_lines_new(params, llprops, fpe2dsfile)

    # ------------------------------------------------------------------
    # Number FP peaks differentially and identify gaps
    # ------------------------------------------------------------------
    fout = find_num_fppeak_diff(llprops, blaze, n_init, n_fin, wave_blaze_thres,
                                xdiff_min, xdiff_max)
    fp_ll, dif_n, fp_order, fp_xx, fp_amp = fout

    # ----------------------------------------------------------------------
    # Assign absolute FP numbers for reddest order
    # ----------------------------------------------------------------------
    # determine absolute number for reference peak of reddest order
    # take reddest FP line and apply FP equation
    m_init = int(round(dopd0 / fp_ll[-1][-1]))
    # absolute numbers for reddest order:
    # get differential numbers for reddest order peaks
    aux_n = dif_n[n_fin - n_init - 1]
    # calculate absolute peak numbers for reddest order
    m_aux = m_init - aux_n + aux_n[-1]
    # set m vector
    m_vec = m_aux
    # initialise vector of order numbers for previous order
    m_ord_prev = m_aux

    # ----------------------------------------------------------------------
    # Assign absolute FP numbers for rest of orders by wavelength matching
    # ----------------------------------------------------------------------
    m_vec = assign_abs_fp_numbers(params, fp_ll, dif_n, m_vec, m_ord_prev,
                                 n_init, n_fin, ll_offset)

    # ----------------------------------------------------------------------
    # Derive d for each HC line
    # ----------------------------------------------------------------------
    hout = get_d_for_each_hcline(params, recipe, llprops, fp_order, fp_xx,
                                 m_vec, blaze, n_init, n_fin, wave_blaze_thres,
                                 dv_max, ll_fit_degree)
    one_m_d, d_arr, hc_ll_test, hc_ord_test = hout

    # ----------------------------------------------------------------------
    # Fit (1/m) vs d
    # ----------------------------------------------------------------------
    fout = fit_1m_vs_d(params, recipe, one_m_d, d_arr, hc_ll_test,
                       update_cavity, m_init, fp_ll, fiber)
    fit_1m_d, fit_ll_d, one_m_d, d_arr = fout

    # ----------------------------------------------------------------------
    # Update FP peak wavelengths
    # ----------------------------------------------------------------------
    llprops = update_fp_peak_wavelengths(params, recipe, llprops, fit_ll_d,
                                         m_vec, fp_order, fp_xx, fp_amp,
                                         fp_cavfit_mode, n_init, n_fin)

    # ----------------------------------------------------------------------
    # Fit wavelength solution from FP peaks
    # ----------------------------------------------------------------------
    llprops = fit_wavesol_from_fppeaks(params, llprops, fp_ll, fiber, n_init,
                                       n_fin, fp_llfit_mode, ll_fit_degree,
                                       errx_min, max_ll_fit_rms, t_order_start,
                                       weight_thres)

    # ----------------------------------------------------------------------
    # Multi-order HC lines plot
    # ----------------------------------------------------------------------
    # get graph starting point
    n_plot_init = params['WAVE_FP_PLOT_MULTI_INIT']
    # get the number of orders to plot
    n_nbo = params['WAVE_FP_PLOT_MULTI_NBO']
    # deal with n_plot_init being out of bounds
    if n_plot_init >= n_fin:
        wargs = [n_plot_init, n_fin, 'WAVE_FP_MULTI_ORDER']
        WLOG(params, 'warning', TextEntry('10-017-00012', args=wargs))
    else:
        recipe.plot('WAVE_FP_MULTI_ORDER', hc_ll=hc_ll_test, hc_ord=hc_ord_test,
                    hcdata=hce2dsfile.data, wave=llprops['LL_OUT_2'],
                    init=n_plot_init, fin=n_fin, nbo=n_nbo, params=params)

    # ----------------------------------------------------------------------
    # Add constants to llprops (Needs to have all from fp_wavesol_bauer
    #    AND fp_wavesol_lovis)
    # ----------------------------------------------------------------------
    llprops['USED_N_INIT'] = n_init
    llprops['USED_N_FIN'] = n_fin
    llprops['USED_BLAZE_THRES'] = wave_blaze_thres
    llprops['USED_XDIFF_MIN'] = xdiff_min
    llprops['USED_XDIFF_MAX'] = xdiff_max
    llprops['USED_DOPD0'] = dopd0
    llprops['USED_LL_OFFSET'] = ll_offset
    llprops['USED_DV_MAX'] = dv_max
    llprops['USED_LL_FIT_DEG'] = ll_fit_degree
    llprops['USED_UPDATE_CAV'] = update_cavity
    llprops['USED_FP_CAV_MODE'] = fp_cavfit_mode
    llprops['USED_LL_FIT_MODE'] = fp_llfit_mode
    llprops['USED_ERRX_MIN'] = errx_min
    llprops['USED_MAX_LL_FIT_RMS'] = max_ll_fit_rms
    llprops['USED_T_ORD_START'] = t_order_start
    llprops['USED_WEIGHT_THRES'] = weight_thres
    llprops['USED_CAVFIT_DEG'] = 'None'
    llprops['USED_LARGE_JUMP'] = 'None'
    llprops['USED_CM_INDEX'] = 'None'

    keys = ['USED_N_INIT', 'USED_N_FIN', 'USED_BLAZE_THRES', 'USED_CAVFIT_DEG',
            'USED_XDIFF_MIN', 'USED_XDIFF_MAX', 'USED_DOPD0', 'USED_LARGE_JUMP',
            'USED_LL_OFFSET', 'USED_DV_MAX', 'USED_LL_FIT_DEG', 'USED_CM_INDEX',
            'USED_DV_MAX', 'USED_LL_FIT_DEG', 'USED_UPDATE_CAV',
            'USED_FP_CAV_MODE', 'USED_LL_FIT_MODE', 'USED_ERRX_MIN',
            'USED_MAX_LL_FIT_RMS', 'USED_T_ORD_START', 'USED_WEIGHT_THRES']
    llprops.set_sources(keys, func_name)

    # return llprops
    return llprops


# =============================================================================
# Define hc aux functions
# =============================================================================
def hc_quality_control(params, hcprops):
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
    if mp.nanmin(wave_diff) < 0:
        fail_msg.append(textdict['40-017-00016'])
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mp.nanmin(wave_diff))
    qc_names.append('MIN WAVE DIFF HC')
    qc_logic.append('MIN WAVE DIFF < 0')
    # --------------------------------------------------------------
    # check the difference between consecutive pixels along an
    #     order is always positive
    # loop through the orders
    ord_check = np.zeros(hcprops['NBO'], dtype=bool)
    for order in range(hcprops['NBO']):
        wave0 = hcprops['WAVE_MAP2'][order, :-1]
        wave1 = hcprops['WAVE_MAP2'][order, 1:]
        ord_check[order] = np.all(wave1 > wave0)
    if np.all(ord_check):
        qc_pass.append(1)
        qc_values.append('None')
    else:
        fail_msg.append(textdict['40-017-00017'])
        qc_pass.append(0)
        badvalues = np.where(~ord_check)[0].astype(str)
        qc_values.append(','.join(list(badvalues)))
    # add to qc header lists
    qc_names.append('WAVE DIFF ALONG ORDER HC')
    qc_logic.append('WAVE DIFF ALONG ORDER < 0')
    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #     quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
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
        res_hc.append(hc_ll_diff * speed_of_light / hc_ll_cat)
        sumres_hc += mp.nansum(res_hc[order])
        sumres2_hc += mp.nansum(res_hc[order] ** 2)
    # get the total number of lines
    total_lines_hc = len(np.concatenate(res_hc))
    # get the final mean and varianace
    final_mean_hc = sumres_hc / total_lines_hc
    final_var_hc = (sumres2_hc / total_lines_hc) - (final_mean_hc ** 2)
    # log global hc stats
    wargs = [fiber, final_mean_hc * 1000.0, np.sqrt(final_var_hc) * 1000.0,
             total_lines_hc, 1000.0 * np.sqrt(final_var_hc / total_lines_hc)]
    WLOG(params, 'info', TextEntry('40-017-00018', args=wargs))


def hc_write_wavesolution(params, recipe, llprops, infile, fiber, combine,
                          rawhcfiles, qc_params, iwprops, wprops):
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
    wavefile.add_hkey('KW_FIBER', value=fiber)
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
    wavefile = add_wave_keys(wavefile, wprops)
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
    # add to output files (for indexing)
    recipe.add_output_file(wavefile)
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
    # set output key
    resfile.add_hkey('KW_OUTPUT', value=resfile.name)
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
    # add to output files (for indexing)
    recipe.add_output_file(resfile)


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


def find_hc_gauss_peaks(params, recipe, iprops, e2dsfile, fiber, **kwargs):
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
                rms = mp.nanmedian(np.abs(segment[1:] - segment[:-1]))
                # find the peak pixel value
                peak = mp.nanmax(segment) - mp.nanmedian(segment)
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
                    popt_left, gfit = mp.gauss_fit_nn(*gargs)
                    # residual of the fit normalized by peak value similar to
                    #    an 1/SNR value
                    gauss_rms_dev0 = mp.nanstd(segment - gfit) / popt_left[0]
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
                        llprops['GFIT_INI'].append(gfit)
            # display the number of peaks found
            WLOG(params, '', TextEntry('40-017-00005', args=[npeaks]))
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
        if __name__ == '__main__':
            recipe.plot('WAVE_HC_GUESS', params=params, wave=iprops['WAVEMAP'],
                        spec=hc_sp, llprops=llprops, nbo=nbo)
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
    llprops['GFIT_INI'] = []
    llprops.set_sources(['XPIX_INI', 'GFIT_INI'], func_name)
    # return properties param dict
    return llprops, exists


def fit_gaussian_triplets(params, recipe, llprops, iprops, wavell, ampll,
                          **kwargs):
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
            if mp.nansum(good) <= nmax_bright:
                nmax = mp.nansum(good) - 1
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
            num_gb = int(mp.nansum(good_bright))
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
                coeffs = mp.nanpolyfit(xx, yy, triplet_deg)
                # extrapolate out over all lines
                fit_all = np.polyval(coeffs, xgau[good_all])
                # work out the error in velocity
                ev = ((wave_catalog[good_all] / fit_all) - 1) * speed_of_light
                # work out the number of lines to keep
                nkeep = mp.nansum(np.abs(ev) < cut_fit_threshold)
                # if number of lines to keep largest seen --> store
                if nkeep > bestn:
                    bestn = nkeep
                    best_coeffs = np.array(coeffs)
            # Log the total number of valid lines found
            wargs = [order_num, bestn, mp.nansum(good_all)]
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
                if mp.nanmax(abs_ev) > cut_fit_threshold:
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
        recipe.plot('WAVE_HC_BRIGHTEST_LINES', wave=wave_catalog, dv=dv,
                    mask=brightest_lines, iteration=sol_iteration,
                    niters=n_iterations)
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
        if mp.nansum(good) < min_tot_num_lines:
            # log error that we have insufficient lines found
            eargs = [mp.nansum(good), min_tot_num_lines, func_name]
            WLOG(params, 'error', TextEntry('00-017-00003', args=eargs))

        # ------------------------------------------------------------------
        # Linear model slice generation
        # ------------------------------------------------------------------
        # storage for the linear model slice
        lin_mod_slice = np.zeros((len(xgau), mp.nansum(order_fit_cont)))
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
        amps0 = np.zeros(mp.nansum(order_fit_cont))

        # Loop sigma_clip_num times for sigma clipping and numerical
        #    convergence. In most cases ~10 iterations would be fine but this
        #    is fast
        for sigma_it in range(sigma_clip_num):
            # calculate the linear minimization
            largs = [wave_catalog - recon0, lin_mod_slice]
            with warnings.catch_warnings(record=True) as _:
                amps, recon = mp.linear_minimization(*largs)
            # add the amps and recon to new storage
            amps0 = amps0 + amps
            recon0 = recon0 + recon
            # loop around the amplitudes and normalise
            for a_it in range(len(amps0)):
                # work out the residuals
                res = (wave_catalog - recon0)
                # work out the sum of residuals
                sum_r = mp.nansum(res * lin_mod_slice[:, a_it])
                sum_l2 = mp.nansum(lin_mod_slice[:, a_it] ** 2)
                # normalise by sum squared
                ampsx = sum_r / sum_l2
                # add this contribution on
                amps0[a_it] += ampsx
                recon0 += (ampsx * lin_mod_slice[:, a_it])
            # recalculate dv [in km/s]
            dv = ((wave_catalog / recon0) - 1) * speed_of_light
            # calculate the standard deviation
            sig = mp.nanstd(dv)
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
                if mp.nanmax(absdev_ord) > sigma_clip_thres:
                    # create mask for worst line
                    sig_mask = absdev_ord < mp.nanmax(absdev_ord)
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
        recipe.plot('WAVE_HC_TFIT_GRID', orders=orders, wave=wave_catalog,
                    recon=recon0, rms=gauss_rms_dev, xgau=xgau, ew=ew,
                    iteration=sol_iteration, niters=n_iterations)

        # ------------------------------------------------------------------
        # Construct wave map
        # ------------------------------------------------------------------
        xpix = np.arange(nbpix)
        wave_map2 = np.zeros((nbo, nbpix))
        poly_wave_sol = np.zeros_like(iprops['COEFFS'])

        # loop around the orders
        for order_num in range(nbo):
            order_mask = orders == order_num
            if mp.nansum(order_mask) == 0:
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


def generate_resolution_map(params, recipe, llprops, e2dsfile, **kwargs):
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
            all_lines = np.zeros((mp.nansum(mask), 2 * wsize + 1))
            all_dvs = np.zeros((mp.nansum(mask), 2 * wsize + 1))

            # set up base
            base = np.zeros(2 * wsize + 1, dtype=bool)
            base[0:3] = True
            base[2 * wsize - 2: 2 * wsize + 1] = True

            # loop around all good lines
            # we express everything in velocity space rather than
            # pixels. This allows us to merge all lines in a single
            # profile and removes differences in pixel sampling and
            # resolution.
            for it in range(int(mp.nansum(mask))):
                # get limits
                border = int(b_orders[it])
                start = int(b_xgau[it] + 0.5) - wsize
                end = int(b_xgau[it] + 0.5) + wsize + 1
                # get line
                line = np.array(hc_sp)[border, start:end]
                # subtract median base and normalise line
                line -= mp.nanmedian(line[base])
                line /= mp.nansum(line)
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
                    popt, pcov = mp.fit_gauss_with_slope(**fargs)
                except Exception as e:
                    # log error: Resolution map curve_fit error
                    eargs = [type(e), e, func_name]
                    WLOG(params, 'error', TextEntry('09-017-00002', args=eargs))
                # calculate residuals for full line list
                res = all_lines - mp.gauss_fit_s(all_dvs, *popt)
                # calculate RMS of residuals
                rms = res / mp.nanmedian(np.abs(res))
                # calculate max deviation
                maxdev = mp.nanmax(np.abs(rms[keep]))
                # re-calculate the keep mask
                keep[np.abs(rms) > max_dev_thres] = False
                # increase value of iterator
                n_it += 1
            # calculate resolution
            resolution = popt[2] * mp.fwhm()
            # store order criteria
            order_dvs.append(all_dvs[keep])
            order_lines.append(all_lines[keep])
            order_params.append(popt)
            # push resolution into resolution map
            resolution1 = speed_of_light / resolution
            resolution_map[order_num // bin_order, xpos] = resolution1
            # log resolution output
            wargs = [order_num, order_num + bin_order, mp.nansum(mask), xpos,
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
    wargs = [mp.nanmean(resolution_map), mp.nanmedian(resolution_map),
             mp.nanstd(resolution_map)]
    WLOG(params, '', TextEntry('40-017-00012', args=wargs))

    # map line profile map
    recipe.plot('WAVE_HC_RESMAP', params=params, resmap_size=resmap_size,
                map_dvs=map_dvs, map_lines=map_lines, map_params=map_params,
                res_map=resolution_map, nbo=nbo, nbpix=nbpix)

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
def littrow(params, recipe, llprops, start, end, wavell, infile, iteration=1,
            fiber=None, **kwargs):
    func_name = __NAME__ + '.littrow_test()'
    # get parameters from params/kwargs
    t_order_start = pcheck(params, 'WAVE_T_ORDER_START', 't_order_start',
                           kwargs, func_name)

    # ------------------------------------------------------------------
    # Littrow test
    # ------------------------------------------------------------------
    # calculate echelle orders
    o_orders = np.arange(start, end)
    echelle_order = t_order_start - o_orders

    # Do Littrow check
    ckwargs = dict(infile=infile, wavell=wavell[start:end, :],
                   iteration=iteration, log=True)
    llprops = calculate_littrow_sol(params, llprops, echelle_order, **ckwargs)
    # ------------------------------------------------------------------
    # Littrow test plot
    # ------------------------------------------------------------------
    # Plot wave solution littrow check
    plotname = 'WAVE_LITTROW_CHECK{0}'.format(iteration)
    recipe.plot(plotname, params=params, llprops=llprops, iteration=iteration,
                fiber=fiber)
    # only plot summary plot for final iteration
    if iteration == 2:
        recipe.plot('SUM_WAVE_LITTROW_CHECK', params=params, llprops=llprops,
                    iteration=iteration, fiber=fiber)
    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------
    ekwargs = dict(infile=infile, wavell=wavell, iteration=iteration)
    llprops = extrapolate_littrow_sol(params, llprops, **ekwargs)

    # ------------------------------------------------------------------
    # Plot littrow solution
    # ------------------------------------------------------------------
    plotname = 'WAVE_LITTROW_EXTRAP{0}'.format(iteration)
    recipe.plot(plotname, params=params, llprops=llprops,
                iteration=iteration, fiber=fiber, image=infile.data)
    # only plot summary plot for final iteration
    if iteration == 2:
        recipe.plot('SUM_WAVE_LITTROW_EXTRAP', params=params, llprops=llprops,
                iteration=iteration, fiber=fiber, image=infile.data)
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
    n_order_start = pcheck(params, 'WAVE_N_ORD_START', 'n_order_start',
                           kwargs, func_name)
    n_order_final = pcheck(params, 'WAVE_N_ORD_FINAL', 'n_order_final',
                           kwargs, func_name)
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
        wargs = ["IC_N_ORD_FINAL", params['IC_N_ORD_FINAL'],
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
        coeffs = mp.nanpolyfit(inv_orderpos, frac_ll_point, fit_degree)[::-1]
        coeffs0 = mp.nanpolyfit(inv_orderpos, frac_ll_point, fit_degree)[::-1]
        # calculate the fit values
        cfit = np.polyval(coeffs[::-1], inv_orderpos)
        # calculate the residuals
        res = cfit - frac_ll_point
        # find the largest residual
        largest = mp.nanmax(abs(res))
        sigmaclip = abs(res) != largest
        # remove the largest residual
        inv_orderpos_s = inv_orderpos[sigmaclip]
        frac_ll_point_s = frac_ll_point[sigmaclip]
        # refit the inverse order numbers against the fractional
        #    wavelength contrib. after sigma clip
        coeffs = mp.nanpolyfit(inv_orderpos_s, frac_ll_point_s, fit_degree)
        coeffs = coeffs[::-1]
        # calculate the fit values (for all values - including sigma clipped)
        cfit = np.polyval(coeffs[::-1], inv_orderpos)
        # calculate residuals (in km/s) between fit and original values
        respix = speed_of_light * (cfit - frac_ll_point) / frac_ll_point
        # calculate stats
        mean = mp.nansum(respix) / len(respix)
        mean2 = mp.nansum(respix ** 2) / len(respix)
        rms = np.sqrt(mean2 - mean ** 2)
        mindev = mp.nanmin(respix)
        maxdev = mp.nanmax(respix)
        mindev_ord = mp.nanargmin(respix)
        maxdev_ord = mp.nanargmax(respix)
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
    t_order_start = pcheck(params, 'WAVE_T_ORDER_START', 't_order_start',
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
        param = mp.nanpolyfit(x_cut_points, littrow_extrap[order_num],
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
def add_fpline_calc_cwid(params, llprops, fpe2dsfile, blaze, dopd0, fit_deg,
                          fp_large_jump, n_ord_start_fp, n_ord_final_fp,
                          cm_ind):
    """
    Derives the FP line wavelengths from the first solution
    Follows the Bauer et al 2015 procedure

    :param params: parameter dictionary, ParamDict containing constants

    :param llprops: parameter dictionary, ParamDict containing data
        Must contain at least:
            FPDATA: the FP e2ds data
            LITTROW_EXTRAP_SOL_1: the wavelength solution derived from the HC
                                  and Littrow-constrained
            LL_PARAM_1: the parameters of the wavelength solution
            ALL_LINES_2: list of numpy arrays, length = number of orders
                       each numpy array contains gaussian parameters
                       for each found line in that order
            BLAZE: numpy array (2D), the blaze data

    :param fpe2dsfile:
    :param blaze:
    :param dopd0:
    :param fit_deg:
    :param fp_large_jump:
    :param n_ord_start_fp:
    :param n_ord_final_fp:
    :param cm_ind:

    :return llprops: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                FP_LL_POS: numpy array, the initial wavelengths of the FP lines
                FP_XX_POS: numpy array, the pixel positions of the FP lines
                FP_M: numpy array, the FP line numbers
                FP_DOPD_T: numpy array, the measured cavity width for each line
                FP_AMPL: numpy array, the FP line amplitudes
                FP_LL_POS_NEW: numpy array, the corrected wavelengths of the
                               FP lines
                ALL_LINES_2: list of numpy arrays, length = number of orders
                             each numpy array contains gaussian parameters
                             for each found line in that order

    """
    func_name = __NAME__ + '.add_fpline_calc_cwid()'
    # find FP lines
    llprops = find_fp_lines_new(params, llprops, fpe2dsfile)
    # get all_lines_2 from llprops
    all_lines_2 = llprops['ALL_LINES_2']
    # set up storage
    llpos_all, xxpos_all, ampl_all = [], [], []
    m_fp_all, weight_bl_all, order_rec_all, dopd_all = [], [], [], []
    ll_prev, m_prev = np.array([]), np.array([])
    # ----------------------------------------------------------------------
    # loop through the orders from red to blue
    for order_num in range(n_ord_final_fp, n_ord_start_fp - 1, -1):
        # select the lines in the order
        gg = llprops['ORDPEAK'] == order_num
        # store the initial wavelengths of the lines
        ctmp = llprops['LITTROW_EXTRAP_PARAM_1'][order_num][::-1]
        # store the pixel positions of the lines
        xxpos = llprops['XPEAK'][gg]
        llpos = np.polyval(ctmp, xxpos)
        # get the median pixel difference between successive lines
        #    (to check for gaps)
        xxpos_diff_med = mp.nanmedian(xxpos[1:] - xxpos[:-1])
        # store the amplitudes of the fp lines
        ampl = llprops['AMPPEAK'][gg]
        # store the values of the blaze at the pixel positions of the lines
        weight_bl = np.zeros_like(llpos)
        # get and normalize blaze for the order
        nblaze = blaze[order_num] / mp.nanmax(blaze[order_num])
        for it in range(1, len(llpos)):
            weight_bl[it] = nblaze[int(np.round(xxpos[it]))]
        # store the order numbers
        order_rec = llprops['ORDPEAK'][gg]
        # set up storage for line numbers
        mpeak = np.zeros_like(llpos)
        # line number for the last (reddest) line of the order (by FP equation)
        mpeak[-1] = int(dopd0 / llpos[-1])
        # calculate successive line numbers
        for it in range(len(llpos) - 2, -1, -1):
            # check for gap in x positions
            flocdiff = xxpos[it + 1] - xxpos[it]
            lowcond = xxpos_diff_med - (0.25 * xxpos_diff_med)
            highcond = xxpos_diff_med + (0.25 * xxpos_diff_med)
            if lowcond < flocdiff < highcond:
                # no gap: add 1 to line number of previous line
                mpeak[it] = mpeak[it + 1] + 1
            # if there is a gap, fix it
            #    Note we have to check if the gap has multiple jumps!
            else:
                # get line x positions
                flocx0 = xxpos[it]
                flocx1 = xxpos[it + 1]
                # get line wavelengths
                floc0 = llpos[it]
                floc1 = llpos[it + 1]
                # estimate the number of peaks missed
                m_offset = int(np.round((flocx1 - flocx0) / xxpos_diff_med))
                # add to m of previous peak
                mpeak[it] = mpeak[it + 1] + m_offset
                # verify there's no dopd jump, fix if present
                dopd_1 = (mpeak[it] * floc0 / 2 - dopd0 / 2)
                dopd_2 = (mpeak[it + 1] * floc1 / 2 - dopd0 / 2)
                # do loops to check jumps until it converges
                if dopd_1 - dopd_2 > fp_large_jump:
                    while (dopd_1 - dopd_2) > fp_large_jump:
                        mpeak[it] = mpeak[it] - 1
                        dopd_1 = (mpeak[it] * floc0 / 2 - dopd0 / 2)
                        dopd_2 = (mpeak[it + 1] * floc1 / 2 - dopd0 / 2)
                elif dopd_1 - dopd_2 < -fp_large_jump:
                    while (dopd_1 - dopd_2) < -fp_large_jump:
                        mpeak[it] = mpeak[it] + 1
                        dopd_1 = (mpeak[it] * floc0 / 2 - dopd0 / 2)
                        dopd_2 = (mpeak[it + 1] * floc1 / 2 - dopd0 / 2)
        # determination of observed effective cavity width
        dopd_t = mpeak * llpos / 2
        # store m and d
        m_fp = mpeak
        dopd_t = dopd_t
        # for orders other than the reddest, attempt to cross-match
        if order_num != n_ord_final_fp:
            # check for overlap
            if llpos[cm_ind] > ll_prev[0]:
                # find closest peak in overlap and get its m value
                ind = np.abs(ll_prev - llpos[cm_ind]).argmin()
                # the peak matching the reddest may not always be found!!
                # define maximum permitted difference
                llpos_diff_med = np.median(llpos[1:] - llpos[:-1])
                # print(llpos_diff_med)
                # print(abs(ll_prev[ind] - floc['llpos'][-1]))
                # check if the difference is over the limit
                if abs(ll_prev[ind] - llpos[-1]) > 1.5 * llpos_diff_med:
                    # print('overlap line not matched')
                    ll_diff = ll_prev[ind] - llpos[-1]
                    ind2 = -2
                    # loop over next reddest peak until they match
                    while ll_diff > 1.5 * llpos_diff_med:
                        # check there is still overlap
                        if llpos[ind2] > ll_prev[0]:
                            ind = np.abs(ll_prev - llpos[ind2]).argmin()
                            ll_diff = ll_prev[ind] - llpos[ind2]
                            ind2 -= 1
                        else:
                            break
                m_match = m_prev[ind]
                # save previous mpeak calculated
                m_init = mpeak[cm_ind]
                # recalculate m if there's an offset from cross_match
                m_offset_c = m_match - m_init
                if m_offset_c != 0:
                    mpeak = mpeak + m_offset_c
                    # print note for dev if different
                    wargs = [order_num, m_match - m_init]
                    WLOG(params, 'debug', TextEntry('90-017-00001', args=wargs))
                    # recalculate observed effective cavity width
                    dopd_t = mpeak * llpos / 2
                    # store new m and d
                    m_fp = mpeak
            else:
                # log that no overlap for order
                wargs = [order_num]
                WLOG(params, 'warning', TextEntry('10-017-00008', args=wargs))
                # save previous mpeak calculated
                m_init = mpeak[cm_ind]
                m_test = mpeak[cm_ind]
                # get dopd for last line of current & first of last order
                dopd_curr = (m_test * llpos[cm_ind] / 2 - dopd0 / 2)
                dopd_prev = (m_prev[0] * ll_prev[0] / 2 - dopd0 / 2)
                # do loops to check jumps
                if dopd_curr - dopd_prev > fp_large_jump:
                    while (dopd_curr - dopd_prev) > fp_large_jump:
                        m_test = m_test - 1
                        dopd_curr = (m_test * llpos[cm_ind] / 2 - dopd0 / 2)
                elif dopd_curr - dopd_prev < -fp_large_jump:
                    while (dopd_curr - dopd_prev) < -fp_large_jump:
                        m_test = m_test + 1
                        dopd_curr = (m_test * llpos[cm_ind] / 2 - dopd0 / 2)
                # recalculate m if there's an offset from cross_match
                m_offset_c = m_test - m_init
                if m_offset_c != 0:
                    mpeak = mpeak + m_offset_c
                    # print note for dev if different
                    # print note for dev if different
                    wargs = [order_num, mpeak[cm_ind] - m_init]
                    WLOG(params, 'debug', TextEntry('90-017-00001', args=wargs))
                    # recalculate observed effective cavity width
                    dopd_t = mpeak * llpos / 2
                    # store new m and d
                    m_fp = mpeak

        # add to storage
        llpos_all += list(llpos)
        xxpos_all += list(xxpos)
        ampl_all += list(ampl)
        m_fp_all += list(m_fp)
        weight_bl_all += list(weight_bl)
        order_rec_all += list(order_rec)
        # difference in cavity width
        dopd_all += list(dopd_t - dopd0 / 2)
        # save numpy arrays of current order to be previous in next loop
        ll_prev = np.array(llpos)
        m_prev = np.array(m_fp)
    # ----------------------------------------------------------------------
    # convert to numpy arrays
    llpos_all = np.array(llpos_all)
    xxpos_all = np.array(xxpos_all)
    ampl_all = np.array(ampl_all)
    m_fp_all = np.array(m_fp_all)
    weight_bl_all = np.array(weight_bl_all)
    order_rec_all = np.array(order_rec_all)
    dopd_all = np.array(dopd_all)
    # ----------------------------------------------------------------------
    # fit a polynomial to line number v measured difference in cavity
    #     width, weighted by blaze
    with warnings.catch_warnings(record=True) as w:
        coeffs = mp.nanpolyfit(m_fp_all, dopd_all, fit_deg,
                               w=weight_bl_all)[::-1]
    drs_log.warninglogger(params, w, funcname=func_name)
    # get the values of the fitted cavity width difference
    cfit = np.polyval(coeffs[::-1], m_fp_all)
    # update line wavelengths using the new cavity width fit
    newll = (dopd0 + 2 * cfit) / m_fp_all
    # ----------------------------------------------------------------------
    # insert fp lines into all_lines2 (at the correct positions)
    all_lines_2 = insert_fp_lines(params, newll, llpos_all, all_lines_2,
                                  order_rec_all, xxpos_all, ampl_all)
    # ----------------------------------------------------------------------
    # add to llprops
    llprops['FP_LL_POS'] = llpos_all
    llprops['FP_XX_POS'] = xxpos_all
    llprops['FP_M'] = m_fp_all
    llprops['FP_DOPD_OFFSET'] = dopd_all
    llprops['FP_AMPL'] = ampl_all
    llprops['FP_LL_POS_NEW'] = newll
    llprops['ALL_LINES_2'] = all_lines_2
    llprops['FP_DOPD_OFFSET_COEFF'] = coeffs
    llprops['FP_DOPD_OFFSET_FIT'] = cfit
    llprops['FP_ORD_REC'] = order_rec_all
    # set sources
    sources = ['FP_LL_POS', 'FP_XX_POS', 'FP_M', 'FP_DOPD_OFFSET',
               'FP_AMPL', 'FP_LL_POS_NEW', 'ALL_LINES_2',
               'FP_DOPD_OFFSET_COEFF', 'FP_DOPD_OFFSET_FIT', 'FP_ORD_REC']
    llprops.set_sources(sources, func_name)

    # return llprops
    return llprops


def find_fp_lines_new(params, llprops, fpe2dsfile, **kwargs):
    func_name = __NAME__ + '.find_fp_lines_new()'
    # get constants from params/kwargs
    border = pcheck(params, 'WAVE_FP_BORDER_SIZE', 'border', kwargs,
                    func_name)
    size = pcheck(params, 'WAVE_FP_FPBOX_SIZE', 'size', kwargs, func_name)
    siglimdict = pcheck(params, 'WAVE_FP_PEAK_SIG_LIM', 'siglimdict',
                        kwargs, func_name, mapf='dict', dtype=float)
    ipeakspace = pcheck(params, 'WAVE_FP_IPEAK_SPACING', 'ipeakspace',
                        kwargs, func_name)
    expwidth = pcheck(params, 'WAVE_FP_EXP_WIDTH', 'expwidth', kwargs,
                      func_name)
    cutwidth = pcheck(params, 'WAVE_FP_NORM_WIDTH_CUT', 'cutwidth',
                      kwargs, func_name)
    # get redefined variables (pipe inputs to llprops with correct names)
    # set fpfile as ref file
    llprops['SPEREF'] = fpe2dsfile.data
    # set wavelength solution as the one from the HC lines
    llprops['WAVE'] = llprops['LITTROW_EXTRAP_SOL_1']
    # set lamp as FP
    llprops['LAMP'] = 'fp'
    # use rv module to get the position of FP peaks from reference file
    #   first need to set all input parameters (via ckwargs)
    ckwargs = dict(border=border, size=size, siglimdict=siglimdict,
                   ipeakspace=ipeakspace)
    # measure the positions of the FP peaks
    llprops = velocity.measure_fp_peaks(params, llprops, **ckwargs)
    # use rv module to remove wide/spurious/doule-fitted peaks
    #   first need to set all input parameters (via ckwargs)
    ckwargs = dict(expwidth=expwidth, cutwidth=cutwidth,
                   peak_spacing=ipeakspace)
    # remove wide / double-fitted peaks
    llprops = velocity.remove_wide_peaks(params, llprops, **ckwargs)

    # add constants to llprops
    llprops['USED_BORDER'] = border
    llprops['USED_BOX_SIZE'] = size
    llprops['USED_SIGLIM'] = siglimdict[llprops['LAMP']]
    llprops['USED_LAMP'] = llprops['LAMP']
    llprops['USED_IPEAK_SPACE'] = ipeakspace
    llprops['USED_EXPWIDTH'] = expwidth
    llprops['USED_CUTWIDTH'] = cutwidth
    # set sources
    keys = ['USED_BORDER', 'USED_BOX_SIZE', 'USED_SIGLIM', 'USED_LAMP',
            'USED_IPEAK_SPACE', 'USED_EXPWIDTH', 'USED_CUTWIDTH']
    llprops.set_sources(keys, func_name)

    # return loc
    return llprops


# TODO: Melissa - needs to remove fp/hc start/final
def insert_fp_lines(params, newll, llpos_all, all_lines_2, order_rec_all,
                    xxpos_all, ampl_all, **kwargs):
    func_name = __NAME__ + '.insert_fp_lines()'
    # get constants from params/kwargs
    n_ord_start_fp = pcheck(params, 'WAVE_N_ORD_START', 'n_ord_start',
                            kwargs, func_name)
    n_ord_final_fp = pcheck(params, 'WAVE_N_ORD_FINAL', 'n_ord_final',
                            kwargs, func_name)
    n_ord_start_hc = pcheck(params, 'WAVE_N_ORD_START', 'n_ord_start',
                            kwargs, func_name)
    n_ord_final_hc = pcheck(params, 'WAVE_N_ORD_FINAL', 'n_ord_final',
                            kwargs, func_name)
    # ----------------------------------------------------------------------
    # insert FP lines into all_lines at the correct orders
    # ----------------------------------------------------------------------
    # define wavelength difference limit for keeping a line
    fp_cut = 3 * mp.nanstd(newll - llpos_all)
    # define correct starting order number
    start_order = min(n_ord_start_fp, n_ord_start_hc)
    # define starting point for prepended zeroes
    insert_count = 0
    for order_num in range(n_ord_start_fp, n_ord_final_fp):
        if order_num < n_ord_start_hc:
            # prepend zeros to all_lines if FP solution is fitted for
            #     bluer orders than HC was
            all_lines_2.insert(insert_count, np.zeros((1, 8), dtype=float))
            # add 1 to insertion counter for next order
            insert_count += 1
        elif order_num >= n_ord_final_hc:
            # append zeros to all_lines if FP solution is fitted for
            #     redder orders than HC was
            all_lines_2.append(np.zeros((1, 8), dtype=float))
        for it in range(len(order_rec_all)):
            # find lines corresponding to order number
            if order_rec_all[it] == order_num:
                # check wavelength difference below limit
                if abs(newll[it] - llpos_all[it]) < fp_cut:
                    # put FP line data into an array
                    # newdll = newll[it] - llpos_all[it]
                    fp_line = np.array([newll[it], 0.0, 0.0, 0.0,
                                        0.0, xxpos_all[it], 0.0, ampl_all[it]])
                    fp_line = fp_line.reshape((1, 8))
                    # append FP line data to all_lines
                    torder = order_num - start_order
                    tvalues = [all_lines_2[torder], fp_line]
                    all_lines_2[torder] = np.concatenate(tvalues)
    # return all lines 2
    return all_lines_2


def fit_1d_solution(params, llprops, wavell, start, end, fiber, errx_min,
                    fit_degree, max_ll_fit_rms, t_order_start, weight_thres,
                    iteration=0):
    func_name = __NAME__ + '.fit_1d_solution()'

    # get data from loc
    all_lines = llprops['ALL_LINES_{0}'.format(iteration)]
    # Get the number of orders
    num_orders = wavell.shape[0]
    # calculate echelle orders
    o_orders = np.arange(start, end)
    torder = t_order_start - o_orders

    # ------------------------------------------------------------------
    # fit 1d wavelength solution
    # ------------------------------------------------------------------
    # get maximum weight from errx_min
    max_weight = 1.0 / errx_min ** 2
    # -------------------------------------------------------------------------
    # set up all storage
    final_iter = []  # will fill [wmean, var, length]
    final_param = []  # will fill the fit coefficients
    final_details = []  # will fill [lines, x_fit, cfit, weight]
    final_dxdl = []  # will fill the derivative of the fit coefficients
    scale = []  # conversion factor to km/s
    # set up global stats
    sweight = 0.0
    wsumres = 0.0
    wsumres2 = 0.0
    # loop around orders
    for order_num in np.arange(num_orders):
        # ---------------------------------------------------------------------
        # get this orders parameters
        weights = all_lines[order_num][:, 7]
        diff_in_out = all_lines[order_num][:, 3]
        centers = all_lines[order_num][:, 0]
        pixelcenters = all_lines[order_num][:, 5]
        # ---------------------------------------------------------------------
        # only keep the lines that have postive weight
        goodlinemask = weights > weight_thres
        lines = centers[goodlinemask] + diff_in_out[goodlinemask]
        x_fit = pixelcenters[goodlinemask]
        # get the weights and modify by max_weight
        weight = (weights[goodlinemask] * max_weight)
        weight = weight / (weights[goodlinemask] + max_weight)
        # ---------------------------------------------------------------------
        # iteratively try to improve the fit
        improve = 1
        iter0, details = [], []
        wmean, var = 0, 0
        # sigma clip the largest rms until RMS < MAX_RMS
        while improve:
            # fit wavelength to pixel solution (with polynomial)
            ww = np.sqrt(weight)
            coeffs = mp.nanpolyfit(lines, x_fit, fit_degree, w=ww)[::-1]
            # calculate the fit
            cfit = np.polyval(coeffs[::-1], lines)
            # calculate the variance
            res = cfit - x_fit
            wsig = mp.nansum(res ** 2 * weight) / mp.nansum(weight)
            wmean = (mp.nansum(res * weight) / mp.nansum(weight))
            var = wsig - (wmean ** 2)
            # append stats
            iter0.append([np.array(wmean), np.array(var),
                          np.array(coeffs)])
            details.append([np.array(lines), np.array(x_fit),
                            np.array(cfit), np.array(weight)])
            # check improve condition (RMS > MAX_RMS)
            ll_fit_rms = abs(res) * np.sqrt(weight)
            badrms = ll_fit_rms > max_ll_fit_rms
            improve = mp.nansum(badrms)
            # set largest weighted residual to zero
            largest = mp.nanmax(ll_fit_rms)
            badpoints = ll_fit_rms == largest
            weight[badpoints] = 0.0
            # only keep the lines that have postive weight
            goodmask = weight > 0.0
            # check that we have points
            if mp.nansum(goodmask) == 0:
                eargs = [order_num, max_ll_fit_rms]
                WLOG(params, 'error', TextEntry('00-017-00007', args=eargs))
            else:
                lines = lines[goodmask]
                x_fit = x_fit[goodmask]
                weight = weight[goodmask]
        # ---------------------------------------------------------------------
        # log the fitted wave solution
        wargs = [torder[order_num], t_order_start - torder[order_num],
                 wavell[order_num][0], wavell[order_num][-1],
                 wmean * 1000, np.sqrt(var) * 1000, len(iter0),
                 len(details[0][1]), len(details[-1][1])]
        WLOG(params, '', TextEntry('40-017-00023', args=wargs))
        # ---------------------------------------------------------------------
        # append to all storage
        # ---------------------------------------------------------------------
        # append the last wmean, var and number of lines
        num_lines = len(details[-1][1])
        final_iter.append([iter0[-1][0], iter0[-1][1], num_lines])
        # append the last coefficients
        final_param.append(iter0[-1][2])
        # append the last details [lines, x_fit, cfit, weight]
        final_details.append(np.array(details[-1]))
        # append the derivative of the coefficients
        poly = np.poly1d(iter0[-1][2][::-1])
        dxdl = np.polyder(poly)(details[-1][0])
        final_dxdl.append(dxdl)
        # ---------------------------------------------------------------------
        # global statistics
        # ---------------------------------------------------------------------
        # work out conversion factor
        convert = speed_of_light / (dxdl * details[-1][0])
        # get res1
        res1 = details[-1][1] - details[-1][2]
        # sum the weights (recursively)
        sweight += mp.nansum(details[-1][3])
        # sum the weighted residuals in km/s
        wsumres += mp.nansum(res1 * convert * details[-1][3])
        # sum the weighted squared residuals in km/s
        wsumres2 += mp.nansum(details[-1][3] * (res1 * convert) ** 2)
        # store the conversion to km/s
        scale.append(convert)
    # convert to arrays
    final_iter = np.array(final_iter)
    final_param = np.array(final_param)
    # calculate the final var and mean
    final_mean = (wsumres / sweight)
    final_var = (wsumres2 / sweight) - (final_mean ** 2)
    # log the global stats
    total_lines = mp.nansum(final_iter[:, 2])
    wargs = [fiber, final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
             total_lines, 1000.0 * np.sqrt(final_var / total_lines)]
    WLOG(params, 'info', TextEntry('40-017-00024', args=wargs))
    # save outputs to loc
    llprops['X_MEAN_{0}'.format(iteration)] = final_mean
    llprops['X_VAR_{0}'.format(iteration)] = final_var
    llprops['X_ITER_{0}'.format(iteration)] = final_iter
    llprops['X_PARAM_{0}'.format(iteration)] = final_param
    llprops['X_DETAILS_{0}'.format(iteration)] = final_details
    llprops['SCALE_{0}'.format(iteration)] = scale
    # set sources
    keys = ['X_MEAN_{0}'.format(iteration), 'X_VAR_{0}'.format(iteration),
            'X_ITER_{0}'.format(iteration), 'X_PARAM_{0}'.format(iteration),
            'X_DETAILS_{0}'.format(iteration), 'SCALE_{0}'.format(iteration)]
    llprops.set_sources(keys, func_name)

    # ------------------------------------------------------------------
    # invert 1d wavelength solution
    # ------------------------------------------------------------------
    # get data from loc
    details = llprops['X_DETAILS_{0}'.format(iteration)]
    iter0 = llprops['X_ITER_{0}'.format(iteration)]
    # Get the number of orders
    num_orders = wavell.shape[0]
    # loop around orders
    inv_details = []
    inv_params = []
    sweight = 0.0
    wsumres = 0.0
    wsumres2 = 0.0
    # loop around orders
    for order_num in np.arange(num_orders):
        # get the lines and wavelength fit for this order
        lines = details[order_num][0]
        cfit = details[order_num][2]
        wei = details[order_num][3]
        # get the number of lines
        num_lines = len(lines)
        # set weights
        weight = np.ones(num_lines, dtype=float)
        # get fit coefficients
        coeffs = mp.nanpolyfit(cfit, lines, fit_degree, w=weight)[::-1]
        # get the y values for the coefficients
        icfit = np.polyval(coeffs[::-1], cfit)
        # work out the residuals
        res = icfit - lines
        # work out the normalised res in km/s
        nres = speed_of_light * (res / lines)
        # append values to storage
        inv_details.append([nres, wei])
        inv_params.append(coeffs)
        # ------------------------------------------------------------------
        # invert parameters
        # ------------------------------------------------------------------
        # sum the weights (recursively)
        sweight += mp.nansum(wei)
        # sum the weighted residuals in km/s
        wsumres += mp.nansum(nres * wei)
        # sum the weighted squared residuals in km/s
        wsumres2 += mp.nansum(wei * nres ** 2)
    # calculate the final var and mean
    final_mean = (wsumres / sweight)
    final_var = (wsumres2 / sweight) - (final_mean ** 2)
    # ------------------------------------------------------------------
    # log the inversion process
    total_lines = mp.nansum(iter0[:, 2])
    wargs = [final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
             1000.0 * np.sqrt(final_var / total_lines)]
    WLOG(params, '', TextEntry('40-017-00025', args=wargs))
    # ------------------------------------------------------------------
    # save outputs to loc
    llprops['LL_MEAN_{0}'.format(iteration)] = final_mean
    llprops['LL_VAR_{0}'.format(iteration)] = final_var
    llprops['LL_PARAM_{0}'.format(iteration)] = np.array(inv_params)
    llprops['LL_DETAILS_{0}'.format(iteration)] = inv_details
    # set the sources
    keys = ['LL_MEAN_{0}'.format(iteration), 'LL_VAR_{0}'.format(iteration),
            'LL_PARAM_{0}'.format(iteration),
            'LL_DETAILS_{0}'.format(iteration)]
    llprops.set_sources(keys, func_name)
    # ------------------------------------------------------------------
    # get the total number of orders to fit
    num_orders = len(llprops['ALL_LINES_{0}'.format(iteration)])
    # get the dimensions of the data
    ydim, xdim = llprops['NBO'], llprops['NBPIX']
    # get inv_params
    inv_params = llprops['LL_PARAM_{0}'.format(iteration)]
    # set pixel shift to zero, as doesn't apply here
    pixel_shift_inter = 0
    pixel_shift_slope = 0
    # get new line list
    ll_out = mp.get_ll_from_coefficients(pixel_shift_inter, pixel_shift_slope,
                                           inv_params, xdim, num_orders)
    # get the first derivative of the line list
    dll_out = mp.get_dll_from_coefficients(inv_params, xdim, num_orders)
    # find the central pixel value
    centpix = ll_out.shape[1] // 2
    # get the mean pixel scale (in km/s/pixel) of the central pixel
    norm = dll_out[:, centpix] / ll_out[:, centpix]
    meanpixscale = speed_of_light * mp.nansum(norm) / len(ll_out[:, centpix])
    # get the total number of lines used
    total_lines = int(mp.nansum(llprops['X_ITER_2'][:, 2]))
    # add to llprops
    llprops['LL_OUT_{0}'.format(iteration)] = ll_out
    llprops['DLL_OUT_{0}'.format(iteration)] = dll_out
    llprops['TOTAL_LINES_{0}'.format(iteration)] = total_lines
    # set sources
    keys = ['LL_OUT_{0}'.format(iteration), 'DLL_OUT_{0}'.format(iteration),
            'TOTAL_LINES_{0}'.format(iteration)]
    llprops.set_sources(keys, func_name)
    # log mean pixel scale at center
    wargs = [fiber, meanpixscale]
    WLOG(params, 'info', TextEntry('40-017-00026', args=wargs))
    # ------------------------------------------------------------------
    return llprops


def fit_1d_solution_sigclip(params, llprops, fiber, n_init, n_fin,
                            ll_fit_degree):
    """
    Fits the 1D solution between pixel position and wavelength
    Uses sigma-clipping and removes modulo 1 pixel errors

    :param params: parameter dictionary, ParamDict containing constants

    :param llprops: parameter dictionary, ParamDict containing data
        Must contain at least:
            FP_XX_NEW: FP pixel pisitions
            FP_LL_NEW: FP wavelengths
            FP_ORD_NEW: FP line orders
            FP_WEI: FP line weights

    :param fiber:
    :param n_init:
    :param n_fin:
    :param ll_fit_degree:

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                FP_ORD_CL = np array, FP line orders (sigma-clipped)
                FP_LLIN_CL = np array, FP wavelengths (sigma-clipped)
                FP_XIN_CL = np array, FP initial pixel values (sigma-clipped)
                FP_XOUT_CL = np array, FP corrected pixel values (sigma-clipped)
                FP_WEI_CL = np array, weights (sigma-clipped)
                RES_CL = np array, normalised residuals in km/s
                LL_OUT_2 = np array, output wavelength map
                LL_PARAM_2 = np array, polynomial coefficients
                X_MEAN_2 = final mean
                X_VAR_2 = final var
                TOTAL_LINES_2 = total lines
                SCALE_2 = scale

    """

    # set up storage arrays
    xpix = np.arange(llprops['NBPIX'])
    wave_map_final = np.zeros((n_fin - n_init, llprops['NBPIX']))
    poly_wave_sol_final = np.zeros((n_fin - n_init, ll_fit_degree + 1))
    fp_x_in_clip, fp_x_final_clip = [], []
    fp_ll_in_clip, fp_ll_final_clip, fp_ord_clip = [], [], []
    wsumres, sweight, wsumres2 = [], [], []
    wei_clip, res_clip, scale = [], [], []
    # fit x v wavelength w/sigma-clipping
    # we remove modulo 1 pixel errors in line centers - 3 iterations
    n_ite_mod_x = 3
    for ite in range(n_ite_mod_x):
        # set up storage
        wsumres = 0.0
        wsumres2 = 0.0
        sweight = 0.0
        fp_x_final_clip = []
        fp_x_in_clip = []
        fp_ll_final_clip = []
        fp_ll_in_clip = []
        fp_ord_clip = []
        res_clip = []
        wei_clip = []
        scale = []
        res_modx = np.zeros_like(llprops['FP_XX_NEW'])
        # loop over the orders
        for onum in range(n_fin - n_init):
            # order mask
            ord_mask = np.where(llprops['FP_ORD_NEW'] == onum +
                                n_init)
            # get FP line pixel positions for the order
            fp_x_ord = llprops['FP_XX_NEW'][ord_mask]
            # get new FP line wavelengths for the order
            fp_ll_new_ord = np.asarray(llprops['FP_LL_NEW'])[ord_mask]
            # get weights for the order
            wei_ord = np.asarray(llprops['FP_WEI'])[ord_mask]
            # fit solution for the order w/sigma-clipping
            coeffs, mask = sigclip_polyfit(params, fp_x_ord, fp_ll_new_ord,
                                           ll_fit_degree, wei_ord)
            # store the coefficients
            poly_wave_sol_final[onum] = coeffs[::-1]
            # get the residuals modulo x
            tmpmodx = (fp_ll_new_ord / np.polyval(coeffs, fp_x_ord)) - 1
            res_modx[ord_mask] = speed_of_light * tmpmodx
            # mask input arrays for statistics
            fp_x_ord = fp_x_ord[mask]
            fp_ll_new_ord = fp_ll_new_ord[mask]
            wei_ord = wei_ord[mask]
            # get final wavelengths
            fp_ll_final_ord = np.polyval(coeffs, fp_x_ord)
            # save wave map
            wave_map_final[onum] = np.polyval(coeffs, xpix)
            # save masked arrays
            fp_x_final_clip.append(fp_x_ord)
            fp_x_in_clip.append(llprops['FP_XX_INIT'][ord_mask][mask])
            fp_ll_final_clip.append(fp_ll_final_ord)
            fp_ll_in_clip.append(fp_ll_new_ord)
            fp_ord_clip.append(llprops['FP_ORD_NEW'][ord_mask][mask])
            wei_clip.append(wei_ord)
            # residuals in km/s
            # calculate the residuals for the final masked arrays
            res = fp_ll_final_ord - fp_ll_new_ord
            res_clip.append(res * speed_of_light / fp_ll_new_ord)
            # save stats
            # get the derivative of the coefficients
            poly = np.poly1d(coeffs)
            dldx = np.polyder(poly)(fp_x_ord)
            # work out conversion factor
            convert = speed_of_light * dldx / fp_ll_final_ord
            scale.append(convert)
            # sum the weights (recursively)
            sweight += mp.nansum(wei_clip[onum])
            # sum the weighted residuals in km/s
            wsumres += mp.nansum(res_clip[onum] * wei_clip[onum])
            # sum the weighted squared residuals in km/s
            wsumres2 += mp.nansum(wei_clip[onum] * res_clip[onum] ** 2)
        # we construct a sin/cos model of the error in line center position
        # and fit it to the residuals
        cosval = np.cos(2 * np.pi * (llprops['FP_XX_NEW'] % 1))
        sinval = np.sin(2 * np.pi * (llprops['FP_XX_NEW'] % 1))

        # find points that are not residual outliers
        # We fit a zeroth order polynomial, so it returns
        # outliers to the mean value.
        outl_fit, mask_all = sigclip_polyfit(params, llprops['FP_XX_NEW'],
                                             res_modx, 0)
        # create model
        sumcos1 = mp.nansum(cosval[mask_all] * res_modx[mask_all])
        sumcos2 = mp.nansum(cosval[mask_all] ** 2)
        acos = sumcos1 / sumcos2
        sumsin1 = mp.nansum(sinval[mask_all] * res_modx[mask_all])
        sumsin2 = mp.nansum(sinval[mask_all] ** 2)

        asin = sumsin1 / sumsin2
        model_sin = ((cosval * acos) + (sinval * asin))
        # update the xpeak positions with model
        llprops['FP_XX_NEW'] += model_sin / 2.2
    # calculate the final var and mean
    total_lines = len(np.concatenate(fp_ll_in_clip))
    final_mean = wsumres / sweight
    final_var = (wsumres2 / sweight) - (final_mean ** 2)
    # log the global stats
    wargs = [fiber, final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
             total_lines, 1000.0 * np.sqrt(final_var / total_lines)]
    WLOG(params, 'info', TextEntry('40-017-00024', args=wargs))
    # save final (sig-clipped) arrays to loc
    llprops['FP_ORD_CL'] = np.array(np.concatenate(fp_ord_clip).ravel())
    llprops['FP_LLIN_CL'] = np.array(np.concatenate(fp_ll_in_clip).ravel())
    llprops['FP_XIN_CL'] = np.array(np.concatenate(fp_x_in_clip).ravel())
    llprops['FP_XOUT_CL'] = np.array(np.concatenate(fp_x_final_clip).ravel())
    llprops['FP_WEI_CL'] = np.array(np.concatenate(wei_clip).ravel())
    llprops['RES_CL'] = np.array(np.concatenate(res_clip).ravel())
    llprops['LL_OUT_2'] = wave_map_final
    llprops['LL_PARAM_2'] = poly_wave_sol_final
    llprops['X_MEAN_2'] = final_mean
    llprops['X_VAR_2'] = final_var
    llprops['TOTAL_LINES_2'] = total_lines
    llprops['SCALE_2'] = scale
    # set up x_details and ll_details structures for line list table:
    # X_DETAILS_i: list, [lines, xfit, cfit, weight] where
    #   lines= original wavelength-centers used for the fit
    #   xfit= original pixel-centers used for the fit
    #   cfit= fitted pixel-centers using fit coefficients
    #   weight=the line weights used
    # LL_DETAILS_i: numpy array (1D), the [nres, wei] where
    #   nres = normalised residuals in km/s
    #   wei = the line weights
    x_details = []
    ll_details = []
    for ord_num in range(n_init, n_fin):
        omask = llprops['FP_ORD_CL'] == ord_num
        x_details.append([llprops['FP_LLIN_CL'][omask],
                          llprops['FP_XIN_CL'][omask],
                          llprops['FP_XOUT_CL'][omask],
                          llprops['FP_WEI_CL'][omask]])
        ll_details.append([llprops['RES_CL'][omask],
                           llprops['FP_WEI_CL'][omask]])
    llprops['X_DETAILS_2'] = x_details
    llprops['LL_DETAILS_2'] = ll_details
    # return llprops
    return llprops


def no_overlap_match_calc(params, ord_num, fp_ll_ord, fp_ll_ord_prev,
                          m_ord_prev, dif_n, **kwargs):
    """
    Calculate the absolute FP peak numbers when there is no overlap from one
    order to the next by estimating the number of peaks missed

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            WAVE_FP_LLDIF_MIN: float, defines the minimum fraction of the median
                        wavelength difference we accept as no gap between lines
            WAVE_FP_LLDIF_MIN: float, defines the maximum fraction of the median
                        wavelength difference we accept as no gap between lines

    :param ord_num: the order number
    :param fp_ll_ord: the FP peak wavelengths for the current order
    :param fp_ll_ord_prev: the FP peak wavelengths for the previous order
    :param fp_ll_diff: wavelength difference between consecutive FP peaks
                       (current order)
    :param fp_ll_diff_prev: wavelength difference between consecutive FP peaks
                       (previous order)
    :param m_ord_prev: absolute peak numbers of previous order
    :param dif_n: differential peak numbering for all orders

    :return m_ord: absolute peak numbers for current order

    """
    func_name = __NAME__ + '.no_overlap_match_calc()'
    # get constants from params/kwargs
    lldif_min = pcheck(params, 'WAVE_FP_LLDIF_MIN', 'lldif_max', kwargs,
                       func_name)
    lldif_max = pcheck(params, 'WAVE_FP_LLDIF_MAX', 'lldif_min', kwargs,
                       func_name)

    ll_diff = fp_ll_ord[1:] - fp_ll_ord[:-1]
    ll_diff_prev = fp_ll_ord_prev[1:] - fp_ll_ord_prev[:-1]

    # print warning re no overlap
    WLOG(params, 'warning', TextEntry('10-017-00009', args=[ord_num]))
    # masks to keep only difference between no-gap lines for current order
    mask_ll_diff = ll_diff > (lldif_min * mp.nanmedian(ll_diff))
    mask_ll_diff &= ll_diff < (lldif_max * mp.nanmedian(ll_diff))
    # get previous min/max limits
    prevminlim = lldif_min * mp.nanmedian(ll_diff_prev)
    prevmaxlim = lldif_max * mp.nanmedian(ll_diff_prev)
    # masks to keep only difference between no-gap lines for previous order
    mask_ll_diff_prev = ll_diff_prev > prevminlim
    mask_ll_diff_prev &= ll_diff_prev < prevmaxlim
    # get last diff for current order, first for prev
    ll_diff_fin = ll_diff[mask_ll_diff][-1]
    ll_diff_init = ll_diff_prev[mask_ll_diff_prev][0]
    # calculate wavelength difference between end lines
    ll_miss = fp_ll_ord_prev[0] - fp_ll_ord[-1]
    # estimate lines missed using ll_diff from each order
    m_end_1 = int(np.round(ll_miss / ll_diff_fin))
    m_end_2 = int(np.round(ll_miss / ll_diff_init))
    # check they are the same, print warning if not
    if not m_end_1 == m_end_2:
        # log that we are missing line estimate miss-match
        wargs = [m_end_1, m_end_2, ll_diff_fin, ll_diff_init]
        WLOG(params, 'warning', TextEntry('10-017-00010', args=wargs))
    # calculate m_end, absolute peak number for last line of the order
    m_end = int(m_ord_prev[0]) + m_end_1
    # define array of absolute peak numbers for the order
    m_ord = m_end + dif_n[ord_num][-1] - dif_n[ord_num]
    # return m_ord
    return m_ord


def sigclip_polyfit(params, xx, yy, degree, weight=None, **kwargs):
    """
    Fit a polynomial with sigma-clipping of outliers

    :param params: parameter dictionary, ParamDict containing constants
    :param xx: numpy array, x values to fit
    :param yy: numpy array, y values to fit
    :param degree: int, the degree of fit
    :param weight: optional, numpy array, weights to the fit

    :return coeff: the fit coefficients
    :return mask: the sigma-clip mask

    """
    func_name = __NAME__ + '.sigclip_polyfit()'
    # read constants from p
    sigclip = pcheck(params, 'WAVE_FP_SIGCLIP', 'sigclip', kwargs, func_name)
    # initialise the while loop
    sigmax = sigclip + 1
    # initialise mask
    mask = np.ones_like(xx, dtype='Bool')
    # set up coeffs
    coeff = np.zeros(degree)
    # while we are above sigclip
    while sigmax > sigclip:
        # Need to mask weight here if not None
        if weight is not None:
            weight2 = weight[mask]
        else:
            weight2 = None
        # fit on masked values
        coeff = mp.nanpolyfit(xx[mask], yy[mask], deg=degree, w=weight2)
        # get residuals (not masked or dimension breaks)
        res = yy - np.polyval(coeff, xx)
        # normalise the residuals
        res = np.abs(res / mp.nanmedian(np.abs(res[mask])))
        # get the max residual in sigmas
        sigmax = mp.nanmax(res[mask])
        # mask all outliers
        if sigmax > sigclip:
            mask[res >= sigclip] = False
    # return the coefficients and mask
    return coeff, mask


def find_num_fppeak_diff(llprops, blaze, n_init, n_fin, wave_blaze_thres,
                         xdiff_min, xdiff_max):
    """

    :param llprops:
    :param blaze:
    :param n_init:
    :param n_fin:
    :param wave_blaze_thres:
    :param xdiff_min:
    :param xdiff_max:
    :return:
    """
    # set up storage
    # FP peak wavelengths
    fp_ll = []
    # FP peak orders
    fp_order = []
    # FP peak pixel centers
    fp_xx = []
    # FP peak differential numbering
    dif_n = []
    # FP peak amplitudes
    fp_amp = []
    # loop over orders
    for order_num in range(n_init, n_fin):
        # ------------------------------------------------------------------
        # Number FP peaks differentially and identify gaps
        # ------------------------------------------------------------------
        # get mask of FP lines for order
        mask_fp = llprops['ORDPEAK'] == order_num
        # get x values of FP lines
        x_fp = llprops['XPEAK'][mask_fp]
        # get amplitudes of FP lines (to save)
        amp_fp = llprops['AMPPEAK'][mask_fp]
        # get the coeff for this order
        poly_wave_coeffs = llprops['POLY_WAVE_SOL'][order_num]
        # get 30% blaze mask
        with warnings.catch_warnings(record=True) as _:
            maxblaze = mp.nanmax(blaze[order_num])
            maskblaze = np.where(blaze[order_num] > wave_blaze_thres * maxblaze)
        # keep only x values at above 30% blaze
        bmask = (mp.nanmax(maskblaze) > x_fp) & (mp.nanmin(maskblaze) < x_fp)
        amp_fp = amp_fp[bmask]
        x_fp = x_fp[bmask]
        # initial differential numbering (assuming no gaps)
        peak_num_init = np.arange(len(x_fp))
        # find gaps in x
        # get array of x differences
        x_diff = x_fp[1:] - x_fp[:-1]
        # get median of x difference
        med_x_diff = mp.nanmedian(x_diff)
        # get indices where x_diff differs too much from median
        cond1 = x_diff < xdiff_min * med_x_diff
        cond2 = x_diff > xdiff_max * med_x_diff
        x_gap_ind = np.where(cond1 | cond2)[0]
        # get the opposite mask (no-gap points)
        cond3 = x_diff > xdiff_min * med_x_diff
        cond4 = x_diff < xdiff_max * med_x_diff
        x_good_ind = np.where(cond3 & cond4)[0]
        # fit x_fp v x_diff for good points
        good_xfp = x_fp[1:][x_good_ind]
        good_xdiff = x_diff[x_good_ind]
        cfit_xdiff = mp.nanpolyfit(good_xfp, good_xdiff, 2)
        # loop over gap points
        for it in range(len(x_gap_ind)):
            # get estimated xdiff value from the fit
            x_diff_aux = np.polyval(cfit_xdiff, x_fp[1:][x_gap_ind[it]])
            # estimate missed peaks
            x_jump = np.round((x_diff[x_gap_ind[it]] / x_diff_aux)) - 1
            # add the jump
            peak_num_init[x_gap_ind[it] + 1:] += int(x_jump)
        # Calculate original (HC sol) FP wavelengths
        fp_ll.append(np.polyval(poly_wave_coeffs[::-1], x_fp))
        # save differential numbering
        dif_n.append(peak_num_init)
        # save order number
        fp_order.append(np.ones(len(x_fp)) * order_num)
        # save x positions
        fp_xx.append(x_fp)
        # save amplitudes
        fp_amp.append(amp_fp)
    # return to main
    return fp_ll, dif_n, fp_order, fp_xx, fp_amp


def assign_abs_fp_numbers(params, fp_ll, dif_n, m_vec, m_ord_prev, n_init,
                          n_fin, ll_offset):
    """

    :param params:
    :param fp_ll:
    :param dif_n:
    :param m_vec:
    :param m_ord_prev:
    :param n_init:
    :param n_fin:
    :param ll_offset:
    :return:
    """
    # set up m_ord
    m_ord = np.nan
    # loop over orders from reddest-1 to bluest
    for ord_num in range(n_fin - n_init - 2, -1, -1):
        # define auxiliary arrays with ll for order and previous order
        fp_ll_ord = fp_ll[ord_num]
        fp_ll_ord_prev = fp_ll[ord_num + 1]
        # define median ll diff for both orders
        fp_ll_diff_med = mp.nanmedian(fp_ll_ord[1:] - fp_ll_ord[:-1])
        fp_ll_diff_prev_med = mp.nanmedian(fp_ll_ord_prev[1:] -
                                           fp_ll_ord_prev[:-1])
        # check if overlap
        if fp_ll_ord[-1] >= fp_ll_ord_prev[0]:
            # get overlapping peaks for both
            # allow WAVE_FP_LL_OFFSET*lldiff offsets
            ord_over_lim = fp_ll_ord_prev[0] - (ll_offset * fp_ll_diff_prev_med)
            prev_ord_lim = fp_ll_ord[-1] + (ll_offset * fp_ll_diff_med)
            mask_ord_over = fp_ll_ord >= ord_over_lim
            fp_ll_ord_over = fp_ll_ord[mask_ord_over]
            mask_prev_over = fp_ll_ord_prev <= prev_ord_lim
            fp_ll_prev_over = fp_ll_ord_prev[mask_prev_over]
            # loop over peaks to find closest match
            mindiff_peak = []
            mindiff_peak_ind = []
            for j in range(len(fp_ll_ord_over)):
                # get differences for peak j
                diff = np.abs(fp_ll_prev_over - fp_ll_ord_over[j])
                # save the minimum and its index
                mindiff_peak.append(mp.nanmin(diff))
                mindiff_peak_ind.append(np.argmin(diff))
            # get the smallest difference and its index
            mindiff_all = mp.nanmin(mindiff_peak)
            mindiff_all_ind = int(np.argmin(mindiff_peak))

            # check that smallest difference is in fact a true line match
            if mindiff_all < (ll_offset * fp_ll_diff_med):
                # set the match m index as the one for the smallest diff
                m_match_ind = mindiff_peak_ind[mindiff_all_ind]
                # get line number for peak with smallest difference
                m_end = m_ord_prev[mask_prev_over][m_match_ind]
                # get differential peak number for peak with smallest diff
                dif_n_match = dif_n[ord_num][mask_ord_over][mindiff_all_ind]
                # define array of absolute peak numbers for the order
                m_ord = m_end + dif_n_match - dif_n[ord_num]
            # if not treat as no overlap
            else:
                m_ord = no_overlap_match_calc(params, ord_num, fp_ll_ord,
                                              fp_ll_ord_prev, m_ord_prev, dif_n)
        # if no overlap
        else:
            m_ord = no_overlap_match_calc(params, ord_num, fp_ll_ord,
                                          fp_ll_ord_prev, m_ord_prev, dif_n)
        # insert absolute order numbers at the start of m
        m_vec = np.concatenate((m_ord, m_vec))
        # redefine order number vector for previous order
        m_ord_prev = m_ord

    return m_vec


def get_d_for_each_hcline(params, recipe, llprops, fp_order, fp_xx, m_vec,
                          blaze, n_init, n_fin, wave_blaze_thres, dv_max,
                          ll_fit_degree):
    func_name = __NAME__ + '.get_d_for_each_hcline()'
    # set up storage
    # m(x) fit coefficients
    coeff_xm_all = []
    # m(x) fit dispersion
    xm_disp = []
    # effective cavity width for the HC lines
    d_arr = []
    # 1/line number of the closest FP line to each HC line
    one_m_d = []
    # line number of the closest FP line to each HC line
    m_d = []
    # wavelength of HC lines
    hc_ll_test = []
    # pixel value of kept HC lines
    hc_xx_test = []
    # order of kept hc lines
    hc_ord_test = []
    # save mask for m(x) fits
    xm_mask = []
    # loop over orders
    for order_num in range(n_fin - n_init):
        # create order mask
        fp_order_rav = np.concatenate(fp_order).ravel()
        ind_ord = np.where(fp_order_rav == order_num + n_init)
        # get FP line pixel positions for the order
        fp_x_ord = fp_xx[order_num]
        # get FP line numbers for the order
        m_ord = m_vec[ind_ord]
        # HC mask for the order - keep best lines (small dv) only
        cond1 = abs(llprops['DV_T']) < dv_max
        cond2 = llprops['ORD_T'] == order_num + n_init
        hc_mask = np.where(cond1 & cond2)
        # get HC line pixel positions for the order
        hc_x_ord = llprops['XGAU_T'][hc_mask]
        # get 30% blaze mask
        with warnings.catch_warnings(record=True) as _:
            maxblaze = mp.nanmax(blaze[order_num])
            mb = np.where(blaze[order_num] > (wave_blaze_thres * maxblaze))
        # keep only x values at above 30% blaze
        blaze_mask = np.logical_and(mp.nanmax(mb) > hc_x_ord,
                                    mp.nanmin(mb) < hc_x_ord)
        hc_x_ord = hc_x_ord[blaze_mask]
        # get corresponding catalogue lines from loc
        hc_ll_ord_cat = llprops['WAVE_CATALOG'][hc_mask][blaze_mask]

        # fit x vs m for FP lines w/sigma-clipping
        coeff_xm, mask = sigclip_polyfit(params, fp_x_ord, m_ord, ll_fit_degree)
        # save coefficients
        coeff_xm_all.append(coeff_xm)
        # save dispersion
        polyval_xm = np.polyval(coeff_xm, fp_x_ord[mask])
        xm_disp.append(mp.nanstd(m_ord[mask] - polyval_xm))
        # save mask
        xm_mask.append(mask)
        # get fractional m for HC lines from fit
        m_hc = np.polyval(coeff_xm, hc_x_ord)
        # get cavity width for HC lines from FP equation
        d_hc = m_hc * hc_ll_ord_cat / 2.
        # save in arrays:
        # cavity width for hc lines
        d_arr.append(d_hc)
        # 1/m for HC lines
        one_m_d.append(1 / m_hc)
        # m for HC lines
        m_d.append(m_hc)
        # catalogue wavelengths
        hc_ll_test.append(hc_ll_ord_cat)
        # HC line centers (pixel position)
        hc_xx_test.append(hc_x_ord)
        # HC line orders
        hc_ord_test.append((order_num + n_init) * np.ones_like(hc_x_ord))

    # residuals plot
    recipe.plot('WAVE_FP_M_X_RES', fp_order=fp_order, fp_xx=fp_xx, m_vec=m_vec,
                xm_mask=xm_mask, coeff_xm_all=coeff_xm_all, n_init=n_init,
                n_fin=n_fin)

    # flatten arrays
    one_m_d = np.concatenate(one_m_d).ravel()
    d_arr = np.concatenate(d_arr).ravel()
    m_d = np.concatenate(m_d).ravel()
    hc_ll_test = np.concatenate(hc_ll_test).ravel()
    hc_ord_test = np.concatenate(hc_ord_test).ravel()

    # log absolute peak number span
    wargs = [round(m_d[0]), round(m_d[-1])]
    WLOG(params, '', TextEntry('40-017-00027', args=wargs))

    return one_m_d, d_arr, hc_ll_test, hc_ord_test


def fit_1m_vs_d(params, recipe, one_m_d, d_arr, hc_ll_test, update_cavity,
                m_init, fp_ll, fiber, **kwargs):
    # set function name
    func_name = __NAME__ + '.fit_1m_vs_d()'
    # get params from params
    dopd0 = pcheck(params, 'WAVE_FP_DOPD0', 'dopd0', kwargs, func_name)

    # load current cavity files
    fit_1m_d, fit_ll_d = drs_data.load_cavity_files(params, required=False)
    # check for exists (will be None if either file doesn't exist)
    if fit_1m_d is None:
        # log that we are going to update cavity files as files do not exist
        WLOG(params, 'warning', TextEntry('10-017-00011'))
        # set update_cavity to True
        update_cavity = True

    # if we need to update_cavity file then work it out
    if update_cavity:
        # define sorted arrays
        one_m_sort = np.argsort(one_m_d)
        one_m_d = np.array(one_m_d)[one_m_sort]
        d_arr = np.array(d_arr)[one_m_sort]
        # polynomial fit for d vs 1/m
        fit_1m_d = mp.nanpolyfit(one_m_d, d_arr, 9)
        fit_1m_d_func = np.poly1d(fit_1m_d)
        res_d_final = d_arr - np.polyval(fit_1m_d, one_m_d)
        # fit d v wavelength w/sigma-clipping
        fit_ll_d, mask = sigclip_polyfit(params, hc_ll_test, d_arr, degree=9)
        # plot d vs 1/m fit and residuals
        if __name__ == '__main__':
            recipe.plot('WAVE_FP_IPT_CWID_1MHC', one_m_d=one_m_d, d_arr=d_arr,
                        m_init=m_init, fit_1m_d_func=fit_1m_d_func,
                        res_d_final=res_d_final, dopd0=dopd0)

        # save the parameters
        drs_data.save_cavity_files(params, fit_1m_d, fit_ll_d)
    # else we need to shift values
    else:
        # get achromatic cavity change - ie shift
        residual = d_arr - np.polyval(fit_ll_d, hc_ll_test)
        # update the coeffs with mean shift
        fit_ll_d[-1] += mp.nanmedian(residual)

    # calculate the fit value
    fitval = np.polyval(fit_ll_d, hc_ll_test)
    # plot the interp cavity width ll hc and fp plot
    # TODO: original d needs fixing I think
    recipe.plot('WAVE_FP_IPT_CWID_LLHC', hc_ll=hc_ll_test, fp_ll=fp_ll,
                d_arr=d_arr, fitval=fitval, dopd0=dopd0, fiber=fiber)
    # summary plot interp cavity width ll hc and fp plot
    recipe.plot('SUM_WAVE_FP_IPT_CWID_LLHC', hc_ll=hc_ll_test, fp_ll=fp_ll,
                d_arr=d_arr, fitval=fitval, dopd0=dopd0, fiber=fiber)
    # return variables
    return fit_1m_d, fit_ll_d, one_m_d, d_arr


def update_fp_peak_wavelengths(params, recipe, llprops, fit_ll_d, m_vec,
                               fp_order, fp_xx, fp_amp, fp_cavfit_mode,
                               n_init, n_fin):
    func_name = __NAME__ + '.update_fp_peak_wavelengths()'
    # define storage
    fp_ll_new = []
    # deal with different ways to calculate cavity fit
    if fp_cavfit_mode == 0:
        # derive using 1/m vs d fit
        # loop over peak numbers
        for i in range(len(m_vec)):
            # calculate wavelength from fit to 1/m vs d
            fp_ll_new.append(2 * np.polyval(fit_ll_d, 1. / m_vec[i]) / m_vec[i])
    elif fp_cavfit_mode == 1:
        # from the d v wavelength fit - iterative fit
        # TODO: Melissa - Why 1600 - should this be a constant?
        # TODO: ---> Ask Etienne
        fp_ll_new = np.ones_like(m_vec) * 1600.
        for ite in range(6):
            recon_d = np.polyval(fit_ll_d, fp_ll_new)
            fp_ll_new = recon_d / m_vec * 2

    # save to loc (flattened)
    llprops['FP_LL_NEW'] = np.array(fp_ll_new)
    llprops['FP_XX_NEW'] = np.array(np.concatenate(fp_xx).ravel())
    llprops['FP_ORD_NEW'] = np.array(np.concatenate(fp_order).ravel())
    llprops['FP_AMP_NEW'] = np.array(np.concatenate(fp_amp).ravel())
    # duplicate for saving
    llprops['FP_XX_INIT'] = np.array(np.concatenate(fp_xx).ravel())
    # set sources
    keys = ['FP_LL_NEW', 'FP_XX_NEW', 'FP_ORD_NEW', 'FP_AMP_NEW',
            'FP_XX_INIT']
    llprops.set_sources(keys, func_name)
    # plot old-new wavelength difference
    recipe.plot('WAVE_FP_LL_DIFF', llprops=llprops, n_init=n_init, n_fin=n_fin)
    # return ll props
    return llprops


def fit_wavesol_from_fppeaks(params, llprops, fp_ll, fiber, n_init, n_fin,
                             fp_llfit_mode, ll_fit_degree, errx_min,
                             max_ll_fit_rms, t_order_start, weight_thres):
    func_name = __NAME__ + '.fit_wavesol_from_fppeaks()'

    fp_ll_new = llprops['FP_LL_NEW']
    # deal with ll fit mode 0
    if fp_llfit_mode == 0:
        # call fit_1d_solution
        # set up ALL_LINES_2 with FP lines
        fp_ll_ini = np.concatenate(fp_ll).ravel()

        iargs = [llprops['FP_LL_NEW'], fp_ll_ini, llprops['ALL_LINES_2'],
                 llprops['FP_ORD_NEW'], llprops['FP_XX_NEW'],
                 llprops['FP_AMP_NEW']]

        llprops['ALL_LINES_2'] = insert_fp_lines(params, *iargs)
        # select the orders to fit
        wavells = llprops['LITTROW_EXTRAP_SOL_1'][n_init:n_fin]
        # fit the solution
        llprops = fit_1d_solution(params, llprops, wavells, n_init, n_fin,
                                  fiber, errx_min, ll_fit_degree,
                                  max_ll_fit_rms, t_order_start, weight_thres,
                                  iteration=2)

    # else deal with ll fit mode 1
    elif fp_llfit_mode == 1:
        # call fit_1d_solution_sigclip
        # weights - dummy array
        llprops['FP_WEI'] = np.ones_like(fp_ll_new)
        # fit the solution
        llprops = fit_1d_solution_sigclip(params, llprops, fiber, n_init, n_fin,
                                          ll_fit_degree)
    # else break
    else:
        eargs = [fp_llfit_mode, func_name]
        WLOG(params, 'error', TextEntry('09-017-00004', args=eargs))

    return llprops


def join_orders(llprops, start, end):
    """
    Merge the littrow extrapolated solutions with the fitted line solutions

    :param llprops: parameter dictionary, ParamDict containing data
        Must contain at least:
            LL_OUT_2: numpy array (2D), the output wavelengths for each
                      pixel and each order (in the shape of original image)
            DLL_OUT_2: numpy array (2D), the output delta wavelengths for
                       each pixel and each order (in the shape of original
                       image)
            LITTROW_EXTRAP_SOL_2: numpy array (2D),
                              size=([no. orders] by [no. cut points])
                              the wavelength solution at each cut point for
                              each order
            LITTROW_EXTRAP_PARAM_2: numy array (2D),
                              size=([no. orders] by [the fit degree +1])
                              the coefficients of the fits for each cut
                              point for each order

    :param start:
    :param end:

    :return loc: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            LL_FINAL: numpy array, the joined littrow extrapolated and fitted
                      solution wavelengths
            LL_PARAM_FINAL: numpy array, the joined littrow extrapolated and
                            fitted fit coefficients

    """

    func_name = __NAME__ + '.join_orders()'
    # get data from loc
    # the second iteration outputs
    ll_out_2 = llprops['LL_OUT_2']
    param_out_2 = llprops['LL_PARAM_2']

    # the littrow extrapolation (for orders < n_ord_start_2)
    litt_extrap_sol_blue = llprops['LITTROW_EXTRAP_SOL_2'][:start]
    litt_extrap_sol_param_blue = llprops['LITTROW_EXTRAP_PARAM_2'][:start]

    # the littrow extrapolation (for orders > n_ord_final_2)
    litt_extrap_sol_red = llprops['LITTROW_EXTRAP_SOL_2'][end:]
    litt_extrap_sol_param_red = llprops['LITTROW_EXTRAP_PARAM_2'][end:]

    # create stack
    ll_stack, param_stack = [], []
    # add extrapolation from littrow to orders < n_ord_start_2
    if len(litt_extrap_sol_blue) > 0:
        ll_stack.append(litt_extrap_sol_blue)
        param_stack.append(litt_extrap_sol_param_blue)
    # add second iteration outputs
    if len(ll_out_2) > 0:
        ll_stack.append(ll_out_2)
        param_stack.append(param_out_2)
    # add extrapolation from littrow to orders > n_ord_final_2
    if len(litt_extrap_sol_red) > 0:
        ll_stack.append(litt_extrap_sol_red)
        param_stack.append(litt_extrap_sol_param_red)

    # convert stacks to arrays and add to storage
    llprops['LL_FINAL'] = np.vstack(ll_stack)
    llprops['LL_PARAM_FINAL'] = np.vstack(param_stack)
    llprops.set_sources(['LL_FINAL', 'LL_PARAM_FINAL'], func_name)

    # return loc
    return llprops


# =============================================================================
# Define fp aux functions
# =============================================================================
def fp_quality_control(params, fpprops, qc_params, **kwargs):

    func_name = __NAME__ + '.fp_quality_control()'
    # get parameters from params/kwargs
    rms_littrow_max = pcheck(params, 'WAVE_LITTROW_QC_RMS_MAX',
                             'rms_littrow_max', kwargs, func_name)
    dev_littrow_max = pcheck(params, 'WAVE_LITTROW_QC_DEV_MAX',
                             'dev_littrow_max', kwargs, func_name)
    # --------------------------------------------------------------
    # set passed variable and fail message list
    fail_msg = []
    qc_names, qc_values, qc_logic, qc_pass = qc_params
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # --------------------------------------------------------------
    # check the difference between consecutive orders is always positive
    # get the differences
    wave_diff = fpprops['LL_FINAL'][1:] - fpprops['LL_FINAL'][:-1]
    if mp.nanmin(wave_diff) < 0:
        fail_msg.append(textdict['40-017-00030'])
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mp.nanmin(wave_diff))
    qc_names.append('MIN WAVE DIFF FP-HC')
    qc_logic.append('MIN WAVE DIFF < 0')
    # ----------------------------------------------------------------------
    # check for infinites and NaNs in mean residuals from fit
    if ~np.isfinite(fpprops['X_MEAN_2']):
        # add failed message to the fail message list
        fail_msg.append(textdict['40-017-00031'])
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(fpprops['X_MEAN_2'])
    qc_names.append('X_MEAN_2')
    qc_logic.append('X_MEAN_2 not finite')
    # ----------------------------------------------------------------------
    # iterate through Littrow test cut values
    lit_it = 2
    # checks every other value
    for x_it in range(1, len(fpprops['X_CUT_POINTS_' + str(lit_it)]), 2):
        # get x cut point
        x_cut_point = fpprops['X_CUT_POINTS_' + str(lit_it)][x_it]
        # get the sigma for this cut point
        sig_littrow = fpprops['LITTROW_SIG_' + str(lit_it)][x_it]
        # get the abs min and max dev littrow values
        min_littrow = abs(fpprops['LITTROW_MINDEV_' + str(lit_it)][x_it])
        max_littrow = abs(fpprops['LITTROW_MAXDEV_' + str(lit_it)][x_it])
        # get the corresponding order
        min_littrow_ord = fpprops['LITTROW_MINDEVORD_' + str(lit_it)][x_it]
        max_littrow_ord = fpprops['LITTROW_MAXDEVORD_' + str(lit_it)][x_it]
        # check if sig littrow is above maximum
        if sig_littrow > rms_littrow_max:
            fargs = [x_cut_point, sig_littrow, rms_littrow_max]
            fail_msg.append(textdict['40-017-00032'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(sig_littrow)
        qc_names.append('sig_littrow')
        qc_logic.append('sig_littrow > {0:.2f}'.format(rms_littrow_max))
        # ----------------------------------------------------------------------
        # check if min/max littrow is out of bounds
        if mp.nanmax([max_littrow, min_littrow]) > dev_littrow_max:
            fargs = [x_cut_point, min_littrow, max_littrow, dev_littrow_max,
                     min_littrow_ord, max_littrow_ord]
            fail_msg.append(textdict['40-017-00033'].format(*fargs))
            qc_pass.append(0)

            # TODO: Should this be the QC header values?
            # TODO:   it does not change the outcome of QC (i.e. passed=False)
            # TODO:   So what is the point?
            # TODO:  Melissa: taken out header stuff - why is this here at all
            # TODO:           if it doesn't change outcome of QC?
            # if sig was out of bounds, recalculate
            if sig_littrow > rms_littrow_max:
                # conditions
                check1 = min_littrow > dev_littrow_max
                check2 = max_littrow > dev_littrow_max
                # get the residuals
                respix = fpprops['LITTROW_YY_' + str(lit_it)][x_it]
                # check if both are out of bounds
                if check1 and check2:
                    # remove respective orders
                    worst_order = (min_littrow_ord, max_littrow_ord)
                    respix_2 = np.delete(respix, worst_order)
                    redo_sigma = True
                # check if min is out of bounds
                elif check1:
                    # remove respective order
                    worst_order = min_littrow_ord
                    respix_2 = np.delete(respix, worst_order)
                    redo_sigma = True
                # check if max is out of bounds
                elif check2:
                    # remove respective order
                    worst_order = max_littrow_ord
                    respix_2 = np.delete(respix, max_littrow_ord)
                    redo_sigma = True
                # else do not recalculate sigma
                else:
                    redo_sigma, respix_2, worst_order = False, None, None

                # if outlying order, recalculate stats
                if redo_sigma:
                    mean = mp.nansum(respix_2) / len(respix_2)
                    mean2 = mp.nansum(respix_2 ** 2) / len(respix_2)
                    rms = np.sqrt(mean2 - mean ** 2)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(mp.nanmax([max_littrow, min_littrow]))
        qc_names.append('max or min littrow')
        qc_logic.append('max or min littrow > {0:.2f}'
                        ''.format(dev_littrow_max))
    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #     quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params


def fp_write_wavesolution(params, recipe, llprops, hcfile, fpfile,
                          fiber, combine, rawhcfiles, rawfpfiles, qc_params,
                          wprops, hcwavefile):
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    wavefile = recipe.outputs['WAVE_FPMAP'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    wavefile.construct_filename(params, infile=hcfile)
    # ------------------------------------------------------------------
    # copy keys from hcwavefile
    wavefile.copy_hdict(hcwavefile)
    # set output key
    wavefile.add_hkey('KW_OUTPUT', value=wavefile.name)
    wavefile.add_hkey('KW_FIBER', value=fiber)
    # add input hc files (and deal with combining or not combining)
    if combine:
        hfiles = rawhcfiles
    else:
        hfiles = [hcfile.basename]
    wavefile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')

    # add input fp files (and deal with combining or not combining)
    if combine:
        hfiles = rawfpfiles
    else:
        hfiles = [fpfile.basename]
    wavefile.add_hkey_1d('KW_INFILE2', values=hfiles, dim1name='file')

    # ------------------------------------------------------------------
    # add the order num, fit degree and fit coefficients
    wavefile = add_wave_keys(wavefile, wprops)
    # ------------------------------------------------------------------
    # add constants used (for reproduction)
    wavefile.add_hkey('KW_WAVE_FITDEG', value=llprops['WAVE_FIT_DEGREE'])
    wavefile.add_hkey('KW_WAVE_MODE_HC', value=params['WAVE_MODE_HC'])
    wavefile.add_hkey('KW_WAVE_MODE_FP', value=params['WAVE_MODE_FP'])
    # from fp_wavesol
    wavefile.add_hkey('KW_WFP_ORD_START', value=llprops['USED_N_INIT'])
    wavefile.add_hkey('KW_WFP_ORD_FINAL', value=llprops['USED_N_FIN'])
    wavefile.add_hkey('KW_WFP_BLZ_THRES', value=llprops['USED_BLAZE_THRES'])
    wavefile.add_hkey('KW_WFP_XDIFF_MIN', value=llprops['USED_XDIFF_MIN'])
    wavefile.add_hkey('KW_WFP_XDIFF_MAX', value=llprops['USED_XDIFF_MAX'])
    wavefile.add_hkey('KW_WFP_DOPD0', value=llprops['USED_DOPD0'])
    wavefile.add_hkey('KW_WFP_LL_OFFSET', value=llprops['USED_LL_OFFSET'])
    wavefile.add_hkey('KW_WFP_DVMAX', value=llprops['USED_DV_MAX'])
    wavefile.add_hkey('KW_WFP_LLFITDEG', value=llprops['USED_LL_FIT_DEG'])
    wavefile.add_hkey('KW_WFP_UPDATECAV', value=llprops['USED_UPDATE_CAV'])
    wavefile.add_hkey('KW_WFP_FPCAV_MODE', value=llprops['USED_FP_CAV_MODE'])
    wavefile.add_hkey('KW_WFP_LLFIT_MODE', value=llprops['USED_LL_FIT_MODE'])
    wavefile.add_hkey('KW_WFP_ERRX_MIN', value=llprops['USED_ERRX_MIN'])
    wavefile.add_hkey('KW_WFP_MAXLL_FIT_RMS',
                      value=llprops['USED_MAX_LL_FIT_RMS'])
    wavefile.add_hkey('KW_WFP_T_ORD_START', value=llprops['USED_T_ORD_START'])
    wavefile.add_hkey('KW_WFP_WEI_THRES', value=llprops['USED_WEIGHT_THRES'])
    wavefile.add_hkey('KW_WFP_CAVFIT_DEG', value=llprops['USED_CAVFIT_DEG'])
    wavefile.add_hkey('KW_WFP_LARGE_JUMP', value=llprops['USED_LARGE_JUMP'])
    wavefile.add_hkey('KW_WFP_CM_INDX', value=llprops['USED_CM_INDEX'])
    # from find_fp_lines_new
    wavefile.add_hkey('KW_WFP_BORDER', value=llprops['USED_BORDER'])
    wavefile.add_hkey('KW_WFP_BSIZE', value=llprops['USED_BOX_SIZE'])
    wavefile.add_hkey('KW_WFP_SIGLIM', value=llprops['USED_SIGLIM'])
    wavefile.add_hkey('KW_WFP_LAMP', value=llprops['USED_LAMP'])
    wavefile.add_hkey('KW_WFP_IPEAK_SPACE', value=llprops['USED_IPEAK_SPACE'])
    wavefile.add_hkey('KW_WFP_EXPWIDTH', value=llprops['USED_EXPWIDTH'])
    wavefile.add_hkey('KW_WFP_CUTWIDTH', value=llprops['USED_CUTWIDTH'])
    # from fp ccf calculation (compute_fp_ccf)
    wavefile.add_hkey('KW_WFP_SIGDET', value=llprops['CCF_SIGDET'])
    wavefile.add_hkey('KW_WFP_BOXSIZE', value=llprops['CCF_BOXSIZE'])
    wavefile.add_hkey('KW_WFP_MAXFLUX', value=llprops['CCF_MAXFLUX'])
    wavefile.add_hkey('KW_WFP_NMAX', value=llprops['CCF_NMAX'])
    wavefile.add_hkey('KW_WFP_MASKMIN', value=llprops['MASK_MIN'])
    wavefile.add_hkey('KW_WFP_MASKWID', value=llprops['MASK_WIDTH'])
    wavefile.add_hkey('KW_WFP_MASKUNITS', value=llprops['MASK_UNITS'])
    # ------------------------------------------------------------------
    # add qc parameters
    wavefile.add_qckeys(qc_params)
    # copy data
    wavefile.data = llprops['LL_FINAL']
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [fiber, wavefile.filename]
    WLOG(params, '', TextEntry('40-017-00037', args=wargs))
    # write image to file
    wavefile.write()
    # add to output files (for indexing)
    recipe.add_output_file(wavefile)
    # ------------------------------------------------------------------
    # return hc wavefile
    return wavefile


def fp_write_results_table(params, recipe, llprops, hcfile, fiber):
    # iterate through Littrow test cut values
    lit_it = 2
    # get from params
    nightname = params['NIGHTNAME']
    # calculate stats for table
    final_mean = 1000 * llprops['X_MEAN_2']
    final_var = 1000 * llprops['X_VAR_2']
    num_lines = llprops['TOTAL_LINES_2']
    err = 1000 * np.sqrt(llprops['X_VAR_2'] / num_lines)
    sig_littrow = 1000 * np.array(llprops['LITTROW_SIG_' + str(lit_it)])
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    wavefile = recipe.outputs['WAVE_FPRESTAB'].newcopy(recipe=recipe,
                                                       fiber=fiber)
    # construct the filename from file instance
    wavefile.construct_filename(params, infile=hcfile)
    # ------------------------------------------------------------------
    # construct and write table
    columnnames = ['night_name', 'file_name', 'fiber', 'mean', 'rms',
                   'N_lines', 'err', 'rms_L500', 'rms_L1000', 'rms_L1500',
                   'rms_L2000', 'rms_L2500', 'rms_L3000', 'rms_L3500']
    columnformats = ['{:20s}', '{:30s}', '{:3s}', '{:7.4f}', '{:6.2f}',
                     '{:3d}', '{:6.3f}', '{:6.2f}', '{:6.2f}', '{:6.2f}',
                     '{:6.2f}', '{:6.2f}', '{:6.2f}', '{:6.2f}']
    columnvalues = [[nightname], [hcfile.basename],
                    [fiber], [final_mean], [final_var],
                    [num_lines], [err], [sig_littrow[0]],
                    [sig_littrow[1]], [sig_littrow[2]], [sig_littrow[3]],
                    [sig_littrow[4]], [sig_littrow[5]], [sig_littrow[6]]]
    # ------------------------------------------------------------------
    # make the table
    table = drs_table.make_table(params, columnnames, columnvalues,
                                 columnformats)
    # ------------------------------------------------------------------
    # log saving of file
    WLOG(params, '', TextEntry('40-017-00034', args=[wavefile.filename]))
    # merge table
    drs_table.merge_table(params, table, wavefile.filename, fmt='ascii.rst')


def fp_write_linelist_table(params, recipe, llprops, hcfile, fiber):

    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    wavefile = recipe.outputs['WAVE_FPLLTAB'].newcopy(recipe=recipe,
                                                      fiber=fiber)
    # construct the filename from file instance
    wavefile.construct_filename(params, infile=hcfile)
    # ------------------------------------------------------------------
    # construct and write table
    columnnames = ['order', 'll', 'dv', 'w', 'xi', 'xo', 'dvdx']
    columnformats = ['{:.0f}', '{:12.4f}', '{:13.5f}', '{:12.4f}',
                     '{:12.4f}', '{:12.4f}', '{:8.4f}']
    columnvalues = []
    # construct column values (flatten over orders)
    for it in range(len(llprops['X_DETAILS_2'])):
        for jt in range(len(llprops['X_DETAILS_2'][it][0])):
            row = [float(it), llprops['X_DETAILS_2'][it][0][jt],
                   llprops['LL_DETAILS_2'][it][0][jt],
                   llprops['X_DETAILS_2'][it][3][jt],
                   llprops['X_DETAILS_2'][it][1][jt],
                   llprops['X_DETAILS_2'][it][2][jt],
                   llprops['SCALE_2'][it][jt]]
            columnvalues.append(row)
    # need to flip values
    columnvalues = np.array(columnvalues).T
    # ------------------------------------------------------------------
    # make the table
    table = drs_table.make_table(params, columnnames, columnvalues,
                                 columnformats)
    # ------------------------------------------------------------------
    # log saving of file
    WLOG(params, '', TextEntry('40-017-00035', args=[wavefile.filename]))
    # merge table
    drs_table.write_table(params, table, wavefile.filename, fmt='ascii.rst')


def wave_summary(recipe, params, llprops, fiber, qc_params):
    # add qc params (fiber specific)
    recipe.plot.add_qc_params(qc_params, fiber=fiber)
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'],
                         fiber=fiber)
    # add constants used (for reproduction)
    recipe.plot.add_stat('KW_WAVE_FITDEG', value=llprops['WAVE_FIT_DEGREE'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WAVE_MODE_HC', value=params['WAVE_MODE_HC'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WAVE_MODE_FP', value=params['WAVE_MODE_FP'],
                         fiber=fiber)
    # from fp_wavesol
    recipe.plot.add_stat('KW_WFP_ORD_START', value=llprops['USED_N_INIT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_ORD_FINAL', value=llprops['USED_N_FIN'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_BLZ_THRES', value=llprops['USED_BLAZE_THRES'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_XDIFF_MIN', value=llprops['USED_XDIFF_MIN'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_XDIFF_MAX', value=llprops['USED_XDIFF_MAX'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_DOPD0', value=llprops['USED_DOPD0'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_LL_OFFSET', value=llprops['USED_LL_OFFSET'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_DVMAX', value=llprops['USED_DV_MAX'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_LLFITDEG', value=llprops['USED_LL_FIT_DEG'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_UPDATECAV', value=llprops['USED_UPDATE_CAV'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_FPCAV_MODE', value=llprops['USED_FP_CAV_MODE'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_LLFIT_MODE', value=llprops['USED_LL_FIT_MODE'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_ERRX_MIN', value=llprops['USED_ERRX_MIN'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_MAXLL_FIT_RMS', fiber=fiber,
                         value=llprops['USED_MAX_LL_FIT_RMS'])
    recipe.plot.add_stat('KW_WFP_T_ORD_START', fiber=fiber,
                         value=llprops['USED_T_ORD_START'])
    recipe.plot.add_stat('KW_WFP_WEI_THRES', value=llprops['USED_WEIGHT_THRES'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_CAVFIT_DEG', value=llprops['USED_CAVFIT_DEG'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_LARGE_JUMP', value=llprops['USED_LARGE_JUMP'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_CM_INDX', value=llprops['USED_CM_INDEX'],
                         fiber=fiber)
    # from find_fp_lines_new
    recipe.plot.add_stat('KW_WFP_BORDER', value=llprops['USED_BORDER'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_BSIZE', value=llprops['USED_BOX_SIZE'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_SIGLIM', value=llprops['USED_SIGLIM'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_LAMP', value=llprops['USED_LAMP'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_IPEAK_SPACE', fiber=fiber,
                         value=llprops['USED_IPEAK_SPACE'])
    recipe.plot.add_stat('KW_WFP_EXPWIDTH', value=llprops['USED_EXPWIDTH'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_CUTWIDTH', value=llprops['USED_CUTWIDTH'],
                         fiber=fiber)
    # from fp ccf calculation (compute_fp_ccf)
    recipe.plot.add_stat('KW_WFP_SIGDET', value=llprops['CCF_SIGDET'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_BOXSIZE', value=llprops['CCF_BOXSIZE'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_MAXFLUX', value=llprops['CCF_MAXFLUX'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_NMAX', value=llprops['CCF_NMAX'], fiber=fiber)
    recipe.plot.add_stat('KW_WFP_MASKMIN', value=llprops['MASK_MIN'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_MASKWID', value=llprops['MASK_WIDTH'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_WFP_MASKUNITS', value=llprops['MASK_UNITS'],
                         fiber=fiber)


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

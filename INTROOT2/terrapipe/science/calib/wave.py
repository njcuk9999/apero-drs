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
def get_masterwave_filename(params, fiber, **kwargs):
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

    :param p: parameter dictionary, ParamDict containing constants
    :param recipe: DrsRecipe instance, the recipe instance used
    :param header: FitsHeader or None, the header to use
    :param infile: DrsFitsFile or None, the infile associated with the header
                   can be used instead of header
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
        wavefile.filename = 'Unknown'
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
def hc_wavesol(params, recipe, iprops, hcfile, blaze, fiber, **kwargs):
    func_name = __NAME__ + '.hc_wavesol()'
    # get parameters from params / kwargs
    wave_mode_hc = pcheck(params, 'WAVE_MODE_HC', 'wave_mode_hc', kwargs,
                          func_name)
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
        return hc_wavesol1(params, recipe, iprops, hcfile, blaze, fiber,
                           wavell, ampll)
    else:
        # log that mode is not currently supported
        WLOG(params, 'error', TextEntry('09-017-00001', args=[wave_mode_hc]))
        return 0


def hc_wavesol1(params, recipe, iprops, hcfile, fiber, blaze, wavell, ampll):
    # ------------------------------------------------------------------
    # Find Gaussian Peaks in HC spectrum
    # ------------------------------------------------------------------
    llprops = find_hc_gauss_peaks(params, recipe, hcfile, fiber)

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

    # ------------------------------------------------------------------
    # Littrow test
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Plot littrow solution
    # ------------------------------------------------------------------


def fp_wavesol():

    return 0


# =============================================================================
# Define hc worker functions
# =============================================================================
def generate_shifted_wave_map(params, props, **kwargs):
    func_name = __NAME__ + '.generate_wave_map()'
    # get constants from p
    pixel_shift_inter = pcheck(params,'WAVE_PIXEL_SHIFT_INTER', 'pixelshifti',
                               kwargs, func_name)
    pixel_shift_slope = pcheck(params,'WAVE_PIXEL_SHIFT_SLOPE', 'pixelshifts',
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


def find_hc_gauss_peaks(params, recipe, hcfile, fiber, **kwargs):
    """
    Find the first guess at the guass peaks in the HC image

    :param params:
    :param recipe:
    :param hcfile:
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
    hc_sp = hcfile.data
    # get dimensions from image
    nbo, nbpix = hcfile.data.shape
    # print process
    WLOG(params, '', TextEntry('40-017-00003'))
    # get initial line list
    llprops, exists = load_hc_init_linelist(params, recipe, hcfile, fiber)
    # if we have an initial line list return here
    if exists:
        return llprops
    # ------------------------------------------------------------------------
    # else we need to populate llprops
    # ------------------------------------------------------------------------
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
            # -----------------------------------------------------------------
            # keep only peaks that are well behaved:
            # RMS not zero
            keep = rms != 0
            # peak not zero
            keep &= peak != 0
            # peak at least a few sigma from RMS
            with warnings.catch_warnings(record=True) as _:
                keep &= (peak / rms > sigma_peak)
            # -----------------------------------------------------------------
            # position of peak within segement - it needs to be close enough
            #   to the center of the segment if it is at the edge we'll catch
            #   it in the following iteration
            imax = np.argmax(segment) - wsize
            # keep only if close enough to the center
            keep &= np.abs(imax) < wsize // 3
            # -----------------------------------------------------------------
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
    columnnames, columnvalues = llprops['COLUMNS'], []
    for colname in columnnames:
        columnvalues.append(llprops[colname])
    # construct table
    ini_table = drs_table.make_table(params, columnnames, columnvalues)
    # log that we are saving hc line-list to file
    WLOG(params, '', TextEntry('40-017-00006', args=llprops['BASENAME']))
    # save the table to file
    drs_table.write_table(params, ini_table, llprops['FILENAME'], fmt=filefmt)
    # plot all orders w/fitted gaussians
    if params['DRS_PLOT'] > 0:
        # TODO: Add plotting
        # sPlt.wave_ea_plot_allorder_hcguess(p, loc)
        pass
    # ------------------------------------------------------------------
    # return lprops
    return llprops


def load_hc_init_linelist(params, recipe, hcfile, fiber, **kwargs):
    """
    Load the initial guess at the gaussian positions (if file already exists)
    else the llprops returned in an empty placeholder waiting to be filled

    :param params:
    :param recipe:
    :param hcfile:
    :param fiber:
    :param kwargs:
    :return:
    """
    func_name = __NAME__ + '.load_hc_init_linelist()'
    # get parameters from params/kwargs
    filefmt = pcheck(params, 'WAVE_HCLL_FILE_FMT', 'filefmt', kwargs, func_name)

    # construct hcll file
    hcllfile = recipe.outputs['WAVE_HCLL'].newcopy(recipe=recipe)
    hcllfile.construct_filename(params, infile=hcfile, fiber=fiber)
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
                                        columns=columns)
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
    llprops['FILENAME'] = hcllfile.filename
    llprops['BASENAME'] = hcllfile.basename
    llprops['COLUMNS'] = columns
    llprops.set_sources(['FILENAME', 'BASENAME', 'COLUMNS'], func_name)
    # add additional properties (for plotting)
    llprops['XPIX_INI'] = []
    llprops['G2_INI'] = []
    llprops.set_sources(['XPIX_INI', 'G2_INI'], func_name)
    # return properties param dict
    return llprops, exists


def fit_gaussian_triplets(params, llprops, iprops, hcfile, wavell, ampll,
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

    :param p:
    :param loc:
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
    # get hc image
    hcimage = hcfile.data
    # get dimensions
    nbo, nbpix = hcimage.shape

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
        nbins = 2 * cat_guess_dist // 1000
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
                mask = (np.abs(dv-dv_cen) > dvcut_order) & good
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
        poly_wave_sol = np.zeros_like(llprops['WAVEPARAMS'])

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
    # save parameters to loc
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

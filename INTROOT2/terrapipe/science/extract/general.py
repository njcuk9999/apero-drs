#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-09 at 13:42

@author: cook
"""
from __future__ import division
import numpy as np
from astropy.table import Table
from astropy import constants as cc
from astropy import units as uu
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe.core import math as mp
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.io import drs_data
from terrapipe.science.calib import localisation
from terrapipe.science.calib import shape
from terrapipe.science.calib import wave
from terrapipe.science.calib import general
from terrapipe.science.extract import berv

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extraction.general.py'
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
DrsNpyFile = drs_file.DrsNpyFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck
# -----------------------------------------------------------------------------
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light_kms = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define functions
# =============================================================================
def order_profiles(params, recipe, infile, fibertypes, shapelocal, shapex,
                   shapey, orderpfile, **kwargs):
    func_name = __NAME__ + '.order_profiles()'
    # get header from infile
    header = infile.header
    # look for filename in kwargs
    filename = kwargs.get('filename', None)
    # ------------------------------------------------------------------------
    # check for filename in inputs
    filename = general.get_input_files(params, 'ORDERPFILE', filename)
    # ------------------------------------------------------------------------
    # storage for order profiles
    orderprofiles = dict()
    orderprofilefiles = dict()
    # loop around fibers
    for fiber in fibertypes:
        # log progress (straightening orderp)
        WLOG(params, 'info', TextEntry('40-016-00003', args=[fiber]))
        # construct order profile file
        orderpsfile = orderpfile.newcopy(recipe=recipe, fiber=fiber)
        orderpsfile.construct_filename(params, infile=infile)
        # check if temporary file exists
        if orderpsfile.file_exists() and (filename is None):
            # load the numpy temporary file
            #    Note: NpyFitsFile needs arguments params!
            if isinstance(orderpsfile, DrsNpyFile):
                # log progress (read file)
                wargs = [orderpsfile.filename]
                WLOG(params, '', TextEntry('40-013-00023', args=wargs))
                # read npy file
                orderpsfile.read(params)
            else:
                eargs = [orderpsfile.__str__(), func_name]
                WLOG(params, 'error', TextEntry('00-016-00023', args=eargs))
            # push data into orderp
            orderp = orderpsfile.data
            orderpfilename = orderpsfile.filename
        # load the order profile
        else:
            # load using localisation load order profile function
            out = localisation.load_orderp(params, header, fiber=fiber,
                                           filename=filename)
            orderpfilename, orderp = out
            # straighten orders
            orderp = shape.ea_transform(params, orderp, shapelocal,
                                        dxmap=shapex, dymap=shapey)
            # push into orderpsfile
            orderpsfile.data = orderp
            # log progress (saving to file)
            wargs = [orderpsfile.filename]
            WLOG(params, '', TextEntry('40-013-00024', args=wargs))
            # save for use later (as .npy)
            orderpsfile.write(params)
        # store in storage dictionary
        orderprofiles[fiber] = orderp
        orderprofilefiles[fiber] = orderpfilename
    # return order profiles
    return orderprofiles, orderprofilefiles


def thermal_correction(params, recipe, header, props=None, eprops=None,
                       fiber=None, **kwargs):
    func_name = __NAME__ + '.thermal_correction()'
    # deal with props = None
    if props is None:
        props = ParamDict()
    # deal with eprops = None
    if eprops is None:
        eprops = ParamDict()
    # get properties from parameter dictionaries / kwargs
    dprtype = pcheck(params, 'DPRTYPE', 'dprtype', kwargs, func_name,
                     paramdict=props)
    tapas_thres = pcheck(params, 'THERMAL_THRES_TAPAS', 'tapas_thres', kwargs,
                         func_name)
    envelope = pcheck(params, 'THERMAL_ENVELOPE_PERCENTILE', 'envelope',
                      kwargs, func_name)
    filter_wid = pcheck(params, 'THERMAL_FILTER_WID', 'filter_wid', kwargs,
                        func_name)
    torder = pcheck(params, 'THERMAL_ORDER', 'torder', kwargs, func_name)
    red_limt = pcheck(params, 'THERMAL_RED_LIMIT', 'red_limit', kwargs,
                      func_name)
    blue_limit = pcheck(params, 'THERMAL_BLUE_LIMIT', 'blue_limit', kwargs,
                        func_name)
    e2ds = pcheck(params, 'E2DS', 'e2ds', kwargs, func_name, paramdict=eprops)
    e2dsff = pcheck(params, 'E2DSFF', 'e2dsff', kwargs, func_name,
                    paramdict=eprops)
    flat = pcheck(params, 'FLAT', paramdict=eprops)

    corrtype1 = pcheck(params, 'THERMAL_CORRETION_TYPE1', 'corrtype1', kwargs,
                       func_name, mapf='list', dtype=str)
    corrtype2 = pcheck(params, 'THERMAL_CORRETION_TYPE2', 'corrtype2', kwargs,
                       func_name, mapf='list', dtype=str)

    thermal_file = kwargs.get('thermal_file', None)
    # ----------------------------------------------------------------------
    # get pconstant from p
    pconst = constants.pload(params['INSTRUMENT'])
    # ----------------------------------------------------------------------
    # get fiber dprtype
    fibertype = pconst.FIBER_DATA_TYPE(dprtype, fiber)
    # ----------------------------------------------------------------------
    # get master wave filename
    mwavefile = wave.get_masterwave_filename(params, fiber)
    # get master wave map
    wprops = wave.get_wavesolution(params, recipe, filename=mwavefile)
    # get the wave solution
    wavemap = wprops['WAVEMAP']
    # ----------------------------------------------------------------------
    # get thermal (only if in one of the correction lists)
    if fibertype in list(corrtype1) + list(corrtype2):
        thermalfile, thermal = get_thermal(params, header, fiber=fiber,
                                           filename=thermal_file)
        # ----------------------------------------------------------------------
        # thermal correction kwargs
        tkwargs = dict(header=header, fiber=fiber, wavemap=wavemap,
                       tapas_thres=tapas_thres, envelope=envelope,
                       filter_wid=filter_wid, torder=torder,
                       red_limit=red_limt, blue_limit=blue_limit,
                       thermal=thermal)
    else:
        tkwargs = dict()
        thermalfile = 'None'
    # base thermal correction on fiber type
    if fibertype in corrtype1:
        # log progress: doing thermal correction
        wargs = [fibertype, 1]
        WLOG(params, 'info', TextEntry('40-016-00012', args=wargs))
        # do thermal correction
        e2ds = tcorrect1(params, recipe, e2ds, **tkwargs)
        e2dsff = tcorrect1(params, recipe, e2dsff, flat=flat, **tkwargs)
    elif fibertype in corrtype2:
        # log progress: doing thermal correction
        wargs = [fibertype, 1]
        WLOG(params, 'info', TextEntry('40-016-00012', args=wargs))
        # do thermal correction
        e2ds = tcorrect2(params, recipe, e2ds, **tkwargs)
        e2dsff = tcorrect2(params, recipe, e2dsff, flat=flat, **tkwargs)
    else:
        # log that we are not correcting thermal
        WLOG(params, 'info', TextEntry('40-016-00013', args=[fibertype]))

        thermalfile = 'None'
    # ----------------------------------------------------------------------
    # add / update eprops
    eprops['E2DS'] = e2ds
    eprops['E2DSFF'] = e2dsff
    eprops['FIBERTYPE'] = fibertype
    eprops['THERMALFILE'] = thermalfile
    # update source
    keys = ['E2DS', 'E2DSFF', 'FIBERTYPE', 'THERMALFILE']
    eprops.set_sources(keys, func_name)
    # return eprops
    return eprops


def get_thermal(params, header, fiber, filename=None):
    # get file definition
    out_thermal = core.get_file_definition('THERMAL_E2DS', params['INSTRUMENT'],
                                           kind='red')
    # get key
    key = out_thermal.get_dbkey(fiber=fiber)
    # load calib file
    thermal, thermal_file = general.load_calib_file(params, key, header,
                                                    filename=filename)
    # log which fpmaster file we are using
    WLOG(params, '', TextEntry('40-014-00040', args=[thermal_file]))
    # return the master image
    return thermal_file, thermal


def tcorrect1(params, recipe, image, header, fiber, wavemap, thermal=None,
              flat=None, **kwargs):
    # get parameters from skwargs
    tapas_thres = kwargs.get('tapas_thres', None)
    filter_wid = kwargs.get('filter_wid', None)
    torder = kwargs.get('torder', None)
    red_limit = kwargs.get('red_limit', None)
    tapas_file = kwargs.get('tapas_file', None)
    # ----------------------------------------------------------------------
    # deal with no thermal
    if thermal is None:
        # get thermal
        _, thermal = get_thermal(params, header, fiber=fiber)
    # ----------------------------------------------------------------------
    # if we have a flat we should apply it to the thermal
    if flat is not None:
        thermal = thermal / flat
        kind = 'FF '
    else:
        kind = ''
    # ----------------------------------------------------------------------
    # deal with rare case that thermal is all zeros
    if mp.nansum(thermal) == 0 or np.sum(np.isfinite(thermal)) == 0:
        return image
    # ----------------------------------------------------------------------
    # load tapas
    tapas, _ = drs_data.load_tapas(params, filename=tapas_file)
    wtapas, ttapas = tapas['wavelength'], tapas['trans_combined']
    # ----------------------------------------------------------------------
    # splining tapas onto the order 49 wavelength grid
    sptapas = mp.iuv_spline(wtapas, ttapas)
    # binary mask to be saved; this corresponds to the domain for which
    #    transmission is basically zero and we can safely use the domain
    #    to scale the thermal background. We only do this for wavelength smaller
    #    than "THERMAL_TAPAS_RED_LIMIT" nm as this is the red end of the
    #    TAPAS domain
    # set torder mask all to False initially
    torder_mask = np.zeros_like(wavemap[torder, :], dtype=bool)
    # get the wave mask
    wavemask = wavemap[torder] < red_limit
    # get the tapas data for these wavelengths
    torder_tapas = sptapas(wavemap[torder, wavemask])
    # find those pixels lower than threshold in tapas
    torder_mask[wavemask] = torder_tapas < tapas_thres
    # median filter the thermal (loop around orders)
    for order_num in range(thermal.shape[0]):
        thermal[order_num] = mp.medfilt_1d(thermal[order_num], filter_wid)

    # we find the median scale between the observation and the thermal
    #    background in domains where there is no transmission
    thermal_torder = thermal[torder, torder_mask]
    image_torder = image[torder, torder_mask]
    ratio = mp.nanmedian(thermal_torder / image_torder)
    # scale thermal by ratio
    thermal = thermal / ratio
    # ----------------------------------------------------------------------
    # plot thermal background plot
    recipe.plot('THERMAL_BACKGROUND', params=params, wave=wavemap, image=image,
                thermal=thermal, torder=torder, tmask=torder_mask, fiber=fiber,
                kind=kind)
    # ----------------------------------------------------------------------
    # correct image
    corrected_image = image - thermal
    # ----------------------------------------------------------------------
    # return p and corrected image
    return corrected_image


def tcorrect2(params, recipe, image, header, fiber, wavemap, thermal=None,
              flat=None, **kwargs):
    envelope_percent = kwargs.get('envelope', None)
    filter_wid = kwargs.get('filter_wid', None)
    torder = kwargs.get('torder', None)
    red_limit = kwargs.get('red_limit', None)
    blue_limit = kwargs.get('blue_limit', None)
    # thermal_file = kwargs.get('thermal_file', None)
    # get the shape
    dim1, dim2 = image.shape
    # ----------------------------------------------------------------------
    # deal with no thermal
    if thermal is None:
        # get thermal
        _, thermal = get_thermal(params, header, fiber=fiber)
    # ----------------------------------------------------------------------
    # if we have a flat we should apply it to the thermal
    if flat is not None:
        thermal = thermal / flat
        kind = 'FF '
    else:
        kind = ''
    # ----------------------------------------------------------------------
    # deal with rare case that thermal is all zeros
    if mp.nansum(thermal) == 0 or np.sum(np.isfinite(thermal)) == 0:
        return image
    # ----------------------------------------------------------------------
    # set up an envelope to measure thermal background in image
    envelope = np.zeros(dim2)
    # loop around all pixels
    for x_it in range(dim2):
        # define start and end points
        start = x_it - filter_wid // 2
        end = x_it + filter_wid // 2
        # deal with out of bounds
        if start < 0:
            start = 0
        if end > dim2 - 1:
            end = dim2 - 1
        # get the box for this pixel
        imagebox = image[torder, start:end]
        # get the envelope
        with warnings.catch_warnings(record=True) as _:
            envelope[x_it] = np.nanpercentile(imagebox, envelope_percent)
    # ----------------------------------------------------------------------
    # median filter the thermal (loop around orders)
    for order_num in range(dim1):
        thermal[order_num] = mp.medfilt_1d(thermal[order_num], filter_wid)
    # ----------------------------------------------------------------------
    # only keep wavelength in range of thermal limits
    wavemask = (wavemap[torder] > blue_limit) & (wavemap[torder] < red_limit)
    # we find the median scale between the observation and the thermal
    #    background in domains where there is no transmission
    thermal_torder = thermal[torder, wavemask]
    envelope_torder = envelope[wavemask]
    ratio = mp.nanmedian(thermal_torder / envelope_torder)
    # scale thermal by ratio
    thermal = thermal / ratio
    # ----------------------------------------------------------------------
    # plot thermal background plot
    recipe.plot('THERMAL_BACKGROUND', params=params, wave=wave, image=image,
                thermal=thermal, torder=torder, tmask=wavemask, fiber=fiber,
                kind=kind)
    # ----------------------------------------------------------------------
    # correct image
    corrected_image = image - thermal
    # ----------------------------------------------------------------------
    # return p and corrected image
    return corrected_image


def e2ds_to_s1d(params, recipe, wavemap, e2ds, blaze, fiber=None, wgrid='wave',
                kind=None, **kwargs):
    func_name = __NAME__ + '.e2ds_to_s1d()'
    # get parameters from p
    wavestart = pcheck(params, 'EXT_S1D_WAVESTART', 'wavestart', kwargs,
                       func_name)
    waveend = pcheck(params, 'EXT_S1D_WAVEEND', 'waveend', kwargs,
                     func_name)
    binwave = pcheck(params, 'EXT_S1D_BIN_UWAVE', 'binwave', kwargs,
                     func_name)
    binvelo = pcheck(params, 'EXT_S1D_BIN_UVELO', 'binvelo', kwargs,
                     func_name)
    smooth_size = pcheck(params, 'EXT_S1D_EDGE_SMOOTH_SIZE', 'smooth_size',
                         kwargs, func_name)
    blazethres = pcheck(params, 'TELLU_CUT_BLAZE_NORM', 'blazethres', kwargs,
                        func_name)

    # get size from e2ds
    nord, npix = e2ds.shape

    # log progress: calculating s1d (wavegrid)
    WLOG(params, '', TextEntry('40-016-00009', args=[wgrid]))

    # -------------------------------------------------------------------------
    # Decide on output wavelength grid
    # -------------------------------------------------------------------------
    if wgrid == 'wave':
        wavegrid = np.arange(wavestart, waveend + binwave / 2.0, binwave)
    else:
        # work out number of wavelength points
        flambda = np.log(waveend / wavestart)
        nlambda = np.round((speed_of_light_kms / binvelo) * flambda)
        # updating end wavelength slightly to have exactly 'step' km/s
        waveend = np.exp(nlambda * (binvelo / speed_of_light_kms)) * wavestart
        # get the wavegrid
        index = np.arange(nlambda) / nlambda
        wavegrid = wavestart * np.exp(index * np.log(waveend / wavestart))

    # -------------------------------------------------------------------------
    # define a smooth transition mask at the edges of the image
    # this ensures that the s1d has no discontinuity when going from one order
    # to the next. We define a scale for this mask
    # smoothing scale
    # -------------------------------------------------------------------------
    # define a kernal that goes from -3 to +3 smooth_sizes of the mask
    xker = np.arange(-smooth_size * 3, smooth_size * 3, 1)
    ker = np.exp(-0.5 * (xker / smooth_size) ** 2)
    # set up the edge vector
    edges = np.ones(npix, dtype=bool)
    # set edges of the image to 0 so that  we get a sloping weight
    edges[:int(3 * smooth_size)] = False
    edges[-int(3 * smooth_size):] = False
    # define the weighting for the edges (slopevector)
    slopevector = np.zeros_like(blaze)
    # for each order find the sloping weight vector
    for order_num in range(nord):
        # get the blaze for this order
        oblaze = np.array(blaze[order_num])
        # find the valid pixels
        cond1 = np.isfinite(oblaze) & np.isfinite(e2ds[order_num])
        with warnings.catch_warnings(record=True) as _:
            cond2 = oblaze > (blazethres * mp.nanmax(oblaze))
        valid = cond1 & cond2 & edges
        # convolve with the edge kernel
        oweight = np.convolve(valid, ker, mode='same')
        # normalise to the maximum
        with warnings.catch_warnings(record=True) as _:
            oweight = oweight - mp.nanmin(oweight)
            oweight = oweight / mp.nanmax(oweight)
        # append to sloping vector storage
        slopevector[order_num] = oweight

    # multiple the spectrum and blaze by the sloping vector
    sblaze = np.array(blaze) * slopevector
    se2ds = np.array(e2ds) * slopevector

    # -------------------------------------------------------------------------
    # Perform a weighted mean of overlapping orders
    # by performing a spline of both the blaze and the spectrum
    # -------------------------------------------------------------------------
    out_spec = np.zeros_like(wavegrid)
    weight = np.zeros_like(wavegrid)

    # loop around all orders
    for order_num in range(nord):
        # identify the valid pixels
        valid = np.isfinite(se2ds[order_num]) & np.isfinite(sblaze[order_num])
        valid_float = valid.astype(float)
        # if we have no valid points we need to skip
        if np.sum(valid) == 0:
            continue
        # get this orders vectors
        owave = wavemap[order_num]
        oe2ds = se2ds[order_num, valid]
        oblaze = sblaze[order_num, valid]
        # create the splines for this order
        spline_sp = mp.iuv_spline(owave[valid], oe2ds, k=5, ext=1)
        spline_bl = mp.iuv_spline(owave[valid], oblaze, k=5, ext=1)
        spline_valid = mp.iuv_spline(owave, valid_float, k=1, ext=1)
        # can only spline in domain of the wave
        useful_range = (wavegrid > mp.nanmin(owave[valid]))
        useful_range &= (wavegrid < mp.nanmax(owave[valid]))
        # finding pixels where we have immediate neighbours that are
        #   considered valid in the spline (to avoid interpolating over large
        #   gaps in validity)
        maskvalid = np.zeros_like(wavegrid, dtype=bool)
        maskvalid[useful_range] = spline_valid(wavegrid[useful_range]) > 0.9
        useful_range &= maskvalid
        # get splines and add to outputs
        weight[useful_range] += spline_bl(wavegrid[useful_range])
        out_spec[useful_range] += spline_sp(wavegrid[useful_range])

    # need to deal with zero weight --> set them to NaNs
    zeroweights = weight == 0
    weight[zeroweights] = np.nan

    # plot the s1d weight/before/after plot
    recipe.plot('EXTRACT_S1D_WEIGHT', params=params, wave=wavegrid,
                flux=out_spec, weight=weight, kind=wgrid, fiber=fiber,
                stype=kind)
    # work out the weighted spectrum
    with warnings.catch_warnings(record=True) as _:
        w_out_spec = out_spec / weight

    # TODO: propagate errors
    ew_out_spec = np.zeros_like(w_out_spec)

    # construct the s1d table (for output)
    s1dtable = Table()
    s1dtable['wavelength'] = wavegrid
    s1dtable['flux'] = w_out_spec
    s1dtable['eflux'] = ew_out_spec
    s1dtable['weight'] = weight

    # set up return dictionary
    props = ParamDict()
    # add data
    props['WAVEGRID'] = wavegrid
    props['S1D'] = w_out_spec
    props['S1D_ERROR'] = ew_out_spec
    props['WEIGHT'] = weight
    # add astropy table
    props['S1DTABLE'] = s1dtable
    # add constants
    props['WAVESTART'] = wavestart
    props['WAVEEND'] = waveend
    props['WAVEKIND'] = wgrid
    if wgrid == 'wave':
        props['BIN_WAVE'] = binwave
        props['BIN_VELO'] = 'None'
    else:
        props['BIN_WAVE'] = 'None'
        props['BIN_VELO'] = binvelo
    props['SMOOTH_SIZE'] = smooth_size
    props['BLAZE_THRES'] = blazethres
    # add source
    keys = ['WAVEGRID', 'S1D', 'WEIGHT', 'S1D_ERROR', 'S1DTABLE',
            'WAVESTART', 'WAVEEND', 'WAVEKIND', 'BIN_WAVE',
            'BIN_VELO', 'SMOOTH_SIZE', 'BLAZE_THRES']
    props.set_sources(keys, func_name)
    # return properties
    return props


def add_s1d_keys(infile, props):
    infile.add_hkey('KW_S1D_WAVESTART', value=props['WAVESTART'])
    infile.add_hkey('KW_S1D_WAVEEND', value=props['WAVEEND'])
    infile.add_hkey('KW_S1D_KIND', value=props['WAVEKIND'])
    infile.add_hkey('KW_S1D_BWAVE', value=props['BIN_WAVE'])
    infile.add_hkey('KW_S1D_BVELO', value=props['BIN_VELO'])
    infile.add_hkey('KW_S1D_SMOOTH', value=props['SMOOTH_SIZE'])
    infile.add_hkey('KW_S1D_BLAZET', value=props['BLAZE_THRES'])
    return infile


# ===========================================================================
# writing and qc functions
# =============================================================================
def qc_extraction(params, eprops):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], [],
    qc_logic, qc_pass = [], []
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # --------------------------------------------------------------
    # if array is completely NaNs it shouldn't pass
    if np.sum(np.isfinite(eprops['E2DS'])) == 0:
        # add failed message to fail message list
        fail_msg.append(textdict['40-016-00008'])
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append('NaN')
    qc_names.append('image')
    qc_logic.append('image is all NaN')
    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return
    return qc_params, passed


def write_extraction_files(params, recipe, infile, rawfiles, combine, fiber,
                           orderpfile, props, lprops, wprops, eprops, bprops,
                           swprops, svprops, shapelocalfile, shapexfile,
                           shapeyfile, shapelocal, flat_file, blaze_file,
                           qc_params):
    # ----------------------------------------------------------------------
    # Store E2DS in file
    # ----------------------------------------------------------------------
    # get a new copy of the e2ds file
    e2dsfile = recipe.outputs['E2DS_FILE'].newcopy(recipe=recipe,
                                                   fiber=fiber)
    # construct the filename from file instance
    e2dsfile.construct_filename(params, infile=infile)
    # define header keys for output file
    # copy keys from input file
    e2dsfile.copy_original_keys(infile)
    # add version
    e2dsfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    e2dsfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    e2dsfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    e2dsfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    e2dsfile.add_hkey('KW_OUTPUT', value=e2dsfile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    e2dsfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add the calibration files use
    e2dsfile = general.add_calibs_to_header(e2dsfile, props)
    e2dsfile.add_hkey('KW_FIBER', value=fiber)
    # ----------------------------------------------------------------------
    # add the other calibration files used
    e2dsfile.add_hkey('KW_CDBORDP', value=orderpfile)
    e2dsfile.add_hkey('KW_CDBLOCO', value=lprops['LOCOFILE'])
    e2dsfile.add_hkey('KW_CDBSHAPEL', value=shapelocalfile)
    e2dsfile.add_hkey('KW_CDBSHAPEDX', value=shapexfile)
    e2dsfile.add_hkey('KW_CDBSHAPEDY', value=shapeyfile)
    e2dsfile.add_hkey('KW_CDBFLAT', value=flat_file)
    e2dsfile.add_hkey('KW_CDBBLAZE', value=blaze_file)
    e2dsfile.add_hkey('KW_CDBTHERMAL', value=eprops['THERMALFILE'])
    e2dsfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    # additional calibration keys
    e2dsfile.add_hkey('KW_C_FTYPE', value=eprops['FIBERTYPE'])
    # ----------------------------------------------------------------------
    # add qc parameters
    e2dsfile.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # add shape transform parameters
    e2dsfile.add_hkey('KW_SHAPE_DX', value=shapelocal[0])
    e2dsfile.add_hkey('KW_SHAPE_DY', value=shapelocal[1])
    e2dsfile.add_hkey('KW_SHAPE_A', value=shapelocal[2])
    e2dsfile.add_hkey('KW_SHAPE_B', value=shapelocal[3])
    e2dsfile.add_hkey('KW_SHAPE_C', value=shapelocal[4])
    e2dsfile.add_hkey('KW_SHAPE_D', value=shapelocal[5])
    # ----------------------------------------------------------------------
    # add extraction type (does not change for future files)
    e2dsfile.add_hkey('KW_EXT_TYPE', value=e2dsfile.name)
    # add SNR parameters to header
    e2dsfile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                         dim1name='order')
    # add start and end extraction order used
    e2dsfile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
    e2dsfile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
    # add extraction ranges used
    e2dsfile.add_hkey('KW_EXT_RANGE1', value=eprops['RANGE1'])
    e2dsfile.add_hkey('KW_EXT_RANGE2', value=eprops['RANGE2'])
    # add cosmic parameters used
    e2dsfile.add_hkey('KW_COSMIC', value=eprops['COSMIC'])
    e2dsfile.add_hkey('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'])
    e2dsfile.add_hkey('KW_COSMIC_THRES',
                      value=eprops['COSMIC_THRESHOLD'])
    # add saturation parameters used
    e2dsfile.add_hkey('KW_SAT_QC', value=eprops['SAT_LEVEL'])
    with warnings.catch_warnings(record=True) as _:
        max_sat_level = mp.nanmax(eprops['FLUX_VAL'])
    e2dsfile.add_hkey('KW_SAT_LEVEL', value=max_sat_level)
    # ----------------------------------------------------------------------
    # add loco parameters (using locofile)
    locofile = lprops['LOCOOBJECT']
    e2dsfile.copy_original_keys(locofile, group='loc')
    # ----------------------------------------------------------------------
    e2dsfile = wave.add_wave_keys(e2dsfile, wprops)
    # ----------------------------------------------------------------------
    # add berv properties to header
    e2dsfile = berv.add_berv_keys(params, e2dsfile, bprops)
    # ----------------------------------------------------------------------
    # copy data
    e2dsfile.data = eprops['E2DS']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsfile.filename]
    WLOG(params, '', TextEntry('40-016-00005', args=wargs))
    # write image to file
    e2dsfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(e2dsfile)
    # ----------------------------------------------------------------------
    # Store E2DSFF in file
    # ----------------------------------------------------------------------
    # get a new copy of the e2dsff file
    e2dsfffile = recipe.outputs['E2DSFF_FILE'].newcopy(recipe=recipe,
                                                       fiber=fiber)
    # construct the filename from file instance
    e2dsfffile.construct_filename(params, infile=infile)
    # copy header from e2dsff file
    e2dsfffile.copy_hdict(e2dsfile)
    # add extraction type (does not change for future files)
    e2dsfffile.add_hkey('KW_EXT_TYPE', value=e2dsfffile.name)
    # set output key
    e2dsfffile.add_hkey('KW_OUTPUT', value=e2dsfffile.name)
    # copy data
    e2dsfffile.data = eprops['E2DSFF']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsfffile.filename]
    WLOG(params, '', TextEntry('40-016-00006', args=wargs))
    # write image to file
    e2dsfffile.write()
    # add to output files (for indexing)
    recipe.add_output_file(e2dsfffile)
    # ----------------------------------------------------------------------
    # Store E2DSLL in file
    # ----------------------------------------------------------------------
    # get a new copy of the e2dsll file
    e2dsllfile = recipe.outputs['E2DSLL_FILE'].newcopy(recipe=recipe,
                                                       fiber=fiber)
    # construct the filename from file instance
    e2dsllfile.construct_filename(params, infile=infile)
    # copy header from e2dsll file
    e2dsllfile.copy_hdict(e2dsfile)
    # set output key
    e2dsllfile.add_hkey('KW_OUTPUT', value=e2dsllfile.name)
    # copy data
    e2dsllfile.data = eprops['E2DSLL']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsllfile.filename]
    WLOG(params, '', TextEntry('40-016-00007', args=wargs))
    # write image to file
    e2dsllfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(e2dsllfile)
    # ----------------------------------------------------------------------
    # Store S1D_W in file
    # ----------------------------------------------------------------------
    # get a new copy of the s1d_w file
    s1dwfile = recipe.outputs['S1D_W_FILE'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    s1dwfile.construct_filename(params, infile=infile)
    # copy header from e2dsll file
    s1dwfile.copy_hdict(e2dsfile)
    # set output key
    s1dwfile.add_hkey('KW_OUTPUT', value=s1dwfile.name)
    # add new header keys
    s1dwfile = add_s1d_keys(s1dwfile, swprops)
    # copy data
    s1dwfile.data = swprops['S1DTABLE']
    # must change the datatype to 'table'
    s1dwfile.datatype = 'table'
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = ['wave', s1dwfile.filename]
    WLOG(params, '', TextEntry('40-016-00010', args=wargs))
    # write image to file
    s1dwfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(s1dwfile)
    # ----------------------------------------------------------------------
    # Store S1D_V in file
    # ----------------------------------------------------------------------
    # get a new copy of the s1d_v file
    s1dvfile = recipe.outputs['S1D_V_FILE'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    s1dvfile.construct_filename(params, infile=infile)
    # copy header from e2dsll file
    s1dvfile.copy_hdict(e2dsfile)
    # add new header keys
    s1dvfile = add_s1d_keys(s1dvfile, svprops)
    # set output key
    s1dvfile.add_hkey('KW_OUTPUT', value=s1dvfile.name)
    # copy data
    s1dvfile.data = svprops['S1DTABLE']
    # must change the datatype to 'table'
    s1dvfile.datatype = 'table'
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = ['velocity', s1dvfile.filename]
    WLOG(params, '', TextEntry('40-016-00010', args=wargs))
    # write image to file
    s1dvfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(s1dvfile)
    # ----------------------------------------------------------------------
    # return e2ds files
    return e2dsfile, e2dsfffile


def extract_summary(recipe, params, qc_params, e2dsfile, shapelocal, eprops,
                    fiber):
    # add qc params (fiber specific)
    recipe.plot.add_qc_params(qc_params, fiber=fiber)
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_TYPE', value=e2dsfile.name,
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_DX', value=shapelocal[0],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_DY', value=shapelocal[1],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_A', value=shapelocal[2],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_B', value=shapelocal[3],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_C', value=shapelocal[4],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_D', value=shapelocal[5],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_START', value=eprops['START_ORDER'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_END', value=eprops['END_ORDER'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE1', value=eprops['RANGE1'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE2', value=eprops['RANGE2'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC', value=eprops['COSMIC'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_THRES', fiber=fiber,
                         value=eprops['COSMIC_THRESHOLD'])


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

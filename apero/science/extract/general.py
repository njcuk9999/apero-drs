#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-09 at 13:42

@author: cook
"""
import numpy as np
from astropy.table import Table
from astropy import constants as cc
from astropy import units as uu
import os
import warnings

from apero import core
from apero.core import constants
from apero.core import math as mp
from apero import locale
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_startup
from apero.io import drs_data
from apero.science.calib import localisation
from apero.science.calib import shape
from apero.science.calib import wave
from apero.science.calib import general
from apero.science.calib import flat_blaze
from apero.science.extract import berv

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extraction.general.py'
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
# Define general functions
# =============================================================================
def order_profiles(params, recipe, infile, fibertypes, shapelocal, shapex,
                   shapey, orderpfile, filenames=None):
    func_name = __NAME__ + '.order_profiles()'
    # filenames must be a dictionary
    if not isinstance(filenames, dict):
        filenames = dict()
        for fiber in fibertypes:
            filenames[fiber] = None
    # ------------------------------------------------------------------------
    # get header from infile
    header = infile.header
    # ------------------------------------------------------------------------
    # storage for order profiles
    orderprofiles = dict()
    orderprofilefiles = dict()
    # loop around fibers
    for fiber in fibertypes:
        # log progress (straightening orderp)
        WLOG(params, 'info', TextEntry('40-016-00003', args=[fiber]))

        # get key
        key = orderpfile.get_dbkey(fiber=fiber)
        # ------------------------------------------------------------------
        # check for filename in inputs
        filename = general.get_input_files(params, 'ORDERPFILE', key, header,
                                           default=filenames[fiber])
        # ------------------------------------------------------------------
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
                orderpsfile.read_file(params)
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
            orderpsfile.write_file(params)
        # store in storage dictionary
        orderprofiles[fiber] = orderp
        orderprofilefiles[fiber] = orderpfilename
    # return order profiles
    return orderprofiles, orderprofilefiles


# =============================================================================
# Define thermal functions
# =============================================================================
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
    thermal_correct = pcheck(params, 'THERMAL_CORRECT', 'thermal_correct',
                             kwargs, func_name)
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
    # deal with skipping thermal correction
    if not thermal_correct:
        # add / update eprops
        eprops['E2DS'] = e2ds
        eprops['E2DSFF'] = e2dsff
        eprops['FIBERTYPE'] = fibertype
        eprops['THERMALFILE'] = 'None'
        # update source
        keys = ['E2DS', 'E2DSFF', 'FIBERTYPE', 'THERMALFILE']
        eprops.set_sources(keys, func_name)
        # return eprops
        return eprops
    # ----------------------------------------------------------------------
    # get thermal (only if in one of the correction lists)
    if fibertype in corrtype1:
        thermalfile, thermal = get_thermal(params, header, fiber=fiber,
                                           filename=thermal_file,
                                           kind='THERMALT_E2DS')
    elif fibertype in corrtype2:
        thermalfile, thermal = get_thermal(params, header, fiber=fiber,
                                           filename=thermal_file,
                                           kind='THERMALI_E2DS')
    else:
        thermal = None
        thermalfile = 'None'
    # ----------------------------------------------------------------------
    # thermal correction kwargs
    tkwargs = dict(header=header, fiber=fiber, wavemap=wavemap,
                   tapas_thres=tapas_thres, envelope=envelope,
                   filter_wid=filter_wid, torder=torder,
                   red_limit=red_limt, blue_limit=blue_limit,
                   thermal=thermal)

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


def get_thermal(params, header, fiber, kind, filename=None):
    # get file definition
    out_thermal = core.get_file_definition(kind, params['INSTRUMENT'],
                                           kind='red')
    # get key
    key = out_thermal.get_dbkey(fiber=fiber)
    # ------------------------------------------------------------------------
    # check for filename in inputs
    filename = general.get_input_files(params, 'THERMAL', key, header, filename)
    # ------------------------------------------------------------------------
    # load calib file
    thermal, thermal_file = general.load_calib_file(params, key, header,
                                                    filename=filename)
    # log which fpmaster file we are using
    WLOG(params, '', TextEntry('40-016-00027', args=[thermal_file]))
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
        _, thermal = get_thermal(params, header, fiber=fiber,
                                 kind='THERMALT_E2DS')
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
        _, thermal = get_thermal(params, header, fiber=fiber,
                                 kind='THERMALI_E2DS')
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
    pconst = constants.pload(params['INSTRUMENT'])
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber =  pconst.FIBER_KINDS()
    # output storage (dictionary of corrected extracted files)
    outputs = dict()
    # ----------------------------------------------------------------------
    # Deal with loading the reference fiber image props
    # ----------------------------------------------------------------------
    # check for reference fiber in extract dict
    if ref_fiber not in extractdict:
        eargs = [ref_fiber, ', '.join(extractdict.keys()), func_name]
        WLOG(params, 'error', TextEntry('00-016-00024', args=eargs))
    # get the reference file
    reffile = extractdict[ref_fiber]
    # get dprtype
    dprtype = reffile.get_key('KW_DPRTYPE')
    # get dpr type for ref image
    refdpr = pconst.FIBER_DPR_POS(dprtype, ref_fiber)
    # check that refdpr is FP (must be a FP)
    if refdpr != 'FP':
        # log and raise error
        eargs = [ref_fiber, dprtype, func_name]
        WLOG(params, 'error', TextEntry('00-016-00025', args=eargs))

    # get the data for the reference image
    refimage = np.array(reffile.data)
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
            WLOG(params, 'error', TextEntry('00-016-00026', args=eargs))
        # get the science image
        scifile = extractdict[sci_fiber]
        # get the data for the reference image
        sciimage = np.array(scifile.data)
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
    # return output dictionary with corrected extracted files
    return outputs


def correct_dark_fp(params, extractdict, **kwargs):
    # set the function name
    func_name = __NAME__ + '.correct_dark_fp()'
    # get properties from parameters
    leak2dext = pcheck(params, 'LEAK_2D_EXTRACT_FILES', 'leak2dext', kwargs,
                       func_name)
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
    pconst = constants.pload(params['INSTRUMENT'])
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber =  pconst.FIBER_KINDS()
    all_fibers = sci_fibers + [ref_fiber]
    # ----------------------------------------------------------------------
    # get reference file
    ref_file = extractdict[extfiletype][ref_fiber]
    refimage = np.array(ref_file.data)
    ref_header = ref_file.header
    # get size of reference image
    nbo, nbpix = refimage.shape
    # ----------------------------------------------------------------------
    # storage for master files
    master_leaks = dict()
    # load master data
    for fiber in all_fibers:
        # get leak master for file
        _, leakmaster = get_leak_master(params, ref_header, fiber,
                                        'LEAKM_E2DS')
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
            wargs = [order_num, ratio, approx_ratio, (1 - bad_ratio),
                     (1 + bad_ratio)]
            WLOG(params, 'warning', TextEntry('10-016-00024', args=wargs))
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
            WLOG(params, 'info', TextEntry('40-016-00029', args=wargs))
            # get extfile
            extfile = extractdict[extfiletype][fiber]
            # get the extraction image
            extimage = np.array(extfile.data)
            # --------------------------------------------------------------
            # if we are dealing with the E2DS we need the flat
            if extfiletype == 'E2DS_FILE':
                # load the flat file for this fiber
                flat_file, flat = flat_blaze.get_flat(params, extfile.header,
                                                      fiber)
            # else we set it to None
            else:
                flat = np.ones_like(extimage)
            # --------------------------------------------------------------
            # loop around orders
            for order_num in range(nbo):
                # scale the leakage for that order to the observed amplitude
                scale = master_sci[order_num] / ref_ratio_arr[order_num]
                # correct for the flat (in E2DS case) - master is E2DSFF
                scale = scale * flat[order_num]
                # apply leakage scaling
                extimage = extimage - scale

            # TODO: Continue here

            # update ext file
            extfile.data = extimage

            # add to output
            outputs[fiber][extfiletype] = extfile
            leakage[fiber][extfiletype] = ratio_leak

    pass


def get_leak_master(params, header, fiber, kind, filename=None):
    # get file definition
    out_leak = core.get_file_definition(kind, params['INSTRUMENT'],
                                           kind='red')
    # get key
    key = out_leak.get_dbkey(fiber=fiber)
    # ------------------------------------------------------------------------
    # check for filename in inputs
    filename = general.get_input_files(params, 'LEAKFILE', key, header,
                                       filename)
    # ------------------------------------------------------------------------
    # load calib file
    leak, leak_file = general.load_calib_file(params, key, header,
                                                    filename=filename)
    # log which fpmaster file we are using
    WLOG(params, '', TextEntry('40-016-00028', args=[leak_file]))
    # return the master image
    return leak_file, leak


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
        outfile = recipe.outputs['LEAK_MASTER'].newcopy(recipe=recipe,
                                                        fiber=fiber)
        # construct the filename from file instance
        outfile.construct_filename(params, infile=extfile)
        # copy keys from input file
        outfile.copy_original_keys(extfile)
        # storage for cube
        cube = []
        # loop around files and get data cube
        for it in range(len(extfiles)):
            # add to cube
            cube.append(extfiles[it].data)
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
    leak2dext = params['LEAK_2D_EXTRACT_FILES']
    # get this instruments science fibers and reference fiber
    pconst = constants.pload(params['INSTRUMENT'])
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber =  pconst.FIBER_KINDS()
    all_fibers = sci_fibers + [ref_fiber]
    # get the input pp list
    rawfiles = infile.read_header_key_1d_list('KW_INFILE1', dtype=str)
    # get the preprocessed file
    ppfile = infile.intype.newcopy(recipe=recipe)
    # get the preprocessed file path
    pppath = os.path.join(params['DRS_DATA_WORKING'], params['NIGHTNAME'])
    # get the pp filename
    ppfile.set_filename(os.path.join(pppath, rawfiles[0]))
    # ------------------------------------------------------------------
    # find the extraction recipe
    extrecipe, _ = drs_startup.find_recipe(extname, params['INSTRUMENT'],
                                           mod=recipe.recipemod)
    extrecipe.drs_params = params
    # ------------------------------------------------------------------
    # storage for outputs
    extouts = recipe.outputs.keys()
    outputs = dict()
    for extout in extouts:
        outputs[extout] = dict()
    # ------------------------------------------------------------------
    # loop around fibers
    for fiber in all_fibers:
        # loop around extraction outputs
        for extout in extouts:
            # get extraction file instance
            outfile = extrecipe.outputs[extout].newcopy(recipe=extrecipe,
                                                        fiber=fiber)
            # construct filename
            outfile.construct_filename(params, infile=ppfile)
            # read 2D image (not 1D images -- these will be re-generated)
            if extout in leak2dext:
                outfile.read_file()
            # push to storage
            outputs[extout] = outfile
    # return outputs
    return outputs


# =============================================================================
# Define s1d functions
# =============================================================================
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


# =============================================================================
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
    e2dsfile.add_hkey('KW_FIBER', value=fiber)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    e2dsfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add the calibration files use
    e2dsfile = general.add_calibs_to_header(e2dsfile, props)
    # ----------------------------------------------------------------------
    # add the other calibration files used
    e2dsfile.add_hkey('KW_CDBORDP', value=orderpfile)
    e2dsfile.add_hkey('KW_CDBLOCO', value=lprops['LOCOFILE'])
    e2dsfile.add_hkey('KW_CDBSHAPEL', value=shapelocalfile)
    e2dsfile.add_hkey('KW_CDBSHAPEDX', value=shapexfile)
    e2dsfile.add_hkey('KW_CDBSHAPEDY', value=shapeyfile)
    e2dsfile.add_hkey('KW_CDBFLAT', value=flat_file)
    e2dsfile.add_hkey('KW_CDBBLAZE', value=blaze_file)
    if 'THERMALFILE' in eprops:
        e2dsfile.add_hkey('KW_CDBTHERMAL', value=eprops['THERMALFILE'])
    e2dsfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    # additional calibration keys
    if 'FIBERTYPE' in eprops:
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
    # add wave keys
    e2dsfile = wave.add_wave_keys(params, e2dsfile, wprops)
    # ----------------------------------------------------------------------
    # add berv properties to header
    e2dsfile = berv.add_berv_keys(params, e2dsfile, bprops)
    # add leakage switch to header (leakage currently not corrected)
    e2dsfile.add_hkey('KW_LEAK_CORR', value=0)
    # ----------------------------------------------------------------------
    # copy data
    e2dsfile.data = eprops['E2DS']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsfile.filename]
    WLOG(params, '', TextEntry('40-016-00005', args=wargs))
    # write image to file
    e2dsfile.write_file()
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
    e2dsfffile.write_file()
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
    e2dsllfile.write_file()
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
    s1dwfile.write_file()
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
    s1dvfile.write_file()
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



def qc_leak_master(params, medcubes):
    # output storage
    qc_params = dict()
    passed = True
    # loop around fibers
    for fiber in medcubes:
        # log that we are doing qc for a specific fiber
        WLOG(params, 'info', TextEntry('40-016-00026', args=[fiber]))
        # set passed variable and fail message list
        fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # no quality control currently
        qc_values.append('None')
        qc_names.append('None')
        qc_logic.append('None')
        qc_pass.append(1)
        # ------------------------------------------------------------------
        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if np.sum(qc_pass) == len(qc_pass):
            WLOG(params, 'info', TextEntry('40-005-10001'))
            passed_fiber = 1
        else:
            for farg in fail_msg:
                WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
            passed_fiber = 0
        # store in qc_params
        qc_params_fiber = [qc_names, qc_values, qc_logic, qc_pass]
        # append to storage
        qc_params[fiber] = qc_params_fiber
        passed &= passed_fiber
    # return qc_params and passed
    return qc_params, passed


def qc_leak(params, outputs):
    # output storage
    qc_params = dict()
    passed = True
    # loop around fibers
    for fiber in outputs:
        # log that we are doing qc for a specific fiber
        WLOG(params, 'info', TextEntry('40-016-00026', args=[fiber]))
        # set passed variable and fail message list
        fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # no quality control currently
        qc_values.append('None')
        qc_names.append('None')
        qc_logic.append('None')
        qc_pass.append(1)
        # ------------------------------------------------------------------
        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if np.sum(qc_pass) == len(qc_pass):
            WLOG(params, 'info', TextEntry('40-005-10001'))
            passed_fiber = 1
        else:
            for farg in fail_msg:
                WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
            passed_fiber = 0
        # store in qc_params
        qc_params_fiber = [qc_names, qc_values, qc_logic, qc_pass]
        # append to storage
        qc_params[fiber] = qc_params_fiber
        passed &= passed_fiber
    # return qc_params and passed
    return qc_params, passed


def write_leak_master(params, recipe, rawfiles, medcubes, qc_params):
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
        # add qc parameters
        outfile.add_qckeys(qc_params_fiber)
        # log that we are saving rotated image
        wargs = [fiber, outfile.filename]
        WLOG(params, '', TextEntry('40-016-00025', args=wargs))
        # write image to file
        outfile.write_file()
        # add to output files (for indexing)
        recipe.add_output_file(outfile)
        # update med cubes (as it was shallow copied this is just for sanity
        #    check)
        medcubes[fiber] = outfile
    # return medcubes
    return medcubes


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

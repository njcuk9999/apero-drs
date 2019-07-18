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
from scipy.signal import medfilt

from terrapipe import core
from terrapipe.core import constants
from terrapipe.core import math
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.io import drs_data
from terrapipe.science.calib import localisation
from terrapipe.science.calib import shape
from terrapipe.science.calib import wave
from terrapipe.science.calib import general

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
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def order_profiles(params, recipe, infile, fibertypes, shapelocal, shapex,
                   shapey, orderpfile):

    # get header from infile
    header = infile.header
    # storage for order profiles
    orderprofiles = dict()
    # loop around fibers
    for fiber in fibertypes:
        # log progress (straightening orderp)
        WLOG(params, 'info', TextEntry('40-016-00003', args=[fiber]))
        # construct order profile file
        orderpsfile = orderpfile.newcopy(recipe=recipe, fiber=fiber)
        orderpsfile.construct_filename(params, infile=infile)
        # check if temporary file exists
        if orderpsfile.file_exists():
            # load the numpy temporary file
            orderpsfile.read(params)
            # push data into orderp
            orderp = orderpsfile.data
        # load the order profile
        else:
            # load using localisation load order profile function
            out = localisation.load_orderp(params, header, fiber=fiber)
            # straighten orders
            orderp = shape.ea_transform(params, out[1], shapelocal,
                                        dxmap=shapex, dymap=shapey)
            # push into orderpsfile
            orderpsfile.data = orderp
            # save for use later
            orderpsfile.write(params)
        # store in storage dictionary
        orderprofiles[fiber] = orderp
    # return order profiles
    return orderprofiles


def thermal_correction(params, recipe, header, props=None, eprops=None,
                       **kwargs):

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
    fiber = pcheck(params, 'FIBER', 'fiber', kwargs, func_name)
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
    corrtype2 = pcheck(params, 'THERMAL_CORRETION_TYPE1', 'corrtype1', kwargs,
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
    mwavefile = wave.get_masterwave_filename(params)
    # get master wave map
    wprops = wave.get_wavesolution(params, recipe, filename=mwavefile)
    # get the wave solution
    wavemap = wprops['WAVEMAP']

    # ----------------------------------------------------------------------
    # thermal correction kwargs
    tkwargs = dict(header=header, fiber=fiber, wavemap=wavemap,
                   tapas_thres=tapas_thres, envelope=envelope,
                   filter_wid=filter_wid, torder=torder,
                   red_limit=red_limt, blue_limit=blue_limit,
                   thermal_file=thermal_file)
    # base thermal correction on fiber type
    if fibertype in corrtype1:
        thermalfile, e2ds = tcorrect1(params, e2ds, **tkwargs)
        _, e2dsff = tcorrect1(params, e2dsff, flat=flat, **tkwargs)
    elif fibertype in corrtype2:
        thermalfile, e2ds = tcorrect2(params, e2ds, **tkwargs)
        _, e2dsff = tcorrect2(params, e2dsff, flat=flat, **tkwargs)
    else:
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


def get_thermal(params, header, fiber=None, filename=None):
    # get fiber if None
    if fiber is None:
        fiber = params['FIBER']
    # get file definition
    out_thermal = core.get_file_definition('THERMAL_E2DS', params['INSTRUMENT'],
                                           kind='red')
    # get key
    key = out_thermal.get_dbkey(fiber=fiber)
    # load calib file
    thermal, thermal_file = general.load_calib_file(params, key, header,
                                                    filename=filename)
    # log which fpmaster file we are using
    WLOG(params, '', TextEntry('40-014-00031', args=[thermal_file]))
    # return the master image
    return thermal_file, thermal


def tcorrect1(params, image, header, fiber, wavemap, flat=None, **kwargs):
    # get parameters from skwargs
    tapas_thres = kwargs.get('tapas_thres', None)
    filter_wid = kwargs.get('filter_wid', None)
    torder = kwargs.get('torder', None)
    red_limit = kwargs.get('red_limt', None)
    thermal_file = kwargs.get('thermal_file', None)
    tapas_file = kwargs.get('tapas_file', None)
    # ----------------------------------------------------------------------
    # get thermal
    thermalfile, thermal = get_thermal(params, header, fiber=fiber,
                                       filename=thermal_file)
    # ----------------------------------------------------------------------
    # if we have a flat we should apply it to the thermal
    if flat is not None:
        thermal = thermal / flat
    # ----------------------------------------------------------------------
    # deal with rare case that thermal is all zeros
    if np.nansum(thermal) == 0 or np.sum(np.isfinite(thermal)) == 0:
        return thermalfile, image
    # ----------------------------------------------------------------------
    # load tapas
    tapas = drs_data.load_tapas(params, filename=tapas_file)
    wtapas, ttapas = tapas['wavelength'], tapas['trans_combined']
    # ----------------------------------------------------------------------
    # splining tapas onto the order 49 wavelength grid
    sptapas = math.iuv_spline(wtapas, ttapas)
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
        thermal[order_num] = medfilt(thermal[order_num], filter_wid)

    # we find the median scale between the observation and the thermal
    #    background in domains where there is no transmission
    thermal_torder = thermal[torder, torder_mask]
    image_torder = image[torder, torder_mask]
    ratio = np.nanmedian(thermal_torder / image_torder)
    # scale thermal by ratio
    thermal = thermal / ratio
    # ----------------------------------------------------------------------
    # plot debug plot
    if params['DRS_DEBUG'] > 0 and params['DRS_PLOT'] > 0:
        # TODO: Handle plots
        pass
        # data = [wavemap, image, thermal, torder, torder_mask]
        # sPlt.thermal_background_debug_plot(p, *data, fiber=fiber)
    # ----------------------------------------------------------------------
    # correct image
    corrected_image = image - thermal
    # ----------------------------------------------------------------------
    # return p and corrected image
    return thermalfile, corrected_image


def tcorrect2(params, image, header, fiber, wavemap, flat=None, **kwargs):

    envelope_percent = kwargs.get('envelope', None)
    filter_wid = kwargs.get('filter_wid', None)
    torder = kwargs.get('torder', None)
    red_limit = kwargs.get('red_limt', None)
    blue_limit = kwargs.get('blue_limit', None)
    thermal_file = kwargs.get('thermal_file', None)
    # get the shape
    dim1, dim2 = image.shape
    # ----------------------------------------------------------------------
    # get thermal
    thermalfile, thermal = get_thermal(params, header, fiber=fiber,
                                       filename=thermal_file)
    # ----------------------------------------------------------------------
    # if we have a flat we should apply it to the thermal
    if flat is not None:
        thermal = thermal / flat
    # ----------------------------------------------------------------------
    # deal with rare case that thermal is all zeros
    if np.nansum(thermal) == 0 or np.sum(np.isfinite(thermal)) == 0:
        return thermalfile, image
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
        envelope[x_it] = np.nanpercentile(imagebox, envelope_percent)
    # ----------------------------------------------------------------------
    # median filter the thermal (loop around orders)
    for order_num in range(dim1):
        thermal[order_num] = medfilt(thermal[order_num], filter_wid)
    # ----------------------------------------------------------------------
    # only keep wavelength in range of thermal limits
    wavemask = (wavemap[torder] > blue_limit) & (wavemap[torder] < red_limit)
    # we find the median scale between the observation and the thermal
    #    background in domains where there is no transmission
    thermal_torder = thermal[torder, wavemask]
    envelope_torder = envelope[wavemask]
    ratio = np.nanmedian(thermal_torder / envelope_torder)
    # scale thermal by ratio
    thermal = thermal / ratio
    # ----------------------------------------------------------------------
    # plot debug plot
    if params['DRS_DEBUG'] > 0 and params['DRS_PLOT'] > 0:
        # TODO: deal with plotting
        pass
        # data = [wavemap, image, thermal, torder, wavemask]
        # sPlt.thermal_background_debug_plot(p, *data, fiber=fiber)
    # ----------------------------------------------------------------------
    # correct image
    corrected_image = image - thermal
    # ----------------------------------------------------------------------
    # return p and corrected image
    return thermalfile, corrected_image


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

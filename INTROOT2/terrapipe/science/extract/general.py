#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-09 at 13:42

@author: cook
"""
from __future__ import division

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.science.calib import localisation
from terrapipe.science.calib import shape
from terrapipe.science.calib import wave

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
    dprtype = pcheck(props, 'DPRTYPE', 'dprtype', kwargs, func_name)
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
    e2ds = pcheck(eprops, 'E2DS', 'e2ds', kwargs, func_name)
    e2dsff = pcheck(eprops, 'E2DSFF', 'e2dsff', kwargs, func_name)
    flat = pcheck(eprops, 'FLAT')
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
    if fibertype in params['THERMAL_CORRETION_TYPE1']:
        thermalfile, e2ds = tcorrect1(e2ds, **tkwargs)
        _, e2dsff = tcorrect1(e2dsff, flat=flat, **tkwargs)

    elif fibertype in params['THERMAL_CORRECTION_TYPE2']:
        thermalfile, e2ds = tcorrect2(e2ds, **tkwargs)
        _, e2dsff = tcorrect2(e2dsff, flat=flat, **tkwargs)
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



    return filename, thermal


def tcorrect1(params, image, header, fiber, wavemap, flat=None, **kwargs):
    # get parameters from skwargs
    tapas_thres = kwargs.get('tapas_thres', None)
    envelope = kwargs.get('envelope', None)
    filter_wid = kwargs.get('filter_wid', None)
    torder = kwargs.get('torder', None)
    red_limit = kwargs.get('red_limt', None)
    blue_limit = kwargs.get('blue_limit', None)
    thermal_file = kwargs.get('thermal_file', None)
    # ----------------------------------------------------------------------
    # get thermal
    thermalfile, thermal = get_thermal(params, header, fiber=fiber,
                                       filename=thermal_file)
    # ----------------------------------------------------------------------
    # if we have a flat we should apply it to the thermal

    return 1

def tcorrect2(params, image, header, fiber, wavemap, flat=None, **kwargs):

    tapas_thres = kwargs.get('tapas_thres', None)
    envelope = kwargs.get('envelope', None)
    filter_wid = kwargs.get('filter_wid', None)
    torder = kwargs.get('torder', None)
    red_limit = kwargs.get('red_limt', None)
    blue_limit = kwargs.get('blue_limit', None)
    thermal_file = kwargs.get('thermal_file', None)


    return 1


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

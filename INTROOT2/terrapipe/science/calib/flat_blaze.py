#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-10 at 09:30

@author: cook
"""
from __future__ import division
import numpy as np
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core import math as mp
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.science.calib import general

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.extraction.py'
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
def calculate_blaze_flat(e2ds, flux, blaze_cut, blaze_deg):
    # ----------------------------------------------------------------------
    # remove edge of orders at low S/N
    # ----------------------------------------------------------------------
    with warnings.catch_warnings(record=True) as _:
        blazemask = e2ds < (flux / blaze_cut)
        e2ds[blazemask] = np.nan
    # ----------------------------------------------------------------------
    # measure the blaze (with polynomial fit)
    # ----------------------------------------------------------------------
    # get x position values
    xpix = np.arange(len(e2ds))
    # find all good pixels
    good = np.isfinite(e2ds)
    # do poly fit on good values
    coeffs = mp.nanpolyfit(xpix[good], e2ds[good], deg=blaze_deg)
    # fit all positions based on these fit coefficients
    blaze = np.polyval(coeffs, xpix)
    # blaze is not usable outside mask range to do this we convole with a
    #   width=1 tophat (this will remove any cluster of pixels that has 2 or
    #   less points and is surrounded by NaN values
    # find minimum/maximum position of convolved blaze
    nanxpix = np.array(xpix).astype(float)
    nanxpix[~good] = np.nan
    minpos, maxpos = mp.nanargmin(nanxpix), mp.nanargmax(nanxpix)

    # TODO: need a way to remove cluster of pixels that are outliers above
    # TODO:    the cut off (blaze mask region)

    # set these bad values to NaN
    blaze[:minpos] = np.nan
    blaze[maxpos:] = np.nan

    # ----------------------------------------------------------------------
    #  calcaulte the flat
    # ----------------------------------------------------------------------
    with warnings.catch_warnings(record=True) as _:
        flat = e2ds / blaze

    # ----------------------------------------------------------------------
    # calculate the rms
    # ----------------------------------------------------------------------
    rms = mp.nanstd(flat)

    # ----------------------------------------------------------------------
    # return values
    return e2ds, flat, blaze, rms


def get_flat(params, header, fiber):
    # get file definition
    out_shape_dymap = core.get_file_definition('FF_FLAT', params['INSTRUMENT'],
                                               kind='red')
    # get key
    key = out_shape_dymap.get_dbkey(fiber=fiber)
    # load calib file
    flat, flat_file = general.load_calib_file(params, key, header)
    # log which fpmaster file we are using
    WLOG(params, '', TextEntry('40-015-00006', args=[flat_file]))
    # return the master image
    return flat_file, flat


def get_blaze(params, header, fiber):
    # get file definition
    out_shape_dymap = core.get_file_definition('FF_BLAZE', params['INSTRUMENT'],
                                               kind='red')
    # get key
    key = out_shape_dymap.get_dbkey(fiber=fiber)
    # load calib file
    blaze, blaze_file = general.load_calib_file(params, key, header)
    # log which fpmaster file we are using
    WLOG(params, '', TextEntry('40-015-00007', args=[blaze_file]))
    # return the master image
    return blaze_file, blaze


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

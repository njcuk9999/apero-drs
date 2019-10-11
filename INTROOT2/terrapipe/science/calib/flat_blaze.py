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
# Define write and qc functions
# =============================================================================
def flat_blaze_qc(params, eprops, fiber):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], [],
    qc_logic, qc_pass = [], []
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # --------------------------------------------------------------
    # check that rms values in required orders are below threshold

    # get mask for removing certain values
    remove_orders = params.listp('FF_RMS_SKIP_ORDERS', dtype=int)
    remove_orders = np.array(remove_orders)
    remove_mask = np.in1d(np.arange(len(eprops['RMS'])), remove_orders)
    # apply max and calculate the maximum of the rms values
    max_rms = mp.nanmax(eprops['RMS'][~remove_mask])
    # apply the quality control based on the maximum rms
    if max_rms > params['QC_FF_MAX_RMS']:
        # add failed message to fail message list
        fargs = [fiber, max_rms, params['QC_FF_MAX_RMS']]
        fail_msg.append(textdict['40-015-00008'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(max_rms)
    qc_names.append('max_rms')
    qc_logic.append('max_rms < {0:.2f}'.format(params['QC_FF_MAX_RMS']))
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
    # return qc params
    return qc_params, passed


def flat_blaze_write(params, recipe, infile, eprops, fiber, rawfiles, combine,
                     props, lprops, orderpfile, shapelocalfile, shapexfile,
                     shapeyfile, qc_params):
    # --------------------------------------------------------------
    # Store Blaze in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file
    blazefile = recipe.outputs['BLAZE_FILE'].newcopy(recipe=recipe,
                                                     fiber=fiber)
    # construct the filename from file instance
    blazefile.construct_filename(params, infile=infile)
    # define header keys for output file
    # copy keys from input file
    blazefile.copy_original_keys(infile)
    # add version
    blazefile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    blazefile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    blazefile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    blazefile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    blazefile.add_hkey('KW_OUTPUT', value=blazefile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    blazefile.add_hkey_1d('KW_INFILE1', values=hfiles,
                          dim1name='file')
    # add qc parameters
    blazefile.add_qckeys(qc_params)
    # add the calibration files use
    blazefile = general.add_calibs_to_header(blazefile, props)
    # --------------------------------------------------------------
    # add the other calibration files used
    blazefile.add_hkey('KW_CDBORDP', value=orderpfile)
    blazefile.add_hkey('KW_CDBLOCO', value=lprops['LOCOFILE'])
    blazefile.add_hkey('KW_CDBSHAPEL', value=shapelocalfile)
    blazefile.add_hkey('KW_CDBSHAPEDX', value=shapexfile)
    blazefile.add_hkey('KW_CDBSHAPEDY', value=shapeyfile)
    # --------------------------------------------------------------
    # add SNR parameters to header
    blazefile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                          dim1name='order')
    # add start and end extraction order used
    blazefile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
    blazefile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
    # add extraction ranges used
    blazefile.add_hkey('KW_EXT_RANGE1', value=eprops['RANGE1'])
    blazefile.add_hkey('KW_EXT_RANGE2', value=eprops['RANGE2'])
    # add cosmic parameters used
    blazefile.add_hkey('KW_COSMIC', value=eprops['COSMIC'])
    blazefile.add_hkey('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'])
    blazefile.add_hkey('KW_COSMIC_THRES',
                       value=eprops['COSMIC_THRESHOLD'])
    # add blaze parameter used
    blazefile.add_hkey('KW_BLAZE_WID', value=eprops['BLAZE_SIZE'])
    blazefile.add_hkey('KW_BLAZE_CUT', value=eprops['BLAZE_CUT'])
    blazefile.add_hkey('KW_BLAZE_DEG', value=eprops['BLAZE_DEG'])
    # add saturation parameters used
    blazefile.add_hkey('KW_SAT_QC', value=eprops['SAT_LEVEL'])
    with warnings.catch_warnings(record=True) as _:
        max_sat_level = mp.nanmax(eprops['FLUX_VAL'])
    blazefile.add_hkey('KW_SAT_LEVEL', value=max_sat_level)
    # --------------------------------------------------------------
    # copy data
    blazefile.data = eprops['BLAZE']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '',
         TextEntry('40-015-00003', args=[blazefile.filename]))
    # write image to file
    blazefile.write()
    # add to output files (for indexing)
    recipe.add_output_file(blazefile)
    # --------------------------------------------------------------
    # Store Flat-field in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file
    flatfile = recipe.outputs['FLAT_FILE'].newcopy(recipe=recipe,
                                                   fiber=fiber)
    # construct the filename from file instance
    flatfile.construct_filename(params, infile=infile)
    # copy header from blaze file
    flatfile.copy_hdict(blazefile)
    # set output key
    flatfile.add_hkey('KW_OUTPUT', value=flatfile.name)
    # copy data
    flatfile.data = eprops['FLAT']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '',
         TextEntry('40-015-00004', args=[flatfile.filename]))
    # write image to file
    flatfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(flatfile)
    # --------------------------------------------------------------
    # Store E2DSLL in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file
    e2dsllfile = recipe.outputs['E2DSLL_FILE'].newcopy(recipe=recipe,
                                                       fiber=fiber)
    # construct the filename from file instance
    e2dsllfile.construct_filename(params, infile=infile)
    # copy header from blaze file
    e2dsllfile.copy_hdict(blazefile)
    # set output key
    e2dsllfile.add_hkey('KW_OUTPUT', value=e2dsllfile.name)
    # copy data
    e2dsllfile.data = eprops['E2DSLL']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '',
         TextEntry('40-015-00005', args=[e2dsllfile.filename]))
    # write image to file
    e2dsllfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(e2dsllfile)
    # return out file
    return blazefile, flatfile


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

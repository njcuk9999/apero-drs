#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-10 at 09:30

@author: cook
"""
import numpy as np
from scipy.optimize import curve_fit
from typing import Union
import warnings

from apero.base import base
from apero.core import constants
from apero import lang
from apero.core import math as mp
from apero.core.core import drs_log, drs_file
from apero.core.core import drs_database
from apero.science.calib import gen_calib

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.extraction.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
def calculate_blaze_flat_sinc(params: ParamDict, e2ds_ini: np.ndarray,
                              peak_cut: float, badpercentile: float,
                              order_num: int, fiber: str,
                              sinc_med_size: Union[int, None] = None):
    """
    Calculate the blaze function using a sinc function

    :param params:
    :param e2ds_ini:
    :param peak_cut:
    :param badpercentile:
    :param order_num:
    :param fiber:
    :param sinc_med_size:
    :return:
    """
    # get function name
    func_name = __NAME__ + '.calculate_blaze_flat_sinc()'
    # get med filt parameter
    med_size = pcheck(params, 'FF_BLAZE_SINC_MED_SIZE', func=func_name,
                      override=sinc_med_size)
    # ----------------------------------------------------------------------
    # defnie the x positions
    xpix = np.arange(len(e2ds_ini))
    # ------------------------------------------------------------------
    # Need to median filter the e2ds here as we want to fit the shape not
    #   individual line shapes for the blaze
    e2ds = mp.medfilt_1d(e2ds_ini, med_size)
    # region over which we will fit
    keep = np.isfinite(e2ds)
    # keep only regions that make sense compared to the 95th percentile
    #   max would be affected by outliers
    with warnings.catch_warnings(record=True) as _:
        keep &= e2ds > 0.05 * np.nanpercentile(e2ds, 95)
        keep &= e2ds < 2 * np.nanpercentile(e2ds, 95)
    # ------------------------------------------------------------------
    # guess of peak value, we do not take the max as there may be a
    #     hot/bad pix in the order
    thres = np.nanpercentile(e2ds, badpercentile)
    # ------------------------------------------------------------------
    # how many points above 50% of peak value?
    # The period should be a factor of about 2.0 more than the domain
    # that is above the 5th percentile
    nthres = mp.nansum(e2ds[keep] > thres / 2.0)
    # median position of points above threshold
    with warnings.catch_warnings(record=True) as _:
        pospeak = mp.nanmedian(xpix[e2ds > thres])
    # bounds
    # with warnings.catch_warnings(record=True) as _:
    #     xlower = mp.nanmin(xpix[e2ds > thres])
    #     xupper = mp.nanmax(xpix[e2ds > thres])
    # ------------------------------------------------------------------
    # starting point for the fit to the blaze sinc model
    # we start with :
    #
    # peak value is == threshold percentile
    # period of sinc is == 2x the width of pixels above 50% of the peak
    # the peak position is == the median x value of pixels above
    #                         95th percent.
    # no quadratic term
    # no SED slope
    fit_guess = [thres, nthres * 2.0, pospeak, 0, 0, 0]
    # ------------------------------------------------------------------
    # we set reasonable bounds
    # bounds = [(thres * 0.5, 0.0, 0.0, -np.inf, -np.inf, -1e-2),
    #           (thres * 1.5, np.inf, np.max(xpix), np.inf, np.inf, 1e-2)]
    # pass without DC and SLOPE
    bounds = [(0, 0.0, 0.0, -np.inf, -np.inf, -1e-20),
              (thres * 1.5, np.inf, np.max(xpix), np.inf, np.inf, 1e-20)]
    # set a counter
    n_it = -1
    # ------------------------------------------------------------------
    # try to fit and if there is a failure catch it
    try:
        # we optimize over pixels that are not NaN
        popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=fit_guess,
                               bounds=bounds)
        # we then re-fit to avoid local minima (this has happened - fitting
        #   a second time seemed to fix this - when the guess is off)
        popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=popt,
                               bounds=bounds)
    except RuntimeError as _:
        # if it failed with bounds try without bounds
        try:
            # we optimize over pixels that are not NaN (this time with no bounds)
            popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                   p0=fit_guess)
            # we then re-fit to avoid local minima (this has happened - fitting
            #   a second time seemed to fix this - when the guess is off)
            popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=popt)
        except RuntimeError as _:
            # finally try without the cubic term
            try:
                fit_guess = fit_guess[:5]
                # we optimize over pixels that are not NaN (this time with
                #    no bounds)
                popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                       p0=fit_guess)
            except RuntimeError as e:
                strlist = ('amp={0} period={1} lin={2} slope={3} quad={4} '
                           'cube={5} ')
                strguess = strlist.format(*fit_guess)
                strlower = strlist.format(*bounds[0])
                strupper = strlist.format(*bounds[1])
                eargs = [order_num, fiber, n_it, strguess, strlower, strupper,
                         type(e), str(e), func_name]
                WLOG(params, 'error', textentry('40-015-00009', args=eargs))
                return
    # ------------------------------------------------------------------
    # calculate the blaze from the curve_fit coefficients
    blaze = mp.sinc(xpix, *popt, peak_cut=peak_cut)
    # ----------------------------------------------------------------------
    # remove nan in the blaze also in the e2ds
    # ----------------------------------------------------------------------
    blazemask = np.isnan(blaze)
    e2ds_ini[blazemask] = np.nan
    # calculate the flat
    with warnings.catch_warnings(record=True) as _:
        flat = e2ds_ini / blaze
    # ----------------------------------------------------------------------
    # calculate the rms
    # ----------------------------------------------------------------------
    rms = mp.robust_nanstd(flat[keep])
    # remove any very large outliers (set to NaN)
    with warnings.catch_warnings(record=True) as _:
        flat[np.abs(flat - 1) > 10 * rms] = np.nan
    # ----------------------------------------------------------------------
    # return values
    return e2ds_ini, flat, blaze, rms


def get_flat(params, header, fiber, filename=None, quiet=False, database=None):
    # get file definition
    out_flat = drs_file.get_file_definition(params, 'FF_FLAT', block_kind='red')
    # get key
    key = out_flat.get_dbkey()
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------------
    # load flat file
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, key, header, filename=filename,
                          userinputkey='FLATFILE', database=calibdbm,
                          fiber=fiber)
    # get properties from calibration file
    flat = cfile.data
    flat_file = cfile.filename
    flat_time = cfile.mjdmid
    # ------------------------------------------------------------------------
    # log which fpmaster file we are using
    if not quiet:
        WLOG(params, '', textentry('40-015-00006', args=[flat_file]))
    # return the master image
    return flat_file, flat_time, flat


def get_blaze(params, header, fiber, filename=None, database=None):
    # get file definition
    out_blaze = drs_file.get_file_definition(params, 'FF_BLAZE',
                                             block_kind='red')
    # get key
    key = out_blaze.get_dbkey()
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------------
    # load blaze file
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, key, header, filename=filename,
                          userinputkey='BLAZEFILE', database=calibdbm,
                          fiber=fiber)
    # get properties from calibration file
    blaze = cfile.data
    blaze_file = cfile.filename
    blaze_time = cfile.mjdmid
    # ------------------------------------------------------------------------
    # log which fpmaster file we are using
    WLOG(params, '', textentry('40-015-00007', args=[blaze_file]))
    # return the master image
    return blaze_file, blaze_time, blaze


# =============================================================================
# Define write and qc functions
# =============================================================================
def flat_blaze_qc(params, eprops, fiber):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], [],
    qc_logic, qc_pass = [], []
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
        fail_msg.append(textentry('40-015-00008', args=fargs))
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
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc params
    return qc_params, passed


def flat_blaze_write(params, recipe, infile, eprops, fiber, rawfiles, combine,
                     props, lprops, sprops, qc_params):
    # --------------------------------------------------------------
    # Store Blaze in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file
    blazefile = recipe.outputs['BLAZE_FILE'].newcopy(params=params,
                                                     fiber=fiber)
    # construct the filename from file instance
    blazefile.construct_filename(infile=infile)
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
    blazefile.add_hkey('KW_FIBER', value=fiber)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    blazefile.add_hkey_1d('KW_INFILE1', values=hfiles,
                          dim1name='file')
    # set in files
    blazefile.infiles = list(hfiles)
    # add qc parameters
    blazefile.add_qckeys(qc_params)
    # add the calibration files use
    blazefile = gen_calib.add_calibs_to_header(blazefile, props)
    # --------------------------------------------------------------
    # add the other calibration files used
    blazefile.add_hkey('KW_CDBORDP', value=lprops['ORDERPFILE'])
    blazefile.add_hkey('KW_CDTORDP', value=lprops['ORDERPTIME'])
    blazefile.add_hkey('KW_CDBLOCO', value=lprops['LOCOFILE'])
    blazefile.add_hkey('KW_CDTLOCO', value=lprops['LOCOTIME'])
    blazefile.add_hkey('KW_CDBSHAPEL', value=sprops['SHAPELFILE'])
    blazefile.add_hkey('KW_CDTSHAPEL', value=sprops['SHAPELTIME'])
    blazefile.add_hkey('KW_CDBSHAPEDX', value=sprops['SHAPEXFILE'])
    blazefile.add_hkey('KW_CDTSHAPEDX', value=sprops['SHAPEXTIME'])
    blazefile.add_hkey('KW_CDBSHAPEDY', value=sprops['SHAPEYFILE'])
    blazefile.add_hkey('KW_CDTSHAPEDY', value=sprops['SHAPEYTIME'])
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
    # add blaze sinc parameters used
    blazefile.add_hkey('KW_BLAZE_SCUT', value=eprops['BLAZE_SCUT'])
    blazefile.add_hkey('KW_BLAZE_BPRCNTL', value=eprops['BLAZE_BPERCENTILE'])
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
    WLOG(params, '', textentry('40-015-00003', args=[blazefile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=blazefile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    blazefile.write_multi(data_list=data_list, name_list=name_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(blazefile)
    # --------------------------------------------------------------
    # Store Flat-field in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file
    flatfile = recipe.outputs['FLAT_FILE'].newcopy(params=params,
                                                   fiber=fiber)
    # construct the filename from file instance
    flatfile.construct_filename(infile=infile)
    # copy header from blaze file
    flatfile.copy_hdict(blazefile)
    # set in files
    flatfile.infiles = list(hfiles)
    # set output key
    flatfile.add_hkey('KW_OUTPUT', value=flatfile.name)
    # copy data
    flatfile.data = eprops['FLAT']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-015-00004', args=[flatfile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=blazefile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    flatfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(flatfile)
    # --------------------------------------------------------------
    # Store E2DSLL in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file
    e2dsllfile = recipe.outputs['E2DSLL_FILE'].newcopy(params=params,
                                                       fiber=fiber)
    # construct the filename from file instance
    e2dsllfile.construct_filename(infile=infile)
    # copy header from blaze file
    e2dsllfile.copy_hdict(blazefile)
    # set in files
    e2dsllfile.infiles = list(hfiles)
    # set output key
    e2dsllfile.add_hkey('KW_OUTPUT', value=e2dsllfile.name)
    # copy data
    e2dsllfile.data = eprops['E2DSLL']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '',
         textentry('40-015-00005', args=[e2dsllfile.filename]))
    # define multi lists
    data_list, name_list = [eprops['E2DSCC']], ['E2DSLL', 'E2DSCC']
    datatype_list = ['image']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsllfile)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write image to file
    e2dsllfile.write_multi(data_list=data_list, name_list=name_list,
                           datatype_list=datatype_list,
                           block_kind=recipe.out_block_str,
                           runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(e2dsllfile)
    # return out file
    return blazefile, flatfile


def flat_blaze_summary(recipe, params, qc_params, eprops, fiber):
    # alias to eprops
    epp = eprops
    # add qc params (fiber specific)
    recipe.plot.add_qc_params(qc_params, fiber=fiber)
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'], fiber=fiber)
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'], fiber=fiber)
    recipe.plot.add_stat('KW_EXT_START', value=epp['START_ORDER'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_END', value=epp['END_ORDER'], fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE1', value=epp['RANGE1'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE2', value=epp['RANGE2'], fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC', value=epp['COSMIC'], fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_CUT', value=epp['COSMIC_SIGCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_THRES', fiber=fiber,
                         value=epp['COSMIC_THRESHOLD'])
    # add blaze sinc parameters used
    recipe.plot.add_stat('KW_BLAZE_SCUT', value=eprops['BLAZE_SCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_BPRCNTL', value=eprops['BLAZE_BPERCENTILE'],
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

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
import warnings

from apero.base import base
from apero.core import constants
from apero import lang
from apero.core import math as mp
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_file
from apero.core.utils import drs_database2 as drs_database
from apero.science.calib import general

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
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
# TODO: not used!
def calculate_blaze_flat(e2ds, flux, blaze_cut, blaze_deg):
    """
    do not use -- old function here for comparison
    :param e2ds:
    :param flux:
    :param blaze_cut:
    :param blaze_deg:
    :return:
    """
    # do not use -- old function here for comparison
    args = [__NAME__ + '.calculate_blaze_flat_sinc()']
    warnings.warn('Do not use - Use {0} instead'.format(*args))
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


def calculate_blaze_flat_sinc(params, e2ds_ini, peak_cut, nsigfit, badpercentile,
                              order_num, fiber, niter=2,):
    # get function name
    func_name = __NAME__ + '.calculate_blaze_flat_sinc()'
    # ----------------------------------------------------------------------
    # defnie the x positions
    xpix = np.arange(len(e2ds_ini))
    # ------------------------------------------------------------------

    e2ds = mp.medfilt_1d(e2ds_ini,15)

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
    with warnings.catch_warnings(record=True) as _:
        xlower = mp.nanmin(xpix[e2ds > thres])
        xupper = mp.nanmax(xpix[e2ds > thres])
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
    bounds = [ (0, 0.0, 0.0, -np.inf, -1e-20, -np.inf),
               (thres * 1.5, np.inf, np.max(xpix), np.inf, 1e-20, np.inf)]
    # set a counter
    n_it = -1
    # ------------------------------------------------------------------
    # try to fit and if there is a failure catch it
    try:
        # we optimize over pixels that are not NaN
        #popt0, pcov0 = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=fit_guess,
        #                         method='dogbox', bounds=bounds)
        # set the first guess for the full fit to the fit without slope and
        #   quadratic terms
        #fit_guess = popt0
        # set the quad, cube and slope to zero (pass without DC and SLOPE)
        #fit_guess[[3, 4, 5]] = 0.0

        # we optimize over pixels that are not NaN (this time with no bounds)
        popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=fit_guess,
                               bounds = bounds)
        # ------------------------------------------------------------------
        # set the model to zeros at first
        blaze = mp.sinc(xpix, popt[0], popt[1], popt[2], popt[3], popt[4],
                        popt[5], peak_cut=peak_cut)

        # # now we iterate using a sigma clip
        # for n_it in range(niter):
        #     # we construct a model with the peak cut-off
        #     blaze = mp.sinc(xpix, popt[0], popt[1], popt[2], popt[3], popt[4],
        #                     popt[5], peak_cut=peak_cut)
        #     # we find residuals to the fit and normalize them
        #     residual = (e2ds - blaze)
        #     residual /= mp.nanmedian(np.abs(residual))
        #     # we keep only non-NaN model points (i.e. above peak_cut) and
        #     # within +- Nsigfit dispersion elements
        #     with warnings.catch_warnings(record=True) as _:
        #         keep = (np.abs(residual) < nsigfit) & np.isfinite(blaze)
        #     popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
        #                            p0=fit_guess) #, bounds=bounds)
    except RuntimeError as e:
        # if it failed with bounds try without bounds
        try:
            # we optimize over pixels that are not NaN (this time with no bounds)
            popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                   p0=fit_guess)
            # ------------------------------------------------------------------
            # set the model to zeros at first
            blaze = mp.sinc(xpix, popt[0], popt[1], popt[2], popt[3], popt[4],
                            popt[5], peak_cut=peak_cut)

        except RuntimeError as e:
            strlist = 'amp={0} period={1} lin={2} quad={3} cube={4} slope={5}'
            strguess = strlist.format(*fit_guess)
            strlower = strlist.format(*bounds[0])
            strupper = strlist.format(*bounds[1])
            eargs = [order_num, fiber, n_it, strguess, strlower, strupper,
                     type(e), str(e), func_name]
            WLOG(params, 'error', TextEntry('40-015-00009', args=eargs))
            blaze = None

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
    out_flat = drs_startup.get_file_definition('FF_FLAT', params['INSTRUMENT'],
                                               kind='red')
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
    cout = general.load_calib_file(params, key, header, filename=filename,
                                   userinputkey='FLATFILE', database=calibdbm)
    flat, _, flat_file = cout
    # ------------------------------------------------------------------------
    # log which fpmaster file we are using
    if not quiet:
        WLOG(params, '', TextEntry('40-015-00006', args=[flat_file]))
    # return the master image
    return flat_file, flat


def get_blaze(params, header, fiber, filename=None, database=None):
    # get file definition
    out_blaze = drs_startup.get_file_definition('FF_BLAZE',
                                                params['INSTRUMENT'],
                                                kind='red')
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
    cout = general.load_calib_file(params, key, header, filename=filename,
                                   userinputkey='BLAZEFILE', database=calibdbm,
                                   fiber=fiber)
    blaze, _, blaze_file = cout
    # ------------------------------------------------------------------------
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
    # TODO: is blaze_size needed with sinc function?
    blazefile.add_hkey('KW_BLAZE_WID', value=eprops['BLAZE_SIZE'])
    # TODO: is blaze_cut needed with sinc function?
    blazefile.add_hkey('KW_BLAZE_CUT', value=eprops['BLAZE_CUT'])
    # TODO: is blaze_deg needed with sinc function?
    blazefile.add_hkey('KW_BLAZE_DEG', value=eprops['BLAZE_DEG'])
    # add blaze sinc parameters used
    blazefile.add_hkey('KW_BLAZE_SCUT', value=eprops['BLAZE_SCUT'])
    blazefile.add_hkey('KW_BLAZE_SIGFIG', value=eprops['BLAZE_SIGFIT'])
    blazefile.add_hkey('KW_BLAZE_BPRCNTL', value=eprops['BLAZE_BPERCENTILE'])
    blazefile.add_hkey('KW_BLAZE_NITER', value=eprops['BLAZE_NITER'])
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
    blazefile.write_file()
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
    # set output key
    flatfile.add_hkey('KW_OUTPUT', value=flatfile.name)
    # copy data
    flatfile.data = eprops['FLAT']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '',
         TextEntry('40-015-00004', args=[flatfile.filename]))
    # write image to file
    flatfile.write_file()
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
    # set output key
    e2dsllfile.add_hkey('KW_OUTPUT', value=e2dsllfile.name)
    # copy data
    e2dsllfile.data = eprops['E2DSLL']
    # --------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '',
         TextEntry('40-015-00005', args=[e2dsllfile.filename]))
    # write image to file
    e2dsllfile.write_file()
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
    # add blaze parameter used
    # TODO: is blaze_size needed with sinc function?
    recipe.plot.add_stat('KW_BLAZE_WID', value=eprops['BLAZE_SIZE'],
                         fiber=fiber)
    # TODO: is blaze_cut needed with sinc function?
    recipe.plot.add_stat('KW_BLAZE_CUT', value=eprops['BLAZE_CUT'],
                         fiber=fiber)
    # TODO: is blaze_deg needed with sinc function?
    recipe.plot.add_stat('KW_BLAZE_DEG', value=eprops['BLAZE_DEG'],
                         fiber=fiber)
    # add blaze sinc parameters used
    recipe.plot.add_stat('KW_BLAZE_SCUT', value=eprops['BLAZE_SCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_SIGFIG', value=eprops['BLAZE_SIGFIT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_BPRCNTL', value=eprops['BLAZE_BPERCENTILE'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_NITER', value=eprops['BLAZE_NITER'],
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

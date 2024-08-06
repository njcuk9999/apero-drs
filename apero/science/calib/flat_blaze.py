#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO flat and blaze calibration functionality

Created on 2019-07-10 at 09:30

@author: cook
"""
import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
from scipy.optimize import curve_fit

from apero.base import base
from apero.core import constants
from apero.core import lang
from apero.core import math as mp
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
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
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict
# Get the input fits file class
DrsFitsFile = drs_file.DrsFitsFile
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
blaze_flat_return = Tuple[np.ndarray, np.ndarray, np.ndarray, float]


def calculate_blaze_flat_sinc(params: ParamDict, e2ds_ini: np.ndarray,
                              peak_cut: float, badpercentile: float,
                              order_num: int, fiber: str,
                              sinc_med_size: Optional[int] = None
                              ) -> blaze_flat_return:
    """
    Calculate the blaze function using a sinc function

    :param params: ParamDict, parameter dictionary of constants
    :param e2ds_ini: numpy (1D) array: the extracted flux for this order
    :param peak_cut: float, the threshold expressed as the fraction of the
                     maximum peak, below this threshold the blaze is set to NaN
    :param badpercentile: float, the hot pixel percentile level
    :param order_num: int, the order number we are dealing with
    :param fiber: str, the fiber name we are dealing with
    :param sinc_med_size: int or None, optional, the sinc fit median filter
                          width, overrides params['FF_BLAZE_SINC_MED_SIZE']

    :return: tuple, 1. the updated extracted flux for this order
             2. the flat profile for this order
             3. the blaze fit for this order
             4. the rms for this order
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
        keep &= e2ds > 0.05 * mp.nanpercentile(e2ds, 95)
        keep &= e2ds < 2 * mp.nanpercentile(e2ds, 95)
    # ------------------------------------------------------------------
    # guess of peak value, we do not take the max as there may be a
    #     hot/bad pix in the order
    thres = mp.nanpercentile(e2ds, badpercentile)
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
    # -------------------------------------------------------------------------
    # try a few times (this can fix it not working)
    tries = 0
    popt, pcov = [], []
    # loop around 5 times
    while tries <= 5:
        # try to fit and if there is a failure catch it
        try:
            # we optimize over pixels that are not NaN
            # noinspection PyTupleAssignmentBalance
            popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                   p0=fit_guess, bounds=bounds)
            # we then re-fit to avoid local minima (this has happened - fitting
            #   a second time seemed to fix this - when the guess is off)
            # noinspection PyTupleAssignmentBalance
            popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=popt,
                                   bounds=bounds)
            # worked --> break while loop
            break
        except RuntimeError as _:
            # if it failed with bounds try without bounds
            try:
                # we optimize over pixels that are not NaN (this time with
                # no bounds)
                # noinspection PyTupleAssignmentBalance
                popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                       p0=fit_guess)
                # we then re-fit to avoid local minima (this has happened
                #    - fitting a second time seemed to fix this
                #    - when the guess is off)
                # noinspection PyTupleAssignmentBalance
                popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep], p0=popt)
                # worked --> break while loop
                break
            except RuntimeError as _:
                # finally try without the cubic term
                try:
                    fit_guess1 = fit_guess[:5]
                    # we optimize over pixels that are not NaN (this time with
                    #    no bounds)
                    # noinspection PyTupleAssignmentBalance
                    popt, pcov = curve_fit(mp.sinc, xpix[keep], e2ds[keep],
                                           p0=fit_guess1)
                    # worked --> break while loop
                    break
                except RuntimeError as e:
                    # try again and give warning that we are trying again
                    if tries < 5:
                        wmsg = textentry('10-015-00001', args=[tries])
                        WLOG(params, 'warning', wmsg, sublevel=2)
                        tries += 1
                    # on the 5th attempt give up
                    if tries == 5:
                        strlist = ('amp={0} period={1} lin={2} slope={3} '
                                   'quad={4} (cube={5})')
                        strguess = strlist.format(*fit_guess)
                        strlower = strlist.format(*bounds[0])
                        strupper = strlist.format(*bounds[1])
                        eargs = [order_num, fiber, n_it, strguess, strlower,
                                 strupper, type(e), str(e), func_name]
                        emsg = textentry('40-015-00009', args=eargs)
                        WLOG(params, 'error', emsg)
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
        bad_mask1 = np.abs(flat - 1) > 10 * rms
        # apply mask
        flat[bad_mask1] = np.nan
        blaze[bad_mask1] = np.nan
        e2ds_ini[bad_mask1] = np.nan
    # ----------------------------------------------------------------------
    # remove outliers within flat field to avoid division by small numbers
    #   or suspiciously large flat response
    with warnings.catch_warnings(record=True) as _:
        bad_mask2 = np.abs(1 - flat) > 0.2
        # apply mask
        flat[bad_mask2] = np.nan
        blaze[bad_mask2] = np.nan
        e2ds_ini[bad_mask1] = np.nan
    # ----------------------------------------------------------------------
    # recalculate calculate the rms
    # ----------------------------------------------------------------------
    rms = mp.robust_nanstd(flat[keep])
    # ----------------------------------------------------------------------
    # return values
    return e2ds_ini, flat, blaze, rms


def get_flat(params: ParamDict, header: Union[drs_file.Header, None],
             fiber: str, filename: Optional[str] = None, quiet: bool = False,
             database: Optional[drs_database.CalibrationDatabase] = None
             ) -> Tuple[str, float, np.ndarray]:
    """
    Get the flat calibration file from the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param header: fits Header, the fits header associated with the input
                   file (required to get closest in time) can be None if
                   filename is given
    :param fiber: str, the fiber name
    :param filename: str or None, the filename of the flat calibration to
                     load, overrides getting it from calibration database
                     header not require for this
    :param quiet: bool, whether to log/print loading messages
    :param database: CalibrationDatabase or None, if passed does not reload
                     the calibration database
    :return: tuple, 1. the flat file name used, 2. the MJD time of the flat file
             3. numpy (2D) array, the loaded flat file
    """
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
    # log which fpref file we are using
    if not quiet:
        WLOG(params, '', textentry('40-015-00006', args=[flat_file]))
    # return the reference image
    return flat_file, flat_time, flat


def get_blaze(params: ParamDict, header: Union[drs_file.Header, None],
              fiber: str, filename: Optional[str] = None,
              database: Optional[drs_database.CalibrationDatabase] = None
              ) -> Tuple[str, float, np.ndarray]:
    """
    Get the blaze calibration file from the calibration database

    :param params: ParamDict, the parameter dictionary of constants
    :param header: fits Header, the fits header associated with the input
                   file (required to get closest in time) can be None if
                   filename is given
    :param fiber: str, the fiber name
    :param filename: str or None, the filename of the blaze calibration to
                     load, overrides getting it from calibration database
                     header not require for this
    :param database: CalibrationDatabase or None, if passed does not reload
                     the calibration database
    :return: tuple, 1. the blaze file name used, 2. the MJD time of the blaze
             file 3. numpy (2D) array, the loaded blaze file
    """
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
    # log which fpref file we are using
    WLOG(params, '', textentry('40-015-00007', args=[blaze_file]))
    # return the reference image
    return blaze_file, blaze_time, blaze


# =============================================================================
# Define write and qc functions
# =============================================================================
def flat_blaze_qc(params: ParamDict, eprops: ParamDict, fiber: str
                  ) -> Tuple[List[list], int]:
    """
    Calculate the flat and blaze quality control criteria

    :param params: ParamDict, the parameter dictionary of constants
    :param eprops: dictionary, the extraction dictionary
    :param fiber: str, the fiber name

    :return: tuple, 1. the qc lists, 2. int 1 if passed 0 if failed
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], [],
    qc_logic, qc_pass = [], []
    # --------------------------------------------------------------
    # check that rms values in required orders are below threshold

    # get mask for removing certain values
    remove_orders = params['FF_RMS_SKIP_ORDERS']
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


def flat_blaze_write(params: ParamDict, recipe: DrsRecipe, infile: DrsFitsFile,
                     eprops: ParamDict, fiber: str, rawfiles: List[str],
                     combine: bool, shapeprops: ParamDict, lprops: ParamDict,
                     sprops: ParamDict, qc_params: List[list]
                     ) -> Tuple[DrsFitsFile, DrsFitsFile]:
    """
    Write the flat and blaze calibration files to disk

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
    :param infile: DrsFitsFile, the input fits file class
    :param eprops: ParamDict, the extraction parameter dictionary
    :param fiber: str, the fiber name
    :param rawfiles: list of strings, the raw filenames
    :param combine: bool, if True input files were combined
    :param shapeprops: ParamDict, the shape parameter dictionary
    :param lprops: ParamDict, the localisation parameter dictionary
    :param sprops: ParamDict, the s1d parameter dictionary
    :param qc_params: list of lists, the quality control lists

    :return: tuple, 1. DrsFitsFile, the output blaze fits file class
             2. DrsFitsFile, the output flat fits file class
    """
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
    # add core values (that should be in all headers)
    blazefile.add_core_hkeys(params)
    # add fiber
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
    blazefile = gen_calib.add_calibs_to_header(blazefile, shapeprops)
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
    if params['DEBUG_E2DSLL_FILE']:
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


def flat_blaze_summary(recipe: DrsRecipe, params: ParamDict,
                       qc_params: List[list], eprops: ParamDict, fiber: str):
    """
    Produce the flat and blaze summary document

    :param recipe: DrsRecipe, the recipe that called this function
    :param params: ParamDict, parameter dictionary of constants
    :param qc_params: list of lists, the quality control lists
    :param eprops: ParamDict, the extraction parameter dictionary
    :param fiber: str, the fiber name

    :return: None, produces the summary document
    """
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

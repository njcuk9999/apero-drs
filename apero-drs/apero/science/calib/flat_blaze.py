#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO flat and blaze calibration functionality

Created on 2019-07-10 at 09:30

@author: cook
"""
import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore import drs_lang
from aperocore import math as mp
from aperocore.science.calib import flat_blaze_core
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.science.calib import gen_calib
from apero.base import base as apero_base

# type alias for the fit_blaze_model return
FitBlazeReturn = Tuple[np.ndarray, dict]

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.extraction.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the input fits file class
DrsFitsFile = drs_file.DrsFitsFile
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)


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
                          width, overrides params['CAL.FLAT.BLAZE_SINC_MED_SIZE']

    :return: tuple, 1. the updated extracted flux for this order
             2. the flat profile for this order
             3. the blaze fit for this order
             4. the rms for this order
    """
    # get function name
    func_name = __NAME__ + '.calculate_blaze_flat_sinc()'
    # get med filt parameter
    med_size = pcheck(params, 'CAL.FLAT.BLAZE_SINC_MED_SIZE', func=func_name,
                      override=sinc_med_size)
    # delegate numerical work to the profile-independent core module
    sinc_args = [e2ds_ini, peak_cut, badpercentile, med_size]
    try:
        with warnings.catch_warnings(record=True) as _:
            outs = flat_blaze_core.calculate_blaze_flat_sinc(*sinc_args)
        return outs
    except RuntimeError as e:
        strguess, strlower, strupper, errtype, errmsg = e.args
        eargs = [order_num, fiber, -1, strguess, strlower, strupper,
                errtype, errmsg, func_name]
        raise AperoCodedException(params, '40-015-00009', targs=eargs)


def get_flat(params: ParamDict, recipe: DrsRecipe,
             header: Union[drs_file.Header, None],
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
        calibdbm = drs_database.CalibrationDatabase(params, recipe.shortname)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------------
    # load flat file
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, recipe.shortname,
                          key, header, filename=filename,
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


def get_blaze(params: ParamDict, recipe: DrsRecipe,
              header: Union[drs_file.Header, None],
              fiber: str,
              e2ds: Optional[np.ndarray] = None,
              filename: Optional[str] = None,
              database: Optional[drs_database.CalibrationDatabase] = None
              ) -> ParamDict:
    """
    Get the blaze calibration and return a ParamDict with blaze properties.

    For flat extractions (extract_type == 'flat') the blaze has not yet been
    computed, so a unity blaze (ones) is returned with 'None' provenance.
    For all other extract types the blaze is loaded from the calibration DB.

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the calling recipe
    :param header: fits Header, the fits header associated with the input
                   file (required to get closest in time) can be None if
                   filename is given
    :param fiber: str, the fiber name
    :param e2ds: numpy (2D) array or None, the extracted spectrum for this
                 fiber; required when extract_type == 'flat' to build a
                 unity blaze with the correct shape; not needed otherwise
    :param filename: str or None, the filename of the blaze calibration to
                     load, overrides getting it from calibration database;
                     header not required for this
    :param database: CalibrationDatabase or None, if passed does not reload
                     the calibration database

    :return: ParamDict with keys BLAZE (numpy 2D array), BLAZEFILE (str),
             BLAZETIME (float)
    """
    func_name = __NAME__ + '.get_blaze()'
    # read the extract type so flat runs do not attempt a DB lookup
    extract_type = params['INPUTS'].get('EXTRACT_TYPE', 'standard')
    fbprops = ParamDict()
    # ------------------------------------------------------------------------
    # For flat extractions the blaze calibration does not yet exist;
    # use a unity blaze so downstream steps receive a well-defined array.
    if extract_type == 'flat':
        # e2ds must be supplied for flat runs so we know the output shape
        if e2ds is None:
            WLOG(params, 'error',
                 'get_blaze: e2ds must be provided for flat extractions')
        fbprops['BLAZE'] = np.ones_like(e2ds)
        fbprops['BLAZEFILE'] = 'None'
        fbprops['BLAZETIME'] = np.nan
        fbprops.set_sources(['BLAZE', 'BLAZEFILE', 'BLAZETIME'], func_name)
        return fbprops
    # ------------------------------------------------------------------------
    # Standard path: load blaze from the calibration database
    WLOG(params, '', 'Loading blaze calibration for fiber {0}'.format(fiber))
    # get file definition
    out_blaze = drs_file.get_file_definition(params, 'FF_BLAZE',
                                             block_kind='red')
    # get calibration database key
    key = out_blaze.get_dbkey()
    # load database if not already provided
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params, recipe.shortname)
        calibdbm.load_db()
    else:
        calibdbm = database
    # load blaze file from the calibration database
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, recipe.shortname,
                          key, header, filename=filename,
                          userinputkey='BLAZEFILE', database=calibdbm,
                          fiber=fiber)
    # log which blaze file we are using
    WLOG(params, '', textentry('40-015-00007', args=[cfile.filename]))
    # populate and return the properties dict
    fbprops['BLAZE'] = cfile.data
    fbprops['BLAZEFILE'] = cfile.filename
    fbprops['BLAZETIME'] = cfile.mjdmid
    fbprops.set_sources(['BLAZE', 'BLAZEFILE', 'BLAZETIME'], func_name)
    return fbprops


def e2ds_correct(params, eprops: ParamDict, fbprops: ParamDict) -> ParamDict:
    """
    Correct the e2ds with the blaze (to match original apero format)

    :param params: ParamDict, the parameter dictionary of constants
    :param eprops: ParamDict, the extracted properties for this fiber
    :param fbprops: ParamDict, the flat/blaze properties for this fiber

    :return: ParamDict, the updated extracted properties for this fiber
    """
    func_name = __NAME__ + '.e2ds_correct()'
    # get the blaze and e2ds from the properties dicts
    blaze = fbprops['BLAZE']
    e2ds = eprops['E2DS']
    # correct the e2ds by dividing by the blaze
    with np.errstate(invalid='ignore', divide='ignore'):
        e2ds_corr = e2ds / blaze
    # update the extracted properties dict with the corrected e2ds
    eprops['E2DS'] = e2ds_corr
    eprops.set_sources(['E2DS'], func_name)
    return eprops


def compute_flat_response(
    params: ParamDict,
    recipe: DrsRecipe,
    model_props: ParamDict,
    order_map: np.ndarray,
    order_ranges: Dict[str, Tuple[int, int]],
) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Compute per-order flat-field response profiles from a flat extraction.

    Reads the extraction constants from ``params``, delegates the numerical
    work to ``flat_blaze_core.compute_flat_response``, then emits debug and
    summary plots via the standard ``recipe.plot`` system.

    :param params: ParamDict, APERO constants
    :param recipe: DrsRecipe, the calling recipe (used for plot calls)
    :param model_props: ParamDict, output of ``run_all_fiber_model``; must
                        contain ``PROFILES_NOSHAPE``, ``SCIENCE_XMAP`` and
                        ``RON`` and may contain ``SPECTRAL_GROUPS`` to mirror
                        the extracted-fiber layout
    :param order_map: numpy (2D) array, trace-label map (pixel → order index)
    :param order_ranges: dict, fiber name → (lo_label, hi_label) trace range

    :return: tuple (flat_response, flat_response_err) — each a dict mapping
             fiber name to a 2D float array of shape (norders, ncols)
    """
    func_name = __NAME__ + '.compute_flat_response()'
    # read convolution constants
    os = pcheck(params, 'CAL.FLAT.RESPONSE_OVERSAMPLING', func=func_name)
    max_hc = pcheck(params, 'CAL.FLAT.RESPONSE_MAX_HALF_CELL',
                    func=func_name) * os
    fwhm = pcheck(params, 'CAL.FLAT.RESPONSE_FWHM_PIX', func=func_name)
    # extract computed products from model_props
    xmap = np.array(model_props['SCIENCE_XMAP'], dtype=float)
    profiles_noshape = model_props['PROFILES_NOSHAPE']
    ron = float(model_props['RON'])
    spectral_groups = model_props.get('SPECTRAL_GROUPS', None)
    # single order used for the non-loop debug/summary plots
    sorder = params['CAL.EXT.PLOT_ORDER']
    # delegate the numerical heavy lifting to the core module
    core_args = [order_map, xmap, profiles_noshape, order_ranges,
                 ron, int(os), float(max_hc), float(fwhm),
                 spectral_groups]
    outs = flat_blaze_core.compute_flat_response(*core_args)
    flat_response, flat_response_err = outs
    # emit debug and summary plots for each fiber
    for fiber, resp in flat_response.items():
        resp_err = flat_response_err[fiber]
        # loop over every order (debug, loop mode)
        recipe.plot('FLAT_RESPONSE_ORDER1',
                    flat_response=resp,
                    flat_response_err=resp_err,
                    order=None, fiber=fiber)
        # single representative order (debug, non-loop)
        recipe.plot('FLAT_RESPONSE_ORDER2',
                    flat_response=resp,
                    flat_response_err=resp_err,
                    order=sorder, fiber=fiber)
        # summary plot for the same representative order
        recipe.plot('SUM_FLAT_RESPONSE_ORDER',
                    flat_response=resp,
                    flat_response_err=resp_err,
                    order=sorder, fiber=fiber)
    return flat_response, flat_response_err


def fit_blaze_model(params: ParamDict, recipe: DrsRecipe,
                    flat_response: np.ndarray,
                    wave: np.ndarray, fiber: str
                    ) -> FitBlazeReturn:
    """
    Fit the physical blaze model to a flat-response profile.

    Reads fit parameters from ``params`` and delegates the numerical
    work to ``flat_blaze_core.fit_blaze_model``.

    :param params: ParamDict, APERO constants
    :param recipe: DrsRecipe, calling recipe (unused, reserved for logging)
    :param flat_response: numpy (2D) array (norders, ncols), flat-response
                          profile to fit
    :param wave: numpy (2D) array (norders, ncols), wavelength solution [nm]
    :param fiber: str, fiber name (used for logging only)

    :return: tuple (blaze_model, fit_params) — blaze_model is a (norders,
             ncols) float array, fit_params is a dict with keys: teff, c0,
             c1, beta, asym, rms, wave_fit_max, lref
    """
    func_name = __NAME__ + '.fit_blaze_model()'
    # read fit constants from params
    teff = pcheck(params, 'CAL.FLAT.BLAZE_TEFF', func=func_name)
    wave_fit_max = pcheck(params, 'CAL.FLAT.BLAZE_WAVE_FIT_MAX',
                          func=func_name)
    sigma_clip = pcheck(params, 'CAL.FLAT.BLAZE_SIGMA_CLIP',
                        func=func_name)
    peak_hw = pcheck(params, 'CAL.FLAT.BLAZE_PEAK_HW', func=func_name)
    spline_k = pcheck(params, 'CAL.FLAT.BLAZE_SPLINE_K', func=func_name)
    WLOG(params, 'info',
         'Fitting physical blaze model for fiber {0}'.format(fiber))
    # delegate numerical work to core module
    core_args = [flat_response, wave]
    core_kwargs = dict(teff=teff, wave_fit_max=wave_fit_max,
                       sigma_clip=sigma_clip, peak_half_width=peak_hw,
                       spline_k=spline_k)
    outs = flat_blaze_core.fit_blaze_model(*core_args, **core_kwargs)
    blaze_model, fit_params = outs
    # log key fit results
    WLOG(params, '',
         '   c0={c0:.1f} nm  c1={c1:+.4f}  '
         'beta={beta:.4f}  asym={asym:+.3f}  '
         'rms={rms:.2%}'.format(**fit_params))
    return blaze_model, fit_params


def make_blaze(params: ParamDict, recipe: DrsRecipe,
               flat_response_files: Dict[str, Optional[np.ndarray]],
               e2ds_files: Dict[str, Optional[DrsFitsFile]],
               wave_maps: Dict[str, np.ndarray],
               fiber_types: List[str]
               ) -> Dict[str, ParamDict]:
    """
    Compute per-fiber blaze models and flat fields from flat-response arrays.

    For each fiber the flat-response profile (loaded from the calibration
    database by ``get_flat_response``) is divided by the fitted physical
    blaze model to give the flat-field.  All relevant eprops keys required
    by ``flat_blaze_write``, ``flat_blaze_qc`` and ``flat_blaze_summary``
    are populated from the fit results and from the e2ds file header (which
    carries full calibration provenance).

    :param params: ParamDict, APERO constants
    :param recipe: DrsRecipe, calling recipe
    :param flat_response_files: dict mapping fiber name to numpy (2D) array
                                containing the flat-response profile, or
                                None if the calibration is not available
    :param e2ds_files: dict mapping fiber name to DrsFitsFile containing
                       the flat e2ds (used to read calibration provenance
                       from its header)
    :param wave_maps: dict mapping fiber name to (norders, ncols) float
                      array with the wavelength solution in nm
    :param fiber_types: list of str, fiber names to process

    :return: dict mapping fiber name to a ParamDict (eprops) containing
             BLAZE, FLAT, E2DS, RMS, SNR, and all calibration provenance
             keys needed by flat_blaze_write/qc/summary
    """
    func_name = __NAME__ + '.make_blaze()'
    nframes = 1
    eprops_all: Dict[str, ParamDict] = dict()
    # announce the overall blaze-fitting step before the per-fiber loop
    WLOG(params, '', 'Fitting physical blaze model for fibers: '
                     '{0}'.format(', '.join(fiber_types)))
    for fiber in fiber_types:
        resp_data = flat_response_files.get(fiber)
        e2ds_file = e2ds_files.get(fiber)
        if resp_data is None or e2ds_file is None:
            WLOG(params, 'warning',
                 'make_blaze: skipping fiber {0} '
                 '(missing flat-response or e2ds file)'.format(fiber))
            continue
        wave_map = wave_maps[fiber]
        flat_response = np.array(resp_data, dtype=float)
        norders, ncols = flat_response.shape
        # fit physical blaze model
        fbout = fit_blaze_model(params, recipe, flat_response,
                                wave_map, fiber)
        blaze_model, fit_params = fbout
        # flat field: is just the extracted flat
        flat = np.array(e2ds_file.data)
        # per-order SNR: median signal / noise from flat_response
        ron = float(e2ds_file.get_hkey('KW_EFF_RON', dtype=float,
                                       required=False) or 0.0)
        with np.errstate(invalid='ignore', divide='ignore'):
            snr = np.nanmedian(flat / np.sqrt(np.abs(flat) + ron ** 2), axis=1)
        rms = np.array([float(np.nanstd(flat[i])) for i in range(norders)])
        # build eprops
        eprops = ParamDict()
        # spectra
        eprops['E2DS'] = flat
        eprops['E2DSFF'] = flat
        eprops['BLAZE'] = blaze_model
        eprops['FLAT'] = flat
        eprops['E2DS_ERROR'] = np.sqrt(np.abs(flat_response) + ron ** 2)
        # per-order statistics
        eprops['SNR'] = snr
        eprops['FLUX_VAL'] = np.nanmean(flat_response, axis=1)
        eprops['N_COSMIC'] = np.zeros(norders)
        eprops['RMS'] = rms
        # fiber info
        eprops['FIBER'] = fiber
        # extraction order range (full range; no trimming)
        eprops['START_ORDER'] = 0
        eprops['END_ORDER'] = norders - 1
        eprops['CAL.EXT.RANGE1'] = 0
        eprops['CAL.EXT.RANGE2'] = 0
        eprops['SKIP_ORDERS'] = []
        # detector parameters (read from e2ds header)
        eprops['EFF_RON'] = ron
        eprops['SIGDET'] = ron
        eprops['GAIN'] = params['IMAGE.EFFGAIN']
        eprops['EFF_GAIN'] = params['IMAGE.EFFGAIN']
        # saturation thresholds (carried from params)
        eprops['SAT_QC'] = params['CAL.EXT.QC_FLUX_MAX']
        eprops['SAT_LEVEL'] = params['CAL.EXT.QC_FLUX_MAX'] * nframes
        # cosmic correction: not applied in the new model extraction
        eprops['COSMIC'] = False
        eprops['COSMIC_SIGCUT'] = params['CAL.EXT.COSMIC_SIGCUT']
        eprops['COSMIC_THRESHOLD'] = params['CAL.EXT.COSMIC_THRES']
        # sinc-fit legacy params: kept in header for backwards compatibility
        eprops['BLAZE_SCUT'] = params['CAL.FLAT.BLAZE_SCUT']
        eprops['BLAZE_BPERCENTILE'] = params['CAL.FLAT.BLAZE_BPTILE']
        # physical model fit parameters
        eprops['BLAZE_TEFF'] = fit_params['teff']
        eprops['BLAZE_C0'] = fit_params['c0']
        eprops['BLAZE_C1'] = fit_params['c1']
        eprops['BLAZE_BETA'] = fit_params['beta']
        eprops['BLAZE_ASYM'] = fit_params['asym']
        eprops['BLAZE_FIT_RMS'] = fit_params['rms']
        eprops.set_all_sources(func_name)
        eprops_all[fiber] = eprops
    WLOG(params, '', 'Blaze model fitting complete')
    return eprops_all


# =============================================================================
# Define write and qc functions
# =============================================================================
def get_flat_response(params: ParamDict, recipe: DrsRecipe,
                      header: Union[drs_file.Header, None],
                      fiber: str, filename: Optional[str] = None,
                      database: Optional[drs_database.CalibrationDatabase] = None
                      ) -> ParamDict:
    """
    Get the flat-response calibration file from the calibration database.

    The flat-response profile is written by ``apero_extract`` during flat
    extraction and registered in the calibration database under key
    ``FLAT_RES``.  This function loads the closest-in-time file for
    ``fiber``.

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the calling recipe
    :param header: fits Header or None, used to find the closest-in-time
                   calibration; not required when ``filename`` is given
    :param fiber: str, the fiber name
    :param filename: str or None, override the calibration database lookup
                     and load this file directly
    :param database: CalibrationDatabase or None, if passed does not reload
                     the calibration database

    :return: ParamDict with keys:
             ``FLAT_RESPONSE``   – numpy (2D) array, the response profile
             ``FLAT_RESP_FILE``  – str, path to the calibration file used
             ``FLAT_RESP_TIME``  – float, MJD-MID of the calibration file
    """
    func_name = __NAME__ + '.get_flat_response()'
    # get file definition and its calibration database key
    out_flat_resp = drs_file.get_file_definition(
        params, 'FLAT_RESPONSE', block_kind='red')
    key = out_flat_resp.get_dbkey()
    # load database if not already provided
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params, recipe.shortname)
        calibdbm.load_db()
    else:
        calibdbm = database
    # load calibration file closest in time to the header observation
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, recipe.shortname,
                          key, header, filename=filename,
                          userinputkey='FLAT_RESP_FILE',
                          database=calibdbm, fiber=fiber)
    WLOG(params, '', 'Loading flat-response calibration for fiber '
                     '{0}: {1}'.format(fiber, cfile.filename))
    frprops = ParamDict()
    frprops['FLAT_RESPONSE'] = cfile.data
    frprops['FLAT_RESP_FILE'] = cfile.filename
    frprops['FLAT_RESP_TIME'] = cfile.mjdmid
    frprops.set_sources(
        ['FLAT_RESPONSE', 'FLAT_RESP_FILE', 'FLAT_RESP_TIME'], func_name)
    return frprops


def write_flat_response(params: ParamDict, recipe: DrsRecipe,
                        infile: DrsFitsFile, flat_response_data: np.ndarray,
                        fiber: str) -> DrsFitsFile:
    """
    Write a per-fiber flat-response array to a FLAT_RESPONSE_FILE on disk.

    Header keys are copied from ``infile`` and the fiber keyword is added.
    The output file is registered with the recipe for downstream indexing.
    The caller is responsible for adding the returned file to the
    calibration database.

    :param params: ParamDict, APERO constants
    :param recipe: DrsRecipe, the calling recipe (used to look up the output
                   file definition and to register the written file)
    :param infile: DrsFitsFile, the science frame used to construct the
                   output filename and to supply the base header keys
    :param flat_response_data: numpy (2D) array, the flat-response profile
                               of shape (norders, ncols)
    :param fiber: str, the fiber name for this flat-response slice

    :return: DrsFitsFile, the written flat-response file (add to calibDB
             to make it discoverable by ``get_flat_response``)
    """
    # get a new copy of the flat-response file type from the recipe outputs
    resp_file = recipe.outputs['FLAT_RESPONSE_FILE'].newcopy(
        params=params, fiber=fiber)
    # build the output filename from the input file
    resp_file.construct_filename(infile=infile)
    # copy standard header keys from the input file, excluding localization
    resp_file.copy_original_keys(infile, exclude_groups=['loc'])
    # add the core APERO header keys common to all output files
    resp_file.add_core_hkeys(params)
    # record the fiber this response array belongs to
    resp_file.add_hkey('KW_FIBER', value=fiber)
    # record the input file basename in the header
    resp_file.infiles = [infile.basename]
    # attach the 2D flat-response data
    resp_file.data = flat_response_data
    # write the file to disk
    resp_file.write_file(block_kind=recipe.out_block_str)
    # register with the recipe for indexing and downstream use
    recipe.add_output_file(resp_file)
    return resp_file


def flat_blaze_qc(params: ParamDict, recipe: DrsRecipe,
                  eprops: ParamDict, fiber: str
                  ) -> Tuple[List[list], int]:
    """
    Calculate the flat and blaze quality control criteria.

    QC is based on the maximum per-order fit RMS across all orders that are
    not listed in CAL.FLAT.RMS_SKIP_ORDERS.

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the drs recipe object
    :param eprops: ParamDict, the extraction dictionary; must contain 'RMS'
    :param fiber: str, the fiber name

    :return: tuple, 1. the qc lists, 2. int 1 if passed 0 if failed
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], []
    qc_logic, qc_pass = [], []
    # -------------------------------------------------------------------------
    # check that rms values in required orders are below threshold
    # get mask for removing certain orders from the RMS check
    remove_orders = params['CAL.FLAT.RMS_SKIP_ORDERS']
    remove_orders = np.array(remove_orders)
    remove_mask = np.isin(np.arange(len(eprops['RMS'])), remove_orders)
    # maximum per-order RMS excluding skipped orders
    max_rms = mp.nanmax(eprops['RMS'][~remove_mask])
    # apply the quality control based on the maximum rms
    if max_rms > params['CAL.FLAT.QC_MAX_RMS']:
        # add failed message to fail message list
        fargs = [fiber, max_rms, params['CAL.FLAT.QC_MAX_RMS']]
        fail_msg.append(textentry('40-015-00008', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(max_rms)
    qc_names.append('max_rms')
    qc_logic.append('max_rms < {0:.2f}'.format(params['CAL.FLAT.QC_MAX_RMS']))
    # -------------------------------------------------------------------------
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


def flat_blaze_write(params: ParamDict, recipe: DrsRecipe,
                     infile: DrsFitsFile, eprops: ParamDict,
                     fiber: str, rawfiles: List[str], combine: bool,
                     source_file: DrsFitsFile, qc_params: List[list]
                     ) -> Tuple[DrsFitsFile, DrsFitsFile]:
    """
    Write the flat and blaze calibration files to disk.

    Calibration provenance (shape, loco, wave, instrument header keys) is
    copied verbatim from ``source_file`` (the flat e2ds DrsFitsFile), which
    already carries a complete provenance header from the extraction step.

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
    :param infile: DrsFitsFile, the raw input fits file (used for filename
                   construction and the raw infile list)
    :param eprops: ParamDict, the extraction parameter dictionary
    :param fiber: str, the fiber name
    :param rawfiles: list of strings, the raw filenames
    :param combine: bool, if True input files were combined
    :param source_file: DrsFitsFile, the flat e2ds file; its header carries
                        full calibration provenance that is copied into the
                        blaze and flat output headers
    :param qc_params: list of lists, the quality control lists

    :return: tuple, 1. DrsFitsFile, the output blaze fits file class
             2. DrsFitsFile, the output flat fits file class
    """
    # --------------------------------------------------------------
    # Build input file list (raw or combined)
    # --------------------------------------------------------------
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    # --------------------------------------------------------------
    # Store Blaze in file
    # --------------------------------------------------------------
    # get a new copy of the blaze file output definition
    blazefile = recipe.outputs['BLAZE_FILE'].newcopy(params=params,
                                                     fiber=fiber)
    # construct the output filename from the raw input file
    blazefile.construct_filename(infile=infile)
    # copy all calibration provenance from the flat e2ds file; this
    # includes shape, loco, wave and instrument header keys already
    # written during the extraction step
    blazefile.copy_header(source_file)
    blazefile.copy_hdict(source_file)
    # refresh core APERO header keys
    blazefile.add_core_hkeys(params)
    # record fiber
    blazefile.add_hkey('KW_FIBER', value=fiber)
    # record input files
    blazefile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    blazefile.infiles = list(hfiles)
    # add qc parameters
    blazefile.add_qckeys(qc_params)
    # add SNR per order
    blazefile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                          dim1name='order')
    # add start and end extraction order used
    blazefile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
    blazefile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
    # add extraction ranges used
    blazefile.add_hkey('KW_EXT_RANGE1', value=eprops['CAL.EXT.RANGE1'])
    blazefile.add_hkey('KW_EXT_RANGE2', value=eprops['CAL.EXT.RANGE2'])
    # add cosmic correction parameters (not applied for model extraction)
    blazefile.add_hkey('KW_COSMIC', value=eprops['COSMIC'])
    blazefile.add_hkey('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'])
    blazefile.add_hkey('KW_COSMIC_THRES', value=eprops['COSMIC_THRESHOLD'])
    # add sinc-fit legacy parameters (filled from params, not used)
    blazefile.add_hkey('KW_BLAZE_SCUT', value=eprops['BLAZE_SCUT'])
    blazefile.add_hkey('KW_BLAZE_BPRCNTL', value=eprops['BLAZE_BPERCENTILE'])
    # add physical blaze model parameters from the fit
    blazefile.add_hkey('KW_BLAZE_TEFF', value=eprops['BLAZE_TEFF'])
    blazefile.add_hkey('KW_BLAZE_C0', value=eprops['BLAZE_C0'])
    blazefile.add_hkey('KW_BLAZE_C1', value=eprops['BLAZE_C1'])
    blazefile.add_hkey('KW_BLAZE_BETA', value=eprops['BLAZE_BETA'])
    blazefile.add_hkey('KW_BLAZE_ASYM', value=eprops['BLAZE_ASYM'])
    blazefile.add_hkey('KW_BLAZE_FIT_RMS', value=eprops['BLAZE_FIT_RMS'])
    # add saturation parameters
    blazefile.add_hkey('KW_SAT_QC', value=eprops['SAT_LEVEL'])
    with warnings.catch_warnings(record=True) as _:
        max_sat_level = mp.nanmax(eprops['FLUX_VAL'])
    blazefile.add_hkey('KW_SAT_LEVEL', value=max_sat_level)
    # attach blaze model data
    blazefile.data = eprops['BLAZE']
    # log that we are saving the blaze file
    WLOG(params, '', textentry('40-015-00003', args=[blazefile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['GLOBAL.PSNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=blazefile)]
        name_list += ['PARAM_TABLE']
    # write blaze file to disk
    blazefile.write_multi(data_list=data_list, name_list=name_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(blazefile)
    # --------------------------------------------------------------
    # Store Flat-field in file
    # --------------------------------------------------------------
    # get a new copy of the flat file output definition
    flatfile = recipe.outputs['FLAT_FILE'].newcopy(params=params,
                                                   fiber=fiber)
    # construct the output filename from the raw input file
    flatfile.construct_filename(infile=infile)
    # copy header from blaze file (includes all provenance keys set above)
    flatfile.copy_header(blazefile)
    flatfile.copy_hdict(blazefile)
    flatfile.infiles = list(hfiles)
    # set the output type keyword for the flat file
    flatfile.add_hkey('KW_OUTPUT', value=flatfile.name)
    # attach flat field data
    flatfile.data = eprops['FLAT']
    # log that we are saving the flat file
    WLOG(params, '', textentry('40-015-00004', args=[flatfile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['GLOBAL.PSNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=flatfile)]
        name_list += ['PARAM_TABLE']
    # write flat file to disk
    flatfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(flatfile)
    # return output files
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
    recipe.plot.add_stat('KW_VERSION', value=params['DRS.VERSION'], fiber=fiber)
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS.DATE'], fiber=fiber)
    recipe.plot.add_stat('KW_EXT_START', value=epp['START_ORDER'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_END', value=epp['END_ORDER'], fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE1', value=epp['CAL.EXT.RANGE1'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE2', value=epp['CAL.EXT.RANGE2'], fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC', value=epp['COSMIC'], fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_CUT', value=epp['COSMIC_SIGCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_THRES', fiber=fiber,
                         value=epp['COSMIC_THRESHOLD'])
    # add sinc-fit legacy parameters (filled from params)
    recipe.plot.add_stat('KW_BLAZE_SCUT', value=eprops['BLAZE_SCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_BPRCNTL', value=eprops['BLAZE_BPERCENTILE'],
                         fiber=fiber)
    # add physical blaze model parameters from the fit
    recipe.plot.add_stat('KW_BLAZE_TEFF', value=eprops['BLAZE_TEFF'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_C0', value=eprops['BLAZE_C0'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_C1', value=eprops['BLAZE_C1'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_BETA', value=eprops['BLAZE_BETA'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_ASYM', value=eprops['BLAZE_ASYM'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_BLAZE_FIT_RMS', value=eprops['BLAZE_FIT_RMS'],
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
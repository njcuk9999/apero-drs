#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO wrapper for model-based extraction background correction

This module keeps APERO parameters, logging and property dictionaries in
apero-drs while delegating numerical work to
``aperocore.science.extract.extract_model_core``.

Created on 2026-09-17

@author: cook
"""
from typing import Optional, Tuple, cast

import numpy as np

from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.math import interpolate
from aperocore.science.extract import extract_model_core
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.model_background.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get parameter class
ParamDict = param_functions.ParamDict
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
def prepare_model_bckgrd_geo(
    params: ParamDict,
    sprops: ParamDict) -> ParamDict:
    """
    Prepare geometry products used by model-background extraction.

    The inverse detector maps (``INV_XMAP``, ``INV_YMAP``) were computed
    once in ``apero_shape`` and stored as SHAPEL extensions; they are
    already present in *sprops* after ``shape.get_shape_calibs`` loads them.
    This function simply copies the relevant fields into a dedicated geometry
    ParamDict so the rest of the extraction code has a stable interface.

    :param params: ParamDict, APERO constants
    :param sprops: ParamDict, shape calibration properties including
                   ``INV_XMAP`` and ``INV_YMAP`` loaded from SHAPEL

    :return: ParamDict, geometry products for model-background extraction
    """
    func_name = __NAME__ + '.prepare_model_bckgrd_geo()'
    WLOG(params, '', 'Preparing model-background extraction geometry')
    # Copy the pre-computed inverse maps and shape arrays from sprops;
    # no re-computation needed here since apero_shape already did it.
    gprops = ParamDict()
    gprops['DXMAP_NO_SHAPE'] = sprops['DXMAP_NO_SHAPE']
    gprops['SHAPEL'] = sprops['SHAPEL']
    gprops['SHAPEX'] = sprops['SHAPEX']
    gprops['SHAPEY'] = sprops['SHAPEY']
    gprops['INV_XMAP'] = np.array(sprops['INV_XMAP'], dtype=float)
    gprops['INV_YMAP'] = np.array(sprops['INV_YMAP'], dtype=float)
    gprops['SHAPELFILE'] = sprops['SHAPELFILE']
    gprops['SHAPELTIME'] = sprops['SHAPELTIME']
    gprops['DXMAP_NO_SHAPEFILE'] = sprops['DXMAP_NO_SHAPEFILE']
    gprops['DXMAP_NO_SHAPETIME'] = sprops['DXMAP_NO_SHAPETIME']
    keys = ['DXMAP_NO_SHAPE', 'INV_XMAP', 'INV_YMAP', 'SHAPELFILE',
            'SHAPELTIME', 'DXMAP_NO_SHAPEFILE', 'DXMAP_NO_SHAPETIME']
    gprops.set_sources(keys, func_name)
    return gprops


def model_background_correction(params: ParamDict, image_noshape: np.ndarray,
                                image_straight: np.ndarray,
                                model_straight: np.ndarray,
                                inverse_x: np.ndarray,
                                inverse_y: np.ndarray,
                                order_map: Optional[np.ndarray] = None,
                                model_noshape: Optional[np.ndarray] = None,
                                gain: Optional[float] = None,
                                ron_start: Optional[float] = None,
                                ron_stride: Optional[int] = None,
                                ron_lag: Optional[int] = None,
                                bkg_box: Optional[Tuple[int, int]] = None,
                                bkg_stride_frac: Optional[float] = None,
                                mask_nsig1: Optional[float] = None,
                                mask_nsig2: Optional[float] = None,
                                fit_ron: Optional[bool] = None
                                ) -> ParamDict:
    """
    Build a smooth background from model-subtracted straightened data and
    subtract it in the unshaped science frame

    :param params: ParamDict, APERO constants
    :param image_noshape: numpy array (2D), science-frame image in electrons
    :param image_straight: numpy array (2D), straightened image in electrons
    :param model_straight: numpy array (2D), all-fiber model in straight
                           frame, in electrons
    :param inverse_x: numpy array (2D), straightened x coordinate read by
                      each science-frame pixel
    :param inverse_y: numpy array (2D), straightened y coordinate read by
                      each science-frame pixel
    :param order_map: numpy array (2D) or None, order labels in science
                      frame, zero outside orders
    :param model_noshape: numpy array (2D) or None, all-fiber model in
                          science frame, in electrons
    :param gain: float or None, detector gain in e-/ADU
    :param ron_start: float or None, initial readout-noise estimate
    :param ron_stride: int or None, stride for fitting readout noise
    :param ron_lag: int or None, lag for between-order readout-noise check
    :param bkg_box: tuple or None, background box as (rows, columns)
    :param bkg_stride_frac: float or None, coarse-grid stride fraction
    :param mask_nsig1: float or None, sigma cut that seeds masking
    :param mask_nsig2: float or None, sigma cut that grows masking

    :return: ParamDict, background-correction products
    """
    func_name = __NAME__ + '.model_background_correction()'
    if gain is None:
        gain = params['IMAGE.EFFGAIN']
    if ron_start is None:
        ron_start = params['CAL.EXT.RON_START']
    if ron_stride is None:
        ron_stride = params['CAL.EXT.RON_STRIDE']
    if ron_lag is None:
        ron_lag = params['CAL.EXT.RON_LAG']
    if bkg_box is None:
        bkg_box = tuple(params['CAL.EXT.BKG_BOX'])
    if bkg_stride_frac is None:
        bkg_stride_frac = params['CAL.EXT.BKG_STRIDE_FRAC']
    if mask_nsig1 is None:
        mask_nsig1 = params['CAL.EXT.MASK_NSIG1']
    if mask_nsig2 is None:
        mask_nsig2 = params['CAL.EXT.MASK_NSIG2']
    if fit_ron is None:
        fit_ron = params['CAL.EXT.FIT_RON']
    ron_start_value = 8.0 if ron_start is None else float(ron_start)
    ron_stride_value = 5 if ron_stride is None else int(ron_stride)
    ron_lag_value = 4 if ron_lag is None else int(ron_lag)
    mask_nsig1_value = 10.0 if mask_nsig1 is None else float(mask_nsig1)
    mask_nsig2_value = 3.0 if mask_nsig2 is None else float(mask_nsig2)
    # ----------------------------------------------------------------------
    # Remove the fitted model first; what remains is the smooth additive light
    #   that should be sampled on the coarse background grid.
    diff_straight = image_straight - model_straight
    xargs = [diff_straight]
    xkwargs = dict(size=bkg_box, stride_frac=bkg_stride_frac, coarse=True)
    xout = extract_model_core.background_model(*xargs, **xkwargs)
    coarse_out = cast(Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
                      xout)
    bkg_coarse, bkgerr_coarse, bkg_y, bkg_x = coarse_out
    xargs = [[bkg_coarse, bkgerr_coarse], bkg_y, bkg_x,
             inverse_y, inverse_x]
    xout = interpolate.sample_bilinear(*xargs)
    bkg_noshape, bkgerr_noshape = xout
    # ----------------------------------------------------------------------
    # estimate readout noise and mask deviant science-frame residuals
    image_noshape_e = np.array(image_noshape, dtype=float)
    model_noshape_array = (np.zeros_like(image_noshape_e)
                           if model_noshape is None
                           else np.array(model_noshape, dtype=float))
    # The science-frame residual is the ADU data minus the electron model, so
    #   the readout-noise estimate sees the same units as the fitted model.
    residual_noshape = image_noshape_e - model_noshape_array
    if fit_ron:
        ron = extract_model_core.fit_ron(
            residual_noshape, model_noshape_array,
            ron_start=ron_start_value, stride=ron_stride_value)
    else:
        ron = ron_start_value
    with np.errstate(invalid='ignore'):
        err_noshape = np.sqrt(np.abs(image_noshape_e) + ron ** 2)
        err_noshape = np.sqrt(err_noshape ** 2
                              + np.nan_to_num(bkgerr_noshape) ** 2)
        nsig_noshape = residual_noshape / np.sqrt(
            np.abs(model_noshape_array) + ron ** 2)
    mask = extract_model_core.hysteresis_mask(
        nsig_noshape, mask_nsig1_value, mask_nsig2_value)
    corrected = np.array(image_noshape - bkg_noshape)
    corrected[mask] = np.nan
    err_noshape[mask] = np.nan
    # ----------------------------------------------------------------------
    # optional independent readout-noise check between orders
    if order_map is None:
        ron_between = np.nan
    else:
        ron_between = extract_model_core.ron_between_orders(
            image_noshape_e, bkg_noshape, order_map,
            lag=ron_lag_value)
    # ----------------------------------------------------------------------
    WLOG(params, '', 'Model background correction complete')
    props = ParamDict()
    props['SCI_BKGSUB'] = corrected
    props['SCI_BKGSUB_ERR'] = err_noshape
    props['BKG_NOSHAPE'] = bkg_noshape
    props['BKG_NOSHAPE_ERR'] = bkgerr_noshape
    props['DIFF_STRAIGHT'] = diff_straight
    props['RESIDUAL_NOSHAPE'] = residual_noshape
    props['NSIG_NOSHAPE'] = nsig_noshape
    props['MASK_NOSHAPE'] = mask
    props['EFF_RON_FIT'] = ron
    props['EFF_RON_BETWEEN'] = ron_between
    props['BKG_BOX'] = list(bkg_box)
    props['BKG_STRIDE_FRAC'] = bkg_stride_frac
    props['MASK_NSIG1'] = mask_nsig1_value
    props['MASK_NSIG2'] = mask_nsig2_value
    props.set_all_sources(func_name)
    return props


def extract_all_fibers(params: ParamDict, image_straight: np.ndarray,
                       profile1: np.ndarray, profile2: np.ndarray,
                       row1: np.ndarray, row2: np.ndarray,
                       gain: Optional[float] = None,
                       ron: Optional[float] = None,
                       robust: bool = False,
                       products: bool = True,
                       extras: bool = True) -> ParamDict:
    """
    Extract all paired fibers from straightened profile ribbons.

    :param params: ParamDict, APERO constants
    :param image_straight: numpy array (2D), straightened science image
    :param profile1: numpy array (2D), first fiber profile image
    :param profile2: numpy array (2D), second fiber profile image
    :param row1: numpy array (1D), first row of each order ribbon
    :param row2: numpy array (1D), last row of each order ribbon
    :param gain: float or None, detector gain in electrons per ADU
    :param ron: float or None, readout noise in electrons
    :param robust: bool, use robust reweighted ribbon fits
    :param products: bool, build image-sized model products
    :param extras: bool, build residual/error diagnostic products

    :return: ParamDict, all-fiber extraction products and fit properties
    """
    func_name = __NAME__ + '.extract_all_fibers()'
    if gain is None:
        gain = params['IMAGE.EFFGAIN']
    if ron is None:
        ron = params['CAL.EXT.RON_START']
    trace_nan_frac = params['CAL.EXT.TRACE_NAN_FRAC']
    trim_keep = params['CAL.EXT.TRIM_KEEP']
    n_iter = params['CAL.EXT.IRLS_ITER']
    fit_nu = params['CAL.EXT.FIT_NU']
    image_e = np.array(image_straight, dtype=float)
    profile1 = np.array(profile1, dtype=float)
    profile2 = np.array(profile2, dtype=float)
    xargs = [image_e, profile1, profile2, row1, row2]
    xkwargs = dict(noise=ron, nclip=params['CAL.EXT.FIT_NCLIP'],
                   nsig_clip=params['CAL.EXT.FIT_NSIG_CLIP'],
                   zp_mad_cut=params['CAL.EXT.FIT_ZP_MAD_CUT'], robust=robust,
                   nu=fit_nu,
                   n_iter=n_iter, trim_keep=trim_keep,
                   trace_nan_frac=trace_nan_frac, products=products,
                   extras=extras)
    xout = extract_model_core.extract_orders(*xargs, **xkwargs)
    keys = ['FLUX1', 'FLUX2', 'ZEROPOINT', 'MODEL1', 'MODEL2',
            'IMAGE_MODEL', 'RESIDUAL', 'NSIG', 'ERROR', 'ZERO_IMAGE']
    props = ParamDict()
    for key, value in zip(keys, xout):
        props[key] = value
    props['GAIN'] = gain
    props['RON'] = ron
    props['TRACE_NAN_FRAC'] = trace_nan_frac
    props['TRIM_KEEP'] = trim_keep
    props['IRLS_ITER'] = n_iter
    props['FIT_NU'] = fit_nu
    props.set_all_sources(func_name)
    return props


def run_all_fiber_model(params: ParamDict, image_noshape: np.ndarray,
                        image_straight: np.ndarray,
                        order_profiles: dict,
                        profiles_noshape: dict,
                        geometry: ParamDict,
                        order_map: np.ndarray,
                        order_nearest: np.ndarray,
                        order_ranges: dict,
                        order_top_pos: np.ndarray,
                        order_bottom_pos: np.ndarray,
                        order_mid_pos: np.ndarray,
                        spectral_groups: list,
                        fiber1: str, fiber2: str,
                        gain: float = None,
                        ron: float = None,
                        robust: bool = None,
                        ) -> ParamDict:
    """
    Fit both fibers and subtract their modelled background.

    :param params: ParamDict, APERO constants
    :param image_noshape: numpy array, calibrated science frame
    :param image_straight: numpy array, straightened science frame
    :param order_profiles: dict, straightened profiles by fiber name
    :param profiles_noshape: dict, detector-frame profiles by fiber name,
                             pre-computed by ``apero_shape`` and loaded from
                             the SHAPEL calibration file
    :param geometry: ParamDict, inverse shape geometry products
    :param order_map: numpy array, localisation order-label map
    :param order_nearest: numpy array, nearest trace-label map
    :param order_ranges: dict, fiber trace-label ranges from LOC_LOCO
    :param order_top_pos: numpy array, top row of each straightened ribbon
    :param order_bottom_pos: numpy array, bottom row of each straightened ribbon
    :param order_mid_pos: numpy array, midpoint row of each straightened ribbon
    :param spectral_groups: list, instrument-owned extraction groupings
    :param fiber1: str, first fiber-set name
    :param fiber2: str, second fiber-set name
    :param gain: float or None, detector gain
    :param ron: float or None, readout noise
    :param robust: bool or None, use robust profile fitting

    :return: ParamDict, model-fit and background-subtraction products
    """
    func_name = __NAME__ + '.run_all_fiber_model()'
    # Read the two straightened profiles that are fitted simultaneously.
    profile1 = np.array(order_profiles[fiber1], dtype=float)
    profile2 = np.array(order_profiles[fiber2], dtype=float)
    # Use the localization-produced straightened ribbon bounds directly.
    row1 = np.array(order_top_pos, dtype=int)
    row2 = np.array(order_bottom_pos, dtype=int)
    if robust is None:
        robust = params['CAL.EXT.FIT_ROBUST']
    # profiles_noshape was computed once in apero_shape and loaded from the
    # SHAPEL file; no per-science-frame reverse transform is needed here.
    dxmap = np.array(geometry['DXMAP_NO_SHAPE'], dtype=float)
    xmap = np.arange(dxmap.shape[1], dtype=float)[None, :] - dxmap
    fit_props = extract_all_fibers(params, image_straight, profile1,
                                   profile2, row1, row2, gain=gain, ron=ron,
                                   robust=robust, products=True, extras=True)
    if params['CAL.EXT.FIT_RON']:
        fiber_model, zero_model = extract_model_core.model_in_science(
            fit_props['FLUX1'], fit_props['FLUX2'], fit_props['ZEROPOINT'],
            order_nearest, xmap, profiles_noshape, order_ranges,
            fibers=(fiber1, fiber2))
        full_model = fiber_model + zero_model
        image_noshape_e = np.array(image_noshape, dtype=float)
        ron_fit = extract_model_core.fit_ron(
            image_noshape_e - full_model, full_model,
            ron_start=fit_props['RON'], stride=params['CAL.EXT.RON_STRIDE'])
        fit_props = extract_all_fibers(
            params, image_straight, profile1, profile2, row1, row2,
            gain=gain, ron=ron_fit, robust=robust, products=True,
            extras=True)
    fiber_model, zero_model = extract_model_core.model_in_science(
        fit_props['FLUX1'], fit_props['FLUX2'], fit_props['ZEROPOINT'],
        order_nearest, xmap, profiles_noshape, order_ranges,
        fibers=(fiber1, fiber2))
    full_model = fiber_model + zero_model
    # Match the original prototype: estimate the smooth background after
    #   subtracting the paired-fiber model while keeping the zero-point term in
    #   the fit diagnostics and the science-frame residuals.
    bkargs = [params, image_noshape, image_straight,
              fit_props['IMAGE_MODEL'],
              geometry['INV_XMAP'], geometry['INV_YMAP']]
    bkkwargs = dict(order_map=order_map, model_noshape=fiber_model,
                    gain=gain, ron_start=fit_props['RON'],
                    fit_ron=False)
    bkg_props = model_background_correction(*bkargs, **bkkwargs)
    # Extract each configured fiber grouping from the corrected science frame.
    corrected = bkg_props['SCI_BKGSUB']
    corrected_err = bkg_props['SCI_BKGSUB_ERR']
    spectrum_step = params['CAL.EXT.SAVGOL_STEP']
    xgrid = np.arange(0.0, corrected.shape[1], spectrum_step)

    spec_args = [corrected, corrected_err, order_map, xmap,
                 profiles_noshape, order_ranges, xgrid, spectral_groups]
    spec_kwargs = dict(window=params['CAL.EXT.SAVGOL_WINDOW'],
                       polyorder=params['CAL.EXT.SAVGOL_POLYORDER'],
                       cut=params['CAL.EXT.SAVGOL_CUT'],
                       minpts=params['CAL.EXT.SAVGOL_MINPTS'],
                       weight_kind=params['CAL.EXT.SAVGOL_WEIGHT'])
    spectra = extract_model_core.extract_spectra(*spec_args, **spec_kwargs)

    # Combine the fit and background products into one APERO property bag.
    props = ParamDict()
    for key in fit_props:
        props[key] = fit_props[key]
    for key in bkg_props:
        props[key] = bkg_props[key]
    # Formalize the fitted amplitudes as the new extraction spectra contract.
    props['MODEL_SPECTRA'] = extract_model_core.model_spectra(
        fit_props['FLUX1'], fit_props['FLUX2'], fiber1, fiber2)
    props['SCIENCE_MODEL'] = full_model
    props['SCIENCE_FIBER_MODEL'] = fiber_model
    props['SCIENCE_ZERO_MODEL'] = zero_model
    props['SCIENCE_XMAP'] = xmap
    # expose the science-frame profiles so the flat-response step can reuse
    # them without re-running the shape transform
    props['PROFILES_NOSHAPE'] = profiles_noshape
    props['SPECTRA'] = spectra
    props['SPECTRUM_GRID'] = xgrid
    props['FIBER1'] = fiber1
    props['FIBER2'] = fiber2
    props['ROW1'] = row1
    props['ROW2'] = row2
    props['ORDER_MID'] = np.array(order_mid_pos, dtype=int)
    props.set_all_sources(func_name)
    return props


def spectra_to_eprops(params: ParamDict, model_props: ParamDict,
                      fiber: str, nframes: int = 1) -> ParamDict:
    """
    Adapt a new science-frame spectrum to the legacy APERO property contract.

    This adapter lets leak, thermal, S1D, QC, and file-writing code consume
    the new simultaneous-fit spectrum while their output contracts migrate.

    :param params: ParamDict, APERO constants
    :param model_props: ParamDict, output from ``run_all_fiber_model``
    :param fiber: str, requested fiber spectrum name
    :param nframes: int, number of combined input frames

    :return: ParamDict, extraction properties backed by model spectra
    """
    func_name = __NAME__ + '.spectra_to_eprops()'
    if 'SPECTRA' in model_props and fiber in model_props['SPECTRA']:
        spectrum, spectrum_error = model_props['SPECTRA'][fiber]
        e2ds = np.array(spectrum, dtype=float)
        e2ds_error = np.array(spectrum_error, dtype=float)
    else:
        e2ds = np.array(model_props['MODEL_SPECTRA'][fiber], dtype=float)
        e2ds_error = np.sqrt(np.abs(e2ds))
    ron = float(model_props['RON'])
    flat = np.ones_like(e2ds)
    blaze = np.ones_like(e2ds)
    with np.errstate(invalid='ignore', divide='ignore'):
        snr = np.nanmedian(e2ds / np.sqrt(np.abs(e2ds) + ron ** 2), axis=1)
    props = ParamDict()
    props['E2DS'] = e2ds
    props['E2DSFF'] = np.array(e2ds)
    props['E2DS_ERROR'] = e2ds_error
    props['SNR'] = snr
    props['N_COSMIC'] = np.zeros(e2ds.shape[0])
    props['FLUX_VAL'] = np.nanmean(e2ds, axis=1)
    props['FIBER'] = fiber
    props['START_ORDER'] = 0
    props['END_ORDER'] = e2ds.shape[0] - 1
    props['CAL.EXT.RANGE1'] = 0
    props['CAL.EXT.RANGE2'] = 0
    props['SKIP_ORDERS'] = []
    props['GAIN'] = params['IMAGE.EFFGAIN']
    props['SIGDET'] = ron
    props['EFF_RON'] = ron
    props['EFF_GAIN'] = params['IMAGE.EFFGAIN']
    props['COSMIC'] = False
    props['COSMIC_SIGCUT'] = np.nan
    props['COSMIC_THRESHOLD'] = np.nan
    props['SAT_QC'] = params['CAL.EXT.QC_FLUX_MAX']
    props['SAT_LEVEL'] = params['CAL.EXT.QC_FLUX_MAX'] * nframes
    props['FLAT'] = flat
    props['BLAZE'] = blaze
    props['RMS'] = np.zeros(e2ds.shape[0])
    props['LEAK_CORRECTED'] = False
    props['LEAKREF_FILE'] = 'No leak'
    props['LEAKREF_TIME'] = 'No leak'
    props['LEAKREF_REFFILE'] = 'No leak'
    props['LEAKREF_REFTIME'] = 'No leak'
    props['LEAKCORR'] = np.full_like(e2ds, np.nan)
    props.set_all_sources(func_name)
    return props


# =============================================================================
# End of code
# =============================================================================
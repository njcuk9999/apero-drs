#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flat and blaze calibration science functions

Pure numerical routines used to fit the blaze/flat sinc model and to
characterise the flux at the edges of the order trace. These functions do
not load APERO profiles or depend on apero-drs.

Created on 2026-09-14

@author: cook
"""
import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.optimize import curve_fit
from scipy.optimize import least_squares

from aperocore.base import base
from aperocore import math as mp
from aperocore.math import interpolate

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.calib.flat_blaze_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

blaze_flat_return = Tuple[np.ndarray, np.ndarray, np.ndarray, float]


# =============================================================================
# Define functions
# =============================================================================
def calculate_blaze_flat_sinc(e2ds_ini: np.ndarray, peak_cut: float,
                              badpercentile: float, med_size: int
                              ) -> blaze_flat_return:
    """
    Calculate the blaze function using a sinc function

    :param e2ds_ini: numpy (1D) array: the extracted flux for this order
    :param peak_cut: float, the threshold expressed as the fraction of the
                     maximum peak, below this threshold the blaze is set to
                     NaN
    :param badpercentile: float, the hot pixel percentile level
    :param med_size: int, the sinc fit median filter width

    :return: tuple, 1. the updated extracted flux for this order
             2. the flat profile for this order
             3. the blaze fit for this order
             4. the rms for this order

    :raises RuntimeError: if the sinc fit fails after all fallback attempts
    """
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
    # pass without DC and SLOPE
    bounds = [(0, 0.0, 0.0, -np.inf, -np.inf, -1e-20),
              (thres * 1.5, np.inf, np.max(xpix), np.inf, np.inf, 1e-20)]
    # set a counter
    n_it = -1
    # -------------------------------------------------------------------------
    # try a few times (this can fix it not working)
    tries = 0
    popt, pcov = [], []
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
                    # try again (this can fix it not working)
                    if tries < 5:
                        tries += 1
                    # on the 5th attempt give up
                    if tries == 5:
                        strlist = ('amp={0} period={1} lin={2} slope={3} '
                                   'quad={4} (cube={5})')
                        strguess = strlist.format(*fit_guess)
                        strlower = strlist.format(*bounds[0])
                        strupper = strlist.format(*bounds[1])
                        raise RuntimeError(strguess, strlower, strupper,
                                          type(e).__name__, str(e))
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
    # If the blaze is below 0.25 we consider that the blaze and flat correction
    # are not reliable
    with warnings.catch_warnings(record=True) as _:
        bad_mask3 = blaze < 0.25 * np.nanmax(blaze)
        flat[bad_mask3] = np.nan
        blaze[bad_mask3] = np.nan
        e2ds_ini[bad_mask3] = np.nan
    # ----------------------------------------------------------------------
    # recalculate calculate the rms
    # ----------------------------------------------------------------------
    rms = mp.robust_nanstd(flat[keep])
    # ----------------------------------------------------------------------
    # return values
    return e2ds_ini, flat, blaze, rms


def fit_blaze_model(
    flat_response: np.ndarray,
    wave: np.ndarray,
    teff: float = 5000.0,
    wave_fit_max: float = 2500.0,
    sigma_clip: float = 5.0,
    peak_half_width: int = 50,
    spline_k: int = 1,
) -> Tuple[np.ndarray, dict]:
    """
    Fit a physical blaze model to a flat-response spectrum.

    The model is:

        model(m, pixel) = BB_photon(lambda, teff)
                          * Trans(lambda)
                          * sinc^2(blaze)
                          * |dlambda/dpixel|

    where BB_photon is proportional to
    ``1 / (lambda^4 * (exp(hc / (lambda * k * teff)) - 1))``,
    Trans is a linear spline in log space through the per-order peak
    values, and the sinc^2 blaze envelope uses the grating constant
    ``C(lambda) = c0 + c1 * (lambda - lref)`` (c0, c1 fitted).

    Four parameters are fitted by least squares with sigma clipping:
    c0, c1, beta (blaze width; 1 = first zeros one FSR from peak), and
    asym (second-order asymmetry of the sinc argument).

    :param flat_response: numpy (2D) array, shape (norders, ncols), the
                          per-order flat-response profile (used as the
                          observed "blaze" to fit against)
    :param wave: numpy (2D) array, shape (norders, ncols), wavelength
                 solution in nm for every pixel
    :param teff: float, effective blackbody temperature of the flat lamp
                 in Kelvin
    :param wave_fit_max: float, red wavelength limit in nm; pixels redder
                         than this are excluded from the fit (but the
                         model is still evaluated there)
    :param sigma_clip: float, sigma-clipping threshold for iterative
                       outlier rejection
    :param peak_half_width: int, half-width in pixels around each order
                            peak used to set the transmission spline knot
                            value (median over this window)
    :param spline_k: int, polynomial degree of the log-transmission
                     spline (1 = linear between order peaks)

    :return: tuple (blaze_model, fit_params) where blaze_model is a
             (norders, ncols) float array and fit_params is a dict with
             keys: teff, c0, c1, beta, asym, rms, wave_fit_max, lref
    """
    # physical constants: h*c/k_B in nm*K
    hc_k = 1.438776877e7
    # diffraction order for every spectral order
    morder = _diffraction_orders(wave)
    # repeat order numbers across all columns
    mm = np.repeat(morder[:, None], wave.shape[1], axis=1).astype(float)
    # |dlambda/dpixel| (nm per pixel) for the flux-density → flux conversion
    dwave = np.abs(np.gradient(wave, axis=1))
    # BB photon density: proportional to 1/(lambda^4 * (exp(hc/lambda/kT)-1))
    with np.errstate(over='ignore', invalid='ignore'):
        photon = 1.0 / (wave ** 4 * np.expm1(hc_k / (wave * teff)))
    # reference wavelength for c1 parameterisation (reduces parameter
    # correlation in the non-linear fit)
    valid = (np.isfinite(flat_response)
             & np.isfinite(wave)
             & (flat_response > 0))
    fitted = valid & (wave < wave_fit_max)
    use = fitted.copy()
    # log of the observed flat-response (finite only where flat_response > 0)
    logobs = np.full(flat_response.shape, np.nan)
    logobs[valid] = np.log(flat_response[valid])
    # normalised wavelength variable for any polynomial transmission model
    wmin = np.min(wave[valid])
    wmax = np.max(wave[valid])
    # reference wavelength to decorrelate c0 and c1
    lref = float(np.median(wave[fitted]))
    # pixel index of each order's observed peak
    index = np.arange(wave.shape[0])
    peaks = np.argmax(
        np.where(fitted, flat_response, -np.inf), axis=1)
    # boolean window: pixels within peak_half_width of the order peak
    pixel = np.arange(wave.shape[1])
    window = (fitted
              & (np.abs(pixel[None, :] - peaks[:, None])
                 <= peak_half_width))

    def _backbone(c0, c1, beta, asym):
        """BB * sinc^2 blaze * dlambda/dpixel (without transmission)."""
        cst = c0 + c1 * (wave - lref)
        ee = mm * wave / cst - 1.0
        env = np.sinc(beta * mm * (ee + asym * ee ** 2)) ** 2
        return photon * np.maximum(env, 1e-8) * dwave

    def _solve_trans(c0, c1, beta, asym):
        """Solve for log-transmission given the grating parameters.

        Uses a linear spline with one knot per order at its peak, where
        the knot value is the median of log(obs) - log(backbone) over
        the peak window.  Returns (logt, residual, (kx, ky)) where kx
        and ky are the spline knot wavelengths and values.
        """
        yy = logobs - np.log(_backbone(c0, c1, beta, asym))
        win = window & use
        rows = np.where(win.any(axis=1))[0]
        kx = np.array([np.median(wave[i][win[i]]) for i in rows])
        ky = np.array([np.median(yy[i][win[i]]) for i in rows])
        srt = np.argsort(kx)
        spline = InterpolatedUnivariateSpline(
            kx[srt], ky[srt], k=spline_k, ext=0)
        logt = spline(wave.ravel()).reshape(wave.shape)
        return logt, yy - logt, (kx[srt], ky[srt])

    # initial estimate of C from m * lambda at the blaze peak per order
    inrange = fitted.any(axis=1)
    cst_start = float(np.mean(
        morder[inrange] * wave[index[inrange], peaks[inrange]]))
    guess = np.array([cst_start, 0.0, 1.0, 0.0])
    slope_max = cst_start / lref
    bounds = (
        [cst_start / 10, -slope_max, 0.1, -100.0],
        [cst_start * 10, slope_max, 5.0, 100.0])
    x_scale = [cst_start, 1e-3 * slope_max, 1.0, 1.0]
    # iterative least-squares fit with sigma clipping (3 passes)
    for _ in range(3):
        def _residual(p):
            return _solve_trans(*p)[1][use]
        fit = least_squares(
            _residual, guess, bounds=bounds,
            loss='soft_l1', f_scale=0.05, x_scale=x_scale)
        guess = fit.x
        logt, res, _ = _solve_trans(*fit.x)
        rms = float(np.std(res[use]))
        use = fitted & (np.abs(res) < sigma_clip * rms)
    # final solution
    c0, c1, beta, asym = fit.x
    logt, res, _ = _solve_trans(c0, c1, beta, asym)
    trans = np.exp(logt)
    blaze_model = _backbone(c0, c1, beta, asym) * trans
    fit_params = dict(
        teff=teff, c0=c0, c1=c1, beta=beta, asym=asym,
        rms=rms, wave_fit_max=wave_fit_max, lref=lref)
    return blaze_model, fit_params


def _diffraction_orders(wave: np.ndarray) -> np.ndarray:
    """
    Derive the diffraction order number for every spectral order from
    the wavelength solution alone.

    At a given detector column all orders share the same diffraction
    angle, so m * lambda is constant.  This gives a direct estimate
    ``m ≈ lambda / |dlambda / dorder|`` plus the integer offset that
    minimises the scatter of m * lambda across all orders.

    :param wave: numpy (2D) array, shape (norders, ncols), wavelength
                 in nm for every pixel

    :return: numpy (1D) int array of length norders, diffraction order
             number for each spectral order
    """
    # wavelength at the central column for each order
    lam = wave[:, wave.shape[1] // 2]
    # sign convention: +1 if order number grows with row index
    step = int(-np.sign(np.median(np.diff(lam))))
    index = np.arange(wave.shape[0])
    # rough estimate of the integer order from the dispersion
    guess = lam / np.abs(np.gradient(lam))
    # integer offset that makes m * lambda flattest across all orders
    start = int(np.round(np.median(guess - step * index)))
    trial = start + np.arange(-2, 3)
    scatter = [
        np.std((t + step * index) * lam)
        / np.mean((t + step * index) * lam)
        for t in trial]
    return trial[int(np.argmin(scatter))] + step * index


def _flat_response_groups(
    order_ranges: Dict[str, Tuple[int, int]],
    spectral_groups: Optional[List[Tuple[str, List[List[int]]]]] = None,
    ) -> List[Tuple[str, List[List[int]]]]:
    """
    Return the trace groupings that define each flat-response spectrum.

    :param order_ranges: dict, localisation-fiber name to trace-label range
    :param spectral_groups: list or None, extracted-spectrum groupings as
                            ``[(name, [[trace...], ...]), ...]``

    :return: list, output fiber/group name and grouped trace labels
    """
    if spectral_groups is not None:
        return spectral_groups
    groups = []
    for fiber, (lo_f, hi_f) in order_ranges.items():
        trace_groups = [[trace] for trace in range(lo_f, hi_f + 1)]
        groups.append((fiber, trace_groups))
    return groups


def _trace_owner(trace: int,
                 order_ranges: Dict[str, Tuple[int, int]]) -> str:
    """
    Return the localisation fiber that owns a trace label.

    :param trace: int, trace label from the localisation maps
    :param order_ranges: dict, localisation-fiber name to trace-label range

    :return: str, localisation fiber name that owns this trace

    :raises ValueError: if the trace label is outside all fiber ranges
    """
    for fiber, (lo_f, hi_f) in order_ranges.items():
        if lo_f <= trace <= hi_f:
            return fiber
    emsg = 'trace label {0} is outside all fiber ranges'
    raise ValueError(emsg.format(trace))


def compute_flat_response(
    order_map: np.ndarray,
    xmap: np.ndarray,
    profiles_noshape: Dict[str, np.ndarray],
    order_ranges: Dict[str, Tuple[int, int]],
    ron: float,
    oversampling: int,
    max_half_cell: float,
    fwhm_pix: float,
    spectral_groups: Optional[List[Tuple[str, List[List[int]]]]] = None
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Compute per-order flat-field response profiles using the
    convolve_irregular algorithm (the order_profile.py approach).

    For each fiber and order, the unshaped profile pixels are convolved
    row by row onto an oversampled regular x-grid and then resampled back
    to integer detector columns.  This gives the flat response free of the
    sub-pixel sampling artefacts that a plain column sum would introduce.

    :param order_map: numpy (2D) array, trace-label map (pixel → order index)
    :param xmap: numpy (2D) array, rectified x coordinate per pixel
    :param profiles_noshape: dict, fiber name → science-frame profile image
    :param order_ranges: dict, fiber name → (lo_label, hi_label) trace range
    :param ron: float, per-pixel readout-noise level in counts
    :param oversampling: int, integer oversampling factor for the output grid
    :param max_half_cell: float, Voronoi cell half-width cap in oversampled
                          pixels (passed directly to convolve_irregular)
    :param fwhm_pix: float, Gaussian kernel FWHM in oversampled pixels
    :param spectral_groups: list or None, extracted-spectrum groupings as
                            ``[(fiber, [[trace...], ...]), ...]``. When
                            provided, flat responses are built for these
                            grouped outputs rather than for localisation
                            fibers only.

    :return: tuple of two dicts (flat_response, flat_response_err), each
             mapping fiber name → 2D float array of shape (norders, ncols)
    """
    ncols = xmap.shape[1]
    # output grid: oversampled detector column positions
    x2 = np.arange(ncols * oversampling, dtype=float)
    # target detector column positions for the final resample
    x_det_cols = np.arange(ncols, dtype=float)
    flat_response: Dict[str, np.ndarray] = dict()
    flat_response_err: Dict[str, np.ndarray] = dict()
    for fiber, trace_groups in _flat_response_groups(order_ranges,
                                                     spectral_groups):
        if len(trace_groups) == 0:
            continue
        owner_fiber = _trace_owner(trace_groups[0][0], order_ranges)
        profile_key = owner_fiber
        if profile_key not in profiles_noshape:
            if fiber not in profiles_noshape:
                continue
            profile_key = fiber
        norders_f = len(trace_groups)
        # pre-allocate output arrays with NaN (unfilled positions stay NaN)
        resp = np.full((norders_f, ncols * oversampling), np.nan)
        resp_err = np.full((norders_f, ncols * oversampling), np.nan)
        for order_num, traces in enumerate(trace_groups):
            # locate pixels belonging to this grouped extracted order
            if len(traces) == 1:
                in_order = order_map == traces[0]
            else:
                in_order = np.isin(order_map, traces)
            if not in_order.any():
                continue
            # detector row indices and per-pixel x coordinates
            row_idx, _ = np.where(in_order)
            x_det = xmap[in_order]
            flux = profiles_noshape[profile_key][in_order]
            # per-pixel noise: photon noise + readout noise in quadrature
            yerr = np.sqrt(np.abs(flux) + ron ** 2)
            # row-by-row convolution; normalize=False gives the row sum
            conv_kwargs = dict(
                group=row_idx,
                normalize=False,
                max_half_cell=max_half_cell,
                fwhm_pix=fwhm_pix,
                weighting='integral',
                min_coverage=0.5)
            result = interpolate.convolve_irregular(
                x_det * oversampling, flux, yerr, x2, **conv_kwargs)
            # push into responce array
            resp[order_num] = result['y']
            resp_err[order_num] = result['err']
        # puhs response into dictionary for return (per fiber)
        flat_response[fiber] = resp
        flat_response_err[fiber] = resp_err
    return flat_response, flat_response_err

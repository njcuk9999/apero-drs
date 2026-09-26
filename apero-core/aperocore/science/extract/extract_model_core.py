#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Model-based all-fiber extraction helper functions

These functions are the profile-independent numerical pieces needed by the
new extraction path: robust image/background modelling, inverse-frame
sampling helpers, readout-noise estimates, and science-frame spectrum
extraction on a rectified pixel coordinate. They do not import apero-drs or
accept APERO recipe/file/config objects.

Created on 2026-09-17

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.ndimage import label
from scipy.optimize import brentq

from aperocore.base import base
from aperocore.math import interpolate

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.extract.extract_model_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def fit_ron(residual: np.ndarray, model: np.ndarray,
            ron_start: float = 8.0, lo: float = 0.05,
            hi: float = 200.0, stride: int = 5) -> float:
    """
    Solve for the readout noise that makes residual/error one sigma wide

    :param residual: numpy array, data minus model
    :param model: numpy array, model flux for the photon-noise term
    :param ron_start: float, value returned if the bracket does not solve
    :param lo: float, lower bracket in electrons
    :param hi: float, upper bracket in electrons
    :param stride: int, spatial stride used to subsample large 2D frames

    :return: float, readout noise in electrons
    """
    residual = np.array(residual, dtype=float)
    model = np.array(model, dtype=float)
    # Use a coarse spatial subsample only for large images so the noise fit is
    #   still stable but no longer dominated by a dense 2D grid.
    if stride > 1 and residual.ndim == 2:
        residual = residual[::stride, ::stride]
        model = model[::stride, ::stride]
    good = np.isfinite(residual) & np.isfinite(model)
    if not good.any():
        return float(ron_start)
    resid = residual[good]
    photon = np.abs(model[good])

    def halfwidth(readout_noise: float) -> float:
        """Half the 16 to 84 percentile width minus one sigma."""
        nsig = resid / np.sqrt(photon + readout_noise ** 2)
        p16, p84 = np.percentile(nsig, [16, 84])
        return 0.5 * (p84 - p16) - 1.0

    if halfwidth(lo) < 0 or halfwidth(hi) > 0:
        return float(ron_start)
    return float(brentq(halfwidth, lo, hi, xtol=1e-3))


def ron_between_orders(image: np.ndarray, background: np.ndarray,
                       order_map: np.ndarray, lag: int = 4) -> float:
    """
    Estimate readout noise from pixels outside all order footprints

    :param image: numpy array (2D), science-frame image in electrons
    :param background: numpy array (2D), background model in electrons
    :param order_map: numpy array (2D), order labels, zero outside orders
    :param lag: int, pixel lag used for the pair difference

    :return: float, readout noise in electrons, or NaN if unsupported
    """
    # Pixels outside orders are the only place where the background and the
    #   detector noise can be estimated without the order signal itself.
    out = ((order_map == 0) & np.isfinite(image)
           & np.isfinite(background))
    pair = out[:, :-lag] & out[:, lag:]
    if pair.sum() < 1000:
        return np.nan
    diff = (image[:, lag:] - image[:, :-lag])[pair]
    grad = (background[:, lag:] - background[:, :-lag])[pair]
    flux = (0.5 * (background[:, lag:] + background[:, :-lag]))[pair]
    mad = np.median(np.abs(diff - np.median(diff)))
    scatter = 1.4826 * mad / np.sqrt(2.0)
    # The variance estimate subtracts the mean photon term and the background
    #   gradient term so that the remaining floor is the readout noise.
    variance = scatter ** 2 - np.mean(flux) - 0.5 * np.mean(grad ** 2)
    return float(np.sqrt(variance)) if variance > 0 else np.nan


def hysteresis_mask(nsig: np.ndarray, nsig1: float = 10.0,
                    nsig2: float = 3.0) -> np.ndarray:
    """
    Mask connected residual structures using a high seed and low grow cut

    :param nsig: numpy array, residual/error map
    :param nsig1: float, sigma level that seeds a masked region
    :param nsig2: float, sigma level that a seeded mask grows into

    :return: numpy array of bool, True where pixels are masked
    """
    abs_nsig = np.abs(np.nan_to_num(nsig))
    candidate = abs_nsig > nsig2
    seed = abs_nsig > nsig1
    if not seed.any():
        return np.zeros(nsig.shape, dtype=bool)
    labels, nlabels = label(candidate)
    if nlabels == 0:
        return np.zeros(nsig.shape, dtype=bool)
    hit = np.zeros(nlabels + 1, dtype=bool)
    hit[np.unique(labels[seed])] = True
    hit[0] = False
    return hit[labels]


def _mad_from_sorted(sorted_box: np.ndarray, count: np.ndarray,
                     median: np.ndarray) -> np.ndarray:
    """Median absolute deviation of finite values in a sorted box."""
    nlast = sorted_box.shape[-1]
    pivot = np.maximum(count - 1, 0) // 2
    nleft = pivot + 1
    nright = np.maximum(count - pivot - 1, 0)

    def arm_left(offset):
        """Sorted absolute deviations on the left side of the median."""
        index = np.clip(pivot[..., None] - offset, 0, nlast - 1)
        value = median[..., None] - np.take_along_axis(sorted_box, index, -1)
        return np.where((offset >= 0) & (offset < nleft[..., None]),
                        value, np.inf)

    def arm_right(offset):
        """Sorted absolute deviations on the right side of the median."""
        index = np.clip(pivot[..., None] + 1 + offset, 0, nlast - 1)
        value = np.take_along_axis(sorted_box, index, -1) - median[..., None]
        return np.where((offset >= 0) & (offset < nright[..., None]),
                        value, np.inf)

    npass = int(np.ceil(np.log2(max(nlast, 2)))) + 1

    def kth(order_index):
        """The order_index-th smallest value in the merged arms."""
        low = np.maximum(0, order_index + 1 - nright)
        high = np.minimum(order_index + 1, nleft)
        for _ in range(npass):
            mid = (low + high) // 2
            left = arm_left(mid[..., None])[..., 0]
            right = arm_right((order_index - mid)[..., None])[..., 0]
            take = (mid < high) & (left < right)
            low = np.where(take, mid + 1, low)
            high = np.where(take, high, mid)
        ileft = low
        iright = order_index + 1 - low
        left = np.where(ileft > 0,
                        arm_left((ileft - 1)[..., None])[..., 0], -np.inf)
        right = np.where(iright > 0,
                         arm_right((iright - 1)[..., None])[..., 0], -np.inf)
        return np.maximum(left, right)

    return 0.5 * (kth(np.maximum(count - 1, 0) // 2) + kth(count // 2))


def background_model(image: np.ndarray, size: Tuple[int, int] = (31, 7),
                     stride_frac: float = 0.5, chunk: int = 128,
                     coarse: bool = False):
    """
    Background model and uncertainty from a NaN-aware coarse median filter

    :param image: numpy array (2D), image to model
    :param size: tuple, median box as (rows, columns)
    :param stride_frac: float, coarse sampling step as a fraction of size
    :param chunk: int, number of coarse rows handled at once
    :param coarse: bool, return coarse grid instead of expanded images

    :return: tuple, either (median, error) full-size images, or
             (median, error, y_positions, x_positions) coarse arrays
    """
    ky, kx = int(size[0]), int(size[1])
    sy = max(int(ky * stride_frac), 1)
    sx = max(int(kx * stride_frac), 1)
    ny, nx = image.shape
    # Pad once so the median boxes are valid all the way to the image edge.
    pad = np.pad(np.array(image, dtype=float),
                 ((ky // 2, ky - 1 - ky // 2),
                  (kx // 2, kx - 1 - kx // 2)),
                 mode='constant', constant_values=np.nan)
    # Work on a coarse grid and keep the statistic local to each box.
    window = sliding_window_view(pad, (ky, kx))[::sy, ::sx]
    nyc, nxc = window.shape[0], window.shape[1]
    median = np.full((nyc, nxc), np.nan)
    error = np.full((nyc, nxc), np.nan)
    for row0 in range(0, nyc, chunk):
        row1 = min(row0 + chunk, nyc)
        block = window[row0:row1].reshape(row1 - row0, nxc,
                                          ky * kx).astype(np.float32)
        # Sort each box to estimate the median and a robust scatter from the
        #   same finite pixel set without materialising a per-box loop.
        sorted_box = np.sort(block, axis=2)
        count = np.sum(np.isfinite(block), axis=2)
        index_low = np.maximum(count - 1, 0) // 2
        index_high = count // 2
        left_med = np.take_along_axis(sorted_box, index_low[..., None], 2)
        right_med = np.take_along_axis(sorted_box, index_high[..., None], 2)
        box_med = 0.5 * (left_med[..., 0] + right_med[..., 0])
        box_mad = _mad_from_sorted(sorted_box, count, box_med)
        median[row0:row1] = box_med.astype(float)
        with np.errstate(invalid='ignore'):
            error[row0:row1] = (1.2533 * (1.4826 * box_mad.astype(float))
                                / np.sqrt(np.maximum(count, 1)))
        error[row0:row1][count < 2] = np.nan
    ys = (np.arange(nyc) * sy).astype(float)
    xs = (np.arange(nxc) * sx).astype(float)
    ys[-1], xs[-1] = float(ny - 1), float(nx - 1)
    if coarse:
        return median, error, ys, xs
    # expand both grids in one call so the shared index/weight arrays are
    #   only computed once
    expanded_median, expanded_error = interpolate.expand_bilinear(
        [median, error], ys, xs, ny, nx)
    return expanded_median, expanded_error


def trace_pixels(labelmap: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Group flat pixel indices by positive integer label

    :param labelmap: numpy array (2D), integer labels, zero means no trace

    :return: tuple, sorted flat positions and start index per label
    """
    flat = np.ascontiguousarray(labelmap, dtype=np.int32).ravel()
    pos = np.flatnonzero(flat)
    labels = flat[pos].astype(np.int32)
    order = np.argsort(labels, kind='stable')
    pos = pos[order]
    labels = labels[order]
    starts = np.searchsorted(labels,
                             np.arange(int(flat.max()) + 2,
                                       dtype=np.int32))
    return pos, np.array(starts)


def spectral_groups(
        ranges: Dict[str, Tuple[int, int]],
        groupings: Optional[List[Tuple[str, List[List[int]]]]] = None
        ) -> List[Tuple[str, List[List[int]]]]:
    """
    Convert fiber trace-label ranges into extraction groups

    :param ranges: dict, fiber -> (first_label, last_label)
    :param groupings: list or None, instrument-supplied grouping definitions

    :return: list, (group_name, trace-label groups)
    """
    if groupings is not None:
        return groupings
    groups = []
    for fiber in ranges:
        lo_fiber, hi_fiber = ranges[fiber]
        traces = [[trace] for trace in range(lo_fiber, hi_fiber + 1)]
        groups.append((fiber, traces))
    return groups


def ribbon_geometry(centers1: np.ndarray, widths1: np.ndarray,
                    centers2: np.ndarray, widths2: np.ndarray,
                    interleaved: bool = False
                    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build tiled row ribbons that contain both fiber profiles.

    :param centers1: numpy array, centers of the first fiber traces
    :param widths1: numpy array, widths of the first fiber traces
    :param centers2: numpy array, centers of the second fiber traces
    :param widths2: numpy array, widths of the second fiber traces
    :param interleaved: bool, whether the first fiber has interleaved traces

    :return: tuple, ribbon centers, first rows and last rows
    """
    centers1 = np.array(centers1, dtype=float)
    widths1 = np.array(widths1, dtype=float)
    centers2 = np.array(centers2, dtype=float)
    widths2 = np.array(widths2, dtype=float)
    per_column = centers1.ndim == 2
    if per_column:
        widths1 = widths1[:, np.newaxis]
        widths2 = widths2[:, np.newaxis]
    if interleaved:
        separation = np.abs(centers1[::2] - centers1[1::2])
        centers1 = (centers1[::2] + centers1[1::2]) / 2.0
        widths1 = separation + (widths1[::2] + widths1[1::2]) / 2.0
    bounds = np.array([centers1 + widths1 // 2,
                       centers1 - widths1 // 2,
                       centers2 + widths2 // 2,
                       centers2 - widths2 // 2])
    ribbon_centers = (bounds.min(axis=0) + bounds.max(axis=0)) / 2.0
    edges = (ribbon_centers[:-1] + ribbon_centers[1:]) / 2.0
    if per_column:
        row1 = np.concatenate([
            (2 * ribbon_centers[:1] - edges[:1]), edges], axis=0)
        row2 = np.concatenate([
            edges, (2 * ribbon_centers[-1:] - edges[-1:])], axis=0)
    else:
        row1 = np.concatenate([[2 * ribbon_centers[0] - edges[0]], edges])
        row2 = np.concatenate([edges,
                               [2 * ribbon_centers[-1] - edges[-1]]])
    row1 = np.round(row1).astype(int)
    row2 = np.round(row2).astype(int)
    return ribbon_centers, row1, row2


def _prep_fit(profile1: np.ndarray, profile2: np.ndarray,
              science: np.ndarray,
              trace_nan_frac: float) -> Tuple[np.ndarray, ...]:
    """Prepare valid masks and NaN-zeroed arrays for ribbon fitting."""
    finite1 = np.isfinite(profile1)
    finite2 = np.isfinite(profile2)
    finite_science = np.isfinite(science)
    valid = finite_science & (finite1 | finite2)
    fittable = np.ones(science.shape[1], dtype=bool)
    for finite in (finite1, finite2):
        owned = np.sum(finite, axis=0)
        kept = np.sum(finite & finite_science, axis=0)
        with np.errstate(invalid='ignore', divide='ignore'):
            frac = np.where(owned > 0,
                            1.0 - kept / np.maximum(owned, 1), 1.0)
            fittable &= frac <= trace_nan_frac
    out1 = np.where(finite1 & valid, profile1, 0.0)
    out2 = np.where(finite2 & valid, profile2, 0.0)
    out_science = np.where(valid, science, 0.0)
    return out1, out2, out_science, valid.astype(float), fittable


def _solve3(profile1: np.ndarray, profile2: np.ndarray, science: np.ndarray,
            unit: np.ndarray, weight: np.ndarray
            ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solve science = amp1 * profile1 + amp2 * profile2 + zero point."""
    wprof1 = weight * profile1
    wprof2 = weight * profile2
    reg = 1e-10
    m11 = np.sum(wprof1 * profile1, axis=0) + reg
    m12 = np.sum(wprof1 * profile2, axis=0)
    m13 = np.sum(wprof1, axis=0)
    m22 = np.sum(wprof2 * profile2, axis=0) + reg
    m23 = np.sum(wprof2, axis=0)
    m33 = np.sum(weight, axis=0) + reg
    r1 = np.sum(wprof1 * science, axis=0)
    r2 = np.sum(wprof2 * science, axis=0)
    r3 = np.sum(weight * science, axis=0)
    with np.errstate(invalid='ignore', divide='ignore'):
        l11 = np.sqrt(m11)
        l21, l31 = m12 / l11, m13 / l11
        l22 = np.sqrt(m22 - l21 * l21)
        l32 = (m23 - l31 * l21) / l22
        l33 = np.sqrt(m33 - l31 * l31 - l32 * l32)
        z1 = r1 / l11
        z2 = (r2 - l21 * z1) / l22
        z3 = (r3 - l31 * z1 - l32 * z2) / l33
        zero_point = z3 / l33
        amp2 = (z2 - l32 * zero_point) / l22
        amp1 = (z1 - l21 * amp2 - l31 * zero_point) / l11
    return amp1, amp2, zero_point


def _blank_unfittable(amp1: np.ndarray, amp2: np.ndarray,
                      zero_point: np.ndarray,
                      fittable: np.ndarray) -> Tuple[np.ndarray, ...]:
    """Set unsupported fit columns to NaN."""
    if fittable.all():
        return amp1, amp2, zero_point
    outs = []
    for array in (amp1, amp2, zero_point):
        out = np.array(array, dtype=float)
        out[~fittable] = np.nan
        outs.append(out)
    return outs[0], outs[1], outs[2]


def simple_fit_batch(profile1: np.ndarray, profile2: np.ndarray,
                     science: np.ndarray, trace_nan_frac: float
                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Plain per-column least-squares fit of two profiles plus zero point

    :param profile1: numpy array (2D), first profile ribbon
    :param profile2: numpy array (2D), second profile ribbon
    :param science: numpy array (2D), science ribbon
    :param max_nan_fraction: float, maximum missing-profile fraction per
                             column before blanking the result

    :return: tuple, amp1, amp2, zero point, each 1D over columns
    """
    fit_out = _prep_fit(profile1, profile2, science, trace_nan_frac)
    profile1c, profile2c, sciencec, unit, fittable = fit_out
    amp1, amp2, zero_point = _solve3(profile1c, profile2c, sciencec,
                                     unit, unit)
    blanked = _blank_unfittable(amp1, amp2, zero_point, fittable)
    return blanked[0], blanked[1], blanked[2]


def _trimmed_start(profile1: np.ndarray, profile2: np.ndarray,
                   science: np.ndarray, keep: float, niter: int,
                   trace_nan_frac: float,
                   prepped: Optional[Tuple[np.ndarray, ...]] = None
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, None]:
    """Get a robust starting fit by iteratively trimming large residuals."""
    if prepped is None:
        profile1c, profile2c, sciencec, unit, _ = _prep_fit(
            profile1, profile2, science, trace_nan_frac)
    else:
        profile1c, profile2c, sciencec, unit = prepped
    npix = science.shape[0]
    nkeep = min(npix, max(int(np.ceil(keep * npix)), 5))
    amp1, amp2, zero_point = _solve3(profile1c, profile2c, sciencec,
                                     unit, unit)
    kept = unit
    for _ in range(niter):
        # Refit on the subset of pixels that remain inside the robust
        #   envelope, then shrink the mask again until the solution settles.
        model = (amp1 * profile1c + amp2 * profile2c
                 + zero_point * unit)
        absres = np.where(unit > 0, np.abs(sciencec - model), np.inf)
        cut = np.partition(absres, nkeep - 1, axis=0)[nkeep - 1]
        new_kept = (absres <= cut) * unit
        if np.array_equal(new_kept, kept):
            break
        kept = new_kept
        amp1, amp2, zero_point = _solve3(profile1c, profile2c, sciencec,
                                         unit, kept)
    return amp1, amp2, zero_point, None


def weighted_fit_batch(profile1: np.ndarray, profile2: np.ndarray,
                       science: np.ndarray, noise: float,
                       nu: float, n_iter: int, trim_keep: float,
                       trace_nan_frac: float
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
                                  np.ndarray]:
    """
    Robust per-column fit of two profiles plus zero point

    :param profile1: numpy array (2D), first profile ribbon
    :param profile2: numpy array (2D), second profile ribbon
    :param science: numpy array (2D), science ribbon
    :param noise: float, readout noise in the same units as science
    :param nu: float, Student-t degrees of freedom for residual weighting
    :param niter: int, number of reweighting iterations
    :param max_nan_fraction: float, maximum missing-profile fraction per
                             column before blanking the result

    :return: tuple, amp1, amp2, zero point and pixel weights
    """
    fit_out = _prep_fit(profile1, profile2, science, trace_nan_frac)
    profile1c, profile2c, sciencec, unit, fittable = fit_out
    xout = _trimmed_start(
        profile1, profile2, science,
        keep=trim_keep, niter=n_iter, trace_nan_frac=trace_nan_frac,
        prepped=(profile1c, profile2c, sciencec, unit))
    amp1, amp2, zero_point, _ = xout
    weight = unit.copy()
    noise2 = float(noise) ** 2
    for _ in range(int(n_iter)):
        # The robust weights are updated from the current residuals, so the
        #   next linear solve follows the same two-profile model with lower
        #   weight on the outliers.
        model = (amp1 * profile1c + amp2 * profile2c
                 + zero_point * unit)
        variance = np.abs(model) + noise2
        with np.errstate(invalid='ignore', divide='ignore'):
            nsig2 = (sciencec - model) ** 2 / variance
            if nu is None:
                gauss = np.exp(-0.5 * nsig2)
                robust = gauss / (gauss + 1e-3)
            else:
                robust = (nu + 1.0) / (nu + nsig2)
            weight = np.where(unit > 0, robust / variance, 0.0)
        amp1, amp2, zero_point = _solve3(profile1c, profile2c, sciencec,
                                         unit, weight)
    amp1, amp2, zero_point = _blank_unfittable(amp1, amp2, zero_point,
                                               fittable)
    return amp1, amp2, zero_point, weight


def extract_orders(image: np.ndarray, profile1: np.ndarray,
                   profile2: np.ndarray, row1: np.ndarray,
                   row2: np.ndarray, noise: float, nclip: int,
                   nsig_clip: float, zp_mad_cut: float, robust: bool,
                   nu: float, n_iter: int, trim_keep: float,
                   trace_nan_frac: float, products: bool, extras: bool
                   ) -> Tuple[Any, ...]:
    """
    Fit every order ribbon as two profiles plus a zero point.

    :param image: numpy array (2D), straightened science image in electrons
    :param profile1: numpy array (2D), first straightened fiber profile
    :param profile2: numpy array (2D), second straightened fiber profile
    :param row1: numpy array (1D), first row of each ribbon
    :param row2: numpy array (1D), last row of each ribbon
    :param noise: float, readout noise in electrons
    :param nclip: int, number of robust refit passes
    :param nsig_clip: float, residual clipping threshold
    :param zp_mad_cut: float, zero-point outlier threshold in MADs
    :param robust: bool, use soft robust fitting with clipping
    :param products: bool, build image-sized model products
    :param extras: bool, build residual/error diagnostic products

    :return: tuple, flux1, flux2, zero points, model products, residual,
             sigma, error and zero-point image
    """
    ny, nx = image.shape
    norders = len(row1)
    flux1 = np.full((norders, nx), np.nan)
    flux2 = np.full((norders, nx), np.nan)
    zero_points = np.full((norders, nx), np.nan)
    model1 = np.full((ny, nx), np.nan)
    model2 = np.full((ny, nx), np.nan)
    residual = np.full((ny, nx), np.nan)
    nsig = np.full((ny, nx), np.nan)
    error = np.full((ny, nx), np.nan)
    zero_image = np.full((ny, nx), np.nan)
    for order_num in range(norders):
        y1, y2 = int(row1[order_num]), int(row2[order_num])
        if y1 < 0 or y2 > ny:
            continue
        # Each ribbon is handled independently, but all columns share the
        #   same order-local profile pair and a single fitted zero point.
        rib_sci = np.array(image[y1:y2], dtype=float)
        rib1 = np.array(profile1[y1:y2], dtype=float)
        rib2 = np.array(profile2[y1:y2], dtype=float)
        if robust:
            for _ in range(nclip):
                xargs = [rib1, rib2, rib_sci, noise]
                xkwargs = dict(nu=nu, n_iter=n_iter,
                               trim_keep=trim_keep,
                               trace_nan_frac=trace_nan_frac)
                xout = weighted_fit_batch(*xargs, **xkwargs)
                amp1, amp2, zero_point = xout[:3]
                model = (amp1 * np.nan_to_num(rib1)
                         + amp2 * np.nan_to_num(rib2) + zero_point)
                err = np.sqrt(np.abs(model) + noise ** 2)
                with np.errstate(invalid='ignore'):
                    rib_sci[(rib_sci - model) / err > nsig_clip] = np.nan
        else:
            xargs = [rib1, rib2, rib_sci, noise]
            xkwargs = dict(nu=nu, n_iter=n_iter,
                           trim_keep=trim_keep,
                           trace_nan_frac=trace_nan_frac)
            xout = weighted_fit_batch(*xargs, **xkwargs)
            amp1, amp2, zero_point = xout[:3]
            model = (amp1 * np.nan_to_num(rib1)
                     + amp2 * np.nan_to_num(rib2) + zero_point)
        zero_point[zero_point == 0] = np.nan
        med = np.nanmedian(zero_point)
        mad = np.nanmedian(np.abs(zero_point - med))
        with np.errstate(invalid='ignore', divide='ignore'):
            bad = np.abs(zero_point - med) / (mad + 1e-30) > zp_mad_cut
        flux1[order_num] = amp1
        flux2[order_num] = amp2
        zero_points[order_num] = zero_point
        if not products:
            continue
        mod1 = amp1 * np.nan_to_num(rib1)
        mod2 = amp2 * np.nan_to_num(rib2)
        mod1[:, bad] = np.nan
        mod2[:, bad] = np.nan
        model1[y1:y2] = mod1
        model2[y1:y2] = mod2
        if not extras:
            continue
        rib_zero = np.repeat(zero_point[None, :], y2 - y1, axis=0)
        rib_zero[:, bad] = np.nan
        zero_image[y1:y2] = rib_zero
        rib_res = np.array(image[y1:y2], dtype=float) - model
        rib_res[:, bad] = np.nan
        residual[y1:y2] = rib_res
        rib_err = np.sqrt(np.abs(model) + float(noise) ** 2)
        rib_err[:, bad] = np.nan
        error[y1:y2] = rib_err
        with np.errstate(invalid='ignore', divide='ignore'):
            nsig[y1:y2] = rib_res / rib_err
    if not products:
        return (flux1, flux2, zero_points, None, None, None, None,
                None, None, None)
    xout = interpolate.fill_nans_nearest([model1, model2])
    model1, model2 = xout
    image_model = model1 + model2
    return (flux1, flux2, zero_points, model1, model2, image_model,
            residual, nsig, error, zero_image)


def model_spectra(flux1: np.ndarray, flux2: np.ndarray,
                  fiber1: str, fiber2: str
                  ) -> Dict[str, np.ndarray]:
    """
    Package fitted fiber amplitudes as extracted spectra.

    The amplitudes returned by ``extract_orders`` are already one value per
    order and dispersion column. They are therefore the new extraction
    products, without another spatial extraction or resampling step.

    :param flux1: numpy array (2D), first fiber order spectra
    :param flux2: numpy array (2D), second fiber order spectra
    :param fiber1: str, first fiber product name
    :param fiber2: str, second fiber product name

    :return: dict, individual fiber spectra and their combined spectrum
    """
    spectra = dict()
    spectra[fiber1] = np.array(flux1, dtype=float)
    spectra[fiber2] = np.array(flux2, dtype=float)
    with np.errstate(invalid='ignore'):
        spectra['COMBINED'] = np.nansum(
            np.stack([spectra[fiber1], spectra[fiber2]]), axis=0)
    both_nan = ~np.isfinite(spectra[fiber1]) & ~np.isfinite(spectra[fiber2])
    spectra['COMBINED'][both_nan] = np.nan
    return spectra


def model_in_science(flux1: np.ndarray, flux2: np.ndarray,
                     zero_point: np.ndarray, nearest: np.ndarray,
                     xmap: np.ndarray, profiles: Dict[str, np.ndarray],
                     ranges: Dict[str, Tuple[int, int]],
                     fibers: Tuple[str, str] = ('A', 'B')
                     ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build an all-fiber model directly in the science frame

    :param flux1: numpy array (2D), first fiber amplitudes
    :param flux2: numpy array (2D), second fiber amplitudes
    :param zero_point: numpy array (2D), fitted zero points
    :param nearest: numpy array (2D), nearest trace label per pixel
    :param xmap: numpy array (2D), rectified x coordinate per pixel
    :param profiles: dict, fiber -> science-frame order profile image
    :param ranges: dict, fiber -> first/last trace labels

    :return: tuple, fiber model and zero-point model in science frame
    """
    columns = np.arange(xmap.shape[1], dtype=float)
    fiber_model = np.zeros(xmap.size, dtype=float)
    zmodel = np.zeros(xmap.size, dtype=float)
    trace_pos, trace_start = trace_pixels(nearest)
    xflat = np.ascontiguousarray(xmap).ravel()
    pflat = {key: np.ascontiguousarray(profiles[key]).ravel()
             for key in profiles}
    amplitude_map = dict(zip(fibers, (flux1, flux2)))
    for fiber in fibers:
        lo_fiber, hi_fiber = ranges[fiber]
        amplitudes = amplitude_map[fiber]
        norders = amplitudes.shape[0]
        per_order = max((hi_fiber - lo_fiber + 1) // norders, 1)
        for trace in range(lo_fiber, hi_fiber + 1):
            order_num = min((trace - lo_fiber) // per_order, norders - 1)
            indices = trace_pos[trace_start[trace]:trace_start[trace + 1]]
            if indices.size == 0:
                continue
            amp_spline = interpolate.finite_spline(
                columns, amplitudes[order_num])
            zp_spline = interpolate.finite_spline(
                columns, zero_point[order_num])
            xsel = xflat[indices]
            if amp_spline is not None:
                profile = np.nan_to_num(pflat[fiber][indices])
                fiber_model[indices] += amp_spline(xsel) * profile
            if zp_spline is not None:
                zmodel[indices] = zp_spline(xsel)
    return fiber_model.reshape(xmap.shape), zmodel.reshape(xmap.shape)


def extract_spectra(image: np.ndarray, error: np.ndarray,
                    order_map: np.ndarray, xmap: np.ndarray,
                    profiles: Dict[str, np.ndarray],
                    ranges: Dict[str, Tuple[int, int]], xgrid: np.ndarray,
                    groupings: Optional[List[Tuple[str, List[List[int]]]]] = None,
                    window: float = 0.45, polyorder: int = 2,
                    cut: float = 3.0, weight_kind: str = 'gauss',
                    minpts: int = 3
                    ) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """
    Extract grouped spectra in the unshaped science frame

    :return: dict, group name -> (spectrum, error), each n_orders x n_grid
    """
    outputs = dict()
    trace_pos, trace_start = trace_pixels(order_map)
    xflat = np.ascontiguousarray(xmap).ravel()
    iflat = np.ascontiguousarray(image).ravel()
    eflat = np.ascontiguousarray(error).ravel()
    pflat = {key: np.ascontiguousarray(profiles[key]).ravel()
             for key in profiles}
    for name, orders in spectral_groups(ranges, groupings):
        spec = np.full((len(orders), xgrid.size), np.nan)
        espec = np.full((len(orders), xgrid.size), np.nan)
        for order_num, traces in enumerate(orders):
            indices = np.concatenate([trace_pos[trace_start[trace]:
                                                trace_start[trace + 1]]
                                      for trace in traces])
            if indices.size == 0:
                continue
            fiber = _fiber_for_trace(traces[0], ranges)
            prof = pflat[fiber][indices]
            with np.errstate(invalid='ignore', divide='ignore'):
                values = iflat[indices] / prof
                errors = eflat[indices] / prof
            fit_out = interpolate.irregular_savgol(
                xflat[indices], values, xgrid, window=window, yerr=errors,
                polyorder=polyorder, cut=cut, weight_kind=weight_kind,
                minpts=minpts)
            spec[order_num], espec[order_num] = fit_out
        # mask out any values with extremely high errors
        bad = espec > 2 * np.nanpercentile(espec, 95)
        spec[bad] = np.nan
        espec[bad] = np.nan
        # push into output dictionary
        outputs[name] = (spec, espec)
    return outputs


def _fiber_for_trace(trace: int, ranges: Dict[str, Tuple[int, int]]) -> str:
    """Return the fiber owning a trace label."""
    for fiber, (lo_fiber, hi_fiber) in ranges.items():
        if lo_fiber <= trace <= hi_fiber:
            return fiber
    emsg = 'trace label {0} is outside all fiber ranges'
    raise ValueError(emsg.format(trace))


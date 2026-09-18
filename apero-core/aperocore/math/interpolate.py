#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generic interpolation and local fitting algorithms."""
from typing import List, Optional, Tuple, Union

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.ndimage import convolve
from scipy.ndimage import distance_transform_edt

# =============================================================================
# Define functions
# =============================================================================
def fill_nans_nearest(image: Union[np.ndarray, List[np.ndarray]],
                      nsmooth: int = 0
                      ) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Fill non-finite pixels from the nearest finite pixel.

    :param image: numpy array (2D), or a list of arrays with compatible holes
    :param nsmooth: int, smoothing passes applied only to filled pixels

    :return: filled array, or a list of filled arrays
    """
    single = not isinstance(image, (list, tuple))
    images = [image] if single else list(image)
    outs = [np.array(one, dtype=float) for one in images]
    kernel = np.ones((3, 3)) / 9.0
    solved = []
    for out in outs:
        bad = ~np.isfinite(out)
        if not bad.any() or bad.all():
            continue
        indices = None
        for prev_bad, prev_indices in solved:
            if np.array_equal(bad, prev_bad):
                indices = prev_indices
                break
        if indices is None:
            indices = distance_transform_edt(
                bad, return_distances=False, return_indices=True)
            solved.append((bad, indices))
        out[bad] = out[tuple(indices)][bad]
        for _ in range(nsmooth):
            out[bad] = convolve(out, kernel, mode='nearest')[bad]
    return outs[0] if single else outs


def finite_spline(xpos: np.ndarray, values: np.ndarray):
    """
    Build a cubic spline through finite samples when enough points exist.

    :param xpos: numpy array (1D), sample positions
    :param values: numpy array (1D), sample values with possible NaNs

    :return: cubic spline or None when fewer than four samples are finite
    """
    good = np.isfinite(values)
    if good.sum() < 4:
        return None
    return CubicSpline(xpos[good], values[good], extrapolate=True)


def expand_bilinear(coarse: np.ndarray, ys: np.ndarray, xs: np.ndarray,
                    ny: int, nx: int) -> np.ndarray:
    """Bilinearly expand a coarse 2D grid to a full-resolution image."""
    rows = np.arange(ny, dtype=float)
    cols = np.arange(nx, dtype=float)
    iy = np.clip(np.searchsorted(ys, rows, 'right') - 1, 0, ys.size - 2)
    ix = np.clip(np.searchsorted(xs, cols, 'right') - 1, 0, xs.size - 2)
    yden = ys[iy + 1] - ys[iy]
    xden = xs[ix + 1] - xs[ix]
    wy = np.divide(rows - ys[iy], yden,
                   out=np.zeros_like(rows, dtype=float), where=yden != 0)
    wx = np.divide(cols - xs[ix], xden,
                   out=np.zeros_like(cols, dtype=float), where=xden != 0)
    row_values = (coarse[iy] * (1.0 - wy[:, None])
                  + coarse[iy + 1] * wy[:, None])
    return (row_values[:, ix] * (1.0 - wx)
            + row_values[:, ix + 1] * wx)


def sample_bilinear(coarse: Union[np.ndarray, List[np.ndarray]],
                    ys: np.ndarray, xs: np.ndarray, rows: np.ndarray,
                    cols: np.ndarray
                    ) -> Union[np.ndarray, List[np.ndarray]]:
    """Bilinearly sample one or more coarse grids at arbitrary positions."""
    single = not isinstance(coarse, (list, tuple))
    maps = [coarse] if single else list(coarse)
    iy = np.clip(np.searchsorted(ys, rows, 'right') - 1, 0, ys.size - 2)
    ix = np.clip(np.searchsorted(xs, cols, 'right') - 1, 0, xs.size - 2)
    yden = ys[iy + 1] - ys[iy]
    xden = xs[ix + 1] - xs[ix]
    wy = np.divide(rows - ys[iy], yden,
                   out=np.zeros_like(rows, dtype=float), where=yden != 0)
    wx = np.divide(cols - xs[ix], xden,
                   out=np.zeros_like(cols, dtype=float), where=xden != 0)
    ncol = maps[0].shape[1]
    flat00 = iy.astype(np.int64) * ncol + ix
    flat01 = flat00 + 1
    flat10 = flat00 + ncol
    flat11 = flat10 + 1
    outs = []
    for one_map in maps:
        flat = one_map.ravel()
        top = flat[flat00] * (1.0 - wx) + flat[flat01] * wx
        bottom = flat[flat10] * (1.0 - wx) + flat[flat11] * wx
        outs.append(top * (1.0 - wy) + bottom * wy)
    return outs[0] if single else outs


def kernel_total(xpos: np.ndarray, values: np.ndarray, xout: np.ndarray,
                 window: float = 0.45, cut: float = 3.0,
                 weight_kind: str = 'gauss') -> np.ndarray:
    """Total irregular samples onto an output grid using a normalized kernel."""
    xpos = np.asarray(xpos, dtype=float).ravel()
    values = np.asarray(values, dtype=float).ravel()
    xout = np.asarray(xout, dtype=float).ravel()
    out = np.full(xout.size, np.nan)
    good = np.isfinite(xpos) & np.isfinite(values)
    xpos, values = xpos[good], values[good]
    if xpos.size == 0 or xout.size < 2:
        return out
    order = np.argsort(xpos)
    xpos, values = xpos[order], values[order]
    triangular = str(weight_kind).lower().startswith('tri')
    radius = window if triangular else cut * window
    lefts = np.searchsorted(xpos, xout - radius, side='left')
    rights = np.searchsorted(xpos, xout + radius, side='right')
    count = rights - lefts
    total = int(count.sum())
    if total == 0:
        return out
    jidx = np.repeat(np.arange(xout.size), count)
    ends = np.cumsum(count)
    offsets = np.arange(total) - np.repeat(ends - count, count)
    iidx = np.repeat(lefts, count) + offsets
    delta = xpos[iidx] - xout[jidx]
    if triangular:
        kernel = 1.0 - np.abs(delta) / window
        np.clip(kernel, 0.0, None, out=kernel)
    else:
        kernel = np.exp(-0.5 * (delta / window) ** 2)
    norm = np.bincount(iidx, weights=kernel, minlength=xpos.size)
    share = np.where(norm[iidx] > 0, kernel / norm[iidx], 0.0)
    filled = count > 0
    result = np.zeros(xout.size)
    result[filled] = np.add.reduceat(share * values[iidx],
                                     (ends - count)[filled])
    step = float(np.median(np.diff(xout)))
    out[filled] = result[filled] / step
    return out


def irregular_savgol(xpos: np.ndarray, values: np.ndarray,
                     xout: np.ndarray, window: float = 0.45,
                     polyorder: int = 2,
                     yerr: Optional[np.ndarray] = None,
                     cut: float = 3.0,
                     weight_kind: str = 'gauss',
                     minpts: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """Fit local polynomials to values sampled on an irregular grid."""
    xpos = np.asarray(xpos, dtype=float).ravel()
    values = np.asarray(values, dtype=float).ravel()
    xout = np.asarray(xout, dtype=float).ravel()
    nout = xout.size
    yout = np.full(nout, np.nan)
    eout = np.full(nout, np.nan)
    ncoeff = polyorder + 1
    if polyorder != 2:
        return yout, eout
    if yerr is None:
        ivar = np.ones(values.size)
    else:
        errors = np.asarray(yerr, dtype=float).ravel()
        with np.errstate(divide='ignore', invalid='ignore'):
            ivar = np.where((errors > 0) & np.isfinite(errors),
                            1.0 / errors ** 2, 0.0)
    good = np.isfinite(xpos) & np.isfinite(values) & (ivar > 0)
    xpos, values, ivar = xpos[good], values[good], ivar[good]
    if xpos.size < ncoeff + minpts:
        return yout, eout
    order = np.argsort(xpos)
    xpos, values, ivar = xpos[order], values[order], ivar[order]
    triangular = str(weight_kind).lower().startswith('tri')
    radius = window if triangular else cut * window
    lefts = np.searchsorted(xpos, xout - radius, side='left')
    rights = np.searchsorted(xpos, xout + radius, side='right')
    counts = rights - lefts
    usable = counts >= ncoeff + minpts
    if not usable.any():
        return yout, eout
    cnt = np.where(usable, counts, 0)
    total = int(cnt.sum())
    jidx = np.repeat(np.arange(nout), cnt)
    ends = np.cumsum(cnt)
    offsets = np.arange(total) - np.repeat(ends - cnt, cnt)
    iidx = np.repeat(np.where(usable, lefts, 0), cnt) + offsets
    delta = xpos[iidx] - xout[jidx]
    if triangular:
        gauss = 1.0 - np.abs(delta) / window
        np.clip(gauss, 0.0, None, out=gauss)
    else:
        gauss = np.exp(-0.5 * (delta / window) ** 2)
    weight = gauss * ivar[iidx]
    yval = values[iidx]
    delta2 = delta * delta
    filled = cnt > 0
    starts = (ends - cnt)[filled]

    def _sum(samples: np.ndarray) -> np.ndarray:
        """Sum samples over each output window."""
        out = np.zeros(nout)
        out[filled] = np.add.reduceat(samples, starts)
        return out

    smom = [_sum(weight), _sum(weight * delta), _sum(weight * delta2),
            _sum(weight * delta2 * delta), _sum(weight * delta2 * delta2)]
    rhs = [_sum(weight * yval), _sum(weight * delta * yval),
           _sum(weight * delta2 * yval)]
    wt2 = gauss * gauss * ivar[iidx]
    cmom = [_sum(wt2), _sum(wt2 * delta), _sum(wt2 * delta2),
            _sum(wt2 * delta2 * delta), _sum(wt2 * delta2 * delta2)]
    m00, m01, m02 = smom[0], smom[1], smom[2]
    m11, m12, m22 = smom[2], smom[3], smom[4]
    cof0 = m11 * m22 - m12 * m12
    cof1 = m02 * m12 - m01 * m22
    cof2 = m01 * m12 - m02 * m11
    det = m00 * cof0 + m01 * cof1 + m02 * cof2
    sel = usable & np.isfinite(det) & (np.abs(det) > 0)
    if not sel.any():
        return yout, eout
    with np.errstate(invalid='ignore', divide='ignore'):
        row = np.stack([cof0, cof1, cof2], axis=-1) / det[:, None]
        value = (row * np.stack(rhs, axis=-1)).sum(axis=1)
        cmat = np.empty((nout, 3, 3))
        for ia in range(3):
            for ib in range(3):
                cmat[:, ia, ib] = cmom[ia + ib]
        variance = np.einsum('nj,njk,nk->n', row, cmat, row)
    yout[sel] = value[sel]
    eout[sel] = np.where(variance[sel] > 0,
                         np.sqrt(np.abs(variance[sel])), np.nan)
    return yout, eout
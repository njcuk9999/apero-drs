#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generic interpolation and local fitting algorithms."""
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from scipy import sparse as _sp_sparse
from scipy.interpolate import CubicSpline
from scipy.ndimage import convolve
from scipy.ndimage import distance_transform_edt
from scipy.special import erf as _sp_erf

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


def expand_bilinear(coarse: Union[np.ndarray, List[np.ndarray]],
                    ys: np.ndarray, xs: np.ndarray, ny: int, nx: int
                    ) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Bilinearly expand one or more coarse 2D grids to a full-resolution image.

    Accepting a list of coarse grids lets callers share the index/weight
    computation across multiple grids sampled on the same (ys, xs)
    coordinates (e.g. a background median and its error map), which is
    where most of the wall-time in the single-grid path is spent.

    :param coarse: numpy array (2D) or list of arrays sharing the same
                   coarse grid shape (ys.size, xs.size)
    :param ys: numpy array (1D), coarse-grid row positions (sorted)
    :param xs: numpy array (1D), coarse-grid column positions (sorted)
    :param ny: int, output row count
    :param nx: int, output column count

    :return: expanded array, or list of expanded arrays if ``coarse`` was
             a list/tuple
    """
    single = not isinstance(coarse, (list, tuple))
    maps = [coarse] if single else list(coarse)
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
    # precompute row-slice views used by every map so the same indexing
    #   into ys is only paid once even when several coarse maps are passed
    one_minus_wy = (1.0 - wy)[:, None]
    wy_col = wy[:, None]
    one_minus_wx = 1.0 - wx
    outs = []
    for one_map in maps:
        # interpolate along the row axis first, then the column axis; this
        #   is a plain 2D bilinear expansion split into two 1D passes
        row_values = one_map[iy] * one_minus_wy + one_map[iy + 1] * wy_col
        outs.append(row_values[:, ix] * one_minus_wx
                    + row_values[:, ix + 1] * wx)
    return outs[0] if single else outs


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
    xpos = np.array(xpos, dtype=float).ravel()
    values = np.array(values, dtype=float).ravel()
    xout = np.array(xout, dtype=float).ravel()
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
    xpos = np.array(xpos, dtype=float).ravel()
    values = np.array(values, dtype=float).ravel()
    xout = np.array(xout, dtype=float).ravel()
    nout = xout.size
    yout = np.full(nout, np.nan)
    eout = np.full(nout, np.nan)
    ncoeff = polyorder + 1
    if polyorder != 2:
        return yout, eout
    if yerr is None:
        ivar = np.ones(values.size)
    else:
        errors = np.array(yerr, dtype=float).ravel()
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


# =============================================================================
# Kernel-based convolution of irregularly sampled data onto a regular grid
# =============================================================================
class Kernel:
    """
    Abstract interface for a parametric convolution kernel.

    Distances dx are in x units (same units as the input positions).
    Subclasses must implement profile, cdf, and half_width.
    """

    def profile(self, dx: np.ndarray) -> np.ndarray:
        """
        Kernel shape normalised to 1 at its peak.

        :param dx: numpy array, signed distances from the kernel centre

        :return: numpy array, kernel values in [0, 1]
        """
        raise NotImplementedError

    def cdf(self, dx: np.ndarray) -> np.ndarray:
        """
        Cumulative integral of the unit-area kernel from -inf to dx.

        :param dx: numpy array, upper limit of integration

        :return: numpy array, CDF values in [0, 1]
        """
        raise NotImplementedError

    def half_width(self, threshold: float) -> float:
        """
        Return the half-width beyond which profile(dx) < threshold * peak.

        :param threshold: float, fractional cutoff (e.g. 1e-6)

        :return: float, half-width in x units
        """
        raise NotImplementedError


class GaussianKernel(Kernel):
    """
    Gaussian convolution kernel parameterised by its FWHM.

    :param fwhm: float, full-width at half-maximum in x units
    """

    def __init__(self, fwhm: float):
        """
        Initialise a Gaussian kernel.

        :param fwhm: float, full-width at half-maximum in x units
        """
        self.fwhm = float(fwhm)
        # sigma derived from FWHM = 2 * sqrt(2 * ln 2) * sigma
        self.sigma = self.fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    def profile(self, dx: np.ndarray) -> np.ndarray:
        """
        Gaussian profile normalised to 1 at the centre.

        :param dx: numpy array, offsets from the kernel centre

        :return: numpy array, Gaussian values in [0, 1]
        """
        return np.exp(-0.5 * (dx / self.sigma) ** 2)

    def cdf(self, dx: np.ndarray) -> np.ndarray:
        """
        Cumulative distribution of the unit-area Gaussian.

        :param dx: numpy array, upper limit of integration

        :return: numpy array, CDF values in [0, 1]
        """
        return 0.5 * (1.0 + _sp_erf(dx / (self.sigma * np.sqrt(2.0))))

    def half_width(self, threshold: float) -> float:
        """
        Return |dx| at which the Gaussian drops below threshold * peak.

        :param threshold: float, fractional peak cutoff

        :return: float, half-width in x units
        """
        return self.sigma * np.sqrt(-2.0 * np.log(threshold))


def _cell_edges(x: np.ndarray,
                max_half_cell: Optional[float] = None
                ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build Voronoi cell boundaries (midpoints) for sorted sample positions.

    End cells are made symmetric around the first and last sample.
    max_half_cell caps any cell that would otherwise span a gap.

    :param x: numpy array (1D), sorted sample x positions
    :param max_half_cell: float or None, maximum half-cell width in x units

    :return: tuple (left, right), 1D arrays of cell left and right edges
    """
    if x.size == 1:
        # single sample: infinite cell unless max_half_cell is set
        half = np.inf if max_half_cell is None else max_half_cell
        return x - half, x + half
    # midpoints between adjacent samples form the interior boundaries
    mid = 0.5 * (x[1:] + x[:-1])
    # mirror the first and last gap to give symmetric end cells
    left = np.concatenate([[x[0] - (mid[0] - x[0])], mid])
    right = np.concatenate([mid, [x[-1] + (x[-1] - mid[-1])]])
    if max_half_cell is not None:
        # cap cells that would span a gap or the detector edge
        left = np.maximum(left, x - max_half_cell)
        right = np.minimum(right, x + max_half_cell)
    return left, right


def _window_pairs(left: np.ndarray, right: np.ndarray,
                  x2: np.ndarray, half_width: float
                  ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find all (output pixel j, input sample i) pairs within the kernel window.

    Uses two binary searches on the sorted cell-edge arrays so the cost
    scales as O(n_out * log n_in) rather than O(n_out * n_in).

    :param left: numpy array (1D), sorted left cell edges of input samples
    :param right: numpy array (1D), sorted right cell edges (same length)
    :param x2: numpy array (1D), output grid positions
    :param half_width: float, kernel half-width, defines the search window

    :return: tuple (rows, cols), flat index arrays into x2 and the input
             sample array; one entry per overlapping (output, input) pair
    """
    # samples whose right edge is inside [x2_j - hw, x2_j + hw]
    lo = np.searchsorted(right, x2 - half_width, side='right')
    hi = np.searchsorted(left, x2 + half_width, side='left')
    counts = np.clip(hi - lo, 0, None)
    rows = np.repeat(np.arange(x2.size), counts)
    starts = np.cumsum(counts) - counts
    cols = lo[rows] + (np.arange(counts.sum()) - starts[rows])
    return rows, cols


def convolve_irregular(
        x: np.ndarray,
        y: np.ndarray,
        yerr: np.ndarray,
        x2: np.ndarray,
        kernel: Optional[Kernel] = None,
        fwhm_pix: float = 2.0,
        threshold: float = 1e-6,
        weighting: str = 'integral',
        max_half_cell: Optional[float] = None,
        min_coverage: float = 0.5,
        group: Optional[np.ndarray] = None,
        normalize: bool = True,
        return_matrix: bool = False
) -> Dict[str, np.ndarray]:
    """
    Convolve irregularly sampled (x, y, yerr) onto the regular grid x2.

    Each input sample owns a Voronoi cell bounded by midpoints to its
    neighbours.  The weight of sample i in output pixel j equals the
    kernel mass that falls inside that cell::

        w_ij = CDF(right_i - x2_j) - CDF(left_i - x2_j)

    This is the exact convolution of the piecewise-constant (nearest-
    neighbour) interpolant of the data, which makes dense clusters
    contribute proportionally to the x range they occupy rather than
    their count.

    When group is supplied (e.g. detector row indices for a spectrograph
    flat), cells are built within each group independently.  Setting
    normalize=False then gives the resampled equivalent of a plain
    column sum over rows (use with weighting='integral').

    :param x: numpy array (1D), input sample positions in any order
    :param y: numpy array (1D), input sample values
    :param yerr: numpy array (1D), input uncertainties; non-positive and
                 non-finite values are excluded automatically
    :param x2: numpy array (1D), strictly increasing regular output grid
    :param kernel: Kernel instance or None; a GaussianKernel with FWHM
                   equal to fwhm_pix output pixels is used when None
    :param fwhm_pix: float, FWHM in x2 pixel units for the default kernel
    :param threshold: float, samples where the kernel < threshold * peak
                      are ignored (default 1e-6, i.e. +/-5.26 sigma)
    :param weighting: str, 'integral' -> w_ij = kernel mass in cell
                      (true piecewise-constant convolution);
                      'ivar' -> w_ij = kernel(x_i - x2_j) / yerr_i^2
                      (minimum-variance kernel-weighted mean)
    :param max_half_cell: float or None, cap on cell half-width in x
                          units; prevents a sample at a gap edge from
                          claiming half the gap so coverage drops there
    :param min_coverage: float, output pixels whose fraction of kernel
                         mass backed by data is below this are set to NaN
    :param group: numpy array (1D) or None, integer group labels; cells
                  are built within each group only (e.g. detector rows)
    :param normalize: bool, True -> weighted mean over all groups;
                      False -> weighted sum (normalize=False requires
                      weighting='integral')
    :param return_matrix: bool, if True also return the sparse linear
                          operator W with y2 = W @ y

    :return: dict with keys:
             'y'        - output values (NaN where coverage < min_coverage)
             'err'      - propagated uncertainties (same masking)
             'coverage' - mean fraction of kernel mass backed by data
             'sum_w'    - sum of cell weights (effective group count)
             'npts'     - number of input samples used per output pixel
             'matrix'   - sparse (n_out, n_in) operator (if return_matrix)
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    yerr = np.array(yerr, dtype=float)
    x2 = np.array(x2, dtype=float)
    n_in, n_out = x.size, x2.size
    # validate the regular output grid
    step = np.diff(x2)
    if n_out < 2 or np.any(step <= 0):
        raise ValueError(
            'x2 must be strictly increasing with >= 2 points')
    dx2 = step.mean()
    if not np.allclose(step, dx2, rtol=1e-6, atol=0):
        raise ValueError('x2 must be a regular (uniform-step) grid')
    if weighting not in ('integral', 'ivar'):
        raise ValueError("weighting must be 'integral' or 'ivar'")
    if not normalize and weighting != 'integral':
        raise ValueError(
            "normalize=False requires weighting='integral'")
    # use a Gaussian kernel with the given FWHM if none is supplied
    if kernel is None:
        kernel = GaussianKernel(fwhm_pix * dx2)
    half_width = kernel.half_width(threshold)
    # default: all samples belong to the same group
    if group is None:
        group = np.zeros(n_in, dtype=int)
    group = np.array(group)
    # retain only valid samples and sort by (group, x) so that within
    # each group the samples are in ascending x order for cell edges
    valid = (np.isfinite(x) & np.isfinite(y)
             & np.isfinite(yerr) & (yerr > 0))
    idx = np.flatnonzero(valid)
    idx = idx[np.lexsort((x[idx], group[idx]))]
    xs = x[idx]
    ys = y[idx]
    es = yerr[idx]
    gs = group[idx]
    # process each group independently so cell boundaries never cross
    # group borders (each group is an independent irregular sampling)
    bounds = np.flatnonzero(np.diff(gs) != 0) + 1
    all_rows: List[np.ndarray] = []
    all_cols: List[np.ndarray] = []
    all_cell_w: List[np.ndarray] = []
    # ngroups counts how many groups have nonzero weight at each pixel
    ngroups = np.zeros(n_out)
    for i0, i1 in zip(np.r_[0, bounds], np.r_[bounds, xs.size]):
        if i1 == i0:
            continue
        # Voronoi cells within this group only
        left, right = _cell_edges(xs[i0:i1], max_half_cell)
        # (output, sample) index pairs within the kernel window
        rows, cols = _window_pairs(left, right, x2, half_width)
        xc = x2[rows]
        # kernel mass that falls inside each cell
        cell_w = (kernel.cdf(right[cols] - xc)
                  - kernel.cdf(left[cols] - xc))
        # a group contributes to output pixel j when its total weight > 0
        ngroups += (
            np.bincount(rows, weights=cell_w, minlength=n_out) > 0)
        all_rows.append(rows)
        # offset cols back to the full sorted-sample index space
        all_cols.append(cols + i0)
        all_cell_w.append(cell_w)
    # concatenate contributions from every group
    rows = (np.concatenate(all_rows) if all_rows
            else np.zeros(0, dtype=int))
    cols = (np.concatenate(all_cols) if all_cols
            else np.zeros(0, dtype=int))
    cell_w = (np.concatenate(all_cell_w) if all_cell_w
              else np.zeros(0))
    # compute per-pair weights for the chosen weighting mode
    if weighting == 'integral':
        # weight = kernel mass within each Voronoi cell
        w = cell_w
    else:
        # ivar: weight = kernel profile / variance
        prof = kernel.profile(xs[cols] - x2[rows])
        # cell-overlap selection may include centres just past the cutoff
        keep = prof >= threshold
        rows = rows[keep]
        cols = cols[keep]
        prof = prof[keep]
        cell_w = cell_w[keep]
        w = prof / es[cols] ** 2
    # weighted sums needed for the output value, error and coverage
    sum_w = np.bincount(rows, weights=w, minlength=n_out)
    sum_wy = np.bincount(rows, weights=w * ys[cols], minlength=n_out)
    sum_w2e2 = np.bincount(rows, weights=(w * es[cols]) ** 2,
                           minlength=n_out)
    sum_cell = np.bincount(rows, weights=cell_w, minlength=n_out)
    # coverage: average fraction of kernel mass backed by data per group
    coverage = np.zeros(n_out)
    np.divide(sum_cell, ngroups, out=coverage, where=ngroups > 0)
    # normalisation: mean (normalize=True) or sum (normalize=False)
    norm_w = sum_w if normalize else np.ones(n_out)
    good = (sum_w > 0) & (coverage >= min_coverage)
    out: Dict[str, np.ndarray] = dict(
        y=np.full(n_out, np.nan),
        err=np.full(n_out, np.nan))
    out['y'][good] = sum_wy[good] / norm_w[good]
    out['err'][good] = np.sqrt(sum_w2e2[good]) / norm_w[good]
    out['coverage'] = coverage
    # sum_w in the return dict is the cell-weight sum (effective group count)
    out['sum_w'] = sum_cell
    out['npts'] = np.bincount(rows, minlength=n_out)
    if return_matrix:
        # sparse linear operator W such that y2 = W @ y
        keep_m = good[rows]
        vals = w[keep_m] / norm_w[rows[keep_m]]
        out['matrix'] = _sp_sparse.csr_matrix(
            (vals, (rows[keep_m], idx[cols[keep_m]])),
            shape=(n_out, n_in))
    return out
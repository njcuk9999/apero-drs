#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Background estimation science functions

Polynomial fit to the lower envelope of a noisy, one sided signal (e.g. a
detector background sitting under illuminated orders).

Created on 2025-11-25 at 09:40

@author: cook
"""
import warnings
from typing import Dict, Tuple, Union

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.ndimage import map_coordinates as mapc
from scipy.ndimage import zoom
from scipy.signal import convolve2d

from aperocore.base import base
from aperocore import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.calib.background_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
def _ribbon_running_pct(ribbon: np.ndarray, hw: int, win: int,
                        percent: float, ny: int) -> np.ndarray:
    """
    Running lower-percentile filter along a 1D ribbon.

    Matches the exact slice bounds used by the original per-row loop in
    ``create_background_map``: ``ribbon[max(0, y - hw) : min(ny - 1,
    y + hw)]``. Interior rows (window of length ``win = 2 * hw``) are
    computed in a single vectorised ``np.nanpercentile`` call via
    ``sliding_window_view``. The (small) edge rows fall back to per-row
    calls to preserve the truncated-window behaviour of the original.

    :param ribbon: numpy (1D) array, the collapsed cross-dispersion
                   ribbon
    :param hw: int, half window size (``width // 2``)
    :param win: int, full window length (``2 * hw``)
    :param percent: float, percentile to evaluate (%)
    :param ny: int, ribbon length

    :return: numpy (1D) array of length ``ny`` with the running
             percentile at each row
    """
    # output vector: one percentile per row of the ribbon
    out = np.empty(ny, dtype=float)
    # number of interior rows that see a full-length window
    nmid = ny - win
    with warnings.catch_warnings():
        # nanpercentile on an all-NaN slice legitimately returns NaN
        warnings.simplefilter('ignore', category=RuntimeWarning)
        # interior: bulk of the work goes here, in one vector call
        if nmid > 0:
            # windows[k] = ribbon[k : k + win]; k=0 corresponds to y=hw
            wins = sliding_window_view(ribbon, win)[:nmid]
            # split fast (all-finite) vs slow (contains NaN) rows: NaN
            # windows still need the exact nanpercentile behaviour, but
            # in practice they are rare and this keeps the hot path in
            # plain np.percentile (which uses O(n) partition rather
            # than O(n log n) sort of nanpercentile)
            nan_wins = np.isnan(wins).any(axis=1)
            clean = ~nan_wins
            mid_out = np.empty(nmid, dtype=float)
            if clean.any():
                mid_out[clean] = np.percentile(wins[clean], percent,
                                               axis=1)
            if nan_wins.any():
                mid_out[nan_wins] = np.nanpercentile(wins[nan_wins],
                                                    percent, axis=1)
            out[hw:hw + nmid] = mid_out
        # left edge: y in [0, hw-1] uses ribbon[0 : y + hw]
        for y_it in range(min(hw, ny)):
            end = min(ny - 1, y_it + hw)
            out[y_it] = np.nanpercentile(ribbon[0:end], percent)
        # right edge: y in [ny-hw, ny-1] uses ribbon[y - hw : ny - 1]
        for y_it in range(max(hw, ny - hw), ny):
            start = max(0, y_it - hw)
            end = min(ny - 1, y_it + hw)
            out[y_it] = np.nanpercentile(ribbon[start:end], percent)
    # bottleneck's nanpercentile fallback returns a scalar; return array
    return out


def create_background_map(image: np.ndarray, badpixmask: np.ndarray,
                          width: int, percent: float, csize: int,
                          nbad: int) -> np.ndarray:
    """
    Create background map mask

    :param image: numpy (2D) array, the image to calculate the background
                  from
    :param badpixmask: numpy (2D) array, a map of bad pixels
    :param width: int, width of the box to produce the background mask
    :param percent: float, the background percentile to compute minimum
                    value (%)
    :param csize: int, size in pixels of to convolve tophat for the
                  background mask
    :param nbad: int, if a pixel has this or more "dark" neighbours, we
                 consider it dark regardless of its initial value

    :return: numpy (2D) array, the background map (same shape as image)
    """
    # set image bad pixels to NaN
    image0 = np.array(image)
    badmask = np.array(badpixmask, dtype=bool)
    image0[badmask] = np.nan
    # image that will contain the background estimate
    backest = np.zeros_like(image0)
    # we slice the image in ribbons of width "width".
    # The slicing is done in the cross-dispersion direction, so we
    # can simply take a median along the "fast" dispersion to find the
    # order profile. We pick width to be small enough for the orders not
    # to show a significant curvature within w pixels

    # width in fast dispersion axis - smaller so there is no blur due to the
    # curvature of orders
    width2 = width // 4
    ny = image0.shape[0]
    # half-window used for the running lower-percentile filter
    hw = width // 2
    # full window length (matches the interior slice ribbon[y-hw : y+hw])
    win = 2 * hw
    # loop around this regions (per region)
    for x_it in range(0, image0.shape[1], width2):
        # ribbon to find the order profile
        ribbon = mp.nanmedian(image0[:, x_it:x_it + width2], axis=1)
        # vectorised running lower percentile along the ribbon; the
        # original loop evaluated ribbon[max(0,y-hw) : min(ny-1,y+hw)]
        # at every row - we preserve those exact slice bounds
        col_backest = _ribbon_running_pct(ribbon, hw, win, percent, ny)
        # assign the column result across the current ribbon columns
        backest[:, x_it:x_it + width2] = col_backest[:, None]
    # the mask is the area that is below then Nth percentile threshold
    with warnings.catch_warnings(record=True) as _:
        backmask = np.array(image0 < backest, dtype=float)
    # we take advantage of the order geometry and for that the "dark"
    # region of the array be continuous in the "fast" dispersion axis
    nribbon = convolve2d(backmask, np.ones([1, csize]), mode='same')
    # we remove from the binary mask all isolated (within 1x7 ribbon)
    # dark pixels
    backmask[nribbon == 1] = 0
    # If a pixel has 3 or more "dark" neighbours, we consider it dark
    # regardless of its initial value
    backmask[nribbon >= nbad] = 1
    # return the background mask
    return backmask


def correct_local_background(image: np.ndarray, wx_ker: int, wy_ker: int,
                             sig_ker: int) -> np.ndarray:
    """
    determine the scattering from an input image. To speed up the code,
    do the following steps rather than a simple convolution with the
    scattering kernel.

    :param image: np.array, image to correct local background
    :param wx_ker: int, background kernel width in x [pixels]
    :param wy_ker: int, background kernel width in y [pixels]
    :param sig_ker: int, convolution kernel sigma range

    Logical (slow) steps -->

    -- create a kernel of a 2D gaussian with a width in X and Y defined
    from the BKGR_KER_WX and BKGR_KER_WY keywords
    this kernel is typically much larger on one axis than on the other
    (typically 1 vs 9 pixels 1/e width)
    -- convolve the image by the kernel

    Faster (but less intuitive) steps that we do -->

    - Downsize (simple binning) the image to dimensions for which the
    convolution kernel is (barely) Nyquist. These dimensions are selected
    to be the smallest integer dimensions where there are integer pixel
    bins while remaining above Nyquist. If we have a 9 pixel 1/e width,
    then we bin by a factor of 8 an 4088 image to a 511 pixel size, and
    the 1/e width in that new reference frame becomes 9/8 ~ 1.1
    - Convolve the binned-down image with the kernel in the down-sized
    reference frame. Here, a 1x9 1/e 2-D gaussian becomes a 1x1.1 1/e
    gaussian. The kernel is smaller and the input image is also similarly
    smaller, so there is a N^2 gain.
    - Upscale the convolved image to the input dimensions

    :returns: np.ndarray, the local background (scattered_light), same size
              as input image
    """
    # Remove NaNs from image
    image1 = mp.nanpad(image)
    # size if input image
    sz = image1.shape
    # size of the smaller image. It is an integer divider of the input image
    # 4088 on an axis and wN_ker = 9 would lead to an 8x scale-down (8*511)
    sz_small = [sz[0] // mp.largest_divisor_below(sz[0], wy_ker),
                sz[1] // mp.largest_divisor_below(sz[1], wx_ker)]

    # downsizing image prior to convolution
    # bins an image from its shape down to a smaller shape, say 4096x4096 to
    # 512x512. Before/after axis ratio must be integers in all dims.
    #
    shape = (sz_small[0], image1.shape[0] // sz_small[0],
             sz_small[1], image1.shape[1] // sz_small[1])
    image2 = np.array(image1).reshape(shape).mean(-1).mean(1)

    # downsizing ratio to properly scale convolution kernel
    downsize_ratio = np.array(sz) / np.array(sz_small)

    # convolution kernel in the downsized domain
    ker_sigx = int((wx_ker * sig_ker * 2) / downsize_ratio[1] + 1)
    ker_sigy = int((wy_ker * sig_ker * 2) / downsize_ratio[0] + 1)
    kery, kerx = np.indices([ker_sigy, ker_sigx], dtype=float)
    # this normalises kernal x and y between +1 and -1
    kery = kery - np.mean(kery)
    kerx = kerx - np.mean(kerx)
    # calculate 2D gaussian kernel
    ker = np.exp(-0.5 * ((kerx / wx_ker * downsize_ratio[1]) ** 2
                         + (kery / wy_ker * downsize_ratio[0]) ** 2))

    # we normalize the integral of the kernel to 1 so that the AMP factor
    #    corresponds to the fraction of scattered light and therefore has a
    #    physical meaning.
    ker = ker / np.sum(ker)

    # upscale image back to original dimensions
    image3 = convolve2d(image2, ker, mode='same')
    image4 = np.array(image1.shape) / np.array(image2.shape)
    scattered_light = zoom(image3, image4, output=None, order=1,
                           mode='constant', cval=0.0)
    # returned the scattered light
    return scattered_light


def iterative_box_background(image2: np.ndarray, width: int,
                             niter: int = 3
                             ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimate a smooth background using an iterative running-median box
    filter, upscaled from a binned-down grid.

    :param image2: numpy (2D) array, the image with non-background pixels
                   already set to NaN
    :param width: int, width of the box used for the running median filter
    :param niter: int, number of iterations to refine the background

    :return: tuple, 1. numpy (2D) array, the full-size background image
             2. numpy (2D) array, the binned-down background image
    """
    # create the box centers
    #     we construct a binned-down version of the full image with the
    #     estimate of the background for each x+y "center". This image
    #     will be up-scaled to the size of the full science image and
    #     subtracted
    xc = np.arange(0, image2.shape[0])
    yc = np.arange(width // 4, image2.shape[1], width // 4)

    imageshape = image2.shape

    background_image = np.zeros((len(xc), len(yc)))
    background_image_offset = np.zeros((len(xc), len(yc)))
    background_image_full = np.zeros_like(image2)
    gridshape = background_image.shape

    # get fractional positions of the full image
    indices = np.indices(imageshape)
    fypix = indices[0] / imageshape[0]
    fxpix = indices[1] / imageshape[1]
    # scalge fraction positions to size of background image
    sypix = (gridshape[0] - 1) * fypix
    sxpix = (gridshape[1] - 1) * fxpix
    # coords for mapping
    coords = np.array([sypix, sxpix])

    # precompute box index bounds once - they do not change across iters
    hw = width // 2
    nx = image2.shape[1]
    box_i0 = np.maximum(yc - hw, 0)
    box_i1 = np.minimum(yc + hw, nx)

    for _ in range(niter):
        image2b = np.array(image2 - background_image_full)
        #     # loop around all boxes with centers xc and yc
        #     # and find pixels within a given widths
        #     # around these centers in the full image
        for ii in range(len(yc)):
            i0 = int(box_i0[ii])
            i1 = int(box_i1[ii])
            with warnings.catch_warnings(record=True) as _:
                # mp.nanmedian dispatches to bottleneck (bn.nanmedian)
                # when available, which is markedly faster than the
                # bare numpy call used previously
                medcol = mp.nanmedian(image2b[:, i0:i1], axis=1)
            background_image_offset[:, ii] = mp.lowpassfilter(medcol, width)

        background_image_full += mapc(background_image_offset, coords,
                                      order=2, cval=np.nan, output=float,
                                      mode='constant')
        background_image += background_image_offset
    # return the full size background image and the binned-down background
    return background_image_full, background_image
# =============================================================================
def fit_lower_envelope_2d(image: np.ndarray, err: np.ndarray,
                          xorder: int = 3, yorder: int = 3,
                          f_pos: Union[float, str] = 'auto',
                          f_bad: float = 1e-3,
                          anneal: Tuple[float, ...] = (8.0, 4.0, 2.0, 1.4,
                                                       1.0),
                          niter: int = 60, start_q: float = 0.20,
                          nbin: Tuple[int, int] = (16, 16),
                          tol: float = 1e-5, bin_size: int = 4,
                          verbose: bool = False) -> Dict[str, np.ndarray]:
    """
    Fit one two dimensional polynomial through the lower envelope of a whole
    image

    The weight of each pixel is inverse variance, times a soft outlier term
    that redescends on both sides, times an asymmetry that makes a point
    above the curve cost f_pos of what a point below it costs:

        w = (1 / sigma^2) * G / (G + f_bad) * (1 if n < 0 else f_pos)

    with G = exp(-n^2 / 2) and n = (y - b) / sigma. The asymmetry is the
    freedom to have any positive outlier: no amount of light above the curve
    pulls it up. f_bad small is the tolerance for rare negative outliers: a
    point below keeps its full weight until it is extreme.

    The surface

        b(x, y) = sum_ij c_ij * y^i * x^j

    is solved once for every pixel of the frame rather than column by
    column, so the background is forced to be smooth along the dispersion
    instead of being independent columns that happen to look alike.

    The design matrix is never built. At degree three in each direction it
    would be many millions of rows by 16 columns for a normal matrix that is
    only 16 by 16. The basis is separable, y^i x^j, so every entry of that
    normal matrix is a moment of the weights,

        M[(i,j),(i',j')] = S[i+i', j+j']    S[p,q] = sum_rc w_rc y_r^p x_c^q

    and the whole set of moments is two matrix products. Nothing bigger than
    the image is allocated, and a pass costs about what one pass over the
    pixels costs.

    :param image: numpy array (2D), the frame, already cut to the roi in y
    :param err: numpy array (2D), its 1 sigma errors, same shape
    :param xorder: int, degree along the columns
    :param yorder: int, degree along the rows
    :param f_pos: float or 'auto', what a point above the surface costs
                  relative to one below it. 'auto' solves for the value that
                  puts half the believable pixels on each side of the
                  surface
    :param f_bad: float, prior on a pixel being bad rather than noise
    :param anneal: tuple, sigma inflation of the first passes, so nothing is
                  rejected while the surface first walks down
    :param niter: int, maximum passes after the annealing
    :param start_q: float, the quantile taken in each tile for the first
                    guess
    :param nbin: tuple, tiles (in y, in x) used by that first guess
    :param tol: float, stop when the surface moves by less than this many
                sigma
    :param bin_size: int, median-binning factor used for fitting. The final
                     surface is evaluated on the full image
    :param verbose: bool, report the convergence and the tuning

    :return: dict with the surface ('fit'), the coefficients ('coef'), the
             deviations in sigma ('nsig'), the number of passes ('npass'),
             the f_pos used ('f_pos'), the balance ('balance') and the mask
             of usable pixels ('ok')
    """
    func_name = f'{__NAME__}.fit_lower_envelope_2d()'
    zfull = np.array(image, dtype=float)
    efull = np.array(err, dtype=float)
    if zfull.shape != efull.shape:
        emsg = 'image and err must have the same shape \n\t Function = {0}'
        raise ValueError(emsg.format(func_name))
    if bin_size < 1:
        emsg = 'bin_size must be at least 1 \n\t Function = {0}'
        raise ValueError(emsg.format(func_name))
    full_ny, full_nx = zfull.shape
    full_ok = np.isfinite(zfull) & np.isfinite(efull) & (efull > 0)
    full_u = np.linspace(-1.0, 1.0, full_ny)
    full_v = np.linspace(-1.0, 1.0, full_nx)
    if bin_size == 1:
        z = zfull
        e = efull
        u = full_u
        v = full_v
    else:
        pad_y = (-full_ny) % bin_size
        pad_x = (-full_nx) % bin_size
        pad = ((0, pad_y), (0, pad_x))
        zvalid = np.where(full_ok, zfull, np.nan)
        evalid = np.where(full_ok, efull, np.nan)
        zpad = np.pad(zvalid, pad, constant_values=np.nan)
        epad = np.pad(evalid, pad, constant_values=np.nan)
        shape = (zpad.shape[0] // bin_size, bin_size,
                 zpad.shape[1] // bin_size, bin_size)
        with warnings.catch_warnings(record=True) as _:
            z = np.nanmedian(zpad.reshape(shape), axis=(1, 3))
            e = np.nanmedian(epad.reshape(shape), axis=(1, 3))
        count = np.isfinite(zpad).reshape(shape).sum(axis=(1, 3))
        e = e / np.sqrt(count)
        ystarts = np.arange(0, full_ny, bin_size)
        xstarts = np.arange(0, full_nx, bin_size)
        ywidths = np.minimum(bin_size, full_ny - ystarts)
        xwidths = np.minimum(bin_size, full_nx - xstarts)
        u = np.add.reduceat(full_u, ystarts) / ywidths
        v = np.add.reduceat(full_v, xstarts) / xwidths
    ny, nx = z.shape
    # only finite pixels with a positive error are usable
    ok = np.isfinite(z) & np.isfinite(e) & (e > 0)
    if ok.sum() < (xorder + 1) * (yorder + 1) + 10:
        emsg = 'not enough usable pixels \n\t Function = {0}'
        raise ValueError(emsg.format(func_name))
    # everything a NaN touches gets zero weight rather than being removed,
    #   which keeps the arrays rectangular and the moments as matrix
    #   products
    zc = np.where(ok, z, 0.0)
    # a safe copy of the errors: a NaN error would poison the deviations of
    #   every pixel through the exponential, and a zero weight afterwards
    #   does not undo it because NaN times zero is still NaN
    esafe = np.where(ok, e, 1.0)
    ivar = np.where(ok, 1.0 / esafe ** 2, 0.0)
    # powers, up to twice the degree for the moments and once for the basis
    upow = np.stack([u ** p for p in range(2 * yorder + 1)])
    vpow = np.stack([v ** q for q in range(2 * xorder + 1)])
    ubas = upow[:yorder + 1].T
    vbas = vpow[:xorder + 1].T
    ii, jj = np.meshgrid(np.arange(yorder + 1), np.arange(xorder + 1),
                         indexing='ij')
    ii, jj = ii.ravel(), jj.ravel()
    # cache the full-detector basis: these depend only on the grid
    # sizes and polynomial order, and were previously rebuilt every
    # call to _full_surface
    full_ubas = np.stack([full_u ** p
                          for p in range(yorder + 1)]).T
    full_vbas = np.stack([full_v ** q
                          for q in range(xorder + 1)]).T

    def _solve(w):
        """the normal equations, as moments of the weights"""
        smom = (upow @ w) @ vpow.T
        rmom = (upow[:yorder + 1] @ (w * zc)) @ vpow[:xorder + 1].T
        mat = smom[ii[:, None] + ii[None, :], jj[:, None] + jj[None, :]]
        coef, *_ = np.linalg.lstsq(mat, rmom.ravel(), rcond=None)
        return coef.reshape(yorder + 1, xorder + 1)

    def _surface(coef):
        """evaluate the polynomial surface from its coefficients"""
        return (ubas @ coef) @ vbas.T

    def _full_surface(coef):
        """evaluate the polynomial surface on the full detector grid"""
        # basis arrays are precomputed once outside the fit loop
        return (full_ubas @ coef) @ full_vbas.T

    # -------------------------------------------------------------------
    # the start: a low quantile per tile, already near the bottom
    # -------------------------------------------------------------------
    ty, tx = int(nbin[0]), int(nbin[1])
    ye = np.linspace(0, ny, ty + 1).astype(int)
    xe = np.linspace(0, nx, tx + 1).astype(int)
    bu, bv, bz = [], [], []
    for a in range(ty):
        for b in range(tx):
            tile = z[ye[a]:ye[a + 1], xe[b]:xe[b + 1]]
            tile = tile[np.isfinite(tile)]
            if tile.size >= 10:
                bu.append(np.mean(u[ye[a]:ye[a + 1]]))
                bv.append(np.mean(v[xe[b]:xe[b + 1]]))
                bz.append(np.quantile(tile, start_q))
    bu, bv, bz = np.array(bu), np.array(bv), np.array(bz)
    if bz.size >= (xorder + 1) * (yorder + 1):
        des = (bu[:, None] ** ii[None, :]) * (bv[:, None] ** jj[None, :])
        c0, *_ = np.linalg.lstsq(des, bz, rcond=None)
        start = c0.reshape(yorder + 1, xorder + 1)
    else:
        start = _solve(ivar)

    # -------------------------------------------------------------------
    # anneal, then iterate to the fixed point
    # -------------------------------------------------------------------
    def _run(fpos):
        """anneal, then iterate the weighted fit to the fixed point"""
        coef = np.array(start)
        surf = _surface(coef)
        npass = 0
        for it, scale in enumerate(list(anneal) + [1.0] * niter):
            nsig = (zc - surf) / (esafe * scale)
            np.clip(nsig, -40.0, 40.0, out=nsig)
            gauss = np.exp(-0.5 * nsig * nsig)
            # equation from the docstring above, pixel by pixel
            w = gauss / (gauss + f_bad)
            w *= np.where(nsig < 0.0, 1.0, fpos)
            w *= ivar
            if not np.any(w > 0):
                break
            coef = _solve(w)
            new = _surface(coef)
            move = np.max(np.abs((new - surf)[ok]) / e[ok])
            surf = new
            npass = it + 1
            if it >= len(anneal) and move < tol:
                break
        return coef, surf, npass

    def _balance(surf):
        """fraction of the believable pixels sitting below the surface"""
        n = np.where(ok, (zc - surf) / esafe, np.nan)
        near = ok & (np.abs(n) < 3.0)
        if near.sum() < 100:
            return 0.0
        return float(np.mean(n[near] < 0))

    if isinstance(f_pos, str) and f_pos.lower().startswith('auto'):
        lo, hi = np.log10(1e-4), np.log10(0.95)
        used, best = None, None
        # early-exit tolerance on the balance being centred on 0.5 -
        # in practice the bisection converges in 3-4 iterations for
        # typical images, so bail out once we are within 1% of centre
        bal_tol = 0.01
        min_iter = 4
        for it in range(12):
            mid = 0.5 * (lo + hi)
            trial = _run(10.0 ** mid)
            bal = _balance(trial[1])
            used, best = 10.0 ** mid, trial
            if verbose:
                print('   f_pos {0:8.5f} -> {1:.3f} below'.format(used, bal))
            # stop once the balance is close enough to 0.5, keeping
            # a small minimum number of iterations for stability
            if it + 1 >= min_iter and abs(bal - 0.5) < bal_tol:
                break
            # more weight above the surface lifts it, so the balance rises
            if bal < 0.5:
                lo = mid
            else:
                hi = mid
        coef, surf, npass = best
    else:
        used = float(f_pos)
        coef, surf, npass = _run(used)
    bal = _balance(surf)
    if verbose:
        pmsg = ('   converged in {0} passes, f_pos = {1:.5g}, {2:.1f}% of '
               'the believable pixels below')
        print(pmsg.format(npass, used, 100 * bal))
    # evaluate the final fit and deviations on the full detector grid
    full_surf = _full_surface(coef)
    full_esafe = np.where(full_ok, efull, 1.0)
    nsig = np.where(full_ok, (zfull - full_surf) / full_esafe, np.nan)
    return dict(fit=full_surf, coef=coef, nsig=nsig, npass=npass,
                f_pos=used, balance=bal, ok=full_ok)


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

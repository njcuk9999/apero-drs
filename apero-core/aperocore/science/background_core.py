#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Background estimation science functions

Polynomial fit to the lower envelope of a noisy, one sided signal (e.g. a
detector background sitting under illuminated orders).

Created on 2025-11-25 at 09:40

@author: cook
"""
from typing import Dict, Tuple, Union

import numpy as np

from aperocore.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.background_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def fit_lower_envelope_2d(image: np.ndarray, err: np.ndarray,
                          xorder: int = 3, yorder: int = 3,
                          f_pos: Union[float, str] = 'auto',
                          f_bad: float = 1e-3,
                          anneal: Tuple[float, ...] = (8.0, 4.0, 2.0, 1.4,
                                                       1.0),
                          niter: int = 60, start_q: float = 0.20,
                          nbin: Tuple[int, int] = (16, 16),
                          tol: float = 1e-5,
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
    :param verbose: bool, report the convergence and the tuning

    :return: dict with the surface ('fit'), the coefficients ('coef'), the
             deviations in sigma ('nsig'), the number of passes ('npass'),
             the f_pos used ('f_pos'), the balance ('balance') and the mask
             of usable pixels ('ok')
    """
    func_name = f'{__NAME__}.fit_lower_envelope_2d()'
    z = np.asarray(image, dtype=float)
    e = np.asarray(err, dtype=float)
    if z.shape != e.shape:
        emsg = 'image and err must have the same shape \n\t Function = {0}'
        raise ValueError(emsg.format(func_name))
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
    # scaled coordinates, both in [-1, 1]
    u = np.linspace(-1.0, 1.0, ny)
    v = np.linspace(-1.0, 1.0, nx)
    # powers, up to twice the degree for the moments and once for the basis
    upow = np.stack([u ** p for p in range(2 * yorder + 1)])
    vpow = np.stack([v ** q for q in range(2 * xorder + 1)])
    ubas = upow[:yorder + 1].T
    vbas = vpow[:xorder + 1].T
    ii, jj = np.meshgrid(np.arange(yorder + 1), np.arange(xorder + 1),
                         indexing='ij')
    ii, jj = ii.ravel(), jj.ravel()

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
        for _ in range(12):
            mid = 0.5 * (lo + hi)
            trial = _run(10.0 ** mid)
            bal = _balance(trial[1])
            used, best = 10.0 ** mid, trial
            if verbose:
                print('   f_pos {0:8.5f} -> {1:.3f} below'.format(used, bal))
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
    # deviations of every pixel from the fitted surface, in sigma
    nsig = np.where(ok, (zc - surf) / esafe, np.nan)
    return dict(fit=surf, coef=coef, nsig=nsig, npass=npass, f_pos=used,
               balance=bal, ok=ok)


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

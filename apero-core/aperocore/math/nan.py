#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO Not-a-Number (NaN) functionality

Mostly linking to the apero fast math module

Created on 2019-05-15 at 12:24

@author: cook
"""
import warnings
from typing import Any, List, Union

import numpy as np
from scipy.ndimage import convolve, distance_transform_edt

from aperocore.base import base
from aperocore.math import fast

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.math.nan.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define NaN functions
# =============================================================================
def nanpad(oimage: np.ndarray) -> np.ndarray:
    """
    Pads NaN values with the median (non NaN values from the 9 pixels around
    it) does this iteratively until no NaNs are left - if all 9 pixels are
    NaN - median is NaN

    :param oimage: numpy array (2D), the input image with NaNs
    :type oimage: np.ndarray

    :return: Nan-removed copy of original image
    :rtype: np.ndarray
    """
    # set function name
    # _ = display_func('nanpad', __NAME__)
    # deep copy image
    image = np.array(oimage)
    # replace the NaNs on the edge with zeros
    image[:, 0] = killnan(image[:, 0], 0)
    image[0, :] = killnan(image[0, :], 0)
    image[:, -1] = killnan(image[:, -1], 0)
    image[-1, :] = killnan(image[-1, :], 0)
    # find x/y positions of NaNs
    gy, gx = np.where(~np.isfinite(image))
    # for each NaN, find the 8 neighbouring pixels and pad them
    # into an array that is 9xN.
    while len(gy) != 0:
        # array that contains neighbours to a given pixel along
        # the axis 1
        tmp = np.zeros([len(gy), 9])
        # pad the neighbour array
        for it in range(9):
            ypix = gy + (it // 3) - 1
            xpix = gx + (it % 3) - 1
            tmp[:, it] = image[ypix, xpix]
        # median the neghbours and pad back into the input image
        with warnings.catch_warnings(record=True) as _:
            image[gy, gx] = fast.nanmedian(tmp, axis=1)
        # find NaNs again and pad again if needed
        gy, gx = np.where(~np.isfinite(image))
    # return padded image
    return image


def fill_nans(image: Union[np.ndarray, List[np.ndarray]],
             nsmooth: int = 1
             ) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Grow the finite pixels of a 2D image into its NaNs

    Every filled pixel has no data behind it, so the only requirements are
    that it be continuous with its surroundings and cheap to compute. This
    is done with a single distance transform (giving every NaN the value of
    the nearest finite pixel) followed by "nsmooth" passes of a 3x3 mean
    over the filled pixels only, which removes the seams left by the
    distance transform.

    :param image: numpy array (2D), or a list of 2D arrays. If a list is
                  passed, arrays sharing the same NaN pattern share the
                  (expensive) distance transform
    :param nsmooth: int, number of 3x3 smoothing passes over the filled
                    pixels

    :return: numpy array (2D), the filled image, or a list of them (matching
             the input type)
    """
    # deal with single image vs list of images
    single = not isinstance(image, (list, tuple))
    images = [image] if single else list(image)
    outs = [np.array(one, dtype=float) for one in images]
    kernel = np.ones((3, 3)) / 9.0
    # hole patterns already solved, as (mask, indices) pairs, so images that
    #   share a NaN pattern share the (expensive) distance transform
    solved = []
    for out in outs:
        bad = ~np.isfinite(out)
        # nothing to do, or nothing to do it with
        if not bad.any() or bad.all():
            continue
        idx = None
        for prev_bad, prev_idx in solved:
            if np.array_equal(bad, prev_bad):
                idx = prev_idx
                break
        if idx is None:
            # the nearest finite pixel, for every hole at once
            idx = distance_transform_edt(bad, return_distances=False,
                                         return_indices=True)
            solved.append((bad, idx))
        out[bad] = out[tuple(idx)][bad]
        # take the seams out, touching only what was missing
        for _ in range(nsmooth):
            out[bad] = convolve(out, kernel, mode='nearest')[bad]
    # return in the same form as the input
    return outs[0] if single else outs


def nanchebyfit(xvector: np.ndarray, yvector: np.ndarray, deg: int,
                domain: List[float],
                weight: Union[np.ndarray, None] = None) -> Any:
    """
    A Chebyshev polyfit that takes into account NaNs in the array (masks them)

    :param xvector: np.array, the x data
    :param yvector: np.array, the y data
    :param deg: int, the degree of the polynomial fit
    :param domain: list of floats, 1. minimum point in domain
                                   2. maximum point in domain
    :param weight: None or np.array - the weight vector

    :return: same as np.polyfit
    """
    # set function name
    # _ = display_func('nanpolyfit', __NAME__)
    # check if there is a weight input in kwargs
    if weight is not None:
        # find the NaNs in x, y, w
        nanmask = np.isfinite(yvector) & np.isfinite(xvector)
        nanmask &= np.isfinite(weight)
        # mask the weight in kwargs
        weight = weight[nanmask]
    else:
        # find the NaNs in x and y
        nanmask = np.isfinite(yvector) & np.isfinite(xvector)

    domain_cheby = 2 * (xvector - domain[0]) / (domain[1] - domain[0]) - 1
    fit = np.polynomial.chebyshev.chebfit(domain_cheby[nanmask],
                                          yvector[nanmask], deg, w=weight)
    # return polyfit without the nans
    return fit


def nanpolyfit(xvector: np.ndarray, yvector: np.ndarray, deg: int,
               weight: Union[np.ndarray, None] = None, **kwargs) -> Any:
    """
    A polyfit that takes into account NaNs in the array (masks them)

    :param xvector: np.array, the x data
    :param yvector: np.array, the y data
    :param weight: None or np.array - the weight vector
    :param deg: int, the degree of the polynomial fit
    :param kwargs: passed to np.polyfit

    :return: same as np.polyfit
    """
    # set function name
    # _ = display_func('nanpolyfit', __NAME__)
    # check if there is a weight input in kwargs
    if weight is not None:
        # find the NaNs in x, y, w
        nanmask = np.isfinite(yvector) & np.isfinite(xvector)
        nanmask &= np.isfinite(weight)
        # mask the weight in kwargs
        weight = weight[nanmask]
    else:
        # find the NaNs in x and y
        nanmask = np.isfinite(yvector) & np.isfinite(xvector)
    # return polyfit without the nans
    return np.polyfit(xvector[nanmask], yvector[nanmask], deg, w=weight,
                      **kwargs)


def killnan(invector: np.ndarray, value: float = 0.0) -> np.ndarray:
    """
    Replace all NaNs in a vector with a value

    :param invector: np.array - the input vector to remove NaNs from
    :param value: float, the value to fill the vectory with

    :return: the invector where NaNs are filled with value
    """
    # set function name
    # _ = display_func('killnan', __NAME__)
    # copy vector
    vector = np.array(invector)
    # find all finite values
    mask = np.isfinite(vector)
    # replace all non-finite numbers with value
    vector[~mask] = value
    # return updated vector
    return vector


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

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

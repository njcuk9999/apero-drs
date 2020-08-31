#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 12:24

@author: cook
"""
import numpy as np
from typing import Any, Union
import warnings

from apero.base import base
from apero.base import drs_misc
from apero.core.math import fast

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.math.nan.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get display func
display_func = drs_misc.display_func


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
    _ = display_func(None, 'nanpad', __NAME__)
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


def nanpolyfit(x: np.ndarray, y: np.ndarray, deg: int,
               w: Union[np.ndarray, None] = None, **kwargs) -> Any:
    """
    A polyfit that takes into account NaNs in the array (masks them)

    :param x: np.array, the x data
    :param y: np.array, the y data
    :param w: None or np.array - the weight vector
    :param deg: int, the degree of the polynomial fit
    :param kwargs: passed to np.polyfit

    :return: same as np.polyfit
    """
    # set function name
    _ = display_func(None, 'nanpolyfit', __NAME__)
    # check if there is a weight input in kwargs
    if w is not None:
        # find the NaNs in x, y, w
        nanmask = np.isfinite(y) & np.isfinite(x) & np.isfinite(w)
        # mask the weight in kwargs
        w = w[nanmask]
    else:
        # find the NaNs in x and y
        nanmask = np.isfinite(y) & np.isfinite(x)
    # return polyfit without the nans
    return np.polyfit(x[nanmask], y[nanmask], deg, w=w, **kwargs)


def killnan(invector: np.ndarray, value: float = 0.0) -> np.ndarray:
    """
    Replace all NaNs in a vector with a value

    :param invector: np.array - the input vector to remove NaNs from
    :param value: float, the value to fill the vectory with

    :return: the invector where NaNs are filled with value
    """
    # set function name
    _ = display_func(None, 'killnan', __NAME__)
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

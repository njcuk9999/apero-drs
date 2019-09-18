#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 12:24

@author: cook
"""
import numpy as np
import warnings

from terrapipe.core import constants
from . import fast

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.math.nan.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
PConstants = constants.pload(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']

# =============================================================================
# Define NaN functions
# =============================================================================
def nanpad(oimage):
    """
    Pads NaN values with the median (non NaN values from the 9 pixels around
    it) does this iteratively until no NaNs are left - if all 9 pixels are
    NaN - median is NaN

    :param oimage: numpy array (2D), the input image with NaNs
    :type oimage: np.ndarray

    :return: Nan-removed copy of original image
    :rtype: np.ndarray
    """
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


def nanpolyfit(x, y, deg, **kwargs):
    # check if there is a weight input in kwargs
    if 'w' in kwargs:
        if kwargs['w'] is not None:
            # find the NaNs in x, y, w
            nanmask = np.isfinite(y) & np.isfinite(x) & np.isfinite(kwargs['w'])
            # mask the weight in kwargs
            kwargs['w'] = kwargs['w'][nanmask]
        else:
            # find the NaNs in x and y
            nanmask = np.isfinite(y) & np.isfinite(x)
    else:
        # find the NaNs in x and y
        nanmask = np.isfinite(y) & np.isfinite(x)
    # return polyfit without the nans
    return np.polyfit(x[nanmask], y[nanmask], deg, **kwargs)


def killnan(vect, val=0):
    mask = ~np.isfinite(vect)
    vect[mask] = val
    return vect

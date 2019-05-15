#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 13:48

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings

from terrapipe import config
from terrapipe import constants
from terrapipe import locale
from terrapipe.config import drs_log
from terrapipe.config import drs_file


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.localisation.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = config.pcheck


# =============================================================================
# Define functions
# =============================================================================
def calculate_order_profile(params, image, **kwargs):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param image: numpy array (2D), the image
    :param kwargs: keyword arguments

    :keyword size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge

    :return newimage: numpy array (2D), the smoothed image
    """
    func_name = __NAME__ + '.calculate_order_profile()'
    # get constants from params
    size = pcheck(params, 'LOC_ORDERP_BOX_SIZE', 'size', kwargs, func_name)
    # -------------------------------------------------------------------------
    # log that we are creating order profile
    WLOG(params, '', TextEntry('40-013-00001'))
    # -------------------------------------------------------------------------
    # copy the original image
    newimage = np.zeros_like(image)
    # loop around each pixel column
    for it in range(0, image.shape[1], 1):
        # ------------------------------------------------------------------
        # deal with leading edge --> i.e. box expands until it is full size
        if it < size:
            # get the subimage defined by the box for all rows
            part = image[:, 0:it + size + 1]
        # deal with main part (where box is of size="size"
        elif size <= it <= image.shape[1]-size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size: it + size + 1]
        # deal with the trailing edge --> i.e. box shrinks from full size
        elif it > image.shape[1]-size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size:]
        # else we have zeros (shouldn't happen)
        else:
            part = np.zeros_like(image)
        # ------------------------------------------------------------------
        # apply the weighted mean for this column
        with warnings.catch_warnings(record=True) as _:
            newimage[:, it] = np.nanmedian(part, axis=1)
    # return the new smoothed image
    return newimage


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

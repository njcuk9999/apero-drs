#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-10 at 14:33

@author: cook



Version 0.0.0
"""

from SpirouDRS import spirouConfig
from . import spirouBACK


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouBACK.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__all__ = ['BoxSmoothedMinMax',
           'MeasureBackgroundFF',
           'MeasureMinMax',
           'MeasureBkgrdGetCentPixs']

# =============================================================================
# Function aliases
# =============================================================================
BoxSmoothedMinMax = spirouBACK.measure_box_min_max
"""
Measure the minimum and maximum pixel value for each row using a box which
contains all pixels for rows:  row-size to row+size and all columns.

Edge pixels (0-->size and (image.shape[0]-size)-->image.shape[0] are
set to the values for row=size and row=(image.shape[0]-size)

:param image: numpy array (2D), the image
:param size: int, the half size of the box to use (half height)
             so box is defined from  row-size to row+size

:return min_image: numpy array (1D length = image.shape[0]), the row values
                   for minimum pixel defined by a box of row-size to
                   row+size for all columns
:retrun max_image: numpy array (1D length = image.shape[0]), the row values
                   for maximum pixel defined by a box of row-size to
                   row+size for all columns
"""

MeasureBackgroundFF = spirouBACK.measure_background_flatfield

MeasureMinMax = spirouBACK.measure_min_max

MeasureBkgrdGetCentPixs = spirouBACK.measure_background_and_get_central_pixels
"""
Takes the image and measure the background

:param pp: dictionary, parameter dictionary
:param loc: dictionary, localisation parameter dictionary
:param image: numpy array (2D), the image

:return ycc: the normalised values the central pixels
"""

# =============================================================================
# End of code
# =============================================================================

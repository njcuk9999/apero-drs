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
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['BoxSmoothedMinMax',
           'MeasureBackgroundFF',
           'MeasureMinMax',
           'MeasureMinMaxSignal',
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
"""
Measures the background of a flat field image - currently does not work
as need an interpolation function (see code)

:param p: parameter dictionary, the parameter dictionary of constants
:param image: numpy array (2D), the image to measure the background of
:return: 
"""


MeasureMinMax = spirouBACK.measure_box_min_max
"""
Measure the minimum and maximum pixel value for each pixel using a box which
surrounds that pixel by:  pixel-size to pixel+size.

Edge pixels (0-->size and (len(y)-size)-->len(y) are
set to the values for pixel=size and pixel=(len(y)-size)

:param y: numpy array (1D), the image
:param size: int, the half size of the box to use (half height)
             so box is defined from  pixel-size to pixel+size

:return min_image: numpy array (1D length = len(y)), the values
                   for minimum pixel defined by a box of pixel-size to
                   pixel+size for all columns
:return max_image: numpy array (1D length = len(y)), the values
                   for maximum pixel defined by a box of pixel-size to
                   pixel+size for all columns
"""

MeasureMinMaxSignal = spirouBACK.measure_min_max
"""
Measure the minimum, maximum peak to peak values in y, the third biggest
pixel in y and the peak-to-peak difference between the minimum and 
maximum values in y

:param pp: dictionary, parameter dictionary of constants
:param y: numpy array (1D), the central column pixel values

:return miny: numpy array (1D length = len(y)), the values
              for minimum pixel defined by a box of pixel-size to
              pixel+size for all columns
:return maxy: numpy array (1D length = len(y)), the values
              for maximum pixel defined by a box of pixel-size to
              pixel+size for all columns
:return max_signal: float, the pixel value of the third biggest value
                    in y
:return diff_maxmin: float, the difference between maxy and miny
"""

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

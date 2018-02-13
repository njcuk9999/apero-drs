#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for SpirouBACK

Created on 2017-11-10 at 14:33

@author: cook

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

MeasureBackgroundFF = spirouBACK.measure_background_flatfield

MeasureMinMax = spirouBACK.measure_box_min_max

MeasureMinMaxSignal = spirouBACK.measure_min_max

MeasureBkgrdGetCentPixs = spirouBACK.measure_background_and_get_central_pixels

# =============================================================================
# End of code
# =============================================================================

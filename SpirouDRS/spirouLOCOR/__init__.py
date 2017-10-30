#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:09

@author: cook



Version 0.0.0
"""

from . import spirouLOCOR


# Produce a (box) smoothed image, smoothed by the mean of a box of
#     size=2*"size" pixels
BoxSmoothedImage = spirouLOCOR.smoothed_boxmean_image

# Measure the minimum and maximum pixel value for each row using a box which
#     contains all pixels for rows:  row-size to row+size and all columns.
BoxSmoothedMinMax = spirouLOCOR.measure_box_min_max

# Finds the central positions based on the central column values
FindPosCentCol = spirouLOCOR.find_position_of_cent_col

# Takes the values across the oder and finds the order center by looking for
#     the start and end of the order (and thus the center) above threshold
LocCentralOrderPos = spirouLOCOR.locate_order_center
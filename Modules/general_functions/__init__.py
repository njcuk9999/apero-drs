#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__init__.py

general functions controller

Created on 2017-10-12 15:51:49

@author: cook

Version 0.0.1
"""
from . import spirouFITS
from . import spirouImage

__all__ = ['BoxSmoothedImage',
           'ConvertToE',
           'CopyOriginalKeys',
           'FlipImage ',
           'GetKey',
           'GetKeys',
           'ReadImage',
           'ResizeImage',
           'WriteImage']
__author__ = 'Neil Cook'
__version__ = '0.0.1'

# =============================================================================
# Define functions
# =============================================================================

# Produce a (box) smoothed image
BoxSmoothedImage = spirouImage.smoothed_boxmean_image

#
ConvertToE = spirouImage.convert_to_e

# Copies keys from hdr dictionary to hdict, if forbid_keys is True some
#     keys will not be copies (defined in python code)
CopyOriginalKeys = spirouFITS.copy_original_keys

# Corrects an image for darks (using calibDB)
CorrectForDark = spirouImage.correct_for_dark

# Flips the image in the x and/or the y direction
FlipImage = spirouImage.flip_image

# Looks for a key(s) in dictionary p, named 'name'
#     if has_default sets value of key to 'default' if not found
#     else logs an error
GetKey = spirouFITS.keylookup
GetKeys = spirouFITS.keyslookup

# Reads the image 'fitsfilename' defined in p and adds files defined in
# 'arg_file_names' if add is True
ReadImage = spirouFITS.readimage

# Resize an image based on a pixel values
ResizeImage = spirouImage.resize

# Write the image to file and adds header file
WriteImage = spirouFITS.writeimage
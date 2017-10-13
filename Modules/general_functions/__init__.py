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
from . import image

__all__ = ['CopyOriginalKeys', 'GetKey', 'GetKeys', 'ReadImage', 'ResizeImage',
           'WriteImage']
__author__ = 'Neil Cook'
__version__ = '0.0.1'

# =============================================================================
# Define functions
# =============================================================================

# Copies keys from hdr dictionary to hdict, if forbid_keys is True some
#     keys will not be copies (defined in python code)
CopyOriginalKeys = spirouFITS.copy_original_keys

# Looks for a key(s) in dictionary p, named 'name'
#     if has_default sets value of key to 'default' if not found
#     else logs an error
GetKey = spirouFITS.keylookup
GetKeys = spirouFITS.keyslookup

# Reads the image 'fitsfilename' defined in p and adds files defined in
# 'arg_file_names' if add is True
ReadImage = spirouFITS.readimage

# Resize an image based on a pixel values
ResizeImage = image.resize

# Write the image to file and adds header file
WriteImage = spirouFITS.writeimage
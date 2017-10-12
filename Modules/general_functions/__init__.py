#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__init__.py

general functions controller

Created on 2017-10-12 15:51:49

@author: cook

Version 0.0.1
"""
from . import readwrite
from . import image

__all__ = ['ReadImage', 'GetKey', 'GetKeys', 'ResizeImage']
__author__ = 'Neil Cook'
__version__ = '0.0.1'

# =============================================================================
# Define functions
# =============================================================================
# Reads the image 'fitsfilename' defined in p and adds files defined in
# 'arg_file_names' if add is True
ReadImage = readwrite.readimage

# Looks for a key(s) in dictionary p, named 'name'
#     if has_default sets value of key to 'default' if not found
#     else logs an error
GetKey = readwrite.keylookup
GetKeys = readwrite.keyslookup

# Resize an image based on a pixel values
ResizeImage = image.resize
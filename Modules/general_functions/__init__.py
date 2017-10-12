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

__all__ = ['ReadImage']
__author__ = 'Neil Cook'


# =============================================================================
# Define functions
# =============================================================================
# Reads the image 'fitsfilename' defined in p and adds files defined in
# 'arg_file_names' if add is True
ReadImage = readwrite.readimage

# Looks for a key in dictionary p, named 'name'
#     if has_default sets value of key to 'default' if not found
#     else logs an error
GetKey = readwrite.keylookup
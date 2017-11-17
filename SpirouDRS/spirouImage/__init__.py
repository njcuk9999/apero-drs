#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:09

@author: cook



Version 0.0.0
"""
from SpirouDRS import spirouConfig
from . import spirouFITS
from . import spirouImage

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouImage.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__all__ = ['AddKey', 'AddKey1DList', 'AddKey2DList',
           'ConvertToE', 'ConvertToADU',
           'CopyOriginalKeys', 'CorrectForDark',
           'FitTilt', 'FlipImage',
           'GetSigdet', 'GetExpTime', 'GetGain',
           'GetKey', 'GetKeys', 'GetTilt', 'GetTypeFromHeader',
           'ReadImage', 'ReadHeader', 'ReadKey', 'Read2Dkey',
           'ReadTiltFile', 'ReadWaveFile', 'ReadOrderProfile',
           'ResizeImage', 'WriteImage']

# =============================================================================
# Function aliases
# =============================================================================
# add a new key to hdict from keywordstorage
AddKey = spirouFITS.add_new_key

AddKey1DList = spirouFITS.add_key_1d_list

# add a new 2d list to key using the keywordstorage[0] as prefix
AddKey2DList = spirouFITS.add_key_2d_list

# Converts image from ADU/s into e-
ConvertToE = spirouImage.convert_to_e
ConvertToADU = spirouImage.convert_to_adu

# Copies keys from hdr dictionary to hdict, if forbid_keys is True some
#     keys will not be copies (defined in python code)
CopyOriginalKeys = spirouFITS.copy_original_keys

# Corrects an image for darks (using calibDB)
CorrectForDark = spirouImage.correct_for_dark

FitTilt = spirouImage.fit_tilt

# Flips the image in the x and/or the y direction
FlipImage = spirouImage.flip_image

GetSigdet = spirouImage.get_sigdet
GetExpTime = spirouImage.get_exptime
GetGain = spirouImage.get_gain

# Looks for a key(s) in dictionary p, named 'name'
#     if has_default sets value of key to 'default' if not found
#     else logs an error
GetKey = spirouFITS.keylookup
GetKeys = spirouFITS.keyslookup


GetTilt = spirouImage.get_tilt

GetTypeFromHeader = spirouFITS.get_type_from_header

# Reads the image 'fitsfilename' defined in p and adds files defined in
# 'arg_file_names' if add is True
ReadImage = spirouFITS.readimage

# Read Header
ReadHeader = spirouFITS.read_header

# Read key
ReadKey = spirouFITS.read_key

# Read 2D key list
Read2Dkey = spirouFITS.read_key_2d_list

# Read the tilt file
ReadTiltFile = spirouFITS.read_tilt_file

ReadWaveFile = spirouFITS.read_wave_file

# Read the order profile file
ReadOrderProfile = spirouFITS.read_order_profile_superposition

# Resize an image based on a pixel values
ResizeImage = spirouImage.resize

# Write the image to file and adds header file
WriteImage = spirouFITS.writeimage

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:09

@author: cook



Version 0.0.0
"""

from . import spirouFITS
from . import spirouImage

# add a new key to hdict from keywordstorage
AddNewKey = spirouFITS.add_new_key

# add a new 2d list to key using the keywordstorage[0] as prefix
AddKey2DList = spirouFITS.add_key_2d_list

# Converts image from ADU/s into e-
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

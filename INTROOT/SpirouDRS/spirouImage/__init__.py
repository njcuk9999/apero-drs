#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou Image processing module

Created on 2017-10-30 at 17:09

@author: cook

"""
from SpirouDRS import spirouConfig
from . import spirouFITS
from . import spirouImage
from . import spirouTable

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouImage.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['AddKey', 'AddKey1DList', 'AddKey2DList',
           'ConvertToE', 'ConvertToADU',
           'CopyOriginalKeys', 'CopyRootKeys', 'CorrectForDark',
           'FitTilt', 'FlipImage',
           'GetAllSimilarFiles', 'GetAcqTime',
           'GetSigdet', 'GetExpTime', 'GetGain',
           'GetKey', 'GetKeys', 'GetTilt', 'GetTypeFromHeader',
           'LocateBadPixels', 'MakeTable', 'MeasureDark',
           'NormMedianFlat', 'ReadData',
           'ReadImage', 'ReadTable', 'ReadImageAndCombine',
           'ReadFlatFile', 'ReadHeader', 'ReadKey', 'Read2Dkey',
           'ReadTiltFile', 'ReadWaveFile', 'ReadOrderProfile',
           'ResizeImage', 'WriteImage', 'WriteTable']

# =============================================================================
# Function aliases
# =============================================================================
AddKey = spirouFITS.add_new_key

AddKey1DList = spirouFITS.add_key_1d_list

AddKey2DList = spirouFITS.add_key_2d_list

ConvertToE = spirouImage.convert_to_e

ConvertToADU = spirouImage.convert_to_adu

CopyOriginalKeys = spirouFITS.copy_original_keys

CopyRootKeys = spirouFITS.copy_root_keys

CorrectForDark = spirouImage.correct_for_dark

CorrectForBadPix = spirouImage.correct_for_badpix

FitTilt = spirouImage.fit_tilt

FlipImage = spirouImage.flip_image

GetAllSimilarFiles = spirouImage.get_all_similar_files

GetSigdet = spirouImage.get_sigdet

GetExpTime = spirouImage.get_exptime

GetBadPixMap = spirouImage.get_badpixel_map

GetGain = spirouImage.get_gain

GetAcqTime = spirouImage.get_acqtime

GetKey = spirouFITS.keylookup

GetKeys = spirouFITS.keyslookup

GetTilt = spirouImage.get_tilt

GetTypeFromHeader = spirouFITS.get_type_from_header

InterpolateBadRegions = spirouImage.interp_bad_regions

LocateBadPixels = spirouImage.locate_bad_pixels

LocateFullBadPixels = spirouImage.locate_bad_pixels_full

MakeTable = spirouTable.make_table

MeasureDark = spirouImage.measure_dark

MergeTable = spirouTable.merge_table

NormMedianFlat = spirouImage.normalise_median_flat

PPCorrectTopBottom = spirouImage.ref_top_bottom

PPMedianFilterDarkAmps = spirouImage.median_filter_dark_amp

PPMedianOneOverfNoise = spirouImage.median_one_over_f_noise

ReadParam = spirouImage.get_param

ReadData = spirouFITS.readdata

ReadImage = spirouFITS.readimage

ReadTable = spirouTable.read_table

ReadImageAndCombine = spirouFITS.readimage_and_combine

ReadFlatFile = spirouFITS.read_flat_file

ReadHeader = spirouFITS.read_header

ReadKey = spirouFITS.read_key

Read2Dkey = spirouFITS.read_key_2d_list

ReadTiltFile = spirouFITS.read_tilt_file

ReadLineList = spirouImage.read_line_list

ReadWaveFile = spirouFITS.read_wave_file

ReadBlazeFile = spirouFITS.read_blaze_file

ReadOrderProfile = spirouFITS.read_order_profile_superposition

ResizeImage = spirouImage.resize

WriteImage = spirouFITS.writeimage

WriteTable = spirouTable.write_table

# =============================================================================
# End of code
# =============================================================================

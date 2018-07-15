#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou Image processing module

Created on 2017-10-30 at 17:09

@author: cook

"""
from SpirouDRS import spirouConfig
from . import spirouFile
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
__all__ = ['AddKey', 'AddKey1DList', 'AddKey2DList', 'CheckFile', 'CheckFiles',
           'ConvertToE', 'ConvertToADU', 'CopyOriginalKeys', 'CopyRootKeys',
           'CorrectForDark', 'CorrectForBadPix', 'E2DStoS1D',
           'FitTilt', 'FlipImage', 'FiberParams', 'GetAllSimilarFiles',
           'GetSigdet', 'GetExpTime', 'GetBadPixMap', 'GetGain', 'GetAcqTime',
           'GetKey', 'GetKeys', 'GetTilt', 'GetTypeFromHeader',
           'IdentifyUnProFile', 'InterpolateBadRegions', 'LocateBadPixels',
           'LocateFullBadPixels', 'MakeTable', 'MeasureDark', 'MergeTable',
           'NormMedianFlat', 'PPCorrectTopBottom', 'PPMedianFilterDarkAmps',
           'PPMedianOneOverfNoise', 'ReadParam', 'ReadData', 'ReadImage',
           'ReadTable', 'ReadImageAndCombine', 'ReadFlatFile', 'ReadHeader',
           'ReadKey', 'Read2Dkey', 'ReadTiltFile', 'ReadLineList',
           'ReadWaveFile', 'ReadBlazeFile', 'ReadOrderProfile',
           'ResizeImage', 'WriteImage', 'WriteTable']


# =============================================================================
# Function aliases
# =============================================================================
AddKey = spirouFITS.add_new_key

AddKey1DList = spirouFITS.add_key_1d_list

AddKey2DList = spirouFITS.add_key_2d_list

CheckFile = spirouFile.check_file_id

CheckFiles = spirouFile.check_files_id

ConvertToE = spirouImage.convert_to_e

ConvertToADU = spirouImage.convert_to_adu

CopyOriginalKeys = spirouFITS.copy_original_keys

CopyRootKeys = spirouFITS.copy_root_keys

CorrectForDark = spirouImage.correct_for_dark

CorrectForBadPix = spirouImage.correct_for_badpix

E2DStoS1D = spirouImage.e2dstos1d

FitTilt = spirouImage.fit_tilt

FixNonPreProcess = spirouImage.fix_non_preprocessed

FlipImage = spirouImage.flip_image

FiberParams = spirouFile.fiber_params

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

GetWaveSolution = spirouImage.get_wave_solution

IdentifyUnProFile = spirouFile.identify_unprocessed_file

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

PrintTable = spirouTable.print_full_table

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

ReadWaveParams = spirouFITS.read_wave_params

ReadHcrefFile = spirouFITS.read_hcref_file

ReadBlazeFile = spirouFITS.read_blaze_file

ReadOrderProfile = spirouFITS.read_order_profile_superposition

ResizeImage = spirouImage.resize

RotateImage = spirouImage.rotate

WriteImage = spirouFITS.writeimage

WriteImageMulti = spirouFITS.write_image_multi

WriteS1D = spirouFITS.write_s1d

WriteTable = spirouTable.write_table


# =============================================================================
# End of code
# =============================================================================

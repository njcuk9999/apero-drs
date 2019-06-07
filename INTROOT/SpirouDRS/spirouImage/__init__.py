#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou Image processing module

Created on 2017-10-30 at 17:09

@author: cook

"""
from SpirouDRS import spirouConfig
from . import spirouBERV
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
__all__ = ['AddKey', 'AddKey1DList', 'AddKey2DList', 'AddQCKeys', 'CheckFile',
           'CheckFiles', 'CheckWaveSolConsistency', 'ConvertToE',
           'ConvertToADU', 'CopyOriginalKeys', 'CopyRootKeys', 'CorrectForDark',
           'CorrectForBadPix', 'E2DStoS1D', 'FitTilt', 'FlipImage',
           'FiberParams', 'GetSimilarDriftFiles', 'GetSigdet',
           'GetExpTime', 'GetBadPixMap', 'GetGain', 'GetAcqTime',
           'GetKey', 'GetKeys', 'GetTilt', 'GetTypeFromHeader',
           'IdentifyUnProFile', 'InterpolateBadRegions', 'LocateBadPixels',
           'LocateFullBadPixels', 'MakeTable', 'MeasureDark', 'MergeTable',
           'NormMedianFlat', 'PPCorrectTopBottom', 'PPMedianFilterDarkAmps',
           'PPMedianOneOverfNoise', 'ReadParam', 'ReadData', 'ReadImage',
           'ReadTable', 'ReadImageAndCombine', 'ReadFlatFile', 'ReadHeader',
           'ReadKey', 'Read2Dkey', 'ReadTiltFile', 'ReadLineList',
           'ReadBlazeFile', 'ReadOrderProfile',
           'ResizeImage', 'WriteImage', 'WriteTable',
           'GetEarthVelocityCorrection', 'EarthVelocityCorrection']


# =============================================================================
# Function aliases
# =============================================================================
AddKey = spirouFITS.add_new_key

AddKey1DList = spirouFITS.add_key_1d_list

AddKey2DList = spirouFITS.add_key_2d_list

AddQCKeys = spirouFITS.add_qc_keys

CheckFile = spirouFile.check_file_id

CheckFiles = spirouFile.check_files_id

CheckWaveSolConsistency = spirouFITS.check_wave_sol_consistency

CheckFitsLockFile = spirouFITS.check_fits_lock_file

CloseFitsLockFile = spirouFITS.close_fits_lock_file

ConvertToE = spirouImage.convert_to_e

ConvertToADU = spirouImage.convert_to_adu

ConstructMasterFP = spirouImage.construct_master_fp

CopyOriginalKeys = spirouFITS.copy_original_keys

CopyRootKeys = spirouFITS.copy_root_keys

CorrectForDark = spirouImage.correct_for_dark

CorrectForBadPix = spirouImage.correct_for_badpix

GetBackgroundMap = spirouImage.get_background_map

EATransform = spirouImage.ea_transform

E2DStoS1D = spirouImage.e2dstos1d

EarthVelocityCorrection = spirouBERV.earth_velocity_correction

FindFiles = spirouImage.get_files

FitTilt = spirouImage.fit_tilt

FixNonPreProcess = spirouImage.fix_non_preprocessed

FlipImage = spirouImage.flip_image

FiberParams = spirouFile.fiber_params

GetSimilarDriftFiles = spirouImage.get_all_similar_files

GetSigdet = spirouImage.get_sigdet

GetExpTime = spirouImage.get_exptime

GetEarthVelocityCorrection = spirouBERV.get_earth_velocity_correction

GetBERV = spirouBERV.get_berv_value

GetBadPixMap = spirouImage.get_badpixel_map

GetGain = spirouImage.get_gain

GetAcqTime = spirouImage.get_acqtime

GetKey = spirouFITS.keylookup

GetKeys = spirouFITS.keyslookup

GetTilt = spirouImage.get_tilt

GetShapeX = spirouImage.load_shape_x

GetShapeY = spirouImage.load_shape_y

GetShapeLocal = spirouImage.load_shape_local

GetXShapeMap = spirouImage.get_x_shape_map

GetYShapeMap = spirouImage.get_y_shape_map

GroupFilesByTime = spirouImage.group_files_by_time

GetObjName = spirouImage.get_obj_name

GetAirmass = spirouImage.get_airmass

GetMostRecent = spirouFile.get_most_recent

GetTypeFromHeader = spirouFITS.get_type_from_header

GetWaveSolution = spirouFITS.get_wave_solution

GetWaveKeys = spirouImage.get_wave_keys

IdentifyUnProFile = spirouFile.identify_unprocessed_file

InterpolateBadRegions = spirouImage.interp_bad_regions

LocateBadPixels = spirouImage.locate_bad_pixels

LocateFullBadPixels = spirouImage.locate_bad_pixels_full

MakeTable = spirouTable.make_table

MakeFitsTable = spirouTable.make_fits_table

MeasureDark = spirouImage.measure_dark

MergeTable = spirouTable.merge_table

NormMedianFlat = spirouImage.normalise_median_flat

OpenFitsLockFile = spirouFITS.open_fits_lock_file

PPCorrectTopBottom = spirouImage.ref_top_bottom

PPMedianFilterDarkAmps = spirouImage.median_filter_dark_amp

PPMedianOneOverfNoise = spirouImage.median_one_over_f_noise

PPMedianOneOverfNoise2 = spirouImage.median_one_over_f_noise2

PPGetHotPixels = spirouImage.get_hot_pixels

PPTestForCorruptFile = spirouImage.test_for_corrupt_files

PrintTable = spirouTable.print_full_table

ReadParam = spirouImage.get_param

ReadData = spirouFITS.readdata

ReadImage = spirouFITS.readimage

ReadTable = spirouTable.read_table

ReadFitsTable = spirouTable.read_fits_table

ReadImageAndCombine = spirouFITS.readimage_and_combine

ReadFlatFile = spirouFITS.read_flat_file

ReadHeader = spirouFITS.read_header

ReadKey = spirouFITS.read_key

Read1Dkey = spirouFITS.read_key_1d_list

Read2Dkey = spirouFITS.read_key_2d_list

ReadTiltFile = spirouFITS.read_tilt_file

ReadShapeMap = spirouFITS.read_shape_file

ReadLineList = spirouImage.read_line_list

ReadCavityLength = spirouImage.read_cavity_length

ReadHcrefFile = spirouFITS.read_hcref_file

ReadBlazeFile = spirouFITS.read_blaze_file

ReadOrderProfile = spirouFITS.read_order_profile_superposition

ResizeImage = spirouImage.resize

RotateImage = spirouImage.rotate

SortByName = spirouFile.sort_by_name

UpdateWaveSolution = spirouFITS.update_wave_sol

UpdateWaveSolutionHC = spirouFITS.update_wave_sol_hc

WriteImage = spirouFITS.writeimage

WriteImageMulti = spirouFITS.write_image_multi

WriteImageTable = spirouFITS.write_image_table

WriteTable = spirouTable.write_table

WriteFitsTable = spirouTable.write_fits_table

# =============================================================================
# End of code
# =============================================================================

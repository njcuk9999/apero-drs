#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-08 at 17:26

@author: cook
"""
from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
LANGUAGE = spirouConfig.Constants.LANGUAGE()
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
class General:
    if LANGUAGE == 'ENG':
        directory_help = """
[STRING] The "night_name" or absolute path of the directory
"""
        file_help = """
[STRING] A single fits files. 
"""
        files_help = """
[STRING/STRINGS] A list of fits files to use separated by spaces. 
"""
        add_cal_help = """
[BOOLEAN] Whether to add outputs to calibration database
"""
        dobad_help = """
[BOOLEAN] Whether to correct for the bad pixel file
"""
        badfile_help = """
[STRING] Define a custom file to use for bad pixel
         correction. Checks for an absolute path and then
         checks "directory".
"""
        backsub_help = """
[BOOLEAN] Whether to do background subtraction
"""
        blazefile_help = """
[STRING] Define a custom file to use for blaze correction. If unset uses 
         closest file from calibDB. Checks for an absolute path and then 
         checks "directory"
"""
        combine_help = """
[BOOLEAN] Whether to combine fits files in file list or to process them 
          separately
"""
        dodark_help = """
[BOOLEAN] Whether to correct for the dark file
"""
        darkfile_help = """
[STRING] Define a custom file to use for dark correction. Checks for an 
         absolute path and then checks "directory
"""
        extractmethod_help = """
[STRING] Define a custom extraction method
"""
        extfiber_help = """
[STRING] Define which fibers to extract
"""
        flatfile_help = """
[STRING] Define a custom file to use for flat correction. If unset uses 
         closest file from calibDB. Checks for an absolute path and then 
         checks "directory"
"""
        flipimage_help = """
[BOOLEAN] Whether to flip fits image
"""
        fluxunits_help = """
[STRING] Output units for flux
"""
        plot_help = """
[BOOLEAN] Manually turn on/off plot of graphs
"""
        resize_help = """
[BOOLEAN] Whether to resize image
"""
        shapefile_help = """
[STRING] Define a custom file to use for shape correction. If unset uses 
         closest file from calibDB. Checks for an absolute path and then 
         checks "directory".
"""
        tiltfile_help = """
[STRING] Define a custom file to use for tilt  correction. If unset uses 
         closest file from calibDB. Checks for an absolute path and then 
         checks "directory"
"""
        wavefile_help = """
[STRING] Define a custom file to use for the wave solution. If unset uses 
         closest file from header or calibDB (depending on setup). 
         Checks for an absolute path and then checks "directory"
"""


class Blank:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

No description

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    recipe.py [NIGHT_NAME] [ARG1]

====================================================
"""
        help = General.files_help + """
Currently allowed types: 
"""


class Test:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Test recipe - used to test the argument parser of the DRS

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    test.py [NIGHT_NAME] [DARK_DARK] [FLAT_FLAT]
    test.py 2018-08-05 2295520f_pp.fits dark_dark_P5_003d_pp.fits
    test.py 2018-08-05 2295520f_pp dark_dark_P5_003d_pp.fits
    test.py 2018-08-05 *f_pp *d_pp

====================================================
"""
        filelist_help = General.files_help + """
Currently allowed types: -DARK_DARK -FLAT_FLAT
"""


class Preprocess:
    if LANGUAGE == 'ENG':
       description =  """
====================================================
 Description: 
====================================================

Pre-processing recipe for SPIRou @ CFHT

====================================================
"""
       example = """
====================================================
 Example uses:
====================================================
    cal_preprocess_spirou.py [NIGHT_NAME] [FILES]
    cal_preprocess_spirou.p 2018-08-05 *.fits
    cal_preprocess_spirou.p 2018-08-05 dark_dark_P5_003d_pp.fits
    cal_preprocess_spirou.p 2018-08-05 *d_pp

====================================================
"""
       ufiles_help = General.files_help + """
Any raw files are currently allowed. Multiple files inputted are handled 
separately (one after the other).
"""


class Badpix:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Bad pixel finding recipe for SPIRou @ CFHT

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    cal_BADPIX_spirou.py [NIGHT_NAME] [FLAT_FLAT] [DARK_DARK]
    cal_BADPIX_spirou.py 2018-08-05 2295524f_pp.fits dark_dark_P5_003d_pp.fits
    cal_BADPIX_spirou.py 2018-08-05 2295524f_pp dark_dark_P5_003d_pp
    cal_BADPIX_spirou.py 2018-08-05 229552*f_pp d_pp.fits

====================================================
"""
        flatfile_help = General.file_help + """
Current allowed types: FLAT_FLAT
"""
        darkfile_help = General.file_help + """
Current allowed types: DARK_DARK
"""


class Dark:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Dark finding recipe for SPIRou @ CFHT

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    cal_DARK_spirou.py [NIGHT_NAME] [FILES]
    cal_DARK_spirou.py 2018-08-05 dark_dark_P5_003d_pp.fits
        cal_DARK_spirou.py 2018-08-05 dark_dark_P5_003d_pp
    cal_DARK_spirou.py 2018-08-05 *d_pp

====================================================
"""
        files_help = General.files_help + """
Current allowed types: DARK_DARK
"""


class Localisation:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Localisation finding recipe for SPIRou @ CFHT

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    cal_loc_RAW_spirou.py [NIGHT_NAME] [DARK_FLAT]
    cal_loc_RAW_spirou.py [NIGHT_NAME] [FLAT_DARK]
    cal_loc_RAW_spirou 2018-08-05 2295510f_pp.fits 2295511f_pp.fits 2295512f_pp.fits
    cal_loc_RAW_spirou 2018-08-05 2295515f_pp.fits 2295516f_pp.fits 2295517f_pp.fits
    cal_loc_RAW_spirou 2018-08-05 22955[10-14]f_pp.fits
    cal_loc_RAW_spirou 2018-08-05 22955[15-19]f_pp.fits

====================================================
"""
        files_help = General.files_help + """
Current allowed types: DARK_FLAT OR FLAT_DARK but not both (exclusive)
"""


class Slit:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Tilt finding recipe for SPIRou @ CFHT

Warning: Deprecated (old) recipe - use cal_SHAPE_spirou.py instead

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    cal_SLIT_spirou.py [NIGHT_NAME] [FP_FP]
    cal_SLIT_spirou.py 2018-08-05 2295525a_pp.fits
    cal_SLIT_spirou.py 2018-08-05 2295525a_pp
    cal_SLIT_spirou.py 2018-08-05 *a_pp.fits

====================================================
"""
        files_help = General.files_help + """
Current allowed types: FP_FP'
"""


class Shape:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Shape finding recipe for SPIRou @ CFHT

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    cal_SHAPE_spirou.py [NIGHT_NAME] [HCONE_HCONE] [FP_FP]
    cal_SHAPE_spirou.py 2018-08-05 2295680c_pp.fits 2295525a_pp.fits
    cal_SHAPE_spirou.py 2018-08-05 2295680c_pp 2295525a_pp
    cal_SHAPE_spirou.py 2018-08-05 2295680c_pp *a_pp.fits
    
====================================================
"""
        hcfile_help = General.file_help + """
Current allowed type: HCONE_HCONE 
"""
        fpfiles_help = General.files_help + """
Current allowed types: FP_FP'
"""


class Flat:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Flat/Blaze finding recipe for SPIRou @ CFHT

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    cal_FF_RAW_spirou.py [NIGHT_NAME] [FLAT_FLAT]
    cal_FF_RAW_spirou.py [NIGHT_NAME] [DARK_FLAT]
    cal_FF_RAW_spirou.py [NIGHT_NAME] [FLAT_DARK]
    cal_FF_RAW_spirou.py 2018-08-05 2295520f_pp.fits 2295521f_pp.fits
    cal_FF_RAW_spirou.py 2018-08-05 2295520f_pp 2295521f_pp
    cal_FF_RAW_spirou.py 2018-08-05 22955[20-24]f_pp.fits
    
====================================================
"""
        files_help = General.files_help + """
Current allowed types: FLAT_FLAT or DARK_FLAT or FLAT_DARK but not a mixture 
                       (exclusive)
"""


class Extract:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Extraction recipe for SPIRou @ CFHT

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    cal_extract_RAW_spirou.py [NIGHT_NAME] [FILES]
    cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp.fits
    cal_extract_RAW_spirou.py 2018-08-05 2295545o_pp.fits
    cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp
    cal_extract_RAW_spirou.py 2018-08-05 2295545o_pp
    cal_extract_RAW_spirou.py 2018-08-05 2295525a_pp.fits 2295526a_pp.fits

====================================================
"""
        files_help = General.files_help + """
All files used will be combined into a single frame.
"""



class HcE2DS:
    if LANGUAGE == 'ENG':
        description = """
====================================================
 Description: 
====================================================

Wavelength solution finding recipe for SPIRou @ CFHT
Uses the less accurate method using only a HCONE_HCONE file 

====================================================
"""
        example = """
====================================================
 Example uses:
====================================================
    recipe.py [NIGHT_NAME] [ARG1]

====================================================
"""
        files_help = General.files_help + """
Currently allowed type: 
    DRS_EOUT = EXT_E2DS_AB (HCONE_HCONE) or EXT_E2DS_A (HCONE_HCONE)
               or EXT_E2DS_B (HCONE_HCONE) or EXT_E2DS_C (HCONE_HCONE)
"""

# =============================================================================
# End of code
# =============================================================================

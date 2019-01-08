#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-08 at 17:26

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings


# =============================================================================
# Define variables
# =============================================================================
LANGUAGE = 'ENG'
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
    test.py [NIGHT_NAME] [DARK_DARK] [FLAT_FLAT]'
    test.py 2018-08-05 2295520f_pp.fits dark_dark_P5_003d_pp.fits
    test.py 2018-08-05 2295520f_pp dark_dark_P5_003d_pp.fits
    test.py 2018-08-05 *f_pp *d_pp
    
====================================================
"""
        help = General.files_help + """
Currently allowed types: -DARK_DARK -FLAT_FLAT
"""




# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

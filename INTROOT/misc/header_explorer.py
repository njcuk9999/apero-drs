#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-11-19 09:33
@author: ncook
Version 0.0.1
"""
import numpy as np
from astropy.io import fits
import os

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = './'


# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def function():
    pass


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get list of files
    files = os.listdir(WORKSPACE)
    # sort files by name
    files = np.sort(files)
    # loop around files
    for filename in files:

        if 'tellu_corrected' not in filename:
            continue

        header = fits.getheader(filename)

        date = header['DATE-OBS'] + ' ' + header['UTC-OBS']
        print(filename, '\t\t\t', date, '\t\t\t', header['WAVEFILE'])

# =============================================================================
# End of code
# =============================================================================
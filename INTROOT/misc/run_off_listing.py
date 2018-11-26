#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-11-26 08:51
@author: ncook
Version 0.0.1
"""
import os
import off_listing_RAW_spirou
import off_listing_REDUC_spirou

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/spirou/cfht_nights/cfht/reduced_ea/'
RAWFOLDER = ''
REDUCEDFOLDER = ''

mode = 'raw'
mode = 'reduced'
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
    # Get directories
    files = os.listdir(WORKSPACE)
    # loop around files
    for filename in files:
        # check if directory
        if not os.path.isdir(filename):
            continue
        # try to run off-listing is directory
        try:
            # deal with raw off listing
            if mode == 'raw':
                # get night name
                night_name = filename
                # run off listing
                off_listing_RAW_spirou.main(night_name)
            # deal with reduced off listing
            if mode == 'reduced':
                # get night name
                night_name = filename
                # run off listing
                off_listing_REDUC_spirou.main(night_name)



# =============================================================================
# End of code
# =============================================================================
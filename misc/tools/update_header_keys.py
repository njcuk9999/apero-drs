#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-21

@author: cook
"""
from pathlib import Path
from astropy.io import fits
import os


# =============================================================================
# Define variables
# =============================================================================
# define workspace
WORKSHAPE = '.'
UPDATE_FILE = WORKSHAPE + '/' + 'vupdate.txt'
# define keys to change
KEYS = dict()
KEYS['PVERSION'] = '0.6.100'
KEYS['DRSVDATE'] = '2020-06-08'
KEYS['VERSION'] = '0.6.100'

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # get all files related to pre-processed files
    files = Path(WORKSHAPE).glob('*/*pp*.fits')
    # load the update file
    if os.path.exists(UPDATE_FILE):
        with open(UPDATE_FILE, 'r') as ufile:
            lines = ufile.readlines()
    else:
        lines = []
    # filter out done targets
    unchanged_files = []
    # loop around files
    for filename in files:
        if str(filename) not in lines:
            unchanged_files.append(filename)
    # loop around files
    for f_it, filename in enumerate(unchanged_files):
        # print progress
        pargs = [f_it + 1, len(unchanged_files), filename]
        print('Processing {0} of {1} ({2})'.format(*pargs))
        # open fits file
        try:
            hdulist = fits.open(str(filename))
        except Exception as e:
            print('\tWARNING: {0}: {1}'.format(type(e), e))
            continue
        # loop around extensions
        for h_it in range(len(hdulist)):
            # check if we have a header
            if hasattr(hdulist[h_it], 'header'):
                # check and change the keys
                for key in KEYS:
                    # update header key
                    hdulist[h_it].header[key] = KEYS[key]

        # save hdu to file
        hdulist.writeto(str(filename), overwrite=True)
        # after this add to update file
        lines.append(str(filename))
        with open(UPDATE_FILE, 'w') as ufile:
            for line in lines:
                ufile.write(line + '\n')


# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-11-13 20:51
@author: ncook
Version 0.0.1
"""
from astropy.io import fits
import numpy as np
import warnings

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/media/sf_Astro/Projects/spirou_py3/data_h4rg/raw/'
FILES = ['AT5/20180407/dark_dark_001d.fits',
         'TEST1/20180805/dark_dark_P5_003d.fits',
         'AT5/20180409a/23456d.fits',
         'TEST3/20180526/2279303d.fits',
         'AT5/20180529/dark_dark_001d.fits',
         'AT5/20180801/2295060f.fits',
         'AT5/20180801/2295076c.fits',
         'AT5/20180729/2294652a.fits']
GOOD = [True, True, True, True, True, False, False, False]


# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def stats(iterator, isgood, image, hdr, kind='med'):

    _ = hdr

    with warnings.catch_warnings(record=True) as _:
        if kind == 'med':
            med = np.nanmedian(image)
            print('\t{0} [{1}] Median = {2}'.format(iterator, isgood, med))

        elif kind == 'numdark':
            darkampmask = image[:, :600] > 10
            num = np.nansum(darkampmask)
            pargs = [iterator, isgood, num]
            print('\t{0} [{1}] Num > 10 (X 0:600) = {2}'.format(*pargs))


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    #  loop around files and open them into data array
    data_array = []
    header_array = []
    for filename in FILES:
        print('Loading file {0}{1}'.format(WORKSPACE, filename))
        data = np.array(fits.getdata(WORKSPACE + filename))
        header = dict(**fits.getheader(WORKSPACE + filename))

        data_array.append(data)
        header_array.append(header)

    # median
    print('Medians: ')
    for it in range(len(data_array)):
        stats(it, GOOD[it], data_array[it], header_array[it], kind='med')

    # numdark
    print('Num dark (> 10 for X between 0 and 600)')
    for it in range(len(data_array)):
        stats(it, GOOD[it], data_array[it], header_array[it], kind='numdark')

# =============================================================================
# End of code
# =============================================================================
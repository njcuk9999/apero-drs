#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-17 at 16:54

@author: cook
"""

import numpy as np
import os
import shutil

# =============================================================================
# Define variables
# =============================================================================
input_dir = '/spirou/cfht_nights/calibDB_cfht/'
output_dir = '/spirou/cfht_nights/calibDB_cfht2/'

filename = 'master_calib_SPIROU.txt'


good_keys = ['DARK', 'BADPIX_OLD', 'BADPIX',
             'LOC_AB', 'LOC_C',
             'ORDER_PROFILE_AB', 'ORDER_PROFILE_C',
             'SHAPE', 'TILT',
             'BLAZE_AB', 'BLAZE_A', 'BLAZE_B', 'BLAZE_C',
             'FLAT_AB', 'FLAT_A', 'FLAT_B', 'FLAT_C']


# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # first read file
    table = np.loadtxt(os.path.join(input_dir, filename), dtype=str)
    # keep only good keys
    print('Filtering table...')
    mask = np.zeros(len(table), dtype=bool)
    for good_key in good_keys:
        # append to the mask
        mask |= table[:, 0] == good_key

    # next check for files existing
    for row in range(len(table)):
        # construct file path
        abs_path = os.path.join(input_dir, table[row, 2])
        # check that it exists
        if not os.path.exists(abs_path):
            mask[row] = False

    # next copy good files to new folder
    print('Copying good files to output dir...')
    for row in range(len(table)):
        # if mask is False do not copy
        if not mask[row]:
            continue
        else:
            # construct file path
            oldpath = os.path.join(input_dir, table[row, 2])
            newpath = os.path.join(output_dir, table[row, 2])
            # print progress
            print('Copying {0}-->{1}'.format(oldpath, newpath))
            # copy
            shutil.copy(oldpath, newpath)

    # next remake master file
    print('Constructing new master file...')
    lines = []
    for row in range(len(table)):
        # if mask if False do not add
        if not mask[row]:
            continue
        else:
            lines.append(' '.join(table[row]) + '\n')

    # Save new master file
    outpath = os.path.join(output_dir, filename)
    print('Saving new master file to: {0}'.format(outpath))
    outfile = open(outpath, 'w')
    outfile.writelines(lines)
    outfile.close()

# =============================================================================
# End of code
# =============================================================================

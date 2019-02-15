#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-31 at 12:53

@author: cook
"""

import numpy as np
import os
import shutil
import glob

# =============================================================================
# Define variables
# =============================================================================
CALIBPATH = '/spirou/cfht_nights/cfht_Jan19/calibDB_1'
OUTPATH = '/spirou/cfht_nights/cfht_Jan19/calibDB_1'
CALIBFILE = 'master_calib_SPIROU.txt'
CLEAN_CALIBFILE = 'master_calib_SPIROU_clean.txt'
# -----------------------------------------------------------------------------
VALID_KEYS = ['DARK', 'BADPIX_OLD', 'BADPIX',
              'LOC_AB', 'LOC_C',
              'ORDER_PROFILE_AB', 'ORDER_PROFILE_C',
              'SHAPE', 'TILT',
              'BLAZE_AB', 'BLAZE_A', 'BLAZE_B', 'BLAZE_C',
              'FLAT_AB', 'FLAT_A', 'FLAT_B', 'FLAT_C',
              'WAVE_AB', 'WAVE_A', 'WAVE_B', 'WAVE_C',
              'HCREF_AB', 'HCREF_A', 'HCREF_B', 'HCREF_C']

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # load fits files in calibdb
    fitsfiles = glob.glob(os.path.join(CALIBPATH, '*.fits'))
    # load calibdb database
    entries = np.loadtxt(os.path.join(CALIBPATH, CALIBFILE), dtype=str)

    # found file storage
    found_files = []
    valid_entries = []
    all_calib_entries = []
    unfound_entries = []
    unfound_files = []

    # search for entries in calibDB but not in files
    for it, entry in enumerate(entries):
        # print progress
        if it % 100 == 0:
            print('Scanning entry {0} of {1}...'.format(it, len(entries)))
        # make sure key is valid
        if entry[0] not in VALID_KEYS:
            continue
        # get filename
        filename = entry[2]
        # condition to be found
        found = False
        # check if file exists
        if os.path.exists(os.path.join(CALIBPATH, filename)):
            found_files.append(filename)
            valid_entries.append(entry)
        else:
            unfound_entries.append(filename)
        # append to all_files
        all_calib_entries.append(filename)

    # now search for files which aren't in the calibDB
    for it, fitsfile in enumerate(fitsfiles):
        # print progress
        if it % 100 == 0:
            print('Scanning file {0} of {1}...'.format(it, len(fitsfiles)))
        # get base filename
        bfitsfile = os.path.basename(fitsfile)
        # find if file is in entry
        if bfitsfile in all_calib_entries:
            continue
        # if not add it to unfoudn
        else:
            unfound_files.append(bfitsfile)

    # print stats
    print('Found {0} files out of {1} total files {2} total entries'
          ''.format(len(found_files), len(fitsfiles), len(all_calib_entries)))
    print('Missing {0} files (with no file)'.format(len(unfound_entries)))
    print('Missing {0} files (with no entry)'.format(len(unfound_files)))

    # get list of valid entries
    str_valid_entries = []
    for valid_entry in valid_entries:
        str_valid_entries.append(' '.join(valid_entry) + '\n')

    # write new calibdatabase
    outfile = os.path.join(CALIBPATH, CLEAN_CALIBFILE)
    print('Writing to file: {0}'.format(outfile))
    f = open(outfile, 'w')
    for valid_entry in np.sort(str_valid_entries):
        f.write(valid_entry)
    f.close()


    # if we are staying in the same folder, just remove other files
    if OUTPATH == CALIBPATH:
        # remove unneeded files by looping around filename
        for filename in unfound_files:
            rm_name = os.path.join(CALIBPATH, filename)
            print('Removing file {0}'.format(rm_name))
            os.remove(rm_name)
        # move calibration database
        shutil.move(outfile, os.path.join(CALIBPATH, CALIBFILE))
    # else copy only required to new folder
    else:
        # copy only required files to new folder by looping around filename
        for filename in found_files:
            old_path = os.path.join(CALIBPATH, filename)
            new_path = os.path.join(OUTPATH, filename)
            print('Copying file {0}'.format(filename))
            shutil.copy(old_path, new_path)
        # move calibration database
        shutil.move(outfile, os.path.join(OUTPATH, CALIBFILE))


# =============================================================================
# End of code
# =============================================================================

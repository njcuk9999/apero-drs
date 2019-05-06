#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-02-05 at 10:18

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
import warnings
import glob
import os
from collections import OrderedDict
import shutil


# =============================================================================
# Define variables
# =============================================================================
PATH = '/spirou/cfht_nights/cfht_April19/pernight/calibDB_master/'

FILE = 'master_calib_SPIROU.txt'

OUTFILE1 = 'master_calib_SPIROU_pernight.txt'
OUTFILE2 = 'master_calib_SPIROU_pertc.txt'


OUTFOLDER1 = '/spirou/cfht_nights/cfht_April19/pernight/calibDB/'
OUTFOLDER2 = '/spirou/cfht_nights/cfht_April19/perrun/calibDB/'

# -----------------------------------------------------------------------------
# if true use TC_DATES to select calib files
TC_DATES = OrderedDict(tc2=1527445620.0, tc3=1533144101.0,
                       tc4=1537723992.0, tc5=1540519817.9,
                       tc6=1545188394.0, tc7=1547746944.8)


HEADER = """# H4RG File (Copied from SpirouDRS data folder)
WAVE_AB None MASTER_WAVE.fits 1970-01-01-00:00:00.000000 0.0
WAVE_A None MASTER_WAVE.fits 1970-01-01-00:00:00.000000 0.0
WAVE_B None MASTER_WAVE.fits 1970-01-01-00:00:00.000000 0.0
WAVE_C None MASTER_WAVE.fits 1970-01-01-00:00:00.000000 0.0

#Drs Processed
"""

SKIP_FOUND = True


# =============================================================================
# Define functions
# =============================================================================
def sort_entries(old_entries):
    new_entries = []

    tags = np.array(old_entries[:, 0])
    utags = np.unique(tags)
    dates = np.array(old_entries[:, -1], dtype=float)

    for tag in np.sort(utags):
        # find tags
        tagmask = tags == tag
        # sort these entries by date
        sortmask = np.argsort(dates[tagmask])
        # get the tag entries
        tagentries = old_entries[tagmask]
        # loop around these and add to new entries
        for entry in tagentries[sortmask]:
            new_entries.append(entry)

    return np.array(new_entries)



def copy_files(my_entries, outpath):


    for row in range(len(my_entries)):

        filename = my_entries[row, 2]

        infilename = os.path.join(PATH, filename)
        outfilename = os.path.join(outpath, filename)

        if SKIP_FOUND:
            if os.path.exists(outfilename):
                continue

        # print progress
        print('Copying {0} --> {1}'.format(infilename, outfilename))

        shutil.copy(infilename, outfilename)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # load calib file
    calibdata = np.loadtxt(os.path.join(PATH, FILE), dtype=str)
    # get filenames from calib
    calibfiles = calibdata[:, 2]

    # load filenames
    fitsfiles = glob.glob(os.path.join(PATH, '*.fits'))

    # locate found calib files
    found = []
    entries = []
    for row, calibfile in enumerate(calibfiles):
        # skip if in header
        if ' '.join(list(calibdata[row])) in HEADER.split('\n'):
            continue

        calibabsfile = os.path.join(PATH, calibfile)
        if calibabsfile in fitsfiles:
            if calibfile not in found:
                found.append(calibfile)
                entries.append(calibdata[row])

    # convert entries to array
    entries = np.array(entries)
    entries = sort_entries(entries)

    # get tags
    tags = np.unique(entries[:, 0])

    # deal with per tc file
    tc_entries = []
    # get entry dates
    entry_dates = np.array(entries[:, -1], dtype=float)
    # loop around tags
    for tag in np.sort(tags):
        # create mask for this tag type
        tag_mask = entries[:, 0] == tag
        # loop around TC_DATES
        for tc_date in np.sort(list(TC_DATES.keys())):
            # get distance from tc_date
            diff_dates = np.abs(entry_dates - TC_DATES[tc_date])
            pos_dates = np.indices(diff_dates.shape)[0]
            # get closest diff date with this tag
            closest_pos_mask = np.argmin(diff_dates[tag_mask])
            closest_pos_all = pos_dates[tag_mask][closest_pos_mask]
            # get tc_entry
            tc_entry = entries[closest_pos_all]
            # append to entries
            tc_entries.append(tc_entry)

    # convert entries to array
    tc_entries = np.array(tc_entries)
    tc_entries = sort_entries(tc_entries)

    # save text
    outfile = open(os.path.join(OUTFOLDER1, OUTFILE1), 'w')
    print('Saving to {0}'.format(outfile))
    outfile.write(HEADER)
    for line in range(len(entries)):
        outfile.write(' '.join(entries[line]) + '\n')
    outfile.close()

    # save text
    outfile = open(os.path.join(OUTFOLDER2, OUTFILE2), 'w')
    print('Saving to {0}'.format(outfile))
    outfile.write(HEADER)
    for line in range(len(tc_entries)):
        outfile.write(' '.join(tc_entries[line]) + '\n')
    outfile.close()

    # copy files from entries
    copy_files(entries, OUTFOLDER1)
    copy_files(tc_entries, OUTFOLDER2)


# =============================================================================
# End of code
# =============================================================================

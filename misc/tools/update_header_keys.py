#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-21

@author: cook
"""
import numpy as np
from pathlib import Path
from astropy.io import fits
import os
from multiprocessing import Pool

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
# define number of cores to use
NUMBER_OF_CORES = 20
# debug mode
DEBUG = False
# toggle file location
#     SUBDUR=0 means search here i.e. *.fits
#     SUBDIR=1 means search in subdirs i.e. */*.fits
SUBDIR = 0

# =============================================================================
# Define functions
# =============================================================================
class Engine:
    def __init__(self, filelist, lines):
        self.filelist = filelist
        self.lines = lines

    def __call__(self, iterator):
        filename = self.filelist[iterator]
        # print progress
        pargs = [iterator + 1, len(self.filelist), filename]
        print('Processing {0} of {1} ({2})'.format(*pargs))

        # skip if debug
        if not DEBUG:
            # open fits file
            try:
                hdulist = fits.open(str(filename))
            except Exception as e:
                print('\tWARNING: {0}: {1}'.format(type(e), e))
                return
            # loop around extensions
            for h_it in range(len(hdulist)):
                # check if we have a header
                if hasattr(hdulist[h_it], 'header'):
                    # check and change the keys
                    for key in KEYS:
                        if key not in hdulist[h_it].header:
                            wmsg = '\tWARNING: key {0} not in header'
                            print(wmsg.format(key))
                            return
                        # if one of the keys matches assume all keys do
                        if hdulist[h_it].header[key] == KEYS[key]:
                            self.lines.append(str(filename))
                            return
                        # update header key
                        hdulist[h_it].header[key] = KEYS[key]
                # save hdu to file
                hdulist.writeto(str(filename), overwrite=True)
                # append to lines
                self.lines.append(str(filename))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # get all files related to pre-processed files
    if SUBDIR == 1:
        files = Path(WORKSHAPE).glob('*/*pp*.fits')
    else:
        files = Path(WORKSHAPE).glob('*pp*.fits')
    # load the update file
    if os.path.exists(UPDATE_FILE):
        with open(UPDATE_FILE, 'r') as ufile:
            lines = ufile.readlines()
    else:
        lines = []
    # print how many found
    print('Found {0} done files'.format(len(lines)))
    # filter out done targets
    unchanged_files = []
    # loop around files
    for filename in files:
        if str(filename) not in lines:
            unchanged_files.append(filename)
    # print how many left
    print('Found {0} undone files'.format(len(unchanged_files)))
    # start the engine
    engine = Engine(filelist=unchanged_files, lines=lines)
    # try to run
    try:
        pool = Pool(NUMBER_OF_CORES)
        pool.map(engine, np.arange(len(unchanged_files)).astype(int))
    finally:
        # after this add to update file
        lines = engine.lines
        with open(UPDATE_FILE, 'w') as ufile:
            for line in lines:
                ufile.write(line + '\n')


# =============================================================================
# End of code
# =============================================================================

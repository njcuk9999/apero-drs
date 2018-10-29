#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-16 at 15:30

@author: cook
"""
import numpy as np
from astropy.io import fits
from astropy.table import Table
import glob
import os


# =============================================================================
# Define variables
# =============================================================================
DIR = '/spirou/cfht_nights/calibDB/'

EXT = '_pp_wave_*.fits'
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def print_full_table(ptable):
    tablestrings = ptable.pformat(max_lines=len(table)*10,
                                  max_width=9999)
    for tablestring in tablestrings:
        print(tablestring)


def get_key(hdr, key):
    if key not in hdr:
        return 'None'
    else:
        return str(hdr[key])


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get all files
    print('Getting files...')
    filenames = glob.glob(DIR + '*' + EXT)
    # set up storage
    files, nights = [], []
    wavefiles, versions, wavenbos = [], [], []
    outputs, hcfiles, fpfiles = [], [], []
    # loop around files
    print('Opening file headers...')
    for it, filename in enumerate(filenames):
        # log progress
        print('\t File {0} of {1}'.format(it+1, len(filenames)))
        # get the header
        header = fits.getheader(filename)
        # get parameters
        basename = os.path.basename(filename)
        night_name = os.path.basename(os.path.dirname(filename))
        wavefile = get_key(header, 'WAVEFILE')
        version = get_key(header, 'VERSION')
        wavenbo = get_key(header, 'TH_LL_D')
        output = get_key(header, 'DRSOUTID')
        hcfile = get_key(header, 'HCFILE')
        fpfile = get_key(header, 'FPFILE')
        # append to lists
        files.append(basename)
        nights.append(night_name)
        wavefiles.append(wavefile)
        versions.append(version)
        wavenbos.append(wavenbo)
        outputs.append(output)
        hcfiles.append(hcfile)
        fpfiles.append(fpfile)

    # push into table
    print('Printing table...')
    table = Table()
    table['FILE'] = files
    table['NIGHT NAME'] = nights
    table['WAVEFILE'] = wavefiles
    table['VERSION'] = versions
    table['NCOEFF'] = wavenbos
    table['OUTPUT'] = outputs
    table['HCFILE'] = hcfiles
    table['FPFILE'] = fpfiles
    # sort by filename
    indices = np.argsort(files)
    table = table[indices]

    # display table
    print_full_table(table)


# =============================================================================
# End of code
# =============================================================================

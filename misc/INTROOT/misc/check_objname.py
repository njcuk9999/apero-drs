#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-02-06 at 12:17

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
import warnings
import os


# =============================================================================
# Define variables
# =============================================================================
PATH = '/spirou/cfht_nights/common/tmp'

INDEX_FILENAME = 'index.fits'

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def find_files(path, infilename):
    outfiles = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == infilename:
                outfiles.append(os.path.join(root, filename))
    return outfiles


def get_all_props(ifiles):

    filenames, objectnames, dnames = [], [], []

    for it, ifile in enumerate(ifiles):

        print('Accessing index file {0} of {1}'.format(it + 1, len(ifiles)))

        data = Table.read(ifile)

        filenames += list(data['FILENAME'])
        objectnames += list(data['OBJNAME'])
        dnames += list(data['DPRTYPE'])

    return filenames, objectnames, dnames


def print_entries(entries):

    for key in np.sort(entries.keys()):
        print('='*80)
        print(' DPRTYPE = {0}'.format(key))
        print('='*80)

        for key1 in np.sort(entries[key].keys()):
            print('\t {0:30s} \t\t Number={1}'.format(key1, entries[key][key1]))
    print()
    print()



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # find index files
    index_files = find_files(PATH, INDEX_FILENAME)

    # get all objnames and dprtypes
    files, objnames, dprtypes = get_all_props(index_files)

    # get unique objnames and dprtypes
    u_objnames = np.unique(objnames)
    u_dprtypes = np.unique(dprtypes)

    # sorted dictionary
    data = dict()

    # sort into groups based on dprtypes and objnames
    for it in range(len(files)):

        if it % 100 == 0:
            print('Analysing object {0} of {1}'.format(it +1, len(files)))

        for u_dprtype in u_dprtypes:

            if dprtypes[it] != u_dprtype:
                continue

            # sub dictionary on objname
            if u_dprtype not in data:
                data[u_dprtype] = dict()

            for u_objname in u_objnames:

                if objnames[it] != u_objname:
                    continue

                if u_objname not in data[u_dprtype]:
                    data[u_dprtype][u_objname] = 1
                else:
                    data[u_dprtype][u_objname] += 1


# =============================================================================
# End of code
# =============================================================================

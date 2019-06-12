#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-02-15 at 14:51

@author: cook
"""
import numpy as np
import os
from astropy.table import Table
from collections import OrderedDict
import pandas as pd

# =============================================================================
# Define variables
# =============================================================================
PATH = '/spirou/cfht_nights/common/tmp'

INDEX_FILENAME = 'index.fits'
# filters
DPRTYPES = ['OBJ_FP', 'OBJ_DARK']
OBJNAMES = ['Gl436']
OBJNAMES = ['74PscB', '31Cas', 'gamTri', 'HR875', 'HR1314', 'pi.02Ori',
            'HR1832', 'zetLep', 'HR2180', 'HR2209', '24Lyn', 'HR3131',
            '33Lyn', 'etaPyx', '23LMi', 'lLeo', 'phiLeo', 'HR4687', 'HR4722',
            'zetVir', '82UMa', 'HD130917', 'betSer', 'HR6025', 'HD159170',
            'gamSct', '51Dra', 'iotCyg', 'omiCapA', 'chiCap', '17Peg',
            'HR8489', '59Peg']
# display columns
DISPALY_COLS = ['SOURCE', 'FILENAME', 'OBJNAME', 'DATE-OBS', 'UTC-OBS', 'EXPTIME']
DISPALY_COLS = ['SOURCE', 'FILENAME', 'OBJNAME', 'DATE-OBS', 'UTC-OBS']

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def get_index_files(path):
    # storage for index files
    index_files = []
    # walk through all sub-directories
    for root, dirs, files in os.walk(path):
        # loop around files in current sub-directory
        for filename in files:
            # only save index files
            if filename == INDEX_FILENAME:
                # append to storage
                index_files.append(os.path.join(root, filename))
    # return index files
    return index_files


def combine_files(files):

    # define storage
    storage = OrderedDict()
    storage['SOURCE'] = []
    # print that we are indexing
    print('Reading all index files (N={0})'.format(len(files)))
    # loop around file names
    for it, filename in enumerate(files):
        # get data from table
        data = Table.read(filename)
        # loop around columns and add to storage
        for col in data.colnames:
            if col not in storage:
                storage[col] = list(data[col])
            else:
                storage[col] += list(data[col])

        storage['SOURCE'] += [os.path.dirname(filename)] * len(data)


    # return storage as pandas dataframe
    df = pd.DataFrame(data=storage)
    return df


def apply_filters(df, **kwargs):
    # filter
    mask = np.ones(len(df), dtype=bool)
    for kwarg in kwargs:
        if kwargs[kwarg] is not None:
            mask_k = np.zeros(len(df), dtype=bool)
            for element in kwargs[kwarg]:
                mask_k |= df[kwarg] == element
            mask &= mask_k
    # return the mask
    return mask


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get index files
    ifiles = get_index_files(PATH)
    # ----------------------------------------------------------------------
    # combine table
    fulltable = combine_files(ifiles)
    # ----------------------------------------------------------------------
    # apply filters (as required)
    mask = apply_filters(fulltable, DPRTYPE=DPRTYPES, OBJNAME=OBJNAMES)
    # get selected table
    selecttable = fulltable[mask]
    # dispaly selected columns
    print('Found {0} row(s) \n'.format(np.sum(mask)))
    with pd.option_context('display.max_rows', None):
        print(selecttable[DISPALY_COLS])


# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-04-25 at 10:03

@author: cook
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings


# =============================================================================
# Define variables
# =============================================================================
INPUT1 = '/scratch/Projects/spirou/data_dev_nonan/reduced/'
NAME1 = 'NO NAN'
INPUT2 = '/scratch/Projects/spirou/data_dev_nan/reduced/'
NAME2 = 'NAN'


OUTPUT = '/scratch/Projects/spirou/data_dev_nan_diff/reduced/'

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def find_files(path):
    outfiles = []
    for root, dirs, files in os.walk(path):
        # get uncommon path
        cpath = os.path.commonpath([path, root])
        upath = root.split(cpath + os.sep)[-1]
        for filename in files:
            fpath = os.path.join(upath, filename)
            outfiles.append(fpath)
    return outfiles


def add_to_stats(d1, d2, diff, dheader):

    dheader['@MEAN'] = (np.nanmean(diff), 'Mean of diff')
    dheader['@MEDIAN'] = (np.nanmedian(diff), 'Median of diff')
    dheader['@STD'] = (np.nanstd(diff), 'Std of diff')

    dheader['@IN1MAX'] = (np.nanmax(d1), 'max of 1')
    dheader['@IN1MIN'] = (np.nanmin(d1), 'min of 1')

    dheader['@IN2MAX'] = (np.nanmax(d2), 'max of 2')
    dheader['@IN2MIN'] = (np.nanmin(d2), 'min of 2')

    dheader['@DIFFMAX'] = (np.nanmax(diff), 'max of diff')
    dheader['@DIFFMIN'] = (np.nanmin(diff), 'min of diff')

    return dheader


def diff_header(h1, h2):

    keys = np.unique(list(h1.keys()) + list(h2.keys()))

    dheader = fits.Header()

    for key in keys:
        if key not in h1.keys():
            value = 'NOT IN 1'
            comment = h2.comments[key]
        elif key not in h2.keys():
            value = 'NOT IN 2'
            comment = h1.comments[key]
        else:
            value1 = h1[key]
            value2 = h2[key]
            comment = h1.comments[key]
            # get diff value
            try:
                value = value1 - value2
                if value == 0:
                    value = '@SAME'
                else:
                    value = str(value)
            except Exception:
                if value1.strip() == value2.strip():
                    value = '@SAME'
                else:
                    value = '{0} /\ {1}'.format(value1, value2)

        if value == '@SAME':
            continue
        else:
            dheader[key] = (value, comment)

    return dheader


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get files in input 1
    files1 = find_files(INPUT1)
    # get files in input 2
    files2 = find_files(INPUT2)
    # ----------------------------------------------------------------------
    jointfiles = []
    print('Checking file outputs the same')
    for filename in files1:
        if filename not in files2:
            emsg = '\tError file {0} in {1} files but not in {2} files'
            print(emsg.format(filename, NAME1, NAME2))
        else:
            jointfiles.append(filename)
    for filename in files2:
        if filename not in files2:
            emsg = '\tError file {0} in {1} files but not in {2} files'
            print(emsg.format(filename, NAME2, NAME1))
    # ----------------------------------------------------------------------
    # loop around and diff files
    print('Producing difference images/headers')
    for it, filename in enumerate(jointfiles):
        # print progress
        print('\tProcessing file {0} / {1}'.format(it + 1, len(jointfiles)))
        # skip non fits files
        if not filename.endswith('.fits'):
            print('\t\t Skipping {0}'.format(filename))
            continue
        # get file paths
        abspath1 = os.path.join(INPUT1, filename)
        abspath2 = os.path.join(INPUT2, filename)
        # load files
        data1, header1 = fits.getdata(abspath1, header=True)
        data2, header2 = fits.getdata(abspath2, header=True)
        # diff file
        try:
            diff_12 = data1 - data2
        except Exception as e:
            print('\t\t Skipping with error')
            print('\t\t Error {0}: {1}'.format(type(e), e))
            continue
        # diff header
        header_12 = diff_header(header1, header2)
        with warnings.catch_warnings(record=True) as _:
            header_12 = add_to_stats(data1, data2, diff_12, header_12)
        # construct diff file output name
        indir = os.path.dirname(filename)
        infile = os.path.basename(filename)
        outpath = os.path.join(OUTPUT, indir)
        outfile = os.path.join(outpath, 'DIFF_' + infile)
        # check outpath directory
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        # write diff file
        with warnings.catch_warnings(record=True) as _:
            fits.writeto(outfile, diff_12, header=header_12, overwrite=True)



# =============================================================================
# End of code
# =============================================================================

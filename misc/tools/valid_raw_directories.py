#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-21

@author: cook
"""
import numpy as np
from astropy.io import fits
from  pathlib import Path
from typing import Tuple, Dict

# =============================================================================
# Define variables
# =============================================================================
# define workspace
WORKSPACE = '/spirou/cfht_nights/common/raw/'
WORKSPACE = '/spirou/cfht_nights/common/rawsym/'

# use header
USE_HDR = True
# skip engineering
SKIP_ENGINEERING = True

# define required file types
REQ_FILES = dict()
REQ_FILES['DARK_DARK'] = 'd.fits', 1
REQ_FILES['DARK_FLAT'] = 'f.fits', 3
REQ_FILES['FLAT_DARK'] = 'f.fits', 3
REQ_FILES['FLAT_FLAT'] = 'f.fits', 3
REQ_FILES['FP_FP'] = 'a.fits', 3
REQ_FILES['HC_HC'] = 'c.fits', 1

# a more in depth requirement
# SBCCAS_P, SBCREF_P, EXT, MIN NUMBER
REQ_HDR = dict()
REQ_HDR['DARK_DARK'] = 'pos_pk', 'pos_pk', 'd.fits', 1
REQ_HDR['DARK_FLAT'] = 'pos_pk', 'pos_wl', 'f.fits', 3
REQ_HDR['FLAT_DARK'] = 'pos_wl', 'pos_pk', 'f.fits', 3
REQ_HDR['FLAT_FLAT'] = 'pos_wl', 'pos_wl', 'f.fits', 3
REQ_HDR['FP_FP'] = 'pos_fp', 'pos_fp', 'a.fits', 3
REQ_HDR['HC_HC'] = 'pos_hc1', 'pos_hc1', 'c.fits', 1
# define the header keys to look at (related to values in REQ_HDR)
KEY1 = 'SBCCAS_P'
KEY2 = 'SBCREF_P'


# =============================================================================
# Define functions
# =============================================================================
def valid_night(night_path: Path) -> Tuple[bool, bool, bool, dict]:
    """

    :param night_path: Path

    :return: passed_exist, passed_number and count dictionary
    """

    # deal with engineering
    if SKIP_ENGINEERING:
        obj_files = list(night_path.glob('*o.fits'))
        if len(obj_files) == 0:
            return True, True, True, dict()

    passed_exist = True
    passed_number = True

    count = dict()

    for req_file in REQ_FILES:
        # get extension and number
        ext, num = REQ_FILES[req_file]
        # get files
        files = np.sort(list(night_path.glob('*' + ext)))
        # if use header filter these files by header values
        if USE_HDR:
            files = filter_by_header(files, req_file)
        # get number of files
        numfiles = len(files)

        # deal with files existing
        if numfiles > 0:
            passed_exist = True
            # add to count dictionary
            count[req_file] = [numfiles, num, True]
        else:
            passed_exist = False
            # add to count dictionary
            count[req_file] = [numfiles, num, False]
        # deal with minimum number of files
        if numfiles < num:
            passed_number = False
            # add to count dictionary
            count[req_file] = [numfiles, num, False]
        else:
            passed_number = True
            # add to count dictionary
            count[req_file] = [numfiles, num, True]
    # return passed criteria and count
    return passed_exist, passed_number, False, count


def filter_by_header(files, key):
    # store filtered files
    filtered_files = []
    # loop through files
    for filename in files:
        # try to load file
        try:
            header = fits.getheader(filename)
        except:
            continue
        # if keys not in header skip this file (it is not valid)
        if KEY1 not in header:
            continue
        if KEY2 not in header:
            continue
        # if keys not equal to the required skip this file
        if not header[KEY1] == REQ_HDR[key][0]:
            continue
        if not header[KEY2] == REQ_HDR[key][1]:
            continue
        # add to filtered files
        filtered_files.append(filename)
    # return filtered files
    return filtered_files


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # get a list of night names
    files = np.sort(list(Path(WORKSPACE).glob('*')))
    # only keep directories
    directories = []
    for filename in files:
        if filename.is_dir():
            directories.append(filename)
    # sort directories
    directories = np.sort(directories)
    # storage
    list_valid = []
    list_invalid = []
    list_engineering = []
    # for all directories find those that are valid
    for directory in directories:

        # get validity
        p1, p2, p3, cnt = valid_night(directory)

        # deal with engineering nights
        if p3:
            print('Processing directory: {0}'.format(directory))
            print('\tDirectory is engineering night - skipping')
            list_engineering.append(directory)
        # deal with
        elif not p1:
            # print directory
            print('Processing directory: {0}'.format(directory))
            print('\tDirectory not valid for DRS: {0}'.format(directory))
            for key in cnt:
                if not cnt[key][2]:
                    pargs = [key, cnt[key][0], cnt[key][1]]
                    print('\t\t {0}: not found'.format(*pargs))
            list_invalid.append(directory)
        elif not p2:
            print('Processing directory: {0}'.format(directory))
            print('\tMinimum number of files not met')
            for key in cnt:
                if not cnt[key][2]:
                    pargs = [key, cnt[key][0], cnt[key][1]]
                    print('\t\t {0}: found {1} required {2}'.format(*pargs))
            list_invalid.append(directory)
        else:
            list_valid.append(directory)

# =============================================================================
# End of code
# =============================================================================

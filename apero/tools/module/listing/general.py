#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-09-16 at 14:07

@author: cook
"""
import numpy as np
import os
import copy
from collections import OrderedDict

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.io import drs_fits
from apero.io import drs_path

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_listing.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict


# =============================================================================
# Define functions
# =============================================================================
def get_all_files(params, path):
    # storage of files
    fits_files = []
    # walk through directories
    for root, dirs, files in os.walk(path, followlinks=True):
        # get night name
        ucpath = drs_path.get_uncommon_path(path, root)
        # do not search directories with no files
        if len(files) == 0:
            continue
        # log the night directory
        if ucpath != path:
            WLOG(params, '', TextEntry('40-503-00003', args=[ucpath]))
        # loop around files id dir
        for filename in files:
            if filename.endswith('.fits'):
                # construct absolute path
                abspath = os.path.join(root, filename)
                # append to storage
                fits_files.append(abspath)
    # return fits files
    return np.sort(fits_files)


def get_nightnames(params, path):
    night_names = []
    # walk through directories
    for root, dirs, files in os.walk(path, followlinks=True):
        # do not search directories with no files
        if len(files) == 0:
            continue
        # get night name
        ucpath = drs_path.get_uncommon_path(path, root)
        # append to night names
        night_names.append(ucpath)
    # return night names
    return np.sort(night_names)


def get_outputs(params, files):
    # log progress: Reading headers for indexing
    WLOG(params, 'info', TextEntry('40-504-00003'))
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get output dictionary
    output_hdr_keys = pconst.OUTPUT_FILE_HEADER_KEYS()
    # storage of files
    output_dict = OrderedDict()
    # loop around files
    for it, filename in enumerate(files):
        # get file basename
        basename = os.path.basename(filename)
        # log progress
        wargs = [it + 1, len(files)]
        WLOG(params, '', TextEntry('40-504-00004', args=wargs))
        # add header dict
        output_dict[basename] = dict()
        # deal with some files needing extension 1
        if 's1d' in basename:
            ext = 1
        else:
            ext = 0
        # load header
        header = drs_fits.read_header(params, filename, ext=ext)
        # loop around output keys and add
        for key in output_hdr_keys:
            # deal with header key stores
            if key in params:
                dkey = params[key][0]
            else:
                dkey = str(key)

            if dkey not in header:
                value = '--'
            else:
                value = copy.deepcopy(header[dkey])
            # add to dictionary
            output_dict[basename][key] = value
    # return header key
    return output_dict


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

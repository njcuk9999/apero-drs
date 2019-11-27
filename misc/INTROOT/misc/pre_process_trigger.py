#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_BADPIX_spirou.py [night_directory] [flat_flat_*.fits] [dark_dark_*.fits]

Recipe to generate the bad pixel map

Created on 2017-12-06 at 14:50

@author: cook

Last modified: 2017-12-11 at 15:23

Up-to-date with cal_BADPIX_spirou AT-4 V47
"""
from __future__ import division
import os
import glob

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup

import cal_preprocess_spirou

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'pre_process_trigger.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# ----------------------------------------------------------------------
FORCE_REPROCESS = False


# =============================================================================
# Define functions
# =============================================================================
def main():
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p)

    # ----------------------------------------------------------------------
    # Get all raw files in DRS_DATA_RAW
    # ----------------------------------------------------------------------
    # define search path
    search_path = os.path.join(p['DRS_DATA_RAW'], '**')
    # get all files
    rawfiles = glob.glob(search_path, recursive=True)

    # ----------------------------------------------------------------------
    # Loop around files and identify valid files
    # ----------------------------------------------------------------------
    valid_files = []
    for rawfilename in rawfiles:
        # skip directories
        if os.path.isdir(rawfilename):
            continue
        # get base name and dir name
        basename = os.path.basename(rawfilename)
        directory = os.path.dirname(rawfilename)
        # skip pre-processed files
        if p['PROCESSED_SUFFIX'] in basename:
            continue
        # search for pre-processed file
        if not FORCE_REPROCESS:
            # get odometer name
            odo_name = str(basename).split('_')[0].split('.fits')[0]
            # get directory files
            dir_files = os.listdir(directory)
            # set preprocessed file found flag
            pp_found = False
            # loop around all files in this directory
            for dir_file in dir_files:
                # check if preprocessed suffix in file
                cond1 = p['PROCESSED_SUFFIX'] in dir_file
                # check that odometer name in file
                cond2 = odo_name in dir_file
                # if both of these are found we have found a preprocessed file
                #    for this rawfilename
                if cond1 and cond2:
                    pp_found = True
            # if we have found a preprocessed file then do not add to
            #    valid files
            if pp_found:
                continue
            else:
                valid_files.append(rawfilename)
        # finally if nothing else add to valid_files
        else:
            valid_files.append(rawfilename)

    # ----------------------------------------------------------------------
    # Run pre-processing
    # ----------------------------------------------------------------------
    # get number of valid files
    number_files = len(valid_files)

    if number_files == 0:
        WLOG(p, 'warning', 'All files up-to-date.')

    # loop around valid files
    for v_it, valid_file in enumerate(valid_files):
        # get base name and dir name
        basename = os.path.basename(valid_file)
        directory = os.path.dirname(valid_file)
        # get night_name
        night_name = directory.split(p['DRS_DATA_RAW'])[-1][len(os.path.sep):]
        # print progress
        WLOG('', '', '')
        WLOG('', '', '=' * 50)
        wmsg = 'Processing file {0} of {1}'.format(v_it + 1, number_files)
        WLOG(p, '', wmsg)
        WLOG('', '', '=' * 50)
        WLOG('', '', '')
        # run pre-processing
        _ = cal_preprocess_spirou.main(night_name, basename)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG(p, 'info', wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================

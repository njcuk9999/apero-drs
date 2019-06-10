#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_FF_RAW_spirou.py [night_directory] [files]

Flat Field

Created on 2017-11-06 11:32

@author: cook

Last modified: 2017-12-11 at 15:11

Up-to-date with cal_FF_RAW_spirou AT-4 V47
"""
from __future__ import division
import os

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

import cal_extract_RAW_spirou

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_thermal_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
__args__ = ['night_name', 'files']
__required__ = [True, True]
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    """
    cal_FF_RAW_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_FF_RAW_spirou.py [night_directory] [files]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p)
    # ----------------------------------------------------------------------
    # get the e2ds filenames (uses ARG_FILE_NAMES by default)
    exists = False
    e2ds_files, e2dsff_files = dict(), dict()
    for fiber in p['FIBER_TYPES']:
        # must set file type
        p['FIBER'] = fiber
        p.set_source('FIBER', __NAME__ + '.main()')
        # construct this fibers file names
        e2dsfits, tag1 = spirouConfig.Constants.EXTRACT_E2DS_FILE(p)
        e2dsfffits, tag2 = spirouConfig.Constants.EXTRACT_E2DSFF_FILE(p)
        # check whether e2ds file exists
        if os.path.exists(e2dsfits):
            exists = exists and True
        else:
            exists = exists and False
        # append to files
        e2ds_files[fiber] = e2dsfits
        e2dsff_files[fiber] = e2dsfffits
    # ----------------------------------------------------------------------
    # extract the dark or read dark e2ds header
    # ----------------------------------------------------------------------
    # check if e2ds file exists - if not extract
    if p['ALWAYS_EXTRACT'] or (not exists):
        llout = cal_extract_RAW_spirou.main(night_name, files)
        # get qc
        passed = llout['p']['QC']
        # get hdr
        hdr = llout['hdr']

    # else we need to get
    else:
        # read file header and push into outputs
        hdr = spirouImage.ReadHeader(p, e2ds_files['AB'])
        # get quality control parameters
        passed = hdr['KW_DRS_QC']

    # ------------------------------------------------------------------
    # Update the calibration database
    # ------------------------------------------------------------------
    for fiber in p['FIBER_TYPES']:
        if passed:
            # copy THERMAL_{FIBER} to calibdb
            keydb = 'THERMAL_' + fiber
            # get absolute path
            abspath = e2ds_files[fiber]
            basename = os.path.basename(abspath)
            # copy localisation file to the calibDB folder
            spirouDB.PutCalibFile(p, abspath)
            # update the master calib DB file with new key
            spirouDB.UpdateCalibMaster(p, keydb, basename, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================

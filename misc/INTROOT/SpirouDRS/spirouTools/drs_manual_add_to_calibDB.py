#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_manual_add_to_calibDB.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, key=None, filename=None):
    """
    Manually add a file the the calibDB with "key"

    i.e. adds

    key night_name filename human-date unix-time

    to the calibDB and copies "filename" from .../reduced_dir/night_name/ into
    the calibDB

    Note filename must be in .../reduced_dir/night_name/
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1]
    fmt = [str, str]
    names = ['key', 'filename']
    call = [key, filename]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(p, pos, fmt, names,
                                                    calls=call)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='filename',
                                    mainfitsdir='reduced')
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    image, hdr, nbo, nx = spirouImage.ReadData(p, p['FITSFILENAME'])

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    # set dark key
    keydb = p['KEY']
    # copy dark fits file to the calibDB folder
    spirouDB.PutCalibFile(p, p['FITSFILENAME'])
    # update the master calib DB file with new key
    spirouDB.UpdateCalibMaster(p, keydb, p['FILENAME'], hdr)

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
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-01 at 11:21

@author: cook
"""
from __future__ import division
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'edit_header.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# set the value to change
HEADER_KEY = ['DRSOUTID', '', 'DRS output identification code']
HEADER_VALUE = 'OBJ_FP'


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, reffile=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with reference file being None (i.e. get from sys.argv)
    if reffile is None:
        customargs = spirouStartup.GetCustomFromRuntime(p, [0], [str],
                                                        ['reffile'])
    else:
        customargs = dict(reffile=reffile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='reffile',
                                    mainfitsdir='reduced')
    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, reffilename = spirouStartup.SingleFileSetup(p, filename=p['REFFILE'],
                                                   skipcheck=True)
    p['REFFILENAME'] = reffilename
    p.set_source('REFFILENAME', __NAME__ + '.main()')
    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, nbo, nx = spirouImage.ReadData(p, p['REFFILENAME'])
    # ----------------------------------------------------------------------
    # Add keys and save file
    # ----------------------------------------------------------------------
    newfilename = p['REFFILE'].replace('.fits', '_edit.fits')
    newpath = os.path.join(p['ARG_FILE_DIR'], newfilename)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    # set the version
    hdict = spirouImage.AddKey(p, hdict, HEADER_KEY, value=HEADER_VALUE)
    # log saving
    wmsg = 'Writing file {0} to {1}'
    WLOG(p, '', wmsg.format(newfilename, p['ARG_FILE_DIR']))
    # save drift values
    p = spirouImage.WriteImage(p, newpath, data, hdict)
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

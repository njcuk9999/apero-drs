#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_preprocess_spirou [night_name] [files]

Rotation of the H4RG fits files

Created on 2018-04-13 at 17:20

@author: melissa-hobson
"""

# {IMPORTS}
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouImage


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_preprocess_spirou.py'
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
def main(night_name=None, files=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p)

    # log processing image type
    p['dprtype'] = spirouImage.GetTypeFromHeader(p, p['kw_DPRTYPE'])
    p.set_source('dprtype', __NAME__ + '/main()')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['log_opt'], wmsg.format(p['dprtype'], p['program']))

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    rout = spirouImage.ReadImageAndCombine(p, framemath='average')
    data, hdr, cdr, nx, ny = rout

    # ----------------------------------------------------------------------
    # Rotate image
    # ----------------------------------------------------------------------
    data = np.rot90(data, -1)

    # ----------------------------------------------------------------------
    # Save rotated image
    # ----------------------------------------------------------------------
    # construct rotated file name
    fitsfile = spirouConfig.Constants.FITSFILENAME(p)
    rotatefits = fitsfile.replace('.fits', '_rot.fits')
    rotatefitsname = os.path.split(rotatefits)[-1]
    # log that we are saving rotated image
    WLOG('', p['log_opt'], 'Saving Rotated Image in ' + rotatefitsname)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # write to file
    spirouImage.WriteImage(rotatefits, data, hdict)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))
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

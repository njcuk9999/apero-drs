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
from SpirouDRS.spirouCore import spirouFile

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


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, ufile=None, xsize=None, ysize=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # need custom args (to accept full path or wild card
    if ufile is None or xsize is None or ysize is None:
        pos = [0, 1, 2]
        names, types = ['ufile', 'xsize', 'ysize'], [str, int, int]
        customargs = spirouStartup.GetCustomFromRuntime(pos, types, names,
                                                        last_multi=True)
    else:
        customargs = dict(ufile=ufile, xsize=xsize, ysize=ysize)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs)
    # add constants not currently in constants file

    # ------------------------------------------------------------------
    # Read image file
    # ------------------------------------------------------------------
    # read the image data
    rout = spirouImage.ReadImage(p, filename=p['ufile'])
    image, hdr, cdr, nx, ny = rout

    # ----------------------------------------------------------------------
    # un-Resize image
    # ----------------------------------------------------------------------
    # create an array of given size
    size = np.product([p['ysize'], p['xsize']])

    newimage = np.repeat(np.nan, size).reshape(p['ysize'], p['xsize'])

    # insert image at given pixels
    xlow, xhigh = p['IC_CCDX_LOW'], p['IC_CCDX_HIGH']
    ylow, yhigh = p['IC_CCDY_LOW'], p['IC_CCDY_HIGH']
    newimage[ylow:yhigh, xlow:xhigh] = image

    # rotate the image
    newimage = spirouImage.FlipImage(newimage)

    # ------------------------------------------------------------------
    # Save rotated image
    # ------------------------------------------------------------------
    # construct rotated file name
    outfits = ufile.replace('.fits', '_old.fits')
    outfitsname = os.path.split(outfits)[-1]
    # log that we are saving rotated image
    WLOG('', p['log_opt'], 'Saving Rotated Image in ' + outfitsname)
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # write to file
    spirouImage.WriteImage(outfits, newimage, hdict)

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
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================

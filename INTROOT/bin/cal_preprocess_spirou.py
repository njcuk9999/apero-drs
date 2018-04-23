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
# Get Path Exception
PathException = spirouFile.PathException
# ----------------------------------------------------------------------------
# constants for constants file
# TODO Constants need moving to constants_SPIROU.py
PROCESSED_SUFFIX = '_pp'
NUMBER_DARK_AMP = 5
NUMBER_REF_TOP = 4
NUMBER_REF_BOTTOM = 4
TOTAL_AMP_NUM = 32
DARK_MED_BINNUM = 32


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, ufiles=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # need custom args (to accept full path or wild card
    if ufiles is None:
        names, types = ['ufiles'], [str]
        customargs = spirouStartup.GetCustomFromRuntime([0], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(ufiles=ufiles)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs)
    # add constants not currently in constants file
    # TODO Constants need moving to constants_SPIROU.py
    p['PROCESSED_SUFFIX'] = PROCESSED_SUFFIX
    p['NUMBER_DARK_AMP'] = NUMBER_DARK_AMP
    p['NUMBER_REF_TOP'] = NUMBER_REF_TOP
    p['NUMBER_REF_BOTTOM'] = NUMBER_REF_BOTTOM
    p['TOTAL_AMP_NUM'] = TOTAL_AMP_NUM
    p['DARK_MED_BINNUM'] = DARK_MED_BINNUM


    # ----------------------------------------------------------------------
    # Process files (including wildcards)
    # ----------------------------------------------------------------------
    # get raw folder (assume all files are in the root directory)
    rawdir = spirouConfig.Constants.RAW_DIR(p)
    try:
        ufiles = spirouFile.Paths(p['ufiles'], root=rawdir).abs_paths
    except PathException as e:
        WLOG('error', p['log_opt'], e)

    # log how many files were found
    wmsg = '{0} files found'
    WLOG('', p['log_opt'], wmsg.format(len(ufiles)))

    # loop around files
    for ufile in ufiles:
        # ------------------------------------------------------------------
        # Check that we can process file
        # ------------------------------------------------------------------
        # check if ufile exists
        if not os.path.exists(ufile):
            wmsg = 'File {0} does not exist... skipping'
            WLOG('warning', p['log_opt'], wmsg.format(ufile))
            continue
        elif p['PROCESSED_SUFFIX'] + '.fits' in ufile:
            wmsg = 'File {0} has been processed... skipping'
            WLOG('warning', p['log_opt'], wmsg.format(ufile))
            continue
        elif '.fits' not in ufile:
            wmsg = 'File {0} not a fits file... skipping'
            WLOG('warning', p['log_opt'], wmsg.format(ufile))
            continue

        # log the file process
        wmsg = 'Processing file {0}'
        WLOG('', p['log_opt'], wmsg.format(ufile))

        # ------------------------------------------------------------------
        # Read image file
        # ------------------------------------------------------------------
        # read the image data
        rout = spirouImage.ReadImage(p, filename=ufile)
        image, hdr, cdr, nx, ny = rout



        # ------------------------------------------------------------------
        # correct image
        # ------------------------------------------------------------------
        # TODO: Eventually remove H2RG fix
        # do not correct for H2RG
        if p['IC_IMAGE_TYPE'] == 'H2RG':
            pass
        else:
            # correct for the top and bottom reference pixels
            WLOG('', p['log_opt'], 'Correcting for top and bottom pixels')
            image = spirouImage.PPCorrectTopBottom(p, image)

            # correct by a median filter from the dark amplifiers
            wmsg = 'Correcting by the median filter from dark amplifiers'
            WLOG('', p['log_opt'], wmsg)
            image = spirouImage.PPMedianFilterDarkAmps(p, image)

            # correct for the 1/f noise
            wmsg = 'Correcting for the 1/f noise'
            WLOG('', p['log_opt'], wmsg)
            image = spirouImage.PPMedianOneOverfNoise(p, image)

        # ------------------------------------------------------------------
        # rotate image
        # ------------------------------------------------------------------
        # TODO: Eventually remove H2RG fix
        # do not rotate for H2RG
        if p['IC_IMAGE_TYPE'] == 'H2RG':
            pass
        else:
            # rotation to match HARPS orientation (expected by DRS)
            image = np.rot90(image, -1)

        # ------------------------------------------------------------------
        # Save rotated image
        # ------------------------------------------------------------------
        # construct rotated file name
        outfits = ufile.replace('.fits', p['PROCESSED_SUFFIX'] + '.fits')
        outfitsname = os.path.split(outfits)[-1]
        # log that we are saving rotated image
        WLOG('', p['log_opt'], 'Saving Rotated Image in ' + outfitsname)
        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
        # write to file
        spirouImage.WriteImage(outfits, image, hdict)

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-02-07 at 17:20

@author: cook
"""
import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'check_for_corrupt_files.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict

EXTS = ['a.fits', 'c.fits', 'd.fits', 'f.fits', 'o.fits']


# =============================================================================
# Define functions
# =============================================================================
def get_full_flat(p):
    # get parameters from p
    filename = p['BADPIX_FULL_FLAT']
    threshold = p['BADPIX_FULL_THRESHOLD']
    # construct filepath
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.BADPIX_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    absfilename = os.path.join(datadir, filename)
    # check that filepath exists
    if not os.path.exists(absfilename):
        emsg = 'badpix full flat ({0}) not found in {1}. Please correct.'
        WLOG(p, 'error', emsg.format(filename, datadir))
    # read image
    mdata, _, _, _, _ = spirouImage.ReadImage(p, absfilename, kind='FULLFLAT')
    # return image
    return mdata


def get_full_flat_hotpix(p):
    # get full badpixel file
    full_badpix = get_full_flat(p)
    # get shape of full badpixel file
    dim1, dim2 = full_badpix.shape

    # get the med_size
    med_size = p['PP_CORRUPT_MED_SIZE']
    # get the hot pix threshold
    hot_thres = p['PP_CORRUPT_HOT_THRES']

    # get size of dark region
    pixels_per_amp = dim2 // p['TOTAL_AMP_NUM']
    dark_size = p['NUMBER_DARK_AMP'] * pixels_per_amp

    # mask the full_badpix (do not include dark area or edges)
    full_badpix[:, dark_size] = 0.0
    full_badpix[:med_size, :] = 0.0
    full_badpix[:, :med_size] = 0.0
    full_badpix[-med_size:, :] = 0.0
    full_badpix[:, -med_size:] = 0.0

    # locate hot pixels in the full bad pix
    yhot, xhot = np.where(full_badpix > hot_thres)

    # return the hot pixel indices
    return yhot, xhot


def get_all_fits_files(p, path):
    fitsfiles = []
    # walk through all sub-directories
    for root, dirs, files in os.walk(path):
        # loop around files in each sub-directory
        for filename in files:
            # check if file has valid extension
            valid = False
            for ext in EXTS:
                if filename.endswith(ext) :
                    valid = True
            if not valid:
                continue
            else:
                fitsfiles.append(os.path.join(root, filename))
    # log found files
    WLOG(p, '', 'Found {0} valid fits files'.format(len(fitsfiles)))

    # return list of files
    return fitsfiles


def find_hotpix_offset(p, filename, yhot, xhot):
    # get the med_size
    med_size = p['PP_CORRUPT_MED_SIZE']
    # get data
    data, _, _, _, _ = spirouImage.ReadImage(p, filename, kind='None',                                       log=False)
    # get median hot pixel box
    med_hotpix = np.zeros([2 * med_size + 1, 2 * med_size + 1])
    # loop around x
    for dx in range(-med_size, med_size + 1):
        # loop around y
        for dy in range(-med_size, med_size + 1):
            # define position in median box
            posx = dx + med_size
            posy = dy + med_size
            # get the hot pixel values at position in median box
            data_hot = data[yhot + dx, xhot + dy]
            # median the data_hot for this box position
            med_hotpix[posx, posy] = np.nanmedian(data_hot)
    # work out an rms
    rms = np.median(np.abs(med_hotpix - np.median(med_hotpix)))
    # return rms
    return rms


if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, None, require_night_name=None)

    # ----------------------------------------------------------------------
    # define constants for constants file
    # ----------------------------------------------------------------------
    # Defines the size around badpixels that is considered part of the bad pixel
    p['PP_CORRUPT_MED_SIZE'] = 2
    # Defines the threshold (above the full engineering flat) that selects bad
    # (hot) pixels
    p['PP_CORRUPT_HOT_THRES'] = 2

    # ----------------------------------------------------------------------
    # get the x and y locations of the hot pixels
    yhot, xhot = get_full_flat_hotpix(p)
    # ----------------------------------------------------------------------
    # get the file list
    filelist = get_all_fits_files(p, p['DRS_DATA_RAW'])
    # ----------------------------------------------------------------------
    # store rms values
    rms_array = []
    # loop around files and save RMS value
    for it, filename in enumerate(filelist):
        # print progress
        wmsg = 'Analysising file {0} of {1}'.format(it + 1, len(filelist))
        WLOG(p, '', wmsg)
        # get the rms
        rms = find_hotpix_offset(p, filename, yhot, xhot)
        # add to array
        rms_array.append(rms)

    # make rms_array a numpy array
    rms_array = np.array(rms_array)




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

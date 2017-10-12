#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readwrite.py

read and writing functions

Created on 2017-10-12 at 15:32

@author: cook



Version 0.0.0
"""

from astropy.io import fits
import os
import sys

from startup import log


# =============================================================================
# Define variables
# =============================================================================
WLOG = log.logger
# -----------------------------------------------------------------------------

# =============================================================================
# Define user functions
# =============================================================================
def readimage(p, add=True):
    # set up frequently used variables
    fitsfilename = p['fitsfilename']
    log_opt = p['log_opt']
    nbframes = len(p['arg_file_names'])
    # log that we are reading the image
    WLOG('', log_opt, 'Reading Image ' + fitsfilename)
    # read data from fits file
    data, header, nx, ny = read_raw_data(fitsfilename)
    # log that we have loaded the image
    WLOG('', log_opt, 'Image {0} x {1} loaded'.format(nx, ny))

    # if we have more than one frame and add is True then add the rest of the
    #    frames
    if (nbframes > 1) and add:
        # log that we are adding frames
        WLOG('info', log_opt, 'Adding frames')
        # loop around each frame
        for f_it in range(1, nbframes):
            # construct frame file name
            framefilename = os.path.join(p['DRS_DATA_RAW'], p['arg_night_name'],
                                         p['arg_file_names'][f_it])
            # check whether frame file name exists, log and exit if not
            if not os.path.exists(framefilename):
                WLOG('error', log_opt, ('File: {0} does not exist'
                                        ''.format(framefilename)))
                sys.exit(1)
            else:
                # load that we are reading this file
                WLOG('', log_opt, 'Reading File: ' + framefilename)
                # finally add data
                data = data + read_raw_data(framefilename, False, False)
    # return data, header, data.shape[0], data.shape[1]
    return data, header, nx, ny


# =============================================================================
# Define pyfits functions
# =============================================================================
def read_raw_data(filename, getheader=True, getshape=True):
    # get the data
    data = fits.getdata(filename)
    # get the header if "getheader" and "getshape" are True
    if getheader:
        header = fits.getheader(filename)
    # return based on whether header and shape
    if getheader and getshape:
        return data, header, data.shape[0], data.shape[1]
    elif getheader:
        return data, header
    elif getshape:
        return data, data.shape[0], data.shape[1]
    else:
        return data

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 17:47

@author: cook



Version 0.0.0
"""

import numpy as np
import sys
import os

from startup import log
from startup import spirouCDB
from . import spirouFITS

# =============================================================================
# Define variables
# =============================================================================
WLOG = log.logger
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def resize(image, x=None, y=None, xlow=0, xhigh=None, ylow=0, yhigh=None,
           getshape=True):
    """
    Resize an image based on a pixel values

    :param image: numpy array (2D), the image
    :param x: None or numpy array (1D), the list of x pixels
    :param y: None or numpy array (1D), the list of y pixels
    :param xlow: int, x pixel value (x, y) in the bottom left corner,
                 default = 0
    :param xhigh:  int, x pixel value (x, y) in the top right corner,
                 if None default is image.shape(1)
    :param ylow: int, y pixel value (x, y) in the bottom left corner,
                 default = 0
    :param yhigh: int, y pixel value (x, y) in the top right corner,
                 if None default is image.shape(0)
    :param getshape: bool, if True returns shape of newimage with newimage

    if getshape = True
    :return newimage: numpy array (2D), the new resized image
    :return nx: int, the shape in the first dimension, i.e. data.shape[0]
    :return ny: int, the shape in the second dimension, i.e. data.shape[1]

    if getshape = False
    :return newimage: numpy array (2D), the new resized image
    """
    # Deal with no low/high values
    if xhigh is None:
        xhigh = image.shape(1)
    if yhigh is None:
        yhigh = image.shape(0)
    # if our x pixels and y pixels to keep are defined then use them to
    # construct the new image
    if x is not None and y is not None:
        pass
    # else define them from low/high values
    else:
        # deal with xlow > xhigh
        if xlow > xhigh:
            x = np.arange(xhigh + 1, xlow + 1)[::-1]
        elif xlow == xhigh:
            emsg = '"xlow" and "xhigh" cannot have the same values'
            WLOG('error', '', emsg)
            sys.exit(1)
        else:
            x = np.arange(xlow, xhigh)
        # deal with ylow > yhigh
        if ylow > yhigh:
            y = np.arange(yhigh + 1, ylow + 1)[::-1]
        elif ylow == yhigh:
            emsg = '"ylow" and "yhigh" cannot have the same values'
            WLOG('error', '', emsg)
            sys.exit(1)
        else:
            y = np.arange(ylow, yhigh)
    # construct the new image
    newimage = np.take(np.take(image, x, axis=1), y, axis=0)
    # if getshape is True return newimage, newimage.shape[0], newimage.shape[1]
    if getshape:
        return newimage, newimage.shape[0], newimage.shape[1]
    else:
        # return new image
        return newimage


def correct_for_dark(p, image, header):
    """
    Corrects "data" for "dark" using calibDB file (header must contain
        value of p['ACQTIME_KEY'] as a keyword

    :param p: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :param header: dictionary, the header dictionary created by
                   spirouFITS.ReadImage

    :return corrected_image: numpy array (2D), the dark corrected image
    """

    # key acqtime_key from parameter dictionary
    if 'ACQTIME_KEY' not in p:
        WLOG('error', p['log_opt'], ('Error ACQTIME_KEY not defined in'
                                     ' config files'))
        sys.exit(1)
    else:
        acqtime_key = p['ACQTIME_KEY']

    # get max_time from file
    if acqtime_key not in header:
        eargs = [acqtime_key, p['arg_file_names'][0]]
        WLOG('error', p['log_opt'], ('Key {0} not in HEADER file of {1}'
                                     ''.format(*eargs)))
        sys.exit(1)
    else:
        acqtime = header[acqtime_key]

    # get calibDB
    cdb = spirouCDB.get_database(p, acqtime)

    # try to read 'DARK' from cdb
    if 'DARK' in cdb:
        darkfile = os.path.join(p['DRS_CALIB_DB'], cdb['DARK'][1])
        WLOG('', p['log_opt'], 'Doing Dark Correction using ' + darkfile)
        darkimage, nx, ny = spirouFITS.read_raw_data(darkfile, False, True)
        corrected_image = image - (darkimage * p['nbframes'])
    else:
        masterfile = os.path.join(p['DRS_CALIB_DB'], p['IC_CALIBDB_FILENAME'])
        emsg = 'No valid DARK in calibDB {0} ( with unix time <={1})'
        WLOG('error', p['log_opt'], emsg.format(masterfile, acqtime))
        sys.exit(1)

    # finally return datac
    return corrected_image



# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-27 at 10:48

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.io import drs_image
from . import dark
from . import badpix
from . import background


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.general.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
PConstants = constants.pload(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def calibrate_ppfile(params, recipe, infile, **kwargs):

    func_name = __NAME__ + '.calibrate_file()'
    # deal with inputs (either from params or kwargs)
    image = kwargs.get('image', None)
    header = kwargs.get('header', None)
    correctdark = kwargs.get('correctdark', True)
    flip = pcheck(params, 'INPUT_FLIP_IMAGE', 'flip', kwargs, func_name)
    converte = kwargs.get('converte', True)
    resize = pcheck(params, 'INPUT_RESIZE_IMAGE', 'resize', kwargs, func_name)
    correctbad = kwargs.get('correctbad', True)
    correctback = kwargs.get('correctback', True)
    cleanhotpix = kwargs.get('cleanhotpix', True)
    n_percentile = kwargs.get('n_percentile', None)

    # get image and header
    if image is None:
        image = np.array(infile.data)
    if header is None:
        header = infile.header
    # Get basic image properties
    sigdet = infile.get_key('KW_RDNOISE')
    exptime = infile.get_key('KW_EXPTIOME')
    gain = infile.get_key('KW_GAIN')
    dprtype = infile.get_key('KW_DPRTYPE', dtype=str)

    # ----------------------------------------------------------------------
    # image 1 is corrected for dark
    # ----------------------------------------------------------------------
    if correctdark:
        darkfile, image1 = dark.correction(params, image, header)
    else:
        image1 = np.array(image)
        darkfile = 'None'
    # ----------------------------------------------------------------------
    # flip image
    # ----------------------------------------------------------------------
    if flip:
        image2 = drs_image.flip_image(params, image1)
    else:
        image2 = np.array(image1)
    # ----------------------------------------------------------------------
    # convert ADU/s to electrons
    # ----------------------------------------------------------------------
    if converte:
        image2 = drs_image.convert_to_e(params, image2, gain=gain,
                                        exptime=exptime)
    # ----------------------------------------------------------------------
    # image 2 is resized (if required)
    # ----------------------------------------------------------------------
    if resize:
        # get resize size
        sargs = dict(xlow=params['IMAGE_X_LOW'], xhigh=params['IMAGE_X_HIGH'],
                     ylow=params['IMAGE_Y_LOW'], yhigh=params['IMAGE_Y_HIGH'])
        # resize flat
        image2 = drs_image.resize(params, image2, **sargs)
    # ----------------------------------------------------------------------
    # image 3 is corrected for bad pixels
    # ----------------------------------------------------------------------
    if correctbad:
        badpfile, image3 = badpix.correction(params, image2, header)
    else:
        image3 = np.array(image2)
        badpfile = 'None'
    # ----------------------------------------------------------------------
    # image 4 is corrected for background
    # ----------------------------------------------------------------------
    if correctback:
        bkgrdfile, image4 = background.correction(recipe, params, infile,
                                                 image3, header)
    else:
        image4 = np.array(image3)
        bkgrdfile = 'None'
    # ----------------------------------------------------------------------
    # image 4 may need to normalise by a percentile
    # ----------------------------------------------------------------------
    if n_percentile is not None:
        image4 = image4 / np.nanpercentile(image4, n_percentile)

    # ----------------------------------------------------------------------
    # image 5 is cleaned from hot pixels
    # ----------------------------------------------------------------------
    if cleanhotpix:
        _, badpixmask = badpix.correction(params, header=header,
                                          return_map=True)
        image5 = drs_image.clean_hotpix(image4, badpixmask)
    else:
        image5 = np.array(image4)

    # ----------------------------------------------------------------------
    # make properties dictionary
    # ----------------------------------------------------------------------
    props = ParamDict()
    # get basic properties
    props['FILENAME'] = infile.filename
    props['BASENAME'] = infile.basename
    props['SIGDET'] = sigdet
    props['EXPTIME'] = exptime
    props['GAIN'] = gain
    props['DPRTYPE'] = dprtype
    # get
    props['SHAPE'] = image5.shape
    props['DARKFILE'] = darkfile
    props['BADPFILE'] = badpfile
    props['BACKFILE'] = bkgrdfile
    props['FLIPPED'] = flip
    props['CONVERT_E'] = converte
    props['RESIZED'] = resize
    if n_percentile is None:
        props['NORMALISED'] = False
    else:
        props['NORMALISED'] = n_percentile
    props['CLEANED'] = cleanhotpix
    # set source
    keys = ['FILENAME', 'BASENAME', 'SIGDET', 'EXPTIME', 'GAIN', 'DPRTYPE',
            'SHAPE', 'DARKFILE', 'BADPFILE', 'BACKFILE', 'FLIPPED',
            'CONVERT_E', 'RESIZED', 'NORMALISED', 'CLEANED']
    props.set_sources(keys, func_name)

    # ----------------------------------------------------------------------
    # return image 5
    return props, image5


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

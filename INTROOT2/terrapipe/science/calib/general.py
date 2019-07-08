#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General calibration functions in here only

Created on 2019-06-27 at 10:48

@author: cook
"""
from __future__ import division
import numpy as np
import os

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.io import drs_fits
from terrapipe.io import drs_image
from terrapipe.io import drs_table
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
    exptime = infile.get_key('KW_EXPTIME')
    gain = infile.get_key('KW_GAIN')
    dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
    nfiles = infile.numfiles

    # log that we are calibrating a file
    WLOG(params, 'info', TextEntry('40-014-00038', args=[infile.filename]))

    # ----------------------------------------------------------------------
    # image 1 is corrected for dark
    # ----------------------------------------------------------------------
    if correctdark:
        darkfile, image1 = dark.correction(params, image, header, nfiles=nfiles)
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
        # print that image has been resize
        wargs = [dprtype, image1.shape, image2.shape]
        WLOG(params, '', TextEntry('40-014-00013', args=wargs))

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
        # log that we are normalising
        WLOG(params, '', TextEntry('40-014-00014', args=[n_percentile]))
        # normalise by nanpercentile
        image4 = image4 / np.nanpercentile(image4, n_percentile)

    # ----------------------------------------------------------------------
    # image 5 is cleaned from hot pixels
    # ----------------------------------------------------------------------
    if cleanhotpix:
        # log progress
        WLOG(params, '', TextEntry('40-014-00012'))
        # get bad pixel mask
        _, badpixmask = badpix.correction(params, header=header,
                                          return_map=True)
        # clean hot pixels
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


def add_calibs_to_header(outfile, props):

    # define property keys (must be in calibrate_ppfile function)
    propkeys = ['DARKFILE', 'BADPFILE', 'BACKFILE', 'FLIPPED', 'CONVERT_E',
                'RESIZED']
    # define the header keywords to use for each
    headerkeys = ['KW_CDBDARK', 'KW_CDBBAD', 'KW_CDBBACK', 'KW_C_FLIP',
                  'KW_C_CVRTE', 'KW_C_RESIZE']

    # loop around property keys
    for it in range(len(propkeys)):
        # get header key
        hkey = headerkeys[it]
        # get property key
        pkey = propkeys[it]
        # add header key
        if pkey in props:
            outfile.add_hkey(hkey, value=str(props[pkey]))
    # return outfile
    return outfile


def load_calib_file(params, key, header, **kwargs):
    func_name = kwargs.get('func', __NAME__ + '.load_calib_file()')

    # get keys from kwargs
    n_entries = kwargs.get('n_entries', 1)
    ext = kwargs.get('ext', 0)
    # ----------------------------------------------------------------------
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')
    # get filename col
    filecol = cdb.file_col
    # get the badpix entries
    entries = drs_database.get_key_from_db(params, key, cdb, header,
                                           n_ent=n_entries)
    # storage
    images, abspaths = [], []
    # loop around entries
    for entry in entries:
        # get badpix filename
        filename = entries[filecol][0]
        abspath = os.path.join(params['DRS_CALIB_DB'], filename)
        # ------------------------------------------------------------------
        # get calib fits file
        image = drs_fits.read(params, abspath, ext=ext)
        # ------------------------------------------------------------------
        # append to storage
        images.append(image)
        abspaths.append(abspath)

    # deal with if n_entries is 1 (just return file not list)
    if n_entries == 1:
        return images[0], abspaths[0]
    else:
        return images, abspaths


def load_calib_table(params, key, header, **kwargs):
    # get keys from kwargs
    n_entries = kwargs.get('n_entries', 1)
    fmt = kwargs.get('fmt', 'fits')
    # ----------------------------------------------------------------------
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')
    # get filename col
    filecol = cdb.file_col
    # get the badpix entries
    entries = drs_database.get_key_from_db(params, key, cdb, header,
                                           n_ent=n_entries)
    # storage
    images, abspaths = [], []
    # loop around entries
    for entry in entries:
        # get badpix filename
        filename = entries[filecol][0]
        abspath = os.path.join(params['DRS_CALIB_DB'], filename)
        # ------------------------------------------------------------------
        # get calib fits file
        image = drs_table.read_table(params, abspath, fmt=fmt)
        # ------------------------------------------------------------------
        # append to storage
        images.append(image)
        abspaths.append(abspath)

    # deal with if n_entries is 1 (just return file not list)
    if n_entries == 1:
        return images[0], abspaths[0]
    else:
        return images, abspaths



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

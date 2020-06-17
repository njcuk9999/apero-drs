#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General calibration functions in here only

Created on 2019-06-27 at 10:48

@author: cook
"""
import numpy as np
import os
import warnings

from apero import core
from apero import lang
from apero.core import constants
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.io import drs_image
from apero.science.calib import dark
from apero.science.calib import badpix
from apero.science.calib import background


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.general.py'
__INSTRUMENT__ = 'None'
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
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define user functions
# =============================================================================
def check_files(params, infile):
    # get infile DPRTYPE and OBJNAME
    dprtype = infile.get_key('KW_DPRTYPE', dtype=str, required=False)
    objname = infile.get_key('KW_OBJNAME', dtype=str, required=False)
    filename = infile.filename
    # deal with unset value
    if dprtype is None:
        dprtype = 'None'
    if objname is None:
        objname = 'None'
    # clean (capitalize and remove white spaces)
    dprtype = clean_strings(dprtype)
    objname = clean_strings(objname)
    # get inputs
    objname_inputs = params['INPUTS']['OBJNAME'].split(',')
    dprtype_inputs = params['INPUTS']['DPRTYPE'].split(',')
    # clean (capitalize and remove white spaces)
    objname_inputs = clean_strings(objname_inputs)
    dprtype_inputs = clean_strings(dprtype_inputs)
    # ----------------------------------------------------------------------
    # storage of outputs
    skip = False
    skip_conditions = [[], [], []]
    # ----------------------------------------------------------------------
    # deal with objname filter
    if 'NONE' in objname_inputs:
        skip = skip or False
    # else check for objname in
    elif objname in objname_inputs:
        skip = skip or False
    # else we skip
    else:
        skip = skip or True
        skip_conditions[0].append('OBJNAME')
        skip_conditions[2] = [objname, ' or '.join(objname_inputs), filename]
    # ----------------------------------------------------------------------
    # deal with objname filter
    if 'NONE' in dprtype_inputs:
        skip = skip or False
    # else check for objname in
    elif dprtype in dprtype_inputs:
        skip = skip or False
    # else we skip
    else:
        skip = skip or True
        skip_conditions[0].append('DPRTYPE')
        skip_conditions[1] = [dprtype, ' or '.join(dprtype_inputs), filename]
    # ----------------------------------------------------------------------
    # return the skip and conditions
    return skip, skip_conditions


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
    darkfile = kwargs.get('darkfile', None)
    badpixfile = kwargs.get('badpixfile', None)
    backfile = kwargs.get('backfile', None)

    # get image and header
    if image is None:
        image = np.array(infile.data)
    if header is None:
        header = infile.header

    # -------------------------------------------------------------------------
    # get loco file instance
    darkinst = core.get_file_definition('DARKM', params['INSTRUMENT'],
                                        kind='red')
    badinst = core.get_file_definition('BADPIX', params['INSTRUMENT'],
                                        kind='red')
    backinst = core.get_file_definition('BKGRD_MAP', params['INSTRUMENT'],
                                        kind='red')

    # get calibration key
    darkkey = darkinst.get_dbkey(func=func_name)
    badkey = badinst.get_dbkey(func=func_name)
    backkey = backinst.get_dbkey(func=func_name)

    # get user input arguments
    darkfile = get_input_files(params, 'DARKFILE', darkkey, header, darkfile)
    badpixfile = get_input_files(params, 'BADPIXFILE', badkey, header,
                                 badpixfile)
    backfile = get_input_files(params, 'BACKFILE', backkey, header, backfile)

    # Get basic image properties
    sigdet = infile.get_key('KW_RDNOISE')
    exptime = infile.get_key('KW_EXPTIME')
    gain = infile.get_key('KW_GAIN')
    dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
    saturate = infile.get_key('KW_SATURATE', dtype=float)
    frmtime = infile.get_key('KW_FRMTIME', dtype=float)
    nfiles = infile.numfiles

    # log that we are calibrating a file
    WLOG(params, 'info', TextEntry('40-014-00038', args=[infile.filename]))

    # ----------------------------------------------------------------------
    # image 0 remove pixels that are out of bounds
    # ----------------------------------------------------------------------
    # Pixel values need to be within reasonable bounds considering the
    # physics of the IR array, and if they are not, we set them to NaN.
    # Upper bound is the saturation/frame time (we express things as slope).
    # A pixel with a value greater than can be recorded by the array is
    # nonphysical. The lower bound is set at -10 * readout noise.
    upperlim = saturate / frmtime
    lowerlim = -10 * (sigdet * gain) / frmtime
    with warnings.catch_warnings(record=True) as _:
        mask = (image > upperlim) | (image < lowerlim)
    image[mask] = np.nan

    # ----------------------------------------------------------------------
    # image 1 is corrected for dark
    # ----------------------------------------------------------------------
    if correctdark:
        darkfile, image1 = dark.correction(params, image, header, nfiles=nfiles,
                                           filename=darkfile)
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
        # convert limits
        upperlim = upperlim * gain * exptime
        lowerlim = lowerlim * gain * exptime

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
        badpfile, image3 = badpix.correction(params, image2, header,
                                             filename=badpixfile)
    else:
        image3 = np.array(image2)
        badpfile = 'None'
    # ----------------------------------------------------------------------
    # image 4 is corrected for background
    # ----------------------------------------------------------------------
    if correctback:
        bkgrdfile, image4 = background.correction(recipe, params, infile,
                                                  image3, header,
                                                  filename=backfile)
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
    # image 5 remove pixels that are out of bounds
    # ----------------------------------------------------------------------
    # Pixel values need to be within reasonable bounds considering the
    # physics of the IR array, and if they are not, we set them to NaN.
    # Upper bound is the saturation/frame time (we express things as slope).
    # A pixel with a value greater than can be recorded by the array is
    # nonphysical. The lower bound is set at -10 * readout noise.
    with warnings.catch_warnings(record=True) as _:
        mask = (image5 > upperlim) | (image5 < lowerlim)
    image5[mask] = np.nan

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
            # get value
            value = props[pkey]
            # check if path
            value = drs_fits.check_dtype_for_header(value)
            # push to header
            outfile.add_hkey(hkey, value=value)
    # return outfile
    return outfile


def load_calib_file(params, key=None, inheader=None, filename=None,
                    get_image=True, get_header=False,
                    return_filename=False, **kwargs):
    func_name = kwargs.get('func', __NAME__ + '.load_calib_file()')
    # get keys from params/kwargs
    n_entries = kwargs.get('n_entries', 1)
    required = kwargs.get('required', True)
    mode = pcheck(params, 'CALIB_DB_MATCH', 'mode', kwargs, func_name)
    # valid extension (zero by default)
    ext = kwargs.get('ext', 0)
    # fmt = valid astropy table format
    fmt = kwargs.get('fmt', 'fits')
    # kind = 'image' or 'table'
    kind = kwargs.get('kind', 'image')
    # ----------------------------------------------------------------------
    # deal with filename set
    if filename is not None:
        # get db fits file
        abspath = drs_database.get_db_abspath(params, filename, where='guess')
        # if we just want the filename return it
        if return_filename:
            return abspath
        # load file
        image, header = drs_database.get_db_file(params, abspath, ext, fmt, kind,
                                                 get_image, get_header)
        # return here
        if get_header:
            if n_entries == 1:
                return image, header, abspath
            else:
                return [image], [header], [abspath]
        else:
            if n_entries == 1:
                return image, abspath
            else:
                return [image], [abspath]
    # ----------------------------------------------------------------------
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')
    # get calibration entries
    entries = drs_database.get_key_from_db(params, key, cdb, inheader,
                                           n_ent=n_entries, mode=mode,
                                           required=required)
    # get filename col
    filecol = cdb.file_col
    # ----------------------------------------------------------------------
    # storage
    images, headers, abspaths = [], [], []
    # ----------------------------------------------------------------------
    # loop around entries
    for it, entry in enumerate(entries):
        # get entry filename
        filename = entry[filecol]
        # ------------------------------------------------------------------
        # get absolute path
        abspath = drs_database.get_db_abspath(params, filename,
                                              where='calibration')
        # append to storage
        abspaths.append(abspath)

        # deal with loading the file
        if not return_filename:
            # load image/header
            image, header = drs_database.get_db_file(params, abspath, ext,
                                                     fmt, kind, get_image,
                                                     get_header)
            # append to storage
            images.append(image)
            # append to storage
            headers.append(header)
    # ----------------------------------------------------------------------
    # deal with just a file return
    if return_filename:
        if not required and len(abspaths) == 0:
            return None
        if n_entries == 1:
            return abspaths[-1]
        else:
            return abspaths
    # ----------------------------------------------------------------------
    # deal with returns with and without header
    if get_header:
        if not required and len(images) == 0:
            return None, None, None
        # deal with if n_entries is 1 (just return file not list)
        if n_entries == 1:
            return images[-1], headers[-1], abspaths[-1]
        else:
            return images, headers, abspaths
    else:
        if not required and len(images) == 0:
            return None, None, None
        # deal with if n_entries is 1 (just return file not list)
        if n_entries == 1:
            return images[-1], abspaths[-1]
        else:
            return images, abspaths


# =============================================================================
# Define worker functions
# =============================================================================
def clean_strings(strings):
    if isinstance(strings, str):
        return strings.strip().upper()
    else:
        outstrings = []
        for string in strings:
            outstrings.append(string.strip().upper())
        return outstrings


def get_input_files(params, inputkey, key, header, default=None):
    # check for input key in inputs
    if ('INPUTS' in params) and (inputkey in params['INPUTS']):
        value = params['INPUTS'][inputkey]
        # deal with value being a list (ie.. [[filename, DrsFitsFile]])
        if isinstance(value, list):
            value = value[0][0]
        # if it is unset or 'None' then return the default
        if value is None or value == 'None':
            return default
        # else check that path exists
        elif not os.path.exists(value):
            # try to load from value (using the calibdb path)
            filename = load_calib_file(params, key, header, filename=value,
                                       return_filename=True, required=False)
            # deal with filename not existing
            if filename is None or not os.path.exists(filename):
                eargs = [inputkey, value]
                WLOG(params, 'error', TextEntry('09-001-00031', args=eargs))
        else:
            return value
    # if we don't have the value return the default
    else:
        return default


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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General calibration functions in here only

Created on 2019-06-27 at 10:48

@author: cook
"""
from astropy.table import Table
import numpy as np
from typing import List, Union, Tuple
import warnings

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_database
from apero.core.utils import drs_data
from apero.io import drs_fits
from apero.io import drs_image

from apero.science.calib import dark
from apero.science.calib import badpix
from apero.science.calib import background


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.gen_calib.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# get calibration database
CalibDatabase = drs_database.CalibrationDatabase
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get display func
display_func = drs_log.display_func


# =============================================================================
# Define user functions
# =============================================================================
def check_files(params, infile):
    # get pseudo constants
    pconst = constants.pload()
    # get infile DPRTYPE and OBJNAME
    dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str, required=False)
    objname = infile.get_hkey('KW_OBJNAME', dtype=str, required=False)
    filename = infile.filename
    # deal with unset value
    if dprtype is None:
        dprtype = 'None'
    if objname is None:
        objname = 'None'
    # clean (capitalize and remove white spaces)
    dprtype = clean_strings(dprtype)
    objname = pconst.DRS_OBJ_NAME(objname)
    # get inputs
    dprtype_inputs = params['INPUTS']['DPRTYPE'].split(',')
    objname_inputs = params['INPUTS']['OBJNAME'].split(',')
    # clean (capitalize and remove white spaces)
    dprtype_inputs = clean_strings(dprtype_inputs)
    objname_inputs = list(map(pconst.DRS_OBJ_NAME, objname_inputs))
    # ----------------------------------------------------------------------
    # log checking file info
    wargs = [dprtype, objname]
    WLOG(params, 'info', textentry('40-016-00032', args=wargs))
    # ----------------------------------------------------------------------
    # storage of outputs
    skip = False
    skip_conditions = [[], [], []]
    # ----------------------------------------------------------------------
    # convert objname_inputs to char array
    objarray = np.char.array(objname_inputs).upper()
    # deal with objname filter
    if 'NONE' in objarray:
        skip = skip or False
    # else check for objname in
    elif objname.upper() in objarray:
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


def calibrate_ppfile(params, recipe, infile, database=None, **kwargs):

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
        image = infile.get_data(copy=True)
    if header is None:
        header = infile.get_header()

    # -------------------------------------------------------------------------
    # get loco file instance
    darkinst = drs_file.get_file_definition(params, 'DARKM', block_kind='red')
    badinst = drs_file.get_file_definition(params, 'BADPIX', block_kind='red')
    backinst = drs_file.get_file_definition(params, 'BKGRD_MAP',
                                            block_kind='red')
    # get calibration key
    darkkey = darkinst.get_dbkey()
    badkey = badinst.get_dbkey()
    backkey = backinst.get_dbkey()
    # load database
    if database is None:
        calibdbm = CalibDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # -------------------------------------------------------------------------
    # load pconst
    pconst = constants.pload()
    # -------------------------------------------------------------------------
    # Get basic image properties
    sigdet = infile.get_hkey('KW_RDNOISE')
    exptime = infile.get_hkey('KW_EXPTIME')
    gain = infile.get_hkey('KW_GAIN')
    dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
    saturate = pconst.SATURATION(params, infile.get_header())
    frmtime = pconst.FRAME_TIME(params, infile.get_header())
    nfiles = infile.numfiles
    # log that we are calibrating a file
    WLOG(params, 'info', textentry('40-014-00038', args=[infile.filename]))

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
        # load dark file
        darkfile = load_calib_file(params, darkkey, header, filename=darkfile,
                                   userinputkey='DARKFILE', database=calibdbm,
                                   return_filename=True)
        # correct image
        image1 = dark.correction(params, image, nfiles=nfiles,
                                 darkfile=darkfile)
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
        WLOG(params, '', textentry('40-014-00013', args=wargs))

    # ----------------------------------------------------------------------
    # image 3 is corrected for bad pixels
    # ----------------------------------------------------------------------
    if correctbad:
        # load the pad pix file
        badpfile = load_calib_file(params, badkey, header, filename=badpixfile,
                                   userinputkey='BADPIXFILE', database=calibdbm,
                                   return_filename=True)
        # correct the image
        image3 = badpix.correction(params, image2, badpixfile=badpfile)
    else:
        image3 = np.array(image2)
        badpfile = 'None'
    # ----------------------------------------------------------------------
    # image 4 is corrected for background
    # ----------------------------------------------------------------------
    if correctback:
        # load background file from inputs/calibdb
        bkgrdfile = load_calib_file(params, backkey, header, filename=backfile,
                                    userinputkey='BACKFILE',
                                    return_filename=True, database=calibdbm)
        # correct image for background
        image4 = background.correction(recipe, params, infile, image3,
                                       bkgrdfile=bkgrdfile)
    else:
        image4 = np.array(image3)
        bkgrdfile = 'None'
    # ----------------------------------------------------------------------
    # image 4 may need to normalise by a percentile
    # ----------------------------------------------------------------------
    if n_percentile is not None:
        # log that we are normalising
        WLOG(params, '', textentry('40-014-00014', args=[n_percentile]))
        # normalise by nanpercentile
        image4 = image4 / np.nanpercentile(image4, n_percentile)

    # ----------------------------------------------------------------------
    # image 5 is cleaned from hot pixels
    # ----------------------------------------------------------------------
    if cleanhotpix:
        # log progress
        WLOG(params, '', textentry('40-014-00012'))
        # load the bad pix file
        badpfile = load_calib_file(params, badkey, header, filename=badpixfile,
                                   userinputkey='BADPIXFILE', database=calibdbm,
                                   return_filename=True)
        # get bad pixel mask
        badpixmask = badpix.correction(params, None, badpixfile=badpfile,
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


# for: load_calib_file
LoadCalibFileReturn = Union[None,
                            # if return filename
                            str,
                            # if return_filename + return_source
                            Tuple[str, str],
                            # default
                            Tuple[Union[np.ndarray, Table, None],
                                  Union[drs_fits.Header, None],
                                  str],
                            # if return_source
                            Tuple[Union[np.ndarray, Table, None],
                                  Union[drs_fits.Header, None],
                                  str, str],
                            # if nentries > 1
                            List[str],
                            # if nentries > 1 + return source
                            Tuple[List[str], str],
                            # if nentries > 1 + default
                            Tuple[List[Union[np.ndarray, Table, None]],
                                  List[Union[drs_fits.Header, None]],
                                  List[str]],
                            # if nentries > 1 + return source
                            Tuple[List[Union[np.ndarray, None]],
                                  List[Union[drs_fits.Header, None]],
                                  List[str], str]
                            ]


def load_calib_file(params: ParamDict, key: str,
                    inheader: Union[drs_fits.Header, None] = None,
                    filename: Union[str, None] = None,
                    get_image: bool = True, get_header: bool = False,
                    fiber: Union[str, None] = None,
                    userinputkey: Union[str, None] = None,
                    database: Union[CalibDatabase, None] = None,
                    return_filename: bool = False, return_source: bool = False,
                    mode: Union[str, None] = None,
                    n_entries: Union[int, str] = 1,
                    required: bool = True, ext: Union[int, None] = None,
                    fmt: str = 'fits',
                    kind: str = 'image') -> LoadCalibFileReturn:
    """
    Load one or many calibration files

    :param params: ParamDict, the parameter dictionary of constants
    :param key: str, the key from the calibration database to select a
                specific calibration with
    :param inheader: fits.Header - the header file (required to match by time)
                     if None does not match by a 'zero point' time)

    :param filename: str or None, if set overrides filename from database
    :param get_image: bool, if True loads image (or images if nentries > 1),
                      if False image is None (or list of Nones if nentries > 1)
    :param get_header: bool, if True loads header (or headers if nentries > 1)
                       if False header is None (or list of Nones if
                       nentries > 1)
    :param fiber: str or None, if set must be the fiber type - all returned
                  calibrations are filtered by this fiber type
    :param userinputkey: str or None, if set checks params['INPUTS'] for this
                         key and sets filename from here - note params['INPUTS']
                         is where command line arguments are stored
    :param database: drs calibration database instance - set this if calibration
                     database already loaded (if unset will reload the database)
    :param return_filename: bool, if True returns the filename only
    :param return_source: bool, if True returns the source of the calib file(s)
    :param mode: str or None, the time mode for getting from sql
                 ('closest'/'newer'/'older')
    :param n_entries: int or str, maximum number of calibration files to return
                      for all entries use '*'
    :param required: bool, whether we require an entry - will raise exception
                     if required=True and no entries found
    :param ext: int, valid extension (unset by default) when kind='image'
    :param fmt: str, astropy.table.Table valid format (when kind='table')
    :param kind: str, either 'image' for fits image or 'table' for table

    :return:
             if get_image, also returns image/table or list of images/tables
             if get_header, also returns header or list of headers
             if return_filename, returns filename or list of filenames
             if return_source, also returns source

             i.e. possible returns are:
                 filename
                 filename, source
                 image, header, filename
                 image, header, filename, source
                 List[filename]
                 List[filename], source
                 List[image], List[header], List[filename]
                 List[image], List[header], List[filename], source

    """
    # set function
    _ = display_func('load_calib_file', __NAME__)
    # ------------------------------------------------------------------------
    # first try to get file from inputs
    fout = drs_data.get_file_from_inputs(params, 'calibration', userinputkey,
                                         filename, return_source=return_source)
    if return_source:
        filename, source = fout
    else:
        filename, source = fout, 'None'
    # ------------------------------------------------------------------------
    # if filename is defined this is the filename we should return
    if filename is not None and return_filename:
        if return_source:
            return str(filename), source
        else:
            return str(filename)
    # -------------------------------------------------------------------------
    # else we have to load from database
    if filename is None:
        # check if we have the database
        if database is None:
            # construct a new database instance
            database = CalibDatabase(params)
            # load the database
            database.load_db()
        # load filename from database
        filename = database.get_calib_file(key, header=inheader,
                                           timemode=mode, nentries=n_entries,
                                           required=required, fiber=fiber)
        source = 'calibDB'
    # -------------------------------------------------------------------------
    # deal with filename being a path --> string (unless None)
    if filename is not None:
        if isinstance(filename, list):
            filename = list(map(lambda strfile: str(strfile), filename))
        else:
            filename = str(filename)
    # -------------------------------------------------------------------------
    # if we are just returning filename return here
    if return_filename:
        if return_source:
            return filename, source
        else:
            return filename
    # deal with not return filename
    elif filename is None and not required:
        return None
    # -------------------------------------------------------------------------
    # need to deal with a list of files
    if isinstance(filename, list):
        # storage for images and headres
        images, headers = [], []
        # loop around files
        for file_it in filename:
            # now read the calibration file
            image, header = drs_data.read_db_file(params, file_it, get_image,
                                                  get_header, kind, fmt, ext)
            # append to storage
            images.append(image)
            headers.append(headers)
        # return all
        if return_source:
            return images, headers, filename, source
        else:
            return images, headers, filename

    else:
        # now read the calibration file
        image, header = drs_data.read_db_file(params, filename, get_image,
                                              get_header, kind, fmt, ext)
        # return all
        if return_source:
            return image, header, filename, source
        else:
            return image, header, filename


def check_fp(params, image, **kwargs):
    """
    Checks that a 2D image containing FP is valid
    :param params:
    :param image:
    :return:
    """
    # set the function name
    func_name = __NAME__ + '.check_fp()'
    # get properties from params
    percentile = pcheck(params, 'CALIB_CHECK_FP_PERCENTILE', 'percentile',
                        kwargs, func_name)
    fp_qc = pcheck(params, 'CALIB_CHECK_FP_THRES', 'fp_qc', kwargs, func_name)
    centersize = pcheck(params, 'CALIB_CHECK_FP_CENT_SIZE', 'centersize',
                        kwargs, func_name)
    num_ref = pcheck(params, 'PP_NUM_REF_TOP', 'num_ref', kwargs, func_name)
    # get the image size
    nbypix, nbxpix = image.shape
    # find the 95th percentile of the center of the image
    xlower, xupper = (nbxpix // 2) - centersize, (nbxpix // 2) + centersize
    ylower, yupper = (nbypix // 2) - centersize, (nbypix // 2) + centersize
    # get the center percentile of image
    cent = np.nanpercentile(image[xlower:xupper, ylower:yupper], percentile)
    # work out the residuals in the reference pixels
    residuals = np.abs(image[:num_ref]) - np.nanmedian(image[:num_ref])
    # get the quality control on fp
    passed = (cent / np.nanmedian(residuals)) > fp_qc
    # return passed
    return passed


def check_fp_files(params, fpfiles):
    """
    Check a set of fpfiles for valid (2D) fp data

    :param params:
    :param fpfiles:
    :return:
    """
    # set the function name
    func_name = __NAME__ + '.check_fp_files()'
    # storage for valid fp files
    newfpfiles, fpfilenames = [], []
    # loop around fp files
    for fpfile in fpfiles:
        # add to list
        fpfilenames.append(fpfile.filename)
        # check if fp is good
        if check_fp(params, fpfile.get_data()):
            newfpfiles.append(fpfile)
        else:
            # log a warning that file removed
            wargs = [fpfile.filename]
            WLOG(params, 'warning', textentry('10-001-00009', args=wargs))
    # deal with having no files left
    if len(newfpfiles) == 0:
        # log: No FP files passed 2D quality control. \n\t Function = {0}
        WLOG(params, 'error', textentry('09-000-00010', args=[func_name]))
    # return new fp files
    return newfpfiles


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

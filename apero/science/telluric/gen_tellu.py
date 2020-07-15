#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:16

@author: cook
"""
from astropy.table import Table
import numpy as np
from astropy.time import Time
from scipy.ndimage import filters
from scipy.optimize import curve_fit
import os
import warnings
from collections import OrderedDict

from apero import core
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_database
from apero.io import drs_data
from apero.io import drs_fits
from apero.io import drs_path
from apero.io import drs_table
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science import extract

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.general.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def get_whitelist(params, **kwargs):
    func_name = __NAME__ + '.get_whitelist()'
    # get pseudo constants
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_WHITELIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    wout = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                   func_name, dtype=str)
    whitelist, whitelistfile = wout
    # must clean names
    whitelist = list(map(pconst.DRS_OBJ_NAME, whitelist))
    # return the whitelist
    return whitelist, whitelistfile


def get_blacklist(params, **kwargs):
    func_name = __NAME__ + '.get_blacklist()'
    # get pseudo constants
    pconst = constants.pload(instrument=params['INSTRUMENT'])
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_BLACKLIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    bout = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                   func_name, dtype=str)
    blacklist, blacklistfile = bout
    # must clean names
    blacklist = list(map(pconst.DRS_OBJ_NAME, blacklist))
    # return the whitelist
    return blacklist, blacklistfile


def normalise_by_pblaze(params, image, header, fiber, **kwargs):
    func_name = __NAME__ + '.normalise_by_pblaze()'
    # get properties from params/kwargs
    blaze_p = pcheck(params, 'MKTELLU_BLAZE_PERCENTILE', 'blaze_p', kwargs,
                     func_name)
    cut_blaze_norm = pcheck(params, 'MKTELLU_CUT_BLAZE_NORM', 'cut_blaze_norm',
                            kwargs, func_name)
    # ----------------------------------------------------------------------
    # copy the image
    image1 = np.array(image)
    # ----------------------------------------------------------------------
    # load the blaze file for this fiber
    blaze_file, blaze = flat_blaze.get_blaze(params, header, fiber)
    # copy blaze
    blaze_norm = np.array(blaze)
    # loop through blaze orders, normalize blaze by its peak amplitude
    for order_num in range(image1.shape[0]):
        # normalize the spectrum
        spo, bzo = image1[order_num], blaze[order_num]
        # normalise image
        image1[order_num] = spo / np.nanpercentile(spo, blaze_p)
        # normalize the blaze
        blaze_norm[order_num] = bzo / np.nanpercentile(bzo, blaze_p)
    # ----------------------------------------------------------------------
    # find where the blaze is bad
    with warnings.catch_warnings(record=True) as _:
        badblaze = blaze_norm < cut_blaze_norm
    # ----------------------------------------------------------------------
    # set bad blaze to NaN
    blaze_norm[badblaze] = np.nan
    # set to NaN values where spectrum is zero
    zeromask = image1 == 0
    image1[zeromask] = np.nan
    # divide spectrum by blaze
    with warnings.catch_warnings(record=True) as _:
        image1 = image1 / blaze_norm
    # ----------------------------------------------------------------------
    # parameter dictionary
    nprops = ParamDict()
    nprops['BLAZE'] = blaze
    nprops['NBLAZE'] = blaze_norm
    nprops['BLAZE_PERCENTILE'] = blaze_p
    nprops['BLAZE_CUT_NORM'] = cut_blaze_norm
    nprops['BLAZE_FILE'] = blaze_file
    # set sources
    keys = ['BLAZE', 'NBLAZE', 'BLAZE_PERCENTILE', 'BLAZE_CUT_NORM',
            'BLAZE_FILE']
    nprops.set_sources(keys, func_name)
    # return the normalised image and the properties
    return image1, nprops


def get_non_tellu_objs(params, recipe, fiber, filetype=None, dprtypes=None,
                       robjnames=None):
    """
    Get the objects of "filetype" and "
    :param params:
    :param fiber:
    :param filetype:
    :return:
    """
    # get the telluric star names (we don't want to process these)
    objnames, _ = get_whitelist(params)
    objnames = list(objnames)
    # deal with filetype being string
    if isinstance(filetype, str):
        filetype = filetype.split(',')
    # deal with dprtypes being string
    if isinstance(dprtypes, str):
        dprtypes = dprtypes.split(',')
    # construct kwargs
    fkwargs = dict()
    if filetype is not None:
        fkwargs['KW_OUTPUT'] = filetype
    if dprtypes is not None:
        fkwargs['KW_DPRTYPE'] = dprtypes
    # # find files
    out = drs_fits.find_files(params, recipe, kind='red', return_table=True,
                              fiber=fiber, **fkwargs)
    obj_filenames, obj_table = out
    # filter out telluric stars
    obj_stars, obj_names = [], []
    # loop around object table and only keep non-telluric stars
    for row in range(len(obj_table)):
        # get object name
        iobjname = obj_table['KW_OBJNAME'][row]
        # if required object name is set
        if robjnames is not None:
            if iobjname in robjnames:
                obj_stars.append(obj_filenames[row])
                if iobjname not in obj_names:
                    obj_names.append(iobjname)
        # if in telluric list skip
        elif iobjname not in objnames:
            obj_stars.append(obj_filenames[row])
            if iobjname not in obj_names:
                obj_names.append(iobjname)
    # return absolute path names and object names
    return obj_stars, obj_names


def get_tellu_objs(params, key, objnames=None, **kwargs):
    """
    Get objects defined be "key" from telluric database (in list objname)

    :param params:
    :param key:
    :param objnames:
    :param kwargs:
    :return:
    """
    # deal with column to select from entries
    column = kwargs.get('column', 'filename')
    objcol = kwargs.get('objcol', 'objname')
    # ----------------------------------------------------------------------
    # deal with objnames
    if isinstance(objnames, str):
        objnames = [objnames]
    # ----------------------------------------------------------------------
    # load telluric obj entries (based on key)
    obj_entries = load_tellu_file(params, key=key, inheader=None, mode='ALL',
                                  return_entries=True, n_entries='all',
                                  required=False)
    # add to type
    typestr = str(key)
    # ----------------------------------------------------------------------
    # keep only objects with objnames
    mask = np.zeros(len(obj_entries)).astype(bool)
    # deal with no object found
    if len(obj_entries) == 0:
        return []
    elif objnames is not None:
        # storage for found objects
        found_objs = []
        # loop around objnames
        for objname in objnames:
            # update the mask
            mask |= obj_entries[objcol] == objname
            # only add to the mask if objname found
            if objname in obj_entries[objcol]:
                # update the found objs
                found_objs.append(objname)
        # update type string
        typestr += ' OBJNAME={0}'.format(', '.join(found_objs))
    # ----------------------------------------------------------------------
    # deal with all entries / one column return
    if column in [None, 'None', '', 'ALL']:
        outputs =  obj_entries[mask]
    else:
        outputs = np.unique(obj_entries[column][mask])
    # ----------------------------------------------------------------------
    # deal with getting absolute paths
    if column == 'filename':
        abspaths = []
        # loop around filenames
        for filename in outputs:
            # get absolute path
            abspath = drs_database.get_db_abspath(params, filename,
                                                  where='telluric')
            # append to list
            abspaths.append(abspath)
        # push back into outputs
        outputs = list(abspaths)
    # ----------------------------------------------------------------------
    # display how many files found
    margs = [len(outputs),  typestr]
    WLOG(params, '', TextEntry('40-019-00039', args=margs))
    return outputs


# =============================================================================
# pre-cleaning functions
# =============================================================================
def tellu_preclean(params, recipe, image, wprops, mprops):
    pass


# =============================================================================
# Database functions
# =============================================================================
def load_tellu_file(params, key=None, inheader=None, filename=None,
                    get_image=True, get_header=False, return_entries=False,
                    **kwargs):
    # get keys from params/kwargs
    n_entries = kwargs.get('n_entries', 1)
    required = kwargs.get('required', True)
    mode = kwargs.get('mode', None)
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
        image, header = drs_database.get_db_file(params, abspath, ext, fmt,
                                                 kind, get_image, get_header)
        # return here
        if get_header:
            return [image], [header], [abspath]
        else:
            return [image], [abspath]
    # ----------------------------------------------------------------------
    # get telluDB
    tdb = drs_database.get_full_database(params, 'telluric')
    # get calibration entries
    entries = drs_database.get_key_from_db(params, key, tdb, inheader,
                                           n_ent=n_entries, mode=mode,
                                           required=required)
    # ----------------------------------------------------------------------
    # deal with return entries
    if return_entries:
        return entries
    # ----------------------------------------------------------------------
    # get filename col
    filecol = tdb.file_col
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
                                              where='telluric')
        # append to storage
        abspaths.append(abspath)
        # load image/header
        image, header = drs_database.get_db_file(params, abspath, ext, fmt,
                                                 kind, get_image, get_header)
        # append to storage
        images.append(image)
        # append to storage
        headers.append(header)
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
            return None, None
        # deal with if n_entries is 1 (just return file not list)
        if n_entries == 1:
            return images[-1], abspaths[-1]
        else:
            return images, abspaths


def load_templates(params, header, objname, fiber):

    # TODO: update - bad loads all files just to get one header
    #   OBJNAME in database --> select most recent and only load that file
    # get file definition
    out_temp = core.get_file_definition('TELLU_TEMP', params['INSTRUMENT'],
                                        kind='red', fiber=fiber)
    # deal with user not using template
    if 'USE_TEMPLATE' in params['INPUTS']:
        if not params['INPUTS']['USE_TEMPLATE']:
            return None, None
    # get key
    temp_key = out_temp.get_dbkey(fiber=fiber)
    # log status
    # TODO: move to language database
    WLOG(params, '', 'Loading {0} files'.format(temp_key))
    # load tellu file, header and abspaths
    temp_out = load_tellu_file(params, temp_key, header, get_header=True,
                               n_entries='all', required=False)
    temp_images, temp_headers, temp_filenames = temp_out

    # deal with no files in database
    if temp_images is None:
        # log that we found no templates in database
        WLOG(params, '', TextEntry('40-019-00003'))
        return None, None
    if len(temp_images) == 0:
        # log that we found no templates in database
        WLOG(params, '', TextEntry('40-019-00003'))
        return None, None
    # storage of valid files
    valid_images, valid_filenames, valid_times = [], [], []
    # loop around header and filter by objname
    for it, temp_header in enumerate(temp_headers):
        # get objname
        temp_objname = temp_header[params['KW_OBJNAME'][0]]
        # if temp_objname is the same as objname (input) then we have a
        #   valid template
        if temp_objname.upper().strip() == objname.upper().strip():
            valid_images.append(temp_images[it])
            valid_filenames.append(temp_filenames[it])

    # deal with no files for this object name
    if len(valid_images) == 0:
        # log that we found no templates for this object
        wargs = [params['KW_OBJNAME'][0], objname]
        WLOG(params, 'info', TextEntry('40-019-00004', args=wargs))
        return None, None
    # log which template we are using
    wargs = [valid_filenames[-1]]
    WLOG(params, 'info', TextEntry('40-019-00005', args=wargs))
    # only return most recent template
    return valid_images[-1], valid_filenames[-1]


def get_transmission_files(params, recipe, header, fiber):
    # get file definition
    out_trans = core.get_file_definition('TELLU_TRANS', params['INSTRUMENT'],
                                         kind='red', fiber=fiber)
    # get key
    trans_key = out_trans.get_dbkey(fiber=fiber)

    # log status
    # TODO: move to language database
    WLOG(params, '', 'Loading {0} files'.format(trans_key))
    # load tellu file, header and abspaths
    _, trans_filenames = load_tellu_file(params, trans_key, header,
                                         n_entries='all', get_image=False)
    # storage for valid files/images/times
    valid_filenames = []
    # loop around header and get times
    for filename in trans_filenames:
        # only add if filename not in list already (files will be overwritten
        #   but we can have multiple entries in database)
        if filename not in valid_filenames:
            # append to list
            valid_filenames.append(filename)
    # convert arrays
    valid_filenames = np.array(valid_filenames)
    # return all valid sorted in time
    return valid_filenames


# =============================================================================
# Tapas functions
# =============================================================================
def load_conv_tapas(params, recipe, header, mprops, fiber, **kwargs):
    func_name = __NAME__ + '.load_conv_tapas()'
    # get parameters from params/kwargs
    tellu_absorbers = pcheck(params, 'TELLU_ABSORBERS', 'absorbers', kwargs,
                             func_name, mapf='list', dtype=str)
    fwhm_pixel_lsf = pcheck(params, 'FWHM_PIXEL_LSF', 'fwhm_lsf', kwargs,
                            func_name)
    # ----------------------------------------------------------------------
    # Load any convolved files from database
    # ----------------------------------------------------------------------
    # get file definition
    if 'TELLU_CONV' in recipe.outputs:
        # get file definition
        out_tellu_conv = recipe.outputs['TELLU_CONV'].newcopy(recipe=recipe,
                                                              fiber=fiber)
        # get key
        conv_key = out_tellu_conv.get_dbkey()
    else:
        # get file definition
        out_tellu_conv = core.get_file_definition('TELLU_CONV',
                                                  params['INSTRUMENT'],
                                                  kind='red', fiber=fiber)
        # get key
        conv_key = out_tellu_conv.get_dbkey(fiber=fiber)
    # load tellu file
    _, conv_paths = load_tellu_file(params, conv_key, header, n_entries='all',
                                    get_image=False, required=False)
    if conv_paths is None:
        conv_paths = []
    # construct the filename from file instance
    out_tellu_conv.construct_filename(params, infile=mprops['WAVEINST'],
                                      path=params['DRS_TELLU_DB'])
    # if our npy file already exists then we just need to read it
    if out_tellu_conv.filename in conv_paths:
        # log that we are loading tapas convolved file
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00001', args=wargs))
        # ------------------------------------------------------------------
        # Load the convolved TAPAS atmospheric transmission from file
        # ------------------------------------------------------------------
        # load npy file
        out_tellu_conv.read_file(params)
        # push data into array
        tapas_all_species = np.array(out_tellu_conv.data)
    # else we need to load tapas and generate the convolution
    else:
        # ------------------------------------------------------------------
        # Load the raw TAPAS atmospheric transmission
        # ------------------------------------------------------------------
        tapas_raw_table, tapas_raw_filename = drs_data.load_tapas(params)
        # ------------------------------------------------------------------
        # Convolve with master wave solution
        # ------------------------------------------------------------------
        tapas_all_species = _convolve_tapas(params, tapas_raw_table, mprops,
                                            tellu_absorbers, fwhm_pixel_lsf)
        # ------------------------------------------------------------------
        # Save convolution for later use
        # ------------------------------------------------------------------
        out_tellu_conv.data = tapas_all_species
        # log saving
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00002', args=wargs))
        # save
        out_tellu_conv.write_file(params)

        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
        # npy file must set header/hdict (to update)
        out_tellu_conv.header = header
        out_tellu_conv.hdict = header
        # copy the order profile to the calibDB
        drs_database.add_file(params, out_tellu_conv)

    # ------------------------------------------------------------------
    # get the tapas_water and tapas_others data
    # ------------------------------------------------------------------
    # water is the second column
    tapas_water = tapas_all_species[1, :]
    # other is defined as the product of the other columns
    tapas_other = np.prod(tapas_all_species[2:, :], axis=0)

    # return the tapas info in a ParamDict
    tapas_props = ParamDict()
    tapas_props['TAPAS_ALL_SPECIES'] = tapas_all_species
    tapas_props['TAPAS_WATER'] = tapas_water
    tapas_props['TAPAS_OTHER'] = tapas_other
    tapas_props['TAPAS_FILE'] = out_tellu_conv.filename
    tapas_props['TELLU_ABSORBERS'] = tellu_absorbers
    tapas_props['FWHM_PIXEL_LSF'] = fwhm_pixel_lsf
    # set source
    keys = ['TAPAS_ALL_SPECIES', 'TAPAS_WATER', 'TAPAS_OTHER',
            'TAPAS_FILE', 'TELLU_ABSORBERS', 'FWHM_PIXEL_LSF']
    tapas_props.set_sources(keys, func_name)
    # return tapas props
    return tapas_props


def load_tapas_convolved(params, recipe, header, mprops, fiber, **kwargs):
    func_name = __NAME__ + '.load_conv_tapas()'
    # get parameters from params/kwargs
    tellu_absorbers = pcheck(params, 'TELLU_ABSORBERS', 'absorbers', kwargs,
                             func_name)
    fwhm_pixel_lsf = pcheck(params, 'FWHM_PIXEL_LSF', 'fwhm_lsf', kwargs,
                            func_name)
    # ----------------------------------------------------------------------
    # Load any convolved files from database
    # ----------------------------------------------------------------------
    # get file definition
    out_tellu_conv = core.get_file_definition('TELLU_CONV',
                                              params['INSTRUMENT'],
                                              kind='red', fiber=fiber)
    # get key
    conv_key = out_tellu_conv.get_dbkey(fiber=fiber)
    # load tellu file
    _, conv_paths = load_tellu_file(params, conv_key, header, n_entries='all',
                                    get_image=False, required=False)
    # construct the filename from file instance
    out_tellu_conv.construct_filename(params, infile=mprops['WAVEINST'],
                                      path=params['DRS_TELLU_DB'])
    # if our npy file already exists then we just need to read it
    if out_tellu_conv.filename in conv_paths:
        # log that we are loading tapas convolved file
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00001', args=wargs))
        # ------------------------------------------------------------------
        # Load the convolved TAPAS atmospheric transmission from file
        # ------------------------------------------------------------------
        # load npy file
        out_tellu_conv.read_file(params)
        # push data into array
        tapas_all_species = np.array(out_tellu_conv.data)
        # ------------------------------------------------------------------
        # get the tapas_water and tapas_others data
        # ------------------------------------------------------------------
        # water is the second column
        tapas_water = tapas_all_species[1, :]
        # other is defined as the product of the other columns
        tapas_other = np.prod(tapas_all_species[2:, :], axis=0)
        # return the tapas info in a ParamDict
        tapas_props = ParamDict()
        tapas_props['TAPAS_ALL_SPECIES'] = tapas_all_species
        tapas_props['TAPAS_WATER'] = tapas_water
        tapas_props['TAPAS_OTHER'] = tapas_other
        tapas_props['TAPAS_FILE'] = out_tellu_conv.filename
        tapas_props['TELLU_ABSORBERS'] = tellu_absorbers
        tapas_props['FWHM_PIXEL_LSF'] = fwhm_pixel_lsf
        # set source
        keys = ['TAPAS_ALL_SPECIES', 'TAPAS_WATER', 'TAPAS_OTHER',
                'TAPAS_FILE', 'TELLU_ABSORBERS', 'FWHM_PIXEL_LSF']
        tapas_props.set_sources(keys, func_name)
        # return tapas props
        return tapas_props
    # else we generate an error
    else:
        # log that no matching tapas convolved file exists
        wargs = [conv_key, out_tellu_conv.filename, func_name]
        WLOG(params, 'error', TextEntry('09-019-00002', args=wargs))


# =============================================================================
# Worker functions
# =============================================================================
def _convolve_tapas(params, tapas_table, mprops, tellu_absorbers,
                    fwhm_pixel_lsf):
    # get master wave data
    masterwave = mprops['WAVEMAP']
    ydim = mprops['NBO']
    xdim = mprops['NBPIX']
    # ----------------------------------------------------------------------
    # generate kernel for convolution
    # ----------------------------------------------------------------------
    # get the number of kernal pixels
    npix_ker = int(np.ceil(3 * fwhm_pixel_lsf * 3.0 / 2) * 2 + 1)
    # set up the kernel exponent
    kernel = np.arange(npix_ker) - npix_ker // 2
    # kernal is the a gaussian
    kernel = np.exp(-0.5 * (kernel / (fwhm_pixel_lsf / mp.fwhm())) ** 2)
    # we only want an approximation of the absorption to find the continuum
    #    and estimate chemical abundances.
    #    there's no need for a varying kernel shape
    kernel /= mp.nansum(kernel)
    # ----------------------------------------------------------------------
    # storage for output
    tapas_all_species = np.zeros([len(tellu_absorbers), xdim * ydim])
    # ----------------------------------------------------------------------
    # loop around each molecule in the absorbers list
    #    (must be in
    for n_species, molecule in enumerate(tellu_absorbers):
        # log process
        wmsg = 'Processing molecule: {0}'
        WLOG(params, '', wmsg.format(molecule))
        # get wavelengths
        lam = tapas_table['wavelength']
        # get molecule transmission
        trans = tapas_table['trans_{0}'.format(molecule)]
        # interpolate with Univariate Spline
        tapas_spline = mp.iuv_spline(lam, trans)
        # log the mean transmission level
        wmsg = '\tMean Trans level: {0:.3f}'.format(np.mean(trans))
        WLOG(params, '', wmsg)
        # convolve all tapas absorption to the SPIRou approximate resolution
        for iord in range(ydim):
            # get the order position
            start = iord * xdim
            end = (iord * xdim) + xdim
            # interpolate the values at these points
            svalues = tapas_spline(masterwave[iord, :])
            # convolve with a gaussian function
            nvalues = np.convolve(np.ones_like(svalues), kernel, mode='same')
            cvalues = np.convolve(svalues, kernel, mode='same') / nvalues
            # add to storage
            tapas_all_species[n_species, start: end] = cvalues
    # deal with non-real values (must be between 0 and 1
    tapas_all_species[tapas_all_species > 1] = 1
    tapas_all_species[tapas_all_species < 0] = 0

    # return tapas_all_species
    return tapas_all_species


def wave_to_wave(params, spectrum, wave1, wave2, reshape=False):
    """
    Shifts a "spectrum" at a given wavelength solution (map), "wave1", to
    another wavelength solution (map) "wave2"

    :param params: ParamDict, the parameter dictionary
    :param spectrum: numpy array (2D),  flux in the reference frame of the
                     file wave1
    :param wave1: numpy array (2D), initial wavelength grid
    :param wave2: numpy array (2D), destination wavelength grid
    :param reshape: bool, if True try to reshape spectrum to the shape of
                    the output wave solution

    :return output_spectrum: numpy array (2D), spectrum resampled to "wave2"
    """
    func_name = __NAME__ + '._wave_to_wave()'
    # deal with reshape
    if reshape or (spectrum.shape != wave2.shape):
        try:
            spectrum = spectrum.reshape(wave2.shape)
        except ValueError:
            # log that we cannot reshape spectrum
            eargs = [spectrum.shape, wave2.shape, func_name]
            WLOG(params, 'error', TextEntry('09-019-00004', args=eargs))
    # if they are the same
    if mp.nansum(wave1 != wave2) == 0:
        return spectrum
    # size of array, assumes wave1, wave2 and spectrum have same shape
    sz = np.shape(spectrum)
    # create storage for the output spectrum
    output_spectrum = np.zeros(sz) + np.nan
    # looping through the orders to shift them from one grid to the other
    for iord in range(sz[0]):
        # only interpolate valid pixels
        g = np.isfinite(spectrum[iord, :])
        # if no valid pixel, thn skip order
        if mp.nansum(g) != 0:
            # spline the spectrum
            spline = mp.iuv_spline(wave1[iord, g], spectrum[iord, g],
                                   k=5, ext=1)
            # keep track of pixels affected by NaNs
            splinemask = mp.iuv_spline(wave1[iord, :], g, k=5, ext=1)
            # spline the input onto the output
            output_spectrum[iord, :] = spline(wave2[iord, :])
            # find which pixels are not NaNs
            mask = splinemask(wave2[iord, :])
            # set to NaN pixels outside of domain
            bad = (output_spectrum[iord, :] == 0)
            output_spectrum[iord, bad] = np.nan
            # affected by a NaN value
            # normally we would use only pixels ==1, but we get values
            #    that are not exactly one due to the interpolation scheme.
            #    We just set that >50% of the
            # flux comes from valid pixels
            bad = (mask <= 0.5)
            # mask pixels affected by nan
            output_spectrum[iord, bad] = np.nan
    # return the filled output spectrum
    return output_spectrum


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

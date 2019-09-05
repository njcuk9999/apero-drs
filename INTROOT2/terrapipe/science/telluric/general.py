#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:16

@author: cook
"""
from __future__ import division
import numpy as np
from scipy.ndimage import filters
from scipy.optimize import curve_fit
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe.core import math
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.core.core import drs_database
from terrapipe.io import drs_data
from terrapipe.io import drs_path
from terrapipe.science.calib import flat_blaze


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.general.py'
__INSTRUMENT__ = None
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
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def get_whitelist(params, **kwargs):
    func_name = __NAME__ + '.get_whitelist()'
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_WHITELIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    whitelist = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                        func_name)
    # return the whitelist
    return whitelist


def get_blacklist(params, **kwargs):
    func_name = __NAME__ + '.get_blacklist()'
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_BLACKLIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    blacklist = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                        func_name)
    # return the whitelist
    return blacklist


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

    # loop through blaze orders, normalize blaze by its peak amplitude
    for order_num in range(image1.shape[0]):
        # normalize the spectrum
        spo, bzo = image1[order_num], blaze[order_num]

        image1[order_num] = spo / np.nanpercentile(spo, blaze_p)
        # normalize the blaze
        blaze[order_num] = bzo / np.nanpercentile(bzo, blaze_p)
    # ----------------------------------------------------------------------
    # find where the blaze is bad
    with warnings.catch_warnings(record=True) as _:
        badblaze = blaze < cut_blaze_norm
    # ----------------------------------------------------------------------
    # set bad blaze to NaN
    blaze[badblaze] = np.nan
    # set to NaN values where spectrum is zero
    zeromask = image1 == 0
    image1[zeromask] = np.nan
    # divide spectrum by blaze
    with warnings.catch_warnings(record=True) as _:
        image1 = image1 / blaze
    # ----------------------------------------------------------------------
    # parameter dictionary
    nprops = ParamDict()
    nprops['BLAZE'] = blaze
    nprops['BLAZE_PERCENTILE'] = blaze_p
    nprops['BLAZE_CUT_NORM'] = cut_blaze_norm
    nprops['BLAZE_FILE'] = blaze_file

    # return the normalised image and the properties
    return image1, nprops


# =============================================================================
# Database functions
# =============================================================================
def load_tellu_file(params, key=None, inheader=None, filename=None,
                    get_image=True, get_header=False, **kwargs):
    func_name = kwargs.get('func', __NAME__ + '.load_tellu_file()')
    # get keys from params/kwargs
    n_entries = kwargs.get('n_entries', 1)
    required = kwargs.get('required', True)
    mode = None
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
        image, header = drs_database.get_db_file(params, abspath, ext, fmt, kind,
                                                 get_image, get_header)
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
    # get filename col
    filecol = tdb.file_col
    # ----------------------------------------------------------------------
    # storage
    images, headers, abspaths = [], [], []
    # ----------------------------------------------------------------------
    # loop around entries
    for it, entry in entries:
        # get entry filename
        filename = entry[filecol]
        # ------------------------------------------------------------------
        # get absolute path
        abspath = drs_database.get_db_abspath(params, filename,
                                              where='telluric')
        # append to storage
        abspaths.append(abspath)
        # load image/header
        image, header = drs_database.get_db_file(params, abspath, ext, fmt, kind,
                                                 get_image, get_header)
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
            return None, None, None
        # deal with if n_entries is 1 (just return file not list)
        if n_entries == 1:
            return images[-1], abspaths[-1]
        else:
            return images, abspaths


def load_templates(params, recipe, header, objname, fiber):
    # get file definition
    out_temp = recipe.outputs['TELLU_TEMP'].newcopy(recipe=recipe, fiber=fiber)
    # get key
    temp_key = out_temp.get_dbkey()
    # load tellu file, header and abspaths
    temp_out = load_tellu_file(params, temp_key, header, get_header=True,
                               n_entries='all')
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
        WLOG(params, '', TextEntry('40-019-00004', args=wargs))
        return None, None
    # log which template we are using
    wargs = [valid_filenames[-1]]
    WLOG(params, '', TextEntry('40-019-00005', args=wargs))
    # only return most recent template
    return valid_images[-1], valid_filenames[-1]


def get_transmission_files(params, recipe, header, fiber):
    # get file definition
    out_trans = recipe.outputs['TELLU_MAP'].newcopy(recipe=recipe, fiber=fiber)
    # get key
    trans_key = out_trans.get_dbkey()
    # load tellu file, header and abspaths
    _, trans_filenames = load_tellu_file(params, trans_key, header,
                                         n_entries='all', get_image=False)
    # storage for valid files/images/times
    valid_filenames = []
    # loop around header and get times
    for filename in enumerate(valid_filenames):
        # only add if filename not in list already (files will be overwritten
        #   but we can have multiple entries in database)
        if filename not in trans_filenames:
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
                             func_name)
    fwhm_pixel_lsf = pcheck(params, 'FWHM_PIXEL_LSF', 'fwhm_lsf', kwargs,
                            func_name)
    # ----------------------------------------------------------------------
    # Load any convolved files from database
    # ----------------------------------------------------------------------
    # get file definition
    out_tellu_conv = recipe.outputs['TELL_CONV'].newcopy(recipe=recipe,
                                                         fiber=fiber)
    # get key
    conv_key = out_tellu_conv.get_dbkey()
    # load tellu file
    _, conv_paths = load_tellu_file(params, conv_key, header, n_entries='all',
                                    get_image=False)
    # construct the filename from file instance
    out_tellu_conv.construct_filename(params, infile=mprops['WAVEINST'])
    # if our npy file already exists then we just need to read it
    if out_tellu_conv.filename in conv_paths:
        # log that we are loading tapas convolved file
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00001', args=wargs))
        # ------------------------------------------------------------------
        # Load the convolved TAPAS atmospheric transmission from file
        # ------------------------------------------------------------------
        # load npy file
        out_tellu_conv.read(params)
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
        out_tellu_conv.write(params)
        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
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
    tapas_props['TELLU_ABORBERS'] = tellu_absorbers
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
    out_tellu_conv = recipe.outputs['TELL_CONV'].newcopy(recipe=recipe,
                                                         fiber=fiber)
    # get key
    conv_key = out_tellu_conv.get_dbkey()
    # load tellu file
    _, conv_paths = load_tellu_file(params, conv_key, header, n_entries='all',
                                    get_images=False)
    # construct the filename from file instance
    out_tellu_conv.construct_filename(params, infile=mprops['WAVEINST'])
    # if our npy file already exists then we just need to read it
    if out_tellu_conv.filename in conv_paths:
        # log that we are loading tapas convolved file
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00001', args=wargs))
        # ------------------------------------------------------------------
        # Load the convolved TAPAS atmospheric transmission from file
        # ------------------------------------------------------------------
        # load npy file
        out_tellu_conv.read(params)
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
        tapas_props['TELLU_ABORBERS'] = tellu_absorbers
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
# Make telluric functions
# =============================================================================
def calculate_telluric_absorption(params, image, template, template_file,
                                  header, wprops, tapas_props, bprops,
                                  **kwargs):

    func_name = __NAME__ + '.calculate_telluric_absoprtion()'
    # get constatns from params/kwargs
    default_conv_width = pcheck(params, 'MKTELLU_DEFAULT_CONV_WIDTH',
                                'default_conv_width', kwargs, func_name)
    finer_conv_width = pcheck(params, 'MKTELLU_FINER_CONV_WIDTH',
                              'finer_conv_width', kwargs, func_name)
    clean_orders = pcheck(params, 'MKTELLU_CLEAN_ORDERS', 'clean_orders',
                          kwargs, func_name, mapf='list', dtype=int)
    med_filt1 = pcheck(params, 'MKTELLU_TEMP_MED_FILT', 'med_filt', kwargs,
                       func_name)
    dparam_threshold = pcheck(params, 'MKTELLU_DPARAMS_THRES',
                              'dparam_threshold', kwargs, func_name)
    max_iteration = pcheck(params, 'MKTELLU_MAX_ITER', 'max_iteration',
                            kwargs, func_name)
    threshold_transmission_fit = pcheck(params, 'MKTELLU_THRES_TRANSFIT',
                                        'treshold_transmission_fit', kwargs,
                                        func_name)
    transfit_upper_bad = pcheck(params, 'MKTELLU_TRANS_FIT_UPPER_BAD',
                                'transfit_upper_bad', kwargs, func_name)
    min_watercol = pcheck(params, 'MKTELLU_TRANS_MIN_WATERCOL', 'min_watercol',
                          kwargs, func_name)
    max_watercol = pcheck(params, 'MKTELLU_TRANS_MAX_WATERCOL', 'max_watercol',
                          kwargs, func_name)
    min_number_good_points = pcheck(params, 'MKTELLU_TRANS_MIN_NUM_GOOD',
                                    'min_number_good_points', kwargs, func_name)
    btrans_percentile = pcheck(params, 'MKTELLU_TRANS_TAU_PERCENTILE',
                               'btrans_percentile', kwargs, func_name)
    nsigclip = pcheck(params, 'MKTELLU_TRANS_SIGMA_CLIP', 'nsigclip',
                      kwargs, func_name)
    med_filt2 = pcheck(params, 'MKTELLU_TRANS_TEMPLATE_MEDFILT',
                       'med_filt', kwargs, func_name)
    small_weight = pcheck(params, 'MKTELLU_SMALL_WEIGHTING_ERROR',
                          'small_weight', kwargs, func_name)
    tellu_med_sampling = pcheck(params, 'IMAGE_PIXEL_SIZE', 'med_sampling',
                                kwargs, func_name)
    plot_order_nums = pcheck(params, 'MKTELLU_PLOT_ORDER_NUMS',
                             'plot_order_nums', kwargs, func_name,
                             mapf='list', dtype=int)
    tau_water_upper = pcheck(params, 'MKTELLU_TAU_WATER_ULIMIT',
                             'tau_water_upper', kwargs, func_name)
    tau_others_lower = pcheck(params, 'MKTELLU_TAU_OTHER_LLIMIT',
                              'tau_water_lower', kwargs, func_name)
    tau_others_upper = pcheck(params, 'MKTELLU_TAU_OTHER_ULIMIT',
                              'tau_others_upper', kwargs, func_name)
    tapas_small_number = pcheck(params, 'MKTELLU_SMALL_LIMIT',
                                'tapas_small_number', kwargs, func_name)
    # ------------------------------------------------------------------
    # copy image
    image1 = np.array(image)
    # get berv from bprops
    berv = bprops['BERV']
    # get airmass from header
    airmass = header[params['KW_AIRMASS'][0]]
    # get wave map
    wavemap = wprops['WAVEMAP']
    # get dimensions of data
    nbo, nbpix = image1.shape
    # get the tapas data
    tapas_water = tapas_props['TAPAS_WATER']
    tapas_others = tapas_props['TAPAS_OTHER']
    # ------------------------------------------------------------------
    # Apply template
    # ------------------------------------------------------------------
    # set the default convolution width for each order
    wconv = np.repeat(default_conv_width, nbo).astype(float)
    # deal with no template
    if template is None:
        # set a flag to tell us that we didn't start with a template
        template_flag = True
        # assume template is ones everywhere
        template = np.ones_like(image1).astype(float)
        # check that clean orders are valid
        for clean_order in clean_orders:
            if (clean_order < 0) or (clean_order >= nbo):
                # log error: one of the orders is out of bounds
                wargs = ['MKTELLU_CLEAN_ORDERS', clean_order, func_name]
                WLOG(params, 'error', TextEntry('09-019-00001', args=wargs))
        # make clean_orders a numpy array
        clean_orders = np.array(clean_orders).astype(int)
        # if we don't have a template then we use a small kernel on only
        #    relatively clean orders
        wconv[clean_orders] = finer_conv_width
    # else we need to divide by template (after shifting)
    else:
        # set a flag to tell us that we didn't start with a template
        template_flag = False
        # wavelength offset from BERV
        dvshift = math.relativistic_waveshift(berv, units='km/s')
        # median-filter the template. we know that stellar features
        #    are very broad. this avoids having spurious noise in our templates
        # loop around each order
        for order_num in range(nbo):
            # only keep non NaNs
            keep = np.isfinite(template[order_num])
            # apply median filter
            mfargs = [template[order_num, keep], med_filt1]
            template[order_num, keep] = filters.median_filter(*mfargs)

        # loop around each order again
        for order_num in range(nbo):
            # only keep non NaNs
            keep = np.isfinite(template[order_num])
            # if less than 50% of the order is considered valid, then set
            #     template value to 1 this only apply to the really contaminated
            #     orders
            if np.nansum(keep) > nbpix // 2:
                # get the wave and template masked arrays
                keepwave = wavemap[order_num, keep]
                keeptmp = template[order_num, keep]
                # spline the good values
                spline = math.iuv_spline(keepwave * dvshift, keeptmp, k=1,
                                         ext=3)
                # interpolate good values onto full array
                template[order_num] = spline(wavemap[order_num])
            else:
                template[order_num] = np.repeat(1.0, nbpix)

    # ------------------------------------------------------------------
    # Calculation of telluric absorption
    # ------------------------------------------------------------------
    # define tapas fit constants parameters
    tapas_fit_kwargs = dict(sp_water=tapas_water, sp_others=tapas_others,
                            tau_water_upper=tau_water_upper,
                            tau_others_lower=tau_others_lower,
                            tau_others_upper=tau_others_upper,
                            tapas_small_number=tapas_small_number)

    # define function for curve_fit
    def tapas_fit(keep, tau_water, tau_others):
        return _calc_tapas_abso(keep, tau_water, tau_others, **tapas_fit_kwargs)

    # starting point for the optical depth of water and other gasses
    guess = [airmass, airmass]

    # first estimate of the absorption spectrum
    tau1 = tapas_fit(np.isfinite(wavemap), guess[0], guess[1])
    tau1 = tau1.reshape(image1.shape)
    # first guess at the SED estimate for the hot start (we guess with a
    #   spectrum full of ones
    sed = np.ones_like(wavemap)
    # flag to see if we converged (starts off very large)
    # this is the quadratic sum of the change in airmass and water column
    # when the change in the sum of these two values is very small between
    # two steps, we assume that the code has converges
    dparam = np.inf

    # count the number of iterations
    iteration = 0

    # if the code goes out-of-bound, then we'll get out of the loop with this
    #    keyword
    fail = False
    skip = False

    # conditions to carry on looping
    cond1 = dparam > dparam_threshold
    cond2 = iteration < max_iteration
    cond3 = not fail

    # set up empty arrays
    oimage2_arr = np.zeros((nbo, nbpix), dtype=float)
    sed_update_arr = np.zeros(nbpix, dtype=float)
    keep = np.zeros(nbpix, dtype=bool)
    # loop around until one condition not met
    while cond1 and cond2 and cond3:
        # ---------------------------------------------------------------------
        # previous guess
        prev_guess = np.array(guess)
        # ---------------------------------------------------------------------
        # we have an estimate of the absorption spectrum
        fit_image = image1 / sed
        # ---------------------------------------------------------------------
        # some masking of NaN regions
        nanmask = ~np.isfinite(fit_image)
        fit_image[nanmask] = 0
        # ---------------------------------------------------------------------
        # vector used to mask invalid regions
        keep = fit_image != 0
        # only fit where the transmission is greater than a certain value
        keep &= tau1 > threshold_transmission_fit
        # considered bad if the spectrum is larger than '. This is
        #     likely an OH line or a cosmic ray
        keep &= fit_image < transfit_upper_bad
        # ---------------------------------------------------------------------
        # fit telluric absorption of the spectrum
        with warnings.catch_warnings(record=True) as _:
            popt, pcov = curve_fit(tapas_fit, keep, fit_image.ravel(), p0=guess)
        # update our guess
        guess = np.array(popt)
        # ---------------------------------------------------------------------
        # if our tau_water guess is bad fail
        if (guess[0] < min_watercol) or (guess[0] > max_watercol):
            # log warning that recovered water vapor optical depth not between
            #     limits
            wargs = [guess[0], min_watercol, max_watercol]
            WLOG(params, 'warning', TextEntry('10-019-00003', args=wargs))
            # set fail to True
            fail = True
            # break out of the while loop
            break
        # ---------------------------------------------------------------------
        # we will use a stricter condition later, but for all steps
        #    we expect an agreement within an airmass difference of 1
        if np.abs(guess[1] - airmass) > 1:
            # log that recovered optical depth of others is too different
            #     from airmass
            wargs = [guess[1], airmass]
            WLOG(params, 'warning', TextEntry('10-019-00004', args=wargs))
            # set fail to True
            fail = True
            # break out of the while loop
            break
        # ---------------------------------------------------------------------
        # calculate how much the optical depth params change
        dparam = np.sqrt(np.nansum((guess - prev_guess) ** 2))
        # ---------------------------------------------------------------------
        # print progress
        wargs = [iteration, max_iteration, guess[0], guess[1], airmass]
        WLOG(params, '', TextEntry('', args=wargs))
        # ---------------------------------------------------------------------
        # get current best-fit spectrum
        tau1 = tapas_fit(np.isfinite(wavemap), guess[0], guess[1])
        tau1 = tau1.reshape(image1.shape)
        # ---------------------------------------------------------------------
        # for each order, we fit the SED after correcting for absorption
        for order_num in range(nbo):
            # -----------------------------------------------------------------
            # get the per-order spectrum divided by best guess
            oimage = image1[order_num] / tau1[order_num]
            # -----------------------------------------------------------------
            # find this orders good pixels
            good = keep[order_num]
            # -----------------------------------------------------------------
            # if we have enough valid points, we normalize the domain by its
            #    median
            if np.nansum(good) > min_number_good_points:
                limit = np.nanpercentile(tau1[order_num][good],
                                         btrans_percentile)
                best_trans = tau1[order_num] > limit
                norm = np.nanmedian(oimage[best_trans])
            else:
                norm = np.ones_like(oimage)
            # -----------------------------------------------------------------
            # normalise this orders spectrum
            image1[order_num] = image1[order_num] / norm
            # normalise sp2 and the sed
            oimage = oimage / norm
            sed[order_num] = sed[order_num] / norm
            # -----------------------------------------------------------------
            # find far outliers to the SED for sigma-clipping
            with warnings.catch_warnings(record=True) as _:
                res = oimage - sed[order_num]
                res -= np.nanmedian(res)
                res /= np.nanmedian(np.abs(res))
            # set all NaN pixels to large value
            nanmask = ~np.isfinite(res)
            res[nanmask] = 99
            # -----------------------------------------------------------------
            # apply sigma clip
            good &= np.abs(res) < nsigclip
            # apply median to sed
            with warnings.catch_warnings(record=True) as _:
                good &= sed[order_num] > 0.5 * np.nanmedian(sed[order_num])
            # only fit where the transmission is greater than a certain value
            good &= tau1[order_num] > threshold_transmission_fit
            # -----------------------------------------------------------------
            # set non-good (bad) pixels to NaN
            oimage[~good] = np.nan
            # sp3 is a median-filtered version of sp2 where pixels that have
            #     a transmission that is too low are clipped.
            oimage2 = filters.median_filter(oimage - sed[order_num], med_filt2)
            oimage2 = oimage2 + sed[order_num]
            # find all the NaNs and set to zero
            nanmask = ~np.isfinite(oimage2)
            oimage2[nanmask] = 0.0
            # also set zero pixels in sp3 to be non-good pixels in "good"
            good[oimage2 == 0.0] = False
            # -----------------------------------------------------------------
            # we smooth sp3 with a kernel. This kernel has to be small
            #    enough to preserve stellar features and large enough to
            #    subtract noise this is why we have an order-dependent width.
            #    the stellar lines are expected to be larger than 200km/s,
            #    so a kernel much smaller than this value does not make sense
            ew = wconv[order_num] / tellu_med_sampling / math.fwhm()
            # get the kernal x values
            wconv_ord = int(wconv[order_num])
            kernal_x = np.arange(-2 * wconv_ord, 2 * wconv_ord)
            # get the gaussian kernal
            kernal_y = np.exp(-0.5*(kernal_x / ew) **2 )
            # normalise kernal so it is max at unity
            kernal_y = kernal_y / np.nansum(kernal_y)
            # -----------------------------------------------------------------
            # construct a weighting matrix for the sed
            ww1 = np.convolve(good, kernal_y, mode='same')
            # need to weight the spectrum accordingly
            spconv = np.convolve(oimage2 * good, kernal_y, mode='same')
            # update the sed
            with warnings.catch_warnings(record=True) as _:
                sed_update = spconv / ww1
            # set all small values to 1% to avoid small weighting errors
            sed_update[ww1 < small_weight] = np.nan
            if wconv[order_num] == finer_conv_width:
                rms_limit = 0.1
            else:
                rms_limit = 0.3
            # iterate around and sigma clip
            for iteration_sig_clip_good in range(1, 6):
                # get residuals
                with warnings.catch_warnings(record=True) as _:
                    residual_SED = oimage2 - sed_update
                    residual_SED[~good] = np.nan
                # turn all residual values to positive
                rms = np.abs(residual_SED)
                # identify the good values and set them to zero
                with warnings.catch_warnings(record=True) as _:
                    good[rms > (rms_limit / iteration_sig_clip_good)] = 0
                # ---------------------------------------------------------
                # construct a weighting matrix for the sed
                ww1 = np.convolve(good, kernal_y, mode='same')
                # need to weight the spectrum accordingly
                spconv = np.convolve(oimage2 * good, kernal_y, mode='same')
                # update the sed
                with warnings.catch_warnings(record=True) as _:
                    sed_update = spconv / ww1
                # set all small values to 1% to avoid small weighting errors
                sed_update[ww1 < 0.01] = np.nan
            # -----------------------------------------------------------------
            # if we have lots of very strong absorption, we subtract the
            #    median value of pixels where the transmission is expected to
            #    be smaller than 1%. This improves things in the stronger
            #    absorptions
            pedestal = tau1[order_num] < 0.01
            # check if we have enough strong absorption
            if np.nansum(pedestal) > 100:
                zero_point = np.nanmedian(image1[order_num, pedestal])
                # if zero_point is finite subtract it off the spectrum
                if np.isfinite(zero_point):
                    image1[order_num] -= zero_point
            # -----------------------------------------------------------------
            # update the sed
            sed[order_num] = sed_update
            # append sp3
            oimage2_arr[order_num] = np.array(oimage2)
            # -----------------------------------------------------------------
            # debug plot
            if params['DRS_PLOT'] and params['DRS_DEBUG'] and not skip:
                # TODO: Add plotting
                # # plot the transmission map plot
                # pargs = [order_num, wavemap, tau1, image, oimage2,
                #          sed, sed_update, keep]
                # sPlt.mk_tellu_wave_flux_plot(params, *pargs)
                # # get user input to continue or skip
                # imsg = 'Press [Enter] for next or [s] for skip:\t'
                # uinput = input(imsg)
                # if 's' in uinput.lower():
                #     skip = True
                # # close plot
                # sPlt.plt.close()
                pass
        # ---------------------------------------------------------------------
        # update the iteration number
        iteration += 1
        # ---------------------------------------------------------------------
        # update while parameters
        cond1 = dparam > dparam_threshold
        cond2 = iteration < max_iteration
        cond3 = not fail
    # ---------------------------------------------------------------------
    if params['DRS_PLOT'] and params['DRS_DEBUG']:
        # TODO: Add plotting
        # # if plot orders is 'all' plot all
        # if plot_order_nums == 'all':
        #     plot_order_nums = np.arange(nbo).astype(int)
        #     # start non-interactive plot
        #     sPlt.plt.ioff()
        #     off = True
        # else:
        #     sPlt.plt.ion()
        #     off = False
        # # loop around the orders to show
        # for order_num in plot_order_nums:
        #     pargs = [order_num, wavemap, tau1, image, oimage2[order_num], sed,
        #              sed[order_num], keep]
        #     sPlt.mk_tellu_wave_flux_plot(params, *pargs)
        # if off:
        #     sPlt.plt.ion()
        pass
    # ---------------------------------------------------------------------
    # calculate transmission map
    transmission_map = image1 / sed
    # ---------------------------------------------------------------------
    # add output dictionary
    tprops = ParamDict()
    tprops['PASSED'] = not fail
    tprops['RECOV_AIRMASS'] = guess[1]
    tprops['RECOV_WATER'] = guess[0]
    tprops['IMAGE_OUT'] = image1
    tprops['SED_OUT'] = sed
    tprops['TEMPLATE'] = template
    tprops['TEMPLATE_FLAG'] = template_flag
    tprops['TRANMISSION_MAP'] = transmission_map
    tprops['AIRMASS'] = airmass
    tprops['TEMPLATE_FILE'] = template_file
    # set sources
    keys = ['PASSED', 'RECOV_AIRMASS', 'RECOV_WATER', 'IMAGE_OUT', 'SED_OUT',
            'TEMPLATE', 'TEMPLATE_FLAG', 'TRANMISSION_MAP', 'AIRMASS',
            'TEMPLATE_FILE']
    tprops.set_sources(keys, func_name)
    # add constants
    tprops['DEFAULT_CWIDTH'] = default_conv_width
    tprops['FINER_CWIDTH'] = finer_conv_width
    tprops['TEMP_MED_FILT'] = med_filt1
    tprops['DPARAM_THRES'] = dparam_threshold
    tprops['MAX_ITERATIONS'] = max_iteration
    tprops['THRES_TRANSFIT'] = threshold_transmission_fit
    tprops['MIN_WATERCOL'] = min_watercol
    tprops['MAX_WATERCOL'] = max_watercol
    tprops['MIN_NUM_GOOD'] = min_number_good_points
    tprops['BTRANS_PERCENT'] = btrans_percentile
    tprops['NSIGCLIP'] = nsigclip
    tprops['TRANS_TMEDFILT'] = med_filt2
    tprops['SMALL_W_ERR'] = small_weight
    tprops['IMAGE_PIXEL_SIZE'] = tellu_med_sampling
    tprops['TAU_WATER_UPPER'] = tau_water_upper
    tprops['TAU_OTHER_LOWER'] = tau_others_lower
    tprops['TAU_OTHER_UPPER'] = tau_others_upper
    tprops['TAPAS_SMALL_NUM'] = tapas_small_number
    # set sources
    keys = ['DEFAULT_CWIDTH', 'FINER_CWIDTH', 'TEMP_MED_FILT',
            'DPARAM_THRES', 'MAX_ITERATIONS', 'THRES_TRANSFIT', 'MIN_WATERCOL',
            'MAX_WATERCOL', 'MIN_NUM_GOOD', 'BTRANS_PERCENT', 'NSIGCLIP',
            'TRANS_TMEDFILT', 'SMALL_W_ERR', 'IMAGE_PIXEL_SIZE',
            'TAU_WATER_UPPER', 'TAU_OTHER_LOWER', 'TAU_OTHER_UPPER',
            'TAPAS_SMALL_NUM']
    tprops.set_sources(keys, func_name)
    # return tprops
    return tprops

# =============================================================================
# Fit telluric functions
# =============================================================================
def gen_absorption_pca_calc(params, recipe, transfiles, fiber, **kwargs):
    func_name = __NAME__ + '.gen_absorption_pca_calc()'
    # ----------------------------------------------------------------------
    # get constants from params/kwargs
    npc = pcheck(params, 'FTELLU_NUM_PRINCIPLE_COMP', 'npc', kwargs, func_name)

    # ------------------------------------------------------------------
    # get the transmission map key
    out_trans = recipe.outputs['TELLU_MAP'].newcopy(recipe=recipe, fiber=fiber)
    # get key
    trans_key = out_trans.get_dbkey()

    # ----------------------------------------------------------------------
    # check that we have enough trans files for pca calculation (must be greater
    #     than number of principle components
    if len(transfiles) <= npc:
        # log and raise error: not enough tranmission maps to run pca analysis
        wargs = [trans_key, len(transfiles), npc, 'FTELLU_NUM_PRINCIPLE_COMP',
                 func_name]
        WLOG(params, 'error', TextEntry('09-019-00003', args=wargs))
    # ----------------------------------------------------------------------
    # check whether we can use pre-saved absorption map
    # ----------------------------------------------------------------------
    # get most recent file time
    recent_filetime = drs_path.get_most_recent(transfiles)
    # get new instance of ABSO_NPY file
    abso_npy = recipe.outputs['ABSO_NPY'].newcopy(recipe=recipe, fiber=fiber)
    # construct the filename from file instance
    abso_npy_filename = 'tellu_save_{0}.npy'.format(recent_filetime)
    abso_npy.construct_filename(params, filename=abso_npy_filename,
                                path=params['DRS_TELLU_DB'])
    # noinspection PyBroadException
    try:
        # try loading from file
        abso = np.load(abso_npy.filename)
    except Exception as e:
        # debug print out
        dargs = [abso_npy, type(e), e]
        # TODO: fill in error
        WLOG(params, 'debug', TextEntry('', args=dargs))






    return None


def shift_all_to_frame(params, **kwargs):
    func_name = __NAME__ + '.shift_all_to_frame()'
    # ------------------------------------------------------------------
    # get constants from params/kwargs
    # ------------------------------------------------------------------


    return None

def calc_recon_and_correct(params, **kwargs):
    func_name = __NAME__ + '.calc_recon_and_correct()'
    # ------------------------------------------------------------------
    # get constants from params/kwargs
    # ------------------------------------------------------------------


    return None


# =============================================================================
# QC and writing functions
# =============================================================================
def mk_tellu_quality_control(params, tprops, infile, **kwargs):

    func_name = __NAME__ + '.mk_tellu_quality_control()'
    # get parameters from params/kwargs
    snr_order = pcheck(params, 'QC_MK_TELLU_SNR_ORDER', 'snr_order', kwargs,
                       func_name)
    qc_snr_min = pcheck(params, 'QC_MK_TELLU_SNR_MIN', 'qc_snr_min', kwargs,
                        func_name)
    qc_airmass_diff = pcheck(params, 'QC_MKTELLU_AIRMASS_DIFF',
                             'qc_airmass_diff', kwargs, func_name)
    qc_min_watercol = pcheck(params, 'MKTELLU_TRANS_MIN_WATERCOL',
                             'qc_min_watercol', kwargs, func_name)
    qc_max_watercol = pcheck(params, 'MKTELLU_TRANS_MAX_WATERCOL',
                             'qc_min_watercol', kwargs, func_name)
    # get the text dictionary
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # get data from tprops
    transmission_map = tprops['TRANMISSION_MAP']
    image1 = tprops['IMAGE_OUT']
    calc_passed = tprops['PASSED']
    airmass = tprops['AIRMASS']
    recovered_airmass = tprops['RECOV_AIRMASS']
    recovered_water = tprops['RECOV_WATER']
    # set passed variable and fail message list
    fail_msg = []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
    # if array is completely NaNs it shouldn't pass
    if np.sum(np.isfinite(transmission_map)) == 0:
        fail_msg.append(textdict['40-019-00006'])
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append('NaN')
    qc_names.append('image')
    qc_logic.append('image is all NaN')
    # ----------------------------------------------------------------------
    # get SNR for each order from header
    nbo, nbpix = image1.shape
    snr = infile.read_header_key_1d_list('KW_EXT_SNR', nbo, dtype=float)
    # check that SNR is high enough
    if snr[snr_order] < qc_snr_min:
        fargs = [snr_order, snr[snr_order], qc_snr_min]
        fail_msg.append(textdict['40-019-00007'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(snr[snr_order])
    qc_name_str = 'SNR[{0}]'.format(snr_order)
    qc_names.append(qc_name_str)
    qc_logic.append('{0} < {1:.2f}'.format(qc_name_str, qc_snr_min))
    # ----------------------------------------------------------------------
    # check that the file passed the CalcTelluAbsorption sigma clip loop
    if not calc_passed:
        fargs = [infile.basename]
        fail_msg.append(textdict['40-019-00008'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(infile.basename)
    qc_names.append('FILE')
    qc_logic.append('FILE did not converge')
    # ----------------------------------------------------------------------
    # check that the airmass is not too different from input airmass
    airmass_diff = np.abs(recovered_airmass - airmass)
    if airmass_diff > qc_airmass_diff:
        fargs = [recovered_airmass, airmass, qc_airmass_diff]
        fail_msg.append(textdict['40-019-00009'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(airmass_diff)
    qc_names.append('airmass_diff')
    qc_logic.append('airmass_diff > {0:.2f}'.format(qc_airmass_diff))
    # ----------------------------------------------------------------------
    # check that the water vapor is within limits
    water_cond1 = recovered_water < qc_min_watercol
    water_cond2 = recovered_water > qc_max_watercol
    # check both conditions
    if water_cond1 or water_cond2:
        fargs = [qc_min_watercol, qc_max_watercol, recovered_water]
        fail_msg.append(textdict['40-019-00010'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # get args for qc_logic
    fargs = [qc_min_watercol, qc_max_watercol]
    # add to qc header lists
    qc_values.append(recovered_water)
    qc_names.append('RECOV_WATER')
    qc_logic.append('RECOV_WATER not between {0:.3f} & {1:.3f}'.format(*fargs))
    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #     quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params


def mk_tellu_write_trans_file(params, recipe, infile, rawfiles, fiber, combine,
                              tapas_props, wprops, nprops, tprops, qc_params):
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    transfile = recipe.outputs['TELLU_TRANS'].newcopy(recipe=recipe,
                                                      fiber=fiber)
    # construct the filename from file instance
    transfile.construct_filename(params, infile=infile)
    # ------------------------------------------------------------------
    # copy keys from input file
    transfile.copy_original_keys(infile)
    # add version
    transfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    transfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    transfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    transfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    transfile.add_hkey('KW_OUTPUT', value=transfile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    transfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add  calibration files used
    transfile.add_hkey('KW_CDBBLAZE', value=nprops['BLAZE_FILE'])
    transfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    # ----------------------------------------------------------------------
    # add qc parameters
    transfile.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # add telluric constants used
    if tprops['TEMPLATE_FLAG']:
        transfile.add_hkey('KW_MKTELL_TEMP_FILE', value=tprops['TEMPLATE_FILE'])
    else:
        transfile.add_hkey('KW_MKTELL_TEMP_FILE', value='None')
    # add blaze parameters
    transfile.add_hkey('KW_MKTELL_BLAZE_PRCT', value=nprops['BLAZE_PERCENTILE'])
    transfile.add_hkey('KW_MKTELL_BLAZE_CUT', value=nprops['BLAZE_CUT_NORM'])
    # add tapas parameteres
    transfile.add_hkey('KW_MKTELL_TAPASFILE', value=tapas_props['TAPAS_FILE'])
    transfile.add_hkey('KW_MKTELL_FWHMPLSF', value=tapas_props['FWHM_PIXEL_LSF'])
    # add tprops parameters
    transfile.add_hkey('KW_MKTELL_DEF_CONV_WID', value=tprops['DEFAULT_CWIDTH'])
    transfile.add_hkey('KW_MKTELL_FIN_CONV_WID', value=tprops['FINER_CWIDTH'])
    transfile.add_hkey('KW_MKTELL_TEMP_MEDFILT', value=tprops['TEMP_MED_FILT'])
    transfile.add_hkey('KW_MKTELL_DPARAM_THRES', value=tprops['DPARAM_THRES'])
    transfile.add_hkey('KW_MKTELL_MAX_ITER', value=tprops['MAX_ITERATIONS'])
    transfile.add_hkey('KW_MKTELL_THRES_TFIT', value=tprops['THRES_TRANSFIT'])
    transfile.add_hkey('KW_MKTELL_MIN_WATERCOL', value=tprops['MIN_WATERCOL'])
    transfile.add_hkey('KW_MKTELL_MAX_WATERCOL', value=tprops['MAX_WATERCOL'])
    transfile.add_hkey('KW_MKTELL_MIN_NUM_GOOD', value=tprops['MIN_NUM_GOOD'])
    transfile.add_hkey('KW_MKTELL_BTRANS_PERC', value=tprops['BTRANS_PERCENT'])
    transfile.add_hkey('KW_MKTELL_NSIGCLIP', value=tprops['NSIGCLIP'])
    transfile.add_hkey('KW_MKTELL_TRANS_TMFILT', value=tprops['TRANS_TMEDFILT'])
    transfile.add_hkey('KW_MKTELL_SMALL_W_ERR', value=tprops['SMALL_W_ERR'])
    transfile.add_hkey('KW_MKTELL_IM_PSIZE', value=tprops['IMAGE_PIXEL_SIZE'])
    transfile.add_hkey('KW_MKTELL_TAU_WATER_U', value=tprops['TAU_WATER_UPPER'])
    transfile.add_hkey('KW_MKTELL_TAU_OTHER_L', value=tprops['TAU_OTHER_LOWER'])
    transfile.add_hkey('KW_MKTELL_TAU_OTHER_U', value=tprops['TAU_OTHER_UPPER'])
    transfile.add_hkey('KW_MKTELL_TAPAS_SNUM', value=tprops['TAPAS_SMALL_NUM'])
    # ----------------------------------------------------------------------
    # save recovered airmass and water vapor
    transfile.add_hkey('KW_MKTELL_AIRMASS', value=tprops['RECOV_AIRMASS'])
    transfile.add_hkey('KW_MKTELL_WATER', value=tprops['RECOV_WATER'])
    # ----------------------------------------------------------------------
    # copy data
    transfile.data = tprops['TRANMISSION_MAP']
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', TextEntry('40-019-00011', args=[transfile.filename]))
    # write image to file
    transfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(transfile)
    # ------------------------------------------------------------------
    # return transmission file instance
    return transfile


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
    kernel = np.exp(-0.5 * (kernel / (fwhm_pixel_lsf / math.fwhm())) ** 2)
    # we only want an approximation of the absorption to find the continuum
    #    and estimate chemical abundances.
    #    there's no need for a varying kernel shape
    kernel /= np.nansum(kernel)
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
        tapas_spline = math.iuv_spline(lam, trans)
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
            cvalues = np.convolve(svalues, kernel, mode='same')
            # add to storage
            tapas_all_species[n_species, start: end] = cvalues
    # deal with non-real values (must be between 0 and 1
    tapas_all_species[tapas_all_species > 1] = 1
    tapas_all_species[tapas_all_species < 0] = 0

    # return tapas_all_species
    return tapas_all_species



def _calc_tapas_abso(keep, tau_water, tau_others, sp_water, sp_others,
                     tau_water_upper, tau_others_lower, tau_others_upper,
                     tapas_small_number):
    """
    generates a Tapas spectrum from the saved temporary .npy
    structure and scales with the given optical depth for
    water and all other absorbers

    as an input, we give a "keep" vector, values set to keep=0
    will be set to zero and not taken into account in the fitting
    algorithm

    """
    # line-of-sight optical depth for water cannot be negative
    if tau_water < 0:
        tau_water = 0
    # line-of-sight optical depth for water cannot be too big -
    #    set uppder threshold
    if tau_water > tau_water_upper:
        tau_water = tau_water_upper
    # line-of-sight optical depth for other absorbers cannot be less than
    #     one (that's zenith) keep the limit at 0.2 just so that the value
    #     gets propagated to header and leaves open the possibility that
    #     during the convergence of the algorithm, values go slightly
    #     below 1.0
    if tau_others < tau_others_lower:
        tau_others = tau_others_lower
    # line-of-sight optical depth for other absorbers cannot be greater than 5
    #     that would be an airmass of 5 and SPIRou cannot observe there
    if tau_others > tau_others_upper:
        tau_others = tau_others_upper

    # we will set to a fractional exponent, we cannot have values below zero
    #    for water
    water_zero = sp_water < 0
    sp_water[water_zero] = 0
    # for others
    others_zero = sp_others < 0
    sp_others[others_zero] = 0

    # calculate the tapas spectrum from absorbers
    sp = (sp_water ** tau_water) * (sp_others ** tau_others)

    # values not to be kept are set to a very low value
    sp[~keep.ravel()] = tapas_small_number

    # to avoid divisons by 0, we set values that are very low to 1e-9
    sp[sp < tapas_small_number] = tapas_small_number

    # return the tapas spectrum
    return sp





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

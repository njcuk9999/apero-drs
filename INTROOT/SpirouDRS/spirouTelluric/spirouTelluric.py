#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-12 16:28
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
import os
from scipy.ndimage import filters
from scipy.optimize import curve_fit
import warnings
import sys

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouImage
from SpirouDRS.spirouCore import spirouMath
from SpirouDRS.spirouCore.spirouMath import IUVSpline

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'obj_mk_tellu.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Custom parameter dictionary
ParamDict = spirouConfig.ParamDict
# Get plotting functions
sPlt = spirouCore.sPlt
# Get sigma FWHM
SIG_FWHM = spirouCore.spirouMath.fwhm()
# whether to plot debug plot per order
DEBUG_PLOT = False


# =============================================================================
# Define new mk_tellu functions
# =============================================================================
def apply_template(p, loc):
    func_name = __NAME__ + '.apply_template()'
    # get constants from p
    default_conv_width = p['MKTELLU_DEFAULT_CONV_WIDTH']
    finer_conv_width = p['MKTELLU_FINER_CONV_WIDTH']
    clean_orders = np.array(p['MKTELLU_CLEAN_ORDERS'])
    med_filt = p['MKTELLU_TEMPLATE_MED_FILTER']
    # get data from loc
    template = loc['TEMPLATE']
    wave = loc['WAVE']
    # get dimensions of data
    norders, npix = loc['SP'].shape
    # set the default convolution width for each order
    wconv = np.repeat(default_conv_width, norders).astype(float)

    # need to deal with when we don't have a template
    if not loc['FLAG_TEMPLATE']:
        # if we don't have a template, we assume that its 1 all over
        template = np.ones_like(loc['SP'])
        # check the clean orders are valid
        for clean_order in clean_orders:
            if (clean_order < 0) or (clean_order > norders):
                emsg1 = ('One of the orders in "TELLU_CLEAN_ORDESR" is out of '
                         'bounds')
                emsg2 = '\tOrders must be between 0 and {0}'.format(norders)
                WLOG(p, 'error', [emsg1, emsg2])
        # if we don't have a template, then we use a small kernel on
        # relatively "clean" orders
        wconv[clean_orders] = finer_conv_width
    # else we have a template so apply it
    else:
        # wavelength offset from BERV
        dvshift = spirouMath.relativistic_waveshift(loc['BERV'], units='km/s')
        # median-filter the template. we know that stellar features
        #    are very broad. this avoids having spurious noise in our templates
        # loop around each order
        for order_num in range(norders):
            # only keep non NaNs
            keep = np.isfinite(template[order_num])
            # apply median filter
            mfargs = [template[order_num, keep], med_filt]
            template[order_num, keep] = filters.median_filter(*mfargs)

        # loop around each order again
        for order_num in range(norders):
            # only keep non NaNs
            keep = np.isfinite(template[order_num])
            # if less than 50% of the order is considered valid, then set
            #     template value to 1 this only apply to the really contaminated
            #     orders
            if np.nansum(keep) > npix // 2:
                # get the wave and template masked arrays
                keepwave = wave[order_num, keep]
                keeptmp = template[order_num, keep]
                # spline the good values
                spline = IUVSpline(keepwave * dvshift, keeptmp, k=1, ext=3)
                # interpolate good values onto full array
                template[order_num] = spline(wave[order_num])
            else:
                template[order_num] = np.repeat(1.0, npix)
        # divide observed spectrum by template. This gets us close to the
        #    actual sky transmission. We will iterate on the exact shape of the
        #    SED by finding offsets of sp relative to 1 (after correcting form
        #    the TAPAS).
        loc['SP'] = loc['SP'] / template
    # add template and wconv to loc
    loc['TEMPLATE'] = template
    loc['WCONV'] = wconv
    # set the source
    loc.set_sources(['SP', 'TEMPLATE', 'WCONV'], func_name)
    # return loc
    return loc


def calculate_telluric_absorption(p, loc):
    func_name = __NAME__ + 'calculate_telluric_absorption()'
    # get parameters from p
    dparam_threshold = p['MKTELLU_DPARAM_THRES']
    maximum_iteration = p['MKTELLU_MAX_ITER']
    threshold_transmission_fit = p['MKTELLU_THRES_TRANSFIT']
    transfit_upper_bad = p['MKTELLU_TRANS_FIT_UPPER_BAD']
    min_watercol = p['MKTELLU_TRANS_MIN_WATERCOL']
    max_watercol = p['MKTELLU_TRANS_MAX_WATERCOL']
    min_number_good_points = p['MKTELLU_TRANS_MIN_NUM_GOOD']
    btrans_percentile = p['MKTELLU_TRANS_TAU_PERCENTILE']
    nsigclip = p['MKTELLU_TRANS_SIGMA_CLIP']
    med_filt = p['MKTELLU_TRANS_TEMPLATE_MEDFILT']
    small_weight = p['MKTELLU_SMALL_WEIGHTING_ERROR']
    tellu_med_sampling = p['MKTELLU_MED_SAMPLING']
    plot_order_nums = p['MKTELLU_PLOT_ORDER_NUMS']

    # get data from loc
    airmass = loc['AIRMASS']
    wave = loc['WAVE']
    sp = np.array(loc['SP'])
    wconv = loc['WCONV']
    # get dimensions of data
    norders, npix = loc['SP'].shape

    # define function for curve_fit
    def tapas_fit(keep, tau_water, tau_others):
        return calc_tapas_abso(p, loc, keep, tau_water, tau_others)

    # starting point for the optical depth of water and other gasses
    guess = [airmass, airmass]

    # first estimate of the absorption spectrum
    tau1 = tapas_fit(np.isfinite(wave), guess[0], guess[1])
    tau1 = tau1.reshape(sp.shape)

    # first guess at the SED estimate for the hot start (we guess with a
    #   spectrum full of ones
    sed = np.ones_like(wave)

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
    cond2 = iteration < maximum_iteration
    cond3 = not fail

    # set up empty arrays
    sp3_arr = np.zeros((norders, npix), dtype=float)
    sed_update_arr = np.zeros(npix, dtype=float)
    keep = np.zeros(npix, dtype=bool)

    # loop around until one condition not met
    while cond1 and cond2 and cond3:
        # ---------------------------------------------------------------------
        # previous guess
        prev_guess = np.array(guess)
        # ---------------------------------------------------------------------
        # we have an estimate of the absorption spectrum
        fit_sp = sp / sed
        # ---------------------------------------------------------------------
        # some masking of NaN regions
        nanmask = ~np.isfinite(fit_sp)
        fit_sp[nanmask] = 0
        # ---------------------------------------------------------------------
        # vector used to mask invalid regions
        keep = fit_sp != 0
        # only fit where the transmission is greater than a certain value
        keep &= tau1 > threshold_transmission_fit
        # considered bad if the spectrum is larger than '. This is
        #     likely an OH line or a cosmic ray
        keep &= fit_sp < transfit_upper_bad
        # ---------------------------------------------------------------------
        # fit telluric absorption of the spectrum
        with warnings.catch_warnings(record=True) as _:
            popt, pcov = curve_fit(tapas_fit, keep, fit_sp.ravel(), p0=guess)
        # update our guess
        guess = np.array(popt)
        # ---------------------------------------------------------------------
        # if our tau_water guess is bad fail
        if (guess[0] < min_watercol) or (guess[0] > max_watercol):
            wmsg = ('Recovered water vapor optical depth not between {0:.2f} '
                    'and {1:.2f}')
            WLOG(p, 'warning', wmsg.format(min_watercol, max_watercol))
            fail = True
            break
        # ---------------------------------------------------------------------
        # we will use a stricter condition later, but for all steps
        #    we expect an agreement within an airmass difference of 1
        if np.abs(guess[1] - airmass) > 1:
            wmsg = ('Recovered optical depth of others too diffferent from '
                    'airmass (airmass={0:.3f} recovered depth={1:.3f})')
            WLOG(p, 'warning', wmsg.format(airmass, guess[1]))
            fail = True
            break
        # ---------------------------------------------------------------------
        # calculate how much the optical depth params change
        dparam = np.sqrt(np.nansum((guess - prev_guess) ** 2))
        # ---------------------------------------------------------------------
        # print progress
        wmsg = ('Iteration {0}/{1} H20 depth: {2:.4f} Other gases depth: '
                '{3:.4f} Airmass: {4:.4f}')
        wmsg2 = '\tConvergence parameter: {0:.4f}'.format(dparam)
        wargs = [iteration, maximum_iteration, guess[0], guess[1], airmass]
        WLOG(p, '', [wmsg.format(*wargs), wmsg2])
        # ---------------------------------------------------------------------
        # get current best-fit spectrum
        tau1 = tapas_fit(np.isfinite(wave), guess[0], guess[1])
        tau1 = tau1.reshape(sp.shape)
        # ---------------------------------------------------------------------
        # for each order, we fit the SED after correcting for absorption
        for order_num in range(norders):
            # -----------------------------------------------------------------
            # get the per-order spectrum divided by best guess
            sp2 = sp[order_num] / tau1[order_num]
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
                norm = np.nanmedian(sp2[best_trans])
            else:
                norm = np.ones_like(sp2)
            # -----------------------------------------------------------------
            # normalise this orders spectrum
            sp[order_num] = sp[order_num] / norm
            # normalise sp2 and the sed
            sp2 = sp2 / norm
            sed[order_num] = sed[order_num] / norm
            # -----------------------------------------------------------------
            # find far outliers to the SED for sigma-clipping
            with warnings.catch_warnings(record=True) as _:
                res = sp2 - sed[order_num]
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
            sp2[~good] = np.nan
            # sp3 is a median-filtered version of sp2 where pixels that have
            #     a transmission that is too low are clipped.
            sp3 = filters.median_filter(sp2 - sed[order_num], med_filt)
            sp3 = sp3 + sed[order_num]
            # find all the NaNs and set to zero
            nanmask = ~np.isfinite(sp3)
            sp3[nanmask] = 0.0
            # also set zero pixels in sp3 to be non-good pixels in "good"
            good[sp3 == 0.0] = False
            # -----------------------------------------------------------------
            # we smooth sp3 with a kernel. This kernel has to be small
            #    enough to preserve stellar features and large enough to
            #    subtract noise this is why we have an order-dependent width.
            #    the stellar lines are expected to be larger than 200km/s,
            #    so a kernel much smaller than this value does not make sense
            ew = wconv[order_num] / tellu_med_sampling / spirouMath.fwhm()
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
            spconv = np.convolve(sp3 * good, kernal_y, mode='same')
            # update the sed
            with warnings.catch_warnings(record=True) as _:
                sed_update = spconv / ww1
            # set all small values to 1% to avoid small weighting errors
            sed_update[ww1 < small_weight] = np.nan

            if wconv[order_num] == p['MKTELLU_FINER_CONV_WIDTH']:
                rms_limit = 0.1
            else:
                rms_limit = 0.3

            # iterate around and sigma clip
            for iteration_sig_clip_good in range(1, 6):

                with warnings.catch_warnings(record=True) as _:
                    residual_SED = sp3 - sed_update
                    residual_SED[~good] = np.nan

                rms = np.abs(residual_SED)

                with warnings.catch_warnings(record=True) as _:
                    good[rms > (rms_limit / iteration_sig_clip_good)] = 0

                # ---------------------------------------------------------
                # construct a weighting matrix for the sed
                ww1 = np.convolve(good, kernal_y, mode='same')
                # need to weight the spectrum accordingly
                spconv = np.convolve(sp3 * good, kernal_y, mode='same')
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
                zero_point = np.nanmedian(sp[order_num, pedestal])
                # if zero_point is finite subtract it off the spectrum
                if np.isfinite(zero_point):
                    sp[order_num] -= zero_point
            # -----------------------------------------------------------------
            # update the sed
            sed[order_num] = sed_update
            # append sp3
            sp3_arr[order_num] = np.array(sp3)
            # -----------------------------------------------------------------
            # debug plot
            if p['DRS_PLOT'] and p['DRS_DEBUG'] and DEBUG_PLOT and not skip:
                # plot only every 10 iterations
                if iteration == 10:
                    # plot the transmission map plot
                    pargs = [order_num, wave, tau1, sp, sp3,
                             sed, sed_update, keep]
                    sPlt.mk_tellu_wave_flux_plot(p, *pargs)
                    # get user input to continue or skip
                    imsg = 'Press [Enter] for next or [s] for skip:\t'
                    uinput = input(imsg)
                    if 's' in uinput.lower():
                        skip = True
                    # close plot
                    sPlt.plt.close()
        # ---------------------------------------------------------------------
        # update the iteration number
        iteration += 1
        # ---------------------------------------------------------------------
        # update while parameters
        cond1 = dparam > dparam_threshold
        cond2 = iteration < maximum_iteration
        cond3 = not fail
    # ---------------------------------------------------------------------
    if p['DRS_PLOT'] and p['DRS_DEBUG'] and not DEBUG_PLOT:
        # if plot orders is 'all' plot all
        if plot_order_nums == 'all':
            plot_order_nums = np.arange(norders).astype(int)
            # start non-interactive plot
            sPlt.plt.ioff()
            off = True
        else:
            sPlt.plt.ion()
            off = False
        # loop around the orders to show
        for order_num in plot_order_nums:
            pargs = [order_num, wave, tau1, sp, sp3_arr[order_num], sed,
                     sed[order_num], keep]
            sPlt.mk_tellu_wave_flux_plot(p, *pargs)
        if off:
            sPlt.plt.ion()

    # return values via loc
    loc['PASSED'] = not fail
    loc['RECOV_AIRMASS'] = guess[1]
    loc['RECOV_WATER'] = guess[0]
    loc['SP_OUT'] = sp
    loc['SED_OUT'] = sed
    # update source
    sources = ['PASSED', 'RECOV_AIRMASS', 'RECOV_WATER', 'SP_OUT', 'SED_OUT']
    loc.set_sources(sources, func_name)
    # return loc
    return loc


# =============================================================================
# Define telluric db functions
# =============================================================================
def update_process(p, title, objname, i1, t1, i2, t2):
    msg1 = '{0}: Processing object = {1} ({2}/{3})'
    msg2 = '\tObject {0} of {1}'
    wmsgs = ['', '=' * 60, '', msg1.format(title, objname, i1 + 1, t1),
             msg2.format(i2 + 1, t2), '', '=' * 60, '', ]
    WLOG(p, 'info', wmsgs, wrap=False)


def get_arguments(p, absfilename):
    # reset sys.argv
    sys.argv = []
    # get constants from p
    path = p['ARG_FILE_DIR']
    # get relative path
    relpath = absfilename.split(path)[-1]
    # get night name
    night_name = os.path.dirname(relpath)
    # get filename
    filename = os.path.basename(relpath)
    # run dict
    return dict(night_name=night_name, files=[filename])



def find_telluric_stars(p):
    # get parameters from p
    path = p['ARG_FILE_DIR']
    filetype = p['FILETYPE']
    allowedtypes = p['TELLU_DB_ALLOWED_OUTPUT']
    ext_types = p['TELLU_DB_ALLOWED_EXT_TYPE']
    # -------------------------------------------------------------------------
    # get the list of whitelist files
    tell_names = get_whitelist()
    # -------------------------------------------------------------------------
    # check file type is allowed
    if filetype not in allowedtypes:
        emsgs = ['Invalid file type = {0}'.format(filetype),
                 '\t Must be one of the following']
        for allowedtype in allowedtypes:
            emsgs.append('\t\t - "{0}"'.format(allowedtype))
    # -------------------------------------------------------------------------
    # get index files
    index_files = []
    # walk through path and find index files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == spirouConfig.Constants.INDEX_OUTPUT_FILENAME():
                index_files.append(os.path.join(root, filename))

    # log number of index files found
    if len(index_files) > 0:
        wmsg = 'Found {0} index files'
        WLOG(p, '', wmsg.format(len(index_files)))
    else:
        emsg = ('No index files found. Please run a off_listing script to '
                'continue')
        WLOG(p, 'error', emsg)
    # -------------------------------------------------------------------------
    # valid files dictionary (key = telluric object name)
    valid_files = dict()
    # loop around telluric names
    for tell_name in tell_names:
        # ---------------------------------------------------------------------
        # log progress
        wmsg = 'Searching for telluric star: "{0}"'
        WLOG(p, '', wmsg.format(tell_name))

        # storage for this objects files
        valid_obj_files = []
        # ---------------------------------------------------------------------
        # loop through index files
        for index_file in index_files:
            # read index file
            index = spirouImage.ReadFitsTable(p, index_file)
            # get directory
            dirname = os.path.dirname(index_file)
            # -----------------------------------------------------------------
            # get filename and object name
            index_filenames = index['FILENAME']
            index_objnames = index['OBJNAME']
            index_output = index[p['KW_OUTPUT'][0]]
            index_ext_type = index[p['KW_EXT_TYPE'][0]]
            # -----------------------------------------------------------------
            # mask by objname
            mask1 = index_objnames == tell_name
            # mask by KW_OUTPUT
            mask2 = index_output == filetype
            # mask by KW_EXT_TYPE
            mask3 = np.zeros(len(index), dtype=bool)
            for ext_type in ext_types:
                mask3 |= (index_ext_type == ext_type)
            # combine masks
            mask = mask1 & mask2 & mask3
            # -----------------------------------------------------------------
            # append found files to this list
            if np.nansum(mask) > 0:
                for filename in index_filenames[mask]:
                    # construct absolute path
                    absfilename = os.path.join(dirname, filename)
                    # check that file exists
                    if not os.path.exists(absfilename):
                        continue
                    # append to storage
                    if filename not in valid_obj_files:
                        valid_obj_files.append(absfilename)
        # ---------------------------------------------------------------------
        # log found
        wmsg = '\tFound {0} objects'.format(len(valid_obj_files))
        WLOG(p, '', wmsg)
        # ---------------------------------------------------------------------
        # append to full dictionary
        if len(valid_obj_files) > 0:
            valid_files[tell_name] = valid_obj_files
    # return full list
    return valid_files


def find_objects(p):
    path = p['ARG_FILE_DIR']
    filetype = p['FILETYPE']
    allowedtypes = p['TELLU_DB_ALLOWED_OUTPUT']
    ext_types = p['TELLU_DB_ALLOWED_EXT_TYPE']

    # strip objects
    if p['OBJECTS'] == 'None':
        object_mask = []
    else:
        object_mask = []

        if type(p['OBJECTS']) is str:
            p['OBJECTS'] = p['OBJECTS'].split(',')

        for objname in p['OBJECTS']:
            object_mask.append(objname.strip().upper())

    # -------------------------------------------------------------------------
    # check file type is allowed
    if filetype not in allowedtypes:
        emsgs = ['Invalid file type = {0}'.format(filetype),
                 '\t Must be one of the following']
        for allowedtype in allowedtypes:
            emsgs.append('\t\t - "{0}"'.format(allowedtype))
    # -------------------------------------------------------------------------
    # get index files
    index_files = []
    # walk through path and find index files
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename == spirouConfig.Constants.INDEX_OUTPUT_FILENAME():
                index_files.append(os.path.join(root, filename))
    # log number of index files found
    if len(index_files) > 0:
        wmsg = 'Found {0} index files'
        WLOG(p, '', wmsg.format(len(index_files)))
    else:
        emsg = ('No index files found. Please run a off_listing script to '
                'continue')
        WLOG(p, 'error', emsg)
    # -------------------------------------------------------------------------
    # valid files dictionary (key = telluric object name)
    valid_files = dict()
    # loop through index files
    for index_file in index_files:
        # read index file
        index = spirouImage.ReadFitsTable(p, index_file)
        # get directory
        dirname = os.path.dirname(index_file)
        # get filename and object name
        index_filenames = index['FILENAME']
        index_objnames = index['OBJNAME']
        index_output = index[p['KW_OUTPUT'][0]]
        index_ext_type = index[p['KW_EXT_TYPE'][0]]
        # ---------------------------------------------------------------------
        # mask by KW_OUTPUT
        mask1 = index_output == filetype
        # mask by KW_EXT_TYPE
        mask2 = np.zeros(len(index), dtype=bool)
        for ext_type in ext_types:
            mask2 |= (index_ext_type == ext_type)
        # combine masks
        mask = mask1 & mask2
        # ---------------------------------------------------------------------
        if np.nansum(mask) > 0:
            # set valid to False
            valid = False
            # loop around rows that are in mask
            for it in range(len(index_filenames[mask])):
                # get object name
                objname_it = index_objnames[mask][it]
                filename_it = index_filenames[mask][it]
                # construct absolute path
                absfilename = os.path.join(dirname, filename_it)
                # filter by object type
                if len(object_mask) > 0:
                    if objname_it.strip().upper() in object_mask:
                        valid = True
                    else:
                        valid = False
                else:
                    valid = True
                # if valid add filename to valid list
                if valid:
                    if objname_it in valid_files:
                        valid_files[objname_it].append(absfilename)
                    else:
                        valid_files[objname_it] = [absfilename]
    # -------------------------------------------------------------------------
    # return full list of valid files
    return valid_files


# =============================================================================
# Define other functions
# =============================================================================
def calc_tapas_abso(p, loc, keep, tau_water, tau_others):
    """
    generates a Tapas spectrum from the saved temporary .npy
    structure and scales with the given optical depth for
    water and all other absorbers

    as an input, we give a "keep" vector, values set to keep=0
    will be set to zero and not taken into account in the fitting
    algorithm

    """
    # get constants from p
    tau_water_upper = p['MKTELLU_TAU_WATER_ULIMIT']
    tau_others_lower = p['MKTELLU_TAU_OTHER_LLIMIT']
    tau_others_upper = p['MKTELLU_TAU_OTHER_ULIMIT']
    tapas_small_number = p['MKTELLU_SMALL_LIMIT']

    # get data from loc
    sp_water = np.array(loc['TAPAS_WATER'])
    sp_others = np.array(loc['TAPAS_OTHERS'])

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


def get_normalized_blaze(p, loc, hdr):
    func_name = __NAME__ + '.get_normalized_blaze()'
    # Get the blaze
    p, blaze = spirouImage.ReadBlazeFile(p, hdr)
    # we mask domains that have <20% of the peak blaze of their respective order
    blaze_norm = np.array(blaze)
    for iord in range(blaze.shape[0]):
        blaze_norm[iord, :] /= np.nanpercentile(blaze_norm[iord, :],
                                                p['TELLU_BLAZE_PERCENTILE'])

    with warnings.catch_warnings(record=True) as _:
        blaze_norm[blaze_norm < p['TELLU_CUT_BLAZE_NORM']] = np.nan
    # add to loc
    loc['BLAZE'] = blaze
    loc['NBLAZE'] = blaze_norm
    loc.set_sources(['BLAZE', 'NBLAZE'], func_name)
    # return loc
    return p, loc


def construct_convolution_kernal1(p, loc):
    func_name = __NAME__ + '.construct_convolution_kernal()'
    # get the number of kernal pixels
    npix_ker = int(np.ceil(3 * p['FWHM_PIXEL_LSF'] * 3.0 / 2) * 2 + 1)
    # set up the kernel exponent
    ker = np.arange(npix_ker) - npix_ker // 2
    # kernal is the a gaussian
    ker = np.exp(-0.5 * (ker / (p['FWHM_PIXEL_LSF'] / SIG_FWHM)) ** 2)
    # we only want an approximation of the absorption to find the continuum
    #    and estimate chemical abundances.
    #    there's no need for a varying kernel shape
    ker /= np.nansum(ker)
    # add to loc
    loc['KER'] = ker
    loc.set_source('KER', func_name)
    # return loc
    return loc


def construct_big_table(p, loc):
    # get choosen order
    snr_order = p['QC_FIT_TELLU_SNR_ORDER']

    colnames = ['RowNum', 'Filename', 'OBJNAME', 'OBJECT', 'BERV', 'WAVEFILE',
                'SNR_{0}'.format(snr_order), 'DATE', 'VERSION', 'DARKFILE',
                'BADFILE', 'LOCOFILE', 'BLAZEFILE', 'FLATFILE', 'SHAPEFILE']

    columns = ['BASE_ROWNUM', 'BASE_FILELIST', 'BASE_OBJNAME', 'BASE_OBJECT',
               'BASE_BERVLIST', 'BASE_WAVELIST',
               'BASE_SNRLIST_{0}'.format(snr_order), 'BASE_DATELIST',
               'BASE_VERSION', 'BASE_DARKFILE', 'BASE_BADFILE',
               'BASE_LOCOFILE', 'BASE_BLAZFILE',
               'BASE_FLATFILE', 'BASE_SHAPEFILE']
    # get values from loc
    values = []
    for col in columns:
        values.append(loc[col])
    # construct table
    newtable = spirouImage.MakeTable(p, colnames, values)
    # return table
    return newtable


def get_molecular_tell_lines(p, loc):
    func_name = __NAME__ + '.get_molecular_tell_lines()'
    # get x and y dimension
    ydim, xdim = loc['DATA'].shape
    # representative atmospheric transmission
    # tapas = pyfits.getdata('tapas_model.fits')
    tapas_file = spirouDB.GetDatabaseTellMole(p)
    tdata = spirouImage.ReadImage(p, tapas_file, kind='TAPAS')
    tapas, thdr, _, _ = tdata

    # load all current telluric convolve files
    convolve_files = spirouDB.GetDatabaseTellConv(p, required=False)

    # tapas spectra resampled onto our data wavelength vector
    tapas_all_species = np.zeros([len(p['TELLU_ABSORBERS']), xdim * ydim])

    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # read master wave map
    masterwavefile = spirouDB.GetDatabaseMasterWave(p, required=True)
    wave_file = os.path.basename(masterwavefile)
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=masterwavefile,
                                       return_wavemap=True, quiet=True,
                                       return_header=True, fiber=wave_fiber)
    masterwavep, masterwave, masterwaveheader, mwsource = mout

    # get the convolve file names
    convolve_file_name = wave_file.replace('.fits', '_tapas_convolved.npy')
    convolve_file = os.path.join(p['ARG_FILE_DIR'], convolve_file_name)

    convolve_basefiles = []
    for cfile in np.unique(convolve_files):
        convolve_basefiles.append(os.path.basename(cfile))

    # find tapas file in files
    if os.path.basename(convolve_file) not in convolve_basefiles:
        generate = True
    else:
        # if we already have a file for this wavelength just open it
        # noinspection PyBroadException
        try:
            # load with numpy
            tapas_all_species = np.load(convolve_file)
            # log loading
            wmsg = 'Loading Tapas convolve file: {0}'
            WLOG(p, '', wmsg.format(convolve_file_name))
            # add name to loc
            loc['TAPAS_FNAME'], loc['TAPAS_ABSNAME'] = None, None
            generate = False
        # if we don't have a tapas file for this wavelength soltuion
        #     calculate it
        except Exception:
            generate = True
    # if we don't have tapas_all_species generate
    if generate:
        # loop around each molecule in the absorbers list
        #    (must be in
        for n_species, molecule in enumerate(p['TELLU_ABSORBERS']):
            # log process
            wmsg = 'Processing molecule: {0}'
            WLOG(p, '', wmsg.format(molecule))
            # get wavelengths
            lam = tapas['wavelength']
            # get molecule transmission
            trans = tapas['trans_{0}'.format(molecule)]
            # interpolate with Univariate Spline
            tapas_spline = IUVSpline(lam, trans)
            # log the mean transmission level
            wmsg = '\tMean Trans level: {0:.3f}'.format(np.mean(trans))
            WLOG(p, '', wmsg)
            # convolve all tapas absorption to the SPIRou approximate resolution
            for iord in range(ydim):
                # get the order position
                start = iord * xdim
                end = (iord * xdim) + xdim
                # interpolate the values at these points
                svalues = tapas_spline(masterwave[iord, :])
                # convolve with a gaussian function
                cvalues = np.convolve(svalues, loc['KER'], mode='same')
                # add to storage
                tapas_all_species[n_species, start: end] = cvalues
        # deal with non-real values (must be between 0 and 1
        tapas_all_species[tapas_all_species > 1] = 1
        tapas_all_species[tapas_all_species < 0] = 0
        # save the file
        np.save(convolve_file, tapas_all_species)
        # add name to loc
        loc['TAPAS_ABSNAME'] = convolve_file
        loc['TAPAS_FNAME'] = os.path.basename(convolve_file)
    # finally add all species to loc
    loc['TAPAS_ALL_SPECIES'] = tapas_all_species
    # add sources
    skeys = ['TAPAS_ALL_SPECIES', 'TAPAS_FNAME']
    loc.set_sources(skeys, func_name)
    # return loc
    return loc


def construct_convolution_kernal2(p, loc, vsini):
    func_name = __NAME__ + '.construct_convolution_kernal2()'

    # gaussian ew for vinsi km/s
    ew = vsini / p['TELLU_MED_SAMPLING'] / SIG_FWHM
    # set up the kernel exponent
    xx = np.arange(ew * 6) - ew * 3
    # kernal is the a gaussian
    ker2 = np.exp(-.5 * (xx / ew) ** 2)

    ker2 /= np.nansum(ker2)
    # add to loc
    loc['KER2'] = ker2
    loc.set_source('KER2', func_name)
    # return loc
    return loc


def calculate_absorption_pca(p, loc, x, mask):
    func_name = __NAME__ + '.calculate_absorption_pca()'
    # get constants from p
    npc = p['TELLU_NUMBER_OF_PRINCIPLE_COMP']

    # get eigen values
    eig_u, eig_s, eig_vt = np.linalg.svd(x[:, mask], full_matrices=False)

    # if we are adding the derivatives to the pc need extra components
    if p['ADD_DERIV_PC']:
        # the npc+1 term will be the derivative of the first PC
        # the npc+2 term will be the broadning factor the first PC
        pc = np.zeros([np.product(loc['DATA'].shape), npc + 2])
    else:
        # create pc image
        pc = np.zeros([np.product(loc['DATA'].shape), npc])

    # fill pc image
    with warnings.catch_warnings(record=True) as _:
        for it in range(npc):
            for jt in range(x.shape[0]):
                pc[:, it] += eig_u[jt, it] * x[jt, :]

    # if we are adding the derivatives add them now
    if p['ADD_DERIV_PC']:
        # first extra is the first derivative
        pc[:, npc] = np.gradient(pc[:, 0])
        # second extra is the second derivative
        pc[:, npc + 1] = np.gradient(np.gradient(pc[:, 0]))
        # number of components is two longer now
        npc += 2

    # if we are fitting the derivative change the fit parameter
    if p['FIT_DERIV_PC']:
        fit_pc = np.gradient(pc, axis=0)
    # else we are fitting the principle components themselves
    else:
        fit_pc = np.array(pc)

    # save pc image to loc
    loc['PC'] = pc
    loc['NPC'] = npc
    loc['FIT_PC'] = fit_pc
    loc.set_sources(['PC', 'NPC', 'FIT_PC'], func_name)
    # return loc
    return loc


def get_berv_value(p, hdr, filename=None):
    # deal with no filename
    if filename is None:
        if '@@@fname' in hdr:
            filename = hdr['@@@fname']
        else:
            filename = 'UNKNOWN'

    # Check for BERV key in header
    if p['KW_BERV'][0] not in hdr:
        emsg = 'HEADER error, file="{0}". Keyword {1} not found'
        eargs = [filename, p['KW_BERV'][0]]
        WLOG(p, 'error', emsg.format(*eargs))
        dv, bjd, bvmax = 0.0, -9999, 0.0
    else:
        # Get the Barycentric correction from header
        dv = float(hdr[p['KW_BERV'][0]])
        bjd = float(hdr[p['KW_BJD'][0]])
        bvmax = float(hdr[p['KW_BERV_MAX'][0]])
    # return dv, bjd, dvmax
    return dv, bjd, bvmax


def berv_correct_template(p, loc, thdr):
    func_name = __NAME__ + '.interp_at_shifted_wavelengths()'
    # Get the Barycentric correction from header
    dv, _, _ = get_berv_value(p, thdr)
    # set up storage for template
    template2 = np.zeros(np.product(loc['DATA'].shape))
    ydim, xdim = loc['DATA'].shape
    # loop around orders
    for order_num in range(ydim):
        # find good (not NaN) pixels
        keep = np.isfinite(loc['TEMPLATE'][order_num, :])
        # if we have enough values spline them
        if np.nansum(keep) > p['TELLU_FIT_KEEP_FRAC']:
            # define keep wave
            keepwave = loc['MASTERWAVE'][order_num, keep]
            # define keep temp
            keeptemp = loc['TEMPLATE'][order_num, keep]
            # calculate interpolation for keep temp at keep wave
            spline = IUVSpline(keepwave, keeptemp, ext=3)
            # interpolate at shifted values
            dvshift = spirouMath.relativistic_waveshift(dv, units='km/s')
            waveshift = loc['MASTERWAVE'][order_num, :] * dvshift
            # interpolate at shifted wavelength
            start = order_num * xdim
            end = order_num * xdim + xdim
            template2[start:end] = spline(waveshift)

    # save to loc
    loc['TEMPLATE2'] = template2
    loc.set_source('TEMPLATE2', func_name)
    # return loc
    return loc


def calc_recon_abso(p, loc):
    func_name = __NAME__ + '.calc_recon_abso()'
    # get data from loc
    sp = loc['sp']
    tapas_all_species = loc['TAPAS_ALL_SPECIES']
    amps_abso_total = loc['AMPS_ABSOL_TOTAL']
    # get data dimensions
    ydim, xdim = loc['DATA'].shape
    # redefine storage for recon absorption
    recon_abso = np.ones(np.product(loc['DATA'].shape))
    # flatten spectrum and wavelengths
    sp2 = sp.ravel()
    wave2 = loc['WAVE_IT'].ravel()
    # define the good pixels as those above minimum transmission
    with warnings.catch_warnings(record=True) as _:
        keep = tapas_all_species[0, :] > p['TELLU_FIT_MIN_TRANSMISSION']
    # also require wavelength constraints
    keep &= (wave2 > p['TELLU_LAMBDA_MIN'])
    keep &= (wave2 < p['TELLU_LAMBDA_MAX'])
    # construct convolution kernel
    loc = construct_convolution_kernal2(p, loc, p['TELLU_FIT_VSINI'])
    # ------------------------------------------------------------------
    # loop around a number of times
    template2 = None
    for ite in range(p['TELLU_FIT_NITER']):
        # log progress
        wmsg = 'Iteration {0} of {1}'.format(ite + 1, p['TELLU_FIT_NITER'])
        WLOG(p, '', wmsg)

        # --------------------------------------------------------------
        # if we don't have a template construct one
        if not loc['FLAG_TEMPLATE']:
            # define template2 to fill
            template2 = np.zeros(np.product(loc['DATA'].shape))
            # loop around orders
            for order_num in range(ydim):
                # get start and end points
                start = order_num * xdim
                end = order_num * xdim + xdim
                # produce a mask of good transmission
                order_tapas = tapas_all_species[0, start:end]
                with warnings.catch_warnings(record=True) as _:
                    mask = order_tapas > p['TRANSMISSION_CUT']
                # get good transmission spectrum
                spgood = sp[order_num, :] * np.array(mask, dtype=float)
                recongood = recon_abso[start:end]
                # convolve spectrum
                ckwargs = dict(v=loc['KER2'], mode='same')
                sp2b = np.convolve(spgood / recongood, **ckwargs)
                # convolve mask for weights
                ww = np.convolve(np.array(mask, dtype=float), **ckwargs)
                # wave weighted convolved spectrum into template2
                with warnings.catch_warnings(record=True) as _:
                    template2[start:end] = sp2b / ww
        # else we have template so load it
        else:
            template2 = loc['TEMPLATE2']
            # -----------------------------------------------------------------
            # Shift the template to correct frame
            # -----------------------------------------------------------------
            # log process
            wmsg1 = '\tShifting template on to master wavelength grid'
            wargs = [os.path.basename(loc['MASTERWAVEFILE'])]
            wmsg2 = '\t\tFile = {0}'.format(*wargs)
            WLOG(p, '', [wmsg1, wmsg2])
            # shift template
            wargs = [p, template2, loc['MASTERWAVE'], loc['WAVE_IT']]
            template2 = wave2wave(*wargs, reshape=True).reshape(template2.shape)
        # --------------------------------------------------------------
        # get residual spectrum
        with warnings.catch_warnings(record=True) as _:
            resspec = (sp2 / template2) / recon_abso
        # --------------------------------------------------------------
        if loc['FLAG_TEMPLATE']:
            # construct convolution kernel
            vsini = p['TELLU_FIT_VSINI2']
            loc = construct_convolution_kernal2(p, loc, vsini)
            # loop around orders
            for order_num in range(ydim):
                # get start and end points
                start = order_num * xdim
                end = order_num * xdim + xdim
                # catch NaN warnings and ignore
                with warnings.catch_warnings(record=True) as _:
                    # produce a mask of good transmission
                    order_tapas = tapas_all_species[0, start:end]
                    mask = order_tapas > p['TRANSMISSION_CUT']
                    fmask = np.array(mask, dtype=float)
                    # get good transmission spectrum
                    resspecgood = resspec[start:end] * fmask
                    recongood = recon_abso[start:end]
                # convolve spectrum
                ckwargs = dict(v=loc['KER2'], mode='same')
                with warnings.catch_warnings(record=True) as _:
                    sp2b = np.convolve(resspecgood / recongood, **ckwargs)
                # convolve mask for weights
                ww = np.convolve(np.array(mask, dtype=float), **ckwargs)
                # wave weighted convolved spectrum into dd
                with warnings.catch_warnings(record=True) as _:
                    resspec[start:end] = resspec[start:end] / (sp2b / ww)
        # --------------------------------------------------------------
        # Log dd and subtract median
        # log dd
        with warnings.catch_warnings(record=True) as _:
            log_resspec = np.log(resspec)
        # --------------------------------------------------------------
        # subtract off the median from each order
        for order_num in range(ydim):
            # get start and end points
            start = order_num * xdim
            end = order_num * xdim + xdim
            # skip if whole order is NaNs
            if np.nansum(np.isfinite(log_resspec[start:end])) == 0:
                continue
            # get median
            log_resspec_med = np.nanmedian(log_resspec[start:end])
            # subtract of median
            log_resspec[start:end] = log_resspec[start:end] - log_resspec_med
        # --------------------------------------------------------------
        # set up fit
        if p['FIT_DERIV_PC']:
            fit_dd = np.gradient(log_resspec)
        else:
            fit_dd = np.array(log_resspec)
        # --------------------------------------------------------------
        # identify good pixels to keep
        keep &= np.isfinite(fit_dd)
        keep &= np.nansum(np.isfinite(loc['FIT_PC']), axis=1) == loc['NPC']
        # log number of kept pixels
        wmsg = '\tNumber to keep total = {0}'.format(np.nansum(keep))
        WLOG(p, '', wmsg)
        # --------------------------------------------------------------
        # calculate amplitudes and reconstructed spectrum
        largs = [fit_dd[keep], loc['FIT_PC'][keep, :]]
        amps, recon = lin_mini(*largs)
        # --------------------------------------------------------------
        # set up storage for absorption array 2
        abso2 = np.zeros(len(resspec))
        with warnings.catch_warnings(record=True) as _:
            for ipc in range(len(amps)):
                amps_abso_total[ipc] += amps[ipc]
                abso2 += loc['PC'][:, ipc] * amps[ipc]
            recon_abso *= np.exp(abso2)

    # save outputs to loc
    loc['SP2'] = sp2
    loc['TEMPLATE2'] = template2
    loc['RECON_ABSO'] = recon_abso
    loc['AMPS_ABSOL_TOTAL'] = amps_abso_total
    # set the source
    skeys = ['SP2', 'TEMPLATE2', 'RECON_ABSO', 'AMPS_ABSOL_TOTAL']
    loc.set_sources(skeys, func_name)
    # return loc
    return loc


def calc_molecular_absorption(p, loc):

    # get constants from p
    limit = p['TELLU_FIT_LOG_LIMIT']
    # get data from loc
    recon_abso = loc['RECON_ABSO']
    tapas_all_species = loc['TAPAS_ALL_SPECIES']

    # log data
    log_recon_abso = np.log(recon_abso)
    with warnings.catch_warnings(record=True) as _:
        log_tapas_abso = np.log(tapas_all_species[1:, :])

    # get good pixels
    with warnings.catch_warnings(record=True) as _:
        keep = np.min(log_tapas_abso, axis=0) > limit
        keep &= log_recon_abso > limit
    keep &= np.isfinite(recon_abso)

    # get keep arrays
    klog_recon_abso = log_recon_abso[keep]
    klog_tapas_abso = log_tapas_abso[:, keep]

    # work out amplitudes and recon
    amps, recon = spirouMath.linear_minimization(klog_recon_abso,
                                                 klog_tapas_abso)

    # load amplitudes into loc
    for it, molecule in enumerate(p['TELLU_ABSORBERS'][1:]):
        # get molecule keyword store and key
        molkey = '{0}_{1}'.format(p['KW_TELLU_ABSO'][0], molecule.upper())
        # load into loc
        loc[molkey] = amps[it]
    # return loc
    return loc


def check_blacklist(objname):
    """
    Check whether file is blacklisted

    :param objname: str, the blacklisted object name (to check against list of
                    blacklisted object names)

    :return:
    """
    # get blacklisted files
    blacklisted_objects = get_blacklist()

    # set check to False
    check = False
    # loop around blacklisted objects
    for blacklisted_object in blacklisted_objects:
        # if objname in blacklisted_objects objname is black listed
        if blacklisted_object.upper() == objname.upper():
            check = True
    # return check
    return check


def get_blacklist():
    # get SpirouDRS data folder
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.DATA_CONSTANT_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    # construct the path for the control file
    blacklistfilename = spirouConfig.Constants.TELLU_DATABASE_BLACKLIST_FILE()
    blacklistfile = os.path.join(datadir, blacklistfilename)
    # load control file
    blacklist = spirouConfig.GetTxt(blacklistfile, comments='#', delimiter=' ')
    # return control
    return blacklist


def get_whitelist():
    # get SpirouDRS data folder
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.DATA_CONSTANT_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    # construct the path for the control file
    blacklistfilename = spirouConfig.Constants.TELLU_DATABASE_WHITELIST_FILE()
    blacklistfile = os.path.join(datadir, blacklistfilename)
    # load control file
    blacklist = spirouConfig.GetTxt(blacklistfile, comments='#', delimiter=' ')
    # return control
    return blacklist


def lin_mini(vector, sample):
    return spirouMath.linear_minimization(vector, sample)


def wave2wave(p, spectrum, wave1, wave2, reshape=False):
    """
    Shifts a "spectrum" at a given wavelength solution (map), "wave1", to
    another wavelength solution (map) "wave2"

    :param p: ParamDict, the parameter dictionary
    :param spectrum: numpy array (2D),  flux in the reference frame of the
                     file wave1
    :param wave1: numpy array (2D), initial wavelength grid
    :param wave2: numpy array (2D), destination wavelength grid
    :param reshape: bool, if True try to reshape spectrum to the shape of
                    the output wave solution

    :return output_spectrum: numpy array (2D), spectrum resampled to "wave2"
    """
    func_name = __NAME__ + '.wave2wave()'
    # deal with reshape
    if reshape or (spectrum.shape != wave2.shape):
        try:
            spectrum = spectrum.reshape(wave2.shape)
        except ValueError:
            emsg1 = ('Spectrum (shape = {0}) cannot be reshaped to'
                     ' shape = {1}')
            emsg2 = '\tfunction = {0}'.format(func_name)
            eargs = [spectrum.shape, wave2.shape]
            WLOG(p, 'error', [emsg1.format(*eargs), emsg2])

    # if they are the same
    if np.nansum(wave1 != wave2) == 0:
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
        if np.nansum(g) != 0:
            # spline the spectrum
            spline = IUVSpline(wave1[iord, g], spectrum[iord, g], k=5, ext=1)

            # keep track of pixels affected by NaNs
            splinemask = IUVSpline(wave1[iord, :], g, k=5, ext=1)

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
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-21 at 12:28

@author: cook
"""
from __future__ import division
from astropy import constants as cc
from astropy import units as uu
import numpy as np
import os
from scipy.optimize import curve_fit
import warnings

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core import math as mp
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.io import drs_data


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.rv.general.py'
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
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define functions
# =============================================================================
# TODO: remove alias once not needed (here as a reminder of name change)
def create_drift_file(*args, **kwargs):
    return measure_fp_peaks(*args, **kwargs)


def measure_fp_peaks(params, props, **kwargs):
    """
    Measure the positions of the FP peaks
    Returns the pixels positions and Nth order of each FP peak

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                drift_peak_border_size: int, the border size (edges in
                                        x-direction) for the FP fitting
                                        algorithm
                drift_peak_fpbox_size: int, the box half-size (in pixels) to
                                       fit an individual FP peak to - a
                                       gaussian will be fit to +/- this size
                                       from the center of the FP peak
                drift_peak_peak_sig_lim: dictionary, the sigma above the median
                                         that a peak must have to be recognised
                                         as a valid peak (before fitting a
                                         gaussian) dictionary must have keys
                                         equal to the lamp types (hc, fp)
                drift_peak_inter_peak_spacing: int, the minimum spacing between
                                               peaks in order to be recognised
                                               as a valid peak (before fitting
                                               a gaussian)
                log_opt: string, log option, normally the program name

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                speref: numpy array (2D), the reference spectrum
                wave: numpy array (2D), the wave solution image
                lamp: string, the lamp type (either 'hc' or 'fp')

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                ordpeak: numpy array (1D), the order number for each valid FP
                         peak
                xpeak: numpy array (1D), the central position each gaussain fit
                       to valid FP peak
                ewpeak: numpy array (1D), the FWHM of each gaussain fit
                        to valid FP peak
                vrpeak: numpy array (1D), the radial velocity drift for each
                        valid FP peak
                llpeak: numpy array (1D), the delta wavelength for each valid
                        FP peak
                amppeak: numpy array (1D), the amplitude for each valid FP peak

    """
    func_name = __NAME__ + '.create_drift_file()'
    # get gauss function
    gfunc = mp.gauss_function
    # get constants from params/kwargs
    border = pcheck(params, 'DRIFT_PEAK_BORDER_SIZE', 'border', kwargs,
                    func_name)
    size = pcheck(params, 'DRIFT_PEAK_FPBOX_SIZE', 'size', kwargs, func_name)
    siglimdict = pcheck(params, 'DRIFT_PEAK_PEAK_SIG_LIM', 'siglimdict',
                        kwargs, func_name, mapf='dict', dtype=float)
    ipeakspace = pcheck(params, 'DRIFT_PEAK_IPEAK_SPACING', 'ipeakspace',
                        kwargs, func_name)

    # get the reference data and the wave data
    speref = np.array(props['SPEREF'])
    wave = props['WAVE']
    lamp = props['LAMP']

    # storage for order of peaks
    allordpeak = []
    allxpeak = []
    allewpeak = []
    allvrpeak = []
    allllpeak = []
    allamppeak = []
    # loop through the orders
    for order_num in range(speref.shape[0]):
        # storage for order of peaks
        ordpeak = []
        xpeak = []
        ewpeak = []
        vrpeak = []
        llpeak = []
        amppeak = []
        # get the pixels for this order
        tmp = np.array(speref[order_num, :])
        # For numerical sanity all values less than zero set to zero
        tmp[~np.isfinite(tmp)] = 0
        tmp[tmp < 0] = 0
        # set border pixels to zero to avoid fit starting off the edge of image
        tmp[0: border + 1] = 0
        tmp[-(border + 1):] = 0

        # normalize by the 98th percentile - avoids super-spurois pixels but
        #   keeps the top of the blaze around 1
        # norm = np.nanpercentile(tmp, 98)
        # tmp /= norm

        # peak value depends on type of lamp
        limit = mp.nanmedian(tmp) * siglimdict[lamp]

        # define the maximum pixel value of the normalized array
        maxtmp = mp.nanmax(tmp)
        # set up loop constants
        xprev, ipeak = -99, 0
        nreject = 0
        # loop for peaks that are above a value of limit
        w_all = []
        while maxtmp > limit:
            # find the position of the maximum
            maxpos = np.argmax(tmp)
            # define an area around the maximum peak
            index = np.arange(-size, 1 + size, 1) + maxpos
            index = np.array(index).astype(int)
            # try to fit a gaussian to that peak
            try:
                # set initial guess
                p0 = [tmp[maxpos], maxpos, 1.0, mp.nanmin(tmp[index])]
                # do gauss fit
                #    gg = [mean, amplitude, sigma, dc]
                with warnings.catch_warnings(record=True) as w:
                    # noinspection PyTypeChecker
                    gg, pcov = curve_fit(gfunc, index, tmp[index], p0=p0)
                    w_all += list(w)
            except ValueError:
                # log that ydata or xdata contains NaNs
                WLOG(params, 'warning', TextEntry('00-018-00001'))
                gg = [np.nan, np.nan, np.nan, np.nan]
            except RuntimeError:
                # WLOG(p, 'warning', 'Least-squares fails')
                gg = [np.nan, np.nan, np.nan, np.nan]
            # little sanity check to be sure that the peak is not the same as
            #    we got before and that there is something fishy with the
            #    detection - dx is the distance from last peak
            dx = np.abs(xprev - gg[1])
            # if the distance from last position > 2 - we have a new fit
            if dx > ipeakspace:
                # subtract off the gaussian without the dc level
                # (leave dc for other peaks
                tmp[index] -= gfunc(index, gg[0], gg[1], gg[2], 0)
            # else just set this region to zero, this is a bogus peak that
            #    cannot be fitted
            else:
                tmp[index] = 0
            # only keep peaks within +/- 1 pixel of original peak
            #  (gaussian fit is to find sub-pixel value)
            cond = np.abs(maxpos - gg[1]) < 1

            if cond:
                # work out the radial velocity of the peak
                lambefore = wave[order_num, maxpos - 1]
                lamafter = wave[order_num, maxpos + 1]
                deltalam = lamafter - lambefore
                # get the radial velocity
                waveomax = wave[order_num, maxpos]
                radvel = speed_of_light_ms * deltalam / (2.0 * waveomax)

                # add to storage
                ordpeak.append(order_num)
                xpeak.append(gg[1])
                ewpeak.append(gg[2])
                vrpeak.append(radvel)
                llpeak.append(deltalam)
                amppeak.append(maxtmp)
            else:
                # add to rejected
                nreject += 1
            # recalculate the max peak
            maxtmp = mp.nanmax(tmp)
            # set previous peak to this one
            xprev = gg[1]
            # iterator
            ipeak += 1
        # display warning messages
        drs_log.warninglogger(params, w_all)
        # log how many FPs were found and how many rejected
        wargs = [order_num, ipeak, nreject]
        WLOG(params, '', TextEntry('40-018-00001', args=wargs))
        # add values to all storage (and sort by xpeak)
        indsort = np.argsort(xpeak)
        allordpeak.append(np.array(ordpeak)[indsort])
        allxpeak.append(np.array(xpeak)[indsort])
        allewpeak.append(np.array(ewpeak)[indsort])
        allvrpeak.append(np.array(vrpeak)[indsort])
        allllpeak.append(np.array(llpeak)[indsort])
        allamppeak.append(np.array(amppeak)[indsort])
    # store values in loc
    props['ORDPEAK'] = np.concatenate(allordpeak).astype(int)
    props['XPEAK'] = np.concatenate(allxpeak)
    props['EWPEAK'] = np.concatenate(allewpeak)
    props['VRPEAK'] = np.concatenate(allvrpeak)
    props['LLPEAK'] = np.concatenate(allllpeak)
    props['AMPPEAK'] = np.concatenate(allamppeak)
    # set source
    keys = ['ordpeak', 'xpeak', 'ewpeak', 'vrpeak', 'llpeak', 'amppeak']
    props.set_sources(keys, func_name)

    # Log the total number of FP lines found
    wargs = [len(allxpeak)]
    WLOG(params, 'info', TextEntry('40-018-00002', args=wargs))

    # return the property parameter dictionary
    return props


def remove_wide_peaks(params, props, **kwargs):
    """
    Remove peaks that are too wide

    :param p: parameter dictionary, ParamDict containing constants

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                ordpeak: numpy array (1D), the order number for each valid FP
                         peak
                xpeak: numpy array (1D), the central position each gaussain fit
                       to valid FP peak
                ewpeak: numpy array (1D), the FWHM of each gaussain fit
                        to valid FP peak
                vrpeak: numpy array (1D), the radial velocity drift for each
                        valid FP peak
                llpeak: numpy array (1D), the delta wavelength for each valid
                        FP peak
                amppeak: numpy array (1D), the amplitude for each valid FP peak

    :param expwidth: float or None, the expected width of FP peaks - used to
                     "normalise" peaks (which are then subsequently removed
                     if > "cutwidth") if expwidth is None taken from
                     p['DRIFT_PEAK_EXP_WIDTH']
    :param cutwidth: float or None, the normalised width of FP peaks thatis too
                     large normalised width FP FWHM - expwidth
                     cut is essentially: FP FWHM < (expwidth + cutwidth), if
                     cutwidth is None taken from p['DRIFT_PEAK_NORM_WIDTH_CUT']

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                ordpeak: numpy array (1D), the order number for each valid FP
                         peak (masked to remove wide peaks)
                xpeak: numpy array (1D), the central position each gaussain fit
                       to valid FP peak (masked to remove wide peaks)
                ewpeak: numpy array (1D), the FWHM of each gaussain fit
                        to valid FP peak (masked to remove wide peaks)
                vrpeak: numpy array (1D), the radial velocity drift for each
                        valid FP peak (masked to remove wide peaks)
                llpeak: numpy array (1D), the delta wavelength for each valid
                        FP peak (masked to remove wide peaks)
                amppeak: numpy array (1D), the amplitude for each valid FP peak
                         (masked to remove wide peaks)
    """
    func_name = __NAME__ + '.remove_wide_peaks()'
    # get constants
    expwidth = pcheck(params, 'DRIFT_PEAK_EXP_WIDTH', 'expwidth', kwargs,
                      func_name)
    cutwidth = pcheck(params, 'DRIFT_PEAK_NORM_WIDTH_CUT', 'cutwidth',
                      kwargs, func_name)
    peak_spacing = pcheck(params, 'DRIFT_PEAK_IPEAK_SPACING', 'peak_spacing',
                          kwargs, func_name)

    # define a mask to cut out wide peaks
    mask = np.abs(np.array(props['EWPEAK']) - expwidth) < cutwidth

    # apply mask
    props['ORDPEAK'] = props['ORDPEAK'][mask]
    props['XPEAK'] = props['XPEAK'][mask]
    props['EWPEAK'] = props['EWPEAK'][mask]
    props['VRPEAK'] = props['VRPEAK'][mask]
    props['LLPEAK'] = props['LLPEAK'][mask]
    props['AMPPEAK'] = props['AMPPEAK'][mask]

    # check for and remove double-fitted lines
    # save old position
    props['XPEAK_OLD'] = np.copy(props['XPEAK'])
    props['ORDPEAK_OLD'] = np.copy(props['ORDPEAK'])

    # set up storage for good lines
    ordpeak_k, xpeak_k, ewpeak_k, vrpeak_k = [], [], [], []
    llpeak_k, amppeak_k = [], []

    # loop through the orders
    for order_num in range(np.shape(props['SPEREF'])[0]):
        # set up mask for the order
        gg = props['ORDPEAK'] == order_num
        # get the xvalues
        xpeak = props['XPEAK'][gg]
        # get the amplitudes
        amppeak = props['AMPPEAK'][gg]
        # get the points where two peaks are spaced by < peak_spacing
        ind = np.argwhere(xpeak[1:] - xpeak[:-1] < peak_spacing)
        # get the indices of the second peak of each pair
        ind2 = ind + 1
        # initialize mask with the same size as xpeak
        xmask = np.ones(len(xpeak), dtype=bool)
        # mask the peak with the lower amplitude of the two
        for i in range(len(ind)):
            if amppeak[ind[i]] < amppeak[ind2[i]]:
                xmask[ind[i]] = False
            else:
                xmask[ind2[i]] = False
        # save good lines
        ordpeak_k += list(props['ORDPEAK'][gg][xmask])
        xpeak_k += list(props['XPEAK'][gg][xmask])
        ewpeak_k += list(props['EWPEAK'][gg][xmask])
        vrpeak_k += list(props['VRPEAK'][gg][xmask])
        llpeak_k += list(props['LLPEAK'][gg][xmask])
        amppeak_k += list(props['AMPPEAK'][gg][xmask])

    # replace FP peak arrays in loc
    props['ORDPEAK'] = np.array(ordpeak_k)
    props['XPEAK'] = np.array(xpeak_k)
    props['EWPEAK'] = np.array(ewpeak_k)
    props['VRPEAK'] = np.array(vrpeak_k)
    props['LLPEAK'] = np.array(llpeak_k)
    props['AMPPEAK'] = np.array(amppeak_k)

    # append this function to sources
    keys = ['ordpeak', 'xpeak', 'ewpeak', 'vrpeak', 'llpeak', 'amppeak']
    props.append_sources(keys, func_name)

    # log number of lines removed for suspicious width
    wargs = [mp.nansum(~mask)]
    WLOG(params, 'info', TextEntry('40-018-00003', args=wargs))

    # log number of lines removed as double-fitted
    if len(props['XPEAK_OLD']) > len(props['XPEAK']):
        wargs = [len(props['XPEAK_OLD']) - len(props['XPEAK'])]
        WLOG(params, 'info', TextEntry('40-018-00004', args=wargs))

    # return props
    return props


def get_ccf_mask(params, filename, **kwargs):
    func_name = __NAME__ + '.get_ccf_mask()'
    # get constants from params / kwargs
    mask_min = pcheck(params, 'CCF_MASK_MIN_WEIGHT', 'mask_min', kwargs,
                      func_name)
    mask_width = pcheck(params, 'CCF_MASK_WIDTH', 'mask_width', kwargs,
                        func_name)
    # load table
    table, absfilename = drs_data.load_ccf_mask(params, filename=filename)
    # calculate the difference in mask_e and mask_s
    ll_mask_d = np.array(table['ll_mask_e']) - np.array(table['ll_mask_s'])
    ll_mask_ctr = np.array(table['ll_mask_s']) + ll_mask_d * 0.5
    # if mask_width > 0 ll_mask_d is multiplied by mask_width/c
    if mask_width > 0:
        ll_mask_d = mask_width * np.array(table['ll_mask_s']) / speed_of_light
    # make w_mask an array
    w_mask = np.array(table['w_mask'])
    # use w_min to select on w_mask or keep all if w_mask_min >= 1
    if mask_min < 1.0:
        mask = w_mask > mask_min
        ll_mask_d = ll_mask_d[mask]
        ll_mask_ctr = ll_mask_ctr[mask]
        w_mask = w_mask[mask]
    # else set all w_mask to one (and use all lines in file)
    else:
        w_mask = np.ones(len(ll_mask_d))
    # return the size of each pixel, the central point of each pixel
    #    and the weight mask
    return ll_mask_d, ll_mask_ctr, w_mask


def delta_v_rms_2d(spe, wave, sigdet, threshold, size):
    """
    Compute the photon noise uncertainty for all orders (for the 2D image)

    :param spe: numpy array (2D), the extracted spectrum
                size = (number of orders by number of columns (x-axis))
    :param wave: numpy array (2D), the wave solution for each pixel
    :param sigdet: float, the read noise (sigdet) for calculating the
                   noise array
    :param threshold: float, upper limit for pixel values, above this limit
                      pixels are regarded as saturated
    :param size: int, size (in pixels) around saturated pixels to also regard
                 as bad pixels

    :return dvrms2: numpy array (1D), the photon noise for each pixel (squared)
    :return weightedmean: float, weighted mean photon noise across all orders
    """
    # flag (saturated) fluxes above threshold as "bad pixels"
    with warnings.catch_warnings(record=True) as _:
        flag = spe < threshold
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2 * size, 1):
        flag[:, size:-size] *= flag[:, i_it: i_it - 2 * size]
    # get the wavelength normalised to the wavelength spacing
    nwave = wave[:, 1:-1] / (wave[:, 2:] - wave[:, :-2])
    # get the flux + noise array
    sxn = (spe[:, 1:-1] + sigdet ** 2)
    # get the flux difference normalised to the flux + noise
    nspe = (spe[:, 2:] - spe[:, :-2]) / sxn
    # get the mask value
    maskv = flag[:, 2:] * flag[:, 1:-1] * flag[:, :-2]
    # get the total
    tot = mp.nansum(sxn * ((nwave * nspe) ** 2) * maskv, axis=1)
    # convert to dvrms2
    with warnings.catch_warnings(record=True) as _:
        dvrms2 = (speed_of_light_ms ** 2) / abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1. / np.sqrt(mp.nansum(1.0 / dvrms2))
    # return dv rms and weighted mean
    return dvrms2, weightedmean


def coravelation(params, props, log=False, **kwargs):
    """
    Calculate the CCF and fit it with a Gaussian profile

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                ccf_berv: float, the barycentric Earth RV (berv)
                ccf_berv_max: float, the maximum barycentric Earth RV
                target_rv: float, the target RV
                ccf_width: float, the CCF width
                ccf_step: float, the CCF step
                ccf_det_noise: float, the detector noise to use in the ccf
                ccf_fit_type: int, the type of fit for the CCF fit
                log_opt: string, log option, normally the program name
                DRS_DEBUG: int, Whether to run in debug mode
                                0: no debug
                                1: basic debugging on errors
                                2: recipes specific (plots and some code runs)
                DRS_PLOT: bool, Whether to plot (True to plot)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                wave_ll: numpy array (1D), the line list values
                param_ll: numpy array (1d), the line list fit coefficients
                          (used to generate line list - read from file defined)
                ll_mask_d: numpy array (1D), the size of each line
                           (in wavelengths)
                ll_mask_ctr: numpy array (1D), the central point of each line
                             (in wavelengths)
                w_mask: numpy array (1D), the weight mask
                e2dsff: numpy array (2D), the flat fielded E2DS spectrum
                        shape = (number of orders x number of columns in image
                                                      (x-axis dimension) )
                blaze: numpy array (2D), the blaze function
                        shape = (number of orders x number of columns in image
                                                      (x-axis dimension) )

    :param log: bool, if True logs to stdout/file if False is silent

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                rv_ccf: numpy array (1D), the radial velocities for the CCF
                ccf: numpy array (2D), the CCF for each order and each RV
                     shape = (number of orders x number of RV points)
                ccf_max: float, numpy array (1D), the max value of the CCF for
                         each order
                pix_passed_all: numpy array (1D), the weighted line list
                                position for each order?
                tot_line: numpy array (1D), the total number of lines for each
                          order
                ll_range_all: numpy array (1D), the weighted line list width for
                          each order
                ccf_noise: numpy array (2D), the CCF noise for each order and
                           each RV
                           shape = (number of orders x number of RV points)
    """
    func_name = __NAME__ + '.coravelation()'
    # -------------------------------------------------------------------------
    # get constants from p
    # -------------------------------------------------------------------------
    ccf_step = pcheck(params, 'CCF_STEP', 'ccf_step', kwargs, func_name)
    ccf_width = pcheck(params, 'CCF_WIDTH', 'ccf_width', kwargs, func_name)
    det_noise = pcheck(params, 'CCF_DET_NOISE', 'det_noise', kwargs, func_name)
    fit_type = pcheck(params, 'CCF_FIT_TYPE', 'fit_type', kwargs, func_name)
    target_rv = pcheck(params, 'CCF_TARGET_RV', 'target_rv', kwargs, func_name)

    # -------------------------------------------------------------------------
    # get data from loc
    # -------------------------------------------------------------------------
    # get the wavelengths for the lines and the fit coefficients for each line
    ll_map, coeff_ll = props['WAVE_LL'], props['PARAM_LL']
    # get the line centers and the line widths
    ll_mask_ctr, ll_mask_d = props['LL_MASK_CTR'], props['LL_MASK_D']
    # get the line weights
    w_mask = props['W_MASK']
    # get the flat fielded flux values
    s2d = props['E2DSFF']
    # get the blaze values
    blaze = props['BLAZE']
    # get the Barycentric Earth Velocity calculation
    berv = props['BERV']
    berv_max = props['BERV_MAX']

    # TODO: Is this okay to do this?
    if ~np.isfinite(berv):
        berv = 0.0
        berv_max = 0.0
    # -------------------------------------------------------------------------
    # log that we are computing ccf at target_rv
    if log:
        WLOG(params, '', TextEntry('40-020-00001', wargs=[target_rv]))
    # -------------------------------------------------------------------------
    # get rvmin and rvmax
    if 'RVMIN' in kwargs:
        rvmin = kwargs['RVMIN']
    elif 'RVMIN' in params:
        rvmin = params['RVMIN']
    else:
        rvmin = target_rv - ccf_width
    if 'RVMAX' in kwargs:
        rvmax = kwargs['RVMAX']
    elif 'RVMAX' in params:
        rvmax = params['RVMAX']
    else:
        rvmax = target_rv + ccf_width + ccf_step
    # create a rv ccf range
    rv_ccf = np.arange(rvmin, rvmax, ccf_step)
    # -------------------------------------------------------------------------
    # calculate modified map
    ll_map_b = ll_map * (1.0 + 1.55e-8) * (1.0 + berv / speed_of_light)
    # calculate modified coefficients
    coeff_ll_b = coeff_ll * (1.0 + 1.55e-8) * (1.0 + berv / speed_of_light)
    # get the differential map
    dll_map = mp.get_dll_from_coefficients(coeff_ll_b, len(ll_map[0]),
                                             len(coeff_ll))
    # -------------------------------------------------------------------------
    # define some constants for loop
    constant1 = (1 + 1.55e-8) * (1 + berv_max / speed_of_light)
    constant2 = (1 + 1.55e-8) * (1 - berv_max / speed_of_light)
    rvshift = 1 + rv_ccf / speed_of_light
    # -------------------------------------------------------------------------
    # storage for loop
    orders = []
    ccf_all = []
    ccf_noise_all = []
    ccf_all_fit = []
    ccf_max = []
    ccf_all_results = []
    pix_passed_all = []
    ll_range_all = []
    tot_line = []
    # -------------------------------------------------------------------------
    # graph set up
    if params['DRS_PLOT'] and params['DRS_DEBUG'] == 2:
        # TODO: Add plots
        # # start interactive plot
        # sPlt.start_interactive_session(p)
        # # define a figure
        # fig = sPlt.define_figure()
        pass
    else:
        fig = None
    # -------------------------------------------------------------------------
    # loop around the orders
    for order_num in range(len(ll_map)):
        # get the line list limits
        ll_min = ll_map[order_num, 1] * constant1 / rvshift[0]
        ll_max = ll_map[order_num, -1] * constant2 / rvshift[-1]
        # define mask (mask centers must be inside ll_min and ll_max
        cond = (ll_mask_ctr - 0.5 * ll_mask_d) > ll_min
        cond &= (ll_mask_ctr + 0.5 * ll_mask_d) < ll_max
        # mask mask_ctr, mask_d and w_mask
        ll_sub_mask_ctr = ll_mask_ctr[cond]
        ll_sub_mask_d = ll_mask_d[cond]
        w_sub_mask = w_mask[cond]

        # if we have values that meet the "cond" condition then we can do CCF
        if mp.nansum(cond) > 0:
            # -----------------------------------------------------------------
            # calculate the CCF
            ccf_args = [ll_sub_mask_ctr, ll_sub_mask_d, w_sub_mask,
                        ll_map_b[order_num], s2d[order_num],
                        dll_map[order_num], blaze[order_num],
                        rv_ccf, det_noise]
            ccf_o, pix_passed, ll_range, ccf_noise = calculate_ccf(*ccf_args)
            # -----------------------------------------------------------------
            # fit the CCF
            fit_args = [params, order_num, rv_ccf, np.array(ccf_o), fit_type]
            try:
                with warnings.catch_warnings(record=True) as _:
                    ccf_o_results, ccf_o_fit = fit_ccf(*fit_args)
            except RuntimeError:
                ll_range, pix_passed = 0.0, 1.0
                ccf_o, ccf_noise, ccf_o_fit = np.zeros((3, len(rv_ccf)))
                ccf_o_results = np.zeros(4)

            if np.sum(np.isfinite(ccf_o) == 0):
                ll_range, pix_passed = 0.0, 1.0
                ccf_o, ccf_noise, ccf_o_fit = np.zeros((3, len(rv_ccf)))
                ccf_o_results = np.zeros(4)
        else:
            # -----------------------------------------------------------------
            # else append empty stats
            ll_range, pix_passed = 0.0, 1.0
            ccf_o, ccf_noise, ccf_o_fit = np.zeros((3, len(rv_ccf)))
            ccf_o_results = np.zeros(4)

        # ---------------------------------------------------------------------
        # append to storage
        orders.append(order_num)
        tot_line.append(len(w_sub_mask))
        ccf_all.append(ccf_o)
        ccf_noise_all.append(ccf_noise)
        ccf_max.append(mp.nanmax(ccf_o))
        ccf_all_fit.append(ccf_o_fit)
        ccf_all_results.append(ccf_o_results)
        pix_passed_all.append(pix_passed)
        ll_range_all.append(ll_range)
        # ---------------------------------------------------------------------
        # Plots
        # ---------------------------------------------------------------------
        cond1 = len(ll_sub_mask_ctr) > 0

        if params['DRS_PLOT'] and cond1 and params['DRS_DEBUG'] == 2:
            # TODO: Add plots
            # # Plot rv vs ccf (and rv vs ccf_fit)
            # sPlt.ccf_rv_ccf_plot(p, rv_ccf, ccf_o, ccf_o_fit, order=order_num,
            #                      fig=fig)
            pass
    # -------------------------------------------------------------------------
    # convert to arrays
    orders = np.array(orders)
    tot_line = np.array(tot_line)
    ccf_all = np.array(ccf_all)
    ccf_noise_all = np.array(ccf_noise_all)
    ccf_max = np.array(ccf_max)
    # ccf_all_fit = np.array(ccf_all_fit)
    ccf_all_results = np.array(ccf_all_results)
    pix_passed_all = np.array(pix_passed_all)
    ll_range_all = np.array(ll_range_all)

    # -------------------------------------------------------------------------
    # add outputs to loc
    props['RV_CCF'] = rv_ccf
    props['CCF'] = ccf_all
    props['CCF_MAX'] = ccf_max
    props['PIX_PASSED_ALL'] = pix_passed_all
    props['TOT_LINE'] = tot_line
    props['LL_RANGE_ALL'] = ll_range_all
    props['CCF_NOISE'] = ccf_noise_all
    props['ORDERS'] = orders
    props['CCF_ALL_RESULTS'] = ccf_all_results

    # set source
    keys = ['rv_ccf', 'ccf', 'ccf_max', 'pix_passed_all', 'tot_line',
            'll_range_all', 'ccf_noise', 'orders', 'ccf_all_results']
    props.set_sources(keys, __NAME__ + '/coravelation()')
    # -------------------------------------------------------------------------
    # return loc
    return props


def calculate_ccf(mask_ll, mask_d, mask_w, sp_ll, sp_flux, sp_dll, blaze,
                  rv_ccf, det_noise, mode='fast'):
    """
    Calculate the cross correlation function

    :param mask_ll: numpy array (1D), the centers of the lines to be used
                    size = (number of lines to use)
    :param mask_d: numpy array (1D), the widths of the lines to be used
                   size = (number of lines to use)
    :param mask_w: numpy array (1D), the weights of each line
                    size = (number of lines to use)
    :param sp_ll: numpy array (1D), the wavelength values for this order
                  size = (number of columns in e2ds file [x-dimension])
    :param sp_flux: numpy array (1D), the flux values for this order
                    size = (number of columns in e2ds file [x-dimension])
    :param sp_dll: numpy array (1D), the derivative of the line list fits for
                   this order
                   size = (number of columns in e2ds file [x-dimension])
    :param blaze: numpy array (1D), the blaze values for this order
                  size = (number of columns in e2ds file [x-dimension])
    :param rv_ccf: numpy array (1D), the RV values for this order
                   size = (2 * ccf_width/ccf_step + 1)
    :param det_noise: float, the detector noise
    :param mode: string, if "fast" uses a non-for-loop python function to run
                 the ccf calculation, if "slow" uses a direct fortran
                 translation to run the ccf calculation

    :return ccf: numpy array (1D), the CCF for each RV value
    :return pix: float, the weighted line list position?
    :return llrange: float, the weighted line list width?
    :return ccf_noise: numpy array (1D), the CCF noise for each RV value
    """

    # constants
    sp_ll_dll = sp_ll + sp_dll * 0.5
    mask_ll_d1 = mask_ll - 0.5 * mask_d
    mask_ll_d2 = mask_ll + 0.5 * mask_d
    rv_corr = 1 + rv_ccf / speed_of_light
    # get the line centers
    line_ctr = mask_ll * (1 + rv_ccf[int(len(rv_ccf) / 2)] / speed_of_light)
    index_line_ctr = np.searchsorted(sp_ll_dll, line_ctr) + 1

    # loop around each rv in rv_ccf
    ccf, ccf_noise = [], []
    pix, llrange = 0.0, 0.0
    for it in range(len(rv_ccf)):
        # ge the blue and red ends of each line
        mask_blue = mask_ll_d1 * rv_corr[it]
        mask_red = mask_ll_d2 * rv_corr[it]
        # get the indices for the blue and red ends of each line
        index_mask_blue = np.searchsorted(sp_ll_dll, mask_blue) + 1
        index_mask_red = np.searchsorted(sp_ll_dll, mask_red) + 1

        # work out the correlation of each bin
        cargs = [sp_flux, sp_ll, sp_dll, blaze, mask_blue, mask_red, mask_w,
                 index_mask_blue, index_mask_red, index_line_ctr, det_noise]
        # if mode == 'fast':
        #     out, pix, llrange, sigout = new_correlbin(*cargs)
        # else:
        #     out, pix, llrange, sigout = correlbin(*cargs)
        out, pix, llrange, sigout = correlbin(*cargs)

        ccf.append(out), ccf_noise.append(sigout)
    # return the ccf, pix, llrange and ccf_noise
    return ccf, pix, llrange, ccf_noise


def correlbin(flux, ll, dll, blaze, ll_s, ll_e, ll_wei, i_start, i_end,
              i_line_ctr, det_noise):
    """
    Raw (Fortran direct translate) of correlbin

    Timing statistics:

    raw_correlbin
    523 µs ± 62.8 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

    correlbin
    126 µs ± 13.5 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)

    fortran
    2.56 µs per loop

    :param flux: numpy array (1D), the flux values for this order
                 size = (number of columns in e2ds file [x-dimension])
    :param ll: numpy array (1D), the wavelength values for this order
               size = (number of columns in e2ds file [x-dimension])
    :param dll: numpy array (1D), the derivative of the line list fits for
                this order
                size = (number of columns in e2ds file [x-dimension])
    :param blaze: numpy array (1D), the blaze values for this order
                  size = (number of columns in e2ds file [x-dimension])
    :param ll_s: numpy array (1D), the wavelength at the blue end of each line
                 size = (number of lines to use)
    :param ll_e: numpy array (1D), the wavelength at the red end of each line
                 size = (number of lines to use)
    :param ll_wei: numpy array (1D), the weights of each line
                   size = (number of lines to use)
    :param i_start: numpy array (1D), the indices ll where ll_s would appear if
                    inserted and sorted (i.e. the bin position to at the blue
                    end of each line in the main image)
                    size = (number of lines to use)
    :param i_end: numpy array (1D), the indices ll where ll_e would appear if
                  inserted and sorted (i.e. the bin position to at the red
                  end of each line in the main image)
                  size = (number of lines to use)
    :param i_line_ctr: numpy array (1D), the indices ll where the line centers
                       would appear if inserted and sorted (i.e. the bin
                       position to at the red end of each line in the main
                       image)
                       size = (number of lines to use)
    :param det_noise: float, the detector noise

    :return out_ccf: float, the calculated CCF
    :return pix: float, the last pix value?
    :return llrange: float, the line list range?
    :return ccf_noise: float, the calculated CCF noise
    """
    # get sizes of arrays
    # nx = len(flux)
    nfind = len(ll_s)
    # set up outputs
    out_ccf = 0.0
    pix = 0.0
    llrange = 0.0
    ccf_noise = 0.0
    # loop around nfind 1 to nfind +1 (+1 for python loop)
    for it in range(1, nfind + 1):
        # adjust from fortran indexing to python indexing
        ft = it - 1

        # get indices
        start, end = i_start[ft], i_end[ft]
        center = i_line_ctr[ft]
        weight = ll_wei[ft]

        # adjust from fortran indexing to python indexing
        start = start - 1
        end = end - 1
        center = center - 1

        # if the end and start index are the same
        if start == end:
            # pix value = take the difference over the derivative
            pix_s = (ll_e[ft] - ll_s[ft]) / dll[start]
            # output ccf calculation
            out = pix_s * flux[start] / blaze[start]
            out_ccf += (out * weight * blaze[center])
            # pixel calculation
            pix += (pix_s * weight)
            llrange += (pix_s * dll[start] * weight)
            # ccf noise calculation
            noise1 = pix_s * np.abs(flux[start])
            noise2 = pix_s * det_noise ** 2
            ccf_noise += ((noise1 + noise2) * weight ** 2)
        # if start+1 == end
        elif (start + 1) == end:
            # pix value = start + 0.5 * derivative - Mask_blue/derivative
            pix_s = (ll[start] + (dll[start] * 0.5) - ll_s[ft]) / dll[start]
            # pix value = (end - (start + derivative)) /derivative
            pix_e = (ll_e[ft] - ll[start] - dll[start] * 0.5) / dll[end]
            # output ccf calculation
            out1 = pix_s * flux[start] / blaze[start]
            out2 = pix_e * flux[end] / blaze[end]
            out_ccf += ((out1 + out2) * weight * blaze[center])
            # pixel calculation
            pix += ((pix_s + pix_e) * weight)
            llrange += ((pix_s * dll[start] + pix_e * dll[end]) * weight)
            # ccf noise calculation
            noise1 = pix_s * np.abs(flux[start])
            noise2 = pix_e * np.abs(flux[end])
            noise3 = (pix_s + pix_e) * det_noise ** 2
            ccf_noise += (noise1 + noise2 + noise3) * weight ** 2
        # else
        else:
            # pix value = start + 0.5 * derivative - Mask_blue/derivative
            pix_s = (ll[start] + (dll[start] * 0.5) - ll_s[ft]) / dll[start]
            # pix value = (end - (start + derivative)) /derivative
            pix_e = (ll_e[ft] - ll[end - 1] - dll[end - 1] * 0.5) / dll[end]
            # output ccf calculation
            out1 = pix_s * flux[start] / blaze[start]
            out2 = pix_e * flux[end] / blaze[end]
            out_ccf += ((out1 + out2) * weight * blaze[center])
            # pixel calculation
            pix += ((pix_s + pix_e) * weight)
            llrange += ((pix_s * dll[start] + pix_e * dll[end]) * weight)
            # ccf noise calculation
            noise1 = pix_s * np.abs(flux[start])
            noise2 = pix_e * np.abs(flux[end])
            noise3 = (pix_s + pix_e) * det_noise ** 2
            ccf_noise += (noise1 + noise2 + noise3) * weight ** 2
            # loop around start + 1 to end - 1 + 1 (+1 for python loop)
            for i in range(start + 1, end - 1 + 1):
                # adjust from fortran indexing to python indexing
                j = i - 1
                # output ccf calculation
                out_ccf += (flux[j] / blaze[j]) * blaze[center] * weight
                # pixel calculation
                pix += weight
                llrange += (dll[j] * weight)
                # ccf noise calculation
                noise1 = np.abs(flux[j])
                noise2 = det_noise ** 2
                ccf_noise += (noise1 + noise2) * weight ** 2

    # sqrt the noise
    ccf_noise = np.sqrt(ccf_noise)
    # return parameters
    return out_ccf, pix, llrange, ccf_noise


def fit_ccf(params, order_num, rv, ccf, fit_type):
    """
    Fit the CCF to a guassian function

    :param rv: numpy array (1D), the radial velocities for the line
    :param ccf: numpy array (1D), the CCF values for the line
    :param fit_type: int, if "0" then we have an absorption line
                          if "1" then we have an emission line

    :return result: numpy array (1D), the fit parameters in the
                    following order:

                [amplitude, center, fwhm, offset from 0 (in y-direction)]

    :return ccf_fit: numpy array (1D), the fit values, i.e. the gaussian values
                     for the fit parameters in "result"
    """
    func_name = __NAME__ + '.fit_ccf()'
    # deal with inconsistent lengths
    if len(rv) != len(ccf):
        eargs = [len(rv), len(ccf), func_name]
        WLOG(params, 'error', TextEntry('00-020-00001', args=eargs))

    # deal with all nans
    if np.sum(np.isnan(ccf)) == len(ccf):
        # log warning about all NaN ccf
        wargs = [order_num]
        WLOG(params, 'warning', TextEntry('10-020-00001', args=wargs))
        # return NaNs
        result = np.zeros(4) * np.nan
        ccf_fit = np.zeros_like(ccf) * np.nan
        return result, ccf_fit

    # get constants
    max_ccf, min_ccf = mp.nanmax(ccf), mp.nanmin(ccf)
    argmin, argmax = mp.nanargmin(ccf), mp.nanargmax(ccf)
    diff = max_ccf - min_ccf
    rvdiff = rv[1] - rv[0]
    # set up guess for gaussian fit
    # if fit_type == 0 then we have absorption lines
    if fit_type == 0:
        if mp.nanmax(ccf) != 0:
            a = np.array([-diff / max_ccf, rv[argmin], 4 * rvdiff, 0])
        else:
            a = np.zeros(4)
    # else (fit_type == 1) then we have emission lines
    else:
        a = np.array([diff / max_ccf, rv[argmax], 4 * rvdiff, 1])
    # normalise y
    y = ccf / max_ccf - 1 + fit_type
    # x is just the RVs
    x = rv
    # uniform weights
    w = np.ones(len(ccf))
    # get gaussian fit
    nanmask = np.isfinite(y)
    y[~nanmask] = 0.0
    # fit the gaussian
    result, fit = mp.fitgaussian(x, y, weights=w, guess=a)
    # scal ethe ccf
    ccf_fit = (fit + 1 - fit_type) * max_ccf
    # return the best guess and the gaussian fit
    return result, ccf_fit


def remove_telluric_domain(params, recipe, infile, fiber, **kwargs):
    func_name = __NAME__ + '.remove_telluric_domain()'
    # get parameters from params/kwargs
    ccf_tellu_thres = pcheck(params, 'CCF_TELLU_THRES', 'ccf_tellu_thres',
                             kwargs, func_name)
    # get extraction type from the header
    ext_type = infile.get_key('KW_EXT_TYPE', dtype=str)
    # get the input file (assumed to be the first file from header
    e2dsfilename = infile.get_key('KW_INFILE1', dtype=str)
    # construct absolute path for the e2ds file
    e2dsabsfilename = os.path.join(infile.path, e2dsfilename)
    # check that e2ds file exists
    if not os.path.exists(e2dsabsfilename):
        eargs = [infile.filename, ext_type, e2dsabsfilename]
        WLOG(params, 'error', TextEntry('09-020-00001', args=eargs))
    # get infile
    e2dsinst = core.get_file_definition(ext_type, params['INSTRUMENT'],
                                        kind='red')
    # construct e2ds file
    e2dsfile = e2dsinst.newcopy(recipe=recipe, fiber=fiber)
    e2dsfile.set_filename(e2dsfilename)
    # get recon file
    reconinst = core.get_file_definition('TELLU_RECON', params['INSTRUMENT'],
                                         kind='red')
    # construct recon file
    reconfile = reconinst.newcopy(recipe=recipe, fiber=fiber)
    reconfile.construct_filename(params, infile=e2dsfile)
    # check recon file exists
    if not os.path.exists(reconfile.filename):
        eargs = [infile.filename, reconfile.name, e2dsfile.filename]
        WLOG(params, 'error', TextEntry('09-020-00001', args=eargs))
    # read recon file
    reconfile.read()
    # find all places below threshold
    keep = reconfile.data > ccf_tellu_thres
    # set all bad data to NaNs
    infile.data[~keep] = np.nan
    # return in file
    return infile


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

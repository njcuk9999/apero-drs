#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou radial velocity module

Created on 2017-11-21 at 11:52

@author: cook

"""
from __future__ import division
import numpy as np
from astropy import constants
from scipy.stats.stats import pearsonr
from scipy.optimize import curve_fit
import warnings
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS.spirouCore import spirouMath

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouRV.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
ConfigError = spirouConfig.ConfigError
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# get speed of light
# noinspection PyUnresolvedReferences
CONSTANT_C = constants.c.value
# get gaussian function
gauss_function = spirouCore.GaussFunction


# =============================================================================
# Define main functions
# =============================================================================
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
    tot = np.nansum(sxn * ((nwave * nspe) ** 2) * maskv, axis=1)
    # convert to dvrms2
    with warnings.catch_warnings(record=True) as _:
        dvrms2 = (CONSTANT_C ** 2) / abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1. / np.sqrt(np.nansum(1.0 / dvrms2))
    # return dv rms and weighted mean
    return dvrms2, weightedmean


def renormalise_cosmic2d(p, speref, spe, threshold, size, cut):
    """
    Correction of the cosmics and renormalisation by comparison with
    reference spectrum (for the 2D image)

    :param speref: numpy array (2D), the REFERENCE extracted spectrum
                   size = (number of orders by number of columns (x-axis))
    :param spe:  numpy array (2D), the COMPARISON extracted spectrum
                 size = (number of orders by number of columns (x-axis))
    :param threshold: float, upper limit for pixel values, above this limit
                      pixels are regarded as saturated
    :param size: int, size (in pixels) around saturated pixels to also regard
                 as bad pixels
    :param cut: float, define the number of standard deviations cut at in
                cosmic renormalisation

    :return spen: numpy array (2D), the corrected normalised COMPARISON
                  extracted spectrrum
    :return cnormspe: numpy array (1D), the flux ratio for each order between
                      corrected normalised COMPARISON extracted spectrum and
                      REFERENCE extracted spectrum
    :return cpt: float, the total flux above the "cut" parameter
                 (cut * standard deviations above median)
    """
    func_name = __NAME__ + '.renormalise_cosmic2d()'
    # flag (saturated) fluxes above threshold as "bad pixels"
    with warnings.catch_warnings(record=True) as _:
        flag = (spe < threshold) & (speref < threshold)
    # get the dimensions of spe
    dim1, dim2 = spe.shape
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2 * size, 1):
        flag[:, size:-size] *= flag[:, i_it: i_it - 2 * size]
    # set bad pixels to zero (multiply by mask)
    spereff = speref * flag
    spef = spe * flag
    # create a normalised spectrum
    normspe = np.nansum(spef, axis=1) / np.nansum(spereff, axis=1)
    # get normed spectrum for each pixel for each order
    rnormspe = np.repeat(normspe, dim2).reshape((dim1, dim2))
    # get the sum of values for the combined speref and spe for each order
    stotal = np.nansum(spereff + spef, axis=1) / dim2
    stotal = np.repeat(stotal, dim2).reshape((dim1, dim2))
    # get difference over the normalised spectrum
    ztop = spereff - spef / rnormspe
    zbottom = (spef / rnormspe) + spereff + stotal
    z = ztop / zbottom
    # get good values
    with warnings.catch_warnings(record=True) as _:
        goodvalues = abs(z) > 0
    # set the bad values to NaN
    znan = np.copy(z)
    znan[~goodvalues] = np.nan
    # if we only have NaNs set rms to nan
    if np.nansum(np.isfinite(znan)) == 0:
        rms = np.repeat(np.nan, znan.shape[0])
    # else get the rms for each order
    else:
        rms = np.nanstd(znan, axis=1)
    # repeat the rms dim2 times
    rrms = np.repeat(rms, dim2).reshape((dim1, dim2))
    # for any values > cut*mean replace spef values with speref values
    with warnings.catch_warnings(record=True) as _:
        spefc = np.where(abs(z) > cut * rrms, spereff * rnormspe, spef)
    # get the total z above cut*mean
    with warnings.catch_warnings(record=True) as _:
        cpt = np.nansum(abs(z) > cut * rrms)
    # create a normalise spectrum for the corrected spef
    cnormspe = np.nansum(spefc, axis=1) / np.nansum(spereff, axis=1)
    # get the normed spectrum for each pixel for each order
    rcnormspe = np.repeat(cnormspe, dim2).reshape((dim1, dim2))
    # get the normalised spectrum using the corrected normalised spectrum
    spen = spefc / rcnormspe
    # return parameters
    return spen, cnormspe, cpt


def calculate_rv_drifts_2d(speref, spe, wave, sigdet, threshold, size):
    """
    Calculate the RV drift between the REFERENCE (speref) and COMPARISON (spe)
    extracted spectra.

    :param speref: numpy array (2D), the REFERENCE extracted spectrum
                   size = (number of orders by number of columns (x-axis))
    :param spe:  numpy array (2D), the COMPARISON extracted spectrum
                 size = (number of orders by number of columns (x-axis))
    :param wave: numpy array (2D), the wave solution for each pixel
    :param sigdet: float, the read noise (sigdet) for calculating the
                   noise array
    :param threshold: float, upper limit for pixel values, above this limit
                      pixels are regarded as saturated
    :param size: int, size (in pixels) around saturated pixels to also regard
                 as bad pixels

    :return rvdrift: numpy array (1D), the RV drift between REFERENCE and
                     COMPARISON spectrum for each order
    """
    # flag bad pixels (less than threshold + difference less than threshold/10)
    with warnings.catch_warnings(record=True) as _:
        flag = (speref < threshold) & (spe < threshold)
        flag &= (speref - spe < threshold / 10.)
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2 * size, 1):
        flag[:, size:-size] *= flag[:, i_it: i_it - 2 * size]
    # get the wavelength normalised to the wavelength spacing
    nwave = wave[:, 1:-1] / (wave[:, 2:] - wave[:, :-2])
    # get the flux + noise array
    sxn = (speref[:, 1:-1] + sigdet ** 2)
    # get the flux difference normalised to the flux + noise
    nspe = (speref[:, 2:] - speref[:, :-2]) / sxn
    # get the mask value
    maskv = flag[:, 2:] * flag[:, 1:-1] * flag[:, :-2]
    # calculate the two sums
    sum1 = np.nansum((nwave * nspe) * (spe[:, 1:-1] - speref[:, 1:-1]) * maskv, 1)
    sum2 = np.nansum(sxn * ((nwave * nspe) ** 2) * maskv, 1)
    # calculate RV drift
    rvdrift = CONSTANT_C * (sum1 / sum2)
    # return RV drift
    return rvdrift


# =============================================================================
# Define drift-peak functions
# =============================================================================
def create_drift_file(p, loc):
    """
    Creates a reference ascii file that contains the positions of the FP peaks
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
    # get gauss function
    gf = gauss_function
    # get constants
    border = p['DRIFT_PEAK_BORDER_SIZE']
    size = p['DRIFT_PEAK_FPBOX_SIZE']
    # minimum_norm_fp_peak = p['drift_peak_min_nfp_peak']

    # get the reference data and the wave data
    speref = np.array(loc['SPEREF'])
    wave = loc['WAVE']
    lamp = loc['LAMP']

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
        limit = np.nanmedian(tmp) * p['DRIFT_PEAK_PEAK_SIG_LIM'][lamp]

        # define the maximum pixel value of the normalized array
        maxtmp = np.nanmax(tmp)
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
            # try to fit a gaussian to that peak
            try:
                # set initial guess
                p0 = [tmp[maxpos], maxpos, 1.0, np.min(tmp[index])]
                # do gauss fit
                #    gg = [mean, amplitude, sigma, dc]
                with warnings.catch_warnings(record=True) as w:
                    # noinspection PyTypeChecker
                    gg, pcov = curve_fit(gf, index, tmp[index], p0=p0)
                    w_all += list(w)
            except ValueError:
                WLOG(p, 'warning', 'ydata or xdata contains NaNS')
                gg = [np.nan, np.nan, np.nan, np.nan]
            except RuntimeError:
                # WLOG(p, 'warning', 'Least-squares fails')
                gg = [np.nan, np.nan, np.nan, np.nan]

            # little sanity check to be sure that the peak is not the same as
            #    we got before and that there is something fishy with the
            #    detection - dx is the distance from last peak
            dx = np.abs(xprev - gg[1])
            # if the distance from last position > 2 - we have a new fit
            if dx > p['DRIFT_PEAK_INTER_PEAK_SPACING']:
                # subtract off the gaussian without the dc level
                # (leave dc for other peaks
                tmp[index] -= gauss_function(index, gg[0], gg[1], gg[2], 0)
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
                rv = CONSTANT_C * deltalam / (2.0 * wave[order_num, maxpos])

                # add to storage
                ordpeak.append(order_num)
                xpeak.append(gg[1])
                ewpeak.append(gg[2])
                vrpeak.append(rv)
                llpeak.append(deltalam)
                amppeak.append(maxtmp)
            else:
                # add to rejected
                nreject += 1
            # recalculate the max peak
            maxtmp = np.max(tmp)
            # set previous peak to this one
            xprev = gg[1]
            # iterator
            ipeak += 1
        # display warning messages
        spirouCore.spirouLog.warninglogger(p, w_all)
        # log how many FPs were found and how many rejected
        wmsg = 'Order {0} : {1} peaks found, {2} peaks rejected'
        WLOG(p, '', wmsg.format(order_num, ipeak, nreject))
        # add values to all storage (and sort by xpeak)
        indsort = np.argsort(xpeak)
        allordpeak = np.append(allordpeak, np.array(ordpeak)[indsort])
        allxpeak = np.append(allxpeak, np.array(xpeak)[indsort])
        allewpeak = np.append(allewpeak, np.array(ewpeak)[indsort])
        allvrpeak = np.append(allvrpeak, np.array(vrpeak)[indsort])
        allllpeak = np.append(allllpeak, np.array(llpeak)[indsort])
        allamppeak = np.append(allamppeak, np.array(amppeak)[indsort])
    # store values in loc
    loc['ORDPEAK'] = np.array(allordpeak, dtype=int)
    loc['XPEAK'] = allxpeak
    loc['EWPEAK'] = allewpeak
    loc['VRPEAK'] = allvrpeak
    loc['LLPEAK'] = allllpeak
    loc['AMPPEAK'] = allamppeak

    # Log the total number of FP lines found
    wmsg = 'Total Nb of FP lines found = {0}'
    WLOG(p, 'info', wmsg.format(len(allxpeak)))

    # set source
    source = __NAME__ + '/create_drift_file()'
    keys = ['ordpeak', 'xpeak', 'ewpeak', 'vrpeak', 'llpeak', 'amppeak']
    loc.set_sources(keys, source)
    # return loc
    return loc


def remove_wide_peaks(p, loc, expwidth=None, cutwidth=None):
    """
    Remove peaks that are too wide

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                drift_peak_exp_width: float, the expected width of FP peaks -
                                      used to "normalise" peaks (which are then
                                      subsequently removed if >
                                      drift_peak_norm_width_cut
                drift_peak_norm_width_cut: float, the "normalised" width of
                                           FP peaks that is too large
                                           normalised width = FP FWHM -
                                           drift_peak_exp_width cut is
                                           essentially:=
                                           FP FWHM < (drift_peak_exp_width +
                                           drift_peak_norm_width_cut)
                log_opt: string, log option, normally the program name

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
    try:
        if expwidth is None:
            expwidth = p['DRIFT_PEAK_EXP_WIDTH']
        if cutwidth is None:
            cutwidth = p['DRIFT_PEAK_NORM_WIDTH_CUT']
    except spirouConfig.ConfigError as e:
        emsg1 = 'Error {0}: {1}'.format(type(e), e)
        emsg2 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2])

    # minimum spacing between FP peaks
    peak_spacing = p['DRIFT_PEAK_INTER_PEAK_SPACING']

    # define a mask to cut out wide peaks
    mask = np.abs(loc['EWPEAK'] - expwidth) < cutwidth

    # apply mask
    loc['ORDPEAK'] = loc['ORDPEAK'][mask]
    loc['XPEAK'] = loc['XPEAK'][mask]
    loc['EWPEAK'] = loc['EWPEAK'][mask]
    loc['VRPEAK'] = loc['VRPEAK'][mask]
    loc['LLPEAK'] = loc['LLPEAK'][mask]
    loc['AMPPEAK'] = loc['AMPPEAK'][mask]

    # check for and remove double-fitted lines
    # save old position
    loc['XPEAK_OLD'] = np.copy(loc['XPEAK'])
    loc['ORDPEAK_OLD'] = np.copy(loc['ORDPEAK'])
    # set up storage for good lines
    ordpeak_k, xpeak_k, ewpeak_k, vrpeak_k, llpeak_k, amppeak_k = \
        [], [], [], [], [], []
    # loop through the orders
    for order_num in range(np.shape(loc['SPEREF'])[0]):
        # set up mask for the order
        gg = loc['ORDPEAK'] == order_num
        # get the xvalues
        xpeak = loc['XPEAK'][gg]
        # get the amplitudes
        amppeak = loc['AMPPEAK'][gg]
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
        ordpeak_k += list(loc['ORDPEAK'][gg][xmask])
        xpeak_k += list(loc['XPEAK'][gg][xmask])
        ewpeak_k += list(loc['EWPEAK'][gg][xmask])
        vrpeak_k += list(loc['VRPEAK'][gg][xmask])
        llpeak_k += list(loc['LLPEAK'][gg][xmask])
        amppeak_k += list(loc['AMPPEAK'][gg][xmask])

    # replace FP peak arrays in loc
    loc['ORDPEAK'] = np.array(ordpeak_k)
    loc['XPEAK'] = np.array(xpeak_k)
    loc['EWPEAK'] = np.array(ewpeak_k)
    loc['VRPEAK'] = np.array(vrpeak_k)
    loc['LLPEAK'] = np.array(llpeak_k)
    loc['AMPPEAK'] = np.array(amppeak_k)

    # append this function to sources
    source = __NAME__ + '/remove_wide_peaks()'
    keys = ['ordpeak', 'xpeak', 'ewpeak', 'vrpeak', 'llpeak', 'amppeak']
    loc.append_sources(keys, source)

    # log number of lines removed for width
    wmsg = 'Nb of lines removed due to suspicious width = {0}'
    WLOG(p, 'info', wmsg.format(np.nansum(~mask)))
    # log number of lines removed as double-fitted
    if len(loc['XPEAK_OLD']) > len(loc['XPEAK']):
        wmsg = 'Nb of double-fitted lines removed  = {0}'
        lenx = len(loc['XPEAK_OLD']) - len(loc['XPEAK'])
        WLOG(p, 'info', wmsg.format(lenx))

    return loc


def remove_zero_peaks(p, loc):
    """
    Remove peaks that have a value of zero

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                xref: numpy array (1D), the central positions of the peaks
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

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                xref: numpy array (1D), the central positions of the peaks
                      (masked with zero peaks removed)
                ordpeak: numpy array (1D), the order number for each valid FP
                         peak (masked with zero peaks removed)
                xpeak: numpy array (1D), the central position each gaussain fit
                       to valid FP peak (masked with zero peaks removed)
                ewpeak: numpy array (1D), the FWHM of each gaussain fit
                        to valid FP peak (masked with zero peaks removed)
                vrpeak: numpy array (1D), the radial velocity drift for each
                        valid FP peak (masked with zero peaks removed)
                llpeak: numpy array (1D), the delta wavelength for each valid
                        FP peak (masked with zero peaks removed)
                amppeak: numpy array (1D), the amplitude for each valid FP peak
                         (masked with zero peaks removed)
    """
    # define a mask to cut out peaks with a value of zero
    mask = loc['XREF'] != 0

    # apply mask
    loc['XREF'] = loc['XREF'][mask]
    loc['ORDPEAK'] = loc['ORDPEAK'][mask]
    loc['XPEAK'] = loc['XPEAK'][mask]
    loc['EWPEAK'] = loc['EWPEAK'][mask]
    loc['VRPEAK'] = loc['VRPEAK'][mask]
    loc['LLPEAK'] = loc['LLPEAK'][mask]
    loc['AMPPEAK'] = loc['AMPPEAK'][mask]

    # append this function to sources
    source = __NAME__ + '/remove_zero_peaks()'
    keys = ['ordpeak', 'xpeak', 'ewpeak', 'vrpeak', 'llpeak', 'amppeak']
    loc.append_sources(keys, source)

    # log number of lines removed
    wmsg = 'Nb of lines removed with no width measurement = {0}'
    WLOG(p, 'info', wmsg.format(np.nansum(~mask)))

    # return loc
    return loc


def get_drift(p, sp, ordpeak, xpeak0, gaussfit=False):
    """
    Get the centroid of all peaks provided an input peak position

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                drift_peak_fpbox_size: int, the box half-size (in pixels) to
                                       fit an individual FP peak to - a
                                       gaussian will be fit to +/- this size
                                       from the center of the FP peak
                drift_peak_exp_width: float, the expected width of FP peaks -
                                      used to "normalise" peaks (which are then
                                      subsequently removed if >
                                      drift_peak_norm_width_cut
                log_opt: string, log option, normally the program name

    :param sp: numpy array (2D), e2ds fits file with FP peaks
               size = (number of orders x number of pixels in x-dim of image)
    :param ordpeak: numpy array (1D), order of each peak
    :param xpeak0: numpy array (1D), position in the x dimension of all peaks
    :param gaussfit: bool, if True uses a gaussian fit to get each centroid
                     (slow) or adjusts a barycenter (gaussfit=False)

    :return xpeak: numpy array (1D), the central positions of the peaks
    """
    # get the size of the peak
    size = p['DRIFT_PEAK_FPBOX_SIZE']
    width = p['DRIFT_PEAK_EXP_WIDTH']

    # measured x position of FP peaks
    xpeaks = np.zeros_like(xpeak0)

    # loop through peaks and measure position
    for peak in range(len(xpeak0)):
        # if using gaussfit
        if gaussfit:
            # get the index from -size to +size in pixels from position of peak
            #   this allows one to have sufficient baseline on either side to
            #   adjust the DC level properly
            index = np.array(range(-size, size + 1)) + int(xpeak0[peak] + 0.5)

            # get the sp values at this index and normalize them
            tmp = np.array(sp[ordpeak[peak], index])
            tmp = tmp - np.min(tmp)
            tmp = tmp / np.max(tmp)

            # sanity check that peak is within 0.5 pix of the barycenter
            v = np.nansum(index * tmp) / np.nansum(tmp)
            if np.abs(v - xpeak0[peak]) < 0.5:
                # try to gauss fit
                try:
                    # set initial guess
                    p0 = [1, xpeak0[peak], width, 0]
                    # fit a gaussian to that peak
                    #    gg = [mean, amplitude, sigma, dc]
                    with warnings.catch_warnings(record=True) as w:
                        # noinspection PyTypeChecker
                        gg, pcov = curve_fit(gauss_function, index, tmp, p0=p0)
                    spirouCore.spirouLog.warninglogger(p, w)
                    # get position
                    xpeaks[peak] = gg[1]
                except ValueError:
                    WLOG(p, 'warning',
                         'ydata or xdata contains NaNS')
                except RuntimeError:
                    wmsg = ('Problem with gaussfit (Not a big deal, one in '
                            'thousands of fits')
                    WLOG(p, 'warning', wmsg)
        # else barycenter adjustment
        else:
            # range from -2 to +2 pixels from position of peak
            # selects only the core of the line. Adding more aseline would
            # underestimate the offsets
            index = np.array(range(-2, 3)) + int(xpeak0[peak] + 0.5)
            # get sp at indices
            tmp = sp[ordpeak[peak], index]
            # get position
            xpeaks[peak] = np.nansum(index * tmp) / np.nansum(tmp)
    # finally return the xpeaks
    return xpeaks


def pearson_rtest(nbo, spe, speref):
    """
    Perform a Pearson R test on each order in spe against speref

    :param nbo: int, the number of orders
    :param spe: numpy array (2D), the extracted array for this iteration
                size = (number of orders x number of pixels in x-dim)
    :param speref: numpy array (2D), the extracted array for the reference
                   image, size = (number of orders x number of pixels in x-dim)

    :return cc_orders: numpy array (1D), the pearson correlation coefficients
                       for each order, size = (number of orders)
    """
    # set up zero array
    cc_orders = np.zeros(nbo)
    # loop around orders
    for order_num in range(nbo):
        # get this orders values
        spei = spe[order_num, :]
        sperefi = speref[order_num, :]
        # find the NaNs
        nanmask = np.isfinite(spei) & np.isfinite(sperefi)
        # perform pearson r test
        cc_orders[order_num] = pearsonr(spei[nanmask], sperefi[nanmask])[0]
    # return cc orders
    return cc_orders


def sigma_clip(loc, sigma=1.0):
    """
    Perform a sigma clip on dv

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                dv: numpy array (1D), the drift values
                ordpeak: numpy array (1D), the order number for each drift
                         value

    :param sigma: float, the sigma of the clip (away from the median)

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                dvc: numpy array (1D), the sigma clipped drift values
                orderpeakc: numpy array (1D), the order numbers for the sigma
                            clipped drift values
    """
    # get dv
    dv = loc['DV']
    # define a mask for sigma clip
    mask = np.abs(dv - np.nanmedian(dv)) < sigma * np.nanstd(dv)
    # perform sigma clip and add to loc
    loc['DVC'] = loc['DV'][mask]
    loc['ORDERPEAKC'] = loc['ORDPEAK'][mask]
    # set the source for these new parameters
    loc.set_sources(['dvc', 'orderpeakc'], __NAME__ + '/sigma_clip()')
    # return to loc
    return loc


def drift_per_order(loc, fileno):
    """
    Calculate the individual drifts per order

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                number_orders: int, the number of orders in reference spectrum
                dvc: numpy array (1D), the sigma clipped drift values
                orderpeakc: numpy array (1D), the order numbers for the sigma
                            clipped drift values

    :param fileno: int, the file number (iterator number)

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                drift: numpy array (2D), the median drift values for each
                       file and each order
                       shape = (number of files x number of orders)
                drift_left: numpy array (2D), the median drift values for the
                            left half of each order (for each file and each
                            order)
                            shape = (number of files x number of orders)
                drift_right: numpy array (2D), the median drift values for the
                             right half of each order (for each file and each
                             order)
                             shape = (number of files x number of orders)
                errdrift: numpy array (2D), the error in the drift for each
                          file and each order
                          shape = (number of files x number of orders)
    """

    # loop around the orders
    for order_num in range(loc['NUMBER_ORDERS']):
        # get the dv for this order
        dv_order = loc['DVC'][loc['ORDERPEAKC'] == order_num]
        # get the number of dvs in this order
        numdv = len(dv_order)
        # get the drift for this order
        drift = np.nanmedian(dv_order)
        driftleft = np.nanmedian(dv_order[:int(numdv / 2.0)])
        driftright = np.nanmedian(dv_order[-int(numdv / 2.0):])
        # get the error in the drift
        errdrift = np.nanstd(dv_order) / np.sqrt(numdv)

        # add to storage
        loc['DRIFT'][fileno, order_num] = drift
        loc['DRIFT_LEFT'][fileno, order_num] = driftleft
        loc['DRIFT_RIGHT'][fileno, order_num] = driftright
        loc['ERRDRIFT'][fileno, order_num] = errdrift

    # return loc
    return loc


def drift_all_orders(p, loc, fileno, nomin, nomax):
    """
    Work out the weighted mean drift across all orders

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                drift: numpy array (2D), the median drift values for each
                       file and each order
                       shape = (number of files x number of orders)
                drift_left: numpy array (2D), the median drift values for the
                            left half of each order (for each file and each
                            order)
                            shape = (number of files x number of orders)
                drift_right: numpy array (2D), the median drift values for the
                             right half of each order (for each file and each
                             order)
                             shape = (number of files x number of orders)
                errdrift: numpy array (2D), the error in the drift for each
                          file and each order
                          shape = (number of files x number of orders)

    :param fileno: int, the file number (iterator number)
    :param nomin: int, the first order to use (i.e. from nomin to nomax)
    :param nomax: int, the last order to use (i.e. from nomin to nomax)

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                meanrv: numpy array (1D), the weighted mean drift, for each file
                        shape = (number of files)
                meanrv_left: numpy array (1D), the weighted mean drift for the
                             left half of each order, for each file
                             shape = (number of files)
                meanrv_right: numpy array (1D), the weighted mean drift for the
                              right half of each order, for each file
                              shape = (number of files)
                merrdrift: numpy array (1D), the error in weighted mean for
                           each file
                           shape = (number of files)
    """

    func_name = __NAME__ + '.drift_all_orders()'
    # get data from loc
    drift = loc['DRIFT'][fileno, nomin:nomax]
    driftleft = loc['DRIFT_LEFT'][fileno, nomin:nomax]
    driftright = loc['DRIFT_RIGHT'][fileno, nomin:nomax]
    errdrift = loc['ERRDRIFT'][fileno, nomin:nomax]

    # work out weighted mean drift
    with warnings.catch_warnings(record=True) as w:
        sumerr = np.nansum(1.0 / errdrift)
        meanvr = np.nansum(drift / errdrift) / sumerr
        meanvrleft = np.nansum(driftleft / errdrift) / sumerr
        meanvrright = np.nansum(driftright / errdrift) / sumerr
        merrdrift = 1.0 / np.sqrt(np.nansum(1.0 / errdrift ** 2))
    # log warnings
    spirouCore.WarnLog(p, w, funcname=func_name)

    # add to storage
    loc['MEANRV'][fileno] = meanvr
    loc['MEANRV_LEFT'][fileno] = meanvrleft
    loc['MEANRV_RIGHT'][fileno] = meanvrright
    loc['MERRDRIFT'][fileno] = merrdrift

    # return loc
    return loc


# =============================================================================
# Define ccf used functions
# =============================================================================
def get_ccf_mask(p, loc, filename=None):
    """
    Get the CCF mask

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                ccf_mask: string, the name (and or location) of the CCF
                          mask file
                ic_w_mask_min: float, the weight of the CCF mask (if 1 force
                               all weights equal)
                ic_mask_width: float, the width of the template line
                               (if 0 use natural
                log_opt: string, log option, normally the program name

    :param loc: parameter dictionary, ParamDict containing data

    :param filename: string or None, the filename and location of the ccf mask
                     file, if None then file names is gotten from p['CCF_MASK']

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                ll_mask_d: numpy array (1D), the size of each pixel
                           (in wavelengths)
                ll_mask_ctr: numpy array (1D), the central point of each pixel
                             (in wavelengths)
                w_mask: numpy array (1D), the weight mask
    """
    func_name = __NAME__ + '.get_ccf_mask()'
    # get constants from p
    mask_min = p['IC_W_MASK_MIN']
    mask_width = p['IC_MASK_WIDTH']

    if filename is None:
        try:
            filename = p['CCF_MASK']
        except spirouConfig.ConfigError as e:
            emsg1 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [e.message, emsg1])

    # try to locate mask
    filename = locate_mask(p, filename)
    # speed of light in km/s
    c = CONSTANT_C / 1000.0
    # get table if not found raise error
    try:
        cols = ['ll_mask_s', 'll_mask_e', 'w_mask']
        ccfmask = spirouImage.ReadTable(p, filename, fmt='ascii',
                                        colnames=cols)
    except IOError:
        emsg = 'Template file: "{0}" not found, unable to proceed'
        WLOG(p, 'error', emsg.format(filename))
        ccfmask = None
    # log that we are using a specific RV template with x rows
    wmsg = 'Using RV template: {0} ({1} rows)'
    wargs = [os.path.split(filename)[-1], len(ccfmask['ll_mask_s'])]
    WLOG(p, '', wmsg.format(*wargs))
    # calculate the difference in mask_e and mask_s
    ll_mask_d = np.array(ccfmask['ll_mask_e']) - np.array(ccfmask['ll_mask_s'])
    ll_mask_ctr = np.array(ccfmask['ll_mask_s']) + ll_mask_d * 0.5
    # if mask_width > 0 ll_mask_d is multiplied by mask_width/c
    if mask_width > 0:
        ll_mask_d = mask_width * np.array(ccfmask['ll_mask_s']) / c
    # make w_mask an array
    w_mask = np.array(ccfmask['w_mask'])
    # use w_min to select on w_mask or keep all if w_mask_min >= 1
    if mask_min < 1.0:
        mask = w_mask > mask_min
        ll_mask_d = ll_mask_d[mask]
        ll_mask_ctr = ll_mask_ctr[mask]
        w_mask = w_mask[mask]
    # else set all w_mask to one (and use all lines in file)
    else:
        w_mask = np.ones(len(ll_mask_d))
    # add to loc
    loc['LL_MASK_D'] = ll_mask_d
    loc['LL_MASK_CTR'] = ll_mask_ctr
    loc['W_MASK'] = w_mask
    # set source
    source = __NAME__ + '/get_ccf_mask()'
    loc.set_sources(['ll_mask_d', 'll_mask_ctr', 'w_mask'], source)
    # return loc
    return loc


def locate_mask(p, filename):
    """
    Search for mask file if the filename does not contain a valid path
    the search in the default data folder
    (defined in spirouConfig.Constants.CDATA_FOLDER())

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name

    :param filename: string, the filename (or filename and path) to search for
                     the mask file
    :return abspath: string, the absolute path of the found mask, or raises an
                     error
    """
    func_name = __NAME__ + '.locate_mask()'
    # check if filename exists
    if os.path.exists(filename):
        abspath = os.path.join(os.getcwd(), filename)
        wmsg = 'Template used for CCF computation: {0}'
        WLOG(p, '', wmsg.format(abspath))
    else:
        # get package name and relative path
        package = spirouConfig.Constants.PACKAGE()
        relfolder = spirouConfig.Constants.CCF_MASK_DIR()
        # get absolute folder path from package and relfolder
        absfolder = spirouConfig.GetAbsFolderPath(package, relfolder)
        # strip filename
        filename = os.path.split(filename)[-1]
        # get absolute path and filename
        abspath = os.path.join(absfolder, filename)
        # if path exists use it
        if os.path.exists(abspath):
            wmsg = 'Template used for CCF computation: {0}'
            WLOG(p, 'info', wmsg.format(abspath))
        # else raise error
        else:
            emsg1 = 'Template file: "{0}" not found, unable to proceed'
            emsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [emsg1.format(filename),
                                         emsg2])
    # return abspath
    return abspath


def coravelation(p, loc, log=False):
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
    ccf_step = p['CCF_STEP']
    det_noise = p['CCF_DET_NOISE']
    fit_type = p['CCF_FIT_TYPE']
    # speed of light in km/s
    c = CONSTANT_C / 1000.0
    # -------------------------------------------------------------------------
    # get data from loc
    # -------------------------------------------------------------------------
    # get the wavelengths for the lines and the fit coefficients for each line
    ll_map, coeff_ll = loc['WAVE_LL'], loc['PARAM_LL']
    # get the line centers and the line widths
    ll_mask_ctr, ll_mask_d = loc['LL_MASK_CTR'], loc['LL_MASK_D']
    # get the line weights
    w_mask = loc['W_MASK']
    # get the flat fielded flux values
    s2d = loc['E2DSFF']
    # get the blaze values
    blaze = loc['BLAZE']
    # get the Barycentric Earth Velocity calculation
    berv = loc['BERV']
    berv_max = loc['BERV_MAX']

    # TODO: Is this okay to do this?
    if ~np.isfinite(berv):
        berv = 0.0
        berv_max = 0.0
    # -------------------------------------------------------------------------
    # log that we are computing ccf
    if log:
        wmsg = 'Computing CCF at RV= {0:6.1f} [km/s]'
        WLOG(p, '', wmsg.format(p['TARGET_RV']))
    # -------------------------------------------------------------------------
    # get rvmin and rvmax
    if 'RVMIN' not in p:
        p['RVMIN'] = p['TARGET_RV'] - p['CCF_WIDTH']
        p.set_source('RVMIN', func_name)
    if 'RVMAX' not in p:
        p['RVMAX'] = p['TARGET_RV'] + p['CCF_WIDTH'] + ccf_step
        p.set_source('RVMAX', func_name)
    # create a rv ccf range
    rv_ccf = np.arange(p['RVMIN'], p['RVMAX'], ccf_step)
    # -------------------------------------------------------------------------
    # calculate modified map
    ll_map_b = ll_map * (1.0 + 1.55e-8) * (1.0 + berv / c)
    # calculate modified coefficients
    coeff_ll_b = coeff_ll * (1.0 + 1.55e-8) * (1.0 + berv / c)
    # get the differential map
    dll_map = spirouMath.get_dll_from_coefficients(coeff_ll_b, len(ll_map[0]),
                                                   len(coeff_ll))
    # -------------------------------------------------------------------------
    # define some constants for loop
    constant1 = (1 + 1.55e-8) * (1 + berv_max / c)
    constant2 = (1 + 1.55e-8) * (1 - berv_max / c)
    rvshift = 1 + rv_ccf / c
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
    if p['DRS_PLOT'] and p['DRS_DEBUG'] == 2:
        # start interactive plot
        sPlt.start_interactive_session(p)
        # define a figure
        fig = sPlt.define_figure()
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
        if np.nansum(cond) > 0:
            # -----------------------------------------------------------------
            # calculate the CCF
            ccf_args = [ll_sub_mask_ctr, ll_sub_mask_d, w_sub_mask,
                        ll_map_b[order_num], s2d[order_num],
                        dll_map[order_num], blaze[order_num],
                        rv_ccf, det_noise]
            ccf_o, pix_passed, ll_range, ccf_noise = calculate_ccf(*ccf_args)
            # -----------------------------------------------------------------
            # fit the CCF
            fit_args = [p, rv_ccf, np.array(ccf_o), fit_type]
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
        ccf_max.append(np.nanmax(ccf_o))
        ccf_all_fit.append(ccf_o_fit)
        ccf_all_results.append(ccf_o_results)
        pix_passed_all.append(pix_passed)
        ll_range_all.append(ll_range)
        # ---------------------------------------------------------------------
        # Plots
        # ---------------------------------------------------------------------
        if p['DRS_PLOT'] and len(ll_sub_mask_ctr) > 0 and p['DRS_DEBUG'] == 2:
            # Plot rv vs ccf (and rv vs ccf_fit)
            sPlt.ccf_rv_ccf_plot(p, rv_ccf, ccf_o, ccf_o_fit, order=order_num,
                                 fig=fig)

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
    loc['RV_CCF'] = rv_ccf
    loc['CCF'] = ccf_all
    loc['CCF_MAX'] = ccf_max
    loc['PIX_PASSED_ALL'] = pix_passed_all
    loc['TOT_LINE'] = tot_line
    loc['LL_RANGE_ALL'] = ll_range_all
    loc['CCF_NOISE'] = ccf_noise_all
    loc['ORDERS'] = orders
    loc['CCF_ALL_RESULTS'] = ccf_all_results

    # set source
    keys = ['rv_ccf', 'ccf', 'ccf_max', 'pix_passed_all', 'tot_line',
            'll_range_all', 'ccf_noise', 'orders', 'ccf_all_results']
    loc.set_sources(keys, __NAME__ + '/coravelation()')
    # -------------------------------------------------------------------------
    # return loc
    return loc


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

    # speed of light in km/s
    c = CONSTANT_C / 1000.0

    # constants
    sp_ll_dll = sp_ll + sp_dll * 0.5
    mask_ll_d1 = mask_ll - 0.5 * mask_d
    mask_ll_d2 = mask_ll + 0.5 * mask_d
    rv_corr = 1 + rv_ccf / c
    # get the line centers
    line_ctr = mask_ll * (1 + rv_ccf[int(len(rv_ccf) / 2)] / c)
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


# TODO: Something is wrong with "cond3"
# TODO: For loop starting:
# TODO:    for i in range(len(i_start)):
# TODO:        start, end = i_start[cond3][i], i_end[cond3][i]
# TODO:  is wrong and is not the same as old function
# TODO:      "correlbin"
#
# def new_correlbin(flux, ll, dll, blaze, ll_s, ll_e, ll_wei, i_start, i_end,
#                   i_line_ctr, det_noise):
#     """
#     Optimized (Fortran translate) of correlbin
#
#     Timing statistics:
#
#     raw_correlbin
#     523 µs ± 62.8 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
#
#     correlbin
#     126 µs ± 13.5 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
#
#     fortran
#     2.56 µs per loop
#
#     :param flux: numpy array (1D), the flux values for this order
#                  size = (number of columns in e2ds file [x-dimension])
#     :param ll: numpy array (1D), the wavelength values for this order
#                size = (number of columns in e2ds file [x-dimension])
#     :param dll: numpy array (1D), the derivative of the line list fits for
#                 this order
#                 size = (number of columns in e2ds file [x-dimension])
#     :param blaze: numpy array (1D), the blaze values for this order
#                   size = (number of columns in e2ds file [x-dimension])
#     :param ll_s: numpy array (1D), the wavelength at the blue end of each line
#                  size = (number of lines to use)
#     :param ll_e: numpy array (1D), the wavelength at the red end of each line
#                  size = (number of lines to use)
#     :param ll_wei: numpy array (1D), the weights of each line
#                    size = (number of lines to use)
#     :param i_start: numpy array (1D), the indices ll where ll_s would appear if
#                     inserted and sorted (i.e. the bin position to at the blue
#                     end of each line in the main image)
#                     size = (number of lines to use)
#     :param i_end: numpy array (1D), the indices ll where ll_e would appear if
#                   inserted and sorted (i.e. the bin position to at the red
#                   end of each line in the main image)
#                   size = (number of lines to use)
#     :param i_line_ctr: numpy array (1D), the indices ll where the line centers
#                        would appear if inserted and sorted (i.e. the bin
#                        position to at the red end of each line in the main
#                        image)
#                        size = (number of lines to use)
#     :param det_noise: float, the detector noise
#
#     :return out_ccf: float, the calculated CCF
#     :return pix: float, the last pix value?
#     :return llrange: float, the line list range?
#     :return ccf_noise: float, the calculated CCF noise
#     """
#     # get sizes of arrays
#     # nx = len(flux)
#     nfind = len(ll_s)
#     # set up outputs
#     out_ccf = 0.0
#     pix = 0.0
#     llrange = 0.0
#     ccf_noise = 0.0
#     # set up storage
#     pix_s = np.zeros(nfind)
#     pix_e = np.zeros(nfind)
#     out = np.zeros(nfind)
#     noise = np.zeros(nfind)
#
#     # adjust from fortran indexing to python indexing
#     i_start = i_start - 1
#     i_end = i_end - 1
#     i_line_ctr = i_line_ctr - 1
#
#     # -------------------------------------------------------------------------
#     # condition   start = end
#     # -------------------------------------------------------------------------
#     # condition definition
#     cond1 = i_start == i_end
#     # only continue if we have some terms
#     if np.nansum(cond1) > 0:
#         # define masked arrays
#         dll_start = (dll[i_start])[cond1]
#         flux_start = (flux[i_start])[cond1]
#         blaze_start = (blaze[i_start])[cond1]
#         blaze_cent = (blaze[i_line_ctr])[cond1]
#         weight = ll_wei[cond1]
#         # define intermediates
#         pix_s[cond1] = (ll_e[cond1] - ll_s[cond1]) / dll_start
#         out[cond1] = pix_s[cond1] * flux_start / blaze_start
#         noise[cond1] = pix_s[cond1] * np.abs(flux_start)
#         noise[cond1] += pix_s[cond1] * det_noise ** 2
#         # calculate sums
#         out_ccf += np.nansum(out[cond1] * weight * blaze_cent)
#         pix += np.nansum(pix_s[cond1] * weight)
#         llrange += np.nansum(pix_s[cond1] * dll_start * weight)
#         ccf_noise += np.nansum(noise[cond1] * weight ** 2)
#     # -------------------------------------------------------------------------
#     # condition   start + 1 = end
#     # -------------------------------------------------------------------------
#     # condition definition
#     cond2 = (i_start + 1) == i_end
#     # only continue if we have some terms
#     if np.nansum(cond2) > 0:
#         # define masked arrays
#         ll_start = (ll[i_start])[cond2]
#         dll_start = (dll[i_start])[cond2]
#         dll_end = (dll[i_end])[cond2]
#         flux_start = (flux[i_start])[cond2]
#         flux_end = (flux[i_end])[cond2]
#         blaze_start = (blaze[i_start])[cond2]
#         blaze_end = (blaze[i_end])[cond2]
#         blaze_cent = (blaze[i_line_ctr])[cond2]
#         weight = ll_wei[cond2]
#         # define intermediates
#         pix_s[cond2] = (ll_start + (0.5 * dll_start) - ll_s[cond2]) / dll_start
#         pix_e[cond2] = (ll_e[cond2] - ll_start - (0.5 * dll_start)) / dll_end
#         out[cond2] = pix_s[cond2] * flux_start / blaze_start
#         out[cond2] += pix_e[cond2] * flux_end / blaze_end
#         noise[cond2] = pix_s[cond2] * np.abs(flux_start)
#         noise[cond2] += pix_e[cond2] * np.abs(flux_end)
#         noise[cond2] += (pix_s[cond2] + pix_e[cond2]) * det_noise ** 2
#         llrangetmp = (pix_s[cond2] * dll_start + pix_e[cond2] * dll_end)
#         # calculate sums
#         out_ccf += np.nansum(out[cond2] * weight * blaze_cent)
#         pix += np.nansum((pix_s[cond2] + pix_e[cond2]) * weight)
#         llrange += np.nansum(llrangetmp * weight)
#         ccf_noise += np.nansum(noise[cond2] * weight ** 2)
#     # -------------------------------------------------------------------------
#     # condition   not (cond1 or cond2)
#     # -------------------------------------------------------------------------
#     # condition definition
#     cond3 = ~(cond1 | cond2)
#     # only continue if we have some terms
#     if np.nansum(cond3) > 0:
#         # define masked arrays
#         ll_start = (ll[i_start])[cond3]
#         ll_end1 = (ll[i_end - 1])[cond3]
#         dll_start = (dll[i_start])[cond3]
#         dll_end = (dll[i_end])[cond3]
#         dll_end1 = (dll[i_end - 1])[cond3]
#         flux_start = (flux[i_start])[cond3]
#         flux_end = (flux[i_end])[cond3]
#         blaze_start = (blaze[i_start])[cond3]
#         blaze_end = (blaze[i_end])[cond3]
#         blaze_cent = (blaze[i_line_ctr])[cond3]
#         weight = ll_wei[cond3]
#         # define intermediates
#         pix_s[cond3] = (ll_start + (dll_start * 0.5) - ll_s[cond3]) / dll_start
#         pix_e[cond3] = (ll_e[cond3] - ll_end1 - (0.8 * dll_end1)) / dll_end
#         out[cond3] = pix_s[cond3] * flux_start / blaze_start
#         out[cond3] += pix_e[cond3] * flux_end / blaze_end
#         noise[cond3] = pix_s[cond3] * np.abs(flux_start)
#         noise[cond3] += pix_e[cond3] * np.abs(flux_end)
#         noise[cond3] += (pix_s[cond3] + pix_e[cond3]) * det_noise ** 2
#         llrangetmp = (pix_s[cond3] * dll_start + pix_e[cond3] * dll_end)
#         # calculate sums
#         out_ccf += np.nansum(out[cond3] * weight * blaze_cent)
#         pix += np.nansum((pix_s[cond3] + pix_e[cond3]) * weight)
#         llrange += np.nansum(llrangetmp * weight)
#         ccf_noise += np.nansum(noise[cond3] * weight ** 2)
#         # calculate fractional contributions
#         out_ccf_i = 0.0
#         llrange_i = 0.0
#         ccf_noise_i = 0.0
#         for i in range(len(i_start)):
#             start, end = i_start[cond3][i], i_end[cond3][i]
#             out_ccf_i += np.nansum(flux[start:end - 1] / blaze[start:end - 1])
#             llrange_i += np.nansum(dll[start:end - 1])
#             # ccf noise calculation
#             noisetmp = np.abs(flux[start:end - 1] + det_noise ** 2)
#             ccf_noise_i += np.nansum(noisetmp)
#         # add fractional contributions to totals
#         out_ccf += (np.nansum(out_ccf_i * weight * blaze_cent))
#         pix += (np.nansum(weight) * len(i_start))
#         llrange += (np.nansum(llrange_i * weight))
#         ccf_noise += (np.nansum(ccf_noise_i * weight ** 2))
#     # sqrt the noise
#     ccf_noise = np.sqrt(ccf_noise)
#     # return parameters
#     return out_ccf, pix, llrange, ccf_noise


def fit_ccf(p, rv, ccf, fit_type):
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
    # deal with inconsistent lengths
    if len(rv) != len(ccf):
        emsg = ('Error "rv" (len={0}) and "ccf" (len={1}) are not the same '
                'length (in {2})')
        eargs = [len(rv), len(ccf), __NAME__ + '/fit_ccf()']
        WLOG(p, 'error', emsg.format(*eargs))

    # get constants
    max_ccf, min_ccf = np.nanmax(ccf), np.nanmin(ccf)
    argmin, argmax = np.argmin(ccf), np.argmax(ccf)
    diff = max_ccf - min_ccf
    rvdiff = rv[1] - rv[0]
    # set up guess for gaussian fit
    # if fit_type == 0 then we have absorption lines
    if fit_type == 0:
        if np.nanmax(ccf) != 0:
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

    result, fit = spirouMath.fitgaussian(x, y, weights=w, guess=a)

    ccf_fit = (fit + 1 - fit_type) * max_ccf
    # return the best guess and the gaussian fit
    return result, ccf_fit


# =============================================================================
# Define file functions
# =============================================================================
def get_fiberc_e2ds_name(p, hdr):
    # This depends on the input filetype
    if p['KW_OUTPUT'][0] not in hdr:
        emsg = 'Cannot find HEADER KEY = "{0}" - Fatal Error'
        eargs = [p['KW_OUTPUT'][0]]
        WLOG(p, '', emsg.format(*eargs))
        return None
    else:
        outputkey = hdr[p['KW_OUTPUT'][0]]
    # -------------------------------------------------------------------------
    # first guess at the filename is the E2DS filename
    ab_file = p['E2DSFILENAME']
    # -------------------------------------------------------------------------
    # Deal with E2DS/E2DSFF files
    # TODO: Do not hard code EXT_E2DS
    if outputkey.startswith('EXT_E2DS_') or outputkey.startswith('EXT_E2DS_FF'):
        # deal with fiber manually
        if outputkey.endswith('_AB'):
            # locate and return C file
            c_file = ab_file.replace('_AB', '_C')
            abspath = os.path.join(p['ARG_FILE_DIR'], c_file)
            return abspath
        if outputkey.endswith('_A'):
            # locate and return C file
            c_file = ab_file.replace('_A', '_C')
            abspath = os.path.join(p['ARG_FILE_DIR'], c_file)
            return abspath
        if outputkey.endswith('_B'):
            # locate and return C file
            c_file = ab_file.replace('_B', '_C')
            abspath = os.path.join(p['ARG_FILE_DIR'], c_file)
            return abspath
    # -------------------------------------------------------------------------
    # deal with TELLU_CORRECTED and POL_ FILES
    # TODO: Do not hard code TELLU_CORRECTED and POL_
    # TODO: What about when we have multiple input files
    if outputkey.startswith('TELLU_CORRECTED') or outputkey.startswith('POL_'):
        # get the infile name
        infile_keyword = p['KW_INFILE1'][0].format(0)
        if infile_keyword not in hdr:
            emsg = 'Header key = "{0}" missing from file={1}'
            eargs = [infile_keyword, ab_file]
            WLOG(p, 'error', emsg.format(*eargs))
            return None
        # get the ab file name
        ab_file = hdr[infile_keyword]
        # deal with fiber manually
        if outputkey.endswith('_AB'):
            # locate and return C file
            c_file = ab_file.replace('_AB', '_C')
            abspath = os.path.join(p['ARG_FILE_DIR'], c_file)
            return abspath
        if outputkey.endswith('_A'):
            # locate and return C file
            c_file = ab_file.replace('_A', '_C')
            abspath = os.path.join(p['ARG_FILE_DIR'], c_file)
            return abspath
        if outputkey.endswith('_B'):
            # locate and return C file
            c_file = ab_file.replace('_B', '_C')
            abspath = os.path.join(p['ARG_FILE_DIR'], c_file)
            return abspath
    # -------------------------------------------------------------------------
    # if we are still in the code we have an invalid outputkey
    emsg = '{0} = "{1}" invalid for recipe for file {2}'
    eargs = [p['KW_OUTPUT'][0], outputkey, p['E2DSFILENAME']]
    WLOG(p, 'error', emsg.format(*eargs))
    return None


# =============================================================================
# End of code
# =============================================================================

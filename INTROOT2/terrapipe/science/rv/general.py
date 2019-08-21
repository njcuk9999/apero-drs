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
from scipy.optimize import curve_fit
import warnings

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core import math
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file


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
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

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
    gfunc = math.gauss_function
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
        limit = np.nanmedian(tmp) * siglimdict[lamp]

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
            maxtmp = np.max(tmp)
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
            allordpeak = np.append(allordpeak, np.array(ordpeak)[indsort])
            allxpeak = np.append(allxpeak, np.array(xpeak)[indsort])
            allewpeak = np.append(allewpeak, np.array(ewpeak)[indsort])
            allvrpeak = np.append(allvrpeak, np.array(vrpeak)[indsort])
            allllpeak = np.append(allllpeak, np.array(llpeak)[indsort])
            allamppeak = np.append(allamppeak, np.array(amppeak)[indsort])
    # store values in loc
    props['ORDPEAK'] = np.array(allordpeak, dtype=int)
    props['XPEAK'] = allxpeak
    props['EWPEAK'] = allewpeak
    props['VRPEAK'] = allvrpeak
    props['LLPEAK'] = allllpeak
    props['AMPPEAK'] = allamppeak
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
    mask = np.abs(props['EWPEAK'] - expwidth) < cutwidth

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
    wargs = [np.nansum(~mask)]
    WLOG(params, 'info', TextEntry('40-018-00003', args=wargs))

    # log number of lines removed as double-fitted
    if len(props['XPEAK_OLD']) > len(props['XPEAK']):
        wargs = [len(props['XPEAK_OLD']) - len(props['XPEAK'])]
        WLOG(params, 'info', TextEntry('40-018-00004', args=wargs))

    # return props
    return props


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

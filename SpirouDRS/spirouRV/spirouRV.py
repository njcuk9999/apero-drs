#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-21 at 11:52

@author: cook

Version 0.0.1
"""
from __future__ import division
import numpy as np
from astropy import constants
from scipy.stats.stats import pearsonr
from scipy.optimize import curve_fit
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouRV.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
ConfigError = spirouConfig.ConfigError
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# get speed of light
CONSTANT_C = constants.c.value

# switch between new and old
# TODO: Should be new
OLDCODEEXACT = False

# =============================================================================
# Define main functions
# =============================================================================
def delta_v_rms_2d(spe, wave, sigdet, threshold, size):
    # flag (saturated) fluxes above threshold as "bad pixels"
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
    tot = np.sum(sxn * ((nwave * nspe) ** 2) * maskv, axis=1)
    # convert to dvrms2
    dvrms2 = (CONSTANT_C ** 2) / abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1. / np.sqrt(np.sum(1.0 / dvrms2))
    # return dv rms and weighted mean
    return dvrms2, weightedmean


def renormalise_cosmic2d(speref, spe, threshold, size, cut):
    # flag (saturated) fluxes above threshold as "bad pixels"
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
    normspe = np.sum(spef, axis=1) / np.sum(spereff, axis=1)
    # get normed spectrum for each pixel for each order
    rnormspe = np.repeat(normspe, dim2).reshape((dim1, dim2))
    # get the sum of values for the combined speref and spe for each order
    stotal = np.sum(spereff + spef, axis=1) / dim2
    stotal = np.repeat(stotal, dim2).reshape((dim1, dim2))
    # get difference over the normalised spectrum
    ztop = spereff - spef / rnormspe
    zbottom = (spef / rnormspe) + spereff + stotal
    z = ztop / zbottom
    # get good values
    goodvalues = abs(z) > 0
    # set the bad values to NaN
    znan = np.copy(z)
    znan[~goodvalues] = np.nan
    # get the rms for each order
    rms = np.nanstd(znan, axis=1)
    # repeat the rms dim2 times
    rrms = np.repeat(rms, dim2).reshape((dim1, dim2))
    # for any values > cut*mean replace spef values with speref values
    spefc = np.where(abs(z) > cut * rrms, spereff * rnormspe, spef)
    # get the total z above cut*mean
    cpt = np.sum(abs(z) > cut * rrms)
    # create a normalise spectrum for the corrected spef
    cnormspe = np.sum(spefc, axis=1) / np.sum(spereff, axis=1)
    # get the normed spectrum for each pixel for each order
    rcnormspe = np.repeat(cnormspe, dim2).reshape((dim1, dim2))
    # get the normalised spectrum using the corrected normalised spectrum
    spen = spefc / rcnormspe
    # return parameters
    return spen, cnormspe, cpt


def calculate_rv_drifts_2d(speref, spe, wave, sigdet, threshold, size):
    # flag bad pixels (less than threshold + difference less than threshold/10)
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
    sum1 = np.sum((nwave * nspe) * (spe[:, 1:-1] - speref[:, 1:-1]) * maskv, 1)
    sum2 = np.sum(sxn * ((nwave * nspe) ** 2) * maskv, 1)
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

    :param p: parameter dictionary, storage of constants
    :param loc: parameter dictionary, storage of data

    :return loc: parameter dictionary, updated with new data
    """
    # get gauss function
    gf = gauss_function
    # get constants
    border = p['drift_peak_border_size']
    size = p['drift_peak_fpbox_size']
    minimum_norm_fp_peak = p['drift_peak_min_nfp_peak']
    # get the reference data and the wave data
    speref = np.array(loc['speref'])
    wave = loc['wave']

    # storage for order of peaks
    allordpeak = []
    allxpeak = []
    allewpeak = []
    allvrpeak = []

    # loop through the orders
    for order_num in range(speref.shape[0]):
        # storage for order of peaks
        ordpeak = []
        xpeak = []
        ewpeak = []
        vrpeak = []
        # get the pixels for this order
        tmp = np.array(speref[order_num, :])
        # For numerical sanity all values less than zero set to zero
        tmp[tmp < 0] = 0
        # set border pixels to zero to avoid fit starting off the edge of image
        # TODO: Change to constant border
        if not OLDCODEEXACT:
            tmp[0: border+1] = 0
            tmp[-(border+1):] = 0
        else:
            tmp[0:3] = 0
            tmp[speref.shape[1] - 5: speref.shape[1] -1] = 0
        # normalize by the 98th percentile - avoids super-spurois pixels but
        #   keeps the top of the blaze around 1
        # TODO: Change to np.percentile
        if not OLDCODEEXACT:
            norm = np.percentile(tmp, 98)
        else:
            tmp2 = np.sort(tmp)
            norm = tmp2[int(len(tmp2)*0.98)]

        tmp /= norm
        # define the maximum pixel value of the normalized array
        maxtmp = np.max(tmp)
        # set up loop constants
        xprev, ipeak = -99, 0
        nreject = 0
        # loop for peaks that are above a value of 0.25 (recall we normalized
        #     to the 98th percentile
        while maxtmp > minimum_norm_fp_peak:
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
                    gg, pcov = curve_fit(gf, index, tmp[index], p0=p0)
                spirouCore.spirouLog.warninglogger(w)
            except ValueError:
                WLOG('warning', p['log_opt'], 'ydata or xdata contains NaNS')
                # TODO: fix this
                if not OLDCODEEXACT:
                    gg = [np.nan, np.nan, np.nan, np.nan]
            except RuntimeError:
                # WLOG('warning', p['log_opt'], 'Least-squares fails')
                # TODO: fix this
                if not OLDCODEEXACT:
                    gg = [np.nan, np.nan, np.nan, np.nan]

            # little sanity check to be sure that the peak is not the same as
            #    we got before and that there is something fishy with the
            #    detection - dx is the distance from last peak
            dx = np.abs(xprev - gg[1])
            # if the distance from last position > 2 - we have a new fit
            if dx > 2:
                # subtract off the gaussian without the dc level
                # (leave dc for other peaks
                tmp[index] -= gauss_function(index, gg[0], gg[1], gg[2], 0)
            # else just set this region to zero, this is a bogus peak that
            #    cannot be fitted
            else:
                tmp[index] = 0

            # only keep peaks within +/- 1 pixel of original peak
            #  (gaussian fit is to find sub-pixel value)
            # TODO: fix this
            if not OLDCODEEXACT:
                cond = np.abs(maxpos - gg[1]) < 1
            else:
                cond = True

            if cond:
                # work out the radial velocity of the peak
                lambefore = wave[order_num, maxpos - 1]
                lamafter = wave[order_num, maxpos + 1]
                deltalam = lamafter - lambefore
                # TODO: use CONSTANT_C
                if not OLDCODEEXACT:
                    rv = CONSTANT_C * deltalam/(2.0 * wave[order_num, maxpos])
                else:
                    rv = 3.e8 * deltalam / (2.0 * wave[order_num, maxpos])
                # add to storage
                ordpeak.append(order_num)
                xpeak.append(gg[1])
                ewpeak.append(gg[2])
                vrpeak.append(rv)
            else:
                # add to rejected
                nreject += 1
            # recalculate the max peak
            maxtmp = np.max(tmp)
            # set previous peak to this one
            xprev = gg[1]
            # iterator
            ipeak += 1
        # log how many FPs were found and how many rejected
        wmsg = 'Order {0} : {1} peaks found, {2} peaks rejected'
        WLOG('', p['log_opt'], wmsg.format(order_num, ipeak, nreject))
        # add values to all storage (and sort by xpeak)
        indsort = np.argsort(xpeak)
        allordpeak = np.append(allordpeak, np.array(ordpeak)[indsort])
        allxpeak = np.append(allxpeak, np.array(xpeak)[indsort])
        allewpeak = np.append(allewpeak, np.array(ewpeak)[indsort])
        allvrpeak = np.append(allvrpeak, np.array(vrpeak)[indsort])

    # store values in loc
    loc['ordpeak'] = np.array(allordpeak, dtype=int)
    loc['xpeak'] = allxpeak
    loc['ewpeak'] = allewpeak
    loc['vrpeak'] = allvrpeak

    # Log the total number of FP lines found
    wmsg = 'Total Nb of FP lines found = {0}'
    WLOG('info', p['log_opt'], wmsg.format(len(allxpeak)))

    # set source
    source = __NAME__ + '/create_drift_file()'
    loc.set_sources(['ordpeak', 'xpeak', 'ewpeak', 'vrpeak'], source)
    # return loc
    return loc


def gauss_function(x, a, x0, sigma, dc):
    """
    A standard gaussian function (for fitting against)]=

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian
    :param dc: float, the constant level below the gaussian

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    return a * np.exp(-0.5 * ((x - x0) / sigma) ** 2) + dc


def remove_wide_peaks(p, loc):

    # get constants
    expwidth = p['drift_peak_exp_width']
    cutwidth = p['drift_peak_norm_width_cut']

    # define a mask to cut out wide peaks
    mask = np.abs(loc['ewpeak'] - expwidth) < cutwidth

    # apply mask
    loc['ordpeak'] = loc['ordpeak'][mask]
    loc['xpeak'] = loc['xpeak'][mask]
    loc['ewpeak'] = loc['ewpeak'][mask]
    loc['vrpeak'] = loc['vrpeak'][mask]

    # append this function to sources
    source = __NAME__ + '/remove_wide_peaks()'
    loc.append_sources(['ordpeak', 'xpeak', 'ewpeak', 'vrpeak'], source)

    # log number of lines removed
    wmsg = 'Nb of lines removed due to suspicious width = {0}'
    WLOG('info', p['log_opt'], wmsg.format(np.sum(~mask)))

    # return loc
    return loc


def remove_zero_peaks(p, loc):

    # define a mask to cut out peaks with a value of zero
    mask = loc['xref'] != 0

    # apply mask
    loc['xref'] = loc['xref'][mask]
    loc['ordpeak'] = loc['ordpeak'][mask]
    loc['xpeak'] = loc['xpeak'][mask]
    loc['ewpeak'] = loc['ewpeak'][mask]
    loc['vrpeak'] = loc['vrpeak'][mask]

    # append this function to sources
    source = __NAME__ + '/remove_zero_peaks()'
    loc.append_sources(['xref', 'ordpeak', 'xpeak', 'ewpeak', 'vrpeak'], source)

    # log number of lines removed
    wmsg = 'Nb of lines removed with no width measurement = {0}'
    WLOG('info', p['log_opt'], wmsg.format(np.sum(~mask)))

    # return loc
    return loc


def get_drift(p, sp, ordpeak, xpeak0, gaussfit=False):
    """
    Get the centroid of all peaks provided an input peak position

    :param p: parameter dictionary, parameter dictionary containing constants
    :param sp: numpy array (2D), e2ds fits file with FP peaks
               size = (number of orders x number of pixels in x-dim of image)
    :param ordpeak: numpy array (1D), order of each peak
    :param xpeak0: numpy array (1D), position in the x dimension of all peaks
    :param gaussfit: bool, if True uses a gaussian fit to get each centroid
                     (slow) or adjusts a barycenter (gaussfit=False)

    :return xpeak: numpy array (1D), the central positions if the peaks
    """
    # get the size of the peak
    size = p['drift_peak_fpbox_size']

    # measured x position of FP peaks
    xpeaks = np.zeros_like(xpeak0)

    # loop through peaks and measure position
    for peak in range(len(xpeak0)):
        # if using gaussfit
        if gaussfit:
            # get the index from -size to +size in pixels from position of peak
            #   this allows one to have sufficient baseline on either side to
            #   adjust the DC level properly
            index = np.array(range(-size, size+1)) + int(xpeak0[peak] + 0.5)

            # get the sp values at this index and normalize them
            tmp = np.array(sp[ordpeak[peak], index])
            tmp = tmp - np.min(tmp)
            tmp = tmp/np.max(tmp)

            # sanity check that peak is within 0.5 pix of the barycenter
            v = np.sum(index * tmp) / np.sum(tmp)
            if np.abs(v - xpeak0[peak]) < 0.5:
                # try to gauss fit
                try:
                    # set initial guess
                    p0 = [1, xpeak0[peak], 0.8, 0]
                    # fit a gaussian to that peak
                    #    gg = [mean, amplitude, sigma, dc]
                    with warnings.catch_warnings(record=True) as w:
                        gg, pcov = curve_fit(gauss_function, index, tmp, p0=p0)
                    spirouCore.spirouLog.warninglogger(w)
                    # get position
                    xpeaks[peak] = gg[1]
                except ValueError:
                    WLOG('warning', p['log_opt'],
                         'ydata or xdata contains NaNS')
                except RuntimeError:
                    wmsg = ('Problem with gaussfit (Not a big deal, one in '
                            'thousands of fits')
                    WLOG('warning', p['log_opt'], wmsg)
        # else barycenter adjustment
        else:
            # range from -2 to +2 pixels from position of peak
            # selects only the core of the line. Adding more aseline would
            # underestimate the offsets
            index = np.array(range(-2, 3)) + int(xpeak0[peak] + 0.5)
            # get sp at indices
            tmp = sp[ordpeak[peak], index]
            # get position
            xpeaks[peak] = np.sum(index * tmp)/np.sum(tmp)
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
        spei = spe[order_num, :]
        sperefi = speref[order_num, :]
        cc_orders[order_num] = pearsonr(spei, sperefi)[0]
    # return cc orders
    return cc_orders


def sigma_clip(loc, sigma=1.0):
    """
    Perform a sigma clip on dv

    :param loc: parameter dictionary, data storage
    :param sigma: float, the sigma of the clip (away from the median)
    :return:
    """
    # get dv
    dv = loc['dv']
    # define a mask for sigma clip
    mask = np.abs(dv - np.median(dv)) < sigma * np.std(dv)
    # perform sigma clip and add to loc
    loc['dvc'] = loc['dv'][mask]
    loc['orderpeakc'] = loc['ordpeak'][mask]
    # set the source for these new parameters
    loc.set_sources(['dvc', 'orderpeakc'], __NAME__ + '/sigma_clip()')
    # return to loc
    return loc


def drift_per_order(loc, fileno):
    """
    Calculate the individual drifts per order

    :param loc: parameter dictionary, data storage
    :param fileno: int, the file number (iterator number)

    :return loc: parameter dictionary, the updated data storage dictionary
    """

    # loop around the orders
    for order_num in range(loc['number_orders']):
        # get the dv for this order
        dv_order = loc['dvc'][loc['orderpeakc'] == order_num]
        # get the number of dvs in this order
        numdv = len(dv_order)
        # get the drift for this order
        drift = np.median(dv_order)
        driftleft = np.median(dv_order[:int(numdv/2.0)])
        driftright = np.median(dv_order[-int(numdv/2.0):])
        # get the error in the drift
        errdrift = np.std(dv_order) / np.sqrt(numdv)

        # add to storage
        loc['drift'][fileno, order_num] = drift
        loc['drift_left'][fileno, order_num] = driftleft
        loc['drift_right'][fileno, order_num] = driftright
        loc['errdrift'][fileno, order_num] = errdrift

    # return loc
    return loc


def drift_all_orders(loc, fileno, nomax):
    """
    Work out the weighted mean drift across all orders

    :param loc: parameter dictionary, data storage
    :param fileno: int, the file number (iterator number)
    :param nomax: int, the maximum order to use (i.e. use from 0 to "nomax")

    :return loc: parameter dictionary, the updated data storage dictionary
    """

    # get data from loc
    drift = loc['drift'][fileno, :nomax]
    driftleft = loc['drift_left'][fileno, :nomax]
    driftright = loc['drift_right'][fileno, :nomax]
    errdrift = loc['errdrift'][fileno, :nomax]

    # work out weighted mean drift
    sumerr = np.sum(1.0/errdrift)
    meanvr = np.sum(drift/errdrift) / sumerr
    meanvrleft = np.sum(driftleft/errdrift) / sumerr
    meanvrright = np.sum(driftright/errdrift) / sumerr
    merrdrift = 1.0 / np.sqrt(np.sum(1.0/errdrift**2))

    # add to storage
    loc['meanrv'][fileno] = meanvr
    loc['meanrv_left'][fileno] = meanvrleft
    loc['meanrv_right'][fileno] = meanvrright
    loc['merrdrift'][fileno] = merrdrift

    # return loc
    return loc


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

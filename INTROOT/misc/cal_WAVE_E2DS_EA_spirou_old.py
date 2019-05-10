#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_HC_E2DS_spirou.py [night_directory] [fitsfilename]

Wavelength calibration

Created on 2018-07-20
@author: artigau, hobson
"""

from scipy.optimize import curve_fit

import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS import spirouDB
from SpirouDRS.spirouCore.spirouMath import nanpolyfit


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_WAVE_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt
plt.ion()
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Auxiliary functions - to be moved elsewhere later
# =============================================================================
def lin_mini(vector, sample):
    sz_sample = np.shape(sample)
    sz_vector = np.shape(vector)

    if sz_vector[0] == sz_sample[0]:
        # noinspection PyUnusedLocal
        cas = 2
    if sz_vector[0] == sz_sample[1]:
        cas = 1
    else:
        cas = None

    #
    # vecteur de N elements
    # sample : matrice N*M, chacune des M colonnes est ajustee en amplitude
    # pour minimiser le chi2 par rapport au vecteur d'entree
    # output : vecteur de M de long qui donne les amplitudes de chaque
    # colonne
    #
    # returns NaN values as amplitudes if the sample vectors lead to an
    # auto-correlation matrix that
    # cannot be inverted (i.e., that are full of zeros or are not linearly
    # independent)
    #
    vector = np.asarray(vector)
    sample = np.asarray(sample)
    sz_sample = np.shape(sample)

    if cas == 1:
        #
        mm = np.zeros([sz_sample[0], sz_sample[0]])
        #
        v = np.zeros(sz_sample[0])

        for i in range(sz_sample[0]):
            for j in range(i, sz_sample[0]):
                mm[i, j] = np.nansum(sample[i, :] * sample[j, :])
                mm[j, i] = mm[i, j]
            v[i] = np.nansum(vector * sample[i, :])
        #
        if np.linalg.det(mm) == 0:
            amps = np.zeros(sz_sample[0]) + np.nan
            recon = np.zeros_like(v)
            return amps, recon

        amps = np.matmul(np.linalg.inv(mm), v)
        #
        recon = np.zeros(sz_sample[1])
        #
        for i in range(sz_sample[0]):
            recon += amps[i] * sample[i, :]
        #
        return amps, recon

    if cas == 2:
        # print('cas = 2')
        # print(sz_sample[1])
        mm = np.zeros([sz_sample[1], sz_sample[1]])
        v = np.zeros(sz_sample[1])

        for i in range(sz_sample[1]):
            for j in range(i, sz_sample[1]):
                mm[i, j] = np.nansum(sample[:, i] * sample[:, j])
                mm[j, i] = mm[i, j]
            v[i] = np.nansum(vector * sample[:, i])

        if np.linalg.det(mm) == 0:
            amps = np.zeros(sz_sample[1]) + np.nan
            recon = np.zeros_like(v)
            return amps, recon

        amps = np.matmul(np.linalg.inv(mm), v)

        recon = np.zeros(sz_sample[0])

        for i in range(sz_sample[1]):
            recon += amps[i] * sample[:, i]

        return amps, recon


def gaus_funct(x, a):
    #
    # translated from IDL'S gaussfit function
    # used to generate a Gaussian but also returns its derivaties for
    # function fitting
    #
    # parts of the comments from the IDL version of the code --
    #
    # NAME:
    #   GAUSS_FUNCT
    #
    # PURPOSE:
    #   EVALUATE THE SUM OF A GAUSSIAN AND A 2ND ORDER POLYNOMIAL
    #   AND OPTIONALLY RETURN THE VALUE OF IT'S PARTIAL DERIVATIVES.
    #   NORMALLY, THIS FUNCTION IS USED BY CURVEFIT TO FIT THE
    #   SUM OF A LINE AND A VARYING BACKGROUND TO ACTUAL DATA.
    #
    # CATEGORY:
    #   E2 - CURVE AND SURFACE FITTING.
    # CALLING SEQUENCE:
    #   FUNCT,X,A,F,PDER
    # INPUTS:
    #   X = VALUES OF INDEPENDENT VARIABLE.
    #   A = PARAMETERS OF EQUATION DESCRIBED BELOW.
    # OUTPUTS:
    #   F = VALUE OF FUNCTION AT EACH X(I).
    #   PDER = matrix with the partial derivatives for function fitting
    #
    # PROCEDURE:
    #   F = A(0)*EXP(-Z^2/2) + A(3) + A(4)*X + A(5)*X^2
    #   Z = (X-A(1))/A(2)
    #   Elements beyond A(2) are optional.
    #

    n = len(a)
    nx = len(x)
    #
    zz = (x - a[1]) / a[2]  #
    ezz = np.exp(-zz ** 2 / 2.)  # GAUSSIAN PART
    #
    ff = None
    if n == 3:
        ff = a[0] * ezz
    if n == 4:
        ff = a[0] * ezz + a[3]
    if n == 5:
        ff = a[0] * ezz + a[3] + a[4] * x
    if n == 6:
        ff = a[0] * ezz + a[3] + a[4] * x + a[5] * x ^ 2
    #
    pder = np.zeros([nx, n])
    pder[:, 0] = ezz  # COMPUTE PARTIALS
    pder[:, 1] = a[0] * ezz * zz / a[2]
    pder[:, 2] = pder[:, 1] * zz
    if n > 3:
        pder[:, 3] = 1.0
    if n > 4:
        pder[:, 4] = x
    if n > 5:
        pder[:, 5] = x ** 2
    return ff, pder


def gaussfit(xpix, ypix, nn):
    # fits a Gaussian function to xpix and ypix without prior
    # knowledge of parameters. The gaussians are expected to have
    # their peaks within the min/max range of xpix
    # the are expected to be reasonably close to Nyquist-sampled
    # nn must be an INT in the range between 3 and 6
    #
    # nn=3 -> the Gaussian has a floor of 0, the output will have 3 elements
    # nn=4 -> the Gaussian has a floor that is non-zero
    # nn=5 -> the Gaussian has a slope
    # nn=6 -> the Guassian has a 2nd order polynomial floor
    #
    # outputs ->
    # [ amplitude , center of peak, amplitude of peak, [dc level],
    # [slope], [2nd order tern] ]
    #

    # we guess that the Gaussian is close to Nyquist and has a
    # 2 PIX FWHM and therefore 2/2.54 e-width
    ew_guess = 2 * np.nanmedian(np.gradient(xpix)) / 2.354

    a0 = None
    if nn == 3:
        # only amp, cen and ew
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess]
    if nn == 4:
        # only amp, cen, ew, dc offset
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess,
              np.min(ypix)]
    if nn == 5:
        # only amp, cen, ew, dc offset, slope
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess,
              np.min(ypix), 0]
    if nn == 6:
        # only amp, cen, ew, dc offset, slope, curvature
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess,
              np.min(ypix), 0, 0]

    residu_prev = np.array(ypix)

    gfit, pder = gaus_funct(xpix, a0)

    rms = 99
    nite = 0

    # loops for 20 iterations MAX or an RMS with an RMS change in residual
    # smaller than 1e-6 of peak
    while (rms > 1e-6) & (nite <= 20):
        gfit, pder = gaus_funct(xpix, a0)
        residu = ypix - gfit

        amps, fit = lin_mini(residu, pder)
        a0 += amps
        rms = np.std(residu - residu_prev) / (np.max(ypix) - np.min(ypix))

        residu_prev = residu
        nite += 1

    return a0, gfit


# =============================================================================
# Defining a Gaussian with a DC level and slope underneath
# =============================================================================
def gauss_function(x, a, x0, sig, zp, slope):
    sig = np.abs(sig)
    return (a * np.exp(-(x - x0) ** 2 / (2 * sig ** 2)) +
            zp + (x - np.mean(x)) * slope)


# =============================================================================
# End auxiliary functions
# =============================================================================
def main(night_name=None, fpfile=None, hcfiles=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------

    # test files TC2
    # night_name = 'AT5/AT5-12/2018-05-29_17-41-44/'
    # fpfile = '2279844a_fp_fp_pp_e2dsff_AB.fits'
    # hcfiles = ['2279845c_hc_pp_e2dsff_AB.fits']

    # test files TC3
    # night_name = 'TC3/AT5/AT5-12/2018-07-24_16-17-57/'
    # fpfile = '2294108a_pp_e2dsff_AB.fits'
    # hcfiles = ['2294115c_pp_e2dsff_AB.fits']

    # night_name = 'TC3/AT5/AT5-12/2018-07-25_16-49-50/'
    # fpfile = '2294223a_pp_e2dsff_AB.fits'
    # hcfiles = ['2294230c_pp_e2dsff_AB.fits']

    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    if hcfiles is None or fpfile is None:
        names, types = ['fpfile', 'hcfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime(p, [0, 1], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(hcfiles=hcfiles, fpfile=fpfile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsdir='reduced',
                                    mainfitsfile='hcfiles')

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, fpfitsfilename = spirouStartup.SingleFileSetup(p, filename=p['FPFILE'])
    fiber1 = str(p['FIBER'])
    p, hcfilenames = spirouStartup.MultiFileSetup(p, files=p['HCFILES'])
    fiber2 = str(p['FIBER'])
    # set the hcfilename to the first hcfilenames
    hcfitsfilename = hcfilenames[0]

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Have to check that the fibers match
    # ----------------------------------------------------------------------
    if fiber1 == fiber2:
        p['FIBER'] = fiber1
        fsource = __NAME__ + '/main() & spirouStartup.GetFiberType()'
        p.set_source('FIBER', fsource)
    else:
        emsg = 'Fiber not matching for {0} and {1}, should be the same'
        eargs = [hcfitsfilename, fpfitsfilename]
        WLOG(p, 'error', emsg.format(*eargs))
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # =============================================================================
    # input parameters
    # =============================================================================

    # read and combine all HC files except the first (fpfitsfilename)
    rargs = [p, 'add', hcfitsfilename, hcfilenames[1:]]
    p, hcdata, hchdr = spirouImage.ReadImageAndCombine(*rargs)
    # read first file (fpfitsfilename)
    fpdata, fphdr, _, _ = spirouImage.ReadImage(p, fpfitsfilename)

    # add data and hdr to loc
    loc = ParamDict()
    loc['HCDATA'], loc['HCHDR'] = hcdata, hchdr
    loc['FPDATA'], loc['FPHDR'] = fpdata, fphdr
    # set the source
    sources = ['HCDATA', 'HCHDR']
    loc.set_sources(sources, 'spirouImage.ReadImageAndCombine()')
    sources = ['FPDATA', 'FPHDR']
    loc.set_sources(sources, 'spirouImage.ReadImage()')

    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hchdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')

    # ----------------------------------------------------------------------
    # Get basic image properties for reference file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hchdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hchdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hchdr, name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, hchdr, name='acqtime', kind='julian')
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p, hchdr)
    # get number of orders
    # we always get fibre A number because AB is doubled in constants file
    nbo = p['QC_LOC_NBO_FPALL']['A']
    # get number of pixels in x from hcdata size
    nbpix = np.shape(hcdata)[1]

    # wavelength file; we will use the polynomial terms in its header,
    # NOT the pixel values that would need to be interpolated

    # set source of wave file
    wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    # get wave image
    wout = spirouImage.GetWaveSolution(p, hdr=hchdr, return_wavemap=True,
                                       return_filename=True)
    loc['WAVEPARAMS'], loc['WAVE_INIT'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    loc.set_sources(['WAVE_INIT', 'WAVEFILE', 'WAVEPARAMS', 'WSOURCE'], wsource)
    poly_wave_sol = loc['WAVEPARAMS']

    # control plotting
    doplot_per_order = False
    doplot_sanity = True

    # =============================================================================

    # generate initial wavelength map
    # set the possibility for a pixel shift
    pixel_shift_inter = p['PIXEL_SHIFT_INTER']
    pixel_shift_slope = p['PIXEL_SHIFT_SLOPE']
    # print a warning if pixel_shift is not 0
    if pixel_shift_slope != 0 or pixel_shift_inter != 0:
        wmsg = 'Pixel shift is not 0, check that this is desired'
        WLOG(p, 'warning', wmsg.format())

    wave_map = np.zeros([nbo, nbpix])
    xpix = np.arange(nbpix) + pixel_shift_inter + pixel_shift_slope * np.arange(
        nbpix)
    for iord in range(nbo):
        wave_map[iord, :] = np.polyval((poly_wave_sol[iord, :])[::-1], xpix)

    # number of sigma above local RMS for a line to be flagged as such
    sigma_peak = 3.0

    # width of the box for fitting HC lines. Lines will be fitted from -W to +W,
    # so a 2*W+1 window
    window = 6

    # defining empty variables, so will be used later
    # others are just there to confuse the reader
    ew = []
    xgau = []
    peak1 = []
    dx = []
    order_ = []
    zp = []
    slope = []
    gauss_rms_dev = []
    wave_hdr_sol = []

    # looping through e2ds orders to find HC peaks.
    #  -- Method
    #
    # We find the highest pixel, fit a gaussian to it (-w to +w window)
    # and keep its e-width
    # as well as other parameters that may be used as quality checks
    # the "keep" vector is used to keep track of pixels where we haven't
    # had a window yet
    # and may find a peak
    # once we have fitted a gaussian, we subtract it and search for
    # the next highest peak
    # we loop until we reach peaks at ~10 sigma

    # we scan all orders and search for local peaks
    # when we find a tentative peak, we fit a gaussian
    # if the gaussian is well-behaved, we keep it in a list that
    # will be compared to the expected lines from the catalog

    wmsg = 'Searching for gaussian peaks on the HC spectrum'
    WLOG(p, 'info', wmsg.format())

    for iord in range(nbo):
        # keep track of pixels where we look for peaks

        if doplot_per_order:
            plt.plot(hcdata[iord, :])

        # print order message
        wmsg = 'Searching for peaks in order {0}'
        WLOG(p, '', wmsg.format(iord))

        # scanning through each order, 1/3rd of w at a time
        for indmax in range(window * 2, nbpix - window * 2 - 1, window // 3):
            xpix = np.asarray(range(indmax - window, indmax + window))
            segment = np.array(hcdata[iord, indmax - window:indmax + window])
            rms = np.nanmedian(np.abs(segment[1:] - segment[:-1]))
            peak = (np.max(segment) - np.nanmedian(segment))

            # peak needs to be well-behaved
            keep = True
            keep &= (rms != 0)
            keep &= (peak != 0)
            keep &= (peak / rms > sigma_peak)

            # position of peak within segment. It needs to be close enough
            # to the center of the segment
            # if it is at the edge, we'll catch it in the following iteration
            #
            # we keep (or not) the peak
            imax = np.argmax(segment) - window
            # this is asymmetrical and allows catching peaks twice
            # keep &= (np.abs(imax) < window // 3)
            # fix (?)
            keep &= (-window // 3 < imax < window // 3 - 1)
            if keep:
                # fit a gaussian with a slope
                popt_left, g2 = gaussfit(xpix, segment, 5)

                # the residual of the
                gauss_rms_dev0 = np.std(segment - g2) / popt_left[0]

                # all values that will be added (if keep_peak=True) to the
                # vector of all line parameters
                zp0 = popt_left[3]
                slope0 = popt_left[4]
                ew0 = popt_left[2]
                xgau0 = popt_left[1]
                peak0 = popt_left[0]

                keep_peak = True

                # the RMS of line-fitted line must be before 0 and 0.2 of the
                # peak value
                gauss_rms_dev_min = 0
                gauss_rms_dev_max = 0.1

                # the e-width of the line must be between 0.7 and 1.1 pixel
                ew_min = 0.7
                ew_max = 1.1
                wave0 = np.polyval((poly_wave_sol[iord, :])[::-1],
                                   xgau0 + pixel_shift_inter +
                                   pixel_shift_slope * xgau0)

                keep_peak &= gauss_rms_dev0 > gauss_rms_dev_min
                keep_peak &= gauss_rms_dev0 < gauss_rms_dev_max
                keep_peak &= ew0 > ew_min
                keep_peak &= ew0 < ew_max

                # if all is fine, we keep the value of the fit
                if keep_peak:
                    zp = np.append(zp, zp0)
                    slope = np.append(slope, slope0)
                    ew = np.append(ew, ew0)
                    xgau = np.append(xgau, xgau0)
                    peak1 = np.append(peak1, peak0)
                    order_ = np.append(order_, iord)
                    gauss_rms_dev = np.append(gauss_rms_dev, gauss_rms_dev0)
                    wave_hdr_sol = np.append(wave_hdr_sol, wave0)

                    if doplot_per_order:
                        plt.plot(g2, '--')
        if doplot_per_order:
            plt.show()

    # print total found lines
    wargs = [len(wave_hdr_sol)]
    wmsg = '{0} gaussian peaks found in HC spectrum'
    WLOG(p, 'info', wmsg.format(*wargs))

    # reading the UNe catalog
    wave_u_ne, amp_u_ne = spirouImage.ReadLineList(p)
    loc['LL_LINE'], loc['AMPL_LINE'] = wave_u_ne, amp_u_ne
    source = __NAME__ + '/main() + spirouImage.ReadLineList()'
    loc.set_sources(['ll_line', 'ampl_line'], source)

    wmsg = 'Matching found lines to the catalogue'
    WLOG(p, 'info', wmsg.format())

    # keeping track of the velocity offset between predicted and observed
    # line centers
    dv = np.zeros(len(wave_hdr_sol)) + np.nan

    # wavelength given in the catalog for the matched line
    wave_catalog = np.zeros(len(wave_hdr_sol)) + np.nan
    # save the amplitudes
    amp_catalog = np.zeros(len(wave_hdr_sol)) + np.nan
    i = -1
    for wave0 in wave_hdr_sol:
        i += 1
        # find closest catalog line to the line considered
        idmin = np.argmin(np.abs(wave_u_ne - wave0))
        ddv = (wave_u_ne[idmin] / wave0 - 1) * 2.997e8
        # if within 2km/s, we consider a match
        if np.abs(ddv) < 30000:
            dv[i] = ddv
            wave_catalog[i] = wave_u_ne[idmin]
            amp_catalog[i] = amp_u_ne[idmin]

    # define 100-nm bins
    # TODO why not from 900?
    xbins = np.array(range(1000, 2200, 100))

    # plot found lines - wavelength vs velocity offset from catalogue
    plt.figure()
    plt.clf()
    plt.plot(wave_catalog, dv, 'g.', label='all lines')
    plt.xlabel('wavelength')
    plt.ylabel('velocity offset from catalogue')
    dv_pred = None
    for ite in range(2):
        meddv = np.zeros_like(xbins)

        i = 0
        for xbin in xbins:
            # define mask for all lines in 100-nm bin
            g = 100 * (wave_catalog // 100) == xbin
            # add only finite dvs to mask
            g &= np.isfinite(dv)

            # calculate median dv for lines in bin with finite dv
            meddv[i] = np.nanmedian(dv[g])
            # print bin and total number of lines in 100-nm bin
            if ite == 0:
                wargs = [xbin, xbin + 100, np.nansum(g)]
                wmsg = 'In wavelength bin {0}-{1}, {2} lines matched to ' \
                       'catalogue'
                WLOG(p, '', wmsg.format(*wargs))
            elif ite == 1:
                wargs = [xbin, xbin + 100, np.nansum(g)]
                wmsg = 'In wavelength bin {0}-{1}, {2} lines with dv<5 kept'
                WLOG(p, '', wmsg.format(*wargs))

            i += 1
        # print total number of lines for ite=0
        if ite == 0:
            wargs = [np.nansum(np.isfinite(dv))]
            wmsg = 'Total {0} lines matched to catalogue'
            WLOG(p, '', wmsg.format(*wargs))

        # 3rd degree polynomial fit to the center of bins vs median dv per bin
        fit = nanpolyfit(xbins + 50, meddv, 3)
        # evaluate fit on all lines to get a predicted velocity offset
        dv_pred = np.polyval(fit, wave_catalog)

        # get median-normalised difference from predicted velocity offset
        err = np.abs(dv - dv_pred) / np.nanmedian(np.abs(dv - dv_pred))
        # if difference >5, set dv to nan
        dv[err > 5] = np.nan
        # print total number of lines for ite=1
        if ite == 1:
            wargs = [np.nansum(np.isfinite(dv))]
            wmsg = 'Total {0} lines with dv<5 kept'
            WLOG(p, '', wmsg.format(*wargs))

    if doplot_sanity:
        # plot the predicted velocity offset from the catalogue
        plt.plot(wave_catalog, dv_pred, 'k.', label='predicted offset')
        # overplot the kept lines (difference from predicted offset <5)
        plt.plot(wave_catalog, dv, 'c.', label='kept lines')
        plt.legend()
        plt.show()

    # for each order, we fit a 4th order polynomial between pix and wavelength
    fit_degree = p['IC_LL_DEGR_FIT']
    fit_per_order = np.zeros([nbo, fit_degree + 1])

    wmsg = 'Sigma-clipping of found lines'
    WLOG(p, 'info', wmsg.format())

    plt.figure()  # open new figure
    # loop through orders
    for iord in range(nbo):
        # keep relevant lines
        # -> right order
        # -> finite dv
        gg = (order_ == iord) & (np.isfinite(dv))
        nlines = np.nansum(gg)

        # if we have less than 10 lines, then its bad
        if nlines >= 10:

            nsigmax = 999

            # we perform a sigma clipping of lines with a 2nd order polynomial
            # of the dV vs pixel position, this is only used for sigma-clipping
            while nsigmax > 3:
                fit = nanpolyfit(xgau[gg], dv[gg], 2)

                # plt.plot(xgau[gg],dv[gg]-np.polyval(fit,xgau[gg]),'r.')
                # plt.show()

                dd = dv[gg] - np.polyval(fit, xgau[gg])
                # print info
                wargs = [iord, nsigmax, np.std(dd)]
                wmsg = 'Sigma-clip for order {0}: sigma={1:.2f}, vel. ' \
                       'offset vs pix stddev={2:.2f}'
                WLOG(p, '', wmsg.format(*wargs))

                dd /= np.std(dd)

                argmax = np.argmax(np.abs(dd))
                nsigmax = np.abs(dd[argmax])

                # print info
                # np.set_printoptions(precision=3)
                wargs = [fit, nsigmax]
                wmsg = 'vel. offset vs pix coeffs: {0}, sigma={1:.2f}'
                WLOG(p, '', wmsg.format(*wargs))

                # if the largest deviation from the 2nd order fit is >3
                # sigma (either + or -) then we remove the point
                if nsigmax > 3:
                    tmp = gg[gg]
                    tmp[argmax] = False
                    gg[gg] = tmp

            if doplot_sanity:
                plt.plot(wave_catalog[gg], xgau[gg], '.')
                plt.xlabel('wavelength')
                plt.ylabel('pixel position')

            # the pix VS wavelength is fitted with a 4th order polynomial
            fit_per_order[iord, :] = nanpolyfit(xgau[gg], wave_catalog[gg],
                                                fit_degree)

    if doplot_sanity:
        plt.show()

    wave_map2 = np.zeros([nbo, nbpix])
    xpix = np.array(range(nbpix))
    for i in range(nbo):
        wave_map2[i, :] = np.polyval(fit_per_order[i, :], xpix)

    # store the wavelength map in loc
    loc['LL_OUT_1'] = wave_map2
    loc.set_source('LL_OUT_1', __NAME__ + '/main()')

    # ===============================================================================================
    # bit of code that smooths the coefficient VS nth order relations
    # DOES NOT WORK (yet...)
    # ===============================================================================================
    # x index in the smoothing of the nth-order VS coefficient

    # set/unset smoothing
    poly_smooth = False
    new_wavelength_solution_polyfit = None
    if poly_smooth:

        plt.figure()
        plt.clf()
        wmsg = 'Forcing continuity of the polynomial fit coefficients'
        WLOG(p, 'info', wmsg.format())

        # We will force continuity of the coefficients of the polynomial
        # fit. The 1st term (wavelength at pix=0) is much better determined
        # than the 4th order-term. This is why the polynomial fit
        # used to force continuity is low-order for the higher-order
        # terms in the wavelength solutions.
        order_fit_continuity = [2, 2, 2, 4, 8, 12]

        nth_order = np.array(range(nbo))

        # keeping track of the best estimates for the polynomial
        # coefficients
        new_wavelength_solution_polyfit = np.zeros([fit_degree + 1, nbo])

        for nth_poly_order in range(fit_degree + 1):

            tmp = fit_per_order[:, nth_poly_order]

            nsigmax = 999

            keep = np.ones([nbo], dtype=bool)

            ite = 0
            # sigma clipping on linear fit to remove few large outliers
            # avoids biassing high-order polynomials by these outliers
            while nsigmax > 3:
                fit = nanpolyfit(nth_order[keep], tmp[keep], 1)
                err = tmp - np.polyval(fit, nth_order)

                idmax = np.argmax(np.abs(err * keep / np.std(err[keep])))
                nsigmax = np.max(np.abs(err * keep / np.std(err[keep])))

                keep[idmax] = False

                # print information to screen
                wargs = [nth_poly_order, nsigmax, np.mean(keep), ite]
                wmsg = 'Coeff order {0}: ' \
                       'Linear sigma-clip: sigma={1:.2f}, qc?={2:.2f}, ' \
                       'iteration={3}'
                WLOG(p, '', wmsg.format(*wargs))

                ite += 1

            nsigmax = 999

            # sigma-clipping of the order VS polynomial coefficients.
            # using higher-order polynomial
            fit, err = None, None
            while nsigmax > 3:
                fit = nanpolyfit(nth_order[keep], tmp[keep],
                                 order_fit_continuity[nth_poly_order])
                err = tmp - np.polyval(fit, nth_order)

                idmax = np.argmax(np.abs(err * keep / np.std(err[keep])))
                nsigmax = np.max(np.abs(err * keep / np.std(err[keep])))

                keep[idmax] = False

                # print information to screen
                wargs = [nth_poly_order, nsigmax, np.mean(keep), ite]
                wmsg = 'Coeff order {0}: ' \
                       'Polynomial sigma-clip: sigma={1:.2f}, qc?={2:.2f}, ' \
                       'iteration={3}'
                WLOG(p, '', wmsg.format(*wargs))

                ite += 1

            if doplot_sanity:
                plt.subplot(fit_degree + 1, 2, 1 + nth_poly_order * 2)

                plt.title('p order ' + str(fit_degree + 1 - nth_poly_order))
                plt.plot(nth_order, tmp, 'r.')
                plt.plot(nth_order[keep], tmp[keep], 'g.')
                plt.plot(nth_order, np.polyval(fit, nth_order), 'k-')
                plt.ylabel('pix')

                plt.xlabel('$\lambda$ (nm)')

                plt.subplot(fit_degree + 1, 2, 2 + nth_poly_order * 2)

                plt.title('p order ' + str(fit_degree + 1 - nth_poly_order))
                plt.ylabel('residual pix')
                plt.xlabel('$\lambda$ (nm)')
                plt.plot(nth_order[keep], err[keep], 'c.')

            nwsp = np.polyval(fit, nth_order)
            new_wavelength_solution_polyfit[nth_poly_order, :] = nwsp
        wave_map3 = np.zeros([nbo, nbpix])
        xpix = np.array(range(nbpix))
        for iord in range(nbo):
            wave_map3[iord, :] = np.polyval(
                new_wavelength_solution_polyfit[:, iord], xpix)

        nsigmax = 999
        if doplot_sanity:
            plt.plot()
            plt.clf()

        # store the smoothed wavelength map in loc
        loc['LL_OUT_2'] = wave_map3
        loc.set_source('LL_OUT_2', __NAME__ + '/main()')

    # TODO incorporate cross-order wavelength checking

    # ===============================================================================================
    # Determine the LSF and calculate the resolution
    # ===============================================================================================

    hc_ini = np.array(hcdata)
    # determining the LSF
    resolution_map = np.zeros([5, 4])

    wmsg = 'Determining the LSF'
    WLOG(p, 'info', wmsg.format())

    i_plot = 0
    # determining the LSF
    bin_ord = 10

    plt.figure()

    for iord in range(0, nbo, bin_ord):
        for xpos in range(0, 4):
            plt.subplot(5, 4, i_plot + 1)
            gg = (gauss_rms_dev < 0.05)
            gg &= (order_ // 10 == iord // 10)
            gg &= (xgau // 1024) == xpos
            gg &= np.isfinite(wave_catalog)

            xcens = xgau[gg]
            orders = order_[gg]
            wave_line = wave_catalog[gg]

            all_lines = np.zeros([np.nansum(gg), 2 * window + 1])
            all_dvs = np.zeros([np.nansum(gg), 2 * window + 1])

            base = np.zeros(2 * window + 1, dtype=bool)
            base[0:3] = True
            base[2 * window - 2:2 * window + 1] = True
            # noinspection PyTypeChecker
            for i in range(np.nansum(gg)):
                part1 = int(orders[i])
                part2 = int(xcens[i] + .5) - window
                part3 = int(xcens[i] + .5) + window + 1
                all_lines[i, :] = hc_ini[part1, part2:part3]
                all_lines[i, :] -= np.nanmedian(all_lines[i, base])
                all_lines[i, :] /= np.nansum(all_lines[i, :])

                v = -2.997e5 * (wave_map2[part1, part2:part3] /
                                wave_line[i] - 1)
                all_dvs[i, :] = v

            all_dvs = all_dvs.ravel()
            all_lines = all_lines.ravel()

            keep = np.ones(len(all_dvs), dtype=bool)

            maxdev = 999
            maxdev_threshold = 8

            popt_left = None
            while maxdev > maxdev_threshold:
                # noinspection PyTypeChecker
                popt_left, pcov = curve_fit(gauss_function, all_dvs[keep],
                                            all_lines[keep],
                                            p0=[.3, 0, 1, 0, 0])
                res = all_lines - gauss_function(all_dvs, popt_left[0],
                                                 popt_left[1],
                                                 popt_left[2], popt_left[3],
                                                 popt_left[4])

                rms = res / np.nanmedian(np.abs(res))
                maxdev = np.max(np.abs(rms[keep]))
                keep[np.abs(rms) > maxdev_threshold] = False
            resolution = popt_left[2] * 2.354

            plt.plot(all_dvs[keep], all_lines[keep], 'g.')

            xx = (np.array(range(301)) - 150) / 10.
            gplot = gauss_function(xx, popt_left[0], popt_left[1], popt_left[2],
                                   popt_left[3], popt_left[4])

            plt.plot(xx, gplot, 'k--')
            wargs = [np.nansum(gg), iord, iord + 9, xpos, resolution,
                     2.997e5 / resolution]
            wmsg = 'nlines={0}, orders={1}-{2}, x region={3}, ' \
                   'resolution={4:.2f} km/s, R={5:.2f}'
            WLOG(p, '', wmsg.format(*wargs))

            #        print('nlines : ', np.nansum(gg), 'iord=', iord,
            #              ' xpos=', xpos,
            #              ' resolution = ', resolution, ' km/s', 'R = ',
            #              2.997e5 / resolution)
            plt.xlim([-8, 8])
            plt.ylim([-0.05, .7])
            plt.title(
                'orders ' + str(iord) + '-' + str(iord + 9) + ' region=' + str(
                    xpos))
            plt.xlabel('dv (km/s)')

            i_plot += 1

            resolution_map[iord // bin_ord, xpos] = 2.997e5 / resolution

    plt.tight_layout()
    plt.show()

    wargs = [np.nanmean(resolution_map), np.nanmedian(resolution_map),
             np.nanstd(resolution_map)]
    wmsg = 'Resolution stats:  mean={0:.2f}, median={1:.2f}, stddev={2:.2f}'
    WLOG(p, 'info', wmsg.format(*wargs))

    # TODO: --> Below is not etienne's code!

    # ----------------------------------------------------------------------
    # Set up all_lines storage list for both wavelength solutions
    # ----------------------------------------------------------------------

    # initialise up all_lines storage
    all_lines_1 = []
    all_lines_2 = []

    # initialise storage for residuals
    res_1 = []
    res_2 = []
    ord_save = []

    n_ord_start = p['IC_HC_N_ORD_START_2']
    n_ord_final = p['IC_HC_N_ORD_FINAL_2']

    # first wavelength solution (no smoothing)
    # loop through orders
    for iord in range(n_ord_start, n_ord_final):
        # keep relevant lines
        # -> right order
        # -> finite dv
        gg = (order_ == iord) & (np.isfinite(dv))
        nlines = np.nansum(gg)
        # put lines into ALL_LINES structure
        # reminder:
        # gparams[0] = output wavelengths
        # gparams[1] = output sigma(gauss fit width)
        # gparams[2] = output amplitude(gauss fit)
        # gparams[3] = difference in input / output wavelength
        # gparams[4] = input amplitudes
        # gparams[5] = output pixel positions
        # gparams[6] = output pixel sigma width (gauss fit width in pixels)
        # gparams[7] = output weights for the pixel position

        # dummy array for weights
        test = np.ones(np.shape(xgau[gg]), 'd')
        # get the final wavelength value for each peak in order
        output_wave_1 = np.polyval(fit_per_order[iord, :], xgau[gg])
        # get the initial solution wavelength value for each peak in the order
        # allow pixel shifting
        xgau_shift = xgau[gg] + pixel_shift_inter + pixel_shift_slope * xgau[gg]
        input_wave = np.polyval((poly_wave_sol[iord, :])[::-1], xgau_shift)
        # convert the pixel equivalent width to wavelength units
        xgau_ew_ini = xgau[gg] - ew[gg] / 2
        xgau_ew_fin = xgau[gg] + ew[gg] / 2
        ew_ll_ini = np.polyval(fit_per_order[iord, :], xgau_ew_ini)
        ew_ll_fin = np.polyval(fit_per_order[iord, :], xgau_ew_fin)
        ew_ll = ew_ll_fin - ew_ll_ini
        # put all lines in the order into array
        gau_params = np.column_stack(
            (output_wave_1, ew_ll, peak1[gg], input_wave - output_wave_1,
             amp_catalog[gg], xgau[gg], ew[gg], test))
        # append the array for the order into a list
        all_lines_1.append(gau_params)
        # save dv in km/s and auxiliary order number
        res_1 = np.concatenate(
            (res_1, 2.997e5 * (input_wave - output_wave_1) / output_wave_1))
        ord_save = np.concatenate((ord_save, test * iord))

    # add to loc
    loc['ALL_LINES_1'] = all_lines_1
    loc['LL_PARAM_1'] = np.fliplr(fit_per_order)
    loc.set_sources(['ALL_LINES_1', 'LL_PARAM_1'], __NAME__ + '/main()')

    # second wavelength solution (smoothed)
    if poly_smooth:
        # loop through orders
        for iord in range(nbo):
            # keep relevant lines
            # -> right order
            # -> finite dv
            gg = (order_ == iord) & (np.isfinite(dv))
            nlines = np.nansum(gg)
            # put lines into ALL_LINES structure
            # reminder:
            # gparams[0] = output wavelengths
            # gparams[1] = output sigma(gauss fit width)
            # gparams[2] = output amplitude(gauss fit)
            # gparams[3] = difference in input / output wavelength
            # gparams[4] = input amplitudes
            # gparams[5] = output pixel positions
            # gparams[6] = output pixel sigma width (gauss fit width in pixels)
            # gparams[7] = output weights for the pixel position

            # dummy array for weights
            test = np.ones(np.shape(xgau[gg]), 'd')
            # get the final wavelength value for each peak in order
            output_wave_2 = np.polyval(new_wavelength_solution_polyfit[:, iord],
                                       xgau[gg])
            # get the initial solution wavelength value for each peak in
            # the order allow pixel shifting
            part1 = xgau[gg] + pixel_shift_inter
            part2 = pixel_shift_slope * xgau[gg]
            xgau_shift = part1 + part2
            input_wave = np.polyval((poly_wave_sol[iord, :])[::-1], xgau_shift)
            # convert the pixel equivalent width to wavelength units
            xgau_ew_ini = xgau[gg] - ew[gg] / 2
            xgau_ew_fin = xgau[gg] + ew[gg] / 2
            ew_ll_ini = np.polyval(new_wavelength_solution_polyfit[:, iord],
                                   xgau_ew_ini)
            ew_ll_fin = np.polyval(new_wavelength_solution_polyfit[:, iord],
                                   xgau_ew_fin)
            ew_ll = ew_ll_fin - ew_ll_ini
            # put all lines in the order into array
            gau_params = np.column_stack(
                (output_wave_2, ew_ll, peak1[gg], input_wave - output_wave_2,
                 amp_catalog[gg], xgau[gg], ew[gg], test))
            # append the array for the order into a list
            all_lines_2.append(gau_params)
            res_2 = np.concatenate(
                (res_2, 2.997e5 * (input_wave - output_wave_2) / output_wave_2))

    # For compatibility w/already defined functions, I need to save
    # here all_lines_2
    if poly_smooth:
        loc['ALL_LINES_2'] = all_lines_2
        loc['LL_PARAM_2'] = np.fliplr(
            np.transpose(new_wavelength_solution_polyfit))
        loc.set_sources(['ALL_LINES_2', 'LL_PARAM_2'], __NAME__ + '/main()')
    else:
        all_lines_2 = list(all_lines_1)
        loc['ALL_LINES_2'] = all_lines_2
        loc['LL_PARAM_2'] = np.fliplr(fit_per_order)
        loc['LL_OUT_2'] = loc['LL_OUT_1']
        loc.set_sources(['ALL_LINES_2', 'LL_PARAM_2'], __NAME__ + '/main()')

    # ------------------------------------------------------------------
    # Littrow test
    # ------------------------------------------------------------------

    # set up start and end orders depending on if smoothing was used
    if poly_smooth:
        # set up echelle orders
        n_ord_start = 0
        n_ord_final = 49

    # calculate echelle orders
    o_orders = np.arange(n_ord_start, n_ord_final)
    echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
    loc['ECHELLE_ORDERS'] = echelle_order
    loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

    # reset Littrow fit degree
    p['IC_LITTROW_FIT_DEG_2'] = 6

    # Do Littrow check
    ckwargs = dict(ll=loc['LL_OUT_2'][n_ord_start:n_ord_final, :], iteration=2,
                   log=True)
    loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

    # Plot wave solution littrow check
    if p['DRS_PLOT'] > 0:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_check_plot(p, loc, iteration=2)

    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------
    ekwargs = dict(ll=loc['LL_OUT_2'], iteration=2)
    loc = spirouTHORCA.ExtrapolateLittrowSolution(p, loc, **ekwargs)

    # ------------------------------------------------------------------
    # Join 0-46 and 47-48 solutions
    # ------------------------------------------------------------------

    # the littrow extrapolation (for orders > n_ord_final_2)
    litt_extrap_sol_red = loc['LITTROW_EXTRAP_SOL_2'][n_ord_final:]
    litt_extrap_sol_param_red = loc['LITTROW_EXTRAP_PARAM_2'][n_ord_final:]

    # the wavelength solution for n_ord_start - n_ord_final
    # taking from loc allows avoiding an if smooth check
    ll_out = loc['LL_OUT_2'][n_ord_start:n_ord_final]
    param_out = loc['LL_PARAM_2'][n_ord_start:n_ord_final]

    print(np.shape(litt_extrap_sol_param_red))
    print(np.shape(param_out))

    # create stack
    ll_stack, param_stack = [], []
    # wavelength solution for n_ord_start - n_ord_final
    if len(ll_out) > 0:
        ll_stack.append(ll_out)
        param_stack.append(param_out)
    # add extrapolation from littrow to orders > n_ord_final
    if len(litt_extrap_sol_red) > 0:
        ll_stack.append(litt_extrap_sol_red)
        param_stack.append(litt_extrap_sol_param_red)

    # convert stacks to arrays and add to storage
    loc['LL_OUT_2'] = np.vstack(ll_stack)
    loc['LL_PARAM_2'] = np.vstack(param_stack)
    loc.set_sources(['LL_OUT_2', 'LL_PARAM_2'], __NAME__ + '/main()')

    # rename for compatibility
    loc['LITTROW_EXTRAP_SOL_1'] = np.vstack(ll_stack)
    loc['LITTROW_EXTRAP_PARAM_1'] = np.vstack(param_stack)

    # temp copy for storage
    loc['LL_FINAL'] = np.vstack(ll_stack)
    loc['LL_PARAM_FINAL'] = np.vstack(param_stack)
    all_lines_final = np.copy(all_lines_2)
    loc['ALL_LINES_FINAL'] = all_lines_final
    loc.set_sources(['LL_FINAL', 'LL_PARAM_FINAL'], __NAME__ + '/main()')

    # ------------------------------------------------------------------
    # Incorporate FP into solution
    # ------------------------------------------------------------------

    use_fp = True

    if use_fp:
        # ------------------------------------------------------------------
        # Find FP lines
        # ------------------------------------------------------------------
        # print message to screen
        wmsg = 'Identification of lines in reference file: {0}'
        WLOG(p, '', wmsg.format(fpfile))

        # ------------------------------------------------------------------
        # Get the FP solution
        # ------------------------------------------------------------------

        loc = spirouTHORCA.FPWaveSolutionNew(p, loc)

        # ------------------------------------------------------------------
        # FP solution plots
        # ------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            # Plot the FP extracted spectrum against wavelength solution
            sPlt.wave_plot_final_fp_order(p, loc, iteration=2)
            # Plot the measured FP cavity width offset against line number
            sPlt.wave_local_width_offset_plot(p, loc)
            # Plot the FP line wavelength residuals
            sPlt.wave_fp_wavelength_residuals(p, loc)

    # ------------------------------------------------------------------
    # Create new wavelength solution
    # ------------------------------------------------------------------

    start = min(p['IC_HC_N_ORD_START_2'], p['IC_FP_N_ORD_START'])
    end = max(p['IC_HC_N_ORD_FINAL_2'], p['IC_FP_N_ORD_FINAL'])

    # recalculate echelle orders for Fit1DSolution
    o_orders = np.arange(start, end)
    echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
    loc['ECHELLE_ORDERS'] = echelle_order
    loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

    # select the orders to fit
    lls = loc['LITTROW_EXTRAP_SOL_1'][start:end]
    loc = spirouTHORCA.Fit1DSolution(p, loc, lls, iteration=2)

    # ------------------------------------------------------------------
    # Calculate uncertainties
    # ------------------------------------------------------------------

    # # First solution (without smoothing)
    # mean1 = np.mean(res_1)
    # var1 = np.var(res_1)
    # num_lines = len(res_1)
    #
    # # Second soluthion (with smoothing) if applicable
    # if poly_smooth:
    #     mean1 = np.mean(res_2)
    #     var1 = np.var(res_2)
    #     num_lines = len(res_2)
    #
    # # print statistics
    # wmsg1 = 'On fiber {0} fit line statistic:'.format(p['FIBER'])
    # wargs2 = [mean1*1000., np.sqrt(var1)*1000., num_lines,
    #           1000.*np.sqrt(var1/num_lines)]
    # wmsg2 = ('\tmean={0:.3f}[m/s] rms={1:.1f} {2} lines (error on mean '
    #              'value:{3:.2f}[m/s])'.format(*wargs2))
    # WLOG(p, 'info', [wmsg1, wmsg2])
    #
    # # Save to loc for later use - names given for coherence with cal_HC
    # loc['X_MEAN_1'] = mean1
    # loc['X_VAR_1'] = var1
    # loc['X_ITER_1'] = num_lines

    # ------------------------------------------------------------------
    # Repeat Littrow test
    # ------------------------------------------------------------------

    # Reset the cut points
    p['IC_LITTROW_CUT_STEP_2'] = 500

    # reset Littrow fit degree
    p['IC_LITTROW_FIT_DEG_2'] = 8

    # Do Littrow check
    ckwargs = dict(ll=loc['LL_OUT_2'][start:end, :], iteration=2, log=True)
    loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

    # Plot wave solution littrow check
    if p['DRS_PLOT'] > 0:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_check_plot(p, loc, iteration=2)

    # ------------------------------------------------------------------
    # Plot single order, wavelength-calibrated, with found lines
    # ------------------------------------------------------------------

    # set order to plot
    plot_order = 7
    # get the correct order to plot for all_lines (which is sized
    #     n_ord_final-n_ord_start)
    plot_order_line = plot_order - n_ord_start
    plt.figure()
    # plot order and flux
    plt.plot(wave_map2[plot_order], hcdata[plot_order],
             label='HC spectrum - order '
                   + str(plot_order))
    # plot found lines
    # first line separate for labelling purposes
    plt.vlines(all_lines_1[plot_order_line][0][0], 0,
               all_lines_1[plot_order_line][0][2],
               'm', label='fitted lines')
    # plot lines to the top of the figure
    plt.vlines(all_lines_1[plot_order_line][0][0], 0,
               np.max(hcdata[plot_order]), 'gray',
               linestyles='dotted')
    # rest of lines
    for i in range(1, len(all_lines_1[plot_order_line])):
        # plot lines to their corresponding amplitude
        plt.vlines(all_lines_1[plot_order_line][i][0], 0,
                   all_lines_1[plot_order_line][i][2],
                   'm')
        # plot lines to the top of the figure
        plt.vlines(all_lines_1[plot_order_line][i][0], 0,
                   np.max(hcdata[plot_order]), 'gray',
                   linestyles='dotted')
    plt.legend()
    plt.xlabel('Wavelength')
    plt.ylabel('Flux')

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # get parameters ffrom p
    p['QC_RMS_LITTROW_MAX'] = p['QC_HC_RMS_LITTROW_MAX']
    p['QC_DEV_LITTROW_MAX'] = p['QC_HC_DEV_LITTROW_MAX']
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # check for infinites and NaNs in mean residuals from fit
    if ~np.isfinite(loc['X_MEAN_2']):
        # add failed message to the fail message list
        fmsg = 'NaN or Inf in X_MEAN_2'
        fail_msg.append(fmsg)
        passed = False
    # iterate through Littrow test cut values
    # if smoothing done need to use Littrow 2, otherwise 1
    if poly_smooth:
        lit_it = 2
    else:
        lit_it = 2
    # for x_it in range(len(loc['X_CUT_POINTS_lit_it'])):
    # checks every other value
    for x_it in range(1, len(loc['X_CUT_POINTS_' + str(lit_it)]), 4):
        # get x cut point
        x_cut_point = loc['X_CUT_POINTS_' + str(lit_it)][x_it]
        # get the sigma for this cut point
        sig_littrow = loc['LITTROW_SIG_' + str(lit_it)][x_it]
        # get the abs min and max dev littrow values
        min_littrow = abs(loc['LITTROW_MINDEV_' + str(lit_it)][x_it])
        max_littrow = abs(loc['LITTROW_MAXDEV_' + str(lit_it)][x_it])
        # check if sig littrow is above maximum
        rms_littrow_max = p['QC_RMS_LITTROW_MAX']
        dev_littrow_max = p['QC_DEV_LITTROW_MAX']
        if sig_littrow > rms_littrow_max:
            fmsg = ('Littrow test (x={0}) failed (sig littrow = '
                    '{1:.2f} > {2:.2f})')
            fargs = [x_cut_point, sig_littrow, rms_littrow_max]
            fail_msg.append(fmsg.format(*fargs))
            passed = False
        # check if min/max littrow is out of bounds
        if np.max([max_littrow, min_littrow]) > dev_littrow_max:
            fmsg = ('Littrow test (x={0}) failed (min|max dev = '
                    '{1:.2f}|{2:.2f} > {3:.2f})')
            fargs = [x_cut_point, min_littrow, max_littrow, dev_littrow_max]
            fail_msg.append(fmsg.format(*fargs))
            passed = False
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG(p, 'info',
             'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG(p, 'warning', wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ------------------------------------------------------------------
    # archive result in e2ds spectra
    # ------------------------------------------------------------------

    # get wave filename
    wavefits = spirouConfig.Constants.WAVE_FILE_EA(p)
    wavefitsname = os.path.split(wavefits)[-1]

    # log progress
    wargs = [p['FIBER'], wavefits]
    wmsg = 'Write wavelength solution for Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(*wargs))
    # write solution to fitsfilename header
    # copy original keys
    hdict = spirouImage.CopyOriginalKeys(loc['HCHDR'])
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])

    # add quality control
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    # add number of orders
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_ORD_N'],
                               value=loc['LL_PARAM_FINAL'].shape[0])
    # add degree of fit
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_LL_DEG'],
                               value=loc['LL_PARAM_FINAL'].shape[1] - 1)
    # add wave solution
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                     values=loc['LL_PARAM_FINAL'])
    # write original E2DS file and add header keys (via hdict)
    # spirouImage.WriteImage(p['FITSFILENAME'], loc['HCDATA'], hdict)

    # write the wave "spectrum"
    spirouImage.WriteImage(wavefits, loc['LL_FINAL'], hdict)

    # get filename for E2DS calibDB copy of FITSFILENAME
    e2dscopy_filename = spirouConfig.Constants.WAVE_E2DS_COPY(p)

    wargs = [p['FIBER'], os.path.split(e2dscopy_filename)[-1]]
    wmsg = 'Write reference E2DS spectra for Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(*wargs))

    # make a copy of the E2DS file for the calibBD
    spirouImage.WriteImage(e2dscopy_filename, loc['HCDATA'], hdict)

    # ------------------------------------------------------------------
    # Save to result table
    # ------------------------------------------------------------------
    # calculate stats for table
    final_mean = 1000 * loc['X_MEAN_2']
    final_var = 1000 * loc['X_VAR_2']
    num_lines = int(np.nansum(loc['X_ITER_2'][:, 2]))  # loc['X_ITER_2']
    err = 1000 * np.sqrt(loc['X_VAR_2'] / num_lines)
    sig_littrow = 1000 * np.array(loc['LITTROW_SIG_' + str(lit_it)])
    # construct filename
    wavetbl = spirouConfig.Constants.WAVE_TBL_FILE_EA(p)
    wavetblname = os.path.split(wavetbl)[-1]
    # construct and write table
    columnnames = ['night_name', 'file_name', 'fiber', 'mean', 'rms',
                   'N_lines', 'err', 'rms_L500', 'rms_L1000', 'rms_L1500',
                   'rms_L2000', 'rms_L2500', 'rms_L3000', 'rms_L3500']
    columnformats = ['{:20s}', '{:30s}', '{:3s}', '{:7.4f}', '{:6.2f}',
                     '{:3d}', '{:6.3f}', '{:6.2f}', '{:6.2f}', '{:6.2f}',
                     '{:6.2f}', '{:6.2f}', '{:6.2f}', '{:6.2f}']
    columnvalues = [[p['ARG_NIGHT_NAME']], [p['ARG_FILE_NAMES'][0]],
                    [p['FIBER']], [final_mean], [final_var],
                    [num_lines], [err], [sig_littrow[0]],
                    [sig_littrow[1]], [sig_littrow[2]], [sig_littrow[3]],
                    [sig_littrow[4]], [sig_littrow[5]], [sig_littrow[6]]]
    # make table
    table = spirouImage.MakeTable(p, columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # merge table
    wmsg = 'Global result summary saved in {0}'
    WLOG(p, '', wmsg.format(wavetblname))
    spirouImage.MergeTable(p, table, wavetbl, fmt='ascii.rst')

    # ------------------------------------------------------------------
    # Save line list table file
    # ------------------------------------------------------------------
    # construct filename

    # TODO proper column values

    wavelltbl = spirouConfig.Constants.WAVE_LINE_FILE_EA(p)
    wavelltblname = os.path.split(wavelltbl)[-1]
    # construct and write table
    columnnames = ['order', 'll', 'dv', 'w', 'xi', 'xo', 'dvdx']
    columnformats = ['{:.0f}', '{:12.4f}', '{:13.5f}', '{:12.4f}',
                     '{:12.4f}', '{:12.4f}', '{:8.4f}']
    columnvalues = []
    # construct column values (flatten over orders)
    for it in range(n_ord_start, n_ord_final):
        gg = (ord_save == it)
        for jt in range(len(loc['ALL_LINES_FINAL'][it])):
            row = [float(it), loc['ALL_LINES_FINAL'][it][jt][0],
                   res_1[gg][jt],
                   loc['ALL_LINES_FINAL'][it][jt][7],
                   loc['ALL_LINES_FINAL'][it][jt][5],
                   loc['ALL_LINES_FINAL'][it][jt][5],
                   res_1[gg][jt]]
            columnvalues.append(row)

    # log saving
    wmsg = 'List of lines used saved in {0}'
    WLOG(p, '', wmsg.format(wavelltblname))

    # make table
    columnvalues = np.array(columnvalues).T
    table = spirouImage.MakeTable(p, columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # write table
    spirouImage.WriteTable(p, table, wavelltbl, fmt='ascii.rst')

    # ------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ------------------------------------------------------------------
    if p['QC']:
        # set the wave key
        keydb = 'WAVE_{0}'.format(p['FIBER'])
        # copy wave file to calibDB folder
        spirouDB.PutCalibFile(p, wavefits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, wavefitsname, loc['HCHDR'])

        # set the hcref key
        keydb = 'HCREF_{0}'.format(p['FIBER'])
        # copy wave file to calibDB folder
        spirouDB.PutCalibFile(p, e2dscopy_filename)
        # update the master calib DB file with new key
        e2dscopyfits = os.path.split(e2dscopy_filename)[-1]
        spirouDB.UpdateCalibMaster(p, keydb, e2dscopyfits, loc['HCHDR'])

    # return p and loc
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

#

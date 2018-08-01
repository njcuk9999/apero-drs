#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_HC_E2DS_spirou.py [night_directory] [fitsfilename]

Wavelength calibration

Created on 2018-07-20

@author: artigau, hobson
"""

#import matplotlib.pyplot as plt
from astropy.io import ascii

from scipy.optimize import curve_fit

import numpy as np

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA

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
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict

# =============================================================================
# Auxiliary functions - to be moved elsewhere later
# =============================================================================

def lin_mini(vector, sample):
    import numpy as np

    sz_sample = np.shape(sample)
    sz_vector = np.shape(vector)

    if sz_vector[0] == sz_sample[0]:
        cas = 2
    if sz_vector[0] == sz_sample[1]:
        cas = 1

    #
    # vecteur de N elements
    # sample : matrice N*M, chacune des M colonnes est ajustee en amplitude pour minimiser le chi2 par rapport au vecteur d'entree
    # output : vecteur de M de long qui donne les amplitudes de chaque colonne
    #
    # returns NaN values as amplitudes if the sample vectors lead to an auto-correlation matrix that
    # cannot be inverted (i.e., that are full of zeros or are not linearly independent)
    #
    vector = np.asarray(vector)
    sample = np.asarray(sample)
    sz_sample = np.shape(sample)
    sz_vector = np.shape(vector)

    if cas == 1:
        #
        M = np.zeros([sz_sample[0], sz_sample[0]])
        #
        v = np.zeros(sz_sample[0])

        for i in range(sz_sample[0]):
            for j in range(i, sz_sample[0]):
                M[i, j] = np.sum(sample[i, :] * sample[j, :])
                M[j, i] = M[i, j]
            v[i] = np.sum(vector * sample[i, :])
        #
        if np.linalg.det(M) == 0:
            amps = np.zeros(sz_sample[0]) + np.nan
            recon = np.zeros_like(v)
            return (amps, recon)

        amps = np.matmul(np.linalg.inv(M), v)
        #
        recon = np.zeros(sz_sample[1])
        #
        for i in range(sz_sample[0]):
            recon += amps[i] * sample[i, :]
        #
        return (amps, recon)

    if cas == 2:
        # print('cas = 2')
        # print(sz_sample[1])
        M = np.zeros([sz_sample[1], sz_sample[1]])
        v = np.zeros(sz_sample[1])

        for i in range(sz_sample[1]):
            for j in range(i, sz_sample[1]):
                M[i, j] = np.sum(sample[:, i] * sample[:, j])
                M[j, i] = M[i, j]
            v[i] = np.sum(vector * sample[:, i])

        if np.linalg.det(M) == 0:
            amps = np.zeros(sz_sample[1]) + np.nan
            recon = np.zeros_like(v)
            return (amps, recon)

        amps = np.matmul(np.linalg.inv(M), v)

        recon = np.zeros(sz_sample[0])

        for i in range(sz_sample[1]):
            recon += amps[i] * sample[:, i]

        return (amps, recon)


def GAUSS_FUNCT(x, a):
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
    Z = (x - a[1]) / a[2]  #
    EZ = np.exp(-Z ** 2 / 2.)  # GAUSSIAN PART
    #
    if n == 3:
        F = a[0] * EZ
    if n == 4:
        F = a[0] * EZ + a[3]
    if n == 5:
        F = a[0] * EZ + a[3] + a[4] * x
    if n == 6:
        F = a[0] * EZ + a[3] + a[4] * X + a[5] * X ^ 2
    #
    PDER = np.zeros([nx, n])
    PDER[:, 0] = EZ  # COMPUTE PARTIALS
    PDER[:, 1] = a[0] * EZ * Z / a[2]
    PDER[:, 2] = PDER[:, 1] * Z
    if n > 3:
        PDER[:, 3] = 1.0
    if n > 4:
        PDER[:, 4] = x
    if n > 5:
        PDER[:, 5] = x ** 2
    return F, PDER


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
    # [ amplitude , center of peak, amplitude of peak, [dc level], [slope], [2nd order tern] ]
    #

    # we guess that the Gaussian is close to Nyquist and has a
    # 2 PIX FWHM and therefore 2/2.54 e-width
    ew_guess = 2 * np.median(np.gradient(xpix)) / 2.354

    if nn == 3:
        # only amp, cen and ew
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess]
    if nn == 4:
        # only amp, cen, ew, dc offset
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess, np.min(ypix)]
    if nn == 5:
        # only amp, cen, ew, dc offset, slope
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess, np.min(ypix), 0]
    if nn == 6:
        # only amp, cen, ew, dc offset, slope, curvature
        a0 = [np.max(ypix) - np.min(ypix), xpix[np.argmax(ypix)], ew_guess, np.min(ypix), 0, 0]

    residu_prev = np.array(ypix)

    gfit, pder = GAUSS_FUNCT(xpix, a0)

    rms = 99
    nite = 0

    # loops for 20 iterations MAX or an RMS with an RMS change in residual smaller than 1e-6 of peak
    while (rms > 1e-6) & (nite <= 20):
        gfit, pder = GAUSS_FUNCT(xpix, a0)
        residu = ypix - gfit

        amps, fit = lin_mini(residu, pder)
        a0 += amps
        rms = np.std(residu - residu_prev) / (np.max(ypix) - np.min(ypix))

        residu_prev = residu
        nite += 1

    return a0, gfit

# =============================================================================
# End auxiliary functions
# =============================================================================

# ----------------------------------------------------------------------
# Set up
# ----------------------------------------------------------------------

# test files
night_name = 'AT5/AT5-12/2018-05-29_17-41-44/'
fpfile = '2279844a_fp_fp_pp_e2dsff_AB.fits'
hcfiles = ['2279845c_hc_pp_e2dsff_AB.fits']

# get parameters from config files/run time args/load paths + calibdb
p = spirouStartup.Begin(recipe=__NAME__)
if hcfiles is None or fpfile is None:
    names, types = ['fpfile', 'hcfiles'], [str, str]
    customargs = spirouStartup.GetCustomFromRuntime([0, 1], types, names,
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
    WLOG('error', p['LOG_OPT'], emsg.format(*eargs))
# set the fiber type
p['FIB_TYP'] = [p['FIBER']]
p.set_source('FIB_TYP', __NAME__ + '/main()')


# =============================================================================
# Defining a Gaussian with a DC level and slope underneath
# =============================================================================
def gauss_function(x, a, x0, sig, zp, slope):
    sig = np.abs(sig)
    return a * np.exp(-(x - x0) ** 2 / (2 * sig ** 2)) + zp + \
           (x - np.mean(x)) * slope


# =============================================================================
# input parameters
# =============================================================================

 # read and combine all HC files except the first (fpfitsfilename)
rargs = [p, 'add', hcfitsfilename, hcfilenames[1:]]
p, hcdata, hchdr, hccdr = spirouImage.ReadImageAndCombine(*rargs)
# read first file (fpfitsfilename)
fpdata, fphdr, fpcdr, _, _ = spirouImage.ReadImage(p, fpfitsfilename)

# add data and hdr to loc
loc = ParamDict()
loc['HCDATA'], loc['HCHDR'], loc['HCCDR'] = hcdata, hchdr, hccdr
loc['FPDATA'], loc['FPHDR'], loc['FPCDR'] = fpdata, fphdr, fpcdr
# set the source
sources = ['HCDATA', 'HCHDR', 'HCCDR']
loc.set_sources(sources, 'spirouImage.ReadImageAndCombine()')
sources = ['FPDATA', 'FPHDR', 'FPCDR']
loc.set_sources(sources, 'spirouImage.ReadImage()')

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

# wavelength file; we will use the polynomial terms in its header,
# NOT the pixel values that would need to be interpolated

# getting header info with wavelength polynomials
wdata = spirouImage.ReadWaveFile(p, hchdr, return_header=True)
wave, wave_hdr = wdata
loc['WAVE'] = wave
loc['WAVEHDR'] = wave_hdr
loc.set_source('WAVE', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

# get wave params from wave header
poly_wave_sol = spirouImage.ReadWaveParams(p, wave_hdr)
loc['WAVEPARAMS'] = poly_wave_sol
loc.set_source('WAVEPARAMS', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

# control plotting
doplot_per_order=False
doplot_sanity=True

# =============================================================================

# generate initial wavelength map
wave_map = np.zeros([49, 4088])
xpix = np.array(range(4088))
for iord in range(49):
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
peak = []
dx = []
ord = []
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
WLOG('info', p['LOG_OPT'], wmsg.format())

for iord in range(49):
    # keep track of pixels where we look for peaks

    if doplot_per_order:
        plt.plot(wave[iord, :], hcdata[iord, :])

    # print order message
    wmsg = 'Searching for peaks in order {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(iord))

    # scanning through each order, 1/3rd of w at a time
    for indmax in range(window * 2, 4088 - window * 2 - 1, window // 3):
        xpix = np.asarray(range(indmax - window, indmax + window))
        segment = np.array(hcdata[iord, indmax - window:indmax + window])
        rms = np.median(np.abs(segment[1:] - segment[:-1]))
        peak = (np.max(segment) - np.nanmedian(segment))

        # peak needs to be well-behaved
        keep = True
        keep &= (rms != 0)
        keep &= (peak != 0)
        keep &= (peak / rms > sigma_peak)

        # position of peak within segment. It needs to be close enough to the
        # center of the segment
        # if it is at the edge, we'll catch it in the following iteration
        #
        # we keep (or not) the peak
        imax = np.argmax(segment) - window
        #
        keep &= (np.abs(imax) < window // 3)

        if keep:
            # fit a gaussian with a slope
            popt_left, g2 = gaussfit(xpix, segment, 5)

            # the residual of the
            gauss_rms_dev0 = np.std(segment - g2) / popt_left[0]

            # all values that will be added (if keep_peak=True) to the vector of all line
            # parameters
            zp0 = popt_left[3]
            slope0 = popt_left[4]
            ew0 = popt_left[2]
            xgau0 = popt_left[1]
            peak0 = popt_left[0]

            keep_peak = True

            # the RMS of line-fitted line must be before 0 and 0.2 of the peak value
            gauss_rms_dev_min = 0
            gauss_rms_dev_max = 0.1

            # the e-width of the line must be between 0.7 and 1.1 pixel
            ew_min = 0.7
            ew_max = 1.1
            wave0 = np.polyval((poly_wave_sol[iord, :])[::-1], xgau0)

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
                peak = np.append(peak, peak0)
                ord = np.append(ord, iord)
                gauss_rms_dev = np.append(gauss_rms_dev, gauss_rms_dev0)
                wave_hdr_sol = np.append(wave_hdr_sol, wave0)

                if doplot_per_order:
                    plt.plot(wave[iord, xpix], g2)
    if doplot_per_order:
        plt.show()


# reading the UNe catalog
wave_UNe, amp_UNe = spirouImage.ReadLineList(p)
loc['LL_LINE'], loc['AMPL_LINE'] = wave_UNe, amp_UNe
source = __NAME__ + '/main() + spirouImage.ReadLineList()'
loc.set_sources(['ll_line', 'ampl_line'], source)

wmsg = 'Matching found lines to the catalogue'
WLOG('info', p['LOG_OPT'], wmsg.format())

# keeping track of the velocity offset between predicted and observed line centers
dv = np.zeros(len(wave_hdr_sol)) + np.nan

# wavelength given in the catalog for the matched line
wave_catalog = np.zeros(len(wave_hdr_sol)) + np.nan
i = -1
for wave0 in wave_hdr_sol:
    i += 1
    # find closest catalog line to the line considered
    idmin = np.argmin(np.abs(wave_UNe - wave0))
    ddv = (wave_UNe[idmin] / wave0 - 1) * 2.997e8
    # if within 2km/s, we consider a match
    if np.abs(ddv) < 30000:
        dv[i] = ddv
        wave_catalog[i] = wave_UNe[idmin]

# define 100-nm bins
# TODO why not from 900?
xbins = np.array(range(1000, 2200, 100))

# plot found lines - wavelength vs velocity offset from catalogue
plt.clf()
plt.plot(wave_catalog, dv, 'g.', label='all lines')
plt.xlabel('wavelength')
plt.ylabel('velocity offset from catalogue')

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
        wargs = [xbin, xbin+100, np.sum(g)]
        wmsg = 'In wavelength bin {0}-{1}, {2} lines w/finite velocity offset from cat.'
        WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

        i += 1

    # 3rd degree polynomial fit to the center of bins vs median dv per bin
    fit = np.polyfit(xbins + 50, meddv, 3)
    # evaluate fit on all lines to get a predicted velocity offset
    dv_pred = np.polyval(fit, wave_catalog)

    # get median-normalised difference from predicted velocity offset
    err = np.abs(dv - dv_pred) / np.nanmedian(np.abs(dv - dv_pred))
    # if difference >5, set dv to nan
    dv[err > 5] = np.nan

if doplot_sanity:
    # plot the predicted velocity offset from the catalogue
    plt.plot(wave_catalog, dv_pred, 'k.', label='predicted offset')
    # overplot the kept lines (difference from predicted offset <5)
    plt.plot(wave_catalog, dv, 'c.', label='kept lines')
    plt.legend()
    plt.show()

# for each order, we fit a 4th order polynomial between pix and wavelength
fit_per_order = np.zeros([5, 49])

wmsg = 'Sigma-clipping of found lines'
WLOG('info', p['LOG_OPT'], wmsg.format())

# loop through orders
for iord in range(49):
    # keep relevant lines
    # -> right order
    # -> finite dv
    gg = (ord == iord) & (np.isfinite(dv))
    nlines = np.sum(gg)

    # if we have less than 10 lines, then its bad
    if nlines >= 10:

        nsigmax = 999

        # we perform a sigma clipping of lines with a 2nd order polynomial
        # of the dV vs pixel position, this is only used for sigma-clipping
        while nsigmax > 3:
            fit = np.polyfit(xgau[gg], dv[gg], 2)

            # plt.plot(xgau[gg],dv[gg]-np.polyval(fit,xgau[gg]),'r.')
            # plt.show()

            dd = dv[gg] - np.polyval(fit, xgau[gg])
            # print info
            wargs = [iord, nsigmax, np.std(dd)]
            wmsg = 'Sigma-clip for order {0}: sigma={1:.2f}, vel. offset vs pix stddev={2:.2f}'
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

            dd /= np.std(dd)

            argmax = np.argmax(np.abs(dd))
            nsigmax = np.abs(dd[argmax])

            # print info
            np.set_printoptions(precision=3)
            wargs = [fit, nsigmax]
            wmsg = 'vel. offset vs pix coeffs: {0}, sigma={1:.2f}'
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

            # if the largest deviation from the 2nd order fit is >3 sigma (either + or -)
            # then we remove the point
            if nsigmax > 3:
                tmp = gg[gg]
                tmp[argmax] = False
                gg[gg] = tmp

        if doplot_sanity:
            plt.plot(wave_catalog[gg], xgau[gg], '.')
            plt.xlabel('wavelength')
            plt.ylabel('pixel position')

        # the pix VS wavelength is fitted with a 4th order polynomial
        fit_per_order[:, iord] = np.polyfit(xgau[gg], wave_catalog[gg], 4)

if doplot_sanity:
    plt.show()

wave_map2 = np.zeros([49, 4088])
xpix = np.array(range(4088))
for i in range(49):
    wave_map2[i, :] = np.polyval(fit_per_order[:, i], xpix)

# ===============================================================================================
# bit of code that smooths the coefficient VS nth order relations
# DOES NOT WORK (yet...)
# ===============================================================================================
# x index in the smoothing of the nth-order VS coefficient

if True:

    plt.clf()
    wmsg = 'Forcing continuity of the polynomial fit coefficients'
    WLOG('info', p['LOG_OPT'], wmsg.format())

    # We will force continuity of the coefficients of the polynomial
    # fit. The 1st term (wavelength at pix=0) is much better determined
    # than the 4th order-term. This is why the polynomial fit
    # used to force continuity is low-order for the higher-order
    # terms in the wavelength solutions.
    order_fit_continuity = [2, 2, 4, 8, 12]

    nth_order = np.array(range(49))

    # keeping track of the best estimates for the polynomial
    # coefficients
    new_wavelength_solution_polyfit = np.zeros([5, 49])

    for nth_poly_order in range(5):

        tmp = fit_per_order[nth_poly_order, :]

        nsigmax = 999

        keep = np.ones([49], dtype=bool)

        ite = 0
        # sigma clipping on linear fit to remove few large outliers
        # avoids biassing high-order polynomials by these outliers
        while nsigmax > 3:
            fit = np.polyfit(nth_order[keep], tmp[keep], 1)
            err = tmp - np.polyval(fit, nth_order)

            idmax = np.argmax(np.abs(err * keep / np.std(err[keep])))
            nsigmax = np.max(np.abs(err * keep / np.std(err[keep])))

            keep[idmax] = False

            # print information to screen
            wargs = [nth_poly_order, nsigmax, np.mean(keep), ite]
            wmsg = 'Coeff order {0}: ' \
                   'Linear sigma-clip: sigma={1:.2f}, qc?={2:.2f}, iteration={3}'
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

            ite += 1

        nsigmax = 999

        # sigma-clipping of the order VS polynomial coefficients.
        # using higher-order polynomial
        while nsigmax > 3:
            fit = np.polyfit(nth_order[keep], tmp[keep], order_fit_continuity[nth_poly_order])
            err = tmp - np.polyval(fit, nth_order)

            idmax = np.argmax(np.abs(err * keep / np.std(err[keep])))
            nsigmax = np.max(np.abs(err * keep / np.std(err[keep])))

            keep[idmax] = False

            # print information to screen
            wargs = [nth_poly_order, nsigmax, np.mean(keep), ite]
            wmsg = 'Coeff order {0}: ' \
                   'Polynomial sigma-clip: sigma={1:.2f}, qc?={2:.2f}, iteration={3}'
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

            ite += 1

        if doplot_sanity:
            plt.subplot(5, 2, 1 + nth_poly_order * 2)

            plt.title('p order ' + str(5 - nth_poly_order))
            plt.plot(nth_order, tmp, 'r.')
            plt.plot(nth_order[keep], tmp[keep], 'g.')
            plt.plot(nth_order, np.polyval(fit, nth_order), 'k-')
            plt.ylabel('pix')

            plt.xlabel('$\lambda$ (nm)')

            plt.subplot(5, 2, 2 + nth_poly_order * 2)

            plt.title('p order ' + str(5 - nth_poly_order))
            plt.ylabel('residual pix')
            plt.xlabel('$\lambda$ (nm)')
            plt.plot(nth_order[keep], err[keep], 'c.')


        new_wavelength_solution_polyfit[nth_poly_order, :] = np.polyval(fit, nth_order)

    wave_map3 = np.zeros([49, 4088])
    xpix = np.array(range(4088))
    for iord in range(49):
        wave_map3[iord, :] = np.polyval(new_wavelength_solution_polyfit[:, iord], xpix)

    nsigmax = 999
    if doplot_sanity:
        plt.plot()
        plt.clf()

# ===============================================================================================
# ===============================================================================================

hc_ini = np.array(hcdata)
# determining the LSF
resolution_map = np.zeros([5, 4])

wmsg = 'Determining the LSF'
WLOG('info', p['LOG_OPT'], wmsg.format())

i_plot = 0
# determining the LSF
bin_ord = 10
for iord in range(0, 49, bin_ord):
    for xpos in range(0, 4):
        plt.subplot(5, 4, i_plot + 1)
        gg = (gauss_rms_dev < 0.05)
        gg &= (ord // 10 == iord // 10)
        gg &= (xgau // 1024) == xpos
        gg &= np.isfinite(wave_catalog)

        xcens = xgau[gg]
        orders = ord[gg]
        wave_line = wave_catalog[gg]

        all_lines = np.zeros([np.sum(gg), 2 * window + 1])
        all_dvs = np.zeros([np.sum(gg), 2 * window + 1])

        base = np.zeros(2 * window + 1, dtype=bool)
        base[0:3] = True
        base[2 * window - 2:2 * window + 1] = True
        for i in range(np.sum(gg)):
            all_lines[i, :] = hc_ini[int(orders[i]), int(xcens[i] + .5) - window:int(xcens[i] + .5) + window + 1]
            all_lines[i, :] -= np.nanmedian(all_lines[i, base])
            all_lines[i, :] /= np.nansum(all_lines[i, :])


            v = -2.997e5 * (wave_map2[int(orders[i]), int(xcens[i] + .5) -
                                                      window:int(xcens[i] + .5) + window + 1]
                            / wave_line[i] - 1)
            all_dvs[i, :] = v


        all_dvs = all_dvs.ravel()
        all_lines = all_lines.ravel()

        keep = np.ones(len(all_dvs), dtype=bool)
        #keep[np.isfinite(all_lines)==False] = False

        maxdev = 999
        maxdev_threshold = 8

        while maxdev > maxdev_threshold:
            popt_left, pcov = curve_fit(gauss_function, all_dvs[keep], all_lines[keep],
                                        p0=[.3, 0, 1, 0, 0])
            res = all_lines - gauss_function(all_dvs, popt_left[0], popt_left[1],
                                             popt_left[2], popt_left[3], popt_left[4])

            rms = (res) / np.median(np.abs(res))
            maxdev = np.max(np.abs(rms[keep]))
            keep[np.abs(rms) > maxdev_threshold] = False
        resolution = popt_left[2] * 2.354

        plt.plot(all_dvs[keep], all_lines[keep], 'g.')

        xx = (np.array(range(301)) - 150) / 10.
        gplot = gauss_function(xx, popt_left[0], popt_left[1], popt_left[2],
                               popt_left[3], popt_left[4])

        plt.plot(xx, gplot, 'k--')
        wargs = [np.sum(gg), iord, iord+9, xpos, resolution, 2.997e5 / resolution]
        wmsg = 'nlines={0}, orders={1}-{2}, x region={3}, resolution={4:.2f} km/s, R={5:.2f}'
        WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

#        print('nlines : ', np.sum(gg), 'iord=', iord, ' xpos=', xpos,
#              ' resolution = ', resolution, ' km/s', 'R = ',
#              2.997e5 / resolution)
        plt.xlim([-8, 8])
        plt.ylim([-0.05, .7])
        plt.title('orders ' + str(iord) + '-' + str(iord + 9) + ' region=' + str(xpos))
        plt.xlabel('dv (km/s)')

        i_plot += 1

        resolution_map[iord // bin_ord, xpos] = 2.997e5 / resolution

plt.tight_layout()
plt.show()

wargs = [np.mean(resolution_map), np.median(resolution_map), np.std(resolution_map)]
wmsg = 'Resolution stats:  mean={0:.2f}, median={1:.2f}, stddev={2:.2f}'
WLOG('info', p['LOG_OPT'], wmsg.format(*wargs))

#print('mean resolution : ', np.mean(resolution_map))
#print('median resolution : ', np.median(resolution_map))
#print('stddev resolution : ', np.std(resolution_map))


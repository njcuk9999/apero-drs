# looping through e2ds orders to find HC peaks.
#  -- Method
#
# We find the highest pixel, fit a gaussian to it (-w to +w window) and
# keep its e-width as well as other parameters that may be used as quality
# checks the "keep" vector is used to keep track of pixels where we haven't
# had a window yet and may find a peak

from astropy.io import fits as pyfits
import matplotlib.pyplot as plt

from astropy.io import ascii
from scipy.optimize import curve_fit

import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS.spirouCore.spirouMath import nanpolyfit


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DARK_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt

p = spirouStartup.Begin(recipe=__NAME__)
p = spirouStartup.LoadArguments(p)


# =============================================================================
# Defining a Gaussian with a DC level and slope underneath
# =============================================================================
def gauss_function(x, a, x0, sigma, zp, slope):
    sigma = np.abs(sigma)
    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + zp + (
            x - np.mean(x)) * slope


def gauss_funct(x, a):
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
    #   FUNCT,X,A,F,pder
    # INPUTS:
    #   X = VALUES OF INDEPENDENT VARIABLE.
    #   A = PARAMETERS OF EQUATION DESCRIBED BELOW.
    # OUTPUTS:
    #   F = VALUE OF FUNCTION AT EACH X(I).
    #   pder = matrix with the partial derivatives for function fitting
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
    if n == 3:
        ff = a[0] * ezz
    if n == 4:
        ff = a[0] * ezz + a[3]
    if n == 5:
        ff = a[0] * ezz + a[3] + a[4] * x
    if n == 6:
        ff = a[0] * ezz + a[3] + a[4] * x + a[5] * x ** 2
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
    # noinspection PyUnboundLocalVariable
    return ff, pder


def gaussfit(xpix1, ypix1, nn):
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
    # [ amplitude , center of peak, amplitude of peak, [dc level], [slope],
    # [2nd order tern] ]
    #

    # we guess that the Gaussian is close to Nyquist and has a
    # 2 PIX FWHM and therefore 2/2.54 e-width
    ew_guess = 2 * np.nanmedian(np.gradient(xpix1)) / 2.3548200450309493

    if nn == 3:
        # only amp, cen and ew
        a0 = [np.max(ypix1) - np.min(ypix1), xpix1[np.argmax(ypix1)], ew_guess]
    if nn == 4:
        # only amp, cen, ew, dc offset
        a0 = [np.max(ypix1) - np.min(ypix1), xpix1[np.argmax(ypix1)], ew_guess,
              np.min(ypix1)]
    if nn == 5:
        # only amp, cen, ew, dc offset, slope
        a0 = [np.max(ypix1) - np.min(ypix1), xpix1[np.argmax(ypix1)], ew_guess,
              np.min(ypix1), 0]
    if nn == 6:
        # only amp, cen, ew, dc offset, slope, curvature
        a0 = [np.max(ypix1) - np.min(ypix1), xpix1[np.argmax(ypix1)], ew_guess,
              np.min(ypix1), 0, 0]

    residu_prev = np.array(ypix1)

    # noinspection PyUnboundLocalVariable
    gfit, pder = gauss_funct(xpix1, a0)

    rms1 = 99
    nite = 0

    # loops for 20 iterations MAX or an RMS with an RMS change in residual
    # smaller than 1e-6 of peak
    while (rms1 > 1e-6) & (nite <= 20):
        gfit, pder = gauss_funct(xpix1, a0)
        residu = ypix1 - gfit

        amps1, fit1 = lin_mini(residu, pder)
        a0 += amps1
        rms1 = np.std(residu - residu_prev) / (np.max(ypix1) - np.min(ypix1))

        residu_prev = residu
        nite += 1

    return a0, gfit


def lin_mini(vector, sample):
    sz_sample = np.shape(sample)
    sz_vector = np.shape(vector)

    if sz_vector[0] == sz_sample[0]:
        cas = 2
    if sz_vector[0] == sz_sample[1]:
        cas = 1

    #
    # vecteur de N elements
    # sample : matrice N*M, chacune des M colonnes est ajustee en amplitude
    # pour minimiser le chi2 par rapport au vecteur d'entree
    # output : vecteur de M de long qui donne les amplitudes de chaque colonne
    #
    # returns NaN values as amplitudes if the sample vectors lead to an
    # auto-correlation matrix that cannot be inverted (i.e., that are full of
    # zeros or are not linearly independent)
    #
    vector = np.asarray(vector)
    sample = np.asarray(sample)
    sz_sample = np.shape(sample)

    # noinspection PyUnboundLocalVariable
    if cas == 1:
        #
        mm = np.zeros([sz_sample[0], sz_sample[0]])
        #
        vv = np.zeros(sz_sample[0])

        for it in range(sz_sample[0]):
            for jt in range(it, sz_sample[0]):
                mm[it, jt] = np.nansum(sample[it, :] * sample[jt, :])
                mm[j, it] = mm[it, jt]
            vv[it] = np.nansum(vector * sample[it, :])
        #
        if np.linalg.det(mm) == 0:
            amps1 = np.zeros(sz_sample[0]) + np.nan
            recon1 = np.zeros_like(vv)
            return amps1, recon1

        amps1 = np.matmul(np.linalg.inv(mm), vv)
        #
        recon1 = np.zeros(sz_sample[1])
        #
        for it in range(sz_sample[0]):
            recon1 += amps1[it] * sample[it, :]
        #
        return amps1, recon1

    if cas == 2:
        # print('cas = 2')
        # print(sz_sample[1])
        mm = np.zeros([sz_sample[1], sz_sample[1]])
        vv = np.zeros(sz_sample[1])

        for it in range(sz_sample[1]):
            for jt in range(it, sz_sample[1]):
                mm[it, jt] = np.nansum(sample[:, it] * sample[:, jt])
                mm[jt, it] = mm[it, jt]
            vv[i] = np.nansum(vector * sample[:, it])

        if np.linalg.det(mm) == 0:
            amps1 = np.zeros(sz_sample[1]) + np.nan
            recon1 = np.zeros_like(vv)
            return amps1, recon1

        amps1 = np.matmul(np.linalg.inv(mm), vv)

        recon1 = np.zeros(sz_sample[0])

        for it in range(sz_sample[1]):
            recon1 += amps1[it] * sample[:, it]

        return amps1, recon1


# =============================================================================
# input parameters
# =============================================================================
# HC file that is used for wavelength solution estimate

# hcfile = '2295398c_pp_e2dsff_AB.fits'
# hcfile = '2279046c_pp_e2dsff_C.fits'
hcfile = '/scratch/Projects/spirou_py3/data_h4rg/reduced/AT5/20180409/' \
         'hcone_hcone_001_pp_e2ds_AB.fits'

# setting the fibre
p['fiber'] = 'AB'

# number of sigma above local RMS for a line to be flagged as such
sigma_peak = 2.0

# width of the box for fitting HC lines. Lines will be fitted from -W to +W,
# so a 2*W+1 window
w = 6

# reading HC e2ds
hc_sp = pyfits.getdata(hcfile)
hc_ini = np.array(hc_sp)

# getting header info with wavelength polynomials
# this can be a very poor fit, as long as the lines are within
# ~10 pixels, we're fine
wave_hdr = pyfits.getheader(hcfile)

# plot per-order. This is way too much plotting in most cases, just
# for debugging
doplot_per_order = False

# plot some sanity-check graphs along the way
doplot_sanity = True

file_catlog_urne = ('/scratch/Projects/spirou/drs/spirou_github/spirou_dev/'
                    'misc/INTROOT/SpirouDRS/data/wavelength_cats/'
                    'catalogue_UNe.dat')

# the RMS of line-fitted line must be before 0 and 0.2 of the peak value
# must be SNR>5 (or 1/SNR<0.2)
gauss_rms_dev_min = 0
gauss_rms_dev_max = 0.2

# the e-width of the line expressed in pixels. 
ew_min = 0.7
ew_max = 1.1

# number of bright lines kept per order 
# avoid >25 as it takes super long
# avoid <12 as some orders are ill-defined and we need >10 valid lines anyway
# 20 is a good number, and I see now reason to change it
nmax_bright = 20

# in the 3-lines alogrithm, we consider a line valid if it is within 500m/s
# of the fit
cut_fit_threshold = 1.0  # en km/s

# this sets the order of the polynomial used to ensure continuity in the xpix
# vs wave solutions
# by setting the first term = 12, we force that the zeroth element of the xpix
# of the wavelegnth
# grid is fitted with a 12th order polynomial as a function of order number
order_fit_continuity = [12, 9, 6, 2, 2]

# =============================================================================

# polynomial xpix/wavelength for all orders
poly_wave_sol, _ = spirouImage.GetWaveSolution(p, wave_hdr)

wave = np.zeros([49, 4088])
xpix = np.array(range(4088))
for iord in range(49):
    wave[iord, :] = np.polyval((poly_wave_sol[iord, :])[::-1], xpix)
    # creating a wavelength[pix] vector for all orders

# defining empty variables, so will be used later, others are just there to
# confuse the reader
ew_ini = []
xgau_ini = []
peak_ini = []
dx_ini = []
ord_ini = []
zp_ini = []
slope_ini = []
gauss_rms_dev_ini = []

# looping through e2ds orders to find HC peaks.
#  -- Method
#
# We find the highest pixel, fit a gaussian to it (-w to +w window) and keep
# its e-width
# as well as other parameters that may be used as quality checks
# the "keep" vector is used to keep track of pixels where we haven't had a
# window yet
# and may find a peak

xprev = -1  # to be sure we are not picking the same line twice, we force a >1
# pixel difference between consecutive lines

# as this part of the code is long, we will save an ASCII file with all the
# relevant parameters
# if the file is present, we just read it
catalog_name = (hcfile.split('.'))[0] + '_linelist_old.dat'

# checking if we have a catalog
if not os.path.isfile(catalog_name):
    for iord in range(49):
        npeaks = 0

        # keep track of pixels where we look for peaks
        if doplot_per_order:
            plt.plot(wave[iord, :], hc_sp[iord, :], color='k')
            plt.title('Per-order spectrum')
            plt.xlabel('wavelength (nm)')
            plt.ylabel('normalized flux')

        # to keep the user waiting
        print('processing order # ', iord, '/', 49)

        ord_prev = -1
        # scanning through each order, 1/3rd of w at a time

        hc_sp_order = hc_sp[iord, :]
        for indmax in range(w * 2, 4088 - w * 2 - 1, w // 3):
            xpix = np.asarray(range(indmax - w, indmax + w))

            segment = np.array(hc_sp_order[indmax - w:indmax + w])
            rms = np.nanmedian(np.abs(segment[1:] - segment[:-1]))
            peak = (np.max(segment) - np.nanmedian(segment))

            # peak needs to be well-behaved
            keep = True
            keep &= (rms != 0)  # rms not zero
            keep &= (peak != 0)  # peak not a zero
            keep &= (
                    peak / rms > sigma_peak)  # peak at least a few sigma
            # form RMS

            # position of peak within segement. It needs to be close enough to
            # the center of the segment
            # if it is at the edge, we'll catch it in the following iteration
            #
            # we keep (or not) the peak
            imax = np.argmax(segment) - w
            #
            keep &= (np.abs(
                imax) < w // 3)  # close enough to the center of the segment

            # we have a good peak worth fitting a gaussian
            if keep:
                # fit a gaussian with a slope
                popt_left, g2 = gaussfit(xpix, segment, 5)

                # residual of the fit normalized by peak value
                # similar to an 1/SNR value
                gauss_rms_dev0 = np.std(segment - g2) / popt_left[0]

                # all values that will be added (if keep_peak=True) to the
                # vector of all line
                # parameters
                zp0 = popt_left[3]
                slope0 = popt_left[4]
                ew0 = popt_left[2]
                xgau0 = popt_left[1]
                peak0 = popt_left[0]

                # will we add the peak to our master list of peaks...
                # test against some sanity checks
                keep_peak = True
                keep_peak &= gauss_rms_dev0 > gauss_rms_dev_min
                keep_peak &= gauss_rms_dev0 < gauss_rms_dev_max
                keep_peak &= ew0 > ew_min
                keep_peak &= ew0 < ew_max

                keep_peak &= (np.abs(
                    xgau0 - xprev) > 1)  # must be >1 pix from previous peak

                # if all is fine, we keep the value of the fit
                if keep_peak:
                    npeaks += 1
                    # print(xgau0 - xprev)
                    xprev = xgau0
                    zp_ini = np.append(zp_ini, zp0)
                    slope_ini = np.append(slope_ini, slope0)
                    ew_ini = np.append(ew_ini, ew0)
                    xgau_ini = np.append(xgau_ini, xgau0)
                    peak_ini = np.append(peak_ini, peak0)
                    ord_ini = np.append(ord_ini, iord)
                    gauss_rms_dev_ini = np.append(gauss_rms_dev_ini,
                                                  gauss_rms_dev0)
                    # xpix_ini = np.append(xpix_ini, xpix)
                    # g2_ini = np.append(g2_ini, g2)

                    if doplot_per_order:
                        plt.plot(wave[iord, xpix], g2)
        if doplot_per_order:
            plt.show()
        print('npeaks = ', npeaks)
    # create a dictonnary with all the peak infos. will be saved as an
    # ASCII file
    catalog_lines = dict()
    catalog_lines['ord'] = ord_ini
    catalog_lines['xgau'] = xgau_ini
    catalog_lines['gauss_rms_dev'] = gauss_rms_dev_ini
    catalog_lines['ew'] = ew_ini
    catalog_lines['zp'] = zp_ini
    catalog_lines['slope'] = slope_ini
    catalog_lines['peak'] = peak_ini
    ascii.write(catalog_lines, catalog_name)

# read the list of fitted lines
catalog_lines = ascii.read(catalog_name)

# reading the UNe catalog
catalogue_UNe = (ascii.read(file_catalog_urne, format='basic', data_start=0))
# wave_UNe=catalogue_UNe['wavelength']
# strength_UNe=catalogue_UNe['strength']
wave_UNe = catalogue_UNe[catalogue_UNe.colnames[0]]
strength_UNe = catalogue_UNe[catalogue_UNe.colnames[1]]

for sol_iteration in range(3):
    # algorithm :
    #
    # within each order, we loop through all bright lines and pick 3 lines
    # These 3 lines are assumed to be good, we fit a second-order xpix vs
    # wavelength polynomial and test it against all other fitted lines along
    # the order
    # we keep track of the best fit for the order, i.e., the fit that
    # provides a solution with the largest number of lines within +-500 m/s
    # We then assume that the fit is fine, we keep the lines that match the
    # "best fit"
    # and we move to the next order
    # Once we have "valid" lines for most/all orders, we attempt to fit a 5th
    # order polynomial
    # of the xpix vs lambda for all orders. The coefficient of the fit must be
    # continuous from
    # one order to the next

    # we perform the fit twice, once to get a coarse solution, once to refine
    # as we will trim some variables, we define them on each loop
    # not 100% elegant, but who cares, it takes 5µs ...
    #
    xgau = catalog_lines['xgau']
    order_ = catalog_lines['ord']
    gauss_rms_dev = catalog_lines['gauss_rms_dev']
    ew = catalog_lines['ew']
    peak = catalog_lines['peak']

    # find the brightest lines for each order
    # only those lines will be used to derive the first
    # estimates of the per-order fit
    brightest_lines = np.zeros(len(xgau), dtype=bool)
    for iord in set(order_):
        g = (order_ == iord)
        peak2 = np.array(peak[g])
        peak2.sort()
        good = (order_ == iord)
        nmax = nmax_bright  # we may have fewer lines within the order than
        # the nmax_bright variable
        if np.nansum(g) < nmax_bright:
            nmax = np.nansum(g) - 1
        good &= peak > (peak2[::-1])[nmax]
        brightest_lines[good] = True

    wave_sol = np.zeros_like(xgau)
    for i in range(len(xgau)):
        wave_sol[i] = np.polyval(
            (poly_wave_sol[np.array(order_[i], dtype=int), :])[::-1], xgau[i])

    # width_box = ([120000,5000,5000,1000,1000,1000])[sol_iteration]

    # keeping track of the velocity offset between predicted and observed
    # line centers
    dv = np.zeros(len(wave_sol)) + np.nan

    # wavelength given in the catalog for the matched line
    wave_catalog = np.zeros(len(wave_sol))
    i = 0
    for wave0 in wave_sol:
        # find closest catalog line to the line considered
        id_match = np.argmin(np.abs(wave_UNe - wave0))
        dd = (wave_UNe[id_match] / wave0 - 1) * 299792458.0
        if np.abs(dd) < 60000:
            wave_catalog[i] = wave_UNe[id_match]
            dv[i] = dd
        i += 1

    # loop through all orders and find the best trio of lines
    for iord in set(order_):
        g_all = (np.where((order_ == iord) & (np.isfinite(wave_catalog))))[0]

        nanmask = (np.isfinite(wave_catalog))
        g = (np.where((order_ == iord) & nanmask & brightest_lines))[0]

        bestn = 0
        best_fit = 0

        for i in range(len(g) - 2):  # first line of the trio
            for j in range(i + 1, len(g) - 1):  # second line of the trio
                for k in range(j + 1, len(g)):  # third line of the trio
                    index = [g[i], g[j], g[k]]
                    xx = xgau[index]
                    yy = wave_catalog[index]
                    fit = nanpolyfit(xx, yy, 2)  # fit the lines and take it as a
                    # best-guess solution
                    dd = (wave_catalog[g_all] / np.polyval(fit, np.array(
                        xgau[g_all])) - 1) * 299792.458  # error

                    nkeep = np.nansum(np.abs(dd) < cut_fit_threshold)
                    if nkeep > bestn:  # the number of good lines is the
                        # largest seen to date
                        bestn = nkeep
                        best_fit = fit

        print('order = ', iord, ' valid/total lines : ',
              bestn, ' / ', len(g_all))

        g = (np.where(order_ == iord))[0]
        if bestn >= 10:
            dd = (wave_catalog[g] / np.polyval(best_fit, np.array(
                xgau[g])) - 1) * 299792.458
            dd = np.abs(dd)
            if np.nanmax(dd) > cut_fit_threshold:
                outliers = g[np.abs(dd) > cut_fit_threshold]
                wave_catalog[outliers] = np.nan
                dv[outliers] = np.nan
        else:
            wave_catalog[g] = np.nan
            dv[g] = np.nan

    if doplot_sanity:
        plt.plot(wave_catalog, dv, 'g.', label='all lines')
        plt.plot(wave_catalog[brightest_lines], dv[brightest_lines], 'r.',
                 label='brightest per order')
        plt.legend()
        plt.title('delta-v error for matched lines')
        plt.xlabel('wavelength (nm)')
        plt.ylabel('dv (km/s)')
        plt.show()

    # we keep only wave_catalog where is it finite

    g = np.isfinite(wave_catalog)

    wave_catalog = wave_catalog[g]
    xgau = xgau[g]
    order_ = order_[g]
    dv = dv[g]
    ew = ew[g]
    gauss_rms_dev = gauss_rms_dev[g]

    if np.nansum(g) < 200:
        print('Error: We have less than 200 good lines total')
        exit()

    # for ite in range(5):
    lin_model_slice = np.zeros([len(xgau), np.nansum(order_fit_continuity)])

    # we construct the unit vectors for our wavelength model
    ii = 0
    for expo_xpix in range(len(order_fit_continuity)):
        for expo_order in range(order_fit_continuity[expo_xpix]):
            part1 = order_ ** expo_order
            part2 = (xgau - 0) ** expo_xpix
            lin_model_slice[:, ii] = part1 * part2
            ii += 1

    recon0 = np.zeros_like(wave_catalog)

    amps0 = np.zeros(np.nansum(order_fit_continuity))

    # we loop 20 times for sigma clipping and numerical convergence
    # in most cases ~10 iterations would be fine, but this is really fast
    for ite in range(20):
        amps, recon = lin_mini(wave_catalog - recon0, lin_model_slice)
        amps0 += amps
        recon0 += recon

        for aa in range(len(amps0)):
            ampsx = np.nansum(
                (wave_catalog - recon0) * lin_model_slice[:, aa]) / np.nansum(
                lin_model_slice[:, aa] ** 2)
            amps0[aa] += ampsx
            recon0 += (ampsx * lin_model_slice[:, aa])

        dv = (wave_catalog / recon0 - 1) * 299792.458
        sig = np.std(dv)

        absdev = np.abs(dv / sig)
        if np.max(absdev) > 3.5:  # sigma-clipping at 3.5 sigma
            # if we have outliers to our wavelength solution, we remove them
            print('   sigma-clipping (>3.5) ---> max(sig) : ', np.max(absdev),
                  'sigma')
            g = absdev < 3.5
            recon0 = recon0[g]
            lin_model_slice = lin_model_slice[g, :]
            wave_catalog = wave_catalog[g]
            xgau = xgau[g]
            order_ = order_[g]
            dv = dv[g]
            ew = ew[g]
            gauss_rms_dev = gauss_rms_dev[g]

        print(ite, ' | rms=', sig, '(km/s) | sig=',
              sig * 1000 / np.sqrt(len(wave_catalog)), 'm/s | n=',
              len(wave_catalog))

    plt.subplot(2, 2, 1)

    for iord in range(49):
        g = (order_ == iord)
        plt.plot(wave_catalog[g], 2.99e5 * (wave_catalog / recon0 - 1)[g], '.')

        plt.xlabel('Wavelength (nm)')
        plt.ylabel('dv (km/s)')

    plt.subplot(2, 2, 2)
    for iord in range(49):
        g = (order_ == iord)
        plt.plot(1 / gauss_rms_dev[g], 2.99e5 * (wave_catalog / recon0 - 1)[g],
                 '.')
        plt.xlabel('Line SNR estimate')
        plt.ylabel('dv (km/s)')

    plt.subplot(2, 2, 3)
    for iord in range(49):
        g = (order_ == iord)
        plt.plot(xgau[g] % 1, 2.99e5 * (wave_catalog / recon0 - 1)[g], '.')
        plt.xlabel('modulo pixel position')
        plt.ylabel('dv (km/s)')

    plt.subplot(2, 2, 4)
    for iord in range(49):
        g = (order_ == iord)
        plt.plot(ew[g], 2.99e5 * (wave_catalog / recon0 - 1)[g], '.')
        plt.xlabel('e-width of the fitted line')
        plt.ylabel('dv (km/s)')

    plt.show()

    xpix = np.array(range(4088))
    wave_map2 = np.zeros([49, 4088])
    poly_wave_sol = np.zeros([49, 5])

    for iord in range(49):
        ii = 0
        for expo_xpix in range(len(order_fit_continuity)):
            for expo_order in range(order_fit_continuity[expo_xpix]):
                poly_wave_sol[iord, expo_xpix] += iord ** expo_order * amps0[ii]
                ii += 1
        wave_map2[iord, :] = np.polyval((poly_wave_sol[iord, :])[::-1], xpix)

# quality control
# noinspection PyUnboundLocalVariable,PyUnboundLocalVariable
if sig * 1000 / np.sqrt(len(wave_catalog)) > 8:
    print('Error')
    exit()

# wave_map2 (wave map) --> fits
# poly_wave_sol  --> header

# =============================================================================

resolution_map = np.zeros([5, 4])

i_plot = 0
# determining the LSF
bin_ord = 10
for iord in range(0, 49, bin_ord):
    for xpos in range(0, 4):
        plt.subplot(5, 4, i_plot + 1)
        # noinspection PyUnboundLocalVariable
        gg = (gauss_rms_dev < 0.05)
        # noinspection PyUnboundLocalVariable
        gg &= (order_ // 10 == iord // 10)
        # noinspection PyUnboundLocalVariable
        gg &= (xgau // 1022) == xpos
        gg &= np.isfinite(wave_catalog)

        xcens = xgau[gg]
        orders = order_[gg]
        wave_line = wave_catalog[gg]

        all_lines = np.zeros([np.nansum(gg), 2 * w + 1])
        all_dvs = np.zeros([np.nansum(gg), 2 * w + 1])

        base = np.zeros(2 * w + 1, dtype=bool)
        base[0:3] = True
        base[2 * w - 2:2 * w + 1] = True

        # noinspection PyTypeChecker
        for i in range(np.nansum(gg)):
            all_lines[i, :] = hc_ini[int(orders[i]),
                                     int(xcens[i] + .5) - w:
                                     int(xcens[i] + .5) + w + 1]
            all_lines[i, :] -= np.nanmedian(all_lines[i, base])
            all_lines[i, :] /= np.nansum(all_lines[i, :])
            # noinspection PyUnboundLocalVariable
            v = -299792.458 * (wave_map2[int(orders[i]),
                               int(xcens[i] + .5) - w:int(
                                   xcens[i] + .5) + w + 1] / wave_line[i] - 1)
            all_dvs[i, :] = v

        all_dvs = all_dvs.ravel()
        all_lines = all_lines.ravel()

        keep = np.ones(len(all_dvs), dtype=bool)

        maxdev = 999

        maxdev_threshold = 8
        n_it = 0
        while maxdev > maxdev_threshold:
            # noinspection PyTypeChecker
            popt_left, pcov = curve_fit(gauss_function, all_dvs[keep],
                                        all_lines[keep], p0=[.3, 0, 1, 0, 0])
            res = all_lines - gauss_function(all_dvs, popt_left[0],
                                             popt_left[1], popt_left[2],
                                             popt_left[3], popt_left[4])

            rms = res / np.nanmedian(np.abs(res))
            maxdev = np.max(np.abs(rms[keep]))
            keep[np.abs(rms) > maxdev_threshold] = False
            n_it += 1

        # noinspection PyUnboundLocalVariable
        resolution = popt_left[2] * 2.3548200450309493

        plt.plot(all_dvs[keep], all_lines[keep], 'g.')

        xx = (np.array(range(301)) - 150) / 10.
        gplot = gauss_function(xx, popt_left[0], popt_left[1], popt_left[2],
                               popt_left[3], popt_left[4])

        plt.plot(xx, gplot, 'k--')
        print('nlines : ', np.nansum(gg), 'iord=', iord, ' xpos=', xpos,
              ' resolution = ', resolution, ' km/s', 'R = ',
              299792.458 / resolution)
        plt.xlim([-8, 8])
        plt.ylim([-0.05, .7])
        plt.title(
            'orders : ' + str(iord) + '-' + str(iord + 9) + ' region=' + str(
                xpos))
        plt.xlabel('dv (km/s)')

        i_plot += 1

        resolution_map[iord // bin_ord, xpos] = 299792.458 / resolution
plt.show()

print('mean resolution : ', np.mean(resolution_map))
print('median resolution : ', np.nanmedian(resolution_map))
print('stddev resolution : ', np.std(resolution_map))

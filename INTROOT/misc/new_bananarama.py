# noinspection PyPep8
import numpy as np
import glob
from astropy.io import fits as pyfits
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline
import scipy.ndimage as ndimage
from scipy.stats.stats import pearsonr

from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouEXTOR
from SpirouDRS.spirouCore import spirouMath

import time

# =============================================================================
# Define variables
# =============================================================================

PLOT = True

# FP file for tilt/dx determination
slope_file = '/scratch/Projects/spirou_py3/data_h4rg/tmp/TEST1/' \
             '20180805/2295525a_pp.fits'

outname = (slope_file.split('_'))[0] + '_dxmap.fits'

hdr_wave = pyfits.getheader("/scratch/Projects/spirou_py3/data_h4rg/reduced/"
                            "TEST1/20180805/20180805_2295515f_pp_loco_AB.fits")
# width of the ABC fibres.
wpix = 55

__NAME__ = 'anything'
p = spirouStartup.Begin(recipe=__NAME__)
p = spirouStartup.LoadArguments(p)

n_ord = hdr_wave["LONBO"] // 2
n_coeff = len(hdr_wave['LOFW[0-9]*']) // (n_ord * 2)

ordfit = 5
poly_c = np.zeros([n_coeff, n_ord * 2])
LOCTR = hdr_wave['LOCTR*']
for order_ in range(0, n_ord * 2, 2):
    for coeff in range(ordfit):
        i = (order_ * n_coeff) + coeff
        poly_c[i % n_coeff, i // n_coeff] = hdr_wave["LOCTR" + str(i)]

poly_c = poly_c[:, poly_c[0, :] != 0]

datac = (pyfits.getdata(slope_file))
hdr = pyfits.getheader(slope_file)
p = spirouImage.GetSigdet(p, hdr, name='sigdet')
# get exposure time
p = spirouImage.GetExpTime(p, hdr, name='exptime')
# get gain
p = spirouImage.GetGain(p, hdr, name='gain')

data = spirouImage.ConvertToE(spirouImage.FlipImage(datac), p=p)
# convert NaN to zeros
data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
# resize image
bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
               ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'], getshape=False)
data1 = spirouImage.ResizeImage(data0, **bkwargs)

# dxmap that will contain the dx per pixel
# if the file does not exist, we fill the map
# with zeros
# TODO: Question: How do we handle this in the DRS?
if len(glob.glob(outname)) > 0:
    print(outname + ' exists... we use its values as a starting point')
    master_dxmap = pyfits.getdata(outname)
    master_dxmap[~np.isfinite(master_dxmap)] = 0
    # number of banana iterations, = 1 if file exists
    nbanana = 1
else:
    master_dxmap = np.zeros_like(data1)  # +np.nan
    # number of banana iterations, = 3 if file does not exists
    nbanana = 3

# iterating the correction, from coarser to finer
for ite_banana in range(nbanana):
    # we use the code that will be used by the extraction to ensure that slice
    # images are as straight as can be

    # if the map is not zeros, we use it as a starting point
    if np.sum(master_dxmap != 0) != 0:
        data2 = spirouEXTOR.DeBananafication(data1, master_dxmap)
        flag_start_slope = False
    else:
        data2 = np.array(data1)
        flag_start_slope = True

    sz = np.shape(data2)

    if flag_start_slope:
        # starting point for slope exploration
        range_slopes_deg = [-12.0, 0.0]
    else:
        # if this is not the first iteration, then we must be really close
        # to a slope of 0
        range_slopes_deg = [-1.0, 1.0]

    # expressed in pixels, not degrees
    range_slopes = np.tan(np.array(range_slopes_deg) / 180 * np.pi)

    # looping through orders
    start = time.time()
    for iord in range(0, n_ord):

        print()
        print('Nth order : ', iord + 1, '/', n_ord, ' || banana iteration : ',
              ite_banana + 1, '/', nbanana)

        # x pixel vecctor that is used with polynomials to
        # find the order center
        xpix = np.array(range(4088))
        # y order center
        ypix = np.polyval((poly_c[:, iord])[::-1], xpix)

        # defining a ribbon that will contain the straightened order
        ribbon = np.zeros([wpix, 4088])

        # spling the original image onto the ribbon
        for i in range(4088):
            bot = int(ypix[i] - wpix / 2 - 2)
            top = int(ypix[i] + wpix / 2 + 2)
            if bot > 0:
                spline = InterpolatedUnivariateSpline(np.arange(bot, top),
                                                      data2[bot:top, i], ext=1,
                                                      k=1)
                ribbon[:, i] = spline(ypix[i] + np.arange(wpix) - wpix / 2.)

        # normalizing ribbon stripes to their median abs dev
        for i in range(wpix):
            ribbon[i, :] /= np.nanmedian(np.abs(ribbon[i, :]))

        # range explored in slopes
        # TODO: Question: Where does the /8.0 come from?
        slopes = np.array(range(0, 9)) * (
                    range_slopes[1] - range_slopes[0]) / 8.0 + range_slopes[0]

        print('range slope exploration : ', range_slopes_deg[0], ' -> ',
              range_slopes_deg[1], ' deg')

        xpix = np.arange(4088)

        # the domain is sliced into a number of sections, then we find
        # the tilt that
        # maximizes the RV content
        nsections = 32
        xsection = 4088 * (np.arange(nsections) + 0.5) / nsections
        dxsection = np.zeros_like(xsection) + np.nan

        # rv content per slice and per slope
        rvcontent = np.zeros([len(slopes), nsections])

        islope = 0
        for slope in slopes:
            ribbon2 = np.array(ribbon)
            for i in range(wpix):
                ddx = (i - wpix / 2.) * slope
                spline = InterpolatedUnivariateSpline(xpix, ribbon[i, :], ext=1)
                ribbon2[i, :] = spline(xpix + ddx)
            profil = np.nanmedian(ribbon2, axis=0)

            for k in range(nsections):
                # sum of integral of derivatives == RV content. This should
                # be maximal
                # when the angle is right
                part1 = k * 4088 // nsections
                part2 = (k + 1) * 4088 // nsections
                part3 = np.gradient(profil[part1:part2])

                rvcontent[islope, k] = np.nansum(part3 ** 2)
            islope += 1

        #
        # we find the peak of RV content and fit a parabola to that peak
        for k in range(nsections):
            # we must have some RV content (i.e., !=0)
            if np.nanmax(rvcontent[:, k]) != 0:
                v = np.ones_like(slopes)
                v[0] = 0
                v[-1] = 0
                maxpix = np.nanargmax(rvcontent[:, k] * v)
                # max RV and fit on the neighbouring pixels
                fit = np.polyfit(slopes[maxpix - 1:maxpix + 2],
                                 rvcontent[maxpix - 1:maxpix + 2, k], 2)
                # if peak within range, then its fine
                if np.abs(-.5 * fit[1] / fit[0]) < 1:
                    dxsection[k] = -.5 * fit[1] / fit[0]
            #
            # we sigma-clip the dx[x] values relative to a linear fit
            keep = np.isfinite(dxsection)

        sigmax = 99
        while sigmax > 4:
            # noinspection PyUnboundLocalVariable
            fit = np.polyfit(xsection[keep], dxsection[keep], 2)
            res = (dxsection - np.polyval(fit, xsection))
            res -= np.nanmedian(res[keep])
            res /= np.nanmedian(np.abs(res[keep]))
            sigmax = np.nanmax(np.abs(res[keep]))
            keep &= (np.abs(
                res) < 4)  # TODO: Question: is this 4 the same as above?

        #
        # we fit a 2nd order polynomial to the slope vx position along order
        # noinspection PyUnboundLocalVariable
        fit = np.polyfit(xsection[keep], dxsection[keep], 2)
        print('slope at pixel 2044 : ',
              np.arctan(np.polyval(fit, 2044)) * 180 / np.pi, ' deg')
        slope = np.polyval(fit, np.arange(4088))

        #
        # some plots to show that the slope is well behaved
        if PLOT:
            plt.subplot(1, 2, 1)
            slope_deg = np.arctan(dxsection[keep]) * 180 / np.pi
            plt.plot(xsection[keep], slope_deg, 'go')
            plt.plot(np.arange(4088), np.arctan(slope) * 180 / np.pi)
            ylim = [np.nanmin(slope_deg) - .2, np.nanmax(slope_deg) + .2]
            plt.ylim(ylim)
            plt.xlabel('x pixel')
            plt.ylabel('slope (deg)')
        #
        # correct for the slope the ribbons and look for the slicer profile
        for i in range(wpix):
            ddx = (i - wpix / 2.) * np.polyval(fit, xpix)
            spline = InterpolatedUnivariateSpline(xpix, ribbon[i, :], ext=1)
            # noinspection PyUnboundLocalVariable
            ribbon2[i, :] = spline(xpix + ddx)

        # median FP peak profile. We will cross-correlate each row of the
        # ribbon with this
        profil = np.nanmedian(ribbon2, axis=0)
        profil -= ndimage.filters.median_filter(profil, 51)

        dx = np.zeros(wpix) + np.nan
        ddx = np.arange(-3, 4)  # TODO: Question: why this size?
        # cross-correlation peaks of median profile VS position along ribbon
        cc = np.zeros([wpix, len(ddx)], dtype=float)
        for i in range(wpix):
            for j in range(len(ddx)):
                cc[i, j] = (pearsonr(ribbon2[i, :], np.roll(profil, ddx[j])))[0]
            # fit a gaussian to the CC peak
            g, gg = spirouMath.gauss_fit_nn(ddx, cc[i, :], 4)

            if np.nanmax(cc[i, :]) > 0.1:
                dx[i] = g[1]

        # remove any offset in dx, this would only shift the spectra
        dx -= np.nanmedian(dx)
        dypix = np.arange(len(dx))
        keep = np.abs(dx) < 1
        keep &= np.isfinite(dx)

        # if the first pixel is nan and the second is OK, then for
        # continuity, pad
        if keep[0] == 0 and keep[1] == 1:
            keep[0] = True
            dx[0] = dx[1]

        # same at the other end
        if keep[-1] == 0 and keep[-2] == 1:
            keep[-1] = True
            dx[-1] = dx[-2]

        # some more graphs
        if PLOT:
            plt.subplot(1, 2, 2)
            plt.imshow(cc, aspect=.2)
            plt.ylim([0, wpix - 1])
            plt.xlim([0, len(ddx) - 1])
            plt.plot(dx - np.min(ddx), dypix, 'ro')
            plt.plot(dx[keep] - np.min(ddx), dypix[keep], 'go')
            # plt.savefig('map_ord'+str(iord)+'.pdf')
            # plt.clf()
            plt.show()
            plt.close()

        # spline everything onto the master DX map
        spline = InterpolatedUnivariateSpline(dypix[keep], dx[keep], ext=0)

        # for all field positions along the order, we determine the dx+rotation
        # values and update the master DX map
        for i in range(4088):
            frac = (ypix[i] - np.fix(ypix[i]))
            dx0 = (np.array(range(wpix)) - wpix // 2. + (1 - frac)) * slope[i]
            ypix2 = int(ypix[i]) + np.array(range(-wpix // 2, wpix // 2))
            ddx = spline(np.array(range(wpix)) - frac)
            ddx[ddx == 0] = np.nan

            g = (ypix2 >= 0)
            if np.sum(g) != 0:
                master_dxmap[ypix2[g], i] += (ddx + dx0)[g]

    end = time.time()

    print('Time = {0}'.format(end - start))

pyfits.writeto(outname, master_dxmap, clobber=True)

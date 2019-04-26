# from lin_mini import *
# import os
import numpy as np
from astropy.io import fits as pyfits
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline
from SpirouDRS.spirouCore.spirouMath import gauss_fit_nn as gaussfit

import warnings

from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS.spirouEXTOR import DeBananafication
from SpirouDRS.spirouCore.spirouMath import nanpolyfit


# FP file for tilt/dx determination
slope_file = '2295305a_pp.fits'
hdr_wave = pyfits.getheader("2295305a_pp_e2dsff_AB.fits")
# width of the ABC fibres.
wpix = 53

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

data = spirouImage.ConvertToE(spirouImage.FlipImage(p, datac), p=p)
# convert NaN to zeros
data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
# resize image
bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
               ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'], getshape=False)
data1 = spirouImage.ResizeImage(p, data0, **bkwargs)

# dxmap that will contain the dx per pixel
master_dxmap = np.zeros_like(data1)  # +np.nan

# looping through orders
for iord in range(0, n_ord):

    # iterating the correction, from coarser to finer
    for ite_banana in range(3):

        # we use the code that will be used by the extraction to ensure
        # that slice
        # images are as straight as can be
        data2 = DeBananafication(data1, master_dxmap)

        # x pixel vecctor that is used with polynomials to
        # find the order center
        xpix = np.array(range(4088))
        # y order center
        ypix = np.polyval((poly_c[:, iord])[::-1], xpix)

        # top and bottom pixels that encompass all 3 fibers
        ytop = np.array(ypix + wpix / 2., dtype=int)
        ybot = np.array(ypix - wpix / 2., dtype=int)

        # we put NaNs on all pixels outside of the order box
        for i in range(len(xpix)):
            data2[0:ybot[i], xpix[i]] = np.nan
            data2[ytop[i]:, xpix[i]] = np.nan

        # we do a "dump" extraction by collapsing the order
        # along the y axis to find the highest peak
        profil = np.nanmedian(data2, axis=0)
        # no peaks too close to the edges
        profil[0:9] = 0
        profil[len(profil) - 10:] = 0

        # brightest peak, should be an FP line
        # will be used afterward for the thresholding of
        # peak finding. We only search for peaks that are more
        # than 0.3*maxpeak
        maxpeak = np.nanmax(profil)
        current_max = maxpeak

        dxmap = np.zeros([wpix, 4088]) + np.nan
        xpospeak = np.zeros([4088])
        allslopes = np.zeros_like(xpospeak) + np.nan
        all_slices = np.zeros([wpix, 6, 10])  # TODO: Why 6? Why 10?
        ii = 0

        # we iteratively find the peaks and set them to NaN afterward
        # for each FP peak, we loop through a range of slit angles
        # to determine its amplitude as a function of angle. We
        # assume that the angle that corresponds to the brightest
        # peak corresponds to the rotation of the slicer
        while current_max > (.3 * maxpeak):
            # find the peak
            id_ = np.nanargmax(profil)
            current_max = profil[id_]
            xpospeak[ii] = id_

            # a condition to avoid running off the edge of the image
            if ybot[id_] > 1:
                # box centered on the peak. This box will be "sheared"
                # until the y-collapsed profile is maximal
                box = data2[ybot[id_]:ytop[id_], xpix[id_] - 9:xpix[id_] + 9]

                # if this is the first iteration, then we loop
                # though a larger set of angles
                if ite_banana == 0:
                    slopes = np.array(range(-11, 5)) / 30.

                    if ii > 20:
                        # we have >20 measurements... lets just
                        # focus on angle values close to the median
                        med = np.nanmedian(allslopes)
                        rms = np.nanmedian(np.abs(allslopes - med))

                        slopes = np.array(range(-2, 3)) * rms + med
                else:
                    # if not, we just look for a small update to the angle
                    slopes = np.array(range(-1, 2)) / 30.

                # max peak value of the collapsed profil
                # as a function of angle
                medmax = np.zeros_like(slopes)
                wbox = (np.shape(box))[1]

                islope = 0

                # xy=np.array(range((np.shape(box))[0]*(np.shape(box))[1])).reshape(np.shape(box))
                # yy = (xy//(np.shape(box))[1]).ravel()
                # xx = (xy % (np.shape(box))[1]).ravel()

                # dxx = (yy-np.mean(yy)).ravel()

                box1 = np.array(box)
                for i in range(wpix):
                    # we take one slice of the box and normalize it
                    tmp = np.array(box[i, :])
                    tmp -= np.nanmedian(tmp)
                    tmp /= np.nansum(tmp ** 2)
                    box1[i, :] = tmp

                # box1=box1.ravel()

                sz = np.shape(box)
                box2 = np.zeros([len(slopes), sz[1], sz[0]])

                xx = np.arange((np.shape(box))[1])
                for i in range(wpix):
                    spline = InterpolatedUnivariateSpline(xx, box1[i, :], ext=1,
                                                          k=1)

                    for islope, slope in enumerate(slopes):
                        dx = (np.arange(wpix) - wpix // 2.) * slope
                        # applying a y-dependent shift in x
                        box2[islope, :, i] = spline(xx + dx[i])

                for islope, slope in enumerate(slopes):
                    medmax[islope] = np.nanmax(
                        np.nanmedian(box2[islope, :, :], axis=1))

                # perform a collapse along the y axis and take the peak value
                # of this profile
                # medmax[islope]=np.nanmax(np.nanmedian(box2,axis=0))

                # as we fit a second-order polynomial to the peak pixel,
                # we can't
                # have the peak value at the either end of the vector.
                v = np.ones_like(medmax)
                v[0] = 0
                v[-1] = 0
                pixmax = np.argmax(medmax)  # *v)

                if pixmax == 0:
                    pixmax += 1

                # we fit a parabolla to the max pixel and its 2 neighbours
                with warnings.catch_warnings(record=True) as _:
                    fit = nanpolyfit(slopes[pixmax - 1:pixmax + 2],
                                     medmax[pixmax - 1:pixmax + 2], 2)

                # the deriv=0 point of the parabola is taken to be the position
                # of the peak. This is the "best" estimate for the slope
                allslopes[ii] = -.5 * fit[1] / fit[0]

                # some output for the overeager
                if (ii % 10) == 0:
                    print('p ratio: ', current_max / maxpeak, ii, allslopes[ii],
                          ' iord = ', iord)

                # for the first 300 peaks, we keep track of the box shape
                # at the "best" angle
                if ii < 300:
                    box2 = np.zeros_like(box)
                    dx = (np.array(range(wpix)) - wpix // 2.) * allslopes[ii]

                    xx = np.array(range((np.shape(box))[1]))
                    for i in range(wpix):
                        tmp = np.array(box[i, :])
                        tmp -= np.nanmedian(tmp)
                        tmp /= np.nansum(tmp ** 2)
                        spline = InterpolatedUnivariateSpline(xx, tmp, ext=1)
                        tmp = spline(xx + dx[i])
                        # tmp=np.array(box[i,:])
                        # tmp=bilinearshift(tmp,-dx[i])
                        box2[i, :] = tmp

                    v = np.zeros(wbox)
                    v[5:wbox - 5] = 1  # TODO: Why +/- 5?
                    maxpix = np.argmax(np.nanmedian(box2, axis=0) * v)
                    if maxpix > 5:  # TODO: Why 5?
                        part1, part2 = maxpix - 3, maxpix + 3
                        all_slices[:, :, ii % 10] += box2[:, part1:part2]
                ii += 1

            # we NaN the peak so that the code can move to the
            # next peak
            profil[xpix[id_] - 2:xpix[id_] + 2] = np.nan  # TODO: Why +/- 2?

        # keep all valid slopes and peak positions
        g = np.isfinite(allslopes)
        # no slope can be a >10 sigma outlier
        g &= (np.abs(allslopes - np.nanmedian(allslopes)) < 10 * np.nanmedian(
            np.abs(allslopes - np.nanmedian(allslopes))))
        xpospeak = xpospeak[g]
        allslopes = allslopes[g]

        # TODO: Move to outside ------------------------->
        # plot the slope vs peak position
        plt.plot(xpospeak, allslopes, 'go')

        # we fit a 2nd order polynomial to pos vs slope
        slope = np.polyval(nanpolyfit(xpospeak, allslopes, 2),
                           np.array(range(4088)))

        plt.plot(slope, 'k--')
        plt.title('slope stdev' + str(np.std(slope)))
        # plt.show()

        plt.savefig('slope_ord' + str(iord) + '.pdf')
        plt.clf()
        # TODO: Move to outside <-------------------------
        # median trace of the brightest 300 peaks after
        # de-rotation
        bigtrace = np.nanmedian(all_slices, axis=2)

        # dx profile
        dx = np.zeros(wpix)
        ew = np.zeros(wpix)
        for i in range(wpix):
            bigtrace[i, :] -= np.nanmin(bigtrace[i, :])
            bigtrace[i, :] /= np.nansum(bigtrace[i, :])

            g, a = gaussfit(np.arange(6), bigtrace[i, :], 4)
            ew[i] = g[2]  # gaussian width, must be reasonable
            dx[i] = g[1]  # center of the gaussian

        dypix = np.array(range(wpix))

        # some sanity checks
        keep = (np.isfinite(dx)) & (ew < 1.5) & (ew > .5)
        # TODO: Move plot outside
        plt.imshow(bigtrace, aspect=0.2)
        plt.title(
            'robust sig dx=' + str(np.nanmedian(np.abs(dx - np.nanmedian(dx)))))

        # only keep dx values that are not too large
        keep &= (np.abs(dx - np.nanmedian(dx)) < 1.5)
        # TODO: Move plot outside
        plt.plot(dx[keep], dypix[keep], 'ro')

        # plt.show()
        plt.savefig('map_ord' + str(iord) + '.pdf')

        plt.clf()
        # TODO: GOT TO HERE
        # the zero point of dx does not have a physical sense. We can subtract
        # it. Adding it would just shift the spectrum by a constant offset
        dx -= np.nanmedian(dx)

        spline = InterpolatedUnivariateSpline(dypix[keep], dx[keep], ext=1)

        # for all field positions along the order, we determine the dx+rotation
        # values and update the master DX map
        for i in range(4088):
            frac = (ypix[i] - np.fix(ypix[i]))
            dx0 = (np.array(range(wpix)) - wpix // 2. + (1 - frac)) * slope[i]
            ypix2 = int(ypix[i]) + np.array(range(-wpix // 2, wpix // 2))
            ddx = spline(np.array(range(wpix)) - frac)
            ddx[ddx == 0] = np.nan

            g = (ypix2 >= 0)
            if np.nansum(g) != 0:
                master_dxmap[ypix2[g], i] += (ddx + dx0)[g]

pyfits.writeto((slope_file.split('_'))[0] + '_dxmap.fits', master_dxmap,
               clobber=True)

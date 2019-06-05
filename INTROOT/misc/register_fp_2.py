#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-05 at 13:56

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def function1():
    return 0


# =============================================================================
# Start of code
# =============================================================================
# Main code here
import numpy as np
import glob
from astropy.io import fits
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy import ndimage
from lin_mini import lin_mini
import warnings


def lin_transform(image, lin_transform_vect):

    image = np.array(image)
    # transforming an image with the 6 linear transform terms
    # Be careful with NaN values, there should be none
    dx = lin_transform_vect[0]
    dy = lin_transform_vect[1]
    A = lin_transform_vect[2]
    B = lin_transform_vect[3]
    C = lin_transform_vect[4]
    D = lin_transform_vect[5]

    sz = image.shape
    yy, xx = np.indices([sz[0], sz[1]], dtype=float)  # /10.

    xx2 = dx + xx * A + yy * B
    yy2 = dy + xx * C + yy * D

    valid_mask = np.isfinite(image)
    mask = valid_mask.astype(float)

    image[~valid_mask] = 0

    # we need to properly propagate NaN in the interpolation.
    out_image = ndimage.map_coordinates(image, [yy2, xx2],
                                        order=2, cval=np.nan, output=float,
                                        mode='constant')
    out_weight = ndimage.map_coordinates(mask, [yy2, xx2],
                                        order=2, cval=0, output=float,
                                        mode='constant')
    out_image = out_image/out_weight
    out_image[out_weight<0.5] = np.nan

    return out_image


def get_lin_transform_params(im1_ini, im2_ini, niterations=5, doplot=False):
    # just to be sure that there's no problem with NaNs later
    #im1_ini[~np.isfinite(im1_ini)] = 0
    #im2_ini[~np.isfinite(im2_ini)] = 0

    im1 = im1_ini

    # linear transform vector
    # with dx0,dy0,A,B,C,D
    # we start assuming that there is no shift in x or y
    # and that the image is not sheared or rotated
    lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])

    # construct a cube with 8 slices that contain the 8 neighbours
    # of any pixel. This is used to find pixels brighter than their neighbours
    sz = np.shape(im1)
    box1 = np.zeros([8, sz[0], sz[1]])
    i = 0
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if (dx == 0) & (dy == 0):
                continue
            box1[i, :, :] = np.roll(np.roll(im1, dx, axis=0), dy, axis=1)
            i += 1
    # maximum value of neighbouring pixels
    maxi1 = np.max(box1, axis=0)

    # find pixels brighter than neighbours and brighter than 80th percentile
    # of image. These are the peaks of FP lines
    # we also impose that the pixel be within 1.5x of its neighbours
    # to filter-out noise excursions
    with warnings.catch_warnings(record=True) as _:
        mask1 = ((im1 - maxi1) > 0) & (im1 > np.nanpercentile(im1, 80)) & (
                    im1 / maxi1 < 1.5)

    for ite_transform in range(niterations):

        if ite_transform == 0:
            # on first iteration, its just the identify transform
            im2 = np.array(im2_ini)
        else:
            # now we have some real transforms
            im2 = lin_tranform(im2_ini, lin_transform_vect)

        box2 = np.zeros([8, sz[0], sz[1]])
        i = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (dx == 0) & (dy == 0):
                    continue
                box2[i, :, :] = np.roll(np.roll(im2, dx, axis=0), dy, axis=1)
                # print(box[i,1000:1005,1000:1005])
                # print(dx,dy,i)
                i += 1

        maxi2 = np.max(box2, axis=0)
        with warnings.catch_warnings(record=True) as _:
            # same conditions as for the im1
            mask2 = ((im2 - maxi2) > 0) & (im2 > np.nanpercentile(im2, 80)) & (
                        im2 / maxi2 < 1.5)

        #
        if ite_transform == 0:
            # we search in +- wdd to find the maximum number of matching
            # bright peaks. We first explore a big +-11 pixel range, but
            # afterward we can scan a much smaller region
            wdd = 11
        else:
            wdd = 2

        # scaning in dx/dy range
        dd = np.arange(-wdd, wdd + 1)
        map_dxdy = np.zeros([len(dd), len(dd)])

        # peaks cannot be at the edges of the image
        mask1[0:wdd + 1, :] = False
        mask1[:, 0:wdd + 1] = False
        mask1[-wdd - 1:, :] = False
        mask1[:, -wdd - 1:] = False

        ypeak1, xpeak1 = np.where(mask1)

        for iy in tqdm(range(len(dd)), leave=False):
            for ix in range(len(dd)):
                map_dxdy[iy, ix] = np.mean(
                    mask2[(ypeak1 + dd[iy]), (xpeak1 + dd[ix])])

        dy0 = -dd[np.argmax(map_dxdy) // len(dd)]
        dx0 = -dd[np.argmax(map_dxdy) % len(dd)]

        # shift by integer if dx0 or dy0 is not 0
        # this is used later to ensures that the pixels found as
        # peaks in one image are also peaks in the other.
        mask2b = np.roll(np.roll(mask2, dy0, axis=0), dx0, axis=1)

        # position of peaks in 2nd image
        xpeak2 = np.array(xpeak1 - dx0, dtype=int)
        ypeak2 = np.array(ypeak1 - dy0, dtype=int)

        # peaks in im1 must be peaks in image2 when accounting for the
        # integer offset
        keep = mask2b[ypeak1, xpeak1]
        xpeak1 = xpeak1[keep]
        ypeak1 = ypeak1[keep]
        xpeak2 = xpeak2[keep]
        ypeak2 = ypeak2[keep]

        # black magic arithmetic for replace a 2nd order polynomial by
        # some arithmedic directly on pixel values to find
        # the maxima in x and y for each peak

        # vectors to contain peak pixels and its neighbours in x or y for
        # im1 and im2
        vvy1 = np.zeros([3, len(ypeak1)])
        vvx1 = np.zeros([3, len(ypeak1)])
        vvy2 = np.zeros([3, len(ypeak1)])
        vvx2 = np.zeros([3, len(ypeak1)])

        # accurate position of all peaks
        dx1 = np.zeros(len(xpeak1))
        dy1 = np.zeros(len(xpeak1))
        dx2 = np.zeros(len(xpeak1))
        dy2 = np.zeros(len(xpeak1))

        # pad values of neighbours in vv[xy][12]
        for i in range(-1, 2):
            vvy1[i + 1, :] = im1[ypeak1 + i, xpeak1]
            vvx1[i + 1, :] = im1[ypeak1, xpeak1 + i]
            vvy2[i + 1, :] = im2[ypeak2 + i, xpeak2]
            vvx2[i + 1, :] = im2[ypeak2, xpeak2 + i]

        # subtract peak pixel value
        vvx1[0, :] -= vvx1[1, :]
        vvx1[2, :] -= vvx1[1, :]
        vvx1[1, :] -= vvx1[1, :]

        # find the slope of the linear fix
        mx1 = (vvx1[2, :] - vvx1[0, :]) / 2

        # find the 2nd order of the polynomial
        ax1 = vvx1[2, :] - mx1

        # all the same in y direction for im1
        vvy1[0, :] -= vvy1[1, :]
        vvy1[2, :] -= vvy1[1, :]
        vvy1[1, :] -= vvy1[1, :]

        my1 = (vvy1[2, :] - vvy1[0, :]) / 2
        ay1 = vvy1[2, :] - my1

        # same arithmetics for im2
        vvx2[0, :] -= vvx2[1, :]
        vvx2[2, :] -= vvx2[1, :]
        vvx2[1, :] -= vvx2[1, :]

        # finding x slopes and 2nd order terms in im2
        mx2 = (vvx2[2, :] - vvx2[0, :]) / 2
        ax2 = vvx2[2, :] - mx2

        vvy2[0, :] -= vvy2[1, :]
        vvy2[2, :] -= vvy2[1, :]
        vvy2[1, :] -= vvy2[1, :]

        # finding y slopes and 2nd order terms in im2
        my2 = (vvy2[2, :] - vvy2[0, :]) / 2
        ay2 = vvy2[2, :] - my2

        # peaks position is point of zero derivative. We add the integer
        # pixel value of [xy]peak[12]
        x1 = -.5 * mx1 / ax1 + xpeak1
        y1 = -.5 * my1 / ay1 + ypeak1

        x2 = -.5 * mx2 / ax2 + xpeak2
        y2 = -.5 * my2 / ay2 + ypeak2

        # we loop on the linear model converting x1 y1 to x2 y2
        nbad = 1
        while nbad != 0:
            v = np.zeros([3, len(x1)])
            v[0, :] = 1
            v[1, :] = x1  # -2044
            v[2, :] = y1  # -2044

            ampsx, xrecon = lin_mini(x1 - x2, v)
            ampsy, yrecon = lin_mini(y1 - y2, v)
            # express distance of all residual error in x1-y1 and y1-y2
            # in absolute deviation
            xrms = ((x1 - x2) - xrecon) ** 2 / np.nanmedian(
                np.abs((x1 - x2) - xrecon))
            yrms = ((y1 - y2) - yrecon) ** 2 / np.nanmedian(
                np.abs((y1 - y2) - yrecon))

            # How many 'sigma' for the core of distribution
            nsig = np.sqrt(xrms ** 2 + yrms ** 2)

            bad = nsig > 1.5
            # remove outliers and start again if there was one
            nbad = np.sum(bad)
            good = ~bad
            x1 = x1[good]
            y1 = y1[good]
            x2 = x2[good]
            y2 = y2[good]

        # we have our linear transform terms!
        dx0 = ampsx[0]
        A = ampsx[1]
        B = ampsx[2]
        dy0 = ampsy[0]
        C = ampsy[1]
        D = ampsy[2]

        d_transform = [dx0, dy0, A, B, C, D]

        # some printouts
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('     iteration : ', ite_transform + 1, ' / ', niterations)
        # print(ite_transform)

        print('dx = ', lin_transform_vect[0])
        print('dy = ', lin_transform_vect[1])

        # shift over the entire width of a full frame
        print('(A-1)*4088 = ', (lin_transform_vect[2] - 1) * 4088)
        print('    B*4088 = ', (lin_transform_vect[3]) * 4088)
        print('    C*4088 = ', (lin_transform_vect[4]) * 4088)
        print('(D-1)*4088 = ', (lin_transform_vect[5] - 1) * 4088)
        print()
        print('rmsx = ', np.nanmedian(np.abs(x1 - x2)))
        print('rmsy = ', np.nanmedian(np.abs(y1 - y2)))

        # print(d_transform)

        lin_transform_vect -= d_transform

        if (doplot == True) and (ite_transform + 1) == (niterations):
            plt.subplot(2, 2, 1)
            plt.hist2d(x1, (x1 - x2), bins=50)
            plt.xlabel('x1')
            plt.ylabel('x1-x2')
            plt.subplot(2, 2, 2)
            plt.hist2d(y1, (x1 - x2), bins=50)
            plt.xlabel('y1')
            plt.ylabel('x1-x2')
            plt.subplot(2, 2, 3)
            plt.hist2d(x1, (y1 - y2), bins=50)
            plt.xlabel('x1')
            plt.ylabel('y1-y2')
            plt.subplot(2, 2, 4)
            plt.hist2d(y1, (y1 - y2), bins=50)
            plt.xlabel('y1')
            plt.ylabel('y1-y2')
            plt.show()

    return lin_transform_vect


def trim_image(image):
    # subimage and normalize
    # 4-4092 in x
    # 250-3350 in y
    # flip in x
    # flip in y
    image = image[::-1, ::-1]
    image = image[250:3350, 4:4092]

    return image


def get_master_fp(ref_fp_file, all_fps, N_dt_bin=2, doplot=False):
    # ref_fp_file -> reference file against which all other fps are compared
    # all_fps -> all fps to be combined together to produce the master fp
    # N_dt_bin -> delay in hours for two FP files to be considered as coming
    #             from the same batch

    # ****** TO BE REMOVED ************************************
    ref_fp_file = '2294794a_pp.fits'
    im1 = fits.getdata(ref_fp_file)
    im1 = trim_image(im1)  # TO BE REMOVED

    all_fps = np.array(glob.glob('*a_pp.fits'))
    # ****** TO BE REMOVED ************************************

    # replace all NaNs by zeros
    im1[np.isfinite(im1) == False] = 0

    # we check that only files with FP_FP DPRTYPE are present
    dprtype = np.zeros(len(all_fps), dtype='<U20')
    for i in tqdm(np.arange(len(all_fps)), leave=False):
        hdr = fits.getheader(all_fps[i])
        dprtype[i] = np.array(hdr['DPRTYPE'])

    # only FP_FP should be used here
    all_fps = all_fps[dprtype == 'FP_FP']

    # keep track of timestamps and median-combined the ones
    # that were taken close in time
    fp_time = np.zeros(len(all_fps))
    # looping through the file headers
    for i in tqdm(np.arange(len(all_fps)), leave=False):
        hdr = fits.getheader(all_fps[i])
        fp_time[i] = float(hdr['MJDATE'])

    # ID of matched multiplets of files
    matched_id = np.zeros_like(fp_time, dtype=int)

    # loop until all files are matched with all other files taken within
    # 2 hours
    ii = 1
    while np.min(matched_id) == False:
        gg = (np.where(matched_id == 0))[0]
        g = np.min(gg)
        # same batch if they are within N hours
        gm = np.abs(fp_time[g] - fp_time) < N_dt_bin / 24.0
        matched_id[gm] = ii
        ii += 1

    # find all matched batches
    u_ids = set(matched_id)

    # how many bins of median darks. The 'long' option has 1 bin per
    # epoch of +-N_dt_bin hours
    i = 0

    # will hold the cube that keeps the median of each of the FP sequences
    all_fps_cube = []
    # looping through epochs
    for u_id in u_ids:
        keep = (matched_id == u_id)

        # only combine if 3 or more images were taken
        if np.sum(keep) >= 3:

            # find all files at that epoch
            fp_id = all_fps[keep]

            # read all files within an epoch into a cube
            cube = []
            for fic in fp_id:
                print(fic)
                tmp = fits.getdata(fic)  # -dark

                tmp = trim_image(tmp)  # TO BE REMOVED

                tmp /= np.nanpercentile(tmp, 90)
                cube.append(tmp)

            # median dark for that epoch
            im2 = np.nanmedian(cube, axis=0)

            transforms = get_lin_transform_params(im1, im2, niterations=5,
                                                  doplot=True)
            im2 = lin_tranform(im2, transforms)

            all_fps_cube.append(im2)

    all_fps_cube = np.array(all_fps_cube)
    # just to check, we save the cube before performing a big meisan
    # along dimension 0
    fits.writeto('super_cube.fits', all_fps_cube, overwrite=True)
    fits.writeto('super_mean.fits', np.sum(all_fps_cube, axis=0),
                 overwrite=True)

# =============================================================================
# End of code
# =============================================================================

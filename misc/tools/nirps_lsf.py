#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2020-01-21 at 10:54

@author: eartigau
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from astropy.table import Table

# The f/ratio of the instrument is ~8
# We know that the Strehl is always very high, median around 0.9, no lower than
# 0.8 anywhere within the domain, therefore we can assume that the optics
# (not fiber shape geometric) diffraction FWHM is lambda*F/#, which

# would be the case for a perfect diffraction PSF.
fratio = 10.0
wavelength = 1.5  # expressed in µm

# we define a 10x10 oversampled pixel grid
# this corresponds to a 12pix x 12 pix map of the PSF
# setup parameters
diam_HR = 3.0  # diameter of HR fibre
prop_HE = [4.0, 10.0]  # two axes of the HE fiber

# computation box width in pixels
pixel_box_width = 20

# pixel oversampling
osamp = 5

# pixel size in micron
pix_size = 15.0

# diffraction image quality in pixel
imqual_fwhm = wavelength * fratio / pix_size
boxwidth = pixel_box_width * osamp

# gives pixel values centered on zero
ypix, xpix = (np.indices([boxwidth, boxwidth]) - boxwidth // 2) / osamp
rad = np.sqrt(xpix ** 2 + ypix ** 2)  # radial position in pixmap

for fib in ['HR', 'HE']:
    pixmap = np.zeros([boxwidth, boxwidth])

    # true pixel position along LSF
    pixel_pos = (np.arange(boxwidth) - boxwidth // 2) / osamp

    if fib == 'HR':
        # we set the purely geometric image of the fibre
        pixmap[rad < diam_HR / 2.0] = 1.0

    if fib == 'HE':
        # we set the rectangular fibre geometry
        cond1 = np.abs(ypix) < prop_HE[0] / 2
        cond2 = np.abs(xpix) < prop_HE[1] / 2
        pixmap[cond1 & cond2] = 1.0

    # we get the diffraction psf
    optics_psf = np.exp(-.5 * (rad / (imqual_fwhm / 2.354)) ** 2)

    # we convolve image by diffraction psf
    pixmap = signal.convolve2d(pixmap, optics_psf, mode='same')

    # we get the pixel convolution kernel
    # we assume its a 3x3 pixel box with 0.96 in the central pixel
    # and 0.01 in the four immediate neighborus. This is a good appoximation
    # for H4RG arrays
    pixkernel = np.zeros([osamp * 3, osamp * 3])
    pixkernel[osamp:osamp * 2, osamp:osamp * 2] = 0.96
    pixkernel[osamp:osamp * 2, 0:osamp] = 0.01
    pixkernel[osamp:osamp * 2, osamp * 2:osamp * 3] = 0.01
    pixkernel[0:osamp, osamp:osamp * 2] = 0.01
    pixkernel[osamp * 2:osamp * 3, osamp:osamp * 2] = 0.01

    # we convolve image by pixel
    pixmap = signal.convolve2d(pixmap, pixkernel, mode='same')

    # we normalize to an integral of 1
    pixmap /= np.sum(pixmap)

    # we sum in 1D and get the LSF
    lsf = np.sum(pixmap, axis=1)

    # we find the FWHM of the LSF
    lsf_max = lsf / np.max(lsf)  # normalized to max
    above_half = np.where(lsf_max > .5)

    cut1 = np.min(above_half)
    cut2 = np.max(above_half)

    pfit1 = np.polyfit(lsf_max[cut1:cut1 + 2], pixel_pos[cut1:cut1 + 2], 1)
    cut_before = np.polyval(pfit1, .5)
    pfit2 = np.polyfit(lsf_max[cut2:cut2 + 2], pixel_pos[cut2:cut2 + 2], 1)
    cut_after = np.polyval(pfit2, .5)

    print('Fiber mode : ' + fib)
    print('FWHM = {0:5.3f} pix'.format(cut_after - cut_before))

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=[16, 8])

    extent = [-pixel_box_width / 2, pixel_box_width / 2, -pixel_box_width / 2,
              pixel_box_width / 2]
    ax[0].imshow(pixmap, origin='lower', extent=extent)
    title = fib + ', 2D image oversampled 10x'
    ax[0].set(xlabel='pixel', ylabel='pixel', title=title)
    ax[1].plot(pixel_pos, lsf)
    ax[1].set(xlabel='pixel', ylabel='Normalized flux', title=fib + ', LSF')
    plt.show()

    # we write down the LSF as an ascii table
    tbl_lsf = Table()
    tbl_lsf['PIXEL'] = pixel_pos
    tbl_lsf['LSF'] = lsf
    tbl_lsf.write('lsf_' + fib + '_{0:5.3f}.csv'.format(wavelength),
                  overwrite=True)

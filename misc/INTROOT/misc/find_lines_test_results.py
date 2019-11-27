#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-07-05 at 14:34

@author: cook
"""
from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import os

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/home/ncook/Downloads/data_h4rg/reduced_backup/'

FOLDER1 = WORKSPACE + 'FIND_LINDS_TEST/FORTRAN'
FOLDER2 = WORKSPACE + 'FIND_LINDS_TEST/SCIPY'
FILENAME1 = '180529_2279845c_hc_pp_wave_AB.fits'
FILENAME2 = '180529_2279845e_hc_pp_wave_AB.fits'
# -----------------------------------------------------------------------------
# FIRST = 13
# LAST = 40

FIRST = 0
LAST = 50


# =============================================================================
# Define functions
# =============================================================================
def plot_wave(y1, y2):
    ydim, xdim = y1.shape

    plt.figure()
    for order in range(ydim):

        if not (13 <= order <= 40):
            continue

        plt.plot(y1[order], color='r')
        plt.text(-10, y1[order][0], s=order, color='r')

        plt.plot(y2[order], color='b')
        plt.text(-10, y2[order][0], s=order, color='b')

    plt.xlabel('Pixel number')
    plt.ylabel('Wavelength [nm]')


def plot_wave_residual(y1, y2):
    ydim, xdim = y1.shape

    jet = plt.get_cmap('jet')
    c_norm = colors.Normalize(vmin=0, vmax=ydim)
    scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=jet)

    plt.figure()
    for order in range(ydim):

        if not (FIRST <= order <= LAST):
            continue

        color_val = scalar_map.to_rgba(order)

        plt.plot(y1[order] - y2[order], label='Order = {0}'.format(order),
                 color=color_val)
        plt.text(-10, y1[order][0] - y2[order][0], s=order, color=color_val)

    plt.legend(loc=0, ncol=5)
    plt.xlabel('Pixel number')
    plt.ylabel('$\Delta$ Wavelength [nm]')


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get data in each folder
    data1 = fits.getdata(os.path.join(FOLDER1, FILENAME1))
    data2 = fits.getdata(os.path.join(FOLDER2, FILENAME2))

    # plot data
    plot_wave(data1, data2)
    plot_wave_residual(data1, data2)

    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================

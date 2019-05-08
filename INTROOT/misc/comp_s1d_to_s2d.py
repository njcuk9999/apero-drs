#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-08 at 14:23

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings
import os


# =============================================================================
# Define variables
# =============================================================================
workspace = '/scratch/Projects/spirou/data_dev/reduced/TEST1/20180805'
file1 = '2295545o_pp_e2ds_AB.fits'
file2 = '2295545o_pp_s1dv_AB.fits'
blazefile = '20180805_2295520f_pp_blaze_AB.fits'
wavefile = '20180805_2295680c_pp_wave_ea_AB.fits'
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
if __name__ == "__main__":
    # ----------------------------------------------------------------------


    data1 = fits.getdata(os.path.join(workspace, file1))
    data2 = Table.read(os.path.join(workspace, file2))
    wave = fits.getdata(os.path.join(workspace, wavefile))
    blaze = fits.getdata(os.path.join(workspace, blazefile))

    # blaze correct data1
    data3 = data1 / blaze

    fig, frame = plt.subplots(ncols=1, nrows=1)

    # plot the e2ds orders one by one
    for order_num in range(data1.shape[0]):

        if order_num % 2 == 0:
            colour = 'r'
        else:
            colour = 'b'

        frame.plot(wave[order_num], data3[order_num]/np.nanmedian(data3),
                   color=colour, linewidth=0.5)

        frame.plot(wave[order_num], blaze[order_num]/np.nanmax(blaze[order_num]),
                   color='orange')

    # plot the s1d
    frame.plot(data2['wavelength'], data2['flux']/np.nanmedian(data2['flux']),
               color='k', linewidth=0.5)


    # set labels
    frame.set(xlabel='wavelength', ylabel='normalised flux',
              ylim=[0.1, 3])

    plt.show()
    plt.close()


# =============================================================================
# End of code
# =============================================================================

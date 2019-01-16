#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-16 at 12:24

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings
import glob
import os

# =============================================================================
# Define variables
# =============================================================================

WORKSPACE = ''

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
    # get wave files
    files = glob.glob(WORKSPACE + '*/*wave*')

    # get data
    data = []
    for filename in files:
        data.append(fits.getdata(filename))

    combinations = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
    positions = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]]

    # get differences
    diff = []
    for combination in combinations:
        diff.append(data[combination[0]] - data[combination[1]])


    # plot
    plt.close()
    fig, frames = plt.subplots(ncols=3, nrows=2)

    for it in range(len(combinations)):
        # get this iterations parameters
        com = combinations[it]
        pos = positions[it]
        # get frame
        frame = frames[pos[0]][pos[1]]

        im = frame.imshow(diff[it], aspect='auto')
        targs = [os.path.basename(files[com[0]]),
                 os.path.basename(files[com[1]])]
        frame.set(xlabel='x pixel position', ylabel='order number')

        cb = plt.colorbar(im, ax=frame, orientation='vertical',
                          label='$\Delta \lambda$ [nm]')

        title = '{0}\n-\n{1}'.format(*targs)
        frame.set_title(title, size=10)

    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================

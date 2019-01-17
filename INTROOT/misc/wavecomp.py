#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2019-01-16 at 12:24

@author: cook
"""

import matplotlib.pyplot as plt
from astropy.io import fits
import glob
import os

# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = ''
# -----------------------------------------------------------------------------


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get wave files (assumes they are in sub folders)
    files = glob.glob(WORKSPACE + '*/*wave*')

    # get data (from files)
    data = []
    for filename in files:
        data.append(fits.getdata(filename))

    # choose which combinations to difference (from files)
    combinations = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
    # choose positions of differences on plot grid
    positions = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]]

    # get differences
    diff = []
    for combination in combinations:
        diff.append(data[combination[0]] - data[combination[1]])

    # setup plot
    plt.close()
    fig, frames = plt.subplots(ncols=3, nrows=2)

    # loop through combinations
    for it in range(len(combinations)):
        # get this iterations parameters
        com = combinations[it]
        pos = positions[it]
        # get frame
        frame = frames[pos[0]][pos[1]]
        # plot the image
        im = frame.imshow(diff[it], aspect='auto')
        targs = [os.path.basename(files[com[0]]),
                 os.path.basename(files[com[1]])]
        # add label
        frame.set(xlabel='x pixel position', ylabel='order number')
        # add colorbar
        cb = plt.colorbar(im, ax=frame, orientation='vertical',
                          label='$\Delta \lambda$ [nm]')
        # add title (separately due to font size change)
        title = '{0}\n-\n{1}'.format(*targs)
        frame.set_title(title, size=10)

    # show and close figure
    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================

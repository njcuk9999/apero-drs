#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-30 at 11:20

@author: cook
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from astropy.io import fits


# =============================================================================
# Define variables
# =============================================================================
PATH = '/spirou/cfht_nights/cfht/calibDB_2/'
CALIBDB = 'master_calib_SPIROU.txt'
# -----------------------------------------------------------------------------
REF_NUM = 10

STD_ORDER = [33, 34, 35, 36, 37]

CURRENT_DATA = []
CURRENT_FILE = []
CURRENT_CODE = []
ALL_FRAMES = []



# =============================================================================
# Define functions
# =============================================================================
def on_pick(event):
    # loop around axis
    for i, ax in enumerate(ALL_FRAMES):
        # For infomation, print which axes the click was in
        if ax == event.inaxes:
            print("Click is in frame {}".format(i+1))

            # plot
            fig1, frame1 = plt.subplots(ncols=1, nrows=1)
            # get title
            targs1 = [CURRENT_FILE[i], CURRENT_CODE[i]]
            title1 = 'Filename = {0} \n Code = {1}'.format(*targs1)
            ticks1 = np.linspace(-200, 200, 9)
            diffplot(frame1, CURRENT_DATA[i], title1, ticks=ticks1, labels=True)
            plt.tight_layout()
            plt.show()


def diffplot(frame, data, title, ticks=None, labels=False, colorbar=True):
    # plot each dv image
    im = frame.imshow(data, aspect='auto', vmin=-200, vmax=200,
                      interpolation='nearest', origin='lower')
    if ticks is None:
        ticks = [-200, -100, 0, 100, 200]
    # set title
    frame.set_title(title, fontsize='small')
    # add colour bar
    if colorbar:
        # make an axis for colorbar
        divider = make_axes_locatable(frame)
        cax = divider.append_axes("right", size='5%', pad=0.05)
        cbar = fig.colorbar(im, cax=cax, ax=frame, ticks=ticks)
        if labels:
            cbar.set_label('dv [m/s]')
    if labels:
        frame.set_xlabel('x-direction pixel number')
        frame.set_ylabel('order number')


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # read lines of calibDB
    f = open(os.path.join(PATH, CALIBDB))
    lines = f.readlines()
    f.close()
    # get AB wave sol files
    files = []
    for line in lines:
        if 'AB' in line and line.startswith('WAVE') and 'MASTER' not in line:
            files.append(line.split()[2])

    files = np.sort(files)
    # add data to the data cubes
    data_array, hdr_array = [], []
    for filename in files:
        data, header = fits.getdata(filename, header=True)
        data_array.append(data)
        hdr_array.append(header)
    # select ref data
    data_ref = data_array[REF_NUM]
    # set up plot
    nrows = int(np.ceil(np.sqrt(len(files))))
    ncols = int(np.ceil(len(files)/nrows))
    # get frames array and figure
    plt.ion()
    fig, frames = plt.subplots(ncols=ncols, nrows=nrows)
    for it in range(len(files)):
        # select the correct frame
        jt, kt = it % nrows, it // nrows
        frame = frames[jt, kt]
        # add frame to list
        ALL_FRAMES.append(frame)
        # ge the difference
        diff = data_array[it] - data_ref
        # convert to dv
        dv = ((diff/data_ref)) * 299792458
        # normalise scatter around zero
        ddv = dv - np.nanmedian(dv)
        # get the standard deviation
        x_ind, y_ind = np.indices(ddv.shape)
        stdmask = np.zeros_like(ddv, dtype=bool)
        for stdorder in STD_ORDER:
            stdmask |= (x_ind == stdorder)
        std = np.nanstd(ddv[stdmask])

        # construct title
        title = '{0} ({1}) std={2:.3f}'
        prog = hdr_array[it]['WAVECODE']
        if 'WAVE' in prog:
            code = 'WAVE'
        else:
            code = 'HC'
        odocode = files[it].split('_pp')[0]
        targs = [odocode, code, std]

        # choose whether to plot colorbar
        cbar = kt == ncols -1

        # plot
        diffplot(frame, ddv, title.format(*targs), colorbar=cbar)

        # remove axis tick labels
        if jt != nrows - 1:
            frame.set_xticklabels([])
        if kt != 0:
            frame.set_yticklabels([])

        # set current data
        CURRENT_DATA.append(ddv)
        CURRENT_FILE.append(files[it])
        CURRENT_CODE.append(prog)

    cid = fig.canvas.mpl_connect('button_press_event', on_pick)

    # clear the empty plots
    for it in range(len(files), nrows*ncols):
        jt, kt = it % nrows, it // nrows
        frame = frames[jt, kt]
        frame.axis('off')

    plt.subplots_adjust(wspace=0.025, hspace=0.5)
    plt.show()




# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-11-16 11:32
@author: ncook
Version 0.0.1
"""
import numpy as np
import os
from astropy.io import fits
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


# =============================================================================
# Define variables
# =============================================================================
RUNFILE = 'hcrun.run'
RECIPE = 'cal_HC_E2DS_EA_spirou'
REDUCED_DIR = '/spirou/cfht_nights/cfht/reduced_1/'
REF_NUM = 10
STD_ORDER = [33, 34, 35, 36, 37]
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def read_run_file(recipe, filename):

    # read file
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()

    # push into dictionary
    runs = []

    for line in lines:
        # extract info from line
        runname = line.split('=')[0]
        args = line.split('=')[1].replace('[', '').replace(']', '')
        args = args.replace('\'', '').replace('\n', '').replace(' ', '')
        args = args.split(',')
        # get run name
        rname = args[0]
        # get night name
        rnightname = args[1]
        # get file names
        rfiles = args[2:]
        # check that recipe is correct
        if rname != recipe:
            continue
        # construct absolute path
        for rfile in rfiles:
            absfile = os.path.join(REDUCED_DIR, rnightname, rfile)
            # check path exists
            if os.path.exists(absfile):
                runs.append(absfile)
            else:
                print('Error: File does not exist = {0}'.format(absfile))

    return runs


def diffplot(frame, data, title, ticks=None, labels=False, colorbar=True):
    # plot each dv image
    im = frame.imshow(data, aspect='auto',
                      interpolation='nearest', origin='lower')
    #if ticks is None:
    #    ticks = [-200, -100, 0, 100, 200]
    # set title
    frame.set_title(title, fontsize='small')
    # add colour bar
    if colorbar:
        # make an axis for colorbar
        divider = make_axes_locatable(frame)
        cax = divider.append_axes("right", size='5%', pad=0.05)
        cbar = fig.colorbar(im, cax=cax, ax=frame)
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
    # Read file
    print('Reading file...')
    hcruns = read_run_file(RECIPE, RUNFILE)
    # add data to the data cubes
    data_array, hdr_array = [], []
    for filename in hcruns:
        data, header = fits.getdata(filename, header=True)
        data_array.append(data)
        hdr_array.append(header)
    # select ref data
    data_ref = data_array[REF_NUM]
    # set up plot
    nrows = int(np.ceil(np.sqrt(len(hcruns))))
    ncols = int(np.ceil(len(hcruns)/nrows))
    # get frames array and figure
    plt.ion()
    fig, frames = plt.subplots(ncols=ncols, nrows=nrows)
    for it in range(len(hcruns)):
        # log
        print('Plotting graph {0} of {1}'.format(it +1, len(hcruns)))
        # select the correct frame
        jt, kt = it % nrows, it // nrows
        frame = frames[jt, kt]
        # ge the difference
        diff = data_array[it] / data_ref
        # convert to dv
        # dv = ((diff/data_ref)) * 299792458
        dv = np.array(diff)
        # normalise scatter around zero
        #ddv = dv - np.nanmedian(dv)
        ddv = np.array(dv)
        # get the standard deviation
        x_ind, y_ind = np.indices(ddv.shape)
        stdmask = np.zeros_like(ddv, dtype=bool)
        for stdorder in STD_ORDER:
            stdmask |= (x_ind == stdorder)
        std = np.nanstd(ddv[stdmask])
        # construct title
        title = '{0} std={1:.3f}'
        odocode = os.path.basename(hcruns[it]).split('_pp')[0]
        targs = [odocode, std]
        # choose whether to plot colorbar
        cbar = kt == ncols -1
        # plot
        diffplot(frame, ddv, title.format(*targs), colorbar=cbar)
        # remove axis tick labels
        if jt != nrows - 1:
            frame.set_xticklabels([])
        if kt != 0:
            frame.set_yticklabels([])

    # clear the empty plots
    for it in range(len(hcruns), nrows*ncols):
        jt, kt = it % nrows, it // nrows
        frame = frames[jt, kt]
        frame.axis('off')

    plt.subplots_adjust(wspace=0.025, hspace=0.5)
    plt.show()


# =============================================================================
# End of code
# =============================================================================
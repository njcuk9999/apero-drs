#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-12-12 at 11:49

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from astropy.io import fits



# =============================================================================
# Define variables
# =============================================================================
WORKSPACE = '/spirou/cfht_nights/cfht/telluDB_1'

OBJNAME = 'Gl15A'
DATE = '2018-09-22'

case = 1
if case == 0:
    ORDER_NUM = 13
    XMIN, XMAX = 1155.3, 1155.9
elif case == 1:
    ORDER_NUM = 35
    XMIN, XMAX = 1749, 1754

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
    # list all files
    files = os.listdir(WORKSPACE)
    # ----------------------------------------------------------------------
    # filter required files
    corrfiles = []
    transfiles = []
    for it, filename in enumerate(files):
        print('Processing file {0} of {1}'.format(it + 1, len(files)))
        path = os.path.join(WORKSPACE, filename)
        if 'tellu_corrected.fits' in filename:
            header = fits.getheader(path)
            # cond1
            cond1 = OBJNAME == header['OBJNAME'].strip()
            # cond2
            cond2 = DATE == header['DATE-OBS'].strip()
            # add to list if pass
            if cond1 and cond2:
                print('\tCorr file added')
                corrfiles.append(path)
        elif 'trans.fits' in filename:
            print('\tTrans file added')
            transfiles.append(path)
    # ----------------------------------------------------------------------
    if len(corrfiles) == 0:
        raise ValueError('No telluric corrected files found.')
    # ----------------------------------------------------------------------
    # load corr files
    print('Loading corrected data...')
    corrdata = []
    for it, filename in enumerate(corrfiles):
        print('\tOpening file {0} of {1}'.format(it + 1, len(corrfiles)))
        path = os.path.join(WORKSPACE, filename)
        corrdata.append(np.array(fits.getdata(path)))
    # ----------------------------------------------------------------------
    # load trans files
    print('Loading trans data...')
    transdata = []
    for it, filename in enumerate(transfiles):
        print('\tOpening file {0} of {1}'.format(it + 1, len(transfiles)))
        path = os.path.join(WORKSPACE, filename)
        transdata.append(np.array(fits.getdata(path)))
    # ----------------------------------------------------------------------
    # get master wave file
    wavedata = fits.getdata('MASTER_WAVE.fits')

    wavemask = (wavedata[ORDER_NUM] >= XMIN) & (wavedata[ORDER_NUM] <= XMAX)

    # ----------------------------------------------------------------------
    # loop around a plot data
    plt.close()
    fig, frame = plt.subplots(nrows=1, ncols=1)
    # ----------------------------------------------------------------------
    # plot corrected spectra
    print('Plotting corrected spectra...')
    for it in range(len(corrfiles)):
        print('\tPlotting corr file {0} of {1}'.format(it, len(corrfiles)))
        x = wavedata[ORDER_NUM][wavemask]
        y = corrdata[it][ORDER_NUM][wavemask]
        # normalise y
        y = y/np.nanmedian(y)
        basename = os.path.basename(corrfiles[it])
        odoname = basename.split('_')[0]
        frame.plot(x, y, label=odoname, linewidth=0.5)
    # ----------------------------------------------------------------------
    # plot corrected spectra
    print('Plotting trans spectra...')
    for it in range(len(transfiles)):
        print('\tPlotting trans file {0} of {1}'.format(it, len(transfiles)))
        x = wavedata[ORDER_NUM][wavemask]
        y = transdata[it][ORDER_NUM][wavemask]
        basename = os.path.basename(transfiles[it])
        odoname = basename.split('_')[0]
        frame.plot(x, y, color='0.5', linestyle='--', linewidth=0.25)
        frame.set(xlabel='Wavelength', ylabel='flux', xlim=(XMIN, XMAX),
                  title='Order {0}'.format(ORDER_NUM))
    # ----------------------------------------------------------------------
    # set axis labels etc
    frame.set(xlabel='Wavelength', ylabel='flux', xlim=(XMIN, XMAX),
              title='Date = {0}, Order {1}'.format(DATE, ORDER_NUM))
    frame.get_xaxis().get_major_formatter().set_useOffset(False)
    frame.legend(loc=2, bbox_to_anchor=(1.01, 1.0), ncol=2)
    # ----------------------------------------------------------------------
    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================

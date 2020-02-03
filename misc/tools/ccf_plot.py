#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-01-07 at 18:56

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

# =============================================================================
# Define variables
# =============================================================================
WORK_DIRECTORY = '/scratch2/spirou/mini_data/reduced'

MASK = 'gl581_sep18_cleaned'
OBJNAME = 'Gl699'
# -----------------------------------------------------------------------------
TIMECOL = 'MJDMID'
RV_OBJ = 'RV_OBJ'
RV_DRIFT = 'RV_DRIFT'
RV_CORR = 'RV_CORR'


# =============================================================================
# Define functions
# =============================================================================



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # get files
    files = glob.glob(WORK_DIRECTORY + '/*/*ccf*{0}*'.format(MASK))

    good_files = []
    good_headers = []
    # open all files and just keep those for our object
    for filename in tqdm(files):
        # get header
        header = fits.getheader(filename, ext=1)
        # keep if objname is valid
        if header['OBJECT'] == OBJNAME:
            good_files.append(filename)
            good_headers.append(dict(header))

    # store rvs
    rv_obj_arr, rv_drift_arr, rv_corr_arr, time_arr = [], [], [], []

    # read the header keys
    for good_header in good_headers:
        time_arr.append(good_header[TIMECOL])
        rv_obj_arr.append(good_header[RV_OBJ])
        rv_drift_arr.append(good_header[RV_DRIFT])
        rv_corr_arr.append(good_header[RV_CORR])

    # convert to numpy arrays
    time_arr = np.array(time_arr)
    rv_obj_arr = np.array(rv_obj_arr)
    rv_drift_arr = np.array(rv_drift_arr)
    rv_corr_arr = np.array(rv_corr_arr)

    OBJRV = np.nanmean(rv_corr_arr)

    # get minimum time
    mintime = np.min(time_arr)


    # plot
    plt.ioff()
    plt.close()
    fig, frame = plt.subplots(ncols=1, nrows=1)

    frame.scatter(time_arr - mintime, 1000 * (rv_obj_arr - OBJRV),
                  label='OBJ Non Corr - {0:.3f} km/s'.format(OBJRV))
    frame.scatter(time_arr - mintime, 1000 * (rv_drift_arr),
                  label='FP Drift')
    frame.scatter(time_arr - mintime, 1000 * (rv_corr_arr - OBJRV),
                  label='OBJ Corr - {0:.3f} km/s'.format(OBJRV))

    frame.legend(loc=0)

    frame.set(xlabel='Time [MJD] - {0}'.format(mintime),
              ylabel='RV [m/s]')
    plt.show()


# =============================================================================
# End of code
# =============================================================================

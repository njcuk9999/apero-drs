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
from astropy.time import Time
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings
import glob

# =============================================================================
# Define variables
# =============================================================================
WORK_DIRECTORY = ''

MASK = 'masque_sept18_andres_trans50_AB'
OBJNAME = 'Gl699'
# -----------------------------------------------------------------------------
TIMECOL = 'MJDMID'
RV_OBJ = 'RV_OBJ'
RV_DRIFT = 'RV_DRIFT'
RV_CORR = 'RV_CORR'
RV_WAVEFP = 'RV_WAVFP'
RV_SIMFP = 'RV_SIMFP'
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
    files = glob.glob(WORK_DIRECTORY + '*/*ccf*{0}*'.format(MASK))

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
    rv_wavefp_arr, rv_simfp_arr = [], []
    # read the header keys
    for good_header in good_headers:
        rv_time = Time(good_header[TIMECOL], format='mjd')
        rv_obj = float(good_header[RV_OBJ])
        rv_drift = float(good_header[RV_DRIFT])
        rv_corr = float(good_header[RV_CORR])
        rv_wavefp = float(good_header[RV_WAVEFP])
        rv_simfp = float(good_header[RV_SIMFP])
        time_arr.append(rv_time)
        rv_obj_arr.append(rv_obj)
        rv_drift_arr.append(rv_drift)
        rv_corr_arr.append(rv_corr)
        rv_wavefp_arr.append(rv_wavefp)
        rv_simfp_arr.append(rv_simfp)

    # convert times to time array
    times = Time(time_arr)
    times.format = 'iso'  # times in iso YYYY-MM-DD

    # convert to numpy arrays
    rv_obj_arr = np.array(rv_obj_arr)
    rv_drift_arr = np.array(rv_drift_arr)
    rv_corr_arr = np.array(rv_corr_arr)
    rv_wavefp_arr = np.array(rv_wavefp_arr)
    rv_simfp_arr = np.array(rv_simfp_arr)

    OBJRV = np.nanmedian(rv_corr_arr)
    # OBJRV = 0.0

    # plot
    plt.ioff()
    plt.close()
    fig, frames = plt.subplots(ncols=1, nrows=2, sharex=True)

    frame = frames[0]
    frame.plot_date(times.plot_date, 1000 * (rv_obj_arr - OBJRV),
                    marker='o', linestyle='None', mfc='None', mec='r',
                    label='OBJ Non Corr - {0:.3f} km/s'.format(OBJRV))
    frame.plot_date(times.plot_date, 1000 * (rv_corr_arr - OBJRV),
                    marker='x', linestyle='None', color='b',
                    label='OBJ Corr - {0:.3f} km/s'.format(OBJRV))
    frame.legend(loc=0)
    frame.set(xlabel='Time', ylabel='RV [m/s]')
    frame.xaxis.set_tick_params(rotation=30, labelsize=10)
    fig.autofmt_xdate()
    frame.ticklabel_format(axis='y', useOffset=False)

    frame = frames[1]
    frame.plot_date(times.plot_date, 1000 * (rv_drift_arr),
                    marker='o', linestyle='None', mfc='None', mec='g',
                    label='FP Drift')
    frame.plot_date(times.plot_date, 1000 * (rv_wavefp_arr),
                    marker='x', linestyle='None', color='orange',
                    label='RV from wave sol. FP')
    frame.plot_date(times.plot_date, 1000 * (rv_simfp_arr),
                    marker='s', linestyle='None', color='purple',
                    label='RV from sim FP')
    frame.legend(loc=0)
    frame.set(xlabel='Time', ylabel='RV [m/s]')
    frame.xaxis.set_tick_params(rotation=30, labelsize=10)
    fig.autofmt_xdate()
    frame.ticklabel_format(axis='y', useOffset=False)

    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================

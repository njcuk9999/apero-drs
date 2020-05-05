#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:38
@author: ncook
Version 0.0.1
"""
import numpy as np
from astropy.io import fits
from astropy.time import Time
import matplotlib.pyplot as plt
import glob
from tqdm import tqdm

# =============================================================================
# Define variables
# =============================================================================
# header keys
KW_FIBER = 'FIBER'
KW_TIME = 'MJDMID'
KW_TIME_UNIT = 'mjd'
KW_DRIFT = 'WFPDRIFT'

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # get wave night files
    files = glob.glob('*wave_night*')
    # get wave master fp files
    files += glob.glob('*wavem_fp_*')

    # storage
    fibers = []
    times = []
    drifts = []
    found = []
    night = []

    # loop around file and save to storage
    for filename in tqdm(files):
        header = fits.getheader(filename)
        # add fiber
        if KW_FIBER in header:
            fibers.append(header[KW_FIBER])
        else:
            continue
        # add time
        if KW_TIME in header:
            times.append(Time(header[KW_TIME], format=KW_TIME_UNIT))
        else:
            continue
        # add drifts
        if KW_DRIFT in header:
            drifts.append(header[KW_DRIFT])
        else:
            continue
        # deal with night vs master
        if 'wave_night' in filename:
            night.append(True)
        else:
            night.append(False)
        # add found filename
        found.append(filename)
    # convert times to time array
    times = Time(times)
    times.format = 'iso'                        # times in iso YYYY-MM-DD
    # convert to numpy arrays
    fibers = np.array(fibers)
    drifts = np.array(drifts) * 1000            # drift in m/s
    found = np.array(found)
    night = np.array(night)
    # sort by time
    sort = np.argsort(times)
    fibers = fibers[sort]
    times = times[sort]
    drifts = drifts[sort]
    found = found[sort]
    night = night[sort]
    # get fiber masks
    fiberab_n = (fibers == 'AB') & night
    fibera_n = (fibers == 'A') & night
    fiberb_n = (fibers == 'B') & night
    fiberc_n = (fibers == 'C') & night
    fiberab_m = (fibers == 'AB') & ~night
    fibera_m = (fibers == 'A') & ~night
    fiberb_m = (fibers == 'B') & ~night
    fiberc_m = (fibers == 'C') & ~night

    # plot
    plt.close()
    fig, frame = plt.subplots(ncols=1, nrows=1)

    frame.plot_date(times[fiberab_m].plot_date, drifts[fiberab_m],
                    markeredgecolor='r', markerfacecolor='None', marker='x',
                    ls='None', markersize=10, label='AB MASTER')
    frame.plot_date(times[fibera_m].plot_date, drifts[fibera_m],
                    markeredgecolor='b', markerfacecolor='None', marker='x',
                    ls='None', markersize=10, label='A MASTER')
    frame.plot_date(times[fiberb_m].plot_date, drifts[fiberb_m],
                    markeredgecolor='g', markerfacecolor='None', marker='x',
                    ls='None', markersize=10, label='B MASTER')
    frame.plot_date(times[fiberc_m].plot_date, drifts[fiberc_m],
                    markeredgecolor='orange', markerfacecolor='None',
                    marker='x', ls='None', markersize=10, label='C MASTER')

    frame.plot_date(times[fiberab_n].plot_date, drifts[fiberab_n],
                    markerfacecolor='r', markeredgecolor='k', marker='o',
                    ls='None', markersize=7, label='AB NIGHT')
    frame.plot_date(times[fibera_n].plot_date, drifts[fibera_n],
                    markerfacecolor='b', markeredgecolor='k', marker='o',
                    ls='None', markersize=7, label='A NIGHT')
    frame.plot_date(times[fiberb_n].plot_date, drifts[fiberb_n],
                    markerfacecolor='g', markeredgecolor='k', marker='o',
                    ls='None', markersize=7, label='B NIGHT')
    frame.plot_date(times[fiberc_n].plot_date, drifts[fiberc_n],
                    markerfacecolor='orange', markeredgecolor='k',
                    marker='o', ls='None', markersize=7, label='C NIGHT')

    frame.legend(loc=0)
    frame.set(xlabel='Date', ylabel='RV (CCF FP) [m/s]')
    fig.autofmt_xdate()
    frame.ticklabel_format(axis='y', useOffset=False)
    plt.show()
    plt.close()

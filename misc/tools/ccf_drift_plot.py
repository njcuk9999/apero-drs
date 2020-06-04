#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-21

@author: cook
"""
import os
import glob
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np
from tqdm import tqdm


# =============================================================================
# Define variables
# =============================================================================

# select an object
OBJNAME = 'Gl699'
# -----------------------------------------------------------------------------
# files
objfiles_AB = glob.glob('*/*o_pp*ccf*AB.fits')
objfiles_C = glob.glob('*/*o_pp*ccf*C.fits')
# keywords
KW_OBJECT = 'OBJECT'
KW_TIME = 'MJDMID'
KW_RV_OBJ = 'RV_OBJ'
KW_RV_DRIFT = 'RV_DRIFT'
KW_RV_SIMFP = 'RV_SIMFP'
KW_RV_WAVFP = 'RV_WAVFP'

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    # -------------------------------------------------------------------------
    # get data
    rv_obj_arr, rv_drift_arr = [], []
    rv_simfp_arr, rv_wavfp_arr = [], []
    time_arr, kind_arr = [], []
    # -------------------------------------------------------------------------
    # get sets
    files = [objfiles_AB, objfiles_C]
    kinds = ['OBJFP_AB', 'OBJFP_C']
    symbols = ['x', '+']
    # -------------------------------------------------------------------------
    # loop around sets
    for it in range(len(files)):
        # print progress
        print('Processing {0} files'.format(kinds[it]))
        # loop around files in set
        for filename in tqdm(files[it]):
            # get header
            header = fits.getheader(filename, ext=1)
            # filter by object
            if OBJNAME is not None:
                objname = header[KW_OBJECT]
                # skip other objects
                if objname != OBJNAME:
                    continue
            # append kind
            kind_arr.append(kinds[it])
            # get time
            time = header[KW_TIME]
            time_arr.append(time)
            # get rv obj
            rv_obj = header[KW_RV_OBJ]
            if rv_obj == 'None':
                rv_obj = np.nan
            rv_obj_arr.append(rv_obj)
            # get rv drift
            rv_drift = header[KW_RV_DRIFT]
            if rv_drift == 'None':
                rv_drift = np.nan
            rv_drift_arr.append(rv_drift)
            # get rv_simfp
            rv_simfp = header[KW_RV_SIMFP]
            if rv_simfp == 'None':
                rv_simfp = np.nan
            rv_simfp_arr.append(rv_simfp)
            # get rv_wavfp
            rv_wavfp = header[KW_RV_WAVFP]
            if rv_wavfp == 'None':
                rv_wavfp = np.nan
            rv_wavfp_arr.append(rv_wavfp)
    # -------------------------------------------------------------------------
    # convert to numpy arrays
    rv_obj_arr, rv_drift_arr = np.array(rv_obj_arr), np.array(rv_drift_arr)
    rv_simfp_arr, rv_wavfp_arr = np.array(rv_simfp_arr), np.array(rv_wavfp_arr)
    time_arr, kind_arr = np.array(time_arr), np.array(kind_arr)

    # -------------------------------------------------------------------------
    # plot
    plt.close()
    fig, frames = plt.subplots(ncols=1, nrows=4, sharex=True)
    # add title if required
    if OBJNAME is not None:
        plt.suptitle('OBJECT = {0}'.format(OBJNAME))

    # plot rv_obj
    frame = frames[0]
    # loop around kinds
    for it, kind in enumerate(kinds):
        sym = symbols[it]
        # make mask
        mask = kind_arr == kind
        frame.scatter(time_arr[mask], rv_obj_arr[mask], label=kind,
                      marker=sym)
    frame.legend(loc=0)
    frame.set(xlabel='MJD', ylabel=KW_RV_OBJ)

    # plot rv_drift
    frame = frames[1]
    # loop around kinds
    for it, kind in enumerate(kinds):
        sym = symbols[it]
        # make mask
        mask = kind_arr == kind
        frame.scatter(time_arr[mask], rv_drift_arr[mask], label=kind,
                      marker=sym)
    frame.legend(loc=0)
    frame.set(xlabel='MJD', ylabel=KW_RV_DRIFT)

    # plot rv_simfp
    frame = frames[2]
    # loop around kinds
    for it, kind in enumerate(kinds):
        sym = symbols[it]
        # make mask
        mask = kind_arr == kind
        frame.scatter(time_arr[mask], rv_simfp_arr[mask], label=kind,
                      marker=sym)
    frame.legend(loc=0)
    frame.set(xlabel='MJD', ylabel=KW_RV_SIMFP)

    # plot rv_wavfp
    frame = frames[3]
    # loop around kinds
    for it, kind in enumerate(kinds):
        sym = symbols[it]
        # make mask
        mask = kind_arr == kind
        frame.scatter(time_arr[mask], rv_wavfp_arr[mask], label=kind,
                      marker=sym)
    frame.legend(loc=0)
    frame.set(xlabel='MJD', ylabel=KW_RV_WAVFP)

    # show and close
    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================

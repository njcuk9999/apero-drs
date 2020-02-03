#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-01-15 at 10:50

@author: cook
"""
import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy import units as uu
from tqdm import tqdm
import matplotlib.pyplot as plt


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'analyse_master_log.py'
RECIPE = 'obj_mk_tellu_spirou'
QC_NAME = 'airmass_diff'
QC_NAME_VALUE = 'Airmass Difference'
LIMIT = 0.1


# =============================================================================
# Define functions
# =============================================================================
def get_qc(mystring):
    # clean start/end of qc string
    raw_qc = mystring.strip()
    # extract individual qc criteria
    qcs = raw_qc.split('||')
    # set default values
    value = None
    passed = None
    # loop around qcs in set
    for it in range(len(qcs)):
        # if qc starts with the qc name we have found the right value
        if qcs[it].startswith(QC_NAME):
            # split by white spaces first
            valuepair = qcs[it].split()[0]
            # split by the equals
            value = valuepair.split('=')[1]

            # get passed failed
            if qcs[it].strip().endswith('PASSED'):
                passed = True
            else:
                passed = False

            # we can stop here
            break
    # return value
    return value, passed


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # load table
    log = Table.read('MASTER_LOG.fits')

    # storage for outputs
    times = []
    qc_values = []
    qc_passes = []
    run_strings = []

    # get columns
    table_recipes = np.array(log['RECIPE'], dtype=str)
    table_times = np.array(log['HTIME'], dtype=str)
    table_qc = np.array(log['QC_STRING'], dtype=str)
    table_rs = np.array(log['RUNSTRING'], dtype=str)

    # loop around rows in the table
    for row in tqdm(range(len(table_recipes))):
        # only consider wanted recipe
        if table_recipes[row] != RECIPE:
            continue
        # get time
        times.append(Time(table_times[row], format='iso'))
        # get qc values
        qc_value, qc_pass = get_qc(table_qc[row])
        qc_values.append(float(qc_value))
        qc_passes.append(qc_pass)
        # append run string
        run_strings.append(table_rs[row])

    # convert time to Time array
    times = Time(times)

    # get delta time in seconds
    dtimes = (times - np.min(times)).to(uu.s)

    # convert to numpy arrays
    qc_values = np.array(qc_values)
    qc_passes = np.array(qc_passes)

    # plot graph
    fig, frame = plt.subplots(ncols=1, nrows=1)
    # plot passed
    frame.scatter(dtimes[qc_passes], qc_values[qc_passes], color='g',
                  marker='x')
    frame.scatter(dtimes[~qc_passes], qc_values[~qc_passes], color='r',
                  marker='x')
    # plot limit
    xmin, xmax = frame.get_xlim()
    frame.hlines(LIMIT, xmin, xmax, color='b')

    title = 'Recipe = {0} \n Passes={1} Fails={2} Total={3}'
    targs = [RECIPE, np.sum(qc_passes), len(qc_passes) - np.sum(qc_passes),
             len(qc_passes)]
    frame.set(xlabel='Time since first [s]', ylabel=QC_NAME_VALUE,
              title=title.format(*targs), xlim=[xmin, xmax])

# =============================================================================
# End of code
# =============================================================================
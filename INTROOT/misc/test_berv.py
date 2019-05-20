#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-10-01 at 09:22

@author: cook
"""

import numpy as np
import matplotlib.dates
import matplotlib.ticker
import matplotlib.pyplot as plt
import os
from astropy.time import Time
import astropy.units as uu
from datetime import datetime
from tqdm import tqdm

from SpirouDRS.spirouImage.spirouBERV import newbervmain


# =============================================================================
# Define variables
# =============================================================================
OBS_LONG = 155.468876
OBS_LAT = 19.825252
OBS_ALT = 4.204
EXPTIME = 5.5 * 60
# -----------------------------------------------------------------------------
DUMP_PATH = '/scratch/Projects/spirou_py3/data_misc/berv_test/'


# =============================================================================
# Define functions
# =============================================================================
def date_axis(fig1, frame, x, y, fmt='%Y-%m-%d %H:%M:%S.%f'):
    # From:
    #    https://stackoverflow.com/a/45717773
    def striptime(s):
        return datetime.strptime(s, fmt)
    x = list(map(striptime, x))
    frame.plot(x, y)
    lloc = matplotlib.ticker.FixedLocator(matplotlib.dates.date2num(x),
                                          nbins=10)
    fmt = matplotlib.dates.DateFormatter(fmt)
    frame.xaxis.set_major_locator(lloc)
    frame.xaxis.set_major_formatter(fmt)
    fig1.autofmt_xdate()

    return fig1, frame


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # need dictionary input/output storage
    p, loc = dict(), dict()
    p['LOG_OPT'] = 'test_berv'
    p['EXPTIME'] = EXPTIME

    # dates / times setup
    year0 = Time(2017, format='decimalyear')
    year1 = Time(2018, format='decimalyear')
    # noinspection PyUnresolvedReferences,PyTypeChecker
    dates = Time(np.arange(year0, year1 + 1*uu.day, 1*uu.day))
    # noinspection PyUnresolvedReferences,PyTypeChecker
    times = Time(np.arange(year0, year0 + 1*uu.day, 1*uu.min))

    # define variables
    var_dates = dates.iso
    var_utc = times.iso
    var_ra = np.arange(0, 360, 0.5)
    var_dec = np.arange(-89.9, 89.9, 0.5)
    var_pmra = 10**np.arange(-3, 3, 0.1)
    var_pmde = 10**np.arange(-3, 3, 0.1)
    var_equinox = [2000.0]

    variables = [var_dates, var_utc, var_ra, var_dec, var_pmra, var_pmde,
                 var_equinox]
    names = ['Dates', 'UTC', 'RA', 'Dec', 'PMRA', 'PMDE', 'EQUINOX']
    units = ['Days', 'Days', 'Deg', 'Deg', 'mas/yr', 'mas/yr', '']

    storage = dict()

    for v_it, var in enumerate(variables):

        # print progress
        print('Processing variation in {0}'.format(names[v_it]))
        # skip if length = 1
        if len(variables[v_it]) == 1:
            continue

        # get the constant for this iteration
        var_const = []
        for v_it2 in range(len(variables)):
            var_const.append(variables[v_it2][0])

        # define storage
        bervs, bjds, bervmaxs = [], [], []

        # loop around variable
        for v_it2 in tqdm(range(len(variables[v_it]))):

            var_const[v_it] = variables[v_it][v_it2]
            # dates and utc seed from same constant
            if v_it == 0:
                var_obs = str(var_const[0]).split(' ')
            elif v_it == 1:
                var_obs = str(var_const[1]).split(' ')
            else:
                var_obs = str(var_const[0]).split(' ')
            # push into variables needed for newbervmain
            p['DATE-OBS'] = var_obs[0]
            p['UTC-OBS'] = var_obs[1]
            ra = var_const[2]
            dec = var_const[3]
            pmra = var_const[4]
            pmde = var_const[5]
            equinox = var_const[6]

            out = newbervmain(p, ra, dec, equinox, None, None, None, None,
                              OBS_LONG, OBS_LAT, OBS_ALT, pmra, pmde,
                              method='new')
            bervs.append(out[0])
            bjds.append(out[1])

        storage[names[v_it]] = [bervs, bjds]

    # save to file
    for var in storage.keys():
        dump_name = 'data_dump_{0}'.format(var)
        dump_path = os.path.join(DUMP_PATH, dump_name)
        np.save(dump_path, np.array(storage[var]))

    plt.close('all')
    plt.ion()

    for v_it in range(len(variables)):
        # print progress
        print('Plotting variation in {0}'.format(names[v_it]))
        # skip if length = 1
        if len(variables[v_it]) == 1:
            continue
        # get variables from storage
        bervs = storage[names[v_it]][0]
        bjds = storage[names[v_it]][1]
        if v_it == 0:
            var = dates.plot_date - np.nanmedian(dates.plot_date)
            xlabel = '$\Delta$' + names[v_it] + ' [{0}]'.format(units[v_it])
        elif v_it == 1:
            var = times.plot_date - np.nanmedian(times.plot_date)
            xlabel = '$\Delta$' + names[v_it] + ' [{0}]'.format(units[v_it])
        else:
            var = variables[v_it]
            xlabel = names[v_it] + ' [{0}]'.format(units[v_it])

        y0 = np.array(bervs) - np.nanmedian(bervs)
        y1 = np.array(bjds) - np.nanmedian(bjds)

        # plot
        fig, frames = plt.subplots(nrows=2, ncols=1)

        frames[0].scatter(var, y0, s=5, marker='x')
        frames[1].scatter(var, y1, s=5, marker='x')
        frames[0].plot(var, y0)
        frames[1].plot(var, y1)

        frames[0].set(xlabel=xlabel, ylabel='$\Delta$ BERV [km/s]')
        frames[0].xaxis.set_ticks_position('top')
        frames[0].xaxis.set_label_position('top')
        frames[1].set(xlabel=xlabel, ylabel='$\Delta$ BJD [Days]')
        fig.subplots_adjust(hspace=0, wspace=0)

        frames[0].set_ylim(np.min(y0), np.max(y0))
        frames[1].set_ylim(np.min(y1), np.max(y1))

        fig.tight_layout()


# =============================================================================
# End of code
# =============================================================================

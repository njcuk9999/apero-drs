#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-06-01 15:35
@author: ncook
Version 0.0.1
"""
import numpy as np
import matplotlib.pyplot as plt

from SpirouDRS import spirouTHORCA

# =============================================================================
# Define variables
# =============================================================================
# RANGE
MIN_X = 0
MAX_X = 200
# number of points
NUM_POINTS = 10
# Amplitude, mean position, sigma, dc offset
INPUT_PARAMS = [4, 100, 25, 1]
# Maximum noise (in units of amplitudes)
MAX_NOISE = 1.0

CCD_RON = 1.0


# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def gauss_function(x, a, x0, sigma, dc):
    """
    A standard 1D gaussian function (for fitting against)]=

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian
    :param dc: float, the constant level below the gaussian

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    return a * np.exp(-0.5 * ((x - x0) / sigma) ** 2) + dc


def plot_gauss(xs, ys, colours, lines, markers, labels):
    # set up graph
    fig, frame = plt.subplots(ncols=1, nrows=1)
    # plot
    for it in range(len(xs)):

        if it > 0:
            xfit = np.linspace(np.min(xs), np.max(xs), 10000)
            yfit = gauss_function(xfit, *ys[it])
        else:
            xfit = xs[it]
            yfit = ys[it]
        frame.plot(xfit, yfit, color=colours[it], ls=lines[it],
                   marker=markers[it], label=labels[it])

    frame.set(xlabel='x value', ylabel='y value')
    frame.legend(loc=0)


def plot_res(xs, ys, labels):
    # set up graph
    fig, frame = plt.subplots(ncols=1, nrows=1)
    # storage
    used = []
    # loop around x
    for it in range(len(xs)):
        for jt in range(len(xs)):
            # get names
            name1 = labels[it]
            name2 = labels[jt]
            # if names are the same do not compare
            if name1 == name2:
                continue
            # if in used or in used backwards to not compare
            if [name2, name1] in used:
                continue
            if [name1, name2] in used:
                continue
            # get residual
            res = ys[it] - ys[jt]
            # plot residual
            frame.plot(xs[it], res, label='{0} - {1}'.format(name1, name2))
            # append used
            used.append([name1, name2])

    frame.set(xlabel='x value', ylabel='residual value')
    frame.legend(loc=0)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------

    p = dict()
    p['PID'] = None
    p['RECIPE'] = 'find_lines_test'

    # Generate a Gaussian with noise
    x_in = np.linspace(MIN_X, MAX_X, NUM_POINTS)
    noise = np.random.uniform(0, MAX_NOISE, size=NUM_POINTS)
    y_in = gauss_function(x_in, *INPUT_PARAMS) + noise
    w_in = 1.0 / (y_in + CCD_RON ** 2)

    guess = INPUT_PARAMS

    fargs = [p, x_in, y_in, w_in, guess]

    # Fortran
    a1, e1, c1 = spirouTHORCA.spirouTHORCA.fitgaus_wrapper(*fargs, mode=0)
    # SciPy
    a2, e2, c2 = spirouTHORCA.spirouTHORCA.fitgaus_wrapper(*fargs, mode=1)

    # ----------------------------------------------------------------------
    # plot the results
    x_all = [x_in, x_in, x_in]
    y_all = [y_in, a1, a2]
    linecolours = ['k', 'b', 'r']
    linestyles = ['None', '-', '-']
    linemarkers = ['x', None, None, None]
    names = ['input', 'FORTRAN', 'scipy.curve_fit']

    plot_gauss(x_all, y_all, linecolours, linestyles, linemarkers, names)
    # ----------------------------------------------------------------------
    # plot the residuals
    x_all = [x_in, x_in]
    y_all = [c1, c2]
    names = ['FORTRAN', 'scipy.curve_fit']

    plot_res(x_all, y_all, names)

    plt.show()
    plt.close()

# =============================================================================
# End of code
# =============================================================================

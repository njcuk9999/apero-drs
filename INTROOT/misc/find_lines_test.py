#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-06-01 15:35
@author: ncook
Version 0.0.1
"""
import numpy as np
import warnings
from scipy.optimize import curve_fit
from scipy.stats import chisquare
from lmfit.models import Model, GaussianModel
import matplotlib.pyplot as plt
import time

from SpirouDRS.fortran import fitgaus


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


def fitgaussian_python(x, y, weights, guess):

    # invert the weights
    sig = 1.0 / weights
    # first gauss fit
    with warnings.catch_warnings(record=True) as _:
        pfit, pcov = curve_fit(gauss_function, x, y, p0=guess, sigma=sig,
                               absolute_sigma=True)
    # calculate the fit from parameters
    yfit = gauss_function(x, *pfit)
    #work out the normalisation constant
    chi2, _ = chisquare(y, f_exp=yfit)
    rchi2 = chi2 / (len(y) - len(guess))
    # calculate the sigma
    siga = np.sqrt(np.diag(pcov)) * np.sqrt(rchi2)

    return pfit, siga, yfit


def fitgaussian_lmfit(x, y, weights, guess):

    gmodel = Model(gauss_function)

    out = gmodel.fit(y, x=x, params=None, weights=weights)
    #     out = gmodel.fit(y, x=x, a=guess[0], x0=guess[1], sigma=guess[2],
    #                      dc=guess[3], params=None, weights=weights)

    pfit = [out.values['a'], out.values['x0'], out.values['sigma'],
            out.values['dc']]


    siga = [out.params['a'].stderr,
            out.params['x0'].stderr,
            out.params['sigma'].stderr,
            out.params['dc'].stderr]

    return np.array(pfit), np.array(siga), out.best_fit


def fitgaussian_fortran(x, y, weights, guess):
    yfit = np.zeros_like(y)
    siga = np.zeros_like(guess)
    fitgaus.fitgaus(x, y, weights, guess, siga, yfit)

    return guess, siga, yfit


def plot_gauss(xs, ys, colours, lines, markers, labels):



    # set up graph
    fig, frame = plt.subplots(ncols=1, nrows=1)
    # plot
    for it in range(len(xs)):

        if it>0:
            xfit = np.linspace(np.min(xs), np.max(xs), 10000)
            yfit = gauss_function(xfit, *ys[it])
        else:
            xfit = xs[it]
            yfit = ys[it]
        frame.plot(xfit, yfit, color=colours[it],  ls=lines[it],
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


def guess_parameters1(x, y, weights):

    # set data less than or equal to 1 to 1
    ymask = y > 1
    y1 = np.where(ymask, y, np.ones_like(y))
    logy = np.log(y1)
    # normalise
    xn = (x - x[0])/(x[-1] - x[0])
    # polyfit (weighted)
    p = np.polyfit(xn, logy, 2, w=np.sqrt(weights * y**2))[::-1]
    # work out guess parameters
    tmp = np.zeros(4, dtype=float)
    tmp[0] = -1 * p[1]/(2 * p[2])
    tmp[1] = np.sqrt(-1/(2*p[2]))
    tmp[2] = np.exp(tmp[0]**2/(2 * tmp[1]**2)) + p[0]
    # set up guess
    guess = np.array([tmp[2], tmp[0], tmp[1], 0.0])

    # return guess
    return guess


def guess_parameters2(x, y, weights):

    mod = GaussianModel()
    params = mod.guess(y, x=x)

    guess = np.array([params['height'].value,
                      params['center'].value,
                      params['sigma'].value,
                      0.0])

    return guess


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Generate a Gaussian with noise
    x_in = np.linspace(MIN_X, MAX_X, NUM_POINTS)
    noise = np.random.uniform(0, MAX_NOISE, size=NUM_POINTS)
    y_in = gauss_function(x_in, *INPUT_PARAMS) + noise
    w_in = 1.0 / (y_in + CCD_RON ** 2)
    guess1 = guess_parameters1(x_in, y_in, w_in)
    guess2 = guess_parameters2(x_in, y_in, w_in)

    guess = np.array(guess2)

    # ----------------------------------------------------------------------
    # Fit 1: fitgauss fortran
    time1 = time.time()
    c1, e1, y_out1 = fitgaussian_fortran(x_in, y_in, w_in, guess)

    # Fit 2: fitgauss scipy curve fit
    time2 = time.time()
    c2, e2, y_out2 = fitgaussian_python(x_in, y_in, w_in, guess)

    # Fit 3: fitguass lmfit
    time3 = time.time()
    c3, e3, y_out3 = fitgaussian_lmfit(x_in, y_in, w_in, guess)
    time4 = time.time()


    # print times
    print('fitgaussian_fortran = {0:.4e} s'.format(time2 - time1))
    print('fitgaussian_python = {0:.4e} s'.format(time3 - time2))
    print('fitgaussian_lmfit = {0:.4e} s'.format(time4 - time3))

    # ----------------------------------------------------------------------
    # plot the results
    x_all = [x_in, x_in, x_in, x_in]
    y_all = [y_in, c1, c2, c3]
    linecolours = ['k', 'b', 'r', 'g']
    linestyles = ['None', '-', '-', '-']
    linemarkers = ['x', None, None, None]
    names = ['input', 'FORTRAN', 'scipy.curve_fit', 'LMFIT']

    plot_gauss(x_all, y_all, linecolours, linestyles, linemarkers, names)
    # ----------------------------------------------------------------------
    # plot the residuals
    x_all = [x_in, x_in, x_in]
    y_all = [y_out1, y_out2, y_out3]
    names = ['FORTRAN', 'scipy.curve_fit', 'LMFIT']

    plot_res(x_all, y_all, names)

    plt.show()
    plt.close()


# =============================================================================
# End of code
# =============================================================================
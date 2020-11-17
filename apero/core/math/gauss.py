#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 12:24

@author: cook
"""
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chisquare
from typing import Any, Tuple, Union
import warnings

from apero.base import base
from apero.core.core import drs_misc
from apero.core.math import general
from apero.core.math import fast

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.math.gauss.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get display func
display_func = drs_misc.display_func

# =============================================================================
# Define complex typing
# =============================================================================
# For: gaussian_function_nn
GFNTypes = Tuple[np.ndarray, np.ndarray]
# For: fit_gauss_with_slope
FGSTypes = Union[Tuple[Any, Any, np.ndarray], Tuple[Any, Any]]
# For: fitgaussian
FGTypes = Union[Tuple[Any, np.ndarray, np.ndarray], Tuple[Any, np.ndarray], Any]


# =============================================================================
# Gaussian function
# =============================================================================
def gauss_function(x: Union[float, np.ndarray], a: float, x0: float,
                   sigma: float, dc: float) -> Union[float, np.ndarray]:
    """
    A standard 1D gaussian function (for fitting against)

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian
    :param dc: float, the constant level below the gaussian

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    # set function name
    _ = display_func(None, 'gauss_function', __NAME__)
    # return gauss function
    return a * np.exp(-0.5 * ((x - x0) / sigma) ** 2) + dc


def gauss_function_nodc(x: Union[float, np.ndarray], a: float, x0: float,
                        sigma: float) -> Union[float, np.ndarray]:
    """
    A standard 1D gaussian function (for fitting against) without a dc
    parameter

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    # set function name
    _ = display_func(None, 'gauss_function_nodc', __NAME__)
    # return gauss function
    return a * np.exp(-0.5 * ((x - x0) / sigma) ** 2)


def gauss_beta_function(x: Union[float, np.ndarray], a: float, x0: float,
                        sigma: float, dc: float,
                        beta: float) -> Union[float, np.ndarray]:
    """
    A 1D gaussian function with beta power (for fitting against)

    :param x: numpy array (1D), the x data points
    :param a: float, the amplitude
    :param x0: float, the mean of the gaussian
    :param sigma: float, the standard deviation (FWHM) of the gaussian
    :param dc: float, the constant level below the gaussian
    :param beta: float, the power the (x-x0)/sigma is raised to (in a normal
                 gaussian beta=2)

    :return gauss: numpy array (1D), size = len(x), the output gaussian
    """
    # set function name
    _ = display_func(None, 'gauss_beta_function', __NAME__)
    # return gauss function
    return a * np.exp(-0.5 * np.abs((x - x0) / sigma) ** beta) + dc


def gaussian_function_nn(x: Union[list, np.ndarray],
                         a: Union[list, np.ndarray]) -> GFNTypes:
    """
    Generate a Gaussian and return its derivaties

    translated from IDL'S gaussfit function
    parts of the comments from the IDL version of the code:

    # NAME:
    #   GAUSS_FUNCT
    #
    # PURPOSE:
    #   EVALUATE THE SUM OF A GAUSSIAN AND A 2ND ORDER POLYNOMIAL
    #   AND OPTIONALLY RETURN THE VALUE OF IT'S PARTIAL DERIVATIVES.
    #   NORMALLY, THIS FUNCTION IS USED BY CURVEFIT TO FIT THE
    #   SUM OF A LINE AND A VARYING BACKGROUND TO ACTUAL DATA.
    #
    # CATEGORY:
    #   E2 - CURVE AND SURFACE FITTING.
    # CALLING SEQUENCE:
    #   FUNCT,X,A,F,PDER
    # INPUTS:
    #   X = VALUES OF INDEPENDENT VARIABLE.
    #   A = PARAMETERS OF EQUATION DESCRIBED BELOW.
    # OUTPUTS:
    #   F = VALUE OF FUNCTION AT EACH X(I).
    #   PDER = matrix with the partial derivatives for function fitting
    #
    # PROCEDURE:
    #   F = A(0)*EXP(-Z^2/2) + A(3) + A(4)*X + A(5)*X^2
    #   Z = (X-A(1))/A(2)
    #   Elements beyond A(2) are optional.


    :param x: numpy array (1D), values of the independent variable
    :param a: list, parameters of equation described above (in F and Z)

    :return fout: numpy array (1D), the gaussian fit
    :return pder: numpy array (1D), the gaussian fit derivatives
    """
    # set function name
    _ = display_func(None, 'gaussian_function_nn', __NAME__)
    # get the dimensions
    n, nx = len(a), len(x)
    # work out gaussian
    z = (x - a[1]) / a[2]
    ez = np.exp(-z ** 2 / 2.0)
    # deal with options
    if n == 3:
        fout = a[0] * ez
    elif n == 4:
        fout = (a[0] * ez) + a[3]
    elif n == 5:
        fout = (a[0] * ez) + a[3] + (a[4] * x)
    elif n == 5:
        fout = (a[0] * ez) + a[3] + (a[4] * x) + (a[5] * x ** 2)
    else:
        emsg = 'Dimensions of "a" not supposed. len(a) must be 3, 4, 5 or 6'
        raise ValueError(emsg)
    # work out derivatives
    pder = np.zeros([nx, n])
    pder[:, 0] = ez  # compute partials
    pder[:, 1] = a[0] * ez * z / a[2]
    pder[:, 2] = pder[:, 1] * z
    if n > 3:
        pder[:, 3] = 1.0
    if n > 4:
        pder[:, 4] = x
    if n > 5:
        pder[:, 5] = x ** 2
    # return fout and pder
    return fout, pder


def gauss_fit_nn(xpix: np.ndarray, ypix: np.ndarray,
                 nn: int) -> Tuple[list, np.ndarray]:
    """
    fits a Gaussian function to xpix and ypix without prior knowledge of
    parameters

    The gaussians are expected to have their peaks within the min/max range
    of xpix and are expected to be reasonably close to Nyquist-sampled
    nn must be an INT in the range between 3 and 6

    :param xpix: numpy array (1D), the x position values (dependent values)
    :param ypix: numpy array (1D), the y position values (fit values)
    :param nn: int, fit mode:

        nn=3 -> the Gaussian has a floor of 0, the output will have 3 elements
        nn=4 -> the Gaussian has a floor that is non-zero
        nn=5 -> the Gaussian has a slope
        nn=6 -> the Guassian has a 2nd order polynomial floor

    :return stats: list, depending on nn

        nn=3 -> [amplitude , center of peak, amplitude of peak]
        nn=4 -> [amplitude , center of peak, amplitude of peak, dc level]
        nn=5 -> [amplitude , center of peak, amplitude of peak, dc level,
                 slope]
        nn=6 -> [amplitude , center of peak, amplitude of peak, dc level,
                 slope, 2nd order term]

    :return gfit: numpy array (1D), the fitted gaussian
    """
    # set function name
    func_name = display_func(None, 'gauss_fit_slope', __NAME__)
    # we guess that the Gaussian is close to Nyquist and has a
    # 2 PIX FWHM and therefore 2/2.54 e-width
    ew_guess = 2 * fast.nanmedian(np.gradient(xpix)) / general.fwhm()

    if nn == 3:
        # only amp, cen and ew
        a0 = [fast.nanmax(ypix) - fast.nanmin(ypix),
              xpix[fast.nanargmax(ypix)], ew_guess]
    elif nn == 4:
        # only amp, cen, ew, dc offset
        a0 = [fast.nanmax(ypix) - fast.nanmin(ypix),
              xpix[fast.nanargmax(ypix)], ew_guess, fast.nanmin(ypix)]
    elif nn == 5:
        # only amp, cen, ew, dc offset, slope
        a0 = [fast.nanmax(ypix) - fast.nanmin(ypix),
              xpix[fast.nanargmax(ypix)], ew_guess, fast.nanmin(ypix), 0]
    elif nn == 6:
        # only amp, cen, ew, dc offset, slope, curvature
        a0 = [fast.nanmax(ypix) - fast.nanmin(ypix),
              xpix[fast.nanargmax(ypix)], ew_guess, fast.nanmin(ypix), 0, 0]
    else:
        emsg = 'nn must be 3, 4, 5 or 6 only. ({0})'
        raise ValueError(emsg.format(func_name))
    # copy the ypix (rediual from previous)
    residu_prev = np.array(ypix)
    # fit a gaussian (with nn options)
    gfit, pder = gaussian_function_nn(xpix, a0)
    # set the RMS and number of iterations
    rms = 99
    n_it = 0
    # loops for 20 iterations MAX or an RMS with an RMS change in residual
    #     smaller than 1e-6 of peak
    while (rms > 1e-6) & (n_it <= 20):
        # calculate fit
        gfit, pder = gaussian_function_nn(xpix, a0)
        # work out residuals
        residu = ypix - gfit
        # work out amplitudes and residual fit
        amps, fit = general.linear_minimization(residu, pder)

        # add to the amplitudes
        a0 += amps
        # recalculate rms
        rdiff = fast.nanmax(ypix) - fast.nanmin(ypix)
        # check for nans
        if np.sum(np.isfinite(residu)) == 0:
            rms = np.nan
        else:
            rms = fast.nanstd(residu - residu_prev) / rdiff
        # set the previous residual to the new one
        residu_prev = np.array(residu)
        # add to iteration
        n_it += 1
    # return a0 and gfit
    return a0, gfit


def gauss_fit_s(x: Union[float, np.ndarray], a: float, x0: float, sigma: float,
                zp: float, slope: float) -> Union[float, np.ndarray]:
    """
    Gaussian fit with a slope

    :param x: numpy array (1D), the x values for the gauss fit
    :param a: float, the amplitude
    :param x0: float, the mean position
    :param sigma: float, the FWHM
    :param zp: float, the dc level
    :param slope: float, the float (x-x0) * slope

    :return: np.ndarray - the gaussian value with slope correction
    """
    # set function name
    _ = display_func(None, 'gauss_fit_s', __NAME__)
    # calculate gaussian
    gauss = a * np.exp(-0.5 * (x - x0) ** 2 / (sigma ** 2)) + zp
    correction = (x - x0) * slope
    return gauss + correction


def fit_gauss_with_slope(x: np.ndarray, y: np.ndarray,
                         guess: Union[list, np.ndarray],
                         return_fit: bool = False) -> FGSTypes:
    """
    Fit a guessian with a slope (given an input x and y data and a guess
    guess in the form [amplitude, mean position, FWHM, DC, slope]

    :param x: numpy array (1D), the x values for the gauss fit
    :param y: numpy array (1D), the y values for the gauss fit
    :param guess: list, first guess at the fit in form:
                    in the form [amplitude, mean position, FWHM, DC, slope]
    :param return_fit: bool, if True returns the git
    :return: return the fit coefficients, covarience matrix and if return_fit
             is True return the best fit y values for the given x values
    """
    # set function name
    _ = display_func(None, 'fit_gauss_with_slope', __NAME__)
    # produce curve_fit using gauss_fit_s function
    with warnings.catch_warnings(record=True) as _:
        popt, pcov = curve_fit(gauss_fit_s, x, y, p0=guess)
    # if we want fit return it
    if return_fit:
        return popt, pcov, gauss_fit_s(x, *popt)
    # else just return the coefficients and the covariance
    else:
        return popt, pcov


def fitgaussian(x: np.ndarray, y: np.ndarray,
                weights: Union[np.ndarray, None] = None,
                guess: Union[list, np.ndarray, None] = None,
                return_fit: bool = True,
                return_uncertainties: bool = False) -> FGTypes:
    """
    Fit a single gaussian to the data "y" at positions "x", points can be
    weighted by "weights" and an initial guess for the gaussian parameters

    :param x: numpy array (1D), the x values for the gaussian
    :param y: numpy array (1D), the y values for the gaussian
    :param weights: numpy array (1D), the weights for each y value
    :param guess: list of floats, the initial guess for the guassian fit
                  parameters in the following order:

                  [amplitude, center, fwhm, offset from 0 (in y-direction)]

    :param return_fit: bool, if True also calculates the fit values for x
                       i.e. yfit = gauss_function(x, *pfit)

    :param return_uncertainties: bool, if True also calculates the uncertainties
                                 based on the covariance matrix (pcov)
                                 uncertainties = np.sqrt(np.diag(pcov))

    :return pfit: numpy array (1D), the fit parameters in the
                  following order:

                [amplitude, center, fwhm, offset from 0 (in y-direction)]

    :return yfit: numpy array (1D), the fit y values, i.e. the gaussian values
                  for the fit parameters, only returned if return_fit = True
    """
    # set function name
    _ = display_func(None, 'fitgaussian', __NAME__)
    # if we don't have weights set them to be all equally weighted
    if weights is None:
        weights = np.ones(len(x))
    weights = 1.0 / weights
    # if we aren't provided a guess, make one
    if guess is None:
        guess = [fast.nanmax(y), fast.nanmean(y), fast.nanstd(y), 0]
    # calculate the fit using curve_fit to the function "gauss_function"
    with warnings.catch_warnings(record=True) as _:
        pfit, pcov = curve_fit(gauss_function, x, y, p0=guess, sigma=weights,
                               absolute_sigma=True)
    if return_fit and return_uncertainties:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # work out the normalisation constant
        chis, _ = chisquare(y, f_exp=yfit)
        norm = chis / (len(y) - len(guess))
        # calculate the fit uncertainties based on pcov
        efit = np.sqrt(np.diag(pcov)) * np.sqrt(norm)
        # return pfit, yfit and efit
        return pfit, yfit, efit
    # if just return fit
    elif return_fit:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # return pfit and yfit
        return pfit, yfit
    # if return uncertainties
    elif return_uncertainties:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        # work out the normalisation constant
        chis, _ = chisquare(y, f_exp=yfit)
        norm = chis / (len(y) - len(guess))
        # calculate the fit uncertainties based on pcov
        efit = np.sqrt(np.diag(pcov)) * np.sqrt(norm)
        # return pfit and efit
        return pfit, efit
    # else just return the pfit
    else:
        # return pfit
        return pfit


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

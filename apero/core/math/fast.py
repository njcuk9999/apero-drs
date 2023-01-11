#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO fast math functions

Usually replacing a defined numpy function

Created on 2019-09-18 at 10:53

@author: cook
"""
from typing import Tuple, Union

import numpy as np
from scipy import signal

from apero.base import base

# try to import bottleneck module
# noinspection PyBroadException
try:
    import bottleneck as bn

    HAS_BOTTLENECK = True
except Exception as e:
    HAS_BOTTLENECK = False
# try to import numba module
# noinspection PyBroadException
try:
    from numba import jit

    HAS_NUMBA = True
except Exception as _:
    jit = None
    HAS_NUMBA = False

# try to import numexpr
# noinspection PyBroadException
try:
    import numexpr as ne
    HAS_NUMEXPR = True
except Exception as _:
    ne = None
    HAS_NUMEXPR = False


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.math.fast.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# alias to non changed nan functions
nanpercentile = np.nanpercentile


# =============================================================================
# Define functions
# =============================================================================
def nanargmax(a: Union[list, np.ndarray],
              axis: Union[None, int, Tuple[int]] = None
              ) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of nanargmax depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.

    :type a: np.ndarray
    :type axis: int

    :return: the argument maximum of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nanargmax', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK:
        # return bottleneck function
        return bn.nanargmax(a, axis=axis)
    else:
        # return numpy function
        return np.nanargmax(a, axis=axis)


def nanargmin(a: Union[list, np.ndarray],
              axis: Union[None, int, Tuple[int]] = None
              ) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of nanargmin depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.

    :type a: np.ndarray
    :type axis: int

    :return: the argument minimum of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nanargmin', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK:
        # return bottleneck function
        return bn.nanargmin(a, axis=axis)
    else:
        # return numpy function
        return np.nanargmin(a, axis=axis)


def nanmax(a: Union[list, np.ndarray],
           axis: Union[None, int, Tuple[int]] = None,
           **kwargs) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of nanmax depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.
    :param kwargs: keyword arguments passed to numpy function only

    :type a: np.ndarray
    :type axis: int

    :return: the maximum of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nanmax', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK and len(kwargs) == 0:
        # return bottleneck function
        return bn.nanmax(a, axis=axis)
    else:
        # return numpy function
        return np.nanmax(a, axis=axis, **kwargs)


def nanmin(a: Union[list, np.ndarray],
           axis: Union[None, int, Tuple[int]] = None,
           **kwargs) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of nanmin depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.
    :param kwargs: keyword arguments passed to numpy function only

    :type a: np.ndarray
    :type axis: int

    :return: the minimum of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nanmin', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK and len(kwargs) == 0:
        # return bottleneck function
        return bn.nanmin(a, axis=axis)
    else:
        # return numpy function
        return np.nanmin(a, axis=axis, **kwargs)


def nanmean(a: Union[list, np.ndarray],
            axis: Union[None, int, Tuple[int]] = None,
            **kwargs) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of nanmean depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.
    :param kwargs: keyword arguments passed to numpy function only

    :type a: np.ndarray
    :type axis: int

    :return: the mean of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nanmin', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK and len(kwargs) == 0:
        # return bottleneck function
        return bn.nanmean(a, axis=axis)
    else:
        # return numpy function
        return np.nanmean(a, axis=axis, **kwargs)


def nanmedian(a: Union[list, np.ndarray],
              axis: Union[None, int, Tuple[int]] = None,
              **kwargs) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of nanmedian depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.
    :param kwargs: keyword arguments passed to numpy function only

    :type a: np.ndarray
    :type axis: int

    :return: the median of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nanmedian', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK and len(kwargs) == 0:
        # return bottleneck function
        return bn.nanmedian(a, axis=axis)
    else:
        # return numpy function
        return np.nanmedian(a, axis=axis, **kwargs)


def nanstd(a: Union[list, np.ndarray],
           axis: Union[None, int, Tuple[int]] = None, ddof: int = 0,
           **kwargs) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of nanstd depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.
    :param ddof: int, optional. Means Delta Degrees of Freedom. The divisor
                 used in calculations is ``N - ddof``, where ``N`` represents
                 the number of non-NaN elements. By default `ddof` is zero.
    :param kwargs: keyword arguments passed to numpy function only

    :type a: np.ndarray
    :type axis: int
    :type ddof: int

    :return: the standard deviation of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nanstd', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK and len(kwargs) == 0:
        # return bottleneck function
        return bn.nanstd(a, axis=axis, ddof=ddof)
    else:
        # return numpy function
        return np.nanstd(a, axis=axis, ddof=ddof, **kwargs)


def nansum(a: Union[list, np.ndarray],
           axis: Union[None, int, Tuple[int]] = None,
           **kwargs) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of nansum depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.
    :param kwargs: keyword arguments passed to numpy function only

    :type a: np.ndarray
    :type axis: int

    :return: the sum of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nansum', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK and len(kwargs) == 0:
        # make sure vector a is an array
        if not isinstance(a, np.ndarray):
            a1 = np.array(a)
        else:
            a1 = a
        # bottle neck return in type given for bool array this is not
        #  what we want
        if a1.dtype == bool:
            a1 = a1.astype(int)
        # return bottleneck function
        return bn.nansum(a1, axis=axis)
    else:
        # return numpy function
        return np.nansum(a, axis=axis, **kwargs)


def median(a: Union[list, np.ndarray],
           axis: Union[None, int, Tuple[int]] = None,
           **kwargs) -> Union[int, float, np.ndarray]:
    """
    Bottleneck or numpy implementation of median depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param axis: {int, None}, optional, Axis along which the median is computed.
                 The default (axis=None) is to compute the median of the
                 flattened array.
    :param kwargs: keyword arguments passed to numpy function only

    :type a: np.ndarray
    :type axis: int

    :return: the median of array `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('nansum', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK and len(kwargs) == 0:
        # return bottleneck function
        return bn.median(a, axis=axis)
    else:
        # return numpy function
        return np.median(a, axis=axis, **kwargs)


def medfilt_1d(a: Union[list, np.ndarray],
               window: Union[None, int] = None) -> np.ndarray:
    """
    Bottleneck or scipy.signal implementation of medfilt depending on imports

    :param a: numpy array, Input array. If `a` is not an array, a conversion
              is attempted.
    :param window: int, The number of elements in the moving window.

    :type a: np.ndarray
    :type window: int

    :return: the 1D median filtered array of `a` (int, float or np.ndarray)
    """
    # set function name
    # _ = display_func('medfilt_1d', __NAME__)
    # check bottleneck functionality
    if HAS_BOTTLENECK:
        # get half window size
        half_window = window // 2
        # need to shift
        a1 = np.append(a, [np.nan] * half_window)
        # median filter (via bottleneck function)
        y = bn.move_median(a1, window=window, min_count=half_window)
        # return shifted bottleneck function
        return y[half_window:]
    else:
        # return scipy function
        return signal.medfilt(a, kernel_size=window)


# =============================================================================
# numba functions
# =============================================================================
# must catch if we do not have the jit decorator and define our own
if not HAS_NUMBA:
    def jit(**options):
        """
        Proxy jit class - used to replace jit when no jit from numba is
        available - decorator just returns original function

        :param options: any options that were to be used as part of the
               decorator

        :return: decorator function
        """
        # don't use options but they are required to match jit definition
        _ = options

        # define decorator
        def decorator(func):
            # define wrapper
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            # return wrapper
            return wrapper
        # return decorator
        return decorator


# Set "nopython" mode for best performance, equivalent to @nji
@jit(nopython=True, fastmath=False)
def lin_mini(vector: np.ndarray, sample: np.ndarray, mm: np.ndarray,
             v: np.ndarray, sz_sample: Tuple[int], case: int,
             recon: np.ndarray, amps: np.ndarray,
             no_recon: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """
    Linear minimization of sample with vector

    Used internally in math.genearl.linear_minimization - you probably should
    use the linear_minization function instead of this directly

    :param vector: vector of N elements
    :param sample: sample: matrix N * M each M column is adjusted in
                   amplitude to minimize the chi2 according to the input vector
    :param mm: zero filled vector for filling size = M
    :param v: zero filled vector for filling size = M
    :param sz_sample: tuple the shape of the sample (N, M)
    :param case: int, if case = 1 then vector.shape[0] = sample.shape[1],
                 if case = 2 vector.shape[0] = sample.shape[0]
    :param recon: zero filled vector size = N, recon output
    :param amps: zero filled vector size = M, amplitudes output
    :param no_recon: boolean if True does not calculate recon
                     (output = input for recon)

    :returns: amps, recon
    """
    # do not set function name here -- cannot use functions here
    # case 1
    if case == 1:
        # fill-in the co-variance matrix
        for i in range(sz_sample[0]):
            for j in range(i, sz_sample[0]):
                mm[i, j] = np.sum(sample[i, :] * sample[j, :])
                # we know the matrix is symetric, we fill the other half
                # of the diagonal directly
                mm[j, i] = mm[i, j]
            # dot-product of vector with sample columns
            v[i] = np.sum(vector * sample[i, :])
        # if the matrix cannot we inverted because the determinant is zero,
        # then we return a NaN for all outputs
        if np.linalg.det(mm) == 0:
            amps = np.zeros(sz_sample[0]) + np.nan
            recon = np.zeros_like(v)
            return amps, recon
        # invert coveriance matrix
        inv = np.linalg.inv(mm)
        # retrieve amplitudes
        for i in range(len(v)):
            for j in range(len(v)):
                amps[i] += inv[i, j] * v[j]
        # reconstruction of the best-fit from the input sample and derived
        # amplitudes
        if not no_recon:
            for i in range(sz_sample[0]):
                recon += amps[i] * sample[i, :]
        return amps, recon
    # same as for case 1 but with axis flipped
    if case == 2:
        # fill-in the co-variance matrix
        for i in range(sz_sample[1]):
            for j in range(i, sz_sample[1]):
                mm[i, j] = np.sum(sample[:, i] * sample[:, j])
                # we know the matrix is symetric, we fill the other half
                # of the diagonal directly
                mm[j, i] = mm[i, j]
            # dot-product of vector with sample columns
            v[i] = np.sum(vector * sample[:, i])
        # if the matrix cannot we inverted because the determinant is zero,
        # then we return a NaN for all outputs
        if np.linalg.det(mm) == 0:
            return amps, recon
        # invert coveriance matrix
        inv = np.linalg.inv(mm)
        # retrieve amplitudes
        for i in range(len(v)):
            for j in range(len(v)):
                amps[i] += inv[i, j] * v[j]
        # reconstruction of the best-fit from the input sample and derived
        # amplitudes
        if not no_recon:
            for i in range(sz_sample[1]):
                recon += amps[i] * sample[:, i]
        return amps, recon


# Set "nopython" mode for best performance, equivalent to @nji
@jit(nopython=True, fastmath=False)
def odd_ratio_mean(value: np.ndarray, error: np.ndarray,
                   odd_ratio: float = 2e-4, nmax: int = 10,
                   conv_cut=1e-2) -> Tuple[float, float]:
    """
    Provide values and corresponding errors and compute a weighted mean

    :param value: np.array (1D), value array
    :param error: np.array (1D), uncertainties for value array
    :param odd_ratio: float, the probability that the point is bad
                    Recommended value in Artigau et al. 2021 : f0 = 0.002
    :param nmax: int, maximum number of iterations to pass through
    :param conv_cut: float, the convergence cut criteria - how precise we have
                     to get

    :return: tuple, 1. the weighted mean, 2. the error on weighted mean
    """
    # deal with NaNs in value or error
    keep = np.isfinite(value) & np.isfinite(error)
    # deal with no finite values
    if np.sum(keep) == 0:
        return np.nan, np.nan
    # remove NaNs from arrays
    value, error = value[keep], error[keep]
    # work out some values to speed up loop
    error2 = error ** 2
    # placeholders for the "while" below
    guess_prev = np.inf
    # the 'guess' must be started as close as we possibly can to the actual
    # value. Starting beyond ~3 sigma (or whatever the odd_ratio implies)
    # would lead to the rejection of pretty much all points and would
    # completely mess the convergence of the loop
    guess = np.nanmedian(value)
    bulk_error = 1.0
    ite = 0
    # loop around until we do all required iterations
    while (np.abs(guess - guess_prev) / bulk_error > conv_cut) and (ite < nmax):
        # store the previous guess
        guess_prev = float(guess)
        # model points as gaussian weighted by likelihood of being a valid point
        # nearly but not exactly one for low-sigma values
        gfit = (1 - odd_ratio) * np.exp(-0.5 * ((value - guess) ** 2 / error2))
        # find the probability that a point is bad
        odd_bad = odd_ratio / (gfit + odd_ratio)
        # find the probability that a point is good
        odd_good = 1 - odd_bad
        # calculate the weights based on the probability of being good
        weights = odd_good / error2
        # update the guess based on the weights
        if np.sum(np.isfinite(weights)) == 0:
            guess = np.nan
        else:
            guess = np.nansum(value * weights) / np.nansum(weights)
            # work out the bulk error
            bulk_error = np.sqrt(1.0 / np.nansum(odd_good / error2))
        # keep track of the number of iterations
        ite += 1

    # return the guess and bulk error
    return guess, bulk_error


# =============================================================================
# numexpr functions
# =============================================================================
def super_gauss_fast(xvector: np.ndarray, fwhm: np.ndarray, expo: np.ndarray):
    """
    Super gaussian using numexpr if possible

    ew = (fwhm/2)/(2*np.log(2))**(1/expo)
    supergauss = exp(-0.5*abs(xvector/ew_string)**expo)

    :param xvector: the xvector points to calculate the super gaussian from
    :param fwhm: np.ndarray, the full width half max value for the gaussian
                 at each pixel position
    :param expo: np.ndarray, the exponent of the super gaussian at each pixel
                 position

    :return: np.ndarray, the super gaussian profile for xvector, fwhm and expo
    """
    # if we have numexpr use it to do this fast
    if HAS_NUMEXPR:
        # do not need to reference these using numexpr
        _ = xvector, fwhm, expo
        # need to write as a string
        ew_string = '(fwhm/2)/(2*log(2))**(1/expo)'
        calc_string = f'exp(-0.5*abs(xvector/({ew_string}))**expo)'
        # evaluate string in numexpr
        return ne.evaluate(calc_string)
    # otherwise we fall back to the slow method
    else:
        ew = (fwhm/2)/(2*np.log(2))**(1/expo)
        return np.exp(-0.5*np.abs(xvector/ew)**expo)


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

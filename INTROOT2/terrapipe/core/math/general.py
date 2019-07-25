#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 12:24

@author: cook
"""
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
import warnings

from terrapipe.core import constants

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.math.general.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
PConstants = constants.pload(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']


# =============================================================================
# Define General functions
# =============================================================================
def measure_box_min_max(y, size):
    """
    Measure the minimum and maximum pixel value for each pixel using a box which
    surrounds that pixel by:  pixel-size to pixel+size.

    Edge pixels (0-->size and (len(y)-size)-->len(y) are
    set to the values for pixel=size and pixel=(len(y)-size)

    :param y: numpy array (1D), the image
    :param size: int, the half size of the box to use (half height)
                 so box is defined from  pixel-size to pixel+size

    :return min_image: numpy array (1D length = len(y)), the values
                       for minimum pixel defined by a box of pixel-size to
                       pixel+size for all columns
    :return max_image: numpy array (1D length = len(y)), the values
                       for maximum pixel defined by a box of pixel-size to
                       pixel+size for all columns
    """
    # get length of rows
    ny = y.shape[0]
    # Set up min and max arrays (length = number of rows)
    min_image = np.zeros(ny, dtype=float)
    max_image = np.zeros(ny, dtype=float)
    # loop around each pixel from "size" to length - "size" (non-edge pixels)
    # and get the minimum and maximum of each box
    for it in range(size, ny - size):
        min_image[it] = np.nanmin(y[it - size:it + size])
        max_image[it] = np.nanmax(y[it - size:it + size])

    # deal with leading edge --> set to value at size
    min_image[0:size] = min_image[size]
    max_image[0:size] = max_image[size]
    # deal with trailing edge --> set to value at (image.shape[0]-size-1)
    min_image[ny - size:] = min_image[ny - size - 1]
    max_image[ny - size:] = max_image[ny - size - 1]
    # return arrays for minimum and maximum (box smoothed)
    return min_image, max_image


def calculate_polyvals(coeffs, dim):
    """
    Calculates all fits in coeffs array across pixels of size=dim

    :param coeffs: coefficient array,
                   size = (number of orders x number of coefficients in fit)
                   output array will be size = (number of orders x dim)
    :param dim: int, number of pixels to calculate fit for
                fit will be done over x = 0 to dim in steps of 1
    :return yfits: array,
                   size = (number of orders x dim)
                   the fit for each order at each pixel values from 0 to dim
    """
    # create storage array
    yfits = np.zeros((len(coeffs), dim))
    # get pixel range for dimension
    xfit = np.arange(0, dim, 1)
    # loop around each fit and fit
    for j_it in range(len(coeffs)):
        yfits[j_it] = np.polyval(coeffs[j_it][::-1], xfit)
    # return fits
    return yfits


def fit2dpoly(x, y, z):
    # fit a 2nd order polynomial in 2d over x/y/z pixel points
    ones = np.ones_like(x)
    a = np.array([ones, x, y, x**2, y**2, x*y]).T
    b = z.flatten()
    # perform a least squares fit on a and b
    coeff, r, rank, s = np.linalg.lstsq(a, b,rcond=None)
    # return the coefficients
    return coeff


def fwhm(sigma=1.0):
    """
    Get the Full-width-half-maximum value from the sigma value (~2.3548)

    :param sigma: float, the sigma, default value is 1.0 (normalised gaussian)
    :return: 2 * sqrt(2 * log(2)) * sigma = 2.3548200450309493 * sigma
    """
    return 2 * np.sqrt(2 * np.log(2)) * sigma


# TODO: Required commenting and cleaning up
def linear_minimization(vector, sample):
    func_name = __NAME__ + '.linear_minimization()'

    vector = np.array(vector)
    sample = np.array(sample)
    sz_sample = sample.shape
    sz_vector = vector.shape

    if sz_vector[0] == sz_sample[0]:
        case = 2
    elif sz_vector[0] == sz_sample[1]:
        case = 1
    else:
        emsg = ('Neither vector[0]==sample[0] nor vector[0]==sample[1] '
                '(function = {0})')
        raise ValueError(emsg.format(func_name))

    # vector of N elements
    # sample: matrix N * M each M column is adjusted in amplitude to minimize
    # the chi2 according to the input vector
    # output: vector of length M gives the amplitude of each column

    if case == 1:
        # set up storage
        mm = np.zeros([sz_sample[0], sz_sample[0]])
        v = np.zeros(sz_sample[0])
        for i in range(sz_sample[0]):
            for j in range(i, sz_sample[0]):
                mm[i, j] = np.nansum(sample[i, :] * sample[j, :])
                mm[j, i] = mm[i, j]
            v[i] = np.nansum(vector * sample[i, :])

        if np.linalg.det(mm) == 0:
            amps = np.zeros(sz_sample[0]) + np.nan
            recon = np.zeros_like(v)
            return amps, recon

        amps = np.matmul(np.linalg.inv(mm), v)
        recon = np.zeros(sz_sample[1])
        for i in range(sz_sample[0]):
            recon += amps[i] * sample[i, :]
        return amps, recon

    if case == 2:
        # set up storage
        mm = np.zeros([sz_sample[1], sz_sample[1]])
        v = np.zeros(sz_sample[1])
        for i in range(sz_sample[1]):
            for j in range(i, sz_sample[1]):
                mm[i, j] = np.nansum(sample[:, i] * sample[:, j])
                mm[j, i] = mm[i, j]
            v[i] = np.nansum(vector * sample[:, i])

        if np.linalg.det(mm) == 0:
            amps = np.zeros(sz_sample[1]) + np.nan
            recon = np.zeros_like(v)
            return amps, recon

        amps = np.matmul(np.linalg.inv(mm), v)
        recon = np.zeros(sz_sample[0])
        for i in range(sz_sample[1]):
            recon += amps[i] * sample[:, i]
        return amps, recon


def iuv_spline(x, y, **kwargs):
    # check whether weights are set
    w = kwargs.get('w', None)
    # copy x and y
    x, y = np.array(x), np.array(y)
    # find all NaN values
    nanmask = ~np.isfinite(y)

    if np.sum(~nanmask) < 2:
        y = np.zeros_like(x)
    elif np.sum(nanmask) == 0:
        pass
    else:
        # replace all NaN's with linear interpolation
        badspline = InterpolatedUnivariateSpline(x[~nanmask], y[~nanmask],
                                                 k=1, ext=1)
        y[nanmask] = badspline(x[nanmask])
    # return spline
    return InterpolatedUnivariateSpline(x, y, **kwargs)


def median_filter_ea(vector, width):
    """
    Median filter array "vector" by a box of width "width"
    Note: uses nanmedian to median the boxes

    :param vector: numpy array (1D): the vector to median filter
    :param width: int, the size of the median box to apply

    :return vector2: numpy array (1D): same size as "vector" except the pixel
                     value is that of the median of box +/- width//2 of each
                     pixel
    """
    # construct an output vector filled with NaNs
    vector2 = np.zeros_like(vector) + np.nan
    # loop around pixel in vector
    for ix in range(len(vector)):
        # define a start and end of our median box
        start = ix - width // 2
        end = ix + width // 2
        # deal with boundaries
        if start < 0:
            start = 0
        if end > len(vector) - 1:
            end = len(vector) - 1
        # set the value of the new pixel equal to the median of the box of
        #   the original vector (and deal with NaNs)
        with warnings.catch_warnings(record=True) as _:
            vector2[ix] = np.nanmedian(vector[start:end])
    # return new vector
    return vector2


# =============================================================================
# Gaussian function
# =============================================================================
def gaussian_function_nn(x, a):
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


def gauss_fit_nn(xpix, ypix, nn):
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
    func_name = __NAME__ + '.gauss_fit_slope()'
    # we guess that the Gaussian is close to Nyquist and has a
    # 2 PIX FWHM and therefore 2/2.54 e-width
    ew_guess = 2 * np.nanmedian(np.gradient(xpix)) / fwhm()

    if nn == 3:
        # only amp, cen and ew
        a0 = [np.nanmax(ypix) - np.nanmin(ypix),
              xpix[np.nanargmax(ypix)], ew_guess]
    elif nn == 4:
        # only amp, cen, ew, dc offset
        a0 = [np.nanmax(ypix) - np.nanmin(ypix),
              xpix[np.nanargmax(ypix)], ew_guess, np.nanmin(ypix)]
    elif nn == 5:
        # only amp, cen, ew, dc offset, slope
        a0 = [np.nanmax(ypix) - np.nanmin(ypix),
              xpix[np.nanargmax(ypix)], ew_guess, np.nanmin(ypix), 0]
    elif nn == 6:
        # only amp, cen, ew, dc offset, slope, curvature
        a0 = [np.nanmax(ypix) - np.nanmin(ypix),
              xpix[np.nanargmax(ypix)], ew_guess, np.nanmin(ypix), 0, 0]
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
        amps, fit = linear_minimization(residu, pder)

        # add to the amplitudes
        a0 += amps
        # recalculate rms
        rdiff = np.nanmax(ypix) - np.nanmin(ypix)
        # check for nans
        if np.sum(np.isfinite(residu)) == 0:
            rms = np.nan
        else:
            rms = np.nanstd(residu - residu_prev) / rdiff
        # set the previous residual to the new one
        residu_prev = np.array(residu)
        # add to iteration
        n_it += 1
    # return a0 and gfit
    return a0, gfit


def gauss_fit_s(x, a, x0, sigma, zp, slope):
    gauss = a * np.exp(-0.5 * (x - x0) ** 2 / (sigma ** 2)) + zp
    # TODO: Question: Changed from (x - np.mean(x))
    correction = (x - x0) * slope
    return gauss + correction


# =============================================================================
# Define NaN functions
# =============================================================================
def nanpad(oimage):
    """
    Pads NaN values with the median (non NaN values from the 9 pixels around
    it) does this iteratively until no NaNs are left - if all 9 pixels are
    NaN - median is NaN

    :param oimage: numpy array (2D), the input image with NaNs
    :type oimage: np.ndarray

    :return: Nan-removed copy of original image
    :rtype: np.ndarray
    """
    image = np.array(oimage)
    # replace the NaNs on the edge with zeros
    image[:, 0] = killnan(image[:, 0], 0)
    image[0, :] = killnan(image[0, :], 0)
    image[:, -1] = killnan(image[:, -1], 0)
    image[-1, :] = killnan(image[-1, :], 0)
    # find x/y positions of NaNs
    gy, gx = np.where(~np.isfinite(image))
    # for each NaN, find the 8 neighbouring pixels and pad them
    # into an array that is 9xN.
    while len(gy) != 0:
        # array that contains neighbours to a given pixel along
        # the axis 1
        tmp = np.zeros([len(gy), 9])
        # pad the neighbour array
        for it in range(9):
            ypix = gy + (it // 3) - 1
            xpix = gx + (it % 3) - 1
            tmp[:, it] = image[ypix, xpix]
        # median the neghbours and pad back into the input image
        with warnings.catch_warnings(record=True) as _:
            image[gy, gx] = np.nanmedian(tmp, axis=1)
        # find NaNs again and pad again if needed
        gy, gx = np.where(~np.isfinite(image))
    # return padded image
    return image


def nanpolyfit(x, y, deg, **kwargs):
    # check if there is a weight input in kwargs
    if 'w' in kwargs:
        # find the NaNs in x, y, w
        nanmask = np.isfinite(y) & np.isfinite(x) & np.isfinite(kwargs['w'])
        # mask the weight in kwargs
        kwargs['w'] = kwargs['w'][nanmask]
    else:
        # find the NaNs in x and y
        nanmask = np.isfinite(y) & np.isfinite(x)
    # return polyfit without the nans
    return np.polyfit(x[nanmask], y[nanmask], deg, **kwargs)


def killnan(vect, val=0):
    mask = ~np.isfinite(vect)
    vect[mask] = val
    return vect



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

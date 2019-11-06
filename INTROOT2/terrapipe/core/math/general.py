#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 12:24

@author: cook
"""
import numpy as np
from astropy import constants as cc
from astropy import units as uu
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.interpolate import UnivariateSpline
import warnings
from scipy import stats

from terrapipe.core import constants
from terrapipe.core.math import fast
from terrapipe.core.math.exceptions import DrsMathException

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
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


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
        min_image[it] = fast.nanmin(y[it - size:it + size])
        max_image[it] = fast.nanmax(y[it - size:it + size])

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


def linear_minimization(vector, sample):
    """
    wrapper function that sets everything for the @jit later
    In particular, we avoid the np.zeros that are not handled
    by numba, size of input vectors and sample to be adjusted

    :param vector: 2d matrix that is N x M or M x N
    :param sample: 1d vector of length N
    :return:
    """
    # setup function name
    func_name = __NAME__ + '.linear_minimization()'

    sz_sample = sample.shape  # 1d vector of length N
    sz_vector = vector.shape  # 2d matrix that is N x M or M x N
    # define which way the sample is flipped relative to the input vector
    if sz_vector[0] == sz_sample[0]:
        case = 2
    elif sz_vector[0] == sz_sample[1]:
        case = 1
    else:
        emsg = ('Neither vector[0]==sample[0] nor vector[0]==sample[1] '
                '(function = {0})')
        print(emsg)
        raise ValueError(emsg.format(func_name))
    # ----------------------------------------------------------------------
    # Part A) we deal with NaNs
    # ----------------------------------------------------------------------
    # set up keep vector
    keep = None
    # we check if there are NaNs in the vector or the sample
    # if there are NaNs, we'll fit the rest of the domain
    isnan = (np.sum(np.isnan(vector)) != 0) or (np.sum(np.isnan(sample)) != 0)
    # ----------------------------------------------------------------------
    # case 1: sample is not flipped relative to the input vector
    if case == 1:
        if isnan:
            # we create a mask of non-NaN
            keep = np.isfinite(vector) * np.isfinite(np.sum(sample, axis=0))
            # redefine the input vector to avoid NaNs
            vector = vector[keep]
            sample = sample[:, keep]
            # re-find shapes
            sz_sample = sample.shape  # 1d vector of length N
        # matrix of covariances
        mm = np.zeros([sz_sample[0], sz_sample[0]])
        # cross-terms of vector and columns of sample
        vec = np.zeros(sz_sample[0])
        # reconstructed amplitudes
        amps = np.zeros(sz_sample[0])
        # reconstruted fit
        recon = np.zeros(sz_sample[1])
    # ----------------------------------------------------------------------
    # case 2: sample is flipped relative to the input vector
    elif case == 2:
        # same as for case 1, but with axis flipped
        if isnan:
            # we create a mask of non-NaN
            keep = np.isfinite(vector) * np.isfinite(np.sum(sample, axis=1))
            vector = vector[keep]
            sample = sample[keep, :]
            # re-find shapes
            sz_sample = sample.shape  # 1d vector of length N
        mm = np.zeros([sz_sample[1], sz_sample[1]])
        vec = np.zeros(sz_sample[1])
        amps = np.zeros(sz_sample[1])
        recon = np.zeros(sz_sample[0])
    # ----------------------------------------------------------------------
    # should not get here (so just repeat the raise from earlier)
    else:
        emsg = ('Neither vector[0]==sample[0] nor vector[0]==sample[1] '
                '(function = {0})')
        raise ValueError(emsg.format(func_name))

    # ----------------------------------------------------------------------
    # Part B) pass to optimized linear minimization
    # ----------------------------------------------------------------------
    # pass all variables and pre-formatted vectors to the @jit part of the code
    amp_out, recon_out = fast.lin_mini(vector, sample, mm, vec, sz_sample,
                                       case, recon, amps)
    # ----------------------------------------------------------------------
    # if we had NaNs in the first place, we create a reconstructed vector
    # that has the same size as the input vector, but pad with NaNs values
    # for which we cannot derive a value
    if isnan:
        recon_out2 = np.zeros_like(keep) + np.nan
        recon_out2[keep] = recon_out
        recon_out = recon_out2

    return amp_out, recon_out


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


def robust_polyfit(x, y, degree, nsigcut):
    keep = np.isfinite(y)
    # set the nsigmax to infinite
    nsigmax = np.inf
    # set the fit as unset at first
    fit = None
    # while sigma is greater than sigma cut keep fitting
    while nsigmax > nsigcut:
        # calculate the polynomial fit (of the non-NaNs)
        fit = np.polyfit(x[keep], y[keep], degree)
        # calculate the residuals of the polynomial fit
        res = y - np.polyval(fit, x)
        # work out the new sigma values
        nsig = np.abs(res) / np.nanmedian(np.abs(res))
        # work out the maximum sigma
        nsigmax = np.max(nsig[keep])
        # re-work out the keep criteria
        keep = nsig < nsigcut
    # return the fit and the mask of good values
    return fit, keep


def sinc(x, amp, period, lin_center, quad_scale, cube_scale, slope,
         peak_cut=0.0):
    """
    Calculates the sinc function with a slope (and position threshold cut)

    y = A * (sin(x)/x)^2 * (1 + C*x)

    x = 2*pi*(X - dx + q2*dx^2 + q3*dx^3) / P

    where X is a position along the x pixel axis. This assumes
    that the blaze follows an airy pattern and that there may be a slope
    to the spectral energy distribution.

    if peak_cut is non-zero:
        y < A * peak_cut = NaN

    :param x: numpy array (1D), the x position vector y (X)
    :param amp: float, the amplitude of the sinc function (A)
    :param period: float, the period of the sinc function (P)
    :param lin_center: float, the linear center of the sinc (dx)
    :param quad_scale: float, the quad scale of the sinc (q2)
    :param cube_scale: float, the cubic scale of the sinc (q3)
    :param slope: the slope of the sinc function (C)
    :param peak_cut: float, if non-zero if the threshold below the maximum
                     amplitude to set to NaNs

    :type x: np.ndarray
    :type amp: float
    :type period: float
    :type lin_center: float
    :type quad_scale: float
    :type cube_scale: float
    :type slope: float
    :type peak_cut: float

    :return: the sinc function (with a slope) and if peak_cut non-zero NaN
             filled before this fraction of the sinc max amplitude
    :rtype: np.ndarray
    """
    # Transform the x expressed in pixels into a stretched version
    # expressed in phase. The quadratic terms allows for a variation of
    # dispersion along the other
    deltax = x - lin_center
    cent = deltax + quad_scale * deltax ** 2 + cube_scale * deltax ** 3
    xp = 2 * np.pi * ((cent) / period)
    # this avoids a division by zero
    if np.min(np.abs(xp) / period) < 1e-9:
        small_x = (np.abs(xp) / period) < 1e-9
        xp[small_x] = 1e-9
    # calculate the sinc function
    yy = amp * (np.sin(xp) / xp) ** 2
    # if we set a peak_cut threshold then values below that fraction of the
    # peak sinc value are set to NaN.
    if peak_cut != 0:
        yy[yy < (peak_cut * amp)] = np.nan
    # multiplicative slope in the SED
    yy *= (1 + slope * (x - lin_center))
    # return the adjusted yy
    return yy


def sigfig(x, n):
    """
    Produces x values to "n" significant figures

    From : https://stackoverflow.com/a/55599055

    :param x: numpy array, the values to round
    :param n: int, the number of significant figures required
    :return:
    """

    if isinstance(x, np.ndarray):
        xin = np.array(x)
    elif isinstance(x, list):
        xin = np.array(x)
    else:
        xin = np.array([x])
    # filter out zeros
    mask = (xin != 0) & (np.isfinite(xin))
    # get the power and factor
    power = -(np.floor(np.log10(abs(xin[mask])))).astype(int) + (n - 1)
    factor = (10 ** power)
    # copy xin into mask
    xr = np.array(xin)
    # get sig fig
    xr[mask] = np.round(xin[mask] * factor) / factor
    # deal with return
    if isinstance(x, np.ndarray):
        return xr
    elif isinstance(x, list):
        return list(xr)
    else:
        return xr[0]


def continuum(x, y, binsize=200, overlap=100, sigmaclip=3.0, window=3,
              mode='median', use_linear_fit=False, excl_bands=None):
    """
    Function to detect and calculate continuum spectrum
    :param x: numpy array (1D), input x data
    :param y: numpy array (1D), input y data (x and y must be of the same size)
    :param binsize: int, number of points in each bin
    :param overlap: int, number of points to overlap with adjacent bins
    :param sigmaclip: int, number of times sigma to cut-off points
    :param window: int, number of bins to use in local fit
    :param mode: string, set combine mode, where mode accepts "median", "mean",
                 "max"
    :param use_linear_fit: bool, whether to use the linar fit
    :param excl_bands: list of pairs of float, list of wavelength ranges
                        ([wl0,wlf]) to exclude data for continuum detection

    :return continuum, xbin, ybin
        continuum: numpy array (1D) of the same size as input arrays containing
                   the continuum data already interpolated to the same points
                   as input data.
        xbin,ybin: numpy arrays (1D) containing the bins used to interpolate
                   data for obtaining the continuum
    """
    # deal with no excl_bands
    if excl_bands is None:
        excl_bands = []
    # ----------------------------------------------------------------------
    # set number of bins given the input array length and the bin size
    nbins = int(np.floor(len(x) / binsize))
    # ----------------------------------------------------------------------
    # initialize arrays to store binned data
    xbin, ybin = [], []
    # ----------------------------------------------------------------------
    # loop around bins
    for i in range(nbins):
        # get first and last index within the bin
        idx0 = i * binsize - overlap
        idxf = (i + 1) * binsize + overlap
        # if it reaches the edges then it reset the indexes
        if idx0 < 0:
            idx0 = 0
        if idxf >= len(x):
            idxf = len(x) - 1
        # ------------------------------------------------------------------
        # get data within the bin
        xbin_tmp = np.array(x[idx0:idxf])
        ybin_tmp = np.array(y[idx0:idxf])
        # create mask of exclusion bands
        excl_mask = np.full(np.shape(xbin_tmp), False, dtype=bool)
        for band in excl_bands:
            excl_mask += (xbin_tmp > band[0]) & (xbin_tmp < band[1])
        # -----------------------------------------------------------------
        # mask data within exclusion bands
        xtmp = xbin_tmp[~excl_mask]
        ytmp = ybin_tmp[~excl_mask]
        # create mask to get rid of NaNs
        nanmask = np.logical_not(np.isnan(ytmp))
        if len(xtmp[nanmask]) > 2:
            # calculate mean x within the bin
            xmean = np.nanmean(xtmp[nanmask])
            # calculate median y within the bin
            medy = np.nanmedian(ytmp[nanmask])

            # calculate median deviation
            medydev = np.nanmedian(np.abs(ytmp[nanmask] - medy))
            # create mask to filter data outside n*sigma range
            filtermask = (ytmp[nanmask] > medy) & (ytmp[nanmask] < medy +
                                                   sigmaclip * medydev)
            # --------------------------------------------------------------
            if len(ytmp[nanmask][filtermask]) > 2:
                # save mean x wihthin bin
                xbin.append(xmean)
                if mode == 'max':
                    # save maximum y of filtered data
                    ybin.append(fast.nanmax(ytmp[nanmask][filtermask]))
                elif mode == 'median':
                    # save median y of filtered data
                    ybin.append(fast.nanmedian(ytmp[nanmask][filtermask]))
                elif mode == 'mean':
                    # save mean y of filtered data
                    ybin.append(fast.nanmean(ytmp[nanmask][filtermask]))
                else:
                    emsg = 'Mode "{0}" is not recognised for continuum fit'
                    raise DrsMathException(emsg.format(mode))
    # ----------------------------------------------------------------------
    # Option to use a linearfit within a given window
    if use_linear_fit:
        # initialize arrays to store new bin data
        newxbin, newybin = [], []
        # append first point to avoid crazy behaviours in the edge
        newxbin.append(x[0])
        newybin.append(ybin[0])
        # -----------------------------------------------------------------
        # loop around bins to obtain a linear fit within a given window size
        for i in range(len(xbin)):
            # set first and last index to select bins within window
            idx0 = i - window
            idxf = i + 1 + window
            # make sure it doesnt go over the edges
            if idx0 < 0:
                idx0 = 0
            if idxf > nbins:
                idxf = nbins - 1
            # --------------------------------------------------------------
            # perform linear fit to these data
            slope, intercept, r_value, p_value, std_err = \
                stats.linregress(xbin[idx0:idxf], ybin[idx0:idxf])
            # --------------------------------------------------------------
            # save data obtained from the fit
            newxbin.append(xbin[i])
            newybin.append(intercept + slope * xbin[i])
        # ------------------------------------------------------------------
        xbin, ybin = newxbin, newybin
    # ----------------------------------------------------------------------
    # interpolate points applying an Spline to the bin data
    sfit = UnivariateSpline(xbin, ybin)
    sfit.set_smoothing_factor(0.5)
    # Resample interpolation to the original grid
    continuum_val = sfit(x)
    # return continuum and x and y bins
    return continuum_val, xbin, ybin


# =============================================================================
# Define wave functions
# =============================================================================
def get_ll_from_coefficients(pixel_shift_inter, pixel_shift_slope, allcoeffs,
                             nx, nbo):
    """
    Use the coefficient matrix "params" to construct fit values for each order
    (dimension 0 of coefficient matrix) for values of x from 0 to nx
    (interger steps)

    :param pixel_shift_inter: float, the intercept of a linear pixel shift
    :param pixel_shift_slope: float, the slope of a linear pixel shift

    :param allcoeffs: numpy array (2D), the coefficient matrix
                   size = (number of orders x number of fit coefficients)

    :param nx: int, the number of values and the maximum value of x to use
               the coefficients for, where x is such that

                yfit = p[0]*x**(N-1) + p[1]*x**(N-2) + ... + p[N-2]*x + p[N-1]

                N = number of fit coefficients
                and p is the coefficients for one order
                (i.e. params = [ p_1, p_2, p_3, p_4, p_5, ... p_nbo]

    :param nbo: int, the number of orders to use

    :return ll: numpy array (2D): the yfit values for each order
                (i.e. ll = [yfit_1, yfit_2, yfit_3, ..., yfit_nbo] )
    """
    # create x values
    xfit = np.arange(nx) + pixel_shift_inter + (
            pixel_shift_slope * np.arange(nx))
    # create empty line list storage
    ll = np.zeros((nbo, nx))
    # loop around orders
    for order_num in range(nbo):
        # get the coefficients for this order and flip them
        # (numpy needs them backwards)
        coeffs = allcoeffs[order_num][::-1]
        # get the y fit using the coefficients for this order and xfit
        yfit = np.polyval(coeffs, xfit)
        # add to line list storage
        ll[order_num, :] = yfit
    # return line list
    return ll


def get_ll_from_coefficients_cheb(pixel_shift_inter, pixel_shift_slope,
                                  allcoeffs, nx, nbo):
    """
    Use the coefficient matrix "params" to construct fit values for each order
    (dimension 0 of coefficient matrix) for values of x from 0 to nx
    (interger steps)

    :param pixel_shift_inter: float, the intercept of a linear pixel shift
    :param pixel_shift_slope: float, the slope of a linear pixel shift

    :param allcoeffs: numpy array (2D), the coefficient matrix
                   size = (number of orders x number of fit coefficients)

    :param nx: int, the number of values and the maximum value of x to use
               the coefficients for, where x is such that

                yfit = p[0]*x**(N-1) + p[1]*x**(N-2) + ... + p[N-2]*x + p[N-1]

                N = number of fit coefficients
                and p is the coefficients for one order
                (i.e. params = [ p_1, p_2, p_3, p_4, p_5, ... p_nbo]

    :param nbo: int, the number of orders to use

    :return ll: numpy array (2D): the yfit values for each order
                (i.e. ll = [yfit_1, yfit_2, yfit_3, ..., yfit_nbo] )
    """
    # create x values
    xfit = np.arange(nx) + pixel_shift_inter + (
            pixel_shift_slope * np.arange(nx))
    # create empty line list storage
    ll = np.zeros((nbo, nx))
    # loop around orders
    for order_num in range(nbo):
        # get the coefficients for this order and flip them
        # (numpy needs them backwards)
        coeffs = allcoeffs[order_num]
        # get the y fit using the coefficients for this order and xfit
        yfit = np.polynomial.chebyshev.chebval(xfit, coeffs)
        # add to line list storage
        ll[order_num, :] = yfit
    # return line list
    return ll


def get_dll_from_coefficients(allcoeffs, nx, nbo):
    """
    Derivative of the coefficients, using the coefficient matrix "params"
    to construct the derivative of the fit values for each order
    (dimension 0 of coefficient matrix) for values of x from 0 to nx
    (interger steps)

    :param allcoeffs: numpy array (2D), the coefficient matrix
                   size = (number of orders x number of fit coefficients)

    :param nx: int, the number of values and the maximum value of x to use
               the coefficients for, where x is such that

                yfit = p[0]*x**(N-1) + p[1]*x**(N-2) + ... + p[N-2]*x + p[N-1]

                dyfit = p[0]*(N-1)*x**(N-2) + p[1]*(N-2)*x**(N-3) + ... +
                        p[N-3]*x + p[N-2]

                N = number of fit coefficients
                and p is the coefficients for one order
                (i.e. params = [ p_1, p_2, p_3, p_4, p_5, ... p_nbo]

    :param nbo: int, the number of orders to use

    :return ll: numpy array (2D): the yfit values for each order
                (i.e. ll = [dyfit_1, dyfit_2, dyfit_3, ..., dyfit_nbo] )
    """

    # create x values
    xfit = np.arange(nx)
    # create empty line list storage
    ll = np.zeros((nbo, nx))
    # loop around orders
    for order_num in range(nbo):
        # get the coefficients for this order and flip them
        coeffs = allcoeffs[order_num]
        # get the y fit using the coefficients for this order and xfit
        yfiti = []
        # derivative =  (j)*(a_j)*x^(j-1)   where j = it + 1
        for it in range(len(coeffs) - 1):
            yfiti.append((it + 1) * coeffs[it + 1] * xfit ** it)
        yfit = fast.nansum(yfiti, axis=0)
        # add to line list storage
        ll[order_num, :] = yfit
    # return line list
    return ll


def relativistic_waveshift(dv, units='km/s'):
    """
    Relativistic offset in wavelength

    default is dv in km/s

    :param dv: float or numpy array, the dv values
    :param units: string or astropy units, the units of dv
    :return:
    """
    # get c in correct units
    # noinspection PyUnresolvedReferences
    if units == 'km/s' or units == uu.km/uu.s:
        c = speed_of_light
    # noinspection PyUnresolvedReferences
    elif units == 'm/s' or units == uu.m/uu.s:
        c = speed_of_light_ms
    else:
        raise ValueError("Wrong units for dv ({0})".format(units))
    # work out correction
    corrv = np.sqrt((1 + dv / c) / (1 - dv / c))
    # return correction
    return corrv


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

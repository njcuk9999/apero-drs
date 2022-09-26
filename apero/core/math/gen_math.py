#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO general math functionality

Created on 2019-05-15 at 12:24

@author: cook
"""
import copy
import numpy as np
from astropy import constants as cc
from astropy import units as uu
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.ndimage.morphology import binary_dilation
from scipy.special import erf, erfinv
from typing import Tuple, Union

from apero.base import base
from apero.core.core.drs_exceptions import DrsCodedException
from apero.core.math import fast

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.math.gen_math.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define General functions
# =============================================================================
def measure_box_min_max(y: np.ndarray,
                        size: int) -> Tuple[np.ndarray, np.ndarray]:
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
    # set function name
    # _ = display_func('measure_box_min_max', __NAME__)
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


def calculate_polyvals(coeffs: Union[list, np.ndarray],
                       dim: int) -> np.ndarray:
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
    # set function name
    # _ = display_func('calculate_polyvals', __NAME__)
    # create storage array
    yfits = np.zeros((len(coeffs), dim))
    # get pixel range for dimension
    xfit = np.arange(0, dim, 1)
    # loop around each fit and fit
    for j_it in range(len(coeffs)):
        yfits[j_it] = np.polyval(coeffs[j_it][::-1], xfit)
    # return fits
    return yfits


def ea_airy_function(x: np.ndarray, amp: float, x0: float, w: float,
                     beta: float, zp: float) -> np.ndarray:
    """
    Calculate dampened cosine with sharper positive peaks for high beta values
    Used to approximate a FP peak

    :param x: numpy array: the positions in x
    :param amp: the peak flux amplitude over the dc level (zp)
    :param x0: the central position of FP peak
    :param w: the period of the FP in pixel space
    :param beta: the exponent (shape factor)
    :param zp: the dc level
    :return:
    """
    # set function name
    # _ = display_func('calculate_polyvals', __NAME__)
    # airy function should always be an emission feature
    amp = abs(amp)
    # calculate ea_airy_function
    y = zp + amp * ((1 + np.cos(2 * np.pi * (x - x0) / w)) / 2.0) ** beta
    return y


def fit2dpoly(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    """
    Calculate the 2d polynomial (degree=2) over X, Y and Z

    :param x: np.ndarray (1D) the x axis positions
    :param y: np.ndarray (1D) the y axis positions
    :param z: np.ndarray (2D) the 2D points for each x and y position
    :return: the coefficients of the 2d polynomial fit
    """
    # set function name
    # _ = display_func('fit2dpoly', __NAME__)
    # fit a 2nd order polynomial in 2d over x/y/z pixel points
    ones = np.ones_like(x)
    a = np.array([ones, x, y, x ** 2, y ** 2, x * y]).T
    b = z.flatten()
    # perform a least squares fit on a and b
    coeff, r, rank, s = np.linalg.lstsq(a, b, rcond=None)
    # return the coefficients
    return coeff


def normal_fraction(sigma: Union[float, np.ndarray] = 1.0
                    ) -> Union[float, np.ndarray]:
    """
    Return the expected fraction of population inside a range
    (Assuming data is normally distributed)

    :param sigma: the number of sigma away from the median to be
    :return:
    """
    # set function name
    # _ = display_func('normal_fraction', __NAME__)
    # return error function
    return erf(sigma / np.sqrt(2.0))


def median_absolute_deviation(sigma: float = 1.0) -> float:
    """
    Calculate the median absolute deviation
    (From: https://en.wikipedia.org/wiki/Median_absolute_deviation)

    :param sigma: the number of sigma away from the median to be

    :return: float, the median absolute deviation
    """
    return sigma * np.sqrt(2) * erfinv(0.5)


def estimate_sigma(tmp: np.ndarray, sigma=1.0) -> float:
    """
    Return a robust estimate of N sigma away from the mean

    :param tmp: np.array (1D) - the data to estimate N sigma of
    :param sigma: int, number of sigma away from mean (default is 1)

    :return: the sigma value
    """
    # get formal definition of N sigma
    sig1 = normal_fraction(sigma)
    # get the 1 sigma as a percentile
    p1 = (1 - (1 - sig1) / 2) * 100
    # work out the lower and upper percentiles for 1 sigma
    upper = fast.nanpercentile(tmp, p1)
    lower = fast.nanpercentile(tmp, 100 - p1)
    # return the mean of these two bounds
    return (upper - lower) / 2.0


def fwhm(sigma: Union[float, np.ndarray] = 1.0) -> Union[float, np.ndarray]:
    """
    Get the Full-width-half-maximum value from the sigma value (~2.3548)

    :param sigma: float, the sigma, default value is 1.0 (normalised gaussian)
    :return: 2 * sqrt(2 * log(2)) * sigma = 2.3548200450309493 * sigma
    """
    # set function name
    # _ = display_func('fwhm', __NAME__)
    # return fwdm
    return 2 * np.sqrt(2 * np.log(2)) * sigma


def linear_minimization(vector: np.ndarray, sample: np.ndarray,
                        no_recon: bool = False
                        ) -> Tuple[np.ndarray, np.ndarray]:
    """
    wrapper function that sets everything for the @jit later
    In particular, we avoid the np.zeros that are not handled
    by numba, size of input vectors and sample to be adjusted

    :param vector: 2d matrix that is (N x M) or (M x N)
    :param sample: 1d vector of length N
    :param no_recon: bool, if True does not calculate recon
    :return:
    """
    # set function name
    func_name = __NAME__ + 'linear_minimization()'
    # get sample and vector shapes
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
                                       case, recon, amps, no_recon=no_recon)
    # ----------------------------------------------------------------------
    # if we had NaNs in the first place, we create a reconstructed vector
    # that has the same size as the input vector, but pad with NaNs values
    # for which we cannot derive a value
    if isnan:
        recon_out2 = np.zeros_like(keep) + np.nan
        recon_out2[keep] = recon_out
        recon_out = recon_out2

    return amp_out, recon_out


def get_magic_grid(wave0: float, wave1: float, dv_grid: float = 500):
    """
    magic grid is a standard way of representing a wavelength vector it is set
    so that each element is exactly dv_grid step in velocity. If you shift
    your velocity, then you have a simple translation of this vector.

    :param wave0: float, first wavelength element
    :param wave1: float, second wavelength element
    :param dv_grid: float, grid size in m/s
    :return:
    """
    # default for the function is 500 m/s
    # the arithmetic is a but confusing here, you first find how many
    # elements you have on your grid, then pass it to an exponential
    # the first element is exactely wave0, the last element is NOT
    # exactly wave1, but is very close and is set to get your exact
    # step in velocity
    # get the length of the magic vector
    logwaveratio = np.log(wave1 / wave0)
    len_magic = int(np.floor(logwaveratio * speed_of_light_ms / dv_grid))
    # need to update the final wavelength so we have exactly round steps
    wave1 = np.exp(len_magic * dv_grid / speed_of_light_ms) * wave0
    # redefining wave1 to have a round number of velocity bins
    logwaveratio = np.log(wave1 / wave0)
    # get the positions for "magic length"
    plen_magic = np.arange(len_magic)
    # define the magic grid to use in ccf
    magic_grid = np.exp((plen_magic / len_magic) * logwaveratio) * wave0
    # return the magic grid
    return magic_grid


class NanSpline:
    def __init__(self, emsg: str, x: Union[np.ndarray, None] = None,
                 y: Union[np.ndarray, None] = None, **kwargs):
        """
        This is used in place of scipy.interpolateInterpolatedUnivariateSpline
        (Any spline following this will return all NaNs)

        :param emsg: str, the error that means we have to use the NanSpline
        """
        self.emsg = str(emsg)
        self.x = copy.deepcopy(x)
        self.y = copy.deepcopy(y)
        self.kwargs = copy.deepcopy(kwargs)

    def __repr__(self) -> str:
        """
        String representation of the class

        :return: string representation
        """
        return 'NanSpline: \n' + self.emsg

    def __str__(self) -> str:
        """
        String representation of the class

        :return: string representation
        """
        return self.__repr__()

    def __call__(self, x: np.ndarray, nu: int = 0,
                 ext: Union[int, None] = None) -> np.ndarray:
        """
        Return a vector of NaNs (this means the spline failed due to
        less points

        This is used in place of scipy.interpolateInterpolatedUnivariateSpline

        Parameters
        ----------
        x : array_like
            A 1-D array of points at which to return the value of the smoothed
            spline or its derivatives. Note: x can be unordered but the
            evaluation is more efficient if x is (partially) ordered.
        nu  : int
            The order of derivative of the spline to compute.
        ext : int
            Controls the value returned for elements of ``x`` not in the
            interval defined by the knot sequence.

            * if ext=0 or 'extrapolate', return the extrapolated value.
            * if ext=1 or 'zeros', return 0
            * if ext=2 or 'raise', raise a ValueError
            * if ext=3 or 'const', return the boundary value.

            The default value is 0, passed from the initialization of
            UnivariateSpline.

        """
        return np.repeat(np.nan, len(x))


def iuv_spline(x: np.ndarray, y: np.ndarray, **kwargs
               ) -> Union[InterpolatedUnivariateSpline, NanSpline]:
    """
    Do an Interpolated Univariate Spline taking into account NaNs (with masks)

    (from scipy.interpolate import InterpolatedUnivariateSpline)

    :param x: the x values of the input to Interpolated Univariate Spline
    :param y: the y values of the input ot Interpolated Univariate Spline

    :param kwargs: passed to scipy.interpolate.InterpolatedUnivariateSpline
    :return: spline instance (from InterpolatedUnivariateSpline(x, y, **kwargs))
    """
    # set function name
    # _ = display_func('iuv_spline', __NAME__)
    # copy x and y
    x, y = np.array(x), np.array(y)
    # find all NaN values
    nanmask = ~np.isfinite(y)
    # deal with dimensions error (on k)
    #   otherwise get   dfitpack.error: (m>k) failed for hidden m
    if kwargs.get('k', None) is not None:
        # deal with to few parameters in x
        if len(x[~nanmask]) < (kwargs['k'] + 1):
            # raise exception if len(x) is bad
            emsg = ('IUV Spline len(x) < k+1 '
                    '\n\tk={0}\n\tlen(x) = {1}'
                    '\n\tx={2}\n\ty={3}')
            eargs = [kwargs['k'], len(x), str(x)[:70], str(y)[:70]]
            # return a nan spline
            return NanSpline(emsg.format(*eargs), x=x, y=y, **kwargs)
        if len(y[~nanmask]) < (kwargs['k'] + 1):
            # raise exception if len(x) is bad
            emsg = ('IUV Spline len(y) < k+1 '
                    '\n\tk={0}\n\tlen(y) = {1}'
                    '\n\tx={2}\n\ty={3}')
            eargs = [kwargs['k'], len(y), str(x)[:70], str(y)[:70]]
            # return a nan spline
            return NanSpline(emsg.format(*eargs), x=x, y=y, **kwargs)

    if np.sum(~nanmask) < 2:
        y = np.repeat(np.nan, len(x))
    elif np.sum(~nanmask) == 0:
        y = np.repeat(np.nan, len(x))
    else:
        # replace all NaN's with linear interpolation
        badspline = InterpolatedUnivariateSpline(x[~nanmask], y[~nanmask],
                                                 k=1, ext=1)
        y[nanmask] = badspline(x[nanmask])
    # return spline
    return InterpolatedUnivariateSpline(x, y, **kwargs)


def robust_polyfit(x: np.ndarray, y: np.ndarray, degree: int,
                   nsigcut: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    A robust polyfit (iterating on the residuals) until nsigma is below the
    nsigcut threshold. Takes care of NaNs before fitting

    :param x: np.ndarray, the x array to pass to np.polyval
    :param y: np.ndarray, the y array to pass to np.polyval
    :param degree: int, the degree of polynomial fit passed to np.polyval
    :param nsigcut: float, the threshold sigma required to return result
    :return:
    """
    # set function name
    # _ = display_func('robust_polyfit', __NAME__)
    # set up mask
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
        sig = fast.nanmedian(np.abs(res))
        if sig == 0:
            nsig = np.zeros_like(res)
            nsig[res != 0] = np.inf
        else:
            nsig = np.abs(res) / sig
        # work out the maximum sigma
        nsigmax = np.max(nsig[keep])
        # re-work out the keep criteria
        keep = nsig < nsigcut
    # return the fit and the mask of good values
    return np.array(fit), np.array(keep)


def robust_nanstd(x: np.ndarray) -> float:
    """
    Calculates the standard deviation (assumes normal distribution where
    1 sigma = the standard deviation)

    Done in a robust way to avoid being affected by outliers and nans

    :param x: numpy array the array to get the percentile of
    :return: the sigma to 100 - sigma value / 2
    """
    # set function name
    # _ = display_func('robust_polyfit', __NAME__)
    # get the 1 sigma error value
    erfvalue = erf(np.array([1.0]))[0] * 100
    # work out the high and low bounds
    low = fast.nanpercentile(x, 100 - erfvalue)
    high = fast.nanpercentile(x, erfvalue)
    # return the 1 sigma value
    return (high - low) / 2.0


def sinc(x: np.ndarray, amp: float, period: float, lin_center: float,
         slope: float, quad_scale: float = 0.0, cube_scale: float = 0.0,
         peak_cut: float = 0.0) -> np.ndarray:
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
    # set function name
    # _ = display_func('sinc', __NAME__)
    # Transform the x expressed in pixels into a stretched version
    # expressed in phase. The quadratic terms allows for a variation of
    # dispersion along the other
    deltax = x - lin_center
    cent = deltax + quad_scale * deltax ** 2 + cube_scale * deltax ** 3
    xp = 2 * np.pi * (cent / period)
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


def sigfig(x: Union[list, np.ndarray, float, int], n: int
           ) -> Union[list, np.ndarray, float]:
    """
    Produces x values to "n" significant figures

    From : https://stackoverflow.com/a/55599055

    :param x: numpy array, the values to round
    :param n: int, the number of significant figures required
    :return: numpy array like x at significant figures
    """
    # set function name
    func_name = __NAME__ + 'sigfig()'
    # deal with differing formats of x (cast to numpy array)
    if isinstance(x, np.ndarray):
        xin = np.array(x)
        dtype = None
    elif isinstance(x, list):
        xin = np.array(x)
        dtype = None
    elif isinstance(x, (float, int)):
        xin = np.array([x])
        dtype = type(x)
    else:
        raise DrsCodedException('00-009-10002', 'error',
                                targs=[type(x)], func_name=func_name)
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
        return dtype(xr[0])


def rot8(image: np.ndarray, nrotation: int, invert: bool = False) -> np.ndarray:
    """
    Rotation of a 2d image with the 8 possible geometries. Rotation 0-3
    do not flip the image, 4-7 perform a flip

    nrot = 0 -> same as input
    nrot = 1 -> 90deg counter-clock-wise
    nrot = 2 -> 180deg
    nrot = 3 -> 90deg clock-wise
    nrot = 4 -> flip top-bottom
    nrot = 5 -> flip top-bottom and rotate 90 deg counter-clock-wise
    nrot = 6 -> flip top-bottom and rotate 180 deg
    nrot = 7 -> flip top-bottom and rotate 90 deg clock-wise
    nrot >=8 -> performs a modulo 8 anyway

    :param image: input image
    :param nrotation: integer between 0 and 7
    :param invert: bool, if True does the opposite rotation to False
                   i.e. image --> rot8(invert=False) --> rot image -->
                        rot8(invert=True) --> image

    :type image: np.ndarray
    :type nrotation: int

    :return: rotated and/or flipped image
    """
    # set function name
    # _ = display_func('rot8', __NAME__)
    # how to invert them (if invert is True
    inversion = {1: 3, 2: 2, 3: 1, 4: 4, 5: 7, 6: 6, 7: 5, 0: 0}
    # module 8 number
    nrot = int(nrotation % 8)
    # deal with possible inverting
    if invert:
        nrot = inversion[nrot]
    # return the correctly rotated image
    return np.rot90(image[::1 - 2 * (nrot // 4)], nrot % 4)


def medbin(image: np.ndarray, by: int, bx: int) -> np.ndarray:
    """
    Median-bin an image to a given size through some funny reshapping.

    No interpoluation is done so bx must be a factor of image.shape[0]
    and by must be a factor of image.shape[1]

    e.g.

        image = np.arange(400).reshape(10, 40)
        by must be either [1, 2, 5]
        bx must be either [1, 2, 5, 8, 10, 20, 40]

    :param image: numpy array (2D), the image to bin
    :param by: int, the binning factor in y (must be a factor of image.shape[0])
    :param bx: int, the binning factor in x (must be a factor of image.shape[1])

    :type image: np.ndarray
    :type by: int
    :type bx: int

    :return: the binned numpy array of dimensions (by, bx)
    """
    # set function name
    func_name = __NAME__ + 'medbin()'
    # get the shape of the image
    dim1, dim2 = image.shape
    # must have valid bx and by
    if dim1 % by != 0:
        eargs = ['by', dim1, func_name]
        raise DrsCodedException('00-009-10003', 'error', targs=eargs,
                                func_name=func_name)
    if dim2 % bx != 0:
        eargs = ['bx', dim2, func_name]
        raise DrsCodedException('00-009-10003', 'error', targs=eargs,
                                func_name=func_name)
    # reshape the image
    array = image.reshape([by, dim1 // by, bx, dim2 // bx])
    # median in axis 1
    med1 = fast.nanmedian(array, axis=1)
    # median in axis 2
    med2 = fast.nanmedian(med1, axis=2)
    # return median-binned array
    return med2


def lowpassfilter(input_vect: np.ndarray, width: int = 101) -> np.ndarray:
    """
    Computes a low-pass filter of an input vector.

    This is done while properly handling NaN values, but at the same time
    being reasonably fast.

    Algorithm:

    provide an input vector of an arbitrary length and compute a running NaN
    median over a box of a given length (width value). The running median is
    NOT computed at every pixel but at steps of 1/4th of the width value.
    This provides a vector of points where the nan-median has been computed
    (ymed) and mean position along the input vector (xmed) of valid (non-NaN)
    pixels. This xmed/ymed combination is then used in a spline to recover a
    vector for all pixel positions within the input vector.

    When there are no valid pixel in a 'width' domain, the value is skipped
    in the creation of xmed and ymed, and the domain is splined over.

    :param input_vect: numpy 1D vector, vector to low pass
    :param width: int, width (box size) of the low pass filter

    :return: np.array, the low-pass of the input_vector
    """
    # set function name
    # _ = display_func('lowpassfilter', __NAME__)
    # indices along input vector
    index = np.arange(len(input_vect))
    # placeholders for x and y position along vector
    xmed = []
    ymed = []
    # loop through the lenght of the input vector
    for it in np.arange(-width // 2, len(input_vect) + width // 2, width // 4):
        # if we are at the start or end of vector, we go 'off the edge' and
        # define a box that goes beyond it. It will lead to an effectively
        # smaller 'width' value, but will provide a consistent result at edges.
        low_bound = it
        high_bound = it + int(width)
        # deal with lower bounds out of bounds --> set to zero
        if low_bound < 0:
            low_bound = 0
        # deal with upper bounds out of bounds --> set to max
        if high_bound > (len(input_vect) - 1):
            high_bound = (len(input_vect) - 1)
        # get the pixel bounds
        pixval = index[low_bound:high_bound]
        # do not low pass if not enough points
        if len(pixval) < 3:
            continue
        # if no finite value, skip
        if np.max(np.isfinite(input_vect[pixval])) == 0:
            continue
        # mean position along vector and NaN median value of
        # points at those positions
        xmed.append(fast.nanmean(pixval))
        ymed.append(fast.nanmedian(input_vect[pixval]))
    # convert to arrays
    xmed = np.array(xmed, dtype=float)
    ymed = np.array(ymed, dtype=float)
    # we need at least 3 valid points to return a
    # low-passed vector.
    if len(xmed) < 3:
        return np.zeros_like(input_vect) + np.nan
    # low pass with a mean
    if len(xmed) != len(np.unique(xmed)):
        xmed2 = np.unique(xmed)
        ymed2 = np.zeros_like(xmed2)
        for i in range(len(xmed2)):
            ymed2[i] = np.mean(ymed[xmed == xmed2[i]])
        xmed = xmed2
        ymed = ymed2
    # splining the vector
    spline = InterpolatedUnivariateSpline(xmed, ymed, k=1, ext=3)
    lowpass = spline(np.arange(len(input_vect)))
    # return the low pass filtered input vector
    return lowpass


def xpand_mask(mask1: np.ndarray, mask2: np.ndarray) -> np.ndarray:
    """
    find all pixels within mask2 that include a mask1 pixel

    :param mask1: numpy 1D array of bool, the base mask
    :param mask2: numpy 1D array of bool, the selection mask

    :return: a mask of all pixels within mask2 that include a mask1 pixel
    """
    increment = 1
    sum_prev = 0
    # loop until increment is zero
    while increment != 0:
        mask1 = np.array(mask2) * binary_dilation(mask1)
        increment = np.sum(mask1) - sum_prev
        sum_prev = np.sum(mask1)
    # return mask1
    return mask1


def percentile_bin(image: np.ndarray, bx: int, by: int,
                   percentile: float = 50) -> np.ndarray:
    """
    Percentile-bin an image

    To be used for low-pass filtering of an image.

    Note the binsizes cannot be smaller than the order footprint on the array
    as it would lead to a set of NaNs in the downsized image and chaos afterward

    :param image: numpy 2D array, the iamge to bin
    :param bx: int, the bin size in the x-direction
    :param by: int, the bin size in the y-direction
    :param percentile: float, the percentile by which to bin

    :return: numpy 2D array, the updated image
    """
    # get the shape of the image
    nbypix, nbxpix = image.shape
    #  To be used for low-pass
    # filterning of an image at a given percentile
    # Nice for background measurement with low percentiles (say ~10%)
    # thresholding for point sources detection with high percentiels (say ~90%)
    outimage = np.zeros([by, bx])
    # loop around the columns (y)
    for b_it in range(by):
        # loop around the rows (x)
        for b_jt in range(bx):
            # get x,y start,end
            ystart, yend = b_it * nbypix // by, (b_it + 1) * nbypix // by
            xstart, xend = b_jt * nbxpix // bx, (b_jt + 1) * nbxpix // bx
            # slice the image
            imslice = image[ystart:yend, xstart:xend]
            # get the nan percentile
            outimage[b_it, b_jt] = fast.nanpercentile(imslice, percentile)
    # return out image
    return outimage


def get_circular_mask(width: int):
    """
    create a circular mask

    :param width: int, the diameter of the circle (and size in x and y of the
                  mask created)
    :return:
    """
    # start mask off as the indices of a width x width square
    mask = np.indices([width, width])
    # move to center on the center of the circle (and square)
    mask = mask - width // 2
    # define points inside the circle as True, outside as False
    circle_mask = np.sqrt(mask[0] ** 2 + mask[1] ** 2) < width / 2
    # return the circle mask
    return circle_mask


# =============================================================================
# Define wave functions
# =============================================================================
def get_ll_from_coefficients(pixel_shift_inter: float,
                             pixel_shift_slope: float,
                             allcoeffs: np.ndarray,
                             nx: int, nbo: int) -> np.ndarray:
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
    # set function name
    # _ = display_func('get_ll_from_coefficients', __NAME__)
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


def get_ll_from_coefficients_cheb(pixel_shift_inter: float,
                                  pixel_shift_slope: float,
                                  allcoeffs: np.ndarray,
                                  nx: int, nbo: int) -> np.ndarray:
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
    # set function name
    # _ = display_func('get_ll_from_coefficients_cheb', __NAME__)
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


def get_dll_from_coefficients(allcoeffs: np.ndarray, nx: int,
                              nbo: int) -> np.ndarray:
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
    # set function name
    # _ = display_func('get_dll_from_coefficients', __NAME__)
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


def relativistic_waveshift(dv: Union[float, np.ndarray],
                           units: Union[uu.Unit, str] = 'km/s'
                           ) -> Union[float, np.ndarray]:
    """
    Relativistic offset in wavelength

    default is dv in km/s

    :param dv: float or numpy array, the dv values
    :param units: string or astropy units, the units of dv
    :return:
    """
    # set function name
    # _ = display_func('relativistic_waveshift', __NAME__)
    # get c in correct units
    # noinspection PyUnresolvedReferences
    if units == 'km/s' or units == uu.km / uu.s:
        c = speed_of_light
    # noinspection PyUnresolvedReferences
    elif units == 'm/s' or units == uu.m / uu.s:
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

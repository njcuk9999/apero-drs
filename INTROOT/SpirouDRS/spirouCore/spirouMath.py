#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-11-07 at 17:28

@author: cook

Import rules: Only from spirouConfig and spirouCore

Version 0.0.0
"""
from __future__ import division
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chisquare
from scipy.interpolate import UnivariateSpline
from scipy import stats
from datetime import datetime, tzinfo, timedelta
from time import mktime
from calendar import timegm
import warnings

from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouMath.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Date format
DATE_FMT = spirouConfig.Constants.DATE_FMT_DEFAULT()
TIME_FMT = spirouConfig.Constants.TIME_FORMAT_DEFAULT()

# =============================================================================
# Define Custom classes
# =============================================================================
class MathException(Exception):
    """Raised when Math is incorrect"""
    pass


# =============================================================================
# Define functions
# =============================================================================
def fwhm(sigma=1.0):
    """
    Get the Full-width-half-maximum value from the sigma value (~2.3548)

    :param sigma: float, the sigma, default value is 1.0 (normalised gaussian)
    :return: 2 * sqrt(2 * log(2)) * sigma = 2.3548200450309493 * sigma
    """
    return 2 * np.sqrt(2 * np.log(2)) * sigma


def polyval(p, x):
    """
    Faster version of numpy.polyval
    From here: https://stackoverflow.com/a/32527284

    :param p: numpy array (1D) or list, the polynomial coefficients
    :param x: numpy array (1D), the x points to fit the polynomial to

    :return y: numpy array (1D), the polynomial fit to x from coefficients p
    """
    # set up a blank y array
    y = np.zeros(x.shape, dtype=float)
    # loop around
    for v in range(p):
        y *= x
        y += v
    return y


def fitgaussian(x, y, weights=None, guess=None, return_fit=True,
                return_uncertainties=False):
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

    # if we don't have weights set them to be all equally weighted
    if weights is None:
        weights = np.ones(len(x))
    weights = 1.0/weights
    # if we aren't provided a guess, make one
    if guess is None:
        guess = [np.max(y), np.mean(y), np.std(y), 0]
    # calculate the fit using curve_fit to the function "gauss_function"
    with warnings.catch_warnings(record=True) as _:
        pfit, pcov = curve_fit(gauss_function, x, y, p0=guess, sigma=weights,
                               absolute_sigma=True)
    if return_fit and return_uncertainties:
        # calculate the fit parameters
        yfit = gauss_function(x, *pfit)
        #work out the normalisation constant
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
        #work out the normalisation constant
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


def fitgaussian_lmfit(x, y, weights, return_fit=True,
                      return_uncertainties=False):

    from lmfit.models import Model, GaussianModel
    # calculate guess
    mod = GaussianModel()
    params = mod.guess(y, x=x)
    guess = np.array([params['height'].value,
                      params['center'].value,
                      params['sigma'].value,
                      0.0])
    # set up model fit
    gmodel = Model(gauss_function)
    # run model fit
    out = gmodel.fit(y, x=x, a=guess[0], x0=guess[1], sigma=guess[2],
                     dc=guess[3], params=None, weights=weights)
    # extract out parameters
    pfit = [out.values['a'], out.values['x0'], out.values['sigma'],
            out.values['dc']]
    # extract out standard errors
    siga = [out.params['a'].stderr,
            out.params['x0'].stderr,
            out.params['sigma'].stderr,
            out.params['dc'].stderr]
    # return
    if return_fit and return_uncertainties:
         return np.array(pfit), np.array(siga), out.best_fit
    elif return_uncertainties:
        return np.array(pfit), np.array(siga)
    elif return_fit:
        return np.array(pfit), out.best_fit
    else:
        return np.array(pfit)


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


def get_ll_from_coefficients(pixel_shift_inter, pixel_shift_slope, params, nx, nbo):
    """
    Use the coefficient matrix "params" to construct fit values for each order
    (dimension 0 of coefficient matrix) for values of x from 0 to nx
    (interger steps)

    :param pixel_shift_inter: float, the intercept of a linear pixel shift
    :param pixel_shift_slope: float, the slope of a linear pixel shift

    :param params: numpy array (2D), the coefficient matrix
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
    xfit = np.arange(nx) + pixel_shift_inter + (pixel_shift_slope * np.arange(nx))
    # create empty line list storage
    ll = np.zeros((nbo, nx))
    # loop around orders
    for order_num in range(nbo):
        # get the coefficients for this order and flip them
        # (numpy needs them backwards)
        coeffs = params[order_num][::-1]
        # get the y fit using the coefficients for this order and xfit
        # TODO: Check order of params[i]
        # Question: This could be wrong - if fit parameters are order
        # Question: differently
        yfit = np.polyval(coeffs, xfit)
        # add to line list storage
        ll[order_num, :] = yfit
    # return line list
    return ll


def get_dll_from_coefficients(params, nx, nbo):
    """
    Derivative of the coefficients, using the coefficient matrix "params"
    to construct the derivative of the fit values for each order
    (dimension 0 of coefficient matrix) for values of x from 0 to nx
    (interger steps)

    :param params: numpy array (2D), the coefficient matrix
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
        coeffs = params[order_num]
        # get the y fit using the coefficients for this order and xfit
        # TODO: Check order of params[i]
        # Question: This could be wrong - if fit parameters are order
        # Question: differently
        yfiti = []
        # derivative =  (j)*(a_j)*x^(j-1)   where j = it + 1
        for it in range(len(coeffs)-1):
            yfiti.append((it + 1) * coeffs[it + 1] * xfit**it)
        yfit = np.sum(yfiti, axis=0)
        # add to line list storage
        ll[order_num, :] = yfit
    # return line list
    return ll


# =============================================================================
# Time functions
# =============================================================================
class UTC(tzinfo):
    """
    UTC class for use in setting time zone to UTC
    from:
    https://aboutsimon.com/blog/2013/06/06/Datetime-hell-Time-zone-
       aware-to-UNIX-timestamp.html
    """

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)


def stringtime2unixtime(string, fmt=DATE_FMT, zone='UTC'):
    """
    Convert a string in format "fmt" into a float unix time (seconds since
    1970-01-01 00:00:00 GMT). Currently supported timezones are UTC and local
    (i.e. your current time zone).

    Default is to assume string is in UTC/GMT time

    Commonly used format codes:

        %Y  Year with century as a decimal number.
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.

    :param string: string, the time string to convert
    :param fmt: string, the format of the string to convert
    :param zone: string, the time zone for the input string
                          (currently supported =  "UTC" or "local")

    :return unix_time: float, unix time (seconds since 1970-01-01 00:00:00 GMT)
    """
    func_name = __NAME__ + '.stringtime2unixtime()'
    # make sure input is a string
    try:
        string = str(string)
    except:
        emsg = 'Error time={0} must be a string in format {1}'
        raise ValueError(emsg.format(string, fmt))
    # try converting to datetime object and make into a string timestamp
    try:
        datetime_obj = datetime.strptime(string, fmt)
        if zone == 'UTC':
            datetime_obj = datetime_obj.replace(tzinfo=UTC())
            timestamp = timegm(datetime_obj.timetuple())
        else:
            timestamp = mktime(datetime_obj.timetuple())
    except Exception as e:
        emsg1 = 'Error in converting time (function = {0})'.format(func_name)
        emsg2 = '{0} reads: {1}'.format(type(e), e)
        raise MathException(emsg1 + '\n\t\t' + emsg2)
    # return time stamp
    return timestamp + datetime_obj.microsecond/1e6


def unixtime2stringtime(ts, fmt=DATE_FMT, zone='UTC'):
    """
    Convert a unix time (seconds since  1970-01-01 00:00:00 GMT) into a
    string in format "fmt". Currently supported timezones are UTC and local
    (i.e. your current time zone).

    Default is to return string time in UTC/GMT time

    Commonly used format codes:

        %Y  Year with century as a decimal number.
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.

    :param ts: float or int, the unix time (seconds since 1970-01-01 00:00:00
               GMT)
    :param fmt: string, the format of the string to convert
    :param zone: string, the time zone for the input string
                          (currently supported =  "UTC" or "local")

    :return stringtime: string, the time in format "fmt"
    """
    func_name = __NAME__ + '.unixtime2stringtime()'
    try:
        if zone == 'UTC':
            dt = datetime.utcfromtimestamp(ts)
        else:
            dt = datetime.fromtimestamp(ts)
    except Exception as e:
        emsg1 = 'Error in converting time (function = {0})'.format(
            func_name)
        emsg2 = '{0} reads: {1}'.format(type(e), e)
        raise MathException(emsg1 + '\n\t\t' + emsg2)

    return dt.strftime(fmt)


def get_time_now_unix(zone='UTC'):
    """
    Get the unix_time now.

    Default is to return unix_time in UTC/GMT time

    :param zone: string, if UTC displays the time in UTC else displays local
                 time

    :return unix_time: float, the unix_time
    """
    if zone == 'UTC':
        dt = datetime.utcnow()
        return timegm(dt.timetuple())
    else:
        dt = datetime.now()
        return mktime(dt.timetuple())


def get_time_now_string(fmt=TIME_FMT, zone='UTC'):
    """
    Get the time now (in string format = "fmt")

    Default is to return string time in UTC/GMT time

        Commonly used format codes:

        %Y  Year with century as a decimal number.
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.


    :param fmt: string, the format code for the returned time
    :param zone: string, if UTC displays the time in UTC else displays local
                 time

    :return stringtime: string, the time in a string in format = "fmt"
    """
    unix_time = get_time_now_unix(zone)
    return unixtime2stringtime(unix_time, fmt=fmt, zone=zone)

def continuum(x, y, binsize=200, overlap=100, sigmaclip=3.0, window=3,
              mode="median", use_linear_fit=False, excl_bands=[]):
    """
    Function to detect and calculate continuum spectrum
    :param x,y: numpy array (1D), input data (x and y must be of the same size)
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

    # set number of bins given the input array length and the bin size
    nbins = int(np.floor(len(x) / binsize))

    # initialize arrays to store binned data
    xbin, ybin = [], []
                       
    for i in range(nbins):
        # get first and last index within the bin
        idx0 = i * binsize - overlap
        idxf = (i + 1) * binsize + overlap
        # if it reaches the edges then it reset the indexes
        if idx0 < 0:
            idx0 = 0
        if idxf >= len(x):
            idxf = len(x) - 1
        # get data within the bin
        xbin_tmp = np.array(x[idx0:idxf])
        ybin_tmp = np.array(y[idx0:idxf])

        # create mask of exclusion bands
        excl_mask = np.full(np.shape(xbin_tmp), False, dtype=bool)
        for band in excl_bands :
            excl_mask += (xbin_tmp > band[0]) & (xbin_tmp < band[1])

        # mask data within exclusion bands
        xtmp = xbin_tmp[~excl_mask]
        ytmp = ybin_tmp[~excl_mask]
        
        # create mask to get rid of NaNs
        nanmask = np.logical_not(np.isnan(ytmp))
        if len(xtmp[nanmask]) > 2 :
            # calculate mean x within the bin
            xmean = np.mean(xtmp[nanmask])
            # calculate median y within the bin
            medy = np.median(ytmp[nanmask])

            # calculate median deviation
            medydev = np.median(np.absolute(ytmp[nanmask] - medy))
            # create mask to filter data outside n*sigma range
            filtermask = (ytmp[nanmask] > medy) & (ytmp[nanmask] < medy +
                                                   sigmaclip * medydev)
            if len(ytmp[nanmask][filtermask]) > 2:
                # save mean x wihthin bin
                xbin.append(xmean)
                if mode == 'max':
                    # save maximum y of filtered data
                    ybin.append(np.max(ytmp[nanmask][filtermask]))
                elif mode == 'median':
                    # save median y of filtered data
                    ybin.append(np.median(ytmp[nanmask][filtermask]))
                elif mode == 'mean':
                    # save mean y of filtered data
                    ybin.append(np.mean(ytmp[nanmask][filtermask]))
                else:
                    emsg = 'Can not recognize selected mode="{0}"...exiting'
                    WLOG('error', DPROG, emsg.format(mode))

    # Option to use a linearfit within a given window
    if use_linear_fit:
        # initialize arrays to store new bin data
        newxbin, newybin = [], []
        # append first point to avoid crazy behaviours in the edge
        newxbin.append(x[0])
        newybin.append(ybin[0])

        # loop around bins to obtain a linear fit within a given window size
        for i in range(len(xbin)):
            # set first and last index to select bins within window
            idx0 = i - window
            idxf = i + 1 + window
            # make sure it doesnt go over the edges
            if idx0 < 0: idx0 = 0
            if idxf > nbins: idxf = nbins - 1

            # perform linear fit to these data
            slope, intercept, r_value, p_value, std_err = \
                stats.linregress(xbin[idx0:idxf], ybin[idx0:idxf])

            # save data obtained from the fit
            newxbin.append(xbin[i])
            newybin.append(intercept + slope * xbin[i])

        xbin, ybin = newxbin, newybin

    # interpolate points applying an Spline to the bin data
    sfit = UnivariateSpline(xbin, ybin)
    sfit.set_smoothing_factor(0.5)
    
    # Resample interpolation to the original grid
    continuum = sfit(x)
    # return continuum and x and y bins
    return continuum, xbin, ybin


# =============================================================================
# End of code
# =============================================================================

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
from datetime import datetime, tzinfo, timedelta
from time import mktime
from calendar import timegm

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


# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:10

@author: cook



Version 0.0.0
"""
from SpirouDRS import spirouConfig
from . import spirouLog
from . import spirouPlot
from . import spirouMath

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouCore.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['wlog',
           'sPlt']


# =============================================================================
# Function aliases
# =============================================================================
wlog = spirouLog.logger
"""
Parses a key (error/warning/info/graph), an option and a message to the
stdout and the log file.

keys are controlled by "spirouConfig.Constants.LOG_TRIG_KEYS()"
printing to screen is controlled by "PRINT_LEVEL" constant (config.py)
printing to log file is controlled by "LOG_LEVEL" constant (config.py)
based on the levels described in "spirouConfig.Constants.WRITE_LEVEL"

:param key: string, either "error" or "warning" or "info" or graph, this
            gives a character code in output
:param option: string, option code
:param message: string or list of strings, message to display or messages
                to display (1 line for each message in list)

output to stdout/log is as follows:

    HH:MM:SS.S - CODE |option|message

time is output in UTC to nearest .1 seconds

:return:
"""

warnlog = spirouLog.warninglogger
"""
Warning logger - takes "w" - a list of caught warnings and pipes them on
to the log functions. If "funcname" is not None then t "funcname" is 
printed with the line reference (intended to be used to identify the code/
function/module warning was generated in)

to catch warnings use the following:

>>> with warnings.catch_warnings(record=True) as w:
>>>     code_to_generate_warnings()
>>> warninglogger(w, 'some name for logging')

:param w: list of warnings, the list of warnings from 
           warnings.catch_warnings
:param funcname: string or None, if string then also pipes "funcname" to the
                 warning message (intended to be used to identify the code/
                 function/module warning was generated in)
:return:
"""

GetTimeNowUnix = spirouMath.get_time_now_unix
"""
Get the unix_time now.

Default is to return unix_time in UTC/GMT time

:param zone: string, if UTC displays the time in UTC else displays local
             time

:return unix_time: float, the unix_time 
"""

GetTimeNowString = spirouMath.get_time_now_string
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

Unix2stringTime = spirouMath.unixtime2stringtime
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

String2unixTime = spirouMath.stringtime2unixtime
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

# Plotting functions alias
sPlt = spirouPlot

# =============================================================================
# End of code
# =============================================================================

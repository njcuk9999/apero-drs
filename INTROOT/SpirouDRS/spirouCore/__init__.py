#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
initialization code for Spirou Core functions module

Created on 2017-10-30 at 17:10

@author: cook

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
__all__ = ['wlog', 'WarnLog',
           'GaussFunction', 'Getll', 'Getdll',
           'GetTimeNowUnix', 'GetTimeNowString', 'Continuum',
           'Unix2stringTime', 'String2unixTime',
           'sPlt']


# =============================================================================
# Function aliases
# =============================================================================
wlog = spirouLog.wlog

WarnLog = spirouLog.warninglogger

GaussFunction = spirouMath.gauss_function

Getll = spirouMath.get_ll_from_coefficients

Getdll = spirouMath.get_dll_from_coefficients

GetTimeNowUnix = spirouMath.get_time_now_unix

GetTimeNowString = spirouMath.get_time_now_string

Continuum = spirouMath.continuum

PrintLog = spirouLog.printlog

PrintColour = spirouLog.printcolour

Unix2stringTime = spirouMath.unixtime2stringtime

String2unixTime = spirouMath.stringtime2unixtime

sPlt = spirouPlot

# =============================================================================
# End of code
# =============================================================================

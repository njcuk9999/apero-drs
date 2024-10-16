#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
from apero import lang
from apero.base import base
from apero.core.core import drs_log

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_static.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry


# =============================================================================
# Define functions
# =============================================================================
def led_flat_static_calib(params):
    """
    Produces an LED FLAT required by the preprocessing.

    :param params:
    :return:
    """
    WLOG(params, '', 'Computing LED_FLAT static calibration')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello world')

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
from aperocore.constants import param_functions
from aperocore.core import drs_log

from aperotest.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperotest.core.general.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get the logger
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def start_splash(name: str):
    """
    Print the start splash

    :return: None, prints to screen
    """
    WLOG(None, 'info', drs_log.MPARAMS['DRS_HEADER'], colour='magenta')
    WLOG(None, 'info', name, colour='magenta')
    vargs = [__version__, __date__]
    WLOG(None, 'info', 'v{0} [{1}]'.format(*vargs), colour='magenta')
    WLOG(None, 'info', drs_log.MPARAMS['DRS_HEADER'], colour='magenta')


def end_splash():
    """
    Print the end splash

    :return: None, prints to screen
    """
    WLOG(None, 'info', drs_log.MPARAMS['DRS_HEADER'], colour='magenta')
    WLOG(None, 'info', 'End of code', colour='magenta')
    WLOG(None, 'info', drs_log.MPARAMS['DRS_HEADER'], colour='magenta')


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

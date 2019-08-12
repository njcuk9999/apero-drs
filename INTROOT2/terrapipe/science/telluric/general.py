#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:16

@author: cook
"""
from __future__ import division

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.io import drs_data


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.general.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def get_whitelist(params, **kwargs):
    func_name = __NAME__ + '.get_whitelist()'
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_WHITELIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    whitelist = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                        func_name)
    # return the whitelist
    return whitelist


def get_blacklist(params, **kwargs):
    func_name = __NAME__ + '.get_blacklist()'
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_BLACKLIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    blacklist = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                        func_name)
    # return the whitelist
    return blacklist


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

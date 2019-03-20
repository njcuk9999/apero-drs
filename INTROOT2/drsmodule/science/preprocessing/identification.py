#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:37
@author: ncook
Version 0.0.1
"""
from __future__ import division
import traceback

from drsmodule import constants
from drsmodule import config
from drsmodule import locale

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'identification.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = config.wlog
# Get the text types
ErrorEntry = locale.drs_text.ErrorEntry


# =============================================================================
# Define functions
# =============================================================================
def drs_file_id(params, given_drs_file):
    """
    Given a generic drs file


    :param params:
    :param given_drs_file:
    :return:
    """
    func_name = __NAME__ + '.drs_file_id()'
    # check we have entries
    if len(given_drs_file.fileset) == 0:
        eargs = [given_drs_file.name, func_name]
        WLOG(params, 'error', ErrorEntry('01-010-00001', args=eargs))

    # get the associated files with this generic drs file
    fileset = list(given_drs_file.fileset)

    # set found to False
    found = False
    kind = None
    # loop around files
    for drs_file in fileset:
        # copy info from given_drs_file into drs_file
        file_in = drs_file.copy(given_drs_file)
        # check this file is valid
        cond, _ = file_in.check_file()
        # if True we have found our file
        if cond:
            found = True
            kind = file_in
            break

    # TODO: Need code here
    pass



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================
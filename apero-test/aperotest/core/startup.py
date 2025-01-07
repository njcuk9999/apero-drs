#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 10:16

@author: cook
"""
import argparse
import os
import string
from typing import Optional

from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from aperocore.core import drs_text

from aperotest.core import base
from aperotest.constants import constants

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperotest.recipes.run.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get the logger
WLOG = drs_log.wlog
# Define paths to create
PATHS = ['DATA_PATH', 'PLOT_PATH']
# Set the description of APERO Core
DESCRIPTIONS = dict()
DESCRIPTIONS['aperotest.recipes.test_setup'] = 'SOSSISSE - SOSS Inspired SpectroScopic Extraction'
DESCRIPTIONS['aperotest.recipes.test_run'] = 'Setup up SOSSISSE directories'

INPUTARGS = dict()
INPUTARGS['aperotest.recipes.test_setup'] = ['GLOBAL.YAML_FILE', 'DATA_PATH',
                                             'PLOT_PATH']
INPUTARGS['aperotest.recipes.test_run'] = ['GLOBAL.YAML_FILE']


# =============================================================================
# Define functions
# =============================================================================
def setup(params: ParamDict):
    """
    Setup the general module

    :return: None
    """
    # print progress
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', 'Checking arguments')
    WLOG(params, 'info', params['DRS_HEADER'])
    # ask user for any missing arguments
    params = load_functions.ask_for_missing_args(params)
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', 'Checking paths')
    WLOG(params, 'info', params['DRS_HEADER'])
    # Create some paths
    for path in PATHS:
        # deal with path not existing in params (skip) - these really should
        #    exist though
        if path not in params:
            continue
        # convert path to a real absolute path
        params[path] = os.path.abspath(params[path])
        # find if path exists
        if os.path.exists(params[path]):
            WLOG(params, '', 'Path exists: {0}'.format(params[path]))
            continue
        # ask user to create path
        question = '\nPath does not exist: {0}\nWould you like to create it?'
        question = question.format(params[path])
        # ask user
        if drs_text.user_input(question, dtype='YN', required=True):
            os.makedirs(params[path])
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', 'Constructing yaml file')
    WLOG(params, 'info', params['DRS_HEADER'])
    # Get the constants dictionary
    cdict = constants.CDict
    # get the yaml file
    yaml_file = params['GLOBAL']['YAML_FILE']
    # print progress
    msg = 'Saving constants to yaml file: {0}'
    WLOG(params, '', msg.format(os.path.realpath(yaml_file)))
    # save the constants dictionary to yaml file
    cdict.save_yaml(params, outpath=yaml_file, log=False)


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

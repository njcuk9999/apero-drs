#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:32

@author: cook
"""
from typing import Optional

from aperocore.core import drs_log
from aperocore.constants import load_functions

from aperotest.constants.constants import CDict
from aperotest.core import base
from aperotest.core import general

# =============================================================================
# Define variables
__NAME__ = 'aperotest.recipes.test_run'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# set description
__description__ = 'Run the APERO test recipe'
__inputs__ = ['GLOBAL.YAML_FILE']
# get the logger
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    # print splash
    general.start_splash('APERO Test Run')
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           param_file_path='GLOBAL.YAML_FILE',
                                           config_list=[CDict],
                                           kwargs=kwargs)
    # -------------------------------------------------------------------------
    # do something here
    # print a message for this function
    WLOG(params, 'info', 'This is a test function')
    # loop around keys in params and print them
    print(params, flush=True)
    print(params.sources, flush=True)
    # -------------------------------------------------------------------------
    # print splash
    general.end_splash()


def run():
    _ = main()

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    _ = main()

# =============================================================================
# End of code
# =============================================================================

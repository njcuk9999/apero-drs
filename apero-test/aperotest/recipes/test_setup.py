#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:32

@author: cook
"""

from aperocore.constants import load_functions

from aperotest.constants.constants import CDict
from aperotest.core import base
from aperotest.core import startup
from aperotest.core import general

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperotest.recipes.test_setup'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# set description
__description__ = 'Setup the APERO test recipes'
__inputs__ = ['GLOBAL.YAML_FILE', 'DATA_PATH', 'PLOT_PATH']

# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    # print splash
    general.start_splash('APERO Test Setup')
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           config_list=[CDict],
                                           from_file=False,
                                           kwargs=kwargs)
    # setup using parameters
    startup.setup(params)
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

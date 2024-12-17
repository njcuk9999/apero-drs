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

from aperotest.core import base
from aperotest.core import startup
from aperotest.core import general

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperotest.constants.constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# set description
__description__ = 'Setup the SCARVS recipes'
# get the logger
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def main(yaml_file: Optional[str] = None):
    # print splash
    general.start_splash('SCARVS Run')
    # get parameters
    params = startup.get_params(yaml_file, description=__description__,
                                name='RUN')
    # -------------------------------------------------------------------------
    # do something here
    # print a message for this function
    WLOG(params, 'info', 'This is a test function')
    # loop around keys in params and print them
    for key in params:
        # skip parameters without an instance
        if params.instances[key] is None:
            continue
        # print parameters flagged as for the user
        if params.instances[key].user:
            msg = 'Key = {0}, Value = {1}'
            margs = [key, params[key]]
            WLOG(params, '', msg.format(*margs), wrap=False)
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

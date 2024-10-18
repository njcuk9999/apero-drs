#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-18 at 12:00

@author: cook
"""
import signal

from aperocore.constants import param_functions

from apero.setup import drs_setup


# =============================================================================
# Define variables
# =============================================================================
ParamDict = param_functions.ParamDict
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def main() -> ParamDict:
    """
    Run the APERO setup
    """
    # catch Ctrl+C
    signal.signal(signal.SIGINT, drs_setup.catch_sigint)
    # -------------------------------------------------------------------------
    # get command line args
    params = drs_setup.command_line_args()
    # -------------------------------------------------------------------------
    # ask the users for any missing arguments
    params = drs_setup.ask_user(params)
    # -------------------------------------------------------------------------
    # run the setup
    if params['UPDATE']:
        drs_setup.update_setup(params)
    else:
        drs_setup.run_setup(params)
    # -------------------------------------------------------------------------
    # return params
    return params


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # run main function
    _ = main()

# =============================================================================
# End of code
# =============================================================================

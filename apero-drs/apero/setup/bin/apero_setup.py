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

from apero.setup.core import drs_setup
from apero.setup.core import setup_constants
from apero.setup.core import drs_demo

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
    # display title
    drs_setup.display_title()
    # -------------------------------------------------------------------------
    # get setup constants
    sargs = setup_constants.SARGS
    # -------------------------------------------------------------------------
    # get command line args
    params = drs_setup.command_line_args(sargs)
    # -------------------------------------------------------------------------
    # update setup
    if params['UPDATE']:
        params = drs_setup.update_setup(params, sargs)
    # -------------------------------------------------------------------------
    # run setup
    else:
        # ask the users for any missing arguments
        params = drs_setup.ask_user(params, sargs)
    # -------------------------------------------------------------------------
    # run setup
    drs_setup.run_setup(params, sargs)
    # -------------------------------------------------------------------------
    # give the user an option to start from a demo (e.g. mini data)
    drs_demo.start_from_demo(params)
    # -------------------------------------------------------------------------
    # end splash
    drs_setup.end_all(params)
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

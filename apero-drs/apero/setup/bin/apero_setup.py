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

# =============================================================================
# Define functions
# =============================================================================
def main() -> ParamDict:
    """
    Run the APERO setup
    """
    # -------------------------------------------------------------------------
    # get setup constants
    sargs = setup_constants.SARGS
    # -------------------------------------------------------------------------
    # get command line args
    params = drs_setup.command_line_args(sargs)
    # -------------------------------------------------------------------------
    # gui mode: the browser gui runs this script again for every action
    if params['GUI']:
        # import here: only needed in gui mode
        from apero.setup.gui import app as setup_gui
        setup_gui.main(params)
        return params
    # -------------------------------------------------------------------------
    # catch Ctrl+C
    signal.signal(signal.SIGINT, drs_setup.catch_sigint)
    # -------------------------------------------------------------------------
    # display title
    drs_setup.display_title()
    # -------------------------------------------------------------------------
    # Script-only mode must not install, reset, or offer demo data.
    if params['INSTALL_SH']:
        params = drs_setup.update_setup(params, sargs)
        drs_setup.create_install_script(params, sargs)
        drs_setup.end_all(None)
        return params
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

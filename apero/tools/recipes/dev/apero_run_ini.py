#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
from apero.base import base
from apero import lang
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_startup
from apero.tools.module.processing import drs_run_ini


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_run_ini.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# --------------------------------------------------------------------------
# define run.ini files




# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_changelog.py

    :param kwargs: any additional keywords

    :type preview: bool

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):

    # get instrument variable
    instruments = list(base.INSTRUMENTS)
    if 'INSTRUMENT' in params['INPUTS']:
        if not drs_text.null_text(params['INPUTS']['INSTRUMENT'], ['None', '']):
            instruments = params['INPUTS']['INSTRUMENT'].split(',')
    # log progress
    WLOG(params, 'info', 'Generating list of default run.ini files')
    # get default run file instances
    run_files = drs_run_ini.main(params)
    # loop around run files
    for run_file in run_files:
        # skip invalid instruments
        if run_file.instrument not in instruments:
            continue
        # progress report
        msg = 'Processing file: {0}'
        margs = [run_file.name]
        WLOG(params, 'info', msg.format(*margs))
        # populate the text file
        run_file.populate_text_file(params)
        # print message
        msg = 'Writing file: {0}'
        margs = [run_file.outpath]
        WLOG(params, 'info', msg.format(*margs))
        # write to file
        run_file.write_text_file()

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

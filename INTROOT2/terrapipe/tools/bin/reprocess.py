#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:47

@author: cook
"""
import numpy as np
import sys

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.tools.module.setup import drs_reprocess


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'reprocess.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(runfile=None, **kwargs):
    """
    Main function for cal_dark_spirou.py

    :param directory: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(runfile=runfile, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    params = core.end_main(params, llmain, recipe, success, outputs=None)
    # return a copy of locally defined variables in the memory
    return core.get_locals(params, dict(locals()), llmain)


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # get run file from inputs
    runfile = params['INPUTS']['RUNFILE']

    # ----------------------------------------------------------------------
    # Deal with run file
    # ----------------------------------------------------------------------
    # deal with run file
    params, runtable = drs_reprocess.read_runfile(params, runfile)
    # reset sys.argv so it doesn't mess with recipes
    sys.argv = [__NAME__]

    # ----------------------------------------------------------------------
    # Send email about starting
    # ----------------------------------------------------------------------
    # send email if configured
    drs_reprocess.send_email(params, kind='start')

    # ----------------------------------------------------------------------
    # Deal with reset options
    # ----------------------------------------------------------------------
    drs_reprocess.reset_files(params)

    # ----------------------------------------------------------------------
    # find all raw files
    # ----------------------------------------------------------------------
    # get raw files
    rawtable, rawpath = drs_reprocess.find_raw_files(params)

    # ----------------------------------------------------------------------
    # Generate run list
    # ----------------------------------------------------------------------
    runlist = drs_reprocess.generate_run_list(params, rawtable, runtable)

    # ----------------------------------------------------------------------
    # Process run list
    # ----------------------------------------------------------------------
    outlist, has_errors = drs_reprocess.process_run_list(params, runlist)

    # ----------------------------------------------------------------------
    # Print timing
    # ----------------------------------------------------------------------
    if not has_errors:
        drs_reprocess.display_timing(params, outlist)

    # ----------------------------------------------------------------------
    # Print out any errors
    # ----------------------------------------------------------------------
    if has_errors:
        drs_reprocess.display_errors(params, outlist)

    # ----------------------------------------------------------------------
    # Send email about finishing
    # ----------------------------------------------------------------------
    # send email if configured
    drs_reprocess.send_email(params, kind='end')

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # Post main plot clean up
    core.post_main(ll['params'], has_plots=True)

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-06-03

@author: cook
"""
from apero.base import base
from apero import lang
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.processing import drs_trigger


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_trigger.py'
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

EXCLUDE_DIRS = ['2022-05-04', '2022-05-05', '2022-05-06', '2022-05-07',
                '2022-05-08', '2022-05-09', '2022-05-10', '2022-05-11',
                '2022-05-12', '2022-05-13', '2022-05-14', '2022-05-15',
                '2022-05-16']

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


    # create trigger class
    trigger = drs_trigger.Trigger(params, recipe)
    # add excluded directories
    trigger.excluded_dirs = EXCLUDE_DIRS
    # set the scripts for calibs and science
    trigger.calib_script = 'trigger_night_calib_run.ini'
    trigger.science_script = 'trigger_night_science_run.ini'
    # define time to wait between loops
    trigger.sleep_time = 1
    # keep track of iterations
    iteration = 1
    # run the loop
    while trigger.active:
        # update progress
        WLOG(params, 'info', f'Iteration {iteration}', colour='magenta')
        # run trigger
        trigger()
        # update iterator
        iteration += 1

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

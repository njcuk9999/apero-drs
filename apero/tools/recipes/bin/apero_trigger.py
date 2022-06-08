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
from apero.core.core import drs_text
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
    # -------------------------------------------------------------------------
    # deal with resetting the trigger file
    if params['INPUTS']['RESET']:
        trigger.reset()
    # set test mode
    if drs_text.true_text(params['INPUTS']['TRIGGER_TEST']):
        trigger.trigger_test = True
    # -------------------------------------------------------------------------
    # add excluded directories
    exclude_dirs = params['INPUTS']['IGNORE']
    if not drs_text.null_text(exclude_dirs, ['None', '', 'Null']):
        trigger.excluded_dirs = params['INPUTS'].listp('IGNORE', dtype=str)
    else:
        trigger.excluded_dirs = None
    # -------------------------------------------------------------------------
    # set the scripts for calibs and science
    trigger.calib_script = params['INPUTS']['CALIB']
    trigger.science_script = params['INPUTS']['SCI']
    # define time to wait between loops
    trigger.sleep_time = params['INPUTS']['WAIT']
    # -------------------------------------------------------------------------
    # keep track of iterations
    iteration = 1
    # run the loop
    while trigger.active:
        # update progress
        # TODO: Add to language database
        msg = f'Iteration {0} (Ctrl+C to cancel)'
        margs = [iteration]
        WLOG(params, 'info', msg.format(*margs), colour='magenta')
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO database push tool

Push all pending database entries into the databases. Recipes run in
parallel mode (e.g. from the processing queue) write their database
entries to the pending directory instead of the databases, so they must
be pushed before any recipe that depends on them runs.

apero_processing (in queue mode) adds one apero_db_push.py run as its own
queue group after every queue group, so the next group always sees the
outputs of the previous group.

Created on 2026-10-28

@author: cook
"""
from typing import Any, Dict

import apero as apero_pkg
from aperocore.constants import param_functions
from aperocore.core import drs_log
from apero.core import drs_database
from apero.utils import drs_recipe
from apero.utils import drs_startup
from aperocore import drs_lang

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_db_push.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = drs_lang.textentry
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
def main(**kwargs):
    """
    Main function for apero_db_push.py

    :param kwargs: additional keyword arguments

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       enable_plotter=False)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success,
                                outputs='None')


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """
    Main code: push all pending database entries into the databases

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Push pending database entries
    # ----------------------------------------------------------------------
    # log: Pushing pending database entries
    WLOG(params, 'info', textentry('40-521-00001'))
    drs_database.db_push(params)
    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

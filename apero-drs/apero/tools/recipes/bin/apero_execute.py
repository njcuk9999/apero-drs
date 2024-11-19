#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-28 11:32

@author: cook
"""
from aperocore.base import base
from aperocore.core import drs_log
from apero.utils import drs_startup
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_execute.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for apero_validate.py

    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)

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
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # Get a list of recipes (for instrument + tools)
    recipe_list = recipe.recipemod.recipes

    if params['INPUTS']['RECIPES']:

        WLOG(params, 'info', 'List of recipes:' )

        for recipe_it in recipe_list:
            msg = '\t{0} [{1}]'
            margs = [recipe_it.name, recipe_it.shortname]
            WLOG(params, 'info', msg.format(*margs))

    # if params['INPUTS']['HELP']:
    #     WLOG(params, 'info', 'Help for recipe: {0}'.format(params['INPUTS']['HELP']))


    WLOG(params, 'info', 'Running apero_execute.py')

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()



def run():
    _ = main()



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run main function
    _ = main()

# =============================================================================
# End of code
# =============================================================================

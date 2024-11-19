#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-10-28 11:32

@author: cook
"""

from aperocore.core import drs_log
from aperocore.constants import load_functions
from apero.base import base as apero_base
from apero.instruments.select import INSTRUMENTS
from apero.setup.core import drs_execute

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
    # get parameters from function
    rparams = drs_execute.command_line_args()
    # get recipe mod
    aparams = load_functions.load_config(INSTRUMENTS)
    instrument = load_functions.load_pconfig(INSTRUMENTS)
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # Get a list of recipes (for instrument + tools)
    recipe_list = instrument.RECIPEMOD().recipes

    if rparams['LIST']:
        WLOG(aparams, 'info', 'List of recipes:' )

        for recipe_it in recipe_list:
            msg = '\t{0} [{1}]'
            margs = [recipe_it.name, recipe_it.shortname]
            WLOG(aparams, 'info', msg.format(*margs))

    # if params['INPUTS']['HELP']:
    #     WLOG(params, 'info', 'Help for recipe: {0}'.format(params['INPUTS']['HELP']))
    WLOG(aparams, 'info', 'Running apero_execute.py')

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

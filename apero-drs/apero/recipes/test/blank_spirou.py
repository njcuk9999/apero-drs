#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
blank_spirou.py

An example recipe used for development

Created on 2019-07-05 at 16:46

@author: cook
"""
from typing import Any, Dict, Tuple, Union

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.tools.module.testing import drs_dev

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'blank.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe

# -----------------------------------------------------------------------------
# Note: move recipe definition to instrument set up when testing is finished
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
blank = drs_dev.TmpRecipe()
blank.name = __NAME__
blank.shortname = 'DEVTEST'
blank.instrument = __INSTRUMENT__
blank.in_block_str = 'red'
blank.out_block_str = 'red'
blank.extension = 'fits'
blank.description = 'Test for developer mode'
blank.kind = 'misc'
blank.set_kwarg(name='--text', dtype=str, default='None',
                helpstr='Enter text here to print it')
# add recipe to recipe definition
RMOD.add(blank)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for blank

    :param kwargs: additional keyword arguments

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    # -------------------------------------------------------------------------
    # Note: remove rmod when put into full recipe
    # -------------------------------------------------------------------------
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success)


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # This is just a test
    if 'TEXT' in params['INPUTS']:
        if params['INPUTS']['TEXT'] not in ['None', None, '']:
            WLOG(params, '', params['INPUTS']['TEXT'])

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

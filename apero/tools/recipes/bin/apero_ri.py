#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI (Reduction Interface)

Takes all the data, compiles object table and recipe  table and uploads
it to the database.

Created on 2019-07-26 at 09:39

@author: cook
"""
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.tools.module.ari import ari_general as ari


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict


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
    Main function for apero_log_stats.py

    :param kwargs: additional keyword arguments

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


def __main__(recipe: DrsRecipe, params: ParamDict):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'

    # ----------------------------------------------------------------------
    # step 1: setup
    # ----------------------------------------------------------------------
    # read parameters from yaml file and push into parameter dictionary
    params = ari.load_ari_params(params)

    # ----------------------------------------------------------------------
    # step 2: previous data
    # ----------------------------------------------------------------------
    # get previous object data from store
    object_classes = ari.load_previous_objects(params)
    # get previous recipe data from store
    recipe_classes = ari.load_previous_recipes(params)

    # ----------------------------------------------------------------------
    # step 3: find new data
    # ----------------------------------------------------------------------
    # find new data for objects
    object_classes = ari.find_new_objects(params, object_classes)
    # find new entries for recipes
    recipe_classes = ari.find_new_recipes(params, recipe_classes)

    # ----------------------------------------------------------------------
    # step 4: compile new data
    # ----------------------------------------------------------------------
    # compile object data
    object_classes = ari.compile_object_data(params, object_classes)
    # compile recipe data
    recipe_classes = ari.compile_recipe_data(params, recipe_classes)

    # ----------------------------------------------------------------------
    # step 5: write pages
    # ----------------------------------------------------------------------
    # write object pages
    ari.write_object_pages(params, object_classes)
    # write recipe pages
    ari.write_recipe_pages(params, recipe_classes)

    # ----------------------------------------------------------------------
    # step 6: compile pages
    # ----------------------------------------------------------------------
    # compile object pages
    ari.compile_object_pages(params)
    # compile recipe pages
    ari.compile_recipe_pages(params)

    # ----------------------------------------------------------------------
    # step 7: upload
    # ----------------------------------------------------------------------
    # upload
    ari.upload(params)

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2021-01-2021-01-13 14:42

@author: cook
"""
from aperocore.base import base
from aperocore.constants import param_functions
from aperocore import drs_lang
from aperocore.core import drs_log
from apero.utils import drs_startup
from apero.tools.module.testing import drs_dev
from apero.tools.module.utils import constants_tools

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_constants.py'
__INSTRUMENT__ = base.IPARAMS['INSTRUMENT']
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = drs_lang.textentry
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# get file definitions for this instrument
FMOD = drs_dev.FileDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
apero_constants = drs_dev.TmpRecipe()
apero_constants.name = __NAME__
apero_constants.shortname = 'APERO_CONST'
apero_constants.instrument = __INSTRUMENT__
apero_constants.in_block_str = 'red'
apero_constants.out_block_str = 'red'
apero_constants.extension = 'fits'
apero_constants.description = ('Developer functionality dealing with the'
                               'constant file')
apero_constants.kind = 'misc'
apero_constants.set_debug_plots()
apero_constants.set_summary_plots()

apero_constants.set_kwarg(name='--generate', dtype=str, default='None',
                          options=['standard', 'full'],
                          helpstr='Regenerate the user config files from'
                                  'defaults (either standard or full')
apero_constants.set_kwarg(name='--clean', dtype='switch', default=False,
                          helpstr='Clean APERO constants (not recommended)')

apero_constants.set_kwarg(name='--glossary', dtype='switch', default=False,
                          helpstr='Create entries for glossary')

# add recipe to recipe definition
RMOD.add(apero_constants)


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
    Main function for exposuremeter_spirou.py

    :param kwargs: additional keyword arguments

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # -------------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # -------------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # -------------------------------------------------------------------------
    # End Message
    # -------------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success)


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # -------------------------------------------------------------------------
    # Main Code
    # -------------------------------------------------------------------------
    mainname = __NAME__ + '._main()'

    # -------------------------------------------------------------------------
    # Generating config file functionality
    # -------------------------------------------------------------------------
    # Deal with config file re-generation
    if 'GENERATE' in params['INPUTS']:
        # deal with generation
        success = constants_tools.deal_with_generate(params)
        # if generation successful stop here
        if success:
            return locals()

    # -------------------------------------------------------------------------
    # Cleaning constant python files functionality
    # -------------------------------------------------------------------------
    if 'CLEAN' in params['INPUTS']:
        # get clean value
        clean = params['INPUTS']['CLEAN']
        # go clean
        if clean:
            # do cleaning
            success = constants_tools.deal_with_clean(params)
            # if cleaning successful stop here
            if success:
                return locals()

    # -------------------------------------------------------------------------
    # Create glossary functionality
    # -------------------------------------------------------------------------
    if 'GLOSSARY' in params['INPUTS']:
        # get the glossary value
        glossary = params['INPUTS']['GLOSSARY']
        # check whether user wants to create glossary
        if glossary:
            # create glossary
            success = constants_tools.create_glossary(params)
            # if creation successful stop here
            if success:
                return locals()

    # -------------------------------------------------------------------------
    # End of main code
    # -------------------------------------------------------------------------
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

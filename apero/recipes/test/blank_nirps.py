#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
from apero import core
from apero import locale
from apero.core import constants
from apero.tools.module.testing import drs_dev


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'blank.py'
__INSTRUMENT__ = 'NIRPS'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# -----------------------------------------------------------------------------
# TODO: move recipe definition to instrument set up when testing is finished
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
blank = drs_dev.TmpRecipe()
blank.name = __NAME__
blank.shortname = 'DEVTEST'
blank.instrument = __INSTRUMENT__
blank.outputdir = 'reduced'
blank.inputdir = 'reduced'
blank.inputtype = 'reduced'
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
def main(**kwargs):
    """
    Main function for cal_update_berv.py

    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    # TODO: remove rmod when put into full recipe
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return core.end_main(params, llmain, recipe, success)


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
    # This is just a test
    if 'TEXT' in params['INPUTS']:
        if params['INPUTS']['TEXT'] not in ['None', None, '']:
            WLOG(params, '', params['INPUTS']['TEXT'])

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

# =============================================================================
# End of code
# =============================================================================
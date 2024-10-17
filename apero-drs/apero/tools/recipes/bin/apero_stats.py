#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.tools.module.testing import drs_stats


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_stats.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
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
    # get arguments
    mode = params['INPUTS']['MODE'].upper()
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # set output to None initially
    tout, qout, eout, mout, fout = None, None, None, None, None
    # ----------------------------------------------------------------------
    # run the timing stats
    if 'TIMING' in mode or 'ALL' in mode:
        # add plots to params
        params.set('STATS_TIMING_PLOT', value=True)
        # do the timing stats
        tout = drs_stats.timing_stats(params, recipe)
    # ----------------------------------------------------------------------
    # run the qc stats
    if 'QC' in mode or 'ALL' in mode:
        # add plots to params
        params.set('STAT_QC_RECIPE_PLOT', value=True)
        # do the qc stats
        qout = drs_stats.qc_stats(params, recipe)
    # ----------------------------------------------------------------------
    # run the error stats
    if 'ERROR' in mode or 'ALL' in mode:
        # do the error stats
        eout = drs_stats.error_stats(params)
    # ----------------------------------------------------------------------
    # run the memory stats
    if 'MEMORY' in mode or 'ALL' in mode:
        # do the memory stats
        mout = drs_stats.memory_stats(params, recipe)
    # ----------------------------------------------------------------------
    # run the file index stats
    if 'FINDEX' in mode or 'ALL' in mode:
        # do the file index stats
        fout = drs_stats.file_index_stats(params)
    # ----------------------------------------------------------------------
    # combine all outputs into a single file that can be compared between
    #   runs
    drs_stats.combine_stats(params, [tout, qout, eout, mout, fout])
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

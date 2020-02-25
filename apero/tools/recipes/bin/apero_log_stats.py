#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from apero import core
from apero import locale
from apero.core import constants
from apero.tools.module.testing import drs_log_stats as logstats


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_log_stats.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(instrument=None, **kwargs):
    """
    Main function for apero_log_stats.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(instrument=instrument, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return core.end_main(params, llmain, recipe, success, outputs='None')


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
    # get arguments
    nightname = params['INPUTS']['NIGHTNAME']
    kind = params['INPUTS']['kind']
    recipename = params['INPUTS']['recipe']
    since = params['INPUTS']['since']
    before = params['INPUTS']['before']
    makemaster = params['INPUTS']['master']
    # load path from kind
    if kind == 'red':
        path = params['DRS_DATA_REDUC']
    else:
        path = params['DRS_DATA_WORKING']

    # deal with recipe name
    recipename = logstats.search_recipes(params, recipe, recipename)
    # deal with since value
    since = logstats.get_time(params, since, 'since')
    # deal with before value
    before = logstats.get_time(params, before, 'before')
    # set up plotting (no plotting before this)
    recipe.plot.set_location(0)

    # ----------------------------------------------------------------------
    # Get log files
    # ----------------------------------------------------------------------
    # get log files
    logfiles, nightnames = logstats.get_log_files(params, recipe, path,
                                                  nightname)
    # ----------------------------------------------------------------------
    # Open log files
    # ----------------------------------------------------------------------
    mastertable = logstats.make_log_table(params, logfiles, nightnames,
                                          recipename, since, before)

    # deal with saving master table
    logstats.save_master(params, mastertable, path, recipename, makemaster)

    # ----------------------------------------------------------------------
    # print master stats
    # ----------------------------------------------------------------------
    # Deal with printing stats
    if mastertable is None:
        if recipename is not None:
            # TODO: Add to language database
            wargs = [recipename]
            wmsg = 'No entries found for recipe="{0}"'
            WLOG(params, 'warning', wmsg.format(*wargs))
        else:
            # TODO: Add to language database
            WLOG(params, 'warning', 'No entries found.')
    else:
        if recipename is not None:
            # TODO: Add to language database
            wmsg = '{0} entries found for recipe="{1}"'
            wargs = [len(mastertable), recipename]
            WLOG(params, '', wmsg.format(*wargs))
        else:
            # TODO: Add to language database
            wmsg = '{0} entries found.'
            wargs = [len(mastertable)]
            WLOG(params, '', wmsg.format(*wargs))

    # ----------------------------------------------------------------------
    # print stats
    # ----------------------------------------------------------------------
    if recipename is None:
        logstats.calculate_stats(params, recipe, mastertable)
    else:
        logstats.calculate_recipe_stats(params, mastertable, recipename)

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
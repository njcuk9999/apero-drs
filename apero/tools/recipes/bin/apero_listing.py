#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-09-16 at 13:48

@author: cook
"""
from apero import lang
from apero.base import base
from apero.core.core import drs_text
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_listing.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# get text entry instance
textentry = lang.textentry
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
    Main function for apero_listing.py

    :param instrument: str, the instrument name
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
    return drs_startup.end_main(params, llmain, recipe, success)


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
    mainname = __NAME__ + '._main()'
    # get the night name from inputs
    obs_dir = params['INPUTS']['OBS_DIR']
    # get the kidn from inputs
    block_kind = params['INPUTS']['BLOCK_KIND']
    # get the white list of nights from inputs
    include_list = params['INPUTS']['INCLUDE_OBS_DIRS']
    if drs_text.null_text(include_list, ['None', '', 'All']):
        include_list = None
    else:
        include_list = params['INPUTS'].listp('INCLUDE_OBS_DIRS')
    # get the black list of nights from inputs
    exclude_list = params['INPUTS']['EXCLUDE_OBS_DIRS']
    if drs_text.null_text(exclude_list, ['None', '', 'All']):
        exclude_list = None
    else:
        exclude_list = params['INPUTS'].listp('EXCLUDE_OBS_DIRS')

    # ----------------------------------------------------------------------
    # Deal with kind
    # ----------------------------------------------------------------------
    # deal with kind
    if block_kind.lower() in ['raw', 'tmp', 'red', 'out']:
        # print progress
        WLOG(params, '', textentry('40-005-00006', args=[block_kind]))
        # update the index database (taking into account include/exclude lists)
        indexdbm = drs_utils.update_index_db(params,
                                             block_kind=block_kind.lower(),
                                             includelist=include_list,
                                             excludelist=exclude_list)
    else:
        for blockkind in ['raw', 'tmp', 'red', 'out']:
            # print progress
            WLOG(params, '', textentry('40-005-00006', args=[block_kind]))
            # update the index database (taking into account include/exclude
            #    lists)
            indexdbm = drs_utils.update_index_db(params, block_kind=blockkind,
                                                 includelist=include_list,
                                                 excludelist=exclude_list)

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

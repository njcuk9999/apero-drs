#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:47

@author: cook
"""
from apero import lang
from apero.base import base
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.utils import drs_startup
from apero.tools.module.processing import drs_processing
from apero.tools.module.processing import drs_precheck


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_precheck.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get index database
IndexDatabase = drs_database.IndexDatabase
ObjectDatabase = drs_database.ObjectDatabase
# get text entry instance
textentry = lang.textentry


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(runfile=None, **kwargs):
    """
    Main function for apero_explorer.py

    :param runfile: str, the run file to run (see the /run/ folder)
    :param kwargs: additional keyword arguments

    :type runfile: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(runfile=runfile, **kwargs)
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
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None',
                                keys=['outlist'])


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
    # get run file from inputs
    runfile = params['INPUTS']['RUNFILE']
    file_check = not params['INPUTS']['NO_FILE_CHECK']
    obj_check = not params['INPUTS']['NO_OBJ_CHECK']
    # -------------------------------------------------------------------------
    # Deal with run file
    # -------------------------------------------------------------------------
    # deal with run file
    params, runtable = drs_startup.read_runfile(params, runfile, rkind='run')
    # -------------------------------------------------------------------------
    # find all files via index database (required for both checks)
    # -------------------------------------------------------------------------
    # construct the index database instance
    indexdbm = IndexDatabase(params)
    indexdbm.load_db()
    # force the parallel key to False here (should not be True before we
    #   run processing)
    params['INPUTS']['PARALLEL'] = False
    # update the index database (taking into account include/exclude lists)
    #    we have to loop around block kinds to prevent recipe from updating
    #    the index database every time a new recipe starts
    # this is really important as we have disabled updating for parallel
    #  runs to make it more efficient
    drs_processing.update_index_db(params)

    # fix the header data (object name, dprtype, mjdmid and trg_type etc)
    WLOG(params, '', textentry('40-503-00043'))
    indexdbm.update_header_fix(recipe)
    # -------------------------------------------------------------------------
    # File check
    #    1. check number of calibrations
    #    2. check number of hot stars / science targets
    # -------------------------------------------------------------------------
    if file_check:
        drs_precheck.file_check(params, recipe, indexdbm)

    # -------------------------------------------------------------------------
    # Object check
    # -------------------------------------------------------------------------
    if obj_check:
        drs_precheck.obj_check(params, indexdbm)

    # -------------------------------------------------------------------------
    # End of main code
    # -------------------------------------------------------------------------
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

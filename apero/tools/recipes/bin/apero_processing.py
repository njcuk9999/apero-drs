#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:47

@author: cook
"""
import sys
import traceback

from apero import lang
from apero.base import base
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.utils import drs_startup
from apero.tools.module.processing import drs_processing
from apero.tools.module.database import manage_databases

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_processing.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get index database
IndexDatabase = drs_database.FileIndexDatabase
ObjectDatabase = drs_database.AstrometricDatabase
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

    :param instrument: str, the instrument name
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
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get run file from inputs
    runfile = params['INPUTS']['RUNFILE']
    # set up drs group (for logging)
    groupname = drs_startup.group_name(params)

    # ----------------------------------------------------------------------
    # Deal with run file
    # ----------------------------------------------------------------------
    # deal with run file
    params, runtable = drs_startup.read_runfile(params, runfile, recipe,
                                                rkind='run')
    # reset sys.argv so it doesn't mess with recipes
    sys.argv = [__NAME__]

    # -------------------------------------------------------------------------
    # Send email about starting
    # -------------------------------------------------------------------------
    # send email if configured
    drs_processing.processing_email(params, 'start', __NAME__)
    # -------------------------------------------------------------------------
    # everything else in a try (to log end email even with exception)
    try:
        # ----------------------------------------------------------------------
        # Update the object database (recommended only for full reprocessing)
        # ----------------------------------------------------------------------
        # check that we have entries in the object database
        has_entries = manage_databases.object_db_populated(params)
        # update the database if required
        if params['UPDATE_OBJ_DATABASE'] or not has_entries:
            manage_databases.update_object_database(params)
        # load the object database
        objdbm = ObjectDatabase(params)
        objdbm.load_db()
        # ----------------------------------------------------------------------
        # Update the reject database (recommended only for full reprocessing)
        # ----------------------------------------------------------------------
        # check that we have entries in the object database
        has_entries = manage_databases.reject_db_populated(params)
        # update the database if required
        if params['UPDATE_REJECT_DATABASE'] or not has_entries:
            manage_databases.update_reject_database(params)
        # ---------------------------------------------------------------------
        # find all files via index database
        # ---------------------------------------------------------------------
        # construct the index database instance
        findexdbm = IndexDatabase(params)
        findexdbm.load_db()
        # there are a few use cases where we want to skip updating the index
        #   database
        if params['UPDATE_FILEINDEX_DATABASE']:
            # force the parallel key to False here (should not be True
            #   before we run processing)
            params['INPUTS']['PARALLEL'] = False
            # update the index database (taking into account include/exclude
            #    lists) we have to loop around block kinds to prevent recipe
            #    from updating the index database every time a new recipe
            #    starts this is really important as we have disabled updating
            #    for parallel runs to make it more efficient
            drs_processing.update_index_db(params)

        # fix the header data (object name, dprtype, mjdmid and
        #     trg_type etc)
        WLOG(params, '', textentry('40-503-00043'))
        findexdbm.update_header_fix(recipe, objdbm=objdbm)

        # find all previous runs
        skiptable = drs_processing.generate_skip_table(params)

        # ----------------------------------------------------------------------
        # Generate run list
        # ----------------------------------------------------------------------
        rlist = drs_processing.generate_run_list(params, findexdbm, runtable,
                                                 skiptable)

        # ----------------------------------------------------------------------
        # Process run list
        # ----------------------------------------------------------------------
        out = drs_processing.process_run_list(params, rlist, groupname,
                                              findexdbm)
        outlist, has_errors, ptime = out

        # ----------------------------------------------------------------------
        # Print timing
        # ----------------------------------------------------------------------
        drs_processing.display_timing(params, outlist, ptime)

        # ----------------------------------------------------------------------
        # Print out any errors
        # ----------------------------------------------------------------------
        if has_errors:
            drs_processing.display_errors(params, outlist)

        # ----------------------------------------------------------------------
        # Compile some useful information as summary
        # ----------------------------------------------------------------------
        drs_processing.save_stats(params, outlist)

        # ----------------------------------------------------------------------
        # Send email about finishing
        # ----------------------------------------------------------------------
        # send email if configured
        drs_processing.processing_email(params, 'end', __NAME__)

    except Exception as e:
        # ---------------------------------------------------------------------
        # Send email about finishing
        # ---------------------------------------------------------------------
        # get traceback
        string_trackback = traceback.format_exc()
        # send email if configured
        drs_processing.processing_email(params, 'end', __NAME__,
                                        tb=string_trackback)
        # raise exception
        raise e
    except KeyboardInterrupt as e:
        # ---------------------------------------------------------------------
        # Send email about finishing
        # ---------------------------------------------------------------------
        # get traceback
        string_trackback = traceback.format_exc()
        # send email if configured
        drs_processing.processing_email(params, 'end', __NAME__,
                                        tb=string_trackback)
        # raise exception
        raise e
    except SystemExit as e:
        # ---------------------------------------------------------------------
        # Send email about finishing
        # ---------------------------------------------------------------------
        # get traceback
        string_trackback = traceback.format_exc()
        # send email if configured
        drs_processing.processing_email(params, 'end', __NAME__,
                                        tb=string_trackback)
        # raise exception
        raise e

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

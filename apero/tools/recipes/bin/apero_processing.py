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
from apero.core.core import drs_file
from apero.core.core import drs_database
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
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
IndexDatabase = drs_database.IndexDatabase
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

    :type instrument: str
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
    params, runtable = drs_processing.read_runfile(params, runfile)
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
        # ---------------------------------------------------------------------
        # find all files via index database
        # ---------------------------------------------------------------------
        includelist = params.listp('INCLUDE_OBS_DIRS', dtype=str)
        excludelist = params.listp('EXCLUDE_OBS_DIRS', dtype=str)
        reindexlist = params.listp('REPROCESS_REINDEX_BLOCKS', dtype=str)
        # get all block kinds
        block_kinds = drs_file.DrsPath.get_block_names(params=params,
                                                       block_filter='indexing')
        # construct the index database instance
        indexdbm = IndexDatabase(params)
        # force the parallel key to False here (should not be True before we
        #   run processing)
        params['INPUTS']['PARALLEL'] = False
        # update the index database (taking into account include/exclude lists)
        #    we have to loop around block kinds to prevent recipe from updating
        #    the index database every time a new recipe starts
        for block_kind in block_kinds:
            # deal with reindexing
            if block_kind not in reindexlist:
                continue
            # log block update
            WLOG(params, '', textentry('40-503-00044', args=[block_kind]))
            # update index database for block kind
            indexdbm = drs_utils.update_index_db(params, block_kind=block_kind,
                                                 includelist=includelist,
                                                 excludelist=excludelist,
                                                 indexdbm=indexdbm)
        # fix the header data (object name, dprtype, mjdmid and trg_type etc)
        WLOG(params, '', textentry('40-503-00043'))
        indexdbm.update_header_fix(recipe)

        # find all previous runs
        skiptable = drs_processing.generate_skip_table(params)

        # ----------------------------------------------------------------------
        # Update the object database (recommended only for full reprocessing)
        # ----------------------------------------------------------------------
        if params['UPDATE_OBJ_DATABASE']:
            manage_databases.update_object_database(params)

        # ----------------------------------------------------------------------
        # Generate run list
        # ----------------------------------------------------------------------
        rlist = drs_processing.generate_run_list(params, indexdbm, runtable,
                                                 skiptable)

        # ----------------------------------------------------------------------
        # Process run list
        # ----------------------------------------------------------------------
        out = drs_processing.process_run_list(params, recipe, rlist, groupname)
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

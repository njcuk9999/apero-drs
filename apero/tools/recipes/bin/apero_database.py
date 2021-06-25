#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from pathlib import Path

from apero import lang
from apero.base import base
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_startup
from apero.tools.module.database import manage_databases
from apero.tools.module.database import database_update
from apero.tools.module.database import manage_db_gui

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_database.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_explorer.py

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
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       enable_plotter=False)
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


def __main__(recipe, params):
    """
    Main function - takes the instrument name, index the databases and python
    script (in real time due to any changes in code) and then runs the
    application to find errors

    :param instrument: string, the instrument name
    :type: str
    :return: returns the local namespace as a dictionary
    :rtype: dict
    """

    # deal with killing sleeping processes
    if params['INPUTS']['KILL']:
        # kill all user processes in the database that have been running for
        manage_databases.kill(params, timeout=60)
        # ------------------------------------------------------------------
        # End of main code
        # ------------------------------------------------------------------
        return drs_startup.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # deal with update
    # ----------------------------------------------------------------------
    if not drs_text.null_text(params['INPUTS']['OBJDB'], ['None', '', 'Null']):
        # update database
        database_update.update_obj_reset(params)
        # ------------------------------------------------------------------
        # End of main code
        # ------------------------------------------------------------------
        return drs_startup.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # deal with delete gui
    # ----------------------------------------------------------------------
    if params['INPUTS']['DELETE']:
        # load delete database app
        manage_db_gui.run_delete_table_app(recipe, params)
        # ------------------------------------------------------------------
        # End of main code
        # ------------------------------------------------------------------
        return drs_startup.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # deal with update
    # ----------------------------------------------------------------------
    if params['INPUTS']['UPDATE']:
        # update database
        database_update.update_database(params, recipe)
        # ------------------------------------------------------------------
        # End of main code
        # ------------------------------------------------------------------
        return drs_startup.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # get csv file path
    # ----------------------------------------------------------------------
    # get it from input parameters
    csvpath = params['INPUTS'].get('CSV', 'None')
    # deal with no csv file
    if drs_text.null_text(csvpath, ['None', '']):
        # log error: Argument Error: --csv file is required'
        WLOG(params, 'error', textentry('09-507-00001'))
        csvpath = None
    else:
        csvpath = Path(csvpath)
    # ----------------------------------------------------------------------
    # deal with export mode
    # ----------------------------------------------------------------------
    # get the database name
    database_name = params['INPUTS'].get('EXPORTDB', 'None')
    # only export if we exportdb is not None
    if not drs_text.null_text(database_name, ['None', '']):
        # export database
        manage_databases.export_database(params, database_name,
                                         csvpath)
        # ------------------------------------------------------------------
        # End of main code
        # ------------------------------------------------------------------
        return drs_startup.return_locals(params, locals())
    # ----------------------------------------------------------------------
    # deal with import mode
    # ----------------------------------------------------------------------
    # get the database name
    database_name = params['INPUTS'].get('IMPORTDB', 'None')
    # get join type
    joinmode = params['INPUTS'].get('JOIN', 'replace')
    # deal with import mode not set
    if not drs_text.null_text(database_name, ['None', '']):
        # import csv file into database
        manage_databases.import_database(params, database_name,
                                         csvpath, joinmode)
        # ------------------------------------------------------------------
        # End of main code
        # ------------------------------------------------------------------
        return drs_startup.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # If we got here user did not define export or import
    # ----------------------------------------------------------------------
    # log error
    emsg = 'Argument Error: Must define either --exportdb or --importdb'
    WLOG(params, 'error', emsg)
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

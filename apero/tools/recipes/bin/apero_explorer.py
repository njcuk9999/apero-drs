#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from pathlib import Path

from apero.base import base
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils

from apero.tools.module.database import manage_databases
from apero.tools.module.database import database_gui

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_explorer.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# -----------------------------------------------------------------------------
# define the program name
PROGRAM_NAME = 'APERO File Explorer'
# define the default path
ALLOWED_PATHS = ['DRS_DATA_WORKING', 'DRS_DATA_REDUC']
# -----------------------------------------------------------------------------


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

    # get inputs
    inputs = params['INPUTS']
    null_text = ['None', '', 'Null']
    # flag mode
    cond1 = drs_text.null_text(inputs.get('RECIPE', None), null_text)
    cond2 = drs_text.null_text(inputs.get('FLAGNUM', None), null_text)

    if not cond1 and not cond2:
        # get flags
        drs_utils.display_flag(params)
        # ----------------------------------------------------------------------
        # End of main code
        # ----------------------------------------------------------------------
        return drs_startup.return_locals(params, locals())

    # get instrument
    instrument = str(recipe.instrument)
    # get hash col argument from inputs
    hash_col = inputs.get('hash', False)
    # get databases
    dbs = manage_databases.list_databases(params)
    # push into database holder
    databases = dict()
    for key in dbs:
        databases[key] = database_gui.DatabaseHolder(params, name=key,
                                                     kind=dbs[key].kind,
                                                     path=Path(dbs[key].path),
                                                     hash_col=hash_col)
    # construct app
    app = database_gui.DatabaseExplorer(databases=databases)
    # set icon?
    app.set_icon()
    # launch the app
    app.mainloop()

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

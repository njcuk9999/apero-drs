#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from apero.core import constants
from apero import core
from apero.tools.module.listing import file_explorer

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_explorer.py'
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
# -----------------------------------------------------------------------------
# define the program name
PROGRAM_NAME = 'APERO File Explorer'
# define the default path
ALLOWED_PATHS = ['DRS_DATA_WORKING', 'DRS_DATA_REDUC']
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def main(instrument=None, **kwargs):
    """
    Main function for cal_dark_spirou.py

    :param directory: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(instrument=instrument, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                enable_plotter=False)
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
    Main function - takes the instrument name, index the databases and python
    script (in real time due to any changes in code) and then runs the
    application to find errors

    :param instrument: string, the instrument name
    :type: str
    :return: returns the local namespace as a dictionary
    :rtype: dict
    """
    # get instrument
    instrument = params['INPUTS']['INSTRUMENT']
    # Log that we are running indexing
    WLOG(params, '', 'Indexing files at {0}'.format(params[ALLOWED_PATHS[0]]))
    # load data
    datastore = file_explorer.LoadData(instrument, recipe, params)
    # Log that we are running indexing
    WLOG(params, '', 'Running file explorer application')
    # Main code here
    app = file_explorer.App(datastore=datastore)
    app.geometry("1024x768")
    app.mainloop()
    # end with a log message
    WLOG(datastore.params, '', 'Program has completed successfully')
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

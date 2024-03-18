#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from apero import lang
from apero.base import base
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.setup import drs_reset

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_remove.py'
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
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for apero_reset.py

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
    # get log and warn from inputs
    obsdir = params['INPUTS']['obsdir']
    fileprefix = params['INPUTS']['file_prefix']
    filesuffix = params['INPUTS']['file_suffix']
    warn = not params['INPUTS']['nowarn']

    # if any are set to 'None' then set to None
    if obsdir == 'None':
        obsdir = None
    if fileprefix == 'None':
        fileprefix = None
    if filesuffix == 'None':
        filesuffix = None
    if params['INPUTS']['test'] == 'None':
        params['INPUTS'].set('test', value=False)
    # deal with non test mode - ask the user
    if not params['INPUTS']['test'] and warn:
        msg = ('Warning this will remove files from disk and the database '
               'are you sure you want to continue?')
        # get user input
        user_input = input(msg + '\n\t[Y]es or [N]o')
        if 'Y' not in user_input.upper():
            params['INPUTS'].set('test', value=True)
        else:
            params['INPUTS'].set('test', value=False)

    # ----------------------------------------------------------------------
    # Must check that we are not inside an apero directory (for safety)
    drs_reset.check_cwd(params)

    # ----------------------------------------------------------------------
    # get a list of files to remove (using the file index database)
    filetable, condition = drs_reset.get_filelist(params, obsdir, fileprefix,
                                                  filesuffix)

    # ----------------------------------------------------------------------
    # remove the files from disk
    disk_entries = drs_reset.remove_files_from_disk(params, filetable)

    # ----------------------------------------------------------------------
    # remove files from database
    db_entries = drs_reset.remove_files_from_databases(params, filetable,
                                                       condition)

    # ----------------------------------------------------------------------
    if params['INPUTS']['test']:
        msg1 = 'Would have removed {0} files from disk'
        msg2 = 'Would have removed {0} entries from database {1}'
    else:
        msg1 = 'Removed {0} files from disk'
        msg2 = 'Removed {0} entries from database {1}'

    # print stats on removed files
    WLOG(params, 'info', msg1.format(disk_entries))
    # print stats on removed database entries
    for db_key in db_entries:
        WLOG(params, 'info', msg2.format(db_entries[db_key], db_key))

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

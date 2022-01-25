#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
import argparse
import sys
from typing import Any, Dict

from apero.base import base
from apero.base import drs_db
from apero.lang.core import drs_lang
from apero.tools.module.database import manage_databases
from apero.tools.module.error import find_error


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_langdb.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# define the drs name (and module name)
DRS_PATH = __PACKAGE__
# Define text (cannot use lanugage database to make language database)
LANGDB_DESC = 'Language database tools'
LANGDB_FIND_HELP = 'Displays the message locator GUI'
LANGDB_UPDATE_HELP = ('Updates local language database and local text files '
                      'with any changes')
LANGDB_RELOAD_HELP = ('Reloads the local language database (with text file '
                      'changes)')


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in __main__
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
def get_args() -> Dict[str, Any]:
    """
    Apero go should be quick
    :return:
    """
    # Note: Cannot use language database here (i.e. no recipe definitions)
    # get parser
    description = LANGDB_DESC
    parser = argparse.ArgumentParser(description=description)
    # add the find argument
    parser.add_argument('--find', action='store_true', default=False,
                        dest='find', help=LANGDB_FIND_HELP)
    # add the update argument
    parser.add_argument('--update', '--upgrade', action='store_true',
                        default=False, dest='update', help=LANGDB_UPDATE_HELP)
    # add the reload argument
    parser.add_argument('--reload', action='store_true', default=False,
                        dest='reload', help=LANGDB_RELOAD_HELP)
    # parse arguments
    args = parser.parse_args()
    # return as dictionary
    return dict(vars(args))


def main():
    # Note: cannot use any package other than apero.lang - as we are
    #       updating the language in this package

    # get arguments
    params = dict()
    params['INPUTS'] = get_args()

    # link --find to the
    if params['INPUTS']['find']:
        # need to reset sys.argv
        sys.argv = [__NAME__]
        # return results of find_error.main()
        return find_error.main()

    # if we are updating database then run
    if params['INPUTS']['update']:
        # make the reset files
        drs_lang.make_reset_csvs()
        # make the databases list (but only language database)
        print('Updating Language Database')
        databases = dict()
        landdbm = drs_db.LanguageDatabase(check=False)
        databases['lang'] = landdbm
        # create the database
        manage_databases.create_lang_database(databases)
        # return None
        return

    # if we are just reloading just reload the language database
    if params['INPUTS']['reload']:
        # make the databases list (but only language database)
        print('Reloading Language Database')
        databases = dict()
        landdbm = drs_db.LanguageDatabase(check=False)
        databases['lang'] = landdbm
        # create the database
        manage_databases.create_lang_database(databases)

    else:
        print('No option selected. See --help for options')


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run main function
    ll = main()

# =============================================================================
# End of code
# =============================================================================

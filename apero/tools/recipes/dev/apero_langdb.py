#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
import sys

from apero.base import base
from apero.base import drs_db
from apero.lang.core import drs_lang
from apero.tools.module.database import manage_databases

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

# the help message
HELP_MESSAGE = """
 ***************************************************************************
 Help for: 'apero_langdb.py'
 ***************************************************************************
	NAME: setup/install.py
	AUTHORS: N. Cook, E. Artigau, F. Bouchy, M. Hobson, C. Moutou, 
	         I. Boisse, E. Martioli

 Usage: apero_langdb.py [options]


 ***************************************************************************
 Description:
 ***************************************************************************

 Install {0} software for reducing observational data

 ***************************************************************************

Arguments:

--update       updates installation (not clean install) and checks for
               updates to your current config files

--upgrade      (see --update)

--help, -h     show this help message and exit

 ***************************************************************************

"""


# =============================================================================
# Define functions
# =============================================================================
def main():
    # Note: cannot use any package other than apero.lang - as we are
    #       updating the language in this package

    # get arguments
    args = sys.argv
    # Help
    if '--help' in args or '-h' in args:
        # print the help message
        print(HELP_MESSAGE.format(DRS_PATH))
        # return None
        return

    # if we are updating database then run
    if '--update' in args or '--upgrade' in args:
        # make the reset files
        drs_lang.make_reset_csvs()
        # make the databases list (but only language database)
        print('Creating Language Database')
        databases = dict()
        landdbm = drs_db.LanguageDatabase(check=False)
        databases['lang'] = landdbm
        # create the database
        manage_databases.create_lang_database(databases)
        # return None
        return
    else:
        print('No option selected. See --help for options')


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run main function
    main()

# =============================================================================
# End of code
# =============================================================================

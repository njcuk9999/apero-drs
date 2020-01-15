#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
import sys

from apero.locale.core import port_database


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_langdb.py'
__INSTRUMENT__ = 'None'
# define the drs name (and module name)
DRS_PATH = 'apero'

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
    # Note: cannot use any package other than apero.locale - as we are
    #       updating the language in this package

    # get arguments
    args = sys.argv
    # Help
    if '--help' in args or '-h' in args:
        print(HELP_MESSAGE.format(DRS_PATH))
        return

    # if we are updating database then run
    if '--update' in args or '--upgrade' in args:
        port_database.main()
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

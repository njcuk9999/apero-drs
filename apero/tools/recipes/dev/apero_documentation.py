#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-01-07 at 14:59

@author: cook
"""
import os
import shutil

from apero import core
from apero.core import constants
from apero import locale
from apero.tools.module.documentation import drs_documentation

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_documentation.py'
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
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# --------------------------------------------------------------------------



# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_documentation.py

    :param kwargs: any additional keywords

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
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
    # Note: no instrument defined so do not use instrument only features

    # ----------------------------------------------------------------------
    # compile documentation
    drs_documentation.compile_docs(params)


    # upload to server
    if params['INPUTS']['UPLOAD']:
        drs_documentation.upload(params)

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
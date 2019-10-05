#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 13:57

@author: cook
"""
from __future__ import division
import traceback

from terrapipe.core import constants
from terrapipe import core
from terrapipe import locale

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'test_recipe.py'
__INSTRUMENT__ = 'NIRPS'
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
Entry = locale.drs_text.Entry
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def __main__(recipe, params):
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # display everything that comes from "INPUT"
    for i in range(10):
        WLOG(params, '', 'Line {0} of code'.format(i+1))
    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, locals())


def main(directory=None, filelist=None, **kwargs):
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, filelist=filelist, **kwargs)
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

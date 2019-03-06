#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:38
@author: ncook
Version 0.0.1
"""
from __future__ import division
import traceback

from drsmodule import constants
from drsmodule import config
from drsmodule import locale

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'blank.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = config.wlog
# Get the text types
ErrorEntry = locale.drs_text.ErrorEntry


# =============================================================================
# Define functions
# =============================================================================
def _main(recipe, params):
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return dict(locals())


def main(directory=None, files=None, **kwargs):
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, files=files, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = config.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    try:
        llmain = _main(recipe, params)
        success = True
    except Exception as e:
        string_trackback = traceback.format_exc()
        success = False
        emsg = ErrorEntry('01-010-00001', args=[type(e)])
        emsg += '\n\n' + ErrorEntry(string_trackback)
        WLOG(params, 'error', emsg, raise_exception=False)
        llmain = dict()
    except SystemExit as e:
        success = False
        llmain = dict()
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    params = config.end_main(params, success, outputs='None')
    # return a copy of locally defined variables in the memory
    return config.get_locals(dict(locals()), llmain)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    config.end(ll, has_plots=True)

# =============================================================================
# End of code
# =============================================================================
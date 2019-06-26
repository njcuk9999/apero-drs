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
__INSTRUMENT__ = 'SPIROU'
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
def _main(recipe, params):
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # display everything that comes from "INPUT"
    for i in range(10):
        WLOG(params, '', 'Line {0} of code'.format(i+1))
    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return dict(locals())


def main(directory=None, filelist1=None, filelist2=None, **kwargs):
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, filelist1=filelist1,
                   filelist2=filelist2, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    try:
        llmain = _main(recipe, params)
        success = True
    except Exception as e:
        string_trackback = traceback.format_exc()
        success = False
        emsg = Entry('01-010-00001', args=[type(e)])
        emsg += '\n\n' + Entry(string_trackback)
        WLOG(params, 'error', emsg, raise_exception=False)
        llmain = dict()
    except SystemExit as e:
        success = False
        llmain = dict()
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    params = core.end_main(params, success, outputs='None')
    # return a copy of locally defined variables in the memory
    return core.get_locals(dict(locals()), llmain)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    core.end(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================

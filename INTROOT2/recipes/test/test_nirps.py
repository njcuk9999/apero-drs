#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 13:57

@author: cook
"""
from __future__ import division

from drsmodule import constants
from drsmodule import config

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
WLOG = config.wlog
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def main(directory=None, filelist=None, **kwargs):
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, filelist=filelist, **kwargs)
    # deal with command line inputs / function call inputs
    recipe, p = config.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # display everything that comes from "INPUT"
    for i in range(10):
        WLOG(p, '', 'Line {0} of code'.format(i+1))
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = config.end_main(p, outputs='None')
    # return a copy of locally defined variables in the memory
    return dict(locals())


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

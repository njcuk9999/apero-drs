#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get files with specific filters

Created on 2021-06-11

@author: cook
"""
import numpy as np
import os
import shutil
from typing import Dict, List, Tuple

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_text
from apero.core.utils import drs_startup
from apero.tools.module.listing import drs_get

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_get.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
ParamDict = constants.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_explorer.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       enable_plotter=False)
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
    Main function - using user inputs (or gui inputs) filters files and
    copies them to a new location

    :param instrument: string, the instrument name
    :type: str
    :return: returns the local namespace as a dictionary
    :rtype: dict
    """
    # get inputs from user
    inputs = params['INPUTS']
    use_gui = params['INPUTS']['GUI']
    if use_gui:
        WLOG(params, 'warning', 'Not Implemented yet',
             sublevel=2)
        return drs_startup.return_locals(params, locals())
    # get filters from user inputs
    kw_objnames = inputs.listp('objnames', dtype=str, required=False)
    kw_dprtypes = inputs.listp('dprtypes', dtype=str, required=False)
    kw_outputs = inputs.listp('outtypes', dtype=str, required=False)
    kw_fibers = inputs.listp('fibers', dtype=str, required=False)
    # get outpath from user inputs
    user_outdir = params['INPUTS']['OUTPATH']
    if drs_text.null_text(user_outdir, ['None', '', 'Null']):
        user_outdir = os.getcwd()
    # get copy criteria from user inputs
    do_copy = not params['INPUTS']['TEST']
    # get sym link criteria from user inputs
    do_symlink = params['INPUTS']['SYMLINKS']
    # check for None
    if drs_text.null_text(kw_objnames, ['None', '', 'Null']):
        kw_objnames = None
    if drs_text.null_text(kw_dprtypes, ['None', '', 'Null']):
        kw_dprtypes = None
    if drs_text.null_text(kw_outputs, ['None', '', 'Null']):
        kw_outputs = None
    if drs_text.null_text(kw_fibers, ['None', '', 'Null']):
        kw_fibers = None
    # push filters into dictionary (not object names these are special)
    filters = dict()
    filters['KW_DPRTYPE'] = kw_dprtypes
    filters['KW_OUTPUT'] = kw_outputs
    filters['KW_FIBER'] = kw_fibers
    # run basic filter
    indict, outdict = drs_get.basic_filter(params, kw_objnames, filters,
                                           user_outdir, do_copy, do_symlink)
    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

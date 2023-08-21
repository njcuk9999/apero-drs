#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get files with specific filters

Created on 2021-06-11

@author: cook
"""
import os
from typing import Any, Dict

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
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
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict
# get time from base
Time = base.Time


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_explorer.py

    :param kwargs: additional keyword arguments

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


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """
    Main function - using user inputs (or gui inputs) filters files and
    copies them to a new location

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # get copy criteria from user inputs
    do_copy = not params['INPUTS']['TEST']
    # get sym link criteria from user inputs
    do_symlink = params['INPUTS']['SYMLINKS']
    # get outpath from user inputs
    user_outdir = params['INPUTS']['OUTPATH']
    if drs_text.null_text(user_outdir, ['None', '', 'Null']):
        user_outdir = os.getcwd()
        current = True
    else:
        current = False

    if drs_text.true_text(params['INPUTS']['NOSUBDIR']):
        nosubdir = True
    else:
        nosubdir = False
    # -------------------------------------------------------------------------
    # deal with tar files
    if drs_text.true_text(params['INPUTS']['TAR']):
        tarfilename = params['INPUTS']['TARFILE']
        # overwrite symlink, copy and nosubdir arguments
        do_symlink = False
        do_copy = True
        nosubdir = True
    else:
        tarfilename = None
    # -------------------------------------------------------------------------
    # get inputs from user
    inputs = params['INPUTS']
    use_gui = params['INPUTS']['GUI']
    if use_gui:
        WLOG(params, 'warning', 'Not Implemented yet',
             sublevel=2)
        return locals()
    # -------------------------------------------------------------------------
    # get filters from user inputs
    kw_objnames = inputs.listp('objnames', dtype=str, required=False)
    kw_dprtypes = inputs.listp('dprtypes', dtype=str, required=False)
    kw_outputs = inputs.listp('outtypes', dtype=str, required=False)
    kw_fibers = inputs.listp('fibers', dtype=str, required=False)
    since = inputs.get('SINCE', None)
    latest = inputs.get('LATEST', None)
    kw_obsdir = inputs.listp('OBSDIR', dtype=str, required=False)
    kw_pi_name = inputs.listp('PI_NAME', dtype=str, required=False)
    kw_runids = inputs.listp('RUNID', dtype=str, required=False)

    # -------------------------------------------------------------------------
    # test that since value is a valid time
    if not drs_text.null_text(since, ['None', '', 'Null']):
        try:
            since = Time(since).iso
            msg = 'Using --since={0}'
            margs = [since]
            WLOG(params, '', msg.format(*margs))
        except Exception as _:
            # TODO: move to language database
            emsg = '--since={0} is not a valid time YYYY-MM-DD hh:mm:ss'
            eargs = [since]
            WLOG(params, 'error', emsg.format(*eargs))
    else:
        since = None
    # -------------------------------------------------------------------------
    # test that since value is a valid time
    if not drs_text.null_text(latest, ['None', '', 'Null']):
        try:
            latest = Time(latest).iso
            msg = 'Using --latest={0}'
            margs = [latest]
            WLOG(params, '', msg.format(*margs))
        except Exception as _:
            # TODO: move to language database
            emsg = '--latest={0} is not a valid time YYYY-MM-DD hh:mm:ss'
            eargs = [latest]
            WLOG(params, 'error', emsg.format(*eargs))
    else:
        latest = None
    # -------------------------------------------------------------------------
    # check for None / *
    if drs_text.null_text(kw_objnames, ['None', '', 'Null']):
        kw_objnames = None
    elif '*' in kw_objnames:
        kw_objnames = drs_get.all_objects(params)
    if drs_text.null_text(kw_dprtypes, ['None', '', 'Null', '*']):
        kw_dprtypes = None
    if drs_text.null_text(kw_outputs, ['None', '', 'Null', '*']):
        kw_outputs = None
    if drs_text.null_text(kw_fibers, ['None', '', 'Null', '*']):
        kw_fibers = None
    if drs_text.null_text(kw_obsdir, ['None', '', 'Null', '*']):
        kw_obsdir = None
    if drs_text.null_text(kw_pi_name, ['None', '', 'Null', '*']):
        kw_pi_name = None
    if drs_text.null_text(kw_runids, ['None', '', 'Null', '*']):
        kw_runids = None
    # -------------------------------------------------------------------------
    # push filters into dictionary (not object names these are special)
    filters = dict()
    filters['KW_DPRTYPE'] = kw_dprtypes
    filters['KW_OUTPUT'] = kw_outputs
    filters['KW_FIBER'] = kw_fibers
    filters['OBS_DIR'] = kw_obsdir
    filters['KW_PI_NAME'] = kw_pi_name
    filters['KW_RUN_ID'] = kw_runids
    # run basic filter
    indict, outdict = drs_get.basic_filter(params, kw_objnames, filters,
                                           user_outdir, do_copy, do_symlink,
                                           tarfilename=tarfilename,
                                           since=since, latest=latest,
                                           nosubdir=nosubdir)
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

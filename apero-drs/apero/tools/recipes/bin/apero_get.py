#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get files with specific filters

Created on 2021-06-11

@author: cook
"""
import os
from typing import Any, Dict

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.tools.module.listing import drs_get
from apero.tools.module.setup import drs_assets
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_get.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
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
        nosubdir = True
    else:
        tarfilename = None
    # -------------------------------------------------------------------------
    # get the database type (usually findex)
    dbkind = params['INPUTS']['DBKIND']
    # -------------------------------------------------------------------------
    # get inputs from user
    inputs = params['INPUTS']
    use_gui = params['INPUTS']['GUI']
    if use_gui:
        WLOG(params, 'warning', 'Not Implemented yet',
             sublevel=2)
        return locals()
    # -------------------------------------------------------------------------
    # get input from user
    get_assets = drs_text.true_text(inputs['ASSETS'])
    # get assets
    if get_assets:
        update_assets = drs_assets.check_local_assets(params)
        if update_assets:
            drs_assets.update_local_assets(params)
        return locals()
    # -------------------------------------------------------------------------
    # get filters from user inputs
    kw_objnames = inputs['objnames']
    kw_dprtypes = inputs['dprtypes']
    kw_outputs = inputs['outtypes']
    kw_fibers = inputs['fibers']
    since = inputs.get('SINCE', None)
    latest = inputs.get('LATEST', None)
    timekey = inputs.get('TIMEKEY', 'observed')
    kw_obsdir = inputs['OBSDIR']
    kw_pi_name = inputs['PI_NAME']
    kw_runids = inputs['RUNID']
    sizelimit = inputs.get('SIZELIMIT', None)
    keyname = inputs['keynames']
    # -------------------------------------------------------------------------
    # test that since value is a valid time
    if not drs_text.null_text(since, ['None', '', 'Null']):
        try:
            since = Time(since)
            msg = 'Using --since={0}'
            margs = [since]
            WLOG(params, '', msg.format(*margs))
        except Exception as _:
            # TODO: move to language database
            emsg = '--since={0} is not a valid time YYYY-MM-DD hh:mm:ss'
            eargs = [since]
            raise AperoCodedException(params, 'error', emsg.format(*eargs),
                                      targs=eargs)
    else:
        since = None
    # -------------------------------------------------------------------------
    # test that since value is a valid time
    if not drs_text.null_text(latest, ['None', '', 'Null']):
        try:
            latest = Time(latest)
            msg = 'Using --latest={0}'
            margs = [latest]
            WLOG(params, '', msg.format(*margs))
        except Exception as _:
            # TODO: move to language database
            emsg = '--latest={0} is not a valid time YYYY-MM-DD hh:mm:ss'
            eargs = [latest]
            raise AperoCodedException(params, 'error', emsg.format(*eargs),
                                      targs=eargs)
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
    if drs_text.null_text(keyname, ['None', '', 'Null', '*']):
        keyname = None
    # -------------------------------------------------------------------------
    # deal with some Kw_outputs not using fibers (fibers will be set to None)
    kw_fibers = drs_get.fiber_by_output(kw_fibers, kw_outputs)
    # -------------------------------------------------------------------------
    # push filters into dictionary (not object names these are special)
    filters = dict()
    filters['KW_DPRTYPE'] = kw_dprtypes
    filters['KW_OUTPUT'] = kw_outputs
    filters['KEYNAME'] = keyname
    filters['KW_FIBER'] = kw_fibers
    filters['OBS_DIR'] = kw_obsdir
    filters['KW_PI_NAME'] = kw_pi_name
    filters['KW_RUN_ID'] = kw_runids
    # -------------------------------------------------------------------------
    # run basic filter
    if dbkind == 'calib':
        indict, outdict = drs_get.calib_filter(params, filters,
                                               user_outdir, do_copy, do_symlink,
                                               tarfilename=tarfilename,
                                               since=since, latest=latest,
                                               sizelimit=sizelimit)
    elif dbkind == 'tellu':
        indict, outdict = drs_get.tellu_filter(params, kw_objnames, filters,
                                               user_outdir, do_copy, do_symlink,
                                               tarfilename=tarfilename,
                                               since=since, latest=latest,
                                               sizelimit=sizelimit)
    else:
        indict, outdict = drs_get.basic_filter(params, kw_objnames, filters,
                                               user_outdir, do_copy, do_symlink,
                                               tarfilename=tarfilename,
                                               since=since, latest=latest,
                                               nosubdir=nosubdir,
                                               sizelimit=sizelimit)
    # -------------------------------------------------------------------------
    # push some variables to params
    params.set('INDICT', indict)
    params.set('OUTDICT', outdict)
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

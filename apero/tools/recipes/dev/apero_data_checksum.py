#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code to update checksums for all data files

Created on 2021-01-2021-01-13 14:42

@author: cook
"""
import os

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_startup
from apero.tools.module.testing import drs_dev
from apero.tools.module.setup import drs_assets

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_constants.py'
__INSTRUMENT__ = base.IPARAMS['INSTRUMENT']
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# get file definitions for this instrument
FMOD = drs_dev.FileDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
apero_dcheck = drs_dev.TmpRecipe()
apero_dcheck.name = __NAME__
apero_dcheck.shortname = 'APERO_DCHECK'
apero_dcheck.instrument = __INSTRUMENT__
apero_dcheck.in_block_str = 'red'
apero_dcheck.out_block_str = 'red'
apero_dcheck.extension = 'fits'
apero_dcheck.description = ('Developer functionality dealing with local/remote asset data files.      '
                            'mode=update-remote - creates a new tar on the server from local assets'
                            'mode=check-local - checks whether the local assets need updating from server'
                            'mode=update-local - update local assets from server')
apero_dcheck.kind = 'misc'
apero_dcheck.set_debug_plots()
apero_dcheck.set_summary_plots()

apero_dcheck.set_arg(pos=0, name='mode', dtype=str,
                     helpstr='Mode of operation (update-remote, check-local, update-local)        '
                            'mode=update-remote - creates a new tar on the server from local assets'
                            'mode=check-local - checks whether the local assets need updating from server'
                            'mode=update-local - update local assets from server')
apero_dcheck.set_kwarg(name='--indir', dtype=str, default='None',
                       helpstr='Input data directory. If set recreates '
                               'checksums and tar file from --indir')
apero_dcheck.set_kwarg(name='--tarfile', dtype=str, default='None',
                       helpstr='Force a local assets tar file to be used '
                               '(If correct does not download from server)')
# add recipe to recipe definition
RMOD.add(apero_dcheck)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for exposuremeter_spirou.py

    :param kwargs: additional keyword arguments

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # -------------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # -------------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # -------------------------------------------------------------------------
    # End Message
    # -------------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success)


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # -------------------------------------------------------------------------
    # Main Code
    # -------------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # -------------------------------------------------------------------------
    # get mode from arguments
    mode = params['INPUTS']['mode']
    if mode not in ['update-remote', 'check-local', 'update-local']:
        msg = ('Mode must be either: "update-remote", "check-local" or '
               '"update-local"')
        WLOG(params, 'error', msg)
        return locals()
    # -------------------------------------------------------------------------
    if mode == 'update-remote':
        # get input directory
        indir = params['INPUTS']['INDIR']
        # deal with no input directory
        if drs_text.null_text(indir, ['None', 'Null', '']):
            emsg = ('Must provide an input directory with --indir '
                    'for mode=update-remote')
            WLOG(params, 'error', emsg)
            return locals()
        # deal with input directory not existing
        if not os.path.exists(indir):
            msg = 'Input directory {0} does not exist'
            margs = [indir]
            WLOG(params, 'error', msg.format(*margs))
            return locals()
        # upload assets
        drs_assets.update_remote_assets(params)
    # deal with checking local assets
    elif mode == 'check-local':
        # check the assets and download / update if necessary
        drs_assets.check_local_assets(params)
    # deal with update local assets
    elif mode == 'update-local':
        # update the local assets
        drs_assets.update_local_assets(params)
    else:
        msg = ('Mode must be either: "update-remote", "check-local" or '
               '"update-local"')
        WLOG(params, 'error', msg)
        return locals()

    # -------------------------------------------------------------------------
    # End of main code
    # -------------------------------------------------------------------------
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

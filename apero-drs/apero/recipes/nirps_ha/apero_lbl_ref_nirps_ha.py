#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run the LBL reference code

- symlinks files

Arguments: None

Created on 2023-08-09 at 11:14

@author: cook
"""
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from aperocore.base import base
from aperocore.constants import param_functions
import apero as apero_pkg
from aperocore import drs_lang
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.science.velocity import gen_lbl
from apero.io import drs_path

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_lbl_ref_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the text types
textentry = drs_lang.textentry


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(obs_dir: Optional[str] = None, files: Optional[List[str]] = None,
         **kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_flat_spirou.py

    :param obs_dir: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    """
    # assign function calls (must add positional)
    fkwargs = dict(obs_dir=obs_dir, files=files, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success)


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # step 1: make all directories (lbl is bad at multiprocessing and
    #         creating directories
    gen_lbl.run_mkdirs(params)

    # -------------------------------------------------------------------------
    # try to import lbl (may not exist)
    try:
        from lbl.recipes import lbl_reset
        # remove any current arguments from sys.argv
        sys.argv = [__NAME__]
    except ImportError:
        # TODO: Add to language database
        emsg = 'Cannot run LBL (not installed) please install LBL'
        WLOG(params, 'error', emsg)
        return locals()
    # -------------------------------------------------------------------------
    # step 2: deal with reset
    if params['OBJ.LBL.RESET']:
        # get program name
        if params['INPUTS']['PROGRAM'] not in ['None', None, '']:
            program = params['INPUTS']['PROGRAM']
        else:
            program = None
        # set up arguments for lbl
        kwargs = dict()
        kwargs['instrument'] = params['INSTRUMENT']
        kwargs['data_dir'] = params['LBL_PATH']
        kwargs['data_source'] = 'APERO'
        skip_done = params['INPUTS'].get('SKIP_DONE', True)
        kwargs['program'] = program
        # print progress
        # TODO: Add to language database
        msg = 'Running LBL reset'
        WLOG(params, 'info', msg)
        # run compute
        lblrtn = lbl_reset.main(**kwargs)
        # log messages from lbl
        gen_lbl.add_log(params, lblrtn)
    # -------------------------------------------------------------------------
    # deal with bad symlinks
    drs_path.remove_broken_symlinks(params, params['PATH.LBL'])
    # -------------------------------------------------------------------------
    # step 3: use apero get to copy files to lbl directory
    #          symlink blaze to calib
    #          symlink wave to calib
    #          symlink tcorr to science
    #          symlink FP
    gen_lbl.run_apero_get(params)
    # --------------------------------------------------------------
    # Quality control
    # --------------------------------------------------------------
    qc_params, passed = gen_lbl.lbl_ref_qc(params)
    # update recipe log
    recipe.log.add_qc(qc_params, passed)
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

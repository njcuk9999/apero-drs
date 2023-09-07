#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run the LBL compile for:
 - science=object template=object
 - science=object template=friend

Arguments:
 - object

Created on 2023-08-09 at 11:14

@author: cook
"""
import sys
from typing import Any, Dict, Optional, Tuple, Union

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.science.velocity import gen_lbl

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_lbl_compile_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
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
# Get the text types
textentry = lang.textentry


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(objname: Optional[str] = None,
         **kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_lbl_compute

    :param obs_dir: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    """
    # assign function calls (must add positional)
    fkwargs = dict(objname=objname, **kwargs)
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
    # get object name
    objname = params['INPUTS']['OBJNAME']
    # set up arguments for lbl
    kwargs = dict()
    kwargs['instrument'] = params['INSTRUMENT']
    kwargs['data_dir'] = params['LBL_PATH']
    kwargs['data_source'] = 'APERO'
    kwargs['skip_done'] = params['INPUTS'].get('SKIP_DONE', False)
    # deal with data type
    if objname in params.listp('LBL_SPECIFIC_DATATYPES', dtype=str):
        data_type = objname
    else:
        data_type = 'SCIENCE'
    # -------------------------------------------------------------------------
    # try to import lbl (may not exist)
    try:
        from lbl.recipes import lbl_compile
        # remove any current arguments from sys.argv
        sys.argv = [__NAME__]
    except ImportError:
        emsg = 'Cannot run LBL (not installed) please install LBL'
        WLOG(params, 'error', emsg)
        return locals()
    # -------------------------------------------------------------------------
    # store errors for reporting later
    errors = []
    # -------------------------------------------------------------------------
    # setup object and template names
    object_science = str(objname)
    object_template = str(objname)
    # run lbl compute for self
    try:
        # print progress
        msg = 'Running LBL compile for {0}_{1}'
        margs = [object_science, object_template]
        WLOG(params, 'info', msg.format(*margs))
        # run compute
        lblself = lbl_compile.main(object_science=object_science,
                                   object_template=object_template,
                                   data_type=data_type, **kwargs)
        # ---------------------------------------------------------------------
        # add output file(s) to database
        for drsfile in recipe.outputs:
            # do not check for a drift file unless we have an FP run
            if data_type != 'FP' and drsfile == 'LBL_DRIFT':
                continue
            # get required criteria
            gen_lbl.add_output(params, recipe,
                               drsfile=recipe.outputs[drsfile],
                               inprefix=object_science,
                               objname=object_science,
                               tempname=object_template)
    except Exception as e:
        emsg = 'LBL Compile Exception [{0}_{1}] {2}: {3}'
        eargs = [object_science, object_template, type(e), str(e)]
        errors.append(emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # stop here if we do not have a science frame
    if data_type != 'SCIENCE':
        # Quality control
        qc_params, passed = gen_lbl.lbl_compile_qc(params)
        # update recipe log
        recipe.log.add_qc(qc_params, passed)
        # report errors
        if len(errors) == 1:
            WLOG(params, 'warning', errors[0])
        return locals()
    # -------------------------------------------------------------------------
    # get friend for this object name
    friend = gen_lbl.find_friend(params, objname)
    # setup object and template names
    object_science = str(objname)
    object_template = str(friend)
    # run lbl compile for friend
    try:
        # print progress
        msg = 'Running LBL compile for {0}_{1}'
        margs = [object_science, object_template]
        WLOG(params, 'info', msg.format(*margs))
        # run compute
        lblfriend = lbl_compile.main(object_science=object_science,
                                     object_template=object_template,
                                     data_type=data_type, **kwargs)
        # ---------------------------------------------------------------------
        # add output file(s) to database
        for drsfile in recipe.outputs:
            # do not check for a drift file unless we have an FP run
            if data_type != 'FP' and drsfile == 'LBLDRIFT':
                continue
            # get required criteria
            gen_lbl.add_output(params, recipe,
                               drsfile=recipe.outputs[drsfile],
                               inprefix=object_science,
                               objname=object_science,
                               tempname=object_template)
    except Exception as e:
        emsg = 'LBL Compile Exception [{0}_{1}] {2}: {3}'
        eargs = [object_science, object_template, type(e), str(e)]
        errors.append(emsg.format(*eargs))
    # --------------------------------------------------------------
    # Quality control
    # --------------------------------------------------------------
    qc_params, passed = gen_lbl.lbl_compile_qc(params)
    # update recipe log
    recipe.log.add_qc(qc_params, passed)
    # ----------------------------------------------------------------------
    # report errors
    if len(errors) == 2:
        WLOG(params, 'error', '\n\n'.join(errors))
    elif len(errors) == 1:
        WLOG(params, 'warning', errors[0])
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
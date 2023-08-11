#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run the LBL reference code

- symlinks files

Arguments: None

Created on 2023-08-09 at 11:14

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.science.velocity import gen_lbl
from apero.core.instruments.spirou import file_definitions as files

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_lbl_mask_spirou.py'
__INSTRUMENT__ = 'SPIROU'
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
    # get object name
    objname = params['INPUTS']['OBJNAME']
    # get the objects for which to calculate a template
    recal_template = params.listp('LBL_RECAL_TEMPLATE', dtype=str)
    # get teff for this object
    teff = gen_lbl.find_teff(params, objname)
    # get friend for this object name
    friend = gen_lbl.find_friend(params, objname)
    # set up arguments for lbl
    kwargs = dict()
    kwargs['instrument'] = params['INSTRUMENT']
    kwargs['data_dir'] = params['LBL_PATH']
    kwargs['data_source'] = 'APERO'
    skip_done = params['INPUTS'].get('SKIP_DONE', True)
    # deal with data type
    if objname in params.listp('LBL_SPECIFIC_DATATYPES', dtype=str):
        kwargs['data_type'] = objname
    else:
        kwargs['data_type'] = 'SCIENCE'
    # -------------------------------------------------------------------------
    # try to import lbl (may not exist)
    try:
        from lbl.recipe import lbl_template
        from lbl.recipes import lbl_mask
    except ImportError:
        # TODO: Add to language database
        emsg = 'Cannot run LBL (not installed) please install LBL'
        WLOG(params, 'error', emsg)
        return locals()
    # -------------------------------------------------------------------------
    if objname in recal_template:
        # run lbl template for self
        try:
            # setup object and template names
            object_science = str(objname)
            object_template = str(objname)
            # print progress
            # TODO: Add to language database
            msg = 'Running LBL template for {0}_{1}'
            margs = [object_science, object_template]
            WLOG(params, 'info', msg.format(*margs))
            # run compute
            lblrtn = lbl_mask.main(object_science=object_science,
                                   object_template=object_template,
                                   overwrite=False, **kwargs)
            # add output file(s) to database
            gen_lbl.add_output(params, recipe,
                               drsfile=files.lbl_template_file,
                               objname=object_science,
                               tempname=object_template)

        except Exception as e:
            # TODO: Add to language database
            emsg = 'LBL Excecption {0}: {1}'
            eargs = [type(e), str(e)]
            WLOG(params, 'error', emsg.format(*eargs))
    else:
        lbltemp = None
    # -------------------------------------------------------------------------
    # run lbl compute for self
    try:
        # setup object and template names
        object_science = str(objname)
        object_template = str(objname)
        # print progress
        msg = 'Running LBL mask for {0}_{1}'
        margs = [object_science, object_template]
        WLOG(params, 'info', msg.format(*margs))
        # run compute
        lblrtn = lbl_mask.main(object_science=object_science,
                               object_template=object_template,
                               object_teff=teff,
                               skip_done=skip_done,
                               **kwargs)
        # get mask type
        lblparams = lblrtn['params'].inst.params
        # get the in suffix (mask type) based on lbl data type from lbl params
        insuffix = lblparams[f'{kwargs["data_type"]}_MASK_TYPE']
        # add output file(s) to database
        gen_lbl.add_output(params, recipe,
                           drsfile=files.lbl_mask_file,
                           insuffix=insuffix,
                           objname=object_science,
                           tempname=object_template)
    except Exception as e:
        # TODO: Add to language database
        emsg = 'LBL Excecption {0}: {1}'
        eargs = [type(e), str(e)]
        WLOG(params, 'error', emsg.format(*eargs))

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
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
from typing import Any, Dict, Optional, Tuple, Union

from apero.base import base
from apero.core.constants import param_functions
from apero.base import drs_lang
from apero.core.base import drs_log
from apero.core.instruments.spirou import file_definitions as files
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.science.velocity import gen_lbl

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_lbl_mask_nirps_ha.py'
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
    # get program name
    if params['INPUTS']['PROGRAM'] not in ['None', None, '']:
        program = params['INPUTS']['PROGRAM']
    else:
        program = None
    # get object name
    objname = params['INPUTS']['OBJNAME']
    # get the objects for which to calculate a template
    recal_template = params['LBL_RECAL_TEMPLATE']
    # set up arguments for lbl
    kwargs = dict()
    kwargs['instrument'] = params['INSTRUMENT']
    kwargs['data_dir'] = params['LBL_PATH']
    kwargs['data_source'] = 'APERO'
    skip_done = gen_lbl.do_skip(params, 'LBL_MASK')
    kwargs['program'] = program
    # deal with data type
    if objname in params['LBL_SPECIFIC_DATATYPES']:
        data_type = objname
        # Just set Teff to room temperature for non-science data
        teff = 300
    else:
        data_type = 'SCIENCE'
        # get teff for this object
        teff = gen_lbl.find_teff(params, objname)
    # -------------------------------------------------------------------------
    # try to import lbl (may not exist)
    try:
        from lbl.recipes import lbl_template
        from lbl.recipes import lbl_mask
        # remove any current arguments from sys.argv
        sys.argv = [__NAME__]
    except ImportError:
        # TODO: Add to language database
        emsg = 'Cannot run LBL (not installed) please install LBL'
        WLOG(params, 'error', emsg)
        return locals()
    # -------------------------------------------------------------------------
    if objname in recal_template:
        # setup object and template names
        object_science = str(objname)
        object_template = str(objname)
        # run lbl template for self
        try:
            # print progress
            # TODO: Add to language database
            msg = 'Running LBL template for {0}_{1}'
            margs = [object_science, object_template]
            WLOG(params, 'info', msg.format(*margs))
            # run compute
            lblrtn = lbl_template.main(object_science=object_science,
                                       object_template=object_template,
                                       overwrite=False, data_type=data_type,
                                       **kwargs)
            # log messages from lbl
            gen_lbl.add_log(params, lblrtn)
            # add output file(s) to database (no tempname used as
            # template=objname)
            gen_lbl.add_output(params, recipe, header_fits_file=None,
                               drsfile=files.lbl_template_file,
                               objname=object_science, tempname='')

        except Exception as e:
            # TODO: Add to language database
            emsg = 'LBL Template Exception [{0}_{1}] {2}: {3}'
            eargs = [object_science, object_template, type(e), str(e)]
            WLOG(params, 'error', emsg.format(*eargs))
    else:
        lbltemp = None
    # -------------------------------------------------------------------------
    # setup object and template names
    object_science = str(objname)
    object_template = str(objname)
    # run lbl compute for self
    try:
        # print progress
        msg = 'Running LBL mask for {0}_{1}'
        margs = [object_science, object_template]
        WLOG(params, 'info', msg.format(*margs))
        # run compute
        lblrtn = lbl_mask.main(object_science=object_science,
                               object_template=object_template,
                               object_teff=teff,
                               skip_done=skip_done, data_type=data_type,
                               **kwargs)
        # log messages from lbl
        gen_lbl.add_log(params, lblrtn)
        # get mask type
        lblparams = lblrtn['inst'].params
        # get the in suffix (mask type) based on lbl data type from lbl params
        mask_type = lblparams[f'{data_type.upper()}_MASK_TYPE']
        insuffix = f'_{mask_type}'
        # add output file(s) to database (no tempname used as
        # template=objname)
        gen_lbl.add_output(params, recipe, header_fits_file=None,
                           drsfile=files.lbl_mask_file,
                           insuffix=insuffix,
                           objname=object_science, tempname='')
    except Exception as e:
        # TODO: Add to language database
        emsg = 'LBL Mask Exception [{0}_{1}] {2}: {3}'
        eargs = [object_science, object_template, type(e), str(e)]
        WLOG(params, 'error', emsg.format(*eargs))
    # --------------------------------------------------------------
    # Quality control
    # --------------------------------------------------------------
    qc_params, passed = gen_lbl.lbl_mask_qc(params)
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
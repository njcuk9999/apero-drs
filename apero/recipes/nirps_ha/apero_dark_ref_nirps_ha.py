#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_dark_ref_nirps_he.py

Dark reference calibration recipe for NIRPS HA

Created on 2019-03-23 at 13:01

@author: cook
"""
from typing import Any, Dict, Tuple, Union

import numpy as np

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
from apero.science.calib import dark

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_dark_ref_nirps_ha.py'
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
def main(**kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_dark_ref

    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
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
    # extract file type from inputs
    filetypes = params['INPUTS'].listp('FILETYPE', dtype=str)
    # get allowed dark types
    allowedtypes = params.listp('ALLOWED_DARK_TYPES', dtype=str)
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()

    # ----------------------------------------------------------------------
    # Get all preprocessed dark files
    # ----------------------------------------------------------------------
    filenames = []

    # check file type
    for filetype in filetypes:
        if filetype not in allowedtypes:
            emsg = textentry('01-001-00020', args=[filetype, mainname])
            for allowedtype in allowedtypes:
                emsg += '\n\t - "{0}"'.format(allowedtype)
            WLOG(params, 'error', emsg)
        # get all "filetype" filenames
        files = drs_utils.find_files(params, block_kind='tmp',
                                     filters=dict(KW_DPRTYPE=filetype))
        # append to filenames
        filenames += list(files)
    # convert to numpy array
    filenames = np.array(filenames)

    # deal with no files found
    if len(filenames) == 0:
        eargs = [params['INPATH']]
        WLOG(params, 'error', textentry('09-011-00005', args=eargs))

    # ----------------------------------------------------------------------
    # Get all dark file properties
    # ----------------------------------------------------------------------
    dark_table = dark.construct_dark_table(params, filenames)

    # ----------------------------------------------------------------------
    # match files by date and median to produce reference dark
    # ----------------------------------------------------------------------
    cargs = [params, dark_table]
    ref_dark, reffile = dark.construct_ref_dark(*cargs)
    # Have to update obs_dir while locked for all param dicts (do not copy)
    #     Note: do not use 'uparamdicts' unless you know what you are doing.
    ukwargs = dict(key='OBS_DIR', value='other', source=mainname)
    constants.uparamdicts(params, recipe.params, WLOG.pin, **ukwargs)

    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    qc_params, passed = dark.reference_qc(params)
    # update recipe log
    recipe.log.add_qc(qc_params, passed)

    # ----------------------------------------------------------------------
    # Save reference dark to file
    # ----------------------------------------------------------------------
    outfile = dark.write_reference_files(params, recipe, reffile, ref_dark,
                                         dark_table, qc_params)

    # ------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ------------------------------------------------------------------
    if passed and params['INPUTS']['DATABASE']:
        calibdbm.add_calib_file(outfile)
    # ---------------------------------------------------------------------
    # if recipe is a reference and QC fail we generate an error
    # ---------------------------------------------------------------------
    if not passed:
        eargs = [recipe.name]
        WLOG(params, 'error', textentry('09-000-00011', args=eargs))
    # ------------------------------------------------------------------
    # Construct summary document
    # ------------------------------------------------------------------
    dark.reference_summary(recipe, params, qc_params, dark_table)

    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    recipe.log.end()

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

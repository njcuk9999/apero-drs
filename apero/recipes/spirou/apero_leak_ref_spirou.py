#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_leak_ref_spirou.py [obs dir]

APERO leak reference calibration recipe for SPIROU

Created on 2020-03-02 at 17:26

@author: cook
"""
from typing import Any, Dict, Optional, Tuple, Union

from apero.base import base
from apero.core.constants import param_functions
from apero.core import lang
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.science.calib import leak
from apero.science.extract import other as extother

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_leak_ref_spirou.py'
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
ParamDict = param_functions.ParamDict

# Get the text types
textentry = lang.textentry
# define extraction code to use
EXTRACT_NAME = 'apero_extract_spirou.py'


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(obs_dir: Optional[str] = None, **kwargs
         ) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_leak_ref_spirou.py

    :param obs_dir: str, the observation directory
    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(obs_dir=obs_dir, **kwargs)
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
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    # ----------------------------------------------------------------------
    # Get all dark_fp files for directory
    # ----------------------------------------------------------------------
    # Note we can only get these from the reference directory as other
    # nights require processing calibrations first
    infiles, rawfiles = leak.get_dark_fps(params, recipe)
    # get the number of infiles
    num_files = len(infiles)
    # ----------------------------------------------------------------------
    # Deal with no files found (use reference)
    if num_files == 0:
        # log that no dark fp were found for this night
        wargs = [params['OBS_DIR']]
        WLOG(params, 'warning', textentry('10-016-00025', args=wargs),
             sublevel=4)
        # update recipe log file
        recipe.log.end()
        # End of main code
        return locals()
    # ----------------------------------------------------------------------
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # set up storage cube
    dark_fp_storage = dict()
    # set up storage of cprops (have to assume cprops constant for loop)
    cprops = None
    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', it)
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.get_header()
        # ------------------------------------------------------------------
        # Get the dark_fp output e2ds filename and extract/read file
        # ------------------------------------------------------------------
        eargs = [params, recipe, EXTRACT_NAME, infile, log1]
        darkfp_extfiles = extother.extract_leak_files(*eargs)
        # get list of basename for dark fp extracted files
        darkfp_extnames = []
        for fiber in darkfp_extfiles:
            darkfp_extnames.append(darkfp_extfiles[fiber].basename)
        # ------------------------------------------------------------------
        # Process the extracted dark fp files for this extract
        # ------------------------------------------------------------------
        # print progress
        wargs = [', '.join(darkfp_extnames)]
        WLOG(params, '', textentry('40-016-00024', args=wargs))
        # correct dark fp
        cout = leak.correct_ref_dark_fp(params, darkfp_extfiles)
        dark_fp_extcorr, cprops = cout
        # ------------------------------------------------------------------
        # add to storage
        for fiber in dark_fp_extcorr:
            if fiber in dark_fp_storage:
                dark_fp_storage[fiber].append(dark_fp_extcorr[fiber])
            else:
                dark_fp_storage[fiber] = [dark_fp_extcorr[fiber]]
        # end this log level
        log1.end()
    # ------------------------------------------------------------------
    # Produce super dark fp from median of all extractions
    # ------------------------------------------------------------------
    dout = leak.ref_dark_fp_cube(params, recipe, dark_fp_storage)
    medcubes, medtables = dout
    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    qc_params, passed = leak.qc_leak_ref(params, medcubes)
    recipe.log.no_qc()
    # ------------------------------------------------------------------
    # Write super dark fp to file
    # ------------------------------------------------------------------
    medcubes = leak.write_leak_ref(params, recipe, rawfiles, medcubes,
                                   medtables, qc_params, cprops)
    # ------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ------------------------------------------------------------------
    if passed and params['INPUTS']['DATABASE']:
        # loop around fibers
        for fiber in medcubes:
            # get outfile
            outfile = medcubes[fiber]
            # copy the order profile to the calibDB
            calibdbm.add_calib_file(outfile)
    # ---------------------------------------------------------------------
    # if recipe is a reference and QC fail we generate an error
    # ---------------------------------------------------------------------
    if not passed:
        eargs = [recipe.name]
        WLOG(params, 'error', textentry('09-000-00011', args=eargs))
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

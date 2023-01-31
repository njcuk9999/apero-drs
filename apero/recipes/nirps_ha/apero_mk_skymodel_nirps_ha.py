#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_mk_template_nirps_ha.py [object name]

APERO recipe to make object templates

Created on 2019-09-05 at 14:58

@author: cook
"""
import numpy as np
import os
from typing import Any, Dict, Optional, Tuple, Union

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
from apero.science.calib import wave
from apero.science import telluric

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_mk_skymodel_nirps_ha.py'
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
def main(objname: Optional[str] = None, **kwargs
         ) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_mk_template

    :param objname: str, the object name to make a template for
    :param kwargs: additional keyword arguments

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
    # get the object name
    objname = params['INPUTS']['OBJNAME']
    # need to convert object to drs object name
    pconst = constants.pload()
    # load object database
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # get clean / alias-safe version of object name
    objname, _ = objdbm.find_objname(pconst, objname)
    # get the filetype (this is overwritten from user inputs if defined)
    filetype = params['INPUTS']['FILETYPE']
    # get the fiber type required
    fiber = params['INPUTS']['FIBER']
    # load the calibration and telluric databases
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    telludbm = drs_database.TelluricDatabase(params)
    telludbm.load_db()

    # TODO: Add these to constants

    # Define the order to get the snr from (for input data qc check)
    params.set('SKYMODEL_EXT_SNR_ORDERNUM', value=35)   # 59 nirps?
    # Define the minimum exptime to use a sky in the model
    params.set('SKYMODEL_MIN_EXPTIME', value=300)

    # ----------------------------------------------------------------------
    # find all sky files
    # ----------------------------------------------------------------------
    # get the science and calib fibers to use
    sci_fiber, calib_fiber = pconst.SKYFIBERS()
    # get the filetype (this is overwritten from user inputs if defined)
    filetype = params['INPUTS']['FILETYPE']
    # find the science fiber files
    if sci_fiber is not None:
        # get the science fiber files for "SKY" files (which are night files)
        #    for the specific filetype
        sky_files_sci = drs_utils.find_files(params, block_kind='red',
                                             filters=dict(KW_TARGET_TYPE='SKY',
                                                          KW_NIGHT_OBS=True,
                                                          KW_OUTPUT=filetype,
                                                          KW_FIBER=sci_fiber))
        # Get filetype definition
        infiletype = drs_file.get_file_definition(params, filetype,
                                                  block_kind='red')
        # get new copy of file definition
        infile_sci = infiletype.newcopy(params=params, fiber=sci_fiber)
        # set reference filename
        infile_sci.set_filename(sky_files_sci[-1])
        # read data
        infile_sci.read_file()
    # otherwise we do not have science files for the sky model
    else:
        # otherwise set to None
        sky_files_sci = None
        infile_sci = None
    # find the calibration fiber files
    if calib_fiber is not None:
        # get the science fiber files for "SKY" files (which are night files)
        #    for the specific filetype
        sky_files_cal = drs_utils.find_files(params, block_kind='red',
                                             filters=dict(KW_TARGET_TYPE='SKY',
                                                          KW_NIGHT_OBS=True,
                                                          KW_OUTPUT=filetype,
                                                          KW_FIBER=calib_fiber))
        # Get filetype definition
        infiletype = drs_file.get_file_definition(params, filetype,
                                                  block_kind='red')
        # get new copy of file definition
        infile_cal = infiletype.newcopy(params=params, fiber=sci_fiber)
        # set reference filename
        infile_cal.set_filename(sky_files_sci[-1])
        # read data
        infile_cal.read_file()
    # otherwise we to not have calib files for the sky model
    else:
        sky_files_cal = None
        infile_cal = None
    # ----------------------------------------------------------------------
    # make sky table
    # ----------------------------------------------------------------------
    # get science table
    sky_table_sci = telluric.skymodel_table(params, sky_files_sci, infile_sci)
    # get calib table
    sky_table_cal = telluric.skymodel_table(params, sky_files_cal, infile_cal)

    # ----------------------------------------------------------------------
    # Construct sky cubes
    # ----------------------------------------------------------------------
    sky_props_sci = telluric.skymodel_cube(params, sky_table_sci)
    sky_props_cal = telluric.skymodel_cube(params, sky_table_cal)

    # ----------------------------------------------------------------------
    # Identify line regions
    # ----------------------------------------------------------------------
    regions = telluric.identify_sky_line_regions(params, sky_props_sci)

    # ----------------------------------------------------------------------
    # Make the sky model
    # ----------------------------------------------------------------------
    sky_props = telluric.calc_skymodel(params, sky_props_sci, sky_props_cal,
                                       regions)

    # ----------------------------------------------------------------------
    # Plot
    # ----------------------------------------------------------------------
    recipe.plot('')

    # ----------------------------------------------------------------------
    # print/log quality control (all assigned previously)
    # ----------------------------------------------------------------------
    qc_params, passed = telluric.mk_skymodel_qc(params, sky_props)
    # update recipe log
    recipe.log.add_qc(qc_params, passed)

    # ----------------------------------------------------------------------
    # Write files to disk
    # ----------------------------------------------------------------------
    skymodel = telluric.write_skymodel(recipe, params, infile_sci, sky_props)

    # ----------------------------------------------------------------------
    # Update the telluric database with the sky model
    # ----------------------------------------------------------------------
    if passed and params['INPUTS']['DATABASE']:
        # copy the big cube median to the calibDB
        telludbm.add_tellu_file(skymodel)

    # ----------------------------------------------------------------------
    # Construct summary document
    # ----------------------------------------------------------------------
    telluric.mk_skymodel_summary(recipe, params, sky_props, qc_params)

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

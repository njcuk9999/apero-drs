#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_mk_template_nirps_ha.py [object name]

APERO recipe to make object templates

Created on 2019-09-05 at 14:58

@author: cook
"""
from typing import Any, Dict, Tuple, Union

from apero.base import base
from apero.core import constants
from apero.core import lang
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.science import telluric
from apero.science.calib import wave

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
def main(**kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_mk_template

    :param objname: str, the object name to make a template for
    :param kwargs: additional keyword arguments

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
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
    # need to convert object to drs object name
    pconst = constants.pload()
    # get the filetype (this is overwritten from user inputs if defined)
    filetype = params['INPUTS']['FILETYPE']
    # load the calibration and telluric databases
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    telludbm = drs_database.TelluricDatabase(params)
    telludbm.load_db()
    # set plot location
    recipe.plot.set_location()
    # ----------------------------------------------------------------------
    # find all sky files
    # ----------------------------------------------------------------------
    # get the science and calib fibers to use
    sci_fiber, cal_fiber = params['SKYFIBERS']
    # find science files
    sky_files_sci, infile_sci = telluric.find_night_skyfiles(params, sci_fiber,
                                                             filetype)
    sky_files_cal, infile_cal = telluric.find_night_skyfiles(params, cal_fiber,
                                                             filetype)
    # only keep files that match between the two
    margs = [sky_files_sci, sky_files_cal, sci_fiber, cal_fiber]
    sky_files_sci, sky_files_cal = telluric.skymodel_matchfiles(*margs)
    # print progress
    # TODO: Add to language database
    msg = 'Found {0} sky files (after matched fiber {1} and {2})'
    margs = [len(sky_files_sci), sci_fiber, cal_fiber]
    WLOG(params, '', msg.format(*margs))

    # ----------------------------------------------------------------------
    # make sky table
    # ----------------------------------------------------------------------
    # get science table and update ref infile to the latest file
    sky_table_sci, infile_sci, nbins = telluric.skymodel_table(params,
                                                               sky_files_sci,
                                                               infile_sci)
    # get calib table and update ref infile to the latest file
    sky_table_cal, infile_cal, nbins = telluric.skymodel_table(params,
                                                               sky_files_cal,
                                                               infile_cal)
    # print progress
    # TODO: Add to language database
    msg = 'Kept {0} sky files (after filtering)'
    margs = [len(sky_table_sci)]
    WLOG(params, '', msg.format(*margs))

    # ----------------------------------------------------------------------
    # load reference wave map
    # ----------------------------------------------------------------------
    # load reference wavelength solution
    mkwargs = dict(infile=infile_sci, ref=True, fiber=sci_fiber,
                   database=calibdbm, rlog=recipe.log)
    refprops = wave.get_wavesolution(params, recipe, **mkwargs)
    # ----------------------------------------------------------------------
    # Construct sky cubes
    # ----------------------------------------------------------------------
    # get sky model cubes
    sky_props_sci = telluric.skymodel_cube(recipe, params, sky_table_sci,
                                           nbins, sci_fiber,
                                           refprops['WAVEMAP'])
    sky_props_cal = telluric.skymodel_cube(recipe, params, sky_table_cal,
                                           nbins, cal_fiber,
                                           refprops['WAVEMAP'])

    # ----------------------------------------------------------------------
    # Identify line regions
    # ----------------------------------------------------------------------
    regions = telluric.identify_sky_line_regions(params, sky_props_sci)

    # ----------------------------------------------------------------------
    # Plot
    # ----------------------------------------------------------------------
    # plot sky model region map
    recipe.plot('TELLU_SKYMODEL_REGION_PLOT', sky_props=sky_props_sci,
                regions=regions)

    # ----------------------------------------------------------------------
    # Make the sky model
    # ----------------------------------------------------------------------
    sky_props = telluric.calc_skymodel(params, sky_props_sci, sky_props_cal,
                                       regions)

    # ----------------------------------------------------------------------
    # Plot
    # ----------------------------------------------------------------------
    # plot sky model median
    recipe.plot('TELLU_SKYMODEL_MED', sky_props=sky_props)
    # clear up memory
    del sky_props['ALL_SCI']
    del sky_props['ALL_CAL']
    # plot line fits
    recipe.plot('TELLU_SKYMODEL_LINEFIT', sky_props=sky_props)

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

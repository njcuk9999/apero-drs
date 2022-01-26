#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
import numpy as np

from apero.base import base
from apero import lang
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.utils import drs_startup
from apero.core.core import drs_database
from apero.core import math as mp
from apero.io import drs_image
from apero.science.calib import wave
from apero.science.extract import other as extractother


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_thermal_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
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
def main(obs_dir=None, files=None, **kwargs):
    """
    Main function for apero_thermal_spirou.py

    :param obs_dir: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type obs_dir: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
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


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get files
    infiles = params['INPUTS']['FILES'][1]
    # get list of filenames (for output)
    rawfiles = []
    for infile in infiles:
        rawfiles.append(infile.basename)
    # ----------------------------------------------------------------------
    # sort thermal files into INT and TEL
    internal_infiles = []
    telescope_infiles = []
    # loop through infiles and add them
    for infile in infiles:
        if infile.get_hkey('KW_DPRTYPE') == 'DARK_DARK_INT':
            internal_infiles.append(infile)
        else:
            telescope_infiles.append(infile)
    # ----------------------------------------------------------------------
    # combine all files of the same type
    # ----------------------------------------------------------------------
    # push into dictionary storage
    drs_dark_files = dict()
    # TODO: QUESTION: only use PM calibrations?
    # deal with combining internal darks
    if len(internal_infiles) > 0:
        cond1 = drs_file.combine(params, recipe, internal_infiles,
                                 math='median')
        drs_dark_files['internal_dark'] = cond1[0]
    # deal with combining telescope darks
    if len(telescope_infiles) > 0:
        cond2 = drs_file.combine(params, recipe, telescope_infiles,
                                 math='median')
        drs_dark_files['telescope_dark'] = cond2[0]
    # we are combining files
    combine = True
    # ----------------------------------------------------------------------
    # get the fiber types from a list parameter
    fiber_types = drs_image.get_fiber_types(params)
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it, drs_type in enumerate(drs_dark_files):
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'drs-type', drs_type)
        # ------------------------------------------------------------------
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        drs_startup.file_processing_update(params, it, len(drs_dark_files))
        # get either the internal or telescope infile
        infile = drs_dark_files[drs_type]
        # ------------------------------------------------------------------
        # Get the thermal output e2ds filename and extract/read file
        # ------------------------------------------------------------------
        eargs = [params, recipe, EXTRACT_NAME, infile]
        thermal_files = extractother.extract_thermal_files(*eargs)

        # TODO: deal with sky darks here

        # ------------------------------------------------------------------
        # Multiple the thermal by excess emissivity
        # ------------------------------------------------------------------
        # TODO: Add in the emissivity stuff


        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        # no quality control --> set passed_qc to True
        log1.no_qc()

        # ------------------------------------------------------------------
        # Write thermal files to file
        # ------------------------------------------------------------------
        # loop around fiber types
        for fiber in fiber_types:
            # get the thermal file
            thermal_file = thermal_files[fiber]
            # log that we are writing thermal files to file
            wargs = [thermal_file.filename]
            WLOG(params, '', textentry('40-016-00022', args=wargs))
            # Update keywords
            # --------------------------------------------------------------
            # add version
            thermal_file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
            # add dates
            thermal_file.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
            # add process id
            thermal_file.add_hkey('KW_PID', value=params['PID'])
            # add output tag
            thermal_file.add_hkey('KW_OUTPUT', value=thermal_file.name)
            thermal_file.add_hkey('KW_FIBER', value=fiber)
            # define multi lists
            data_list, name_list = [], []
            # snapshot of parameters
            if params['PARAMETER_SNAPSHOT']:
                data_list += [params.snapshot_table(recipe,
                                                    drsfitsfile=thermal_file)]
                name_list += ['PARAM_TABLE']
            # write thermal files
            thermal_file.write_multi(data_list=data_list, name_list=name_list,
                                     block_kind=recipe.out_block_str,
                                     runstring=recipe.runstring)
            # add to output files (for indexing)
            recipe.add_output_file(thermal_file)
        # ------------------------------------------------------------------
        # Update the calibration database
        # ------------------------------------------------------------------
        # only if user wants us to add to database
        if params['INPUTS']['DATABASE']:
            # loop around fiber types
            for fiber in fiber_types:
                # add output from thermal files
                calibdbm.add_calib_file(thermal_files[fiber])
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end()

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

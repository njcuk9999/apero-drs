#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
from __future__ import division
import os

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.core.core import drs_startup
from terrapipe.io import drs_fits
from terrapipe.io import drs_image
from terrapipe.science.extract import other as extractother


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_thermal_spirou.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# define extraction code to use
EXTRACT_NAME = 'cal_extract_spirou.py'


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, files=None, **kwargs):
    """
    Main function for cal_thermal_spirou.py

    :param directory: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, files=files, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return core.end_main(params, llmain, recipe, success)


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
    # get nightname
    nightname = params['INPUTS']['DIRECTORY']
    # get files
    infiles = params['INPUTS']['FILES'][1]
    # get list of filenames (for output)
    rawfiles = []
    for infile in infiles:
        rawfiles.append(infile.basename)
    # deal with input data from function
    if 'files' in params['DATA_DICT']:
        infiles = params['DATA_DICT']['files']
        rawfiles = params['DATA_DICT']['rawfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        infiles = [drs_fits.combine(params, infiles, math='median')]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)
    # get the fiber types from a list parameter
    fiber_types = drs_image.get_fiber_types(params)
    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # ------------------------------------------------------------------
        # Get the thermal output e2ds filename and extract/read file
        # ------------------------------------------------------------------
        eargs = [params, recipe, EXTRACT_NAME, infile]
        thermal_files = extractother.extract_thermal_files(*eargs)

        # TODO: deal with sky darks here

        # ------------------------------------------------------------------
        # Write thermal files to file
        # ------------------------------------------------------------------
        # loop around fiber types
        for fiber in fiber_types:
            # log that we are writing thermal files to file
            wargs = [thermal_files[fiber].filename]
            WLOG(params, '', TextEntry('', args=wargs))
            # write thermal files
            # TODO: Remove breakpoint
            constants.breakpoint(params)
            thermal_files[fiber].write()

        # ------------------------------------------------------------------
        # Update the calibration database
        # ------------------------------------------------------------------
        # loop around fiber types
        for fiber in fiber_types:
            # add output from thermal files
            drs_database.add_file(params, thermal_files[fiber])

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

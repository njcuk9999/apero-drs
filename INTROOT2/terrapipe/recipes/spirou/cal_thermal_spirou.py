#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
from __future__ import division

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.instruments.spirou import file_definitions
from terrapipe.io import drs_fits
from terrapipe.recipes.spirou import cal_extract_spirou

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
# Define the output files
EXT_E2DS_AB_FILE = file_definitions.out_ext_e2ds_ab
EXT_E2DS_A_FILE = file_definitions.out_ext_e2ds_a
EXT_E2DS_B_FILE = file_definitions.out_ext_e2ds_b
EXT_E2DS_C_FILE = file_definitions.out_ext_e2ds_c


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
    params = core.end_main(params, success)
    # return a copy of locally defined variables in the memory
    return core.get_locals(dict(locals()), llmain)


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
    # combine input images if required
    if params['INPUT_COMBINE_IMAGES']:
        # get combined file
        infiles = [drs_fits.combine(params, infiles, math='average')]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)

    # get the fiber types from a list parameter
    fiber_types = params.listp('FIBER_TYPE')

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]

        # ------------------------------------------------------------------
        # Get the output filename (to pipe into cal_extract
        # ------------------------------------------------------------------
        for fiber in fiber_types:

            if fiber == 'AB':
                e2dsfile = EXT_E2DS_AB_FILE.newcopy(recipe=recipe)
            elif fiber == 'A':
                e2dsfile = EXT_E2DS_A_FILE.newcopy(recipe=recipe)
            elif fiber == 'B':
                e2dsfile = EXT_E2DS_B_FILE.newcopy(recipe=)
            else:




            exists = False

        # ------------------------------------------------------------------
        # extract the dark (AB, A, B and C) or read dark e2ds header
        # ------------------------------------------------------------------
        if params['THERMAL_ALWAYS_EXTRACT'] or (not exists):
            # pipe into cal_extract
            llout = cal_extract_spirou.main(night_name, files)
            # get qc
            passed = llout['p']['QC']
            # get hdr
            hdr = llout['hdr']
        # else we just need to read the header of the output file
        else:
            pass

        # ------------------------------------------------------------------
        # Update the calibration database
        # ------------------------------------------------------------------





    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    core.end(ll, has_plots=True)

# =============================================================================
# End of code
# =============================================================================

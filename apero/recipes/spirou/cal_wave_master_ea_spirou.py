#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-16 at 09:23

@author: cook
"""
import numpy as np

from apero import core
from apero import lang
from apero.core import constants
from apero.core.core import drs_database
from apero.io import drs_image
from apero.io import drs_fits
from apero.science.calib import flat_blaze
from apero.science.calib import wave, wave2
from apero.science.extract import other as extractother
from apero.science import velocity

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_wave_master_nirps_ha.py'
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
ParamDict = constants.ParamDict
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
# define extraction code to use
EXTRACT_NAME = 'cal_extract_nirps_ha.py'


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, hcfiles=None, fpfiles=None, **kwargs):
    """
    Main function for cal_wave_master_spirou.py

    :param directory: string, the night name sub-directory
    :param hcfiles: list of strings or string, the list of hc files
    :param fpfiles: list of strings or string, the list of fp files
    :param kwargs: any additional keywords

    :type directory: str
    :type hcfiles: list[str]
    :type fpfiles: list[str]

    :keyword debug: int, debug level (0 for None)
    :keyword fpfiles: list of strings or string, the list of fp files (optional)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, hcfiles=hcfiles, fpfiles=fpfiles,
                   **kwargs)
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
    # get files
    hcfiles = params['INPUTS']['HCFILES'][1]
    # deal with (optional fp files)
    if len(params['INPUTS']['FPFILES']) == 0:
        fpfiles = None
    else:
        fpfiles = params['INPUTS']['FPFILES'][1]
    # get list of filenames (for output)
    rawhcfiles, rawfpfiles = [], []
    for infile in hcfiles:
        rawhcfiles.append(infile.basename)
    # deal with (optional fp files)
    if fpfiles is not None:
        for infile in fpfiles:
            rawfpfiles.append(infile.basename)

    # deal with input data from function
    if 'hcfiles' in params['DATA_DICT']:
        hcfiles = params['DATA_DICT']['hcfiles']
        fpfiles = params['DATA_DICT']['fpfiles']
        rawhcfiles = params['DATA_DICT']['rawhcfiles']
        rawfpfiles = params['DATA_DICT']['rawfpfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        hcfiles = [drs_fits.combine(params, recipe, hcfiles, math='median')]
        # get combined file
        if fpfiles is not None:
            fpfiles = [drs_fits.combine(params, recipe, fpfiles, math='median')]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(hcfiles)

    # warn user if lengths differ
    if fpfiles is not None:
        if len(hcfiles) != len(fpfiles):
            wargs = [len(hcfiles), len(fpfiles)]
            WLOG(params, 'error', TextEntry('10-017-00002', args=wargs))
    # get the number of files
    num_files = len(hcfiles)
    # get the fiber types from a list parameter (or from inputs)
    fiber_types = drs_image.get_fiber_types(params)
    # get wave master file (controller fiber)
    master_fiber = params['WAVE_MASTER_FIBER']
    # ----------------------------------------------------------------------
    # For wave master may need update cavity file
    # TODO: Figure out when we should do this - if it is every time we
    # TODO:    do a master may need to move cavity_length files to calibDB
    # params.set('WAVE_FP_UPDATE_CAVITY', value=True, source=mainname)

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', it)
        # ------------------------------------------------------------------
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # get this iterations files
        hcfile = hcfiles[it]
        if fpfiles is None:
            fpfile = None
        else:
            fpfile = fpfiles[it]
        # ------------------------------------------------------------------
        # extract the hc file and fp file
        # ------------------------------------------------------------------
        # set up parameters
        eargs = [params, recipe, EXTRACT_NAME, hcfile, fpfile]
        # run extraction
        hc_outputs, fp_outputs = extractother.extract_wave_files(*eargs)

        # ==================================================================
        # Load initial guess
        # ==================================================================
        # log fiber process
        core.fiber_processing_update(params, master_fiber)
        # get hc and fp outputs
        hc_e2ds_file = hc_outputs[master_fiber]
        fp_e2ds_file = fp_outputs[master_fiber]
        # define the header as being from the hc e2ds file
        hcheader = hc_e2ds_file.header
        # --------------------------------------------------------------
        # load the blaze file for this fiber
        blaze_file, blaze = flat_blaze.get_blaze(params, hcheader, master_fiber)
        # --------------------------------------------------------------
        # load initial wavelength solution (start point) for this fiber
        #    this should only be a master wavelength solution
        iwprops = wave.get_wavesolution(params, recipe, infile=hc_e2ds_file,
                                        fiber=master_fiber, master=True)
        # check that wave parameters are consistent with required number
        #   of parameters (from constants)
        iwprops = wave.check_wave_consistency(params, iwprops)

        # ==================================================================
        # Construct master line reference files
        # ==================================================================
        # generate the hc reference lines
        hcargs = dict(e2dsfile=hc_e2ds_file, wavemap=iwprops['WAVEMAP'])
        hclines = wave2.get_master_lines(params, recipe, **hcargs)
        # generate the fp reference lines
        fpargs = dict(e2dsfile=fp_e2ds_file, wavemap=iwprops['WAVEMAP'],
                      cavity_poly=None)
        fplines = wave2.get_master_lines(params, recipe, **fpargs)

        # ----------------------------------------------------------
        # Write master line references to file
        #   master fiber hclines and fplines for all fibers!
        # ----------------------------------------------------------
        wmargs = [hc_e2ds_file, fp_e2ds_file, hclines, fplines,
                  master_fiber, combine, rawhcfiles, rawfpfiles]
        out = wave2.write_master_lines(params, recipe, *wmargs)
        hclinefile, fplinefile = out

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

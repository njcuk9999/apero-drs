#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-16 at 09:23

@author: cook
"""
from __future__ import division

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.io import drs_image
from terrapipe.io import drs_fits
from terrapipe.science.calib import flat_blaze
from terrapipe.science.calib import wave
from terrapipe.science.extract import other as extractother


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_wave_spirou.py'
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
def main(directory=None, hcfiles=None, **kwargs):
    """
    Main function for cal_badpix_spirou.py

    :param directory: string, the night name sub-directory
    :param hcfiles: list of strings or string, the list of hc files
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)
    :keyword fpfiles: list of strings or string, the list of fp files (optional)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, hcfiles=None, **kwargs)
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
    # get calibration database
    cdb = drs_database.get_full_database(params, 'calibration')
    params[cdb.dbshort] = cdb
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
        hcfiles = [drs_fits.combine(params, hcfiles, math='median')]
        # get combined file
        if fpfiles is not None:
            fpfiles = [drs_fits.combine(params, fpfiles, math='median')]
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

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
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

        # ------------------------------------------------------------------
        # Loop around fibers
        # ------------------------------------------------------------------
        for fiber in fiber_types:
            # get hc and fp outputs
            hc_e2ds_file = hc_outputs[fiber]
            fp_e2ds_file = fp_outputs[fiber]
            # define the header as being from the hc e2ds file
            hcheader = hc_e2ds_file.header
            # --------------------------------------------------------------
            # load the blaze file for this fiber
            blaze_file, blaze = flat_blaze.get_blaze(params, hcheader, fiber)
            # --------------------------------------------------------------
            # load intial wavelength solution (start point) for this fiber
            iwprops = wave.get_wavesolution(params, recipe, hcheader,
                                            fiber=fiber)
            # check that wave parameters are consistent with required number
            #   of parameters (from constants)
            iwprops = wave.check_wave_consistency(params, iwprops)
            # --------------------------------------------------------------
            # HC wavelength solution
            # --------------------------------------------------------------
            hcprops, wprops = wave.hc_wavesol(params, recipe, iwprops,
                                              hc_e2ds_file, fiber)
            # --------------------------------------------------------------
            # HC quality control
            # --------------------------------------------------------------
            qc_params = wave.hc_quality_control(params, hcprops, hc_e2ds_file)
            # --------------------------------------------------------------
            # log the global stats
            # --------------------------------------------------------------
            wave.hc_log_global_stats(params, hcprops, hc_e2ds_file, fiber)
            # --------------------------------------------------------------
            # write HC wavelength solution to file
            # --------------------------------------------------------------
            hcargs = [hcprops, hc_e2ds_file, fiber, combine, rawhcfiles,
                      qc_params, iwprops]
            hcwavefile = wave.hc_write_wavesolution(params, recipe, *hcargs)
            # --------------------------------------------------------------
            # write resolution and line profiles to file
            # --------------------------------------------------------------
            hcargs = [hcprops, hc_e2ds_file, hcwavefile, fiber]
            wave.hc_write_resmap(params, recipe, *hcargs)

            # --------------------------------------------------------------
            # Update calibDB with HC solution
            # --------------------------------------------------------------
            if params['QC']:
                # copy the hc wave solution file to the calibDB
                drs_database.add_file(params, hcwavefile)

            # --------------------------------------------------------------
            # Update header of current file with HC solution
            # --------------------------------------------------------------
            if params['QC']:
                # create copy of infile
                hc_update = hc_e2ds_file.completecopy(hc_e2ds_file)
                # update wave solution
                hc_update = wave.add_wave_keys(hc_update, wprops)
                # write hc update
                hc_update.write()

            # --------------------------------------------------------------
            # FP addition to wavelength solution
            # --------------------------------------------------------------
            # check if there's a FP input and if HC solution passed QCs
            if (fp_e2ds_file is not None) and params['QC']:
                # ----------------------------------------------------------
                # FP wavelength solution
                # ----------------------------------------------------------
                fpprops, wprops = wave.fp_wavesol(params, fp_e2ds_file, hcprops,
                                                  wprops, fiber)

                # ----------------------------------------------------------
                # FP quality control
                # ----------------------------------------------------------

                # ----------------------------------------------------------
                # write FP wavelength solution to file
                # ----------------------------------------------------------

                # ----------------------------------------------------------
                # Update calibDB with FP solution
                # ----------------------------------------------------------

            # If the HC solution failed QCs we do not compute FP-HC solution
            elif (fp_e2ds_file is not None) and (not params['QC']):
                WLOG(params, 'warning', TextEntry('10-017-00006'))
            # If there is no FP file we log that
            else:
                WLOG(params, 'warning', TextEntry('10-017-00007'))



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

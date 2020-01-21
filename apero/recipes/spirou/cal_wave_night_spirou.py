#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-18 at 16:57

@author: cook
"""
# TODO: change to cal_wave_spirou after testing complete
# TODO: Currently a placeholder for EA code
from __future__ import division
import numpy as np

from apero import core
from apero import locale
from apero.core import constants
from apero.core.core import drs_database
from apero.io import drs_image
from apero.io import drs_fits
from apero.science.calib import flat_blaze
from apero.science.calib import wave1 as wave
from apero.science import velocity
from apero.science.extract import other as extractother


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_wave_night_spirou.py'
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
def main(directory=None, hcfiles=None, fpfiles=None, **kwargs):
    """
    Main function for cal_wave_night_spirou.py

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
    fkwargs = dict(directory=directory, hcfiles=hcfiles,
                   fpfiles=fpfiles, **kwargs)
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

    # deal with input hc/fp data from function
    if 'hcfiles' in params['DATA_DICT'] and 'fpfiles' in params['DATA_DICT']:
        hcfiles = params['DATA_DICT']['hcfiles']
        fpfiles = params['DATA_DICT']['fpfiles']
        rawhcfiles = params['DATA_DICT']['rawhcfiles']
        rawfpfiles = params['DATA_DICT']['rawfpfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        hcfiles = [drs_fits.combine(params, hcfiles, math='median')]
        fpfiles = [drs_fits.combine(params, fpfiles, math='median')]
        combine = True
    else:
        combine = False

    # get the number of infiles
    num_files = len(hcfiles)

    # warn user if lengths differ
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
            # ------------------------------------------------------------------
            # add level to recipe log
            log_hc = log1.add_level(params, 'mode=hc fiber', fiber)
            # ------------------------------------------------------------------
            # log fiber process
            core.fiber_processing_update(params, fiber)
            # get hc and fp outputs
            hc_e2ds_file = hc_outputs[fiber]
            fp_e2ds_file = fp_outputs[fiber]
            # --------------------------------------------------------------
            # get master hc lines and fp lines from calibDB
            wargs = []
            wout = wave.get_wavelines(params, recipe, infile=hc_e2ds_file)
            mhclines, mhclsource, mfplines, mfplsource = wout

            # --------------------------------------------------------------
            # load wavelength solution (start point) for this fiber
            #    this should only be a master wavelength solution
            wprops = wave.get_wavesolution(params, recipe, infile=hc_e2ds_file,
                                           fiber=fiber, master=True)

            # --------------------------------------------------------------
            # define the header as being from the hc e2ds file
            hcheader = hc_e2ds_file.header
            # load the blaze file for this fiber
            blaze_file, blaze = flat_blaze.get_blaze(params, hcheader, fiber)
            # --------------------------------------------------------------
            # calculate the night wavelength solution
            wargs = [hc_e2ds_file, fp_e2ds_file, mhclines, mfplines, wprops]
            nprops = wave.night_wavesolution(params, recipe, *wargs)

            # ----------------------------------------------------------
            # ccf computation
            # ----------------------------------------------------------
            # get the FP (reference) fiber
            pconst = constants.pload(params['INSTRUMENT'])
            sfiber, rfiber = pconst.FIBER_CCF()
            # compute the ccf
            ccfargs = [fp_e2ds_file, fp_e2ds_file.data, blaze,
                       nprops['WAVEMAP'], rfiber]
            rvprops = velocity.compute_ccf_fp(params, recipe, *ccfargs)
            # merge rvprops into llprops (shallow copy)
            nprops.merge(rvprops)

            # ----------------------------------------------------------
            # wave solution quality control
            # ----------------------------------------------------------
            qc_params, passed = wave.night_quality_control(params, nprops)

            # ----------------------------------------------------------
            # write wave solution to file
            # ----------------------------------------------------------
            wargs = [nprops, hcfile, fpfile, fiber, combine, rawhcfiles,
                     rawfpfiles, qc_params, wprops['WAVEINST']]
            wavefile = wave.night_write_wavesolution(params, recipe, *wargs)

            # ----------------------------------------------------------
            # Update calibDB with solution
            # ----------------------------------------------------------
            if passed:
                # copy the hc wave solution file to the calibDB
                drs_database.add_file(params, wavefile)

            # ----------------------------------------------------------
            # Update header of current files with FP solution
            # ----------------------------------------------------------
            if passed and params['INPUTS']['DATABASE']:
                # log that we are updating the HC file with wave params
                wargs = [hc_e2ds_file.name, hc_e2ds_file.filename]
                WLOG(params, '', TextEntry('40-017-00038', args=wargs))
                # create copy of input e2ds hc file
                hc_update = hc_e2ds_file.completecopy(hc_e2ds_file)
                # update wave solution
                hc_update = wave.add_wave_keys(params, hc_update, wprops)
                # write hc update
                hc_update.write_file()
                # log that we are updating the HC file with wave params
                wargs = [fp_e2ds_file.name, fp_e2ds_file.filename]
                WLOG(params, '', TextEntry('40-017-00038', args=wargs))
                # create copy of input e2ds fp file
                fp_update = fp_e2ds_file.completecopy(fp_e2ds_file)
                # update wave solution
                fp_update = wave.add_wave_keys(params, fp_update, wprops)
                # write hc update
                fp_update.write_file()
                # add to output files (for indexing)
                recipe.add_output_file(fp_update)

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


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_wave_night_nirps_he.py [obs dir] [HC_HC files] [FP_FP files]

APERO wavelength solution nightly calibration recipe for NIRPS HE

Created on 2019-08-16 at 09:23

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from astropy import constants as cc
from astropy import units as uu

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.io import drs_image
from apero.science import velocity
from apero.science.calib import flat_blaze
from apero.science.calib import gen_calib
from apero.science.calib import wave
from apero.science.extract import other as extractother

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_wave_night_nirps_he.py'
__INSTRUMENT__ = 'NIRPS_HE'
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
textentry = drs_lang.textentry
# define extraction code to use
EXTRACT_NAME = 'apero_extract_nirps_he.py'
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(obs_dir: Optional[str] = None, hcfiles: Optional[List[str]] = None,
         fpfiles: Optional[List[str]] = None,
         **kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_wave_night

    :param obs_dir: string, the night name sub-directory
    :param hcfiles: list of strings or string, the list of hc files
    :param fpfiles: list of strings or string, the list of fp files
    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)
    :keyword fpfiles: list of strings or string, the list of fp files (optional)

    :returns: dictionary of the local space
    """
    # assign function calls (must add positional)
    fkwargs = dict(obs_dir=obs_dir, hcfiles=hcfiles, fpfiles=fpfiles,
                   **kwargs)
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
    # get files
    hcfiles = params['INPUTS']['HCFILES'][1]
    # check qc
    hcfiles = drs_file.check_input_qc(params, hcfiles, 'hc files')
    # deal with (optional fp files)
    if len(params['INPUTS']['FPFILES']) == 0:
        fpfiles = None
    else:
        fpfiles = params['INPUTS']['FPFILES'][1]
        # check qc
        fpfiles = drs_file.check_input_qc(params, fpfiles, 'fp files')
        # must check fp files pass quality control
        fpfiles = gen_calib.check_fp_files(params, fpfiles)
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
        cond1 = drs_file.combine(params, recipe, hcfiles, math='mean')
        hcfiles = [cond1[0]]
        # get combined file
        if fpfiles is not None:
            cond2 = drs_file.combine(params, recipe, fpfiles, math='mean')
            fpfiles = [cond2[0]]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(hcfiles)

    # warn user if lengths differ
    if fpfiles is not None:
        if len(hcfiles) != len(fpfiles):
            wargs = [len(hcfiles), len(fpfiles)]
            WLOG(params, 'error', textentry('10-017-00002', args=wargs))
    # get the number of files
    num_files = len(hcfiles)
    # get the fiber types from a list parameter (or from inputs)
    fiber_types = drs_image.get_fiber_types(params)
    # get wave reference file (controller fiber)
    ref_fiber = params['WAVE_REF_FIBER']
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()

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
        drs_startup.file_processing_update(params, it, num_files)
        # get this iterations files
        hcfile = hcfiles[it]
        if fpfiles is None:
            fpfile = None
        else:
            fpfile = fpfiles[it]
        # -----------------------------------------------------------------
        # load initial wavelength solution (start point) for this fiber
        #    this should only be a reference wavelength solution
        iwprops = wave.get_wavesolution(params, recipe, infile=hcfile,
                                        fiber=ref_fiber, ref=True,
                                        database=calibdbm)
        # check that wave parameters are consistent with required number
        #   of parameters (from constants)
        iwprops = wave.check_wave_consistency(params, iwprops)
        # -----------------------------------------------------------------
        # extract the hc file and fp file
        # -----------------------------------------------------------------
        # set up parameters
        eargs = [params, recipe, EXTRACT_NAME, hcfile, fpfile]
        ekwargs = dict(wavefile=iwprops['WAVEFILE'], logger=log1)
        # run extraction
        hc_outputs, fp_outputs = extractother.extract_wave_files(*eargs,
                                                                 **ekwargs)

        # =================================================================
        # get blaze and initial wave solution
        # =================================================================
        # log fiber process
        drs_startup.fiber_processing_update(params, ref_fiber)
        # get hc and fp outputs
        hc_e2ds_file = hc_outputs[ref_fiber]
        fp_e2ds_file = fp_outputs[ref_fiber]
        # read these files
        hc_e2ds_file.read_file()
        fp_e2ds_file.read_file()
        # define the header as being from the hc e2ds file
        hcheader = hc_e2ds_file.get_header()
        # -----------------------------------------------------------------
        # load the blaze file for this fiber
        bout = flat_blaze.get_blaze(params, hcheader, ref_fiber)
        blaze_file, blaze_time, blaze = bout

        # =================================================================
        # Construct HC + FP line reference files for ref_fiber
        # =================================================================
        # set the wprops to initial wave solution
        wprops = iwprops.copy()
        # get cavity solution from database
        params, wprops['CAVITY'] = wave.get_cavity_file(params,
                                                        infile=fp_e2ds_file,
                                                        database=calibdbm)
        # -----------------------------------------------------------------
        # generate the hc reference lines
        hcargs = dict(e2dsfile=hc_e2ds_file, wavemap=wprops['WAVEMAP'],
                      iteration=1)
        hclines = wave.calc_wave_lines(params, recipe, **hcargs)
        # -----------------------------------------------------------------
        # generate the fp reference lines
        fpargs = dict(e2dsfile=fp_e2ds_file, wavemap=wprops['WAVEMAP'],
                      cavity_poly=wprops['CAVITY'], iteration=1)
        fplines = wave.calc_wave_lines(params, recipe, **fpargs)

        # -----------------------------------------------------------------
        # Calculate the wave solution for reference fiber
        # reference fiber + reference wave setup
        # Random night (not reference), AB -> We only allow for changes in the
        # achromatic term, fit_cavity = True, fit_achromatic = True
        fit_cavity = True
        fit_achromatic = True
        # calculate wave solution
        wprops = wave.calc_wave_sol(params, recipe, hclines, fplines,
                                    nbo=hc_e2ds_file.shape[0],
                                    nbxpix=hc_e2ds_file.shape[1],
                                    fit_cavity=fit_cavity,
                                    fit_achromatic=fit_achromatic,
                                    cavity_update=wprops['CAVITY'],
                                    iteration=1)

        # =================================================================
        # Recalculate HC + FP line reference files for ref_fiber
        # =================================================================
        # generate the hc reference lines
        hcargs = dict(e2dsfile=hc_e2ds_file, wavemap=wprops['WAVEMAP'],
                      iteration=2)
        hclines = wave.calc_wave_lines(params, recipe, **hcargs)
        # generate the fp reference lines
        fpargs = dict(e2dsfile=fp_e2ds_file, wavemap=wprops['WAVEMAP'],
                      cavity_poly=wprops['CAVITY'], iteration=2)
        fplines = wave.calc_wave_lines(params, recipe, **fpargs)
        # add lines to wave properties
        wprops['HCLINES'] = hclines
        wprops['FPLINES'] = fplines
        # add wave time and file
        wprops['WAVETIME'] = fp_e2ds_file.get_hkey('MJDMID', dtype=float)
        wprops['WAVEFILE'] = 'None'
        wprops['WAVESOURCE'] = __NAME__
        # set sources
        skeys = ['HCLINES', 'FPLINES', 'WAVETIME', 'WAVEFILE']
        wprops.set_sources(skeys, mainname)

        # =================================================================
        # Calculate wave solution for other fibers
        # =================================================================
        # other fiber + reference wave setup
        # Random night, not AB -> We fit nothing and use the AB coefficient
        #    from that night (should be same as reference except for the
        #    achromatic term):
        #    fit_achromatic = False, fig_cavity = False
        fit_cavity = False
        fit_achromatic = False
        # get solution for other fibers and save all in a list of param dicts
        #   one for each fiber
        wprops_all = wave.process_fibers(params, recipe, wprops, fp_outputs,
                                         hc_outputs, fit_cavity,
                                         fit_achromatic)

        # ==================================================================
        # FP CCF COMPUTATION - need all fibers done one-by-one
        # ==================================================================
        # store rvs from ccfs
        rvs_all = dict()
        # loop around fibers
        for fiber in fiber_types:
            # choose which wprops to use
            wprops = wprops_all[fiber].copy()
            # get fp e2ds file
            fp_e2ds_file = fp_outputs[fiber]
            # compute the ccf
            ccfargs = [fp_e2ds_file, fp_e2ds_file.get_data(), blaze,
                       wprops['WAVEMAP'], fiber]
            rvprops = velocity.compute_ccf_fp(params, recipe, *ccfargs)
            # update ccf properties and push into wprops for wave sol outputs
            wprops, rvprops = wave.update_w_rv_props(wprops, rvprops, mainname)
            # -----------------------------------------------------------------
            # update correct wprops
            wprops_all[fiber] = wprops
            # add to rv storage
            rvs_all[fiber] = rvprops

        # ==================================================================
        # DV from wave measured in the FP line files
        # ==================================================================
        rvs_all = wave.wave_meas_diff(params, ref_fiber, wprops_all, rvs_all)

        # =================================================================
        # Quality control
        # =================================================================
        qc_params = wave.wave_quality_control(params, wprops_all,
                                              rvs_all)
        # passed if all qc passed
        passed = np.all(qc_params[-1])
        # update recipe log
        log1.add_qc(qc_params, passed)

        # =================================================================
        # Write all files to disk
        # =================================================================
        # store global passed
        global_passed = bool(passed)
        # loop around all fibers
        for fiber in fiber_types:
            # get the wprops for this fiber
            wprops = wprops_all[fiber]
            # get e2ds files for this fiber
            hc_e2ds_file = hc_outputs[fiber]
            fp_e2ds_file = fp_outputs[fiber]
            # get the hclines and fp flines for this fiber
            hclines = wprops['HCLINES']
            fplines = wprops['FPLINES']
            # get the echelle order numbers
            wprops = wave.get_echelle_orders(params, wprops)
            # -----------------------------------------------------------------
            # Write wave solution
            # -----------------------------------------------------------------
            fpargs = [recipe, fiber, wprops, hc_e2ds_file, fp_e2ds_file,
                      combine, rawhcfiles, rawfpfiles, qc_params]
            wavefile = wave.write_wavesol(params, *fpargs)

            # -----------------------------------------------------------------
            # Write reference line references to file
            #   reference fiber hclines and fplines for all fibers!
            # -----------------------------------------------------------------
            wmargs = [hc_e2ds_file, fp_e2ds_file, wavefile, hclines,
                      fplines, fiber]
            out = wave.write_wave_lines(params, recipe, *wmargs, ref=False)
            hclinefile, fplinefile = out

            # ----------------------------------------------------------
            # Update header of current file with FP solution
            # ----------------------------------------------------------
            if passed and params['INPUTS']['DATABASE']:
                # update the e2ds and s1d files for hc
                newhce2ds = wave.update_extract_files(params, recipe,
                                                      hc_e2ds_file, wprops,
                                                      EXTRACT_NAME, fiber,
                                                      calibdbm=calibdbm)
                # update the e2ds and s1d files for fp
                #  we returrn the fp e2ds file as it has an updated header
                newfpe2ds = wave.update_extract_files(params, recipe,
                                                      fp_e2ds_file, wprops,
                                                      EXTRACT_NAME, fiber,
                                                      calibdbm=calibdbm)
            # else just get the e2ds file from the current fp file
            else:
                newfpe2ds = fp_e2ds_file

            # ------------------------------------------------------------------
            # archive ccf from fiber
            # ------------------------------------------------------------------
            # need to use the updated header in newfpe2ds
            velocity.write_ccf(params, recipe, newfpe2ds, rvs_all[fiber],
                               rawfpfiles, combine, qc_params, fiber,
                               fit_type=1)

            # ----------------------------------------------------------
            # Update calibDB with FP solution and line references
            # ----------------------------------------------------------
            if passed and params['INPUTS']['DATABASE']:
                # copy the hc wave solution file to the calibDB
                calibdbm.add_calib_file(wavefile)

            # update global passed
            global_passed &= passed

        # ---------------------------------------------------------------------
        # if recipe is a reference and QC fail we generate an error
        # ---------------------------------------------------------------------
        if not global_passed and params['INPUTS']['REF']:
            eargs = [recipe.name]
            WLOG(params, 'error', textentry('09-000-00011', args=eargs))

        # -----------------------------------------------------------------
        # Construct summary document
        # -----------------------------------------------------------------
        # if we have a wave solution wave summary from fpprops
        wave.wave_summary(recipe, params, wprops, ref_fiber, qc_params)

        # construct summary (outside fiber loop)
        recipe.plot.summary_document(it)

        # -----------------------------------------------------------------
        # update recipe log file
        # -----------------------------------------------------------------
        log1.end()

    # ---------------------------------------------------------------------
    # End of main code
    # ---------------------------------------------------------------------
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

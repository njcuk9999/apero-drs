#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-16 at 09:23

@author: cook
"""
from astropy import constants as cc
from astropy import units as uu
import numpy as np

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.core import drs_database
from apero.io import drs_image
from apero.science.calib import gen_calib
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science.extract import other as extractother
from apero.science import velocity

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_wave_master_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
ParamDict = constants.ParamDict
# Get the text types
textentry = lang.textentry
# define extraction code to use
EXTRACT_NAME = 'apero_extract_nirps_ha.py'
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
def main(obs_dir=None, hcfiles=None, fpfiles=None, **kwargs):
    """
    Main function for apero_wave_master

    :param obs_dir: string, the night name sub-directory
    :param hcfiles: list of strings or string, the list of hc files
    :param fpfiles: list of strings or string, the list of fp files
    :param kwargs: any additional keywords

    :type obs_dir: str
    :type hcfiles: list[str]
    :type fpfiles: list[str]

    :keyword debug: int, debug level (0 for None)
    :keyword fpfiles: list of strings or string, the list of fp files (optional)

    :returns: dictionary of the local space
    :rtype: dict
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
        cond1 = drs_file.combine(params, recipe, hcfiles, math='median')
        hcfiles = [cond1[0]]
        # get combined file
        if fpfiles is not None:
            cond2 = drs_file.combine(params, recipe, fpfiles, math='median')
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
    # get wave master file (controller fiber)
    master_fiber = params['WAVE_MASTER_FIBER']
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
        # extract the hc file and fp file
        # -----------------------------------------------------------------
        # set up parameters
        eargs = [params, recipe, EXTRACT_NAME, hcfile, fpfile]
        # run extraction
        hc_outputs, fp_outputs = extractother.extract_wave_files(*eargs)

        # =====================================================================
        # get blaze and initial wave solution
        # =====================================================================
        # log fiber process
        drs_startup.fiber_processing_update(params, master_fiber)
        # get hc and fp outputs
        hc_e2ds_file = hc_outputs[master_fiber]
        fp_e2ds_file = fp_outputs[master_fiber]
        # read these files
        hc_e2ds_file.read_file()
        fp_e2ds_file.read_file()
        # define the header as being from the hc e2ds file
        hcheader = hc_e2ds_file.get_header()
        # ---------------------------------------------------------------------
        # load the blaze file for this fiber
        blaze_file, blaze = flat_blaze.get_blaze(params, hcheader,
                                                 master_fiber)
        # ---------------------------------------------------------------------
        # load initial wavelength solution (start point) for this fiber
        #    this should only be a master wavelength solution
        iwprops = wave.get_wavesolution(params, recipe, infile=hc_e2ds_file,
                                        fiber=master_fiber, master=True,
                                        database=calibdbm)
        # check that wave parameters are consistent with required number
        #   of parameters (from constants)
        iwprops = wave.check_wave_consistency(params, iwprops)

        # =====================================================================
        # Construct HC + FP line reference files for master_fiber
        # =====================================================================
        # set the wprops to initial wave solution
        wprops = iwprops.copy()
        # set cavity solution to None initially
        wprops['CAVITY'] = None
        wprops.set_source('CAVITY', mainname)
        # iterate twice so we have a good cavity length to start
        for iteration in range(2):
            # -----------------------------------------------------------------
            # generate the hc reference lines
            hcargs = dict(e2dsfile=hc_e2ds_file, wavemap=wprops['WAVEMAP'],
                          iteration=iteration + 1)
            hclines = wave.calc_wave_lines(params, recipe, **hcargs)
            # -----------------------------------------------------------------
            # default wave map might be off by too many pixels therefore we
            #   calculate a global offset and re-calculate
            if iteration == 0:
                # calculate hc offset
                oargs = [wprops['WAVEMAP'], hclines]
                wprops['WAVEMAP'] = wave.hc_wave_sol_offset(params, *oargs)
                # recalculate hclines with offset applied
                hcargs = dict(e2dsfile=hc_e2ds_file, wavemap=wprops['WAVEMAP'],
                              iteration='{0} + offset'.format(iteration + 1))
                hclines = wave.calc_wave_lines(params, recipe, **hcargs)
            # -----------------------------------------------------------------
            # generate the fp reference lines
            fpargs = dict(e2dsfile=fp_e2ds_file, wavemap=wprops['WAVEMAP'],
                          cavity_poly=wprops['CAVITY'], iteration=iteration + 1)
            fplines = wave.calc_wave_lines(params, recipe, **fpargs)
            # -----------------------------------------------------------------
            # Calculate the wave solution for master fiber
            # master fiber + master wave setup
            fit_cavity = True
            fit_achromatic = False
            # calculate wave solution
            wprops = wave.calc_wave_sol(params, recipe, hclines, fplines,
                                        nbo=hc_e2ds_file.shape[0],
                                        nbxpix=hc_e2ds_file.shape[1],
                                        fit_cavity=fit_cavity,
                                        fit_achromatic=fit_achromatic,
                                        cavity_update=wprops['CAVITY'])

        # =================================================================
        # Recalculate HC + FP line reference files for master_fiber
        # =================================================================
        # generate the hc reference lines
        hcargs = dict(e2dsfile=hc_e2ds_file, wavemap=wprops['WAVEMAP'],
                      iteration=3)
        hclines = wave.calc_wave_lines(params, recipe, **hcargs)
        # generate the fp reference lines
        fpargs = dict(e2dsfile=fp_e2ds_file, wavemap=wprops['WAVEMAP'],
                      cavity_poly=wprops['CAVITY'], iteration=3)
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
        # Calculate resolution map
        # =================================================================
        # log progress: Generating resolution map'
        WLOG(params, 'info', textentry('40-017-00010'))
        # generate resolution map and update wprops
        wprops = wave.generate_resolution_map(params, recipe, wprops,
                                              hc_e2ds_file)
        # =================================================================
        # Calculate wave solution for other fibers
        # =================================================================
        # other fiber + master wave setup
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
        # must update the smart mask now cavity polynomial has been update
        #   (if it has been update else this just recomputes the mask)
        wave.update_smart_fp_mask(params, wprops['CAVITY'])
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
        rvs_all = wave.wave_meas_diff(params, master_fiber, wprops_all, rvs_all)

        # =================================================================
        # Quality control
        # =================================================================
        qc_params = wave.wave_quality_control(params, wprops_all,
                                              rvs_all)
        # passed if all qc passed
        passed = np.all(qc_params[-1])
        # update recipe log
        log1.add_qc(qc_params, passed)
        # proxy cavity file
        cavityfile = None

        # =================================================================
        # Write all files to disk
        # =================================================================
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
            wavefile = wave.write_wavesol(params, *fpargs, master=True)
            # -----------------------------------------------------------------
            # Write cavity file (for master fiber)
            # -----------------------------------------------------------------
            if fiber == master_fiber:
                # cavity args
                cargs = [fp_e2ds_file, wavefile, wprops['CAVITY']]
                # write cavity file
                cavityfile = wave.write_cavity_file(params, recipe, *cargs)
                # resolution args
                rargs = [fp_e2ds_file, fiber, wavefile, wprops]
                # write to file
                wave.write_resolution_map(params, recipe, *rargs)

            # -----------------------------------------------------------------
            # Write master line references to file
            #   master fiber hclines and fplines for all fibers!
            # -----------------------------------------------------------------
            wmargs = [hc_e2ds_file, fp_e2ds_file, wavefile, hclines,
                      fplines, fiber]
            out = wave.write_wave_lines(params, recipe, *wmargs, master=True)
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
                               rawfpfiles, combine, qc_params, fiber)

            # ----------------------------------------------------------
            # Update calibDB with FP solution and line references
            # ----------------------------------------------------------
            if passed and params['INPUTS']['DATABASE']:
                # only save cavity file for master fiber
                if fiber == master_fiber:
                    # copy the cavity solution to calibration database
                    calibdbm.add_calib_file(cavityfile)
                # copy the hc wave solution file to the calibDB
                calibdbm.add_calib_file(wavefile)
                # copy the hc line ref file to the calibDB
                calibdbm.add_calib_file(hclinefile)
                # copy the fp line ref file to the calibDB
                calibdbm.add_calib_file(fplinefile)

        # -----------------------------------------------------------------
        # Construct summary document
        # -----------------------------------------------------------------
        # if we have a wave solution wave summary from fpprops
        wave.wave_summary(recipe, params, wprops, master_fiber, qc_params)

        # construct summary (outside fiber loop)
        recipe.plot.summary_document(it)

        # -----------------------------------------------------------------
        # update recipe log file
        # -----------------------------------------------------------------
        log1.end()

    # ---------------------------------------------------------------------
    # End of main code
    # ---------------------------------------------------------------------
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

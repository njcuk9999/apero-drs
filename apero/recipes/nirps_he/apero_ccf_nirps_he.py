#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO Cross-correlation radial velocity recipe

Created on 2019-09-19 at 13:16

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.science import extract
from apero.science import velocity
from apero.science.calib import flat_blaze
from apero.science.calib import wave

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ccf_nirps_he.py'
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
ParamDict = constants.ParamDict
# get text entry
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
def main(obs_dir: Optional[str] = None, files: Optional[List[str]] = None,
         **kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_ccf

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
    infiles = params['INPUTS']['FILES'][1]
    # check qc
    infiles = drs_file.check_input_qc(params, infiles, 'files')
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
        cout = drs_file.combine(params, recipe, infiles, math='median')
        infiles = [cout[0]]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)
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
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.get_header()
        # ------------------------------------------------------------------
        # check that file has valid DPRTYPE
        # ------------------------------------------------------------------
        dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
        # if dprtype is incorrect skip
        if dprtype not in params.listp('CCF_ALLOWED_DPRTYPES'):
            # join allowed dprtypes
            allowed_dprtypes = ', '.join(params.listp('CCF_ALLOWED_DPRTYPES'))
            # log that we are skipping
            wargs = [dprtype, recipe.name, allowed_dprtypes, infile.basename]
            WLOG(params, 'warning', textentry('10-019-00001', args=wargs),
                 sublevel=4)
            # continue
            continue
        # flag whether calibration fiber is FP
        if dprtype in params.listp('CCF_VALID_FP_DPRTYPES'):
            has_fp = True
        else:
            has_fp = False
        # ------------------------------------------------------------------
        # get fiber from infile
        fiber = infile.get_fiber(header=header)
        # ----------------------------------------------------------------------
        # Check we are using correct fiber
        # ----------------------------------------------------------------------
        pconst = constants.pload()
        sfiber, rfiber = pconst.FIBER_KINDS()
        if fiber not in sfiber:
            # log that the science fiber was not correct
            eargs = [fiber, ' or '.join(sfiber), infile.name,
                     infile.filename, mainname]
            WLOG(params, 'error', textentry('09-020-00001', args=eargs))

        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        # get berv from header
        bprops = extract.get_berv(params, infile, log=False)
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe, fiber=fiber,
                                       infile=infile, database=calibdbm)
        # ------------------------------------------------------------------
        # Get blaze
        # ------------------------------------------------------------------
        bout = flat_blaze.get_blaze(params, header, fiber)
        blazefile, blazetime, blaze = bout

        # ------------------------------------------------------------------
        #   Remove domain with telluric > 50%
        # ------------------------------------------------------------------
        outtype = infile.get_hkey('KW_OUTPUT', dtype=str)
        # get ccf fibers
        recon_sfiber, recon_rfiber = pconst.FIBER_CCF()
        # correct tellurics
        if outtype in params['CCF_CORRECT_TELLU_TYPES']:
            # remove telluric domain below a defined threshold
            #    and return the infile (with infile.data updated)
            targs = [infile, fiber]
            image = velocity.remove_telluric_domain(params, *targs)
        else:
            image = infile.get_data(copy=True)

        # ------------------------------------------------------------------
        # Compute CCF on science channel
        # ------------------------------------------------------------------
        # log progress: Computing CCF on fiber
        WLOG(params, 'info', textentry('40-020-00007', args=[fiber]))
        # compute ccf
        cargs = [infile, image, blaze, wprops['WAVEMAP'], bprops, fiber]
        rv_props1 = velocity.compute_ccf_science(params, recipe, *cargs)

        # ------------------------------------------------------------------
        # Compute CCF on reference fiber (FP only)
        # ------------------------------------------------------------------
        if has_fp:
            # find the c fiber file
            infile_r = drs_file.locate_calibfiber_file(params, infile)
            # get the wave solution associated with this file
            wprops_r = wave.get_wavesolution(params, recipe, fiber='C',
                                             infile=infile_r,
                                             database=calibdbm)
            # get c fiber file time
            filetime_r = infile_r.get_hkey('KW_MID_OBS_TIME')

            # --------------------------------------------------------------
            # deal with differing wavelength solutions (between science and
            #    reference)
            if wprops['WAVETIME'] != wprops_r['WAVETIME']:
                # log warning
                wargs = [wprops_r['WAVETIME'], wprops['WAVETIME'],
                         wprops_r['WAVEFILE'], wprops['WAVEFILE']]
                WLOG(params, 'warning', textentry('10-020-00003', args=wargs),
                     sublevel=2)
                # set the reference wave solution to the science wave solution
                wprops_r = wprops
            # log progress: Computing CCF on fiber
            WLOG(params, 'info', textentry('40-020-00007', args=[fiber]))
            # --------------------------------------------------------------
            # Compute CCF on reference channel
            cargs = [infile_r, infile_r.get_data(), blaze, wprops_r['WAVEMAP'],
                     rfiber]
            rv_props2 = velocity.compute_ccf_fp(params, recipe, *cargs)
            # get the time difference (between file and wave)
            timediff = filetime_r - wprops_r['WAVETIME']
            # --------------------------------------------------------------
            # compute the rv output stats
            # --------------------------------------------------------------
            # need to deal with no drift from wave solution
            if wprops_r['WFP_DRIFT'] is None:
                rv_wave_fp = np.nan
                rv_simu_fp = rv_props2['MEAN_RV']
                rv_drift = rv_simu_fp
                rv_obj = rv_props1['MEAN_RV']
                rv_corrected = rv_obj - rv_drift
            # else we have drift from wave solution
            else:
                rv_wave_fp = wprops_r['WFP_DRIFT']
                rv_simu_fp = rv_props2['MEAN_RV']
                rv_drift = rv_wave_fp - rv_simu_fp
                rv_obj = rv_props1['MEAN_RV']
                rv_corrected = rv_obj - rv_drift
        # need to deal with no drift from wave solution and no simultaneous FP
        elif wprops['WFP_DRIFT'] is None:
            # set rv_props2
            rv_props2 = ParamDict()
            # compute the stats
            rv_wave_fp = np.nan
            rv_simu_fp = np.nan
            rv_drift = 0.0
            rv_obj = rv_props1['MEAN_RV']
            rv_corrected = rv_obj - rv_drift
            infile_r = None
            wprops_r = None
            timediff = np.nan
        # need way to deal no simultaneous FP
        else:
            # set rv_props2
            rv_props2 = ParamDict()
            # compute the stats
            rv_wave_fp = 0.0
            rv_simu_fp = 0.0
            rv_drift = 0.0
            rv_obj = rv_props1['MEAN_RV']
            rv_corrected = rv_obj - rv_drift
            infile_r = None
            wprops_r = None
            timediff = np.nan
        # ------------------------------------------------------------------
        # add rv stats to properties
        rv_props1['RV_WAVEFILE'] = wprops['WAVEFILE']
        rv_props1['RV_WAVETIME'] = wprops['WAVETIME']
        rv_props1['RV_WAVESRCE'] = wprops['WAVESOURCE']
        rv_props1['RV_TIMEDIFF'] = timediff
        rv_props1['RV_WAVE_FP'] = rv_wave_fp
        rv_props1['RV_SIMU_FP'] = rv_simu_fp
        rv_props1['RV_DRIFT'] = rv_drift
        rv_props1['RV_OBJ'] = rv_obj
        rv_props1['RV_CORR'] = rv_corrected
        # set sources
        keys = ['RV_WAVEFILE', 'RV_WAVETIME', 'RV_WAVESRCE', 'RV_TIMEDIFF',
                'RV_WAVE_FP', 'RV_SIMU_FP', 'RV_DRIFT', 'RV_OBJ', 'RV_CORR']
        rv_props1.set_sources(keys, mainname)
        # add the fp fiber properties
        if has_fp:
            rv_props2['RV_WAVEFILE'] = wprops_r['WAVEFILE']
            rv_props2['RV_WAVETIME'] = wprops_r['WAVETIME']
            rv_props2['RV_WAVESRCE'] = wprops_r['WAVESOURCE']
            rv_props2['RV_TIMEDIFF'] = timediff
            rv_props2['RV_WAVE_FP'] = rv_wave_fp
            rv_props2['RV_SIMU_FP'] = rv_simu_fp
            rv_props2['RV_DRIFT'] = rv_drift
            rv_props2['RV_OBJ'] = rv_obj
            rv_props2['RV_CORR'] = rv_corrected
            rv_props2.set_sources(keys, mainname)

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        # set passed variable and fail message list
        fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
        # no quality control currently
        qc_values.append('None')
        qc_names.append('None')
        qc_logic.append('None')
        qc_pass.append(1)
        # ------------------------------------------------------------------
        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if np.sum(qc_pass) == len(qc_pass):
            WLOG(params, 'info', textentry('40-005-10001'))
            passed = 1
        else:
            for farg in fail_msg:
                WLOG(params, 'warning', textentry('40-005-10002') + farg,
                     sublevel=6)
            passed = 0
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # update recipe log
        log1.add_qc(qc_params, passed)

        # ------------------------------------------------------------------
        # archive ccf from science fiber
        # ------------------------------------------------------------------
        velocity.write_ccf(params, recipe, infile, rv_props1, rawfiles,
                           combine, qc_params, fiber)

        # ------------------------------------------------------------------
        # archive ccf from reference fiber
        # ------------------------------------------------------------------
        if has_fp:
            velocity.write_ccf(params, recipe, infile_r, rv_props2, rawfiles,
                               combine, qc_params, rfiber)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end()

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

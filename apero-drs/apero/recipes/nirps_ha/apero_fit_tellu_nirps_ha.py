#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_fit_tellu_nirps_ha.py [obs dir] [files]

Using all transmission files, we fit the absorption of a given science
observation.

Created on 2019-09-05 at 14:58

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.science import extract
from apero.science import telluric
from apero.science.calib import wave
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_fit_tellu_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
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
    Main function for apero_fit_tellu

    :param obs_dir: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
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
    # get whether we should only do precleaning (not recommended)
    #   debug purposes only
    onlypreclean = False
    if 'ONLYPRECLEAN' in params['INPUTS']:
        onlypreclean = params['INPUTS']['ONLYPRECLEAN']
    # force only preclean from params
    if params['TELLU_ONLY_PRECLEAN']:
        onlypreclean = True
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
        cond = drs_file.combine(params, recipe, infiles, math='median')
        infiles = [cond[0]]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)
    # load the calibration and telluric databases
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    telludbm = drs_database.TelluricDatabase(params)
    telludbm.load_db()
    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', it)
        # flag only doing pre-clean
        log1.update_flags(ONLYPRECLEAN=onlypreclean)
        # ------------------------------------------------------------------
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.get_header()
        # get image
        image = infile.get_data(copy=True)
        # ------------------------------------------------------------------
        # check that file has valid DPRTYPE
        # ------------------------------------------------------------------
        dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
        # if dprtype is incorrect skip
        if dprtype not in params['TELLU_ALLOWED_DPRTYPES']:
            # join allowed dprtypes
            allowed_dprtypes = ', '.join(params['TELLU_ALLOWED_DPRTYPES'])
            # log that we are skipping
            wargs = [dprtype, recipe.name, allowed_dprtypes, infile.basename]
            WLOG(params, 'warning', textentry('10-019-00001', args=wargs),
                 sublevel=4)
            # end log correctly
            log1.end()
            # continue
            continue
        # ------------------------------------------------------------------
        # check that file objname is not in blacklist
        # ------------------------------------------------------------------
        objname = infile.get_hkey('KW_OBJNAME', dtype=str)
        # get black list
        tellu_exclude_list = telluric.get_tellu_exclude_list(params)
        # if objname in blacklist then skip
        if objname in tellu_exclude_list:
            # log that we are skipping
            wargs = [infile.basename, params['KW_OBJNAME'][0], objname]
            WLOG(params, 'warning', textentry('10-019-00002', args=wargs),
                 sublevel=2)
            # end log correctly
            log1.end()
            # continue
            continue
        else:
            # log that file is validated
            args = [objname, dprtype]
            WLOG(params, 'info', textentry('40-019-00048', args=args))
        # ------------------------------------------------------------------
        # get fiber from infile
        fiber = infile.get_fiber(header=header)
        # ------------------------------------------------------------------
        # load reference wavelength solution for this fiber
        # get pseudo constants
        pconst = load_functions.load_pconfig(select.INSTRUMENTS)
        # deal with fibers that we don't have
        usefiber = pconst.FIBER_WAVE_TYPES(fiber)
        # ------------------------------------------------------------------
        # load reference wavelength solution
        refprops = wave.get_wavesolution(params, recipe, ref=True,
                                         fiber=fiber, infile=infile,
                                         database=calibdbm)
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe, fiber=fiber,
                                       infile=infile, database=calibdbm)

        # ------------------------------------------------------------------
        # Get template file (if available)
        # ------------------------------------------------------------------
        template_props = telluric.load_templates(params, header, objname, fiber,
                                                 database=telludbm)


        # ------------------------------------------------------------------
        # Load transmission model
        # ------------------------------------------------------------------
        if not onlypreclean:
            trans_props = telluric.get_trans_model(params, header, fiber,
                                                   database=telludbm)
        else:
            trans_props = ParamDict()
            trans_props['TRANS_TABLE'] = None

        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        bprops = extract.get_berv(params, infile)

        # ------------------------------------------------------------------
        # Shift the template from reference wave solution --> night
        #     wave solution
        template_props = telluric.shift_template(params, recipe, image,
                                                 template_props, refprops,
                                                 wprops, bprops)
        # ------------------------------------------------------------------
        # mask bad regions
        # ------------------------------------------------------------------
        # Some regions cannot be telluric corrected and the data should be
        #   just set to NaNs to avoid bad corrections
        infile.data = telluric.mask_bad_regions(params, infile.data,
                                                wprops['WAVEMAP'],
                                                pconst=pconst)

        # ------------------------------------------------------------------
        # apply sky correction
        # ------------------------------------------------------------------
        if dprtype in params['ALLOWED_SKYCORR_DPRTYPES']:
            # correct sky using model and B fiber
            scprops = telluric.correct_sky_with_ref(params, recipe, infile,
                                                    wprops, rawfiles, combine,
                                                    calibdbm, telludbm)
            # update infile
            infile.data = scprops[f'CORR_EXT_{fiber}']
            # turn off cleaning of OH lines in pre-cleaning
            clean_ohlines = False
        else:
            # correct sky using model and B fiber
            scprops = telluric.correct_sky_no_ref(params, recipe, infile,
                                                  wprops, rawfiles, combine,
                                                  calibdbm, telludbm)
            # update infile
            infile.data = scprops[f'CORR_EXT_{fiber}']
            # turn off cleaning of OH lines in pre-cleaning
            clean_ohlines = False

        # ------------------------------------------------------------------
        # telluric pre-cleaning
        # ------------------------------------------------------------------
        tpreprops = telluric.tellu_preclean(params, recipe, infile, wprops,
                                            fiber, rawfiles, combine,
                                            database=telludbm,
                                            template_props=template_props,
                                            clean_ohlines=clean_ohlines,
                                            sky_props=scprops)
        # get corrected image out of pre-cleaning parameter dictionary
        image1 = tpreprops['CORRECTED_E2DS']

        # ------------------------------------------------------------------
        # Get blaze
        # ------------------------------------------------------------------
        nprops = telluric.get_blaze_props(params, header, fiber)

        # ------------------------------------------------------------------
        # Calculate residual model and correct spectrum
        # ------------------------------------------------------------------
        if not onlypreclean:
            cprops = telluric.calc_res_model(params, recipe, image, image1,
                                             trans_props, tpreprops, refprops,
                                             wprops, infile)
        else:
            cprops = telluric.pclean_only(tpreprops)

        # ------------------------------------------------------------------
        # Create 1d spectra (s1d) of the corrected E2DS file
        # ------------------------------------------------------------------
        scargs = [wprops['WAVEMAP'], cprops['CORRECTED_SP'], nprops['BLAZE']]
        scwprops = extract.e2ds_to_s1d(params, recipe, *scargs, wgrid='wave',
                                       fiber=fiber, s1dkind='corrected sp')
        scvprops = extract.e2ds_to_s1d(params, recipe, *scargs,
                                       wgrid='velocity', fiber=fiber,
                                       s1dkind='corrected sp')

        # ------------------------------------------------------------------
        # Create 1d spectra (s1d) of the reconstructed absorption
        # ------------------------------------------------------------------
        # must multiple recon by blaze (for proper weighting in s1d)
        brecon = cprops['RECON_ABSO'] * nprops['BLAZE']
        # do s1d
        rcargs = [wprops['WAVEMAP'], brecon, nprops['BLAZE']]
        rcwprops = extract.e2ds_to_s1d(params, recipe, *rcargs, wgrid='wave',
                                       fiber=fiber, s1dkind='recon')
        rcvprops = extract.e2ds_to_s1d(params, recipe, *rcargs,
                                       wgrid='velocity', fiber=fiber,
                                       s1dkind='recon')

        # ------------------------------------------------------------------
        # s1d plots
        # ------------------------------------------------------------------
        # plot the s1d plot
        recipe.plot('EXTRACT_S1D', params=params, props=scwprops,
                    fiber=fiber, kind='corrected sp')
        recipe.plot('EXTRACT_S1D', params=params, props=rcwprops,
                    fiber=fiber, kind='recon')

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        qc_params, passed = telluric.fit_tellu_quality_control(params, infile,
                                                               tpreprops)
        # update recipe log
        log1.add_qc(qc_params, passed)

        # ------------------------------------------------------------------
        # Save corrected E2DS to file
        # ------------------------------------------------------------------
        fargs = [infile, rawfiles, fiber, combine, nprops, wprops,
                 trans_props, cprops, qc_params, template_props, tpreprops]
        corrfile = telluric.fit_tellu_write_corrected(params, recipe, *fargs)

        # ------------------------------------------------------------------
        # Save 1d corrected spectra to file
        # ------------------------------------------------------------------
        fsargs = [infile, corrfile, fiber, scwprops, scvprops]
        telluric.fit_tellu_write_corrected_s1d(params, recipe, *fsargs)

        # ------------------------------------------------------------------
        # Save reconstructed absorption to file (E2DS + S1D)
        # ------------------------------------------------------------------
        frargs = [infile, corrfile, fiber, cprops, rcwprops, rcvprops]
        reconfile = telluric.fit_tellu_write_recon(params, recipe, *frargs)

        # ------------------------------------------------------------------
        # Correct other science fibers (using recon)
        # ------------------------------------------------------------------
        # get fibers
        sfibers, rfiber = pconst.FIBER_KINDS()
        # loop around fibers and correct/create s1d/save
        for sfiber in sfibers:
            # print that we are correcting other fibers
            # log: Correcting fiber {0}
            WLOG(params, 'info', textentry('40-019-00049', args=[sfiber]))
            # skip reference fiber
            if sfiber == fiber:
                continue
            # else correct/create s1d/ and save
            coargs = [sfiber, infile, cprops, rawfiles, combine, qc_params,
                      template_props, tpreprops, trans_props]
            telluric.correct_other_science(params, recipe, *coargs,
                                           database=calibdbm)

        # ------------------------------------------------------------------
        # Add TELLU_OBJ and TELLU_RECON to database
        # ------------------------------------------------------------------
        if np.all(qc_params[3]) and params['INPUTS']['DATABASE']:
            # copy the tellu_obj file to database
            telludbm.add_tellu_file(corrfile)
            # copy the tellu_rcon file to database
            telludbm.add_tellu_file(reconfile)

        # ------------------------------------------------------------------
        # Summary plots
        # ------------------------------------------------------------------
        # plot the s1d plot
        recipe.plot('SUM_EXTRACT_S1D', params=params, props=scwprops,
                    fiber=fiber, kind='corrected sp')
        recipe.plot('SUM_EXTRACT_S1D', params=params, props=rcwprops,
                    fiber=fiber, kind='recon')
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        telluric.fit_tellu_summary(recipe, it, params, qc_params, tpreprops,
                                   fiber)
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

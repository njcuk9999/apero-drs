#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
obj_fit_tellu [night_directory] [files]

Using all transmission files, we fit the absorption of a given science
observation. To reduce the number of degrees of freedom, we perform a PCA and
keep only the N (currently we suggest N=5)  principal components in absorbance.
As telluric absorption may shift in velocity from one observation to another,
we have the option of including the derivative of the absorbance in the
reconstruction. The method also measures a proxy of optical depth per molecule
(H2O, O2, O3, CO2, CH4, N2O) that can be used for data quality assessment.

Usage:
  obj_fit_tellu night_name object.fits

Outputs:
  telluDB: TELL_OBJ file - The object corrected for tellurics
        file also saved in the reduced folder
        input file + '_tellu_corrected.fits'

    recon_abso file - The reconstructed absorption file saved in the reduced
                    folder
        input file + '_tellu_recon.fits'

Created on 2019-09-05 at 14:58

@author: cook
"""
import numpy as np

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.core import drs_database
from apero.science.calib import wave
from apero.science import extract
from apero.science import telluric


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_fit_tellu_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
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
def main(obs_dir=None, files=None, **kwargs):
    """
    Main function for obj_fit_tellu_spirou.py

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
    # deal with input data from function
    if 'files' in params['DATA_DICT']:
        infiles = params['DATA_DICT']['files']
        rawfiles = params['DATA_DICT']['rawfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        infiles = [drs_file.combine(params, recipe, infiles, math='median')]
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
        if dprtype not in params.listp('TELLU_ALLOWED_DPRTYPES'):
            # join allowed dprtypes
            allowed_dprtypes = ', '.join(params.listp('TELLU_ALLOWED_DPRTYPES'))
            # log that we are skipping
            wargs = [dprtype, recipe.name, allowed_dprtypes, infile.basename]
            WLOG(params, 'warning', textentry('10-019-00001', args=wargs))
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
            WLOG(params, 'warning', textentry('10-019-00002', args=wargs))
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
        # load master wavelength solution for this fiber
        # get pseudo constants
        pconst = constants.pload()
        # deal with fibers that we don't have
        usefiber = pconst.FIBER_WAVE_TYPES(fiber)
        # ------------------------------------------------------------------
        # load master wavelength solution
        mprops = wave.get_wavesolution(params, recipe, header, master=True,
                                       fiber=fiber, infile=infile,
                                       database=calibdbm)
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe, header, fiber=fiber,
                                       infile=infile, database=calibdbm)

        # ------------------------------------------------------------------
        # telluric pre-cleaning
        # ------------------------------------------------------------------
        tpreprops = telluric.tellu_preclean(params, recipe, infile, wprops,
                                            fiber, rawfiles, combine,
                                            database=telludbm)
        # get variables out of tpreprops
        image1 = tpreprops['CORRECTED_E2DS']
        # ------------------------------------------------------------------
        # Normalize image by peak blaze
        # ------------------------------------------------------------------
        nargs = [image1, header, fiber]
        _, nprops = telluric.normalise_by_pblaze(params, *nargs)
        # normalise by the blaze
        image2 = image1 / nprops['NBLAZE']
        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        bprops = extract.get_berv(params, infile)
        # ------------------------------------------------------------------
        # Load transmission files
        # ------------------------------------------------------------------
        trans_files = telluric.get_trans_files(params, header, fiber,
                                               database=telludbm)
        # ------------------------------------------------------------------
        # Get template file (if available)
        # ------------------------------------------------------------------
        tout = telluric.load_templates(params, header, objname, fiber,
                                       database=telludbm)
        template, template_props = tout
        # ------------------------------------------------------------------
        # load the expected atmospheric transmission
        # ------------------------------------------------------------------
        largs = [header, mprops, fiber]
        tapas_props = telluric.load_conv_tapas(params, recipe, *largs,
                                               database=telludbm)
        # ------------------------------------------------------------------
        # Generate the absorption map + calculate PCA components
        # ------------------------------------------------------------------
        pargs = [image2, trans_files, fiber, mprops, tpreprops]
        pca_props = telluric.gen_abso_pca_calc(params, recipe, *pargs)
        # ------------------------------------------------------------------
        # Shift the template/pca components and tapas spectrum to correct
        #     frames
        #   shift from master wave solution --> night wave solution
        # ------------------------------------------------------------------
        sargs = [image2, template, bprops, mprops, wprops, pca_props,
                 tapas_props]
        sprops = telluric.shift_all_to_frame(params, recipe, *sargs)
        # ------------------------------------------------------------------
        # Calculate reconstructed absorption + correct E2DS file
        # ------------------------------------------------------------------
        cargs = [image2, wprops, pca_props, sprops, nprops, tpreprops]
        cprops = telluric.calc_recon_and_correct(params, recipe, *cargs)

        # ------------------------------------------------------------------
        # Create 1d spectra (s1d) of the corrected E2DS file
        # ------------------------------------------------------------------
        scargs = [wprops['WAVEMAP'], cprops['CORRECTED_SP'], nprops['BLAZE']]
        scwprops = extract.e2ds_to_s1d(params, recipe, *scargs, wgrid='wave',
                                       fiber=fiber, kind='corrected sp')
        scvprops = extract.e2ds_to_s1d(params, recipe, *scargs,
                                       wgrid='velocity', fiber=fiber,
                                       kind='corrected sp')

        # ------------------------------------------------------------------
        # Create 1d spectra (s1d) of the reconstructed absorption
        # ------------------------------------------------------------------
        rcargs = [wprops['WAVEMAP'], cprops['RECON_ABSO_SP'], nprops['BLAZE']]
        rcwprops = extract.e2ds_to_s1d(params, recipe, *rcargs, wgrid='wave',
                                       fiber=fiber, kind='recon')
        rcvprops = extract.e2ds_to_s1d(params, recipe, *rcargs,
                                       wgrid='velocity', fiber=fiber,
                                       kind='recon')

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
        fargs = [infile, rawfiles, fiber, combine, nprops, wprops, pca_props,
                 sprops, cprops, qc_params, template_props, tpreprops]
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
        pconst = constants.pload()
        sfibers, rfiber = pconst.FIBER_KINDS()
        # loop around fibers and correct/create s1d/save
        for sfiber in sfibers:
            # print that we are correcting other fibers
            # log: Correcting fiber {0}
            WLOG(params, 'info', textentry('40-019-00049', args=[sfiber]))
            # skip master fiber
            if sfiber == fiber:
                continue
            # else correct/create s1d/ and save
            coargs = [sfiber, infile, cprops, rawfiles, combine, pca_props,
                      sprops, qc_params, template_props, tpreprops]
            telluric.correct_other_science(params, recipe, *coargs,
                                           database=calibdbm)

        # ------------------------------------------------------------------
        # Add TELLU_OBJ and TELLU_RECON to database
        # ------------------------------------------------------------------
        if np.all(qc_params[3]):
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
        telluric.fit_tellu_summary(recipe, it, params, qc_params, pca_props,
                                   sprops, cprops, fiber)
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

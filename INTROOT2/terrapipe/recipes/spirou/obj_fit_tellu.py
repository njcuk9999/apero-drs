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
from __future__ import division
import numpy as np

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.io import drs_fits
from terrapipe.science.calib import wave
from terrapipe.science import extract
from terrapipe.science import telluric


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_fit_tellu.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict


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
    Main function for cal_extract_spirou.py

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

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.header
        # get image
        image = infile.image
        # ------------------------------------------------------------------
        # check that file has valid DPRTYPE
        # ------------------------------------------------------------------
        dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
        # if dprtype is incorrect skip
        if dprtype not in params.listp('TEELU_ALLOWED_DPRTYPES'):
            # join allowed dprtypes
            allowed_dprtypes = ', '.join(params.listp('TEELU_ALLOWED_DPRTYPES'))
            # log that we are skipping
            wargs = [dprtype, recipe.name, allowed_dprtypes, infile.basename]
            WLOG(params, 'warning', TextEntry('10-019-00001', args=wargs))
            # continue
            continue
        # ------------------------------------------------------------------
        # check that file objname is not in blacklist
        # ------------------------------------------------------------------
        objname = infile.get_key('KW_OBJNAME', dtype=str)
        # get black list
        blacklist = telluric.get_blacklist(params)
        # if objname in blacklist then skip
        if objname in blacklist:
            # log that we are skipping
            wargs = [infile.basename, params['KW_OBJNAME'][0], objname]
            WLOG(params, 'warning', TextEntry('10-019-00002', args=wargs))
            # continue
            continue
        # ------------------------------------------------------------------
        # get fiber from infile
        fiber = infile.get_fiber(header=header)
        # ------------------------------------------------------------------
        # load master wavelength solution for this fiber
        # get pseudo constants
        pconst = constants.pload(params['INSTRUMENT'])
        # deal with fibers that we don't have
        usefiber = pconst.FIBER_WAVE_TYPES(fiber)
        # ------------------------------------------------------------------
        # load master wavelength solution
        mprops = wave.get_wavesolution(params, recipe, header, master=True,
                                       fiber=fiber)
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe, header, fiber=fiber)
        # ------------------------------------------------------------------
        # Normalize image by peak blaze
        # ------------------------------------------------------------------
        nargs = [image, header, fiber]
        image2, nprops = telluric.normalise_by_pblaze(params, *nargs)
        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        bprops = extract.get_berv(params, infile, dprtype=dprtype)
        # ----------------------------------------------------------------------
        # Load transmission files
        # ----------------------------------------------------------------------
        trans_files = telluric.get_trans_files(params, recipe, header, fiber)
        # ------------------------------------------------------------------
        # Get template file (if available)
        # ------------------------------------------------------------------
        tout = telluric.load_templates(params, header, objname, fiber)
        template, template_file = tout
        # ----------------------------------------------------------------------
        # load the expected atmospheric transmission
        # ----------------------------------------------------------------------
        tpargs = [header, mprops, fiber]
        tapas_props = telluric.load_tapas_convolved(params, recipe, *tpargs)
        # ----------------------------------------------------------------------
        # Generate the absorption map + calculate PCA components
        # ----------------------------------------------------------------------
        pargs = [image2, trans_files, fiber]
        pca_props = telluric.gen_abso_pca_calc(params, recipe, *pargs)
        # ------------------------------------------------------------------
        # Shift the template/pca components and tapas spectrum to correct
        #     frames
        # ------------------------------------------------------------------
        sargs = [image2, template, bprops, mprops, wprops, pca_props,
                 tapas_props]
        sprops = telluric.shift_all_to_frame(params, *sargs)
        # ------------------------------------------------------------------
        # Calculate reconstructed absorption + correct E2DS file
        # ------------------------------------------------------------------
        cargs = [image, wprops, pca_props, sprops]
        cprops = telluric.calc_recon_and_correct(params, *cargs)

        # ------------------------------------------------------------------
        # Create 1d spectra (s1d) of the corrected E2DS file
        # ------------------------------------------------------------------
        scargs = [wprops['WAVEMAP'], cprops['CORRECTED_SP'], nprops['BLAZE']]
        scwprops = extract.e2ds_to_s1d(params, *scargs, wgrid='wave')
        scvprops = extract.e2ds_to_s1d(params, *scargs, wgrid='velocity')

        # ------------------------------------------------------------------
        # Create 1d spectra (s1d) of the reconstructed absorption
        # ------------------------------------------------------------------
        rcargs = [wprops['WAVEMAP'], cprops['RECON_ABSO_SP'], nprops['BLAZE']]
        rcwprops = extract.e2ds_to_s1d(params, *rcargs, wgrid='wave')
        rcvprops = extract.e2ds_to_s1d(params, *rcargs, wgrid='velocity')

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        qc_params = telluric.fit_tellu_quality_control(params, infile)

        # ------------------------------------------------------------------
        # Save corrected E2DS to file
        # ------------------------------------------------------------------
        fargs = [infile, rawfiles, fiber, combine, nprops, wprops, pca_props,
                 sprops, cprops, qc_params]
        corrfile = telluric.fit_tellu_write_corrected(params, recipe, *fargs)

        # ------------------------------------------------------------------
        # Save 1d corrected spectra to file
        # ------------------------------------------------------------------
        fsargs = [infile, corrfile, fiber, scwprops, scvprops]
        telluric.fit_tellu_write_corrected_s1d(params, recipe, *fsargs)

        # ------------------------------------------------------------------
        # Save reconstructed absorption to file (E2DS + S1D)
        # ------------------------------------------------------------------
        frargs = [infile. corrfile, fiber, cprops, rcwprops, rcvprops]
        reconfile = telluric.fit_tellu_write_recon(params, recipe, *frargs)

        # ------------------------------------------------------------------
        # Add TELLU_OBJ and TELLU_RECON to database
        # ------------------------------------------------------------------
        if np.all(qc_params[3]):
            # copy the tellu_obj file to database
            drs_database.add_file(params, corrfile)
            # copy the tellu_rcon file to database
            drs_database.add_file(params, reconfile)

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
    # Post main plot clean up
    core.post_main(ll['params'], has_plots=True)

# =============================================================================
# End of code
# =============================================================================

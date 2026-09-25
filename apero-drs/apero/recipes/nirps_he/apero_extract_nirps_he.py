#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_extract_nirps_he.py [obs dir] [ files]

APERO extraction recipe for NIRPS HE

Created on 2019-07-05 at 16:46

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
import apero as apero_pkg
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.science import extract
from apero.science.calib import flat_blaze
from apero.science.calib import gen_calib
from apero.science.calib import leak
from apero.science.calib import localisation
from apero.science.calib import shape
from apero.science.calib import thermal
from apero.science.calib import wave
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_extract_nirps_he.py'
__INSTRUMENT__ = 'NIRPS_HE'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
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
    Main function for apero_extract

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
    # load instrument pseudo-constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # -------------------------------------------------------------------------
    # Setup: input files and combine options
    # -------------------------------------------------------------------------
    # get input files and check QC
    infiles = params['INPUTS']['FILES'][1]
    infiles = drs_file.check_input_qc(params, infiles, 'files')
    # collect raw basenames for header provenance
    rawfiles = [infile.basename for infile in infiles]
    # handle files / combine mode passed via DATA_DICT (e.g. from apero_flat)
    if 'files' in params['DATA_DICT']:
        if params['DATA_DICT']['files'] is not None:
            infiles = params['DATA_DICT']['files']
        rawfiles = params['DATA_DICT']['rawfiles']
        combine = params['DATA_DICT']['combine']
    elif params['IMAGE.COMBINE_INPUT']:
        # combine all input frames into one before processing
        cond = drs_file.combine(params, recipe, infiles,
                                math=params['INPUTS']['COMBINE_METHOD'])
        infiles = [cond[0]]
        combine = True
    else:
        combine = False
    num_files = len(infiles)
    # -------------------------------------------------------------------------
    # Setup: pipeline control flags from DATA_DICT / INPUTS
    # -------------------------------------------------------------------------
    quicklook = params['CAL.EXT.QUICKLOOK']
    # leak correction flag may be injected by the calling recipe
    if 'leakcorr' in params['DATA_DICT']:
        params['INPUTS']['LEAKCORR'] = params['DATA_DICT']['LEAKCORR']
    # wavelength solution file may be injected by the calling recipe
    if 'wavefile' in params['DATA_DICT']:
        params['INPUTS']['WAVEFILE'] = params['DATA_DICT']['WAVEFILE']
    # extract_type controls whether flat-response products are generated
    if 'EXTRACT_TYPE' in params['DATA_DICT']:
        params['INPUTS']['EXTRACT_TYPE'] = (
            params['DATA_DICT']['EXTRACT_TYPE'])
    else:
        params['INPUTS']['EXTRACT_TYPE'] = 'standard'
    # -------------------------------------------------------------------------
    # Load calibration database (shared across all files)
    # -------------------------------------------------------------------------
    calibdbm = drs_database.CalibrationDatabase(params, recipe.shortname)
    calibdbm.load_db()
    # =========================================================================
    # Loop around input files
    # =========================================================================
    for it in range(num_files):
        # add level to recipe log and initialise plotting for this file
        log1 = recipe.log.add_level(params, 'num', it)
        recipe.plot.set_location(it)
        drs_startup.file_processing_update(params, it, num_files)
        infile = infiles[it]
        # --------------------------------------------------------------------
        # Skip files that do not match the required DPRTYPE / OBJNAME filters
        # --------------------------------------------------------------------
        skip, skip_conditions = gen_calib.check_files(
            params, recipe.shortname, infile)
        if skip:
            if 'DPRTYPE' in skip_conditions[0]:
                WLOG(params, 'warning',
                     textentry('10-016-00012',
                               args=skip_conditions[1]), sublevel=2)
            if 'OBJNAME' in skip_conditions[0]:
                WLOG(params, 'warning',
                     textentry('10-016-00013',
                               args=skip_conditions[2]), sublevel=2)
            log1.write_logfile()
            continue
        extract_type = params['INPUTS']['EXTRACT_TYPE']
        # --------------------------------------------------------------------
        # Main extraction: shape → calibrate → profiles → model
        # Returns image, image2, sprops, props, oprops, model_props, eprops_all
        # --------------------------------------------------------------------
        WLOG(params, 'info',
             'Running main extraction (shape, calibration, '
             'profiles, model)')
        mprops = extract.main_extract(params, recipe, infile, pconst,
                                      database=calibdbm)
        WLOG(params, '', 'Main extraction complete')
        # reference spectrum used by leak correction for all science fibers
        ref_e2ds = (mprops['MODEL_PROPS']['SPECTRA']
                    [mprops['REF_FIBER']][0])
        # --------------------------------------------------------------------
        # Flat response: per-order response profiles (flat extractions only)
        # --------------------------------------------------------------------
        if extract_type == 'flat':
            WLOG(params, '', 'Computing flat-response profiles')
            frargs = [params, recipe, mprops['MODEL_PROPS'],
                      mprops['ORDER_PROPS']['ORDER_MAP'],
                      mprops['ORDER_PROPS']['ORDER_RANGES']]
            frout = flat_blaze.compute_flat_response(*frargs)
            flat_response, flat_response_err = frout
        else:
            flat_response = dict()
        # --------------------------------------------------------------------
        # Barycentric correction (skipped in quick-look mode)
        # --------------------------------------------------------------------
        if not quicklook:
            WLOG(params, '', 'Computing barycentric velocity correction')
            bprops = extract.get_berv(params, infile, mprops['HEADER'])
        else:
            bprops = None
        # storage for downstream output files (e.g. for wave recipe)
        e2dsoutputs = dict()
        # =====================================================================
        # Fiber loop: post-extraction calibrations and output products
        # =====================================================================
        for fiber in mprops['FIBERTYPES']:
            log2 = log1.add_level(params, 'fiber', fiber)
            if quicklook:
                log2.update_flags(QUICKLOOK=True)
            wargs = [fiber, ', '.join(mprops['FIBERTYPES'])]
            WLOG(params, 'info', textentry('40-016-00014', args=wargs))
            # per-fiber extraction properties (mutated below by calibrations)
            eprops = mprops['EPROPS_ALL'][fiber]
            # short aliases for dicts subscripted repeatedly in this loop body
            sprops = mprops['SHAPE_PROPS']
            oprops = mprops['ORDER_PROPS']
            # ----------------------------------------------------------------
            # Wavelength solution for this fiber (skipped in quick-look mode)
            # ----------------------------------------------------------------
            if not quicklook:
                mwave = params['INPUTS'].get('FORCE_REF_WAVE', False)
                wpargs = [params, recipe, mprops['HEADER']]
                wpkwargs = dict(fiber=fiber, ref=mwave,
                                database=calibdbm, log=log2)
                wprops = wave.get_wavesolution(*wpargs, **wpkwargs)
            else:
                wprops = ParamDict()
            # wavemap is None for quick-look (no wave solution loaded)
            wavemap = wprops.get('WAVEMAP', None)
            # ----------------------------------------------------------------
            # Localisation coefficients for this fiber
            # ----------------------------------------------------------------
            lpargs = [params, recipe, mprops['HEADER']]
            lpkwargs = dict(fiber=fiber, merge=True, database=calibdbm)
            lprops = localisation.get_coefficients(*lpargs, **lpkwargs)
            # straightened localisation coefficients (for plots)
            lcoeffs = lprops['CENT_COEFFS']
            lcoeffs2 = shape.ea_transform_coeff(mprops['IMAGE_STRAIGHT'],
                                                lcoeffs, sprops['SHAPEL'])
            # attach order-profile provenance to localisation props
            lprops['ORDERP'] = oprops['ORDERP'][fiber]
            lprops['ORDERPFILE'] = oprops['ORDERPFILE'][fiber]
            lprops['ORDERPTIME'] = oprops['ORDERPTIME'][fiber]
            lprops.set_sources(
                ['ORDERP', 'ORDERPFILE', 'ORDERPTIME'], mainname)
            # ----------------------------------------------------------------
            # Blaze calibration for this fiber
            # get_blaze returns a unity blaze for flat extractions and
            # loads from the calibDB otherwise.
            # ----------------------------------------------------------------
            fbargs = [params, recipe, mprops['HEADER'], fiber,
                      eprops['E2DS']]
            fbkwargs = dict(database=calibdbm)
            fbprops = flat_blaze.get_blaze(*fbargs, **fbkwargs)
            # ----------------------------------------------------------------
            # Leak correction: remove reference-fiber contamination
            # ----------------------------------------------------------------
            lkargs = [params, recipe, eprops['E2DS'],
                      ref_e2ds, infile, fiber]
            lkkwargs = dict(database=calibdbm)
            lkout = leak.correct_spectra_leak(*lkargs, **lkkwargs)
            corrected_spectrum, leakcorr, leak_props = lkout
            # store corrected spectrum and leak diagnostics in eprops
            eprops['E2DS'] = corrected_spectrum
            eprops['E2DSFF'] = corrected_spectrum
            eprops['LEAKCORR'] = leakcorr
            for key, val in leak_props.items():
                eprops[key] = val
            # ----------------------------------------------------------------
            # Thermal correction (handled internally for quicklook/flat)
            # ----------------------------------------------------------------
            thargs = [params, recipe, mprops['HEADER'],
                      mprops['CALIB_PROPS'], eprops['E2DS'], fiber]
            thkwargs = dict(database=calibdbm)
            thout = thermal.correct_spectrum_thermal(*thargs, **thkwargs)
            thermal_spectrum, thermal_props = thout
            eprops['E2DS'] = thermal_spectrum
            eprops['E2DSFF'] = thermal_spectrum
            for key, val in thermal_props.items():
                eprops[key] = val
            # ----------------------------------------------------------------
            # S1D: resampled 1D spectrum on wavelength and velocity grids
            # e2ds_to_s1d returns None for quicklook, flat, or missing wave.
            # ----------------------------------------------------------------
            model_blaze = fbprops['BLAZE']
            s1args = [wavemap, eprops['E2DS'], model_blaze]
            s1kwargs = dict(fiber=fiber, s1dkind='SPECTRA',
                            e2dserr=eprops['E2DS_ERROR'])
            swprops = extract.e2ds_to_s1d(params, recipe, *s1args,
                                           wgrid='wave', **s1kwargs)
            svprops = extract.e2ds_to_s1d(params, recipe, *s1args,
                                           wgrid='velocity', **s1kwargs)
            # ----------------------------------------------------------------
            # Pixel-to-pixel scatter (returns None when wavemap is None)
            # ----------------------------------------------------------------
            eprops['MP2P_E2DS'] = extract.measure_p2p_scat(
                params, wavemap, eprops['E2DS'])
            eprops['MP2P_E2DSFF'] = extract.measure_p2p_scat(
                params, wavemap, eprops['E2DSFF'])
            eprops.set_sources(['MP2P_E2DS', 'MP2P_E2DSFF'], mainname)
            # ----------------------------------------------------------------
            # Plots
            # ----------------------------------------------------------------
            sorder = params['CAL.EXT.PLOT_ORDER']
            recipe.plot('FLAT_ORDER_FIT_EDGES1', params=params,
                        image1=mprops['IMAGE'],
                        image2=mprops['IMAGE_STRAIGHT'],
                        order=None, coeffs1=lcoeffs, coeffs2=lcoeffs2,
                        fiber=fiber)
            recipe.plot('FLAT_ORDER_FIT_EDGES2', params=params,
                        image1=mprops['IMAGE'],
                        image2=mprops['IMAGE_STRAIGHT'],
                        order=sorder, coeffs1=lcoeffs, coeffs2=lcoeffs2,
                        fiber=fiber)
            if not quicklook:
                recipe.plot('EXTRACT_SPECTRAL_ORDER1', order=None,
                            eprops=eprops, wave=wprops['WAVEMAP'],
                            fiber=fiber)
                recipe.plot('EXTRACT_SPECTRAL_ORDER2', order=sorder,
                            eprops=eprops, wave=wprops['WAVEMAP'],
                            fiber=fiber)
                if svprops is not None:
                    recipe.plot('EXTRACT_S1D', params=params, props=svprops,
                                fiber=fiber, kind='E2DSFF')
            # ----------------------------------------------------------------
            # Quality control
            # ----------------------------------------------------------------
            qc_params, passed = extract.qc_extraction(
                params, eprops,
                spectra=mprops['MODEL_PROPS']['SPECTRA'][fiber])
            log2.add_qc(qc_params, passed)
            # ----------------------------------------------------------------
            # Write extraction files
            # ----------------------------------------------------------------
            WLOG(params, '',
                 'Fiber {0}: writing extraction '
                 'files'.format(fiber))
            if quicklook:
                wqlargs = [params, recipe, infile, rawfiles, combine,
                           fiber, mprops['CALIB_PROPS'], lprops, eprops,
                           sprops, fbprops, qc_params]
                wqlout = extract.write_extraction_files_ql(*wqlargs)
                e2dsfile, e2dsfffile = wqlout
            else:
                wfargs = [params, recipe, infile, rawfiles, combine,
                          fiber, mprops['CALIB_PROPS'], lprops, wprops,
                          eprops, bprops, swprops, svprops,
                          sprops, fbprops, qc_params]
                wfout = extract.write_extraction_files(*wfargs)
                e2dsfile, e2dsfffile = wfout
            # ----------------------------------------------------------------
            # Write flat-response file and register in calibDB
            # (flat extractions only)
            # ----------------------------------------------------------------
            if extract_type == 'flat':
                resp_data = flat_response.get(fiber)
                if resp_data is not None:
                    resp_file = flat_blaze.write_flat_response(
                        params, recipe, infile, resp_data, fiber)
                    # add to calibDB so get_flat_response can retrieve it
                    if params['INPUTS']['DATABASE']:
                        calibdbm.add_calib_file(resp_file)
            # ----------------------------------------------------------------
            # FP reference lines (ref_fplines returns None for quicklook/flat)
            # ----------------------------------------------------------------
            rfargs = [e2dsfile, wavemap, fiber,
                      wprops.get('CAVITY', None)]
            rfpl = extract.ref_fplines(params, recipe, *rfargs,
                                       database=calibdbm)
            if rfpl is not None:
                rfwargs = [rfpl, e2dsfile, e2dsfile,
                           fiber, 'EXT_FPLINES']
                wave.write_fplines(params, recipe, *rfwargs)
                log2.update_flags(EXP_FPLINE=True)
            else:
                log2.update_flags(EXP_FPLINE=False)
            # ----------------------------------------------------------------
            # Register output files for downstream use (e.g. wave recipe)
            # ----------------------------------------------------------------
            if not quicklook:
                for key, efile in zip(['E2DS', 'E2DSFF'],
                                      [e2dsfile, e2dsfffile]):
                    outkey = '{0}_{1}'.format(key, fiber)
                    e2dsoutputs[outkey] = efile.completecopy(efile)
            # ----------------------------------------------------------------
            # Summary plots
            # ----------------------------------------------------------------
            if not quicklook:
                sorder = params['CAL.EXT.PLOT_ORDER']
                recipe.plot('SUM_FLAT_ORDER_FIT_EDGES', params=params,
                            image1=mprops['IMAGE'],
                            image2=mprops['IMAGE_STRAIGHT'],
                            order=sorder, coeffs1=lcoeffs, coeffs2=lcoeffs2,
                            fiber=fiber)
                recipe.plot('SUM_EXTRACT_SP_ORDER', order=sorder,
                            wave=wprops['WAVEMAP'], eprops=eprops,
                            fiber=fiber)
                if svprops is not None:
                    recipe.plot('SUM_EXTRACT_S1D', params=params,
                                props=svprops, fiber=fiber)
                # SUM_FLAT_RESPONSE_ORDER is emitted by
                # flat_blaze.compute_flat_response before the fiber loop
            # ----------------------------------------------------------------
            # Summary document (per fiber)
            # ----------------------------------------------------------------
            if not quicklook:
                extract.extract_summary(recipe, params, qc_params, e2dsfile,
                                        sprops, eprops, fiber)
            log2.end()
        # end of fiber loop
        # construct per-file summary document (outside fiber loop)
        if not quicklook:
            recipe.plot.summary_document(it)
        log1.end()
    # -------------------------------------------------------------------------
    # End of main code
    # -------------------------------------------------------------------------
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

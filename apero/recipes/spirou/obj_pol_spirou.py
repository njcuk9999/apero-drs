#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-25 at 16:44

@author: cook
"""
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.science.polar import gen_pol
from apero.science.polar import lsd

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_pol_spirou.py'
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
    Main function for obj_pol_spirou.py

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

    # TODO --------------------------------------------------------------------
    # TODO: Move to constants
    # TODO --------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # GENERAL POLAR SETTINGS
    # -------------------------------------------------------------------------
    # Define all possible fibers used for polarimetry
    params.set('POLAR_FIBERS', value='A,B', source=mainname)
    #  Define all possible stokes parameters
    params.set('POLAR_STOKES_PARAMS', value='V,Q,U', source=mainname)
    # Whether or not to correct for BERV shift before calculate polarimetry
    params.set('POLAR_BERV_CORRECT', value=True, source=mainname)
    # Whether or not to correct for SOURCE RV shift before calculate polarimetry
    params.set('POLAR_SOURCE_RV_CORRECT', value=False, source=mainname)
    #  Define the polarimetry method
    #    currently must be either:
    #         - Ratio
    #         - Difference
    params.set('POLAR_METHOD', value='Ratio', source=mainname)
    # Wheter or not to inerpolate flux values to correct for wavelength
    #   shifts between exposures
    params.set('POLAR_INTERPOLATE_FLUX', value=True, source=mainname)

    # Select stokes I continuum detection algorithm:
    #     'IRAF' or 'MOVING_MEDIAN'
    params.set('STOKESI_CONTINUUM_DETECTION_ALGORITHM',
               value='MOVING_MEDIAN', source=mainname)
    # Select stokes I continuum detection algorithm:
    #     'IRAF' or 'MOVING_MEDIAN'
    params.set('POLAR_CONTINUUM_DETECTION_ALGORITHM',
               value='MOVING_MEDIAN', source=mainname)
    # Normalize Stokes I (True or False)
    params.set('POLAR_NORMALIZE_STOKES_I', value=True, source=mainname)
    # Remove continuum polarization
    params.set('POLAR_REMOVE_CONTINUUM', value=True, source=mainname)
    # Apply polarimetric sigma-clip cleanning (Works better if continuum
    #     is removed)
    params.set('POLAR_CLEAN_BY_SIGMA_CLIPPING', value=True, source=mainname)
    # Define number of sigmas within which apply clipping
    params.set('POLAR_NSIGMA_CLIPPING', value=4, source=mainname)

    # -------------------------------------------------------------------------
    # POLAR 'MOVING_MEDIAN' ALGORITHM SETTINGS
    # -------------------------------------------------------------------------
    #  Define the polarimetry continuum bin size
    params.set('POLAR_CONT_BINSIZE', value=900, source=mainname)
    #  Define the polarimetry continuum overlap size
    params.set('POLAR_CONT_OVERLAP', value=200, source=mainname)
    #  Fit polynomial to continuum polarization?
    # If False it will use a cubic interpolation instead of polynomial fit
    params.set('POLAR_CONT_POLYNOMIAL_FIT', value=True, source=mainname)
    #  Define degree of polynomial to fit continuum polarization
    params.set('POLAR_CONT_DEG_POLYNOMIAL', value=3, source=mainname)
    # -------------------------------------------------------------------------
    # POLAR 'IRAF' ALGORITHM SETTINGS
    # -------------------------------------------------------------------------
    # function to fit to the stokes I continuum: must be 'polynomial' or
    #    'spline3'
    params.set('STOKESI_IRAF_CONT_FIT_FUNCTION', value="polynomial",
               source=mainname)
    # function to fit to the polar continuum: must be 'polynomial' or 'spline3'
    params.set('POLAR_IRAF_CONT_FIT_FUNCTION', value="polynomial",
               source=mainname)
    # polar continuum fit function order: 'polynomial': degree or 'spline3':
    #    number of knots
    params.set('STOKESI_IRAF_CONT_FUNCTION_ORDER', value=5, source=mainname)
    # polar continuum fit function order: 'polynomial': degree or 'spline3':
    #    number of knots
    params.set('POLAR_IRAF_CONT_FUNCTION_ORDER', value=3, source=mainname)
    # -------------------------------------------------------------------------
    # POLAR LSD SETTINGS
    # -------------------------------------------------------------------------
    #  Define the spectral lsd mask directory for lsd polar calculations
    params.set('POLAR_LSD_DIR', value='lsd', source=mainname)
    #  Define the file regular expression key to lsd mask files
    #  for "marcs_t3000g50_all" this should be:
    #     - filekey = 'marcs_t*g
    #  for "t4000_g4.0_m0.00" it should be:
    #     - filekey = 't*_g'
    params.set('POLAR_LSD_FILE_KEY', value='marcs_t*g50_all', source=mainname)
    #  Define minimum lande of lines to be used in the LSD analyis
    params.set('POLAR_LSD_MIN_LANDE', value=0.0, source=mainname)
    #  Define maximum lande of lines to be used in the LSD analyis
    params.set('POLAR_LSD_MAX_LANDE', value=10.0, source=mainname)
    #  If mask lines are in air-wavelength then they will have to be
    #     converted from air to vacuum
    params.set('POLAR_LSD_CCFLINES_AIR_WAVE', value=False, source=mainname)
    #  Define minimum line depth to be used in the LSD analyis
    params.set('POLAR_LSD_MIN_LINEDEPTH', value=0.005, source=mainname)
    #  Define initial velocity (km/s) for output LSD profile
    params.set('POLAR_LSD_V0', value=-150.0, source=mainname)
    #  Define final velocity (km/s) for output LSD profile
    params.set('POLAR_LSD_VF', value=150.0, source=mainname)
    #  Define number of points for output LSD profile
    params.set('POLAR_LSD_NP', value=151, source=mainname)
    # Renormalize data before LSD analysis
    params.set('POLAR_LSD_NORMALIZE', value=False, source=mainname)
    #  Remove edges of LSD profile
    params.set('POLAR_LSD_REMOVE_EDGES', value=True, source=mainname)
    #  Define the guess at the resolving power for lsd profile fit
    params.set('POLAR_LSD_RES_POWER_GUESS', value=50000.0, source=mainname)

    # TODO --------------------------------------------------------------------
    # TODO: End of constants
    # TODO --------------------------------------------------------------------

    # set polar exposures
    inputs = gen_pol.set_polar_exposures(params)
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # get constants from params
    remove_continuum = params['POLAR_REMOVE_CONTINUUM']
    normalize_stokesi = params['POLAR_NORMALIZE_STOKES_I']
    clean_by_sigmaclip = params['POLAR_CLEAN_BY_SIGMA_CLIPPING']
    clean_nsig = params['POLAR_NSIGMA_CLIPPING']
    do_lsd_analysis = params['INPUTS']['LSD']
    drs_header = params['DRS_HEADER']
    # -------------------------------------------------------------------------
    # part 1: deal with input files and load data
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', 'Part 1: loading input data')
    WLOG(params, 'info', drs_header)
    # TODO: decide here (or inside) which products to load from
    # TODO:   - add e.fits + t.fits + v.fits instead of reduced products
    pprops = gen_pol.apero_load_data(params, recipe, inputs)
    # calculate polar times
    pprops = gen_pol.calculate_polar_times(pprops)

    # -------------------------------------------------------------------------
    # part 2: run polarimetry analysis
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', 'Part 2: Run polar analysis')
    WLOG(params, 'info', drs_header)
    pprops = gen_pol.calculate_polarimetry(params, pprops)
    pprops = gen_pol.calculate_stokes_i(params, pprops)

    # -------------------------------------------------------------------------
    # part 3: run analysis for continuum detection and removal
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', 'Part 3: Run continuum analysis')
    WLOG(params, 'info', drs_header)
    # calculate the continuum
    pprops = gen_pol.calculate_continuum(params, recipe, pprops)
    # if we are removing polar continuum
    if remove_continuum:
        pprops = gen_pol.remove_continuum_polarization(pprops)
    # if we are
    if normalize_stokesi:
        pprops = gen_pol.normalize_stokes_i(pprops)

    # ----------------------------------------------------------------------
    # Apply sigma-clipping
    # ----------------------------------------------------------------------
    if clean_by_sigmaclip:
        # run the cleaning
        pprops = gen_pol.clean_polarimetry_data(pprops, sigclip=True,
                                                nsig=clean_nsig, overwrite=True)

    # -------------------------------------------------------------------------
    # part4: run lsd analysis
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', 'Part 4: Run LSD Analysis')
    WLOG(params, 'info', drs_header)
    # run analysis
    if do_lsd_analysis:
        # run LSD analysis
        pprops = lsd.lsd_analysis_wrapper(params, pprops)

    # -------------------------------------------------------------------------
    # part5: quality control
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', 'Part 5: Quality Control')
    WLOG(params, 'info', drs_header)
    # add quality control (currently empty)
    qc_params, passed = gen_pol.quality_control(params)

    # -------------------------------------------------------------------------
    # part6: Make S1D files
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', 'Part 6: Making S1D tables')
    WLOG(params, 'info', drs_header)
    s1dprops = gen_pol.make_s1d(params, recipe, pprops)

    # -------------------------------------------------------------------------
    # part6: writing files
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', 'Part 7: Writing files')
    WLOG(params, 'info', drs_header)

    # write polar files
    wout = gen_pol.write_files(params, recipe, pprops, inputs, s1dprops,
                               qc_params)
    polfile, cfile, ctable = wout

    # TODO:   p.fits should be done in the output post processing script

    # save LSD data to fits
    #if do_lsd_analysis:
    #    lsd.write_files(params, recipe, pprops, inputs, qc_params)

    # -------------------------------------------------------------------------
    # part7: plots
    # -------------------------------------------------------------------------
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', 'Part 8: plots')
    WLOG(params, 'info', drs_header)
    # -------------------------------------------------------------------------
    # Debug plots:
    # -------------------------------------------------------------------------
    # plot continuum plots
    recipe.plot('POLAR_CONTINUUM', props=pprops)
    # plot polarimetry results
    recipe.plot('POLAR_RESULTS', props=pprops)
    # plot total flux (Stokes I)
    recipe.plot('POLAR_STOKES_I', props=pprops)
    # plot LSD analysis plot only if we did lsd analysis
    if do_lsd_analysis:
        # plot LSD analysis
        recipe.plot('POLAR_LSD', props=pprops)
    # -------------------------------------------------------------------------
    # Summary plots
    # -------------------------------------------------------------------------
    # TODO: Question: which plots should be summary plots?

    # write summary plot to disk
    # TODO: Add summary function
    # gen_pol.summary(params, recipe, qc_params, pprops)

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

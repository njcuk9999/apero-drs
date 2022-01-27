#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-25 at 16:44

@author: cook
"""
from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.science.polar import gen_pol
from apero.science.polar import lsd

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_pol_spirou.py'
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
    Main function for apero_pol_spirou.py

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
    # log message: Part 1: loading input data
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', textentry('40-021-00012'))
    WLOG(params, 'info', drs_header)
    # TODO: decide here (or inside) which products to load from
    # TODO:   - add e.fits + t.fits + v.fits instead of reduced products
    pprops = gen_pol.apero_load_data(params, recipe, inputs)
    # calculate polar times
    pprops = gen_pol.calculate_polar_times(pprops)

    # -------------------------------------------------------------------------
    # part 2: run polarimetry analysis
    # -------------------------------------------------------------------------
    # log progress: Part 2: Run polar analysis
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', textentry('40-021-00013'))
    WLOG(params, 'info', drs_header)
    pprops = gen_pol.calculate_polarimetry(params, pprops)
    pprops = gen_pol.calculate_stokes_i(params, pprops)

    # -------------------------------------------------------------------------
    # part 3: run analysis for continuum detection and removal
    # -------------------------------------------------------------------------
    # log progress: Part 3: Run continuum analysis
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', textentry('40-021-00014'))
    WLOG(params, 'info', drs_header)
    # calculate the continuum
    pprops = gen_pol.calculate_continuum(params, recipe, pprops)
    # if we are removing polar continuum
    if remove_continuum:
        pprops = gen_pol.remove_continuum_polarization(params, pprops)
    # if we are
    if normalize_stokesi:
        pprops = gen_pol.normalize_stokes_i(params, pprops)

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
    # log progress: Part 4: Run LSD Analysis
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', textentry('40-021-00015'))
    WLOG(params, 'info', drs_header)
    # run analysis
    if do_lsd_analysis:
        # run LSD analysis
        pprops = lsd.lsd_analysis_wrapper(params, pprops)

    # -------------------------------------------------------------------------
    # part5: quality control
    # -------------------------------------------------------------------------
    # log progress: Part 5: Quality Control
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', textentry('40-021-00016'))
    WLOG(params, 'info', drs_header)
    # add quality control (currently empty)
    qc_params, passed = gen_pol.quality_control(params)

    # -------------------------------------------------------------------------
    # part6: Make S1D files
    # -------------------------------------------------------------------------
    # log progress: Part 6: Making S1D tables
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', textentry('40-021-00017'))
    WLOG(params, 'info', drs_header)
    s1dprops = gen_pol.make_s1d(params, recipe, pprops)

    # -------------------------------------------------------------------------
    # part6: writing files
    # -------------------------------------------------------------------------
    # log progress: Part 7: Writing files
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', textentry('40-021-00018'))
    WLOG(params, 'info', drs_header)

    # write polar files
    wout = gen_pol.write_files(params, recipe, pprops, inputs, s1dprops,
                               qc_params)
    polfile, cfile, ctable = wout

    # save LSD data to fits
    if do_lsd_analysis:
       lsd.write_files(params, recipe, pprops, polfile, cfile, ctable)

    # -------------------------------------------------------------------------
    # part7: plots
    # -------------------------------------------------------------------------
    # log progress: Part 8: plots
    WLOG(params, 'info', drs_header)
    WLOG(params, 'info', textentry('40-021-00019'))
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

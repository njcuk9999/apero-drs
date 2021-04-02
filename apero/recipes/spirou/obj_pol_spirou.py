#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-25 at 16:44

@author: cook
"""
from apero.base import base
from apero import lang
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

    # set polar exposures
    inputs = gen_pol.set_polar_exposures(params)

    # -------------------------------------------------------------------------
    # part1: deal with input files and load data
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', 'Part 1: loading input data')
    polardict = gen_pol.apero_load_data(params, inputs)

    # -------------------------------------------------------------------------
    # part2: run polarimetry analysis
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', 'Part 2: Run polar analysis')
    pprops = gen_pol.calculate_polarimetry(params, pprops)
    pprops = gen_pol.calculate_stokes_i(params, pprops)

    # -------------------------------------------------------------------------
    # part3: run analysis for continuum detection and removal
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', 'Part 3: Run continuum analysis')

    pprops = gen_pol.calculate_continuum(params, pprops)

    if params['POLAR_REMOVE_CONTINUUM']:
        pprops = gen_pol.remove_continuum_polarization(pprops)

    if params['POLAR_NORMALIZE_STOKES_I']:
        pprops = gen_pol.normalize_stokes_i(pprops)

    # ----------------------------------------------------------------------
    # Apply sigma-clipping
    # ----------------------------------------------------------------------
    if params['POLAR_CLEAN_BY_SIGMA_CLIPPING'] :
        # get the sigma criteria
        nsig = params['POLAR_NSIGMA_CLIPPING']
        # run the cleaning
        pprops = gen_pol.clean_polarimetry_data(pprops, sigclip=True, nsig=nsig,
                                                overwrite=True)

    # -------------------------------------------------------------------------
    # part4: run lsd analysis
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', 'Part 4: Run LSD Analysis')

    if params['INPUTS']['LSD']:

        # Load LSD mask
        if params['INPUTS']['LSDMASK'] != 'None':
            # set lsd mask file from input
            lsd_mask_file = params['INPUTS']['LSDMASK']
            # TODO: move text to language database
            msg = 'Selected input LSD mask: '
            margs = [lsd_mask_file]
            WLOG(params, 'info', msg.format(*margs))
        else:
            # select an lsd mask file from repositories
            lsd_mask_file = lsd.select_lsd_mask(params, pprops)
            # TODO: move text to language database
            msg = 'Selected repository LSD mask: '
            margs = [lsd_mask_file]
            WLOG(params, 'info', msg.format(*margs))
        # run LSD analysis
        pprops = lsd.lsd_analysis_wrapper(params, pprops)

        # save LSD data to fits
        if params['INPUTS']['OUTPUT_LSD'] != 'None':
            # get output filename
            output_lsd = params['INPUTS']['OUTPUT_LSD']

            # TODO: move text to language database
            msg = 'Saving LSD analysis to file: {0}'
            margs = [params['INPUTS']['OUTPUT_LSD']]
            WLOG(params, 'info', msg.format(*margs))
            lsd.save_lsd_fits(output_lsd, pprops, params)

    # -------------------------------------------------------------------------
    # part5: quality control
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', 'Part 5: Quality Control')

    # -------------------------------------------------------------------------
    # part6: writing files
    # -------------------------------------------------------------------------
    # TODO: move text to language database
    WLOG(params, 'info', 'Part 6: Writing files')

    if params['INPUTS']['OUTPUT']:
        gen_pol.apero_create_pol_product(params['INPUTS']['OUTPUT'], params,
                                         pprops)

    # -------------------------------------------------------------------------
    # part7: summary plots
    # -------------------------------------------------------------------------
    WLOG(params, 'info', 'Part 7: Summary plots')

    # plot continuum plots
    recipe.plot.polar_continuum_plot(params, pprops)
    # plot polarimetry results
    recipe.plot.polar_result_plot(params, pprops)
    # plot total flux (Stokes I)
    recipe.plot.polar_stokes_i_plot(params, pprops)

    if params['INPUTS']['LSD'] :
        # plot LSD analysis
        recipe.plot.polar_lsd_plot(params, pprops)

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

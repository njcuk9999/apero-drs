#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2020-05-13

@author: cook
"""
from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.science.polar import general_new

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pol_spirou_new.py'
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
def main(directory=None, exp1=None, exp2=None, exp3=None, exp4=None, **kwargs):
    """
    Main function for pol_spirou.py

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
    fkwargs = dict(directory=directory, exp1=exp1, exp2=exp2, exp3=exp3,
                   exp4=exp4, **kwargs)
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
    infiles = []
    infiles += params['INPUTS']['EXP1'][1]
    infiles += params['INPUTS']['EXP2'][1]
    infiles += params['INPUTS']['EXP3'][1]
    infiles += params['INPUTS']['EXP4'][1]
    # get list of filenames (for output)
    rawfiles = []
    for infile in infiles:
        rawfiles.append(infile.basename)

    # TODO: ------------------------------------------------------------------
    # TODO: Add these to constants file
    # Wheter or not to correct for BERV shift before calculate polarimetry
    params.set('POLAR_BERV_CORRECT', value=True, source=mainname)
    # Whether or not to use telluric subctracted flux
    params.set('POLAR_TELLU_CORRECT', value=True, source=mainname)
    # Wheter or not to correct for SOURCE RV shift before calculate polarimetry
    params.set('POLAR_SOURCERV_CORRECT', value=True, source=mainname)
    # Define the fiber used as the main fiber
    params.set('POLAR_MASTER_FIBER', value='AB', source=mainname)
    # Define the file definition describing the CCF FILE used to get the RV
    params.set('POLAR_CCF_FILE', value='CCF_RV', source=mainname)
    # Define the ccf mask used for the RV
    params.set('POLAR_CCF_MASK', value='masque_sept18_andres_trans50.mas',
               source=mainname)
    # Define the file definition describing the telluric object file
    params.set('POLAR_TCORR_FILE', value='TELLU_OBJ', source=mainname)
    # Define the file definition describing the telluric recon file
    params.set('POLAR_RECON_FILE', value='TELLU_RECON', source=mainname)
    #  Define the polarimetry continuum bin size for the stokes
    #      continuum correction
    params.set('POLAR_SCONT_BINSIZE', value=900, source=mainname)
    #  Define the polarimetry continuum overlap size for the stokes
    #      continuum correction
    params.set('POLAR_SCONT_OVERLAP', value=200, source=mainname)
    #  Define the polarimetry continuum bin size for the polar correction
    params.set('POLAR_PCONT_BINSIZE', value=900, source=mainname)
    #  Define the polarimetry continuum overlap size for the polar correction
    params.set('POLAR_PCONT_OVERLAP', value=200, source=mainname)
    # Whether or not to inerpolate flux values to correct for wavelength
    #     shifts between exposures
    params.set('POLAR_INTERPOLATE_FLUX', value=True, source=mainname)
    # Select stokes I continuum detection algorithm:
    #      'IRAF' or 'MOVING_MEDIAN'
    params.set('POLAR_STOKESI_CONT_MODE', value='MOVING_MEDIAN',
               source=mainname)
    # Select polarization continuum detection algorithm:
    #      'IRAF' or 'MOVING_MEDIAN'
    params.set('POLAR_POLAR_CONT_MODE', value='MOVING_MEDIAN',
               source=mainname)
    # moving median mode for polar correction
    # define the continuum window size for the stokes i continuum correction
    params.set('POLAR_SCONT_WINDOW', value=6, source=mainname)
    # define the continuum mode for the stokes i continuum correction
    params.set('POLAR_SCONT_MODE', value='max', source=mainname)
    # define whether to use a linear fit for the stokes i continuum correction
    params.set('POLAR_SCONT_LINFIT', value=True, source=mainname)

    # function to fit to the polar continuum: must be 'polynomial' or 'spline3'
    params.set('POLAR_SIRAF_FIT_FUNC', value='polynomial', source=mainname)
    # polar continuum fit function order: 'polynomial': degree or
    #     'spline3': number of knots
    params.set('POLAR_SIRAF_CONT_ORD', value=5, source=mainname)
    params.set('POLAR_SIRAF_NIT', value=5, source=mainname)
    params.set('POLAR_SIRAF_REJ_LOW', value=3.0, source=mainname)
    params.set('POLAR_SIRAF_REJ_HIGH', value=3.0, source=mainname)
    params.set('POLAR_SIRAF_GROW', value=1, source=mainname)
    params.set('POLAR_SIRAF_MED_FILT', value=0, source=mainname)
    params.set('POLAR_SIRAF_PER_LOW', value=0.0, source=mainname)
    params.set('POLAR_SIRAF_PER_HIGH', value=100.0, source=mainname)
    params.set('POLAR_SIRAF_MIN_PTS', value=10, source=mainname)
    # define the continuum mode for the polar continuum correction
    params.set('POLAR_PCONT_MODE', value='median', source=mainname)
    # define whether to use a polynomial fit for the polar continuum correction
    params.set('POLAR_PCONT_USE_POLYFIT', value=True, source=mainname)
    # define the polynomial fit degree for the polar continuum correction
    params.set('POLAR_PCONT_POLY_DEG', value=2, source=mainname)
    # function to fit to the polar continuum: must be 'polynomial' or 'spline3'
    params.set('POLAR_PIRAF_FIT_FUNC', value='polynomial', source=mainname)
    # polar continuum fit function order: 'polynomial': degree or 'spline3': number of knots
    params.set('POLAR_PIRAF_CONT_ORD', value=3, source=mainname)
    params.set('POLAR_PIRAF_NIT', value=5, source=mainname)
    params.set('POLAR_PIRAF_REJ_LOW', value=3.0, source=mainname)
    params.set('POLAR_PIRAF_REJ_HIGH', value=3.0, source=mainname)
    params.set('POLAR_PIRAF_GROW', value=1, source=mainname)
    params.set('POLAR_PIRAF_MED_FILT', value=0, source=mainname)
    params.set('POLAR_PIRAF_PER_LOW', value=0.0, source=mainname)
    params.set('POLAR_PIRAF_PER_HIGH', value=100.0, source=mainname)
    params.set('POLAR_PIRAF_MIN_PTS', value=10, source=mainname)
    # define whether to remove continuum polarization
    params.set('POLAR_REMOVE_CONTINUUM', value=True, source=mainname)
    # define whether to normalize Stokes I
    params.set('POLAR_NORMALIZE_STOKES_I', value=True, source=mainname)
    # Apply polarimetric sigma-clip cleanning
    #    (Works better if continuum is removed)
    params.set('POLAR_CLEAN_BY_SIGMA_CLIPPING', value=True, source=mainname)
    # Define whether to sigma clip in sigma cliping function
    params.set('POLAR_CLEAN_SIGCLIP', value=True, source=mainname)
    # Define number of sigmas within which apply clipping
    params.set('POLAR_NSIGMA_CLIPPING', value=4, source=mainname)
    # Define whether to overwrite input data with sigma clipping data
    params.set('POLAR_SIGCLIP_OVERWRITE', value=True, source=mainname)
    # Define minimum lande of lines to be used in the LSD analyis
    params.set('POLAR_LSD_MIN_LANDE', value=0.0)
    # Define maximum lande of lines to be used in the LSD analyis
    params.set('POLAR_LSD_MAX_LANDE', value=10.0)

    # TODO: ------------------------------------------------------------------

    # set the location (must do before any plotting starts)
    recipe.plot.set_location()
    # ----------------------------------------------------------------------
    # Validate polar files
    # ----------------------------------------------------------------------
    pobjects, props = general_new.validate_polar_files(params, recipe, infiles)

    # ----------------------------------------------------------------------
    # Polarimetry computation
    # ----------------------------------------------------------------------
    pprops = general_new.calculate_polarimetry(params, pobjects, props)

    # ----------------------------------------------------------------------
    # Stokes I computation
    # ----------------------------------------------------------------------
    pprops = general_new.calculate_stokes_i(params, pobjects, pprops)

    # ----------------------------------------------------------------------
    # Calculate continuum (for plotting)
    # ----------------------------------------------------------------------
    pprops = general_new.calculate_continuum(params, pprops)

    # ----------------------------------------------------------------------
    # Remove continuum polarization
    # ----------------------------------------------------------------------
    pprops = general_new.remove_continuum_polarization(params, pprops)

    # ----------------------------------------------------------------------
    # Normalize Stokes I
    # ----------------------------------------------------------------------
    pprops = general_new.normalize_stokes_i(params, pprops)

    # ----------------------------------------------------------------------
    # Apply sigma-clipping
    # ----------------------------------------------------------------------
    if params['POLAR_CLEAN_BY_SIGMA_CLIPPING']:

        pprops = general_new.clean_polar_data(params, pprops)

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    # TODO: This is unfinished
    # TODO: rememebr plot from fit_continuum (Line 2139 of eder spirouPoalr)

    # ----------------------------------------------------------------------
    # LSD Analysis
    # ----------------------------------------------------------------------

    # TODO: This is unfinished

    # ----------------------------------------------------------------------
    # Write files
    # ----------------------------------------------------------------------

    # TODO: This is unfinished

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

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
from terrapipe.science.calib import wave
from terrapipe.science import polar


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_pol_spirou.py'
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
    # set the location (must do before any plotting starts)
    recipe.plot.set_location()
    # ----------------------------------------------------------------------
    # Validate polar files
    # ----------------------------------------------------------------------
    pobjects, props = polar.validate_polar_files(params, infiles)
    # get first file
    pobj = pobjects['A_1']
    # ----------------------------------------------------------------------
    # load wavelength solution for this fiber
    # ----------------------------------------------------------------------
    wprops = wave.get_wavesolution(params, recipe, fiber=pobj.fiber,
                                   infile=pobj.infile)
    # ----------------------------------------------------------------------
    # polarimetry computation
    # ----------------------------------------------------------------------
    pprops = polar.calculate_polarimetry(params, pobjects, props)

    # ----------------------------------------------------------------------
    # Stokes I computation
    # ----------------------------------------------------------------------
    pprops = polar.calculate_stokes_i(params, pobjects, pprops)

    # ----------------------------------------------------------------------
    # Calculate continuum (for plotting)
    # ----------------------------------------------------------------------
    pprops = polar.calculate_continuum(params, pprops, wprops)

    # ---------------------------------------------------------------------
    # LSD Analysis
    # ---------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    qc_params, passed = polar.quality_control(params)

    # ------------------------------------------------------------------
    # Store polarimetry in files
    # ------------------------------------------------------------------




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

# =============================================================================
# End of code
# =============================================================================

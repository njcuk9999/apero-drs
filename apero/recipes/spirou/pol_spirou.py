#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2019-09-05 at 14:58

@author: cook
"""
import numpy as np

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_database
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science import extract
from apero.science import polar


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pol_spirou.py'
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
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict


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
    fkwargs = dict(directory=directory, files=files, **kwargs)
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

    # TODO: these are added in as they were removed for pol_spirou_new
    params.set('POLAR_CONT_BINSIZE ', value=1000, source=__NAME__)
    params.set('POLAR_CONT_OVERLAP', value=0, source=__NAME__)

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
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    # set the location (must do before any plotting starts)
    recipe.plot.set_location()
    # ----------------------------------------------------------------------
    # Validate polar files
    # ----------------------------------------------------------------------
    pobjects, props = polar.validate_polar_files(params, infiles)
    # get first file
    pobj = pobjects['A_1']
    # ----------------------------------------------------------------------
    # generate timing statistics
    polstats = polar.generate_statistics(params, pobjects)
    # ----------------------------------------------------------------------
    # load wavelength solution for this fiber
    # ----------------------------------------------------------------------
    wprops = wave.get_wavesolution(params, recipe, fiber=pobj.fiber,
                                   infile=pobj.infile, database=calibdbm)
    # ----------------------------------------------------------------------
    # load the blaze file for this fiber
    # ----------------------------------------------------------------------
    blaze_file, blaze = flat_blaze.get_blaze(params, fiber=pobj.fiber,
                                             header=pobj.infile.get_header())
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
    try:
        lprops = polar.lsd_analysis_wrapper(params, pobjects, pprops, wprops)
    except np.linalg.LinAlgError:
        # TODO: Hack to avoid error - if presistent should deal with it better
        #  inside lsd_analysis_wrapper
        lprops = dict(LSD_ANALYSIS=False)

    # ----------------------------------------------------------------------
    # Create 1d soectra (s1d) of all products [pol, null1, null2, stokesi]
    # ----------------------------------------------------------------------
    # store s1d props
    s1dprops = dict()
    # loop around the s1d files
    for s1dfile in ['POL', 'NULL1', 'NULL2', 'STOKESI']:
        # loop around s1d grids
        for grid in ['wave', 'velocity']:
            # compute s1d
            sargs = [wprops['WAVEMAP'], pprops[s1dfile], blaze]
            sprops = extract.e2ds_to_s1d(params, recipe, *sargs, wgrid=grid,
                                         kind=s1dfile)
            # store s1d
            skey = 'S1D{0}_{1}'.format(grid[0].upper(), s1dfile)
            s1dprops[skey] = sprops
            # ------------------------------------------------------------------
            # plot only for wave grid
            if grid == 'wave':
                # plot the debug plot
                recipe.plot('EXTRACT_S1D', params=params, props=sprops,
                            fiber=None, kind=s1dfile)
                # plot the summary plot
                recipe.plot('SUM_EXTRACT_S1D', params=params, props=sprops,
                            fiber=None, kind=s1dfile)

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    # plot continuum plots
    recipe.plot('POLAR_CONTINUUM', props=pprops)
    # plot polarimetry results
    recipe.plot('POLAR_RESULTS', props=pprops)
    # plot total flux (Stokes I)
    recipe.plot('POLAR_STOKES_I', props=pprops)
    # plot LSD analysis
    if lprops['LSD_ANALYSIS']:
        recipe.plot('POLAR_LSD', pprops=pprops, lprops=lprops)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    qc_params, passed = polar.quality_control(params)
    # update recipe log
    recipe.log.add_qc(params, qc_params, passed)

    # ------------------------------------------------------------------
    # Store polarimetry in files
    # ------------------------------------------------------------------
    polar.write_files(params, recipe, pobjects, rawfiles, pprops, lprops,
                      wprops, polstats, s1dprops, qc_params)

    # ------------------------------------------------------------------
    # Add summary pdf
    # ------------------------------------------------------------------
    # construct summary (outside fiber loop)
    recipe.plot.summary_document(0, qc_params)

    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    recipe.log.end(params)

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

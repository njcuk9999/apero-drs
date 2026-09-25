#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_flat_spirou.py [obs dir] [files]

APERO flat and blaze finding recipe for SPIROU

Created on 2019-07-05 at 16:45

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

from aperocore.base import base
from aperocore.constants import param_functions
import apero as apero_pkg
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.io import drs_image
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science.extract import other as extractother

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_flat_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the text types
textentry = drs_lang.textentry
# name of the extraction recipe called as a sub-recipe
EXTRACT_NAME = 'apero_extract_spirou.py'


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
    Main function for apero_flat_spirou.py

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
    # check qc
    if 'files' in params['DATA_DICT']:
        infiles = params['DATA_DICT']['files']
    else:
        # get files
        infiles = params['INPUTS']['FILES'][1]
    # check the quality control from input files
    infiles = drs_file.check_input_qc(params, infiles, 'files')
    # loc is run twice we need to check that all input files can be used
    #  together and we are not mixing both types
    infiles = drs_file.check_input_dprtypes(params, recipe, infiles)
    # get list of filenames (for output)
    rawfiles = []
    for infile in infiles:
        rawfiles.append(infile.basename)
    # deal with input data from function
    if 'files' in params['DATA_DICT']:
        rawfiles = params['DATA_DICT']['rawfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['IMAGE.COMBINE_INPUT']:
        # get combined file
        cond = drs_file.combine(params, recipe, infiles, math='mean',
                                same_type=False, test_similarity=False)
        infiles = [cond[0]]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params, recipe.shortname)
    calibdbm.load_db()
    # get the fiber types from a list parameter
    fiber_types = drs_image.get_fiber_types(params)
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
        # get this iteration's file
        infile = infiles[it]

        # ------------------------------------------------------------------
        # Get the flat output e2ds filename and extract/read file
        # ------------------------------------------------------------------
        # --forceext=True forces re-extraction even if output exists,
        # taking precedence over the CAL.FLAT.ALWAYS_EXTRACT constant
        force_ext = params['INPUTS'].get('FORCEEXT',
                                         params['CAL.FLAT.ALWAYS_EXTRACT'])
        eargs = [params, recipe, EXTRACT_NAME, infile, log1]
        # returns {'e2ds': {fiber: DrsFitsFile}, 'flat_response': {fiber: ...}}
        flat_outputs = extractother.extract_flat_files(*eargs,
                                                       always_extract=force_ext)
        # per-fiber extracted spectra
        flat_files = flat_outputs['e2ds']
        # per-fiber flat-response profiles (used by the blaze step below)
        flat_response_files = flat_outputs['flat_response']

        # ------------------------------------------------------------------
        # Load wave solution for each fiber (use ref wave as default)
        # ------------------------------------------------------------------
        WLOG(params, '',
             'Loading reference wave solutions for fibers: '
             '{0}'.format(', '.join(fiber_types)))
        wave_maps = dict()
        for fiber in fiber_types:
            # load the reference wave solution for this fiber
            wkwargs = dict(fiber=fiber, infile=infile, ref=True,
                           database=calibdbm)
            wprops = wave.get_wavesolution(params, recipe, **wkwargs)
            wave_maps[fiber] = wprops['WAVEMAP']
        WLOG(params, '', 'Wave solutions loaded')

        # ------------------------------------------------------------------
        # Fit physical blaze model and compute flat per fiber
        # ------------------------------------------------------------------
        bargs = [params, recipe, flat_response_files, flat_files,
                 wave_maps, fiber_types]
        eprops_all = flat_blaze.make_blaze(*bargs)

        # ------------------------------------------------------------------
        # Fiber loop
        # ------------------------------------------------------------------
        # loop around fiber types
        for fiber in fiber_types:
            # ------------------------------------------------------------------
            # add level to recipe log
            log2 = log1.add_level(params, 'fiber', fiber)
            # retrieve eprops built by make_blaze for this fiber
            eprops = eprops_all[fiber]
            WLOG(params, '',
                 'Fiber {0}: blaze model fit — '
                 'rms={1:.2%}'.format(fiber, eprops['BLAZE_FIT_RMS']))
            # --------------------------------------------------------------
            # Plots
            # --------------------------------------------------------------
            sorder = params['CAL.FLAT.PLOT_ORDER']
            # plot (in a loop) the fitted blaze and calculated flat with
            # the e2ds image
            recipe.plot('FLAT_BLAZE_ORDER1', order=None, eprops=eprops,
                        fiber=fiber)
            # plot for sorder the fitted blaze and calculated flat with
            # the e2ds image
            recipe.plot('FLAT_BLAZE_ORDER2', order=sorder, eprops=eprops,
                        fiber=fiber)
            # --------------------------------------------------------------
            # Quality control
            # --------------------------------------------------------------
            qc_params, passed = flat_blaze.flat_blaze_qc(params, recipe,
                                                          eprops, fiber)
            # update recipe log
            log2.add_qc(qc_params, passed)
            # --------------------------------------------------------------
            # write files
            # flat_files[fiber] carries full calibration provenance in
            # its header (shape, loco, wave) and is used as source_file
            # --------------------------------------------------------------
            WLOG(params, '',
                 'Fiber {0}: writing blaze and flat '
                 'calibration files'.format(fiber))
            wargs = [infile, eprops, fiber, rawfiles, combine,
                     flat_files[fiber], qc_params]
            outfiles = flat_blaze.flat_blaze_write(params, recipe, *wargs)
            blazefile, flatfile = outfiles

            # --------------------------------------------------------------
            # Update the calibration database
            # --------------------------------------------------------------
            if passed and params['INPUTS']['DATABASE']:
                WLOG(params, '',
                     'Fiber {0}: updating calibration '
                     'database'.format(fiber))
                # copy the blaze file to the calibDB
                calibdbm.add_calib_file(blazefile)
                # copy the flat file to the calibDB
                calibdbm.add_calib_file(flatfile)
            # ------------------------------------------------------------------
            # if recipe is a reference and QC fail we generate an error
            # ------------------------------------------------------------------
            if not passed and params['INPUTS']['REF']:
                eargs = [recipe.name]
                raise AperoCodedException(params, '09-000-00011', targs=eargs)
            # ------------------------------------------------------------------
            # Summary plots
            # ------------------------------------------------------------------
            sorder = params['CAL.FLAT.PLOT_ORDER']
            # plot the fitted blaze and calculated flat with the e2ds image
            recipe.plot('SUM_FLAT_BLAZE_ORDER', order=sorder, eprops=eprops,
                        fiber=fiber)
            # ------------------------------------------------------------------
            # Construct summary document
            # ------------------------------------------------------------------
            flat_blaze.flat_blaze_summary(recipe, params, qc_params, eprops,
                                          fiber)
            # ------------------------------------------------------------------
            # update recipe log file
            # ------------------------------------------------------------------
            log2.end()

        # construct summary (outside fiber loop)
        recipe.plot.summary_document(it)

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

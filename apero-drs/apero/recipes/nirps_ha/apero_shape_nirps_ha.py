#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_shape_nirps_ha.py [obs dir] [files]

APERO shape calibration recipe for NIRPS HA

Created on 2019-03-23 at 13:01

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.science.calib import gen_calib
from apero.science.calib import shape

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_shape_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)


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
    Main function for apero_shape

    :param obs_dir: string, the night name sub-directory
    :param files: list of strings or string, the list of fp files
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
    # get files
    infiles = params['INPUTS']['FILES'][1]
    # must check fp files pass quality control
    infiles = gen_calib.check_fp_files(params, infiles)
    # check qc
    infiles = drs_file.check_input_qc(params, infiles, 'files')
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
        cond = drs_file.combine(params, recipe, infiles, math='median')
        infiles = [cond[0]]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
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
        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = gen_calib.calibrate_ppfile(params, recipe, infile)
        # ------------------------------------------------------------------
        # Load reference fp, shape dxmap and dymap
        # ------------------------------------------------------------------
        fkwargs = dict(database=calibdbm)
        reffp_file, reffp_image = shape.get_ref_fp(params, header,
                                                   **fkwargs)
        # get shape x and shape x mjdmid
        sout = shape.get_shapex(params, header, **fkwargs)
        dxmap_file, dxtime, dxmap = sout
        # get shape y and shape y mjdmid
        sout = shape.get_shapey(params, header, **fkwargs)
        dymap_file, dytime, dymap = sout
        # ----------------------------------------------------------------------
        # Get transform parameters (transform image onto fpref)
        # ----------------------------------------------------------------------
        # log progress
        WLOG(params, '', textentry('40-014-00033'))
        # transform
        targs = [params, recipe, reffp_image, image]
        transform, xres, yres = shape.get_linear_transform_params(*targs)
        # ----------------------------------------------------------------------
        # For debug purposes straighten the image
        # ----------------------------------------------------------------------
        image2 = shape.ea_transform(params, image, transform, dxmap=dxmap,
                                    dymap=dymap)
        # ----------------------------------------------------------------------
        # Quality control
        # ----------------------------------------------------------------------
        qc_params, passed = shape.shape_local_qc(params, transform, xres, yres)
        # update recipe log
        log1.add_qc(qc_params, passed)

        # ------------------------------------------------------------------
        # Writing shape to file
        # ------------------------------------------------------------------
        # push shape properties into dictionary
        sprops = dict(SHAPEX_FILE=dxmap_file, SHAPEX_TIME=dxtime,
                      SHAPEY_FILE=dymap_file, SHAPEY_TIME=dytime,
                      TRANSFORM=transform)
        # write to file
        outfile = shape.write_shape_local_files(params, recipe, infile, combine,
                                                rawfiles, props, sprops,
                                                image, image2, qc_params)
        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if passed and params['INPUTS']['DATABASE']:
            # add shapel transforms
            calibdbm.add_calib_file(outfile)
        # ---------------------------------------------------------------------
        # if recipe is a reference and QC fail we generate an error
        # ---------------------------------------------------------------------
        if not passed and params['INPUTS']['REF']:
            eargs = [recipe.name]
            WLOG(params, 'error', textentry('09-000-00011', args=eargs))
        # ------------------------------------------------------------------
        # plot a zoom in of non-shifted vs shifted
        # ------------------------------------------------------------------
        pkwargs = dict(params=params, image=image, simage=image2)
        # debug plot
        recipe.plot('SHAPEL_ZOOM_SHIFT', **pkwargs)
        # summary plot
        recipe.plot('SUM_SHAPEL_ZOOM_SHIFT', **pkwargs)
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        shape.write_shape_local_summary(recipe, params, qc_params, it,
                                        transform)
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

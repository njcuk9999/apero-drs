#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_flat_nirps_ha.py [obs dir] [files]

APERO flat and blaze finding recipe for NIRPS HA

Created on 2019-07-05 at 16:45

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

from apero.base import base
from apero.core.constants import param_functions
from apero.core import lang
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.io import drs_image
from apero.science import extract
from apero.science.calib import flat_blaze
from apero.science.calib import gen_calib
from apero.science.calib import localisation
from apero.science.calib import shape

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_flat_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
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
def main(obs_dir: Optional[str] = None, files: Optional[List[str]] = None,
         **kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_flat

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
    elif params['INPUT_COMBINE_IMAGES']:
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
        # get the fiber types needed
        fibertypes = drs_image.get_fiber_types(params)

        # ------------------------------------------------------------------
        # Load shape components
        # ------------------------------------------------------------------
        sprops = shape.get_shape_calibs(params, header, database=calibdbm)

        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = gen_calib.calibrate_ppfile(params, recipe, infile,
                                                  database=calibdbm)

        # ------------------------------------------------------------------
        # Load and straighten order profiles
        # ------------------------------------------------------------------
        sargs = [infile, fibertypes, sprops]
        oout = extract.order_profiles(params, recipe, *sargs, database=calibdbm)
        orderps, orderpfiles, orderptimes = oout
        # ------------------------------------------------------------------
        # Apply shape transformations
        # ------------------------------------------------------------------
        # log progress (straightening orderp)
        WLOG(params, 'info', textentry('40-016-00004'))
        # straighten image
        image2 = shape.ea_transform(params, image, sprops['SHAPEL'],
                                    dxmap=sprops['SHAPEX'],
                                    dymap=sprops['SHAPEY'])

        # ------------------------------------------------------------------
        # Fiber loop
        # ------------------------------------------------------------------
        # loop around fiber types
        for fiber in fibertypes:
            # ------------------------------------------------------------------
            # add level to recipe log
            log2 = log1.add_level(params, 'fiber', fiber)
            # --------------------------------------------------------------
            # load the localisation properties for this fiber
            lprops = localisation.get_coefficients(params, header, fiber=fiber,
                                                   merge=True,
                                                   database=calibdbm)
            # get the localisation center coefficients for this fiber
            lcoeffs = lprops['CENT_COEFFS']
            # shift the coefficients
            lcoeffs2 = shape.ea_transform_coeff(image2, lcoeffs,
                                                sprops['SHAPEL'])
            # --------------------------------------------------------------
            # get the number of frames used
            nframes = infile.numfiles
            # --------------------------------------------------------------
            # get the order profile for this fiber
            lprops['ORDERP'] = orderps[fiber]
            lprops['ORDERPFILE'] = orderpfiles[fiber]
            lprops['ORDERPTIME'] = orderptimes[fiber]
            lprops.set_sources(['ORDERP', 'ORDERPFILE', 'ORDERPTIME'], mainname)
            # --------------------------------------------------------------
            # extract spectrum
            eprops = extract.extract2d(params, image2, lprops['ORDERP'],
                                       lcoeffs2, nframes, props,
                                       kind='flat', fiber=fiber)
            # fit blaze and get flat
            eprops = extract.extract_blaze_flat(params, eprops, fiber)
            # --------------------------------------------------------------
            # Plots
            # --------------------------------------------------------------
            sorder = params['FF_PLOT_ORDER']
            # plot (in a loop) order fit + e2ds (on original image)
            recipe.plot('FLAT_ORDER_FIT_EDGES1', params=params, image1=image,
                        image2=image2, order=None, coeffs1=lcoeffs,
                        coeffs2=lcoeffs2, fiber=fiber)
            # plot for sorder order fit + e2ds (on original image)
            recipe.plot('FLAT_ORDER_FIT_EDGES2', params=params, image1=image,
                        image2=image2, order=sorder, coeffs1=lcoeffs,
                        coeffs2=lcoeffs2, fiber=fiber)
            # plot (in a loop) the fitted blaze and calculated flat with the
            #     e2ds image
            recipe.plot('FLAT_BLAZE_ORDER1', order=None, eprops=eprops,
                        fiber=fiber)
            # plot for sorder the fitted blaze and calculated flat with the
            #     e2ds image
            recipe.plot('FLAT_BLAZE_ORDER2', order=sorder, eprops=eprops,
                        fiber=fiber)
            # --------------------------------------------------------------
            # Quality control
            # --------------------------------------------------------------
            qc_params, passed = flat_blaze.flat_blaze_qc(params, eprops, fiber)
            # update recipe log
            log2.add_qc(qc_params, passed)
            # --------------------------------------------------------------
            # write files
            # --------------------------------------------------------------
            wargs = [infile, eprops, fiber, rawfiles, combine, props, lprops,
                     sprops, qc_params]
            outfiles = flat_blaze.flat_blaze_write(params, recipe, *wargs)
            blazefile, flatfile = outfiles

            # --------------------------------------------------------------
            # Update the calibration database
            # --------------------------------------------------------------
            if passed and params['INPUTS']['DATABASE']:
                # copy the blaze file to the calibDB
                calibdbm.add_calib_file(blazefile)
                # copy the flat file to the calibDB
                calibdbm.add_calib_file(flatfile)
            # ---------------------------------------------------------------------
            # if recipe is a reference and QC fail we generate an error
            # ---------------------------------------------------------------------
            if not passed and params['INPUTS']['REF']:
                eargs = [recipe.name]
                WLOG(params, 'error', textentry('09-000-00011', args=eargs))
            # ------------------------------------------------------------------
            # Summary plots
            # ------------------------------------------------------------------
            sorder = params['FF_PLOT_ORDER']
            # plot (in a loop) order fit + e2ds (on original image)
            recipe.plot('SUM_FLAT_ORDER_FIT_EDGES', params=params, image1=image,
                        image2=image2, order=sorder, coeffs1=lcoeffs,
                        coeffs2=lcoeffs2, fiber=fiber)
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

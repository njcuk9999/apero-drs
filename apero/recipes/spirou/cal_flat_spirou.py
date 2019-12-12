#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:45

@author: cook
"""
from __future__ import division

from apero import core
from apero import locale
from apero.core import constants
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.io import drs_image
from apero.science.calib import general
from apero.science.calib import localisation
from apero.science.calib import shape
from apero.science.calib import flat_blaze
from apero.science import extract

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_flat_spirou.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# Define the output files



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
    Main function for cal_flat_spirou.py

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
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        infiles = [drs_fits.combine(params, infiles, math='median')]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)
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
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.header
        # get calibrations for this data
        drs_database.copy_calibrations(params, header)
        # get the fiber types needed
        fibertypes = drs_image.get_fiber_types(params)

        # ------------------------------------------------------------------
        # Load shape components
        # ------------------------------------------------------------------
        shapexfile, shapex = shape.get_shapex(params, header)
        shapeyfile, shapey = shape.get_shapey(params, header)
        shapelocalfile, shapelocal = shape.get_shapelocal(params, header)

        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = general.calibrate_ppfile(params, recipe, infile)

        # ------------------------------------------------------------------
        # Load and straighten order profiles
        # ------------------------------------------------------------------
        sargs = [infile, fibertypes, shapelocal, shapex, shapey,
                 recipe.outputs['ORDERP_SFILE']]
        orderps, orderpfiles = extract.order_profiles(params, recipe, *sargs)

        # ------------------------------------------------------------------
        # Apply shape transformations
        # ------------------------------------------------------------------
        # log progress (straightening orderp)
        WLOG(params, 'info', TextEntry('40-016-00004'))
        # straighten image
        image2 = shape.ea_transform(params, image, shapelocal, dxmap=shapex,
                                    dymap=shapey)

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
            lprops = localisation.get_coefficients(params, recipe, header,
                                                   fiber=fiber, merge=True)
            # get the localisation center coefficients for this fiber
            lcoeffs = lprops['CENT_COEFFS']
            # shift the coefficients
            lcoeffs2 = shape.ea_transform_coeff(image2, lcoeffs, shapelocal)
            # --------------------------------------------------------------
            # get the number of frames used
            nframes = infile.numfiles
            # --------------------------------------------------------------
            # get the order profile for this fiber
            orderp = orderps[fiber]
            orderpfile = orderpfiles[fiber]
            # --------------------------------------------------------------
            # extract spectrum
            eprops = extract.extract2d(params, image2, orderp, lcoeffs2,
                                       nframes, props, kind='flat', fiber=fiber)
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
            log2.add_qc(params, qc_params, passed)
            # --------------------------------------------------------------
            # write files
            # --------------------------------------------------------------
            wargs = [infile, eprops, fiber, rawfiles, combine, props, lprops,
                     orderpfile, shapelocalfile, shapexfile, shapeyfile,
                     qc_params]
            outfiles = flat_blaze.flat_blaze_write(params, recipe, *wargs)
            blazefile, flatfile = outfiles

            # --------------------------------------------------------------
            # Update the calibration database
            # --------------------------------------------------------------
            if passed:
                # copy the blaze file to the calibDB
                drs_database.add_file(params, blazefile)
                # copy the flat file to the calibDB
                drs_database.add_file(params, flatfile)
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
            log2.end(params)

        # construct summary (outside fiber loop)
        recipe.plot.summary_document(it)

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

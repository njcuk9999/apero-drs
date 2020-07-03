#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-13 at 11:04

@author: cook
"""
import numpy as np

from apero import core
from apero import lang
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.io import drs_image
from apero.science.calib import badpix
from apero.science.calib import background

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_badpix_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
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
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, flatfiles=None, darkfiles=None, **kwargs):
    """
    Main function for cal_badpix_spirou.py

    :param directory: string, the night name sub-directory
    :param flatfiles: list of strings or string, the list of flat files
    :param darkfiles: list of strings or string, the list of dark files
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, flatfiles=flatfiles,
                   darkfiles=darkfiles, **kwargs)
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
    flatfiles = params['INPUTS']['FLATFILES'][1]
    darkfiles = params['INPUTS']['DARKFILES'][1]
    # get list of filenames (for output)
    rawflatfiles, rawdarkfiles = [], []
    for infile in flatfiles:
        rawflatfiles.append(infile.basename)
    for infile in darkfiles:
        rawdarkfiles.append(infile.basename)
    # deal with input data from function
    if 'flatfiles' in params['DATA_DICT']:
        flatfiles = params['DATA_DICT']['flatfiles']
        darkfiles = params['DATA_DICT']['darkfiles']
        rawflatfiles = params['DATA_DICT']['rawflatfiles']
        rawdarkfiles = params['DATA_DICT']['rawdarkfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        flatfiles = [drs_fits.combine(params, recipe, flatfiles, math='median')]
        # get combined file
        darkfiles = [drs_fits.combine(params, recipe, darkfiles, math='median')]
        combine = True
    else:
        combine = False
    # warn user if lengths differ
    if len(flatfiles) != len(darkfiles):
        wargs = [len(flatfiles), len(darkfiles)]
        WLOG(params, 'error', TextEntry('10-012-00001', args=wargs))
        # get the number of files
        num_files = mp.nanmin([len(flatfiles), len(darkfiles)])
    else:
        # get the number of files
        num_files = len(flatfiles)

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
        # get this iterations file
        flatfile = flatfiles[it]
        darkfile = darkfiles[it]
        # get data from file instance
        flat_image = np.array(flatfile.data)
        dark_image = np.array(darkfile.data)
        # ------------------------------------------------------------------
        # Normalise flat and median of flat
        # ------------------------------------------------------------------
        flat_med, flat_image = badpix.normalise_median_flat(params, flat_image)
        # ------------------------------------------------------------------
        # Locate bad pixels
        # ------------------------------------------------------------------
        # Locate bad pixels from dark and flat
        bargs = [flat_image, flat_med, dark_image]
        badpixelmap_a, bstats_a = badpix.locate_bad_pixels(params, *bargs)
        # Locate bad pixels from full detector flat
        bargs = [flat_image]
        badpixelmap_b, bstats_b = badpix.locate_bad_pixels_full(params, *bargs)

        # ------------------------------------------------------------------
        # Combine bad pixel masks
        # ------------------------------------------------------------------
        bad_pixel_map = badpixelmap_a | badpixelmap_b
        # total number of bad pixels
        btotal = (mp.nansum(bad_pixel_map) / bad_pixel_map.size) * 100
        # log result
        WLOG(params, '', TextEntry('40-012-00007', args=[btotal]))

        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        recipe.plot('BADPIX_MAP', badmap=bad_pixel_map)

        # ------------------------------------------------------------------
        # Flip images
        # ------------------------------------------------------------------
        if params['INPUT_FLIP_IMAGE']:
            # flip flat
            flat_image1 = drs_image.flip_image(params, flat_image)
            # flip bad pixel map
            bad_pixel_map1 = drs_image.flip_image(params, bad_pixel_map)
        else:
            flat_image1, bad_pixel_map1 = flat_image, bad_pixel_map

        # ------------------------------------------------------------------
        # Resize image
        # ------------------------------------------------------------------
        if params['INPUT_RESIZE_IMAGE']:
            # get resize size
            sargs = dict(xlow=params['IMAGE_X_LOW'],
                         xhigh=params['IMAGE_X_HIGH'],
                         ylow=params['IMAGE_Y_LOW'],
                         yhigh=params['IMAGE_Y_HIGH'])
            # resize flat
            flat_image1 = drs_image.resize(params, flat_image1, **sargs)
            # resize bad pixel map
            bad_pixel_map1 = drs_image.resize(params, bad_pixel_map1, **sargs)
        else:
            flat_image1 = np.array(flat_image)
            bad_pixel_map1 = np.array(bad_pixel_map)

        # ------------------------------------------------------------------
        # Create background map mask
        # ------------------------------------------------------------------
        bargs = [flat_image1, bad_pixel_map1]
        backmap = background.create_background_map(params, *bargs)

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        qc_params, passed = badpix.quality_control(params)
        # update recipe log
        log1.add_qc(params, qc_params, passed)

        # ----------------------------------------------------------------------
        # Save bad pixel mask
        # ----------------------------------------------------------------------
        wargs = [flatfile, darkfile, backmap, combine, rawflatfiles,
                 rawdarkfiles, bstats_a, bstats_b, btotal, bad_pixel_map1,
                 qc_params]
        badpixfile, backmapfile = badpix.write_files(params, recipe, *wargs)
        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if passed:
            drs_database.add_file(params, badpixfile)
            drs_database.add_file(params, backmapfile)
        # ------------------------------------------------------------------
        # Summary plots
        # ------------------------------------------------------------------
        recipe.plot('SUM_BADPIX_MAP', badmap=bad_pixel_map)
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        badpix.summary(recipe, it, params, bstats_a, bstats_b, btotal)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end(params)

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-13 at 11:04

@author: cook
"""
from __future__ import division
import numpy as np

from terrapipe import constants
from terrapipe import config
from terrapipe import locale
from terrapipe.config.core import drs_database
from terrapipe.config.instruments.spirou import file_definitions
from terrapipe.io import drs_fits
from terrapipe.science.calib import badpix
from terrapipe.science.calib import background

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_DARK_spirou.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = config.wlog
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
    recipe, params = config.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = config.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    params = config.end_main(params, success)
    # return a copy of locally defined variables in the memory
    return config.get_locals(dict(locals()), llmain)


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
    rawfiles = []
    for infile in flatfiles:
        rawfiles.append(infile.basename)
    # combine input flat images if required
    if params['INPUT_COMBINE_IMAGES']:
        # get combined file
        flatfiles = [drs_fits.combine(params, flatfiles, math='average')]
        # get combined file
        darkfiles = [drs_fits.combine(params, darkfiles, math='average')]

    # warn user if lengths differ
    if len(flatfiles) != len(darkfiles):
        wargs = [len(flatfiles), len(darkfiles)]
        WLOG(params, 'warning', TextEntry('10-012-00001', args=wargs))
        # get the number of files
        num_files = np.min([len(flatfiles), len(darkfiles)])
    else:
        # get the number of files
        num_files = len(flatfiles)

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # print file iteration progress
        config.file_processing_update(params, it, num_files)
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
        btotal = (np.nansum(bad_pixel_map) / bad_pixel_map.size) * 100
        # log result
        WLOG(params, '', TextEntry('40-012-00007', args=btotal))

        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        # TODO: fill in section

        # ------------------------------------------------------------------
        # Flip images
        # ------------------------------------------------------------------
        if params['INPUT_FLIP_IMAGE']:
            # flip flat
            flat_image1 = drs_fits.flip_image(params, flat_image)
            # flip bad pixel map
            bad_pixel_map1 = drs_fits.flip_image(params, bad_pixel_map)
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
            flat_image1 = drs_fits.resize(params, flat_image1, **sargs)
            # resize bad pixel map
            bad_pixel_map1 = drs_fits.resize(params, bad_pixel_map1, **sargs)
        else:
            flat_image1, bad_pixel_map1 = flat_image, bad_pixel_map

        # ------------------------------------------------------------------
        # Create background map mask
        # ------------------------------------------------------------------
        bargs = [flat_image1, bad_pixel_map1]
        backmap = background.create_background_map(params, *bargs)



    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    config.end(ll, has_plots=True)

# =============================================================================
# End of code
# =============================================================================

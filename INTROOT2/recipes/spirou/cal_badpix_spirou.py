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

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.core.instruments.spirou import file_definitions
from terrapipe.io import drs_fits
from terrapipe.io import drs_image
from terrapipe.science.calib import badpix
from terrapipe.science.calib import background

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_badpix_spirou.py'
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
BADPIX = file_definitions.out_badpix
BACKMAP = file_definitions.out_backmap


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
    params = core.end_main(params, success)
    # return a copy of locally defined variables in the memory
    return core.get_locals(dict(locals()), llmain)


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
    # combine input flat images if required
    if params['INPUT_COMBINE_IMAGES']:
        # get combined file
        flatfiles = [drs_fits.combine(params, flatfiles, math='average')]
        # get combined file
        darkfiles = [drs_fits.combine(params, darkfiles, math='average')]
        combine = True
    else:
        combine = False
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
        btotal = (np.nansum(bad_pixel_map) / bad_pixel_map.size) * 100
        # log result
        WLOG(params, '', TextEntry('40-012-00007', args=[btotal]))

        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        # TODO: fill in section

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
        # set passed variable and fail message list
        fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # ------------------------------------------------------------------
        # TODO: Needs doing
        # add to qc header lists
        qc_values.append('None')
        qc_names.append('None')
        qc_logic.append('None')
        qc_pass.append(1)
        # ------------------------------------------------------------------
        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if np.sum(qc_pass) == len(qc_pass):
            WLOG(params, 'info', TextEntry('40-005-10001'))
            params['QC'] = 1
            params.set_source('QC', __NAME__ + '/main()')
        else:
            for farg in fail_msg:
                WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
            params['QC'] = 0
            params.set_source('QC', __NAME__ + '/main()')
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

        # ----------------------------------------------------------------------
        # Save bad pixel mask
        # ----------------------------------------------------------------------
        badpixfile = BADPIX.newcopy(recipe=recipe)
        # construct the filename from file instance
        badpixfile.construct_filename(params, infile=flatfile)
        # ------------------------------------------------------------------
        # define header keys for output file
        # copy keys from input file
        badpixfile.copy_original_keys(flatfile)
        # add version
        badpixfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add process id
        badpixfile.add_hkey('KW_PID', value=params['PID'])
        # add output tag
        badpixfile.add_hkey('KW_OUTPUT', value=badpixfile.name)
        # add input files
        if combine:
            hfiles1, hfiles2 = rawflatfiles, rawdarkfiles
        else:
            hfiles1, hfiles2 = [flatfile.basename], [darkfile.basename]
        badpixfile.add_hkey_1d('KW_INFILE1', values=hfiles1,
                               dim1name='flatfile')
        badpixfile.add_hkey_1d('KW_INFILE2', values=hfiles2,
                               dim1name='darkfile')
        # add qc parameters
        badpixfile.add_qckeys(qc_params)
        # add background statistics
        badpixfile.add_hkey('KW_BHOT', value=bstats_a[0])
        badpixfile.add_hkey('KW_BBFLAT', value=bstats_a[1])
        badpixfile.add_hkey('KW_BNDARK', value=bstats_a[2])
        badpixfile.add_hkey('KW_BNFLAT', value=bstats_a[3])
        badpixfile.add_hkey('KW_BBAD', value=bstats_a[4])
        badpixfile.add_hkey('KW_BNILUM', value=bstats_b)
        badpixfile.add_hkey('KW_BTOT', value=btotal)
        # write to file
        bad_pixel_map1 = np.array(bad_pixel_map1, dtype=int)
        # copy data
        badpixfile.data = bad_pixel_map1
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        WLOG(params, '', TextEntry('40-012-00013', args=[badpixfile.filename]))
        # write image to file
        badpixfile.write()

        # ----------------------------------------------------------------------
        # Save background map file
        # ----------------------------------------------------------------------
        backmapfile = BACKMAP.newcopy(recipe=recipe)
        # construct the filename from file instance
        backmapfile.construct_filename(params, infile=flatfile)
        # ------------------------------------------------------------------
        # define header keys for output file
        # copy keys from input file
        backmapfile.copy_original_keys(flatfile)
        # add version
        backmapfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add process id
        backmapfile.add_hkey('KW_PID', value=params['PID'])
        # add output tag
        backmapfile.add_hkey('KW_OUTPUT', value=backmapfile.name)
        # add input files (and deal with combining or not combining)
        if combine:
            hfiles1, hfiles2 = rawflatfiles, rawdarkfiles
        else:
            hfiles1, hfiles2 = [flatfile.basename], [darkfile.basename]
        badpixfile.add_hkey_1d('KW_INFILE1', values=hfiles1,
                               dim1name='flatfile')
        badpixfile.add_hkey_1d('KW_INFILE2', values=hfiles2,
                               dim1name='darkfile')
        # add qc parameters
        backmapfile.add_qckeys(qc_params)
        # write to file
        backmap = np.array(backmap, dtype=int)
        # copy data
        backmapfile.data = backmap
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        WLOG(params, '', TextEntry('40-012-00014', args=[backmapfile.filename]))
        # write image to file
        backmapfile.write()

        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if params['QC']:
            drs_database.add_file(params, badpixfile)
            drs_database.add_file(params, backmapfile)

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
    core.end(ll, has_plots=True)

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

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
from terrapipe.science.calib import dark


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_dark_spirou.py'
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
    Main function for cal_dark_spirou.py

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
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get data from file instance
        image = np.array(infile.data)
        # ------------------------------------------------------------------
        # Get basic image properties
        # ------------------------------------------------------------------
        # get image readout noise
        sigdet = infile.get_key('KW_RDNOISE')
        # get expsoure time
        exptime = infile.get_key('KW_EXPTIME')
        # get gain
        gain = infile.get_key('KW_GAIN')
        # get data type
        dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
        # ------------------------------------------------------------------
        # Dark exposure time check
        # ------------------------------------------------------------------
        # log the Dark exposure time
        WLOG(params, 'info', 'Dark Time = {0:.3f} s'.format(exptime))
        # Quality control: make sure the exposure time is longer than
        #                  qc_dark_time
        if exptime < params['QC_DARK_TIME']:
            emsg = 'Dark exposure time too short (< {0:.1f} s)'
            WLOG(params, 'error', emsg.format(params['QC_DARK_TIME']))
        # ------------------------------------------------------------------
        # Resize and rotate image
        # ------------------------------------------------------------------
        # convert NaNs to zeros
        nanmask = ~np.isfinite(image)
        image0 = np.where(nanmask, np.zeros_like(image), image)
        # resize blue image
        bkwargs = dict(xlow=params['IMAGE_X_BLUE_LOW'],
                       xhigh=params['IMAGE_X_BLUE_HIGH'],
                       ylow=params['IMAGE_Y_BLUE_LOW'],
                       yhigh=params['IMAGE_Y_BLUE_HIGH'])
        imageblue = drs_image.resize(params, image0, **bkwargs)
        # resize red image
        rkwargs = dict(xlow=params['IMAGE_X_RED_LOW'],
                       xhigh=params['IMAGE_X_RED_HIGH'],
                       ylow=params['IMAGE_Y_RED_LOW'],
                       yhigh=params['IMAGE_Y_RED_HIGH'])
        imagered = drs_image.resize(params, image0, **rkwargs)
        # ------------------------------------------------------------------
        # Dark Measurement
        # ------------------------------------------------------------------
        # Log that we are doing dark measurement
        WLOG(params, '', TextEntry('40-011-00001'))
        # measure dark for whole frame
        out1 = dark.measure_dark(params, image, '40-011-00003')
        hist_full, med_full, dadead_full = out1
        # measure dark for blue part
        out2 = dark.measure_dark(params, imageblue, '40-011-00004')
        hist_blue, med_blue, dadead_blue = out2
        # measure dark for rede part
        out3 = dark.measure_dark(params, imagered, '40-011-00005')
        hist_red, med_red, dadead_red = out3
        # ------------------------------------------------------------------
        # Identification of bad pixels
        # ------------------------------------------------------------------
        # Question bad pixel detection is done in cal_BAD_pix
        # Question:   shouldn't this be used instead of a separate badpix here?
        out = dark.measure_dark_badpix(params, image, nanmask)
        baddark, dadeadall = out
        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        recipe.plot('DARK_IMAGE_REGIONS', params=params, image=image,
                             med=med_full)
        recipe.plot('DARK_HISTOGRAM', params=params,
                             histograms=[hist_full, hist_blue, hist_red])
        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        qc_params, passed = dark.dark_qc(params, med_full, dadeadall, baddark)

        # ------------------------------------------------------------------
        # Save dark to file
        # ------------------------------------------------------------------
        wargs = [dprtype, infile, combine, rawfiles, dadead_full, med_full,
                 dadead_blue, med_blue, dadead_red, med_red, qc_params, image0]
        outfile = dark.dark_write_files(params, recipe, *wargs)

        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if passed:
            drs_database.add_file(params, outfile)
        # ------------------------------------------------------------------
        # Summary plots
        # ------------------------------------------------------------------
        recipe.plot('SUM_DARK_IMAGE_REGIONS', params=params, image=image,
                    med=med_full)
        recipe.plot('SUM_DARK_HISTOGRAM', params=params,
                    histograms=[hist_full, hist_blue, hist_red])
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        dark.dark_summary(recipe, it, params, dadead_full, med_full,
                          dadead_blue, med_blue, dadead_red, med_red, qc_params)

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

@author: cook
"""
from __future__ import division
import traceback
import numpy as np

from drsmodule import constants
from drsmodule import config
from drsmodule import locale
from drsmodule.io import drs_fits
from drsmodule.science.calib import dark

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
ErrorEntry = locale.drs_text.ErrorEntry


# =============================================================================
# Define functions
# =============================================================================
def _main(recipe, params):
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get files
    infiles = params['INPUTS']['FILES'][1]
    # combine input images if required
    if params['COMBINE_IMAGES']:
        infiles = [drs_fits.combine(params, infiles, math='average')]
    # get the number of infiles
    num_files = len(infiles)

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # print file iteration progress
        config.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get data from file instance
        image = np.array(infile.data)

        # ------------------------------------------------------------------
        # Get basic image properties
        # ------------------------------------------------------------------
        # get image readout noise
        params['SIGDET'] = infile.get_key('KW_RDNOISE')
        # get expsoure time
        params['EXPTIME'] = infile.get_key('KW_EXPTIME')
        # get gain
        params['GAIN'] = infile.get_key('KW_GAIN')
        # set sources
        params.set_sources(['SIGDET', 'EXPTIME', 'GAIN'], mainname)

        # ------------------------------------------------------------------
        # Dark exposure time check
        # ------------------------------------------------------------------
        # log the Dark exposure time
        WLOG(params, 'info', 'Dark Time = {0:.3f} s'.format(params['EXPTIME']))
        # Quality control: make sure the exposure time is longer than qc_dark_time
        if params['EXPTIME'] < params['QC_DARK_TIME']:
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
        imageblue = drs_fits.resize(params, image0, **bkwargs)

        # resize red image
        bkwargs = dict(xlow=params['IMAGE_X_RED_LOW'],
                       xhigh=params['IMAGE_X_RED_HIGH'],
                       ylow=params['IMAGE_Y_RED_LOW'],
                       yhigh=params['IMAGE_Y_RED_HIGH'])
        imagered = drs_fits.resize(params, image0, **bkwargs)

        # ------------------------------------------------------------------
        # Dark Measurement
        # ------------------------------------------------------------------
        # Log that we are doing dark measurement
        WLOG(params, '', ErrorEntry('40-011-00001'))
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
        # TODO: fill in section

        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        # TODO: fill in section

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        # TODO: fill in section

        # ------------------------------------------------------------------
        # Save dark to file
        # ------------------------------------------------------------------
        # TODO: fill in section

        # ----------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ----------------------------------------------------------------------
        # TODO: fill in section


    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return dict(locals())


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
    recipe, params = config.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    if params['DRS_DEBUG'] > 0:
        llmain = _main(recipe, params)
        llmain['e'], llmain['tb'] = None, None
        success = True
    else:
        try:
            llmain = _main(recipe, params)
            llmain['e'], llmain['tb'] = None, None
            success = True
        except Exception as e:
            string_trackback = traceback.format_exc()
            success = False
            emsg = ErrorEntry('01-010-00001', args=[type(e)])
            emsg += '\n\n' + ErrorEntry(string_trackback)
            WLOG(params, 'error', emsg, raise_exception=False, wrap=False)
            llmain = dict(e=e, tb=string_trackback)
        except SystemExit as e:
            string_trackback = traceback.format_exc()
            success = False
            llmain = dict(e=e, tb=string_trackback)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    params = config.end_main(params, success)
    # return a copy of locally defined variables in the memory
    return config.get_locals(dict(locals()), llmain)


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

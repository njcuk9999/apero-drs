#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-14 at 09:40

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
from terrapipe.science.calib import dark


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_loc_spirou.py'
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
    # get calibration database
    cdb = drs_database.get_full_database(params, 'calibration')
    params[cdb.dbshort] = cdb
    # get files
    infiles = params['INPUTS']['FILES'][1]
    # get list of filenames (for output)
    rawfiles = []
    for infile in infiles:
        rawfiles.append(infile.basename)
    # combine input images if required
    if params['INPUT_COMBINE_IMAGES']:
        # get combined file
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
        header = infile.header
        # get calibrations for this data
        drs_database.copy_calibrations(params, header)
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
        # Correction of DARK
        # ------------------------------------------------------------------
        params, image1 = dark.correction(params, image, header, len(rawfiles))

        # ------------------------------------------------------------------
        # Resize image
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Correct for the BADPIX mask (set all bad pixels to NaNs)
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Background computation
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Construct image order_profile
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Write image order_profile to file
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Move order_profile to calibDB and update calibDB
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Localization of orders on central column
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Measurement and correction of background on the central column
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Search for order center on the central column - quick estimation
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Search for order center and profile on specific columns
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Plot the image (ready for fit points to be overplotted later)
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Plot of RMS for positions and widths
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Save and record of image of localization with order center
        #     and keywords
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Save and record of image of sigma
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Save and Record of image of localization
        # ------------------------------------------------------------------
        # TODO: complete

        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        # TODO: complete


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

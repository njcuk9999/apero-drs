#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:38
@author: ncook
Version 0.0.1
"""
import numpy as np
import os

from apero import core
from apero import locale
from apero.core import constants
from apero.science import preprocessing
from apero.io import drs_image
from apero.io import drs_fits
from apero.core.instruments.spirou import file_definitions


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_preprocess_spirou.py'
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
# Raw prefix
RAW_PREFIX = file_definitions.raw_prefix


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
    Main function for cal_preprocess_spirou.py

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
    return core.end_main(params, llmain, recipe, success, outputs='None')



def __main__(recipe, params):
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # Get hot pixels for corruption check
    hotpixels = preprocessing.get_hot_pixels(params)
    # get skip parmaeter
    skip = params['SKIP_DONE_PP']

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    # get files
    infiles = params['INPUTS']['FILES'][1]
    # Number of files
    num_files = len(params['INPUTS']['FILES'][1])
    # storage for output files
    output_names = []

    # loop around number of files
    for it in range(num_files):
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', it)
        # ------------------------------------------------------------------
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        file_instance = infiles[it]
        # ------------------------------------------------------------------
        # Fix the spirou header
        # ------------------------------------------------------------------
        # certain keys may not be in some spirou files
        file_instance = preprocessing.fix_header(params, recipe, file_instance)
        # ------------------------------------------------------------------
        # identification of file drs type
        # ------------------------------------------------------------------
        # identify this iterations file type
        cond, infile = preprocessing.drs_infile_id(params, recipe,
                                                   file_instance)
        # ------------------------------------------------------------------
        # if it wasn't found skip this file, if it was print a message
        if cond:
            eargs = [infile.name]
            WLOG(params, 'info', TextEntry('40-010-00001', args=eargs))
        else:
            eargs = [infile.filename]
            WLOG(params, 'info', TextEntry('40-010-00002', args=eargs))
            continue
        # get data from file instance
        image = np.array(infile.data)

        # ------------------------------------------------------------------
        # Get out file and check skip
        # ------------------------------------------------------------------
        # get the output drs file
        oargs = [params, recipe, infile, recipe.outputs['PP_FILE'], RAW_PREFIX]
        found, outfile = preprocessing.drs_outfile_id(*oargs)
        # construct out filename
        outfile.construct_filename(params, infile=infile)
        # if we didn't find the output file we should log this error
        if not found:
            eargs = [outfile.name]
            WLOG(params, 'error', TextEntry('00-010-00003', args=eargs))
        if skip:
            if os.path.exists(outfile.filename):
                wargs = [infile.filename]
                WLOG(params, 'info', TextEntry('40-010-00012', args=wargs))
                continue

        # ----------------------------------------------------------------------
        # Check for pixel shift and/or corrupted files
        # ----------------------------------------------------------------------
        # get pass condition
        cout = preprocessing.test_for_corrupt_files(params, image, hotpixels)
        snr_hotpix, rms_list = cout[0], cout[1]
        shiftdx, shiftdy = cout[2], cout[3]
        # use dx/dy to shift the image back to where the engineering flat
        #    is located
        if shiftdx != 0 or shiftdy != 0:
            # log process
            WLOG(params, '', TextEntry('40-010-00013', args=[shiftdx, shiftdy]))
            # shift image
            image = np.roll(image, [shiftdy], axis=0)
            image = np.roll(image, [shiftdx], axis=1)

        # ------------------------------------------------------------------
        # correct image
        # ------------------------------------------------------------------
        # correct for the top and bottom reference pixels
        WLOG(params, '', TextEntry('40-010-00003'))
        image = preprocessing.correct_top_bottom(params, image)

        # correct by a median filter from the dark amplifiers
        WLOG(params, '', TextEntry('40-010-00004'))
        image = preprocessing.median_filter_dark_amps(params, image)

        # correct for the 1/f noise
        WLOG(params, '', TextEntry('40-010-00005'))
        image = preprocessing.median_one_over_f_noise(params, image)

        # ------------------------------------------------------------------
        # Quality control to check for corrupt files
        # ------------------------------------------------------------------
        qargs = [snr_hotpix, infile, rms_list]
        qc_params, passed = preprocessing.quality_control(params ,*qargs)
        # update recipe log
        log1.add_qc(params, qc_params, passed)
        if not passed:
            # end log here
            log1.end(params)
            # go to next iteration
            continue

        # ------------------------------------------------------------------
        # calculate mid observation time
        # ------------------------------------------------------------------
        mout = drs_fits.get_mid_obs_time(params, infile.header)
        mid_obs_time, mid_obs_method = mout

        # ------------------------------------------------------------------
        # rotate image
        # ------------------------------------------------------------------
        # rotation to match HARPS orientation (expected by DRS)
        image = drs_image.rotate_image(image, params['RAW_TO_PP_ROTATION'])

        # ------------------------------------------------------------------
        # Save rotated image
        # ------------------------------------------------------------------
        # define header keys for output file
        # copy keys from input file
        outfile.copy_original_keys(infile)
        # add version
        outfile.add_hkey('KW_PPVERSION', value=params['DRS_VERSION'])
        # add dates
        outfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
        outfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
        # add process id
        outfile.add_hkey('KW_PID', value=params['PID'])
        # add input filename
        outfile.add_hkey_1d('KW_INFILE1', values=[infile.basename],
                            dim1name='infile')
        # add qc parameters
        outfile.add_qckeys(qc_params)
        # add dprtype
        outfile.add_hkey('KW_DPRTYPE', value=outfile.name)
        # add the shift that was used to correct the image
        outfile.add_hkey('KW_PPSHIFTX', value=shiftdx)
        outfile.add_hkey('KW_PPSHIFTY', value=shiftdy)
        # add mid observation time
        outfile.add_hkey('KW_MID_OBS_TIME', value=mid_obs_time.mjd)
        outfile.add_hkey('KW_MID_OBSTIME_METHOD', value=mid_obs_method)
        # ------------------------------------------------------------------
        # copy data
        outfile.data = image
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        wargs = [outfile.filename]
        WLOG(params, '', TextEntry('40-010-00009', args=wargs))
        # ------------------------------------------------------------------
        # writefits image to file
        outfile.write_file()
        # add to output files (for indexing)
        recipe.add_output_file(outfile)
        # index this file
        core.end_main(params, None, recipe, success=True, outputs='pp',
                      end=False)
        # ------------------------------------------------------------------
        # append to output storage in p
        # ------------------------------------------------------------------
        output_names.append(outfile.filename)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end(params)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, dict(locals()))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

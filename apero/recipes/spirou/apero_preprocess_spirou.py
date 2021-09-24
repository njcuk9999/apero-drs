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

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.utils import drs_startup
from apero.science import preprocessing as prep
from apero.io import drs_image
from apero.core.instruments.spirou import file_definitions


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_preprocess_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# Raw prefix
RAW_PREFIX = file_definitions.raw_prefix
# get the object database
ObjectDatabase = drs_database.ObjectDatabase


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(obs_dir=None, files=None, **kwargs):
    """
    Main function for apero_preprocess

    :param obs_dir: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type obs_dir: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
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
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # Get hot pixels for corruption check
    hotpixels = prep.get_hot_pixels(params)
    # get skip parmaeter
    skip = params['SKIP_DONE_PP']
    # get pseudo constants
    pconst = constants.pload()
    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    # get files
    infiles = params['INPUTS']['FILES'][1]
    # Number of files
    num_files = len(params['INPUTS']['FILES'][1])
    # storage for output files
    output_names = []
    # get object database
    objdbm = ObjectDatabase(params)

    # loop around number of files
    for it in range(num_files):
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', it)
        # ------------------------------------------------------------------
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
        # ge this iterations file
        file_instance = infiles[it]
        # ------------------------------------------------------------------
        # Check that file is not in bad list
        # ------------------------------------------------------------------
        # find out if file is flagged as bad
        reject_file = prep.reject_infile(params, file_instance.get_header())
        # deal with bad files
        if reject_file:
            WLOG(params, 'warning', textentry('10-503-00022'))

        # ------------------------------------------------------------------
        # Fix the header
        # ------------------------------------------------------------------
        # certain keys may not be in some spirou files
        file_instance = drs_file.fix_header(params, recipe, file_instance)
        # ------------------------------------------------------------------
        # identification of file drs type
        # ------------------------------------------------------------------
        # identify this iterations file type
        cond, infile = prep.drs_infile_id(params, recipe, file_instance)

        # ------------------------------------------------------------------
        # For OBJECT files we need to resolve object and update header
        # ------------------------------------------------------------------
        obj_dprtypes = params.listp('PP_OBJ_DPRTYPES', dtype=str)
        # only resolve targets that are objects
        if infile.get_hkey('KW_DPRTYPE') in obj_dprtypes:
            # get object based on object name and gaia id
            infile.header = prep.resolve_target(params, pconst,
                                                header=infile.header,
                                                database=objdbm)
        # ------------------------------------------------------------------
        # if it wasn't found skip this file, if it was print a message
        if cond:
            eargs = [infile.name]
            WLOG(params, 'info', textentry('40-010-00001', args=eargs))
        else:
            eargs = [infile.filename]
            WLOG(params, 'info', textentry('40-010-00002', args=eargs))
            continue
        # get data from file instance
        datalist = infile.get_data(copy=True, extensions=[1, 2, 3, 4])
        # get flux image from the data list
        image = datalist[0]
        # get intercept from the data list
        intercept = datalist[1]
        # get error on slope from the data list
        errslope = datalist[2]
        # get frame time
        frame_time = pconst.FRAME_TIME(params, infile.get_header())
        # get the pixel exposure time from the data list
        inttime = datalist[3] * frame_time

        # ------------------------------------------------------------------
        # Get out file and check skip
        # ------------------------------------------------------------------
        # get the output drs file
        oargs = [params, recipe, infile, recipe.outputs['PP_FILE'], RAW_PREFIX]
        found, outfile = prep.drs_outfile_id(*oargs)
        # construct out filename
        outfile.construct_filename(infile=infile)
        # if we didn't find the output file we should log this error
        if not found:
            eargs = [outfile.name]
            WLOG(params, 'error', textentry('00-010-00003', args=eargs))
        if skip:
            if os.path.exists(outfile.filename):
                wargs = [infile.filename]
                WLOG(params, 'info', textentry('40-010-00012', args=wargs))
                continue

        # ----------------------------------------------------------------------
        # Check for pixel shift and/or corrupted files
        # ----------------------------------------------------------------------
        # storage
        snr_hotpix, rms_list = [], []
        shiftdx, shiftdy = 0, 0
        # do this iteratively as if there is a shift need to re-workout QC
        for iteration in range(2):
            # get pass condition
            cout = prep.test_for_corrupt_files(params, image, hotpixels)
            snr_hotpix, rms_list = cout[0], cout[1]
            shiftdx, shiftdy = int(cout[2]), int(cout[3])
            # use dx/dy to shift the image back to where the engineering flat
            #    is located
            if shiftdx != 0 and shiftdy != 0:
                # log process
                wmsg = textentry('40-010-00013', args=[shiftdx, shiftdy])
                WLOG(params, '', wmsg)
                # roll on the y axis
                image = np.roll(image, [shiftdy], axis=0)
                intercept = np.roll(intercept, [shiftdy], axis=0)
                errslope = np.roll(errslope, [shiftdy], axis=0)
                inttime = np.roll(inttime, [shiftdy], axis=0)
                # roll on the x axis
                image = np.roll(image, [shiftdx], axis=1)
                intercept = np.roll(intercept, [shiftdx], axis=1)
                errslope = np.roll(errslope, [shiftdx], axis=1)
                inttime = np.roll(inttime, [shiftdx], axis=1)
            elif shiftdx != 0:
                # log process
                wmsg = textentry('40-010-00013', args=[shiftdx, shiftdy])
                WLOG(params, '', wmsg)
                # roll on the x axis
                image = np.roll(image, [shiftdx], axis=1)
                intercept = np.roll(intercept, [shiftdx], axis=1)
                errslope = np.roll(errslope, [shiftdx], axis=1)
                inttime = np.roll(inttime, [shiftdx], axis=1)
            elif shiftdy != 0:
                # log process
                wmsg = textentry('40-010-00013', args=[shiftdx, shiftdy])
                WLOG(params, '', wmsg)
                # roll on the y axis
                image = np.roll(image, [shiftdy], axis=0)
                intercept = np.roll(intercept, [shiftdy], axis=0)
                errslope = np.roll(errslope, [shiftdy], axis=0)
                inttime = np.roll(inttime, [shiftdy], axis=0)
            # work out QC here
            qargs = [snr_hotpix, infile, rms_list]
            qc_params, passed = prep.quality_control(params, *qargs, log=False)
            # if passed break
            if passed:
                break

        # ------------------------------------------------------------------
        # Quality control to check for corrupt files
        # ------------------------------------------------------------------
        # re-calculate qc
        qargs = [snr_hotpix, infile, rms_list]
        qc_params, passed = prep.quality_control(params, *qargs, log=True)
        # update recipe log
        log1.add_qc(qc_params, passed)
        if not passed:
            # end log here
            log1.end()
            # go to next iteration
            continue

        # ------------------------------------------------------------------
        # correct image
        # ------------------------------------------------------------------
        # correct for the top and bottom reference pixels
        WLOG(params, '', textentry('40-010-00003'))
        image = prep.correct_top_bottom(params, image)
        # correct by a median filter from the dark amplifiers
        WLOG(params, '', textentry('40-010-00004'))
        image = prep.median_filter_dark_amps(params, image)
        # correct for the 1/f noise
        WLOG(params, '', textentry('40-010-00005'))
        image = prep.median_one_over_f_noise(params, image)

        # ----------------------------------------------------------------------
        # Correct for cosmic rays before the possible pixel shift
        # ----------------------------------------------------------------------
        # correct the intercept
        WLOG(params, '', textentry('40-010-00021'))
        intercept = prep.intercept_correct(intercept)
        # correct error slope
        WLOG(params, '', textentry('40-010-00022'))
        errslope1 = prep.errslope_correct(errslope)
        # correct cosmic rays
        WLOG(params, '', textentry('40-010-00018'))
        image, cprops = prep.correct_cosmics(params, image, intercept,
                                             errslope1, inttime)

        # ------------------------------------------------------------------
        # calculate mid observation time
        # ------------------------------------------------------------------
        mout = drs_file.get_mid_obs_time(params, infile.get_header())
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
        # set infiles
        outfile.infiles = [infile.basename]
        # add qc parameters
        outfile.add_qckeys(qc_params)
        # add dprtype
        outfile.add_hkey('KW_DPRTYPE', value=outfile.name)
        outfile.add_hkey('KW_OUTPUT', value=recipe.outputs['PP_FILE'].name)
        # add the shift that was used to correct the image
        outfile.add_hkey('KW_PPSHIFTX', value=shiftdx)
        outfile.add_hkey('KW_PPSHIFTY', value=shiftdy)
        # add mid observation time
        outfile.add_hkey('KW_MID_OBS_TIME', value=mid_obs_time.mjd)
        outfile.add_hkey('KW_MID_OBSTIME_METHOD', value=mid_obs_method)
        # add the cosmic correction keys
        outfile.add_hkey('KW_PPC_NBAD_INTE', value=cprops['NUM_BAD_INTERCEPT'])
        outfile.add_hkey('KW_PPC_NBAD_SLOPE', value=cprops['NUM_BAD_SLOPE'])
        outfile.add_hkey('KW_PPC_NBAD_BOTH', value=cprops['NUM_BAD_BOTH'])
        # ------------------------------------------------------------------
        # copy data
        outfile.data = image
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        wargs = [outfile.filename]
        WLOG(params, '', textentry('40-010-00009', args=wargs))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=outfile)]
            name_list += ['PARAM_TABLE']
        # ------------------------------------------------------------------
        # writefits image to file
        outfile.write_multi(data_list=data_list, name_list=name_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(outfile)
        # index this file
        drs_startup.end_main(params, None, recipe, success=True, outputs='pp',
                             end=False)
        # ------------------------------------------------------------------
        # append to output storage in p
        # ------------------------------------------------------------------
        output_names.append(outfile.filename)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end()

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, dict(locals()))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

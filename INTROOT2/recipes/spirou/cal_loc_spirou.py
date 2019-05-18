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
from terrapipe.science.calib import badpix
from terrapipe.science.calib import background
from terrapipe.science.calib import localisation

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_loc_spirou.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
PConstants = constants.pload(__INSTRUMENT__)
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
ORDERP_AB = file_definitions.out_loc_orderp_ab
ORDERP_C = file_definitions.out_loc_orderp_c
# alias pcheck
pcheck = config.pcheck


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
        combine = True
    else:
        combine = False
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
        # identify fiber type
        if dprtype == 'FLAT_DARK':
            params['FIBER'] = 'AB'
        elif dprtype == 'DARK_FLAT':
            params['FIBER'] = 'C'
        else:
            eargs = [dprtype, recipe.name, 'FLAT_DARK or DARK_FLAT',
                     infile.basename]
            WLOG(params, 'error', TextEntry('00-013-00001', args=eargs))
            params['FIBER'] = None
        params.set_source('FIBER', mainname)
        # get fiber parameters
        params = PConstants.FIBER_SETTINGS(params)

        # ------------------------------------------------------------------
        # Correction of DARK
        # ------------------------------------------------------------------
        # image 1 is corrected for dark
        params, image1 = dark.correction(params, image, header, len(rawfiles))

        # ------------------------------------------------------------------
        # Flip images
        # ------------------------------------------------------------------
        # image 2 is flipped (if required)
        if params['INPUT_FLIP_IMAGE']:
            # flip flat
            image2 = drs_fits.flip_image(params, image1)
        else:
            image2 = np.array(image1)

        # ------------------------------------------------------------------
        # Resize image
        # ------------------------------------------------------------------
        # image 2 is resized (if required)
        if params['INPUT_RESIZE_IMAGE']:
            # get resize size
            sargs = dict(xlow=params['IMAGE_X_LOW'],
                         xhigh=params['IMAGE_X_HIGH'],
                         ylow=params['IMAGE_Y_LOW'],
                         yhigh=params['IMAGE_Y_HIGH'])
            # resize flat
            image2 = drs_fits.resize(params, image2, **sargs)

        # ------------------------------------------------------------------
        # Correct for the BADPIX mask (set all bad pixels to NaNs)
        # ------------------------------------------------------------------
        # image 3 is corrected for bad pixels
        params, image3 = badpix.correction(params, image2, header)

        # ------------------------------------------------------------------
        # Background computation
        # ------------------------------------------------------------------
        # image 4 is corrected for background
        params, image4 = background.correction(recipe, params, infile,
                                               image3, header)

        # ------------------------------------------------------------------
        # Construct image order_profile
        # ------------------------------------------------------------------
        order_profile = localisation.calculate_order_profile(params, image4)

        # ------------------------------------------------------------------
        # Localization of orders on central column
        # ------------------------------------------------------------------
        largs = [order_profile, sigdet]
        lout = localisation.find_and_fit_localisation(params, *largs)
        # get parameters from lout
        cent_0, cent_coeffs, cent_rms, cent_max_ptp = lout[:4]
        cent_frac_ptp, cent_max_rmpts = lout[4:6]
        wid_0, wid_coeffs, wid_rms, wid_max_ptp = lout[6:10]
        wid_frac_ptp, wid_max_rmpts, xplot, yplot = lout[10:]

        # ------------------------------------------------------------------
        # Plot the image (ready for fit points to be overplotted later)
        # ------------------------------------------------------------------
        # Plot the image (ready for fit points to be overplotted later)
        if params['DRS_PLOT'] > 0:
            # get saturation threshold
            sat_thres = pcheck(params, 'LOC_SAT_THRES') * gain * num_files
            # plot image above saturation threshold
            # TODO: Add sPlt.locplot_im_sat_threshold(p, loc, data2, sat_thres)

        # ------------------------------------------------------------------
        # Plot of RMS for positions and widths
        # ------------------------------------------------------------------
        if params['DRS_PLOT'] > 0:
            # TODO: Add sPlt.locplot_order_number_against_rms(p, loc, rorder_num)
            pass

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        # set passed variable and fail message list
        fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])

        # TODO: complete

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

        # ------------------------------------------------------------------
        # Write image order_profile to file
        # ------------------------------------------------------------------
        if params['FIBER'] == 'AB':
            orderpfile = ORDERP_AB.newcopy(recipe=recipe)
        else:
            orderpfile = ORDERP_C.newcopy(recipe=recipe)
        # construct the filename from file instance
        orderpfile.construct_filename(params, infile=infile)
        # define header keys for output file
        # copy keys from input file
        orderpfile.copy_original_keys(infile)
        # add version
        orderpfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add process id
        orderpfile.add_hkey('KW_PID', value=params['PID'])
        # add output tag
        orderpfile.add_hkey('KW_OUTPUT', value=orderpfile.name)
        # add input files (and deal with combining or not combining)
        if combine:
            hfiles = rawfiles
        else:
            hfiles = [infile.basename]
        orderpfile.add_hkey_1d('KW_INFILE1', values=rawfiles, dim1name='file')
        # add qc parameters
        orderpfile.add_qckeys(qc_params)
        # copy data
        orderpfile.data = order_profile
        # log that we are saving rotated image
        WLOG(params, '', TextEntry('40-013-00002', args=[orderpfile.filename]))
        # write image to file
        orderpfile.write()

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
        if params['QC']:
            drs_database.add_file(params, orderpfile)

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

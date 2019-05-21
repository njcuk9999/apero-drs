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
from terrapipe.config import math
from terrapipe.config.core import drs_database
from terrapipe.config.instruments.spirou import file_definitions
from terrapipe.io import drs_fits
from terrapipe.io import drs_image
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

LOCO1_AB = file_definitions.out_loc_loco_ab
LOCO1_C =file_definitions.out_loc_loco_c
LOCO2_AB = file_definitions.out_loc_loco_2_ab
LOCO2_C = file_definitions.out_loc_loco_2c
LOCO3_AB = file_definitions.out_loc_loco_3_ab
LOCO3_C = file_definitions.out_loc_loco_3_c

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
            image2 = drs_image.flip_image(params, image1)
        else:
            image2 = np.array(image1)

        # ------------------------------------------------------------------
        #  Convert ADU/s to electrons
        # ------------------------------------------------------------------
        image2 = drs_image.convert_to_e(params, image2)

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
            image2 = drs_image.resize(params, image2, **sargs)

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
        wid_frac_ptp, wid_max_rmpts, xplot, yplot = lout[10:14]
        rorder_num, mean_rms_cent, mean_rms_wid = lout[14:]

        # ------------------------------------------------------------------
        # Use the fits the calculate pixel fit values
        # ------------------------------------------------------------------
        center_fits = math.calculate_polyvals(cent_coeffs, image4.shape[1])
        width_fits = math.calculate_polyvals(wid_coeffs, image4.shape[1])

        # ------------------------------------------------------------------
        # Plot the image (ready for fit points to be overplotted later)
        # ------------------------------------------------------------------
        # Plot the image (ready for fit points to be overplotted later)
        if params['DRS_PLOT'] > 0:
            # get saturation threshold
            loc_sat_thres = pcheck(params, 'LOC_SAT_THRES', func=mainname)
            sat_thres = loc_sat_thres * gain * num_files
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
        # get qc parameters
        max_removed_cent = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_CTR',
                                  func=mainname)
        max_removed_wid = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_WID',
                                 func=mainname)
        rmsmax_cent = pcheck(params, 'QC_LOC_RMSMAX_CTR', func=mainname)
        rmsmax_wid = pcheck(params, 'QC_LOC_RMSMAX_WID', func=mainname)
        required_norders = pcheck(params, 'FIBER_MAX_NUM_ORDERS', func=mainname)
        # ----------------------------------------------------------------------
        # check that max number of points rejected in center fit is below
        #    threshold
        if np.nansum(cent_max_rmpts) > max_removed_cent:
            # add failed message to fail message list
            fargs = [np.nansum(cent_max_rmpts), max_removed_cent]
            fail_msg.append(textdict['40-013-00014'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(np.nansum(cent_max_rmpts))
        qc_names.append('sum(MAX_RMPTS_POS')
        qc_logic.append('sum(MAX_RMPTS_POS) < {0:.2f}'.format(cent_max_rmpts))
        # ----------------------------------------------------------------------
        # check that  max number of points rejected in width fit is below
        #   threshold
        if np.nansum(wid_max_rmpts) > max_removed_wid:
            # add failed message to fail message list
            fargs = [np.nansum(cent_max_rmpts), max_removed_wid]
            fail_msg.append(textdict['40-013-00015'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(np.nansum(wid_max_rmpts))
        qc_names.append('sum(MAX_RMPTS_WID)')
        qc_logic.append('sum(MAX_RMPTS_WID) < {0:.2f}'.format(max_removed_wid))
        # ------------------------------------------------------------------
        if mean_rms_cent > rmsmax_cent:
            # add failed message to fail message list
            fargs = [mean_rms_cent, rmsmax_cent]
            fail_msg.append(textdict['40-013-00016'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(mean_rms_cent)
        qc_names.append('mean_rms_center')
        qc_logic.append('mean_rms_center < {0:.2f}'.format(rmsmax_cent))
        # ------------------------------------------------------------------
        if mean_rms_wid > rmsmax_wid:
            # add failed message to fail message list
            fargs = [mean_rms_wid, rmsmax_wid]
            fail_msg.append(textdict['40-013-00017'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(mean_rms_wid)
        qc_names.append('mean_rms_wid')
        qc_logic.append('mean_rms_wid < {0:.2f}'.format(rmsmax_wid))
        # ------------------------------------------------------------------
        # check for abnormal number of identified orders
        if rorder_num != required_norders:
            # add failed message to fail message list
            fargs = [rorder_num, required_norders]
            fail_msg.append(textdict['40-013-00018'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(rorder_num)
        qc_names.append('rorder_num')
        qc_logic.append('rorder_num != {0}'.format(required_norders))
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
        loco1file = LOCO1_AB.newcopy(recipe=recipe)
        # construct the filename from file instance
        loco1file.construct_filename(params, infile=infile)
        # ------------------------------------------------------------------
        # define header keys for output file
        # copy keys from input file
        loco1file.copy_original_keys(infile)
        # add version
        loco1file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add output tag
        loco1file.add_hkey('KW_OUTPUT', value=loco1file.name)
        # add input files (and deal with combining or not combining)
        if combine:
            hfiles = rawfiles
        else:
            hfiles = [infile.basename]
        loco1file.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
        # add the calibration files use
        loco1file.add_hkey('KW_CDBDARK', value=params['DARKFILE'])
        loco1file.add_hkey('KW_CDBBAD', value=params['BADPFILE'])
        loco1file.add_hkey('KW_CDBBACK', value=params['BACKFILE'])
        # add localisation parameters

        # TODO: complete

        # add qc parameters
        loco1file.add_qckeys(qc_params)
        # copy data
        loco1file.data = center_fits
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        WLOG(params, '', TextEntry('40-013-00019', args=[loco1file.filename]))
        # write image to file
        loco1file.write()

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

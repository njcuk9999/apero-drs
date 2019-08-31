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

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core import math
from terrapipe.core.core import drs_database
from terrapipe.core.instruments.spirou import file_definitions
from terrapipe.io import drs_fits
from terrapipe.science.calib import general
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
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


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
    Main function for cal_loc_spirou.py

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
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.header
        # get calibrations for this data
        drs_database.copy_calibrations(params, header)

        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = general.calibrate_ppfile(params, recipe, infile)

        # ------------------------------------------------------------------
        # Identify fiber type
        # ------------------------------------------------------------------
        # identify fiber type based on data type
        if props['DPRTYPE'] == 'FLAT_DARK':
            fiber = 'AB'
        elif props['DPRTYPE'] == 'DARK_FLAT':
            fiber = 'C'
        else:
            eargs = [props['DPRTYPE'], recipe.name, 'FLAT_DARK or DARK_FLAT',
                     infile.basename]
            WLOG(params, 'error', TextEntry('00-013-00001', args=eargs))
            fiber = None

        # ------------------------------------------------------------------
        # Construct image order_profile
        # ------------------------------------------------------------------
        order_profile = localisation.calculate_order_profile(params, image)

        # ------------------------------------------------------------------
        # Localization of orders on central column
        # ------------------------------------------------------------------
        # find and fit localisation
        largs = [order_profile, props['SIGDET'], fiber]
        lout = localisation.find_and_fit_localisation(params, *largs)
        # get parameters from lout
        cent_0, cent_coeffs, cent_rms, cent_max_ptp = lout[:4]
        cent_frac_ptp, cent_max_rmpts = lout[4:6]
        wid_0, wid_coeffs, wid_rms, wid_max_ptp = lout[6:10]
        wid_frac_ptp, wid_max_rmpts, xplot, yplot = lout[10:14]
        rorder_num, mean_rms_cent, mean_rms_wid = lout[14:17]
        max_signal, mean_backgrd = lout[17:]

        # ------------------------------------------------------------------
        # Use the fits the calculate pixel fit values
        # ------------------------------------------------------------------
        center_fits = math.calculate_polyvals(cent_coeffs, image.shape[1])
        width_fits = math.calculate_polyvals(wid_coeffs, image.shape[1])

        # ------------------------------------------------------------------
        # Plot the image (ready for fit points to be overplotted later)
        # ------------------------------------------------------------------
        # Plot the image (ready for fit points to be overplotted later)
        if params['DRS_PLOT'] > 0:
            # get saturation threshold
            loc_sat_thres = pcheck(params, 'LOC_SAT_THRES', func=mainname)
            sat_thres = loc_sat_thres * props['GAIN'] * num_files
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
        # this one comes from pseudo constants
        pconst = constants.pload(params['INSTRUMENT'])
        fiberparams = pconst.FIBER_SETTINGS(params, fiber)

        required_norders = pcheck(params, 'FIBER_MAX_NUM_ORDERS', func=mainname,
                                  paramdict=fiberparams)
        # ----------------------------------------------------------------------
        # check that max number of points rejected in center fit is below
        #    threshold
        sum_cent_max_rmpts = np.nansum(cent_max_rmpts)
        if sum_cent_max_rmpts > max_removed_cent:
            # add failed message to fail message list
            fargs = [sum_cent_max_rmpts, max_removed_cent]
            fail_msg.append(textdict['40-013-00014'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(sum_cent_max_rmpts)
        qc_names.append('sum(MAX_RMPTS_POS')
        qc_logic.append('sum(MAX_RMPTS_POS) < {0:.2f}'
                        ''.format(sum_cent_max_rmpts))
        # ----------------------------------------------------------------------
        # check that  max number of points rejected in width fit is below
        #   threshold
        sum_wid_max_rmpts = np.nansum(wid_max_rmpts)
        if sum_wid_max_rmpts > max_removed_wid:
            # add failed message to fail message list
            fargs = [sum_wid_max_rmpts, max_removed_wid]
            fail_msg.append(textdict['40-013-00015'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(sum_wid_max_rmpts)
        qc_names.append('sum(MAX_RMPTS_WID)')
        qc_logic.append('sum(MAX_RMPTS_WID) < {0:.2f}'
                        ''.format(sum_wid_max_rmpts))
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
        #    quality control QC = 0 if we fail quality control
        if np.sum(qc_pass) == len(qc_pass):
            WLOG(params, 'info', TextEntry('40-005-10001'))
            passed = 1
        else:
            for farg in fail_msg:
                WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
            passed = 0
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

        # ------------------------------------------------------------------
        # Write image order_profile to file
        # ------------------------------------------------------------------
        # get a new copy to the order profile
        orderpfile = recipe.outputs['ORDERP_FILE'].newcopy(recipe=recipe,
                                                           fiber=fiber)
        # construct the filename from file instance
        orderpfile.construct_filename(params, infile=infile)
        # define header keys for output file
        # copy keys from input file
        orderpfile.copy_original_keys(infile)
        # add version
        orderpfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add dates
        orderpfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
        orderpfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
        # add process id
        orderpfile.add_hkey('KW_PID', value=params['PID'])
        # add output tag
        orderpfile.add_hkey('KW_OUTPUT', value=orderpfile.name)
        # add input files (and deal with combining or not combining)
        if combine:
            hfiles = rawfiles
        else:
            hfiles = [infile.basename]
        orderpfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
        # add the calibration files use
        orderpfile = general.add_calibs_to_header(orderpfile, props)
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
        loco1file = recipe.outputs['LOCO_FILE'].newcopy(recipe=recipe,
                                                        fiber=fiber)
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
        loco1file = general.add_calibs_to_header(loco1file, props)
        # add localisation parameters
        loco1file.add_hkey('KW_LOC_BCKGRD', value=mean_backgrd)
        loco1file.add_hkey('KW_LOC_NBO', value=rorder_num)
        loco1file.add_hkey('KW_LOC_DEG_C', value=params['LOC_CENT_POLY_DEG'])
        loco1file.add_hkey('KW_LOC_DEG_W', value=params['LOC_WIDTH_POLY_DEG'])
        loco1file.add_hkey('KW_LOC_MAXFLX', value=max_signal)
        loco1file.add_hkey('KW_LOC_SMAXPTS_CTR', value=max_removed_cent)
        loco1file.add_hkey('KW_LOC_SMAXPTS_WID', value=max_removed_wid)
        loco1file.add_hkey('KW_LOC_RMS_CTR', value=rmsmax_cent)
        loco1file.add_hkey('KW_LOC_RMS_WID', value=rmsmax_wid)
        # write 2D list of position fit coefficients
        loco1file.add_hkeys_2d('KW_LOC_CTR_COEFF', values=cent_coeffs,
                               dim1name='order', dim2name='coeff')
        # write 2D list of width fit coefficients
        loco1file.add_hkeys_2d('KW_LOC_WID_COEFF', values=wid_coeffs,
                               dim1name='order', dim2name='coeff')
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
        loco2file = recipe.outputs['FWHM_FILE'].newcopy(recipe=recipe,
                                                        fiber=fiber)
        # construct the filename from file instance
        loco2file.construct_filename(params, infile=infile)
        # ------------------------------------------------------------------
        # define header keys for output file
        # copy keys from loco1file
        loco2file.copy_hdict(loco1file)
        # copy data
        loco2file.data = width_fits
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        WLOG(params, '', TextEntry('40-013-00020', args=[loco2file.filename]))
        # write image to file
        loco2file.write()

        # ------------------------------------------------------------------
        # Save and Record of image of localization
        # ------------------------------------------------------------------
        if params['LOC_SAVE_SUPERIMP_FILE']:
            # --------------------------------------------------------------
            # super impose zeros over the fit in the image
            image5 = localisation.image_superimp(image, cent_coeffs)
            # --------------------------------------------------------------
            loco3file = recipe.outputs['SUP_FILE'].newcopy(recipe=recipe,
                                                           fiber=fiber)
            # construct the filename from file instance
            loco3file.construct_filename(params, infile=infile)
            # --------------------------------------------------------------
            # define header keys for output file
            # copy keys from loco1file
            loco3file.copy_hdict(loco1file)
            # copy data
            loco3file.data = image5
            # --------------------------------------------------------------
            # log that we are saving rotated image
            wargs = [loco3file.filename]
            WLOG(params, '', TextEntry('40-013-00021', args=wargs))
            # write image to file
            loco3file.write()

        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if passed:
            # copy the order profile to the calibDB
            drs_database.add_file(params, orderpfile)
            # copy the loco file to the calibDB
            drs_database.add_file(params, loco1file)

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
    # Post main plot clean up
    core.post_main(ll['params'], has_plots=True)

# =============================================================================
# End of code
# =============================================================================

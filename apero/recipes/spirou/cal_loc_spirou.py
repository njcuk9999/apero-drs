#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-14 at 09:40

@author: cook
"""
from apero.base import base
from apero import core
from apero import lang
from apero.core import constants
from apero.core import math as mp
from apero.core.utils import drs_database2 as drs_database
from apero.io import drs_fits
from apero.science.calib import general
from apero.science.calib import localisation


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_loc_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


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
        infiles = [drs_fits.combine(params, recipe, infiles, math='median')]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', it)
        # ------------------------------------------------------------------
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.header

        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = general.calibrate_ppfile(params, recipe, infile,
                                                database=calibdbm)

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
        lout = localisation.find_and_fit_localisation(params, recipe, *largs)

        # get parameters from lout
        cent_0, cent_coeffs, cent_rms, cent_max_ptp = lout[:4]
        cent_frac_ptp, cent_max_rmpts = lout[4:6]
        wid_0, wid_coeffs, wid_rms, wid_max_ptp = lout[6:10]
        wid_frac_ptp, wid_max_rmpts, xplot, yplot = lout[10:14]
        rorder_num, mean_rms_cent, mean_rms_wid = lout[14:17]
        max_signal, mean_backgrd = lout[17:]

        # ------------------------------------------------------------------
        # Clean the coefficients (using a sanity check)
        # ------------------------------------------------------------------
        # clean the center position fits
        cargs = [image, cent_coeffs, fiber, 'center']
        cent_coeffs = localisation.check_coeffs(params, recipe, *cargs)
        # clean the width fits
        wargs = [image, wid_coeffs, fiber, 'width']
        wid_coeffs = localisation.check_coeffs(params, recipe, *wargs)

        # ------------------------------------------------------------------
        # Use the fits the calculate pixel fit values
        # ------------------------------------------------------------------
        center_fits = mp.calculate_polyvals(cent_coeffs, image.shape[1])
        width_fits = mp.calculate_polyvals(wid_coeffs, image.shape[1])

        # ------------------------------------------------------------------
        # Plot the image and fit points
        # ------------------------------------------------------------------
        # get saturation threshold
        loc_sat_thres = params['LOC_SAT_THRES']
        sat_thres = loc_sat_thres * props['GAIN'] * num_files

        # plot image above saturation threshold
        recipe.plot('LOC_IM_SAT_THRES', image=image, xarr=xplot, yarr=yplot,
                    threshold=sat_thres, coeffs=cent_coeffs)
        # ------------------------------------------------------------------
        # Plot of RMS for positions and widths
        # ------------------------------------------------------------------
        recipe.plot('LOC_ORD_VS_RMS', rnum=rorder_num, fiber=fiber,
                    rms_center=cent_rms, rms_fwhm=wid_rms)

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        qargs = [fiber, cent_max_rmpts, wid_max_rmpts, mean_rms_cent,
                 mean_rms_wid, rorder_num, center_fits]

        qc_params, passed = localisation.loc_quality_control(params, *qargs)
        # update recipe log
        log1.add_qc(params, qc_params, passed)

        # ------------------------------------------------------------------
        # write files
        # ------------------------------------------------------------------
        fargs = [infile, image, rawfiles, combine, fiber, props, order_profile,
                 mean_backgrd, rorder_num, max_signal, cent_coeffs,
                 wid_coeffs, center_fits, width_fits, qc_params]
        outfiles = localisation.write_localisation_files(params, recipe, *fargs)
        orderpfile, loco1file = outfiles

        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if passed:
            # copy the order profile to the calibDB
            calibdbm.add_calib_file(orderpfile)
            # copy the loco file to the calibDB
            calibdbm.add_calib_file(loco1file)
        # ------------------------------------------------------------------
        # Summary plots
        # ------------------------------------------------------------------
        recipe.plot('SUM_LOC_IM_THRES', image=image, xarr=xplot, yarr=yplot,
                    threshold=sat_thres, coeffs=cent_coeffs)
        recipe.plot('SUM_LOC_IM_CORNER', image=image, xarr=xplot, yarr=yplot,
                    threshold=sat_thres, params=params, coeffs=cent_coeffs)
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        localisation.loc_summary(recipe, it, params, qc_params, props,
                                 mean_backgrd, rorder_num, max_signal)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end(params)

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

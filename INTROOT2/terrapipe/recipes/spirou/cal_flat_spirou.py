#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:45

@author: cook
"""
from __future__ import division
import numpy as np
import warnings

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.core.instruments.spirou import file_definitions
from terrapipe.io import drs_fits
from terrapipe.io import drs_image
from terrapipe.science.calib import general
from terrapipe.science.calib import localisation
from terrapipe.science.calib import shape
from terrapipe.science.calib import wave
from terrapipe.science import extract

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_flat_spirou.py'
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
FLAT_FILE = file_definitions.out_ff_flat
BLAZE_FILE = file_definitions.out_ff_blaze
E2DSLL_FILE = file_definitions.out_ext_e2dsll
ORDERP_SFILE = file_definitions.out_orderp_straight


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
    Main function for cal_flat_spirou.py

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
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.header
        # get calibrations for this data
        drs_database.copy_calibrations(params, header)
        # get the fiber types needed
        fibertypes = drs_image.get_fiber_types(params)

        # ------------------------------------------------------------------
        # Load shape components
        # ------------------------------------------------------------------
        shapexfile, shapex = shape.get_shapex(params, header)
        shapeyfile, shapey = shape.get_shapey(params, header)
        shapelocalfile, shapelocal = shape.get_shapelocal(params, header)

        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = general.calibrate_ppfile(params, recipe, infile)

        # ------------------------------------------------------------------
        # Load and straighten order profiles
        # ------------------------------------------------------------------
        sargs = [infile, fibertypes, shapelocal, shapex, shapey, ORDERP_SFILE]
        orderps, orderpfiles = extract.order_profiles(params, recipe, *sargs)

        # ------------------------------------------------------------------
        # Apply shape transformations
        # ------------------------------------------------------------------
        # log progress (straightening orderp)
        WLOG(params, 'info', TextEntry('40-016-00004'))
        # straighten image
        image2 = shape.ea_transform(params, image, shapelocal, dxmap=shapex,
                                    dymap=shapey)

        # ------------------------------------------------------------------
        # Fiber loop
        # ------------------------------------------------------------------
        # loop around fiber types
        for fiber in fibertypes:
            # push fiber into params
            params['FIBER'] = fiber
            params.set_source('FIBER', mainname)
            # --------------------------------------------------------------
            # load the localisation properties for this fiber
            lprops = localisation.get_coefficients(params, recipe, header,
                                                   fiber=fiber, merge=True)
            # get the localisation center coefficients for this fiber
            lcoeffs = lprops['CENT_COEFFS']
            # --------------------------------------------------------------
            # get the number of frames used
            nframes = infile.numfiles
            # --------------------------------------------------------------
            # get the order profile for this fiber
            orderp = orderps[fiber]
            orderpfile = orderpfiles[fiber]
            # --------------------------------------------------------------
            # extract spectrum
            eprops = extract.extract2d(params, image2, orderp, lcoeffs, nframes,
                                       props, kind='flat')

            # --------------------------------------------------------------
            # Plots
            # --------------------------------------------------------------
            if params['DRS_PLOT'] > 0:
                # TODO fill in
                # # start interactive session if needed
                # sPlt.start_interactive_session(p)
                # # plot all orders or one order
                # if p['IC_FF_PLOT_ALL_ORDERS']:
                #     # plot image with all order fits (slower)
                #     sPlt.ff_aorder_fit_edges(p, loc, data1)
                # else:
                #     # plot image with selected order fit and edge fit (faster)
                #     sPlt.ff_sorder_fit_edges(p, loc, data1)
                # # plot tilt adjusted e2ds and blaze for selected order
                # sPlt.ff_sorder_tiltadj_e2ds_blaze(p, loc)
                # # plot flat for selected order
                # sPlt.ff_sorder_flat(p, loc)
                # # plot the RMS for all but skipped orders
                # # sPlt.ff_rms_plot(p, loc)
                #
                # if p['IC_FF_EXTRACT_TYPE'] in EXTRACT_SHAPE_TYPES:
                #     sPlt.ff_debanana_plot(p, loc, data2)
                pass

            # --------------------------------------------------------------
            # Quality control
            # --------------------------------------------------------------
            # set passed variable and fail message list
            fail_msg, qc_values, qc_names = [], [], [],
            qc_logic, qc_pass = [], []
            textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
            # --------------------------------------------------------------
            # check that rms values in required orders are below threshold

            # get mask for removing certain values
            remove_orders = params.listp('FF_RMS_SKIP_ORDERS', dtype=int)
            remove_orders = np.array(remove_orders)
            remove_mask = np.in1d(np.arange(len(eprops['RMS'])), remove_orders)
            # apply max and calculate the maximum of the rms values
            max_rms = np.nanmax(eprops['RMS'][~remove_mask])
            # apply the quality control based on the maximum rms
            if max_rms > params['QC_FF_MAX_RMS']:
                # add failed message to fail message list
                fargs = [fiber, max_rms, params['QC_FF_MAX_RMS']]
                fail_msg.append(textdict['40-015-00008'].format(*fargs))
                qc_pass.append(0)
            else:
                qc_pass.append(1)
            # add to qc header lists
            qc_values.append(max_rms)
            qc_names.append('max_rms')
            qc_logic.append('max_rms < {0:.2f}'.format(params['QC_FF_MAX_RMS']))
            # --------------------------------------------------------------
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

            # --------------------------------------------------------------
            # Store Blaze in file
            # --------------------------------------------------------------
            # get a new copy of the blaze file
            blazefile = BLAZE_FILE.newcopy(recipe=recipe, fiber=fiber)
            # construct the filename from file instance
            blazefile.construct_filename(params, infile=infile)
            # define header keys for output file
            # copy keys from input file
            blazefile.copy_original_keys(infile)
            # add version
            blazefile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
            # add dates
            blazefile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
            blazefile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
            # add process id
            blazefile.add_hkey('KW_PID', value=params['PID'])
            # add output tag
            blazefile.add_hkey('KW_OUTPUT', value=blazefile.name)
            # add input files (and deal with combining or not combining)
            if combine:
                hfiles = rawfiles
            else:
                hfiles = [infile.basename]
            blazefile.add_hkey_1d('KW_INFILE1', values=hfiles,
                                  dim1name='file')
            # add qc parameters
            blazefile.add_qckeys(qc_params)
            # add the calibration files use
            blazefile = general.add_calibs_to_header(blazefile, props)
            # --------------------------------------------------------------
            # add the other calibration files used
            blazefile.add_hkey('KW_CDBORDP', value=orderpfile)
            blazefile.add_hkey('KW_CDBLOCO', value=lprops['LOCOFILE'])
            blazefile.add_hkey('KW_CDBSHAPEL', value=shapelocalfile)
            blazefile.add_hkey('KW_CDBSHAPEDX', value=shapexfile)
            blazefile.add_hkey('KW_CDBSHAPEDY', value=shapeyfile)
            # --------------------------------------------------------------
            # add SNR parameters to header
            blazefile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                                  dim1name='order')
            # add start and end extraction order used
            blazefile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
            blazefile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
            # add extraction ranges used
            blazefile.add_hkey('KW_EXT_RANGE1', value=eprops['RANGE1'])
            blazefile.add_hkey('KW_EXT_RANGE2', value=eprops['RANGE2'])
            # add cosmic parameters used
            blazefile.add_hkey('KW_COSMIC', value=eprops['COSMIC'])
            blazefile.add_hkey('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'])
            blazefile.add_hkey('KW_COSMIC_THRES',
                               value=eprops['COSMIC_THRESHOLD'])
            # add blaze parameter used
            blazefile.add_hkey('KW_BLAZE_WID', value=eprops['BLAZE_SIZE'])
            blazefile.add_hkey('KW_BLAZE_CUT', value=eprops['BLAZE_CUT'])
            blazefile.add_hkey('KW_BLAZE_DEG', value=eprops['BLAZE_DEG'])
            # add saturation parameters used
            blazefile.add_hkey('KW_SAT_QC', value=eprops['SAT_LEVEL'])
            with warnings.catch_warnings(record=True) as _:
                max_sat_level = np.nanmax(eprops['FLUX_VAL'])
            blazefile.add_hkey('KW_SAT_LEVEL', value=max_sat_level)
            # --------------------------------------------------------------
            # copy data
            blazefile.data = eprops['BLAZE']
            # --------------------------------------------------------------
            # log that we are saving rotated image
            WLOG(params, '',
                 TextEntry('40-015-00003', args=[blazefile.filename]))
            # write image to file
            blazefile.write()

            # --------------------------------------------------------------
            # Store Flat-field in file
            # --------------------------------------------------------------
            # get a new copy of the blaze file
            flatfile = FLAT_FILE.newcopy(recipe=recipe, fiber=fiber)
            # construct the filename from file instance
            flatfile.construct_filename(params, infile=infile)
            # copy header from blaze file
            flatfile.copy_hdict(blazefile)
            # copy data
            flatfile.data = eprops['FLAT']
            # --------------------------------------------------------------
            # log that we are saving rotated image
            WLOG(params, '',
                 TextEntry('40-015-00004', args=[flatfile.filename]))
            # write image to file
            flatfile.write()

            # --------------------------------------------------------------
            # Store E2DSLL in file
            # --------------------------------------------------------------
            # get a new copy of the blaze file
            e2dsllfile = E2DSLL_FILE.newcopy(recipe=recipe, fiber=fiber)
            # construct the filename from file instance
            e2dsllfile.construct_filename(params, infile=infile)
            # copy header from blaze file
            e2dsllfile.copy_hdict(blazefile)
            # copy data
            e2dsllfile.data = eprops['E2DSLL']
            # --------------------------------------------------------------
            # log that we are saving rotated image
            WLOG(params, '',
                 TextEntry('40-015-00005', args=[e2dsllfile.filename]))
            # write image to file
            e2dsllfile.write()

            # --------------------------------------------------------------
            # Update the calibration database
            # --------------------------------------------------------------
            if params['QC']:
                # copy the blaze file to the calibDB
                drs_database.add_file(params, blazefile)
                # copy the flat file to the calibDB
                drs_database.add_file(params, flatfile)

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

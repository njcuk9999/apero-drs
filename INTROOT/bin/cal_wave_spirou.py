#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_wave_spirou.py [night_directory] [fitsfilename]

Wavelength calibration

Created on 2018-07-20
@author: hobson, artigau, cook
"""

from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouRV
from SpirouDRS import spirouTHORCA
from SpirouDRS.spirouTHORCA import spirouWAVE2

from astropy import constants as cc
from astropy import units as uu


# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_WAVE_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt
plt.ion()
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict

# TODO set up file input (Neil's fault)
has_fp = True

# =============================================================================
# Define functions
# =============================================================================


def main(night_name=None, fpfile=None, hcfiles=None):
    """
    cal_wave_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_wave_spirou.py [night_directory] [fpfile] [hcfiles]

    :param night_name: string or None, the folder within data reduced directory
                                containing files (also reduced directory) i.e.
                                /data/reduced/20170710 would be "20170710" but
                                /data/reduced/AT5/20180409 is "AT5/20180409"
    :param fpfile: string, or None, the FP file to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)
    :param hcfiles: string, list or None, the list of HC files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------

    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    if hcfiles is None or fpfile is None:
        names, types = ['fpfile', 'hcfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime(p, [0, 1], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(hcfiles=hcfiles, fpfile=fpfile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsdir='reduced',
                                    mainfitsfile='hcfiles')

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, fpfitsfilename = spirouStartup.SingleFileSetup(p, filename=p['FPFILE'])
    fiber1 = str(p['FIBER'])
    p, hcfilenames = spirouStartup.MultiFileSetup(p, files=p['HCFILES'])
    fiber2 = str(p['FIBER'])
    # set the hcfilename to the first hcfilenames
    hcfitsfilename = hcfilenames[0]

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Have to check that the fibers match
    # ----------------------------------------------------------------------
    if fiber1 == fiber2:
        p['FIBER'] = fiber1
        fsource = __NAME__ + '/main() & spirouStartup.GetFiberType()'
        p.set_source('FIBER', fsource)
    else:
        emsg = 'Fiber not matching for {0} and {1}, should be the same'
        eargs = [hcfitsfilename, fpfitsfilename]
        WLOG(p, 'error', emsg.format(*eargs))
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Read FP and HC files
    # ----------------------------------------------------------------------

    # read and combine all HC files except the first (fpfitsfilename)
    rargs = [p, 'add', hcfitsfilename, hcfilenames[1:]]
    p, hcdata, hchdr, hccdr = spirouImage.ReadImageAndCombine(*rargs)
    # read first file (fpfitsfilename)
    fpdata, fphdr, fpcdr, _, _ = spirouImage.ReadImage(p, fpfitsfilename)

    # add data and hdr to loc
    loc = ParamDict()
    loc['HCDATA'], loc['HCHDR'], loc['HCCDR'] = hcdata, hchdr, hccdr
    loc['FPDATA'], loc['FPHDR'], loc['FPCDR'] = fpdata, fphdr, fpcdr

    # set the source
    sources = ['HCDATA', 'HCHDR', 'HCCDR']
    loc.set_sources(sources, 'spirouImage.ReadImageAndCombine()')
    sources = ['FPDATA', 'FPHDR', 'FPCDR']
    loc.set_sources(sources, 'spirouImage.ReadImage()')

    # ----------------------------------------------------------------------
    # Get basic image properties for reference file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hchdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hchdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hchdr, name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, hchdr, name='acqtime', kind='julian')
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # get lamp parameters
    p = spirouWAVE2.get_lamp_parameters(p, hchdr)

    # get number of orders
    # we always get fibre A number because AB is doubled in constants file
    loc['NBO'] = p['QC_LOC_NBO_FPALL']['A']
    loc.set_source('NBO', __NAME__ + '.main()')
    # get number of pixels in x from hcdata size
    loc['NBPIX'] = loc['HCDATA'].shape[1]
    loc.set_source('NBPIX', __NAME__ + '.main()')

    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    p, loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hchdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')
    # make copy of blaze (as it's overwritten later in CCF part)
    # TODO is this needed? More sensible to make and set copy in CCF?
    loc['BLAZE2'] = np.copy(loc['BLAZE'])

    # ----------------------------------------------------------------------
    # Read wave solution
    # ----------------------------------------------------------------------
    # wavelength file; we will use the polynomial terms in its header,
    # NOT the pixel values that would need to be interpolated

    # set source of wave file
    wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # get wave image
    wout = spirouImage.GetWaveSolution(p, hdr=hchdr, return_wavemap=True,
                                       return_filename=True, fiber=wave_fiber)
    loc['WAVEPARAMS'], loc['WAVE_INIT'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    loc.set_sources(['WAVE_INIT', 'WAVEFILE', 'WAVEPARAMS', 'WSOURCE'], wsource)
    poly_wave_sol = loc['WAVEPARAMS']

    # ----------------------------------------------------------------------
    # Check that wave parameters are consistent with "ic_ll_degr_fit"
    # ----------------------------------------------------------------------
    loc = spirouImage.CheckWaveSolConsistency(p, loc)

    # ----------------------------------------------------------------------
    # HC wavelength solution
    # ----------------------------------------------------------------------
    # log that we are running the HC part and the mode
    wmsg = 'Now running the HC solution, mode = {0}'
    WLOG(p, 'info', wmsg.format(p['WAVE_MODE_HC']))

    # get the solution
    loc = spirouWAVE2.do_hc_wavesol(p, loc)

    # ----------------------------------------------------------------------
    # Quality control - HC solution
    # ----------------------------------------------------------------------

    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
    # quality control on sigma clip (sig1 > qc_hc_wave_sigma_max
    if loc['SIG1'] > p['QC_HC_WAVE_SIGMA_MAX']:
        fmsg = 'Sigma too high ({0:.5f} > {1:.5f})'
        fail_msg.append(fmsg.format(loc['SIG1'], p['QC_HC_WAVE_SIGMA_MAX']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(loc['SIG1'])
    qc_names.append('SIG1 HC')
    qc_logic.append('SIG1 > {0:.2f}'.format(p['QC_HC_WAVE_SIGMA_MAX']))
    # ----------------------------------------------------------------------
    # check the difference between consecutive orders is always positive
    # get the differences
    wave_diff = loc['WAVE_MAP2'][1:]-loc['WAVE_MAP2'][:-1]
    if np.min(wave_diff) < 0:
        fmsg = 'Negative wavelength difference between orders'
        fail_msg.append(fmsg)
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(np.min(wave_diff))
    qc_names.append('MIN WAVE DIFF HC')
    qc_logic.append('MIN WAVE DIFF < 0')

    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG(p, 'info', 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG(p, 'warning', wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # ----------------------------------------------------------------------
    # log the global stats
    # ----------------------------------------------------------------------

    # calculate catalog-fit residuals in km/s

    res_hc = []
    sumres_hc = 0.0
    sumres2_hc = 0.0

    for order in range(loc['NBO']):
        # get HC line wavelengths for the order
        order_mask = loc['ORD_T'] == order
        hc_x_ord = loc['XGAU_T'][order_mask]
        hc_ll_ord = np.polyval(loc['POLY_WAVE_SOL'][order][::-1], hc_x_ord)
        hc_ll_cat = loc['WAVE_CATALOG'][order_mask]
        hc_ll_diff = hc_ll_ord - hc_ll_cat
        res_hc.append(hc_ll_diff*speed_of_light/hc_ll_cat)
        sumres_hc += np.nansum(res_hc[order])
        sumres2_hc += np.nansum(res_hc[order] ** 2)

    total_lines_hc = len(np.concatenate(res_hc))
    final_mean_hc = sumres_hc/total_lines_hc
    final_var_hc = (sumres2_hc/total_lines_hc) - (final_mean_hc ** 2)
    wmsg1 = 'On fiber {0} HC fit line statistic:'.format(p['FIBER'])
    wargs2 = [final_mean_hc * 1000.0, np.sqrt(final_var_hc) * 1000.0,
              total_lines_hc, 1000.0 * np.sqrt(final_var_hc / total_lines_hc)]
    wmsg2 = ('\tmean={0:.3f}[m/s] rms={1:.1f} {2} HC lines (error on mean '
             'value:{3:.4f}[m/s])'.format(*wargs2))
    WLOG(p, 'info', [wmsg1, wmsg2])

    # ----------------------------------------------------------------------
    # Save wave map to file
    # ----------------------------------------------------------------------
    # TODO single file-naming function? Ask Neil
    # get base input filenames
    bfilenames = []
    for raw_file in p['ARG_FILE_NAMES']:
        bfilenames.append(os.path.basename(raw_file))
    # get wave filename
    wavefits, tag1 = spirouConfig.Constants.WAVE_FILE_EA(p)
    wavefitsname = os.path.basename(wavefits)
    # log progress
    WLOG(p, '', 'Saving wave map to {0}'.format(wavefitsname))
    # log progress
    wargs = [p['FIBER'], wavefitsname]
    wmsg = 'Write wavelength solution for Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(*wargs))
    # write solution to fitsfilename header
    # copy original keys
    hdict = spirouImage.CopyOriginalKeys(loc['HCHDR'], loc['HCCDR'])
    # set the version
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    # TODO add DRS_DATE and DRS_NOW
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
    # set the input files
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'], value=p['BLAZFILE'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # add wave solution date
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME1'],
                               value=p['MAX_TIME_HUMAN'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME2'],
                               value=p['MAX_TIME_UNIX'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_CODE'], value=__NAME__)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'], value=loc['WAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['ARG_FILE_NAMES'])
    # add number of orders
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_ORD_N'],
                               value=loc['POLY_WAVE_SOL'].shape[0])
    # add degree of fit
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_LL_DEG'],
                               value=loc['POLY_WAVE_SOL'].shape[1]-1)
    # add wave solution
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                     values=loc['POLY_WAVE_SOL'])
    # write the wave "spectrum"
    p = spirouImage.WriteImage(p, wavefits, loc['WAVE_MAP2'], hdict)

    # get filename for E2DS calibDB copy of FITSFILENAME
    e2dscopy_filename, tag2 = spirouConfig.Constants.WAVE_E2DS_COPY(p)

    wargs = [p['FIBER'], os.path.split(e2dscopy_filename)[-1]]
    wmsg = 'Write reference E2DS spectra for Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(*wargs))

    # make a copy of the E2DS file for the calibBD
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
    p = spirouImage.WriteImage(p, e2dscopy_filename, loc['HCDATA'], hdict)

    # ----------------------------------------------------------------------
    # Save resolution and line profiles to file
    # ----------------------------------------------------------------------
    raw_infile = os.path.basename(p['FITSFILENAME'])
    # get wave filename
    resfits, tag3 = spirouConfig.Constants.WAVE_RES_FILE_EA(p)
    resfitsname = os.path.basename(resfits)
    WLOG(p, '', 'Saving wave resmap to {0}'.format(resfitsname))

    # make a copy of the E2DS file for the calibBD
    # set the version
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    # TODO add DRS_DATE and DRS_NOW
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)

    # get res data in correct format
    resdata, hdicts = spirouWAVE2.generate_res_files(p, loc, hdict)
    # save to file
    p = spirouImage.WriteImageMulti(p, resfits, resdata, hdicts=hdicts)

    # ----------------------------------------------------------------------
    # Update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        # set the wave key
        keydb = 'WAVE_{0}'.format(p['FIBER'])
        # copy wave file to calibDB folder
        spirouDB.PutCalibFile(p, wavefits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, wavefitsname, loc['HCHDR'])

        # set the hcref key
        keydb = 'HCREF_{0}'.format(p['FIBER'])
        # copy wave file to calibDB folder
        spirouDB.PutCalibFile(p, e2dscopy_filename)
        # update the master calib DB file with new key
        e2dscopyfits = os.path.split(e2dscopy_filename)[-1]
        spirouDB.UpdateCalibMaster(p, keydb, e2dscopyfits, loc['HCHDR'])

    # ----------------------------------------------------------------------
    # Update header of current files
    # ----------------------------------------------------------------------
    # only copy over if QC passed
    if p['QC']:
        rdir = os.path.dirname(wavefits)
        # loop around hc files and update header with
        for rawhcfile in p['ARG_FILE_NAMES']:
            hcfile = os.path.join(rdir, rawhcfile)
            raw_infilepath1 = os.path.join(p['ARG_FILE_DIR'], hcfile)
            p = spirouImage.UpdateWaveSolutionHC(p, loc, raw_infilepath1)

    # ----------------------------------------------------------------------
    # HC+FP wavelength solution
    # ----------------------------------------------------------------------
    # check if there's a FP input and if HC solution passed QCs
    if has_fp and p['QC']:
        # log that we are doing the FP solution
        wmsg = 'Now running the combined FP-HC solution, mode = {}'
        WLOG(p, 'info', wmsg.format(p['WAVE_MODE_FP']))
        # do the wavelength solution
        loc = spirouWAVE2.do_fp_wavesol(p, loc)

        # ----------------------------------------------------------------------
        # Quality control
        # ----------------------------------------------------------------------
        # get parameters ffrom p
        p['QC_RMS_LITTROW_MAX'] = p['QC_HC_RMS_LITTROW_MAX']
        p['QC_DEV_LITTROW_MAX'] = p['QC_HC_DEV_LITTROW_MAX']
        # set passed variable and fail message list
        # passed, fail_msg = True, []
        # qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
        # ----------------------------------------------------------------------
        # check the difference between consecutive orders is always positive
        # get the differences
        wave_diff = loc['LL_FINAL'][1:] - loc['LL_FINAL'][:-1]
        if np.min(wave_diff) < 0:
            fmsg = 'Negative wavelength difference between orders'
            fail_msg.append(fmsg)
            passed = False
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(np.min(wave_diff))
        qc_names.append('MIN WAVE DIFF FP-HC')
        qc_logic.append('MIN WAVE DIFF < 0')
        # ----------------------------------------------------------------------
        # check for infinites and NaNs in mean residuals from fit
        if ~np.isfinite(loc['X_MEAN_2']):
            # add failed message to the fail message list
            fmsg = 'NaN or Inf in X_MEAN_2'
            fail_msg.append(fmsg)
            passed = False
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(loc['X_MEAN_2'])
        qc_names.append('X_MEAN_2')
        qc_logic.append('X_MEAN_2 not finite')
        # ----------------------------------------------------------------------
        # iterate through Littrow test cut values
        lit_it = 2
        # checks every other value
        # TODO: This QC check (or set of QC checks needs re-writing it is
        # TODO:    nearly impossible to understand
        for x_it in range(1, len(loc['X_CUT_POINTS_' + str(lit_it)]), 2):
            # get x cut point
            x_cut_point = loc['X_CUT_POINTS_' + str(lit_it)][x_it]
            # get the sigma for this cut point
            sig_littrow = loc['LITTROW_SIG_' + str(lit_it)][x_it]
            # get the abs min and max dev littrow values
            min_littrow = abs(loc['LITTROW_MINDEV_' + str(lit_it)][x_it])
            max_littrow = abs(loc['LITTROW_MAXDEV_' + str(lit_it)][x_it])
            # get the corresponding order
            min_littrow_ord = loc['LITTROW_MINDEVORD_' + str(lit_it)][x_it]
            max_littrow_ord = loc['LITTROW_MAXDEVORD_' + str(lit_it)][x_it]
            # check if sig littrow is above maximum
            rms_littrow_max = p['QC_RMS_LITTROW_MAX']
            dev_littrow_max = p['QC_DEV_LITTROW_MAX']
            if sig_littrow > rms_littrow_max:
                fmsg = ('Littrow test (x={0}) failed (sig littrow = '
                        '{1:.2f} > {2:.2f})')
                fargs = [x_cut_point, sig_littrow, rms_littrow_max]
                fail_msg.append(fmsg.format(*fargs))
                passed = False
                qc_pass.append(0)
            else:
                qc_pass.append(1)
            # add to qc header lists
            qc_values.append(sig_littrow)
            qc_names.append('sig_littrow')
            qc_logic.append('sig_littrow > {0:.2f}'.format(rms_littrow_max))
            # ----------------------------------------------------------------------
            # check if min/max littrow is out of bounds
            if np.max([max_littrow, min_littrow]) > dev_littrow_max:
                fmsg = ('Littrow test (x={0}) failed (min|max dev = '
                        '{1:.2f}|{2:.2f} > {3:.2f} for order {4}|{5})')
                fargs = [x_cut_point, min_littrow, max_littrow, dev_littrow_max,
                         min_littrow_ord, max_littrow_ord]
                fail_msg.append(fmsg.format(*fargs))
                passed = False
                qc_pass.append(0)

                # TODO: Should this be the QC header values?
                # TODO:   it does not change the outcome of QC (i.e. passed=False)
                # TODO:   So what is the point?
                # if sig was out of bounds, recalculate
                if sig_littrow > rms_littrow_max:
                    # conditions
                    check1 = min_littrow > dev_littrow_max
                    check2 = max_littrow > dev_littrow_max
                    # get the residuals
                    respix = loc['LITTROW_YY_' + str(lit_it)][x_it]
                    # check if both are out of bounds
                    if check1 and check2:
                        # remove respective orders
                        worst_order = (min_littrow_ord, max_littrow_ord)
                        respix_2 = np.delete(respix, worst_order)
                        redo_sigma = True
                    # check if min is out of bounds
                    elif check1:
                        # remove respective order
                        worst_order = min_littrow_ord
                        respix_2 = np.delete(respix, worst_order)
                        redo_sigma = True
                    # check if max is out of bounds
                    elif check2:
                        # remove respective order
                        worst_order = max_littrow_ord
                        respix_2 = np.delete(respix, max_littrow_ord)
                        redo_sigma = True
                    # else do not recalculate sigma
                    else:
                        redo_sigma, respix_2, worst_order = False, None, None
                        wmsg = 'No outlying orders, sig littrow not recalculated'
                        fail_msg.append(wmsg.format())

                    # if outlying order, recalculate stats
                    if redo_sigma:
                        mean = np.nansum(respix_2) / len(respix_2)
                        mean2 = np.nansum(respix_2 ** 2) / len(respix_2)
                        rms = np.sqrt(mean2 - mean ** 2)
                        if rms > rms_littrow_max:
                            fmsg = ('Littrow test (x={0}) failed (sig littrow = '
                                    '{1:.2f} > {2:.2f} removing order {3})')
                            fargs = [x_cut_point, rms, rms_littrow_max, worst_order]
                            fail_msg.append(fmsg.format(*fargs))
                        else:
                            wargs = [x_cut_point, rms, rms_littrow_max, worst_order]
                            wmsg = ('Littrow test (x={0}) passed (sig littrow = '
                                    '{1:.2f} > {2:.2f} removing order {3})')
                            fail_msg.append(wmsg.format(*wargs))
            else:
                qc_pass.append(1)
            # add to qc header lists
            qc_values.append(np.max([max_littrow, min_littrow]))
            qc_names.append('max or min littrow')
            qc_logic.append('max or min littrow > {0:.2f}'
                            ''.format(dev_littrow_max))
        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if passed:
            WLOG(p, 'info',
                 'QUALITY CONTROL SUCCESSFUL - Well Done -')
            p['QC'] = 1
            p.set_source('QC', __NAME__ + '/main()')
        else:
            for farg in fail_msg:
                wmsg = 'QUALITY CONTROL FAILED: {0}'
                WLOG(p, 'warning', wmsg.format(farg))
            p['QC'] = 0
            p.set_source('QC', __NAME__ + '/main()')
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

        # ------------------------------------------------------------------
        # archive result in e2ds spectra
        # ------------------------------------------------------------------
        # get raw input file name(s)
        raw_infiles1 = []
        for hcfile in p['HCFILES']:
            raw_infiles1.append(os.path.basename(hcfile))
        raw_infile2 = os.path.basename(p['FPFILE'])
        # get wave filename
        wavefits, tag1 = spirouConfig.Constants.WAVE_FILE_EA_2(p)
        wavefitsname = os.path.split(wavefits)[-1]
        # log progress
        wargs = [p['FIBER'], wavefits]
        wmsg = 'Write wavelength solution for Fiber {0} in {1}'
        WLOG(p, '', wmsg.format(*wargs))
        # write solution to fitsfilename header
        # copy original keys
        hdict = spirouImage.CopyOriginalKeys(loc['HCHDR'], loc['HCCDR'])
        # add version number
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
        # set the input files
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'],
                                   value=p['BLAZFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                                   value=loc['WAVEFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                                   value=loc['WSOURCE'])
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                         dim1name='fpfile', values=p['FPFILE'])
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE2'],
                                         dim1name='hcfile', values=p['HCFILES'])
        # add qc parameters
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
        hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
        # add wave solution date
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME1'],
                                   value=p['MAX_TIME_HUMAN'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME2'],
                                   value=p['MAX_TIME_UNIX'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_CODE'], value=__NAME__)
        # add number of orders
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_ORD_N'],
                                   value=loc['LL_PARAM_FINAL'].shape[0])
        # add degree of fit
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_LL_DEG'],
                                   value=loc['LL_PARAM_FINAL'].shape[1] - 1)
        # add wave solution
        hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                         values=loc['LL_PARAM_FINAL'])

        # add FP CCF drift
        # target RV and width
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_TARG_RV'],
                                   value=p['TARGET_RV'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_WIDTH'],
                                   value=p['CCF_WIDTH'])
        # the rv step
        # rvstep = np.abs(loc['RV_CCF'][0] - loc['RV_CCF'][1])
        # hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_CDELT'], value=rvstep)
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_STEP'],
                                   value=p['CCF_STEP'])

        # add ccf stats
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_DRIFT'],
                                   value=loc['CCF_RES'][1])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_FWHM'],
                                   value=loc['FWHM'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_CONTRAST'],
                                   value=loc['CONTRAST'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_MAXCPP'],
                                   value=loc['MAXCPP'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_MASK'],
                                   value=p['CCF_MASK'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_LINES'],
                                   value=np.nansum(loc['TOT_LINE']))

        # write the wave "spectrum"
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
        p = spirouImage.WriteImage(p, wavefits, loc['LL_FINAL'], hdict)

        # get filename for E2DS calibDB copy of FITSFILENAME
        e2dscopy_filename = spirouConfig.Constants.WAVE_E2DS_COPY(p)[0]
        wargs = [p['FIBER'], os.path.split(e2dscopy_filename)[-1]]
        wmsg = 'Write reference E2DS spectra for Fiber {0} in {1}'
        WLOG(p, '', wmsg.format(*wargs))

        # make a copy of the E2DS file for the calibBD
        p = spirouImage.WriteImage(p, e2dscopy_filename, loc['HCDATA'], hdict)

        # only copy over if QC passed
        if p['QC']:
            # loop around hc files and update header with
            for hcfile in p['HCFILES']:
                raw_infilepath1 = os.path.join(p['ARG_FILE_DIR'], hcfile)
                p = spirouImage.UpdateWaveSolution(p, loc, raw_infilepath1)
            # update fp file
            raw_infilepath2 = os.path.join(p['ARG_FILE_DIR'], raw_infile2)
            p = spirouImage.UpdateWaveSolution(p, loc, raw_infilepath2)

        # ------------------------------------------------------------------
        # Save to result table
        # ------------------------------------------------------------------
        # calculate stats for table
        final_mean = 1000 * loc['X_MEAN_2']
        final_var = 1000 * loc['X_VAR_2']
        num_lines = loc['TOTAL_LINES_2']
        err = 1000 * np.sqrt(loc['X_VAR_2'] / num_lines)
        sig_littrow = 1000 * np.array(loc['LITTROW_SIG_' + str(lit_it)])
        # construct filename
        wavetbl = spirouConfig.Constants.WAVE_TBL_FILE_EA(p)
        wavetblname = os.path.basename(wavetbl)
        # construct and write table
        columnnames = ['night_name', 'file_name', 'fiber', 'mean', 'rms',
                       'N_lines', 'err', 'rms_L500', 'rms_L1000', 'rms_L1500',
                       'rms_L2000', 'rms_L2500', 'rms_L3000', 'rms_L3500']
        columnformats = ['{:20s}', '{:30s}', '{:3s}', '{:7.4f}', '{:6.2f}',
                         '{:3d}', '{:6.3f}', '{:6.2f}', '{:6.2f}', '{:6.2f}',
                         '{:6.2f}', '{:6.2f}', '{:6.2f}', '{:6.2f}']
        columnvalues = [[p['ARG_NIGHT_NAME']], [p['ARG_FILE_NAMES'][0]],
                        [p['FIBER']], [final_mean], [final_var],
                        [num_lines], [err], [sig_littrow[0]],
                        [sig_littrow[1]], [sig_littrow[2]], [sig_littrow[3]],
                        [sig_littrow[4]], [sig_littrow[5]], [sig_littrow[6]]]
        # make table
        table = spirouImage.MakeTable(p, columns=columnnames,
                                      values=columnvalues,
                                      formats=columnformats)
        # merge table
        wmsg = 'Global result summary saved in {0}'
        WLOG(p, '', wmsg.format(wavetblname))
        spirouImage.MergeTable(p, table, wavetbl, fmt='ascii.rst')

        # ------------------------------------------------------------------
        # Save line list table file
        # ------------------------------------------------------------------
        # construct filename
        # TODO proper column values
        wavelltbl = spirouConfig.Constants.WAVE_LINE_FILE_EA(p)
        wavelltblname = os.path.split(wavelltbl)[-1]
        # construct and write table
        columnnames = ['order', 'll', 'dv', 'w', 'xi', 'xo', 'dvdx']
        columnformats = ['{:.0f}', '{:12.4f}', '{:13.5f}', '{:12.4f}',
                         '{:12.4f}', '{:12.4f}', '{:8.4f}']

        columnvalues = []
        # construct column values (flatten over orders)
        for it in range(len(loc['X_DETAILS_2'])):
            for jt in range(len(loc['X_DETAILS_2'][it][0])):
                row = [float(it), loc['X_DETAILS_2'][it][0][jt],
                       loc['LL_DETAILS_2'][it][0][jt],
                       loc['X_DETAILS_2'][it][3][jt],
                       loc['X_DETAILS_2'][it][1][jt],
                       loc['X_DETAILS_2'][it][2][jt],
                       loc['SCALE_2'][it][jt]]
                columnvalues.append(row)

        # log saving
        wmsg = 'List of lines used saved in {0}'
        WLOG(p, '', wmsg.format(wavelltblname))

        # make table
        columnvalues = np.array(columnvalues).T
        table = spirouImage.MakeTable(p, columns=columnnames,
                                      values=columnvalues,
                                      formats=columnformats)
        # write table
        spirouImage.WriteTable(p, table, wavelltbl, fmt='ascii.rst')

        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if p['QC']:
            # set the wave key
            keydb = 'WAVE_{0}'.format(p['FIBER'])
            # copy wave file to calibDB folder
            spirouDB.PutCalibFile(p, wavefits)
            # update the master calib DB file with new key
            spirouDB.UpdateCalibMaster(p, keydb, wavefitsname, loc['HCHDR'])
            # set the hcref key
            keydb = 'HCREF_{0}'.format(p['FIBER'])
            # copy wave file to calibDB folder
            spirouDB.PutCalibFile(p, e2dscopy_filename)
            # update the master calib DB file with new key
            e2dscopyfits = os.path.split(e2dscopy_filename)[-1]
            spirouDB.UpdateCalibMaster(p, keydb, e2dscopyfits, loc['HCHDR'])

    # If the HC solution failed QCs we do not compute FP-HC solution
    elif has_fp and not p['QC']:
        wmsg = 'HC solution failed quality controls; FP not processed'
        WLOG(p, 'warning', wmsg)

    # If there is no FP file we log that
    elif not has_fp:
        wmsg = 'No FP file given; FP-HC combined solution cannot be generated'
        WLOG(p, 'warning', wmsg)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return p and loc
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

#

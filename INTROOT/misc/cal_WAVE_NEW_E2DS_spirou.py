#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_WAVE_NEW_E2DS_spirou.py [night_directory] [HCfitsfilename] [FPfitsfilename]

Wavelength calibration incorporating the FP lines
Following C. Lovis's method for Espresso

Created on 2018-06-08 at 16:00

@author: mhobson
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS.spirouTHORCA import spirouWAVE

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_WAVE_NEW_E2DS_spirou.py'
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


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, fpfile=None, hcfiles=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    if hcfiles is None or fpfile is None:
        names, types = ['fpfile', 'hcfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime([0, 1], types, names,
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
        WLOG('error', p['LOG_OPT'], emsg.format(*eargs))
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

#    # set find line mode
#    find_lines_mode = p['HC_FIND_LINES_MODE']

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
    p = spirouTHORCA.GetLampParams(p, hchdr)

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
    loc['WAVEPARAMS'], loc['WAVE_INIT'], loc['WAVEFILE'] = wout
    loc.set_sources(['WAVE_INIT', 'WAVEFILE', 'WAVEPARAMS'], wsource)
    poly_wave_sol = loc['WAVEPARAMS']

    # ----------------------------------------------------------------------
    # Check that wave parameters are consistent with "ic_ll_degr_fit"
    # ----------------------------------------------------------------------
    loc = spirouImage.CheckWaveSolConsistency(p, loc)

    # ----------------------------------------------------------------------
    # Read UNe solution
    # ----------------------------------------------------------------------
    wave_UNe, amp_UNe = spirouImage.ReadLineList(p)
    loc['LL_LINE'], loc['AMPL_LINE'] = wave_UNe, amp_UNe
    source = __NAME__ + '.main() + spirouImage.ReadLineList()'
    loc.set_sources(['ll_line', 'ampl_line'], source)

    # ----------------------------------------------------------------------
    # Generate wave map from wave solution
    # ----------------------------------------------------------------------
    loc = spirouWAVE.generate_wave_map(p, loc)

    # ----------------------------------------------------------------------
    # Find Gaussian Peaks in HC spectrum
    # ----------------------------------------------------------------------
    loc = spirouWAVE.find_hc_gauss_peaks(p, loc)

    # ----------------------------------------------------------------------
    # Start plotting session
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()

    # ----------------------------------------------------------------------
    # Fit Gaussian peaks (in triplets) to
    # ----------------------------------------------------------------------
    loc = spirouWAVE.fit_gaussian_triplets(p, loc)

    # ----------------------------------------------------------------------
    # Generate Resolution map and line profiles
    # ----------------------------------------------------------------------
    # log progress
    wmsg = 'Generating resolution map and '
    # generate resolution map
    loc = spirouWAVE.generate_resolution_map(p, loc)
    # map line profile map
    if p['DRS_PLOT']:
        sPlt.wave_ea_plot_line_profiles(p, loc)

    # ----------------------------------------------------------------------
    # End plotting session
    # ----------------------------------------------------------------------
    # end interactive session
    if p['DRS_PLOT']:
        sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    # quality control on sigma clip (sig1 > qc_hc_wave_sigma_max
    if loc['SIG1'] > p['QC_HC_WAVE_SIGMA_MAX']:
        fmsg = 'Sigma too high ({0:.5f} > {1:.5f})'
        fail_msg.append(fmsg.format(loc['SIG1'], p['QC_HC_WAVE_SIGMA_MAX']))
        passed = False
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['LOG_OPT'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')


    # # ----------------------------------------------------------------------
    # # define wave filename - TODO
    # # ----------------------------------------------------------------------
    #
    # # ----------------------------------------------------------------------
    # # Fit HC lines from filtered catalogue
    # # ----------------------------------------------------------------------
    # # TODO create new filtered catalogue
    # # set filtered catalogue as input for read_line_list
    # p['IC_LL_LINE_FILE'] = 'cat_UNe_drift_filt_waveformat.rdb'
    # # log message
    # wmsg = 'Processing Wavelength Calibration for Fiber {0}'
    # WLOG('info', p['LOG_OPT'] + p['FIBER'], wmsg.format(p['FIBER']))
    #
    # # ------------------------------------------------------------------
    # # First guess at solution for each order
    # # ------------------------------------------------------------------
    # # FIXME: Cannot get same number of lines identified
    # # Question: Tried with python gaussian fitting
    # # Question: Tried with Fortran fitgaus.fitgaus
    # loc = spirouTHORCA.FirstGuessSolution(p, loc, mode=find_lines_mode)
    #
    # # ------------------------------------------------------------------
    # # Detect bad fit filtering and saturated lines
    # # ------------------------------------------------------------------
    # # log message
    # wmsg = 'On fiber {0} cleaning list of identified lines'
    # WLOG('', p['LOG_OPT'], wmsg.format(p['FIBER']))
    # # clean lines
    # # question - this wasn't being done on oldDRS version as catalogue is good
    # # so is it necessary here? Probably safer...
    # loc = spirouTHORCA.DetectBadLines(p, loc, iteration=1)
    #


# TODO FP part starts from here

    # ----------------------------------------------------------------------
    # Find FP peaks after a central HC in each order and interpolate wavelength
    # ----------------------------------------------------------------------

    #setup for CreateDriftFile
    # set fpfile as ref file
    loc['SPEREF'] = loc['FPDATA']
    # set wavelength solution as the one from the HC lines
    loc['WAVE'] = loc['WAVE_MAP2']
    # set lamp as FP
    loc['LAMP'] = 'fp'

    # use spirouRV to get the position of FP peaks from reference file
    loc = spirouRV.CreateDriftFile(p, loc)
    # remove wide/spurious peaks
    loc = spirouRV.RemoveWidePeaks(p, loc)

    # get parameters from p
    n_init = p['IC_FP_N_ORD_START']
    n_fin = p['IC_FP_N_ORD_FINAL']
    size = p['IC_FP_SIZE']
    threshold = p['IC_FP_THRESHOLD']
    dopd0 = p['IC_FP_DOPD0']
    fit_deg = p['IC_FP_FIT_DEGREE']
    # get parameters from loc
    fpdata = loc['FPDATA']

    # set up storage
    FP_ll = []
    FP_ll2 = []
    FP_order = []
    FP_xx = []
    # reference peaks
    FP_ll_ref = []
    FP_xx_ref = []
    dif_n = []

    # loop over orders
    for order_num in range(n_init, n_fin):
        # get mask of HC line list for order
        mask1 = np.where(loc['ORD_T'] == order_num)
        # get pixel values of found HC lines for the order
        xgau = loc['XGAU_T'][mask1]
        # get mask of central HC lines
        mask2 = np.where((1000 < xgau) & (xgau < 3000))
        # get dv values of central HC lines
        dv = loc['DV_T'][mask1][mask2]
        # find HC line with smallest dv value
        best_line_ind = np.argmin(abs(dv))
        # get best HC line x value
        best_line_x = xgau[mask2][best_line_ind]
        # calculate best HC line wavelength value
        best_line_ll = np.polyval(loc['POLY_WAVE_SOL'][0][::-1], best_line_x)
        # get mask of FP lines for order
        mask_fp = np.where(loc['ORDPEAK'] == order_num)
        # get x values of FP lines
        x_fp = loc['XPEAK'][mask_fp]
        # Find FP line immediately after the HC line
        for j in range(1, len(x_fp)):
            if x_fp[j - 1] < best_line_x < x_fp[j]:
                # interpolate and save the FP ref line wavelength
                FP_ll_ref.append(best_line_ll + (best_line_ll ** 2 / dopd0) *
                                 ((x_fp[j] - best_line_x) / (x_fp[j] - x_fp[j - 1])))
                # save the FP ref line pixel position
                FP_xx_ref.append(x_fp[j])
                # save the FP ref line number
                initial_peak = j
        # ----------------------------------------------------------------------
        # number adjacent peaks differentially and asign wavelengths
        # ----------------------------------------------------------------------

        for k in range(len(pos)):
            # number peaks differentially
            dif_numb = k - initial_peak
            # get wavelength using differential numbering and reference peak
            FP_ll.append(1 / (1 / FP_ll_ref[order_num] - dif_numb / dopd0))
            # save order number
            FP_order.append(order_num)
            # save differential numbering
            dif_n.append(dif_numb)
            # save x positions of the lines
            FP_xx.append(pos[k])

    # # get initial wavelength solution from loc (is in there from firstguess)
    # ll_init = loc['WAVE_MAP2']
    # # set up storage
    # FP_ll = []
    # FP_ll2 = []
    # FP_order = []
    # FP_xx = []
    # # reference peaks
    # FP_ll_ref = []
    # FP_xx_ref = []
    # dif_n = []
    # # get parameters from p
    # n_init = p['IC_FP_N_ORD_START']
    # n_fin = p['IC_FP_N_ORD_FINAL']
    # size = p['IC_FP_SIZE']
    # threshold = p['IC_FP_THRESHOLD']
    # dopd0 = p['IC_FP_DOPD0']
    # fit_deg = p['IC_FP_FIT_DEGREE']
    # # get parameters from loc
    # fpdata = loc['FPDATA']
    # all_lines = loc['ALL_LINES']
    # # loop over the orders
    # for order_num in range(n_init, n_fin):
    #     # normalize the order
    #     miny, maxy = spirouBACK.BoxSmoothedMinMax(fpdata[order_num], 2 * size)
    #     fpdata_c = (fpdata[order_num] - miny) / (maxy - miny)
    #     # find all peaks in the order
    #     pos = spirouLOCOR.FindPosCentCol(fpdata_c, threshold)
    #     # remove first and last peaks to avoid edge effects
    #     pos = np.array(pos[1:-1])
    #
    #     # Select mid-range HC line in each order
    #     # TODO this is not very robust
    #     line_ind = len(all_lines[order_num]) / 2
    #     HC_ll = all_lines[order_num][line_ind][0]  # ll_out
    #     HC_x = all_lines[order_num][line_ind][5]  # x_out
    #
    #     # Find FP line immediately after the HC line
    #     for j in range(1, len(pos)):
    #         if pos[j - 1] < HC_x < pos[j]:
    #             # interpolate and save the FP ref line wavelength
    #             FP_ll_ref.append(HC_ll + (HC_ll ** 2 / dopd0) *
    #                              ((pos[j] - HC_x) / (pos[j] - pos[j - 1])))
    #             # save the FP ref line pixel position
    #             FP_xx_ref.append(pos[j])
    #             # save the FP ref line number
    #             initial_peak = j
    #
    #     # ----------------------------------------------------------------------
    #     # number adjacent peaks differentially and asign wavelengths
    #     # ----------------------------------------------------------------------
    #
    #     for k in range(len(pos)):
    #         # number peaks differentially
    #         dif_numb = k - initial_peak
    #         # get wavelength using differential numbering and reference peak
    #         FP_ll.append(1 / (1 / FP_ll_ref[order_num] - dif_numb / dopd0))
    #         # save order number
    #         FP_order.append(order_num)
    #         # save differential numbering
    #         dif_n.append(dif_numb)
    #         # save x positions of the lines
    #         FP_xx.append(pos[k])
    #
    # # ----------------------------------------------------------------------
    # # Plot initial and new wavelengths for an order - TODO move to spirouPLOT
    # # ----------------------------------------------------------------------
    #
    # # set plot order
    # plot_order = 5
    #
    # # set source of wave file
    # wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    # # get wave image
    # wout = spirouImage.GetWaveSolution(p, hdr=loc['HCHDR'], return_wavemap=True,
    #                                    return_filename=True)
    # param_ll_init, ll_init, wave_file = wout
    #
    # # define polynomial fit
    # c_aux = np.poly1d(param_ll_init[plot_order][::-1])  # reverse order
    # # create mask to select FP lines from plot_order only
    # ind = np.where(np.asarray(FP_order) == plot_order)
    # # get new FP line wavelengths for plot_order
    # FP_ll_plot = np.asarray(FP_ll)[ind]
    # # get FP line pixel positions for plot_order
    # FP_xx_plot = np.asarray(FP_xx)[ind]
    # # determine FP line wavelengths from initial wavelength solution
    # FP_ll_plot_orig = c_aux(FP_xx_plot)
    # # plot FP wavelength difference
    # plt.figure()
    # plt.plot(FP_ll_plot_orig, FP_ll_plot - FP_ll_plot_orig, 'o')
    # plt.xlabel('initial FP wavelength [nm]')
    # plt.ylabel('initial - new FP wavelengths [nm]')
    # plt.title('FP wavelengths - order ' + str(plot_order))
    #
    # # ----------------------------------------------------------------------
    # # Assign absolute FP numbers for reddest order
    # # ----------------------------------------------------------------------
    # # determine absolute number for reference peak of reddest order
    # m_init = int(round(dopd0 / FP_ll_ref[n_fin - 1]))
    # # absolute numbers for reddest order:
    # # find indexes for reddest order values
    # ind = np.where(np.asarray(FP_order) == n_fin - 1)
    # # get differential numbers for reddest order peaks
    # aux_n = np.asarray(dif_n)[ind]
    # # calculate absolute peak numbers for reddest order
    # m_aux = m_init - aux_n
    # # set m vector
    # m = m_aux
    # # initialise vector of order numbers for previous order
    # m_ord_prev = m_aux
    #
    # # ----------------------------------------------------------------------
    # # Plot FP lines, reference HC line for reddest order -
    # # TODO move to spirouPLOT
    # # ----------------------------------------------------------------------
    # # find indexes for reddest order values
    # ind = np.where(np.asarray(FP_order) == n_fin - 1)
    # # get FP line wavelengths for reddest order
    # FP_ll_red = np.asarray(FP_ll)[ind]
    # # get FP line pixel positions for reddest order
    # FP_xx_red = np.asarray(FP_xx)[ind]
    # # get index of reference HC line for reddest order
    # line_ind_red = len(all_lines[n_fin - 1]) / 2
    # # get wavelength of reference HC line for reddest order
    # HC_ll_red = all_lines[n_fin - 1][line_ind_red][0]
    # # get pixel position of reference HC line for reddest order
    # HC_x_red = all_lines[n_fin - 1][line_ind_red][5]
    # # plot
    # plt.figure()
    # plt.plot(ll_init[n_fin - 1], fpdata[n_fin - 1])
    # plt.xlabel('nm')
    # plt.ylabel('e-')
    # plt.title('FP order ' + str(n_fin - 1))
    # for i in range(len(FP_ll_red)):
    #     plt.vlines(FP_ll_red[i], 0, 3500000)
    # plt.vlines(HC_ll_red, 0, 3500000, color='green')
    # plt.vlines(FP_ll_ref[n_fin - 1], 0, 3500000, color='red')
    #
    # # ----------------------------------------------------------------------
    # # Assign absolute FP numbers for rest of orders by wavelength matching
    # # ----------------------------------------------------------------------
    # # loop over orders from reddest-1 to bluest
    # for i in range(n_fin - 2, -1, -1):
    #     # define auxiliary arrays with ll for order and previous order
    #     ind_ord = np.where(np.asarray(FP_order) == i)
    #     FP_ll_ord = np.asarray(FP_ll)[ind_ord]
    #     ind_ord_prev = np.where(np.asarray(FP_order) == i + 1)
    #     FP_ll_ord_prev = np.asarray(FP_ll)[ind_ord_prev]
    #     # check if overlap
    #     if FP_ll_ord[-1] >= FP_ll_ord_prev[0]:
    #         # find closest peak to last of this order in previous order
    #         m_match = (np.abs(FP_ll_ord_prev - FP_ll_ord[-1])).argmin()
    #         # get order number for last peak (take int so it's not an array)
    #         m_end = int(m_ord_prev[m_match])
    #         # define array of absolute peak numbers
    #         m_ord = m_end + np.arange(len(FP_ll_ord) - 1, -1, -1)
    #         # insert absolute order numbers at the start of m
    #         m = np.concatenate((m_ord, m))
    #         # redefine order number vector for previous order
    #         m_ord_prev = m_ord
    #     # if no overlap - TODO do something about it!
    #     else:
    #         print('no overlap')
    #
    # # ----------------------------------------------------------------------
    # # Derive d for each HC line
    # # ----------------------------------------------------------------------
    #
    # # set up storage
    # # effective cavity width for the HC lines
    # d = []
    # # 1/line number of the closest FP line to each HC line
    # one_m_d = []
    # # line number of the closest FP line to each HC line
    # m_d = []
    # one_m_d_w = []
    # # wavelength of HC lines
    # HC_ll_test = []
    #
    # # loop over orders
    # for ord_num in range(n_fin):
    #     # create order mask
    #     ind_ord = np.where(np.asarray(FP_order) == ord_num)
    #     # get FP line wavelengths for the order
    #     FP_ll_ord = np.asarray(FP_ll)[ind_ord]
    #     # get FP line pixel positions for the order
    #     FP_x_ord = np.asarray(FP_xx)[ind_ord]
    #     # get FP line numbers for the order
    #     m_ord = np.asarray(m)[ind_ord]
    #     # loop over HC lines in the order
    #     for j in range(len(all_lines[ord_num])):
    #         # loop over FP lines in the order
    #         for k in range(len(FP_ll_ord) - 1):
    #             # find surrounding FP lines for the HC line
    #             if FP_ll_ord[k - 1] < all_lines[ord_num][j][0] <= FP_ll_ord[k]:
    #                 # derive d for the HC line
    #                 t1 = all_lines[ord_num][j][0] * m_ord[k] * (m_ord[k] + 1)
    #                 t2 = FP_x_ord[k] - FP_x_ord[k - 1]
    #                 t3 = m_ord[k] * FP_x_ord[k] - \
    #                      (m_ord[k] + 1) * FP_x_ord[k - 1] \
    #                      + all_lines[ord_num][j][5]
    #                 d.append(0.5 * t1 * (t2 / t3))
    #                 # save 1/line number of closest FP line
    #                 one_m_d.append(1. / m_ord[k])
    #                 # save 1/ weighted average of line numbers - not used
    #                 one_m_d_w.append(1. /
    #                                  ((all_lines[ord_num][j][5] - FP_x_ord[k]) /
    #                                   (FP_x_ord[k - 1] - FP_x_ord[k])
    #                                   + m_ord[k]))
    #                 # save line number of closest FP line
    #                 m_d.append(m_ord[k])
    #                 # save HC line wavelength
    #                 HC_ll_test.append(all_lines[ord_num][j][0])
    #
    # # log line number span
    # wargs = [m_d[0], m_d[-1]]
    # wmsg = 'Mode number span: {0} - {1}'
    # WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
    #
    # # Sigma clipping on bad d values
    # # save copies of d and one_m_d for comparison
    # d_all = np.copy(np.asarray(d))
    # one_m_d_all = np.copy(np.asarray(one_m_d))
    # # define boundaries and mask
    # critlower = np.median(d) - np.std(d) * 4.
    # critupper = np.median(d) + np.std(d) * 4.
    # sig_clip_d = np.where((d > critlower) & (d < critupper))
    # # sigma clip
    # d = np.asarray(d)[sig_clip_d]
    # HC_ll_test = np.asarray(HC_ll_test)[sig_clip_d]
    # one_m_d = np.asarray(one_m_d)[sig_clip_d]
    # # log number of points removed
    # wargs = [len(d_all) - np.shape(sig_clip_d)[1]]
    # wmsg = '{0} points removed by d sigma clip'
    # WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
    #
    # # Verification sigma clip plot - TODO move to spirouPLOT
    # if (len(d_all) - np.shape(sig_clip_d)[1]) > 0:
    #     plt.figure()
    #     plt.plot(one_m_d_all, d_all, 'o')
    #
    # # ----------------------------------------------------------------------
    # # Fit (1/m) vs d
    # # ----------------------------------------------------------------------
    #
    # # define sorted arrays
    # one_m_sort = np.asarray(one_m_d).argsort()
    # one_m_d = np.asarray(one_m_d)[one_m_sort]
    # d = np.asarray(d)[one_m_sort]
    #
    # # ploynomial fit
    # fit_1m_d = np.polyfit(one_m_d, d, 5)
    # fit_1m_d_func = np.poly1d(fit_1m_d)
    #
    # # plot 1/m vs d and the fitted polynomial - TODO move to spirouPLOT
    # plt.figure()
    # # plot values
    # plt.plot(one_m_d, d, 'o')
    # # plot initial cavity width value
    # plt.hlines(dopd0 / 2., min(one_m_d), max(one_m_d), label='original d')
    # # plot reference peak of reddest order
    # plt.plot(1. / m_init, dopd0 / 2., 'D')
    # # plot fit
    # plt.plot(one_m_d, fit_1m_d_func(one_m_d), label='polynomial fit')
    # plt.xlabel('1/m')
    # plt.ylabel('d')
    # plt.legend(loc='best')
    #
    # # ----------------------------------------------------------------------
    # # Update FP peak wavelengths
    # # ----------------------------------------------------------------------
    #
    # # define storage
    # FP_ll_new = []
    #
    # # loop over peak numbers
    # for i in range(len(m)):
    #     # calculate wavelength from fit to 1/m vs d
    #     FP_ll_new.append(2 * fit_1m_d_func(1. / m[i]) / m[i])
    #
    # # plot by order - TODO move to spirouPLOT?
    #
    # # define colours
    # col = cm.rainbow(np.linspace(0, 1, n_fin))
    # plt.figure()
    # for i in range(n_fin):
    #     # get parameters for initial wavelength solution
    #     c_aux = np.poly1d(param_ll_init[i][::-1])
    #     # order mask
    #     ind_ord = np.where(np.asarray(FP_order) == i)
    #     # get FP line pixel positions for the order
    #     FP_x_ord = np.asarray(FP_xx)[ind_ord]
    #     # derive FP line wavelengths using initial solution
    #     FP_ll_orig = c_aux(FP_x_ord)
    #     # get new FP line wavelengths for the order
    #     FP_ll_new_ord = np.asarray(FP_ll_new)[ind_ord]
    #     # plot old-new wavelengths
    #     plt.plot(FP_x_ord, FP_ll_orig - FP_ll_new_ord, 'o',
    #              label='order ' + str(i), color=col[i])
    # plt.xlabel('FP peak position [pix]')
    # plt.ylabel('FP old-new wavelength difference [nm]')
    # plt.legend(loc='best')
    #
    # # ----------------------------------------------------------------------
    # # Fit wavelength solution from FP peaks
    # # ----------------------------------------------------------------------
    #
    # # set fit degree - TODO move to constants file
    # ic_FP_fit_deg = 3
    # # define storage array for fit params
    # param_FP_fit = np.zeros((n_fin, ic_FP_fit_deg + 1), 'd')
    # # define storage array for l(x)
    # FP_sol = np.zeros((n_fin, len(fpdata[0])), 'd')
    #
    # # loop over orders
    # for ord_num in range(n_fin):
    #     # creat order mask
    #     ind_ord = np.where(np.asarray(FP_order) == ord_num)
    #     # get FP line pixel positions for the order
    #     FP_x_ord = np.asarray(FP_xx)[ind_ord]
    #     # get new FP line wavelengths for the order
    #     FP_ll_new_ord = np.asarray(FP_ll_new)[ind_ord]
    #     # fit a polynomial to the new FP ll vs the pixel positions
    #     param = np.polyfit(FP_x_ord, FP_ll_new_ord, ic_FP_fit_deg)
    #     # saves the fit parameters IN DRS ORDER
    #     param_FP_fit[ord_num] = param[::-1]
    #     aux_param = np.poly1d(param)
    #     # evaluate the polynomial in each x for each order
    #     for pix in range(len(fpdata[0])):
    #         aux2 = aux_param(pix)
    #         # save the evaluated wavelength
    #         FP_sol[ord_num, pix] = aux2
    #
    # # Comparison plot with initial wave sol - TODO move to spirouPLOT
    # # define colours
    # col = cm.rainbow(np.linspace(0, 1, n_fin))
    # plt.figure()
    # for ord_num in range(n_fin):
    #     x = np.arange(len(fpdata[0]))
    #     lldif = ll_init[ord_num] - FP_sol[ord_num]
    #     plt.plot(x, lldif, label='order ' + str(ord_num), color=col[ord_num])
    # plt.xlabel('pixel coordinate')
    # plt.ylabel('wavelength solution difference (initial-new) [nm]')
    # plt.legend(loc='best')
    #
    # # ----------------------------------------------------------------------
    # # archive result in e2ds spectra
    # # ----------------------------------------------------------------------
    #
    # # get wave filename - TODO define this
    # wavefits, tag1 = spirouConfig.Constants.WAVE_FILE(p)
    # wavefitsname = os.path.split(wavefits)[-1]
    #
    # # log progress
    # wargs = [p['FIBER'], wavefitsname]
    # wmsg = 'Write wavelength solution for Fiber {0} in {1}'
    # WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
    # # write solution to fitsfilename header
    # # copy original keys
    # hdict = spirouImage.CopyOriginalKeys(loc['HCHDR'], loc['HCCDR'])
    # # add version number
    # hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    # hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag1)
    # # add quality control
    # hdict = spirouImage.AddKey(hdict, p['KW_DRS_QC'], value=p['QC'])
    # # add number of orders
    # hdict = spirouImage.AddKey(hdict, p['KW_WAVE_ORD_N'],
    #                            value=loc['LL_PARAM_FINAL'].shape[0])
    # # add degree of fit
    # hdict = spirouImage.AddKey(hdict, p['KW_WAVE_LL_DEG'],
    #                            value=loc['LL_PARAM_FINAL'].shape[1] - 1)
    # # add wave solution
    # hdict = spirouImage.AddKey2DList(hdict, p['KW_WAVE_PARAM'],
    #                                  values=loc['LL_PARAM_FINAL'])
    # # write original E2DS file and add header keys (via hdict)
    # p = spirouImage.WriteImage(p, p['FITSFILENAME'], loc['HCDATA'], hdict)
    # # write the wave "spectrum"
    # p = spirouImage.WriteImage(p, wavefits, loc['LL_FINAL'], hdict)
    #
    # # get filename for E2DS calibDB copy of FITSFILENAME
    # e2dscopy_filename, tag2 = spirouConfig.Constants.WAVE_E2DS_COPY(p)
    # # make a copy of the E2DS file for the calibBD
    # hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag2)
    # p = spirouImage.WriteImage(p, e2dscopy_filename, loc['HCDATA'], hdict)
    #
    # # ----------------------------------------------------------------------
    # # Quality control - TODO
    # # ----------------------------------------------------------------------
    #
    # # ----------------------------------------------------------------------
    # # Update the calibration data base - TODO
    # # ----------------------------------------------------------------------
    #
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_WAVE_NEW_E2DS_spirou.py [night_directory] [HCfitsfilename] [FPfitsfilename]

Wavelength calibration incorporating the FP lines
Following C. Lovis's method for Espresso

Created on 2018-06-08 at 16:00

@author: mhobson
"""
from __future__ import division
import numpy as np
import matplotlib.cm as cm
import os

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS.spirouTHORCA import spirouWAVE
from SpirouDRS.spirouCore.spirouMath import nanpolyfit
from SpirouDRS import spirouRV

from astropy import constants as cc
from astropy import units as uu
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value

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
    # TODO: Needs changing as this is only testable on one machine
    #tmp_wave_file = '/data/CFHT/calibDB_1/2018-07-30_MASTER_wave_ea_AB.fits'
    # tmp_wave_file = '/data/CFHT/calibDB_1/2018-09-25_2305967c_pp_wave_ea_C.fits'
    wout = spirouImage.GetWaveSolution(p, hdr=hchdr,
                                       #filename=tmp_wave_file,
                                       return_wavemap=True,
                                       return_filename=True, fiber=wave_fiber)
    loc['WAVEPARAMS'], loc['WAVE_INIT'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    loc.set_sources(['WAVE_INIT', 'WAVEFILE', 'WAVEPARAMS', 'WSOURCE'], wsource)
    poly_wave_sol = loc['WAVEPARAMS']

    # ----------------------------------------------------------------------
    # Check that wave parameters are consistent with "ic_ll_degr_fit"
    # ----------------------------------------------------------------------

    loc = spirouImage.CheckWaveSolConsistency(p, loc)

    p['IC_LL_DEGR_FIT'] = 4
    p['IC_LITTROW_ORDER_FIT_DEG'] = 4


    # ----------------------------------------------------------------------
    # Read UNe solution
    # ----------------------------------------------------------------------
    wave_u_ne, amp_u_ne = spirouImage.ReadLineList(p)
    loc['LL_LINE'], loc['AMPL_LINE'] = wave_u_ne, amp_u_ne
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
        sPlt.start_interactive_session(p)

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
        sPlt.end_interactive_session(p)

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
        WLOG(p, 'info', 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG(p, 'warning', wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # log the global stats
    # ----------------------------------------------------------------------

    # calculate catalog-fit residuals in km/s

    res_hc =[]
    sumres_hc = 0.0
    sumres2_hc = 0.0

    for order in range(loc['NBO']):
        # get HC line wavelengths for the order
        order_mask = loc['ORD_T'] == order
        hc_x_ord = loc['XGAU_T'][order_mask]
        hc_ll_ord = np.polyval(loc['POLY_WAVE_SOL'][order][::-1],hc_x_ord)
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

    # rest = (np.concatenate(fp_ll_final_clip)-np.concatenate(fp_ll_in_clip))\
    #        *speed_of_light/np.concatenate(fp_ll_in_clip)
    # print(1000 * np.sqrt((np.nansum(rest ** 2) / total_lines -
    #                       np.nansum(rest / total_lines) ** 2) / total_lines))


    # TODO FP part starts from here

    # ----------------------------------------------------------------------
    # Find FP peaks after a central HC in each order and interpolate wavelength
    # ----------------------------------------------------------------------
    # setup for find_fp_lines_new_setup (to be compatible w/ wave_EA)
    # set wavelength solution as the one from the HC lines
    loc['LITTROW_EXTRAP_SOL_1'] = loc['WAVE_MAP2']

    # get FP peaks
    loc = spirouTHORCA.FindFPLinesNew(p, loc)

    # get parameters from p
    n_init = 0  # p['IC_FP_N_ORD_START']
    n_fin = 47  # p['IC_FP_N_ORD_FINAL'] # note: no lines in 48 from calHC
    size = p['IC_FP_SIZE']
    threshold = p['IC_FP_THRESHOLD']
    dopd0 = 2.44962434814043e7    #2.450101e7  # 2.4508e7   # p['IC_FP_DOPD0']
    fit_deg = p['IC_FP_FIT_DEGREE']
    # get parameters from loc
    fpdata = loc['FPDATA']

    # set up storage
    fp_ll = []
    fp_ll2 = []
    fp_order = []
    fp_xx = []
    # reference peaks
    fp_ll_ref = []
    fp_xx_ref = []
    hc_ll_ref = []
    hc_xx_ref = []
    dif_n = []
    peak_num_init = []

    # INITTEST saves
    fp_ll_init = []
    fp_ll_ref_init = []

    # loop over orders
    for order_num in range(n_init, n_fin):
        # ----------------------------------------------------------------------
        # number fp peaks differentially and identify gaps
        # ----------------------------------------------------------------------

        # get mask of FP lines for order
        mask_fp = loc['ORDPEAK'] == order_num
        # get x values of FP lines
        x_fp = loc['XPEAK'][mask_fp]
        # get 30% blaze mask
        mb = np.where(loc['BLAZE'][order_num]>0.3*np.max(loc['BLAZE'][order_num]))
        # keep only x values at above 30% blaze
        x_fp = x_fp[np.logical_and(np.max(mb) > x_fp, np.min(mb) < x_fp)]
        # initial differential numbering (assuming no gaps)
        peak_num_init = np.arange(len(x_fp))
        # find gaps in x
        # get median of x difference
        med_x_diff = np.nanmedian(x_fp[1:] - x_fp[:-1])
        # get array of x differences
        x_diff = x_fp[1:] - x_fp[:-1]
        # get indices where x_diff differs too much from median
        cond1 = x_diff < 0.75 * med_x_diff
        cond2 = x_diff > 1.25 * med_x_diff
        x_gap_ind = np.where(cond1 | cond2)
        # get the opposite mask (no-gap points)
        cond3 = x_diff > 0.75 * med_x_diff
        cond4 = x_diff < 1.25 * med_x_diff
        x_good_ind = np.where(cond3 & cond4)
        # fit x_fp v x_diff for good points
        cfit_xdiff = nanpolyfit(x_fp[1:][x_good_ind], x_diff[x_good_ind], 2)
        # loop over gap points
        for i in range(np.shape(x_gap_ind)[1]):
            # # find closest good x diff
            # x_diff_aux_ind = np.argmin(abs(x_good_ind - x_gap_ind[0][i]))
            # x_diff_aux = x_diff[x_good_ind[0][x_diff_aux_ind]]
            # get estimated xdiff value from the fit
            x_diff_aux = np.polyval(cfit_xdiff, x_fp[1:][x_gap_ind[0][i]])
            # estimate missed peaks
            x_jump = int(np.round((x_diff[x_gap_ind[0][i]] / x_diff_aux))) - 1
            # add the jump
            peak_num_init[x_gap_ind[0][i] + 1:] += x_jump

        # INITTEST save original (HC sol) wavelengths
        # fp_ll_ref_init.append(np.polyval(loc['POLY_WAVE_SOL'][order_num][::-1], x_fp[fp_ref_ind]))
        fp_ll_init.append(np.polyval(loc['POLY_WAVE_SOL'][order_num][::-1], x_fp))
        dif_num = peak_num_init

        # save differential numbering
        dif_n.append(dif_num)
        # save order number
        fp_order.append(np.ones(len(x_fp)) * order_num)
        # save x positions
        fp_xx.append(x_fp)

    #INITTEST replace fp_lls with init version
    fp_ll = fp_ll_init
    # fp_ll_ref = fp_ll_ref_init


    # ----------------------------------------------------------------------
    # Assign absolute FP numbers for reddest order
    # ----------------------------------------------------------------------

    # determine absolute number for reference peak of reddest order
    # m_init = int(round(dopd0 / fp_ll_ref[n_fin - n_init - 1]))
    # INITTEST take reddest FP line
    m_init = int(round(dopd0 / fp_ll[-1][-1]))
    # absolute numbers for reddest order:
    # get differential numbers for reddest order peaks
    aux_n = dif_n[n_fin - n_init - 1]
    # calculate absolute peak numbers for reddest order
    m_aux = m_init - aux_n + aux_n[-1]
    # set m vector
    m = m_aux
    # initialise vector of order numbers for previous order
    m_ord_prev = m_aux

    # ----------------------------------------------------------------------
    # Assign absolute FP numbers for rest of orders by wavelength matching
    # ----------------------------------------------------------------------

    # define no-overlap-matching function (sorry Neil)
    def no_overlap_match_calc(fp_ll_ord, fp_ll_ord_prev,
                              fp_ll_diff, fp_ll_diff_prev, m_ord_prev):
        # print warning re no overlap
        wmsg = 'no overlap for order ' + str(i) + ', estimating gap size'
        WLOG(p, 'warning', wmsg.format())
        # mask to keep only difference between no-gap lines for both ord
        mask_ll_diff = fp_ll_diff > 0.75 * np.nanmedian(fp_ll_diff)
        mask_ll_diff &= fp_ll_diff < 1.25 * np.nanmedian(fp_ll_diff)
        mask_ll_diff_prev = fp_ll_diff_prev > 0.75 * np.nanmedian(
            fp_ll_diff_prev)
        mask_ll_diff_prev &= fp_ll_diff_prev < 1.25 * np.nanmedian(
            fp_ll_diff_prev)
        # get last diff for current order, first for prev
        ll_diff_fin = fp_ll_diff[mask_ll_diff][-1]
        ll_diff_init = fp_ll_diff_prev[mask_ll_diff_prev][0]
        # estimate lines missed using both ll_diff
        ll_miss = fp_ll_ord_prev[0] - fp_ll_ord[-1]
        m_end_1 = int(np.round(ll_miss / ll_diff_fin))
        m_end_2 = int(np.round(ll_miss / ll_diff_init))
        # check they are the same, print warning if not
        if not m_end_1 == m_end_2:
            wmsg = ('Missing line estimate miss-match: {0} v {1} '
                    'from {2:.5f} v {3:.5f}')
            wargs = [m_end_1, m_end_2, ll_diff_fin, ll_diff_init]
            WLOG(p, 'warning', wmsg.format(*wargs))
        # calculate m_end
        m_end = int(m_ord_prev[0]) + m_end_1
        # define array of absolute peak numbers
        m_ord = m_end + dif_n[i][-1] - dif_n[i]
        # return m_ord
        return m_ord

    # loop over orders from reddest-1 to bluest
    for i in range(n_fin - n_init - 2, -1, -1):
        # define auxiliary arrays with ll for order and previous order
        fp_ll_ord = fp_ll[i]
        fp_ll_ord_prev = fp_ll[i + 1]
        # define median ll diff for both orders
        fp_ll_diff = np.nanmedian(fp_ll_ord[1:] - fp_ll_ord[:-1])
        fp_ll_diff_prev = np.nanmedian(fp_ll_ord_prev[1:] - fp_ll_ord_prev[:-1])
        # check if overlap
        if fp_ll_ord[-1] >= fp_ll_ord_prev[0]:
            # get overlapping peaks for both
            # allow 0.25*lldiff offsets
            mask_ord_over = fp_ll_ord >= fp_ll_ord_prev[0] - 0.25*fp_ll_diff_prev
            fp_ll_ord_over = fp_ll_ord[mask_ord_over]
            mask_prev_over = fp_ll_ord_prev <= fp_ll_ord[-1] + 0.25*fp_ll_diff
            fp_ll_prev_over = fp_ll_ord_prev[mask_prev_over]
            # loop to find closest match
            mindiff = []
            argmindiff = []
            for j in range(len(fp_ll_ord_over)):
                diff = np.abs(fp_ll_prev_over-fp_ll_ord_over[j])
                mindiff.append(np.min(diff))
                argmindiff.append(np.argmin(diff))
            # check that smallest diff is in fact a line match
            if np.min(mindiff) < 0.25*fp_ll_diff:
                # set the match m as the one for the smallest diff
                m_match = argmindiff[np.argmin(mindiff)]
                # get line number for peak with smallest diff
                m_end = m_ord_prev[mask_prev_over][m_match]
                # get dif n for peak with smallest diff
                dif_n_match = dif_n[i][mask_ord_over][np.argmin(mindiff)]
                # define array of absolute peak numbers
                m_ord = m_end + dif_n_match - dif_n[i]
            # if not treat as no overlap
            else:
                m_ord = no_overlap_match_calc(fp_ll_ord, fp_ll_ord_prev,
                                              fp_ll_diff, fp_ll_diff_prev, m_ord_prev)
        # if no overlap
        else:
            m_ord = no_overlap_match_calc(fp_ll_ord, fp_ll_ord_prev,
                                          fp_ll_diff, fp_ll_diff_prev, m_ord_prev)
            # wmsg = 'no overlap for order ' + str(i) + ', estimating gap size'
            # WLOG(p, 'warning', wmsg.format())
            #
            # # get fp wavelength diff for consecutive lines in orders
            # fp_ll_diff = fp_ll_ord[1:] - fp_ll_ord[:-1]
            # fp_ll_diff_prev = fp_ll_ord_prev[1:] - fp_ll_ord_prev[:-1]
            # # mask to keep only difference between no-gap lines for both ord
            # mask_ll_diff = fp_ll_diff > 0.75 * np.nanmedian(fp_ll_diff)
            # mask_ll_diff &= fp_ll_diff < 1.25 * np.nanmedian(fp_ll_diff)
            # mask_ll_diff_prev = fp_ll_diff_prev > 0.75 * np.nanmedian(
            #     fp_ll_diff_prev)
            # mask_ll_diff_prev &= fp_ll_diff_prev < 1.25 * np.nanmedian(
            #     fp_ll_diff_prev)
            # # get last diff for current order, first for prev
            # ll_diff_fin = fp_ll_diff[mask_ll_diff][-1]
            # ll_diff_init = fp_ll_diff_prev[mask_ll_diff_prev][0]
            # # estimate lines missed using both ll_diff
            # ll_miss = fp_ll_ord_prev[0] - fp_ll_ord[-1]
            # m_end_1 = int(np.round(ll_miss / ll_diff_fin))
            # m_end_2 = int(np.round(ll_miss / ll_diff_init))
            # # check they are the same, print warning if not
            # if not m_end_1 == m_end_2:
            #     wmsg = ('Missing line estimate miss-match: {0} v {1} '
            #             'from {2:.5f} v {3:.5f}')
            #     wargs = [m_end_1, m_end_2, ll_diff_fin, ll_diff_init]
            #     WLOG(p, 'warning', wmsg.format(*wargs))
            # # calculate m_end
            # m_end = int(m_ord_prev[0]) + m_end_1
            # # define array of absolute peak numbers
            # m_ord = m_end + dif_n[i][-1] - dif_n[i]
        # insert absolute order numbers at the start of m
        m = np.concatenate((m_ord, m))
        # redefine order number vector for previous order
        m_ord_prev = m_ord



    # ----------------------------------------------------------------------
    # Derive d for each HC line
    # ----------------------------------------------------------------------

    # set up storage
    # m(x) fit coefficients
    coeff_xm_all = []
    # m(x) fit dispersion
    xm_disp = []
    # effective cavity width for the HC lines
    d = []
    # 1/line number of the closest FP line to each HC line
    one_m_d = []
    # line number of the closest FP line to each HC line
    m_d = []
    one_m_d_w = []
    # wavelength of HC lines
    hc_ll_test = []
    # pixel value of kept HC lines
    hc_xx_test = []
    # order of kept hc lines
    hc_ord_test = []


    # Test if fp gaps create the bad points
    d_test = []
    one_m_d_test = []

    # save mask for m(x) fits
    xm_mask = []
    # loop over orders
    for ord_num in range(n_fin - n_init):
        # create order mask
        ind_ord = np.where(np.concatenate(fp_order).ravel() == ord_num + n_init)
        # get FP line wavelengths for the order
        fp_ll_ord = fp_ll[ord_num]
        # get FP line pixel positions for the order
        fp_x_ord = fp_xx[ord_num]
        # get FP line numbers for the order
        m_ord = m[ind_ord]
        # HC mask - keep best lines with small dv at above 30% blaze only
        cond1 = abs(loc['DV_T']) < 0.25
        cond2 = loc['ORD_T'] == ord_num + n_init
        hc_mask = np.where(cond1 & cond2)
        # get HC line pixel positions for the order
        hc_x_ord = loc['XGAU_T'][hc_mask]
        # get 30% blaze mask
        mb = np.where(loc['BLAZE'][ord_num] > 0.3 * np.max(loc['BLAZE'][ord_num]))
        # keep only x values at above 30% blaze
        blaze_mask = np.logical_and(np.max(mb) > hc_x_ord, np.min(mb) < hc_x_ord)
        hc_x_ord = hc_x_ord[blaze_mask]
        # get HC line wavelengths for the order
        hc_ll_ord = np.polyval(loc['POLY_WAVE_SOL'][ord_num + n_init][::-1],
                               hc_x_ord)
        # get corresponding catalogue lines from loc
        hc_ll_ord_cat = loc['WAVE_CATALOG'][hc_mask][blaze_mask]

        # fit x vs m for FP lines w/sigma-clipping
        sigclip = 7
        # initialise the while loop
        sigmax = sigclip + 1
        # initialise mask
        mask = np.ones_like(fp_x_ord, dtype = 'Bool')
        while sigmax>sigclip:
            # fit on masked values
            coeff_xm = nanpolyfit(fp_x_ord[mask], m_ord[mask], deg=p['IC_LL_DEGR_FIT'])
            # get residuals (not masked or dimension break)
            res = m_ord - np.polyval(coeff_xm, fp_x_ord)
            # normalise
            res = np.abs(res/np.nanmedian(np.abs(res[mask])))
            # get the max residual in sigmas
            sigmax = np.max(res[mask])
            # mask all outliers
            if sigmax > sigclip:
                mask[res>=sigclip] = False
        # save coefficients
        coeff_xm_all.append(coeff_xm)
        # save dispersion
        xm_disp.append(np.std(m_ord[mask] -np.polyval(coeff_xm, fp_x_ord[mask])))
        # save mask
        xm_mask.append(mask)

        # get fractional m for HC lines from fit
        m_hc = np.polyval(coeff_xm, hc_x_ord)
        # get cavity width for HC lines from FP equation
        d_hc = m_hc * hc_ll_ord_cat / 2.
        # save in arrays
        d.append(d_hc)
        one_m_d.append(1/m_hc)
        m_d.append(m_hc)
        hc_ll_test.append(hc_ll_ord_cat)
        hc_xx_test.append(hc_x_ord)
        hc_ord_test.append((ord_num + n_init)*np.ones_like(hc_x_ord))

    # plots
    if p['DRS_PLOT']:
        # residuals plot
        plt.figure()
        # loop over orders
        for ord_num in range(n_fin - n_init):
            # create order mask
            ind_ord = np.where(np.concatenate(fp_order).ravel() == ord_num + n_init)
            # get FP line pixel positions for the order
            fp_x_ord = fp_xx[ord_num]
            # get FP line numbers for the order
            m_ord = m[ind_ord]
            # get m(x) mask for the order
            mask = xm_mask[ord_num]
            # get coefficients for the order
            coeff_xm = coeff_xm_all[ord_num]
            # plot residuals
            plt.plot(fp_x_ord[mask], m_ord[mask] - np.polyval(coeff_xm, fp_x_ord[mask]) + 0.01 * ord_num, '.')
        plt.xlabel('FP pixel position')
        plt.ylabel('m(x) residuals (shifted +0.01*Order)')

        #m(x) dispersion plot
        plt.figure()
        plt.plot(np.arange(n_fin-n_init), xm_disp,'.')
        plt.xlabel('Order')
        plt.ylabel('m(x) dispersion')

        # verification plot
        plt.figure()
        plt.plot(np.concatenate(hc_ll_test).ravel(), np.concatenate(d).ravel(),'.')
        plt.xlabel('HC line wavelengths')
        plt.ylabel('cavity width')

    #flatten arrays
    one_m_d_sa = one_m_d
    d_sa = d
    m_d_sa = m_d
    one_m_d = np.concatenate(one_m_d).ravel()
    d = np.concatenate(d).ravel()
    m_d = np.concatenate(m_d).ravel()
    hc_ll_test = np.concatenate(hc_ll_test).ravel()
    hc_xx_test = np.concatenate(hc_xx_test).ravel()
    hc_ord_test = np.concatenate(hc_ord_test).ravel()


    # log line number span
    wargs = [round(m_d[0]), round(m_d[-1])]
    wmsg = 'Mode number span: {0} - {1}'
    WLOG(p, '', wmsg.format(*wargs))

    # ----------------------------------------------------------------------
    # Fit (1/m) vs d
    # ----------------------------------------------------------------------

    # decide if refit or read fit from file
    update_cavity = not os.path.exists('cavity_length_m_fit.dat')

    if update_cavity:
        # define sorted arrays
        one_m_sort = np.asarray(one_m_d).argsort()
        one_m_d = np.asarray(one_m_d)[one_m_sort]
        d = np.asarray(d)[one_m_sort]

        # # initial polynomial fit
        # fit_1m_d_init = nanpolyfit(one_m_d, d, 9)
        # # get residuals
        # res = d - np.polyval(fit_1m_d_init, one_m_d)
        # # mask points at +/- 1 sigma
        # sig_clip = abs(res) < np.std(res)
        # one_m_d = one_m_d[sig_clip]
        # d = d[sig_clip]

        # second polynomial fit
        fit_1m_d = nanpolyfit(one_m_d, d, 9)
        fit_1m_d_func = np.poly1d(fit_1m_d)
        res_d_final = d - fit_1m_d_func(one_m_d)


        if p['DRS_PLOT']:
            # plot 1/m vs d and the fitted polynomial - TODO move to spirouPLOT
            plt.figure()
            plt.subplot(211)
            # plot values
            plt.plot(one_m_d, d, 'o')
            # plot initial cavity width value
            plt.hlines(dopd0 / 2., min(one_m_d), max(one_m_d), label='original d')
            # plot reference peak of reddest order
            plt.plot(1. / m_init, dopd0 / 2., 'D')
            # plot fit
            plt.plot(one_m_d, fit_1m_d_func(one_m_d), label='polynomial fit')
            plt.xlabel('1/m')
            plt.ylabel('d')
            plt.legend(loc='best')
            plt.title('Interpolated cavity width for HC lines')
            # plot residuals
            plt.subplot(212)
            plt.plot(one_m_d, res_d_final, '.')
            plt.xlabel('1/m')
            plt.ylabel('residuals [nm]')


        # fit d v wavelength w/sigma-clipping
        sigclip = 7
        # initialise the while loop
        sigmax = sigclip + 1
        # initialise mask
        mask = np.ones_like(hc_ll_test, dtype='Bool')
        while sigmax > sigclip:
            # fit on masked values
            ff = nanpolyfit(hc_ll_test[mask], d[mask], deg=9)
            # get residuals (not masked or dimension break)
            res = d - np.polyval(ff, hc_ll_test)
            # normalise
            res = np.abs(res / np.nanmedian(np.abs(res[mask])))
            # get the max residual in sigmas
            sigmax = np.max(res[mask])
            # mask all outliers
            if sigmax > sigclip:
                mask[res >= sigclip] = False



        # write polyfits to files
        # TODO proper paths
        np.savetxt('cavity_length_m_fit.dat', fit_1m_d)
        np.savetxt('cavity_length_ll_fit.dat', ff)
    else:
        # read fit coefficients from files
        # TODO proper paths
        fit_1m_d = np.genfromtxt('cavity_length_m_fit.dat')
        ff = np.genfromtxt('cavity_length_ll_fit.dat')
        fit_1m_d_func = np.poly1d(fit_1m_d)
        # get achromatic cavity change - ie shift
        residual = d - np.polyval(ff, hc_ll_test)
        # update coeffs with mean shift
        ff[-1] += np.nanmedian(residual)

    fitval = np.polyval(ff, hc_ll_test)

    if p['DRS_PLOT']:
        # plot wavelength vs d and the fitted polynomial - TODO move to spirouPLOT
        plt.figure()
        plt.subplot(211)
        # plot values
        plt.plot(hc_ll_test, d, '.')
        # plot initial cavity width value
        plt.hlines(dopd0 / 2., min(hc_ll_test), max(hc_ll_test), label='original d')
        # plot reference peak of reddest order
        plt.plot(fp_ll[-1][-1], dopd0 / 2., 'D')
        # plot fit
        plt.plot(hc_ll_test, fitval, label='polynomial fit')
        plt.xlabel('wavelength')
        plt.ylabel('d')
        plt.legend(loc='best')
        plt.title('Interpolated cavity width for HC lines')
        # plot residuals
        plt.subplot(212)
        plt.plot(hc_ll_test, d-fitval, '.')
        plt.xlabel('wavelength')
        plt.ylabel('residuals [nm]')

    #26189.3
    # ----------------------------------------------------------------------
    # Update FP peak wavelengths
    # ----------------------------------------------------------------------

    # define storage
    fp_ll_new = []

    # loop over peak numbers
    for i in range(len(m)):
        # calculate wavelength from fit to 1/m vs d
        fp_ll_new.append(2 * fit_1m_d_func(1. / m[i]) / m[i])

    # from the d v wavelength fit
    fp_ll_new_2 = np.ones_like(m)*1600.
    for ite in range(6):
        recon_d = np.polyval(ff, fp_ll_new_2)
        fp_ll_new_2 = recon_d/m*2
    # TODO toggle to switch between fp ll fits
    fp_ll_new = fp_ll_new_2

    # save to loc (flattened)
    loc['FP_LL_NEW'] = np.array(fp_ll_new)
    loc['FP_XX_NEW'] = np.array(np.concatenate(fp_xx).ravel())
    loc['FP_ORD_NEW'] = np.array(np.concatenate(fp_order).ravel())

    if p['DRS_PLOT']:
        # plot by order - TODO move to spirouPLOT
        # define colours
        # noinspection PyUnresolvedReferences
        col = cm.rainbow(np.linspace(0, 1, n_fin))
        plt.figure()
        for ind_ord in range(n_fin - n_init):
            # get parameters for initial wavelength solution
            c_aux = np.poly1d(loc['POLY_WAVE_SOL'][ind_ord + n_init][::-1])
            # order mask
            ord_mask = np.where(
                np.concatenate(fp_order).ravel() == ind_ord + n_init)
            # get FP line pixel positions for the order
            fp_x_ord = fp_xx[ind_ord]
            # derive FP line wavelengths using initial solution
            fp_ll_orig = c_aux(fp_x_ord)
            # get new FP line wavelengths for the order
            fp_ll_new_ord = np.asarray(fp_ll_new)[ord_mask]
            # plot old-new wavelengths
            plt.plot(fp_x_ord, fp_ll_orig - fp_ll_new_ord + 0.001 * ind_ord, '.',
                     label='order ' + str(ind_ord), color=col[ind_ord])
        plt.xlabel('FP peak position [pix]')
        ylabel = 'FP old-new wavelength difference [nm] (shifted +0.001 per order)'
        plt.ylabel(ylabel)
        plt.legend(loc='best')

    # ----------------------------------------------------------------------
    # Fit wavelength solution from FP peaks
    # ----------------------------------------------------------------------

    #reset deg to match Etienne
    p['IC_LL_DEGR_FIT'] = 4

    # set up storage arrays
    xpix = np.arange(loc['NBPIX'])
    wave_map_final = np.zeros((n_fin - n_init, loc['NBPIX']))
    poly_wave_sol_final = np.zeros((n_fin-n_init, p['IC_LL_DEGR_FIT']+1))
    wsumres = 0.0
    wsumres2 = 0.0
    total_lines = 0.0
    sweight = 0.0
    fp_x_final_clip = []
    fp_ll_final_clip = []
    fp_ll_in_clip = []
    res_clip = []
    wei_clip = []
    scale = []

    # weights - dummy array
    wei = np.ones_like(fp_ll_new)
    # flat x array
    fp_xx_f = np.array(np.concatenate(fp_xx).ravel())

    # fit x v wavelength w/sigma-clipping
    # we remove modulo 1 pixel errors in line centers
    n_ite_mod_x = 3
    for ite in range(n_ite_mod_x):
        wsumres = 0.0
        wsumres2 = 0.0
        total_lines = 0.0
        sweight = 0.0
        fp_x_final_clip = []
        fp_ll_final_clip = []
        fp_ll_in_clip = []
        res_clip = []
        wei_clip = []
        scale = []
        res_modx = np.zeros_like(fp_xx_f)
        # loop over the orders
        for onum in range(n_fin - n_init):
            # order mask
            ord_mask = np.where(np.concatenate(fp_order).ravel() == onum + n_init)
            # get FP line pixel positions for the order
            fp_x_ord = fp_xx_f[ord_mask]
            # get new FP line wavelengths for the order
            fp_ll_new_ord = np.asarray(fp_ll_new)[ord_mask]
            # get weights for the order
            wei_ord = np.asarray(wei)[ord_mask]
            # fit sol w/sigma-clip
            # set sigma
            sigclip = 7
            # initialise the while loop
            sigmax = sigclip + 1
            # initialise mask
            mask = np.ones_like(fp_x_ord, dtype='Bool')
            while sigmax > sigclip:
                # fit on masked values
                poly_wave_sol_final[onum] = nanpolyfit(fp_x_ord[mask],
                                                       fp_ll_new_ord[mask],
                                    p['IC_LL_DEGR_FIT'], w=wei_ord[mask])[::-1]
                # get residuals
                res = fp_ll_new_ord - np.polyval(poly_wave_sol_final[onum][::-1], fp_x_ord)
                # normalise
                res = np.abs(res / np.nanmedian(np.abs(res[mask])))
                # get the max residual in sigmas
                sigmax = np.max(res[mask])
                # mask outliers
                if sigmax > sigclip:
                    mask[res >= sigclip] = False

            res_modx[ord_mask] = 2.998e5*(fp_ll_new_ord/
                                      np.polyval(poly_wave_sol_final[onum][::-1],
                                                 fp_x_ord) - 1)
            # mask input arrays for stats
            fp_x_ord = fp_x_ord[mask]
            fp_ll_new_ord = fp_ll_new_ord[mask]
            wei_ord = wei_ord[mask]
            # get final wavelengths
            fp_ll_final_ord = np.polyval(poly_wave_sol_final[onum][::-1], fp_x_ord)
            # save wave map
            wave_map_final[onum] = np.polyval(poly_wave_sol_final[onum][::-1], xpix)
            # save aux arrays
            fp_x_final_clip.append(fp_x_ord)
            fp_ll_final_clip.append(fp_ll_final_ord)
            fp_ll_in_clip.append(fp_ll_new_ord)
            # residuals in km/s
            # recalculate the residuals (not absolute value!!)
            res = fp_ll_final_ord - fp_ll_new_ord
            res_clip.append(res*speed_of_light/fp_ll_new_ord)
            wei_clip.append(wei_ord)
            # save stats
            # get the derivative of the coefficients
            poly = np.poly1d(poly_wave_sol_final[onum][::-1])
            dldx = np.polyder(poly)(fp_x_ord)
            # work out conversion factor
            convert = speed_of_light * dldx / fp_ll_final_ord
            scale.append(convert)
            # sum the weights (recursively)
            sweight += np.nansum(wei_clip[onum])
            # sum the weighted residuals in km/s
            wsumres += np.nansum(res_clip[onum] * wei_clip[onum])
            # sum the weighted squared residuals in km/s
            wsumres2 += np.nansum(wei_clip[onum] * res_clip[onum] ** 2)

        # we construct a sin/cos model of the error in line center position
        # and fit it to the residuals
        cos = np.cos(2 * np.pi * (fp_xx_f % 1))
        sin = np.sin(2 * np.pi * (fp_xx_f % 1))

        # find points that are not residual outliers
        # We fit a zeroth order polynomial, so it returns
        # outliers to the mean value.
        # set sigma
        sigclip = 7
        # initialise the while loop
        sigmax = sigclip + 1
        # initialise mask
        mask_all = np.ones_like(fp_xx_f, dtype='Bool')
        while sigmax > sigclip:
            # fit on masked values
            fitfit = nanpolyfit(fp_xx_f[mask_all],
                                res_modx[mask_all],0)
            # get residuals
            res = fp_xx_f - np.polyval(fitfit, fp_xx_f)
            # normalise
            res = np.abs(res / np.nanmedian(np.abs(res[mask_all])))
            # get the max residual in sigmas
            sigmax = np.max(res[mask_all])
            # mask outliers
            if sigmax > sigclip:
                mask_all[res >= sigclip] = False
        # create model
        acos = np.nansum(cos[mask_all] * res_modx[mask_all]) / np.nansum(cos[mask_all] ** 2)
        asin = np.nansum(sin[mask_all] * res_modx[mask_all]) / np.nansum(sin[mask_all] ** 2)
        model_sin = (cos * acos + sin * asin)
        # update the xpeak positions with model
        fp_xx_f += model_sin / 2.2

    # # loop over the orders
    # for onum in range(n_fin - n_init):
    #     # order mask
    #     ord_mask = np.where(np.concatenate(fp_order).ravel() == onum + n_init)
    #     # get FP line pixel positions for the order
    #     fp_x_ord = fp_xx[onum]
    #     # get new FP line wavelengths for the order
    #     fp_ll_new_ord = np.asarray(fp_ll_new)[ord_mask]
    #     # get weights for the order
    #     wei_ord = np.asarray(wei)[ord_mask]
    #     # fit polynomial
    #     # pargs = [fp_x_ord, fp_ll_new_ord, p['IC_LL_DEGR_FIT'], w=wei_ord]
    #     poly_wave_sol_final[onum][:-1] = nanpolyfit(fp_x_ord, fp_ll_new_ord,
    #                            p['IC_LL_DEGR_FIT']-1, w=wei_ord)[::-1]
    #     # get final wavelengths
    #     fp_ll_final_ord = np.polyval(poly_wave_sol_final[onum][::-1], fp_x_ord)
    #     # get residuals
    #     res = np.abs(fp_ll_final_ord - fp_ll_new_ord)
    #     # if residuals are large, iterative improvement
    #     while np.max(res) > p['IC_MAX_LLFIT_RMS']:
    #         # create sigma mask
    #         sig_mask = res < np.max(res)
    #         # mask input arrays
    #         fp_x_ord = fp_x_ord[sig_mask]
    #         fp_ll_new_ord = fp_ll_new_ord[sig_mask]
    #         wei_ord = wei_ord[sig_mask]
    #         # refit polynomial
    #         #pargs = [fp_x_ord, fp_ll_new_ord, p['IC_LL_DEGR_FIT'], w=wei_ord]
    #         poly_wave_sol_final[onum] = nanpolyfit(fp_x_ord, fp_ll_new_ord,
    #                                                p['IC_LL_DEGR_FIT'], w=wei_ord)[::-1]
    #         # get new final wavelengths
    #         fp_ll_final_ord = np.polyval(poly_wave_sol_final[onum][::-1],
    #                                      fp_x_ord)
    #         # get new residuals
    #         res = np.abs(fp_ll_final_ord - fp_ll_new_ord)
    #     # save wave map
    #     wave_map_final[onum] = np.polyval(poly_wave_sol_final[onum][::-1], xpix)
    #     # save aux arrays
    #     fp_x_final_clip.append(fp_x_ord)
    #     fp_ll_final_clip.append(fp_ll_final_ord)
    #     fp_ll_in_clip.append(fp_ll_new_ord)
    #     # residuals in km/s
    #     # recalculate the residuals (not absolute value!!)
    #     res = fp_ll_final_ord - fp_ll_new_ord
    #     res_clip.append(res*speed_of_light/fp_ll_new_ord)
    #     wei_clip.append(wei_ord)
    #     # save stats
    #     # get the derivative of the coefficients
    #     poly = np.poly1d(poly_wave_sol_final[onum][::-1])
    #     dldx = np.polyder(poly)(fp_x_ord)
    #     # work out conversion factor
    #     convert = speed_of_light * dldx / fp_ll_final_ord
    #     scale.append(convert)
    #     # sum the weights (recursively)
    #     sweight += np.nansum(wei_clip[onum])
    #     # sum the weighted residuals in km/s
    #     wsumres += np.nansum(res_clip[onum] * wei_clip[onum])
    #     # sum the weighted squared residuals in km/s
    #     wsumres2 += np.nansum(wei_clip[onum] * res_clip[onum] ** 2)

    # calculate the final var and mean
    total_lines = len(np.concatenate(fp_ll_in_clip))
    final_mean = wsumres / sweight
    final_var = (wsumres2 / sweight) - (final_mean ** 2)
    # log the global stats
    wmsg1 = 'On fiber {0} fit line statistic:'.format(p['FIBER'])
    wargs2 = [final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
              total_lines, 1000.0 * np.sqrt(final_var / total_lines)]
    wmsg2 = ('\tmean={0:.3f}[m/s] rms={1:.1f} {2} lines (error on mean '
             'value:{3:.4f}[m/s])'.format(*wargs2))
    WLOG(p, 'info', [wmsg1, wmsg2])

    # rest = (np.concatenate(fp_ll_final_clip)-np.concatenate(fp_ll_in_clip))\
    #        *speed_of_light/np.concatenate(fp_ll_in_clip)
    # print(1000 * np.sqrt((np.nansum(rest ** 2) / total_lines -
    #                       np.nansum(rest / total_lines) ** 2) / total_lines))

    if p['DRS_PLOT']:
        # control plot - single order - TODO move to spirouPlot
        plot_order = p['IC_WAVE_EA_PLOT_ORDER']
        plt.figure()
        # get mask for HC lines
        hc_mask = loc['ORD_T'] == plot_order
        # get hc lines
        hc_ll = loc['WAVE_CATALOG'][hc_mask]
        # plot hc data
        plt.plot(wave_map_final[plot_order - n_init], loc['HCDATA'][plot_order])
        plt.vlines(hc_ll, 0, np.max(loc['HCDATA'][plot_order]))
        plt.xlabel('Wavelength')
        plt.ylabel('Flux')

    if p['DRS_PLOT']:
        # control plot - selection of orders - TODO move to spirouPlot
        n_plot_init = 0
        n_plot_fin = np.min((n_fin-1, 5))

        plt.figure()
        # define spectral order colours
        col1 = ['black', 'grey']
        lty = ['--', ':']
        #    col2 = ['green', 'purple']
        # loop through the orders
        for order_num in range(n_plot_init, n_plot_fin):
            # set up mask for the order
            gg = loc['ORD_T'] == order_num
            # keep only lines for the order
            hc_ll = loc['WAVE_CATALOG'][gg]
            # get colours from order parity
            col1_1 = col1[np.mod(order_num, 2)]
            lty_1 = lty[np.mod(order_num, 2)]
            #        col2_1 = col2[np.mod(order_num, 2)]
            # plot hc data
            plt.plot(wave_map_final[order_num - n_init], loc['HCDATA'][order_num])
            plt.vlines(hc_ll, 0, np.max(loc['HCDATA'][order_num]), color=col1_1,
                       linestyles=lty_1)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Flux')

    safetytest = np.copy(wave_map_final)

    # # TODO test linmin fitting
    #
    # # ----------------------------------------------------------------------
    # # Fit wavelength solution to FP peaks with linear minimization
    # # ----------------------------------------------------------------------
    # loc = spirouWAVE.fit_fp_linmin(p, loc)
    # wave_map_final = loc['WAVE_MAP_FP']
    # loc['LL_OUT_2'] = wave_map_final
    # loc['LL_FINAL'] = loc['WAVE_MAP_FP']
    # loc['LL_PARAM_FINAL'] = loc['POLY_WAVE_SOL_FP']
    #
    # ----------------------------------------------------------------------
    # Do Littrow check
    # ----------------------------------------------------------------------
    #reset orders to ignore 0 in Littrow
    start = p['IC_LITTROW_ORDER_INIT_2']
    end = p['IC_LITTROW_ORDER_FINAL_2']
    # recalculate echelle orders for Littrow check
    o_orders = np.arange(start, end)
    echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
    loc['ECHELLE_ORDERS'] = echelle_order
    loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

    # Do Littrow check
    ckwargs = dict(ll=wave_map_final[start:end, :], iteration=2, log=True)
    loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

    # Plot wave solution littrow check
    if p['DRS_PLOT']:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_check_plot(p, loc, iteration=2)


    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------

    #saves for compatibility
    loc['LL_OUT_2'] = wave_map_final
    loc['LL_PARAM_2'] = poly_wave_sol_final
    p['IC_HC_N_ORD_START_2'] = n_init
    p['IC_HC_N_ORD_FINAL_2'] = n_fin
    # p['IC_LITTROW_ORDER_INIT_2'] = n_init
    loc['X_MEAN_2'] = final_mean
    loc['X_VAR_2'] = final_var


    ekwargs = dict(ll=loc['LL_OUT_2'], iteration=2)
    loc = spirouTHORCA.ExtrapolateLittrowSolution(p, loc, **ekwargs)

    # ------------------------------------------------------------------
    # Plot littrow solution
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_extrap_plot(p, loc, iteration=2)

    # ------------------------------------------------------------------
    # Join 0-47 and 47-49 solutions
    # ------------------------------------------------------------------
    loc = spirouTHORCA.JoinOrders(p, loc)

    # ------------------------------------------------------------------
    # Plot single order, wavelength-calibrated, with found lines
    # ------------------------------------------------------------------

    if p['DRS_PLOT']:
        sPlt.wave_ea_plot_single_order(p, loc)

    # ----------------------------------------------------------------------
    # Do correlation on FP spectra
    # ----------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Compute photon noise uncertainty for FP
    # ------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['FPDATA'], loc['LL_FINAL']]
    dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DRIFT_BOXSIZE'],
                   threshold=p['IC_DRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)
    # save to loc
    loc['DVRMSREF'], loc['WMEANREF'] = dvrmsref, wmeanref
    loc.set_sources(['dvrmsref', 'wmeanref'], __NAME__ + '/main()()')
    # log the estimated RV uncertainty
    wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f} m/s'
    WLOG(p, 'info', wmsg.format(p['FIBER'], wmeanref))

    # Use CCF Mask function with drift constants
    p['CCF_MASK'] = p['DRIFT_CCF_MASK']
    p['TARGET_RV'] = p['DRIFT_TARGET_RV']
    p['CCF_WIDTH'] = p['DRIFT_CCF_WIDTH']
    p['CCF_STEP'] = p['DRIFT_CCF_STEP']
    p['RVMIN'] = p['TARGET_RV'] - p['CCF_WIDTH']
    p['RVMAX'] = p['TARGET_RV'] + p['CCF_WIDTH'] + p['CCF_STEP']

    # get the CCF mask from file (check location of mask)
    loc = spirouRV.GetCCFMask(p, loc)

    # TODO Check why Blaze makes bugs in correlbin
    loc['BLAZE'] = np.ones((loc['NBO'],loc['NBPIX']))
    # set sources
    # loc.set_sources(['flat', 'blaze'], __NAME__ + '/main()')
    loc.set_source('blaze', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Do correlation on FP
    # ----------------------------------------------------------------------
    # calculate and fit the CCF
    loc['E2DSFF'] = np.array(loc['FPDATA'])
    loc.set_source('E2DSFF', __NAME__ + '/main()')
    p['CCF_FIT_TYPE'] = 1
    loc['BERV'] = 0.0
    loc['BERV_MAX'] = 0.0
    loc['BJD'] = 0.0

    # run the RV coravelation function with these parameters
    loc['WAVE_LL'] = np.array(loc['LL_FINAL'])
    loc['PARAM_LL'] = np.array(loc['LL_PARAM_FINAL'])
    loc = spirouRV.Coravelation(p, loc)

    # ----------------------------------------------------------------------
    # Update the Correlation stats with values using fiber C (FP) drift
    # ----------------------------------------------------------------------
    # get the maximum number of orders to use
    nbmax = p['CCF_NUM_ORDERS_MAX']
    # get the average ccf
    loc['AVERAGE_CCF'] = np.nansum(loc['CCF'][: nbmax], axis=0)
    # normalize the average ccf
    normalized_ccf = loc['AVERAGE_CCF'] / np.max(loc['AVERAGE_CCF'])
    # get the fit for the normalized average ccf
    ccf_res, ccf_fit = spirouRV.FitCCF(p, loc['RV_CCF'], normalized_ccf,
                                       fit_type=1)
    loc['CCF_RES'] = ccf_res
    loc['CCF_FIT'] = ccf_fit
    # get the max cpp
    loc['MAXCPP'] = np.nansum(loc['CCF_MAX']) / np.nansum(loc['PIX_PASSED_ALL'])
    # get the RV value from the normalised average ccf fit center location
    loc['RV'] = float(ccf_res[1])
    # get the contrast (ccf fit amplitude)
    loc['CONTRAST'] = np.abs(100 * ccf_res[0])
    # get the FWHM value
    loc['FWHM'] = ccf_res[2] * spirouCore.spirouMath.fwhm()
    # set the source
    keys = ['AVERAGE_CCF', 'MAXCPP', 'RV', 'CONTRAST', 'FWHM',
            'CCF_RES', 'CCF_FIT']
    loc.set_sources(keys, __NAME__ + '/main()')
    # ----------------------------------------------------------------------
    # log the stats
    wmsg = ('FP Correlation: C={0:.1f}[%] DRIFT={1:.5f}[km/s] '
            'FWHM={2:.4f}[km/s] maxcpp={3:.1f}')
    wargs = [loc['CONTRAST'], float(ccf_res[1]), loc['FWHM'], loc['MAXCPP']]
    WLOG(p, 'info', wmsg.format(*wargs))
    # ----------------------------------------------------------------------
    # rv ccf plot
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # Plot rv vs ccf (and rv vs ccf_fit)
        p['OBJNAME']='FP'
        sPlt.ccf_rv_ccf_plot(p, loc['RV_CCF'], normalized_ccf, ccf_fit)

    #TODO : Add QC of the FP CCF

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # get parameters from p
    p['QC_RMS_LITTROW_MAX'] = p['QC_HC_RMS_LITTROW_MAX']
    p['QC_DEV_LITTROW_MAX'] = p['QC_HC_DEV_LITTROW_MAX']
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # check for infinites and NaNs in mean residuals from fit
    if ~np.isfinite(loc['X_MEAN_2']):
        # add failed message to the fail message list
        fmsg = 'NaN or Inf in X_MEAN_2'
        fail_msg.append(fmsg)
        passed = False

    # iterate through Littrow test cut values
    lit_it = 2
    # checks every other value
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
        # check if min/max littrow is out of bounds
        if np.max([max_littrow, min_littrow]) > dev_littrow_max:
            fmsg = ('Littrow test (x={0}) failed (min|max dev = '
                    '{1:.2f}|{2:.2f} > {3:.2f} for order {4}|{5})')
            fargs = [x_cut_point, min_littrow, max_littrow, dev_littrow_max,
                     min_littrow_ord, max_littrow_ord]
            fail_msg.append(fmsg.format(*fargs))
            passed = False

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

    # ------------------------------------------------------------------
    # archive result in e2ds spectra
    # ------------------------------------------------------------------
    # get raw input file name
    raw_infile1 = os.path.basename(p['HCFILES'][0])
    raw_infile2 = os.path.basename(p['FPFILE'])
    tag0a = loc['HCHDR'][p['KW_OUTPUT'][0]]
    tag0b = loc['FPHDR'][p['KW_OUTPUT'][0]]
    # get wave filename
    wavefits, tag1 = spirouConfig.Constants.WAVE_FILE_NEW(p)
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
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    # set the input files
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'], value=loc['WAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    # add quality control
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
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
    hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_FWHM'], value=loc['FWHM'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_CONTRAST'],
                               value=loc['CONTRAST'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_MAXCPP'],
                               value=loc['MAXCPP'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_MASK'], value=p['CCF_MASK'])
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

    # # ------------------------------------------------------------------
    # # Save to result table
    # # ------------------------------------------------------------------
    # # calculate stats for table
    # final_mean = 1000 * loc['X_MEAN_2']
    # final_var = 1000 * loc['X_VAR_2']
    # num_lines = int(total_lines)
    # err = 1000.0 * np.sqrt(loc['X_VAR_2'] / num_lines)
    # sig_littrow = 1000 * np.array(loc['LITTROW_SIG_' + str(lit_it)])
    # # construct filename
    # wavetbl = spirouConfig.Constants.WAVE_TBL_FILE_NEW(p)
    # wavetblname = os.path.basename(wavetbl)
    # # construct and write table
    # columnnames = ['night_name', 'file_name', 'fiber', 'mean', 'rms',
    #                'N_lines', 'err', 'rms_L500', 'rms_L1000', 'rms_L1500',
    #                'rms_L2000', 'rms_L2500', 'rms_L3000', 'rms_L3500']
    # columnformats = ['{:20s}', '{:30s}', '{:3s}', '{:7.4f}', '{:6.4f}',
    #                  '{:3d}', '{:6.3f}', '{:6.2f}', '{:6.2f}', '{:6.2f}',
    #                  '{:6.2f}', '{:6.2f}', '{:6.2f}', '{:6.2f}']
    # columnvalues = [[p['ARG_NIGHT_NAME']], [p['ARG_FILE_NAMES'][0]],
    #                 [p['FIBER']], [final_mean], [final_var],
    #                 [num_lines], [err], [sig_littrow[0]],
    #                 [sig_littrow[1]], [sig_littrow[2]], [sig_littrow[3]],
    #                 [sig_littrow[4]], [sig_littrow[5]], [sig_littrow[6]]]
    # # make table
    # table = spirouImage.MakeTable(p, columns=columnnames, values=columnvalues,
    #                               formats=columnformats)
    # # merge table
    # wmsg = 'Global result summary saved in {0}'
    # WLOG(p, '', wmsg.format(wavetblname))
    # spirouImage.MergeTable(p, table, wavetbl, fmt='ascii.rst')
    #
    # # ----------------------------------------------------------------------
    # # Save resolution and line profiles to file
    # # ----------------------------------------------------------------------
    # raw_infile = os.path.basename(p['FITSFILENAME'])
    # # get wave filename
    # resfits, tag3 = spirouConfig.Constants.WAVE_RES_FILE_NEW(p)
    # resfitsname = os.path.basename(resfits)
    # WLOG(p, '', 'Saving wave resmap to {0}'.format(resfitsname))
    #
    # # make a copy of the E2DS file for the calibBD
    # # set the version
    # hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    # hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    # hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)
    #
    # # get res data in correct format
    # resdata, hdicts = spirouTHORCA.GenerateResFiles(p, loc, hdict)
    # # save to file
    # p = spirouImage.WriteImageMulti(p, resfits, resdata, hdicts=hdicts)
    #
    # # ------------------------------------------------------------------
    # # Save line list table file
    # # ------------------------------------------------------------------
    # # construct filename
    #
    # wavelltbl = spirouConfig.Constants.WAVE_LINE_FILE_NEW(p)
    # wavelltblname = os.path.split(wavelltbl)[-1]
    # # construct and write table
    # columnnames = ['order', 'll', 'dv', 'w', 'x', 'll0', 'dvdx']
    # columnformats = ['{:.0f}', '{:12.4f}', '{:13.5f}', '{:12.4f}',
    #                  '{:12.4f}', '{:12.4f}', '{:8.4f}']
    #
    #
    # columnvalues = []
    # # construct column values (flatten over orders)
    # for it in range(len(fp_x_final_clip)):
    #     for jt in range(len(fp_x_final_clip[it])):
    #         row = [float(it),
    #                fp_ll_final_clip[it][jt],
    #                res_clip[it][jt],
    #                1,
    #                fp_x_final_clip[it][jt],
    #                fp_ll_in_clip[it][jt],
    #                scale[it][jt]]
    #         columnvalues.append(row)
    #
    # # log saving
    # wmsg = 'List of lines used saved in {0}'
    # WLOG(p, '', wmsg.format(wavelltblname))
    #
    # # make table
    # columnvalues = np.array(columnvalues).T
    # table = spirouImage.MakeTable(p, columns=columnnames, values=columnvalues,
    #                               formats=columnformats)
    # # write table
    # spirouImage.WriteTable(p, table, wavelltbl, fmt='ascii.rst')
    #
    #
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

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
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
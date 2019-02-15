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

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS.spirouTHORCA import spirouWAVE

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
    tmp_wave_file = '/data/CFHT/calibDB_cfht/2018-07-30_MASTER_wave_ea_AB.fits'
    wout = spirouImage.GetWaveSolution(p, hdr=hchdr,
                                       filename=tmp_wave_file,
                                       return_wavemap=True,
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
    if p['DRS_PLOT'] > 0:
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
    if p['DRS_PLOT'] > 0:
        sPlt.wave_ea_plot_line_profiles(p, loc)

    # ----------------------------------------------------------------------
    # End plotting session
    # ----------------------------------------------------------------------
    # end interactive session
    if p['DRS_PLOT'] > 0:
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
    dopd0 = 2.450101e7  # 2.4508e7   # p['IC_FP_DOPD0']
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

    # loop over orders
    for order_num in range(n_init, n_fin):
        # get mask of HC line list for order
        mask1 = loc['ORD_T'] == order_num
        # get pixel values of found HC lines for the order
        xgau = loc['XGAU_T'][mask1]
        # get mask of central HC lines
        mask2 = 1000 < xgau
        mask2 &= xgau < 3000
        # get dv values of central HC lines
        dv = loc['DV_T'][mask1][mask2]
        # find HC line with smallest dv value
        best_line_ind = np.argmin(abs(dv))
        # get best HC line x value
        best_line_x = xgau[mask2][best_line_ind]
        hc_xx_ref.append(best_line_x)
        # calculate best HC line wavelength value
        coeffs = loc['POLY_WAVE_SOL'][order_num][::-1]
        best_line_ll = np.polyval(coeffs, best_line_x)
        hc_ll_ref.append(best_line_ll)
        # get mask of FP lines for order
        mask_fp = loc['ORDPEAK'] == order_num
        # get x values of FP lines
        x_fp = loc['XPEAK'][mask_fp]
        # Find FP line immediately after the HC line
        fp_ref_ind = np.argmin(abs(x_fp - best_line_x))
        if x_fp[fp_ref_ind] < best_line_x:
            fp_ref_ind += 1
        # interpolate and save the FP ref line wavelength
        fp_ll_ref.append(best_line_ll + (best_line_ll ** 2 / dopd0) *
                         ((x_fp[fp_ref_ind] - best_line_x) /
                          (x_fp[fp_ref_ind] - x_fp[fp_ref_ind - 1])))
        # save the FP ref line pixel position
        fp_xx_ref.append(x_fp[fp_ref_ind])
        # save the FP ref line number
        initial_peak = fp_ref_ind

        # ----------------------------------------------------------------------
        # number adjacent peaks differentially and assign wavelengths
        # ----------------------------------------------------------------------

        # differential numbering (assuming no gaps)
        dif_num = np.arange(len(x_fp)) - initial_peak
        # find gaps in x
        # get median of x difference
        med_x_diff = np.median(x_fp[1:] - x_fp[:-1])
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
        cfit_xdiff = np.polyfit(x_fp[1:][x_good_ind], x_diff[x_good_ind], 2)
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
            dif_num[x_gap_ind[0][i] + 1:] += x_jump

        # check if reference peak has been shifted
        if not dif_num[initial_peak] == 0:
            # if it has move it back to zero
            dif_num -= dif_num[initial_peak]

        # get wavelength using differential numbering and reference peak
        fp_ll.append(1 / (1 / fp_ll_ref[order_num - n_init] - dif_num / dopd0))

        # save differential numbering
        dif_n.append(dif_num)
        # save order number
        fp_order.append(np.ones(len(x_fp)) * order_num)
        # save x positions
        fp_xx.append(x_fp)

    # ----------------------------------------------------------------------
    # Plot initial and new wavelengths for an order - TODO move to spirouPLOT
    # ----------------------------------------------------------------------

    # set plot order
    plot_order = 0

    # create mask to select FP lines from plot_order only
    ind = np.where(loc['ORDPEAK'] == plot_order)
    # get new FP line wavelengths for plot_order
    fp_ll_plot = fp_ll[plot_order - n_init]
    # get FP line pixel positions for plot_order
    fp_xx_plot = loc['XPEAK'][ind]
    # determine FP line wavelengths from initial wavelength solution
    fp_ll_plot_orig = np.polyval(loc['POLY_WAVE_SOL'][plot_order][::-1],
                                 fp_xx_plot)
    # plot FP wavelength difference
    plt.figure()
    plt.plot(fp_ll_plot_orig, fp_ll_plot - fp_ll_plot_orig, 'o')
    plt.xlabel('initial FP wavelength [nm]')
    plt.ylabel('initial - new FP wavelengths [nm]')
    plt.title('FP wavelengths - order ' + str(plot_order))

    # ----------------------------------------------------------------------
    # Assign absolute FP numbers for reddest order
    # ----------------------------------------------------------------------

    # determine absolute number for reference peak of reddest order
    m_init = int(round(dopd0 / fp_ll_ref[n_fin - n_init - 1]))
    # absolute numbers for reddest order:
    # get differential numbers for reddest order peaks
    aux_n = dif_n[n_fin - n_init - 1]
    # calculate absolute peak numbers for reddest order
    m_aux = m_init - aux_n
    # set m vector
    m = m_aux
    # initialise vector of order numbers for previous order
    m_ord_prev = m_aux

    # ----------------------------------------------------------------------
    # Plot FP lines, reference HC line for reddest order -
    # TODO move to spirouPLOT
    # ----------------------------------------------------------------------
    # get FP line wavelengths for reddest order
    fp_ll_red = fp_ll[-1]
    # get wavelength of reference HC line for reddest order
    hc_ll_red = hc_ll_ref[-1]
    # get pixel position of reference HC line for reddest order
    hc_x_red = hc_xx_ref[-1]
    # plot
    plt.figure()
    plt.plot(loc['WAVE_MAP2'][n_fin - 1], fpdata[n_fin - 1])
    plt.xlabel('nm')
    plt.ylabel('e-')
    plt.title('FP order ' + str(n_fin - 1))
    for i in range(len(fp_ll_red)):
        plt.vlines(fp_ll_red[i], 0, 200000)
    plt.vlines(hc_ll_red, 0, 200000, color='green')
    plt.vlines(fp_ll_ref[n_fin - n_init - 1], 0, 200000, color='red')

    # ----------------------------------------------------------------------
    # Assign absolute FP numbers for rest of orders by wavelength matching
    # ----------------------------------------------------------------------
    # loop over orders from reddest-1 to bluest
    for i in range(n_fin - n_init - 2, -1, -1):
        # define auxiliary arrays with ll for order and previous order
        fp_ll_ord = fp_ll[i]
        fp_ll_ord_prev = fp_ll[i + 1]
        # check if overlap
        if fp_ll_ord[-1] >= fp_ll_ord_prev[0]:
            # find closest peak to last of this order in previous order
            m_match = (np.abs(fp_ll_ord_prev - fp_ll_ord[-1])).argmin()
            # get order number for last peak (take int so it's not an array)
            m_end = int(m_ord_prev[m_match])
            # define array of absolute peak numbers
            m_ord = m_end + dif_n[i][-1] - dif_n[i]
            # insert absolute order numbers at the start of m
            m = np.concatenate((m_ord, m))
            # redefine order number vector for previous order
            m_ord_prev = m_ord
        # if no overlap
        else:
            wmsg = 'no overlap for order ' + str(i) + ', estimating gap size'
            WLOG(p, 'warning', wmsg.format())

            # get fp wavelength diff for consecutive lines in orders
            fp_ll_diff = fp_ll_ord[1:] - fp_ll_ord[:-1]
            fp_ll_diff_prev = fp_ll_ord_prev[1:] - fp_ll_ord_prev[:-1]
            # mask to keep only difference between no-gap lines for both ord
            mask_ll_diff = fp_ll_diff > 0.75 * np.median(fp_ll_diff)
            mask_ll_diff &= fp_ll_diff < 1.25 * np.median(fp_ll_diff)
            mask_ll_diff_prev = fp_ll_diff_prev > 0.75 * np.median(
                fp_ll_diff_prev)
            mask_ll_diff_prev &= fp_ll_diff_prev < 1.25 * np.median(
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
            # insert absolute order numbers at the start of m
            m = np.concatenate((m_ord, m))
            # redefine order number vector for previous order
            m_ord_prev = m_ord

    # ----------------------------------------------------------------------
    # Derive d for each HC line
    # ----------------------------------------------------------------------

    # set up storage
    # effective cavity width for the HC lines
    d = []
    # 1/line number of the closest FP line to each HC line
    one_m_d = []
    # line number of the closest FP line to each HC line
    m_d = []
    one_m_d_w = []
    # wavelength of HC lines
    hc_ll_test = []

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
        # HC mask - keep best lines with small dv only
        cond1 = abs(loc['DV_T']) < 0.25
        cond2 = loc['ORD_T'] == ord_num + n_init
        hc_mask = np.where(cond1 & cond2)
        # get HC line pixel positions for the order
        hc_x_ord = loc['XGAU_T'][hc_mask]
        # get HC line wavelengths for the order
        hc_ll_ord = np.polyval(loc['POLY_WAVE_SOL'][ord_num + n_init][::-1],
                               hc_x_ord)
        # loop over HC lines in the order
        for j in range(len(hc_ll_ord)):
            # loop over FP lines in the order
            for k in range(len(fp_ll_ord) - 1):
                # find surrounding FP lines for the HC line
                if fp_ll_ord[k - 1] < hc_ll_ord[j] <= fp_ll_ord[k]:
                    # derive d for the HC line
                    t1 = hc_ll_ord[j] * m_ord[k] * (m_ord[k] + 1)
                    t2 = fp_x_ord[k] - fp_x_ord[k - 1]
                    t3a = m_ord[k] * fp_x_ord[k]
                    t3b = (m_ord[k] + 1) * fp_x_ord[k - 1]
                    t3 = t3a - t3b + hc_x_ord[j]
                    d.append(0.5 * t1 * (t2 / t3))
                    # save 1/line number of closest FP line
                    one_m_d.append(1. / m_ord[k])
                    # save 1/ weighted average of line numbers - not used
                    part1 = hc_x_ord[j] - fp_x_ord[k]
                    part2 = fp_x_ord[k - 1] - fp_x_ord[k]
                    one_m_d_w.append(1. / (part1 / part2 + m_ord[k]))
                    # save line number of closest FP line
                    m_d.append(m_ord[k])
                    # save HC line wavelength
                    hc_ll_test.append(hc_ll_ord[j])

    # log line number span
    wargs = [m_d[0], m_d[-1]]
    wmsg = 'Mode number span: {0} - {1}'
    WLOG(p, '', wmsg.format(*wargs))

    # Sigma clipping on bad d values
    # save copies of d and one_m_d for comparison
    d_all = np.copy(np.asarray(d))
    one_m_d_all = np.copy(np.asarray(one_m_d))
    # define boundaries and mask
    # critlower = np.median(d) - np.std(d) * 4.
    # critupper = np.median(d) + np.std(d) * 4.
    # sig_clip_d = np.where((d > critlower) & (d < critupper))
    # get difference in consecutive points (zero added for dimensionality)
    d_diff = np.concatenate(([0], d_all[1:] - d_all[:-1]))
    critlower = np.median(d_diff) - np.std(d_diff)
    critupper = np.median(d_diff) + np.std(d_diff)
    sig_clip_d = np.where((d_diff > critlower) & (d_diff < critupper))
    # sigma clip
    d = np.asarray(d)[sig_clip_d]
    hc_ll_test = np.asarray(hc_ll_test)[sig_clip_d]
    one_m_d = np.asarray(one_m_d)[sig_clip_d]
    # log number of points removed
    wargs = [len(d_all) - np.shape(sig_clip_d)[1]]
    wmsg = '{0} points removed by d sigma clip'
    WLOG(p, '', wmsg.format(*wargs))

    # Verification sigma clip plot - TODO move to spirouPLOT
    if (len(d_all) - np.shape(sig_clip_d)[1]) > 0:
        plt.figure()
        plt.plot(one_m_d_all, d_all, 'o')

    # ----------------------------------------------------------------------
    # Fit (1/m) vs d
    # ----------------------------------------------------------------------

    # define sorted arrays
    one_m_sort = np.asarray(one_m_d).argsort()
    one_m_d = np.asarray(one_m_d)[one_m_sort]
    d = np.asarray(d)[one_m_sort]

    # initial polynomial fit
    fit_1m_d_init = np.polyfit(one_m_d, d, 5)
    # get residuals
    res = d - np.polyval(fit_1m_d_init, one_m_d)
    # mask points at +/- 1 sigma
    sig_clip = abs(res) < np.std(res)
    one_m_d = one_m_d[sig_clip]
    d = d[sig_clip]

    # second polynomial fit
    fit_1m_d = np.polyfit(one_m_d, d, 10)
    fit_1m_d_func = np.poly1d(fit_1m_d)

    # plot 1/m vs d and the fitted polynomial - TODO move to spirouPLOT
    plt.figure()
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

    # ----------------------------------------------------------------------
    # Update FP peak wavelengths
    # ----------------------------------------------------------------------

    # define storage
    fp_ll_new = []

    # loop over peak numbers
    for i in range(len(m)):
        # calculate wavelength from fit to 1/m vs d
        fp_ll_new.append(2 * fit_1m_d_func(1. / m[i]) / m[i])

    # plot by order - TODO move to spirouPLOT?

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
    # Fit wavelength solution from FP peaks - TODO
    # ----------------------------------------------------------------------

    # set up storage arrays
    xpix = np.arange(loc['NBPIX'])
    wave_map_final = np.zeros((n_fin - n_init, loc['NBPIX']))
    poly_wave_sol_final = np.zeros_like(loc['WAVEPARAMS'])
    wsumres = 0.0
    wsumres2 = 0.0
    total_lines = 0.0

    # loop over the orders
    for onum in range(n_fin - n_init):
        # order mask
        ord_mask = np.where(np.concatenate(fp_order).ravel() == onum + n_init)
        # get FP line pixel positions for the order
        fp_x_ord = fp_xx[onum]
        # get new FP line wavelengths for the order
        fp_ll_new_ord = np.asarray(fp_ll_new)[ord_mask]
        # fit polinomial
        pargs = [fp_x_ord, fp_ll_new_ord, p['IC_LL_DEGR_FIT']]
        poly_wave_sol_final[onum] = np.polyfit(*pargs)[::-1]
        # get final wavelengths
        fp_ll_final_ord = np.polyval(poly_wave_sol_final[onum][::-1], fp_x_ord)
        # get residuals
        res = np.abs(fp_ll_final_ord - fp_ll_new_ord)
        # if residuals are large, iterative improvement
        while np.max(res) > p['IC_MAX_LLFIT_RMS']:
            # create sigma mask
            sig_mask = res < np.max(res)
            # mask input arrays
            fp_x_ord = fp_x_ord[sig_mask]
            fp_ll_new_ord = fp_ll_new_ord[sig_mask]
            # refit polinomial
            pargs = [fp_x_ord, fp_ll_new_ord, p['IC_LL_DEGR_FIT']]
            poly_wave_sol_final[onum] = np.polyfit(*pargs)[::-1]
            # get new final wavelengths
            fp_ll_final_ord = np.polyval(poly_wave_sol_final[onum][::-1],
                                         fp_x_ord)
            # get new residuals
            res = np.abs(fp_ll_final_ord - fp_ll_new_ord)
        # save wave map
        wave_map_final[onum] = np.polyval(poly_wave_sol_final[onum][::-1], xpix)
        # save stats
        # get the derivative of the coefficients
        poly = np.poly1d(poly_wave_sol_final[onum][::-1])
        dxdl = np.polyder(poly)(fp_x_ord)
        # work out conversion factor
        convert = speed_of_light / (dxdl * fp_ll_final_ord)
        # sum the residuals in km/s
        wsumres += np.sum(res * convert)
        # sum the weighted squared residuals in km/s
        wsumres2 += np.sum((res * convert) ** 2)
        # total lines
        total_lines += len(fp_x_ord)
    # calculate the final var and mean
    final_mean = wsumres
    final_var = wsumres2 - (final_mean ** 2)
    # log the global stats
    wmsg1 = 'On fiber {0} fit line statistic:'.format(p['FIBER'])
    wargs2 = [final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
              total_lines, 1000.0 * np.sqrt(final_var / total_lines)]
    wmsg2 = ('\tmean={0:.3f}[m/s] rms={1:.1f} {2} lines (error on mean '
             'value:{3:.2f}[m/s])'.format(*wargs2))
    WLOG(p, 'info', [wmsg1, wmsg2])

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

    # control plot - selection of orders - TODO move to spirouPlot

    n_plot_init = 0
    n_plot_fin = 5

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

    # ----------------------------------------------------------------------
    # Do Littrow check
    # ----------------------------------------------------------------------

    # calculate echelle orders
    o_orders = np.arange(n_init, n_fin)
    echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
    loc['ECHELLE_ORDERS'] = echelle_order
    loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

    # Do Littrow check
    ckwargs = dict(ll=wave_map_final, iteration=2, log=True)
    loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

    # Plot wave solution littrow check
    if p['DRS_PLOT'] > 0:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_check_plot(p, loc, iteration=2)

    # ----------------------------------------------------------------------
    # archive result in e2ds spectra -TODO
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Quality control - TODO
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Update the calibration data base - TODO
    # ----------------------------------------------------------------------

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

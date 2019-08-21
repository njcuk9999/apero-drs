#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FP wavelength function

Created on 2017-12-19 at 16:20

@author: mhobson

"""
from __future__ import division
import numpy as np
from numpy.polynomial import chebyshev
from astropy import constants as cc
from astropy import units as uu
import os
import warnings
import itertools

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouRV
from SpirouDRS.spirouCore import spirouMath
from SpirouDRS.spirouCore.spirouMath import nanpolyfit


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouWAVE.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# User functions
# =============================================================================
def do_hc_wavesol(p, loc):
    """
    Calculate the wavelength solution from the HC file
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            log_opt: string, log option, normally the program name
            DRS_PLOT: bool, if True do plots else do not
            FIBER: string, the fiber type (i.e. AB or A or B or C)
            WAVE_MODE_HC: int, the solution method

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            HCDATA: numpy array (2D), the image data
            HCHDR: dictionary, the header dictionary for HCDATA

    :return:
    """

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
    loc = generate_wave_map(p, loc)

    # ----------------------------------------------------------------------
    # Create new wavelength solution (method 0, old cal_HC_E2DS_EA)
    # ----------------------------------------------------------------------
    if p['WAVE_MODE_HC'] == 0:

        # ---------------------------------------------------------------------
        # Find Gaussian Peaks in HC spectrum
        # ---------------------------------------------------------------------
        loc = find_hc_gauss_peaks(p, loc)

        # ---------------------------------------------------------------------
        # Start plotting session
        # ---------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            # start interactive plot
            sPlt.start_interactive_session(p)

        # ---------------------------------------------------------------------
        # Fit Gaussian peaks (in triplets) to
        # ---------------------------------------------------------------------
        loc = fit_gaussian_triplets(p, loc)

        # ---------------------------------------------------------------------
        # Generate Resolution map and line profiles
        # ---------------------------------------------------------------------
        # log progress
        wmsg = 'Generating resolution map and calculating line spread function'
        WLOG(p, '', wmsg)
        # generate resolution map
        loc = generate_resolution_map(p, loc)
        # map line profile map
        if p['DRS_PLOT'] > 0:
            sPlt.wave_ea_plot_line_profiles(p, loc)

        # ---------------------------------------------------------------------
        # End plotting session
        # ---------------------------------------------------------------------
        # end interactive session
        if p['DRS_PLOT'] > 0:
            sPlt.end_interactive_session(p)

        # ----------------------------------------------------------------------
        # Set up all_lines storage
        # ----------------------------------------------------------------------

        # initialise up all_lines storage
        all_lines_1 = []

        # get parameters from p
        n_ord_start = p['WAVE_N_ORD_START']
        n_ord_final = p['WAVE_N_ORD_FINAL']

        # get values from loc:
        # line centers in pixels
        xgau = np.array(loc['XGAU_T'])
        # distance from catalogue in km/s - used for sanity checks
        dv = np.array(loc['DV_T'])
        # fitted polynomials per order
        fit_per_order = np.array(loc['POLY_WAVE_SOL'])
        # equivalent width of fitted gaussians to each line (in pixels)
        ew = np.array(loc['EW_T'])
        # amplitude  of fitted gaussians to each line
        peak = np.array(loc['PEAK_T'])
        # catalogue line amplitude
        amp_catalog = np.array(loc['AMP_CATALOG'])
        # catalogue line wavelength
        wave_catalog = np.array(loc['WAVE_CATALOG'])
        # spectral order for each line
        ord_t = np.array(loc['ORD_T'])

        # loop through orders
        for iord in range(n_ord_start, n_ord_final):
            # keep relevant lines
            # -> right order
            # -> finite dv
            gg = (ord_t == iord) & (np.isfinite(dv))
            # put lines into ALL_LINES structure
            # reminder:
            # gparams[0] = output wavelengths
            # gparams[1] = output sigma(gauss fit width)
            # gparams[2] = output amplitude(gauss fit)
            # gparams[3] = difference in input / output wavelength
            # gparams[4] = input amplitudes
            # gparams[5] = output pixel positions
            # gparams[6] = output pixel sigma width (gauss fit width in pixels)
            # gparams[7] = output weights for the pixel position

            # dummy array for weights
            test = np.ones(np.shape(xgau[gg]), 'd') * 1e4
            # get the final wavelength value for each peak in the order
            output_wave_1 = np.polyval(fit_per_order[iord][::-1], xgau[gg])
            # convert the pixel equivalent width to wavelength units
            xgau_ew_ini = xgau[gg] - ew[gg] / 2
            xgau_ew_fin = xgau[gg] + ew[gg] / 2
            ew_ll_ini = np.polyval(fit_per_order[iord, :], xgau_ew_ini)
            ew_ll_fin = np.polyval(fit_per_order[iord, :], xgau_ew_fin)
            ew_ll = ew_ll_fin - ew_ll_ini
            # put all lines in the order into single array
            gau_params = np.column_stack((output_wave_1, ew_ll, peak[gg],
                                          wave_catalog[gg] - output_wave_1,
                                          amp_catalog[gg],
                                          xgau[gg], ew[gg], test))
            # append the array for the order into a list
            all_lines_1.append(gau_params)

        # add to loc
        loc['ALL_LINES_1'] = all_lines_1
        loc['LL_PARAM_1'] = np.array(fit_per_order)
        loc['LL_OUT_1'] = np.array(loc['WAVE_MAP2'])
        loc.set_sources(['ALL_LINES_1', 'LL_PARAM_1'], __NAME__ + '/main()')

        # For compatibility w/already defined functions, I need to save
        # here all_lines_2
        all_lines_2 = list(all_lines_1)
        loc['ALL_LINES_2'] = all_lines_2

        # ------------------------------------------------------------------
        # Littrow test
        # ------------------------------------------------------------------

        start = p['IC_LITTROW_ORDER_INIT_1']
        end = p['IC_LITTROW_ORDER_FINAL_1']

        # calculate echelle orders
        o_orders = np.arange(start, end)
        echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
        loc['ECHELLE_ORDERS'] = echelle_order
        loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

        # Do Littrow check
        ckwargs = dict(ll=loc['LL_OUT_1'][start:end, :], iteration=1, log=True)
        loc = calculate_littrow_sol(p, loc, **ckwargs)

        # Plot wave solution littrow check
        if p['DRS_PLOT'] > 0:
            # plot littrow x pixels against fitted wavelength solution
            sPlt.wave_littrow_check_plot(p, loc, iteration=1)

        # ------------------------------------------------------------------
        # extrapolate Littrow solution
        # ------------------------------------------------------------------
        ekwargs = dict(ll=loc['LL_OUT_1'], iteration=1)
        loc = extrapolate_littrow_sol(p, loc, **ekwargs)

        # ------------------------------------------------------------------
        # Plot littrow solution
        # ------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            # plot littrow x pixels against fitted wavelength solution
            sPlt.wave_littrow_extrap_plot(p, loc, iteration=1)

    return loc


def do_fp_wavesol(p, loc):
    """
    Calculate the wavelength solution from the HC file
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            log_opt: string, log option, normally the program name
            DRS_PLOT: bool, if True do plots else do not
            FIBER: string, the fiber type (i.e. AB or A or B or C)
            WAVE_MODE_HC: int, the solution method

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            HCDATA: numpy array (2D), the HC image data
            HCHDR: dictionary, the header dictionary for HCDATA
            FPDATA: numpy array (2D), the image data
            FPHDR: dictionary, the header dictionary for FPDATA

    :return: loc
    """

    # ------------------------------------------------------------------
    # Incorporate FP into solution
    # ------------------------------------------------------------------
    # Copy LL_OUT_1 and LL_PARAM_1 into new constants (for FP integration)
    loc['LITTROW_EXTRAP_SOL_1'] = np.array(loc['LL_OUT_1'])
    loc['LITTROW_EXTRAP_PARAM_1'] = np.array(loc['LL_PARAM_1'])

    # ------------------------------------------------------------------
    # Using the Bauer15 (WAVE_E2DS_EA) method:
    # ------------------------------------------------------------------
    if p['WAVE_MODE_FP'] == 0:
        # ------------------------------------------------------------------
        # Find FP lines
        # ------------------------------------------------------------------
        # print message to screen
        wmsg = 'Identification of lines in reference file: {0}'
        WLOG(p, '', wmsg.format(p['FPFILE']))

        # ------------------------------------------------------------------
        # Get the FP solution
        # ------------------------------------------------------------------

        loc = fp_wavelength_sol_new(p, loc)

        # ------------------------------------------------------------------
        # FP solution plots
        # ------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            # Plot the FP extracted spectrum against wavelength solution
            sPlt.wave_plot_final_fp_order(p, loc, iteration=1)
            # Plot the measured FP cavity width offset against line number
            sPlt.wave_local_width_offset_plot(p, loc)
            # Plot the FP line wavelength residuals
            sPlt.wave_fp_wavelength_residuals(p, loc)

        # ------------------------------------------------------------------
        # Create new wavelength solution
        # ------------------------------------------------------------------

        start = p['WAVE_N_ORD_START']
        end = p['WAVE_N_ORD_FINAL']

        # recalculate echelle orders for Fit1DSolution
        o_orders = np.arange(start, end)
        echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
        loc['ECHELLE_ORDERS'] = echelle_order
        loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

        # select the orders to fit
        lls = loc['LITTROW_EXTRAP_SOL_1'][start:end]
        loc = fit_1d_solution(p, loc, lls, iteration=2)
        # from here, LL_OUT_2 wil be 0-47

    # ------------------------------------------------------------------
    # Using the C Lovis (WAVE_NEW_2) method:
    # ------------------------------------------------------------------
    elif p['WAVE_MODE_FP'] == 1:
        # ------------------------------------------------------------------
        # Find FP lines
        # ------------------------------------------------------------------
        # print message to screen
        wmsg = 'Identification of lines in reference file: {0}'
        WLOG(p, '', wmsg.format(p['FPFILE']))

        # get FP peaks (calls spirouRV functions)
        loc = find_fp_lines_new(p, loc)

        # get parameters from p
        n_init = p['WAVE_N_ORD_START']  # 0
        n_fin = p['WAVE_N_ORD_FINAL']    # 47 note: no lines in 48 from calHC
        dopd0 = p['IC_FP_DOPD0']

        # set up storage
        # FP peak wavelengths
        fp_ll = []
        # FP peak orders
        fp_order = []
        # FP peak pixel centers
        fp_xx = []
        # FP peak differential numbering
        dif_n = []
        # FP peak amplitudes
        fp_amp = []

        # loop over orders
        for order_num in range(n_init, n_fin):
            # ------------------------------------------------------------------
            # Number FP peaks differentially and identify gaps
            # ------------------------------------------------------------------
            # get mask of FP lines for order
            mask_fp = loc['ORDPEAK'] == order_num
            # get x values of FP lines
            x_fp = loc['XPEAK'][mask_fp]
            # get amplitudes of FP lines (to save)
            amp_fp = loc['AMPPEAK'][mask_fp]
            # get 30% blaze mask
            with warnings.catch_warnings(record=True) as _:
                mb = np.where(loc['BLAZE'][order_num] > p['WAVE_BLAZE_THRESH'] *
                              np.nanmax(loc['BLAZE'][order_num]))
            # keep only x values at above 30% blaze
            amp_fp = amp_fp[np.logical_and(np.nanmax(mb) > x_fp,
                                       np.nanmin(mb) < x_fp)]
            x_fp = x_fp[np.logical_and(np.nanmax(mb) > x_fp,
                                       np.nanmin(mb) < x_fp)]
            # initial differential numbering (assuming no gaps)
            peak_num_init = np.arange(len(x_fp))
            # find gaps in x
            # get array of x differences
            x_diff = x_fp[1:] - x_fp[:-1]
            # get median of x difference
            med_x_diff = np.nanmedian(x_diff)
            # get indices where x_diff differs too much from median
            cond1 = x_diff < p['WAVE_FP_XDIF_MIN'] * med_x_diff
            cond2 = x_diff > p['WAVE_FP_XDIF_MAX'] * med_x_diff
            x_gap_ind = np.where(cond1 | cond2)
            # get the opposite mask (no-gap points)
            cond3 = x_diff > p['WAVE_FP_XDIF_MIN'] * med_x_diff
            cond4 = x_diff < p['WAVE_FP_XDIF_MAX'] * med_x_diff
            x_good_ind = np.where(cond3 & cond4)
            # fit x_fp v x_diff for good points
            cfit_xdiff = nanpolyfit(x_fp[1:][x_good_ind], x_diff[x_good_ind], 2)
            # loop over gap points
            for i in range(np.shape(x_gap_ind)[1]):
                # get estimated xdiff value from the fit
                x_diff_aux = np.polyval(cfit_xdiff, x_fp[1:][x_gap_ind[0][i]])
                # estimate missed peaks
                x_jump = np.round((x_diff[x_gap_ind[0][i]] / x_diff_aux)) - 1
                # add the jump
                peak_num_init[x_gap_ind[0][i] + 1:] += int(x_jump)

            # Calculate original (HC sol) FP wavelengths
            fp_ll.append(np.polyval(loc['POLY_WAVE_SOL'][order_num][::-1],
                                    x_fp))

            # save differential numbering
            dif_n.append(peak_num_init)
            # save order number
            fp_order.append(np.ones(len(x_fp)) * order_num)
            # save x positions
            fp_xx.append(x_fp)
            # save amplitudes
            fp_amp.append(amp_fp)

        # ----------------------------------------------------------------------
        # Assign absolute FP numbers for reddest order
        # ----------------------------------------------------------------------

        # determine absolute number for reference peak of reddest order
        # take reddest FP line
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

        # loop over orders from reddest-1 to bluest
        for ord_num in range(n_fin - n_init - 2, -1, -1):
            # define auxiliary arrays with ll for order and previous order
            fp_ll_ord = fp_ll[ord_num]
            fp_ll_ord_prev = fp_ll[ord_num + 1]
            # define median ll diff for both orders
            fp_ll_diff = np.nanmedian(fp_ll_ord[1:] - fp_ll_ord[:-1])
            fp_ll_diff_prev = np.nanmedian(fp_ll_ord_prev[1:] -
                                           fp_ll_ord_prev[:-1])
            # check if overlap
            if fp_ll_ord[-1] >= fp_ll_ord_prev[0]:
                # get overlapping peaks for both
                # allow WAVE_FP_LL_OFFSET*lldiff offsets
                mask_ord_over = fp_ll_ord >= fp_ll_ord_prev[0] - \
                                p['WAVE_FP_LL_OFFSET'] * fp_ll_diff_prev
                fp_ll_ord_over = fp_ll_ord[mask_ord_over]
                mask_prev_over = fp_ll_ord_prev <= fp_ll_ord[-1] + \
                                 p['WAVE_FP_LL_OFFSET'] * fp_ll_diff
                fp_ll_prev_over = fp_ll_ord_prev[mask_prev_over]
                # loop over peaks to find closest match
                mindiff_peak = []
                mindiff_peak_ind = []
                for j in range(len(fp_ll_ord_over)):
                    # get differences for peak j
                    diff = np.abs(fp_ll_prev_over - fp_ll_ord_over[j])
                    # save the minimum and its index
                    mindiff_peak.append(np.min(diff))
                    mindiff_peak_ind.append(np.argmin(diff))
                # get the smallest difference and its index
                mindiff_all = np.min(mindiff_peak)
                mindiff_all_ind = np.argmin(mindiff_peak)

                # check that smallest difference is in fact a true line match
                if mindiff_all < p['WAVE_FP_LL_OFFSET'] * fp_ll_diff:
                    # set the match m index as the one for the smallest diff
                    m_match_ind = mindiff_peak_ind[mindiff_all_ind]
                    # get line number for peak with smallest difference
                    m_end = m_ord_prev[mask_prev_over][m_match_ind]
                    # get differential peak number for peak with smallest diff
                    dif_n_match = dif_n[ord_num][mask_ord_over][mindiff_all_ind]
                    # define array of absolute peak numbers for the order
                    m_ord = m_end + dif_n_match - dif_n[ord_num]
                # if not treat as no overlap
                else:
                    m_ord = no_overlap_match_calc(p, ord_num, fp_ll_ord,
                                                  fp_ll_ord_prev, fp_ll_diff,
                                                  fp_ll_diff_prev, m_ord_prev,
                                                  dif_n)
            # if no overlap
            else:
                m_ord = no_overlap_match_calc(p, ord_num, fp_ll_ord,
                                              fp_ll_ord_prev, fp_ll_diff,
                                              fp_ll_diff_prev, m_ord_prev,
                                              dif_n)
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
        # wavelength of HC lines
        hc_ll_test = []
        # pixel value of kept HC lines
        hc_xx_test = []
        # order of kept hc lines
        hc_ord_test = []

        # save mask for m(x) fits
        xm_mask = []
        # loop over orders
        for ord_num in range(n_fin - n_init):
            # create order mask
            ind_ord = np.where(np.concatenate(fp_order).ravel() == ord_num + n_init)
            # get FP line pixel positions for the order
            fp_x_ord = fp_xx[ord_num]
            # get FP line numbers for the order
            m_ord = m[ind_ord]
            # HC mask for the order - keep best lines (small dv) only
            cond1 = abs(loc['DV_T']) < p['WAVE_DV_MAX']
            cond2 = loc['ORD_T'] == ord_num + n_init
            hc_mask = np.where(cond1 & cond2)
            # get HC line pixel positions for the order
            hc_x_ord = loc['XGAU_T'][hc_mask]
            # get 30% blaze mask
            with warnings.catch_warnings(record=True) as _:
                mb = np.where(loc['BLAZE'][ord_num] > p['WAVE_BLAZE_THRESH'] *
                              np.nanmax(loc['BLAZE'][ord_num]))
            # keep only x values at above 30% blaze
            blaze_mask = np.logical_and(np.nanmax(mb) > hc_x_ord,
                                        np.nanmin(mb) < hc_x_ord)
            hc_x_ord = hc_x_ord[blaze_mask]
            # get corresponding catalogue lines from loc
            hc_ll_ord_cat = loc['WAVE_CATALOG'][hc_mask][blaze_mask]

            # fit x vs m for FP lines w/sigma-clipping
            coeff_xm, mask = sigclip_polyfit(p, fp_x_ord, m_ord,
                                             p['IC_LL_DEGR_FIT'])
            # save coefficients
            coeff_xm_all.append(coeff_xm)
            # save dispersion
            xm_disp.append(np.std(m_ord[mask] - np.polyval(coeff_xm, fp_x_ord[mask])))
            # save mask
            xm_mask.append(mask)

            # get fractional m for HC lines from fit
            m_hc = np.polyval(coeff_xm, hc_x_ord)
            # get cavity width for HC lines from FP equation
            d_hc = m_hc * hc_ll_ord_cat / 2.
            # save in arrays:
            # cavity width for hc lines
            d.append(d_hc)
            # 1/m for HC lines
            one_m_d.append(1 / m_hc)
            # m for HC lines
            m_d.append(m_hc)
            # catalogue wavelengths
            hc_ll_test.append(hc_ll_ord_cat)
            # HC line centers (pixel position)
            hc_xx_test.append(hc_x_ord)
            # HC line orders
            hc_ord_test.append((ord_num + n_init) * np.ones_like(hc_x_ord))

        # residuals plot
        if p['DRS_PLOT'] and p['DRS_DEBUG'] > 0:
            sPlt.fp_m_x_residuals(p, fp_order, fp_xx, m, xm_mask, coeff_xm_all)

        # flatten arrays
        one_m_d = np.concatenate(one_m_d).ravel()
        d = np.concatenate(d).ravel()
        m_d = np.concatenate(m_d).ravel()
        hc_ll_test = np.concatenate(hc_ll_test).ravel()
        hc_ord_test = np.concatenate(hc_ord_test).ravel()

        # log absolute peak number span
        wargs = [round(m_d[0]), round(m_d[-1])]
        wmsg = 'Mode number span: {0} - {1}'
        WLOG(p, '', wmsg.format(*wargs))

        # TODO: GOT TO HERE IN TERRAPIPE CONVERSION (2019-08-21)

        # ----------------------------------------------------------------------
        # Fit (1/m) vs d
        # ----------------------------------------------------------------------

        # get the update cavity value from p
        update_cavity = p['WAVE_UPDATE_CAVITY']

        # check if cavity fits exist, else they need to be created
        m_d_path = os.path.join(p['DRS_ROOT'], 'SpirouDRS/data/wavelength_cats',
                                'cavity_length_m_fit.dat')
        ll_d_path = os.path.join(p['DRS_ROOT'], 'SpirouDRS/data/wavelength_cats'
                                 , 'cavity_length_ll_fit.dat')
        #
        if not os.path.exists(m_d_path):
            wmsg = 'WAVE_UPDATE_CAVITY = False but m vs cavity length fit ' \
                   'does not exist; fits will be created'
            WLOG(p, 'warning', wmsg)
            update_cavity = True
        elif not os.path.exists(ll_d_path):
            wmsg = 'WAVE_UPDATE_CAVITY = False but ll vs cavity length fit ' \
                   'does not exist; fits will be created'
            WLOG(p, 'warning', wmsg)
            update_cavity = True

        if update_cavity:
            # define sorted arrays
            one_m_sort = np.asarray(one_m_d).argsort()
            one_m_d = np.asarray(one_m_d)[one_m_sort]
            d = np.asarray(d)[one_m_sort]

            # polynomial fit for d vs 1/m
            fit_1m_d = nanpolyfit(one_m_d, d, 9)
            fit_1m_d_func = np.poly1d(fit_1m_d)
            res_d_final = d - fit_1m_d_func(one_m_d)

            # fit d v wavelength w/sigma-clipping
            fit_ll_d, mask = sigclip_polyfit(p, hc_ll_test, d, degree=9)

            # plot d vs 1/m fit and residuals
            if p['DRS_PLOT']:
                sPlt.interpolated_cavity_width_one_m_hc(p, one_m_d, d, m_init,
                                                    fit_1m_d_func, res_d_final)

            # write polynomial fits to files
            np.savetxt(m_d_path, fit_1m_d)
            np.savetxt(ll_d_path, fit_ll_d)
        else:
            # read fit coefficients from files
            fit_1m_d = np.genfromtxt(m_d_path)
            fit_ll_d = np.genfromtxt(ll_d_path)
            fit_1m_d_func = np.poly1d(fit_1m_d)
            # get achromatic cavity change - ie shift
            residual = d - np.polyval(fit_ll_d, hc_ll_test)
            # update coeffs with mean shift
            fit_ll_d[-1] += np.nanmedian(residual)

        fitval = np.polyval(fit_ll_d, hc_ll_test)

        if p['DRS_PLOT']:
            # plot wavelength vs d and the fitted polynomial
            sPlt.interpolated_cavity_width_ll_hc(p, hc_ll_test, d, fp_ll, fitval)

        # ----------------------------------------------------------------------
        # Update FP peak wavelengths
        # ----------------------------------------------------------------------

        # define storage
        fp_ll_new = []

        # get the fitting mode from p
        fp_cavfit_mode = p['WAVE_FP_CAVFIT_MODE']

        if fp_cavfit_mode == 0:
            # derive using 1/m vs d fit
            # loop over peak numbers
            for i in range(len(m)):
                # calculate wavelength from fit to 1/m vs d
                fp_ll_new.append(2 * fit_1m_d_func(1. / m[i]) / m[i])
        elif fp_cavfit_mode == 1:
            # from the d v wavelength fit - iterative fit
            fp_ll_new = np.ones_like(m) * 1600.
            for ite in range(6):
                recon_d = np.polyval(fit_ll_d, fp_ll_new)
                fp_ll_new = recon_d / m * 2

        # save to loc (flattened)
        loc['FP_LL_NEW'] = np.array(fp_ll_new)
        loc['FP_XX_NEW'] = np.array(np.concatenate(fp_xx).ravel())
        loc['FP_ORD_NEW'] = np.array(np.concatenate(fp_order).ravel())
        loc['FP_AMP_NEW'] = np.array(np.concatenate(fp_amp).ravel())
        # duplicate for saving
        loc['FP_XX_INIT'] = np.array(np.concatenate(fp_xx).ravel())

        # plot old-new wavelength difference
        if p['DRS_PLOT']:
            sPlt.fp_ll_difference(p, loc)

        # ----------------------------------------------------------------------
        # Fit wavelength solution from FP peaks
        # ----------------------------------------------------------------------

        # select fitting method:
        fp_llfit_mode = p['WAVE_FP_LLFIT_MODE']

        if fp_llfit_mode == 0:
            # call fit_1d_solution
            # set up ALL_LINES_2 with FP lines
            fp_ll_ini = np.concatenate(fp_ll).ravel()
            loc['ALL_LINES_2'] = insert_fp_lines(p, loc['FP_LL_NEW'], fp_ll_ini,
                                                 loc['ALL_LINES_2'],
                                                 loc['FP_ORD_NEW'],
                                                 loc['FP_XX_NEW'], loc['FP_AMP_NEW'])
            # select the orders to fit
            lls = loc['LITTROW_EXTRAP_SOL_1'][n_init:n_fin]
            # fit the solution
            loc = fit_1d_solution(p, loc, lls, iteration=2)

        elif fp_llfit_mode == 1:
            # call fit_1d_solution_sigclip
            # weights - dummy array
            loc['FP_WEI'] = np.ones_like(fp_ll_new)
            # fit the solution
            loc = fit_1d_solution_sigclip(p, loc)

        # Multi-order HC lines plot
        if p['DRS_PLOT'] and p['DRS_DEBUG'] > 0:
            # check the orders to be plotted are sensible
            if p['WAVE_PLOT_MULTI_INIT'] >= p['WAVE_N_ORD_FINAL']:
                wmsg = 'First order for multi-order plot, {0}, higher than ' \
                       'final wavelength solution order {1}; no plot created'
                WLOG(p, 'warning', wmsg.format(p['WAVE_PLOT_MULTI_INIT'],
                                               p['WAVE_N_ORD_FINAL']))
            else:
                sPlt.wave_plot_multi_order(p, hc_ll_test, hc_ord_test,
                                           loc['LL_OUT_2'], loc['HCDATA'])

        # # TODO test linmin fitting

        # ------------------------------------------------------------------
        # Saves for compatibility w/already defined functions
        # ------------------------------------------------------------------
        p['IC_HC_N_ORD_START_2'] = n_init
        p['IC_HC_N_ORD_FINAL_2'] = n_fin
        # p['IC_LITTROW_ORDER_INIT_2'] = n_init

    # ----------------------------------------------------------------------
    # LITTROW SECTION - common to all methods
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # Do Littrow check
    # ----------------------------------------------------------------------
    # reset orders to ignore 0 in Littrow
    start = p['IC_LITTROW_ORDER_INIT_2']
    end = p['IC_LITTROW_ORDER_FINAL_2']
    # recalculate echelle orders for Littrow check
    o_orders = np.arange(start, end)
    echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
    loc['ECHELLE_ORDERS'] = echelle_order
    loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

    # Do Littrow check
    ckwargs = dict(ll=loc['LL_OUT_2'][start:end, :], iteration=2, log=True)
    loc = calculate_littrow_sol(p, loc, **ckwargs)

    # Plot wave solution littrow check
    if p['DRS_PLOT']:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_check_plot(p, loc, iteration=2)

    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------
    ekwargs = dict(ll=loc['LL_OUT_2'], iteration=2)
    loc = extrapolate_littrow_sol(p, loc, **ekwargs)

    # ------------------------------------------------------------------
    # Plot littrow solution
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_extrap_plot(p, loc, iteration=2)

    # ------------------------------------------------------------------
    # Join 0-47 and 47-49 solutions
    # ------------------------------------------------------------------
    loc = join_orders(p, loc)

    # ------------------------------------------------------------------
    # Plot single order, wavelength-calibrated, with found lines
    # ------------------------------------------------------------------

    if p['DRS_PLOT'] > 0:
        sPlt.wave_ea_plot_single_order(p, loc)

    # ----------------------------------------------------------------------
    # FP CCF COMPUTATION - common to all methods
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
    loc['BLAZE'] = np.ones((loc['NBO'], loc['NBPIX']))
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
    normalized_ccf = loc['AVERAGE_CCF'] / np.nanmax(loc['AVERAGE_CCF'])
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
    if p['DRS_PLOT'] > 0:
        # Plot rv vs ccf (and rv vs ccf_fit)
        p['OBJNAME'] = 'FP'
        sPlt.ccf_rv_ccf_plot(p, loc['RV_CCF'], normalized_ccf, ccf_fit)

    # TODO : Add QC of the FP CCF once they are defined

    return loc


def get_lamp_parameters(p, header, filename=None, kind=None):
    """
    Get lamp parameters from either a specified lamp type="kind" or a filename
    or from p['ARG_FILE_NAMES'][0] (if no filename or kind defined)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LAMPS: list of strings, the different allowed lamp types
            log_opt: string, log option, normally the program name
            KW_CREF: string, the HEADER keyowrd store of the reference fiber
            KW_CCAS: string, the HEADER keyword store of the science fiber

    :param header: e2ds hc fitsfile header
    :param filename: string or None, the filename to check for the lamp
                     substring in
    :param kind: string or None, the lamp type

    :return p: parameter dictionary, the updated parameter dictionary
            Adds the following:
                LAMP_TYPE: string, the type of lamp (e.g. UNe or TH)
                IC_LL_LINE_FILE: string, the file name of the line list to use
                IC_CAT_TYPE: string, the line list catalogue type
    """

    func_name = __NAME__ + '.get_lamp_parameters()'
    # get relevant (cass/ref) fiber position (for lamp identification)
    gkwargs = dict(return_value=True, dtype=str)
    if p['FIBER'] == 'C':
        p['FIB_POS'] = spirouImage.ReadParam(p, header, 'kw_CREF', **gkwargs)
        p['FIB_POS_ID'] = p['kw_CREF'][0]
    elif p['FIBER'] in ['AB', 'A', 'B']:
        p['FIB_POS'] = spirouImage.ReadParam(p, header, 'kw_CCAS', **gkwargs)
        p['FIB_POS_ID'] = p['kw_CCAS'][0]
    else:
        emsg1 = ('Fiber position cannot be identified for fiber={0}'
                 .format(p['FIB_TYP']))
        emsg2 = '    function={0}'.format(__NAME__)
        WLOG(p, 'error', [emsg1, emsg2])
    # set the source of fib_pos
    p.set_sources(['FIB_POS', 'FIB_POS_ID'], func_name)

    # identify lamp
    if kind is not None:
        lamp = kind
    elif filename is not None:
        lamp = decide_on_lamp_type(p, filename=filename)
    else:
        lamp = decide_on_lamp_type(p, filename=p['ARG_FILE_NAMES'][0])

    # -------------------------------------------------------------------------
    # Now set parameters in p based on lamp type

    # the lamp type
    p['LAMP_TYPE'] = lamp
    p.set_source('LAMP_TYPE', func_name)
    # the lamp file
    p['IC_LL_LINE_FILE'] = p['IC_LL_LINE_FILE_ALL'][lamp]
    p.set_source('IC_LL_LINE_FILE', func_name)
    # the lamp cat type
    p['IC_CAT_TYPE'] = p['IC_CAT_TYPE_ALL'][lamp]
    p.set_source('IC_CAT_TYPE', func_name)
    # -------------------------------------------------------------------------
    # finally return p
    return p


def generate_res_files(p, loc, hdict):
    # get constants from p
    resmap_size = p['HC_RESMAP_SIZE']
    # get data from loc
    map_dvs = np.array(loc['RES_MAP_DVS'])
    map_lines = np.array(loc['RES_MAP_LINES'])
    map_params = np.array(loc['RES_MAP_PARAMS'])
    resolution_map = np.array(loc['RES_MAP'])

    # get dimensions
    nbo, nbpix = loc['NBO'], loc['NBPIX']

    # bin size in order direction
    bin_order = int(np.ceil(nbo / resmap_size[0]))
    bin_x = int(np.ceil(nbpix / resmap_size[1]))
    # get ranges of values
    order_range = np.arange(0, nbo, bin_order)
    x_range = np.arange(0, nbpix // bin_x)

    # loop around the order bins
    resdata, hdicts = [], []
    for order_num in order_range:
        # loop around the x position
        for xpos in x_range:
            # get the correct data
            all_dvs = map_dvs[order_num // bin_order][xpos]
            all_lines = map_lines[order_num // bin_order][xpos]
            params = map_params[order_num // bin_order][xpos]
            resolution = resolution_map[order_num // bin_order][xpos]
            # get start and end order
            start_order = order_num
            end_order = start_order + bin_order - 1
            # generate header keywordstores
            kw_startorder = ['ORDSTART', '', 'First order covered in res map']
            kw_endorder = ['ORDEND', '', 'Last order covered in res map']
            kw_region = ['REGION', '', 'Region along x-axis in res map']
            largs = [order_num, order_num + bin_order - 1, xpos]
            comment = 'Resolution: order={0}-{1} r={2}'
            kw_res = ['RESOL', '', comment.format(*largs)]
            comment = 'Gaussian params: order={0}-{1} r={2}'
            kw_params = ['GPARAMS', '', comment.format(*largs)]
            # add keys to headed
            hdict = spirouImage.AddKey(p, hdict, kw_startorder,
                                       value=start_order)
            hdict = spirouImage.AddKey(p, hdict, kw_endorder, value=end_order)
            hdict = spirouImage.AddKey(p, hdict, kw_region, value=xpos)
            hdict = spirouImage.AddKey(p, hdict, kw_res, value=resolution)
            hdict = spirouImage.AddKey1DList(p, hdict, kw_params,
                                             values=params, dim1name='coeff')
            # append this hdict to hicts
            hdicts.append(dict(hdict))
            # push data into correct columns
            resdata.append(np.array(list(zip(all_dvs, all_lines))))
    # return the data and hdicts
    return resdata, hdicts

# =============================================================================
# Worker functions
# =============================================================================
def generate_wave_map(p, loc):
    func_name = __NAME__ + '.generate_wave_map()'
    # get constants from p
    pixel_shift_inter = p['PIXEL_SHIFT_INTER']
    pixel_shift_slope = p['PIXEL_SHIFT_SLOPE']
    # get data from loc
    poly_wave_sol = loc['WAVEPARAMS']
    nbo, nbpix = loc['NBO'], loc['NBPIX']

    # print a warning if pixel_shift is not 0
    if pixel_shift_slope != 0 or pixel_shift_inter != 0:
        wmsg = 'Pixel shift is not 0, check that this is desired'
        WLOG(p, 'warning', wmsg.format())

    # generate wave map with shift
    wave_map = np.zeros([nbo, nbpix])
    shift = pixel_shift_inter + pixel_shift_slope
    xpix = np.arange(nbpix) + shift * np.arange(nbpix)
    for iord in range(nbo):
        wave_map[iord, :] = np.polyval((poly_wave_sol[iord, :])[::-1], xpix)

    # save wave map to loc
    loc['INITIAL_WAVE_MAP'] = wave_map
    loc.set_source('INITIAL_WAVE_MAP', func_name)
    # return loc
    return loc


def find_hc_gauss_peaks(p, loc):
    """

    :param p:
    :param loc:
    :return:
    """
    func_name = __NAME__ + '.find_hc_gauss_peaks()'
    # get constants from p
    wsize = p['HC_FITTING_BOX_SIZE']
    sigma_peak = p['HC_FITTING_BOX_SIGMA']
    gfitmode = p['HC_FITTING_BOX_GFIT_TYPE']
    gauss_rms_dev_min = p['HC_FITTINGBOX_RMS_DEVMIN']
    gauss_rms_dev_max = p['HC_FITTINGBOX_RMS_DEVMAX']
    ew_min = p['HC_FITTINGBOX_EW_MIN']
    ew_max = p['HC_FITTINGBOX_EW_MAX']
    # get data from loc
    hc_sp = loc['HCDATA']
    nbo, nbpix = loc['NBO'], loc['NBPIX']
    # columns from listline file
    litems = ['ZP_INI', 'SLOPE_INI', 'EW_INI', 'XGAU_INI', 'PEAK_INI',
              'ORD_INI', 'GAUSS_RMS_DEV_INI']
    # ---------------------------------------------------------------------
    # get filename
    ini_table_name = spirouConfig.Constants.HC_INIT_LINELIST(p)
    # check if we already have a cached guess for this file
    if os.path.exists(ini_table_name) and not p['HC_EA_FORCE_CREATE_LINELIST']:
        # if we do load from file
        ini_table = spirouImage.ReadTable(p, ini_table_name, fmt='ascii.rst',
                                          colnames=litems)
        # log that we're reading from file
        wmsg = 'Table of found lines already exists; reading lines from {0}'
        WLOG(p, '', wmsg.format(ini_table_name))

        # load ini_table into loc
        for col in ini_table.colnames:
            loc[col] = np.array(ini_table[col])

        # set sources
        loc.set_sources(litems, func_name)

        # return loc
        return loc
    else:
        # set up storage
        for litem in litems:
            loc[litem] = []
        loc.set_sources(litems, func_name)
        # add extra storage for plotting
        loc['XPIX_INI'] = []
        loc['G2_INI'] = []
        loc.set_sources(['XPIX_INI', 'G2_INI'], func_name)

    # ------------------------------------------------------------------------
    # Only done if ini_table_name does not exist
    # ------------------------------------------------------------------------
    # set the first "previous peak" to -1
    xprev = -1
    # loop around orders
    for order_num in range(nbo):
        # print progress for user
        wmsg = 'Processing Order {0} of {1}'
        WLOG(p, '', wmsg.format(order_num, nbo))
        # set number of peaks found
        npeaks = 0
        # extract this orders spectrum
        hc_sp_order = np.array(hc_sp[order_num, :])
        # loop around boxes in each order 1/3rd of wsize at a time
        bstart, bend = wsize * 2, hc_sp.shape[1] - wsize * 2 - 1
        bstep = wsize // 3
        for indmax in range(bstart, bend, bstep):
            # get this iterations start and end
            istart, iend = indmax - wsize, indmax + wsize
            # get the pixels for this iteration
            xpix = np.arange(istart, iend, 1)
            # get the spectrum at these points
            segment = np.array(hc_sp_order[istart:iend])
            # check there are not too many nans in segment:
            # if total not-nans is smaller than gaussian params +1
            if np.sum(~np.isnan(segment)) < gfitmode + 1:
                # continue to next segment
                continue
            # calculate the RMS
            rms = np.nanmedian(np.abs(segment[1:] - segment[:-1]))
            # find the peak pixel value
            peak = np.nanmax(segment) - np.nanmedian(segment)
            # -----------------------------------------------------------------
            # keep only peaks that are well behaved:
            # RMS not zero
            keep = rms != 0
            # peak not zero
            keep &= peak != 0
            # peak at least a few sigma from RMS
            with warnings.catch_warnings(record=True) as _:
                keep &= (peak / rms > sigma_peak)
            # -----------------------------------------------------------------
            # position of peak within segement - it needs to be close enough
            #   to the center of the segment if it is at the edge we'll catch
            #   it in the following iteration
            imax = np.argmax(segment) - wsize
            # keep only if close enough to the center
            keep &= np.abs(imax) < wsize // 3
            # -----------------------------------------------------------------
            # if keep is still True we have a good peak worth fitting
            #    a Gaussian
            if keep:
                # fit a gaussian with a slope
                gargs = [xpix, segment, gfitmode]
                popt_left, g2 = spirouMath.gauss_fit_nn(*gargs)
                # residual of the fit normalized by peak value similar to
                #    an 1/SNR value
                gauss_rms_dev0 = np.std(segment - g2) / popt_left[0]
                # all values that will be added (if keep_peak=True) to the
                #    vector of all line parameters
                zp0 = popt_left[3]
                slope0 = popt_left[4]
                ew0 = popt_left[2]
                xgau0 = popt_left[1]
                peak0 = popt_left[0]
                # test whether we will add peak to our master list of peak
                keep_peak = gauss_rms_dev0 > gauss_rms_dev_min
                keep_peak &= gauss_rms_dev0 < gauss_rms_dev_max
                keep_peak &= ew0 > ew_min
                keep_peak &= ew0 < ew_max
                # must be > 1 pix from previous peak
                keep_peak &= np.abs(xgau0 - xprev) > 1
                # if all if fine, we keep the value of the fit
                if keep_peak:
                    # update number of peaks
                    npeaks += 1
                    # update the value of previous peak
                    xprev = xgau0
                    # append values
                    loc['ZP_INI'].append(zp0)
                    loc['SLOPE_INI'].append(slope0)
                    loc['EW_INI'].append(ew0)
                    loc['XGAU_INI'].append(xgau0)
                    loc['PEAK_INI'].append(peak0)
                    loc['ORD_INI'].append(order_num)
                    loc['GAUSS_RMS_DEV_INI'].append(gauss_rms_dev0)
                    # add values for plotting
                    loc['XPIX_INI'].append(xpix)
                    loc['G2_INI'].append(g2)
        # display the number of peaks found
        wmsg = '\tNumber of peaks found = {0}'
        WLOG(p, '', wmsg.format(npeaks))

        # debug plot
        if p['DRS_PLOT'] and p['DRS_DEBUG'] == 2:
            if p['HC_EA_PLOT_PER_ORDER']:
                sPlt.wave_ea_plot_per_order_hcguess(p, loc, order_num)
    # ------------------------------------------------------------------
    # write to table
    columnnames, columnvalues, columnfmts = litems, [], []
    for colname in columnnames:
        columnvalues.append(loc[colname])
        columnfmts.append(None)
    ini_table = spirouImage.MakeTable(p, columnnames, columnvalues,
                                      columnfmts)
    # save the table to file
    wmsg = 'Writing HC line-list to file {0}'
    WLOG(p, '', wmsg.format(os.path.basename(ini_table_name)))
    spirouImage.WriteTable(p, ini_table, ini_table_name, fmt='ascii.rst')

    # plot all orders w/fitted gaussians
    if p['DRS_PLOT'] > 0:
        sPlt.wave_ea_plot_allorder_hcguess(p, loc)

    # return loc
    return loc


# TODO: This function needs organising into more than one function
# TODO:    - it is insane to follow!!
def fit_gaussian_triplets(p, loc):
    """
    Fits the Gaussian peaks with sigma clipping

    fits a second-order xpix vs wavelength polynomial and test it against
    all other fitted lines along the order we keep track of the best fit for
    the order, i.e., the fit that provides a solution with the largest number
    of lines within +-500 m/s

    We then assume that the fit is fine, we keep the lines that match the
    "best fit" and we move to the next order.

    Once we have "valid" lines for most/all orders, we attempt to fit a
    5th order polynomial of the xpix vs lambda for all orders.
    The coefficient of the fit must be continuous from one order to the next

    we perform the fit twice, once to get a coarse solution, once to refine
    as we will trim some variables, we define them on each loop
    not 100% elegant, but who cares, it takes 5µs ...

    :param p:
    :param loc:
    :return:
    """
    func_name = __NAME__ + '.fit_gaussian_triplets()'
    # get constants from p
    nmax_bright = p['HC_NMAX_BRIGHT']
    n_iterations = p['HC_NITER_FIT_TRIPLET']
    cat_guess_dist = p['HC_MAX_DV_CAT_GUESS']
    triplet_deg = p['HC_TFIT_DEG']
    cut_fit_threshold = p['HC_TFIT_CUT_THRES']
    minimum_number_of_lines = p['HC_TFIT_MIN_NUM_LINES']
    minimum_total_number_of_lines = p['HC_TFIT_MIN_TOT_LINES']
    order_fit_continuity = p['HC_TFIT_ORDER_FIT_CONTINUITY']
    sigma_clip_num = p['HC_TFIT_SIGCLIP_NUM']
    sigma_clip_threshold = p['HC_TFIT_SIGCLIP_THRES']
    # get data from loc
    wave_ll, amp_ll = loc['LL_LINE'], loc['AMPL_LINE']
    poly_wave_sol = loc['WAVEPARAMS']

    # get dimensions
    nbo, nbpix = loc['NBO'], loc['NBPIX']

    # ------------------------------------------------------------------
    # triplet loop
    # TODO: Move loop out of function
    # set up storage
    wave_catalog = []
    amp_catalog = []
    wave_map2 = np.zeros((nbo, nbpix))
    sig = np.nan
    # get coefficients
    xgau = np.array(loc['XGAU_INI'])
    orders = np.array(loc['ORD_INI'])
    gauss_rms_dev = np.array(loc['GAUSS_RMS_DEV_INI'])
    ew = np.array(loc['EW_INI'])
    peak2 = np.array(loc['PEAK_INI'])
    dv = np.array([])

    for sol_iteration in range(n_iterations):
        # log progress
        # TODO Move log progress out of function
        wmsg = 'Fit Triplet {0} of {1}'
        WLOG(p, 'info', wmsg.format(sol_iteration + 1, n_iterations))
        # get coefficients
        xgau = np.array(loc['XGAU_INI'])
        orders = np.array(loc['ORD_INI'])
        gauss_rms_dev = np.array(loc['GAUSS_RMS_DEV_INI'])
        ew = np.array(loc['EW_INI'])
        peak = np.array(loc['PEAK_INI'])
        # get peak again for saving (to make sure nothing goes wrong
        #     in selection)
        peak2 = np.array(loc['PEAK_INI'])
        # --------------------------------------------------------------
        # find the brightest lines for each order, only those lines will
        #     be used to derive the first estimates of the per-order fit
        # ------------------------------------------------------------------
        brightest_lines = np.zeros(len(xgau), dtype=bool)
        # loop around order
        for order_num in set(orders):
            # find all order_nums that belong to this order
            good = orders == order_num
            # get the peaks for this order
            order_peaks = peak[good]
            # we may have fewer lines within the order than nmax_bright
            if np.nansum(good) <= nmax_bright:
                nmax = np.nansum(good) - 1
            else:
                nmax = nmax_bright
            # Find the "nmax" brightest peaks
            smallest_peak = np.sort(order_peaks)[::-1][nmax]
            good &= (peak > smallest_peak)
            # apply good mask to brightest_lines storage
            brightest_lines[good] = True
        # ------------------------------------------------------------------
        # Calculate wave solution at each x gaussian center
        # ------------------------------------------------------------------
        ini_wave_sol = np.zeros_like(xgau)
        # get wave solution for these xgau values
        for order_num in set(orders):
            # find all order_nums that belong to this order
            good = orders == order_num
            # get the xgau for this order
            xgau_order = xgau[good]
            # get wave solution for this order
            pargs = poly_wave_sol[order_num][::-1], xgau_order
            wave_sol_order = np.polyval(*pargs)
            # pipe wave solution for order into full wave_sol
            ini_wave_sol[good] = wave_sol_order
        # ------------------------------------------------------------------
        # match gaussian peaks
        # ------------------------------------------------------------------
        # keep track of the velocity offset between predicted and observed
        #    line centers
        dv = np.repeat(np.nan, len(ini_wave_sol))
        # wavelength given in the catalog for the matched line
        wave_catalog = np.repeat(np.nan, len(ini_wave_sol))
        # amplitude given in the catolog for the matched lines
        amp_catalog = np.zeros(len(ini_wave_sol))
        # loop around all lines in ini_wave_sol
        for w_it, wave0 in enumerate(ini_wave_sol):
            # find closest catalog line to the line considered
            id_match = np.argmin(np.abs(wave_ll - wave0))
            # find distance between catalog and ini solution  in m/s
            distv = ((wave_ll[id_match] / wave0) - 1) * speed_of_light_ms
            # check that distance is below threshold
            if np.abs(distv) < cat_guess_dist:
                wave_catalog[w_it] = wave_ll[id_match]
                amp_catalog[w_it] = amp_ll[id_match]
                dv[w_it] = distv

        # ------------------------------------------------------------------
        # loop through orders and reject bright lines not within
        #     +- HC_TFIT_DVCUT km/s histogram peak
        # ------------------------------------------------------------------

        # width in dv [km/s] - though used for number of bins?
        # TODO: Question: Why km/s --> number
        nbins = 2 * p['HC_MAX_DV_CAT_GUESS'] // 1000
        # loop around all order
        for order_num in set(orders):
            # get the good pixels in this order
            good = (orders == order_num) & (np.isfinite(dv))
            # get histogram of points for this order
            histval, histcenters = np.histogram(dv[good], bins=nbins)
            # get the center of the distribution
            dv_cen = histcenters[np.argmax(histval)]
            # define a mask to remove points away from center of histogram
            with warnings.catch_warnings(record=True) as _:
                mask = (np.abs(dv-dv_cen) > p['HC_TFIT_DVCUT_ORDER']) & good
            # apply mask to dv and to brightest lines
            dv[mask] = np.nan
            brightest_lines[mask] = False

        # re-get the histogram of points for whole image
        histval, histcenters = np.histogram(dv[np.isfinite(dv)], bins=nbins)
        # re-find the center of the distribution
        dv_cen = histcenters[np.argmax(histval)]
        # re-define the mask to remove poitns away from center of histogram
        with warnings.catch_warnings(record=True) as _:
            mask = (np.abs(dv-dv_cen) > p['HC_TFIT_DVCUT_ALL'])
        # re-apply mask to dv and to brightest lines
        dv[mask] = np.nan
        brightest_lines[mask] = False

        # ------------------------------------------------------------------
        # Find best trio of lines
        # ------------------------------------------------------------------
        for order_num in set(orders):
            # find this order's lines
            good = orders == order_num
            # find all usable lines in this order
            good_all = good & (np.isfinite(wave_catalog))
            # good_all = good & (np.isfinite(dv))
            # find all bright usable lines in this order
            good_bright = good_all & brightest_lines
            # get the positions of lines
            pos_bright = np.where(good_bright)[0]
            pos = np.where(good)[0]
            # get number of good_bright
            num_gb = int(np.nansum(good_bright))
            bestn = 0
            best_coeffs = np.zeros(triplet_deg + 1)
            # get the indices of the triplets of bright lines
            indices = itertools.combinations(range(num_gb), 3)
            # loop around triplets
            for index in indices:
                # get this iterations positions
                pos_it = pos_bright[np.array(index)]
                # get the x values for this iterations position
                xx = xgau[pos_it]
                # get the y values for this iterations position
                yy = wave_catalog[pos_it]
                # fit this position's lines and take it as the best-guess
                #    solution
                coeffs = nanpolyfit(xx, yy, triplet_deg)
                # extrapolate out over all lines
                fit_all = np.polyval(coeffs, xgau[good_all])
                # work out the error in velocity
                ev = ((wave_catalog[good_all] / fit_all) - 1) * speed_of_light
                # work out the number of lines to keep
                nkeep = np.nansum(np.abs(ev) < cut_fit_threshold)
                # if number of lines to keep largest seen --> store
                if nkeep > bestn:
                    bestn = nkeep
                    best_coeffs = np.array(coeffs)
            # Log the total number of valid lines found
            wmsg = '\tOrder {0}: Number of valid lines = {1} / {2}'
            wargs = [order_num, bestn, np.nansum(good_all)]
            WLOG(p, '', wmsg.format(*wargs))
            # if we have the minimum number of lines check that we satisfy
            #   the cut_fit_threshold for all good lines and reject outliers
            if bestn >= minimum_number_of_lines:
                # extrapolate out best fit coefficients over all lines in
                #    this order
                fit_best = np.polyval(best_coeffs, xgau[good])
                # work out the error in velocity
                ev = ((wave_catalog[good] / fit_best) - 1) * speed_of_light
                abs_ev = np.abs(ev)
                # if max error in velocity greater than threshold, remove
                #    those greater than cut_fit_threshold
                if np.nanmax(abs_ev) > cut_fit_threshold:
                    # get outliers
                    with warnings.catch_warnings(record=True) as _:
                        outliers = pos[abs_ev > cut_fit_threshold]
                    # set outliers to NaN in wave catalog
                    wave_catalog[outliers] = np.nan
                    # set dv of outliers to NaN
                    dv[outliers] = np.nan
            # else set everything to NaN
            else:
                wave_catalog[good] = np.nan
                dv[good] = np.nan

        # ------------------------------------------------------------------
        # Plot wave catalogue all lines and brightest lines
        # ------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            pargs = [wave_catalog, dv, brightest_lines, sol_iteration]
            sPlt.wave_ea_plot_wave_cat_all_and_brightest(p, *pargs)

        # ------------------------------------------------------------------
        # Keep only wave_catalog where values are finite
        # -----------------------------------------------------------------
        # create mask
        good = np.isfinite(wave_catalog)
        # apply mask
        wave_catalog = wave_catalog[good]
        amp_catalog = amp_catalog[good]
        xgau = xgau[good]
        orders = orders[good]
        dv = dv[good]
        ew = ew[good]
        gauss_rms_dev = gauss_rms_dev[good]
        peak2 = peak2[good]

        # ------------------------------------------------------------------
        # Quality check on the total number of lines found
        # ------------------------------------------------------------------
        if np.nansum(good) < minimum_total_number_of_lines:
            emsg1 = 'Insufficient number of lines found.'
            emsg2 = '\t Found = {0}  Required = {1}'
            eargs = [np.nansum(good), minimum_total_number_of_lines]
            WLOG(p, 'error', [emsg1, emsg2.format(*eargs)])

        # ------------------------------------------------------------------
        # Linear model slice generation
        # ------------------------------------------------------------------
        # storage for the linear model slice
        lin_mod_slice = np.zeros((len(xgau), np.nansum(order_fit_continuity)))

        # construct the unit vectors for wavelength model
        # loop around order fit continuity values
        ii = 0
        for expo_xpix in range(len(order_fit_continuity)):
            # loop around orders
            for expo_order in range(order_fit_continuity[expo_xpix]):
                part1 = orders ** expo_order
                part2 = np.array(xgau) ** expo_xpix
                lin_mod_slice[:, ii] = part1 * part2
                # iterate
                ii += 1

        # ------------------------------------------------------------------
        # Sigma clipping
        # ------------------------------------------------------------------
        # storage for arrays
        recon0 = np.zeros_like(wave_catalog)
        amps0 = np.zeros(np.nansum(order_fit_continuity))

        # Loop sigma_clip_num times for sigma clipping and numerical
        #    convergence. In most cases ~10 iterations would be fine but this
        #    is fast
        for sigma_it in range(sigma_clip_num):
            # calculate the linear minimization
            largs = [wave_catalog - recon0, lin_mod_slice]
            with warnings.catch_warnings(record=True) as _:
                amps, recon = spirouMath.linear_minimization(*largs)
            # add the amps and recon to new storage
            amps0 = amps0 + amps
            recon0 = recon0 + recon
            # loop around the amplitudes and normalise
            for a_it in range(len(amps0)):
                # work out the residuals
                res = (wave_catalog - recon0)
                # work out the sum of residuals
                sum_r = np.nansum(res * lin_mod_slice[:, a_it])
                sum_l2 = np.nansum(lin_mod_slice[:, a_it] ** 2)
                # normalise by sum squared
                ampsx = sum_r / sum_l2
                # add this contribution on
                amps0[a_it] += ampsx
                recon0 += (ampsx * lin_mod_slice[:, a_it])
            # recalculate dv [in km/s]
            dv = ((wave_catalog / recon0) - 1) * speed_of_light
            # calculate the standard deviation
            sig = np.std(dv)
            absdev = np.abs(dv / sig)

            # initialize lists for saving
            recon0_aux = []
            lin_mod_slice_aux = []
            wave_catalog_aux = []
            amp_catalog_aux = []
            xgau_aux = []
            orders_aux = []
            dv_aux = []
            ew_aux = []
            gauss_rms_dev_aux = []
            peak2_aux = []

            # Sigma clip worst line per order
            for order_num in set(orders):
                # mask for order
                omask = orders == order_num
                # get abs dev for order
                absdev_ord = absdev[omask]
                # check if above threshold
                if np.max(absdev_ord) > sigma_clip_threshold:
                    # create mask for worst line
                    sig_mask = absdev_ord < np.max(absdev_ord)
                    # apply mask
                    recon0_aux.append(recon0[omask][sig_mask])
                    lin_mod_slice_aux.append(lin_mod_slice[omask][sig_mask])
                    wave_catalog_aux.append(wave_catalog[omask][sig_mask])
                    amp_catalog_aux.append(amp_catalog[omask][sig_mask])
                    xgau_aux.append(xgau[omask][sig_mask])
                    orders_aux.append(orders[omask][sig_mask])
                    dv_aux.append(dv[omask][sig_mask])
                    ew_aux.append(ew[omask][sig_mask])
                    gauss_rms_dev_aux.append(gauss_rms_dev[omask][sig_mask])
                    peak2_aux.append(peak2[omask][sig_mask])
                # if all below threshold keep all
                else:
                    recon0_aux.append(recon0[omask])
                    lin_mod_slice_aux.append(lin_mod_slice[omask])
                    wave_catalog_aux.append(wave_catalog[omask])
                    amp_catalog_aux.append(amp_catalog[omask])
                    xgau_aux.append(xgau[omask])
                    orders_aux.append(orders[omask])
                    dv_aux.append(dv[omask])
                    ew_aux.append(ew[omask])
                    gauss_rms_dev_aux.append(gauss_rms_dev[omask])
                    peak2_aux.append(peak2[omask])
            # save aux lists to initial arrays
            orders = np.concatenate(orders_aux)
            recon0 = np.concatenate(recon0_aux)
            lin_mod_slice = np.concatenate(lin_mod_slice_aux)
            wave_catalog = np.concatenate(wave_catalog_aux)
            amp_catalog = np.concatenate(amp_catalog_aux)
            xgau = np.concatenate(xgau_aux)
            dv = np.concatenate(dv_aux)
            ew = np.concatenate(ew_aux)
            gauss_rms_dev = np.concatenate(gauss_rms_dev_aux)
            peak2 = np.concatenate(peak2_aux)

            # if np.max(absdev) > sigma_clip_threshold:
            #     # log sigma clipping
            #     wmsg = '\tSigma-clipping at (>{0}) --> max(sig)={1:.5f} sigma'
            #     wargs = [sigma_clip_threshold, np.max(absdev)]
            #     WLOG(p, '', wmsg.format(*wargs))
            #     # mask for sigma clip
            #     sig_mask = absdev < sigma_clip_threshold
            #     # apply mask
            #     recon0 = recon0[sig_mask]
            #     lin_mod_slice = lin_mod_slice[sig_mask]
            #     wave_catalog = wave_catalog[sig_mask]
            #     amp_catalog = amp_catalog[sig_mask]
            #     xgau = xgau[sig_mask]
            #     orders = orders[sig_mask]
            #     dv = dv[sig_mask]
            #     ew = ew[sig_mask]
            #     gauss_rms_dev = gauss_rms_dev[sig_mask]
            #     peak2 = peak2[sig_mask]

            # Log stats
            sig1 = sig * 1000 / np.sqrt(len(wave_catalog))
            wmsg = '\t{0} | RMS={1:.5f} km/s sig={2:.5f} m/s n={3}'
            wargs = [sigma_it, sig, sig1, len(wave_catalog)]
            WLOG(p, '', wmsg.format(*wargs))

        # ------------------------------------------------------------------
        # Plot wave catalogue all lines and brightest lines
        # ------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            pargs = [orders, wave_catalog, recon0, gauss_rms_dev, xgau, ew,
                     sol_iteration]
            sPlt.wave_ea_plot_tfit_grid(p, *pargs)

        # ------------------------------------------------------------------
        # Construct wave map
        # ------------------------------------------------------------------
        xpix = np.arange(nbpix)
        wave_map2 = np.zeros((nbo, nbpix))
        poly_wave_sol = np.zeros_like(loc['WAVEPARAMS'])

        # loop around the orders
        for order_num in range(nbo):
            order_mask = orders == order_num
            if np.nansum(order_mask) == 0:
                wmsg = 'No values found for order {0}'
                WLOG(p, 'warning', wmsg.format(order_num))
            ii = 0
            for expo_xpix in range(len(order_fit_continuity)):
                for expo_order in range(order_fit_continuity[expo_xpix]):
                    # calculate new coefficient
                    new_coeff = (order_num ** expo_order) * amps0[ii]
                    # add to poly wave solution
                    poly_wave_sol[order_num, expo_xpix] += new_coeff
                    # iterate
                    ii += 1
            # add to wave_map2
            wcoeffs = poly_wave_sol[order_num, :][::-1]
            wave_map2[order_num, :] = np.polyval(wcoeffs, xpix)

        # TODO ----------------------------------------------------------------
        # TODO: Remove below
        # TODO: or reformat to allow different ployfits w/switch?
        # TODO ----------------------------------------------------------------
    #     wave_map3 = np.zeros((nbo, nbpix))
    #     poly_wave_sol3 = np.zeros_like(loc['WAVEPARAMS'])
    #     wave_mapc = np.zeros((nbo, nbpix))
    #     poly_wave_solc = np.zeros_like(loc['WAVEPARAMS'])
    #     for order_num in range(nbo):
    #         order_mask = orders == order_num
    #         # check if there are found lines, if not continue
    #         if np.nansum(order_mask) == 0:
    #             continue
    #
    #         ppx = xgau[order_mask]
    #         ppy = wave_catalog[order_mask]
    #         wcoeffs = nanpolyfit(ppx, ppy, loc['WAVEPARAMS'].shape[1]-1)[::-1]
    #         poly_wave_sol3[order_num, :] = wcoeffs
    #         wave_map3[order_num, :] = np.polyval(wcoeffs[::-1], xpix)
    #
    #         ppx2 = xgau[order_mask]
    #         ppy2 = wave_catalog[order_mask]
    #         cheb_coeffs = chebyshev.chebfit(ppx2, ppy2, 4)
    #         poly_wave_solc[order_num, :] = cheb_coeffs
    #
    #         ppx3 = np.arange(loc['NBPIX'])
    #         wave_mapc[order_num, :] = chebyshev.chebval(ppx3, cheb_coeffs)
    #     # save parameters to loc
    #     loc['WAVE_CATALOG'] = wave_catalog
    #     loc['AMP_CATALOG'] = amp_catalog
    #     loc['SIG'] = sig
    #     loc['SIG1'] = sig * 1000 / np.sqrt(len(wave_catalog))
    #     loc['POLY_WAVE_SOL'] = poly_wave_sol
    #     loc['WAVE_MAP2'] = wave_map2
    #     loc['XGAU_T'] = xgau
    #     loc['ORD_T'] = orders
    #     loc['GAUSS_RMS_DEV_T'] = gauss_rms_dev
    #     loc['DV_T'] = dv
    #     loc['EW_T'] = ew
    #     loc['PEAK_T'] = peak2
    #
    #     loc2 = spirouConfig.ParamDict()
    #     for key in loc:
    #         loc2[key] = loc[key]
    #     loc2['POLY_WAVE_SOL'] = poly_wave_sol3
    #     loc2['WAVE_MAP2'] = wave_map3
    #
    #     do_stuff(p, loc)
    #     do_stuff(p, loc2)
    #
    # loc['POLY_WAVE_SOL3'] = poly_wave_sol3
    # loc['WAVE_MAP3'] = wave_map3
    #
    # loc['POLY_WAVE_SOL4'] = poly_wave_solc
    # loc['WAVE_MAP4'] = wave_mapc
    #
    # #loc['POLY_WAVE_SOL4'][-1] = poly_wave_sol[-1]
    # #loc['WAVE_MAP4'][-1] = wave_map3[-1]
    #
    # ppx4 = np.arange(loc['NBPIX'])
    # loc['POLY_WAVE_SOL4'][-2] = chebyshev.chebfit(ppx4, loc['WAVE_MAP2'][-2], 4)
    # loc['WAVE_MAP4'][-2] = chebyshev.chebval(ppx4, loc['POLY_WAVE_SOL4'][-2])
    #
    # loc['POLY_WAVE_SOL4'][-1] = chebyshev.chebfit(ppx4, loc['WAVE_MAP2'][-1], 4)
    # loc['WAVE_MAP4'][-1] = chebyshev.chebval(ppx4, loc['POLY_WAVE_SOL4'][-1])
    #
    # loc['POLY_WAVE_SOL5'] = poly_wave_sol
    # loc['WAVE_MAP5'] = wave_map2
    #
    # loc['POLY_WAVE_SOL5'][0] = poly_wave_sol3[0]
    # loc['WAVE_MAP5'][0] = wave_map3[0]

    # TODO ----------------------------------------------------------------
    # TODO: Remove above
    # TODO: or reformat to allow different polyfits w/switch?
    # TODO ----------------------------------------------------------------

    # save parameters to loc
    loc['WAVE_CATALOG'] = wave_catalog
    loc['AMP_CATALOG'] = amp_catalog
    loc['SIG'] = sig
    loc['SIG1'] = sig * 1000 / np.sqrt(len(wave_catalog))
    loc['POLY_WAVE_SOL'] = poly_wave_sol
    loc['WAVE_MAP2'] = wave_map2

    loc['XGAU_T'] = xgau
    loc['ORD_T'] = orders
    loc['GAUSS_RMS_DEV_T'] = gauss_rms_dev
    loc['DV_T'] = dv
    loc['EW_T'] = ew
    loc['PEAK_T'] = peak2

    loc['LIN_MOD_SLICE'] = lin_mod_slice
    loc['RECON0'] = recon0

    # loc['POLY_WAVE_SOLC'] = poly_wave_solc
    # loc['WAVE_MAPC'] = wave_mapc

    # return loc
    return loc


def generate_resolution_map(p, loc):
    func_name = __NAME__ + '.generate_resolution_map()'
    # get constants from p
    resmap_size = p['HC_RESMAP_SIZE']
    wsize = p['HC_FITTING_BOX_SIZE']
    max_dev_threshold = p['HC_RES_MAXDEV_THRES']
    # get data from loc
    hc_sp = np.array(loc['HCDATA'])
    xgau = np.array(loc['XGAU_T'])
    orders = np.array(loc['ORD_T'])
    gauss_rms_dev = np.array(loc['GAUSS_RMS_DEV_T'])
    wave_catalog = np.array(loc['WAVE_CATALOG'])
    wave_map2 = np.array(loc['WAVE_MAP2'])
    # get dimensions
    nbo, nbpix = loc['NBO'], loc['NBPIX']
    # storage of resolution map
    resolution_map = np.zeros(resmap_size)
    map_dvs = []
    map_lines = []
    map_params = []

    # bin size in order direction
    bin_order = int(np.ceil(nbo / resmap_size[0]))
    bin_x = int(np.ceil(nbpix / resmap_size[1]))

    # determine the line spread function

    # loop around the order bins
    for order_num in range(0, nbo, bin_order):
        # storage of map parameters
        order_dvs = []
        order_lines = []
        order_params = []
        # loop around the x position
        for xpos in range(0, nbpix // bin_x):
            # we verify that the line is well modelled by a gaussian
            # fit. If the RMS to the fit is small enough, we include
            # the line in the profile measurement
            mask = gauss_rms_dev < 0.05
            # the line must fall in the right part of the array
            # in both X and cross-dispersed directions. The
            # resolution is expected to change slightly
            mask &= (orders // bin_order) == (order_num // bin_order)
            mask &= (xgau // bin_x) == xpos
            mask &= np.isfinite(wave_catalog)

            # get the x centers for this bin
            b_xgau = xgau[mask]
            b_orders = orders[mask]
            b_wave_catalog = wave_catalog[mask]

            # set up storage for lines and dvs
            all_lines = np.zeros((np.nansum(mask), 2 * wsize + 1))
            all_dvs = np.zeros((np.nansum(mask), 2 * wsize + 1))

            # set up base
            base = np.zeros(2 * wsize + 1, dtype=bool)
            base[0:3] = True
            base[2 * wsize - 2: 2 * wsize + 1] = True

            # loop around all good lines
            # we express everything in velocity space rather than
            # pixels. This allows us to merge all lines in a single
            # profile and removes differences in pixel sampling and
            # resolution.
            for it in range(int(np.nansum(mask))):
                # get limits
                border = int(b_orders[it])
                start = int(b_xgau[it] + 0.5) - wsize
                end = int(b_xgau[it] + 0.5) + wsize + 1
                # get line
                line = np.array(hc_sp)[border, start:end]
                # subtract median base and normalise line
                line -= np.nanmedian(line[base])
                line /= np.nansum(line)
                # calculate velocity... express things in velocity
                ratio = wave_map2[border, start:end] / b_wave_catalog[it]
                dv = -speed_of_light * (ratio - 1)
                # store line and dv
                all_lines[it, :] = line
                all_dvs[it, :] = dv

            # flatten all lines and dvs
            all_dvs = all_dvs.ravel()
            all_lines = all_lines.ravel()
            # define storage for keep mask
            # keep = np.ones(len(all_dvs), dtype=bool)
            # TODO New hack: Do not keep as hardcoded
            keep = np.abs(all_lines) < 5

            # set an initial maximum deviation
            maxdev = np.inf
            # set up the fix parameters and initial guess parameters
            popt = np.zeros(5)
            init_guess = [0.3, 0.0, 1.0, 0.0, 0.0]
            # loop around until criteria met
            n_it = 0

            # import matplotlib.pyplot as plt
            # plt.ioff()
            # plt.figure()
            # plt.scatter(all_dvs[keep], all_lines[keep], label=str(n_it))
            # plt.legend(loc=0)
            # plt.show()
            # plt.close()

            # fit the merged line profile and do some sigma-clipping
            while maxdev > max_dev_threshold:
                # fit with a guassian with a slope
                fargs = dict(x=all_dvs[keep], y=all_lines[keep],
                             guess=init_guess)

                try:
                    popt, pcov = spirouMath.fit_gaussian_with_slope(**fargs)
                except Exception as e:
                    emsg = 'Resolution map curve fit error {0}: {1}'
                    WLOG(p, 'error', emsg.format(type(e), e))
                # calculate residuals for full line list
                res = all_lines - spirouMath.gauss_fit_s(all_dvs, *popt)
                # calculate RMS of residuals
                rms = res / np.nanmedian(np.abs(res))
                # calculate max deviation
                maxdev = np.nanmax(np.abs(rms[keep]))
                # re-calculate the keep mask
                keep[np.abs(rms) > max_dev_threshold] = False

                n_it += 1

            # calculate resolution
            resolution = popt[2] * spirouMath.fwhm()
            # store order criteria
            order_dvs.append(all_dvs[keep])
            order_lines.append(all_lines[keep])
            order_params.append(popt)
            # push resolution into resolution map
            resolution1 = speed_of_light / resolution
            resolution_map[order_num // bin_order, xpos] = resolution1
            # log resolution output
            wmsg = ('\tOrders {0} - {1}: nlines={2} xpos={3} '
                    'resolution={4:.5f} km/s R={5:.5f}')
            wargs = [order_num, order_num + bin_order, np.nansum(mask), xpos,
                     resolution,
                     resolution1]
            WLOG(p, '', wmsg.format(*wargs))
        # store criteria. All lines are kept for reference
        map_dvs.append(order_dvs)
        map_lines.append(order_lines)
        map_params.append(order_params)

    # push to loc
    loc['RES_MAP_DVS'] = map_dvs
    loc['RES_MAP_LINES'] = map_lines
    loc['RES_MAP_PARAMS'] = map_params
    loc['RES_MAP'] = resolution_map
    # set source
    sources = ['RES_MAP_DVS', 'RES_MAP_LINES', 'RES_MAP_PARAMS', 'RES_MAP']
    loc.set_sources(sources, func_name)

    # print stats
    wmsg1 = 'Mean resolution: {0:.3f}'.format(np.nanmean(resolution_map))
    wmsg2 = 'Median resolution: {0:.3f}'.format(np.nanmedian(resolution_map))
    wmsg3 = 'StdDev resolution: {0:.3f}'.format(np.nanstd(resolution_map))

    WLOG(p, '', [wmsg1, wmsg2, wmsg3])

    # return loc
    return loc


def calculate_littrow_sol(p, loc, ll, iteration=0, log=False):
    """
    Calculate the Littrow solution for this iteration for a set of cut points

    Uses ALL_LINES_i  where i = iteration to calculate the littrow solutions
    for defined cut points (given a cut_step and fit_deg of
    IC_LITTROW_CUT_STEP_i and IC_LITTROW_FIT_DEG_i where i = iteration)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, log option, normally the program name
            FIBER: string, the fiber type (i.e. AB or A or B or C)
            IC_LITTROW_REMOVE_ORDERS: list of ints, if not empty removes these
                                      orders from influencing the fit
            IC_LITTROW_ORDER_INIT: int, defines the first order to for the fit
                                   solution
            IC_HC_N_ORD_START: int, defines first order HC solution was
                               calculated from
            IC_HC_N_ORD_FINAL: int, defines last order HC solution was
                               calculated to
            IC_LITTROW_CUT_STEP_i: int, defines the step to use between
                                   cut points
            IC_LITTROW_FIT_DEG_i: int, defines the polynomial fit degree

            where i = iteration

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            ECHELLE_ORDERS: numpy array (1D), the echelle order numbers
            HCDATA: numpy array (2D), the image data (used for shape)
            ALL_LINES_i: list of numpy arrays, length = number of orders
                         each numpy array contains gaussian parameters
                         for each found line in that order

            where i = iteration

    :param ll: numpy array (1D), the initial guess wavelengths for each line
    :param iteration: int, the iteration number (used so we can store multiple
                      calculations in loc, defines "i" in input and outputs
                      from p and loc
    :param log: bool, if True will print a final log message on completion with
                some stats

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                X_CUT_POINTS_i: numpy array (1D), the x pixel cut points
                LITTROW_MEAN_i: list, the mean position of each cut point
                LITTROW_SIG_i: list, the mean FWHM of each cut point
                LITTROW_MINDEV_i: list, the minimum deviation of each cut point
                LITTROW_MAXDEV_i: list, the maximum deviation of each cut point
                LITTROW_PARAM_i: list of numpy arrays, the gaussian fit
                                 coefficients of each cut point
                LITTROW_XX_i: list, the order positions of each cut point
                LITTROW_YY_i: list, the residual fit of each cut point

                where i = iteration

    ALL_LINES_i definition:
        ALL_LINES_i[row] = [gparams1, gparams2, ..., gparamsN]

                    where:
                        gparams[0] = output wavelengths
                        gparams[1] = output sigma (gauss fit width)
                        gparams[2] = output amplitude (gauss fit)
                        gparams[3] = difference in input/output wavelength
                        gparams[4] = input amplitudes
                        gparams[5] = output pixel positions
                        gparams[6] = output pixel sigma width
                                          (gauss fit width in pixels)
                        gparams[7] = output weights for the pixel position
    """
    func_name = __NAME__ + '.calculate_littrow_sol()'
    # get parameters from p
    remove_orders = p['IC_LITTROW_REMOVE_ORDERS']
    # TODO: Fudge factor - Melissa will fix this :)
    n_order_init = p['IC_LITTROW_ORDER_INIT_{0}'.format(1)]
    n_order_final = p['IC_HC_N_ORD_FINAL']
    n_order_start = p['IC_HC_N_ORD_START']
    x_cut_step = p['IC_LITTROW_CUT_STEP_{0}'.format(iteration)]
    fit_degree = p['IC_LITTROW_FIT_DEG_{0}'.format(iteration)]
    # get parameters from loc
    torder = loc['ECHELLE_ORDERS']
    ll_out = ll
    # test if n_order_init is in remove_orders
    if n_order_init in remove_orders:
        # TODO: Fudge factor - Melissa will fix this
        wargs = ['IC_LITTROW_ORDER_INIT_{0}'.format(1),
                 p['IC_LITTROW_ORDER_INIT_{0}'.format(1)],
                 "IC_LITTROW_REMOVE_ORDERS"]
        wmsg1 = 'Warning {0}={1} in {2}'.format(*wargs)
        wmsg2 = '    Please check constants file'
        wmsg3 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [wmsg1, wmsg2, wmsg3])
    # test if n_order_init is in remove_orders
    if n_order_final in remove_orders:
        wargs = ["IC_HC_N_ORD_FINAL", p['IC_HC_N_ORD_FINAL'],
                 "IC_LITTROW_REMOVE_ORDERS"]
        wmsg1 = 'Warning {0}={1} in {2}'.format(*wargs)
        wmsg2 = '    Please check constants file'
        wmsg3 = '    function = {0}'.format(func_name)
        WLOG(p, 'error', [wmsg1, wmsg2, wmsg3])
    # check that all remove orders exist
    for remove_order in remove_orders:
        if remove_order not in np.arange(n_order_final):
            wargs1 = [remove_order, 'IC_LITTROW_REMOVE_ORDERS', n_order_init,
                      n_order_final]
            wmsg1 = (' Invalid order number={0} in {1} must be between'
                     '{2} and {3}'.format(*wargs1))
            wmsg2 = '    function = {0}'.format(func_name)
            WLOG(p, 'error', [wmsg1, wmsg2])

    # check to make sure we have some orders left
    if len(np.unique(remove_orders)) == n_order_final - n_order_start:
        wmsg = 'Cannot remove all orders. Check IC_LITTROW_REMOVE_ORDERS'
        WLOG(p, 'error', wmsg)
    # get the total number of orders to fit
    num_orders = len(loc['ECHELLE_ORDERS'])
    # get the dimensions of the data
    ydim, xdim = loc['HCDATA'].shape
    # deal with removing orders (via weighting stats)
    rmask = np.ones(num_orders, dtype=bool)
    if len(remove_orders) > 0:
        rmask[np.array(remove_orders)] = False
    # storage of results
    keys = ['LITTROW_MEAN', 'LITTROW_SIG', 'LITTROW_MINDEV',
            'LITTROW_MAXDEV', 'LITTROW_PARAM', 'LITTROW_XX', 'LITTROW_YY',
            'LITTROW_INVORD', 'LITTROW_FRACLL', 'LITTROW_PARAM0',
            'LITTROW_MINDEVORD', 'LITTROW_MAXDEVORD']
    for key in keys:
        nkey = key + '_{0}'.format(iteration)
        loc[nkey] = []
        loc.set_source(nkey, func_name)
    # construct the Littrow cut points
    x_cut_points = np.arange(x_cut_step, xdim-x_cut_step, x_cut_step)
    # save to storage
    loc['X_CUT_POINTS_{0}'.format(iteration)] = x_cut_points
    # get the echelle order values
    # TODO check if mask needs resizing
    orderpos = torder[rmask]
    # get the inverse order number
    inv_orderpos = 1.0 / orderpos
    # loop around cut points and get littrow parameters and stats
    for it in range(len(x_cut_points)):
        # this iterations x cut point
        x_cut_point = x_cut_points[it]
        # get the fractional wavelength contrib. at each x cut point
        ll_point = ll_out[:, x_cut_point][rmask]
        ll_start_point = ll_out[n_order_init, x_cut_point]
        frac_ll_point = ll_point/ll_start_point
        # fit the inverse order numbers against the fractional
        #    wavelength contrib.
        coeffs = nanpolyfit(inv_orderpos, frac_ll_point, fit_degree)[::-1]
        coeffs0 = nanpolyfit(inv_orderpos, frac_ll_point, fit_degree)[::-1]
        # calculate the fit values
        cfit = np.polyval(coeffs[::-1], inv_orderpos)
        # calculate the residuals
        res = cfit - frac_ll_point
        # find the largest residual
        largest = np.max(abs(res))
        sigmaclip = abs(res) != largest
        # remove the largest residual
        inv_orderpos_s = inv_orderpos[sigmaclip]
        frac_ll_point_s = frac_ll_point[sigmaclip]
        # refit the inverse order numbers against the fractional
        #    wavelength contrib. after sigma clip
        coeffs = nanpolyfit(inv_orderpos_s, frac_ll_point_s, fit_degree)[::-1]
        # calculate the fit values (for all values - including sigma clipped)
        cfit = np.polyval(coeffs[::-1], inv_orderpos)
        # calculate residuals (in km/s) between fit and original values
        respix = speed_of_light * (cfit - frac_ll_point)/frac_ll_point
        # calculate stats
        mean = np.nansum(respix) / len(respix)
        mean2 = np.nansum(respix ** 2) / len(respix)
        rms = np.sqrt(mean2 - mean ** 2)
        mindev = np.min(respix)
        maxdev = np.max(respix)
        mindev_ord = np.argmin(respix)
        maxdev_ord = np.argmax(respix)
        # add to storage
        loc['LITTROW_INVORD_{0}'.format(iteration)].append(inv_orderpos)
        loc['LITTROW_FRACLL_{0}'.format(iteration)].append(frac_ll_point)
        loc['LITTROW_MEAN_{0}'.format(iteration)].append(mean)
        loc['LITTROW_SIG_{0}'.format(iteration)].append(rms)
        loc['LITTROW_MINDEV_{0}'.format(iteration)].append(mindev)
        loc['LITTROW_MAXDEV_{0}'.format(iteration)].append(maxdev)
        loc['LITTROW_MINDEVORD_{0}'.format(iteration)].append(mindev_ord)
        loc['LITTROW_MAXDEVORD_{0}'.format(iteration)].append(maxdev_ord)
        loc['LITTROW_PARAM_{0}'.format(iteration)].append(coeffs)
        loc['LITTROW_PARAM0_{0}'.format(iteration)].append(coeffs0)
        loc['LITTROW_XX_{0}'.format(iteration)].append(orderpos)
        loc['LITTROW_YY_{0}'.format(iteration)].append(respix)
        # if log then log output
        if log:
            emsg1 = 'Littrow check at X={0}'.format(x_cut_point)
            eargs = [mean * 1000, rms * 1000, mindev * 1000, maxdev * 1000,
                     mindev/rms, maxdev/rms]
            emsg2 = ('    mean:{0:.3f}[m/s] rms:{1:.2f}[m/s] min/max:{2:.2f}/'
                     '{3:.2f}[m/s] (frac:{4:.1f}/{5:.1f})'.format(*eargs))
            WLOG(p, '', [emsg1, emsg2])

    # return loc
    return loc


def extrapolate_littrow_sol(p, loc, ll, iteration=0):
    """
    Extrapolate and fit the Littrow solution at defined points and return
    the wavelengths, solutions, and cofficients of the littorw fits

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LITTROW_ORDER_FIT_DEG: int, defines the polynomial fit degree
            IC_HC_T_ORDER_START
            IC_LITTROW_ORDER_INIT int, defines the first order to for the fit
                                   solution
    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            HCDATA: numpy array (2D), the image data (used for shape)
            LITTROW_PARAM_i: list of numpy arrays, the gaussian fit
                             coefficients of each cut point
            X_CUT_POINTS_i: numpy array (1D), the x pixel cut points

            where i = iteration

    :param ll: numpy array (1D), the initial guess wavelengths for each line
    :param iteration: int, the iteration number (used so we can store multiple
                      calculations in loc, defines "i" in input and outputs
                      from p and loc

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                LITTROW_EXTRAP_i: numpy array (2D),
                                  size=([no. orders] by [no. cut points])
                                  the wavelength values at each cut point for
                                  each order
                LITTROW_EXTRAP_SOL_i: numpy array (2D),
                                  size=([no. orders] by [no. cut points])
                                  the wavelength solution at each cut point for
                                  each order
                LITTROW_EXTRAP_PARAM_i: numy array (2D),
                                  size=([no. orders] by [the fit degree +1])
                                  the coefficients of the fits for each cut
                                  point for each order

                where i = iteration
    """

    func_name = __NAME__ + '.extrapolate_littrow_sol()'
    # get parameters from p
    fit_degree = p['IC_LITTROW_ORDER_FIT_DEG']
    t_order_start = p['IC_HC_T_ORDER_START']
    n_order_init = p['IC_LITTROW_ORDER_INIT_{0}'.format(iteration)]

    # get parameters from loc
    litt_param = loc['LITTROW_PARAM_{0}'.format(iteration)]

    # get the dimensions of the data
    ydim, xdim = loc['HCDATA'].shape
    # get the pixel positions
    x_points = np.arange(xdim)
    # construct the Littrow cut points (in pixels)
    x_cut_points = loc['X_CUT_POINTS_{0}'.format(iteration)]
    # construct the Littrow cut points (in wavelength)
    ll_cut_points = ll[n_order_init][x_cut_points]

    # set up storage
    littrow_extrap = np.zeros((ydim, len(x_cut_points)), dtype=float)
    littrow_extrap_sol = np.zeros_like(loc['HCDATA'])
    littrow_extrap_param = np.zeros((ydim, fit_degree + 1), dtype=float)

    # calculate the echelle order position for this order
    echelle_order_nums = t_order_start - np.arange(ydim)
    # calculate the inverse echelle order nums
    inv_echelle_order_nums = 1.0 / echelle_order_nums

    # loop around the x cut points
    for it in range(len(x_cut_points)):
        # evaluate the fit for this x cut (fractional wavelength contrib.)
        cfit = np.polyval(litt_param[it][::-1], inv_echelle_order_nums)
        # evaluate littrow fit for x_cut_points on each order (in wavelength)
        litt_extrap_o = cfit * ll_cut_points[it]
        # add to storage
        littrow_extrap[:, it] = litt_extrap_o

    for order_num in range(ydim):
        # fit the littrow extrapolation
        param = nanpolyfit(x_cut_points, littrow_extrap[order_num],
                           fit_degree)[::-1]
        # add to storage
        littrow_extrap_param[order_num] = param
        # evaluate the polynomial for all pixels in data
        littrow_extrap_sol[order_num] = np.polyval(param[::-1], x_points)

    # add to storage
    loc['LITTROW_EXTRAP_{0}'.format(iteration)] = littrow_extrap
    loc['LITTROW_EXTRAP_SOL_{0}'.format(iteration)] = littrow_extrap_sol
    loc['LITTROW_EXTRAP_PARAM_{0}'.format(iteration)] = littrow_extrap_param

    sources = ['LITTROW_EXTRAP_{0}'.format(iteration),
               'LITTROW_EXTRAP_SOL_{0}'.format(iteration),
               'LITTROW_EXTRAP_PARAM_{0}'.format(iteration)]
    loc.set_sources(sources, func_name)
    # return loc
    return loc


def do_stuff(p, loc):
    # ----------------------------------------------------------------------
    # Set up all_lines storage
    # ----------------------------------------------------------------------
    # initialise up all_lines storage
    all_lines_1 = []
    # get parameters from p
    n_ord_start = p['IC_HC_N_ORD_START_2']
    n_ord_final = p['IC_HC_N_ORD_FINAL_2']
    # get values from loc
    xgau = np.array(loc['XGAU_T'])
    dv = np.array(loc['DV_T'])
    fit_per_order = np.array(loc['POLY_WAVE_SOL'])
    ew = np.array(loc['EW_T'])
    peak = np.array(loc['PEAK_T'])
    amp_catalog = np.array(loc['AMP_CATALOG'])
    wave_catalog = np.array(loc['WAVE_CATALOG'])
    ord_t = np.array(loc['ORD_T'])
    # loop through orders
    for iord in range(n_ord_start, n_ord_final):
        # keep relevant lines
        # -> right order
        # -> finite dv
        gg = (ord_t == iord)
        nlines = np.nansum(gg)
        # put lines into ALL_LINES structure
        # reminder:
        # gparams[0] = output wavelengths
        # gparams[1] = output sigma(gauss fit width)
        # gparams[2] = output amplitude(gauss fit)
        # gparams[3] = difference in input / output wavelength
        # gparams[4] = input amplitudes
        # gparams[5] = output pixel positions
        # gparams[6] = output pixel sigma width (gauss fit width in pixels)
        # gparams[7] = output weights for the pixel position

        # dummy array for weights
        test = np.ones(np.shape(xgau[gg]), 'd')
        # get the final wavelength value for each peak in order
        output_wave_1 = np.polyval(fit_per_order[iord][::-1], xgau[gg])
        # convert the pixel equivalent width to wavelength units
        xgau_ew_ini = xgau[gg] - ew[gg] / 2
        xgau_ew_fin = xgau[gg] + ew[gg] / 2
        ew_ll_ini = np.polyval(fit_per_order[iord, :], xgau_ew_ini)
        ew_ll_fin = np.polyval(fit_per_order[iord, :], xgau_ew_fin)
        ew_ll = ew_ll_fin - ew_ll_ini
        # put all lines in the order into array
        gau_params = np.column_stack((output_wave_1, ew_ll, peak[gg],
                                      wave_catalog[gg] - output_wave_1,
                                      amp_catalog[gg],
                                      xgau[gg], ew[gg], test))
        # append the array for the order into a list
        all_lines_1.append(gau_params)
        # save dv in km/s and auxiliary order number
        # res_1 = np.concatenate((res_1,2.997e5*(input_wave - output_wave_1)/
        #                        output_wave_1))
        # ord_save = np.concatenate((ord_save, test*iord))
    # add to loc
    loc['ALL_LINES_1'] = all_lines_1
    loc['LL_PARAM_1'] = np.array(fit_per_order)
    loc['LL_OUT_1'] = np.array(loc['WAVE_MAP2'])
    loc.set_sources(['ALL_LINES_1', 'LL_PARAM_1'], __NAME__ + '/main()')
    # For compatibility w/already defined functions, I need to save
    # here all_lines_2
    all_lines_2 = list(all_lines_1)
    loc['ALL_LINES_2'] = all_lines_2
    # # ------------------------------------------------------------------
    # # Littrow test
    # # ------------------------------------------------------------------
    # # calculate echelle orders
    # o_orders = np.arange(n_ord_start, n_ord_final)
    # echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
    # loc['ECHELLE_ORDERS'] = echelle_order
    # loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')
    # # reset Littrow fit degree
    # p['IC_LITTROW_FIT_DEG_1'] = 7
    # # Do Littrow check
    # ckwargs = dict(ll=loc['LL_OUT_1'][n_ord_start:n_ord_final, :],
    #                iteration=1, log=True)
    # loc = spirouTHORCA.calculate_littrow_sol(p, loc, **ckwargs)
    # # Plot wave solution littrow check
    # if p['DRS_PLOT']:
    #     # plot littrow x pixels against fitted wavelength solution
    #     sPlt.wave_littrow_check_plot(p, loc, iteration=1)


def decide_on_lamp_type(p, filename):
    """
    From a filename and p['IC_LAMPS'] decide on a lamp type for the file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_LAMPS: list of strings, the different allowed lamp types
            log_opt: string, log option, normally the program name
            FIB_POS: string, position of the fiber
            FIB_POS_ID: string; the HEADER key for the fiber
    :param filename: string, the filename to check for the lamp substring in

    :return lamp_type: string, the lamp type for this file (one of the values
                       in p['IC_LAMPS']
    """
    func_name = __NAME__ + '.decide_on_lamp_type()'
    # get fiber position from p
    fib_pos = p['FIB_POS']
    fib_pos_id = p['FIB_POS_ID']
    # storage for lamp type
    lamp_type = None
    # loop around each lamp in defined lamp types
    for lamp in p['IC_LAMPS']:
        # loop around the identifications of this lamp
        for lamp_it in p['IC_LAMPS'][lamp]:
            # check for lamp in filename
            if lamp_it in fib_pos:
                # check if we have already found a lamp type
                if lamp_type is not None:
                    emsg1 = ('Multiple lamp types found for fiber pos={0}, '
                             'lamp type is ambiguous'.format(fib_pos))
                    emsg2 = '    function={0}'.format(func_name)
                    WLOG(p, 'error', [emsg1, emsg2])
                else:
                    lamp_type = lamp
    # check that lamp is defined
    if lamp_type is None:
        emsg1 = ('Lamp type for file="{0}" cannot be identified.'
                 ''.format(filename))
        emsg2 = '\tHeader key {0}="{1}"'.format(fib_pos_id, fib_pos)
        emsg3 = ('\tMust be one of the following: {0}'
                 ''.format(', '.join(p['IC_LAMPS'])))
        emsg4 = '\t\tfunction={0}'.format(func_name)
        WLOG(p, 'error', [emsg1, emsg2, emsg3, emsg4])
    # finally return lamp type
    return lamp_type


def fp_wavelength_sol_new(p, loc):
    """
    Derives the FP line wavelengths from the first solution
    Follows the Bauer et al 2015 procedure

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_FP_N_ORD_START: int, defines first order FP solution is
                               calculated from

            IC_FP_N_ORD_FINAL: int, defines last order FP solution is
                               calculated to

            IC_HC_N_ORD_START_2: int, defines first order HC solution was
                                 calculated from

            IC_HC_N_ORD_FINAL_2: int, defines last order HC solution was
                                 calculated to

            DRIFT_PEAK_INTER_PEAK_SPACING: int, defines minimum line separation

            IC_FP_DOPD0: float, initial value of FP effective cavity width

            IC_FP_FIT_DEGREE: int, degree of polynomial fit

            log_opt: string, log option, normally the program name

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            FPDATA: the FP e2ds data
            LITTROW_EXTRAP_SOL_1: the wavelength solution derived from the HC
                                  and Littrow-constrained
            LL_PARAM_1: the parameters of the wavelength solution
            ALL_LINES_2: list of numpy arrays, length = number of orders
                       each numpy array contains gaussian parameters
                       for each found line in that order
            BLAZE: numpy array (2D), the blaze data

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                FP_LL_POS: numpy array, the initial wavelengths of the FP lines
                FP_XX_POS: numpy array, the pixel positions of the FP lines
                FP_M: numpy array, the FP line numbers
                FP_DOPD_T: numpy array, the measured cavity width for each line
                FP_AMPL: numpy array, the FP line amplitudes
                FP_LL_POS_NEW: numpy array, the corrected wavelengths of the
                               FP lines
                ALL_LINES_2: list of numpy arrays, length = number of orders
                             each numpy array contains gaussian parameters
                             for each found line in that order

    """
    func_name = __NAME__ + '.fp_wavelength_sol_new()'
    # get parameters from p
    dopd0 = p['IC_FP_DOPD0']
    fit_deg = p['IC_FP_FIT_DEGREE']
    fp_large_jump = p['IC_FP_LARGE_JUMP']
    n_ord_start_fp = p['IC_FP_N_ORD_START']
    n_ord_final_fp = p['IC_FP_N_ORD_FINAL']
    cm_ind = p['IC_WAVE_FP_CM_IND']

    # find FP lines
    loc = find_fp_lines_new(p, loc)
    all_lines_2 = loc['ALL_LINES_2']
    # set up storage
    llpos_all, xxpos_all, ampl_all = [], [], []
    m_fp_all, weight_bl_all, order_rec_all, dopd_all = [], [], [], []
    ll_prev, m_prev = np.array([]), np.array([])
    # loop through the orders from red to blue
    for order_num in range(n_ord_final_fp, n_ord_start_fp - 1, -1):
        # define storage
        floc = dict()
        # select the lines in the order
        gg = loc['ORDPEAK'] == order_num
        # store the initial wavelengths of the lines
        # floc['llpos'] = np.polynomial.chebyshev.chebval(
        #    loc['XPEAK'][gg],
        #    loc['LITTROW_EXTRAP_PARAM_1'][order_num])
        floc['llpos'] = np.polyval(
            loc['LITTROW_EXTRAP_PARAM_1'][order_num][::-1],
            loc['XPEAK'][gg])
        # store the pixel positions of the lines
        floc['xxpos'] = loc['XPEAK'][gg]
        # get the median pixel difference between successive lines
        #    (to check for gaps)
        xxpos_diff_med = np.nanmedian(floc['xxpos'][1:] - floc['xxpos'][:-1])
        # store the amplitudes of the lines
        floc['ampl'] = loc['AMPPEAK'][gg]
        # store the values of the blaze at the pixel positions of the lines
        floc['weight_bl'] = np.zeros_like(floc['llpos'])
        # get and normalize blaze for the order
        nblaze = loc['BLAZE'][order_num] / np.nanmax(loc['BLAZE'][order_num])
        for it in range(1, len(floc['llpos'])):
            floc['weight_bl'][it] = nblaze[int(np.round(floc['xxpos'][it]))]
        # store the order numbers
        floc['order_rec'] = loc['ORDPEAK'][gg]
        # set up storage for line numbers
        mpeak = np.zeros_like(floc['llpos'])
        # line number for the last (reddest) line of the order (by FP equation)
        mpeak[-1] = int(dopd0 / floc['llpos'][-1])
        # calculate successive line numbers
        for it in range(len(floc['llpos']) - 2, -1, -1):
            # check for gap in x positions
            flocdiff = floc['xxpos'][it + 1] - floc['xxpos'][it]
            lowcond = xxpos_diff_med - (0.25 * xxpos_diff_med)
            highcond = xxpos_diff_med + (0.25 * xxpos_diff_med)
            if lowcond < flocdiff < highcond:
                # no gap: add 1 to line number of previous line
                mpeak[it] = mpeak[it + 1] + 1
            # if there is a gap, fix it
            else:
                # get line x positions
                flocx0 = floc['xxpos'][it]
                flocx1 = floc['xxpos'][it + 1]
                # get line wavelengths
                floc0 = floc['llpos'][it]
                floc1 = floc['llpos'][it + 1]
                # estimate the number of peaks missed
                m_offset = int(np.round((flocx1 - flocx0) / xxpos_diff_med))
                # add to m of previous peak
                mpeak[it] = mpeak[it + 1] + m_offset
                # verify there's no dopd jump, fix if present
                dopd_1 = (mpeak[it] * floc0 - dopd0) * 1.e-3
                dopd_2 = (mpeak[it + 1] * floc1 - dopd0) * 1.e-3
                # do loops to check jumps
                if dopd_1 - dopd_2 > fp_large_jump:
                    while (dopd_1 - dopd_2) > fp_large_jump:
                        mpeak[it] = mpeak[it] - 1
                        dopd_1 = (mpeak[it] * floc0 - dopd0) * 1.e-3
                        dopd_2 = (mpeak[it + 1] * floc1 - dopd0) * 1.e-3
                elif dopd_1 - dopd_2 < -fp_large_jump:
                    while (dopd_1 - dopd_2) < -fp_large_jump:
                        mpeak[it] = mpeak[it] + 1
                        dopd_1 = (mpeak[it] * floc0 - dopd0) * 1.e-3
                        dopd_2 = (mpeak[it + 1] * floc1 - dopd0) * 1.e-3
        # determination of observed effective cavity width
        dopd_t = mpeak * floc['llpos']
        # store m and d
        floc['m_fp'] = mpeak
        floc['dopd_t'] = dopd_t
        # for orders other than the reddest, attempt to cross-match
        if order_num != n_ord_final_fp:
            # check for overlap
            if floc['llpos'][cm_ind] > ll_prev[0]:
                # find closest peak in overlap and get its m value
                ind = np.abs(ll_prev - floc['llpos'][cm_ind]).argmin()
                # the peak matching the reddest may not always be found!!
                # define maximum permitted difference
                llpos_diff_med = np.nanmedian(
                    floc['llpos'][1:] - floc['llpos'][:-1])
                # print(llpos_diff_med)
                # print(abs(ll_prev[ind] - floc['llpos'][-1]))
                # check if the difference is over the limit
                if abs(ll_prev[ind] - floc['llpos'][-1]) > 1.5 * llpos_diff_med:
                    # print('overlap line not matched')
                    ll_diff = ll_prev[ind] - floc['llpos'][-1]
                    ind2 = -2
                    # loop over next reddest peak until they match
                    while ll_diff > 1.5 * llpos_diff_med:
                        # check there is still overlap
                        if floc['llpos'][ind2] > ll_prev[0]:
                            ind = np.abs(ll_prev - floc['llpos'][ind2]).argmin()
                            ll_diff = ll_prev[ind] - floc['llpos'][ind2]
                            ind2 -= 1
                        else:
                            break
                m_match = m_prev[ind]
                # save previous mpeak calculated
                m_init = mpeak[cm_ind]
                # recalculate m if there's an offset from cross_match
                m_offset_c = m_match - m_init
                if m_offset_c != 0:
                    mpeak = mpeak + m_offset_c
                    # print note for dev if different
                    if p['DRS_DEBUG']:
                        wargs = [order_num, m_match - m_init]
                        wmsg = 'M difference for order {0}: {1}'
                        WLOG(p, '', wmsg.format(*wargs))
                    # recalculate observed effective cavity width
                    dopd_t = mpeak * floc['llpos']
                    # store new m and d
                    floc['m_fp'] = mpeak
                    floc['dopd_t'] = dopd_t
            else:
                wmsg = 'No overlap for order {0}'
                WLOG(p, 'warning', wmsg.format(order_num))
                # save previous mpeak calculated
                m_init = mpeak[cm_ind]
                m_test = mpeak[cm_ind]
                # get dopd for last line of current & first of last order
                dopd_curr = (m_test * floc['llpos'][cm_ind] - dopd0) * 1.e-3
                dopd_prev = (m_prev[0] * ll_prev[0] - dopd0) * 1.e-3
                # do loops to check jumps
                if dopd_curr - dopd_prev > fp_large_jump:
                    while (dopd_curr - dopd_prev) > fp_large_jump:
                        m_test = m_test - 1
                        dopd_curr = (m_test * floc['llpos'][cm_ind] - dopd0)
                        dopd_curr = dopd_curr * 1.e-3
                elif dopd_curr - dopd_prev < -fp_large_jump:
                    while (dopd_curr - dopd_prev) < -fp_large_jump:
                        m_test = m_test + 1
                        dopd_curr = (m_test * floc['llpos'][cm_ind] - dopd0)
                        dopd_curr = dopd_curr * 1.e-3
                # recalculate m if there's an offset from cross_match
                m_offset_c = m_test - m_init
                if m_offset_c != 0:
                    mpeak = mpeak + m_offset_c
                    # print note for dev if different
                    if p['DRS_DEBUG']:
                        wargs = [order_num, mpeak[cm_ind] - m_init]
                        wmsg = 'M difference for order {0}: {1}'
                        WLOG(p, '', wmsg.format(*wargs))
                    # recalculate observed effective cavity width
                    dopd_t = mpeak * floc['llpos']
                    # store new m and d
                    floc['m_fp'] = mpeak
                    floc['dopd_t'] = dopd_t

        # add to storage
        llpos_all += list(floc['llpos'])
        xxpos_all += list(floc['xxpos'])
        ampl_all += list(floc['ampl'])
        m_fp_all += list(floc['m_fp'])
        weight_bl_all += list(floc['weight_bl'])
        order_rec_all += list(floc['order_rec'])
        # difference in cavity width converted to microns
        dopd_all += list((floc['dopd_t'] - dopd0) * 1.e-3)
        # save numpy arrays of current order to be previous in next loop
        ll_prev = np.array(floc['llpos'])
        m_prev = np.array(floc['m_fp'])

    # convert to numpy arrays
    llpos_all = np.array(llpos_all)
    xxpos_all = np.array(xxpos_all)
    ampl_all = np.array(ampl_all)
    m_fp_all = np.array(m_fp_all)
    weight_bl_all = np.array(weight_bl_all)
    order_rec_all = np.array(order_rec_all)
    dopd_all = np.array(dopd_all)

    # fit a polynomial to line number v measured difference in cavity
    #     width, weighted by blaze
    with warnings.catch_warnings(record=True) as w:
        coeffs = nanpolyfit(m_fp_all, dopd_all, fit_deg, w=weight_bl_all)[::-1]
    spirouCore.WarnLog(p, w, funcname=func_name)
    # get the values of the fitted cavity width difference
    cfit = np.polyval(coeffs[::-1], m_fp_all)
    # update line wavelengths using the new cavity width fit
    newll = (dopd0 + cfit * 1000.) / m_fp_all
    # insert fp lines into all_lines2 (at the correct positions)
    all_lines_2 = insert_fp_lines(p, newll, llpos_all, all_lines_2,
                                  order_rec_all, xxpos_all, ampl_all)

    # add to loc
    loc['FP_LL_POS'] = llpos_all
    loc['FP_XX_POS'] = xxpos_all
    loc['FP_M'] = m_fp_all
    loc['FP_DOPD_OFFSET'] = dopd_all
    loc['FP_AMPL'] = ampl_all
    loc['FP_LL_POS_NEW'] = newll
    loc['ALL_LINES_2'] = all_lines_2
    loc['FP_DOPD_OFFSET_COEFF'] = coeffs
    loc['FP_DOPD_OFFSET_FIT'] = cfit
    loc['FP_ORD_REC'] = order_rec_all
    # set sources
    sources = ['FP_LL_POS', 'FP_XX_POS', 'FP_M', 'FP_DOPD_OFFSET',
               'FP_AMPL', 'FP_LL_POS_NEW', 'ALL_LINES_2',
               'FP_DOPD_OFFSET_COEFF', 'FP_DOPD_OFFSET_FIT', 'FP_ORD_REC']
    loc.set_sources(sources, func_name)

    return loc


def insert_fp_lines(p, newll, llpos_all, all_lines_2, order_rec_all,
                    xxpos_all, ampl_all):
    # get constants from p
    n_init = p['IC_FP_N_ORD_START']
    n_fin = p['IC_FP_N_ORD_FINAL']
    n_init_hc = p['IC_HC_N_ORD_START_2']
    n_fin_hc = p['IC_HC_N_ORD_FINAL_2']
    # insert FP lines into all_lines at the correct orders
    # define wavelength difference limit for keeping a line
    fp_cut = 3*np.std(newll - llpos_all)
    # define correct starting order number
    start_order = min(n_init, n_init_hc)
    # define starting point for prepended zeroes
    insert_count = 0
    for order_num in range(n_init, n_fin):
        if order_num < n_init_hc:
            # prepend zeros to all_lines if FP solution is fitted for
            #     bluer orders than HC was
            all_lines_2.insert(insert_count, np.zeros((1, 8), dtype=float))
            # add 1 to insertion counter for next order
            insert_count += 1
        elif order_num >= n_fin_hc:
            # append zeros to all_lines if FP solution is fitted for
            #     redder orders than HC was
            all_lines_2.append(np.zeros((1, 8), dtype=float))
        for it in range(len(order_rec_all)):
            # find lines corresponding to order number
            if order_rec_all[it] == order_num:
                # check wavelength difference below limit
                if abs(newll[it] - llpos_all[it]) < fp_cut:
                    # put FP line data into an array
                    # newdll = newll[it] - llpos_all[it]
                    fp_line = np.array([newll[it], 0.0, 0.0, 0.0,
                                        0.0, xxpos_all[it], 0.0, ampl_all[it]])
                    fp_line = fp_line.reshape((1, 8))
                    # append FP line data to all_lines
                    torder = order_num - start_order
                    tvalues = [all_lines_2[torder], fp_line]
                    all_lines_2[torder] = np.concatenate(tvalues)
    # return all lines 2
    return all_lines_2


def find_fp_lines_new(p, loc):
    # get parameters from p
    # minimum spacing between FP peaks
    # peak_spacing = p['DRIFT_PEAK_INTER_PEAK_SPACING']
    # get redefined variables
    loc = find_fp_lines_new_setup(loc)
    # reset minimum value (to find more edge peaks which are important)
    # p['DRIFT_PEAK_PEAK_SIG_LIM']['fp'] = 0.7
    # use spirouRV to get the position of FP peaks from reference file
    loc = spirouRV.CreateDriftFile(p, loc)
    # remove wide/spurious peaks
    loc = spirouRV.RemoveWidePeaks(p, loc)
    # return loc
    return loc


def find_fp_lines_new_setup(loc):
    # auxiliary function to set up variables for find_fp_lines_new

    # pipe inputs to loc with correct names
    # set fpfile as ref file
    loc['SPEREF'] = loc['FPDATA']
    # set wavelength solution as the one from the HC lines
    loc['WAVE'] = loc['LITTROW_EXTRAP_SOL_1']
    # set lamp as FP
    loc['LAMP'] = 'fp'

    return loc


def fit_1d_solution(p, loc, ll, iteration=0):
    """
    Fits the 1D solution between wavelength and pixel postion and inverts it
    into a fit between pixel position and wavelength

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, log option, normally the program name
            FIBER: string, the fiber type (i.e. AB or A or B or C)

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            ECHELLE_ORDERS: numpy array (1D), the echelle order numbers
            HCDATA: numpy array (2D), the image data (used for shape)
            ALL_LINES_i: list of numpy arrays, length = number of orders
                         each numpy array contains gaussian parameters
                         for each found line in that order
            IC_ERRX_MIN: float, the minimum instrumental error
            IC_LL_DEGR_FIT: int, the wavelength fit polynomial order
            IC_MAX_LLFIT_RMS: float, the max rms for the wavelength
                              sigma-clip fit
            IC_HC_T_ORDER_START: int, defines the echelle order of
                                the first e2ds order

    :param ll: numpy array (1D), the initial guess wavelengths for each line
    :param iteration: int, the iteration number (used so we can store multiple
                      calculations in loc, defines "i" in input and outputs
                      from p and loc

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                X_MEAN_i: float, the mean residual from the fit [km/s]
                X_VAR_i: float, the rms residual from the fit [km/s]
                X_ITER_i: numpy array(1D), the last line central position, FWHM
                and the number of lines in each order
                X_PARAM_i: numpy array (1D), the coefficients of the fit to x
                           pixel position as a function of wavelength
                X_DETAILS_i: list, [lines, xfit, cfit, weight] where
                             lines= original wavelength-centers used for the fit
                             xfit= original pixel-centers used for the fit
                             cfit= fitted pixel-centers using fit coefficients
                             weight=the line weights used
                SCALE_i: list, the convertion for each line into wavelength
                LL_MEAN_i: float, the mean residual after inversion [km/s]
                LL_VAR_i: float, the rms residual after inversion [km/s]
                LL_PARAM_i: numpy array (1D), the cofficients of the inverted
                            fit (i.e. wavelength as a function of x pixel
                            position)
                LL_DETAILS_i: numpy array (1D), the [nres, wei] where
                              nres = normalised residuals in km/s
                              wei = the line weights
                LL_OUT_i: numpy array (2D), the output wavelengths for each
                          pixel and each order (in the shape of original image)
                DLL_OUT_i: numpy array (2D), the output delta wavelengths for
                           each pixel and each order (in the shape of original
                           image)
                TOTAL_LINES_i: Total number of lines used

                where i = iteration

    ALL_LINES_i definition:
        ALL_LINES_i[row] = [gparams1, gparams2, ..., gparamsN]

                    where:
                        gparams[0] = output wavelengths
                        gparams[1] = output sigma (gauss fit width)
                        gparams[2] = output amplitude (gauss fit)
                        gparams[3] = difference in input/output wavelength
                        gparams[4] = input amplitudes
                        gparams[5] = output pixel positions
                        gparams[6] = output pixel sigma width
                                          (gauss fit width in pixels)
                        gparams[7] = output weights for the pixel position
    """

    func_name = __NAME__ + '.fit_1d_solution()'
    # get 1d solution
    loc = fit_1d_ll_solution(p, loc, ll, iteration)
    # invert solution
    loc = invert_1ds_ll_solution(p, loc, ll, iteration)
    # get the total number of orders to fit
    num_orders = len(loc['ALL_LINES_{0}'.format(iteration)])
    # get the dimensions of the data
    ydim, xdim = loc['HCDATA'].shape
    # get inv_params
    inv_params = loc['LL_PARAM_{0}'.format(iteration)]
    # set pixel shift to zero, as doesn't apply here
    pixel_shift_inter = 0
    pixel_shift_slope = 0
    # get new line list
    ll_out = spirouMath.get_ll_from_coefficients(pixel_shift_inter,
                                                 pixel_shift_slope,
                                                 inv_params, xdim, num_orders)
    # get the first derivative of the line list
    dll_out = spirouMath.get_dll_from_coefficients(inv_params, xdim, num_orders)
    # find the central pixel value
    centpix = ll_out.shape[1]//2
    # get the mean pixel scale (in km/s/pixel) of the central pixel
    norm = dll_out[:, centpix]/ll_out[:, centpix]
    meanpixscale = speed_of_light * np.nansum(norm)/len(ll_out[:, centpix])
    # get the total number of lines used
    total_lines = int(np.nansum(loc['X_ITER_2'][:, 2]))
    # add to loc
    loc['LL_OUT_{0}'.format(iteration)] = ll_out
    loc.set_source('LL_OUT_{0}'.format(iteration), func_name)
    loc['DLL_OUT_{0}'.format(iteration)] = dll_out
    loc.set_source('DLL_OUT_{0}'.format(iteration), func_name)
    loc['TOTAL_LINES_{0}'.format(iteration)] = total_lines
    loc.set_source('TOTAL_LINES_{0}'.format(iteration), func_name)
    # log message
    wmsg = 'On fiber {0} mean pixel scale at center: {1:.4f} [km/s/pixel]'
    WLOG(p, 'info', wmsg.format(p['FIBER'], meanpixscale))
    # return loc
    return loc


def fit_1d_ll_solution(p, loc, ll, iteration):
    func_name = __NAME__ + '.fit_1d_ll_solution()'
    # get constants from p
    #   max_weight is the weight corresponding to IC_ERRX_MIN
    max_weight = 1.0 / p['IC_ERRX_MIN'] ** 2
    fit_degree = p['IC_LL_DEGR_FIT']
    max_ll_fit_rms = p['IC_MAX_LLFIT_RMS']
    t_ord_start = p['IC_HC_T_ORDER_START']
    threshold = 1e-30
    # get data from loc
    torder = loc['ECHELLE_ORDERS']
    all_lines = loc['ALL_LINES_{0}'.format(iteration)]
    # Get the number of orders
    num_orders = ll.shape[0]
    # -------------------------------------------------------------------------
    # set up all storage
    final_iter = []       # will fill [wmean, var, length]
    final_param = []      # will fill the fit coefficients
    final_details = []    # will fill [lines, x_fit, cfit, weight]
    final_dxdl = []       # will fill the derivative of the fit coefficients
    scale = []            # conversion factor to km/s
    # set up global stats
    sweight = 0.0
    wsumres = 0.0
    wsumres2 = 0.0
    # loop around orders
    for order_num in np.arange(num_orders):
        # ---------------------------------------------------------------------
        # get this orders parameters
        weights = all_lines[order_num][:, 7]
        diff_in_out = all_lines[order_num][:, 3]
        centers = all_lines[order_num][:, 0]
        pixelcenters = all_lines[order_num][:, 5]
        # ---------------------------------------------------------------------
        # only keep the lines that have postive weight
        goodlinemask = weights > threshold
        lines = centers[goodlinemask] + diff_in_out[goodlinemask]
        x_fit = pixelcenters[goodlinemask]
        # get the weights and modify by max_weight
        weight = (weights[goodlinemask] * max_weight)
        weight = weight / (weights[goodlinemask] + max_weight)
        # ---------------------------------------------------------------------
        # iteratively try to improve the fit
        improve = 1
        iter0, details = [], []
        wmean, var = 0, 0
        # sigma clip the largest rms until RMS < MAX_RMS
        while improve:
            # fit wavelength to pixel solution (with polynomial)
            ww = np.sqrt(weight)
            coeffs = nanpolyfit(lines, x_fit, fit_degree, w=ww)[::-1]
            # calculate the fit
            cfit = np.polyval(coeffs[::-1], lines)
            # calculate the variance
            res = cfit - x_fit
            wsig = np.nansum(res**2 * weight) / np.nansum(weight)
            wmean = (np.nansum(res * weight) / np.nansum(weight))
            var = wsig - (wmean ** 2)
            # append stats
            iter0.append([np.array(wmean), np.array(var),
                         np.array(coeffs)])
            details.append([np.array(lines),  np.array(x_fit),
                            np.array(cfit), np.array(weight)])
            # check improve condition (RMS > MAX_RMS)
            ll_fit_rms = abs(res) * np.sqrt(weight)
            badrms = ll_fit_rms > max_ll_fit_rms
            improve = np.nansum(badrms)
            # set largest weighted residual to zero
            largest = np.max(ll_fit_rms)
            badpoints = ll_fit_rms == largest
            weight[badpoints] = 0.0
            # only keep the lines that have postive weight
            goodmask = weight > 0.0
            # check that we have points
            if np.nansum(goodmask) == 0:
                emsg1 = ('Order {0}: Sigma clipping in 1D fit solution '
                         'failed'.format(order_num))
                emsg2 = ('\tRMS > MAX_RMS={0}'
                         ''.format(max_ll_fit_rms))
                emsg3 = '\tfunction = {0}'.format(func_name)
                WLOG(p, 'error', [emsg1, emsg2, emsg3])
            else:
                lines = lines[goodmask]
                x_fit = x_fit[goodmask]
                weight = weight[goodmask]
        # ---------------------------------------------------------------------
        # log the fitted wave solution
        wmsg1 = 'Fit wave. sol. order: {0:3d} ({1:2d}) [{2:.1f}- {3:.1f}]'
        wargs1 = [torder[order_num], t_ord_start - torder[order_num],
                  ll[order_num][0], ll[order_num][-1]]
        wmsg2 = ('\tmean: {0:.4f}[mpix] rms={1:.5f} [mpix] ({2:2d} it.) '
                 '[{3} --> {4} lines] ')
        wargs2 = [wmean * 1000, np.sqrt(var) * 1000, len(iter0),
                  len(details[0][1]), len(details[-1][1])]
        wmsgs = [wmsg1.format(*wargs1), wmsg2.format(*wargs2)]
        WLOG(p, '', wmsgs)
        # ---------------------------------------------------------------------
        # append to all storage
        # ---------------------------------------------------------------------
        # append the last wmean, var and number of lines
        num_lines = len(details[-1][1])
        final_iter.append([iter0[-1][0], iter0[-1][1], num_lines])
        # append the last coefficients
        final_param.append(iter0[-1][2])
        # append the last details [lines, x_fit, cfit, weight]
        final_details.append(np.array(details[-1]))
        # append the derivative of the coefficients
        poly = np.poly1d(iter0[-1][2][::-1])
        dxdl = np.polyder(poly)(details[-1][0])
        final_dxdl.append(dxdl)
        # ---------------------------------------------------------------------
        # global statistics
        # ---------------------------------------------------------------------
        # work out conversion factor
        convert = speed_of_light / (dxdl * details[-1][0])
        # get res1
        res1 = details[-1][1] - details[-1][2]
        # sum the weights (recursively)
        sweight += np.nansum(details[-1][3])
        # sum the weighted residuals in km/s
        wsumres += np.nansum(res1 * convert * details[-1][3])
        # sum the weighted squared residuals in km/s
        wsumres2 += np.nansum(details[-1][3] * (res1 * convert) ** 2)
        # store the conversion to km/s
        scale.append(convert)
    # convert to arrays
    final_iter = np.array(final_iter)
    final_param = np.array(final_param)
    # calculate the final var and mean
    final_mean = (wsumres / sweight)
    final_var = (wsumres2 / sweight) - (final_mean ** 2)
    # log the global stats
    total_lines = np.nansum(final_iter[:, 2])
    wmsg1 = 'On fiber {0} fit line statistic:'.format(p['FIBER'])
    wargs2 = [final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
              total_lines, 1000.0 * np.sqrt(final_var / total_lines)]
    wmsg2 = ('\tmean={0:.3f}[m/s] rms={1:.1f} {2} lines (error on mean '
             'value:{3:.2f}[m/s])'.format(*wargs2))
    WLOG(p, 'info', [wmsg1, wmsg2])
    # save outputs to loc
    loc['X_MEAN_{0}'.format(iteration)] = final_mean
    loc['X_VAR_{0}'.format(iteration)] = final_var
    loc['X_ITER_{0}'.format(iteration)] = final_iter
    loc['X_PARAM_{0}'.format(iteration)] = final_param
    loc['X_DETAILS_{0}'.format(iteration)] = final_details
    loc['SCALE_{0}'.format(iteration)] = scale
    sources = ['X_MEAN_{0}'.format(iteration),
               'X_VAR_{0}'.format(iteration),
               'X_ITER_{0}'.format(iteration),
               'X_PARAM_{0}'.format(iteration),
               'X_DETAILS_{0}'.format(iteration),
               'SCALE_{0}'.format(iteration)]
    loc.set_sources(sources, func_name)
    # return loc
    return loc


def invert_1ds_ll_solution(p, loc, ll, iteration=0):
    func_name = __NAME__ + '.invert_1ds_ll_solution()'
    # get constants from p
    fit_degree = p['IC_LL_DEGR_FIT']
    # get data from loc
    details = loc['X_DETAILS_{0}'.format(iteration)]
    iter0 = loc['X_ITER_{0}'.format(iteration)]
    # Get the number of orders
    num_orders = ll.shape[0]
    # loop around orders
    inv_details = []
    inv_params = []
    sweight = 0.0
    wsumres = 0.0
    wsumres2 = 0.0
    for order_num in np.arange(num_orders):
        # get the lines and wavelength fit for this order
        lines = details[order_num][0]
        cfit = details[order_num][2]
        wei = details[order_num][3]
        # get the number of lines
        num_lines = len(lines)
        # set weights
        weight = np.ones(num_lines, dtype=float)
        # get fit coefficients
        coeffs = nanpolyfit(cfit, lines, fit_degree, w=weight)[::-1]
        # get the y values for the coefficients
        icfit = np.polyval(coeffs[::-1], cfit)
        # work out the residuals
        res = icfit - lines
        # work out the normalised res in km/s
        nres = speed_of_light * (res / lines)
        # append values to storage
        inv_details.append([nres, wei])
        inv_params.append(coeffs)
        # ---------------------------------------------------------------------
        # invert parameters
        # ---------------------------------------------------------------------
        # sum the weights (recursively)
        sweight += np.nansum(wei)
        # sum the weighted residuals in km/s
        wsumres += np.nansum(nres * wei)
        # sum the weighted squared residuals in km/s
        wsumres2 += np.nansum(wei * nres ** 2)
    # calculate the final var and mean
    final_mean = (wsumres / sweight)
    final_var = (wsumres2 / sweight) - (final_mean ** 2)
    # log the invertion process
    total_lines = np.nansum(iter0[:, 2])
    wargs = [final_mean * 1000.0, np.sqrt(final_var) * 1000.0,
             1000.0 * np.sqrt(final_var / total_lines)]
    wmsg = ('Inversion noise ==> mean={0:.3f}[m/s] rms={1:.1f}'
            '(error on mean value:{2:.2f}[m/s])'.format(*wargs))
    WLOG(p, '', wmsg)
    # save outputs to loc
    loc['LL_MEAN_{0}'.format(iteration)] = final_mean
    loc['LL_VAR_{0}'.format(iteration)] = final_var
    loc['LL_PARAM_{0}'.format(iteration)] = np.array(inv_params)
    loc['LL_DETAILS_{0}'.format(iteration)] = inv_details
    sources = ['LL_MEAN_{0}'.format(iteration),
               'LL_VAR_{0}'.format(iteration),
               'LL_PARAM_{0}'.format(iteration),
               'LL_DETAILS_{0}'.format(iteration)]
    loc.set_sources(sources, func_name)
    # return loc
    return loc


def join_orders(p, loc):
    """
    Merge the littrow extrapolated solutions with the fitted line solutions

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_HC_N_ORD_START: int, defines first order solution is calculated
            IC_HC_N_ORD_FINAL: int, defines last order solution is calculated
                                from

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            LL_OUT_2: numpy array (2D), the output wavelengths for each
                      pixel and each order (in the shape of original image)
            DLL_OUT_2: numpy array (2D), the output delta wavelengths for
                       each pixel and each order (in the shape of original
                       image)
            LITTROW_EXTRAP_SOL_2: numpy array (2D),
                              size=([no. orders] by [no. cut points])
                              the wavelength solution at each cut point for
                              each order
            LITTROW_EXTRAP_PARAM_2: numy array (2D),
                              size=([no. orders] by [the fit degree +1])
                              the coefficients of the fits for each cut
                              point for each order

    :return loc: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            LL_FINAL: numpy array, the joined littrow extrapolated and fitted
                      solution wavelengths
            LL_PARAM_FINAL: numpy array, the joined littrow extrapolated and
                            fitted fit coefficients

    """

    func_name = __NAME__ + '.join_orders()'
    # get parameters from p
    n_ord_start_2 = p['IC_HC_N_ORD_START_2']
    n_ord_final_2 = p['IC_HC_N_ORD_FINAL_2']

    # get data from loc
    # the second iteration outputs
    ll_out_2 = loc['LL_OUT_2']
    param_out_2 = loc['LL_PARAM_2']

    # the littrow extrapolation (for orders < n_ord_start_2)
    litt_extrap_sol_blue = loc['LITTROW_EXTRAP_SOL_2'][:n_ord_start_2]
    litt_extrap_sol_param_blue = loc['LITTROW_EXTRAP_PARAM_2'][:n_ord_start_2]

    # the littrow extrapolation (for orders > n_ord_final_2)
    litt_extrap_sol_red = loc['LITTROW_EXTRAP_SOL_2'][n_ord_final_2:]
    litt_extrap_sol_param_red = loc['LITTROW_EXTRAP_PARAM_2'][n_ord_final_2:]

    # create stack
    ll_stack, param_stack = [], []
    # add extrapolation from littrow to orders < n_ord_start_2
    if len(litt_extrap_sol_blue) > 0:
        ll_stack.append(litt_extrap_sol_blue)
        param_stack.append(litt_extrap_sol_param_blue)
    # add second iteration outputs
    if len(ll_out_2) > 0:
        ll_stack.append(ll_out_2)
        param_stack.append(param_out_2)
    # add extrapolation from littrow to orders > n_ord_final_2
    if len(litt_extrap_sol_red) > 0:
        ll_stack.append(litt_extrap_sol_red)
        param_stack.append(litt_extrap_sol_param_red)

    # convert stacks to arrays and add to storage
    loc['LL_FINAL'] = np.vstack(ll_stack)
    loc['LL_PARAM_FINAL'] = np.vstack(param_stack)
    loc.set_sources(['LL_FINAL', 'LL_PARAM_FINAL'], func_name)

    # return loc
    return loc


def no_overlap_match_calc(p, ord_num, fp_ll_ord, fp_ll_ord_prev,
                          fp_ll_diff, fp_ll_diff_prev, m_ord_prev, dif_n):
    """
    Calculate the absolute FP peak numbers when there is no overlap from one
    order to the next by estimating the number of peaks missed

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            WAVE_FP_LLDIF_MIN: float, defines the minimum fraction of the median
                        wavelength difference we accept as no gap between lines
            WAVE_FP_LLDIF_MIN: float, defines the maximum fraction of the median
                        wavelength difference we accept as no gap between lines

    :param ord_num: the order number
    :param fp_ll_ord: the FP peak wavelengths for the current order
    :param fp_ll_ord_prev: the FP peak wavelengths for the previous order
    :param fp_ll_diff: wavelength difference between consecutive FP peaks
                       (current order)
    :param fp_ll_diff_prev: wavelength difference between consecutive FP peaks
                       (previous order)
    :param m_ord_prev: absolute peak numbers of previous order
    :param dif_n: differential peak numbering for all orders

    :return m_ord: absolute peak numbers for current order

    """
    func_name = __NAME__ + '.no_overlap_match_calc()'
    # print warning re no overlap
    wmsg = 'no overlap for order {0}, estimating gap size'
    WLOG(p, 'warning', wmsg.format(ord_num))
    # masks to keep only difference between no-gap lines for both orders
    mask_ll_diff = fp_ll_diff > p['WAVE_FP_LLDIF_MIN'] * \
                   np.nanmedian(fp_ll_diff)
    mask_ll_diff &= fp_ll_diff < p['WAVE_FP_LLDIF_MAX'] * \
                    np.nanmedian(fp_ll_diff)
    mask_ll_diff_prev = fp_ll_diff_prev > p['WAVE_FP_LLDIF_MIN'] * \
                        np.nanmedian(fp_ll_diff_prev)
    mask_ll_diff_prev &= fp_ll_diff_prev < p['WAVE_FP_LLDIF_MAX'] * \
                         np.nanmedian(fp_ll_diff_prev)
    # get last diff for current order, first for prev
    ll_diff_fin = fp_ll_diff[mask_ll_diff][-1]
    ll_diff_init = fp_ll_diff_prev[mask_ll_diff_prev][0]
    # calculate wavelength difference between end lines
    ll_miss = fp_ll_ord_prev[0] - fp_ll_ord[-1]
    # estimate lines missed using ll_diff from each order
    m_end_1 = int(np.round(ll_miss / ll_diff_fin))
    m_end_2 = int(np.round(ll_miss / ll_diff_init))
    # check they are the same, print warning if not
    if not m_end_1 == m_end_2:
        wmsg = ('Missing line estimate miss-match: {0} v {1} '
                'from {2:.5f} v {3:.5f}')
        wargs = [m_end_1, m_end_2, ll_diff_fin, ll_diff_init]
        WLOG(p, 'warning', wmsg.format(*wargs))
    # calculate m_end, absolute peak number for last line of the order
    m_end = int(m_ord_prev[0]) + m_end_1
    # define array of absolute peak numbers for the order
    m_ord = m_end + dif_n[ord_num][-1] - dif_n[ord_num]
    # return m_ord
    return m_ord

def sigclip_polyfit(p, xx, yy, degree, weight = None):
    """
    Fit a polynomial with sigma-clipping of outliers

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            WAVE_SIGCLIP: clipping parameter

    :param xx: numpy array, x values to fit
    :param yy: numpy array, y values to fit
    :param degree: int, the degree of fit
    :param weight: optional, numpy array, weights to the fit

    :return coeff: the fit coefficients
    :return mask: the sigma-clip mask

    """
    # read constants from p
    sigclip = p['WAVE_SIGCLIP']
    # initialise the while loop
    sigmax = sigclip + 1
    # initialise mask
    mask = np.ones_like(xx, dtype='Bool')
    while sigmax > sigclip:
        # Need to mask weight here if not None
        if weight is not None:
            weight2 = weight[mask]
        else:
            weight2 = None
        # fit on masked values
        coeff = nanpolyfit(xx[mask], yy[mask], deg=degree, w=weight2)
        # get residuals (not masked or dimension breaks)
        res = yy - np.polyval(coeff, xx)
        # normalise the residuals
        res = np.abs(res / np.nanmedian(np.abs(res[mask])))
        # get the max residual in sigmas
        sigmax = np.max(res[mask])
        # mask all outliers
        if sigmax > sigclip:
            mask[res >= sigclip] = False
    # return the coefficients and mask
    return coeff, mask

def fit_1d_solution_sigclip(p, loc):
    """
    Fits the 1D solution between pixel position and wavelength
    Uses sigma-clipping and removes modulo 1 pixel errors

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            WAVE_N_ORD_START: first order of the wavelength solution
            WAVE_N_ORD_FINAL: last order of the wavelength solution

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            FP_XX_NEW: FP pixel pisitions
            FP_LL_NEW: FP wavelengths
            FP_ORD_NEW: FP line orders
            FP_WEI: FP line weights

    :param ll: numpy array (1D), the initial guess wavelengths for each line
    :param iteration: int, the iteration number (used so we can store multiple
                      calculations in loc, defines "i" in input and outputs
                      from p and loc

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                FP_ORD_CL = np array, FP line orders (sigma-clipped)
                FP_LLIN_CL = np array, FP wavelengths (sigma-clipped)
                FP_XIN_CL = np array, FP initial pixel values (sigma-clipped)
                FP_XOUT_CL = np array, FP corrected pixel values (sigma-clipped)
                FP_WEI_CL = np array, weights (sigma-clipped)
                RES_CL = np array, normalised residuals in km/s
                LL_OUT_2 = np array, output wavelength map
                LL_PARAM_2 = np array, polynomial coefficients
                X_MEAN_2 = final mean
                X_VAR_2 = final var
                TOTAL_LINES_2 = total lines
                SCALE_2 = scale

    """
    func_name = __NAME__ + '.fit_1d_solution_sigclip()'
    # read constants from p
    n_init = p['WAVE_N_ORD_START']
    n_fin = p['WAVE_N_ORD_FINAL']

    # set up storage arrays
    xpix = np.arange(loc['NBPIX'])
    wave_map_final = np.zeros((n_fin - n_init, loc['NBPIX']))
    poly_wave_sol_final = np.zeros((n_fin - n_init, p['IC_LL_DEGR_FIT'] + 1))

    # fit x v wavelength w/sigma-clipping
    # we remove modulo 1 pixel errors in line centers - 3 iterations
    n_ite_mod_x = 3
    for ite in range(n_ite_mod_x):
        # set up storage
        wsumres = 0.0
        wsumres2 = 0.0
        sweight = 0.0
        fp_x_final_clip = []
        fp_x_in_clip = []
        fp_ll_final_clip = []
        fp_ll_in_clip = []
        fp_ord_clip = []
        res_clip = []
        wei_clip = []
        scale = []
        res_modx = np.zeros_like(loc['FP_XX_NEW'])
        # loop over the orders
        for onum in range(n_fin - n_init):
            # order mask
            ord_mask = np.where(loc['FP_ORD_NEW'] == onum +
                                n_init)
            # get FP line pixel positions for the order
            fp_x_ord = loc['FP_XX_NEW'][ord_mask]
            # get new FP line wavelengths for the order
            fp_ll_new_ord = np.asarray(loc['FP_LL_NEW'])[ord_mask]
            # get weights for the order
            wei_ord = np.asarray(loc['FP_WEI'])[ord_mask]
            # fit solution for the order w/sigma-clipping
            coeffs, mask = sigclip_polyfit(p, fp_x_ord, fp_ll_new_ord,
                                           p['IC_LL_DEGR_FIT'], wei_ord)
            # store the coefficients
            poly_wave_sol_final[onum] = coeffs[::-1]
            # get the residuals modulo x
            res_modx[ord_mask] = speed_of_light * (fp_ll_new_ord /
                                                   np.polyval(coeffs,
                                                              fp_x_ord) - 1)
            # mask input arrays for statistics
            fp_x_ord = fp_x_ord[mask]
            fp_ll_new_ord = fp_ll_new_ord[mask]
            wei_ord = wei_ord[mask]
            # get final wavelengths
            fp_ll_final_ord = np.polyval(coeffs, fp_x_ord)
            # save wave map
            wave_map_final[onum] = np.polyval(coeffs, xpix)
            # save masked arrays
            fp_x_final_clip.append(fp_x_ord)
            fp_x_in_clip.append(loc['FP_XX_INIT'][ord_mask][mask])
            fp_ll_final_clip.append(fp_ll_final_ord)
            fp_ll_in_clip.append(fp_ll_new_ord)
            fp_ord_clip.append(loc['FP_ORD_NEW'][ord_mask][mask])
            wei_clip.append(wei_ord)
            # residuals in km/s
            # calculate the residuals for the final masked arrays
            res = fp_ll_final_ord - fp_ll_new_ord
            res_clip.append(res * speed_of_light / fp_ll_new_ord)
            # save stats
            # get the derivative of the coefficients
            poly = np.poly1d(coeffs)
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
        cos = np.cos(2 * np.pi * (loc['FP_XX_NEW'] % 1))
        sin = np.sin(2 * np.pi * (loc['FP_XX_NEW'] % 1))

        # find points that are not residual outliers
        # We fit a zeroth order polynomial, so it returns
        # outliers to the mean value.
        outl_fit, mask_all = sigclip_polyfit(p, loc['FP_XX_NEW'],
                                             res_modx, 0)
        # create model
        acos = np.nansum(cos[mask_all] * res_modx[mask_all]) / \
               np.nansum(cos[mask_all] ** 2)
        asin = np.nansum(sin[mask_all] * res_modx[mask_all]) / \
               np.nansum(sin[mask_all] ** 2)
        model_sin = (cos * acos + sin * asin)
        # update the xpeak positions with model
        loc['FP_XX_NEW'] += model_sin / 2.2

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

    # save final (sig-clipped) arrays to loc
    loc['FP_ORD_CL'] = np.array(np.concatenate(fp_ord_clip).ravel())
    loc['FP_LLIN_CL'] = np.array(np.concatenate(fp_ll_in_clip).ravel())
    loc['FP_XIN_CL'] = np.array(np.concatenate(fp_x_in_clip).ravel())
    loc['FP_XOUT_CL'] = np.array(np.concatenate(fp_x_final_clip).ravel())
    loc['FP_WEI_CL'] = np.array(np.concatenate(wei_clip).ravel())
    loc['RES_CL'] = np.array(np.concatenate(res_clip).ravel())
    loc['LL_OUT_2'] = wave_map_final
    loc['LL_PARAM_2'] = poly_wave_sol_final
    loc['X_MEAN_2'] = final_mean
    loc['X_VAR_2'] = final_var
    loc['TOTAL_LINES_2'] = total_lines
    loc['SCALE_2'] = scale

    # set up x_details and ll_details structures for line list table:
    # X_DETAILS_i: list, [lines, xfit, cfit, weight] where
    #   lines= original wavelength-centers used for the fit
    #   xfit= original pixel-centers used for the fit
    #   cfit= fitted pixel-centers using fit coefficients
    #   weight=the line weights used
    # LL_DETAILS_i: numpy array (1D), the [nres, wei] where
    #   nres = normalised residuals in km/s
    #   wei = the line weights
    x_details = []
    ll_details = []
    for ord_num in range(n_init, n_fin):
        omask = loc['FP_ORD_CL'] == ord_num
        x_details.append([loc['FP_LLIN_CL'][omask], loc['FP_XIN_CL'][omask],
                          loc['FP_XOUT_CL'][omask], loc['FP_WEI_CL'][omask]])
        ll_details.append([loc['RES_CL'][omask], loc['FP_WEI_CL'][omask]])
    loc['X_DETAILS_2'] = x_details
    loc['LL_DETAILS_2'] = ll_details

    # return
    return loc

# =============================================================================
# End of code
# =============================================================================

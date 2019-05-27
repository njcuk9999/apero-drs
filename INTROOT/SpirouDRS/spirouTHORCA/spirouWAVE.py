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
from collections import OrderedDict

from SpirouDRS import spirouBACK
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouRV
from SpirouDRS.spirouCore import spirouMath
from SpirouDRS.spirouCore.spirouMath import nanpolyfit

from . import spirouTHORCA

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
def calculate_instrument_drift(p, loc):
    """
    Calculate the instrumental drift between the reference file and the current
    file

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                DRS_PLOT: bool, if True do plots else do not
                FIBER: string, the fiber type (i.e. AB or A or B or C)
                IC_HC_N_ORD_FINAL: int, the order to which the solution is
                                   calculated
                IC_WAVE_IDRIFT_NOISE: float, the noise used in drift calculation
                IC_WAVE_IDRIFT_BOXSIZE: int, the size around a saturated pixel
                                        to count as bad
                IC_WAVE_IDRIFT_MAXFLUX: int, the maximum flux for a good
                                        (unsaturated) pixel
                IC_WAVE_IDRIFT_RV_CUT: float, the rv cut above which rv from
                                       orders are not used
                QC_WAVE_IDRIFT_NBORDEROUT: int, the maximum number of orders to
                                           remove from RV calculation
                QC_WAVE_IDRIFT_RV_MAX: float, the maximum allowed drift (in m/s)

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            HCDATA: numpy array (2D), the image data
            HCHDR: dictionary, the header dictionary for HCDATA

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                DRIFT_REF: string, the filename of the reference data
                DRIFT_RV: float, the mean instrumental RV
                DRIFT_NBCOS: int, the number of cosmic pixels found
                DRIFT_RFLUX: float, the mean flux ratio
                DRIFT_NBORDKILL: int, the number of orders removed
                DRIFT_NOISE: flat, the weighted mean uncertainty on the RV
    """

    func_name = __NAME__ + '.calculate_instrument_drift()'
    # get used constants from p
    n_order_final = p['IC_HC_N_ORD_FINAL']
    # ---------------------------------------------------------------------
    # actual data
    # ---------------------------------------------------------------------
    # copy hc data
    spe = np.array(loc['HCDATA'])
    # cut down data to correct orders
    spe = spe[:n_order_final]
    # ---------------------------------------------------------------------
    # Reference data
    # ---------------------------------------------------------------------
    # get reference hc data
    reffilename = spirouImage.ReadHcrefFile(p, loc['HCHDR'],
                                            return_filename=True)
    speref = spirouImage.ReadHcrefFile(p, loc['HCHDR'])
    # get wave image
    wout = spirouImage.GetWaveSolution(p, hdr=loc['HCHDR'], return_wavemap=True)
    _, waveref, wsource = wout

    # cut down data to correct orders
    speref = speref[:n_order_final]
    waveref = waveref[:n_order_final]
    # ---------------------------------------------------------------------
    # plot comparison between spe and speref
    if p['DRS_PLOT'] > 0:
        sPlt.wave_plot_instrument_drift(p, waveref, spe, speref)
    # ---------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ---------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dkwargs = dict(sigdet=p['IC_WAVE_IDRIFT_NOISE'],
                   size=p['IC_WAVE_IDRIFT_BOXSIZE'],
                   threshold=p['IC_WAVE_IDRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(speref, waveref, **dkwargs)
    # ---------------------------------------------------------------------
    # Compute photon noise uncertainty for data file
    # ---------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dkwargs = dict(sigdet=p['IC_WAVE_IDRIFT_NOISE'],
                   size=p['IC_DRIFT_BOXSIZE'],
                   threshold=p['IC_DRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsdata, wmeandata = spirouRV.DeltaVrms2D(spe, waveref, **dkwargs)
    # log RV uncertainty
    wmsg = 'On fiber {0} estimated RV uncertainy on spectrum is {1} m/s'
    wargs = [p['FIBER'], wmeandata]
    WLOG(p, 'info', wmsg.format(*wargs))
    # ---------------------------------------------------------------------
    # log unexpected RV uncertainty
    if wmeandata > p['IC_WAVE_IDRIFT_MAX_ERR']:
        wmsg1 = 'Unexpected RV uncertainty on spectrum. Check Flux.'
        wmsg2 = '\tmean > ic_wave_idrift_max_err  ({0:.3f} > {1:.3f})'
        wargs = [wmeandata, p['IC_WAVE_IDRIFT_MAX_ERR']]
        WLOG(p, 'error', [wmsg1, wmsg2.format(*wargs)])
    # ---------------------------------------------------------------------
    # Compute the correction of the cosmics and re-normalisation by
    #   comparison with the reference spectrum
    # ---------------------------------------------------------------------
    # log process
    wmsg = 'Normalizing spectrum and doing cosmic correction'
    WLOG(p, '', wmsg)
    # correction of the cosmics and renomalisation by comparison with
    #   the reference spectrum
    dkwargs = dict(threshold=p['IC_WAVE_IDRIFT_MAXFLUX'],
                   size=p['IC_WAVE_IDRIFT_BOXSIZE'],
                   cut=p['IC_WAVE_IDRIFT_CUT_E2DS'])
    spen, cfluxr, cpt = spirouRV.ReNormCosmic2D(p, speref, spe, **dkwargs)
    # ------------------------------------------------------------------
    # Calculate the RV drift
    # ------------------------------------------------------------------
    # log process
    wmsg = 'Normalizing spectrum and doing cosmic correction'
    WLOG(p, '', wmsg)
    # calculate the drift
    dkwargs = dict(sigdet=p['IC_WAVE_IDRIFT_NOISE'],
                   threshold=p['IC_WAVE_IDRIFT_MAXFLUX'],
                   size=p['IC_WAVE_IDRIFT_BOXSIZE'])
    rv = spirouRV.CalcRVdrift2D(speref, spen, waveref, **dkwargs)
    # ------------------------------------------------------------------
    # Calculate RV properties
    # ------------------------------------------------------------------
    # calculate mean cosmic normalised flux
    meancfluxr = np.mean(cfluxr)
    # calculate the weighted mean radial velocity
    # Question: why is this squared here but not in cal_DRIFT_E2DS??
    wref = 1.0 / dvrmsref ** 2
    meanrv = -1.0 * np.nansum(rv * wref) / np.nansum(wref)
    # calculate residual
    residual = np.abs(rv - meanrv)
    # get all those rv values less than ic_wave_idrift_rv_cut
    norm = np.sqrt(dvrmsref ** 2 + dvrmsdata ** 2)
    cond = (residual / norm) > p['IC_WAVE_IDRIFT_RV_CUT']
    # recalculate the weighted mean radial velocity
    meanrv2 = -1.0 * np.nansum(rv[cond] / wref[cond]) / np.nansum(wref[cond])
    # keep the number of orders used
    nborderout = np.nansum(cond)
    # ------------------------------------------------------------------
    # Quality control checks
    # ------------------------------------------------------------------
    # log removal of orders from RV calculation
    if nborderout > 0:
        wmsg = 'On fiber {0} discarding {0} order(s) for drift computation'
        WLOG(p, 'info', wmsg.format(nborderout))
    # log the rv properties
    wmsg = ('On fiber {0}\tDrift: {1:.3f} m/s - Cosmic found: {2} - '
            'Flux ration: {3:.3f}')
    wargs = [p['FIBER'], meanrv2, cpt, meancfluxr]
    WLOG(p, 'info', wmsg.format(*wargs))
    # log warning about number of orders removed and meanrv value
    if nborderout > p['QC_WAVE_IDRIFT_NBORDEROUT']:
        wmsg1 = 'Abnormal drift compared with previous calibration'
        wargs = [nborderout, p['QC_WAVE_IDRIFT_NBORDEROUT']]
        wmsg2 = ('\tnumber of RV orders removed > max ({0} > {1})'
                 ''.format(*wargs))
        WLOG(p, 'warning', [wmsg1, wmsg2])
    if meanrv2 > p['QC_WAVE_IDRIFT_RV_MAX']:
        wmsg1 = 'Abnormal drift compared with previous calibration'
        wargs = [meanrv2, p['QC_WAVE_IDRIFT_RV_MAX']]
        wmsg2 = '\tcalculated drift > max ({0} > {1})'.format(*wargs)
        WLOG(p, 'warning', [wmsg1, wmsg2])
    # add to loc
    loc['DRIFT_REF'] = reffilename
    loc['DRIFT_RV'] = meanrv2
    loc['DRIFT_NBCOS'] = cpt
    loc['DRIFT_RFLUX'] = meancfluxr
    loc['DRIFT_NBORDKILL'] = nborderout
    loc['DRIFT_NOISE'] = wmeandata
    # add source
    sources = ['DRIFT_REF', 'DRIFT_RV', 'DRIFT_NBCOS', 'DRIFT_RFLUX',
               'DRIFT_NBORDKILL', 'DRIFT_NOISE']
    loc.set_sources(sources, func_name)
    # return loc
    return loc


def fp_wavelength_sol(p, loc, mode='new'):
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

            IC_FP_THRESHOLD: float, defines threshold for detecting FP lines

            IC_FP_SIZE: int, defines size of region where each line is fitted

            IC_FP_DOPD0: float, initial value of FP effective cavity width

            IC_FP_FIT_DEGREE: int, degree of polynomial fit

            log_opt: string, log option, normally the program name

    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            FP_DATA: the FP e2ds data
            LITTROW_EXTRAP_SOL_1: the wavelength solution derived from the HC
                                  and Littrow-constrained
            ALL_LINES: list of numpy arrays, length = number of orders
                       each numpy array contains gaussian parameters
                       for each found line in that order
            BLAZE: numpy array (2D), the blaze data

    :param mode: string, either 'old' or 'new' - passed to find_fp_lines to
                 decide which way lines are found

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
    func_name = __NAME__ + '.fp_wavelength_sol()'
    # get parameters from p
    n_init = p['IC_FP_N_ORD_START']
    n_fin = p['IC_FP_N_ORD_FINAL']
    size = p['IC_FP_SIZE']
    threshold = p['IC_FP_THRESHOLD']
    dopd0 = p['IC_FP_DOPD0']
    fit_deg = p['IC_FP_FIT_DEGREE']
    # get parameters from loc
    fp_data = loc['FPDATA']
    all_lines_2 = loc['ALL_LINES_2']
    # set up storage
    llpos_all, xxpos_all, ampl_all = [], [], []
    m_fp_all, weight_bl_all, order_rec_all, dopd_all = [], [], [], []
    # loop around the orders from FP start order to FP end order
    for order_num in range(n_init, n_fin):
        # normalize the order
        miny, maxy = spirouBACK.BoxSmoothedMinMax(fp_data[order_num], 2 * size)
        fp_data_c = (fp_data[order_num] - miny) / (maxy - miny)
        # find all peaks in the order
        pos = spirouLOCOR.FindPosCentCol(fp_data_c, threshold)
        # remove first and last peaks to avoid edge effects
        pos = np.array(pos[1:-1])
        # log number of identified lines per order
        wmsg = 'On order {0:2}, {1:2} lines identified'
        wargs = [order_num, len(pos)]
        WLOG(p, '', wmsg.format(*wargs))
        # find the fp lines
        find_data = find_fp_lines(p, loc, pos, size, order_num, mode)
        # add to storage
        if order_num != n_init:
            # correct for large jumps
            find_data = correct_for_large_fp_jumps(p, order_num, find_data,
                                                   dopd_all)
        # add to storage
        llpos_all += list(find_data['llpos'])
        xxpos_all += list(find_data['xxpos'])
        ampl_all += list(find_data['ampl'])
        m_fp_all += list(find_data['m_fp'])
        weight_bl_all += list(find_data['weight_bl'])
        order_rec_all += list(find_data['order_rec'])
        # difference in cavity width converted to microns
        dopd_all += list((find_data['dopd_t'] - dopd0) * 1.e-3)

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
    # return loc
    return loc


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
                print('no overlap for order ' + str(order_num))
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


# =============================================================================
# New functions from Etienne
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


# def fit_gaussian_triplets(p, loc):
#     """
#     Fits the Gaussian peaks with sigma clipping
#
#     fits a second-order xpix vs wavelength polynomial and test it against
#     all other fitted lines along the order we keep track of the best fit for
#     the order, i.e., the fit that provides a solution with the largest number
#     of lines within +-500 m/s
#
#     We then assume that the fit is fine, we keep the lines that match the
#     "best fit" and we move to the next order.
#
#     Once we have "valid" lines for most/all orders, we attempt to fit a
#     5th order polynomial of the xpix vs lambda for all orders.
#     The coefficient of the fit must be continuous from one order to the next
#
#     we perform the fit twice, once to get a coarse solution, once to refine
#     as we will trim some variables, we define them on each loop
#     not 100% elegant, but who cares, it takes 5µs ...
#
#     :param p:
#     :param loc:
#     :return:
#     """
#
#     # get constants from p
#     nmax_bright = p['HC_NMAX_BRIGHT']
#     n_iterations = p['HC_NITER_FIT_TRIPLET']
#     cat_guess_dist = p['HC_MAX_DV_CAT_GUESS']
#     triplet_deg = p['HC_TFIT_DEG']
#     cut_fit_threshold = p['HC_TFIT_CUT_THRES']
#     minimum_number_of_lines = p['HC_TFIT_MIN_NUM_LINES']
#     minimum_total_number_of_lines = p['HC_TFIT_MIN_TOT_LINES']
#     order_fit_continuity = p['HC_TFIT_ORDER_FIT_CONTINUITY']
#     sigma_clip_num = p['HC_TFIT_SIGCLIP_NUM']
#     sigma_clip_threshold = p['HC_TFIT_SIGCLIP_THRES']
#     # get data from loc
#     wave_ll, amp_ll = loc['LL_LINE'], loc['AMPL_LINE']
#     poly_wave_sol = loc['WAVEPARAMS']
#
#     # get dimensions
#     nbo, nbpix = loc['NBO'], loc['NBPIX']
#
#     # ------------------------------------------------------------------
#     # triplet loop
#     # TODO: Move loop out of function
#     # set up storage
#     wave_catalog = []
#     amp_catalog = []
#     wave_map2 = np.zeros((nbo, nbpix))
#     sig = np.nan
#     # get coefficients
#     xgau = np.array(loc['XGAU_INI'])
#     orders = np.array(loc['ORD_INI'])
#     gauss_rms_dev = np.array(loc['GAUSS_RMS_DEV_INI'])
#     ew = np.array(loc['EW_INI'])
#     peak2 = np.array(loc['PEAK_INI'])
#     dv = np.array([])
#
#     for sol_iteration in range(n_iterations):
#         # log progress
#         # TODO Move log progress out of function
#         wmsg = 'Fit Triplet {0} of {1}'
#         WLOG(p, 'info', wmsg.format(sol_iteration + 1, n_iterations))
#         # get coefficients
#         xgau = np.array(loc['XGAU_INI'])
#         orders = np.array(loc['ORD_INI'])
#         gauss_rms_dev = np.array(loc['GAUSS_RMS_DEV_INI'])
#         ew = np.array(loc['EW_INI'])
#         peak = np.array(loc['PEAK_INI'])
#         # get peak again for saving (to make sure nothing goes wrong
#         #     in selection)
#         peak2 = np.array(loc['PEAK_INI'])
#         # --------------------------------------------------------------
#         # find the brightest lines for each order, only those lines will
#         #     be used to derive the first estimates of the per-order fit
#         # ------------------------------------------------------------------
#         brightest_lines = np.zeros(len(xgau), dtype=bool)
#         # loop around order
#         for order_num in set(orders):
#             # find all order_nums that belong to this order
#             good = orders == order_num
#             # get the peaks for this order
#             order_peaks = peak[good]
#             # we may have fewer lines within the order than nmax_bright
#             if np.nansum(good) <= nmax_bright:
#                 nmax = np.nansum(good) - 1
#             else:
#                 nmax = nmax_bright
#             # Find the "nmax" brightest peaks
#             smallest_peak = np.sort(order_peaks)[::-1][nmax]
#             good &= (peak > smallest_peak)
#             # apply good mask to brightest_lines storage
#             brightest_lines[good] = True
#         # ------------------------------------------------------------------
#         # Calculate wave solution at each x gaussian center
#         # ------------------------------------------------------------------
#         ini_wave_sol = np.zeros_like(xgau)
#         # get wave solution for these xgau values
#         for order_num in set(orders):
#             # find all order_nums that belong to this order
#             good = orders == order_num
#             # get the xgau for this order
#             xgau_order = xgau[good]
#             # get wave solution for this order
#             pargs = poly_wave_sol[order_num][::-1], xgau_order
#             wave_sol_order = np.polyval(*pargs)
#             # pipe wave solution for order into full wave_sol
#             ini_wave_sol[good] = wave_sol_order
#         # ------------------------------------------------------------------
#         # match gaussian peaks
#         # ------------------------------------------------------------------
#         # keep track of the velocity offset between predicted and observed
#         #    line centers
#         dv = np.repeat(np.nan, len(ini_wave_sol))
#         # wavelength given in the catalog for the matched line
#         wave_catalog = np.repeat(np.nan, len(ini_wave_sol))
#         # amplitude given in the catolog for the matched lines
#         amp_catalog = np.zeros(len(ini_wave_sol))
#         # loop around all lines in ini_wave_sol
#         for w_it, wave0 in enumerate(ini_wave_sol):
#             # find closest catalog line to the line considered
#             id_match = np.argmin(np.abs(wave_ll - wave0))
#             # find distance between catalog and ini solution  in m/s
#             distv = ((wave_ll[id_match] / wave0) - 1) * speed_of_light_ms
#             # check that distance is below threshold
#             if np.abs(distv) < cat_guess_dist:
#                 wave_catalog[w_it] = wave_ll[id_match]
#                 amp_catalog[w_it] = amp_ll[id_match]
#                 dv[w_it] = distv
#
#         # ------------------------------------------------------------------
#         # loop through orders and reject bright lines not within
#         #     +- HC_TFIT_DVCUT km/s histogram peak
#         # ------------------------------------------------------------------
#
#         # width in dv [km/s] - though used for number of bins?
#         # TODO: Question: Why km/s --> number
#         nbins = 2 * p['HC_MAX_DV_CAT_GUESS'] // 1000
#         # loop around all order
#         for order_num in set(orders):
#             # get the good pixels in this order
#             good = (orders == order_num) & (np.isfinite(dv))
#             # get histogram of points for this order
#             histval, histcenters = np.histogram(dv[good], bins=nbins)
#             # get the center of the distribution
#             dv_cen = histcenters[np.argmax(histval)]
#             # define a mask to remove points away from center of histogram
#             mask = (np.abs(dv-dv_cen) > p['HC_TFIT_DVCUT_ORDER']) & good
#             # apply mask to dv and to brightest lines
#             dv[mask] = np.nan
#             brightest_lines[mask] = False
#
#         # re-get the histogram of points for whole image
#         histval, histcenters = np.histogram(dv[np.isfinite(dv)], bins=nbins)
#         # re-find the center of the distribution
#         dv_cen = histcenters[np.argmax(histval)]
#         # re-define the mask to remove poitns away from center of histogram
#         mask = (np.abs(dv-dv_cen) > p['HC_TFIT_DVCUT_ALL'])
#         # re-apply mask to dv and to brightest lines
#         dv[mask] = np.nan
#         brightest_lines[mask] = False
#
#         # ------------------------------------------------------------------
#         # Find best trio of lines
#         # ------------------------------------------------------------------
#         for order_num in set(orders):
#             # find this order's lines
#             good = orders == order_num
#             # find all usable lines in this order
#             good_all = good & (np.isfinite(wave_catalog))
#             # good_all = good & (np.isfinite(dv))
#             # find all bright usable lines in this order
#             good_bright = good_all & brightest_lines
#             # get the positions of lines
#             pos_bright = np.where(good_bright)[0]
#             pos = np.where(good)[0]
#             # get number of good_bright
#             num_gb = int(np.nansum(good_bright))
#             bestn = 0
#             best_coeffs = np.zeros(triplet_deg + 1)
#             # get the indices of the triplets of bright lines
#             indices = itertools.combinations(range(num_gb), 3)
#             # loop around triplets
#             for index in indices:
#                 # get this iterations positions
#                 pos_it = pos_bright[np.array(index)]
#                 # get the x values for this iterations position
#                 xx = xgau[pos_it]
#                 # get the y values for this iterations position
#                 yy = wave_catalog[pos_it]
#                 # fit this position's lines and take it as the best-guess
#                 #    solution
#                 coeffs = nanpolyfit(xx, yy, triplet_deg)
#                 # extrapolate out over all lines
#                 fit_all = np.polyval(coeffs, xgau[good_all])
#                 # work out the error in velocity
#                 ev = ((wave_catalog[good_all] / fit_all) - 1) * speed_of_light
#                 # work out the number of lines to keep
#                 nkeep = np.nansum(np.abs(ev) < cut_fit_threshold)
#                 # if number of lines to keep largest seen --> store
#                 if nkeep > bestn:
#                     bestn = nkeep
#                     best_coeffs = np.array(coeffs)
#             # Log the total number of valid lines found
#             wmsg = '\tOrder {0}: Number of valid lines = {1} / {2}'
#             wargs = [order_num, bestn, np.nansum(good_all)]
#             WLOG(p, '', wmsg.format(*wargs))
#             # if we have the minimum number of lines check that we satisfy
#             #   the cut_fit_threshold for all good lines and reject outliers
#             if bestn >= minimum_number_of_lines:
#                 # extrapolate out best fit coefficients over all lines in
#                 #    this order
#                 fit_best = np.polyval(best_coeffs, xgau[good])
#                 # work out the error in velocity
#                 ev = ((wave_catalog[good] / fit_best) - 1) * speed_of_light
#                 abs_ev = np.abs(ev)
#                 # if max error in velocity greater than threshold, remove
#                 #    those greater than cut_fit_threshold
#                 if np.nanmax(abs_ev) > cut_fit_threshold:
#                     # get outliers
#                     outliers = pos[abs_ev > cut_fit_threshold]
#                     # set outliers to NaN in wave catalog
#                     wave_catalog[outliers] = np.nan
#                     # set dv of outliers to NaN
#                     dv[outliers] = np.nan
#             # else set everything to NaN
#             else:
#                 wave_catalog[good] = np.nan
#                 dv[good] = np.nan
#
#         # ------------------------------------------------------------------
#         # Plot wave catalogue all lines and brightest lines
#         # ------------------------------------------------------------------
#         if p['DRS_PLOT']:
#             pargs = [wave_catalog, dv, brightest_lines, sol_iteration]
#             sPlt.wave_ea_plot_wave_cat_all_and_brightest(p, *pargs)
#
#         # ------------------------------------------------------------------
#         # Keep only wave_catalog where values are finite
#         # -----------------------------------------------------------------
#         # create mask
#         good = np.isfinite(wave_catalog)
#         # apply mask
#         wave_catalog = wave_catalog[good]
#         amp_catalog = amp_catalog[good]
#         xgau = xgau[good]
#         orders = orders[good]
#         dv = dv[good]
#         ew = ew[good]
#         gauss_rms_dev = gauss_rms_dev[good]
#         peak2 = peak2[good]
#
#         # test save pre-sig-clip arrays to go into cal_wave
#         # create mask
#         good = np.isfinite(wave_catalog)
#         # apply mask
#         wave_catalog_0 = wave_catalog[good]
#         amp_catalog_0 = amp_catalog[good]
#         xgau_0 = xgau[good]
#         orders_0 = orders[good]
#         dv_0 = dv[good]
#         ew_0 = ew[good]
#         gauss_rms_dev_0 = gauss_rms_dev[good]
#         peak2_0 = peak2[good]
#
#
#         # ------------------------------------------------------------------
#         # Quality check on the total number of lines found
#         # ------------------------------------------------------------------
#         if np.nansum(good) < minimum_total_number_of_lines:
#             emsg1 = 'Insufficient number of lines found.'
#             emsg2 = '\t Found = {0}  Required = {1}'
#             eargs = [np.nansum(good), minimum_total_number_of_lines]
#             WLOG(p, 'error', [emsg1, emsg2.format(*eargs)])
#
#         # ------------------------------------------------------------------
#         # Linear model slice generation
#         # ------------------------------------------------------------------
#         # storage for the linear model slice
#         lin_mod_slice = np.zeros((len(xgau), np.nansum(order_fit_continuity)))
#
#         # construct the unit vectors for wavelength model
#         # loop around order fit continuity values
#         ii = 0
#         for expo_xpix in range(len(order_fit_continuity)):
#             # loop around orders
#             for expo_order in range(order_fit_continuity[expo_xpix]):
#                 part1 = orders ** expo_order
#                 part2 = np.array(xgau) ** expo_xpix
#                 lin_mod_slice[:, ii] = part1 * part2
#                 # iterate
#                 ii += 1
#
#         # ------------------------------------------------------------------
#         # Sigma clipping
#         # ------------------------------------------------------------------
#         # storage for arrays
#         recon0 = np.zeros_like(wave_catalog)
#         amps0 = np.zeros(np.nansum(order_fit_continuity))
#
#         # Loop sigma_clip_num times for sigma clipping and numerical
#         #    convergence. In most cases ~10 iterations would be fine but this
#         #    is fast
#         for sigma_it in range(sigma_clip_num):
#             # calculate the linear minimization
#             largs = [wave_catalog - recon0, lin_mod_slice]
#             amps, recon = spirouMath.linear_minimization(*largs)
#             # add the amps and recon to new storage
#             amps0 = amps0 + amps
#             recon0 = recon0 + recon
#             # loop around the amplitudes and normalise
#             for a_it in range(len(amps0)):
#                 # work out the residuals
#                 res = (wave_catalog - recon0)
#                 # work out the sum of residuals
#                 sum_r = np.nansum(res * lin_mod_slice[:, a_it])
#                 sum_l2 = np.nansum(lin_mod_slice[:, a_it] ** 2)
#                 # normalise by sum squared
#                 ampsx = sum_r / sum_l2
#                 # add this contribution on
#                 amps0[a_it] += ampsx
#                 recon0 += (ampsx * lin_mod_slice[:, a_it])
#             # recalculate dv [in km/s]
#             dv = ((wave_catalog / recon0) - 1) * speed_of_light
#             # calculate the standard deviation
#             sig = np.std(dv)
#             absdev = np.abs(dv / sig)
#             # Sigma clip those above sigma_clip_threshold
#             if np.max(absdev) > sigma_clip_threshold:
#                 # log sigma clipping
#                 wmsg = '\tSigma-clipping at (>{0}) --> max(sig)={1:.5f} sigma'
#                 wargs = [sigma_clip_threshold, np.max(absdev)]
#                 WLOG(p, '', wmsg.format(*wargs))
#                 # mask for sigma clip
#                 sig_mask = absdev < sigma_clip_threshold
#                 # apply mask
#                 recon0 = recon0[sig_mask]
#                 lin_mod_slice = lin_mod_slice[sig_mask]
#                 wave_catalog = wave_catalog[sig_mask]
#                 amp_catalog = amp_catalog[sig_mask]
#                 xgau = xgau[sig_mask]
#                 orders = orders[sig_mask]
#                 dv = dv[sig_mask]
#                 ew = ew[sig_mask]
#                 gauss_rms_dev = gauss_rms_dev[sig_mask]
#                 peak2 = peak2[sig_mask]
#             # Log stats
#             sig1 = sig * 1000 / np.sqrt(len(wave_catalog))
#             wmsg = '\t{0} | RMS={1:.5f} km/s sig={2:.5f} m/s n={3}'
#             wargs = [sigma_it, sig, sig1, len(wave_catalog)]
#             WLOG(p, 'info', wmsg.format(*wargs))
#
#         # ------------------------------------------------------------------
#         # Plot wave catalogue all lines and brightest lines
#         # ------------------------------------------------------------------
#         if p['DRS_PLOT']:
#             pargs = [orders, wave_catalog, recon0, gauss_rms_dev, xgau, ew,
#                      sol_iteration]
#             sPlt.wave_ea_plot_tfit_grid(p, *pargs)
#
#         # ------------------------------------------------------------------
#         # Construct wave map
#         # ------------------------------------------------------------------
#         xpix = np.arange(nbpix)
#         wave_map2 = np.zeros((nbo, nbpix))
#         poly_wave_sol = np.zeros_like(loc['WAVEPARAMS'])
#
#         # loop around the orders
#         for order_num in range(nbo):
#             ii = 0
#             for expo_xpix in range(len(order_fit_continuity)):
#                 for expo_order in range(order_fit_continuity[expo_xpix]):
#                     # calculate new coefficient
#                     new_coeff = (order_num ** expo_order) * amps0[ii]
#                     # add to poly wave solution
#                     poly_wave_sol[order_num, expo_xpix] += new_coeff
#                     # iterate
#                     ii += 1
#             # add to wave_map2
#             wcoeffs = poly_wave_sol[order_num, :][::-1]
#             wave_map2[order_num, :] = np.polyval(wcoeffs, xpix)
#
#     # save parameters to loc
#     loc['WAVE_CATALOG'] = wave_catalog
#     loc['AMP_CATALOG'] = amp_catalog
#     loc['SIG'] = sig
#     loc['SIG1'] = sig * 1000 / np.sqrt(len(wave_catalog))
#     loc['POLY_WAVE_SOL'] = poly_wave_sol
#     loc['WAVE_MAP2'] = wave_map2
#
#     loc['XGAU_T'] = xgau
#     loc['ORD_T'] = orders
#     loc['GAUSS_RMS_DEV_T'] = gauss_rms_dev
#     loc['DV_T'] = dv
#     loc['EW_T'] = ew
#     loc['PEAK_T'] = peak2
#
#     #save test
#     loc['WAVE_CATALOG_0'] = wave_catalog_0
#     loc['AMP_CATALOG_0'] = amp_catalog_0
#     loc['XGAU_T_0'] = xgau_0
#     loc['ORD_T_0'] = orders_0
#     loc['GAUSS_RMS_DEV_T_0'] = gauss_rms_dev_0
#     loc['DV_T_0'] = dv_0
#     loc['EW_T_0'] = ew_0
#     loc['PEAK_T_0'] = peak2_0
#
#
#     # return loc
#     return loc


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
def find_fp_lines(p, loc, pos, size, order_num, mode):
    # get constants from p
    dopd0 = p['IC_FP_DOPD0']
    # get parameters from loc
    fp_data = loc['FPDATA']
    fp_ll_init = loc['LITTROW_EXTRAP_SOL_1']
    blaze = loc['BLAZE']
    # define storage
    floc = OrderedDict()
    floc['llpos'] = np.zeros_like(pos)
    floc['xxpos'] = np.zeros_like(pos)
    floc['m_fp'] = np.zeros_like(pos)
    floc['dopd_t'] = np.zeros_like(pos)
    floc['ampl'] = np.zeros_like(pos)
    floc['weight_bl'] = np.zeros_like(pos)
    floc['order_rec'] = np.ones_like(pos) * 999
    # loop over all the lines in the order
    for it in np.arange(len(pos)):
        # get the pixel position of the line
        xpos = int(pos[it])
        # define the range over which to fit the line by a gaussian
        xx = np.arange(xpos - size, xpos + size)
        # do the gaussian fit
        fll_it = fp_ll_init[order_num, xpos - size:xpos + size]
        fdata_it = fp_data[order_num, xpos - size:xpos + size]
        weight_it = np.ones(2 * size)
        # TODO: This will crash "Missing weight parameter"
        # TODO:   fit_emi_line(p, sll, sxpos, sdata, weight, mode=0)
        gparams = spirouTHORCA.fit_emi_line(fll_it, xx, fdata_it, weight_it,
                                            mode=mode)
        # quality check on the fit
        #    x value should be close to initial measured position
        if abs(gparams[5] - pos[it]) > 1.:
            # refit in smaller region around poorly fitted line
            size2 = 2
            # redo the gaussian fit
            fll_it = fp_ll_init[order_num, xpos - size2:xpos + size2]
            fdata_it = fp_data[order_num, xpos - size2:xpos + size2]
            weight_it = np.ones(2 * size2)
            # TODO: This will crash "Missing weight parameter"
            # TODO:   fit_emi_line(p, sll, sxpos, sdata, weight, mode=0)
            gparams = spirouTHORCA.fit_emi_line(fll_it, xx, fdata_it, weight_it,
                                                mode=mode)
        # store the initial wavelength of the line
        floc['llpos'][it] = gparams[0]
        # store the pixel position of the line
        floc['xxpos'][it] = gparams[5]
        # store the amplitude of the line
        floc['ampl'][it] = gparams[7]
        # store the value of the blaze at the pixel position of the line
        floc['weight_bl'][it] = blaze[order_num, int(np.round(gparams[5]))]
        # store the order number
        floc['order_rec'][it] = order_num
        # determine the line number
        if it == 0:
            # line number for first line of the order (by FP equation)
            floc['m_fp'][it] = int(dopd0 / gparams[0])  # + 0.5)
        else:
            # successive line numbers (assuming no gap)
            floc['m_fp'][it] = floc['m_fp'][it - 1] - 1
        # determination of observed effective cavity width
        floc['dopd_t'][it] = floc['m_fp'][it] * gparams[0]
    # return data dictionary
    return floc


def correct_for_large_fp_jumps(p, order_num, find_data, dopd_all):
    # get constants from p
    dopd0 = p['IC_FP_DOPD0']
    fp_large_jump = p['IC_FP_LARGE_JUMP']
    # get dopd_t from find lines data
    dopd_t = find_data['dopd_t']
    # check for one line number difference between orders
    if ((dopd_t[0] - dopd0) * 1.e-3 - dopd_all[-1]) > fp_large_jump:
        # print warning message
        wmsg = 'Jump larger than +0.7 on order {0:2}'
        wargs = [order_num]
        WLOG(p, 'warning', wmsg.format(*wargs))
        # shift line numbers one down
        find_data['m_fp'] = find_data['m_fp'] - 1.
        # recalculate cavity width with corrected line numbers
        find_data['dopd_t'] = find_data['m_fp'] * find_data['llpos']
    elif ((dopd_t[0] - dopd0) * 1.e-3 - dopd_all[-1]) < -fp_large_jump:
        # print warning message
        wmsg = 'Jump larger than -0.7 on order {0:2}'
        wargs = [order_num]
        WLOG(p, 'warning', wmsg.format(*wargs))
        # shift line numbers one up
        find_data['m_fp'] = find_data['m_fp'] + 1.
        # recalculate cavity width with corrected line numbers
        find_data['dopd_t'] = find_data['m_fp'] * find_data['llpos']
    # return the recalculated cavity width
    return find_data


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


###########################################################
# TESTS
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
            mask = (np.abs(dv-dv_cen) > p['HC_TFIT_DVCUT_ORDER']) & good
            # apply mask to dv and to brightest lines
            dv[mask] = np.nan
            brightest_lines[mask] = False

        # re-get the histogram of points for whole image
        histval, histcenters = np.histogram(dv[np.isfinite(dv)], bins=nbins)
        # re-find the center of the distribution
        dv_cen = histcenters[np.argmax(histval)]
        # re-define the mask to remove poitns away from center of histogram
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

        # test save pre-sig-clip arrays to go into cal_wave
        # create mask
        good = np.isfinite(wave_catalog)
        # apply mask
        wave_catalog_0 = wave_catalog[good]
        amp_catalog_0 = amp_catalog[good]
        xgau_0 = xgau[good]
        orders_0 = orders[good]
        dv_0 = dv[good]
        ew_0 = ew[good]
        gauss_rms_dev_0 = gauss_rms_dev[good]
        peak2_0 = peak2[good]

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
        # TODO ----------------------------------------------------------------
        wave_map3 = np.zeros((nbo, nbpix))
        poly_wave_sol3 = np.zeros_like(loc['WAVEPARAMS'])
        wave_mapc = np.zeros((nbo, nbpix))
        poly_wave_solc = np.zeros_like(loc['WAVEPARAMS'])
        for order_num in range(nbo):
            order_mask = orders == order_num
            if np.nansum(order_mask) == 0:
                print('No values found for order {0}'.format(order_num))
                continue

            ppx = xgau[order_mask]
            ppy = wave_catalog[order_mask]
            wcoeffs = nanpolyfit(ppx, ppy, loc['WAVEPARAMS'].shape[1]-1)[::-1]
            poly_wave_sol3[order_num, :] = wcoeffs
            wave_map3[order_num, :] = np.polyval(wcoeffs[::-1], xpix)

            ppx2 = xgau[order_mask]
            ppy2 = wave_catalog[order_mask]
            cheb_coeffs = chebyshev.chebfit(ppx2, ppy2, 4)
            poly_wave_solc[order_num, :] = cheb_coeffs

            ppx3 = np.arange(loc['NBPIX'])
            wave_mapc[order_num, :] = chebyshev.chebval(ppx3, cheb_coeffs)
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

        loc2 = spirouConfig.ParamDict()
        for key in loc:
            loc2[key] = loc[key]
        loc2['POLY_WAVE_SOL'] = poly_wave_sol3
        loc2['WAVE_MAP2'] = wave_map3

        do_stuff(p, loc)
        do_stuff(p, loc2)

    loc['POLY_WAVE_SOL3'] = poly_wave_sol3
    loc['WAVE_MAP3'] = wave_map3

    loc['POLY_WAVE_SOL4'] = poly_wave_solc
    loc['WAVE_MAP4'] = wave_mapc

    #loc['POLY_WAVE_SOL4'][-1] = poly_wave_sol[-1]
    #loc['WAVE_MAP4'][-1] = wave_map3[-1]

    ppx4 = np.arange(loc['NBPIX'])
    loc['POLY_WAVE_SOL4'][-2] = chebyshev.chebfit(ppx4, loc['WAVE_MAP2'][-2], 4)
    loc['WAVE_MAP4'][-2] = chebyshev.chebval(ppx4, loc['POLY_WAVE_SOL4'][-2])

    loc['POLY_WAVE_SOL4'][-1] = chebyshev.chebfit(ppx4, loc['WAVE_MAP2'][-1], 4)
    loc['WAVE_MAP4'][-1] = chebyshev.chebval(ppx4, loc['POLY_WAVE_SOL4'][-1])

    loc['POLY_WAVE_SOL5'] = poly_wave_sol
    loc['WAVE_MAP5'] = wave_map2

    loc['POLY_WAVE_SOL5'][0] = poly_wave_sol3[0]
    loc['WAVE_MAP5'][0] = wave_map3[0]

    # TODO ----------------------------------------------------------------
    # TODO: Remove above
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

    #save test
    loc['WAVE_CATALOG_0'] = wave_catalog_0
    loc['AMP_CATALOG_0'] = amp_catalog_0
    loc['XGAU_T_0'] = xgau_0
    loc['ORD_T_0'] = orders_0
    loc['GAUSS_RMS_DEV_T_0'] = gauss_rms_dev_0
    loc['DV_T_0'] = dv_0
    loc['EW_T_0'] = ew_0
    loc['PEAK_T_0'] = peak2_0

    loc['LIN_MOD_SLICE'] = lin_mod_slice
    loc['RECON0'] = recon0

    loc['POLY_WAVE_SOLC'] = poly_wave_solc
    loc['WAVE_MAPC'] = wave_mapc

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



def fit_fp_linmin(p, loc):
    """
    Fits the fp peaks with sigma clipping and linear minimization

    We attempt to fit a 5th order polynomial of the xpix vs lambda for all orders.
    The coefficient of the fit must be continuous from one order to the next

    we perform the fit twice, once to get a coarse solution, once to refine
    as we will trim some variables, we define them on each loop
    not 100% elegant, but who cares, it takes 5µs ...

    :param p: ParamDict - the constant parameter dictionary
    :param loc: ParamDict - the data parameter dictionary
    :return:
    """

    # get constants from p
    # nmax_bright = p['HC_NMAX_BRIGHT']
    # n_iterations = p['HC_NITER_FIT_TRIPLET']
    # cat_guess_dist = p['HC_MAX_DV_CAT_GUESS']
    # triplet_deg = p['HC_TFIT_DEG']
    # cut_fit_threshold = p['HC_TFIT_CUT_THRES']
    # minimum_number_of_lines = p['HC_TFIT_MIN_NUM_LINES']
    # minimum_total_number_of_lines = p['HC_TFIT_MIN_TOT_LINES']
    order_fit_continuity = p['HC_TFIT_ORDER_FIT_CONTINUITY']
    sigma_clip_num = p['HC_TFIT_SIGCLIP_NUM']
    sigma_clip_threshold = p['HC_TFIT_SIGCLIP_THRES']

    # get data from loc
    fp_ll = loc['FP_LL_NEW']
    fp_xx = loc['FP_XX_NEW']
    fp_ord = loc['FP_ORD_NEW']

    # get dimensions
    nbo, nbpix = loc['NBO'], loc['NBPIX']

    # ------------------------------------------------------------------
    # Linear model slice generation
    # ------------------------------------------------------------------
    # storage for the linear model slice
    lin_mod_slice = np.zeros((len(fp_xx), np.nansum(order_fit_continuity)))

    # construct the unit vectors for wavelength model
    # loop around order fit continuity values
    ii = 0
    for expo_xpix in range(len(order_fit_continuity)):
        # loop around orders
        for expo_order in range(order_fit_continuity[expo_xpix]):
            part1 = fp_ord ** expo_order
            part2 = np.array(fp_xx) ** expo_xpix
            lin_mod_slice[:, ii] = part1 * part2
            # iterate
            ii += 1

    # ------------------------------------------------------------------
    # Sigma clipping
    # ------------------------------------------------------------------
    # storage for arrays
    recon0 = np.zeros_like(fp_ll)
    amps0 = np.zeros(np.nansum(order_fit_continuity))

    # Loop sigma_clip_num times for sigma clipping and numerical
    #    convergence. In most cases ~10 iterations would be fine but this
    #    is fast
    for sigma_it in range(sigma_clip_num):
        # calculate the linear minimization
        largs = [fp_ll - recon0, lin_mod_slice]
        amps, recon = spirouMath.linear_minimization(*largs)
        # add the amps and recon to new storage
        amps0 = amps0 + amps
        recon0 = recon0 + recon
        # loop around the amplitudes and normalise
        for a_it in range(len(amps0)):
            # work out the residuals
            res = (fp_ll - recon0)
            # work out the sum of residuals
            sum_r = np.nansum(res * lin_mod_slice[:, a_it])
            sum_l2 = np.nansum(lin_mod_slice[:, a_it] ** 2)
            # normalise by sum squared
            ampsx = sum_r / sum_l2
            # add this contribution on
            amps0[a_it] += ampsx
            recon0 += (ampsx * lin_mod_slice[:, a_it])
        # recalculate dv [in km/s]
        dv = ((fp_ll / recon0) - 1) * speed_of_light
        # calculate the standard deviation
        sig = np.std(dv)
        absdev = np.abs(dv / sig)

        # initialize lists for saving
        recon0_aux = []
        lin_mod_slice_aux = []
        fp_ll_aux = []
        fp_xx_aux = []
        fp_ord_aux = []
        dv_aux = []

        # Sigma clip worst line per order
        for ord in set(fp_ord):
            # mask for order
            order_mask = fp_ord == ord
            # get abs dev for order
            absdev_ord = absdev[order_mask]
            # check if above threshold
            if np.max(absdev_ord) > sigma_clip_threshold:
                # create mask for worst line
                sig_mask = absdev_ord < np.max(absdev_ord)
                # apply mask
                recon0_aux.append(recon0[order_mask][sig_mask])
                lin_mod_slice_aux.append(lin_mod_slice[order_mask][sig_mask])
                fp_ll_aux.append(fp_ll[order_mask][sig_mask])
                fp_xx_aux.append(fp_xx[order_mask][sig_mask])
                fp_ord_aux.append(fp_ord[order_mask][sig_mask])
                dv_aux.append(dv[order_mask][sig_mask])
            # if all below threshold keep all
            else:
                recon0_aux.append(recon0[order_mask])
                lin_mod_slice_aux.append(lin_mod_slice[order_mask])
                fp_ll_aux.append(fp_ll[order_mask])
                fp_xx_aux.append(fp_xx[order_mask])
                fp_ord_aux.append(fp_ord[order_mask])
                dv_aux.append(dv[order_mask])
        # save aux lists to initial arrays
        fp_ord = np.concatenate(fp_ord_aux)
        recon0 = np.concatenate(recon0_aux)
        lin_mod_slice = np.concatenate(lin_mod_slice_aux)
        fp_ll = np.concatenate(fp_ll_aux)
        fp_xx = np.concatenate(fp_xx_aux)
        dv = np.concatenate(dv_aux)

        # Log stats
        sig1 = sig * 1000 / np.sqrt(len(fp_ll))
        wmsg = '\t{0} | RMS={1:.5f} km/s sig={2:.5f} m/s n={3}'
        wargs = [sigma_it, sig, sig1, len(fp_ll)]
        WLOG(p, '', wmsg.format(*wargs))

        # ------------------------------------------------------------------
        # Construct wave map
        # ------------------------------------------------------------------
        xpix = np.arange(nbpix)
        wave_map2 = np.zeros((nbo, nbpix))
        poly_wave_sol = np.zeros_like(loc['WAVEPARAMS'])

        # loop around the orders
        for order_num in range(nbo):
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

    # save parameters to loc
    loc['SIG'] = sig
    loc['SIG1'] = sig * 1000 / np.sqrt(len(fp_ll))
    loc['POLY_WAVE_SOL_FP'] = poly_wave_sol
    loc['WAVE_MAP_FP'] = wave_map2

    loc['FP_LL_NEW_T'] = fp_ll
    loc['FP_XX_NEW_T'] = fp_xx
    loc['FP_ORD_NEW_T'] = fp_ord
    loc['DV_T'] = dv

    loc['LIN_MOD_SLICE'] = lin_mod_slice
    loc['RECON0'] = recon0

    # return loc
    return loc

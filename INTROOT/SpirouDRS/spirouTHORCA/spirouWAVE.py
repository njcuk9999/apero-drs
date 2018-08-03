#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FP wavelength function

Created on 2017-12-19 at 16:20

@author: mhobson

"""
from __future__ import division
import numpy as np
import warnings

from SpirouDRS import spirouBACK
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouRV

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
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# Get plotting functions
sPlt = spirouCore.sPlt


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
    # get the wavelengths and parameters for the reference
    waveref, _ = spirouTHORCA.get_e2ds_ll(p, loc['HCHDR'], filename=reffilename)
    # cut down data to correct orders
    speref = speref[:n_order_final]
    waveref = waveref[:n_order_final]
    # ---------------------------------------------------------------------
    # plot comparison between spe and speref
    if p['DRS_PLOT']:
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
    WLOG('info', p['LOG_OPT'] + p['FIBER'], wmsg.format(*wargs))
    # ---------------------------------------------------------------------
    # log unexpected RV uncertainty
    if wmeandata > p['IC_WAVE_IDRIFT_MAX_ERR']:
        wmsg1 = 'Unexpected RV uncertainty on spectrum. Check Flux.'
        wmsg2 = '\tmean > ic_wave_idrift_max_err  ({0:.3f} > {1:.3f})'
        wargs = [wmeandata, p['IC_WAVE_IDRIFT_MAX_ERR']]
        WLOG('error', p['LOG_OPT'] + p['FIBER'], [wmsg1, wmsg2.format(*wargs)])
    # ---------------------------------------------------------------------
    # Compute the correction of the cosmics and re-normalisation by
    #   comparison with the reference spectrum
    # ---------------------------------------------------------------------
    # log process
    wmsg = 'Normalizing spectrum and doing cosmic correction'
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg)
    # correction of the cosmics and renomalisation by comparison with
    #   the reference spectrum
    dkwargs = dict(threshold=p['IC_WAVE_IDRIFT_MAXFLUX'],
                   size=p['IC_WAVE_IDRIFT_BOXSIZE'],
                   cut=p['IC_WAVE_IDRIFT_CUT_E2DS'])
    spen, cfluxr, cpt = spirouRV.ReNormCosmic2D(speref, spe, **dkwargs)
    # ------------------------------------------------------------------
    # Calculate the RV drift
    # ------------------------------------------------------------------
    # log process
    wmsg = 'Normalizing spectrum and doing cosmic correction'
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg)
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
    meanrv = -1.0 * np.sum(rv * wref) / np.sum(wref)
    # calculate residual
    residual = np.abs(rv - meanrv)
    # get all those rv values less than ic_wave_idrift_rv_cut
    norm = np.sqrt(dvrmsref ** 2 + dvrmsdata ** 2)
    cond = (residual / norm) > p['IC_WAVE_IDRIFT_RV_CUT']
    # recalculate the weighted mean radial velocity
    meanrv2 = -1.0 * np.sum(rv[cond]/ wref[cond]) / np.sum(wref[cond])
    # keep the number of orders used
    nborderout = np.sum(cond)
    # ------------------------------------------------------------------
    # Quality control checks
    # ------------------------------------------------------------------
    # log removal of orders from RV calculation
    if nborderout > 0:
        wmsg = 'On fiber {0} discarding {0} order(s) for drift computation'
        WLOG('info', p['LOG_OPT'] + p['FIBER'], wmsg.format(nborderout))
    # log the rv properties
    wmsg = ('On fiber {0}\tDrift: {1:.3f} m/s - Cosmic found: {2} - '
            'Flux ration: {3:.3f}')
    wargs = [p['FIBER'], meanrv2, cpt, meancfluxr]
    WLOG('info', p['LOG_OPT'] + p['FIBER'], wmsg.format(*wargs))
    # log warning about number of orders removed and meanrv value
    if nborderout > p['QC_WAVE_IDRIFT_NBORDEROUT']:
        wmsg1 = 'Abnormal drift compared with previous calibration'
        wargs = [nborderout, p['QC_WAVE_IDRIFT_NBORDEROUT']]
        wmsg2 = ('\tnumber of RV orders removed > max ({0} > {1})'
                 ''.format(*wargs))
        WLOG('warning', p['LOG_OPT'] + p['FIBER'], [wmsg1, wmsg2])
    if meanrv2 > p['QC_WAVE_IDRIFT_RV_MAX']:
        wmsg1 = 'Abnormal drift compared with previous calibration'
        wargs = [meanrv2, p['QC_WAVE_IDRIFT_RV_MAX']]
        wmsg2 = '\tcalculated drift > max ({0} > {1})'.format(*wargs)
        WLOG('warning', p['LOG_OPT'] + p['FIBER'], [wmsg1, wmsg2])
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
        WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
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
        coeffs = np.polyfit(m_fp_all, dopd_all, fit_deg, w=weight_bl_all)[::-1]
    spirouCore.WarnLog(w, funcname=func_name)
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
               'FP_DOPD_OFFSET_COEFF', 'FP_DOPD_OFFSET_FIT']
    loc.set_sources(sources, func_name)
    # return loc
    return loc


# =============================================================================
# Worker functions
# =============================================================================
def find_fp_lines(p, loc, pos, size, order_num, mode):
    # get constants from p
    dopd0 = p['IC_FP_DOPD0']
    # get parameters from loc
    fp_data = loc['FPDATA']
    FP_ll_init = loc['LITTROW_EXTRAP_SOL_1']
    blaze = loc['BLAZE']
    # define storage
    floc = dict()
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
        fll_it = FP_ll_init[order_num, xpos - size:xpos + size]
        fdata_it = fp_data[order_num, xpos - size:xpos + size]
        weight_it = np.ones(2 * size)
        gparams = spirouTHORCA.fit_emi_line(fll_it, xx, fdata_it, weight_it,
                                            mode=mode)
        # quality check on the fit
        #    x value should be close to initial measured position
        if abs(gparams[5] - pos[it]) > 1.:
            # refit in smaller region around poorly fitted line
            size2 = 2
            # redo the gaussian fit
            fll_it = FP_ll_init[order_num, xpos - size2:xpos + size2]
            fdata_it = fp_data[order_num, xpos - size2:xpos + size2]
            weight_it = np.ones(2 * size2)
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
            floc['m_fp'][it] = int(dopd0 / gparams[0])# + 0.5)
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
        WLOG('warning', p['LOG_OPT'], wmsg.format(*wargs))
        # shift line numbers one down
        find_data['m_fp'] = find_data['m_fp'] - 1.
        # recalculate cavity width with corrected line numbers
        find_data['dopd_t'] = find_data['m_fp'] * find_data['llpos']
    elif ((dopd_t[0] - dopd0) * 1.e-3 - dopd_all[-1]) < -fp_large_jump:
        # print warning message
        wmsg = 'Jump larger than -0.7 on order {0:2}'
        wargs = [order_num]
        WLOG('warning', p['LOG_OPT'], wmsg.format(*wargs))
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
    n_init_HC = p['IC_HC_N_ORD_START_2']
    n_fin_HC = p['IC_HC_N_ORD_FINAL_2']
    # insert FP lines into all_lines at the correct orders
    # define wavelength difference limit for keeping a line
    fp_cut = np.std(newll - llpos_all)
    for order_num in range(n_init, n_fin):
        if order_num < n_init_HC:
            # prepend zeros to all_lines if FP solution is fitted for
            #     bluer orders than HC was
            all_lines_2.insert(0, np.zeros((1, 8), dtype=float))
        elif order_num > n_fin_HC:
            # append zeros to all_lines if FP solution is fitted for
            #     redder orders than HC was
            all_lines_2.append(np.zeros((1, 8), dtype=float))
        for it in range(len(order_rec_all)):
            # find lines corresponding to order number
            if order_rec_all[it] == order_num:
                # check wavelength difference below limit
                if abs(newll[it] - llpos_all[it]) < fp_cut:
                    # put FP line data into an array
                    newdll = newll[it] - llpos_all[it]
                    FP_line = np.array([newll[it], 0.0, 0.0, newdll,
                                        0.0, xxpos_all[it], 0.0, ampl_all[it]])
                    FP_line = FP_line.reshape((1, 8))
                    # append FP line data to all_lines
                    torder = order_num
                    tvalues = [all_lines_2[torder], FP_line]
                    all_lines_2[torder] = np.concatenate(tvalues)
    # return all lines 2
    return all_lines_2

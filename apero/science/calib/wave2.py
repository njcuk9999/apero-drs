#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 

@author: 
"""
from astropy.table import Table
from astropy import constants as cc
from astropy import units as uu
import itertools
import numpy as np
import os
from typing import Union
import warnings
import copy

from apero import core
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_startup
from apero.io import drs_data
from apero.io import drs_table
from apero.io import drs_image
from apero.science import velocity
from apero.science.calib import general
from apero.science import extract
from apero.science.calib import flat_blaze

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.wave2.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value
# Get function string
display_func = drs_log.display_func


# =============================================================================
# Define line functions
# =============================================================================
def get_wave_lines(params, recipe, e2dsfile, wavemap, cavity_poly=None,
                     hclines=None, fplines=None, **kwargs):
    # set the function name
    func_name = display_func(params, 'get_master_lines', __NAME__)
    # get parameters from params and kwargs
    nsig_min = pcheck(params, 'WAVEREF_NSIG_MIN', 'nsig_min', kwargs, func_name)
    wmax = pcheck(params, 'WAVEREF_EDGE_WMAX', 'wmax', kwargs, func_name)
    hcboxsize = pcheck(params, 'WAVEREF_HC_BOXSIZE', 'hcboxsize', kwargs,
                       func_name)
    hcfibtypes = pcheck(params, 'WAVEREF_HC_FIBTYPES', 'hcfibtypes', kwargs,
                        func_name, mapf='list', dtype=str)
    fpfibtypes = pcheck(params, 'WAVEREF_FP_FIBTYPES', 'fpfibtypes', kwargs,
                        func_name, mapf='list', dtype=str)
    fitdeg = pcheck(params, 'WAVEREF_FITDEG', 'fitdeg', kwargs, func_name)
    fp_nlow = pcheck(params, 'WAVEREF_FP_NLOW', 'fp_nlow', kwargs,
                     func_name)
    fp_nhigh = pcheck(params, 'WAVEREF_FP_NHIGH', 'fp_nhigh', kwargs,
                      func_name)
    fp_inv_itr = pcheck(params, 'WAVEREF_FP_POLYINV', 'fp_inv_itr', kwargs,
                        func_name)
    iteration = kwargs.get('iteration', None)

    # ------------------------------------------------------------------
    # get psuedo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get the shape from the wavemap
    nbo, nbpix = wavemap.shape
    # get dprtype
    dprtype = e2dsfile.get_key('KW_DPRTYPE', dtype=str)
    # get fiber type
    fiber = e2dsfile.get_key('KW_FIBER', dtype=str)
    # get fiber type
    fibtype = pconst.FIBER_DPR_POS(dprtype, fiber)
    # set up the xpixels
    xpix = np.arange(nbpix)

    # ----------------------------------------------------------------------
    # get the lines for HC files from hclines input
    # ----------------------------------------------------------------------
    if hclines is not None:
        list_waves = hclines['WAVE_REF']
        list_orders = hclines['ORDER']
        list_pixels = hclines['PIXEL_REF']
        list_wfit = hclines['WFIT']
        peak_number = hclines['PEAK_NUMBER']

    # ----------------------------------------------------------------------
    # get the lines for HC files from fplines input
    # ----------------------------------------------------------------------
    elif fplines is not None:
        list_waves = fplines['WAVE_REF']
        list_orders = fplines['ORDER']
        list_pixels = fplines['PIXEL_REF']
        list_wfit = fplines['WFIT']
        peak_number = fplines['PEAK_NUMBER']

    # ----------------------------------------------------------------------
    # get the lines for HC files
    # ----------------------------------------------------------------------
    elif fibtype in hcfibtypes:
        # print progress Running get ref lines for HC
        WLOG(params, 'info', TextEntry('40-017-00049'))
        # load the line list
        wavell, ampll = drs_data.load_linelist(params, **kwargs)
        # storage for outputs
        list_waves, list_orders, list_pixels = [], [], []
        # loop around orders and get the lines that fall within each
        #    diffraction order
        for order_num in range(nbo):
            # we have a wavelength value, we get an approximate pixel
            # value by fitting wavelength to pixel
            owave = wavemap[order_num]
            with warnings.catch_warnings(record=True) as _:
                fit_reverse = np.polyfit(owave, xpix, fitdeg)
            # we find lines within the order
            good = (wavell > np.min(owave)) & (wavell < np.max(owave))
            # we check that there is at least 1 line and append our line list
            if np.sum(good) != 0:
                # get the pixels positions based on out owave fit
                pixfit = np.polyval(fit_reverse, wavell[good])
                # append lists
                list_waves += list(wavell[good])
                list_orders += list(np.repeat(order_num, np.sum(good)))
                list_pixels += list(pixfit)
        # make line lists np arrays
        list_waves = np.array(list_waves)
        list_orders = np.array(list_orders)
        list_pixels = np.array(list_pixels)
        # keep lines that are  not too close to image edge
        keep = (list_pixels > wmax) & (list_pixels < (nbpix - wmax))
        # apply to list arrays
        list_waves = list_waves[keep]
        list_orders = list_orders[keep]
        list_pixels = list_pixels[keep]
        # set wfit to a constant for HC
        list_wfit = np.repeat(hcboxsize, len(list_pixels))

        # just for the sake of consistency, we need to attribute a fractional
        # FP cavity number to HC peaks. This ensures that the table saved at
        # then end of this code has the same format as for FPs.
        peak_number = np.repeat(np.nan, len(list_pixels))

    # ----------------------------------------------------------------------
    # get the lines for FP files
    # ----------------------------------------------------------------------
    elif fibtype in fpfibtypes:
        # print progress Running get ref lines for FP
        WLOG(params, 'info', TextEntry('40-017-00050'))
        # ------------------------------------------------------------------
        # deal with getting cavity poly
        if cavity_poly is not None:
            cavity_length_poly = np.array(cavity_poly)
        else:
            # load the cavity polynomial from file
            _, fit_ll = drs_data.load_cavity_files(params)
            cavity_length_poly = fit_ll
        # ------------------------------------------------------------------
        # range of the N FP peaks
        nth_peak = np.arange(fp_nlow, fp_nhigh)
        # storage for the wavelength centers
        wave0 = np.ones_like(nth_peak, dtype=float)
        # start the wave inversion of the polynomial at a sensible value
        wave0 = wave0 * np.nanmean(wavemap)
        # need a few iterations to invert polynomial relations
        for _ in range(fp_inv_itr):
            wave0 = np.polyval(cavity_length_poly, wave0)
            wave0 = wave0 * 2 / nth_peak
        # keep lines within the master_wavelength domain
        keep = (wave0 > np.min(wavemap)) & (wave0 < np.max(wavemap))
        wave0 = wave0[keep]
        # sort by wavelength
        wave0 = wave0[np.argsort(wave0)]
        # storage for outputs
        list_waves, list_orders, list_pixels, list_wfit = [], [], [], []
        # loop around orders and get the lines that fall within each
        #    diffraction order
        for order_num in range(nbo):
            # we have a wavelength value, we get an approximate pixel
            # value by fitting wavelength to pixel
            owave = wavemap[order_num]
            with warnings.catch_warnings(record=True) as _:
                # fit_reverse = np.polyfit(owave, xpix, fitdeg)

                ord_owave = np.argsort(owave)
                spline_fit_reverse = mp.iuv_spline(owave[ord_owave],
                                                   xpix[ord_owave])

            # we find lines within the order
            good = (wave0 > np.min(owave)) & (wave0 < np.max(owave))
            # we check that there is at least 1 line and append our line list
            if np.sum(good) != 0:
                # get the pixels positions based on out owave fit
                # pixfit = np.polyval(fit_reverse, wave0[good])
                pixfit = spline_fit_reverse(wave0[good])
                # get the dpix coeffs
                dpixc = np.polyfit(pixfit[1:], pixfit[1:] - pixfit[:-1], 2)
                # use this to get the rounded width?
                wfit = np.ceil(np.polyval(dpixc, pixfit))
                # append to the lists
                list_waves += list(wave0[good])
                list_orders += list(np.repeat(order_num, np.sum(good)))
                list_pixels += list(pixfit)
                list_wfit += list(wfit)
        # make line lists np arrays
        list_waves = np.array(list_waves)
        list_orders = np.array(list_orders)
        list_pixels = np.array(list_pixels)
        list_wfit = np.array(list_wfit, dtype=int)
        # keep lines that are  not too close to image edge
        keep = (list_pixels > wmax) & (list_pixels < (nbpix - wmax))
        # apply to list arrays
        list_waves = list_waves[keep]
        list_orders = list_orders[keep]
        list_pixels = list_pixels[keep]
        list_wfit = list_wfit[keep]

        # Once we have a cavity length, we find the integer FP peak number.
        # This will be compiled in the table later and used for nightly
        # wavelength solutions by changing the achromatic part of the cavity
        # length relative to the master night. By construction, this is
        # always an integer. The factor 2 comes from the FP equation.
        # It arrises from the back-and-forth within the FP cavity
        cavfit = np.polyval(cavity_length_poly, list_waves)
        peak_number = np.array(cavfit * 2 / list_waves, dtype=int)

    # ----------------------------------------------------------------------
    # else we break
    # ----------------------------------------------------------------------
    else:
        # log error and break
        eargs = [e2dsfile.name, dprtype, fiber, func_name, hcfibtypes,
                 fpfibtypes]
        WLOG(params, 'error', TextEntry('00-017-00012', args=eargs))
        list_waves = []
        list_orders = []
        list_pixels = []
        list_wfit = []
        peak_number = []

    # ----------------------------------------------------------------------
    # Fit the peaks
    # ----------------------------------------------------------------------
    # set up storage
    pixel_m = np.array(list_pixels)
    wave_m = np.zeros_like(list_waves)
    ewidth = np.zeros_like(list_pixels)
    amp = np.zeros_like(list_pixels)
    nsig = np.repeat(np.nan, len(list_pixels))

    # ----------------------------------------------------------------------
    # loop around orders
    for order_num in range(nbo):
        # get the order spectrum
        sorder = e2dsfile.data[order_num]
        # find all lines in this order
        good = np.where(list_orders == order_num)[0]
        # get order lines
        order_waves = list_waves[good]
        order_pixels = list_pixels[good]
        order_wfit = list_wfit[good]
        # ------------------------------------------------------------------
        # loop around lines
        valid_lines = 0
        for it in range(len(order_waves)):
            # get the x pixel position
            xpixi = int(np.round(order_pixels[it]))
            # get the width
            wfit = int(np.round(order_wfit[it]))
            # get the pixels within this peak
            index = np.arange(xpixi - wfit, xpixi + wfit + 1)
            # Need to check that index is in bounds
            if (np.min(index) < 0) or (np.max(index) >= nbpix):
                eargs = [order_num, it, index, xpixi, wfit, func_name]
                WLOG(params, 'warning', TextEntry('09-017-00005', args=eargs))
                continue
            # get the flux value in this peak
            ypix = sorder[index]
            # deal with less points than fit (shouldn't happen but worth
            #    catching before an exception happens in fit_gauss_with_slope)
            if len(ypix) < 5:
                eargs = [order_num, it, index, ypix]
                WLOG(params, 'warning', TextEntry('09-017-00006', args=eargs))
                continue
            # --------------------------------------------------------------
            # only continue if we have some finite values
            if np.all(np.isfinite(ypix)):
                # try fitting a gaussian with a slope
                try:
                    # get ypix max and min
                    ymax, ymin = mp.nanmax(ypix), mp.nanmin(ypix)
                    # get up a gauss fit guess
                    guess = [ymax - ymin, xpixi, 1, ymin, 0]
                    # if HC fit a gaussian with a slope
                    if fibtype in hcfibtypes:
                        out = mp.fit_gauss_with_slope(index, ypix, guess, True)
                        # get parameters from fit
                        popt, pcov, model = out
                        # get width condition
                        cond2 = (popt[2] < 2) and (popt[2] > 0.5)
                    # else fit ea airy function to FP
                    else:
                        out = velocity.fit_fp_peaks(index, ypix, wfit,
                                                    return_model=True)
                        # get parameters from fit
                        p0, popt, pcov, warns, model = out
                        # get width condition
                        cond2 = np.abs(popt[2] / wfit - 1) < 0.5
                    # calculate the RMS of the fit
                    rms = mp.nanstd(ypix - model)
                    # if we find 'good' values add to storage
                    cond1 = np.abs(popt[1] - xpixi) < wfit
                    if cond1 and cond2:
                        amp[good[it]] = popt[0]
                        pixel_m[good[it]] = popt[1]
                        ewidth[good[it]] = popt[2]
                        nsig[good[it]] = popt[0] / rms
                        # line is valid
                        valid_lines += 1
                # ignore any bad lines
                except RuntimeError:
                    pass
        # log progress: Order {0}/{1} Fiber {2} Valid lines: {3}/{4} (type={5})
        eargs = [order_num, nbo - 1, fiber, valid_lines, len(order_waves),
                 fibtype]
        WLOG(params, '', TextEntry('40-017-00051', args=eargs))

    # lines that are not at a high enough SNR are flagged as NaN
    # we do NOT remove these lines as we want all tables to have
    # exactly the same length
    with warnings.catch_warnings(record=True) as _:
        bad = ~(nsig > nsig_min)
    nsig[bad] = np.nan
    ewidth[bad] = np.nan
    amp[bad] = np.nan
    pixel_m[bad] = np.nan
    wave_m[bad] = np.nan
    # calculate the difference
    diffpix = pixel_m - list_pixels

    # ----------------------------------------------------------------------
    # Plot the expected lines vs measured line positions
    # ----------------------------------------------------------------------
    # debug plot expected lines vs measured positions
    recipe.plot('WAVEREF_EXPECTED', orders=list_orders, wavemap=list_waves,
                diff=diffpix, fiber=fiber, nbo=nbo, fibtype=fibtype,
                iteration=iteration)

    # ----------------------------------------------------------------------
    # Create table to store them in
    # ----------------------------------------------------------------------
    columnnames = ['WAVE_REF', 'WAVE_MEAS', 'PIXEL_REF', 'PIXEL_MEAS',
                   'ORDER', 'WFIT', 'EWIDTH_MEAS', 'AMP_MEAS', 'NSIG',
                   'DIFF', 'PEAK_NUMBER']
    columnvalues = [list_waves, wave_m, list_pixels, pixel_m, list_orders,
                    list_wfit, ewidth, amp, nsig, diffpix, peak_number]
    # make table
    table = drs_table.make_table(params, columnnames, columnvalues)
    # return table
    return table


def write_wave_lines(params, recipe, hce2ds, fpe2ds, hclines, fplines,
                     fiber, combine, rawhcfiles, rawfpfiles):
    # set function name
    _ = display_func(params, 'write_master_lines', __NAME__)

    # get copy of instance of wave file (WAVE_HCMAP)
    fpwavefile = recipe.outputs['WAVEM_FPMAP'].newcopy(recipe=recipe,
                                                       fiber=fiber)
    # construct the filename from file instance
    fpwavefile.construct_filename(params, infile=hce2ds)
    # ------------------------------------------------------------------
    # copy keys from hcwavefile
    fpwavefile.copy_hdict(fpe2ds)
    # set output key
    fpwavefile.add_hkey('KW_OUTPUT', value=fpwavefile.name)
    fpwavefile.add_hkey('KW_FIBER', value=fiber)
    # add input hc files (and deal with combining or not combining)
    if combine:
        hfiles = rawhcfiles
    else:
        hfiles = [hce2ds.basename]
    fpwavefile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add input fp files (and deal with combining or not combining)
    if combine:
        hfiles = rawfpfiles
    else:
        hfiles = [hce2ds.basename]
    fpwavefile.add_hkey_1d('KW_INFILE2', values=hfiles, dim1name='file')

    # ------------------------------------------------------------------
    # write hc lines
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    hcfile = recipe.outputs['WAVEM_HCLIST'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    hcfile.construct_filename(params, infile=hce2ds)
    # ------------------------------------------------------------------
    # copy keys from hcwavefile
    hcfile.copy_hdict(fpwavefile)
    # set output key
    hcfile.add_hkey('KW_OUTPUT', value=hcfile.name)
    # set data
    hcfile.data = hclines
    hcfile.datatype = 'table'
    # ------------------------------------------------------------------
    # TODO: REMOVE: modify filename
    path = hcfile.filename.split(hcfile.basename)[0]
    hcfile.filename = os.path.join(path, 'EA_' + hcfile.basename)
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [fiber, hcfile.filename]
    WLOG(params, '', TextEntry('40-017-00039', args=wargs))
    # write image to file
    hcfile.write_file()
    # add to output files (for indexing)
    recipe.add_output_file(hcfile)
    # ------------------------------------------------------------------
    # write fp lines
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    fpfile = recipe.outputs['WAVEM_FPLIST'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    fpfile.construct_filename(params, infile=fpe2ds)
    # ------------------------------------------------------------------
    # copy keys from hcwavefile
    fpfile.copy_hdict(fpwavefile)
    # set output key
    fpfile.add_hkey('KW_OUTPUT', value=fpfile.name)
    # set data
    fpfile.data = fplines
    fpfile.datatype = 'table'
    # ------------------------------------------------------------------
    # TODO: REMOVE: modify filename
    path = fpfile.filename.split(fpfile.basename)[0]
    fpfile.filename = os.path.join(path, 'EA_' + fpfile.basename)
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [fiber, fpfile.filename]
    WLOG(params, '', TextEntry('40-017-00039', args=wargs))
    # write image to file
    fpfile.write_file()
    # add to output files (for indexing)
    recipe.add_output_file(fpfile)
    # ------------------------------------------------------------------
    # return hc  and fp line files
    return hcfile, fpfile


def calc_wave_sol(params: ParamDict, hclines: Table, fplines: Table,
                  nbxpix: int, fit_cavity: bool = True,
                  fit_achromatic: bool = True,
                  wavesol_fit_degree: Union[int, None] = None,
                  cavity_fit_degree: Union[int, None] = None,
                  cavity_table_name: Union[str, None] = None,
                  nsig_cut: Union[float, None] = None):
    """
    Calculate the wave solution using a table of hclines and fplines

    each lines table (hclines and fplines) must contain the following columns:
        - WAVE_REF - the line catalogue reference wavelength
        - WAVE_MEAS - the measured line wavelength (can be empty)
        - PIXEL_MEAS - the measured pixel position
        - ORDER - the order each line belongs to
        - NSIG - the uncertainty on the line measurement
        - PEAK_NUMBER - the peak number (blank for HC)

    Original Author: Etienne Artigau

    :param params: ParamDict, parameter dictionary of constants
    :param hclines: Table, HC line table (see above description)
    :param fplines: Table, FP line table (see above description)
    :param nbxpix: int, the number of pixels in the along-order direction
    :param fit_cavity: bool, if True fits cavity width
    :param fit_achromatic: bool, if True fits achromatic part of cavity
    :param wavesol_fit_degree: int, the polynomial degree fit order for the
                               wave solution fit
    :param cavity_fit_degree: int, the polynomial degree fit order for the
                              cavity fit
    :param cavity_table_name: str, the name of the cavity table
    :param nsig_cut: int, the number of sigmas to cut in the robust polyfits

    :return: ParamDict, the wave properties
    """
    # set function name
    func_name = display_func(params, 'calc_wave_sol', __NAME__)
    # -------------------------------------------------------------------------
    # TODO: Add to constants

    # Define the wave solution polynomial fit degree
    params.set('WAVE2_WAVESOL_FIT_DEGREE', value=5)
    # Define the cavity fit polynomial fit degree for wave solution
    params.set('WAVE2_CAVITY_FIT_DEGREE', value=9)
    # Define the cavity fit solution file for wave solution
    params.set('WAVE2_CAVITY_TABLE', value='cavity.csv')
    # Define the number of sigmas to use in wave sol robust fits
    params.set('WAVE2_NSIG_CUT', value=5)
    # Define the minimum number of HC lines in an order to try to find
    #   absolute numbering
    params.set('WAVE2_MIN_HC_LINES', value=5)
    # Define the maximum offset in FP peaks to explore when FP peak counting
    params.set('WAVE2_MAX_FP_COUNT_OFFSET', value=5)
    # Define the number of iterations required to converge the FP peak counting
    #   offset loop
    params.set('WAVE2_FP_COUNT_OFFSET_ITRS', value=3)
    # Define the number of iterations required to converge on a cavity fit
    #  (first time this is done)
    params.set('WAVE2_CAVITY_FIT_ITRS1', value=3)
    # Define the number of iterations required to check order offset
    params.set('WAVE2_ORDER_OFFSET_ITRS', value=2)
    # Define the maximum bulk offset of lines in a order can have
    params.set('WAVE2_MAX_ORDER_BULK_OFFSET', value=10)
    # Define the number of iterations required to converge on a cavity fit
    #  (first time this is done)
    params.set('WAVE2_CAVITY_FIT_ITRS2', value=3)
    # Define the number of iterations required to do the final fplines
    #   wave solution
    params.set('WAVE2_FWAVESOL_ITRS', value=3)

    # -------------------------------------------------------------------------
    # TODO: 0.6 dummy kwargs (replace with override in pcheck)
    kwargs = dict()
    kwargs['wavesol_fit_degree'] = wavesol_fit_degree
    kwargs['cavity_fit_degree'] = cavity_fit_degree
    kwargs['cavity_table_name'] = cavity_table_name
    kwargs['nsig_cut'] = nsig_cut
    # -------------------------------------------------------------------------
    # get parameters from params / inputs
    # -------------------------------------------------------------------------
    wavesol_order = pcheck(params, 'WAVE2_WAVESOL_FIT_DEGREE',
                           'wavesol_fit_degree', kwargs, func_name)
    cavity_fit_degree = pcheck(params, 'WAVE2_CAVITY_FIT_DEGREE',
                               'cavity_fit_degree', kwargs, func_name)
    cavity_table_name = pcheck(params, 'WAVE2_CAVITY_TABLE',
                               'cavity_table_name', kwargs, func_name)
    nsig_cut = pcheck(params, 'WAVE2_NSIG_CUT', 'nsig_cut', kwargs, func_name)
    min_hc_lines = pcheck(params, 'WAVE2_MIN_HC_LINES', 'min_hc_lines',
                          kwargs, func_name)
    max_fp_c_offset = pcheck(params, 'WAVE2_MAX_FP_COUNT_OFFSET',
                             'max_fp_c_offset', kwargs, func_name)
    fp_count_offset_iterations = pcheck(params, 'WAVE2_FP_COUNT_OFFSET_ITRS',
                                        'fp_count_itr', kwargs, func_name)
    cavity_fit_iterations1 = pcheck(params, 'WAVE2_CAVITY_FIT_ITRS1',
                                   'cavity_fit_itr1', kwargs, func_name)
    order_offset_iterations = pcheck(params, 'WAVE2_ORDER_OFFSET_ITRS',
                                     'ord_offset_itr', kwargs, func_name)
    max_ord_bulk_offset = pcheck(params, 'WAVE2_MAX_ORDER_BULK_OFFSET',
                                 'max_ord_bulk_offset', kwargs, func_name)
    cavity_change_err_thres = pcheck(params, 'WAVE2_CAVITY_CHANGE_ERR_THRES',
                                     'cav_change_err_thres', kwargs, func_name)
    cavity_fit_iterations2 = pcheck(params, 'WAVE2_CAVITY_FIT_ITRS2',
                                   'cavity_fit_itr2', kwargs, func_name)
    odd_ratio = pcheck(params, 'WAVE2_HC_VEL_ODD_RATIO', 'odd_ratio',
                       kwargs, func_name)
    fwavesol_iterations = pcheck(params, 'WAVE2_FWAVESOL_ITRS', 'fwavesol_itr',
                                 kwargs, func_name)
    # -------------------------------------------------------------------------
    # setup parameters
    # -------------------------------------------------------------------------
    # order list
    orders = np.unique(fplines['ORDER'])
    # -------------------------------------------------------------------------
    # only keep pixels that have finite positions
    # it is fine to have orders with no valid lines
    hclines = hclines[np.isfinite(hclines['PIXEL_MEAS'])]
    fplines = fplines[np.isfinite(fplines['PIXEL_MEAS'])]
    # -------------------------------------------------------------------------
    # to get started, we assume that we do not know the wavelength of FP lines
    fplines['WAVE_MEAS'] = np.repeat(np.nan, len(fplines))
    # -------------------------------------------------------------------------
    # Part 1: We do not know the wavelength of FP lines --> measure it for
    #         all FP lines (using the HC lines if there are enough)
    # -------------------------------------------------------------------------
    # loop around orders
    for order_num in orders:
        # find the hc and fp lines for the current oder
        good_fp = fplines['ORDER'] == order_num
        good_hc = hclines['ORDER'] == order_num
        # get the fplines for this order
        ordfp_pix_meas = fplines[good_fp]['PIXEL_MEAS']
        ordfp_peak_num = fplines[good_fp]['PEAK_NUMBER']
        # mask the hclines
        ordhc_pix_meas = hclines[good_hc]['PIXEL_MEAS']
        ordhc_wave_ref = hclines[good_hc]['WAVE_REF']
        # ---------------------------------------------------------------------
        # express step in pixels as a polynomial fit. This is used to count
        # fp peaks afterward
        xfit1 = ordfp_pix_meas[1:]
        yfit1 = ordfp_pix_meas[1:] - ordfp_pix_meas[:-1]
        # fit the step between FP lines
        fit_step, _ = mp.robust_polyfit(xfit1, yfit1, wavesol_order, nsig_cut)
        # ---------------------------------------------------------------------
        # counting steps backward
        # maybe first step is wrong, we'll see later by x-matching with HC lines
        # after this step, we know that lines within the order have
        # *relative* numbers that are ok
        for step_fp in range(1, len(ordfp_pix_meas)):
            # find expected step between previous and current FP peak
            # We start numbering at 1 as the 0th serves as a relative
            # starting point
            diff = ordfp_pix_meas[step_fp] - ordfp_pix_meas[step_fp - 1]
            dfit = np.polyval(fit_step, ordfp_pix_meas[step_fp - 1])
            dnum = diff / dfit
            # dnum is always very close to an integer value, we round it
            # we subtract the steps, FP peaks go in decreasing number
            rdnum = np.round(dnum)
            ordfp_peak_num[step_fp] = ordfp_peak_num[step_fp - 1] - rdnum
        # ---------------------------------------------------------------------
        # if we don't have more than "min_hc_lines" hc lines, we store the
        #   new values and skip to next order
        # ---------------------------------------------------------------------
        if np.sum(good_hc) <= min_hc_lines:
            # put into the table
            fplines[good_fp]['PIXEL_MEAS'] = ordfp_pix_meas
            fplines[good_fp]['PEAK_NUMBER'] = ordfp_peak_num
            # skip to next order
            continue
        # ---------------------------------------------------------------------
        # if we have more than "min_hc_lines" hc lines, we try to find
        #     the absolute numbering
        # ---------------------------------------------------------------------
        # we fit an approximate wavelength solution
        hc_wave_fit, _ = mp.robust_polyfit(ordhc_pix_meas, ordhc_wave_ref,
                                           wavesol_fit_degree, nsig_cut)
        # we find the steps in FP lines at the position of all HC lines
        step_hc = np.polyval(fit_step, ordhc_pix_meas)
        # get the derivative of the wave fit
        d_hc_wave_fit = np.polyder(hc_wave_fit)
        # get the step in waves
        step_hc_wave = np.polyval(d_hc_wave_fit, ordhc_pix_meas) * step_hc
        # -----------------------------------------------------------------
        # convert step in cavity through the order. We assume a constant
        #    cavity through the order
        cavity_per_order = mp.nanmedian(ordhc_wave_ref**2 / step_hc_wave)
        # copy this
        cavity_per_order0 = np.array(cavity_per_order)
        # -----------------------------------------------------------------
        # we explore integer offset in FP peak counting and find the
        #     offset that defines the wavelength solution leading to the
        #     smallest RMS between predicted and catalog HC peak positions
        offset = np.arange(-max_fp_c_offset, max_fp_c_offset + 1)
        # set up storage of sigmas
        osigmas = np.zeros_like(offset, dtype=float)
        # loop around offsets
        for o_it in range(len(offset)):
            # reset the cavity per order
            cavity_per_order = np.array(cavity_per_order0)
            # get the peak number offset
            peak_num_offset = ordfp_peak_num + offset[o_it]
            # get a temporary wave sol
            wave_tmp = cavity_per_order / peak_num_offset
            # fit this wave solution for FP lines
            ofpwave_fit = np.polyfit(ordfp_pix_meas, wave_tmp,
                                     wavesol_fit_degree)
            # -----------------------------------------------------------------
            # loop iteratively to converge cavity per order
            for _ in range(fp_count_offset_iterations):
                # get a temporary wave sol
                wave_tmp = cavity_per_order / peak_num_offset
                # fit this wave solution for FP lines
                ofpwave_fit = np.polyfit(ordfp_pix_meas, wave_tmp,
                                         wavesol_fit_degree)
                # fit the inverse for the hc lines
                ohcwave_fit = np.polyfit(ofpwave_fit, ordhc_pix_meas)
                # work out the median of the residuals to the fit for the
                #   hc lines
                med_hc_res = mp.nanmedian(1 - ordhc_wave_ref/ohcwave_fit)
                # update the cavity per order by 1 - the median of the res
                cavity_per_order = cavity_per_order * (1-med_hc_res)
            # -----------------------------------------------------------------
            # if the inverse for the hc lines once more
            ohcwave_fit = np.polyfit(ofpwave_fit, ordhc_pix_meas)
            # calculate the hc residuals
            hc_res = 1 - ordhc_wave_ref/ohcwave_fit
            # calculate the offset sigma for this offset (and express as
            #   velocity)
            osigma = mp.estimate_sigma(hc_res * speed_of_light_ms, 1.0)
            # store in osgimas
            osigmas[o_it] = osigma
        # ---------------------------------------------------------------------
        # we apply the offset that leads to the smallest HC (o-c) RMS
        ordfp_peak_num = ordfp_peak_num + offset[np.argmin(osigmas)]
        # get a temporary wave sol
        wave_tmp = cavity_per_order / ordfp_peak_num
        # ---------------------------------------------------------------------
        # we find the best cavity length estimate
        for _ in range(cavity_fit_iterations1):
            # we force the cavity length to lead to a median HC peak position
            # error of zero.
            # we could use a better sigma-clipping, but this is hard with a
            # small number of lines
            # -----------------------------------------------------------------
            # get a temporary wave sol
            wave_tmp = cavity_per_order / ordfp_peak_num
            # fit this wave solution
            wave_fit = np.polyfit(ordfp_pix_meas, wave_tmp, wavesol_fit_degree)
            # inverse this fit using the HC lines
            ohcwave_fit = np.polyval(wave_fit, ordhc_pix_meas)
            # work out the residuals
            med_hc_res = mp.nanmedian(1 - ordhc_wave_ref / ohcwave_fit)
            # update the cavity per order by 1 - the median of the res
            cavity_per_order = cavity_per_order * (1-med_hc_res)
        # ---------------------------------------------------------------------
        # we now have a best-guess of the wavelength solution, we update
        #  the WAVE_MEAS in the FP line list. This will be used to constrain the
        # cavity length below
        wave_fit = np.polyfit(ordfp_pix_meas, wave_tmp, wavesol_fit_degree)
        # re-fit wave solution on all lines --> measured wave sol
        ordfp_wave_meas = np.polyval(wave_fit, ordfp_pix_meas)
        # ---------------------------------------------------------------------
        # put into the table. If we had enough HC lines, the WAVE_MEAS has
        #    been updated if not, at least the FP peak counting is valid.
        fplines[good_fp]['PIXEL_MEAS'] = ordfp_pix_meas
        fplines[good_fp]['PEAK_NUMBER'] = ordfp_peak_num
        fplines[good_fp]['WAVE_MEAS'] = ordfp_wave_meas
    # -------------------------------------------------------------------------
    # save some information for plotting later
    fp_pix_meas_1 = np.array(fplines['PIXEL_MEAS'])
    fp_wave_meas_1 = np.array(fplines['WAVE_MEAS'])

    # -------------------------------------------------------------------------
    # Loop 2: Find offsets
    # -------------------------------------------------------------------------
    # loop around order offset iterations
    for _ in range(order_offset_iterations):
        # loop around orders
        # skip first order, and check order to order if the cavity
        # is consistent with previous. Order=1 is compared to Order=0, then
        # Order=2 to Order=1...
        for order_num in orders[1: ]:
            # get mask for previous order
            good_prev_fp = fplines['ORDER'] == order_num - 1
            good_fp = fplines['ORDER'] == order_num
            # get vectors for this order
            ordfp_wave_meas = fplines['WAVE_MEAS'][good_fp]
            ordfp_peak_num = fplines['PEAK_NUMBER'][good_fp]
            # get vectors for previous order
            prevfp_wave_meas = fplines['WAVE_MEAS'][good_prev_fp]
            prevfp_peak_num = fplines['PEAK_NUMBER'][good_prev_fp]
            # -----------------------------------------------------------------
            # current peak numbers if you take the previous order cavity
            #    length and assume it's the same of current order while using
            #    the current order wavelength solution.
            current_numbering = ordfp_peak_num
            # The median between the two should be close to zero
            #    (extrapolated_numbering can be float, not int as
            #     current_numbering). If the is a mis-counting, then you get
            #     a median very close to an integer value. This tells you the
            #     offset to be applied to have a consistent cavity length
            # get the median of previous order
            med_prev = mp.nanmedian(prevfp_wave_meas * prevfp_peak_num)
            # user median of previous order to extrapolate to this order
            extrapolated_numbering = med_prev / ordfp_wave_meas
            # -----------------------------------------------------------------
            # work out the offset between current numbering and those
            #   extrapolated from previous order
            offset = mp.nanmedian(current_numbering - extrapolated_numbering)
            # subtract this offset off the order values
            if np.isfinite(offset):
                ordfp_peak_num = ordfp_peak_num - offset
            # add the peak num back to fplines
            fplines['PEAK_NUMBER'][good_fp] = ordfp_peak_num
        # ---------------------------------------------------------------------
        # now that we have patched the order-to-order glitches, we look for
        #     a bulk offset in the counts that minimizes the dispersion in
        #     cavity length.
        global_offset = np.arange(max_ord_bulk_offset, max_ord_bulk_offset + 1)
        # set up storage of sigmas
        gosigmas = np.zeros_like(global_offset, dtype=float)
        # loop around offsets
        for goffset in range(len(global_offset)):
            # apply global offset
            peak_num = fplines['PEAK_NUMBER'] + global_offset[goffset]
            # calculate cavity
            cavity = fplines['WAVE_MEAS'] * peak_num
            # work out sigma
            gosigmas[goffset] = mp.estimate_sigma(cavity, 1.0)
        # best guess at offset
        best_offset = global_offset[np.argmin(gosigmas)]
        # update peak number with best offset (from gosigmas)
        fplines['PEAK_NUMBER'] = fplines['PEAK_NUMBER'] + best_offset
    # -------------------------------------------------------------------------
    # now we have valid numbering and best-guess WAVE_MEAS, we find the
    #    cavity length
    wavepeak = fplines['WAVE_MEAS'] * fplines['PEAK_NUMBER']
    cavity, _ = mp.robust_polyfit(fplines['WAVE_MEAS'], wavepeak,
                                  cavity_fit_degree, nsig_cut)
    # -------------------------------------------------------------------------
    # save some information for plotting later
    fp_pix_meas_2 = np.array(fplines['PIXEL_MEAS'])
    fp_wave_meas_2 = np.array(fplines['WAVE_MEAS'])
    # -------------------------------------------------------------------------
    # TODO: Add plot cavity fit before and after
    plotkwargs = dict(fp_pix_meas_1=fp_pix_meas_1,
                      fp_wave_meas_1=fp_wave_meas_1,
                      fp_pix_meas_2=fp_pix_meas_2,
                      fp_wave_meas_2=fp_wave_meas_2)
    # -------------------------------------------------------------------------
    # if fit_cavity is False and a file exists we load this file
    # (otherwise we save this cavity file later)

    if not fit_cavity:
        # TODO: load cavity file  + deal with file not existing
        pass

    # -------------------------------------------------------------------------
    # copy the cavity fit
    cavity0 = np.array(cavity)
    # set the mean2error to infinite
    mean2error = np.inf
    # -------------------------------------------------------------------------
    # we change the achromatic cavity length term to force HC peaks to have a
    #    zero velocity error.
    while mean2error > cavity_change_err_thres:
        # get the proper cavity length from the cavity polynomial
        for _ in range(cavity_fit_iterations2):
            # get width
            tmp = fplines['WAVE_REF'] / fplines['PEAK_NUMBER']
            # update wave ref based on the fit
            fplines['WAVE_REF'] = np.polyval(cavity, tmp)
        # ---------------------------------------------------------------------
        # get the wavelength solution for the order and the HC line position
        #     that it implies. The diff between the HC position found here and
        #     the catalog one is used to change the cavity length
        # ---------------------------------------------------------------------
        # loop around order
        for order_num in orders:
            # find the hc and fp lines for the current oder
            good_fp = fplines['ORDER'] == order_num
            good_hc = hclines['ORDER'] == order_num
            # get the fplines for this order
            ordfp_pix_meas = fplines[good_fp]['PIXEL_MEAS']
            ordfp_wave_ref = fplines[good_fp]['PEAK_NUMBER']
            # mask the hclines
            ordhc_pix_meas = hclines[good_hc]['PIXEL_MEAS']
            # get wave fit
            wave_fit, _ = mp.robust_polyfit(ordfp_pix_meas, ordfp_wave_ref,
                                            wavesol_fit_degree, nsig_cut)
            # update wave measure from this fit
            fp_wave_meas = np.polyval(wave_fit, ordfp_pix_meas)
            fplines['WAVE_MEAS'][good_fp] = fp_wave_meas
            # if we have some HC lines update these too
            if np.sum(good_hc) > 0:
                hc_wave_meas = np.polyval(wave_fit, ordhc_pix_meas)
                hclines['WAVE_MEAS'][good_fp] = hc_wave_meas
        # ---------------------------------------------------------------------
        # in velocity, diff between measured and catalog HC line positions
        res = hclines['WAVE_MEAS'] / hclines['WAVE_REF']
        diff_hc = (1 - res) * speed_of_light_ms
        # model of the errors in the HC line positions. We assume that
        # they decrease as 1/NSIG
        hcsigma = mp.estimate_sigma(diff_hc * hclines['NSIG']) / hclines['NSIG']
        # get smart mean of the velocity error
        mean_hc_vel, err_hc_vel = mp.odd_ratio_mean(diff_hc, hcsigma,
                                                    odd_ratio=odd_ratio)
        # ---------------------------------------------------------------------
        # if we are allowed to change the achromatic cavity length, then
        #    we do it, else we just keep track of how much we would have
        #    changed it.
        if fit_achromatic:
            # recalculate mean to error ratio
            mean2error = np.abs(mean_hc_vel / err_hc_vel)
            # update last coefficient of the cavity fit
            cavity[-1] = cavity[-1] * (1 + mean2error / speed_of_light_ms)
        # else set the mean2error to zero
        else:
            mean2error = 0.0
        # ---------------------------------------------------------------------
        # TODO: move to language database
        msg = 'Mean HC position {0:6.2f}+-{1:.2f} m/s'
        margs = [mean_hc_vel, err_hc_vel]
        WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # TODO: move to language database
    msg = 'Change in cavity length {0:6.2f} nm'
    margs = [cavity[-1] - cavity0[-1]]
    WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # TODO: plot diff_hc hist + nsig hist

    # -------------------------------------------------------------------------
    # update wave solution for fplines
    for _ in range(fwavesol_iterations):
        # get wave / peak
        wavepeak = fplines['WAVE_REF'] / fplines['PEAK_NUMBER']
        # update fplines
        fplines['WAVE_REF'] = np.polyval(cavity, wavepeak)
        # TODO: why don't we update hclines?
    # -------------------------------------------------------------------------
    # Construct the wavelength coefficients / wave map
    # -------------------------------------------------------------------------
    wave_coeffs = np.zeros([len(orders), wavesol_fit_degree])
    wave_map = np.zeros([len(orders), nbxpix])
    # get xpix
    xpix = np.arange(nbxpix)
    # loop around orders
    for order_num in orders:
        # get the fp lines for this order
        good_fp = fplines['ORDER'] == order_num
        # get fpline vectors
        ordfp_pix_meas = fplines[good_fp]['PIXEL_MEAS']
        ordfp_wave_ref = fplines[good_fp]['WAVE_REF']
        # fit the solution to this order
        ord_wave_sol, _ = mp.robust_polyfit(ordfp_pix_meas, ordfp_wave_ref,
                                            wavesol_fit_degree, nsig_cut)
        # add to wave coefficients
        # TODO: should this be backwards?
        wave_coeffs[order_num] = ord_wave_sol[::-1]
        # generate wave map for order
        wave_map[order_num] = np.polyval(ord_wave_sol, xpix)
    # -------------------------------------------------------------------------
    # construct wave properties
    # -------------------------------------------------------------------------
    wprops = ParamDict()
    wprops['COEFFS'] = wave_coeffs
    wprops['WAVEMAP'] = wave_map
    wprops['NBO'] = len(orders)
    wprops['DEG'] = wavesol_fit_degree
    wprops['NBPIX'] = nbxpix
    # set source
    keys = ['WAVEMAP', 'NBO', 'DEG', 'COEFFS', 'NBPIX']
    wprops.set_sources(keys, func_name)
    # return wave properties
    return wprops


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

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
# Define functions
# =============================================================================
def get_master_lines(params, recipe, e2dsfile, wavemap, cavity_poly=None,
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


def write_master_lines(params, recipe, hce2ds, fpe2ds, hclines, fplines,
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


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

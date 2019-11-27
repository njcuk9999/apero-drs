#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-07 at 13:28

@author: cook
"""
from __future__ import division
from astropy import constants as cc
from astropy import units as uu
import numpy as np
from scipy.optimize import curve_fit
import warnings
import os

from apero import core
from apero.core import math as mp
from apero import locale
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.io import drs_data

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'polar.lsd.py'
__INSTRUMENT__ = None
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
WLOG = core.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define user functions
# =============================================================================
def lsd_analysis_wrapper(params, pobjects, pprops, wprops, **kwargs):
    """
    Function to call functions to perform Least Squares Deconvolution (LSD)
    analysis on the polarimetry data.

    :param params: ParamDict, parameter dictionary of constants
    :param pprops: ParamDict, parameter dictionary of polar data
    :param wprops: ParamDict, parameter dictionary of wavelength data
    :param kwargs: additional arguments (overwrite param properties)
    :return:
    """
    # set function name
    func_name = display_func(params, 'lsd_analysis', __NAME__)
    # get parameters from params/kwargs
    do_lsd = pcheck(params, 'POLAR_LSD_ANALYSIS', 'do_lsd', kwargs, func_name)
    wl_lower = pcheck(params, 'POLAR_LSD_WL_LOWER', 'wl_lower', kwargs,
                      func_name, mapf='list', dtype=float)
    wl_upper = pcheck(params, 'POLAR_LSD_WL_UPPER', 'wl_lower', kwargs,
                      func_name, mapf='list', dtype=float)
    min_depth = pcheck(params, 'POLAR_LSD_MIN_LINEDEPTH', 'min_depth', kwargs,
                       func_name)
    vinit = pcheck(params, 'POLAR_LSD_VINIT', 'vinit', kwargs, func_name)
    vfinal = pcheck(params, 'POLAR_LSD_VFINAL', 'vfinal', kwargs, func_name)
    normalize = pcheck(params, 'POLAR_LSD_NORM', 'normalize', kwargs, func_name)
    nbinsize1 = pcheck(params, 'POLAR_LSD_NBIN1', 'nbinsize1', kwargs,
                       func_name)
    noverlap1 = pcheck(params, 'POLAR_LSD_NOVERLAP1', 'noverlap1', kwargs,
                      func_name)
    nsigclip1 = pcheck(params, 'POLAR_LSD_NSIGCLIP1', 'nsigclip1', kwargs,
                      func_name)
    nwindow1 = pcheck(params, 'POLAR_LSD_NWINDOW1', 'nwindow1', kwargs,
                      func_name)
    nmode1 = pcheck(params, 'POLAR_LSD_NMODE1', 'nmode1', kwargs, func_name)
    nlfit1 = pcheck(params, 'POLAR_LSD_NLFIT1', 'nlfit1', kwargs, func_name)
    npoints = pcheck(params, 'POLAR_LSD_NPOINTS', 'npoints', kwargs, func_name)

    nbinsize2 = pcheck(params, 'POLAR_LSD_NBIN2', 'nbinsize2', kwargs,
                       func_name)
    noverlap2 = pcheck(params, 'POLAR_LSD_NOVERLAP2', 'noverlap2', kwargs,
                      func_name)
    nsigclip2 = pcheck(params, 'POLAR_LSD_NSIGCLIP1', 'nsigclip1', kwargs,
                      func_name)
    nwindow2 = pcheck(params, 'POLAR_LSD_NWINDOW2', 'nwindow2', kwargs,
                      func_name)
    nmode2 = pcheck(params, 'POLAR_LSD_NMODE2', 'nmode2', kwargs, func_name)
    nlfit2 = pcheck(params, 'POLAR_LSD_NLFIT2', 'nlfit2', kwargs, func_name)
    # define outputs
    lprops = ParamDict()
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', TextEntry('40-021-00004'))
    # ----------------------------------------------------------------------
    # deal with not running lsd
    if not do_lsd:
        oargs = [lprops, func_name, do_lsd, wl_lower, wl_upper, min_depth,
                 vinit, vfinal, normalize, nbinsize1, noverlap1, nsigclip1,
                 nwindow1, nmode1, nlfit1, npoints, nbinsize2, noverlap2,
                 nsigclip2, nwindow2, nmode2, nlfit2]
        return add_outputs(*oargs)
    # ----------------------------------------------------------------------
    # get data from pprops
    pol = pprops['POL']
    polerr = pprops['POLERR']
    null = pprops['NULL2']
    stokesi = pprops['STOKESI']
    stokesierr = pprops['STOKESIERR']
    # get data from wprops
    wavemap = wprops['WAVEMAP']
    # get first file as reference
    pobj = pobjects['A_1']
    # ----------------------------------------------------------------------
    # get temperature from file
    temperature = pobj.infile.get_key('KW_OBJ_TEMP', dtype=float,
                                      required=False)
    # deal with no temperature
    if temperature is None:
        eargs = [pobj.filename, params['KW_OBJTEMP'][0], func_name]
        WLOG(params, 'warning', TextEntry('09-021-00008', args=eargs))
        # return outputs
        oargs = [lprops, func_name, False, wl_lower, wl_upper, min_depth,
                 vinit, vfinal, normalize, nbinsize1, noverlap1, nsigclip1,
                 nwindow1, nmode1, nlfit1, npoints, nbinsize2, noverlap2,
                 nsigclip2, nwindow2, nmode2, nlfit2]
        return add_outputs(*oargs)
    # ----------------------------------------------------------------------
    # load the spectral lines
    # ----------------------------------------------------------------------
    out = load_lsd_spectral_lines(params, temperature, wl_lower, wl_upper,
                                  min_depth)
    sp_filename, wavec, zn, depth, weight = out

    # ----------------------------------------------------------------------
    # get wavelength ranges covering spectral lines in the ccf mask
    # ----------------------------------------------------------------------
    fwave_lower, fwave_upper = get_wl_ranges(wavec, vinit, vfinal)

    # ----------------------------------------------------------------------
    # prepare polarimetry data
    # ----------------------------------------------------------------------
    # bunch normalisation params into nparams
    nparams = dict(binsize=nbinsize1, overlap=noverlap1, sigmaclip=nsigclip1,
                   window=nwindow1, mode=nmode1, use_linear_fit=nlfit1)
    # prepare data
    out = prepare_polarimetry_data(params, wavemap, stokesi, stokesierr, pol,
                                   polerr, null, fwave_lower, fwave_upper,
                                   normalize, nparams)
    spfile, lsd_wave, lsd_stokesi, lsd_stokesierr, lsd_pol = out[:5]
    lsd_polerr, lsd_null = out[5:]

    # ----------------------------------------------------------------------
    # call function to perform lsd analysis
    # ----------------------------------------------------------------------
    # bunch normalisation params into nparams
    nparams = dict(binsize=nbinsize2, overlap=noverlap2, sigmaclip=nsigclip2,
                   window=nwindow2, mode=nmode2, use_linear_fit=nlfit2)
    # run lsd analysis
    out = lsd_analysis(lsd_wave, lsd_stokesi, lsd_stokesierr, lsd_pol,
                       lsd_polerr, lsd_null, wavec, depth, weight, vinit,
                       vfinal, npoints, nparams)
    # ----------------------------------------------------------------------
    # push into storage
    lprops['LSD_WAVE'] = lsd_wave
    lprops['LSD_VELOCITIES'] = out[0]
    lprops['LSD_STOKES_I'] = out[1]
    lprops['LSD_STOKES_I_ERR'] = lsd_stokesierr
    lprops['LSD_STOKES_I_MODEL'] = out[2]
    lprops['LSD_STOKES_I_FIT_RV'] = out[3]
    lprops['LSD_STOKES_FIT_RESOL'] = out[4]
    lprops['LSD_POL'] = lsd_pol
    lprops['LSD_POLERR'] = lsd_polerr
    lprops['LSD_POL_MEAN'] = out[5]
    lprops['LSD_POL_STD'] = out[6]
    lprops['LSD_POL_MEDIAN'] = out[7]
    lprops['LSD_POL_MED_ABS_DEV'] = out[8]
    lprops['LSD_STOKES_VQU'] = out[9]
    lprops['LSD_STOKES_VQU_MEAN'] = out[10]
    lprops['LSD_STOKES_VQU_STD'] = out[11]
    lprops['LSD_NULL'] = out[12]
    lprops['LSD_NULL_MEAN'] = out[13]
    lprops['LSD_NULL_STD'] = out[14]
    lprops['LSD_MASK'] = spfile
    # set source
    keys = ['LSD_WAVE', 'LSD_VELOCITIES', 'LSD_STOKES_I', 'LSD_STOKES_I_ERR',
            'LSD_STOKES_I_MODEL', 'LSD_STOKES_I_FIT_RV', 'LSD_STOKES_FIT_RESOL',
            'LSD_POL', 'LSD_POLERR', 'LSD_POL_MEAN', 'LSD_POL_STD',
            'LSD_POL_MEDIAN', 'LSD_POL_MED_ABS_DEV', 'LSD_STOKES_VQU',
            'LSD_STOKES_VQU_MEAN', 'LSD_STOKES_VQU_STD', 'LSD_NULL',
            'LSD_NULL_MEAN', 'LSD_NULL_STD', 'LSD_MASK']
    lprops.set_sources(keys, func_name)

    # return lsd properties
    oargs = [lprops, func_name, do_lsd, wl_lower, wl_upper, min_depth,
             vinit, vfinal, normalize, nbinsize1, noverlap1, nsigclip1,
             nwindow1, nmode1, nlfit1, npoints, nbinsize2, noverlap2,
             nsigclip2, nwindow2, nmode2, nlfit2]
    return add_outputs(*oargs)


# =============================================================================
# Define worker functions
# =============================================================================
def load_lsd_spectral_lines(params, temperature, wl_lower, wl_upper,
                            min_depth):
    """
    Function to load spectral lines data for LSD analysis.

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            IC_POLAR_LSD_CCFLINES: list of strings, list of files containing
                                   spectral lines data
            IC_POLAR_LSD_WLRANGES: array of float pairs for wavelength ranges
            IC_POLAR_LSD_MIN_LINEDEPTH: float, line depth threshold
    :param loc: parameter dictionary, ParamDict to store data

    :return loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
        sp_filename: string, selected filename with CCF lines
        wavec: numpy array (1D), central wavelengths
        znum: numpy array (1D), atomic number (Z)
        loc['LSD_LINES_DEPTH']: numpy array (1D), line depths
        loc['LSD_LINES_POL_WEIGHT']: numpy array (1D), line weights =
                                     depth * lande * wlc
    """
    # set function name
    func_name = display_func(params, 'load_lsd_spectral_lines', __NAME__)
    # ----------------------------------------------------------------------
    # get temperature data
    sp_data, sp_filename = drs_data.load_sp_mask_lsd(params, temperature)
    # get data
    wavec = sp_data['wavec']
    znum = sp_data['znum']
    depth = sp_data['depth']
    lande = sp_data['lande']
    # ----------------------------------------------------------------------
    # set up mask for wl ranges
    wl_mask = np.zeros(len(wavec), dtype=bool)
    # loop over spectral ranges to select only spectral lines within ranges
    for it in range(len(wl_lower)):
        wl_mask |= (wavec > wl_lower[it]) & (wavec < wl_upper[it])
    # apply mask to data
    wavec = wavec[wl_mask]
    zn = znum[wl_mask]
    depth = depth[wl_mask]
    lande = lande[wl_mask]
    # ----------------------------------------------------------------------
    # PS. Below it applies a line depth mask, however the cut in line depth
    # should be done according to the SNR. This will be studied and implemented
    # later. E. Martioli, Aug 10 2018.

    # create mask to cut lines with depth lower than POLAR_LSD_MIN_LINEDEPTH
    dmask = np.where(depth > min_depth)
    # apply mask to the data
    wavec = wavec[dmask]
    zn = zn[dmask]
    depth = depth[dmask]
    lande = lande[dmask]
    # calculate weights for calculation of polarimetric Z-profile
    weight = wavec * depth * lande
    weight = weight / np.max(weight)
    # return variables
    return sp_filename, wavec, zn, depth, weight


def get_wl_ranges(wavec, vinit, vfinal):
    """
    Function to generate a list of spectral ranges covering all spectral
    lines in the CCF mask, where the width of each individual range is
    defined by the LSD velocity vector

    :param wavec: numpy array (1D), central wavelengths
    :param vinit: initial velocity for LSD profile
    :param vfinal: final velocity for LSD profile

    :returns: the wavelength ranges tuple of lower and upper bounds
    """
    # calculate the velocity difference
    vdiff = vfinal - vinit

    # define the spectral ranges
    d_wave = wavec * vdiff / (2 * speed_of_light)
    wave_lower = wavec - d_wave
    wave_upper = wavec + d_wave
    # merge overlapping regions
    current_lower, current_upper = wave_lower[0], wave_upper[0]
    # storage for outputs
    final_wave_lower, final_wave_upper = [], []
    # loop through limits and merge
    for it in range(len(wave_lower)):
        # if lower is less than current upper change the current upper value
        if wave_lower[it] <= current_upper:
            current_upper = wave_upper[it]
        # else append to final bounds
        else:
            final_wave_lower.append(current_lower)
            final_wave_upper.append(current_upper)
            # update the current bounds
            current_lower, current_upper = wave_lower[it], wave_upper[it]
    # append last bounds
    final_wave_lower.append(current_lower)
    final_wave_upper.append(current_upper)
    # return wlranges
    return final_wave_lower, final_wave_upper


def prepare_polarimetry_data(params, wavemap, stokesi, stokesierr, pol, polerr,
                             null, fwave_lower, fwave_upper, normalize=True,
                             nparams=None):
    """
    Function to prepare polarimetry data for LSD analysis.

    :param wave: numpy array (2D), wavelength data
    :param stokesi: numpy array (2D), Stokes I data
    :param stokesierr: numpy array (2D), errors of Stokes I
    :param pol: numpy array (2D), degree of polarization data
    :param polerr: numpy array (2D), errors of degree of polarization
    :param null2: numpy array (2D), 2nd null polarization
    :param normalize: bool, normalize Stokes I data

    :returns: updated data (wave, stokesi, stokesierr, pol, polerr, null2)
    """
    # get the dimensions from wavemap
    nord, nbpix = wavemap.shape
    # get the wavelength mask (per order)
    # TODO: Question: Why do we need this?
    owltable, owlfilename = drs_data.load_order_mask(params)
    owl_lower = owltable['lower']
    owl_upper = owltable['upper']
    # ------------------------------------------------------------------
    # storage for lsd
    lsd_wave, lsd_stokesi, lsd_stokesierr = [], [], []
    lsd_pol, lsd_polerr, lsd_null = [], [], []
    # ------------------------------------------------------------------
    # loop over each order
    for order_num in range(nord):
        # ------------------------------------------------------------------
        # mask the nan values
        nanmask = np.isfinite(stokesi[order_num]) & np.isfinite(pol[order_num])
        # ------------------------------------------------------------------
        # mask by wavelength
        wavemask  = wavemap[order_num] > owl_lower[order_num]
        wavemask  &= wavemap[order_num] < owl_upper[order_num]
        # ------------------------------------------------------------------
        # combine masks
        mask = nanmask & wavemask
        # ------------------------------------------------------------------
        # test if we still have valid elements
        if np.sum(mask) == 0:
            continue
        # ------------------------------------------------------------------
        # normalise if required
        if normalize and nparams is not None:
            # add x and y to nparams
            nparams['x'] = wavemap[order_num][mask]
            nparams['y'] = stokesi[order_num][mask]
            # calculate continuum
            continuum, _, _ = mp.continuum(**nparams)
            # normalize stokesi
            flux = stokesi[order_num][mask] / continuum
        else:
            flux = stokesi[order_num][mask]
        # ------------------------------------------------------------------
        # append to lsd storage
        lsd_wave += list(wavemap[order_num][mask])
        lsd_stokesi += list(flux)
        lsd_stokesierr += list(stokesierr[order_num][mask])
        lsd_pol += list(pol[order_num][mask])
        lsd_polerr += list(polerr[order_num][mask])
        lsd_null += list(null[order_num][mask])
    # ----------------------------------------------------------------------
    # sort by wavelength
    sortmask = np.argsort(lsd_wave)
    lsd_wave = np.array(lsd_wave)[sortmask]
    lsd_stokesi = np.array(lsd_stokesi)[sortmask]
    lsd_stokesierr = np.array(lsd_stokesierr)[sortmask]
    lsd_pol = np.array(lsd_pol)[sortmask]
    lsd_polerr = np.array(lsd_polerr)[sortmask]
    lsd_null = np.array(lsd_null)[sortmask]
    # ----------------------------------------------------------------------
    # combine mask
    lsdmask = np.zeros(len(lsd_wave), dtype=bool)
    # loop over spectral ranges to select only spectral regions of interest
    for it in range(len(fwave_lower)):
        # create wavelength mask to limit wavelength range
        wavemask = lsd_wave > fwave_lower[it]
        wavemask &= lsd_wave < fwave_upper[it]
        # add to lsdmask
        lsdmask |= wavemask
    # ----------------------------------------------------------------------
    # apply mask to lsd data
    lsd_wave = lsd_wave[lsdmask]
    lsd_stokesi = lsd_stokesi[lsdmask]
    lsd_stokesierr = lsd_stokesierr[lsdmask]
    lsd_pol = lsd_pol[lsdmask]
    lsd_polerr = lsd_polerr[lsdmask]
    lsd_null = lsd_null[lsdmask]
    # ----------------------------------------------------------------------
    # return data
    return (owlfilename, lsd_wave, lsd_stokesi, lsd_stokesierr, lsd_pol,
            lsd_polerr, lsd_null)


def lsd_analysis(lsd_wave, lsd_stokesi, lsd_stokesierr, lsd_pol, lsd_polerr,
                 lsd_null, wavec, depths, weight, vinit, vfinal, npoints,
                 nparams):
    # create velocity vector for output LSD profile
    velocities = np.linspace(vinit, vfinal, npoints)
    # ----------------------------------------------------------------------
    # create line pattern matrix for flux LSD
    mmf, mmp = line_pattern_matrix(lsd_wave, wavec, depths, weight, velocities)
    # ----------------------------------------------------------------------
    # calculate flux LSD profile
    stokesi = calculate_lsd_profile(lsd_stokesi, lsd_stokesierr,
                                    velocities, mmf, normalize=False)
    # ----------------------------------------------------------------------
    # fit gaussian to the measured flux LSD profile
    out = fit_gauss_lsd_profile(velocities, stokesi)
    stokesi_model, fit_rv, fit_resol = out
    # ----------------------------------------------------------------------
    # calculate polarimetry LSD profile
    stokes_vqu = calculate_lsd_profile(lsd_pol, lsd_polerr, velocities, mmp,
                                       nparams)
    # ----------------------------------------------------------------------
    # calculate null polarimetry LSD profile
    null = calculate_lsd_profile(lsd_null, lsd_polerr, velocities, mmp,
                                 nparams)
    # ----------------------------------------------------------------------
    # calculate statistical quantities
    # for pol
    pol_mean = mp.nanmean(lsd_pol)
    pol_std = mp.nanstd(lsd_pol)
    pol_median = mp.nanmedian(lsd_pol)
    pol_medabsdev = mp.nanmedian(abs(lsd_pol - pol_median))
    # for stokesi
    stokesvqu_mean = mp.nanmean(stokes_vqu)
    stokesvqu_std = mp.nanstd(stokes_vqu)
    # for null
    null_mean = mp.nanmean(null)
    null_std = mp.nanstd(null)
    # return all lsd values
    return (velocities, stokesi, stokesi_model, fit_rv, fit_resol, pol_mean,
            pol_std, pol_median, pol_medabsdev, stokes_vqu, stokesvqu_mean,
            stokesvqu_std, null, null_mean, null_std)


def line_pattern_matrix(wl, wlc, depth, weight, vels):
    """
    Function to calculate the line pattern matrix M given in Eq (4) of paper
    Donati et al. (1997), MNRAS 291, 658-682

    :param wl: numpy array (1D), input wavelength data (size n = spectrum size)
    :param wlc: numpy array (1D), central wavelengths (size = number of lines)
    :param depth: numpy array (1D), line depths (size = number of lines)
    :param weight: numpy array (1D), line polar weights (size = number of lines)
    :param vels: numpy array (1D), , LSD profile velocity vector (size = m)

    :return mm, mmp
        mm: numpy array (2D) of size n x m, line pattern matrix for flux LSD.
        mmp: numpy array (2D) of size n x m, line pattern matrix for polar LSD.
    """
    # set number of points and velocity (km/s) limits in LSD profile
    mnum, vinit, vfinal = len(vels), vels[0], vels[-1]
    # set number of spectral points
    num = len(wl)
    # initialize line pattern matrix for flux LSD
    mmf = np.zeros((num, mnum))
    # initialize line pattern matrix for polar LSD
    mmp = np.zeros((num, mnum))
    # set first i=0 -> trick to improve speed
    i0 = 0
    # set values of line pattern matrix M
    for lt in range(len(wlc)):
        noi0 = True
        for it in range(i0, num):
            # Calculate line velocity: v = c Δλ / λ
            velocity = speed_of_light * (wl[it] - wlc[lt]) / wlc[lt]
            if vinit <= velocity <= vfinal:
                # below is a trick to improve speed
                if noi0:
                    # next spectral line starts with first i of previous line
                    # warning: list of CCF lines must be sorted by wavelength
                    i0 = it
                    noi0 = False
                for jt in range(mnum - 1):
                    if vels[jt] <= velocity < vels[jt + 1]:
                        mmp[it][jt] += weight[lt]
                        mmf[it][jt] += depth[lt]
                        if mmf[it][jt] > 1.0:
                            mmf[it][jt] = 1.0
                        break
            elif velocity > vfinal:
                break
    # return the line pattern matrix for flux and for polar
    return mmf, mmp


def calculate_lsd_profile(flux, fluxerr, vels, mm, normalize=False,
                          nparams=None):
    """
    Function to calculate the LSD profile Z given in Eq (4) of paper
    Donati et al. (1997), MNRAS 291, 658-682

    :param wl: numpy array (1D), input wavelength data (size = n)
    :param flux: numpy array (1D), input flux or polarimetry data (size = n)
    :param fluxerr: numpy array (1D), input flux or polarimetry error data
                    (size = n)
    :param vels: numpy array (1D), , LSD profile velocity vector (size = m)
    :param mm: numpy array (2D) of size n x m, line pattern matrix for LSD.
    :param normalize: bool, to calculate a continuum and normalize profile

    :return Z: numpy array (1D) of size m, LSD profile.
    """
    # set number of spectral points
    # First calculate transpose of M
    mmt = np.matrix.transpose(mm)
    # Initialize matrix for dot product between MT . S^2
    mmt_x_s2 = np.zeros_like(mmt)
    # Then calculate dot product between MT . S^2, where S^2=covariance matrix
    for j in range(np.shape(mmt)[0]):
        mmt_x_s2[j] = mmt[j] / fluxerr ** 2
    # calculate autocorrelation, i.e., MT . S^2 . M
    mmt_x_s2_x_mm = mmt_x_s2.dot(mm)
    # calculate the inverse of autocorrelation using numpy pinv method
    mmt_x_s2_x_mm_inv = np.linalg.pinv(mmt_x_s2_x_mm)
    # calculate cross correlation term, i.e. MT . S^2 . Y
    x_corr_term = mmt_x_s2.dot(flux)
    # calculate velocity profile
    zz = mmt_x_s2_x_mm_inv.dot(x_corr_term)
    # recover last point
    zz[-1] = np.nanmedian(zz[-6:-2])
    # normalize if required
    if normalize and nparams is not None:
        # add x and y to nparams
        nparams['x'] = vels
        nparams['y'] = zz
        # calculate continuum of LSD profile to remove trend
        cont_z, xbin, ybin = mp.continuum(**nparams)
        # calculate normalized and detrended LSD profile
        zz /= cont_z
    # return the lsd profile
    return zz


def gauss_function(x, a, x0, sigma):
    return a * np.exp(-(x - x0) ** 2 / (2. * sigma ** 2))


def fit_gauss_lsd_profile(vels, zz):
    """
        Function to fit gaussian to LSD Stokes I profile.

        :param vels: numpy array (1D), input velocity data
        :param zz: numpy array (1D), input LSD profile data

        :return z_gauss, RV, resolving_power:
            z_gauss: numpy array (1D), gaussian fit to LSD profile (same size
                    as input vels and Z)
            RV: float, velocity of minimum obtained from gaussian fit
            resolving_power: float, spectral resolving power calculated from
                            sigma of gaussian fit
        """
    # obtain velocity at minimum, amplitude, and sigma for initial guess
    rvel = vels[np.argmin(zz)]
    amplitude = 1.0 - np.min(zz)
    resolving_power = 50000.0
    sig = speed_of_light / (resolving_power * mp.fwhm())
    # get inverted profile
    z_inv = 1.0 - zz
    # fit gaussian profile
    guess = [amplitude, rvel, sig]
    # noinspection PyTypeChecker
    popt, pcov = curve_fit(gauss_function, vels, z_inv, p0=guess)
    # initialize output profile vector
    z_gauss = np.zeros_like(vels)
    # loop around velocities
    for i in range(len(z_gauss)):
        # calculate gaussian model profile
        z_gauss[i] = gauss_function(vels[i], *popt)
    # invert fit profile
    z_gauss = 1.0 - z_gauss
    # calculate full width at half maximum (fwhm)
    fwhm = mp.fwhm() * popt[2]
    # calculate resolving power from mesasured fwhm
    resolving_power = speed_of_light / fwhm
    # set radial velocity directly from fitted v_0
    rv = popt[1]
    # return z_gauss, RV, resolving_power
    return z_gauss, rv, resolving_power


def add_outputs(lprops, func_name, do_lsd, wl_lower, wl_upper, min_depth,
                vinit, vfinal, normalize, nbinsize1, noverlap1, nsigclip1,
                nwindow1, nmode1, nlfit1, npoints, nbinsize2, noverlap2,
                nsigclip2, nwindow2, nmode2, nlfit2):
    # add constants
    lprops['LSD_ANALYSIS'] = do_lsd
    lprops['LSD_WL_LOWER'] = wl_lower
    lprops['LSD_WL_UPPER'] = wl_upper
    lprops['LSD_MIN_LINEDEPTH'] = min_depth
    lprops['LSD_VINIT'] = vinit
    lprops['LSD_VFINAL'] = vfinal
    lprops['LSD_NORM'] = normalize
    lprops['LSD_NBIN1'] = nbinsize1
    lprops['LSD_NOVERLAP1'] = noverlap1
    lprops['LSD_NSIGCLIP1'] = nsigclip1
    lprops['LSD_NWINDOW1'] = nwindow1
    lprops['LSD_NMODE1'] = nmode1
    lprops['LSD_NLFIT1'] = nlfit1
    lprops['LSD_NPOINTS'] = npoints
    lprops['LSD_NBIN2'] = nbinsize2
    lprops['LSD_NOVERLAP2'] = noverlap2
    lprops['LSD_NSIGCLIP2'] = nsigclip2
    lprops['LSD_NWINDOW2'] = nwindow2
    lprops['LSD_NMODE2'] = nmode2
    lprops['LSD_NLFIT2'] = nlfit2
    # set sources
    keys = ['LSD_ANALYSIS', 'LSD_WL_LOWER', 'LSD_WL_UPPER',
            'LSD_MIN_LINEDEPTH', 'LSD_VINIT', 'LSD_VFINAL',
            'LSD_NORM', 'LSD_NBIN1', 'LSD_NOVERLAP1',
            'LSD_NSIGCLIP1', 'LSD_NWINDOW1', 'LSD_NMODE1',
            'LSD_NLFIT1', 'LSD_NPOINTS', 'LSD_NBIN2',
            'LSD_NOVERLAP2', 'LSD_NSIGCLIP2', 'LSD_NWINDOW2',
            'LSD_NMODE2', 'LSD_NLFIT2']
    lprops.set_sources(keys, func_name)
    # return lprops
    return lprops


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

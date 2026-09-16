#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Polarimetry science functions

Pure numerical routines for computing degree of polarization (difference
and ratio methods), Stokes I intensity, continuum removal/normalization
and cleaning of polarimetry data. These functions do not load APERO
profiles or depend on apero-drs.

Created on 2026-09-14

@author: cook
"""
import warnings
from typing import Dict, List, Tuple

import numpy as np
from scipy import interpolate

from aperocore.base import base
from aperocore import math as mp

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.polar.polar_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

PolarReturn = Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]


# =============================================================================
# Define functions
# =============================================================================
def polarimetry_diff_method(data: Dict[str, np.ndarray],
                            errdata: Dict[str, np.ndarray],
                            nexp: int) -> PolarReturn:
    """
    Calculate polarimetry using the difference method as described in the
    paper: Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)

    :param data: dict, maps 'A_{exp}'/'B_{exp}' (exp = 1..nexp) to the
                 e2ds flux data for that fiber/exposure
    :param errdata: dict, maps 'A_{exp}'/'B_{exp}' to the e2ds flux error
                    data for that fiber/exposure
    :param nexp: int, the number of polarimetry exposures (2 or 4)

    :return: tuple, 1. numpy array (2D), degree of polarization, 2. numpy
             array (2D), error of the degree of polarization, 3. numpy
             array (2D), 1st null polarization, 4. numpy array (2D), 2nd
             null polarization

    :raises ValueError: if nexp is not 2 or 4
    """
    nexp = float(nexp)
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    data_shape = data['A_1'].shape
    pol_arr = np.zeros(data_shape)
    pol_err_arr = np.zeros(data_shape)
    null1_arr = np.zeros(data_shape)
    null2_arr = np.zeros(data_shape)
    # storage
    gg, gvar = [], []
    # loop around exposures
    for exp in range(1, int(nexp) + 1):
        # get exposure names
        a_exp = 'A_{0}'.format(exp)
        b_exp = 'B_{0}'.format(exp)
        # ---------------------------------------------------------------------
        # STEP 1 - calculate the quantity Gn (Eq #12-14 on page 997 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        part1 = data[a_exp] - data[b_exp]
        part2 = data[a_exp] + data[b_exp]
        gg.append(part1 / part2)

        # Calculate the variances for fiber A and B:
        a_var = errdata[a_exp] ** 2
        b_var = errdata[b_exp] ** 2

        # ---------------------------------------------------------------------
        # STEP 2 - calculate the quantity g_n^2 (Eq #A4 on page 1013 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        nomin = 2.0 * data[a_exp] * data[b_exp]
        denom = (data[a_exp] + data[b_exp]) ** 2.0
        factor1 = (nomin / denom) ** 2.0
        a_var_part = a_var / (data[a_exp] ** 2)
        b_var_part = b_var / (data[b_exp] ** 2)
        gvar.append(factor1 * (a_var_part + b_var_part))

    # if we have 4 exposures
    if nexp == 4:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Dm (Eq #18 on page 997 of
        #          Bagnulo et al. 2009 paper) and the quantity Dms with
        #          exposures 2 and 4 swapped, m being the pair of exposures
        #          Ps. Notice that SPIRou design is such that the angles of
        #          the exposures that correspond to different angles of the
        #          retarder are obtained in the order (1)->(2)->(4)->(3),
        #          which explains the swap between G[3] and G[2].
        # -----------------------------------------------------------------
        d1, d2 = gg[0] - gg[1], gg[3] - gg[2]
        d1s, d2s = gg[0] - gg[2], gg[3] - gg[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the degree of polarization for Stokes
        #          parameter (Eq #19 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol_arr = (d1 + d2) / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the first NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        null1_arr = (d1 - d2) / nexp
        # -----------------------------------------------------------------
        # STEP 6 - calculate the second NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        null2_arr = (d1s - d2s) / nexp
        # -----------------------------------------------------------------
        # STEP 7 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1] + gvar[2] + gvar[3]
        pol_err_arr = np.sqrt(sum_of_gvar / (nexp ** 2.0))

    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Dm
        #          (Eq #18 on page 997 of Bagnulo et al. 2009) and
        #          the quantity Dms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        d1 = gg[0] - gg[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the degree of polarization
        #          (Eq #19 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol_arr = d1 / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1]
        pol_err_arr = np.sqrt(sum_of_gvar / (nexp ** 2.0))

    # else we have insufficient data (should not get here)
    else:
        emsg = 'nexp={0} not supported for polarimetry calculations'
        raise ValueError(emsg.format(nexp))
    # -------------------------------------------------------------------------
    return pol_arr, pol_err_arr, null1_arr, null2_arr


def polarimetry_ratio_method(data: Dict[str, np.ndarray],
                             errdata: Dict[str, np.ndarray],
                             nexp: int) -> PolarReturn:
    """
    Calculate polarimetry using the ratio method as described in the
    paper: Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)

    :param data: dict, maps 'A_{exp}'/'B_{exp}' (exp = 1..nexp) to the
                 e2ds flux data for that fiber/exposure
    :param errdata: dict, maps 'A_{exp}'/'B_{exp}' to the e2ds flux error
                    data for that fiber/exposure
    :param nexp: int, the number of polarimetry exposures (2 or 4)

    :return: tuple, 1. numpy array (2D), degree of polarization, 2. numpy
             array (2D), error of the degree of polarization, 3. numpy
             array (2D), 1st null polarization, 4. numpy array (2D), 2nd
             null polarization

    :raises ValueError: if nexp is not 2 or 4
    """
    nexp = float(nexp)
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    data_shape = data['A_1'].shape
    pol_arr = np.zeros(data_shape)
    pol_err_arr = np.zeros(data_shape)
    null1_arr = np.zeros(data_shape)
    null2_arr = np.zeros(data_shape)
    # storage
    flux_ratio, var_term = [], []
    # loop around exposures
    for exp in range(1, int(nexp) + 1):
        # get exposure names
        a_exp = 'A_{0}'.format(exp)
        b_exp = 'B_{0}'.format(exp)
        # ---------------------------------------------------------------------
        # STEP 1 - calculate ratio of beams for each exposure
        #          (Eq #12 on page 997 of Bagnulo et al. 2009 )
        # ---------------------------------------------------------------------
        flux_ratio.append(data[a_exp] / data[b_exp])
        # Calculate the variances for fiber A and B:
        a_var = errdata[a_exp] ** 2
        b_var = errdata[b_exp] ** 2
        # ---------------------------------------------------------------------
        # STEP 2 - calculate the error quantities for Eq #A10 on page 1014 of
        #          Bagnulo et al. 2009
        # ---------------------------------------------------------------------
        var_term_part1 = a_var / (data[a_exp] ** 2)
        var_term_part2 = b_var / (data[b_exp] ** 2)
        var_term.append(var_term_part1 + var_term_part2)

    # if we have 4 exposures
    if nexp == 4:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        #          Ps. Notice that SPIRou design is such that the angles of
        #          the exposures that correspond to different angles of the
        #          retarder are obtained in the order (1)->(2)->(4)->(3),which
        #          explains the swap between flux_ratio[3] and flux_ratio[2].
        # -----------------------------------------------------------------
        r1, r2 = flux_ratio[0] / flux_ratio[1], flux_ratio[3] / flux_ratio[2]
        r1s, r2s = flux_ratio[0] / flux_ratio[2], flux_ratio[3] / flux_ratio[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rr = (r1 * r2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol_arr = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the quantity RN1
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rn1 = (r1 / r2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 7 - calculate the first NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        null1_arr = (rn1 - 1.0) / (rn1 + 1.0)
        # -----------------------------------------------------------------
        # STEP 8 - calculate the quantity RN2
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rn2 = (r1s / r2s) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 9 - calculate the second NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        null2_arr = (rn2 - 1.0) / (rn2 + 1.0)
        # -----------------------------------------------------------------
        # STEP 10 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            numer_part1 = (r1 * r2) ** (1.0 / 2.0)
            denom_part1 = ((r1 * r2) ** (1.0 / 4.0) + 1.0) ** 4.0
        part1 = numer_part1 / (denom_part1 * 4.0)
        sumvar = var_term[0] + var_term[1] + var_term[2] + var_term[3]
        pol_err_arr = np.sqrt(part1 * sumvar)

    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        r1 = flux_ratio[0] / flux_ratio[1]

        # -----------------------------------------------------------------
        # STEP 4 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        rr = r1 ** (1.0 / nexp)

        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol_arr = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        # numer_part1 = R1
        denom_part1 = ((r1 ** 0.5) + 1.0) ** 4.0
        part1 = r1 / denom_part1
        sumvar = var_term[0] + var_term[1]
        pol_err_arr = np.sqrt(part1 * sumvar)

    # else we have insufficient data (should not get here)
    else:
        emsg = 'nexp={0} not supported for polarimetry calculations'
        raise ValueError(emsg.format(nexp))
    # -------------------------------------------------------------------------
    return pol_arr, pol_err_arr, null1_arr, null2_arr


def calculate_stokes_i(data: Dict[str, np.ndarray],
                       errdata: Dict[str, np.ndarray],
                       nexp: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate the Stokes I total intensity

    :param data: dict, maps 'A_{exp}'/'B_{exp}' (exp = 1..nexp) to the
                 e2ds flux data for that fiber/exposure
    :param errdata: dict, maps 'A_{exp}'/'B_{exp}' to the e2ds flux error
                    data for that fiber/exposure
    :param nexp: int, the number of polarimetry exposures

    :return: tuple, 1. numpy array (2D), the Stokes I total flux, 2. numpy
             array (2D), the Stokes I error
    """
    nexp = float(nexp)
    # storage for flux and variance
    flux, var = [], []
    # loop around exposure
    for exp in range(1, int(nexp) + 1):
        # get exposure names
        a_exp = 'A_{0}'.format(exp)
        b_exp = 'B_{0}'.format(exp)
        # Calculate sum of fluxes from fibers A and B
        flux_ab = data[a_exp] + data[b_exp]
        # Save A+B flux for each exposure
        flux.append(flux_ab)
        # Calculate the variances for fiber A+B
        #    -> varA+B = sigA * sigA + sigB * sigB
        var_ab = errdata[a_exp] ** 2 + errdata[b_exp] ** 2
        # Save varAB = sigA^2 + sigB^2, ignoring cross-correlated terms
        var.append(var_ab)
    # Sum fluxes and variances from different exposures
    stokesi_arr = np.sum(flux, axis=0)
    stokesierr_arr = np.sum(var, axis=0)
    # Calcualte errors -> sigma = sqrt(variance)
    stokesierr_arr = np.sqrt(stokesierr_arr)
    # return the Stokes I intensity and its error
    return stokesi_arr, stokesierr_arr


def remove_continuum_polarization(wldata: np.ndarray, pol: np.ndarray,
                                  stokesi: np.ndarray, wavemap: np.ndarray,
                                  cont_pol: np.ndarray, reddest_thres: float
                                  ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove the continuum polarization

    :param wldata: numpy array (1D), flatten polarimetric x data
    :param pol: numpy array (2D), e2ds degree of polarization data
    :param stokesi: numpy array (2D), e2ds Stokes I data
    :param wavemap: numpy array (2D), e2ds wavelength data
    :param cont_pol: numpy array (1D), e2ds continuum polarization data
    :param reddest_thres: float, the reddest wavelength threshold to keep

    :return: tuple, 1. numpy array (2D), the updated degree of
             polarization, 2. numpy array (2D), the continuum degree of
             polarization per order
    """
    # get the shape of pol
    ydim, xdim = pol.shape
    # initialize continuum empty array
    order_cont_pol = np.full((ydim, xdim), np.nan)
    # ---------------------------------------------------------------------
    # interpolate and remove continuum (across orders)
    # loop around order data
    for order_num in range(ydim):
        # remove the reddest pixels
        ordkeep = wavemap[order_num] < reddest_thres
        ordkeep &= np.isfinite(pol[order_num])
        ordkeep &= np.isfinite(stokesi[order_num])
        ordkeep &= stokesi[order_num] > 0
        # deal with no values to keep
        if np.sum(ordkeep) == 0:
            # set all other polar values to NaN
            pol[order_num][~ordkeep] = np.nan
            continue
        # get wavelengths for current order
        ordwave = wavemap[order_num][ordkeep]
        # get polarimetry for current order
        ordpol = pol[order_num][ordkeep]
        # get wavelength at edges of order
        wl0, wlf = ordwave[0], ordwave[-1]
        # create mask to get only continuum data within wavelength range
        wlmask = (wldata >= wl0) & (wldata <= wlf)
        # get continuum data within order range
        wl_cont = wldata[wlmask]
        pol_cont = cont_pol[wlmask]
        # interpolate points applying a cubic spline to the continuum data
        pol_interp = interpolate.interp1d(wl_cont, pol_cont, kind='cubic')
        # create continuum vector at same wavelength sampling as polar data
        cont_vector = pol_interp(ordwave)
        # save continuum with the same shape as input pol
        order_cont_pol[order_num][ordkeep] = cont_vector
        # remove continuum from data
        ordpol = ordpol - cont_vector
        # update pol array
        pol[order_num][ordkeep] = ordpol
        # set all other polar values to NaN
        pol[order_num][~ordkeep] = np.nan
    # -------------------------------------------------------------------------
    return pol, order_cont_pol


def normalize_stokes_i(wldata: np.ndarray, pol: np.ndarray,
                       stokesi: np.ndarray, stokesierr: np.ndarray,
                       wavemap: np.ndarray, cont_flux: np.ndarray,
                       reddest_thres: float
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Normalize Stokes I by the continuum flux

    :param wldata: numpy array (1D), flatten polarimetric x data
    :param pol: numpy array (2D), e2ds degree of polarization data
    :param stokesi: numpy array (2D), e2ds Stokes I data
    :param stokesierr: numpy array (2D), e2ds Stokes I error data
    :param wavemap: numpy array (2D), e2ds wavelength data
    :param cont_flux: numpy array (1D), e2ds continuum flux data
    :param reddest_thres: float, the reddest wavelength threshold to keep

    :return: tuple, 1. numpy array (2D), the normalized Stokes I data,
             2. numpy array (2D), the normalized Stokes I error data,
             3. numpy array (2D), the flux continuum per order
    """
    # get the shape of pol
    ydim, xdim = stokesi.shape
    # initialize continuum empty array
    order_cont_flux = np.full(stokesi.shape, np.nan)
    # ---------------------------------------------------------------------
    # interpolate and remove continuum (across orders)
    # loop around order data
    for order_num in range(ydim):
        # remove the reddest pixels
        ordkeep = wavemap[order_num] < reddest_thres
        ordkeep &= np.isfinite(pol[order_num])
        ordkeep &= np.isfinite(stokesi[order_num])
        ordkeep &= stokesi[order_num] > 0
        # deal with no values to keep
        if np.sum(ordkeep) == 0:
            # set all other polar values to NaN
            stokesi[order_num][~ordkeep] = np.nan
            stokesierr[order_num][~ordkeep] = np.nan
            continue
        # get wavelengths for current order
        ordwave = wavemap[order_num][ordkeep]
        # get wavelength at edges of order
        wl0, wlf = ordwave[0], ordwave[-1]
        # get polarimetry for current order
        flux = stokesi[order_num][ordkeep]
        fluxerr = stokesierr[order_num][ordkeep]
        # create mask to get only continuum data within wavelength range
        wlmask = (wldata >= wl0) & (wldata <= wlf)
        # get continuum data within order range
        wl_cont = wldata[wlmask]
        flux_cont = cont_flux[wlmask]
        # interpolate points applying a cubic spline to the continuum data
        flux_interp = interpolate.interp1d(wl_cont, flux_cont, kind='cubic')
        # create continuum vector at same wavelength sampling as polar data
        _continuum = flux_interp(ordwave)
        # save continuum with the same shape as input pol
        order_cont_flux[order_num][ordkeep] = _continuum
        # normalize stokes I by the continuum
        stokesi[order_num][ordkeep] = flux / _continuum
        stokesi[order_num][~ordkeep] = np.nan
        # normalize stokes I by the continuum
        stokesierr[order_num][ordkeep] = fluxerr / _continuum
        stokesierr[order_num][~ordkeep] = np.nan
    # -------------------------------------------------------------------------
    return stokesi, stokesierr, order_cont_flux


CleanPolarReturn = Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray,
                        np.ndarray, np.ndarray, np.ndarray, np.ndarray,
                        np.ndarray]


def clean_polarimetry_data(wavemap: np.ndarray, stokesi: np.ndarray,
                           stokesierr: np.ndarray, pol: np.ndarray,
                           polerr: np.ndarray, null1: np.ndarray,
                           null2: np.ndarray, cont_pol: np.ndarray,
                           cont_flux: np.ndarray, sigclip: bool = False,
                           nsig: int = 3, overwrite: bool = False
                           ) -> CleanPolarReturn:
    """
    Clean polarimetry data by removing non-finite values (and, optionally,
    sigma-clipping the polarization values), sorted by wavelength

    :param wavemap: numpy array (2D), wavelength data
    :param stokesi: numpy array (2D), Stokes I data
    :param stokesierr: numpy array (2D), errors of Stokes I
    :param pol: numpy array (2D), degree of polarization data
    :param polerr: numpy array (2D), errors of degree of polarization
    :param null1: numpy array (2D), 1st null polarization
    :param null2: numpy array (2D), 2nd null polarization
    :param cont_pol: numpy array (2D), per-order continuum polarization
    :param cont_flux: numpy array (2D), per-order continuum flux
    :param sigclip: bool, if True also sigma clip the polarization values
    :param nsig: int, the number of sigmas to clip at
    :param overwrite: bool, if True updates the original (2D) arrays with
                      NaNs where values are cleaned/sigma-clipped

    :return: tuple of 1D numpy arrays (sorted by wavelength): clean
             wavemap, clean Stokes I, clean Stokes I error, clean
             polarization, clean polarization error, clean null1, clean
             null2, clean continuum polarization, clean continuum flux
    """
    # -------------------------------------------------------------------------
    # get shape
    ydim, xdim = pol.shape
    # -------------------------------------------------------------------------
    # store clean data
    clean_wavemap = []
    clean_stokesi, clean_stokesierr = [], []
    clean_pol, clean_polerr = [], []
    clean_null1, clean_null2 = [], []
    clean_cont_pol, clean_cont_flux = [], []
    # -------------------------------------------------------------------------
    # loop over each order
    for order_num in range(ydim):
        # mask NaN values
        mask = np.isfinite(stokesi[order_num])
        mask &= np.isfinite(stokesierr[order_num])
        mask &= np.isfinite(pol[order_num]) & np.isfinite(polerr[order_num])
        mask &= np.isfinite(null1[order_num]) & np.isfinite(null2[order_num])
        # make values where stokes I is positive
        mask &= stokesi[order_num] > 0
        # ---------------------------------------------------------------------
        # if user wants to sigma clip do add the sigma clip to mask
        if sigclip:
            # calcualte meidan of the polar array
            median_pol = mp.nanmedian(pol[order_num][mask])
            # calculate the median sigma
            meddiff = pol[order_num][mask] - median_pol
            mad = mp.inv_normal_fraction()
            medsig_pol = mp.nanmedian(np.abs(meddiff)) / mad
            # add this to mask
            mask &= pol[order_num] > (median_pol - (nsig * medsig_pol))
            mask &= pol[order_num] < (median_pol + (nsig * medsig_pol))
        # ---------------------------------------------------------------------
        # append this cleaned data on to our clean storage
        # do this as lists (more efficient than numpy)
        clean_wavemap += list(wavemap[order_num][mask])
        clean_stokesi += list(stokesi[order_num][mask])
        clean_stokesierr += list(stokesierr[order_num][mask])
        clean_pol += list(pol[order_num][mask])
        clean_polerr += list(polerr[order_num][mask])
        clean_null1 += list(null1[order_num][mask])
        clean_null2 += list(null2[order_num][mask])
        clean_cont_pol += list(cont_pol[order_num][mask])
        clean_cont_flux += list(cont_flux[order_num][mask])
        # deal with updating original arrays
        if overwrite:
            wavemap[order_num][~mask] = np.nan
            pol[order_num][~mask] = np.nan
            polerr[order_num][~mask] = np.nan
            stokesi[order_num][~mask] = np.nan
            stokesierr[order_num][~mask] = np.nan
            null1[order_num][~mask] = np.nan
            null2[order_num][~mask] = np.nan
    # -------------------------------------------------------------------------
    # sort by wavelength (or pixel number)
    sortmask = np.argsort(clean_wavemap)
    # return the sorted 1D clean arrays
    return (np.array(clean_wavemap)[sortmask],
           np.array(clean_stokesi)[sortmask],
           np.array(clean_stokesierr)[sortmask],
           np.array(clean_pol)[sortmask],
           np.array(clean_polerr)[sortmask],
           np.array(clean_null1)[sortmask],
           np.array(clean_null2)[sortmask],
           np.array(clean_cont_pol)[sortmask],
           np.array(clean_cont_flux)[sortmask])

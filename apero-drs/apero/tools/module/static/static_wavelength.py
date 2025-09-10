#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2025-06-02 at 08:50

@author: artigau

===============================================================================
Code Steps (matches main code steps):
===============================================================================
    1. Change to working directory.
    2. Load and filter the Uranium-Neon line catalog.
    3. Deduplicate lines, keeping only the brightest within 20 km/s.
    4. Define function to get approximate wavelength for an order.
    5. Load hollow cathode (HC) and Fabry-Perot (FP) spectra.
    6. Prepare order list (start from middle order and alternate outwards).
    7. Initialize cavity fit and bookkeeping arrays.
    8. If enough previous solutions exist, robustly fit the cavity using all orders.
    9. Check for integer offset in cavity numbering and correct if needed.
    10. Fill missing values and robustly filter orders for cavity fit.
    11. Final robust fit to the cavity using all FP data and user validation.
    12. Main loop over orders to build wavelength solution:
        a. Extract 1D spectrum for this order.
        b. Find the NLINES brightest HC lines in this order.
        c. Find Fabry-Perot peaks for this order.
        d. Estimate the step between FP peaks and fit a polynomial to it.
        e. Normalize the step size to integer multiples of the fit.
        f. Assign a running index to each FP peak (cavity order).
        g. Remove outliers in the FP peak sequence.
        h. Create a synthetic spectrum with spikes at the HC line positions.
        i. Get the approximate wavelength range for this order.
        j. Estimate the range of possible FP cavity orders for this order.
        k. Try all possible FP cavity order guesses and find the best alignment.
        l. Normalize the nvalid2 array for plotting.
        m. Plot the results and ask the user for validation.
        n. If user accepts, save the wavelength solution and pickle.
    13. Build the final 2D wavelength solution for all orders:
        a. For each order, fit a Chebyshev polynomial to the wavelength solution.
        b. Smooth the Chebyshev coefficients across orders to remove outliers.
        c. For each order, compute the final wavelength solution and store coefficients in header.
    14. Save the final wavelength solution to a FITS file.
    15. Save the cavity fit coefficients to a file.
    16. Plot the final wavelength solution for all orders.
===============================================================================
"""
import os
import glob
import pickle
from typing import Any, Dict, Literal, List, Tuple
import numpy as np

from astropy.table import Table
from astropy import units as uu

from astroquery.vizier import Vizier

from aperocore.core import drs_log
from aperocore.constants import load_functions
from aperocore.constants import param_functions
from aperocore.base import physics
from aperocore import math as mp

from apero.base import base as apero_base
from apero.utils import drs_data
from apero.tools.module.static import drs_static
from apero.plotting import plot_functions
from apero.science.calib import wave as wave_mod
from apero.instruments import select


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.static.static_wavelength.py'
__INSTRUMENT__ = 'None'
# Get version and author
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# speed of light
speed_of_light_kms = physics.speed_of_light_kms
speed_of_light_ms = physics.speed_of_light_ms
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get the TQDM functionality
tqdm = apero_base.TQDM
# get astropy.time
Time = apero_base.AstropyTime


# TODO:
#    - Fill in + test this code
#    - Remove REF_LEAK from usage
#    - Get wave guess from assets (need to deal with no wave guess)
#    - Get cavity from wave guess
#    - Add HC update part (from apero-utils.updates_to_drs.apero_Static_tools.hollow_cathode_update.py
#    - remove "reset" directory from assets (move assets/reset/runs to assets/runs)
#    - when resetting copy assets/runs to runs


# =============================================================================
# Define functions
# =============================================================================
def main(params: ParamDict, recipe, sparams: Dict[str, Any]):
    # -------------------------------------------------------------------------
    # sort out detector path (this is where we are saving things to)
    cal_path = str(os.path.join(params['PATH.ASSETS'],
                                params['TOOLS.STATIC.CAL_PATH']))
    if not os.path.exists(cal_path):
        os.makedirs(cal_path)
    # -------------------------------------------------------------------------
    # Step 1: Create HC catalogue
    # -------------------------------------------------------------------------
    if sparams['wavelength']['run_generate_hc_catalogue']:
        generate_hc_catagloue(params, recipe, sparams, cal_path)

    # -------------------------------------------------------------------------
    # Step 2: Run reduction for given night
    # -------------------------------------------------------------------------
    if sparams['wavelength']['run_generate_night']:
        drs_static.proxy_processing(params, recipe, sparams, cal_path)

    # -------------------------------------------------------------------------
    # Step 3: Extract HC and FP
    # -------------------------------------------------------------------------
    if sparams['wavelength']['run_generate_wave_guess']:
        generate_wave_guess(params, recipe, sparams, cal_path)

    # -------------------------------------------------------------------------
    # Update repo
    # -------------------------------------------------------------------------
    drs_static.update_repo(params, recipe, save_path=cal_path)


def generate_hc_catagloue(params: ParamDict, recipe, sparams: Dict[str, Any],
                          cal_path: str):
    # get the wavelength sparams for input hc cat
    wparams = sparams['wavelength']
    # download the hc model
    hc_model = get_hc_model(params, sparams)
    # only keep lines
    hc_table = get_hc_lines(params, recipe, sparams, hc_model)
    # -------------------------------------------------------------------------
    # remove duplicated lines (keep brightest within certain velocity range)
    # -------------------------------------------------------------------------
    # get the hc window
    hc_window = wparams['window_size']
    # get the vectors for convience
    wavemap = np.array(hc_table['wavemap'])
    flux = np.array(hc_table['wavemap'])
    # lines to keep
    keep = np.zeros_like(wavemap, dtype=bool)
    # loop around table
    for it in range(len(hc_table)):
        # work out the velocity of every line compared to this iteration
        dv = (1 - wavemap[it]/wavemap) * speed_of_light_kms
        # find all lines within our velocity window
        good = np.abs(dv) < hc_window
        # if the flux of this peak is the max in itself velocity window keep it
        if flux[it] == np.nanmax(flux[good]):
            keep[it] = True
    # cut down out hc_table
    hc_table = hc_table[keep]
    # -------------------------------------------------------------------------
    # get static file
    static_file = recipe.outputs['STATIC_HC_CAT'].newcopy(params=params)
    # construct the filename from file instance
    static_file.construct_filename(path=cal_path)
    # save static file
    drs_static.save_static_file(params, recipe, static_file,
                                desc='hotpix', data_list=[hc_table])


def generate_wave_guess(params: ParamDict, recipe, sparams: Dict[str, Any],
                        cal_path: str):

    # get static hc e2ds file
    hc_file = recipe.outputs['STATIC_HC_E2DS'].newcopy(params=params)
    # construct the filename from file instance
    hc_file.construct_filename(path=cal_path)
    # load the hc file
    hc_image = hc_file.hdulist_load('HC_E2DS')
    # -------------------------------------------------------------------------
    # get static fp e2ds file
    fp_file = recipe.outputs['STATIC_FP_E2DS'].newcopy(params=params)
    # construct the filename from file instance
    fp_file.construct_filename(path=cal_path)
    # load the hc file
    fp_image = fp_file.hdulist_load('FP_E2DS')
    # -------------------------------------------------------------------------
    # get static file
    hc_cat_file = recipe.outputs['STATIC_HC_CAT'].newcopy(params=params)
    # construct the filename from file instance
    hc_cat_file.construct_filename(path=cal_path)
    # load the hc catalogue
    hc_cat_table = hc_cat_file.hdulist_load('HC_CAT')
    # -------------------------------------------------------------------------
    # get the number of orders
    norders, nxpix = hc_image.shape

    # get the orders starting from the middle and alternating outwards
    orders = np.arange(norders)
    orders = orders[np.argsort(np.abs(orders - (norders / 2)))]

    # now we iterate several times to build the wavelength solution
    # first time we use the initial guess from the yaml file
    # then we use the previous solution to robustly fit the cavity

    for iteration in range(sparams['wavelength']['number_iterations']):

        # initialize storage arrays
        fit_cavity = [sparams['wavelength']['cavity0']]
        # ---------------------------------------------------------------------
        # Step 1: Check if we have enough previous solutions to
        #         robustly fit the cavity
        # ---------------------------------------------------------------------
        n_pickles = count_wave_pickles(sparams)
        # if we have more than 5 pickles, we can refine the cavity fit
        if n_pickles > 5:
            rout = refine_cavity_fit(params, recipe, sparams, orders)
            fit_cavity, known_orders = rout
        # ---------------------------------------------------------------------
        # Step 2: Build the wavelength solution (two iterations)
        # ---------------------------------------------------------------------
        for iteration in range(2):
            build_wavesol(params, recipe, sparams, cal_path, hc_image,
                          fp_image, hc_cat_table, iteration, fit_cavity, orders)
        # ---------------------------------------------------------------------
        # Step 3: Build the final 2D wavelength solution for all orders
        # ---------------------------------------------------------------------
        fout = build_final_wavesol(params, recipe, sparams, cal_path, hc_image,
                                    fp_image, )
        final_wave_sol, final_wave_coeffs, final_fit_cavity = fout       
        # ---------------------------------------------------------------------
        # plot the final wavelength solution for all orders
        recipe.plot('STATIC_WAVE_FINAL', 
                    final_wave_sol=final_wave_sol,
                    hc_image=hc_image, fp_image=fp_image)
        recipe.plot('SUM_STATIC_WAVE_FINAL',
                    final_wave_sol=final_wave_sol,
                    hc_image=hc_image, fp_image=fp_image)
        # ---------------------------------------------------------------------
        # Step 4: compile into packaged wavelength solution and cavity fit file
        # ---------------------------------------------------------------------
        package_wavesol(params, recipe, sparams, cal_path, 
                        hc_file, fp_file,
                        final_wave_sol, final_wave_coeffs, final_fit_cavity)


# =============================================================================
# Define main wave guess functions
# =============================================================================
def refine_cavity_fit(params: ParamDict, recipe, sparams: Dict[str, Any],
                      orders: np.ndarray):
    """
    Refine the cavity fit using all previous wavelength solutions.

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: Recipe, recipe instance
    :param sparams: dict, parameters from yaml file

    :return: list, refined cavity fit coefficients
    """

    # get the wavelength fit degree from params
    wavedegn = params['CAL.WAVE.GEN.WAVESOL_FIT_DEG']
    # get the cavity refine polyfit degree
    cavity_deg = sparams['wavelength']['cavity_refine_poly_deg']
    # get the cavity refine sigma for robust_polyfit
    cavity_sigma = sparams['wavelength']['cavity_refine_sigma']
    # degree for robust_polyfit on Chebyshev coeffs
    robust_deg = sparams['wavelength']['robust_polyfit_deg']
    # sigma cut for robust_polyfit on Chebyshev coeffs
    robust_sigma = sparams['wavelength']['robust_polyfit_sigma']
    # get the input path
    inpath = sparams['inpath'] 
    # set the cavity fit to None initially
    fit_cavity = None
    # get the wave pickle path
    wave_pickle_path = os.path.join(inpath, 'wave_pickles')
    # store the mid-wavelength for each order
    mid_wavelengths = []
    # store the known orders
    known_orders = []
    # store the wavelength center for each order (calculated)
    ord_wave_center = np.full(len(orders), np.nan)
    # store the cavity center for each order (calculated)
    ord_cavity_center = np.full(len(orders), np.nan)

    # store all fp peaks wavelength
    all_fp_wave = []
    # store all fp peaks count
    all_fp_int = []
    # store all fp peaks order number
    all_fp_order = []

    # loop around orders
    for it, order_num in enumerate(orders):
        # construct wave filenames
        wave_order_basename = f'wave_order_{order_num}.csv'
        wave_order_csvfile = os.path.join(wave_pickle_path, wave_order_basename)
        wave_order_pklfile = wave_order_csvfile.replace('.csv', '.pkl')
        # ---------------------------------------------------------------------
        # if the file does not exist, skip this order
        if not os.path.exists(wave_order_csvfile):
            msg = 'Skipping order {0} - no pickle file found'
            margs = [order_num]
            WLOG(params, '', msg.format(*margs))
            continue
        # ---------------------------------------------------------------------
        # Register that we known this order
        known_orders.append(order_num)
        # ---------------------------------------------------------------------
        # read the csv file
        wtbl = Table.read(wave_order_csvfile, format='ascii.csv')
        # get the mid-wavelength for this order
        mid_wavelengths.append(np.mean(wtbl['wavelength']))
        # load the pickle file
        dict_fp = load_wave_pickle(params, wave_order_pklfile)
        # get the vectors from the dictionary
        fp_wave = dict_fp['fp_wave']
        fp_int = dict_fp['fp_int']
        # deal with initial cavity fit (for first order)
        if fit_cavity is None:
            # rough guess for the cavity fit 
            fit_cavity_ord = [np.nanmedian(fp_wave * fp_int)]
            # update fp orders storage
            all_fp_wave += list(fp_wave)            
            all_fp_int += list(fp_int)
            all_fp_order += [order_num] * len(fp_wave)
        # if we have a fit cavity we can update fit with subsequent orders
        else:
            # set cavity to the set value
            fit_cavity_ord = list(fit_cavity)
            # get the updated cavity fit
            cavity = np.polyval(fit_cavity_ord, fp_wave)
            # store the previous fp count
            prev_fp_int = np.copy(fp_int)
            # get the new fp count
            new_fp_int = np.round(cavity / fp_wave).astype(int)
            # if any values have been updated compared to previously display
            #   a warning
            if not np.array_equal(prev_fp_int, new_fp_int):
                # log a warning message
                wmsg = 'Intensity values have changed for order {0}'
                wargs = [order_num]
                WLOG(params, 'warning', wmsg.format(*wargs))
                # set fp_int to the new values
                fp_int = new_fp_int
                # update the fp_int for this order
                dict_fp['fp_int'] = fp_int
                # -------------------------------------------------------------
                # save the updated pickle file
                save_wave_pickle(params, dict_fp, wave_order_pklfile)

            # update all orders storage
            all_fp_wave += list(fp_wave)
            all_fp_int += list(fp_int)
            all_fp_order += [order_num] * len(fp_wave)
            # convert all_fp_wave and all_fp_int to numpy arrays
            all_fp_wave_arr = np.array(all_fp_wave)
            all_fp_int_arr = np.array(all_fp_int)
            # -----------------------------------------------------------------
            # re-fit the cavity using all fp peaks
            fit_cavity_ord, _ = mp.robust_polyfit(all_fp_wave_arr, 
                                                  all_fp_wave_arr * all_fp_int_arr,
                                                  cavity_deg, cavity_sigma)
            # update the order center and cavity for this order
            ord_wave_center[it] = np.median(fp_wave)
            ord_cavity_center[it] = np.median(fp_wave * fp_int)
    # -------------------------------------------------------------------------
    # fill in missing order values and robustly  filter orders for cavity fit
    # -------------------------------------------------------------------------
    # convert known and mid to numpy arrays
    known_orders = np.array(known_orders)
    mid_wavelengths = np.array(mid_wavelengths)
    # convert all fp orders to numpy array
    all_fp_order = np.array(all_fp_order)
    # find orders that are missing
    invalid = ~np.isfinite(ord_wave_center)
    # fill in missing orders with the polyfit of the known orders
    ofits = np.polyfit(known_orders, mid_wavelengths, 2)
    ord_wave_center[invalid] = np.polyval(ofits, orders[invalid])
    ord_cavity_center[invalid] = np.polyval(fit_cavity_ord, 
                                            ord_wave_center[invalid])
    # -------------------------------------------------------------------------
    # robustly fit the known orders
    kfit, keep_orders = mp.robust_polyfit(known_orders, 1 / mid_wavelengths, 
                                          1, 3)
    # get the valid orders to keep
    valid_orders = np.in1d(all_fp_order, known_orders[keep_orders])
    # update ord wave and cavity centers
    ord_wave_center = ord_wave_center[valid_orders]
    ord_cavity_center = ord_cavity_center[valid_orders]

    # -------------------------------------------------------------------------
    # Final robust fit to the cavity using all fp data and user validation
    # -------------------------------------------------------------------------
    # convert all_fp_wave and all_fp_int to numpy arrays
    all_fp_wave_arr = np.array(all_fp_wave)
    all_fp_int_arr = np.array(all_fp_int)
    # robustly fit one final time
    fit_cavity_tmp, _ = mp.robust_polyfit(all_fp_wave_arr, 
                                          all_fp_int_arr * all_fp_wave_arr, 
                                          robust_deg, robust_sigma)
    # -------------------------------------------------------------------------
    # set up the plot kwargs
    pkwargs = dict()
    pkwargs['fit_cavity_tmp'] = fit_cavity_tmp
    pkwargs['all_fp_wave'] = all_fp_wave_arr
    pkwargs['all_fp_int'] = all_fp_int_arr
    pkwargs['all_fp_order'] = all_fp_order
    # ask the user (via a plot) whether to accept this cavity fit
    accept = plot_functions.plot_static_cav_check_plot(recipe.plot, **pkwargs)
    # -------------------------------------------------------------------------
    # print acceptance
    if accept:
        fit_cavity = fit_cavity_tmp
        msg = 'Cavity fit accepted with coefficients: {0}'
        margs = [fit_cavity]
        WLOG(params, '', msg.format(*margs))
    else:
        msg = 'Cavity fit rejected - keeping previous fit'
        WLOG(params, '', msg)
    # return fit 
    return fit_cavity


def build_wavesol(params: ParamDict, recipe, sparams: Dict[str, Any],
                  cal_path: str, hc_image: np.ndarray, fp_image: np.ndarray,
                  hc_cat_table: Table, iteration: int, fit_cavity: List[float], 
                  orders: np.ndarray):
    """
    Build the wavelength solution for all orders.
    This is done order-by-order with a user check after each order.
    Those that are accepted are saved to pickle and csv files.

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: Recipe, recipe instance
    :param sparams: dict, parameters from yaml file
    :param cal_path: str, path to calibration files
    :param hc_image: np.ndarray, 2D array of HC spectrum
    :param fp_image: np.ndarray, 2D array of FP spectrum
    :param hc_cat_table: Table, table containing the HC line catalogue
    :param iteration: int, iteration number
    :param fit_cavity: list, cavity fit coefficients
    :param orders: np.ndarray, array of order numbers to process

    :return: None, saves wavelength solutions (per order) to pickle and 
             csv files 
    """
    # get the input path
    inpath = sparams['inpath'] 
    # get wavelength parameters
    wsparams = sparams['wavelength']
    # get the number of lines to use (maximum)
    nlines = wsparams['nlines']
    # get the initial guess for the cavity length
    cavity0 = wsparams['cavity0']
    # get the fp peak step window size
    fp_peak_step_window = wsparams['fp_peak_step_window']
    # get the degree for polyfit in wave_guess/fp_pix
    fp_poly_deg = wsparams['fp_poly_deg']
    # get the minimum number of valid points to fit the step
    fp_step_valid_min = wsparams['fp_step_valid_min']
    # Number of bins for histogram in mini
    fp_step_mad_bins = wsparams['fp_step_mad_bins']
    # Range for histogram in mini
    fp_step_mad_range = wsparams['fp_step_mad_range']
    # Threshold for mini selection
    fp_step_mad_threshold = wsparams['fp_step_mad_threshold']
    # Range for integer offset search
    fp_step_offs_range = wsparams['fp_step_offs_range']
    # Step for integer offset search
    fp_step_offs_step = wsparams['fp_step_offs_step']
    # Number of sigma to blindy accept an order as valid
    nsig_accept_fp = wsparams['nsig_accept_fp']
    # get the wave pickle path
    wave_pickle_path = os.path.join(inpath, 'wave_pickles')
    # set the number of orders (from the HC E2DS file)
    norders, nbxpix = hc_image.shape

    # get the wave reference from the hc catalogue
    wave_ref0 = np.array(hc_cat_table['wavelength'])

    # loop around orders
    for order_num in orders:
        # construct wave filenames
        wave_order_basename = f'wave_order_{order_num}.csv'
        wave_order_csvfile = os.path.join(wave_pickle_path, wave_order_basename)
        wave_order_pklfile = wave_order_csvfile.replace('.csv', '.pkl')
        # ---------------------------------------------------------------------
        # if the csv file already exists we can skip this step
        if os.path.exists(wave_order_csvfile):
            msg = 'Skipping order {0} - csv file already exists'
            margs = [order_num]
            WLOG(params, '', msg.format(*margs))
        else:
            msg = 'Building wavelength solution for order {0}'
            margs = [order_num]
            WLOG(params, '', msg.format(*margs))
        # ---------------------------------------------------------------------
        # load the HC spectrum for this order
        hc_spectrum = hc_image[order_num]
        # load the FP spectrum for this order
        fp_spectrum = fp_image[order_num]
        # ---------------------------------------------------------------------
        # find the HC lines in this order
        dhc_out = detect_spectral_lines(params, sparams, hc_spectrum, 
                                        peak_kind='hc')
        hc_pix, _, hc_flux, _ = dhc_out
        # if we have more than nlines, keep only the nlines brightest
        if len(hc_pix) > nlines:
            # get the indices of the nlines brightest lines
            brightest_indices = np.argsort(hc_flux)[-nlines:]
            # keep only the nlines brightest lines
            hc_pix = hc_pix[brightest_indices]
            hc_flux = hc_flux[brightest_indices]

        # ---------------------------------------------------------------------
        # find the FP lines in this order
        dfp_out = detect_spectral_lines(params, sparams, fp_spectrum, 
                                        peak_kind='fp')
        fp_pix, fp_sigmas, fp_flux, fp_index = dfp_out
        # ---------------------------------------------------------------------
        # create a syntheric spectrum with spikes at the HC line positions
        synth_spectrum = np.zeros_like(hc_spectrum, dtype=float)
        synth_spectrum[hc_pix.astype(int)] = 1.0
        kernel = mp.gauss_function(np.arange(-5, 6), 1, 0, 1.5, 0)
        synth_spectrum += np.convolve(synth_spectrum, kernel, mode='same')
        # ---------------------------------------------------------------------
        # get the approximate wavelength range for this order
        wave0, wave_start, wave_end = get_approx_wavesol(sparams, order_num,
                                                         norders)
        # mask the catalogue to only keep lines in this wavelength range
        wmask = (wave_ref0 > wave_start) & (wave_ref0 < wave_end)
        # get the wavelengths in this order
        waveord = wave_ref0[wmask]
        # ---------------------------------------------------------------------
        # estimate the range of possible FP cavity orders for this order
        peak0_guess = get_peak0_guess(params, sparams, order_num)
        # deal with no estimate given
        if np.isnan(peak0_guess):
            istart = int(cavity0 / wave_end)
            iend = int(cavity0 / wave_start)
            step = 0.2
        else:
            istart = peak0_guess - 200
            iend = peak0_guess + 200
            step = 0.05

        # ---------------------------------------------------------------------
        # set up grid of peak position and FP numbers guesses
        peak0_guesses = np.arange(istart, iend, step)
        nvalid = np.full(len(peak0_guesses), np.nan)
        nvalid2 = np.full(len(peak0_guesses), np.nan)
        # best nvalid found
        best_nvalid = 0
        best_wave = []
        # start the storage of the best fit
        dict_fp = dict()
        dict_fp['fp_int'] = None
        dict_fp['fp_wave'] = None
        dict_fp['fp_pix'] = None
        dict_fp['peak0_guess'] = None
        # ---------------------------------------------------------------------
        # try all possible FP cavity order guesses and find the best alignment
        for it, peak0_guess in tqdm(enumerate(peak0_guesses)):
            # peak diff (guess vs measured)
            peak_diff = peak0_guess - fp_index
            # compute the guessed wavelength solution for this peak0
            wave_guess = np.polyval(fit_cavity, wave0) / peak_diff
            # fit a polynomial between guessed wavelengths and FP pixel positions
            fit = np.polyfit(wave_guess[::fp_peak_step_window],
                                 fp_pix[::fp_peak_step_window], 
                                 fp_poly_deg)
            # map reference wavelengths to pixel positions using the fit
            pix_ref = np.polyval(fit, waveord)
            # only keep lines that fall on the detector
            keep = (pix_ref > 0) & (pix_ref < nbxpix)

            # if enough valid points count how many HC lines match FP peaks
            if np.sum(keep) > fp_step_valid_min:
                pix_ref = pix_ref[keep].astype(int)
                # update the number of valid points
                nvalid[it] = np.sum(synth_spectrum[pix_ref])
            else:
                continue

            # compute a normalized metric for plotting and selection
            nvalid2[it] = nvalid[it] - np.nanmedian(nvalid[it - 11:it])

            # if this guess is promising, refine the alignment
            if nvalid[it] == 0:
                continue

            # compute pixel offsets betwen HC and FP lines
            mini = np.zeros(len(fp_pix))
            mini_wave = np.zeros(len(fp_pix))
            # loop around each fp line
            for jt in range(len(fp_pix)):
                # find the closest reference line to this FP line
                imin = np.argmin(np.abs(pix_ref - fp_pix[jt]))
                # push into the storage
                mini[jt] = pix_ref[imin] - fp_pix[jt]
                mini_wave[jt] = waveord[imin] - wave_guess[fp_index[jt]]
            # histogram the offsets to find the best alginment cluster
            hist_count, hist_bins = np.histogram(mini, bins=fp_step_mad_bins,
                                                  range=fp_step_mad_range)
            # only keep offsets that are below our mad threshold
            absdiff_hist = abs(mini - hist_bins[np.argmax(hist_count)])
            good = absdiff_hist < fp_step_mad_threshold

            # if enough lines are well-aligned fit a polynomial to the offsets
            if np.sum(good) <= fp_step_valid_min:
                continue

            # fit a polynomial to the offsets
            hc_pix2 = hc_pix[good]
            mini2 = mini[good]
            mini_wave2 = mini_wave[good]

            # if the number of valid points is not better that the best 
            #   found so far continue
            if nvalid2[it] <= best_nvalid:
                continue

            # update the best nvalid
            best_nvalid = nvalid2[it]
            # robust fit to the best-matched lines
            _, keep = mp.robust_polyfit(hc_pix2, mini_wave2, 2, 3)
            # only keep the good lines
            hc_pix2 = hc_pix2[keep]
            mini_wave2 = mini_wave2[keep]
            # final polynomal fit for wavelength solution
            best_fit = np.polyfit(hc_pix2, mini_wave2, 3)
            fp_wave = np.polyval(best_fit, fp_pix)
            # compute the cavity length from the polynomial fit
            cavity_len = np.polyval(fit_cavity, fp_wave)
            # update the fp count
            fp_int = np.array(np.round(cavity_len / fp_wave), dtype=int)
            # search for the best integer offset for FP orders
            offsets = np.arange(-fp_step_offs_range, fp_step_offs_range + 1,
                                fp_step_offs_step)
            mads = np.zeros(len(offsets))
            # load the mad values into the array
            for ioffs, off in enumerate(offsets):
                mads[ioffs] = mp.cal_med_abs_dev((fp_int + off) * fp_wave)
            # compute the best-fit wavelength solution for all pixels
            best_wave = np.polyval(best_fit, np.arange(len(hc_spectrum)))
            fp_int = fp_int + offsets[np.argmin(mads)]
            # select valid FP peaks within the fitted wavelength range
            valid = (fp_wave > np.min(mini_wave))
            valid &= (fp_wave < np.max(mini_wave))
            # only process if there are valid FP peaks
            if len(fp_wave) > 0 and len(fp_pix) > 0:
                continue
            # store the FP solution for this guess (current best guess)
            dict_fp['fp_int'] = fp_int[valid]
            dict_fp['fp_wave'] = fp_wave[valid]
            dict_fp['fp_pix'] = fp_pix[valid]
            dict_fp['peak0_guess'] = peak0_guess
        # ---------------------------------------------------------------------
        # normalize the nvalid2 array
        nvalid2 /= mp.cal_med_abs_dev(nvalid2)
        # report the max nvalid 
        msg = 'Order {0}: Nvalid[{1}]={2}'
        margs = [order_num, np.nanmax(nvalid), np.nanmax(nvalid2)]
        WLOG(params, '', msg.format(*margs))
        # ---------------------------------------------------------------------
        # deal with no solution
        if (iteration == 0) and np.nanmax(nvalid2) < nsig_accept_fp:
            msg = 'Order {0}: No valid FP solution found - skipping order'
            margs = [order_num]
            WLOG(params, 'warning', msg.format(*margs))

        # set up the plotting kwargs
        pkwargs = dict()

        # ask user for validation about this order
        accept = plot_functions.plot_static_wave_check_plot(recipe.plot,
                                                            **pkwargs)
        
        # if we are accepting this wave solution we save the dict_fp to csv
        # and dump into a pickle file
        if accept:
            # save the csv file
            wtbl = Table()
            wtbl['pixel'] = np.arange(len(best_wave))
            wtbl['wavelength'] = best_wave
            # write to csv file
            wtbl.write(wave_order_csvfile, format='ascii.csv', overwrite=True)
            # save the pickle file
            save_wave_pickle(params, dict_fp, wave_order_pklfile)


def build_final_wavesol(params: ParamDict, recipe, sparams: Dict[str, Any],
                        cal_path: str, fp_image: np.ndarray, 
                        fit_cavity: List[float]
                        ) -> Tuple[np.ndarray, np.ndarray, List[float]]:

    # For each order compute the final wavelength solution and store 
    #   coefficients in the header
    # get the wavelength fit degree from params
    wavedegn = params['CAL.WAVE.GEN.WAVESOL_FIT_DEG']
    # get the number of orders
    norders = fp_image.shape[0]
    # get the number of x pixels
    nbxpix = fp_image.shape[1]
    # get the array of x pixels (used in multiple places)
    xpixels = np.arange(nbxpix, dtype=float)
    # get the array of orders
    orders = np.arange(norders, dtype=float)

    # storage for the final wave solution
    final_wave_sol = np.full((norders, nbxpix), np.nan)
    # final wave coefficients
    final_wave_coeffs = np.full((norders, wavedegn + 1), np.nan)
    
    # store the middle pixel of fp peak
    middle_pixel_fp_peak = np.full((norders,), np.nan)
    # store the cavity middle
    cavity_middle = np.full((norders,), np.nan)


    # loop around all orders
    for order_num in range(norders):
        # construct wave filenames
        wave_order_basename = f'wave_order_{order_num}.csv'
        wave_order_csvfile = os.path.join(cal_path, wave_order_basename)
        wave_order_pklfile = wave_order_csvfile.replace('.csv', '.pkl')
        # ---------------------------------------------------------------------
        # if pickle doesn't exist continue
        if not os.path.exists(wave_order_pklfile):
            continue
        # ---------------------------------------------------------------------
        # load the pickle file
        dict_fp = load_wave_pickle(params, wave_order_pklfile)
        # get all peaks from the pickle
        fp_wave = dict_fp['fp_wave']
        fp_pix = dict_fp['fp_pix']
        fp_int = dict_fp['fp_int']

        # get the residual between the fp_wave and the poly fit to the cavity
        cavity_fit = np.polyval(fit_cavity, fp_wave)
        cavity_residual = fp_wave - (cavity_fit / np.round(cavity_fit / fp_wave))
        # get the wave from the cavity fit and the fp peak numbers
        wave_from_cavity = cavity_fit / fp_int

        # fit a polynomial from the pixel to cavity wave sol
        fit_wave = np.polyfit(fp_pix, wave_from_cavity, wavedegn)   
        # final wave is these coefficients evaluated at all pixels
        final_wave = np.polyval(fit_wave, xpixels)
        # get the coefficients as a chebyshev fit
        cheby_coeffs = mp.fit_cheby(xpixels, final_wave, wavedegn,
                                    domain=[0, nbxpix - 1])
        # store the chebyshev coeffs
        final_wave_coeffs[order_num] = cheby_coeffs
        # work out the middle wave length and push into cavtiy and pixel storage
        wave_middle = final_wave[len(final_wave) // 2]
        cavity_middle[order_num] = np.polyval(fit_cavity, wave_middle)
        middle_pixel_fp_peak[order_num] = cavity_middle[order_num] / wave_middle
    # -------------------------------------------------------------------------
    # once we have all orders robusyly fit centers
    fit_middle_fp, keep = mp.robust_polyfit(orders, middle_pixel_fp_peak, 5, 8)
    # get the residual to the middle pixel peak position
    middle_res = middle_pixel_fp_peak - np.polyval(fit_middle_fp, orders)
    # -------------------------------------------------------------------------
    # plot the final middle pixel position
    recipe.plot('STATIC_WAVE_MIDDLE', orders=orders, 
                middle_pixel_fp_peak=middle_pixel_fp_peak,
                middle_res=middle_res, keep=keep)
    recipe.plot('SUM_STATIC_WAVE_MIDDLE', orders=orders, 
                middle_pixel_fp_peak=middle_pixel_fp_peak,
                middle_res=middle_res, keep=keep)
    # ------------------------------------------------------------------------
    # For each order compute the final wavelength solution and update coeffs
    #   Start from the FP lines
    for order_num in range(norders):
        # get the lines
        dfp_out = detect_spectral_lines(params, sparams, fp_image[order_num], 
                                        peak_kind='fp')
        fp_pix, fp_sigmas, fp_flux, fp_index = dfp_out

        # beacuse the Nth peak is decreasing
        fp_index = np.max(fp_index) - fp_index
        # if our coefficients are nans we need to re-fit the coefficients
        if np.any(np.isnan(final_wave_coeffs[order_num])):
            # get valid middles
            valid = np.isfinite(cavity_middle)
            # get the valid orders
            valid_orders = orders[valid]
            # fit the cavity middles to all orders
            fit_cavity_to_order = np.polyfit(valid_orders, 
                                             cavity_middle[valid], 7)
            # re-generate the cavity 
            cavity = np.polyval(fit_cavity_to_order, order_num)
            # get the peak count
            fp_int = fp_index
        # otherwise we just use what we have from the coefficients
        else:
            # get the wave solution from the coefficients
            wave = mp.val_cheby(final_wave_coeffs[order_num], fp_pix,
                                domain=[0, nbxpix - 1])
            # re-generate the cavity 
            cavity = np.polyval(fit_cavity, order_num)
            # get the peak count
            fp_int = cavity / wave

        # ---------------------------------------------------------------------
        # get the middle fp (using a spline across )
        fp_spline = mp.iuv_spline(fp_pix, fp_int, k=1)
        middle_fp = fp_spline(nbxpix // 2)

        # get the error in fp position (based on the fit_middle_fp
        err_fp_pos = middle_fp - np.polyval(fit_middle_fp, order_num)    
        # round this to nearest peak
        fp_offset = np.round(err_fp_pos)
        # print that we found an offset
        msg = 'Order {0}: Middle FP peak offset by {1} peaks'
        margs = [order_num, fp_offset]
        WLOG(params, '', msg.format(*margs))
        # correct the fp_int for this offset
        fp_int = fp_int = fp_offset
        # loop around and iteratively fit the cavity
        for _ in range(3):
            wave = cavity / fp_int
            cavity = np.polyval(fit_cavity, wave)
        # calculate the final wave solution coefficients    
        fcoeffs = mp.fit_cheby(fp_pix, wave, wavedegn, domain=[0, nbxpix - 1])
        # update the chebyshev polynomial values
        final_wave_coeffs[order_num] = fcoeffs
        # update the final wave solution
        final_wave_sol[order_num] = mp.val_cheby(fcoeffs, xpixels,
                                                 domain=[0, nbxpix - 1])
    # -------------------------------------------------------------------------
    # return the final wave solution, the final wave coefficients and the
    # fit cavity (even though it hasn't changed)
    return final_wave_sol, final_wave_coeffs, fit_cavity


# =============================================================================
# Define worker functions
# =============================================================================
def get_hc_model(params: ParamDict, sparams: Dict[str, Any]) -> Table:
    """
    Get the HC mode using the wavelength.input_hc_cat.vizier-ref keyword
    from Vizier and save to input + wavelength.input_hc_cat.filename

    :param params: ParamDict, parameter dictionary of constants
    :param sparams: dict, parameters from yaml file
    """
    # get the wavelength sparams for input hc cat
    wparams = sparams['wavelength']['input_hc_cat']
    # get the vizier reference
    vizier_ref = wparams['vizier-ref']
    # construct the name for the downloaded hc model
    hc_model_file = os.path.join(sparams['inpath'], wparams['filename'])
    # -------------------------------------------------------------------------
    # if we already have the file don't download again
    if os.path.exists(hc_model_file):
        return Table.read(hc_model_file)
    # -------------------------------------------------------------------------
    # deal with vizier-ref being a file on disk
    if os.path.exists(vizier_ref):
        table = Table.read(vizier_ref)
    else:
        # No row limit: get all rows
        Vizier.ROW_LIMIT = -1
        # Query the entire table
        try:
            tables = Vizier.get_catalogs(vizier_ref) # type: ignore
            # get the first table
            table = tables[0]
        except Exception as e:
            # TODO: Move to language database
            emsg = 'Failed to load model: {0} from Vizier\n\t{1}: {2}'
            eargs = [vizier_ref, type(e), str(e)]
            # raise an APERO exception
            raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                      targs=eargs)
    # -------------------------------------------------------------------------
    # try to save the HC model to file
    try:
        # print that we are writing hc model file
        msg = 'Saving HC model file to: {0}'
        margs = [hc_model_file]
        WLOG(params, '', msg.format(*margs))
        # write to file
        table.write(hc_model_file, overwrite=True)
        # return tables[0]
        return table
    except Exception as e:
        # TODO: Move to language database
        emsg = 'Failed to save model: {0} to: {1}\n\t{2}: {3}'
        eargs = [vizier_ref, hc_model_file, (e), str(e)]
        # raise an APERO exception
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)


def get_hc_lines(params: ParamDict, recipe, sparams: Dict[str, Any],
                 table: Table) -> Table:
    """
    Cut down the HC model to only keep species and wavelength we are
    interested in.

    :param params: ParamDict, parameter dictionary of constants
    :param sparams: dict, parameters from yaml file
    :param table: Table, table containing HC model

    :return: Table, table containing the cut down HC model for lines we
             are interested in
    """
    # get the wavelength sparams for input hc cat
    wparams = sparams['wavelength']['input_hc_cat']
    # get the required wavelength domain
    wavemin, wavemax = wparams['wave_domain']
    # get the species we want
    species_keep = wparams['species_keep']
    # get the species column
    hc_species_col = wparams['species_col']
    # get the flux column
    hc_flux_col = wparams['flux_col']
    # get the wavelength column
    hc_wave_col = wparams['wave_col']
    # get wavelength units and convert to astropy unit
    hc_wave_unit = wparams['wave_units']
    # get the vizier reference
    vizier_ref = wparams['vizier-ref']
    # -------------------------------------------------------------------------
    try:
        wave_unit = uu.Unit(hc_wave_unit)
    except Exception as e:
        emsg = 'wavelength.input_hc_Cat.wave_units={0} invalid.\n\t{1}: {2}'
        eargs = [hc_wave_unit, type(e), str(e)]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # make sure wavelength is in nm
    try:
        if table[hc_wave_col].unit is None:
            wavemap = (table[hc_wave_col] * wave_unit).to(uu.nm).value
        else:
            wavemap = (table[hc_wave_col].to(uu.nm)).value # type: ignore
    except Exception as e:
        # TODO: Add to language database
        emsg = ('wavelength.input_hc_Cat.wave_units={0} [astropy={1}] invalid.'
                '\n\t{2}: {3}')
        eargs = [hc_wave_unit, str(wave_unit), type(e), str(e)]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # -------------------------------------------------------------------------
    # assume we don't want any lines at first
    smask = np.zeros(len(table), dtype=bool)
    # loop around species to keep from hc model
    for species in species_keep:
        # get the species as a character array
        species_arr = np.char.array(table[hc_species_col], unicode=True)
        # strip white space around species arr
        species_arr = np.char.strip(species_arr)
        # get a mask just for this species
        sp_mask = species_arr == species
        # get wavelength constraints
        sp_mask &= wavemap > wavemin
        sp_mask &= wavemap < wavemax
        # combine to full mask
        smask |= sp_mask
    # deal with no lines
    if np.sum(smask) == 0:
        # TODO: Add to language database
        emsg = ('No lines left in HC model after cut\n\tSpecies: {0}'
                '\n\tWavemin: {1} nm\n\tWavemax: {2} nm')
        eargs = [','.join(species_keep), wavemin, wavemax]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    else:
        # get static file
        hccat = recipe.outputs['STATIC_HC_CAT'].newcopy(params=params)
        stbl = hccat.hdulist['HC_CAT']
        # lets make a new table, cut down to smask, and cleaned ready for use
        outtable = stbl.create_table(wavelength=wavemap[smask],
                                     flux=table[hc_flux_col][smask],
                                     species=table[hc_species_col][smask],
                                     source=[vizier_ref] * np.sum(smask))
        # lets sort the table by wavelength column
        outtable.sort('wavelength')
        # return the new, cleaned, cut down table
        return outtable


def get_approx_wavesol(sparams: Dict[str, Any], order_num: int,
                       norders: int) -> Tuple[float, float, float]:
    """
    Calculate a very rough approximation of the wave solution
    (center and start and end) for an order - based on a linear fit
    in wavenumber

    :param sparams: dict, parameters from yaml file
    :param order_num: int, order of approximation
    :param norders: int, number of orders in total

    :return: Tuple, Guess for this order: 1. wave center, 2. start, 3. end
    """
    # get the wavelength sparams for input hc cat
    wparams = sparams['wavelength']['input_hc_cat']
    # get the required wavelength domain
    wavemin, wavemax = wparams['wave_domain']
    # get the fractional range for approximate wavelength
    wave_approx = wparams['wave_approx']

    # linear fit across orders in wavenumber
    lfit = np.polyfit([0, norders], [1/wavemin, 1/wavemax], 1)
    # the wave guess it the inverse of this fit in wavenumber
    waveguess = float(1 / np.polyval(lfit, order_num))
    # start and end points given the wave_approx size (and waveguess as center)
    wavestart = waveguess * (1 - wave_approx)
    waveend = waveguess * (1 + wave_approx)

    return waveguess, wavestart, waveend


def count_wave_pickles(sparams: Dict[str, Any]) -> int:
    """
    Count the number of wavelength solution pickles available in the
    wavelength directory.

    :param sparams: dict, parameters from yaml file

    :return: int, number of wavelength solution pickles available
    """
    # get the input path
    inpath = sparams['inpath'] 
    # get the wave pickle path
    wave_pickle_path = os.path.join(inpath, 'wave_pickles')
    # check if the path exists
    if not os.path.exists(wave_pickle_path):
        # if not, return 0
        return 0
    # list all files in the wave pickle path
    files = glob.glob(os.path.join(wave_pickle_path, 'wave_order_*.pkl'))
    # return the number of files    
    return len(files)


def detect_spectral_lines(params: ParamDict, sparams: Dict[str, Any], 
                          spectrum: np.ndarray, 
                          peak_kind: Literal['hc', 'fp'] = 'hc'
                          ) -> Tuple[np.ndarray, np.ndarray, 
                                     np.ndarray, np.ndarray]:
    """
    Detect spectral lines in a given 1D spectrum.

    This function identifies spectral lines in the input spectrum by finding 
    local maxima and fitting them with appropriate models

    :param params: ParamDict, parameter dictionary of constants
    :param sparams: dict, parameters from yaml file
    :param spectrum: np.ndarray, 1D array representing the spectrum
    :param peak_kind: str, type of peaks to detect ('hc' for hollow cathode,
                      'fp' for Fabry-Perot)
    :return: Tuple of np.ndarrays:
             - mus: Peak positions in pixel units
             - sigmas: FWHM of the peaks in pixel units
             - flux: Peak flux values
             - peak index: Running index of each peak
    """
    # set function name
    func_name = __NAME__ + '.detect_spectral_lines()'
    # print progress
    msg = '\tDetecting {0} spectral lines in spectrum'
    margs = [peak_kind]
    WLOG(params, '', msg.format(*margs))
    # copy the spectrum
    spec = np.array(spectrum, dtype=float)
    # get parameters from sparams
    fp_peak_step_poly_deg = sparams['wavelength']['fp_peak_step_poly_deg']
    fp_peak_poly_deg = sparams['wavelength']['fp_peak_poly_deg']
    # -------------------------------------------------------------------------
    # remove low frequence bacground if we are dealing with a HC spectrum
    if peak_kind == 'hc':
        spec -= mp.lowpassfilter(spec, 15)
    # -------------------------------------------------------------------------
    # clean up spectrum: set non-finite and edge values to zero
    spec[~np.isfinite(spec)] = 0
    spec[:5] = 0
    spec[-5:] = 0
    # -------------------------------------------------------------------------
    # Find local maxima (peaks) in the spectrum
    peak_mask = spec > np.roll(spec, 1)
    peak_mask &= spec > np.roll(spec, -1)
    peak_indices = np.where(peak_mask)[0]
    # -------------------------------------------------------------------------
    # storage for loop
    peak_pixels, peaks_max, fwhm_pixels = [], [], []
    # loop around peaks
    for ipeak in peak_indices:
        # get the peak index value
        peak_index = peak_indices[ipeak]
        # for hollow cathode we fit a quadratic to the peak
        if peak_kind == 'hc':
            # we isolate the values around the peak
            # 3 pixels: peak -1, peak, peak +1
            pix_id_bit = [-1, 0, 1]
            # get the start and end of this peak
            bit_start = peak_index - 1
            bit_end = peak_index + 2
            # get the flux in this peak (normalixed to the peak value)
            pix_bit = spec[bit_start:bit_end] / spec[peak_index]
            # if any values are negative we skip this peak
            if np.min(pix_bit) < 0:
                continue
            # we fit a qualdratic to the peak
            pfit = np.polyfit(pix_id_bit, pix_bit, 2)
            # calculate the fwhm of the peak from the fit
            pfwhm = 2 * np.sqrt(-0.5 / pfit[0])
            # if the fwhm is too small (<1) or too large (>5) we skip
            if pfwhm < 1 or pfwhm > 5:
                continue
            # work out the peak position
            peak_pos = -0.5 * pfit[1] / pfit[0]
            # store these peak values
            peak_pixels.append(peak_index + peak_pos)
            peaks_max.append(spec[peak_index])
            fwhm_pixels.append(pfwhm)
        # for Fabry-Perot we just take the pixel position and max value
        elif peak_kind == 'fp':
            # skip peaks on the edge
            if ipeak == 0 or ipeak == len(peak_indices) - 1:
                continue
            # work out the width of the FP peak
            width = (peak_indices[ipeak + 1] - peak_indices[ipeak - 1]) / 4
            # must be an integer
            width = int(np.round(width))
            # get the index of these pixels
            pix_id_bit = np.arange(-width, width + 1)
            # get the start and end of this peak
            bit_start = peak_index - width
            bit_end = peak_index + width + 1
            # get the flux in this peak)
            pix_bit = spec[bit_start:bit_end]
            # try to fit the peak with a gaussian
            try:
                # guess for the gaussian fit [amp, pos, sigma, offset]
                pguess = [spec[peak_index], 0, 1, 0]
                # fit a single gaussian to the peak
                pfit = mp.fitgaussian(pix_id_bit, pix_bit, guess=pguess,
                                      return_fit=False)
                # if the fit fails we skip this peak
                if pfit is None:
                    continue
                # get the fwhm from the fit
                pfwhm = mp.fwhm(pfit[2])
                # store these peak values
                peak_pixels.append(peak_index + pfit[1])
                peaks_max.append(pfit[0])
                fwhm_pixels.append(pfwhm)
            except Exception:
                # if the fit fails we skip this peak
                continue
        else:
            emsg = 'peak_kind={0} not recognised. Function = {1}'
            eargs = [peak_kind, func_name]
            raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                      targs=eargs)
    # -------------------------------------------------------------------------
    # convert to numpy arrays
    mus = np.array(peak_pixels)
    sigmas = np.array(fwhm_pixels)
    flux = np.array(peaks_max)

    # only keep peaks that are finite, non-zero, and non-negative
    valid = np.isfinite(mus) & np.isfinite(sigmas) & np.isfinite(flux)
    valid &= (sigmas > 0) & (flux > 0)
    mus = mus[valid]
    sigmas = sigmas[valid]
    flux = flux[valid]
    # sort by pixel position
    sort_order = np.argsort(mus)[::-1]
    mus = mus[sort_order]
    sigmas = sigmas[sort_order]
    flux = flux[sort_order]
    # -------------------------------------------------------------------------
    # if we have a FP then we have a bit more to do
    if peak_kind == 'fp':
        # estimate the step between FP peaks and fita  polynomial to it
        peak_step = np.diff(mus)
        # reject the first peak
        mus = mus[1:]
        flux = flux[1:]
        sigmas = sigmas[1:]
        # ---------------------------------------------------------------------
        # iteratively and robustly fit the peaks
        for _ in range(2):
            # fit a polynomial to the peak steps
            pfit, keep = mp.robust_polyfit(mus, peak_step, 
                                           fp_peak_step_poly_deg, 3)
            # cut down our arrays
            peak_step = peak_step[keep]
            mus = mus[keep]
            flux = flux[keep]
            sigmas = sigmas[keep]
        # ---------------------------------------------------------------------
        # normalize the step size to integer multiple of the fit
        step_norm = np.round(peak_step / np.polyval(pfit, mus))
        peak_step /= step_norm
        # ---------------------------------------------------------------------
        # Assign a running index to each FP peak (cavity order)
        peak_count = np.zeros(len(mus), dtype=int)
        for count in range(1, len(mus)):
            # work out the expected value of this pixel based on the fit
            count_val = np.polyval(pfit, mus[count])
            # work out the distance from the last peak
            step_from_last = (mus[count] - mus[count - 1]) / count_val
            # round to the nearest integer (peaks must be integers)
            step_from_last = np.round(step_from_last).astype(int)
            # get the new peak count
            peak_count[count] = peak_count[count -1] + step_from_last
        # remove outliers in the FP peak sequence
        _, okeep = mp.robust_polyfit(peak_count, mus, fp_peak_poly_deg, 7)
        # cut down our arrays to reject outliers
        mus = mus[okeep]
        flux = flux[okeep]
        sigmas = sigmas[okeep]
        peak_count = peak_count[okeep]
    # -------------------------------------------------------------------------
    # otherwise anything else we just count numerically (as they are already
    # sorted by pixel position)
    else:
        peak_count = np.arange(len(mus))
    # -------------------------------------------------------------------------
    # report the number of peaks found
    msg = '\t\tFound {0} {1} peaks'
    margs = [len(mus), peak_kind]
    WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # return the peak positions, widths, fluxes, and counts
    return mus, sigmas, flux, peak_count


def get_peak0_guess(params: ParamDict, sparams: Dict[str, Any],
                    order_num) -> float:
    """
    Get the initial guess for the peak position in order "order_num".
    This is done by looking at all previous wavelength solution pickles
    and fitting a linear polynomial to the peak0 guesses.

    :param order_num: int, the order number to get the guess

    :return: float, the initial guess for the peak position
    """
    # get the input path
    inpath = sparams['inpath']
    # print progress
    msg = '\tGetting peak0 guess for order {0}'
    margs = [order_num]
    WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # get the wave pickle path
    wave_pickle_path = os.path.join(inpath, 'wave_pickles')
    # check if the path exists
    if not os.path.exists(wave_pickle_path):
        # if not, return 0
        return np.nan
    # list all files in the wave pickle path
    files = glob.glob(os.path.join(wave_pickle_path, 'wave_order_*.pkl'))
    # if we have no files (or only very few) return nan
    if len(files) < 5:
        return np.nan
    # -------------------------------------------------------------------------
    # storage for loop
    orders = []
    peak0_guesses = []
    # loop around pickle files, try to load them and append to storage if valid
    for filename in files:
        # load wave pickle
        wave_data = load_wave_pickle(params, filename)
        # get the order number from the filename
        base = os.path.basename(filename)
        order_str = base.replace('wave_order_', '').replace('.pkl', '')
        try:
            order = int(order_str)
        except Exception:
            continue
        # get the peak0 guess from the pickle (unless this is not possible)
        if 'peak0_guess' in wave_data:
            peak0_guess = wave_data['peak0_guess']
            orders.append(order)
            peak0_guesses.append(peak0_guess)   
    # -------------------------------------------------------------------------
    # sort the orders numerically
    orders = np.array(orders)
    peak0_guesses = np.array(peak0_guesses)
    sort_order = np.argsort(orders)
    orders = orders[sort_order]
    peak0_guesses = peak0_guesses[sort_order]
    # -------------------------------------------------------------------------
    # fit a linear polynomial to the peak0 guesses
    pfit = mp.robust_polyfit(orders, peak0_guesses, 1, 3)
    # -------------------------------------------------------------------------
    # return the fit to these values (for this order)
    return np.polyval(pfit, order_num)


def package_wavesol(params: ParamDict, recipe, sparams: Dict[str, Any],
                    cal_path: str, hc_file, fp_file,
                    final_wave_sol: np.ndarray, final_wave_coeffs: np.ndarray, 
                    final_fit_cavity: List[float]):
    """
    Package the final wavelength solution into static files for each fiber.
    Try to minic the APERO wave solution files as much as possible.

    :param params: ParamDict, parameter dictionary of constants
    :param sparams: dict, parameters from yaml file
    :param cal_path: str, path to save the static files
    :param hc_file: DrsFitsFile, the hollow cathode file used for wave
    :param fp_file: DrsFitsFile, the fabry-perot file used for
    :param final_wave_sol: np.ndarray, the final wavelength solution
    :param final_wave_coeffs: np.ndarray, the final wavelength solution
                              coefficients
    :param final_fit_cavity: List[float], the final fit to the cavity

    :return: None, saves wave solution static files
    """
    # get instrument
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get the fiber names
    science_fibers, ref_fiber = pconst.FIBER_KINDS()
    # get wave time from mean of hc and fp files
    fp_hdr = fp_file.hdulist_load('FP_E2DS', getdata=False, gethdr=True)
    hc_hdr = hc_file.hdulist_load('HC_E2DS', getdata=False, gethdr=True)
    # --------------------------------------------------------------------------
    # get wave time
    hc_wavetime = hc_hdr[params['KW_MID_OBS_TIME'][0]]
    fp_wavetime = fp_hdr[params['KW_MID_OBS_TIME'][0]]
    # take the wave time as then mean of hc and fp
    wave_time = (hc_wavetime + fp_wavetime) / 2
    # set up the header kwargs
    hdr_kwargs = dict()
    hdr_kwargs['KW_INFILE1'] = dict(DIM=1, 
                                    VALUES=[hc_file.basename], 
                                    DIM1='file')
    hdr_kwargs['KW_INFILE2'] = dict(DIM=1, 
                                    VALUES=[fp_file.basename], 
                                    DIM1='file')
    # set up the wave properties
    wprops = ParamDict()
    wprops['WAVEMAP'] = final_wave_sol
    wprops['WAVETIME'] = wave_time
    wprops['WAVEPATH'] = cal_path
    wprops['WAVESOURCE'] = 'Static'
    wprops['NBO'] = final_wave_sol.shape[0]
    wprops['DEG'] = final_wave_coeffs.shape[1] - 1
    wprops['COEFFS'] = final_wave_coeffs
    wprops['EORDERS'] = None
    wprops['WFP_FILE'] = 'None'
    wprops['WFP_DRIFT'] = 'None'
    wprops['WFP_FWHM'] = 'None'
    wprops['WFP_CONTRAST'] = 'None'
    wprops['WFP_MASK'] = 'None'
    wprops['WFP_LINES'] = None
    wprops['WFP_TARG_RV'] = 'None'
    wprops['WFP_WIDTH'] = 'None'
    wprops['WFP_STEP'] = 'None'
    wprops['CAVITY'] = final_fit_cavity
    wprops['CAVITY_DEG'] = len(final_fit_cavity)
    wprops['CAVITY_PEDESTAL'] = 0.0
    wprops['MEAN_HC_VEL'] = 0.0
    wprops['ERR_HC_VEL'] = 0.0
    wprops['WAVE_POLY_TYPE'] = 'Chebyshev'

    # get echelle orders
    wprops = wave_mod.get_echelle_orders(params, wprops)

    # we loop around all fibers (we will use the same wave solution for all)
    for fiber in science_fibers + [ref_fiber]:
        # ---------------------------------------------------------------------
        # get static file
        static_file = recipe.outputs['STATIC_WAVE_REF'].newcopy(params=params)
        # construct the filename from file instance
        static_file.construct_filename(path=cal_path, fiber=fiber)

        static_file = wave_mod.add_wave_keys(static_file, wprops)
        # ---------------------------------------------------------------------
        # add the fiber to the header kwargs
        hdr_kwargs['KW_FIBER'] = fiber
        # set the wave file
        wprops['WAVEFILE'] = static_file.basename
        # ---------------------------------------------------------------------
        drs_static.save_static_file(params, recipe, static_file,
                                    desc='wave solution',
                                    data_list=[final_wave_sol],
                                    hdr_kwargs=hdr_kwargs)


def load_wave_pickle(params: ParamDict, pickle_file: str) -> Dict[str, Any]:
    """
    Load a wavelength solution pickle file.

    :param pickle_file: str, path to the pickle file

    :return: dict, dictionary containing the wavelength solution data
    """

    # check if the file exists
    if not os.path.exists(pickle_file):
        emsg = 'Pickle file not found: {0}'
        eargs = [pickle_file]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # load the pickle file
    with open(pickle_file, 'rb') as f:
        return pickle.load(f)


def save_wave_pickle(params, data: Dict[str, Any], pickle_file: str):
    """
    Save a wavelength solution dictionary to a pickle file.

    :param data: dict, dictionary containing the wavelength solution data
    :param pickle_file: str, path to the pickle file
    """
    # save the pickle file
    with open(pickle_file, 'wb') as f:
        pickle.dump(data, f)
    # log that we saved the file
    msg = 'Saved wavelength solution pickle to: {0}'
    margs = [pickle_file]
    WLOG(params, '', msg.format(*margs))



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

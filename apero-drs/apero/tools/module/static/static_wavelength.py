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
from typing import Dict, Any

from aperocore.constants import param_functions
from apero.base import base as apero_base
from apero.utils import drs_data
from apero.tools.module.static import drs_static

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


# TODO:
#    1.  Fill in + test this code
#    2.  Remove REF_LEAK from usage
#    3.  Get wave guess from assets
#    4.  Add HC update part (from apero-utils.updates_to_drs.apero_Static_tools.hollow_cathode_update.py
#    5.  remove "reset" directory from assets (move assets/reset/runs to assets/runs)
#    6.  when resetting copy assets/runs to runs


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
        generate_night(params, recipe, sparams)

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
    pass


def generate_night(params: ParamDict, recipe, sparams: Dict[str, Any]):
    pass


def generate_wave_guess(params: ParamDict, recipe, sparams: Dict[str, Any],
                        cal_path: str):
    # load the line list
    wavell, ampll = drs_data.load_linelist(params)

    pass


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

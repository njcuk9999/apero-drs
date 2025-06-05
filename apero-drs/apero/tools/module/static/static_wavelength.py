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

from typing import Dict, Any

from aperocore.constants import param_functions
from apero.base import base as apero_base
from apero.utils import drs_data

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.static.static_wave.py'
__INSTRUMENT__ = 'None'
# Get version and author
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict


# -----------------------------------------------------------------------------
# TODO: Need to load line list


# =============================================================================
# Define functions
# =============================================================================
def main(params: ParamDict, recipe, sparams: Dict[str, Any]):

    hc_raw_file = sparams['hc_raw_file']
    fp_raw_file = sparams['fp_raw_file']
    line_list = sparams['line_list']

    cavity0 = sparams['cavity0']

    cavity_ll_file = params['CAL.WAVE.GEN.CAVITY_LL_FILE']

    # load the line list
    wavell, ampll = drs_data.load_linelist(params)


    return 0


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

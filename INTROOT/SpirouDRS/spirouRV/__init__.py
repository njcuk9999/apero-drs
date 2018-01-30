#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialization code for Spirou radial velocity module module

Created on 2017-11-21 at 11:52

@author: cook

"""

from SpirouDRS import spirouConfig
from . import spirouRV

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouRV.__init__()'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# define imports using asterisk
__all__ = ['CalcRVdrift2D', 'Coravelation', 'CreateDriftFile',
           'DeltaVrms2D', 'DriftPerOrder', 'DriftAllOrders',
           'FitCCF', 'GetDrift', 'GetCCFMask',
           'PearsonRtest', 'RemoveWidePeaks', 'RemoveZeroPeaks',
           'ReNormCosmic2D', 'SigmaClip']

# =============================================================================
# Function aliases
# =============================================================================
# Compute radial velocity drift between reference spectrum and current spectrum
CalcRVdrift2D = spirouRV.calculate_rv_drifts_2d
"""
Calculate the RV drift between the REFERENCE (speref) and COMPARISON (spe)
extracted spectra.

:param speref: numpy array (2D), the REFERENCE extracted spectrum
               size = (number of orders by number of columns (x-axis))
:param spe:  numpy array (2D), the COMPARISON extracted spectrum
             size = (number of orders by number of columns (x-axis))
:param wave: numpy array (2D), the wave solution for each pixel
:param sigdet: float, the read noise (sigdet) for calculating the
               noise array
:param threshold: float, upper limit for pixel values, above this limit
                  pixels are regarded as saturated
:param size: int, size (in pixels) around saturated pixels to also regard
             as bad pixels

:return rvdrift: numpy array (1D), the RV drift between REFERENCE and 
                 COMPARISON spectrum for each order
"""

Coravelation = spirouRV.coravelation
"""
Calculate the CCF and fit it with a Gaussian profile

:param p: parameter dictionary, parameter dictionary containing the
          constants
:param loc: parameter dictionary, parameter dictionary containing the data

:return loc: the updated parameter dictionary
"""

CreateDriftFile = spirouRV.create_drift_file
"""
Creates a reference ascii file that contains the positions of the FP peaks
Returns the pixels positions and Nth order of each FP peak

:param p: parameter dictionary, storage of constants
:param loc: parameter dictionary, storage of data

:return loc: parameter dictionary, updated with new data
"""

DeltaVrms2D = spirouRV.delta_v_rms_2d
"""
Compute the photon noise uncertainty for all orders (for the 2D image)

:param spe: numpy array (2D), the extracted spectrum
            size = (number of orders by number of columns (x-axis))
:param wave: numpy array (2D), the wave solution for each pixel
:param sigdet: float, the read noise (sigdet) for calculating the
               noise array
:param threshold: float, upper limit for pixel values, above this limit
                  pixels are regarded as saturated
:param size: int, size (in pixels) around saturated pixels to also regard
             as bad pixels

:return dvrms2: numpy array (1D), the photon noise for each pixel (squared)
:return weightedmean: float, weighted mean photon noise across all orders
"""

DriftPerOrder = spirouRV.drift_per_order
"""
Calculate the individual drifts per order

:param loc: parameter dictionary, data storage
:param fileno: int, the file number (iterator number)

:return loc: parameter dictionary, the updated data storage dictionary
"""

DriftAllOrders = spirouRV.drift_all_orders
"""
Work out the weighted mean drift across all orders

:param loc: parameter dictionary, data storage
:param fileno: int, the file number (iterator number)
:param nomin: int, the first order to use (i.e. from nomin to nomax)
:param nomax: int, the last order to use (i.e. from nomin to nomax)

:return loc: parameter dictionary, the updated data storage dictionary
"""

FitCCF = spirouRV.fit_ccf
"""
Fit the CCF to a guassian function

:param rv: numpy array (1D), the radial velocities for the line
:param ccf: numpy array (1D), the CCF values for the line
:param fit_type: int, if "0" then we have an absorption line
                      if "1" then we have an emission line

:return result: numpy array (1D), the fit parameters in the
                following order:

            [amplitude, center, fwhm, offset from 0 (in y-direction)]

:return ccf_fit: numpy array (1D), the fit values, i.e. the gaussian values
                 for the fit parameters in "result"
"""

GetDrift = spirouRV.get_drift
"""
Get the centroid of all peaks provided an input peak position

:param p: parameter dictionary, parameter dictionary containing constants
:param sp: numpy array (2D), e2ds fits file with FP peaks
           size = (number of orders x number of pixels in x-dim of image)
:param ordpeak: numpy array (1D), order of each peak
:param xpeak0: numpy array (1D), position in the x dimension of all peaks
:param gaussfit: bool, if True uses a gaussian fit to get each centroid
                 (slow) or adjusts a barycenter (gaussfit=False)

:return xpeak: numpy array (1D), the central positions if the peaks
"""

GetCCFMask = spirouRV.get_ccf_mask
"""
Get the CCF mask

:param p: parameter dictionary, parameter dictionary containing the
          constants
:param loc: parameter dictionary, parameter dictionary containing the data
:param filename: string or None, the filename and location of the ccf mask 
                 file, if None then file names is gotten from p["ccf_mask"]

:return loc: the updated parameter dictionary
"""

PearsonRtest = spirouRV.pearson_rtest
"""
Perform a Pearson R test on each order in spe against speref

:param nbo: int, the number of orders
:param spe: numpy array (2D), the extracted array for this iteration
            size = (number of orders x number of pixels in x-dim)
:param speref: numpy array (2D), the extracted array for the reference
               image, size = (number of orders x number of pixels in x-dim)

:return cc_orders: numpy array (1D), the pearson correlation coefficients
                   for each order, size = (number of orders)
"""

RemoveWidePeaks = spirouRV.remove_wide_peaks
"""
Remove peaks that are too wide

:param p: parameter dictionary, storage of constants
:param loc: parameter dictionary, storage of data
:param expwidth: float or None, the expected width of FP peaks - used to
                 "normalise" peaks (which are then subsequently removed
                 if > "cutwidth") if expwidth is None taken from 
                 p["drift_peak_exp_width"]
:param cutwidth: float or None, the normalised width of FP peaks thatis too
                 large normalised width FP FWHM - expwidth
                 cut is essentially: FP FWHM < (expwidth + cutwidth), if
                 cutwidth is None taken from p["drift_peak_norm_width_cut"]

:return loc: parameter dictionary, updated with new data
"""

RemoveZeroPeaks = spirouRV.remove_zero_peaks
"""
Remove peaks that have a value of zero

:param p: parameter dictionary, storage of constants
:param loc: parameter dictionary, storage of data

:return loc: parameter dictionary, updated with new data
"""

ReNormCosmic2D = spirouRV.renormalise_cosmic2d
"""
Correction of the cosmics and renormalisation by comparison with
reference spectrum (for the 2D image)

:param speref: numpy array (2D), the REFERENCE extracted spectrum
               size = (number of orders by number of columns (x-axis))
:param spe:  numpy array (2D), the COMPARISON extracted spectrum
             size = (number of orders by number of columns (x-axis))
:param threshold: float, upper limit for pixel values, above this limit
                  pixels are regarded as saturated
:param size: int, size (in pixels) around saturated pixels to also regard
             as bad pixels
:param cut: float, define the number of standard deviations cut at in             -                  cosmic renormalisation

:return spen: numpy array (2D), the corrected normalised COMPARISON
              extracted spectrrum
:return cnormspe: numpy array (1D), the flux ratio for each order between
                  corrected normalised COMPARISON extracted spectrum and
                  REFERENCE extracted spectrum
:return cpt: float, the total flux above the "cut" parameter
             (cut * standard deviations above median)
"""

SigmaClip = spirouRV.sigma_clip
"""
Perform a sigma clip on dv

:param loc: parameter dictionary, data storage
:param sigma: float, the sigma of the clip (away from the median)

:return loc: the updated parameter dictionary
"""


# =============================================================================
# End of code
# =============================================================================

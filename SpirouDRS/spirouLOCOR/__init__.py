#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 17:09

@author: cook



Version 0.0.0
"""

from . import spirouLOCOR


BoxSmoothedImage = spirouLOCOR.smoothed_boxmean_image
"""
Produce a (box) smoothed image, smoothed by the mean of a box of
    size=2*"size" pixels.

    if mode='convolve' (default) then this is done
    by convolving a top-hat function with the image (FAST)
    - note produces small inconsistencies due to FT of top-hat function

    if mode='manual' then this is done by working out the mean in each
    box manually (SLOW)

:param image: numpy array (2D), the image
:param size: int, the number of pixels to mask before and after pixel
             (for every row)
             i.e. box runs from  "pixel-size" to "pixel+size" unless
             near an edge
:param weighted: bool, if True pixel values less than zero are weighted to
                 a value of 1e-6 and values above 0 are weighted to a value
                 of 1
:param mode: string, if 'convolve' convoles with a top-hat function of the
                     size "box" for each column (FAST) - note produces small
                     inconsistencies due to FT of top-hat function

                     if 'manual' calculates every box individually (SLOW)

:return newimage: numpy array (2D), the smoothed image
"""


CalcLocoFits = spirouLOCOR.calculate_location_fits
"""
Calculates all fits in coeffs array across pixels of size=dim

:param coeffs: coefficient array, 
               size = (number of orders x number of coefficients in fit)
               output array will be size = (number of orders x dim)
:param dim: int, number of pixels to calculate fit for
            fit will be done over x = 0 to dim in steps of 1
:return yfits: array,
               size = (number of orders x dim)
               the fit for each order at each pixel values from 0 to dim 
"""

FiberParams = spirouLOCOR.fiber_params
"""
Takes the parameters defined in FIBER_PARAMS from parameter dictionary
(i.e. from config files) and adds the correct parameter to a fiber
parameter dictionary

:param pp: dictionary, parameter dictionary
:param fiber: string, the fiber type (and suffix used in confiruation file)
              i.e. for fiber AB fiber="AB" and nbfib_AB should be present
              in config if "nbfib" is in FIBER_PARAMS
:return fparam: dictionary, the fiber parameter dictionary
"""

FindPosCentCol = spirouLOCOR.find_position_of_cent_col
"""
Finds the central positions based on the central column values

:param values: numpy array (1D) size = number of rows,
                the central column values
:param threshold: float, the threshold above which to find pixels as being
                  part of an order

:return position: numpy array (1D), size= number of rows,
                  the pixel positions in cvalues where the centers of each
                  order should be

For 1000 loops, best of 3: 771 µs per loop
"""

FindOrderCtrs = spirouLOCOR.find_order_centers
"""
Find the center pixels and widths of this order at specific points 
along this order="order_num"

specific points are defined by steps (ic_locstepc) away from the
central pixel (ic_cent_col)

:param pp: dictionary, parameter dictionary
:param image: numpy array (2D), the image
:param loc: dictionary, localisation parameter dictionary
:param order_num: int, the current order to process

:return loc: dictionary, parameter dictionary with updates center and width
             positions
"""

GetCoeffs = spirouLOCOR.get_loc_coefficients
"""
Extracts loco coefficients from parameters keys (uses header="hdr" provided 
to get acquisition time or uses p['fitsfilename'] to get acquisition time if
"hdr" is None    

:param pp: dictionary, parameter dictionary
:param hdr: dictionary, header file from FITS rec (opened by spirouFITS)

:return loc: dictionary, parameter dictionary containing the coefficients,
             the number of orders and the number of coeffiecients from 
             center and width localization fits 
"""

imageLocSuperimp = spirouLOCOR.image_localization_superposition
"""
Take an image and superimpose zeros over the positions in the image where
the central fits where found to be

:param image: numpy array (2D), the image
:param coeffs: coefficient array, 
               size = (number of orders x number of coefficients in fit)
               output array will be size = (number of orders x dim)
:return newimage: numpy array (2D), the image with super-imposed zero filled
                  fits
"""


InitialOrderFit = spirouLOCOR.initial_order_fit
"""
Performs a crude initial fit for this order, uses the ctro positions or
sigo width values found in "FindOrderCtrs" or "find_order_centers" to do
the fit

:param pp: dictionary, parameter dictionary containing constants and
           keywords
:param loc: dictionary, parameter dictionary containing the localization
            data "ctro" and "sigo"
:param mask: numpy array (1D) of booleans, True where we have non-zero
             widths
:param onum: int, order iteration number (running number over all
             iterations)
:param rnum: int, order number (running number of successful order
             iterations only)
:param kind: string, 'center' or 'fwhm', if 'center' then this fit is for
             the central positions, if 'fwhm' this fit is for the width of
             the orders
:param fig: plt.figure, the figure to plot initial fit on
:param frame: matplotlib axis i.e. plt.subplot(), the axis on which to plot
              the initial fit on (carries the plt.imshow(image))
:return fitdata: dictionary, contains the fit data key value pairs for this
                 initial fit. keys are as follows:

        a = coefficients of the fit from key 

        size = 'ic_locdfitc' [for kind='center'] or 
             = 'ic_locdftiw' [for kind='fwhm']

        fit = the fity values for the fit (for x = loc['x'])
            where fity = Sum(a[i] * x^i)  

        res = the residuals from y - fity 
             where y = ctro [kind='center'] or 
                     = sigo [kind='fwhm'])

        abs_res = abs(res)

        rms = the standard deviation of the residuals

        max_ptp = maximum residual value max(res)

        max_ptp_frac = max_ptp / rms  [kind='center']
                     = max(abs_res/y) * 100   [kind='fwhm']
"""

LocCentralOrderPos = spirouLOCOR.locate_order_center
"""
Takes the values across the oder and finds the order center by looking for
the start and end of the order (and thus the center) above threshold

:param values: numpy array (1D) size = number of rows, the pixels in an
                order

:param threshold: float, the threshold above which to find pixels as being
                  part of an order

:param min_width: float, the minimum width for an order to be accepted

:return positions: numpy array (1D), size= number of rows,
                   the pixel positions in cvalues where the centers of each
                   order should be

:return widths:    numpy array (1D), size= number of rows,
                   the pixel positions in cvalues where the centers of each
                   order should be

For 1000 loops, best of 3: 771 µs per loop
"""


MergeCoefficients = spirouLOCOR.merge_coefficients


SigClipOrderFit = spirouLOCOR.sigmaclip_order_fit
"""
Performs a sigma clip fit for this order, uses the ctro positions or
sigo width values found in "FindOrderCtrs" or "find_order_centers" to do
the fit. Removes the largest residual from the initial fit (or subsequent
sigmaclips) value in x and y and recalculates the fit. 

Does this until all the following conditions are NOT met:
       rms > 'ic_max_rms'   [kind='center' or kind='fwhm']
    or max_ptp > 'ic_max_ptp [kind='center']
    or max_ptp_frac > 'ic_ptporms_center'   [kind='center']
    or max_ptp_frac > 'ic_max_ptp_frac'     [kind='fwhm'

:param pp: dictionary, parameter dictionary containing constants and
           keywords
:param loc: dictionary, parameter dictionary containing the localization
            data "ctro" and "sigo"
:param fitdata: dictionary, contains the fit data key value pairs for this
                 initial fit. keys are as follows:

        a = coefficients of the fit from key 

        size = 'ic_locdfitc' [for kind='center'] or 
             = 'ic_locdftiw' [for kind='fwhm']

        fit = the fity values for the fit (for x = loc['x'])
            where fity = Sum(a[i] * x^i)  

        res = the residuals from y - fity 
             where y = ctro [kind='center'] or 
                     = sigo [kind='fwhm'])

        abs_res = abs(res)

        rms = the standard deviation of the residuals

        max_ptp = maximum residual value max(res)

        max_ptp_frac = max_ptp / rms  [kind='center']
                     = max(abs_res/y) * 100   [kind='fwhm'] 

:param mask: numpy array (1D) of booleans, True where we have non-zero
             widths
:param onum: int, order iteration number (running number over all
             iterations)
:param rnum: int, order number (running number of successful order
             iterations only)
:param kind: string, 'center' or 'fwhm', if 'center' then this fit is for
             the central p

:return fitdata: dictionary, contains the fit data key value pairs for this
                 initial fit. keys are as follows:

        a = coefficients of the fit from key 

        size = 'ic_locdfitc' [for kind='center'] or 
             = 'ic_locdftiw' [for kind='fwhm']

        fit = the fity values for the fit (for x = loc['x'])
            where fity = Sum(a[i] * x^i)  

        res = the residuals from y - fity 
             where y = ctro [kind='center'] or 
                     = sigo [kind='fwhm'])

        abs_res = abs(res)

        rms = the standard deviation of the residuals

        max_ptp = maximum residual value max(res)

        max_ptp_frac = max_ptp / rms  [kind='center']
                     = max(abs_res/y) * 100   [kind='fwhm'] 
"""
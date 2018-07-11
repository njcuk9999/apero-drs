#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-05-18 at 14:16

@author: cook
"""

import numpy as np
from scipy.interpolate import interp1d
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from . import spirouFITS
from . import spirouImage


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouExposeMeter.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog


# =============================================================================
# Define functions
# =============================================================================
def get_telluric(p, loc, hdr):
    """
    Reads the telluric file "tellwave" (wavelength data) and "tellspe"
    (telluric absorption data) from files defined in "p" and finds "good" areas
    of the telluric model, i.e.

        p['EM_MIN_LAMBDA'] > wavelength > p['EM_MAX_LAMBDA']

        and

        telluric transmission > p['EM_TELL_THRESHOLD']

    :param p: parameter dictionary, ParamDict containing constants

    :param loc: parameter dictionary, ParamDict containing data

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                tell_x: numpy array (1D), the wavelengths (in nm) of the
                        telluric model
                tell_y: numpy array (1D), the transmission 1 = 100% transmission
                        for the telluric model (shape = same as tell_x)
                tell_mask: numpy array (1D), array of booleans, True if
                           telluric model at this wavelength is deemed "good"
                           and False if deemed "bad"
    """

    func_name = __NAME__ + '.get_telluric()'
    # load the telluric model
    txfile = spirouDB.GetCalibFile(p, 'EM_TELL_X', hdr, required=True)
    tyfile = spirouDB.GetCalibFile(p, 'EM_TELL_Y', hdr, required=True)
    # add to p
    p['TELLWAVE'] = txfile
    p['TELLSPE'] = tyfile
    p.set_sources(['tellwave', 'tellspe'], func_name)
    # add model and mask to loc
    rout = spirouFITS.readimage(p, filename=txfile, log=False)
    loc['TELL_X'] = rout[0]
    rout = spirouFITS.readimage(p, filename=tyfile, log=False)
    loc['TELL_Y'] = rout[0]
    # set source
    loc.set_sources(['tell_x', 'tell_y'], func_name)
    # return p and loc
    return p, loc


def order_profile(p, loc):
    """
    Create a 2D image of the order profile. Each order's pixels are labelled
    with the order_number, pixels not in orders are given a value of -1

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                image: numpy array (2D), the original image (used for sizing
                       new images of the same size)
                       shape = (number of rows x number of columns)
                       shape = (y-dimension x x-dimension)
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                orderimage: numpy array (2D), the values of the each pixel
                            according to which order they are in
                            shape is same as "image"
                suborderimage: numpy array (2D), the values of the each pixel
                            according to which order and fiber they are in
                            shape is same as "image". i.e. order 0 fiber A = 0,
                            order 0 fiber B = 1, order 1 fiber A = 2,
                            order 1 fiber B = 3
    """
    func_name = __NAME__ + '.order_profile()'
    # get data from loc
    image = loc['IMAGE']
    allacc, allass = loc['ALL_ACC'], loc['ALL_ASS']
    # construct a "NaN" image (for wavelengths)
    ishape = image.shape
    # Define empty order image
    orderimage = np.repeat([-1], np.product(ishape)).reshape(ishape)
    suborderimage = np.repeat([-1], np.product(ishape)).reshape(ishape)
    fiberimage = np.repeat(['00'], np.product(ishape)).reshape(ishape)
    # get the indices locations
    yimage, ximage = np.indices(image.shape)
    # loop around number of orders (AB)
    for order_no in range(loc['NBO']):
        # loop around fibers
        for fiber in allacc.keys():
            # get localisation parameters for this fiber
            acc, ass = allacc[fiber], allass[fiber]
            # deal with AB fiber
            if fiber == 'AB':
                for fno in [0, 1]:
                    # get fiber iteration number
                    fin = 2*order_no + fno
                    # get central positions
                    cfit = np.polyval(acc[fin][::-1], ximage)
                    # get width positions
                    wfit = np.polyval(ass[fin][::-1], ximage)
                    # define the lower and upper bounds of this order
                    upper = cfit + wfit/2
                    lower = cfit - wfit/2
                    # define the mask of the pixels in this order
                    mask = (yimage < upper) & (yimage > lower)
                    # create the order image
                    orderimage[mask] = order_no
                    suborderimage[mask] = fin
                    fiberimage[mask] = fiber
            # else if fiber is A
            elif fiber == 'A':
                # get fiber iteration number
                fin = 2 * order_no
                # get central positions
                cfit = np.polyval(acc[fin][::-1], ximage)
                # get width positions
                wfit = np.polyval(ass[fin][::-1], ximage)
                # define the lower and upper bounds of this order
                upper = cfit + wfit / 2
                lower = cfit - wfit / 2
                # define the mask of the pixels in this order
                mask = (yimage < upper) & (yimage > lower)
                # create the order image
                orderimage[mask] = order_no
                suborderimage[mask] = fin
                fiberimage[mask] = fiber
            # else if fiber is B
            elif fiber == 'B':
                # get fiber iteration number
                fin = 2 * order_no + 1
                # get central positions
                cfit = np.polyval(acc[fin][::-1], ximage)
                # get width positions
                wfit = np.polyval(ass[fin][::-1], ximage)
                # define the lower and upper bounds of this order
                upper = cfit + wfit / 2
                lower = cfit - wfit / 2
                # define the mask of the pixels in this order
                mask = (yimage < upper) & (yimage > lower)
                # create the order image
                orderimage[mask] = order_no
                suborderimage[mask] = fin
                fiberimage[mask] = fiber
            # else if fiber is C
            elif fiber == 'C':
                # get fiber iteration number
                fin = order_no
                # get central positions
                cfit = np.polyval(acc[fin][::-1], ximage)
                # get width positions
                wfit = np.polyval(ass[fin][::-1], ximage)
                # define the lower and upper bounds of this order
                upper = cfit + wfit / 2
                lower = cfit - wfit / 2
                # define the mask of the pixels in this order
                mask = (yimage < upper) & (yimage > lower)
                # create the order image
                orderimage[mask] = order_no
                suborderimage[mask] = fin
                fiberimage[mask] = fiber
            #else break
            else:
                emsg1 = 'Fiber type="{0}" invalid'.format(fiber)
                emsg2 = '\tfunction={0}'.format(func_name)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])

    # add to loc
    loc['ORDERIMAGE'] = orderimage
    loc['SUBORDERIMAGE'] = suborderimage
    loc['FIBERIMAGE'] = fiberimage
    # add source
    loc.set_sources(['orderimage', 'suborderimage','fiberimage'], func_name)
    # return loc
    return loc


def create_wavelength_image(p, loc):
    """
    Using each orders location coefficents, tilt and wavelength coefficients
    Make a 2D map the size of the image of each pixels wavelength value
    (or NaN if not a valid position for a wavelength)

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                image: numpy array (2D), the original image (used for sizing
                       new images of the same size)
                       shape = (number of rows x number of columns)
                       shape = (y-dimension x x-dimension)

                # TODO: This should be wavelength coefficient array
                wave: numpy array (2D), the wavelength for each x pixel for each
                      order.
                      shape = (number of orders x number of columns)
                      shape = (number of orders x x-dimension)
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                tilt: numpy array (1D), the tilt angle of each order
                suborderimage: numpy array (2D), the values of the each pixel
                            according to which order and fiber they are in
                            shape is same as "image". i.e. order 0 fiber A = 0,
                            order 0 fiber B = 1, order 1 fiber A = 2,
                            order 1 fiber B = 3

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                waveimage: numpy array (2D), the wavelength of each pixel
                           shape is same as input "image"
    """
    func_name = __NAME__ + '.create_wavelength_image()'
    # get data from loc
    image = loc['IMAGE']
    wave = loc['WAVE']
    allacc, allass = loc['ALL_ACC'], loc['ALL_ASS']
    tilt = loc['TILT']
    orderimage = loc['ORDERIMAGE']
    suborderimage = loc['SUBORDERIMAGE']
    fiberimage = loc['FIBERIMAGE']
    # construct a "NaN" image (for wavelengths)
    ishape = image.shape
    # construct
    waveimage = np.repeat([np.nan], np.product(ishape)).reshape(ishape)
    # get the indices locations
    yimage, ximage = np.indices(image.shape)
    # loop around number of orders (AB)
    for order_no in range(loc['NBO']):

        # get wavelength coefficients for this order
        # TODO: in future this fit should have already be done!
        awave0 = fit_wavelength(ximage[0], wave[order_no])
        # get first derivative of wavelength coefficients
        awave1 = np.polyder(awave0, 1)
        # get second derivative of wavelength coefficients
        awave2 = np.polyder(awave0, 2)
        # get third derivative of wavelength coefficients
        awave3 = np.polyder(awave0, 3)

        # loop around fibers
        for fiber in allacc.keys():
            # get localisation parameters for this fiber
            acc = allacc[fiber]
            # deal with AB fiber
            if fiber == 'AB':
                # loop around A and B
                for fno in [0, 1]:
                    # get fiber iteration number
                    fin = 2 * order_no + fno
                    # get central polynomial coefficients
                    centpoly = acc[fin][::-1]
                    # find those pixels in this suborder
                    mask = suborderimage == fin
                    # get x0s and y0s
                    x0s, y0s = np.array(ximage[mask]), np.array(yimage[mask])
                    # calculate centers
                    xcenters = np.array(x0s)
                    ycenters = np.polyval(centpoly, xcenters)
                    # get deltax and delta y
                    deltay = y0s - ycenters
                    deltax = deltay * np.tan(np.deg2rad(-tilt[order_no]))

                    # construct lambda from x
                    lambda0 = np.polyval(awave0, x0s)
                    lambda1 = np.polyval(awave1, x0s) * deltax
                    lambda2 = np.polyval(awave2, x0s) * deltax ** 2
                    lambda3 = np.polyval(awave3, x0s) * deltax ** 3
                    # sum of lambdas
                    lambda_total = lambda0 + lambda1 + lambda2 + lambda3
                    # add to array
                    waveimage[y0s, x0s] = lambda_total
            # else if fiber is A
            elif fiber == 'A':
                # get fiber iteration number
                fin = 2 * order_no
                # get central polynomial coefficients
                centpoly = acc[fin][::-1]
                # find those pixels in this suborder
                mask = (orderimage == fin) & (fiberimage == fiber)
                # get x0s and y0s
                x0s, y0s = np.array(ximage[mask]), np.array(yimage[mask])
                # calculate centers
                xcenters = np.array(x0s)
                ycenters = np.polyval(centpoly, xcenters)
                # get deltax and delta y
                deltay = y0s - ycenters
                deltax = deltay * np.tan(np.deg2rad(-tilt[order_no]))

                # construct lambda from x
                lambda0 = np.polyval(awave0, x0s)
                lambda1 = np.polyval(awave1, x0s) * deltax
                lambda2 = np.polyval(awave2, x0s) * deltax ** 2
                lambda3 = np.polyval(awave3, x0s) * deltax ** 3
                # sum of lambdas
                lambda_total = lambda0 + lambda1 + lambda2 + lambda3
                # add to array
                waveimage[y0s, x0s] = lambda_total
            # else if fiber is B
            elif fiber == 'B':
                # get fiber iteration number
                fin = 2 * order_no + 1
                # get central polynomial coefficients
                centpoly = acc[fin][::-1]
                # find those pixels in this suborder
                mask = (orderimage == fin) & (fiberimage == fiber)
                # get x0s and y0s
                x0s, y0s = np.array(ximage[mask]), np.array(yimage[mask])
                # calculate centers
                xcenters = np.array(x0s)
                ycenters = np.polyval(centpoly, xcenters)
                # get deltax and delta y
                deltay = y0s - ycenters
                deltax = deltay * np.tan(np.deg2rad(-tilt[order_no]))

                # construct lambda from x
                lambda0 = np.polyval(awave0, x0s)
                lambda1 = np.polyval(awave1, x0s) * deltax
                lambda2 = np.polyval(awave2, x0s) * deltax ** 2
                lambda3 = np.polyval(awave3, x0s) * deltax ** 3
                # sum of lambdas
                lambda_total = lambda0 + lambda1 + lambda2 + lambda3
                # add to array
                waveimage[y0s, x0s] = lambda_total
            # else if fiber is C
            elif fiber == 'C':
                # get fiber iteration number
                fin = order_no
                # get central polynomial coefficients
                centpoly = acc[fin][::-1]
                # find those pixels in this suborder
                mask = (orderimage == fin) & (fiberimage == fiber)
                # get x0s and y0s
                x0s, y0s = np.array(ximage[mask]), np.array(yimage[mask])
                # calculate centers
                xcenters = np.array(x0s)
                ycenters = np.polyval(centpoly, xcenters)
                # get deltax and delta y
                deltay = y0s - ycenters
                deltax = deltay * np.tan(np.deg2rad(-tilt[order_no]))

                # construct lambda from x
                lambda0 = np.polyval(awave0, x0s)
                lambda1 = np.polyval(awave1, x0s) * deltax
                lambda2 = np.polyval(awave2, x0s) * deltax ** 2
                lambda3 = np.polyval(awave3, x0s) * deltax ** 3
                # sum of lambdas
                lambda_total = lambda0 + lambda1 + lambda2 + lambda3
                # add to array
                waveimage[y0s, x0s] = lambda_total
            #else break
            else:
                emsg1 = 'Fiber type="{0}" invalid'.format(fiber)
                emsg2 = '\tfunction={0}'.format(func_name)
                WLOG('error', p['LOG_OPT'], [emsg1, emsg2])

    # add to loc
    loc['WAVEIMAGE'] = waveimage
    # set source
    loc.set_source('WAVEIMAGE', func_name)
    # return loc
    return loc


# TODO: This function should be removed once we have wavelength coefficients
def fit_wavelength(x, lam, order=5):
    """
    Temporary function to fit the wavelength values for each x value

    :param x: numpy array (1D), the x pixel values along the order, must be the
              same shape as "lam"
    :param lam: numpy array(1D), the corresponding wavelength value for each
                x pixel, must be the same shape as "x"
    :param order: int, the order of the polynomial fit (default = 5)

    :return coeffs: numpy array (1D), the coefficients defining the fit,
            polynomial ``p(x) = p[0] * x**deg + ... + p[deg]`` of degree `deg`
    """
    # fit the coefficients
    coeffs = np.polyfit(x, lam, order)
    # return the coefficients
    return coeffs


def create_image_from_waveimage(loc, x, y):
    """
    Takes a spectrum "y" at wavelengths "x" and uses these to interpolate
    wavelength positions in loc['WAVEIMAGE'] to map the spectrum onto
    the waveimage

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                waveimage: numpy array (2D), the wavelength of each pixel
                           shape is same as input image and must be the same
                           shape as spe
    :param x: numpy array (1D), the wavelength values to map onto the image
    :param y: numpy array (1D), the spectrum values to map onto the image

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                spe: numpy array (2D), the spectrum of each pixel, shape is
                           same as input image and must be the same shape
                           as waveimage
    """
    func_name = __NAME__ + '.create_image_from_waveimage()'
    # get data from loc
    waveimage = loc['WAVEIMAGE']
    # set up interpolation (catch warnings)
    with warnings.catch_warnings(record=True) as _:
        wave_interp = interp1d(x, y)
    # create new spectrum
    newimage = np.zeros_like(waveimage)
    # loop around each row in image, interpolate wavevalues
    for row in range(len(waveimage)):
        # get row values
        rvalues = waveimage[row]
        # TODO change mask out zeros to NaNs
        # mask out zeros (NaNs in future)
        invalidpixels = (rvalues == 0)
        invalidpixels &= ~np.isfinite(rvalues)
        # don't try to interpolate those pixels outside range of "x"
        with warnings.catch_warnings(record=True) as _:
            invalidpixels |= rvalues < np.min(x)
            invalidpixels |= rvalues > np.max(x)
        # valid pixel definition
        validpixels = ~invalidpixels
        # check that we have some valid pixels
        if np.sum(validpixels) == 0:
            continue
        # interpolate wavelengths in waveimage to get newimage (catch warnings)
        with warnings.catch_warnings(record=True) as _:
            newimage[row][validpixels] = wave_interp(rvalues[validpixels])
    # add to loc
    loc['SPE'] = newimage
    loc.set_source('SPE', func_name)
    # return loc
    return loc


def create_image_from_e2ds(p, loc):
    """
    Takes a spectrum "y" at wavelengths "x" and uses these to interpolate
    wavelength positions in loc['WAVEIMAGE'] to map the spectrum onto
    the waveimage

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                waveimage: numpy array (2D), the wavelength of each pixel
                           shape is same as input image and must be the same
                           shape as spe
    :param x: numpy array (1D), the wavelength values to map onto the image
    :param y: numpy array (1D), the spectrum values to map onto the image

    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                spe: numpy array (2D), the spectrum of each pixel, shape is
                           same as input image and must be the same shape
                           as waveimage
    """
    func_name = __NAME__ + '.create_image_from_waveimage()'
    # get data from loc
    waveimage = loc['WAVEIMAGE']
    orderimage = loc['ORDERIMAGE']
    fiberimage = loc['FIBERIMAGE']
    e2dsimages = loc['E2DSFILES']
    wave = loc['ALLWAVE']
    allacc, allass = loc['ALL_ACC'], loc['ALL_ASS']

    # create new spectrum
    newimage = np.zeros_like(waveimage) * np.nan

    # loop around orders
    for order_num in range(loc['NBO']):

        # log progress
        wmsg = 'Extrapolating order {0}'.format(order_num)
        WLOG('', p['LOG_OPT'], wmsg)

        # loop around fibers
        for fiber in allacc.keys():
            # get x data for this order and thus fiber
            x = wave[fiber][order_num]
            # get y data for this order and this fiber
            y = e2dsimages[fiber][order_num]

            # set up interpolation (catch warnings)
            with warnings.catch_warnings(record=True) as _:
                wave_interp = interp1d(x, y)

            # loop around each row in image, interpolate wavevalues
            for row in range(len(waveimage)):
                # get row values
                rvalues = waveimage[row]
                # TODO change mask out zeros to NaNs
                # mask out zeros (NaNs in future)
                invalidpixels = (rvalues == 0)
                invalidpixels &= ~np.isfinite(rvalues)
                # don't try to interpolate those pixels outside range of "x"
                with warnings.catch_warnings(record=True) as _:
                    invalidpixels |= rvalues < np.min(x)
                    invalidpixels |= rvalues > np.max(x)
                # valid pixel definition
                validpixels = ~invalidpixels
                # check that we have some valid pixels
                if np.sum(validpixels) == 0:
                    continue

                # add order mask to valid pixels
                validpixels &= (orderimage[row] == order_num)
                # check that we have some valid pixels
                if np.sum(validpixels) == 0:
                    continue

                # add fiber type mask
                validpixels &= (fiberimage[row] == fiber)
                # check that we have some valid pixels
                if np.sum(validpixels) == 0:
                    continue

                # interpolate wavelengths in waveimage to get newimage
                #     (catch warnings)
                with warnings.catch_warnings(record=True) as _:
                    ivalues = wave_interp(rvalues[validpixels])
                    newimage[row][validpixels] = ivalues
    # add to loc
    loc['SPE'] = newimage
    loc['SPE0'] = np.where(np.isfinite(newimage), newimage, 0.0)
    loc.set_sources(['SPE', 'SPE0'], func_name)
    # return loc
    return loc


def create_mask(p, loc):
    """
    Create a mask of a telluric spectrum

    Mask criteria (value = 1 if True or 0 elsewise)

        p['em_min_lambda'] < loc['WAVEIMAGE'] < p['em_max_lambda']

        loc['SPE'] > p['em_tell_threshold']

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            em_min_lambda: float, the minimum allowed wavelength (in nm)
            em_max_lambda: float, the maximum allowed wavelength (in nm)
            em_tell_threshold: float, the minimum transmission to define
                               good parts of the spectrum

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                waveimage: numpy array (2D), the wavelength of each pixel
                           shape is same as input image and must be the same
                           shape as spe
                spe: numpy array (2D), the spectrum of each pixel, shape is
                           same as input image and must be the same shape
                           as waveimage
    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                tell_mask_2D: numpy array (2D), the mask image, shape is the
                              same as waveimage/spe. Values that meet the
                              above criteria have a value of 1, elsewise 0
    """

    func_name = __NAME__ + '.create_image_from_waveimage()'
    # get data from loc
    waveimage = loc['WAVEIMAGE']
    tell_spe = loc['SPE']
    # apply mask to telluric model
    with warnings.catch_warnings(record=True) as _:
        mask1 = waveimage > p['EM_MIN_LAMBDA']
        mask2 = waveimage < p['EM_MAX_LAMBDA']
        mask3 = tell_spe > p['EM_TELL_THRESHOLD']
    # combine masks
    mask = mask1 & mask2 & mask3
    # save mask to loc
    loc['TELL_MASK_2D'] = mask
    loc.set_source('TELL_MASK_2D', func_name)
    # return loc
    return loc


def unresize(p, image, xsize, ysize):
    # ----------------------------------------------------------------------
    # un-Resize image
    # ----------------------------------------------------------------------

    # log change
    wargs = image.shape[1], image.shape[0], xsize, ysize
    wmsg = 'Resizing from ({0}x{1}) to ({2}x{3}) [Fill with NaNs]'
    WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

    # create an array of given size
    size = np.product([ysize, xsize])

    newimage = np.repeat(np.nan, size).reshape(ysize, xsize)

    # insert image at given pixels
    xlow, xhigh = p['IC_CCDX_LOW'], p['IC_CCDX_HIGH']
    ylow, yhigh = p['IC_CCDY_LOW'], p['IC_CCDY_HIGH']
    newimage[ylow:yhigh, xlow:xhigh] = image

    # rotate the image
    WLOG('', p['LOG_OPT'], 'Flipping image in x and y')
    newimage = spirouImage.flip_image(newimage)

    # return a copy of locally defined variables in the memory
    return newimage


# =============================================================================
# End of code
# =============================================================================

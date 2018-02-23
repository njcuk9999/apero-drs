#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-02-15 at 14:05

@author: cook
"""
from __future__ import division
import numpy as np
from scipy.interpolate import interp1d
import os
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'telluric_2d_mask.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# -----------------------------------------------------------------------------

DATA = '/scratch/Projects/spirou_py3/data'

# will be inputs?
FLATFILE = 'flat_dark02f10.fits'
TAPASX = DATA + '/calibDB/TAPAS_X_axis_speed_dv=0.5.fits'
TAPASY = DATA + '/calibDB/tapas_combined_za=20.000000.fits'
THRESHOLD = 0.95
# minimum and maximum H band (MKO))
MINLAM = 1478.7
MAXLAM = 1823.1
# -----------------------------------------------------------------------------


# =============================================================================
# Define main program function
# =============================================================================
def main(night_name=None, flatfile=None, tellwave=None, tellspe=None,
         tellthres=None, minlam=None, maxlam=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1, 2, 3, 4, 5]
    fmt = [str, str, str, float, float, float]
    name = ['flatfile', 'tellwave', 'tellspe', 'tellthres', 'minlam',
            'maxlam']
    lname = ['Flat fits file', 'Telluric spectrum', 'Good threshold',
             'Minimum lambda', 'Maximum lambda']
    req = [True, True, True, True, True, True]
    call = [flatfile, tellwave, tellspe, tellthres, minlam, maxlam]
    call_priority = [True, True, True, True, True, True]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(pos, fmt, name, req, call,
                                                    call_priority, lname)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='flatfile')
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)
    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    # get reduced directory + night name
    rdir = p['raw_dir']
    # construct and test the reffile
    flatfilename = spirouStartup.GetFile(p, rdir, p['flatfile'], 'flat_dark',
                                         'TELLMASK')
    # get the fiber type (set to AB)
    p['fiber'] = 'AB'
    # ----------------------------------------------------------------------
    # Read flat image file
    # ----------------------------------------------------------------------
    # read the image data
    flat, hdr, cdr, ny, nx = spirouImage.ReadData(p, flatfilename)
    # create loc
    loc = ParamDict()
    # ----------------------------------------------------------------------
    # Get basic image properties
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')
    # ----------------------------------------------------------------------
    # Resize flat image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    flat = spirouImage.ConvertToE(spirouImage.FlipImage(flat), p=p)
    # convert NaN to zeros
    flat0 = np.where(~np.isfinite(flat), np.zeros_like(flat), flat)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    flat2 = spirouImage.ResizeImage(flat0, **bkwargs)
    # save flat to to loc and set source
    loc['image'] = flat2
    loc.set_sources(['image'], __NAME__ + '/main()')
    # log change in data size
    wmsg = 'Image format changed to {0}x{1}'
    WLOG('', p['log_opt'], wmsg.format(*flat2.shape))
    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # get tilts
    loc['tilt'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('tilt', __NAME__ + '/main() + /spirouImage.ReadTiltFile')
    # set number of orders from tilt length
    loc['nbo'] = len(loc['tilt'])
    loc.set_source('nbo', __NAME__ + '/main()')
    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    loc['blaze'] = spirouImage.ReadBlazeFile(p, hdr)
    loc.set_source('blaze', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')
    # ------------------------------------------------------------------
    # Read wavelength solution
    # ------------------------------------------------------------------
    loc['wave'] = spirouImage.ReadWaveFile(p, hdr)
    loc.set_source('wave', __NAME__ + '/main() + /spirouImage.ReadWaveFile')
    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # get this fibers parameters
    p = spirouLOCOR.FiberParams(p, p['fiber'], merge=True)
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
    # ------------------------------------------------------------------
    # Get telluric and telluric mask and add to loc
    # ------------------------------------------------------------------
    # log process
    wmsg = 'Loading telluric model and locating "good" tranmission'
    WLOG('', p['log_opt'], wmsg)
    # load telluric and get mask (add to loc)
    loc = get_telluric(p, loc)
    # ------------------------------------------------------------------
    # Make 2D map of orders
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Making 2D map of order locations')
    # make the 2D wave-image
    loc = order_profile(loc)
    # ------------------------------------------------------------------
    # Make 2D map of wavelengths accounting for tilt
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Mapping pixels on to wavelength grid')
    # make the 2D map of wavelength
    loc = create_wavelength_image(loc)
    # ------------------------------------------------------------------
    # Use spectra wavelength to create 2D image from wave-image
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Creating image from wave-image interpolation')
    # create image from waveimage
    loc = create_image_from_waveimage(loc, x=loc['tell_x'], y=loc['tell_y'])
    # ------------------------------------------------------------------
    # Create 2D mask (min to max lambda + transmission threshold)
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Creating wavelength/tranmission mask')
    # create mask
    loc = create_mask(p, loc)
    # ----------------------------------------------------------------------
    # save 2D spectrum, wavelength image and mask to file
    # ----------------------------------------------------------------------
    # TODO: move filenames to spirouConst
    # construct spectrum filename
    redfolder = p['reduced_dir']
    specfilename = 'telluric_mapped_spectrum2.fits'
    specfitsfile = os.path.join(redfolder, specfilename)
    # log progress
    wmsg = 'Writing spectrum to file {0}'
    WLOG('', p['log_opt'], wmsg.format(specfilename))
    # write to file
    spirouImage.WriteImage(specfitsfile, loc['spe'])
    # ----------------------------------------------------------------------
    # construct waveimage filename
    wavefilename = 'telluric_mapped_waveimage2.fits'
    wavefitsfile = os.path.join(redfolder, wavefilename)
    # log progress
    wmsg = 'Writing wave image to file {0}'
    WLOG('', p['log_opt'], wmsg.format(wavefilename))
    # write to file
    spirouImage.WriteImage(wavefitsfile, loc['waveimage'])
    # ----------------------------------------------------------------------
    # construct tell mask 2D filename
    maskfilename = 'telluric_mapped_mask2.fits'
    maskfitsfile = os.path.join(redfolder, maskfilename)
    # log progress
    wmsg = 'Writing telluric mask to file {0}'
    WLOG('', p['log_opt'], wmsg.format(maskfilename))
    # convert boolean mask to integers
    writablemask = np.array(loc['tell_mask_2D'], dtype=int)
    # write to file
    spirouImage.WriteImage(maskfitsfile, writablemask)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Define functions
# =============================================================================
def get_telluric(p, loc):
    """
    Reads the telluric file "tellwave" (wavelength data) and "tellspe"
    (telluric absorption data) from files defined in "p" and finds "good" areas
    of the telluric model, i.e. p["minlam"] > wavelength > p["maxlam"] and
    telluric transmission > p["tellthres"]

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            minlam: float, the minimum allowed wavelength (in nm)
            maxlam: float, the maximum allowed wavelength (in nm)
            tellthres: float, the minimum transmission to define good parts of
                       the spectrum

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
    tkwargs = dict(return_header=False, return_shape=False)
    tx = spirouImage.ReadData(p, filename=p['tellwave'], **tkwargs)
    ty = spirouImage.ReadData(p, filename=p['tellspe'], **tkwargs)
    # add model and mask to loc
    loc['tell_x'] = tx
    loc['tell_y'] = ty
    # set source
    loc.set_sources(['tell_x', 'tell_y'], func_name)
    # return loc
    return loc


def order_profile(loc):
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
    image = loc['image']
    acc, ass = loc['acc'], loc['ass']
    # construct a "NaN" image (for wavelengths)
    ishape = image.shape
    # Define empty order image
    orderimage = np.repeat([-1], np.product(ishape)).reshape(ishape)
    suborderimage = np.repeat([-1], np.product(ishape)).reshape(ishape)
    # get the indices locations
    yimage, ximage = np.indices(image.shape)
    # loop around number of orders (AB)
    for order_no in range(loc['nbo']):
        # loop around A and B
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

    # add to loc
    loc['orderimage'] = orderimage
    loc['suborderimage'] = suborderimage
    # add source
    loc.set_sources(['orderimage', 'suborderimage'], func_name)
    # return loc
    return loc


def create_wavelength_image(loc):
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
    image = loc['image']
    wave = loc['wave']
    acc = loc['acc']
    tilt = loc['tilt']
    suborderimage = loc['suborderimage']
    # construct a "NaN" image (for wavelengths)
    ishape = image.shape
    # construct
    waveimage = np.repeat([np.nan], np.product(ishape)).reshape(ishape)
    # get the indices locations
    yimage, ximage = np.indices(image.shape)
    # loop around number of orders (AB)
    for order_no in range(loc['nbo']):

        # get wavelength coefficients for this order
        # TODO: in future this fit should have already be done!
        awave0 = fit_wavelength(ximage[0], wave[order_no])
        # get first derivative of wavelength coefficients
        awave1 = np.polyder(awave0, 1)
        # get second derivative of wavelength coefficients
        awave2 = np.polyder(awave0, 2)
        # get third derivative of wavelength coefficients
        awave3 = np.polyder(awave0, 3)
        # loop around A and B
        for fno in [0, 1]:
            # get fiber iteration number
            fin = 2*order_no + fno
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
            lambda2 = np.polyval(awave2, x0s) * deltax**2
            lambda3 = np.polyval(awave3, x0s) * deltax**3
            # sum of lambdas
            lambda_total = lambda0 + lambda1 + lambda2 + lambda3
            # add to array
            waveimage[y0s, x0s] = lambda_total

    # add to loc
    loc['waveimage'] = waveimage
    # set source
    loc.set_source('waveimage', func_name)
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
    wavelength positions in loc['waveimage'] to map the spectrum onto
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
    waveimage = loc['waveimage']
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
    loc['spe'] = newimage
    loc.set_source('spe', func_name)
    # return loc
    return loc


def create_mask(p, loc):
    """
    Create a mask of a telluric spectrum

    Mask criteria (value = 1 if True or 0 elsewise)

        p['minlam'] < loc['waveimage'] < p['maxlam']

        loc['spe'] > p['tellthres']

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            minlam: float, the minimum wavelength allowed (in the same units as
                    the loc['waveimage'])
            maxlam: float, the maximum wavelength allowed (in the same units as
                    the loc['waveimage'])
            tellthres: float, the threshold value for the spectrum, above this
                       value mask is True
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
    waveimage = loc['waveimage']
    tell_spe = loc['spe']
    # apply mask to telluric model
    with warnings.catch_warnings(record=True) as _:
        mask1 = waveimage > p['minlam']
        mask2 = waveimage < p['maxlam']
        mask3 = tell_spe > p['tellthres']
    # combine masks
    mask = mask1 & mask2 & mask3
    # save mask to loc
    loc['tell_mask_2D'] = mask
    loc.set_source('tell_mask_2D', func_name)
    # return loc
    return loc


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # function inputs
    # TODO: This should be removed when function in main()
    kwargs = dict(night_name='20170710', flatfile=FLATFILE, tellwave=TAPASX,
                  tellspe=TAPASY, tellthres=THRESHOLD, minlam=MINLAM,
                  maxlam=MAXLAM)
    # TODO: Should remove kwargs
    ll = main(**kwargs)
    # exit message
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================

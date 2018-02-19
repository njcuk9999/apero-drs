#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-02-15 at 14:05

@author: cook



Version 0.0.0
"""

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
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
MINLAM = 1500
MAXLAM = 1800
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, flatfile=None, tellfile=None, tellthres=None,
         minlam=None, maxlam=None):


    # return a copy of locally defined variables in the memory
    return dict(locals())


def get_telluric(p, loc):
    """
    Reads the telluric file "tellmodx" (wavelength data) and "tellmody"
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
    kwargs = dict(return_header=False, return_shape=False)
    tx = spirouImage.ReadData(p, filename=p['tellmodx'], **kwargs)
    ty = spirouImage.ReadData(p, filename=p['tellmody'], **kwargs)
    # apply mask to telluric model
    mask1 = tx > p['minlam']
    mask2 = tx < p['maxlam']
    mask3 = ty > p['tellthres']
    # combine masks
    mask = mask1 & mask2 & mask3
    # add model and mask to loc
    loc['tell_x'] = tx
    loc['tell_y'] = ty
    loc['tell_mask'] = mask
    # set source
    loc.set_sources(['tell_x', 'tell_y', 'tell_mask'], func_name)
    # return loc
    return loc


def make_2d_wave_image(p, loc):
    """

    :param p: parameter dictionary, ParamDict containing constants

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                flat2: numpy array (2D), the flat image
                      shape = (number of orders x number of columns (x-dir)
                wave: numpy array (2D), the wave solution image
                tilt: numpy array (1D), the tilt angle of each order
                acc: numpy array (2D), the fit coefficients array for
                      the centers fit
                      shape = (number of orders x number of fit coefficients)
                ass: numpy array (2D), the fit coefficients array for
                      the widths fit
                      shape = (number of orders x number of fit coefficients)
    :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                waveimage: numpy array (2D), the wavelengths of every pixel
                           for all orders
                           shape = (number of columns x number of rows)
                                   i.e. the same size as original image
    """
    func_name = __NAME__ + '.make_2d_wave_image()'
    # get data from loc
    image = loc['flat2']
    wave = loc['wave']
    tilt = loc['tilt']
    acc, ass = loc['acc'], loc['ass']
    # assign number of orders
    number_orders = len(wave)
    # construct a "NaN" image (for wavelengths)
    ishape = image.shape

    # TODO: change to np.nan array
    waveimage = np.repeat([np.nan], np.product(ishape)).reshape(ishape)

    waveimage = np.zeros_like(image)

    # make 2D image of wavelength positions (super imposed on nan image)
    # central values are easy
    # values around are difficult (have tilt)

    # get xpixel positions
    xpos = np.arange(image.shape[1])
    # loop around number of orders (AB)
    for order_no in range(number_orders):
        # loop around A and B
        for fno in [0, 1]:
            # get fiber iteration number
            fin = 2*order_no + fno
            # get central positions
            cfit = np.polyval(acc[fin][::-1], xpos)
            # get width positions
            wfit = np.polyval(ass[fin][::-1], xpos)
            # get tilt
            otilt = tilt[order_no]
            # calculate pixel positions for each center
            #     need +0.5 for int rounding
            ypos = np.array(cfit + 0.5, dtype=int)
            # calculate pixel widths for each width
            widths = np.array(wfit + 0.5, dtype=int)
            # loop around each width
            for w_it, width in enumerate(widths):
                # loop around all pixels in width
                for pix in range(-width//2, width//2):
                    # get this iterations position and wave value
                    yposi = ypos[w_it] + pix
                    xposi = xpos[w_it]
                    # add wavelength values at correct positions
                    waveimage[yposi, xposi] = wave[order_no][w_it]

    # add to loc
    loc['waveimage'] = waveimage
    # set source
    loc.set_source('waveimage', func_name)

    return loc


def create_image_from_waveimage(p, loc, x, y):
    """
    Takes a spectrum "y" at wavelengths "x" and uses these to interpolate
    wavelength positions in loc['waveimage'] to map the spectrum onto
    the waveimage

    :param p: parameter dictionary, ParamDict containing constants

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                waveimage: numpy array (2D), the wavelengths of every pixel
                           for all orders
                           shape = (number of columns x number of rows)
                                   i.e. the same size as original image
    :param x: numpy array (1D), the wavelength values for each spectrum pixel
    :param y: numpy array (1D), the
    :return:
    """
    func_name = __NAME__ + '.create_image_from_waveimage()'
    # get data from loc
    waveimage = loc['waveimage']
    # set up interpolation
    F = interp1d(x, y)
    # create new spectrum
    newimage = np.zeros_like(waveimage)
    # loop around each row in image, interpolate wavevalues
    for row in range(len(waveimage)):
        # get row values
        rvalues = waveimage[row]
        # TODO change mask out zeros to NaNs
        # mask out zeros (NaNs in future)
        invalidpixels = (rvalues == 0)
        # don't try to interpolate those pixels outside range of "x"
        invalidpixels |= rvalues < np.min(x)
        invalidpixels |= rvalues > np.max(x)
        # valid pixel definition
        validpixels = ~invalidpixels
        # check that we have some valid pixels
        if np.sum(validpixels) == 0:
            continue
        # interpolate wavelengths in waveimage to get newimage
        newimage[row][validpixels] = F(rvalues[validpixels])
    # add to loc
    loc['spe'] = newimage
    loc.set_source('spe', func_name)
    # return loc
    return loc



# =============================================================================
# Define plotting
# =============================================================================
def test_image(loc):
    """
    Test image: plot the flat image with the superimposed localisation fits
    on top for all orders
    """
    # get data from loc
    image = loc['flat2']
    acc, ass = loc['acc'], loc['ass']
    # plot
    plt.imshow(image)
    for it in range(len(acc)):
        xfit = np.arange(image.shape[1])
        cfit = np.polyval(acc[it][::-1], xfit)
        wfit = np.polyval(ass[it][::-1], xfit)
        p = plt.plot(xfit, cfit - wfit/2, ls='--')
        plt.plot(xfit, cfit, ls='-', color=p[0].get_color())
        plt.plot(xfit, cfit + wfit/2, ls='--', color=p[0].get_color())
    plt.show()
    plt.close()


def test_spec(loc):

    # get data from loc
    waveimage = loc['waveimage']
    spec = loc['spe']
    x, y = loc['tell_x'], loc['tell_y']

    # set zeros to NaN
    mask1 = waveimage == 0
    waveimage[mask1] = np.nan
    mask2 = spec == 0
    spec[mask2] = np.nan

    plt.close()

    # plot input spectrum
    fig0, frame0 = plt.subplots(ncols=1, nrows=1)
    frame0.plot(x, y)
    frame0.set(xlim=(1000, 2500), ylim=(0.8, 1.01),
               xlabel='Wavelength', ylabel='Transmission')

    # plot wavelength map
    fig1, frame1 = plt.subplots(ncols=1, nrows=1)
    frame1.set_facecolor('black')
    im1 = frame1.imshow(waveimage, vmin=1000, vmax=2500, cmap='inferno')
    cb1 = plt.colorbar(im1, ax=frame1)
    frame1.set(title='Wavelength Map')
    cb1.set_label('Wavelength')

    # plot spectrum map
    fig2, frame2 = plt.subplots(ncols=1, nrows=1)
    frame2.set_facecolor('black')
    im2 = frame2.imshow(spec, vmin=0.95, vmax=1.0, cmap='inferno')
    cb2 = plt.colorbar(im2, ax=frame2)
    frame2.set(title='Spectrum Interpolation')
    cb2.set_label('Transmission')

    plt.show()
    plt.close()


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # function inputs
    # TODO: This should be removed when function in main()
    night_name = '20170710'
    flatfile = FLATFILE
    tellmodx = TAPASX
    tellmody = TAPASY
    tellthres = THRESHOLD
    minlam, maxlam = MINLAM, MAXLAM

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1, 2, 3, 4, 5]
    fmt = [str, str, str, float, float, float]
    name = ['flatfile', 'tellmodx', 'tellmody', 'tellthres', 'minlam',
            'maxlam']
    lname = ['Flat fits file', 'Telluric spectrum', 'Good threshold',
             'Minimum lambda', 'Maximum lambda']
    req = [True, True, True, True, True, True]
    call = [flatfile, tellmodx, tellmody, tellthres, minlam, maxlam]
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
    # get the fiber type
    p['fiber'] = 'AB'

    # ----------------------------------------------------------------------
    # Read flat image file
    # ----------------------------------------------------------------------
    # read the image data
    flat, hdr, cdr, ny, nx = spirouImage.ReadData(p, flatfilename)
    # add to loc
    loc = ParamDict()
    loc['flat'] = flat
    loc.set_sources(['flat'], __NAME__ + '/main()')

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
    loc['flat2'] = flat2
    loc.set_sources(['flat2'], __NAME__ + '/main()')
    # log change in data size
    WLOG('', p['log_opt'], ('Image format changed to '
                            '{0}x{1}').format(*flat2.shape))

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # get tilts
    loc['tilt'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('tilt', __NAME__ + '/main() + /spirouImage.ReadTiltFile')

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
    # Make 2D wave-image from flat, loc, wave, tilt
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Constructing 2D wave-image')
    # make the 2D wave-image
    loc = make_2d_wave_image(p, loc)

    # ------------------------------------------------------------------
    # Use spectra wavelength to create 2D image from wave-image
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Creating image from wave-image interpolation')
    # create image from waveimage
    loc = create_image_from_waveimage(p, loc, x=loc['tell_x'], y=loc['tell_y'])

    # ----------------------------------------------------------------------
    # save 2D spectrum and wavelength image to file
    # ----------------------------------------------------------------------
    # TODO: move to spirouConst
    # construct spectrum filename
    redfolder = p['reduced_dir']
    specfilename = 'telluric_mapped_spectrum.fits'
    specfitsfile = os.path.join(redfolder, specfilename)
    # log progress
    wmsg = 'Writing spectrum to file {0}'
    WLOG('', p['log_opt'], wmsg.format(specfilename))
    # write to file
    spirouImage.WriteImage(specfitsfile, loc['spe'])
    # ----------------------------------------------------------------------
    # construct waveimage filename
    wavefilename = 'telluric_mapped_waveimage.fits'
    wavefitsfile = os.path.join(redfolder, wavefilename)
    # log progress
    wmsg = 'Writing wave image to file {0}'
    WLOG('', p['log_opt'], wmsg.format(wavefilename))
    # write to file
    spirouImage.WriteImage(wavefitsfile, loc['waveimage'])

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))


# =============================================================================
# End of code
# =============================================================================

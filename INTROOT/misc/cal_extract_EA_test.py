#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-19 at 16:31

@author: cook
"""
from __future__ import division
import numpy as np
import os
from astropy.io import fits
from scipy.interpolate import InterpolatedUnivariateSpline
import matplotlib.pyplot as plt

from SpirouDRS import spirouBACK
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouEXTOR
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup

from SpirouDRS.spirouEXTOR.spirouEXTOR import *

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_extract_RAW_spirou.py'
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
# define night name
night_name = 'TEST1/20180805'
# define filename
files = ['2295680c_pp.fits']
files = ['2295546o_pp.fits']
# define fiber_type
fiber_type = None
fiber = 'AB'
# define kwargs
kwargs = dict(IC_EXT_TILT_BORD=10)
# define order number
selected_order = 33
selected_order = None
# save dir for outputs
savedir = '/scratch/Projects/spirou_py3/data_ea/extract_test/'
# turn on plotting
plot = False


# =============================================================================
# Define functions
# =============================================================================
def part1(night_name, files, fiber_type, kwargs, fiber):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
    # deal with fiber type
    if fiber_type is None:
        fiber_type = p['FIBER_TYPES']
    if type(fiber_type) == str:
        if fiber_type.upper() == 'ALL':
            fiber_type = p['FIBER_TYPES']
        elif fiber_type in p['FIBER_TYPES']:
            fiber_type = [fiber_type]
        else:
            emsg = 'fiber_type="{0}" not understood'
            WLOG('error', p['LOG_OPT'], emsg.format(fiber_type))
    # set fiber type
    p['FIB_TYPE'] = fiber_type
    p.set_source('FIB_TYPE', __NAME__ + '__main__()')
    # Overwrite keys from source
    for kwarg in kwargs:
        p[kwarg] = kwargs[kwarg]

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, data, hdr, cdr = spirouImage.ReadImageAndCombine(p, framemath='add')

    # ----------------------------------------------------------------------
    # fix for un-preprocessed files
    # ----------------------------------------------------------------------
    data = spirouImage.FixNonPreProcess(p, data)

    # ----------------------------------------------------------------------
    # Get basic image properties
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # now change the value of sigdet if require
    if p['IC_EXT_SIGDET'] > 0:
        p['SIGDET'] = float(p['IC_EXT_SIGDET'])
    # get DPRTYPE from header (Will have it if valid)
    p = spirouImage.ReadParam(p, hdr, 'KW_DPRTYPE', required=False, dtype=str)
    # check the DPRTYPE is not None
    if (p['DPRTYPE'] == 'None') or (['DPRTYPE'] is None):
        emsg1 = 'Error: {0} is not set in header for file {1}'
        eargs = [p['KW_DPRTYPE'][0], p['FITSFILENAME']]
        emsg2 = '\tPlease run pre-processing on file.'
        emsg3 = ('\tIf pre-processing fails or skips file, file is not '
                 'currrently as valid DRS fits file.')
        WLOG('error', p['LOG_OPT'], [emsg1.format(*eargs), emsg2, emsg3])
    else:
        p['DPRTYPE'] = p['DPRTYPE'].strip()

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to ADU
    data = spirouImage.ConvertToADU(spirouImage.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    wmsg = 'Image format changed to {1}x{0}'
    WLOG('', p['LOG_OPT'], wmsg.format(*data2.shape))

    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    data2 = spirouImage.CorrectForBadPix(p, data2, hdr)

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 == 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.4f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get the miny, maxy and max_signal for the central column
    # ----------------------------------------------------------------------
    # get the central column
    y = data2[p['IC_CENT_COL'], :]
    # get the min max and max signal using box smoothed approach
    miny, maxy, max_signal, diff_maxmin = spirouBACK.MeasureMinMaxSignal(p, y)
    # Log max average flux/pixel
    wmsg = 'Maximum average flux/pixel in the spectrum: {0:.1f} [ADU]'
    WLOG('info', p['LOG_OPT'], wmsg.format(max_signal / p['NBFRAMES']))

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG('', p['LOG_OPT'], 'Doing background measurement on raw frame')
        # get the bkgr measurement
        background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(p, data2)
    else:
        background = np.zeros_like(data2)
    # apply background correction to data (and set to zero where negative)
    data2 = np.where(data2 > 0, data2 - background, 0)

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # define loc storage parameter dictionary
    loc = ParamDict()
    # get tilts
    loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('TILT', __NAME__ + '/main() + /spirouImage.ReadTiltFile')

    # ----------------------------------------------------------------------
    #  Earth Velocity calculation
    # ----------------------------------------------------------------------
    if p['IC_IMAGE_TYPE'] == 'H4RG':
        p, loc = spirouImage.GetEarthVelocityCorrection(p, loc, hdr)

    # ----------------------------------------------------------------------
    # Fiber loop
    # ----------------------------------------------------------------------

    # set fiber
    p['FIBER'] = fiber
    p.set_source('FIBER', __NAME__ + '/main()()')

    # ------------------------------------------------------------------
    # Read wavelength solution
    # ------------------------------------------------------------------
    wdata = spirouImage.ReadWaveFile(p, hdr, return_header=True)
    loc['WAVE'], loc['WAVEHDR'] = wdata
    wavefile = spirouImage.ReadWaveFile(p, hdr, return_filename=True)
    loc['WAVEFILE'] = os.path.basename(wavefile)
    skeys = ['WAVE', 'WAVEFILE']
    loc.set_sources(skeys, __NAME__ + '.main + .spirouImage.ReadWaveFile()')
    # get wave params from wave header
    loc['WAVEPARAMS'] = spirouImage.ReadWaveParams(p, loc['WAVEHDR'])
    loc.set_source('WAVEPARAMS', '.main() + spirouImage.ReaveWaveParams()')

    # get dates
    loc['WAVE_ACQTIMES'] = spirouDB.GetTimes(p, loc['WAVEHDR'])

    # ----------------------------------------------------------------------
    # Read Flat file
    # ----------------------------------------------------------------------
    loc['FLAT'] = spirouImage.ReadFlatFile(p, hdr)
    loc.set_source('FLAT', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    loc['FLAT'] = np.where(loc['FLAT'] == 0, 1.0, loc['FLAT'])

    # ------------------------------------------------------------------
    # Read Blaze file
    # ------------------------------------------------------------------
    loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hdr)
    blazesource = __NAME__ + '/main() + /spirouImage.ReadBlazeFile'
    loc.set_source('BLAZE', blazesource)

    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # get this fibers parameters
    p = spirouImage.FiberParams(p, p['FIBER'], merge=True)
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
    # ------------------------------------------------------------------
    # Read image order profile
    # ------------------------------------------------------------------
    order_profile, _, _, nx, ny = spirouImage.ReadOrderProfile(p, hdr)
    # ------------------------------------------------------------------
    # Average AB into one fiber for AB, A and B
    # ------------------------------------------------------------------
    # if we have an AB fiber merge fit coefficients by taking the average
    # of the coefficients
    # (i.e. average of the 1st and 2nd, average of 3rd and 4th, ...)
    # if fiber is AB take the average of the orders
    if fiber == 'AB':
        # merge
        loc['ACC'] = spirouLOCOR.MergeCoefficients(loc, loc['ACC'], step=2)
        loc['ASS'] = spirouLOCOR.MergeCoefficients(loc, loc['ASS'], step=2)
        # set the number of order to half of the original
        loc['NUMBER_ORDERS'] = int(loc['NUMBER_ORDERS'] / 2.0)
    # if fiber is B take the even orders
    elif fiber == 'B':
        loc['ACC'] = loc['ACC'][:-1:2]
        loc['ASS'] = loc['ASS'][:-1:2]
        loc['NUMBER_ORDERS'] = int(loc['NUMBER_ORDERS'] / 2.0)
    # if fiber is A take the even orders
    elif fiber == 'A':
        loc['ACC'] = loc['ACC'][1::2]
        loc['ASS'] = loc['ASS'][:-1:2]
        loc['NUMBER_ORDERS'] = int(loc['NUMBER_ORDERS'] / 2.0)

    # ------------------------------------------------------------------
    # Set up Extract storage
    # ------------------------------------------------------------------
    # Create array to store extraction (for each order and each pixel
    # along order)
    loc['E2DS'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    loc['E2DSFF'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    loc['SPE1'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    loc['SPE3'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    loc['SPE4'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    loc['SPE5'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    # Create array to store the signal to noise ratios for each order
    loc['SNR'] = np.zeros(loc['NUMBER_ORDERS'])

    loc['E2DS_1'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    loc['E2DSFF_1'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    loc['SNR_1'] = np.zeros(loc['NUMBER_ORDERS'])

    # ------------------------------------------------------------------
    # Extract orders
    # ------------------------------------------------------------------
    # source for parameter dictionary
    source = __NAME__ + '/main()'
    # get limits of order extraction
    valid_orders = spirouEXTOR.GetValidOrders(p, loc)

    # return to main
    return p, loc, data2, valid_orders, order_profile, source


def part2(p, loc, data2, order_num, order_profile):
    eargs = [p, loc, data2, order_num]
    ekwargs = dict(mode=p['IC_EXTRACT_TYPE'],
                   order_profile=order_profile)

    # ************************************************************************
    #
    #     spirouEXTOR.extraction_wrapper
    #
    # ************************************************************************
    p, loc, image, rnum = eargs
    mode = ekwargs['mode']
    order_profile = ekwargs['order_profile']

    # -------------------------------------------------------------------------
    # Getting and checking globally used parameters
    # -------------------------------------------------------------------------
    # make sure mode is a string
    mode = str(mode)
    # check for an image
    check_for_none(image, 'image')
    # check and get localisation position "ACC" from loc
    posall = kwargs.get('posall', loc.get('ACC', None))
    pos = get_check_for_orderlist_none(p, posall, 'ACC', rnum)
    # also check for a single order position coming in from kwargs
    pos = kwargs.get('pos', pos)
    # get gain
    gain = kwargs.get('gain', p.get('GAIN', None))
    check_for_none(gain, 'gain')
    # get sigdet (but don't test until used)
    sigdet = kwargs.get('sigdet', p.get('SIGDET', None))
    # get tilt (but don't test until used)
    tiltall = kwargs.get('tilt', loc.get('TILT', None))
    # get tilt border (not don't test until used)
    tiltborder = kwargs.get('tiltborder', p.get('IC_EXT_TILT_BORD', None))

    # get and check values
    range1 = kwargs.get('range1', p['IC_EXT_RANGE1'])
    range2 = kwargs.get('range2', p['IC_EXT_RANGE2'])
    cosmic_sigcut = kwargs.get('csigcut', p['IC_COSMIC_SIGCUT'])
    cosmic_threshold = kwargs.get('cthres', p['IC_COSMIC_THRESH'])
    check_for_none(range1, 'range1')
    check_for_none(range2, 'range2')
    check_for_none(order_profile, 'Order Profile Image')
    check_for_none(sigdet, 'SIGDET')
    tilt = get_check_for_orderlist_none(p, tiltall, 'TILT', rnum)
    check_for_none(tiltborder, 'Tilt Pixel Border')

    # ************************************************************************
    #
    #     spirouEXTOR.extraction_wrapper
    #
    # ************************************************************************
    r1, r2, orderp = range1, range2, order_profile

    return (image, pos, tilt, r1, r2, orderp, gain, sigdet,
            tiltborder, cosmic_sigcut, cosmic_threshold)


def part3(p, loc, e2ds, cpt, data2, order_num, source, kind=0):
    # calculate the noise
    range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
    # set the noise
    noise = p['SIGDET'] * np.sqrt(range1 + range2)
    # get window size
    blaze_win1 = int(data2.shape[0] / 2) - p['IC_EXTFBLAZ']
    blaze_win2 = int(data2.shape[0] / 2) + p['IC_EXTFBLAZ']
    # get average flux per pixel
    flux = np.sum(e2ds[blaze_win1:blaze_win2]) / (2 * p['IC_EXTFBLAZ'])
    # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
    snr = flux / np.sqrt(flux + noise ** 2)
    # log the SNR RMS
    if kind == 0:
        kindstr = 'OLD --'
        ext = ''
    else:
        kindstr = 'NEW -- '
        ext = '_1'

    wmsg = '{0} On fiber {1} order {2}: S/N= {3:.1f} Nbcosmic= {4}'
    wargs = [kindstr, p['FIBER'], order_num, snr, cpt]
    WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
    # add calculations to storage
    e2ds = np.where(loc['BLAZE'][order_num] > 1, e2ds, 0.)
    loc['E2DS' + ext][order_num] = e2ds
    loc['E2DSFF' + ext][order_num] = e2ds / loc['FLAT'][order_num]
    loc['SNR' + ext][order_num] = snr
    # set sources
    loc.set_sources(['E2DS' + ext, 'SNR' + ext], source)
    # Log if saturation level reached
    satvalue = (flux / p['GAIN']) / (range1 + range2)
    if satvalue > (p['QC_LOC_FLUMAX'] * p['NBFRAMES']):
        wmsg = 'SATURATION LEVEL REACHED on Fiber {0} order={1}'
        WLOG('warning', p['LOG_OPT'], wmsg.format(fiber, order_num))

    return loc


def plot_compare_ww(ww, wwea):
    plt.ion()
    fig, frames = plt.subplots(nrows=1, ncols=3)

    frames[0].imshow(ww)
    frames[0].set(title='Original')

    frames[1].imshow(wwea)
    frames[1].set(title='New')

    frames[2].imshow(ww - wwea)
    frames[2].set(title='Original - New')


def plot_spelong(spelong):
    plt.ion()
    fig, frame = plt.subplots(nrows=1, ncols=1)
    frame.imshow(spelong, origin='lower')


def debanananificator(image, dx):
    # getting the size of the image and creating the image after correction of
    # distortion
    image1 = np.array(image)
    sz = np.shape(dx)

    # x indices in the initial image
    xpix = np.array(range(sz[1]))

    # we shift all lines by the appropiate, pixel-dependent, dx
    for i in range(sz[0]):
        not0 = image[i, :] != 0
        spline = InterpolatedUnivariateSpline(xpix[not0], image[i, not0], ext=1)
        # only pixels where dx is finite are considered
        g = np.isfinite(dx[i, :])
        image1[i, g] = spline(xpix[g] + dx[i, g])

    return image1


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":

    # Get to order loop
    output1 = part1(night_name, files, fiber_type, kwargs, fiber)
    p, loc, data, valid_orders, order_profile, source = output1

    # turn on/off using a single order
    if selected_order is not None:
        valid_orders = [selected_order]

    # storage
    e2ds = []
    e2dslong = []
    e2ds1 = []
    e2dslong1 = []
    f2ds = []
    f2dslong = []
    f2ds1 = []
    f2dslong1 = []

    # need to debanananify for EA method
    WLOG('', p['LOG_OPT'], 'Running debanananification')
    data1 = debanananificator(data, SHAPEMAP)
    order_profile1 = debanananificator(order_profile, SHAPEMAP)

    # loop around each order
    for order_num in valid_orders:

        WLOG('', p['LOG_OPT'], 'Order {0}'.format(order_num))

        # Get to spirouEXTOR.extract_shape_weight_cosm
        output1 = part2(p, loc, data, order_num, order_profile)
        image, pos, tilt, r1, r2, orderp, gain, sigdet = output1[:8]
        tiltborder, cosmic_sigcut, cosmic_threshold = output1[8:]

        # Get to spirouEXTOR.extract_shape_weight_cosm
        output2 = part2(p, loc, data1, order_num, order_profile1)
        image1, orderp1 = output2[0], output2[5]

        # ********************************************************************
        #
        #     spirouEXTOR.spirouEXTOR.extract_shape_weight_cosm
        #
        # ********************************************************************
        dim1, dim2 = image.shape
        # create storage for extration
        spe = np.zeros(dim2, dtype=float)
        spe1 = np.zeros(dim2, dtype=float)
        fpe = np.zeros(dim2, dtype=float)
        fpe1 = np.zeros(dim2, dtype=float)
        # create array of pixel values
        ics = np.arange(dim2)
        # get positions across the orders for each pixel value along the order
        jcs = np.polyval(pos[::-1], ics)
        # get the lower bound of the order for each pixel value along the order
        lim1s = jcs - r1
        # get the upper bound of the order for each pixel value along the order
        lim2s = jcs + r2
        # get the pixels around the order
        i1s = ics - tiltborder
        i2s = ics + tiltborder
        # get the integer pixel position of the lower bounds
        j1s = np.array(np.round(lim1s), dtype=int)
        # get the integer pixel position of the upper bounds
        j2s = np.array(np.round(lim2s), dtype=int)
        # make sure the pixel positions are within the image
        mask = (j1s > 0) & (j2s < dim1)
        # get the ranges ww0 = j2-j1+1, ww1 = i2-i1+1
        ww00, ww01 = j2s - j1s + 1, i2s - i1s + 1
        # calculate the tilt shift
        tiltshift = np.tan(np.deg2rad(tilt))
        # get the weight contribution matrix (look up table)
        wwa = work_out_ww(ww00, ww01, tiltshift, r1)
        # count of the detected cosmic rays
        cpt = 0
        cpt1 = 0
        spelong = np.zeros((np.max(j2s - j1s) + 1, dim2), dtype=float)
        spelong1 = np.zeros((np.max(j2s - j1s) + 1, dim2), dtype=float)
        fpelong = np.zeros((np.max(j2s - j1s) + 1, dim2), dtype=float)
        fpelong1 = np.zeros((np.max(j2s - j1s) + 1, dim2), dtype=float)

        # ---------------------------------------------------------------------
        # loop around each pixel along the order
        for ic in ics[tiltborder:-tiltborder]:
            if mask[ic]:
                # get ww0i and ww1i for this iteration
                ww00i, ww01i = ww00[ic], ww01[ic]
                ww = wwa[(ww00i, ww01i)]
                # multiple the image by the rotation matrix
                sx = image[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
                # multiple the order_profile by the rotation matrix
                fx = orderp[j1s[ic]:j2s[ic] + 1, i1s[ic]:i2s[ic] + 1] * ww
                # Renormalise the rotated order profile
                if np.sum(fx) > 0:
                    fx = fx / np.sum(fx)
                else:
                    fx = np.ones(fx.shape, dtype=float)
                # weight values less than 0 to 1e-9
                raw_weights = np.where(sx > 0, 1, 1e-9)
                # weights are then modified by the gain and sigdet added in
                #    quadrature
                weights = raw_weights / ((sx * gain) + sigdet ** 2)
                # set the value of this pixel to the weighted sum
                sumA = np.sum(weights * sx * fx, axis=1)
                sumB = np.sum(weights * fx ** 2, axis=1)
                spelong[:, ic] = sumA / sumB
                spe[ic] = np.sum(weights * sx * fx) / np.sum(weights * fx ** 2)
                fpelong[:, ic] = np.sum(fx, axis=1)
                fpe[ic] = np.sum(fx)

                # Cosmic rays correction
                spe, cpt = cosmic_correction(sx, spe, fx, ic, weights, cpt,
                                             cosmic_sigcut, cosmic_threshold)
        # ---------------------------------------------------------------------
        # EA method
        for ic in ics:
            if mask[ic]:
                # extract the straighted image
                sx1 = image1[j1s[ic]:j2s[ic] + 1, ic]
                fx1 = orderp1[j1s[ic]:j2s[ic] + 1, ic]
                # Renormalise the rotated order profile
                if np.sum(fx1) > 0:
                    fx1 = fx1 / np.sum(fx1)
                else:
                    fx1 = np.ones(fx1.shape, dtype=float)
                # weight values less than 0 to 1e-9
                raw_weights1 = np.where(sx1 > 0, 1, 1e-9)
                # weights are then modified by the gain and sigdet added in
                #    quadrature
                weights1 = raw_weights1 / ((sx1 * gain) + sigdet ** 2)
                # set the value of this pixel to the weighted sum
                A1 = weights1 * sx1 * fx1
                B1 = weights1 * fx1 ** 2
                spelong1[:, ic] = A1 / B1
                spe1[ic] = np.sum(A1) / np.sum(B1)
                fpelong1[:, ic] = fx1
                fpe1[ic] = np.sum(fx1)
                # Cosmic rays correction
                spe1, cpt1 = cosmic_correction(sx1, spe1, fx1, ic, weights1,
                                               cpt1, cosmic_sigcut,
                                               cosmic_threshold)
        # ---------------------------------------------------------------------
        # multiple by gain
        spe *= gain
        spe1 *= gain

        # part 3
        loc = part3(p, loc, np.array(spe), cpt, data, order_num, source,
                    kind=0)
        loc = part3(p, loc, np.array(spe1), cpt1, data1, order_num, source,
                    kind=1)
        # append storage
        e2ds.append(spe)
        e2dslong.append(spelong)
        e2ds1.append(spe1)
        e2dslong1.append(spelong1)
        f2ds.append(fpe)
        f2dslong.append(fpelong)
        f2ds1.append(fpe1)
        f2dslong1.append(fpelong1)

    # convert e2ds to array
    e2dsarray = np.array(e2ds)
    e2dsarray1 = np.array(e2ds1)
    f2dsarray = np.array(f2ds)
    f2dsarray1 = np.array(f2ds1)
    # stack e2dslong
    e2dslongarray = np.vstack(e2dslong)
    e2dslongarray1 = np.vstack(e2dslong1)
    f2dslongarray = np.vstack(f2dslong)
    f2dslongarray1 = np.vstack(f2dslong1)
    # save arrays
    absfilename = savedir + p['ARG_FILE_NAMES'][0]
    fiberstrA = '_E2DS_{0}.fits'.format(p['FIBER'])
    fiberstrB = '_E2DSLL_{0}.fits'.format(p['FIBER'])
    fiberstrA1 = '_E2DS_1_{0}.fits'.format(p['FIBER'])
    fiberstrB1 = '_E2DSLL_1_{0}.fits'.format(p['FIBER'])

    ffiberstrA = '_F2DS_{0}.fits'.format(p['FIBER'])
    ffiberstrB = '_F2DSLL_{0}.fits'.format(p['FIBER'])
    ffiberstrA1 = '_F2DS_1_{0}.fits'.format(p['FIBER'])
    ffiberstrB1 = '_F2DSLL_1_{0}.fits'.format(p['FIBER'])

    fits.writeto(absfilename.replace('.fits', fiberstrA), e2dsarray,
                 overwrite=True)
    fits.writeto(absfilename.replace('.fits', fiberstrB), e2dslongarray,
                 overwrite=True)
    fits.writeto(absfilename.replace('.fits', fiberstrA1), e2dsarray1,
                 overwrite=True)
    fits.writeto(absfilename.replace('.fits', fiberstrB1), e2dslongarray1,
                 overwrite=True)

    fits.writeto(absfilename.replace('.fits', ffiberstrA), f2dsarray,
                 overwrite=True)
    fits.writeto(absfilename.replace('.fits', ffiberstrB), f2dslongarray,
                 overwrite=True)
    fits.writeto(absfilename.replace('.fits', ffiberstrA1), f2dsarray1,
                 overwrite=True)
    fits.writeto(absfilename.replace('.fits', ffiberstrB1), f2dslongarray1,
                 overwrite=True)

# =============================================================================
# End of code
# =============================================================================

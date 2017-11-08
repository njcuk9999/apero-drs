#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_SLIT_spirou

Flat Field

Created on 2017-11-06 11:32

@author: cook

Version 0.0.1
"""
import numpy as np
import os
import time

from SpirouDRS import spirouCDB
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS.spirouCore import spirouPlot as sPlt

neilstart = time.time()

# =============================================================================
# Define variables
# =============================================================================
# Get Logging function
WLOG = spirouCore.wlog
# Name of program
__NAME__ = 'cal_SLIT_spirou.py'
# -----------------------------------------------------------------------------
# Remove this for final (only for testing)
import sys
if len(sys.argv) == 1:
    sys.argv = ['test.py', '20170710', 'fp_fp02a203.fits', 'fp_fp03a203.fits',
                'fp_fp04a203.fits']

# =============================================================================
# Define functions
# =============================================================================
def get_tilt(pp, lloc, image):
    """
    Get the tilt by correlating the extracted fibers

    :param pp: dictionary, parameter dictionary
    :param lloc: dictionary, parameter dictionary containing the data
    :param image: numpy array (2D), the image

    :return lloc: dictionary, parameter dictionary containing the data
    """
    nbo = lloc['number_orders']
    nx2, ny2 = image.shape
    # storage for "nbcos"
    # Question: what is nbcos?
    lloc['nbcos'] = np.zeros(nbo, dtype=int)
    lloc.set_source('nbcos', __NAME__ + '/get_tilt()')
    # storage for blaze
    blaze = np.zeros((nbo, ny2), dtype=float)
    # storage for rms
    rms = np.zeros(nbo, dtype=float)
    # storage for tilt
    lloc['tilt'] = np.zeros(int(nbo/2), dtype=float)
    lloc.set_source('tilt', __NAME__ + '/get_tilt()')
    # loop around each order
    for order_num in range(0, nbo, 2):
        # extract this AB order
        lloc = extract_AB_order(pp, lloc, order_num)
        # --------------------------------------------------------------------
        # Over sample the data and interpolate new extraction values
        pixels = np.arange(data2.shape[1])
        os_pixels = np.arange(data2.shape[1] * p['COI']) / p['COI']
        cent1i = np.interp(os_pixels, pixels, lloc['cent1'])
        cent2i = np.interp(os_pixels, pixels, lloc['cent2'])
        # --------------------------------------------------------------------
        # get the correlations between cent2i and cent1i
        cori = np.correlate(cent2i, cent1i, mode='same')
        # --------------------------------------------------------------------
        # get the tilt - the maximum correlation between the middle pixel
        #   and the middle pixel + 50 * p['COI']
        coi = int(p['COI'])
        pos = int(data2.shape[1] * coi / 2)
        delta = np.argmax(cori[pos:pos + 50 * coi]) / coi
        # get the angle of the tilt
        angle = np.rad2deg(-1 * np.arctan(delta / (2 * lloc['offset'])))
        # log the tilt and angle
        wmsg = 'Order {0}: Tilt = {1:.2f} on pixel {2:.1f} = {3:.2f} deg'
        wargs = [order_num / 2, delta, 2 * lloc['offset'], angle]
        WLOG('', p['log_opt'], wmsg.format(*wargs))
        # save tilt angle to lloc
        lloc['tilt'][int(order_num / 2)] = angle
    # return the lloc
    return lloc


def extract_AB_order(pp, lloc, order_num):
    """
    Perform the extraction on the AB fibers separately using the summation
    over constant range

    :param pp: dictionary, parameter dictionary
    :param lloc: dictionary, parameter dictionary containing the data
    :param order_num: int, the order number for this iteration
    :return lloc: dictionary, parameter dictionary containing the data
    """
    # get the width fit coefficients for this fit
    assi = lloc['ass'][order_num]
    # --------------------------------------------------------------------
    # Center the central pixel (using the width fit)
    # get the width of the central pixel of this order
    width_cent = np.polyval(assi[::-1], pp['IC_CENT_COL'])
    # work out the offset in width for the center pixel
    lloc['offset'] = width_cent * p['IC_FACDEC']
    lloc.set_source('offset', __NAME__ + '/extract_AB_order()')
    # --------------------------------------------------------------------
    # deal with fiber A:

    # Get the center coeffs for this order
    acci = np.array(lloc['acc'][order_num])
    # move the intercept of the center fit by -offset
    acci[0] -= lloc['offset']
    # extract the data
    lloc['cent1'], cpt = spirouEXTOR.Extraction(p, data2, acci, assi)
    lloc.set_source('cent1', __NAME__ + '/extract_AB_order()')
    lloc['nbcos'][order_num] = cpt
    # --------------------------------------------------------------------
    # deal with fiber B:

    # Get the center coeffs for this order
    acci = np.array(lloc['acc'][order_num])
    # move the intercept of the center fit by -offset
    acci[0] += lloc['offset']
    # extract the data
    lloc['cent2'], cpt = spirouEXTOR.Extraction(p, data2, acci, assi)
    lloc.set_source('cent2', __NAME__ + '/extract_AB_order()')
    lloc['nbcos'][order_num] = cpt

    # return loc dictionary
    return lloc


def fit_tilt(pp, lloc):
    """
    Fit the tilt (lloc['tilt'] with a polynomial of size = p['ic_tilt_filt']
    return the coefficients, fit and residual rms in lloc dictionary

    :param pp: dictionary, parameter dictionary
    :param lloc: dictionary, parameter dictionary containing the data
    :return lloc: dictionary, parameter dictionary containing the data
    """

    # get the x values for
    xfit = np.arange(lloc['number_orders']/2)
    # get fit coefficients for the tilt polynomial fit
    atc = np.polyfit(xfit, lloc['tilt'], p['IC_TILT_FIT'])[::-1]
    # get the yfit values for the fit
    yfit = np.polyval(atc[::-1], xfit)
    # get the rms for the residuls of the fit and the data
    rms = np.std(lloc['tilt'] - yfit)
    # store the fit data in lloc
    lloc['xfit_tilt'] = xfit
    lloc.set_source('xfit_tilt', __NAME__ + '/fit_tilt()')
    lloc['yfit_tilt'] = yfit
    lloc.set_source('yfit_tilt', __NAME__ + '/fit_tilt()')
    lloc['a_tilt'] = atc
    lloc.set_source('a_tilt', __NAME__ + '/fit_tilt()')
    lloc['rms_tilt'] = rms
    lloc.set_source('rms_tilt', __NAME__ + '/fit_tilt()')

    # return lloc
    return lloc



# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    p = spirouCore.RunInitialStartup()
    # run specific start up
    p = spirouCore.RunStartup(p, kind='slit', prefixes='fp_fp',
                              calibdb=True)
    # set the fiber type
    p['fib_typ'] = ['AB']
    p.set_source('fib_typ', __NAME__ + '/__main__')
    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImage(p, framemath='add')
    # get ccd sig det value
    p['ccdsigdet'] = float(spirouImage.GetKey(p, hdr, 'RDNOISE',
                                              hdr['@@@hname']))
    p.set_source('ccdsigdet', __NAME__ + '/__main__')
    # get exposure time
    p['exptime'] = float(spirouImage.GetKey(p, hdr, 'EXPTIME', hdr['@@@hname']))
    p.set_source('exptime', __NAME__ + '/__main__')
    # get gain
    p['gain'] = float(spirouImage.GetKey(p, hdr, 'GAIN', hdr['@@@hname']))
    p.set_source('gain', __NAME__ + '/__main__')

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToE(spirouImage.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], ('Image format changed to '
                            '{0}x{1}').format(*data2.shape))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 <= 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['log_opt'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get coefficients
    # ----------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p['fiber'] = p['fib_typ'][0]
    p.set_source('fiber', __NAME__ + '/__main__')
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr)

    # ----------------------------------------------------------------------
    # Calculating the tilt
    # ----------------------------------------------------------------------
    # get the tilt by extracting the AB fibers and correlating them
    loc = get_tilt(p, loc, data2)
    # fit the tilt with a polynomial
    loc = fit_tilt(p, loc)
    # log the tilt dispersion
    wmsg = 'Tilt dispersion = {0:.3f} deg'
    WLOG('info', p['log_opt'] + p['fiber'], wmsg.format(loc['rms_tilt']))

    # ----------------------------------------------------------------------
    # Plotting
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # plots setup: start interactive plot
        sPlt.start_interactive_session()
        # plot image with selected order shown
        sPlt.selected_order_plot(p, loc, data2)
        # plot slit tilt angle and fit
        sPlt.slit_tilt_angle_and_fit_plot(p, loc)
        # end interactive section
        sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Replace tilt by the global fit
    # ----------------------------------------------------------------------
    loc['tilt'] = loc['yfit_tilt']
    oldsource = loc.get_source('tilt')
    loc.set_source('tilt',oldsource + '+{0}/__main__'.format(__NAME__))

    # ----------------------------------------------------------------------
    # Save and record of tilt table
    # ----------------------------------------------------------------------
    # copy the tilt along the orders
    tiltima = np.ones((int(loc['number_orders']/2), data2.shape[1]))
    tiltima *= loc['tilt'][:, None]
    # construct file name and path
    tiltfits = p['arg_file_names'][0].replace('.fits', '_tilt.fits')
    reduced_dir = os.path.join(p['DRS_DATA_REDUC'], p['arg_night_name'])
    # Log that we are saving tilt file
    wmsg = 'Saving tilt  information in file: {0}'
    WLOG('', p['log_opt'], wmsg.format(tiltfits))
    # Copy keys from fits file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # add version number
    hdict = spirouImage.AddKey(hdict, p['kw_Version'])
    # add the tilt parameters
    for order_num in range(0, int(loc['number_orders']/2)):
        # modify name and comment for keyword
        tilt_keywordstore = list(p['kw_TILT'])
        tilt_keywordstore[0] += str(order_num)
        tilt_keywordstore[2] += str(order_num)
        # add keyword to hdict
        hdict = spirouImage.AddKey(hdict, tilt_keywordstore,
                                   value=loc['tilt'][order_num])
    # write tilt file to file
    spirouImage.WriteImage(os.path.join(reduced_dir, tiltfits), tiltima, hdict)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # to be done
    p['QC'] = 1

    # ----------------------------------------------------------------------
    # Update the calibration data base
    # ----------------------------------------------------------------------
    if p['QC']:
        keydb = 'TILT'
        # copy localisation file to the calibDB folder
        spirouCDB.PutFile(p, os.path.join(reduced_dir, tiltfits))
        # update the master calib DB file with new key
        spirouCDB.UpdateMaster(p, keydb, tiltfits, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                '').format(p['program']))

    neilend = time.time()
    print('Time taken (py3) = {0}'.format(neilend - neilstart))

# =============================================================================
# End of code
# =============================================================================

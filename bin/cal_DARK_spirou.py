#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DARK_spirou.py [night_directory] [fitsfilename]

Prepares the dark files for SPIRou

Created on 2017-10-11 at 10:45

@author: cook

Version 0.0.1

Last modified: 2017-10-11 at 10:49
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
import sys
import warnings

import startup
import general_functions as gf

# =============================================================================
# Define variables
# =============================================================================
WLOG = startup.log.logger
# -----------------------------------------------------------------------------
INTERACTIVE_PLOTS = True


# =============================================================================
# Define functions
# =============================================================================
def measure_dark(pp, image, image_name, short_name):
    """
    Measure the dark pixels in "image"

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :param image_name: string, the name of the image (for logging)
    :param short_name: string, suffix (for parameter naming -
                        parmaeters added to pp with suffix i)
    :return pp: dictionary, parameter dictionary
    """

    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = np.median(fimage)
    # get the 5th and 95h percentile qmin
    qmin, qmax = np.percentile(fimage, [pp['DARK_QMIN'], pp['DARK_QMAX']])
    # get the histogram for flattened data
    histo = np.histogram(fimage, bins=p['HISTO_BINS'],
                         range=(pp['HISTO_RANGE_LOW'], pp['HISTO_RANGE_HIGH']))
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    largs = ['In {0}'.format(image_name), dadead, med, pp['DARK_QMIN'],
               pp['DARK_QMAX'], qmin, qmax]
    WLOG('info', pp['log_opt'], ('{0:12s}: Frac dead pixels= {1:.1f} % - '
                                 'Median= {2:.2f} ADU/s - '
                                 'Percent[{3}:{4}]= {5:.2f}-{6:.2f} ADU/s'
                                 '').format(*largs))
    # add required variables to pp
    pp['histo_{0}'.format(short_name)] = histo
    pp['med_{0}'.format(short_name)] = med
    pp['dadead_{0}'.format(short_name)] = dadead

    return pp


def plot_image_and_regions(pp, image):
    """
    Plot the image and the red and plot regions

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image

    :return:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot the image
    im = frame.imshow(image, origin='lower', clim=(1., 10 * pp['med_full']),
                      cmap='jet')
    # plot the colorbar
    plt.colorbar(im, ax=frame)
    # get the blue region
    bxlow, bxhigh = pp['IC_CCDX_BLUE_LOW'], pp['IC_CCDX_BLUE_HIGH']
    bylow, byhigh = pp['IC_CCDY_BLUE_LOW'], pp['IC_CCDY_BLUE_HIGH']
    # adjust for backwards limits
    if bxlow > bxhigh:
        bxlow, bxhigh = bxhigh-1, bxlow-1
    if bylow > byhigh:
        bylow, byhigh = byhigh-1, bylow-1
    # plot blue rectangle
    brec = Rectangle((bxlow, bylow), bxhigh-bxlow, byhigh-bylow,
                     edgecolor='b', facecolor='None')
    frame.add_patch(brec)
    # get the red region
    rxlow, rxhigh = pp['IC_CCDX_RED_LOW'], pp['IC_CCDX_RED_HIGH']
    rylow, ryhigh = pp['IC_CCDY_RED_LOW'], pp['IC_CCDY_RED_HIGH']
    # adjust for backwards limits
    if rxlow > rxhigh:
        rxlow, rxhigh = rxhigh-1, rxlow-1
    if rylow > ryhigh:
        rylow, ryhigh = ryhigh-1, rylow-1
    # plot blue rectangle
    rrec = Rectangle((rxlow, rylow), rxhigh-rxlow, ryhigh-rylow,
                     edgecolor='r', facecolor='None')
    frame.add_patch(rrec)


def plot_datacut(imagecut):
    """
    Plot the data cut mask

    :param imagecut: numpy array (2D), the data cut mask

    :return:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot the image cut
    im = frame.imshow(imagecut, origin='lower', cmap='gray')
    # plot the colorbar
    plt.colorbar(im, ax=frame)
    # make sure image is bounded by shape
    plt.axis([0, imagecut.shape[0], 0, imagecut.shape[1]])


def plot_histograms(pp):
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # get variables from property dictionary
    histo_f, edge_f = pp['histo_full']
    histo_b, edge_b = pp['histo_blue']
    histo_r, edge_r = pp['histo_red']
    # plot the main histogram
    xf = np.repeat(edge_f, 2)
    yf = [0] + list(np.repeat(histo_f*100/np.max(histo_f), 2)) + [0]
    frame.plot(xf, yf, color='green')
    # plot the blue histogram
    xb = np.repeat(edge_b, 2)
    yb = [0] + list(np.repeat(histo_b*100/np.max(histo_b), 2)) + [0]
    frame.plot(xb, yb, color='blue')
    # plot the red histogram
    xr = np.repeat(edge_r, 2)
    yr = [0] + list(np.repeat(histo_r*100/np.max(histo_r), 2)) + [0]
    frame.plot(xr, yr, color='red')


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    p = startup.RunInitialStartup()
    # run specific start up
    p = startup.RunStartup(p, kind='dark', prefixes=['dark_dark'])

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = gf.ReadImage(p, framemath='average')
    # get ccd sig det value
    p['ccdsigdet'] = float(gf.GetKey(p, hdr, 'RDNOISE', hdr['@@@hname']))
    # get exposure time
    p['exptime'] = float(gf.GetKey(p, hdr, 'EXPTIME', hdr['@@@hname']))
    # get gain
    p['gain'] = float(gf.GetKey(p, hdr, 'GAIN', hdr['@@@hname']))
    # log the Dark exposure time
    WLOG('info', p['log_opt'], 'Dark Time = {0:.3f} [s]'.format(p['exptime']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if p['exptime'] < p['QC_DARK_TIME']:
        WLOG('error', p['log_opt'], 'Dark exposure time too short')
        sys.exit(1)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # # rotate the image and conver from ADU/s to e-
    # data = data[::-1, ::-1] * p['exptime'] * p['gain']
    # convert NaN to zeros
    nanmask = ~np.isfinite(data)
    data0 = np.where(nanmask, 0.0, data)
    # resize blue image
    bkwargs = dict(xlow=p['IC_CCDX_BLUE_LOW'], xhigh=p['IC_CCDX_BLUE_HIGH'],
                   ylow=p['IC_CCDY_BLUE_LOW'], yhigh=p['IC_CCDY_BLUE_HIGH'])
    datablue, nx2, ny2 = gf.ResizeImage(data, **bkwargs)
    # Make sure we have data in the blue image
    if nx2 == 0 or ny2 == 0:
        WLOG('error', p['log_opt'], ('IC_CCD(X/Y)_BLUE_(LOW/HIGH) remove '
                                     'all pixels from image.'))
        sys.exit(1)
    # resize red image
    rkwargs = dict(xlow=p['IC_CCDX_RED_LOW'], xhigh=p['IC_CCDX_RED_HIGH'],
                   ylow=p['IC_CCDY_RED_LOW'], yhigh=p['IC_CCDY_RED_HIGH'])
    datared, nx3, ny3 = gf.ResizeImage(data, **rkwargs)
    # Make sure we have data in the red image
    if nx3 == 0 or ny3 == 0:
        WLOG('error', p['log_opt'], ('IC_CCD(X/Y)_RED_(LOW/HIGH) remove '
                                     'all pixels from image.'))
        sys.exit(1)

    # ----------------------------------------------------------------------
    # Dark Measurement
    # ----------------------------------------------------------------------
    # Log that we are doing dark measurement
    WLOG('', p['log_opt'], 'Doing Dark measurement')
    # measure dark for whole frame
    p = measure_dark(p, data, 'Whole det', 'full')
    # measure dark for blue part
    p = measure_dark(p, datablue, 'Blue part', 'blue')
    # measure dark for rede part
    p = measure_dark(p, datared, 'Red part', 'red')

    # ----------------------------------------------------------------------
    # Identification of bad pixels
    # ----------------------------------------------------------------------
    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as w:
        datacutmask = ~((data > p['DARK_CUTLIMIT']) | (~np.isfinite(data)))
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.product(data.shape) - np.sum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    p['dadeadall'] = n_bad_pix * 100 / np.product(data.shape)
    # log fraction of dead pixels + dark > cut
    logargs = [p['DARK_CUTLIMIT'], p['dadeadall']]
    WLOG('info', p['log_opt'], ('Total Frac dead pixels (N.A.N) + DARK > '
                                '{0:.1f} ADU/s = {1:.1f} %').format(*logargs))

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive plot
        if INTERACTIVE_PLOTS:
            plt.ion()
        # plot the image with blue and red regions
        plot_image_and_regions(p, data)
        # plot the data cut
        plot_datacut(datacutmask)
        # plot histograms
        plot_histograms(p)
        # turn off interactive plotting
        if not INTERACTIVE_PLOTS:
            plt.show()
            plt.close()

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # check that med < qc_max_darklevel
    if p['med_full'] > p['QC_MAX_DARKLEVEL']:
        # add failed message to fail message list
        fmsg = 'Unexpected Dark level  ({0:5.2f} > {1:5.2f} ADU/s)'
        fail_msg.append(fmsg.format(p['med_full'], p['QC_MAX_DARKLEVEL']))
        passed = False
    # check that fraction of dead pixels < qc_max_dead
    if p['dadeadall'] > p['QC_MAX_DEAD']:
        # add failed message to fail message list
        fmsg = 'Unexpected Fraction of dead pixels ({0:5.2f} > {1:5.2f} %)'
        fail_msg.append(fmsg.format(p['dadeadall'], p['QC_MAX_DEAD']))
        passed = False
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['log_opt'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
    else:
        fargs = [', '.join(fail_msg)]
        WLOG('info', p['log_opt'], 'QUALITY CONTROL FAILED: {0}'.format(*fargs))
        p['QC'] = 0

    # ----------------------------------------------------------------------
    # Save dark to file
    # ----------------------------------------------------------------------

    # construst folder and filename
    reducedfolder = os.path.join(p['DRS_DATA_REDUC'], p['arg_night_name'])
    darkfits = p['arg_file_names'][0]
    # log saving dark frame
    WLOG('', p['log_opt'], 'Saving Dark frame in ' + darkfits)
    # add keys from original header file
    hdict = gf.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict['DADEAD'] = (p['dadead_full'], 'Fraction dead pixels [%]')
    hdict['DAMED'] = (p['med_full'], 'median dark level [ADU/s]')
    hdict['DABDEAD'] = (p['dadead_blue'], 'Fraction dead pixels blue part [%]')
    hdict['DABMED'] = (p['med_blue'], 'median dark level blue part [ADU/s]')
    hdict['DARDEAD'] = (p['dadead_red'], 'Fraction dead pixels red part [%]')
    hdict['DARMED'] = (p['med_red'], 'median dark level red part [ADU/s]')
    hdict['DACUT'] = (p['DARK_CUTLIMIT'],
                      'Threshold of dark level retain [ADU/s]')
    # write to file
    gf.WriteImage(os.path.join(reducedfolder, darkfits), data0, hdict)

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # construct bad pixel file name
    badpixelfits = p['arg_file_names'][0].replace('.fits', '_badpixel.fits')
    # log that we are saving bad pixel map in dir
    WLOG('', p['log_opt'], 'Saving Bad Pixel Map in ' + badpixelfits)
    # add keys from original header file
    hdict = gf.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict['DACUT'] = (p['DARK_CUTLIMIT'],
                      'Threshold of dark level retain [ADU/s]')
    # write to file
    datacutmask = np.array(datacutmask, dtype=int)
    gf.WriteImage(os.path.join(reducedfolder, badpixelfits), datacutmask, hdict)

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        keydb = 'DARK'
        # copy dark fits file to the calibDB folder
        startup.PutFile(p, os.path.join(reducedfolder, darkfits))
        # update the master calib DB file with new key
        startup.UpdateMaster(p, 'DARK', darkfits, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                '').format(p['program']))

# =============================================================================
# End of code
# =============================================================================

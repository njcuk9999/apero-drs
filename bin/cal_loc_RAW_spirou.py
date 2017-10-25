#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_loc_RAW_spirou.py

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
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
# These must exist in a config file
FIBER_PARAMS = 'nbfib', 'ic_first_order_jump', 'ic_locnbmaxo', 'qc_loc_nbo'

# =============================================================================
# Define functions
# =============================================================================
def fiber_params(p, fiber):
    """
    Takes the parameters defined in FIBER_PARAMS from parameter dictionary
    (i.e. from config files) and adds the correct parameter to a fiber
    parameter dictionary

    :param p: dictionary, parameter dictionary
    :param fiber: string, the fiber type (and suffix used in confiruation file)
                  i.e. for fiber AB fiber="AB" and nbfib_AB should be present
                  in config if "nbfib" is in FIBER_PARAMS
    :return fparam: dictionary, the fiber parameter dictionary
    """
    # set up the fiber parameter directory
    fparam = dict()
    # loop around keys in FIBER_PARAMS
    for key in FIBER_PARAMS:
        # construct the parameter key (must ex
        configkey = '{0}_{1}'.format(key, fiber).upper()
        # check that key (in _fiber form) is in parameter dictionary
        if configkey not in p:
            WLOG('error', p['log_opt'], ('Config Error: Key {0} does not exist '
                                         'in parameter dictionary'
                                         '').format(configkey))

        fparam[key] = p[configkey]
    # add fiber to the parameters
    fparam['fiber'] = fiber
    # return fiber dictionary
    return fparam


def measure_background(p, image):
    """
    Takes the image and measure the background

    :param p: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :return:
    """
    # clip the data - start with the ic_offset row and only
    # deal with the central column column=ic_cent_col
    y = image[p['IC_OFFSET']:, p['IC_CENT_COL']]
    # Get the box-smoothed min and max for the central column
    miny, maxy = gf.BoxSmoothedMinMax(y, p['IC_LOCNBPIX'])
    # record the maximum signal in the central column
    # QUESTION: Why the third biggest?
    max_signal = np.sort(y)[-3]
    # get the difference between max and min pixel values
    diff_maxmin = maxy - miny
    # normalised the central pixel values above the minimum amplitude
    #   zero by miny and normalise by (maxy - miny)
    #   Set all values below ic_min_amplitude to zero
    max_amp = p['IC_MIN_AMPLITUDE']
    ycc = np.where(diff_maxmin > max_amp, (y - miny)/diff_maxmin, 0)
    # get the normalised minimum values for those rows above threshold
    #   i.e. good background measurements
    normed_miny = miny/diff_maxmin
    goodback = np.compress(ycc > p['IC_LOCSEUIL'], normed_miny)
    # measure the mean good background as a percentage
    # (goodback and ycc are between 0 and 1)
    mean_backgrd = np.mean(goodback) * 100
    # Log the maximum signal and the mean background
    WLOG('info', p['log_opt'], ('Maximum flux/pixel in the spectrum: '
                                '{0:.1f} [e-]').format(max_signal))
    WLOG('info', p['log_opt'], ('Average background level: '
                                '{0:.2f} [%]').format(mean_backgrd))
    # if in debug mode plot y, miny and maxy else just plot y
    if p['IC_DEBUG'] and p['DRS_PLOT']:
        plot_y_miny_maxy(y, miny, maxy)
    if p['DRS_PLOT']:
        plot_y_miny_maxy(y)
    # return the normalised central pixel values
    return ycc


def plot_y_miny_maxy(y, miny=None, maxy=None):
    """
    Plots the row number against central column pixel value, smoothed minimum
    central pixel value and smoothed maximum, central pixel value

    :param y: numpy array, central column pixel value
    :param miny: numpy array, smoothed minimum central pixel value
    :param maxy: numpy array, smoothed maximum central pixel value
    :return:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # define row number
    rownumber = np.arange(len(y))
    # plot y against row number
    frame.plot(rownumber, y, linestyle='-')
    # plot miny against row number
    if miny is not None:
        frame.plot(rownumber, miny, marker='_')
    # plot maxy against row number
    if maxy is not None:
        frame.plot(rownumber, maxy, marker='_')
    # set title
    frame.set(title='Central CUT', xlabel='pixels', ylabel='ADU')


def plot_min_ycc_loc_threshold(p, ycc):
    """
    Plots the minimum value between the value in ycc and ic_loc_seuil (the
    normalised amplitude threshold to accept pixels for background calculation)

    :param p: dictionary, parameter dictionary
    :param ycc: numpy array, normalised central column pixel values
    :return:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # define row number
    rownumber = np.arange(len(ycc))
    # plot minimum
    frame.plot(rownumber, np.minimum(ycc, p['IC_LOC_SEUIL']))
    # set title
    frame.set(title='Central CUT', xlabel='pixels', ylabel='ADU')


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
    params2add = dict()
    params2add['dark_flat'] = fiber_params(p, 'C')
    params2add['flat_dark'] = fiber_params(p, 'AB')
    p = startup.RunStartup(p, kind='localisation',
                           prefixes=['dark_flat', 'flat_dark'],
                           add_to_p=params2add, calibdb=True)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = gf.ReadImage(p, framemath='add')
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
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = gf.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = gf.ConvertToE(gf.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), 0.0, data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'])
    data2, nx2, ny2 = gf.ResizeImage(data0, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], 'Image format changed to {0}x{1}'.format(nx2, ny2))

    # ----------------------------------------------------------------------
    # Construct image order_profile
    # ----------------------------------------------------------------------
    order_profile = gf.BoxSmoothedImage(data2, p['LOC_BOX_SIZE'])
    # data 2 is now set to the order profile
    data2 = order_profile.copy()

    # ----------------------------------------------------------------------
    # Write image order_profile to file
    # ----------------------------------------------------------------------
    # Construct folder and filename
    reducedfolder = os.path.join(p['DRS_DATA_REDUC'], p['arg_night_name'])
    newext = '_order_profile_{0}.fits'.format(p['fiber'])
    rawfits = p['arg_file_names'][0].replace('.fits', newext)
    # log saving order profile
    WLOG('', p['log_opt'], 'Saving processed raw frame in {0}'.format(rawfits))
    # add keys from original header file
    hdict = gf.CopyOriginalKeys(hdr, cdr)
    # write to file
    gf.WriteImage(os.path.join(reducedfolder, rawfits), order_profile, hdict)

    # ----------------------------------------------------------------------
    # Move order_profile to calibDB and update calibDB
    # ----------------------------------------------------------------------
    # set key for calibDB
    keydb = 'ORDER_PROFILE_{0}'.format(p['fiber'])
    # copy dark fits file to the calibDB folder
    startup.PutFile(p, os.path.join(reducedfolder, rawfits))
    # update the master calib DB file with new key
    startup.UpdateMaster(p, keydb, rawfits, hdr)

    # ######################################################################
    # Localization of orders on central column
    # ######################################################################

    # Plots setup: start interactive plot
    if p['DRS_PLOT'] and INTERACTIVE_PLOTS:
        plt.ion()
    # ----------------------------------------------------------------------
    # Measurement and correction of background on the central column
    # ----------------------------------------------------------------------
    ycc = measure_background(p, data2)
    # ----------------------------------------------------------------------
    # Search for order center on the central column - quick estimation
    # ----------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Searching order center on central column')
    # plot the minimum of ycc and ic_locseuil if in debug and plot mode
    if p['IC_DEBUG'] and p['DRS_PLOT']:
        plot_min_ycc_loc_threshold(p, ycc)

    # TODO: Stopped here and tested

    # ----------------------------------------------------------------------
    # Search for order center and profile on every column
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Plot order number against rms_center and against rms_FWHM
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # other plots here

        # turn off interactive plotting
        if not INTERACTIVE_PLOTS:
            plt.show()
            plt.close()

    # ----------------------------------------------------------------------
    # Save and record of image of localization
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Save and record of image of sigma
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Update the calibration database
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                 '').format(p['program']))

# =============================================================================
# End of code
# =============================================================================

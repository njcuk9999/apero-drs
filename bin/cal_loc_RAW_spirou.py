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
import os
import sys
import time

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
def fiber_params(pp, fiber):
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
    # set up the fiber parameter directory
    fparam = dict()
    # loop around keys in FIBER_PARAMS
    for key in FIBER_PARAMS:
        # construct the parameter key (must ex
        configkey = ('{0}_{1}'.format(key, fiber)).upper()
        # check that key (in _fiber form) is in parameter dictionary
        if configkey not in pp:
            WLOG('error', pp['log_opt'], ('Config Error: Key {0} does not '
                                          'exist in parameter dictionary'
                                          '').format(configkey))

        fparam[key.upper()] = pp[configkey]
    # add fiber to the parameters
    fparam['fiber'] = fiber
    # return fiber dictionary
    return fparam


def measure_background_and_get_central_pixels(pp, image):
    """
    Takes the image and measure the background

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image

    :return ycc: the normalised values the central pixels
    """
    # clip the data - start with the ic_offset row and only
    # deal with the central column column=ic_cent_col
    y = image[pp['IC_OFFSET']:, pp['IC_CENT_COL']]
    # Get the box-smoothed min and max for the central column
    miny, maxy = gf.BoxSmoothedMinMax(y, pp['IC_LOCNBPIX'])
    # record the maximum signal in the central column
    # QUESTION: Why the third biggest?
    max_signal = np.sort(y)[-3]
    # get the difference between max and min pixel values
    diff_maxmin = maxy - miny
    # normalised the central pixel values above the minimum amplitude
    #   zero by miny and normalise by (maxy - miny)
    #   Set all values below ic_min_amplitude to zero
    max_amp = pp['IC_MIN_AMPLITUDE']
    ycc = np.where(diff_maxmin > max_amp, (y - miny)/diff_maxmin, 0)
    # get the normalised minimum values for those rows above threshold
    #   i.e. good background measurements
    normed_miny = miny/diff_maxmin
    goodback = np.compress(ycc > pp['IC_LOCSEUIL'], normed_miny)
    # measure the mean good background as a percentage
    # (goodback and ycc are between 0 and 1)
    mean_backgrd = np.mean(goodback) * 100
    # Log the maximum signal and the mean background
    WLOG('info', pp['log_opt'], ('Maximum flux/pixel in the spectrum: '
                                 '{0:.1f} [e-]').format(max_signal))
    WLOG('info', pp['log_opt'], ('Average background level: '
                                 '{0:.2f} [%]').format(mean_backgrd))
    # if in debug mode plot y, miny and maxy else just plot y
    if pp['IC_DEBUG'] and pp['DRS_PLOT']:
        plot_y_miny_maxy(y, miny, maxy)
    if pp['DRS_PLOT']:
        plot_y_miny_maxy(y)
    # return the normalised central pixel values
    return ycc


def find_order_centers(pp, image, loc, order_num):
    """
    Find the center pixels at specific points along this order="order_num"

    specific points are defined by steps (ic_locstepc) away from the
    central pixel (ic_cent_col)

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :param cpos_orders: numpy array (2D)
                        size = (number of orders x image.data[1])
                        storage array for the central positions along all the
                        orders
    :param cwid_orders: numpy array (2D)
                        size = (number of orders x image.data[1])
                        storage array for the order widths along all the
                        orders
    :param order_num: int, the current order to process

    :return cpos_orders: numpy array (2D)
                         size = (number of orders x image.data[1])
                         storage array for the central positions along all the
                         orders
    :return cwid_orders: numpy array (2D)
                         size = (number of orders x image.data[1])
                         storage array for the order widths along all the
                         orders
    """

    # get constants from parameter dictionary
    locstep, centralcol = pp['IC_LOCSTEPC'], pp['IC_CENT_COL']
    ext_window, image_gap = pp['IC_EXT_WINDOW'], pp['IC_IMAGE_GAP']
    sigdet, locthreshold = pp['ccdsigdet'], pp['IC_LOCSEUIL']
    widthmin = pp['IC_WIDTHMIN']
    # get columns (start from the center and work outwards right side first
    # the left side) the order of these seems weird but we calculate row centers
    # from the central col (posc) to the RIGHT edge then calculate the center
    # pixel again from the "central col+locstep" pixel (first column calculated)
    # then we calculate row centers to the LEFT edge
    #   - hence the order of columns
    columns = list(range(centralcol + locstep, nx2 - locstep, locstep))
    columns += list(range(centralcol, locstep, -locstep))
    # loop around each column to get the order row center position from
    # previous central measurement.
    # For the first iteration this uses "posc" for all other iterations
    # uses the central position found at the nearest column to it
    # must also correct for conversion to int by adding 0.5
    center, width = np.nan, np.nan
    for col in columns:
        # for pixels>central pixel we need to get row center from last
        # iteration (or posc) this is to the LEFT
        if col > centralcol:
            rowcenter = int(loc['ctro'][order_num, col - locstep] + 0.5)
        # for pixels<=central pixel we need to get row center from last
        # iteration this ir to the RIGHT
        else:
            rowcenter = int(loc['ctro'][order_num, col + locstep] + 0.5)
        # need to define the extraction window edges
        rowtop, rowbottom = rowcenter - ext_window, rowcenter + ext_window
        # now make sure our extraction isn't out of bounds
        if rowtop <= 0 or rowbottom >= nx2:
            break
        # make sure we are not in the image_gap
        # Question: Not sure what this is for
        if rowtop < image_gap and rowbottom > image_gap:
            break
        # get the pixel values between row bottom and row top for
        # this column
        cvalues = image[rowtop:rowbottom, col]
        # only use if max - min above threshold = 100 * sigdet
        if np.max(cvalues) - np.min(cvalues) > (100.0 * sigdet):
            # as we are not normalised threshold needs multiplying by
            # the maximum value
            threshold = np.max(cvalues) * locthreshold
            # find the row center position and the width of the order
            # for this column
            lkwargs = dict(cvalues=cvalues, threshold=threshold,
                           min_width=widthmin)
            centers, widths = gf.LocCentralOrderPos(**lkwargs)
            # There should only be one order found so just need the first
            # also need to add on row top (as centers are relative positions)
            center, width = centers[0] + rowtop, widths[0]
            # if the width is zero set the position back to the original
            # position
            if width == 0:
                center = float(rowcenter)
        # add these positions to storage
        loc['ctro'][order_num, col] = center
        loc['sigo'][order_num, col] = width
        # debug plot
        if pp['IC_DEBUG'] == 2 and pp['DRS_PLOT']:
            dvars = [pp, order_num, col, rowcenter, rowtop, rowbottom,
                     center, width, cvalues]
            debug_plot_finding_orders(*dvars)
    # return the storage dictionary
    return loc


def fit_order(pp, loc, x, mask, onum, rnum, fig=None, frame=None):

    # get constants
    pos_fit_order = pp['IC_LOCDFITC']
    wid_fit_order = pp['IC_LOCDFITW']
    centralcol = pp['IC_CENT_COL']
    # get values for position and width from loc
    pos_y = loc['ctro'][onum, :][mask]
    wid_y = loc['sigo'][onum, :][mask]
    # Do initial fit on position (revere due to fortran compatibility)
    loc['ac'][rnum] = np.polyfit(x, pos_y, deg=pos_fit_order)[::-1]
    # Do initial fit on width
    loc['ass'][rnum] = np.polyfit(x, wid_y, deg=wid_fit_order)[::-1]
    # Get the intial fit data
    pos_fit = np.polyval(loc['ac'][rnum][::-1], x)
    wid_fit = np.polyval(loc['ass'][rnum][::-1], x)
    # work out diff
    pos_diff = pos_y - pos_fit
    wid_diff = wid_y - wid_fit
    # Work out residuals
    pos_res = abs(pos_diff)
    wid_res = abs(wid_diff)
    # work out rms at center
    loc['rms_center'][rnum] = np.std(pos_diff)
    loc['rms_fwhm'][rnum] = np.std(wid_diff)
    # work out max point to point of residuals
    loc['max_ptp_center'][rnum] = np.max(pos_res)
    loc['max_ptp_fwhm'][rnum] = np.max(wid_res)
    loc['max_ptp_fracfwhm'][rnum] = np.max(wid_res/wid_y)
    # Log order number and fit at central pixel and width and rms
    wargs = [centralcol, pos_fit[centralcol], wid_fit[centralcol],
             loc['rms_center'][rnum]]
    WLOG('', pp['log_opt'], ('Order: {0} center at pixel {1:.1f} width '
                             '{2:.1f} rms {3:.3f}').format(*wargs))

    # plot order
    if pp['DRS_PLOT'] and fig is not None and frame is not None:
        plot_order(fig, frame, x, pos_y)

    return loc


def plot_order(fig, frame, x, y):
    frame.plot(x, y)


def plot_y_miny_maxy(y, miny=None, maxy=None):
    """
    Plots the row number against central column pixel value, smoothed minimum
    central pixel value and smoothed maximum, central pixel value

    :param y: numpy array, central column pixel value
    :param miny: numpy array, smoothed minimum central pixel value
    :param maxy: numpy array, smoothed maximum central pixel value
    :return None:
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
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()


def debug_plot_min_ycc_loc_threshold(pp, cvalues):
    """
    Plots the minimum value between the value in ycc and ic_loc_seuil (the
    normalised amplitude threshold to accept pixels for background calculation)

    :param pp: dictionary, parameter dictionary
    :param cvalues: numpy array, normalised central column pixel values
    :return None:
    """
    # set up figure
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # define row number
    rownumber = np.arange(len(cvalues))
    # plot minimum
    frame.plot(rownumber, np.minimum(cvalues, pp['IC_LOC_SEUIL']))
    # set title
    frame.set(title='Central CUT', xlabel='pixels', ylabel='ADU')
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)


def plot_image_with_saturation_threshold(image, threshold):
    """
    Plots the image (order_profile) below the saturation threshold

    :param image: numpy array (2D), the image
    :param threshold: float, the saturation threshold
    :return None:
    """
    # set up fig
    fig = plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.imshow(image, origin='lower', clim=(1.0, threshold), cmap='pink')
    # set the limits
    frame.set(xlim=(0, image.shape[0]), ylim=(0, image.shape[1]))
    # return fig and frame
    return fig, frame


def debug_plot_finding_orders(pp, no, ncol, ind0, ind1, ind2, cgx, wx, ycc):

    # log output for this row
    wargs = [no, ncol, ind0, cgx, wx]
    WLOG('', pp['log_opt'], '{0:d} {0:d}  {0:f}  {0:f}  {0:f}'.format(*wargs))

    xx = np.array([ind1, cgx - wx / 2., cgx - wx / 2., cgx - wx / 2., cgx,
                   cgx + wx / 2., cgx + wx / 2., cgx + wx / 2., ind2])
    yy = np.array([0., 0., max(ycc) / 2., max(ycc), max(ycc), max(ycc),
                   max(ycc) / 2., 0., 0.])
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot orders
    frame.plot(np.arange(ind1, ind2, 1.0), ycc)
    frame.plot(xx, yy)
    frame.set(xlim=(ind1, ind2), ylim=(0, np.max(ycc)))
    # turn off interactive plotting
    if not plt.isinteractive():
        plt.show()
        plt.close()
    else:
        time.sleep(pp['IC_DISPLAY_TIMEOUT'] * 3)


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
    ycc = measure_background_and_get_central_pixels(p, data2)
    # ----------------------------------------------------------------------
    # Search for order center on the central column - quick estimation
    # ----------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Searching order center on central column')
    # plot the minimum of ycc and ic_locseuil if in debug and plot mode
    if p['IC_DEBUG'] and p['DRS_PLOT']:
        debug_plot_min_ycc_loc_threshold(p, ycc)
    # find the central positions of the orders in the central
    posc_all, _ = gf.LocCentralOrderPos(ycc, p['IC_LOCSEUIL'])
    # depending on the fiber type we may need to skip some pixels and also
    # we need to add back on the ic_offset applied
    start = p['IC_FIRST_ORDER_JUMP']
    posc = posc_all[start:] + p['IC_OFFSET']
    # work out the number of orders to use (minimum of ic_locnbmaxo and number
    #    of orders found in 'LocateCentralOrderPositions')
    number_of_orders = np.min([p['IC_LOCNBMAXO'], len(posc)])
    # log the number of orders than have been detected
    wargs = [p['fiber'], int(number_of_orders/p['NBFIB']), p['NBFIB']]
    WLOG('info', p['log_opt'], ('On fiber {0} {1} orders have been detected '
                                'on {2} fiber(s)').format(*wargs))

    # ----------------------------------------------------------------------
    # Search for order center and profile on every column
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # get saturation threshold
        satseuil = p['IC_SATSEUIL'] * p['gain'] * p['nbframes']
        # plot image above saturation threshold
        fig1, frame1 = plot_image_with_saturation_threshold(data2, satseuil)
    else:
        fig1, frame1 = None, None
    # ----------------------------------------------------------------------
    # Save and record of image of localization
    # ----------------------------------------------------------------------
    # get fit polynomial orders for position and width
    fitpos, fitwid = p['IC_LOCDFITC'], p['IC_LOCDFITW']
    # storage dictionary for localization parameters
    loc = dict()
    # Create arrays to store position and width of order for each order
    loc['ctro'] = np.zeros((number_of_orders, data2.shape[1]), dtype=float)
    loc['sigo'] = np.zeros((number_of_orders, data2.shape[1]), dtype=float)
    # Create arrays to store coefficients for position and width
    loc['ac'] = np.zeros((number_of_orders, fitpos))
    loc['ass'] = np.zeros((number_of_orders, fitpos))
    # Create arrays to store rms values for position and width
    loc['rms_center'] = np.zeros(number_of_orders)
    loc['rms_fwhm'] = np.zeros(number_of_orders)
    # Create arrays to store point to point max value for position and width
    loc['max_ptp_center'] = np.zeros(number_of_orders)
    loc['max_ptp_fwhm'] = np.zeros(number_of_orders)
    loc['max_ptp_fracfwhm'] = np.zeros(number_of_orders)

    # ----------------------------------------------------------------------
    # set the central col centers in the cpos_orders array
    loc['ctro'][:, p['IC_CENT_COL']] = posc[0:number_of_orders]
    # ----------------------------------------------------------------------
    # loop around each order
    rorder_num = 0
    for order_num in range(number_of_orders):
        # find the row centers of the columns
        loc = find_order_centers(p, data2, loc, order_num)
        # only keep the orders with non-zero width
        mask = loc['sigo'][order_num, :] != 0
        pixels = np.arange(data2.shape[1])[mask]
        # check that we have enough data points to fit data
        if len(pixels) > (fitpos + 1):
            loc = fit_order(p, loc, pixels, mask, order_num, rorder_num,
                            fig1, frame1)
            rorder_num += 1
        # else log that the order is unusable
        else:
            WLOG('', p['log_opt'], 'Order found too much incomplete, discarded')


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

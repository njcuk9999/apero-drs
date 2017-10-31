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

from SpirouDRS import spirouCDB
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR


# =============================================================================
# Define variables
# =============================================================================
WLOG = spirouCore.wlog
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


def measure_background_and_get_central_pixels(pp, loc, image):
    """
    Takes the image and measure the background

    :param pp: dictionary, parameter dictionary
    :param loc: dictionary, localisation parameter dictionary
    :param image: numpy array (2D), the image

    :return ycc: the normalised values the central pixels
    """
    # clip the data - start with the ic_offset row and only
    # deal with the central column column=ic_cent_col
    y = image[pp['IC_OFFSET']:, pp['IC_CENT_COL']]
    # Get the box-smoothed min and max for the central column
    miny, maxy = spirouLOCOR.BoxSmoothedMinMax(y, pp['IC_LOCNBPIX'])
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

    # Add to loc
    loc['ycc'] = ycc
    loc['mean_backgrd'] = mean_backgrd
    loc['max_signal'] = max_signal
    # return the localisation dictionary
    return loc


def find_order_centers(pp, image, loc, order_num):
    """
    Find the center pixels at specific points along this order="order_num"

    specific points are defined by steps (ic_locstepc) away from the
    central pixel (ic_cent_col)

    :param pp: dictionary, parameter dictionary
    :param image: numpy array (2D), the image
    :param loc: dictionary, localisation parameter dictionary
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
    nx2 = image.shape[1]
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
    center, width = 0, 0
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
        rowtop, rowbottom = (rowcenter - ext_window), (rowcenter + ext_window)
        # now make sure our extraction isn't out of bounds
        if rowtop <= 0 or rowbottom >= nx2:
            break
        # make sure we are not in the image_gap
        # Question: Not sure what this is for
        if rowtop < image_gap and rowbottom > image_gap:
            break
        # get the pixel values between row bottom and row top for
        # this column
        ovalues = image[rowtop:rowbottom, col]
        # only use if max - min above threshold = 100 * sigdet
        if np.max(ovalues) - np.min(ovalues) > (100.0 * sigdet):
            # as we are not normalised threshold needs multiplying by
            # the maximum value
            threshold = np.max(ovalues) * locthreshold
            # find the row center position and the width of the order
            # for this column
            lkwargs = dict(values=ovalues, threshold=threshold,
                           min_width=widthmin)
            center, width = spirouLOCOR.LocCentralOrderPos(**lkwargs)
            # need to add on row top (as centers are relative positions)
            center = center + rowtop
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
                     center, width, ovalues]
            debug_plot_finding_orders(*dvars)
    # return the storage dictionary
    return loc


def initial_order_fit(pp, loc, mask, onum, rnum, kind, fig=None, frame=None):
    # deal with kind
    if kind not in ['center', 'fwhm']:
        WLOG('error', pp['log_opt'], ('Error: sigma_clip "kind" must be '
                                      'either "center" or "fwhm"'))
    # get variables that are independent of kind
    x = loc['x']
    # get variables dependent on kind
    if kind == 'center':
        # constants
        f_order = pp['IC_LOCDFITC']
        # variables
        y = loc['ctro'][onum, :][mask]
    else:
        # constants
        f_order = pp['IC_LOCDFITW']
        # variables
        y = loc['sigo'][onum, :][mask]
    # -------------------------------------------------------------------------
    # calculate fit - coefficients, fit y params, residuals, absolute residuals,
    #                 rms and max_ptp
    # -------------------------------------------------------------------------
    acoeffs, fit, res, abs_res, rms, max_ptp = calculate_fit(x, y, f_order)
    # max_ptp_frac is different for different cases
    if kind == 'center':
        max_ptp_frac = max_ptp / rms
    else:
        max_ptp_frac = np.max(abs_res/y) * 100
    # -------------------------------------------------------------------------
    # plot order on image plot (if drs_plot is true)
    if pp['DRS_PLOT'] and kind == 'center':
        if fig is not None and frame is not None:
            plot_order(fig, frame, x, y)
    # -------------------------------------------------------------------------
    # Work out the fit value at ic_cent_col (for logging)
    cfitval = np.polyval(acoeffs[::-1], p['IC_CENT_COL'])
    # -------------------------------------------------------------------------
    # return fit data
    fitdata = dict(a=acoeffs, fit=fit, res=res, abs_res=abs_res, rms=rms,
                   max_ptp=max_ptp, max_ptp_frac=max_ptp_frac, cfitval=cfitval)
    return fitdata


def sigmaclip_order_fit(pp, loc, fitdata, mask, onum, rnum, kind):
    # deal with kind
    if kind not in ['center', 'fwhm']:
        WLOG('error', pp['log_opt'], ('Error: sigma_clip "kind" must be '
                                      'either "center" or "fwhm"'))
    # extract constants from fitdata
    acoeffs = fitdata['a']
    fit = fitdata['fit']
    res = fitdata['res']
    abs_res = fitdata['abs_res']
    rms = fitdata['rms']
    max_ptp = fitdata['max_ptp']
    max_ptp_frac = fitdata['max_ptp_frac']
    # get variables that are independent of kind
    x = loc['x']
    ic_max_rms = pp['IC_MAX_RMS_{0}'.format(kind.upper())]
    # get variables dependent on kind
    if kind == 'center':
        # constants
        f_order = pp['IC_LOCDFITC']
        ic_max_ptp = pp['IC_MAX_PTP_{0}'.format(kind.upper())]
        ic_max_ptp_frac = None
        ic_ptporms_center = pp['IC_PTPORMS_CENTER']
        # variables
        y = loc['ctro'][onum, :][mask]
        max_rmpts = loc['max_rmpts_pos'][rnum]
        kind2, ptpfrackind = 'center', 'sigrms'
    else:
        # constants
        f_order = pp['IC_LOCDFITW']
        ic_max_ptp = -np.inf
        ic_max_ptp_frac = pp['IC_MAX_PTP_FRAC{0}'.format(kind.upper())]
        ic_ptporms_center = None
        # variables
        y = loc['sigo'][onum, :][mask]
        max_rmpts = loc['max_rmpts_wid'][rnum]
        kind2, ptpfrackind = 'width ', 'ptp%'
    # -------------------------------------------------------------------------
    # Need to do sigma clip fit
    # -------------------------------------------------------------------------
    # define clipping mask
    wmask = np.ones(len(abs_res), dtype=bool)
    # get condition for doing sigma clip
    cond = rms > ic_max_rms
    if kind == 'center':
        cond |= max_ptp > ic_max_ptp
        cond |= (max_ptp_frac > ic_ptporms_center)
    else:
        cond |= (max_ptp_frac > ic_max_ptp_frac)
    # keep clipping until cond is met
    xo, yo = np.array(x), np.array(y)
    while cond:
        # Log that we are clipping the fit
        wargs = [kind, ptpfrackind, rms, max_ptp, max_ptp_frac]
        WLOG('', pp['log_opt'], ('      {0} fit converging with rms/ptp/{1}:'
                                 ' {2:.3f}/{3:.3f}/{4:.3f}').format(*wargs))
        # debug plot
        if pp['DRS_PLOT'] and pp['IC_DEBUG']:
            debug_plot_fit_residual(pp, loc, rnum, kind)
        # add one to the max rmpts
        max_rmpts += 1
        # remove the largest residual (set wmask = 0 at that position)
        wmask[np.argmax(abs_res)] = False
        # get the new x and y values (without largest residual)
        xo, yo = xo[wmask], yo[wmask]
        # fit the new x and y
        acoeffs, fit, res, abs_res, rms, max_ptp = calculate_fit(xo, yo, f_order)
        # max_ptp_frac is different for different cases
        if kind == 'center':
            max_ptp_frac = max_ptp / rms
        else:
            max_ptp_frac = np.max(abs_res / yo) * 100
        # recalculate condition for doing sigma clip
        cond = rms > ic_max_rms
        if kind == 'center':
            cond |= (max_ptp > ic_max_ptp)
            cond |= (max_ptp_frac > ic_ptporms_center)
        else:
            cond |= (max_ptp_frac > ic_max_ptp_frac)
        # reform wmask
        wmask = wmask[wmask]
    else:
        wargs = [kind2, ptpfrackind, rms, max_ptp, max_ptp_frac, int(max_rmpts)]
        WLOG('', pp['log_opt'], (' - {0} fit rms/ptp/{1}: {2:.3f}/{3:.3f}/'
                                 '{4:.3f} with {5} rejected points'
                                 '').format(*wargs))
    # if max_rmpts > 50:
    #     stats = ('\n\tacoeffs={0}, \n\tfit={1}, \n\tres={2}, '
    #              '\t\tabs_res={3}, \n\trms={4}, \n\tmax_pt={5}'
    #              ''.format(acoeffs, fit, res, abs_res, rms, max_ptp))
    #     print('{0} fit did not converge stats: {1}'.format(kind, stats))
    #     sys.exit()
    # return fit data
    fitdata = dict(a=acoeffs, fit=fit, res=res, abs_res=abs_res, rms=rms,
                   max_ptp=max_ptp, max_ptp_frac=max_ptp_frac,
                   max_rmpts=max_rmpts)
    return fitdata


def calculate_fit(x, y, f):
    # Do initial fit (revere due to fortran compatibility)
    a = np.polyfit(x, y, deg=f)[::-1]
    # Get the intial fit data
    fit = np.polyval(a[::-1], x)
    # work out residuals
    res = y - fit
    # Work out absolute residuals
    abs_res = abs(res)
    # work out rms
    rms = np.std(res)
    # work out max point to point of residuals
    max_ptp = np.max(abs_res)
    # return all
    return a, fit, res, abs_res, rms, max_ptp


# =============================================================================
# Define plot functions
# =============================================================================
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


def plot_order_number_against_rms(pp, loc, rnum):
    """

    :param pp:
    :param loc:
    :param rnum:
    :return:
    """
    # set up fig
    fig = plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot image
    frame.plot(np.arange(rnum), loc['rms_center'][0:rnum], label='fwhm')
    frame.plot(np.arange(rnum), loc['rms_fwhm'][0:rnum], label='fwhm')
    # set title labels limits
    frame.set(xlim=(0, rnum), ylim=(0, 0.1),
              xlabel='Order number', ylabel='RMS [pixel]',
              title=('Dispersion of localization parameters fiber {0}'
                     '').format(pp['fiber']))
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


def debug_plot_finding_orders(pp, no, ncol, ind0, ind1, ind2, cgx, wx, ycc):
    """

    :param pp:
    :param no:
    :param ncol:
    :param ind0:
    :param ind1:
    :param ind2:
    :param cgx:
    :param wx:
    :param ycc:
    :return:
    """
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


def debug_plot_fit_residual(pp, loc, rnum, kind):
    """

    :param pp:
    :param loc:
    :param rnum:
    :param kind:
    :return:
    """
    # get variables from loc dictionary
    x = loc['x']
    xo = loc['ctro'][rnum]
    if kind == 'center':
        y = loc['pos_diff']
    else:
        y = loc['wid_diff']
    # new fig
    plt.figure()
    # clear the current figure
    plt.clf()
    # set up axis
    frame = plt.subplot(111)
    # plot residuals of data - fit
    frame.plot(x, y, marker='_')
    # set title and limits
    frame.set(title='{0} fit residual of order {1}'.format(kind, rnum),
              xlim=(0, len(xo)), ylim=(np.min(y), np.max(y)))
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
    p = spirouCore.RunInitialStartup()
    # run specific start up
    params2add = dict()
    params2add['dark_flat'] = fiber_params(p, 'C')
    params2add['flat_dark'] = fiber_params(p, 'AB')
    p = spirouCore.RunStartup(p, kind='localisation',
                              prefixes=['dark_flat', 'flat_dark'],
                              add_to_p=params2add, calibdb=True)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImage(p, framemath='add')
    # get ccd sig det value
    p['ccdsigdet'] = float(spirouImage.GetKey(p, hdr, 'RDNOISE',
                                              hdr['@@@hname']))
    # get exposure time
    p['exptime'] = float(spirouImage.GetKey(p, hdr, 'EXPTIME', hdr['@@@hname']))
    # get gain
    p['gain'] = float(spirouImage.GetKey(p, hdr, 'GAIN', hdr['@@@hname']))
    # log the Dark exposure time
    WLOG('info', p['log_opt'], 'Dark Time = {0:.3f} [s]'.format(p['exptime']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if p['exptime'] < p['QC_DARK_TIME']:
        WLOG('error', p['log_opt'], 'Dark exposure time too short')
        sys.exit(1)

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
    data0 = np.where(~np.isfinite(data), 0.0, data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], ('Image format changed to '
                            '{0}x{1}').format(*data2.shape))

    # ----------------------------------------------------------------------
    # Construct image order_profile
    # ----------------------------------------------------------------------
    order_profile = spirouLOCOR.BoxSmoothedImage(data2, p['LOC_BOX_SIZE'],
                                                 mode='manual')
    # data 2 is now set to the order profile
    data2o = data2.copy()
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
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # write to file
    rawpath = os.path.join(reducedfolder, rawfits)
    spirouImage.WriteImage(rawpath, order_profile, hdict)

    # ----------------------------------------------------------------------
    # Move order_profile to calibDB and update calibDB
    # ----------------------------------------------------------------------
    # set key for calibDB
    keydb = 'ORDER_PROFILE_{0}'.format(p['fiber'])
    # copy dark fits file to the calibDB folder
    spirouCDB.PutFile(p, os.path.join(reducedfolder, rawfits))
    # update the master calib DB file with new key
    spirouCDB.UpdateMaster(p, keydb, rawfits, hdr)

    # ######################################################################
    # Localization of orders on central column
    # ######################################################################
    # storage dictionary for localization parameters
    loc = dict()
    # Plots setup: start interactive plot
    if p['DRS_PLOT'] and INTERACTIVE_PLOTS:
        plt.ion()
    # ----------------------------------------------------------------------
    # Measurement and correction of background on the central column
    # ----------------------------------------------------------------------
    loc = measure_background_and_get_central_pixels(p, loc, data2)
    # ----------------------------------------------------------------------
    # Search for order center on the central column - quick estimation
    # ----------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Searching order center on central column')
    # plot the minimum of ycc and ic_locseuil if in debug and plot mode
    if p['IC_DEBUG'] and p['DRS_PLOT']:
        debug_plot_min_ycc_loc_threshold(p, loc['ycc'])
    # find the central positions of the orders in the central
    posc_all = spirouLOCOR.FindPosCentCol(loc['ycc'], p['IC_LOCSEUIL'])
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
    # Search for order center and profile on specific columns
    # ----------------------------------------------------------------------
    # Plot the image (ready for fit points to be overplotted later)
    if p['DRS_PLOT']:
        # get saturation threshold
        satseuil = p['IC_SATSEUIL'] * p['gain'] * p['nbframes']
        # plot image above saturation threshold
        fig1, frame1 = plot_image_with_saturation_threshold(data2, satseuil)
    else:
        fig1, frame1 = None, None
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # get fit polynomial orders for position and width
    fitpos, fitwid = p['IC_LOCDFITC'], p['IC_LOCDFITW']
    # Create arrays to store position and width of order for each order
    loc['ctro'] = np.zeros((number_of_orders, data2.shape[1]), dtype=float)
    loc['sigo'] = np.zeros((number_of_orders, data2.shape[1]), dtype=float)
    # Create arrays to store coefficients for position and width
    loc['ac'] = np.zeros((number_of_orders, fitpos + 1))
    loc['ass'] = np.zeros((number_of_orders, fitpos + 1))
    # Create arrays to store rms values for position and width
    loc['rms_center'] = np.zeros(number_of_orders)
    loc['rms_fwhm'] = np.zeros(number_of_orders)
    # Create arrays to store point to point max value for position and width
    loc['max_ptp_center'] = np.zeros(number_of_orders)
    loc['max_ptp_fraccenter'] = np.zeros(number_of_orders)
    loc['max_ptp_fwhm'] = np.zeros(number_of_orders)
    loc['max_ptp_fracfwhm'] = np.zeros(number_of_orders)
    # Create arrays to store rejected points
    loc['max_rmpts_pos'] = np.zeros(number_of_orders)
    loc['max_rmpts_wid'] = np.zeros(number_of_orders)
    # set the central col centers in the cpos_orders array
    loc['ctro'][:, p['IC_CENT_COL']] = posc[0:number_of_orders]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # loop around each order
    rorder_num = 0
    for order_num in range(number_of_orders):
        # find the row centers of the columns
        loc = find_order_centers(p, data2, loc, order_num)
        # only keep the orders with non-zero width
        mask = loc['sigo'][order_num, :] != 0
        loc['x'] = np.arange(data2.shape[1])[mask]
        # check that we have enough data points to fit data
        if len(loc['x']) > (fitpos + 1):
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # initial fit for center positions for this order
            cf_data = initial_order_fit(p, loc, mask, order_num, rorder_num,
                                        kind='center', fig=fig1, frame=frame1)
            # initial fit for widths for this order
            wf_data = initial_order_fit(p, loc, mask, order_num, rorder_num,
                                        kind='fwhm', fig=fig1, frame=frame1)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Log order number and fit at central pixel and width and rms
            wargs = [rorder_num, cf_data['cfitval'], wf_data['cfitval'],
                     cf_data['rms']]
            WLOG('', p['log_opt'], ('ORDER: {0} center at pixel {1:.1f} width '
                                    '{2:.1f} rms {3:.3f}').format(*wargs))
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # sigma clip fit for center positions for this order
            cf_data = sigmaclip_order_fit(p, loc, cf_data, mask, order_num,
                                          rorder_num,  kind='center')
            # load results into storage arrags for this order
            loc['ac'][rorder_num] = cf_data['a']
            loc['rms_center'][rorder_num] = cf_data['rms']
            loc['max_ptp_center'][rorder_num] = cf_data['max_ptp']
            loc['max_ptp_fraccenter'][rorder_num] = cf_data['max_ptp_frac']
            loc['max_rmpts_pos'][rorder_num] = cf_data['max_rmpts']
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # sigma clip fit for width positions for this order
            wf_data = sigmaclip_order_fit(p, loc, wf_data, mask, order_num,
                                          rorder_num, kind='fwhm')
            # load results into storage arrags for this order
            loc['ass'][rorder_num] = wf_data['a']
            loc['rms_fwhm'][rorder_num] = wf_data['rms']
            loc['max_ptp_fwhm'][rorder_num] = wf_data['max_ptp']
            loc['max_ptp_fracfwhm'][rorder_num] = wf_data['max_ptp_frac']
            loc['max_rmpts_wid'][rorder_num] = wf_data['max_rmpts']
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # increase the roder_num iterator
            rorder_num += 1
        # else log that the order is unusable
        else:
            WLOG('', p['log_opt'], 'Order found too much incomplete, discarded')

    # Log that order geometry has been measured
    WLOG('info', p['log_opt'], ('On fiber {0} {1} orders geometry have been '
                                'measured').format(p['fiber'], rorder_num))
    # Get mean rms
    mean_rms_center = np.sum(loc['rms_center'][:rorder_num]) * 1000/rorder_num
    mean_rms_fwhm = np.sum(loc['rms_fwhm'][:rorder_num]) * 1000/rorder_num
    # Log mean rms values
    wmsg = 'Average uncertainty on {0}: {1:.2f} [mpix]'
    WLOG('info', p['log_opt'], wmsg.format('position', mean_rms_center))
    WLOG('info', p['log_opt'], wmsg.format('width', mean_rms_fwhm))

    # ----------------------------------------------------------------------
    # Plot of RMS for positions and widths
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        plot_order_number_against_rms(p, loc, rorder_num)

    # ----------------------------------------------------------------------
    # Save and record of image of localization with order center and keywords
    # ----------------------------------------------------------------------

    # construct filename
    locoext =  '_loco_{0}.fits'.format(p['fiber'])
    locofits = p['arg_file_names'][0].replace('.fits', locoext)

    # log that we are saving localization file
    WLOG('', p['log_opt'], ('Saving localization information '
                            'in file: {0}').format(locofits))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict = spirouImage.AddNewKey(hdict, p['kw_version'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_CCD_SIGDET'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_CCD_CONAD'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_BCKGRD'],
                                  value=loc['mean_backgrd'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_NBO'],
                                  value=rorder_num)
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_DEG_C'],
                                  value=p['IC_LOCDFITC'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_DEG_W'],
                                  value=p['IC_LOCDFITW'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_DEG_E'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_DELTA'])
    # write 2D list of position fit coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['kw_LOCO_CTR_COEFF'],
                                     values=loc['ac'][0:rorder_num])
    # write 2D list of width fit coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['kw_LOCO_FWHM_COEFF'],
                                     values=loc['ass'][0:rorder_num])
    # write image and add header keys (via hdict)
    spirouImage.WriteImage(os.path.join(reducedfolder, locofits),
                           loc['ac'][0:rorder_num], hdict)

    # ----------------------------------------------------------------------
    # Save and record of image of sigma
    # ----------------------------------------------------------------------
    # construct filename
    locoext =  '_fwhm-order_{0}.fits'.format(p['fiber'])
    locofits2 = p['arg_file_names'][0].replace('.fits', locoext)

    # log that we are saving localization file
    WLOG('', p['log_opt'], ('Saving FWHM information '
                            'in file: {0}').format(locofits))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict = spirouImage.AddNewKey(hdict, p['kw_version'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_CCD_SIGDET'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_CCD_CONAD'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_BCKGRD'],
                                  value=loc['mean_backgrd'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_NBO'],
                                  value=rorder_num)
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_DEG_C'],
                                  value=p['IC_LOCDFITC'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_DEG_W'],
                                  value=p['IC_LOCDFITW'])
    hdict = spirouImage.AddNewKey(hdict, p['kw_LOCO_DEG_E'])
    # write 2D list of position fit coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['kw_LOCO_CTR_COEFF'],
                                     values=loc['ac'][0:rorder_num])
    # write 2D list of width fit coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['kw_LOCO_FWHM_COEFF'],
                                     values=loc['ass'][0:rorder_num])
    # write image and add header keys (via hdict)
    spirouImage.WriteImage(os.path.join(reducedfolder, locofits),
                           loc['ass'][0:rorder_num], hdict)

    # ----------------------------------------------------------------------
    # Save and Record of image of localization
    # ----------------------------------------------------------------------
    if p['IC_LOCOPT1']:
        # construct filename
        locoext = '_with-order_{0}.fits'.format(p['fiber'])
        locofits3 = p['arg_file_names'][0].replace('.fits', locoext)
        locopath = os.path.join(reducedfolder, locofits3)
        # log that we are saving localization file
        WLOG('', p['log_opt'], ('Saving localization image with superposition '
                                'of orders in file: {0}').format(locofits))

        # TODO: Start from here!
        sys.exit()
        spirouLOCOR.imaloco2(data2o, loc['ac'][0:rorder_num], locopath)
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

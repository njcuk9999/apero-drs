#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-15 at 13:48

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core import math
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.core.core import drs_database
from terrapipe.io import drs_fits


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.localisation.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def calculate_order_profile(params, image, **kwargs):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param image: numpy array (2D), the image
    :param kwargs: keyword arguments

    :keyword size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge

    :return newimage: numpy array (2D), the smoothed image
    """
    func_name = __NAME__ + '.calculate_order_profile()'
    # get constants from params
    size = pcheck(params, 'LOC_ORDERP_BOX_SIZE', 'size', kwargs, func_name)
    # -------------------------------------------------------------------------
    # log that we are creating order profile
    WLOG(params, '', TextEntry('40-013-00001'))
    # -------------------------------------------------------------------------
    # copy the original image
    newimage = np.zeros_like(image)
    # loop around each pixel column
    for it in range(0, image.shape[1], 1):
        # ------------------------------------------------------------------
        # deal with leading edge --> i.e. box expands until it is full size
        if it < size:
            # get the subimage defined by the box for all rows
            part = image[:, 0:it + size + 1]
        # deal with main part (where box is of size="size"
        elif size <= it <= image.shape[1]-size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size: it + size + 1]
        # deal with the trailing edge --> i.e. box shrinks from full size
        elif it > image.shape[1]-size:
            # get the subimage defined by the box for all rows
            part = image[:, it - size:]
        # else we have zeros (shouldn't happen)
        else:
            part = np.zeros_like(image)
        # ------------------------------------------------------------------
        # apply the weighted mean for this column
        with warnings.catch_warnings(record=True) as _:
            newimage[:, it] = np.nanmedian(part, axis=1)
    # return the new smoothed image
    return newimage


def find_and_fit_localisation(params, image, sigdet, **kwargs):
    func_name = __NAME__ + '.find_and_fit_localisation()'

    # ----------------------------------------------------------------------
    # get constants from p
    # ----------------------------------------------------------------------
    row_offset = pcheck(params, 'LOC_START_ROW_OFFSET', 'row_offset', kwargs,
                        func=func_name)
    central_col = pcheck(params, 'LOC_CENTRAL_COLUMN', 'central_col', kwargs,
                         func=func_name)
    horder_size = pcheck(params, 'LOC_HALF_ORDER_SPACING', 'horder_size',
                         kwargs, func=func_name)
    minpeak_amp = pcheck(params, 'LOC_MINPEAK_AMPLITUDE', 'minpeak_amp',
                         kwargs, func=func_name)
    back_thres = pcheck(params, 'LOC_BKGRD_THRESHOLD', 'back_thres', kwargs,
                        func=func_name)
    first_order = pcheck(params, 'FIBER_FIRST_ORDER_JUMP', 'first_order',
                         kwargs, func=func_name)
    max_num_orders = pcheck(params, 'FIBER_MAX_NUM_ORDERS', 'max_num_orders',
                            kwargs, func=func_name)
    num_fibers = pcheck(params, 'FIBER_SET_NUM_FIBERS', 'num_fibers', kwargs,
                        func=func_name)
    wid_poly_deg = pcheck(params, 'LOC_WIDTH_POLY_DEG', 'wid_poly_deg', kwargs,
                          func=func_name)
    cent_poly_deg = pcheck(params, 'LOC_CENT_POLY_DEG', 'cent_poly_deg',
                           kwargs, func=func_name)
    locstep = pcheck(params, 'LOC_COLUMN_SEP_FITTING', 'locstep', kwargs,
                     func=func_name)
    ext_window = pcheck(params, 'LOC_EXT_WINDOW_SIZE', 'ext_window', kwargs,
                        func=func_name)
    image_gap = pcheck(params, 'LOC_IMAGE_GAP', 'image_gap', kwargs,
                       func=func_name)
    widthmin = pcheck(params, 'LOC_ORDER_WIDTH_MIN', 'widthmin', kwargs,
                      func=func_name)
    nm_thres = pcheck(params, 'LOC_NOISE_MULTIPLIER_THRES', 'nm_thres', kwargs,
                      func=func_name)
    max_rms_cent = pcheck(params, 'LOC_MAX_RMS_CENT', 'max_rms_cent', kwargs,
                          func=func_name)
    max_ptp_cent = pcheck(params, 'LOC_MAX_PTP_CENT', 'max_ptp_cent', kwargs,
                          func=func_name)
    ptporms_cent = pcheck(params, 'LOC_PTPORMS_CENT', 'ptporms_cent', kwargs,
                          func=func_name)
    max_rms_wid = pcheck(params, 'LOC_MAX_RMS_WID', 'max_rms_wid', kwargs,
                         func=func_name)
    max_ptp_wid = pcheck(params, 'LOC_MAX_PTP_WID', 'max_ptp_wid', kwargs,
                         func=func_name)
    center_drop = pcheck(params, 'LOC_ORDER_CURVE_DROP', 'curve_drop', kwargs,
                         func=func_name)
    # ----------------------------------------------------------------------
    # Step 1: Measure and correct background on the central column
    # ----------------------------------------------------------------------
    # clip the data - start with the ic_offset row and only
    # deal with the central column column=ic_cent_col
    y = image[row_offset:, central_col]
    # measure min max of box smoothed central col
    miny, maxy = math.measure_box_min_max(y, horder_size)
    max_signal = np.nanpercentile(y, 95)
    diff_maxmin = maxy - miny

    # normalised the central pixel values above the minimum amplitude
    #   zero by miny and normalise by (maxy - miny)
    #   Set all values below ic_min_amplitude to zero
    ycc = np.where(diff_maxmin > minpeak_amp, (y - miny) / diff_maxmin, 0)

    # get the normalised minimum values for those rows above threshold
    #   i.e. good background measurements
    normed_miny = miny / diff_maxmin
    goodback = np.compress(ycc > back_thres, normed_miny)
    # measure the mean good background as a percentage
    # (goodback and ycc are between 0 and 1)
    mean_backgrd = np.mean(goodback) * 100
    # Log the maximum signal and the mean background
    WLOG(params, 'info', TextEntry('40-013-00003', args=[max_signal]))
    WLOG(params, 'info', TextEntry('40-013-00004', args=[mean_backgrd]))
    # plot y, miny and maxy
    if params['DRS_PLOT'] > 0:
        # TODO: Add locplot_y_miny_maxy(p, y, miny, maxy) here
        pass

    # ----------------------------------------------------------------------
    # Step 2: Search for order center on the central column - quick
    #         estimation
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', TextEntry('40-013-00005'))
    # plot the minimum of ycc and ic_locseuil if in debug and plot mode
    if params['DRS_DEBUG'] > 0 and params['DRS_PLOT']:
        # TODO: Add debug_locplot_min_ycc_loc_threshold(p, ycc)
        pass
    # find the central positions of the orders in the central
    posc_all = find_position_of_cent_col(ycc, back_thres)
    # depending on the fiber type we may need to skip some pixels and also
    # we need to add back on the ic_offset applied
    posc = posc_all[first_order:] + row_offset
    # work out the number of orders to use (minimum of ic_locnbmaxo and number
    #    of orders found in 'LocateCentralOrderPositions')
    num_orders = np.min([max_num_orders, len(posc)])
    norm_num_orders = int(num_orders / num_fibers)
    # log the number of orders than have been detected
    wargs = [params['FIBER'], norm_num_orders, num_fibers]
    WLOG(params, 'info', TextEntry('40-013-00006', args=wargs))

    # ----------------------------------------------------------------------
    # Step 3: Search for order center and profile on specific columns
    # ----------------------------------------------------------------------
    cent_0 = np.zeros((num_orders, image.shape[1]), dtype=float)
    wid_0 = np.zeros((num_orders, image.shape[1]), dtype=float)
    # Create arrays to store coefficients for position and width
    cent_coeffs = np.zeros((num_orders, cent_poly_deg + 1))
    wid_coeffs = np.zeros((num_orders, wid_poly_deg + 1))
    # Create arrays to store rms values for position and width
    cent_rms = np.zeros(num_orders)
    wid_rms = np.zeros(num_orders)
    # Create arrays to store point to point max value for position and width
    cent_max_ptp = np.zeros(num_orders)
    cent_frac_ptp = np.zeros(num_orders)
    wid_max_ptp = np.zeros(num_orders)
    wid_frac_ptp = np.zeros(num_orders)
    # Create arrays to store rejected points
    cent_max_rmpts = np.zeros(num_orders)
    wid_max_rmpts = np.zeros(num_orders)
    # storage for plotting
    xplot, yplot = [], []
    # ----------------------------------------------------------------------
    # set the central col centers in the cpos_orders array
    cent_0[:, central_col] = posc[0:num_orders]
    # ----------------------------------------------------------------------
    # loop around each order
    rorder_num = 0
    for order_num in range(num_orders):
        # get the shape of the image
        nx2 = image.shape[1]
        # ------------------------------------------------------------------
        # get columns (start from the center and work outwards right side
        # first the left side) the order of these seems weird but we
        # calculate row centers from the central col (posc) to the RIGHT
        # edge then calculate the center pixel again from the
        # "central col+locstep" pixel (first column calculated) then we
        # calculate row centers to the LEFT edge - hence the order of columns
        columns = list(range(central_col + locstep, nx2 - locstep, locstep))
        columns += list(range(central_col, locstep, -locstep))
        # ------------------------------------------------------------------
        # loop around each column to get the order row center position from
        # previous central measurement.
        # For the first iteration this uses "posc" for all other iterations
        # uses the central position found at the nearest column to it
        # must also correct for conversion to int by adding 0.5
        # center, width = 0, 0
        for col in columns:
            # for pixels>central pixel we need to get row center from last
            # iteration (or posc) this is to the LEFT
            if col > central_col:
                rowcenter = int(cent_0[order_num, col - locstep] + 0.5)
            # for pixels<=central pixel we need to get row center from last
            # iteration this ir to the RIGHT
            else:
                rowcenter = int(cent_0[order_num, col + locstep] + 0.5)
            # need to define the extraction window edges
            rowtop, rowbottom = (rowcenter - ext_window), (
                        rowcenter + ext_window)
            # now make sure our extraction isn't out of bounds
            if rowtop <= 0 or rowbottom >= nx2:
                break

            # TODO: This value may need changing - What does it do?
            # if col <= (800 - order_num*30):
            if col <= (750 - rowcenter * 0.7):
                break
            # make sure we are not in the image_gap
            if (rowtop < image_gap) and (rowbottom > image_gap):
                break
            # get the pixel values between row bottom and row top for
            # this column
            ovalues = image[rowtop:rowbottom, col]
            # only use if max - min above threshold = 100 * sigdet
            truethres = nm_thres * sigdet
            cond = np.nanmax(ovalues) - np.nanmin(ovalues) > truethres
            if cond:
                # as we are not normalised threshold needs multiplying by
                # the maximum value
                threshold = np.nanmax(ovalues) * back_thres
                # find the row center position and the width of the order
                # for this column
                lkwargs = dict(values=ovalues, threshold=threshold,
                               min_width=widthmin)
                center, width = locate_order_center(**lkwargs)
                # need to add on row top (as centers are relative positions)
                center = center + rowtop
                # if the width is zero set the position back to the original
                # position
                if width == 0:
                    # to force the order curvature
                    center = float(rowcenter) - center_drop
            else:
                width = 0
                # to force the order curvature
                center = float(rowcenter) - center_drop
            # add these positions to storage
            cent_0[order_num, col] = center
            wid_0[order_num, col] = width
            # debug plot
            if params['DRS_DEBUG'] == 2 and params['DRS_PLOT']:
                dvars = [params, order_num, col, rowcenter, rowtop, rowbottom,
                         center, width, ovalues]
                #TODO: Add sPlt.debug_locplot_finding_orders(*dvars)
        # ------------------------------------------------------------------
        # only keep the orders with non-zero width
        mask = wid_0[order_num, :] != 0
        # get the x pixels where we have non-zero width
        xpix = np.arange(image.shape[1])[mask]
        # check that we have enough data points to fit data
        if len(xpix) > (np.max([wid_poly_deg, cent_poly_deg]) + 1):
            # --------------------------------------------------------------
            # initial fit for center positions for this order
            cent_y = cent_0[rorder_num, :][mask]
            iofargs = [params, xpix, cent_y, cent_poly_deg, central_col]
            cf_data = initial_order_fit(*iofargs, kind='center')
            # append centers for plot
            xplot.append(xpix), yplot.append(cent_y)
            # --------------------------------------------------------------
            # initial fit for widths for this order
            wid_y = wid_0[rorder_num, :][mask]
            iofargs = [params, xpix, wid_y, wid_poly_deg, central_col]
            wf_data = initial_order_fit(*iofargs, kind='fwhm')
            # --------------------------------------------------------------
            # Log order number and fit at central pixel and width and rms
            wargs = [rorder_num, cf_data['cfitval'], wf_data['cfitval'],
                     cf_data['rms']]
            WLOG(params, '', TextEntry('40-013-00007', args=wargs))
            # --------------------------------------------------------------
            # sigma fit params for center
            sigfargs = [params, xpix, cent_y, cf_data, cent_poly_deg,
                        cent_max_rmpts[rorder_num]]
            sigfkwargs = dict(ic_max_ptp=max_ptp_cent, ic_max_ptp_frac=None,
                              ic_ptporms=ptporms_cent, ic_max_rms=max_rms_cent,
                              kind='center')
            # sigma clip fit for center positions for this order
            cf_data = sigmaclip_order_fit(*sigfargs, **sigfkwargs)
            # load results into storage arrays for this order
            cent_coeffs[rorder_num] = cf_data['a']
            cent_rms[rorder_num] = cf_data['rms']
            cent_max_ptp[rorder_num] = cf_data['max_ptp']
            cent_frac_ptp[rorder_num] = cf_data['max_ptp_frac']
            cent_max_rmpts[rorder_num] = cf_data['max_rmpts']
            # --------------------------------------------------------------
            # sigma fit params for width
            sigfargs = [params, xpix, wid_y, wf_data, wid_poly_deg,
                        wid_max_rmpts[rorder_num]]
            sigfkwargs = dict(ic_max_ptp=-np.inf, ic_max_ptp_frac=max_ptp_wid,
                              ic_ptporms=None, ic_max_rms=max_rms_wid,
                              kind='fwhm')
            # sigma clip fit for width positions for this order
            wf_data = sigmaclip_order_fit(*sigfargs, **sigfkwargs)
            # load results into storage arrays for this order
            wid_coeffs[rorder_num] = wf_data['a']
            wid_rms[rorder_num] = wf_data['rms']
            wid_max_ptp[rorder_num] = wf_data['max_ptp']
            wid_frac_ptp[rorder_num] = wf_data['max_ptp_frac']
            wid_max_rmpts[rorder_num] = wf_data['max_rmpts']
            # --------------------------------------------------------------
            # increase the roder_num iterator
            rorder_num += 1
        # else log that the order is unusable
        else:
            WLOG(params, '', TextEntry('40-013-00010'))

    # ----------------------------------------------------------------------
    # Log that the order geometry has been measured
    wargs = [params['FIBER'], rorder_num]
    WLOG(params, 'info', TextEntry('40-013-00011', args=wargs))
    # get the mean rms values
    mean_rms_cent = np.nansum(cent_rms[:rorder_num]) * 1000 / rorder_num
    mean_rms_wid = np.nansum(wid_rms[:rorder_num]) * 1000 / rorder_num
    # Log mean rms values
    WLOG(params, 'info', TextEntry('40-013-00012', args=[mean_rms_cent]))
    WLOG(params, 'info', TextEntry('40-013-00013', args=[mean_rms_wid]))
    # ----------------------------------------------------------------------
    # return
    outputs = [cent_0, cent_coeffs, cent_rms, cent_max_ptp, cent_frac_ptp,
               cent_max_rmpts, wid_0, wid_coeffs, wid_rms, wid_max_ptp,
               wid_frac_ptp, wid_max_rmpts, xplot, yplot, rorder_num,
               mean_rms_cent, mean_rms_wid, max_signal, mean_backgrd]
    return outputs


def image_superimp(image, coeffs):
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
    # copy the old image
    newimage = image.copy()
    # get the number of orders
    n_orders = len(coeffs)
    # get the pixel positions along the order
    xdata = np.arange(image.shape[1])
    # loop around each order
    fitxarray, fityarray = [], []
    for order_num in range(n_orders):
        # get the pixel positions across the order (from fit coeffs in position)
        # add 0.5 to account for later conversion to int
        fity = np.polyval(coeffs[order_num][::-1], xdata) + 0.5
        # elements must be > 0 and less than image.shape[0]
        mask = (fity > 0) & (fity < image.shape[0])
        # Add good values to storage array
        fityarray = np.append(fityarray, fity[mask])
        fitxarray = np.append(fitxarray, xdata[mask])

    # convert fitxarray and fityarra to integers
    fitxarray = np.array(fitxarray, dtype=int)
    fityarray = np.array(fityarray, dtype=int)
    # use fitxarray and fityarray as positions to set 0 in newimage
    newimage[fityarray, fitxarray] = 0
    # return newimage
    return newimage


def get_coefficients(params, recipe, header, **kwargs):
    func_name = __NAME__ + '.get_coefficients()'
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get parameters from params/kwargs
    fiber = pcheck(params, 'FIBER', 'fiber', kwargs, func_name)
    merge = kwargs.get('merge', False)
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')
    # get filename col
    filecol = cdb.file_col
    # deal with fibers that we don't have
    usefiber = pconst.FIBER_LOC_TYPES(fiber)
    # get calibration key
    key = 'LOC_{0}'.format(usefiber)
    filetype = 'LOC_LOCO_{0}'.format(usefiber)
    # get the badpix entries
    locoentries = drs_database.get_key_from_db(params, key, cdb, header,
                                                 n_ent=1)
    # get badpix filename
    locofilename = locoentries[filecol][0]
    locofilepath = os.path.join(params['DRS_CALIB_DB'], locofilename)
    # -------------------------------------------------------------------------
    # get loco file instance
    locofile = core.get_file_definition(filetype, params['INSTRUMENT'],
                                        kind='red')
    # construct new infile instance and read data/header
    locofile = locofile.newcopy(filename=locofilepath, recipe=recipe)
    locofile.read()
    # -------------------------------------------------------------------------
    # extract keys from header
    nbo = locofile.read_header_key('KW_LOC_NBO', dtype=int)
    deg_c = locofile.read_header_key('KW_LOC_DEG_C', dtype=int)
    deg_w = locofile.read_header_key('KW_LOC_DEG_W', dtype=int)
    nset = params['FIBER_SET_NUM_FIBERS_{0}'.format(fiber)]
    # extract coefficients from header
    cent_coeffs = locofile.read_header_key_2d_list('KW_LOC_CTR_COEFF',
                                                   dim1=nbo, dim2=deg_c + 1)
    wid_coeffs = locofile.read_header_key_2d_list('KW_LOC_WID_COEFF',
                                                  dim1=nbo, dim2=deg_w + 1)
    # merge or extract individual coeffs
    if merge:
        cent_coeffs, nbo = pconst.FIBER_LOC_COEFF_EXT(cent_coeffs, fiber)
        wid_coeffs, nbo = pconst.FIBER_LOC_COEFF_EXT(wid_coeffs, fiber)
        nset = 1
    # -------------------------------------------------------------------------
    # store localisation properties in parameter dictionary
    lprops = ParamDict()
    lprops['LOCOFILE'] = locofilepath
    lprops['NBO'] = int(nbo // nset)
    lprops['DEG_C'] = int(deg_c)
    lprops['DEG_W'] = int(deg_w)
    lprops['CENT_COEFFS'] = cent_coeffs
    lprops['WID_COEFFS'] = wid_coeffs
    lprops['MERGED'] = merge
    lprops['NSET'] = nset
    # set sources
    keys = ['CENT_COEFFS', 'WID_COEFFS', 'LOCOFILE', 'NBO', 'DEG_C', 'DEG_W',
            'MERGED', 'NSET']
    lprops.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # return the coefficients and properties
    return lprops




# =============================================================================
# Worker functions
# =============================================================================
def find_position_of_cent_col(values, threshold):
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
    # store the positions of the orders
    positions = []
    # get the len of cvalues
    length = len(values)
    # initialise the row number to zero
    row, order_end = 0, 0
    # move the row number to the first row below threshold
    # (avoids first order on the edge)
    while values[row] > threshold:
        row += 1
        if row == length:
            break
    # continue to move through rows
    while row < length:
        # if row is above threshold then we have found a start point
        if values[row] > threshold:
            # save the start point
            order_start = row
            # continue to move through rows to find end (end of order defined
            # as the point at which it slips below the threshold)
            while values[row] >= threshold:
                row += 1
                # if we have reached the end of cvalues stop (it is an end of
                # an order by definition
                if row == length:
                    break
            # as we have reached the end we should not add to positions
            if row == length:
                break
            else:
                # else record the end position
                order_end = row
                # determine the center of gravity of the order
                # lx is the pixels in this order
                lx = np.arange(order_start, order_end, 1)
                # ly is the cvalues values in this order (use lx to get them)
                ly = values[lx]
                # position = sum of (lx * ly) / sum of sum(ly)
                position = np.nansum(lx * ly * 1.0) / np.nansum(ly)
                # append position and width to storage
                positions.append(position)
        # if row is still below threshold then move the row number forward
        else:
            row += 1
    # finally return the positions
    return np.array(positions)


def locate_order_center(values, threshold, min_width=None):
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
    # deal with no min_width
    if min_width is None:
        min_width = 0
    # get the len of cvalues
    length = len(values)
    # initialise the row number to zero
    row, order_end = 0, 0
    position, width = 0, 0
    # move the row number to the first row below threshold
    # (avoids first order on the edge)
    while values[row] > threshold:
        row += 1
        if row == length:
            break
    # continue to move through rows
    while row < length and (order_end == 0):
        # if row is above threshold then we have found a start point
        if values[row] > threshold:
            # save the start point
            order_start = row
            # continue to move through rows to find end (end of order defined
            # as the point at which it slips below the threshold)
            while values[row] >= threshold:
                row += 1
                # if we have reached the end of cvalues stop (it is an end of
                # an order by definition
                if row == length:
                    break
            # as we have reached the end we should not add to positions
            if row == length:
                break
            elif (row - order_start) > min_width:
                # else record the end position
                order_end = row
                # determine the center of gravity of the order
                # lx is the pixels in this order
                lx = np.arange(order_start, order_end, 1)
                # ly is the cvalues values in this order (use lx to get them)
                ly = values[lx]
                # position = sum of (lx * ly) / sum of sum(ly)
                position = np.nansum(lx * ly * 1.0) / np.nansum(ly)
                # width is just the distance from start to end
                width = abs(order_end - order_start)
        # if row is still below threshold then move the row number forward
        else:
            row += 1
    # finally return the positions
    return position, width


def initial_order_fit(params, x, y, f_order, ccol, kind):
    """
    Performs a crude initial fit for this order, uses the ctro positions or
    sigo width values found in "FindOrderCtrs" or "find_order_centers" to do
    the fit

    :param mask: numpy array (1D) of booleans, True where we have non-zero
                 widths
    :param onum: int, order iteration number (running number over all
                 iterations)
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
            fit = the fity values for the fit (for x = loc['X'])
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
    func_name = __NAME__ + '.initial_order_fit()'
    # deal with kind
    if kind not in ['center', 'fwhm']:
        WLOG(params, 'error', TextEntry('00-013-00002', args=[kind, func_name]))
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
    # Work out the fit value at ic_cent_col (for logging)
    cfitval = np.polyval(acoeffs[::-1], ccol)
    # -------------------------------------------------------------------------
    # return fit data
    fitdata = dict(a=acoeffs, fit=fit, res=res, abs_res=abs_res, rms=rms,
                   max_ptp=max_ptp, max_ptp_frac=max_ptp_frac, cfitval=cfitval)
    return fitdata


def sigmaclip_order_fit(params, x, y, fitdata, f_order, max_rmpts,
                        ic_max_ptp, ic_max_ptp_frac, ic_ptporms, ic_max_rms,
                        kind):
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

    :param params:
    :param x:
    :param y:

    :param fitdata: dictionary, contains the fit data key value pairs for this
                     initial fit. keys are as follows:

            a = coefficients of the fit from key
            size = 'ic_locdfitc' [for kind='center'] or
                 = 'ic_locdftiw' [for kind='fwhm']
            fit = the fity values for the fit (for x = loc['X'])
                where fity = Sum(a[i] * x^i)
            res = the residuals from y - fity
                 where y = ctro [kind='center'] or
                         = sigo [kind='fwhm'])
            abs_res = abs(res)
            rms = the standard deviation of the residuals
            max_ptp = maximum residual value max(res)
            max_ptp_frac = max_ptp / rms  [kind='center']
                         = max(abs_res/y) * 100   [kind='fwhm']

    :param f_order:

    :param rnum: int, order number (running number of successful order
                 iterations only)
    :param kind: string, 'center' or 'fwhm', if 'center' then this fit is for
                 the central p

    :return fitdata: dictionary, contains the fit data key value pairs for this
                     initial fit. keys are as follows:

            a = coefficients of the fit from key
            size = 'ic_locdfitc' [for kind='center'] or
                 = 'ic_locdftiw' [for kind='fwhm']
            fit = the fity values for the fit (for x = loc['X'])
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
    func_name = __NAME__ + '.sigmaclip_order_fit()'
    # deal with kind
    if kind not in ['center', 'fwhm']:
        WLOG(params, 'error', TextEntry('00-013-00003', args=[kind, func_name]))
    # extract constants from fitdata
    acoeffs = fitdata['a']
    fit = fitdata['fit']
    res = fitdata['res']
    abs_res = fitdata['abs_res']
    rms = fitdata['rms']
    max_ptp = fitdata['max_ptp']
    max_ptp_frac = fitdata['max_ptp_frac']

    # get variables dependent on kind
    if kind == 'center':
        # variables
        kind2, ptpfrackind = 'center', 'sigrms'
    else:
        # variables
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
        cond |= (max_ptp_frac > ic_ptporms)
    else:
        cond |= (max_ptp_frac > ic_max_ptp_frac)
    # keep clipping until cond is met
    xo, yo = np.array(x), np.array(y)
    while cond:
        # Log that we are clipping the fit
        wargs = [kind, ptpfrackind, rms, max_ptp, max_ptp_frac]
        WLOG(params, '', TextEntry('40-013-00008', args=wargs))
        # add residuals to loc
        # debug plot
        if params['DRS_PLOT'] and params['DRS_DEBUG'] == 2:
            # TODO: Add sPlt.debug_locplot_fit_residual(pp, loc, rnum, kind)
            pass
        # add one to the max rmpts
        max_rmpts += 1
        # remove the largest residual (set wmask = 0 at that position)
        wmask[np.argmax(abs_res)] = False
        # get the new x and y values (without largest residual)
        xo, yo = xo[wmask], yo[wmask]
        # fit the new x and y
        fdata = calculate_fit(xo, yo, f_order)
        acoeffs, fit, res, abs_res, rms, max_ptp = fdata
        # max_ptp_frac is different for different cases
        if kind == 'center':
            max_ptp_frac = max_ptp / rms
        else:
            max_ptp_frac = np.max(abs_res / yo) * 100
        # recalculate condition for doing sigma clip
        cond = rms > ic_max_rms
        if kind == 'center':
            cond |= (max_ptp > ic_max_ptp)
            cond |= (max_ptp_frac > ic_ptporms)
        else:
            cond |= (max_ptp_frac > ic_max_ptp_frac)
        # reform wmask
        wmask = wmask[wmask]
    else:
        wargs = [kind2, ptpfrackind, rms, max_ptp, max_ptp_frac, int(max_rmpts)]
        WLOG(params, '', TextEntry('40-013-00009', args=wargs))

    # return fit data
    fitdata = dict(a=acoeffs, fit=fit, res=res, abs_res=abs_res, rms=rms,
                   max_ptp=max_ptp, max_ptp_frac=max_ptp_frac,
                   max_rmpts=max_rmpts)
    return fitdata


def calculate_fit(x, y, f):
    """
    Calculate the polynomial fit between x and y, for "f" fit parameters,
    also calculate the residuals, absolute residuals, RMS and max peak-to-peak
    values

    :param x: numpy array (1D), the x values to use for the fit
    :param y: numpy array (1D), the y values to fit
    :param f: int, the number of fit parameters (i.e. for quadratic fit f=2)

    :return a: numpy array (1D), the fit coefficients
                        shape = f
    :return fit: numpy array (1D), the fit values for positions in x
                        shape = len(y) and len(x)
    :return res: numpy array (1D), the residuals between y and fit
                        shape = len(y) and len(x)
    :return abs_res: numpy array (1D), the absolute values of "res"  abs(res)
                        shape = len(y) and len(x)
    :return rms: float, the RMS (root-mean square) of the residuals (std)
    :return max_ptp: float, the max peak to peak value of the absolute
                     residuals i.e. max(abs_res)
    """
    # Do initial fit (revere due to fortran compatibility)
    a = math.nanpolyfit(x, y, deg=f)[::-1]
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
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

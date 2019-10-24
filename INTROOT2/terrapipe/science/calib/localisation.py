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
from collections import OrderedDict

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core import math as mp
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.core.core import drs_database
from terrapipe.science.calib import general

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
# Get function string
display_func = drs_log.display_func
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
            newimage[:, it] = mp.nanmedian(part, axis=1)
    # return the new smoothed image
    return newimage


def check_coeffs(params, recipe, image, coeffs, fiber, kind=None):
    """
    Check and correct the coefficients by rejecting misbehaving coefficients
    and smoothing with a robust fit

    :param coeffs:
    :param nsigclip:
    :return:
    """
    # get the sigma clipping cut off value
    nsigclip = params['LOC_COEFF_SIGCLIP']
    coeffdeg = params['LOC_COEFFSIG_DEG']
    # ----------------------------------------------------------------------
    # get fiber params
    pconst = constants.pload(params['INSTRUMENT'])
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)
    max_num_orders = fiberparams['FIBER_MAX_NUM_ORDERS']
    set_num_fibers = fiberparams['FIBER_SET_NUM_FIBERS']
    num_fibers = max_num_orders / set_num_fibers
    # ----------------------------------------------------------------------
    # make sure coeffs is a numpy array
    coeffs = np.array(coeffs)
    # get the shape of coefficients
    nbo, nbcoeff = coeffs.shape
    # get the image shape
    dim1, dim2 = image.shape
    # ----------------------------------------------------------------------
    # define an x array and we'll determine the position along each order as a
    # matrix of y values. These will be sanitized and used to compute new coeffs
    xpix = np.linspace(0, dim2, nbcoeff * 10, dtype=float)
    # y matrix full of zeros
    ypix = np.zeros([nbo, len(xpix)])
    # fill in ypix
    for order_num in range(nbo):
        ypix[order_num] = np.polyval(coeffs[order_num][::-1], xpix)
    # sanity check
    ypix_ini = np.array(ypix)
    # ----------------------------------------------------------------------
    # storage of output values
    new_coeffs = np.zeros_like(coeffs)
    # we loop through fiber A and B and sanitize y position independently
    for mod in range(int(nbo // num_fibers)):
        # log progress
        WLOG(params, '', TextEntry('40-013-00026', args=[mod]))
        # index of Nth diffraction order
        index = np.arange(nbo)
        # keep either fiber A or B using modulo
        index = index[(index % (nbo // num_fibers)) == mod]
        # loop through xpix values and sanitize ypix values. y pix is fitted
        # with a sigma-clipped 6 or 7th order polynomial
        for it in range(len(xpix)):
            # only use in the fit values falling on the science array. Otherwise
            # the values are unconstrainted by flat field frames
            good = (ypix[index, it] > 0) & (ypix[index, it] < dim2)
            # robust polynomial fit
            fit, keep = mp.robust_polyfit(index[good], ypix[index, it][good],
                                          coeffdeg, nsigclip)
            # put values back in the ypix matri
            ypix[index, it] = np.polyval(fit, index)
    # ----------------------------------------------------------------------
    # storage for plotting
    good_arr = []
    # ----------------------------------------------------------------------
    # re-fit the coefficients
    for order_num in range(nbo):
        # fit the order position using the sanitized ypix values
        good = (ypix[order_num] > 0) & (ypix[order_num] < dim2)
        # use the same order of coefficient
        new_coeff_ord = np.polyfit(xpix[good], ypix[order_num, good], nbcoeff-1)
        # push into new array
        new_coeffs[order_num] = new_coeff_ord[::-1]
        # storage for plotting
        good_arr.append(good)

    # ----------------------------------------------------------------------
    # plot of the coeffs
    recipe.plot('LOC_CHECK_COEFFS', ypix=ypix, ypix0=ypix_ini,
                xpix=xpix, good=good_arr, kind=kind, image=image)
    # ----------------------------------------------------------------------
    return new_coeffs


def find_and_fit_localisation(params, recipe, image, sigdet, fiber, **kwargs):
    func_name = __NAME__ + '.find_and_fit_localisation()'

    # get fiber params
    pconst = constants.pload(params['INSTRUMENT'])
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)

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
                         kwargs, func=func_name, paramdict=fiberparams)
    max_num_orders = pcheck(params, 'FIBER_MAX_NUM_ORDERS', 'max_num_orders',
                            kwargs, func=func_name, paramdict=fiberparams)
    num_fibers = pcheck(params, 'FIBER_SET_NUM_FIBERS', 'num_fibers', kwargs,
                        func=func_name, paramdict=fiberparams)
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
    miny, maxy = mp.measure_box_min_max(y, horder_size)
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
    recipe.plot('LOC_MINMAX_CENTS', y=y, miny=miny, maxy=maxy)

    # ----------------------------------------------------------------------
    # Step 2: Search for order center on the central column - quick
    #         estimation
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', TextEntry('40-013-00005'))
    # plot the minimum of ycc and back_thres
    recipe.plot('LOC_MIN_CENTS_THRES', centers=ycc, threshold=back_thres)
    # find the central positions of the orders in the central
    posc_all = find_position_of_cent_col(ycc, back_thres)
    # depending on the fiber type we may need to skip some pixels and also
    # we need to add back on the ic_offset applied
    posc = posc_all[first_order:] + row_offset
    # work out the number of orders to use (minimum of ic_locnbmaxo and number
    #    of orders found in 'LocateCentralOrderPositions')
    num_orders = mp.nanmin([max_num_orders, len(posc)])
    norm_num_orders = int(num_orders / num_fibers)
    # log the number of orders than have been detected
    wargs = [fiber, norm_num_orders, num_fibers]
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
    # storage for plotting
    dvars = OrderedDict()
    plimits = OrderedDict()
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
        # storage for plotting
        col_vals, maxycc, minxcc, maxxcc = [], -np.inf, np.inf, -np.inf
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
            cond = mp.nanmax(ovalues) - mp.nanmin(ovalues) > truethres
            if cond:
                # as we are not normalised threshold needs multiplying by
                # the maximum value
                threshold = mp.nanmax(ovalues) * back_thres
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
            # debug plot parameters
            if np.nanmax(ovalues) > maxycc:
                maxycc = np.nanmax(ovalues)
            if (rowtop - center) < minxcc:
                minxcc = rowtop - center
            if (rowbottom - center) > maxxcc:
                maxxcc = rowbottom - center
            col_val = [rowcenter, rowtop, rowbottom, center, width, ovalues]
            col_vals.append(col_val)
        # append col vals to order storage
        dvars[order_num] = col_vals
        plimits[order_num] = [minxcc, maxxcc, 0, maxycc]
        # ------------------------------------------------------------------
        # only keep the orders with non-zero width
        mask = wid_0[order_num, :] != 0
        # get the x pixels where we have non-zero width
        xpix = np.arange(image.shape[1])[mask]
        # check that we have enough data points to fit data
        if len(xpix) > (mp.nanmax([wid_poly_deg, cent_poly_deg]) + 1):
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
    # plot finding orders plot
    recipe.plot('LOC_FINDING_ORDERS', plotdict=dvars, plimits=plimits)
    # ----------------------------------------------------------------------
    # Log that the order geometry has been measured
    wargs = [fiber, rorder_num]
    WLOG(params, 'info', TextEntry('40-013-00011', args=wargs))
    # get the mean rms values
    mean_rms_cent = mp.nansum(cent_rms[:rorder_num]) * 1000 / rorder_num
    mean_rms_wid = mp.nansum(wid_rms[:rorder_num]) * 1000 / rorder_num
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


def get_coefficients(params, recipe, header, fiber, **kwargs):
    func_name = __NAME__ + '.get_coefficients()'
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get parameters from params/kwargs
    merge = kwargs.get('merge', False)
    filename = kwargs.get('filename', None)
    # deal with fibers that we don't have
    usefiber = pconst.FIBER_LOC_TYPES(fiber)
    # ------------------------------------------------------------------------
    # check for filename in inputs
    filename = general.get_input_files(params, 'LOCOFILE', filename)
    # -------------------------------------------------------------------------
    # get loco file instance
    locofile = core.get_file_definition('LOC_LOCO', params['INSTRUMENT'],
                                        kind='red')
    # ------------------------------------------------------------------------
    # get loco filename
    if filename is not None:
        locofilepath = filename
    else:
        # get calibDB
        cdb = drs_database.get_full_database(params, 'calibration')
        # get filename col
        filecol = cdb.file_col

        # get calibration key
        key = locofile.get_dbkey(func=func_name, fiber=usefiber)
        # get the badpix entries
        locoentries = drs_database.get_key_from_db(params, key, cdb, header,
                                                   n_ent=1)
        # get badpix filename
        locofilename = locoentries[filecol][0]
        locofilepath = os.path.join(params['DRS_CALIB_DB'], locofilename)
    # ------------------------------------------------------------------------
    # construct new infile instance and read data/header
    locofile = locofile.newcopy(filename=locofilepath, recipe=recipe,
                                fiber=usefiber)
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
    props = ParamDict()
    props['LOCOFILE'] = locofilepath
    props['LOCOOBJECT'] = locofile
    props['NBO'] = int(nbo // nset)
    props['DEG_C'] = int(deg_c)
    props['DEG_W'] = int(deg_w)
    props['CENT_COEFFS'] = cent_coeffs
    props['WID_COEFFS'] = wid_coeffs
    props['MERGED'] = merge
    props['NSET'] = nset
    # set sources
    keys = ['CENT_COEFFS', 'WID_COEFFS', 'LOCOFILE', 'LOCOOBJECT', 'NBO',
            'DEG_C', 'DEG_W', 'MERGED', 'NSET']
    props.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # return the coefficients and properties
    return props


def load_orderp(params, header, fiber, filename=None):
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # deal with fibers that we don't have
    usefiber = pconst.FIBER_LOC_TYPES(fiber)
    # get file definition
    out_loc_orderp = core.get_file_definition('LOC_ORDERP',
                                               params['INSTRUMENT'], kind='red')
    # get key
    key = out_loc_orderp.get_dbkey(fiber=usefiber)
    # load calib file
    orderp, orderp_file = general.load_calib_file(params, key, header,
                                                     filename=filename)
    # log which fpmaster file we are using
    WLOG(params, '', TextEntry('40-013-00022', args=[orderp_file]))
    # return the master image
    return orderp_file, orderp

# =============================================================================
# write files and qc functions
# =============================================================================
def loc_quality_control(params, fiber, cent_max_rmpts, wid_max_rmpts,
                        mean_rms_cent, mean_rms_wid, rorder_num):

    # set function name
    func_name = display_func(params, 'localisation_quality_control', __NAME__)
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # get qc parameters
    max_removed_cent = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_CTR',
                              func=func_name)
    max_removed_wid = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_WID',
                             func=func_name)
    rmsmax_cent = pcheck(params, 'QC_LOC_RMSMAX_CTR', func=func_name)
    rmsmax_wid = pcheck(params, 'QC_LOC_RMSMAX_WID', func=func_name)
    # this one comes from pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)

    required_norders = pcheck(params, 'FIBER_MAX_NUM_ORDERS', func=func_name,
                              paramdict=fiberparams)
    # ----------------------------------------------------------------------
    # check that max number of points rejected in center fit is below
    #    threshold
    sum_cent_max_rmpts = mp.nansum(cent_max_rmpts)
    if sum_cent_max_rmpts > max_removed_cent:
        # add failed message to fail message list
        fargs = [sum_cent_max_rmpts, max_removed_cent]
        fail_msg.append(textdict['40-013-00014'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(sum_cent_max_rmpts)
    qc_names.append('sum(MAX_RMPTS_POS)')
    qc_logic.append('sum(MAX_RMPTS_POS) < {0:.2f}'
                    ''.format(sum_cent_max_rmpts))
    # ----------------------------------------------------------------------
    # check that  max number of points rejected in width fit is below
    #   threshold
    sum_wid_max_rmpts = mp.nansum(wid_max_rmpts)
    if sum_wid_max_rmpts > max_removed_wid:
        # add failed message to fail message list
        fargs = [sum_wid_max_rmpts, max_removed_wid]
        fail_msg.append(textdict['40-013-00015'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(sum_wid_max_rmpts)
    qc_names.append('sum(MAX_RMPTS_WID)')
    qc_logic.append('sum(MAX_RMPTS_WID) < {0:.2f}'
                    ''.format(sum_wid_max_rmpts))
    # ------------------------------------------------------------------
    if mean_rms_cent > rmsmax_cent:
        # add failed message to fail message list
        fargs = [mean_rms_cent, rmsmax_cent]
        fail_msg.append(textdict['40-013-00016'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mean_rms_cent)
    qc_names.append('mean_rms_center')
    qc_logic.append('mean_rms_center < {0:.2f}'.format(rmsmax_cent))
    # ------------------------------------------------------------------
    if mean_rms_wid > rmsmax_wid:
        # add failed message to fail message list
        fargs = [mean_rms_wid, rmsmax_wid]
        fail_msg.append(textdict['40-013-00017'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mean_rms_wid)
    qc_names.append('mean_rms_wid')
    qc_logic.append('mean_rms_wid < {0:.2f}'.format(rmsmax_wid))
    # ------------------------------------------------------------------
    # check for abnormal number of identified orders
    if rorder_num != required_norders:
        # add failed message to fail message list
        fargs = [rorder_num, required_norders]
        fail_msg.append(textdict['40-013-00018'].format(*fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(rorder_num)
    qc_names.append('rorder_num')
    qc_logic.append('rorder_num != {0}'.format(required_norders))
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #    quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params, passed


def write_localisation_files(params, recipe, infile, image, rawfiles, combine,
                             fiber, props, order_profile, mean_backgrd,
                             rorder_num, max_signal, cent_coeffs, wid_coeffs,
                             center_fits, width_fits, qc_params):
    # set function name
    func_name = display_func(params, 'write_localisation_files', __NAME__)
    # get qc parameters
    max_removed_cent = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_CTR',
                              func=func_name)
    max_removed_wid = pcheck(params, 'QC_LOC_MAXFIT_REMOVED_WID',
                             func=func_name)
    rmsmax_cent = pcheck(params, 'QC_LOC_RMSMAX_CTR', func=func_name)
    rmsmax_wid = pcheck(params, 'QC_LOC_RMSMAX_WID', func=func_name)
    # this one comes from pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    fiberparams = pconst.FIBER_SETTINGS(params, fiber)
    # ------------------------------------------------------------------
    # Write image order_profile to file
    # ------------------------------------------------------------------
    # get a new copy to the order profile
    orderpfile = recipe.outputs['ORDERP_FILE'].newcopy(recipe=recipe,
                                                       fiber=fiber)
    # construct the filename from file instance
    orderpfile.construct_filename(params, infile=infile)
    # define header keys for output file
    # copy keys from input file
    orderpfile.copy_original_keys(infile)
    # add version
    orderpfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    orderpfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    orderpfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    orderpfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    orderpfile.add_hkey('KW_OUTPUT', value=orderpfile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    orderpfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add the calibration files use
    orderpfile = general.add_calibs_to_header(orderpfile, props)
    # add qc parameters
    orderpfile.add_qckeys(qc_params)
    # copy data
    orderpfile.data = order_profile
    # log that we are saving rotated image
    WLOG(params, '', TextEntry('40-013-00002', args=[orderpfile.filename]))
    # write image to file
    orderpfile.write()
    # add to output files (for indexing)
    recipe.add_output_file(orderpfile)
    # ------------------------------------------------------------------
    # Save and record of image of localization with order center
    #     and keywords
    # ------------------------------------------------------------------
    loco1file = recipe.outputs['LOCO_FILE'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    loco1file.construct_filename(params, infile=infile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    loco1file.copy_original_keys(infile)
    # add version
    loco1file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add output tag
    loco1file.add_hkey('KW_OUTPUT', value=loco1file.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    loco1file.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add the calibration files use
    loco1file = general.add_calibs_to_header(loco1file, props)
    # add localisation parameters
    loco1file.add_hkey('KW_LOC_BCKGRD', value=mean_backgrd)
    loco1file.add_hkey('KW_LOC_NBO', value=rorder_num)
    loco1file.add_hkey('KW_LOC_DEG_C', value=params['LOC_CENT_POLY_DEG'])
    loco1file.add_hkey('KW_LOC_DEG_W', value=params['LOC_WIDTH_POLY_DEG'])
    loco1file.add_hkey('KW_LOC_MAXFLX', value=max_signal)
    loco1file.add_hkey('KW_LOC_SMAXPTS_CTR', value=max_removed_cent)
    loco1file.add_hkey('KW_LOC_SMAXPTS_WID', value=max_removed_wid)
    loco1file.add_hkey('KW_LOC_RMS_CTR', value=rmsmax_cent)
    loco1file.add_hkey('KW_LOC_RMS_WID', value=rmsmax_wid)
    # write 2D list of position fit coefficients
    loco1file.add_hkeys_2d('KW_LOC_CTR_COEFF', values=cent_coeffs,
                           dim1name='order', dim2name='coeff')
    # write 2D list of width fit coefficients
    loco1file.add_hkeys_2d('KW_LOC_WID_COEFF', values=wid_coeffs,
                           dim1name='order', dim2name='coeff')
    # add qc parameters
    loco1file.add_qckeys(qc_params)
    # copy data
    loco1file.data = center_fits
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', TextEntry('40-013-00019', args=[loco1file.filename]))
    # write image to file
    loco1file.write()
    # add to output files (for indexing)
    recipe.add_output_file(loco1file)
    # ------------------------------------------------------------------
    # Save and record of image of sigma
    # ------------------------------------------------------------------
    loco2file = recipe.outputs['FWHM_FILE'].newcopy(recipe=recipe,
                                                    fiber=fiber)
    # construct the filename from file instance
    loco2file.construct_filename(params, infile=infile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from loco1file
    loco2file.copy_hdict(loco1file)
    # set output key
    loco2file.add_hkey('KW_OUTPUT', value=loco2file.name)
    # copy data
    loco2file.data = width_fits
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', TextEntry('40-013-00020', args=[loco2file.filename]))
    # write image to file
    loco2file.write()
    # add to output files (for indexing)
    recipe.add_output_file(loco2file)
    # ------------------------------------------------------------------
    # Save and Record of image of localization
    # ------------------------------------------------------------------
    if params['LOC_SAVE_SUPERIMP_FILE']:
        # --------------------------------------------------------------
        # super impose zeros over the fit in the image
        image5 = image_superimp(image, cent_coeffs)
        # --------------------------------------------------------------
        loco3file = recipe.outputs['SUP_FILE'].newcopy(recipe=recipe,
                                                       fiber=fiber)
        # construct the filename from file instance
        loco3file.construct_filename(params, infile=infile)
        # --------------------------------------------------------------
        # define header keys for output file
        # copy keys from loco1file
        loco3file.copy_hdict(loco1file)
        # set output key
        loco3file.add_hkey('KW_OUTPUT', value=loco3file.name)
        # copy data
        loco3file.data = image5
        # --------------------------------------------------------------
        # log that we are saving rotated image
        wargs = [loco3file.filename]
        WLOG(params, '', TextEntry('40-013-00021', args=wargs))
        # write image to file
        loco3file.write()
        # add to output files (for indexing)
        recipe.add_output_file(loco3file)
    # ------------------------------------------------------------------
    # return out files
    return orderpfile, loco1file


def loc_summary(recipe, it, params, qc_params, props, mean_backgrd, rorder_num,
                max_signal):
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_DPRTYPE', value=props['DPRTYPE'])
    recipe.plot.add_stat('KW_LOC_BCKGRD', value=mean_backgrd)
    recipe.plot.add_stat('KW_LOC_NBO', value=rorder_num)
    recipe.plot.add_stat('KW_LOC_DEG_C', value=params['LOC_CENT_POLY_DEG'])
    recipe.plot.add_stat('KW_LOC_DEG_W', value=params['LOC_WIDTH_POLY_DEG'])
    recipe.plot.add_stat('KW_LOC_MAXFLX', value=max_signal)
    recipe.plot.add_stat('KW_LOC_SMAXPTS_CTR',
                         value=params['QC_LOC_MAXFIT_REMOVED_CTR'])
    recipe.plot.add_stat('KW_LOC_SMAXPTS_WID',
                         value=params['QC_LOC_MAXFIT_REMOVED_WID'])
    recipe.plot.add_stat('KW_LOC_RMS_CTR',
                         value=params['QC_LOC_RMSMAX_CTR'])
    recipe.plot.add_stat('KW_LOC_RMS_WID',
                         value=params['QC_LOC_RMSMAX_WID'])
    # construct summary
    recipe.plot.summary_document(it, qc_params)


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
                position = mp.nansum(lx * ly * 1.0) / mp.nansum(ly)
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
                position = mp.nansum(lx * ly * 1.0) / mp.nansum(ly)
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
        max_ptp_frac = mp.nanmax(abs_res/y) * 100
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
            max_ptp_frac = mp.nanmax(abs_res / yo) * 100
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
    a = mp.nanpolyfit(x, y, deg=f)[::-1]
    # Get the intial fit data
    fit = np.polyval(a[::-1], x)
    # work out residuals
    res = y - fit
    # Work out absolute residuals
    abs_res = abs(res)
    # work out rms
    rms = mp.nanstd(res)
    # work out max point to point of residuals
    max_ptp = mp.nanmax(abs_res)
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

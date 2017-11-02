#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-25 at 11:31

@author: cook



Version 0.0.0
"""

import numpy as np
import matplotlib.pyplot as plt

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS.spirouCore import spirouPlot as splt

# =============================================================================
# Define variables
# =============================================================================
# Define the name of this module
__NAME__ = 'spirouLOCOR.py'
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# get the logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------


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
    fparam = ParamDict()
    # loop around keys in FIBER_PARAMS
    for key in pp['FIBER_PARAMS']:
        # construct the parameter key (must ex
        configkey = ('{0}_{1}'.format(key, fiber)).upper()
        # check that key (in _fiber form) is in parameter dictionary
        if configkey not in pp:
            WLOG('error', pp['log_opt'], ('Config Error: Key {0} does not '
                                          'exist in parameter dictionary'
                                          '').format(configkey))

        fparam[key.upper()] = pp[configkey]
        fparam.set_source(key.upper(), __NAME__ + '/fiber_params()')

    # add fiber to the parameters
    fparam['fiber'] = fiber
    fparam.set_source('fiber', __NAME__ + '/fiber_params()')
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
    miny, maxy = measure_box_min_max(y, pp['IC_LOCNBPIX'])
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
        splt.locplot_y_miny_maxy(y, miny, maxy)
    if pp['DRS_PLOT']:
        splt.locplot_y_miny_maxy(y)

    # set function name (for source)
    __funcname__ = '/measure_background_and_get_central_pixels()'
    # Add to loc
    loc['ycc'] = ycc
    loc.set_source('ycc', __NAME__ + __funcname__)
    loc['mean_backgrd'] = mean_backgrd
    loc.set_source('mean_backgrd', __NAME__ + __funcname__)
    loc['max_signal'] = max_signal
    loc.set_source('max_signal', __NAME__ + __funcname__)
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

    :return loc: dictionary, parameter dictionary
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
            center, width = locate_order_center(**lkwargs)
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
            splt.debug_locplot_finding_orders(*dvars)
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
            splt.locplot_order(frame, x, y)
    # -------------------------------------------------------------------------
    # Work out the fit value at ic_cent_col (for logging)
    cfitval = np.polyval(acoeffs[::-1], pp['IC_CENT_COL'])
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
            splt.debug_locplot_fit_residual(pp, loc, rnum, kind)
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


def smoothed_boxmean_image(image, size, weighted=True, mode='convolve'):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels.

        if mode='convolve' (default) then this is done
        by convolving a top-hat function with the image (FAST)
        - note produces small inconsistencies due to FT of top-hat function

        if mode='manual' then this is done by working out the mean in each
        box manually (SLOW)

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param weighted: bool, if True pixel values less than zero are weighted to
                     a value of 1e-6 and values above 0 are weighted to a value
                     of 1
    :param mode: string, if 'convolve' convoles with a top-hat function of the
                         size "box" for each column (FAST) - note produces small
                         inconsistencies due to FT of top-hat function

                         if 'manual' calculates every box individually (SLOW)

    :return newimage: numpy array (2D), the smoothed image
    """
    if mode == 'convolve':
        return smoothed_boxmean_image2(image, size, weighted=weighted)
    if mode == 'manual':
        return smoothed_boxmean_image1(image, size, weighted=weighted)
    else:
        emsg = 'mode keyword={0} not valid. Must be "convolve" or "manual"'
        raise KeyError(emsg.format(mode))


def smoothed_boxmean_image1(image, size, weighted=True):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param weighted: bool, if True pixel values less than zero are weighted to
                     a value of 1e-6 and values above 0 are weighted to a value
                     of 1

    :return newimage: numpy array (2D), the smoothed image

    For 1 loop, best of 3: 628 ms per loop
    """
    newimage = np.zeros_like(image)

    # loop around each pixel column
    for it in range(0, image.shape[1], 1):
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
            part = image[:, it - size: it + size + 1]
        # get the weights (pixels below 0 are set to 1e-6, pixels above to 1)
        if weighted:
            weights = np.where(part > 0, 1, 1.e-6)
        else:
            weights = np.ones(len(part))
        # apply the weighted mean for this column
        newimage[:, it] = np.average(part, axis=1, weights=weights)
    # return the new smoothed image
    return newimage


def smoothed_boxmean_image2(image, size, weighted=True):
    """
    Produce a (box) smoothed image, smoothed by the mean of a box of
        size=2*"size" pixels, edges are dealt with by expanding the size of the
        box from or to the edge - essentially expanding/shrinking the box as
        it leaves/approaches the edges. Performed along the columns.
        pixel values less than 0 are given a weight of 1e-6, pixel values
        above 0 are given a weight of 1

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param weighted: bool, if True pixel values less than zero are weighted to
                     a value of 1e-6 and values above 0 are weighted to a value
                     of 1

    :return newimage: numpy array (2D), the smoothed image

    For 10 loops, best of 3: 94.7 ms per loop
    """
    # define a box to smooth by
    box = np.ones(size)
    # defined the weights for each pixel
    if weighted:
        weights = np.where(image > 0, 1.0, 1.e-6)
    else:
        weights = np.ones_like(image)
    # new weighted image
    weightedimage = image * weights

    # need to work on each row separately
    newimage = np.zeros_like(image)
    for row in range(image.shape[0]):
        # work out the weighted image
        s_weighted_image = np.convolve(weightedimage[row], box, mode='same')
        s_weights = np.convolve(weights[row], box, mode='same')
        # apply the weighted mean for this column
        newimage[row] = s_weighted_image/s_weights
    # return new image
    return newimage


def __test_smoothed_boxmean_image(image, size, row=1000, column=1000):
    """
    This is a test code for comparison between smoothed_boxmean_image1 "manual"
    and smoothed_boxmean_image2 "convovle"

    :param image: numpy array (2D), the image
    :param size: int, the number of pixels to mask before and after pixel
                 (for every row)
                 i.e. box runs from  "pixel-size" to "pixel+size" unless
                 near an edge
    :param column: int, the column number to plot for
    :return None:
    """
    # get the new images
    image1 = smoothed_boxmean_image(image, size)
    image2 = smoothed_boxmean_image2(image, size)
    # set up the plot
    fsize = (4, 6)
    plt.figure()
    frames = [plt.subplot2grid(fsize, (0, 0), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (0, 2), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (0, 4), colspan=2, rowspan=2),
              plt.subplot2grid(fsize, (2, 0), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (2, 3), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (3, 0), colspan=3, rowspan=1),
              plt.subplot2grid(fsize, (3, 3), colspan=3, rowspan=1)]
    # plot the images and image diff
    frames[0].imshow(image1)
    frames[0].set_title('Image Old method')
    frames[1].imshow(image2)
    frames[1].set_title('Image New method')
    frames[2].imshow(image1 - image2)
    frames[2].set_title('Image1 - Image2')
    # plot the column plot
    frames[3].plot(image[:, column], label='Original')
    frames[3].plot(image1[:, column], label='Old method')
    frames[3].plot(image2[:, column], label='New method')
    frames[3].legend()
    frames[3].set_title('Column {0}'.format(column))
    frames[4].plot(image1[:, column] - image2[:, column])
    frames[4].set_title('Column {0}  Image1 - Image2'.format(column))
    # plot the row plot
    frames[5].plot(image[row, :], label='Original')
    frames[5].plot(image1[row, :], label='Old method')
    frames[5].plot(image2[row, :], label='New method')
    frames[5].legend()
    frames[5].set_title('Row {0}'.format(row))
    frames[6].plot(image1[row, :] - image2[row, :])
    frames[6].set_title('Row {0}  Image1 - Image2'.format(row))
    plt.subplots_adjust(hspace=0.5)

    if not plt.isinteractive():
        plt.show()
        plt.close()


def measure_box_min_max(image, size):
    """
    Measure the minimum and maximum pixel value for each row using a box which
    contains all pixels for rows:  row-size to row+size and all columns.

    Edge pixels (0-->size and (image.shape[0]-size)-->image.shape[0] are
    set to the values for row=size and row=(image.shape[0]-size)

    :param image: numpy array (2D), the image
    :param size: int, the half size of the box to use (half height)
                 so box is defined from  row-size to row+size

    :return min_image: numpy array (1D length = image.shape[0]), the row values
                       for minimum pixel defined by a box of row-size to
                       row+size for all columns
    :retrun max_image: numpy array (1D length = image.shape[0]), the row values
                       for maximum pixel defined by a box of row-size to
                       row+size for all columns
    """
    # get length of rows
    ny = image.shape[0]
    # Set up min and max arrays (length = number of rows)
    min_image = np.zeros(ny, dtype=float)
    max_image = np.zeros(ny, dtype=float)
    # loop around each pixel from "size" to length - "size" (non-edge pixels)
    # and get the minimum and maximum of each box
    for it in range(size, ny - size):
        min_image[it] = np.min(image[it-size:it+size])
        max_image[it] = np.max(image[it-size:it+size])

    # deal with leading edge --> set to value at size
    min_image[0:size] = min_image[size]
    max_image[0:size] = max_image[size]
    # deal with trailing edge --> set to value at (image.shape[0]-size-1)
    min_image[ny-size:] = min_image[ny-size-1]
    max_image[ny-size:] = max_image[ny-size-1]
    # return arrays for minimum and maximum (box smoothed)
    return min_image, max_image


# def locate_center_order_positions(cvalues, threshold, mode='convolve',
#                                   min_width=None):
#     """
#     Takes the central pixel values and finds orders by looking for the start
#     and end of orders above threshold
#
#         if mode='convolve' (default) then this is done
#         by convolving a top-hat function with a mask of cvalues>threshold (FAST)
#
#         if mode='manual' then this is done by working out the star and end
#         positions manually (SLOW)
#
#     :param cvalues: numpy array (1D) size = number of rows,
#                     the central pixel values
#     :param threshold: float, the threshold above which to find pixels as being
#                       part of an order
#     :param mode: string, if 'convolve' convolves a top-hat function with a mask
#                          of cvalues>threshold (FAST)
#
#                          if 'manual' manually counts every start and end (SLOW)
#
#     :param min_width: int or None, if not None sets a minimum width requirement
#                       for the size of the order (disregards
#
#     :return positions: numpy array (1D), size=len(cvalues),
#                        the pixel positions in cvalues where the centers of each
#                        order should be
#
#     :return widths: numpy array (1D), size=len(cvalues), the widths of each
#                     order
#     """
#     if mode == 'convolve':
#         return locate_order_positions2(cvalues, threshold, min_width)
#     if mode == 'manual':
#         return locate_order_positions1(cvalues, threshold, min_width)
#     else:
#         emsg = 'mode keyword={0} not valid. Must be "convolve" or "manual"'
#         raise KeyError(emsg.format(mode))


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
                position = np.sum(lx * ly * 1.0) / np.sum(ly)
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
                position = np.sum(lx * ly * 1.0) / np.sum(ly)
                # width is just the distance from start to end
                width = abs(order_end - order_start)
        # if row is still below threshold then move the row number forward
        else:
            row += 1
    # finally return the positions
    return position, width


# def locate_order_positions2(cvalues, threshold, min_width=None):
#     """
#     Test version
#
#     Takes the central pixel values and finds orders by looking for the start
#     and end of orders above threshold
#
#     :param cvalues: numpy array (1D) size = number of rows,
#                     the central pixel values
#     :param threshold: float, the threshold above which to find pixels as being
#                       part of an order
#     :param min_width: int or None, if not None sets a minimum width requirement
#                       for the size of the order (disregards
#
#     :return positions: numpy array (1D), size=len(cvalues),
#                        the pixel positions in cvalues where the centers of each
#                        order should be
#
#     :return widths: numpy array (1D), size=len(cvalues), the widths of each
#                     order
#
#     For 1000 loops, best of 3: 401 µs per loop
#     """
#     # deal with no min_width
#     if min_width is None:
#         min_width = 0
#     # define a mask of cvalues < threshold
#     mask = np.array(cvalues) > threshold
#     # if there is an order on the leading edge set ignore it (set to False)
#     row = 0
#     while mask[row]:
#         mask[row] = False
#         row += 1
#     # define a box (of width 3) to smooth the mask
#     box = np.ones(3)
#     # convole box with mask
#     smoothmask = np.convolve(mask, box, mode='same')
#     # now where the array was [True, True, True] gives a value of 3 at the
#     #     center
#     # now where the array was [True, True, False] or [False, True, True] or
#     #     [True, False, True] gives a value of 2 at the center
#     # now where the array was [False, False, True] or [True, True, False] or
#     #     [False, True, False] gives a value of 1
#     # now where the array was [False, False, False] gives a value of 0
#     # --> we want the positions where the value==2
#     raw_positions = np.where(smoothmask == 2)[0]
#     # starts are the even positions
#     ostarts = raw_positions[::2]
#     # ends are the odd positions
#     oends = raw_positions[1::2]
#     # then loop around to calculate true positions
#     positions, widths = [], []
#     for start, end in zip(ostarts, oends):
#         if (end - start) > min_width:
#             # get x values and y values for order
#             # add one to end to get full pixel range
#             lx = np.arange(start, end + 1)
#             ly = cvalues[lx]
#             # position = sum of (lx * ly) / sum of sum(ly)
#             positions.append(np.sum(lx * ly) / np.sum(ly))
#             # width = end - start, add one to end to get full pixel range
#             widths.append(abs((end + 1 ) - start))
#     # return positions
#     return np.array(positions), np.array(widths)


# =============================================================================
# End of code
# =============================================================================


def image_localazation_superposition(image, coeffs):
    """
    Take an image
    :param image:
    :param coeffs:
    :return:
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

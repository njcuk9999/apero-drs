#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-27 at 10:13

@author: cook
"""
from __future__ import division
import numpy as np
import os
from scipy.ndimage import filters
from scipy.ndimage import map_coordinates as mapc
from scipy.optimize import curve_fit
from scipy.signal import medfilt
from scipy.stats import stats
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core import math
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.io import drs_path
from terrapipe.io import drs_fits
from terrapipe.io import drs_table
from terrapipe.io import drs_image
from . import general

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.shape.py'
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
# Define user functions
# =============================================================================
def construct_fp_table(params, filenames):
    # define storage for table columns
    fp_time, fp_exp, fp_pp_version = [], [], []
    basenames, nightnames = [], []
    # log that we are reading all dark files
    WLOG(params, '', TextEntry('40-014-00003'))
    # loop through file headers
    for it in range(len(filenames)):
        # get the basename from filenames
        basename = os.path.basename(filenames[it])
        # get the night name
        nightname = drs_path.get_nightname(params, filenames[it])
        # read the header
        hdr = drs_fits.read_header(params, filenames[it])
        # get keys from hdr
        acqtime = drs_fits.header_time(params, hdr, 'mjd')
        exptime = hdr[params['KW_EXPTIME'][0]]
        ppversion = hdr[params['KW_PPVERSION'][0]]
        # append to lists
        fp_time.append(float(acqtime))
        fp_exp.append(float(exptime))
        fp_pp_version.append(ppversion)
        basenames.append(basename)
        nightnames.append(nightname)
    # convert lists to table
    columns = ['NIGHTNAME', 'BASENAME', 'FILENAME', 'MJDATE', 'EXPTIME',
               'PPVERSION']
    values = [nightnames, basenames, filenames, fp_time, fp_exp,
              fp_pp_version]
    # make table using columns and values
    fp_table = drs_table.make_table(params, columns, values)
    # return table
    return fp_table


def construct_master_fp(params, recipe, dprtype, fp_table, image_ref, **kwargs):
    func_name = __NAME__ + '.construct_master_dark'
    # get constants from params/kwargs
    time_thres = pcheck(params, 'FP_MASTER_MATCH_TIME', 'time_thres', kwargs,
                        func_name)
    percent_thres = pcheck(params, 'FP_MASTER_PERCENT_THRES', 'percent_thres',
                           kwargs, func_name)
    qc_res = pcheck(params, 'SHAPE_QC_LTRANS_RES_THRES', 'qc_res', kwargs,
                    func_name)
    min_num = pcheck(params, 'SHAPE_FP_MASTER_MIN_IN_GROUP', 'min_num', kwargs,
                     func_name)

    # get col data from dark_table
    filenames = fp_table['FILENAME']
    fp_times = fp_table['MJDATE']

    # ----------------------------------------------------------------------
    # match files by date
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', TextEntry('40-014-00004', args=[time_thres]))
    # match files by time
    matched_id = drs_path.group_files_by_time(params, fp_times, time_thres)

    # ----------------------------------------------------------------------
    # Read individual files and sum groups
    # ----------------------------------------------------------------------
    # log process
    WLOG(params, '', TextEntry('40-014-00005'))
    # Find all unique groups
    u_groups = np.unique(matched_id)
    # storage of dark cube
    fp_cube, transforms_list, fp_dprtypes = [], [], []
    fp_darkfiles, fp_badpfiles, fp_backfiles =  [], [], []
    # loop through groups
    for g_it, group_num in enumerate(u_groups):
        # log progress
        wargs = [g_it + 1, len(u_groups)]
        WLOG(params, 'info', TextEntry('40-014-00006', args=wargs))
        # find all files for this group
        fp_ids = filenames[matched_id == group_num]
        # only combine if 3 or more images were taken
        if len(fp_ids) >= min_num:
            # load this groups files into a cube
            cube = []
            for f_it, filename in enumerate(fp_ids):
                # log reading of data
                wargs = [os.path.basename(filename), f_it + 1, len(fp_ids)]
                WLOG(params, 'info', TextEntry('40-014-00007', args=wargs))
                # get infile from filetype
                fpfile_it = core.get_file_definition(dprtype,
                                                     params['INSTRUMENT'])
                # construct new infile instance
                fpfile_it = fpfile_it.newcopy(filename=filename, recipe=recipe)
                fpfile_it.read()
                # get and correct file
                cargs = [params, recipe, fpfile_it]
                ckwargs = dict(n_percentile=percent_thres,
                               correctback=False)
                props_it, image_it = general.calibrate_ppfile(*cargs, **ckwargs)
                # extract properties and add to lists
                fp_dprtypes.append(props_it['DPRTYPE'])
                fp_darkfiles.append(os.path.basename(props_it['DARKFILE']))
                fp_badpfiles.append(os.path.basename(props_it['BADPFILE']))
                fp_backfiles.append(os.path.basename(props_it['BACKFILE']))
                # append to cube
                cube.append(image_it)
            # log process
            WLOG(params, '', TextEntry('40-014-00008', args=[len(fp_ids)]))
            # median fp cube
            with warnings.catch_warnings(record=True) as _:
                groupfp = np.nanmedian(cube, axis=0)
            # shift group to master
            gout = get_linear_transform_params(params, image_ref, groupfp)
            transforms, xres, yres = gout
            # quality control on group
            if transforms is None:
                # log that image quality too poor
                wargs = [g_it + 1]
                WLOG(params, 'warning', TextEntry('10-014-00001', args=wargs))
                # skip adding to group
                continue
            if (xres > qc_res) or (yres > qc_res):
                # log that xres and yres too larger
                wargs = [xres, yres, qc_res]
                WLOG(params, 'warning', TextEntry('10-014-00002', args=wargs))
                # skip adding to group
                continue
            # perform a final transform on the group
            groupfp = ea_transform(params, groupfp,
                                   lin_transform_vect=transforms)
            # append to cube
            fp_cube.append(groupfp)
            # append transforms to list
            for filename in fp_ids:
                transforms_list.append(transforms)
        else:
            eargs = [g_it + 1, min_num]
            WLOG(params, '', TextEntry('40-014-00015', args=eargs))
            # add blank properties
            fp_dprtypes.append('')
            fp_darkfiles.append('')
            fp_badpfiles.append('')
            fp_backfiles.append('')
            # append transforms to list
            for filename in fp_ids:
                transforms_list.append([np.nan]*6)

    # ----------------------------------------------------------------------
    # convert fp cube to array
    fp_cube = np.array(fp_cube)
    # convert transform_list to array
    tarrary = np.array(transforms_list)
    # ----------------------------------------------------------------------
    # add columns to fp_table
    colnames = ['DPRTYPE', 'DARKFILE', 'BADPFILE', 'BACKFILE', 'GROUPID',
                'DXREF', 'DYREF', 'A', 'B', 'C', 'D']
    values = [fp_dprtypes, fp_darkfiles, fp_badpfiles, fp_backfiles,
              matched_id, tarrary[:, 0], tarrary[:, 1], tarrary[:, 2],
              tarrary[:, 3], tarrary[:, 4], tarrary[:, 5]]
    for c_it, col in enumerate(colnames):
        fp_table[col] = values[c_it]
    # ----------------------------------------------------------------------
    # return fp_cube
    return fp_cube, fp_table


def get_linear_transform_params(params, image1, image2, **kwargs):

    func_name = __NAME__ + '.get_linear_transform_params()'
    # get parameters from params/kwargs
    maxn_percent = pcheck(params, 'SHAPE_MASTER_VALIDFP_PERCENTILE',
                          'maxn_perecent', kwargs, func_name)
    maxn_thres = pcheck(params, 'SHAPE_MASTER_VALIDFP_THRESHOLD',
                        'maxn_thres', kwargs, func_name)
    niterations = pcheck(params, 'SHAPE_MASTER_LINTRANS_NITER',
                         'niterations', kwargs, func_name)
    ini_boxsize = pcheck(params, 'SHAPE_MASTER_FP_INI_BOXSIZE',
                         'ini_boxsize', kwargs, func_name)
    small_boxsize = pcheck(params, 'SHAPE_MASTER_FP_SMALL_BOXSIZE',
                           'small_boxsize', kwargs, func_name)
    # get the shape of the image
    dim1, dim2 = image1.shape
    # check that image is correct shape
    if image2.shape != image1.shape:
        # log that the shapes are inconsistent
        eargs = [image1.shape, image2.shape, func_name]
        WLOG(params, 'error', TextEntry('00-014-00001', args=eargs))
    # linear transform vector
    # with dx0,dy0,A,B,C,D
    # we start assuming that there is no shift in x or y
    # and that the image is not sheared or rotated
    lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    # find the fp peaks (via max neighbours) in image1
    mask1 = _max_neighbour_mask(image1, maxn_percent, maxn_thres)
    # copy image2
    image3 = np.array(image2)
    # print out initial conditions of linear transform vector
    WLOG(params, 'info', TextEntry('40-014-00009'))
    # set up arguments
    ltv = np.array(lin_transform_vect)
    wargs1 = [dim2, (ltv[2] - 1) * dim2, ltv[3] * dim2]
    wargs2 = [dim2, ltv[3] * dim2, (ltv[5] - 1) * dim2]
    # add to output
    wmsg = TextEntry('')
    wmsg += '\tdx={0:.6f} dy={1:.6f}'.format(*ltv)
    wmsg += '\n\t{0}(A-1)={1:.6f}\t{0}B={2:.6f}'.format(*wargs1)
    wmsg += '\n\t{0}C={1:.6f}\t{0}(D-1)={2:.6f}'.format(*wargs2)
    WLOG(params, '', wmsg)
    # outputs
    xres, yres = np.nan, np.nan

    # loop around iterations
    for n_it in range(niterations):
        # log progress
        wargs = [n_it + 1, niterations]
        WLOG(params, '', TextEntry('40-014-00010', args=wargs))
        # transform image2 if we have some transforms (initial we don't)
        if n_it > 0:
            image3 = ea_transform(params, image2, lin_transform_vect)
        # find the fp peaks (via max neighbours) in image2
        mask2 = _max_neighbour_mask(image3, maxn_percent, maxn_thres)
        # we search in +- wdd to find the maximum number of matching
        # bright peaks. We first explore a big +-11 pixel range, but
        # afterward we can scan a much smaller region
        if n_it == 0:
            wdd = ini_boxsize
        else:
            wdd = small_boxsize
        # define the scanning range in dx and dy
        dd = np.arange(-wdd, wdd + 1)
        map_dxdy = np.zeros([len(dd), len(dd)])
        # peaks cannot be at the edges of the image
        mask1[:wdd + 1, :] = False
        mask1[:, :wdd + 1] = False
        mask1[-wdd -1:, :] = False
        mask1[:, -wdd -1:] = False
        # get the positions of the x and y peaks (based on mask1)
        ypeak1, xpeak1 = np.where(mask1)
        # fill map_dxdy with the mean of the wdd box
        for y_it in range(len(dd)):
            for x_it in range(len(dd)):
                # get the boolean values for mask 2 for this dd
                boxvalues = mask2[ypeak1 + dd[y_it], xpeak1 + dd[x_it]]
                # push these values into the map
                map_dxdy[y_it, x_it] = np.mean(boxvalues)
        # get the shifts for these mapped values
        pos = np.argmax(map_dxdy)
        dy0, dx0 = -dd[pos // len(dd)], -dd[pos % len(dd)]
        # shift by integer if dx0 or dy0 is not 0
        # this is used later to ensures that the pixels found as
        # peaks in one image are also peaks in the other.
        mask2b = np.roll(np.roll(mask2, dy0, axis=0), dx0, axis=1)
        # position of peaks in 2nd image
        xpeak2 = np.array(xpeak1 - dx0, dtype=int)
        ypeak2 = np.array(ypeak1 - dy0, dtype=int)
        # peaks in image1 must be peaks in image2 when accounting for the
        # integer offset
        keep = mask2b[ypeak1, xpeak1]
        xpeak1 = xpeak1[keep]
        ypeak1 = ypeak1[keep]
        xpeak2 = xpeak2[keep]
        ypeak2 = ypeak2[keep]
        # do a fit to these positions in both images to get the peak centers
        x1, y1 = _xy_acc_peak(xpeak1, ypeak1, image1)
        x2, y2 = _xy_acc_peak(xpeak2, ypeak2, image3)
        # we loop on the linear model converting x1 y1 to x2 y2
        nbad, ampsx, ampsy = 1, np.zeros(3), np.zeros(3)

        n_terms = len(x1)
        xrecon, yrecon = None, None
        while nbad != 0:
            # define vectory
            vvv = np.zeros([3, len(x1)])
            vvv[0, :], vvv[1, :], vvv[2, :] = np.ones_like(x1), x1, y1
            # linear minimisation of difference w.r.t. v
            ampsx, xrecon = math.linear_minimization(x1 - x2, vvv)
            ampsy, yrecon = math.linear_minimization(y1 - y2, vvv)
            # express distance of all residual error in x1-y1 and y1-y2
            # in absolute deviation
            xnanmed = np.nanmedian(np.abs((x1 - x2) - xrecon))
            ynanmed = np.nanmedian(np.abs((y1 - y2) - yrecon))
            xrms = ((x1 - x2) - xrecon) ** 2 / xnanmed
            yrms = ((y1 - y2) - yrecon) ** 2 / ynanmed
            # How many 'sigma' for the core of distribution
            nsig = np.sqrt(xrms ** 2 + yrms ** 2)
            with warnings.catch_warnings(record=True) as _:
                bad = nsig > 1.5
            # remove outliers and start again if there was one
            nbad = np.sum(bad)

            x1, x2 = x1[~bad], x2[~bad]
            y1, y2 = y1[~bad], y2[~bad]

            if len(x1) < (0.5 * n_terms):
                return None, None, None

        xres = np.std((x1 - x2) - xrecon)
        yres = np.std((y1 - y2) - yrecon)

        # we have our linear transform terms!
        dx0, dy0 = ampsx[0], ampsy[0]
        d_transform = [dx0, dy0, ampsx[1], ampsx[2], ampsy[1], ampsy[2]]
        # propagate to linear transform vector
        lin_transform_vect -= d_transform
        ltv = np.array(lin_transform_vect)

        # print out per iteration values
        # set up arguments
        ltv = np.array(lin_transform_vect)
        wargs1 = [dim2, (ltv[2] - 1) * dim2, ltv[3] * dim2]
        wargs2 = [dim2, ltv[3] * dim2, (ltv[5] - 1) * dim2]
        # add to output
        wmsg = TextEntry('')
        wmsg += '\tdx={0:.6f} dy={1:.6f}'.format(*ltv)
        wmsg += '\n\t{0}(A-1)={1:.6f}\t{0}B={2:.6f}'.format(*wargs1)
        wmsg += '\n\t{0}C={1:.6f}\t{0}(D-1)={2:.6f}'.format(*wargs2)
        WLOG(params, '', wmsg)

    # plot if in debug mode
    if params['DRS_DEBUG'] > 0 and params['DRS_PLOT'] > 0:
        # TODO: Add plot
        pass
    # return linear transform vector
    return lin_transform_vect, xres, yres


def ea_transform(params, image, lin_transform_vect=None,
                 dxmap=None, dymap=None):
    """
    Shifts / transforms image by three different transformations:

    a) a linear transform (defined by "lin_transform_vect")

        this is a list of components for the shift:
            dx, dy, A, B, C, D
        where dx and dy are shifts in x and y and A, B, C, D form the
        transform matrix:

                    [ A   B
                      C   D ]

    b) a shift in x position (dxmap) where a shift is defined for each pixel

    c) a shift in y position (dymap) where a shift is defined for each pixel

    :param image: numpy array (2D), the image to transform
    :param lin_transform_vect: np.ndarray [size=6], the linear transform
                               parameters (dx, dy, A, B, C, D)
    :param dxmap: numpy array (2D), the x shift map (same size as image)
    :param dymap: numpy array (2D), the y shift map (same size as image)

    :type image: np.ndarray
    :type lin_transform_vect: np.ndarray
    :type dxmap: np.ndarray
    :type dymap: np.ndarray

    :returns: The transformed image
    :rtype: np.ndarray
    """
    func_name = __NAME__ + '.ea_transform()'
    # check size of dx and dy map
    if dxmap is not None:
        if dxmap.shape != image.shape:
            eargs = [dxmap.shape, image.shape, func_name]
            WLOG(params, 'error', TextEntry('00-014-00002', args=eargs))
    if dymap is not None:
        if dymap.shape != image.shape:
            eargs = [dymap.shape, image.shape, func_name]
            WLOG(params, 'error', TextEntry('00-014-00003', args=eargs))
    # deal with no linear transform required (just a dxmap or dymap shift)
    if lin_transform_vect is None:
        lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    # copy the image
    image = np.array(image)
    # transforming an image with the 6 linear transform terms
    # Be careful with NaN values, there should be none
    dx, dy, A, B, C, D = lin_transform_vect
    # get the pixel locations for the image
    yy, xx = np.indices(image.shape, dtype=float)
    # get the shifted x pixel locations
    xx2 = dx + xx * A + yy * B
    if dxmap is not None:
        xx2 += dxmap
    # get the shifted y pixel locations
    yy2 = dy + xx * C + yy * D
    if dymap is not None:
        yy2 += dymap
    # get the valid (non Nan) pixels
    valid_mask = np.isfinite(image)
    # set the weight equal to the valid pixels (1 for valid, 0 for not valid)
    weight = valid_mask.astype(float)
    # set all NaNs to zero (for transform)
    image[~valid_mask] = 0
    # we need to properly propagate NaN in the interpolation.
    out_image = mapc(image, [yy2, xx2], order=2, cval=np.nan, output=float,
                     mode='constant')
    out_weight = mapc(weight, [yy2, xx2], order=2, cval=0, output=float,
                      mode='constant')
    # divide by the weight (NaN pixels)
    with warnings.catch_warnings(record=True) as _:
        out_image = out_image / out_weight
        out_image[out_weight < 0.5] = np.nan
    # return transformed image
    return out_image


def calculate_dxmap(params, hcdata, fpdata, wprops, lprops, **kwargs):

    func_name = __NAME__ + '.calculate_dxmap()'
    # get parameters from params/kwargs
    nbanana = pcheck(params, 'SHAPE_NUM_ITERATIONS', 'nbanana', kwargs,
                     func_name)
    width = pcheck(params, 'SHAPE_ORDER_WIDTH', 'width', kwargs, func_name)
    nsections = pcheck(params, 'SHAPE_NSECTIONS', 'nsections', kwargs,
                       func_name)
    large_angle_min = pcheck(params, 'SHAPE_LARGE_ANGLE_MIN',
                                'large_angle_min', kwargs, func_name)
    large_angle_max = pcheck(params, 'SHAPE_LARGE_ANGLE_MAX',
                                'large_angle_max', kwargs, func_name)
    large_angle_range = [large_angle_min, large_angle_max]
    small_angle_min = pcheck(params, 'SHAPE_SMALL_ANGLE_MIN',
                                'small_angle_min', kwargs, func_name)
    small_angle_max = pcheck(params, 'SHAPE_SMALL_ANGLE_MAX',
                                'small_angle_max', kwargs, func_name)
    small_angle_range = [small_angle_min, small_angle_max]
    sigclipmax = pcheck(params, 'SHAPE_SIGMACLIP_MAX', 'sigclipmax',
                        kwargs, func_name)
    med_filter_size = pcheck(params, 'SHAPE_MEDIAN_FILTER_SIZE',
                             'med_filter_size', kwargs, func_name)
    min_good_corr = pcheck(params, 'SHAPE_MIN_GOOD_CORRELATION',
                           'min_good_corr', kwargs, func_name)
    short_medfilt_width = pcheck(params, 'SHAPE_SHORT_DX_MEDFILT_WID',
                                 'short_medfilt_width', kwargs, func_name)
    long_medfilt_width = pcheck(params, 'SHAPE_LONG_DX_MEDFILT_WID',
                                'long_medfilt_width', kwargs, func_name)
    std_qc = pcheck(params, 'SHAPE_QC_DXMAP_STD', 'std_qc', kwargs, func_name)
    plot_on = pcheck(params, 'SHAPE_PLOT_PER_ORDER', 'plot_on',
                     kwargs, func_name)

    # get properties from property dictionaries
    nbo = lprops['NBO']
    acc = lprops['CENT_COEFFS']
    # get the dimensions
    dim1, dim2 = fpdata.shape
    # -------------------------------------------------------------------------
    # define storage for plotting
    slope_deg_arr, slope_arr, skeep_arr = [], [], []
    xsec_arr, ccor_arr = [], []
    ddx_arr, dx_arr = [], []
    dypix_arr, cckeep_arr = [], []

    # define storage for output
    master_dxmap = np.zeros_like(fpdata)
    map_orders = np.zeros_like(fpdata) - 1
    order_overlap = np.zeros_like(fpdata)
    slope_all_ord = np.zeros((nbo, dim2))
    corr_dx_from_fp = np.zeros((nbo, dim2))
    corr_dx_from_fp = np.zeros((nbo, dim2))
    xpeak2 = [[]] * nbo
    peakval2 = [[]] * nbo
    ewval2 = [[]] * nbo
    err_pix = [[]] * nbo
    good_mask = [[]] * nbo
    # -------------------------------------------------------------------------
    # create the x pixel vector (used with polynomials to find
    #    order center)
    xpix = np.array(range(dim2))
    # y order center positions (every other one)
    ypix = np.zeros((nbo, dim2))
    # loop around order number
    for order_num in range(nbo):
        # x pixel vecctor that is used with polynomials to
        # find the order center y order center
        ypix[order_num] = np.polyval(acc[order_num * 2][::-1], xpix)
    # -------------------------------------------------------------------------
    # storage of the dxmap standard deviations
    dxmap_stds = []
    # -------------------------------------------------------------------------
    # iterating the correction, from coarser to finer
    for banana_num in range(nbanana):
        # ---------------------------------------------------------------------
        # we use the code that will be used by the extraction to ensure
        # that slice images are as straight as can be
        # ---------------------------------------------------------------------
        # if the map is not zeros, we use it as a starting point
        if np.sum(master_dxmap != 0) != 0:
            hcdata2 = ea_transform(hcdata, dxmap=master_dxmap)
            fpdata2 = ea_transform(fpdata, dxmap=master_dxmap)
            # if this is not the first iteration, then we must be really close
            # to a slope of 0
            range_slopes_deg = small_angle_range
        else:
            hcdata2 = np.array(hcdata)
            fpdata2 = np.array(fpdata)
            # starting point for slope exploration
            range_slopes_deg = large_angle_range
        # expressed in pixels, not degrees
        range_slopes = np.tan(np.deg2rad(np.array(range_slopes_deg)))
        # set up iteration storage
        slope_deg_arr_i, slope_arr_i, skeep_arr_i = [], [], []
        xsec_arr_i, ccor_arr_i = [], []
        ddx_arr_i, dx_arr_i = [], []
        dypix_arr_i,  cckeep_arr_i = [], []

        # storage for loc2
        loc2s = []
        # get dx array (NaN)
        dx = np.zeros((nbo, width)) + np.nan
        # ---------------------------------------------------------------------
        # loop around orders
        for order_num in range(nbo):
            # -----------------------------------------------------------------
            # Log progress
            wmsg = 'Banana iteration: {0}/{1}: Order {2}/{3} '
            wargs = [banana_num + 1, nbanana, order_num + 1, nbo]
            WLOG(params, '', wmsg.format(*wargs))
            # -----------------------------------------------------------------
            # defining a ribbon that will contain the straightened order
            ribbon_hc = np.zeros([width, dim2])
            ribbon_fp = np.zeros([width, dim2])
            # get the widths
            widths = np.arange(width) - width / 2.0
            # get all bottoms and tops
            bottoms = ypix[order_num] - width/ 2 - 2
            tops = ypix[order_num] + width/ 2 + 2
            # splitting the original image onto the ribbon
            for ix in range(dim2):
                # define bottom and top that encompasses all 3 fibers
                bottom = int(bottoms[ix])
                top = int(tops[ix])
                sx = np.arange(bottom, top)
                # calculate spline interpolation and ribbon values
                if bottom > 0:
                    # for the hc data
                    spline_hc = math.iuv_spline(sx, hcdata2[bottom:top, ix],
                                                ext=1, k=3)
                    ribbon_hc[:, ix] = spline_hc(ypix[order_num, ix] + widths)
                    # for the fp data
                    spline_fp = math.iuv_spline(sx, fpdata2[bottom:top, ix],
                                                ext=1, k=3)
                    ribbon_fp[:, ix] = spline_fp(ypix[order_num, ix] + widths)

            # normalizing ribbon stripes to their median abs dev
            for iw in range(width):
                # for the hc data
                norm_fp = np.nanmedian(np.abs(ribbon_fp[iw, :]))
                ribbon_hc[iw, :] = ribbon_hc[iw, :] / norm_fp
                # for the fp data
                ribbon_fp[iw, :] = ribbon_fp[iw, :] / norm_fp
            # range explored in slopes
            # TODO: question Where does the /8.0 come from?
            sfactor = (range_slopes[1] - range_slopes[0]) / 8.0
            slopes = (np.arange(9) * sfactor) + range_slopes[0]
            # log the range slope exploration
            wmsg = '\tRange slope exploration: {0:.3f} -> {1:.3f} deg'
            wargs = [range_slopes_deg[0], range_slopes_deg[1]]
            WLOG(params, '', wmsg.format(*wargs))
            # -------------------------------------------------------------
            # the domain is sliced into a number of sections, then we
            # find the tilt that maximizes the RV content
            xsection = dim2 * (np.arange(nsections) + 0.5) / nsections
            dxsection = np.repeat([np.nan], len(xsection))
            keep = np.zeros(len(dxsection), dtype=bool)
            ribbon_fp2 = np.array(ribbon_fp)
            # RV content per slice and per slope
            rvcontent = np.zeros([len(slopes), nsections])
            # loop around the slopes
            for islope, slope in enumerate(slopes):
                # copy the ribbon
                ribbon_fp2 = np.array(ribbon_fp)
                # interpolate new slope-ed ribbon
                for iw in range(width):
                    # get the ddx value
                    ddx = (iw - width/2.0) * slope
                    # get the spline
                    spline = math.iuv_spline(xpix, ribbon_fp[iw, :], ext=1)
                    # calculate the new ribbon values
                    ribbon_fp2[iw, :] = spline(xpix + ddx)
                # record the profile of the ribbon
                profile = np.nanmedian(ribbon_fp2, axis=0)
                # loop around the sections to record rv content
                for nsection in range(nsections):
                    # sum of integral of derivatives == RV content.
                    # This should be maximal when the angle is right
                    start = nsection * dim2//nsections
                    end = (nsection + 1) * dim2//nsections
                    grad = np.gradient(profile[start:end])
                    rvcontent[islope, nsection] = np.nansum(grad ** 2)
            # -------------------------------------------------------------
            # we find the peak of RV content and fit a parabola to that peak
            for nsection in range(nsections):
                # we must have some RV content (i.e., !=0)
                if np.nanmax(rvcontent[:, nsection]) != 0:
                    vec = np.ones_like(slopes)
                    vec[0], vec[-1] = 0, 0
                    # get the max pixel
                    maxpix = np.nanargmax(rvcontent[:, nsection] * vec)
                    # max RV and fit on the neighbouring pixels
                    xff = slopes[maxpix - 1: maxpix + 2]
                    yff = rvcontent[maxpix - 1: maxpix + 2, nsection]
                    coeffs = math.nanpolyfit(xff, yff, 2)
                    # if peak within range, then its fine
                    dcoeffs = -0.5 * coeffs[1] / coeffs[0]
                    if np.abs(dcoeffs) < 1:
                        dxsection[nsection] = dcoeffs
                # we sigma-clip the dx[x] values relative to a linear fit
                keep = np.isfinite(dxsection)
            # -------------------------------------------------------------
            # work out the median slope
            dxdiff = dxsection[1:] - dxsection[:-1]
            xdiff = xsection[1:] - xsection[:-1]
            medslope = np.nanmedian(dxdiff/xdiff)
            # work out the residual of dxsection (based on median slope)
            residual = dxsection - (medslope * xsection)
            residual = residual - np.nanmedian(residual)
            res_residual = residual - np.nanmedian(residual)
            residual = residual / np.nanmedian(np.abs(res_residual))
            # work out the maximum sigma and update keep vector
            sigmax = np.nanmax(np.abs(residual[keep]))
            with warnings.catch_warnings(record=True) as _:
                keep &= np.abs(residual) < sigclipmax
            # -------------------------------------------------------------
            # sigma clip
            while sigmax > sigclipmax:
                # recalculate the fit
                coeffs = math.nanpolyfit(xsection[keep], dxsection[keep], 2)
                # get the residuals
                res = dxsection - np.polyval(coeffs, xsection)
                # normalise residuals
                res = res - np.nanmedian(res[keep])
                res = res / np.nanmedian(np.abs(res[keep]))
                # calculate the sigma
                sigmax = np.nanmax(np.abs(res[keep]))
                # do not keep bad residuals
                with warnings.catch_warnings(record=True) as _:
                    keep &= np.abs(res) < sigclipmax
            # -------------------------------------------------------------
            # fit a 2nd order polynomial to the slope vx position
            #    along order
            coeffs = math.nanpolyfit(xsection[keep], dxsection[keep], 2)
            # log slope at center
            s_xpix = dim2 // 2
            s_ypix = np.rad2deg(np.arctan(np.polyval(coeffs, s_xpix)))
            wmsg = '\tSlope at pixel {0}: {1:.5f} deg'
            wargs = [s_xpix, s_ypix]
            WLOG(params, '', wmsg.format(*wargs))
            # get slope for full range
            slope_all_ord[order_num] = np.polyval(coeffs, np.arange(dim2))
            # -------------------------------------------------------------
            # append to storage (for plotting)
            xsec_arr_i.append(np.array(xsection))
            slope_deg_arr_i.append(np.rad2deg(np.arctan(dxsection)))
            slope_arr_i.append(np.rad2deg(np.arctan(slope_all_ord[order_num])))
            skeep_arr_i.append(np.array(keep))

            # -----------------------------------------------------------------
            # append to new loc
            loc2 = ParamDict()
            if params['DRS_PLOT'] and params['DRS_DEBUG'] >= 2:
                # add temp keys for debug plot
                loc2['NUMBER_ORDERS'] = loc['NUMBER_ORDERS']
                loc2['HCDATA'] = loc['HCDATA']
                loc2['SLOPE_DEG'] = np.rad2deg(np.arctan(dxsection))
                loc2['SLOPE'] = np.rad2deg(np.arctan(slope_all_ord[order_num]))
                loc2['S_KEEP'] = np.array(keep)

            # -------------------------------------------------------------
            # correct for the slope the ribbons and look for the
            #    slicer profile in the fp
            yfit = np.polyval(coeffs, xpix)
            for iw in range(width):
                # get the x shift
                ddx = (iw - width/2.0) * yfit
                # calculate the spline at this width
                spline_fp = math.iuv_spline(xpix, ribbon_fp[iw, :], ext=1)
                # push spline values with shift into ribbon2
                ribbon_fp2[iw, :] = spline_fp(xpix + ddx)
            # -------------------------------------------------------------
            # correct for the slope the ribbons and look for the slicer profile
            #    in the hc
            ribbon_hc2 = np.array(ribbon_hc)
            for iw in range(width):
                # get the x shift
                ddx = (iw - width/2.0) * yfit
                # calculate the spline at this width
                spline_hc = math.iuv_spline(xpix, ribbon_hc[iw, :], ext=1)
                # push spline values with shift into ribbon2
                ribbon_hc2[iw, :] = spline_hc(xpix + ddx)

            # -------------------------------------------------------------
            # get the median values of the fp and hc
            sp_fp = np.nanmedian(ribbon_fp2, axis=0)
            sp_hc = np.nanmedian(ribbon_hc2, axis=0)

            loc = _get_offset_sp(params, loc, sp_fp, sp_hc, order_num)
            corr_dx_from_fp[order_num] = loc['CORR_DX_FROM_FP'][order_num]

            # -------------------------------------------------------------
            # median FP peak profile. We will cross-correlate each
            # row of the ribbon with this
            profile = np.nanmedian(ribbon_fp2, axis=0)
            medianprofile = filters.median_filter(profile, med_filter_size)
            profile = profile - medianprofile

            # -------------------------------------------------------------
            # cross-correlation peaks of median profile VS position
            #    along ribbon
            # TODO: Question: Why -3 to 4 where does this come from?
            ddx = np.arange(-3, 4)
            # set up cross-correlation storage
            ccor = np.zeros([width, len(ddx)], dtype=float)
            # loop around widths
            for iw in range(width):
                for jw in range(len(ddx)):
                    # calculate the peasron r coefficient
                    xff = ribbon_fp2[iw, :]
                    yff = np.roll(profile, ddx[jw])
                    pearsonr_value = stats.pearsonr(xff, yff)[0]
                    # push into cross-correlation storage
                    ccor[iw, jw] = pearsonr_value
                # fit a gaussian to the cross-correlation peak
                xvec = ddx
                yvec = ccor[iw, :]
                with warnings.catch_warnings(record=True) as _:
                    gcoeffs, _ = math.gauss_fit_nn(xvec, yvec, 4)
                # check that max value is good
                if np.nanmax(ccor[iw, :]) > min_good_corr:
                    dx[order_num, iw] = gcoeffs[1]
            # -------------------------------------------------------------
            # remove any offset in dx, this would only shift the spectra
            dypix = np.arange(len(dx[order_num]))
            with warnings.catch_warnings(record=True):
                keep = np.abs(dx[order_num] - np.nanmedian(dx[order_num])) < 1
            keep &= np.isfinite(dx[order_num])
            # -------------------------------------------------------------
            # if the first pixel is nan and the second is OK,
            #    then for continuity, pad
            # if (not keep[0]) and keep[1]:
            #     keep[0] = True
            #     dx[0] = dx[1]
            # # same at the other end
            # if (not keep[-1]) and keep[-2]:
            #     keep[-1] = True
            #     dx[-1] = dx[-2]

            # -------------------------------------------------------------
            # append to storage for plotting
            ccor_arr_i.append(np.array(ccor))
            ddx_arr_i.append(np.array(ddx))
            dx_arr_i.append(np.array(dx[order_num]))
            dypix_arr_i.append(np.array(dypix))
            cckeep_arr_i.append(np.array(keep))
            # -----------------------------------------------------------------
            if params['DRS_PLOT'] and params['DRS_DEBUG'] >= 2:
                # add temp keys for debug plot
                loc2['XSECTION'] = np.array(xsection)
                loc2['CCOR'], loc2['DDX'] = ccor, ddx
                loc2['DX'], loc2['DYPIX'] = dx[order_num], dypix
                loc2['C_KEEP'] = keep
            # append loc2 to storage
            loc2s.append(loc2)
            # -----------------------------------------------------------------
            # set those values that should not be kept to NaN
            dx[order_num][~keep] = np.nan

        # -----------------------------------------------------------------
        # get the median filter of dx (short median filter)
        dx2_short = np.array(dx)
        for iw in range(width):
            margs = [dx[:, iw], short_medfilt_width]
            dx2_short[:, iw] = math.median_filter_ea(*margs)
        # get the median filter of short dx with longer median
        #     filter/second pass
        dx2_long = np.array(dx)
        for iw in range(width):
            margs = [dx2_short[:, iw], long_medfilt_width]
            dx2_long[:, iw] = math.median_filter_ea(*margs)
        # apply short dx filter to dx2
        dx2 = np.array(dx2_short)
        # apply long dx filter to NaN positions of short dx filter
        nanmask = ~np.isfinite(dx2)
        dx2[nanmask] = dx2_long[nanmask]

        # ---------------------------------------------------------------------
        # dx plot
        if params['DRS_PLOT'] > 0:
            # TODO: Do plots
            pass
            # # plots setup: start interactive plot
            # sPlt.start_interactive_session(p)
            # # plot
            # sPlt.slit_shape_dx_plot(p, dx, dx2, banana_num)
            # # end interactive section
            # sPlt.end_interactive_session(p)

        # ---------------------------------------------------------------------
        # loop around orders
        for order_num in range(nbo):
            # -------------------------------------------------------------
            # log process
            wmsg = ('Update of the big dx map after filtering of pre-order '
                    'dx: {0}/{1}')
            wargs = [order_num + 1, nbo]
            WLOG(params, '', wmsg.format(*wargs))
            # -------------------------------------------------------------
            # spline everything onto the master DX map
            #    ext=3 forces that out-of-range values are set to boundary
            #    value this simply uses the last reliable dx measurement for
            #    the neighbouring slit position

            # redefine keep array from dx2
            keep = np.isfinite(dx2[order_num])
            # redefine dypix
            dypix = np.arange(len(keep))
            # get locations of keep
            pos_keep = np.where(keep)[0]
            # set the start point
            start_good_ccor = np.min(pos_keep) - 2
            # deal with start being out-of-bounds
            if start_good_ccor == -1:
                start_good_ccor = 0
            # set the end point
            end_good_ccor = np.max(pos_keep) + 2
            # deal with end being out-of-bounds
            if end_good_ccor == width:
                end_good_ccor = width - 1
            # work out spline
            spline = math.iuv_spline(dypix[keep], dx2[order_num][keep], ext=3)
            # define a mask for the good ccor
            good_ccor_mask = np.zeros(len(keep), dtype=bool)
            good_ccor_mask[start_good_ccor:end_good_ccor] = True

            # log start and end points
            wmsg = '\tData along slice. Start={0} End={1}'
            wargs = [start_good_ccor, end_good_ccor]
            WLOG(params, '', wmsg.format(*wargs))

            # -------------------------------------------------------------
            # for all field positions along the order, we determine the
            #    dx+rotation values and update the master DX map
            fracs = ypix[order_num] - np.fix(ypix[order_num])
            widths = np.arange(width)

            for ix in range(dim2):
                # get slope
                slope = slope_all_ord[order_num, ix]
                # get dx0 with slope factor added
                dx0 = (widths - width // 2 + (1 - fracs[ix])) * slope
                # get the ypix at this value
                widthrange = np.arange(-width//2, width//2)
                ypix2 = int(ypix[order_num, ix]) + widthrange
                # get the ddx
                ddx = spline(widths - fracs[ix])
                # set the zero shifts to NaNs
                ddx[ddx == 0] = np.nan
                # only set positive ypixels
                pos_y_mask = (ypix2 >= 0) & good_ccor_mask
                # do not want overlap between orders and a gap of 1 pixel
                ypix0 = ypix[order_num, ix]
                # identify the upper bound of order
                if order_num != (nbo-1):
                    ypixa = ypix[order_num + 1, ix]
                    upper_ylimit_overlap = ypix0 + 0.5 * (ypixa - ypix0) - 1
                else:
                    upper_ylimit_overlap = dim1 - 1
                # identify the lower bound of order
                if order_num !=0:
                    ypixb = ypix[order_num - 1, ix]
                    lower_ylimit_overlap = ypix0 - 0.5 * (ypix0 - ypixb) + 1
                else:
                    lower_ylimit_overlap = 0
                # add these constraints to the position mask
                pos_y_mask &= (ypix2 > lower_ylimit_overlap)
                pos_y_mask &= (ypix2 < upper_ylimit_overlap)
                # if we have some values add to master DX map
                if np.sum(pos_y_mask) != 0:
                    # get positions in y
                    positions = ypix2[pos_y_mask]

                    # for first iteration
                    if banana_num == 0:
                        # get good positions
                        good_pos = map_orders[positions, ix] != -1
                        # get order overlap from last order
                        order_overlap[positions, ix] += good_pos
                        # update map_orders
                        map_orders[positions, ix] = order_num

                    # get shifts combination of ddx and dx0 correction
                    ddx_f = ddx + dx0
                    shifts = ddx_f[pos_y_mask] - corr_dx_from_fp[order_num][ix]
                    # apply shifts to master dx map at correct positions
                    master_dxmap[positions, ix] += shifts

                    # after each iteration updating the dxmap, we verify
                    # that the per-order and per-x-pixel shift is not larger
                    # than the maximum seen over 'normal' images.
                    dxmap_std = np.nanstd(master_dxmap[positions, ix])

                    dxmap_stds.append(dxmap_std)

                    # return here if QC not met
                    if dxmap_std > std_qc:
                        # add DXMAP to loc
                        loc['DXMAP'] = None
                        loc['MAXDXMAPSTD'] = dxmap_std
                        loc['MAXDXMAPINFO'] = [order_num, ix]
                        keys = ['DXMAP', 'MAXDXMAPSTD', 'MAXDXMAPINFO']
                        loc.set_sources(keys, func_name)
                        return loc

            # -----------------------------------------------------------------
            if params['DRS_PLOT'] and (params['DRS_DEBUG'] >= 2) and plot_on:
                # TODO: Do plots
                pass
                # # plot angle and offset plot for each order
                # sPlt.plt.ioff()
                # sPlt.slit_shape_angle_plot(p, loc2s[order_num], bnum=banana_num,
                #                            order=order_num)
                # sPlt.slit_shape_offset_plot(p, loc, bnum=banana_num,
                #                             order=order_num)
                # sPlt.plt.show()
                # sPlt.plt.close()
                # sPlt.plt.ion()
        # ---------------------------------------------------------------------
        # append to storage
        slope_deg_arr.append(slope_deg_arr_i), slope_arr.append(slope_arr_i)
        skeep_arr.append(skeep_arr_i), xsec_arr.append(xsec_arr_i)
        ccor_arr.append(ccor_arr_i), ddx_arr.append(ddx_arr_i)
        dx_arr.append(dx_arr_i), dypix_arr.append(dypix_arr_i)
        cckeep_arr.append(cckeep_arr_i)

    # setting to 0 pixels that are NaNs
    nanmask = ~np.isfinite(master_dxmap)
    master_dxmap[nanmask] = 0.0

    # distortions where there is some overlap between orders will be wrong
    master_dxmap[order_overlap != 0] = 0.0

    return master_dxmap


# =============================================================================
# Define worker functions
# =============================================================================
def _max_neighbour_mask(image, percent, thres):
    # construct a cube with 8 slices that contain the 8 neighbours
    #   of any pixel. This is used to find pixels brighter that their
    #   neighbours
    box = np.zeros([9, image.shape[0], image.shape[1]], dtype=float)
    xpos, ypos = np.indices([3, 3]) - 1
    # loop around
    for it in range(len(xpos.flatten())):
        dx, dy = xpos.flatten()[it], ypos.flatten()[it]
        if (dx == 0) and (dy == 0):
            box[it] = np.nan
        else:
            box[it] = np.roll(np.roll(image, dx, axis=0), dy, axis=1)
    # maximum value of neighbouring pixels
    with warnings.catch_warnings(record=True) as _:
        max_neighbours = np.nanmax(box, axis=0)

    # find pixels brighter than neighbours and brighter than 80th percentile
    # of image. These are the peaks of FP lines
    # we also impose that the pixel be within 1.5x of its neighbours
    # to filter-out noise excursions
    with warnings.catch_warnings(record=True) as _:
        mask = (image > max_neighbours)
        mask &= (image > np.nanpercentile(image, percent))
        mask &= (image / max_neighbours < thres)
    # return mask of where peaks are
    return mask


def _xy_acc_peak(xpeak, ypeak, im):
    # black magic arithmetic for replace a 2nd order polynomial by
    # some arithmetic directly on pixel values to find
    # the maxima in x and y for each peak

    # vectors to contain peak pixels and its neighbours in x or y for
    # im1 and im2
    vvy = np.zeros([3, len(ypeak)])
    vvx = np.zeros([3, len(ypeak)])

    # pad values of neighbours in vv[xy][12]
    for i in range(-1, 2):
        vvy[i + 1, :] = im[ypeak + i, xpeak]
        vvx[i + 1, :] = im[ypeak, xpeak + i]

    # subtract peak pixel value
    vvx[0, :] -= vvx[1, :]
    vvx[2, :] -= vvx[1, :]

    # find the slope of the linear fix
    mx = (vvx[2, :] - vvx[0, :]) / 2

    # find the 2nd order of the polynomial
    ax = vvx[2, :] - mx

    # all the same in y direction for im
    vvy[0, :] -= vvy[1, :]
    vvy[2, :] -= vvy[1, :]

    my = (vvy[2, :] - vvy[0, :]) / 2
    ay = vvy[2, :] - my

    # peaks position is point of zero derivative. We add the integer
    # pixel value of [xy]peak[12]
    x1 = -0.5 * mx / ax + xpeak
    y1 = -0.5 * my / ay + ypeak

    return x1,y1


def _get_offset_sp(params, loc, sp_fp, sp_hc, order_num, **kwargs):

    func_name = __NAME__ + '._get_offset_sp'
    # get constants from params/kwargs
    xoffset = pcheck(params, 'SHAPEOFFSET_XOFFSET', 'xoffset', kwargs, func_name)
    bottom_fp_percentile = pcheck(params, 'SHAPEOFFSET_BOTTOM_PERCENTILE',
                                  'bottom_fp_percentile', kwargs, func_name)
    top_fp_percentile = pcheck(params, 'SHAPEOFFSET_TOP_PERCENTILE',
                               'top_fp_percentile', kwargs, func_name)
    top_floor_frac = pcheck(params, 'SHAPEOFFSET_TOP_FLOOR_FRAC',
                            'top_floor_frac', kwargs, func_name)
    med_filter_wid = pcheck(params, 'SHAPEOFFSET_MED_FILTER_WIDTH',
                            'med_filter_wid', kwargs, func_name)
    fpindexmax = pcheck(params, 'SHAPEOFFSET_FPINDEX_MAX', 'fpindexmax',
                        kwargs, func_name)
    valid_fp_length = pcheck(params, 'SHAPEOFFSET_VALID_FP_LENGTH',
                             'valid_fp_length', kwargs, func_name)
    drift_margin = pcheck(params, 'SHAPEOFFSET_DRIFT_MARGIN',
                          'drift_margin', kwargs, func_name)
    inv_iterations = pcheck(params, 'SHAPEOFFSET_WAVEFP_INV_IT',
                            'inv_iterations', kwargs, func_name)
    mask_border = pcheck(params, 'SHAPEOFFSET_MASK_BORDER', 'mask_border',
                         kwargs, func_name)
    minimum_maxpeak_frac = pcheck(params, 'SHAPEOFFSET_MIN_MAXPEAK_FRAC',
                                  'minimum_maxpeak_frac', kwargs, func_name)
    mask_pixwidth = pcheck(params, 'SHAPEOFFSET_MASK_PIXWIDTH',
                           'mask_pixwidth', kwargs, func_name)
    mask_extwidth = pcheck(params, 'SHAPEOFFSET_MASK_EXTWIDTH',
                           'mask_extwidth', kwargs, func_name)
    dpmin = pcheck(params, 'SHAPEOFFSET_DEVIANT_PMIN', 'dpmin',
                   kwargs, func_name)
    dpmax = pcheck(params, 'SHAPEOFFSET_DEVIANT_PMAX', 'dpmax',
                   kwargs, func_name)
    deviant_percentiles = [dpmin, dpmax]
    fp_max_num_error = pcheck(params, 'SHAPEOFFSET_FPMAX_NUM_ERROR',
                              'fp_max_num_error', kwargs, func_name)
    fit_hc_sigma = pcheck(params, 'SHAPEOFFSET_FIT_HC_SIGMA',
                          'fit_hc_sigma', kwargs, func_name)
    maxdev_threshold = pcheck(params, 'SHAPEOFFSET_MAXDEV_THRESHOLD',
                              'maxdev_threshold', kwargs, func_name)
    absdev_threshold = pcheck(params, 'SHAPEOFFSET_ABSDEV_THRESHOLD',
                              'absdev_threshold', kwargs, func_name)

    # -------------------------------------------------------------------------
    # get data from loc
    dim1, dim2 = np.shape(loc['HCDATA1'])
    poly_wave_ref = loc['MASTERWAVEP']
    une_lines = loc['LL_LINE']
    poly_cavity = loc['CAVITY_LEN_COEFFS']
    # -------------------------------------------------------------------------
    # define storage for the bottom and top values of the FPs
    bottom = np.zeros_like(sp_fp)
    top = np.zeros_like(sp_fp)
    # -------------------------------------------------------------------------
    # loop around pixels
    for xpix in range(dim2):
        # put the start a certain number of pixels behind
        start = xpix - xoffset
        end = xpix + xoffset
        # deal with boundaries
        if start < 0:
            start = 0
        if end > (dim2 - 1):
            end = dim2 - 1
        # define a segment between start and end
        segment = sp_fp[start:end]
        # push values into bottom and top
        bottom[xpix] = np.nanpercentile(segment, bottom_fp_percentile)
        top[xpix] = np.nanpercentile(segment, top_fp_percentile)
    # -------------------------------------------------------------------------
    # put a floor in the top values
    top_floor_value = top_floor_frac * np.max(top)
    top_mask = top <= top_floor_value
    top[top_mask] = top_floor_value
    # -------------------------------------------------------------------------
    # subtract off the bottom from the FP's of this order
    sp_fp = sp_fp - bottom
    # normalise by the difference between top and bottom
    sp_fp = sp_fp / (top - bottom)
    # set NaN's to zero
    sp_fp[~np.isfinite(sp_fp)] = 0.0
    # -------------------------------------------------------------------------
    # The HC spectrum is high-passed. We are just interested to know if
    # a given expected line from the catalog falls at the position of a
    # >3-sigma peak relative to the continuum
    sp_hc = sp_hc - math.medfilt(sp_hc, med_filter_wid)
    # normalise HC to its absolute deviation
    norm = np.nanmedian(np.abs(sp_hc[sp_hc != 0]))
    sp_hc = sp_hc / norm
    # -------------------------------------------------------------------------
    # fpindex is a variable that contains the index of the FP peak interference
    # this is expected to range from ~10000 to ~25000
    fpindex = np.arange(fpindexmax) + 1
    # -------------------------------------------------------------------------
    # We find the exact wavelength of each FP peak in fpindex
    # considering the cavity length

    # The cavity length is very slightly wavelength dependent (hence the
    # polynomial read earlier). First we find the length in the middle of the
    # expected wavelength domain from the reference file

    # just to cut the number of peaks so that they are
    # all contained within the relevant domain
    xdomain = np.linspace(0, dim2, 3).astype(int)
    wave_start_med_end = np.polyval(poly_wave_ref[order_num][::-1], xdomain)
    # get the wavelengths for the fp
    wave_fp = np.polyval(poly_cavity, wave_start_med_end[1]) * 2/fpindex
    # -------------------------------------------------------------------------
    # we give a 20 nm marging on either side... who knows, maybe SPIRou
    #    has drifted
    good = (wave_fp > wave_start_med_end[0] - drift_margin)
    good &= (wave_fp < wave_start_med_end[2] + drift_margin)
    # keep only the relevant FPs in this good region
    fpindex = fpindex[good]
    wave_fp = wave_fp[good]
    # -------------------------------------------------------------------------
    # a numerical trick so that we don't have to invert the poly_cavity
    #    polynomial wave_fp depends on the cavity length, which in turns
    #    depends (very slightly) on wave_fp again. This iteration
    #    fixes the problem
    for iteration in range(inv_iterations):
        wave_fp = np.polyval(poly_cavity, wave_fp) * 2 / fpindex
    # -------------------------------------------------------------------------
    # get the pixel position along the spectrum
    xpixs = np.arange(len(sp_fp))
    # storage to be appended to
    # x position of the FP peak, peak value. Could be used for quality check,
    #    e-width of the line. Could be used for quality check
    xpeak, peakval, ewval = [], [], []
    # peak value of the FP spectrum
    maxfp = np.max(sp_fp)
    # current maximum value after masking
    max_it = float(maxfp)
    # mask
    mask = np.ones_like(sp_fp).astype(int)
    # deal with borders
    mask[:mask_border] = 0
    mask[-mask_border:] = 0

    # looping while FP peaks are at least "minimum_maxpeak_frac" * 100% of
    #     the max peak value
    while max_it > (maxfp * minimum_maxpeak_frac):
        # get the position of the maximum peak
        pos = np.argmax(sp_fp * mask)
        # get the current maximum value
        max_it = sp_fp[pos]
        # set this peak to False in the mask
        fpstart, fpend = pos - mask_pixwidth, pos + mask_pixwidth + 1
        mask[fpstart:fpend] = 0
        # set the width
        extstart, extend = pos - mask_extwidth, pos + mask_extwidth + 1
        # extract a window in the spectrum
        yy = sp_fp[extstart:extend]
        xx = xpixs[extstart:extend]
        # find the domain between the minima before and the minima after the
        #   peak value
        mask1 = np.ones_like(yy).astype(int)
        mask1[:mask_extwidth] = 0
        mask2 = np.ones_like(yy).astype(int)
        mask2[mask_extwidth:] = 0
        # find the minima of the fp's in this mask
        y0 = np.argmin(yy/np.max(yy) + mask1)
        y1 = np.argmin(yy/np.max(yy) + mask2)
        # re-set xx and yy
        xx = np.array(xx[y0:y1 + 1]).astype(float)
        yy = np.array(yy[y0:y1 + 1]).astype(float)

        # the FP must be at least 5 pixels long to be valid
        if len(xx) > valid_fp_length:
            # set up the guess: amp, x0, w, zp
            guess = [np.max(yy) - np.min(yy),  xx[np.argmax(yy)],
                     1, np.min(yy), 0]
            # try to fit a gaussian
            try:
                coeffs, _ = curve_fit(math.gauss_fit_s, xx, yy, p0=guess)
                goodfit = True
            except Exception as _:
                goodfit, coeffs = False, None
            # if we had a fit then update some values
            if goodfit:
                xpeak.append(coeffs[1])
                peakval.append(coeffs[0])
                ewval.append(coeffs[2])

    # -------------------------------------------------------------------------
    # sort FP peaks by their x pixel position
    indices = np.argsort(xpeak)
    # apply sort to vectors
    xpeak2 = np.array(xpeak)[indices]
    peakval2 = np.array(peakval)[indices]
    ewval2 = np.array(ewval)[indices]
    # we  "count" the FP peaks and determine their number in the
    #   FP interference
    # determine distance between consecutive peaks
    xpeak2_mean = (xpeak2[1:] + xpeak2[:-1]) / 2
    dxpeak = xpeak2[1:] - xpeak2[:-1]
    # we clip the most deviant peaks
    lowermask = dxpeak > np.nanpercentile(dxpeak, deviant_percentiles[0])
    uppermask = dxpeak < np.nanpercentile(dxpeak, deviant_percentiles[1])
    good = lowermask & uppermask
    # apply good mask and fit the peak separation
    fit_peak_separation = math.nanpolyfit(xpeak2_mean[good], dxpeak[good], 2)
    # Looping through peaks and counting the number of meddx between peaks
    #    we know that peaks will be at integer multiple or medds (in the
    #    overwhelming majority, they will be at 1 x meddx)
    ipeak = np.zeros(len(xpeak2), dtype=int)
    # loop around the xpeaks
    for it in range(1, len(xpeak2)):
        # get the distance between peaks
        dx = xpeak2[it] - xpeak2[it - 1]
        # get the estimate from the fit peak separation
        dx_est = np.polyval(fit_peak_separation, xpeak2[it])
        # find the integer number of the peak
        ipeak[it] = ipeak[it - 1] + np.round(dx / dx_est)
        # if we have a unexpected deviation log it
        if np.round(dx/dx_est) != 1:
            wmsg = '\t\tdx = {0:.5f} dx/dx_est = {1:.5f} estimate = {2:.5f}'
            wargs = [dx, dx/dx_est, dx_est]
            WLOG(params, '', wmsg.format(*wargs))
    # -------------------------------------------------------------------------
    # Trusting the wavelength solution this is the wavelength of FP peaks
    wave_from_hdr = np.polyval(poly_wave_ref[order_num][::-1], xpeak2)
    # We estimate the FP order of the first FP peak. This integer value
    # should be good to within a few units
    fit0 = np.polyval(poly_cavity, wave_from_hdr[0])
    fp_peak0_est = int(fit0 * 2 / wave_from_hdr[0])
    # we scan "zp", which is the FP order of the first FP peak that we've
    #    found we assume that the error in FP order assignment could range
    #    from -50 to +50 in practice, it is -1, 0 or +1 for the cases we've
    #    tested to date
    best_zp = int(fp_peak0_est)
    max_good = 0
    # loop around estimates
    fpstart = fp_peak0_est - fpindex[0] - fp_max_num_error
    fpend = fp_peak0_est - fpindex[0] + fp_max_num_error
    # loop from fpstart to fpend
    for zp in range(fpstart, fpend):
        # we take a trial solution between wave (from the theoretical FP
        #    solution) and the x position of measured peaks
        fitzp = math.nanpolyfit(wave_fp[zp - ipeak], xpeak2, 3)
        # we predict an x position for the known U Ne lines
        xpos_predict = np.polyval(fitzp, une_lines)
        # deal with borders
        good = (xpos_predict > 0) & (xpos_predict < dim2)
        xpos_predict = xpos_predict[good]
        # we check how many of these lines indeed fall on > "fit_hc_sigma"
        #    sigma excursion of the HC spectrum
        xpos_predict_int = np.zeros(len(xpos_predict), dtype=int)
        for it in range(len(xpos_predict_int)):
            xpos_predict_int[it] = xpos_predict[it]
        # the FP order number that produces the most HC matches
        #   is taken to be the right wavelength solution
        frac_good = np.mean(sp_hc[xpos_predict_int] > fit_hc_sigma)
        # update the best values if better than last iteration
        if frac_good > max_good:
            max_good, best_zp = frac_good, zp
    # -------------------------------------------------------------------------
    # log the predicted vs measured FP peak
    wmsg = '\tPredicted FP peak #: {0}   Measured FP peak #: {1}'
    wargs = [fp_peak0_est, fpindex[best_zp]]
    WLOG(params, '', wmsg.format(*wargs))
    # -------------------------------------------------------------------------
    # we find teh actual wavelength of our IDed peaks
    wave_xpeak2 = wave_fp[best_zp - ipeak]
    # get the derivative of the polynomial
    poly = poly_wave_ref[order_num]
    deriv_poly = np.polyder(poly[::-1], 1)[::-1]
    # we find the corresponding offset
    err_wave = wave_xpeak2 - np.polyval(poly[::-1], xpeak2)
    err_pix = err_wave / np.polyval(deriv_poly[::-1], xpeak2)
    # -------------------------------------------------------------------------
    # first we perform a thresholding with a 1st order polynomial
    maxabsdev = np.inf
    good = np.isfinite(err_pix)
    # loop around until we are better than threshold
    while maxabsdev > maxdev_threshold:
        # get the error fit (1st order polynomial)
        fit_err_xpix = math.nanpolyfit(xpeak2[good], err_pix[good], 1)
        # get the deviation from error fit
        dev = err_pix - np.polyval(fit_err_xpix, xpeak2)
        # get the median absolute deviation
        absdev = np.nanmedian(np.abs(dev))
        # very low thresholding values tend to clip valid points
        if absdev < absdev_threshold:
            absdev = absdev_threshold
        # get the max median asbolute deviation
        maxabsdev = np.nanmax(np.abs(dev[good]/absdev))
        # iterate the good mask
        good &= np.abs(dev / absdev) < maxdev_threshold
    # -------------------------------------------------------------------------
    # then we perform a thresholding with a 5th order polynomial
    maxabsdev = np.inf
    # loop around until we are better than threshold
    while maxabsdev > maxdev_threshold:
        # get the error fit (1st order polynomial)
        fit_err_xpix = math.nanpolyfit(xpeak2[good], err_pix[good], 5)
        # get the deviation from error fit
        dev = err_pix - np.polyval(fit_err_xpix, xpeak2)
        # get the median absolute deviation
        absdev = np.nanmedian(np.abs(dev))
        # very low thresholding values tend to clip valid points
        if absdev < absdev_threshold:
            absdev = absdev_threshold
        # get the max median asbolute deviation
        maxabsdev = np.nanmax(np.abs(dev[good]/absdev))
        # iterate the good mask
        good &= np.abs(dev/absdev)  < maxdev_threshold
    # -------------------------------------------------------------------------
    # this relation is the (sigma-clipped) fit between the xpix error
    #    and xpix along the order. The corresponding correction vector will
    #    be sent back to the dx grid
    corr_err_xpix = np.polyval(fit_err_xpix, np.arange(dim2))
    # -------------------------------------------------------------------------
    # get the statistics
    std_dev = np.std(dev)
    errpix_med = np.nanmedian(err_pix)
    std_corr = np.std(corr_err_xpix[xpos_predict_int])
    corr_med = np.nanmedian(corr_err_xpix[xpos_predict_int])
    cent_fit = math.nanpolyfit(xpeak2[good], fpindex[zp - ipeak[good]], 5)
    num_fp_cent = np.polyval(cent_fit, dim2//2)
    # log the statistics
    wargs = [std_dev, absdev, errpix_med, std_corr, corr_med, num_fp_cent]
    wmsg1 = '\t\tstddev pixel error relative to fit: {0:.5f} pix'.format(*wargs)
    wmsg2 = '\t\tabsdev pixel error relative to fit: {1:.5f} pix'.format(*wargs)
    wmsg3 = ('\t\tmedian pixel error relative to zero: {2:.5f} '
             'pix'.format(*wargs))
    wmsg4 = '\t\tstddev applied correction: {3:.5f} pix'.format(*wargs)
    wmsg5 = '\t\tmed applied correction: {4:.5f} pix'.format(*wargs)
    wmsg6 = '\t\tNth FP peak at center of order: {5:.5f}'.format(*wargs)
    WLOG(params, '', [wmsg1, wmsg2, wmsg3, wmsg4, wmsg5, wmsg6])
    # -------------------------------------------------------------------------
    # save to loc
    loc['CORR_DX_FROM_FP'][order_num] = corr_err_xpix
    loc['XPEAK2'][order_num] = xpeak2
    loc['PEAKVAL2'][order_num] = peakval2
    loc['EWVAL2'][order_num] = ewval2
    loc['ERR_PIX'][order_num] = err_pix
    loc['GOOD_MASK'][order_num] = good
    # -------------------------------------------------------------------------
    # return loc
    return loc



# =============================================================================
# End of code
# =============================================================================

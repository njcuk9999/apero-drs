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
from scipy.ndimage import map_coordinates as mapc
import warnings
import os

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
            for filename in fp_ids:
                transforms_list.append(transforms)
        else:
            WLOG(params, '', TextEntry('', args=[g_it + 1, min_num]))
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


def calculate_dxmap(params, ):



    return dxmap


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


# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-27 at 10:13

@author: cook
"""
import numpy as np
import os
from scipy.ndimage import filters
from scipy.ndimage import map_coordinates as mapc
from scipy.optimize import curve_fit
from scipy.signal import convolve2d
from scipy.stats import stats
import warnings

from apero.base import base
from apero.core import constants
from apero import lang
from apero.core import math as mp
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_data
from apero.core.core import drs_database
from apero.io import drs_path
from apero.io import drs_fits
from apero.io import drs_image
from apero.io import drs_table
from apero.science.calib import gen_calib
from apero.science.calib import localisation


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.shape.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define user functions
# =============================================================================
def construct_fp_table(params, filenames):
    # define storage for table columns
    fp_time, fp_exp, fp_pp_version = [], [], []
    basenames, obs_dirs = [], []
    valid_files = []
    # log that we are reading all dark files
    WLOG(params, '', textentry('40-014-00003'))
    # loop through file headers
    for it in range(len(filenames)):
        # get the basename from filenames
        basename = os.path.basename(filenames[it])
        # get the path inst
        path_inst = drs_file.DrsPath(params, abspath=filenames[it])
        # get the observation directory
        obs_dir = path_inst.obs_dir
        # read the header
        hdr = drs_fits.read_header(params, filenames[it])
        # must load file here to check if fp is valid
        image = drs_fits.readfits(params, filenames[it], log=False)
        # if image is not valid skip
        if not gen_calib.check_fp(params, image, filename=filenames[it]):
            continue
        # delete image we'll get it again later in more memory efficient manner
        del image
        # get keys from hdr
        acqtime, acqmethod = drs_file.get_mid_obs_time(params, hdr,
                                                       out_fmt='mjd')
        exptime = hdr[params['KW_EXPTIME'][0]]
        ppversion = hdr[params['KW_PPVERSION'][0]]
        # append to lists
        valid_files.append(filenames[it])
        fp_time.append(float(acqtime))
        fp_exp.append(float(exptime))
        fp_pp_version.append(ppversion)
        basenames.append(basename)
        obs_dirs.append(obs_dir)
    # convert lists to table
    columns = ['OBS_DIR', 'BASENAME', 'FILENAME', 'MJDATE', 'EXPTIME',
               'PPVERSION']
    values = [obs_dirs, basenames, valid_files, fp_time, fp_exp,
              fp_pp_version]
    # make table using columns and values
    fp_table = drs_table.make_table(params, columns, values)
    # return table
    return fp_table


# def construct_master_fp(params, recipe, dprtype, fp_table, image_ref, **kwargs):
#     func_name = __NAME__ + '.construct_master_dark'
#     # get constants from params/kwargs
#     time_thres = pcheck(params, 'FP_MASTER_MATCH_TIME', 'time_thres', kwargs,
#                         func_name)
#     percent_thres = pcheck(params, 'FP_MASTER_PERCENT_THRES', 'percent_thres',
#                            kwargs, func_name)
#     qc_res = pcheck(params, 'SHAPE_QC_LTRANS_RES_THRES', 'qc_res', kwargs,
#                     func_name)
#     min_num = pcheck(params, 'SHAPE_FP_MASTER_MIN_IN_GROUP', 'min_num', kwargs,
#                      func_name)
#
#     # get col data from dark_table
#     filenames = fp_table['FILENAME']
#     fp_times = fp_table['MJDATE']
#
#     # ----------------------------------------------------------------------
#     # match files by date
#     # ----------------------------------------------------------------------
#     # log progress
#     WLOG(params, '', textentry('40-014-00004', args=[time_thres]))
#     # match files by time
#     matched_id = drs_path.group_files_by_time(params, fp_times, time_thres)
#
#     # ----------------------------------------------------------------------
#     # Read individual files and sum groups
#     # ----------------------------------------------------------------------
#     # log process
#     WLOG(params, '', textentry('40-014-00005'))
#     # Find all unique groups
#     u_groups = np.unique(matched_id)
#     # storage of dark cube
#     valid_dark_files, valid_badpfiles, valid_backfiles = [], [], []
#     fp_cube, transforms_list, valid_matched_id = [], [], []
#     table_mask = np.zeros(len(fp_table), dtype=bool)
#     # loop through groups
#     for g_it, group_num in enumerate(u_groups):
#         # log progress
#         wargs = [g_it + 1, len(u_groups)]
#         WLOG(params, 'info', textentry('40-014-00006', args=wargs))
#         # find all files for this group
#         fp_ids = filenames[matched_id == group_num]
#         indices = np.arange(len(filenames))[matched_id == group_num]
#         # only combine if 3 or more images were taken
#         if len(fp_ids) >= min_num:
#             # load this groups files into a cube
#             cube = []
#             # get infile from filetype
#             file_inst = core.get_file_definition(dprtype, params['INSTRUMENT'],
#                                                  kind='tmp')
#             # get this groups storage
#             vheaders = []
#             # loop around fp ids
#             for f_it, filename in enumerate(fp_ids):
#                 # log reading of data
#                 wargs = [os.path.basename(filename), f_it + 1, len(fp_ids)]
#                 WLOG(params, 'info', textentry('40-014-00007', args=wargs))
#                 # construct new infile instance
#                 fpfile_it = file_inst.newcopy(filename=filename, recipe=recipe)
#                 fpfile_it.read_file()
#                 # append to cube
#                 cube.append(np.array(fpfile_it.data))
#                 vheaders.append(drs_fits.Header(fpfile_it.header))
#                 # delete fits data
#                 del fpfile_it
#             # convert to numpy array
#             cube = np.array(cube)
#             # log process
#             WLOG(params, '', textentry('40-014-00008', args=[len(fp_ids)]))
#             # median fp cube
#             with warnings.catch_warnings(record=True) as _:
#                 groupfp = mp.nanmedian(cube, axis=0)
#
#             # --------------------------------------------------------------
#             # calibrate group fp
#             # --------------------------------------------------------------
#             # construct new infile instance
#             groupfile = file_inst.newcopy(params=params)
#             groupfile.data = groupfp
#             groupfile.header = vheaders[0]
#             groupfile.filename = fp_ids[0]
#             groupfile.basename = os.path.basename(fp_ids[0])
#
#             # get and correct file
#             cargs = [params, recipe, groupfile]
#             ckwargs = dict(n_percentile=percent_thres,
#                            correctback=False)
#             props, groupfp = general.calibrate_ppfile(*cargs, **ckwargs)
#             # --------------------------------------------------------------
#             # shift group to master
#             targs = [image_ref, groupfp]
#             gout = get_linear_transform_params(params, recipe, *targs)
#             transforms, xres, yres = gout
#             # quality control on group
#             if transforms is None:
#                 # log that image quality too poor
#                 wargs = [g_it + 1]
#                 WLOG(params, 'warning', textentry('10-014-00001', args=wargs))
#                 # skip adding to group
#                 continue
#             if (xres > qc_res) or (yres > qc_res):
#                 # log that xres and yres too larger
#                 wargs = [xres, yres, qc_res]
#                 WLOG(params, 'warning', textentry('10-014-00002', args=wargs))
#                 # skip adding to group
#                 continue
#             # perform a final transform on the group
#             groupfp = ea_transform(params, groupfp,
#                                    lin_transform_vect=transforms)
#             # append to cube
#             fp_cube.append(groupfp)
#             # append transforms to list
#             for _ in fp_ids:
#                 transforms_list.append(transforms)
#                 # now add extract properties to main group
#                 valid_matched_id.append(group_num)
#                 valid_dark_files.append(props['DARKFILE'])
#                 valid_badpfiles.append(props['BADPFILE'])
#                 valid_backfiles.append(props['BACKFILE'])
#             # validate table mask
#             table_mask[indices] = True
#         else:
#             eargs = [g_it + 1, min_num]
#             WLOG(params, '', textentry('40-014-00015', args=eargs))
#     # ----------------------------------------------------------------------
#     # convert fp cube to array
#     fp_cube = np.array(fp_cube)
#     # convert transform_list to array
#     tarrary = np.array(transforms_list)
#     # cut down fp_table to valid
#     valid_fp_table = fp_table[table_mask]
#     # ----------------------------------------------------------------------
#     # add columns to fp_table
#     colnames = ['GROUPID', 'DARKFILE', 'BADPFILE', 'BACKFILE', 'DXREF',
#                 'DYREF', 'A', 'B', 'C', 'D']
#     values = [valid_matched_id, valid_dark_files, valid_badpfiles,
#               valid_backfiles, tarrary[:, 0], tarrary[:, 1],
#               tarrary[:, 2], tarrary[:, 3], tarrary[:, 4], tarrary[:, 5]]
#     for c_it, col in enumerate(colnames):
#         valid_fp_table[col] = values[c_it]
#     # ----------------------------------------------------------------------
#     # return fp_cube
#     return fp_cube, valid_fp_table


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
    # get temporary output dir
    out_obs_dir = params['INPUTS']['OBS_DIR']
    # get col data from dark_table
    filenames = fp_table['FILENAME']
    fp_times = fp_table['MJDATE']
    # ----------------------------------------------------------------------
    # match files by date
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', textentry('40-014-00004', args=[time_thres]))
    # match files by time
    matched_id = drs_path.group_files_by_time(params, fp_times, time_thres)
    # ----------------------------------------------------------------------
    # Read individual files and sum groups
    # ----------------------------------------------------------------------
    # log process
    WLOG(params, '', textentry('40-014-00005'))
    # Find all unique groups
    u_groups = np.unique(matched_id)
    # storage of dark cube
    valid_dark_files, valid_badpfiles, valid_backfiles = [], [], []
    fp_cube, transforms_list, valid_matched_id = [], [], []
    table_mask = np.zeros(len(fp_table), dtype=bool)
    fp_cube_files, fpsubdir = None, None
    # row counter
    row = 0
    # loop through groups
    for g_it, group_num in enumerate(u_groups):
        # log progress
        wargs = [g_it + 1, len(u_groups)]
        WLOG(params, 'info', textentry('40-014-00006', args=wargs))
        # find all files for this group
        fp_ids = filenames[matched_id == group_num]
        indices = np.arange(len(filenames))[matched_id == group_num]
        # only combine if 3 or more images were taken
        if len(fp_ids) >= min_num:
            # get infile from filetype
            file_inst = drs_file.get_file_definition(params, dprtype,
                                                     block_kind='tmp')
            # perform a large image median on FP files in this group
            groupfp = drs_image.large_image_combine(params, fp_ids,
                                                    math='median',
                                                    outdir=out_obs_dir,
                                                    fmt='fits')
            # -------------------------------------------------------------
            # get first file header
            # construct new infile instance
            fpfile0 = file_inst.newcopy(filename=fp_ids[0], params=params)
            fpfile0.read_header()
            # --------------------------------------------------------------
            # calibrate group fp
            # --------------------------------------------------------------
            # construct new infile instance
            groupfile = file_inst.newcopy(params=params)
            groupfile.data = groupfp
            groupfile.header = drs_fits.Header(fpfile0.get_header())
            groupfile.filename = fp_ids[0]
            groupfile.basename = os.path.basename(fp_ids[0])
            # get and correct file
            cargs = [params, recipe, groupfile]
            ckwargs = dict(n_percentile=percent_thres, correctback=False)
            props, groupfp = gen_calib.calibrate_ppfile(*cargs, **ckwargs)
            # --------------------------------------------------------------
            # shift group to master
            targs = [image_ref, groupfp]
            gout = get_linear_transform_params(params, recipe, *targs)
            transforms, xres, yres = gout
            # quality control on group
            if transforms is None:
                # log that image quality too poor
                wargs = [g_it + 1]
                WLOG(params, 'warning', textentry('10-014-00001', args=wargs))
                # skip adding to group
                continue
            if (xres > qc_res) or (yres > qc_res):
                # log that xres and yres too larger
                wargs = [xres, yres, qc_res]
                WLOG(params, 'warning', textentry('10-014-00002', args=wargs))
                # skip adding to group
                continue
            # perform a final transform on the group
            groupfp = ea_transform(params, groupfp,
                                   lin_transform_vect=transforms)
            # save files for medianing later
            nargs = ['fp_master_cube', row, groupfp, fp_cube_files, fpsubdir,
                     out_obs_dir]
            fp_cube_files, fpsubdir = drs_image.npy_filelist(params, *nargs)
            # delete groupfp
            del groupfp
            # add to row
            row += 1
            # append transforms to list
            for _ in fp_ids:
                transforms_list.append(transforms)
                # now add extract properties to main group
                valid_matched_id.append(group_num)
                valid_dark_files.append(str(props['DARKFILE']))
                valid_badpfiles.append(str(props['BADPFILE']))
                valid_backfiles.append(str(props['BACKFILE']))
            # validate table mask
            table_mask[indices] = True
        else:
            eargs = [g_it + 1, min_num]
            WLOG(params, '', textentry('40-014-00015', args=eargs))
    # ----------------------------------------------------------------------
    # produce the large median (write ribbons to disk to save space)
    with warnings.catch_warnings(record=True) as _:
        fp_master = drs_image.large_image_combine(params, fp_cube_files,
                                                  math='mean',
                                                  outdir=out_obs_dir, fmt='npy')
    # clean up npy dir
    drs_image.npy_fileclean(params, fp_cube_files, fpsubdir, out_obs_dir)
    # ----------------------------------------------------------------------
    # convert transform_list to array
    tarrary = np.array(transforms_list)
    # cut down fp_table to valid
    valid_fp_table = fp_table[table_mask]
    # ----------------------------------------------------------------------
    # add columns to fp_table
    colnames = ['GROUPID', 'DARKFILE', 'BADPFILE', 'BACKFILE', 'DXREF',
                'DYREF', 'A', 'B', 'C', 'D']
    values = [valid_matched_id, valid_dark_files, valid_badpfiles,
              valid_backfiles, tarrary[:, 0], tarrary[:, 1],
              tarrary[:, 2], tarrary[:, 3], tarrary[:, 4], tarrary[:, 5]]
    for c_it, col in enumerate(colnames):
        valid_fp_table[col] = values[c_it]
    # ----------------------------------------------------------------------
    # return fp_master
    return fp_master, valid_fp_table


def get_linear_transform_params(params, recipe, image1, image2, **kwargs):
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
        WLOG(params, 'error', textentry('00-014-00001', args=eargs))
    # linear transform vector
    # with dx0,dy0,A,B,C,D
    # we start assuming that there is no shift in x or y
    # and that the image is not sheared or rotated
    lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    # find the fp peaks (via max neighbours) in image1
    mask1 = max_neighbour_mask(image1, maxn_percent, maxn_thres)
    # copy image2
    image3 = np.array(image2)
    # print out initial conditions of linear transform vector
    WLOG(params, 'info', textentry('40-014-00009'))
    # set up arguments
    ltv = np.array(lin_transform_vect)
    wargs1 = [dim2, (ltv[2] - 1) * dim2, ltv[3] * dim2]
    wargs2 = [dim2, ltv[4] * dim2, (ltv[5] - 1) * dim2]
    # add to output
    wmsg = textentry('')
    wmsg += '\tdx={0:.6f} dy={1:.6f}'.format(*ltv)
    wmsg += '\n\t{0}(A-1)={1:.6f}\t{0}B={2:.6f}'.format(*wargs1)
    wmsg += '\n\t{0}C={1:.6f}\t{0}(D-1)={2:.6f}'.format(*wargs2)
    WLOG(params, '', wmsg)
    # outputs
    xres, yres = np.nan, np.nan
    x1, x2, y1, y2 = None, None, None, None
    # loop around iterations
    for n_it in range(niterations):
        # log progress
        wargs = [n_it + 1, niterations]
        WLOG(params, '', textentry('40-014-00010', args=wargs))
        # transform image2 if we have some transforms (initial we don't)
        if n_it > 0:
            image3 = ea_transform(params, image2, lin_transform_vect)
        # find the fp peaks (via max neighbours) in image2
        mask2 = max_neighbour_mask(image3, maxn_percent, maxn_thres)
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
        mask1[-wdd - 1:, :] = False
        mask1[:, -wdd - 1:] = False
        # get the positions of the x and y peaks (based on mask1)
        ypeak1, xpeak1 = np.where(mask1)
        # fill map_dxdy with the mean of the wdd box
        for y_it in range(len(dd)):
            for x_it in range(len(dd)):
                # get the boolean values for mask 2 for this dd
                boxvalues = mask2[ypeak1 + dd[y_it], xpeak1 + dd[x_it]]
                # push these values into the map
                map_dxdy[y_it, x_it] = np.mean(boxvalues)
        # To determine the  accurate shift between a nightly FP and the master
        # FP, we first find the round pixel offset. To do so, we put the master
        # FP peaks on a binary mask of the night's FP peaks and count the
        # number of matches for a range of offsets. Normally, the best match
        # is the shift with the largest fraction of FP peaks falling at peak
        # positions on the mask. As the slicer has 4 peaks, you get
        # 'outriggers' in that correlation map where ~75% of peaks are matched,
        # meaning that you are off by 1 slice width (slice 1-2-3 in on image
        # are matched to slices 2-3-4 in the other). Normally this works
        # nicely, but we had a problem when the detector moved by nearly 0.5
        # pixel. We ended with 50%/50% of good matches for two different
        # pixels corresponding to the correct offset and 75% corresponding
        # to the offset by 1 slice.
        # To fix if, we now 'smooth' the correlation map, so that two pixels
        # at 0.5 count more than a single pixel at 0.75
        map_kernel = [[0.5, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 0.5]]
        map_dxdy = convolve2d(map_dxdy, map_kernel, mode='same')
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
        x1, y1 = xy_acc_peak(xpeak1, ypeak1, image1)
        x2, y2 = xy_acc_peak(xpeak2, ypeak2, image3)
        # we loop on the linear model converting x1 y1 to x2 y2
        nbad, ampsx, ampsy = 1, np.zeros(3), np.zeros(3)

        n_terms = len(x1)
        xrecon, yrecon = None, None

        while nbad != 0:
            # define vectory
            vvv = np.zeros([3, len(x1)])
            vvv[0, :], vvv[1, :], vvv[2, :] = np.ones_like(x1), x1, y1
            # linear minimisation of difference w.r.t. v
            ampsx, xrecon = mp.linear_minimization(x1 - x2, vvv)
            ampsy, yrecon = mp.linear_minimization(y1 - y2, vvv)
            # express distance of all residual error in x1-y1 and y1-y2
            # in absolute deviation
            xnanmed = mp.nanmedian(np.abs((x1 - x2) - xrecon))
            ynanmed = mp.nanmedian(np.abs((y1 - y2) - yrecon))
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

        xres = mp.nanstd((x1 - x2) - xrecon)
        yres = mp.nanstd((y1 - y2) - yrecon)

        # we have our linear transform terms!
        dx0, dy0 = ampsx[0], ampsy[0]
        d_transform = [dx0, dy0, ampsx[1], ampsx[2], ampsy[1], ampsy[2]]
        # propagate to linear transform vector
        lin_transform_vect -= d_transform

        # print out per iteration values
        # set up arguments
        ltv = np.array(lin_transform_vect)
        wargs1 = [dim2, (ltv[2] - 1) * dim2, ltv[3] * dim2]
        wargs2 = [dim2, ltv[3] * dim2, (ltv[5] - 1) * dim2]
        # add to output
        wmsg = textentry('')
        wmsg += '\tdx={0:.6f} dy={1:.6f}'.format(*ltv)
        wmsg += '\n\t{0}(A-1)={1:.6f}\t{0}B={2:.6f}'.format(*wargs1)
        wmsg += '\n\t{0}C={1:.6f}\t{0}(D-1)={2:.6f}'.format(*wargs2)
        WLOG(params, '', wmsg)

    # plot if in debug mode
    recipe.plot('SHAPE_LINEAR_TPARAMS', image=image1, x1=x1, x2=x2,
                y1=y1, y2=y2)

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

    :param params: ParamDict, the parameter dictionary of constants
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
    # log progress (transforming dxmap, dymap, trans)
    dxmapstr = int(dxmap is not None)
    dymapstr = int(dymap is not None)
    transstr = int(lin_transform_vect is not None)
    wargs = [dxmapstr, dymapstr, transstr]
    WLOG(params, '', textentry('40-014-00041', args=wargs))

    # check size of dx and dy map
    if dxmap is not None:
        if dxmap.shape != image.shape:
            eargs = [dxmap.shape, image.shape, func_name]
            WLOG(params, 'error', textentry('00-014-00002', args=eargs))
    if dymap is not None:
        if dymap.shape != image.shape:
            eargs = [dymap.shape, image.shape, func_name]
            WLOG(params, 'error', textentry('00-014-00003', args=eargs))
    # deal with no linear transform required (just a dxmap or dymap shift)
    if lin_transform_vect is None:
        lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    # copy the image
    image = np.array(image)
    # transforming an image with the 6 linear transform terms
    # Be careful with NaN values, there should be none
    lout = list(lin_transform_vect)
    shape_dx, shape_dy, shape_a, shape_b, shape_c, shape_d = lout
    # get the pixel locations for the image
    yy, xx = np.indices(image.shape, dtype=float)
    # get the shifted x pixel locations
    xx2 = shape_dx + xx * shape_a + yy * shape_b
    if dxmap is not None:
        xx2 += dxmap
    # get the shifted y pixel locations
    yy2 = shape_dy + xx * shape_c + yy * shape_d
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


def ea_transform_coeff(image, coeffs, lin_transform_vect):
    # get the number of orders
    nbo = coeffs.shape[0]
    # get the x pixel positions
    xpix = np.arange(image.shape[1])
    # extract out the parameters from lin transform vector
    dx0, dy0 = lin_transform_vect[:2]
    # invert the lin transform vector
    lin_vec = np.array(lin_transform_vect[2:]).reshape(2, 2)
    inv_lin_vec = np.linalg.inv(lin_vec)
    lin_a, lin_b, lin_c, lin_d = inv_lin_vec.ravel()
    # get the new coeffs array
    coeffs2 = np.zeros_like(coeffs)
    # loop through the orders
    for order_num in range(nbo):
        # get this orders coefficients
        ocoeff = coeffs[order_num]
        # get the poly fit values for coeffs
        yfit = np.polyval(ocoeff[::-1], xpix)
        # transform the x pixel positions and fit positions
        xpix2 = -dx0 + xpix * lin_a + yfit * lin_b
        yfit2 = -dy0 + xpix * lin_c + yfit * lin_d
        # refit polynomial
        coeffs2[order_num] = np.polyfit(xpix2, yfit2, len(ocoeff) - 1)[::-1]
    # return new coefficients
    return coeffs2


def calculate_dxmap(params, recipe, hcdata, fpdata, lprops, **kwargs):
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
    short_medfilt_wid = pcheck(params, 'SHAPE_SHORT_DX_MEDFILT_WID',
                               'short_medfilt_width', kwargs, func_name)
    long_medfilt_wid = pcheck(params, 'SHAPE_LONG_DX_MEDFILT_WID',
                              'long_medfilt_width', kwargs, func_name)
    std_qc = pcheck(params, 'SHAPE_QC_DXMAP_STD', 'std_qc', kwargs, func_name)

    # get properties from property dictionaries
    nbo = lprops['NBO']
    acc = lprops['CENT_COEFFS']
    # poly_wave_ref = wprops['COEFFS']
    # une_lines, une_amps = drs_data.load_linelist(params)
    _, poly_cavity = drs_data.load_cavity_files(params)
    # get the dimensions
    dim1, dim2 = fpdata.shape
    # -------------------------------------------------------------------------
    # define storage for plotting
    slope_deg_arr, slope_arr, skeep_arr = [], [], []
    xsec_arr, ccor_arr = [], []
    ddx_arr, dx_arr = [], []
    dypix_arr, cckeep_arr = [], []
    dxrms_arr = []
    # define storage for output
    master_dxmap = np.zeros_like(fpdata)
    map_orders = np.zeros_like(fpdata) - 1
    order_overlap = np.zeros_like(fpdata)
    slope_all_ord = np.zeros((nbo, dim2))
    # -------------------------------------------------------------------------
    # create the x pixel vector (used with polynomials to find
    #    order center)
    xpix = np.array(range(dim2))
    # y order center positions (every other one)
    ypix = np.zeros((nbo, dim2))
    # loop around order number
    for order_num in range(nbo):
        # x pixel vector that is used with polynomials to
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
            hcdata2 = ea_transform(params, hcdata, dxmap=master_dxmap)
            fpdata2 = ea_transform(params, fpdata, dxmap=master_dxmap)
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
        xsec_arr_i, ccor_arr_i, ddx_arr_i, dx_arr_i = [], [], [], []
        dypix_arr_i, cckeep_arr_i, dxrms_arr_i = [], [], []
        # corr_dx_from_fp = np.zeros((nbo, dim2))
        shifts_all = np.zeros((nbo, dim2))
        # get dx array (NaN)
        dx = np.zeros((nbo, width)) + np.nan
        # ------------------------------------------------------------------
        # loop around orders
        for order_num in range(nbo):
            # --------------------------------------------------------------
            # Log progress banana iteration {0} of {1} order {2} of {3}
            wargs = [banana_num + 1, nbanana, order_num + 1, nbo]
            WLOG(params, '', textentry('40-014-00016', args=wargs))
            # --------------------------------------------------------------
            # defining a ribbon that will contain the straightened order
            ribbon_hc = np.zeros([width, dim2])
            ribbon_fp = np.zeros([width, dim2])
            # get the widths
            widths = np.arange(width) - width / 2.0
            # get all bottoms and tops
            bottoms = ypix[order_num] - width / 2 - 2
            tops = ypix[order_num] + width / 2 + 2
            # splitting the original image onto the ribbon
            for ix in range(dim2):
                # define bottom and top that encompasses all 3 fibers
                bottom = int(bottoms[ix])
                top = int(tops[ix])
                # deal with bottom and top being out of bounds
                if bottom < 0:
                    bottom = 0
                if top > dim1:
                    top = dim1
                # get the x pixels for range
                sx = np.arange(bottom, top)
                # calculate spline interpolation and ribbon values
                if bottom > 0:
                    # for the hc data
                    spline_hc = mp.iuv_spline(sx, hcdata2[bottom:top, ix],
                                              ext=1, k=3)
                    ribbon_hc[:, ix] = spline_hc(ypix[order_num, ix] + widths)
                    # for the fp data
                    spline_fp = mp.iuv_spline(sx, fpdata2[bottom:top, ix],
                                              ext=1, k=3)
                    ribbon_fp[:, ix] = spline_fp(ypix[order_num, ix] + widths)

            # normalizing ribbon stripes to their median abs dev
            for iw in range(width):
                # for the hc data
                norm_fp = mp.nanmedian(np.abs(ribbon_fp[iw, :]))
                # deal with a row of zeros
                if norm_fp == 0.0:
                    continue
                # deal with a zero norm_fp (means the order is out of bounds
                ribbon_hc[iw, :] = ribbon_hc[iw, :] / norm_fp
                # for the fp data
                ribbon_fp[iw, :] = ribbon_fp[iw, :] / norm_fp
            # range explored in slopes
            #
            # Once we have searched through a range of slopes and found the
            # best slope, we search a narrower range. We cut the slope range
            # by a factor of 8. This is a big ad-hoc as a number, but its a
            # reasonable compromise between code speed and being sure that we
            # would not miss the best slope on the next iteration
            #
            sfactor = (range_slopes[1] - range_slopes[0]) / 8.0
            slopes = (np.arange(9) * sfactor) + range_slopes[0]
            # log the range slope exploration
            wargs = [range_slopes_deg[0], range_slopes_deg[1]]
            WLOG(params, '', textentry('40-014-00017', args=wargs))
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
                    ddx = (iw - width / 2.0) * slope
                    # get the spline
                    spline = mp.iuv_spline(xpix, ribbon_fp[iw, :], ext=1)
                    # calculate the new ribbon values
                    ribbon_fp2[iw, :] = spline(xpix + ddx)
                # record the profile of the ribbon
                profile = mp.nanmedian(ribbon_fp2, axis=0)
                # loop around the sections to record rv content
                for nsection in range(nsections):
                    # sum of integral of derivatives == RV content.
                    # This should be maximal when the angle is right
                    start = nsection * dim2 // nsections
                    end = (nsection + 1) * dim2 // nsections
                    grad = np.gradient(profile[start:end])
                    rvcontent[islope, nsection] = mp.nansum(grad ** 2)
            # -------------------------------------------------------------
            # we find the peak of RV content and fit a parabola to that peak
            for nsection in range(nsections):
                # we must have some RV content (i.e., !=0)
                if mp.nanmax(rvcontent[:, nsection]) != 0:
                    vec = np.ones_like(slopes)
                    vec[0], vec[-1] = 0, 0
                    # get the max pixel
                    maxpix = mp.nanargmax(rvcontent[:, nsection] * vec)
                    # max RV and fit on the neighbouring pixels
                    xff = slopes[maxpix - 1: maxpix + 2]
                    yff = rvcontent[maxpix - 1: maxpix + 2, nsection]
                    coeffs = mp.nanpolyfit(xff, yff, 2)
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
            medslope = mp.nanmedian(dxdiff / xdiff)
            # work out the residual of dxsection (based on median slope)
            residual = dxsection - (medslope * xsection)
            residual = residual - mp.nanmedian(residual)
            res_residual = residual - mp.nanmedian(residual)
            residual = residual / mp.nanmedian(np.abs(res_residual))
            # work out the maximum sigma and update keep vector
            sigmax = mp.nanmax(np.abs(residual[keep]))
            with warnings.catch_warnings(record=True) as _:
                keep &= np.abs(residual) < sigclipmax
            # -------------------------------------------------------------
            # sigma clip
            while sigmax > sigclipmax:
                # recalculate the fit
                coeffs = mp.nanpolyfit(xsection[keep], dxsection[keep], 2)
                # get the residuals
                res = dxsection - np.polyval(coeffs, xsection)
                # normalise residuals
                res = res - mp.nanmedian(res[keep])
                res = res / mp.nanmedian(np.abs(res[keep]))
                # calculate the sigma
                sigmax = mp.nanmax(np.abs(res[keep]))
                # do not keep bad residuals
                with warnings.catch_warnings(record=True) as _:
                    keep &= np.abs(res) < sigclipmax
            # -------------------------------------------------------------
            # fit a 2nd order polynomial to the slope vx position
            #    along order
            coeffs = mp.nanpolyfit(xsection[keep], dxsection[keep], 2)
            # log slope at center
            s_xpix = dim2 // 2
            s_ypix = np.rad2deg(np.arctan(np.polyval(coeffs, s_xpix)))
            wargs = [s_xpix, s_ypix]
            WLOG(params, '', textentry('40-014-00018', args=wargs))
            # get slope for full range
            slope_all_ord[order_num] = np.polyval(coeffs, np.arange(dim2))
            # -------------------------------------------------------------
            # append to storage (for plotting)
            xsec_arr_i.append(np.array(xsection))
            slope_deg_arr_i.append(np.rad2deg(np.arctan(dxsection)))
            slope_arr_i.append(np.rad2deg(np.arctan(slope_all_ord[order_num])))
            skeep_arr_i.append(np.array(keep))

            # -------------------------------------------------------------
            # correct for the slope the ribbons and look for the
            #    slicer profile in the fp
            yfit = np.polyval(coeffs, xpix)
            for iw in range(width):
                # get the x shift
                ddx = (iw - width / 2.0) * yfit
                # calculate the spline at this width
                spline_fp = mp.iuv_spline(xpix, ribbon_fp[iw, :], ext=1)
                # push spline values with shift into ribbon2
                ribbon_fp2[iw, :] = spline_fp(xpix + ddx)
            # -------------------------------------------------------------
            # correct for the slope the ribbons and look for the slicer profile
            #    in the hc
            ribbon_hc2 = np.array(ribbon_hc)
            for iw in range(width):
                # get the x shift
                ddx = (iw - width / 2.0) * yfit
                # calculate the spline at this width
                spline_hc = mp.iuv_spline(xpix, ribbon_hc[iw, :], ext=1)
                # push spline values with shift into ribbon2
                ribbon_hc2[iw, :] = spline_hc(xpix + ddx)

            # -------------------------------------------------------------
            # get the median values of the fp and hc
            # sp_fp = mp.nanmedian(ribbon_fp2, axis=0)
            # sp_hc = mp.nanmedian(ribbon_hc2, axis=0)

            # pargs = [params, sp_fp, sp_hc, order_num, hcdata,
            #          poly_wave_ref, une_lines, poly_cavity]
            # out = get_offset_sp(*pargs)
            # # get and save offest outputs into lists
            # corr_dx_from_fp[order_num] = out[0]
            # xpeak2.append(out[1])
            # peakval2.append(out[2])
            # ewval2.append(out[3])
            # err_pix.append(out[4])
            # good_mask.append(out[5])
            # -------------------------------------------------------------
            # median FP peak profile. We will cross-correlate each
            # row of the ribbon with this
            profile = mp.nanmedian(ribbon_fp2, axis=0)
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
                    # we perform a gaussian fit on the correlation coefficient
                    # between the median order profile and the Nth slice in
                    # y perpendicular to dispersion along the order. The
                    # gaussian fit has nn=4 as there may be a DC offset
                    # nn=4 is gaussian+offset (5th is slope, just in case
                    # you wondered)
                    gcoeffs, _ = mp.gauss_fit_nn(xvec, yvec, 4)
                # check that max value is good
                if mp.nanmax(ccor[iw, :]) > min_good_corr:
                    dx[order_num, iw] = gcoeffs[1]
            # -------------------------------------------------------------
            # remove any offset in dx, this would only shift the spectra

            # TODO : bad bad bad, don't comment out yet!
            dypix = np.arange(len(dx[order_num]))
            with warnings.catch_warnings(record=True):
                keep = np.abs(dx[order_num] - mp.nanmedian(dx[order_num])) < 1
            keep &= np.isfinite(dx[order_num])
            # -------------------------------------------------------------
            # append to storage for plotting
            ccor_arr_i.append(np.array(ccor))
            ddx_arr_i.append(np.array(ddx))
            dx_arr_i.append(np.array(dx[order_num]))
            dypix_arr_i.append(np.array(dypix))
            cckeep_arr_i.append(np.array(keep))
            # get rms values
            dxrms_arr_i.append(np.array(dx[order_num] - np.nanmin(ddx)))
            # -----------------------------------------------------------------
            # set those values that should not be kept to NaN
            dx[order_num][~keep] = np.nan
        # -----------------------------------------------------------------
        # get the median filter of dx (short median filter)
        dx2_short = np.array(dx)
        for iw in range(width):
            dx2_short[:, iw] = mp.medfilt_1d(dx[:, iw], short_medfilt_wid)
        # get the median filter of short dx with longer median
        #     filter/second pass
        dx2_long = np.array(dx)
        for iw in range(width):
            dx2_long[:, iw] = mp.medfilt_1d(dx2_short[:, iw], long_medfilt_wid)
        # apply short dx filter to dx2
        dx2 = np.array(dx2_short)
        # apply long dx filter to NaN positions of short dx filter
        nanmask = ~np.isfinite(dx2)
        dx2[nanmask] = dx2_long[nanmask]
        # ---------------------------------------------------------------------
        # dx plot
        recipe.plot('SHAPE_DX', dx=dx, dx2=dx2, bnum=banana_num,
                    nbanana=nbanana)
        # ---------------------------------------------------------------------
        # loop around orders
        for order_num in range(nbo):
            # -------------------------------------------------------------
            # log process (updating big dx map)
            wargs = [order_num + 1, nbo]
            WLOG(params, '', textentry('40-014-00021', args=wargs))
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
            start_good_ccor = mp.nanmin(pos_keep) - 2
            # deal with start being out-of-bounds
            if start_good_ccor == -1:
                start_good_ccor = 0
            # set the end point
            end_good_ccor = mp.nanmax(pos_keep) + 2
            # deal with end being out-of-bounds
            if end_good_ccor == width:
                end_good_ccor = width - 1
            # work out spline
            spline = mp.iuv_spline(dypix[keep], dx2[order_num][keep], ext=3)
            # define a mask for the good ccor
            good_ccor_mask = np.zeros(len(keep), dtype=bool)
            good_ccor_mask[start_good_ccor:end_good_ccor] = True

            # log start and end points along slice
            wargs = [start_good_ccor, end_good_ccor]
            WLOG(params, '', textentry('40-014-00022', args=wargs))

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
                widthrange = np.arange(-width // 2, width // 2)
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
                if order_num != (nbo - 1):
                    ypixa = ypix[order_num + 1, ix]
                    upper_ylimit_overlap = ypix0 + 0.5 * (ypixa - ypix0) - 1
                else:
                    upper_ylimit_overlap = dim1 - 1
                # identify the lower bound of order
                if order_num != 0:
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
                    shifts = ddx_f[pos_y_mask]  # - corr_dx_from_fp[order_num][ix]
                    shifts_all[order_num][ix] = np.nanmean(shifts)
                    # apply shifts to master dx map at correct positions
                    master_dxmap[positions, ix] += shifts

                    # after each iteration updating the dxmap, we verify
                    # that the per-order and per-x-pixel shift is not larger
                    # than the maximum seen over 'normal' images.
                    dxmap_std = mp.nanstd(master_dxmap[positions, ix])

                    dxmap_stds.append(dxmap_std)

                    # return here if QC not met
                    if dxmap_std > std_qc:
                        # add DXMAP to loc
                        dxmap = None
                        max_dxmap_std = dxmap_std
                        max_dxmap_info = [order_num, ix, std_qc]
                        return dxmap, max_dxmap_std, max_dxmap_info, None
        # -----------------------------------------------------------------
        # plot all order angle_offset plot (in loop)
        pkwargs = dict(slope_deg=[slope_deg_arr_i], slope=[slope_arr_i],
                       skeep=[skeep_arr_i], xsection=[xsec_arr_i],
                       ccor=[ccor_arr_i], ddx=[ddx_arr_i], dx=[dx_arr_i],
                       dypix=[dypix_arr_i], ckeep=[cckeep_arr_i])
        recipe.plot('SHAPE_ANGLE_OFFSET_ALL', params=params, bnum=banana_num,
                    nbo=nbo, nbpix=dim2, **pkwargs)
        # ---------------------------------------------------------------------
        # append to storage
        slope_deg_arr.append(slope_deg_arr_i), slope_arr.append(slope_arr_i)
        skeep_arr.append(skeep_arr_i), xsec_arr.append(xsec_arr_i)
        ccor_arr.append(ccor_arr_i), ddx_arr.append(ddx_arr_i)
        dx_arr.append(dx_arr_i), dypix_arr.append(dypix_arr_i)
        dxrms_arr.append(dxrms_arr_i), cckeep_arr.append(cckeep_arr_i)
    # ---------------------------------------------------------------------
    # plot selected order angle_offset plot
    pkwargs = dict(slope_deg=slope_deg_arr, slope=slope_arr,
                   skeep=skeep_arr, xsection=xsec_arr, ccor=ccor_arr,
                   ddx=ddx_arr, dx=dx_arr, dypix=dypix_arr, ckeep=cckeep_arr)
    # plot as debug plot
    recipe.plot('SHAPE_ANGLE_OFFSET', params=params, bnum=None, nbo=nbo,
                nbpix=dim2, **pkwargs)
    # plot as summary plot
    recipe.plot('SUM_SHAPE_ANGLE_OFFSET', params=params, bnum=None, nbo=nbo,
                nbpix=dim2, **pkwargs)
    # ---------------------------------------------------------------------
    # setting to 0 pixels that are NaNs
    nanmask = ~np.isfinite(master_dxmap)
    master_dxmap[nanmask] = 0.0

    # distortions where there is some overlap between orders will be wrong
    master_dxmap[order_overlap != 0] = 0.0
    # save qc
    max_dxmap_std = mp.nanmax(dxmap_stds)
    max_dxmap_info = [None, None, std_qc]
    # ---------------------------------------------------------------------
    # calculate rms for dx-ddx (last iteration)
    dxrms = []
    for order_num in range(nbo):
        # get the keep mask
        keep = cckeep_arr[-1][order_num]

        dxrms.append(np.nanstd(dxrms_arr[-1][order_num][keep]))
    # ---------------------------------------------------------------------
    # return parameters
    return master_dxmap, max_dxmap_std, max_dxmap_info, dxrms


def calculate_dymap(params, fpimage, fpheader, **kwargs):
    func_name = __NAME__ + '.calculate_dymap()'
    # get properties from property dictionaries
    fibers = pcheck(params, 'SHAPE_UNIQUE_FIBERS', 'fibers', kwargs, func_name)
    # get the dimensions
    dim1, dim2 = fpimage.shape
    # make fibers a list
    fibers = list(map(lambda x: x.strip(), fibers.split(',')))
    # x indices in the initial image
    xpix = np.arange(dim2)
    # ----------------------------------------------------------------------
    # get localisation parameters for each fiber
    accs, nbo = dict(), 0
    # loop around fiber
    for fiber in fibers:
        # log progress
        WLOG(params, '', textentry('40-014-00024', args=[fiber]))
        # get coefficients
        lprops = localisation.get_coefficients(params, fpheader, fiber=fiber,
                                               merge=True)
        # update nbo
        nbo = lprops['NBO']
        # add to array
        accs[fiber] = np.array(lprops['CENT_COEFFS'])
    # number of fibers
    nfibers = len(fibers)
    # ----------------------------------------------------------------------
    # looping through x pixels
    # We take each column and determine where abc fibers fall relative
    # to the central pixel in x (normally, that's 4088/2) along the y axis.
    # This difference in position gives a dy that need to be applied to
    # straighten the orders

    # Once we have determined this for all abc fibers and all orders, we
    # fit a Nth order polynomial to the dy versus y relation along the
    # column, and apply a spline to straighten the order.
    y0 = np.zeros((nbo * nfibers, dim2))
    # log progress
    WLOG(params, '', textentry('40-014-00023'))
    # set a master dy map
    master_dymap = np.zeros_like(fpimage)
    # loop around orders and get polynomial values for fibers A, B and C
    for order_num in range(nbo):
        iord = order_num * nfibers
        # loop around the fibers and calculate the y positions using each
        #   fibers coefficients (for each order)
        for f_it, fiber in enumerate(accs.keys()):
            # get this order + fibers coefficients
            acco = accs[fiber][order_num, :][::-1]
            # get the poly values
            ypoly = np.polyval(acco, xpix)
            # work out this order + fibers y values: polynomial(x position)
            y0[iord + f_it, :] = ypoly
    # loop around each x pixel (columns)
    for ix in range(dim2):
        # dy for all orders and all fibers
        dy = y0[:, ix] - y0[:, dim2 // 2]
        # fitting the dy to the position of the order
        yfit = mp.nanpolyfit(y0[:, dim2 // 2], dy, 3)
        ypix = np.arange(dim1)
        # add to the master dy map
        master_dymap[:, ix] = np.polyval(yfit, ypix)
    # return dymap
    return master_dymap


def get_master_fp(params, header, filename=None, database=None):
    # get file definition
    out_fpmaster = drs_file.get_file_definition(params, 'MASTER_FP',
                                                block_kind='red')
    # get key
    key = out_fpmaster.dbkey
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ----------------------------------------------------------------------
    # load master fp
    cout = gen_calib.load_calib_file(params, key, header, filename=filename,
                                     userinputkey='FPMASTER', database=calibdbm)
    fpmaster, _, fpmaster_file = cout
    # ----------------------------------------------------------------------
    # log which fpmaster file we are using
    WLOG(params, '', textentry('40-014-00030', args=[fpmaster_file]))
    # return the master image
    return fpmaster_file, fpmaster


def get_shape_calibs(params, header, database):
    # set function name
    func_name = __NAME__ + '.get_shape_calibs()'
    # get shape x
    sout = get_shapex(params, header, database=database)
    shapexfile, shapextime, shapex = sout
    # get shape y
    sout = get_shapey(params, header, database=database)
    shapeyfile, shapeytime, shapey = sout
    # get shape local
    sout = get_shapelocal(params, header, database=database)
    shapelocalfile, shapelocaltime, shapelocal = sout
    # out to parameter dictionary
    sprops = ParamDict()
    sprops['SHAPEX'] = shapex
    sprops['SHAPEXFILE'] = shapexfile
    sprops['SHAPEXTIME'] = shapextime
    sprops['SHAPEY'] = shapey
    sprops['SHAPEYFILE'] = shapeyfile
    sprops['SHAPEYTIME'] = shapeytime
    sprops['SHAPEL'] = shapelocal
    sprops['SHAPELFILE'] = shapelocalfile
    sprops['SHAPELTIME'] = shapelocaltime
    # set source
    keys = ['SHAPEX', 'SHAPEXFILE', 'SHAPEXTIME',
            'SHAPEY', 'SHAPEYFILE', 'SHAPEYTIME',
            'SHAPEL', 'SHAPELFILE', 'SHAPELTIME']
    sprops.set_sources(keys, func_name)
    # return shape properties
    return sprops


def get_shapex(params, header, filename=None, database=None):
    # get file definition
    out_shape_dxmap = drs_file.get_file_definition(params, 'SHAPE_X',
                                                   block_kind='red')
    # get key
    key = out_shape_dxmap.dbkey
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ----------------------------------------------------------------------
    # load shape x file
    cout = gen_calib.load_calib_file(params, key, header, filename=filename,
                                     userinputkey='SHAPEX', database=calibdbm,
                                     return_time=True)
    dxmap, fhdr, shapex_file, shapetime = cout
    # ------------------------------------------------------------------------
    # log which fpmaster file we are using
    WLOG(params, '', textentry('40-014-00031', args=[shapex_file]))
    # return the master image
    return shapex_file, shapetime, dxmap


def get_shapey(params, header, filename=None, database=None):
    # get file definition
    out_shape_dymap = drs_file.get_file_definition(params, 'SHAPE_Y',
                                                   block_kind='red')
    # get key
    key = out_shape_dymap.dbkey
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ----------------------------------------------------------------------
    # load shape x file
    cout = gen_calib.load_calib_file(params, key, header, filename=filename,
                                     userinputkey='SHAPEY', database=calibdbm,
                                     return_time=True)
    dymap, fhdr, shapey_file, shapetime = cout
    # ------------------------------------------------------------------------
    # log which fpmaster file we are using
    WLOG(params, '', textentry('40-014-00032', args=[shapey_file]))
    # return the master image
    return shapey_file, shapetime, dymap


def get_shapelocal(params, header, filename=None, database=None):
    # get file definition
    out_shape_local = drs_file.get_file_definition(params, 'SHAPEL',
                                                   block_kind='red')
    # get key
    key = out_shape_local.dbkey
    # ----------------------------------------------------------------------
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ----------------------------------------------------------------------
    # load shape x file
    cout = gen_calib.load_calib_file(params, key, header, filename=filename,
                                     userinputkey='SHAPEL', database=calibdbm,
                                     return_time=True)
    shapel, fhdr, shapel_file, shapetime = cout
    # ------------------------------------------------------------------------
    # log which fpmaster file we are using
    WLOG(params, '', textentry('40-014-00039', args=[shapel_file]))
    # return the master image
    return shapel_file, shapetime, shapel.flatten()


# =============================================================================
# write file functions
# =============================================================================
def write_shape_master_files(params, recipe, fpfile, hcfile, rawfpfiles,
                             rawhcfiles, dxmap, dymap, master_fp, fp_table,
                             fpprops, dxmap0, fpimage, fpimage2, hcimage,
                             hcimage2, qc_params):
    # ----------------------------------------------------------------------
    # Writing DXMAP to file
    # ----------------------------------------------------------------------
    # define outfile
    outfile1 = recipe.outputs['DXMAP_FILE'].newcopy(params=params)
    # construct the filename from file instance
    outfile1.construct_filename(infile=fpfile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    outfile1.copy_original_keys(fpfile)
    # add version
    outfile1.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    outfile1.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    outfile1.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    outfile1.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    outfile1.add_hkey('KW_OUTPUT', value=outfile1.name)
    # add input files (and deal with combining or not combining)
    # deal with not having hc or fp files
    if hcfile is None:
        outfile1.add_hkey_1d('KW_INFILE1', values=rawfpfiles,
                             dim1name='fpfiles')
        # add in files
        outfile1.infiles = rawfpfiles
    elif fpfile is None:
        outfile1.add_hkey_1d('KW_INFILE1', values=rawhcfiles,
                             dim1name='hcfiles')
        # add in files
        outfile1.infiles = rawhcfiles
    else:
        outfile1.add_hkey_1d('KW_INFILE1', values=rawhcfiles,
                             dim1name='hcfiles')
        outfile1.add_hkey_1d('KW_INFILE2', values=rawfpfiles,
                             dim1name='fpfiles')
        # add in files
        outfile1.infiles = list(rawhcfiles) + list(rawfpfiles)
    # add the calibration files use
    outfile1 = gen_calib.add_calibs_to_header(outfile1, fpprops)
    # add qc parameters
    outfile1.add_qckeys(qc_params)
    # copy data
    outfile1.data = dxmap
    # ------------------------------------------------------------------
    # log that we are saving dxmap to file
    WLOG(params, '', textentry('40-014-00026', args=[outfile1.filename]))
    # define multi lists
    data_list = [fp_table]
    name_list = ['FP_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        ptable = params.snapshot_table(recipe, drsfitsfile=outfile1)
        data_list += [ptable]
        name_list += ['PARAM_TABLE']
    # write image to file
    outfile1.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(outfile1)
    # ----------------------------------------------------------------------
    # Writing DYMAP to file
    # ----------------------------------------------------------------------
    # define outfile
    outfile2 = recipe.outputs['DYMAP_FILE'].newcopy(params=params)
    # construct the filename from file instance
    outfile2.construct_filename(infile=fpfile)
    # copy header from outfile1
    outfile2.copy_hdict(outfile1)
    # add in files
    outfile2.infiles = list(outfile1.infiles)
    # set output key
    outfile2.add_hkey('KW_OUTPUT', value=outfile2.name)
    # copy data
    outfile2.data = dymap
    # log that we are saving dymap to file
    WLOG(params, '', textentry('40-014-00027', args=[outfile2.filename]))
    # define multi lists
    data_list = [fp_table]
    name_list = ['FP_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=outfile2)]
        name_list += ['PARAM_TABLE']
    # write image to file
    outfile2.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(outfile2)
    # ----------------------------------------------------------------------
    # Writing Master FP to file
    # ----------------------------------------------------------------------
    # define outfile
    outfile3 = recipe.outputs['FPMASTER_FILE'].newcopy(params=params)
    # construct the filename from file instance
    outfile3.construct_filename(infile=fpfile)
    # copy header from outfile1
    outfile3.copy_hdict(outfile1)
    # add in files
    outfile3.infiles = list(outfile1.infiles)
    # set output key
    outfile3.add_hkey('KW_OUTPUT', value=outfile3.name)
    # copy data
    outfile3.data = master_fp
    # log that we are saving master_fp to file
    WLOG(params, '', textentry('40-014-00028', args=[outfile3.filename]))
    # define multi lists
    data_list = [fp_table]
    name_list = ['FP_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=outfile3)]
        name_list += ['PARAM_TABLE']
    # write image to file
    outfile3.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(outfile3)
    # ----------------------------------------------------------------------
    # Writing DEBUG files
    # ----------------------------------------------------------------------
    if params['DEBUG_SHAPE_FILES']:
        # log progress (writing debug outputs)
        WLOG(params, '', textentry('40-014-00029'))
        # ------------------------------------------------------------------
        # deal with the unstraighted dxmap
        # ------------------------------------------------------------------
        debugfile0 = recipe.outputs['SHAPE_BDXMAP_FILE'].newcopy(params=params)
        debugfile0.construct_filename(infile=fpfile)
        debugfile0.copy_hdict(outfile1)
        # add in files
        debugfile0.infiles = list(outfile1.infiles)
        # add output type
        debugfile0.add_hkey('KW_OUTPUT', value=debugfile0.name)
        # add data
        debugfile0.data = dxmap0
        # define multi lists
        data_list = [fp_table]
        name_list = ['FP_TABLE']
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=debugfile0)]
            name_list += ['PARAM_TABLE']
        # write file
        debugfile0.write_multi(data_list=data_list, name_list=name_list,
                               block_kind=recipe.out_block_str,
                               runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(debugfile0)
        # ------------------------------------------------------------------
        # for the fp files take the header from outfile1
        # ------------------------------------------------------------------
        # in file
        debugfile1 = recipe.outputs['SHAPE_IN_FP_FILE'].newcopy(params=params)
        debugfile1.construct_filename(infile=fpfile)
        debugfile1.copy_hdict(outfile1)
        # add in files
        debugfile1.infiles = list(outfile1.infiles)
        # add output type
        debugfile1.add_hkey('KW_OUTPUT', value=debugfile1.name)
        # add output type
        debugfile1.data = fpimage
        # define multi lists
        data_list = [fp_table]
        name_list = ['FP_TABLE']
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=debugfile1)]
            name_list += ['PARAM_TABLE']
        # write file
        debugfile1.write_multi(data_list=data_list, name_list=name_list,
                               block_kind=recipe.out_block_str,
                               runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(debugfile1)
        # out file
        debugfile2 = recipe.outputs['SHAPE_OUT_FP_FILE'].newcopy(params=params)
        debugfile2.construct_filename(infile=fpfile)
        debugfile2.copy_hdict(outfile1)
        # add in files
        debugfile2.infiles = list(outfile1.infiles)
        # add output type
        debugfile2.add_hkey('KW_OUTPUT', value=debugfile2.name)
        # add data
        debugfile2.data = fpimage2
        # define multi lists
        data_list = [fp_table]
        name_list = ['FP_TABLE']
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=debugfile2)]
            name_list += ['PARAM_TABLE']
        # write file
        debugfile2.write_multi(data_list=data_list, name_list=name_list,
                               block_kind=recipe.out_block_str,
                               runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(debugfile2)
        # ------------------------------------------------------------------
        # for hc files copy over the fp parameters with the hc parameters
        # ------------------------------------------------------------------
        if 'SHAPE_IN_HC_FILE' in recipe.outputs:
            # in file
            shape_in_hc_file = recipe.outputs['SHAPE_IN_HC_FILE']
            debugfile3 = shape_in_hc_file.newcopy(params=params)
            debugfile3.construct_filename(infile=hcfile)
            debugfile3.copy_original_keys(hcfile)
            # add in files
            debugfile3.infiles = list(outfile1.infiles)
            # add version
            debugfile3.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
            # add dates
            debugfile3.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
            debugfile3.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
            # add process id
            debugfile3.add_hkey('KW_PID', value=params['PID'])
            # add output tag
            debugfile3.add_hkey('KW_OUTPUT', value=debugfile3.name)
            # add input files (and deal with combining or not combining)
            debugfile3.add_hkey_1d('KW_INFILE1', values=rawhcfiles,
                                   dim1name='hcfiles')
            debugfile3.add_hkey_1d('KW_INFILE2', values=rawfpfiles,
                                   dim1name='fpfiles')
            # add the calibration files use
            debugfile3 = gen_calib.add_calibs_to_header(debugfile3, fpprops)
            # add qc parameters
            debugfile3.add_qckeys(qc_params)
            # add data
            debugfile3.data = hcimage
            # define multi lists
            data_list = [fp_table]
            name_list = ['FP_TABLE']
            # snapshot of parameters
            if params['PARAMETER_SNAPSHOT']:
                data_list += [params.snapshot_table(recipe, drsfitsfile=debugfile3)]
                name_list += ['PARAM_TABLE']
            # write file
            debugfile3.write_multi(data_list=data_list, name_list=name_list,
                                   block_kind=recipe.out_block_str,
                                   runstring=recipe.runstring)
            # add to output files (for indexing)
            recipe.add_output_file(debugfile3)
            if 'SHAPE_OUT_HC_FILE' in recipe.outputs:
                # out file
                shape_out_hc_file = recipe.outputs['SHAPE_OUT_HC_FILE']
                debugfile4 = shape_out_hc_file.newcopy(params=params)
                debugfile4.construct_filename(infile=hcfile)
                # copy debug file 3
                debugfile4.copy_hdict(debugfile3)
                # add in files
                debugfile4.infiles = list(outfile1.infiles)
                # add output key
                debugfile4.add_hkey('KW_OUTPUT', value=debugfile4.name)
                debugfile4.data = hcimage2
                # define multi lists
                data_list = [fp_table]
                name_list = ['FP_TABLE']
                # snapshot of parameters
                if params['PARAMETER_SNAPSHOT']:
                    data_list += [params.snapshot_table(recipe,
                                                        drsfitsfile=debugfile4)]
                    name_list += ['PARAM_TABLE']
                # write file
                debugfile4.write_multi(data_list=data_list, name_list=name_list,
                                       block_kind=recipe.out_block_str,
                                       runstring=recipe.runstring)
                # add to output files (for indexing)
                recipe.add_output_file(debugfile4)
    # return output files (not debugs)
    return outfile1, outfile2, outfile3


def shape_master_qc(params, dxrms=None, qc_params=None, **kwargs):
    func_name = __NAME__ + '.shape_master_qc()'
    # set passed variable and fail message list
    fail_msg = []
    # deal with having qc parameters already
    if qc_params is not None:
        qc_names, qc_values, qc_logic, qc_pass = qc_params
    else:
        qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # get dxrms criteria
    dxrmscut = pcheck(params, 'SHAPE_MASTER_DX_RMS_QC', 'dxrmscut', kwargs,
                      func_name)
    # ------------------------------------------------------------------
    # dxmap and dxrms can be None
    if dxrms is None:
        # no quality control currently
        qc_values.append('None')
        qc_names.append('None')
        qc_logic.append('None')
        qc_pass.append(1)
    else:
        # loop around orders and check dx rms
        for order_num in range(len(dxrms)):
            # get qcargs
            qcargs = [order_num, dxrms[order_num], dxrmscut]
            # check that rms is below required level
            if dxrms[order_num] > dxrmscut:
                fail_msg.append(textentry('40-014-00042', args=qcargs))
                qc_pass.append(0)
            else:
                qc_pass.append(1)
            # add to qc header lists
            qc_values.append(dxrms[order_num])
            qc_names.append('dxrms')
            qc_logic.append('dxrms{0} > {2:.2f}'.format(*qcargs))
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # return qc_params and passed
    return qc_params, passed


def write_shape_master_summary(recipe, params, fp_table, qc_params):
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('NFPMASTER', value=len(fp_table),
                         comment='Number FP in Master')
    # TODO: Add more stats?
    # construct summary
    recipe.plot.summary_document(0, qc_params)


def shape_local_qc(params, transform, xres, yres):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # ------------------------------------------------------------------
    # check that transform is not None
    if transform is None:
        fail_msg.append(textentry('40-014-00034'))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    qc_values.append('None')
    qc_names.append('Image Quality')
    qc_logic.append('Image too poor')
    # ------------------------------------------------------------------
    # check that the x and y residuals are low enough
    qc_res = params['SHAPE_QC_LTRANS_RES_THRES']
    # assess quality of x residuals
    if xres > qc_res:
        fail_msg.append(textentry('40-014-00035', args=[xres, qc_res]))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    qc_values.append(xres)
    qc_names.append('XRES')
    qc_logic.append('XRES > {0}'.format(qc_res))
    # assess quality of x residuals
    if yres > qc_res:
        fail_msg.append(textentry('40-014-00036', args=[yres, qc_res]))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    qc_values.append(yres)
    qc_names.append('YRES')
    qc_logic.append('YRES > {0}'.format(qc_res))
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def write_shape_local_files(params, recipe, infile, combine, rawfiles, props,
                            transform, image, image2, qc_params):
    # define outfile
    outfile = recipe.outputs['LOCAL_SHAPE_FILE'].newcopy(params=params)
    # construct the filename from file instance
    outfile.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    outfile.copy_original_keys(infile)
    # add version
    outfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    outfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    outfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    outfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    outfile.add_hkey('KW_OUTPUT', value=outfile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    outfile.add_hkey_1d('KW_INFILE1', values=hfiles,
                        dim1name='hcfiles')
    # add in files
    outfile.infiles = list(hfiles)
    # add the calibration files use
    outfile = gen_calib.add_calibs_to_header(outfile, props)
    # add qc parameters
    outfile.add_qckeys(qc_params)
    # add shape transform parameters
    outfile.add_hkey('KW_SHAPE_DX', value=transform[0])
    outfile.add_hkey('KW_SHAPE_DY', value=transform[1])
    outfile.add_hkey('KW_SHAPE_A', value=transform[2])
    outfile.add_hkey('KW_SHAPE_B', value=transform[3])
    outfile.add_hkey('KW_SHAPE_C', value=transform[4])
    outfile.add_hkey('KW_SHAPE_D', value=transform[5])
    # copy data
    outfile.data = [transform]
    # ------------------------------------------------------------------
    # log that we are saving dxmap to file
    WLOG(params, '', textentry('40-014-00037', args=[outfile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=outfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    outfile.write_multi(data_list=data_list, name_list=name_list,
                        block_kind=recipe.out_block_str,
                        runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(outfile)
    # ----------------------------------------------------------------------
    # Writing DEBUG files
    # ----------------------------------------------------------------------
    if params['DEBUG_SHAPE_FILES']:
        # log progress (writing debug outputs)
        WLOG(params, '', textentry('40-014-00029'))
        # in file
        shapel_in_fp_file = recipe.outputs['SHAPEL_IN_FP_FILE']
        debugfile1 = shapel_in_fp_file.newcopy(params=params)
        debugfile1.construct_filename(infile=infile)
        debugfile1.copy_hdict(outfile)
        # add in files
        debugfile1.infiles = list(hfiles)
        # add output file
        debugfile1.add_hkey('KW_OUTPUT', value=debugfile1.name)
        debugfile1.data = image
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=debugfile1)]
            name_list += ['PARAM_TABLE']
        # write file
        debugfile1.write_multi(data_list=data_list, name_list=name_list,
                               block_kind=recipe.out_block_str,
                               runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(debugfile1)
        # out file
        shapel_out_fp_file = recipe.outputs['SHAPEL_OUT_FP_FILE']
        debugfile2 = shapel_out_fp_file.newcopy(params=params)
        debugfile2.construct_filename(infile=infile)
        debugfile2.copy_hdict(outfile)
        # add in files
        debugfile2.infiles = list(hfiles)
        # add output file
        debugfile2.add_hkey('KW_OUTPUT', value=debugfile2.name)
        debugfile2.data = image2
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=debugfile2)]
            name_list += ['PARAM_TABLE']
        # write file
        debugfile2.write_multi(data_list=data_list, name_list=name_list,
                               block_kind=recipe.out_block_str,
                               runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(debugfile2)
    # return outfile
    return outfile


def write_shape_local_summary(recipe, params, qc_params, it, transform):
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_SHAPE_DX', value=transform[0])
    recipe.plot.add_stat('KW_SHAPE_DY', value=transform[1])
    recipe.plot.add_stat('KW_SHAPE_A', value=transform[2])
    recipe.plot.add_stat('KW_SHAPE_B', value=transform[3])
    recipe.plot.add_stat('KW_SHAPE_C', value=transform[4])
    recipe.plot.add_stat('KW_SHAPE_D', value=transform[5])
    # construct summary
    recipe.plot.summary_document(it, qc_params)


# =============================================================================
# Define worker functions
# =============================================================================
def max_neighbour_mask(image, percent, thres):
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
        max_neighbours = mp.nanmax(box, axis=0)

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


def xy_acc_peak(xpeak, ypeak, im):
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

    return x1, y1


# TODO: function no longer used (was used in calculate_dxmap)
def get_offset_sp(params, sp_fp, sp_hc, order_num, hcdata, poly_wave_ref,
                  une_lines, poly_cavity, **kwargs):
    func_name = __NAME__ + '.get_offset_sp'
    # get constants from params/kwargs
    xoffset = pcheck(params, 'SHAPEOFFSET_XOFFSET', 'xoffset', kwargs,
                     func_name)
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
    dim1, dim2 = hcdata.shape
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
    top_floor_value = top_floor_frac * mp.nanmax(top)
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
    sp_hc = sp_hc - mp.medfilt_1d(sp_hc, med_filter_wid)
    # normalise HC to its absolute deviation
    norm = mp.nanmedian(np.abs(sp_hc[sp_hc != 0]))
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
    wave_fp = np.polyval(poly_cavity, wave_start_med_end[1]) * 2 / fpindex
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
    maxfp = mp.nanmax(sp_fp)
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
        y0 = mp.nanargmin(yy / mp.nanmax(yy) + mask1)
        y1 = mp.nanargmin(yy / mp.nanmax(yy) + mask2)
        # re-set xx and yy
        xx = np.array(xx[y0:y1 + 1]).astype(float)
        yy = np.array(yy[y0:y1 + 1]).astype(float)

        # the FP must be at least 5 pixels long to be valid
        if len(xx) > valid_fp_length:
            # set up the guess: amp, x0, w, zp
            guess = (float(mp.nanmax(yy) - mp.nanmin(yy)),
                     float(xx[mp.nanargmax(yy)]), 1.0,
                     float(mp.nanmin(yy)), 0.0)
            # try to fit a gaussian
            # noinspection PyBroadException
            try:
                coeffs, _ = curve_fit(mp.gauss_fit_s, xx, yy, p0=guess)
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
    fit_peak_separation = mp.nanpolyfit(xpeak2_mean[good], dxpeak[good], 2)
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
        if np.round(dx / dx_est) != 1:
            wmsg = '\t\tdx={0:.5f} dx/dx_est={1:.5f} est={2:.5f}'
            wargs = [dx, dx / dx_est, dx_est]
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
    # empty value
    xpos_predict_int, zp = None, None
    # loop from fpstart to fpend
    for zp in range(fpstart, fpend):
        # we take a trial solution between wave (from the theoretical FP
        #    solution) and the x position of measured peaks
        fitzp = mp.nanpolyfit(wave_fp[zp - ipeak], xpeak2, 3)
        # we predict an x position for the known U Ne lines
        xpos_predict = np.polyval(fitzp, une_lines)
        # deal with borders
        good = (xpos_predict > 0) & (xpos_predict < dim2)
        # doing this for order where there are no UNe lines
        if np.sum(good) == 0:
            WLOG(params, 'warning', textentry('40-014-00040', args=[order_num]))
            best_zp = fp_peak0_est - fpindex[0]
            break
        # mask
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
    wargs = [fp_peak0_est, fpindex[best_zp]]
    WLOG(params, '', textentry('40-014-00019', args=wargs))
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
        fit_err_xpix = mp.nanpolyfit(xpeak2[good], err_pix[good], 1)
        # get the deviation from error fit
        dev = err_pix - np.polyval(fit_err_xpix, xpeak2)
        # get the median absolute deviation
        absdev = mp.nanmedian(np.abs(dev))
        # very low thresholding values tend to clip valid points
        if absdev < absdev_threshold:
            absdev = absdev_threshold
        # get the max median asbolute deviation
        maxabsdev = mp.nanmax(np.abs(dev[good] / absdev))
        # iterate the good mask
        good &= np.abs(dev / absdev) < maxdev_threshold
    # -------------------------------------------------------------------------
    # then we perform a thresholding with a 5th order polynomial
    maxabsdev = np.inf
    # temp empty values
    fit_err_xpix, dev, absdev = None, None, None
    # loop around until we are better than threshold
    while maxabsdev > maxdev_threshold:
        # get the error fit (1st order polynomial)
        fit_err_xpix = mp.nanpolyfit(xpeak2[good], err_pix[good], 5)
        # get the deviation from error fit
        dev = err_pix - np.polyval(fit_err_xpix, xpeak2)
        # get the median absolute deviation
        absdev = mp.nanmedian(np.abs(dev))
        # very low thresholding values tend to clip valid points
        if absdev < absdev_threshold:
            absdev = absdev_threshold
        # get the max median asbolute deviation
        maxabsdev = mp.nanmax(np.abs(dev[good] / absdev))
        # iterate the good mask
        good &= np.abs(dev / absdev) < maxdev_threshold
    # -------------------------------------------------------------------------
    # this relation is the (sigma-clipped) fit between the xpix error
    #    and xpix along the order. The corresponding correction vector will
    #    be sent back to the dx grid
    corr_err_xpix = np.polyval(fit_err_xpix, np.arange(dim2))
    # -------------------------------------------------------------------------
    # get the statistics
    std_dev = mp.nanstd(dev)
    errpix_med = mp.nanmedian(err_pix)
    std_corr = mp.nanstd(corr_err_xpix[xpos_predict_int])
    corr_med = mp.nanmedian(corr_err_xpix[xpos_predict_int])
    cent_fit = mp.nanpolyfit(xpeak2[good], fpindex[zp - ipeak[good]], 5)
    num_fp_cent = np.polyval(cent_fit, dim2 // 2)
    # log the statistics
    wargs = [std_dev, absdev, errpix_med, std_corr, corr_med, num_fp_cent]
    WLOG(params, '', textentry('40-014-00020', args=wargs))
    # -------------------------------------------------------------------------
    # return loc
    return corr_err_xpix, xpeak2, peakval2, ewval2, err_pix, good

# =============================================================================
# End of code
# =============================================================================

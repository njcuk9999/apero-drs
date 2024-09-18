#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-07-2020-07-15 17:58

@author: cook
"""
import os
import warnings
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from astropy import constants as cc
from astropy import units as uu
from astropy.io import fits
from astropy.table import Table
from scipy.signal import savgol_filter

from apero.base import base
from apero.base import drs_base
from apero.core.constants import param_functions
from apero.core import lang
from apero.core import math as mp
from apero.core.base import drs_misc
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.io import drs_fits
from apero.io import drs_table
from apero.science import extract
from apero.science.calib import gen_calib
from apero.science.calib import wave
from apero.science.telluric import gen_tellu

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.template_tellu.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Astropy Time and Time Delta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# get param dict
ParamDict = param_functions.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsRecipe = drs_recipe.DrsRecipe
# get databases
CalibrationDatabase = drs_database.CalibrationDatabase
TelluricDatabase = drs_database.TelluricDatabase
# Get function string
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# General functions
# =============================================================================
def make_template_cubes(params: ParamDict, recipe: DrsRecipe,
                        filenames: Union[str, None], reffile: DrsFitsFile,
                        refprops: ParamDict, nprops: ParamDict,
                        fiber: str, qc_params: list, flag_hotstar: bool,
                        calibdb: Union[CalibrationDatabase, None] = None,
                        **kwargs) -> ParamDict:
    # set function mame
    func_name = display_func('make_template_cubes', __NAME__)
    # get parameters from params/kwargs
    qc_snr_order = pcheck(params, 'MKTEMPLATE_SNR_ORDER', 'qc_snr_order',
                          kwargs, func_name)
    e2ds_iterations = pcheck(params, 'MKTEMPLATE_E2DS_ITNUM', 's1d_iterations',
                             kwargs, func_name)
    e2ds_lowf_size = pcheck(params, 'MKTEMPLATE_E2DS_LOWF_SIZE',
                            's1d_lowf_size',
                            kwargs, func_name)
    min_berv_cov = pcheck(params, 'MKTEMPLATE_BERVCOR_QCMIN', 'min_berv_cov',
                          kwargs, func_name)
    core_snr = pcheck(params, 'MKTEMPLATE_BERVCOV_CSNR', 'core_snr', kwargs,
                      func_name)
    resolution = pcheck(params, 'MKTEMPLATE_BERVCOV_RES', 'resolution', kwargs,
                        func_name)
    debug_mode = pcheck(params, 'MKTEMPLATE_DEBUG_MODE', 'debug_mode', kwargs,
                        func_name)
    max_files = pcheck(params, 'MKTEMPLATE_MAX_OPEN_FILES', 'max_files',
                       kwargs, func_name)
    hotstar_kernel_velocity = pcheck(params, 'MKTEMPLATE_HOTSTAR_KER_VEL',
                                     'hotstar_ker_vel', kwargs, func_name)
    # get reference wave map
    mwavemap = refprops['WAVEMAP']
    # get the objname
    objname = reffile.get_hkey('KW_OBJNAME', dtype=str)
    # log that we are constructing the cubes
    WLOG(params, 'info', textentry('40-019-00027'))
    # ----------------------------------------------------------------------
    # Compile a median SNR for rejection of bad files
    # ----------------------------------------------------------------------
    # storage
    snr_all, infiles, vfilenames, vbasenames, midexps = [], [], [], [], []
    headers, basecolnames = [], []
    # choose snr to check
    snr_order = qc_snr_order
    # loop through files
    for it, filename in enumerate(filenames):
        # do not get duplicate files with same base name
        if os.path.basename(filename) in vbasenames:
            continue
        # get new copy of file definition - do not copy the data as it is
        #   already loaded in reffile (set to empty array for now)
        infile = reffile.newcopy(params=params, fiber=fiber,
                                 data=np.array([]))
        # set filename
        infile.set_filename(filename)
        # read header only
        infile.read_header()
        # get number of orders
        nbo = infile.get_hkey('KW_WAVE_NBO', dtype=int)
        # get snr
        snr = infile.get_hkey_1d('KW_EXT_SNR', nbo, dtype=float)
        # get times (for sorting)
        midexp = infile.get_hkey('KW_MID_OBS_TIME', dtype=float)
        # append filename
        vfilenames.append(filename)
        vbasenames.append(os.path.basename(filename))
        # append snr_all
        snr_all.append(snr[snr_order])
        # append times
        midexps.append(midexp)
        # append infiles
        infiles.append(infile)
        # append headers and column name for dict
        headers.append(infile.header)
        basecolnames.append(infile.basename.replace('.fits', ''))
    # ----------------------------------------------------------------------
    # Sort by mid observation time
    # ----------------------------------------------------------------------
    sortmask = np.argsort(midexps)
    snr_all = np.array(snr_all)[sortmask]
    midexps = np.array(midexps)[sortmask]
    vfilenames = np.array(vfilenames)[sortmask]
    infiles = np.array(infiles)[sortmask]
    # ----------------------------------------------------------------------
    # work our bad snr (less than half the median SNR)
    # ----------------------------------------------------------------------
    snr_thres = mp.nanmedian(snr_all) / 2.0
    bad_snr_objects = np.where(snr_all < snr_thres)[0]

    # ----------------------------------------------------------------------
    # Create combined header and combined table from input headers
    # ----------------------------------------------------------------------
    chout = drs_file.combine_headers(params, headers, basecolnames,
                                     math='median')
    template_header, _, template_combinetable = chout

    # ----------------------------------------------------------------------
    # Storage for cube table
    # ----------------------------------------------------------------------
    # compile base columns
    b_cols = template_bcols0(params)
    # ----------------------------------------------------------------------
    # Deal with binning up the template
    # ----------------------------------------------------------------------
    # make vfilenames an array
    vfilenames = np.array(vfilenames)
    vlen = len(vfilenames)

    # if we have more then the maximum number of files and we are not in
    #   debug mode we need to bin the files and do a median of a median for
    #   all files
    if vlen > max_files and not debug_mode:
        # get the number of bins to make
        nbins = int(np.sqrt(len(vfilenames)))
        # get the bin position for each file
        pbins = np.array(np.arange(vlen) // (nbins + 0.5)).astype(int)
    # otherwise each file is a "bin"
    else:
        # each bin has exactly one file
        pbins = np.arange(vlen).astype(int)
    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # get the unique bins
    upbins = np.unique(pbins)
    # set up flat size
    dims = [reffile.shape[0], reffile.shape[1], len(upbins)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_cube0 = np.repeat([np.nan], flatsize).reshape(*dims)
    # set up qc params
    qc_names, qc_values, qc_logic, qc_pass = qc_params
    fail_msgs = []
    # ----------------------------------------------------------------------
    # Loop through bins
    # ----------------------------------------------------------------------
    for p_it in upbins:
        # get a mask of files in this bin
        pmask = np.array(p_it == pbins)
        # ----------------------------------------------------------------------
        # Set up storage for cubes (NaN arrays) for binned median
        # ----------------------------------------------------------------------
        # set up flat size fpr the binned median
        dims_tmp = [reffile.shape[0], reffile.shape[1], np.sum(pmask)]
        flatsize_tmp = np.product(dims_tmp)
        # create NaN filled storage for the binned median
        big_cube_tmp = np.repeat([np.nan], flatsize_tmp).reshape(*dims_tmp)
        big_cube0_tmp = np.repeat([np.nan], flatsize_tmp).reshape(*dims_tmp)
        # ----------------------------------------------------------------------
        # Loop through input files (masked)
        # ----------------------------------------------------------------------
        for it, jt in enumerate(np.where(pmask)[0]):
            # get the infile for this iteration
            infile = infiles[jt]
            # log progress
            wargs = [reffile.name, jt + 1, len(pmask), p_it + 1,
                     len(upbins)]
            WLOG(params, '', params['DRS_HEADER'])
            WLOG(params, '', textentry('40-019-00028', args=wargs))
            WLOG(params, '', params['DRS_HEADER'])
            # ------------------------------------------------------------------
            # load the data for this iteration
            # ------------------------------------------------------------------
            # log progres: reading file: {0}
            wargs = [infile.filename]
            WLOG(params, '', textentry('40-019-00033', args=wargs))
            # read data
            infile.read_file(copy=True)
            # get image and set up shifted image
            image = np.array(infile.get_data(copy=True))
            # normalise image by the normalised blaze
            image2 = image / nprops['NBLAZE']
            # ------------------------------------------------------------------
            # Get barycentric corrections (BERV)
            # ------------------------------------------------------------------
            bprops = extract.get_berv(params, infile, log=False)
            # get berv from bprops
            berv = bprops['USE_BERV']
            # deal with bad berv (nan or None)
            if berv in [np.nan, None] or not isinstance(berv, (int, float)):
                eargs = [berv, func_name]
                WLOG(params, 'error', textentry('09-016-00004', args=eargs))
            # ------------------------------------------------------------------
            # load wavelength solution for this fiber
            # ------------------------------------------------------------------
            wprops = wave.get_wavesolution(params, recipe, infile=infile,
                                           fiber=fiber, database=calibdb)
            # get wavemap
            wavemap = wprops['WAVEMAP']
            # ------------------------------------------------------------------
            # populate the template file table
            # ------------------------------------------------------------------
            b_cols = template_bcols(params, b_cols, infile, jt, p_it, bprops,
                                    snr_all[jt], midexps[jt])

            # ------------------------------------------------------------------
            # skip if bad snr object
            # ------------------------------------------------------------------
            if jt in bad_snr_objects:
                # flag that we are not using this file
                b_cols['USED'].append(0)
                # log skipping
                wargs = [jt + 1, len(vfilenames), snr_order, snr_all[jt],
                         snr_thres]
                WLOG(params, 'warning', textentry('10-019-00006', args=wargs),
                     sublevel=4)
                # skip
                continue
            else:
                b_cols['USED'].append(1)
            # ------------------------------------------------------------------
            # Shift to correct berv
            # ------------------------------------------------------------------
            # get velocity shift due to berv
            dvshift = mp.relativistic_waveshift(berv, units='km/s')
            # shift the image
            simage = gen_tellu.wave_to_wave(params, image2, wavemap * dvshift,
                                            mwavemap)
            # ------------------------------------------------------------------
            # normalise by the median of each order
            # ------------------------------------------------------------------
            for order_num in range(reffile.shape[0]):
                # normalise the shifted data
                simage[order_num, :] /= mp.nanmedian(simage[order_num, :])
                # normalise the original data
                image2[order_num, :] /= mp.nanmedian(image2[order_num, :])

            # ------------------------------------------------------------------
            # add to cube storage
            # ------------------------------------------------------------------
            # add the shifted data to big_cube
            big_cube_tmp[:, :, it] = np.array(simage)
            # add the original data to big_cube0
            big_cube0_tmp[:, :, it] = np.array(image2)
            # -----------------------------------------------------------------
            # clean up
            del infile
            del simage
            del image2

        # ------------------------------------------------------------------
        # add to cube storage
        # ------------------------------------------------------------------
        # deal with having no bins (no extra median)
        if dims_tmp[-1] == 1:
            # add the shifted data to big_cube
            big_cube[:, :, p_it] = big_cube_tmp[:, :, 0]
            # add the original data to big_cube0
            big_cube0[:, :, p_it] = big_cube0_tmp[:, :, 0]

        else:
            # add the shifted data to big_cube
            big_cube[:, :, p_it] = mp.nanmedian(big_cube_tmp, axis=2)
            # add the original data to big_cube0
            big_cube0[:, :, p_it] = mp.nanmedian(big_cube0_tmp, axis=2)
        # -----------------------------------------------------------------
        # clean up
        del big_cube_tmp
        del big_cube0_tmp

    # ------------------------------------------------------------------
    # Deal with BERV coverage
    # ------------------------------------------------------------------
    # get the mask of only the used files
    used_mask = np.array(b_cols['USED']) == 1
    # get the berv coverage criteria
    bcovargs = [np.array(b_cols['BERV'])[used_mask],
                np.array(b_cols['SNR{0}'.format(snr_order)])[used_mask],
                core_snr, resolution, objname]
    bcout = calculate_berv_coverage(params, recipe, *bcovargs)
    berv_cov_table, berv_cov = bcout
    # quality control on coverage
    if berv_cov < min_berv_cov:
        # deal with insufficient berv coverage
        qc_names.append('BERV_COV')
        qc_values.append(berv_cov)
        qc_logic.append('BERV_COV < {0}'.format(min_berv_cov))
        qc_pass.append(0)
        fargs = [berv_cov, min_berv_cov]
        fail_msgs.append(textentry('10-019-00011', args=fargs))
    else:
        qc_names.append('BERV_COV')
        qc_values.append(berv_cov)
        qc_logic.append('BERV_COV < {0}'.format(min_berv_cov))
        qc_pass.append(1)

    # ------------------------------------------------------------------
    # Iterate until low frequency noise is gone
    # ------------------------------------------------------------------
    # deal with having no files
    if len(b_cols['RowNum']) == 0:
        # set big_cube_med to None
        median = None
        # deal with no median
        qc_names.append('HAS_ROWS')
        qc_values.append('False')
        qc_logic.append('HAS_ROWS==False')
        qc_pass.append(0)
        fail_msgs.append(textentry('10-019-00007', args=[objname]))

    else:
        # calculate the median of the big cube
        median = mp.nanmedian(big_cube, axis=2)
        # iterate until low frequency gone
        for iteration in range(e2ds_iterations):
            wargs = [iteration + 1, e2ds_iterations]
            # print which iteration we are on
            WLOG(params, '', textentry('40-019-00034', args=wargs))
            # loop each order
            for order_num in range(reffile.shape[0]):
                # loop through files and normalise by cube median
                for it in range(big_cube.shape[-1]):
                    # get the new ratio
                    ratio = big_cube[order_num, :, it] / median[order_num]
                    # apply median filtered ratio (low frequency removal)
                    lowpass = mp.medfilt_1d(ratio, e2ds_lowf_size)
                    big_cube[order_num, :, it] /= lowpass
            # calculate the median of the big cube
            median = mp.nanmedian(big_cube, axis=2)

            # TODO: only accept pixels where we have a fraction of values
            #    finite (i.e. if <30 obs need 50%  if >30 need 30)

        # ----------------------------------------------------------------------
        # deal with hot star (low pass filter)
        if flag_hotstar:
            # get the image pixel size
            psize = params['IMAGE_PIXEL_SIZE']
            # calculate hot star kernel size
            hotstar_kernel_size = hotstar_kernel_velocity / psize
            # must be an odd integer
            hotstar_kernel_size = int(np.round(hotstar_kernel_size / 2) * 2 + 1)
            # loop around each order and keep the low pass filter
            for order_num in range(reffile.shape[0]):
                median[order_num] = mp.lowpassfilter(median[order_num],
                                                     hotstar_kernel_size)
        # ----------------------------------------------------------------------
        # deal with quality control (passed)
        qc_names.append('HAS_ROWS')
        qc_values.append('True')
        qc_logic.append('HAS_ROWS==True')
        qc_pass.append(1)

    # ----------------------------------------------------------------------
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # ----------------------------------------------------------------------
    # setup output parameter dictionary
    props = ParamDict()
    props['BIG_CUBE'] = np.swapaxes(big_cube, 1, 2)
    props['BIG_CUBE0'] = np.swapaxes(big_cube0, 1, 2)
    props['BIG_COLS'] = b_cols
    props['MEDIAN'] = median
    props['QC_SNR_ORDER'] = qc_snr_order
    props['QC_SNR_THRES'] = snr_thres
    props['QC_SNR_THRES'] = snr_thres
    props['E2DS_ITERATIONS'] = e2ds_iterations
    props['E2DS_LOWF_SIZE'] = e2ds_lowf_size
    props['BERV_COVERAGE_VAL'] = berv_cov
    props['MIN_BERV_COVERAGE'] = min_berv_cov
    props['BERV_COVERAGE_SNR'] = core_snr
    props['BERV_COVERAGE_RES'] = resolution
    props['BERV_COVERAGE_TABLE'] = berv_cov_table
    props['QC_PARAMS'] = qc_params
    props['FAIL_MSG'] = fail_msgs
    props['TEMPLATE_HEADER'] = template_header
    props['HEADER_TABLE'] = template_combinetable
    # set sources
    keys = ['BIG_CUBE', 'BIG_CUBE0', 'BIG_COLS', 'MEDIAN', 'QC_SNR_ORDER',
            'QC_SNR_THRES', 'E2DS_ITERATIONS', 'E2DS_LOWF_SIZE',
            'BERV_COVERAGE_VAL', 'MIN_BERV_COVERAGE', 'BERV_COVERAGE_TABLE',
            'QC_PARAMS', 'FAIL_MSG', 'TEMPLATE_HEADER', 'HEADER_TABLE']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return outputs
    return props


def template_bcols0(params: ParamDict):
    """
    Construct the lists for each column in the template table

    :param params: ParamDict, parameter dictionary of constants
    :return:
    """
    # get parameters from params/kwargs
    snr_order = params['MKTEMPLATE_SNR_ORDER']
    b_cols = OrderedDict()
    b_cols['RowNum'] = []
    b_cols['Filename'], b_cols['OBJNAME'] = [], []
    b_cols['BERV'], b_cols['BJD'], b_cols['BERVMAX'] = [], [], []
    b_cols['SNR{0}'.format(snr_order)] = []
    b_cols['DPRTYPE'] = []
    b_cols['MidObsHuman'], b_cols['MidObsMJD'] = [], []
    b_cols['VERSION'], b_cols['Process_Date'], b_cols['DRS_Date'] = [], [], []
    b_cols['DARKFILE'], b_cols['BADFILE'], b_cols['BACKFILE'] = [], [], []
    b_cols['LOCOFILE'], b_cols['BLAZEFILE'], b_cols['FLATFILE'] = [], [], []
    b_cols['SHAPEXFILE'], b_cols['SHAPEYFILE'] = [], []
    b_cols['SHAPELFILE'], b_cols['THERMFILE'], b_cols['WAVEFILE'] = [], [], []
    b_cols['DARKTIME'], b_cols['BADTIME'], b_cols['BACKTIME'] = [], [], []
    b_cols['LOCOTIME'], b_cols['BLAZETIME'], b_cols['FLATTIME'] = [], [], []
    b_cols['SHAPEXTIME'], b_cols['SHAPEYTIME'] = [], []
    b_cols['SHAPELTIME'], b_cols['THERMTIME'], b_cols['WAVETIME'] = [], [], []
    b_cols['USED'], b_cols['TEMPLATE_BIN'] = [], []
    # return table dict
    return b_cols


def template_bcols(params: ParamDict, b_cols: Dict[str, list],
                   infile: DrsFitsFile,
                   rownum: int, templatenum: int,
                   bprops: ParamDict, snr: float, midexp: float
                   ) -> Dict[str, list]:
    """
    Fill the template columns for this observation

    :param params: ParamDict, parameter dictionary of constants
    :param b_cols: dictionary (template table dictionary) from
                   template_bcols0
    :param infile: DrsFitsFile, the input file that goes into the template
    :param rownum: int, The row in the table (time order)
    :param templatenum: int, the sub-median number (combined before final
                        median) we do a median of medians to avoid opening
                        too many files
    :param bprops: ParamDict, the BERV parameter dictionary
    :param snr: float, snr in selected order for this file
    :param midexp: float, the mid exposure time of the observation

    :return: dictionary (template table dictionary) updated with this
             observation
    """
    # get parameters from params/kwargs
    snr_order = params['MKTEMPLATE_SNR_ORDER']
    # get berv from bprops
    berv = bprops['USE_BERV']
    bjd = bprops['USE_BJD']
    bervmax = bprops['USE_BERV_MAX']
    # ------------------------------------------------------------------
    # append to table lists
    # ------------------------------------------------------------------
    # get string/file kwargs
    bkwargs = dict(dtype=str, required=False)
    # get drs date now
    drs_date_now = infile.get_hkey('KW_DRS_DATE_NOW', dtype=str)
    # add values
    b_cols['RowNum'].append(rownum)
    b_cols['Filename'].append(infile.basename)
    b_cols['OBJNAME'].append(infile.get_hkey('KW_OBJNAME', dtype=str))
    b_cols['BERV'].append(berv)
    b_cols['BJD'].append(bjd)
    b_cols['BERVMAX'].append(bervmax)
    b_cols['SNR{0}'.format(snr_order)].append(snr)
    b_cols['DPRTYPE'].append(infile.get_hkey('KW_DPRTYPE', dtype=str))
    b_cols['MidObsHuman'].append(Time(midexp, format='mjd').iso)
    b_cols['MidObsMJD'].append(midexp)
    b_cols['VERSION'].append(infile.get_hkey('KW_VERSION', dtype=str))
    b_cols['Process_Date'].append(drs_date_now)
    b_cols['DRS_Date'].append(infile.get_hkey('KW_DRS_DATE', dtype=str))
    # add dark file and time
    b_cols['DARKFILE'].append(infile.get_hkey('KW_CDBDARK', **bkwargs))
    b_cols['DARKTIME'].append(infile.get_hkey('KW_CDTDARK', **bkwargs))
    # add bad file and time
    b_cols['BADFILE'].append(infile.get_hkey('KW_CDBBAD', **bkwargs))
    b_cols['BADTIME'].append(infile.get_hkey('KW_CDTBAD', **bkwargs))
    # add back file and time
    b_cols['BACKFILE'].append(infile.get_hkey('KW_CDBBACK', **bkwargs))
    b_cols['BACKTIME'].append(infile.get_hkey('KW_CDTBACK', **bkwargs))
    # add loco file and time
    b_cols['LOCOFILE'].append(infile.get_hkey('KW_CDBLOCO', **bkwargs))
    b_cols['LOCOTIME'].append(infile.get_hkey('KW_CDTLOCO', **bkwargs))
    # add blaze file and time
    b_cols['BLAZEFILE'].append(infile.get_hkey('KW_CDBBLAZE', **bkwargs))
    b_cols['BLAZETIME'].append(infile.get_hkey('KW_CDTBLAZE', **bkwargs))
    # add flat file and time
    b_cols['FLATFILE'].append(infile.get_hkey('KW_CDBFLAT', **bkwargs))
    b_cols['FLATTIME'].append(infile.get_hkey('KW_CDTFLAT', **bkwargs))
    # add shape x file and time
    b_cols['SHAPEXFILE'].append(infile.get_hkey('KW_CDBSHAPEDX', **bkwargs))
    b_cols['SHAPEXTIME'].append(infile.get_hkey('KW_CDTSHAPEDX', **bkwargs))
    # add shape y file and time
    b_cols['SHAPEYFILE'].append(infile.get_hkey('KW_CDBSHAPEDY', **bkwargs))
    b_cols['SHAPEYTIME'].append(infile.get_hkey('KW_CDTSHAPEDY', **bkwargs))
    # add shape local file and time
    b_cols['SHAPELFILE'].append(infile.get_hkey('KW_CDBSHAPEL', **bkwargs))
    b_cols['SHAPELTIME'].append(infile.get_hkey('KW_CDTSHAPEL', **bkwargs))
    # add the thermal file
    cdb_thermal = infile.get_hkey('KW_CDBTHERMAL', **bkwargs)
    # can be None if no thermal correction done
    if cdb_thermal is None:
        cdb_thermal = 'None'
    b_cols['THERMFILE'].append(cdb_thermal)
    # add the thermal time (MJDMID)
    cdt_thermal = infile.get_hkey('KW_CDTTHERMAL', **bkwargs)
    # can be None if no thermal correction done
    if cdt_thermal is None:
        cdt_thermal = 0.0
    b_cols['THERMTIME'].append(cdt_thermal)
    # add wave file and time
    b_cols['WAVEFILE'].append(infile.get_hkey('KW_CDBWAVE', **bkwargs))
    b_cols['WAVETIME'].append(infile.get_hkey('KW_CDTWAVE', **bkwargs))
    # add the bin number for this file
    b_cols['TEMPLATE_BIN'].append(templatenum)
    # return table dict
    return b_cols


def make_1d_template_cube(params, recipe, filenames, reffile, fiber, header,
                          flag_hotstar: bool, calibdbm, **kwargs):
    # set function mame
    func_name = display_func('make_1d_template_cube', __NAME__)
    # get parameters from params/kwargs
    qc_snr_order = pcheck(params, 'MKTEMPLATE_SNR_ORDER', 'qc_snr_order',
                          kwargs, func_name)
    s1d_iterations = pcheck(params, 'MKTEMPLATE_S1D_ITNUM', 's1d_iterations',
                            kwargs, func_name)
    s1d_lowf_size = pcheck(params, 'MKTEMPLATE_S1D_LOWF_SIZE', 's1d_lowf_size',
                           kwargs, func_name)
    debug_mode = pcheck(params, 'MKTEMPLATE_DEBUG_MODE', 'debug_mode', kwargs,
                        func_name)
    max_files = pcheck(params, 'MKTEMPLATE_MAX_OPEN_FILES', 'max_files',
                       kwargs, func_name)
    hotstar_kernel_velocity = pcheck(params, 'MKTEMPLATE_HOTSTAR_KER_VEL',
                                     'hotstar_ker_vel', kwargs, func_name)
    # log that we are constructing the cubes
    WLOG(params, 'info', textentry('40-019-00027'))

    # read first file as reference
    reffile.set_filename(filenames[0])
    reffile.read_file()
    # get the reference wave map
    rwavemap = np.array(reffile.get_data()['wavelength'])
    # get s1d type
    if reffile.name == 'SC1D_W_FILE':
        s1d_type = 'S1DW'
    else:
        s1d_type = 'S1DV'
    # ----------------------------------------------------------------------
    # Compile a median SNR for rejection of bad files
    # ----------------------------------------------------------------------
    # storage
    snr_all, infiles, vfilenames, vbasenames, midexps = [], [], [], [], []
    # choose snr to check
    snr_order = qc_snr_order
    # loop through files
    for it, filename in enumerate(filenames):
        # do not get duplicate files with same base name
        if os.path.basename(filename) in vbasenames:
            continue
        # get new copy of file definition - do not copy the data as it is
        #   already loaded in reffile (set to empty Table for now)
        infile = reffile.newcopy(params=params, fiber=fiber,
                                 data=Table())
        # set filename
        infile.set_filename(filename)
        # read header only
        infile.read_header()
        # get number of orders
        nbo = infile.get_hkey('KW_WAVE_NBO', dtype=int)
        # get snr
        snr = infile.get_hkey_1d('KW_EXT_SNR', nbo, dtype=float)
        # get times (for sorting)
        midexp = infile.get_hkey('KW_MID_OBS_TIME', dtype=float)
        # append filename
        vfilenames.append(filename)
        vbasenames.append(os.path.basename(filename))
        # append snr_all
        snr_all.append(snr[snr_order])
        # append times
        midexps.append(midexp)
        # append infiles
        infiles.append(infile)
    # ----------------------------------------------------------------------
    # Sort by mid observation time
    # ----------------------------------------------------------------------
    sortmask = np.argsort(midexps)
    snr_all = np.array(snr_all)[sortmask]
    midexps = np.array(midexps)[sortmask]
    vfilenames = np.array(vfilenames)[sortmask]
    infiles = np.array(infiles)[sortmask]
    # ----------------------------------------------------------------------
    # work our bad snr (less than half the median SNR)
    # ----------------------------------------------------------------------
    snr_thres = mp.nanmedian(snr_all) / 2.0
    bad_snr_objects = np.where(snr_all < snr_thres)[0]
    # ----------------------------------------------------------------------
    # Storage for cube table
    # ----------------------------------------------------------------------
    # compile base columns
    b_cols = template_bcols0(params)
    # ----------------------------------------------------------------------
    # Deal with binning up the template
    # ----------------------------------------------------------------------
    # make vfilenames an array
    vfilenames = np.array(vfilenames)
    vlen = len(vfilenames)
    # if we have more then the maximum number of files and we are not in
    #   debug mode we need to bin the files and do a median of a median for
    #   all files
    if vlen > max_files and not debug_mode:
        # get the number of bins to make
        nbins = int(np.sqrt(len(vfilenames)))
        # get the bin position for each file
        pbins = np.array(np.arange(vlen) // (nbins + 0.5)).astype(int)
        # flag that we are binning
        flag_bin = True
    # otherwise each file is a "bin"
    else:
        # each bin has exactly one file
        pbins = np.arange(vlen).astype(int)
        # flag that we are not binning
        flag_bin = False
    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # get the unique bins
    upbins = np.unique(pbins)
    # set up flat size
    dims = [reffile.shape[0], len(upbins)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_errors = np.repeat([np.nan], flatsize).reshape(*dims)
    big_n = np.repeat([np.nan], flatsize).reshape(*dims)
    # get the 16th 50th and 84th percentile
    percentiles = [100 * (1 - mp.normal_fraction()) / 2, 50,
                   100 * (1 - (1 - mp.normal_fraction()) / 2)]
    # ----------------------------------------------------------------------
    # Loop through bins
    # ----------------------------------------------------------------------
    for p_it in upbins:
        # get a mask of files in this bin
        pmask = np.array(p_it == pbins)
        # ----------------------------------------------------------------------
        # Set up storage for cubes (NaN arrays) for binned median
        # ----------------------------------------------------------------------
        # set up flat size fpr the binned median
        dims_tmp = [reffile.shape[0], np.sum(pmask)]
        flatsize_tmp = np.product(dims_tmp)
        # create NaN filled storage for the binned median
        big_cube_tmp = np.repeat([np.nan], flatsize_tmp).reshape(*dims_tmp)
        # ----------------------------------------------------------------------
        # Loop through input files
        # ----------------------------------------------------------------------
        for it, jt in enumerate(np.where(pmask)[0]):
            # get the infile for this iteration
            infile = infiles[jt]
            # log progress
            wargs = [reffile.name, jt + 1, len(pmask), p_it + 1,
                     len(upbins)]
            WLOG(params, '', params['DRS_HEADER'])
            WLOG(params, '', textentry('40-019-00028', args=wargs))
            WLOG(params, '', params['DRS_HEADER'])
            # ------------------------------------------------------------------
            # load the data for this iteration
            # ------------------------------------------------------------------
            # log progres: reading file: {0}
            wargs = [infile.filename]
            WLOG(params, '', textentry('40-019-00033', args=wargs))

            # TODO: This is a test
            # manually open the file inside a with (we must close the fits file here)
            with fits.open(infile.filename) as fitsfile:
                image = np.array(fitsfile[1].data['flux'])
                wavemap = np.array(fitsfile[1].data['wavelength'])

            # TODO: This is the original code
            # read data
            # infile.read_file(copy=True)
            # # get image and set up shifted image
            # image = np.array(infile.get_data()['flux'])
            # wavemap = np.array(infile.get_data()['wavelength'])

            # normalise image by the normalised blaze
            image2 = image / mp.nanmedian(image)
            # ------------------------------------------------------------------
            # Get barycentric corrections (BERV)
            # ------------------------------------------------------------------
            bprops = extract.get_berv(params, infile, log=False)
            # get berv from bprops
            berv = bprops['USE_BERV']
            # deal with bad berv (nan or None)
            if berv in [np.nan, None] or not isinstance(berv, (int, float)):
                eargs = [berv, func_name]
                WLOG(params, 'error', textentry('09-016-00004', args=eargs))

            # ------------------------------------------------------------------
            # populate the template file table
            # ------------------------------------------------------------------
            b_cols = template_bcols(params, b_cols, infile, jt, p_it, bprops,
                                    snr_all[jt], midexps[jt])

            # ------------------------------------------------------------------
            # skip if bad snr object
            # ------------------------------------------------------------------
            if jt in bad_snr_objects:
                # flag that we are not using this file
                b_cols['USED'].append(0)
                # log skipping
                wargs = [jt + 1, len(vfilenames), snr_order, snr_all[jt],
                         snr_thres]
                WLOG(params, 'warning', textentry('10-019-00006', args=wargs),
                     sublevel=4)
                # skip
                continue
            else:
                b_cols['USED'].append(1)
            # ------------------------------------------------------------------
            # Shift to correct berv
            # ------------------------------------------------------------------
            # get velocity shift due to berv
            dvshift = mp.relativistic_waveshift(berv, units='km/s')
            # shift the image
            image3 = np.array([image2])
            wave3a = np.array([wavemap * dvshift])
            wave3b = np.array([rwavemap])
            simage = gen_tellu.wave_to_wave(params, image3, wave3a, wave3b)
            # ------------------------------------------------------------------
            # normalise by the median of each order
            # ------------------------------------------------------------------
            # normalise the shifted data
            simage /= mp.nanmedian(simage)
            # normalise the original data
            image2 /= mp.nanmedian(image2)
            # ------------------------------------------------------------------
            # add to cube storage
            # ------------------------------------------------------------------
            # add the shifted data to big_cube
            big_cube_tmp[:, it] = np.array(simage)
            # ------------------------------------------------------------------
            # clean up
            del infile
            del image
            del image2
            del image3
            del wave3a
            del wave3b
            del simage

        # ------------------------------------------------------------------
        # add to cube storage
        # ------------------------------------------------------------------
        # deal with having no bins (no extra median)
        if not flag_bin:
            # add the shifted data to big_cube
            big_cube[:, p_it] = big_cube_tmp[:, 0]
        else:
            # print progress
            WLOG(params, 'info', params['DRS_HEADER'])
            # TODO: Add to language database
            msg = 'Combining bin {0} of {1}'
            margs = [p_it + 1, len(upbins)]
            WLOG(params, '', msg.format(*margs))
            WLOG(params, '', params['DRS_HEADER'])
            # work out the median of this bin
            median = mp.nanmedian(big_cube_tmp, axis=1)
            # loop through files and normalise by cube median
            for it in range(big_cube_tmp.shape[-1]):
                # get the new ratio
                ratio = big_cube_tmp[:, it] / median
                # apply median filtered ratio (low frequency removal)
                big_cube_tmp[:, it] /= mp.medfilt_1d(ratio, s1d_lowf_size)
            # work out the percentiles at 16, 50 and 84
            with warnings.catch_warnings(record=True) as _:
                p16, p50, p84 = mp.nanpercentile(big_cube_tmp, percentiles,
                                                 axis=1)
                sig = (p84 - p16) / 2  # 1-sigma excursion
                # add the shifted data to big_cube
                big_n[:, p_it] = np.sum(np.isfinite(big_cube_tmp), axis=1)
                big_errors[:, p_it] = np.array(sig) / np.sqrt(big_n[:, p_it] - 1)
                big_cube[:, p_it] = np.array(p50)
            # ---------------------------------------------------------------
            # clean up
            del median
            del ratio
            del p16, p50, p84
            del sig
        # clean up
        del big_cube_tmp

    # ------------------------------------------------------------------
    # Iterate until low frequency noise is gone
    # ------------------------------------------------------------------
    # calculate the median of the big cube
    median = mp.nanmedian(big_cube, axis=1)
    # iterate until low frequency gone
    for iteration in range(s1d_iterations):
        wargs = [iteration + 1, s1d_iterations]
        # print which iteration we are on
        WLOG(params, '', textentry('40-019-00035', args=wargs))
        # loop through files and normalise by cube median
        for it in range(big_cube.shape[-1]):
            # get the new ratio
            ratio = big_cube[:, it] / median
            # apply median filtered ratio (low frequency removal)
            big_cube[:, it] /= mp.medfilt_1d(ratio, s1d_lowf_size)
        # calculate the median of the big cube
        median = mp.nanmedian(big_cube, axis=1)

    # ------------------------------------------------------------------
    # Combine eflux and number of valid pixels properly
    # ------------------------------------------------------------------
    # for case when bin
    if flag_bin:
        with warnings.catch_warnings(record=True) as _:
            eflux = (1 / np.sqrt(np.nansum(1 / big_errors ** 2, axis=1)))
            eflux[~np.isfinite(eflux)] = np.nan
            final_n = np.sum(big_n, axis=1)
    else:
        # print progress
        WLOG(params, '', params['DRS_HEADER'])
        # TODO: Add to language database
        msg = 'Combining big_cube error and number of valid pixels'
        WLOG(params, '', msg)
        WLOG(params, '', params['DRS_HEADER'])

        with warnings.catch_warnings(record=True) as _:
            p16, p50, p84 = mp.nanpercentile(big_cube, percentiles, axis=1)
            final_n = np.sum(np.isfinite(big_cube), axis=1)
            eflux = ((p84 - p16) / 2) / np.sqrt(final_n - 1)

    # ----------------------------------------------------------------------
    # deal with hot star low pass filter
    if flag_hotstar:
        # get the image pixel size
        psize = np.median(np.gradient(rwavemap) / rwavemap) * speed_of_light
        # calculate hot star kernel size
        hotstar_kernel_size = hotstar_kernel_velocity / psize
        # must be an odd integer
        hotstar_kernel_size = int(np.round(hotstar_kernel_size / 2) * 2 + 1)
        # loop around each order and keep the low pass filter
        median = mp.lowpassfilter(median, hotstar_kernel_size)
    # ----------------------------------------------------------------------
    # calculate residuals from the median
    residual_cube = np.array(big_cube)
    for it in range(big_cube.shape[-1]):
        residual_cube[:, it] -= median
    # calculate rms (median of residuals)
    norm_frac = mp.normal_fraction() * 100
    rms = mp.nanpercentile(np.abs(residual_cube), norm_frac, axis=1)

    # ----------------------------------------------------------------------
    # create the deconvolved template (used to correct finite resolution
    #   effects)
    # ----------------------------------------------------------------------
    # deal with hot star
    if flag_hotstar:
        deconv = np.array(median)
    else:
        deconv = create_deconvolved_template(params, recipe, rwavemap, median,
                                             header, s1d_type, calibdbm)
    # ----------------------------------------------------------------------
    # setup output parameter dictionary
    props = ParamDict()
    props['S1D_TYPE'] = s1d_type
    props['S1D_BIG_CUBE'] = big_cube.T
    props['S1D_BIG_COLS'] = b_cols
    props['S1D_WAVELENGTH'] = rwavemap
    props['S1D_MEDIAN'] = median
    props['S1D_RMS'] = rms
    props['S1D_EFLUX'] = eflux
    props['S1D_N_VALID'] = final_n
    props['QC_SNR_ORDER'] = qc_snr_order
    props['QC_SNR_THRES'] = snr_thres
    props['S1D_ITERATIONS'] = s1d_iterations
    props['S1D_LOWF_SIZE'] = s1d_lowf_size
    props['S1D_DECONV'] = deconv
    # set sources
    keys = ['S1D_TYPE', 'S1D_BIG_CUBE', 'S1D_BIG_COLS', 'S1D_MEDIAN',
            'S1D_WAVELENGTH', 'S1D_RMS', 'QC_SNR_ORDER', 'QC_SNR_THRES',
            'S1D_ITERATIONS', 'S1D_LOWF_SIZE', 'S1D_DECONV', 'S1D_EFLUX',
            'S1D_N_VALID']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return outputs
    return props


def list_current_templates(params: ParamDict,
                           telludb: Union[TelluricDatabase, None] = None,
                           all_objects: Union[List[str]] = None) -> np.array:
    """
    Get a list of current templates from the telluric database

    :param params: ParamDict, the parameter dictionary of constants
    :param telludb: None or telluric database (to save opening it more times
                    than needed)
    :param all_objects: list of strings, the list of all objects to filter
                        the list of templates by

    :return: list of current templates
    """
    # deal with no telluric database set up
    if telludb is None:
        telludb = TelluricDatabase(params)
    # load database (if not loaded)
    telludb.load_db()
    # get a list of all templates
    objnames = telludb.get_tellu_entry('OBJECT', key='TELLU_TEMP')
    # get unique objects
    uobjnames = np.array(list(set(objnames)))
    # deal with all objects filter
    if all_objects is not None:
        mask = np.in1d(uobjnames, all_objects)
        uobjnames = list(np.array(uobjnames)[mask])
    # return the unique set of object names
    return uobjnames


def calculate_berv_coverage(params: ParamDict, recipe: DrsRecipe,
                            berv: np.ndarray, snr: np.ndarray,
                            core_snr: float, resolution: float,
                            objname: str) -> Tuple[Table, float]:
    """
    Calculate the BERV coverage using the individual BERV measurements and
    the SNR

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: Recipe, DrsRecipe instance (the recipe using this function)
    :param berv: numpy array, the BERVs for each observation
    :param snr: numpy array, the SNR for each observation
    :param core_snr: float, the core SNR for weighting observations
    :param resolution: float, the rough resolution of the instrument in km/s
    :param objname: str, the object name for this target

    :return: tuple, 1. the table of berv coverage, 2. the berv coverage value
             the higher the better
    """
    # make sure berv and snr are numpy arrays
    berv = np.array(berv)
    snr = np.array(snr)
    # calculate a weight at a given SNR
    #  SNR = 100 is equivalent to a weight of 0.5 at core of line
    weight = (snr ** 2) / (core_snr ** 2)
    # get the min and max BERV
    minberv = mp.nanmin(berv)
    maxberv = mp.nanmax(berv)
    # limits include twice the resolution element
    low = minberv - (2 * resolution)
    high = maxberv + (2 * resolution)
    # get the BERV velocity range [km/s]
    velo_range = np.arange(low, high, 0.1)
    # get the equivalent width (FWHM) of the resolution
    ewid = resolution / mp.fwhm()
    # work out the lack of coverage at each velocity bin
    anticoverage = np.ones_like(velo_range)
    # loop around all data we have
    for row in range(len(snr)):
        # get this data points difference between itself and all velocity points
        diff = berv[row] - velo_range
        # work out coverage using a gaussian at each velocity bin
        gauss = np.exp(-0.5 * (diff ** 2) / (ewid ** 2))
        # work out anticoverage
        anticoverage = anticoverage * (1 - np.sqrt(gauss)) ** weight[row]
    # calculate coverage
    coverage = 1 - anticoverage
    # calculate berv coverage (integral of coverage) in km/s
    berv_cov = float(np.trapz(coverage, velo_range))
    # log coverage
    WLOG(params, 'info', textentry('40-019-00051', args=[berv_cov]))
    # plot coverage for this object
    recipe.plot('MKTEMP_BERV_COV', berv=velo_range, coverage=coverage,
                objname=objname, total=berv_cov)
    recipe.plot('SUM_MKTEMP_BERV_COV', berv=velo_range, coverage=coverage,
                objname=objname, total=berv_cov)
    # construct table
    columns = ['BERV', 'ANTICOVERAGE', 'COVERAGE']
    values = [velo_range, anticoverage, coverage]
    table = drs_table.make_table(columns, values,
                                 units=['km/s', None, None])
    # return table
    return table, berv_cov


def create_deconvolved_template(params: ParamDict, recipe: DrsRecipe,
                                wavemap: np.ndarray, flux0: np.ndarray,
                                header: drs_fits.Header,
                                s1d_type: str,
                                calibdbm: Optional[CalibrationDatabase] = None,
                                p99_itr_thres: Optional[float] = None,
                                p99_itr_max: Optional[int] = None
                                ) -> np.ndarray:
    """
    Deconvolves the s1d template (for finite resolution correction later)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
    :param wavemap: np.ndarray (1D), the s1d wavelength solution vector
    :param flux0: np.ndarray (1D), the s1d flux vector
    :param header: fits.Header, the header assoicated with the s1d
    :param s1d_type: str, the type of s1d (either S1DW or S1DV) this also
                     corresponds to the hdu extname in the res_e2ds file
    :param calibdbm: Calibration database (or None), if not passed will load
                     calibration database again
    :param p99_itr_thres: float, threshold for the Lucy-Richardson
                          deconvolution steps (max value of 99th percentile),
                          overrides MKTEMPLATE_DECONV_ITR_THRES in params if
                          set
    :param p99_itr_max: int, maximum number of iterations to run if the
                        iteration threshold is not met, overrides
                        MKTEMPLATE_DECONV_ITR_MAX in params if set.

    :return: np.ndarray, the deconvolved vector (same shape as flux)
    """
    # set function name
    func_name = display_func('create_deconvolved_template', __NAME__)
    # -------------------------------------------------------------------------
    # get parameters from params
    # -------------------------------------------------------------------------
    # Threshold for the Lucy-Richardson deconvolution steps. This is the maximum
    #    value of the 99th percentile of the feed-back term
    p99_iteration_threshold = pcheck(params, 'MKTEMPLATE_DECONV_ITR_THRES',
                                     func=func_name, override=p99_itr_thres)
    # Max number of iterations to run if the iteration threshold is not met
    niterations_max = pcheck(params, 'MKTEMPLATE_DECONV_ITR_MAX',
                             func=func_name, override=p99_itr_max)
    # -------------------------------------------------------------------------
    # get database if none
    if calibdbm is None:
        calibdbm = CalibrationDatabase(params)
        calibdbm.load_db()
    # -------------------------------------------------------------------------
    # keep track of valid pixels within template
    valid = np.isfinite(flux0)
    mask = np.ones_like(flux0)
    mask[~valid] = np.nan
    # spline NaNs with linear slopes in gaps. Avoids having any NaN in the
    # deconvolution
    spline_flux = mp.iuv_spline(wavemap[valid], flux0[valid], k=1, ext=3)
    flux = spline_flux(wavemap)
    # ----------------------------------------------------------------------
    # get the map of resolution in the s1d
    # ----------------------------------------------------------------------
    # get res_e2ds file instance
    res_e2ds = drs_file.get_file_definition(params, 'WAVEM_RES_E2DS',
                                            block_kind='red')
    # get calibration key
    key = res_e2ds.get_dbkey()
    # define the fiber to use (this is the one that was used in the wave ref
    #   code to make the resolution map)
    usefiber = params['WAVE_REF_FIBER']
    # load loco file
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, key, header, database=calibdbm,
                          fiber=usefiber, return_filename=True)
    # get properties from calibration file
    res_e2ds_path = cfile.filename
    # get the res table
    res_table = drs_table.read_table(params, res_e2ds_path, fmt='fits',
                                     hdu=s1d_type)
    # get the fwhm and expo from the table
    res_fwhm = np.array(res_table['flux_res_fwhm'])
    res_expo = np.array(res_table['flux_res_expo'])
    # -------------------------------------------------------------------------
    # print progress
    # TODO: Add to language database
    msg = 'Calculating deconvolution of template'
    WLOG(params, '', msg)
    # -------------------------------------------------------------------------
    # spline with slopes in domains that are not defined. We cannot have a NaN
    # in these maps.
    # -------------------------------------------------------------------------
    # pixel positions
    index = np.arange(len(res_fwhm))
    # valid map for FWHM
    fwhm_valid = np.isfinite(res_fwhm)
    # spline for FWHM
    spline_fwhm = mp.iuv_spline(index[fwhm_valid], res_fwhm[fwhm_valid],
                                k=1, ext=3)
    # map back onto original fwhm vector
    res_fwhm = spline_fwhm(index)
    # valid map for expo
    expo_valid = np.isfinite(res_expo)
    # spline for expo
    spline_expo = mp.iuv_spline(index[expo_valid], res_expo[expo_valid],
                                k=1, ext=3)
    # map back on to original expo vector
    res_expo = spline_expo(index)
    # -------------------------------------------------------------------------
    # calculate the first iteration in the Lucy-Richardson deconvolution
    deconv = gen_tellu.variable_res_conv(wavemap, flux, res_fwhm, res_expo)
    # reconvolve (should be very similar to the flux)
    reconv = gen_tellu.variable_res_conv(wavemap, deconv, res_fwhm,
                                         res_expo)
    # find the difference
    res = reconv - flux
    # -------------------------------------------------------------------------
    # find the incremental update to the deconvolved spectrum at each step of
    #    Lucy-Richardson
    p99 = np.inf
    # window that is 1.5 resolution element.
    savgol_window = int((np.ceil(np.nanmedian(res_fwhm) / 1.5) * 2) + 1)
    # start a counter
    iteration = 0
    # loop around until we reach our iteration threshold
    while (p99 > p99_iteration_threshold) and (iteration < niterations_max):
        # reconvolve the deconvolve spectrum
        reconv = gen_tellu.variable_res_conv(wavemap, deconv, res_fwhm,
                                             res_expo)
        # find the difference
        res = reconv - flux
        # we filter residuals such that we only keep derivatives of the 2 over
        # the width of a window that is 1.5 FWHM in size.
        res = savgol_filter(res, savgol_window, 2)
        # convolve the difference
        corr = gen_tellu.variable_res_conv(wavemap, res, res_fwhm, res_expo)
        # find the amplitude of the feedback term
        p99 = np.nanpercentile(corr[valid], 99)
        # update the deconvolved spectrum
        deconv = deconv - corr
        # update the iteration
        iteration += 1
        # log the progress
        # TODO: Add to language database
        msg = '\tIteration {0}. residual (99th percentile) = {1:.3e}'
        WLOG(params, '', msg.format(iteration, p99))
    # -------------------------------------------------------------------------
    # plot the deconv plot
    recipe.plot('MKTEMP_S1D_DECONV', wavemap=wavemap, flux=flux, mask=mask,
                deconv=deconv, reconv=reconv, res=res)
    # -------------------------------------------------------------------------
    # return the deconvolution vector
    return deconv


# =============================================================================
# QC and summary functions
# =============================================================================
def mk_template_qc(params, qc_params, fail_msg=None):
    # set passed variable and fail message list
    if fail_msg is None:
        fail_msg = []
    qc_names, qc_values, qc_logic, qc_pass = qc_params
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc params and passed
    return qc_params, passed


def mk_template_summary(recipe, params, cprops, template_file, qc_params):
    # count number of files
    nfiles = len(cprops['BIG_COLS']['RowNum'])
    temp_hash = template_file.get_hkey('KW_MKTEMP_HASH', dtype=str)
    berv_cov = template_file.get_hkey('KW_MKTEMP_BERV_COV')
    min_berv_cov = template_file.get_hkey('KW_MKTEMP_BERV_COV_MIN')
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_MKTEMP_SNR_ORDER', value=cprops['QC_SNR_ORDER'])
    recipe.plot.add_stat('KW_MKTEMP_SNR_THRES', value=cprops['QC_SNR_THRES'])
    recipe.plot.add_stat('KW_MKTEMP_NFILES', value=nfiles,
                         comment='Number of files')
    recipe.plot.add_stat('KW_MKTEMP_HASH', value=temp_hash)
    recipe.plot.add_stat('KW_MKTEMP_TIME', value=params['DATE_NOW'])
    recipe.plot.add_stat('KW_MKTEMP_BERV_COV', value=berv_cov)
    recipe.plot.add_stat('KW_MKTEMP_BERV_COV_MIN', value=min_berv_cov)
    # construct summary
    recipe.plot.summary_document(0, qc_params)


# =============================================================================
# Write functions
# =============================================================================
def gen_template_hash(string_text: str) -> str:
    # return hash
    return str(drs_base.generate_hash(string_text, 10))


def mk_template_write(params, recipe, infile, cprops, filetype,
                      fiber, wprops, qc_params):
    # get objname
    objname = infile.get_hkey('KW_OBJNAME', dtype=str)
    # construct suffix
    suffix = '_{0}_{1}_{2}'.format(objname, filetype.lower(), fiber)

    # get a mask of files used
    nused = np.array(cprops['BIG_COLS']['USED']) == 1
    # ------------------------------------------------------------------
    # Set up template big table
    # ------------------------------------------------------------------
    # get columns and values from cprops big column dictionary
    columns = list(cprops['BIG_COLS'].keys())
    values = list(cprops['BIG_COLS'].values())
    # construct table
    bigtable = drs_table.make_table(columns=columns, values=values)
    # make a hash so this template is unique
    template_hash = gen_template_hash(','.join(bigtable['Filename'][nused]))
    # get berv coverage table
    berv_cov_table = cprops['BERV_COVERAGE_TABLE']
    # ------------------------------------------------------------------
    # write the template file (TELLU_TEMP)
    # ------------------------------------------------------------------
    # get copy of instance of file
    template_file = recipe.outputs['TELLU_TEMP'].newcopy(params=params,
                                                         fiber=fiber)
    # construct the filename from file instance
    template_file.construct_filename(infile=infile, suffix=suffix)
    # ------------------------------------------------------------------
    # copy header from template
    template_file.copy_header(header=cprops['TEMPLATE_HEADER'])
    # copy keys from input file
    # template_file.copy_original_keys(infile, exclude_groups='wave')
    # add wave keys
    template_file = wave.add_wave_keys(template_file, wprops)
    # add core values (that should be in all headers)
    template_file.add_core_hkeys(params)
    # add qc parameters
    template_file.add_qckeys(qc_params)
    # deal with number of files total + used
    template_file.add_hkey('KW_MKTEMP_NFILES', value=len(nused))
    template_file.add_hkey('KW_MKTEMP_NFILES_USED', value=np.sum(nused))
    # add constants
    template_file.add_hkey('KW_MKTEMP_HASH', value=template_hash)
    template_file.add_hkey('KW_MKTEMP_TIME', value=params['DATE_NOW'])
    template_file.add_hkey('KW_MKTEMP_SNR_ORDER', value=cprops['QC_SNR_ORDER'])
    template_file.add_hkey('KW_MKTEMP_SNR_THRES', value=cprops['QC_SNR_THRES'])
    template_file.add_hkey('KW_MKTEMP_BERV_COV',
                           value=cprops['BERV_COVERAGE_VAL'])
    template_file.add_hkey('KW_MKTEMP_BERV_COV_MIN',
                           value=cprops['MIN_BERV_COVERAGE'])
    template_file.add_hkey('KW_MKTEMP_BERV_COV_SNR',
                           value=cprops['BERV_COVERAGE_SNR'])
    template_file.add_hkey('KW_MKTEMP_BERV_COV_RES',
                           value=cprops['BERV_COVERAGE_RES'])
    # set data
    template_file.data = cprops['MEDIAN']
    # log that we are saving s1d table
    WLOG(params, '', textentry('40-019-00029', args=[template_file.filename]))
    # define multi lists
    data_list = [bigtable, berv_cov_table, cprops['HEADER_TABLE']]
    datatype_list = ['table', 'table', 'table']
    name_list = ['TEMPLATE_TABLE', 'BERV_TABLE', 'COMBINE_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=template_file)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write multi
    template_file.write_multi(data_list=data_list, name_list=name_list,
                              datatype_list=datatype_list,
                              block_kind=recipe.out_block_str,
                              runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(template_file)

    # ------------------------------------------------------------------
    # write the big cube file
    # ------------------------------------------------------------------
    bigcubefile = recipe.outputs['TELLU_BIGCUBE'].newcopy(params=params,
                                                          fiber=fiber)
    # construct the filename from file instance
    bigcubefile.construct_filename(infile=infile, suffix=suffix)
    # copy header from corrected e2ds file
    bigcubefile.copy_hdict(template_file)
    bigcubefile.copy_header(template_file)
    # add output tag
    bigcubefile.add_hkey('KW_OUTPUT', value=bigcubefile.name)
    # set data
    bigcubefile.data = cprops['BIG_CUBE']
    # log that we are saving s1d table
    WLOG(params, '', textentry('40-019-00030', args=[bigcubefile.filename]))
    # define multi lists
    data_list = [bigtable, berv_cov_table]
    datatype_list = ['table', 'table']
    name_list = ['TEMPLATE_TABLE', 'BERV_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=bigcubefile)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write multi
    bigcubefile.write_multi(data_list=data_list, name_list=name_list,
                            datatype_list=datatype_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(bigcubefile)

    # ------------------------------------------------------------------
    # write the big cube 0 file
    # ------------------------------------------------------------------
    bigcubefile0 = recipe.outputs['TELLU_BIGCUBE0'].newcopy(params=params,
                                                            fiber=fiber)
    # construct the filename from file instance
    bigcubefile0.construct_filename(infile=infile, suffix=suffix)
    # copy header from corrected e2ds file
    bigcubefile0.copy_hdict(template_file)
    bigcubefile0.copy_header(template_file)
    # add output tag
    bigcubefile0.add_hkey('KW_OUTPUT', value=bigcubefile0.name)
    # set data
    bigcubefile0.data = cprops['BIG_CUBE0']
    # log that we are saving s1d table
    WLOG(params, '', textentry('40-019-00031', args=[bigcubefile0.filename]))
    # define multi lists
    data_list = [bigtable, berv_cov_table]
    datatype_list = ['table', 'table']
    name_list = ['TEMPLATE_TABLE', 'BERV_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=bigcubefile0)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write multi
    bigcubefile0.write_multi(data_list=data_list, name_list=name_list,
                             datatype_list=datatype_list,
                             block_kind=recipe.out_block_str,
                             runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(bigcubefile0)

    # return the template file
    return template_file


def mk_1d_template_write(params, recipe, infile, props, filetype, fiber,
                         wprops, qc_params, template_2d_file):
    # get objname
    objname = infile.get_hkey('KW_OBJNAME', dtype=str)
    # construct suffix
    suffix = '_{0}_{1}_{2}'.format(objname, filetype.lower(), fiber)
    # ------------------------------------------------------------------
    # Set up template big table
    # ------------------------------------------------------------------
    # get columns and values from cprops big column dictionary
    columns = list(props['S1D_BIG_COLS'].keys())
    values = list(props['S1D_BIG_COLS'].values())
    # construct table
    bigtable = drs_table.make_table(columns=columns, values=values)

    # ------------------------------------------------------------------
    # Set up template big table
    # ------------------------------------------------------------------
    s1dtable = Table()
    s1dtable['wavelength'] = props['S1D_WAVELENGTH']
    s1dtable['flux'] = props['S1D_MEDIAN']
    s1dtable['eflux'] = props['S1D_EFLUX']
    s1dtable['rms'] = props['S1D_RMS']
    s1dtable['deconv'] = props['S1D_DECONV']
    s1dtable['n_valid'] = props['S1D_N_VALID']
    # ------------------------------------------------------------------
    # write the s1d template file (TELLU_TEMP)
    # ------------------------------------------------------------------
    # deal with difference file type for s1dv and s1dw
    if props['S1D_TYPE'] == 'S1DV':
        drs_file_type = 'TELLU_TEMP_S1DV'
    else:
        drs_file_type = 'TELLU_TEMP_S1DW'
    # get copy of instance of file
    template_file = recipe.outputs[drs_file_type].newcopy(params=params,
                                                          fiber=fiber)
    # construct the filename from file instance
    template_file.construct_filename(infile=infile, suffix=suffix)
    # copy keys from input file
    template_file.copy_original_keys(infile, exclude_groups='wave')
    template_file.copy_hdict(template_2d_file)
    template_file.copy_header(template_2d_file)
    # add core values (that should be in all headers)
    template_file.add_core_hkeys(params)
    # add wave keys
    template_file = wave.add_wave_keys(template_file, wprops)
    # add qc parameters
    template_file.add_qckeys(qc_params)
    # set data
    template_file.data = s1dtable
    # log that we are saving s1d table
    WLOG(params, '', textentry('40-019-00036', args=[template_file.filename]))
    # define multi lists
    data_list = [bigtable]
    datatype_list = ['table']
    name_list = ['TEMPLATE_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=template_file)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write multi
    template_file.write_multi(data_list=data_list, name_list=name_list,
                              datatype_list=datatype_list,
                              block_kind=recipe.out_block_str,
                              runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(template_file)

    # ------------------------------------------------------------------
    # write the big cube file
    # ------------------------------------------------------------------
    bigcubefile = recipe.outputs['TELLU_BIGCUBE_S1D'].newcopy(params=params,
                                                              fiber=fiber)
    # construct the filename from file instance
    bigcubefile.construct_filename(infile=infile, suffix=suffix)
    # copy header from corrected e2ds file
    bigcubefile.copy_hdict(template_file)
    bigcubefile.copy_header(template_file)
    # add output tag
    bigcubefile.add_hkey('KW_OUTPUT', value=bigcubefile.name)
    # set data
    bigcubefile.data = props['S1D_BIG_CUBE']
    # log that we are saving s1d table
    WLOG(params, '', textentry('40-019-00037', args=[bigcubefile.filename]))
    # define multi lists
    data_list = [bigtable]
    datatype_list = ['table']
    name_list = ['TEMPLATE_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=bigcubefile)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write multi
    bigcubefile.write_multi(data_list=data_list, name_list=name_list,
                            datatype_list=datatype_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(bigcubefile)

    # return props
    props = ParamDict()
    props['S1DTABLE'] = s1dtable
    props['S1DFILE'] = template_file
    return props


# =============================================================================
# Worker functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

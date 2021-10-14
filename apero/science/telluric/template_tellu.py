#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-07-2020-07-15 17:58

@author: cook
"""
from astropy.table import Table
from collections import OrderedDict
import numpy as np
import os
from typing import Tuple, Union

from apero import lang
from apero.base import base
from apero.base import drs_base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.utils import drs_recipe
from apero.io import drs_table
from apero.science.calib import wave
from apero.science import extract
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
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsRecipe = drs_recipe.DrsRecipe
# get databases
CalibrationDatabase = drs_database.CalibrationDatabase
TelluricDatabase = drs_database.TelluricDatabase
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# General functions
# =============================================================================
def make_template_cubes(params: ParamDict, recipe: DrsRecipe,
                        filenames: Union[str, None], reffile: DrsFitsFile,
                        mprops: ParamDict, nprops: ParamDict,
                        fiber: str, qc_params: list,
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
    # get master wave map
    mwavemap = mprops['WAVEMAP']
    # get the objname
    objname = reffile.get_hkey('KW_OBJNAME', dtype=str)
    # log that we are constructing the cubes
    WLOG(params, 'info', textentry('40-019-00027'))
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
        # get new copy of file definition
        infile = reffile.newcopy(params=params, fiber=fiber)
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
    b_cols = OrderedDict()
    b_cols['RowNum'], b_cols['Filename'], b_cols['OBJNAME'] = [], [], []
    b_cols['BERV'], b_cols['BJD'], b_cols['BERVMAX'] = [], [], []
    b_cols['SNR{0}'.format(snr_order)] = []
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
    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # set up flat size
    dims = [reffile.shape[0], reffile.shape[1], len(vfilenames)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_cube0 = np.repeat([np.nan], flatsize).reshape(*dims)
    # set up qc params
    qc_names, qc_values, qc_logic, qc_pass = qc_params
    fail_msgs = []
    # ----------------------------------------------------------------------
    # Loop through input files
    # ----------------------------------------------------------------------
    for it, filename in enumerate(vfilenames):
        # get the infile for this iteration
        infile = infiles[it]
        # log progress
        wargs = [reffile.name, it + 1, len(vfilenames)]
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
        image = infile.get_data(copy=True)
        # normalise image by the normalised blaze
        image2 = image / nprops['NBLAZE']
        # get dprtype
        dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        bprops = extract.get_berv(params, infile, log=False)
        # get berv from bprops
        berv = bprops['USE_BERV']
        bjd = bprops['USE_BJD']
        bervmax = bprops['USE_BERV_MAX']
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
        # append to table lists
        # ------------------------------------------------------------------
        # get string/file kwargs
        bkwargs = dict(dtype=str, required=False)
        # get drs date now
        drs_date_now = infile.get_hkey('KW_DRS_DATE_NOW', dtype=str)
        # add values
        b_cols['RowNum'].append(it)
        b_cols['Filename'].append(infile.basename)
        b_cols['OBJNAME'].append(infile.get_hkey('KW_OBJNAME', dtype=str))
        b_cols['BERV'].append(berv)
        b_cols['BJD'].append(bjd)
        b_cols['BERVMAX'].append(bervmax)
        b_cols['SNR{0}'.format(snr_order)].append(snr_all[it])
        b_cols['MidObsHuman'].append(Time(midexps[it], format='mjd').iso)
        b_cols['MidObsMJD'].append(midexps[it])
        b_cols['VERSION'].append(infile.get_hkey('KW_VERSION', dtype=str))
        b_cols['Process_Date'].append(drs_date_now)
        b_cols['DRS_Date'].append(infile.get_hkey('KW_DRS_DATE', dtype=str))
        # add the dark file and dark file time (MJDMID)
        b_cols['DARKFILE'].append(infile.get_hkey('KW_CDBDARK', **bkwargs))
        b_cols['DARKTIME'].append(infile.get_hkey('KW_CDTDARK', **bkwargs))
        # add the bad file and bad file time (MJDMID)
        b_cols['BADFILE'].append(infile.get_hkey('KW_CDBBAD', **bkwargs))
        b_cols['BADTIME'].append(infile.get_hkey('KW_CDTBAD', **bkwargs))
        # add the background file and background file time (MJDMID)
        b_cols['BACKFILE'].append(infile.get_hkey('KW_CDBBACK', **bkwargs))
        b_cols['BACKTIME'].append(infile.get_hkey('KW_CDTBACK', **bkwargs))
        # add the loco file and loco time (MJDMID)
        b_cols['LOCOFILE'].append(infile.get_hkey('KW_CDBLOCO', **bkwargs))
        b_cols['LOCOTIME'].append(infile.get_hkey('KW_CDTLOCO', **bkwargs))
        # add the blaze file and blaze time (MJDMID)
        b_cols['BLAZEFILE'].append(infile.get_hkey('KW_CDBBLAZE', **bkwargs))
        b_cols['BLAZETIME'].append(infile.get_hkey('KW_CDTBLAZE', **bkwargs))
        # add the flat file and flat time (MJDMID)
        b_cols['FLATFILE'].append(infile.get_hkey('KW_CDBFLAT', **bkwargs))
        b_cols['FLATTIME'].append(infile.get_hkey('KW_CDTFLAT', **bkwargs))
        # add the shape x file and shape x time (MJDMID)
        b_cols['SHAPEXFILE'].append(infile.get_hkey('KW_CDBSHAPEDX', **bkwargs))
        b_cols['SHAPEXTIME'].append(infile.get_hkey('KW_CDTSHAPEDX', **bkwargs))
        # add the shape y file and shape y time (MJDMID)
        b_cols['SHAPEYFILE'].append(infile.get_hkey('KW_CDBSHAPEDY', **bkwargs))
        b_cols['SHAPEYTIME'].append(infile.get_hkey('KW_CDTSHAPEDY', **bkwargs))
        # add the shape local file and shape local time (MJDMID)
        b_cols['SHAPELFILE'].append(infile.get_hkey('KW_CDBSHAPEL', **bkwargs))
        b_cols['SHAPELTIME'].append(infile.get_hkey('KW_CDTSHAPEL', **bkwargs))
        # add the thermal file and thermal time (MJDMID)
        b_cols['THERMFILE'].append(infile.get_hkey('KW_CDTTHERMAL', **bkwargs))
        b_cols['THERMTIME'].append(infile.get_hkey('KW_CDTTHERMAL', **bkwargs))
        # add the wave file and wave time (MJDMID)
        b_cols['WAVEFILE'].append(os.path.basename(wprops['WAVEFILE']))
        b_cols['WAVETIME'].append(wprops['WAVETIME'])
        # remove the infile
        del infile
        # ------------------------------------------------------------------
        # skip if bad snr object
        # ------------------------------------------------------------------
        if it in bad_snr_objects:
            # log skipping
            wargs = [it + 1, len(vfilenames), snr_order, snr_all[it], snr_thres]
            WLOG(params, 'warning', textentry('10-019-00006', args=wargs),
                 sublevel=4)
            # skip
            continue

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
        big_cube[:, :, it] = simage
        # add the original data to big_cube0
        big_cube0[:, :, it] = image2

    # ------------------------------------------------------------------
    # Deal with BERV coverage
    # ------------------------------------------------------------------
    bcovargs = [b_cols['BERV'], b_cols['SNR{0}'.format(snr_order)],
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
                for it in range(len(vfilenames)):
                    # get the new ratio
                    ratio = big_cube[order_num, :, it] / median[order_num]
                    # apply median filtered ratio (low frequency removal)
                    lowpass = mp.medfilt_1d(ratio, e2ds_lowf_size)
                    big_cube[order_num, :, it] /= lowpass
            # calculate the median of the big cube
            median = mp.nanmedian(big_cube, axis=2)

            # TODO: only accept pixels where we have a fraction of values
            #    finite (i.e. if <30 obs need 50%  if >30 need 30)

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
    # set sources
    keys = ['BIG_CUBE', 'BIG_CUBE0', 'BIG_COLS', 'MEDIAN', 'QC_SNR_ORDER',
            'QC_SNR_THRES', 'E2DS_ITERATIONS', 'E2DS_LOWF_SIZE',
            'BERV_COVERAGE_VAL', 'MIN_BERV_COVERAGE', 'BERV_COVERAGE_TABLE',
            'QC_PARAMS']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return outputs
    return props


def make_1d_template_cube(params, recipe, filenames, reffile, fiber, **kwargs):
    # set function mame
    func_name = display_func('make_1d_template_cube', __NAME__)
    # get parameters from params/kwargs
    qc_snr_order = pcheck(params, 'MKTEMPLATE_SNR_ORDER', 'qc_snr_order',
                          kwargs, func_name)

    s1d_iterations = pcheck(params, 'MKTEMPLATE_S1D_ITNUM', 's1d_iterations',
                            kwargs, func_name)
    s1d_lowf_size = pcheck(params, 'MKTEMPLATE_S1D_LOWF_SIZE', 's1d_lowf_size',
                           kwargs, func_name)

    # log that we are constructing the cubes
    WLOG(params, 'info', textentry('40-019-00027'))

    # read first file as reference
    reffile.set_filename(filenames[0])
    reffile.read_file()
    # get the reference wave map
    rwavemap = np.array(reffile.get_data()['wavelength'])

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
        # get new copy of file definition
        infile = reffile.newcopy(params=params, fiber=fiber)
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
    b_cols = OrderedDict()
    b_cols['RowNum'], b_cols['Filename'], b_cols['OBJNAME'] = [], [], []
    b_cols['BERV'], b_cols['SNR{0}'.format(snr_order)] = [], []
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
    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # set up flat size
    dims = [reffile.shape[0], len(vfilenames)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    # ----------------------------------------------------------------------
    # Loop through input files
    # ----------------------------------------------------------------------
    for it, filename in enumerate(vfilenames):
        # get the infile for this iteration
        infile = infiles[it]
        # log progress
        wargs = [reffile.name, it + 1, len(vfilenames)]
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
        image = np.array(infile.get_data()['flux'])
        wavemap = np.array(infile.get_data()['wavelength'])

        # normalise image by the normalised blaze
        image2 = image / mp.nanmedian(image)

        # get dprtype
        dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
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
        # append to table lists
        # ------------------------------------------------------------------
        # get string/file kwargs
        bkwargs = dict(dtype=str, required=False)
        # get drs date now
        drs_date_now = infile.get_hkey('KW_DRS_DATE_NOW', dtype=str)
        # add values
        b_cols['RowNum'].append(it)
        b_cols['Filename'].append(infile.basename)
        b_cols['OBJNAME'].append(infile.get_hkey('KW_OBJNAME', dtype=str))
        b_cols['BERV'].append(berv)
        b_cols['SNR{0}'.format(snr_order)].append(snr_all[it])
        b_cols['MidObsHuman'].append(Time(midexps[it], format='mjd').iso)
        b_cols['MidObsMJD'].append(midexps[it])
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
        # add thermal file and time
        b_cols['THERMFILE'].append(infile.get_hkey('KW_CDBTHERMAL', **bkwargs))
        b_cols['THERMTIME'].append(infile.get_hkey('KW_CDTTHERMAL', **bkwargs))
        # add wave file and time
        b_cols['WAVEFILE'].append(infile.get_hkey('KW_CDBWAVE', **bkwargs))
        b_cols['WAVETIME'].append(infile.get_hkey('KW_CDTWAVE', **bkwargs))
        # ------------------------------------------------------------------
        # skip if bad snr object
        # ------------------------------------------------------------------
        if it in bad_snr_objects:
            # log skipping
            wargs = [it + 1, len(vfilenames), snr_order, snr_all[it], snr_thres]
            WLOG(params, 'warning', textentry('10-019-00006', args=wargs),
                 sublevel=4)
            # skip
            continue
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
        big_cube[:, it] = simage
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
        for it in range(len(vfilenames)):
            # get the new ratio
            ratio = big_cube[:, it] / median
            # apply median filtered ratio (low frequency removal)
            big_cube[:, it] /= mp.medfilt_1d(ratio, s1d_lowf_size)
        # calculate the median of the big cube
        median = mp.nanmedian(big_cube, axis=1)
    # ----------------------------------------------------------------------
    # calculate residuals from the median
    residual_cube = np.array(big_cube)
    for it in range(len(vfilenames)):
        residual_cube[:, it] -= median
    # calculate rms (median of residuals)
    rms = mp.nanmedian(np.abs(residual_cube), axis=1)
    # ----------------------------------------------------------------------
    # setup output parameter dictionary
    props = ParamDict()
    props['S1D_BIG_CUBE'] = big_cube.T
    props['S1D_BIG_COLS'] = b_cols
    props['S1D_WAVELENGTH'] = rwavemap
    props['S1D_MEDIAN'] = median
    props['S1D_RMS'] = rms
    props['QC_SNR_ORDER'] = qc_snr_order
    props['QC_SNR_THRES'] = snr_thres
    props['S1D_ITERATIONS'] = s1d_iterations
    props['S1D_LOWF_SIZE'] = s1d_lowf_size
    # set sources
    keys = ['S1D_BIG_CUBE', 'S1D_BIG_COLS', 'S1D_MEDIAN', 'S1D_WAVELENGTH',
            'S1D_RMS', 'QC_SNR_ORDER', 'QC_SNR_THRES', 'S1D_ITERATIONS',
            'S1D_LOWF_SIZE']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return outputs
    return props


def list_current_templates(params: ParamDict,
                           telludb: Union[TelluricDatabase, None] = None
                           ) -> np.array:
    """
    Get a list of current templates from the telluric database

    :param params: ParamDict, the parameter dictionary of constants
    :param telludb: None or telluric database (to save opening it more times
                    than needed)

    :return: list of current templates
    """
    # deal with no telluric database set up
    if telludb is None:
        telludb = TelluricDatabase(params)
    # load database (if not loaded)
    telludb.load_db()
    # get a list of all templates
    objnames = telludb.get_tellu_entry('OBJECT', key='TELLU_TEMP')
    # return the unique set of object names
    return np.unique(objnames)


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
    table = drs_table.make_table(params, columns, values,
                                 units=['km/s', None, None])
    # return table
    return table, berv_cov


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
    temp_hash = template_file.get_hkey('KW_MKTEMP_HASH')
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

    # ------------------------------------------------------------------
    # Set up template big table
    # ------------------------------------------------------------------
    # get columns and values from cprops big column dictionary
    columns = list(cprops['BIG_COLS'].keys())
    values = list(cprops['BIG_COLS'].values())
    # construct table
    bigtable = drs_table.make_table(params, columns=columns, values=values)
    # make a hash so this template is unique
    template_hash = gen_template_hash(','.join(cprops['BIG_COLS']['Filename']))
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
    # copy keys from input file
    template_file.copy_original_keys(infile, exclude_groups='wave')
    # add wave keys
    template_file = wave.add_wave_keys(template_file, wprops)
    # add version
    template_file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    template_file.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    template_file.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    template_file.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    template_file.add_hkey('KW_OUTPUT', value=template_file.name)
    # add qc parameters
    template_file.add_qckeys(qc_params)
    # add constants
    template_file.add_hkey('KW_MKTEMP_NFILES', value=len(bigtable))
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
    data_list = [bigtable, berv_cov_table]
    datatype_list = ['table', 'table']
    name_list = ['TEMPLATE_TABLE', 'BERV_TABLE']
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
    bigtable = drs_table.make_table(params, columns=columns, values=values)

    # ------------------------------------------------------------------
    # Set up template big table
    # ------------------------------------------------------------------
    s1dtable = Table()
    s1dtable['wavelength'] = props['S1D_WAVELENGTH']
    s1dtable['flux'] = props['S1D_MEDIAN']
    s1dtable['eflux'] = np.zeros_like(props['S1D_MEDIAN'])
    s1dtable['rms'] = props['S1D_RMS']

    # ------------------------------------------------------------------
    # write the s1d template file (TELLU_TEMP)
    # ------------------------------------------------------------------
    # get copy of instance of file
    template_file = recipe.outputs['TELLU_TEMP_S1D'].newcopy(params=params,
                                                             fiber=fiber)
    # construct the filename from file instance
    template_file.construct_filename(infile=infile, suffix=suffix)
    # copy keys from input file
    template_file.copy_original_keys(infile, exclude_groups='wave')
    template_file.copy_hdict(template_2d_file)
    template_file.copy_header(template_2d_file)
    # add wave keys
    template_file = wave.add_wave_keys(template_file, wprops)
    # add version
    template_file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    template_file.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    template_file.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    template_file.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    template_file.add_hkey('KW_OUTPUT', value=template_file.name)
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

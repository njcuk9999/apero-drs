#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-07-2020-07-15 17:58

@author: cook
"""
from astropy.table import Table
import numpy as np
import os
from collections import OrderedDict

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log
from apero.core.utils import drs_file
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
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# General functions
# =============================================================================
def make_template_cubes(params, recipe, filenames, reffile, mprops, nprops,
                        fiber, database=None, **kwargs):
    # set function mame
    func_name = display_func(params, 'make_template_cubes', __NAME__)
    # get parameters from params/kwargs
    qc_snr_order = pcheck(params, 'MKTEMPLATE_SNR_ORDER', 'qc_snr_order',
                          kwargs, func_name)
    e2ds_iterations = pcheck(params, 'MKTEMPLATE_E2DS_ITNUM', 's1d_iterations',
                             kwargs, func_name)
    e2ds_lowf_size = pcheck(params, 'MKTEMPLATE_E2DS_LOWF_SIZE',
                            's1d_lowf_size',
                            kwargs, func_name)
    # get master wave map
    mwavemap = mprops['WAVEMAP']
    # get the objname
    objname = reffile.get_key('KW_OBJNAME', dtype=str)
    # log that we are constructing the cubes
    WLOG(params, 'info', TextEntry('40-019-00027'))
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
        infile = reffile.newcopy(recipe=recipe, fiber=fiber)
        # set filename
        infile.set_filename(filename)
        # read header only
        infile.read_header()
        # get number of orders
        nbo = infile.get_key('KW_WAVE_NBO', dtype=int)
        # get snr
        snr = infile.read_header_key_1d_list('KW_EXT_SNR', nbo, dtype=float)
        # get times (for sorting)
        midexp = infile.get_key('KW_MID_OBS_TIME', dtype=float)
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
    b_cols['SHAPELFILE'], b_cols['THERMALFILE'], b_cols['WAVEFILE'] = [], [], []
    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # set up flat size
    dims = [reffile.shape[0], reffile.shape[1], len(vfilenames)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_cube0 = np.repeat([np.nan], flatsize).reshape(*dims)

    # ----------------------------------------------------------------------
    # Loop through input files
    # ----------------------------------------------------------------------
    for it, filename in enumerate(vfilenames):
        # get the infile for this iteration
        infile = infiles[it]
        # log progress
        wargs = [reffile.name, it + 1, len(vfilenames)]
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', TextEntry('40-019-00028', args=wargs))
        WLOG(params, '', params['DRS_HEADER'])
        # ------------------------------------------------------------------
        # load the data for this iteration
        # ------------------------------------------------------------------
        # log progres: reading file: {0}
        wargs = [infile.filename]
        WLOG(params, '', TextEntry('40-019-00033', args=wargs))
        # read data (but copy data)
        infile.read_file(copy=True)
        # get image and set up shifted image
        image = np.array(infile.data)
        # normalise image by the normalised blaze
        image2 = image / nprops['NBLAZE']
        # get dprtype
        dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        bprops = extract.get_berv(params, infile, dprtype=dprtype, log=False)
        # get berv from bprops
        berv = bprops['USE_BERV']
        # deal with bad berv (nan or None)
        if berv in [np.nan, None] or not isinstance(berv, (int, float)):
            eargs = [berv, func_name]
            WLOG(params, 'error', TextEntry('09-016-00004', args=eargs))
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        # ------------------------------------------------------------------
        wprops = wave.get_wavesolution(params, recipe, infile=infile,
                                       fiber=fiber, database=database)
        # get wavemap
        wavemap = wprops['WAVEMAP']
        # ------------------------------------------------------------------
        # append to table lists
        # ------------------------------------------------------------------
        # get string/file kwargs
        bkwargs = dict(dtype=str, required=False)
        # get drs date now
        drs_date_now = infile.get_key('KW_DRS_DATE_NOW', dtype=str)
        # add values
        b_cols['RowNum'].append(it)
        b_cols['Filename'].append(infile.basename)
        b_cols['OBJNAME'].append(infile.get_key('KW_OBJNAME', dtype=str))
        b_cols['BERV'].append(berv)
        b_cols['SNR{0}'.format(snr_order)].append(snr_all[it])
        b_cols['MidObsHuman'].append(Time(midexps[it], format='mjd').iso)
        b_cols['MidObsMJD'].append(midexps[it])
        b_cols['VERSION'].append(infile.get_key('KW_VERSION', dtype=str))
        b_cols['Process_Date'].append(drs_date_now)
        b_cols['DRS_Date'].append(infile.get_key('KW_DRS_DATE', dtype=str))
        b_cols['DARKFILE'].append(infile.get_key('KW_CDBDARK', **bkwargs))
        b_cols['BADFILE'].append(infile.get_key('KW_CDBBAD', **bkwargs))
        b_cols['BACKFILE'].append(infile.get_key('KW_CDBBACK', **bkwargs))
        b_cols['LOCOFILE'].append(infile.get_key('KW_CDBLOCO', **bkwargs))
        b_cols['BLAZEFILE'].append(infile.get_key('KW_CDBBLAZE', **bkwargs))
        b_cols['FLATFILE'].append(infile.get_key('KW_CDBFLAT', **bkwargs))
        b_cols['SHAPEXFILE'].append(infile.get_key('KW_CDBSHAPEDX', **bkwargs))
        b_cols['SHAPEYFILE'].append(infile.get_key('KW_CDBSHAPEDY', **bkwargs))
        b_cols['SHAPELFILE'].append(infile.get_key('KW_CDBSHAPEL', **bkwargs))
        b_cols['THERMALFILE'].append(infile.get_key('KW_CDBTHERMAL', **bkwargs))
        b_cols['WAVEFILE'].append(os.path.basename(wprops['WAVEFILE']))
        # remove the infile
        del infile
        # ------------------------------------------------------------------
        # skip if bad snr object
        # ------------------------------------------------------------------
        if it in bad_snr_objects:
            # log skipping
            wargs = [it + 1, len(vfilenames), snr_order, snr_all[it], snr_thres]
            WLOG(params, 'warning', TextEntry('10-019-00006', args=wargs))
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
    # Iterate until low frequency noise is gone
    # ------------------------------------------------------------------
    # deal with having no files
    if len(b_cols['RowNum']) == 0:
        # log that no files were found
        WLOG(params, 'warning', TextEntry('10-019-00007', args=[objname]))
        # set big_cube_med to None
        median = None
    else:
        # calculate the median of the big cube
        median = mp.nanmedian(big_cube, axis=2)
        # iterate until low frequency gone
        for iteration in range(e2ds_iterations):
            wargs = [iteration + 1, e2ds_iterations]
            # print which iteration we are on
            WLOG(params, '', TextEntry('40-019-00034', args=wargs))
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
    # set sources
    keys = ['BIG_CUBE', 'BIG_CUBE0', 'BIG_COLS', 'MEDIAN', 'QC_SNR_ORDER',
            'QC_SNR_THRES', 'E2DS_ITERATIONS', 'E2DS_LOWF_SIZE']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return outputs
    return props


def make_1d_template_cube(params, recipe, filenames, reffile, fiber, **kwargs):
    # set function mame
    func_name = display_func(params, 'make_1d_template_cube', __NAME__)
    # get parameters from params/kwargs
    qc_snr_order = pcheck(params, 'MKTEMPLATE_SNR_ORDER', 'qc_snr_order',
                          kwargs, func_name)

    s1d_iterations = pcheck(params, 'MKTEMPLATE_S1D_ITNUM', 's1d_iterations',
                            kwargs, func_name)
    s1d_lowf_size = pcheck(params, 'MKTEMPLATE_S1D_LOWF_SIZE', 's1d_lowf_size',
                           kwargs, func_name)

    # log that we are constructing the cubes
    WLOG(params, 'info', TextEntry('40-019-00027'))

    # read first file as reference
    reffile.set_filename(filenames[0])
    reffile.read_file()
    # get the reference wave map
    rwavemap = np.array(reffile.data['wavelength'])

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
        infile = reffile.newcopy(recipe=recipe, fiber=fiber)
        # set filename
        infile.set_filename(filename)
        # read header only
        infile.read_header(ext=1)
        # get number of orders
        nbo = infile.get_key('KW_WAVE_NBO', dtype=int)
        # get snr
        snr = infile.read_header_key_1d_list('KW_EXT_SNR', nbo, dtype=float)
        # get times (for sorting)
        midexp = infile.get_key('KW_MID_OBS_TIME', dtype=float)
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
    b_cols['SHAPELFILE'], b_cols['THERMALFILE'], b_cols['WAVEFILE'] = [], [], []
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
        WLOG(params, '', TextEntry('40-019-00028', args=wargs))
        WLOG(params, '', params['DRS_HEADER'])
        # ------------------------------------------------------------------
        # load the data for this iteration
        # ------------------------------------------------------------------
        # log progres: reading file: {0}
        wargs = [infile.filename]
        WLOG(params, '', TextEntry('40-019-00033', args=wargs))
        # read data
        infile.read_file()
        # get image and set up shifted image
        image = np.array(infile.data['flux'])
        wavemap = np.array(infile.data['wavelength'])

        # normalise image by the normalised blaze
        image2 = image / mp.nanmedian(image)

        # get dprtype
        dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        bprops = extract.get_berv(params, infile, dprtype=dprtype, log=False)
        # get berv from bprops
        berv = bprops['USE_BERV']
        # deal with bad berv (nan or None)
        if berv in [np.nan, None] or not isinstance(berv, (int, float)):
            eargs = [berv, func_name]
            WLOG(params, 'error', TextEntry('09-016-00004', args=eargs))
        # ------------------------------------------------------------------
        # append to table lists
        # ------------------------------------------------------------------
        # get string/file kwargs
        bkwargs = dict(dtype=str, required=False)
        # get drs date now
        drs_date_now = infile.get_key('KW_DRS_DATE_NOW', dtype=str)
        # add values
        b_cols['RowNum'].append(it)
        b_cols['Filename'].append(infile.basename)
        b_cols['OBJNAME'].append(infile.get_key('KW_OBJNAME', dtype=str))
        b_cols['BERV'].append(berv)
        b_cols['SNR{0}'.format(snr_order)].append(snr_all[it])
        b_cols['MidObsHuman'].append(Time(midexps[it], format='mjd').iso)
        b_cols['MidObsMJD'].append(midexps[it])
        b_cols['VERSION'].append(infile.get_key('KW_VERSION', dtype=str))
        b_cols['Process_Date'].append(drs_date_now)
        b_cols['DRS_Date'].append(infile.get_key('KW_DRS_DATE', dtype=str))
        b_cols['DARKFILE'].append(infile.get_key('KW_CDBDARK', **bkwargs))
        b_cols['BADFILE'].append(infile.get_key('KW_CDBBAD', **bkwargs))
        b_cols['BACKFILE'].append(infile.get_key('KW_CDBBACK', **bkwargs))
        b_cols['LOCOFILE'].append(infile.get_key('KW_CDBLOCO', **bkwargs))
        b_cols['BLAZEFILE'].append(infile.get_key('KW_CDBBLAZE', **bkwargs))
        b_cols['FLATFILE'].append(infile.get_key('KW_CDBFLAT', **bkwargs))
        b_cols['SHAPEXFILE'].append(infile.get_key('KW_CDBSHAPEDX', **bkwargs))
        b_cols['SHAPEYFILE'].append(infile.get_key('KW_CDBSHAPEDY', **bkwargs))
        b_cols['SHAPELFILE'].append(infile.get_key('KW_CDBSHAPEL', **bkwargs))
        b_cols['THERMALFILE'].append(infile.get_key('KW_CDBTHERMAL', **bkwargs))
        b_cols['WAVEFILE'].append(os.path.basename(filename))
        # ------------------------------------------------------------------
        # skip if bad snr object
        # ------------------------------------------------------------------
        if it in bad_snr_objects:
            # log skipping
            wargs = [it + 1, len(vfilenames), snr_order, snr_all[it], snr_thres]
            WLOG(params, 'warning', TextEntry('10-019-00006', args=wargs))
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
        WLOG(params, '', TextEntry('40-019-00035', args=wargs))
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


# =============================================================================
# QC and summary functions
# =============================================================================
def mk_template_qc(params):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], [],
    qc_logic, qc_pass = [], []

    # add to qc header lists
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc params and passed
    return qc_params, passed


def mk_template_summary(recipe, params, cprops, qc_params):
    # count number of files
    nfiles = len(cprops['BIG_COLS']['RowNum'])
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])

    recipe.plot.add_stat('KW_MKTEMP_SNR_ORDER', value=cprops['QC_SNR_ORDER'])
    recipe.plot.add_stat('KW_MKTEMP_SNR_THRES', value=cprops['QC_SNR_THRES'])
    recipe.plot.add_stat('NTMASTER', value=nfiles,
                         comment='Number files in template')
    # construct summary
    recipe.plot.summary_document(0, qc_params)


# =============================================================================
# Write functions
# =============================================================================
def mk_template_write(params, recipe, infile, cprops, filetype,
                      fiber, wprops, qc_params):
    # get objname
    objname = infile.get_key('KW_OBJNAME', dtype=str)
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

    # ------------------------------------------------------------------
    # write the template file (TELLU_TEMP)
    # ------------------------------------------------------------------
    # get copy of instance of file
    template_file = recipe.outputs['TELLU_TEMP'].newcopy(recipe=recipe,
                                                         fiber=fiber)
    # construct the filename from file instance
    template_file.construct_filename(params, infile=infile, suffix=suffix)
    # ------------------------------------------------------------------
    # copy keys from input file
    template_file.copy_original_keys(infile, exclude_groups='wave')
    # add wave keys
    template_file = wave.add_wave_keys(params, template_file, wprops)
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
    template_file.add_hkey('KW_MKTEMP_SNR_ORDER', value=cprops['QC_SNR_ORDER'])
    template_file.add_hkey('KW_MKTEMP_SNR_THRES', value=cprops['QC_SNR_THRES'])
    # set data
    template_file.data = cprops['MEDIAN']
    # log that we are saving s1d table
    WLOG(params, '', TextEntry('40-019-00029', args=[template_file.filename]))
    # write multi
    template_file.write_multi(data_list=[bigtable], datatype_list=['table'])
    # add to output files (for indexing)
    recipe.add_output_file(template_file)

    # ------------------------------------------------------------------
    # write the big cube file
    # ------------------------------------------------------------------
    bigcubefile = recipe.outputs['TELLU_BIGCUBE'].newcopy(recipe=recipe,
                                                          fiber=fiber)
    # construct the filename from file instance
    bigcubefile.construct_filename(params, infile=infile, suffix=suffix)
    # copy header from corrected e2ds file
    bigcubefile.copy_hdict(bigcubefile)
    # add output tag
    bigcubefile.add_hkey('KW_OUTPUT', value=bigcubefile.name)
    # set data
    bigcubefile.data = cprops['BIG_CUBE']
    # log that we are saving s1d table
    WLOG(params, '', TextEntry('40-019-00030', args=[bigcubefile.filename]))
    # write multi
    bigcubefile.write_multi(data_list=[bigtable], datatype_list=['table'])
    # add to output files (for indexing)
    recipe.add_output_file(bigcubefile)

    # ------------------------------------------------------------------
    # write the big cube 0 file
    # ------------------------------------------------------------------
    bigcubefile0 = recipe.outputs['TELLU_BIGCUBE0'].newcopy(recipe=recipe,
                                                            fiber=fiber)
    # construct the filename from file instance
    bigcubefile0.construct_filename(params, infile=infile, suffix=suffix)
    # copy header from corrected e2ds file
    bigcubefile0.copy_hdict(bigcubefile0)
    # add output tag
    bigcubefile0.add_hkey('KW_OUTPUT', value=bigcubefile0.name)
    # set data
    bigcubefile0.data = cprops['BIG_CUBE0']
    # log that we are saving s1d table
    WLOG(params, '', TextEntry('40-019-00031', args=[bigcubefile0.filename]))
    # write multi
    bigcubefile0.write_multi(data_list=[bigtable], datatype_list=['table'])
    # add to output files (for indexing)
    recipe.add_output_file(bigcubefile0)

    # return the template file
    return template_file


def mk_1d_template_write(params, recipe, infile, props, filetype, fiber,
                         wprops, qc_params):
    # get objname
    objname = infile.get_key('KW_OBJNAME', dtype=str)
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
    template_file = recipe.outputs['TELLU_TEMP_S1D'].newcopy(recipe=recipe,
                                                             fiber=fiber)
    # construct the filename from file instance
    template_file.construct_filename(params, infile=infile, suffix=suffix)
    # copy keys from input file
    template_file.copy_original_keys(infile, exclude_groups='wave')
    # add wave keys
    template_file = wave.add_wave_keys(params, template_file, wprops)
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
    template_file.add_hkey('KW_MKTEMP_SNR_ORDER', value=props['QC_SNR_ORDER'])
    template_file.add_hkey('KW_MKTEMP_SNR_THRES', value=props['QC_SNR_THRES'])
    # set data
    template_file.data = s1dtable
    # log that we are saving s1d table
    WLOG(params, '', TextEntry('40-019-00036', args=[template_file.filename]))
    # write multi
    template_file.write_multi(data_list=[bigtable], datatype_list=['table'])
    # add to output files (for indexing)
    recipe.add_output_file(template_file)

    # ------------------------------------------------------------------
    # write the big cube file
    # ------------------------------------------------------------------
    bigcubefile = recipe.outputs['TELLU_BIGCUBE_S1D'].newcopy(recipe=recipe,
                                                              fiber=fiber)
    # construct the filename from file instance
    bigcubefile.construct_filename(params, infile=infile, suffix=suffix)
    # copy header from corrected e2ds file
    bigcubefile.copy_hdict(bigcubefile)
    # add output tag
    bigcubefile.add_hkey('KW_OUTPUT', value=bigcubefile.name)
    # set data
    bigcubefile.data = props['S1D_BIG_CUBE']
    # log that we are saving s1d table
    WLOG(params, '', TextEntry('40-019-00037', args=[bigcubefile.filename]))
    # write multi
    bigcubefile.write_multi(data_list=[bigtable], datatype_list=['table'])
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

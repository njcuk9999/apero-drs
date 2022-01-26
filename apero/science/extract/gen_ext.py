#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-09 at 13:42

@author: cook
"""
import numpy as np
from astropy.table import Table
from astropy import constants as cc
from astropy import units as uu
import os
from typing import Union
import warnings

from apero.base import base
from apero.core.core import drs_text
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_recipe
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.science.calib import shape
from apero.science.calib import wave
from apero.science.calib import gen_calib
from apero.science.extract import berv


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extraction.gen_ext.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsNpyFile = drs_file.DrsNpyFile
DrsRecipe = drs_recipe.DrsRecipe
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# -----------------------------------------------------------------------------
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light_kms = cc.c.to(uu.km / uu.s).value
# Get function string
display_func = drs_log.display_func


# =============================================================================
# Define general functions
# =============================================================================
def order_profiles(params, recipe, infile, fibertypes, sprops,
                   filenames=None, database=None):
    func_name = __NAME__ + '.order_profiles()'
    # filenames must be a dictionary
    if not isinstance(filenames, dict):
        filenames = dict()
        for fiber in fibertypes:
            filenames[fiber] = 'None'
    # ------------------------------------------------------------------------
    # get generic drs file types required
    opfile = drs_file.get_file_definition(params, 'LOC_ORDERP',
                                          block_kind='red')
    ospfile = drs_file.get_file_definition(params, 'ORDERP_STRAIGHT',
                                           block_kind='red')
    slocalfile = drs_file.get_file_definition(params, 'SHAPEL',
                                              block_kind='red')
    # ------------------------------------------------------------------------
    # get header from infile
    header = infile.get_header()
    # ----------------------------------------------------------------------
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------------
    # storage for order profiles
    orderprofiles = dict()
    orderfiles = dict()
    ordertimes = dict()
    # loop around fibers
    for fiber in fibertypes:
        # log progress (straightening orderp)
        WLOG(params, 'info', textentry('40-016-00003', args=[fiber]))
        # ------------------------------------------------------------------
        # get the order profile filename
        filename = filenames[fiber]
        # ------------------------------------------------------------------
        # deal with filename from user entry
        cond1 = not drs_text.null_text(filename, ['None'])
        cond2 = os.path.exists(filename)
        if cond1 and cond2:
            # construct order profile straightened
            orderpsfile = ospfile.newcopy(params=params, fiber=fiber)
            orderpsfile.set_filename(filename)
        else:
            # infile of opderpsfile should be a shape local file
            oinfile = slocalfile.newcopy(params=params, fiber=fiber)
            oinfile.set_filename(sprops['SHAPELFILE'])
            # construct order profile straightened
            orderpsfile = ospfile.newcopy(params=params, fiber=fiber)
            orderpsfile.construct_filename(infile=oinfile)
        # ------------------------------------------------------------------
        # check if temporary file exists
        if orderpsfile.file_exists():
            # load the numpy temporary file
            #    Note: NpyFitsFile needs arguments params!
            if isinstance(orderpsfile, DrsFitsFile):
                # log progress (read file)
                wargs = [orderpsfile.filename]
                WLOG(params, '', textentry('40-013-00023', args=wargs))
                # read npy file
                orderpsfile.read_file()
            else:
                eargs = [orderpsfile.__str__(), func_name]
                WLOG(params, 'error', textentry('00-016-00023', args=eargs))
            # push data into orderp
            orderp = orderpsfile.get_data()
            orderpfilename = orderpsfile.filename
            # time is the MJDMID of the order profile
            orderptime = orderpsfile.get_hkey('KW_MID_OBS_TIME')
        # if straighted order profile doesn't exist and we have no filename
        #   defined then we need to figure out the order profile file -
        #   load it and then save it as a straighted version (orderpsfile)
        else:
            # get key
            key = opfile.get_dbkey()
            # get pseudo constants
            pconst = constants.pload()
            # get fiber to use for ORDERPFILE (i.e. AB,A,B --> AB  and C-->C)
            usefiber = pconst.FIBER_LOC_TYPES(fiber)
            # get the order profile filename
            cfile = gen_calib.CalibFile()
            cfile.load_calib_file(params, key, header, filename=filename,
                                  userinputkey='ORDERPFILE', database=calibdbm,
                                  fiber=usefiber, return_filename=True)
            # get properties from calibration file
            filename, orderptime = cfile.filename, cfile.mjdmid
            # load order profile
            orderp, orderhdr = drs_fits.readfits(params, filename, getdata=True,
                                                 gethdr=True)
            orderpfilename = filename
            # straighten orders
            orderp = shape.ea_transform(params, orderp, sprops['SHAPEL'],
                                        dxmap=sprops['SHAPEX'],
                                        dymap=sprops['SHAPEY'],)
            # copy full header from order profile
            orderpsfile.copy_header(header=orderhdr)
            orderpsfile.add_hkey('KW_CDBSHAPEL', value=sprops['SHAPELFILE'])
            orderpsfile.add_hkey('KW_CDTSHAPEL', value=sprops['SHAPELTIME'])
            orderpsfile.add_hkey('KW_CDBSHAPEDX', value=sprops['SHAPEXFILE'])
            orderpsfile.add_hkey('KW_CDTSHAPEDX', value=sprops['SHAPEXTIME'])
            orderpsfile.add_hkey('KW_CDBSHAPEDY', value=sprops['SHAPEYFILE'])
            orderpsfile.add_hkey('KW_CDTSHAPEDY', value=sprops['SHAPEYTIME'])
            # push into orderpsfile
            orderpsfile.data = orderp
            # log progress (saving to file)
            wargs = [orderpsfile.filename]
            WLOG(params, '', textentry('40-013-00024', args=wargs))
            # save for use later (as .npy)
            orderpsfile.write_file(block_kind=recipe.out_block_str,
                                   runstring=recipe.runstring)
        # store in storage dictionary
        orderprofiles[fiber] = orderp
        orderfiles[fiber] = orderpfilename
        ordertimes[fiber] = orderptime
    # return order profiles
    return orderprofiles, orderfiles, ordertimes


def ref_fplines(params, recipe, e2dsfile, wavemap, fiber, database=None,
                **kwargs):
    # set up function name
    func_name = display_func('ref_fplines', __NAME__)
    # get constant from params
    allowtypes = pcheck(params, 'WAVE_FP_DPRLIST', 'fptypes', kwargs, func_name,
                        mapf='list')
    # get dprtype
    dprtype = e2dsfile.get_hkey('KW_DPRTYPE', dtype=str)
    # get psuedo constants
    pconst = constants.pload()
    sfibers, rfiber = pconst.FIBER_KINDS()
    # ----------------------------------------------------------------------
    # deal with fiber being the reference fiber
    if fiber != rfiber:
        # Skipping FPLINES (Fiber = {0})'
        WLOG(params, 'debug', textentry('90-016-00003', args=[fiber]))
        return None
    # ----------------------------------------------------------------------
    # deal with allowed dprtypes
    if dprtype not in allowtypes:
        # Skipping FPLINES (DPRTYPE = {0})
        WLOG(params, 'debug', textentry('90-016-000034', args=[dprtype]))
        return None
    # ----------------------------------------------------------------------
    # get master hc lines and fp lines from calibDB
    wout = wave.get_wavelines(params, fiber, infile=e2dsfile,
                              database=database)
    mhclines, mhclsource, mfplines, mfplsource = wout
    # deal with no fplines found
    if mfplines is None:
        return None
    # ----------------------------------------------------------------------
    # generate the fp reference lines
    fpargs = dict(e2dsfile=e2dsfile, wavemap=wavemap, fplines=mfplines)
    rfpl = wave.calc_wave_lines(params, recipe, **fpargs)
    # ----------------------------------------------------------------------
    # return fp lines for e2ds file
    return rfpl


# =============================================================================
# Define s1d functions
# =============================================================================
def e2ds_to_s1d(params: ParamDict, recipe: DrsRecipe,  wavemap: np.ndarray,
                e2ds: np.ndarray,  blaze: np.ndarray,
                fiber: Union[str, None] = None, wgrid: str = 'wave',
                s1dkind: Union[str, None] = None,
                e2dserr: Union[np.ndarray, None] = None,
                **kwargs):
    func_name = __NAME__ + '.e2ds_to_s1d()'
    # get parameters from p
    wavestart = pcheck(params, 'EXT_S1D_WAVESTART', 'wavestart', kwargs,
                       func_name)
    waveend = pcheck(params, 'EXT_S1D_WAVEEND', 'waveend', kwargs,
                     func_name)
    binwave = pcheck(params, 'EXT_S1D_BIN_UWAVE', 'binwave', kwargs,
                     func_name)
    binvelo = pcheck(params, 'EXT_S1D_BIN_UVELO', 'binvelo', kwargs,
                     func_name)
    smooth_size = pcheck(params, 'EXT_S1D_EDGE_SMOOTH_SIZE', 'smooth_size',
                         kwargs, func_name)
    blazethres = pcheck(params, 'TELLU_CUT_BLAZE_NORM', 'blazethres', kwargs,
                        func_name)
    # -------------------------------------------------------------------------
    # get size from e2ds
    nord, npix = e2ds.shape
    # -------------------------------------------------------------------------
    # deal with no errors
    if e2dserr is None:
        # just have a line
        e2dserr = np.tile(np.arange(npix), nord).reshape((nord, npix))
        has_errors = False
    else:
        has_errors = True

    # -------------------------------------------------------------------------
    # log progress: calculating s1d (wavegrid)
    WLOG(params, '', textentry('40-016-00009', args=[wgrid]))
    # -------------------------------------------------------------------------
    # Decide on output wavelength grid
    # -------------------------------------------------------------------------
    if wgrid == 'wave':
        wavegrid = np.arange(wavestart, waveend + binwave / 2.0, binwave)
    else:
        # velocity grid in round numbers of m / s
        magicgrid = mp.get_magic_grid(wavestart, waveend, binvelo * 1000)
        # we want wave grid in
        wavegrid = np.array(magicgrid)
    # -------------------------------------------------------------------------
    # define a smooth transition mask at the edges of the image
    # this ensures that the s1d has no discontinuity when going from one order
    # to the next. We define a scale for this mask
    # smoothing scale
    # -------------------------------------------------------------------------
    # define a kernal that goes from -3 to +3 smooth_sizes of the mask
    xker = np.arange(-smooth_size * 3, smooth_size * 3, 1)
    ker = np.exp(-0.5 * (xker / smooth_size) ** 2)
    # set up the edge vector
    edges = np.ones(npix, dtype=bool)
    # set edges of the image to 0 so that  we get a sloping weight
    edges[:int(3 * smooth_size)] = False
    edges[-int(3 * smooth_size):] = False
    # define the weighting for the edges (slopevector)
    slopevector = np.zeros_like(blaze)
    # for each order find the sloping weight vector
    for order_num in range(nord):
        # get the blaze for this order
        oblaze = np.array(blaze[order_num])
        # find the valid pixels
        cond1 = np.isfinite(oblaze) & np.isfinite(e2ds[order_num])
        with warnings.catch_warnings(record=True) as _:
            cond2 = oblaze > (blazethres * mp.nanmax(oblaze))
        valid = cond1 & cond2 & edges
        # convolve with the edge kernel
        oweight = np.convolve(valid, ker, mode='same')
        # normalise to the maximum
        with warnings.catch_warnings(record=True) as _:
            oweight = oweight - mp.nanmin(oweight)
            oweight = oweight / mp.nanmax(oweight)
        # append to sloping vector storage
        slopevector[order_num] = oweight

    # multiple the spectrum and blaze by the sloping vector
    sblaze = np.array(blaze) * slopevector
    se2ds = np.array(e2ds) * slopevector
    se2dserr = np.array(e2dserr) * slopevector
    # -------------------------------------------------------------------------
    # Perform a weighted mean of overlapping orders
    # by performing a spline of both the blaze and the spectrum
    # -------------------------------------------------------------------------
    out_spec = np.zeros_like(wavegrid)
    out_spec_err = np.zeros_like(wavegrid)
    weight = np.zeros_like(wavegrid)
    # loop around all orders
    for order_num in range(nord):
        # get wavelength mask - if there are NaNs in wavemap have to deal with
        #    them (happens at least for polar)
        wavemask = np.isfinite(wavemap[order_num])
        # identify the valid pixels
        valid = np.isfinite(se2ds[order_num]) & np.isfinite(sblaze[order_num])
        valid &= wavemask
        # if we have no valid points we need to skip
        if np.sum(valid) == 0:
            continue
        # get this orders vectors
        owave = wavemap[order_num]
        oe2ds = se2ds[order_num, valid]
        oe2dserr = se2dserr[order_num, valid]
        oblaze = sblaze[order_num, valid]
        # create the splines for this order
        spline_sp = mp.iuv_spline(owave[valid], oe2ds, k=5, ext=1)
        spline_bl = mp.iuv_spline(owave[valid], oblaze, k=1, ext=1)
        spline_sperr = mp.iuv_spline(owave[valid], oe2dserr, k=5, ext=1)
        # valid must be cast as float for splining
        valid_float = valid.astype(float)
        # we mask pixels that are neighbours to a NaN.
        valid_float = np.convolve(valid_float, np.ones(3) / 3.0, mode='same')
        spline_valid = mp.iuv_spline(owave[wavemask], valid_float[wavemask],
                                     k=1, ext=1)
        # can only spline in domain of the wave
        useful_range = (wavegrid > mp.nanmin(owave[valid]))
        useful_range &= (wavegrid < mp.nanmax(owave[valid]))
        # finding pixels where we have immediate neighbours that are
        #   considered valid in the spline (to avoid interpolating over large
        #   gaps in validity)
        maskvalid = np.zeros_like(wavegrid, dtype=bool)
        maskvalid[useful_range] = spline_valid(wavegrid[useful_range]) > 0.9
        useful_range &= maskvalid
        # get splines and add to outputs
        weight[useful_range] += spline_bl(wavegrid[useful_range])
        out_spec[useful_range] += spline_sp(wavegrid[useful_range])
        out_spec_err[useful_range] += spline_sperr(wavegrid[useful_range])
    # need to deal with zero weight --> set them to NaNs
    zeroweights = weight == 0
    weight[zeroweights] = np.nan

    # plot the s1d weight/before/after plot
    recipe.plot('EXTRACT_S1D_WEIGHT', params=params, wave=wavegrid,
                flux=out_spec, weight=weight, kind=wgrid, fiber=fiber,
                stype=s1dkind)
    # work out the weighted spectrum
    with warnings.catch_warnings(record=True) as _:
        w_out_spec = out_spec / weight
        w_out_spec_err = out_spec_err / weight

    # deal with errors - set them to zero (spline here is meaningless)
    if not has_errors:
        w_out_spec_err = np.zeros_like(w_out_spec)

    # construct the s1d table (for output)
    s1dtable = Table()
    s1dtable['wavelength'] = wavegrid
    s1dtable['flux'] = w_out_spec
    s1dtable['eflux'] = w_out_spec_err
    s1dtable['weight'] = weight

    # set up return dictionary
    props = ParamDict()
    # add data
    props['WAVEGRID'] = wavegrid
    props['S1D'] = w_out_spec
    props['S1D_ERROR'] = w_out_spec_err
    props['WEIGHT'] = weight
    # add astropy table
    props['S1DTABLE'] = s1dtable
    # add constants
    props['WAVESTART'] = wavestart
    props['WAVEEND'] = waveend
    props['WAVEKIND'] = wgrid
    if wgrid == 'wave':
        props['BIN_WAVE'] = binwave
        props['BIN_VELO'] = 'None'
    else:
        props['BIN_WAVE'] = 'None'
        props['BIN_VELO'] = binvelo
    props['SMOOTH_SIZE'] = smooth_size
    props['BLAZE_THRES'] = blazethres
    # add source
    keys = ['WAVEGRID', 'S1D', 'WEIGHT', 'S1D_ERROR', 'S1DTABLE',
            'WAVESTART', 'WAVEEND', 'WAVEKIND', 'BIN_WAVE',
            'BIN_VELO', 'SMOOTH_SIZE', 'BLAZE_THRES']
    props.set_sources(keys, func_name)
    # return properties
    return props


def add_s1d_keys(infile, props):
    infile.add_hkey('KW_S1D_WAVESTART', value=props['WAVESTART'])
    infile.add_hkey('KW_S1D_WAVEEND', value=props['WAVEEND'])
    infile.add_hkey('KW_S1D_KIND', value=props['WAVEKIND'])
    infile.add_hkey('KW_S1D_BWAVE', value=props['BIN_WAVE'])
    infile.add_hkey('KW_S1D_BVELO', value=props['BIN_VELO'])
    infile.add_hkey('KW_S1D_SMOOTH', value=props['SMOOTH_SIZE'])
    infile.add_hkey('KW_S1D_BLAZET', value=props['BLAZE_THRES'])
    return infile


# =============================================================================
# writing and qc functions
# =============================================================================
def qc_extraction(params, eprops):
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], [],
    qc_logic, qc_pass = [], []
    # --------------------------------------------------------------
    # if array is completely NaNs it shouldn't pass
    if np.sum(np.isfinite(eprops['E2DS'])) == 0:
        # add failed message to fail message list
        fail_msg.append(textentry('40-016-00008'))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append('NaN')
    qc_names.append('image')
    qc_logic.append('image is all NaN')
    # --------------------------------------------------------------
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
    # return
    return qc_params, passed


def write_extraction_files(params, recipe, infile, rawfiles, combine, fiber,
                           props, lprops, wprops, eprops, bprops,
                           swprops, svprops, sprops, fbprops, qc_params):
    # ----------------------------------------------------------------------
    # Store E2DS in file
    # ----------------------------------------------------------------------
    # get a new copy of the e2ds file
    e2dsfile = recipe.outputs['E2DS_FILE'].newcopy(params=params,
                                                   fiber=fiber)
    # construct the filename from file instance
    e2dsfile.construct_filename(infile=infile)
    # define header keys for output file
    # copy keys from input file (excluding loc)
    e2dsfile.copy_original_keys(infile, exclude_groups=['loc'])
    # add version
    e2dsfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    e2dsfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    e2dsfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    e2dsfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    e2dsfile.add_hkey('KW_OUTPUT', value=e2dsfile.name)
    e2dsfile.add_hkey('KW_FIBER', value=fiber)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    e2dsfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add infiles to outfile
    e2dsfile.infiles = list(hfiles)
    # add the calibration files use
    e2dsfile = gen_calib.add_calibs_to_header(e2dsfile, props)
    # ----------------------------------------------------------------------
    # add the order profile used
    e2dsfile.add_hkey('KW_CDBORDP', value=lprops['ORDERPFILE'])
    e2dsfile.add_hkey('KW_CDTORDP', value=lprops['ORDERPTIME'])
    # add the localisation file used
    e2dsfile.add_hkey('KW_CDBLOCO', value=lprops['LOCOFILE'])
    e2dsfile.add_hkey('KW_CDTLOCO', value=lprops['LOCOTIME'])
    # add the shape local file used
    e2dsfile.add_hkey('KW_CDBSHAPEL', value=sprops['SHAPELFILE'])
    e2dsfile.add_hkey('KW_CDTSHAPEL', value=sprops['SHAPELTIME'])
    # add the shape dx file used
    e2dsfile.add_hkey('KW_CDBSHAPEDX', value=sprops['SHAPEXFILE'])
    e2dsfile.add_hkey('KW_CDTSHAPEDX', value=sprops['SHAPEXTIME'])
    # add the shape dy file used
    e2dsfile.add_hkey('KW_CDBSHAPEDY', value=sprops['SHAPEYFILE'])
    e2dsfile.add_hkey('KW_CDTSHAPEDY', value=sprops['SHAPEYTIME'])
    # add the flat file used
    e2dsfile.add_hkey('KW_CDBFLAT', value=fbprops['FLATFILE'])
    e2dsfile.add_hkey('KW_CDTFLAT', value=fbprops['FLATTIME'])
    # add the blaze file used
    e2dsfile.add_hkey('KW_CDBBLAZE', value=fbprops['BLAZEFILE'])
    e2dsfile.add_hkey('KW_CDTBLAZE', value=fbprops['BLAZETIME'])
    # add the thermal file used
    if 'THERMALFILE' in eprops:
        e2dsfile.add_hkey('KW_CDBTHERMAL', value=eprops['THERMALFILE'])
        e2dsfile.add_hkey('KW_CDTTHERMAL', value=eprops['THERMALTIME'])
        e2dsfile.add_hkey('KW_THERM_RATIO_1', value=eprops['THERMAL_RATIO1'])
        e2dsfile.add_hkey('KW_THERM_RATIO_2', value=eprops['THERMAL_RATIO2'])
        e2dsfile.add_hkey('KW_THERM_RATIO_U',
                          value=eprops['THERMAL_RATIO_USED'])

    # add the wave file used
    e2dsfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    e2dsfile.add_hkey('KW_CDTWAVE', value=wprops['WAVETIME'])
    # add the leak master calibration file used
    e2dsfile.add_hkey('KW_CDBLEAKM', value=eprops['LEAKM_FILE'])
    e2dsfile.add_hkey('KW_CDTLEAKM', value=eprops['LEAKM_TIME'])
    e2dsfile.add_hkey('KW_CDBLEAKR', value=eprops['LEAKM_REFFILE'])
    e2dsfile.add_hkey('KW_CDTLEAKR', value=eprops['LEAKM_REFTIME'])
    # additional calibration keys
    if 'FIBERTYPE' in eprops:
        e2dsfile.add_hkey('KW_C_FTYPE', value=eprops['FIBERTYPE'])
    # ----------------------------------------------------------------------
    # add qc parameters
    e2dsfile.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # add shape transform parameters
    e2dsfile.add_hkey('KW_SHAPE_DX', value=sprops['SHAPEL'][0])
    e2dsfile.add_hkey('KW_SHAPE_DY', value=sprops['SHAPEL'][1])
    e2dsfile.add_hkey('KW_SHAPE_A', value=sprops['SHAPEL'][2])
    e2dsfile.add_hkey('KW_SHAPE_B', value=sprops['SHAPEL'][3])
    e2dsfile.add_hkey('KW_SHAPE_C', value=sprops['SHAPEL'][4])
    e2dsfile.add_hkey('KW_SHAPE_D', value=sprops['SHAPEL'][5])
    # ----------------------------------------------------------------------
    # add extraction type (does not change for future files)
    e2dsfile.add_hkey('KW_EXT_TYPE', value=e2dsfile.name)
    # add SNR parameters to header
    e2dsfile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                         dim1name='order')
    # add start and end extraction order used
    e2dsfile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
    e2dsfile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
    # add extraction ranges used
    e2dsfile.add_hkey('KW_EXT_RANGE1', value=eprops['RANGE1'])
    e2dsfile.add_hkey('KW_EXT_RANGE2', value=eprops['RANGE2'])
    # add cosmic parameters used
    e2dsfile.add_hkey('KW_COSMIC', value=eprops['COSMIC'])
    e2dsfile.add_hkey('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'])
    e2dsfile.add_hkey('KW_COSMIC_THRES',
                      value=eprops['COSMIC_THRESHOLD'])
    # add saturation parameters used
    e2dsfile.add_hkey('KW_SAT_QC', value=eprops['SAT_LEVEL'])
    with warnings.catch_warnings(record=True) as _:
        max_sat_level = mp.nanmax(eprops['FLUX_VAL'])
    e2dsfile.add_hkey('KW_SAT_LEVEL', value=max_sat_level)
    # ----------------------------------------------------------------------
    # add loco parameters (using locofile)
    locofile = lprops['LOCOOBJECT']
    e2dsfile.copy_original_keys(locofile, group='loc')
    # ----------------------------------------------------------------------
    # add wave keys
    e2dsfile = wave.add_wave_keys(e2dsfile, wprops)
    # ----------------------------------------------------------------------
    # add berv properties to header
    e2dsfile = berv.add_berv_keys(params, e2dsfile, bprops)
    # add whether we corrected FP leakage
    if eprops['LEAK_CORRECTED']:
        e2dsfile.add_hkey('KW_LEAK_CORR', value=1)
    else:
        e2dsfile.add_hkey('KW_LEAK_CORR', value=0)
    # set leak corr header keys to add
    keys = ['KW_LEAK_BP_U', 'KW_LEAK_NP_U', 'KW_LEAK_LP_U', 'KW_LEAK_UP_U',
            'KW_LEAK_BADR_U']
    values = ['LEAK_BCKGRD_PERCENTILE_USED', 'LEAK_NORM_PERCENTILE_USED',
              'LEAK_LOW_PERCENTILE_USED', 'LEAK_HIGH_PERCENTILE_USED',
              'LEAK_BAD_RATIO_OFFSET_USED']
    # loop around leak keys to add
    for it in range(len(keys)):
        e2dsfile.add_hkey(keys[it], value=eprops[values[it]])
    # ----------------------------------------------------------------------
    # copy data
    e2dsfile.data = eprops['E2DS']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsfile.filename]
    WLOG(params, '', textentry('40-016-00005', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    e2dsfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(e2dsfile)
    # ----------------------------------------------------------------------
    # Store E2DSFF in file
    # ----------------------------------------------------------------------
    # get a new copy of the e2dsff file
    e2dsfffile = recipe.outputs['E2DSFF_FILE'].newcopy(params=params,
                                                       fiber=fiber)
    # construct the filename from file instance
    e2dsfffile.construct_filename(infile=infile)
    # copy header from e2dsff file
    e2dsfffile.copy_hdict(e2dsfile)
    # add infiles to outfile
    e2dsfffile.infiles = list(hfiles)
    # add extraction type (does not change for future files)
    e2dsfffile.add_hkey('KW_EXT_TYPE', value=e2dsfffile.name)
    # set output key
    e2dsfffile.add_hkey('KW_OUTPUT', value=e2dsfffile.name)
    # need to use different thermal ratio keys
    e2dsfffile.add_hkey('KW_THERM_RATIO_1', value=eprops['THERMALFF_RATIO1'])
    e2dsfffile.add_hkey('KW_THERM_RATIO_2', value=eprops['THERMALFF_RATIO2'])
    e2dsfffile.add_hkey('KW_THERM_RATIO_U',
                        value=eprops['THERMALFF_RATIO_USED'])
    # copy data
    e2dsfffile.data = eprops['E2DSFF']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsfffile.filename]
    WLOG(params, '', textentry('40-016-00006', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsfffile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    e2dsfffile.write_multi(data_list=data_list, name_list=name_list,
                           block_kind=recipe.out_block_str,
                           runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(e2dsfffile)
    # ----------------------------------------------------------------------
    # Store E2DSLL in file
    # ----------------------------------------------------------------------
    if params['DEBUG_E2DSLL_FILE']:
        # get a new copy of the e2dsll file
        e2dsllfile = recipe.outputs['E2DSLL_FILE'].newcopy(params=params,
                                                           fiber=fiber)
        # construct the filename from file instance
        e2dsllfile.construct_filename(infile=infile)
        # copy header from e2dsll file
        e2dsllfile.copy_hdict(e2dsfffile)
        # add infiles to outfile
        e2dsllfile.infiles = list(hfiles)
        # set output key
        e2dsllfile.add_hkey('KW_OUTPUT', value=e2dsllfile.name)
        # copy data
        e2dsllfile.data = eprops['E2DSLL']
        # ----------------------------------------------------------------------
        # log that we are saving rotated image
        wargs = [e2dsllfile.filename]
        WLOG(params, '', textentry('40-016-00007', args=wargs))
        # define multi lists
        data_list = [eprops['E2DSCC']]
        name_list = ['E2DSLL', 'E2DSCC']
        datatype_list = ['image']
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsllfile)]
            name_list += ['PARAM_TABLE']
            datatype_list += ['table']
        # write image to file
        e2dsllfile.write_multi(data_list=data_list, name_list=name_list,
                               datatype_list=datatype_list,
                               block_kind=recipe.out_block_str,
                               runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(e2dsllfile)
    # ----------------------------------------------------------------------
    # Store S1D_W in file
    # ----------------------------------------------------------------------
    # get a new copy of the s1d_w file
    s1dwfile = recipe.outputs['S1D_W_FILE'].newcopy(params=params,
                                                    fiber=fiber)
    # construct the filename from file instance
    s1dwfile.construct_filename(infile=infile)
    # copy header from e2dsll file
    s1dwfile.copy_hdict(e2dsfffile)
    # add infiles to outfile
    s1dwfile.infiles = list(hfiles)
    # set output key
    s1dwfile.add_hkey('KW_OUTPUT', value=s1dwfile.name)
    # add new header keys
    s1dwfile = add_s1d_keys(s1dwfile, swprops)
    # copy data
    s1dwfile.data = swprops['S1DTABLE']
    # must change the datatype to 'table'
    s1dwfile.datatype = 'table'
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = ['wave', s1dwfile.filename]
    WLOG(params, '', textentry('40-016-00010', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsfffile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    s1dwfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(s1dwfile)
    # ----------------------------------------------------------------------
    # Store S1D_V in file
    # ----------------------------------------------------------------------
    # get a new copy of the s1d_v file
    s1dvfile = recipe.outputs['S1D_V_FILE'].newcopy(params=params,
                                                    fiber=fiber)
    # construct the filename from file instance
    s1dvfile.construct_filename(infile=infile)
    # copy header from e2dsll file
    s1dvfile.copy_hdict(e2dsfffile)
    # add new header keys
    s1dvfile = add_s1d_keys(s1dvfile, svprops)
    # add infiles to outfile
    s1dvfile.infiles = list(hfiles)
    # set output key
    s1dvfile.add_hkey('KW_OUTPUT', value=s1dvfile.name)
    # copy data
    s1dvfile.data = svprops['S1DTABLE']
    # must change the datatype to 'table'
    s1dvfile.datatype = 'table'
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = ['velocity', s1dvfile.filename]
    WLOG(params, '', textentry('40-016-00010', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=s1dvfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    s1dvfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(s1dvfile)
    # ----------------------------------------------------------------------
    # return e2ds files
    return e2dsfile, e2dsfffile


def write_extraction_files_ql(params, recipe, infile, rawfiles, combine, fiber,
                              props, lprops, eprops, sprops, fbprops,
                              qc_params):
    # ----------------------------------------------------------------------
    # Store E2DS in file
    # ----------------------------------------------------------------------
    # get a new copy of the e2ds file
    e2dsfile = recipe.outputs['Q2DS_FILE'].newcopy(params=params,
                                                   fiber=fiber)
    # construct the filename from file instance
    e2dsfile.construct_filename(infile=infile)
    # define header keys for output file
    # copy keys from input file (excluding loc)
    e2dsfile.copy_original_keys(infile, exclude_groups=['loc'])
    # add version
    e2dsfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    e2dsfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    e2dsfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    e2dsfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    e2dsfile.add_hkey('KW_OUTPUT', value=e2dsfile.name)
    e2dsfile.add_hkey('KW_FIBER', value=fiber)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    e2dsfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add infiles to outfile
    e2dsfile.infiles = list(hfiles)
    # add the calibration files use
    e2dsfile = gen_calib.add_calibs_to_header(e2dsfile, props)
    # ----------------------------------------------------------------------
    # add the other calibration files used
    e2dsfile.add_hkey('KW_CDBORDP', value=lprops['ORDERPFILE'])
    e2dsfile.add_hkey('KW_CDTORDP', value=lprops['ORDERPTIME'])
    e2dsfile.add_hkey('KW_CDBLOCO', value=lprops['LOCOFILE'])
    e2dsfile.add_hkey('KW_CDTLOCO', value=lprops['LOCOTIME'])
    e2dsfile.add_hkey('KW_CDBSHAPEL', value=sprops['SHAPELFILE'])
    e2dsfile.add_hkey('KW_CDTSHAPEL', value=sprops['SHAPELTIME'])
    e2dsfile.add_hkey('KW_CDBSHAPEDX', value=sprops['SHAPEXFILE'])
    e2dsfile.add_hkey('KW_CDTSHAPEDX', value=sprops['SHAPEXTIME'])
    e2dsfile.add_hkey('KW_CDBSHAPEDY', value=sprops['SHAPEYFILE'])
    e2dsfile.add_hkey('KW_CDTSHAPEDY', value=sprops['SHAPEYTIME'])
    e2dsfile.add_hkey('KW_CDBFLAT', value=fbprops['FLATFILE'])
    e2dsfile.add_hkey('KW_CDTFLAT', value=fbprops['FLATTIME'])
    e2dsfile.add_hkey('KW_CDBBLAZE', value=fbprops['BLAZEFILE'])
    e2dsfile.add_hkey('KW_CDTBLAZE', value=fbprops['BLAZETIME'])
    # additional calibration keys
    if 'FIBERTYPE' in eprops:
        e2dsfile.add_hkey('KW_C_FTYPE', value=eprops['FIBERTYPE'])
    # ----------------------------------------------------------------------
    # add qc parameters
    e2dsfile.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # add shape transform parameters
    e2dsfile.add_hkey('KW_SHAPE_DX', value=sprops['SHAPEL'][0])
    e2dsfile.add_hkey('KW_SHAPE_DY', value=sprops['SHAPEL'][1])
    e2dsfile.add_hkey('KW_SHAPE_A', value=sprops['SHAPEL'][2])
    e2dsfile.add_hkey('KW_SHAPE_B', value=sprops['SHAPEL'][3])
    e2dsfile.add_hkey('KW_SHAPE_C', value=sprops['SHAPEL'][4])
    e2dsfile.add_hkey('KW_SHAPE_D', value=sprops['SHAPEL'][5])
    # ----------------------------------------------------------------------
    # add extraction type (does not change for future files)
    e2dsfile.add_hkey('KW_EXT_TYPE', value=e2dsfile.name)
    # add SNR parameters to header
    e2dsfile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                         dim1name='order')
    # add start and end extraction order used
    e2dsfile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
    e2dsfile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
    # add extraction ranges used
    e2dsfile.add_hkey('KW_EXT_RANGE1', value=eprops['RANGE1'])
    e2dsfile.add_hkey('KW_EXT_RANGE2', value=eprops['RANGE2'])
    # add cosmic parameters used
    e2dsfile.add_hkey('KW_COSMIC', value=eprops['COSMIC'])
    e2dsfile.add_hkey('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'])
    e2dsfile.add_hkey('KW_COSMIC_THRES',
                      value=eprops['COSMIC_THRESHOLD'])
    # add saturation parameters used
    e2dsfile.add_hkey('KW_SAT_QC', value=eprops['SAT_LEVEL'])
    with warnings.catch_warnings(record=True) as _:
        max_sat_level = mp.nanmax(eprops['FLUX_VAL'])
    e2dsfile.add_hkey('KW_SAT_LEVEL', value=max_sat_level)
    # add whether we corrected FP leakage (quick mode = False)
    e2dsfile.add_hkey('KW_LEAK_CORR', value=0)
    # ----------------------------------------------------------------------
    # copy data
    e2dsfile.data = eprops['E2DS']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsfile.filename]
    WLOG(params, '', textentry('40-016-00005', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    e2dsfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(e2dsfile)
    # ----------------------------------------------------------------------
    # Store E2DSFF in file
    # ----------------------------------------------------------------------
    # get a new copy of the e2dsff file
    e2dsfffile = recipe.outputs['Q2DSFF_FILE'].newcopy(params=params,
                                                       fiber=fiber)
    # construct the filename from file instance
    e2dsfffile.construct_filename(infile=infile)
    # copy header from e2dsff file
    e2dsfffile.copy_hdict(e2dsfile)
    # add infiles to outfile
    e2dsfffile.infiles = list(hfiles)
    # add extraction type (does not change for future files)
    e2dsfffile.add_hkey('KW_EXT_TYPE', value=e2dsfffile.name)
    # set output key
    e2dsfffile.add_hkey('KW_OUTPUT', value=e2dsfffile.name)
    # copy data
    e2dsfffile.data = eprops['E2DSFF']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsfffile.filename]
    WLOG(params, '', textentry('40-016-00006', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsfffile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    e2dsfffile.write_multi(data_list=data_list, name_list=name_list,
                           block_kind=recipe.out_block_str,
                           runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(e2dsfffile)
    # ----------------------------------------------------------------------
    # return e2ds files
    return e2dsfile, e2dsfffile


def extract_summary(recipe, params, qc_params, e2dsfile, sprops, eprops,
                    fiber):
    # add qc params (fiber specific)
    recipe.plot.add_qc_params(qc_params, fiber=fiber)
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_TYPE', value=e2dsfile.name,
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_DX', value=sprops['SHAPEL'][0],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_DY', value=sprops['SHAPEL'][1],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_A', value=sprops['SHAPEL'][2],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_B', value=sprops['SHAPEL'][3],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_C', value=sprops['SHAPEL'][4],
                         fiber=fiber)
    recipe.plot.add_stat('KW_SHAPE_D', value=sprops['SHAPEL'][5],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_START', value=eprops['START_ORDER'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_END', value=eprops['END_ORDER'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE1', value=eprops['RANGE1'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE2', value=eprops['RANGE2'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC', value=eprops['COSMIC'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_THRES', fiber=fiber,
                         value=eprops['COSMIC_THRESHOLD'])


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

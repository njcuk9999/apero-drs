#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-09 at 13:42

@author: cook
"""
import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from astropy import constants as cc
from astropy import units as uu
from astropy.table import Table

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore import drs_lang
from aperocore import math as mp
from aperocore.core import drs_misc
from apero.core import drs_database
from aperocore.core import drs_log
from apero.core import drs_file
from aperocore.core import drs_text
from apero.utils import drs_recipe
from apero.io import drs_fits
from apero.science.calib import gen_calib
from apero.science.calib import localisation
from apero.science.calib import shape
from apero.science.calib import wave
from apero.science.extract import berv
from apero.science.extract import model_background
from apero.instruments import select
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extraction.gen_ext.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsNpyFile = drs_file.DrsNpyFile
DrsRecipe = drs_recipe.DrsRecipe
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)
# -----------------------------------------------------------------------------
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light_kms = cc.c.to(uu.km / uu.s).value
# Get function string
display_func = drs_misc.display_func


# =============================================================================
# Define general functions
# =============================================================================
def get_order_profiles(params: ParamDict, recipe: DrsRecipe,
                       fibertypes: List[str],
                       sprops: ParamDict) -> dict:
    """
    Load pre-computed order profiles and localisation geometry from the SHAPEL
    calibration file.

    The straightened profiles (``ORDERP_STRAIGHT_{fiber}``), detector-frame
    profiles (``PROFILES_NOSHAPE_{fiber}``), and localisation geometry arrays
    are written into the SHAPEL file by ``apero_shape`` via
    ``shape.compute_shape_order_profiles``.  This function reads them back so
    that ``apero_extract`` does not need to recompute or re-straighten anything.

    :param params: ParamDict, APERO constants
    :param recipe: DrsRecipe, the calling recipe instance
    :param fibertypes: list of str, fiber names to load (e.g. ['A', 'B', 'C'])
    :param sprops: ParamDict, shape calibration properties from
                   ``shape.get_shape_calibs``; must contain ``SHAPELFILE``,
                   ``SHAPELTIME``, ``KW_CDBORDP``, and ``KW_CDTORDP``

    :return: dict with keys:
        ``ORDERP``         – {fiber: straightened profile array}
        ``ORDERPFILE``     – {fiber: source LOC_LOCO filename}
        ``ORDERPTIME``     – {fiber: source LOC_LOCO MJD-MID}
        ``PROFILES_NOSHAPE`` – {fiber: detector-frame profile array}
        ``LOCOFILE``       – path to the LOC_LOCO used
        ``ORDER_MAP``      – order label map (int32 array)
        ``ORDER_NEAREST``  – nearest-trace label map (int32 array)
        ``ORDER_RANGES``   – {fiber: (first_label, last_label)}
        ``ORDER_TOP``      – top-row bounds (float array)
        ``ORDER_BOTTOM``   – bottom-row bounds (float array)
        ``ORDER_MID``      – midpoint rows (float array)
    """
    func_name = __NAME__ + '.get_order_profiles()'
    shapelfile = sprops['SHAPELFILE']
    WLOG(params, 'info',
         'Loading order profiles from SHAPEL: {0}'.format(shapelfile))
    # load the LOC_LOCO provenance recorded in the SHAPEL header so downstream
    # header keys reflect where the profiles originally came from
    shapel_hdr = drs_fits.read_header(params, shapelfile)
    locofile = shapel_hdr.get('KW_CDBLOCO', 'None')
    locotime = shapel_hdr.get('KW_CDTLOCO', np.nan)
    # straight profiles and detector-frame profiles, keyed by fiber name
    orderprofiles = dict()
    profiles_noshape = dict()
    orderpfiles = dict()
    orderptimes = dict()
    for fiber in fibertypes:
        WLOG(params, '', textentry('40-016-00003', args=[fiber]))
        orderprofiles[fiber] = np.array(
            drs_fits.readfits(params, shapelfile,
                              extname='ORDERP_STRAIGHT_{0}'.format(fiber)))
        profiles_noshape[fiber] = np.array(
            drs_fits.readfits(params, shapelfile,
                              extname='PROFILES_NOSHAPE_{0}'.format(fiber)))
        # provenance: each fiber's profile traces back to the same LOC_LOCO
        orderpfiles[fiber] = locofile
        orderptimes[fiber] = locotime
    # load localisation geometry stored in SHAPEL by apero_shape
    order_map = drs_fits.readfits(params, shapelfile,
                                  extname='ORDER_POS_MAP')
    order_nearest = drs_fits.readfits(params, shapelfile,
                                      extname='ORDER_NEAREST_MAP')
    order_top = drs_fits.readfits(params, shapelfile, extname='ORDER_TOP')
    order_bottom = drs_fits.readfits(params, shapelfile,
                                     extname='ORDER_BOTTOM')
    order_mid = drs_fits.readfits(params, shapelfile, extname='ORDER_MID')
    range_table = drs_fits.readfits(params, shapelfile, fmt='fits-table',
                                    extname='ORDER_RANGE_TABLE')
    # convert the range table into the {fiber: (first, last)} dict used by the
    # extraction model
    order_ranges = dict()
    for rt_fiber, first, last in zip(range_table['FIBER'],
                                     range_table['FIRST'],
                                     range_table['LAST']):
        order_ranges[str(rt_fiber)] = (int(first), int(last))
    # assemble the property bag used by main_extract and run_all_fiber_model
    oprops = dict()
    oprops['ORDERP'] = orderprofiles
    oprops['ORDERPFILE'] = orderpfiles
    oprops['ORDERPTIME'] = orderptimes
    oprops['PROFILES_NOSHAPE'] = profiles_noshape
    oprops['LOCOFILE'] = locofile
    oprops['ORDER_MAP'] = np.array(order_map, dtype=np.int32)
    oprops['ORDER_NEAREST'] = np.array(order_nearest, dtype=np.int32)
    oprops['ORDER_RANGES'] = order_ranges
    oprops['ORDER_TOP'] = np.array(order_top, dtype=float)
    oprops['ORDER_BOTTOM'] = np.array(order_bottom, dtype=float)
    oprops['ORDER_MID'] = np.array(order_mid, dtype=float)
    return oprops


def ref_fplines(params, recipe, e2dsfile, wavemap, fiber, cavity_poly,
                database=None, **kwargs):
    # set up function name
    func_name = display_func('ref_fplines', __NAME__)
    # skip FP-line processing for quick-look mode and flat extractions;
    # wave solution is not available or not yet meaningful in these cases
    extract_type = params['INPUTS'].get('EXTRACT_TYPE', 'standard')
    if params['CAL.EXT.QUICKLOOK'] or extract_type == 'flat':
        return None
    # get constant from params
    allowtypes = pcheck(params, 'CAL.WAVE.FP.DPRLIST', 'fptypes',
                        kwargs, func_name)

    allowfibers = pcheck(params, 'CAL.WAVE.FP.FIBER_TYPES', 'fpfibers', kwargs)
    # get dprtype
    dprtype = e2dsfile.get_hkey('KW_DPRTYPE', dtype=str)
    # get psuedo constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    if fiber in allowfibers:
        rfiber = str(fiber)
    else:
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
    # make sure fiber is FP
    if pconst.FIBER_DPR_POS(dprtype, fiber) != 'FP':
        # Skipping FPLINES (Fiber = {0})'
        WLOG(params, 'debug', textentry('90-016-00003', args=[fiber]))
        return None
    # ----------------------------------------------------------------------
    # announce FP-line processing (after all early-exit checks pass)
    WLOG(params, '', 'Computing FP reference lines for '
                     'fiber {0}'.format(fiber))
    # get reference hc lines and fp lines from calibDB
    wout = wave.get_wavelines(params, recipe, fiber, infile=e2dsfile,
                              database=database)
    mhclines, mhclsource, mfplines, mfplsource = wout
    # deal with no fplines found
    if mfplines is None:
        return None
    # ----------------------------------------------------------------------
    # generate the fp reference lines
    fpargs = dict(e2dsfile=e2dsfile, wavemap=wavemap, fplines=mfplines,
                  cavity_poly=cavity_poly)
    rfpl = wave.calc_wave_lines(params, recipe, **fpargs)
    # ----------------------------------------------------------------------
    # return fp lines for e2ds file
    return rfpl


# =============================================================================
# Define s1d functions
# =============================================================================
def e2ds_to_s1d(params: ParamDict, recipe: DrsRecipe,
                wavemap: Optional[np.ndarray],
                e2ds: np.ndarray,  blaze: np.ndarray,
                fiber: Union[str, None] = None, wgrid: str = 'wave',
                s1dkind: Union[str, None] = None,
                e2dserr: Union[np.ndarray, None] = None,
                **kwargs):
    """
    Resample an extracted 2D spectrum onto a 1D wavelength or velocity grid.

    Returns None when the 1D spectrum should be skipped: quick-look mode,
    flat extractions (no meaningful blaze), or when the wave solution is
    absent (wavemap is None).

    :param params: ParamDict, APERO constants
    :param recipe: DrsRecipe, calling recipe
    :param wavemap: numpy (2D) array or None; the per-order wavelength solution
    :param e2ds: numpy (2D) array, the extracted spectrum
    :param blaze: numpy (2D) array, the blaze function
    :param fiber: str or None, the fiber name
    :param wgrid: str, 'wave' or 'velocity' grid type
    :param s1dkind: str or None, label for the spectrum kind
    :param e2dserr: numpy (2D) array or None, errors on e2ds

    :return: ParamDict with S1D properties, or None when skipped
    """
    func_name = __NAME__ + '.e2ds_to_s1d()'
    # skip S1D for quick-look mode, flat extractions (blaze is unity and
    # velocity corrections are not yet applied), or missing wave solution
    extract_type = params['INPUTS'].get('EXTRACT_TYPE', 'standard')
    if (params['CAL.EXT.QUICKLOOK'] or extract_type == 'flat'
            or wavemap is None):
        return None
    # get parameters from p
    wavestart = pcheck(params, 'CAL.EXT.S1D_WAVESTART', 'wavestart', kwargs,
                       func_name)
    waveend = pcheck(params, 'CAL.EXT.S1D_WAVEEND', 'waveend', kwargs,
                     func_name)
    binwave = pcheck(params, 'CAL.EXT.S1D_BIN_UWAVE', 'binwave', kwargs,
                     func_name)
    binvelo = pcheck(params, 'CAL.EXT.S1D_BIN_UVEL', 'binvelo', kwargs,
                     func_name)
    smooth_size = pcheck(params, 'CAL.EXT.S1D_EDGE_SSIZE', 'smooth_size',
                         kwargs, func_name)
    blazethres = pcheck(params, 'OBJ.TELL.GEN.CUT_BLAZE_NORM',
                        'blazethres', kwargs, func_name)
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
        # this is our wave grid
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
def _extracted_image_key(eprops: ParamDict) -> str:
    """
    Get the primary extracted-image key from an extraction property dict

    :param eprops: ParamDict, extraction property dictionary

    :return: str, extracted-image key to use for image-level checks
    """
    if 'E2DS' in eprops:
        return 'E2DS'
    if 'E2DSFF' in eprops:
        return 'E2DSFF'
    raise KeyError('Extraction properties contain no E2DS/E2DSFF image')


def qc_extraction(params, eprops=None, spectra=None):
    """
    Check that the extracted spectrum contract contains finite data.

    :param params: ParamDict, APERO constants
    :param eprops: ParamDict or None, legacy extraction properties
    :param spectra: tuple or None, spectrum and error arrays

    :return: tuple, QC parameter lists and pass flag
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names = [], [], [],
    qc_logic, qc_pass = [], []
    # Prefer the new spectrum tuple when supplied by the model path.
    if spectra is not None:
        image = spectra[0]
    else:
        image_key = _extracted_image_key(eprops)
        image = eprops[image_key]
    # --------------------------------------------------------------
    # if array is completely NaNs it shouldn't pass
    if np.sum(np.isfinite(image)) == 0:
        # add failed message to fail message list
        fail_msg.append(textentry('40-016-00008'))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append('NaN')
    qc_names.append('image')
    qc_logic.append('image is all NaN')
    # -------------------------------------------------------------------------
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


def create_order_table(lprops: ParamDict, wprops: ParamDict,
                       eprops: ParamDict) -> Table:
    """
    Create the order table with statistics about each order
    and the wave and loc coefficients

    :param lprops: ParamDict, the localisation parameter dictionary
    :param wprops: ParamDict, the wave solution parameter dictionary
    :param eprops: ParamDict, the extraction parameter dictionary

    :return: astropy.Table - the order table
    """
    # number of orders
    nbo = wprops['NBO']
    # nbxpix = wprops['NBPIX']
    # start the table
    order_table = Table()
    # order number
    order_table['order_num'] = np.arange(nbo).astype(int)
    # echelle number
    order_table['echelle_num'] = wprops['EORDERS']
    # wave min/max/med
    order_table['WAVE_MIN'] = mp.nanmin(wprops['WAVEMAP'], axis=1)
    order_table['WAVE_MED'] = mp.nanmedian(wprops['WAVEMAP'], axis=1)
    order_table['WAVE_MEAN'] = mp.nanmean(wprops['WAVEMAP'], axis=1)
    order_table['WAVE_MAX'] = mp.nanmax(wprops['WAVEMAP'], axis=1)
    # central y pixel position
    order_table['YPIX_CENT'] = lprops['YCENT']
    # extract parameters
    order_table['SNR'] = eprops['SNR']
    order_table['NCOSMIC'] = eprops['N_COSMIC']
    order_table['FLUXVAL'] = eprops['FLUX_VAL']
    # loop around available extraction frames
    keys = ['E2DS', 'E2DSFF', 'FLAT', 'BLAZE']
    for key in keys:
        if key not in eprops:
            continue
        order_table[f'{key}_MIN'] = mp.nanmin(eprops[key], axis=1)
        order_table[f'{key}_MAX'] = mp.nanmax(eprops[key], axis=1)
        order_table[f'{key}_MED'] = mp.nanmedian(eprops[key], axis=1)
        order_table[f'{key}_MEAN'] = mp.nanmean(eprops[key], axis=1)
    # loc parameters
    for n_coeff in range(lprops['CENT_COEFFS'].shape[1]):
        keyname = f'LOC_POS_COEFF_{n_coeff}'
        order_table[keyname] = lprops['CENT_COEFFS'][:, n_coeff]
    for n_coeff in range(lprops['WID_COEFFS'].shape[1]):
        keyname = f'LOC_WID_COEFF_{n_coeff}'
        order_table[keyname] = lprops['WID_COEFFS'][:, n_coeff]
    # return the table
    return order_table


def write_extraction_files(params, recipe, infile, rawfiles, combine, fiber,
                           props, lprops, wprops, eprops, bprops,
                           swprops, svprops, sprops, fbprops, qc_params):

    # create extraction order table
    order_table = create_order_table(lprops, wprops, eprops)
    # ----------------------------------------------------------------------
    # Store the single E2DSFF product.
    # ----------------------------------------------------------------------
    # get a new copy of the e2ds file
    e2dsfile = recipe.outputs['E2DSFF_FILE'].newcopy(params=params,
                                                     fiber=fiber)
    # construct the filename from file instance
    e2dsfile.construct_filename(infile=infile)
    # define header keys for output file
    # copy keys from input file (excluding loc)
    e2dsfile.copy_original_keys(infile, exclude_groups=['loc'])
    # add core values (that should be in all headers)
    e2dsfile.add_core_hkeys(params)
    # add fiber
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
    # add the blaze file used (flat is no longer applied during extraction)
    e2dsfile.add_hkey('KW_CDBBLAZE', value=fbprops['BLAZEFILE'])
    e2dsfile.add_hkey('KW_CDTBLAZE', value=fbprops['BLAZETIME'])
    # add the thermal file used
    if 'THERMALFILE' in eprops:
        e2dsfile.add_hkey('KW_CDBTHERMAL', value=eprops['THERMALFILE'])
        e2dsfile.add_hkey('KW_CDTTHERMAL', value=eprops['THERMALTIME'])
        e2dsfile.add_hkey('KW_THERM_RATIO', value=eprops['THERMAL_RATIO'])
        e2dsfile.add_hkey('KW_THERM_RATIO_U',
                          value=eprops['THERMAL_RATIO_USED'])

    # add the wave file used
    e2dsfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    e2dsfile.add_hkey('KW_CDTWAVE', value=wprops['WAVETIME'])
    # add the leak reference calibration file used
    e2dsfile.add_hkey('KW_CDBLEAKM', value=eprops['LEAKREF_FILE'])
    e2dsfile.add_hkey('KW_CDTLEAKM', value=eprops['LEAKREF_TIME'])
    e2dsfile.add_hkey('KW_CDBLEAKR', value=eprops['LEAKREF_REFFILE'])
    e2dsfile.add_hkey('KW_CDTLEAKR', value=eprops['LEAKREF_REFTIME'])
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
    # add effective readout noise
    e2dsfile.add_hkey('KW_EFF_RON', value=eprops['EFF_RON'])
    # add SNR parameters to header
    e2dsfile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                         dim1name='order')
    e2dsfile.add_hkey('KW_EXT_NBO', value=len(eprops['SNR']))
    # ----------------------------------------------------------------------
    # get measured pixel to pixel scatter values
    mp2p_e2ds = eprops['MP2P_E2DSFF']
    # add the measured snr
    e2dsfile.add_hkey_1d('KW_P2P_SCAT', values=mp2p_e2ds['MP2P'])
    # add the measured band snrs
    e2dsfile.add_hkey_vals(f'KW_P2P_BSCAT', name='band',
                           keys=list(mp2p_e2ds['BP2P'].keys()),
                           values=list(mp2p_e2ds['BP2P'].values()))
    # ----------------------------------------------------------------------
    # add start and end extraction order used
    e2dsfile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
    e2dsfile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
    # add extraction ranges used
    e2dsfile.add_hkey('KW_EXT_RANGE1', value=eprops['CAL.EXT.RANGE1'])
    e2dsfile.add_hkey('KW_EXT_RANGE2', value=eprops['CAL.EXT.RANGE2'])
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
    e2dsfile.data = eprops['E2DSFF']
    # ----------------------------------------------------------------------
    # Use the prepared E2DSFF file for the final write.
    e2dsfffile = e2dsfile
    # ----------------------------------------------------------------------
    # get measured pixel to pixel scatter values
    mp2p_e2dsff = eprops['MP2P_E2DSFF']
    # add the measured snr
    e2dsfffile.add_hkey_1d('KW_P2P_SCAT', values=mp2p_e2dsff['MP2P'])
    # add the measured band snrs
    e2dsfffile.add_hkey_vals(f'KW_P2P_BSCAT', name='band',
                           keys=list(mp2p_e2dsff['BP2P'].keys()),
                           values=list(mp2p_e2dsff['BP2P'].values()))
    # -------------------------------------------------------------------------
    # set output key
    e2dsfffile.add_hkey('KW_OUTPUT', value=e2dsfffile.name)
    # need to use different thermal ratio keys if we have corrected thermal
    e2dsfffile.add_hkey('KW_THERM_RATIO', value=eprops['THERMAL_RATIO'])
    e2dsfffile.add_hkey('KW_THERM_RATIO_U',
                        value=eprops['THERMAL_RATIO_USED'])
    # copy data
    e2dsfffile.data = eprops['E2DSFF']
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [e2dsfffile.filename]
    WLOG(params, '', textentry('40-016-00006', args=wargs))
    # define multi lists
    data_list, name_list = [order_table], ['ORDER_TABLE']
    # snapshot of parameters
    if params['GLOBAL.PSNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=e2dsfffile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    e2dsfffile.write_multi(data_list=data_list, name_list=name_list,
                           block_kind=recipe.out_block_str,
                           runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(e2dsfffile)
    # ----------------------------------------------------------------------
    # Store S1D_W in file (skipped for flat extractions where swprops is None)
    # ----------------------------------------------------------------------
    if swprops is not None:
        # get a new copy of the s1d_w file
        s1dwfile = recipe.outputs['S1D_W_FILE'].newcopy(params=params,
                                                        fiber=fiber)
        # construct the filename from file instance
        s1dwfile.construct_filename(infile=infile)
        # copy header from e2dsff file
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
        # log that we are saving the wave-grid S1D
        wargs = ['wave', s1dwfile.filename]
        WLOG(params, '', textentry('40-016-00010', args=wargs))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['GLOBAL.PSNAPSHOT']:
            data_list += [
                params.snapshot_table(recipe, drsfitsfile=e2dsfffile)]
            name_list += ['PARAM_TABLE']
        # write image to file
        s1dwfile.write_multi(data_list=data_list, name_list=name_list,
                             block_kind=recipe.out_block_str,
                             runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(s1dwfile)
    # ----------------------------------------------------------------------
    # Store S1D_V in file (skipped for flat extractions where svprops is None)
    # ----------------------------------------------------------------------
    if svprops is not None:
        # get a new copy of the s1d_v file
        s1dvfile = recipe.outputs['S1D_V_FILE'].newcopy(params=params,
                                                        fiber=fiber)
        # construct the filename from file instance
        s1dvfile.construct_filename(infile=infile)
        # copy header from e2dsff file
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
        # log that we are saving the velocity-grid S1D
        wargs = ['velocity', s1dvfile.filename]
        WLOG(params, '', textentry('40-016-00010', args=wargs))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['GLOBAL.PSNAPSHOT']:
            data_list += [
                params.snapshot_table(recipe, drsfitsfile=s1dvfile)]
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
    # Store the single quicklook E2DSFF product.
    # ----------------------------------------------------------------------
    # get a new copy of the e2ds file
    e2dsfile = recipe.outputs['Q2DSFF_FILE'].newcopy(params=params,
                                                     fiber=fiber)
    # construct the filename from file instance
    e2dsfile.construct_filename(infile=infile)
    # define header keys for output file
    # copy keys from input file (excluding loc)
    e2dsfile.copy_original_keys(infile, exclude_groups=['loc'])
    # add core values (that should be in all headers)
    e2dsfile.add_core_hkeys(params)
    # add fiber
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
    # flat is no longer applied during extraction; blaze only
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
    # add effective readout noise
    e2dsfile.add_hkey('KW_EFF_RON', value=eprops['EFF_RON'])
    # add SNR parameters to header
    e2dsfile.add_hkey_1d('KW_EXT_SNR', values=eprops['SNR'],
                         dim1name='order')
    e2dsfile.add_hkey('KW_EXT_NBO', value=len(eprops['SNR']))
    # -------------------------------------------------------------------------
    # add start and end extraction order used
    e2dsfile.add_hkey('KW_EXT_START', value=eprops['START_ORDER'])
    e2dsfile.add_hkey('KW_EXT_END', value=eprops['END_ORDER'])
    # add extraction ranges used
    e2dsfile.add_hkey('KW_EXT_RANGE1', value=eprops['CAL.EXT.RANGE1'])
    e2dsfile.add_hkey('KW_EXT_RANGE2', value=eprops['CAL.EXT.RANGE2'])
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
    e2dsfile.data = eprops['E2DSFF']
    # ----------------------------------------------------------------------
    # Use the prepared Q2DSFF file for the final write.
    e2dsfffile = e2dsfile
    # -------------------------------------------------------------------------
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
    if params['GLOBAL.PSNAPSHOT']:
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
    recipe.plot.add_stat('KW_VERSION', value=params['DRS.VERSION'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS.DATE'],
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
    recipe.plot.add_stat('KW_EXT_RANGE1', value=eprops['CAL.EXT.RANGE1'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_EXT_RANGE2', value=eprops['CAL.EXT.RANGE2'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC', value=eprops['COSMIC'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_CUT', value=eprops['COSMIC_SIGCUT'],
                         fiber=fiber)
    recipe.plot.add_stat('KW_COSMIC_THRES', fiber=fiber,
                         value=eprops['COSMIC_THRESHOLD'])


def main_extract(params: ParamDict, recipe: DrsRecipe, infile: DrsFitsFile,
                 pconst,
                 database: Optional[drs_database.CalibrationDatabase] = None) -> ParamDict:
    """
    Top-level extraction setup: shape calibration, image calibration, order
    profiles, shape transform, geometry, and simultaneous-fiber model fit.

    Wraps the complete per-file setup that precedes the per-fiber loop in every
    extraction recipe.  All instruments run identical steps so a single call
    here replaces ~80 lines of boilerplate in each recipe.

    :param params: ParamDict, APERO constants
    :param recipe: DrsRecipe, the calling recipe
    :param infile: DrsFitsFile, the science frame to process
    :param pconst: instrument pseudo-constants (from load_pconfig)
    :param database: CalibrationDatabase or None; if None a new one is
                     opened internally

    :return: ParamDict with the following keys:
        IMAGE         - original calibrated image (2D array)
        IMAGE_STRAIGHT - shape-transformed image (2D array)
        HEADER        - FITS header from infile
        SHAPE_PROPS   - shape calibration ParamDict
        CALIB_PROPS   - general calibration ParamDict (from calibrate_ppfile)
        ORDER_PROPS   - order-profile dict (from get_order_profiles)
        MODEL_PROPS   - simultaneous-fiber model ParamDict
        EPROPS_ALL    - dict mapping fiber name to per-fiber ParamDict
        FIBERTYPES    - list of fibers being processed (ref first)
        SCI_FIBERS    - list of science fiber names
        REF_FIBER     - reference fiber name
    """
    func_name = __NAME__ + '.main_extract()'
    # use supplied database or open a new one
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(
            params, recipe.shortname)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------
    # Determine fiber topology from instrument pseudo-constants
    # ------------------------------------------------------------------
    fiber_specs = pconst.FIBER_SPECS()
    sci_fibers = [spec.name for spec in fiber_specs
                  if spec.role == 'science']
    ref_fiber = next(spec.name for spec in fiber_specs
                     if spec.role == 'reference')
    # reference fiber must be processed first (leak correction depends on it)
    if params['INPUTS']['FIBER'] == 'ALL':
        fibertypes = [ref_fiber] + sci_fibers
    else:
        fibertypes = [params['INPUTS']['FIBER']]
    # ------------------------------------------------------------------
    # Load shape calibration components
    # ------------------------------------------------------------------
    header = infile.get_header()
    sprops = shape.get_shape_calibs(params, recipe, header,
                                    database=calibdbm)
    # ------------------------------------------------------------------
    # Calibrate the input pre-processed frame
    # ------------------------------------------------------------------
    cargs = [params, recipe, infile]
    ckwargs = dict(database=calibdbm, correctback=False)
    cout = gen_calib.calibrate_ppfile(*cargs, **ckwargs)
    props, image = cout
    # ------------------------------------------------------------------
    # Load order profiles and geometry from SHAPEL calibration file
    # ------------------------------------------------------------------
    # Profiles were straightened once in apero_shape; load them here so
    # apero_extract does not recompute anything per-science-frame.
    oprops = get_order_profiles(params, recipe, fibertypes, sprops)
    # ------------------------------------------------------------------
    # Apply shape transformation to straighten the science image
    # ------------------------------------------------------------------
    WLOG(params, 'info', textentry('40-016-00004'))
    shape_order = params['CAL.EXT.SPLINE_ORDER']
    shargs = [params, image, sprops['SHAPEL']]
    shkwargs = dict(dxmap=sprops['SHAPEX'],
                    dymap=sprops['SHAPEY'],
                    order=shape_order)
    image2 = shape.ea_transform(*shargs, **shkwargs)
    # ------------------------------------------------------------------
    # Prepare geometry for the all-fiber model / background path
    # ------------------------------------------------------------------
    mbgprops = model_background.prepare_model_bckgrd_geo(params, sprops)
    # ------------------------------------------------------------------
    # Run the simultaneous all-fiber model extraction
    # ------------------------------------------------------------------
    # science fiber is the first model fiber; reference is the second
    model_fiber1 = sci_fibers[0]
    model_fiber2 = ref_fiber
    model_groups = pconst.FIBER_SPECTRAL_GROUPS(oprops['ORDER_RANGES'])
    mpargs = (params, image, image2,
              oprops['ORDERP'], oprops['PROFILES_NOSHAPE'],
              mbgprops,
              oprops['ORDER_MAP'], oprops['ORDER_NEAREST'],
              oprops['ORDER_RANGES'],
              oprops['ORDER_TOP'], oprops['ORDER_BOTTOM'],
              oprops['ORDER_MID'], model_groups,
              model_fiber1, model_fiber2)
    model_props = model_background.run_all_fiber_model(*mpargs)
    # emit the model/background diagnostic plot
    recipe.plot('EXTRACT_MODEL_BACKGROUND', params=params,
                model_props=model_props)
    # ------------------------------------------------------------------
    # Build initial per-fiber extraction property bags from model output
    # ------------------------------------------------------------------
    # nframes is used to scale the saturation-level quality-control threshold
    nframes = infile.numfiles
    ron = float(model_props['RON'])
    eprops_all: Dict[str, ParamDict] = dict()
    for fiber in fibertypes:
        e2ds, e2ds_err = model_props['SPECTRA'][fiber]
        e2ds = np.array(e2ds, dtype=float)
        e2ds_err = np.array(e2ds_err, dtype=float)
        # per-order SNR: median signal-to-noise ratio per order
        with np.errstate(invalid='ignore', divide='ignore'):
            snr = np.nanmedian(
                e2ds / np.sqrt(np.abs(e2ds) + ron ** 2), axis=1)
        eprops = ParamDict()
        # raw model spectrum and its uncertainty
        eprops['E2DS'] = e2ds
        eprops['E2DSFF'] = np.array(e2ds)
        eprops['E2DS_ERROR'] = e2ds_err
        eprops['SNR'] = snr
        # per-order mean flux (used for saturation QC)
        eprops['FLUX_VAL'] = np.nanmean(e2ds, axis=1)
        eprops['N_COSMIC'] = np.zeros(e2ds.shape[0])
        eprops['FIBER'] = fiber
        # extraction order range (full range; no order trimming here)
        eprops['START_ORDER'] = 0
        eprops['END_ORDER'] = e2ds.shape[0] - 1
        eprops['CAL.EXT.RANGE1'] = 0
        eprops['CAL.EXT.RANGE2'] = 0
        eprops['SKIP_ORDERS'] = []
        # detector noise and gain parameters
        eprops['GAIN'] = params['IMAGE.EFFGAIN']
        eprops['SIGDET'] = ron
        eprops['EFF_RON'] = ron
        eprops['EFF_GAIN'] = params['IMAGE.EFFGAIN']
        # saturation quality-control thresholds
        eprops['SAT_QC'] = params['CAL.EXT.QC_FLUX_MAX']
        eprops['SAT_LEVEL'] = params['CAL.EXT.QC_FLUX_MAX'] * nframes
        # placeholder flat and blaze (ones until calib files are applied)
        eprops['FLAT'] = np.ones_like(e2ds)
        eprops['BLAZE'] = np.ones_like(e2ds)
        # per-order RMS (zero until blaze fit is run for flat extractions)
        eprops['RMS'] = np.zeros(e2ds.shape[0])
        # cosmic correction: not applied in the model-based extraction
        eprops['COSMIC'] = False
        eprops['COSMIC_SIGCUT'] = params['CAL.EXT.COSMIC_SIGCUT']
        eprops['COSMIC_THRESHOLD'] = params['CAL.EXT.COSMIC_THRES']
        eprops.set_all_sources(func_name)
        eprops_all[fiber] = eprops
    # ------------------------------------------------------------------
    # Bundle all products into a single return dict
    # ------------------------------------------------------------------
    mprops = ParamDict()
    mprops['IMAGE'] = image
    mprops['IMAGE_STRAIGHT'] = image2
    mprops['HEADER'] = header
    mprops['SHAPE_PROPS'] = sprops
    mprops['CALIB_PROPS'] = props
    mprops['ORDER_PROPS'] = oprops
    mprops['MODEL_PROPS'] = model_props
    mprops['EPROPS_ALL'] = eprops_all
    mprops['FIBERTYPES'] = fibertypes
    mprops['SCI_FIBERS'] = sci_fibers
    mprops['REF_FIBER'] = ref_fiber
    mprops.set_all_sources(func_name)
    return mprops


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
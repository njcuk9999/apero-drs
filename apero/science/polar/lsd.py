#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-25 at 13:25

@author: cook
"""
from astropy import constants as cc
from astropy.table import Table
from astropy import units as uu
import numpy as np
import os
from scipy.optimize import curve_fit
from typing import Tuple

from apero.base import base
from apero.core import math as mp
from apero import lang
from apero.core import constants
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_data
from apero.core.utils import drs_recipe
from apero.io import drs_table
from apero.science.polar import gen_pol

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'polar.lsd.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsRecipe = drs_recipe.DrsRecipe
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# LSD wrapper function
# =============================================================================
def lsd_analysis_wrapper(params: ParamDict, props: ParamDict) -> ParamDict:
    """
    Wrapper for the LSD analysis
    1. loads LSD mask
    2. gets the correct wavelength ranges
    3. prepares the polarimetry data
    4. runs the LSD analysis

    :param params: ParamDict, the parameter dictionary of constants
    :param props: ParamDict, the parameter dictionary of data

    :return: ParamDict, the updated props dictionary of data
    """
    # select the correct lsd mask and load values into props
    props = load_lsd_mask(params, props)
    # get wavelength ranges covering spectral lines in the ccf mask
    props = get_wl_ranges(params, props)
    # prepare polarimetry data
    props = prepare_polarimetry_data(params, props)
    # call function to perform lsd analysis
    props = lsd_analysis(params, props)
    # return props
    return props


def write_files(params: ParamDict, recipe: DrsRecipe, props: ParamDict,
                polfile: DrsFitsFile, cfile: DrsFitsFile, ctable: Table):
    """
    Write the LSD file to disk

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe instance that called this function
    :param props: ParamDict, the parameter dictionary of data
    :param polfile: DrsFitsFile, the pol DrsFitsFile (header copied from here)
    :param cfile: DrsFitsFile, the combined input file (file base from here)
    :param ctable: astropy.table.Table, the combined input file table with all
                   header keys that are not shared between input files

    :return: None - writes to disk
    """
    # set function name
    _ = display_func('write_files', __NAME__)
    # get data from polfile
    lsd_velocities = props['LSD_VELOCITIES']
    lsd_stokesvqu = props['LSD_STOKESVQU']
    lsd_stokesvqu_err = props['LSD_STOKESVQU_ERR']
    lsd_stokesi = props['LSD_STOKESI']
    lsd_stokesi_err = props['LSD_STOKESI_ERR']
    lsd_stokesi_model = props['LSD_STOKESI_MODEL']
    lsd_null = props['LSD_NULL']
    lsd_null_err = props['LSD_NULL_ERR']
    lsd_fit_rv = props['LSD_FIT_RV']
    lsd_pol_mean = props['LSD_POL_MEAN']
    lsd_pol_stddev = props['LSD_POL_STDDEV']
    lsd_pol_med = props['LSD_POL_MEDIAN']
    lsd_pol_medabsdev = props['LSD_POL_MEDABSDEV']
    lsd_stokesvqu_mean = props['LSD_STOKESVQU_MEAN']
    lsd_stokesvqu_stddev = props['LSD_STOKESVQU_STDDEV']
    lsd_null_mean = props['LSD_NULL_MEAN']
    lsd_null_stddev = props['LSD_NULL_STDDEV']
    lsd_mask_file = props['LSD_MASK_FILE']
    lsd_num_lines_mask = props['LSD_LINES_NUM_MASK']
    lsd_num_lines_used = props['LSD_LINES_NUM_USED']
    lsd_lines_mean_wave = props['LSD_LINES_MEAN_WAVE']
    lsd_lines_mean_lande = props['LSD_LINES_MEAN_LANDE']
    # -------------------------------------------------------------------------
    # make lsd table

    columns = ['Velocity', 'StokesVQU', 'StokesVQU_Err', 'StokesI',
               'StokesI_Err', 'StokesIModel', 'Null', 'Null_Err']
    values = [lsd_velocities, lsd_stokesvqu, lsd_stokesvqu_err, lsd_stokesi,
              lsd_stokesi_err, lsd_stokesi_model, lsd_null, lsd_null_err]
    # construct table
    lsd_table = drs_table.make_table(params, columns=columns, values=values)
    # -------------------------------------------------------------------------
    # Write LSD file to disk
    # -------------------------------------------------------------------------
    # get a new copy of the pol file
    lsdfile = recipe.outputs['POL_LSD'].newcopy(params=params)
    # construct the filename from file instance
    lsdfile.construct_filename(infile=cfile)
    # copy header from pol file
    lsdfile.copy_hdict(polfile)
    # -------------------------------------------------------------------------
    # add output tag
    lsdfile.add_hkey('KW_OUTPUT', value=lsdfile.name)
    # add the lsd origin
    instrument = params['INSTRUMENT']
    lsdfile.add_hkey('KW_LSD_ORIGIN', value='{0}_LSD'.format(instrument))
    # add the rv from lsd gaussian fit
    lsdfile.add_hkey('KW_LSD_FIT_RV', value=lsd_fit_rv)
    # add the mean degree of polarization
    lsdfile.add_hkey('KW_LSD_POL_MEAN', value=lsd_pol_mean)
    # add the std deviation of degree of polarization
    lsdfile.add_hkey('KW_LSD_POL_STDDEV', value=lsd_pol_stddev)
    # add the median degree of polarization
    lsdfile.add_hkey('KW_LSD_POL_MEDIAN', value=lsd_pol_med)
    # add the median deviations of degree of polarization
    lsdfile.add_hkey('KW_LSD_POL_MEDABSDEV', value=lsd_pol_medabsdev)
    # add the mean of stokes VQU lsd profile
    lsdfile.add_hkey('KW_LSD_STOKESVQU_MEAN', value=lsd_stokesvqu_mean)
    # add the std deviation of stokes VQU LSD profile
    lsdfile.add_hkey('KW_LSD_STOKESVQU_STDDEV', value=lsd_stokesvqu_stddev)
    # add the mean of stokes VQU LSD null profile
    lsdfile.add_hkey('KW_LSD_NULL_MEAN', value=lsd_null_mean)
    # add the std deviation of stokes vqu lsd null profile
    lsdfile.add_hkey('KW_LSD_NULL_STDDEV', value=lsd_null_stddev)
    # add the mask file used in the lsd analysis
    lsdfile.add_hkey('KW_LSD_MASK_FILE', value=lsd_mask_file)
    # add the number of lines in the original mask
    lsdfile.add_hkey('KW_LSD_MASK_NUMLINES', value=lsd_num_lines_mask)
    # add the number of lines used in the LSD analysis
    lsdfile.add_hkey('KW_LSD_MASKLINES_USED', value=lsd_num_lines_used)
    # add the mean wavelength of lines use din lsd analysis
    lsdfile.add_hkey('KW_LSD_MASKLINES_MWAVE', value=lsd_lines_mean_wave)
    # add the mean lande of lines used in lsd analysis
    lsdfile.add_hkey('KW_LSD_MASKLINES_MLANDE', value=lsd_lines_mean_lande)
    # -------------------------------------------------------------------------
    # add data
    lsdfile.data = lsd_table
    # define other extensions
    data_list = [ctable]
    datatype_list = ['table']
    name_list = ['POL_TABLE']
    # log that we are saving pol file
    WLOG(params, '', textentry('40-021-00009', args=[lsdfile.filename]))
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=lsdfile)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write image to file
    lsdfile.write_multi(data_list=data_list, name_list=name_list,
                        datatype_list=datatype_list,
                        block_kind=recipe.out_block_str,
                        runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(lsdfile)


# =============================================================================
# Define worker functions
# =============================================================================
def load_lsd_mask(params: ParamDict, props: ParamDict) -> ParamDict:
    """
        Function to select a LSD mask file from a given list of
        mask repositories that best match the object temperature,
        and then load spectral lines data for the LSD analysis.

        :param params: parameter dictionary of constants
            Must contain at least:
                POLAR_LSD_MIN_LANDE
                POLAR_LSD_MAX_LANDE
                POLAR_LSD_CCFLINES_AIR_WAVE
                POLAR_LSD_MIN_LINEDEPTH

        :param props: parameter dictionary of data
            Must contain at least:
                OBJECT_TEMPERATURE: float, object effective temperatures

        return: ParamDict, the parameter dictionary of data
            Adds:
                LSD_LINES_WLC
                LSD_LINES_ZNUMBER
                LSD_LINES_DEPTH
                LSD_LINES_POL_WEIGHT
                LSD_LINES_LANDE
                LSD_LINES_POL_EXC_POTENTIAL
                LSD_LINES_POL_FLAG
                LSD_LINES_NUM_USED
                LSD_LINES_MEAN_WAVE
                LSD_LINES_MEAN_LANDE
    """
    # set function name
    func_name = display_func('load_lsd_mask', __NAME__)
    # get parameters from params
    lsdmaskinput = params['INPUTS']['LSDMASK']
    min_lande = params['POLAR_LSD_MIN_LANDE']
    max_lande = params['POLAR_LSD_MAX_LANDE']
    ccflines_air_wave = params['POLAR_LSD_CCFLINES_AIR_WAVE']
    min_linedepth = params['POLAR_LSD_MIN_LINEDEPTH']
    # -------------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    # get lsd regions
    wl_regions = pconst.GET_LSD_LINE_REGIONS()
    # -------------------------------------------------------------------------
    # get temperature
    temperature = props['OBJECT_TEMPERATURE']
    # -------------------------------------------------------------------------
    # Load LSD mask
    if lsdmaskinput != 'None':
        lsd_mask_file = lsdmaskinput
    else:
        lsd_mask_file = None
    # -------------------------------------------------------------------------
    # load mask file
    maskdata, maskpath = drs_data.load_sp_mask_lsd(params, temperature,
                                                   filename=lsd_mask_file)
    # -------------------------------------------------------------------------
    # log message: Selected input LSD mask: {0}'
    margs = [maskpath]
    WLOG(params, 'info', textentry('40-021-00028', args=margs))
    # -------------------------------------------------------------------------
    # get parameters from maskdata
    wavec = np.array(maskdata['wavec'])
    znum = np.array(maskdata['znum'])
    depth = np.array(maskdata['depth'])
    lande = np.array(maskdata['lande'])
    excpotf = np.array(maskdata['excpotf'])
    flag = np.array(maskdata['flagf'])
    # -------------------------------------------------------------------------
    # log number of lines in original mask
    lines_num_mask = len(wavec)
    margs = [lines_num_mask]
    WLOG(params, '', textentry('40-021-00029', args=margs))
    # -------------------------------------------------------------------------
    # get a flag mask
    flag_mask = flag == 1
    # storage for all valid lines
    keep_mask = np.zeros_like(flag_mask).astype(bool)
    # filter lines
    for wlrange in wl_regions:
        # set initial and final wavelengths in range
        wlower, wupper = wlrange[0], wlrange[1]
        # make a mask of valid regions for this region
        mask = flag_mask & (wavec > wlower) & (wavec < wupper)
        # add mask to keep mask
        keep_mask |= mask
    # add to this a cut in lande g-factor
    keep_mask &= (lande > min_lande) & (lande < max_lande)
    # -------------------------------------------------------------------------
    if ccflines_air_wave:
        # if ccf line wavelengths are measured in air convert to vacuum
        wavec = convert_air_to_vacuum_wl(wavec)
    # create mask to cutoff lines with depth lower than POLAR_LSD_MIN_LINEDEPTH
    keep_mask &= depth > min_linedepth
    # -------------------------------------------------------------------------
    # now cut down our arrays to valid lines
    wavec = wavec[keep_mask]
    znum = znum[keep_mask]
    depth = depth[keep_mask]
    lande = lande[keep_mask]
    excpotf = excpotf[keep_mask]
    flag = flag[keep_mask]
    # -------------------------------------------------------------------------
    # set some statistics
    num_lines_used = len(wavec)
    mean_wave_lines = np.nanmean(wavec)
    mean_lande_lines = np.nanmean(lande)
    # -------------------------------------------------------------------------
    # log the number of valid lines after filtering
    margs = [num_lines_used]
    WLOG(params, '', textentry('40-021-00030', args=margs))
    # -------------------------------------------------------------------------
    # get weight from masks
    weight = wavec * depth * lande
    # normalize weight
    weight = weight / np.max(weight)
    # -------------------------------------------------------------------------
    # push values into props
    props['LSD_LINES_WLC'] = wavec
    props['LSD_LINES_ZNUMBER'] = znum
    props['LSD_LINES_DEPTH'] = depth
    props['LSD_LINES_POL_WEIGHT'] = weight
    props['LSD_LINES_LANDE'] = lande
    props['LSD_LINES_POL_EXC_POTENTIAL'] = excpotf
    props['LSD_LINES_POL_FLAG'] = flag
    props['LSD_MASK_FILE'] = os.path.basename(maskpath)
    props['LSD_LINES_NUM_MASK'] = lines_num_mask
    props['LSD_LINES_NUM_USED'] = num_lines_used
    props['LSD_LINES_MEAN_WAVE'] = mean_wave_lines
    props['LSD_LINES_MEAN_LANDE'] = mean_lande_lines
    # set source
    keys = ['LSD_LINES_WLC', 'LSD_LINES_ZNUMBER', 'LSD_LINES_DEPTH',
            'LSD_LINES_POL_WEIGHT', 'LSD_LINES_LANDE', 'LSD_MASK_FILE',
            'LSD_LINES_POL_EXC_POTENTIAL', 'LSD_LINES_POL_FLAG',
            'LSD_LINES_NUM_MASK', 'LSD_LINES_NUM_USED', 'LSD_LINES_MEAN_WAVE',
            'LSD_LINES_MEAN_LANDE']
    props.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # return the prop dictionary
    return props


def get_wl_ranges(params: ParamDict, props: ParamDict) -> ParamDict:
    """
    Function to generate a list of spectral ranges covering all spectral
    lines in the CCF mask, where the width of each individual range is
    defined by the LSD velocity vector

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_POLAR_LSD_V0: initial velocity for LSD profile
            IC_POLAR_LSD_VF: final velocity for LSD profile

    :param props: parameter dictionary, ParamDict to store data
        LSD_LINES_WLC: numpy array (1D), central wavelengths

    :return props: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
            LSD_LINES_WLRANGES: array of float pairs for wavelength ranges

    """
    # set function name
    func_name = display_func('get_wl_ranges', __NAME__)
    # -------------------------------------------------------------------------
    # set initial and final velocity
    vinit = params['POLAR_LSD_V0']
    vfinal = params['POLAR_LSD_VF']
    # get parameters from props
    wavec = props['LSD_LINES_WLC']
    # -------------------------------------------------------------------------
    # define vector of spectral ranges covering only regions around lines
    # work out the delta wavelength
    dwl = wavec * (vfinal - vinit) / (2. * speed_of_light)
    # get the initial and final wavelength of each line
    wlrange_tmp_init = wavec - dwl
    wlrange_tmp_final = wavec + dwl
    # -------------------------------------------------------------------------
    # initialize final vector of spectral ranges
    wl_ranges_init = []
    wl_ranges_final = []
    # -------------------------------------------------------------------------
    # initialize current wl0 and wlf
    current_wl_init = float(wlrange_tmp_init[0], )
    current_wl_final = float(wlrange_tmp_final[0])
    # merge overlapping ranges
    for it in range(len(wlrange_tmp_init)):
        # get iteration initial and final values
        iter_wl_init = wlrange_tmp_init[it]
        iter_wl_final = wlrange_tmp_final[it]
        # if the initial value is less than current final then we move
        # the current final to the new final value
        if iter_wl_init <= current_wl_final:
            current_wl_final = iter_wl_final
        else:
            wl_ranges_init.append(current_wl_init)
            wl_ranges_final.append(current_wl_final)
            # update the current value
            current_wl_init = float(iter_wl_init)
            current_wl_final = float(iter_wl_final)
    # append last range
    wl_ranges_init.append(current_wl_init)
    wl_ranges_final.append(current_wl_final)
    # -------------------------------------------------------------------------
    # add to the data props
    props['LSD_LINES_WLRANGES_INIT'] = wl_ranges_init
    props['LSD_LINES_WLRANGES_FINAL'] = wl_ranges_final
    # -------------------------------------------------------------------------
    # set source
    props.set_sources(['LSD_LINES_WLRANGES_INIT', 'LSD_LINES_WLRANGES_FINAL'],
                      func_name)
    # -------------------------------------------------------------------------
    # return data props
    return props


def prepare_polarimetry_data(params: ParamDict, props: ParamDict) -> ParamDict:
    """
    Function to prepare polarimetry data for LSD analysis.

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            IC_POLAR_LSD_NORMALIZE: bool, normalize Stokes I data

    :param props: parameter dictionary, ParamDict to store data
        Must contain at least:
            GLOBAL_WAVEMAP: numpy array (2D), wavelength data
            STOKESI: numpy array (2D), Stokes I data
            STOKESIERR: numpy array (2D), errors of Stokes I
            POL: numpy array (2D), degree of polarization data
            POLERR' numpy array (2D), errors of degree of polarization
            NULL2: numpy array (2D), 2nd null polarization

    :return props: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
            LSD_WAVE: numpy array (1D), wavelength data
            LSD_FLUX: numpy array (1D), Stokes I data
            LSD_FLUXERR: numpy array (1D), errors of Stokes I
            LSD_POL: numpy array (1D), degree of polarization data
            LSD_POLERR: numpy array (1D), errors of polarization
            LSD_NULL: numpy array (1D), 2nd null polarization

    """
    # set function name
    func_name = display_func('prepare_polarimetry_data', __NAME__)
    # get parameters from params
    normalize = params['POLAR_LSD_NORMALIZE']
    # get input arrays
    wavemap = props['GLOBAL_WAVEMAP']
    stokesi, stokesierr = props['STOKESI'], props['STOKESIERR']
    pol, polerr = props['POL'], props['POLERR']
    null1, null2 = props['NULL1'], props['NULL2']
    # -------------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    # -------------------------------------------------------------------------
    # get the shape of pol
    ydim, xdim = pol.shape
    # -------------------------------------------------------------------------
    # get wavelength ranges to be considered in each spectral order
    ordermask = pconst.GET_LSD_ORDER_RANGES()
    # -------------------------------------------------------------------------
    # initialize output data vectors
    lsd_wave, lsd_flux, lsd_fluxerr = [], [], []
    lsd_pol, lsd_polerr, lsd_null = [], [], []
    # -------------------------------------------------------------------------
    # loop over each order
    for order_num in range(ydim):
        # mask NaN values
        mask = np.isfinite(stokesi[order_num])
        mask &= np.isfinite(stokesierr[order_num])
        mask &= np.isfinite(pol[order_num]) & np.isfinite(polerr[order_num])
        mask &= np.isfinite(null1[order_num]) & np.isfinite(null2[order_num])
        # make values where stokes I is positive
        mask &= stokesi[order_num] > 0
        # ---------------------------------------------------------------------
        # set order wavelength limits
        wl0, wlf = ordermask[order_num][0], ordermask[order_num][1]
        # create wavelength mask
        mask &= wavemap[order_num] > wl0
        mask &= wavemap[order_num] < wlf
        # ---------------------------------------------------------------------
        # test if order is not empty
        if np.sum(mask) > 0:
            # mask arrays for this order
            ordwave = wavemap[order_num][mask]
            ordflux = stokesi[order_num][mask]
            ordfluxerr = stokesierr[order_num][mask]
            ordpol = pol[order_num][mask]
            ordpolerr = polerr[order_num][mask]
            ordnull = null2[order_num][mask]
            # -----------------------------------------------------------------
            # deal with normalization by continuum
            if normalize:
                # measure continuum
                # TODO: Should be in constant file
                kwargs = dict(binsize=80, overlap=15, window=3,
                              mode='max', use_linear_fit=True)
                cont, xbin, ybin = gen_pol.continuum(params, ordwave, ordflux,
                                                     **kwargs)
                # normalize flux
                ordflux = ordflux / cont
                ordfluxerr = ordfluxerr / cont
            # -----------------------------------------------------------------
            # append data to output vector
            lsd_wave += list(ordwave)
            lsd_flux += list(ordflux)
            lsd_fluxerr += list(ordfluxerr)
            lsd_pol += list(ordpol)
            lsd_polerr += list(ordpolerr)
            lsd_null += list(ordnull)
    # -------------------------------------------------------------------------
    # add back to props
    props['LSD_WAVE'] = np.array(lsd_wave)
    props['LSD_FLUX'] = np.array(lsd_flux)
    props['LSD_FLUXERR'] = np.array(lsd_fluxerr)
    props['LSD_POL'] = np.array(lsd_pol)
    props['LSD_POLERR'] = np.array(lsd_polerr)
    props['LSD_NULL'] = np.array(lsd_null)
    # set source
    keys = ['LSD_WAVE', 'LSD_FLUX', 'LSD_FLUXERR', 'LSD_POL', 'LSD_POLERR',
            'LSD_NULL']
    props.set_sources(keys, func_name)
    # return data parameter dictionary
    return props


def lsd_analysis(params: ParamDict, props: ParamDict) -> ParamDict:
    """
    Function to perform Least Squares Deconvolution (LSD) analysis.

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            POLAR_LSD_V0: initial velocity for LSD profile
            POLAR_LSD_VF: final velocity for LSD profile
            POLAR_LSD_NP: number of points in the LSD profile

    :param props: parameter dictionary, ParamDict to store data
        Must contain at least:
            LSD_WAVE: numpy array (1D), wavelength data
            LSD_STOKESI: numpy array (1D), Stokes I data
            LSD_STOKESIERR: numpy array (1D), errors of Stokes I
            LSD_POL: numpy array (1D), degree of polarization data
            LSD_POLERR: numpy array (1D), errors of polarization
            LSD_NULL: numpy array (1D), 2nd null polarization
            LSD_LINES_WLC: numpy array (1D), central wavelengths
            LSD_LINES_DEPTH: numpy array (1D), line depths
            LSD_LINES_POL_WEIGHT: numpy array (1D),
                                  line weights = depth * lande * wlc

    :return loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
            LSD_VELOCITIES: numpy array (1D), LSD profile velocities
            LSD_STOKESI: numpy array (1D), LSD profile for Stokes I
            LSD_STOKESI_MODEL: numpy array (1D), LSD gaussian model
                               profile for Stokes I
            LSD_STOKESVQU: numpy array (1D), LSD profile for Stokes
                           Q,U,V polarimetry spectrum
            LSD_NULL: numpy array (1D), LSD profile for null
                      polarization spectrum
    """
    # set function name
    func_name = display_func('lsd_analysis', __NAME__)
    # initialize variables to define velocity vector of output LSD profile
    vinit = params['POLAR_LSD_V0']
    vfinal = params['POLAR_LSD_VF']
    npoints = params['POLAR_LSD_NP']
    remove_edges = params['POLAR_LSD_REMOVE_EDGES']
    # get parameters from props
    lsd_wave = props['LSD_WAVE']
    lsd_lines_wlc = props['LSD_LINES_WLC']
    lsd_lines_depth = props['LSD_LINES_DEPTH']
    lsd_lines_pol_weight = props['LSD_LINES_POL_WEIGHT']
    lsd_flux = props['LSD_FLUX']
    lsd_fluxerr = props['LSD_FLUXERR']
    lsd_pol = props['LSD_POL']
    lsd_polerr = props['LSD_POLERR']
    lsd_null = props['LSD_NULL']
    # -------------------------------------------------------------------------
    # create velocity vector for output LSD profile
    lsd_velocities = np.linspace(vinit, vfinal, npoints)
    # -------------------------------------------------------------------------
    # create line pattern matrix for flux LSD
    lpout = line_pattern_matrix(lsd_wave, lsd_lines_wlc, lsd_lines_depth,
                                lsd_lines_pol_weight, lsd_velocities)
    flux_lpm, pol_lpm = lpout
    # -------------------------------------------------------------------------
    # calculate flux LSD profile
    fluxres = 1.0 - lsd_flux
    lprout = calculate_lsd_profile(params, fluxres, lsd_fluxerr,
                                   lsd_velocities, flux_lpm, normalize=False)
    lsd_stokesi, lsd_stokesi_err = lprout
    # -------------------------------------------------------------------------
    # calculate model Stokes I spectrum
    # lsd_stokesi_model = 1.0 - flux_lpm.dot(lsd_stokesi)
    # -------------------------------------------------------------------------
    # uncomment below to check model Stokes I spectrum
    # plt.plot(loc['LSD_WAVE'],loc['LSD_FLUX'])
    # plt.plot(loc['LSD_WAVE'],loc['LSD_STOKESI_MODEL'])
    # plt.show()
    # -------------------------------------------------------------------------
    # return profile to standard natural shape (as absorption)
    lsd_stokesi = 1.0 - lsd_stokesi
    # -------------------------------------------------------------------------
    # fit gaussian to the measured flux LSD profile
    fout = fit_gaussian_to_lsd_profile(params, lsd_velocities, lsd_stokesi)
    lsd_stokesi_model, lsd_fit_rv, lsd_fit_resol = fout
    # -------------------------------------------------------------------------
    # calculate polarimetry LSD profile
    vquout = calculate_lsd_profile(params, lsd_pol, lsd_polerr,
                                   lsd_velocities, pol_lpm)
    lsd_stokesvqu, lsd_stokesvqu_err = vquout
    # -------------------------------------------------------------------------
    # calculate model Stokes VQU spectrum
    lsd_pol_model = pol_lpm.dot(lsd_stokesvqu)
    # -------------------------------------------------------------------------
    # uncomment below to check model Stokes VQU spectrum
    # plt.errorbar(loc['LSD_WAVE'], loc['LSD_POL'],
    #              yerr=loc['LSD_POLERR'], fmt='.')
    # plt.plot(loc['LSD_WAVE'], loc['LSD_POL_MODEL'], '-')
    # plt.show()
    # -------------------------------------------------------------------------
    # calculate null polarimetry LSD profile
    nullout = calculate_lsd_profile(params, lsd_null, lsd_polerr,
                                    lsd_velocities, pol_lpm)
    lsd_null, lsd_nullerr = nullout
    # -------------------------------------------------------------------------
    # make sure output arrays are numpy arrays and remove edges if required
    lsd_velocities = _remove_edges(lsd_velocities, remove_edges)
    lsd_stokesvqu = _remove_edges(lsd_stokesvqu, remove_edges)
    lsd_stokesvqu_err = _remove_edges(lsd_stokesvqu_err, remove_edges)
    lsd_stokesi = _remove_edges(lsd_stokesi, remove_edges)
    lsd_stokesi_err = _remove_edges(lsd_stokesi_err, remove_edges)
    lsd_null = _remove_edges(lsd_null, remove_edges)
    lsd_nullerr = _remove_edges(lsd_nullerr, remove_edges)
    lsd_stokesi_model = _remove_edges(lsd_stokesi_model, remove_edges)
    # -------------------------------------------------------------------------
    # calculate statistical quantities
    lsd_pol_mean = np.nanmean(lsd_pol)
    lsd_pol_stddev = np.nanstd(lsd_pol)
    lsd_pol_median = np.nanmedian(lsd_pol)
    lsd_pol_medabsdev = np.nanmedian(np.abs(lsd_pol - lsd_pol_median))
    lsd_stokesvqu_mean = np.nanmean(lsd_stokesvqu)
    lsd_stokesvqu_stddev = np.nanstd(lsd_stokesvqu)
    lsd_null_mean = np.nanmean(lsd_null)
    lsd_null_stddev = np.nanstd(lsd_null)
    # -------------------------------------------------------------------------
    # add to props data parameter dictionary
    props.set('LSD_VELOCITIES', lsd_velocities, source=func_name)
    props.set('LSD_STOKESI', lsd_stokesi, source=func_name)
    props.set('LSD_STOKESI_ERR', lsd_stokesi_err, source=func_name)
    props.set('LSD_STOKESI_MODEL', lsd_stokesi_model, source=func_name)
    props.set('LSD_POL_MODEL', lsd_pol_model, source=func_name)
    props.set('LSD_FIT_RV', lsd_fit_rv, source=func_name)
    props.set('LSD_FIT_RESOL', lsd_fit_resol, source=func_name)
    props.set('LSD_STOKESVQU', lsd_stokesvqu, source=func_name)
    props.set('LSD_STOKESVQU_ERR', lsd_stokesvqu_err, source=func_name)
    props.set('LSD_NULL', lsd_null, source=func_name)
    props.set('LSD_NULL_ERR', lsd_nullerr, source=func_name)
    props.set('LSD_POL_MEAN', lsd_pol_mean, source=func_name)
    props.set('LSD_POL_STDDEV', lsd_pol_stddev, source=func_name)
    props.set('LSD_POL_MEDIAN', lsd_pol_median, source=func_name)
    props.set('LSD_POL_MEDABSDEV', lsd_pol_medabsdev, source=func_name)
    props.set('LSD_STOKESVQU_MEAN', lsd_stokesvqu_mean, source=func_name)
    props.set('LSD_STOKESVQU_STDDEV', lsd_stokesvqu_stddev, source=func_name)
    props.set('LSD_NULL_MEAN', lsd_null_mean, source=func_name)
    props.set('LSD_NULL_STDDEV', lsd_null_stddev, source=func_name)
    # -------------------------------------------------------------------------
    # return the props data parameter dictionary
    return props


def nrefrac(wavelength: np.ndarray, density: float = 1.0):
    """
    Calculate refractive index of air from Cauchy formula.

    :param wavelength: wavelength vector in angstroms
    :param density: density in ??

    Input: wavelength in nm, density of air in amagat (relative to STP,
    e.g. ~10% decrease per 1000m above sea level).
    Returns N = (n-1) * 1.e6.
    """
    # The IAU standard for conversion from air to vacuum wavelengths is given
    # in Morton (1991, ApJS, 77, 119). For vacuum wavelengths (VAC) in
    # Angstroms, convert to air wavelength (AIR) via:

    #  AIR = VAC / (1.0 + 2.735182E-4 + 131.4182 / VAC^2 + 2.76249E8 / VAC^4)
    wl2inv = (1.e3 / wavelength) ** 2
    refracstp = 272.643 + 1.2288 * wl2inv + 3.555e-2 * wl2inv ** 2
    # return wavelengths in a vacuum
    return density * refracstp


def convert_vacuum_to_air_wl(vacuum_wavelength: np.ndarray,
                             air_density=1.0) -> np.ndarray:
    """
    Convert vacuum wavelengths to air wavelengths at a certain air density

    :param vacuum_wavelength: np.ndarray, the vacuum wavelength vector
    :param air_density: float, the air density

    :return: np.ndarray, the air wavelength vector
    """
    # get the refractive index
    nrefractive = nrefrac(vacuum_wavelength, density=air_density)
    # get the air wavelengths
    air_wavelength = vacuum_wavelength / (1. + (1.e-6 * nrefractive))
    # return the air wavelengths
    return air_wavelength


def convert_air_to_vacuum_wl(air_wavelength: np.ndarray,
                             air_density: float = 1.0) -> np.ndarray:
    """
    Convert air wavelengths to vacuum wavelengths at a certain air density

    :param air_wavelength: np.ndarray, the air wavelength vector
    :param air_density: float, the air density

    :return: np.ndarray, the vacuum wavelength vector
    """
    # get the refractive index
    nrefractive = nrefrac(air_wavelength, density=air_density)
    # get the vacuum wavelengths
    vacuum_wavelength = air_wavelength * (1. + 1.e-6 * nrefractive)
    # return the vacuum wavelengths
    return vacuum_wavelength


def _remove_edges(vector: np.ndarray, remove_edges: bool = True,
                  size: int = 1) -> np.ndarray:
    """
    Remove edges or just copy array

    :param vector: np.ndarray, array to remove edges
    :param remove_edges: bool, if True removes edges, else just copies
    :param size: int, the size in pixels to remove from each side

    :return: np.ndarray, the updated vector
    """
    if remove_edges:
        return np.array(vector[size:-(size + 1)])
    else:
        return np.array(vector)


def line_pattern_matrix(wavemap: np.ndarray, wavec: np.ndarray,
                        depth: np.ndarray, weight: np.ndarray,
                        velocities: np.ndarray
                        ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Function to calculate the line pattern matrix M given in Eq (4) of paper
    Donati et al. (1997), MNRAS 291, 658-682

    :param wavemap: numpy array (1D), input wavelength data
                   (size n = spectrum size)
    :param wavec: numpy array (1D), central wavelengths
                  (size = number of lines)
    :param depth: numpy array (1D), line depths (size = number of lines)
    :param weight: numpy array (1D), line polar weights (size = number of lines)
    :param velocities: numpy array (1D), , LSD profile velocity vector
                       (size = m)

    :return flux_lpm, pol_lpm
            flux_lpm: numpy array (2D) of size n x m, line pattern matrix for
                      flux LSD.
            pol_lpm: numpy array (2D) of size n x m, line pattern matrix for
                     polar LSD.
    """
    # set function name
    _ = display_func('line_pattern_matrix', __NAME__)
    # set number of points and velocity (km/s) limits in LSD profile
    numlines, vinit, vfinal = len(velocities), velocities[0], velocities[-1]
    # set number of spectral points
    numpixels = len(wavemap)
    # initialize line pattern matrix for flux LSD
    flux_lpm = np.zeros((numpixels, numlines))
    # initialize line pattern matrix for polar LSD
    pol_lpm = np.zeros((numpixels, numlines))
    # -------------------------------------------------------------------------
    # set values of line pattern matrix M
    for line_it in range(len(wavec)):
        # get the wavelength profile
        waveprofile = wavec[line_it] * (1 + velocities / speed_of_light)
        # make a line mask
        linemask = (wavemap >= waveprofile[0]) & (wavemap <= waveprofile[-1])
        # get the positions of linesmask
        linepos = np.where(linemask)[0]
        # Calculate line velocities for the observed wavelength sampling:
        #     v = c Δλ / λ
        wavediff = wavemap[linemask] - wavec[line_it]
        linevelo = speed_of_light * wavediff / wavec[line_it]
        # loop around pixels and calculate the line pattern matrix for
        #   flux and polar - for all valid positions
        for pix in range(len(linepos)):
            # linear interpolation
            # -----------------------------------------------------------------
            # find position in velocities where our velocity should be inserted
            jpos = np.searchsorted(velocities, linevelo[pix], side='right')
            # -----------------------------------------------------------------
            # get the weight of the velocity
            vpart1 = linevelo[pix] - velocities[jpos - 1]
            vpart2 = velocities[jpos] - velocities[jpos - 1]
            velo_weight = vpart1 / vpart2
            # -----------------------------------------------------------------
            # calculate the polar line pattern matrix element
            pol_lpm_pix1 = weight[line_it] * (1.0 - velo_weight)
            pol_lpm_pix2 = weight[line_it] * velo_weight
            # add to polar line pattern matrix
            pol_lpm[linepos[pix]][jpos - 1] = pol_lpm_pix1
            pol_lpm[linepos[pix]][jpos] = pol_lpm_pix2
            # -----------------------------------------------------------------
            # calculate the flux line pattern matrix element
            flux_lpm_pix1 = depth[line_it] * (1.0 - velo_weight)
            flux_lpm_pix2 = depth[line_it] * velo_weight
            # add to polar line pattern matrix
            flux_lpm[linepos[pix]][jpos - 1] = flux_lpm_pix1
            flux_lpm[linepos[pix]][jpos] = flux_lpm_pix2
    # ------------------------------------------------------------------------
    # return the
    return flux_lpm, pol_lpm


def calculate_lsd_profile(params: ParamDict, flux: np.ndarray,
                          fluxerr: np.ndarray, velocities: np.ndarray,
                          lpm: np.ndarray, normalize: bool = False
                          ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Function to calculate the LSD profile Z given in Eq (4) of paper
    Donati et al. (1997), MNRAS 291, 658-682

    :param params: ParamDict, parameter dictionary of constants
    :param flux: numpy array (1D), input flux or polarimetry data (size = n)
    :param fluxerr: numpy array (1D), input flux or polarimetry error data
                    (size = n)
    :param velocities: numpy array (1D), , LSD profile velocity vector
                       (size = m)
    :param lpm: numpy array (2D) of size n x m, line pattern matrix for LSD.
    :param normalize: bool, to calculate a continuum and normalize profile

    :return: tuple, velocity profile and velocity profile error, both are
             numpy array (1D) of size lpm, LSD profile.
    """
    # -------------------------------------------------------------------------
    # First calculate transpose of M
    #   MT = M.T
    lpmt = np.matrix.transpose(lpm)
    # -------------------------------------------------------------------------
    # Initialize matrix for dot product between MT . S^2
    lpmt_x_s2 = np.zeros_like(lpmt)
    # Then calculate dot product between MT . S^2, where S^2=covariance matrix
    #   MT.S^2 = MT.(1/FLUXERR^2)
    # loop around each matrix element
    for it in range(lpmt.shape[0]):
        lpmt_x_s2[it] = lpmt[it] / (fluxerr ** 2)
    # -------------------------------------------------------------------------
    # calculate autocorrelation
    #  MT.S^2.M
    lpmt_x_s2_x_lpm = lpmt_x_s2.dot(lpm)
    # -------------------------------------------------------------------------
    # calculate the inverse of autocorrelation using numpy pinv method
    #  INV(MT.S^2.M)
    lpmt_x_s2_x_lpm_inv = np.linalg.pinv(lpmt_x_s2_x_lpm)
    # -------------------------------------------------------------------------
    # calculate cross correlation term
    # MT.S^2.FLUX
    x_corr_term = lpmt_x_s2.dot(flux)
    # -------------------------------------------------------------------------
    # calculate velocity profile
    # INV(MT.S^2.M).(MT.S^2.FLUX)
    velo_profile = lpmt_x_s2_x_lpm_inv.dot(x_corr_term)
    # -------------------------------------------------------------------------
    # calculate error of velocity profile
    # SQRT(DIAG(INV(MT.S^2.M))
    velo_profile_err = np.sqrt(np.diag(lpmt_x_s2_x_lpm_inv))
    # -------------------------------------------------------------------------
    # deal with continuum normalization
    if normalize:
        # calculate continuum of LSD profile to remove trend
        velo_cont, _, _ = gen_pol.continuum(params, velocities, velo_profile,
                                            binsize=20, overlap=5,
                                            sigmaclip=3.0, window=2,
                                            mode="median", use_linear_fit=False)
        # calculate normalized and detrended LSD profile
        velo_profile = velo_profile / velo_cont
        velo_profile_err = velo_profile_err / velo_cont
    # -------------------------------------------------------------------------
    # make sure velo profile and uncertain are arrays
    velo_profile = np.array(velo_profile)
    velo_profile_err = np.array(velo_profile_err)
    # -------------------------------------------------------------------------
    # return the velocity of the profile and its uncertainty
    return velo_profile, velo_profile_err


def fit_gaussian_to_lsd_profile(params: ParamDict, velocities: np.ndarray,
                                profile: np.ndarray
                                ) -> Tuple[np.ndarray, float, float]:
    """
        Function to fit gaussian to LSD Stokes I profile.

        :param params: ParamDict, parameter dictionary of constants
        :param velocities: numpy array (1D), input velocity data
        :param profile: numpy array (1D), input LSD profile data

        :return z_gauss, RV, resolving_power:
            z_gauss: numpy array (1D), gaussian fit to LSD profile (same size
                    as input vels and Z)
            RV: float, velocity of minimum obtained from gaussian fit
            resolving_power: float, spectral resolving power calculated from
                            sigma of gaussian fit
        """
    # set function name
    func_name = display_func('fit_gaussian_to_lsd_profile', __NAME__)
    # get guess at resolving power from params
    resolving_power_guess = params['POLAR_LSD_RES_POWER_GUESS']
    # get the position of minimum profile
    pos = np.argmin(profile)
    # obtain velocity at minimum
    min_velo = velocities[pos]
    # get median amplitude of velocity profile
    med_profile = np.median(profile)
    # get the amplitude (median - minimum)
    amplitude = np.abs(med_profile - profile[pos])
    # work out the sigma (c/(R*2.35482))
    sigma = speed_of_light / (resolving_power_guess * mp.fwhm())
    # get inverted profile
    profile_inv = 1.0 - profile
    # -------------------------------------------------------------------------
    # guess for fitting gaussian profile
    guess = [amplitude, min_velo, sigma, med_profile]
    # guess = [0.1, 0.0, 1.0]
    # -------------------------------------------------------------------------
    # noinspection PyTypeChecker
    try:
        popt, pcov = curve_fit(mp.gauss_function, velocities, profile_inv,
                               p0=guess)
    except Exception as e:
        # Log warning: Failed to fit gaussian to LSD profile\n\t{0}: {1}'
        wargs = [type(e), str(e), func_name]
        WLOG(params, 'warning', textentry('10-021-00008', args=wargs))
        # set coefficients to guess
        popt = guess
    # -------------------------------------------------------------------------
    # initialize output profile vector
    profile_gauss = np.zeros_like(velocities)
    # loop around all velocities and populate gaussian fit to profile
    for it in range(len(profile_gauss)):
        profile_gauss[it] = mp.gauss_function(velocities[it], *popt)
    # -------------------------------------------------------------------------
    # invert fit profile
    profile_gauss = 1.0 - profile_gauss
    # -------------------------------------------------------------------------
    # calculate full width at half maximum (fwhm)
    fwhm = mp.fwhm() * popt[2]
    # -------------------------------------------------------------------------
    # calculate resolving power from mesasured fwhm
    resolving_power = speed_of_light / fwhm
    # -------------------------------------------------------------------------
    # set radial velocity directly from fitted v_0
    rv = popt[1]
    # -------------------------------------------------------------------------
    # return fitted profile, radial velocity and resolving power
    return profile_gauss, rv, resolving_power


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

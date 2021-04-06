#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-25 at 13:25

@author: cook
"""
import numpy as np
import warnings

from apero.base import base
from apero.core import math as mp
from apero import lang
from apero.core import constants
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_startup
from apero.core.utils import drs_data
from apero.io import drs_table
from apero.science import extract

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
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# LSD wrapper function
# =============================================================================
def lsd_analysis_wrapper(params: ParamDict, props: ParamDict) -> ParamDict:

    # select the correct lsd mask and load values into props
    props = load_lsd_mask(params, props)

    # TODO: --------------------------------------------------------------------
    # TODO: Got to here
    # TODO: --------------------------------------------------------------------

    # get wavelength ranges covering spectral lines in the ccf mask
    props = get_wl_ranges(params, props)

    # prepare polarimetry data
    props = prepare_polarimetry_data(params, props)

    # call function to perform lsd analysis
    props = lsd_analysis(params, props)

    return props


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
    # TODO: move text to language database
    msg = 'Selected input LSD mask: {0}'
    margs = [maskpath]
    WLOG(params, 'info', msg.format(*margs))
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
    # TODO: move teext to language database
    msg = 'Number of lines in the original mask = {0}'
    margs = [len(wavec)]
    WLOG(params, '', msg.format(*margs))
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
    mean_lande_lines =np.nanmean(lande)
    # -------------------------------------------------------------------------
    # log the number of valid lines after filtering
    # TODO: move teext to language database
    msg = 'Number of lines after filtering: {0}'
    margs = [num_lines_used]
    WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # get weight from masks
    weight = maskdata['wavec'] * maskdata['depth'] * maskdata['lande']
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
    props['LSD_LINES_NUM_USED'] = num_lines_used
    props['LSD_LINES_MEAN_WAVE'] = mean_wave_lines
    props['LSD_LINES_MEAN_LANDE'] = mean_lande_lines
    # set source
    keys = ['LSD_LINES_WLC', 'LSD_LINES_ZNUMBER' ,'LSD_LINES_DEPTH',
            'LSD_LINES_POL_WEIGHT', 'LSD_LINES_LANDE',
            'LSD_LINES_POL_EXC_POTENTIAL', 'LSD_LINES_POL_FLAG',
            'LSD_LINES_NUM_USED', 'LSD_LINES_MEAN_WAVE', 'LSD_LINES_MEAN_LANDE']
    props.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # return the prop dictionary
    return props


# =============================================================================
# Define quality control and writing functions
# =============================================================================


# =============================================================================
# Define worker functions
# =============================================================================
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
    wl2inv = (1.e3 / wavelength)**2
    refracstp = 272.643 + 1.2288 * wl2inv + 3.555e-2 * wl2inv**2
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
    air_wavelength = vacuum_wavelength / ( 1. + (1.e-6 * nrefractive))
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
    vacuum_wavelength = air_wavelength * ( 1. + 1.e-6 * nrefractive)
    # return the vacuum wavelengths
    return vacuum_wavelength

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

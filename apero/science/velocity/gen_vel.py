#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-21 at 12:28

@author: cook
"""
import os
import warnings
from typing import Optional, Tuple

import numpy as np
from astropy import constants as cc
from astropy import units as uu
from astropy.table import Table
from scipy.optimize import curve_fit

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_data
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.rv.gen_vel.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
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
# Define functions
# =============================================================================
def measure_fp_peaks(params: ParamDict, props: ParamDict, limit: float,
                     normpercent: float) -> ParamDict:
    """
    Measure the positions of the FP peaks
    Returns the pixels positions and Nth order of each FP peak

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
                drift_peak_border_size: int, the border size (edges in
                                        x-direction) for the FP fitting
                                        algorithm
                drift_peak_fpbox_size: int, the box half-size (in pixels) to
                                       fit an individual FP peak to - a
                                       gaussian will be fit to +/- this size
                                       from the center of the FP peak
                drift_peak_peak_sig_lim: dictionary, the sigma above the median
                                         that a peak must have to be recognised
                                         as a valid peak (before fitting a
                                         gaussian) dictionary must have keys
                                         equal to the lamp types (hc, fp)
                drift_peak_inter_peak_spacing: int, the minimum spacing between
                                               peaks in order to be recognised
                                               as a valid peak (before fitting
                                               a gaussian)
                log_opt: string, log option, normally the program name

    :param props: parameter dictionary, ParamDict containing data
            Must contain at least:
                speref: numpy array (2D), the reference spectrum
                wave: numpy array (2D), the wave solution image
                lamp: string, the lamp type (either 'hc' or 'fp')

    :param limit: float, FP peak limit for keeping a line
    :param normpercent: float, percentile to normalize by

    :return props: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                ordpeak: numpy array (1D), the order number for each valid FP
                         peak
                xpeak: numpy array (1D), the central position each gaussain fit
                       to valid FP peak
                ewpeak: numpy array (1D), the FWHM of each gaussain fit
                        to valid FP peak
                vrpeak: numpy array (1D), the radial velocity drift for each
                        valid FP peak
                llpeak: numpy array (1D), the delta wavelength for each valid
                        FP peak
                amppeak: numpy array (1D), the amplitude for each valid FP peak

    """
    func_name = __NAME__ + '.create_drift_file()'

    # get the reference data and the wave data
    speref = np.array(props['SPEREF'])
    wave = props['WAVE']
    # storage for order of peaks
    allpeaksize = []
    allordpeak = []
    allxpeak = []
    allewpeak = []
    allvrpeak = []
    allllpeak = []
    allamppeak = []
    alldcpeak = []
    allshapepeak = []

    # loop through the orders
    for order_num in range(speref.shape[0]):
        # storage for order of peaks
        ordpeak = []
        xpeak = []
        ewpeak = []
        vrpeak = []
        llpeak = []
        amppeak = []
        dcpeak = []
        shapepeak = []
        # storage of warnings
        warn_dict = dict()
        # set number of peaks rejected to zero
        nreject = 0
        # set a counter for total number of peaks
        ipeak = 0
        # get the pixels for this order
        tmp = np.array(speref[order_num, :])
        # define indices
        index = np.arange(len(tmp))
        # ------------------------------------------------------------------
        # normalize the spectrum
        tmp = tmp / mp.nanpercentile(tmp, normpercent)
        # ------------------------------------------------------------------
        # find the peaks
        with warnings.catch_warnings(record=True) as _:
            peakmask = (tmp[1:-1] > tmp[2:]) & (tmp[1:-1] > tmp[:-2])
        peakpos = np.where(peakmask)[0]
        # work out the FP width for this order
        size = int(mp.nanmedian(peakpos[1:] - peakpos[:-1]))
        # ------------------------------------------------------------------
        # mask for finding maximum peak
        mask = np.ones_like(tmp)
        # mask out the edges
        mask[:size + 1] = 0
        mask[-(size + 1):] = 0
        # ------------------------------------------------------------------
        # loop for peaks that are above a value of limit
        while mp.nanmax(mask * tmp) > limit:
            # --------------------------------------------------------------
            # find peak along the order
            maxpos = mp.nanargmax(mask * tmp)
            maxtmp = tmp[maxpos]
            # --------------------------------------------------------------
            # get the values around the max position
            index_peak = index[maxpos - size: maxpos + size]
            tmp_peak = tmp[maxpos - size: maxpos + size]
            # --------------------------------------------------------------
            # mask out this peak for next iteration of while loop
            mask[maxpos - (size // 2):maxpos + (size // 2) + 1] = 0
            # --------------------------------------------------------------
            # return the initial guess and the best fit
            p0, gg, _, warns = fit_fp_peaks(index_peak, tmp_peak, size)
            # --------------------------------------------------------------
            # only keep peaks within +/- 1 pixel of original peak
            #  (gaussian fit is to find sub-pixel value)
            cond = np.abs(maxpos - gg[1]) < 1
            if cond:
                # work out the radial velocity of the peak
                lambefore = wave[order_num, maxpos - 1]
                lamafter = wave[order_num, maxpos + 1]
                deltalam = lamafter - lambefore
                # get the radial velocity
                waveomax = wave[order_num, maxpos]
                radvel = speed_of_light_ms * deltalam / (2.0 * waveomax)
                # add to storage
                ordpeak.append(order_num)
                xpeak.append(gg[1])
                ewpeak.append(gg[2])
                vrpeak.append(radvel)
                llpeak.append(deltalam)
                amppeak.append(maxtmp)
                shapepeak.append(gg[3])
                dcpeak.append(gg[4])
            else:
                # add to rejected
                nreject += 1
            # iterator
            ipeak += 1
            # --------------------------------------------------------------
            # deal with warnings
            if warns is not None:
                if warns in warn_dict:
                    warn_dict[warns] += 1
                else:
                    warn_dict[warns] = 1
            # --------------------------------------------------------------
        # log how many FPs were found and how many rejected
        wargs = [order_num, ipeak, nreject]
        WLOG(params, '', textentry('40-018-00001', args=wargs))
        # ------------------------------------------------------------------
        # print warnings
        for key in list(warn_dict.keys()):
            wargs = [warn_dict[key], key]
            WLOG(params, 'warning', textentry('00-018-00001', args=wargs),
                 sublevel=2)
        # ------------------------------------------------------------------
        # add values to all storage (and sort by xpeak)
        indsort = np.argsort(xpeak)
        allordpeak.append(np.array(ordpeak)[indsort])
        allxpeak.append(np.array(xpeak)[indsort])
        allewpeak.append(np.array(ewpeak)[indsort])
        allvrpeak.append(np.array(vrpeak)[indsort])
        allllpeak.append(np.array(llpeak)[indsort])
        allamppeak.append(np.array(amppeak)[indsort])
        allshapepeak.append(np.array(shapepeak)[indsort])
        alldcpeak.append(np.array(dcpeak)[indsort])
        allpeaksize.append(size)
    # store values in loc
    props['ORDPEAK'] = np.concatenate(allordpeak).astype(int)
    props['XPEAK'] = np.concatenate(allxpeak)
    props['PEAK2PEAK'] = np.concatenate(allewpeak)
    props['VRPEAK'] = np.concatenate(allvrpeak)
    props['LLPEAK'] = np.concatenate(allllpeak)
    props['AMPPEAK'] = np.concatenate(allamppeak)
    props['DCPEAK'] = np.concatenate(alldcpeak)
    props['SHAPEPEAK'] = np.concatenate(allshapepeak)
    props['PEAKSIZE'] = np.array(allpeaksize)
    # set source
    keys = ['ORDPEAK', 'XPEAK', 'PEAK2PEAK', 'VRPEAK', 'LLPEAK', 'AMPPEAK',
            'DCPEAK', 'SHAPEPEAK', 'PEAKSIZE']
    props.set_sources(keys, func_name)

    # Log the total number of FP lines found
    wargs = [len(props['XPEAK'])]
    WLOG(params, 'info', textentry('40-018-00002', args=wargs))

    # return the property parameter dictionary
    return props


def fit_fp_peaks(x, y, size, return_model=False):
    # storage of warnings
    warns = None
    # get gauss function
    ea_airy = mp.ea_airy_function
    # get the guess on the maximum peak position
    maxpos = mp.nanargmax(y)
    minpos = mp.nanargmin(y)
    ymax = y[maxpos]
    ymin = y[minpos]
    # set up initial guess
    # [amp, position, period, exponent, zero point]
    p0 = [ymax - ymin, mp.nanmedian(x), size, 1.5, np.max([0, ymin])]

    # deal with bad bounds
    if warns is not None:
        popt = [np.nan, np.nan, np.nan, np.nan, np.nan]
        pcov = None
        model = np.repeat([np.nan], len(x))
    else:
        # try to fit etiennes airy function
        try:
            with warnings.catch_warnings(record=True) as _:
                # popt, pcov = curve_fit(ea_airy, x, y, p0=p0, bounds=bounds)
                # noinspection PyTupleAssignmentBalance
                popt, pcov = curve_fit(ea_airy, x, y, p0=p0)
            model = ea_airy(x, *popt)
        except ValueError as e:
            # log that ydata or xdata contains NaNs
            popt = [np.nan, np.nan, np.nan, np.nan, np.nan]
            pcov = None
            warns = '{0}: {1}'.format(type(e), e)
            model = np.repeat([np.nan], len(x))
        except RuntimeError as e:
            popt = [np.nan, np.nan, np.nan, np.nan, np.nan]
            pcov = None
            warns = '{0}: {1}'.format(type(e), e)
            model = np.repeat([np.nan], len(x))
    # deal with returning model
    if return_model:
        return p0, popt, pcov, warns, model
    else:
        # return the guess and the best fit
        return p0, popt, pcov, warns


def remove_wide_peaks(params: ParamDict, props: ParamDict,
                      cutwidth: float) -> ParamDict:
    """
    Remove peaks that are too wide

    :param params: parameter dictionary, ParamDict containing constants

    :param props: parameter dictionary, ParamDict containing data
            Must contain at least:
                ordpeak: numpy array (1D), the order number for each valid FP
                         peak
                xpeak: numpy array (1D), the central position each gaussain fit
                       to valid FP peak
                ewpeak: numpy array (1D), the FWHM of each gaussain fit
                        to valid FP peak
                vrpeak: numpy array (1D), the radial velocity drift for each
                        valid FP peak
                llpeak: numpy array (1D), the delta wavelength for each valid
                        FP peak
                amppeak: numpy array (1D), the amplitude for each valid FP peak

    :param cutwidth: float, the normalised width of FP peaks that is too
                     large

    :return props: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                ordpeak: numpy array (1D), the order number for each valid FP
                         peak (masked to remove wide peaks)
                xpeak: numpy array (1D), the central position each gaussain fit
                       to valid FP peak (masked to remove wide peaks)
                ewpeak: numpy array (1D), the FWHM of each gaussain fit
                        to valid FP peak (masked to remove wide peaks)
                vrpeak: numpy array (1D), the radial velocity drift for each
                        valid FP peak (masked to remove wide peaks)
                llpeak: numpy array (1D), the delta wavelength for each valid
                        FP peak (masked to remove wide peaks)
                amppeak: numpy array (1D), the amplitude for each valid FP peak
                         (masked to remove wide peaks)
    """
    func_name = __NAME__ + '.remove_wide_peaks()'

    # define a mask to cut out wide peaks
    mask = np.array(props['PEAK2PEAK']) < cutwidth

    # apply mask
    props['ORDPEAK'] = props['ORDPEAK'][mask]
    props['XPEAK'] = props['XPEAK'][mask]
    props['PEAK2PEAK'] = props['PEAK2PEAK'][mask]
    props['VRPEAK'] = props['VRPEAK'][mask]
    props['LLPEAK'] = props['LLPEAK'][mask]
    props['AMPPEAK'] = props['AMPPEAK'][mask]

    # check for and remove double-fitted lines
    # save old position
    props['XPEAK_OLD'] = np.copy(props['XPEAK'])
    props['ORDPEAK_OLD'] = np.copy(props['ORDPEAK'])

    # set up storage for good lines
    ordpeak_k, xpeak_k, ewpeak_k, vrpeak_k = [], [], [], []
    llpeak_k, amppeak_k = [], []

    # loop through the orders
    for order_num in range(np.shape(props['SPEREF'])[0]):
        # set up mask for the order
        gg = props['ORDPEAK'] == order_num
        # get the xvalues
        xpeak = props['XPEAK'][gg]
        # get the amplitudes
        amppeak = props['AMPPEAK'][gg]
        # get peak spacing
        peak_spacing = props['PEAKSIZE'][order_num] / 2
        # get the points where two peaks are spaced by < peak_spacing
        ind = np.argwhere(xpeak[1:] - xpeak[:-1] < peak_spacing)
        # get the indices of the second peak of each pair
        ind2 = ind + 1
        # initialize mask with the same size as xpeak
        xmask = np.ones(len(xpeak), dtype=bool)
        # mask the peak with the lower amplitude of the two
        for i in range(len(ind)):
            if amppeak[ind[i]] < amppeak[ind2[i]]:
                xmask[ind[i]] = False
            else:
                xmask[ind2[i]] = False
        # save good lines
        ordpeak_k += list(props['ORDPEAK'][gg][xmask])
        xpeak_k += list(props['XPEAK'][gg][xmask])
        ewpeak_k += list(props['PEAK2PEAK'][gg][xmask])
        vrpeak_k += list(props['VRPEAK'][gg][xmask])
        llpeak_k += list(props['LLPEAK'][gg][xmask])
        amppeak_k += list(props['AMPPEAK'][gg][xmask])

    # replace FP peak arrays in loc
    props['ORDPEAK'] = np.array(ordpeak_k)
    props['XPEAK'] = np.array(xpeak_k)
    props['PEAK2PEAK'] = np.array(ewpeak_k)
    props['VRPEAK'] = np.array(vrpeak_k)
    props['LLPEAK'] = np.array(llpeak_k)
    props['AMPPEAK'] = np.array(amppeak_k)

    # append this function to sources
    keys = ['ordpeak', 'xpeak', 'PEAK2PEAK', 'vrpeak', 'llpeak', 'amppeak']
    props.append_sources(keys, func_name)

    # log number of lines removed for suspicious width
    # noinspection PyTypeChecker
    wargs = [mp.nansum(~mask)]
    WLOG(params, 'info', textentry('40-018-00003', args=wargs))

    # log number of lines removed as double-fitted
    wargs = [len(props['XPEAK_OLD']) - len(props['XPEAK'])]
    WLOG(params, 'info', textentry('40-018-00004', args=wargs))

    # return props
    return props


def get_ccf_teff_mask(params: ParamDict,
                      header: drs_fits.Header,
                      assetsdir: Optional[str] = None,
                      mask_dir: Optional[str] = None) -> Tuple[str, str]:
    """
    Decide on a mask based on effective temperature (from the header)

    :param params: ParamDict, the parameter dictionary of constants
    :param header: fits Header, to get temperature from
    :param assetsdir: str, the assets directory (overrides DRS_DATA_ASSETS)
    :param mask_dir: str, the mask directory (overrides CCF_MASK_PATH)

    :return: tuple, 1. str, the ccf mask to use 2. str, the format
             for astropy.table.Table.read
    """
    # set function name
    func_name = display_func('get_ccf_teff_mask', __NAME__)
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'CCF_MASK_PATH', func=func_name,
                       override=mask_dir)
    # get temperature header key
    teff_key = params['KW_DRS_TEFF'][0]
    # get teff mask file
    teff_masks_file = params['CCF_TEFF_MASK_TABLE']
    # get teff mask datatype
    teff_masks_fmt = params.instances['CCF_TEFF_MASK_TABLE'].datatype
    # get temperature from header
    if teff_key in header:
        teff = float(header[teff_key])
        # log that we are using a Teff key for mask
        WLOG(params, '', textentry('40-020-00008', args=[teff]))
    else:
        # error msg: Object temperature key "{0}" not in header'
        eargs = [teff_key]
        WLOG(params, 'error', textentry('09-020-00008', args=eargs))
        # should never get here
        return '', ''
    # ---------------------------------------------------------------------
    # load teff masks file
    teff_mask_path = os.path.join(assetdir, relfolder, teff_masks_file)
    teff_masks = Table.read(teff_mask_path, format=teff_masks_fmt)
    # ---------------------------------------------------------------------
    # find default
    if 'default' not in teff_masks['kind']:
        # error msg: Cannot use {0} - must have default value in kind column
        eargs = [teff_masks_file]
        WLOG(params, 'error', textentry('09-020-00009', args=eargs))
        return '', ''
    # get position of defaults
    default_mask = teff_masks['kind'] == 'default'
    pos = np.where(default_mask)[0][0]
    # use mask for default
    default_maskfile = str(teff_masks['mask'][pos])
    default_datatype = str(teff_masks['datatype'][pos])
    # remove default from teff_masks
    teff_masks = teff_masks[~default_mask]
    # ---------------------------------------------------------------------
    # deal with teff choosing mask
    # ---------------------------------------------------------------------
    # non finite values should use default mask
    if not np.isfinite(teff):
        # return the mask and the file type (i.e. fits, ascii)
        return default_maskfile, default_datatype
    # loop around rows in teff_masks
    for row in range(len(teff_masks)):
        # get teff limits
        cond1 = teff >= teff_masks['teff_min'][row]
        cond2 = teff < teff_masks['teff_max'][row]
        # if teff satisfies both limits return here
        if cond1 and cond2:
            # get this rows mask and data type
            row_maskfile = str(teff_masks['mask'][row])
            row_datatype = str(teff_masks['datatype'][row])
            # return the mask and the file type (i.e. fits, ascii)
            return row_maskfile, row_datatype
    # ---------------------------------------------------------------------
    # else we use the default for anything else
    return default_maskfile, default_datatype


def get_ccf_mask(params, filename, mask_width, mask_units='nm',
                 fmt=None):
    func_name = __NAME__ + '.get_ccf_mask()'
    # load table
    table, absfilename = drs_data.load_ccf_mask(params, filename=filename,
                                                fmt=fmt)
    # convert to floats
    ll_mask_e = np.array(table['ll_mask_e']).astype(float)
    ll_mask_s = np.array(table['ll_mask_s']).astype(float)
    # calculate the difference in mask_e and mask_s
    ll_mask_d = ll_mask_e - ll_mask_s
    ll_mask_ctr = ll_mask_s + ll_mask_d * 0.5
    # if mask_width > 0 ll_mask_d is multiplied by mask_width/c
    if mask_width > 0:
        ll_mask_d = mask_width * ll_mask_s / speed_of_light
    # make w_mask an array
    w_mask = np.array(table['w_mask']).astype(float)
    # ----------------------------------------------------------------------
    # deal with the units of ll_mask_d and ll_mask_ctr
    # must be returned in nanometers
    # ----------------------------------------------------------------------
    # get unit object from mask units string
    try:
        unit = getattr(uu, mask_units)
    except Exception as e:
        # log error
        eargs = [mask_units, type(e), e, func_name]
        WLOG(params, 'error', textentry('09-020-00002', args=eargs))
        return None, None, None
    # add units
    ll_mask_d = ll_mask_d * unit
    ll_mask_ctr = ll_mask_ctr * unit
    # convert to nanometers
    ll_mask_d = ll_mask_d.to(uu.nm).value
    ll_mask_ctr = ll_mask_ctr.to(uu.nm).value
    # ----------------------------------------------------------------------
    # return the size of each pixel, the central point of each pixel
    #    and the weight mask
    return ll_mask_d, ll_mask_ctr, w_mask


def delta_v_rms_2d(spe, wave, sigdet, threshold, size):
    """
    Compute the photon noise uncertainty for all orders (for the 2D image)

    :param spe: numpy array (2D), the extracted spectrum
                size = (number of orders by number of columns (x-axis))
    :param wave: numpy array (2D), the wave solution for each pixel
    :param sigdet: float, the read noise (sigdet) for calculating the
                   noise array
    :param threshold: float, upper limit for pixel values, above this limit
                      pixels are regarded as saturated
    :param size: int, size (in pixels) around saturated pixels to also regard
                 as bad pixels

    :return dvrms2: numpy array (1D), the photon noise for each pixel (squared)
    :return weightedmean: float, weighted mean photon noise across all orders
    """
    # flag (saturated) fluxes above threshold as "bad pixels"
    with warnings.catch_warnings(record=True) as _:
        flag = spe < threshold
    # flag all fluxes around "bad pixels" (inside +/- size of the bad pixel)
    for i_it in range(1, 2 * size, 1):
        flag[:, size:-size] *= flag[:, i_it: i_it - 2 * size]
    # get the wavelength normalised to the wavelength spacing
    nwave = wave[:, 1:-1] / (wave[:, 2:] - wave[:, :-2])
    # get the flux + noise array
    sxn = (spe[:, 1:-1] + sigdet ** 2)
    # get the flux difference normalised to the flux + noise
    nspe = (spe[:, 2:] - spe[:, :-2]) / sxn
    # get the mask value
    maskv = flag[:, 2:] * flag[:, 1:-1] * flag[:, :-2]
    # get the total per order
    tot = mp.nansum(sxn * ((nwave * nspe) ** 2) * maskv, axis=1)
    # convert to dvrms2
    with warnings.catch_warnings(record=True) as _:
        dvrms2 = (speed_of_light_ms ** 2) / abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1. / np.sqrt(mp.nansum(1.0 / dvrms2))
    # per order value
    weightedmeanorder = np.sqrt(dvrms2)
    # return dv rms and weighted mean
    return dvrms2, weightedmean, weightedmeanorder


def remove_telluric_domain(params, infile, fiber, **kwargs):
    func_name = __NAME__ + '.remove_telluric_domain()'
    # get parameters from params/kwargs
    ccf_tellu_thres = pcheck(params, 'CCF_TELLU_THRES', 'ccf_tellu_thres',
                             kwargs, func_name)
    # get the image
    image = infile.get_data(copy=True)
    # get extraction type from the header
    ext_type = infile.get_hkey('KW_EXT_TYPE', dtype=str)
    # get the input file (assumed to be the first file from header
    e2dsfiles = infile.get_hkey_1d('KW_INFILE1', dim1=None,
                                   dtype=str)
    e2dsfilename = e2dsfiles[0]
    # construct absolute path for the e2ds file
    e2dsabsfilename = os.path.join(infile.path, e2dsfilename)
    # check that e2ds file exists
    if not os.path.exists(e2dsabsfilename):
        eargs = [infile.filename, ext_type, e2dsabsfilename]
        WLOG(params, 'error', textentry('09-020-00003', args=eargs))
    # get infile
    e2dsinst = drs_file.get_file_definition(params, ext_type, block_kind='red')
    # construct e2ds file
    e2dsfile = e2dsinst.newcopy(params=params, fiber=fiber)
    e2dsfile.set_filename(e2dsfilename)
    # get recon file
    reconinst = drs_file.get_file_definition(params, 'TELLU_RECON',
                                             block_kind='red')
    # construct recon file
    reconfile = reconinst.newcopy(params=params, fiber=fiber)
    reconfile.construct_filename(infile=e2dsfile)
    # check recon file exists
    if not os.path.exists(reconfile.filename):
        eargs = [infile.filename, reconfile.name, e2dsfile.filename]
        WLOG(params, 'error', textentry('09-020-00003', args=eargs))
    # read recon file
    reconfile.read_file()
    # find all places below threshold
    with warnings.catch_warnings(record=True) as _:
        keep = reconfile.get_data() > ccf_tellu_thres
    # set all bad data to NaNs
    image[~keep] = np.nan
    # return in file
    return image


def fill_e2ds_nans(params, image, **kwargs):
    func_name = __NAME__ + '.fill_e2ds_nans()'
    # get parameters from params/kwargs
    kernel_size = pcheck(params, 'CCF_FILL_NAN_KERN_SIZE', 'kernel_size',
                         kwargs, func_name)
    kernel_res = pcheck(params, 'CCF_FILL_NAN_KERN_RES', 'kernel_res',
                        kwargs, func_name)
    # check whether we have NaNs
    if np.sum(np.isnan(image)) == 0:
        return image
    # create a kernel to fill in the NaN gaps
    xker = np.arange(-kernel_size, kernel_size + kernel_res, kernel_res)
    kernel = np.exp(-0.5 * (xker ** 2))
    kernel /= np.sum(kernel)
    # log that NaNs were found
    WLOG(params, 'warning', textentry('10-020-00002'), sublevel=2)
    # copy original image
    image2 = np.array(image)
    # loop around orders
    for order_num in np.arange(image.shape[0]):
        # get the vector for this order
        oimage = np.array(image2[order_num])
        # find all the nan pixels in this order
        nanmask = np.isnan(oimage)
        # convert the nanmask to floats (for convolution)
        floatmask = (~nanmask).astype(float)
        # set the NaN values in image to zero
        oimage[nanmask] = 0.0
        # convolve the NaN mask with the kernel
        smooth_mask = np.convolve(floatmask, kernel, mode='same')
        smooth_data = np.convolve(oimage, kernel, mode='same')
        # calculate the smooth data (this is what is replaced)
        smooth = smooth_data / smooth_mask
        # set the NaN values to the smooth value
        image2[order_num][nanmask] = smooth[nanmask]

    # return the filled e2ds
    return image2


# =============================================================================
# Define CCF calculation functions
# =============================================================================
def compute_ccf_science(params, recipe, infile, image, blaze, wavemap, bprops,
                        fiber, **kwargs):
    func_name = __NAME__ + '.compute_ccf()'
    # get parameters from params/kwargs
    noise_sigdet = pcheck(params, 'CCF_NOISE_SIGDET', 'noise_sigdet', kwargs,
                          func_name)
    noise_size = pcheck(params, 'CCF_NOISE_BOXSIZE', 'noise_size', kwargs,
                        func_name)
    noise_thres = pcheck(params, 'CCF_NOISE_THRES', 'noise_thres', kwargs,
                         func_name)
    mask_width = pcheck(params, 'CCF_MASK_WIDTH', 'mask_width', kwargs,
                        func_name)
    mask_units = pcheck(params, 'CCF_MASK_UNITS', 'mask_units', kwargs,
                        func_name)
    fit_type = pcheck(params, 'CCF_FIT_TYPE', 'fit_type', kwargs, func_name)
    ccfnmax = pcheck(params, 'CCF_N_ORD_MAX', 'ccfnmax', kwargs,
                     func_name)
    null_targetrv = pcheck(params, 'OBJRV_NULL_VAL', 'null_targetrv',
                           kwargs, func_name)
    maxwsr = pcheck(params, 'CCF_MAX_CCF_WID_STEP_RATIO', 'maxwsr', kwargs,
                    func_name)
    # get image size
    nbo, nbpix = image.shape
    # set the number of fit parameters used
    fit_params = 6
    # get parameters from inputs
    ccfstep = params['INPUTS']['STEP']
    ccfwidth = params['INPUTS']['WIDTH']
    targetrv = params['INPUTS']['RV']
    # ----------------------------------------------------------------------
    # need to deal with no target rv step
    if np.isnan(targetrv):
        targetrv = infile.get_hkey('KW_DRS_RV', required=False, dtype=float)
        # set target rv to zero if we don't have a value
        if targetrv is None:
            wargs = [params['KW_DRS_RV'][0], infile.filename]
            WLOG(params, 'warning', textentry('09-020-00006', args=wargs),
                 sublevel=2)
            targetrv = 0.0
        elif np.abs(targetrv) > null_targetrv:
            wargs = [params['KW_DRS_RV'][0], null_targetrv, infile.filename]
            WLOG(params, 'warning', textentry('09-020-00007', args=wargs),
                 sublevel=2)
            targetrv = 0.0
    # ----------------------------------------------------------------------
    # need to deal with mask coming from inputs
    if isinstance(params['INPUTS']['MASK'], list):
        ccfmask = params['INPUTS']['MASK'][0][0]
    # else mask has come from constants
    else:
        ccfmask = params['INPUTS']['MASK']
    # get the berv
    berv = bprops['USE_BERV']
    # ----------------------------------------------------------------------
    # deal with ccf mask from TEFF
    if ccfmask == 'TEFF':
        # load ccf mask using infile header (i.e. from Teff consideration)
        ccfmask, ccf_fmt = get_ccf_teff_mask(params, infile.header)
    else:
        ccf_fmt = params['CCF_MASK_FMT']
    # ----------------------------------------------------------------------
    # need to get ccf normalization mode
    if 'MASKNORMMODE' in params['INPUTS']:
        ccfnormmode = params['INPUTS']['MASKNORMMODE']
    else:
        ccfnormmode = params['CCF_MASK_NORMALIZATION']
    # ----------------------------------------------------------------------
    # Need some sanity checking on width and step
    # ----------------------------------------------------------------------
    if ccfstep > (ccfwidth / maxwsr):
        eargs = [ccfwidth, ccfstep, maxwsr, func_name]
        WLOG(params, 'error', textentry('09-020-00005', args=eargs))

    # ----------------------------------------------------------------------
    # Check we are using correct fiber
    # ----------------------------------------------------------------------
    pconst = constants.pload()
    sfiber, rfiber = pconst.FIBER_KINDS()
    if fiber not in sfiber:
        # log that the science fiber was not correct
        eargs = [fiber, ' or '.join(sfiber), infile.name, infile.filename,
                 func_name]
        WLOG(params, 'error', textentry('09-020-00001', args=eargs))

    # ----------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ----------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dkwargs = dict(spe=image, wave=wavemap, sigdet=noise_sigdet,
                   size=noise_size, threshold=noise_thres)
    # run DeltaVrms2D
    dvrmsref, wmeanref, wmeanrefo = delta_v_rms_2d(**dkwargs)
    # log the estimated RV uncertainty
    wargs = [fiber, wmeanref]
    WLOG(params, 'info', textentry('40-020-00003', args=wargs))

    # ----------------------------------------------------------------------
    # Do the CCF calculations
    # ----------------------------------------------------------------------
    # get the mask parameters
    mkwargs = dict(filename=ccfmask, mask_width=mask_width,
                   mask_units=mask_units, fmt=ccf_fmt)
    ll_mask_d, ll_mask_ctr, w_mask = get_ccf_mask(params, **mkwargs)

    # calculate the CCF per order
    props = ccf_calculation_per_order(params, image, blaze, wavemap, berv,
                                      targetrv, ccfwidth, ccfstep, ll_mask_ctr,
                                      w_mask, fit_type, fiber, ccfnormmode)

    # calculate the CCF for the stack
    props = ccf_calculation_stack(params, props, fit_type, fit_params,
                                  wavemap)
    # ----------------------------------------------------------------------
    # Update the per order fits using prior knowledge from the stack
    # ----------------------------------------------------------------------
    props = update_per_order_ccfs(params, props, nbo, fit_type, fit_params,
                                  wavemap)
    # ----------------------------------------------------------------------
    # log the stats
    # ----------------------------------------------------------------------
    wargs = [props['CONTRAST_STACK'], props['RV_STACK'],
             props['CCF_PHOT_NOISE_STACK'], props['FWHM_STACK']]
    WLOG(params, 'info', textentry('40-020-00004', args=wargs))
    # ----------------------------------------------------------------------
    # add to output array
    props['TOT_SPEC_RMS'] = wmeanref
    props['ORD_SPEC_RMS'] = wmeanrefo
    # add constants to props
    props['CCF_MASK'] = ccfmask
    props['CCF_STEP'] = ccfstep
    props['CCF_WIDTH'] = ccfwidth
    props['TARGET_RV'] = targetrv
    props['CCF_SIGDET'] = noise_sigdet
    props['CCF_BOXSIZE'] = noise_size
    props['CCF_MAXFLUX'] = noise_thres
    props['CCF_NMAX'] = ccfnmax
    props['MASK_WIDTH'] = mask_width
    props['MASK_UNITS'] = mask_units
    # set source
    keys = ['TOT_SPEC_RMS', 'ORD_SPEC_RMS',
            'CCF_MASK', 'CCF_STEP', 'CCF_WIDTH', 'TARGET_RV', 'CCF_SIGDET',
            'CCF_BOXSIZE', 'CCF_MAXFLUX', 'CCF_NMAX', 'MASK_WIDTH',
            'MASK_UNITS']
    props.set_sources(keys, func_name)

    # ----------------------------------------------------------------------
    # Reference plots
    # ----------------------------------------------------------------------
    # the image vs wavelength for an order
    recipe.plot('CCF_SWAVE_REF', wavemap=wavemap, image=image, fiber=fiber,
                nbo=nbo)
    # the photon noise uncertainty plot
    recipe.plot('CCF_PHOTON_UNCERT', x=np.arange(nbo), y_sp=wmeanrefo,
                y_cc=props['CCF_PHOT_NOISE'] * 1000)
    # as a summary plot
    recipe.plot('SUM_CCF_PHOTON_UNCERT', x=np.arange(nbo), y_sp=wmeanrefo,
                y_cc=props['CCF_PHOT_NOISE'] * 1000)
    # ------------------------------------------------------------------
    # rv ccf plot
    # ------------------------------------------------------------------
    # loop around every order
    recipe.plot('CCF_RV_FIT_LOOP', params=params, x=props['RV_CCF'],
                y=props['CCF_NORM'],
                yfit=props['CCF_FIT'], kind='SCIENCE',
                rv=props['CCF_FIT_COEFFS'][:, 0], ccfmask=ccfmask,
                orders=np.arange(len(props['CCF'])), order=None)
    # the ccf stack
    recipe.plot('CCF_RV_FIT', params=params, x=props['RV_CCF'],
                y=props['CCF_STACK'], yfit=props['CCF_FIT_STACK'],
                kind='SCIENCE STACK', rv=props['RV_STACK'],
                ccfmask=ccfmask, orders=None, order=None)
    # the mean ccf for summary
    recipe.plot('SUM_CCF_RV_FIT', params=params, x=props['RV_CCF'],
                y=props['CCF_STACK'], yfit=props['CCF_FIT_STACK'],
                kind='SCIENCE STACK', rv=props['RV_STACK'],
                ccfmask=ccfmask, orders=None, order=None)
    # ------------------------------------------------------------------
    # return property dictionary
    return props


def compute_ccf_fp(params, recipe, infile, image, blaze, wavemap, fiber,
                   **kwargs):
    func_name = __NAME__ + '.compute_ccf_fp()'
    # get constants from params/kwargs
    noise_sigdet = pcheck(params, 'WAVE_CCF_NOISE_SIGDET', 'sigdet', kwargs,
                          func_name)
    noise_size = pcheck(params, 'WAVE_CCF_NOISE_BOXSIZE', 'boxsize', kwargs,
                        func_name)
    noise_thres = pcheck(params, 'WAVE_CCF_NOISE_THRES', 'maxflux', kwargs,
                         func_name)
    ccfstep = pcheck(params, 'WAVE_CCF_STEP', 'ccfstep', kwargs, func_name)
    ccfwidth = pcheck(params, 'WAVE_CCF_WIDTH', 'ccfwidth', kwargs, func_name)
    targetrv = pcheck(params, 'WAVE_CCF_TARGET_RV', 'targetrv', kwargs,
                      func_name)
    ccfmask = pcheck(params, 'WAVE_CCF_MASK', 'ccfmask', kwargs, func_name)
    ccfnmax = pcheck(params, 'WAVE_CCF_N_ORD_MAX', 'ccfnmax', kwargs,
                     func_name)
    mask_width = pcheck(params, 'WAVE_CCF_MASK_WIDTH', 'mask_width', kwargs,
                        func_name)
    mask_units = pcheck(params, 'WAVE_CCF_MASK_UNITS', 'mask_units', kwargs,
                        func_name)
    ccfnormmode = params['CCF_MASK_NORMALIZATION']
    # get image size
    nbo, nbpix = image.shape
    # we do not use infile
    _ = infile
    # set the berv to zero (fp have no berv)
    berv = 0
    # the fit type must be set to 1 (for emission lines)
    fit_type = 1
    # set the number of fit parameters
    if fit_type == 0:
        fit_params = 6
    else:
        fit_params = 5
    # ------------------------------------------------------------------
    # Compute photon noise uncertainty for FP
    # ------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dkwargs = dict(spe=image, wave=wavemap, sigdet=noise_sigdet,
                   size=noise_size, threshold=noise_thres)
    # run DeltaVrms2D
    dvrmsref, wmeanref, wmeanrefo = delta_v_rms_2d(**dkwargs)

    # log the estimated RV uncertainty
    wargs = [fiber, wmeanref]
    WLOG(params, 'info', textentry('40-017-00028', args=wargs))
    # ----------------------------------------------------------------------
    # Do the CCF calculations
    # ----------------------------------------------------------------------
    # get the mask parameters
    mkwargs = dict(filename=ccfmask, mask_width=mask_width,
                   mask_units=mask_units)
    ll_mask_d, ll_mask_ctr, w_mask = get_ccf_mask(params, **mkwargs)

    # calculate the CCF per order
    props = ccf_calculation_per_order(params, image, blaze, wavemap, berv,
                                      targetrv, ccfwidth, ccfstep, ll_mask_ctr,
                                      w_mask, fit_type, fiber, ccfnormmode)

    # calculate the CCF for the stack
    props = ccf_calculation_stack(params, props, fit_type, fit_params,
                                  wavemap)
    # ----------------------------------------------------------------------
    # Update the per order fits using prior knowledge from the stack
    # ----------------------------------------------------------------------
    props = update_per_order_ccfs(params, props, nbo, fit_type, fit_params,
                                  wavemap)
    # ----------------------------------------------------------------------
    # log the stats
    # ----------------------------------------------------------------------
    wargs = [props['CONTRAST_STACK'], props['RV_STACK'],
             props['CCF_PHOT_NOISE_STACK'], props['FWHM_STACK']]
    WLOG(params, 'info', textentry('40-020-00004', args=wargs))
    # ----------------------------------------------------------------------
    # add to output array
    props['TOT_SPEC_RMS'] = wmeanref
    props['ORD_SPEC_RMS'] = wmeanrefo
    props['CCF_MASK'] = ccfmask
    props['CCF_STEP'] = ccfstep
    props['CCF_WIDTH'] = ccfwidth
    props['TARGET_RV'] = targetrv
    props['CCF_SIGDET'] = noise_sigdet
    props['CCF_BOXSIZE'] = noise_size
    props['CCF_MAXFLUX'] = noise_thres
    props['CCF_NMAX'] = ccfnmax
    props['MASK_WIDTH'] = mask_width
    props['MASK_UNITS'] = mask_units
    # set source
    keys = ['TOT_SPEC_RMS', 'ORD_SPEC_RMS',
            'CCF_MASK', 'CCF_STEP', 'CCF_WIDTH', 'TARGET_RV', 'CCF_SIGDET',
            'CCF_BOXSIZE', 'CCF_MAXFLUX', 'CCF_NMAX', 'MASK_WIDTH',
            'MASK_UNITS']
    props.set_sources(keys, func_name)

    # ----------------------------------------------------------------------
    # Reference plots
    # ----------------------------------------------------------------------
    # the image vs wavelength for an order
    recipe.plot('CCF_SWAVE_REF', wavemap=wavemap, image=image, fiber=fiber,
                nbo=nbo)
    # the photon noise uncertainty plot
    recipe.plot('CCF_PHOTON_UNCERT', x=np.arange(nbo), y_sp=wmeanrefo,
                y_cc=props['CCF_PHOT_NOISE'] * 1000)
    # as a summary plot
    recipe.plot('SUM_CCF_PHOTON_UNCERT', x=np.arange(nbo), y_sp=wmeanrefo,
                y_cc=props['CCF_PHOT_NOISE'] * 1000)
    # ------------------------------------------------------------------
    # rv ccf plot
    # ------------------------------------------------------------------
    # loop around every order
    recipe.plot('CCF_RV_FIT_LOOP', params=params, x=props['RV_CCF'],
                y=props['CCF_NORM'],
                yfit=props['CCF_FIT'], kind='FP',
                rv=props['CCF_FIT_COEFFS'][:, 1], ccfmask=ccfmask,
                orders=np.arange(len(props['CCF'])), order=None)
    # the ccf stack
    recipe.plot('CCF_RV_FIT', params=params, x=props['RV_CCF'],
                y=props['CCF_STACK'], yfit=props['CCF_FIT_STACK'],
                kind='FP STACK', rv=props['RV_STACK'],
                ccfmask=ccfmask, orders=None, order=None)
    # the mean ccf for summary
    recipe.plot('SUM_CCF_RV_FIT', params=params, x=props['RV_CCF'],
                y=props['CCF_STACK'], yfit=props['CCF_FIT_STACK'],
                kind='FP STACK', rv=props['RV_STACK'],
                ccfmask=ccfmask, orders=None, order=None)

    # return the rv props
    return props


def ccf_calculation_per_order(params, image, blaze, wavemap, berv, targetrv,
                              ccfwidth, ccfstep, mask_centers, mask_weights,
                              fit_type, fiber, ccfnormmode, **kwargs):
    # set function name
    func_name = display_func('ccf_calculation_per_order', __NAME__)
    # get properties from params
    blaze_norm_percentile = pcheck(params, 'CCF_BLAZE_NORM_PERCENTILE',
                                   'blaze_norm_percentile', kwargs, func_name)
    blaze_threshold = pcheck(params, 'WAVE_FP_BLAZE_THRES', 'blaze_threshold',
                             kwargs, func_name)
    # get rvmin and rvmax in km/s
    rvmin = targetrv - ccfwidth
    rvmin = pcheck(params, 'RVMIN', 'rvmin', kwargs, func_name, default=rvmin)
    rvmax = targetrv + ccfwidth + ccfstep
    rvmax = pcheck(params, 'RVMAX', 'rvmax', kwargs, func_name, default=rvmax)
    # get the dimensions
    nbo, nbpix = image.shape
    # create a rv ccf range in km/s
    rv_ccf = np.arange(rvmin, rvmax, ccfstep)
    # set the number of fit parameters
    if fit_type == 0:
        fit_params = 6
    else:
        fit_params = 5
    # store outputs in param dict
    props = ParamDict()
    props['RV_CCF'] = rv_ccf
    props['CCF'] = np.full((nbo, len(rv_ccf)), np.nan)
    props['CCF_NORM'] = np.full((nbo, len(rv_ccf)), np.nan)
    props['CCF_LINES'] = np.repeat(np.nan, nbo)
    props['TOT_LINE'] = np.repeat(0, nbo)
    props['CCF_PHOT_NOISE'] = np.repeat(np.nan, nbo)
    props['CCF_PIX_NOISE'] = np.full((nbo, len(rv_ccf)), np.nan)
    props['CCF_SNR'] = np.repeat(np.nan, nbo)
    props['CCF_FIT'] = np.full((nbo, len(rv_ccf)), np.nan)
    props['CCF_FIT_COEFFS'] = np.full((nbo, fit_params), np.nan)
    props['CCF_NORM_FACTOR'] = np.repeat(np.nan, nbo)

    # set sources
    keys = list(props.keys())
    props.set_sources(keys, func_name)

    # ----------------------------------------------------------------------
    # switch normalization across all weights
    if ccfnormmode.upper() == 'ALL':
        mask_weights = mask_weights / mp.nanmean(np.abs(mask_weights))
    # ----------------------------------------------------------------------
    # calculate proper wave shift
    dvshift = mp.relativistic_waveshift(berv, units='km/s')
    # get all rv_ccf wave shifts (so we don't compute them every time)
    wave_shifts = mp.relativistic_waveshift(rv_ccf, units='km/s')
    # apply to wave solution
    wavemap2 = wavemap * dvshift
    # ----------------------------------------------------------------------
    # loop around the orders
    for order_num in range(nbo):
        # log the process
        WLOG(params, '', textentry('40-020-00005', args=[fiber, order_num]))
        # ------------------------------------------------------------------
        # get this orders values
        wa_ord = np.array(wavemap2[order_num])
        sp_ord = np.array(image[order_num])
        bl_ord = np.array(blaze[order_num])

        # normalize per-ord blaze to its peak value
        # this gets rid of the calibration lamp SED
        bl_ord /= mp.nanpercentile(bl_ord, blaze_norm_percentile)
        # change NaNs in blaze to zeros
        bl_ord[~np.isfinite(bl_ord)] = 0.0
        # mask on the blaze
        with warnings.catch_warnings(record=True) as _:
            blazemask = bl_ord > blaze_threshold
        # get order mask centers and mask weights
        min_ord_wav = mp.nanmin(wa_ord[blazemask])
        max_ord_wav = mp.nanmax(wa_ord[blazemask])
        # mask the ccf mask by the order length
        mask_wave_mask = (mask_centers > min_ord_wav)
        mask_wave_mask &= (mask_centers < max_ord_wav)
        omask_centers = mask_centers[mask_wave_mask]
        omask_weights = mask_weights[mask_wave_mask]
        # ------------------------------------------------------------------
        # find any places in spectrum where spectrum is valid
        valid = np.isfinite(sp_ord) & np.isfinite(bl_ord)
        # ------------------------------------------------------------------
        # deal with no valid lines
        if np.sum(mask_wave_mask) == 0:
            # log all NaN
            wargs = [order_num, min_ord_wav, max_ord_wav]
            WLOG(params, 'warning', textentry('10-020-00006', args=wargs),
                 sublevel=4)
            continue
        # ------------------------------------------------------------------
        # deal with all nan
        if np.sum(~valid) == nbpix:
            # log all NaN
            wargs = [order_num]
            WLOG(params, 'warning', textentry('10-020-00004', args=wargs),
                 sublevel=4)
            continue
        # ------------------------------------------------------------------
        # the weight of the order is the valid criteria
        weight_ord = np.array(valid, dtype=float)
        # ------------------------------------------------------------------
        # spline the spectrum and the blaze
        spline_sp = mp.iuv_spline(wa_ord[valid], sp_ord[valid], k=2, ext=1)
        spline_bl = mp.iuv_spline(wa_ord[valid], bl_ord[valid], k=2, ext=1)
        # spline to monitor if line falls on a NaN
        spl_valid = mp.iuv_spline(wa_ord, weight_ord, k=1, ext=1)
        # make sure the doppler shifted line is also valid
        valid2 = np.full((len(rv_ccf), len(omask_centers)), np.nan)
        for rv_element in range(len(rv_ccf)):
            valid2[rv_element] = spl_valid(omask_centers * wave_shifts[rv_element])
        # lines must be 99% valid
        keep = np.nanmin(valid2, axis=0) > 0.99
        # ------------------------------------------------------------------
        # propagating the extreme wave shifts to see if any lines fall off
        #  the domain that is considered valid for the spline
        # find the wave grid for the first shift
        wave_tmp_start = omask_centers * wave_shifts[0]
        # find the wave grid for the last shift
        wave_tmp_end = omask_centers * wave_shifts[-1]
        # find the valid lines within these limits
        # (ext=1 puts 0 when point is beyond domain)
        valid_lines_start = spline_bl(wave_tmp_start) != 0
        valid_lines_end = spline_bl(wave_tmp_end) != 0
        # combine the valid masks for start and end
        keep &= (valid_lines_start & valid_lines_end)
        # ------------------------------------------------------------------
        # deal with no valid lines
        if np.sum(keep) == 0:
            # log all NaN
            wargs = [order_num]
            WLOG(params, 'warning', textentry('10-020-00007', args=wargs),
                 sublevel=4)
            continue
        # ------------------------------------------------------------------
        # apply masks to centers and weights
        omask_centers = omask_centers[keep]
        omask_weights = omask_weights[keep]
        # normalise omask weights by order (if required)
        if ccfnormmode.upper() == 'ORDER':
            omask_weights = omask_weights / mp.nanmean(omask_weights)
        # ------------------------------------------------------------------
        # set up the ccf for this order
        ccf_ord = np.zeros_like(rv_ccf)
        sig_ord = np.zeros_like(rv_ccf)
        # ------------------------------------------------------------------
        # set number of valid lines used to zero
        numlines = 0
        # loop around the rvs and calculate the CCF at this point
        for rv_element in range(len(rv_ccf)):
            centers_tmp = omask_centers * wave_shifts[rv_element]
            numlines = np.sum(spline_bl(centers_tmp) != 0)
            # CCF is the division of the sums
            with warnings.catch_warnings(record=True) as _:
                # the ccf is the sum of the spline of the spectrum
                ccf_element = spline_sp(centers_tmp)
                ccf_ord[rv_element] = mp.nansum(ccf_element * omask_weights)

                sig_ccf_element = ccf_element * omask_weights ** 2
                sig_ord[rv_element] = np.sqrt(mp.nansum(sig_ccf_element))
        # ------------------------------------------------------------------
        # deal with NaNs in ccf
        if np.sum(np.isnan(ccf_ord)) > 0:
            # log all NaN
            wargs = [order_num]
            WLOG(params, 'warning', textentry('10-020-00005', args=wargs),
                 sublevel=4)
            continue
        # ------------------------------------------------------------------
        # norm the ccf
        ccf_norm = mp.nanmedian(ccf_ord)
        ccf_ord_norm = ccf_ord / ccf_norm
        # fit the CCF with a gaussian with a slope
        fargs = [order_num, rv_ccf, ccf_ord_norm, sig_ord, fit_type, fit_params]
        ccf_coeffs_ord, ccf_fit_ord = fit_ccf_ea(params, *fargs)

        # ------------------------------------------------------------------
        # Estimate the noise
        # ------------------------------------------------------------------
        pn_args = [wa_ord, rv_ccf, ccf_fit_ord, ccf_coeffs_ord, sig_ord,
                   fit_type]
        ccf_phot_noise, ccf_snr = estimate_photon_noise(*pn_args)
        # ------------------------------------------------------------------
        # append ccf to storage
        props['CCF'][order_num] = ccf_ord
        props['CCF_NORM'][order_num] = ccf_ord_norm
        props['CCF_LINES'][order_num] = numlines
        props['TOT_LINE'][order_num] += numlines
        props['CCF_PHOT_NOISE'][order_num] = ccf_phot_noise
        props['CCF_PIX_NOISE'][order_num] = sig_ord
        props['CCF_SNR'][order_num] = ccf_snr
        props['CCF_FIT'][order_num] = ccf_fit_ord
        props['CCF_FIT_COEFFS'][order_num] = ccf_coeffs_ord
        props['CCF_NORM_FACTOR'][order_num] = ccf_norm

    # return props
    return props


def ccf_calculation_stack(params: ParamDict, props: ParamDict, fit_type: int,
                          fit_params: int, wavemap: np.ndarray):
    # set function name
    func_name = display_func('ccf_calculation_stack', __NAME__)
    # ----------------------------------------------------------------------
    # Calculate the mean CCF
    # ----------------------------------------------------------------------
    # get the average ccf (after fwhm sigma clip)
    ccf_stack = mp.nansum(props['CCF'], axis=0)

    ccf_stack_pix_noise = np.sqrt(mp.nansum(props['CCF_PIX_NOISE'] ** 2, axis=0))

    ccf_norm = mp.nanmedian(ccf_stack)
    ccf_stack_norm = ccf_stack / ccf_norm
    ccf_stack_pix_noise_norm = ccf_stack_pix_noise / ccf_norm

    # ------------------------------------------------------------------
    # Fit the CCF
    # ------------------------------------------------------------------
    # get the fit for the normalized average ccf
    ccf_coeffs_stack, ccf_fit_stack = fit_ccf_ea(params, 'stack',
                                                 props['RV_CCF'],
                                                 ccf_stack_norm,
                                                 ccf_stack_pix_noise_norm,
                                                 fit_type=fit_type,
                                                 fit_params=fit_params)
    # ------------------------------------------------------------------
    # Estimate the noise
    # ------------------------------------------------------------------
    pn_args = [wavemap, props['RV_CCF'], ccf_fit_stack,
               ccf_coeffs_stack, ccf_stack_pix_noise_norm, fit_type]
    ccf_stack_phot_noise, ccf_stack_snr = estimate_photon_noise(*pn_args)
    # ------------------------------------------------------------------
    if fit_type == 0:
        # get the RV value from the normalised average ccf fit center location
        ccf_rv = float(ccf_coeffs_stack[0])
        # get the FWHM value
        ccf_fwhm = ccf_coeffs_stack[1] * mp.fwhm()
        # get the contrast (ccf fit amplitude)
        ccf_contrast = float(ccf_coeffs_stack[2])
    else:
        # get the RV value from the normalised average ccf fit center location
        ccf_rv = float(ccf_coeffs_stack[1])
        # get the FWHM value
        ccf_fwhm = ccf_coeffs_stack[2] * mp.fwhm()
        # get the contrast (ccf fit amplitude)
        ccf_contrast = np.nan
    # ----------------------------------------------------------------------
    # Work out the bisector span
    bisspan = bisector(params, props['RV_CCF'], ccf_stack_norm,
                       ccf_coeffs_stack, fit_type)
    # add to output array
    props['CCF_STACK'] = ccf_stack_norm
    props['RV_STACK'] = ccf_rv
    props['CONTRAST_STACK'] = ccf_contrast
    props['FWHM_STACK'] = ccf_fwhm
    props['BISSPAN_STACK'] = bisspan
    props['CCF_SNR_STACK'] = ccf_stack_snr
    props['CCF_NORM_FACTOR_STACK'] = ccf_norm
    props['CCF_COEFFS_STACK'] = ccf_coeffs_stack
    props['CCF_FIT_STACK'] = ccf_fit_stack
    props['CCF_PIX_NOISE_STACK'] = ccf_stack_pix_noise_norm
    props['CCF_PHOT_NOISE_STACK'] = ccf_stack_phot_noise
    # set the source
    keys = ['CCF_STACK', 'RV_STACK', 'CONTRAST_STACK', 'FWHM_STACK',
            'BISSPAN_STACK', 'CCF_SNR_STACK', 'CCF_NORM_FACTOR_STACK',
            'CCF_COEFFS_STACK', 'CCF_FIT_STACK',
            'CCF_PIX_NOISE_STACK', 'CCF_PHOT_NOISE_STACK']
    props.set_sources(keys, func_name)

    return props


def update_per_order_ccfs(params: ParamDict, props: ParamDict, nbo: int,
                          fit_type: int, fit_params: int, wavemap: np.ndarray):
    # set function name
    func_name = display_func('update_per_order_ccfs', __NAME__)
    # storage for outputs
    ccf_all_fit = []
    ccf_all_results = []
    ccf_all_snr = []
    ccf_phot_noise_all = []
    # get parameters from props
    rv_ccf = props['RV_CCF']
    ccf_coeffs_stack = props['CCF_COEFFS_STACK']
    # loop around orders
    for order_num in range(nbo):

        # get this orders values
        ccf_ord_norm = props['CCF_NORM'][order_num]
        sig_ord = props['CCF_PIX_NOISE'][order_num]
        norm = props['CCF_NORM_FACTOR'][order_num]
        wa_ord = wavemap[order_num]
        # deal with nan orders - don't re-fit
        if np.sum(np.isfinite(ccf_ord_norm)) == 0:
            # append to storage
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, fit_params))
            ccf_all_snr.append(np.nan)
            ccf_phot_noise_all.append(np.nan)
            continue
        # guess_dict
        guess_dict = dict()
        guess_dict['guess_cent'] = ccf_coeffs_stack[0]
        guess_dict['guess_ew'] = ccf_coeffs_stack[1] / mp.fwhm()
        guess_dict['guess_depth'] = ccf_coeffs_stack[2]
        # fit the CCF with a gaussian with a slope
        fargs = [order_num, rv_ccf, ccf_ord_norm, sig_ord, fit_type,
                 fit_params, guess_dict]
        ccf_coeffs_ord, ccf_fit_ord = fit_ccf_ea(params, *fargs)
        # ------------------------------------------------------------------
        # Estimate the noise
        # ------------------------------------------------------------------
        pn_args = [wa_ord, rv_ccf, ccf_fit_ord, ccf_coeffs_ord, sig_ord,
                   fit_type, norm]
        ccf_phot_noise, ccf_snr = estimate_photon_noise(*pn_args)
        # append to storage
        ccf_all_fit.append(ccf_fit_ord)
        ccf_all_results.append(ccf_coeffs_ord)
        ccf_all_snr.append(ccf_snr)
        ccf_phot_noise_all.append(ccf_phot_noise)
    # update props
    props['CCF_SNR'] = np.array(ccf_all_snr)
    props['CCF_FIT'] = np.array(ccf_all_fit)
    props['CCF_FIT_COEFFS'] = np.array(ccf_all_results)
    props['CCF_PHOT_NOISE'] = np.array(ccf_phot_noise_all)
    # set sources
    keys = ['CCF_SNR', 'CCF_FIT', 'CCF_FIT_COEFFS', 'CCF_PHOT_NOISE']
    props.set_sources(keys, func_name)
    # return props
    return props


def fit_ccf_ea(params, order_num, rv, ccf, sig, fit_type, fit_params,
               guess_dict=None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit the CCF to a guassian function with a slope.
    Allow priors on some of the guess functions

    :param params:
    :param order_num:
    :param rv:
    :param ccf:
    :param sig:
    :param fit_type:
    :param fit_params:
    :param guess_dict:
    :return:
    """
    func_name = __NAME__ + '.fit_ccf()'
    # resolution element in m/s
    image_pixel_size = params['IMAGE_PIXEL_SIZE']

    # if there is no guess dictionary set it to an empty dictionary
    if guess_dict is None:
        guess_dict = dict()

    # deal with inconsistent lengths
    if len(rv) != len(ccf):
        eargs = [len(rv), len(ccf), func_name]
        WLOG(params, 'error', textentry('00-020-00001', args=eargs))
    # deal with all nans
    if np.sum(np.isnan(ccf)) == len(ccf):
        # log warning about all NaN ccf
        wargs = [order_num]
        WLOG(params, 'warning', textentry('10-020-00001', args=wargs))
        # return NaNs
        result = np.zeros(fit_params) * np.nan
        ccf_fit = np.zeros_like(ccf) * np.nan
        return result, ccf_fit

    # get constants
    max_ccf, min_ccf = mp.nanmax(ccf), mp.nanmin(ccf)
    min_rv, max_rv = mp.nanmin(rv), mp.nanmax(rv)
    argmin, argmax = mp.nanargmin(ccf), mp.nanargmax(ccf)

    # set up guess for gaussian fit
    # if fit_type == 0 then we have absorption lines
    if fit_type == 0:
        # set up guess for gaussian fit
        guess_cent = guess_dict.get('guess_cent', rv[argmin])
        # twice the image pixel size in km/s
        guess_w = guess_dict.get('guess_ew', 2 * image_pixel_size)
        # for absorption this should be 1 - the min ccf
        guess_depth = guess_dict.get('guess_depth', 1 - min_ccf)
        # fit the continnum to guess the slope and curvature
        continuum_fit, _ = mp.robust_polyfit(rv, ccf, 2, nsigcut=3)
        # guess slope
        guess_slope = continuum_fit[0]
        # guess curvature
        guess_curv = continuum_fit[1]
        # guess amp
        guess_amp = 1
        # set bounds for the curve fit
        bounds_lower = [min_rv, 0, 0, -np.inf, -np.inf, 0]
        bounds_upper = [max_rv, (max_rv - min_rv) / 2, 1, np.inf, np.inf, 2]

        # push guess values into list
        guess = [guess_cent, guess_w, guess_depth, guess_slope, guess_curv,
                 guess_amp]
        # get gaussian fit
        nanmask = np.isfinite(ccf)
        ccf[~nanmask] = 0.0
        # fit the gaussian
        try:
            with warnings.catch_warnings(record=True) as _:
                # noinspection PyTupleAssignmentBalance
                result, _ = curve_fit(mp.gaussian_slope, rv, ccf,
                                      bounds=[bounds_lower, bounds_upper],
                                      p0=guess, sigma=sig)
                fit = mp.gaussian_slope(rv, *result)
        except RuntimeError:
            result = np.repeat(np.nan, fit_params)
            fit = np.repeat(np.nan, len(rv))

    # else (fit_type == 1) then we have emission lines
    else:
        # set the amplitude
        guess_amp = 1
        # set up guess for gaussian fit
        guess_cent = rv[argmax]
        # set up sigma
        guess_sigma = image_pixel_size
        # set up zp
        guess_zp = min_ccf
        # set up slope
        guess_slope = 0
        # set bounds for the curve fit
        bounds_lower = [0, min_rv, 0, 0, -np.inf]
        bounds_upper = [2 * max_ccf, max_rv, (max_rv - min_rv) / 2, max_ccf, np.inf]
        # push guess values into list
        #      a, x0, sigma, zp, slope
        guess = [guess_amp, guess_cent, guess_sigma, guess_zp, guess_slope]
        # get gaussian fit
        nanmask = np.isfinite(ccf)
        ccf[~nanmask] = 0.0
        # fit the gaussian
        try:
            with warnings.catch_warnings(record=True) as _:
                # noinspection PyTupleAssignmentBalance
                result, _ = curve_fit(mp.gauss_fit_s, rv, ccf,
                                      bounds=[bounds_lower, bounds_upper],
                                      p0=guess, sigma=sig)
                fit = mp.gauss_fit_s(rv, *result)
        except RuntimeError:
            result = np.repeat(np.nan, fit_params)
            fit = np.repeat(np.nan, len(rv))

    # scale the ccf
    # ccf_fit = (fit + 1 - fit_type) * max_ccf
    # return the best guess and the gaussian fit
    return result, fit


def estimate_photon_noise(wavemap: np.ndarray, rv_ccf: np.ndarray,
                          ccf_fit_ord: np.ndarray, ccf_coeffs_ord: np.ndarray,
                          sig_ord: np.ndarray, fit_type: int,
                          norm=1) -> Tuple[float, float]:
    """
    Estimate the photon noise using the gradients of wave, dv and ccf

    :param wavemap: np.ndarray, the wavelength map for this order
    :param rv_ccf: np.ndarray, the rv vector
    :param ccf_fit_ord: np.ndarray, the fitted gaussian slope vector
    :param ccf_coeffs_ord: np.ndarray, the gaussian slope coefficients
    :param sig_ord: np.ndarray, the ccf pixel noise vector
    :param fit_type: int, the type of fit (0=absorption, 1=emission)
    :param norm: scale factor for the fit compared to the ccf

    :return: tuple, 1. the CCF photon noise, 2. The CCF SNR
    """
    # some gradients
    gradwave = np.nanmedian(wavemap / np.gradient(wavemap))
    grad_dv = np.gradient(rv_ccf)
    med_grad_dv = mp.nanmedian(grad_dv)
    # estimate oversampling factor
    oversampling_ratio_ord = (speed_of_light / gradwave) / med_grad_dv
    # error on the RV from the photon noise
    ccf_grad = np.gradient(ccf_fit_ord * norm) / grad_dv
    # bouchy 2001 formula
    sum_ratio2 = np.sqrt(np.sum((ccf_grad / sig_ord) ** 2))
    ccf_phot_noise = (1 / sum_ratio2) * np.sqrt(oversampling_ratio_ord)
    # get the ccf snr (1/mean snr)*depth
    if fit_type == 0:
        ccf_snr = ccf_coeffs_ord[1] * mp.fwhm() / ccf_phot_noise
    else:
        ccf_snr = ccf_coeffs_ord[2] * mp.fwhm() / ccf_phot_noise
    # return the photon noise and SNR
    return ccf_phot_noise, ccf_snr


def bisector(params: ParamDict, rv: np.ndarray, ccf: np.ndarray,
             ccf_coeffs: np.ndarray, fit_type: int) -> float:
    """
    Calculate the bisector span of the CCF

    :param params: ParamDict, parameter dictionary of constants
    :param rv: np.ndarray, the radial velocities for the ccf
    :param ccf: np.ndarray, the CCF values
    :param ccf_coeffs: np.ndarray, the gaussian fit coefficients for the CCF
    :param fit_type: int, the type of fit (0=absorption, 1=emission)

    :return: float, the bisector span
    """
    # get min and max depth for the bisector
    bs_cut_top = params['CCF_BIS_CUT_TOP'] / 100.0
    bs_cut_bottom = params['CCF_BIS_CUT_BOTTOM'] / 100.0
    # take the gaussian fit without a depth
    ccf_coeffs2 = np.array(ccf_coeffs)
    # set the depth to 0 (i.e. no depth)
    ccf_coeffs2[2] = 0
    # normalize CCF without the gaussian. Sets the continuum flat to 1
    if fit_type == 0:
        ccf2 = (1 - ccf / mp.gaussian_slope(rv, *ccf_coeffs2)) / ccf_coeffs[2]
    else:
        ccf2 = (ccf - mp.gauss_fit_s(rv, *ccf_coeffs2)) / ccf_coeffs[0]
    # ----------------------------------------------------------------------
    # Bisector at cut1
    span_top = bisector_cut(rv, ccf2, bs_cut_top)
    # Bisector at cut2
    span_bottom = bisector_cut(rv, ccf2, bs_cut_bottom)
    # difference between the two bisector cuts
    return span_top - span_bottom


def bisector_cut(xx: np.ndarray, yy: np.ndarray, cut: float) -> float:
    """
    Calculate the bisector span of the CCF at a given cut

    :param xx: np.ndarray, the x values (radial velocities)
    :param yy: np.ndarray, the y values (CCF values)
    :param cut: float, the cut value to calculate the bisector span at

    :return: float, the bisector span at this cut value
    """
    # find the two points where the CCF is above cut and interpolate with a
    #    linear fit
    lims1 = np.where(yy > cut)[0][[0, -1]]
    # find the value at the left side
    x1_start = max([lims1[0] - 2, 0])
    x1_end = min([lims1[0] + 1, len(yy)])
    v1_fit = np.polyfit(yy[x1_start:x1_end], xx[x1_start:x1_end], 1)
    v1_val = np.polyval(v1_fit, cut)
    # find the value at the right side
    x2_start = lims1[1]
    x2_end = min([lims1[1] + 2, len(yy)])
    v2_fit = np.polyfit(yy[x2_start:x2_end], xx[x2_start:x2_end], 1)
    v2_val = np.polyval(v2_fit, cut)
    # return the bisector span for this cut
    return (v1_val + v2_val) / 2


# =============================================================================
# Define writing functions
# =============================================================================
def write_ccf(params: ParamDict, recipe, infile: DrsFitsFile,
              props: ParamDict, rawfiles, combine: bool, qc_params,
              fiber: str, fit_type: int):
    # ----------------------------------------------------------------------
    # produce CCF table
    table1 = Table()
    table1['RV'] = props['RV_CCF']
    for order_num in range(len(props['CCF'])):
        table1['CCF{0:02d}'.format(order_num)] = props['CCF'][order_num]
        table1['ECCF{0:02d}'.format(order_num)] = props['CCF_PIX_NOISE'][order_num]
        table1['FIT{0:02d}'.format(order_num)] = props['CCF_FIT'][order_num]
    table1['CCF_STACK'] = props['CCF_STACK']
    table1['ECCF_STACK'] = props['CCF_PIX_NOISE_STACK']
    table1['FIT_STACK'] = props['CCF_FIT_STACK']
    # add table descriptions
    table1['RV'].description = 'Radial velocity (km/s)'
    for order_num in range(len(props['CCF'])):
        table1['CCF{0:02d}'.format(order_num)].description = 'CCF for order {0}'.format(order_num)
        table1['ECCF{0:02d}'.format(order_num)].description = 'CCF pixel noise for order {0}'.format(order_num)
        table1['FIT{0:02d}'.format(order_num)].description = 'CCF fit for order {0}'.format(order_num)
    table1['CCF_STACK'].description = 'CCF stack'
    table1['ECCF_STACK'].description = 'CCF stack pixel noise'
    table1['FIT_STACK'].description = 'CCF stack fit'
    # ----------------------------------------------------------------------
    # produce stats table
    table2 = Table()
    table2['Orders'] = np.arange(len(props['CCF'])).astype(int)
    table2['NLines'] = props['CCF_LINES']
    # get the coefficients
    coeffs = props['CCF_FIT_COEFFS']
    if fit_type == 0:
        table2['RV'] = coeffs[:, 0]
        table2['EW'] = coeffs[:, 1]
        table2['DEPTH'] = coeffs[:, 2]
        table2['SLOPE'] = coeffs[:, 3]
        table2['CURV'] = coeffs[:, 4]
        table2['AMP'] = coeffs[:, 5]
        table2['FWHM'] = coeffs[:, 1] * mp.fwhm()
        table2['Contrast'] = np.abs(100 * coeffs[:, 2])
    else:
        table2['RV'] = coeffs[:, 1]
        table2['SIG'] = coeffs[:, 2]
        table2['ZP'] = coeffs[:, 3]
        table2['SLOPE'] = coeffs[:, 4]
        table2['AMP'] = coeffs[:, 0]
        table2['FWHM'] = coeffs[:, 2] * mp.fwhm()
        table2['Contrast'] = np.repeat(np.nan, len(coeffs))

    table2['SNR'] = props['CCF_SNR']
    table2['Norm'] = props['CCF_NORM_FACTOR']
    table2['DVRMS_SP'] = props['ORD_SPEC_RMS']
    table2['DVRMS_CC'] = 1000 * props['CCF_PHOT_NOISE']
    # add table descriptions
    table2['Orders'].description = 'Order number'
    table2['NLines'].description = 'Number of lines used in CCF'

    if fit_type == 0:
        table2['RV'].description = 'Radial velocity (km/s) from fit'
        table2['EW'].description = 'Equivalent width (km/s) from fit'
        table2['DEPTH'].description = 'Depth of the CCF from fit'
        table2['SLOPE'].description = 'Slope of the CCF from fit'
        table2['CURV'].description = 'Curvature of the CCF from fit'
        table2['AMP'].description = 'Amplitude of the CCF from fit'
        table2['FWHM'].description = 'Full width half maximum of the CCF from fit'
        table2['Contrast'].description = 'Contrast of the CCF from fit'
    else:
        table2['RV'].description = 'Radial velocity (km/s) from fit'
        table2['SIG'].description = 'Sigma of the CCF from fit'
        table2['ZP'].description = 'Zero point of the CCF from fit'
        table2['SLOPE'].description = 'Slope of the CCF from fit'
        table2['AMP'].description = 'Amplitude of the CCF from fit'
        table2['FWHM'].description = 'Full width half maximum of the CCF from fit'
        table2['Contrast'].description = 'Contrast of the CCF from fit'

    table2['SNR'].description = 'Signal to noise ratio of the CCF'
    table2['Norm'].description = ('Normalization factor of the CCF '
                                  '(median of CCF)')
    table2['DVRMS_SP'].description = ('RV photon-noise uncertainty calc on E2DS '
                                      'spectrum [m/s]')
    table2['DVRMS_CC'].description = ('final photon-noise RV uncertainty calc '
                                      'on stacked on the CCF [m/s]')
    # ----------------------------------------------------------------------
    # archive ccf to fits file
    # ----------------------------------------------------------------------
    # get a new copy of the ccf file
    ccf_file = recipe.outputs['CCF_RV'].newcopy(params=params, fiber=fiber)
    # push mask to suffix
    suffix = ccf_file.suffix
    mask_file = os.path.basename(props['CCF_MASK']).replace('.mas', '')
    if suffix is not None:
        suffix += '_{0}'.format(mask_file).lower()
    else:
        suffix = '_ccf_{0}'.format(mask_file).lower()
    # construct the filename from file instance
    ccf_file.construct_filename(infile=infile, suffix=suffix)
    # define header keys for output file
    # copy keys from input file
    ccf_file.copy_original_keys(infile)
    # add core values (that should be in all headers)
    ccf_file.add_core_hkeys(params)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    ccf_file.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add infiles to outfile
    ccf_file.infiles = list(hfiles)
    # add fiber to file
    ccf_file.add_hkey('KW_FIBER', value=fiber)
    # ----------------------------------------------------------------------
    if fit_type == 0:
        ccf_file.add_hkey('KW_CCF_FIT_TYPE', value='aborption')
    else:
        ccf_file.add_hkey('KW_CCF_FIT_TYPE', value='emission')
    # add results from the CCF
    ccf_file.add_hkey('KW_CCF_STACK_RV', value=props['RV_STACK'])
    ccf_file.add_hkey('KW_CCF_STACK_CONTRAST', value=props['CONTRAST_STACK'])
    ccf_file.add_hkey('KW_CCF_STACK_FWHM', value=props['FWHM_STACK'])
    # ----------------------------------------------------------------------
    # add bisector values
    ccf_file.add_hkey('KW_CCF_BISECTOR', value=props['BISSPAN_STACK'])
    bs_cut_top = params['CCF_BIS_CUT_TOP']
    bs_cut_bottom = params['CCF_BIS_CUT_BOTTOM']
    bs_span = f'{bs_cut_top}%-{bs_cut_bottom}%'
    ccf_file.add_hkey('KW_CCF_BIS_SPAN', value=bs_span)
    # ----------------------------------------------------------------------
    # add SNR, norm, number of lines and dv rms
    ccf_file.add_hkey('KW_CCF_SNR_STACK', value=props['CCF_SNR_STACK'])
    ccf_file.add_hkey('KW_CCF_NORM_STACK', value=props['CCF_NORM_FACTOR_STACK'])
    ccf_file.add_hkey('KW_CCF_TOT_LINES', value=np.sum(props['TOT_LINE']))
    ccf_file.add_hkey('KW_CCF_DVRMS_SP',
                      value=np.round(props['TOT_SPEC_RMS'], 4))
    ccf_file.add_hkey('KW_CCF_DVRMS_CC',
                      value=np.round(1000 * props['CCF_PHOT_NOISE_STACK'], 4))
    # ----------------------------------------------------------------------
    # add constants used to process
    ccf_file.add_hkey('KW_CCF_MASK', value=props['CCF_MASK'])
    ccf_file.add_hkey('KW_CCF_STEP', value=props['CCF_STEP'])
    ccf_file.add_hkey('KW_CCF_WIDTH', value=props['CCF_WIDTH'])
    ccf_file.add_hkey('KW_CCF_TARGET_RV', value=props['TARGET_RV'])
    ccf_file.add_hkey('KW_CCF_SIGDET', value=props['CCF_SIGDET'])
    ccf_file.add_hkey('KW_CCF_BOXSIZE', value=props['CCF_BOXSIZE'])
    ccf_file.add_hkey('KW_CCF_MAXFLUX', value=props['CCF_MAXFLUX'])
    ccf_file.add_hkey('KW_CCF_NMAX', value=props['CCF_NMAX'])
    ccf_file.add_hkey('KW_CCF_MASK_WID', value=props['MASK_WIDTH'])
    ccf_file.add_hkey('KW_CCF_MASK_UNITS', value=props['MASK_UNITS'])
    # ----------------------------------------------------------------------
    ccf_file.add_hkey('KW_CCF_RV_WAVE_FP', value=props['RV_WAVE_FP'])
    ccf_file.add_hkey('KW_CCF_RV_SIMU_FP', value=props['RV_SIMU_FP'])
    ccf_file.add_hkey('KW_CCF_RV_DRIFT', value=props['RV_DRIFT'])
    ccf_file.add_hkey('KW_CCF_RV_OBJ', value=props['RV_OBJ'])
    ccf_file.add_hkey('KW_CCF_RV_CORR', value=props['RV_CORR'])
    ccf_file.add_hkey('KW_CCF_RV_WAVEFILE', value=props['RV_WAVEFILE'])
    ccf_file.add_hkey('KW_CCF_RV_WAVETIME', value=props['RV_WAVETIME'])
    ccf_file.add_hkey('KW_CCF_RV_TIMEDIFF', value=props['RV_TIMEDIFF'])
    ccf_file.add_hkey('KW_CCF_RV_WAVESRCE', value=props['RV_WAVESRCE'])
    # ----------------------------------------------------------------------
    # add qc parameters
    ccf_file.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # copy data
    ccf_file.data = table1
    ccf_file.datatype = 'table'
    # ----------------------------------------------------------------------
    # log that we are saving rotated image
    wargs = [fiber, ccf_file.filename]
    WLOG(params, '', textentry('40-020-00006', args=wargs))
    # define multi lists
    data_list = [table2]
    datatype_list = ['table']
    name_list = ['RV_TABLE', 'ORDER_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=ccf_file)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write multi
    ccf_file.write_multi(data_list=data_list, name_list=name_list,
                         datatype_list=datatype_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(ccf_file)


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

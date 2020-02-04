#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-21 at 12:28

@author: cook
"""
from astropy.table import Table
from astropy import constants as cc
from astropy import units as uu
import numpy as np
import os
from scipy.optimize import curve_fit
import warnings

from apero import core
from apero import locale
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.io import drs_data


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.rv.general.py'
__INSTRUMENT__ = 'None'
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
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define functions
# =============================================================================
def measure_fp_peaks(params, props, **kwargs):
    """
    Measure the positions of the FP peaks
    Returns the pixels positions and Nth order of each FP peak

    :param p: parameter dictionary, ParamDict containing constants
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

    :param loc: parameter dictionary, ParamDict containing data
            Must contain at least:
                speref: numpy array (2D), the reference spectrum
                wave: numpy array (2D), the wave solution image
                lamp: string, the lamp type (either 'hc' or 'fp')

    :return loc: parameter dictionary, the updated parameter dictionary
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
    # get gauss function
    gfunc = mp.gauss_function
    # get constants from params/kwargs
    border = pcheck(params, 'DRIFT_PEAK_BORDER_SIZE', 'border', kwargs,
                    func_name)
    size = pcheck(params, 'DRIFT_PEAK_FPBOX_SIZE', 'size', kwargs, func_name)
    siglimdict = pcheck(params, 'DRIFT_PEAK_PEAK_SIG_LIM', 'siglimdict',
                        kwargs, func_name, mapf='dict', dtype=float)
    ipeakspace = pcheck(params, 'DRIFT_PEAK_IPEAK_SPACING', 'ipeakspace',
                        kwargs, func_name)

    # get the reference data and the wave data
    speref = np.array(props['SPEREF'])
    wave = props['WAVE']
    lamp = props['LAMP']

    # storage for order of peaks
    allordpeak = []
    allxpeak = []
    allewpeak = []
    allvrpeak = []
    allllpeak = []
    allamppeak = []
    # loop through the orders
    for order_num in range(speref.shape[0]):
        # storage for order of peaks
        ordpeak = []
        xpeak = []
        ewpeak = []
        vrpeak = []
        llpeak = []
        amppeak = []
        # get the pixels for this order
        tmp = np.array(speref[order_num, :])
        # For numerical sanity all values less than zero set to zero
        tmp[~np.isfinite(tmp)] = 0
        tmp[tmp < 0] = 0
        # set border pixels to zero to avoid fit starting off the edge of image
        tmp[0: border + 1] = 0
        tmp[-(border + 1):] = 0

        # normalize by the 98th percentile - avoids super-spurois pixels but
        #   keeps the top of the blaze around 1
        # norm = np.nanpercentile(tmp, 98)
        # tmp /= norm

        # peak value depends on type of lamp
        limit = mp.nanmedian(tmp) * siglimdict[lamp]

        # define the maximum pixel value of the normalized array
        maxtmp = mp.nanmax(tmp)
        # set up loop constants
        xprev, ipeak = -99, 0
        nreject = 0
        # loop for peaks that are above a value of limit
        w_all = []
        while maxtmp > limit:
            # find the position of the maximum
            maxpos = np.argmax(tmp)
            # define an area around the maximum peak
            index = np.arange(-size, 1 + size, 1) + maxpos
            index = np.array(index).astype(int)
            # try to fit a gaussian to that peak
            try:
                # set initial guess
                p0 = [tmp[maxpos], maxpos, 1.0, mp.nanmin(tmp[index])]
                # do gauss fit
                #    gg = [mean, amplitude, sigma, dc]
                with warnings.catch_warnings(record=True) as w:
                    # noinspection PyTypeChecker
                    gg, pcov = curve_fit(gfunc, index, tmp[index], p0=p0)
                    w_all += list(w)
            except ValueError:
                # log that ydata or xdata contains NaNs
                WLOG(params, 'warning', TextEntry('00-018-00001'))
                gg = [np.nan, np.nan, np.nan, np.nan]
            except RuntimeError:
                # WLOG(p, 'warning', 'Least-squares fails')
                gg = [np.nan, np.nan, np.nan, np.nan]
            # little sanity check to be sure that the peak is not the same as
            #    we got before and that there is something fishy with the
            #    detection - dx is the distance from last peak
            dx = np.abs(xprev - gg[1])
            # if the distance from last position > 2 - we have a new fit
            if dx > ipeakspace:
                # subtract off the gaussian without the dc level
                # (leave dc for other peaks
                tmp[index] -= gfunc(index, gg[0], gg[1], gg[2], 0)
            # else just set this region to zero, this is a bogus peak that
            #    cannot be fitted
            else:
                tmp[index] = 0
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
            else:
                # add to rejected
                nreject += 1
            # recalculate the max peak
            maxtmp = mp.nanmax(tmp)
            # set previous peak to this one
            xprev = gg[1]
            # iterator
            ipeak += 1
        # display warning messages
        drs_log.warninglogger(params, w_all)
        # log how many FPs were found and how many rejected
        wargs = [order_num, ipeak, nreject]
        WLOG(params, '', TextEntry('40-018-00001', args=wargs))
        # add values to all storage (and sort by xpeak)
        indsort = np.argsort(xpeak)
        allordpeak.append(np.array(ordpeak)[indsort])
        allxpeak.append(np.array(xpeak)[indsort])
        allewpeak.append(np.array(ewpeak)[indsort])
        allvrpeak.append(np.array(vrpeak)[indsort])
        allllpeak.append(np.array(llpeak)[indsort])
        allamppeak.append(np.array(amppeak)[indsort])
    # store values in loc
    props['ORDPEAK'] = np.concatenate(allordpeak).astype(int)
    props['XPEAK'] = np.concatenate(allxpeak)
    props['EWPEAK'] = np.concatenate(allewpeak)
    props['VRPEAK'] = np.concatenate(allvrpeak)
    props['LLPEAK'] = np.concatenate(allllpeak)
    props['AMPPEAK'] = np.concatenate(allamppeak)
    # set source
    keys = ['ordpeak', 'xpeak', 'ewpeak', 'vrpeak', 'llpeak', 'amppeak']
    props.set_sources(keys, func_name)

    # Log the total number of FP lines found
    wargs = [len(props['XPEAK'])]
    WLOG(params, 'info', TextEntry('40-018-00002', args=wargs))

    # return the property parameter dictionary
    return props


def remove_wide_peaks(params, props, **kwargs):
    """
    Remove peaks that are too wide

    :param p: parameter dictionary, ParamDict containing constants

    :param loc: parameter dictionary, ParamDict containing data
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

    :param expwidth: float or None, the expected width of FP peaks - used to
                     "normalise" peaks (which are then subsequently removed
                     if > "cutwidth") if expwidth is None taken from
                     p['DRIFT_PEAK_EXP_WIDTH']
    :param cutwidth: float or None, the normalised width of FP peaks thatis too
                     large normalised width FP FWHM - expwidth
                     cut is essentially: FP FWHM < (expwidth + cutwidth), if
                     cutwidth is None taken from p['DRIFT_PEAK_NORM_WIDTH_CUT']

    :return loc: parameter dictionary, the updated parameter dictionary
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
    # get constants
    expwidth = pcheck(params, 'DRIFT_PEAK_EXP_WIDTH', 'expwidth', kwargs,
                      func_name)
    cutwidth = pcheck(params, 'DRIFT_PEAK_NORM_WIDTH_CUT', 'cutwidth',
                      kwargs, func_name)
    peak_spacing = pcheck(params, 'DRIFT_PEAK_IPEAK_SPACING', 'peak_spacing',
                          kwargs, func_name)

    # define a mask to cut out wide peaks
    mask = np.abs(np.array(props['EWPEAK']) - expwidth) < cutwidth

    # apply mask
    props['ORDPEAK'] = props['ORDPEAK'][mask]
    props['XPEAK'] = props['XPEAK'][mask]
    props['EWPEAK'] = props['EWPEAK'][mask]
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
        ewpeak_k += list(props['EWPEAK'][gg][xmask])
        vrpeak_k += list(props['VRPEAK'][gg][xmask])
        llpeak_k += list(props['LLPEAK'][gg][xmask])
        amppeak_k += list(props['AMPPEAK'][gg][xmask])

    # replace FP peak arrays in loc
    props['ORDPEAK'] = np.array(ordpeak_k)
    props['XPEAK'] = np.array(xpeak_k)
    props['EWPEAK'] = np.array(ewpeak_k)
    props['VRPEAK'] = np.array(vrpeak_k)
    props['LLPEAK'] = np.array(llpeak_k)
    props['AMPPEAK'] = np.array(amppeak_k)

    # append this function to sources
    keys = ['ordpeak', 'xpeak', 'ewpeak', 'vrpeak', 'llpeak', 'amppeak']
    props.append_sources(keys, func_name)

    # log number of lines removed for suspicious width
    wargs = [mp.nansum(~mask)]
    WLOG(params, 'info', TextEntry('40-018-00003', args=wargs))

    # log number of lines removed as double-fitted
    if len(props['XPEAK_OLD']) > len(props['XPEAK']):
        wargs = [len(props['XPEAK_OLD']) - len(props['XPEAK'])]
        WLOG(params, 'info', TextEntry('40-018-00004', args=wargs))

    # return props
    return props


def get_ccf_mask(params, filename, mask_min, mask_width, mask_units='nm'):
    func_name = __NAME__ + '.get_ccf_mask()'
    # load table
    table, absfilename = drs_data.load_ccf_mask(params, filename=filename)
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
    # use w_min to select on w_mask or keep all if w_mask_min >= 1
    if mask_min < 1.0:
        mask = w_mask > mask_min
        ll_mask_d = ll_mask_d[mask]
        ll_mask_ctr = ll_mask_ctr[mask]
        w_mask = w_mask[mask]
    # else set all w_mask to one (and use all lines in file)
    else:
        w_mask = np.ones(len(ll_mask_d))
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
        WLOG(params, 'error', TextEntry('09-020-00002', args=eargs))
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
    # get the total
    tot = mp.nansum(sxn * ((nwave * nspe) ** 2) * maskv, axis=1)
    # convert to dvrms2
    with warnings.catch_warnings(record=True) as _:
        dvrms2 = (speed_of_light_ms ** 2) / abs(tot)
    # weighted mean of dvrms2 values
    weightedmean = 1. / np.sqrt(mp.nansum(1.0 / dvrms2))
    # return dv rms and weighted mean
    return dvrms2, weightedmean


def remove_telluric_domain(params, recipe, infile, fiber, **kwargs):
    func_name = __NAME__ + '.remove_telluric_domain()'
    # get parameters from params/kwargs
    ccf_tellu_thres = pcheck(params, 'CCF_TELLU_THRES', 'ccf_tellu_thres',
                             kwargs, func_name)
    # get the image
    image = np.array(infile.data)
    # get extraction type from the header
    ext_type = infile.get_key('KW_EXT_TYPE', dtype=str)
    # get the input file (assumed to be the first file from header
    e2dsfiles = infile.read_header_key_1d_list('KW_INFILE1', dim1=None,
                                               dtype=str)
    e2dsfilename = e2dsfiles[0]
    # construct absolute path for the e2ds file
    e2dsabsfilename = os.path.join(infile.path, e2dsfilename)
    # check that e2ds file exists
    if not os.path.exists(e2dsabsfilename):
        eargs = [infile.filename, ext_type, e2dsabsfilename]
        WLOG(params, 'error', TextEntry('09-020-00003', args=eargs))
    # get infile
    e2dsinst = core.get_file_definition(ext_type, params['INSTRUMENT'],
                                        kind='red')
    # construct e2ds file
    e2dsfile = e2dsinst.newcopy(recipe=recipe, fiber=fiber)
    e2dsfile.set_filename(e2dsfilename)
    # get recon file
    reconinst = core.get_file_definition('TELLU_RECON', params['INSTRUMENT'],
                                         kind='red')
    # construct recon file
    reconfile = reconinst.newcopy(recipe=recipe, fiber=fiber)
    reconfile.construct_filename(params, infile=e2dsfile)
    # check recon file exists
    if not os.path.exists(reconfile.filename):
        eargs = [infile.filename, reconfile.name, e2dsfile.filename]
        WLOG(params, 'error', TextEntry('09-020-00003', args=eargs))
    # read recon file
    reconfile.read_file()
    # find all places below threshold
    with warnings.catch_warnings(record=True) as _:
        keep = reconfile.data > ccf_tellu_thres
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
    WLOG(params, 'warning', TextEntry('10-020-00002'))
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

        if params['DRS_PLOT'] > 0 and params['DRS_DEBUG'] > 1:
            # TODO: add plot
            pass
            # plt.plot(smooth)
            # plt.plot(image2[order_num])
            # plt.show()

    # return the filled e2ds
    return image2


def locate_reference_file(params, recipe, infile):
    # set function name
    func_name = display_func(params, 'locate_reference_file', __NAME__)
    # get pp file name
    pp_filename = infile.filename.split('_pp')[0] + '_pp.fits'
    # deal with infile being telluric file (we do not have reference file
    #   for telluric files) --> must use the telluric files "intype file"
    if infile.name == 'TELLU_OBJ':
        instance = infile.intype
    else:
        instance = infile
    # get pp file
    ppfile = instance.intype.newcopy(recipe=recipe)
    ppfile.set_filename(pp_filename)
    # check that ppfile is a ppfile
    if ppfile.suffix != '_pp':
        # log that we could not locate reference file for file
        eargs = [infile.name, ppfile.name, infile.filename, func_name]
        WLOG(params, 'error', TextEntry('00-020-00003', args=eargs))
    # make a new copy of this instance
    outfile = instance.newcopy(recipe=recipe, fiber='C')
    # construct filename
    outfile.construct_filename(params, infile=ppfile)
    # read outfile
    outfile.read_file()
    # return outfile
    return outfile


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
    mask_min = pcheck(params, 'CCF_MASK_MIN_WEIGHT', 'mask_min', kwargs,
                      func_name)
    mask_width = pcheck(params, 'CCF_MASK_WIDTH', 'mask_width', kwargs,
                        func_name)
    mask_units = pcheck(params, 'CCF_MASK_UNITS', 'mask_units', kwargs,
                        func_name)
    fit_type = pcheck(params, 'CCF_FIT_TYPE', 'fit_type', kwargs, func_name)
    ccfnmax = pcheck(params, 'CCF_N_ORD_MAX', 'ccfnmax', kwargs,
                     func_name)
    image_pixel_size = pcheck(params, 'IMAGE_PIXEL_SIZE', 'image_pixel_size',
                              kwargs, func_name)

    maxwsr = pcheck(params, 'CCF_MAX_CCF_WID_STEP_RATIO', 'maxwsr', kwargs,
                    func_name)
    # get image size
    nbo, nbpix = image.shape
    # get parameters from inputs
    ccfstep = params['INPUTS']['STEP']
    ccfwidth = params['INPUTS']['WIDTH']
    targetrv = params['INPUTS']['RV']
    # need to deal with mask coming from inputs
    if isinstance(params['INPUTS']['MASK'], list):
        ccfmask = params['INPUTS']['MASK'][0][0]
    # else mask has come from constants
    else:
        ccfmask = params['INPUTS']['MASK']
    # get the berv
    berv = bprops['USE_BERV']

    # ----------------------------------------------------------------------
    # Need some sanity checking on width and step
    # ----------------------------------------------------------------------
    if ccfstep > (ccfwidth / maxwsr):
        eargs = [ccfwidth, ccfstep, maxwsr, func_name]
        WLOG(params, 'error', TextEntry('09-020-00005', args=eargs))

    # ----------------------------------------------------------------------
    # Check we are using correct fiber
    # ----------------------------------------------------------------------
    pconst = constants.pload(params['INSTRUMENT'])
    sfiber, rfiber = pconst.FIBER_CCF()
    if fiber != sfiber:
        # log that the science fiber was not correct
        eargs = [fiber, sfiber, infile.name, infile.filename]
        WLOG(params, 'error', TextEntry('09-020-00001', args=eargs))

    # ----------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ----------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dkwargs = dict(spe=image, wave=wavemap, sigdet=noise_sigdet,
                   size=noise_size, threshold=noise_thres)
    # run DeltaVrms2D
    dvrmsref, wmeanref = delta_v_rms_2d(**dkwargs)
    # log the estimated RV uncertainty
    wargs = [fiber, wmeanref]
    WLOG(params, 'info', TextEntry('40-020-00003', args=wargs))
    # ----------------------------------------------------------------------
    # Reference plots
    # ----------------------------------------------------------------------
    # the image vs wavelength for an order
    recipe.plot('CCF_SWAVE_REF', wavemap=wavemap, image=image, fiber=fiber,
                nbo=nbo)
    # the photon noise uncertainty plot
    recipe.plot('CCF_PHOTON_UNCERT', x=np.arange(nbo), y=dvrmsref)
    # as a summary plot
    recipe.plot('SUM_CCF_PHOTON_UNCERT', x=np.arange(nbo), y=dvrmsref)
    # ----------------------------------------------------------------------
    # Do the CCF calculations
    # ----------------------------------------------------------------------
    # get the mask parameters
    mkwargs = dict(filename=ccfmask, mask_min=mask_min, mask_width=mask_width,
                   mask_units=mask_units)
    ll_mask_d, ll_mask_ctr, w_mask = get_ccf_mask(params, **mkwargs)
    # calculate the CCF
    props = ccf_calculation(params, image, blaze, wavemap, berv, targetrv,
                            ccfwidth, ccfstep, ll_mask_ctr, w_mask,
                            fit_type, fiber)

    # ----------------------------------------------------------------------
    # Calculate the mean CCF
    # ----------------------------------------------------------------------
    # get the average ccf
    mean_ccf = mp.nanmean(props['CCF'][: ccfnmax], axis=0)

    # get the fit for the normalized average ccf
    mean_ccf_coeffs, mean_ccf_fit = fit_ccf(params, 'mean', props['RV_CCF'],
                                            mean_ccf, fit_type=fit_type)
    # get the max cpp
    # TODO: How do we calculate max_cpp and what is it? Do we need it?
    # max_cpp = mp.nansum(props['CCF_MAX']) / mp.nansum(props['PIX_PASSED_ALL'])
    # get the RV value from the normalised average ccf fit center location
    ccf_rv = float(mean_ccf_coeffs[1])
    # get the contrast (ccf fit amplitude)
    ccf_contrast = np.abs(100 * mean_ccf_coeffs[0])
    # get the FWHM value
    ccf_fwhm = mean_ccf_coeffs[2] * mp.fwhm()
    # ----------------------------------------------------------------------

    # TODO: Need Etienne's help this ccf_noise is not the same as
    # TODO:   Francois one - his gives a sigdet per rv element

    #  CCF_NOISE uncertainty
    ccf_noise_tot = np.sqrt(mp.nanmean(props['CCF_NOISE'] ** 2, axis=0))
    # Calculate the slope of the CCF
    average_ccf_diff = (mean_ccf[2:] - mean_ccf[:-2])
    rv_ccf_diff = (props['RV_CCF'][2:] - props['RV_CCF'][:-2])
    ccf_slope = average_ccf_diff / rv_ccf_diff
    # Calculate the CCF oversampling
    ccf_oversamp = image_pixel_size / ccfstep
    # create a list of indices based on the oversample grid size
    flist = np.arange(np.round(len(ccf_slope) / ccf_oversamp))
    indexlist = np.array(flist * ccf_oversamp, dtype=int)
    # we only want the unique pixels (not oversampled)
    indexlist = np.unique(indexlist)
    # get the rv noise from the sum of pixels for those points that are
    #     not oversampled
    keep_ccf_slope = ccf_slope[indexlist]
    keep_ccf_noise = ccf_noise_tot[1:-1][indexlist]
    rv_noise = mp.nansum(keep_ccf_slope ** 2 / keep_ccf_noise ** 2) ** (-0.5)
    # ----------------------------------------------------------------------
    # log the stats
    wargs = [ccf_contrast, float(mean_ccf_coeffs[1]), rv_noise, ccf_fwhm]
    WLOG(params, 'info', TextEntry('40-020-00004', args=wargs))
    # ----------------------------------------------------------------------
    # add to output array
    props['MEAN_CCF'] = mean_ccf
    props['MEAN_RV'] = ccf_rv
    props['MEAN_CONTRAST'] = ccf_contrast
    props['MEAN_FWHM'] = ccf_fwhm
    props['MEAN_CCF_RES'] = mean_ccf_coeffs
    props['MEAN_CCF_FIT'] = mean_ccf_fit
    props['MEAN_RV_NOISE'] = rv_noise
    # set the source
    keys = ['MEAN_CCF', 'MEAN_RV', 'MEAN_CONTRAST', 'MEAN_FWHM', 'MEAN_CCF_RES',
            'MEAN_CCF_FIT', 'MEAN_RV_NOISE']
    props.set_sources(keys, func_name)
    # add constants to props
    props['CCF_MASK'] = ccfmask
    props['CCF_STEP'] = ccfstep
    props['CCF_WIDTH'] = ccfwidth
    props['TARGET_RV'] = targetrv
    props['CCF_SIGDET'] = noise_sigdet
    props['CCF_BOXSIZE'] = noise_size
    props['CCF_MAXFLUX'] = noise_thres
    props['CCF_NMAX'] = ccfnmax
    props['MASK_MIN'] = mask_min
    props['MASK_WIDTH'] = mask_width
    props['MASK_UNITS'] = mask_units
    # set source
    keys = ['CCF_MASK', 'CCF_STEP', 'CCF_WIDTH', 'TARGET_RV', 'CCF_SIGDET',
            'CCF_BOXSIZE', 'CCF_MAXFLUX', 'CCF_NMAX', 'MASK_MIN', 'MASK_WIDTH',
            'MASK_UNITS']
    props.set_sources(keys, func_name)

    # ------------------------------------------------------------------
    # rv ccf plot
    # ------------------------------------------------------------------
    # loop around every order
    recipe.plot('CCF_RV_FIT_LOOP', params=params, x=props['RV_CCF'],
                y=props['CCF'], yfit=props['CCF_FIT'], kind='SCIENCE',
                rv=props['CCF_FIT_COEFFS'][:, 1], ccfmask=ccfmask,
                orders=np.arange(len(props['CCF'])), order=None)
    # the mean ccf
    recipe.plot('CCF_RV_FIT', params=params, x=props['RV_CCF'],
                y=mean_ccf, yfit=mean_ccf_fit, kind='MEAN SCIENCE',
                rv=ccf_rv, ccfmask=ccfmask,
                orders=None, order=None)
    # the mean ccf for summary
    recipe.plot('SUM_CCF_RV_FIT', params=params, x=props['RV_CCF'],
                y=mean_ccf, yfit=mean_ccf_fit, kind='MEAN SCIENCE',
                rv=ccf_rv, ccfmask=ccfmask,
                orders=None, order=None)

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
    mask_min = pcheck(params, 'WAVE_CCF_MASK_MIN_WEIGHT', 'mask_min', kwargs,
                      func_name)
    mask_width = pcheck(params, 'WAVE_CCF_MASK_WIDTH', 'mask_width', kwargs,
                        func_name)
    mask_units = pcheck(params, 'WAVE_CCF_MASK_UNITS', 'mask_units', kwargs,
                        func_name)
    image_pixel_size = pcheck(params, 'IMAGE_PIXEL_SIZE', 'image_pixel_size',
                              kwargs, func_name)
    # set the berv to zero (fp have no berv)
    berv = 0
    # the fit type must be set to 1 (for emission lines)
    fit_type = 1
    # ----------------------------------------------------------------------
    # Check we are using correct fiber
    # ----------------------------------------------------------------------
    pconst = constants.pload(params['INSTRUMENT'])
    sfiber, rfiber = pconst.FIBER_CCF()
    if fiber != rfiber:
        # log that the science fiber was not correct
        eargs = [fiber, rfiber, infile.name, infile.filename]
        WLOG(params, 'error', TextEntry('09-020-00004', args=eargs))
    # ------------------------------------------------------------------
    # Compute photon noise uncertainty for FP
    # ------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dkwargs = dict(spe=image, wave=wavemap, sigdet=noise_sigdet,
                   size=noise_size, threshold=noise_thres)
    # run DeltaVrms2D
    dvrmsref, wmeanref = delta_v_rms_2d(**dkwargs)

    # log the estimated RV uncertainty
    wargs = [fiber, wmeanref]
    WLOG(params, 'info', TextEntry('40-017-00028', args=wargs))
    # ----------------------------------------------------------------------
    # Do the CCF calculations
    # ----------------------------------------------------------------------
    # get the mask parameters
    mkwargs = dict(filename=ccfmask, mask_min=mask_min, mask_width=mask_width,
                   mask_units=mask_units)
    ll_mask_d, ll_mask_ctr, w_mask = get_ccf_mask(params, **mkwargs)
    # calculate the CCF
    props = ccf_calculation(params, image, blaze, wavemap, berv, targetrv,
                            ccfwidth, ccfstep, ll_mask_ctr, w_mask, fit_type,
                            fiber)
    # ----------------------------------------------------------------------
    # Calculate the mean CCF
    # ----------------------------------------------------------------------
    # get the average ccf
    mean_ccf = mp.nanmean(props['CCF'][: ccfnmax], axis=0)

    # get the fit for the normalized average ccf
    mean_ccf_coeffs, mean_ccf_fit = fit_ccf(params, 'mean', props['RV_CCF'],
                                            mean_ccf, fit_type=fit_type)
    # get the max cpp
    # TODO: How do we calculate max_cpp and what is it? Do we need it?
    # max_cpp = mp.nansum(props['CCF_MAX']) / mp.nansum(props['PIX_PASSED_ALL'])
    # get the RV value from the normalised average ccf fit center location
    ccf_rv = float(mean_ccf_coeffs[1])
    # get the contrast (ccf fit amplitude)
    ccf_contrast = np.abs(100 * mean_ccf_coeffs[0])
    # get the FWHM value
    ccf_fwhm = mean_ccf_coeffs[2] * mp.fwhm()
    # ----------------------------------------------------------------------

    # TODO: Need Etienne's help this ccf_noise is not the same as
    # TODO:   Francois one - his gives a sigdet per rv element

    #  CCF_NOISE uncertainty
    ccf_noise_tot = np.sqrt(mp.nanmean(props['CCF_NOISE'] ** 2, axis=0))
    # Calculate the slope of the CCF
    average_ccf_diff = (mean_ccf[2:] - mean_ccf[:-2])
    rv_ccf_diff = (props['RV_CCF'][2:] - props['RV_CCF'][:-2])
    ccf_slope = average_ccf_diff / rv_ccf_diff
    # Calculate the CCF oversampling
    ccf_oversamp = image_pixel_size / ccfstep
    # create a list of indices based on the oversample grid size
    flist = np.arange(np.round(len(ccf_slope) / ccf_oversamp))
    indexlist = np.array(flist * ccf_oversamp, dtype=int)
    # we only want the unique pixels (not oversampled)
    indexlist = np.unique(indexlist)
    # get the rv noise from the sum of pixels for those points that are
    #     not oversampled
    keep_ccf_slope = ccf_slope[indexlist]
    keep_ccf_noise = ccf_noise_tot[1:-1][indexlist]
    rv_noise = mp.nansum(keep_ccf_slope ** 2 / keep_ccf_noise ** 2) ** (-0.5)
    # ----------------------------------------------------------------------
    # log the stats
    wargs = [ccf_contrast, float(mean_ccf_coeffs[1]), rv_noise, ccf_fwhm]
    WLOG(params, 'info', TextEntry('40-020-00004', args=wargs))
    # ----------------------------------------------------------------------
    # add to output array
    props['MEAN_CCF'] = mean_ccf
    props['MEAN_RV'] = ccf_rv
    props['MEAN_CONTRAST'] = ccf_contrast
    props['MEAN_FWHM'] = ccf_fwhm
    props['MEAN_CCF_COEFFS'] = mean_ccf_coeffs
    props['MEAN_CCF_FIT'] = mean_ccf_fit
    props['MEAN_RV_NOISE'] = rv_noise
    # set the source
    keys = ['MEAN_CCF', 'MEAN_RV', 'MEAN_CONTRAST', 'MEAN_FWHM',
            'MEAN_CCF_COEFFS', 'MEAN_CCF_FIT', 'MEAN_RV_NOISE']
    props.set_sources(keys, func_name)
    # add constants to props
    props['CCF_MASK'] = ccfmask
    props['CCF_STEP'] = ccfstep
    props['CCF_WIDTH'] = ccfwidth
    props['TARGET_RV'] = targetrv
    props['CCF_SIGDET'] = noise_sigdet
    props['CCF_BOXSIZE'] = noise_size
    props['CCF_MAXFLUX'] = noise_thres
    props['CCF_NMAX'] = ccfnmax
    props['MASK_MIN'] = mask_min
    props['MASK_WIDTH'] = mask_width
    props['MASK_UNITS'] = mask_units
    # set source
    keys = ['CCF_MASK', 'CCF_STEP', 'CCF_WIDTH', 'TARGET_RV', 'CCF_SIGDET',
            'CCF_BOXSIZE', 'CCF_MAXFLUX', 'CCF_NMAX', 'MASK_MIN', 'MASK_WIDTH',
            'MASK_UNITS']
    props.set_sources(keys, func_name)

    # ----------------------------------------------------------------------
    # rv ccf plot
    # ----------------------------------------------------------------------
    # loop around every order
    recipe.plot('CCF_RV_FIT_LOOP', params=params, x=props['RV_CCF'],
                y=props['CCF'], yfit=props['CCF_FIT'], kind='FP',
                rv=props['CCF_FIT_COEFFS'][:, 1], ccfmask=ccfmask,
                orders=np.arange(len(props['CCF'])), order=None)
    # the mean ccf
    recipe.plot('CCF_RV_FIT', params=params, x=props['RV_CCF'],
                y=mean_ccf, yfit=mean_ccf_fit, kind='MEAN FP',
                rv=props['MEAN_CCF_COEFFS'][1], ccfmask=ccfmask,
                orders=None, order=None)
    # the mean ccf for summary
    recipe.plot('SUM_CCF_RV_FIT', params=params, x=props['RV_CCF'],
                y=mean_ccf, yfit=mean_ccf_fit, kind='MEAN SCIENCE',
                rv=ccf_rv, ccfmask=ccfmask,
                orders=None, order=None)

    # TODO : Add QC of the FP CCF once they are defined

    # return the rv props
    return props


def ccf_calculation(params, image, blaze, wavemap, berv, targetrv, ccfwidth,
                    ccfstep, mask_centers, mask_weights, fit_type, fiber,
                    **kwargs):
    # set function name
    func_name = display_func(params, 'calculate_ccf', __NAME__)
    # get rvmin and rvmax
    rvmin = targetrv - ccfwidth
    rvmin = pcheck(params, 'RVMIN', 'rvmin', kwargs, func_name, default=rvmin)
    rvmax = targetrv + ccfwidth + ccfstep
    rvmax = pcheck(params, 'RVMAX', 'rvmax', kwargs, func_name, default=rvmax)
    # get the dimensions
    nbo, nbpix = image.shape
    # create a rv ccf range
    rv_ccf = np.arange(rvmin, rvmax, ccfstep)
    # storage of the ccf
    ccf_all = []
    ccf_noise_all = []
    ccf_all_fit = []
    ccf_all_results = []
    ccf_lines = []
    ccf_all_snr = []
    ccf_norm_all = []
    # ----------------------------------------------------------------------
    # loop around the orders
    for order_num in range(nbo):
        # log the process
        WLOG(params, '', TextEntry('40-020-00005', args=[fiber, order_num]))
        # ------------------------------------------------------------------
        # get this orders values
        wa_ord = np.array(wavemap[order_num])
        sp_ord = np.array(image[order_num])
        bl_ord = np.array(blaze[order_num])
        # ------------------------------------------------------------------
        # find any places in spectrum or blaze where pixel is NaN
        nanmask = np.isnan(sp_ord) | np.isnan(bl_ord)
        # ------------------------------------------------------------------
        # deal with all nan
        if np.sum(nanmask) == nbpix:
            # log all NaN
            wargs = [order_num]
            WLOG(params, 'warning', TextEntry('10-020-00004', args=wargs))
            # set all values to NaN
            ccf_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, 4))
            ccf_noise_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_lines.append(0)
            ccf_all_snr.append(np.nan)
            ccf_norm_all.append(np.nan)
            continue
        # ------------------------------------------------------------------
        # set the spectrum or blaze NaN pixels to zero (dealt with by divide)
        sp_ord[nanmask] = 0
        bl_ord[nanmask] = 0
        # ------------------------------------------------------------------
        # spline the spectrum and the blaze
        spline_sp = mp.iuv_spline(wa_ord, sp_ord, k=5, ext=1)
        spline_bl = mp.iuv_spline(wa_ord, bl_ord, k=5, ext=1)
        # ------------------------------------------------------------------
        # set up the ccf for this order
        ccf_ord = np.zeros_like(rv_ccf)
        # ------------------------------------------------------------------
        # get the wavelength shift (dv) in relativistic way
        wave_shifts = mp.relativistic_waveshift(rv_ccf - berv)
        # ------------------------------------------------------------------
        # set number of valid lines used to zero
        numlines = 0
        # loop around the rvs and calculate the CCF at this point
        for rv_element in range(len(rv_ccf)):
            wave_tmp = mask_centers * wave_shifts[rv_element]
            part1 = np.sum(spline_sp(wave_tmp) * mask_weights)
            part2 = np.sum(spline_bl(wave_tmp) * mask_weights)
            numlines = np.sum(spline_bl(wave_tmp) != 0)
            # CCF is the division of the sums
            with warnings.catch_warnings(record=True) as _:
                ccf_ord[rv_element] = part1 / part2
        # ------------------------------------------------------------------
        # deal with NaNs in ccf
        if np.sum(np.isnan(ccf_ord)) > 0:
            # log all NaN
            wargs = [order_num]
            WLOG(params, 'warning', TextEntry('10-020-00005', args=wargs))
            # set all values to NaN
            ccf_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_fit.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_all_results.append(np.repeat(np.nan, 4))
            ccf_noise_all.append(np.repeat(np.nan, len(rv_ccf)))
            ccf_lines.append(0)
            ccf_all_snr.append(np.nan)
            ccf_norm_all.append(np.nan)
            continue
        # ------------------------------------------------------------------
        # normalise each orders CCF to median
        ccf_norm = mp.nanmedian(ccf_ord)
        ccf_ord = ccf_ord / ccf_norm
        # ------------------------------------------------------------------
        # fit the CCF with a gaussian
        fargs = [order_num, rv_ccf, ccf_ord, fit_type]
        ccf_coeffs_ord, ccf_fit_ord = fit_ccf(params, *fargs)
        # ------------------------------------------------------------------
        # calculate the residuals of the ccf fit
        res = ccf_ord - ccf_fit_ord
        # calculate the CCF noise per order
        ccf_noise = np.array(res)
        # calculate the snr for this order
        ccf_snr = np.abs(ccf_coeffs_ord[0] / mp.nanmedian(np.abs(ccf_noise)))
        # ------------------------------------------------------------------
        # append ccf to storage
        ccf_all.append(ccf_ord)
        ccf_all_fit.append(ccf_fit_ord)
        ccf_all_results.append(ccf_coeffs_ord)
        ccf_noise_all.append(ccf_noise)
        ccf_lines.append(numlines)
        ccf_all_snr.append(ccf_snr)
        ccf_norm_all.append(ccf_norm)

    # store outputs in param dict
    props = ParamDict()
    props['RV_CCF'] = rv_ccf
    props['CCF'] = np.array(ccf_all)
    props['CCF_LINES'] = np.array(ccf_lines)
    props['TOT_LINE'] = np.sum(ccf_lines)
    props['CCF_NOISE'] = np.array(ccf_noise_all)
    props['CCF_SNR'] = np.array(ccf_all_snr)
    props['CCF_FIT'] = np.array(ccf_all_fit)
    props['CCF_FIT_COEFFS'] = np.array(ccf_all_results)
    props['CCF_NORM'] = np.array(ccf_norm_all)

    # set sources
    keys = ['RV_CCF', 'CCF', 'TOT_LINE', 'CCF_NOISE', 'CCF_FIT', 'CCF_SNR',
            'CCF_FIT_COEFFS', 'CCF_LINES', 'CCF_NORM']
    props.set_sources(keys, func_name)
    # return props
    return props


def fit_ccf(params, order_num, rv, ccf, fit_type):
    """
    Fit the CCF to a guassian function

    :param rv: numpy array (1D), the radial velocities for the line
    :param ccf: numpy array (1D), the CCF values for the line
    :param fit_type: int, if "0" then we have an absorption line
                          if "1" then we have an emission line

    :return result: numpy array (1D), the fit parameters in the
                    following order:

                [amplitude, center, fwhm, offset from 0 (in y-direction)]

    :return ccf_fit: numpy array (1D), the fit values, i.e. the gaussian values
                     for the fit parameters in "result"
    """
    func_name = __NAME__ + '.fit_ccf()'
    # deal with inconsistent lengths
    if len(rv) != len(ccf):
        eargs = [len(rv), len(ccf), func_name]
        WLOG(params, 'error', TextEntry('00-020-00001', args=eargs))

    # deal with all nans
    if np.sum(np.isnan(ccf)) == len(ccf):
        # log warning about all NaN ccf
        wargs = [order_num]
        WLOG(params, 'warning', TextEntry('10-020-00001', args=wargs))
        # return NaNs
        result = np.zeros(4) * np.nan
        ccf_fit = np.zeros_like(ccf) * np.nan
        return result, ccf_fit

    # get constants
    max_ccf, min_ccf = mp.nanmax(ccf), mp.nanmin(ccf)
    argmin, argmax = mp.nanargmin(ccf), mp.nanargmax(ccf)
    diff = max_ccf - min_ccf
    rvdiff = rv[1] - rv[0]
    # set up guess for gaussian fit
    # if fit_type == 0 then we have absorption lines
    if fit_type == 0:
        if mp.nanmax(ccf) != 0:
            a = np.array([-diff / max_ccf, rv[argmin], 4 * rvdiff, 0])
        else:
            a = np.zeros(4)
    # else (fit_type == 1) then we have emission lines
    else:
        a = np.array([diff / max_ccf, rv[argmax], 4 * rvdiff, 1])
    # normalise y
    y = ccf / max_ccf - 1 + fit_type
    # x is just the RVs
    x = rv
    # uniform weights
    w = np.ones(len(ccf))
    # get gaussian fit
    nanmask = np.isfinite(y)
    y[~nanmask] = 0.0
    # fit the gaussian
    try:
        with warnings.catch_warnings(record=True) as _:
            result, fit = mp.fitgaussian(x, y, weights=w, guess=a)
    except RuntimeError:
        result = np.repeat(np.nan, 4)
        fit = np.repeat(np.nan, len(x))

    # scale the ccf
    ccf_fit = (fit + 1 - fit_type) * max_ccf

    # return the best guess and the gaussian fit
    return result, ccf_fit


# =============================================================================
# Define writing functions
# =============================================================================
def write_ccf(params, recipe, infile, props, rawfiles, combine, qc_params,
              fiber):
    # ----------------------------------------------------------------------
    # produce CCF table
    table1 = Table()
    table1['RV'] = props['RV_CCF']
    for order_num in range(len(props['CCF'])):
        table1['ORDER{0:02d}'.format(order_num)] = props['CCF'][order_num]
    table1['COMBINED'] = props['MEAN_CCF']
    # ----------------------------------------------------------------------
    # produce stats table
    table2 = Table()
    table2['ORDERS'] = np.arange(len(props['CCF'])).astype(int)
    table2['NLINES'] = props['CCF_LINES']
    # get the coefficients
    coeffs = props['CCF_FIT_COEFFS']
    table2['CONTRAST'] = np.abs(100 * coeffs[:, 0])
    table2['RV'] = coeffs[:, 1]
    table2['FWHM'] = coeffs[:, 2]
    table2['DC'] = coeffs[:, 3]
    table2['SNR'] = props['CCF_SNR']
    table2['NORM'] = props['CCF_NORM']
    # ----------------------------------------------------------------------
    # archive ccf to fits file
    # ----------------------------------------------------------------------
    # get a new copy of the ccf file
    ccf_file = recipe.outputs['CCF_RV'].newcopy(recipe=recipe, fiber=fiber)
    # push mask to suffix
    suffix = ccf_file.suffix
    mask_file = os.path.basename(props['CCF_MASK']).replace('.mas', '')
    if suffix is not None:
        suffix += '_{0}'.format(mask_file).lower()
    else:
        suffix = '_ccf_{0}'.format(mask_file).lower()
    # construct the filename from file instance
    ccf_file.construct_filename(params, infile=infile, suffix=suffix)
    # define header keys for output file
    # copy keys from input file
    ccf_file.copy_original_keys(infile)
    # add version
    ccf_file.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    ccf_file.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    ccf_file.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    ccf_file.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    ccf_file.add_hkey('KW_OUTPUT', value=ccf_file.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    ccf_file.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add fiber to file
    ccf_file.add_hkey('KW_FIBER', value=fiber)
    # ----------------------------------------------------------------------
    # add results from the CCF
    ccf_file.add_hkey('KW_CCF_MEAN_RV', value=props['MEAN_RV'])
    ccf_file.add_hkey('KW_CCF_MEAN_CONSTRAST', value=props['MEAN_CONTRAST'])
    ccf_file.add_hkey('KW_CCF_MEAN_FWHM', value=props['MEAN_FWHM'])
    ccf_file.add_hkey('KW_CCF_MEAN_RV_NOISE', value=props['MEAN_RV_NOISE'])
    ccf_file.add_hkey('KW_CCF_TOT_LINES', value=props['TOT_LINE'])
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
    ccf_file.add_hkey('KW_CCF_MASK_MIN', value=props['MASK_MIN'])
    ccf_file.add_hkey('KW_CCF_MASK_WID', value=props['MASK_WIDTH'])
    ccf_file.add_hkey('KW_CCF_MASK_UNITS', value=props['MASK_UNITS'])
    # ----------------------------------------------------------------------
    ccf_file.add_hkey('KW_CCF_RV_WAVE_FP', value=props['RV_WAVE_FP'])
    ccf_file.add_hkey('KW_CCF_RV_SIMU_FP', value=props['RV_SIMU_FP'])
    ccf_file.add_hkey('KW_CCF_RV_DRIFT', value=props['RV_DRIFT'])
    ccf_file.add_hkey('KW_CCF_RV_OBJ', value=props['RV_OBJ'])
    ccf_file.add_hkey('KW_CCF_RV_CORR', value=props['RV_CORR'])
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
    WLOG(params, '', TextEntry('40-020-00006', args=wargs))
    # write multi
    ccf_file.write_multi(data_list=[table2], datatype_list=['table'])
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

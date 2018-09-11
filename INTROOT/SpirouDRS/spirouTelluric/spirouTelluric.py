#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-12 16:28
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
import os
from astropy import constants
from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouImage
from SpirouDRS.spirouCore import spirouMath


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'obj_mk_tellu.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Custom parameter dictionary
ParamDict = spirouConfig.ParamDict
# Get sigma FWHM
SIG_FWHM = spirouCore.spirouMath.fwhm()
# speed of light
CONSTANT_C = constants.c.value


# =============================================================================
# Define functions
# =============================================================================
def get_normalized_blaze(p, loc, hdr):
    func_name = __NAME__ + '.get_normalized_blaze()'
    # Get the blaze
    blaze = spirouImage.ReadBlazeFile(p, hdr)
    # we mask domains that have <20% of the peak blaze of their respective order
    blaze_norm = np.array(blaze)
    for iord in range(blaze.shape[0]):
        blaze_norm[iord, :] /= np.percentile(blaze_norm[iord, :],
                                             p['TELLU_BLAZE_PERCENTILE'])
    blaze_norm[blaze_norm < p['TELLU_CUT_BLAZE_NORM']] = np.nan
    # add to loc
    loc['BLAZE'] = blaze
    loc['NBLAZE'] = blaze_norm
    loc.set_sources(['BLAZE', 'NBLAZE'], func_name)
    # return loc
    return loc


def construct_convolution_kernal1(p, loc):
    func_name = __NAME__ + '.construct_convolution_kernal()'
    # get the number of kernal pixels
    npix_ker = int(np.ceil(3 * p['FWHM_PIXEL_LSF'] * 1.5 / 2) * 2 + 1)
    # set up the kernel exponent
    ker = np.arange(npix_ker) - npix_ker // 2
    # kernal is the a gaussian
    ker = np.exp(-0.5 * (ker / (p['FWHM_PIXEL_LSF'] / SIG_FWHM)) ** 2)
    # we only want an approximation of the absorption to find the continuum
    #    and estimate chemical abundances.
    #    there's no need for a varying kernel shape
    ker /= np.sum(ker)
    # add to loc
    loc['KER'] = ker
    loc.set_source('KER', func_name)
    # return loc
    return loc


def get_molecular_tell_lines(p, loc):
    func_name = __NAME__ + '.get_molecular_tell_lines()'
    # get x and y dimension
    ydim, xdim = loc['DATA'].shape
    # representative atmospheric transmission
    # tapas = pyfits.getdata('tapas_model.fits')
    tapas_file = spirouDB.GetDatabaseTellMole(p)
    tdata = spirouImage.ReadImage(p, tapas_file, kind='FLAT')
    tapas, thdr, tcmt, _, _ = tdata

    # load all current telluric convolve files
    convole_files = spirouDB.GetDatabaseTellConv(p, required=False)

    # tapas spectra resampled onto our data wavelength vector
    tapas_all_species = np.zeros([len(p['TELLU_ABSORBERS']), xdim * ydim])
    # TODO: Make this the date and not the wave file name??
    wave_file = os.path.basename(loc['WAVEFILE'])
    convolve_file_name = wave_file.replace('.fits', '_tapas_convolved.npy')
    convolve_file = os.path.join(p['ARG_FILE_DIR'], convolve_file_name)

    # find tapas file in files
    if convolve_file not in convole_files:
        generate = True
    else:
        # if we already have a file for this wavelength just open it
        try:
            # load with numpy
            tapas_all_species = np.load(convolve_file)
            # log loading
            wmsg = 'Loading Tapas convolve file: {0}'
            WLOG('', p['LOG_OPT'], wmsg.format(convolve_file_name))
            # add name to loc
            loc['TAPAS_FNAME'], loc['TAPAS_ABSNAME'] = None, None
            generate = False
        # if we don't have a tapas file for this wavelength soltuion calculate it
        except Exception:
            generate = True
    # if we don't have tapas_all_species generate
    if generate:
        # loop around each molecule in the absorbers list
        #    (must be in
        for n_species, molecule in enumerate(p['TELLU_ABSORBERS']):
            # log process
            wmsg = 'Processing molecule: {0}'
            WLOG('', p['LOG_OPT'], wmsg.format(molecule))
            # get wavelengths
            lam = tapas['wavelength']
            # get molecule transmission
            trans = tapas['trans_{0}'.format(molecule)]
            # interpolate with Univariate Spline
            tapas_spline = IUVSpline(lam, trans)
            # log the mean transmission level
            wmsg = '\tMean Trans level: {0:.3f}'.format(np.mean(trans))
            WLOG('', p['LOG_OPT'], wmsg)
            # convolve all tapas absorption to the SPIRou approximate resolution
            for iord in range(49):
                # get the order position
                start = iord * xdim
                end = (iord * xdim) + xdim
                # interpolate the values at these points
                svalues = tapas_spline(loc['WAVE'][iord, :])
                # convolve with a gaussian function
                cvalues = np.convolve(svalues, loc['KER'], mode='same')
                # add to storage
                tapas_all_species[n_species, start: end] = cvalues
        # deal with non-real values (must be between 0 and 1
        tapas_all_species[tapas_all_species > 1] = 1
        tapas_all_species[tapas_all_species < 0] = 0
        # save the file
        np.save(convolve_file, tapas_all_species)
        # add name to loc
        loc['TAPAS_ABSNAME'] = convolve_file
        loc['TAPAS_FNAME'] = os.path.basename(convolve_file)
    # finally add all species to loc
    loc['TAPAS_ALL_SPECIES'] = tapas_all_species
    # add sources
    skeys = ['TAPAS_ALL_SPECIES', 'TAPAS_FNAME']
    loc.set_sources(skeys, func_name)
    # return loc
    return loc


def construct_convolution_kernal2(p, loc, vsini):
    func_name = __NAME__ + '.construct_convolution_kernal2()'

    # gaussian ew for vinsi km/s
    ew = vsini / p['TELLU_MED_SAMPLING'] / SIG_FWHM
    # set up the kernel exponent
    xx = np.arange(ew * 6) - ew * 3
    # kernal is the a gaussian
    ker2 = np.exp(-.5 * (xx / ew) ** 2)

    ker2 /= np.sum(ker2)
    # add to loc
    loc['KER2'] = ker2
    loc.set_source('KER2', func_name)
    # return loc
    return loc


def calculate_absorption_pca(p, loc, x, mask):
    func_name = __NAME__ + '.calculate_absorption_pca()'
    # get constants from p
    npc = p['TELLU_NUMBER_OF_PRINCIPLE_COMP']

    # get eigen values
    eig_u, eig_s, eig_vt = np.linalg.svd(x[:, mask], full_matrices=False)

    # if we are adding the derivatives to the pc need extra components
    if p['ADD_DERIV_PC']:
        # the npc+1 term will be the derivative of the first PC
        # the npc+2 term will be the broadning factor the first PC
        pc = np.zeros([np.product(loc['DATA'].shape), npc + 2])
    else:
        # create pc image
        pc = np.zeros([np.product(loc['DATA'].shape), npc])

    # fill pc image
    with warnings.catch_warnings(record=True) as w:
        for it in range(npc):
            for jt in range(x.shape[0]):
                pc[:, it] += eig_u[jt, it] * x[jt, :]

    # if we are adding the derivatives add them now
    if p['ADD_DERIV_PC']:
        # first extra is the first derivative
        pc[:, npc] = np.gradient(pc[:, 0])
        # second extra is the second derivative
        pc[:, npc + 1] = np.gradient(np.gradient(pc[:, 0]))
        # number of components is two longer now
        npc += 2

    # if we are fitting the derivative change the fit parameter
    if p['FIT_DERIV_PC']:
        fit_pc = np.gradient(pc, axis=0)
    # else we are fitting the principle components themselves
    else:
        fit_pc = np.array(pc)

    # save pc image to loc
    loc['PC'] = pc
    loc['NPC'] = npc
    loc['FIT_PC'] = fit_pc
    loc.set_sources(['PC', 'NPC', 'FIT_PC'], func_name)
    # return loc
    return loc


def get_berv_value(p, hdr, filename=None):
    # deal with no filename
    if filename is None:
        if '@@@fname' in hdr:
            filename = hdr['@@@fname']
        else:
            filename = 'UNKNOWN'

    # Check for BERV key in header
    if p['KW_BERV'][0] not in hdr:
        emsg = 'HEADER error, file="{0}". Keyword {1} not found'
        eargs = [filename, p['KW_BERV'][0]]
        # TODO: CHANGE TO ERROR
        WLOG('warning', p['LOG_OPT'], emsg.format(*eargs))
        dv, bjd, bvmax = 0.0, -9999, 0.0
    else:
        # Get the Barycentric correction from header
        dv = hdr[p['KW_BERV'][0]]
        bjd = hdr[p['KW_BJD'][0]]
        bvmax = hdr[p['KW_BERV_MAX'][0]]
    # return dv, bjd, dvmax
    return dv, bjd, bvmax


def interp_at_shifted_wavelengths(p, loc, thdr):
    func_name = __NAME__ + '.interp_at_shifted_wavelengths()'
    # Get the Barycentric correction from header
    dv, _, _ = get_berv_value(p, thdr)
    # set up storage for template
    template2 = np.zeros(np.product(loc['DATA'].shape))
    ydim, xdim = loc['DATA'].shape
    # loop around orders
    for order_num in range(ydim):
        # find good (not NaN) pixels
        keep = np.isfinite(loc['TEMPLATE'][order_num, :])
        # if we have enough values spline them
        if np.sum(keep) > p['TELLU_FIT_KEEP_FRAC']:
            # define keep wave
            keepwave = loc['WAVE_IT'][order_num, keep]
            # define keep temp
            keeptemp = loc['TEMPLATE'][order_num, keep]
            # calculate interpolation for keep temp at keep wave
            spline = IUVSpline(keepwave, keeptemp, ext=3)
            # interpolate at shifted values
            dvshift = 1 + (dv / CONSTANT_C)
            waveshift = loc['WAVE_IT'][order_num, :] * dvshift
            # interpolate at shifted wavelength
            start = order_num * xdim
            end = order_num * xdim + xdim
            template2[start:end] = spline(waveshift)

    # save to loc
    loc['TEMPLATE2'] = template2
    loc.set_source('TEMPLATE2', func_name)
    # return loc
    return loc


def calc_recon_abso(p, loc):
    func_name = __NAME__ + '.calc_recon_abso()'
    # get data from loc
    sp = loc['sp']
    tapas_all_species = loc['TAPAS_ALL_SPECIES']
    amps_abso_total = loc['AMPS_ABSOL_TOTAL']
    # get data dimensions
    ydim, xdim = loc['DATA'].shape
    # redefine storage for recon absorption
    recon_abso = np.ones(np.product(loc['DATA'].shape))
    # flatten spectrum and wavelengths
    sp2 = sp.ravel()
    wave2 = loc['WAVE_IT'].ravel()
    # get the normalisation factor
    # TODO: Not used??
    norm = np.nanmedian(sp2)
    # define the good pixels as those above minimum transmission
    keep = tapas_all_species[0, :] > p['TELLU_FIT_MIN_TRANSMISSION']
    # also require wavelength constraints
    keep &= (wave2 > p['TELLU_LAMBDA_MIN'])
    keep &= (wave2 < p['TELLU_LAMBDA_MAX'])
    # construct convolution kernel
    loc = construct_convolution_kernal2(p, loc, p['TELLU_FIT_VSINI'])
    # ------------------------------------------------------------------
    # loop around a number of times
    for ite in range(p['TELLU_FIT_NITER']):
        # --------------------------------------------------------------
        # if we don't have a template construct one
        if not loc['FLAG_TEMPLATE']:
            # define template2 to fill
            template2 = np.zeros(np.product(loc['DATA'].shape))
            # loop around orders
            for order_num in range(ydim):
                # get start and end points
                start = order_num * xdim
                end = order_num * xdim + xdim
                # produce a mask of good transmission
                order_tapas = tapas_all_species[0, start:end]
                mask = order_tapas > p['TRANSMISSION_CUT']
                # get good transmission spectrum
                spgood = sp[order_num, :] * np.array(mask, dtype=float)
                recongood = recon_abso[start:end]
                # convolve spectrum
                ckwargs = dict(v=loc['KER2'], mode='same')
                sp2b = np.convolve(spgood / recongood, **ckwargs)
                # convolve mask for weights
                ww = np.convolve(np.array(mask, dtype=float), **ckwargs)
                # wave weighted convolved spectrum into template2
                with warnings.catch_warnings(record=True) as w:
                    template2[start:end] = sp2b / ww
        # else we have template so load it
        else:
            template2 = loc['TEMPLATE2']
        # --------------------------------------------------------------
        # get residual spectrum
        with warnings.catch_warnings(record=True) as w:
            resspec = (sp2 / template2) / recon_abso
        # --------------------------------------------------------------
        if loc['FLAG_TEMPLATE']:
            # construct convolution kernel
            vsini = p['TELLU_FIT_VSINI2']
            loc = construct_convolution_kernal2(p, loc, vsini)
            # loop around orders
            for order_num in range(ydim):
                # get start and end points
                start = order_num * xdim
                end = order_num * xdim + xdim
                # produce a mask of good transmission
                order_tapas = tapas_all_species[0, start:end]
                mask = order_tapas > p['TRANSMISSION_CUT']
                fmask = np.array(mask, dtype=float)
                # get good transmission spectrum
                with warnings.catch_warnings(record=True) as w:
                    resspecgood = resspec[start:end] * fmask
                    recongood = recon_abso[start:end]
                # convolve spectrum
                ckwargs = dict(v=loc['KER2'], mode='same')
                with warnings.catch_warnings(record=True) as w:
                    sp2b = np.convolve(resspecgood / recongood, **ckwargs)
                # convolve mask for weights
                ww = np.convolve(np.array(mask, dtype=float), **ckwargs)
                # wave weighted convolved spectrum into dd
                with warnings.catch_warnings(record=True) as w:
                    resspec[start:end] = resspec[start:end] / (sp2b / ww)
        # --------------------------------------------------------------
        # Log dd and subtract median
        # log dd
        with warnings.catch_warnings(record=True) as w:
            log_resspec = np.log(resspec)
        # --------------------------------------------------------------
        # subtract off the median from each order
        for order_num in range(ydim):
            # get start and end points
            start = order_num * xdim
            end = order_num * xdim + xdim
            # skip if whole order is NaNs
            if np.sum(np.isfinite(log_resspec[start:end])) == 0:
                continue
            # get median
            log_resspec_med = np.nanmedian(log_resspec[start:end])
            # subtract of median
            log_resspec[start:end] = log_resspec[start:end] - log_resspec_med
        # --------------------------------------------------------------
        # set up fit
        if p['FIT_DERIV_PC']:
            fit_dd = np.gradient(log_resspec)
        else:
            fit_dd = np.array(log_resspec)
        # --------------------------------------------------------------
        # identify good pixels to keep
        keep &= np.isfinite(fit_dd)
        keep &= np.sum(np.isfinite(loc['FIT_PC']), axis=1) == loc['NPC']
        # log number of kept pixels
        wmsg = 'Number to keep total = {0}'.format(np.sum(keep))
        WLOG('', p['LOG_OPT'], wmsg)
        # --------------------------------------------------------------
        # calculate amplitudes and reconstructed spectrum
        largs = [fit_dd[keep], loc['FIT_PC'][keep, :]]
        amps, recon = lin_mini(*largs)
        # --------------------------------------------------------------
        # set up storage for absorption array 2
        abso2 = np.zeros(len(resspec))
        with warnings.catch_warnings(record=True) as w:
            for ipc in range(len(amps)):
                amps_abso_total[ipc] += amps[ipc]
                abso2 += loc['PC'][:, ipc] * amps[ipc]
            recon_abso *= np.exp(abso2)

    # save outputs to loc
    loc['SP2'] = sp2
    loc['TEMPLATE2'] = template2
    loc['RECON_ABSO'] = recon_abso
    loc['AMPS_ABSOL_TOTAL'] = amps_abso_total
    # set the source
    skeys = ['SP2', 'TEMPLATE2', 'RECON_ABSO','AMPS_ABSOL_TOTAL']
    loc.set_sources(skeys, func_name)
    # return loc
    return loc


def calc_molecular_absorption(p, loc):

    # get constants from p
    limit = p['TELLU_FIT_LOG_LIMIT']
    # get data from loc
    recon_abso = loc['RECON_ABSO']
    tapas_all_species = loc['TAPAS_ALL_SPECIES']

    # log data
    log_recon_abso = np.log(recon_abso)
    with warnings.catch_warnings(record=True) as w:
        log_tapas_abso = np.log(tapas_all_species[1:, :])

    # get good pixels
    keep = np.min(log_tapas_abso, axis=0) > limit
    with warnings.catch_warnings(record=True) as w:
        keep &= log_recon_abso > limit
    keep &= np.isfinite(recon_abso)

    # get keep arrays
    klog_recon_abso = log_recon_abso[keep]
    klog_tapas_abso = log_tapas_abso[:, keep]

    # work out amplitudes and recon
    amps, recon = lin_mini(klog_recon_abso, klog_tapas_abso)

    # load amplitudes into loc
    for it, molecule in enumerate(p['TELLU_ABSORBERS'][1:]):
        # get molecule keyword store and key
        molkey = '{0}_{1}'.format(p['KW_TELLU_ABSO'][0], molecule.upper())
        # load into loc
        loc[molkey] = amps[it]
    # return loc
    return loc


def check_blacklist(objname):
    """
    Check whether file is blacklisted

    :param objname: str, the blacklisted object name (to check against list of
                    blacklisted object names)

    :return:
    """
    # get blacklisted files
    blacklisted_objects = get_blacklist()

    # set check to False
    check = False
    # loop around blacklisted objects
    for blacklisted_object in blacklisted_objects:
        # if objname in blacklisted_objects objname is black listed
        if blacklisted_object.upper() == objname.upper():
            check = True
    # return check
    return check


def get_blacklist():
    # get SpirouDRS data folder
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.DATA_CONSTANT_DIR()
    datadir = spirouConfig.GetAbsFolderPath(package, relfolder)
    # construct the path for the control file
    blacklistfilename = spirouConfig.Constants.TELLU_DATABASE_BLACKLIST_FILE()
    blacklistfile = os.path.join(datadir, blacklistfilename)
    # load control file
    blacklist = spirouConfig.GetTxt(blacklistfile, comments='#', delimiter=' ')
    # return control
    return blacklist


# TODO: Needs better commenting
def lin_mini(vector, sample):
    return spirouMath.linear_minimization(vector, sample)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================

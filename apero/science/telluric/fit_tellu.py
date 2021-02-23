#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-07-2020-07-15 17:55

@author: cook
"""
import numpy as np
import os
import warnings

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_startup
from apero.io import drs_fits
from apero.io import drs_path
from apero.io import drs_table
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science import extract
from apero.science.telluric import gen_tellu


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.fit_tellu.py'
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


# =============================================================================
# General functions
# =============================================================================
def gen_abso_pca_calc(params, recipe, image, transfiles, fiber, mprops,
                      tpreprops, **kwargs):
    func_name = __NAME__ + '.gen_abso_pca_calc()'
    # ----------------------------------------------------------------------
    # get constants from params/kwargs
    npc = pcheck(params, 'FTELLU_NUM_PRINCIPLE_COMP', 'npc', kwargs, func_name)
    add_deriv_pc = pcheck(params, 'FTELLU_ADD_DERIV_PC', 'add_deriv_pc',
                          kwargs, func_name)
    fit_deriv_pc = pcheck(params, 'FTELLU_FIT_DERIV_PC', 'fit_deriv_pc',
                          kwargs, func_name)
    thres_transfit_low = pcheck(params, 'MKTELLU_THRES_TRANSFIT',
                                'thres_transfit_low', kwargs, func_name)
    thres_transfit_upper = pcheck(params, 'MKTELLU_TRANS_FIT_UPPER_BAD',
                                  'thres_transfit_upper', kwargs, func_name)
    num_trans = pcheck(params, 'FTELLU_NUM_TRANS', 'num_trans', kwargs,
                       func_name)
    # ------------------------------------------------------------------
    # get the transmission map key
    # ----------------------------------------------------------------------
    out_trans = drs_startup.get_file_definition('TELLU_TRANS',
                                                params['INSTRUMENT'],
                                                kind='red', fiber=fiber)
    # get key
    trans_key = out_trans.get_dbkey() + '[{0}]'.format(fiber)
    # ----------------------------------------------------------------------
    # check that we have enough trans files for pca calculation (must be greater
    #     than number of principle components
    # ----------------------------------------------------------------------
    if len(transfiles) <= npc:
        # log and raise error: not enough tranmission maps to run pca analysis
        wargs = [trans_key, len(transfiles), npc, 'FTELLU_NUM_PRINCIPLE_COMP',
                 func_name]
        WLOG(params, 'error', textentry('09-019-00003', args=wargs))
    # ----------------------------------------------------------------------
    # check whether we can use pre-saved absorption map and create it by
    #     loading trans files if pre-saved abso map does not exist
    # ----------------------------------------------------------------------
    # get most recent file time
    recent_filetime = drs_path.get_most_recent(transfiles)
    # get new instances of ABSO_NPY files
    abso_npy = recipe.outputs['ABSO_NPY'].newcopy(params=params, fiber=fiber)
    abso1_npy = recipe.outputs['ABSO1_NPY'].newcopy(params=params, fiber=fiber)
    # construct the filename from file instance
    abso_npy_filename = 'tellu_save_{0}.npy'.format(recent_filetime)
    abso_npy.construct_filename(filename=abso_npy_filename,
                                path=params['DRS_TELLU_DB'])
    abso1_npy_filename = 'tellu_save1_{0}.npy'.format(recent_filetime)
    abso1_npy.construct_filename(filename=abso1_npy_filename,
                                path=params['DRS_TELLU_DB'])
    # noinspection PyBroadException
    try:
        # try loading from file
        abso = drs_path.numpy_load(abso_npy.filename)
        abso1 = drs_path.numpy_load(abso1_npy.filename)
        # log that we have loaded abso from file
        wargs = [abso_npy.filename]
        WLOG(params, '', textentry('40-019-00012', args=wargs))
        # set abso source
        abso_source = '[file] ' + abso_npy.basename
        transfiles_used = list(transfiles)
    except Exception as e:
        # debug print out: cannot load abso file
        dargs = [abso_npy, type(e), e]
        WLOG(params, 'debug', textentry('90-019-00001', args=dargs))
        # set up storage for the absorption
        abso = np.zeros([len(transfiles), np.product(image.shape)])
        abso1 = np.zeros([len(transfiles), 2])
        # storage for transfile used
        transfiles_used = []
        # load all the trans files
        for it, filename in enumerate(transfiles):
            # load trans image
            tout = drs_fits.readfits(params, filename, gethdr=True)
            transimage, transhdr = tout
            # test whether whole transimage is NaNs
            if np.sum(np.isnan(transimage)) == np.product(transimage):
                # log that we are removing a trans file
                wargs = [transfiles[it]]
                WLOG(params, '', textentry('40-019-00014', args=wargs))
            # make sure we have required header key for expo_water
            elif params['KW_TELLUP_EXPO_WATER'][0] not in transhdr:
                wargs = [params['KW_TELLUP_EXPO_WATER'][0], transfiles[it]]
                WLOG(params, '', textentry('40-019-00050', args=wargs))
            # make sure we have required header key for expo_others
            elif params['KW_TELLUP_EXPO_OTHERS'][0] not in transhdr:
                wargs = [params['KW_TELLUP_EXPO_OTHERS'][0], transfiles[it]]
                WLOG(params, '', textentry('40-019-00050', args=wargs))
            else:
                # push data into abso array
                abso[it, :] = transimage.reshape(np.product(image.shape))
                # get header keys
                abso1[it, 0] = transhdr[params['KW_TELLUP_EXPO_WATER'][0]]
                abso1[it, 1] = transhdr[params['KW_TELLUP_EXPO_OTHERS'][0]]
                # add to the trans files used list
                transfiles_used.append(filename)
        # set abso source
        abso_source = '[database] trans_file'
        # log that we are saving the abso to file
        WLOG(params, '', textentry('40-019-00013', args=[abso_npy.filename]))
        # remove all other abso npy files
        _remove_absonpy_files(params, params['DRS_TELLU_DB'], 'tellu_save_')
        _remove_absonpy_files(params, params['DRS_TELLU_DB'], 'tellu_save1_')
        # write to npy file
        abso_npy.data = abso
        abso_npy.write_npy(kind=recipe.outputtype, runstring=recipe.runstring)
        abso1_npy.data = abso1
        abso1_npy.write_npy(kind=recipe.outputtype, runstring=recipe.runstring)
    # ----------------------------------------------------------------------
    # use abso1 (water/others exponent) to create a mask for abso
    # ----------------------------------------------------------------------
    # deal with number of trans file less that num_trans required
    if len(list(transfiles)) < num_trans:
        num_trans = len(list(transfiles))
    # extract the expo water/others from abso1
    expo_water_tellu = abso1[:, 0]
    expo_others_tellu = abso1[:, 1]
    # get differences between trans files and current file
    water_diff = tpreprops['EXPO_WATER'] - expo_water_tellu
    others_diff = tpreprops['EXPO_OTHERS'] - expo_others_tellu
    # combine differences
    rad_expo = np.sqrt(water_diff ** 2 + others_diff ** 2)
    # make mask
    radmask = rad_expo <= rad_expo[np.argsort(rad_expo)[num_trans - 1]]
    # ----------------------------------------------------------------------
    # mask the abso
    abso = abso[radmask]
    # mask the used files and expo arrays
    transfiles_used = np.array(transfiles_used)[radmask]
    expo_water_tellu = expo_water_tellu[radmask]
    expo_others_tellu = expo_others_tellu[radmask]
    # ----------------------------------------------------------------------
    # log the absorption cube
    # ----------------------------------------------------------------------
    with warnings.catch_warnings(record=True) as _:
        log_abso = np.log(abso)
    # ----------------------------------------------------------------------
    # Locate valid pixels for PCA
    # ----------------------------------------------------------------------
    # determining the pixels relevant for PCA construction
    keep = np.isfinite(np.sum(abso, axis=0))
    with warnings.catch_warnings(record=True) as _:
        keep &= (np.min(abso, axis=0) > thres_transfit_low)
        keep &= (np.max(abso, axis=0) < thres_transfit_upper)

    # log fraction of valid (non NaN) pixels
    fraction = mp.nansum(keep) / len(keep)
    WLOG(params, '', textentry('40-019-00015', args=[fraction]))
    # log fraction of valid pixels > 1 - (1/e)
    with warnings.catch_warnings(record=True) as _:
        keep &= mp.nanmin(log_abso, axis=0) > -1
    fraction = mp.nansum(keep) / len(keep)
    WLOG(params, '', textentry('40-019-00016', args=[fraction]))
    # ----------------------------------------------------------------------
    # Perform PCA analysis on the log of the telluric absorption map
    # ----------------------------------------------------------------------
    # get eigen values
    eig_u, eig_s, eig_vt = np.linalg.svd(log_abso[:, keep], full_matrices=False)
    # if we are adding the derivatives to the pc need extra components
    if add_deriv_pc:
        # the npc+1 term will be the derivative of the first PC
        # the npc+2 term will be the broadening factor the first PC
        pc = np.zeros([np.product(image.shape), npc + 2])
    else:
        # create pc image
        pc = np.zeros([np.product(image.shape), npc])
    # fill pc image
    with warnings.catch_warnings(record=True) as _:
        for it in range(npc):
            for jt in range(log_abso.shape[0]):
                pc[:, it] += eig_u[jt, it] * log_abso[jt, :]
    # if we are adding the derivatives add them now
    if add_deriv_pc:
        # first extra is the first derivative
        pc[:, npc] = np.gradient(pc[:, 0])
        # second extra is the second derivative
        pc[:, npc + 1] = np.gradient(np.gradient(pc[:, 0]))
        # number of components is two longer now
        npc += 2
    # if we are fitting the derivative change the fit parameter
    if fit_deriv_pc:
        fit_pc = np.gradient(pc, axis=0)
    # else we are fitting the principle components themselves
    else:
        fit_pc = np.array(pc)
    # ----------------------------------------------------------------------
    # pca components plot (in loop)
    recipe.plot('FTELLU_PCA_COMP1', image=image, wavemap=mprops['WAVEMAP'],
                pc=pc, add_deriv_pc=add_deriv_pc, npc=npc, order=None)
    # pca components plot (single order)
    recipe.plot('FTELLU_PCA_COMP2', image=image, wavemap=mprops['WAVEMAP'],
                pc=pc, add_deriv_pc=add_deriv_pc, npc=npc,
                order=params['FTELLU_SPLOT_ORDER'])
    # ----------------------------------------------------------------------
    # set up properties
    # ----------------------------------------------------------------------
    props = ParamDict()
    props['ABSO'] = abso
    props['LOG_ABSO'] = log_abso
    props['PC'] = pc
    props['NPC'] = npc
    props['NTRANS'] = num_trans
    props['FIT_PC'] = fit_pc
    props['ADD_DERIV_PC'] = add_deriv_pc
    props['FIT_DERIV_PC'] = fit_deriv_pc
    props['ABSO_SOURCE'] = abso_source
    props['TRANS_FILE_USED'] = transfiles_used
    props['TRANS_FILE_EH2O'] = expo_water_tellu
    props['TRANS_FILE_EOTR'] = expo_others_tellu
    # set the source
    keys = ['ABSO', 'LOG_ABSO', 'PC', 'NPC', 'NTRANS', 'FIT_PC',
            'TRANS_FILE_USED', 'ADD_DERIV_PC', 'FIT_DERIV_PC', 'ABSO_SOURCE',
            'TRANS_FILE_EH2O', 'TRANS_FILE_EOTR']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return props
    return props


def shift_all_to_frame(params, recipe, image, template, bprops, mprops, wprops,
                       pca_props, tapas_props, **kwargs):
    func_name = __NAME__ + '.shift_all_to_frame()'
    # ------------------------------------------------------------------
    # get constants from params/kwargs
    # ------------------------------------------------------------------
    fit_keep_num = pcheck(params, 'FTELLU_FIT_KEEP_NUM', 'fit_keep_num',
                          kwargs, func_name)
    # ------------------------------------------------------------------
    # get data from property dictionaries
    # ------------------------------------------------------------------
    # Get the Barycentric correction from berv props
    dv = bprops['USE_BERV']
    # deal with bad berv (nan or None)
    if dv in [np.nan, None] or not isinstance(dv, (int, float)):
        eargs = [dv, func_name]
        WLOG(params, 'error', textentry('09-016-00004', args=eargs))
    # Get the master wavemap from master wave props
    masterwavemap = mprops['WAVEMAP']
    masterwavefile = os.path.basename(mprops['WAVEFILE'])
    # Get the current wavemap from wave props
    wavemap = wprops['WAVEMAP']
    wavefile = os.path.basename(wprops['WAVEFILE'])
    # get the pca props
    npc = pca_props['NPC']
    pc = pca_props['PC']
    fit_pc = pca_props['FIT_PC']
    # ge the tapas props
    tapas_all_species = tapas_props['TAPAS_ALL_SPECIES']
    # ------------------------------------------------------------------
    # copy shifted parameters
    pc2 = np.array(pc)
    fit_pc2 = np.array(fit_pc)
    tapas_all_species2 = np.array(tapas_all_species)
    # ------------------------------------------------------------------
    # Interpolate at shifted wavelengths (if we have a template)
    # ------------------------------------------------------------------
    if template is not None:
        # Log that we are shifting the template
        WLOG(params, '', textentry('40-019-00017'))
        # set up storage for template
        template2 = np.zeros(np.product(image.shape))
        ydim, xdim = image.shape
        # loop around orders
        for order_num in range(ydim):
            # find good (not NaN) pixels
            keep = np.isfinite(template[order_num, :])
            # if we have enough values spline them
            if mp.nansum(keep) > fit_keep_num:
                # define keep wave
                keepwave = masterwavemap[order_num, keep]
                # define keep temp
                keeptemp = template[order_num, keep]
                # calculate interpolation for keep temp at keep wave
                spline = mp.iuv_spline(keepwave, keeptemp, ext=3)
                # interpolate at shifted values
                dvshift = mp.relativistic_waveshift(dv, units='km/s')
                waveshift = masterwavemap[order_num, :] * dvshift
                # interpolate at shifted wavelength
                start = order_num * xdim
                end = order_num * xdim + xdim
                template2[start:end] = spline(waveshift)

        # ------------------------------------------------------------------
        # Shift the template to correct wave frame
        # ------------------------------------------------------------------
        # log the shifting of PCA components
        wargs = [masterwavefile, wavefile]
        WLOG(params, '', textentry('40-019-00021', args=wargs))
        # shift template
        shift_temp = gen_tellu.wave_to_wave(params, template2, masterwavemap,
                                            wavemap, reshape=True)
        template2 = shift_temp.reshape(template2.shape)

        # debug plot - reconstructed spline (in loop)
        recipe.plot('FTELLU_RECON_SPLINE1', image=image, wavemap=wavemap,
                    template=template2, order=None)
        # debug plot - reconstructed spline (selected order)
        recipe.plot('FTELLU_RECON_SPLINE2', image=image, wavemap=wavemap,
                    template=template2, order=params['FTELLU_SPLOT_ORDER'])

    else:
        template2 = None
    # ------------------------------------------------------------------
    # Shift the pca components to correct wave frame
    # ------------------------------------------------------------------
    # log the shifting of PCA components
    wargs = [masterwavefile, wavefile]
    WLOG(params, '', textentry('40-019-00018', args=wargs))
    # shift pca components (one by one)
    for comp in range(npc):
        shift_pc = gen_tellu.wave_to_wave(params, pc2[:, comp], masterwavemap,
                                          wavemap, reshape=True)
        pc2[:, comp] = shift_pc.reshape(pc2[:, comp].shape)

        shift_fpc = gen_tellu.wave_to_wave(params, fit_pc2[:, comp],
                                           masterwavemap, wavemap, reshape=True)
        fit_pc2[:, comp] = shift_fpc.reshape(fit_pc2[:, comp].shape)
    # ------------------------------------------------------------------
    # Shift the pca components to correct wave frame
    # ------------------------------------------------------------------
    # log the shifting of the tapas spectrum
    wargs = [masterwavefile, wavefile]
    WLOG(params, '', textentry('40-019-00019', args=wargs))
    # shift tapas species
    for row in range(len(tapas_all_species2)):
        stapas = gen_tellu.wave_to_wave(params, tapas_all_species[row],
                                        masterwavemap, wavemap, reshape=True)
        tapas_all_species2[row] = stapas.reshape(tapas_all_species[row].shape)

    # water is the second column
    tapas_water2 = tapas_all_species2[1, :]
    # other is defined as the product of the other columns
    tapas_other2 = np.prod(tapas_all_species2[2:, :], axis=0)
    # ------------------------------------------------------------------
    # Shift comparison plot
    # ------------------------------------------------------------------
    # Debug plot to test shifting (in loop)
    recipe.plot('FTELLU_WAVE_SHIFT1', image=image, tapas0=tapas_all_species,
                tapas1=tapas_all_species2, pc0=pc, pc1=pc2, order=None)
    # Debug plot to test shifting (single order)
    recipe.plot('FTELLU_WAVE_SHIFT2', image=image, tapas0=tapas_all_species,
                tapas1=tapas_all_species2, pc0=pc, pc1=pc2,
                order=params['FTELLU_SPLOT_ORDER'])
    # ------------------------------------------------------------------
    # Save shifted props
    # ------------------------------------------------------------------
    props = ParamDict()
    props['TEMPLATE2'] = template2
    props['PC2'] = pc2
    props['FIT_PC2'] = fit_pc2
    props['TAPAS_ALL_SPECIES2'] = tapas_all_species2
    props['TAPAS_WATER2'] = tapas_water2
    props['TAPAS_OTHER2'] = tapas_other2
    props['FIT_KEEP_NUM'] = fit_keep_num
    # set sources
    keys = ['TEMPLATE2', 'PC2', 'FIT_PC2', 'TAPAS_ALL_SPECIES2', 'FIT_KEEP_NUM']
    props.set_sources(keys, func_name)
    # return props
    return props


def calc_recon_and_correct(params, recipe, image, wprops, pca_props, sprops,
                           nprops, tpreprops, **kwargs):
    func_name = __NAME__ + '.calc_recon_and_correct()'
    # ------------------------------------------------------------------
    # get constants from params/kwargs
    # ------------------------------------------------------------------
    fit_min_trans = pcheck(params, 'FTELLU_FIT_MIN_TRANS', 'fit_min_trans',
                           kwargs, func_name)
    lambda_min = pcheck(params, 'FTELLU_LAMBDA_MIN', 'lambda_min', kwargs,
                        func_name)
    lambda_max = pcheck(params, 'FTELLU_LAMBDA_MAX', 'lambda_max', kwargs,
                        func_name)
    kernel_vsini = pcheck(params, 'FTELLU_KERNEL_VSINI', 'kernel_vsini',
                          kwargs, func_name)
    image_pixel_size = pcheck(params, 'IMAGE_PIXEL_SIZE', 'image_pixel_size',
                              kwargs, func_name)
    fit_iterations = pcheck(params, 'FTELLU_FIT_ITERS', 'fit_iterations',
                            kwargs, func_name)
    fit_deriv_pc = pcheck(params, 'FTELLU_FIT_DERIV_PC', 'fit_deriv_pc',
                          kwargs, func_name)
    recon_limit = pcheck(params, 'FTELLU_FIT_RECON_LIMIT', 'recon_limit',
                         kwargs, func_name)
    tellu_absorbers = pcheck(params, 'TELLU_ABSORBERS', 'absorbers', kwargs,
                             func_name, mapf='list', dtype=str)
    thres_transfit_low = pcheck(params, 'MKTELLU_THRES_TRANSFIT',
                                'thres_transfit_low', kwargs, func_name)
    thres_transfit_upper = pcheck(params, 'MKTELLU_TRANS_FIT_UPPER_BAD',
                                  'thres_transfit_upper', kwargs, func_name)
    # ------------------------------------------------------------------
    # get data from property dictionaries
    # ------------------------------------------------------------------
    # get the wave map
    wavemap = wprops['WAVEMAP']
    # get the pca props
    npc = pca_props['NPC']
    # ge the blaze and normalized blaze
    blaze = nprops['BLAZE']
    nblaze = nprops['NBLAZE']
    # get the shifted props
    tapas_all_species2 = sprops['TAPAS_ALL_SPECIES2']
    pc2 = sprops['PC2']
    fit_pc2 = sprops['FIT_PC2']
    template2 = sprops['TEMPLATE2']
    # set a flag to know we didn't start with a template
    if template2 is None:
        no_template_flag = True
    else:
        no_template_flag = False
    # ----------------------------------------------------------------------
    # get image dimensions
    nbo, nbpix = image.shape
    # flatten image
    sp2 = image.ravel()
    # flatten wavemap
    fwavemap = wavemap.ravel()
    # ----------------------------------------------------------------------
    # set storage
    # ----------------------------------------------------------------------
    recon_abso = np.ones(np.product(image.shape))
    amps_abso_total = np.zeros(npc)
    # ----------------------------------------------------------------------
    # construct keep mask
    # ----------------------------------------------------------------------
    # find pc where all components are finite
    keep = np.sum(np.isnan(pc2), axis=1) == 0
    # also require wavelength constraints
    keep &= (fwavemap > lambda_min)
    keep &= (fwavemap < lambda_max)
    # ----------------------------------------------------------------------
    # construct convolution kernel
    # ----------------------------------------------------------------------
    # gaussian ew for vinsi km/s
    ewid = kernel_vsini / image_pixel_size / mp.fwhm()
    # set up the kernel exponent
    xxarr = np.arange(ewid * 6) - ewid * 3
    # kernel is the a gaussian
    kernel = np.exp(-.5 * (xxarr / ewid) ** 2)
    # normalise kernel
    kernel /= mp.nansum(kernel)
    # ----------------------------------------------------------------------
    # loop around a number of times
    for ite in range(fit_iterations):
        # log progress
        wargs = [ite + 1, fit_iterations]
        WLOG(params, '', textentry('40-019-00020', args=wargs))
        # ------------------------------------------------------------------
        # if we don't have a template construct one
        # ------------------------------------------------------------------
        if no_template_flag:
            # define template2 to fill
            template2 = np.zeros(np.product(image.shape))
            # loop around orders
            for order_num in range(nbo):
                # get start and end points
                start = order_num * nbpix
                end = order_num * nbpix + nbpix
                # get good transmission spectrum
                spgood = image[order_num, :]
                recongood = recon_abso[start:end]
                # convolve spectrum
                ckwargs = dict(v=kernel, mode='same')
                sp2b = np.convolve(spgood / recongood, **ckwargs)
                # convolved spectrum into template2
                template2[start:end] = sp2b
        # ------------------------------------------------------------------
        # get residual spectrum
        # ------------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            resspec = (sp2 / template2) / recon_abso
        # ------------------------------------------------------------------
        # if we were supplied a template convolve the residual spectrum
        #      with a kernel
        # ------------------------------------------------------------------
        if not no_template_flag:
            # loop around orders
            for order_num in range(nbo):
                # get start and end points
                start = order_num * nbpix
                end = order_num * nbpix + nbpix
                # get good transmission spectrum
                resspecgood = resspec[start:end]
                recongood = recon_abso[start:end]
                # convolve spectrum
                ckwargs = dict(v=kernel, mode='same')
                with warnings.catch_warnings(record=True) as _:
                    sp2b = np.convolve(resspecgood / recongood, **ckwargs)
                # convolved spectrum into dd
                resspec[start:end] = resspec[start:end] / sp2b
        # ------------------------------------------------------------------
        # get the logarithm of the residual spectrum
        # ------------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            log_resspec = np.log(resspec)
        # ------------------------------------------------------------------
        # subtract off the median from each order
        # ------------------------------------------------------------------
        for order_num in range(nbo):
            # get start and end points
            start = order_num * nbpix
            end = order_num * nbpix + nbpix
            # skip if whole order is NaNs
            if mp.nansum(np.isfinite(log_resspec[start:end])) == 0:
                continue
            # get median
            log_resspec_med = mp.nanmedian(log_resspec[start:end])
            # subtract of median
            log_resspec[start:end] = log_resspec[start:end] - log_resspec_med
        # ------------------------------------------------------------------
        # set up the fit parameter
        # ------------------------------------------------------------------
        if fit_deriv_pc:
            fit_dd = np.gradient(log_resspec)
        else:
            fit_dd = np.array(log_resspec)
        # ------------------------------------------------------------------
        # identify good pixels to keep
        # ------------------------------------------------------------------
        keep &= np.isfinite(fit_dd)
        keep &= mp.nansum(np.isfinite(fit_pc2), axis=1) == npc

        # TODO: added a constraint on the max deviation in fit_dd
        #     this prevents points that are very deviant to be include
        #     in principle, there should be NO very deviant point as
        #     we already have a cut on the abso from TAPAS, but this
        #     is used as a sigma-clipping. The cut is expressed in log
        #     abso, so a value of 1 is equivalent to a 2.7x difference
        #     in residual.
        sigma = 1.0  # mp.nanmedian(np.abs(fit_dd))
        with warnings.catch_warnings(record=True) as _:
            keep &= (np.abs(fit_dd) < sigma)

        # log number of kept pixels
        wargs = [mp.nansum(keep)]
        WLOG(params, '', textentry('40-019-00022', args=wargs))
        # ------------------------------------------------------------------
        # calculate amplitudes and reconstructed spectrum
        # ------------------------------------------------------------------
        amps, recon = mp.linear_minimization(fit_dd[keep], fit_pc2[keep, :])
        # set up storage for absorption array 2
        abso2 = np.zeros(len(resspec))
        with warnings.catch_warnings(record=True) as _:
            for ipc in range(len(amps)):
                amps_abso_total[ipc] += amps[ipc]
                abso2 += pc2[:, ipc] * amps[ipc]
            recon_abso *= np.exp(abso2)
    # ------------------------------------------------------------------
    # reconstructed absorption plot
    # ------------------------------------------------------------------
    # plot recon abso in loop
    recipe.plot('FTELLU_RECON_ABSO1', params=params, image=image, order=None,
                wavemap=wavemap, sp2=sp2, template=template2, recon=recon_abso)

    # plot recon abso (single order)
    recipe.plot('FTELLU_RECON_ABSO2', params=params, image=image,
                wavemap=wavemap, sp2=sp2, template=template2, recon=recon_abso,
                order=params['FTELLU_SPLOT_ORDER'])
    # plot recon abso (summary plot)
    recipe.plot('SUM_FTELLU_RECON_ABSO', params=params, image=image,
                wavemap=wavemap, sp2=sp2, template=template2, recon=recon_abso,
                orders=params.listp('FTELLU_PLOT_ORDER_NUMS', dtype=int))

    # ------------------------------------------------------------------
    # copy the residual recon for use below
    recon_abso_res = np.array(recon_abso)
    # convert the recon back into a true transmission
    recon_abso = recon_abso * tpreprops['ABSO_E2DS'].ravel()

    # ------------------------------------------------------------------
    # calculate molecular absorption
    # ------------------------------------------------------------------
    # log data
    log_recon_abso = np.log(recon_abso)
    with warnings.catch_warnings(record=True) as _:
        log_tapas_abso = np.log(tapas_all_species2[1:, :])
    # get good pixels
    with warnings.catch_warnings(record=True) as _:
        keep = mp.nanmin(log_tapas_abso, axis=0) > recon_limit
        keep &= log_recon_abso > recon_limit
    keep &= np.isfinite(recon_abso)
    # get keep arrays
    klog_recon_abso = log_recon_abso[keep]
    klog_tapas_abso = log_tapas_abso[:, keep]
    # work out amplitudes and recon
    amps1, recon1 = mp.linear_minimization(klog_recon_abso, klog_tapas_abso)
    # load amplitudes into loc
    water_it, others_it = [], []
    molecule_data = dict()
    for it, molecule in enumerate(tellu_absorbers[1:]):
        # load into loc
        molecule_data[molecule.upper()] = amps1[it]
        # record water col
        if molecule.upper() == 'H2O':
            water_it.append(it)
        else:
            others_it.append(it)
    # set up second set of vectors (water + combined others)
    klog_tapas_abso2 = np.zeros_like(klog_tapas_abso[:2])
    # put water straight in
    klog_tapas_abso2[0] = klog_tapas_abso[np.array(water_it)]
    # combine others
    klog_tapas_abso2[1] = np.sum(klog_tapas_abso[np.array(others_it)], axis=0)
    # work out amplitudes and recon
    amps2, recon2 = mp.linear_minimization(klog_recon_abso, klog_tapas_abso2)

    # ------------------------------------------------------------------
    # remove all bad tranmission
    # ------------------------------------------------------------------
    with warnings.catch_warnings(record=True) as _:
        badmask = recon_abso < thres_transfit_low
        badmask |= recon_abso > thres_transfit_upper
    # set bad values in sp2 to NaN
    sp2[badmask] = np.nan

    # ------------------------------------------------------------------
    # correct spectrum
    # ------------------------------------------------------------------
    # divide spectrum by reconstructed absorption
    sp_out = sp2 / recon_abso_res
    sp_out = sp_out.reshape(image.shape)
    # multiple by the normalised blaze
    sp_out = sp_out * nblaze
    # need to set up a recon_abso that is blaze corrected and the correct shape
    recon_abso2 = recon_abso.reshape(image.shape)
    recon_abso2 = recon_abso2 * blaze

    # ------------------------------------------------------------------
    # save to props
    # ------------------------------------------------------------------
    props = ParamDict()
    props['TEMPLATE2'] = template2
    props['CORRECTED_SP'] = sp_out
    props['RECON_ABSO'] = recon_abso.reshape(image.shape)
    props['RECON_ABSO_SP'] = recon_abso2
    props['AMPS_ABSO_TOTAL'] = amps_abso_total
    props['TAU_MOLECULES'] = molecule_data
    props['TAU_H2O'] = amps2[0]
    props['TAU_REST'] = amps2[1]
    # set sources
    keys = ['TEMPLATE2', 'CORRECTED_SP', 'RECON_ABSO', 'RECON_ABSO_SP',
            'AMPS_ABSO_TOTAL', 'TAU_MOLECULES', 'TAU_H2O', 'TAU_REST']
    props.set_sources(keys, func_name)
    # add constants for reproducability
    props['FIT_MIN_TRANS'] = fit_min_trans
    props['LAMBDA_MIN'] = lambda_min
    props['LAMBDA_MAX'] = lambda_max
    props['KERNEL_VSINI'] = kernel_vsini
    props['IMAGE_PIXEL_SIZE'] = image_pixel_size
    props['FIT_ITERATIONS'] = fit_iterations
    props['FIT_DERIV_PC'] = fit_deriv_pc
    props['RECON_LIMIT'] = recon_limit
    props['TELLU_ABSORBERS'] = tellu_absorbers
    props['THRES_TRANSFIT'] = thres_transfit_low
    props['TRANS_FIT_UPPER_BAD'] = thres_transfit_upper
    # set sources
    keys = ['FIT_MIN_TRANS', 'LAMBDA_MIN', 'LAMBDA_MAX', 'KERNEL_VSINI',
            'IMAGE_PIXEL_SIZE', 'FIT_ITERATIONS',
            'FIT_DERIV_PC', 'RECON_LIMIT', 'TELLU_ABSORBERS']
    props.set_sources(keys, func_name)
    # return props
    return props


def correct_other_science(params, recipe, fiber, infile, cprops, rawfiles,
                          combine, pca_props, sprops, qc_params,
                          template_props, tpreprops, database=None):
    # get the header
    header = infile.get_header()
    # ------------------------------------------------------------------
    # load wavelength solution for this fiber
    wprops = wave.get_wavesolution(params, recipe, header, fiber=fiber,
                                   infile=infile, database=database)
    # ------------------------------------------------------------------
    # Construct fiber file name and read data
    # ------------------------------------------------------------------
    # locate fiber spectrum
    fiber_infile = infile.newcopy(params=params)
    fiber_infile.reconstruct_filename(outext=fiber_infile.filetype,
                                      fiber=fiber)
    # read fiber file
    fiber_infile.read_file()
    # get image
    image = fiber_infile.get_data()
    # ------------------------------------------------------------------
    # Normalize image by peak blaze
    # ------------------------------------------------------------------
    # load the blaze file for this fiber
    blaze_file, blaze = flat_blaze.get_blaze(params, header, fiber)
    # fake nprop dict
    nprops = dict()
    nprops['BLAZE_FILE'] = blaze_file
    # ------------------------------------------------------------------
    # Correct spectrum with simple division
    # ------------------------------------------------------------------
    # corrected data is just input data / recon
    scorr = image * blaze / cprops['RECON_ABSO_SP']
    # ------------------------------------------------------------------
    # Create 1d spectra (s1d) of the corrected E2DS file
    # ------------------------------------------------------------------
    scargs = [wprops['WAVEMAP'], scorr,blaze]
    scwprops = extract.e2ds_to_s1d(params, recipe, *scargs, wgrid='wave',
                                   fiber=fiber, kind='corrected sp')
    scvprops = extract.e2ds_to_s1d(params, recipe, *scargs,
                                   wgrid='velocity', fiber=fiber,
                                   kind='corrected sp')
    # ------------------------------------------------------------------
    # Save corrected E2DS to file
    # ------------------------------------------------------------------
    fargs = [fiber_infile, rawfiles, fiber, combine, nprops, wprops,
             pca_props, sprops, cprops, qc_params, template_props, tpreprops]
    fkwargs = dict(CORRECTED_SP=scorr)
    corrfile = fit_tellu_write_corrected(params, recipe, *fargs, **fkwargs)
    # ------------------------------------------------------------------
    # Save 1d corrected spectra to file
    # ------------------------------------------------------------------
    fsargs = [infile, corrfile, fiber, scwprops, scvprops]
    fit_tellu_write_corrected_s1d(params, recipe, *fsargs)


# =============================================================================
# QC and summary functions
# =============================================================================
def fit_tellu_quality_control(params, infile, tpreprops, **kwargs):
    func_name = __NAME__ + '.fit_tellu_quality_control()'
    # get parameters from params/kwargs
    snr_order = pcheck(params, 'FTELLU_QC_SNR_ORDER', 'snr_order', kwargs,
                       func_name)
    qc_snr_min = pcheck(params, 'FTELLU_QC_SNR_MIN', 'qc_snr_min', kwargs,
                        func_name)
    # set passed variable and fail message list
    fail_msg = []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
    # deal with tellu precleaning qc params - just add them correctly
    tqc_names, tqc_values, tqc_logic, tqc_pass = tpreprops['QC_PARAMS']
    # loop around all tqc
    for qc_it in range(len(tqc_names)):
        # if tqc_pass failed (zero) make fail message
        if tqc_pass[qc_it] == 0:
            fail_msg.append(tqc_logic[qc_it].lower())
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(tqc_values[qc_it])
        qc_names.append(tqc_names[qc_it])
        qc_logic.append(tqc_logic[qc_it])
    # ----------------------------------------------------------------------
    # get SNR for each order from header
    nbo, nbpix = infile.shape
    snr = infile.get_hkey_1d('KW_EXT_SNR', nbo, dtype=float)
    # check that SNR is high enough
    if snr[snr_order] < qc_snr_min:
        fargs = [snr_order, snr[snr_order], qc_snr_min]
        fail_msg.append(textentry('40-019-00007', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(snr[snr_order])
    qc_name_str = 'SNR[{0}]'.format(snr_order)
    qc_names.append(qc_name_str)
    qc_logic.append('{0} < {1:.2f}'.format(qc_name_str, qc_snr_min))

    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #     quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params, passed


def fit_tellu_summary(recipe, it, params, qc_params, pca_props, sprops,
                      cprops, fiber):
    # add qc params (fiber specific)
    recipe.plot.add_qc_params(qc_params, fiber=fiber)
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_FTELLU_NPC', value=pca_props['NPC'])
    recipe.plot.add_stat('KW_FTELLU_ADD_DPC',
                         value=pca_props['ADD_DERIV_PC'])
    recipe.plot.add_stat('KW_FTELLU_FIT_DPC',
                         value=pca_props['FIT_DERIV_PC'])
    recipe.plot.add_stat('KW_FTELLU_ABSO_SRC',
                         value=pca_props['ABSO_SOURCE'])
    recipe.plot.add_stat('KW_FTELLU_FIT_KEEP_NUM',
                         value=sprops['FIT_KEEP_NUM'])
    recipe.plot.add_stat('KW_FTELLU_FIT_MIN_TRANS',
                         value=cprops['FIT_MIN_TRANS'])
    recipe.plot.add_stat('KW_FTELLU_LAMBDA_MIN',
                         value=cprops['LAMBDA_MIN'])
    recipe.plot.add_stat('KW_FTELLU_LAMBDA_MAX',
                         value=cprops['LAMBDA_MAX'])
    recipe.plot.add_stat('KW_FTELLU_KERN_VSINI',
                         value=cprops['KERNEL_VSINI'])
    recipe.plot.add_stat('KW_FTELLU_IM_PX_SIZE',
                         value=cprops['IMAGE_PIXEL_SIZE'])
    recipe.plot.add_stat('KW_FTELLU_FIT_ITERS',
                         value=cprops['FIT_ITERATIONS'])
    recipe.plot.add_stat('KW_FTELLU_RECON_LIM',
                         value=cprops['RECON_LIMIT'])
    recipe.plot.add_stat('KW_MKTELL_THRES_TFIT',
                         value=cprops['THRES_TRANSFIT'])
    recipe.plot.add_stat('KW_MKTELL_TRANS_FIT_UPPER_BAD',
                         value=cprops['TRANS_FIT_UPPER_BAD'])
    # construct summary
    recipe.plot.summary_document(it)


# =============================================================================
# Write functions
# =============================================================================
def fit_tellu_write_corrected(params, recipe, infile, rawfiles, fiber, combine,
                              nprops, wprops, pca_props, sprops, cprops,
                              qc_params, template_props, tpreprops, **kwargs):
    func_name = __NAME__ + '.fit_tellu_write_corrected()'
    # get parameters from params
    abso_prefix_kws = pcheck(params, 'KW_FTELLU_ABSO_PREFIX', 'abso_prefix_kws',
                             kwargs, func_name)
    npc = pca_props['NPC']
    add_deriv_pc = pca_props['ADD_DERIV_PC']
    # get parameters from cprops
    sp_out = kwargs.get('CORRECTED_SP', cprops['CORRECTED_SP'])
    amps_abso_t = cprops['AMPS_ABSO_TOTAL']
    tau_molecules = cprops['TAU_MOLECULES']

    # ------------------------------------------------------------------
    # Set up fit_tellu trans table
    # ------------------------------------------------------------------
    columns = ['TRANS_FILE', 'EXPO_H2O', 'EXPO_OTHERS']
    values = [pca_props['TRANS_FILE_USED'],
              pca_props['TRANS_FILE_EH2O'],
              pca_props['TRANS_FILE_EOTR']]
    # construct table
    trans_table = drs_table.make_table(params, columns=columns, values=values)
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    corrfile = recipe.outputs['TELLU_OBJ'].newcopy(params=params, fiber=fiber)
    # construct the filename from file instance
    corrfile.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # copy keys from input file
    corrfile.copy_original_keys(infile)
    # add version
    corrfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    corrfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    corrfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    corrfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    corrfile.add_hkey('KW_OUTPUT', value=corrfile.name)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    corrfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='file')
    # add  calibration files used
    corrfile.add_hkey('KW_CDBBLAZE', value=nprops['BLAZE_FILE'])
    corrfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    # ----------------------------------------------------------------------
    # add qc parameters
    corrfile.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # add telluric constants used
    corrfile.add_hkey('KW_FTELLU_NPC', value=npc)
    corrfile.add_hkey('KW_FTELLU_ADD_DPC', value=add_deriv_pc)
    corrfile.add_hkey('KW_FTELLU_FIT_DPC', value=pca_props['FIT_DERIV_PC'])
    corrfile.add_hkey('KW_FTELLU_ABSO_SRC', value=pca_props['ABSO_SOURCE'])
    corrfile.add_hkey('KW_FTELLU_FIT_KEEP_NUM', value=sprops['FIT_KEEP_NUM'])
    corrfile.add_hkey('KW_FTELLU_FIT_MIN_TRANS', value=cprops['FIT_MIN_TRANS'])
    corrfile.add_hkey('KW_FTELLU_LAMBDA_MIN', value=cprops['LAMBDA_MIN'])
    corrfile.add_hkey('KW_FTELLU_LAMBDA_MAX', value=cprops['LAMBDA_MAX'])
    corrfile.add_hkey('KW_FTELLU_KERN_VSINI', value=cprops['KERNEL_VSINI'])
    corrfile.add_hkey('KW_FTELLU_IM_PX_SIZE', value=cprops['IMAGE_PIXEL_SIZE'])
    corrfile.add_hkey('KW_FTELLU_FIT_ITERS', value=cprops['FIT_ITERATIONS'])
    corrfile.add_hkey('KW_FTELLU_RECON_LIM', value=cprops['RECON_LIMIT'])
    corrfile.add_hkey('KW_MKTELL_THRES_TFIT', value=cprops['THRES_TRANSFIT'])
    corrfile.add_hkey('KW_MKTELL_TRANS_FIT_UPPER_BAD',
                      value=cprops['TRANS_FIT_UPPER_BAD'])
    # ----------------------------------------------------------------------
    # add tellu pre-clean keys
    corrfile.add_hkey('KW_TELLUP_EXPO_WATER', value=tpreprops['EXPO_WATER'])
    corrfile.add_hkey('KW_TELLUP_EXPO_OTHERS', value=tpreprops['EXPO_OTHERS'])
    corrfile.add_hkey('KW_TELLUP_DV_WATER', value=tpreprops['DV_WATER'])
    corrfile.add_hkey('KW_TELLUP_DV_OTHERS', value=tpreprops['DV_OTHERS'])
    corrfile.add_hkey('KW_TELLUP_DO_PRECLEAN',
                      value=tpreprops['TELLUP_DO_PRECLEANING'])
    corrfile.add_hkey('KW_TELLUP_DFLT_WATER',
                      value=tpreprops['TELLUP_D_WATER_ABSO'])
    corrfile.add_hkey('KW_TELLUP_CCF_SRANGE',
                      value=tpreprops['TELLUP_CCF_SCAN_RANGE'])
    corrfile.add_hkey('KW_TELLUP_CLEAN_OHLINES',
                      value=tpreprops['TELLUP_CLEAN_OH_LINES'])
    corrfile.add_hkey('KW_TELLUP_REMOVE_ORDS',
                      value=tpreprops['TELLUP_REMOVE_ORDS'], mapf='list')
    corrfile.add_hkey('KW_TELLUP_SNR_MIN_THRES',
                      value=tpreprops['TELLUP_SNR_MIN_THRES'])
    corrfile.add_hkey('KW_TELLUP_DEXPO_CONV_THRES',
                      value=tpreprops['TELLUP_DEXPO_CONV_THRES'])
    corrfile.add_hkey('KW_TELLUP_DEXPO_MAX_ITR',
                      value=tpreprops['TELLUP_DEXPO_MAX_ITR'])
    corrfile.add_hkey('KW_TELLUP_ABSOEXPO_KTHRES',
                      value=tpreprops['TELLUP_ABSO_EXPO_KTHRES'])
    corrfile.add_hkey('KW_TELLUP_WAVE_START',
                      value=tpreprops['TELLUP_WAVE_START'])
    corrfile.add_hkey('KW_TELLUP_WAVE_END',
                      value=tpreprops['TELLUP_WAVE_END'])
    corrfile.add_hkey('KW_TELLUP_DVGRID',
                      value=tpreprops['TELLUP_DVGRID'])
    corrfile.add_hkey('KW_TELLUP_ABSOEXPO_KWID',
                      value=tpreprops['TELLUP_ABSO_EXPO_KWID'])
    corrfile.add_hkey('KW_TELLUP_ABSOEXPO_KEXP',
                      value=tpreprops['TELLUP_ABSO_EXPO_KEXP'])
    corrfile.add_hkey('KW_TELLUP_TRANS_THRES',
                      value=tpreprops['TELLUP_TRANS_THRES'])
    corrfile.add_hkey('KW_TELLUP_TRANS_SIGL',
                      value=tpreprops['TELLUP_TRANS_SIGLIM'])
    corrfile.add_hkey('KW_TELLUP_FORCE_AIRMASS',
                      value=tpreprops['TELLUP_FORCE_AIRMASS'])
    corrfile.add_hkey('KW_TELLUP_OTHER_BOUNDS',
                      value=tpreprops['TELLUP_OTHER_BOUNDS'], mapf='list')
    corrfile.add_hkey('KW_TELLUP_WATER_BOUNDS',
                      value=tpreprops['TELLUP_WATER_BOUNDS'], mapf='list')
    # ----------------------------------------------------------------------
    # add template key (if we have template)
    if template_props['TEMP_FILE'] is None:
        corrfile.add_hkey('KW_FTELLU_TEMPLATE', value='None')
        corrfile.add_hkey('KW_FTELLU_TEMPNUM', value=0)
        corrfile.add_hkey('KW_FTELLU_TEMPHASH', value='None')
        corrfile.add_hkey('KW_FTELLU_TEMPTIME', value='None')
    else:
        corrfile.add_hkey('KW_FTELLU_TEMPLATE',
                          value=os.path.basename(template_props['TEMP_FILE']))
        corrfile.add_hkey('KW_FTELLU_TEMPNUM',
                          value=template_props['TEMP_NUM'])
        corrfile.add_hkey('KW_FTELLU_TEMPHASH',
                          value=template_props['TEMP_HASH'])
        corrfile.add_hkey('KW_FTELLU_TEMPTIME',
                          value=template_props['TEMP_TIME'])
    # ----------------------------------------------------------------------
    # add the amplitudes (and derivatives)
    if add_deriv_pc:
        values = amps_abso_t[:npc - 2]
        # add the standard keys
        corrfile.add_hkey_1d('KW_FTELLU_AMP_PC', values=values, dim1name='amp')
        # add the derivs
        corrfile.add_hkey('KW_FTELLU_DVTELL1', value=amps_abso_t[npc - 2])
        corrfile.add_hkey('KW_FTELLU_DVTELL2', value=amps_abso_t[npc - 1])
    # else just add the amp pc and blank for the dvtells
    else:
        # add the standard keys
        corrfile.add_hkey_1d('KW_FTELLU_AMP_PC', values=amps_abso_t,
                             dim1name='amp')
        # add the derivs (blank)
        corrfile.add_hkey('KW_FTELLU_DVTELL1', value='None')
        corrfile.add_hkey('KW_FTELLU_DVTELL2', value='None')
    # ----------------------------------------------------------------------
    # add the absorbance
    for molecule in tau_molecules:
        # construct molecule key
        molkey = '{0}_{1}'.format(abso_prefix_kws[0], molecule.upper())
        # construct keyword dict
        molkws = [molkey, 0.0, abso_prefix_kws[2].format(molecule)]
        # add to header
        corrfile.add_hkey(molkws, value=tau_molecules[molecule])
    # add the tau values
    corrfile.add_hkey('KW_FTELLU_TAU_H2O', value=cprops['TAU_H2O'])
    corrfile.add_hkey('KW_FTELLU_TAU_REST', value=cprops['TAU_REST'])
    # ----------------------------------------------------------------------
    # copy data
    corrfile.data = sp_out
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-019-00023', args=[corrfile.filename]))
    # define multi lists
    data_list = [trans_table]
    datatype_list = ['table']
    name_list = ['TRANS_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(drsfitsfile=corrfile)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write image to file
    corrfile.write_multi(data_list=data_list, name_list=name_list,
                         datatype_list=datatype_list,
                         kind=recipe.outputtype, runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(corrfile)
    # ------------------------------------------------------------------
    # return corrected e2ds file instance
    return corrfile


def fit_tellu_write_corrected_s1d(params, recipe, infile, corrfile, fiber,
                                  scwprops, scvprops):
    # ------------------------------------------------------------------
    # get new copy of the corrected s1d_w file
    sc1dwfile = recipe.outputs['SC1D_W_FILE'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    sc1dwfile.construct_filename(infile=infile)
    # copy header from corrected e2ds file
    sc1dwfile.copy_hdict(corrfile)
    # add output tag
    sc1dwfile.add_hkey('KW_OUTPUT', value=sc1dwfile.name)
    # add new header keys
    sc1dwfile = extract.add_s1d_keys(sc1dwfile, scwprops)
    # copy data
    sc1dwfile.data = scwprops['S1DTABLE']
    # must change the datatpye to 'table'
    sc1dwfile.datatype = 'table'
    # log that we are saving s1d table
    wargs = ['wave', sc1dwfile.filename]
    WLOG(params, '', textentry('40-019-00024', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(drsfitsfile=sc1dwfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    sc1dwfile.write_multi(data_list=data_list, name_list=name_list,
                          kind=recipe.outputtype,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(sc1dwfile)
    # ------------------------------------------------------------------
    # get new copy of the corrected s1d_v file
    sc1dvfile = recipe.outputs['SC1D_V_FILE'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    sc1dvfile.construct_filename(infile=infile)
    # copy header from corrected e2ds file
    sc1dvfile.copy_hdict(corrfile)
    # add output tag
    sc1dvfile.add_hkey('KW_OUTPUT', value=sc1dvfile.name)
    # add new header keys
    sc1dvfile = extract.add_s1d_keys(sc1dvfile, scvprops)
    # copy data
    sc1dvfile.data = scvprops['S1DTABLE']
    # must change the datatpye to 'table'
    sc1dvfile.datatype = 'table'
    # log that we are saving s1d table
    wargs = ['velocity', sc1dvfile.filename]
    WLOG(params, '', textentry('40-019-00024', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(drsfitsfile=sc1dvfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    sc1dvfile.write_multi(data_list=data_list, name_list=name_list,
                          kind=recipe.outputtype,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(sc1dvfile)


def fit_tellu_write_recon(params, recipe, infile, corrfile, fiber, cprops,
                          rcwprops, rcvprops):
    # ------------------------------------------------------------------
    # get new copy of the corrected s1d_w file
    reconfile = recipe.outputs['TELLU_RECON'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    reconfile.construct_filename(infile=infile)
    # copy header from corrected e2ds file
    reconfile.copy_hdict(corrfile)
    # add output tag
    reconfile.add_hkey('KW_OUTPUT', value=reconfile.name)
    # copy data
    reconfile.data = cprops['RECON_ABSO']
    # log that we are saving recon e2ds file
    WLOG(params, '', textentry('40-019-00025', args=[reconfile.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(drsfitsfile=reconfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    reconfile.write_multi(data_list=data_list, name_list=name_list,
                          kind=recipe.outputtype,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(reconfile)
    # ------------------------------------------------------------------
    # get new copy of the corrected s1d_w file
    rc1dwfile = recipe.outputs['RC1D_W_FILE'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    rc1dwfile.construct_filename(infile=infile)
    # copy header from corrected e2ds file
    rc1dwfile.copy_hdict(corrfile)
    # add output tag
    rc1dwfile.add_hkey('KW_OUTPUT', value=rc1dwfile.name)
    # add new header keys
    rc1dwfile = extract.add_s1d_keys(rc1dwfile, rcwprops)
    # copy data
    rc1dwfile.data = rcwprops['S1DTABLE']
    # must change the datatpye to 'table'
    rc1dwfile.datatype = 'table'
    # log that we are saving s1d table
    wargs = ['wave', rc1dwfile.filename]
    WLOG(params, '', textentry('40-019-00026', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(drsfitsfile=rc1dwfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    rc1dwfile.write_multi(data_list=data_list, name_list=name_list,
                          kind=recipe.outputtype,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(rc1dwfile)
    # ------------------------------------------------------------------
    # get new copy of the corrected s1d_v file
    rc1dvfile = recipe.outputs['RC1D_V_FILE'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    rc1dvfile.construct_filename(infile=infile)
    # copy header from corrected e2ds file
    rc1dvfile.copy_hdict(corrfile)
    # add output tag
    rc1dvfile.add_hkey('KW_OUTPUT', value=rc1dvfile.name)
    # add new header keys
    rc1dvfile = extract.add_s1d_keys(rc1dvfile, rcvprops)
    # copy data
    rc1dvfile.data = rcvprops['S1DTABLE']
    # must change the datatpye to 'table'
    rc1dvfile.datatype = 'table'
    # log that we are saving s1d table
    wargs = ['velocity', rc1dvfile.filename]
    WLOG(params, '', textentry('40-019-00026', args=wargs))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(drsfitsfile=rc1dvfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    rc1dvfile.write_multi(data_list=data_list, name_list=name_list,
                          kind=recipe.outputtype,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(rc1dvfile)
    # ------------------------------------------------------------------
    return reconfile


# =============================================================================
# Worker functions
# =============================================================================
def _remove_absonpy_files(params, path, prefix):
    # list files in path
    filelist = np.sort(os.listdir(path))
    # loop around files and decide whether to delete them or not
    for filename in filelist:
        # must be a .npy file
        if not filename.endswith('.npy'):
            continue
        # must start with prefix
        if filename.startswith(prefix):
            # create abspath
            abspath = os.path.join(path, filename)
            # debug log removal of other abso files
            WLOG(params, 'debug', textentry('90-019-00002', args=[abspath]))
            # remove file
            try:
                os.remove(abspath)
            except Exception as _:
                pass


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

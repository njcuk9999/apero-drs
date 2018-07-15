#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-13 05:18
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
import os
from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTelluric

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
SIG_FWHM = spirouCore.spirouMath.fwhm
# Get plotting functions
sPlt = spirouCore.sPlt
# get speed of light
# noinspection PyUnresolvedReferences
CONSTANT_C = constants.c.value


def interp_at_shifted_wavelengths(p, loc, thdr):
    func_name = __NAME__ + '.interp_at_shifted_wavelengths()'
    # Get the Barycentric correction from header
    dv, _, _ = spirouTelluric.GetBERV(p, thdr)
    # set up storage for template
    template2 = np.zeros_like(loc['DATA'])
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
    # debug plot
    if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1):
        # start interactive plot
        sPlt.start_interactive_session()
        # plot the transmission map plot
        sPlt.tellu_fit_tellu_spline_plot(p, loc, sp, template2)
        # end interactive session
        sPlt.end_interactive_session()
    # save to loc
    loc['TEMPLATE2'] = template2
    loc.set_source('TEMPLATE2', func_name)
    # return loc
    return loc


def make_template2(p, loc):

    # set up storage for template
    template2 = np.zeros_like(loc['DATA'])
    ydim, xdim = loc['DATA'].shape



# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p)
    # set up function name
    main_name = __NAME__ + '.main()'

    # TODO =================================================================
    # TODO: Move to constants file
    # TODO =================================================================
    # number of principal components to be used
    p['TELLU_NUMBER_OF_PRINCIPLE_COMP'] = 5

    p['TELLU_FIT_KEEP_FRAC'] = 20.0

    p['TELLU_PLOT_ORDER'] = 35

    p['tellu_fit_min_transmission'] = 0.2
    p['tellu_lambda_min'] = 1000.0
    p['tellu_lambda_max'] = 2100.0

    p['TELLU_FIT_VSINI'] = 15.0

    p['TELLU_FIT_NITER'] = 4

    p['TELLU_FIT_VSINI2'] = 30.0

    # TODO =================================================================

    # ------------------------------------------------------------------
    # Load first file
    # ------------------------------------------------------------------
    loc = ParamDict()
    rd = spirouImage.ReadImage(p, p['FITSFILENAME'])
    loc['DATA'], loc['DATAHDR'], loc['DATACDR'], loc['XDIM'], loc['YDIM'] = rd
    loc.set_sources(['DATA', 'DATAHDR', 'DATACDR', 'XDIM', 'YDIM'], main_name)

    # ------------------------------------------------------------------
    # Read wavelength solution
    # ------------------------------------------------------------------
    loc['WAVE'] = spirouImage.GetWaveSolution(p, loc['DATA'], loc['DATAHDR'])

    # ----------------------------------------------------------------------
    # Get and Normalise the blaze
    # ----------------------------------------------------------------------
    loc = spirouTelluric.GetNormalizedBlaze(p, loc, loc['DATAHDR'])

    # ----------------------------------------------------------------------
    # Load transmission files
    # ----------------------------------------------------------------------
    trans_files = spirouDB.GetDatabaseTellMap(p)

    # ----------------------------------------------------------------------
    # Load template (if available)
    # ----------------------------------------------------------------------
    # TODO: Is this per object? If so how do we select? Based on OBJNAME?
    # TODO: Currently just selects the most recent
    # read filename from telluDB
    template_file = spirouDB.GetDatabaseTellTemp(p, required=False)
    # if we don't have a template flag it
    if template_file is None:
        loc['FLAG_TEMPLATE'] = False
        loc['TEMPLATE'] = None
    else:
        loc['FLAG_TEMPLATE'] = True
        # load template
        template, _, _, _, _ = spirouImage.ReadImage(p, template_file)
        # renormalize the template
        template = template / loc['NBLAZE']
        # add to loc
        loc['TEMPLATE'] = template
    # set the source for flag and template
    loc.set_sources(['FLAG_TEMPLATE', 'TEMPLATE'], main_name)

    # ----------------------------------------------------------------------
    # load the expected atmospheric transmission
    # ----------------------------------------------------------------------
    # read filename from telluDB
    # TODO: This is per wave solution but wave solution in e2ds file header
    # TODO:  If so how do we select?
    # TODO: Currently just selects the most recent
    tapas_file_name = spirouDB.GetDatabaseTellConv(p)
    # load atmospheric transmission
    tapas_all_species = np.load(tapas_file_name)

    # ----------------------------------------------------------------------
    # Generate the absorption map
    # ----------------------------------------------------------------------
    # get number of files
    nfiles = len(trans_files)
    # set up storage for the absorption
    abso = np.zeros([nfiles, np.product(loc['DATA'].shape)])
    # loop around outputfiles and add them to abso
    for it, filename in enumerate(trans_files):
        # push data into array
        data_it, _, _, _, _ = spirouImage.ReadImage(p, filename)
        abso[it, :] = data_it.reshape(np.product(loc['DATA'].shape))

    # log the absorption cube
    log_abso = np.log(abso)

    # ----------------------------------------------------------------------
    # Locate valid pixels for PCA
    # ----------------------------------------------------------------------
    # determining the pixels relevant for PCA construction
    keep = np.isfinite(np.sum(abso, axis=0))
    # log fraction of valid (non NaN) pixels
    fraction = np.sum(keep)/len(keep)
    wmsg = 'Fraction of valid pixels (not NaNs) for PCA construction = {0:.3f}'
    WLOG('', p['LOG_OPT'], wmsg.format(fraction))
    # log fraction of valid pixels > 1 - (1/e)
    keep &= np.min(log_abso, axis=0) > -1
    fraction = np.sum(keep)/len(keep)
    wmsg = 'Fraction of valid pixels with transmission > 1 - (1/e) = {0:.3f}'
    WLOG('', p['LOG_OPT'], wmsg.format(fraction))

    # ----------------------------------------------------------------------
    # Perform PCA analysis on the log of the telluric absorption map
    # ----------------------------------------------------------------------
    loc = spirouTelluric.CalculateAbsorptionPCA(p, loc, log_abso, keep)
    # Plot PCA components
    # debug plot
    if p['DRS_PLOT'] and (p['DRS_DEBUG'] > 1):
        # start interactive plot
        sPlt.start_interactive_session()
        # plot the transmission map plot
        sPlt.tellu_pca_comp_plot(p, loc)
        # end interactive session
        sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Loop around telluric files
    # ----------------------------------------------------------------------
    for filename in p['ARG_FILE_NAMES']:
        # ------------------------------------------------------------------
        # Construct output file names
        # ------------------------------------------------------------------
        # TODO: Move to spirouConfig
        oldext = '.fits'
        newext = '_tellu_free.fits'
        outfilename1 = os.path.basename(filename).replace(oldext, newext)
        outfile1 = os.path.join(p['ARG_FILE_DIR'], outfilename1)
        # TODO: move to spirouConfig
        oldext = '.fits'
        newext = '_tellu.fits'
        outfilename2 = os.path.basename(filename).replace(oldext, newext)
        outfile2 = os.path.join(p['ARG_FILE_DIR'], outfilename2)
        # ------------------------------------------------------------------
        # Skip if output file already exists
        # ------------------------------------------------------------------
        if os.path.exists(outfile1):
            # log that file was skipped
            wmsg = 'File "{0}" exist, skipping.'
            WLOG('', p['LOG_OPT'], wmsg.format(outfilename1))
            continue
        # ------------------------------------------------------------------
        # Read filename
        # ------------------------------------------------------------------
        # read image
        tdata, thdr, hcdr, _, _ = spirouImage.ReadImage(p, filename)
        # normalise with blaze function
        sp = tdata / loc['NBLAZE']
        # ------------------------------------------------------------------
        # Read wavelength solution
        # ------------------------------------------------------------------
        loc['WAVE_IT'] = spirouImage.GetWaveSolution(p, tdata, thdr)

        # ------------------------------------------------------------------
        # Interpolate at shifted wavelengths (if we have a template)
        # ------------------------------------------------------------------
        if loc['FLAG_TEMPLATE']:
            loc = interp_at_shifted_wavelengths(p, loc, thdr)

        # ------------------------------------------------------------------
        # Something
        # ------------------------------------------------------------------
        # get data dimensions
        ydim, xdim = loc['DATA'].shape
        # redefine storage for recon absorption
        recon_abso = np.ones(np.product(loc['DATA'].shape))
        # flatten spectrum and wavelengths
        sp2 = sp.ravel()
        wave2 = loc['WAVE_IT'].ravel()
        # get the normalisation factor
        norm = np.nanmedian(sp2)
        # define the good pixels as those above minimum transmission
        keep = tapas_all_species[0, :] > p['TELLU_FIT_MIN_TRANSMISSION']
        # also require wavelength constraints
        keep &= (wave2 > p['TELLU_LAMBDA_MIN'])
        keep &= (wave2 < p['TELLU_LAMBDA_MAX'])
        # construct convolution kernel
        loc = spirouTelluric.ConstructConvKernel2(p, loc, p['TELLU_FIT_VSINI'])
        # ------------------------------------------------------------------
        # loop around a number of times
        for ite in range(p['TELLU_FIT_NITER']):
            # --------------------------------------------------------------
            # if we don't have a template construct one
            if not loc['FLAG_TEMPLATE']:
                # define template2 to fill
                template2 = np.zeros(np.product(loc['DATA']))
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
                    sp2b= np.convolve(spgood / recon_abso, **ckwargs)
                    # convolve mask for weights
                    ww = np.convolve(np.array(mask, dtype=float), **ckwargs)
                    # wave weighted convolved spectrum into template2
                    template2[start, end] = sp2b / ww
            # else we have template so load it
            else:
                template2 = loc['TEMPLATE2']
            # --------------------------------------------------------------
            # get dd
            dd = (sp2 / template2) / recon_abso
            # --------------------------------------------------------------
            if loc['FLAG_TEMPLATE']:
                # construct convolution kernel
                vsini = p['TELLU_FIT_VSINI2']
                loc = spirouTelluric.ConstructConvKernel2(p, loc, vsini)
                # loop around orders
                for order_num in range(ydim):
                    # get start and end points
                    start = order_num * xdim
                    end = order_num * xdim + xdim
                    # produce a mask of good transmission
                    order_tapas = tapas_all_species[0, start:end]
                    mask = order_tapas > p['TRANSMISSION_CUT']
                    # get good transmission spectrum
                    ddgood = dd[start:end] * np.array(mask, dtype=float)
                    recongood = recon_abso[start:end]
                    # convolve spectrum
                    ckwargs = dict(v=loc['KER2'], mode='same')
                    sp2b= np.convolve(ddgood / recon_abso, **ckwargs)
                    # convolve mask for weights
                    ww = np.convolve(np.array(mask, dtype=float), **ckwargs)
                    # wave weighted convolved spectrum into dd
                    dd[start:end] = dd[start:end] / (sp2b / ww)
            # --------------------------------------------------------------
            # Log dd and subtract median
            # --------------------------------------------------------------
            # log dd
            log_dd = np.log(dd)
            # --------------------------------------------------------------
            # subtract off the median from each order
            for order_num in range(ydim):
                # get start and end points
                start = order_num * xdim
                end = order_num * xdim + xdim
                # get median
                log_dd_med = np.nanmedian(log_dd[start:end])
                # subtract of median
                log_dd[start:end] = log_dd[start:end] - log_dd_med
            # --------------------------------------------------------------
            # identify good pixels to keep
            keep &= np.isfinite(log_dd)
            keep &= np.sum(np.isfinite(loc['PC']), axis=1) == loc['NPC']
            # log number of kept pixels
            wmsg = 'Number to keep total = {0}'.format(np.sum(keep))
            WLOG('', p['LOG_OPT'], wmsg)


    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================






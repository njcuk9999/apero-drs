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

    p['TELLU_FIT_KEEP_FRAC'] = 20

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
        # Interpolate at shifted wavelengths
        # ------------------------------------------------------------------
        if loc['FLAG_TEMPLATE']:
            # Get the Barycentric correction from header
            dv, _, _ = spirouTelluric.GetBERV(p, thdr)
            # set up storage for template
            template2 = np.zeros_like(loc['DATA'])
            # loop around orders
            for order_num in range(loc['DATA'].shape[0]):
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
                    dvshift =  1 + (dv / CONSTANT_C)
                    waveshift = loc['WAVE_IT'][order_num, :]  * dvshift

                    # TODO: Got to here

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






#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DRIFT_RAW_spirou.py

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""
import numpy as np
import os
import time

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouRV
from SpirouDRS import spirouStartup

neilstart = time.time()

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DRIFT_RAW_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt

# -----------------------------------------------------------------------------
# Remove this for final (only for testing)
import sys
if len(sys.argv) == 1:
    sys.argv = ['test: ' + __NAME__, '20170710', 'fp_fp02a203.fits',
                'fp_fp03a203.fits', 'fp_fp04a203.fits']

# =============================================================================
# Define functions
# =============================================================================


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    p = spirouStartup.RunInitialStartup()
    # run specific start up
    p = spirouStartup.RunStartup(p, kind='Drift', prefixes='fp_fp',
                                 calibdb=True)
    # set the fiber type
    p['fiber'] = 'AB'
    p.set_source('fiber', __NAME__ + '/__main__')

    # log processing image type
    p['dprtype'] = spirouImage.GetTypeFromHeader(p, p['kw_DPRTYPE'])
    p.set_source('dprtype', __NAME__ + '/__main__')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['log_opt'], wmsg.format(p['dprtype'], p['program']))

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImage(p)

    # ----------------------------------------------------------------------
    # Get basic image properties for reference file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, hdr, name='acqtime')
    # set sigdet and conad keywords (sigdet is changed later)
    p['kw_CCD_SIGDET'][1] = p['sigdet']
    p['kw_CCD_CONAD'][1] = p['gain']

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac, dark = spirouImage.CorrectForDark(p, data, hdr, nfiles=1,
                                             return_dark=True)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToADU(spirouImage.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], ('Image format changed to '
                            '{0}x{1}').format(*data2.shape[::-1]))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 == 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['log_opt'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get localisation coefficients
    # ----------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p = spirouLOCOR.FiberParams(p, p['fiber'], merge=True)
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr)

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # get tilts
    loc['tilt'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('tilt', __NAME__ + '/__main__ + /spirouImage.ReadTiltFile')

    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    loc['wave'] = spirouImage.ReadWaveFile(p, hdr)
    loc.set_source('wave', __NAME__ + '/__main__ + /spirouImage.ReadWaveFile')

    # ------------------------------------------------------------------
    # Read image order profile
    # ------------------------------------------------------------------
    order_profile, _, _, nx, ny = spirouImage.ReadOrderProfile(p, hdr)

    # ------------------------------------------------------------------
    # Average AB into one fiber for AB, A and B
    # ------------------------------------------------------------------
    # if we have an AB fiber merge fit coefficients by taking the average
    # of the coefficients
    # (i.e. average of the 1st and 2nd, average of 3rd and 4th, ...)
    if p['fiber'] in ['A', 'B', 'AB']:
        # merge
        loc['acc'] = spirouLOCOR.MergeCoefficients(loc, loc['acc'], step=2)
        loc['ass'] = spirouLOCOR.MergeCoefficients(loc, loc['ass'], step=2)
        # set the number of order to half of the original
        loc['number_orders'] = int(loc['number_orders'] / 2)

    # ------------------------------------------------------------------
    # Set up Extract storage
    # ------------------------------------------------------------------
    # Create array to store extraction (for each order and each pixel
    # along order)
    loc['speref'] = np.zeros((loc['number_orders'], data2.shape[1]))
    # Create array to store the signal to noise ratios for each order
    loc['SNR'] = np.zeros(loc['number_orders'])

    # ------------------------------------------------------------------
    # Extract reference file
    # ------------------------------------------------------------------
    # Log that we are extracting reference file
    wmsg = 'Extraction Reference file {0}'
    WLOG('', p['log_opt'], wmsg.format(p['fitsfilename']))

    # loop around each order
    for order_num in range(loc['number_orders']):
        # Extract with Weight
        eargs = [p, loc, data2, order_profile, order_num]
        ekwargs = dict(range1=p['ic_ext_d_range'],
                       range2=p['ic_ext_d_range'])
        e2ds, cpt = spirouEXTOR.ExtractWeightOrder(*eargs, **ekwargs)
        # get window size
        blaze_win1 = int(data2.shape[0] / 2) - p['IC_EXTFBLAZ']
        blaze_win2 = int(data2.shape[0] / 2) + p['IC_EXTFBLAZ']
        # get average flux per pixel
        flux = np.sum(e2ds[blaze_win1:blaze_win2]) / (2 * p['IC_EXTFBLAZ'])
        # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
        snr = flux / np.sqrt(flux + p['IC_DRIFT_NOISE'] ** 2)
        # add calculations to storage
        loc['speref'][order_num] = e2ds
        loc['SNR'][order_num] = snr
        # log the SNR RMS
        wmsg = 'On fiber {0} order {1}: S/N= {2:.1f}'
        wargs = [p['fiber'], order_num, snr]
        WLOG('', p['log_opt'], wmsg.format(*wargs))

    # ------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['speref'], loc['wave']]
    dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DV_BOXSIZE'],
                   threshold=p['IC_DV_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)
    # save to loc
    loc['dvrmsref'], loc['wmeanref'] = dvrmsref, wmeanref
    # log the estimated RV uncertainty
    wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f} m/s'
    WLOG('info', p['log_opt'], wmsg.format(p['fiber'], wmeanref))

    # ------------------------------------------------------------------
    # Reference plots
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive session if needed
        sPlt.start_interactive_session()
        # plot FP spectral order
        sPlt.drift_plot_selected_wave_ref(p, loc)
        # plot photon noise uncertainty
        sPlt.drift_plot_photon_uncertainty(p, loc)

    # ------------------------------------------------------------------
    # Get all other fp_fp*[ext].fits files
    # ------------------------------------------------------------------
    # Get files, remove fitsfilename, and sort
    listfiles = spirouImage.GetAllSimilarFiles(p)
    Nfiles = len(listfiles)
    # Log the number of files found
    wmsg = 'Nb fp_fp files found on directory = {0}'
    WLOG('info', p['log_opt'], wmsg.format(Nfiles))

    # ------------------------------------------------------------------
    # Set up Extract storage for all files
    # ------------------------------------------------------------------
    # decide whether we need to skip (for large number of files)
    if len(listfiles) >= p['DRIFT_NLARGE']:
        Nfiles = int(Nfiles/p['DRIFT_FILE_SKIP'])
        skip = p['DRIFT_FILE_SKIP']
    else:
        skip = 1
    # set up storage
    loc['drift'] = np.zeros((Nfiles+1, loc['number_orders']))
    loc['errdrift'] = np.zeros((Nfiles+1, loc['number_orders']))
    loc['deltatime'] = np.zeros((Nfiles+1, loc['number_orders']))


    spirouConfig.Constants.EXIT()(1)
    # ------------------------------------------------------------------
    # Loop around all files: correct for dark, reshape, extract and
    #     calculate dvrms and meanpond
    # ------------------------------------------------------------------
    for i_it in range(Nfiles):
        # get file for this iteration
        fpfile = listfiles[::skip][i_it]
        # Log the file we are reading
        wmsg = 'Reading file {0}'
        WLOG('', p['log_opt'], wmsg.format(os.path.split(fpfile)[-1]))
        # ------------------------------------------------------------------
        # read, correct for dark and reshape iteration file
        # ------------------------------------------------------------------
        # read data
        datai, hdri, cdri, nxi, nyi = spirouImage.ReadImage(p, filename=fpfile,
                                                            log=False)
        # get acqtime
        bjdspe = spirouImage.GetAcqTime(p, hdri, name='acqtime', return_value=1)
        # correct for dark (using dark from reference file)
        dataci = datai - dark
        # rotate the image and convert from ADU/s to e-
        datai = spirouImage.ConvertToADU(spirouImage.FlipImage(dataci), p=p)
        # convert NaN to zeros
        data0i = np.where(~np.isfinite(datai), np.zeros_like(datai), datai)
        # resize image (using bkwargs from reference)
        data2i = spirouImage.ResizeImage(data0i, **bkwargs)
        # ------------------------------------------------------------------
        # Extract iteration file
        # ------------------------------------------------------------------
        loc['spe'] = np.zeros((loc['number_orders'], data2.shape[1]))
        # loop around each order
        for order_num in range(loc['number_orders']):
            # Extract with Weight
            eargs = [p, loc, data2i, order_profile, order_num]
            ekwargs = dict(range1=p['ic_ext_d_range'],
                           range2=p['ic_ext_d_range'])
            e2ds, cpt = spirouEXTOR.ExtractWeightOrder(*eargs, **ekwargs)
            # save in loc
            loc['spe'][order_num] = e2ds
        # ------------------------------------------------------------------
        # Compute photon noise uncertainty for iteration file
        # ------------------------------------------------------------------
        # set up the arguments for DeltaVrms2D
        dargs = [loc['spe'], loc['wave']]
        dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'],
                       size=p['IC_DRIFT_BOXSIZE'],
                       threshold=p['IC_DRIFT_MAXFLUX'])
        # run DeltaVrms2D
        dvrmsspe, wmodespe = spirouRV.DeltaVrms2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Compute the correction of the cosmics and re-normalisation by
        #   comparison with the reference spectrum
        # ------------------------------------------------------------------
        # correction of the cosmics and renomalisation by comparison with
        #   the reference spectrum
        dargs = [loc['speref'], loc['spe']]
        dkwargs = dict(threshold=p['IC_DRIFT_MAXFLUX'],
                       size=p['IC_DRIFT_BOXSIZE'],
                       cut=p['IC_DRIFT_CUT'])
        spen, cnormspe, cpt = spirouRV.ReNormCosmic2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Calculate the RV drift
        # ------------------------------------------------------------------
        dargs = [loc['speref'], spen, loc['wave']]
        dkwargs = dict(threshold=p['IC_DRIFT_MAXFLUX'],
                       size=p['IC_DRIFT_BOXSIZE'],
                       cut=p['IC_DRIFT_CUT'])
        rv = spirouRV.CalcRVdrift2D(*dargs)

        # ------------------------------------------------------------------
        # Calculate mean RV
        # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Plot of mean drift
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Save drift values to file
    # ------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                 '').format(p['program']))

# =============================================================================
# End of code
# =============================================================================

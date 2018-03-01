#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_DRIFT_RAW_spirou.py [night_directory] [Reference file name]

Old drift recipe. Extracts the spectra and calculates the drift between the
reference file and all other similar named files (also extracted in this code).

Created on 2017-10-12 at 15:21

@author: cook

Last modified: 2017-12-12 at 10:54

Up-to-date with cal_DRIFT_RAW_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouRV
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DRIFT_RAW_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None, fiber='AB'):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, kind='Drift', prefixes='fp_fp',
                                       calibdb=True)
    # set the fiber type
    p['fiber'] = fiber
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
    p = spirouImage.GetAcqTime(p, hdr, name='acqtime', kind='unix')
    bjdref = p['acqtime']
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
    # get wave image
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
    # set loc sources
    loc.set_sources(['speref', 'SNR'], __NAME__ + '/__main__()')

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
    dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DRIFT_BOXSIZE'],
                   threshold=p['IC_DRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)
    # save to loc
    loc['dvrmsref'], loc['wmeanref'] = dvrmsref, wmeanref
    loc.set_sources(['dvrmsref', 'wmeanref'], __NAME__ + '/__main__()')
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
    # get reduced folder
    reffilename = p['fitsfilename']
    rfolder = p['raw_dir']
    # Get files, remove fitsfilename, and sort
    prefix = p['arg_file_names'][0][0:5]
    suffix = p['arg_file_names'][0][-8:]
    listfiles = spirouImage.GetAllSimilarFiles(p, rfolder, prefix, suffix)
    # remove reference file
    try:
        listfiles.remove(reffilename)
    except ValueError:
        emsg = 'File {0} not found in {1}'
        WLOG('error', p['log_opt'], emsg.format(reffilename, rfolder))
    # get length of files
    nfiles = len(listfiles)
    # make sure we have some files
    if nfiles == 0:
        emsg = 'No additional {0}*{1} files found in {2}'
        WLOG('error', p['log_opt'], emsg.format(prefix, suffix, rfolder))
    else:
        # else Log the number of files found
        wmsg = 'Number of fp_fp files found on directory = {0}'
        WLOG('info', p['log_opt'], wmsg.format(nfiles))

    # ------------------------------------------------------------------
    # Set up Extract storage for all files
    # ------------------------------------------------------------------
    # decide whether we need to skip (for large number of files)
    if len(listfiles) >= p['DRIFT_NLARGE']:
        nfiles = int(nfiles/p['DRIFT_FILE_SKIP'])
        skip = p['DRIFT_FILE_SKIP']
    else:
        skip = 1
    # set up storage
    loc['drift'] = np.zeros((nfiles, loc['number_orders']))
    loc['errdrift'] = np.zeros((nfiles, loc['number_orders']))
    loc['deltatime'] = np.zeros(nfiles)
    # set loc sources
    keys = ['drift', 'errdrift', 'deltatime']
    loc.set_sources(keys, __NAME__ + '/__main__()')

    # ------------------------------------------------------------------
    # Loop around all files: correct for dark, reshape, extract and
    #     calculate dvrms and meanpond
    # ------------------------------------------------------------------
    wref = 1.0
    for i_it in range(nfiles):
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
        bjdspe = spirouImage.GetAcqTime(p, hdri, name='acqtime', kind='unix',
                                        return_value=1)
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
        loc.set_source('spe', __NAME__ + '/__main__()')
        # loop around each order
        for order_num in range(loc['number_orders']):
            # Extract with Weight
            eargs = [p, loc, data2i, order_profile, order_num]
            ekwargs = dict(range1=p['IC_EXT_D_RANGE'],
                           range2=p['IC_EXT_D_RANGE'])
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
                       cut=p['IC_DRIFT_CUT_RAW'])
        spen, cfluxr, cpt = spirouRV.ReNormCosmic2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Calculate the RV drift
        # ------------------------------------------------------------------
        dargs = [loc['speref'], spen, loc['wave']]
        dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'],
                       threshold=p['IC_DRIFT_MAXFLUX'],
                       size=p['IC_DRIFT_BOXSIZE'])
        rv = spirouRV.CalcRVdrift2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Calculate RV properties
        # ------------------------------------------------------------------
        # calculate the mean flux ratio
        meanfratio = np.mean(cfluxr)
        # calculate the weighted mean radial velocity
        wref = 1.0/dvrmsref
        meanrv = np.sum(rv * wref)/np.sum(wref)
        err_meanrv = np.sqrt(dvrmsref + dvrmsspe)
        # calculate the time from reference (in hours)
        deltatime = (bjdspe - bjdref) * 24
        # Log the RV properties
        wmsg = ('Time from ref={0:.2f} h  - Drift mean={1:.2f} m/s - Flux '
                'ratio={2:.2f} = Nb Comsic={3}')
        WLOG('', p['log_opt'], wmsg.format(deltatime, meanrv, meanfratio, cpt))
        # add this iteration to storage
        loc['drift'][i_it] = rv
        loc['errdrift'][i_it] = err_meanrv
        loc['deltatime'][i_it] = deltatime

    # ------------------------------------------------------------------
    # Calculate drift properties
    # ------------------------------------------------------------------
    # get the maximum number of orders to use
    nomax = p['IC_DRIFT_N_ORDER_MAX']
    # ------------------------------------------------------------------
    # if use mean
    if p['drift_type_raw'].upper() == 'WEIGHTED MEAN':
        # mean radial velocity
        sumwref = np.sum(wref[:nomax])
        meanrv = np.sum(loc['drift'][:, :nomax] * wref[:nomax], 1)/sumwref
        # error in mean radial velocity
        errdrift2 = loc['errdrift'][:, :nomax]**2
        meanerr = 1.0/np.sqrt(np.sum(1.0/errdrift2, 1))
        # add to loc
        loc['mdrift'] = meanrv
        loc['merrdrift'] = meanerr
    # else use median
    else:
        # median drift
        loc['mdrift'] = np.median(loc['drift'][:, :nomax], 1)
        # median err drift
        loc['merrdrift'] = np.median(loc['errdrift'][:, :nomax], 1)
    # set source
    loc.set_sources(['mdrift', 'merrdrift'], __NAME__ + '/__main__()')
    # ------------------------------------------------------------------
    # peak to peak drift
    driftptp = np.max(loc['mdrift']) - np.min(loc['mdrift'])
    driftrms = np.std(loc['mdrift'])
    # log th etotal drift peak-to-peak and rms
    wmsg = ('Total drift Peak-to-Peak={0:.3f} m/s RMS={1:.3f} m/s in '
            '{2:.2f} hour')
    wargs = [driftptp, driftrms, np.max(loc['deltatime'])]
    WLOG('', p['log_opt'], wmsg.format(*wargs))

    # ------------------------------------------------------------------
    # Plot of mean drift
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive session if needed
        sPlt.start_interactive_session()
        # plot delta time against median drift
        sPlt.drift_plot_dtime_against_mdrift(p, loc, kind='raw')

    # ------------------------------------------------------------------
    # Save drift values to file
    # ------------------------------------------------------------------
    # construct filename
    driftfits = spirouConfig.Constants.DRIFT_RAW_FILE(p)
    driftfitsname = os.path.split(driftfits)[-1]
    # log that we are saving drift values
    wmsg = 'Saving drift values of Fiber {0} in {1}'
    WLOG('', p['log_opt'], wmsg.format(p['fiber'], driftfitsname))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # save drift values
    spirouImage.WriteImage(driftfits, loc['drift'], hdict)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))

    # return a copy of locally defined variables in the memory
    return dict(locals())

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_DRIFT_RAW_spirou.py [night_directory] [files]

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
    """
    cal_DRIFT_RAW_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_DRIFT_RAW_spirou.py [night_directory] [files]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)
    :param fiber: string, the fiber to extract (AB, A, B or C)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, kind='Drift', prefixes='fp_fp',
                                       calibdb=True)
    # set the fiber type
    p['FIBER'] = fiber
    p.set_source('FIBER', __NAME__ + '/__main__')

    # log processing image type
    p['DPRTYPE'] = spirouImage.GetTypeFromHeader(p, p['KW_DPRTYPE'])
    p.set_source('DPRTYPE', __NAME__ + '/__main__')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['DPRTYPE'], p['PROGRAM']))

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
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']

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
    WLOG('', p['LOG_OPT'], ('Image format changed to '
                            '{0}x{1}').format(*data2.shape[::-1]))

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 == 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.2f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get localisation coefficients
    # ----------------------------------------------------------------------
    # original there is a loop but it is not used --> removed
    p = spirouLOCOR.FiberParams(p, p['FIBER'], merge=True)
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr)

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # get tilts
    loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('TILT', __NAME__ + '/__main__ + /spirouImage.ReadTiltFile')

    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    # get wave image
    loc['WAVE'] = spirouImage.ReadWaveFile(p, hdr)
    loc.set_source('WAVE', __NAME__ + '/__main__ + /spirouImage.ReadWaveFile')

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
    if p['FIBER'] in ['A', 'B', 'AB']:
        # merge
        loc['ACC'] = spirouLOCOR.MergeCoefficients(loc, loc['ACC'], step=2)
        loc['ASS'] = spirouLOCOR.MergeCoefficients(loc, loc['ASS'], step=2)
        # set the number of order to half of the original
        loc['NUMBER_ORDERS'] = int(loc['NUMBER_ORDERS'] / 2)

    # ------------------------------------------------------------------
    # Set up Extract storage
    # ------------------------------------------------------------------
    # Create array to store extraction (for each order and each pixel
    # along order)
    loc['SPEREF'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
    # Create array to store the signal to noise ratios for each order
    loc['SNR'] = np.zeros(loc['NUMBER_ORDERS'])
    # set loc sources
    loc.set_sources(['speref', 'SNR'], __NAME__ + '/__main__()')

    # ------------------------------------------------------------------
    # Extract reference file
    # ------------------------------------------------------------------
    # Log that we are extracting reference file
    wmsg = 'Extraction Reference file {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(p['FITSFILENAME']))

    # loop around each order
    for order_num in range(loc['NUMBER_ORDERS']):
        # Extract with Weight
        eargs = [p, loc, data2, order_profile, order_num]
        ekwargs = dict(range1=p['IC_EXT_D_RANGE'],
                       range2=p['IC_EXT_D_RANGE'])
        e2ds, cpt = spirouEXTOR.ExtractWeightOrder(*eargs, **ekwargs)
        # get window size
        blaze_win1 = int(data2.shape[0] / 2) - p['IC_EXTFBLAZ']
        blaze_win2 = int(data2.shape[0] / 2) + p['IC_EXTFBLAZ']
        # get average flux per pixel
        flux = np.sum(e2ds[blaze_win1:blaze_win2]) / (2 * p['IC_EXTFBLAZ'])
        # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
        snr = flux / np.sqrt(flux + p['IC_DRIFT_NOISE'] ** 2)
        # add calculations to storage
        loc['SPEREF'][order_num] = e2ds
        loc['SNR'][order_num] = snr
        # log the SNR RMS
        wmsg = 'On fiber {0} order {1}: S/N= {2:.1f}'
        wargs = [p['FIBER'], order_num, snr]
        WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

    # ------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['SPEREF'], loc['WAVE']]
    dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DRIFT_BOXSIZE'],
                   threshold=p['IC_DRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)
    # save to loc
    loc['DVRMSREF'], loc['WMEANREF'] = dvrmsref, wmeanref
    loc.set_sources(['dvrmsref', 'wmeanref'], __NAME__ + '/__main__()')
    # log the estimated RV uncertainty
    wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f} m/s'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['FIBER'], wmeanref))

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
    reffilename = p['FITSFILENAME']
    rfolder = p['RAW_DIR']
    # Get files, remove fitsfilename, and sort
    prefix = p['ARG_FILE_NAMES'][0][0:5]
    suffix = p['ARG_FILE_NAMES'][0][-8:]
    listfiles = spirouImage.GetAllSimilarFiles(p, rfolder, prefix, suffix)
    # remove reference file
    try:
        listfiles.remove(reffilename)
    except ValueError:
        emsg = 'File {0} not found in {1}'
        WLOG('error', p['LOG_OPT'], emsg.format(reffilename, rfolder))
    # get length of files
    nfiles = len(listfiles)
    # make sure we have some files
    if nfiles == 0:
        emsg = 'No additional {0}*{1} files found in {2}'
        WLOG('error', p['LOG_OPT'], emsg.format(prefix, suffix, rfolder))
    else:
        # else Log the number of files found
        wmsg = 'Number of fp_fp files found on directory = {0}'
        WLOG('info', p['LOG_OPT'], wmsg.format(nfiles))

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
    loc['DRIFT'] = np.zeros((nfiles, loc['NUMBER_ORDERS']))
    loc['ERRDRIFT'] = np.zeros((nfiles, loc['NUMBER_ORDERS']))
    loc['DELTATIME'] = np.zeros(nfiles)
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
        WLOG('', p['LOG_OPT'], wmsg.format(os.path.split(fpfile)[-1]))
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
        loc['SPE'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        loc.set_source('SPE', __NAME__ + '/__main__()')
        # loop around each order
        for order_num in range(loc['NUMBER_ORDERS']):
            # Extract with Weight
            eargs = [p, loc, data2i, order_profile, order_num]
            ekwargs = dict(range1=p['IC_EXT_D_RANGE'],
                           range2=p['IC_EXT_D_RANGE'])
            e2ds, cpt = spirouEXTOR.ExtractWeightOrder(*eargs, **ekwargs)
            # save in loc
            loc['SPE'][order_num] = e2ds
        # ------------------------------------------------------------------
        # Compute photon noise uncertainty for iteration file
        # ------------------------------------------------------------------
        # set up the arguments for DeltaVrms2D
        dargs = [loc['SPE'], loc['WAVE']]
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
        dargs = [loc['SPEREF'], loc['SPE']]
        dkwargs = dict(threshold=p['IC_DRIFT_MAXFLUX'],
                       size=p['IC_DRIFT_BOXSIZE'],
                       cut=p['IC_DRIFT_CUT_RAW'])
        spen, cfluxr, cpt = spirouRV.ReNormCosmic2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Calculate the RV drift
        # ------------------------------------------------------------------
        dargs = [loc['SPEREF'], spen, loc['WAVE']]
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
        WLOG('', p['LOG_OPT'], wmsg.format(deltatime, meanrv, meanfratio, cpt))
        # add this iteration to storage
        loc['DRIFT'][i_it] = rv
        loc['ERRDRIFT'][i_it] = err_meanrv
        loc['DELTATIME'][i_it] = deltatime

    # ------------------------------------------------------------------
    # Calculate drift properties
    # ------------------------------------------------------------------
    # get the maximum number of orders to use
    nomax = p['IC_DRIFT_N_ORDER_MAX']
    # ------------------------------------------------------------------
    # if use mean
    if p['DRIFT_TYPE_RAW'].upper() == 'WEIGHTED MEAN':
        # mean radial velocity
        sumwref = np.sum(wref[:nomax])
        meanrv = np.sum(loc['DRIFT'][:, :nomax] * wref[:nomax], 1)/sumwref
        # error in mean radial velocity
        errdrift2 = loc['ERRDRIFT'][:, :nomax]**2
        meanerr = 1.0/np.sqrt(np.sum(1.0/errdrift2, 1))
        # add to loc
        loc['MDRIFT'] = meanrv
        loc['MERRDRIFT'] = meanerr
    # else use median
    else:
        # median drift
        loc['MDRIFT'] = np.median(loc['DRIFT'][:, :nomax], 1)
        # median err drift
        loc['MERRDRIFT'] = np.median(loc['ERRDRIFT'][:, :nomax], 1)
    # set source
    loc.set_sources(['mdrift', 'merrdrift'], __NAME__ + '/__main__()')
    # ------------------------------------------------------------------
    # peak to peak drift
    driftptp = np.max(loc['MDRIFT']) - np.min(loc['MDRIFT'])
    driftrms = np.std(loc['MDRIFT'])
    # log th etotal drift peak-to-peak and rms
    wmsg = ('Total drift Peak-to-Peak={0:.3f} m/s RMS={1:.3f} m/s in '
            '{2:.2f} hour')
    wargs = [driftptp, driftrms, np.max(loc['DELTATIME'])]
    WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

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
    WLOG('', p['LOG_OPT'], wmsg.format(p['FIBER'], driftfitsname))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # save drift values
    spirouImage.WriteImage(driftfits, loc['DRIFT'], hdict)

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

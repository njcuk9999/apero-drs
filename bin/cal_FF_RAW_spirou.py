#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_SLIT_spirou

Flat Field

Created on 2017-11-06 11:32

@author: cook


Last modified: 2017-12-11 at 15:11

Up-to-date with cal_FF_RAW_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os


from SpirouDRS import spirouBACK
from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from SpirouDRS import spirouFLAT
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_SLIT_spirou.py'
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
def main(night_name=None, files=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    p = spirouStartup.LoadArguments(p, night_name, files)
    # run specific start up
    params2add = dict()
    params2add['dark_flat'] = spirouLOCOR.FiberParams(p, 'C')
    params2add['flat_dark'] = spirouLOCOR.FiberParams(p, 'AB')
    p = spirouStartup.InitialFileSetup(p, kind='Flat-field',
                                       prefixes=['dark_flat', 'flat_dark'],
                                       add_to_p=params2add, calibdb=True)

    # log processing image type
    p['dprtype'] = spirouImage.GetTypeFromHeader(p, p['kw_DPRTYPE'])
    p.set_source('dprtype', __NAME__ + '/main()')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['log_opt'], wmsg.format(p['dprtype'], p['program']))

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImageAndCombine(p, framemath='add')

    # ----------------------------------------------------------------------
    # Get basic image properties
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')
    # set sigdet and conad keywords (sigdet is changed later)
    p['kw_CCD_SIGDET'][1] = p['sigdet']
    p['kw_CCD_CONAD'][1] = p['gain']

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = spirouImage.CorrectForDark(p, data, hdr)

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
    # Get the miny, maxy and max_signal for the central column
    # ----------------------------------------------------------------------
    # get the central column
    y = data2[p['IC_CENT_COL'], :]
    # get the min max and max signal using box smoothed approach
    miny, maxy, max_signal, diff_maxmin = spirouBACK.MeasureMinMaxSignal(p, y)
    # Log max average flux/pixel
    wmsg = 'Maximum average flux/pixel in the spectrum: {0:.1f} [ADU]'
    WLOG('info', p['log_opt'], wmsg.format(max_signal/p['nbframes']))

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG('', p['log_opt'], 'Doing background measurement on raw frame')
        # get the bkgr measurement
        background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(p, data2)
    else:
        background = np.zeros_like(data2)

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # define loc storage parameter dictionary
    loc = ParamDict()
    # get tilts
    loc['tilt'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('tilt', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Fiber loop
    # ----------------------------------------------------------------------
    # loop around fiber types
    for fiber in p['fib_type']:
        # ------------------------------------------------------------------
        # Get localisation coefficients
        # ------------------------------------------------------------------
        # get this fibers parameters
        p = spirouLOCOR.FiberParams(p, fiber, merge=True)
        # get localisation fit coefficients
        loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
        # ------------------------------------------------------------------
        # Read image order profile
        # ------------------------------------------------------------------
        order_profile, _, _, nx, ny = spirouImage.ReadOrderProfile(p, hdr)
        # ------------------------------------------------------------------
        # Average AB into one fiber
        # ------------------------------------------------------------------
        # if we have an AB fiber merge fit coefficients by taking the average
        # of the coefficients
        # (i.e. average of the 1st and 2nd, average of 3rd and 4th, ...)
        if fiber in ['A', 'B', 'AB']:
            # merge
            loc['acc'] = spirouLOCOR.MergeCoefficients(loc, loc['acc'], step=2)
            loc['ass'] = spirouLOCOR.MergeCoefficients(loc, loc['ass'], step=2)
            # set the number of order to half of the original
            loc['number_orders'] = int(loc['number_orders']/2.0)
        # ------------------------------------------------------------------
        # Set up Extract storage
        # ------------------------------------------------------------------
        # Create array to store extraction (for each order and each pixel
        # along order)
        loc['e2ds'] = np.zeros((loc['number_orders'], data2.shape[1]))
        # Create array to store the blaze (for each order and at each pixel
        # along order)
        loc['blaze'] = np.zeros((loc['number_orders'], data2.shape[1]))
        # Create array to store the flat (for each order and at each pixel
        # along order)
        loc['flat'] = np.zeros((loc['number_orders'], data2.shape[1]))
        # Create array to store the signal to noise ratios for each order
        loc['SNR'] = np.zeros(loc['number_orders'])
        # Create array to store the rms for each order
        loc['RMS'] = np.zeros(loc['number_orders'])

        # Manually set the sigdet to be used in extraction weighting
        if p['IC_FF_SIGDET'] > 0:
            p['sigdet'] = float(p['IC_FF_SIGDET'])
        # ------------------------------------------------------------------
        # Extract orders
        # old code time: 1 loop, best of 3: 22.3 s per loop
        # new code time: 3.16 s ± 237 ms per loop
        # ------------------------------------------------------------------
        # loop around each order
        for order_num in range(loc['number_orders']):
            # extract this order
            eargs = [p, loc, data2, order_profile, order_num]
            e2ds, cpt = spirouEXTOR.ExtractTiltWeightOrder2(*eargs)
            # calculate the noise
            range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
            noise = p['sigdet'] * np.sqrt(range1 + range2)
            # get window size
            blaze_win1 = int(data2.shape[0]/2) - p['IC_EXTFBLAZ']
            blaze_win2 = int(data2.shape[0]/2) + p['IC_EXTFBLAZ']
            # get average flux per pixel
            flux = np.sum(e2ds[blaze_win1:blaze_win2]) / (2*p['IC_EXTFBLAZ'])
            # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
            snr = flux / np.sqrt(flux + noise**2)
            # calcualte the blaze function
            blaze = spirouFLAT.MeasureBlazeForOrder(e2ds, p['IC_BLAZE_FITN'])
            # calculate the flat
            flat = e2ds/blaze
            # calculate the rms
            rms = np.std(flat)
            # log the SNR RMS
            wmsg = 'On fiber {0} order {1}: S/N= {2:.1f}  - FF rms={3:.2f} %'
            wargs = [fiber, order_num, snr, rms * 100.0]
            WLOG('', p['log_opt'], wmsg.format(*wargs))
            # add calculations to storage
            loc['e2ds'][order_num] = e2ds
            loc['SNR'][order_num] = snr
            loc['RMS'][order_num] = rms
            loc['blaze'][order_num] = blaze
            loc['flat'][order_num] = flat
            # set sources
            source = __NAME__ + '/main()()'
            loc.set_sources(['e2ds', 'SNR', 'RMS', 'blaze', 'flat'], source)
            # Log if saturation level reached
            satvalue = (flux/p['gain'])/(range1 + range2)
            if satvalue > (p['QC_LOC_FLUMAX'] * p['nbframes']):
                wmsg = 'SATURATION LEVEL REACHED on Fiber {0}'
                WLOG('warning', p['log_opt'], wmsg.format(fiber))

        # ----------------------------------------------------------------------
        # Plots
        # ----------------------------------------------------------------------
        if p['DRS_PLOT']:
            # start interactive session if needed
            sPlt.start_interactive_session()
            # plot all orders or one order
            if p['IC_FF_PLOT_ALL_ORDERS']:
                # plot image with all order fits (slower)
                sPlt.ff_aorder_fit_edges(p, loc, data2)
            else:
                # plot image with selected order fit and edge fit (faster)
                sPlt.ff_sorder_fit_edges(p, loc, data2)
            # plot tilt adjusted e2ds and blaze for selected order
            sPlt.ff_sorder_tiltadj_e2ds_blaze(p, loc, data2)
            # plot flat for selected order
            sPlt.ff_sorder_flat(p, loc, data2)

        # ----------------------------------------------------------------------
        # Store Blaze in file
        # ----------------------------------------------------------------------
        # construct filename
        blazefits = spirouConfig.Constants.FF_BLAZE_FILE(p)
        blazefitsname = os.path.split(blazefits)[-1]
        # log that we are saving blaze file
        wmsg = 'Saving blaze spectrum for fiber: {0} in {1}'
        WLOG('', p['log_opt'] + fiber, wmsg.format(fiber, blazefitsname))
        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
        # define new keys to add
        hdict = spirouImage.AddKey(hdict, p['kw_version'])
        hdict = spirouImage.AddKey(hdict, p['kw_CCD_SIGDET'])
        hdict = spirouImage.AddKey(hdict, p['kw_CCD_CONAD'])
        # write 1D list of the SNR
        hdict = spirouImage.AddKey1DList(hdict, p['kw_EXTRA_SN'],
                                         values=loc['SNR'])
        # write center fits and add header keys (via hdict)
        spirouImage.WriteImage(blazefitsname, loc['blaze'], hdict)

        # ----------------------------------------------------------------------
        # Store Flat-field in file
        # ----------------------------------------------------------------------
        # construct filename
        flatfits = spirouConfig.Constants.FF_FLAT_FILE(p)
        flatfitsname = os.path.split(flatfits)[-1]
        # log that we are saving blaze file
        wmsg = 'Saving FF spectrum for fiber: {0} in {1}'
        WLOG('', p['log_opt'] + fiber, wmsg.format(fiber, flatfitsname))
        # write 1D list of the RMS (add to hdict from blaze)
        hdict = spirouImage.AddKey1DList(hdict, p['kw_FLAT_RMS'],
                                         values=loc['RMS'])
        # write center fits and add header keys (via same hdict as blaze)
        spirouImage.WriteImage(flatfits, loc['flat'], hdict)

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        passed, fail_msg = True, []
        # saturation check: check that the max_signal is lower than
        # qc_max_signal
        # if max_signal > (p['QC_MAX_SIGNAL'] * p['nbframes']):
        #     fmsg = 'Too much flux in the image (max authorized={0})'
        #     fail_msg.append(fmsg.format(p['QC_MAX_SIGNAL'] * p['nbframes']))
        #     passed = False
        #     # For some reason this test is ignored in old code
        #     passed = True
        #     WLOG('info', p['log_opt'], fail_msg[-1])
        max_rms = np.max(loc['RMS'])
        if max_rms > p['QC_FF_RMS']:
            fmsg = 'abnormal RMS of FF ({0:.2f} > {1:.2f})'
            fail_msg.append(fmsg.format(max_rms, p['QC_FF_RMS']))
            passed = False

        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if passed:
            wmsg = 'QUALITY CONTROL SUCCESSFUL - Well Done -'
            WLOG('info', p['log_opt'], wmsg)
            p['QC'] = 1
            p.set_source('QC', __NAME__ + '/main()')
        else:
            for farg in fail_msg:
                wmsg = 'QUALITY CONTROL FAILED: {0}'
                WLOG('info', p['log_opt'], wmsg.format(farg))
            p['QC'] = 0
            p.set_source('QC', __NAME__ + '/main()')

        # ------------------------------------------------------------------
        # Update the calibration database
        # ------------------------------------------------------------------
        if p['QC'] == 1:
            keydb = 'FLAT_' + p['fiber']
            # copy localisation file to the calibDB folder
            spirouCDB.PutFile(p, flatfits)
            # update the master calib DB file with new key
            spirouCDB.UpdateMaster(p, keydb, flatfitsname, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been succesfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))

    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    locals = main()


# =============================================================================
# End of code
# =============================================================================

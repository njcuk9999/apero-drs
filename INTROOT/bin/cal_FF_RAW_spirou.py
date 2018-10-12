#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_FF_RAW_spirou.py [night_directory] [files]

Flat Field

Created on 2017-11-06 11:32

@author: cook

Last modified: 2017-12-11 at 15:11

Up-to-date with cal_FF_RAW_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os
import warnings

from SpirouDRS import spirouBACK
from SpirouDRS import spirouDB
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
__NAME__ = 'cal_FF_RAW_spirou.py'
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
    """
    cal_FF_RAW_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_FF_RAW_spirou.py [night_directory] [files]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, calibdb=True)

    # run specific start up
    p['FIB_TYPE'] = p['FIBER_TYPES']
    p.set_source('FIB_TYPE', __NAME__ + '__main__()')

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, data, hdr, cdr = spirouImage.ReadImageAndCombine(p, framemath='add')

    # ----------------------------------------------------------------------
    # fix for un-preprocessed files
    # ----------------------------------------------------------------------
    data = spirouImage.FixNonPreProcess(p, data)

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
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    p, datac = spirouImage.CorrectForDark(p, data, hdr)

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
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    p, data2 = spirouImage.CorrectForBadPix(p, data2, hdr)

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data2 == 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data2.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.4f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get the miny, maxy and max_signal for the central column
    # ----------------------------------------------------------------------
    # get the central column
    y = data2[p['IC_CENT_COL'], :]
    # get the min max and max signal using box smoothed approach
    miny, maxy, max_signal, diff_maxmin = spirouBACK.MeasureMinMaxSignal(p, y)
    # Log max average flux/pixel
    wmsg = 'Maximum average flux/pixel in the spectrum: {0:.1f} [ADU]'
    WLOG('info', p['LOG_OPT'], wmsg.format(max_signal/p['NBFRAMES']))

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG('', p['LOG_OPT'], 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bdata = spirouBACK.MeasureBackgroundFF(p, data2)
        background, gridx, gridy, minlevel = bdata
    else:
        background = np.zeros_like(data2)

    # data2=data2-background
    # correct data2 with background (where positive)
    data2 = np.where(data2 > 0, data2 - background, 0)

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # define loc storage parameter dictionary
    loc = ParamDict()
    # get tilts
    p, loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('TILT', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Fiber loop
    # ----------------------------------------------------------------------
    # loop around fiber types
    for fiber in p['FIB_TYPE']:
        # set fiber in p
        p['FIBER'] = fiber
        p.set_source('FIBER', __NAME__ + '/main()')

        # get fiber parameters
        params2add = spirouImage.FiberParams(p, p['FIBER'])
        for param in params2add:
            p[param] = params2add[param]
            p.set_source(param, __NAME__ + '.main()')

        # ------------------------------------------------------------------
        # Get localisation coefficients
        # ------------------------------------------------------------------
        # get this fibers parameters
        p = spirouImage.FiberParams(p, fiber, merge=True)
        # get localisation fit coefficients
        p, loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
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
        # if fiber is AB take the average of the orders
        if fiber == 'AB':
            # merge
            loc['ACC'] = spirouLOCOR.MergeCoefficients(loc, loc['ACC'], step=2)
            loc['ASS'] = spirouLOCOR.MergeCoefficients(loc, loc['ASS'], step=2)
            # set the number of order to half of the original
            loc['NUMBER_ORDERS'] = int(loc['NUMBER_ORDERS']/2.0)
        # if fiber is B take the even orders
        elif fiber == 'B':
            loc['ACC'] = loc['ACC'][:-1:2]
            loc['ASS'] = loc['ASS'][:-1:2]
            loc['NUMBER_ORDERS'] = int(loc['NUMBER_ORDERS'] / 2.0)
        # if fiber is A take the even orders
        elif fiber == 'A':
            loc['ACC'] = loc['ACC'][1::2]
            loc['ASS'] = loc['ASS'][:-1:2]
            loc['NUMBER_ORDERS'] = int(loc['NUMBER_ORDERS'] / 2.0)

        # ------------------------------------------------------------------
        # Set up Extract storage
        # ------------------------------------------------------------------
        # Create array to store extraction (for each order and each pixel
        # along order)
        loc['E2DS'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        # Create array to store the blaze (for each order and at each pixel
        # along order)
        loc['BLAZE'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        # Create array to store the flat (for each order and at each pixel
        # along order)
        loc['FLAT'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        # Create array to store the signal to noise ratios for each order
        loc['SNR'] = np.zeros(loc['NUMBER_ORDERS'])
        # Create array to store the rms for each order
        loc['RMS'] = np.zeros(loc['NUMBER_ORDERS'])

        # Manually set the sigdet to be used in extraction weighting
        if p['IC_FF_SIGDET'] > 0:
            p['SIGDET'] = float(p['IC_FF_SIGDET'])
        # ------------------------------------------------------------------
        # Extract orders
        # old code time: 1 loop, best of 3: 22.3 s per loop
        # new code time: 3.16 s ± 237 ms per loop
        # ------------------------------------------------------------------
        # get limits of order extraction
        valid_orders = spirouFLAT.GetValidOrders(p, loc)
        # loop around each order
        for order_num in valid_orders:
            # extract this order
            eargs = [p, loc, data2, order_num]
            ekwargs = dict(mode=p['IC_FF_EXTRACT_TYPE'],
                           order_profile=order_profile)
            with warnings.catch_warnings(record=True) as w:
                eout = spirouEXTOR.Extraction(*eargs, **ekwargs)
            #deal with different return
            if p['IC_EXTRACT_TYPE'] in ['3c', '3d', '4a', '4b']:
                e2ds, e2dsll, cpt = eout
            else:
                e2ds, cpt = eout
                e2dsll = None
            # calculate the noise
            range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
            noise = p['SIGDET'] * np.sqrt(range1 + range2)
            # get window size
            blaze_win1 = int(data2.shape[1]/2) - p['IC_EXTFBLAZ']
            blaze_win2 = int(data2.shape[1]/2) + p['IC_EXTFBLAZ']
            # get average flux per pixel
            flux = np.sum(e2ds[blaze_win1:blaze_win2]) / (2*p['IC_EXTFBLAZ'])
            # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
            snr = flux / np.sqrt(flux + noise**2)
            # remove edge of orders at low S/N
            e2ds = np.where(e2ds < flux / p['IC_FRACMINBLAZE'], 0., e2ds)
#            e2ds = np.where(e2ds < p['IC_MINBLAZE'], 0., e2ds)
            # calcualte the blaze function
            blaze = spirouFLAT.MeasureBlazeForOrder(p, e2ds)
            # calculate the flat
            flat = np.where(blaze > 1, e2ds / blaze, 1)
            # calculate the rms
            rms = np.std(flat)
            # log the SNR RMS
            wmsg = 'On fiber {0} order {1}: S/N= {2:.1f}  - FF rms={3:.2f} %'
            wargs = [fiber, order_num, snr, rms * 100.0]
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
            # add calculations to storage
            loc['E2DS'][order_num] = e2ds
            loc['SNR'][order_num] = snr
            loc['RMS'][order_num] = rms
            loc['BLAZE'][order_num] = blaze
            loc['FLAT'][order_num] = flat
            # set sources
            source = __NAME__ + '/main()()'
            loc.set_sources(['e2ds', 'SNR', 'RMS', 'blaze', 'flat'], source)
            # Log if saturation level reached
            satvalue = (flux/p['GAIN'])/(range1 + range2)
            if satvalue > (p['QC_LOC_FLUMAX'] * p['NBFRAMES']):
                wmsg = 'SATURATION LEVEL REACHED on Fiber {0} order={1}'
                WLOG('warning', p['LOG_OPT'], wmsg.format(fiber, order_num))

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
            sPlt.ff_sorder_tiltadj_e2ds_blaze(p, loc)
            # plot flat for selected order
            sPlt.ff_sorder_flat(p, loc)
            # plot the RMS for all but skipped orders
            # sPlt.ff_rms_plot(p, loc)

        # ----------------------------------------------------------------------
        # Store Blaze in file
        # ----------------------------------------------------------------------
        # get raw flat filename
        raw_flat_file = os.path.basename(p['FITSFILENAME'])
        # get extraction method and function
        efout = spirouEXTOR.GetExtMethod(p, p['IC_FF_EXTRACT_TYPE'])
        extmethod, extfunc = efout
        # construct filename
        blazefits, tag1 = spirouConfig.Constants.FF_BLAZE_FILE(p)
        blazefitsname = os.path.split(blazefits)[-1]
        # log that we are saving blaze file
        wmsg = 'Saving blaze spectrum for fiber: {0} in {1}'
        WLOG('', p['LOG_OPT'] + fiber, wmsg.format(fiber, blazefitsname))
        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
        # define new keys to add
        hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag1)
        hdict = spirouImage.AddKey(hdict, p['KW_DARKFILE'], value=p['DARKFILE'])
        hdict = spirouImage.AddKey(hdict, p['KW_BADPFILE1'],
                                   value=p['BADPFILE1'])
        hdict = spirouImage.AddKey(hdict, p['KW_BADPFILE2'],
                                   value=p['BADPFILE2'])
        hdict = spirouImage.AddKey(hdict, p['KW_LOCOFILE'], value=p['LOCOFILE'])
        hdict = spirouImage.AddKey(hdict, p['KW_TILTFILE'], value=p['TILTFILE'])
        hdict = spirouImage.AddKey(hdict, p['KW_BLAZFILE'], value=raw_flat_file)
        hdict = spirouImage.AddKey(hdict, p['KW_CCD_SIGDET'])
        hdict = spirouImage.AddKey(hdict, p['KW_CCD_CONAD'])
        # copy extraction method and function to header
        #     (for reproducibility)
        hdict = spirouImage.AddKey(hdict, p['KW_E2DS_EXTM'],
                                   value=extmethod)
        hdict = spirouImage.AddKey(hdict, p['KW_E2DS_FUNC'],
                                   value=extfunc)
        # output keys
        hdict = spirouImage.AddKey(hdict, p['KW_EXT_TYPE'], value=p['DPRTYPE'])
        # write 1D list of the SNR
        hdict = spirouImage.AddKey1DList(hdict, p['KW_EXTRA_SN'],
                                         values=loc['SNR'])
        # write center fits and add header keys (via hdict)
        p = spirouImage.WriteImage(p, blazefits, loc['BLAZE'], hdict)

        # ----------------------------------------------------------------------
        # Store Flat-field in file
        # ----------------------------------------------------------------------
        # construct filename
        flatfits, tag2 = spirouConfig.Constants.FF_FLAT_FILE(p)
        flatfitsname = os.path.split(flatfits)[-1]
        # log that we are saving blaze file
        wmsg = 'Saving FF spectrum for fiber: {0} in {1}'
        WLOG('', p['LOG_OPT'] + fiber, wmsg.format(fiber, flatfitsname))
        # write 1D list of the RMS (add to hdict from blaze)
        hdict = spirouImage.AddKey(hdict, p['KW_FLATFILE'], value=raw_flat_file)
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag2)
        hdict = spirouImage.AddKey1DList(hdict, p['KW_FLAT_RMS'],
                                         values=loc['RMS'])
        # write center fits and add header keys (via same hdict as blaze)
        p = spirouImage.WriteImage(p, flatfits, loc['FLAT'], hdict)

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

        # get mask for removing certain orders in the RMS calculation
        remove_orders = np.array(p['FF_RMS_PLOT_SKIP_ORDERS'])
        mask = np.in1d(np.arange(len(loc['RMS'])), remove_orders)
        # apply mask and calculate the maximum RMS
        max_rms = np.max(loc['RMS'][~mask])
        # apply the quality control based on the new RMS
        if max_rms > p['QC_FF_RMS']:
            fmsg = 'abnormal RMS of FF ({0:.3f} > {1:.3f})'
            fail_msg.append(fmsg.format(max_rms, p['QC_FF_RMS']))
            passed = False

        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if passed:
            wmsg = 'QUALITY CONTROL SUCCESSFUL - Well Done -'
            WLOG('info', p['LOG_OPT'], wmsg)
            p['QC'] = 1
            p.set_source('QC', __NAME__ + '/main()')
        else:
            for farg in fail_msg:
                wmsg = 'QUALITY CONTROL FAILED: {0}'
                WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
            p['QC'] = 0
            p.set_source('QC', __NAME__ + '/main()')

        # ------------------------------------------------------------------
        # Update the calibration database
        # ------------------------------------------------------------------
        if p['QC'] == 1:
            # copy flatfits to calibdb
            keydb = 'FLAT_' + p['FIBER']
            # copy localisation file to the calibDB folder
            spirouDB.PutCalibFile(p, flatfits)
            # update the master calib DB file with new key
            spirouDB.UpdateCalibMaster(p, keydb, flatfitsname, hdr)
            # copy blazefits to calibdb
            keydb = 'BLAZE_' + p['FIBER']
            # copy localisation file to the calibDB folder
            spirouDB.PutCalibFile(p, blazefits)
            # update the master calib DB file with new key
            spirouDB.UpdateCalibMaster(p, keydb, blazefitsname, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
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

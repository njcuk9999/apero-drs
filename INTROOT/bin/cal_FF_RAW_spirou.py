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
# define ll extract types
EXTRACT_LL_TYPES = ['3c', '3d', '4a', '4b', '5a', '5b']
EXTRACT_SHAPE_TYPES = ['4a', '4b', '5a', '5b']

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
    data = spirouImage.ConvertToADU(spirouImage.FlipImage(p, datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data1 = spirouImage.ResizeImage(p, data0, **bkwargs)
    # log change in data size
    WLOG(p, '', ('Image format changed to '
                 '{0}x{1}').format(*data1.shape[::-1]))
    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    p, data1 = spirouImage.CorrectForBadPix(p, data1, hdr)

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(~np.isfinite(data1))
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data1.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.4f} %'
    WLOG(p, 'info', wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get the miny, maxy and max_signal for the central column
    # ----------------------------------------------------------------------
    # get the central column
    y = data1[p['IC_CENT_COL'], :]
    # get the min max and max signal using box smoothed approach
    miny, maxy, max_signal, diff_maxmin = spirouBACK.MeasureMinMaxSignal(p, y)
    # Log max average flux/pixel
    wmsg = ('Maximum average flux (95th percentile) /pixel in the spectrum: '
            '{0:.1f} [ADU]')
    WLOG(p, 'info', wmsg.format(max_signal / p['NBFRAMES']))

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    # p['ic_bkgr_percent'] = 3.0
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG(p, '', 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bargs = [p, data1, hdr, cdr]
        # background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(*bargs)
        background = spirouBACK.MeasureBackgroundMap(*bargs)
    else:
        background = np.zeros_like(data1)
    # apply background correction to data (and set to zero where negative)
    # TODO: Etienne --> Francois - Cannot set negative flux to zero!
    # data1 = np.where(data1 > 0, data1 - background, 0)
    data1 = data1 - background

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # define loc storage parameter dictionary
    loc = ParamDict()
    # get tilts
    if p['IC_FF_EXTRACT_TYPE'] not in EXTRACT_SHAPE_TYPES:
        p, loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
    else:
        loc['TILT'] = None
    loc.set_source('TILT', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Get all fiber data (for all fibers)
    # ----------------------------------------------------------------------
    # TODO: This is temp solution for options 5a and 5b
    loc_fibers = spirouLOCOR.GetFiberData(p, hdr)

    # ------------------------------------------------------------------
    # Deal with debananafication
    # ------------------------------------------------------------------
    # if mode 4a or 4b we need to straighten in x only
    if p['IC_EXTRACT_TYPE'] in ['4a', '4b']:
        # log progress
        WLOG(p, '', 'Debananafying (straightening) image')
        # get the shape map
        p, shapemap = spirouImage.ReadShapeMap(p, hdr)
        # debananafy data
        bkwargs = dict(image=np.array(data1), kind='full', dx=shapemap)
        data2 = spirouEXTOR.DeBananafication(p, **bkwargs)
    # if mode 5a or 5b we need to straighten in x and y using the
    #     polynomial fits for location
    elif p['IC_EXTRACT_TYPE'] in ['5a', '5b']:
        # log progress
        WLOG(p, '', 'Debananafying (straightening) image')
        # get the shape map
        p, shapemap = spirouImage.ReadShapeMap(p, hdr)
        # get the bad pixel map
        p, badpix = spirouImage.CorrectForBadPix(p, data1, hdr, return_map=True,
                                                 quiet=True)
        # debananafy data
        bkwargs = dict(image=np.array(data1), kind='full', badpix=badpix,
                       dx=shapemap, pos_a=loc_fibers['A']['ACC'],
                       pos_b=loc_fibers['B']['ACC'],
                       pos_c=loc_fibers['C']['ACC'])
        data2 = spirouEXTOR.DeBananafication(p, **bkwargs)
    # in any other mode we do not straighten
    else:
        data2 = np.array(data1)

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
        # Get fiber specific parameters from loc_fibers
        # ------------------------------------------------------------------
        # get this fibers parameters
        p = spirouImage.FiberParams(p, p['FIBER'], merge=True)
        # get localisation parameters
        for key in loc_fibers[fiber]:
            loc[key] = loc_fibers[fiber][key]
            loc.set_source(key, loc_fibers[fiber].sources[key])
        # get locofile source
        p['LOCOFILE'] = loc['LOCOFILE']
        p.set_source('LOCOFILE', loc.sources['LOCOFILE'])
        # get the order_profile
        order_profile = loc_fibers[fiber]['ORDER_PROFILE']

        # ------------------------------------------------------------------
        # Set up Extract storage
        # ------------------------------------------------------------------
        # Create array to store extraction (for each order and each pixel
        # along order)
        loc['E2DS'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        loc['E2DSLL'] = []
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
            # deal with different return
            if p['IC_EXTRACT_TYPE'] in EXTRACT_LL_TYPES:
                e2ds, e2dsll, cpt = eout
            else:
                e2ds, cpt = eout
                e2dsll = None
            # calculate the noise
            range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
            noise = p['SIGDET'] * np.sqrt(range1 + range2)
            # get window size
            blaze_win1 = int(data2.shape[1] / 2) - p['IC_EXTFBLAZ']
            blaze_win2 = int(data2.shape[1] / 2) + p['IC_EXTFBLAZ']
            # get average flux per pixel
            flux = np.nansum(e2ds[blaze_win1:blaze_win2]) / (2 * p['IC_EXTFBLAZ'])
            # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
            snr = flux / np.sqrt(flux + noise ** 2)
            # remove edge of orders at low S/N
            with warnings.catch_warnings(record=True) as _:
                blazemask = e2ds < (flux / p['IC_FRACMINBLAZE'])
                e2ds = np.where(blazemask, np.nan, e2ds)
            #            e2ds = np.where(e2ds < p['IC_MINBLAZE'], 0., e2ds)
            # calcualte the blaze function
            blaze = spirouFLAT.MeasureBlazeForOrder(p, e2ds)
            # calculate the flat
            flat = e2ds / blaze
            # calculate the rms
            rms = np.nanstd(flat)
            # log the SNR RMS
            wmsg = 'On fiber {0} order {1}: S/N= {2:.1f}  - FF rms={3:.2f} %'
            wargs = [fiber, order_num, snr, rms * 100.0]
            WLOG(p, '', wmsg.format(*wargs))
            # add calculations to storage
            loc['E2DS'][order_num] = e2ds
            loc['SNR'][order_num] = snr
            loc['RMS'][order_num] = rms
            loc['BLAZE'][order_num] = blaze
            loc['FLAT'][order_num] = flat
            # save the longfile
            if p['IC_EXTRACT_TYPE'] in EXTRACT_LL_TYPES:
                loc['E2DSLL'].append(e2dsll)
            # set sources
            source = __NAME__ + '/main()()'
            loc.set_sources(['e2ds', 'SNR', 'RMS', 'blaze', 'flat'], source)
            # Log if saturation level reached
            satvalue = (flux / p['GAIN']) / (range1 + range2)
            if satvalue > (p['QC_LOC_FLUMAX'] * p['NBFRAMES']):
                wmsg = 'SATURATION LEVEL REACHED on Fiber {0} order={1}'
                WLOG(p, 'warning', wmsg.format(fiber, order_num))

        # ----------------------------------------------------------------------
        # Plots
        # ----------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            # start interactive session if needed
            sPlt.start_interactive_session(p)
            # plot all orders or one order
            if p['IC_FF_PLOT_ALL_ORDERS']:
                # plot image with all order fits (slower)
                sPlt.ff_aorder_fit_edges(p, loc, data1)
            else:
                # plot image with selected order fit and edge fit (faster)
                sPlt.ff_sorder_fit_edges(p, loc, data1)
            # plot tilt adjusted e2ds and blaze for selected order
            sPlt.ff_sorder_tiltadj_e2ds_blaze(p, loc)
            # plot flat for selected order
            sPlt.ff_sorder_flat(p, loc)
            # plot the RMS for all but skipped orders
            # sPlt.ff_rms_plot(p, loc)

            if p['IC_FF_EXTRACT_TYPE'] in EXTRACT_SHAPE_TYPES:
                sPlt.ff_debanana_plot(p, loc, data2)
        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        passed, fail_msg = True, []
        qc_values, qc_names, qc_logic, qc_pass = [], [], [], []

        # saturation check: check that the max_signal is lower than
        # qc_max_signal
        # if max_signal > (p['QC_MAX_SIGNAL'] * p['nbframes']):
        #     fmsg = 'Too much flux in the image (max authorized={0})'
        #     fail_msg.append(fmsg.format(p['QC_MAX_SIGNAL'] * p['nbframes']))
        #     passed = False
        #     # For some reason this test is ignored in old code
        #     passed = True
        #     WLOG(p, 'info', fail_msg[-1])

        # get mask for removing certain orders in the RMS calculation
        remove_orders = np.array(p['FF_RMS_PLOT_SKIP_ORDERS'])
        mask = np.in1d(np.arange(len(loc['RMS'])), remove_orders)
        # apply mask and calculate the maximum RMS
        max_rms = np.nanmax(loc['RMS'][~mask])
        # apply the quality control based on the new RMS
        if max_rms > p['QC_FF_RMS']:
            fmsg = 'abnormal RMS of FF ({0:.3f} > {1:.3f})'
            fail_msg.append(fmsg.format(max_rms, p['QC_FF_RMS']))
            passed = False
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(max_rms)
        qc_names.append('max_rms')
        qc_logic.append('max_rms > {0:.3f}'.format(p['QC_FF_RMS']))

        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if passed:
            wmsg = 'QUALITY CONTROL SUCCESSFUL - Well Done -'
            WLOG(p, 'info', wmsg)
            p['QC'] = 1
            p.set_source('QC', __NAME__ + '/main()')
        else:
            for farg in fail_msg:
                wmsg = 'QUALITY CONTROL FAILED: {0}'
                WLOG(p, 'warning', wmsg.format(farg))
            p['QC'] = 0
            p.set_source('QC', __NAME__ + '/main()')
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

        # ----------------------------------------------------------------------
        # Store Blaze in file
        # ----------------------------------------------------------------------
        # get raw flat filename
        raw_flat_file = os.path.basename(p['FITSFILENAME'])
        e2dsllfits, tag4 = spirouConfig.Constants.EXTRACT_E2DSLL_FILE(p)
        # get extraction method and function
        efout = spirouEXTOR.GetExtMethod(p, p['IC_FF_EXTRACT_TYPE'])
        extmethod, extfunc = efout
        # construct filename
        blazefits, tag1 = spirouConfig.Constants.FF_BLAZE_FILE(p)
        blazefitsname = os.path.split(blazefits)[-1]
        # log that we are saving blaze file
        wmsg = 'Saving blaze spectrum for fiber: {0} in {1}'
        WLOG(p, '', wmsg.format(fiber, blazefitsname))
        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
        # define new keys to add
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'],
                                   value=p['DARKFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'],
                                   value=p['BADPFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBLOCO'],
                                   value=p['LOCOFILE'])
        if p['IC_EXTRACT_TYPE'] not in EXTRACT_SHAPE_TYPES:
            hdict = spirouImage.AddKey(p, hdict, p['KW_CDBTILT'],
                                       value=p['TILTFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'],
                                   value=raw_flat_file)
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                         dim1name='file',
                                         values=p['ARG_FILE_NAMES'])
        # add some properties back
        hdict = spirouImage.AddKey(p, hdict, p['KW_CCD_SIGDET'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CCD_CONAD'])
        # add qc parameters
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
        hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
        # copy extraction method and function to header
        #     (for reproducibility)
        hdict = spirouImage.AddKey(p, hdict, p['KW_E2DS_EXTM'],
                                   value=extmethod)
        hdict = spirouImage.AddKey(p, hdict, p['KW_E2DS_FUNC'],
                                   value=extfunc)
        # output keys
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        # write 1D list of the SNR
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_EXTRA_SN'],
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
        WLOG(p, '', wmsg.format(fiber, flatfitsname))
        # write 1D list of the RMS (add to hdict from blaze)
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_FLAT_RMS'],
                                         values=loc['RMS'])
        # write center fits and add header keys (via same hdict as blaze)
        p = spirouImage.WriteImage(p, flatfits, loc['FLAT'], hdict)

        # Save E2DSLL file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag4)
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        if p['IC_EXTRACT_TYPE'] in EXTRACT_LL_TYPES:
            llstack = np.vstack(loc['E2DSLL'])
            p = spirouImage.WriteImage(p, e2dsllfits, llstack, hdict)

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

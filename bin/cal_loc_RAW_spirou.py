#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_loc_RAW_spirou.py

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import time

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS.spirouCore import spirouPlot as sPlt

neilstart = time.time()

# =============================================================================
# Define variables
# =============================================================================
# Get Logging function
WLOG = spirouCore.wlog
# Name of program
__NAME__ = 'cal_loc_RAW_spirou.py'
# -----------------------------------------------------------------------------
# whether to use plt.ion or plt.show
INTERACTIVE_PLOTS = spirouConfig.spirouConfig.INTERACTIVE_PLOTS
# Custom parameter dictionary
ParamDict = spirouConfig.ParamDict

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    p = spirouCore.RunInitialStartup()
    # run specific start up
    params2add = dict()
    params2add['dark_flat'] = spirouLOCOR.FiberParams(p, 'C')
    params2add['flat_dark'] = spirouLOCOR.FiberParams(p, 'AB')
    p = spirouCore.RunStartup(p, kind='localisation',
                              prefixes=['dark_flat', 'flat_dark'],
                              add_to_p=params2add, calibdb=True)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = spirouImage.ReadImage(p, framemath='add')
    # get ccd sig det value
    p['ccdsigdet'] = float(spirouImage.GetKey(p, hdr, 'RDNOISE',
                                              hdr['@@@hname']))
    p.set_source('ccdsigdet', __NAME__ + '/__main__')
    # get exposure time
    p['exptime'] = float(spirouImage.GetKey(p, hdr, 'EXPTIME', hdr['@@@hname']))
    p.set_source('exptime', __NAME__ + '/__main__')
    # get gain
    p['gain'] = float(spirouImage.GetKey(p, hdr, 'GAIN', hdr['@@@hname']))
    p.set_source('gain', __NAME__ + '/__main__')

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToE(spirouImage.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], ('Image format changed to '
                            '{0}x{1}').format(*data2.shape))

    # ----------------------------------------------------------------------
    # Construct image order_profile
    # ----------------------------------------------------------------------
    order_profile = spirouLOCOR.BoxSmoothedImage(data2, p['LOC_BOX_SIZE'],
                                                 mode='manual')
    # data 2 is now set to the order profile
    data2o = data2.copy()
    data2 = order_profile.copy()

    # ----------------------------------------------------------------------
    # Write image order_profile to file
    # ----------------------------------------------------------------------
    # Construct folder and filename
    reducedfolder = os.path.join(p['DRS_DATA_REDUC'], p['arg_night_name'])
    newext = '_order_profile_{0}.fits'.format(p['fiber'])
    rawfits = p['arg_file_names'][0].replace('.fits', newext)
    # log saving order profile
    WLOG('', p['log_opt'], 'Saving processed raw frame in {0}'.format(rawfits))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # write to file
    rawpath = os.path.join(reducedfolder, rawfits)
    spirouImage.WriteImage(rawpath, order_profile, hdict)

    # ----------------------------------------------------------------------
    # Move order_profile to calibDB and update calibDB
    # ----------------------------------------------------------------------
    # set key for calibDB
    keydb = 'ORDER_PROFILE_{0}'.format(p['fiber'])
    # copy dark fits file to the calibDB folder
    spirouCDB.PutFile(p, os.path.join(reducedfolder, rawfits))
    # update the master calib DB file with new key
    spirouCDB.UpdateMaster(p, keydb, rawfits, hdr)

    # ######################################################################
    # Localization of orders on central column
    # ######################################################################
    # storage dictionary for localization parameters
    loc = ParamDict()
    # Plots setup: start interactive plot
    if p['DRS_PLOT'] and INTERACTIVE_PLOTS:
        plt.ion()
    # ----------------------------------------------------------------------
    # Measurement and correction of background on the central column
    # ----------------------------------------------------------------------
    loc = spirouLOCOR.MeasureBkgrdGetCentPixs(p, loc, data2)
    # ----------------------------------------------------------------------
    # Search for order center on the central column - quick estimation
    # ----------------------------------------------------------------------
    # log progress
    WLOG('', p['log_opt'], 'Searching order center on central column')
    # plot the minimum of ycc and ic_locseuil if in debug and plot mode
    if p['IC_DEBUG'] and p['DRS_PLOT']:
        sPlt.debug_locplot_min_ycc_loc_threshold(p, loc['ycc'])
    # find the central positions of the orders in the central
    posc_all = spirouLOCOR.FindPosCentCol(loc['ycc'], p['IC_LOCSEUIL'])
    # depending on the fiber type we may need to skip some pixels and also
    # we need to add back on the ic_offset applied
    start = p['IC_FIRST_ORDER_JUMP']
    posc = posc_all[start:] + p['IC_OFFSET']
    # work out the number of orders to use (minimum of ic_locnbmaxo and number
    #    of orders found in 'LocateCentralOrderPositions')
    number_of_orders = np.min([p['IC_LOCNBMAXO'], len(posc)])
    # log the number of orders than have been detected
    wargs = [p['fiber'], int(number_of_orders/p['NBFIB']), p['NBFIB']]
    WLOG('info', p['log_opt'], ('On fiber {0} {1} orders have been detected '
                                'on {2} fiber(s)').format(*wargs))

    # ----------------------------------------------------------------------
    # Search for order center and profile on specific columns
    # ----------------------------------------------------------------------
    # Plot the image (ready for fit points to be overplotted later)
    if p['DRS_PLOT']:
        # get saturation threshold
        satseuil = p['IC_SATSEUIL'] * p['gain'] * p['nbframes']
        # plot image above saturation threshold
        fig1, frame1 = sPlt.locplot_im_sat_threshold(data2o, satseuil)
    else:
        fig1, frame1 = None, None
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # get fit polynomial orders for position and width
    fitpos, fitwid = p['IC_LOCDFITC'], p['IC_LOCDFITW']
    # Create arrays to store position and width of order for each order
    loc['ctro'] = np.zeros((number_of_orders, data2.shape[1]), dtype=float)
    loc['sigo'] = np.zeros((number_of_orders, data2.shape[1]), dtype=float)
    # Create arrays to store coefficients for position and width
    loc['ac'] = np.zeros((number_of_orders, fitpos + 1))
    loc['ass'] = np.zeros((number_of_orders, fitpos + 1))
    # Create arrays to store rms values for position and width
    loc['rms_center'] = np.zeros(number_of_orders)
    loc['rms_fwhm'] = np.zeros(number_of_orders)
    # Create arrays to store point to point max value for position and width
    loc['max_ptp_center'] = np.zeros(number_of_orders)
    loc['max_ptp_fraccenter'] = np.zeros(number_of_orders)
    loc['max_ptp_fwhm'] = np.zeros(number_of_orders)
    loc['max_ptp_fracfwhm'] = np.zeros(number_of_orders)
    # Create arrays to store rejected points
    loc['max_rmpts_pos'] = np.zeros(number_of_orders)
    loc['max_rmpts_wid'] = np.zeros(number_of_orders)
    # set the central col centers in the cpos_orders array
    loc['ctro'][:, p['IC_CENT_COL']] = posc[0:number_of_orders]
    # set source for all locs
    loc.set_all_sources(__NAME__ + '/__main__')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # loop around each order
    rorder_num = 0
    for order_num in range(number_of_orders):
        # find the row centers of the columns
        loc = spirouLOCOR.FindOrderCtrs(p, data2, loc, order_num)
        # only keep the orders with non-zero width
        mask = loc['sigo'][order_num, :] != 0
        loc['x'] = np.arange(data2.shape[1])[mask]
        loc.set_source('x', __NAME__ + '/__main__')
        # check that we have enough data points to fit data
        if len(loc['x']) > (fitpos + 1):
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # initial fit params
            iofargs = [p, loc, mask, order_num, rorder_num]
            # initial fit for center positions for this order
            cf_data = spirouLOCOR.InitialOrderFit(*iofargs, kind='center',
                                                  fig=fig1, frame=frame1)
            # initial fit for widths for this order
            wf_data = spirouLOCOR.InitialOrderFit(*iofargs, kind='fwhm',
                                                  fig=fig1, frame=frame1)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Log order number and fit at central pixel and width and rms
            wargs = [rorder_num, cf_data['cfitval'], wf_data['cfitval'],
                     cf_data['rms']]
            WLOG('', p['log_opt'], ('ORDER: {0} center at pixel {1:.1f} width '
                                    '{2:.1f} rms {3:.3f}').format(*wargs))
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # sigma fit params
            sigfargs = [p, loc, cf_data, mask, order_num, rorder_num]
            # sigma clip fit for center positions for this order
            cf_data = spirouLOCOR.SigClipOrderFit(*sigfargs, kind='center')
            # load results into storage arrags for this order
            loc['ac'][rorder_num] = cf_data['a']
            loc['rms_center'][rorder_num] = cf_data['rms']
            loc['max_ptp_center'][rorder_num] = cf_data['max_ptp']
            loc['max_ptp_fraccenter'][rorder_num] = cf_data['max_ptp_frac']
            loc['max_rmpts_pos'][rorder_num] = cf_data['max_rmpts']
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # sigma fit params
            sigfargs = [p, loc, cf_data, mask, order_num, rorder_num]
            # sigma clip fit for width positions for this order
            wf_data = spirouLOCOR.SigClipOrderFit(*sigfargs, kind='fwhm')
            # load results into storage arrags for this order
            loc['ass'][rorder_num] = wf_data['a']
            loc['rms_fwhm'][rorder_num] = wf_data['rms']
            loc['max_ptp_fwhm'][rorder_num] = wf_data['max_ptp']
            loc['max_ptp_fracfwhm'][rorder_num] = wf_data['max_ptp_frac']
            loc['max_rmpts_wid'][rorder_num] = wf_data['max_rmpts']
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # increase the roder_num iterator
            rorder_num += 1
        # else log that the order is unusable
        else:
            WLOG('', p['log_opt'], 'Order found too much incomplete, discarded')

    # Log that order geometry has been measured
    WLOG('info', p['log_opt'], ('On fiber {0} {1} orders geometry have been '
                                'measured').format(p['fiber'], rorder_num))
    # Get mean rms
    mean_rms_center = np.sum(loc['rms_center'][:rorder_num]) * 1000/rorder_num
    mean_rms_fwhm = np.sum(loc['rms_fwhm'][:rorder_num]) * 1000/rorder_num
    # Log mean rms values
    wmsg = 'Average uncertainty on {0}: {1:.2f} [mpix]'
    WLOG('info', p['log_opt'], wmsg.format('position', mean_rms_center))
    WLOG('info', p['log_opt'], wmsg.format('width', mean_rms_fwhm))

    # ----------------------------------------------------------------------
    # Plot of RMS for positions and widths
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        sPlt.locplot_order_number_against_rms(p, loc, rorder_num)

    # ----------------------------------------------------------------------
    # Save and record of image of localization with order center and keywords
    # ----------------------------------------------------------------------

    # construct filename
    locoext = '_loco_{0}.fits'.format(p['fiber'])
    locofits = p['arg_file_names'][0].replace('.fits', locoext)

    # log that we are saving localization file
    WLOG('', p['log_opt'], ('Saving localization information '
                            'in file: {0}').format(locofits))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict = spirouImage.AddKey(hdict, p['kw_version'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCD_SIGDET'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCD_CONAD'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_BCKGRD'],
                               value=loc['mean_backgrd'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_NBO'],
                               value=rorder_num)
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_DEG_C'],
                               value=p['IC_LOCDFITC'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_DEG_W'],
                               value=p['IC_LOCDFITW'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_DEG_E'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_DELTA'])

    hdict = spirouImage.AddKey(hdict, p['kw_LOC_MAXFLX'],
                               value=float(loc['max_signal']))
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_SMAXPTS_CTR'],
                               value=np.sum(loc['max_rmpts_pos']))
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_SMAXPTS_WID'],
                               value=np.sum(loc['max_rmpts_wid']))
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_RMS_CTR'],
                               value=mean_rms_center)
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_RMS_WID'],
                               value=mean_rms_fwhm)
    # write 2D list of position fit coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['kw_LOCO_CTR_COEFF'],
                                     values=loc['ac'][0:rorder_num])
    # write 2D list of width fit coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['kw_LOCO_FWHM_COEFF'],
                                     values=loc['ass'][0:rorder_num])
    # write image and add header keys (via hdict)
    spirouImage.WriteImage(os.path.join(reducedfolder, locofits),
                           loc['ac'][0:rorder_num], hdict)

    # ----------------------------------------------------------------------
    # Save and record of image of sigma
    # ----------------------------------------------------------------------
    # construct filename
    locoext = '_fwhm-order_{0}.fits'.format(p['fiber'])
    locofits2 = p['arg_file_names'][0].replace('.fits', locoext)

    # log that we are saving localization file
    WLOG('', p['log_opt'], ('Saving FWHM information '
                            'in file: {0}').format(locofits))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # define new keys to add
    hdict = spirouImage.AddKey(hdict, p['kw_version'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCD_SIGDET'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCD_CONAD'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_BCKGRD'],
                               value=loc['mean_backgrd'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_NBO'],
                               value=rorder_num)
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_DEG_C'],
                               value=p['IC_LOCDFITC'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_DEG_W'],
                               value=p['IC_LOCDFITW'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOCO_DEG_E'])
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_MAXFLX'],
                               value=float(loc['max_signal']))
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_SMAXPTS_CTR'],
                               value=np.sum(loc['max_rmpts_pos']))
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_SMAXPTS_WID'],
                               value=np.sum(loc['max_rmpts_wid']))
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_RMS_CTR'],
                               value=mean_rms_center)
    hdict = spirouImage.AddKey(hdict, p['kw_LOC_RMS_WID'],
                               value=mean_rms_fwhm)
    # write 2D list of position fit coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['kw_LOCO_CTR_COEFF'],
                                     values=loc['ac'][0:rorder_num])
    # write 2D list of width fit coefficients
    hdict = spirouImage.AddKey2DList(hdict, p['kw_LOCO_FWHM_COEFF'],
                                     values=loc['ass'][0:rorder_num])
    # write image and add header keys (via hdict)
    spirouImage.WriteImage(os.path.join(reducedfolder, locofits),
                           loc['ass'][0:rorder_num], hdict)

    # ----------------------------------------------------------------------
    # Save and Record of image of localization
    # ----------------------------------------------------------------------
    if p['IC_LOCOPT1']:
        # construct filename
        locoext = '_with-order_{0}.fits'.format(p['fiber'])
        locofits3 = p['arg_file_names'][0].replace('.fits', locoext)
        # log that we are saving localization file
        WLOG('', p['log_opt'], ('Saving localization image with superposition '
                                'of orders in file: {0}').format(locofits))
        # superpose zeros over the fit in the image
        data4 = spirouLOCOR.imageLocSuperimp(data2o, loc['ac'][0:rorder_num])
        # save this image to file
        spirouImage.WriteImage(os.path.join(reducedfolder, locofits3), data4,
                               hdict)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    # check that max number of points rejected in center fit is below threshold
    if np.sum(loc['max_rmpts_pos']) > p['QC_LOC_MAXLOCFIT_REMOVED_CTR']:
        fmsg = 'abnormal points rejection during ctr fit ({0} > {1})'
        fail_msg.append(fmsg.format(np.sum(loc['max_rmpts_pos']),
                                    p['QC_LOC_MAXLOCFIT_REMOVED_CTR']))
        passed = False
    # check that max number of points rejected in width fit is below threshold
    if np.sum(loc['max_rmpts_wid']) > p['QC_LOC_MAXLOCFIT_REMOVED_WID']:
        fmsg = 'abnormal points rejection during width fit ({0} > {1})'
        fail_msg.append(fmsg.format(np.sum(loc['max_rmpts_wid']),
                                    p['QC_LOC_MAXLOCFIT_REMOVED_WID']))
        passed = False
    # check that the rms in center fit is lower than qc threshold
    if mean_rms_center > p['QC_LOC_RMSMAX_CENTER']:
        fmsg = 'too high rms on center fitting ({0} > {1})'
        fail_msg.append(fmsg.format(mean_rms_center, p['QC_LOC_RMSMAX_CENTER']))
        passed = False
    # check that the rms in center fit is lower than qc threshold
    if mean_rms_center > p['QC_LOC_RMSMAX_FWHM']:
        fmsg = 'too high rms on profile fwhm fitting ({0} > {1})'
        fail_msg.append(fmsg.format(mean_rms_center, p['QC_LOC_RMSMAX_CENTER']))
        passed = False
    # check for abnormal number of identified orders
    if rorder_num != p['QC_LOC_NBO']:
        fmsg = 'abnormal number of identified orders (found {0} expected {1})'
        fail_msg.append(fmsg.format(rorder_num, p['QC_LOC_NBO']))
        passed = False
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['log_opt'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/__main__')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('info', p['log_opt'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/__main__')

    # ----------------------------------------------------------------------
    # Update the calibration database
    # ----------------------------------------------------------------------
    if p['QC'] == 1:
        keydb = 'LOC_' + p['fiber']
        # copy localisation file to the calibDB folder
        spirouCDB.PutFile(p, os.path.join(reducedfolder, locofits))
        # update the master calib DB file with new key
        spirouCDB.UpdateMaster(p, keydb, locofits, hdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                '').format(p['program']))

    neilend = time.time()
    print('Time taken (py3) = {0}'.format(neilend-neilstart))

# =============================================================================
# End of code
# =============================================================================

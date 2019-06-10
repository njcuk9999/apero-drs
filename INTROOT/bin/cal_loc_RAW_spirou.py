#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_loc_RAW_spirou.py [night_name] [files]

Localisation of orders (centers and widths) on the dark_flat or flat_dark
images

Created on 2017-10-12 at 15:21

@author: cook

Last modified: 2017-12-11 at 15:09

Up-to-date with cal_loc_RAW_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouBACK
from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Name of program
__NAME__ = 'cal_loc_RAW_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
__args__ = ['night_name', 'files']
__required__ = [True, True]
# Custom parameter dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    """
    cal_loc_RAW_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_loc_RAW_spirou.py [night_name] [files]

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

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, data, hdr = spirouImage.ReadImageAndCombine(p, framemath='add')

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

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    p, datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    #  Interpolation over bad regions (to fill in the holes)
    # ----------------------------------------------------------------------
    # log process
    # wmsg = 'Interpolating over bad regions'
    # WLOG(p, '', wmsg)
    # run interpolation
    # datac = spirouImage.InterpolateBadRegions(p, datac)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    data = spirouImage.ConvertToE(spirouImage.FlipImage(p, datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(p, data0, **bkwargs)
    # log change in data size
    WLOG(p, '', ('Image format changed to '
                            '{0}x{1}').format(*data2.shape))

    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    p, data2 = spirouImage.CorrectForBadPix(p, data2, hdr)

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG(p, '', 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bargs = [p, data2, hdr]
        # background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(*bargs)
        p, background = spirouBACK.MeasureBackgroundMap(*bargs)
    else:
        background = np.zeros_like(data2)
        p['BKGRDFILE'] = 'None'
        p.set_source('BKGRDFILE', __NAME__ + '.main()')
    # apply background correction to data
    data2 = data2 - background

    # ----------------------------------------------------------------------
    # Construct image order_profile
    # ----------------------------------------------------------------------
    # log that we are doing background measurement
    WLOG(p, '', 'Creating Order Profile')
    order_profile = spirouLOCOR.BoxSmoothedImage(data2, p['LOC_BOX_SIZE'])
    # data 2 is now set to the order profile
    data2o = data2.copy()
    data2 = order_profile.copy()

    # ----------------------------------------------------------------------
    # Write image order_profile to file
    # ----------------------------------------------------------------------
    # Construct folder and filename
    rawfits, tag1 = spirouConfig.Constants.LOC_ORDER_PROFILE_FILE(p)
    rawfitsname = os.path.split(rawfits)[-1]
    # log saving order profile
    wmsg = 'Saving processed raw frame in {0}'
    WLOG(p, '', wmsg.format(rawfitsname))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'], value=p['DARKFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'], value=p['BADPFILE'])
    # write to file
    p = spirouImage.WriteImage(p, rawfits, order_profile, hdict)

    # ----------------------------------------------------------------------
    # Move order_profile to calibDB and update calibDB
    # ----------------------------------------------------------------------
    # set key for calibDB
    keydb = 'ORDER_PROFILE_{0}'.format(p['FIBER'])
    # copy dark fits file to the calibDB folder
    spirouDB.PutCalibFile(p, rawfits)
    # update the master calib DB file with new key
    spirouDB.UpdateCalibMaster(p, keydb, rawfitsname, hdr)

    # ######################################################################
    # Localization of orders on central column
    # ######################################################################
    # storage dictionary for localization parameters
    loc = ParamDict()
    # Plots setup: start interactive plot
    if p['DRS_PLOT'] > 0:
        sPlt.start_interactive_session(p)
    # ----------------------------------------------------------------------
    # Measurement and correction of background on the central column
    # ----------------------------------------------------------------------
    loc = spirouBACK.MeasureBkgrdGetCentPixs(p, loc, data2)
    # ----------------------------------------------------------------------
    # Search for order center on the central column - quick estimation
    # ----------------------------------------------------------------------
    # log progress
    WLOG(p, '', 'Searching order center on central column')
    # plot the minimum of ycc and ic_locseuil if in debug and plot mode
    if p['DRS_DEBUG'] > 0 and p['DRS_PLOT']:
        sPlt.debug_locplot_min_ycc_loc_threshold(p, loc['YCC'])
    # find the central positions of the orders in the central
    posc_all = spirouLOCOR.FindPosCentCol(loc['YCC'], p['IC_LOCSEUIL'])
    # depending on the fiber type we may need to skip some pixels and also
    # we need to add back on the ic_offset applied
    start = p['IC_FIRST_ORDER_JUMP']
    posc = posc_all[start:] + p['IC_OFFSET']
    # work out the number of orders to use (minimum of ic_locnbmaxo and number
    #    of orders found in 'LocateCentralOrderPositions')
    number_of_orders = np.min([p['IC_LOCNBMAXO'], len(posc)])
    # log the number of orders than have been detected
    wargs = [p['FIBER'], int(number_of_orders/p['NBFIB']), p['NBFIB']]
    WLOG(p, 'info', ('On fiber {0} {1} orders have been detected '
                                'on {2} fiber(s)').format(*wargs))

    # ----------------------------------------------------------------------
    # Search for order center and profile on specific columns
    # ----------------------------------------------------------------------
    # get fit polynomial orders for position and width
    fitpos, fitwid = p['IC_LOCDFITC'], p['IC_LOCDFITW']
    # Create arrays to store position and width of order for each order
    loc['CTRO'] = np.zeros((number_of_orders, data2.shape[1]), dtype=float)
    loc['SIGO'] = np.zeros((number_of_orders, data2.shape[1]), dtype=float)
    # Create arrays to store coefficients for position and width
    loc['ACC'] = np.zeros((number_of_orders, fitpos + 1))
    loc['ASS'] = np.zeros((number_of_orders, fitpos + 1))
    # Create arrays to store rms values for position and width
    loc['RMS_CENTER'] = np.zeros(number_of_orders)
    loc['RMS_FWHM'] = np.zeros(number_of_orders)
    # Create arrays to store point to point max value for position and width
    loc['MAX_PTP_CENTER'] = np.zeros(number_of_orders)
    loc['MAX_PTP_FRACCENTER'] = np.zeros(number_of_orders)
    loc['MAX_PTP_FWHM'] = np.zeros(number_of_orders)
    loc['MAX_PTP_FRACFWHM'] = np.zeros(number_of_orders)
    # Create arrays to store rejected points
    loc['MAX_RMPTS_POS'] = np.zeros(number_of_orders)
    loc['MAX_RMPTS_WID'] = np.zeros(number_of_orders)
    # set the central col centers in the cpos_orders array
    loc['CTRO'][:, p['IC_CENT_COL']] = posc[0:number_of_orders]
    # set source for all locs
    loc.set_all_sources(__NAME__ + '/main()')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # storage for plotting
    loc['XPLOT'], loc['YPLOT'] = [], []
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # loop around each order
    rorder_num = 0
    for order_num in range(number_of_orders):
        # find the row centers of the columns
        loc = spirouLOCOR.FindOrderCtrs(p, data2, loc, order_num)
        # only keep the orders with non-zero width
        mask = loc['SIGO'][order_num, :] != 0
        loc['X'] = np.arange(data2.shape[1])[mask]
        loc.set_source('X', __NAME__ + '/main()')
        # check that we have enough data points to fit data
        if len(loc['X']) > (fitpos + 1):
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # initial fit params
            iofargs = [p, loc, mask, rorder_num]
            # initial fit for center positions for this order
            loc, cf_data = spirouLOCOR.InitialOrderFit(*iofargs, kind='center')
            # initial fit for widths for this order
            loc, wf_data = spirouLOCOR.InitialOrderFit(*iofargs, kind='fwhm')
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Log order number and fit at central pixel and width and rms
            wargs = [rorder_num, cf_data['cfitval'], wf_data['cfitval'],
                     cf_data['rms']]
            WLOG(p, '', ('ORDER: {0} center at pixel {1:.1f} width '
                                    '{2:.1f} rms {3:.3f}').format(*wargs))
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # sigma fit params
            sigfargs = [p, loc, cf_data, mask, order_num, rorder_num]
            # sigma clip fit for center positions for this order
            cf_data = spirouLOCOR.SigClipOrderFit(*sigfargs, kind='center')
            # load results into storage arrags for this order
            loc['ACC'][rorder_num] = cf_data['a']
            loc['RMS_CENTER'][rorder_num] = cf_data['rms']
            loc['MAX_PTP_CENTER'][rorder_num] = cf_data['max_ptp']
            loc['MAX_PTP_FRACCENTER'][rorder_num] = cf_data['max_ptp_frac']
            loc['MAX_RMPTS_POS'][rorder_num] = cf_data['max_rmpts']

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # sigma fit params
            sigfargs = [p, loc, wf_data, mask, order_num, rorder_num]
            # sigma clip fit for width positions for this order
            wf_data = spirouLOCOR.SigClipOrderFit(*sigfargs, kind='fwhm')
            # load results into storage arrags for this order
            loc['ASS'][rorder_num] = wf_data['a']
            loc['RMS_FWHM'][rorder_num] = wf_data['rms']
            loc['MAX_PTP_FWHM'][rorder_num] = wf_data['max_ptp']
            loc['MAX_PTP_FRACFWHM'][rorder_num] = wf_data['max_ptp_frac']
            loc['MAX_RMPTS_WID'][rorder_num] = wf_data['max_rmpts']
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # increase the roder_num iterator
            rorder_num += 1
        # else log that the order is unusable
        else:
            WLOG(p, '', 'Order found too much incomplete, discarded')
    # ----------------------------------------------------------------------
    # Plot the image (ready for fit points to be overplotted later)
    if p['DRS_PLOT'] > 0:
        # get saturation threshold
        satseuil = p['IC_SATSEUIL'] * p['GAIN'] * p['NBFRAMES']
        # plot image above saturation threshold
        sPlt.locplot_im_sat_threshold(p, loc, data2, satseuil)
    # ----------------------------------------------------------------------

    # Log that order geometry has been measured
    WLOG(p, 'info', ('On fiber {0} {1} orders geometry have been '
                                'measured').format(p['FIBER'], rorder_num))
    # Get mean rms
    mean_rms_center = np.nansum(loc['RMS_CENTER'][:rorder_num]) * 1000/rorder_num
    mean_rms_fwhm = np.nansum(loc['RMS_FWHM'][:rorder_num]) * 1000/rorder_num
    # Log mean rms values
    wmsg = 'Average uncertainty on {0}: {1:.2f} [mpix]'
    WLOG(p, 'info', wmsg.format('position', mean_rms_center))
    WLOG(p, 'info', wmsg.format('width', mean_rms_fwhm))

    # ----------------------------------------------------------------------
    # Plot of RMS for positions and widths
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        sPlt.locplot_order_number_against_rms(p, loc, rorder_num)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
    # check that max number of points rejected in center fit is below threshold
    if np.nansum(loc['MAX_RMPTS_POS']) > p['QC_LOC_MAXLOCFIT_REMOVED_CTR']:
        fmsg = 'abnormal points rejection during ctr fit ({0:.2f} > {1:.2f})'
        fail_msg.append(fmsg.format(np.nansum(loc['MAX_RMPTS_POS']),
                                    p['QC_LOC_MAXLOCFIT_REMOVED_CTR']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(np.nansum(loc['MAX_RMPTS_POS']))
    qc_names.append('sum(MAX_RMPTS_POS)')
    qc_logic.append('sum(MAX_RMPTS_POS) > {0:.2f}'
                    ''.format(p['QC_LOC_MAXLOCFIT_REMOVED_CTR']))
    # ----------------------------------------------------------------------
    # check that max number of points rejected in width fit is below threshold
    if np.nansum(loc['MAX_RMPTS_WID']) > p['QC_LOC_MAXLOCFIT_REMOVED_WID']:
        fmsg = 'abnormal points rejection during width fit ({0:.2f} > {1:.2f})'
        fail_msg.append(fmsg.format(np.nansum(loc['MAX_RMPTS_WID']),
                                    p['QC_LOC_MAXLOCFIT_REMOVED_WID']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(np.nansum(loc['MAX_RMPTS_WID']))
    qc_names.append('sum(MAX_RMPTS_WID)')
    qc_logic.append('sum(MAX_RMPTS_WID) > {0:.2f}'
                    ''.format(p['QC_LOC_MAXLOCFIT_REMOVED_WID']))
    # ----------------------------------------------------------------------
    # check that the rms in center fit is lower than qc threshold
    if mean_rms_center > p['QC_LOC_RMSMAX_CENTER']:
        fmsg = 'too high rms on center fitting ({0:.2f} > {1:.2f})'
        fail_msg.append(fmsg.format(mean_rms_center, p['QC_LOC_RMSMAX_CENTER']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mean_rms_center)
    qc_names.append('mean_rms_center')
    qc_logic.append('mean_rms_center > {0:.2f}'
                    ''.format(p['QC_LOC_RMSMAX_CENTER']))
    # ----------------------------------------------------------------------
    # check that the rms in center fit is lower than qc threshold
    if mean_rms_fwhm > p['QC_LOC_RMSMAX_FWHM']:
        fmsg = 'too high rms on profile fwhm fitting ({0:.2f} > {1:.2f})'
        fail_msg.append(fmsg.format(mean_rms_fwhm, p['QC_LOC_RMSMAX_CENTER']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(mean_rms_fwhm)
    qc_names.append('mean_rms_fwhm')
    qc_logic.append('mean_rms_fwhm > {0:.2f}'
                    ''.format(p['QC_LOC_RMSMAX_CENTER']))
    # ----------------------------------------------------------------------
    # check for abnormal number of identified orders
    if rorder_num != p['QC_LOC_NBO']:
        fmsg = ('abnormal number of identified orders (found {0:.2f} '
                'expected {1:.2f})')
        fail_msg.append(fmsg.format(rorder_num, p['QC_LOC_NBO']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(rorder_num)
    qc_names.append('rorder_num')
    qc_logic.append('rorder_num != {0:.2f}'.format(p['QC_LOC_NBO']))
    # ----------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG(p, 'info', 'QUALITY CONTROL SUCCESSFUL - Well Done -')
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
    # Save and record of image of localization with order center and keywords
    # ----------------------------------------------------------------------
    raw_loco_file = os.path.basename(p['FITSFILENAME'])
    # construct filename
    locofits, tag2 = spirouConfig.Constants.LOC_LOCO_FILE(p)
    locofitsname = os.path.split(locofits)[-1]
    # log that we are saving localization file
    WLOG(p, '', ('Saving localization information '
                            'in file: {0}').format(locofitsname))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    # define new keys to add
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'], value=p['DARKFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'], value=p['BADPFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBLOCO'], value=raw_loco_file)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCD_SIGDET'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCD_CONAD'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_BCKGRD'],
                               value=loc['MEAN_BACKGRD'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_NBO'],
                               value=rorder_num)
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_DEG_C'],
                               value=p['IC_LOCDFITC'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_DEG_W'],
                               value=p['IC_LOCDFITW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_DEG_E'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_DELTA'])

    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_MAXFLX'],
                               value=float(loc['MAX_SIGNAL']))
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_SMAXPTS_CTR'],
                               value=np.nansum(loc['MAX_RMPTS_POS']))
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_SMAXPTS_WID'],
                               value=np.nansum(loc['MAX_RMPTS_WID']))
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_RMS_CTR'],
                               value=mean_rms_center)
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_RMS_WID'],
                               value=mean_rms_fwhm)
    # write 2D list of position fit coefficients
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_LOCO_CTR_COEFF'],
                                     values=loc['ACC'][0:rorder_num])
    # write 2D list of width fit coefficients
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_LOCO_FWHM_COEFF'],
                                     values=loc['ASS'][0:rorder_num])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # write center fits and add header keys (via hdict)
    center_fits = spirouLOCOR.CalcLocoFits(loc['ACC'], data2.shape[1])
    p = spirouImage.WriteImage(p, locofits, center_fits, hdict)

    # ----------------------------------------------------------------------
    # Save and record of image of sigma
    # ----------------------------------------------------------------------
    # construct filename
    locofits2, tag3 = spirouConfig.Constants.LOC_LOCO_FILE2(p)
    locofits2name = os.path.split(locofits2)[-1]

    # log that we are saving localization file
    wmsg = 'Saving FWHM information in file: {0}'
    WLOG(p, '', wmsg.format(locofits2name))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr)
    # define new keys to add
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'], value=p['DARKFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'], value=p['BADPFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBACK'],
                               value=p['BKGRDFILE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['ARG_FILE_NAMES'])
    # add outputs
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCD_SIGDET'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCD_CONAD'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_NBO'],
                               value=rorder_num)
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_DEG_C'],
                               value=p['IC_LOCDFITC'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_DEG_W'],
                               value=p['IC_LOCDFITW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_DEG_E'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_MAXFLX'],
                               value=float(loc['MAX_SIGNAL']))
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_SMAXPTS_CTR'],
                               value=np.nansum(loc['MAX_RMPTS_POS']))
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_SMAXPTS_WID'],
                               value=np.nansum(loc['MAX_RMPTS_WID']))
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_RMS_CTR'],
                               value=mean_rms_center)
    hdict = spirouImage.AddKey(p, hdict, p['KW_LOC_RMS_WID'],
                               value=mean_rms_fwhm)
    # write 2D list of position fit coefficients
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_LOCO_CTR_COEFF'],
                                     values=loc['ACC'][0:rorder_num])
    # write 2D list of width fit coefficients
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_LOCO_FWHM_COEFF'],
                                     values=loc['ASS'][0:rorder_num])
    # add quality control
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    # write image and add header keys (via hdict)
    width_fits = spirouLOCOR.CalcLocoFits(loc['ASS'], data2.shape[1])
    p = spirouImage.WriteImage(p, locofits2, width_fits, hdict)

    # ----------------------------------------------------------------------
    # Save and Record of image of localization
    # ----------------------------------------------------------------------
    if p['IC_LOCOPT1']:
        # construct filename
        locofits3, tag4 = spirouConfig.Constants.LOC_LOCO_FILE3(p)
        locofits3name = os.path.split(locofits3)[-1]
        # log that we are saving localization file
        wmsg1 = 'Saving localization image with superposition of orders in '
        wmsg2 = 'file: {0}'.format(locofits3name)
        WLOG(p, '', [wmsg1, wmsg2])
        # superpose zeros over the fit in the image
        data4 = spirouLOCOR.ImageLocSuperimp(data2o, loc['ACC'][0:rorder_num])
        # save this image to file
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'],
                                   value=p['DRS_DATE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'],
                                   value=p['DATE_NOW'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_FIBER'], value=p['FIBER'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag4)
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBDARK'],
                                   value=p['DARKFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'],
                                   value=p['BADPFILE'])
        p = spirouImage.WriteImage(p, locofits3, data4, hdict)

    # ----------------------------------------------------------------------
    # Update the calibration database
    # ----------------------------------------------------------------------
    if p['QC'] == 1:
        keydb = 'LOC_' + p['FIBER']
        # copy localisation file to the calibDB folder
        spirouDB.PutCalibFile(p, locofits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, locofitsname, hdr)

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

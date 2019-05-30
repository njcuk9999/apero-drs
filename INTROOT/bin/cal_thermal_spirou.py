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
__NAME__ = 'cal_thermal_spirou.py'
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

if True:


    import matplotlib.pyplot as plt
    from astropy.io import fits 
    night_name = '2018-08-05'
    files = ['2295507d_pp.fits','2295508d_pp.fits','2295509d_pp.fits','2295656d_pp.fits','2295657d_pp.fits','2295658d_pp.fits']

    outname = '/spirou/sandbox/thermal_demo.fits'


    #def main(night_name=None, files=None):
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
    #p, datac = spirouImage.CorrectForDark(p, data, hdr)
    datac = np.array(data)
        
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
        
        e2ds_all = []
        e2dsll_all = []
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
            e2ds_all.append(e2ds)
            e2dsll_all.append(e2dsll)

        e2ds_all = np.array(e2ds_all)
        e2dsll_all = np.vstack(e2dsll_all)

        fits.writeto(outname,e2ds_all,overwrite=True)
        #plt.figure()
        #plt.imshow(e2dsll_all)
        #plt.title('Fiber {0}'.format(fiber))
        


        """
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

	"""
        """
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
	"""

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    #return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
"""
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)
"""
# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_DRIFT_E2DS_spirou.py [night_directory] [files]

Extracts orders for specific fibers and files.

Created on 2017-10-12 at 15:21

@author: cook

Last modified: 2017-12-11 at 15:12

Up-to-date with cal_extract_RAW_spirouALL AT-4 V47
"""
from __future__ import division
import numpy as np
import os
import time

from SpirouDRS import spirouBACK
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouEXTOR
from SpirouDRS import spirouImage
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_extract_RAW_spirou.py'
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
def main(night_name=None, files=None, fiber_type=None, **kwargs):
    """
    cal_DRIFT_E2DS_spirou.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_DRIFT_E2DS_spirou.py [night_directory] [files]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)
    :param fiber_type: string, if None does all fiber types (defined in
                       constants_SPIROU FIBER_TYPES (default is AB, A, B, C
                       if defined then only does this fiber type (but must
                       be in FIBER_TYPES)
    :param kwargs: any keyword to overwrite constant in param dict "p"

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, kind=None, calibdb=True)
    # log processing image type
    p['DPRTYPE'] = spirouImage.GetTypeFromHeader(p, p['KW_DPRTYPE'])
    p.set_source('DPRTYPE', __NAME__ + '/main()')
    wmsg = 'Now processing Image TYPE {0} with {1} recipe'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['DPRTYPE'], p['PROGRAM']))
    # deal with fiber type
    if fiber_type is None:
        fiber_type = p['FIBER_TYPES']
    if type(fiber_type) == str:
        if fiber_type.upper() == 'ALL':
            fiber_type = p['FIBER_TYPES']
        elif fiber_type in p['FIBER_TYPES']:
            fiber_type = [fiber_type]
        else:
            emsg = 'fiber_type="{0}" not understood'
            WLOG('error', p['LOG_OPT'], emsg.format(fiber_type))
    # set fiber type
    p['FIB_TYPE'] = fiber_type
    p.set_source('FIB_TYPE', __NAME__ + '__main__()')

    # Overwrite keys from source
    for kwarg in kwargs:
        p[kwarg] = kwargs[kwarg]

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
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # now change the value of sigdet if require
    if p['IC_EXT_SIGDET'] > 0:
        p['SIGDET'] = float(p['IC_EXT_SIGDET'])

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to ADU
    data = spirouImage.ConvertToADU(spirouImage.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data2 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    wmsg = 'Image format changed to {1}x{0}'
    WLOG('', p['LOG_OPT'], wmsg.format(*data2.shape))

    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    # TODO: Remove H2RG compatibility
    if p['IC_IMAGE_TYPE'] == 'H4RG':
        data2 = spirouImage.CorrectForBadPix(p, data2, hdr)

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
        background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(p, data2)
    else:
        background = np.zeros_like(data2)

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # define loc storage parameter dictionary
    loc = ParamDict()
    # get tilts
    loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('TILT', __NAME__ + '/main() + /spirouImage.ReadTiltFile')

    # ----------------------------------------------------------------------
    # Fiber loop
    # ----------------------------------------------------------------------
    # loop around fiber types
    for fiber in p['FIB_TYPE']:
        # set fiber
        p['FIBER'] = fiber
        p.set_source('FIBER', __NAME__ + '/main()()')

        # ------------------------------------------------------------------
        # Read wavelength solution
        # ------------------------------------------------------------------
        # TODO: Remove H2RG dependency
        if p['IC_IMAGE_TYPE'] == 'H2RG':
            loc['WAVE'] = spirouImage.ReadWaveFile(p, hdr)
        else:
            loc['WAVE'] = None
        loc.set_source('WAVE', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

        # ------------------------------------------------------------------
        # Get localisation coefficients
        # ------------------------------------------------------------------
        # get this fibers parameters
        p = spirouLOCOR.FiberParams(p, p['FIBER'], merge=True)
        # get localisation fit coefficients
        loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
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
        loc['E2DS'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        loc['SPE1'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        loc['SPE3'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        loc['SPE4'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        loc['SPE5'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        # Create array to store the signal to noise ratios for each order
        loc['SNR'] = np.zeros(loc['NUMBER_ORDERS'])

        # ------------------------------------------------------------------
        # Extract orders
        # ------------------------------------------------------------------
        # source for parameter dictionary
        source = __NAME__ + '/main()'
        # get limits of order extraction
        valid_orders = spirouEXTOR.GetValidOrders(p, loc)
        # loop around each order
        for order_num in valid_orders:
            # -------------------------------------------------------------
            # IC_EXTRACT_TYPE decides the extraction routine
            # -------------------------------------------------------------
            eargs = [p, loc, data2, order_num]
            ekwargs = dict(mode=p['IC_EXTRACT_TYPE'],
                           order_profile=order_profile)
            e2ds, cpt = spirouEXTOR.Extraction(*eargs, **ekwargs)
            # -------------------------------------------------------------
            # calculate the noise
            range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
            # set the noise
            noise = p['SIGDET'] * np.sqrt(range1 + range2)
            # get window size
            blaze_win1 = int(data2.shape[0]/2) - p['IC_EXTFBLAZ']
            blaze_win2 = int(data2.shape[0]/2) + p['IC_EXTFBLAZ']
            # get average flux per pixel
            flux = np.sum(e2ds[blaze_win1:blaze_win2]) / (2*p['IC_EXTFBLAZ'])
            # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
            snr = flux / np.sqrt(flux + noise**2)
            # log the SNR RMS
            wmsg = 'On fiber {0} order {1}: S/N= {2:.1f} Nbcosmic= {3}'
            wargs = [p['FIBER'], order_num, snr, cpt]
            WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
            # add calculations to storage
            loc['E2DS'][order_num] = e2ds
            loc['SNR'][order_num] = snr
            # set sources
            loc.set_sources(['e2ds', 'SNR'], source)
            # Log if saturation level reached
            satvalue = (flux/p['GAIN'])/(range1 + range2)
            if satvalue > (p['QC_LOC_FLUMAX'] * p['NBFRAMES']):
                wmsg = 'SATURATION LEVEL REACHED on Fiber {0}'
                WLOG('warning', p['LOG_OPT'], wmsg.format(fiber))

        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        if p['DRS_PLOT']:
            # start interactive session if needed
            sPlt.start_interactive_session()
            # plot all orders or one order
            if p['IC_FF_PLOT_ALL_ORDERS']:
                # plot image with all order fits (slower)
                sPlt.ext_aorder_fit(p, loc, data2)
            else:
                # plot image with selected order fit and edge fit (faster)
                sPlt.ext_sorder_fit(p, loc, data2)
            # plot e2ds against wavelength
            sPlt.ext_spectral_order_plot(p, loc)

        # ------------------------------------------------------------------
        # Store extraction in file(s)
        # ------------------------------------------------------------------
        # get extraction method and function
        extmethod, extfunc = spirouEXTOR.GetExtMethod(p, p['IC_EXTRACT_TYPE'])
        # construct filename
        e2dsfits = spirouConfig.Constants.EXTRACT_E2DS_FILE(p)
        e2dsfitsname = os.path.split(e2dsfits)[-1]
        # log that we are saving E2DS spectrum
        wmsg = 'Saving E2DS spectrum of Fiber {0} in {1}'
        WLOG('', p['LOG_OPT'], wmsg.format(p['FIBER'], e2dsfitsname))
        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
        # construct loco filename
        locofile = spirouConfig.Constants.EXTRACT_LOCO_FILE(p)
        locofilename = os.path.split(locofile)[-1]
        # copy extraction method and function to header (for reproducibility)
        hdict = spirouImage.AddKey(hdict, p['KW_E2DS_EXTM'], value=extmethod)
        hdict = spirouImage.AddKey(hdict, p['KW_E2DS_FUNC'], value=extfunc)

        # write 1D list of the SNR
        hdict = spirouImage.AddKey1DList(hdict, p['KW_E2DS_SNR'],
                                         values=loc['SNR'])
        # add localization file name to header
        hdict = spirouImage.AddKey(hdict, p['KW_LOCO_FILE'], value=locofilename)
        # add localization file keys to header
        root = p['KW_ROOT_DRS_LOC'][0]
        hdict = spirouImage.CopyRootKeys(hdict, locofile, root=root)
        # Save E2DS file
        spirouImage.WriteImage(e2dsfits, loc['E2DS'], hdict)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    # saturation check: check that the max_signal is lower than qc_max_signal
    if max_signal > (p['QC_MAX_SIGNAL'] * p['NBFRAMES']):
        fmsg = 'Too much flux in the image (max authorized={0})'
        fail_msg.append(fmsg.format(p['QC_MAX_SIGNAL'] * p['NBFRAMES']))
        passed = False
        # Question: Why is this test ignored?
        # For some reason this test is ignored in old code
        passed = True
        WLOG('info', p['LOG_OPT'], fail_msg[-1])

    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['LOG_OPT'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('info', p['LOG_OPT'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

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

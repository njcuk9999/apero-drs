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
import warnings

from SpirouDRS import spirouBACK
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
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
# debug (skip ic_ff_extract_type = ic_extract_type)
DEBUG = False
# define ll extract types
EXTRACT_LL_TYPES = ['3c', '3d', '4a', '4b', '5a', '5b']
EXTRACT_SHAPE_TYPES = ['4a', '4b', '5a', '5b']

# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None, fiber_type=None, **kwargs):
    """
    cal_DRIFT_E2DS_spirou.py main function, if night_name and files are
    None uses arguments from run time i.e.:
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
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files)
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
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
            WLOG(p, 'error', emsg.format(fiber_type))
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
    # now change the value of sigdet if require
    if p['IC_EXT_SIGDET'] > 0:
        p['SIGDET'] = float(p['IC_EXT_SIGDET'])
    # get DPRTYPE from header (Will have it if valid)
    p = spirouImage.ReadParam(p, hdr, 'KW_DPRTYPE', required=False, dtype=str)
    # check the DPRTYPE is not None
    if (p['DPRTYPE'] == 'None') or (['DPRTYPE'] is None):
        emsg1 = 'Error: {0} is not set in header for file {1}'
        eargs = [p['KW_DPRTYPE'][0], p['FITSFILENAME']]
        emsg2 = '\tPlease run pre-processing on file.'
        emsg3 = ('\tIf pre-processing fails or skips file, file is not '
                 'currrently as valid DRS fits file.')
        WLOG(p, 'error', [emsg1.format(*eargs), emsg2, emsg3])
    else:
        p['DPRTYPE'] = p['DPRTYPE'].strip()

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    p, datac = spirouImage.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to ADU
    data = spirouImage.ConvertToADU(spirouImage.FlipImage(p, datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data1 = spirouImage.ResizeImage(p, data0, **bkwargs)
    # log change in data size
    wmsg = 'Image format changed to {1}x{0}'
    WLOG(p, '', wmsg.format(*data1.shape))

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
    wmsg = 'Maximum average flux/pixel in the spectrum: {0:.1f} [ADU]'
    WLOG(p, 'info', wmsg.format(max_signal / p['NBFRAMES']))

    # ----------------------------------------------------------------------
    # Background computation
    # ----------------------------------------------------------------------
    if p['IC_DO_BKGR_SUBTRACTION']:
        # log that we are doing background measurement
        WLOG(p, '', 'Doing background measurement on raw frame')
        # get the bkgr measurement
        bargs = [p, data1, hdr, cdr]
        background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(*bargs)
    else:
        background = np.zeros_like(data1)
    # apply background correction to data (and set to zero where negative)
    data1 = data1 - background

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # define loc storage parameter dictionary
    loc = ParamDict()
    # get tilts (if the mode requires it)
    if p['IC_EXTRACT_TYPE'] not in EXTRACT_SHAPE_TYPES:
        p, loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
        loc.set_source('TILT', __NAME__ + '/main() + /spirouImage.ReadTiltFile')
    else:
        loc['TILT'] = None
        loc.set_source('TILT', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    #  Earth Velocity calculation
    # ----------------------------------------------------------------------
    if p['IC_IMAGE_TYPE'] == 'H4RG':
        p, loc = spirouImage.GetEarthVelocityCorrection(p, loc, hdr)

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
        # set fiber
        p['FIBER'] = fiber
        p.set_source('FIBER', __NAME__ + '/main()()')

        # ------------------------------------------------------------------
        # Read wavelength solution
        # ------------------------------------------------------------------
        # set source of wave file
        wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
        # Force A and B to AB solution
        if fiber in ['A', 'B']:
            wave_fiber = 'AB'
        else:
            wave_fiber = fiber
        # get wave image
        wkwargs = dict(hdr=hdr, return_wavemap=True, return_filename=True,
                       return_header=True, fiber=wave_fiber)
        wout = spirouImage.GetWaveSolution(p, **wkwargs)
        loc['WAVEPARAMS'], loc['WAVE'], loc['WAVEFILE'] = wout[:3]
        loc['WAVEHDR'], loc['WSOURCE'] = wout[3:]
        source_names = ['WAVE', 'WAVEFILE', 'WAVEPARAMS', 'WAVEHDR']
        loc.set_sources(source_names, wsource)
        # get dates
        loc['WAVE_ACQTIMES'] = spirouDB.GetTimes(p, loc['WAVEHDR'])
        loc.set_source('WAVE_ACQTIMES', __NAME__ + '.main()')
        # get the recipe that produced the wave solution
        if 'WAVECODE' in loc['WAVEHDR']:
            loc['WAVE_CODE'] = loc['WAVEHDR']['WAVECODE']
        else:
            loc['WAVE_CODE'] = 'UNKNOWN'
        loc.set_source('WAVE_CODE', __NAME__ + '.main()')

        # ----------------------------------------------------------------------
        # Get WFP keys
        # ----------------------------------------------------------------------
        # Read the WFP keys - if they don't exist set to None and deal
        #    with later
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_DRIFT',
                                  name='WFP_DRIFT', required=False)
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_FWHM',
                                  name='WFP_FWHM', required=False)
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_CONTRAST',
                                  name='WFP_CONTRAST', required=False)
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_MAXCPP',
                                  name='WFP_MAXCPP', required=False)
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_MASK',
                                  name='WFP_MASK', required=False)
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_LINES',
                                  name='WFP_LINES', required=False)
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_TARG_RV',
                                  name='WFP_TARG_RV', required=False)
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_WIDTH',
                                  name='WFP_WIDTH', required=False)
        p = spirouImage.ReadParam(p, loc['WAVEHDR'], 'KW_WFP_STEP',
                                  name='WFP_STEP', required=False)

        # ----------------------------------------------------------------------
        # Read Flat file
        # ----------------------------------------------------------------------
        fout = spirouImage.ReadFlatFile(p, hdr, return_header=True)
        p, loc['FLAT'], flathdr = fout
        loc.set_source('FLAT', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
        # get flat extraction mode
        if p['KW_E2DS_EXTM'][0] in flathdr:
            flat_ext_mode = flathdr[p['KW_E2DS_EXTM'][0]]
        else:
            flat_ext_mode = None

        # ------------------------------------------------------------------
        # Check extraction method is same as flat extraction method
        # ------------------------------------------------------------------
        # get extraction method and function
        extmethod, extfunc = spirouEXTOR.GetExtMethod(p, p['IC_EXTRACT_TYPE'])
        if not DEBUG:
            # compare flat extraction mode to extraction mode
            spirouEXTOR.CompareExtMethod(p, flat_ext_mode, extmethod,
                                         'FLAT', 'EXTRACTION')
        # ------------------------------------------------------------------
        # Read Blaze file
        # ------------------------------------------------------------------
        p, loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hdr)
        blazesource = __NAME__ + '/main() + /spirouImage.ReadBlazeFile'
        loc.set_source('BLAZE', blazesource)

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
        loc['E2DSFF'] = np.zeros((loc['NUMBER_ORDERS'], data2.shape[1]))
        loc['E2DSLL'] = []
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
            with warnings.catch_warnings(record=True) as w:
                eout = spirouEXTOR.Extraction(*eargs, **ekwargs)
            # deal with different return
            if p['IC_EXTRACT_TYPE'] in EXTRACT_LL_TYPES:
                e2ds, e2dsll, cpt = eout
            else:
                e2ds, cpt = eout
                e2dsll = None
            # -------------------------------------------------------------
            # calculate the noise
            range1, range2 = p['IC_EXT_RANGE1'], p['IC_EXT_RANGE2']
            # set the noise
            noise = p['SIGDET'] * np.sqrt(range1 + range2)
            # get window size
            blaze_win1 = int(data2.shape[0] / 2) - p['IC_EXTFBLAZ']
            blaze_win2 = int(data2.shape[0] / 2) + p['IC_EXTFBLAZ']
            # get average flux per pixel
            flux = np.nansum(e2ds[blaze_win1:blaze_win2]) / (2 * p['IC_EXTFBLAZ'])
            # calculate signal to noise ratio = flux/sqrt(flux + noise^2)
            snr = flux / np.sqrt(flux + noise ** 2)
            # log the SNR RMS
            wmsg = 'On fiber {0} order {1}: S/N= {2:.1f} Nbcosmic= {3}'
            wargs = [p['FIBER'], order_num, snr, cpt]
            WLOG(p, '', wmsg.format(*wargs))
            # add calculations to storage
            loc['E2DS'][order_num] = e2ds
            loc['E2DSFF'][order_num] = e2ds / loc['FLAT'][order_num]
            loc['SNR'][order_num] = snr
            # save the longfile
            if p['IC_EXTRACT_TYPE'] in EXTRACT_LL_TYPES:
                loc['E2DSLL'].append(e2dsll)
            # set sources
            loc.set_sources(['e2ds', 'SNR'], source)
            # Log if saturation level reached
            satvalue = (flux / p['GAIN']) / (range1 + range2)
            if satvalue > (p['QC_LOC_FLUMAX'] * p['NBFRAMES']):
                wmsg = 'SATURATION LEVEL REACHED on Fiber {0} order={1}'
                WLOG(p, 'warning', wmsg.format(fiber, order_num))

        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            # start interactive session if needed
            sPlt.start_interactive_session(p)
            # plot all orders or one order
            if p['IC_FF_PLOT_ALL_ORDERS']:
                # plot image with all order fits (slower)
                sPlt.ext_aorder_fit(p, loc, data1, max_signal / 10.)
            else:
                # plot image with selected order fit and edge fit (faster)
                sPlt.ext_sorder_fit(p, loc, data1, max_signal / 10.)
            # plot e2ds against wavelength
            sPlt.ext_spectral_order_plot(p, loc)

            if p['IC_EXTRACT_TYPE'] in EXTRACT_SHAPE_TYPES:
                sPlt.ext_debanana_plot(p, loc, data2, max_signal / 10.)

        # ----------------------------------------------------------------------
        # Quality control
        # ----------------------------------------------------------------------
        passed, fail_msg = True, []
        qc_values, qc_names, qc_logic, qc_pass = [], [], [], []

        # saturation check: check that the max_signal is lower than
        # qc_max_signal
        max_qcflux = p['QC_MAX_SIGNAL'] * p['NBFRAMES']
        if max_signal > max_qcflux:
            fmsg = 'Too much flux in the image ({0:.2f} > {1:.2f})'
            fail_msg.append(fmsg.format(max_signal, max_qcflux))
            passed = False
            # Question: Why is this test ignored?
            # For some reason this test is ignored in old code
            passed = True
            WLOG(p, 'info', fail_msg[-1])
            qc_pass.append(0)
        else:
            qc_pass.append(1)

        # add to qc header lists
        qc_values.append(max_signal)
        qc_names.append('max_signal')
        qc_logic.append('QC_MAX_SIGNAL > {0:.3f}'.format(max_qcflux))

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

        # ------------------------------------------------------------------
        # Store extraction in file(s)
        # ------------------------------------------------------------------
        raw_ext_file = os.path.basename(p['FITSFILENAME'])
        # construct filename
        e2dsfits, tag1 = spirouConfig.Constants.EXTRACT_E2DS_FILE(p)
        e2dsfitsname = os.path.split(e2dsfits)[-1]
        e2dsfffits, tag2 = spirouConfig.Constants.EXTRACT_E2DSFF_FILE(p)
        e2dsfffitsname = os.path.split(e2dsfffits)[-1]
        e2dsllfits, tag4 = spirouConfig.Constants.EXTRACT_E2DSLL_FILE(p)
        e2dsfllitsname = os.path.split(e2dsllfits)[-1]
        # log that we are saving E2DS spectrum
        wmsg = 'Saving E2DS spectrum of Fiber {0} in {1}'
        WLOG(p, '', wmsg.format(p['FIBER'], e2dsfitsname))
        wmsg = 'Saving E2DSFF spectrum of Fiber {0} in {1}'
        WLOG(p, '', wmsg.format(p['FIBER'], e2dsfffitsname))
        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
        # set the version
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])

        # set the input files
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
                                   value=p['BLAZFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBFLAT'],
                                   value=p['FLATFILE'])
        if p['IC_EXTRACT_TYPE'] in EXTRACT_SHAPE_TYPES:
            hdict = spirouImage.AddKey(p, hdict, p['KW_CDBSHAPE'],
                                       value=p['SHAPFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                                   value=loc['WAVEFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                                   value=loc['WSOURCE'])
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                         dim1name='file',
                                         values=p['ARG_FILE_NAMES'])
        # construct loco filename
        locofile, _ = spirouConfig.Constants.EXTRACT_LOCO_FILE(p)
        locofilename = os.path.basename(locofile)
        # add barycentric keys to header
        hdict = spirouImage.AddKey(p, hdict, p['KW_BERV'], value=loc['BERV'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_BJD'], value=loc['BJD'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_BERV_MAX'],
                                   value=loc['BERV_MAX'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_B_OBS_HOUR'],
                                   value=loc['BERVHOUR'])
        # add qc parameters
        hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
        hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
        # copy extraction method and function to header
        #     (for reproducibility)
        hdict = spirouImage.AddKey(p, hdict, p['KW_E2DS_EXTM'],
                                   value=extmethod)
        hdict = spirouImage.AddKey(p, hdict, p['KW_E2DS_FUNC'],
                                   value=extfunc)
        # add localization file name to header
        hdict = spirouImage.AddKey(p, hdict, p['KW_LOCO_FILE'],
                                   value=locofilename)
        # add wave solution date
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME1'],
                                   value=loc['WAVE_ACQTIMES'][0])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME2'],
                                   value=loc['WAVE_ACQTIMES'][1])
        # add wave solution number of orders
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_ORD_N'],
                                   value=loc['WAVEPARAMS'].shape[0])
        # add wave solution degree of fit
        hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_LL_DEG'],
                                   value=loc['WAVEPARAMS'].shape[1] - 1)
        # -------------------------------------------------------------------------
        # add keys of the wave solution FP CCF
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_FILE'],
                                   value=loc['WAVEFILE'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_DRIFT'],
                                   value=p['WFP_DRIFT'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_FWHM'],
                                   value=p['WFP_FWHM'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_CONTRAST'],
                                   value=p['WFP_CONTRAST'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_MAXCPP'],
                                   value=p['WFP_MAXCPP'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_MASK'],
                                   value=p['WFP_MASK'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_LINES'],
                                   value=p['WFP_LINES'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_TARG_RV'],
                                   value=p['WFP_TARG_RV'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_WIDTH'],
                                   value=p['WFP_WIDTH'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_WFP_STEP'],
                                   value=p['WFP_STEP'])

        # write 1D list of the SNR
        hdict = spirouImage.AddKey1DList(p, hdict, p['KW_E2DS_SNR'],
                                         values=loc['SNR'])
        # add localization file keys to header
        root = p['KW_ROOT_DRS_LOC'][0]
        hdict = spirouImage.CopyRootKeys(p, hdict, locofile, root=root)
        # add wave solution coefficients
        hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                         values=loc['WAVEPARAMS'])
        # Save E2DS file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        p = spirouImage.WriteImage(p, e2dsfits, loc['E2DS'], hdict)
        # Save E2DSFF file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        p = spirouImage.WriteImage(p, e2dsfffits, loc['E2DSFF'], hdict)
        # Save E2DSLL file
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag4)
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        if p['IC_EXTRACT_TYPE'] in EXTRACT_LL_TYPES:
            llstack = np.vstack(loc['E2DSLL'])
            p = spirouImage.WriteImage(p, e2dsllfits, llstack, hdict)

        # ------------------------------------------------------------------
        # 1-dimension spectral S1D (uniform in wavelength)
        # ------------------------------------------------------------------
        # get arguments for E2DS to S1D
        e2dsargs = [loc['WAVE'], loc['E2DSFF'], loc['BLAZE']]
        # get 1D spectrum
        xs1d1, ys1d1 = spirouImage.E2DStoS1D(p, *e2dsargs, wgrid='wave')
        # Plot the 1D spectrum
        if p['DRS_PLOT'] > 0:
            sPlt.ext_1d_spectrum_plot(p, xs1d1, ys1d1)
        # construct file name
        s1dfile1, tag3 = spirouConfig.Constants.EXTRACT_S1D_FILE1(p)
        s1dfilename1 = os.path.basename(s1dfile1)
        # add header keys
        # set the version
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        # log writing to file
        wmsg = 'Saving 1D spectrum (uniform in wavelength) for Fiber {0} in {1}'
        WLOG(p, '', wmsg.format(p['FIBER'], s1dfilename1))
        # Write to file
        columns = ['wavelength', 'flux', 'eflux']
        values = [xs1d1, ys1d1, np.zeros_like(ys1d1)]
        units = ['nm', None, None]
        s1d1 = spirouImage.MakeTable(p, columns, values, units=units)
        spirouImage.WriteTable(p, s1d1, s1dfile1, header=hdict)

        # ------------------------------------------------------------------
        # 1-dimension spectral S1D (uniform in velocity)
        # ------------------------------------------------------------------
        # get arguments for E2DS to S1D
        e2dsargs = [loc['WAVE'], loc['E2DSFF'], loc['BLAZE']]
        # get 1D spectrum
        xs1d2, ys1d2 = spirouImage.E2DStoS1D(p, *e2dsargs, wgrid='velocity')
        # Plot the 1D spectrum
        if p['DRS_PLOT'] > 0:
            sPlt.ext_1d_spectrum_plot(p, xs1d2, ys1d2)
        # construct file name
        s1dfile2, tag4 = spirouConfig.Constants.EXTRACT_S1D_FILE2(p)
        s1dfilename2 = os.path.basename(s1dfile2)
        # add header keys
        hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
        hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag4)
        hdict = spirouImage.AddKey(p, hdict, p['KW_EXT_TYPE'],
                                   value=p['DPRTYPE'])
        # log writing to file
        wmsg = 'Saving 1D spectrum (uniform in velocity) for Fiber {0} in {1}'
        WLOG(p, '', wmsg.format(p['FIBER'], s1dfilename2))
        # Write to file
        columns = ['wavelength', 'flux', 'eflux']
        values = [xs1d2, ys1d2, np.zeros_like(ys1d2)]
        units = ['nm', None, None]
        s1d2 = spirouImage.MakeTable(p, columns, values, units=units)
        spirouImage.WriteTable(p, s1d2, s1dfile2, header=hdict)

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

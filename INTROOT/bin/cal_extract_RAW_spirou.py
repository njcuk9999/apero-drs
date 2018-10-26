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
        WLOG('error', p['LOG_OPT'], [emsg1.format(*eargs), emsg2, emsg3])
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
    data = spirouImage.ConvertToADU(spirouImage.FlipImage(datac), p=p)
    # convert NaN to zeros
    data0 = np.where(~np.isfinite(data), np.zeros_like(data), data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    data1 = spirouImage.ResizeImage(data0, **bkwargs)
    # log change in data size
    wmsg = 'Image format changed to {1}x{0}'
    WLOG('', p['LOG_OPT'], wmsg.format(*data1.shape))

    # ----------------------------------------------------------------------
    # Correct for the BADPIX mask (set all bad pixels to zero)
    # ----------------------------------------------------------------------
    p, data1 = spirouImage.CorrectForBadPix(p, data1, hdr)

    # ----------------------------------------------------------------------
    # Log the number of dead pixels
    # ----------------------------------------------------------------------
    # get the number of bad pixels
    n_bad_pix = np.sum(data1 == 0)
    n_bad_pix_frac = n_bad_pix * 100 / np.product(data1.shape)
    # Log number
    wmsg = 'Nb dead pixels = {0} / {1:.4f} %'
    WLOG('info', p['LOG_OPT'], wmsg.format(int(n_bad_pix), n_bad_pix_frac))

    # ----------------------------------------------------------------------
    # Get the miny, maxy and max_signal for the central column
    # ----------------------------------------------------------------------
    # get the central column
    y = data1[p['IC_CENT_COL'], :]
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
        background, xc, yc, minlevel = spirouBACK.MeasureBackgroundFF(p, data1)
    else:
        background = np.zeros_like(data1)
    # apply background correction to data (and set to zero where negative)
    # TODO: Etienne --> Francois - Cannot set negative flux to zero!
    data1 = np.where(data1 > 0, data1 - background, 0)

    # ----------------------------------------------------------------------
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # define loc storage parameter dictionary
    loc = ParamDict()
    # get tilts
    p, loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('TILT', __NAME__ + '/main() + /spirouImage.ReadTiltFile')

    # ----------------------------------------------------------------------
    #  Earth Velocity calculation
    # ----------------------------------------------------------------------
    if p['IC_IMAGE_TYPE'] == 'H4RG':
        p, loc = spirouImage.GetEarthVelocityCorrection(p, loc, hdr)

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
        wout = spirouImage.GetWaveSolution(p, hdr=hdr, return_wavemap=True,
                                           return_filename=True,
                                           return_header=True, fiber=wave_fiber)
        loc['WAVEPARAMS'], loc['WAVE'], loc['WAVEFILE'], loc['WAVEHDR'] = wout
        loc.set_sources(['WAVE', 'WAVEFILE', 'WAVEPARAMS', 'WAVEHDR'], wsource)

        # get dates
        loc['WAVE_ACQTIMES'] = spirouDB.GetTimes(p, loc['WAVEHDR'])

        # ----------------------------------------------------------------------
        # Read Flat file
        # ----------------------------------------------------------------------
        fout = spirouImage.ReadFlatFile(p, hdr, return_header=True)
        p, loc['FLAT'], flathdr = fout
        loc.set_source('FLAT', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
        # get all values in flat that are zero to 1
        loc['FLAT'] = np.where(loc['FLAT'] == 0, 1.0, loc['FLAT'])

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
        # Get localisation coefficients
        # ------------------------------------------------------------------
        # get this fibers parameters
        p = spirouImage.FiberParams(p, p['FIBER'], merge=True)
        # get localisation fit coefficients
        p, loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
        # ------------------------------------------------------------------
        # Read image order profile
        # ------------------------------------------------------------------
        order_profile, _, _, nx, ny = spirouImage.ReadOrderProfile(p, hdr)

        # ------------------------------------------------------------------
        # Deal with debananafication
        # ------------------------------------------------------------------
        if p['IC_EXTRACT_TYPE'] in ['4a', '4b']:
            # log progress
            WLOG('', p['LOG_OPT'], 'Debananafying (straightening) image')
            # get the shape map
            p, shapemap = spirouImage.ReadShapeMap(p, hdr)
            # debananafy data and order profile
            data2 = spirouEXTOR.DeBananafication(np.array(data1), shapemap)
            order_profile = spirouEXTOR.DeBananafication(order_profile,
                                                         shapemap)
        else:
            data2 = np.array(data1)

        # ------------------------------------------------------------------
        # Average AB into one fiber for AB, A and B
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
            loc['NUMBER_ORDERS'] = int(loc['NUMBER_ORDERS'] / 2.0)
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
            #deal with different return
            if p['IC_EXTRACT_TYPE'] in ['3c', '3d', '4a', '4b']:
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
            e2ds = np.where(loc['BLAZE'][order_num] > 1, e2ds, 0.)
            loc['E2DS'][order_num] = e2ds
            loc['E2DSFF'][order_num] = e2ds / loc['FLAT'][order_num]
            loc['SNR'][order_num] = snr
            # save the longfile
            if p['IC_EXTRACT_TYPE'] in ['3c', '3d', '4a', '4b']:
                loc['E2DSLL'].append(e2dsll)
            # set sources
            loc.set_sources(['e2ds', 'SNR'], source)
            # Log if saturation level reached
            satvalue = (flux/p['GAIN'])/(range1 + range2)
            if satvalue > (p['QC_LOC_FLUMAX'] * p['NBFRAMES']):
                wmsg = 'SATURATION LEVEL REACHED on Fiber {0} order={1}'
                WLOG('warning', p['LOG_OPT'], wmsg.format(fiber, order_num))

        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        if p['DRS_PLOT']:
            # start interactive session if needed
            sPlt.start_interactive_session()
            # plot all orders or one order
            if p['IC_FF_PLOT_ALL_ORDERS']:
                # plot image with all order fits (slower)
                sPlt.ext_aorder_fit(p, loc, data2, max_signal / 10.)
            else:
                # plot image with selected order fit and edge fit (faster)
                sPlt.ext_sorder_fit(p, loc, data2, max_signal / 10.)
            # plot e2ds against wavelength
            sPlt.ext_spectral_order_plot(p, loc)

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
        WLOG('', p['LOG_OPT'], wmsg.format(p['FIBER'], e2dsfitsname))
        wmsg = 'Saving E2DSFF spectrum of Fiber {0} in {1}'
        WLOG('', p['LOG_OPT'], wmsg.format(p['FIBER'], e2dsfffitsname))
        # add keys from original header file
        hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
        # set the version
        hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])

        # set the input files
        hdict = spirouImage.AddKey(hdict, p['KW_DARKFILE'], value=p['DARKFILE'])
        hdict = spirouImage.AddKey(hdict, p['KW_BADPFILE1'],
                                   value=p['BADPFILE1'])
        hdict = spirouImage.AddKey(hdict, p['KW_BADPFILE2'],
                                   value=p['BADPFILE2'])
        hdict = spirouImage.AddKey(hdict, p['KW_LOCOFILE'], value=p['LOCOFILE'])
        hdict = spirouImage.AddKey(hdict, p['KW_TILTFILE'], value=p['TILTFILE'])
        hdict = spirouImage.AddKey(hdict, p['KW_BLAZFILE'], value=p['BLAZFILE'])
        hdict = spirouImage.AddKey(hdict, p['KW_FLATFILE'], value=p['FLATFILE'])
        if p['IC_EXTRACT_TYPE'] in ['4a', '4b']:
            hdict = spirouImage.AddKey(hdict, p['KW_SHAPEFILE'],
                                       value=p['SHAPFILE'])
        hdict = spirouImage.AddKey(hdict, p['KW_EXTFILE'], value=raw_ext_file)
        hdict = spirouImage.AddKey(hdict, p['KW_WAVEFILE'],
                                   value=loc['WAVEFILE'])
        # construct loco filename
        locofile, _ = spirouConfig.Constants.EXTRACT_LOCO_FILE(p)
        locofilename = os.path.basename(locofile)
        # add barycentric keys to header
        hdict = spirouImage.AddKey(hdict, p['KW_BERV'], value=loc['BERV'])
        hdict = spirouImage.AddKey(hdict, p['KW_BJD'], value=loc['BJD'])
        hdict = spirouImage.AddKey(hdict, p['KW_BERV_MAX'],
                                   value=loc['BERV_MAX'])
        # copy extraction method and function to header
        #     (for reproducibility)
        hdict = spirouImage.AddKey(hdict, p['KW_E2DS_EXTM'],
                                   value=extmethod)
        hdict = spirouImage.AddKey(hdict, p['KW_E2DS_FUNC'],
                                   value=extfunc)
        # add localization file name to header
        hdict = spirouImage.AddKey(hdict, p['KW_LOCO_FILE'], value=locofilename)
        # add wave solution date
        hdict = spirouImage.AddKey(hdict, p['KW_WAVE_TIME1'],
                                   value=loc['WAVE_ACQTIMES'][0])
        hdict = spirouImage.AddKey(hdict, p['KW_WAVE_TIME2'],
                                   value=loc['WAVE_ACQTIMES'][1])
        # add wave solution number of orders
        hdict = spirouImage.AddKey(hdict, p['KW_WAVE_ORD_N'],
                                   value=loc['WAVEPARAMS'].shape[0])
        # add wave solution degree of fit
        hdict = spirouImage.AddKey(hdict, p['KW_WAVE_LL_DEG'],
                                   value=loc['WAVEPARAMS'].shape[1] - 1)
        # write 1D list of the SNR
        hdict = spirouImage.AddKey1DList(hdict, p['KW_E2DS_SNR'],
                                         values=loc['SNR'])
        # add localization file keys to header
        root = p['KW_ROOT_DRS_LOC'][0]
        hdict = spirouImage.CopyRootKeys(hdict, locofile, root=root)
        # add wave solution coefficients
        hdict = spirouImage.AddKey2DList(hdict, p['KW_WAVE_PARAM'],
                                         values=loc['WAVEPARAMS'])
        # Save E2DS file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag1)
        hdict = spirouImage.AddKey(hdict, p['KW_EXT_TYPE'], value=p['DPRTYPE'])
        p = spirouImage.WriteImage(p, e2dsfits, loc['E2DS'], hdict)
        # Save E2DSFF file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag2)
        hdict = spirouImage.AddKey(hdict, p['KW_EXT_TYPE'], value=p['DPRTYPE'])
        p = spirouImage.WriteImage(p, e2dsfffits, loc['E2DSFF'], hdict)
        # Save E2DSLL file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag4)
        hdict = spirouImage.AddKey(hdict, p['KW_EXT_TYPE'], value=p['DPRTYPE'])
        if p['IC_EXTRACT_TYPE'] in ['3c', '3d', '4a', '4b']:
            llstack = np.vstack(loc['E2DSLL'])
            p = spirouImage.WriteImage(p, e2dsllfits, llstack, hdict)

        # ------------------------------------------------------------------
        # 1-dimension spectral S1D
        # ------------------------------------------------------------------
        # normalise E2DSFF with the blaze function
        e2dsffb = loc['E2DSFF'] / loc['BLAZE']
        # only want certain orders
        s1dwave = loc['WAVE'][p['IC_START_ORDER_1D']:p['IC_END_ORDER_1D']]
        s1de2dsffb = e2dsffb[p['IC_START_ORDER_1D']:p['IC_END_ORDER_1D']]
        # get arguments for E2DS to S1D
        e2dsargs = [s1dwave, s1de2dsffb, p['IC_BIN_S1D']]
        # get 1D spectrum
        try:
            xs1d, ys1d = spirouImage.E2DStoS1D(*e2dsargs)
        except Exception as e:
            emsg1 = 'Cannot compute 1D spectrum'
            emsg2 = '\tError reads: {0}'.format(e)
            WLOG('warning', p['LOG_OPT'], [emsg1, emsg2])
            xs1d, ys1d = None, None
        # Plot the 1D spectrum
        if p['DRS_PLOT'] and (xs1d is not None) and (ys1d is not None):
            sPlt.ext_1d_spectrum_plot(p, xs1d, ys1d)

        # construct file name
        if (xs1d is not None) and (ys1d is not None):
            s1dfile, tag3 = spirouConfig.Constants.EXTRACT_S1D_FILE(p)
            s1dfilename = os.path.basename(s1dfile)

            # add header keys
            # set the version
            hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
            hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag3)
            hdict = spirouImage.AddKey(hdict, p['KW_EXT_TYPE'],
                                       value=p['DPRTYPE'])
            hdict = spirouImage.AddKey(hdict, p['KW_CRPIX1'], value=1.0)
            hdict = spirouImage.AddKey(hdict, p['KW_CRVAL1'], value=xs1d[0])
            hdict = spirouImage.AddKey(hdict, p['KW_CDELT1'],
                                       value=p['IC_BIN_S1D'])
            hdict = spirouImage.AddKey(hdict, p['KW_CTYPE1'], value='nm')
            hdict = spirouImage.AddKey(hdict, p['KW_BUNIT'],
                                       value='Relative Flux')
            # log writing to file
            wmsg = 'Saving S1D spectrum of Fiber {0} in {1}'
            WLOG('', p['LOG_OPT'], wmsg.format(p['FIBER'], s1dfilename))
            # Write to file
            p = spirouImage.WriteImage(p, s1dfile, ys1d, hdict)

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
            WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

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

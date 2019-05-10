#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-02-15 at 14:05

@author: cook
"""
from __future__ import division
import numpy as np
import os
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS.spirouImage import spirouExposeMeter as spirouExM
from SpirouDRS import spirouLOCOR
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_exposure_meter.py'
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
EXTRACT_SHAPE_TYPES = ['4a', '4b', '5a', '5b']


# =============================================================================
# Define main program function
# =============================================================================
def main(night_name=None, flatfile=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with arguments being None (i.e. get from sys.argv)
    name, lname = ['flatfile'], ['Reference file']
    req, call, call_priority = [True], [flatfile], [True]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(p, [0], [str], name, req,
                                                    call, call_priority, lname)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='flatfile')
    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, reffile = spirouStartup.SingleFileSetup(p, filename=p['FLATFILE'])

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Get the required fiber type from the constants file
    # ----------------------------------------------------------------------
    # get the fiber type (set to AB)
    p['FIBER'] = p['EM_FIB_TYPE']
    p['FIBER_TYPES'] = [p['EM_FIB_TYPE']]

    # ----------------------------------------------------------------------
    # Read flat image file
    # ----------------------------------------------------------------------
    # read the image data (for the header only)
    image, hdr, ny, nx = spirouImage.ReadData(p, reffile)

    # ----------------------------------------------------------------------
    # fix for un-preprocessed files
    # ----------------------------------------------------------------------
    image = spirouImage.FixNonPreProcess(p, image)

    # ----------------------------------------------------------------------
    # Get basic image properties
    # ----------------------------------------------------------------------
    # create loc
    loc = ParamDict()
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')

    # ----------------------------------------------------------------------
    # Resize flat image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    image2 = spirouImage.ConvertToE(spirouImage.FlipImage(p, image), p=p)
    # convert NaN to zeros
    image2 = np.where(~np.isfinite(image2), np.zeros_like(image2), image2)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    image2 = spirouImage.ResizeImage(p, image2, **bkwargs)
    # save flat to to loc and set source
    loc['IMAGE'] = image2
    loc.set_sources(['image'], __NAME__ + '/main()')
    # log change in data size
    wmsg = 'Image format changed to {0}x{1}'
    WLOG(p, '', wmsg.format(*image2.shape))

    # ----------------------------------------------------------------------
    # Read shape or tilt slit angle
    # ----------------------------------------------------------------------
    # set source of tilt file
    tsource = __NAME__ + '/main() + /spirouImage.ReadTiltFile'

    if p['IC_EXTRACT_TYPE'] in EXTRACT_SHAPE_TYPES:
        # log progress
        WLOG(p, '', 'Debananafying (straightening) image')
        # get the shape map
        p, loc['SHAPE'] = spirouImage.ReadShapeMap(p, hdr)
        loc.set_source('SHAPE', tsource)
    else:
        # get tilts
        p, loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
        loc.set_source('TILT', tsource)

    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    p, loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')
    # set number of orders from blaze file
    loc['NBO'] = loc['BLAZE'].shape[0]
    loc.set_source('NBO', __NAME__ + '/main()')

    # ------------------------------------------------------------------
    # Read wavelength solution
    # ------------------------------------------------------------------
    # set source of wave file
    wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # get wave image
    wout = spirouImage.GetWaveSolution(p, hdr=hdr, return_wavemap=True,
                                       return_filename=True, fiber=wave_fiber)
    loc['WAVEPARAMS'], loc['WAVE'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    loc.set_sources(['WAVEPARAMS', 'WAVE', 'WAVEFILE', 'WSOURCE'], wsource)

    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # storage for fiber parameters
    loc['ALL_ACC'] = OrderedDict()
    loc['ALL_ASS'] = OrderedDict()
    # get this fibers parameters
    for fiber in p['FIBER_TYPES']:
        p = spirouImage.FiberParams(p, fiber, merge=True)
        # get localisation fit coefficients
        p, loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
        # save all fibers
        loc['ALL_ACC'][fiber] = loc['ACC']
        loc['ALL_ASS'][fiber] = loc['ASS']

    # ------------------------------------------------------------------
    # Get telluric and telluric mask and add to loc
    # ------------------------------------------------------------------
    # log process
    wmsg = 'Loading telluric model and locating "good" tranmission'
    WLOG(p, '', wmsg)
    # load telluric and get mask (add to loc)
    loc = spirouExM.get_telluric(p, loc)

    # ------------------------------------------------------------------
    # Make 2D map of orders
    # ------------------------------------------------------------------
    # log progress
    WLOG(p, '', 'Making 2D map of order locations')
    # make the 2D wave-image
    loc = spirouExM.order_profile(p, loc)

    # ------------------------------------------------------------------
    # Make 2D map of wavelengths accounting for shape / tilt
    # ------------------------------------------------------------------
    # log progress
    WLOG(p, '', 'Mapping pixels on to wavelength grid')
    # make the 2D map of wavelength
    loc = spirouExM.create_wavelength_image(p, loc)

    # ------------------------------------------------------------------
    # Use spectra wavelength to create 2D image from wave-image
    # ------------------------------------------------------------------
    if p['EM_SAVE_MASK_MAP'] or p['EM_SAVE_TELL_SPEC']:
        # log progress
        WLOG(p, '', 'Creating image from wave-image interpolation')
        # create image from waveimage
        wkwargs = dict(x=loc['TELL_X'], y=loc['TELL_Y'])
        loc = spirouExM.create_image_from_waveimage(loc, **wkwargs)
    else:
        loc['SPE'] = np.zeros_like(image2).astype(float)

    # ------------------------------------------------------------------
    # Create 2D mask (min to max lambda + transmission threshold)
    # ------------------------------------------------------------------
    if p['EM_SAVE_MASK_MAP']:
        # log progress
        WLOG(p, '', 'Creating wavelength/tranmission mask')
        # create mask
        loc = spirouExM.create_mask(p, loc)
    else:
        loc['TELL_MASK_2D'] = np.zeros_like(image2).astype(bool)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # TODO: Needs doing
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
    # add to qc header lists
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # ------------------------------------------------------------------
    # Construct parameters for header
    # ------------------------------------------------------------------
    hdict = OrderedDict()
    # set the version
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    # set the input files
    if loc['SHAPE'] is not None:
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBSHAPE'],
                                   value=p['SHAPFILE'])
    else:
        hdict = spirouImage.AddKey(p, hdict, p['KW_CDBTILT'],
                                   value=p['TILTFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBLOCO'], value=p['LOCOFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'], value=loc['WAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['FLATFILE'])
    # add name of the TAPAS y data
    hdict = spirouImage.AddKey(p, hdict, p['KW_EM_TELLY'], value=loc['TELLSPE'])
    # add name of the localisation fits file used
    hfile = os.path.basename(loc['LOCO_CTR_FILE'])
    hdict = spirouImage.AddKey(p, hdict, p['kw_EM_LOCFILE'], value=hfile)
    # add the max and min wavelength threshold
    hdict = spirouImage.AddKey(p, hdict, p['kw_EM_MINWAVE'],
                               value=p['EM_MIN_LAMBDA'])
    hdict = spirouImage.AddKey(p, hdict, p['kw_EM_MAXWAVE'],
                               value=p['EM_MAX_LAMBDA'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # add the transmission cut
    hdict = spirouImage.AddKey(p, hdict, p['kw_EM_TRASCUT'],
                               value=p['EM_TELL_THRESHOLD'])

    # ------------------------------------------------------------------
    # Deal with output preferences
    # ------------------------------------------------------------------
    # add bad pixel map (if required)
    if p['EM_COMBINED_BADPIX']:
        # get bad pix mask (True where bad)
        badpixmask, bhdr, badfile = spirouImage.GetBadPixMap(p, hdr)
        goodpixels = badpixmask == 0
        # apply mask (multiply)
        loc['TELL_MASK_2D'] = loc['TELL_MASK_2D'] & goodpixels.astype(bool)
    else:
        badfile = 'None'
    # add to hdict
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBAD'], value=badfile)

    # convert waveimage mask into float array
    loc['TELL_MASK_2D'] = loc['TELL_MASK_2D'].astype('float')

    # check EM_OUTPUT_TYPE and deal with set to "all"
    if p['EM_OUTPUT_TYPE'] not in ["drs", "raw", "preprocess", "all"]:
        emsg1 = '"EM_OUTPUT_TYPE" not understood'
        emsg2 = '   must be either "drs", "raw" or "preprocess"'
        emsg3 = '   currently EM_OUTPUT_TYPE="{0}"'.format(p['EM_OUTPUT_TYPE'])
        WLOG(p, 'error', [emsg1, emsg2, emsg3])
        outputs = []
    elif p['EM_OUTPUT_TYPE'] != 'all':
        outputs = [str(p['EM_OUTPUT_TYPE'])]
    else:
        outputs = ["drs", "raw", "preprocess"]

    # ----------------------------------------------------------------------
    # loop around output types
    # ----------------------------------------------------------------------
    for output in outputs:
        # log progress
        WLOG(p, '', 'Processing {0} outputs'.format(output))
        # change EM_OUTPUT_TYPE
        p['EM_OUTPUT_TYPE'] = output
        # copy arrays
        out_spe = np.array(loc['SPE'])
        out_wave = np.array(loc['WAVEIMAGE'])
        out_mask = np.array(loc['TELL_MASK_2D'])
        # change image size if needed
        if output in ["raw", "preprocess"]:
            kk = dict(xsize=image.shape[1], ysize=image.shape[0])
            if p['EM_SAVE_TELL_SPEC']:
                WLOG(p, '', 'Resizing/Flipping SPE')
                out_spe = spirouExM.unresize(p, out_spe, **kk)
                WLOG(p, '', 'Rescaling SPE')
                out_spe = out_spe / (p['GAIN'] * p['EXPTIME'])
            if p['EM_SAVE_WAVE_MAP']:
                WLOG(p, '', 'Resizing/Flipping WAVEIMAGE')
                out_wave = spirouExM.unresize(p, out_wave, **kk)
            if p['EM_SAVE_MASK_MAP']:
                WLOG(p, '', 'Resizing/Flipping TELL_MASK_2D')
                out_mask = spirouExM.unresize(p, out_mask, **kk)
        # if raw need to rotate (undo pre-processing)
        if output == "raw":
            if p['EM_SAVE_TELL_SPEC']:
                WLOG(p, '', 'Rotating SPE')
                out_spe = np.rot90(out_spe, 1)
            if p['EM_SAVE_WAVE_MAP']:
                WLOG(p, '', 'Rotating WAVEIMAGE')
                out_wave = np.rot90(out_wave, 1)
            if p['EM_SAVE_MASK_MAP']:
                WLOG(p, '', 'Rotating TELL_MASK_2D')
                out_mask = np.rot90(out_mask, 1)

        # ----------------------------------------------------------------------
        # save 2D spectrum, wavelength image and mask to file
        # ----------------------------------------------------------------------
        # save telluric spectrum
        if p['EM_SAVE_TELL_SPEC']:
            # construct spectrum filename
            specfitsfile, tag = spirouConfig.Constants.EM_SPE_FILE(p)
            specfilename = os.path.split(specfitsfile)[-1]
            # set the version
            hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
            hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
            # log progress
            wmsg = 'Writing spectrum to file {0}'
            WLOG(p, '', wmsg.format(specfilename))
            # write to file
            p = spirouImage.WriteImage(p, specfitsfile, out_spe, hdict=hdict)

        # ----------------------------------------------------------------------
        # save wave map
        if p['EM_SAVE_WAVE_MAP']:
            # construct waveimage filename
            wavefitsfile, tag = spirouConfig.Constants.EM_WAVE_FILE(p)
            wavefilename = os.path.split(wavefitsfile)[-1]
            # set the version
            hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
            hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
            # log progress
            wmsg = 'Writing wave image to file {0}'
            WLOG(p, '', wmsg.format(wavefilename))
            # write to file
            p = spirouImage.WriteImage(p, wavefitsfile, out_wave, hdict=hdict)

        # ----------------------------------------------------------------------
        # save mask file
        if p['EM_SAVE_MASK_MAP']:
            # construct tell mask 2D filename
            maskfitsfile, tag = spirouConfig.Constants.EM_MASK_FILE(p)
            maskfilename = os.path.split(maskfitsfile)[-1]
            # set the version
            hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
            hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
            # log progress
            wmsg = 'Writing telluric mask to file {0}'
            WLOG(p, '', wmsg.format(maskfilename))
            # convert boolean mask to integers
            writablemask = np.array(out_mask, dtype=float)
            # write to file
            p = spirouImage.WriteImage(p, maskfitsfile, writablemask,
                                       hdict=hdict)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================

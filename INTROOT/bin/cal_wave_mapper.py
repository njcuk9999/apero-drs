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
__NAME__ = 'cal_wave_mapper.py'
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
# # test files
# night_name, reffile = '180529', '2279713f_flat_flat_pp.fits'
# e2dsprefix = '2279725a_fp_fp_pp_e2dsff'


# =============================================================================
# Define main program function
# =============================================================================
def main(night_name=None, flatfile=None, e2dsprefix=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with arguments being None (i.e. get from sys.argv)
    name, lname = ['flatfile', 'e2dsprefix'], ['Reference file', 'E2DS Prefix']
    req, call, call_priority = [True, True], [flatfile, e2dsprefix], [True, True]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime([0, 1], [str, str], name,
                                                    req, call, call_priority,
                                                    lname)
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
    p['FIBER_TYPES'] = ['AB', 'C']

    # ----------------------------------------------------------------------
    # Read flat image file
    # ----------------------------------------------------------------------
    # read the image data (for the header only)
    image, hdr, cdr, ny, nx = spirouImage.ReadData(p, reffile)

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
    image2 = spirouImage.ConvertToE(spirouImage.FlipImage(image), p=p)
    # convert NaN to zeros
    image2 = np.where(~np.isfinite(image2), np.zeros_like(image2), image2)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    image2 = spirouImage.ResizeImage(image2, **bkwargs)
    # save flat to to loc and set source
    loc['IMAGE'] = image2
    loc.set_sources(['image'], __NAME__ + '/main()')
    # log change in data size
    wmsg = 'Image format changed to {0}x{1}'
    WLOG('', p['LOG_OPT'], wmsg.format(*image2.shape))

    # ----------------------------------------------------------------------
    # Read shape or tilt slit angle
    # ----------------------------------------------------------------------
    # set source of tilt file
    tsource = __NAME__ + '/main() + /spirouImage.ReadTiltFile'


    if p['IC_EXTRACT_TYPE'] in ['4a', '4b']:
        # log progress
        WLOG('', p['LOG_OPT'], 'Debananafying (straightening) image')
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
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # storage for fiber parameters
    loc['ALL_ACC'] = OrderedDict()
    loc['ALL_ASS'] = OrderedDict()
    loc['E2DSFILENAMES'] = []
    loc['E2DSFILES'] = OrderedDict()
    loc['ALLWAVE'] = OrderedDict()
    # set source
    lkeys = ['ALL_ACC', 'ALL_ASS', 'E2DSFILES', 'E2DSFILENAMES', 'ALLWAVE']
    loc.set_sources(lkeys, __NAME__ + '.main()')
    # get this fibers parameters
    ehdr = dict()
    for fiber in p['FIBER_TYPES']:
        p = spirouImage.FiberParams(p, fiber, merge=True)
        # get localisation fit coefficients
        p, loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
        # save all fibers
        loc['ALL_ACC'][fiber] = loc['ACC']
        loc['ALL_ASS'][fiber] = loc['ASS']
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
                                           return_filename=True,
                                           fiber=wave_fiber)
        loc['WAVEPARAMS'], loc['WAVE'], loc['WAVEFILE'] = wout
        loc.set_sources(['WAVE', 'WAVEFILE', 'WAVEPARAMS'], wsource)

        # add wave to all waves
        loc['ALLWAVE'][fiber] = loc['WAVE']
        # ------------------------------------------------------------------
        # Get file names
        # ------------------------------------------------------------------

        if os.path.exists(p['E2DSPREFIX']):
            e2dsfile = p['E2DSPREFIX']
            e2dsfilename = os.path.basename(e2dsfile)

        else:
            # get files using e2ds
            e2dsfilename = '{0}_{1}.fits'.format(p['E2DSPREFIX'], fiber)
            e2dsfile = os.path.join(p['REDUCED_DIR'], e2dsfilename)
            # check if file exists - if it doesn't raise exception
            if not os.path.exists(e2dsfile):
                emsg1 = 'File {0} does not exist in directory {1}'
                emsg2 = '\tcheck E2DSPREFIX (Input argument 2)'
                emsg3 = '\tE2DSPREFIX = {0}'
                emsgs = [emsg1.format(e2dsfile, p['REDUCED_DIR']),
                         emsg2, emsg3.format(p['E2DSPREFIX'])]
                WLOG('error', p['LOG_OPT'], emsgs)
        # get data
        e2dsdata, ehdr, ecdr, ny, nx = spirouImage.ReadData(p, e2dsfile)
        # store data
        loc['E2DSFILES'][fiber] = e2dsdata
        loc['E2DSFILENAMES'].append(e2dsfilename)

    # # ------------------------------------------------------------------
    # # Get telluric and telluric mask and add to loc
    # # ------------------------------------------------------------------
    # # log process
    # wmsg = 'Loading telluric model and locating "good" tranmission'
    # WLOG('', p['LOG_OPT'], wmsg)
    # # load telluric and get mask (add to loc)
    # loc = spirouExM.get_telluric(p, loc)

    # ------------------------------------------------------------------
    # Make 2D map of orders
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], 'Making 2D map of order locations')
    # make the 2D wave-image
    loc = spirouExM.order_profile(p, loc)

    # ------------------------------------------------------------------
    # Make 2D map of wavelengths accounting for shape / tilt
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], 'Mapping pixels on to wavelength grid')
    # make the 2D map of wavelength
    loc = spirouExM.create_wavelength_image(p, loc)

    # ------------------------------------------------------------------
    # Use E2DS file to
    # ------------------------------------------------------------------
    loc = spirouExM.create_image_from_e2ds(p, loc)

    # ------------------------------------------------------------------
    # Apply the flat field
    # ------------------------------------------------------------------
    if p['EM_FLAT_CORRECTION']:
        # log progress
        WLOG('', p['LOG_OPT'], 'Correcting for flat={0}'.format(p['FLATFILE']))
        # normalise flat
        if p['EM_NORM_FLUX']:
            image2 = image2 / np.median(image2)
        # correct for flat
        loc['SPE'] = loc['SPE'] * image2
        loc['SPE0'] = loc['SPE0'] * image2

    # ------------------------------------------------------------------
    # Construct parameters for header
    # ------------------------------------------------------------------
    hdict = OrderedDict()
    # set the version
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    # set the input files
    if loc['SHAPE'] is not None:
        hdict = spirouImage.AddKey(hdict, p['KW_SHAPEFILE'],
                                   value=p['SHAPFILE'])
    else:
        hdict = spirouImage.AddKey(hdict, p['KW_TILTFILE'], value=p['TILTFILE'])
    hdict = spirouImage.AddKey(hdict, p['KW_BLAZFILE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(hdict, p['KW_LOCOFILE'], value=p['LOCOFILE'])
    hdict = spirouImage.AddKey(hdict, p['KW_WAVEFILE'], value=loc['WAVEFILE'])
    # add input filelist
    hdict = spirouImage.AddKey1DList(hdict, p['KW_INFILELIST'], dim1name='file',
                                     values=loc['E2DSFILENAMES'])
    # add name of the localisation fits file used
    hfile = os.path.basename(loc['LOCO_CTR_FILE'])
    hdict = spirouImage.AddKey(hdict, p['kw_EM_LOCFILE'], value=hfile)
    # add the max and min wavelength threshold
    hdict = spirouImage.AddKey(hdict, p['kw_EM_MINWAVE'],
                               value=p['EM_MIN_LAMBDA'])
    hdict = spirouImage.AddKey(hdict, p['kw_EM_MAXWAVE'],
                               value=p['EM_MAX_LAMBDA'])
    # add the transmission cut
    hdict = spirouImage.AddKey(hdict, p['kw_EM_TRASCUT'],
                               value=p['EM_TELL_THRESHOLD'])


    # ------------------------------------------------------------------
    # Deal with output preferences
    # ------------------------------------------------------------------
    # add bad pixel map (if required)
    if p['EM_COMBINED_BADPIX']:
        # get bad pix mask (True where bad)
        badpixmask, bhdr = spirouImage.GetBadPixMap(p, hdr)
        goodpixels = badpixmask == 0
        # apply mask (multiply)
        loc['SPE'] = loc['SPE'] * goodpixels.astype(float)
        loc['SPE0'] = loc['SPE0'] * goodpixels.astype(float)

    # check EM_OUTPUT_TYPE and deal with set to "all"
    if p['EM_OUTPUT_TYPE'] not in ["drs", "raw", "preprocess", "all"]:
        emsg1 = '"EM_OUTPUT_TYPE" not understood'
        emsg2 = '   must be either "drs", "raw" or "preprocess"'
        emsg3 = '   currently EM_OUTPUT_TYPE="{0}"'.format(p['EM_OUTPUT_TYPE'])
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])
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
        WLOG('', p['LOG_OPT'], 'Processing {0} outputs'.format(output))
        # change EM_OUTPUT_TYPE
        p['EM_OUTPUT_TYPE'] = output
        # copy arrays
        out_spe = np.array(loc['SPE'])
        out_spe_0 = np.array(loc['SPE0'])
        out_wave = np.array(loc['WAVEIMAGE'])
        # change image size if needed
        if output in ["raw", "preprocess"]:
            kk = dict(xsize=image.shape[1], ysize=image.shape[0])
            WLOG('', p['LOG_OPT'], 'Resizing/Flipping SPE')
            out_spe = spirouExM.unresize(p, out_spe, **kk)
            WLOG('', p['LOG_OPT'], 'Resizing/Flipping SPE0')
            out_spe_0 = spirouExM.unresize(p, out_spe_0, **kk)
            WLOG('', p['LOG_OPT'], 'Resizing/Flipping WAVEIMAGE')
            out_wave = spirouExM.unresize(p, out_wave, **kk)
            WLOG('', p['LOG_OPT'], 'Rescaling SPE')
            out_spe = out_spe / (p['GAIN'] * p['EXPTIME'])
            WLOG('', p['LOG_OPT'], 'Rescaling SPE0')
            out_spe_0 = out_spe_0 / (p['GAIN'] * p['EXPTIME'])

        # if raw need to rotate (undo pre-processing)
        if output == "raw":
            WLOG('', p['LOG_OPT'], 'Rotating SPE')
            out_spe = np.rot90(out_spe, 1)
            WLOG('', p['LOG_OPT'], 'Rotating SPE0')
            out_spe_0 = np.rot90(out_spe_0, 1)
            WLOG('', p['LOG_OPT'], 'Rotating WAVEIMAGE')
            out_wave = np.rot90(out_wave, 1)

        # ----------------------------------------------------------------------
        # save 2D spectrum, wavelength image and mask to file
        # ----------------------------------------------------------------------
        # save E2DS nan filled
        # construct spectrum filename
        specfitsfile, tag1 = spirouConfig.Constants.WAVE_MAP_SPE_FILE(p)
        specfilename = os.path.split(specfitsfile)[-1]
        # log progress
        wmsg = 'Writing spectrum to file {0}'
        WLOG('', p['LOG_OPT'], wmsg.format(specfilename))
        # write to file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag1)
        p = spirouImage.WriteImage(p, specfitsfile, out_spe, hdict=hdict)
        # ----------------------------------------------------------------------
        # save E2DS 0 filled
        specfitsfile, tag2 = spirouConfig.Constants.WAVE_MAP_SPE0_FILE(p)
        specfilename = os.path.split(specfitsfile)[-1]
        # log progress
        wmsg = 'Writing spectrum to file {0}'
        WLOG('', p['LOG_OPT'], wmsg.format(specfilename))
        # write to file
        hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag2)
        p = spirouImage.WriteImage(p, specfitsfile, out_spe_0, hdict=hdict)
        # ----------------------------------------------------------------------
        # save wave map
        if p['EM_SAVE_WAVE_MAP']:
            # construct waveimage filename
            wavefitsfile, tag3 = spirouConfig.Constants.EM_WAVE_FILE(p)
            wavefilename = os.path.split(wavefitsfile)[-1]
            # log progress
            wmsg = 'Writing wave image to file {0}'
            WLOG('', p['LOG_OPT'], wmsg.format(wavefilename))
            # write to file
            hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag3)
            p = spirouImage.WriteImage(p, wavefitsfile, out_wave, hdict=hdict)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
# # Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================

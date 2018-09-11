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
def main(night_name=None, reffile=None, e2dsprefix=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with arguments being None (i.e. get from sys.argv)
    name, lname = ['reffile', 'e2dsprefix'], ['Reference file', 'E2DS Prefix']
    req, call, call_priority = [True, True], [reffile, e2dsprefix], [True, True]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime([0, 1], [str, str], name,
                                                    req, call, call_priority,
                                                    lname)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='reffile')
    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, reffile = spirouStartup.SingleFileSetup(p, filename=p['REFFILE'])

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Get the required fiber type from the constants file
    # ----------------------------------------------------------------------
    # get the fiber type (set to AB)
    # TODO: SET EM_FIB_TYPE to FIBER_TYPES
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
    # Read tilt slit angle
    # ----------------------------------------------------------------------
    # set source of tilt file
    tsource = __NAME__ + '/main() + /spirouImage.ReadTiltFile'
    # get tilts
    loc['TILT'] = spirouImage.ReadTiltFile(p, hdr)
    loc.set_source('TILT', tsource)
    # get tilt file
    p['TILT_FILE'] = spirouImage.ReadTiltFile(p, hdr, return_filename=True)
    p.set_source('TILT_FILE', tsource)
    # set number of orders from tilt length
    loc['NBO'] = len(loc['TILT'])
    loc.set_source('NBO', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')

    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # storage for fiber parameters
    loc['ALL_ACC'] = OrderedDict()
    loc['ALL_ASS'] = OrderedDict()
    loc['E2DSFILES'] = OrderedDict()
    loc['ALLWAVE'] = OrderedDict()
    loc.set_sources(['ALL_ACC', 'ALL_ASS', 'E2DSFILES', 'ALLWAVE'],
                    __NAME__ + '.main()')
    # get this fibers parameters
    for fiber in p['FIBER_TYPES']:
        p = spirouImage.FiberParams(p, fiber, merge=True)
        # get localisation fit coefficients
        loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
        # save all fibers
        loc['ALL_ACC'][fiber] = loc['ACC']
        loc['ALL_ASS'][fiber] = loc['ASS']
        # ------------------------------------------------------------------
        # Read wavelength solution
        # ------------------------------------------------------------------
        # set source of wave file
        wsource = __NAME__ + '/main() + /spirouImage.ReadWaveFile'
        # get wave solution
        loc['WAVE'] = spirouImage.ReadWaveFile(p, hdr)
        loc.set_source('WAVE', wsource)
        # get wave file
        p['WAVE_FILE'] = spirouImage.ReadWaveFile(p, hdr, return_filename=True)
        p.set_source('WAVE_FILE', wsource)
        # add wave to all waves
        loc['ALLWAVE'][fiber] = loc['WAVE']
        # ------------------------------------------------------------------
        # Get file names
        # ------------------------------------------------------------------
        # get files using e2ds
        e2dsfilename = '{0}_{1}.fits'.format(p['E2DSPREFIX'], fiber)
        e2dsfile = os.path.join(p['REDUCED_DIR'], e2dsfilename)
        # get data
        e2dsdata, hdr, cdr, ny, nx = spirouImage.ReadData(p, e2dsfile)
        # store data
        loc['E2DSFILES'][fiber] = e2dsdata

    # ------------------------------------------------------------------
    # Get telluric and telluric mask and add to loc
    # ------------------------------------------------------------------
    # log process
    wmsg = 'Loading telluric model and locating "good" tranmission'
    WLOG('', p['LOG_OPT'], wmsg)
    # load telluric and get mask (add to loc)
    loc = spirouExM.get_telluric(p, loc)

    # ------------------------------------------------------------------
    # Make 2D map of orders
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], 'Making 2D map of order locations')
    # make the 2D wave-image
    loc = spirouExM.order_profile(p, loc)

    # ------------------------------------------------------------------
    # Make 2D map of wavelengths accounting for tilt
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
    # Construct parameters for header
    # ------------------------------------------------------------------
    hdict = OrderedDict()
    # add version number
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    # add name of the TAPAS y data
    hdict = spirouImage.AddKey(hdict, p['KW_EM_TELLY'], value=loc['TELLSPE'])
    # add name of the localisation fits file used
    hfile = os.path.split(loc['LOCO_CTR_FILE'])[-1]
    hdict = spirouImage.AddKey(hdict, p['kw_EM_LOCFILE'], value=hfile)
    # add name of the tilt solution used
    hfile = os.path.split(p['TILT_FILE'])[-1]
    hdict = spirouImage.AddKey(hdict, p['kw_EM_TILT'], value=hfile)
    # add name of the wavelength solution used
    hfile = os.path.split(p['WAVE_FILE'])[-1]
    hdict = spirouImage.AddKey(hdict, p['kw_EM_WAVE'], value=hfile)
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

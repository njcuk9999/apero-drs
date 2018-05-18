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
__NAME__ = 'telluric_2d_mask.py'
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
# Define main program function
# =============================================================================
def main(night_name=None, reffile=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # deal with arguments being None (i.e. get from sys.argv)
    name, lname = ['reffile'], ['Reference file']
    req, call, call_priority = [True], [reffile], [True]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime([0], [str], name, req, call,
                                                    call_priority, lname)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='reffile')
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)
    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    # get reduced directory + night name
    rdir = p['RAW_DIR']
    # construct and test the reffile
    reffile = spirouStartup.GetFile(p, rdir, p['REFFILE'], kind='TELLMASK')
    # get the fiber type (set to AB)
    p['FIBER'] = 'AB'
    # ----------------------------------------------------------------------
    # Read flat image file
    # ----------------------------------------------------------------------
    # read the image data (for the header only)
    image, hdr, cdr, ny, nx = spirouImage.ReadData(p, reffile)
    # create loc
    loc = ParamDict()
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
    # ------------------------------------------------------------------
    # Get localisation coefficients
    # ------------------------------------------------------------------
    # get this fibers parameters
    p = spirouLOCOR.FiberParams(p, p['FIBER'], merge=True)
    # get localisation fit coefficients
    loc = spirouLOCOR.GetCoeffs(p, hdr, loc=loc)
    # ------------------------------------------------------------------
    # Get telluric and telluric mask and add to loc
    # ------------------------------------------------------------------
    # log process
    wmsg = 'Loading telluric model and locating "good" tranmission'
    WLOG('', p['LOG_OPT'], wmsg)
    # load telluric and get mask (add to loc)
    p, loc = spirouExM.get_telluric(p, loc, hdr)
    # ------------------------------------------------------------------
    # Make 2D map of orders
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], 'Making 2D map of order locations')
    # make the 2D wave-image
    loc = spirouExM.order_profile(loc)
    # ------------------------------------------------------------------
    # Make 2D map of wavelengths accounting for tilt
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], 'Mapping pixels on to wavelength grid')
    # make the 2D map of wavelength
    loc = spirouExM.create_wavelength_image(loc)
    # ------------------------------------------------------------------
    # Use spectra wavelength to create 2D image from wave-image
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], 'Creating image from wave-image interpolation')
    # create image from waveimage
    wkwargs = dict(x=loc['TELL_X'], y=loc['TELL_Y'])
    loc = spirouExM.create_image_from_waveimage(loc, **wkwargs)
    # ------------------------------------------------------------------
    # Create 2D mask (min to max lambda + transmission threshold)
    # ------------------------------------------------------------------
    # log progress
    WLOG('', p['LOG_OPT'], 'Creating wavelength/tranmission mask')
    # create mask
    loc = spirouExM.create_mask(p, loc)

    # ------------------------------------------------------------------
    # Deal with output preferences
    # ------------------------------------------------------------------

    # add bad pixel map (if required)
    if p['EM_COMBINED_BADPIX']:
        # get bad pix mask (True where bad)
        badpixmask = spirouImage.GetBadPixMap(p, hdr)
        goodpixels = ~badpixmask
        # apply mask (multiply)
        loc['TELL_MASK_2D'] = loc['TELL_MASK_2D'] * goodpixels.astype(float)

    # convert waveimage into
    loc['TELL_MASK_2D'] = loc['TELL_MASK_2D'].astype('float')

    # check EM_OUTPUT_TYPE
    if p['EM_OUTPUT_TYPE'] not in ["drs", "raw", "preprocess"]:
        emsg1 = '"EM_OUTPUT_TYPE" not understood'
        emsg2 = '   must be either "drs", "raw" or "preprocess"'
        emsg3 = '   currently EM_OUTPUT_TYPE="{0}"'.format(p['EM_OUTPUT_TYPE'])
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2, emsg3])

    # change image size if needed
    if p['EM_OUTPUT_TYPE'] in ["raw", "preprocess"]:
        kk = dict(xsize=image.shape[1], ysize=image.shape[0])
        loc['SPE'] = spirouExM.unresize(p, loc['SPE'], **kk)
        loc['WAVEIMAGE'] = spirouExM.unresize(p, loc['WAVEIMAGE'], **kk)
        loc['TELL_MASK_2D'] = spirouExM.unresize(p, loc['TELL_MASK_2D'], **kk)

    # if raw need to rotate (undo pre-processing)
    if p['EM_OUTPUT_TYPE'] == "raw":
        loc['SPE'] = np.rot90(loc['SPE'], 1)
        loc['WAVEIMAGE'] = np.rot90(loc['WAVEIMAGE'])
        loc['TELL_MASK_2D'] = np.rot90(loc['TELL_MASK_2D'])

    # ------------------------------------------------------------------
    # Construct parameters for header
    # ------------------------------------------------------------------
    hdict = dict()
    # add name of the TAPAS x data
    hfile = os.path.split(p['TELLWAVE'])[-1]
    hdict = spirouImage.AddKey(hdict, p['KW_EM_TELLX'], value=hfile)
    # add name of the TAPAS y data
    hfile = os.path.split(p['TELLSPE'])[-1]
    hdict = spirouImage.AddKey(hdict, p['KW_EM_TELLY'], value=hfile)
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

    # ----------------------------------------------------------------------
    # save 2D spectrum, wavelength image and mask to file
    # ----------------------------------------------------------------------
    # TODO: move filenames to spirouConst
    # construct spectrum filename
    redfolder = p['REDUCED_DIR']
    specfilename = 'telluric_mapped_spectrum2.fits'
    specfitsfile = os.path.join(redfolder, specfilename)
    # log progress
    wmsg = 'Writing spectrum to file {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(specfilename))
    # write to file
    spirouImage.WriteImage(specfitsfile, loc['SPE'], hdict=hdict)
    # ----------------------------------------------------------------------
    # construct waveimage filename
    wavefilename = 'telluric_mapped_waveimage2.fits'
    wavefitsfile = os.path.join(redfolder, wavefilename)
    # log progress
    wmsg = 'Writing wave image to file {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(wavefilename))
    # write to file
    spirouImage.WriteImage(wavefitsfile, loc['WAVEIMAGE'], hdict=hdict)
    # ----------------------------------------------------------------------
    # construct tell mask 2D filename
    maskfilename = 'telluric_mapped_mask2.fits'
    maskfitsfile = os.path.join(redfolder, maskfilename)
    # log progress
    wmsg = 'Writing telluric mask to file {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(maskfilename))
    # convert boolean mask to integers
    writablemask = np.array(loc['TELL_MASK_2D'], dtype=float)
    # write to file
    spirouImage.WriteImage(maskfitsfile, writablemask, hdict=hdict)
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
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DRIFT-PEAK_E2DS_spirou.py [night_directory] [Reference file name]

# CODE DESCRIPTION HERE

Created on 2017-12-12 at 10:52

@author: cook

Last modified: 2017-12-12 at 10:52

Up-to-date with cal_DRIFT_RAW_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouBACK
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouRV
from SpirouDRS import spirouStartup


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DRIFT-PEAK_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
# def main(night_name=None, reffile=None):
if 1:
    night_name = '20170710'
    reffile = 'fp_fp02a203_e2ds_AB.fits'
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # deal with reference file being None (i.e. get from sys.argv)
    if reffile is None:
        customargs = spirouStartup.GetCustomFromRuntime([0], [str], ['reffile'])
    else:
        customargs = dict(reffile=reffile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.RunInitialStartup(night_name, customargs=customargs)

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    # get reduced directory + night name
    rdir = p['reduced_dir']
    # construct and test the reffile
    reffilename = spirouStartup.GetFile(p, rdir, p['reffile'], 'fp_fp',
                                        'DRIFT')
    # get the fiber type
    p['fiber'] = spirouStartup.GetFiberType(p, reffilename)
    fsource = __NAME__ + '/main()() & spirouStartup.GetFiberType()'
    p.set_source('fiber', fsource)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    speref, hdr, cdr, nbo, nx = spirouImage.ReadData(p, reffilename)
    # add to loc
    loc = ParamDict()
    loc['speref'] = speref
    loc['number_orders'] = nbo
    loc.set_sources(['speref', 'number_orders'], __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Get basic image properties for reference file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, hdr, name='acqtime', kind='unix')
    bjdref = p['acqtime']
    # set sigdet and conad keywords (sigdet is changed later)
    p['kw_CCD_SIGDET'][1] = p['sigdet']
    p['kw_CCD_CONAD'][1] = p['gain']

    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    # get wave image
    loc['wave'] = spirouImage.ReadWaveFile(p, hdr)
    loc.set_source('wave', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

    # ----------------------------------------------------------------------
    # Background correction
    # ----------------------------------------------------------------------
    # log that we are performing background correction
    WLOG('', p['log_opt'], 'Perform background correction')
    # get the box size from constants
    bsize = p['DRIFT_PEAK_MINMAX_BOXSIZE']
    # Loop around the orders
    for order_num in range(loc['number_orders']):
        miny, maxy = spirouBACK.MeasureMinMax(loc['speref'][order_num], bsize)
        loc['speref'] -= miny

    # ----------------------------------------------------------------------
    # Identify FP peaks in reference file
    # ----------------------------------------------------------------------
    # log that we are identifying peaks
    wmsg = 'Identifying FP peaks in reference file: {0}'
    WLOG('', p['log_opt'], wmsg.format(p['reffile']))
    # get the position of FP peaks from reference file
    loc = spirouRV.CreateDriftFile(p, loc)

    # ----------------------------------------------------------------------
    # Removal of suspiciously wide FP lines
    # ----------------------------------------------------------------------
    loc = spirouRV.RemoveWidePeaks(p, loc)

    # ----------------------------------------------------------------------
    # Get reference drift
    # ----------------------------------------------------------------------
    # are we using gaussfit?
    gaussfit = p['drift_peak_getdrift_gaussfit']
    # get drift
    loc['xref'] = spirouRV.GetDrift(p, loc['speref'], loc['ordpeak'],
                                    loc['xpeak'], gaussfit=gaussfit)
    # remove any drifts that are zero (i.e. peak not measured
    loc = spirouRV.RemoveZeroPeaks(p, loc)

    # ------------------------------------------------------------------
    # Reference plots
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive session if needed
        sPlt.start_interactive_session()
        # plot FP spectral order
        sPlt.drift_plot_selected_wave_ref(p, loc)
        # plot photon noise uncertainty
        sPlt.drift_plot_photon_uncertainty(p, loc)

    # ------------------------------------------------------------------
    # Get all other fp_fp*[ext]_e2ds.fits files
    # ------------------------------------------------------------------
    # get reduced folder
    rfolder = p['reduced_dir']
    # Get files, remove fitsfilename, and sort
    prefix = p['reffile'][0:5]
    suffix = '_e2ds_{0}.fits'.format(p['fiber'])
    listfiles = spirouImage.GetAllSimilarFiles(p, rfolder, prefix, suffix)
    # remove reference file
    try:
        listfiles.remove(reffilename)
    except ValueError:
        emsg = 'File {0} not found in {1}'
        WLOG('error', p['log_opt'], emsg.format(reffilename, rfolder))
    # get length of files
    Nfiles = len(listfiles)
    # make sure we have some files
    if Nfiles == 0:
        emsg = 'No additional {0}*{1} files found in {2}'
        WLOG('error', p['log_opt'], emsg.format(prefix, suffix, rfolder))
    else:
        # else Log the number of files found
        wmsg = 'Number of fp_fp files found on directory = {0}'
        WLOG('info', p['log_opt'], wmsg.format(Nfiles))

    # ------------------------------------------------------------------
    # Set up Extract storage for all files
    # ------------------------------------------------------------------
    # decide whether we need to skip (for large number of files)
    if len(listfiles) >= p['DRIFT_NLARGE']:
        skip = p['DRIFT_PEAK_FILE_SKIP']
        Nfiles = int(Nfiles/skip)
    else:
        skip = 1
    # set up storage
    loc['drift'] = np.zeros(Nfiles, loc['number_orders'])
    loc['drift_left'] = np.zeros(Nfiles, loc['number_orders'])
    loc['drift_right'] = np.zeros(Nfiles, loc['number_orders'])
    loc['errdrift'] = np.zeros((Nfiles, loc['number_orders']))
    loc['deltatime'] = np.zeros(Nfiles)
    loc['meanrv'] = np.zeros(Nfiles)
    loc['meanrvleft'] = np.zeros(Nfiles)
    loc['meanrvright'] = np.zeros(Nfiles)
    loc['merrdrift'] = np.zeros(Nfiles)

    WLOG('error', '', '')

    # ------------------------------------------------------------------
    # Loop around all files: correct for dark, reshape, extract and
    #     calculate dvrms and meanpond
    # ------------------------------------------------------------------
    # get the maximum number of orders to use
    nomax = nbo    # p['IC_DRIFT_N_ORDER_MAX']
    wref = 1
    # loop around files
    for i_it in range(Nfiles):
        # get file for this iteration
        fpfile = listfiles[::skip][i_it]
        # Log the file we are reading
        wmsg = 'Reading file {0}'
        WLOG('', p['log_opt'], wmsg.format(os.path.split(fpfile)[-1]))
        # ------------------------------------------------------------------
        # read e2ds files and get timestamp
        # ------------------------------------------------------------------
        # read data
        rout = spirouImage.ReadData(p, filename=fpfile, log=False)
        loc['spe'], hdri, cdri, nxi, nyi = rout
        # get acqtime
        bjdspe = spirouImage.GetAcqTime(p, hdri, name='acqtime', kind='unix',
                                        return_value=1)
        # ----------------------------------------------------------------------
        # Background correction
        # ----------------------------------------------------------------------
        # Loop around the orders
        for order_num in range(loc['number_orders']):
            miny, maxy = spirouBACK.MeasureMinMax(loc['speref'][order_num],
                                                  bsize)
            loc['spe'] -= miny
        # ------------------------------------------------------------------
        # Calculate delta time
        # ------------------------------------------------------------------
        # calculate the time from reference (in hours)
        deltatime = (bjdspe - bjdref) * 24
        # ------------------------------------------------------------------
        # Calculate PearsonR coefficient
        # ------------------------------------------------------------------
        correlation_coeffs = spirouRV.PearsonRtest(p, loc['spe'], loc['speref'])
        # ----------------------------------------------------------------------
        # Get drift with comparison to the reference image
        # ----------------------------------------------------------------------
        # only calculate drift if the correlation between orders and
        #   reference file is above threshold
        if np.min(correlation_coeffs[:nomax]) < 0.5:
            continue
        else:
            # get drifts for each order
            x = spirouRV.GetDrift(p, loc['spe'], loc['ordpeak'], loc['xref'],
                                  gaussfit = gaussfit)
            # get delta v
            dv = (x - loc['xref'])
            # sigma clip
            mask = 0


    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been succesfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))

    # return locals()

    # =============================================================================
    # Start of code
    # =============================================================================


if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    locals = main()


    # =============================================================================
    # End of code
    # =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_DRIFTPEAK_E2DS_spirou.py [night_directory] [Reference file name]

Additional drift recipe fitting the FP peaks with gaussians (slower).
Calculates the drift between the reference E2DS file and all other similar
named E2DS files in the reduced directory.

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

import time
neilstart = time.time()

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_DRIFTPEAK_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__release__ = spirouConfig.Constants.RELEASE()
__date__ = spirouConfig.Constants.LATEST_EDIT()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# switch between new and old
# TODO: Should be new
OLDCODEEXACT = False


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, reffile=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # deal with reference file being None (i.e. get from sys.argv)
    if reffile is None:
        customargs = spirouStartup.GetCustomFromRuntime([0], [str], ['reffile'])
    else:
        customargs = dict(reffile=reffile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='reffile',
                                    mainfitsdir='reduced')
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)
    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    # get reduced directory + night name
    rdir = p['REDUCED_DIR']
    # construct and test the reffile
    gfkwargs = dict(path=rdir, name=p['REFFILE'], prefixes=['fp', 'hc'],
                    kind='DRIFT')
    p['REFFILENAME'] = spirouStartup.GetFile(p, **gfkwargs)
    p.set_source('REFFILENAME', __NAME__ + '/main()')
    # get the fiber type
    p['FIBER'] = spirouStartup.GetFiberType(p, p['REFFILENAME'])
    fsource = __NAME__ + '/main()() & spirouStartup.GetFiberType()'
    p.set_source('FIBER', fsource)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    speref, hdr, cdr, nbo, nx = spirouImage.ReadData(p, p['REFFILENAME'])
    # add to loc
    loc = ParamDict()
    loc['SPEREF'] = speref
    loc['NUMBER_ORDERS'] = nbo
    loc.set_sources(['speref', 'number_orders'], __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Get lamp type
    # ----------------------------------------------------------------------
    # get lamp type
    if 'hc' in p['REFFILE']:
        loc['LAMP'] = 'hc'
    elif 'fp' in p['REFFILE']:
        loc['LAMP'] = 'fp'
    else:
        emsg = 'Wrong type of image for Drift, should be "hc_hc" or "fp_fp"'
        WLOG('error', p['LOG_OPT'], emsg)
    loc.set_source('LAMP', __NAME__ + '/main()')

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
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']

    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    # get wave image
    loc['WAVE'] = spirouImage.ReadWaveFile(p, hdr)
    loc.set_source('WAVE', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

    # ----------------------------------------------------------------------
    # Read Flat file
    # ----------------------------------------------------------------------
    # get flat
    loc['FLAT'] = spirouImage.ReadFlatFile(p, hdr)
    loc.set_source('FLAT', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    loc['FLAT'] = np.where(loc['FLAT'] == 0, 1.0, loc['FLAT'])
    # correct for flat file
    loc['SPEREF'] = loc['SPEREF']/loc['FLAT']

    # ----------------------------------------------------------------------
    # Background correction
    # ----------------------------------------------------------------------
    # log that we are performing background correction
    WLOG('', p['LOG_OPT'], 'Perform background correction')
    # get the box size from constants
    bsize = p['DRIFT_PEAK_MINMAX_BOXSIZE']
    # Loop around the orders
    for order_num in range(loc['NUMBER_ORDERS']):
        miny, maxy = spirouBACK.MeasureMinMax(loc['SPEREF'][order_num], bsize)
        loc['SPEREF'][order_num] = loc['SPEREF'][order_num] - miny

    # ----------------------------------------------------------------------
    # Identify FP peaks in reference file
    # ----------------------------------------------------------------------
    # log that we are identifying peaks
    wmsg = 'Identification of lines in reference file: {0}'
    WLOG('', p['LOG_OPT'], wmsg.format(p['REFFILE']))
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
    gaussfit = p['DRIFT_PEAK_GETDRIFT_GAUSSFIT']
    # get drift
    loc['XREF'] = spirouRV.GetDrift(p, loc['SPEREF'], loc['ORDPEAK'],
                                    loc['XPEAK'], gaussfit=gaussfit)
    loc.set_source('XREF', __NAME__ + '/main()')
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

    # ------------------------------------------------------------------
    # Get all other fp_fp*[ext]_e2ds.fits files
    # ------------------------------------------------------------------
    # get reduced folder
    rfolder = p['REDUCED_DIR']
    # Get files, remove fitsfilename, and sort
    prefix = p['REFFILE'][0:5]
    suffix = '_e2ds_{0}.fits'.format(p['FIBER'])
    listfiles = spirouImage.GetAllSimilarFiles(p, rfolder, prefix, suffix)
    # remove reference file
    try:
        listfiles.remove(p['REFFILENAME'])
    except ValueError:
        emsg = 'File {0} not found in {1}'
        WLOG('error', p['LOG_OPT'], emsg.format(p['REFFILENAME'], rfolder))
    # get length of files
    nfiles = len(listfiles)
    # make sure we have some files
    if nfiles == 0:
        emsg = 'No additional {0}*{1} files found in {2}'
        WLOG('error', p['LOG_OPT'], emsg.format(prefix, suffix, rfolder))
    else:
        # else Log the number of files found
        wmsg = 'Number of files found on directory = {0}'
        WLOG('info', p['LOG_OPT'], wmsg.format(nfiles))

    # ------------------------------------------------------------------
    # Set up Extract storage for all files
    # ------------------------------------------------------------------
    # decide whether we need to skip (for large number of files)
    if len(listfiles) >= p['DRIFT_NLARGE']:
        skip = p['DRIFT_PEAK_FILE_SKIP']
        nfiles = int(nfiles/skip)
    else:
        skip = 1
    # set up storage
    loc['DRIFT'] = np.zeros((nfiles, loc['NUMBER_ORDERS']))
    loc['DRIFT_LEFT'] = np.zeros((nfiles, loc['NUMBER_ORDERS']))
    loc['DRIFT_RIGHT'] = np.zeros((nfiles, loc['NUMBER_ORDERS']))
    loc['ERRDRIFT'] = np.zeros((nfiles, loc['NUMBER_ORDERS']))
    loc['DELTATIME'] = np.zeros(nfiles)
    loc['MEANRV'] = np.zeros(nfiles)
    loc['MEANRV_LEFT'] = np.zeros(nfiles)
    loc['MEANRV_RIGHT'] = np.zeros(nfiles)
    loc['MERRDRIFT'] = np.zeros(nfiles)
    loc['FLUXRATIO'] = np.zeros(nfiles)
    # add sources
    source = __NAME__ + '/main()'
    keys = ['drift', 'drift_left', 'drift_right', 'errdrift', 'deltatime',
            'meanrv', 'meanrv_left', 'meanrv_right', 'merrdrift', 'fluxratio']
    loc.set_sources(keys, source)

    # ------------------------------------------------------------------
    # Loop around all files: correct for dark, reshape, extract and
    #     calculate dvrms and meanpond
    # ------------------------------------------------------------------
    # get the maximum number of orders to use
    nomin = p['IC_DRIFT_PEAK_N_ORDER_MIN']
    nomax = p['IC_DRIFT_PEAK_N_ORDER_MAX']
    # loop around files
    for i_it in range(nfiles):
        # get file for this iteration
        fpfile = listfiles[::skip][i_it]
        # Log the file we are reading
        wmsg = 'Reading file {0}'
        WLOG('', p['LOG_OPT'], wmsg.format(os.path.split(fpfile)[-1]))
        # ------------------------------------------------------------------
        # read e2ds files and get timestamp
        # ------------------------------------------------------------------
        # read data
        rout = spirouImage.ReadData(p, filename=fpfile, log=False)
        loc['SPE'], hdri, cdri, nxi, nyi = rout
        # apply flat
        loc['SPE'] = loc['SPE']/loc['FLAT']
        # get acqtime
        bjdspe = spirouImage.GetAcqTime(p, hdri, name='acqtime', kind='unix',
                                        return_value=1)
        # ----------------------------------------------------------------------
        # Background correction
        # ----------------------------------------------------------------------
        # Loop around the orders
        for order_num in range(loc['NUMBER_ORDERS']):
            miny, maxy = spirouBACK.MeasureMinMax(loc['SPE'][order_num],
                                                  bsize)
            loc['SPE'][order_num] = loc['SPE'][order_num] - miny
        # ------------------------------------------------------------------
        # calculate flux ratio
        # ------------------------------------------------------------------
        sorder = p['IC_DRIFT_ORDER_PLOT']
        fratio = np.sum(loc['SPE'][sorder])/np.sum(loc['SPEREF'][sorder])
        loc['FLUXRATIO'][i_it] = fratio
        # ------------------------------------------------------------------
        # Calculate delta time
        # ------------------------------------------------------------------
        # calculate the time from reference (in hours)
        loc['DELTATIME'][i_it] = (bjdspe - bjdref) * 24
        # ------------------------------------------------------------------
        # Calculate PearsonR coefficient
        # ------------------------------------------------------------------
        pargs = [loc['NUMBER_ORDERS'], loc['SPE'], loc['SPEREF']]
        correlation_coeffs = spirouRV.PearsonRtest(*pargs)
        # ----------------------------------------------------------------------
        # Get drift with comparison to the reference image
        # ----------------------------------------------------------------------
        # only calculate drift if the correlation between orders and
        #   reference file is above threshold
        prcut = p['DRIFT_PEAK_PEARSONR_CUT']
        if np.min(correlation_coeffs[nomin:nomax]) > prcut:
            # get drifts for each order
            dargs = [p, loc['SPE'], loc['ORDPEAK'], loc['XREF']]
            x = spirouRV.GetDrift(*dargs, gaussfit=gaussfit)
            # get delta v
            loc['DV'] = (x - loc['XREF']) * loc['VRPEAK']
            # sigma clip
            loc = spirouRV.SigmaClip(loc, sigma=p['DRIFT_PEAK_SIGMACLIP'])
            # work out median drifts per order
            loc = spirouRV.DriftPerOrder(loc, i_it)
            # work out mean drift across all orders
            loc = spirouRV.DriftAllOrders(loc, i_it, nomin, nomax)
            # log the mean drift
            wmsg = ('Time from ref= {0:.2f} h '
                    '- Flux Ratio= {1:.2f} '
                    '- Drift mean= {2:.2f} +- '
                    '{3:.2f} m/s')
            wargs = [loc['DELTATIME'][i_it], loc['FLUXRATIO'][i_it],
                     loc['MEANRV'][i_it], loc['MERRDRIFT'][i_it]]
            WLOG('info', p['LOG_OPT'], wmsg.format(*wargs))
        # else we can't use this extract
        else:
            if p['DRS_PLOT']:
                # start interactive session if needed
                sPlt.start_interactive_session()
                # plot comparison between spe and ref
                sPlt.drift_plot_correlation_comp(p, loc, correlation_coeffs)
            # log that we cannot use this extraction
            wmsg1 = 'The correlation of some orders compared to the template is'
            wmsg2 = '   < {0}, something went wrong in the extract.'
            WLOG('warning', p['LOG_OPT'], wmsg1)
            WLOG('warning', p['LOG_OPT'], wmsg2.format(prcut))
    # ------------------------------------------------------------------
    # peak to peak drift
    driftptp = np.max(loc['MEANRV']) - np.min(loc['MEANRV'])
    driftrms = np.std(loc['MEANRV'])
    # log th etotal drift peak-to-peak and rms
    wmsg = ('Total drift Peak-to-Peak={0:.3f} m/s RMS={1:.3f} m/s in '
            '{2:.2f} hour')
    wargs = [driftptp, driftrms, np.max(loc['DELTATIME'])]
    WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

    # ------------------------------------------------------------------
    # Plot of mean drift
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive session if needed
        sPlt.start_interactive_session()
        # plot delta time against median drift
        sPlt.drift_peak_plot_dtime_against_drift(p, loc)

    # ------------------------------------------------------------------
    # Save drift values to file
    # ------------------------------------------------------------------
    # construct filename
    driftfits = spirouConfig.Constants.DRIFTPEAK_E2DS_FITS_FILE(p)
    driftfitsname = os.path.split(driftfits)[-1]
    # log that we are saving drift values
    wmsg = 'Saving drift values of Fiber {0} in {1}'
    WLOG('', p['LOG_OPT'], wmsg.format(p['FIBER'], driftfitsname))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # save drift values
    spirouImage.WriteImage(driftfits, loc['DRIFT'], hdict)

    # ------------------------------------------------------------------
    # print .tbl result
    # ------------------------------------------------------------------
    # construct filename
    drifttbl = spirouConfig.Constants.DRIFTPEAK_E2DS_TBL_FILE(p)
    drifttblname = os.path.split(drifttbl)[-1]
    # construct and write table
    columnnames = ['time', 'drift', 'drifterr', 'drift_left', 'drift_right']
    columnformats = ['7.4f', '6.2f', '6.3f', '6.2f', '6.2f']
    columnvalues = [loc['DELTATIME'], loc['MEANRV'], loc['MERRDRIFT'],
                    loc['MEANRV_LEFT'], loc['MEANRV_RIGHT']]
    table = spirouImage.MakeTable(columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # write table
    wmsg = 'Average Drift saved in {0} Saved '
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(drifttblname))
    spirouImage.WriteTable(table, drifttbl, fmt='ascii.rst')

    # ------------------------------------------------------------------
    # Plot amp and llpeak
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] and p['DRIFT_PEAK_PLOT_LINE_LOG_AMP']:
        # start interactive session if needed
        sPlt.start_interactive_session()
        # plot delta time against median drift
        sPlt.drift_peak_plot_llpeak_amps(p, loc)

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

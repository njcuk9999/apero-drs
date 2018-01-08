#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DRIFTPEAK_E2DS_spirou.py [night_directory] [Reference file name]

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
    pass
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
    # Get lamp type
    # ----------------------------------------------------------------------
    # get lamp type
    if 'hc' in p['reffile']:
        loc['lamp'] = 'hc'
    elif 'fp' in p['reffile']:
        loc['lamp'] = 'fp'
    else:
        emsg = 'Wrong type of image for Drift, should be "hc_hc" or "fp_fp"'
        WLOG('error', p['log_opt'], emsg)
    loc.set_source('lamp', __NAME__ + '/main()')

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
    # Read Flat file
    # ----------------------------------------------------------------------
    # get flat
    loc['flat'] = spirouImage.ReadFlatFile(p, hdr)
    loc.set_source('flat', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    loc['flat'] = np.where(loc['flat'] == 0, 1.0, loc['flat'])
    # correct for flat file
    loc['speref'] = loc['speref']/loc['flat']

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
        loc['speref'][order_num] = loc['speref'][order_num] - miny

    # ----------------------------------------------------------------------
    # Identify FP peaks in reference file
    # ----------------------------------------------------------------------
    # log that we are identifying peaks
    wmsg = 'Identification of lines in reference file: {0}'
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
    loc.set_source('xref', __NAME__ + '/main()')
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
        wmsg = 'Number of files found on directory = {0}'
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
    loc['drift'] = np.zeros((Nfiles, loc['number_orders']))
    loc['drift_left'] = np.zeros((Nfiles, loc['number_orders']))
    loc['drift_right'] = np.zeros((Nfiles, loc['number_orders']))
    loc['errdrift'] = np.zeros((Nfiles, loc['number_orders']))
    loc['deltatime'] = np.zeros(Nfiles)
    loc['meanrv'] = np.zeros(Nfiles)
    loc['meanrv_left'] = np.zeros(Nfiles)
    loc['meanrv_right'] = np.zeros(Nfiles)
    loc['merrdrift'] = np.zeros(Nfiles)
    loc['fluxratio'] = np.zeros(Nfiles)
    # add sources
    source = __NAME__ + '/main()'
    keys = ['drift', 'drift_left', 'drift_right', 'err_drift', 'deltatime',
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
        # apply flat
        loc['spe'] = loc['spe']/loc['flat']
        # get acqtime
        bjdspe = spirouImage.GetAcqTime(p, hdri, name='acqtime', kind='unix',
                                        return_value=1)
        # ----------------------------------------------------------------------
        # Background correction
        # ----------------------------------------------------------------------
        # Loop around the orders
        for order_num in range(loc['number_orders']):
            miny, maxy = spirouBACK.MeasureMinMax(loc['spe'][order_num],
                                                  bsize)
            loc['spe'][order_num] = loc['spe'][order_num] - miny
        # ------------------------------------------------------------------
        # calculate flux ratio
        # ------------------------------------------------------------------
        sorder = p['IC_DRIFT_ORDER_PLOT']
        fratio = np.sum(loc['spe'][sorder])/np.sum(loc['speref'][sorder])
        loc['fluxratio'][i_it] = fratio
        # ------------------------------------------------------------------
        # Calculate delta time
        # ------------------------------------------------------------------
        # calculate the time from reference (in hours)
        loc['deltatime'][i_it] = (bjdspe - bjdref) * 24
        # ------------------------------------------------------------------
        # Calculate PearsonR coefficient
        # ------------------------------------------------------------------
        pargs = [loc['number_orders'], loc['spe'], loc['speref']]
        correlation_coeffs = spirouRV.PearsonRtest(*pargs)
        # ----------------------------------------------------------------------
        # Get drift with comparison to the reference image
        # ----------------------------------------------------------------------
        # only calculate drift if the correlation between orders and
        #   reference file is above threshold
        prcut = p['drift_peak_pearsonr_cut']
        if np.min(correlation_coeffs[nomin:nomax]) > prcut:
            # get drifts for each order
            dargs = [p, loc['spe'], loc['ordpeak'], loc['xref']]
            x = spirouRV.GetDrift(*dargs, gaussfit=gaussfit)
            # get delta v
            loc['dv'] = (x - loc['xref']) * loc['vrpeak']
            # sigma clip
            loc = spirouRV.SigmaClip(loc, sigma=p['drift_peak_sigmaclip'])
            # work out median drifts per order
            loc = spirouRV.DriftPerOrder(loc, i_it)
            # work out mean drift across all orders
            loc = spirouRV.DriftAllOrders(loc, i_it, nomin, nomax)
            # log the mean drift
            wmsg = ('Time from ref= {0:.2f} h '
                    '- Flux Ratio= {1:.2f} '
                    '- Drift mean= {2:.2f} +- '
                    '{3:.2f} m/s')
            wargs = [loc['deltatime'][i_it], loc['fluxratio'][i_it],
                     loc['meanrv'][i_it], loc['merrdrift'][i_it]]
            WLOG('info', p['log_opt'], wmsg.format(*wargs))
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
            WLOG('warning', p['log_opt'], wmsg1)
            WLOG('warning', p['log_opt'], wmsg2.format(prcut))
    # ------------------------------------------------------------------
    # peak to peak drift
    driftptp = np.max(loc['meanrv']) - np.min(loc['meanrv'])
    driftrms = np.std(loc['meanrv'])
    # log th etotal drift peak-to-peak and rms
    wmsg = ('Total drift Peak-to-Peak={0:.3f} m/s RMS={1:.3f} m/s in '
            '{2:.2f} hour')
    wargs = [driftptp, driftrms, np.max(loc['deltatime'])]
    WLOG('', p['log_opt'], wmsg.format(*wargs))

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
    reducedfolder = p['reduced_dir']
    drift_ext = '_driftnew_{0}.fits'.format(p['fiber'])
    driftfits = reffilename.replace('.fits', drift_ext)
    # log that we are saving drift values
    wmsg = 'Saving drift values of Fiber {0} in {1}'
    WLOG('', p['log_opt'], wmsg.format(p['fiber'], driftfits))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # save drift values
    spirouImage.WriteImage(os.path.join(reducedfolder, driftfits),
                           loc['drift'], hdict)

    # ------------------------------------------------------------------
    # print .tbl result
    # ------------------------------------------------------------------
    # construct filename
    reducedfolder = p['reduced_dir']
    drift_ext = '_driftnew_{0}.tbl'.format(p['fiber'])
    drifttbl = reffilename.replace('.fits', drift_ext)
    drifttblfilename = os.path.join(reducedfolder, drifttbl)
    # construct and write table
    columnnames = ['time', 'drift', 'drifterr', 'drift_left', 'drift_right']
    columnformats = ['7.4f', '6.2f', '6.3f', '6.2f', '6.2f']
    columnvalues = [loc['deltatime'], loc['meanrv'], loc['merrdrift'],
                    loc['meanrv_left'], loc['meanrv_right']]
    table = spirouImage.MakeTable(columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # write table
    wmsg = 'Average Drift saved in {0} Saved '
    WLOG('', p['log_opt'] + p['fiber'], wmsg.format(drifttblfilename))
    spirouImage.WriteTable(table, drifttblfilename, fmt='ascii.rst')

    # ------------------------------------------------------------------
    # Plot amp and llpeak
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] and p['drift_peak_plot_line_log_amp']:
        # start interactive session if needed
        sPlt.start_interactive_session()
        # plot delta time against median drift
        sPlt.drift_peak_plot_llpeak_amps(p, loc)

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

    print('Neil timing: AT-4 took {0} seconds'.format(time.time() - neilstart))

# =============================================================================
# End of code
# =============================================================================

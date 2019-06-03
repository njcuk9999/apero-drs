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
OLDCODEEXACT = False


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, reffile=None):
    """
    cal_DRIFTPEAK_E2DS_spirou.py main function, if arguments are None uses
    arguments from run time i.e.:
        cal_DRIFTPEAK_E2DS_spirou.py [night_directory] [reffile]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param reffile: string, the reference file to use

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with reference file being None (i.e. get from sys.argv)
    if reffile is None:
        customargs = spirouStartup.GetCustomFromRuntime(p,
                                                        [0], [str], ['reffile'])
    else:
        customargs = dict(reffile=reffile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='reffile',
                                    mainfitsdir='reduced')

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, reffilename = spirouStartup.SingleFileSetup(p, filename=p['REFFILE'])
    p['REFFILENAME'] = reffilename
    p.set_source('REFFILENAME', __NAME__ + '.main()')

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    speref, hdr, cdr, nbo, nx = spirouImage.ReadData(p, p['REFFILENAME'])
    # add to loc
    loc = ParamDict()
    loc['SPEREF'] = speref
    loc['NUMBER_ORDERS'] = nbo
    loc.set_sources(['SPEREF', 'NUMBER_ORDERS'], __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Get lamp type
    # ----------------------------------------------------------------------
    # get lamp type
    if p['KW_EXT_TYPE'][0] in hdr:
        ext_type = hdr[p['KW_EXT_TYPE'][0]]
        drift_types = p['DRIFT_PEAK_ALLOWED_TYPES'].keys()
        found = False
        for kind in drift_types:
            if ext_type == kind:
                loc['LAMP'] = p['DRIFT_PEAK_ALLOWED_TYPES'][kind]
                found = True
        if not found:
            eargs1 = [p['KW_EXT_TYPE'][0], ' or '.join(drift_types)]
            emsg1 = ('Wrong type of image for Drift, header key "{0}" should be'
                     '{1}'.format(*eargs1))
            emsg2 = '\tPlease check DRIFT_PEAK_ALLOWED_TYPES'
            WLOG(p, 'error', [emsg1, emsg2])
    else:
        emsg = 'Header key = "{0}" missing from file {1}'
        eargs = [p['KW_EXT_TYPE'][0], p['REFFILENAME']]
        WLOG(p, 'error', emsg.format(*eargs))
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
    p = spirouImage.GetAcqTime(p, hdr, name='acqtime', kind='julian')
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']

    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # get wave image
    source = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    wout = spirouImage.GetWaveSolution(p, hdr=hdr, return_wavemap=True,
                                       return_filename=True, fiber=wave_fiber)
    _, loc['WAVE'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    loc.set_sources(['WAVE', 'WAVEFILE', 'WSOURCE'], source)

    # ----------------------------------------------------------------------
    # Read Flat file
    # ----------------------------------------------------------------------
    # get flat
    p, loc['FLAT'] = spirouImage.ReadFlatFile(p, hdr)
    loc.set_source('FLAT', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    loc['FLAT'] = np.where(loc['FLAT'] == 0, 1.0, loc['FLAT'])
    # correct for flat file
    loc['SPEREF'] = loc['SPEREF']/loc['FLAT']

    # ----------------------------------------------------------------------
    # Background correction
    # ----------------------------------------------------------------------
    # test whether we want to subtract background
    if p['IC_DRIFT_BACK_CORR']:
        # Loop around the orders
        for order_num in range(loc['NUMBER_ORDERS']):
            # get the box size from constants
            bsize = p['DRIFT_PEAK_MINMAX_BOXSIZE']
            # Measurethe min and max flux
            miny, maxy = spirouBACK.MeasureMinMax(loc['SPEREF'][order_num],
                                                  bsize)
            # subtract off the background (miny)
            loc['SPEREF'][order_num] = loc['SPEREF'][order_num] - miny

    # ----------------------------------------------------------------------
    # Identify FP peaks in reference file
    # ----------------------------------------------------------------------
    # log that we are identifying peaks
    wmsg = 'Identification of lines in reference file: {0}'
    WLOG(p, '', wmsg.format(p['REFFILE']))
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
    if p['DRS_PLOT'] > 0:
        # start interactive session if needed
        sPlt.start_interactive_session(p)
        # plot FP spectral order
        sPlt.drift_plot_selected_wave_ref(p, loc)

    # ------------------------------------------------------------------
    # Get all other files that match kw_OUTPUT and kw_EXT_TYPE from
    #    ref file
    # ------------------------------------------------------------------
    # get files
    listfiles, listtypes = spirouImage.GetSimilarDriftFiles(p, hdr)
    # get the number of files
    nfiles = len(listfiles)
    # Log the number of files found
    wmsgs = ['Number of files found on directory = {0}'.format(nfiles),
             '\tExtensions allowed:']
    for listtype in listtypes:
        wmsgs.append('\t\t - {0}'.format(listtype))
    WLOG(p, 'info', wmsgs)

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
        WLOG(p, '', wmsg.format(os.path.split(fpfile)[-1]))
        # ------------------------------------------------------------------
        # read e2ds files and get timestamp
        # ------------------------------------------------------------------
        # read data
        rout = spirouImage.ReadData(p, filename=fpfile, log=False)
        loc['SPE'], hdri, cdri, nxi, nyi = rout
        # apply flat
        loc['SPE'] = loc['SPE']/loc['FLAT']
        # get acqtime
        bjdspe = spirouImage.GetAcqTime(p, hdri, name='acqtime', return_value=1,
                                        kind='julian')
        # ----------------------------------------------------------------------
        # Background correction
        # ----------------------------------------------------------------------
        # test whether we want to subtract background
        if p['IC_DRIFT_BACK_CORR']:
            # Loop around the orders
            for order_num in range(loc['NUMBER_ORDERS']):
                # get the box size from constants
                bsize = p['DRIFT_PEAK_MINMAX_BOXSIZE']
                # Measurethe min and max flux
                miny, maxy = spirouBACK.MeasureMinMax(loc['SPE'][order_num],
                                                      bsize)
                # subtract off the background (miny)
                loc['SPE'][order_num] = loc['SPE'][order_num] - miny

        # ------------------------------------------------------------------
        # calculate flux ratio
        # ------------------------------------------------------------------
        sorder = p['IC_DRIFT_ORDER_PLOT']
        fratio = np.nansum(loc['SPE'][sorder])/np.nansum(loc['SPEREF'][sorder])
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
            loc = spirouRV.DriftAllOrders(p, loc, i_it, nomin, nomax)
            # log the mean drift
            wmsg = ('Time from ref= {0:.2f} h - Flux Ratio= {1:.3f} '
                    '- Drift mean= {2:.2f} +- {3:.2f} m/s')
            wargs = [loc['DELTATIME'][i_it], loc['FLUXRATIO'][i_it],
                     loc['MEANRV'][i_it], loc['MERRDRIFT'][i_it]]
            WLOG(p, 'info', wmsg.format(*wargs))
        # else we can't use this extract
        else:
            if p['DRS_PLOT'] > 0:
                # start interactive session if needed
                sPlt.plt.ioff()
                # plot comparison between spe and ref
                sPlt.drift_plot_correlation_comp(p, loc, correlation_coeffs,
                                                 i_it)
                sPlt.plt.show()
                sPlt.plt.close()
                # turn interactive plotting back on
                sPlt.plt.ion()
            # log that we cannot use this extraction
            wmsg1 = 'The correlation of some orders compared to the template is'
            wmsg2 = '   < {0}, something went wrong in the extract.'
            WLOG(p, 'warning', wmsg1)
            WLOG(p, 'warning', wmsg2.format(prcut))
    # ------------------------------------------------------------------
    # peak to peak drift
    driftptp = np.max(loc['MEANRV']) - np.min(loc['MEANRV'])
    driftrms = np.std(loc['MEANRV'])
    # log th etotal drift peak-to-peak and rms
    wmsg = ('Total drift Peak-to-Peak={0:.3f} m/s RMS={1:.3f} m/s in '
            '{2:.2f} hour')
    wargs = [driftptp, driftrms, np.max(loc['DELTATIME'])]
    WLOG(p, '', wmsg.format(*wargs))

    # ------------------------------------------------------------------
    # Plot of mean drift
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive session if needed
        sPlt.start_interactive_session(p)
        # plot delta time against median drift
        sPlt.drift_peak_plot_dtime_against_drift(p, loc)

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
    # Save drift values to file
    # ------------------------------------------------------------------
    # get raw input file name
    raw_infile = os.path.basename(p['REFFILE'])
    # construct filename
    driftfits, tag = spirouConfig.Constants.DRIFTPEAK_E2DS_FITS_FILE(p)
    driftfitsname = os.path.split(driftfits)[-1]
    # log that we are saving drift values
    wmsg = 'Saving drift values of Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(p['FIBER'], driftfitsname))
    # add keys from original header file
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    # set the version
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    # set the input files
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBFLAT'], value=p['FLATFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_REFFILE'], value=raw_infile)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'], value=loc['WAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # save drift values
    p = spirouImage.WriteImage(p, driftfits, loc['DRIFT'], hdict)

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
    table = spirouImage.MakeTable(p, columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # write table
    wmsg = 'Average Drift saved in {0} Saved '
    WLOG(p, '', wmsg.format(drifttblname))
    spirouImage.WriteTable(p, table, drifttbl, fmt='ascii.rst')

    # ------------------------------------------------------------------
    # Plot amp and llpeak
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] and p['DRIFT_PEAK_PLOT_LINE_LOG_AMP']:
        # start interactive session if needed
        sPlt.start_interactive_session(p)
        # plot delta time against median drift
        sPlt.drift_peak_plot_llpeak_amps(p, loc)

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_DRIFT_E2DS_spirou.py [night_directory] [Reference file name]

Primary drift recipe. Calculates the drift between the reference E2DS file and
all other similar named E2DS files in the reduced directory.

Created on 2017-10-12 at 15:21

@author: cook

Last modified: 2017-12-12 at 10:55

Up-to-date with cal_DRIFT_E2DS_spirou AT-4 V47
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
__NAME__ = 'cal_DRIFT_E2DS_spirou.py'
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
def main(night_name=None, reffile=None):
    """
    cal_DRIFT_E2DS_spirou.py main function, if arguments are None uses
    arguments from run time i.e.:
        cal_DRIFT_E2DS_spirou.py [night_directory] [reffile]

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
        customargs = spirouStartup.GetCustomFromRuntime(p, [0], [str],
                                                        ['reffile'])
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
    speref, hdr, cdr, nbo, nx = spirouImage.ReadData(p, reffilename)
    # add to loc
    loc = ParamDict()
    loc['SPEREF'] = speref
    loc['NUMBER_ORDERS'] = nbo
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
    wout = spirouImage.GetWaveSolution(p, hdr=hdr, fiber=wave_fiber,
                                       return_wavemap=True,
                                       return_filename=True)
    _, loc['WAVE'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    source = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    loc.set_sources(['WAVE', 'WAVEFILE', 'WSOURCE'], source)
    # ----------------------------------------------------------------------
    # Read Flat file
    # ----------------------------------------------------------------------
    # get flat
    p, loc['FLAT'] = spirouImage.ReadFlatFile(p, hdr)
    loc.set_source('FLAT', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    loc['FLAT'] = np.where(loc['FLAT'] == 0, 1.0, loc['FLAT'])

    # ----------------------------------------------------------------------
    # Background correction
    # ----------------------------------------------------------------------
    # log that we are performing background correction
    if p['IC_DRIFT_BACK_CORR']:
        WLOG(p, '', 'Perform background correction')
        # get the box size from constants
        bsize = p['DRIFT_PEAK_MINMAX_BOXSIZE']
        # Loop around the orders
        for order_num in range(loc['NUMBER_ORDERS']):
            miny, maxy = spirouBACK.MeasureMinMax(loc['SPEREF'][order_num],
                                                  bsize)
            loc['SPEREF'][order_num] = loc['SPEREF'][order_num] - miny

    # ------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['SPEREF'], loc['WAVE']]
    dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DRIFT_BOXSIZE'],
                   threshold=p['IC_DRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)
    # save to loc
    loc['DVRMSREF'], loc['WMEANREF'] = dvrmsref, wmeanref
    loc.set_sources(['dvrmsref', 'wmeanref'], __NAME__ + '/main()()')
    # log the estimated RV uncertainty
    wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f} m/s'
    WLOG(p, 'info', wmsg.format(p['FIBER'], wmeanref))

    # ------------------------------------------------------------------
    # Reference plots
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive session if needed
        sPlt.start_interactive_session(p)
        # plot FP spectral order
        sPlt.drift_plot_selected_wave_ref(p, loc)
        # plot photon noise uncertainty
        sPlt.drift_plot_photon_uncertainty(p, loc)

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
        skip = p['DRIFT_E2DS_FILE_SKIP']
        nfiles = int(nfiles/skip)
    else:
        skip = 1
    # set up storage
    loc['DRIFT'] = np.zeros((nfiles, loc['NUMBER_ORDERS']))
    loc['ERRDRIFT'] = np.zeros((nfiles, loc['NUMBER_ORDERS']))
    loc['DELTATIME'] = np.zeros(nfiles)
    # set loc sources
    keys = ['drift', 'errdrift', 'deltatime']
    loc.set_sources(keys, __NAME__ + '/main()()')

    # ------------------------------------------------------------------
    # Loop around all files: correct for dark, reshape, extract and
    #     calculate dvrms and meanpond
    # ------------------------------------------------------------------
    wref = 1
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
        # get acqtime
        bjdspe = spirouImage.GetAcqTime(p, hdri, name='acqtime', return_value=1,
                                        kind='julian')
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
        # Compute photon noise uncertainty for iteration file
        # ------------------------------------------------------------------
        # set up the arguments for DeltaVrms2D
        dargs = [loc['SPE'], loc['WAVE']]
        dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'],
                       size=p['IC_DRIFT_BOXSIZE'],
                       threshold=p['IC_DRIFT_MAXFLUX'])
        # run DeltaVrms2D
        dvrmsspe, wmodespe = spirouRV.DeltaVrms2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Compute the correction of the cosmics and re-normalisation by
        #   comparison with the reference spectrum
        # ------------------------------------------------------------------
        # correction of the cosmics and renomalisation by comparison with
        #   the reference spectrum
        dargs = [p, loc['SPEREF'], loc['SPE']]
        dkwargs = dict(threshold=p['IC_DRIFT_MAXFLUX'],
                       size=p['IC_DRIFT_BOXSIZE'],
                       cut=p['IC_DRIFT_CUT_E2DS'])
        spen, cfluxr, cpt = spirouRV.ReNormCosmic2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Calculate the RV drift
        # ------------------------------------------------------------------
        dargs = [loc['SPEREF'], spen, loc['WAVE']]
        dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'],
                       threshold=p['IC_DRIFT_MAXFLUX'],
                       size=p['IC_DRIFT_BOXSIZE'])
        rv = spirouRV.CalcRVdrift2D(*dargs, **dkwargs)
        # ------------------------------------------------------------------
        # Calculate delta time
        # ------------------------------------------------------------------
        # calculate the time from reference (in hours)
        deltatime = (bjdspe - bjdref) * 24
        # ------------------------------------------------------------------
        # Calculate RV properties
        # ------------------------------------------------------------------
        # calculate the mean flux ratio
        meanfratio = np.nanmean(cfluxr)
        # calculate the weighted mean radial velocity
        wref = 1.0/dvrmsref
        meanrv = -1.0 * np.nansum(rv * wref)/np.nansum(wref)
        err_meanrv = np.sqrt(dvrmsref + dvrmsspe)
        merr = 1./np.sqrt(np.nansum((1./err_meanrv)**2))
        # Log the RV properties
        wmsg = ('Time from ref={0:.2f} h  - Drift mean= {1:.2f} +- {2:.3f} m/s '
                '- Flux ratio= {3:.3f} - Nb Comsic= {4}')
        WLOG(p, '', wmsg.format(deltatime, meanrv, merr,
                                           meanfratio, cpt))
        # add this iteration to storage
        loc['DRIFT'][i_it] = -1.0 * rv
        loc['ERRDRIFT'][i_it] = err_meanrv
        loc['DELTATIME'][i_it] = deltatime

    # ------------------------------------------------------------------
    # Calculate drift properties
    # ------------------------------------------------------------------
    # get the maximum number of orders to use
    nomax = nbo    # p['IC_DRIFT_N_ORDER_MAX']
    # ------------------------------------------------------------------
    # if use mean
    if p['DRIFT_TYPE_E2DS'].upper() == 'WEIGHTED MEAN':
        # mean radial velocity
        sumwref = np.nansum(wref[:nomax])
        meanrv = np.nansum(loc['DRIFT'][:, :nomax] * wref[:nomax], 1)/sumwref
        # error in mean radial velocity
        errdrift2 = loc['ERRDRIFT'][:, :nomax]**2
        meanerr = 1.0/np.sqrt(np.nansum(1.0/errdrift2, 1))
        # add to loc
        loc['MDRIFT'] = meanrv
        loc['MERRDRIFT'] = meanerr
    # else use median
    else:
        # median drift
        loc['MDRIFT'] = np.nanmedian(loc['DRIFT'][:, :nomax], 1)
        # median err drift
        loc['MERRDRIFT'] = np.nanmedian(loc['ERRDRIFT'][:, :nomax], 1)
    # ------------------------------------------------------------------
    # set source
    loc.set_sources(['mdrift', 'merrdrift'], __NAME__ + '/main()()')
    # ------------------------------------------------------------------
    # peak to peak drift
    driftptp = np.max(loc['MDRIFT']) - np.min(loc['MDRIFT'])
    driftrms = np.std(loc['MDRIFT'])
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
        sPlt.drift_plot_dtime_against_mdrift(p, loc, kind='e2ds')

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
    driftfits, tag = spirouConfig.Constants.DRIFT_E2DS_FITS_FILE(p)
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
    drifttbl = spirouConfig.Constants.DRIFT_E2DS_TBL_FILE(p)
    drifttblname = os.path.split(drifttbl)[-1]
    # construct and write table
    columnnames = ['time', 'drift', 'drifterr']
    columnformats = ['7.4f', '6.2f', '6.3f']
    columnvalues = [loc['DELTATIME'], loc['MDRIFT'], loc['MERRDRIFT']]
    table = spirouImage.MakeTable(p, columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # write table
    wmsg = 'Average Drift saved in {0} Saved '
    WLOG(p, '', wmsg.format(drifttblname))
    spirouImage.WriteTable(p, table, drifttbl, fmt='ascii.rst')

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

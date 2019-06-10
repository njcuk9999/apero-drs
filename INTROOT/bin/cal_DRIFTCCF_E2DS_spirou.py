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
__NAME__ = 'cal_DRIFTCCF_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
__args__ = ['night_name', 'reffile']
__required__ = [True, True]
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
    speref, hdr, nbo, nx = spirouImage.ReadData(p, reffilename)
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
    # manually set OBJNAME to FP
    p['OBJNAME'] = 'FP'

    # ----------------------------------------------------------------------
    #  Earth Velocity calculation
    # ----------------------------------------------------------------------
    if p['IC_IMAGE_TYPE'] == 'H4RG':
        p, loc = spirouImage.GetEarthVelocityCorrection(p, loc, hdr)

    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # # get wave image
    # wout = spirouImage.GetWaveSolution(p, hdr=hdr, fiber=wave_fiber,
    #                                    return_wavemap=True)
    # _, loc['WAVE'] = wout
    # loc.set_source('WAVE', __NAME__+'/main() + /spirouImage.GetWaveSolution')

    # get wave image
    wout = spirouImage.GetWaveSolution(p, hdr=hdr, return_wavemap=True,
                                       return_filename=True, fiber=wave_fiber)
    param_ll, wave_ll, wavefile, wsource = wout
    # save to storage
    loc['PARAM_LL'], loc['WAVE_LL'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    source = __NAME__ + '/main() + spirouTHORCA.GetWaveSolution()'
    loc.set_sources(['WAVE_LL', 'PARAM_LL', 'WAVEFILE', 'WSOURCE'], source)

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

    # ----------------------------------------------------------------------
    # Preliminary set up = no flat, no blaze
    # ----------------------------------------------------------------------
    # reset flat to all ones
    # loc['FLAT'] = np.ones((nbo, nx))
    # set blaze to all ones (if not bug in correlbin !!!
    # TODO Check why Blaze makes bugs in correlbin
    loc['BLAZE'] = np.ones((nbo, nx))
    # set sources
    # loc.set_sources(['flat', 'blaze'], __NAME__ + '/main()')
    loc.set_sources(['blaze'], __NAME__ + '/main()')

    # ------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['SPEREF'], loc['WAVE_LL']]
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
        # sPlt.drift_plot_selected_wave_ref(p, loc)
        # plot photon noise uncertainty
        sPlt.drift_plot_photon_uncertainty(p, loc)

    # ----------------------------------------------------------------------
    # Get template RV (from ccf_mask)
    # ----------------------------------------------------------------------
    # Use CCF Mask function with drift constants
    p['CCF_MASK'] = p['DRIFT_CCF_MASK']
    p['TARGET_RV'] = p['DRIFT_TARGET_RV']
    p['CCF_WIDTH'] = p['DRIFT_CCF_WIDTH']
    p['CCF_STEP'] = p['DRIFT_CCF_STEP']

    # get the CCF mask from file (check location of mask)
    loc = spirouRV.GetCCFMask(p, loc)

    # check and deal with mask in microns (should be in nm)
    if np.mean(loc['LL_MASK_CTR']) < 2.0:
        loc['LL_MASK_CTR'] *= 1000.0
        loc['LL_MASK_D'] *= 1000.0

    # ----------------------------------------------------------------------
    # Do correlation
    # ----------------------------------------------------------------------
    # calculate and fit the CCF
    loc['E2DSFF'] = np.array(loc['SPEREF'])
    loc.set_source('E2DSFF', __NAME__ + '/main()')
    p['CCF_FIT_TYPE'] = 1
    # run the RV coravelation function with these parameters
    loc = spirouRV.Coravelation(p, loc)

    # ----------------------------------------------------------------------
    # Correlation stats
    # ----------------------------------------------------------------------
    # get the maximum number of orders to use
    nbmax = p['CCF_NUM_ORDERS_MAX']
    # get the average ccf
    loc['AVERAGE_CCF'] = np.nansum(loc['CCF'][: nbmax], axis=0)
    # normalize the average ccf
    normalized_ccf = loc['AVERAGE_CCF'] / np.nanmax(loc['AVERAGE_CCF'])
    # get the fit for the normalized average ccf
    ccf_res, ccf_fit = spirouRV.FitCCF(p, loc['RV_CCF'], normalized_ccf,
                                       fit_type=1)
    loc['CCF_RES'] = ccf_res
    loc['CCF_FIT'] = ccf_fit
    # get the max cpp
    loc['MAXCPP'] = np.nansum(loc['CCF_MAX']) / np.nansum(loc['PIX_PASSED_ALL'])
    # get the RV value from the normalised average ccf fit center location
    loc['RV'] = float(ccf_res[1])
    # get the contrast (ccf fit amplitude)
    loc['CONTRAST'] = np.abs(100 * ccf_res[0])
    # get the FWHM value
    loc['FWHM'] = ccf_res[2] * spirouCore.spirouMath.fwhm()

    # ----------------------------------------------------------------------
    # set the source
    keys = ['average_ccf', 'maxcpp', 'rv', 'contrast', 'fwhm',
            'ccf_res', 'ccf_fit']
    loc.set_sources(keys, __NAME__ + '/main()')
    # ----------------------------------------------------------------------
    # log the stats
    wmsg = ('Correlation: C={0:.1f}[%] RV={1:.5f}[km/s] '
            'FWHM={2:.4f}[km/s] maxcpp={3:.1f}')
    wargs = [loc['CONTRAST'], loc['RV'], loc['FWHM'], loc['MAXCPP']]
    WLOG(p, 'info', wmsg.format(*wargs))

    # get the reference RV in m/s
    rvref = loc['RV'] * 1000.

    # ----------------------------------------------------------------------
    # rv ccf plot
    # ----------------------------------------------------------------------

    if p['DRS_PLOT'] > 0:
        # Plot rv vs ccf (and rv vs ccf_fit)
        sPlt.ccf_rv_ccf_plot(p, loc['RV_CCF'], normalized_ccf, ccf_fit)

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
        nfiles = int(nfiles / skip)
    else:
        skip = 1
    # set up storage
    loc['MDRIFT'] = np.zeros(nfiles)
    loc['MERRDRIFT'] = np.zeros(nfiles)
    loc['DELTATIME'] = np.zeros(nfiles)
    loc['FLUXRATIO'] = np.zeros(nfiles)
    # set loc sources
    keys = ['mdrift', 'merrdrift', 'deltatime']
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
        loc['SPE'], hdri, nxi, nyi = rout
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
        # calculate flux ratio
        # ------------------------------------------------------------------
        sorder = p['IC_DRIFT_ORDER_PLOT']
        fratio = np.nansum(loc['SPE'][sorder]) / np.nansum(loc['SPEREF'][sorder])
        loc['FLUXRATIO'][i_it] = fratio

        # ------------------------------------------------------------------
        # Compute photon noise uncertainty for reference file
        # ------------------------------------------------------------------
        # set up the arguments for DeltaVrms2D
        dargs = [loc['SPE'], loc['WAVE_LL']]
        dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DRIFT_BOXSIZE'],
                       threshold=p['IC_DRIFT_MAXFLUX'])
        # run DeltaVrms2D
        dvrmsspe, wmeanspe = spirouRV.DeltaVrms2D(*dargs, **dkwargs)

        # ----------------------------------------------------------------------
        # Do correlation
        # ----------------------------------------------------------------------
        # calculate and fit the CCF
        loc['E2DSFF'] = loc['SPE'] * 1.
        loc.set_source('E2DSFF', __NAME__ + '/main()')

        loc = spirouRV.Coravelation(p, loc)

        # ----------------------------------------------------------------------
        # Correlation stats
        # ----------------------------------------------------------------------
        # get the maximum number of orders to use
        nbmax = p['CCF_NUM_ORDERS_MAX']
        # get the average ccf
        loc['AVERAGE_CCF'] = np.nansum(loc['CCF'][: nbmax], axis=0)
        # normalize the average ccf
        normalized_ccf = loc['AVERAGE_CCF'] / np.nanmax(loc['AVERAGE_CCF'])
        # get the fit for the normalized average ccf
        ccf_res, ccf_fit = spirouRV.FitCCF(p, loc['RV_CCF'], normalized_ccf,
                                           fit_type=1)
        # calculate the mean RV
        meanrv = ccf_res[1] * 1000. - rvref
        # ------------------------------------------------------------------
        # Calculate delta time
        # ------------------------------------------------------------------
        # calculate the time from reference (in hours)
        deltatime = (bjdspe - bjdref) * 24

        err_meanrv = np.sqrt(dvrmsref + dvrmsspe)
        merr = 1. / np.sqrt(np.nansum((1. / err_meanrv) ** 2))
        # Log the RV properties
        wmsg = ('Time from ref= {0:.2f} h '
                '- Flux Ratio= {1:.2f} '
                '- Drift mean= {2:.2f} +- '
                '{3:.2f} m/s')
        wargs = [deltatime, loc['FLUXRATIO'][i_it], meanrv, merr]
        WLOG(p, '', wmsg.format(*wargs))
        # add this iteration to storage
        loc['MDRIFT'][i_it] = meanrv
        loc['MERRDRIFT'][i_it] = merr
        loc['DELTATIME'][i_it] = deltatime

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

    # ------------------------------------------------------------------
    # Save drift values to file
    # ------------------------------------------------------------------
    # # get raw input file name
    # raw_infile = os.path.basename(p['REFFILE'])
    # # construct filename
    # driftfits, tag = spirouConfig.Constants.DRIFTCCF_E2DS_FITS_FILE(p)
    # driftfitsname = os.path.split(driftfits)[-1]
    # # log that we are saving drift values
    # wmsg = 'Saving drift values of Fiber {0} in {1}'
    # WLOG(p, '', wmsg.format(p['FIBER'], driftfitsname))
    # # add keys from original header file
    # hdict = spirouImage.CopyOriginalKeys(hdr)
    # # add the reference RV
    # hdict = spirouImage.AddKey(p, hdict, p['KW_REF_RV'], value=rvref)
    #
    # # set the version
    # hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    # hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    # # set the input files
    # hdict = spirouImage.AddKey(p, hdict, p['KW_CDBFLAT'], value=p['FLATFILE'])
    # hdict = spirouImage.AddKey(p, hdict, p['KW_REFFILE'], value=raw_infile)
    # # save drift values
    # p = spirouImage.WriteImage(p, driftfits, loc['DRIFT'], hdict)

    # ------------------------------------------------------------------
    # print .tbl result
    # ------------------------------------------------------------------
    # construct filename
    drifttbl = spirouConfig.Constants.DRIFTCCF_E2DS_TBL_FILE(p)
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

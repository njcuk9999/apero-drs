#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DRIFT_RAW_spirou.py

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""
from __future__ import division
import numpy as np
import os

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
    night_name, reffile = None, None
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
    # Read Flat file
    # ----------------------------------------------------------------------
    # get flat
    loc['flat'] = spirouImage.ReadFlatFile(p, hdr)
    loc.set_source('flat', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    loc['flat'] = np.where(loc['flat'] == 0, 1.0, loc['flat'])

    # ------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['speref'], loc['wave']]
    dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DRIFT_BOXSIZE'],
                   threshold=p['IC_DRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)
    # save to loc
    loc['dvrmsref'], loc['wmeanref'] = dvrmsref, wmeanref
    loc.set_sources(['dvrmsref', 'wmeanref'], __NAME__ + '/main()()')
    # log the estimated RV uncertainty
    wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f} m/s'
    WLOG('info', p['log_opt'], wmsg.format(p['fiber'], wmeanref))

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
        Nfiles = int(Nfiles/p['DRIFT_FILE_SKIP'])
        skip = p['DRIFT_FILE_SKIP']
    else:
        skip = 1
    # set up storage
    loc['drift'] = np.zeros((Nfiles, loc['number_orders']))
    loc['errdrift'] = np.zeros((Nfiles, loc['number_orders']))
    loc['deltatime'] = np.zeros(Nfiles)
    # set loc sources
    keys = ['drift', 'errdrift', 'deltatime']
    loc.set_sources(keys, __NAME__ + '/main()()')

    # ------------------------------------------------------------------
    # Loop around all files: correct for dark, reshape, extract and
    #     calculate dvrms and meanpond
    # ------------------------------------------------------------------
    wref = 1
    for i_it in range(Nfiles):
        # get file for this iteration
        fpfile = listfiles[::skip][i_it]
        # Log the file we are reading
        wmsg = 'Reading file {0}'
        WLOG('', p['log_opt'], wmsg.format(os.path.split(fpfile)[-1]))
        # ------------------------------------------------------------------
        # read, correct for dark and reshape iteration file
        # ------------------------------------------------------------------
        # read data
        rout = spirouImage.ReadData(p, filename=fpfile, log=False)
        loc['spe'], hdri, cdri, nxi, nyi = rout
        # get acqtime
        bjdspe = spirouImage.GetAcqTime(p, hdri, name='acqtime', kind='unix',
                                        return_value=1)
        # ------------------------------------------------------------------
        # Compute photon noise uncertainty for iteration file
        # ------------------------------------------------------------------
        # set up the arguments for DeltaVrms2D
        dargs = [loc['spe'], loc['wave']]
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
        dargs = [loc['speref'], loc['spe']]
        dkwargs = dict(threshold=p['IC_DRIFT_MAXFLUX'],
                       size=p['IC_DRIFT_BOXSIZE'],
                       cut=p['IC_DRIFT_CUT_E2DS'])
        spen, cfluxr, cpt = spirouRV.ReNormCosmic2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Calculate the RV drift
        # ------------------------------------------------------------------
        dargs = [loc['speref'], spen, loc['wave']]
        dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'],
                       threshold=p['IC_DRIFT_MAXFLUX'],
                       size=p['IC_DRIFT_BOXSIZE'])
        rv = spirouRV.CalcRVdrift2D(*dargs, **dkwargs)

        # ------------------------------------------------------------------
        # Calculate RV properties
        # ------------------------------------------------------------------
        # calculate the mean flux ratio
        meanfratio = np.mean(cfluxr)
        # calculate the weighted mean radial velocity
        wref = 1.0/dvrmsref
        meanrv = -1.0 * np.sum(rv * wref)/np.sum(wref)
        err_meanrv = np.sqrt(dvrmsref + dvrmsspe)
        merr = 1./np.sqrt(np.sum((1./err_meanrv)**2))
        # calculate the time from reference (in hours)
        deltatime = (bjdspe - bjdref) * 24
        # Log the RV properties
        wmsg = ('Time from ref={0:.2f} h  - Drift mean= {1:.2f} +- {2:.3f} m/s '
                '- Flux ratio= {3:.2f} - Nb Comsic= {4}')
        WLOG('', p['log_opt'], wmsg.format(deltatime, meanrv, merr,
                                           meanfratio, cpt))
        # add this iteration to storage
        loc['drift'][i_it] = -1.0 * rv
        loc['errdrift'][i_it] = err_meanrv
        loc['deltatime'][i_it] = deltatime

    # ------------------------------------------------------------------
    # Calculate drift properties
    # ------------------------------------------------------------------
    # get the maximum number of orders to use
    nomax = nbo    # p['IC_DRIFT_N_ORDER_MAX']
    # ------------------------------------------------------------------
    # if use mean
    if p['drift_type_e2ds'].upper() == 'WEIGHTED MEAN':
        # mean radial velocity
        sumwref = np.sum(wref[:nomax])
        meanrv = np.sum(loc['drift'][:, :nomax] * wref[:nomax], 1)/sumwref
        # error in mean radial velocity
        errdrift2 = loc['errdrift'][:, :nomax]**2
        meanerr = 1.0/np.sqrt(np.sum(1.0/errdrift2, 1))
        # add to loc
        loc['mdrift'] = meanrv
        loc['merrdrift'] = meanerr
    # else use median
    else:
        # median drift
        loc['mdrift'] = np.median(loc['drift'][:, :nomax], 1)
        # median err drift
        loc['merrdrift'] = np.median(loc['errdrift'][:, :nomax], 1)
    # ------------------------------------------------------------------
    # set source
    loc.set_sources(['mdrift', 'merrdrift'], __NAME__ + '/main()()')
    # ------------------------------------------------------------------
    # peak to peak drift
    driftptp = np.max(loc['mdrift']) - np.min(loc['mdrift'])
    driftrms = np.std(loc['mdrift'])
    # log th etotal drift peak-to-peak and rms
    wmsg = ('Total drift Peak-to_peak={0:.3f} m/s RMS={1:.3f} m/s in '
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
        sPlt.drift_plot_dtime_against_mdrift(p, loc, kind='e2ds')

    # ------------------------------------------------------------------
    # Save drift values to file
    # ------------------------------------------------------------------
    # construct filename
    reducedfolder = p['reduced_dir']
    drift_ext = '_drift_{0}.fits'.format(p['fiber'])
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
    drift_ext = '_drift_{0}.tbl'.format(p['fiber'])
    drifttbl = reffilename.replace('.fits', drift_ext)
    drifttblfilename = os.path.join(reducedfolder, drifttbl)
    # construct and write table
    columnnames = ['time', 'drift', 'drifterr']
    columnformats = ['7.4f', '6.2f', '6.3f']
    columnvalues = [loc['deltatime'], loc['mdrift'], loc['merrdrift']]
    table = spirouImage.MakeTable(columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # write table
    wmsg = 'Average Drift saved in {0} Saved '
    WLOG('', p['log_opt'] + p['fiber'], wmsg.format(drifttblfilename))
    spirouImage.WriteTable(table, drifttblfilename, fmt='ascii.rst')

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been succesfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))

    return locals()

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    locals = main()


# =============================================================================
# End of code
# =============================================================================

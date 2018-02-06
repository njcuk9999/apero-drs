#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_CCF_E2DS_spirou.py [night_directory] [E2DSfilename] [mask] [RV] [width] [step]

# CODE DESCRIPTION HERE

Created on 2017-12-18 at 15:43

@author: cook

Last modified: 2017-12-18 at 15:48

Up-to-date with cal_CCF_E2DS_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouRV
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_CCF_E2DS_spirou.py'
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
def main(night_name=None, reffile=None, mask=None, rv=None, width=None,
         step=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()

    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1, 2, 3, 4]
    fmt = [str, str, float, float, float]
    name = ['reffile', 'ccf_mask', 'target_rv', 'ccf_width', 'ccf_step']
    lname = ['input_file', 'CCF_mask', 'RV', 'CCF_width', 'CCF_step']
    req = [True, True, True, False, False]
    call = [reffile, mask, rv, width, step]
    call_priority = [True, True, True, True, True]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(pos, fmt, name, req, call,
                                                    call_priority, lname)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs)
    # define default arguments (if ccf_width and ccf_step are not defined
    # in function call or run time arguments
    if 'ccf_width' not in p:
        p['ccf_width'] = p['ic_ccf_width']
    if 'ccf_step' not in p:
        p['ccf_step'] = p['ic_ccf_step']
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
    e2ds, hdr, cdr, nbo, nx = spirouImage.ReadData(p, reffilename)
    # add to loc
    loc = ParamDict()
    loc['e2ds'] = e2ds
    loc['number_orders'] = nbo
    loc.set_sources(['e2ds', 'number_orders'], __NAME__ + '/main()')

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
    # log
    WLOG('', p['log_opt'], 'Reading wavelength solution ')

    # get wave image
    wave_ll, param_ll = spirouTHORCA.GetE2DSll(p, hdr=hdr)

    # save to storage
    loc['wave_ll'], loc['param_ll'] = wave_ll, param_ll
    source = __NAME__ + '/main() + spirouTHORCA.GetE2DSll()'
    loc.set_sources(['wave_ll', 'param_ll'], source)

    # ----------------------------------------------------------------------
    # Read Flat file
    # ----------------------------------------------------------------------
    # log
    WLOG('', p['log_opt'], 'Reading Flat-Field ')

    # get flat
    loc['flat'] = spirouImage.ReadFlatFile(p, hdr)
    loc.set_source('flat', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    loc['flat'] = np.where(loc['flat'] == 0, 1.0, loc['flat'])

    # ----------------------------------------------------------------------
    # Preliminary set up = no flat, no blaze
    # ----------------------------------------------------------------------
    # reset flat to all ones
    loc['flat'] = np.ones((nbo, nx))
    # set blaze to all ones
    loc['blaze'] = np.ones((nbo, nx))
    # set sources
    loc.set_sources(['flat', 'blaze'], __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # correct extracted image for flat
    # ----------------------------------------------------------------------
    loc['e2dsff'] = e2ds/loc['flat']
    loc.set_source('e2dsff', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ----------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['e2ds'], loc['wave_ll']]
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

    # ----------------------------------------------------------------------
    # Reference plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive session if needed
        sPlt.start_interactive_session()
        # plot FP spectral order
        sPlt.drift_plot_selected_wave_ref(p, loc, y=loc['e2ds'])
        # plot photon noise uncertainty
        sPlt.drift_plot_photon_uncertainty(p, loc)

    # ----------------------------------------------------------------------
    # Get template RV (from ccf_mask)
    # ----------------------------------------------------------------------
    # get the CCF mask from file (check location of mask)
    loc = spirouRV.GetCCFMask(p, loc)

    # check and deal with mask in microns (should be in nm)
    if np.mean(loc['ll_mask_ctr']) < 2.0:
        loc['ll_mask_ctr'] *= 1000.0
        loc['ll_mask_d'] *= 1000.0

    # ----------------------------------------------------------------------
    # Do correlation
    # ----------------------------------------------------------------------
    # calculate and fit the CCF
    loc = spirouRV.Coravelation(p, loc)

    # ----------------------------------------------------------------------
    # Correlation stats
    # ----------------------------------------------------------------------
    # get the maximum number of orders to use
    nbmax = p['ccf_num_orders_max']
    # get the average ccf
    loc['average_ccf'] = np.sum(loc['ccf'][: nbmax], axis=0)
    # normalize the average ccf
    normalized_ccf = loc['average_ccf']/np.max(loc['average_ccf'])
    # get the fit for the normalized average ccf
    ccf_res, ccf_fit = spirouRV.FitCCF(loc['rv_ccf'], normalized_ccf,
                                       fit_type=0)
    loc['ccf_res'] = ccf_res
    loc['ccf_fit'] = ccf_fit
    # get the max cpp
    loc['maxcpp'] = np.sum(loc['ccf_max'])/np.sum(loc['pix_passed_all'])
    # get the RV value from the normalised average ccf fit center location
    loc['rv'] = float(ccf_res[1])
    # get the contrast (ccf fit amplitude)
    loc['contrast'] = np.abs(100*ccf_res[0])
    # get the FWHM value
    loc['fwhm'] = ccf_res[2] * 2.3548
    # ----------------------------------------------------------------------
    # set the source
    keys = ['average_ccf', 'maxcpp', 'rv', 'contrast', 'fwhm',
            'ccf_res', 'ccf_fit']
    loc.set_sources(keys, __NAME__ + '/main()')
    # ----------------------------------------------------------------------
    # log the stats
    wmsg = ('Correlation: C={0:.1f}[%] RV={1:.5f}[km/s] '
            'FWHM={2:.4f}[km/s] maxcpp={3:.1f}')
    wargs = [loc['contrast'], loc['rv'], loc['fwhm'], loc['maxcpp']]
    WLOG('info', p['log_opt'], wmsg.format(*wargs))

    # ----------------------------------------------------------------------
    # rv ccf plot
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # Plot rv vs ccf (and rv vs ccf_fit)
        sPlt.ccf_rv_ccf_plot(loc['rv_ccf'], normalized_ccf, ccf_fit)

    # ----------------------------------------------------------------------
    # archive ccf
    # ----------------------------------------------------------------------
    # construct folder and filename
    corfile = spirouConfig.Constants.CCF_FITS_FILE(p)
    corfilename = os.path.split(corfile)[-1]
    # log that we are archiving the CCF on file
    WLOG('', p['log_opt'], 'Archiving CCF on file {0}'.format(corfilename))
    # get constants from p
    mask = p['ccf_mask']
    # if file exists remove it
    if os.path.exists(corfile):
        os.remove(corfile)
    # add the average ccf to the end of ccf
    data = np.vstack([loc['ccf'], loc['average_ccf']])
    # add keys
    hdict = dict()
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_CTYPE'], value='km/s')
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_CRVAL'], value=loc['rv_ccf'][0])
    # the rv step
    rvstep = np.abs(loc['rv_ccf'][0] - loc['rv_ccf'][1])
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_CDELT'], value=rvstep)
    # add stats
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_RV'], value=loc['ccf_res'][1])
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_RVC'], value=loc['rv'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_FWHM'], value=loc['fwhm'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_CONTRAST'],
                               value=loc['contrast'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_MAXCPP'], value=loc['maxcpp'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_MASK'], value=p['ccf_mask'])
    hdict = spirouImage.AddKey(hdict, p['kw_CCF_LINES'],
                               value=np.sum(loc['tot_line']))
    # write image and add header keys (via hdict)
    spirouImage.WriteImage(corfile, data, hdict)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
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

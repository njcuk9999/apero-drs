#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_CCF_E2DS_spirou.py
       [night_directory] [E2DSfilename] [mask] [RV] [width] [step]

Computes the CCF for a specific file using a CCF mask, target RV, CCF width
and CCF step.

Created on 2017-12-18 at 15:43

@author: cook

Last modified: 2017-12-18 at 15:48

Up-to-date with cal_CCF_E2DS_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os
import warnings

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouRV
from SpirouDRS import spirouStartup

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
def main(night_name=None, e2dsfile=None, mask=None, rv=None, width=None,
         step=None):
    """
    cal_CCF_E2DS_spirou.py main function, if arguments are None uses
    arguments from run time i.e.:
        cal_CCF_E2DS_spirou.py [night_directory] [E2DSfilename] [mask] [RV]
                               [width] [step]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param e2dsfile: string, the E2DS file to use
    :param mask: string, the mask file to use (i.e. "UrNe.mas")
    :param rv: float, the target RV to use
    :param width: float, the CCF width to use
    :param step: float, the CCF step to use

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1, 2, 3, 4]
    fmt = [str, str, float, float, float]
    name = ['e2dsfile', 'ccf_mask', 'target_rv', 'ccf_width', 'ccf_step']
    lname = ['input_file', 'CCF_mask', 'RV', 'CCF_width', 'CCF_step']
    req = [True, True, True, False, False]
    call = [e2dsfile, mask, rv, width, step]
    call_priority = [True, True, True, True, True]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(p, pos, fmt, name, req,
                                                    call, call_priority, lname)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='e2dsfile',
                                    mainfitsdir='reduced')

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, e2dsfilename = spirouStartup.SingleFileSetup(p, filename=p['E2DSFILE'])

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Deal with optional run time arguments
    # ----------------------------------------------------------------------
    # define default arguments (if ccf_width and ccf_step are not defined
    # in function call or run time arguments
    if 'ccf_width' not in p:
        p['CCF_WIDTH'] = p['IC_CCF_WIDTH']
    if 'ccf_step' not in p:
        p['CCF_STEP'] = p['IC_CCF_STEP']

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    e2ds, hdr, cdr, nbo, nx = spirouImage.ReadData(p, e2dsfilename)
    # add to loc
    loc = ParamDict()
    loc['E2DS'] = e2ds
    loc['NUMBER_ORDERS'] = nbo
    loc.set_sources(['E2DS', 'number_orders'], __NAME__ + '/main()')

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
    # get obj name
    p = spirouImage.ReadParam(p, hdr, 'KW_OBJNAME', name='OBJNAME', dtype=str)

    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']

    # ----------------------------------------------------------------------
    #  Earth Velocity calculation
    # ----------------------------------------------------------------------
    if p['IC_IMAGE_TYPE'] == 'H4RG':
        p, loc = spirouImage.GetEarthVelocityCorrection(p, loc, hdr)

    # ----------------------------------------------------------------------
    # Read wavelength solution
    # ----------------------------------------------------------------------
    # log
    WLOG(p, '', 'Reading wavelength solution ')
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
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
    # TODO We do not need to correct FLAT
    # log
    # WLOG(p, '', 'Reading Flat-Field ')

    # get flat
    # loc['FLAT'] = spirouImage.ReadFlatFile(p, hdr)
    # loc.set_source('FLAT', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    # loc['FLAT'] = np.where(loc['FLAT'] == 0, 1.0, loc['FLAT'])

    # get blaze
    # p, loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hdr)
    p, blaze0 = spirouImage.ReadBlazeFile(p, hdr)

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

    # Modification of E2DS array  with N.A.N
    if np.isnan(np.sum(e2ds)):
        WLOG(p, 'warning', 'NaN values found in e2ds, converting process')
        #  First basic approach Replacing N.A.N by zeros
        #    e2ds[np.isnan(e2ds)] = 0

        # Second approach replacing N.A.N by the Adjusted Blaze
        e2dsb = e2ds / blaze0
        for i in np.arange(len(e2ds)):
            with warnings.catch_warnings(record=True) as _:
                rap = np.mean(e2dsb[i][np.isfinite(e2dsb[i])])
            if np.isnan(rap):
                rap = 0.0
            e2ds[i] = np.where(np.isfinite(e2dsb[i]), e2ds[i], blaze0[i] * rap)

    # ----------------------------------------------------------------------
    # correct extracted image for flat
    # ----------------------------------------------------------------------
    # loc['E2DSFF'] = e2ds/loc['FLAT']
    # loc['E2DSFF'] = e2ds*1.
    loc['E2DSFF'] = e2ds
    loc.set_source('E2DSFF', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ----------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['E2DS'], loc['WAVE_LL']]
    dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DRIFT_BOXSIZE'],
                   threshold=p['IC_DRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)
    # save to loc
    loc['DVRMSREF'], loc['WMEANREF'] = dvrmsref, wmeanref
    loc.set_sources(['dvrmsref', 'wmeanref'], __NAME__ + '/main()()')
    # log the estimated RV uncertainty
    # wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f} m/s'
    # WLOG(p, 'info', wmsg.format(p['FIBER'], wmeanref))
    wmsg = 'On fiber estimated RV uncertainty on spectrum is {0:.3f} m/s'
    WLOG(p, 'info', wmsg.format(wmeanref))
    # TEST N.A.N
    # loc['E2DSFF'][20:22,2000:3000]=np.nan
    # e2ds[20:30,1000:3000]=np.nan

    # ----------------------------------------------------------------------
    # Reference plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive session if needed
        sPlt.start_interactive_session(p)
        # plot FP spectral order
        sPlt.drift_plot_selected_wave_ref(p, loc, x=loc['WAVE_LL'],
                                          y=loc['E2DS'])
        # plot photon noise uncertainty
        sPlt.drift_plot_photon_uncertainty(p, loc)

    # ----------------------------------------------------------------------
    # Get template RV (from ccf_mask)
    # ----------------------------------------------------------------------
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
    loc = spirouRV.Coravelation(p, loc)

    # ----------------------------------------------------------------------
    # Correlation stats
    # ----------------------------------------------------------------------
    # get the maximum number of orders to use
    nbmax = p['CCF_NUM_ORDERS_MAX']
    # get the average ccf
    loc['AVERAGE_CCF'] = np.nansum(loc['CCF'][: nbmax], axis=0)
    # normalize the average ccf
    normalized_ccf = loc['AVERAGE_CCF'] / np.max(loc['AVERAGE_CCF'])
    # get the fit for the normalized average ccf
    ccf_res, ccf_fit = spirouRV.FitCCF(p, loc['RV_CCF'], normalized_ccf,
                                       fit_type=0)
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

    # ----------------------------------------------------------------------
    # rv ccf plot
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # Plot rv vs ccf (and rv vs ccf_fit)
        sPlt.ccf_rv_ccf_plot(p, loc['RV_CCF'], normalized_ccf, ccf_fit)

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

    # ----------------------------------------------------------------------
    # archive ccf to table
    # ----------------------------------------------------------------------
    # construct filename
    res_table_file = spirouConfig.Constants.CCF_TABLE_FILE(p)
    # log progress
    WLOG(p, '', 'Archiving CCF on file {0}'.format(res_table_file))
    # define column names
    columns = ['order', 'maxcpp', 'nlines', 'contrast', 'RV', 'sig']
    # define values for each column
    values = [loc['ORDERS'],
              loc['CCF_MAX'] / loc['PIX_PASSED_ALL'],
              loc['TOT_LINE'],
              np.abs(100 * loc['CCF_ALL_RESULTS'][:, 0]),
              loc['CCF_ALL_RESULTS'][:, 1],
              loc['CCF_ALL_RESULTS'][:, 2]]
    # define the format for each column
    formats = ['2.0f', '5.0f', '4.0f', '4.1f', '9.4f', '7.4f']
    # construct astropy table from column names, values and formats
    table = spirouImage.MakeTable(p, columns, values, formats)
    # save table to file
    spirouImage.WriteTable(p, table, res_table_file, fmt='ascii')

    # ----------------------------------------------------------------------
    # archive ccf to fits file
    # ----------------------------------------------------------------------
    raw_infile = os.path.basename(p['E2DSFILE'])
    # construct folder and filename
    corfile, tag = spirouConfig.Constants.CCF_FITS_FILE(p)
    corfilename = os.path.split(corfile)[-1]
    # log that we are archiving the CCF on file
    WLOG(p, '', 'Archiving CCF on file {0}'.format(corfilename))
    # get constants from p
    mask = p['CCF_MASK']
    # if file exists remove it
    if os.path.exists(corfile):
        os.remove(corfile)
    # add the average ccf to the end of ccf
    data = np.vstack([loc['CCF'], loc['AVERAGE_CCF']])
    # add drs keys
    hdict = spirouImage.CopyOriginalKeys(hdr, cdr)
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    # set the input files
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'], value=loc['WAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['E2DSFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_INCCFMASK'], value=p['CCF_MASK'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_INRV'], value=p['TARGET_RV'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_INWIDTH'], value=p['CCF_WIDTH'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_INSTEP'], value=p['CCF_STEP'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # add CCF keys
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_CTYPE'], value='km/s')
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_CRVAL'],
                               value=loc['RV_CCF'][0])
    # the rv step
    rvstep = np.abs(loc['RV_CCF'][0] - loc['RV_CCF'][1])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_CDELT'], value=rvstep)
    # add ccf stats
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_RV'],
                               value=loc['CCF_RES'][1])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_RVC'], value=loc['RV'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_FWHM'], value=loc['FWHM'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_WMREF'],
                               value=loc['WMEANREF'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_CONTRAST'],
                               value=loc['CONTRAST'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_MAXCPP'], value=loc['MAXCPP'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_MASK'], value=p['CCF_MASK'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CCF_LINES'],
                               value=np.nansum(loc['TOT_LINE']))
    # add berv values
    hdict = spirouImage.AddKey(p, hdict, p['KW_BERV'], value=loc['BERV'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_BJD'], value=loc['BJD'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_BERV_MAX'],
                               value=loc['BERV_MAX'])
    # write image and add header keys (via hdict)
    p = spirouImage.WriteImage(p, corfile, data, hdict)

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

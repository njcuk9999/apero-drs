#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_HC_E2DS_spirou.py [night_directory] [fitsfilename]

Wavelength calibration

Created on 2018-08-28

@author: artigau, hobson, cook
"""
from __future__ import division
import os
import numpy as np

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS.spirouTHORCA import spirouWAVE

from astropy import constants as cc
from astropy import units as uu
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_HC_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, files=None):
    """
    cal_HC_E2DS.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_DARK_spirou.py [night_directory] [fitsfilename]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param files: string, list or None, the list of files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, files, mainfitsdir='reduced')
    # setup files and get fiber
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read and combine all files
    p, hcdata, hchdr = spirouImage.ReadImageAndCombine(p, 'add')
    # add data and hdr to loc
    loc = ParamDict()
    loc['HCDATA'], loc['HCHDR'] = hcdata, hchdr
    # set the source
    sources = ['HCDATA', 'HCHDR']
    loc.set_sources(sources, 'spirouImage.ReadImageAndCombine()')

    # ----------------------------------------------------------------------
    # Get basic parameters
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, loc['HCHDR'], name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, loc['HCHDR'], name='exptime')
    # get gain
    p = spirouImage.GetGain(p, loc['HCHDR'], name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, loc['HCHDR'], name='ACQTIME', kind='julian')
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p, loc['HCHDR'])

    # get number of orders
    # we always get fibre A number because AB is doubled in constants file
    loc['NBO'] = p['QC_LOC_NBO_FPALL']['A']
    loc.set_source('NBO', __NAME__ + '.main()')
    # get number of pixels in x from hcdata size
    loc['NBPIX'] = loc['HCDATA'].shape[1]
    loc.set_source('NBPIX', __NAME__ + '.main()')

    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hchdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')

    # ----------------------------------------------------------------------
    # Read wave solution
    # ----------------------------------------------------------------------
    # wavelength file; we will use the polynomial terms in its header,
    # NOT the pixel values that would need to be interpolated
    # getting header info with wavelength polynomials

    # set source of wave file
    wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # get wave image
    wout = spirouImage.GetWaveSolution(p, hdr=hchdr, return_wavemap=True,
                                       return_filename=True, fiber=wave_fiber)
    loc['WAVEPARAMS'], loc['WAVE_INIT'], loc['WAVEFILE'], loc['WSOURCE'] = wout
    loc.set_sources(['WAVE_INIT', 'WAVEFILE', 'WAVEPARAMS', 'WSOURCE'], wsource)

    # ----------------------------------------------------------------------
    # Check that wave parameters are consistent with "ic_ll_degr_fit"
    # ----------------------------------------------------------------------
    loc = spirouImage.CheckWaveSolConsistency(p, loc)

    # ----------------------------------------------------------------------
    # Read UNe solution
    # ----------------------------------------------------------------------
    wave_u_ne, amp_u_ne = spirouImage.ReadLineList(p)
    loc['LL_LINE'], loc['AMPL_LINE'] = wave_u_ne, amp_u_ne
    source = __NAME__ + '.main() + spirouImage.ReadLineList()'
    loc.set_sources(['ll_line', 'ampl_line'], source)

    # ----------------------------------------------------------------------
    # Generate wave map from wave solution
    # ----------------------------------------------------------------------
    loc = spirouWAVE.generate_wave_map(p, loc)

    # ----------------------------------------------------------------------
    # Find Gaussian Peaks in HC spectrum
    # ----------------------------------------------------------------------
    loc = spirouWAVE.find_hc_gauss_peaks(p, loc)

    # ----------------------------------------------------------------------
    # Start plotting session
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive plot
        sPlt.start_interactive_session(p)

    # ----------------------------------------------------------------------
    # Fit Gaussian peaks (in triplets) to
    # ----------------------------------------------------------------------
    loc = spirouWAVE.fit_gaussian_triplets(p, loc)

    # ----------------------------------------------------------------------
    # Generate Resolution map and line profiles
    # ----------------------------------------------------------------------
    # log progress
    wmsg = 'Generating resolution map and '
    # generate resolution map
    loc = spirouWAVE.generate_resolution_map(p, loc)
    # map line profile map
    if p['DRS_PLOT'] > 0:
        sPlt.wave_ea_plot_line_profiles(p, loc)

    # ----------------------------------------------------------------------
    # End plotting session
    # ----------------------------------------------------------------------
    # end interactive session
    if p['DRS_PLOT'] > 0:
        sPlt.end_interactive_session(p)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []

    # quality control on sigma clip (sig1 > qc_hc_wave_sigma_max
    if loc['SIG1'] > p['QC_HC_WAVE_SIGMA_MAX']:
        fmsg = 'Sigma too high ({0:.5f} > {1:.5f})'
        fail_msg.append(fmsg.format(loc['SIG1'], p['QC_HC_WAVE_SIGMA_MAX']))
        passed = False
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(loc['SIG1'])
    qc_names.append('SIG1')
    qc_logic.append('SIG1 > {0:.2f}'.format(p['QC_HC_WAVE_SIGMA_MAX']))
    # ----------------------------------------------------------------------
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
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # ----------------------------------------------------------------------
    # log the global stats
    # ----------------------------------------------------------------------

    # calculate catalog-fit residuals in km/s

    res_hc =[]
    sumres_hc = 0.0
    sumres2_hc = 0.0

    for order in range(loc['NBO']):
        # get HC line wavelengths for the order
        order_mask = loc['ORD_T'] == order
        hc_x_ord = loc['XGAU_T'][order_mask]
        hc_ll_ord = np.polyval(loc['POLY_WAVE_SOL'][order][::-1],hc_x_ord)
        hc_ll_cat = loc['WAVE_CATALOG'][order_mask]
        hc_ll_diff = hc_ll_ord - hc_ll_cat
        res_hc.append(hc_ll_diff*speed_of_light/hc_ll_cat)
        sumres_hc += np.nansum(res_hc[order])
        sumres2_hc += np.nansum(res_hc[order] ** 2)

    total_lines_hc = len(np.concatenate(res_hc))
    final_mean_hc = sumres_hc/total_lines_hc
    final_var_hc = (sumres2_hc/total_lines_hc) - (final_mean_hc ** 2)
    wmsg1 = 'On fiber {0} HC fit line statistic:'.format(p['FIBER'])
    wargs2 = [final_mean_hc * 1000.0, np.sqrt(final_var_hc) * 1000.0,
              total_lines_hc, 1000.0 * np.sqrt(final_var_hc / total_lines_hc)]
    wmsg2 = ('\tmean={0:.3f}[m/s] rms={1:.1f} {2} HC lines (error on mean '
             'value:{3:.4f}[m/s])'.format(*wargs2))
    WLOG(p, 'info', [wmsg1, wmsg2])

    # ----------------------------------------------------------------------
    # Save wave map to file
    # ----------------------------------------------------------------------
    # get base input filenames
    bfilenames = []
    for raw_file in p['ARG_FILE_NAMES']:
        bfilenames.append(os.path.basename(raw_file))
    # get wave filename
    wavefits, tag1 = spirouConfig.Constants.WAVE_FILE_EA(p)
    wavefitsname = os.path.basename(wavefits)
    # log progress
    WLOG(p, '', 'Saving wave map to {0}'.format(wavefitsname))
    # log progress
    wargs = [p['FIBER'], wavefitsname]
    wmsg = 'Write wavelength solution for Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(*wargs))
    # write solution to fitsfilename header
    # copy original keys
    hdict = spirouImage.CopyOriginalKeys(loc['HCHDR'])
    # set the version
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
    # set the input files
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'], value=p['BLAZFILE'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # add wave solution date
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME1'],
                               value=p['MAX_TIME_HUMAN'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_TIME2'],
                               value=p['MAX_TIME_UNIX'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_CODE'], value=__NAME__)
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'], value=loc['WAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['ARG_FILE_NAMES'])
    # add number of orders
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_ORD_N'],
                               value=loc['POLY_WAVE_SOL'].shape[0])
    # add degree of fit
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_LL_DEG'],
                               value=loc['POLY_WAVE_SOL'].shape[1]-1)
    # add wave solution
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                     values=loc['POLY_WAVE_SOL'])
    # write the wave "spectrum"
    p = spirouImage.WriteImage(p, wavefits, loc['WAVE_MAP2'], hdict)

    # get filename for E2DS calibDB copy of FITSFILENAME
    e2dscopy_filename, tag2 = spirouConfig.Constants.WAVE_E2DS_COPY(p)

    wargs = [p['FIBER'], os.path.split(e2dscopy_filename)[-1]]
    wmsg = 'Write reference E2DS spectra for Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(*wargs))

    # make a copy of the E2DS file for the calibBD
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
    p = spirouImage.WriteImage(p, e2dscopy_filename, loc['HCDATA'], hdict)

    # ----------------------------------------------------------------------
    # Save resolution and line profiles to file
    # ----------------------------------------------------------------------
    raw_infile = os.path.basename(p['FITSFILENAME'])
    # get wave filename
    resfits, tag3 = spirouConfig.Constants.WAVE_RES_FILE_EA(p)
    resfitsname = os.path.basename(resfits)
    WLOG(p, '', 'Saving wave resmap to {0}'.format(resfitsname))

    # make a copy of the E2DS file for the calibBD
    # set the version
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag3)

    # get res data in correct format
    resdata, hdicts = spirouTHORCA.GenerateResFiles(p, loc, hdict)
    # save to file
    p = spirouImage.WriteImageMulti(p, resfits, resdata, hdicts=hdicts)

    # ----------------------------------------------------------------------
    # Update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        # set the wave key
        keydb = 'WAVE_{0}'.format(p['FIBER'])
        # copy wave file to calibDB folder
        spirouDB.PutCalibFile(p, wavefits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, wavefitsname, loc['HCHDR'])

        # set the hcref key
        keydb = 'HCREF_{0}'.format(p['FIBER'])
        # copy wave file to calibDB folder
        spirouDB.PutCalibFile(p, e2dscopy_filename)
        # update the master calib DB file with new key
        e2dscopyfits = os.path.split(e2dscopy_filename)[-1]
        spirouDB.UpdateCalibMaster(p, keydb, e2dscopyfits, loc['HCHDR'])

    # ----------------------------------------------------------------------
    # Update header of current files
    # ----------------------------------------------------------------------
    # only copy over if QC passed
    if p['QC']:
        rdir = os.path.dirname(wavefits)
        # loop around hc files and update header with
        for rawhcfile in p['ARG_FILE_NAMES']:
            hcfile = os.path.join(rdir, rawhcfile)
            raw_infilepath1 = os.path.join(p['ARG_FILE_DIR'], hcfile)
            p = spirouImage.UpdateWaveSolutionHC(p, loc, raw_infilepath1)

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

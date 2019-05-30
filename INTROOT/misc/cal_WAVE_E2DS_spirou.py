#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_WAVE_E2DS_spirou.py [night_directory] [FPfitsfilename] [HCfiles]

Wavelength calibration incorporating the FP lines

Created on 2018-02-09 at 10:57

@author: cook
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouFLAT
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA

import cal_HC_E2DS_spirou

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_WAVE_E2DS_spirou.py'
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
def main(night_name=None, fpfile=None, hcfiles=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    if hcfiles is None or fpfile is None:
        names, types = ['fpfile', 'hcfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime(p, [0, 1], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(hcfiles=hcfiles, fpfile=fpfile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsdir='reduced',
                                    mainfitsfile='hcfiles')

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, fpfitsfilename = spirouStartup.SingleFileSetup(p, filename=p['FPFILE'])
    fiber1 = str(p['FIBER'])
    p, hcfilenames = spirouStartup.MultiFileSetup(p, files=p['HCFILES'])
    fiber2 = str(p['FIBER'])
    # set the hcfilename to the first hcfilenames
    hcfitsfilename = hcfilenames[0]

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Have to check that the fibers match
    # ----------------------------------------------------------------------
    if fiber1 == fiber2:
        p['FIBER'] = fiber1
        fsource = __NAME__ + '/main() & spirouStartup.GetFiberType()'
        p.set_source('FIBER', fsource)
    else:
        emsg = 'Fiber not matching for {0} and {1}, should be the same'
        eargs = [hcfitsfilename, fpfitsfilename]
        WLOG(p, 'error', emsg.format(*eargs))
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # set find line mode
    find_lines_mode = p['HC_FIND_LINES_MODE']

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read and combine all HC files except the first (fpfitsfilename)
    rargs = [p, 'add', hcfitsfilename, hcfilenames[1:]]
    p, hcdata, hchdr, hccdr = spirouImage.ReadImageAndCombine(*rargs)
    # read first file (fpfitsfilename)
    fpdata, fphdr, fpcdr, _, _ = spirouImage.ReadImage(p, fpfitsfilename)

    # add data and hdr to loc
    loc = ParamDict()
    loc['HCDATA'], loc['HCHDR'], loc['HCCDR'] = hcdata, hchdr, hccdr
    loc['FPDATA'], loc['FPHDR'], loc['FPCDR'] = fpdata, fphdr, fpcdr
    # set the source
    sources = ['HCDATA', 'HCHDR', 'HCCDR']
    loc.set_sources(sources, 'spirouImage.ReadImageAndCombine()')
    sources = ['FPDATA', 'FPHDR', 'FPCDR']
    loc.set_sources(sources, 'spirouImage.ReadImage()')

    # ----------------------------------------------------------------------
    # Get basic image properties for reference file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hchdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hchdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hchdr, name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, hchdr, name='acqtime', kind='julian')
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p, hchdr)

    # ----------------------------------------------------------------------
    # Obtain the flat
    # ----------------------------------------------------------------------
    # get the flat
    p, loc = spirouFLAT.GetFlat(p, loc, hchdr)

    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    p, loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hchdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')

    # correct the data with the flat
    # TODO: Should this be used?
    # log
    # WLOG(p, '', 'Applying flat correction')
    # loc['HCDATA'] = loc['HCDATA']/loc['FLAT']
    # loc['FPDATA'] = loc['FPDATA']/loc['FLAT']

    # ----------------------------------------------------------------------
    # Start plotting session
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive plot
        sPlt.start_interactive_session(p)

    # ----------------------------------------------------------------------
    # loop around fiber type
    # ----------------------------------------------------------------------
    for fiber in p['FIB_TYP']:
        # set fiber type for inside loop
        p['FIBER'] = fiber

        # ------------------------------------------------------------------
        # Instrumental drift computation (if previous solution exists)
        # ------------------------------------------------------------------
        # get key
        keydb = 'HCREF_{0}'.format(p['FIBER'])
        # check for key in calibDB
        if keydb in p['CALIBDB'].keys():
            # log process
            wmsg = ('Doing Instrumental drift computation from previous '
                    'calibration')
            WLOG(p, '', wmsg)
            # calculate instrument drift
            loc = spirouTHORCA.CalcInstrumentDrift(p, loc)

        # ------------------------------------------------------------------
        # Wave solution
        # ------------------------------------------------------------------
        # log message for loop
        wmsg = 'Processing Wavelength Calibration for Fiber {0}'
        WLOG(p, 'info', wmsg.format(p['FIBER']))

        # ------------------------------------------------------------------
        # Part 1 of cal_HC
        # ------------------------------------------------------------------
        p, loc = cal_HC_E2DS_spirou.part1(p, loc, mode=find_lines_mode)

        # ------------------------------------------------------------------
        # FP solution
        # ------------------------------------------------------------------
        # log message
        wmsg = 'Calculating FP wave solution'
        WLOG(p, '', wmsg)
        # calculate FP wave solution
        # spirouTHORCA.FPWaveSolution(p, loc, mode=find_lines_mode)
        spirouTHORCA.FPWaveSolutionNew(p, loc)

        # ------------------------------------------------------------------
        # FP solution plots
        # ------------------------------------------------------------------
        if p['DRS_PLOT'] > 0:
            # Plot the FP extracted spectrum against wavelength solution
            sPlt.wave_plot_final_fp_order(p, loc, iteration=1)
            # Plot the measured FP cavity width offset against line number
            sPlt.wave_local_width_offset_plot(p,loc)
            # Plot the FP line wavelength residuals
            sPlt.wave_fp_wavelength_residuals(p, loc)

        # ------------------------------------------------------------------
        # Part 2 of cal_HC
        # ------------------------------------------------------------------
        # set params for part2
        p['QC_RMS_LITTROW_MAX'] = p['QC_WAVE_RMS_LITTROW_MAX']
        p['QC_DEV_LITTROW_MAX'] = p['QC_WAVE_DEV_LITTROW_MAX']

        p['IC_HC_N_ORD_START_2'] = min(p['IC_HC_N_ORD_START_2'],
                                       p['IC_FP_N_ORD_START'])
        p['IC_HC_N_ORD_FINAL_2'] = max(p['IC_HC_N_ORD_FINAL_2'],
                                       p['IC_FP_N_ORD_FINAL'])

        # run part 2
        # p, loc = part2test(p, loc)
        p, loc = cal_HC_E2DS_spirou.part2(p, loc)

    # ----------------------------------------------------------------------
    # End plotting session
    # ----------------------------------------------------------------------
    # end interactive session
    sPlt.end_interactive_session(p)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())


# local copy of part2 to test more easily
def part2test(p, loc):
    # ------------------------------------------------------------------
    # Fit wavelength solution on identified lines (using Littrow)
    # ------------------------------------------------------------------
    # log message
    wmsg = ('On fiber {0} fitting wavelength solution on identified '
            'lines: (second pass)')
    WLOG(p, '', wmsg.format(p['FIBER']))
    # fit lines
    start, end = p['IC_HC_N_ORD_START_2'], p['IC_HC_N_ORD_FINAL_2']
    lls = loc['LITTROW_EXTRAP_SOL_1'][start: end]
    loc = spirouTHORCA.Fit1DSolution(p, loc, lls,  iteration=2)

    # ------------------------------------------------------------------
    # Littrow test
    # ------------------------------------------------------------------
    ckwargs = dict(ll=loc['LL_OUT_2'], iteration=2, log=True)
    loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

    # ------------------------------------------------------------------
    # Plot wave solution littrow check
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_check_plot(p, loc, iteration=2)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------
    ekwargs = dict(ll=loc['LL_OUT_2'], iteration=2)
    loc = spirouTHORCA.ExtrapolateLittrowSolution(p, loc, **ekwargs)

    # ------------------------------------------------------------------
    # Plot littrow solution
    # ------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_extrap_plot(p, loc, iteration=2)

    # ------------------------------------------------------------------
    # Join 0-24 and 25-36 solutions
    # ------------------------------------------------------------------
    loc = spirouTHORCA.JoinOrders(p, loc)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # check for infinites and NaNs in X_MEAN_2
    if ~np.isfinite(loc['X_MEAN_2']):
        # add failed message to the fail message list
        fmsg = 'NaN or Inf in X_MEAN_2'
        fail_msg.append(fmsg)
        passed = False
    # iterate through Littrow test cut values
    # for x_it in range(len(loc['X_CUT_POINTS_2'])):
    for x_it in range(1, len(loc['X_CUT_POINTS_2']), 2):
        # get x cut point
        x_cut_point = loc['X_CUT_POINTS_2'][x_it]
        # get the sigma for this cut point
        sig_littrow = loc['LITTROW_SIG_2'][x_it]
        # get the abs min and max dev littrow values
        min_littrow = abs(loc['LITTROW_MINDEV_2'][x_it])
        max_littrow = abs(loc['LITTROW_MAXDEV_2'][x_it])
        # check if sig littrow is above maximum
        rms_littrow_max = p['QC_RMS_LITTROW_MAX']
        dev_littrow_max = p['QC_DEV_LITTROW_MAX']
        if sig_littrow > rms_littrow_max:
            fmsg = ('Littrow test (x={0}) failed (sig littrow = '
                    '{1:.2f} > {2:.2f})')
            fargs = [x_cut_point, sig_littrow, rms_littrow_max]
            fail_msg.append(fmsg.format(*fargs))
            passed = False
        # check if min/max littrow is out of bounds
        if np.max([max_littrow, min_littrow]) > dev_littrow_max:
            fmsg = ('Littrow test (x={0}) failed (min|max dev = '
                    '{1:.2f}|{2:.2f} > {3:.2f})')
            fargs = [x_cut_point, min_littrow, max_littrow, dev_littrow_max]
            fail_msg.append(fmsg.format(*fargs))
            passed = False
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG(p, 'info',
             'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG(p, 'warning', wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ------------------------------------------------------------------
    # archive result in e2ds spectra
    # ------------------------------------------------------------------
    # get raw input file name
    raw_infile1 = os.path.basename(p['HCFILES'][0])
    raw_infile2 = os.path.basename(p['FPFILE'])
    # get wave filename
    wavefits, tag1 = spirouConfig.Constants.WAVE_FILE_FP(p)
    wavefitsname = os.path.split(wavefits)[-1]
    WLOG(p, '', wavefits)

    # log progress
    wargs = [p['FIBER'], wavefitsname]
    wmsg = 'Write wavelength solution for Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(*wargs))
    # write solution to fitsfilename header
    # copy original keys
    hdict = spirouImage.CopyOriginalKeys(loc['HCHDR'], loc['HCCDR'])
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag1)
    # set the input files
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBFLAT'], value=p['FLATFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'], value=p['BLAZFILE'])
    # add quality control
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    # add number of orders
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_ORD_N'],
                               value=loc['LL_PARAM_FINAL'].shape[0])
    # add degree of fit
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVE_LL_DEG'],
                               value=loc['LL_PARAM_FINAL'].shape[1]-1)
    # add wave solution
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                     values=loc['LL_PARAM_FINAL'])
    # write original E2DS file and add header keys (via hdict)
    # spirouImage.WriteImage(p['FITSFILENAME'], loc['HCDATA'], hdict)

    # write the wave "spectrum"
    p = spirouImage.WriteImage(p, wavefits, loc['LL_FINAL'], hdict)

    # get filename for E2DS calibDB copy of FITSFILENAME
    e2dscopy_filename, tag2 = spirouConfig.Constants.WAVE_E2DS_COPY(p)

    wargs = [p['FIBER'], os.path.split(e2dscopy_filename)[-1]]
    wmsg = 'Write reference E2DS spectra for Fiber {0} in {1}'
    WLOG(p, '', wmsg.format(*wargs))

    # make a copy of the E2DS file for the calibBD
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag2)
    p = spirouImage.WriteImage(p, e2dscopy_filename, loc['HCDATA'], hdict)

    # ------------------------------------------------------------------
    # Save to result table
    # ------------------------------------------------------------------
    # calculate stats for table
    final_mean = 1000 * loc['X_MEAN_2']
    final_var = 1000 * loc['X_VAR_2']
    num_iterations = int(np.nansum(loc['X_ITER_2'][:, 2]))
    err = 1000 * np.sqrt(final_var/num_iterations)
    sig_littrow = 1000 * np.array(loc['LITTROW_SIG_2'])
    # construct filename
    wavetbl = spirouConfig.Constants.WAVE_TBL_FILE_FP(p)
    wavetblname = os.path.split(wavetbl)[-1]
    # construct and write table
    columnnames = ['night_name', 'file_name', 'fiber', 'mean', 'rms',
                   'N_lines', 'err', 'rms_L0', 'rms_L1', 'rms_L2']
    columnformats = ['{:20s}', '{:30s}', '{:3s}', '{:7.4f}', '{:6.2f}',
                     '{:3d}', '{:6.3f}', '{:6.2f}', '{:6.2f}', '{:6.2f}']
    columnvalues = [[p['ARG_NIGHT_NAME']], [p['ARG_FILE_NAMES'][0]],
                    [p['FIBER']], [final_mean], [final_var],
                    [num_iterations], [err], [sig_littrow[0]],
                    [sig_littrow[1]], [sig_littrow[2]]]
    # make table
    table = spirouImage.MakeTable(p, columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # merge table
    wmsg = 'Global result summary saved in {0}'
    WLOG(p, '', wmsg.format(wavetblname))
    spirouImage.MergeTable(p, table, wavetbl, fmt='ascii.rst')

    # ------------------------------------------------------------------
    # Save line list table file
    # ------------------------------------------------------------------
    # construct filename
    wavelltbl = spirouConfig.Constants.WAVE_LINE_FILE(p)
    wavelltblname = os.path.split(wavelltbl)[-1]
    # construct and write table
    columnnames = ['order', 'll', 'dv', 'w', 'xi', 'xo', 'dvdx']
    columnformats = ['{:.0f}', '{:12.4f}', '{:13.5f}', '{:12.4f}',
                     '{:12.4f}', '{:12.4f}', '{:8.4f}']
    columnvalues = []
    # construct column values (flatten over orders)
    for it in range(len(loc['X_DETAILS_2'])):
        for jt in range(len(loc['X_DETAILS_2'][it][0])):
            row = [float(it), loc['X_DETAILS_2'][it][0][jt],
                   loc['LL_DETAILS_2'][it][0][jt],
                   loc['X_DETAILS_2'][it][3][jt],
                   loc['X_DETAILS_2'][it][1][jt],
                   loc['X_DETAILS_2'][it][2][jt],
                   loc['SCALE_2'][it][jt]]
            columnvalues.append(row)

    # log saving
    wmsg = 'List of lines used saved in {0}'
    WLOG(p, '', wmsg.format(wavelltblname))

    # make table
    columnvalues = np.array(columnvalues).T
    table = spirouImage.MakeTable(p, columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # write table
    spirouImage.WriteTable(p, table, wavelltbl, fmt='ascii.rst')

    # ------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ------------------------------------------------------------------
    # if p['QC']:
    #     # set the wave key
    #     keydb = 'WAVE_{0}'.format(p['FIBER'])
    #     # copy wave file to calibDB folder
    #     spirouDB.PutFile(p, wavefits)
    #     # update the master calib DB file with new key
    #     spirouDB.UpdateMaster(p, keydb, wavefitsname, loc['HCHDR'])
    #
    #     # set the hcref key
    #     keydb = 'HCREF_{0}'.format(p['FIBER'])
    #     # copy wave file to calibDB folder
    #     spirouDB.PutFile(p, e2dscopy_filename)
    #     # update the master calib DB file with new key
    #     e2dscopyfits = os.path.split(e2dscopy_filename)[-1]
    #     spirouDB.UpdateMaster(p, keydb, e2dscopyfits, loc['HCHDR'])

    # return p and loc
    return p, loc


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

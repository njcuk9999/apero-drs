#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_HC_E2DS_spirou.py [night_directory] [fitsfilename]

Wavelength calibration

Created on 2018-07-20
@author: artigau, hobson, cook
"""

from __future__ import division
import numpy as np
import os
from collections import OrderedDict

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS.spirouTHORCA import spirouWAVE

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
plt = sPlt.plt
plt.ion()
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define functions
# =============================================================================

def main(night_name=None, fpfile=None, hcfiles=None):
    """
    cal_WAVE_E2DS.py main function, if night_name and files are None uses
    arguments from run time i.e.:
        cal_DARK_spirou.py [night_directory] [fpfile] [hcfiles]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param fpfile: string, or None, the FP file to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)
    :param hcfiles: string, list or None, the list of HC files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------

    # test files TC2
    # night_name = 'AT5/AT5-12/2018-05-29_17-41-44/'
    # fpfile = '2279844a_fp_fp_pp_e2dsff_AB.fits'
    # hcfiles = ['2279845c_hc_pp_e2dsff_AB.fits']

    # test files TC3
    # night_name = 'TC3/AT5/AT5-12/2018-07-24_16-17-57/'
    # fpfile = '2294108a_pp_e2dsff_AB.fits'
    # hcfiles = ['2294115c_pp_e2dsff_AB.fits']

    # night_name = 'TC3/AT5/AT5-12/2018-07-25_16-49-50/'
    # fpfile = '2294223a_pp_e2dsff_AB.fits'
    # hcfiles = ['2294230c_pp_e2dsff_AB.fits']

    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    if hcfiles is None or fpfile is None:
        names, types = ['fpfile', 'hcfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime([0, 1], types, names,
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
        WLOG('error', p['LOG_OPT'], emsg.format(*eargs))
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Read FP and HC files
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
    p, loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hchdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')

    # ----------------------------------------------------------------------
    # Read wave solution
    # ----------------------------------------------------------------------
    # wavelength file; we will use the polynomial terms in its header,
    # NOT the pixel values that would need to be interpolated

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
    loc['WAVEPARAMS'], loc['WAVE_INIT'], loc['WAVEFILE'] = wout
    loc.set_sources(['WAVE_INIT', 'WAVEFILE', 'WAVEPARAMS'], wsource)
    poly_wave_sol = loc['WAVEPARAMS']

    # ----------------------------------------------------------------------
    # Read UNe solution
    # ----------------------------------------------------------------------
    wave_UNe, amp_UNe = spirouImage.ReadLineList(p)
    loc['LL_LINE'], loc['AMPL_LINE'] = wave_UNe, amp_UNe
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
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()

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
    if p['DRS_PLOT']:
        sPlt.wave_ea_plot_line_profiles(p, loc)

    # ----------------------------------------------------------------------
    # End plotting session
    # ----------------------------------------------------------------------
    # end interactive session
    if p['DRS_PLOT']:
        sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    passed, fail_msg = True, []
    # quality control on sigma clip (sig1 > qc_hc_wave_sigma_max
    if loc['SIG1'] > p['QC_HC_WAVE_SIGMA_MAX']:
        fmsg = 'Sigma too high ({0:.5f} > {1:.5f})'
        fail_msg.append(fmsg.format(loc['SIG1'], p['QC_HC_WAVE_SIGMA_MAX']))
        passed = False
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['LOG_OPT'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # TODO: --> Below is not etienne's code!

    # ----------------------------------------------------------------------
    # Set up all_lines storage
    # ----------------------------------------------------------------------

    # initialise up all_lines storage
    all_lines_1 = []

    # get parameters from p
    n_ord_start = p['IC_HC_N_ORD_START_2']
    n_ord_final = p['IC_HC_N_ORD_FINAL_2']
    pixel_shift_inter = p['PIXEL_SHIFT_INTER']
    pixel_shift_slope = p['PIXEL_SHIFT_SLOPE']

    # get values from loc
    xgau = np.array(loc['XGAU_T'])
    dv = np.array(loc['DV_T'])
    fit_per_order = np.array(loc['POLY_WAVE_SOL'])
    ew = np.array(loc['EW_T'])
    peak = np.array(loc['PEAK_T'])
    amp_catalog = np.array(loc['AMP_CATALOG'])
    wave_catalog = np.array(loc['WAVE_CATALOG'])
    ord_t = np.array(loc['ORD_T'])

    # loop through orders
    for iord in range(n_ord_start, n_ord_final):
        # keep relevant lines
        # -> right order
        # -> finite dv
        gg = (ord_t == iord) & (np.isfinite(dv))
        nlines = np.sum(gg)
        # put lines into ALL_LINES structure
        # reminder:
        # gparams[0] = output wavelengths
        # gparams[1] = output sigma(gauss fit width)
        # gparams[2] = output amplitude(gauss fit)
        # gparams[3] = difference in input / output wavelength
        # gparams[4] = input amplitudes
        # gparams[5] = output pixel positions
        # gparams[6] = output pixel sigma width (gauss fit width in pixels)
        # gparams[7] = output weights for the pixel position

        # dummy array for weights
        test = np.ones(np.shape(xgau[gg]), 'd')
        # get the final wavelength value for each peak in order
        output_wave_1 = np.polyval(fit_per_order[iord][::-1], xgau[gg])
        # convert the pixel equivalent width to wavelength units
        xgau_ew_ini = xgau[gg] - ew[gg]/2
        xgau_ew_fin = xgau[gg] + ew[gg]/2
        ew_ll_ini = np.polyval(fit_per_order[iord, :], xgau_ew_ini)
        ew_ll_fin = np.polyval(fit_per_order[iord, :], xgau_ew_fin)
        ew_ll = ew_ll_fin - ew_ll_ini
        # put all lines in the order into array
        gau_params = np.column_stack((output_wave_1, ew_ll, peak[gg],
                                      wave_catalog[gg] - output_wave_1, amp_catalog[gg],
                                      xgau[gg], ew[gg], test))
        # append the array for the order into a list
        all_lines_1.append(gau_params)
        # save dv in km/s and auxiliary order number
#        res_1 = np.concatenate((res_1,2.997e5*(input_wave - output_wave_1)/output_wave_1))
#        ord_save = np.concatenate((ord_save, test*iord))

    # add to loc
    loc['ALL_LINES_1'] = all_lines_1
    loc['LL_PARAM_1'] = np.array(fit_per_order)
    loc['LL_OUT_1'] = np.array(loc['WAVE_MAP2'])
    loc.set_sources(['ALL_LINES_1', 'LL_PARAM_1'], __NAME__ + '/main()')


    # For compatibility w/already defined functions, I need to save here all_lines_2
    all_lines_2 = list(all_lines_1)
    loc['ALL_LINES_2'] = all_lines_2
#    loc['LL_PARAM_2'] = np.fliplr(fit_per_order)
#    loc['LL_OUT_2'] = np.array(loc['WAVE_MAP2'])
#    loc.set_sources(['ALL_LINES_2', 'LL_PARAM_2'], __NAME__ + '/main()')

    # ------------------------------------------------------------------
    # Littrow test
    # ------------------------------------------------------------------

    # calculate echelle orders
    o_orders = np.arange(n_ord_start, n_ord_final)
    echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
    loc['ECHELLE_ORDERS'] = echelle_order
    loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

    # reset Littrow fit degree
    p['IC_LITTROW_FIT_DEG_1'] = 7

    # Do Littrow check
    ckwargs = dict(ll=loc['LL_OUT_1'][n_ord_start:n_ord_final, :], iteration=1, log=True)
    loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

    # Plot wave solution littrow check
    if p['DRS_PLOT']:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_check_plot(p, loc, iteration=1)

    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------
    ekwargs = dict(ll=loc['LL_OUT_1'], iteration=1)
    loc = spirouTHORCA.ExtrapolateLittrowSolution(p, loc, **ekwargs)

    # ------------------------------------------------------------------
    # Plot littrow solution
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_extrap_plot(loc, iteration=1)

    # ------------------------------------------------------------------
    # Join 0-46 and 47-48 solutions
    # ------------------------------------------------------------------

    # # the littrow extrapolation (for orders > n_ord_final_2)
    # litt_extrap_sol_red = loc['LITTROW_EXTRAP_SOL_1'][n_ord_final:]
    # litt_extrap_sol_param_red = loc['LITTROW_EXTRAP_PARAM_1'][n_ord_final:]
    #
    # # the wavelength solution for n_ord_start - n_ord_final
    # # taking from loc allows avoiding an if smooth check
    # ll_out = loc['LL_OUT_1'][n_ord_start:n_ord_final]
    # param_out = loc['LL_PARAM_1'][n_ord_start:n_ord_final]
    #
    # print(np.shape(litt_extrap_sol_param_red))
    # print(np.shape(param_out))
    #
    # # create stack
    # ll_stack, param_stack = [], []
    # # wavelength solution for n_ord_start - n_ord_final
    # if len(ll_out) > 0:
    #     ll_stack.append(ll_out)
    #     param_stack.append(param_out)
    # # add extrapolation from littrow to orders > n_ord_final
    # if len(litt_extrap_sol_red) > 0:
    #     ll_stack.append(litt_extrap_sol_red)
    #     param_stack.append(litt_extrap_sol_param_red)
    #
    # # convert stacks to arrays and add to storage
    # loc['LL_OUT_2'] = np.vstack(ll_stack)
    # loc['LL_PARAM_2'] = np.vstack(param_stack)
    # loc.set_sources(['LL_OUT_2', 'LL_PARAM_2'], __NAME__ + '/main()')

    # TODO can I remove this?
    #     # rename for compatibility w FP solution functions
    #    loc['LITTROW_EXTRAP_SOL_1'] = np.vstack(ll_stack)
    #    loc['LITTROW_EXTRAP_PARAM_1'] = np.vstack(param_stack)
    loc['LITTROW_EXTRAP_SOL_1'] = np.array(loc['LL_OUT_1'])
    loc['LITTROW_EXTRAP_PARAM_1'] = np.array(loc['LL_PARAM_1'])

    # ------------------------------------------------------------------
    # Incorporate FP into solution
    # ------------------------------------------------------------------

    use_fp = True

    if use_fp:
        # ------------------------------------------------------------------
        # Find FP lines
        # ------------------------------------------------------------------
        # print message to screen
        wmsg = 'Identification of lines in reference file: {0}'
        WLOG('', p['LOG_OPT'], wmsg.format(fpfile))

        # ------------------------------------------------------------------
        # Get the FP solution
        # ------------------------------------------------------------------

        loc = spirouTHORCA.FPWaveSolutionNew(p, loc)

        # ------------------------------------------------------------------
        # FP solution plots
        # ------------------------------------------------------------------
        if p['DRS_PLOT']:
            # Plot the FP extracted spectrum against wavelength solution
            sPlt.wave_plot_final_fp_order(p, loc, iteration=1)
            # Plot the measured FP cavity width offset against line number
            sPlt.wave_local_width_offset_plot(loc)
            # Plot the FP line wavelength residuals
            sPlt.wave_fp_wavelength_residuals(loc)

    # ------------------------------------------------------------------
    # Create new wavelength solution
    # ------------------------------------------------------------------
    # TODO: Melissa fault - fix later
    p['IC_HC_N_ORD_START_2'] = min(p['IC_HC_N_ORD_START_2'],
                                   p['IC_FP_N_ORD_START'])
    p['IC_HC_N_ORD_FINAL_2'] = max(p['IC_HC_N_ORD_FINAL_2'],
                                   p['IC_FP_N_ORD_FINAL'])
    start = p['IC_HC_N_ORD_START_2']
    end = p['IC_HC_N_ORD_FINAL_2']

    # recalculate echelle orders for Fit1DSolution
    o_orders = np.arange(start,end)
    echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
    loc['ECHELLE_ORDERS'] = echelle_order
    loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')

    # select the orders to fit
    ll = loc['LITTROW_EXTRAP_SOL_1'][start:end]
    loc = spirouTHORCA.Fit1DSolution(p, loc, ll,  iteration=2)
    # from here, LL_OUT_2 wil be 0-47

    # ------------------------------------------------------------------
    # Repeat Littrow test
    # ------------------------------------------------------------------

    # Do Littrow check
    ckwargs = dict(ll=loc['LL_OUT_2'][start:end, :], iteration=2, log=True)
    loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

    # Plot wave solution littrow check
    if p['DRS_PLOT']:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_check_plot(p, loc, iteration=2)

    # ------------------------------------------------------------------
    # extrapolate Littrow solution
    # ------------------------------------------------------------------
    ekwargs = dict(ll=loc['LL_OUT_2'], iteration=2)
    loc = spirouTHORCA.ExtrapolateLittrowSolution(p, loc, **ekwargs)

    # ------------------------------------------------------------------
    # Plot littrow solution
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # plot littrow x pixels against fitted wavelength solution
        sPlt.wave_littrow_extrap_plot(loc, iteration=2)

    # ------------------------------------------------------------------
    # Join 0-47 and 47-49 solutions
    # ------------------------------------------------------------------
    loc = spirouTHORCA.JoinOrders(p, loc)

    # ------------------------------------------------------------------
    # Plot single order, wavelength-calibrated, with found lines
    # ------------------------------------------------------------------

    if p['DRS_PLOT']:
        sPlt.wave_ea_plot_single_order(p, loc)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # get parameters ffrom p
    p['QC_RMS_LITTROW_MAX'] = p['QC_HC_RMS_LITTROW_MAX']
    p['QC_DEV_LITTROW_MAX'] = p['QC_HC_DEV_LITTROW_MAX']
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # check for infinites and NaNs in mean residuals from fit
    if ~np.isfinite(loc['X_MEAN_2']):
        # add failed message to the fail message list
        fmsg = 'NaN or Inf in X_MEAN_2'
        fail_msg.append(fmsg)
        passed = False

    # iterate through Littrow test cut values
    lit_it = 2
    # checks every other value
    for x_it in range(1, len(loc['X_CUT_POINTS_'+str(lit_it)]), 2):
        # get x cut point
        x_cut_point = loc['X_CUT_POINTS_'+str(lit_it)][x_it]
        # get the sigma for this cut point
        sig_littrow = loc['LITTROW_SIG_'+str(lit_it)][x_it]
        # get the abs min and max dev littrow values
        min_littrow = abs(loc['LITTROW_MINDEV_'+str(lit_it)][x_it])
        max_littrow = abs(loc['LITTROW_MAXDEV_'+str(lit_it)][x_it])
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
        WLOG('info', p['LOG_OPT'],
             'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ------------------------------------------------------------------
    # archive result in e2ds spectra
    # ------------------------------------------------------------------
    # get raw input file name
    raw_infile1 = os.path.basename(p['HCFILES'][0])
    raw_infile2 = os.path.basename(p['FPFILE'])
    # get wave filename
    wavefits, tag1 = spirouConfig.Constants.WAVE_FILE_EA(p)
    wavefitsname = os.path.split(wavefits)[-1]

    # log progress
    wargs = [p['FIBER'], wavefits]
    wmsg = 'Write wavelength solution for Fiber {0} in {1}'
    WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
    # write solution to fitsfilename header
    # copy original keys
    hdict = spirouImage.CopyOriginalKeys(loc['HCHDR'], loc['HCCDR'])
    # add version number
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag1)
    # set the input files
    hdict = spirouImage.AddKey(hdict, p['KW_BLAZFILE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(hdict, p['kw_HCFILE'], value=raw_infile1)
    hdict = spirouImage.AddKey(hdict, p['kw_FPFILE'], value=raw_infile2)
    # add quality control
    hdict = spirouImage.AddKey(hdict, p['KW_DRS_QC'], value=p['QC'])
    # add number of orders
    hdict = spirouImage.AddKey(hdict, p['KW_WAVE_ORD_N'],
                               value=loc['LL_PARAM_FINAL'].shape[0])
    # add degree of fit
    hdict = spirouImage.AddKey(hdict, p['KW_WAVE_LL_DEG'],
                               value=loc['LL_PARAM_FINAL'].shape[1]-1)
    # add wave solution
    hdict = spirouImage.AddKey2DList(hdict, p['KW_WAVE_PARAM'],
                                     values=loc['LL_PARAM_FINAL'])
    # write original E2DS file and add header keys (via hdict)
    # spirouImage.WriteImage(p['FITSFILENAME'], loc['HCDATA'], hdict)

    # write the wave "spectrum"
    p = spirouImage.WriteImage(p, wavefits, loc['LL_FINAL'], hdict)

    # get filename for E2DS calibDB copy of FITSFILENAME
    e2dscopy_filename = spirouConfig.Constants.WAVE_E2DS_COPY(p)[0]
    print(e2dscopy_filename)
    wargs = [p['FIBER'], os.path.split(e2dscopy_filename)[-1]]
    wmsg = 'Write reference E2DS spectra for Fiber {0} in {1}'
    WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

    # make a copy of the E2DS file for the calibBD
    p = spirouImage.WriteImage(p, e2dscopy_filename, loc['HCDATA'], hdict)

    # ------------------------------------------------------------------
    # Save to result table
    # ------------------------------------------------------------------
    # calculate stats for table
    final_mean = 1000 * loc['X_MEAN_2']
    final_var = 1000 * loc['X_VAR_2']
    num_lines = int(np.sum(loc['X_ITER_2'][:, 2]))        #loc['X_ITER_2']
    err = 1000 * np.sqrt(loc['X_VAR_2']/num_lines)
    sig_littrow = 1000 * np.array(loc['LITTROW_SIG_'+str(lit_it)])
    # construct filename
    wavetbl = spirouConfig.Constants.WAVE_TBL_FILE_EA(p)
    wavetblname = os.path.split(wavetbl)[-1]
    # construct and write table
    columnnames = ['night_name', 'file_name', 'fiber', 'mean', 'rms',
                   'N_lines', 'err', 'rms_L500', 'rms_L1000', 'rms_L1500',
                    'rms_L2000', 'rms_L2500', 'rms_L3000', 'rms_L3500']
    columnformats = ['{:20s}', '{:30s}', '{:3s}', '{:7.4f}', '{:6.2f}',
                     '{:3d}', '{:6.3f}', '{:6.2f}', '{:6.2f}', '{:6.2f}',
                     '{:6.2f}', '{:6.2f}', '{:6.2f}', '{:6.2f}']
    columnvalues = [[p['ARG_NIGHT_NAME']], [p['ARG_FILE_NAMES'][0]],
                    [p['FIBER']], [final_mean], [final_var],
                    [num_lines], [err], [sig_littrow[0]],
                    [sig_littrow[1]], [sig_littrow[2]], [sig_littrow[3]],
                    [sig_littrow[4]], [sig_littrow[5]], [sig_littrow[6]]]
    # make table
    table = spirouImage.MakeTable(columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # merge table
    wmsg = 'Global result summary saved in {0}'
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(wavetblname))
    spirouImage.MergeTable(table, wavetbl, fmt='ascii.rst')

    # ----------------------------------------------------------------------
    # Save resolution and line profiles to file
    # ----------------------------------------------------------------------
    raw_infile = os.path.basename(p['FITSFILENAME'])
    # get wave filename
    resfits, tag3 = spirouConfig.Constants.WAVE_RES_FILE_EA(p)
    resfitsname = os.path.basename(resfits)
    WLOG('', p['LOG_OPT'], 'Saving wave resmap to {0}'.format(resfitsname))

    # make a copy of the E2DS file for the calibBD
    # set the version
    hdict = OrderedDict()
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag3)
    hdict = spirouImage.AddKey(hdict, p['kw_HCFILE'], value=raw_infile)

    # get res data in correct format
    resdata, hdicts = spirouTHORCA.GenerateResFiles(p, loc, hdict)
    # save to file
    p = spirouImage.WriteImageMulti(p, resfits, resdata, hdicts=hdicts)

    # ------------------------------------------------------------------
    # Save line list table file
    # ------------------------------------------------------------------
    # construct filename

    # TODO proper column values

    wavelltbl = spirouConfig.Constants.WAVE_LINE_FILE_EA(p)
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
    WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(wavelltblname))

    # make table
    columnvalues = np.array(columnvalues).T
    table = spirouImage.MakeTable(columns=columnnames, values=columnvalues,
                                  formats=columnformats)
    # write table
    spirouImage.WriteTable(table, wavelltbl, fmt='ascii.rst')

    # ------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ------------------------------------------------------------------
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
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
    # return p and loc
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

#

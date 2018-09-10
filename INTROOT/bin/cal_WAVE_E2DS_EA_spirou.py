#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_HC_E2DS_spirou.py [night_directory] [fitsfilename]

Wavelength calibration

Created on 2018-07-20
@author: artigau, hobson, cook
"""

from __future__ import division
from scipy.optimize import curve_fit
import numpy as np
import os
import warnings

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
    :param fhciles: string, list or None, the list of HC files to use for
                  arg_file_names and fitsfilename
                  (if None assumes arg_file_names was set from run time)

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------

    # test files TC2
    #night_name = 'AT5/AT5-12/2018-05-29_17-41-44/'
    #fpfile = '2279844a_fp_fp_pp_e2dsff_AB.fits'
    #hcfiles = ['2279845c_hc_pp_e2dsff_AB.fits']

    # test files TC3
    #night_name = 'TC3/AT5/AT5-12/2018-07-24_16-17-57/'
    #fpfile = '2294108a_pp_e2dsff_AB.fits'
    #hcfiles = ['2294115c_pp_e2dsff_AB.fits']

    #night_name = 'TC3/AT5/AT5-12/2018-07-25_16-49-50/'
    #fpfile = '2294223a_pp_e2dsff_AB.fits'
    #hcfiles = ['2294230c_pp_e2dsff_AB.fits']

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
    loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hchdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')

    # ----------------------------------------------------------------------
    # Read wave solution
    # ----------------------------------------------------------------------
    # wavelength file; we will use the polynomial terms in its header,
    # NOT the pixel values that would need to be interpolated

    # getting header info with wavelength polynomials
    wdata = spirouImage.ReadWaveFile(p, hchdr,return_header=True)
    wave, wave_hdr = wdata
    loc['WAVE_INIT'] = wave
    loc['WAVEHDR'] = wave_hdr
    loc.set_source('WAVE_INIT', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

    # get wave params from wave header
    poly_wave_sol = spirouImage.ReadWaveParams(p, wave_hdr)
    loc['WAVEPARAMS'] = poly_wave_sol
    loc.set_source('WAVEPARAMS', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

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
# Set up all_lines storage list for both wavelength solutions
# ----------------------------------------------------------------------
#
#     # initialise up all_lines storage
#     all_lines_1 = []
#     all_lines_2 = []
#
#     # initialise storage for residuals
#     res_1 = []
#     res_2 = []
#     ord_save = []
#
#     n_ord_start = p['IC_HC_N_ORD_START_2']
#     n_ord_final = p['IC_HC_N_ORD_FINAL_2']
#
#     # first wavelength solution (no smoothing)
#     # loop through orders
#     for iord in range(n_ord_start, n_ord_final):
#         # keep relevant lines
#         # -> right order
#         # -> finite dv
#         gg = (ord == iord) & (np.isfinite(dv))
#         nlines = np.sum(gg)
#         # put lines into ALL_LINES structure
#         # reminder:
#         # gparams[0] = output wavelengths
#         # gparams[1] = output sigma(gauss fit width)
#         # gparams[2] = output amplitude(gauss fit)
#         # gparams[3] = difference in input / output wavelength
#         # gparams[4] = input amplitudes
#         # gparams[5] = output pixel positions
#         # gparams[6] = output pixel sigma width (gauss fit width in pixels)
#         # gparams[7] = output weights for the pixel position
#
#         # dummy array for weights
#         test = np.ones(np.shape(xgau[gg]), 'd')
#         # get the final wavelength value for each peak in order
#         output_wave_1 = np.polyval(fit_per_order[iord, :], xgau[gg])
#         # get the initial solution wavelength value for each peak in the order
#         # allow pixel shifting
#         xgau_shift = xgau[gg] + pixel_shift_inter + pixel_shift_slope*xgau[gg]
#         input_wave = np.polyval((poly_wave_sol[iord, :])[::-1], xgau_shift)
#         # convert the pixel equivalent width to wavelength units
#         xgau_ew_ini = xgau[gg] - ew[gg]/2
#         xgau_ew_fin = xgau[gg] + ew[gg]/2
#         ew_ll_ini = np.polyval(fit_per_order[iord, :], xgau_ew_ini)
#         ew_ll_fin = np.polyval(fit_per_order[iord, :], xgau_ew_fin)
#         ew_ll = ew_ll_fin - ew_ll_ini
#         # put all lines in the order into array
#         gau_params = np.column_stack((output_wave_1, ew_ll, peak1[gg], input_wave-output_wave_1,
#                                       amp_catalog[gg], xgau[gg], ew[gg], test))
#         # append the array for the order into a list
#         all_lines_1.append(gau_params)
#         # save dv in km/s and auxiliary order number
#         res_1 = np.concatenate((res_1,2.997e5*(input_wave - output_wave_1)/output_wave_1))
#         ord_save = np.concatenate((ord_save, test*iord))
#
#     # add to loc
#     loc['ALL_LINES_1'] = all_lines_1
#     loc['LL_PARAM_1'] = np.fliplr(fit_per_order)
#     loc.set_sources(['ALL_LINES_1', 'LL_PARAM_1'], __NAME__ + '/main()')
#
#     # second wavelength solution (smoothed)
#     if poly_smooth:
#         # loop through orders
#         for iord in range(nbo):
#             # keep relevant lines
#             # -> right order
#             # -> finite dv
#             gg = (ord == iord) & (np.isfinite(dv))
#             nlines = np.sum(gg)
#             # put lines into ALL_LINES structure
#             # reminder:
#             # gparams[0] = output wavelengths
#             # gparams[1] = output sigma(gauss fit width)
#             # gparams[2] = output amplitude(gauss fit)
#             # gparams[3] = difference in input / output wavelength
#             # gparams[4] = input amplitudes
#             # gparams[5] = output pixel positions
#             # gparams[6] = output pixel sigma width (gauss fit width in pixels)
#             # gparams[7] = output weights for the pixel position
#
#             # dummy array for weights
#             test = np.ones(np.shape(xgau[gg]), 'd')
#             # get the final wavelength value for each peak in order
#             output_wave_2 = np.polyval(new_wavelength_solution_polyfit[:, iord], xgau[gg])
#             # get the initial solution wavelength value for each peak in the order
#             # allow pixel shifting
#             xgau_shift = xgau[gg] + pixel_shift_inter + pixel_shift_slope * xgau[gg]
#             input_wave = np.polyval((poly_wave_sol[iord, :])[::-1], xgau_shift)
#             # convert the pixel equivalent width to wavelength units
#             xgau_ew_ini = xgau[gg] - ew[gg]/2
#             xgau_ew_fin = xgau[gg] + ew[gg]/2
#             ew_ll_ini = np.polyval(new_wavelength_solution_polyfit[:, iord], xgau_ew_ini)
#             ew_ll_fin = np.polyval(new_wavelength_solution_polyfit[:, iord], xgau_ew_fin)
#             ew_ll = ew_ll_fin - ew_ll_ini
#             # put all lines in the order into array
#             gau_params = np.column_stack((output_wave_2, ew_ll, peak1[gg], input_wave-output_wave_2,
#                                           amp_catalog[gg], xgau[gg], ew[gg], test))
#             # append the array for the order into a list
#             all_lines_2.append(gau_params)
#             res_2 = np.concatenate((res_2, 2.997e5*(input_wave - output_wave_2)/output_wave_2))
#
#     # For compatibility w/already defined functions, I need to save here all_lines_2
#     if poly_smooth:
#         loc['ALL_LINES_2'] = all_lines_2
#         loc['LL_PARAM_2'] = np.fliplr(np.transpose(new_wavelength_solution_polyfit))
#         loc.set_sources(['ALL_LINES_2', 'LL_PARAM_2'], __NAME__ + '/main()')
#     else:
#         all_lines_2 = list(all_lines_1)
#         loc['ALL_LINES_2'] = all_lines_2
#         loc['LL_PARAM_2'] = np.fliplr(fit_per_order)
#         loc['LL_OUT_2'] = loc['LL_OUT_1']
#         loc.set_sources(['ALL_LINES_2', 'LL_PARAM_2'], __NAME__ + '/main()')
#
#
#     # ------------------------------------------------------------------
#     # Littrow test
#     # ------------------------------------------------------------------
#
#     # set up start and end orders depending on if smoothing was used
#     if poly_smooth:
#         # set up echelle orders
#         n_ord_start = 0
#         n_ord_final = 49
#
#     # calculate echelle orders
#     o_orders = np.arange(n_ord_start, n_ord_final)
#     echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
#     loc['ECHELLE_ORDERS'] = echelle_order
#     loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')
#
#     # reset Littrow fit degree
#     p['IC_LITTROW_FIT_DEG_2'] = 6
#
#     # Do Littrow check
#     ckwargs = dict(ll=loc['LL_OUT_2'][n_ord_start:n_ord_final, :], iteration=2, log=True)
#     loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)
#
#     # Plot wave solution littrow check
#     if p['DRS_PLOT']:
#         # plot littrow x pixels against fitted wavelength solution
#         sPlt.wave_littrow_check_plot(p, loc, iteration=2)
#
#     # ------------------------------------------------------------------
#     # extrapolate Littrow solution
#     # ------------------------------------------------------------------
#     ekwargs = dict(ll=loc['LL_OUT_2'], iteration=2)
#     loc = spirouTHORCA.ExtrapolateLittrowSolution(p, loc, **ekwargs)
#
#     # ------------------------------------------------------------------
#     # Join 0-46 and 47-48 solutions
#     # ------------------------------------------------------------------
#
#     # the littrow extrapolation (for orders > n_ord_final_2)
#     litt_extrap_sol_red = loc['LITTROW_EXTRAP_SOL_2'][n_ord_final:]
#     litt_extrap_sol_param_red = loc['LITTROW_EXTRAP_PARAM_2'][n_ord_final:]
#
#     # the wavelength solution for n_ord_start - n_ord_final
#     # taking from loc allows avoiding an if smooth check
#     ll_out = loc['LL_OUT_2'][n_ord_start:n_ord_final]
#     param_out = loc['LL_PARAM_2'][n_ord_start:n_ord_final]
#
#     print(np.shape(litt_extrap_sol_param_red))
#     print(np.shape(param_out))
#
#     # create stack
#     ll_stack, param_stack = [], []
#     # wavelength solution for n_ord_start - n_ord_final
#     if len(ll_out) > 0:
#         ll_stack.append(ll_out)
#         param_stack.append(param_out)
#     # add extrapolation from littrow to orders > n_ord_final
#     if len(litt_extrap_sol_red) > 0:
#         ll_stack.append(litt_extrap_sol_red)
#         param_stack.append(litt_extrap_sol_param_red)
#
#     # convert stacks to arrays and add to storage
#     loc['LL_OUT_2'] = np.vstack(ll_stack)
#     loc['LL_PARAM_2'] = np.vstack(param_stack)
#     loc.set_sources(['LL_OUT_2', 'LL_PARAM_2'], __NAME__ + '/main()')
#
#     # rename for compatibility
#     loc['LITTROW_EXTRAP_SOL_1'] = np.vstack(ll_stack)
#     loc['LITTROW_EXTRAP_PARAM_1'] = np.vstack(param_stack)
#
#     # temp copy for storage
#     loc['LL_FINAL'] = np.vstack(ll_stack)
#     loc['LL_PARAM_FINAL'] = np.vstack(param_stack)
#     all_lines_final = np.copy(all_lines_2)
#     loc['ALL_LINES_FINAL'] = all_lines_final
#     loc.set_sources(['LL_FINAL', 'LL_PARAM_FINAL'], __NAME__ + '/main()')
#
#     # ------------------------------------------------------------------
#     # Incorporate FP into solution
#     # ------------------------------------------------------------------
#
#     use_fp = True
#
#     if use_fp:
#         # ------------------------------------------------------------------
#         # Find FP lines
#         # ------------------------------------------------------------------
#         # print message to screen
#         wmsg = 'Identification of lines in reference file: {0}'
#         WLOG('', p['LOG_OPT'], wmsg.format(fpfile))
#
#         # ------------------------------------------------------------------
#         # Get the FP solution
#         # ------------------------------------------------------------------
#
#         loc = spirouTHORCA.FPWaveSolutionNew(p, loc)
#
#         # ------------------------------------------------------------------
#         # FP solution plots
#         # ------------------------------------------------------------------
#         if p['DRS_PLOT']:
#             # Plot the FP extracted spectrum against wavelength solution
#             sPlt.wave_plot_final_fp_order(p, loc, iteration=2)
#             # Plot the measured FP cavity width offset against line number
#             sPlt.wave_local_width_offset_plot(loc)
#             # Plot the FP line wavelength residuals
#             sPlt.wave_fp_wavelength_residuals(loc)
#
#     # ------------------------------------------------------------------
#     # Create new wavelength solution
#     # ------------------------------------------------------------------
#
#     start = min(p['IC_HC_N_ORD_START_2'], p['IC_FP_N_ORD_START'])
#     end = max(p['IC_HC_N_ORD_FINAL_2'], p['IC_FP_N_ORD_FINAL'])
#
#     # recalculate echelle orders for Fit1DSolution
#     o_orders = np.arange(start,end)
#     echelle_order = p['IC_HC_T_ORDER_START'] - o_orders
#     loc['ECHELLE_ORDERS'] = echelle_order
#     loc.set_source('ECHELLE_ORDERS', __NAME__ + '/main()')
#
#
#     # select the orders to fit
#     ll = loc['LITTROW_EXTRAP_SOL_1'][start:end]
#     loc = spirouTHORCA.Fit1DSolution(p, loc, ll,  iteration=2)
#
#     # ------------------------------------------------------------------
#     # Calculate uncertainties
#     # ------------------------------------------------------------------
#
#     # # First solution (without smoothing)
#     # mean1 = np.mean(res_1)
#     # var1 = np.var(res_1)
#     # num_lines = len(res_1)
#     #
#     # # Second soluthion (with smoothing) if applicable
#     # if poly_smooth:
#     #     mean1 = np.mean(res_2)
#     #     var1 = np.var(res_2)
#     #     num_lines = len(res_2)
#     #
#     # # print statistics
#     # wmsg1 = 'On fiber {0} fit line statistic:'.format(p['FIBER'])
#     # wargs2 = [mean1*1000., np.sqrt(var1)*1000., num_lines, 1000.*np.sqrt(var1/num_lines)]
#     # wmsg2 = ('\tmean={0:.3f}[m/s] rms={1:.1f} {2} lines (error on mean '
#     #              'value:{3:.2f}[m/s])'.format(*wargs2))
#     # WLOG('info', p['LOG_OPT'] + p['FIBER'], [wmsg1, wmsg2])
#     #
#     # # Save to loc for later use - names given for coherence with cal_HC
#     # loc['X_MEAN_1'] = mean1
#     # loc['X_VAR_1'] = var1
#     # loc['X_ITER_1'] = num_lines
#
#     # ------------------------------------------------------------------
#     # Repeat Littrow test
#     # ------------------------------------------------------------------
#
#     # Reset the cut points
#     p['IC_LITTROW_CUT_STEP_2'] = 500
#
#     # reset Littrow fit degree
#     p['IC_LITTROW_FIT_DEG_2'] = 8
#
#
#     # Do Littrow check
#     ckwargs = dict(ll=loc['LL_OUT_2'][start:end, :], iteration=2, log=True)
#     loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)
#
#     # Plot wave solution littrow check
#     if p['DRS_PLOT']:
#         # plot littrow x pixels against fitted wavelength solution
#         sPlt.wave_littrow_check_plot(p, loc, iteration=2)
#
#
#     # ------------------------------------------------------------------
#     # Plot single order, wavelength-calibrated, with found lines
#     # ------------------------------------------------------------------
#
#     # set order to plot
#     plot_order = 7
#     # get the correct order to plot for all_lines (which is sized n_ord_final-n_ord_start)
#     plot_order_line = plot_order - n_ord_start
#     plt.figure()
#     # plot order and flux
#     plt.plot(wave_map2[plot_order], hcdata[plot_order], label='HC spectrum - order '
#                                                                 + str(plot_order))
#     # plot found lines
#     # first line separate for labelling purposes
#     plt.vlines(all_lines_1[plot_order_line][0][0], 0, all_lines_1[plot_order_line][0][2],
#                'm', label='fitted lines')
#     # plot lines to the top of the figure
#     plt.vlines(all_lines_1[plot_order_line][0][0], 0, np.max(hcdata[plot_order]), 'gray',
#                linestyles='dotted')
#     # rest of lines
#     for i in range(1, len(all_lines_1[plot_order_line])):
#         # plot lines to their corresponding amplitude
#         plt.vlines(all_lines_1[plot_order_line][i][0], 0, all_lines_1[plot_order_line][i][2],
#                    'm')
#         # plot lines to the top of the figure
#         plt.vlines(all_lines_1[plot_order_line][i][0], 0, np.max(hcdata[plot_order]), 'gray',
#                    linestyles='dotted')
#     plt.legend()
#     plt.xlabel('Wavelength')
#     plt.ylabel('Flux')
#
#     # ----------------------------------------------------------------------
#     # Quality control
#     # ----------------------------------------------------------------------
#     # get parameters ffrom p
#     p['QC_RMS_LITTROW_MAX'] = p['QC_HC_RMS_LITTROW_MAX']
#     p['QC_DEV_LITTROW_MAX'] = p['QC_HC_DEV_LITTROW_MAX']
#     # set passed variable and fail message list
#     passed, fail_msg = True, []
#     # check for infinites and NaNs in mean residuals from fit
#     if ~np.isfinite(loc['X_MEAN_2']):
#         # add failed message to the fail message list
#         fmsg = 'NaN or Inf in X_MEAN_2'
#         fail_msg.append(fmsg)
#         passed = False
#     # iterate through Littrow test cut values
#     # if smoothing done need to use Littrow 2, otherwise 1
#     if poly_smooth:
#         lit_it = 2
#     else:
#         lit_it = 2
#     # for x_it in range(len(loc['X_CUT_POINTS_lit_it'])):
#     # checks every other value
#     for x_it in range(1, len(loc['X_CUT_POINTS_'+str(lit_it)]), 4):
#         # get x cut point
#         x_cut_point = loc['X_CUT_POINTS_'+str(lit_it)][x_it]
#         # get the sigma for this cut point
#         sig_littrow = loc['LITTROW_SIG_'+str(lit_it)][x_it]
#         # get the abs min and max dev littrow values
#         min_littrow = abs(loc['LITTROW_MINDEV_'+str(lit_it)][x_it])
#         max_littrow = abs(loc['LITTROW_MAXDEV_'+str(lit_it)][x_it])
#         # check if sig littrow is above maximum
#         rms_littrow_max = p['QC_RMS_LITTROW_MAX']
#         dev_littrow_max = p['QC_DEV_LITTROW_MAX']
#         if sig_littrow > rms_littrow_max:
#             fmsg = ('Littrow test (x={0}) failed (sig littrow = '
#                     '{1:.2f} > {2:.2f})')
#             fargs = [x_cut_point, sig_littrow, rms_littrow_max]
#             fail_msg.append(fmsg.format(*fargs))
#             passed = False
#         # check if min/max littrow is out of bounds
#         if np.max([max_littrow, min_littrow]) > dev_littrow_max:
#             fmsg = ('Littrow test (x={0}) failed (min|max dev = '
#                     '{1:.2f}|{2:.2f} > {3:.2f})')
#             fargs = [x_cut_point, min_littrow, max_littrow, dev_littrow_max]
#             fail_msg.append(fmsg.format(*fargs))
#             passed = False
#     # finally log the failed messages and set QC = 1 if we pass the
#     # quality control QC = 0 if we fail quality control
#     if passed:
#         WLOG('info', p['LOG_OPT'],
#              'QUALITY CONTROL SUCCESSFUL - Well Done -')
#         p['QC'] = 1
#         p.set_source('QC', __NAME__ + '/main()')
#     else:
#         for farg in fail_msg:
#             wmsg = 'QUALITY CONTROL FAILED: {0}'
#             WLOG('warning', p['LOG_OPT'], wmsg.format(farg))
#         p['QC'] = 0
#         p.set_source('QC', __NAME__ + '/main()')
#
#     # ------------------------------------------------------------------
#     # archive result in e2ds spectra
#     # ------------------------------------------------------------------
#
#     # get wave filename
#     wavefits = spirouConfig.Constants.WAVE_FILE_EA(p)
#     wavefitsname = os.path.split(wavefits)[-1]
#
#     # log progress
#     wargs = [p['FIBER'], wavefits]
#     wmsg = 'Write wavelength solution for Fiber {0} in {1}'
#     WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
#     # write solution to fitsfilename header
#     # copy original keys
#     hdict = spirouImage.CopyOriginalKeys(loc['HCHDR'], loc['HCCDR'])
#     # add version number
#     hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
#     # add quality control
#     hdict = spirouImage.AddKey(hdict, p['KW_DRS_QC'], value=p['QC'])
#     # add number of orders
#     hdict = spirouImage.AddKey(hdict, p['KW_WAVE_ORD_N'],
#                                value=loc['LL_PARAM_FINAL'].shape[0])
#     # add degree of fit
#     hdict = spirouImage.AddKey(hdict, p['KW_WAVE_LL_DEG'],
#                                value=loc['LL_PARAM_FINAL'].shape[1]-1)
#     # add wave solution
#     hdict = spirouImage.AddKey2DList(hdict, p['KW_WAVE_PARAM'],
#                                      values=loc['LL_PARAM_FINAL'])
#     # write original E2DS file and add header keys (via hdict)
#     # spirouImage.WriteImage(p['FITSFILENAME'], loc['HCDATA'], hdict)
#
#     # write the wave "spectrum"
#     spirouImage.WriteImage(wavefits, loc['LL_FINAL'], hdict)
#
#     # get filename for E2DS calibDB copy of FITSFILENAME
#     e2dscopy_filename = spirouConfig.Constants.WAVE_E2DS_COPY(p)
#
#     wargs = [p['FIBER'], os.path.split(e2dscopy_filename)[-1]]
#     wmsg = 'Write reference E2DS spectra for Fiber {0} in {1}'
#     WLOG('', p['LOG_OPT'], wmsg.format(*wargs))
#
#     # make a copy of the E2DS file for the calibBD
#     spirouImage.WriteImage(e2dscopy_filename, loc['HCDATA'], hdict)
#
#     # ------------------------------------------------------------------
#     # Save to result table
#     # ------------------------------------------------------------------
#     # calculate stats for table
#     final_mean = 1000 * loc['X_MEAN_2']
#     final_var = 1000 * loc['X_VAR_2']
#     num_lines = int(np.sum(loc['X_ITER_2'][:, 2]))        #loc['X_ITER_2']
#     err = 1000 * np.sqrt(loc['X_VAR_2']/num_lines)
#     sig_littrow = 1000 * np.array(loc['LITTROW_SIG_'+str(lit_it)])
#     # construct filename
#     wavetbl = spirouConfig.Constants.WAVE_TBL_FILE_EA(p)
#     wavetblname = os.path.split(wavetbl)[-1]
#     # construct and write table
#     columnnames = ['night_name', 'file_name', 'fiber', 'mean', 'rms',
#                    'N_lines', 'err', 'rms_L500', 'rms_L1000', 'rms_L1500',
#                     'rms_L2000', 'rms_L2500', 'rms_L3000', 'rms_L3500']
#     columnformats = ['{:20s}', '{:30s}', '{:3s}', '{:7.4f}', '{:6.2f}',
#                      '{:3d}', '{:6.3f}', '{:6.2f}', '{:6.2f}', '{:6.2f}',
#                      '{:6.2f}', '{:6.2f}', '{:6.2f}', '{:6.2f}']
#     columnvalues = [[p['ARG_NIGHT_NAME']], [p['ARG_FILE_NAMES'][0]],
#                     [p['FIBER']], [final_mean], [final_var],
#                     [num_lines], [err], [sig_littrow[0]],
#                     [sig_littrow[1]], [sig_littrow[2]], [sig_littrow[3]],
#                     [sig_littrow[4]], [sig_littrow[5]], [sig_littrow[6]]]
#     # make table
#     table = spirouImage.MakeTable(columns=columnnames, values=columnvalues,
#                                   formats=columnformats)
#     # merge table
#     wmsg = 'Global result summary saved in {0}'
#     WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(wavetblname))
#     spirouImage.MergeTable(table, wavetbl, fmt='ascii.rst')
#
#     # ------------------------------------------------------------------
#     # Save line list table file
#     # ------------------------------------------------------------------
#     # construct filename
#
#     # TODO proper column values
#
#     wavelltbl = spirouConfig.Constants.WAVE_LINE_FILE_EA(p)
#     wavelltblname = os.path.split(wavelltbl)[-1]
#     # construct and write table
#     columnnames = ['order', 'll', 'dv', 'w', 'xi', 'xo', 'dvdx']
#     columnformats = ['{:.0f}', '{:12.4f}', '{:13.5f}', '{:12.4f}',
#                      '{:12.4f}', '{:12.4f}', '{:8.4f}']
#     columnvalues = []
#     # construct column values (flatten over orders)
#     for it in range(n_ord_start, n_ord_final):
#         gg = (ord_save == it)
#         for jt in range(len(loc['ALL_LINES_FINAL'][it])):
#              row = [float(it), loc['ALL_LINES_FINAL'][it][jt][0],
#                     res_1[gg][jt],
#                     loc['ALL_LINES_FINAL'][it][jt][7],
#                     loc['ALL_LINES_FINAL'][it][jt][5],
#                     loc['ALL_LINES_FINAL'][it][jt][5],
#                     res_1[gg][jt]]
#              columnvalues.append(row)
#
#     # log saving
#     wmsg = 'List of lines used saved in {0}'
#     WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg.format(wavelltblname))
#
#     # make table
#     columnvalues = np.array(columnvalues).T
#     table = spirouImage.MakeTable(columns=columnnames, values=columnvalues,
#                                   formats=columnformats)
#     # write table
#     spirouImage.WriteTable(table, wavelltbl, fmt='ascii.rst')
#
#     # ------------------------------------------------------------------
#     # Move to calibDB and update calibDB
#     # ------------------------------------------------------------------
#     if p['QC']:
#         # set the wave key
#         keydb = 'WAVE_{0}'.format(p['FIBER'])
#         # copy wave file to calibDB folder
#         spirouDB.PutCalibFile(p, wavefits)
#         # update the master calib DB file with new key
#         spirouDB.UpdateCalibMaster(p, keydb, wavefitsname, loc['HCHDR'])
#
#         # set the hcref key
#         keydb = 'HCREF_{0}'.format(p['FIBER'])
#         # copy wave file to calibDB folder
#         spirouDB.PutCalibFile(p, e2dscopy_filename)
#         # update the master calib DB file with new key
#         e2dscopyfits = os.path.split(e2dscopy_filename)[-1]
#         spirouDB.UpdateCalibMaster(p, keydb, e2dscopyfits, loc['HCHDR'])

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
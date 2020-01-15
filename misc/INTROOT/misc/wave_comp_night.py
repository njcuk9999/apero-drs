#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_WAVE_NEW_E2DS_spirou.py [night_directory] [HCfitsfilename] [FPfitsfilename]

Wavelength calibration incorporating the FP lines
Following C. Lovis's method for Espresso

Created on 2018-06-08 at 16:00

@author: mhobson
"""
from __future__ import division
import matplotlib.cm as cm

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA
from SpirouDRS.spirouTHORCA import spirouWAVE

from astropy import constants as cc
from astropy import units as uu

from astropy.io import fits
from astropy.table import Table
import numpy as np
import matplotlib.pyplot as plt
import os

# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.m / uu.s).value

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_WAVE_NEW_E2DS_spirou.py'
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
def main():
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p)
    p['FIBER'] = 'AB'

    # read data - TODO generalize

    datadir = '/data/CFHT/reduced/TEST/TESTWAVE/'
    wave1, waveheader1 = fits.getdata(datadir +
                                      '2018-09-24/2018-09-24_2305552a_pp_2305570c_pp_wave_new_C.fits',
                                      header=True)
    wave2, waveheader2 = fits.getdata(datadir +
                                      '2018-09-25/2018-09-25_2305960a_pp_2305967c_pp_wave_new_C.fits',
                                      header=True)
    wave1, waveheader1 = fits.getdata('/home/data/CFHT/reduced/19AQ02-Feb24/19AQ02-Feb24_2375831a_pp_2375835c_pp_wave_new_AB.fits', header=True)
    wave2, waveheader2 = fits.getdata('/home/data/CFHT/reduced/19AQ02-Feb25/19AQ02-Feb25_2376092a_pp_2376096c_pp_wave_new_AB.fits', header=True)

    # wave3, waveheader3 = fits.getdata(datadir +
    #                                   '2018-09-24/2018-09-24_2305552a_pp_2305570c_pp_wave_new_AB.fits',
    #                                   header=True)
    # wave4, waveheader4 = fits.getdata(datadir +
    #                                   '2018-09-25/2018-09-25_2305960a_pp_2305967c_pp_wave_new_AB.fits',
    #                                   header=True)
    wave3, waveheader3 = fits.getdata(datadir +
                                      'comp_Et/comp_Et_2329931a_pp_2329986c_pp_wave_new_AB.fits',
                                      header=True)
    wave4, waveheader4 = fits.getdata(datadir +
                                      'comp_Et/comp_Et_2329713a_pp_2329824c_pp_wave_new_AB.fits',
                                      header=True)

    # read a blaze - TODO read correct one, but they're all similar

    blaze = fits.getdata(datadir +'comp_Et/2018-10-26_20181026-004433_flat_flat_002f_pp_blaze_AB.fits')
    for iord in range(49):
        blaze[iord, :] /= np.nanpercentile(blaze[iord, :], 90)

    wave1[blaze < 0.5] = np.nan
    wave2[blaze < 0.5] = np.nan
    wave3[blaze < 0.5] = np.nan
    wave4[blaze < 0.5] = np.nan

    wavediffC = wave1 - wave2
    wavediffAB = wave3 - wave4

    rvdiffC = speed_of_light*wavediffC/wave1
    rvdiffAB = speed_of_light*wavediffAB/wave3

    print('rms C = ', np.nanmedian(np.abs(rvdiffC - np.nanmedian(rvdiffC))), 'm/s')
    print('rms AB = ', np.nanmedian(np.abs(rvdiffAB - np.nanmedian(rvdiffAB))), 'm/s')

    g = (wave1 > 1500) & (wave1 < 1800)

    print('rms C 1.5-1.8= ', np.nanmedian(np.abs(rvdiffC[g] - np.nanmedian(rvdiffC[g]))), 'm/s')
    print('rms AB 1.5-1.8 = ', np.nanmedian(np.abs(rvdiffAB[g] - np.nanmedian(rvdiffAB[g]))), 'm/s')



    plt.figure()
    for ord in range(len(wave1)):
        plt.plot(wave1[ord], rvdiffC[ord])

    plt.figure()
    for ord in range(len(wave3)):
        plt.plot(wave3[ord], rvdiffAB[ord])

    # wave1, waveheader1 = fits.getdata(datadir+'2018-09-21/2018-09-21_2305103a_pp_2305110c_pp_wave_ea_AB.fits', header=True)
    # fp1, header1 = fits.getdata(datadir+'2018-09-21/2305103a_pp_e2dsff_AB.fits', header=True)
    #
    # wave2, waveheader2 = fits.getdata(datadir+'2018-09-22/2018-09-22_2305301a_pp_2305308c_pp_wave_ea_AB.fits', header=True)
    # fp2, header2 = fits.getdata(datadir+'2018-09-22/2305301a_pp_e2dsff_AB.fits', header=True)
    #
    # wave3 = fits.getdata(datadir+'2018-09-23/2018-09-23_2305491a_pp_2305498c_pp_wave_ea_AB.fits')
    # fp3, header3 = fits.getdata(datadir+'2018-09-23/2305491a_pp_e2dsff_AB.fits', header=True)
    #
    # wave4 = fits.getdata(datadir+'2018-09-24/2018-09-24_2305552a_pp_2305570c_pp_wave_ea_AB.fits')
    # fp4, header4 = fits.getdata(datadir+'2018-09-24/2305552a_pp_e2dsff_AB.fits', header=True)
    #
    # wave5 = fits.getdata(datadir+'2018-09-25/2018-09-25_2305960a_pp_2305967c_pp_wave_ea_AB.fits')
    # fp5, header5 = fits.getdata(datadir+'2018-09-25/2305960a_pp_e2dsff_AB.fits', header=True)
    #
    # # add data and hdr to loc
    # loc = ParamDict()
    #
    # # plot superimposed - TODO generalize
    #
    # limits = [[1005.0, 1006.0], [1742.0, 1744.0], [2413.0, 2415.5]]
    #
    # fig, frames = plt.subplots(len(limits), 1)
    #
    # for it, limit in enumerate(limits):
    #
    #     for order_num in range(fp1.shape[0]):
    #
    #         x1 = wave1[order_num]
    #         y1 = fp1[order_num]
    #         # sort1 = np.argsort(x1)
    #         # x1, y1 = x1[sort1], y1[sort1]
    #         mask1 = (x1 >= limit[0]) & (x1 <= limit[1])
    #
    #         x2 = wave2[order_num]
    #         y2 = fp2[order_num]
    #         # sort2 = np.argsort(x2)
    #         # x2, y2 = x2[sort2], y2[sort2]
    #         mask2 = (x2 >= limit[0]) & (x2 <= limit[1])
    #
    #         x3 = wave3[order_num]
    #         y3 = fp3[order_num]
    #         mask3 = (x3 >= limit[0]) & (x3 <= limit[1])
    #
    #         x4 = wave4[order_num]
    #         y4 = fp4[order_num]
    #         mask4 = (x4 >= limit[0]) & (x4 <= limit[1])
    #
    #         x5 = wave5[order_num]
    #         y5 = fp5[order_num]
    #         mask5 = (x5 >= limit[0]) & (x5 <= limit[1])
    #
    #         if (np.sum(mask1) == 0) or (np.sum(mask2) == 0):
    #             continue
    #
    #         #		args1 = [file1.split('_')[0], date1, order_num]
    #         #		args2 = [file2.split('_')[0], date2, order_num]
    #
    #         label1 = '2018-09-21 - Order {0}'.format(order_num)
    #         label2 = '2018-09-22 - Order {0}'.format(order_num)
    #         label3 = '2018-09-23 - Order {0}'.format(order_num)
    #         label4 = '2018-09-24 - Order {0}'.format(order_num)
    #         label5 = '2018-09-25 - Order {0}'.format(order_num)
    #
    #         frames[it].plot(x1[mask1], y1[mask1] / np.nanmedian(y1[mask1]),
    #                         label=label1)
    #         frames[it].plot(x2[mask2], y2[mask2] / np.nanmedian(y2[mask2]),
    #                         label=label2)
    #         frames[it].plot(x3[mask3], y3[mask3] / np.nanmedian(y3[mask3]),
    #                         label=label3)
    #         frames[it].plot(x4[mask4], y4[mask4] / np.nanmedian(y4[mask4]),
    #                         label=label4)
    #         frames[it].plot(x5[mask5], y5[mask5] / np.nanmedian(y5[mask5]),
    #                         label=label5)
    #
    #         frames[it].set(xlabel='Wavelength', ylabel='norm flux')
    #         frames[it].legend(loc=6, bbox_to_anchor=(1.01, 0.5))
    #
    # # ----------------------------------------------------------------------
    # # Read wave solution per file - TODO generalize
    # # ----------------------------------------------------------------------
    # # wavelength file; we will use the polynomial terms in its header,
    # # NOT the pixel values that would need to be interpolated
    #
    # # set source of wave file
    # wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    # # Force A and B to AB solution
    # if p['FIBER'] in ['A', 'B']:
    #     wave_fiber = 'AB'
    # else:
    #     wave_fiber = p['FIBER']
    # tmp_wave_file = '/home/data/CFHT/calibDB_1/' + header1['WAVEFILE']
    # wout = spirouImage.GetWaveSolution(p, hdr=header1,
    #                                    filename=tmp_wave_file,
    #                                    return_wavemap=True,
    #                                    return_filename=True, fiber=wave_fiber)
    # loc['WAVEPARAMS'], loc['WAVE_INIT'], loc['WAVEFILE'] = wout
    # loc.set_sources(['WAVE_INIT', 'WAVEFILE', 'WAVEPARAMS'], wsource)
    # poly_wave_sol_1 = loc['WAVEPARAMS']
    #
    # # ----------------------------------------------------------------------
    # # Check that wave parameters are consistent with "ic_ll_degr_fit"
    # # ----------------------------------------------------------------------
    # loc = spirouImage.CheckWaveSolConsistency(p, loc)
    #
    # # ----------------------------------------------------------------------
    # # Find FP peaks and get wavelengths
    # # ----------------------------------------------------------------------
    # # setup for find_fp_lines_new_setup (to be compatible w/ wave_EA)
    # # set wavelength solution
    # # loc['LITTROW_EXTRAP_SOL_1'] = loc['WAVE_INIT']
    # # # set data
    # # loc['FPDATA'] = fp1
    # #
    # # # get FP peaks
    # # loc = spirouTHORCA.FindFPLinesNew(p, loc)
    # # xpeaks1 = np.array(loc['XPEAK'])
    # # ordpeaks1 = np.array(loc['ORDPEAK'])
    # waveparam1 = np.array(loc['WAVEPARAMS'])
    # #
    #
    # #repeat for 2 - TODO generalize
    #
    # tmp_wave_file = '/home/data/CFHT/calibDB_1/' + header2['WAVEFILE']
    # wout = spirouImage.GetWaveSolution(p, hdr=header2,
    #                                    filename=tmp_wave_file,
    #                                    return_wavemap=True,
    #                                    return_filename=True, fiber=wave_fiber)
    # loc['WAVEPARAMS'], loc['WAVE_INIT'], loc['WAVEFILE'] = wout
    # loc.set_sources(['WAVE_INIT', 'WAVEFILE', 'WAVEPARAMS'], wsource)
    # poly_wave_sol_2 = loc['WAVEPARAMS']
    #
    # # ----------------------------------------------------------------------
    # # Check that wave parameters are consistent with "ic_ll_degr_fit"
    # # ----------------------------------------------------------------------
    # # loc = spirouImage.CheckWaveSolConsistency(p, loc)
    #
    # # ----------------------------------------------------------------------
    # # Find FP peaks and get wavelengths
    # # ----------------------------------------------------------------------
    # # setup for find_fp_lines_new_setup (to be compatible w/ wave_EA)
    # # set wavelength solution
    # # loc['LITTROW_EXTRAP_SOL_1'] = loc['WAVE_INIT']
    # # # set data
    # # loc['FPDATA'] = fp2
    # #
    # # # get FP peaks
    # # loc = spirouTHORCA.FindFPLinesNew(p, loc)
    # # xpeaks2 = np.array(loc['XPEAK'])
    # # ordpeaks2 = np.array(loc['ORDPEAK'])
    # waveparam2 = np.array(loc['WAVEPARAMS'])
    # #
    # # wavediff = []
    # # rvdiff = []
    # # #get peak diffs
    # # for order in range(49):
    # #     print('processing order '+str(order))
    # #     order_mask1 = ordpeaks1 == order
    # #     xpeaks1_ord = xpeaks1[order_mask1]
    # #     wave1_ord = np.polyval(waveparam1[order][::-1], xpeaks1_ord)
    # #     order_mask2 = ordpeaks2 == order
    # #     xpeaks2_ord = xpeaks2[order_mask2]
    # #     wave2_ord = np.polyval(waveparam2[order][::-1], xpeaks2_ord)
    # #     for peak1 in range(len(xpeaks1_ord)):
    # #         for peak2 in range(len(xpeaks2_ord)):
    # #             if abs(xpeaks2_ord[peak2] - xpeaks1_ord[peak1]) < 3:
    # #                 wavediff.append(wave2_ord[peak2] - wave1_ord[peak1])
    # #                 rvdiff.append((wave2_ord[peak2] - wave1_ord[peak1])
    # #                               *speed_of_light/wave1_ord[peak1])
    # #
    #
    # ########################################################################
    # # ----------------------------------------------------------------------
    # # Comparing HC peaks
    # # ----------------------------------------------------------------------
    #
    # # Get linelist name
    # wavellext = '_linelist.dat'
    #
    # wavellfn1 = waveheader1['HCFILE'].replace('.fits', wavellext)
    # wavellfile1 = os.path.join(datadir, '2018-09-21', wavellfn1)
    #
    # wavellfn2 = waveheader2['HCFILE'].replace('.fits', wavellext)
    # wavellfile2 = os.path.join(datadir, '2018-09-22', wavellfn2)
    #
    # print(wavellfile1, wavellfile2)
    #
    # # read tables
    # hc_lines_1 = Table.read(wavellfile1, format='ascii.rst')
    # hc_lines_2 = Table.read(wavellfile2, format='ascii.rst')
    #
    # # initialise saving vectors
    # hc_ll_match_1 = []
    # hc_ll_match_2 = []
    # hc_x_match_1 = []
    # hc_x_match_2 = []
    # order_match = []
    #
    # for order in range(49):
    #     # get x and ll values for order, for file 1
    #     ord_mask_1 = hc_lines_1['ORD_INI'] == order
    #     ord_x_1 = hc_lines_1['XGAU_INI'][ord_mask_1]
    #     ord_ll_1 = np.polyval(waveparam1[order][::-1], ord_x_1)
    #     # get x and ll values for order, for file 2
    #     ord_mask_2 = hc_lines_2['ORD_INI'] == order
    #     ord_x_2 = hc_lines_2['XGAU_INI'][ord_mask_2]
    #     ord_ll_2 = np.polyval(waveparam2[order][::-1], ord_x_2)
    #
    #     # wavelength match
    #     for i in range(len(ord_ll_1)):
    #         for j in range(len(ord_ll_2)):
    #             if abs(ord_ll_1[i] - ord_ll_2[j]) < 0.01:
    #                 hc_ll_match_1.append(ord_ll_1[i])
    #                 hc_ll_match_2.append(ord_ll_2[j])
    #                 hc_x_match_1.append(ord_x_1[i])
    #                 hc_x_match_2.append(ord_x_2[j])
    #                 order_match.append(order)
    #
    # # convert to arrays
    # hc_ll_match_1 = np.array(hc_ll_match_1)
    # hc_ll_match_2 = np.array(hc_ll_match_2)
    # hc_x_match_1 = np.array(hc_x_match_1)
    # hc_x_match_2 = np.array(hc_x_match_2)
    # order_match = np.array(order_match)
    #
    # #calculate rvs
    # rv = (hc_ll_match_2 - hc_ll_match_1)*speed_of_light/hc_ll_match_1
    #
    # # plot wavelength difference
    # # plot_order = [5,10,15,20,25,30,35,40,45]
    # #plot_order = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    # plot_order = np.arange(48)
    # colors = cm.rainbow(np.linspace(0, 1, len(plot_order)))
    #
    # plt.figure()
    # it = 0
    # for po in plot_order:
    #     plt.plot(hc_ll_match_1[order_match==po],
    #              hc_ll_match_2[order_match==po] - hc_ll_match_1[order_match==po],
    #              '.', color=colors[it])
    #     it += 1
    # plt.hlines(0, 950,2400)
    # plt.ylabel('Wavelength (nm)')
    #
    # # plot rv difference
    # plt.figure()
    # it = 0
    # for po in plot_order:
    #     plt.plot(hc_ll_match_1[order_match == po],
    #              rv[order_match == po],
    #              '.', color=colors[it])
    #     it += 1
    # plt.hlines(0, 950, 2400)
    # plt.ylabel('RV (km/s)')
    #
    # # plot x difference
    # plt.figure()
    # it = 0
    # for po in plot_order:
    #     fit = nanpolyfit(hc_x_match_1[order_match == po],
    #                      hc_x_match_2[order_match == po] - hc_x_match_1[order_match == po],
    #                      deg=2)
    #     # plt.plot(hc_x_match_1[order_match==po],
    #     #          hc_x_match_2[order_match==po] - hc_x_match_1[order_match==po],
    #     #          '.', color=colors[it])
    #     plt.plot(hc_x_match_1[order_match==po],
    #              np.polyval(fit, hc_x_match_1[order_match==po])+0.2*it,
    #              color=colors[it])
    #     plt.hlines(0+0.2*it,0,4000)
    #     it += 1
    # plt.ylabel('Pixel')
    #
    # rv_med_ord = []
    # rv_std_ord = []
    # # calculate per-order RV std dev
    # for po in plot_order:
    #     rv_med_ord.append(np.nanmedian(rv[order_match == po]))
    #     rv_std_ord.append(np.nanstd(rv[order_match == po]))
    #


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

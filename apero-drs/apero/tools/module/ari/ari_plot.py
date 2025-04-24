#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-23 at 10:56

@author: cook
"""
from typing import Any, Dict

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import ListedColormap
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy.time import Time

from aperocore import math as mp
from apero.plotting import gen_plot
from aperocore.constants import param_functions
from aperocore import drs_lang
from aperocore.core import drs_log
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.ari.ari_core.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# -----------------------------------------------------------------------------
# Get ParamDict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get the text types
textentry = drs_lang.textentry
# Set background color in plots
PLOT_BACKGROUND_COLOR = '#FEFDE1'


# =============================================================================
# Define classes
# =============================================================================
class DebugPlot:
    def __init__(self):
        self.name = None
        self.basename = None
        self.path = None
        self.plot = None
        self.description = None
        self.active = False


# =============================================================================
# Define functions
# =============================================================================
def spec_plot(spec_props: Dict[str, Any], plot_path: str, plot_title: str):
    # get parameters from props
    mjd = spec_props['mjd']
    ext_y = spec_props['EXT_Y']
    ext_h = spec_props['EXT_H']
    ext_y_label = spec_props['EXT_Y_LABEL']
    ext_h_label = spec_props['EXT_H_LABEL']
    wavemap = spec_props['WAVE']
    ext_spec = spec_props['EXT_SPEC']
    tcorr_spec = spec_props['TCORR_SPEC']
    wavemask0 = spec_props['WAVEMASK0']
    wavemask1 = spec_props['WAVEMASK1']
    wavemask2 = spec_props['WAVEMASK2']
    wavemask3 = spec_props['WAVEMASK3']
    max_file = spec_props['MAX_FILE']
    max_snr = spec_props['MAX_SNR']
    wavelim0 = spec_props['WAVELIM0']
    wavelim1 = spec_props['WAVELIM1']
    wavelim2 = spec_props['WAVELIM2']
    wavelim3 = spec_props['WAVELIM3']
    bjd_tcorr = Time(spec_props['BJD_TCORR'], format='jd')
    berv_tcorr = spec_props['BERV_TCORR']
    bjd_e2ds = Time(spec_props['BJD_E2DS'], format='jd')
    berv_e2ds = spec_props['BERV_E2DS']
    tcorr_fail = spec_props['TCORR_FAIL_MASK']
    e2ds_fail = spec_props['E2DS_FAIL_MASK']
    bjd_curve = Time(spec_props['BJD_CURVE'], format='jd')
    berv_curve = spec_props['BERV_CURVE']
    berv_cov = spec_props['BERV_COV']
    vsys = spec_props['VSYS']
    obs_days = spec_props['OBS_DAYS']
    obs_windows = spec_props['OBS_WINDOWS']
    # --------------------------------------------------------------------------
    # setup the figure
    plt.figure(figsize=(12, 16))
    frame0 = plt.subplot2grid((4, 3), (0, 0), colspan=3, rowspan=1)
    frame1 = plt.subplot2grid((4, 3), (1, 0), colspan=3, rowspan=1)
    frame2 = plt.subplot2grid((4, 3), (2, 0), colspan=3, rowspan=1)
    frame3a = plt.subplot2grid((4, 3), (3, 0), colspan=1, rowspan=1)
    frame3b = plt.subplot2grid((4, 3), (3, 1), colspan=1, rowspan=1)
    frame3c = plt.subplot2grid((4, 3), (3, 2), colspan=1, rowspan=1)

    # set background color
    frame0.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame1.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame2.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame3a.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame3b.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame3c.set_facecolor(PLOT_BACKGROUND_COLOR)
    # --------------------------------------------------------------------------
    # Top plot SNR Y
    # --------------------------------------------------------------------------
    # # plot the CCF RV points
    frame0.plot_date(mjd.plot_date, ext_y, fmt='.', alpha=0.5,
                     label=ext_y_label)
    frame0.plot_date(mjd.plot_date, ext_h, fmt='.', alpha=0.5,
                     label=ext_h_label)
    frame0.legend(loc=0, ncol=2)
    frame0.grid(which='both', color='lightgray', ls='--')
    frame0.set(xlabel='Date', ylabel='EXT SNR')
    # move the limits to match frame1 berv curve
    xmin0, _, _, _ = frame0.axis()
    xmax0 = np.max(Time(bjd_curve, format='mjd').plot_date)
    frame0.set(xlim=[xmin0, xmax0])
    # --------------------------------------------------------------------------
    # Middle plot - BERV coverage
    # --------------------------------------------------------------------------
    if vsys is None:
        ylabel = 'BERV [km/s]  [No LBL]'
        vsys_value = 0.0
    else:
        ylabel = r'$v_{tot}$ [km/s] = $v_{sys} - BERV$'
        vsys_value = float(vsys) / 1000
    # Plot different categories of data points
    frame1.plot_date(bjd_tcorr[~tcorr_fail].plot_date,
                     berv_tcorr[~tcorr_fail].value + vsys_value, fmt='o',
                     color='green', zorder=1, ls='None',
                     label='Passed all QC (PP to TCORR)', alpha=0.5)
    frame1.plot_date(bjd_e2ds[e2ds_fail].plot_date,
                     berv_e2ds[e2ds_fail].value + vsys_value,
                     fmt='x', color='blue', zorder=2, ms=10,
                     label='Failed QC (EXT)', ls='None')
    frame1.plot_date(bjd_tcorr[tcorr_fail].plot_date,
                     berv_tcorr[tcorr_fail].value + vsys_value,
                     fmt='x', color='red', ls='None', zorder=3, ms=10,
                     label='Failed QC (TCORR)')
    # Plot berv curve
    frame1.plot(Time(bjd_curve, format='mjd').plot_date,
                berv_curve + vsys_value,
                ls=':', color='gray', lw=2)
    # plot
    if vsys is not None:
        frame1.axhline(y=vsys_value,
                       label=r'$v_{sys}$ = ' + f'{vsys_value:.3f} [km/s]')

    frame1.set(xlim=[xmin0, xmax0])
    # get limits
    xmin, xmax, ymin, ymax = frame1.axis()
    # set the last value to the same as the second from last (boundary effect)
    obs_windows[-1] = bool(obs_windows[-1])
    # fill between observation windows
    # TODO: Fix the unobservable region
    # frame1.fill_between(obs_days, y1=ymin, y2=ymax,
    #                     where=np.invert(obs_windows), color='k', alpha=0.1,
    #                     label='Unobservable')
    # labels/axis/legend
    frame1.legend(loc=0, ncols=1, fontsize=8).set_zorder(10)
    frame1.set(xlabel='Date', ylabel=ylabel)
    frame1.set_title(f'BERV coverage = {berv_cov:.3f} km/s', fontsize=10)
    frame1.grid(which='both', color='lightgray', ls='--')
    frame1.set(xlim=[xmin, xmax], ylim=[ymin, ymax])
    # --------------------------------------------------------------------------
    # Middle plot - full spectra + tcorr
    # --------------------------------------------------------------------------
    title = (f'Spectrum closest to Median {ext_h_label}'
             f'     SNR:{max_snr}     File: {max_file}')

    frame2.plot(wavemap[wavemask0], ext_spec[wavemask0],
                color='k', label='Extracted Spectrum', lw=0.5)
    if tcorr_spec is not None:
        frame2.plot(wavemap[wavemask0], tcorr_spec[wavemask0],
                    color='r', label='Telluric Corrected', lw=0.5)
        frame2.set_ylim((0, 1.5 * np.nanpercentile(tcorr_spec, 99)))
    frame2.set(xlabel='Wavelength [nm]', ylabel='Flux', xlim=wavelim0)
    frame2.set_title(title, fontsize=10)
    frame2.legend(loc=0, ncol=2)
    frame2.grid(which='both', color='lightgray', ls='--')
    # --------------------------------------------------------------------------
    # Bottom plots - Y, J, H spectra + tcorr
    # --------------------------------------------------------------------------
    masks = [wavemask1, wavemask2, wavemask3]
    frames = [frame3a, frame3b, frame3c]
    limits = [wavelim1, wavelim2, wavelim3]
    # loop around masks and frames and plot the middle plots
    for it in range(len(masks)):
        frame, mask, wavelim = frames[it], masks[it], limits[it]
        frame.plot(wavemap[mask], ext_spec[mask],
                   color='k', label='Extracted Spectrum', lw=0.5)
        if tcorr_spec is not None:
            frame.plot(wavemap[mask], tcorr_spec[mask],
                       color='r', label='Telluric Corrected', lw=0.5)
            ymin_mask = 0.5 * np.nanpercentile(tcorr_spec[mask], 1)
            ymax_mask = 1.5 * np.nanpercentile(tcorr_spec[mask], 99)
            frame.set_ylim((ymin_mask, ymax_mask))
        if it == 0:
            frame.set_ylabel('Flux')
        frame.set(xlabel='Wavelength [nm]', xlim=wavelim)
        frame.set_title(f'Zoom {it + 1}', fontsize=10)
        frame.grid(which='both', color='lightgray', ls='--')

    # --------------------------------------------------------------------------
    # add title
    plt.suptitle(plot_title)
    plt.subplots_adjust(bottom=0.05, left=0.06, right=0.99, hspace=0.35,
                        top=0.95)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()


def lbl_plot(lbl_props: Dict[str, Any], plot_path: str,
             plot_title: str) -> Dict[str, Any]:
    # setup the figure
    fig, frame = plt.subplots(3, 1, figsize=(12, 9), sharex='all')
    # get parameters from props
    plot_date = lbl_props['plot_date']
    vrad = lbl_props['vrad']
    svrad = lbl_props['svrad']
    snr_h = lbl_props['snr_h']
    snr_h_label = lbl_props['SNR_H_LABEL']
    reset_mask = lbl_props['RESET_RV']
    vrad_dict = lbl_props['VRAD_DICT']
    svrad_dict = lbl_props['SVRAD_DICT']
    wavemap = lbl_props['wavemap']
    # sort data by date
    sort = np.argsort(plot_date)
    plot_date = plot_date[sort]
    vrad = vrad[sort]
    svrad = svrad[sort]
    snr_h = snr_h[sort]
    reset_mask = reset_mask[sort]
    for key in vrad_dict:
        vrad_dict[key] = vrad_dict[key][sort]
        svrad_dict[key] = svrad_dict[key][sort]
    # set background color
    frame[0].set_facecolor(PLOT_BACKGROUND_COLOR)
    frame[1].set_facecolor(PLOT_BACKGROUND_COLOR)
    frame[2].set_facecolor(PLOT_BACKGROUND_COLOR)
    # --------------------------------------------------------------------------
    # Top plot LBL RV
    # --------------------------------------------------------------------------
    # plot the points
    frame[0].plot_date(plot_date[~reset_mask], vrad[~reset_mask], fmt='.',
                       alpha=0.5, color='green', ls='None')
    frame[0].plot_date(plot_date[reset_mask], vrad[reset_mask], fmt='.',
                       alpha=0.5, color='purple', ls='None')
    # plot the error bars
    frame[0].errorbar(plot_date[~reset_mask], vrad[~reset_mask],
                      yerr=svrad[~reset_mask],
                      marker='o', alpha=0.5, color='green', ls='None',
                      label='Good')
    frame[0].errorbar(plot_date[reset_mask], vrad[reset_mask],
                      yerr=svrad[reset_mask],
                      marker='o', alpha=0.5, color='purple', ls='None',
                      label='Possibly bad (reset rv)')
    # find percentile cuts that will be expanded by 150% for the ylim
    pp = np.nanpercentile(vrad, [10, 90])
    diff = pp[1] - pp[0]
    central_val = np.nanmean(pp)
    # used for plotting but also for the flagging of outliers
    ylim = [central_val - 1.5 * diff, central_val + 1.5 * diff]
    # length of the arrow flagging outliers
    l_arrow = 0.05 * (ylim[1] - ylim[0])
    # store the bad points
    bad_points = []
    # set the arrow properties
    arrowprops = dict(arrowstyle='<-', linewidth=2, color='red')
    arrow = None
    # --------------------------------------------------------------------------
    # flag the low outliers
    low = vrad < ylim[0]
    # get the x and y values of the outliers to be looped over within
    # the arrow plotting
    xpoints = np.array(plot_date[low], dtype=float)
    # x_range = np.nanmax(plot_date) - np.nanmin(plot_date)
    for ix in range(len(xpoints)):
        bad_points.append(ix)
        arrow = frame[0].annotate('',
                                  xy=(xpoints[ix], ylim[0] + l_arrow),
                                  xytext=(xpoints[ix], ylim[0] - l_arrow * 2),
                                  xycoords='data', textcoords='data',
                                  arrowprops=arrowprops)

        # frame[0].arrow(xpoints[ix], ylim[0] + l_arrow * 2, 0, -l_arrow,
        #                color='red', head_width=0.01 * x_range,
        #                head_length=0.25 * l_arrow, alpha=0.5, label='Outliers')
    # same as above for the high outliers
    high = vrad > ylim[1]
    xpoints = np.array(plot_date[high], dtype=float)
    for ix in range(len(xpoints)):
        bad_points.append(ix)

        arrow = frame[0].annotate('',
                                  xy=(xpoints[ix], ylim[1] - l_arrow * 2),
                                  xytext=(xpoints[ix], ylim[1] + l_arrow),
                                  xycoords='data', textcoords='data',
                                  arrowprops=arrowprops)

        # frame[0].arrow(xpoints[ix], ylim[1] - l_arrow * 2, 0, l_arrow,
        #                color='red', head_width=0.01 * x_range,
        #                head_length=0.25 * l_arrow, alpha=0.5, label='Outliers')
    # --------------------------------------------------------------------------
    # setting the plot
    frame[0].set(ylim=ylim)
    frame[0].set(title=plot_title)
    frame[0].grid(which='both', color='lightgray', linestyle='--')
    frame[0].set(ylabel='Velocity [m/s]')
    # only keep one unique labels for legend
    handles, labels = [], []
    raw_handles, raw_labels = frame[0].get_legend_handles_labels()
    for it in range(len(raw_labels)):
        if raw_labels[it] not in labels:
            handles.append(raw_handles[it])
            labels.append(raw_labels[it])
    # --------------------------------------------------------------------------
    # Create a custom legend handle for the arrows
    if arrow is not None:
        arrow_handle = gen_plot.ArrowHandler()
        arrow_handle.arrowprops = arrowprops
        handler_map = {tuple: arrow_handle}
        handles.append((arrow,))
        labels.append('Outliers')
        # add legend
        frame[0].legend(handles, labels, loc=0, handler_map=handler_map)
    else:
        frame[0].legend(handles, labels, loc=0)
    # --------------------------------------------------------------------------
    # Bottom plot SNR
    # --------------------------------------------------------------------------
    # simple plot of the SNR in a sample order. You need to
    # update the relevant ketword for SPIRou
    frame[1].plot_date(plot_date[~reset_mask], snr_h[~reset_mask], fmt='.',
                       alpha=0.5, color='green', ls='None', label='Good')
    frame[1].plot_date(plot_date[reset_mask], snr_h[reset_mask], fmt='.',
                       alpha=0.5, color='purple', ls='None',
                       label='Possibly bad (reset rv)')
    # over plot the bad points from above
    if len(bad_points) > 0:
        bad_points = np.array(bad_points)
        frame[1].plot_date(plot_date[bad_points], snr_h[bad_points], fmt='.',
                           alpha=0.5, color='red', ls='None', label='Outliers')
    # add properties
    frame[1].grid(which='both', color='lightgray', linestyle='--')
    frame[1].set(ylabel=snr_h_label)
    # add legend
    frame[1].legend(loc=0)
    # --------------------------------------------------------------------------
    # frame 3: wavelength bin lbl rvs
    # --------------------------------------------------------------------------
    # Normalize the wavelength values for color mapping
    norm = plt.Normalize(vmin=min(wavemap), vmax=max(wavemap))
    # Get the 'coolwarm' colormap for plotting
    cmap = plt.get_cmap('coolwarm')
    # Calculate the median of the 'svrad' column, which represents the RV errors
    med_vrad_err = np.nanmedian(svrad)
    med = np.nanmedian(vrad)

    p5, p95 = np.nanpercentile(vrad, [5, 95])
    # frame 3: wave bin rv
    for ikey, key in enumerate(vrad_dict):
        # get the median error
        med_svrad = np.nanmedian(svrad_dict[key])
        # Skip the key if the median RV error is too high
        if med_svrad > (10 * med_vrad_err):
            continue
        # Skip the key if the median RV error is too low
        if med_svrad < med_vrad_err:
            continue
        # Get the color for the current wavelength
        color = cmap(norm(wavemap[ikey]))
        # Plot the RVs with error bars, using the calculated color
        frame[2].errorbar(plot_date, vrad_dict[key], yerr=svrad_dict[key],
                          label=key.replace('vrad_', ''),
                          alpha=0.5, fmt='.', color=color)
        # deal with p5 and p95 for limits
        p5_key, p95_key = np.nanpercentile(vrad_dict[key], [5, 95])
        # update limits if they have widened
        if p5_key < p5:
            p5 = p5_key
        if p95_key > p95:
            p95 = p95_key
    # Plot the overall 'vrad' with error bars as black dots
    frame[2].errorbar(plot_date, vrad, yerr=svrad, fmt='k.', label='vrad')
    # set the Date for all axis
    frame[2].set(xlabel='Date')
    frame[2].set(ylabel='RV [m/s]')
    frame[2].grid(which='both', color='lightgray', linestyle='--')
    frame[2].legend(ncol=5, fontsize='xx-small')
    # zoom in on the median
    frame[2].set(ylim=[p5 - (med - p5), p95 + (p95 - med)])
    # --------------------------------------------------------------------------
    plt.tight_layout()
    # --------------------------------------------------------------------------
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()
    # some parameters are required later save them in a dictionary
    lbl_props['low'] = low
    lbl_props['high'] = high
    lbl_props['ylim'] = ylim
    # return the props
    return lbl_props


def ccf_plot(ccf_props: Dict[str, Any], plot_path: str, plot_title: str):
    # get parameters from props
    mjd = ccf_props['mjd']
    vrad = ccf_props['dv']
    svrad = ccf_props['sdv']
    rv_vec = ccf_props['rv_vec']
    y1_1sig = ccf_props['y1_1sig']
    y2_1sig = ccf_props['y2_1sig']
    y1_2sig = ccf_props['y1_2sig']
    y2_2sig = ccf_props['y2_2sig']
    med_ccf = ccf_props['med_ccf']
    has_fit = ccf_props['has_fit']
    fit = ccf_props['fit']
    xlim = ccf_props['xlim']

    # sort data by mjd.plot_date
    sort = np.argsort(mjd.plot_date)
    mjd = mjd[sort]
    vrad = vrad[sort]
    svrad = svrad[sort]
    # ylim = ccf_props['ylim']
    # --------------------------------------------------------------------------
    # setup the figure
    fig, frame = plt.subplots(4, 1, figsize=(12, 12))
    # set background color
    frame[0].set_facecolor(PLOT_BACKGROUND_COLOR)
    frame[1].set_facecolor(PLOT_BACKGROUND_COLOR)
    frame[2].set_facecolor(PLOT_BACKGROUND_COLOR)
    frame[3].set_facecolor(PLOT_BACKGROUND_COLOR)
    # --------------------------------------------------------------------------
    # Top plot CCF RV
    # --------------------------------------------------------------------------
    # # plot the CCF RV points
    frame[0].plot_date(mjd.plot_date, vrad, fmt='.', alpha=0.5,
                       color='green', label='Good')
    # plot the CCF RV errors
    frame[0].errorbar(mjd.plot_date, vrad, yerr=svrad, fmt='o',
                      alpha=0.5, color='green')
    # find percentile cuts that will be expanded by 150% for the ylim
    pp = np.nanpercentile(vrad, [10, 90])
    diff = pp[1] - pp[0]
    central_val = np.nanmean(pp)
    # used for plotting but also for the flagging of outliers
    if diff == 0:
        ylim = [0, 1]
    else:
        ylim = [central_val - 1.5 * diff, central_val + 1.5 * diff]
    # length of the arrow flagging outliers
    l_arrow = 0.05 * (ylim[1] - ylim[0])
    # set the arrow properties
    arrowprops = dict(arrowstyle='<-', linewidth=2, color='red')
    arrow = None
    # --------------------------------------------------------------------------
    # flag the low outliers
    low = vrad < ylim[0]
    # get the x and y values of the outliers to be looped over within
    # the arrow plotting
    xpoints = np.array(mjd.plot_date[low], dtype=float)
    # x_range = np.nanmax(mjd.plot_date) - np.nanmin(mjd.plot_date)
    for ix in range(len(xpoints)):
        arrow = frame[0].annotate('',
                                  xy=(xpoints[ix], ylim[0] - l_arrow),
                                  xytext=(xpoints[ix], ylim[0] + l_arrow * 2),
                                  xycoords='data', textcoords='data',
                                  arrowprops=arrowprops)

        # frame[0].arrow(xpoints[ix], ylim[0] + l_arrow * 2, 0, -l_arrow,
        #                color='red', head_width=0.01 * x_range,
        #                head_length=0.25 * l_arrow, alpha=0.5, label='Outliers')
    # same as above for the high outliers
    high = vrad > ylim[1]
    xpoints = np.array(mjd.plot_date[high], dtype=float)
    for ix in range(len(xpoints)):
        arrow = frame[0].annotate('',
                                  xy=(xpoints[ix], ylim[1] - l_arrow * 2),
                                  xytext=(xpoints[ix], ylim[1] + l_arrow),
                                  xycoords='data', textcoords='data',
                                  arrowprops=arrowprops)

        # frame[0].arrow(xpoints[ix], ylim[1] - l_arrow * 2, 0, l_arrow,
        #                color='red', head_width=0.01 * x_range,
        #                head_length=0.25 * l_arrow, alpha=0.5, label='Outliers')
    # --------------------------------------------------------------------------
    # setting the plot
    frame[0].set(ylim=ylim)
    frame[0].grid(which='both', color='lightgray', ls='--')
    frame[0].set(xlabel='Date', ylabel='Velocity [m/s]')
    # only keep one unique labels for legend
    handles, labels = [], []
    raw_handles, raw_labels = frame[0].get_legend_handles_labels()
    for it in range(len(raw_labels)):
        if raw_labels[it] not in labels:
            handles.append(raw_handles[it])
            labels.append(raw_labels[it])
    # --------------------------------------------------------------------------
    # Create a custom legend handle for the arrows
    if arrow is not None:
        arrow_handle = gen_plot.ArrowHandler()
        arrow_handle.arrowprops = arrowprops
        handler_map = {tuple: arrow_handle}
        handles.append((arrow,))
        labels.append('Outliers')
        # add legend
        frame[0].legend(handles, labels, loc=0, handler_map=handler_map)
    else:
        frame[0].legend(handles, labels, loc=0)
    # --------------------------------------------------------------------------
    # Middle plot median CCF
    # --------------------------------------------------------------------------
    # mask by xlim
    limmask = (rv_vec > xlim[0]) & (rv_vec < xlim[1])

    frame[1].fill_between(rv_vec[limmask], y1_2sig[limmask], y2_2sig[limmask],
                          color='orange', alpha=0.4)
    frame[1].fill_between(rv_vec[limmask], y1_1sig[limmask], y2_1sig[limmask],
                          color='red', alpha=0.4)
    frame[1].plot(rv_vec[limmask], med_ccf[limmask], alpha=1.0, color='black')
    if has_fit:
        frame[1].plot(rv_vec[limmask], fit[limmask], alpha=0.8,
                      label='Gaussian fit', ls='--')
    frame[1].legend(loc=0)
    frame[1].set(xlabel='RV [km/s]',
                 ylabel='Normalized CCF')
    frame[1].grid(which='both', color='lightgray', ls='--')

    # --------------------------------------------------------------------------
    # Middle plot median CCF residuals
    # --------------------------------------------------------------------------
    if has_fit:
        frame[2].fill_between(rv_vec[limmask], y1_2sig[limmask] - fit[limmask],
                              y2_2sig[limmask] - fit[limmask], color='orange',
                              alpha=0.4, label=r'2-$\sigma$')
        frame[2].fill_between(rv_vec[limmask], y1_1sig[limmask] - fit[limmask],
                              y2_1sig[limmask] - fit[limmask], color='red',
                              alpha=0.4, label=r'1-$\sigma$')
        frame[2].plot(rv_vec[limmask], med_ccf[limmask] - fit[limmask],
                      alpha=0.8, label='Median residual')
        frame[2].legend(loc=0, ncol=3)
        frame[2].set(xlabel='RV [km/s]', ylabel='Residuals [to fit]')
    else:
        frame[2].text(0.5, 0.5, 'No fit to CCF possible',
                      horizontalalignment='center')
        frame[2].legend(loc=0, ncol=3)
        frame[2].set(xlim=[0, 1], ylim=[0, 1], xlabel='RV [km/s]',
                     ylabel='Residuals')
    frame[2].grid(which='both', color='lightgray', ls='--')
    # --------------------------------------------------------------------------
    # Bottom plot median CCF residuals
    # --------------------------------------------------------------------------
    if has_fit:
        frame[3].fill_between(rv_vec[limmask],
                              y1_2sig[limmask] - med_ccf[limmask],
                              y2_2sig[limmask] - med_ccf[limmask], color='orange',
                              alpha=0.4, label=r'2-$\sigma$')
        frame[3].fill_between(rv_vec[limmask],
                              y1_1sig[limmask] - med_ccf[limmask],
                              y2_1sig[limmask] - med_ccf[limmask], color='red',
                              alpha=0.4, label=r'1-$\sigma$')
        frame[3].plot(rv_vec[limmask], med_ccf[limmask] - med_ccf[limmask],
                      alpha=0.8, label='Median residual')
        frame[3].legend(loc=0, ncol=3)
        frame[3].set(xlabel='RV [km/s]', ylabel='Residuals [To Median]')
    else:
        frame[3].text(0.5, 0.5, 'No fit to CCF possible',
                      horizontalalignment='center')
        frame[3].legend(loc=0, ncol=3)
        frame[3].set(xlim=[0, 1], ylim=[0, 1], xlabel='RV [km/s]',
                     ylabel='Residuals [To Median]')
    frame[3].grid(which='both', color='lightgray', ls='--')
    # --------------------------------------------------------------------------
    # add title
    plt.suptitle(plot_title)
    plt.subplots_adjust(hspace=0.2, left=0.1, right=0.99, bottom=0.05,
                        top=0.95)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()

# =============================================================================
# Calibration plots
# =============================================================================
def shape_qc_plot_plot(calib_props: Dict[str, Any], plot_path: str,
                       plot_title: str):
    # get shape props
    shape_props = calib_props['SHAPEL']
    # get hdict and header yaml descriptions
    hdict = shape_props['HDICT']
    labels = shape_props['LABEL']
    # get mjd date
    mjd = Time(hdict['KW_MID_OBS_TIME'], format='mjd')
    # get dx, dy, A, B, C, d
    shape_dx = np.array(hdict['KW_SHAPE_DX'])
    shape_dy = np.array(hdict['KW_SHAPE_DY'])
    shape_a = 1 - np.array(hdict['KW_SHAPE_A'])
    shape_b = np.array(hdict['KW_SHAPE_B'])
    shape_c = np.array(hdict['KW_SHAPE_C'])
    shape_d = 1 - np.array(hdict['KW_SHAPE_D'])
    # --------------------------------------------------------------------------
    # setup the figure
    fig, frames = plt.subplots(nrows=6, ncols=1, figsize=(12, 12),
                               sharex='all')
    # set background color
    for frame in frames:
        frame.set_facecolor(PLOT_BACKGROUND_COLOR)
        frame.grid(which='both', color='lightgray', ls='--')
    # plot shape dx
    frames[0].plot_date(mjd.plot_date, shape_dx, fmt='.', alpha=0.5)
    frames[0].set(xlabel='Date', ylabel=labels['KW_SHAPE_DX'])
    frames[0].xaxis.set_ticks_position('top')
    frames[0].xaxis.set_label_position('top')
    # plot shape dy
    frames[1].plot_date(mjd.plot_date, shape_dy, fmt='.', alpha=0.5)
    frames[1].set(ylabel=labels['KW_SHAPE_DY'])
    # plot shape a
    frames[2].plot_date(mjd.plot_date, shape_a, fmt='.', alpha=0.5)
    frames[2].set(ylabel=labels['KW_SHAPE_A'])
    # plot shape b
    frames[3].plot_date(mjd.plot_date, shape_b, fmt='.', alpha=0.5)
    frames[3].set(ylabel=labels['KW_SHAPE_B'])
    # plot shape c
    frames[4].plot_date(mjd.plot_date, shape_c, fmt='.', alpha=0.5)
    frames[4].set(ylabel=labels['KW_SHAPE_C'])
    # plot shape d
    frames[5].plot_date(mjd.plot_date, shape_d, fmt='.', alpha=0.5)
    frames[5].set(xlabel='Date', ylabel=labels['KW_SHAPE_D'])
    # --------------------------------------------------------------------------
    # add title
    plt.suptitle(plot_title)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()


def calib_mjd_wfpdrift_plot(calib_props: Dict[str, Any], plot_path: str,
                            plot_title: str):

    wave_props = calib_props['WAVE_NIGHT']

    calib_mjd_plot('KW_WFP_DRIFT', wave_props, plot_title, plot_path)


def calib_mjd_wcav000_plot(calib_props: Dict[str, Any], plot_path: str,
                           plot_title: str):
    # get the wave night props
    wave_props = calib_props['WAVE_NIGHT']

    calib_mjd_plot('KW_CAVITY_WIDTH', wave_props, plot_title, plot_path)


def calib_mjd_wcent_plot(calib_props: Dict[str, Any], plot_path: str,
                         plot_title: str):
    # get the wave night props
    wave_props = calib_props['WAVE_NIGHT']
    # get hdict and label descriptions
    hdict = wave_props['HDICT']
    cal_orders = wave_props['OTHER']['ORDERS']
    # get the wave cents
    wave_cents = hdict['WAVE_CENT_X']
    # get mjd date
    mjdmid = Time(hdict['KW_MID_OBS_TIME'], format='mjd')
    mjdmid_diff = np.diff(mjdmid.mjd)
    # we need dv not wavelength
    dv = np.log(wave_cents / np.nanmedian(wave_cents, axis=0)) * cc.c.value
    # set up figure
    fig, frames = plt.subplots(nrows=2, ncols=1, figsize=(12, 8))
    # set background color
    for frame in frames:
        frame.set_facecolor(PLOT_BACKGROUND_COLOR)
        frame.grid(which='both', color='lightgray', ls='--')
    # loop around orders and plot
    for order_num in cal_orders:
        # get a mean across a few orders (if possible)
        start = np.max([0, order_num-5])
        end = np.min([wave_cents.shape[1], order_num+5])
        dv_ord = np.nanmean(dv[:, start:end], axis=1)
        dv_ord_ratio = np.diff(dv_ord) / mjdmid_diff

        frames[0].plot_date(mjdmid.plot_date, dv_ord,
                            label=f'Order {order_num}', ls='None',
                            marker='o')
        frames[1].plot_date(mjdmid.plot_date[1:], dv_ord_ratio,
                            label=f'Order {order_num}', ls='None',
                            marker='o')
    # set labels
    frames[0].set(xlabel='Date', ylabel='Central pixel offset [m/s]')
    frames[0].legend(loc=0)
    frames[1].set(xlabel='Date', ylabel='Central pixel offset [m/s/day]')
    frames[1].legend(loc=0)
    # add title
    plt.suptitle(plot_title)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()


def calib_mjd_plot(prop_name: str, cal_props: Dict[str, Any],
                   plot_title: str, plot_path: str,
                   mjd_key: str = 'KW_MID_OBS_TIME'):
    # get hdict and header yaml descriptions
    hdict = cal_props['HDICT']
    label = cal_props['LABEL']
    # get mjd date
    mjd = Time(cal_props['HDICT'][mjd_key], format='mjd')
    # get variable
    variable = hdict[prop_name]
    variable_name = label[prop_name]
    # --------------------------------------------------------------------------
    # setup the figure
    fig, frame = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
    # set background color
    frame.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame.grid(which='both', color='lightgray', ls='--')
    # plot shape dx
    frame.plot_date(mjd.plot_date, variable, fmt='.', alpha=0.5)
    frame.set(xlabel='Date', ylabel=variable_name)
    # --------------------------------------------------------------------------
    plt.subplots_adjust(hspace=0, left=0.1, right=0.99, bottom=0.15, top=0.9)
    # add title
    plt.suptitle(plot_title)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()


# =============================================================================
# Debug plots
# =============================================================================
def debug_mjd_extsmax_plot(debug_props: Dict[str, Any], plot_path: str,
                           plot_title: str):
    debug_mjd_plot('EXT_EXTSMAX', debug_props, plot_title, plot_path)


def debug_mjd_effron_plot(debug_props: Dict[str, Any], plot_path: str,
                          plot_title: str):
    debug_mjd_plot('EXT_EFFRON', debug_props, plot_title, plot_path)


def debug_mjd_plot(prop_name: str, debug_props: Dict[str, Any],
                   plot_title: str, plot_path: str, ykind: str = 'ext',
                   mjd_key: str = 'EXT_MJD'):
    # get hdict and header yaml descriptions
    hdict = debug_props['HDICT']
    ext_headers = debug_props['HYAML'][ykind]
    # get mjd date
    mjd = debug_props[mjd_key]
    # get variable
    variable = hdict[prop_name]
    variable_name = ext_headers[prop_name]['label']
    # --------------------------------------------------------------------------
    # setup the figure
    fig, frame = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
    # set background color
    frame.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame.grid(which='both', color='lightgray', ls='--')
    # plot shape dx
    frame.plot_date(mjd.plot_date, variable, fmt='.', alpha=0.5)
    frame.set(xlabel='Date', ylabel=variable_name)
    # --------------------------------------------------------------------------
    plt.subplots_adjust(hspace=0, left=0.1, right=0.99, bottom=0.15, top=0.9)
    # add title
    plt.suptitle(plot_title)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()


def debug_tcorr_map_plot(debug_props: Dict[str, Any], plot_path: str,
                         plot_title: str):
    # get pconstants
    sc1d_files = debug_props['SC1D_FILES']
    tmp_s1d = debug_props['TEMP_S1D']
    wave_min, wave_max = debug_props['TCORR_WAVE_RANGE']
    wave_diff = wave_max - wave_min
    # -------------------------------------------------------------------------
    # deal with having no template
    if len(tmp_s1d) == 0:
        cal_med = True
    else:
        cal_med = False
    # -------------------------------------------------------------------------
    # load the first file as reference
    ref_table = Table.read(sc1d_files[0], 'SC1D_V_FILE')
    ref_wave = np.array(ref_table['wavelength'])
    # Find the order with the most data points within the wavelength range
    # of interest
    wave_mask = (ref_wave > wave_min - 0.5 * wave_diff)
    wave_mask &= (ref_wave < wave_max + 0.5 * wave_diff)
    # cut down the wavelength vector
    ref_wave = ref_wave[wave_mask]
    # -------------------------------------------------------------------------
    # create a map for plot
    map2d = np.zeros((len(sc1d_files), np.sum(wave_mask)))
    map2d_star = np.zeros((len(sc1d_files), np.sum(wave_mask)))
    bervs = np.zeros(len(sc1d_files))
    qcc_pass = np.zeros((len(sc1d_files), 1))
    rvoffset = np.zeros((len(sc1d_files), 1))
    # -------------------------------------------------------------------------
    # loop through each file and process each spectra (and add to maps)
    for it, sc1d_file in enumerate(sc1d_files):
        # open the sc1d file
        it_table = Table.read(sc1d_file, 'SC1D_V_FILE')
        # get the header
        it_hdr = fits.getheader(sc1d_file)
        # ---------------------------------------------------------------------
        # get the berv
        bervs[it] = float(it_hdr['BERV'])
        # ---------------------------------------------------------------------
        # get the parameter that all quality control passed
        qc_all = str(it_hdr['QCC_ALL'])
        if qc_all.upper() in ['T', 'TRUE', '1']:
            qcc_pass[it] = 1
        else:
            qcc_pass[it] = 0
        # ---------------------------------------------------------------------
        # get the rv offset (set to zero if not found)
        rvoffset[it] = float(it_hdr.get('MKT_ARV', 0.0))
        # if set to NaN set to zero (for shift)
        if np.isnan(rvoffset[it]):
            rvoffset[it] = 0.0
        # ---------------------------------------------------------------------
        # get spectrum for preferred order
        spec_ord = np.array(it_table['flux'][wave_mask]).astype(float)
        # remove the table
        del it_table
        del it_hdr
        # ---------------------------------------------------------------------
        # apply low pass filter to the spectrum and normalize
        map2d[it] = spec_ord / mp.lowpassfilter(spec_ord, 501)
        # update the map2d_star (if we don't have a template)
        if cal_med:
            # interpolate the valid data points
            valid = np.isfinite(map2d[it])
            spec_spline = mp.iuv_spline(ref_wave[valid], map2d[it][valid])
            # correct for the stars motions using doppler shift
            dv = bervs[it] - (rvoffset[it] / 1000.0)
            dvshift = mp.relativistic_waveshift(dv, units='km/s')
            map2d_star[it] = spec_spline(ref_wave / dvshift)
    # -------------------------------------------------------------------------
    # Compute the median spectrum across all observations
    if cal_med:
        med = mp.nanmedian(map2d_star, axis=0)
    else:
        tmp_table = Table.read(tmp_s1d[-1], 'TELLU_TEMP_S1DV')
        med = np.array(tmp_table['flux'][wave_mask]).astype(float)
        med = med / mp.lowpassfilter(med, 501)
    # Copy the original map2d to map2d_star
    map2d_star = np.array(map2d)
    # Interpolate the median spectrum
    valid = np.isfinite(med)
    # get the spline of the median (or template)
    med_spl = mp.iuv_spline(ref_wave[valid], med[valid])
    # Subtract the median spectrum from each observation
    for it in range(len(sc1d_files)):
        # calculate shift for this file
        dv = bervs[it] - (rvoffset[it] / 1000.0)
        dvshift = mp.relativistic_waveshift(-dv, units='km/s')
        # correct the spectrum by the median of all observations
        map2d_star[it] -= med_spl(ref_wave / dvshift)
    # -------------------------------------------------------------------------
    # Custom colormap for binary data: green for 1, red for 0
    binary_cmap = ListedColormap(['orange', 'purple'])
    # set up grid size
    gridspec_kw = {'width_ratios': [40, 1, 1, 1],
                   'height_ratios': [1, 1]}
    # Create subplots for the original and corrected data
    fig = plt.figure(figsize=(12, 12))
    gs = gridspec.GridSpec(2, 4, **gridspec_kw)
    # main plot frames
    main_1 = fig.add_subplot(gs[0, 0])
    main_2 = fig.add_subplot(gs[1, 0])
    # qcc axis
    qcc_1 = fig.add_subplot(gs[0, 1])
    qcc_2 = fig.add_subplot(gs[1, 1])
    # colorbars
    cb_1 = fig.add_subplot(gs[0, 3])
    cb_2 = fig.add_subplot(gs[1, 3])
    # Define the extent of the plot in terms of wavelength and
    # observation number
    extent = [ref_wave.min(), ref_wave.max(), 0, len(sc1d_files)]
    # -------------------------------------------------------------------------
    # Calculate the plotting range for the original data
    p10, p90 = np.nanpercentile(map2d, [10, 90])
    mid = 0.5 * (p10 + p90)
    width = 3 * (p90 - p10)
    range_plot = [mid - 0.5 * width, mid + 0.5 * width]
    # -------------------------------------------------------------------------
    # Plot the original data
    im0 = main_1.imshow(map2d, aspect='auto',
                        vmin=range_plot[0], vmax=range_plot[1],
                        interpolation='nearest', extent=extent,
                        origin='lower')
    # Set labels and titles for the plots
    main_1.set_ylabel('Observation number')
    main_1.set_title('Telluric corrected s1d')
    main_1.set(xlim=[wave_min, wave_max])
    # -------------------------------------------------------------------------
    # add color bar 1
    fig.colorbar(im0, cax=cb_1, orientation='vertical',
                 label='Normalized\nIntensity')
    cb_1.set_aspect('auto')
    # -------------------------------------------------------------------------
    # Plot qcc
    qcc_1.imshow(qcc_pass, aspect='auto', cmap=binary_cmap,
                 interpolation='nearest', origin='lower', vmin=0, vmax=1)
    # adjust the binary mask axis
    for pos in ['top', 'right', 'left', 'bottom']:
        qcc_1.spines[pos].set_visible(False)
    qcc_1.tick_params(left=False, bottom=False, labelleft=False,
                      labelbottom=False)
    qcc_1.set_xticks([])
    qcc_1.set_xlabel('QC', labelpad=10, loc='center')
    qcc_1.xaxis.set_label_position('top')
    # -------------------------------------------------------------------------
    # Calculate the plotting range for the corrected data
    p10, p90 = np.nanpercentile(map2d_star, [10, 90])
    mid = 0.5 * (p10 + p90)
    width = 3 * (p90 - p10)
    range_plot = [mid - 0.5 * width, mid + 0.5 * width]
    # -------------------------------------------------------------------------
    # Plot the corrected data
    im1 = main_2.imshow(map2d_star, aspect='auto',
                        vmin=range_plot[0], vmax=range_plot[1],
                        interpolation='nearest', extent=extent,
                        origin='lower')
    # Set labels and titles for the plots
    main_2.set_xlabel('Wavelength')
    main_2.set_ylabel('Observation number')
    main_2.set_title('Residuals to star median')
    main_2.set(xlim=[wave_min, wave_max])
    # -------------------------------------------------------------------------
    # add color bar
    fig.colorbar(im1, cax=cb_2, orientation='vertical',
                 label='Normalized\nResidual')
    # Ensure the colorbar axes are properly adjusted
    cb_2.set_aspect('auto')
    # -------------------------------------------------------------------------
    # Plot qcc
    qcc_2.imshow(qcc_pass, aspect='auto', cmap=binary_cmap,
                 interpolation='nearest', origin='lower', vmin=0, vmax=1)
    # adjust the binary mask axis
    qcc_2.axis('off')
    # --------------------------------------------------------------------------
    plt.subplots_adjust(hspace=0.15, wspace=0.01,
                        left=0.1, right=0.9, bottom=0.05, top=0.9)
    # deal with flagging no tempalte
    if cal_med:
        plot_title += ' [No Template Found]'
    # add title
    plt.suptitle(plot_title)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()


def debug_version_plot(debug_props: Dict[str, Any], plot_path: str,
                       plot_title: str):
    # get hdict and header yaml descriptions
    hdict = debug_props['HDICT']
    ext_headers = debug_props['HYAML']['ext']
    # get mjd date
    mjd = debug_props['EXT_MJD']
    # get variable
    version = hdict['EXT_VERSION']
    version_name = ext_headers['EXT_VERSION']['label']
    pdate = np.array(hdict['EXT_PDATE']).astype(str)
    pdate = Time(pdate, format='iso').mjd
    pdate_name = ext_headers['EXT_PDATE']['label']
    # --------------------------------------------------------------------------
    # setup the figure
    fig, frames = plt.subplots(nrows=2, ncols=1, figsize=(12, 4), sharex='all')
    # set background color
    for frame in frames:
        frame.set_facecolor(PLOT_BACKGROUND_COLOR)
        frame.grid(which='both', color='lightgray', ls='--')
    # plot version
    frames[0].plot_date(mjd.plot_date, version, fmt='.', alpha=0.5,
                        label=version_name)
    frames[0].legend(loc=0)
    # plot processed date
    frames[1].plot_date(mjd.plot_date, pdate, fmt='.', alpha=0.5,
                        label=pdate_name)
    frames[1].set(xlabel='Date', ylabel='mjd')
    frames[1].legend(loc=0)
    # --------------------------------------------------------------------------
    plt.subplots_adjust(hspace=0.05, left=0.1, right=0.99, bottom=0.15, top=0.9)
    # add title
    plt.suptitle(plot_title)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()


def debug_mjd_cdt_plot(debug_props: Dict[str, Any], plot_path: str,
                       plot_title: str):
    # get hdict and header yaml descriptions
    hdict = debug_props['HDICT']
    ext_headers = debug_props['HYAML']['ext']
    # get mjd date
    mjd = debug_props['EXT_MJD']
    # define the keys to add
    keys = dict()
    keys['CDTDARK'] = 1
    keys['CDTBAD'] = 0
    keys['CDTBACK'] = 0
    keys['CDTORDP'] = 0
    keys['CDTLOCO'] = 0
    keys['CDTSHAPL'] = 0
    keys['CDTSHAPX'] = 1
    keys['CDTSHAPY'] = 1
    keys['CDTFLAT'] = 0
    keys['CDTBLAZE'] = 0
    keys['CDTWAVE'] = 0
    keys['WAVETIME'] = 0
    # --------------------------------------------------------------------------
    # setup the figure
    fig, frames = plt.subplots(nrows=12, ncols=1, figsize=(12, 24),
                               sharex='all')
    # loop through keys
    for it, key in enumerate(keys):
        # get the variable and variable name
        variable = hdict[f'EXT_{key}']
        variable_name = ext_headers[f'EXT_{key}']['label']
        # get the color of the points
        if keys[key] == 1:
            color = 'purple'
        else:
            color = 'orange'
        # get frame
        frame = frames[it]
        # set background color
        frame.set_facecolor(PLOT_BACKGROUND_COLOR)
        frame.grid(which='both', color='lightgray', ls='--')
        # plot shape dx
        frame.plot_date(mjd.plot_date, variable - mjd.value, color=color,
                        fmt='.', alpha=0.5, label=variable_name)
        frame.set(ylabel=r'$\Delta$t [d]')
        frame.legend(loc=0)

    frames[-1].set(xlabel='Date')
    # --------------------------------------------------------------------------
    plt.subplots_adjust(hspace=0, left=0.1, right=0.99, bottom=0.05, top=0.95)
    # add title
    plt.suptitle(plot_title)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()

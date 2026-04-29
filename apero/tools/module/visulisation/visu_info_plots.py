#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-12-12 at 14:10

@author: cook
"""
import os
import warnings
from typing import Any, Dict, List, Union

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from astropy.io import fits
from astropy.table import Table

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
from apero.science.calib import wave as wave_mod
from apero.tools.module.ari import ari_core
from apero.tools.module.ari import ari_plot


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.visulisation.visu_info_plots.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict
# define the colours for graphs
COLORS = {
    'title': '#F57C00',  # deep orange
    'row_even': '#FFF3CD',  # pastel yellow
    'row_odd': '#FFE0B2',  # pastel orange
    'panel_bg': '#FFF8E1',  # spectrum background
    'key': '#E3F2FD',  # header key
    'value': '#E8F5E9',  # header value
    'comment': '#FCE4EC',  # header comment
}

# target header keys
T_HKEYS = dict()
T_HKEYS['Object name'] = '{KW_OBJNAME}'
T_HKEYS['RA'] = '{KW_OBJRA} deg ({KW_DRS_RA_S})'
T_HKEYS['Dec'] = '{KW_OBJDEC} deg ({KW_DRS_DEC_S})'
T_HKEYS['pmra'] = '{KW_DRS_PMRA} mas/yr ({KW_DRS_PMRA_S})'
T_HKEYS['pmde'] = '{KW_DRS_PMDE} mas/yr ({KW_DRS_PMDE_S})'
T_HKEYS['Plx'] = '{KW_DRS_PLX} mas ({KW_DRS_PLX_S})'
T_HKEYS['Teff'] = '{KW_DRS_TEFF} K ({KW_DRS_TEFF_S})'
T_HKEYS['PI names'] = '{KW_PI_NAME}'
T_HKEYS['Project/Run name'] = '{KW_RUN_ID}'
# max number of inches for figure height
MAX_FIG_H = 30
# plot extensions
EXTENSIONS = ['.png']


# =============================================================================
# Define general functions
# =============================================================================
def plotend(params: ParamDict, filename: str, thumbnail: bool = False):
    # deal with show vs save
    pkind = 'summary'
    # get path
    if not drs_text.null_text(params['INPUTS']['INFOPATH'], ['None', 'Null', '']):
        filepath = params['INPUTS']['INFOPATH']
    else:
        filepath = os.path.dirname(filename)
    # we don't want a file for the filepath we want its directory
    if os.path.isfile(filepath):
        filepath = os.path.dirname(filepath)
    # remove any extension
    basename = os.path.splitext(os.path.basename(filename))[0]
    # get full plot path
    filename = os.path.join(filepath, basename)
    # deal with summary plots
    if pkind == 'summary':
        # loop around extensions
        for ext in EXTENSIONS:
            # deal with thumbnails
            if thumbnail:
                savename = filename + '_256' + ext
            else:
                savename = filename + ext
            # print progress
            if params.get('__VISU_VERBOSE', True):
                msg = '\tSaving plot to {0}'
                WLOG(params, '', msg.format(savename))
            # save file to disk
            plt.savefig(savename)
        plt.close()
    # deal with show plots
    elif pkind == 'show':
        plt.show(block=True)
        plt.close()
    else:
        pass


def draw_kv_table(ax, title, data):
    ax.axis('off')

    rows = [[k, str(v)] for k, v in data.items()]
    table = ax.table(
        cellText=rows,
        colLabels=[title, 'Value'],
        loc='center',
        cellLoc='left'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.4)

    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor(COLORS['title'])
            cell.set_text_props(color='white', weight='bold')
        else:
            color = COLORS['row_even'] if r % 2 == 0 \
                else COLORS['row_odd']
            cell.set_facecolor(color)


def make_target_dict(params: ParamDict, filename: str,
                     header: fits.Header = None,
                     tdict: Dict[str, Any] = None) -> Dict[str, Any]:
    # get all keys from header in the parameter format
    hdict = dict()
    if header is not None:
        for key in params.keys():
            if key.startswith('KW_'):
                hdict[key] = header.get(params[key][0], 'N/A')
    # push the strings into target dictionary for formatting
    target_dict = dict()
    target_dict['PATH'] = os.path.dirname(filename)
    target_dict['FILENAME'] = os.path.basename(filename)
    # add extra keys
    if tdict is not None:
        for key in tdict:
            target_dict[key] = tdict[key]
    # add the header keys
    if header is not None:
        for key in T_HKEYS:
            target_dict[key] = T_HKEYS[key].format(**hdict)
    # return the target dictionary
    return target_dict


def get_main_fiber() -> str:
    # update instrument
    instrument = str(base.IPARAMS['INSTRUMENT'])
    # load pconst
    pconst = constants.pload(instrument=instrument)
    # get science fiber
    science_fibers, _ = pconst.FIBER_KINDS()
    # assume first fiber is the main science fiber
    fiber = science_fibers[0]
    # return the main fiber
    return fiber


# =============================================================================
# Define spectrum functions
# =============================================================================
def spec_plus_zoom_page(target_dict: Dict[str, Any],
                        zooms: List[List[float]]) -> Dict[str, Any]:
    fig = plt.figure(figsize=(15, 15), dpi=300)

    gs = fig.add_gridspec(
        nrows=3,
        ncols=len(zooms),
    )
    frames = dict()
    # Target info
    frames['TARGET'] = fig.add_subplot(gs[0, :])
    draw_kv_table(frames['TARGET'], 'Target Information', target_dict)
    # Spectrum: 4 panels
    frames['MAIN'] = fig.add_subplot(gs[1, :])

    for z_it, zoom in enumerate(zooms):
        frames[f'ZOOM{z_it}'] = fig.add_subplot(gs[2, z_it])
    # loop around frames to plot spectrum
    for fkey in frames.keys():
        frame = frames[fkey]
        frame.set_facecolor(COLORS['panel_bg'])
        frame.grid(which='both', color='lightgray', ls='--')

    return frames


def plot_zoom(frame, x: np.ndarray, y: np.ndarray, limits: list,
              **kwargs):
    # mask the data  - instead of just setting limits
    mask = (x >= limits[0]) & (x <= limits[1])
    # plot the masked data (passing any args from call)
    frame.plot(x[mask], y[mask], **kwargs)
    return frame


def plot_spectrum(params: ParamDict, filename: str,
                  dataset: Dict[str, Any], header: fits.Header,
                  title: str,
                  zoom_params: Union[List[str], List[float]],
                  xlabel: str = 'Wavelength [nm]',
                  ylabel: str = 'Flux'):
    # construct target dictionary
    target_dict = make_target_dict(params, filename, header)
    # get zoom limits
    zooms = []
    for zoom in zoom_params:
        if isinstance(zoom, str):
            zooms.append(params.listp(zoom, dtype=float))
        else:
            zooms.append(zoom)

    # set up figure, tables and get plotting frames
    frames = spec_plus_zoom_page(target_dict, zooms)
    # plot the spectra
    for label in dataset:
        # get parameters for each dataset to plot
        x = dataset[label]['x']
        y = dataset[label]['y']
        # skip plotting if we don't have any points
        mask = np.isfinite(x) & np.isfinite(y)
        if np.sum(mask) == 0:
            continue
        # get plot kwargs from dataset kwargs
        pkwargs = dataset[label]['kwargs']
        # plot the main plot
        frames['MAIN'].plot(x, y, **pkwargs, label=label)
        frames['MAIN'].legend(loc=0)
        # plot the zooms
        for z_it, zoom in enumerate(zooms):
            _ = plot_zoom(frames[f'ZOOM{z_it}'], x, y, zoom, **pkwargs)

    # add legend
    frames['MAIN'].set_title(title)
    frames['MAIN'].set_xlabel(xlabel)
    frames['MAIN'].set_ylabel(ylabel)
    # save/show etc
    plotend(params, filename)


def plot_spectrum_thumbnail(params: ParamDict, filename: str,
                            dataset: Dict[str, Any]):
    dpi = 100
    fig = plt.figure(figsize=(256 / dpi, 256 / dpi), dpi=dpi)
    frame = fig.add_subplot(1, 1, 1)
    frame.set_facecolor(COLORS['panel_bg'])
    frame.grid(which='both', color='lightgray', ls='--')
    # plot the spectra
    for label in dataset:
        # get parameters for each dataset to plot
        x = dataset[label]['x']
        y = dataset[label]['y']
        # skip plotting if we don't have any points
        mask = np.isfinite(x) & np.isfinite(y)
        if np.sum(mask) == 0:
            continue
        # get plot kwargs from dataset kwargs
        pkwargs = dataset[label]['kwargs']
        frame.plot(x, y, **pkwargs)
    # force a tight layout for thumbnails
    plt.tight_layout()
    # save/show etc
    plotend(params, filename, thumbnail=True)


# =============================================================================
# Define ccf functions
# =============================================================================
def plot_ccf(params: ParamDict, filename: str, header: fits.Header,
             ccf_props: Dict[str, Any], title: str):
    # construct target dictionary
    target_dict = make_target_dict(params, filename, header)
    # set up figure, tables and get plotting frames
    fig = plt.figure(figsize=(15, 15), dpi=300)

    gs = fig.add_gridspec(
        nrows=4,
        ncols=1,
    )
    frames = dict()
    # Target info
    frames['TARGET'] = fig.add_subplot(gs[0])
    draw_kv_table(frames['TARGET'], 'Target Information', target_dict)
    # CCF: 3 panels
    frames['CCF1'] = fig.add_subplot(gs[1])
    frames['CCF2'] = fig.add_subplot(gs[2])
    frames['CCF3'] = fig.add_subplot(gs[3])
    # loop around frames to plot spectrum
    for fkey in frames.keys():
        frame = frames[fkey]
        frame.set_facecolor(COLORS['panel_bg'])
    # get parameters from props
    rv_vec = ccf_props['rv_vec']
    y1_1sig = ccf_props['y1_1sig']
    y2_1sig = ccf_props['y2_1sig']
    y1_2sig = ccf_props['y1_2sig']
    y2_2sig = ccf_props['y2_2sig']
    med_ccf = ccf_props['med_ccf']
    has_fit = ccf_props['has_fit']
    fit = ccf_props['fit']
    xlim = ccf_props['xlim']
    # ---------------------------------------------------------------------
    # Top plot median CCF
    # ---------------------------------------------------------------------
    # mask by xlim
    limmask = (rv_vec > xlim[0]) & (rv_vec < xlim[1])

    frames['CCF1'].fill_between(rv_vec[limmask], y1_2sig[limmask],
                                y2_2sig[limmask],
                                color='orange', alpha=0.4)
    frames['CCF1'].fill_between(rv_vec[limmask], y1_1sig[limmask],
                                y2_1sig[limmask],
                                color='red', alpha=0.4)
    frames['CCF1'].plot(rv_vec[limmask], med_ccf[limmask], alpha=1.0,
                        color='black')
    if has_fit:
        frames['CCF1'].plot(rv_vec[limmask], fit[limmask], alpha=0.8,
                            label='Gaussian fit', ls='--')
    frames['CCF1'].legend(loc=0)
    frames['CCF1'].set(xlabel='RV [km/s]',
                       ylabel='Normalized CCF')
    frames['CCF1'].grid(which='both', color='lightgray', ls='--')

    # ---------------------------------------------------------------------
    # Middle plot median CCF residuals
    # ---------------------------------------------------------------------
    if has_fit:
        frames['CCF2'].fill_between(rv_vec[limmask],
                                    y1_2sig[limmask] - fit[limmask],
                                    y2_2sig[limmask] - fit[limmask],
                                    color='orange',
                                    alpha=0.4, label=r'2-$\sigma$')
        frames['CCF2'].fill_between(rv_vec[limmask],
                                    y1_1sig[limmask] - fit[limmask],
                                    y2_1sig[limmask] - fit[limmask],
                                    color='red',
                                    alpha=0.4, label=r'1-$\sigma$')
        frames['CCF2'].plot(rv_vec[limmask], med_ccf[limmask] - fit[limmask],
                            alpha=0.8, label='Median residual')
        frames['CCF2'].legend(loc=0, ncol=3)
        frames['CCF2'].set(xlabel='RV [km/s]', ylabel='Residuals [to fit]')
    else:
        frames['CCF2'].text(0.5, 0.5, 'No fit to CCF possible',
                            horizontalalignment='center')
        frames['CCF2'].legend(loc=0, ncol=3)
        frames['CCF2'].set(xlim=[0, 1], ylim=[0, 1], xlabel='RV [km/s]',
                           ylabel='Residuals')
    frames['CCF2'].grid(which='both', color='lightgray', ls='--')
    # ---------------------------------------------------------------------
    # Bottom plot median CCF residuals
    # ---------------------------------------------------------------------
    if has_fit:
        frames['CCF3'].fill_between(rv_vec[limmask],
                                    y1_2sig[limmask] - med_ccf[limmask],
                                    y2_2sig[limmask] - med_ccf[limmask],
                                    color='orange',
                                    alpha=0.4, label=r'2-$\sigma$')
        frames['CCF3'].fill_between(rv_vec[limmask],
                                    y1_1sig[limmask] - med_ccf[limmask],
                                    y2_1sig[limmask] - med_ccf[limmask],
                                    color='red',
                                    alpha=0.4, label=r'1-$\sigma$')
        frames['CCF3'].plot(rv_vec[limmask],
                            med_ccf[limmask] - med_ccf[limmask],
                            alpha=0.8, label='Median residual')
        frames['CCF3'].legend(loc=0, ncol=3)
        frames['CCF3'].set(xlabel='RV [km/s]', ylabel='Residuals [To Median]')
    else:
        frames['CCF3'].text(0.5, 0.5, 'No fit to CCF possible',
                            horizontalalignment='center')
        frames['CCF3'].legend(loc=0, ncol=3)
        frames['CCF3'].set(xlim=[0, 1], ylim=[0, 1], xlabel='RV [km/s]',
                           ylabel='Residuals [To Median]')
    frames['CCF3'].grid(which='both', color='lightgray', ls='--')
    # ---------------------------------------------------------------------
    # add title
    plt.suptitle(title)
    # force a tight layout for thumbnails
    plt.tight_layout()
    # save/show etc
    plotend(params, filename)


def plot_ccf_thumbnail(params: ParamDict, filename: str,
                       ccf_props: Dict[str, Any]):
    dpi = 100
    fig = plt.figure(figsize=(256 / dpi, 256 / dpi), dpi=dpi)
    frame = fig.add_subplot(1, 1, 1)
    frame.set_facecolor(COLORS['panel_bg'])
    frame.grid(which='both', color='lightgray', ls='--')
    # get parameters from props
    rv_vec = ccf_props['rv_vec']
    med_ccf = ccf_props['med_ccf']
    xlim = ccf_props['xlim']
    # ---------------------------------------------------------------------
    # Top plot median CCF
    # ---------------------------------------------------------------------
    # mask by xlim
    limmask = (rv_vec > xlim[0]) & (rv_vec < xlim[1])
    # plot median ccf
    frame.plot(rv_vec[limmask], med_ccf[limmask], alpha=1.0, color='black')
    # save/show etc
    plotend(params, filename, thumbnail=True)


# =============================================================================
# Define lbl functions
# =============================================================================
def get_lbl_rdb_props(params: ParamDict, rdb_table: Table):
    """
    Take from apero_core.AriObject.get_lbl_parameters

    # TODO: merge this at some point

    :param params:
    :param filename:
    :return:
    """
    # storage of properties
    lbl_props = dict()
    # get ext h key
    ext_h_order = params['INFO_VISU_EXT_ORDER']
    ext_h_key = params['KW_EXT_SNR'][0].format(ext_h_order)
    # get the values required
    lbl_props['rjd'] = np.array(rdb_table['rjd'])
    lbl_props['vrad'] = np.array(rdb_table['vrad'])
    lbl_props['svrad'] = np.array(rdb_table['svrad'])
    lbl_props['plot_date'] = np.array(rdb_table['plot_date'])
    lbl_props['snr_h'] = np.array(rdb_table[ext_h_key])
    lbl_props['SNR_H_LABEL'] = 'SNR[Order {0}]'.format(ext_h_order)
    lbl_props['RESET_RV'] = np.array(rdb_table['RESET_RV']).astype(bool)
    lbl_props['NUM_RESET_RV'] = np.sum(rdb_table['RESET_RV'])
    # -----------------------------------------------------------------
    # deal with wavelength rv plot parameters
    # -----------------------------------------------------------------
    # Get all the keys (column names) from the table
    keys = np.array(rdb_table.keys())
    # Filter keys to keep only those that start with 'vrad'
    vrad_keys = keys[np.char.startswith(keys, 'vrad')]
    # Further filter keys to keep only those that contain 'nm' in their name
    vrad_keys = vrad_keys[np.char.find(vrad_keys, 'nm') > 0]
    # push into lbl props
    lbl_props['VRAD_DICT'] = dict()
    lbl_props['SVRAD_DICT'] = dict()
    # add keys from vrad dict
    for key in vrad_keys:
        lbl_props['VRAD_DICT'][key] = np.array(rdb_table[key])
        lbl_props['SVRAD_DICT'][key] = np.array(rdb_table['s' + key])

    # Extract the wavelength from the 'vrad' keys by splitting
    # the string
    wavemap = []
    for vrad_key in vrad_keys:
        wavemap.append(float(vrad_key.split('_')[1].split('nm')[0]))
    lbl_props['wavemap'] = np.array(wavemap)

    return lbl_props


def plot_lbl_rdb(params: ParamDict, filename: str,
                 header: Union[fits.Header, None],
                 lbl_props: Dict[str, Any], objname_template: str):
    # construct target dictionary
    target_dict = make_target_dict(params, filename, header)
    # set up figure, tables and get plotting frames
    fig = plt.figure(figsize=(15, 15), dpi=300)

    gs = fig.add_gridspec(
        nrows=4,
        ncols=1,
    )
    frames = []
    # Target info
    frames.append(fig.add_subplot(gs[0]))
    draw_kv_table(frames[0], 'Target Information', target_dict)
    # CCF: 3 panels
    frames.append(fig.add_subplot(gs[1]))
    frames.append(fig.add_subplot(gs[2]))
    frames.append(fig.add_subplot(gs[3]))
    # loop around frames to add background
    for frame in frames:
        frame.set_facecolor(COLORS['panel_bg'])
    # plot the full lbl plot
    ari_plot.lbl_plot(lbl_props, '',
                      plot_title=f'LBL {objname_template}',
                      fig=fig, frames=frames[1:])
    # save/show etc
    plotend(params, filename)


def plot_lbl_rdb_thumbnail(params: ParamDict, filename: str,
                           lbl_props: Dict[str, Any]):
    # get parameters from props
    plot_date = lbl_props['plot_date']
    vrad = lbl_props['vrad']
    # find percentile cuts that will be expanded by 150% for the ylim
    pp = np.nanpercentile(vrad, [10, 90])
    diff = pp[1] - pp[0]
    central_val = np.nanmean(pp)
    # used for plotting but also for the flagging of outliers
    ylim = [central_val - 1.5 * diff, central_val + 1.5 * diff]
    # set up figure
    dpi = 100
    fig = plt.figure(figsize=(256 / dpi, 256 / dpi), dpi=dpi)
    frame = fig.add_subplot(1, 1, 1)
    frame.set_facecolor(COLORS['panel_bg'])
    frame.grid(which='both', color='lightgray', ls='--')
    # plot just the vrad vs date
    frame.plot_date(plot_date, vrad, fmt='.',
                    alpha=0.5, color='black', ls='None')
    frame.set(ylim=ylim)
    # get start end
    start = plot_date[0]
    end = plot_date[-1]
    # get 1/4 and 3/4 labels
    label1 = start + (end - start) / 4
    label2 = start + 3 * (end - start) / 4
    # push onto x axis
    frame.set_xticks([label1, label2])
    # save/show etc
    plotend(params, filename, thumbnail=True)


def lbl_trumpet_plot(frame, wavemap: np.ndarray, y: np.ndarray,
                     ey: np.ndarray, mask: np.ndarray,
                     mask_on_label: str, mask_off_label: str,
                     on_color: str = 'blue', off_color: str = 'cyan',
                     ylabel: str = None, low_percentile: float = 5.0,
                     high_percentile: float = 95.0):
    # plot the mask off (bad) points (faint)
    frame.errorbar(wavemap[~mask], y[~mask], yerr=ey[~mask],
                   marker='o', alpha=0.05, color=off_color,
                   label=mask_off_label, ls='None')
    # plot the mask on (good) points
    frame.errorbar(wavemap[mask], y[mask], yerr=ey[mask],
                   marker='o', alpha=0.5, color=on_color,
                   label=mask_on_label, ls='None')
    # set limits to 5 sigma away from median
    with warnings.catch_warnings(record=True) as _:
        median = np.nanmedian(y)
        low, high = np.nanpercentile(y, [low_percentile, high_percentile])
    frame.set(ylim=[low, high])
    # plot the median line
    frame.axhline(median, color='red', ls='--',
                  label='Med: {0:.2f}'.format(median))
    # set the background colour
    frame.set_facecolor(COLORS['panel_bg'])
    # set the grid
    frame.grid(which='both', color='lightgray', ls='--')
    # add labels and legend if required
    if ylabel is not None:
        frame.set_xlabel('Wavelength [nm]')
        frame.set_ylabel(ylabel)
        # --- LEGEND WITH OPAQUE PROXY ARTISTS ---
        legend_handles = [
            Line2D([], [], marker='o', color=off_color, linestyle='None',
                   markersize=6, label=mask_off_label),
            Line2D([], [], marker='o', color=on_color, linestyle='None',
                   markersize=6, label=mask_on_label),
            Line2D([], [], color='red', linestyle='--',
                   label=f'Med: {median:.2f}')
        ]

        frame.legend(handles=legend_handles, loc=0)


# =============================================================================
# Define worker functions
# =============================================================================
def wave_from_header(params: ParamDict, nbx: int,
                     header: fits.Header) -> np.ndarray:
    # get the number of orders from the header
    nbo = int(header[params['KW_WAVE_NBO'][0]])
    # get the wave fit degree from the header
    deg = int(header[params['KW_WAVE_DEG'][0]])
    # get the header key that has the constants
    drskey = params['KW_WAVECOEFFS'][0]
    # create 2d list
    wave_coeffs = np.zeros((nbo, deg + 1), dtype=float)
    # loop around the 2D array
    dim1, dim2 = wave_coeffs.shape
    for it in range(dim1):
        for jt in range(dim2):
            # construct the key name
            keyname = drs_file.test_for_formatting(drskey, it * dim2 + jt)
            # set the value
            wave_coeffs[it][jt] = float(header[keyname])
    # get wavelength from header
    wavemap = wave_mod.get_wavemap_from_coeffs(wave_coeffs, nbo, nbx)
    # return the wavemap
    return wavemap


# =============================================================================
# Define file type functions (one per file type)
# =============================================================================
def plot_drs_post_e(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get main fiber
    fiber = get_main_fiber()
    # get the header
    header = fits.getheader(filename, extname='Flux{0}'.format(fiber))
    # get the data for this plot
    wave = fits.getdata(filename, extname='Wave{0}'.format(fiber))
    blaze = fits.getdata(filename, extname='Blaze{0}'.format(fiber))
    spectrum = fits.getdata(filename, extname='Flux{0}'.format(fiber))
    # set up dataset
    dataset = dict()
    dataset['Extracted Spectrum'] = {
        'x': wave.ravel(),
        'y': spectrum.ravel() / blaze.ravel(),
        'kwargs': {'color': 'blue', 'alpha': 0.7}
    }
    # set zoom from parameters
    zoom_params = ['INFO_VISU_Z1', 'INFO_VISU_Z2', 'INFO_VISU_Z3']
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO extracted spectrum', zoom_params)
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def plot_drs_post_t(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get main fiber
    fiber = get_main_fiber()
    # get the header
    header = fits.getheader(filename, extname='Flux{0}'.format(fiber))
    # get the data for this plot
    wave = fits.getdata(filename, extname='Wave{0}'.format(fiber))
    blaze = fits.getdata(filename, extname='Blaze{0}'.format(fiber))
    spectrum = fits.getdata(filename, extname='Flux{0}'.format(fiber))
    # set up dataset
    dataset = dict()
    dataset['Normalized Spectrum'] = {
        'x': wave.ravel(), 'y': spectrum.ravel() / blaze.ravel(),
        'kwargs': {'color': 'black', 'alpha': 0.7}
    }
    # set zoom from parameters
    zoom_params = ['INFO_VISU_Z1', 'INFO_VISU_Z2', 'INFO_VISU_Z3']
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO telluric corrected extracted spectrum', zoom_params)
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def post_drs_post_s(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get main fiber
    fiber = get_main_fiber()
    # get the header
    header = fits.getheader(filename, extname='UniformVelocity')
    # get the data for this plot
    table = Table.read(filename, hdu='UniformVelocity')
    # get columns from table
    wave = np.array(table['Wave'])
    spectrum = np.array(table['Flux{0}'.format(fiber)])
    # note tcorr may not be present (if it failed QC)
    tcorr_key = 'Flux{0}TelluCorrected'.format(fiber)
    if tcorr_key in table:
        tcorr = np.array(table[tcorr_key])
    # if we don't have any tcorr data then just fill with nans
    else:
        tcorr = np.full_like(spectrum, np.nan)
    # set up dataset
    dataset = dict()
    dataset['Extracted 1D Spectrum'] = {
        'x': wave, 'y': spectrum,
        'kwargs': {'color': 'black', 'alpha': 0.7}
    }
    dataset['Telluric corrected 1D Spectrum'] = {
        'x': wave, 'y': tcorr,
        'kwargs': {'color': 'red', 'alpha': 0.7}
    }
    # set zoom from parameters
    zoom_params = ['INFO_VISU_Z1', 'INFO_VISU_Z2', 'INFO_VISU_Z3']
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO 1D spectrum', zoom_params)
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def plot_drs_post_p(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get main fiber
    fiber = get_main_fiber()
    # get the header
    header = fits.getheader(filename, extname='Pol'.format(fiber))
    # get the data for this plot
    wave = fits.getdata(filename, extname='Wave{0}'.format(fiber))
    # get the data for this plot
    pol = fits.getdata(filename, extname='Pol')
    stokesi = fits.getdata(filename, extname='StokesI')
    null1 = fits.getdata(filename, extname='Null1')
    null2 = fits.getdata(filename, extname='Null2')
    # set up dataset
    dataset = dict()
    dataset['Pol'] = {
        'x': wave.ravel(), 'y': pol.ravel(),
        'kwargs': {'color': 'black', 'alpha': 0.7}
    }
    dataset['StokesI'] = {
        'x': wave.ravel(), 'y': stokesi.ravel(),
        'kwargs': {'color': 'blue', 'alpha': 0.7}
    }
    dataset['Null1'] = {
        'x': wave.ravel(), 'y': null1.ravel(),
        'kwargs': {'color': 'orange', 'alpha': 0.7}
    }
    dataset['Null2'] = {
        'x': wave.ravel(), 'y': null2.ravel(),
        'kwargs': {'color': 'purple', 'alpha': 0.7}
    }
    # set zoom from parameters
    zoom_params = ['INFO_VISU_Z1', 'INFO_VISU_Z2', 'INFO_VISU_Z3']
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO polarimetry spectru', zoom_params)
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def post_drs_post_v(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get main fiber
    fiber = get_main_fiber()
    # get the header
    header = fits.getheader(filename, extname='CCF'.format(fiber))
    # number of orders from header
    n_orders = header[params['KW_CCF_NMAX'][0]]
    # get the data for this plot
    table = Table.read(filename, hdu='CCF')
    # set up dataset
    ccf_props = dict()
    # push columns from table into ccf_props
    rv_vec = ccf_props['rv_vec'] = np.asarray(table['RV'], dtype=float)
    # storage for the CCF vectors
    all_ccf = np.zeros((n_orders, len(rv_vec)))
    # loop around all other files, load them and load into all_ccf
    for row in range(n_orders):
        # get the combined CCF for this file
        ccf_row = np.asarray(table['CCF{0:02d}'.format(row)], dtype=float)
        # normalize ccf
        with warnings.catch_warnings(record=True) as _:
            ccf_row = ccf_row / np.nanmedian(ccf_row)
        # push into vector
        all_ccf[row] = ccf_row
    # -----------------------------------------------------------------
    # get the 1 and 2 sigma limits
    lower_sig1 = 100 * (0.5 - mp.normal_fraction(1) / 2)
    upper_sig1 = 100 * (0.5 + mp.normal_fraction(1) / 2)
    lower_sig2 = 100 * (0.5 - mp.normal_fraction(2) / 2)
    upper_sig2 = 100 * (0.5 + mp.normal_fraction(2) / 2)
    # -----------------------------------------------------------------
    # there will be some nan slices - just ignore warnings here
    with warnings.catch_warnings(record=True):
        # y1 1sig is the 15th percentile of all ccfs
        ccf_props['y1_1sig'] = np.nanpercentile(all_ccf, lower_sig1, axis=0)
        # y2 1sig is the 84th percentile of all ccfs
        ccf_props['y2_1sig'] = np.nanpercentile(all_ccf, upper_sig1, axis=0)
        # y1 1sig is the 15th percentile of all ccfs
        ccf_props['y1_2sig'] = np.nanpercentile(all_ccf, lower_sig2, axis=0)
        # y2 1sig is the 84th percentile of all ccfs
        ccf_props['y2_2sig'] = np.nanpercentile(all_ccf, upper_sig2, axis=0)
        # med ccf is the median ccf (50th percentile)
        with warnings.catch_warnings(record=True) as _:
            ccf_props['med_ccf'] = np.nanmedian(all_ccf, axis=0)
        # get other properties using the ari core function
        ccf_props = ari_core.fit_ccf(ccf_props)
    # plot ccf
    plot_ccf(params, filename, header, ccf_props, 'APERO CCF spectrum')
    # plot ccf thumbnail
    plot_ccf_thumbnail(params, filename, ccf_props)


def red_tellu_temp(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get the header
    header = fits.getheader(filename, ext=0)
    # get the object name
    objname = header.get(params['KW_OBJNAME'][0], 'Unknown')
    # get the data for this plot
    spectrum = fits.getdata(filename, extname='TELLU_TEMP')
    # get wavelength from header
    wave = wave_from_header(params, spectrum.shape[1], header)
    # set up dataset
    dataset = dict()
    dataset['Template flux'] = {
        'x': wave.ravel(),
        'y': spectrum.ravel(),
        'kwargs': {'color': 'black', 'alpha': 0.7}
    }
    # set zoom from parameters (just look at one order at the center)
    zoom_params = ['INFO_VISU_Z1', 'INFO_VISU_Z2', 'INFO_VISU_Z3']
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO 2D Template {0}'.format(objname), zoom_params)
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def red_tellu_temp_s1dv(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get the header
    header = fits.getheader(filename, ext=0)
    # get the object name
    objname = header.get(params['KW_OBJNAME'][0], 'Unknown')
    # get table
    table = Table.read(filename, hdu='TELLU_TEMP_S1DV')
    # get the data for this plot
    wave = np.array(table['wavelength'])
    flux = np.array(table['flux'])
    # set up dataset
    dataset = dict()
    dataset['Template flux'] = {
        'x': wave, 'y': flux,
        'kwargs': {'color': 'black', 'alpha': 0.7}
    }
    # set zoom from parameters
    zoom_params = ['INFO_VISU_Z1', 'INFO_VISU_Z2', 'INFO_VISU_Z3']
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO 1D Template [v] {0}'.format(objname), zoom_params)
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def red_tellu_temp_s1dw(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get the header
    header = fits.getheader(filename, ext=0)
    # get the object name
    objname = header.get(params['KW_OBJNAME'][0], 'Unknown')
    # get table
    table = Table.read(filename, hdu='TELLU_TEMP_S1DW')
    # get the data for this plot
    wave = np.array(table['wavelength'])
    flux = np.array(table['flux'])
    # set up dataset
    dataset = dict()
    dataset['Template flux'] = {
        'x': wave, 'y': flux,
        'kwargs': {'color': 'black', 'alpha': 0.7}
    }
    # set zoom from parameters
    zoom_params = ['INFO_VISU_Z1', 'INFO_VISU_Z2', 'INFO_VISU_Z3']
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO 1D Template [w] {0}'.format(objname), zoom_params)
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def lbl_rdb(params: ParamDict, filename: str, identity: str = ''):

    # get the basename
    basename = os.path.basename(filename)
    # header
    header = None
    # ----------------------------------------------------------------------
    # deal with identity
    if identity == 'LBL_RDB':
        # deal with identity
        objname_template = basename.removeprefix('lbl_').removesuffix('.rdb')
        # load rdb file
        rdb_table = Table.read(filename, format='ascii.rdb', fast_reader=False)
    elif identity == 'LBL_RDB2':
        # deal with identity
        objname_template = basename.removeprefix('lbl2_').removesuffix('.rdb')
        # load rdb file
        rdb_table = Table.read(filename, format='ascii.rdb', fast_reader=False)
    elif identity == 'LBL_DRIFT':
        # deal with identity
        objname_template = 'DRIFT'
        # load rdb file
        rdb_table = Table.read(filename, format='ascii.rdb', fast_reader=False)
    elif identity == 'LBL_RDB_DRIFT':
        # deal with identity
        objname_template = basename.removeprefix('lbl_').removesuffix('_drift.rdb')
        # load rdb file
        rdb_table = Table.read(filename, format='ascii.rdb', fast_reader=False)
    elif identity == 'LBL_RDB2_DRIFT':
        # deal with identity
        objname_template = basename.removeprefix('lbl2_').removesuffix('_drift.rdb')
        # load rdb file
        rdb_table = Table.read(filename, format='ascii.rdb', fast_reader=False)
    elif identity == 'LBL_RDB_FITS':
        # deal with identity
        objname_template = basename.removeprefix('lbl_').removesuffix('.fits')
        # load fits file
        rdb_table = Table.read(filename, format='fits', hdu='RDB')
        # 
        header = fits.getheader(filename, ext='RDB')
    else:
        raise ValueError('Unknown identity {0} in lbl_rdb plot function'
                         .format(identity))
    # ----------------------------------------------------------------------
    # get lbl rdb properties
    lbl_props = get_lbl_rdb_props(params, rdb_table)
    # ----------------------------------------------------------------------
    # plot lbl rdb
    plot_lbl_rdb(params, filename, header, lbl_props, objname_template)
    # plot lbl rdb thumbnail
    plot_lbl_rdb_thumbnail(params, filename, lbl_props)



def lbl_fits(params: ParamDict, filename: str, identity: str = ''):
    # we don't use identity here
    _ = identity
    # get the header
    header = fits.getheader(filename)
    # load rdb table from fits
    fits_table = Table.read(filename)
    # ----------------------------------------------------------------------
    # get fiber
    fiber = get_main_fiber()
    # get objname template from split after fiber
    objname_template = filename.split(fiber)[-1].split('.fits')[0]
    # ----------------------------------------------------------------------
    # construct target dictionary
    target_dict = make_target_dict(params, filename, header)
    # set up figure, tables and get plotting frames
    fig = plt.figure(figsize=(15, 15), dpi=300)

    gs = fig.add_gridspec(
        nrows=4,
        ncols=1,
    )
    frames = []
    # Target info
    frames.append(fig.add_subplot(gs[0]))
    draw_kv_table(frames[0], 'Target Information', target_dict)
    # CCF: 3 panels
    frames.append(fig.add_subplot(gs[1]))
    frames.append(fig.add_subplot(gs[2]))
    frames.append(fig.add_subplot(gs[3]))
    # get columns from fits table
    wavestart = np.array(fits_table['WAVE_START'])
    waveend = np.array(fits_table['WAVE_END'])
    wave = 0.5 * (wavestart + waveend)
    dv = np.array(fits_table['dv']) / 1000.0
    sdv = np.array(fits_table['sdv']) / 1000.0
    d2v = np.array(fits_table['d2v'])
    sd2v = np.array(fits_table['sd2v'])
    d3v = np.array(fits_table['d3v'])
    sd3v = np.array(fits_table['sd3v'])
    # calculate mask for points with sdv > 300 m/s
    mask = sdv < (300 / 1000.0)
    mask_on = '$\sigma$ < 300 m/s'
    mask_off = '$\sigma$ > 300 m/s'
    # plot three panels from lbl fits
    lbl_trumpet_plot(frames[1], wave, dv, sdv, mask, mask_on, mask_off,
                     on_color='#1f4e79', off_color='#6fa8dc',
                     ylabel='dv [km/s]')
    lbl_trumpet_plot(frames[2], wave, d2v, sd2v, mask, mask_on, mask_off,
                     on_color='#b45f06', off_color='#f6b26b',
                     ylabel='d2v')
    lbl_trumpet_plot(frames[3], wave, d3v, sd3v, mask, mask_on, mask_off,
                     on_color='#38761d', off_color='#93c47d',
                     ylabel='d3v')
    # set the title of the top frame
    frames[1].set_title('LBL Velocities {0}'.format(objname_template))
    # save/show etc
    plotend(params, filename)
    # ----------------------------------------------------------------------
    # plot lbl fits thumbnail
    # ----------------------------------------------------------------------
    # set up figure
    dpi = 100
    fig = plt.figure(figsize=(256 / dpi, 256 / dpi), dpi=dpi)
    frame = fig.add_subplot(1, 1, 1)

    lbl_trumpet_plot(frame, wave, dv, sdv, mask, mask_on, mask_off,
                     on_color='#1f4e79', off_color='#6fa8dc',
                     low_percentile=1.0, high_percentile=99.0)
    plt.tight_layout()
    # save/show etc
    plotend(params, filename, thumbnail=True)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================

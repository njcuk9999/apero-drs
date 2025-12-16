#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-12-12 at 14:10

@author: cook
"""
import os
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.table import Table

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.core import drs_text
from apero.core import math as mp
from apero.tools.module.ari import ari_core

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
        filepath = os.path.dirname(params['INPUTS']['PATH'])
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
            # save file to disk
            print('Saving figure to {0}'.format(filename))
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
                     header: fits.Header) -> Dict[str, Any]:
    # get all keys from header in the parameter format
    hdict = dict()
    for key in params.keys():
        if key.startswith('KW_'):
            hdict[key] = header.get(params[key][0], 'N/A')
    # push the strings into target dictionary for formatting
    target_dict = dict()
    target_dict['PATH'] = os.path.dirname(filename)
    target_dict['FILENAME'] = os.path.basename(filename)

    # add the header keys
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
                        ) -> Dict[str, Any]:
    fig = plt.figure(figsize=(15, 15), dpi=300)

    gs = fig.add_gridspec(
        nrows=3,
        ncols=3,
    )
    frames = dict()
    # Target info
    frames['TARGET'] = fig.add_subplot(gs[0, :])
    draw_kv_table(frames['TARGET'], 'Target Information', target_dict)
    # Spectrum: 4 panels
    frames['MAIN'] = fig.add_subplot(gs[1, :])
    frames['ZOOM1'] = fig.add_subplot(gs[2, 0])
    frames['ZOOM2'] = fig.add_subplot(gs[2, 1])
    frames['ZOOM3'] = fig.add_subplot(gs[2, 2])
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
                  title: str):
    # construct target dictionary
    target_dict = make_target_dict(params, filename, header)
    # set up figure, tables and get plotting frames
    frames = spec_plus_zoom_page(target_dict)

    # get zoom limits
    zoom1 = params.listp('INFO_VISU_Z1', dtype=float)
    zoom2 = params.listp('INFO_VISU_Z2', dtype=float)
    zoom3 = params.listp('INFO_VISU_Z3', dtype=float)

    # plot the spectra
    for label in dataset:
        # get parameters for each dataset to plot
        x = dataset[label]['x']
        y = dataset[label]['y']
        pkwargs = dataset[label]['kwargs']
        # plot the main plot
        frames['MAIN'].plot(x, y, **pkwargs, label=label)
        frames['MAIN'].legend(loc=0)
        # plot the zooms
        frames['ZOOM1'] = plot_zoom(frames['ZOOM1'], x, y, zoom1, **pkwargs)

        frames['ZOOM2'] = plot_zoom(frames['ZOOM2'], x, y, zoom2, **pkwargs)
        frames['ZOOM3'] = plot_zoom(frames['ZOOM3'], x, y, zoom3, **pkwargs)

    # add legend
    frames['MAIN'].set_title(title)
    frames['MAIN'].set_xlabel('Wavelength [nm]')
    frames['MAIN'].set_ylabel('Flux')
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
        pkwargs = dataset[label]['kwargs']
        frame.plot(x, y, **pkwargs)
    # save/show etc
    plotend(params, filename, thumbnail=True)


# =============================================================================
# Define ccf functions
# =============================================================================
def ccf_page(target_dict: Dict[str, Any]) -> Dict[str, Any]:
    # ---------------------------------------------------------------------

    fig = plt.figure(figsize=(15, 15), dpi=300)

    gs = fig.add_gridspec(
        nrows=4,
        ncols=1,
    )
    frames = dict()
    # Target info
    frames['TARGET'] = fig.add_subplot(gs[0])
    draw_kv_table(frames['TARGET'], 'Target Information', target_dict)
    # Spectrum: 4 panels
    frames['CCF1'] = fig.add_subplot(gs[1])
    frames['CCF2'] = fig.add_subplot(gs[2])
    frames['CCF3'] = fig.add_subplot(gs[3])
    # loop around frames to plot spectrum
    for fkey in frames.keys():
        frame = frames[fkey]
        frame.set_facecolor(COLORS['panel_bg'])

    return frames


def plot_ccf(params: ParamDict, filename: str, header: fits.Header,
             ccf_props: Dict[str, Any], title: str):
    # construct target dictionary
    target_dict = make_target_dict(params, filename, header)
    # set up figure, tables and get plotting frames
    frames = ccf_page(target_dict)
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
    frame.plot(rv_vec, med_ccf, color='orange', alpha=0.4)
    # save/show etc
    plotend(params, filename, thumbnail=True)


# =============================================================================
# Define file type functions (one per file type)
# =============================================================================
def plot_drs_post_e(params: ParamDict, filename: str):
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
        'kwargs': {'color': 'blue', 'alpha': 0.7, 'label': 'Extracted Spectrum'}
    }
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO extracted spectrum')
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def plot_drs_post_t(params: ParamDict, filename: str):
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
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO telluric corrected extracted spectrum')
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def post_drs_post_s(params: ParamDict, filename: str):
    # get main fiber
    fiber = get_main_fiber()
    # get the header
    header = fits.getheader(filename, extname='UniformVelocity'.format(fiber))
    # get the data for this plot
    table = Table.read(filename, hdu='UniformVelocity')
    # get columns from table
    wave = np.array(table['Wave'])
    spectrum = np.array(table['Flux{0}'.format(fiber)])
    tcorr = np.array(table['Flux{0}TelluCorrected'.format(fiber)])
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
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO 1D spectrum')
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def plot_drs_post_p(params: ParamDict, filename: str):
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
    # plot spectrum
    plot_spectrum(params, filename, dataset, header,
                  'APERO polarimetry spectru')
    # plot spectrum thumbnail
    plot_spectrum_thumbnail(params, filename, dataset)


def post_drs_post_v(params: ParamDict, filename: str):
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
    rv_vec = ccf_props['rv_vec'] = table['RV']
    # storage for the CCF vectors
    all_ccf = np.zeros((n_orders, len(rv_vec)))
    # loop around all other files, load them and load into all_ccf
    for row in range(n_orders):
        # get the combined CCF for this file
        ccf_row = table['CCF{0:02d}'.format(row)]
        # normalize ccf
        ccf_row = ccf_row / np.nanmedian(ccf_row)
        # push into vector
        all_ccf[row] = ccf_row
    # -----------------------------------------------------------------
    # get the 1 and 2 sigma limits
    lower_sig1 = 100 * (0.5 - mp.normal_fraction(1) / 2)
    upper_sig1 = 100 * (0.5 + mp.normal_fraction(1) / 2)
    lower_sig2 = 100 * (0.5 - mp.normal_fraction(2) / 2)
    upper_sig2 = 100 * (0.5 + mp.normal_fraction(2) / 2)
    # y1 1sig is the 15th percentile of all ccfs
    ccf_props['y1_1sig'] = np.nanpercentile(all_ccf, lower_sig1, axis=0)
    # y2 1sig is the 84th percentile of all ccfs
    ccf_props['y2_1sig'] = np.nanpercentile(all_ccf, upper_sig1, axis=0)
    # y1 1sig is the 15th percentile of all ccfs
    ccf_props['y1_2sig'] = np.nanpercentile(all_ccf, lower_sig2, axis=0)
    # y2 1sig is the 84th percentile of all ccfs
    ccf_props['y2_2sig'] = np.nanpercentile(all_ccf, upper_sig2, axis=0)
    # med ccf is the median ccf (50th percentile)
    ccf_props['med_ccf'] = np.nanmedian(all_ccf, axis=0)
    # get other properties using the ari core function
    ccf_props = ari_core.fit_ccf(ccf_props)
    # plot ccf
    plot_ccf(params, filename, header, ccf_props, 'APERO CCF spectrum')
    # plot ccf thumbnail
    plot_ccf_thumbnail(params, filename, ccf_props)


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

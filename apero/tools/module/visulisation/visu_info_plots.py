#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-12-12 at 14:10

@author: cook
"""
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from astropy.io import fits

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.core import drs_text


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
    'title': '#F57C00',      # deep orange
    'row_even': '#FFF3CD',   # pastel yellow
    'row_odd': '#FFE0B2',    # pastel orange
    'panel_bg': '#FFF8E1',   # spectrum background
    'key': '#E3F2FD',        # header key
    'value': '#E8F5E9',      # header value
    'comment': '#FCE4EC',    # header comment
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


# =============================================================================
# Define general functions
# =============================================================================
def plotend(params: ParamDict, filename):

    # deal with show vs save
    if params['INPUTS']['INFOSAVE']:
        pkind = 'summary'
    else:
        pkind = 'show'
    # get path
    if drs_text.null_text(params['INPUTS']['INFOPATH'], ['None', 'Null', '']):
        filepath = params['INPUTS']['INFOPATH']
    else:
        filepath = params['INPUTS']['PATH']
    # remove any extension
    basename = os.path.splitext(os.path.basename(filename))[0]
    # get full plot path
    filename = os.path.join(filepath, basename) + '.png'
    # deal with summary plots
    if pkind == 'summary':
        # 1. save to file
        print('Saving figure to {0}'.format(filename))
        plt.savefig(filename)
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


def draw_header_table(ax, title, header):
    ax.axis('off')
    # push header keys/values/comments into rows
    rows = []
    for key in header:
        value = header[key]
        try:
            comment = header.comments[key]
        except KeyError:
            comment = 'N/A'
        rows.append([key, value, comment])
    # push into table
    table = ax.table(
        cellText=rows,
        colLabels=[title, 'Value', 'Comment'],
        loc='center',
        cellLoc='left'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.3)

    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor(COLORS['title'])
            cell.set_text_props(color='white', weight='bold')
        else:
            if c == 0:
                cell.set_facecolor(COLORS['key'])
            elif c == 1:
                cell.set_facecolor(COLORS['value'])
            else:
                cell.set_facecolor(COLORS['comment'])


def fig_height_for_rows(n_rows, row_h=0.35, base=6):
    return base + n_rows * row_h


def spec_plus_zoom_page(target_dict: Dict[str, Any],
                        header_dict: Dict[str, Tuple[Any, str]]
                        ) -> Dict[str, Any]:
    n_header = len(header_dict)
    fig_h = fig_height_for_rows(n_header)

    fig = plt.figure(
        figsize=(14, fig_h),
        dpi=200
    )

    gs = fig.add_gridspec(
        nrows=4,
        ncols=3,
        height_ratios=[1.2, 2.5, 1.5, 1.5],
        hspace=0.6
    )
    frames = dict()
    # Target info
    frames['TARGET'] = fig.add_subplot(gs[0, :])
    draw_kv_table(frames['TARGET'], 'Target Information', target_dict)
    # Spectrum: 4 panels
    frames['MAIN']  = fig.add_subplot(gs[1, :])
    frames['ZOOM1']  = fig.add_subplot(gs[2, 0])
    frames['ZOOM2'] = fig.add_subplot(gs[2, 1])
    frames['ZOOM3'] = fig.add_subplot(gs[2, 2])
    # loop around frames to plot spectrum
    for fkey in frames.keys():
        frame = frames[fkey]
        frame.set_facecolor(COLORS['panel_bg'])

    # Header section
    frames['HEADER'] = fig.add_subplot(gs[3, :])
    draw_header_table(frames['HEADER'], 'Header', header_dict)

    return frames


def make_target_dict(params: ParamDict, header: fits.Header) -> Dict[str, Any]:

    # get all keys from header in the parameter format
    hdict = dict()
    for key in params.keys():
        if key.startswith('KW_'):
            hdict[key] = header.get(params[key][0], 'N/A')
    # push the strings into target dictionary for formatting
    target_dict  = dict()
    for key in T_HKEYS:
        target_dict[key] = T_HKEYS[key].format(**hdict)
    # return the target dictionary
    return target_dict


# =============================================================================
# Define file type functions (one per file type)
# =============================================================================
def plot_drs_post_e(params: ParamDict, filename: str):

    # update instrument
    instrument = str(base.IPARAMS['INSTRUMENT'])
    # load pconst
    pconst = constants.pload(instrument=instrument)
    # get science fiber
    science_fibers, _ = pconst.FIBER_KINDS()

    fiber = science_fibers[0]

    # load header
    header = fits.getheader(filename, extname='Flux{0}'.format(fiber))
    # construct target dictionary
    target_dict = make_target_dict(params, header)

    # set up figure, tables and get plotting frames
    frames = spec_plus_zoom_page(target_dict, header)

    # get the data for this plot
    wave = fits.getdata(filename, extname='Wave{0}'.format(fiber))
    blaze = fits.getdata(filename, extname='Blaze{0}'.format(fiber))
    data = fits.getdata(filename, extname='Flux{0}'.format(fiber))

    # plot the spectra
    frames['MAIN'].plot(wave.ravel(), data.ravel()/blaze.ravel())
    frames['ZOOM1'].plot(wave.ravel(), data.ravel()/blaze.ravel())
    frames['ZOOM2'].plot(wave.ravel(), data.ravel()/blaze.ravel())
    frames['ZOOM3'].plot(wave.ravel(), data.ravel()/blaze.ravel())
    # add legend
    frames['MAIN'].set_title('APERO extracted spectrum')
    frames['MAIN'].set_xlabel('Wavelength [nm]')
    frames['MAIN'].set_ylabel('Flux')

    plotend(params, filename)



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

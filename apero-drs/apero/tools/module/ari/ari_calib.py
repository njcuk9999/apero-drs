#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-04-23 at 12:15

@author: cook
"""
import os
from typing import Any, Dict, List, Union

import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy.io import fits

from aperocore.constants import load_functions
from apero.instruments import select
from apero.base import base as apero_base
from aperocore.constants import param_functions
from apero.core import drs_database
from aperocore.core import drs_log
from apero.tools.module.documentation import drs_markdown
from apero.base.base import TQDM as tqdm
from apero.tools.module.ari import ari_pages
from apero.tools.module.ari import ari_plot

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.ari.ari_calib.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get ParamDict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define calibration keys
# =============================================================================
class CalibKey:
    def __init__(self, name: str, kind: str, label: str = None,
                 dtype: bool = float):
        self.name = name
        self.kind = kind
        self.label = label
        self.dtype = dtype

    def get_key(self, params, hdr, dim1 = 0, dim2 =0):
        # get key name
        if self.name in params:
            hkey = params[self.name][0]
        else:
            hkey = self.name
        # deal with list keys
        if '{' in hkey and '}' in hkey:
            if hkey.count('{') == 1:
                hkey = hkey.format(dim1)
            else:
                hkey = hkey.format(dim1, dim2)
        # deal with typing
        if self.dtype == float:
            null = np.nan
        else:
            null = ''
        # return with a default
        return hdr.get(hkey, null)


CALIB_KEYS = dict()
CALIB_KEYS['BASENAME'] = CalibKey('BASENAME', kind='key')
CALIB_KEYS['KW_OUTPUT'] = CalibKey('KW_OUTPUT', kind='hdr',
                                   label='APERO file type')
CALIB_KEYS['KW_MID_OBS_TIME'] = CalibKey('KW_MID_OBS_TIME', kind='hdr',
                                         label='mid exposure time [MJD]')
CALIB_KEYS['KW_SHAPE_DX'] = CalibKey('KW_SHAPE_DX', kind='hdr',
                                     label='Shape X')
CALIB_KEYS['KW_SHAPE_DY'] = CalibKey('KW_SHAPE_DY', kind='hdr',
                                     label='Shape Y')
CALIB_KEYS['KW_SHAPE_A'] = CalibKey('KW_SHAPE_A', kind='hdr', label='Shape A')
CALIB_KEYS['KW_SHAPE_B'] = CalibKey('KW_SHAPE_B', kind='hdr', label='Shape B')
CALIB_KEYS['KW_SHAPE_C'] = CalibKey('KW_SHAPE_C', kind='hdr', label='Shape C')
CALIB_KEYS['KW_SHAPE_D'] = CalibKey('KW_SHAPE_D', kind='hdr', label='Shape D')

CALIB_KEYS['KW_EXT_NBO'] = CalibKey('KW_EXT_NBO', kind='hdr')
CALIB_KEYS['KW_WFP_DRIFT'] = CalibKey('KW_WFP_DRIFT', kind='hdr',
                                      label='Wavesol abs CCF FP drift [km/s]')
CALIB_KEYS['KW_CAVITY_WIDTH'] = CalibKey('KW_CAVITY_WIDTH', kind='hdr',
                                         label='Wave cavity c0')
CALIB_KEYS['WAVE_CENT_X'] = CalibKey('WAVE_CENT_X', kind='key')
CALIB_KEYS['ABSPATH'] = CalibKey('ABSPATH', kind='key')

# set required calibrations
REQ_CALS = ['SHAPEL', 'WAVE_NIGHT']
REQ_FIBER = [False, True]

# =============================================================================
# Define functions
# =============================================================================
def add_calib_page(params: ParamDict, recipe_table: ari_pages.TableFile):
    """
    Adds calibration page to ARI

    :param params: ParamDict, parameter dictionary of constants
    :param recipe_table: AriTable, table containing calibration pages info

    :return: None, writes calibration rst to disk
    """
    # set where this page is relative to the ari/home directory
    rel_root = '../../../ari/home/'
    # ---------------------------------------------------------------------
    # make a markdown page for the table
    calib_page = drs_markdown.MarkDownPage(recipe_table.ref)
    # add object table
    title = f'{recipe_table.name} ({recipe_table.user})'
    calib_page.add_title(title)
    # add page access
    calib_page.add_html(ari_pages.add_page_access(recipe_table.params,
                                                  rel_root))
    # -----------------------------------------------------------------
    # Add basic text
    # construct text to add
    calib_page.add_text(f'This is the APERO Reduction Interface (ARI) '
                        f'for the reduction: {recipe_table.user}')
    calib_page.add_newline()
    calib_page.add_text('This is the calibration monitoring page.')
    calib_page.add_newline()
    calib_page.add_text('If you have any issues please report using '
                        '`this sheet <https://docs.google.com/spreadsheets/d/1Ea_WEFTlTCbth'
                        'R24aaQm4KaleIteLuXLgn4RiNBnEqs/edit?usp=sharing>`_')
    calib_page.add_newline()
    calib_page.add_text('Last updated: {0} [UTC]'.format(Time.now()))
    calib_page.add_newline()
    # -----------------------------------------------------------------
    # get calib properties
    calib_props = get_calib_props(params)
    # create plots
    calib_plots = create_plots(params, calib_props)
    # ------------------------------------------------------------------
    # add the debug plots
    for calib_plot in calib_plots:
        # skip plots that are not active (i.e. plotting disabled them)
        if not calib_plot.active:
            continue
        # make a sub section for this debug plot
        calib_page.add_sub_section(calib_plot.name)
        # add the snr plot to the page
        calib_page.add_image('calib_page/' + calib_plot.basename, align='left')
        # add debug plot description
        calib_page.add_text(calib_plot.description)
        # add a new line
        calib_page.add_newline(2)
    # -----------------------------------------------------------------
    # write table page
    print('Writing table page: {0}'.format(recipe_table.rst_path))
    calib_page.write_page(recipe_table.rst_path)
    return 0


def create_plots(params: ParamDict, calib_props: Dict[str, Dict[str, Any]]
                 ) -> List[ari_plot.DebugPlot]:
    """
    Create the plots that go on the ARI calibration page

    :param params: ParamDict, parameter dictionary of constants
    :param calib_props: dict, calibration properties

    :return: List[ari_plot.DebugPlot], list of plots, for adding to the page
    """
    # set up the object page
    calib_save_path = params['TOOLS.ARI.CALIB_PAGE']
    ari_user = params['TOOLS.ARI.USER']
    # storage for return
    calib_plots = []
    # ---------------------------------------------------------------------
    # add shape plot
    calib_shape = ari_plot.DebugPlot()
    calib_shape.name = 'Shape QC plot'
    calib_shape.basename = f'calib_shape_plot_{ari_user}.png'
    calib_shape.plot = ari_plot.shape_qc_plot_plot
    calib_shape.description = ('Shape parameters varying in time.'
                               'dx is a shift along the order, dy is a '
                               'shift across orders, [[A,B],[C,D]] is an '
                               'affine transformation matrix.')
    calib_shape.active = True
    calib_plots.append(calib_shape)
    # ---------------------------------------------------------------------
    # add wfpdrift plot
    calib_wfpdrift = ari_plot.DebugPlot()
    calib_wfpdrift.name = 'wfpdrift plot'
    calib_wfpdrift.basename = (f'calib_wfpdrift_plot_{ari_user}.png')
    calib_wfpdrift.plot = ari_plot.calib_mjd_wfpdrift_plot
    calib_wfpdrift.description = ('Wavelength solution absolute CCF FP '
                                  'Drift [km/s]')
    calib_wfpdrift.active = True
    calib_plots.append(calib_wfpdrift)
    # ---------------------------------------------------------------------
    # add wcav000 plot
    calib_wcav000 = ari_plot.DebugPlot()
    calib_wcav000.name = 'Wave cavity (c0) plot'
    calib_wcav000.basename = (f'calib_wcav000_plot_{ari_user}.png')
    calib_wcav000.plot = ari_plot.calib_mjd_wcav000_plot
    calib_wcav000.description = 'Wave cavity polynomial coeffs=0'
    calib_wcav000.active = True
    calib_plots.append(calib_wcav000)
    # ---------------------------------------------------------------------
    # add wave cent plot
    calib_wcent = ari_plot.DebugPlot()
    calib_wcent.name = 'Wave centroid plot'
    calib_wcent.basename = (f'calib_wcentplot_{ari_user}.png')
    calib_wcent.plot = ari_plot.calib_mjd_wcent_plot
    calib_wcent.description = 'Wave centroid plot'
    calib_wcent.active = True
    calib_plots.append(calib_wcent)
    # ---------------------------------------------------------------------
    # plot the debug plots
    # ---------------------------------------------------------------------
    # loop around plots and plot
    for calib_plot in calib_plots:
        # set the plot title
        plot_title = f'{calib_plot.name}'
        # get the plot path
        calib_plot.path = os.path.join(calib_save_path, calib_plot.basename)
        # plot the debug plot
        calib_plot.plot(calib_props, calib_plot.path, plot_title)
    # ---------------------------------------------------------------------
    return calib_plots


# =============================================================================
# Define functions
# =============================================================================
def get_calib_props(params: ParamDict) -> Dict[str, Dict[str, Any]]:
    """
    Get calibration properties

    :param params: ParamDict, calibration properties

    :return: dict, calibration properties
    """
    # storage for return
    calib_props = dict()
    # get previous files
    calib_save_path = params['TOOLS.ARI.CALIB_PAGE']
    ari_user = params['TOOLS.ARI.USER']
    calib_key_file = os.path.join(calib_save_path, f'calib_keys_{ari_user}.fits')
    # get orders
    cal_orders = params['TOOLS.ARI.CAL_ORDERS']
    # -------------------------------------------------------------------------
    # get the previous calib files (from storage) or create empty
    calib_data = get_prev_data(calib_key_file)
    # -------------------------------------------------------------------------
    # get a list of calibration files
    calib_files = get_calib_files(params)
    # -------------------------------------------------------------------------
    # populate calib data with new entries (read headers)
    calib_data = get_calib_hkeys(params, calib_data, calib_files)
    # -------------------------------------------------------------------------
    # add wave centers (WAVE_CENT_X)
    calib_data = get_wave_cent_x(params, calib_data)
    # -------------------------------------------------------------------------
    # save calib data to disk
    WLOG(params, '', 'Writing file {0}'.format(calib_key_file))
    Table(calib_data).write(calib_key_file, overwrite=True)
    # -------------------------------------------------------------------------
    # sort into a more usable form for plotting
    for cal in REQ_CALS:
        calib_props[cal] = dict()
        calib_props[cal]['HDICT'] = dict()
        calib_props[cal]['LABEL'] = dict()
        calib_props[cal]['OTHER'] = dict(ORDERS=cal_orders)
        # get a mask for this calibration type
        mask = calib_data['KW_OUTPUT'] == cal
        # add each column into our sub-dictionary
        for key in CALIB_KEYS:

            calib_props[cal]['HDICT'][key] = calib_data[key][mask]
            calib_props[cal]['LABEL'][key] = CALIB_KEYS[key].label
    # return the props
    return calib_props


def get_prev_data(calib_key_file: str) -> Dict[str, list]:
    """
    Get previous data stored so we don't have to re-open every file

    :param calib_key_file: path to calibration keys file

    :return dictionary of columns for adding to calib props
    """
    # -------------------------------------------------------------------------
    # empty existing or start new calib file dictionary
    calib_data = dict()
    # -------------------------------------------------------------------------
    # populate from disk if we have it
    if os.path.exists(calib_key_file):
        # read file from disk
        calib_table = Table.read(calib_key_file)
        # make sure if we've added new header keys we unset calib_files
        # (and re-calculate)
        recalculate = False
        # loop around keys
        for key in CALIB_KEYS:
            icalib = CALIB_KEYS[key]

            if icalib.name in calib_table.colnames:
                calib_data[icalib.name] = list(calib_table[icalib.name])
            else:
                recalculate = True
                break
    else:
        recalculate = True
    # -------------------------------------------------------------------------
    # reset (or start) calib files as empty
    if recalculate:
        # empty existing or start new calib file dictionary
        calib_data = dict()
        # populate with empty columns
        for key in CALIB_KEYS:
            icalib = CALIB_KEYS[key]
            calib_data[icalib.name] = []
    # -------------------------------------------------------------------------
    return calib_data


def get_calib_files(params: ParamDict) -> List[str]:
    """
    From the file index database get a list of all calibration files
    given in REQ_CALS

    :param params: ParamDict, parameter dictionary of constants

    :return: list of calibration files
    """
    # load pconst
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    sci_fibers, _ = pconst.FIBER_KINDS()
    # storage for output
    calib_files = []
    # get and load the file index database
    findexdb = drs_database.FileIndexDatabase(params)
    findexdb.load_db()
    # get required calibration files
    for it, cal in enumerate(REQ_CALS):
        # set up condition
        condition = f'BLOCK_KIND="red" AND KW_OUTPUT="{cal}"'
        # deal with requiring fiber
        if REQ_FIBER[it]:
            condition += f' AND KW_FIBER="{sci_fibers[0]}"'
        # get absolute file path for file
        abspath = list(findexdb.get_entries('ABSPATH', condition=condition))
        calib_files += abspath
    # return all files
    return calib_files


def get_calib_hkeys(params: ParamDict, calib_data: Dict[str, Any],
                    calib_files: List[str]) -> Dict[str, Any]:
    """
    From the files either keep the data already existing or load the file
    from disk and populate the columns using the headers

    :param params: ParamDict, parameter dictionary of constants
    :param calib_data: dict, calibration data (previously loaded from disk)
    :param calib_files: list, list of calibration files

    :return: dict, calibration properties
    """
    # print progress
    WLOG(params, '', 'Loading calibration data')
    # loop around all files
    for filename in tqdm(calib_files):
        basename = os.path.basename(filename)
        if basename in calib_data['BASENAME']:
            continue
        else:
            # load file header
            try:
                hdr = fits.getheader(filename)
            except Exception as _:
                continue
            # loop around keys
            for key in CALIB_KEYS:
                icalib = CALIB_KEYS[key]
                if icalib.kind == 'hdr':
                    value = icalib.get_key(params, hdr)
                    calib_data[key].append(value)
                elif key == 'BASENAME':
                    calib_data[key].append(basename)
                elif key == 'ABSPATH':
                    calib_data[key].append(filename)
                elif key == 'WAVE_CENT_X':
                    calib_data[key].append(None)
                else:
                    calib_data[key].append(np.nan)
    # convert to numpy arrays
    for key in CALIB_KEYS:
        if key != 'WAVE_CENT_X':
            calib_data[key] = np.array(calib_data[key])

    return calib_data


def get_wave_cent_x(params: ParamDict, calib_data: Dict[str, np.ndarray]):
    """
    Add a special column (for WAVE_NIGHT files) which is the wavelength for the
    central pixel of every order - either loaded from file or remembered
    from previous loading

    :param params: ParamDict, parameter dictionary of constants
    :param calib_data: dict, calibration data

    :return: dict, calibration properties
    """
    # deal with no wave data
    if np.sum(np.isfinite(calib_data['KW_EXT_NBO'])) == 0:
        WLOG(params, 'warning', 'No WAVE_NIGHT files. Skipping WAVE_CENT_X')
        return calib_data
    # get the nbo
    nbo = int(np.nanmean(calib_data['KW_EXT_NBO']))
    # loop around
    for it in tqdm(range(len(calib_data['BASENAME']))):
        # only do the rest for wave night files
        if calib_data['KW_OUTPUT'][it] != 'WAVE_NIGHT':
            # fill with nans (to have correct shape)
            calib_data['WAVE_CENT_X'][it] = np.full(nbo, np.nan)
            continue
        # if data isn't None we already have this data
        if calib_data['WAVE_CENT_X'][it] is not None:
            continue
        # load the file
        wavemap = np.array(fits.getdata(calib_data['ABSPATH'][it]))
        # get central pixel
        cent_x = wavemap.shape[1] // 2
        # get the central pixels of every order
        wave_cents = wavemap[:, cent_x]
        # push into calib_data
        calib_data['WAVE_CENT_X'][it] = wave_cents

    # push into a single numpy array
    calib_data['WAVE_CENT_X'] = np.array(calib_data['WAVE_CENT_X'])
    # return the updated calib_data
    return calib_data


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

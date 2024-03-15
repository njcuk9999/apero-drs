#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-23 at 15:52

@author: cook
"""
import glob
import os
from typing import Any, Dict, List, Tuple, Union

import numpy as np
from astropy.table import Table
from astropy.time import Time
from bs4 import BeautifulSoup

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.io import drs_path
from apero.tools.module.ari import ari_core
from apero.tools.module.ari import ari_find
from apero.tools.module.documentation import drs_markdown
from apero.tools.module.error import error_html

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.ari.ari_core.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# -----------------------------------------------------------------------------
# Get ParamDict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# Get ARI core classes
AriObject = ari_core.AriObject
AriRecipe = ari_core.AriRecipe
FileType = ari_core.FileType


# =============================================================================
# Define classes
# =============================================================================
class TableFile:
    def __init__(self, name: str, params: ParamDict):
        if name == 'null':
            self.null = True
            return
        self.null = False
        self.name = name.lower()
        self.user = params['ARI_USER']
        self.title = f'{name.lower()} ({self.user})'
        self.machinename = self.name.replace(' ', '_').upper()
        self.params = params
        self.ref: str = self.user + '_' + self.machinename
        self.csv_filename = name.replace(' ', '_') + '.csv'
        self.rst_filename = self.csv_filename.replace('.csv', '.rst')
        # this is just for table files where we generate the html without
        #   sphinx
        self.html_filename = self.csv_filename.replace('.csv', '.html')
        # we need the recipe table page to be in the recipe pages directory
        if 'recipe' in name.lower():
            self.html_path = os.path.join('recipe_pages',
                                          self.html_filename)
        else:
            self.html_path = os.path.join(self.html_filename)

        self.csv_path = os.path.join(params['ARI_DIR'], self.csv_filename)
        self.rst_path = os.path.join(params['ARI_DIR'], self.rst_filename)
        self.rst_ref_path = self.rst_filename
        self.csv_ref_path = self.csv_filename

    @staticmethod
    def null_table(params: ParamDict) -> 'TableFile':
        new = TableFile('null', params)
        new.null = True
        return new

    def make_table(self, table: Union[Table, None]):
        # make a markdown page for the table
        table_page = drs_markdown.MarkDownPage(self.ref)
        # add object table
        title = f'{self.name} ({self.user})'
        table_page.add_title(title)
        # add page access
        table_page.add_html(add_page_access(self.params['ARI_GROUP']))
        # -----------------------------------------------------------------
        # Add basic text
        # construct text to add
        table_page.add_text(f'This is the APERO Reduction Interface (ARI) '
                            f'for the reduction: {self.user}')
        table_page.add_newline()
        table_page.add_text('Please note: Your object may be under another '
                            'name. Please check `here <https://docs.google.com/'
                            'spreadsheets/d/'
                            '1dOogfEwC7wAagjVFdouB1Y1JdF9Eva4uDW6CTZ8x2FM/'
                            'edit?usp=sharing>`_, the name displayed in ARI will '
                            'be the first column [OBJNAME]')
        table_page.add_newline()
        table_page.add_text('If you have any issues please report using '
                            '`this sheet <https://docs.google.com/spreadsheets/d/1Ea_WEFTlTCbth'
                            'R24aaQm4KaleIteLuXLgn4RiNBnEqs/edit?usp=sharing>`_')
        table_page.add_newline()
        table_page.add_text('Last updated: {0} [UTC]'.format(Time.now()))
        table_page.add_newline()
        # deal with column widths for this file type
        if table is not None and len(table) > 0:
            if 'object' in self.name:
                # add the csv version of this table
                table_page.add_csv_table('', self.csv_ref_path,
                                         cssclass='csvtable2')
            elif 'recipe' in self.name:
                # add the recipe tables
                add_recipe_tables(self.params, table, self.machinename)
        else:
            # if we have no table then add a message
            table_page.add_text('No table created.')
        # write table page
        print('Writing table page: {0}'.format(self.rst_path))
        table_page.write_page(self.rst_path)
        # -----------------------------------------------------------------
        # write csv table to file
        if table is not None and len(table) > 0:
            print('Writing csv table: {0}'.format(self.csv_path))
            table.write(self.csv_path, format='ascii.csv', overwrite=True)


# =============================================================================
# Define Object Table functions
# =============================================================================
def make_obj_table(params: ParamDict, object_classes: Dict
                   ) -> TableFile:
    # get the ari user
    ari_user = params['ARI_USER']
    # storage dictionary for conversion to table
    table_dict = dict()
    # deal with no entries
    if len(object_classes) == 0:
        return TableFile.null_table(params)
    # get the first instance (for has polar)
    key = list(object_classes.keys())[0]
    object_class0 = object_classes[key]
    # start columns as empty lists
    for col in ari_core.OBJTABLE_COLS:
        if col in ari_core.POLAR_COLS:
            if object_class0.has_polar:
                table_dict[col] = []
        else:
            table_dict[col] = []
    # -------------------------------------------------------------------------
    # loop around rows in table
    for key in object_classes:
        # get the class for this objname
        object_class = object_classes[key]
        # get the page reference
        page_ref = f'{ari_user}_object_page_{object_class.objname}'
        page_link = drs_markdown.make_url(object_class.objname, page_ref)
        # set the object name
        table_dict['OBJNAME'].append(page_link)
        # set the ra and dec
        table_dict['RA'].append(object_class.ra)
        table_dict['DEC'].append(object_class.dec)
        # set the Teff
        if object_class.teff is None:
            table_dict['TEFF'].append(np.nan)
        else:
            table_dict['TEFF'].append(object_class.teff)
        # set the SpT
        if object_class.sptype is None:
            table_dict['SPTYPE'].append('')
        else:
            table_dict['SPTYPE'].append(object_class.sptype)
        # set the dprtypes
        table_dict['DPRTYPE'].append(object_class.dprtypes)
        # set the raw number of files
        table_dict['RAW'].append(object_class.filetypes['raw'].num)
        # set the number of pp files (passed qc)
        table_dict['PP'].append(object_class.filetypes['pp'].num_passed)
        # set the number of ext files (passed qc)
        table_dict['EXT'].append(object_class.filetypes['ext'].num_passed)
        # set the number of tcorr files (passed qc)
        table_dict['TCORR'].append(object_class.filetypes['tcorr'].num_passed)
        # set the number of ccf files (passed qc)
        table_dict['CCF'].append(object_class.filetypes['ccf'].num_passed)
        # set the number of polar files (passed qc)
        if object_class.has_polar:
            table_dict['POL'].append(object_class.filetypes['polar'].num_passed)
        # set the number of e.fits files
        table_dict['efits'].append(object_class.filetypes['efiles'].num)
        # set the number of t.fits files
        table_dict['tfits'].append(object_class.filetypes['tfiles'].num)
        # set the number of v.fits files
        table_dict['vfits'].append(object_class.filetypes['vfiles'].num)
        # set the number of p.fits files
        if object_class.has_polar:
            table_dict['pfits'].append(object_class.filetypes['pfiles'].num)
        # set the number of lbl files
        table_dict['lbl'].append(object_class.filetypes['lbl.fits'].num)
        # set the last observed value raw file
        table_dict['last_obs'].append(object_class.filetypes['raw'].last.iso)
        # set the last processed value
        if object_class.last_processed is not None:
            table_dict['last_proc'].append(object_class.last_processed.iso)
        else:
            table_dict['last_proc'].append('')
    # -------------------------------------------------------------------------
    # convert this to a table but use the output column names
    out_table = Table()
    # loop around all columns
    for col in list(table_dict.keys()):
        # get the out table column name
        new_col = ari_core.OBJTABLE_COLS[col]
        # push values into out table
        out_table[new_col] = table_dict[col]
    # -------------------------------------------------------------------------
    # make a table file instance
    table_file = TableFile('object table', params)
    # add the table to the table file
    table_file.make_table(out_table)
    # return this instance
    return table_file


# =============================================================================
# Individual Object functions
# =============================================================================
def _add_obj_page(it: int, key: str, params: ParamDict,
                  object_classes: Dict[str, AriObject]):
    # get object
    object_class = object_classes[key]
    # do not recalculate object page if we are not updating
    if not object_class.update:
        return
    # get the object name for this row
    objname = object_class.objname
    # get the ari user
    ari_user = params['ARI_USER']
    # get the page reference
    page_ref = f'{ari_user}_object_page_{objname}'
    # get the table reference
    table_ref = f'{ari_user}_object_table'
    # get the sections references
    object_section_ref = f'object_{ari_user}_objpage_{objname}'
    spectrum_section_ref = f'spectrum_{ari_user}_objpage_{objname}'
    lbl_section_ref = f'lbl_{ari_user}_objpage_{objname}'
    ccf_section_ref = f'ccf_{ari_user}_objpage_{objname}'
    timeseries_section_ref = f'timeseries_{ari_user}_objpage_{objname}'
    # ------------------------------------------------------------------
    # print progress
    msg = '\tCreating page for {0} [{1} of {2}]'
    margs = [objname, it + 1, len(object_classes)]
    WLOG(params, '', msg.format(*margs))
    # ---------------------------------------------------------------------
    # construct path for object
    obj_save_path = os.path.join(params['ARI_OBJ_PAGES'], objname)
    # Make sure directory exists
    if not os.path.exists(obj_save_path):
        os.makedirs(obj_save_path)
    # ---------------------------------------------------------------------
    # populate the header dictionary for this object instance
    # wlog(params, '', f'\t\tPopulating header dictionary')
    object_class.populate_header_dict(params)
    # ---------------------------------------------------------------------
    # create ARI object page
    object_page = drs_markdown.MarkDownPage(page_ref)
    # state that this page does not have a paranet (as it is accessed via table)
    object_page.add_text(':orphan:')
    object_page.add_newline()
    # add title
    object_page.add_title(f'{objname} ({ari_user})')
    # add page access
    object_page.add_html(add_page_access(params['ARI_GROUP']))
    # ---------------------------------------------------------------------
    # Add basic text
    # construct text to add
    object_page.add_text(f'This page was last modified: {Time.now()} (UTC)')
    object_page.add_newline()
    # link back to the table
    # create a table page for this table
    table_ref_url = drs_markdown.make_url('object table', table_ref)
    object_page.add_text(f'Back to the {table_ref_url}')
    object_page.add_newline()
    # ---------------------------------------------------------------------
    # table of contents
    # ---------------------------------------------------------------------
    # Add the names of the sections
    names = ['Target info', 'Spectrum', 'LBL', 'CCF', 'Time series']
    # add the links to the pages
    items = [object_section_ref, spectrum_section_ref, lbl_section_ref,
             ccf_section_ref, timeseries_section_ref]
    # add table of contents
    object_page.add_table_of_contents(items=items, names=names)
    object_page.add_newline(nlines=3)
    # ---------------------------------------------------------------------
    # Target information section
    # ---------------------------------------------------------------------
    objpage_targetinfo(params, object_page, names[0], items[0], object_class)
    # ---------------------------------------------------------------------
    # Spectrum section
    # ---------------------------------------------------------------------
    # print progress
    # wlog(params, '', f'\t\tCreating spectrum section')
    # add spectrum section
    objpage_spectrum(params, object_page, names[1], items[1], object_class)
    # ---------------------------------------------------------------------
    # LBL section
    # ---------------------------------------------------------------------
    # print progress
    # wlog(params, '', f'\t\tCreating LBL section')
    # add LBL section
    objpage_lbl(params, object_page, names[2], items[2], object_class)
    # ---------------------------------------------------------------------
    # CCF section
    # ---------------------------------------------------------------------
    # print progress
    # wlog(params, '', f'\t\tCreating CCF section')
    # add CCF section
    objpage_ccf(params, object_page, names[3], items[3], object_class)
    # ---------------------------------------------------------------------
    # Time series section
    # ---------------------------------------------------------------------
    # print progress
    # wlog(params, '', f'\t\tCreating time series section')
    # add time series section
    objpage_timeseries(params, object_page, names[4], items[4], object_class)
    # ---------------------------------------------------------------------
    # write object page
    # ---------------------------------------------------------------------
    # construct the rst path
    object_page_path = os.path.join(params['ARI_OBJ_PAGES'], objname)
    # construct the rst filename
    rst_filename = f'{objname}.rst'
    # save object page
    object_page.write_page(os.path.join(object_page_path, rst_filename))
    # ------------------------------------------------------------------
    # print progress
    msg = '\tFinished creating page for {0} [{1} of {2}]'
    margs = [objname, it + 1, len(object_classes)]
    WLOG(params, '', msg.format(*margs), colour='magenta')


def add_obj_pages(params: ParamDict, object_classes: Dict[str, AriObject]):
    # -------------------------------------------------------------------------
    # deal with no entries in object table
    if len(object_classes) == 0:
        # print progress
        WLOG(params, '', 'No new objects found in object table')
        # return empty table
        return object_classes
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', 'Creating object pages')
    # set up the arguments for the multiprocessing
    args = [0, '', params, object_classes]
    # get the number of cores
    n_cores = params['ARI_NCORES']
    if n_cores is None:
        raise ValueError('Must define N_CORES in settings or profile')
    # -------------------------------------------------------------------------
    # deal with running on a single core
    if n_cores == 1:
        # change the object column to a url
        for it, key in enumerate(object_classes):
            # combine arguments
            itargs = [it, key] + args[2:]
            # run the pool
            _add_obj_page(*itargs)
    # -------------------------------------------------------------------------
    # deal with running on a single core
    if n_cores == 1:
        # change the object column to a url
        for it, key in enumerate(object_classes):
            # combine arguments
            itargs = [it, key] + args[2:]
            # run the pool
            _add_obj_page(*itargs)
    # -------------------------------------------------------------------------
    elif n_cores > 1:
        if ari_core.MULTI == 'POOL':
            from multiprocessing import get_context
            # list of params for each entry
            params_per_process = []
            for it, key in enumerate(object_classes):
                itargs = [it, key] + args[2:]
                params_per_process.append(itargs)
            # start parellel jobs
            with get_context('spawn').Pool(n_cores, maxtasksperchild=1) as pool:
                pool.starmap(_add_obj_page, params_per_process)
        else:
            from multiprocessing import Process
            # split up groups
            group_iterations, group_keys = [], []
            all_iterations = list(range(len(object_classes)))
            all_keys = list(object_classes.keys())
            ngroups = int(np.ceil(len(object_classes) / n_cores))
            for group_it in range(ngroups):
                start = group_it * n_cores
                end = (group_it * n_cores) + n_cores
                iterations = all_iterations[start:end]
                keys = all_keys[start:end]
                # push into storage
                group_iterations.append(iterations)
                group_keys.append(keys)
            # do the multiprocessing
            for group_it in range(ngroups):
                jobs = []
                # loop around jobs in group
                for group_jt in range(len(group_iterations[group_it])):
                    group_args = [group_iterations[group_it][group_jt],
                                  group_keys[group_it][group_jt]] + args[2:]
                    # get parallel process
                    process = Process(target=_add_obj_page, args=group_args)
                    process.start()
                    jobs.append(process)
                # do not continue until finished
                for pit, proc in enumerate(jobs):
                    proc.join()
    # -------------------------------------------------------------------------
    # return the object table
    return object_classes


def objpage_targetinfo(params: ParamDict, page: Any, name: str, ref: str,
                     object_instance: AriObject):
    # add divider
    # page.add_divider(color=DIVIDER_COLOR, height=DIVIDER_HEIGHT)
    # add a reference to this section
    page.add_reference(ref)
    # add the section heading
    page.add_section(name)
    # ------------------------------------------------------------------
    # get the target parameters
    object_instance.get_target_parameters(params)
    # ------------------------------------------------------------------
    # add stats
    if object_instance.target_stats_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.target_stats_table,
                           cssclass='csvtable2')


def objpage_spectrum(params: ParamDict, page: Any, name: str, ref: str,
                     object_instance: AriObject):
    # add divider
    # page.add_divider(color=DIVIDER_COLOR, height=DIVIDER_HEIGHT)
    # add a reference to this section
    page.add_reference(ref)
    # add the section heading
    page.add_section(name)
    # ------------------------------------------------------------------
    # deal with no spectrum found
    if len(object_instance.filetypes['ext'].files) == 0:
        page.add_text('No spectrum found')
        return
    # ------------------------------------------------------------------
    # get the spectrum parameters
    object_instance.get_spec_parameters(params)
    # ------------------------------------------------------------------
    # add the snr plot
    if object_instance.spec_plot_path is not None:
        # add the snr plot to the page
        page.add_image(object_instance.spec_plot_path, align='left')
        # add a new line
        page.add_newline()
    # ------------------------------------------------------------------
    # add stats
    if object_instance.spec_stats_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.spec_stats_table,
                           cssclass='csvtable2')
    # ------------------------------------------------------------------
    # add request table
    if object_instance.spec_rlink_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.spec_rlink_table,
                           cssclass='csvtable2')
    # ------------------------------------------------------------------
    # add download links
    if object_instance.spec_dwn_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.spec_dwn_table,
                           cssclass='csvtable2')


def objpage_lbl(params: ParamDict, page: Any, name: str, ref: str,
                object_instance: AriObject):
    # add divider
    # page.add_divider(color=DIVIDER_COLOR, height=DIVIDER_HEIGHT)
    # add a reference to this section
    page.add_reference(ref)
    # get the first lbl files
    lbl_files = dict()
    for filetype in ari_core.LBL_FILETYPES:
        if object_instance.filetypes[filetype].num > 0:
            lbl_files[filetype] = object_instance.filetypes[filetype].files
    # ------------------------------------------------------------------
    # deal with no spectrum found
    if len(lbl_files) == 0:
        # add the section heading
        page.add_section(name)
        # print that there is no LBL reduction found
        page.add_text('No LBL reduction found')
        return
    # ------------------------------------------------------------------
    # get the spectrum parameters
    object_instance.get_lbl_parameters(params)
    # ------------------------------------------------------------------
    # loop around the object+template combinations
    for objcomb in object_instance.lbl_combinations:
        # add subsection for the object+template combination
        page.add_section(f'LBL ({objcomb})')
        # add the lbl plot
        if object_instance.lbl_plot_path[objcomb] is not None:
            # add the snr plot to the page
            page.add_image(object_instance.lbl_plot_path[objcomb], align='left')
            # add a new line
            page.add_newline()
        # ------------------------------------------------------------------
        # add stats
        if object_instance.lbl_stats_table[objcomb] is not None:
            # add the stats table
            page.add_csv_table('', object_instance.lbl_stats_table[objcomb],
                               cssclass='csvtable2')
        # ------------------------------------------------------------------
        # add request table
        if object_instance.lbl_rlink_table[objcomb] is not None:
            # add the stats table
            page.add_csv_table('', object_instance.lbl_rlink_table[objcomb],
                               cssclass='csvtable2')
        # ------------------------------------------------------------------
        # add download links
        if object_instance.lbl_dwn_table is not None:
            # add the stats table
            page.add_csv_table('', object_instance.lbl_dwn_table[objcomb],
                               cssclass='csvtable2')


def objpage_ccf(params: ParamDict, page: Any, name: str, ref: str,
                object_instance: AriObject):
    # add divider
    # page.add_divider(color=DIVIDER_COLOR, height=DIVIDER_HEIGHT)
    # add a reference to this section
    page.add_reference(ref)
    # get lbl rdb files
    ccf_files = object_instance.filetypes['ccf'].files
    # ------------------------------------------------------------------
    # deal with no spectrum found
    if len(ccf_files) == 0:
        # add the section heading
        page.add_section(name)
        # print that there is no LBL reduction found
        page.add_text('No CCF files found')
        return
    # ------------------------------------------------------------------
    # add the section heading
    page.add_section(name)
    # ------------------------------------------------------------------
    # get the spectrum parameters
    object_instance.get_ccf_parameters(params)
    # ------------------------------------------------------------------
    # add the ccf plot
    if object_instance.ccf_plot_path is not None:
        # add the snr plot to the page
        page.add_image(object_instance.ccf_plot_path, align='left')
        # add a new line
        page.add_newline()
    # ------------------------------------------------------------------
    # add stats
    if object_instance.ccf_stats_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.ccf_stats_table,
                           cssclass='csvtable2')
    # ------------------------------------------------------------------
    # add request table
    if object_instance.ccf_rlink_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.ccf_rlink_table,
                           cssclass='csvtable2')
    # ------------------------------------------------------------------
    # add download links
    if object_instance.ccf_dwn_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.ccf_dwn_table,
                           cssclass='csvtable2')


def objpage_timeseries(params: ParamDict, page: Any, name: str, ref: str,
                       object_instance: AriObject):
    # add divider
    # page.add_divider(color=DIVIDER_COLOR, height=DIVIDER_HEIGHT)
    # add a reference to this section
    page.add_reference(ref)
    # add the section heading
    page.add_section(name)
    # ------------------------------------------------------------------
    # get the spectrum parameters
    object_instance.get_time_series_parameters(params)
    # ------------------------------------------------------------------
    # add stats
    if object_instance.time_series_stats_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.time_series_stats_table,
                           cssclass='csvtable2')
    # ------------------------------------------------------------------
    # add download links
    if object_instance.time_series_dwn_table is not None:
        # add the stats table
        page.add_csv_table('', object_instance.time_series_dwn_table,
                           cssclass='csvtable2')


# =============================================================================
# Recipe functions
# =============================================================================
def recipe_date_table(table: Table, machine_name: str
                      ) -> Tuple[Table, List[str], List[str], np.ndarray]:
    """
    Create the date table which links to each date page

    :param table: astropy.table.Table, the table of all recipes
    :param machine_name: str, the machine readible name for the table
    :return:
    """
    # define the columns (passed back to main code)
    date_colnames = ['DATE', 'NUM_TOTAL', 'NUM_FAIL', 'LINK']
    date_coltypes = ['str', 'str', 'str', 'url']
    table_dates = []
    # dictionary for storage
    date_dict = dict()
    # add columns
    for col in date_colnames:
        date_dict[col] = []
    # get table name
    table_filename = machine_name.lower()
    # loop around rows in table
    for row in range(len(table)):
        # convert start time into a YYYY-MM-DD
        date = table['START_TIME'][row].split(' ')[0]
        # get the date given to this row
        table_dates.append(date)
    # make the table dates a numpy array
    table_dates = np.array(table_dates)
    # get a list of unique dates
    unique_dates = list(set(table_dates))

    for unique_date in unique_dates:
        # get a mask for this date in the original table
        mask = table_dates == unique_date
        # count the number of entries
        num_entries = np.sum(mask)
        # count the number of errors (False or 0)
        num_errors = np.sum(table['ENDED'][mask] == 'False')
        num_errors += np.sum(table['ENDED'][mask] == 0)
        # create html url link
        html_file = f'{table_filename}_{unique_date.replace("-", "_")}.html'
        # deal with populating date table
        date_dict['DATE'].append(unique_date)
        date_dict['NUM_TOTAL'].append(num_entries)
        date_dict['NUM_FAIL'].append(num_errors)
        date_dict['LINK'].append(html_file)
    # convert date_dict into table
    date_table = Table(date_dict)
    # sort by date (newest first)
    sortmask = np.argsort(date_dict['DATE'])[::-1]
    date_table = date_table[sortmask]
    # return the date_table, colnames, coltypes and the date value for each col
    return date_table, date_colnames, date_coltypes, table_dates



# =============================================================================
# Finder functions
# =============================================================================
def add_finder_table(params: ParamDict, data_dict: Dict[str, Any]):
    # set function name
    funcname = __NAME__ + '.add_recipe_tables()'
    # get the ari user
    ari_user = params['ARI_USER']
    # set html body
    # Take directly from one of the sphinx pages (this is a massive hack)
    html_body1 = """

    <div class="related" role="navigation" aria-label="related navigation">
      <h3>Navigation</h3>
      <ul>
        <li class="right" style="margin-right: 10px">
          <a href="http://apero.exoplanets.ca/" title="Home">Home</a></li>
        <li class="right" style="margin-right: 10px">
          <a href="http://apero.exoplanets.ca/genindex.html" title="General Index"
             accesskey="I">index</a></li>
        <li class="nav-item nav-item-0"><a href="http://apero.exoplanets.ca/ari/home">APERO Reduction interface</a> &#187;</li>
      </ul>
    </div>

      <div class="pageheader">

      <ul>
      <li><a title="Home" href="http://apero.exoplanets.ca">
          <i class="fa fa-home fa-3x" aria-hidden="true"></i></a></li>
      <li><a title="install" href="http://apero.exoplanets.ca/user/general/installation">
          <i class="fa fa-cog fa-3x" aria-hidden="true"></i></a></li>
      <li><a title="github" href="https://github.com/njcuk9999/apero-drs">
          <i class="fa fa-git-square fa-3x" aria-hidden="true"></i></a></li>
      <li><a title="download paper" href="https://ui.adsabs.harvard.edu/abs/2022PASP..134k4509C">
          <i class="fa fa-file-pdf-o fa-3x" aria-hidden="true"></i></a></li>
      <li><a title="UdeM" href="http://apero.exoplanets.ca/main/misc/udem.html">
          <i class="fa fa-university fa-3x" aria-hidden="true"></i></a></li>
    </ul>

      <div>
      <a href="http://apero.exoplanets.ca">
        <img src="../_static/images/apero_logo.png" alt="APERO" />
      </a>
      <br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A PipelinE to Reduce Observations
      </div>

      </div>

      <div class="document">
        <div class="documentwrapper">
            <div class="body" role="main">

      <h1>{TITLE}</h1>
      <p> Note this table contains all objects in the APERO astrometrics 
      database, not only objects currently observed or planned to be observed.</p>
      <br>
      <p><a href="../index.html">Back to index page</a></p>
      <br>

      """

    html_body2 = """
              <div class="clearer"></div>
            </div>
          </div>
        <div class="clearer"></div>
      </div>
      """

    html_body2 += """
    <script src="/ari/home/login.js"></script>
    <script>EnableContent()</script>
    
    <div class="related" role="navigation" aria-label="related navigation">
      <h3>Navigation</h3>
    </div>
    <div class="footer" role="contentinfo">
        &#169; Copyright {0}, Neil Cook.
    </div>
    """.format(Time.now().datetime.year)

    # set html table class
    table_class = 'class="csvtable2 docutils align-default"'
    # css to include
    css_files = ['../_static/pygments.css',
                 '../_static/bizstyle.css',
                 '../_static/images/fonta/css/font-awesome.css',
                 '../_static/apero.css']
    # make path
    table_path = params['ARI_FINDER']['directory']
    # construct the html paths to copy to after compiling
    html_table_path = str(os.path.join(params['DRS_DATA_OTHER'], 'ari',
                                       '_build', 'html', 'finder'))
    # storage of html files
    added_html_files = []
    # define the columns (passed back to main code)
    date_colnames = ['Target', 'PDF', 'Updated']
    date_coltypes = ['str', 'url', 'str']
    data_table = Table()
    for col in date_colnames:
        data_table[col] = data_dict[col]
    # -------------------------------------------------------------------------
    # make recipe table
    # -------------------------------------------------------------------------
    # construct local path to save html to
    table_html1 = os.path.join(table_path, 'index.html')
    # convert table to outlist
    tout = error_html.table_to_outlist(data_table, date_colnames,
                                       out_types=date_coltypes)
    outlist, t_colnames, t_coltype = tout
    # convert outlist to a html/javascript table
    html_table = error_html.filtered_html_table(outlist,
                                                t_colnames,
                                                t_coltype,
                                                clean=False, log=False,
                                                table_class=table_class)
    # build html page
    html_title = 'Finder Charts'
    html_body1_filled = html_body1.format(TITLE=html_title,
                                          PROFILE=ari_user)
    html_content = error_html.full_page_html(html_body1=html_body1_filled,
                                             html_table=html_table,
                                             html_body2=html_body2,
                                             css=css_files)
    # write html page
    with open(table_html1, 'w') as wfile:
        wfile.write(html_content)
    # add recipe pages html directory store
    added_html_files.append([table_path, html_table_path])
    # update ari_extras with these html files
    ari_extras = list(params['ARI_EXTRAS'])
    ari_extras += added_html_files
    # push by into params extras (to add whole directory)
    params.set('ARI_EXTRAS', ari_extras, source=funcname)



def add_recipe_tables(params: ParamDict, table: Table, machine_name: str):
    # set function name
    funcname = __NAME__ + '.add_recipe_tables()'
    # get the ari user
    ari_user = params['ARI_USER']
    # set html body
    # Take directly from one of the sphinx pages (this is a massive hack)
    html_body1 = """
    <div class="related" role="navigation" aria-label="related navigation">
      <h3>Navigation</h3>
      <ul>
        <li class="right" style="margin-right: 10px">
          <a href="http://apero.exoplanets.ca/" title="Home">Home</a></li>
        <li class="right" style="margin-right: 10px">
          <a href="http://apero.exoplanets.ca/genindex.html" title="General Index"
             accesskey="I">index</a></li>
        <li class="nav-item nav-item-0"><a href="http://apero.exoplanets.ca/ari/home">APERO Reduction interface</a> &#187;</li>
      </ul>
    </div>
    
    <div class="pageheader">

    <ul>
    <li><a title="Home" href="http://apero.exoplanets.ca">
        <i class="fa fa-home fa-3x" aria-hidden="true"></i></a></li>
    <li><a title="install" href="http://apero.exoplanets.ca/user/general/installation">
        <i class="fa fa-cog fa-3x" aria-hidden="true"></i></a></li>
    <li><a title="github" href="https://github.com/njcuk9999/apero-drs">
        <i class="fa fa-git-square fa-3x" aria-hidden="true"></i></a></li>
    <li><a title="download paper" href="https://ui.adsabs.harvard.edu/abs/2022PASP..134k4509C">
        <i class="fa fa-file-pdf-o fa-3x" aria-hidden="true"></i></a></li>
    <li><a title="UdeM" href="http://apero.exoplanets.ca/main/misc/udem.html">
        <i class="fa fa-university fa-3x" aria-hidden="true"></i></a></li>
  </ul>

    <div>
    <a href="http://apero.exoplanets.ca">
      <img src="../../_static/images/apero_logo.png" alt="APERO" />
    </a>
    <br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A PipelinE to Reduce Observations
    </div>

    </div>

    <div class="document">
      <div class="documentwrapper">
          <div class="body" role="main">

    <h1>{TITLE}</h1>
    <p> Note the date is the date processed NOT the observation directory 
        (or night directory)</p>
    <br>
    <p><a href="../profile.html">Back to profile page ({PROFILE})</a></p>
    <br>
    <p> 
    A list of known errors can be found 
    <a href=""" + ari_core.KNOWN_ERRORS_SHEET + """"">here</a>
    <br>
    Please report any errors missing.
    </p>
    <br>


    """

    html_body2 = """
              <div class="clearer"></div>
            </div>
          </div>
        <div class="clearer"></div>
      </div>
      """
    html_body2 += """
    <script src="/ari/home/login.js"></script>
    <script>EnableContent()</script>
    
    <div class="related" role="navigation" aria-label="related navigation">
      <h3>Navigation</h3>
    </div>
    <div class="footer" role="contentinfo">
        &#169; Copyright {0}, Neil Cook.
    </div>
    """.format(Time.now().datetime.year)

    # set html table class
    table_class = 'class="csvtable2 docutils align-default"'
    # css to include
    css_files = ['../_static/pygments.css',
                 '../_static/bizstyle.css',
                 '../_static/images/fonta/css/font-awesome.css',
                 '../_static/apero.css']
    # make path
    table_path = params['ARI_RECIPE_PAGES']
    # get table name
    table_filename = machine_name.lower()
    # construct the html paths to copy to after compiling
    html_table_path1 = str(os.path.join(params['DRS_DATA_OTHER'], 'ari',
                                        '_build', 'html', ari_user))
    html_table_path2 = str(os.path.join(html_table_path1, 'recipe_pages'))
    # storage of html files
    added_html_files = []
    # split the table into sub-tables based on start date
    dout = recipe_date_table(table, machine_name)
    date_table, date_colnames, date_coltypes, table_dates = dout
    # loop around sub tables
    for date in date_table['DATE']:
        # find all rows in table that conform to this date
        tablemask = table_dates == date
        # make the table
        subtable = table[tablemask]
        # get the filename to create
        subtable_filename = f'{table_filename}_{date.replace("-", "_")}'
        # get html col names
        html_out_col_names = ari_core.HTML_OUTCOL_NAMES[machine_name]
        html_col_types = ari_core.HTML_COL_TYPES[machine_name]
        # convert table to outlist
        tout = error_html.table_to_outlist(subtable, html_out_col_names,
                                           out_types=html_col_types)
        outlist, t_colnames, t_coltype = tout

        # convert outlist to a html/javascript table
        html_table = error_html.filtered_html_table(outlist, t_colnames,
                                                    t_coltype, clean=False,
                                                    log=False,
                                                    table_class=table_class)
        # deal with path not existing
        if not os.path.exists(table_path):
            os.makedirs(table_path)
        # construct local path to save html to
        subtable_html1 = os.path.join(table_path, f'{subtable_filename}.html')
        # build html page

        html_title = 'Recipe log for {0} ({1})'.format(date, ari_user)
        html_body1_filled = html_body1.format(TITLE=html_title,
                                              PROFILE=ari_user)

        html_body1_filled += f"""
        <p>
        <a href="recipe_table.html">Back to recipe log ({ari_user})</a>
        </p>
        <br>
        """

        html_content = error_html.full_page_html(html_body1=html_body1_filled,
                                                 html_table=html_table,
                                                 html_body2=html_body2,
                                                 css=css_files)
        # write html page
        with open(subtable_html1, 'w') as wfile:
            wfile.write(html_content)

    # -------------------------------------------------------------------------
    # make recipe table
    # -------------------------------------------------------------------------
    # construct local path to save html to
    table_html1 = os.path.join(table_path, f'{table_filename.lower()}.html')
    # convert table to outlist
    tout = error_html.table_to_outlist(date_table, date_colnames,
                                       out_types=date_coltypes)
    outlist, t_colnames, t_coltype = tout
    # convert outlist to a html/javascript table
    html_table = error_html.filtered_html_table(outlist,
                                                t_colnames,
                                                t_coltype,
                                                clean=False, log=False,
                                                table_class=table_class)
    # build html page
    html_title = 'Recipe log ({0})'.format(ari_user)
    html_body1_filled = html_body1.format(TITLE=html_title,
                                          PROFILE=ari_user)
    html_content = error_html.full_page_html(html_body1=html_body1_filled,
                                             html_table=html_table,
                                             html_body2=html_body2,
                                             css=css_files)
    # write html page
    with open(table_html1, 'w') as wfile:
        wfile.write(html_content)
    # add recipe pages html directory store
    added_html_files.append([table_path, html_table_path2])
    # update ari_extras with these html files
    ari_extras = list(params['ARI_EXTRAS'])
    ari_extras += added_html_files
    # push by into params
    params.set('ARI_EXTRAS', ari_extras, source=funcname)


# =============================================================================
# Object index page
# =============================================================================
def make_finder_page(params: ParamDict):
    # load object database
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # get all objects
    object_table = objdbm.get_entries()
    # get list of object names
    objnames = list(object_table['OBJNAME'])
    # sort object names in alphabetical order
    objnames = np.sort(objnames)
    # load finder chart parameters
    params = ari_find.load_params(params)
    # get the finder directory
    finder_dir = params['ARI_FINDER']['directory']
    # copy finder charts from online to local directory (to avoid doing them
    #   again)
    ari_find.copy_finder_charts(params)
    # create dictionary to store finder charts for html table
    finder_dict = dict()
    finder_dict['Target'] = []
    finder_dict['PDF'] = []
    finder_dict['Updated'] = []
    finder_dict['Found'] = []
    # loop around object names
    for it, objname in enumerate(objnames):
        # get the target name
        finder_dict['Target'].append(objname)
        # construct pdf path
        pdf_name = f'{objname}.pdf'
        pdf_path = os.path.join(finder_dir, pdf_name)
        # if we are being asked to reset create a new finder chart
        if params['ARI_FINDER']['reset']:
            # create a new finder chart
            ari_find.create_finder_chart(params, objname, it, object_table)
            # add to finder_dict
            finder_dict['PDF'].append(pdf_name)
            finder_dict['Found'].append('True')
            last_updated_unix = os.path.getmtime(pdf_path)
            last_updated_iso = Time(last_updated_unix, format='unix').iso
            finder_dict['Updated'].append(str(last_updated_iso))
        # else if we have a finder chart, do not recreate it
        elif os.path.exists(pdf_path):
            finder_dict['PDF'].append(pdf_name)
            finder_dict['Found'].append('True')
            last_updated_unix = os.path.getmtime(pdf_path)
            last_updated_iso = Time(last_updated_unix, format='unix').iso
            finder_dict['Updated'].append(str(last_updated_iso))
        # else if we are told not to create a finder chart then do not create
        elif not params['ARI_FINDER']['create']:
            finder_dict['PDF'].append('No finder chart')
            finder_dict['Found'].append('False')
            finder_dict['Updated'].append('None')
        # otherwise we do not have a finder chart, so create one
        else:
            # create a new finder chart
            ari_find.create_finder_chart(params, objname, it, object_table)
            # add to finder_dict
            finder_dict['PDF'].append(pdf_name)
            finder_dict['Found'].append('True')
            last_updated_unix = os.path.getmtime(pdf_path)
            last_updated_iso = Time(last_updated_unix, format='unix').iso
            finder_dict['Updated'].append(str(last_updated_iso))
    # -------------------------------------------------------------------------
    # make html finder page
    add_finder_table(params, finder_dict)


# =============================================================================
# General functions
# =============================================================================
def make_index_page(params: ParamDict):
    # get ari user
    ari_user = params['ARI_USER']
    # get path to save index to (above ari_dir level)
    index_path = os.path.dirname(params['ARI_DIR'])
    # create ARI index page
    index_page = drs_markdown.MarkDownPage('ari_index')
    # add title
    index_page.add_title('APERO Reduction Interface (ARI)')
    # TODO: This really needs to be all profiles
    profile_files = [os.path.join(ari_user, 'profile.rst')]
    # -------------------------------------------------------------------------
    # add page access
    index_page.add_html(add_page_access(params['ARI_GROUP']))
    # -------------------------------------------------------------------------
    # Add basic text
    # construct text to add
    index_page.add_text('This is the APERO Reduction Interface (ARI).')
    index_page.add_newline()
    index_page.add_text('Please select a reduction')
    index_page.add_newline()
    index_page.add_text('Please note: Your object may be under another '
                        'name. Please check `here <https://docs.google.com/'
                        'spreadsheets/d/'
                        '1dOogfEwC7wAagjVFdouB1Y1JdF9Eva4uDW6CTZ8x2FM/'
                        'edit?usp=sharing>`_, the name displayed in ARI will '
                        'be the first column [OBJNAME]')
    index_page.add_newline()
    index_page.add_text('If you have any issues please report using '
                        '`this sheet <https://docs.google.com/spreadsheets/d/1Ea_WEFTlTCbth'
                        'R24aaQm4KaleIteLuXLgn4RiNBnEqs/edit?usp=sharing>`_.')
    index_page.add_newline()
    index_page.add_text('Last updated: {0} [UTC]'.format(Time.now()))
    index_page.add_newline()
    # -------------------------------------------------------------------------
    # add table of contents
    index_page.add_table_of_contents(profile_files, sectionname='Reductions:')
    # -------------------------------------------------------------------------
    index_page.add_section('Finder charts')
    index_page.add_newline()
    index_page.add_text('Please note this includes objects not currently '
                        'observed.')
    index_page.add_newline()
    index_page.lines += [f'* `Finder chart table <finder/index.html>`_']
    # -------------------------------------------------------------------------
    # save index page
    index_page.write_page(os.path.join(index_path, 'index.rst'))


def make_profile_page(params: ParamDict, tables: List[TableFile]):
    # get ari user
    ari_user = params['ARI_USER']
    # get path to save
    profile_path = params['ARI_DIR']
    # construct the profile name
    profile_name = f'profile.rst'
    # create a page
    profile_page = drs_markdown.MarkDownPage(ari_user)
    # add title
    profile_page.add_title(ari_user)
    # add page access
    profile_page.add_html(add_page_access(params['ARI_GROUP']))
    # -----------------------------------------------------------------
    # Add basic text
    # construct text to add
    profile_page.add_text(f'This is the APERO Reduction Interface (ARI) '
                          f'for the reduction: {ari_user}')
    profile_page.add_newline()
    profile_page.add_text('Please note: Your object may be under another '
                          'name. Please check `here <https://docs.google.com/'
                          'spreadsheets/d/'
                          '1dOogfEwC7wAagjVFdouB1Y1JdF9Eva4uDW6CTZ8x2FM/'
                          'edit?usp=sharing>`_, the name displayed in ARI will '
                          'be the first column [OBJNAME]')
    profile_page.add_newline()
    profile_page.add_text('If you have any issues please report using '
                          '`this sheet <https://docs.google.com/spreadsheets/d/1Ea_WEFTlTCbth'
                          'R24aaQm4KaleIteLuXLgn4RiNBnEqs/edit?usp=sharing>`_')
    profile_page.add_newline()
    profile_page.add_text('Last updated: {0} [UTC]'.format(Time.now()))
    profile_page.add_newline()

    # get table files list
    table_names, table_files, table_urls = [], [], []
    for table in tables:
        if not table.null:
            if table.machinename.upper() in ari_core.CONTENTS_TABLES:
                table_files.append(table.rst_filename)
            elif table.machinename.upper() in ari_core.OTHER_TABLES:
                table_names.append(table.title)
                table_urls.append(table.html_path)

    # add table of contents to profile page
    if len(table_files) > 0:
        profile_page.add_table_of_contents(table_files)

    # add list of urls
    if len(table_urls) > 0:
        # add a section
        profile_page.add_newline()
        profile_page.add_text('Other: ')
        profile_page.add_newline()
        # add the urls as a list
        for table_it in range(len(table_urls)):
            # get url from table urls
            url = table_urls[table_it]
            title = table_names[table_it]
            # add the url
            profile_page.lines += [f'* `{title} <{url}>`_']
            # add a new line
            profile_page.add_newline()
        profile_page.add_newline()
    # save profile page
    profile_page.write_page(os.path.join(profile_path, profile_name))


def sphinx_compile(params: ParamDict):
    # get the working directory path
    working_dir = os.path.dirname(params['ARI_DIR'])
    # get the resources default working directory path
    resources_dir = params['ARI_DWORKING_DIR']
    # copy over working directory from resources
    content = glob.glob(os.path.join(resources_dir, '*'))
    for element in content:
        # get the path to copy to
        new_element = element.replace(resources_dir, working_dir)
        # copy
        drs_path.copy_element(element, new_element)
    # ------------------------------------------------------------------
    # get current directory
    cwd = os.getcwd()
    # change to docs directory
    os.chdir(working_dir)
    # ------------------------------------------------------------------
    # clean build
    # ------------------------------------------------------------------
    # Cleaning build directories
    WLOG(params, '', textentry('40-506-00001'))
    os.system('make clean')
    # ------------------------------------------------------------------
    # build html
    # ------------------------------------------------------------------
    # Compiling HTML
    WLOG(params, '', textentry('40-506-00002'))
    # Running make html
    WLOG(params, '', textentry('40-506-00003'))
    # make html using sphinx
    os.system('make html')
    # ------------------------------------------------------------------
    # copy extras (directory generated html files - not by sphinx)
    for extra in params['ARI_EXTRAS']:
        old_path, new_path = extra
        drs_path.copy_element(old_path, new_path)
    # ------------------------------------------------------------------
    # change back to current directory
    os.chdir(cwd)


def add_other_reductions(params: ParamDict):
    # get the base_path page (above ari_dir level)
    base_path = str(os.path.join(params['DRS_DATA_OTHER'], 'ari',
                                 '_build', 'html'))
    # index.html file
    index_html = os.path.join(base_path, 'index.html')
    # define the userlist yaml file
    userlist_file = 'user.yaml'
    userlist_yaml = os.path.join(base_path, userlist_file)
    # get the ssh directory
    ssh_directory = params['ARI_SSH_COPY']['directory']
    # download the userlist.txt file and copy it over userlist_yaml
    remote_path = str(os.path.join(ssh_directory,
                                   params['ARI_INSTRUMENT'].lower(),
                                   userlist_file))
    # get file
    ari_core.do_rsync(params, mode='get', path_in=remote_path,
                      path_out=userlist_yaml)
    # open the userlist.yaml file
    if os.path.exists(userlist_yaml):
        userlist = base.load_yaml(userlist_yaml)
    # if it doesn't exist just assume it is blank
    else:
        userlist = dict()
    # -------------------------------------------------------------------------
    # get the usernames for this instrument
    if params['ARI_INSTRUMENT'] not in userlist:
        usernames = set()
    else:
        usernames = set(userlist[params['ARI_INSTRUMENT']])
    # add the current ari username to the list
    usernames.add(params['ARI_USER'])
    # turn usernames into a list and sort it
    usernames = list(usernames)
    usernames.sort()
    # -------------------------------------------------------------------------
    # load the index
    with open(index_html, 'r') as rfile:
        index = rfile.read()
    # Parse the HTML content using beautiful soup
    soup = BeautifulSoup(index, 'html.parser')
    # get the div for the content we want to change
    contents_div = soup.find('div', {'class': 'toctree-wrapper compound'})
    # find the lists in div and remove them
    for contents_li in contents_div.find_all('li'):
        contents_li.decompose()
    # remove the ul from contents_div
    for contents_ul in contents_div.find_all('ul'):
        contents_ul.decompose()
    # remove all br from contents_div
    for contents_br in contents_div.find_all('br'):
        contents_br.decompose()
    # now add the new usernames
    for username in usernames:
        # create a new item
        new_item = soup.new_tag('li', **{'class': 'toctree-l1'})
        # create a new link
        new_link = soup.new_tag('a', href=f'{username}/profile.html')
        # add the link text
        new_link.string = username
        # add the link to the item
        new_item.append(new_link)
        # append the new item to the contents_div
        contents_div.append(new_item)
    # save over the index.html
    with open(index_html, 'w') as wfile:
        wfile.write(str(soup))
    # -------------------------------------------------------------------------
    # add the username to the userlist
    userlist[params['ARI_INSTRUMENT']] = list(usernames)
    # save the userlist
    base.write_yaml(userlist, userlist_yaml)


def add_page_access(group_name: str) -> List[str]:
    """
    This locks the page to only be accessible by the group name
    i.e. via log in

    :param group_name: str, the group name to lock the page to

    :return: str, the html code to add
    """
    htmllines = []
    htmllines += ['<script src="/ari/home/login.js"></script>']
    htmllines += [f'<script>pageAccess("{group_name}", "/ari/home/index.html")</script>']

    return htmllines


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

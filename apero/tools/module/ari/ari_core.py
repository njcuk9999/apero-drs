#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-23 at 10:56

@author: cook
"""
import copy
import glob
import os
import shutil
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.table import Table
from astropy.time import Time, TimeDelta
from astropy.io import fits
from astropy import units as uu
from scipy.optimize import curve_fit

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.io import drs_table
from apero.core.math import normal_fraction
from apero.tools.module.documentation import drs_markdown
from apero.plotting import gen_plot
from apero.base.base import TQDM as tqdm


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
# -----------------------------------------------------------------------------
# Parameter variables
# -----------------------------------------------------------------------------
# mapping of yaml keys to param dict keys
YAML_TO_PARAM = dict()
YAML_TO_PARAM['settings.instrument'] = 'ARI_INSTRUMENT'
YAML_TO_PARAM['settings.username'] = 'ARI_USER'
YAML_TO_PARAM['settings.N_CORES'] = 'ARI_NCORES'
YAML_TO_PARAM['settings.SpecWave'] = 'ARI_WAVE_RANGES'
YAML_TO_PARAM['settings.ssh'] = 'ARI_SSH_COPY'
YAML_TO_PARAM['settings.reset'] = 'ARI_RESET'
YAML_TO_PARAM['settings.filter objects'] = 'c'
YAML_TO_PARAM['settings.objects'] = 'ARI_FILTER_OBJECTS_LIST'
YAML_TO_PARAM['settings.finding charts'] = 'ARI_FINDING_CHARTS'
YAML_TO_PARAM['headers'] = 'ARI_HEADER_PROPS'
# mapping of AriObject keys to yaml dump
OBJ_TO_YAML = dict()
OBJ_TO_YAML['objname'] = 'OBJNAME'
OBJ_TO_YAML['exists'] = 'EXISTS'
OBJ_TO_YAML['dprtypes'] = 'DPRTYPES'
OBJ_TO_YAML['last_processed'] = 'LAST_PROCESSED'
OBJ_TO_YAML['lbl_templates'] = 'LBL_TEMPLATES'
OBJ_TO_YAML['lbl_select'] = 'LBL_SELECT'
OBJ_TO_YAML['spec_plot_path'] = 'SPEC_PLOT_PATH'
OBJ_TO_YAML['spec_stats_table'] = 'SPEC_STATS_TABLE'
OBJ_TO_YAML['spec_rlink_table'] = 'SPEC_RLINK_TABLE'
OBJ_TO_YAML['spec_dwn_table'] = 'SPEC_DWN_TABLE'
OBJ_TO_YAML['lbl_combinations'] = 'LBL_COMBINATIONS'
OBJ_TO_YAML['lbl_plot_path'] = 'LBL_PLOT_PATH'
OBJ_TO_YAML['lbl_stats_table'] = 'LBL_STATS_TABLE'
OBJ_TO_YAML['lbl_rlink_table'] = 'LBL_RLINK_TABLE'
OBJ_TO_YAML['lbl_dwn_table'] = 'LBL_DWN_TABLE'
OBJ_TO_YAML['ccf_plot_path'] = 'CCF_PLOT_PATH'
OBJ_TO_YAML['ccf_stats_table'] = 'CCF_STATS_TABLE'
OBJ_TO_YAML['ccf_rlink_table'] = 'CCF_RLINK_TABLE'
OBJ_TO_YAML['ccf_dwn_table'] = 'CCF_DWN_TABLE'
OBJ_TO_YAML['time_series_plot_path'] = 'TIME_SERIES_PLOT_PATH'
OBJ_TO_YAML['time_series_stats_table'] = 'TIME_SERIES_STATS_TABLE'
OBJ_TO_YAML['time_series_rlink_table'] = 'TIME_SERIES_RLINK_TABLE'
OBJ_TO_YAML['time_series_dwn_table'] = 'TIME_SERIES_DWN_TABLE'

# Some keys need to be converted to put into the yaml
OBJ_TO_YAML_DTYPES = dict()
OBJ_TO_YAML_DTYPES['last_processed'] = 'astropy.time.Time'

# -----------------------------------------------------------------------------
# Instrument variables
# -----------------------------------------------------------------------------
# define which instruments have polar
HAS_POLAR = dict(SPIROU=True, NIRPS_HE=False, NIRPS_HA=False)

# -----------------------------------------------------------------------------
# Object Table variables
# -----------------------------------------------------------------------------
# define the column which is the object name
OBJECT_COLUMN = 'OBJNAME'
# define the astrometric database column names to get
ASTROMETRIC_COLUMNS = ['OBJNAME', 'RA_DEG', 'DEC_DEG', 'TEFF', 'SP_TYPE']
ASTROMETRIC_DTYPES = [str, float, float, float, str]
# define the log database column names to get
LOG_COLUMNS = ['RECIPE', 'SHORTNAME', 'RUNSTRING', 'START_TIME', 'END_TIME',
               'PASSED_ALL_QC', 'ENDED', 'ERRORMSGS', 'LOGFILE']
LOG_TYPES = ['str', 'str', 'str', 'str', 'str', 'bool', 'bool', 'str', 'str']
# Columns in the object table
OBJTABLE_COLS = dict()
OBJTABLE_COLS['OBJNAME'] = 'OBJNAME'
OBJTABLE_COLS['RA'] = 'RA [Deg]'
OBJTABLE_COLS['DEC'] = 'Dec [Deg]'
OBJTABLE_COLS['TEFF'] = 'Teff [K]'
OBJTABLE_COLS['SPTYPE'] = 'SpT'
OBJTABLE_COLS['DPRTYPE'] = 'DPRTYPE'
OBJTABLE_COLS['RAW'] = 'raw files'
OBJTABLE_COLS['PP'] = 'pp files'
OBJTABLE_COLS['EXT'] = 'ext files'
OBJTABLE_COLS['TCORR'] = 'tcorr files'
OBJTABLE_COLS['CCF'] = 'ccf files'
OBJTABLE_COLS['POL'] = 'pol files'
OBJTABLE_COLS['efits'] = 'e.fits'
OBJTABLE_COLS['tfits'] = 't.fits'
OBJTABLE_COLS['vfits'] = 't.fits'
OBJTABLE_COLS['pfits'] = 'p.fits'
OBJTABLE_COLS['lbl'] = 'LBL'
OBJTABLE_COLS['last_obs'] = 'Last observed'
OBJTABLE_COLS['last_proc'] = 'Last Processed'
# polar columns (only used for instruments that use polarimetry)
POLAR_COLS = ['POL', 'pfits']

# Finder columns
FINDER_COLUMNS = ['Target', 'PDF', 'Last updated']

# -----------------------------------------------------------------------------
# File variables
# -----------------------------------------------------------------------------
# define science dprtypes
SCIENCE_DPRTYPES = ['OBJ_FP', 'OBJ_SKY', 'OBJ_DARK', 'POLAR_FP', 'POLAR_DARK']
# define the lbl files
LBL_FILETYPES = ['lbl_rdb', 'lbl2_rdb', 'lbl_drift', 'lbl2_drift', 'lbl_fits']
LBL_FILENAMES = ['lbl_{0}_{1}.rdb', 'lbl2_{0}_{1}.rdb',
                 'lbl_{0}_{1}_drift.rdb', 'lbl2_{0}_{1}_drift.rdb',
                 'lbl_{0}_{1}.fits']
LBL_FILE_DESC = ['RDB file', 'RDB2 file', 'Drift file', 'Drift2 file',
                 'LBL RDB fits file']
LBL_DOWNLOAD = [True, True, True, True, False]
# define how many ccf files to use
MAX_NUM_CCF = 100

# -----------------------------------------------------------------------------
# Processing variables
# -----------------------------------------------------------------------------
# define which parellisation mode to run in
MULTI = 'Process'

# -----------------------------------------------------------------------------
# Page variables
# -----------------------------------------------------------------------------
# object page styling
DIVIDER_COLOR = '#FFA500'
DIVIDER_HEIGHT = 6
PLOT_BACKGROUND_COLOR = '#FEFDE1'
# define which one of these files to use as the main plot file
LBL_PLOT_FILE = 0
# define the LBL stat dir (inside the lbl directory)
LBL_STAT_DIR = 'lblstats'
# define the LBL stat files {0} is for the object name + template name
#  i.e. {objname}_{template}
LBL_STAT_FILES = dict()
LBL_STAT_FILES['LBL Diagnostic Plots'] = 'lbl_{0}_plots.pdf'
LBL_STAT_FILES['LBL BERV zp RDB file'] = 'lbl_{0}_bervzp.rdb'
LBL_STAT_FILES['LBL BERV zp RDB2 file'] = 'lbl2_{0}_bervzp.rdb'
LBL_STAT_FILES['LBL BERV Zp Diaganostic Plots'] = 'lbl_{0}_bervzp_plots.pdf'
LBL_STAT_FILES['LBL-PCA RDB file'] = 'lbl_{0}_PCAx.rdb'
LBL_STAT_FILES['LBL-PCA RDB2 file'] = 'lbl2_{0}_PCAx.rdb'
# time series column names
TIME_SERIES_COLS = ['Obs Dir', 'First obs mid',
                    'Last obs mid', 'Number of ext', 'Number of tcorr',
                    'Seeing', 'Airmass',
                    'Mean Exptime', 'Total Exptime', 'DPRTYPEs', None, None]
# Which tables are Contents tables (linked to via .rst)
CONTENTS_TABLES = ['OBJECT_TABLE']
# Which tables are Other tables (linked to via .html)
OTHER_TABLES = ['RECIPE_TABLE']

# -----------------------------------------------------------------------------
# Google variables
# -----------------------------------------------------------------------------
# define the prefilled request link
PREFILLED_REQUEST_LINK = ('https://docs.google.com/forms/d/e/1FAIpQLSev3v7EnHq'
                          '2KyQyVWlDikA8-tDzMINYZA0SkYz93vAanpIdhA/'
                          'viewform?usp=pp_url')
# each entry has an id - we define these in a dictionary
PREFILLED_RDICT = dict()
PREFILLED_RDICT['OBJNAMES'] = 'entry.193319269'
PREFILLED_RDICT['STARTDATE'] = 'entry.293060210'
PREFILLED_RDICT['ENDDATE'] = 'entry.299959352'
PREFILLED_RDICT['APERO_MODE'] = 'entry.923271952'
PREFILLED_RDICT['FIBER'] = 'entry.1651377065'
PREFILLED_RDICT['DPRTYPES'] = 'entry.298205572'
PREFILLED_RDICT['DRSOUTID'] = 'entry.459458944'
# define the request form fiber types
RDICT_FIBERS = ['Science fiber', 'Reference fiber', 'All fibers']
# Known errors sheet
KNOWN_ERRORS_SHEET = ('https://docs.google.com/spreadsheets/d/15Gu_aY6h9Esw1uTF'
                      '8Y5JCHl6m7191AviJNTPkbeTiQE/edit?usp=sharing')

# -----------------------------------------------------------------------------
# html and rsync variables
# -----------------------------------------------------------------------------
# define rsync commands
RSYNC_CMD_IN = 'rsync -avuz -e "{SSH}" {USER}@{HOST}:{INPATH} {OUTPATH}'
RSYNC_CMD_OUT = 'rsync -avuz -e "{SSH}" {INPATH} {USER}@{HOST}:{OUTPATH}'
# define the html col names for each table
HTML_INCOL_NAMES = dict()
HTML_INCOL_NAMES['OBJECT_TABLE'] = list(OBJTABLE_COLS.keys())
HTML_INCOL_NAMES['RECIPE_TABLE'] = LOG_COLUMNS
# define the html col names for each table
HTML_OUTCOL_NAMES = dict()
HTML_OUTCOL_NAMES['OBJECT_TABLE'] = list(OBJTABLE_COLS.values())
HTML_OUTCOL_NAMES['RECIPE_TABLE'] = LOG_COLUMNS
HTML_OUTCOL_NAMES['FINDER_TABLE'] = FINDER_COLUMNS
# define the html col types for each table ('str' or 'list')
HTML_COL_TYPES = dict()
HTML_COL_TYPES['OBJECT_TABLE'] = ['str'] * len(HTML_OUTCOL_NAMES['OBJECT_TABLE'])
HTML_COL_TYPES['RECIPE_TABLE'] = ['str'] * len(HTML_OUTCOL_NAMES['RECIPE_TABLE'])
HTML_COL_TYPES['FINDER_TABLE'] = ['str'] * len(HTML_OUTCOL_NAMES['FINDER_TABLE'])


# =============================================================================
# Define classes
# =============================================================================
class FileType:
    def __init__(self, name: str, block_kind: Optional[str] = None,
                 kw_output: Optional[str] = None, fiber: Optional[str] = None,
                 count: bool = True, chain: Optional[str] = None):
        self.name = str(name)
        self.block_kind = copy.deepcopy(block_kind)
        self.kw_output = copy.deepcopy(kw_output)
        self.fiber = copy.deepcopy(fiber)
        self.count = bool(count)
        self.chain = copy.deepcopy(chain)
        # whether FileType properties came from previous run
        self.exists = False
        # whether we need to update this
        self.update = False
        # file properties
        self.cond = None
        self.files = []
        self.qc_mask = None
        self.obsdirs = []
        self.processed_times = []
        self.first = None
        self.last = None
        self.num = 0
        self.num_passed = 0
        self.num_failed = 0

    def yaml_dump(self):
        # set up yaml dict
        yaml_dict = dict()
        # ------------------------------------------------------------------
        # push properties into yaml dict
        # ------------------------------------------------------------------
        # the name of the filetype
        yaml_dict['name'] = str(self.name)
        # the block kind (i.e. raw, tmp, red, out)
        yaml_dict['block_kind'] = str(self.block_kind)
        # the file type (DRSOUTID)
        yaml_dict['kw_output'] = str(self.kw_output)
        # the fiber type
        yaml_dict['fiber'] = str(self.fiber)
        # whether to count the files
        yaml_dict['count'] = bool(self.count)
        # whether there is a chain (i.e. this file was created from another)
        yaml_dict['chain'] = str(self.chain)
        # the sql condition used
        yaml_dict['cond'] = str(self.cond)
        # numpy array of file paths --> list
        files = []
        for filename in self.files:
            files.append(str(filename))
        yaml_dict['files'] = files
        # numpy array of booleans (for the mask) --> list
        if self.qc_mask is not None:
            qc_mask_list = []
            for qc in self.qc_mask:
                qc_mask_list.append(bool(qc))
            yaml_dict['qc_mask'] = qc_mask_list
        else:
            yaml_dict['qc_mask'] = None
        # numpy array of observation directories --> list
        obsdirs = []
        for obsdir in self.obsdirs:
            obsdirs.append(str(obsdir))
        yaml_dict['obsdirs'] = obsdirs
        # ------------------------------------------------------------------
        # deal with processed times being a list of astropy Time objects
        if len(self.processed_times) == 0:
            yaml_dict['processed_times'] = []
        # we convert list to a Time array then to a list of iso strings
        else:
            processed_time_list = []
            for _time in self.processed_times:
                processed_time_list.append(str(_time.iso))
            yaml_dict['processed_times'] = processed_time_list
        # ------------------------------------------------------------------
        # deal with first variable as an astropy time --> str for yaml
        if self.first is not None:
            yaml_dict['first'] = str(self.first.iso)
        else:
            yaml_dict['first'] = None
        # ------------------------------------------------------------------
        # deal with last variable as an astropy time --> str for yaml
        if self.last is not None:
            yaml_dict['last'] = str(self.last.iso)
        else:
            yaml_dict['last'] = None
        # ------------------------------------------------------------------
        # number of files
        yaml_dict['num'] = int(self.num)
        # number of files passed QC
        yaml_dict['num_passed'] = int(self.num_passed)
        # number of files failed QC
        yaml_dict['num_failed'] = int(self.num_failed)
        # return yaml_dict
        return yaml_dict

    def load_dump(self, yaml_dict):
        # ------------------------------------------------------------------
        # set properties from yaml dict
        # ------------------------------------------------------------------
        # the name of the filetype
        self.name = yaml_dict['name']
        # the block kind (i.e. raw, tmp, red, out)
        self.block_kind = yaml_dict['block_kind']
        if self.block_kind in ['Null', 'None']:
            self.block_kind = None
        # the file type (DRSOUTID)
        self.kw_output = yaml_dict['kw_output']
        if self.kw_output in ['Null', 'None']:
            self.kw_output = None
        # the fiber type
        self.fiber = yaml_dict['fiber']
        if self.fiber in ['Null', 'None']:
            self.fiber = None
        # whether to count the files
        self.count = yaml_dict['count']
        # whether there is a chain (i.e. this file was created from another)
        self.chain = yaml_dict['chain']
        if self.chain in ['Null', 'None']:
            self.chain = None
        # the sql condition used
        self.cond = yaml_dict['cond']
        if self.cond in ['Null', 'None']:
            self.cond = None
        # list of file paths --> numpy array
        self.files = np.array(yaml_dict['files'])
        # list of booleans (for the mask) --> numpy array
        if yaml_dict['qc_mask'] in [None, 'None']:
            self.qc_mask = None
        else:
            self.qc_mask = np.array(yaml_dict['qc_mask'])
        # list of observation directories --> numpy array
        self.obsdirs = np.array(yaml_dict['obsdirs'])
        # ------------------------------------------------------------------
        # deal with processed times being a list of astropy Time objects
        if len(yaml_dict['processed_times']) == 0:
            self.processed_times = []
        else:
            self.processed_times = Time(yaml_dict['processed_times'],
                                        format='iso')
        # ------------------------------------------------------------------
        # deal with first variable as an astropy time --> str for yaml
        if yaml_dict['first'] is None:
            self.first = None
        else:
            self.first = Time(yaml_dict['first'], format='iso')
        # ------------------------------------------------------------------
        # deal with last variable as an astropy time --> str for yaml
        if yaml_dict['last'] is None:
            self.last = None
        else:
            self.last = Time(yaml_dict['last'], format='iso')
        # ------------------------------------------------------------------
        # number of files
        self.num = yaml_dict['num']
        # number of files passed QC
        self.num_passed = yaml_dict['num_passed']
        # number of files failed QC
        self.num_failed = yaml_dict['num_failed']
        # we used a yaml so we know this object existed before now
        self.exists = True

    def copy_new(self) -> 'FileType':
        # inherit values from self
        new = FileType(self.name, self.block_kind, self.kw_output, self.fiber,
                       self.count)
        return new

    def count_files(self, objname, indexdbm, logdbm,
                    filetypes: Dict[str, 'FileType']):
        # deal with not wanting to count in every case
        if not self.count:
            return
        # storage for giving to self
        first = None
        last = None
        processed_times = []
        # ------------------------------------------------------------------
        # Construct the condition for the query
        # ------------------------------------------------------------------
        if self.cond in [None, 'None', 'Null']:
            cond = f'KW_OBJNAME="{objname}"'
            if self.block_kind is not None:
                cond += f' AND BLOCK_KIND="{self.block_kind}"'
            if self.kw_output is not None:
                cond += f' AND KW_OUTPUT="{self.kw_output}"'
            if self.fiber is not None:
                cond += f' AND KW_FIBER="{self.fiber}"'
        else:
            cond = str(self.cond)
        # ------------------------------------------------------------------
        # run counting conditions using indexdbm
        # ------------------------------------------------------------------
        # deal with chain value being zero (don't continue)
        if self.chain is not None:
            if self.chain in filetypes:
                # get the number of files in chain filetype
                if filetypes[self.chain].num:
                    return
        # get the files
        dbcols = 'ABSPATH,OBS_DIR,KW_PID,KW_MID_OBS_TIME,KW_DRS_DATE_NOW'
        findex_table = indexdbm.get_entries(dbcols, condition=cond)
        # get a mask of rows that passed QC (based on PID)
        if self.name != 'raw':
            mask = _filter_pids(findex_table, logdbm)
            files = np.array(findex_table['ABSPATH'])
            qc_mask = mask
            obsdirs = np.array(findex_table['OBS_DIR'])
            # add last processed time of all files for this object
            pdates = np.array(findex_table['KW_DRS_DATE_NOW']).astype(str)
            if len(pdates) > 0:
                times_it = np.max(Time(pdates, format='iso'))
                processed_times.append(times_it)
        else:
            files = np.array(findex_table['ABSPATH'])
            qc_mask = np.ones(len(files)).astype(bool)
            obsdirs = np.array(findex_table['OBS_DIR'])
        # get the first and last files in time
        mjdmids = np.array(findex_table['KW_MID_OBS_TIME']).astype(float)
        mjdmids = Time(mjdmids, format='mjd')
        if len(mjdmids) > 0:
            first = np.min(mjdmids)
            last = np.max(mjdmids)
        # count files
        num = len(files)
        num_passed = np.sum(qc_mask)
        num_failed = np.sum(~qc_mask)

        # deal with no change in the number of files
        if self.num == num:
            self.update = False
        else:
            self.update = True
        # ------------------------------------------------------------------
        # update self
        # ------------------------------------------------------------------
        if self.update:
            self.cond = cond
            self.files = files
            self.qc_mask = qc_mask
            self.obsdirs = obsdirs
            self.processed_times = processed_times
            self.first = first
            self.last = last
            self.num = num
            self.num_passed = num_passed
            self.num_failed = num_failed

    def get_files(self, qc: Optional[bool] = None, attr='files'):
        # get the value of the attribute
        vector = getattr(self, attr)
        # deal with no qc --> all files
        if qc is None:
            return vector
        # deal with no mask --> all files
        if self.qc_mask is None:
            return vector
        # deal with qc = True --> return only qc files
        if qc:
            return vector[self.qc_mask]
        # deal with qc = False --> return only non qc files
        else:
            return vector[~self.qc_mask]


class RecipeEntry:
    pass


class AriObject:
    def __init__(self, objname: str, filetypes: Dict[str, FileType]):
        # get the object name
        self.objname = objname
        self.ra: Optional[str] = None
        self.dec: Optional[str] = None
        self.teff: Optional[str] = None
        self.sptype: Optional[str] = None
        self.aliases: Optional[str] = None
        self.pmra: Optional[str] = None
        self.pmde: Optional[str] = None
        self.plx: Optional[str] = None
        self.rv: Optional[str] = None

        self.ra_source: Optional[str] = None
        self.dec_source: Optional[str] = None
        self.teff_source: Optional[str] = None
        self.sp_source: Optional[str] = None
        self.pmra_source: Optional[str] = None
        self.pmde_source: Optional[str] = None
        self.plx_source: Optional[str] = None
        self.rv_source: Optional[str] = None

        # ----------------------------s-----------------------------------------
        # Add files as copy of filetype class
        # ---------------------------------------------------------------------
        self.filetypes: Dict[str, FileType] = dict()
        for key in filetypes:
            self.filetypes[key] = filetypes[key].copy_new()
        # flag for whether we have polar files
        self.has_polar: bool = False
        # set up yaml file
        self.yaml_filename: str = f'{self.objname}.yaml'
        # whether we need to update this
        self.update: bool = False
        # ---------------------------------------------------------------------
        # yaml parameters
        # ---------------------------------------------------------------------
        # whether this object has been seen before
        self.exists: bool = False
        # a string list of all dprtypes for this object
        self.dprtypes: Optional[str] = None
        # last processed of all files for this object
        self.last_processed: Optional[Time] = None
        # ---------------------------------------------------------------------
        # lbl parameters
        self.lbl_templates: Optional[List[str]] = None
        self.lbl_select: Optional[str] = None
        # add the lbl stat files into a dictionary
        self.lbl_stat_files = dict()
        # loop around lbl stats files and load lblfilekey dict in
        #   each dict should contain obj+temp combinations
        for lblfilekey in LBL_STAT_FILES:
            self.lbl_stat_files[lblfilekey] = dict()
        # ---------------------------------------------------------------------
        # get target output parameters
        self.target_stats_table: Optional[str] = None
        # get spectrum output parameters (for page integration)
        self.spec_plot_path: Optional[str] = None
        self.spec_stats_table: Optional[str] = None
        self.spec_rlink_table: Optional[str] = None
        self.spec_dwn_table: Optional[str] = None
        # get lbl output parameters (for page integration)
        self.lbl_combinations = []
        self.lbl_plot_path = dict()
        self.lbl_stats_table = dict()
        self.lbl_rlink_table = dict()
        self.lbl_dwn_table = dict()
        # get ccf output parameters (for page integration)
        self.ccf_plot_path: Optional[str] = None
        self.ccf_stats_table: Optional[str] = None
        self.ccf_rlink_table: Optional[str] = None
        self.ccf_dwn_table: Optional[str] = None
        # get time series output parameters (for page integration)
        self.time_series_plot_path: Optional[str] = None
        self.time_series_stats_table: Optional[str] = None
        self.time_series_rlink_table: Optional[str] = None
        self.time_series_dwn_table: Optional[str] = None
        # ---------------------------------------------------------------------
        # other parameters
        # ---------------------------------------------------------------------
        self.headers: Optional[Dict[str, Any]] = None
        # store the required header info
        self.header_dict = dict()

    def add_astrometrics(self, table):
        self.ra = str(table["RA_DEG"])
        self.ra_source = str(table['RA_SOURCE'])
        self.dec = str(table["DEC_DEG"])
        self.dec_source = str(table['DEC_SOURCE'])
        self.teff = str(table["TEFF"])
        self.teff_source = str(table['TEFF_SOURCE'])
        self.sptype = str(table["SP_TYPE"])
        self.sp_source = str(table['SP_SOURCE'])
        self.pmra = str(table["PMRA"])
        self.pmra_source = str(table['PMRA_SOURCE'])
        self.pmde = str(table["PMDE"])
        self.pmde_source = str(table['PMDE_SOURCE'])
        self.plx = str(table["PLX"])
        self.plx_source = str(table['PLX_SOURCE'])
        self.rv = str(table["RV"])
        self.rv_source = str(table['RV_SOURCE'])

        alias_list = table['ALIASES'].split('|')
        self.aliases = ',   '.join(alias_list)

        # aliases can start with a * replace them with the html
        self.aliases = self.aliases.replace('*', '\*')

        # TODO: Add Keywords, vsini etc when available

    def add_files_stats(self, indexdbm, logdbm):
        # keep track of whether we need to update
        update = False
        # loop around raw files
        for key in self.filetypes:
            # get iterations filetype
            filetype = self.filetypes[key]
            # count files and get lists of files
            filetype.count_files(self.objname, indexdbm, logdbm, self.filetypes)
            # deal with update
            update = update or bool(filetype.update)
            # if there are no entries we have no raw files for this object
            if key == 'raw':
                if filetype.num == 0:
                    return
        # ------------------------------------------------------------------
        # if we do not need to update stop here
        if not update:
            self.update = False
            return
        else:
            self.update = True
        # ------------------------------------------------------------------
        # Add a dpr type column
        dprtypes = indexdbm.get_entries('KW_DPRTYPE',
                                        condition=self.filetypes['pp'].cond)
        self.dprtypes = ','.join(list(np.unique(dprtypes)))
        # ------------------------------------------------------------------
        # get all filetype last processing times
        all_last_processed = []
        for key in self.filetypes:
            if len(self.filetypes[key].processed_times) > 0:
                for _time in self.filetypes[key].processed_times:
                    all_last_processed.append(_time)
        # convert to Time
        if len(all_last_processed) > 0:
            all_last_processed = Time(np.array(all_last_processed))
            # get the last processed time of all files
            self.last_processed = np.max(all_last_processed)
        else:
            self.last_processed = None

    def populate_header_dict(self, params: ParamDict):
        """
        Populate the header dictionary with the required header keys
        :return:
        """
        # push the header properites into self
        self.headers = params['ARI_HEADER_PROPS']
        # loop around COUNT COLS and populate header dict
        for key in self.filetypes:
            # check file kind in headers
            if key not in self.headers:
                continue
            # get the header keys
            self.get_header_keys(self.headers[key], self.filetypes[key].files)

    def get_header_keys(self, keys: Dict[str, Dict[str, str]], files: List[str]):
        """
        Get the header keys from the files
        :param keys: dictionary of keys to get (with their properties)
        :param files: list of files (for error reporting)
        :return:
        """

        # deal with no keys
        if len(keys) == 0:
            return
        # get an array of length of the files for each key
        for keydict in keys:
            # get key
            kstore = keys[keydict]
            dtype = kstore.get('dtype', None)
            timefmt = kstore.get('timefmt', None)
            unit = kstore.get('unit', None)
            # deal with no files
            if len(files) == 0:
                self.header_dict[keydict] = None
            elif dtype == 'float' and timefmt is None and unit is None:
                self.header_dict[keydict] = np.full(len(files), np.nan)
            elif unit is not None:
                null_list = [np.nan] * len(files)
                self.header_dict[keydict] = uu.Quantity(null_list, unit)
            else:
                self.header_dict[keydict] = np.array([None] * len(files))
        # loop around files and populate the header_dict
        for pos, filename in enumerate(files):
            header = fits.getheader(filename)
            for keydict in keys:
                # get value (for header dict)
                value = _header_value(keys[keydict], header, filename)
                # set value in header dict
                self.header_dict[keydict][pos] = value

    def save_to_disk(self, params: ParamDict):
        # make full yaml path
        yaml_path = params['ARI_OBJ_YAMLS']
        # check if yaml file exists
        yaml_abs_path = os.path.join(yaml_path, self.yaml_filename)
        # return if yaml file does not exist and remove if it does
        if os.path.exists(yaml_abs_path):
            os.remove(yaml_abs_path)
        # make sure exists is set to True
        self.exists = True
        # convert self keys into yaml dict
        yaml_dict = dict()
        for key in OBJ_TO_YAML:
            # get the value
            value = getattr(self, key)
            # deal with special data types
            if key in OBJ_TO_YAML_DTYPES:
                dtype = OBJ_TO_YAML_DTYPES[key]
                if value is None:
                    pass
                elif dtype == 'astropy.time.Time':
                    value = value.iso
            # push into yaml dictionary
            yaml_dict[OBJ_TO_YAML[key]] = value
        # ---------------------------------------------------------------------
        # manually add filetype dumps
        yaml_dict['FileType'] = dict()
        # loop around filetypes and add them
        for key in self.filetypes:
            yaml_dict['FileType'][key] = self.filetypes[key].yaml_dump()
        # ---------------------------------------------------------------------
        # save yaml dict to yaml file
        base.write_yaml(yaml_dict, yaml_abs_path)

    def load_from_disk(self, params: ParamDict):
        # make full yaml path
        yaml_path = params['ARI_OBJ_YAMLS']
        # check if yaml file exists
        yaml_abs_path = os.path.join(yaml_path, self.yaml_filename)
        # ---------------------------------------------------------------------
        # deal with a reset
        if params['ARI_RESET']:
            if os.path.exists(yaml_abs_path):
                os.remove(yaml_abs_path)
            return
        # ---------------------------------------------------------------------
        # return if yaml file does not exist
        if not os.path.exists(yaml_abs_path):
            return
        # load yaml file into dictionary
        yaml_dict = base.load_yaml(yaml_abs_path)
        # push keys into self
        for key in OBJ_TO_YAML:
            # get value from yaml dictionary
            value = yaml_dict[OBJ_TO_YAML[key]]
            # deal with special data types
            if key in OBJ_TO_YAML_DTYPES:
                dtype = OBJ_TO_YAML_DTYPES[key]
                if value in [None, 'None']:
                    value = None
                elif dtype == 'astropy.time.Time':
                    value = Time(value, format='iso')
            # update self
            setattr(self, key, value)
        # ---------------------------------------------------------------------
        # manually load filetype dumps into self.filetypes
        if 'FileType' in yaml_dict:
            # loop around filetypes and add them
            for key in yaml_dict['FileType']:
                self.filetypes[key].load_dump(yaml_dict['FileType'][key])

    # -------------------------------------------------------------------------
    # Target functions
    # -------------------------------------------------------------------------
    def get_target_parameters(self, params: ParamDict):
        # set up the object page
        obj_save_path = os.path.join(params['ARI_OBJ_PAGES'], self.objname)
        # ---------------------------------------------------------------------
        # storage for spectrum values
        target_props = dict()
        # object properties
        target_props['COORD_URL'] = f'../../../finder/{self.objname}.pdf'
        target_props['RA'] = f'{self.ra} [deg] ({self.ra_source})'
        target_props['Dec'] = f'{self.dec} [deg] ({self.dec_source})'
        target_props['Teff'] = f'{self.teff} [K] ({self.teff_source})'
        target_props['Spectral Type'] = f'{self.sptype} ({self.sp_source})'
        target_props['Proper motion RA'] = f'{self.pmra} [mas/yr] ({self.pmra_source})'
        target_props['Proper motion Dec'] = f'{self.pmde} [mas/yr] ({self.pmde_source})'
        target_props['Parallax'] = f'{self.plx} [mas/yr] ({self.plx_source})'
        target_props['RV'] = f'{self.rv} [mas/yr] ({self.rv_source})'
        target_props['Aliases'] = self.aliases

        # -----------------------------------------------------------------
        # construct the stats
        # -----------------------------------------------------------------
        # get the stats base name
        target_base_name = 'target_stat_' + self.objname + '.txt'
        # get the stat path
        target_path = os.path.join(obj_save_path, target_base_name)
        # compute the stats
        target_stats_table(target_props, target_path,
                           title='Target Information')
        # -----------------------------------------------------------------
        # update the paths
        self.target_stats_table = target_base_name

    # -------------------------------------------------------------------------
    # Spectrum functions
    # -------------------------------------------------------------------------
    def get_spec_parameters(self, params: ParamDict):
        # set up the object page
        obj_save_path = os.path.join(params['ARI_OBJ_PAGES'], self.objname)
        # get the extracted files
        ext_files = self.filetypes['ext'].get_files()
        # don't go here if ext files are not present
        if len(ext_files) == 0:
            return
        # ---------------------------------------------------------------------
        # storage for spectrum values
        spec_props = dict()
        # get files to use
        spec_props['RAW'] = self.filetypes['raw']
        spec_props['EXT'] = self.filetypes['ext']
        spec_props['TCORR'] = self.filetypes['tcorr']
        spec_props['S1D'] = self.filetypes['s1d']
        spec_props['SC1D'] = self.filetypes['sc1d']
        # ---------------------------------------------------------------------

        spec_props['DPRTYPES'] = self.dprtypes
        # ---------------------------------------------------------------------
        # header dict alias
        hdict = self.header_dict
        ftypes = self.filetypes
        # get values for use in plot
        spec_props['mjd'] = Time(np.array(hdict['EXT_MJDMID']))
        spec_props['EXT_Y'] = np.array(hdict['EXT_Y'])
        ext_h = np.array(hdict['EXT_H'])
        spec_props['EXT_H'] = ext_h
        spec_props['EXT_Y_LABEL'] = self.headers['ext']['EXT_Y']['label']
        spec_props['EXT_H_LABEL'] = self.headers['ext']['EXT_H']['label']
        spec_props['NUM_RAW_FILES'] = ftypes['raw'].num_passed
        spec_props['NUM_PP_FILES'] = ftypes['pp'].num_passed
        spec_props['NUM_EXT_FILES'] = ftypes['ext'].num_passed
        spec_props['NUM_TCORR_FILES'] = ftypes['tcorr'].num_passed
        spec_props['NUM_PP_FILES_FAIL'] = ftypes['pp'].num_failed
        spec_props['NUM_EXT_FILES_FAIL'] = ftypes['ext'].num_failed
        spec_props['NUM_TCORR_FILES_FAIL'] = ftypes['tcorr'].num_failed
        # -----------------------------------------------------------------
        # add the first and last raw file type
        first_time = self.filetypes['raw'].first
        last_time = self.filetypes['raw'].last
        if first_time is not None:
            spec_props['FIRST_RAW'] = first_time.iso
        else:
            spec_props['FIRST_RAW'] = None
        if last_time is not None:
            spec_props['LAST_RAW'] = last_time.iso
        else:
            spec_props['LAST_RAW'] = None
        # Add first / last pp files
        if ftypes['pp'].num_passed > 0:
            spec_props['FIRST_PP'] = Time(np.min(hdict['PP_MJDMID'])).iso
            spec_props['LAST_PP'] = Time(np.max(hdict['PP_MJDMID'])).iso
            spec_props['LAST_PP_PROC'] = Time(np.max(hdict['PP_PROC'])).iso
            spec_props['PP_VERSION'] = ','.join(list(np.unique(hdict['PP_VERSION'])))
        else:
            spec_props['FIRST_PP'] = None
            spec_props['LAST_PP'] = None
            spec_props['LAST_PP_PROC'] = None
            spec_props['PP_VERSION'] = None
            # Add first / last ext files
        if ftypes['ext'].num_passed > 0:
            spec_props['FIRST_EXT'] = Time(np.min(hdict['EXT_MJDMID'])).iso
            spec_props['LAST_EXT'] = Time(np.max(hdict['EXT_MJDMID'])).iso
            spec_props['LAST_EXT_PROC'] = Time(np.max(hdict['EXT_PROC'])).iso
            spec_props['EXT_VERSION'] = ','.join(list(np.unique(hdict['EXT_VERSION'])))
        else:
            spec_props['FIRST_EXT'] = None
            spec_props['LAST_EXT'] = None
            spec_props['LAST_EXT_PROC'] = None
            spec_props['EXT_VERSION'] = None
        # Add first / last tcorr files
        if ftypes['tcorr'].num_passed > 0:
            spec_props['FIRST_TCORR'] = Time(np.min(hdict['TCORR_MJDMID'])).iso
            spec_props['LAST_TCORR'] = Time(np.max(hdict['TCORR_MJDMID'])).iso
            spec_props['LAST_TCORR_PROC'] = Time(np.max(hdict['TCORR_PROC'])).iso
            spec_props['TCORR_VERSION'] = ','.join(list(np.unique(hdict['TCORR_VERSION'])))
        else:
            spec_props['FIRST_TCORR'] = None
            spec_props['LAST_TCORR'] = None
            spec_props['LAST_TCORR_PROC'] = None
            spec_props['TCORR_VERSION'] = None
        # -----------------------------------------------------------------
        # standard request keyword args
        rkwargs = dict(fiber='Science fiber',
                       dprtypes=SCIENCE_DPRTYPES,
                       apero_mode=params['ARI_USER'])
        # add the links to request data
        spec_props['RLINK_EXT_E2DSFF'] = self.rlink(filetype='ext', **rkwargs)
        spec_props['RLINK_EXT_S1D_V'] = self.rlink(filetype='s1d', **rkwargs)
        spec_props['RLINK_TELLU_OBJ'] = self.rlink(filetype='tcorr', **rkwargs)
        spec_props['RLINK_TELLU_S1DV'] = self.rlink(filetype='sc1d', **rkwargs)
        spec_props['RLINK_TELLU_TEMP'] = self.rlink(drsoutid='TELLU_TEMP',
                                                    **rkwargs)
        spec_props['RLINK_TELLU_TEMP_S1D'] = self.rlink(drsoutid='TELLU_TEMP_S1DV',
                                                        **rkwargs)
        spec_props['RLINK_DRS_POST_E'] = self.rlink(filetype='efiles', **rkwargs)
        spec_props['RLINK_DRS_POST_T'] = self.rlink(filetype='tfiles', **rkwargs)
        spec_props['RLINK_DRS_POST_S'] = self.rlink(drsoutid='DRS_POST_S',
                                                    **rkwargs)
        spec_props['RLINK_DRS_POST_V'] = self.rlink(filetype='vfiles', **rkwargs)
        spec_props['RLINK_DRS_POST_P'] = self.rlink(filetype='pfiles', **rkwargs)
        # -----------------------------------------------------------------
        # we have to match files (as ext_files, tcorr_files and raw_files may
        #   be different lengths)
        matched = False
        # get the median snr
        med_snr = np.nanmedian(ext_h)
        n_ext_h = abs(ext_h - med_snr)
        # sort all snr by closest to the median
        all_snr_pos = list(np.argsort(n_ext_h))
        # set these up
        pos_ext, pos_raw, pos_s1d, pos_sc1d = None, None, None, None
        file_ext = 'NoFile'
        # loop until we match
        while not matched and len(all_snr_pos) > 0:
            # Find the closest to the median
            pos_ext = all_snr_pos[0]
            # set the filename
            file_ext = spec_props['EXT'].get_files()[pos_ext]
            # Find the matching raw file
            pos_raw = _match_file(reffile=file_ext,
                                  files=spec_props['RAW'].get_files(qc=True))
            pos_s1d = _match_file(reffile=file_ext,
                                  files=spec_props['S1D'].get_files(qc=True))
            pos_sc1d = _match_file(reffile=file_ext,
                                   files=spec_props['SC1D'].get_files(qc=True))
            # three conditions that have to be met for a match
            cond1 = pos_raw is not None
            cond2 = pos_s1d is not None
            cond3 = pos_sc1d is not None
            # we only stop is a match is found
            if cond1 and cond2 and cond3:
                matched = True
            else:
                all_snr_pos = all_snr_pos[1:]
        # ---------------------------------------------------------------------
        cond1 = pos_raw is None
        cond2 = pos_s1d is None
        cond3 = pos_sc1d is None
        # deal with case we have no matching raw file we have a big problem
        #   extracted file cannot exist without a raw file
        if cond1 or cond2 or cond3:
            if cond1:
                print(f'No raw file matching {file_ext}. '
                      f'This should not be possible')
            if cond2 or cond3:
                print(f'No s1d file matching {file_ext}')
            return
        # ---------------------------------------------------------------------
        # get the extracted spectrum for the spectrum with the highest SNR
        ext_file = spec_props['S1D'].get_files(qc=True)[pos_s1d]
        # load the table
        ext_table = drs_table.read_table(params, ext_file, fmt='fits', hdu=1)
        # get wavelength masks for plotting
        wavemap = ext_table['wavelength']
        limits = params['ARI_WAVE_RANGES']
        wavemask0 = (wavemap > limits['limit0'][0])
        wavemask0 &= (wavemap < limits['limit0'][1])
        wavemask1 = (wavemap > limits['limit1'][0])
        wavemask1 &= (wavemap < limits['limit1'][1])
        wavemask2 = (wavemap > limits['limit2'][0])
        wavemask2 &= (wavemap < limits['limit2'][1])
        wavemask3 = (wavemap > limits['limit3'][0])
        wavemask3 &= (wavemap < limits['limit3'][1])
        # ---------------------------------------------------------------------
        # push into spec_props
        spec_props['WAVE'] = np.array(ext_table['wavelength'])
        spec_props['EXT_SPEC'] = np.array(ext_table['flux'])
        spec_props['EXT_SPEC_ERR'] = np.array(ext_table['eflux'])
        spec_props['WAVEMASK0'] = wavemask0
        spec_props['WAVEMASK1'] = wavemask1
        spec_props['WAVEMASK2'] = wavemask2
        spec_props['WAVEMASK3'] = wavemask3
        spec_props['WAVELIM0'] = limits['limit0']
        spec_props['WAVELIM1'] = limits['limit1']
        spec_props['WAVELIM2'] = limits['limit2']
        spec_props['WAVELIM3'] = limits['limit3']
        spec_props['MAX_SNR'] = np.round(spec_props['EXT_H'][pos_ext], 2)
        raw_file = spec_props['RAW'].get_files(qc=True)[pos_raw]
        spec_props['MAX_FILE'] = os.path.basename(raw_file)
        # ---------------------------------------------------------------------
        # deal with having telluric file
        if pos_sc1d is not None:
            # get the telluric corrected spectrum for the spectrum with the
            # highest SNR
            tcorr_file = spec_props['SC1D'].get_files(qc=True)[pos_sc1d]
            # load the table
            tcorr_table = drs_table.read_table(params, tcorr_file, fmt='fits',
                                               hdu=1)
            # push into spec_props
            spec_props['TCORR_SPEC'] = np.array(tcorr_table['flux'])
            spec_props['TCORR_SPEC_ERR'] = np.array(tcorr_table['eflux'])
        else:
            spec_props['TCORR_SPEC'] = None
            spec_props['TCORR_SPEC_ERR'] = None
        # -----------------------------------------------------------------
        # plot the figure
        # -----------------------------------------------------------------
        # get the plot base name
        plot_base_name = 'spec_plot_' + self.objname + '.png'
        # get the plot path
        plot_path = os.path.join(obj_save_path, plot_base_name)
        # plot the lbl figure
        spec_plot(spec_props, plot_path, plot_title=f'{self.objname}')
        # -----------------------------------------------------------------
        # construct the stats
        # -----------------------------------------------------------------
        # get the stats base name
        stat_base_name = 'spec_stat_' + self.objname + '.txt'
        # get the stat path
        stat_path = os.path.join(obj_save_path, stat_base_name)
        # compute the stats
        spec_stats_table(spec_props, stat_path, title='Spectrum Information')
        # -----------------------------------------------------------------
        # construct the header file
        ext_header_file = os.path.join(obj_save_path,
                                       f'ext2d_header_{self.objname}_file.csv')
        create_header_file(spec_props['EXT'].get_files(qc=True),
                           self.headers, 'ext', self.header_dict,
                           ext_header_file)
        # -----------------------------------------------------------------
        # Create the request link table for this object
        # -----------------------------------------------------------------
        # get the rlink base name
        rlink_base_name = 'spec_rlink_' + self.objname + '.txt'
        # get the rlink table path
        rlink_item_path = os.path.join(obj_save_path, rlink_base_name)
        # define the keys in spec_props that contain rlinks to add
        rlinks = ['RLINK_EXT_E2DSFF', 'RLINK_EXT_S1D_V',
                  'RLINK_TELLU_OBJ', 'RLINK_TELLU_S1DV',
                  'RLINK_TELLU_TEMP', 'RLINK_TELLU_TEMP_S1D',
                  'RLINK_DRS_POST_E', 'RLINK_DRS_POST_T',
                  'RLINK_DRS_POST_S', 'RLINK_DRS_POST_V',
                  'RLINK_DRS_POST_P']
        # define the rlink descriptions
        rlink_text = ['Extracted 2D spectra', 'Extracted 1D spectra',
                      'Telluric corrected 2D spectra',
                      'Telluric corrected 1D spectra',
                      '2D Template (after telluric correction)',
                      '1D Template (after telluric correction)',
                      'Packaged extraction files (e.fits)',
                      'Packaged telluric corrected files (t.fits)',
                      'Packaged s1d extract+tcorr (s.fits)',
                      'Packaged velocity files (v.fits)',
                      'Packaged polarimetry files (p.fits)']
        # compute the rlink table
        create_request_link_table(spec_props, rlink_item_path, rlinks,
                                  rlink_text)
        # -----------------------------------------------------------------
        # Create the file lists for this object
        # -----------------------------------------------------------------
        # construct the save path for ext files (2D)
        ext2d_file = os.path.join(obj_save_path,
                                  f'ext2d_{self.objname}_file_list.txt')
        create_file_list(spec_props['EXT'].get_files(qc=True), ext2d_file)
        # construct the save path for ext files (1D)
        ext1d_file = os.path.join(obj_save_path,
                                  f'ext1d_{self.objname}_file_list.txt')
        create_file_list(spec_props['S1D'].get_files(qc=True), ext1d_file)
        # construct the save path for the tcorr files (2D)
        tcorr2d_file = os.path.join(obj_save_path,
                                    f'tcorr2d_{self.objname}_file_list.txt')
        create_file_list(spec_props['TCORR'].get_files(qc=True), tcorr2d_file)
        # construct the save path for the tcorr files (1D)
        tcorr1d_file = os.path.join(obj_save_path,
                                    f'tcorr1d_{self.objname}_file_list.txt')
        create_file_list(spec_props['SC1D'].get_files(qc=True), tcorr1d_file)
        # -----------------------------------------------------------------
        # construct the download table
        # -----------------------------------------------------------------
        # get the download base name
        dwn_base_name = 'spec_download_' + self.objname + '.txt'
        # get the download table path
        dwn_item_path = os.path.join(obj_save_path, dwn_base_name)
        # define the download files
        down_files = [ext2d_file, ext1d_file, tcorr2d_file, tcorr1d_file,
                      ext_header_file]
        # define the download descriptions
        down_descs = ['Extracted 2D spectra', 'Extracted 1D spectra',
                      'Telluric corrected 2D spectra',
                      'Telluric corrected 1D spectra',
                      'Extracted 2D header file']
        # compute the download table
        download_table(down_files, down_descs, dwn_item_path, '',
                       obj_save_path, title='Spectrum Downloads')
        # -----------------------------------------------------------------
        # update the paths
        self.spec_plot_path = plot_base_name
        self.spec_stats_table = stat_base_name
        self.spec_rlink_table = rlink_base_name
        self.spec_dwn_table = dwn_base_name

    # -------------------------------------------------------------------------
    # LBL functions
    # -------------------------------------------------------------------------
    def get_lbl_parameters(self, params: ParamDict):
        """
        Get the LBL parameters for this object

        :return:
        """
        # set up the object page
        obj_save_path = os.path.join(params['ARI_OBJ_PAGES'], self.objname)
        # get lbl rdb files
        lbl_files = dict()
        for filetype in LBL_FILETYPES:
            if self.filetypes[filetype].num > 0:
                lbl_files[filetype] = self.filetypes[filetype].get_files()

        # don't go here is lbl rdb files are not present
        if len(lbl_files) == 0:
            return
        # ---------------------------------------------------------------------
        # storage of properties
        lbl_props = dict()
        # ---------------------------------------------------------------------
        # get the ext h-band key
        ext_h_key = self.headers['LBL']['EXT_H']['key']
        # store the object+ template combinations
        lbl_objtmps = dict()
        # loop around templates (found previously)
        for template in self.lbl_templates:
            # make objtmp string
            lbl_objtmp = f'{self.objname}_{template}'
            # set each template to have a dictionary of files
            lbl_objtmps[lbl_objtmp] = dict()
            # loop around each lbl file type
            for lbl_filetype in lbl_files:
                # file to be found
                matched_file = None
                # find the file that matches the template
                for lbl_file in lbl_files[lbl_filetype]:
                    if lbl_objtmp in lbl_file:
                        matched_file = lbl_file
                        break
                # append to list if we found a matching objname+template file
                if matched_file is not None:
                    lbl_objtmps[lbl_objtmp][lbl_filetype] = matched_file
        # ---------------------------------------------------------------------
        # def the plot file
        plot_file = LBL_FILETYPES[LBL_PLOT_FILE]
        # loop around the objname+template combinations
        for lbl_objtmp in lbl_objtmps:
            # deal with the plot file not existing
            if plot_file not in lbl_objtmps[lbl_objtmp]:
                # must set these to None if no LBL files
                self.lbl_plot_path[lbl_objtmp] = None
                self.lbl_stats_table[lbl_objtmp] = None
                self.lbl_rlink_table[lbl_objtmp] = None
                self.lbl_dwn_table[lbl_objtmp] = None
                continue
            # get the plot file for this objname+template
            lbl_pfile = lbl_objtmps[lbl_objtmp][plot_file]
            # load rdb file
            rdb_table = drs_table.read_table(params, lbl_pfile, fmt='ascii.rdb')
            # get the values required
            lbl_props['rjd'] = np.array(rdb_table['rjd'])
            lbl_props['vrad'] = np.array(rdb_table['vrad'])
            lbl_props['svrad'] = np.array(rdb_table['svrad'])
            lbl_props['plot_date'] = np.array(rdb_table['plot_date'])
            lbl_props['snr_h'] = np.array(rdb_table[ext_h_key])
            lbl_props['SNR_H_LABEL'] = self.headers['LBL']['EXT_H']['label']
            lbl_props['RESET_RV'] = np.array(rdb_table['RESET_RV']).astype(bool)
            lbl_props['NUM_RESET_RV'] = np.sum(rdb_table['RESET_RV'])
            # get the lbl header key
            lbl_version_hdrkey = self.headers['LBL']['LBL_VERSION']['key']
            # find the lbl fits file
            for it, lblfilekey in enumerate(LBL_FILETYPES):
                if lblfilekey == 'lbl_fits':
                    # get the lbl file
                    lbl_file = lbl_objtmps[lbl_objtmp][lblfilekey]
                    # get the header
                    lbl_hdr = fits.getheader(lbl_file)
                    # if we have the lbl version header key add it
                    if lbl_version_hdrkey in lbl_hdr:
                        lbl_props['version'] = lbl_hdr[lbl_version_hdrkey]
            # -----------------------------------------------------------------
            # standard request keyword args
            rkwargs = dict(fiber='Science fiber',
                           dprtypes=SCIENCE_DPRTYPES,
                           apero_mode=params['ARI_USER'])
            # add the links to request data
            lbl_props['RLINK_LBL_FITS'] = self.rlink(filetype='lbl.fits',
                                                     **rkwargs)
            for filetype in LBL_FILETYPES:
                lbl_props[f'RLINK_{filetype}'] = self.rlink(filetype=filetype,
                                                            **rkwargs)

            # -----------------------------------------------------------------
            # plot the figure
            # -----------------------------------------------------------------
            # get the plot base name
            plot_base_name = 'lbl_plot_' + lbl_objtmp + '.png'
            # get the plot path
            plot_path = os.path.join(obj_save_path, plot_base_name)
            # plot the lbl figure
            lbl_props = lbl_plot(lbl_props, plot_path,
                                 plot_title=f'LBL {lbl_objtmp}')
            # -----------------------------------------------------------------
            # construct the stats
            # -----------------------------------------------------------------
            # get the stats base name
            stat_base_name = 'lbl_stat_' + lbl_objtmp + '.txt'
            # get the stat path
            stat_path = os.path.join(obj_save_path, stat_base_name)
            # compute the stats
            lbl_stats_table(lbl_props, stat_path, title='LBL stats')
            # -----------------------------------------------------------------
            # Create the request link table for this object
            # -----------------------------------------------------------------
            # get the rlink base name
            rlink_base_name = 'lbl_rlink_' + self.objname + '.txt'
            # get the rlink table path
            rlink_item_path = os.path.join(obj_save_path, rlink_base_name)
            # define the keys in spec_props that contain rlinks to add
            rlinks = ['RLINK_LBL_FITS']
            for filetype in LBL_FILETYPES:
                rlinks += [f'RLINK_{filetype}']

            # define the rlink descriptions
            rlink_text = ['LBL fits files']
            for filetype in LBL_FILETYPES:
                rlink_text += [f'{filetype} files']
            # compute the rlink table
            create_request_link_table(lbl_props, rlink_item_path, rlinks,
                                      rlink_text)
            # -----------------------------------------------------------------
            # construct the download table
            # -----------------------------------------------------------------
            # get the download base name
            dwn_base_name = 'lbl_download_' + lbl_objtmp + '.txt'
            # get the download table path
            dwn_item_path = os.path.join(obj_save_path, dwn_base_name)
            # define the download files
            down_files = []
            # define the download descriptions
            down_descs = []
            # add the lbl files to the down files
            for it, lblfilekey in enumerate(LBL_FILETYPES):
                # check that we want to add to download files
                if not LBL_DOWNLOAD[it]:
                    continue
                # check for file in lbl_objtmps
                if lblfilekey not in lbl_objtmps[lbl_objtmp]:
                    continue
                # get lbl file
                lbl_file = lbl_objtmps[lbl_objtmp][lblfilekey]
                # add to down_files
                down_files.append(lbl_file)
                down_descs.append(LBL_FILE_DESC[it])
            # Add the lbl stat files
            for lblfilekey in LBL_STAT_FILES:
                # deal with no lbl file key for this object
                if lblfilekey not in self.lbl_stat_files:
                    continue
                # deal with this obj+templ being present
                if lbl_objtmp in self.lbl_stat_files[lblfilekey]:
                    # get lblsfile
                    lblsfile = self.lbl_stat_files[lblfilekey][lbl_objtmp]
                    # add to the list
                    down_files.append(lblsfile)
                    # add to the list
                    down_descs.append(lblfilekey)
            # compute the download table
            download_table(down_files, down_descs, dwn_item_path, '',
                           obj_save_path, title='LBL Downloads')
            # -----------------------------------------------------------------
            # update the paths
            self.lbl_plot_path[lbl_objtmp] = plot_base_name
            self.lbl_stats_table[lbl_objtmp] = stat_base_name
            self.lbl_rlink_table[lbl_objtmp] = rlink_base_name
            self.lbl_dwn_table[lbl_objtmp] = dwn_base_name
        # ---------------------------------------------------------------------
        # set the lbl combinations
        self.lbl_combinations = list(lbl_objtmps.keys())

    # -------------------------------------------------------------------------
    # CCF functions
    # -------------------------------------------------------------------------
    def get_ccf_parameters(self, params: ParamDict):
        # set up the object page
        obj_save_path = os.path.join(params['ARI_OBJ_PAGES'], self.objname)
        # get ccf files
        ccf_files = self.filetypes['ccf'].get_files(qc=True)
        # don't go here is lbl rdb files are not present
        if len(ccf_files) == 0:
            return
        # -----------------------------------------------------------------
        # alias to header dict
        hdict = self.header_dict
        # storage for ccf values
        ccf_props = dict()
        # get values for use in plot
        ccf_props['mjd'] = Time(np.array(hdict['CCF_MJDMID']))
        dv_vec = hdict['CCF_DV'].to(uu.m / uu.s).value
        ccf_props['dv'] = np.array(dv_vec)
        sdv_vec = hdict['CCF_SDV'].to(uu.m / uu.s).value
        ccf_props['sdv'] = np.array(sdv_vec)
        fwhm_vec = hdict['CCF_FWHM'].to(uu.m / uu.s).value
        ccf_props['fwhm'] = np.array(fwhm_vec)
        ccf_props['masks'] = np.array(hdict['CCF_MASK'])
        ccf_props['files'] = self.filetypes['ccf'].get_files(qc=True)
        ccf_props['files_failed'] = self.filetypes['ccf'].get_files(qc=False)
        # -----------------------------------------------------------------
        ccf_props['FIRST_CCF'] = Time(np.min(hdict['CCF_MJDMID'])).iso
        ccf_props['LAST_CCF'] = Time(np.max(hdict['CCF_MJDMID'])).iso
        ccf_props['LAST_CCF_PROC'] = Time(np.max(hdict['CCF_PROC'])).iso
        # -----------------------------------------------------------------
        # ccf version
        ccf_props['CCF_VERSION'] = ','.join(list(np.unique(hdict['CCF_VERSION'])))
        # -----------------------------------------------------------------
        # standard request keyword args
        rkwargs = dict(fiber='Science fiber',
                       dprtypes=SCIENCE_DPRTYPES,
                       apero_mode=params['ARI_USER'])
        # add the links to request data
        ccf_props['RLINK_CCF'] = self.rlink(filetype='ccf', **rkwargs)
        # -----------------------------------------------------------------
        # select ccf files to use
        ccf_props = choose_ccf_files(ccf_props)
        # load the first file to get the rv vector
        ccf_table0 = drs_table.read_table(params, ccf_props['select_files'][0],
                                          fmt='fits', hdu=1)
        # get the rv vector
        ccf_props['rv_vec'] = ccf_table0['RV']
        # storage for the CCF vectors
        all_ccf = np.zeros((len(ccf_props['select_files']), len(ccf_table0)))
        # loop around all other files, load them and load into all_ccf
        for row, select_file in enumerate(ccf_props['select_files']):
            table_row = drs_table.read_table(params, select_file,
                                             fmt='fits', hdu=1)
            # get the combined CCF for this file
            ccf_row = table_row['Combined']
            # normalize ccf
            ccf_row = ccf_row / np.nanmedian(ccf_row)
            # push into vector
            all_ccf[row] = ccf_row
        # -----------------------------------------------------------------
        # get the 1 and 2 sigma limits
        lower_sig1 = 100 * (0.5 - normal_fraction(1) / 2)
        upper_sig1 = 100 * (0.5 + normal_fraction(1) / 2)
        lower_sig2 = 100 * (0.5 - normal_fraction(2) / 2)
        upper_sig2 = 100 * (0.5 + normal_fraction(2) / 2)
        # -----------------------------------------------------------------
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
        # delete all_ccf to save memeory
        del all_ccf
        # fit the median ccf
        ccf_props = fit_ccf(ccf_props)
        # -----------------------------------------------------------------
        # plot the figure
        # -----------------------------------------------------------------
        # get the plot base name
        plot_base_name = 'ccf_plot_' + self.objname + '.png'
        # get the plot path
        plot_path = os.path.join(obj_save_path, plot_base_name)
        # set the plot title
        plot_title = f'CCF {self.objname} [mask={ccf_props["chosen_mask"]}]'
        # plot the lbl figure
        ccf_plot(ccf_props, plot_path, plot_title=plot_title)
        # -----------------------------------------------------------------
        # construct the stats
        # -----------------------------------------------------------------
        # get the stats base name
        stat_base_name = 'ccf_stat_' + self.objname + '.txt'
        # get the stat path
        stat_path = os.path.join(obj_save_path, stat_base_name)
        # compute the stats
        ccf_stats_table(ccf_props, stat_path, title='CCF stats')
        # -----------------------------------------------------------------
        # Create the request link table for this object
        # -----------------------------------------------------------------
        # get the rlink base name
        rlink_base_name = 'ccf_rlink_' + self.objname + '.txt'
        # get the rlink table path
        rlink_item_path = os.path.join(obj_save_path, rlink_base_name)
        # define the keys in spec_props that contain rlinks to add
        rlinks = ['RLINK_CCF']
        # define the rlink descriptions
        rlink_text = ['CCF files']
        # compute the rlink table
        create_request_link_table(ccf_props, rlink_item_path, rlinks,
                                  rlink_text)
        # -----------------------------------------------------------------
        # Create the file lists for this object
        # -----------------------------------------------------------------
        # construct the save path for ccf files
        ccf_file = os.path.join(obj_save_path,
                                f'ccf_{self.objname}_file_list.txt')
        create_file_list(ccf_files, ccf_file)
        # -----------------------------------------------------------------
        # construct the download table
        # -----------------------------------------------------------------
        # get the download base name
        dwn_base_name = 'ccf_download_' + self.objname + '.txt'
        # get the download table path
        dwn_item_path = os.path.join(obj_save_path, dwn_base_name)
        # define the download files
        down_files = [ccf_file]
        # define the download descriptions
        down_descs = ['CCF Table']
        # compute the download table
        download_table(down_files, down_descs, dwn_item_path, '',
                       obj_save_path, title='CCF Downloads')
        # -----------------------------------------------------------------
        # update the paths
        self.ccf_plot_path = plot_base_name
        self.ccf_stats_table = stat_base_name
        self.ccf_rlink_table = rlink_base_name
        self.ccf_dwn_table = dwn_base_name

    # -------------------------------------------------------------------------
    # Time Series functions
    # -------------------------------------------------------------------------
    def get_time_series_parameters(self, params: ParamDict):
        # set up the object page
        obj_save_path = os.path.join(params['ARI_OBJ_PAGES'], self.objname)
        # get ext files
        ftypes = self.filetypes
        ext_files_all = ftypes['ext'].get_files(qc=True)
        tcorr_files_all = ftypes['tcorr'].get_files(qc=True)
        # don't go here is lbl rdb files are not present
        if len(ext_files_all) == 0:
            return
        # -----------------------------------------------------------------
        # storage for ccf values
        ts_props = dict()
        # get labels
        snr_y_label = self.headers['ext']['EXT_Y']['label']
        snr_y_label = snr_y_label.replace(r'$\mu$', 'u')
        snr_h_label = self.headers['ext']['EXT_H']['label']
        snr_h_label = snr_h_label.replace(r'$\mu$', 'u')
        ext_col = 'ext_files'
        tcorr_col = 'tcorr_files'
        rlink_ext_col = 'Request ext files'
        rlink_tcorr_col = 'Request tcorr files'
        # ---------------------------------------------------------------------
        # construct the stats table
        # ---------------------------------------------------------------------
        # columns
        ts_props['columns'] = TIME_SERIES_COLS[0:9]
        ts_props['columns'] += [snr_y_label, snr_h_label]
        ts_props['columns'] += [TIME_SERIES_COLS[9]]
        ts_props['columns'] += [ext_col, tcorr_col]
        ts_props['columns'] += [rlink_ext_col, rlink_tcorr_col]
        # get values for use in time series table
        for time_series_col in TIME_SERIES_COLS:
            ts_props[time_series_col] = []
        ts_props[snr_y_label] = []
        ts_props[snr_h_label] = []
        ts_props[ext_col] = []
        ts_props[tcorr_col] = []
        ts_props[rlink_ext_col] = []
        ts_props[rlink_tcorr_col] = []
        # get values from self.header_dict
        mjd_vec = np.array(self.header_dict['EXT_MJDMID'])
        seeing_vec = np.array(self.header_dict['EXT_SEEING'])
        airmass_vec = np.array(self.header_dict['EXT_AIRMASS'])
        exptime_vec = np.array(self.header_dict['EXT_EXPTIME'])
        snry_vec = np.array(self.header_dict['EXT_Y'])
        snyh_vec = np.array(self.header_dict['EXT_H'])
        dprtype_vec = np.array(self.header_dict['EXT_DPRTYPE'])
        # get the obs dirs for files that passed qc
        obs_dirs_ext = ftypes['ext'].get_files(qc=True, attr='obsdirs')
        obs_dirs_tcorr = ftypes['tcorr'].get_files(qc=True, attr='obsdirs')
        # get unique object directories (for this object)
        u_obs_dirs = np.unique(obs_dirs_ext)
        # loop around observation directories
        for obs_dir in u_obs_dirs:
            # create a mask for this observation directory
            obs_mask_ext = obs_dirs_ext == obs_dir
            obs_mask_tcorr = obs_dirs_tcorr == obs_dir
            # get the first and last mjd for this observation directory
            first_time = Time(np.min(mjd_vec[obs_mask_ext]))
            last_time = Time(np.max(mjd_vec[obs_mask_ext]))
            first_iso = first_time.iso
            last_iso = last_time.iso
            # get the number of observations for this observation
            num_obs_ext = str(np.sum(obs_mask_ext))
            num_obs_tcorr = str(np.sum(obs_mask_tcorr))
            # get the seeing for this observation directory
            # TODO: nanmean for all below?
            seeing = np.mean(seeing_vec[obs_mask_ext])
            seeing = '{:.3f}'.format(seeing)
            # get the airmass for this observation directory
            airmass = np.mean(airmass_vec[obs_mask_ext])
            airmass = '{:.3f}'.format(airmass)
            # get the mean exposure time
            exptime = np.mean(exptime_vec[obs_mask_ext])
            exptime = '{:.3f}'.format(exptime)
            # get the total exposure time
            texptime = np.sum(exptime_vec[obs_mask_ext])
            texptime = '{:.3f}'.format(texptime)
            # get the mean snr_y
            snry = np.mean(snry_vec[obs_mask_ext])
            snry = '{:.3f}'.format(snry)
            # get the mean snr_h
            snyh = np.mean(snyh_vec[obs_mask_ext])
            snyh = '{:.3f}'.format(snyh)
            # get the dprtypes
            dprtype = ','.join(list(np.unique(dprtype_vec[obs_mask_ext])))
            # -----------------------------------------------------------------
            # Create the ext and tellu for this object
            # -----------------------------------------------------------------
            ext_files = ext_files_all[obs_mask_ext]
            tcorr_files = tcorr_files_all[obs_mask_tcorr]
            # -----------------------------------------------------------------
            # Create the file lists for this object
            # -----------------------------------------------------------------
            # construct the save path for ext files
            ext_file = f'ext_file_list_{obs_dir}_{self.objname}.txt'
            ext_path = os.path.join(obj_save_path, ext_file)
            ext_rel_path = ext_file
            create_file_list(ext_files, ext_path)
            ext_download = drs_markdown.make_download('[download]',
                                                      ext_rel_path)
            ext_value = f'{len(ext_files)} {ext_download}'
            # construct the save path for the tcorr files
            tcorr_file = f'tcorr_file_list_{obs_dir}_{self.objname}.txt'
            tcorr_path = os.path.join(obj_save_path, tcorr_file)
            tcorr_rel_path = tcorr_file
            create_file_list(tcorr_files, tcorr_path)
            tcorr_download = drs_markdown.make_download('[download]',
                                                        tcorr_rel_path)
            tcorr_value = f'{len(tcorr_files)} {tcorr_download}'
            # -----------------------------------------------------------------
            # append to the time series properties
            ts_props[TIME_SERIES_COLS[0]].append(obs_dir)
            ts_props[TIME_SERIES_COLS[1]].append(first_iso)
            ts_props[TIME_SERIES_COLS[2]].append(last_iso)
            ts_props[TIME_SERIES_COLS[3]].append(num_obs_ext)
            ts_props[TIME_SERIES_COLS[4]].append(num_obs_tcorr)
            ts_props[TIME_SERIES_COLS[5]].append(seeing)
            ts_props[TIME_SERIES_COLS[6]].append(airmass)
            ts_props[TIME_SERIES_COLS[7]].append(exptime)
            ts_props[TIME_SERIES_COLS[8]].append(texptime)
            ts_props[snr_y_label].append(snry)
            ts_props[snr_h_label].append(snyh)
            ts_props[TIME_SERIES_COLS[9]].append(dprtype)
            ts_props[ext_col].append(ext_value)
            ts_props[tcorr_col].append(tcorr_value)
            # -----------------------------------------------------------------
            # standard request keyword args
            rkwargs = dict(fiber='Science fiber',
                           dprtypes=SCIENCE_DPRTYPES,
                           apero_mode=params['ARI_USER'])
            # get the date YYYY-MM-DD format
            rlink_start = first_time.strftime('%Y-%m-%d')
            rlink_end = last_time.strftime('%Y-%m-%d')
            # deal with rlink_start and end being the same
            if rlink_end == rlink_start:
                tdelta = TimeDelta(1 * uu.day)
                rlink_end = (last_time + tdelta).strftime('%Y-%m-%d')
            # add the links to request data
            time_series_ext_rlink = self.rlink(filetype='ext',
                                               startdate=rlink_start,
                                               enddate=rlink_end, **rkwargs)
            time_series_tcorr_rlink = self.rlink(filetype='tcorr',
                                                 startdate=rlink_start,
                                                 enddate=rlink_end, **rkwargs)
            # -----------------------------------------------------------------
            # Create the request link table for this object
            # -----------------------------------------------------------------
            # add the ext rlink
            if time_series_ext_rlink is not None:
                rargs = ['Extracted 2D files', time_series_ext_rlink]
                ts_props[rlink_ext_col].append('`{0} <{1}>`_'.format(*rargs))
            # add the corr rlink
            if time_series_tcorr_rlink is not None:
                rargs = ['Telluric corrected 2D files', time_series_tcorr_rlink]
                ts_props[rlink_tcorr_col].append('`{0} <{1}>`_'.format(*rargs))
        # -----------------------------------------------------------------
        # construct the stats
        # -----------------------------------------------------------------
        # get the stats base name
        time_series_base_name = 'time_series_stat_' + self.objname + '.txt'
        # get the stat path
        stat_path = os.path.join(obj_save_path, time_series_base_name)
        # compute the stats
        time_series_stats_table(ts_props, stat_path)
        # -----------------------------------------------------------------
        # update the paths
        self.time_series_plot_path = None
        self.time_series_stats_table = time_series_base_name
        self.time_series_dwn_table = None

    # -------------------------------------------------------------------------
    # General page functions
    # -------------------------------------------------------------------------
    def rlink(self, filetype: Optional[str] = None,
              startdate: Optional[str] = None,
              enddate: Optional[str] = None,
              apero_mode: Optional[str] = None,
              fiber: Optional[str] = None,
              dprtypes: Optional[str] = None,
              drsoutid: Optional[str] = None):
        """
        Create a link to pre-fill the request form

        :param filetype: str, the filetype (FileType.name) to use
        :param startdate: optional str, the start date DD/MM/YYYY
        :param enddate: optional str, the end date DD/MM/YYYY
        :param apero_mode: optional str, the apero mode to use (e.g.
                           nirps_he_online)
        :param fiber: optional str, the fibers to get should be one of
                      "Science fiber", "Reference fiber", "All fibers"
        :param dprtypes: optional str, the dprtypes
        :param drsoutid: optional str, the drsoutid (not used if filetype is
                         defined)
        :return:
        """
        # lets create a url
        url = PREFILLED_REQUEST_LINK
        # get the objname
        url += _url_addp(PREFILLED_RDICT['OBJNAMES'], self.objname)
        # add the start date
        if startdate is not None:
            url += _url_addp(PREFILLED_RDICT['STARTDATE'], startdate)
        # add the end date
        if enddate is not None:
            url += _url_addp(PREFILLED_RDICT['ENDDATE'], enddate)
        # add the apero mode
        if apero_mode is not None:
            url += _url_addp(PREFILLED_RDICT['APERO_MODE'], apero_mode)
        # add the fiber
        if fiber is not None and fiber in RDICT_FIBERS:
            url += _url_addp(PREFILLED_RDICT['FIBER'], fiber)
        # add the dprtypes
        if dprtypes is not None:
            url += _url_addp(PREFILLED_RDICT['DPRTYPES'], dprtypes)
        else:
            dprtypes = np.char.array(SCIENCE_DPRTYPES)
            dprtypes = list(dprtypes.strip())
            url += _url_addp(PREFILLED_RDICT['DPRTYPES'], dprtypes)
        # add the drsoutids using filetype
        if filetype in self.filetypes:
            # get the file instance class
            fileinst = self.filetypes[filetype]
            # add the drsoutids
            url += _url_addp(PREFILLED_RDICT['DRSOUTID'], fileinst.kw_output)
        elif drsoutid is not None:
            # add the drsoutids
            url += _url_addp(PREFILLED_RDICT['DRSOUTID'], drsoutid)
        # return the url
        return url


class AriRecipe:
    def __init__(self):
        self.obsdir = None
        self.numtotal = None
        self.numfail = None
        self.link = None
        self.recipes = dict()
        self.yamlfile = None

    @staticmethod
    def from_yaml(yaml_abs_path):
        # load yaml file into dictionary
        yaml_dict = base.load_yaml(yaml_abs_path)
        # create instance of AriRecipe
        ari_recipe = AriRecipe()
        # store the yaml file
        ari_recipe.yamlfile = yaml_abs_path
        # store the obsdir
        ari_recipe.obsdir = yaml_dict['obsdir']
        # store the numtotal
        ari_recipe.numtotal = yaml_dict['numtotal']
        # store the numfail
        ari_recipe.numfail = yaml_dict['numfail']
        # store the link
        ari_recipe.link = yaml_dict['link']
        # get the recipes
        ari_recipe.recipes = yaml_dict['recipes']

    def save_yaml(self, params: ParamDict):
        # get the recipe yaml directory
        yaml_path = params['ARI_RECIPE_YAMLS']
        # construct the filename
        self.yamlfile = str(os.path.join(yaml_path, self.obsdir + '.yaml'))
        # ----------------------------------------------------------------------
        # create the yaml dictionary
        yaml_dict = dict()
        # store the obsdir
        yaml_dict['obsdir'] = self.obsdir
        # store the numtotal
        yaml_dict['numtotal'] = self.numtotal
        # store the numfail
        yaml_dict['numfail'] = self.numfail
        # store the link
        yaml_dict['link'] = self.link
        # store the recipes
        yaml_dict['recipes'] = self.recipes
        # ----------------------------------------------------------------------
        # save the yaml file
        base.write_yaml(yaml_dict, self.yamlfile)


# =============================================================================
# Define functions
# =============================================================================
def ari_filetypes(params: ParamDict) -> Dict[str, FileType]:
    # load pseudo-constants from apero
    pconst = constants.pload()
    # get the science fiber from pconst
    science_fibers, ref_fiber = pconst.FIBER_KINDS()
    # we assume the first science fiber is the primary science fiber
    science_fiber = science_fibers[0]
    # get has_polar criteria
    has_polar = get_has_polar(params)
    # define types of files we want to count
    filetypes = dict()
    filetypes['raw'] = FileType('raw', block_kind='raw')
    filetypes['pp'] = FileType('pp', block_kind='tmp', chain='raw')
    filetypes['ext'] = FileType('ext', block_kind='red', chain='pp',
                                kw_output='EXT_E2DS_FF', fiber=science_fiber)
    filetypes['tcorr'] = FileType('tcorr', block_kind='red', chain='ext',
                                  kw_output='TELLU_OBJ',
                                  fiber=science_fiber)
    filetypes['ccf'] = FileType('ccf', block_kind='red', chain='tcorr',
                                kw_output='CCF_RV', fiber=science_fiber)
    filetypes['polar'] = FileType('polar', block_kind='red', chain='tcorr',
                                  kw_output='POL_DEG',
                                  fiber=science_fiber, count=has_polar)
    filetypes['efiles'] = FileType('efiles', block_kind='out', chain='pp',
                                   kw_output='DRS_POST_E')
    filetypes['tfiles'] = FileType('tfiles', block_kind='out', chain='ext',
                                   kw_output='DRS_POST_T')
    filetypes['vfiles'] = FileType('vfiles', block_kind='out', chain='tcorr',
                                   kw_output='DRS_POST_V')
    filetypes['pfiles'] = FileType('pfiles', block_kind='out', chain='tcorr',
                                   kw_output='DRS_POST_P', count=has_polar)
    filetypes['s1d'] = FileType('s1d', block_kind='red', chain='ext',
                                kw_output='EXT_S1D_V', fiber=science_fiber)
    filetypes['sc1d'] = FileType('sc1d', block_kind='red', chain='tcorr',
                                 kw_output='SC1D_V_FILE', fiber=science_fiber)
    # lbl files added as filetype but don't count in same was as other files
    filetypes['lbl.fits'] = FileType('lbl.fits', count=False)
    for filetype in LBL_FILETYPES:
        filetypes[filetype] = FileType(filetype, count=False)

    return filetypes


def get_has_polar(params: ParamDict) -> bool:
    # get polar condition
    has_polar = HAS_POLAR[params['INSTRUMENT']]
    # return has polar
    return has_polar


# =============================================================================
# Target info page functions
# =============================================================================
def target_stats_table(target_props: Dict[str, Any], stat_path: str,
                       title: str):

    # get parameters from props
    coord_url = target_props['COORD_URL']
    ra, dec = target_props['RA'], target_props['Dec']
    teff, spt = target_props['Teff'], target_props['Spectral Type']
    pmra = target_props['Proper motion RA']
    pmde = target_props['Proper motion Dec']
    plx = target_props['Parallax']
    rv = target_props['RV']
    aliases = target_props['Aliases']

    # --------------------------------------------------------------------------
    # construct the stats table
    # --------------------------------------------------------------------------
    # start with a stats dictionary
    target_dict = dict(Description=[], Value=[])
    # Add RA
    target_dict['Description'].append('RA')
    target_dict['Value'].append(ra)
    # Add Dec
    target_dict['Description'].append('Dec')
    target_dict['Value'].append(dec)
    # Finder chart
    target_dict['Description'].append('Finder chart')
    target_dict['Value'].append(f'`[FINDER CHART] <{coord_url}>`_')
    # Add Teff
    target_dict['Description'].append('Teff')
    target_dict['Value'].append(teff)
    # Add Spectral type
    target_dict['Description'].append('Spectral Type')
    target_dict['Value'].append(spt)
    # Add proper motion (RA)
    target_dict['Description'].append('Proper Motion (RA)')
    target_dict['Value'].append(pmra)
    # Add proper motion (Dec)
    target_dict['Description'].append('Proper Motion (Dec)')
    target_dict['Value'].append(pmde)
    # Add parallax
    target_dict['Description'].append('Parallax')
    target_dict['Value'].append(plx)
    # Add radial velocity
    target_dict['Description'].append('Radial Velocity')
    target_dict['Value'].append(rv)
    # Add aliases
    target_dict['Description'].append('Aliases')
    target_dict['Value'].append(aliases)

    # --------------------------------------------------------------------------
    # change the columns names
    target_dict2 = dict()
    target_dict2[title] = target_dict['Description']
    target_dict2[' '] = target_dict['Value']
    # --------------------------------------------------------------------------
    # convert to table
    target_table = Table(target_dict2)
    # write to file as csv file
    target_table.write(stat_path, format='ascii.csv', overwrite=True)


# =============================================================================
# Spectrum page functions
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
    # --------------------------------------------------------------------------
    # setup the figure
    plt.figure(figsize=(12, 12))
    frame0 = plt.subplot2grid((3, 3), (0, 0), colspan=3, rowspan=1)
    frame1 = plt.subplot2grid((3, 3), (1, 0), colspan=3, rowspan=1)
    frame2a = plt.subplot2grid((3, 3), (2, 0), colspan=1, rowspan=1)
    frame2b = plt.subplot2grid((3, 3), (2, 1), colspan=1, rowspan=1)
    frame2c = plt.subplot2grid((3, 3), (2, 2), colspan=1, rowspan=1)

    # set background color
    frame0.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame1.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame2a.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame2b.set_facecolor(PLOT_BACKGROUND_COLOR)
    frame2c.set_facecolor(PLOT_BACKGROUND_COLOR)
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

    # --------------------------------------------------------------------------
    # Middle plot - full spectra + tcorr
    # --------------------------------------------------------------------------
    title = (f'Spectrum closest to Median {ext_h_label}'
             f'     SNR:{max_snr}     File: {max_file}')

    frame1.plot(wavemap[wavemask0], ext_spec[wavemask0],
                color='k', label='Extracted Spectrum', lw=0.5)
    if tcorr_spec is not None:
        frame1.plot(wavemap[wavemask0], tcorr_spec[wavemask0],
                    color='r', label='Telluric Corrected', lw=0.5)
        frame1.set_ylim((0, 1.5 * np.nanpercentile(tcorr_spec, 99)))
    frame1.set(xlabel='Wavelength [nm]', ylabel='Flux', xlim=wavelim0)
    frame1.set_title(title, fontsize=10)
    frame1.legend(loc=0, ncol=2)
    frame1.grid(which='both', color='lightgray', ls='--')
    # --------------------------------------------------------------------------
    # Bottom plots - Y, J, H spectra + tcorr
    # --------------------------------------------------------------------------
    masks = [wavemask1, wavemask2, wavemask3]
    frames = [frame2a, frame2b, frame2c]
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
    plt.subplots_adjust(bottom=0.05, left=0.06, right=0.99, hspace=0.3,
                        top=0.95)
    # save figure and close the plot
    plt.savefig(plot_path)
    plt.close()


def spec_stats_table(spec_props: Dict[str, Any], stat_path: str, title: str):
    from apero.core.math import estimate_sigma
    # get parameters from props
    num_raw = spec_props['NUM_RAW_FILES']
    num_pp = spec_props['NUM_PP_FILES']
    num_ext = spec_props['NUM_EXT_FILES']
    num_tcorr = spec_props['NUM_TCORR_FILES']

    num_pp_qc = spec_props['NUM_PP_FILES_FAIL']
    num_ext_qc = spec_props['NUM_EXT_FILES_FAIL']
    num_tcorr_qc = spec_props['NUM_TCORR_FILES_FAIL']

    ext_y = spec_props['EXT_Y']
    ext_h = spec_props['EXT_H']
    first_raw = spec_props['FIRST_RAW']
    last_raw = spec_props['LAST_RAW']
    first_pp = spec_props['FIRST_PP']
    last_pp = spec_props['LAST_PP']
    last_pp_proc = spec_props['LAST_PP_PROC']
    first_ext = spec_props['FIRST_EXT']
    last_ext = spec_props['LAST_EXT']
    last_ext_proc = spec_props['LAST_EXT_PROC']
    first_tcorr = spec_props['FIRST_TCORR']
    last_tcorr = spec_props['LAST_TCORR']
    last_tcorr_proc = spec_props['LAST_TCORR_PROC']
    version_pp = spec_props['PP_VERSION']
    version_ext = spec_props['EXT_VERSION']
    version_tcorr = spec_props['TCORR_VERSION']
    dprtypes = spec_props['DPRTYPES']
    # --------------------------------------------------------------------------
    # Calculate stats
    # --------------------------------------------------------------------------
    # average SNR
    med_snr_y = np.nanmedian(ext_y)
    med_snr_h = np.nanmedian(ext_h)
    # RMS of SNR
    rms_snr_y = estimate_sigma(ext_y)
    rms_snr_h = estimate_sigma(ext_h)
    # --------------------------------------------------------------------------
    # construct the stats table
    # --------------------------------------------------------------------------
    # start with a stats dictionary
    stat_dict = dict(Description=[], Value=[])
    # Add dprtypes
    stat_dict['Description'].append('DPRTYPES')
    stat_dict['Value'].append(dprtypes)
    # -------------------------------------------------------------------------
    # add number of raw files
    # -------------------------------------------------------------------------
    stat_dict['Description'].append('Total number raw files')
    stat_dict['Value'].append(f'{num_raw}')
    stat_dict['Description'].append('First raw files')
    stat_dict['Value'].append(f'{first_raw}')
    stat_dict['Description'].append('Last raw files')
    stat_dict['Value'].append(f'{last_raw}')

    # -------------------------------------------------------------------------
    # add number of pp files
    # -------------------------------------------------------------------------
    stat_dict['Description'].append('Total number PP files')
    stat_dict['Value'].append(f'{num_pp + num_pp_qc}')
    stat_dict['Description'].append('Number PP files passed QC')
    stat_dict['Value'].append(f'{num_pp}')
    stat_dict['Description'].append('Number PP files failed QC')
    stat_dict['Value'].append(f'{num_pp_qc}')
    stat_dict['Description'].append('First pp file [Mid exposure]')
    stat_dict['Value'].append(f'{first_pp}')
    stat_dict['Description'].append('Last pp file [Mid exposure]')
    stat_dict['Value'].append(f'{last_pp}')
    stat_dict['Description'].append('Last processed [pp]')
    stat_dict['Value'].append(f'{last_pp_proc}')
    stat_dict['Description'].append('Version [pp]')
    stat_dict['Value'].append(f'{version_pp}')
    # -------------------------------------------------------------------------
    # add number of ext files
    # -------------------------------------------------------------------------
    stat_dict['Description'].append('Total number ext files')
    stat_dict['Value'].append(f'{num_ext + num_ext_qc}')
    stat_dict['Description'].append('Number ext files passed QC')
    stat_dict['Value'].append(f'{num_ext}')
    stat_dict['Description'].append('Number ext files failed QC')
    stat_dict['Value'].append(f'{num_ext_qc}')
    stat_dict['Description'].append('First ext file [Mid exposure]')
    stat_dict['Value'].append(f'{first_ext}')
    stat_dict['Description'].append('Last ext file [Mid exposure]')
    stat_dict['Value'].append(f'{last_ext}')
    stat_dict['Description'].append('Last processed [ext]')
    stat_dict['Value'].append(f'{last_ext_proc}')
    stat_dict['Description'].append('Version [ext]')
    stat_dict['Value'].append(f'{version_ext}')
    # -------------------------------------------------------------------------
    # add number of tcorr files
    # -------------------------------------------------------------------------
    stat_dict['Description'].append('Total number tcorr files')
    stat_dict['Value'].append(f'{num_tcorr + num_tcorr_qc}')
    stat_dict['Description'].append('Number tcorr files passed QC')
    stat_dict['Value'].append(f'{num_tcorr}')
    stat_dict['Description'].append('Number tcorr files failed QC')
    stat_dict['Value'].append(f'{num_tcorr_qc}')
    stat_dict['Description'].append('First tcorr file [Mid exposure]')
    stat_dict['Value'].append(f'{first_tcorr}')
    stat_dict['Description'].append('Last tcorr file [Mid exposure]')
    stat_dict['Value'].append(f'{last_tcorr}')
    stat_dict['Description'].append('Last processed [tcorr]')
    stat_dict['Value'].append(f'{last_tcorr_proc}')
    stat_dict['Description'].append('Version [tcorr]')
    stat_dict['Value'].append(f'{version_tcorr}')
    # -------------------------------------------------------------------------
    # add the SNR in Y
    stat_dict['Description'].append('Median SNR Y')
    value = r'{:.2f} :math:`\pm` {:.2f}'.format(med_snr_y, rms_snr_y)
    stat_dict['Value'].append(value)
    # add the SNR in H
    stat_dict['Description'].append('Median SNR H')
    value = r'{:.2f} :math:`\pm` {:.2f}'.format(med_snr_h, rms_snr_h)
    stat_dict['Value'].append(value)
    # --------------------------------------------------------------------------
    # change the columns names
    stat_dict2 = dict()
    stat_dict2[title] = stat_dict['Description']
    stat_dict2[' '] = stat_dict['Value']
    # --------------------------------------------------------------------------
    # convert to table
    stat_table = Table(stat_dict2)
    # write to file as csv file
    stat_table.write(stat_path, format='ascii.csv', overwrite=True)


# =============================================================================
# LBL page functions
# =============================================================================
def add_lbl_count(params: ParamDict, object_classes: Dict[str, AriObject]
                  ) -> Dict[str, AriObject]:
    # get WLOG
    wlog = drs_log.wlog
    # -------------------------------------------------------------------------
    # get the lbl path
    lbl_path = params['LBL_PATH']
    if lbl_path in params:
        lbl_path = params[lbl_path]
    # -------------------------------------------------------------------------
    # deal with no valid lbl path
    if lbl_path is None:
        return object_classes
    # deal with lbl path not existing
    if not os.path.exists(lbl_path):
        return object_classes
    # print that we are analysing lbl outputs
    wlog(params, '', 'Analysing LBL files')
    # -------------------------------------------------------------------------
    # loop around objects
    for objname in tqdm(object_classes):
        # get the object class for this objname
        object_class = object_classes[objname]
        # ---------------------------------------------------------------------
        # LBL RV files
        # ---------------------------------------------------------------------
        # for each object find all directories in lbl path that match this
        #   object name
        lblrv_dir = glob.glob(os.path.join(lbl_path, 'lblrv', f'{objname}_*'))
        # ---------------------------------------------------------------------
        # deal with no directories --> skip
        if len(lblrv_dir) == 0:
            continue
        # ---------------------------------------------------------------------
        # store a list of templates
        templates = []
        # store a list of counts
        counts = []
        # loop around each directory
        for directory in lblrv_dir:
            # get the template name for each directory
            basename = os.path.basename(directory)
            template = basename.split(f'{objname}_')[-1]
            # get the number of lbl files in each directory
            count = len(glob.glob(os.path.join(directory, '*lbl.fits')))
            # append storage
            templates.append(template)
            counts.append(count)
        # decide which template to use (using max of counts)
        select = np.argmax(counts)
        # get strings to add to storage
        _select = templates[select]
        _count = int(counts[select])
        # --------------------------------------------------------------------
        # deal with the update (do not update if there are no difference
        # in files)
        if _count != object_class.filetypes['lbl.fits']:
            object_class.update = True
        else:
            continue
        # --------------------------------------------------------------------
        # add the counts to the object class
        object_class.lbl_templates = templates
        object_class.lbl_select = _select
        # --------------------------------------------------------------------
        # set the number of files
        object_class.filetypes['lbl.fits'].num = _count
        # ---------------------------------------------------------------------
        # LBL files
        # ---------------------------------------------------------------------
        # loop around all lbl files
        for it, filetype in enumerate(LBL_FILETYPES):
            lbl_files = []
            # loop around templates
            for template in templates:
                # push the object and template name into the glob
                lbl_file = LBL_FILENAMES[it].format(objname, template)
                # get all the lbl files for this object name
                lbl_file_path = os.path.join(lbl_path, 'lblrdb', lbl_file)
                # remove drift files from the lbl rdb files
                if os.path.exists(lbl_file_path):
                    lbl_files.append(lbl_file_path)
            # add list to the LBLRDB file dict for this object
            object_class.filetypes[filetype].files = lbl_files
            # add to object table
            object_class.filetypes[filetype].num = len(lbl_files)
        # ---------------------------------------------------------------------
        # LBL Stats (generated by Charles)
        # ---------------------------------------------------------------------
        # define lbl stat dir
        lbl_stat_dir = os.path.join(lbl_path, LBL_STAT_DIR)
        # loop around the stat files
        for lblfilekey in LBL_STAT_FILES:
            # get obj+template glob
            objtmp_glob = f'{objname}_*'
            # get all obj+template directories
            lblsdirs = glob.glob(os.path.join(lbl_stat_dir, objtmp_glob))
            # make the file_dict
            object_class.lbl_stat_files[lblfilekey] = dict()
            # loop around obj_templates
            for objtmpdir in lblsdirs:
                # get the obj+tmp name
                objtmp = os.path.basename(objtmpdir)
                # get the expected stats file name
                lblsfile = LBL_STAT_FILES[lblfilekey].format(objtmp)
                # get the expected stats file path
                lblspath = os.path.join(objtmpdir, lblsfile)
                # check that expected file exists
                if os.path.exists(lblspath):
                    # add a list to file dict for this object
                    object_class.lbl_stat_files[lblfilekey][objtmp] = lblspath
    # -------------------------------------------------------------------------
    # return the object table
    return object_classes


def lbl_plot(lbl_props: Dict[str, Any], plot_path: str,
             plot_title: str) -> Dict[str, Any]:
    # setup the figure
    fig, frame = plt.subplots(2, 1, figsize=(12, 6), sharex='all')
    # get parameters from props
    plot_date = lbl_props['plot_date']
    vrad = lbl_props['vrad']
    svrad = lbl_props['svrad']
    snr_h = lbl_props['snr_h']
    snr_h_label = lbl_props['SNR_H_LABEL']
    reset_mask = lbl_props['RESET_RV']
    # sort data by date
    sort = np.argsort(plot_date)
    plot_date = plot_date[sort]
    vrad = vrad[sort]
    svrad = svrad[sort]
    snr_h = snr_h[sort]
    reset_mask = reset_mask[sort]
    # set background color
    frame[0].set_facecolor(PLOT_BACKGROUND_COLOR)
    frame[1].set_facecolor(PLOT_BACKGROUND_COLOR)
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
                       label='Possibily bad (reset rv)')
    # over plot the bad points from above
    if len(bad_points) > 0:
        bad_points = np.array(bad_points)
        frame[1].plot_date(plot_date[bad_points], snr_h[bad_points], fmt='.',
                           alpha=0.5, color='red', ls='None', label='Outliers')

    # add properties
    frame[1].grid(which='both', color='lightgray', linestyle='--')
    frame[1].set(xlabel='Date')
    frame[1].set(ylabel=snr_h_label)
    # add legend
    frame[1].legend(loc=0)
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


def lbl_stats_table(lbl_props: Dict[str, Any], stat_path: str, title: str):
    # get parameters from props
    rjd = lbl_props['rjd']
    vrad = lbl_props['vrad']
    svrad = lbl_props['svrad']
    low = lbl_props['low']
    high = lbl_props['high']
    vel_domain = lbl_props['ylim']
    version_lbl = lbl_props['version']
    num_reset_rv = lbl_props['NUM_RESET_RV']
    # --------------------------------------------------------------------------
    # compute the stats
    # --------------------------------------------------------------------------
    # get the 25, 50 and 75 percentile of the velocity uncertainty
    p_sigma = np.nanpercentile(svrad, [25, 50, 75])
    # get the 25, 50 and 75 percentile of the velocity
    v_sigma = np.nanpercentile(abs(vrad - np.nanmedian(vrad)),
                               [25, 50, 75])
    # calculate the number of nights
    n_nights = len(np.unique(np.floor(rjd)))
    # calculate the systemetic velocity
    sys_vel = np.nanmedian(vrad)
    # --------------------------------------------------------------------------
    # construct the stats table
    # --------------------------------------------------------------------------
    # start with a stats dictionary
    stat_dict = dict(Description=[], Value=[])
    # add rv uncertainty
    stat_dict['Description'].append('RV Uncertainty lbl.rdb (25, 50, 75 percentile)')
    stat_dict['Value'].append('{:.2f}, {:.2f}, {:.2f} m/s'.format(*p_sigma))
    # add the absolute deviation
    stat_dict['Description'].append('RV Absolute Deviation lbl.rdb (25, 50, 75 '
                                    'percentile)')
    stat_dict['Value'].append('{:.2f}, {:.2f}, {:.2f} m/s'.format(*v_sigma))
    # add the number of measurements
    stat_dict['Description'].append('Number of lbl.rdb Measurements')
    stat_dict['Value'].append(len(vrad))
    # add the spurious low points
    stat_dict['Description'].append('Number of lbl.rdb Spurious Low Points')
    stat_dict['Value'].append(np.sum(low))
    # add the spurious high points
    stat_dict['Description'].append('Number of lbl.rdb Spurious High Points')
    stat_dict['Value'].append(np.sum(high))
    # add the number of nights
    stat_dict['Description'].append('Number of Nights')
    stat_dict['Value'].append(n_nights)
    # add the number of reset RV points
    stat_dict['Description'].append('Number of Reset RV Points')
    stat_dict['Value'].append(num_reset_rv)
    # add the systemic velocity
    stat_dict['Description'].append('Systemic Velocity')
    stat_dict['Value'].append('{:.2f} m/s'.format(sys_vel))
    # add the Velocity domain considered
    stat_dict['Description'].append('Velocity Domain considered valid')
    stat_dict['Value'].append('{:.2f} to {:.2f} m/s'.format(*vel_domain))
    # add the LBL version
    stat_dict['Description'].append('LBL Version')
    stat_dict['Value'].append(version_lbl)
    # --------------------------------------------------------------------------
    # change the columns names
    stat_dict2 = dict()
    stat_dict2[title] = stat_dict['Description']
    stat_dict2[' '] = stat_dict['Value']
    # --------------------------------------------------------------------------
    # convert to table
    stat_table = Table(stat_dict2)
    # write to file as csv file
    stat_table.write(stat_path, format='ascii.csv', overwrite=True)


# =============================================================================
# CCF page functions
# =============================================================================
def choose_ccf_files(ccf_props: Dict[str, Any]) -> Dict[str, Any]:
    """
    Choose CCF files based on the most numerious of a single mask
    and then the MAX_NUM_CCF selected uniformly in time
    """
    from apero.core.utils import drs_utils
    # get parameters from props
    masks = ccf_props['masks']
    files = np.array(ccf_props['files'])
    mjd = ccf_props['mjd']
    # storage of the ccf mask count
    mask_names, mask_counts = [], []
    # loop around masks
    for mask in masks:
        # count how many files of each mask
        mask_names = np.append(mask_names, mask)
        mask_counts = np.append(mask_counts, np.sum(masks == mask))
    # choose the mask with the most counts
    chosen_mask = mask_names[np.argmax(mask_counts)]
    # filter files and mjd by chosen mask
    mask_mask = masks == chosen_mask
    sfiles = files[mask_mask]
    smjd = mjd[mask_mask]
    # now choose files distributed equally in time
    time_mask = drs_utils.uniform_time_list(smjd, MAX_NUM_CCF)
    # filter files by the time mask
    sfiles = sfiles[time_mask]

    ccf_props['select_files'] = sfiles
    ccf_props['chosen_mask'] = chosen_mask
    # return ccf props
    return ccf_props


def fit_ccf(ccf_props: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fit the median CCF in order to plot the graph

    :param ccf_props:
    :return:
    """
    from apero.core.math.gauss import gauss_function
    # get parameters from props
    rv_vec = ccf_props['rv_vec']
    med_ccf = ccf_props['med_ccf']
    y1_1sig = ccf_props['y1_1sig']
    y2_1sig = ccf_props['y2_1sig']
    # set up guess
    amp0 = 1 - med_ccf[np.argmin(med_ccf)]
    pos0 = rv_vec[np.argmin(med_ccf)]
    sig0 = 4.0
    dc0 = 1.0
    guess = [-amp0, pos0, sig0, dc0]
    # try to fit the median ccf
    # noinspection PyBroadException
    try:
        # noinspection PyTupleAssignmentBalance
        coeffs, _ = curve_fit(gauss_function, rv_vec, med_ccf, p0=guess)
        fit = gauss_function(rv_vec, *coeffs)
        xlim = [coeffs[1] - coeffs[2] * 20, coeffs[1] + coeffs[2] * 20]
        ylim = [np.min(y1_1sig - fit), np.max(y2_1sig - fit)]
        has_fit = True
    except Exception as _:
        fit = np.full(len(rv_vec), np.nan)
        xlim = [np.min(rv_vec), np.max(rv_vec)]
        ylim = [np.min(med_ccf), np.max(med_ccf)]
        has_fit = False
    # adjust ylim
    ylim = [ylim[0] - 0.1 * (ylim[1] - ylim[0]),
            ylim[1] + 0.1 * (ylim[1] - ylim[1])]
    # add to ccf_props
    ccf_props['has_fit'] = has_fit
    ccf_props['fit'] = fit
    ccf_props['xlim'] = xlim
    ccf_props['ylim'] = ylim
    # return ccf props
    return ccf_props


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


def ccf_stats_table(ccf_props: Dict[str, Any], stat_path: str, title: str):
    from apero.core.math import estimate_sigma
    # get parameters from props
    vrad = ccf_props['dv']
    fwhm = ccf_props['fwhm']
    num_ccf = len(ccf_props['files'])
    num_ccf_qc = len(ccf_props['files_failed'])
    first_ccf = ccf_props['FIRST_CCF']
    last_ccf = ccf_props['LAST_CCF']
    last_ccf_proc = ccf_props['LAST_CCF_PROC']
    version_ccf = ccf_props['CCF_VERSION']
    chosen_mask = ccf_props['chosen_mask']
    # --------------------------------------------------------------------------
    # compute the stats
    # --------------------------------------------------------------------------
    # get the systemic velocity
    sys_vel = np.nanmedian(vrad)
    # get the error in systemic velocity
    err_sys_vel = estimate_sigma(vrad)
    # get the fwhm
    ccf_fwhm = np.nanmedian(fwhm)
    # get the error on fwhm
    err_ccf_fwhm = estimate_sigma(fwhm)
    # --------------------------------------------------------------------------
    # construct the stats table
    # --------------------------------------------------------------------------
    # start with a stats dictionary
    stat_dict = dict(Description=[], Value=[])
    # add mask used
    stat_dict['Description'].append('Mask used')
    stat_dict['Value'].append(chosen_mask)
    # add systemic velocity
    stat_dict['Description'].append('CCF systemic velocity')
    value = r'{:.2f} :math:`\pm` {:.2f} m/s'.format(sys_vel, err_sys_vel)
    stat_dict['Value'].append(value)
    # add fwhm
    stat_dict['Description'].append('CCF FWHM')
    value = r'{:.2f} :math:`\pm` {:.2f} m/s'.format(ccf_fwhm, err_ccf_fwhm)
    stat_dict['Value'].append(value)
    # add number of files
    stat_dict['Description'].append('Number of CCF files Total')
    stat_dict['Value'].append(num_ccf + num_ccf_qc)
    # add number of files
    stat_dict['Description'].append('Number of CCF passed QC')
    stat_dict['Value'].append(num_ccf)
    # add number of ccf files failed
    stat_dict['Description'].append('Number CCF files failed QC')
    stat_dict['Value'].append(num_ccf_qc)
    # add times
    stat_dict['Description'].append('First ccf file [Mid exposure]')
    stat_dict['Value'].append(f'{first_ccf}')
    stat_dict['Description'].append('Last ccf file [Mid exposure]')
    stat_dict['Value'].append(f'{last_ccf}')
    stat_dict['Description'].append('Last processed [ccf]')
    stat_dict['Value'].append(f'{last_ccf_proc}')
    stat_dict['Description'].append('Version [ccf]')
    stat_dict['Value'].append(f'{version_ccf}')
    # --------------------------------------------------------------------------
    # change the columns names
    stat_dict2 = dict()
    stat_dict2[title] = stat_dict['Description']
    stat_dict2[' '] = stat_dict['Value']
    # --------------------------------------------------------------------------
    # convert to table
    stat_table = Table(stat_dict2)
    # write to file as csv file
    stat_table.write(stat_path, format='ascii.csv', overwrite=True)


# =============================================================================
# Time series page functions
# =============================================================================
def time_series_stats_table(time_series_props: Dict[str, Any], stat_path: str):
    # get parameters from props
    columns = time_series_props['columns']
    # --------------------------------------------------------------------------
    # push columns into table
    stat_table = Table()
    for column in columns:
        stat_table[column] = time_series_props[column]
    # write to file as csv file
    stat_table.write(stat_path, format='ascii.csv', overwrite=True)


# =============================================================================
# Define worker functions
# =============================================================================
def _filter_pids(findex_table: pd.DataFrame, logdbm: Any) -> np.ndarray:
    """
    Filter file index database by pid to find those that passed

    :param findex_table: Table, the file index database
    :param logdbm: the drs_database.LogDatabase instance

    :return: numpy 1D array, a True/False mask the same length as findex_table
    """
    # assume everything failed
    passed = np.zeros(len(findex_table)).astype(bool)
    if len(findex_table) == 0:
        return passed
    # get the pids for these files
    pids = np.array(findex_table['KW_PID'])
    # get the pid
    pid_conds = []
    for pid in pids:
        pid_conds.append(f'PID="{pid}"')
    pid_condition = ' OR '.join(pid_conds)
    # need to crossmatch again recipe log database for QC
    ltable = logdbm.get_entries('PID,PASSED_ALL_QC', condition=pid_condition)
    # get the columsn from the log table
    all_pids = np.array(ltable['PID'])
    # get the passed all qc value
    passed_all_qc = np.array(ltable['PASSED_ALL_QC'])
    # if value is None assume it passed
    null_mask = ~(passed_all_qc == 1)
    null_mask &= ~(passed_all_qc == 0)
    passed_all_qc[null_mask] = 1
    # push into True and False
    all_pass = passed_all_qc.astype(bool)
    # need to loop around all files
    for row in range(len(findex_table)):
        # get the pid for this row
        pid = findex_table['KW_PID'].iloc[row]
        # find all rows that have this pid
        mask = all_pids == pid
        # deal with no entries
        # noinspection PyTypeChecker
        if len(mask) == 0:
            continue
        # if all rows pass qc passed = 1
        if np.sum(all_pass[mask]):
            passed[row] = True
    # return the passed mask
    return passed


def _match_file(reffile: str, files: List[str]):
    """
    Using a ref file split at the _pp level and try to locate the position
    of this file in the files list

    If ref file does not have _pp we assume it is a raw file and just remove
    the .fits and search based on this

    :param reffile: str,
    :param files:
    :return:
    """
    # force ref to be a basename
    refbasename = os.path.basename(reffile)
    # get the search string
    if '_pp' not in refbasename:
        searchstr = refbasename.split('.fits')[0]
    else:
        searchstr = refbasename.split('_pp')[0]

    # look for each string in list (correct entry should start with it)
    for it, filename in enumerate(files):
        # get basename of filename
        basename = os.path.basename(filename)
        # search for the string, if we find it we can stop here
        if basename.startswith(searchstr):
            return it
    # if we get to here we did not find the string - return None
    return None


def _header_value(keydict: Dict[str, str], header: fits.Header,
                  filename: str):
    # get properties of header key
    key = keydict['key']
    unit = keydict.get('unit', None)
    dtype = keydict.get('dtype', None)
    timefmt = keydict.get('timefmt', None)
    # -------------------------------------------------------------------------
    # get raw value from header
    rawvalue = header.get(key, None)
    # deal with no value
    if rawvalue is None:
        if "fallback" in keydict:
            rawvalue = keydict["fallback"]
            if rawvalue is None:
                if dtype == 'float':
                    rawvalue = np.nan
                elif dtype == 'str':
                    rawvalue = "N.A."
                else:
                    # Hard to define an unambiguous value for other types.
                    # Leaving as unsupported until the need arises.
                    raise TypeError('Null (None) fallback value unsupported'
                                    f' for dtype {dtype} (key {key})'
                                    f'\n\tFile: {filename}'
                                    )
        else:
            raise ValueError(f'HeaderKey: {key} not found in header'
                             ' and no fallback specified in config'
                             f'\n\tFile: {filename}')
    # -------------------------------------------------------------------------
    # deal with dtype
    if dtype is not None:
        try:
            if dtype == 'int':
                rawvalue = int(rawvalue)
            elif dtype == 'float':
                rawvalue = float(rawvalue)
            elif dtype == 'bool':
                rawvalue = bool(rawvalue)
        except Exception as _:
            raise ValueError(f'HeaderDtype: {dtype} not valid for '
                             f'{key}={rawvalue}\n\tFile: {filename}')
    # -------------------------------------------------------------------------
    # deal with time
    if timefmt is not None:
        try:
            return Time(rawvalue, format=timefmt)
        except Exception as _:
            raise ValueError(f'HeaderTime: {timefmt} not valid for '
                             f'{key}={rawvalue}\n\tFile: {filename}')
    # -------------------------------------------------------------------------
    # deal with units
    if unit is not None:
        try:
            rawvalue = uu.Quantity(rawvalue, unit)
        except ValueError:
            raise ValueError(f'HeaderUnit: {unit} not valid for '
                             f'{key}={rawvalue}\n\tFile: {filename}')
    # -------------------------------------------------------------------------
    # return the raw value
    return rawvalue


def _url_addp(key: str, value: Union[str, List[str], None],
              fmt: str = '&{0}={1}') -> str:
    # deal with value being None
    if value is None:
        return ''
    # deal with a str or a list
    if isinstance(value, str):
        values = [value]
    else:
        values = value
    # storage for output string
    outstr = ''
    # loop around all values
    for value in values:
        if ' ' in value:
            outstr += fmt.format(key, value.replace(' ', '+'))
        else:
            outstr += fmt.format(key, value)
    # return outstr
    return outstr


def create_header_file(files: List[str], headers: Dict[str, Any], filetype: str,
                       hdict: Dict[str, Any], filename: str):
    """
    Creates a header file (csv) from a dictionary of header keys

    :param files: list of str, the files to loop around
    :param headers: dict, a dictionary containing those headers to add for
                    each filetype
    :param filetype: str, a filetype (i.e. ext, pp, tcorr, ccf)
    :param hdict: dict, the header values
    :param filename: str, the filename to save the csv file to

    :return: None, writes file to disk
    """
    # check file kind in headers (if it isn't we don't create files)
    if filetype not in headers:
        return
    # storage for dict-->table
    tabledict = dict()
    # first column is the filenames
    tabledict['filename'] = [os.path.basename(filename) for filename in files]
    # loop around keys in header for this filetype and add to tabledict
    for keydict in headers[filetype]:
        tabledict[keydict] = hdict[keydict]
    # convert to table
    table = Table(tabledict)
    # write to file
    table.write(filename, format='ascii.csv', overwrite=True)


def create_request_link_table(props: Dict[str, Any], save_path: str,
                              rlinks: List[str], rlinkstxt: List[str]):
    # rlinks
    rlink_dict = dict()
    rlink_dict['Request'] = []
    # loop around rlinks
    for r_it, rlink in enumerate(rlinks):
        if rlink not in props:
            continue
        if props[rlink] is None:
            continue
        # get the rlink text
        rlinktxt = rlinkstxt[r_it]
        # construct the request link in markdown format
        rlinkstr = '`{0} <{1}>`_'.format(rlinktxt, props[rlink])
        # push into dictionary
        rlink_dict['Request'].append(rlinkstr)
    # --------------------------------------------------------------------------
    # convert to table
    rdict_table = Table(rlink_dict)
    # write to file as csv file
    rdict_table.write(save_path, format='ascii.csv', overwrite=True)


def create_file_list(files: List[str], path: str):
    """
    Writes a list of files to disk
    """
    # if file exists remove it
    if os.path.exists(path):
        # noinspection PyBroadException
        try:
            os.remove(path)
        except Exception as _:
            pass
    # sort files alphabetically
    files = np.sort(files)
    # open file
    with open(path, 'w') as filelist:
        # loop around files
        for filename in files:
            # write to file
            filelist.write(filename + '\n')


def download_table(files: List[str], descriptions: List[str],
                   item_path: str, dwn_rel_path: str, down_dir: str,
                   title: str, versions: Optional[List[str]] = None):
    """
    Generic download table saving to the item relative path

    :param files: the list of files to add to download table
    :param descriptions: the list of descriptions for each file
    :param dwn_rel_path: the path of the download relative to the page
    :param item_path: the absolute path to the item csv table file (to save to)
    :param down_dir: the path to the download directory
    :param title: the title for the download table
    :param versions: the versions of the files (optional)
    :return:
    """
    # --------------------------------------------------------------------------
    # storage for ref file
    ref_paths = dict()
    # storage for outpath
    out_paths = dict()
    # storage for inpath
    in_paths = dict()
    # storage for the descriptions
    descs = dict()
    # storage of the last modified times
    last_modified = dict()
    # storage for the version
    out_versions = dict()
    # loop around files and get the paths
    for it, filename in enumerate(files):
        # get the basename
        basename = os.path.basename(filename)
        # get the in path
        in_paths[basename] = filename
        # get the reference path (for the link)
        ref_paths[basename] = dwn_rel_path + basename
        # get the outpath
        out_paths[basename] = os.path.join(down_dir, basename)
        # get the descriptions
        descs[basename] = descriptions[it]
        # ---------------------------------------------------------------------
        # get the last modified time of the filename
        if os.path.exists(filename):
            last_mod = Time(os.path.getmtime(filename), format='unix').iso
            last_modified[basename] = last_mod
        else:
            last_modified[basename] = 'N/A'
        # ---------------------------------------------------------------------
        # deal with version
        if versions is not None:
            out_versions[basename] = versions[it]
        # if file is a fits file get the version from the header
        elif filename.endswith('.fits'):
            # get the header
            hdr = fits.getheader(filename)
            if 'VERSION' in hdr:
                out_versions[basename] = hdr['VERSION']
            else:
                out_versions[basename] = ''
        # otherwise we have no version info
        else:
            out_versions[basename] = ''

    # --------------------------------------------------------------------------
    # construct the stats table
    # --------------------------------------------------------------------------
    # start with a download dictionary
    down_dict = dict(Description=[], Value=[], Uploaded=[], Version=[])
    # flag for having versions
    has_version = False
    # loop around files
    for basename in in_paths:
        # make the sphinx reference
        down_ref = drs_markdown.make_download(basename, ref_paths[basename])
        # add the rdb file
        down_dict['Description'].append(descs[basename])
        down_dict['Value'].append(down_ref)
        down_dict['Uploaded'].append(last_modified[basename])
        down_dict['Version'].append(out_versions[basename])
        # check for version
        if out_versions[basename] != '':
            has_version = True
        # copy the file from in path to out path
        #   if file is already here then don't copy
        if in_paths[basename] != out_paths[basename]:
            shutil.copy(in_paths[basename], out_paths[basename])
    # --------------------------------------------------------------------------
    # change the columns names
    down_dict2 = dict()
    down_dict2[title] = down_dict['Description']
    down_dict2['File URL'] = down_dict['Value']
    down_dict2['Uploaded'] = down_dict['Uploaded']
    # add version only if one file has version (with the has_version flag)
    if has_version:
        down_dict2['Version'] = down_dict['Version']
    # --------------------------------------------------------------------------
    # convert to table
    down_table = Table(down_dict2)
    # write to file as csv file
    down_table.write(item_path, format='ascii.csv', overwrite=True)


def do_rsync(params: ParamDict, mode: str, path_in: str, path_out: str,
             required=True):
    # --------------------------------------------------------------------------
    # get the correct rsync command
    if mode == 'get':
        rsync_cmd = RSYNC_CMD_IN
    elif mode == 'send':
        rsync_cmd = RSYNC_CMD_OUT
    else:
        WLOG(params, 'error', 'Mode not recognized (must be "get" or "send")')
        return
    # --------------------------------------------------------------------------
    # get the ssh command
    ssh_dict = dict()
    ssh_dict['SSH'] = params['ARI_SSH_COPY']['options']
    ssh_dict['USER'] = params['ARI_SSH_COPY']['user']
    ssh_dict['HOST'] = params['ARI_SSH_COPY']['host']
    ssh_dict['INPATH'] = path_in
    ssh_dict['OUTPATH'] = path_out
    # --------------------------------------------------------------------------
    # try to do the rsync
    try:
        msg = 'Running rsync command: {0}'
        margs = [rsync_cmd.format(**ssh_dict)]
        WLOG(params, '', msg.format(*margs))
        os.system(rsync_cmd.format(**ssh_dict))
    except Exception as e:
        msg = 'Failed to rsync file from/to ari\n\t{0}:{1}'
        margs = [type(e), str(e)]
        if required:
            WLOG(params, 'error', msg.format(margs))


def find_finder_charts(path: str, objname: str) -> Tuple[List[str], List[str]]:
    """
    Find finder charts for this object
    :param path: str, the path to the finder charts directory
    :param objname: str, the object name to locate
    :return:
    """
    # expected directory name
    expected_dir = os.path.join(path, objname)
    # deal with no directory --> no finder files
    if not os.path.exists(expected_dir):
        return [], []
    # storage for list of files
    list_of_files = []
    list_of_descs = []
    # loop around filenames
    for filename in os.listdir(expected_dir):
        # only include APERO finder charts
        if not filename.startswith('APERO_finder_chart_'):
            continue
        # only include pdf files
        if not filename.endswith('.pdf'):
            continue
        # get the finder desc
        description = filename.split(objname)[-1]
        description = description.strip('_')
        description = description.replace('_', '-').replace('.pdf', '')
        # append to list
        list_of_files.append(os.path.join(expected_dir, filename))
        list_of_descs.append(description)
    # return the list of files
    return list_of_files, list_of_descs


def make_finder_download_table(entry, objname, item_save_path, item_rel_path,
                               down_save_path, down_rel_path):
    # get the download base name
    dwn_base_name = f'finder_download_{objname}.txt'
    # get the download table path
    item_path = os.path.join(item_save_path, dwn_base_name)
    # compute the download table
    download_table(entry['find_files'], entry['find_descs'],
                   item_path, down_rel_path,
                   down_save_path, title='Finder charts')
    return item_rel_path + dwn_base_name


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

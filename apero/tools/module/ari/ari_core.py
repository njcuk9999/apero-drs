#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-23 at 10:56

@author: cook
"""
import copy
import os
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from astropy.time import Time

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log

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
YAML_TO_PARAM['settings.username'] = 'ARI_USER'
YAML_TO_PARAM['settings.N_CORES'] = 'ARI_NCORES'
YAML_TO_PARAM['settings.SpecWave'] = 'ARI_WAVE_RANGES'
YAML_TO_PARAM['settings.ssh'] = 'ARI_SSH_COPY'
YAML_TO_PARAM['settings.reset'] = 'ARI_RESET'
YAML_TO_PARAM['settings.filter objects'] = 'ARI_FILTER_OBJECTS'
YAML_TO_PARAM['settings.objects'] = 'ARI_FILTER_OBJECTS_LIST'
YAML_TO_PARAM['headers'] = 'ARI_HEADER_PROPS'
# mapping of AriObject keys to yaml dump
OBJ_TO_YAML = dict()
OBJ_TO_YAML['objname'] = 'OBJNAME'
OBJ_TO_YAML['exists'] = 'EXISTS'
OBJ_TO_YAML['dprtypes'] = 'DPRTYPES'
OBJ_TO_YAML['last_processed'] = 'LAST_PROCESSED'
# Some keys need to be converted to put into the yaml
OBJ_TO_YAML_DTYPES  = dict()
OBJ_TO_YAML_DTYPES['last_processed'] = 'astropy.time.Time'


# -----------------------------------------------------------------------------
# Instrument variables
# -----------------------------------------------------------------------------
# define which instruments have polar
HAS_POLAR = dict(SPIROU=True, NIRPS_HE=False, NIRPS_HA=False)
# -----------------------------------------------------------------------------
# Object variables
# -----------------------------------------------------------------------------
# define the column which is the object name
OBJECT_COLUMN = 'OBJNAME'
# define the astrometric database column names to get
ASTROMETRIC_COLUMNS = ['OBJNAME', 'RA_DEG', 'DEC_DEG', 'TEFF', 'SP_TYPE']
ASTROMETRIC_DTYPES = [str, float, float, float, str]
# -----------------------------------------------------------------------------
# File variables
# -----------------------------------------------------------------------------
# define the lbl files
LBL_FILETYPES = ['lbl_rdb', 'lbl2_rdb', 'lbl_drift', 'lbl2_drift', 'lbl_fits']
LBL_FILENAMES = ['lbl_{0}_{1}.rdb', 'lbl2_{0}_{1}.rdb',
                 'lbl_{0}_{1}_drift.rdb', 'lbl2_{0}_{1}_drift.rdb',
                 'lbl_{0}_{1}.fits']
LBL_FILE_DESC = ['RDB file', 'RDB2 file', 'Drift file', 'Drift2 file',
                 'LBL RDB fits file']
LBL_DOWNLOAD = [True, True, True, True, False]


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
        yaml_dict['files'] = list(self.files)
        # numpy array of booleans (for the mask) --> list
        if self.qc_mask is not None:
            qc_mask_list = []
            for qc in self.qc_mask:
                qc_mask_list.append(bool(qc))
            yaml_dict['qc_mask'] = qc_mask_list
        else:
            yaml_dict['qc_mask'] = None
        # numpy array of observation directories --> list
        yaml_dict['obsdirs'] = list(self.obsdirs)
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
        # the file type (DRSOUTID)
        self.kw_output = yaml_dict['kw_output']
        # the fiber type
        self.fiber = yaml_dict['fiber']
        # whether to count the files
        self.count = yaml_dict['count']
        # whether there is a chain (i.e. this file was created from another)
        self.chain = yaml_dict['chain']
        # the sql condition used
        self.cond = yaml_dict['cond']
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
        cond = f'KW_OBJNAME="{objname}"'
        if self.block_kind is not None:
            cond += f' AND BLOCK_KIND="{self.block_kind}"'
        if self.kw_output is not None:
            cond += f' AND KW_OUTPUT="{self.kw_output}"'
        if self.fiber is not None:
            cond += f' AND KW_FIBER="{self.fiber}"'
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


class AriObject:
    def __init__(self, objname: str, filetypes: Dict[str, FileType]):
        # get the object name
        self.objname = objname
        self.ra: Optional[float] = None
        self.dec: Optional[float] = None
        self.teff: Optional[float] = None
        self.sptype: Optional[str] = None

        # ---------------------------------------------------------------------
        # Add files as copy of filetype class
        # ---------------------------------------------------------------------
        self.filetypes: Dict[str, FileType] = dict()
        for key in filetypes:
            self.filetypes[key] = filetypes[key].copy_new()
        # flag for whether we have polar files
        self.has_polar: bool = False
        # set up yaml file
        self.yaml_path: str = os.path.join('ari', 'object_yamls')
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

    def add_astrometrics(self, table):
        self.ra = table['RA_DEG']
        self.dec = table['DEC_DEG']
        self.teff = table['TEFF']
        self.sptype = table['SP_TYPE']

    def add_files_stats(self, indexdbm, logdbm):
        # loop around raw files
        for key in self.filetypes:
            # get iterations filetype
            filetype = self.filetypes[key]
            # count files and get lists of files
            filetype.count_files(self.objname, indexdbm, logdbm, self.filetypes)
            # deal with update
            self.update = bool(filetype.update)
            # if we are not updating to not continue
            if not self.update:
                return
            # if there are no entries we have no raw files for this object
            if key == 'raw':
                if filetype.num == 0:
                    return
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

    def save_to_disk(self, params: ParamDict):
        # make full yaml path
        yaml_root = params['DRS_DATA_OTHER']
        yaml_path = os.path.join(yaml_root, self.yaml_path)
        # check if yaml directory exists
        if not os.path.exists(yaml_path):
            os.makedirs(yaml_path)
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
        yaml_root = params['DRS_DATA_OTHER']
        yaml_path = os.path.join(yaml_root, self.yaml_path)
        # check if yaml directory exists
        if not os.path.exists(yaml_path):
            os.makedirs(yaml_path)
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


class AriRecipe:
    pass






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

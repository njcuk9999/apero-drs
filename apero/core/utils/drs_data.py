#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs data


Used to load data files from the assets directory only

Created on 2019-07-02 at 09:24

@author: cook
"""
from astropy.table import Table
import glob
import numpy as np
import os
from pathlib import Path
from typing import List, Tuple, Type, Union

from apero.base import base
from apero.base import drs_misc
from apero.base import drs_exceptions
from apero.base import drs_text
from apero.core import constants
from apero import lang
from apero.core.core import drs_log
from apero.io import drs_path
from apero.io import drs_fits
from apero.io import drs_table

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_data.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get ParamDict
ParamDict = constants.ParamDict
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
LoadException = drs_exceptions.LoadException
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# get display func
display_func = drs_misc.display_func


# =============================================================================
# Define functions
# =============================================================================
def load_linelist(params: ParamDict,
                  assetsdir: Union[str, None] = None,
                  directory: Union[str, Path, None] = None,
                  filename: Union[str, None] = None,
                  fmt: Union[str, None] = None,
                  cols: Union[str, None] = None,
                  start: Union[int, None] = None,
                  wavecol: Union[str, None] = None,
                  ampcol: Union[str, None] = None,
                  return_filename: bool = False,
                  func: Union[str, None] = None,
                  ) -> Union[str, Tuple[np.ndarray, np.ndarray]]:
    """
    Load wave line list file

    :param params: ParamDict, parameter dictionary of constants
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the wave data are stored (within assets
                      directory) -- overrides params['DRS_WAVE_DATA']
    :param filename: str, Define the line list file (located in the
                       DRS_WAVE_DATA directory) -- overrides
                       params['WAVE_LINELIST_FILE']
    :param fmt: str, Define the line list file format (must be astropy.table
                  format) -- overrides params['WAVE_LINELIST_FMT']
    :param cols: str, Define the line list file column names (must be
                   separated by commas and must be equal to the number of
                   columns in file) -- overrides params['WAVE_LINELIST_COLS']
    :param start: int, Define the line list file row the data starts
                    -- overrides params['WAVE_LINELIST_START']
    :param wavecol: str, Define the line list file wavelength column name
                      -- overrides params['WAVE_LINELIST_WAVECOL']
    :param ampcol: str,  Define the line list file amplitude column name
                     -- overrides params['WAVE_LINELIST_AMPCOL']
    :param return_filename: bool, whether to return filename
    :param func: str, the function where load_linelist was called

    :return:
    """
    # set function name
    if func is None:
        func_name = display_func(params, 'load_linelist', __NAME__)
    else:
        func_name = func
    # get parameters from params (or override)
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'DRS_WAVE_DATA', func=func_name,
                       override=directory)
    filename = pcheck(params, 'WAVE_LINELIST_FILE', func=func_name,
                      override=filename)
    tablefmt = pcheck(params, 'WAVE_LINELIST_FMT', func=func_name,
                      override=fmt)
    tablecols = pcheck(params, 'WAVE_LINELIST_COLS', func=func_name,
                       override=cols)
    tablestart = pcheck(params, 'WAVE_LINELIST_START', func=func_name,
                        override=start)
    wavecol = pcheck(params, 'WAVE_LINELIST_WAVECOL', func=func_name,
                     override=wavecol)
    ampcol = pcheck(params, 'WAVE_LINELIST_AMPCOL', func=func_name,
                    override=ampcol)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # split table columns
    tablecols = list(map(lambda x: x.strip(), tablecols.split(',')))

    # return image
    try:
        table = load_table_file(params, absfilename, fmt=tablefmt,
                                colnames=tablecols, datastart=int(tablestart),
                                func_name=func_name)
        WLOG(params, '', TextEntry('40-017-00001', args=absfilename))
        # push columns into numpy arrays and force to floats
        ll = np.array(table[wavecol], dtype=float)
        amp = np.array(table[ampcol], dtype=float)
        # return wavelength and amplitude columns
        return ll, amp
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-017-00002', args=eargs))


def load_cavity_files(params: ParamDict,
                      required: bool = True,
                      assetsdir: Union[str, None] = None,
                      directory: Union[str, None] = None,
                      file1m: Union[str, None] = None,
                      filell: Union[str, None] = None
                      ) -> Union[Tuple[None, None],
                                 Tuple[np.ndarray, np.ndarray]]:
    """
    Load the 1/m file and ll wavelength cavity files

    :param params: ParamDict, parameter dictionary of constants
    :param required: bool, if True raises an exception when files don't exist
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the wave data are stored (within assets
                      directory) -- overrides params['DRS_WAVE_DATA']
    :param file1m: str, Define the coefficients of the fit of 1/m vs d
                   -- overrides params['CAVITY_1M_FILE']
    :param filell: str, Define the coefficients of the fit of wavelength vs d
                   -- overrides params['CAVITY_LL_FILE']
    :return:
    """
    # set function name
    func_name = display_func(params, 'load_cavity_files', __NAME__)
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'DRS_CALIB_DATA', func=func_name,
                       override=directory)
    filename_1m = pcheck(params, 'CAVITY_1M_FILE', func=func_name,
                         override=file1m)
    filename_ll = pcheck(params, 'CAVITY_LL_FILE', func=func_name,
                         override=filell)
    # construct absolute filenames
    absfilename_1m = os.path.join(assetdir, relfolder, filename_1m)
    absfilename_ll = os.path.join(assetdir, relfolder, filename_ll)
    # check for absolute path existence
    exists1 = os.path.exists(absfilename_1m)
    exists2 = os.path.exists(absfilename_ll)
    # deal with not required
    if not required:
        if not exists1 or not exists2:
            return None, None
    # load text files
    fit_1m = load_text_file(params, absfilename_1m, func_name, dtype=float)
    fit_ll = load_text_file(params, absfilename_ll, func_name, dtype=float)
    # return arrays from text files
    return np.array(fit_1m), np.array(fit_ll)


def save_cavity_files(params: ParamDict, fit_1m_d: np.ndarray,
                      fit_ll_d: np.ndarray,
                      assetsdir: Union[str, None] = None,
                      directory: Union[str, None] = None,
                      file1m: Union[str, None] = None,
                      filell: Union[str, None] = None):
    """
    Save the 1/m file and ll wavelength cavity files

    :param params: ParamDict, parameter dictionary of constants
    :param fit_1m_d: numpy array - the 1/m cavity array
    :param fit_ll_d: numpy array - the ll cavity array
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the wave data are stored (within assets
                      directory) -- overrides params['DRS_WAVE_DATA']
    :param file1m: str, Define the coefficients of the fit of 1/m vs d
                   -- overrides params['CAVITY_1M_FILE']
    :param filell: str, Define the coefficients of the fit of wavelength vs d
                   -- overrides params['CAVITY_LL_FILE']
    :return:
    """
    # set function name
    func_name = display_func(params, 'save_cavity_files', __NAME__)
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'DRS_CALIB_DATA', func=func_name,
                       override=directory)
    filename_1m = pcheck(params, 'CAVITY_1M_FILE', func=func_name,
                         override=file1m)
    filename_ll = pcheck(params, 'CAVITY_LL_FILE', func=func_name,
                         override=filell)
    absfilename_1m = os.path.join(assetdir, relfolder, filename_1m)
    absfilename_ll = os.path.join(assetdir, relfolder, filename_ll)
    # save the 1m file
    save_text_file(params, absfilename_1m, fit_1m_d, func_name)
    # save the ll file
    save_text_file(params, absfilename_ll, fit_ll_d, func_name)


def load_full_flat_badpix(params: ParamDict,
                          assetsdir: Union[str, None] = None,
                          directory: Union[str, None] = None,
                          filename: Union[str, None] = None,
                          func: Union[str, None] = None,
                          return_filename: bool = False
                          ) -> Union[str, np.ndarray]:
    """
    Load the full flat bad pixel image

    :param params: ParamDict, the parameter dictionary of constants
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the badpix file is stored (within assets
                      directory) -- overrides params['DRS_BADPIX_DATA']
    :param filename: str, the badpix file name
                     -- overrides params['BADPIX_FULL_FLAT']
    :param func: str, the function name calling this function
    :param return_filename: bool, if True returns filename else returns image

    :return: either the filename (return_filename=True) or np.ndarray the
             full flat badpix image
    """
    # set function name
    if func is None:
        func_name = display_func(params, 'load_full_flat_badpix', __NAME__)
    else:
        func_name = func
    # set parameters from params (or override)
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'DRS_BADPIX_DATA', func=func_name,
                       override=directory)
    filename = pcheck(params, 'BADPIX_FULL_FLAT', func=func_name,
                      override=filename)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # return image
    try:
        image = load_fits_file(params, absfilename, func_name)
        WLOG(params, '', TextEntry('40-012-00003', args=absfilename))
        return image
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder), func_name]
        WLOG(params, 'error', TextEntry('00-012-00001', args=eargs))


def load_hotpix(params: ParamDict,
                assetsdir: Union[str, None] = None,
                directory: Union[str, None] = None,
                filename: Union[str, None] = None,
                func: Union[str, None] = None,
                fmt: str = 'csv', datastart: int = 1,
                return_filename: bool = False) -> Union[str, Table]:
    """
    Load the preprocessing hotpix image

    :param params: ParamDict, the parameter dictionary of constants
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the hotpix file is stored (within assets
                      directory) -- overrides params['DATA_ENGINEERING']
    :param filename: str, the hotpix file name
                     -- overrides params['PP_HOTPIX_FILE']
    :param func: str, the function name calling this function
    :param fmt: str, the data format (astropy.table format)
    :param datastart: int, the row at which to start reading the file
    :param return_filename: bool, if True returns filename else returns image

    :return: either the filename (return_filename=True) or np.ndarray the
             hot pix image
    """
    # set function name
    if func is None:
        func_name = display_func(params, 'load_full_flat_badpix', __NAME__)
    else:
        func_name = func
    # set parameters from params (or override)
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'DATA_ENGINEERING', func=func_name,
                       override=directory)
    filename = pcheck(params, 'PP_HOTPIX_FILE', func=func_name,
                      override=filename)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # return table
    try:
        table = load_table_file(params, absfilename, fmt=fmt,
                                datastart=datastart, func_name=func_name)
        WLOG(params, '', TextEntry('40-010-00011', args=absfilename))
        return table
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-010-00002', args=eargs))


def load_tapas(params: ParamDict,
               assetsdir: Union[str, None] = None,
               directory: Union[str, None] = None,
               filename: Union[str, None] = None,
               func: Union[str, None] = None,
               fmt: Union[str, None] = None,
               return_filename: bool = False) -> Union[str, Tuple[Table, str]]:
    """
    Load the tapas file

    :param params: ParamDict, the parameter dictionary of constants
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the tapas file is stored (within assets
                      directory) -- overrides params['TELLU_LIST_DIRECOTRY']
    :param filename: str, the tapas file name
                     -- overrides params['TAPAS_FILE']
    :param func: str, the function name calling this function
    :param fmt: str, the data format (astropy.table format)
    :param return_filename: bool, if True returns filename else returns image

    :return: either the filename (return_filename=True) or np.ndarray the
             tapas table and the filename
    """
    # set function name
    if func is None:
        func_name = display_func(params, 'load_tapas', __NAME__)
    else:
        func_name = func
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', func=func_name,
                       override=directory)
    filename = pcheck(params, 'TAPAS_FILE', func=func_name,
                      override=filename)
    fmt = pcheck(params, 'TAPAS_FILE_FMT', func=func_name, override=fmt)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # return image
    try:
        table = load_table_file(params, absfilename, fmt=fmt,
                                func_name=func_name)
        WLOG(params, '', TextEntry('40-999-00002', args=absfilename))
        return table, absfilename
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-010-00004', args=eargs))


def load_object_list(params: ParamDict,
                     assetsdir: Union[str, None] = None,
                     directory: Union[str, None] = None,
                     filename: Union[str, None] = None,
                     func: Union[str, None] = None,
                     fmt: Union[str, None] = None,
                     return_filename: bool = False) -> Union[str, Table]:
    """
    Load the object list file

    :param params: ParamDict, the parameter dictionary of constants
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the object list file is stored (within assets
                      directory) -- overrides params['DATABASE_DIR']
    :param filename: str, the object list file name
                     -- overrides params['OBJ_LIST_FILE']
    :param func: str, the function name calling this function
    :param fmt: str, the data format (astropy.table format)
    :param return_filename: bool, if True returns filename else returns image

    :return: either the filename (return_filename=True) or np.ndarray the
             object list table
    """
    # set function name
    if func is None:
        func_name = display_func(params, 'load_object_list', __NAME__)
    else:
        func_name = func
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'DATABASE_DIR', func=func_name,
                       override=directory)
    filename = pcheck(params, 'OBJ_LIST_FILE', func=func_name,
                      override=filename)
    fmt = pcheck(params, 'OBJ_LIST_FILE_FMT', func=func_name, override=fmt)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # return image
    try:
        table = load_table_file(params, absfilename, fmt=fmt,
                                func_name=func_name)
        WLOG(params, '', TextEntry('40-999-00003', args=absfilename))
        return table
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-010-00005', args=eargs))


def load_ccf_mask(params: ParamDict,
                  assetsdir: Union[str, None] = None,
                  directory: Union[str, None] = None,
                  filename: Union[str, None] = None,
                  func: Union[str, None] = None,
                  fmt: Union[str, None] = None,
                  return_filename: bool = False
                  ) -> Union[str, Tuple[Table, str]]:
    """
    Load the ccf mask file

    :param params: ParamDict, the parameter dictionary of constants
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the ccf mask file is stored (within assets
                      directory) -- overrides params['CCF_MASK_PATH']
    :param filename: str, the ccf mask  file name
                     -- overrides params['CCF_MASK']
    :param func: str, the function name calling this function
    :param fmt: str, the data format (astropy.table format)
    :param return_filename: bool, if True returns filename else returns image

    :return: either the filename (return_filename=True) or np.ndarray the
             ccf mask table and the filename
    """
    # set function name
    if func is None:
        func_name = display_func(params, 'load_ccf_mask', __NAME__)
    else:
        func_name = func
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'CCF_MASK_PATH', func=func_name,
                       override=directory)
    filename = pcheck(params, 'CCF_MASK', func=func_name,
                      override=filename)
    fmt = pcheck(params, 'CCF_MASK_FMT', func=func_name, override=fmt)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # return image
    try:
        table = load_table_file(params, absfilename, fmt=fmt,
                                colnames=['ll_mask_s', 'll_mask_e', 'w_mask'],
                                func_name=func_name)
        WLOG(params, '', TextEntry('40-020-00002', args=absfilename))
        return table, absfilename
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-020-00002', args=eargs))


def load_sp_mask_lsd(params: ParamDict, temperature: float,
                     assetsdir: Union[str, None] = None,
                     directory: Union[str, None] = None,
                     filename: Union[str, None] = None,
                     func: Union[str, None] = None,
                     filekey: Union[str, None] = None,
                     return_filename: bool = False
                     ) -> Union[str, Tuple[Table, str]]:
    """
    Load the spectrum mask LSD file

    :param params: ParamDict, the parameter dictionary of constants
    :param temperature: float, the temperature of object to be used with the
                        mask - the mask with the closest temperature to this
                        will be used
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the sp mask lsd file is stored (within assets
                      directory) -- overrides params['POLAR_LSD_PATH']
    :param filename: str, the sp mask lsd mask  file name
    :param func: str, the function name calling this function
    :param filekey: str, Define the file regular expression key to lsd mask
                    files wildcard key used in form filekey={prefix}*{suffix}
                    -- overrides params['POLAR_LSD_FILE_KEY']
    :param return_filename: bool, if True returns filename else returns image

    :return: either the filename (return_filename=True) or np.ndarray the
             sp mask lsd table and the filename
    """
    # set function name
    if func is None:
        func_name = display_func(params, 'load_sp_mask_lsd', __NAME__)
    else:
        func_name = func
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'POLAR_LSD_PATH', func=func_name,
                       override=directory)
    filekey = pcheck(params, 'POLAR_LSD_FILE_KEY', func=func_name,
                     override=filekey)
    # ------------------------------------------------------------------
    # get filename if None
    if filename is None:
        # get path to directory
        fulldir = os.path.join(assetdir, relfolder)
        # get all files
        allfiles = np.sort(glob.glob('{0}/{1}'.format(fulldir, filekey)))
        # loop around files and get their temperatures
        file_temperatures, basenames = [], []
        for filename in allfiles:
            # get file basename
            basename = os.path.basename(filename)
            # find prefix and suffix to the temperature key
            prefix, suffix = filekey.split('*')
            # get the temperature
            file_temperature = basename.split(prefix)[-1].split(suffix)[0]
            # try to convert to float
            try:
                file_temperatures.append(float(file_temperature))
                basenames.append(basename)
            except Exception as e:
                # log error
                eargs = [filename, type(e), e]
                WLOG(params, 'error', TextEntry('09-021-00009', args=eargs))
        # ------------------------------------------------------------------
        # now we have the temperatures find the closest to the input
        #     temperature
        # ------------------------------------------------------------------
        # find the temperature difference
        diff = temperature - np.array(file_temperatures)
        # find the position in our list of files closest in temperature
        pos = int(np.argmin(abs(diff)))
        # get filename from this
        filename = basenames[pos]
    # ----------------------------------------------------------------------
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # ----------------------------------------------------------------------
    # define table column names
    colnames = ['wavec', 'znum', 'depth', 'excpotf', 'lande', 'flagf']
    # ----------------------------------------------------------------------
    # return image
    try:
        # file currently must be an ascii file and must start on line 1
        table = load_table_file(params, absfilename, fmt='ascii', datastart=1,
                                func_name=func_name, colnames=colnames)
        WLOG(params, '', TextEntry('40-020-00002', args=absfilename))
        return table, absfilename

    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-020-00002', args=eargs))


def load_order_mask(params: ParamDict,
                    assetsdir: Union[str, None] = None,
                    directory: Union[str, None] = None,
                    filename: Union[str, None] = None,
                    func: Union[str, None] = None,
                    return_filename: bool = False
                    ) -> Union[str, Tuple[Table, str]]:
    """
    Load the order mask file for polarisation

    :param params: ParamDict, the parameter dictionary of constants
    :param assetsdir: str, Define the assets directory -- overrides
                      params['DRS_DATA_ASSETS']
    :param directory: str, where the ccf mask file is stored (within assets
                      directory) -- overrides params['POLAR_LSD_PATH']
    :param filename: str, the ccf mask  file name
                     -- overrides params['POLAR_LSD_ORDER_MASK']
    :param func: str, the function name calling this function
    :param return_filename: bool, if True returns filename else returns image

    :return: either the filename (return_filename=True) or np.ndarray the
             polar mask table and the filename
    """
    # set function name
    if func is None:
        func_name = display_func(params, 'load_order_mask', __NAME__)
    else:
        func_name = func
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', func=func_name,
                      override=assetsdir)
    relfolder = pcheck(params, 'POLAR_LSD_PATH', func=func_name,
                       override=directory)
    filename = pcheck(params, 'POLAR_LSD_ORDER_MASK', func=func_name,
                      override=filename)
    # ----------------------------------------------------------------------
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # ----------------------------------------------------------------------
    # return image
    try:
        # file currently must be an ascii file and must start on line 1
        table = load_table_file(params, absfilename, fmt='ascii',
                                datastart=1, func_name=func_name,
                                colnames=['order', 'lower', 'upper'])
        WLOG(params, '', TextEntry('40-020-00002', args=absfilename))
        return table, absfilename
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-020-00002', args=eargs))


# =============================================================================
# Worker functions
# =============================================================================
def load_fits_file(params: ParamDict, filename: str,
                   func_name: Union[str, None] = None) -> np.ndarray:
    """
    Load a fits file (using drs_fits.readfits)  and raise an error if file
    does not exist

    :param params: ParamDict, the parameter dictionary of constants
    :param filename: str, the filename to load
    :param func_name: str, the function that called load_fits_file

    :returns: the fits file image (assumes fits file is ImageBin)
    """
    # set function name
    if func_name is None:
        func_name = display_func(params, 'load_fits_file', __NAME__)
    # check that filepath exists and log an error if it was not found
    if not os.path.exists(filename):
        # load text dict
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # generate error
        eargs = [filename, func_name]
        raise LoadException(textdict['01-001-00022'].format(*eargs))
    # read image
    image = drs_fits.readfits(params, filename)
    # return image
    return image


def load_table_file(params: ParamDict, filename: str,
                    fmt: str = 'fits', datastart: int = 0,
                    colnames: Union[List[str], None] = None,
                    func_name: Union[str, None] = None) -> Table:
    """
    Load an astropy.table file

    :param params: ParamDict, parameter dictionary of constants
    :param filename: str, filename of the astropy table
    :param fmt: str, the file format (astropy Table format) defaults to 'fits'
    :param datastart: int, the row to start reading data from (defaults to 0)
    :param colnames: list of strings, the column names (optional None returns
                     table with col0, col1, col2, col3
    :param func_name: string or None - the function name load_table_file was
                      called from

    :return: an astropy Table instance of the loaded data
    """
    # set function name
    if func_name is None:
        func_name = display_func(params, 'load_table_file', __NAME__)
    # check that filepath exists and log an error if it was not found
    if not os.path.exists(filename):
        # load text dict
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # raise exception
        eargs = [filename, func_name]
        raise LoadException(textdict['01-001-00022'].format(*eargs))
    # read table
    table = drs_table.read_table(params, filename, fmt=fmt,
                                 colnames=colnames, data_start=datastart)
    # return image
    return table


def load_text_file(params: ParamDict, filename: str,
                   func_name: Union[str, None] = None,
                   dtype: Type = float) -> np.ndarray:
    """
    Load a text file from filename

    :param params: ParamDict, parameter dictionary of constants
    :param filename: str, filename of the text file to load
    :param func_name: string or None - the function name load_table_file was
                      called from
    :param dtype: type - the data type to convert the data to (defaults to
                  float)

    :return: numpy array of the text file
    """
    # set function name
    if func_name is None:
        func_name = display_func(params, 'load_text_file', __NAME__)
    # check that filepath exists and log an error if it was not found
    if not os.path.exists(filename):
        # load text dict
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        eargs = [filename, func_name]
        raise LoadException(textdict['01-001-00022'].format(*eargs))
    # load text as list
    try:
        textlist = drs_text.load_text_file(filename, '#', ' ')
    except DrsCodedException as e:
        elevel = e.get('level', 'error')
        eargs = e.get('targs', None)
        WLOG(params, elevel, TextEntry(e.codeid, args=eargs))
        textlist = None
    # deal with change list to numpy array
    textlist = np.array(textlist).astype(dtype)
    # return image
    return textlist


def save_text_file(params: ParamDict, filename: str, array: np.ndarray,
                   func_name: Union[None, str] = None):
    """
    Saves a numpy array to a text file

    :param params: ParamDict, parameter dictionary of constants
    :param filename: str, filename of the text file to load
    :param array: np.ndarray the array to save to text file
    :param func_name: str the function name where save_text_file was called
    :return:
    """
    # set function name
    if func_name is None:
        func_name = display_func(params, 'save_text_file', __NAME__)
    # save text file
    try:
        drs_text.save_text_file(filename, array, func_name)
    except DrsCodedException as e:
        elevel = e.get('level', 'error')
        eargs = e.get('targs', None)
        WLOG(params, elevel, TextEntry(e.codeid, args=eargs))


def construct_path(params: ParamDict, filename: Union[str, None] = None,
                   directory: Union[str, None] = None,
                   package: Union[str, None] = None,
                   func_name: Union[str, None] = None) -> str:
    """
    Construct path to file (given a filename and a directory)

    :param params: ParamDict, parameter dictionary of constants
    :param filename: str or None, the filename
    :param directory: str or None, the directory path
    :param package: str or None, the drs package name
    :param func_name: str or None the function construct_path was called from

    :return: str, the absolute file name
    """
    # set function name
    if func_name is None:
        func_name = display_func(params, 'construct_path', __NAME__)
    # deal with no filename
    if filename is None:
        filename = ''
    # deal with no directory
    if directory is None:
        directory = ''
    # get properties from params/jwargs
    package = pcheck(params, 'DRS_PACKAGE', func=func_name, override=package)
    # construct filepath
    datadir = drs_path.get_relative_folder(params, package, directory)
    absfilename = os.path.join(datadir, filename)
    # return absolute path
    return absfilename


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
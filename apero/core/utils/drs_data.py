#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs data


Used to load data files from the assets directory only

Created on 2019-07-02 at 09:24

@author: cook
"""
import numpy as np
import os
import glob

from apero.base import base
from apero.base import drs_exceptions
from apero.base import drs_text
from apero import core
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
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define classes
# =============================================================================
class LoadException(Exception):
    """Raised when config file is incorrect"""
    pass


# =============================================================================
# Define functions
# =============================================================================
def load_linelist(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_badpix()')
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'DRS_WAVE_DATA', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'WAVE_LINELIST_FILE', 'filename', kwargs,
                      func_name)
    tablefmt = pcheck(params, 'WAVE_LINELIST_FMT', 'fmt', kwargs, func_name)
    tablecols = pcheck(params, 'WAVE_LINELIST_COLS', 'cols', kwargs, func_name)
    tablestart = pcheck(params, 'WAVE_LINELIST_START', 'start', kwargs,
                        func_name)

    wavecol = pcheck(params, 'WAVE_LINELIST_WAVECOL', 'wavecol', kwargs,
                     func_name)
    ampcol = pcheck(params, 'WAVE_LINELIST_AMPCOL', 'ampcol', kwargs,
                    func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # split table columns
    tablecols = list(map(lambda x: x.strip(), tablecols.split(',')))
    # add back to kwargs
    kwargs['fmt'] = tablefmt
    kwargs['colnames'] = tablecols
    kwargs['datastart'] = int(tablestart)

    # return image
    try:
        table = load_table_file(params, absfilename, kwargs, func_name)
        WLOG(params, '', TextEntry('40-017-00001', args=absfilename))
        # push columns into numpy arrays and force to floats
        ll = np.array(table[wavecol], dtype=float)
        amp = np.array(table[ampcol], dtype=float)
        # return wavelength and amplitude columns
        return ll, amp
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-017-00002', args=eargs))


def load_cavity_files(params, required=True, **kwargs):

    func_name = __NAME__ + '.load_cavity_files()'
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'DRS_CALIB_DATA', 'directory', kwargs,
                       func_name)

    filename_1m = pcheck(params, 'CAVITY_1M_FILE', 'filename', kwargs,
                         func_name)
    filename_ll = pcheck(params, 'CAVITY_LL_FILE', 'filename', kwargs,
                         func_name)
    # construct absolute filenames
    absfilename_1m = os.path.join(assetdir, relfolder, filename_1m)
    absfilename_ll = os.path.join(assetdir, relfolder, filename_ll)
    # check for absolute path existence
    exists1 = os.path.exists(absfilename_1m)
    exists2 = os.path.exists(absfilename_ll)

    if not required:
        if not exists1 or not exists2:
            return None, None

    # load text files
    fit_1m = load_text_file(params, absfilename_1m, func_name, dtype=float)
    fit_ll = load_text_file(params, absfilename_ll, func_name, dtype=float)
    # return arrays from text files
    return np.array(fit_1m), np.array(fit_ll)


def save_cavity_files(params, fit_1m_d, fit_ll_d, **kwargs):
    func_name = __NAME__ + '.save_cavity_files()'
    # TODO: Ask about when and where we save this file
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'DRS_CALIB_DATA', 'directory', kwargs,
                       func_name)
    filename_1m = pcheck(params, 'CAVITY_1M_FILE', 'filename', kwargs,
                         func_name)
    filename_ll = pcheck(params, 'CAVITY_LL_FILE', 'filename', kwargs,
                         func_name)
    absfilename_1m = os.path.join(assetdir, relfolder, filename_1m)
    absfilename_ll = os.path.join(assetdir, relfolder, filename_ll)
    # save the 1m file
    save_text_file(params, absfilename_1m, fit_1m_d, func_name)
    # save the ll file
    save_text_file(params, absfilename_ll, fit_ll_d, func_name)


def load_full_flat_badpix(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_badpix()')
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'DRS_BADPIX_DATA', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'BADPIX_FULL_FLAT', 'filename', kwargs,
                      func_name)
    return_filename = kwargs.get('return_filename', False)
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


def load_hotpix(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_pp()')
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'DATA_ENGINEERING', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'PP_HOTPIX_FILE', 'filename', kwargs,
                      func_name)
    return_filename = kwargs.get('return_filename', False)
    # add table fmt
    kwargs['fmt'] = kwargs.get('fmt', 'csv')
    kwargs['datastart'] = 1
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # return table
    try:
        table = load_table_file(params, absfilename, kwargs, func_name)
        WLOG(params, '', TextEntry('40-010-00011', args=absfilename))
        return table
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-010-00002', args=eargs))


def load_tapas(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_pp()')
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TAPAS_FILE', 'filename', kwargs, func_name)

    tablefmt = pcheck(params, 'TAPAS_FILE_FMT', 'fmt', kwargs, func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # add back to kwargs
    kwargs['fmt'] = tablefmt
    # return image
    try:
        table = load_table_file(params, absfilename, kwargs, func_name)
        WLOG(params, '', TextEntry('40-999-00002', args=absfilename))
        return table, absfilename
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-010-00004', args=eargs))


def load_object_list(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_pp()')
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'DATABASE_DIR', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'OBJ_LIST_FILE', 'filename', kwargs, func_name)

    tablefmt = pcheck(params, 'OBJ_LIST_FILE_FMT', 'fmt', kwargs, func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename

    # add back to kwargs
    kwargs['fmt'] = tablefmt
    # return image
    try:
        table = load_table_file(params, absfilename, kwargs, func_name)
        WLOG(params, '', TextEntry('40-999-00003', args=absfilename))
        return table
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-010-00005', args=eargs))


def load_ccf_mask(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_ccf_mask()')
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'CCF_MASK_PATH', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'CCF_MASK', 'filename', kwargs, func_name)

    tablefmt = pcheck(params, 'CCF_MASK_FMT', 'fmt', kwargs, func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # add back to kwargs
    kwargs['fmt'] = tablefmt
    kwargs['colnames'] = ['ll_mask_s', 'll_mask_e', 'w_mask']
    # return image
    try:
        table = load_table_file(params, absfilename, kwargs, func_name)
        WLOG(params, '', TextEntry('40-020-00002', args=absfilename))
        return table, absfilename
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-020-00002', args=eargs))


def load_sp_mask_lsd(params, temperature=None, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_sp_mask_lsd()')
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'POLAR_LSD_PATH', 'directory', kwargs,
                       func_name)
    filekey = pcheck(params, 'POLAR_LSD_FILE_KEY', 'filekey', kwargs,
                     func_name)
    filename = kwargs.get('filename', None)
    return_filename = kwargs.get('return_filename', False)
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
    # file currently must be an ascii file and must start on line 1
    kwargs['fmt'] = 'ascii'
    kwargs['colnames'] = ['wavec', 'znum', 'depth', 'excpotf', 'lande', 'flagf']
    kwargs['datastart'] = 1
    # ----------------------------------------------------------------------
    # return image
    try:
        table = load_table_file(params, absfilename, kwargs, func_name)
        WLOG(params, '', TextEntry('40-020-00002', args=absfilename))
        return table, absfilename

    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-020-00002', args=eargs))


def load_order_mask(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_sp_mask_lsd()')
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'POLAR_LSD_PATH', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'POLAR_LSD_ORDER_MASK', 'filename', kwargs,
                     func_name)
    return_filename = kwargs.get('return_filename', False)
    # ----------------------------------------------------------------------
    # deal with return_filename
    absfilename = os.path.join(assetdir, relfolder, filename)
    if return_filename:
        return absfilename
    # ----------------------------------------------------------------------
    # file currently must be an ascii file and must start on line 1
    kwargs['fmt'] = 'ascii'
    kwargs['colnames'] = ['order', 'lower', 'upper']
    kwargs['datastart'] = 1
    # ----------------------------------------------------------------------
    # return image
    try:
        table = load_table_file(params, absfilename, kwargs, func_name)
        WLOG(params, '', TextEntry('40-020-00002', args=absfilename))
        return table, absfilename
    except LoadException:
        eargs = [filename, os.path.join(assetdir, relfolder)]
        WLOG(params, 'error', TextEntry('00-020-00002', args=eargs))


# =============================================================================
# Worker functions
# =============================================================================
def load_fits_file(params, filename, func_name):
    # load text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # check that filepath exists and log an error if it was not found
    if not os.path.exists(filename):
        eargs = [filename, func_name]
        raise LoadException(textdict['01-001-00022'].format(*eargs))
    # read image
    image = drs_fits.readfits(params, filename)
    # return image
    return image


def load_table_file(params, filename, kwargs, func_name):
    # load text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # extra parameters
    fmt = kwargs.get('fmt', 'fits')
    colnames = kwargs.get('colnames', None)
    datastart = kwargs.get('datastart', 0)
    # check that filepath exists and log an error if it was not found
    if not os.path.exists(filename):
        eargs = [filename, func_name]
        raise LoadException(textdict['01-001-00022'].format(*eargs))
    # read table
    table = drs_table.read_table(params, filename, fmt=fmt,
                                 colnames=colnames, data_start=datastart)
    # return image
    return table


def load_text_file(params, filename, func_name=None, dtype=float):
    if func_name is None:
        func_name = __NAME__ + '.load_text_file()'
    # load text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # check that filepath exists and log an error if it was not found
    if not os.path.exists(filename):
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


def save_text_file(params, filename, array, func_name):
    if func_name is None:
        func_name = __NAME__ + '.save_text_file()'
    # save text file
    try:
        drs_text.save_text_file(filename, array, func_name)
    except DrsCodedException as e:
        elevel = e.get('level', 'error')
        eargs = e.get('targs', None)
        WLOG(params, elevel, TextEntry(e.codeid, args=eargs))


def construct_path(params, filename=None, directory=None, **kwargs):
    func_name = kwargs.get('func', __NAME__ + '.construct_filename()')
    # deal with no filename
    if filename is None:
        filename = ''
    # deal with no directory
    if directory is None:
        directory = ''
    # get properties from params/jwargs
    package = pcheck(params, 'DRS_PACKAGE', 'package', kwargs, func_name)
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
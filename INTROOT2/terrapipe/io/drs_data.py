#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs data


Used to load data files from the ./data/ directory only

Created on 2019-07-02 at 09:24

@author: cook
"""
from __future__ import division
import numpy as np
import os

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from . import drs_path
from . import drs_fits
from . import drs_table

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_data.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
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
    if return_filename:
        return construct_filename(params, filename, relfolder, func=func_name)
    # split table columns
    tablecols = list(map(lambda x: x.strip(), tablecols.split(',')))
    # add back to kwargs
    kwargs['fmt'] = tablefmt
    kwargs['colnames'] = tablecols
    kwargs['data_start'] = tablestart

    # return image
    try:
        table, outf = load_table_file(params, filename, relfolder, kwargs,
                                      func_name)
        WLOG(params, '', TextEntry('40-017-00001', args=outf))
        # push columns into numpy arrays and force to floats
        ll = np.array(table[wavecol], dtype=float)
        amp = np.array(table[ampcol], dtype=float)
        # return wavelength and amplitude columns
        return ll, amp
    except LoadException:
        eargs = [filename, relfolder]
        WLOG(params, 'error', TextEntry('00-017-00002', args=eargs))


def load_cavity_file(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_badpix()')
    relfolder = pcheck(params, 'DRS_CALIB_DATA', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'CAVITY_LENGTH_FILE', 'filename', kwargs,
                      func_name)
    tablefmt = pcheck(params, 'CAVITY_LENGTH_FILE_FMT', 'fmt', kwargs,
                      func_name)
    tablecols = pcheck(params, 'CAVITY_LENGTH_FILE_COLS', 'cols', kwargs,
                       func_name)
    tablestart = pcheck(params, 'CAVITY_LENGTH_FILE_START', 'start', kwargs,
                        func_name)
    wavecol = pcheck(params, 'CAVITY_LENGTH_FILE_WAVECOL', 'wavecol', kwargs,
                     func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    if return_filename:
        return construct_filename(params, filename, relfolder, func=func_name)
    # split table columns
    tablecols = list(map(lambda x: x.strip(), tablecols.split(',')))
    # add back to kwargs
    kwargs['fmt'] = tablefmt
    kwargs['colnames'] = tablecols
    kwargs['data_start'] = tablestart

    # return image
    try:
        table, outf = load_table_file(params, filename, relfolder, kwargs,
                                      func_name)
        WLOG(params, '', TextEntry('40-999-00001', args=outf))
        # push columns into numpy arrays and force to floats
        coeff_values = np.array(table[wavecol], dtype=float)
        ncoeff = len(coeff_values)
        # reformat into well behaved array
        poly_cavity = np.zeros(ncoeff)
        for it in range(ncoeff):
            poly_cavity[it] = coeff_values[it]
        # flip to match
        poly_cavity = poly_cavity[::-1]
        # return line list and amps
        return poly_cavity
    except LoadException:
        eargs = [filename, relfolder]
        WLOG(params, 'error', TextEntry('00-008-00012', args=eargs))


def load_full_flat_badpix(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_badpix()')
    relfolder = pcheck(params, 'DRS_BADPIX_DATA', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'BADPIX_FULL_FLAT', 'filename', kwargs,
                      func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    if return_filename:
        return construct_filename(params, filename, relfolder, func=func_name)
    # return image
    try:
        image, outf = load_fits_file(params, filename, relfolder, func_name)
        WLOG(params, '', TextEntry('40-012-00003', args=outf))
        return image
    except LoadException:
        eargs = [filename, relfolder]
        WLOG(params, 'error', TextEntry('00-012-00001', args=eargs))


def load_full_flat_pp(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_pp()')
    relfolder = pcheck(params, 'DATA_ENGINEERING', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'PP_FULL_FLAT', 'filename', kwargs,
                      func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    if return_filename:
        return construct_filename(params, filename, relfolder, func=func_name)
    # return image
    try:
        image, outf = load_fits_file(params, filename, relfolder, func_name)
        WLOG(params, '', TextEntry('40-010-00011', args=outf))
        return image
    except LoadException:
        eargs = [filename, relfolder]
        WLOG(params, 'error', TextEntry('00-010-00002', args=eargs))


def load_tapas(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_pp()')
    relfolder = pcheck(params, 'DATA_CORE', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TAPAS_FILE', 'filename', kwargs, func_name)

    tablefmt = pcheck(params, 'TAPAS_FILE_FMT', 'fmt', kwargs, func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    if return_filename:
        return construct_filename(params, filename, relfolder, func=func_name)
    # add back to kwargs
    kwargs['fmt'] = tablefmt
    # return image
    try:
        table, outf = load_table_file(params, filename, relfolder, kwargs,
                                      func_name)
        WLOG(params, '', TextEntry('40-999-00002', args=outf))
        return table
    except LoadException:
        eargs = [filename, relfolder]
        WLOG(params, 'error', TextEntry('00-010-00004', args=eargs))


def load_object_list(params, **kwargs):
    # get parameters from params/kwargs
    func_name = kwargs.get('func', __NAME__ + '.load_full_flat_pp()')
    relfolder = pcheck(params, 'DATA_CORE', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'OBJ_LIST_FILE', 'filename', kwargs, func_name)

    tablefmt = pcheck(params, 'OBJ_LIST_FILE_FMT', 'fmt', kwargs, func_name)
    return_filename = kwargs.get('return_filename', False)
    # deal with return_filename
    if return_filename:
        return construct_filename(params, filename, relfolder, func=func_name)

    # add back to kwargs
    kwargs['fmt'] = tablefmt
    # return image
    try:
        table, outf = load_table_file(params, filename, relfolder, kwargs,
                                      func_name)
        WLOG(params, '', TextEntry('40-999-00003', args=outf))
        return table
    except LoadException:
        eargs = [filename, relfolder]
        WLOG(params, 'error', TextEntry('00-010-00005', args=eargs))


# =============================================================================
# Worker functions
# =============================================================================
def load_fits_file(params, filename, directory, func_name):
    # load text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # construct filename
    absfilename = construct_filename(params, filename, directory,
                                     func=func_name)
    # check that filepath exists and log an error if it was not found
    if not os.path.exists(absfilename):
        eargs = [absfilename, func_name]
        raise LoadException(textdict['01-001-00022'].format(*eargs))
    # read image
    image = drs_fits.read(params, absfilename)
    # return image
    return image, absfilename


def load_table_file(params, filename, directory, kwargs, func_name):
    # load text dict
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # construct filename
    absfilename = construct_filename(params, filename, directory,
                                     func=func_name)
    # extra parameters
    fmt = kwargs.get('fmt', None)
    colnames = kwargs.get('colnames', None)
    datastart = kwargs.get('datastart', 0)
    # check that filepath exists and log an error if it was not found
    if not os.path.exists(absfilename):
        eargs = [absfilename, func_name]
        raise LoadException(textdict['01-001-00022'].format(*eargs))
    # read table
    table = drs_table.read_table(params, absfilename, fmt=fmt,
                                 colnames=colnames, data_start=datastart)
    # return image
    return table, absfilename


def construct_filename(params, filename=None, directory=None, **kwargs):
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-06-27 at 13:54

@author: cook
"""
from __future__ import division
import numpy as np
import os
import warnings

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.core.core import drs_database


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.wave.py'
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
# Define user functions
# =============================================================================
def get_masterwave_filename(params, **kwargs):
    func_name = __NAME__ + '.get_masterwave_filename()'
    # get parameters from params/kwargs
    fiber = pcheck(params, 'FIBER', 'fiber', kwargs, func_name)
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # deal with fibers that we don't have
    usefiber = pconst.FIBER_WAVE_TYPES(fiber)
    # ------------------------------------------------------------------------
    # get file definition
    out_wave = core.get_file_definition('WAVEM', params['INSTRUMENT'],
                                        kind='red')
    # get calibration key
    key = out_wave.get_dbkey(fiber=usefiber)
    # ------------------------------------------------------------------------
    # get calibDB
    cdb = drs_database.get_full_database(params, 'calibration')
    # get filename col
    filecol = cdb.file_col
    # get the badpix entries
    waveentries = cdb.get_entry(key)
    # get filename
    filename = waveentries[filecol][-1]
    # get absolute path
    abspath = os.path.join(params['DRS_CALIB_DB'], filename)
    # return the last valid wave entry
    return abspath


def get_wavesolution(params, recipe, header=None, infile=None, **kwargs):
    """
    Get the wavelength solution

    Wavelength solution will come from "filename" if keyword argument is set

    Wavelength solution will come from calibration database if:

    1) params['CALIB_DB_FORCE_WAVESOL'] is True
    2) keyword argument "force" is True
    3) header and infile.header are not defined (None)

    Otherwise wavelength solution will come from header

    :param p: parameter dictionary, ParamDict containing constants
    :param recipe: DrsRecipe instance, the recipe instance used
    :param header: FitsHeader or None, the header to use
    :param infile: DrsFitsFile or None, the infile associated with the header
                   can be used instead of header
    :param kwargs: keyword arguments passed to function

    :keyword fiber: str, the fiber name (if not set will look for this in
                    parameter dictionary params['FIBER']
    :keyword force: bool, if True forces wave solution to come from calibDB
    :keyword filename: str or None, the filename to get wave solution from
                       this will overwrite all other options
    :return:
    """
    func_name = __NAME__ + '.get_wavesolution()'
    # get parameters from params/kwargs
    filename = kwargs.get('filename', None)
    fiber = pcheck(params, 'FIBER', 'fiber', kwargs, func_name)
    force = pcheck(params, 'CALIB_DB_FORCE_WAVESOL', 'force', kwargs,
                   func_name)
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # deal with fibers that we don't have
    usefiber = pconst.FIBER_WAVE_TYPES(fiber)
    # ------------------------------------------------------------------------
    # get file definition
    out_wave = core.get_file_definition('WAVE', params['INSTRUMENT'],
                                        kind='red')
    # get calibration key
    key = out_wave.get_dbkey(fiber=usefiber)
    # ------------------------------------------------------------------------
    # check infile is instance of DrsFitsFile
    if infile is not None:
        if isinstance(infile, drs_file.DrsFitsFile):
            eargs = [type(infile), func_name]
            WLOG(params, 'error', TextEntry('00-017-00001', args=eargs))
    # ------------------------------------------------------------------------
    # deal with no header but an infile
    if header is None and infile is not None:
        header = infile.header
    # ------------------------------------------------------------------------
    # check whether we need to force from database
    if header is None:
        force = True
    else:
        force = force or params['KW_WAVE_NBO'][0] not in header
        force = force or params['KW_WAVE_DEG'][0] not in header
        force = force or params['KW_CDBWAVE'][0] not in header
    # ------------------------------------------------------------------------
    # Mode 1: wave filename defined
    # ------------------------------------------------------------------------
    # if filename is defined get wave file from this file
    if filename is not None:
        # construct new infile instance and read data/header
        wavefile = out_wave.newcopy(filename=filename, recipe=recipe,
                                    fiber=usefiber)
        wavefile.read()
        # get wave map
        wavemap = np.array(wavefile.data)
        # set wave source of wave file
        wavesource = 'filename'
    # ------------------------------------------------------------------------
    # Mode 2: force from calibDB
    # ------------------------------------------------------------------------
    # if we are forcing from calibDB get the wave file from calibDB
    elif force:
        # get calibDB
        cdb = drs_database.get_full_database(params, 'calibration')
        # get filename col
        filecol = cdb.file_col
        # get the badpix entries
        waveentries = drs_database.get_key_from_db(params, key, cdb, header,
                                                   n_ent=1)
        # get badpix filename
        wavefilename = waveentries[filecol][0]
        wavefilepath = os.path.join(params['DRS_CALIB_DB'], wavefilename)
        # construct new infile instance and read data/header
        wavefile = out_wave.newcopy(filename=wavefilepath, recipe=recipe,
                                    fiber=usefiber)
        wavefile.read()
        # get wave map
        wavemap = np.array(wavefile.data)
        # set source of wave file
        wavesource = 'calibDB'
    # ------------------------------------------------------------------------
    # Mode 3: using header only
    # ------------------------------------------------------------------------
    # else we are using the header only
    elif infile is None:
        # get filetype from header (dprtype)
        filetype = header[params['KW_DPRTYPE'][0]]
        # get wave file instance
        wavefile = core.get_file_definition(filetype, params['INSTRUMENT'])
        # set wave file properties (using header)
        wavefile.recipe = recipe
        wavefile.header = header
        wavefile.filename = 'Unknown'
        wavefile.data = np.zeros((header['NAXIS2'], header['NAXIS1']))
        wavesource = 'header'
        # get wave map
        wavemap = None
    # ------------------------------------------------------------------------
    # Mode 4: using infile (DrsFitsFile)
    # ------------------------------------------------------------------------
    # else we are using the infile
    else:
        wavefile = infile
        wavesource = 'header'
        # get wave map
        wavemap = None

    # ------------------------------------------------------------------------
    # Now deal with using wavefile
    # -------------------------------------------------------------------------
    # extract keys from header
    nbo = wavefile.read_header_key('KW_WAVE_NBO', dtype=int)
    deg = wavefile.read_header_key('KW_WAVE_DEG', dtype=int)
    # extract cofficients from header
    wave_coeffs = wavefile.read_header_key_2d_list('KW_WAVE_PARAM',
                                                   dim1=nbo, dim2=deg + 1)
    # -------------------------------------------------------------------------
    # if wavemap is unset create it from wave coefficients
    if wavemap is None:
        # get image dimensions
        nby, nbx = infile.data.shape
        # set up storage
        wavemap = np.zeros((nbo, nbx))
        xpixels = np.arange(nbx)
        # loop aroun each order
        for order_num in range(nbo):
            # get this order coefficients
            ocoeffs = wave_coeffs[order_num][::-1]
            # calculate polynomial values and push into wavemap
            wavemap[order_num] = np.polyval(ocoeffs, xpixels)

    # -------------------------------------------------------------------------
    # store wave properties in parameter dictionary
    wprops = ParamDict()
    wprops['WAVEFILE'] = wavefile.filename
    wprops['WAVESOURCE'] = wavesource
    wprops['NBO'] = nbo
    wprops['DEG'] = deg
    wprops['COEFFS'] = wave_coeffs
    wprops['WAVEMAP'] = wavemap
    # set the source
    keys = ['WAVEMAP', 'WAVEFILE', 'WAVESOURCE', 'NBO', 'DEG', 'COEFFS']
    wprops.set_sources(keys, func_name)

    # -------------------------------------------------------------------------
    # return the map and properties
    return wprops





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

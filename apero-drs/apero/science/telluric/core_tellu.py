#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:16

@author: cook
"""
from typing import List, Tuple, Union

import numpy as np
from astropy import constants as cc
from astropy import units as uu
from astropy.table import Table

from apero.base import base as apero_base
from apero.core import drs_database
from apero.core import drs_file
from apero.io import drs_fits
from apero.utils import drs_data
from apero.utils import drs_recipe
from aperocore import drs_lang
from aperocore import math as mp
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_misc

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.gen_calib.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsRecipe = drs_recipe.DrsRecipe
# get calibration database
TelluDatabase = drs_database.TelluricDatabase
# Get function string
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value

# =============================================================================
# Define functions
# =============================================================================
# for: load_tellu_file
LoadTelluFileReturn = Union[str,
                            Tuple[str, str],
                            Tuple[Union[np.ndarray, Table, None],
                            Union[drs_fits.Header, None], str],
                            Tuple[Union[np.ndarray, Table, None],
                            Union[drs_fits.Header, None], str, str],
                            List[str],
                            Tuple[List[str], str],
                            Tuple[List[Union[np.ndarray, Table, None]],
                            List[Union[drs_fits.Header, None]],
                            List[str]],
                            Tuple[List[Union[np.ndarray, None]],
                            List[Union[drs_fits.Header, None]],
                            List[str], str],
                            Tuple[None, None, None, str],
                            Tuple[None, None, None]]


def load_tellu_file(params: ParamDict, shortname: str, key: str,
                    inheader: Union[drs_fits.Header, None] = None,
                    filename: Union[str, None] = None,
                    get_image: bool = True, get_header: bool = False,
                    fiber: Union[str, None] = None,
                    userinputkey: Union[str, None] = None,
                    database: Union[TelluDatabase, None] = None,
                    return_filename: bool = False, return_source: bool = False,
                    mode: Union[str, None] = None,
                    n_entries: Union[int, str] = 1,
                    objname: Union[str, None] = None,
                    tau_water: Union[Tuple[float, float], None] = None,
                    tau_others: Union[Tuple[float, float], None] = None,
                    no_times: bool = False,
                    required: bool = True, ext: Union[int, None] = None,
                    fmt: str = 'fits',
                    kind: str = 'image') -> LoadTelluFileReturn:
    """
    Load one or many telluric files

    :param params: ParamDict, the parameter dictionary of constants
    :param key: str, the key from the telluric database to select a
                specific telluric with
    :param inheader: fits.Header - the header file (required to match by time)
                     if None does not match by a 'zero point' time)

    :param filename: str or None, if set overrides filename from database
    :param get_image: bool, if True loads image (or images if nentries > 1),
                      if False image is None (or list of Nones if nentries > 1)
    :param get_header: bool, if True loads header (or headers if nentries > 1)
                       if False header is None (or list of Nones if
                       nentries > 1)
    :param fiber: str or None, if set must be the fiber type - all returned
                  calibrations are filtered by this fiber type
    :param userinputkey: str or None, if set checks params['INPUTS'] for this
                         key and sets filename from here - note params['INPUTS']
                         is where command line arguments are stored
    :param database: drs telluric database instance - set this if calibration
                     database already loaded (if unset will reload the database)
    :param return_filename: bool, if True returns the filename only
    :param return_source: bool, if True returns the source of the calib file(s)
    :param mode: str or None, the time mode for getting from sql
                 ('closest'/'newer'/'older')
    :param n_entries: int or str, maximum number of calibration files to return
                      for all entries use '*'
    :param objname: str or None, if set OBJECT=="fiber"
    :param tau_water: tuple or None, if set sets the lower and upper
                      bounds for tau water i.e.
                      TAU_WATER > tau_water[0]
                      TAU_WATER < tau_water[1]
    :param tau_others: tuple or None, if set sets the lower and upper bounds
                       for tau others  i.e.
                       TAU_OTHERS > tau_others[0]
                       TAU_OTHERS < tau_others[1]
    :param no_times: bool, if True does not use times to choose correct
                 files
    :param required: bool, whether we require an entry - will raise exception
                     if required=True and no entries found
    :param ext: int, valid extension (None by default) when kind='image'
    :param fmt: str, astropy.table.Table valid format (when kind='table')
    :param kind: str, either 'image' for fits image or 'table' for table

    :return:
             if get_image, also returns image/table or list of images/tables
             if get_header, also returns header or list of headers
             if return_filename, returns filename or list of filenames
             if return_source, also returns source

             i.e. possible returns are:
                 filename
                 filename, source
                 image, header, filename
                 image, header, filename, source
                 List[filename]
                 List[filename], source
                 List[image], List[header], List[filename]
                 List[image], List[header], List[filename], source

    """
    # set function
    # _ = display_func('load_tellu_file', __NAME__)
    # ------------------------------------------------------------------------
    # first try to get file from inputs
    fout = drs_data.get_file_from_inputs(params, 'telluric', userinputkey,
                                         filename, return_source=return_source)
    if return_source:
        filename, source = fout
    else:
        filename, source = fout, 'None'
    # ------------------------------------------------------------------------
    # if filename is defined this is the filename we should return
    if filename is not None and return_filename:
        if return_source:
            return str(filename), source
        else:
            return str(filename)
    # -------------------------------------------------------------------------
    # else we have to load from database
    if filename is None:
        # check if we have the database
        if database is None:
            # construct a new database instance
            database = TelluDatabase(params, shortname)
            # load the database
            database.load_db()
        # load filename from database
        filename = database.get_tellu_file(key, header=inheader,
                                           timemode=mode, nentries=n_entries,
                                           required=required, fiber=fiber,
                                           objname=objname, tau_water=tau_water,
                                           tau_others=tau_others,
                                           no_times=no_times)
        source = 'telluDB'
    # -------------------------------------------------------------------------
    # deal with filename being a path --> string (unless None)
    if filename is not None:
        if isinstance(filename, list):
            filename = list(map(lambda strfile: str(strfile), filename))
        else:
            filename = str(filename)
    # -------------------------------------------------------------------------
    # if we are just returning filename return here
    if return_filename:
        if return_source:
            return filename, source
        else:
            return filename
    # -------------------------------------------------------------------------
    # deal with no file
    if filename is None:
        if return_source:
            return None, None, None, 'None'
        else:
            return None, None, None
    # -------------------------------------------------------------------------
    # need to deal with a list of files
    if isinstance(filename, list):
        # storage for images and headres
        images, headers = [], []
        # loop around files
        for file_it in filename:
            # now read the calibration file
            image, header = drs_data.read_db_file(params, file_it, get_image,
                                                  get_header, kind, fmt, ext)
            # append to storage
            images.append(image)
            headers.append(headers)
        # return all
        if return_source:
            return images, headers, filename, source
        else:
            return images, headers, filename
    # -------------------------------------------------------------------------
    else:
        # now read the calibration file
        image, header = drs_data.read_db_file(params, filename, get_image,
                                              get_header, kind, fmt, ext)
        # return all
        if return_source:
            return image, header, filename, source
        else:
            return image, header, filename


# TODO: should splinek=5 (default before 2023-01-18)
def wave_to_wave(params, spectrum, wave1, wave2, reshape=False, splinek=5):
    """
    Shifts a "spectrum" at a given wavelength solution (map), "wave1", to
    another wavelength solution (map) "wave2"

    :param params: ParamDict, the parameter dictionary
    :param spectrum: numpy array (2D),  flux in the reference frame of the
                     file wave1
    :param wave1: numpy array (2D), initial wavelength grid
    :param wave2: numpy array (2D), destination wavelength grid
    :param reshape: bool, if True try to reshape spectrum to the shape of
                    the output wave solution
    :param splinek: int, the splinke k value

    :return output_spectrum: numpy array (2D), spectrum resampled to "wave2"
    """
    func_name = __NAME__ + '._wave_to_wave()'
    # deal with reshape
    if reshape or (spectrum.shape != wave2.shape):
        try:
            spectrum = spectrum.reshape(wave2.shape)
        except ValueError:
            # log that we cannot reshape spectrum
            eargs = [spectrum.shape, wave2.shape, func_name]
            raise AperoCodedException(params, '09-019-00004', targs=eargs)
    # if they are the same
    # noinspection PyTypeChecker
    if mp.nansum(wave1 != wave2) == 0:
        return spectrum
    # size of array, assumes wave1, wave2 and spectrum have same shape
    sz = np.shape(spectrum)
    # create storage for the output spectrum
    output_spectrum = np.zeros(sz) + np.nan
    # looping through the orders to shift them from one grid to the other
    for iord in range(sz[0]):
        # only interpolate valid pixels
        g = np.isfinite(spectrum[iord, :])
        # if not enough valid pixel, then skip order (need k+1 points)
        if mp.nansum(g) > 6:
            # spline the spectrum
            spline = mp.iuv_spline(wave1[iord, g], spectrum[iord, g],
                                   k=splinek, ext=3)
            # keep track of pixels affected by NaNs
            splinemask = mp.iuv_spline(wave1[iord, :], g, k=1, ext=1)
            # spline the input onto the output
            output_spectrum[iord, :] = spline(wave2[iord, :])
            # find which pixels are not NaNs
            mask = splinemask(wave2[iord, :])
            # set to NaN pixels outside of domain
            bad = (output_spectrum[iord, :] == 0)
            output_spectrum[iord, bad] = np.nan
            # affected by a NaN value
            # normally we would use only pixels ==1, but we get values
            #    that are not exactly one due to the interpolation scheme.
            #    We just set that >50% of the
            # flux comes from valid pixels
            bad = (mask <= 0.9)
            # mask pixels affected by nan
            output_spectrum[iord, bad] = np.nan
    # return the filled output spectrum
    return output_spectrum


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

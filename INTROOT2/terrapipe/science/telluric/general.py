#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:16

@author: cook
"""
from __future__ import division
import numpy as np

from terrapipe import core
from terrapipe.core import constants
from terrapipe.core import math
from terrapipe import locale
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file
from terrapipe.core.core import drs_database
from terrapipe.io import drs_data


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.general.py'
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
# Define functions
# =============================================================================
def get_whitelist(params, **kwargs):
    func_name = __NAME__ + '.get_whitelist()'
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_WHITELIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    whitelist = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                        func_name)
    # return the whitelist
    return whitelist


def get_blacklist(params, **kwargs):
    func_name = __NAME__ + '.get_blacklist()'
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECOTRY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLU_BLACKLIST_NAME', 'filename', kwargs,
                      func_name)
    # load the white list
    blacklist = drs_data.load_text_file(params, filename, relfolder, kwargs,
                                        func_name)
    # return the whitelist
    return blacklist


# =============================================================================
# Database functions
# =============================================================================
def load_tellu_file(params, key=None, header=None, filename=None, **kwargs):
    func_name = kwargs.get('func', __NAME__ + '.load_tellu_file()')
    # get file
    return drs_database.load_db_file(params, key, header, filename,
                                     where='telluric', func=func_name,
                                     **kwargs)

# =============================================================================
# Tapas functions
# =============================================================================
def load_conv_tapas(params, recipe, header, mprops, fiber, **kwargs):

    # ----------------------------------------------------------------------
    # Load any convolved files from database
    # ----------------------------------------------------------------------
    # get file definition
    out_tellu_conv = recipe.outputs['TELL_CONV'].newcopy(recipe=recipe,
                                                         fiber=fiber)
    # get key
    conv_key = out_tellu_conv.get_dbkey()
    # load tellu file
    conv_files, conv_paths = load_tellu_file(params, conv_key, header,
                                             n_entries='all')
    # construct the filename from file instance
    out_tellu_conv.construct_filename(params, infile=mprops['WAVEINST'])

    # if our npy file already exists then we just need to read it
    if out_tellu_conv.filename in conv_files:
        # log that we are loading tapas convolved file
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00001', args=wargs))
        # load npy file
        out_tellu_conv.read(params)
    # else we need to load tapas and generate the convolution
    else:
        # ------------------------------------------------------------------
        # Load the raw TAPAS atmospheric transmission
        # ------------------------------------------------------------------
        tapas_raw_table, tapas_raw_filename = drs_data.load_tapas(params)
        # ------------------------------------------------------------------
        # Convolve with master wave solution
        # ------------------------------------------------------------------
        tapas_all_species = _convolve_tapas(params, tapas_raw_table, mprops)
        # ------------------------------------------------------------------
        # Save convolution for later use
        # ------------------------------------------------------------------
        out_tellu_conv.data = tapas_all_species
        # log saving
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', TextEntry('40-019-00002', args=wargs))
        # save
        out_tellu_conv.write(params)
        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
        # copy the order profile to the calibDB
        drs_database.add_file(params, out_tellu_conv)




# =============================================================================
# Worker functions
# =============================================================================
def _convolve_tapas(params, tapas_table, mprops, **kwargs):

    func_name = __NAME__ + '._convolve_tapas()'
    # get parameters from params/kwargs
    tellu_absorbers = pcheck(params, 'TELLU_ABSORBERES', 'absorbers', kwargs,
                             func_name)
    fwhm_pixel_lsf = pcheck(params, 'FWHM_PIXEL_LSF', 'fwhm_lsf', kwargs,
                            func_name)

    # get master wave data
    masterwave = mprops['WAVEMAP']
    ydim = mprops['NBO']
    xdim = mprops['NBPIX']

    # ----------------------------------------------------------------------
    # generate kernel for convolution
    # ----------------------------------------------------------------------
    # get the number of kernal pixels
    npix_ker = int(np.ceil(3 * fwhm_pixel_lsf * 3.0 / 2) * 2 + 1)
    # set up the kernel exponent
    kernel = np.arange(npix_ker) - npix_ker // 2
    # kernal is the a gaussian
    kernel = np.exp(-0.5 * (kernel / (fwhm_pixel_lsf / math.fwhm())) ** 2)
    # we only want an approximation of the absorption to find the continuum
    #    and estimate chemical abundances.
    #    there's no need for a varying kernel shape
    kernel /= np.nansum(kernel)

    # ----------------------------------------------------------------------
    # storage for output
    tapas_all_species = np.zeros([len(tellu_absorbers), xdim * ydim])
    # ----------------------------------------------------------------------
    # loop around each molecule in the absorbers list
    #    (must be in
    for n_species, molecule in enumerate(tellu_absorbers):
        # log process
        wmsg = 'Processing molecule: {0}'
        WLOG(params, '', wmsg.format(molecule))
        # get wavelengths
        lam = tapas_table['wavelength']
        # get molecule transmission
        trans = tapas_table['trans_{0}'.format(molecule)]
        # interpolate with Univariate Spline
        tapas_spline = math.iuv_spline(lam, trans)
        # log the mean transmission level
        wmsg = '\tMean Trans level: {0:.3f}'.format(np.mean(trans))
        WLOG(params, '', wmsg)
        # convolve all tapas absorption to the SPIRou approximate resolution
        for iord in range(ydim):
            # get the order position
            start = iord * xdim
            end = (iord * xdim) + xdim
            # interpolate the values at these points
            svalues = tapas_spline(masterwave[iord, :])
            # convolve with a gaussian function
            cvalues = np.convolve(svalues, kernel, mode='same')
            # add to storage
            tapas_all_species[n_species, start: end] = cvalues
    # deal with non-real values (must be between 0 and 1
    tapas_all_species[tapas_all_species > 1] = 1
    tapas_all_species[tapas_all_species < 0] = 0


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

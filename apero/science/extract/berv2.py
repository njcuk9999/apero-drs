#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-10-2020-10-29 15:40

@author: cook
"""
from astropy import units as uu
from astropy.coordinates import SkyCoord
import numpy as np
import os
from typing import List, Union
import warnings

from apero.base import base
from apero.base import drs_exceptions
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core import math as mp
from apero.io import drs_lock
from apero.io import drs_path
from apero.io import drs_fits
from apero.science.extract import bervest
from apero.science.extract import crossmatch



# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.berv.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Astropy Time and Time Delta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# get param dict
ParamDict = constants.ParamDict
# Get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)

# =============================================================================
# Define functions
# =============================================================================
def get_berv(params, infile=None, header=None, props=None, log=True,
             warn=False, force=False,
             dprtypes: Union[List[str], None] = None):

    func_name = __NAME__ + '.get_berv()'
    # log progress
    if log:
        WLOG(params, 'info', TextEntry('40-016-00017'))
    # get parameters from params and kwargs
    dprtypes = pcheck(params, 'EXT_ALLOWED_BERV_DPRTYPES', func=func_name,
                      mapf='list', dtype=str, override=dprtypes)

    # lets store properties in a param dict
    bprops = ParamDict()



def get_keys_from_header(params, header, bprops):

    # make sure header is drs_fits.header
    if not isinstance(header, drs_fits.Header):
        header = drs_fits.Header(header)

    # get barycorrpy berv measurement (or set NaN)
    bprops['BERV'] = header.get(params['KW_BERV'][0], np.nan)
    # get barycorrpy BJD measurment (or set NaN)
    bprops['BJD'] = header.get(params['KW_BJD'][0], np.nan)
    # get barycorrpy BERVMAX (or set NaN)
    bprops['BERV_MAX'] = header.get(params['KW_BERVMAX'][0], np.nan)
    # get barycorrpy berv diff (or set NaN)
    bprops['DBERV'] = header.get(params['KW_DBERV'][0], np.nan)
    # get berv source
    bprops['BERVSOURCE'] = header.get(params['KW_BERVSOURCE'][0], 'None')
    # get pyasl (berv estimate) BERV measurement (or set NaN)
    bprops['BERV_EST'] = header.get(params['KW_BERV_EST'][0], np.nan)
    # get pyasl (berv estimate) BJD measurement (or set NaN)
    bprops['BJD_EST'] = header.get(params['KW_BJD_EST'][0], np.nan)
    # get pyasl (berv estimate) BJD measurement (or set NaN)
    bprops['BERV_MAX_EST'] = header.get(params['KW_BERV_MAX_EST'][0], np.nan)
    # get the berv diff from pyasl (or set NaN)
    bprops['DBERV_EST'] = header.get(params['KW_DBERV_EST'][0], np.nan)
    # get the observation time and method parameters
    bprops['OBSTIME'] = header.get(params['KW_BERV_OBSTIME'][0], np.nan)
    bprops['OBSTIMEMETHOD'] = header.get(params['KW_BERV_OBSTIME_METHOD'],
                                         'None')
    # get object name and source
    bprops['DRS_OBJNAME'] = header.get(params['KW_DRS_OBJNAME'], np.nan)
    bprops['DRS_OBJNAME_S'] = header.get(params['KW_DRS_OBJNAME_S'], 'None')
    # get gaia id and source
    bprops['DRS_GAIAID'] = header.get(params['KW_DRS_GAIAID'], np.nan)

    # TODO: Got to here

    header.set_key(params, 'KW_DRS_GAIAID', value=self.gaia_id)
    header.set_key(params, 'KW_DRS_GAIAID_S', value=self.gaia_id_source)
    # add the ra and source
    header.set_key(params, 'KW_DRS_RA', value=self.ra)
    header.set_key(params, 'KW_DRS_RA_S', value=self.ra_source)
    # add the dec and source
    header.set_key(params, 'KW_DRS_DEC', value=self.dec)
    header.set_key(params, 'KW_DRS_DEC_S', value=self.dec_source)
    # add the pmra
    header.set_key(params, 'KW_DRS_PMRA', value=self.pmra)
    header.set_key(params, 'KW_DRS_PMRA_S', value=self.pmra_source)
    # add the pmde
    header.set_key(params, 'KW_DRS_PMDE', value=self.pmde)
    header.set_key(params, 'KW_DRS_PMDE_S', value=self.pmde_source)
    # add the plx
    header.set_key(params, 'KW_DRS_PLX', value=self.plx)
    header.set_key(params, 'KW_DRS_PLX_S', value=self.plx_source)
    # add the rv
    header.set_key(params, 'KW_DRS_RV', value=self.rv)
    header.set_key(params, 'KW_DRS_RV_S', value=self.rv_source)
    # add the gmag
    header.set_key(params, 'KW_DRS_GMAG', value=self.gmag)
    header.set_key(params, 'KW_DRS_GMAG_S', value=self.gmag_source)
    # add the bpmag
    header.set_key(params, 'KW_DRS_BPMAG', value=self.bpmag)
    header.set_key(params, 'KW_DRS_BPMAG_S', value=self.bpmag_source)
    # add the rpmag
    header.set_key(params, 'KW_DRS_RPMAG', value=self.rpmag)
    header.set_key(params, 'KW_DRS_RPMAG_S', value=self.rpmag_source)
    # add the epoch
    header.set_key(params, 'KW_DRS_EPOCH', value=self.epoch)
    header.set_key(params, 'KW_DRS_EPOCH_S', value=self.epoch_source)
    # add the teff
    header.set_key(params, 'KW_DRS_TEFF', value=self.teff)
    header.set_key(params, 'KW_DRS_TEFF_S', value=self.teff_source)




# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

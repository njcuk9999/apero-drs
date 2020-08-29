#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

@author: cook
"""
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy import units as uu
import os
import shutil

from apero.base import base
from apero import core
from apero.core import constants
from apero import lang


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'get_grid_models.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)

# MIN WAVELENGTH (slightly before detector)   [um]
WAVE_MIN = 950
# MAX WAVELENGTH (slightly after detector)    [um]
WAVE_MAX = 2550
# MIN TEMP [K]
MIN_TEMP = 2800
# MAX_TEMP [K]
MAX_TEMP = 7000
# Temperature bins
TEMP_BINS = 100
# Define output column names
WAVECOL = 'WAVELENGTH'
TEMPCOL = 'TEFF{0}'
# Define the URL where models are hosted
URL = 'ftp://phoenix.astro.physik.uni-goettingen.de/HiResFITS/'
# Define the workspace with temporary files in
WORKSPACE = ''
# Define the wavelength file to use
WAVE_FILE = 'WAVE_PHOENIX-ACES-AGSS-COND-2011.fits'
WAVE_UNITS = uu.AA
# Define the path to the models
MODEL_PATH = 'PHOENIX-ACES-AGSS-COND-2011/Z-0.0/'
# Define the model file
MODEL_FILE = 'lte0{teff}-4.50-0.0.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits'
# Define the output table name
TABLENAME = 'goettingen_model_grids.fits'

# =============================================================================
# Define functions
# =============================================================================
def get_url(download_url, infile, outpath):
    # construct wave file url
    url = download_url + '/' + infile
    # get wave file
    os.system('wget {0}'.format(url))
    # move file to saved_wave_file
    if not os.path.exists(outpath):
        shutil.move(infile, outpath)


def main():
    # create a table for output
    table = Table()

    # ----------------------------------------------------------------------
    # Wave file
    # ----------------------------------------------------------------------
    # construct save wave file name
    saved_wave_file = os.path.join(WORKSPACE, WAVE_FILE)
    # get wave file
    if not os.path.exists(saved_wave_file):
        print('Getting wavelength file')
        get_url(URL, WAVE_FILE, saved_wave_file)
    # open wave file
    wave = fits.getdata(saved_wave_file)
    # give units
    wave = wave * WAVE_UNITS
    # convert to micron and remove units
    wave = wave.to(uu.um).value
    # only keep valid wavelength
    keep = (wave > WAVE_MIN) & (wave < WAVE_MAX)
    # add column to table
    table[WAVECOL] = wave[keep]

    # ----------------------------------------------------------------------
    # Temperature files
    # ----------------------------------------------------------------------
    # get temperature values
    temperatures = np.arange(MIN_TEMP, MAX_TEMP, TEMP_BINS).astype(int)

    # loop around temperature range
    for temperature in temperatures:
        # construct model filename
        model_file = MODEL_FILE.format(teff=temperature)
        saved_model_file = os.path.join(WORKSPACE, model_file)
        # get model
        if not os.path.exists(saved_model_file):
            print('Getting model for Teff = {0} K'.format(temperature))
            get_url(URL, model_file, saved_model_file)
        # load the model
        print('Loading model for Teff = {0} K'.format(temperature))
        model = fits.getdata(saved_model_file)
        # add column to table
        table[TEMPCOL.format(temperature)] = model[keep]

    # ----------------------------------------------------------------------
    # Write table
    # ----------------------------------------------------------------------
    table.write(TABLENAME, overwrite=True)

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main
    main()

# =============================================================================
# End of code
# =============================================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-04-05 11:44:00

@author: cook
"""
import numpy as np
import os
from scipy.signal import medfilt, convolve2d
from astropy.table import Table
from astropy.io import fits

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.testing import drs_dev

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_pphotpix_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get constants
Constants = constants.load(__INSTRUMENT__)
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
Help = lang.core.drs_lang_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])

# whether this is a debug run (produces mask image)
DEBUG = False
# define relative output path
DEBUGFILE = 'mask_hotpix_pp.fits'

# -----------------------------------------------------------------------------
# get file definitions for this instrument
FMOD = drs_dev.FileDefinition(instrument=__INSTRUMENT__)
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
c_hotpix = drs_dev.TmpRecipe()
c_hotpix.name = __NAME__
c_hotpix.shortname = 'CRT_HTPX'
c_hotpix.instrument = __INSTRUMENT__
c_hotpix.outputdir = 'reduced'
c_hotpix.inputdir = 'raw'
c_hotpix.inputtype = 'raw'
c_hotpix.extension = 'fits'
c_hotpix.description = ('Create the hotpix table for an instrument (required '
                        'for preprocessing)')
c_hotpix.kind = 'misc'
c_hotpix.set_arg(pos=0, name='directory', dtype='directory',
                 helpstr=Help['DIRECTORY_HELP'])
c_hotpix.set_arg(pos=1, name='darkfile', dtype='file',
                 helpstr='[STRING] The night name (directory name)',
                 files=[FMOD.files.raw_dark_dark_int,
                        FMOD.files.raw_dark_dark_tel])
c_hotpix.set_kwarg(name='--debugfile', dtype='switch', default=False,
                   helpstr='If set activates debug mode (saves mask)')
# add recipe to recipe definition
RMOD.add(c_hotpix)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(instrument=None, directory=None, darkfile=None, **kwargs):
    """
    Main function for exposuremeter_spirou.py

    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(instrument=instrument, directory=directory,
                   darkfile=darkfile, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success)


def __main__(recipe, params):
    # get input dark file drs fits file instance
    darkfile = params['INPUTS']['darkfile'][1][0]
    debug = params['INPUTS']['debugfile']

    # ----------------------------------------------------------------------
    # Prepare dark file
    # ----------------------------------------------------------------------
    WLOG(params, '', 'Loading dark and preparing image')
    # load file
    image = darkfile.data
    # set NaNS and infs to zero. NaN pixels will not be flagged as hot pixels
    image[~np.isfinite(image)] = 0
    # subtract a DC offset of the image level
    image = image - mp.nanmedian(image)
    # express image normalized in terms of sigma
    image = image / np.nanpercentile(np.abs(image), 100 * mp.normal_fraction())

    # ----------------------------------------------------------------------
    # Find hot pixels
    # ----------------------------------------------------------------------
    WLOG(params, '', 'Finding hot pixels')
    # get box size from parameters
    boxsize = params['PP_HOTPIX_BOXSIZE']
    threshold = params['PP_CORRUPT_HOT_THRES']
    # a hot pixel is a point that is > 10 sigma (positive) and that has a
    # 5x5 median around it that is within +/- 1 sigma; it is well-behaved and
    #  not surrounded by bad pixels
    WLOG(params, '', '\t- median filter')
    medimage = medfilt(image, [boxsize, boxsize])

    # find the hot pixels
    mask = (np.abs(medimage) < 1.0) & (image > threshold)
    hotpix = np.array(mask).astype(float)

    # find if hot pixels are alone in a 5x5 box
    WLOG(params, '', '\t- convolve')
    box = np.ones([boxsize, boxsize]).astype(float)
    neighbours = convolve2d(hotpix, box, mode='same')

    # after the convolution, isolated (within 5x5)
    #     hotpixels have neighbours = 1
    WLOG(params, '', '\t- find neighbours')
    has_neighbours = neighbours == 1
    # set non-isolated hot pixels to zero
    hotpix[~has_neighbours] = 0.0

    # find positions in x and y of good hot pixels
    WLOG(params, '', '\t- locate')
    y, x = np.where(hotpix)

    # ----------------------------------------------------------------------
    # write table to file
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, '', 'Writing to file')
    # create table
    table = Table()
    table['nsig'] = image[y, x]
    table['xpix'] = x
    table['ypix'] = y

    # get outpath
    assetdir = params['DRS_DATA_ASSETS']
    filename = params['PP_HOTPIX_FILE']
    relpath = params['DATA_ENGINEERING']
    absoutpath = os.path.join(assetdir, relpath, filename)
    # write output as a csv file
    WLOG(params, '', '\t Saved to: {0}'.format(absoutpath))
    table.write(absoutpath, format='csv', overwrite=True)

    # if debug is True save the mask (to compare to image)
    if debug:
        # get debug file
        debugabspath = os.path.join(assetdir, relpath, DEBUGFILE)
        # print progress
        WLOG(params, '', '\t Saved debug to: {0}'.format(debugabspath))
        # write to file
        fits.writeto(debugabspath, hotpix, overwrite=True)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

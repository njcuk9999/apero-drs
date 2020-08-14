#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-14 12:48

@author: cook
"""
import numpy as np
import warnings

from apero import core
from apero import lang
from apero.core import constants
from apero.io import drs_fits
from apero.core import math as mp
from apero.science.calib import shape
from apero.science.calib import wave
from apero.science import telluric
from apero.tools.module.testing import drs_dev
from apero.tools.module.utils import inverse

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_drift_spirou.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
Help = lang.drs_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# get file definitions for this instrument
FMOD = drs_dev.FileDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
cal_drift = drs_dev.TmpRecipe()
cal_drift.name = __NAME__
cal_drift.shortname = 'DRIFT'
cal_drift.instrument = __INSTRUMENT__
cal_drift.outputdir = 'reduced'
cal_drift.inputdir = 'reduced'
cal_drift.inputtype = 'reduced'
cal_drift.extension = 'fits'
cal_drift.description = 'Calculates the drift in a set of FP_FP files'
cal_drift.kind = 'misc'
cal_drift.set_arg(pos=0, name='directory', dtype='directory',
                      helpstr=Help['DIRECTORY_HELP'])

# add recipe to recipe definition
RMOD.add(cal_drift)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, **kwargs):
    """
    Main function for exposuremeter_spirou.py

    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return core.end_main(params, llmain, recipe, success)


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'

    # ----------------------------------------------------------------------
    # Get all FP_FP e2ds files
    # ----------------------------------------------------------------------
    # check file type
    filetype = 'FP_FP'
    outtype = 'EXT_E2DS_FF'

    if filetype not in params['ALLOWED_FP_TYPES']:
        emsg = TextEntry('01-001-00020', args=[filetype, mainname])
        for allowedtype in params['ALLOWED_FP_TYPES']:
            emsg += '\n\t - "{0}"'.format(allowedtype)
        WLOG(params, 'error', emsg)
    # get all "filetype" filenames
    filenames = drs_fits.find_files(params, recipe, kind='reduced',
                                    KW_DPRTYPE=filetype,
                                    KW_OUTPUT=outtype)
    # convert to numpy array
    filenames = np.array(filenames)




# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================

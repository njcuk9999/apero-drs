#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
from __future__ import division
import numpy as np
import warnings

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core import math as mp
from terrapipe.core.core import drs_database
from terrapipe.io import drs_fits
from terrapipe.io import drs_image
from terrapipe.science.calib import flat_blaze
from terrapipe.science.calib import general
from terrapipe.science.calib import localisation
from terrapipe.science.calib import shape
from terrapipe.science.calib import wave
from terrapipe.science import extract

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_update_berv.py'
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
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for cal_extract_spirou.py

    :param directory: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
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


    # find all OBJ_DARK and OBJ_FP files
    filetypes = ['OBJ_FP', 'OBJ_DARK']
    intype = 'EXT_E2DS_FF'

    # loop around files and update BERV
    for filetype in filetypes:
        # Get filetype definition
        infiletype = core.get_file_definition(intype, params['INSTRUMENT'],
                                              kind='red')
        # get files of this type
        filenames = drs_fits.find_files(params, kind='red',
                                        KW_DPRTYPE=filetypes,
                                        KW_OUTPUT=intype)
        # loop around filenames
        for filename in filenames:
            # get new copy of file definition
            infile = infiletype.newcopy(recipe=recipe)
            # set reference filename
            infile.set_filename(filename)
            # read data
            infile.read()
            # ----------------------------------------------------------
            # get header from file instance
            header = infile.header
            # ----------------------------------------------------------
            # Calculate Barycentric correction
            # ----------------------------------------------------------
            props = ParamDict()
            props['DPRTYPE'] = infile.get_key('KW_DPRTYPE', dtype=float)
            bprops = extract.get_berv(params, infile, header, props, warn=True)


            args = [infile.basename, bprops['USE_BERV']]
            print('{0} USE_BERV: {1}'.format(*args))


    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

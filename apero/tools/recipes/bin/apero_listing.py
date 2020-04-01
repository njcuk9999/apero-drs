#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-09-16 at 13:48

@author: cook
"""
import os

from apero import core
from apero import locale
from apero.core import constants
from apero.core.core import drs_startup
from apero.tools.module import listing
from apero.io import drs_fits

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_listing.py'
__INSTRUMENT__ = 'None'
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
def main(instrument=None, **kwargs):
    """
    Main function for apero_listing.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(instrument=instrument, **kwargs)
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
    # get the night name from inputs
    nightname = params['INPUTS']['NIGHTNAME']
    # get the kidn from inputs
    kind = params['INPUTS']['KIND']
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # get index file name
    index_file_name = pconst.INDEX_OUTPUT_FILENAME()
    # ----------------------------------------------------------------------
    # Deal with kind
    # ----------------------------------------------------------------------
    # deal with kind
    if kind.lower() == 'raw':
        # push files in to runs/raw_index
        _ = drs_fits.find_raw_files(params, recipe)

        return core.return_locals(params, locals())
    elif kind.lower() == 'tmp':
        path = params['DRS_DATA_WORKING']
        columns = pconst.RAW_OUTPUT_KEYS()
    elif kind.lower() == 'red':
        path = params['DRS_DATA_REDUC']
        columns = pconst.REDUC_OUTPUT_KEYS()
    else:
        path = params['DRS_DATA_WORKING']
        columns = pconst.RAW_OUTPUT_KEYS()
    # ----------------------------------------------------------------------
    # Deal with night name
    # ----------------------------------------------------------------------
    if (nightname is None) or (nightname == ''):
        nightnames = listing.get_nightnames(params, path)
    else:
        nightnames = [nightname]
    # ----------------------------------------------------------------------
    # Loop over night name
    # ----------------------------------------------------------------------
    # loop around night names
    for nightname in nightnames:
        # construct path
        path1 = os.path.join(path, nightname)
        # test path exists
        if not os.path.exists(path1):
            # log error and exit
            eargs = [nightname, path]
            WLOG(params, 'error', TextEntry('09-504-00001', args=eargs))
        # else log the progress
        else:
            WLOG(params, 'info', TextEntry('40-504-00005', args=[nightname]))
        # ----------------------------------------------------------------------
        # Find all index files and remove them (we are remaking them)
        # ----------------------------------------------------------------------
        listing.remove_index_files(params, path1)
        # ----------------------------------------------------------------------
        # Get all files in this directory
        # ----------------------------------------------------------------------
        files = listing.get_all_files(params, path1)
        # ----------------------------------------------------------------------
        # Read header outputs for all these files
        # ----------------------------------------------------------------------
        output_dictionary = listing.get_outputs(params, files)
        # ----------------------------------------------------------------------
        # Create indexing for all these files
        # ----------------------------------------------------------------------
        # get the index path
        index_path = os.path.join(path1, index_file_name)
        # index
        istore = drs_startup.indexing(params, output_dictionary, columns,
                                      index_path)
        # save to file
        drs_startup.save_index_file(params, istore, index_path)

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

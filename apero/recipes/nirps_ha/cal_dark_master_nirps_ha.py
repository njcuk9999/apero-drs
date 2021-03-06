#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

@author: cook
"""
import numpy as np

from apero import core
from apero import lang
from apero.core import constants
from apero.core.core import drs_database
from apero.core.instruments.spirou import file_definitions
from apero.io import drs_fits
from apero.io import drs_path
from apero.science.calib import dark


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_dark_master_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict


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
    Main function for cal_dark_master_spirou.py

    :param kwargs: any additional keywords

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
    # extract file type from inputs
    filetypes = params['INPUTS'].listp('FILETYPE', dtype=str)
    # get allowed dark types
    allowedtypes = params.listp('ALLOWED_DARK_TYPES', dtype=str)
    # set up plotting (no plotting before this)
    recipe.plot.set_location()

    # ----------------------------------------------------------------------
    # Get all preprocessed dark files
    # ----------------------------------------------------------------------
    filenames = []

    # check file type
    for filetype in filetypes:
        if filetype not in allowedtypes:
            emsg = TextEntry('01-001-00020', args=[filetype, mainname])
            for allowedtype in allowedtypes:
                emsg += '\n\t - "{0}"'.format(allowedtype)
            WLOG(params, 'error', emsg)
        # get all "filetype" filenames
        files = drs_fits.find_files(params, recipe, kind='tmp',
                                    KW_DPRTYPE=filetype)
        # append to filenames
        filenames += list(files)
    # convert to numpy array
    filenames = np.array(filenames)

    # deal with no files found
    if len(filenames) == 0:
        eargs = [params['INPATH']]
        WLOG(params, 'error', TextEntry('09-011-00005', args=eargs))

    # ----------------------------------------------------------------------
    # Get all dark file properties
    # ----------------------------------------------------------------------
    dark_table = dark.construct_dark_table(params, filenames)

    # ----------------------------------------------------------------------
    # match files by date and median to produce master dark
    # ----------------------------------------------------------------------
    cargs = [params, recipe, dark_table]
    master_dark, reffile = dark.construct_master_dark(*cargs)
    # get reference file night name
    nightname = drs_path.get_nightname(params, reffile.filename)
    # Have to update nightname while locked for all param dicts (do not copy)
    #     Note: do not use 'uparamdicts' unless you know what you are doing.
    ukwargs = dict(key='NIGHTNAME', value=nightname, source=mainname)
    constants.uparamdicts(params, recipe.drs_params, WLOG.pin, **ukwargs)

    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    qc_params, passed = dark.master_qc(params)
    # update recipe log
    recipe.log.add_qc(params, qc_params, passed)

    # ----------------------------------------------------------------------
    # Save master dark to file
    # ----------------------------------------------------------------------
    outfile = dark.write_master_files(params, recipe, reffile, master_dark,
                                      dark_table, qc_params)

    # ------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ------------------------------------------------------------------
    if passed:
        drs_database.add_file(params, outfile)

    # ------------------------------------------------------------------
    # Construct summary document
    # ------------------------------------------------------------------
    dark.master_summary(recipe, params, qc_params, dark_table)

    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    recipe.log.end(params)

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

@author: cook
"""
from __future__ import division
import numpy as np

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.core.instruments.spirou import file_definitions
from terrapipe.io import drs_fits
from terrapipe.io import drs_path
from terrapipe.science.calib import dark


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_dark_master_spirou.py'
__INSTRUMENT__ = 'SPIROU'
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
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# Define the output files
DARK_MASTER_FILE = file_definitions.out_dark_master


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
    Main function for cal_dark_spirou.py

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
    params = core.end_main(params, success)
    # return a copy of locally defined variables in the memory
    return core.get_locals(dict(locals()), llmain)


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
    params['FILETYPE'] = params['INPUTS']['FILETYPE']
    params.set_source('FILETYPE', mainname)

    # ----------------------------------------------------------------------
    # Get all preprocessed dark files
    # ----------------------------------------------------------------------
    # get all "filetype" filenames
    fargs = [params['FILETYPE'], params['ALLOWED_DARK_TYPES']]
    filenames = drs_fits.find_filetypes(params, *fargs)
    # convert to numpy array
    filenames = np.array(filenames)

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
    params['NIGHTNAME'] = drs_path.get_nightname(params, reffile.filename)
    params.set_source('NIGHTNAME', mainname)

    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # no quality control currently
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', TextEntry('40-005-10001'))
        params['QC'] = 1
        params.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
        params['QC'] = 0
        params.set_source('QC', __NAME__ + '/main()')
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # ----------------------------------------------------------------------
    # Save master dark to file
    # ----------------------------------------------------------------------
    # define outfile
    outfile = DARK_MASTER_FILE.newcopy(recipe=recipe)
    # construct the filename from file instance
    outfile.construct_filename(params, infile=reffile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    outfile.copy_original_keys(reffile)
    # add version
    outfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    outfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    outfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    outfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    outfile.add_hkey('KW_OUTPUT', value=outfile.name)
    # add qc parameters
    outfile.add_qckeys(qc_params)
    # ------------------------------------------------------------------
    # copy data
    outfile.data = master_dark
    # log that we are saving rotated image
    WLOG(params, '', TextEntry('40-011-10006', args=[outfile.filename]))
    # write data and header list to file
    outfile.write_multi(data_list=[dark_table])

    # ------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ------------------------------------------------------------------
    if params['QC']:
        drs_database.add_file(params, outfile)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    core.end(ll, has_plots=True)

# =============================================================================
# End of code
# =============================================================================

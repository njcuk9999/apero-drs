#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
from __future__ import division
import itertools

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.io import drs_fits
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
    # ----------------------------------------------------------------------
    # find all OBJ_DARK and OBJ_FP files
    filetypes = ['OBJ_FP', 'OBJ_DARK']
    intypes = ['EXT_E2DS', 'EXT_E2DS_FF']
    # ----------------------------------------------------------------------
    # get all combinations
    combinations = list(itertools.product(filetypes, intypes))
    # ----------------------------------------------------------------------
    # loop around files and update BERV
    for jt in range(len(combinations)):
        # ------------------------------------------------------------------
        # get this combination
        filetype, intype = combinations[jt]
        # ------------------------------------------------------------------
        # log progress
        WLOG(params, 'info', params['DRS_HEADER'])
        wargs = [filetype, intype]
        WLOG(params, 'info', 'FILETYPE = {0}   INTYPE = {1}'.format(*wargs))
        WLOG(params, 'info', params['DRS_HEADER'])
        # ------------------------------------------------------------------
        # Get filetype definition
        infiletype = core.get_file_definition(intype, params['INSTRUMENT'],
                                              kind='red')
        # ------------------------------------------------------------------
        # get files of this type
        filenames = drs_fits.find_files(params, kind='red', KW_OUTPUT=intype,
                                        KW_DPRTYPE=filetypes)
        # ------------------------------------------------------------------
        # loop around files
        for it, filename in enumerate(filenames):
            # print file currently processing
            wmsg = 'Processing file {1} of {2} \n\t File: {0}'
            wargs = [filename, it + 1, len(filenames)]
            WLOG(params, 'info', wmsg.format(*wargs))
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
            bprops = extract.get_berv(params, infile, header, props,
                                      warn=True, force=True)
            args = [infile.basename, bprops['USE_BERV']]
            # print that we have update the BERV measurement
            if bprops['USED_ESTIMATE']:
                wargs = ['PyASL', bprops['USE_BERV']]
            else:
                wargs = ['Barycorrpy', bprops['USE_BERV']]
            WLOG(params, '', '{0} BERV: {1}'.format(*wargs))
            # ----------------------------------------------------------
            # overwrite file
            # ----------------------------------------------------------
            # log progress
            WLOG(params, '', 'Writing to file: {0}'.format(infile.filename))
            # update header
            infile.copy_original_keys(infile, forbid_keys=False, allkeys=True)
            extract.add_berv_keys(params, infile, bprops)
            # write data to file
            infile.write()

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

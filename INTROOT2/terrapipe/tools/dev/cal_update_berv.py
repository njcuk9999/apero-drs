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
    fibers = ['AB', 'A', 'B', 'C']
    # ----------------------------------------------------------------------
    # get all combinations
    combinations = list(itertools.product(filetypes, intypes))
    # ----------------------------------------------------------------------
    # loop around files and update BERV
    for filetype in range(len(filetypes)):
        # ------------------------------------------------------------------
        # get this combination
        intype0 = intypes[0]
        fiber0 = fibers[0]
        # ------------------------------------------------------------------
        # log progress
        WLOG(params, 'info', params['DRS_HEADER'])
        wargs = [filetype, intype0]
        WLOG(params, 'info', 'FILETYPE = {0}   INTYPE = {1}'.format(*wargs))
        WLOG(params, 'info', params['DRS_HEADER'])
        # ------------------------------------------------------------------
        # get files of this type and the intypes
        filenames, infiletypes = dict(), dict()
        for intype in intypes:
            # get the in file type
            infiletype = core.get_file_definition(intype, params['INSTRUMENT'],
                                                  kind='red')
            # get the files for this filetype
            filenames1 = drs_fits.find_files(params, kind='red',
                                             KW_OUTPUT=intype,
                                             KW_DPRTYPE=filetype)
            # append to storage
            filenames[intype] = filenames1
            infiletypes[intype] = infiletype
        # ------------------------------------------------------------------
        # loop around files
        for it, filename in enumerate(filenames[intype0]):
            # print file currently processing
            wmsg = 'Processing file {1} of {2} \n\t File: {0}'
            wargs = [filename, it + 1, len(filenames)]
            WLOG(params, 'info', wmsg.format(*wargs))
            # ----------------------------------------------------------
            # skip if already using barycorppy
            skip = False
            infiles = dict()
            for intype in intypes:
                # get new copy of file definition
                infile1 = infiletypes[intype].newcopy(recipe=recipe)
                # set filename
                infile1.set_filename(filenames[intype])
                # read data
                infile1.read()
                # get header from file instance
                header1 = infile1.header
                # append to list
                infiles[intype] = infile1
                # ----------------------------------------------------------
                # skip if already using barycorppy
                if header1['BERVSRCE'] != 'barycorrpy':
                    skip = True
            if skip:
                continue
            # --------------------------------------------------------------
            # get the first infile
            infile = infiles[intypes[0]]
            # --------------------------------------------------------------
            # get header from file instance
            header = infile.header
            # --------------------------------------------------------------
            # Calculate Barycentric correction
            # --------------------------------------------------------------
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
            # --------------------------------------------------------------
            # overwrite file(s)
            # --------------------------------------------------------------
            for intype in intypes:
                # get infile from storage
                infile1 = infiles[intype]
                # get header from file instance
                header1 = infile1.header
                # ----------------------------------------------------------
                # skip if already using barycorppy
                if header1['BERVSRCE'] == 'barycorrpy':
                    continue
                # ----------------------------------------------------------
                # log progress
                wmsg = 'Writing to file: {0}'.format(infile1.filename)
                WLOG(params, '', wmsg)
                # update header
                infile1.copy_original_keys(infile1, forbid_keys=False,
                                          allkeys=True)
                extract.add_berv_keys(params, infile1, bprops)
                # write data to file
                # infile1.write()

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-05-13 at 11:04

@author: cook
"""
import numpy as np
import os

from apero.base import base
from apero import lang
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_text
from apero.core.utils import drs_startup
from apero.core.instruments.spirou import file_definitions as fd

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'out_postprocess_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry


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
    Main function for cal_badpix_spirou.py

    :param directory: string, the night name sub-directory
    :param flatfiles: list of strings or string, the list of flat files
    :param darkfiles: list of strings or string, the list of dark files
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
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
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
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # define main function name
    mainname = __NAME__ + '._main()'
    # ---------------------------------------------------------------------
    # get input parameters: clear
    clear = False
    if 'CLEAR' in params['INPUTS']:
        clear = params['INPUTS']['CLEAR']
    # get input parameters: overwrite
    overwrite = False
    if 'OVERWRITE' in params['INPUTS']:
        overwrite = params['INPUTS']['OVERWRITE']
    # get input parameters: night
    night = None
    if 'NIGHT' in params['INPUTS']:
        night = params['INPUTS']['NIGHT']
        if drs_text.null_text(night, ['None', '']):
            night = None
    # get input parameter: whitelist
    wnightlist = None
    if 'WNIGHTLIST' in params['INPUTS']:
        wnightlist = params['INPUTS']['WNIGHTLIST']
        if drs_text.null_text(wnightlist, ['None', '']):
            wnightlist = None
        else:
            wnightlist = wnightlist.replace(' ', '').split(',')
    # get input parameter: blacklist
    bnightlist = None
    if 'BNIGHTLIST' in params['INPUTS']:
        bnightlist = params['INPUTS']['BNIGHTLIST']
        if drs_text.null_text(bnightlist, ['None', '']):
            bnightlist = None
        else:
            bnightlist = bnightlist.replace(' ', '').split(',')
    # ---------------------------------------------------------------------
    # add master condition based on night, wnightlist and bnightlist
    # ---------------------------------------------------------------------
    # deal with night
    if night is not None:
        mastercondition = 'DIRNAME={0}'.format(night)
    # deal with white night list
    elif wnightlist is not None:
        # loop around all nights in wnightlist
        subcondition = []
        for wnight in wnightlist:
            subcondition.append('DIRNAME="{0}"'.format(wnight))
        # add to master condition
        mastercondition = '({0})'.format(' OR '.join(subcondition))
    # deal with black night list
    elif bnightlist is not None:
        # loop around all nights in bnightlist
        subcondition = []
        for bnight in bnightlist:
            subcondition.append('DIRNAME!="{0}"'.format(bnight))
        # add to master condition
        mastercondition = '({0})'.format(' AND '.join(subcondition))
    else:
        mastercondition = None

    # ---------------------------------------------------------------------
    # load the index database
    indexdbm = drs_database.IndexDatabase(params)
    indexdbm.load_db()
    # get the list of post files
    post_files = fd.post_file.fileset
    # loop around post files
    for post_file in post_files:
        # ---------------------------------------------------------------------
        # make a copy of post_file that we can then fill
        postfile = post_file.copy()
        # ---------------------------------------------------------------------
        # add params to post_file
        postfile.params = params
        # get the output filename function
        outfunc = postfile.outfunc
        # ---------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'POST_FILE', postfile.name)
        # ---------------------------------------------------------------------
        # find files for extension 0
        table0 = postfile.find_files(0, indexdbm, mastercondition)
        # get number of files
        num_files = len(table0['ABSPATH'])
        # ---------------------------------------------------------------------
        # loop around all files in ext 0
        for row in range(num_files):
            # -----------------------------------------------------------------
            # generate out file name
            outfile, outdir = outfunc(params, postfile,
                                      table0['KW_IDENTIFIER'][row],
                                      table0['DIRNAME'][row])
            # skip existing files
            if (not overwrite) and os.path.exists(outfile):
                continue
            # -----------------------------------------------------------------
            # log process
            imsg = 'Processing {0} output file {1} of {2}: {3}'
            iargs = [post_file.name, row + 1, num_files, outfile]
            WLOG(params, 'info', params['DRS_HEADER'])
            WLOG(params, 'info', imsg.format(*iargs))
            WLOG(params, 'info', params['DRS_HEADER'])
            # -----------------------------------------------------------------
            # make a new copy of out file
            filepostfile = postfile.copy()
            # add params to filepostfile
            filepostfile.params = params
            # add output filename
            filepostfile.out_filename = outfile
            filepostfile.out_dirname = outdir
            # add extension 0 file properties
            filepostfile.extensions[0].set_infile(row, table0)
            # load the extension 0 file
            filepostfile.extensions[0].load_infile(params)
            # -----------------------------------------------------------------
            # link all other extensions
            success = filepostfile.process_links(params, indexdbm,
                                                 filepostfile.out_required)
            # deal with writing file
            if success:
                # deal with processing headers
                filepostfile.process_header(params)
                # update filename/basename and path
                filepostfile.set_filename(filepostfile.out_filename)
                # write file
                msg = 'Writing to file: {0}'
                margs = [filepostfile.filename]
                WLOG(params, '', msg.format(*margs))
                filepostfile.write_file(recipe.outputtype, recipe.runstring)
            else:
                WLOG(params, 'warning', '\tSkipping - files not found')

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

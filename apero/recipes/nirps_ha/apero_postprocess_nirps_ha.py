#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_postprocess_spirou.py [obs_dir] [files]

APERO post processing recipe for SPIROU

Created on 2019-05-13 at 11:04

@author: cook
"""
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.instruments.nirps_ha import file_definitions as fd
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_postprocess_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict
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
def main(obs_dir: Optional[str] = None, files: Optional[List[str]] = None,
         **kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_badpix_spirou.py

    :param obs_dir: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type obs_dir: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(obs_dir=obs_dir, files=files, **kwargs)
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


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # define main function name
    mainname = __NAME__ + '._main()'
    # get files
    infile = params['INPUTS']['FILES'][1][0]
    # get whether we are skipping files that exist on disk
    skip = params['INPUTS']['SKIP']
    # get whether we are to clean the reduced inputs
    clear = params['INPUTS']['CLEAR']
    # ---------------------------------------------------------------------
    # load the databases
    findexdbm = drs_database.FileIndexDatabase(params)
    findexdbm.load_db()
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    telludbm = drs_database.TelluricDatabase(params)
    telludbm.load_db()
    # ---------------------------------------------------------------------
    # get directory name
    obs_dir = params['OBS_DIR']
    # get identifier
    identifier = infile.get_hkey('KW_IDENTIFIER')
    # get the list of post files
    post_files = fd.post_file.fileset
    # has skipped
    has_skipped = False
    # storage of possible errors
    error_storage = []
    # loop around post files
    for post_file in post_files:
        # ---------------------------------------------------------------------
        # make a copy of post_file that we can then fill
        postfile = post_file.copy()
        # ---------------------------------------------------------------------
        # add params to post_file
        postfile.params = params
        # get the output filename function
        outclass = postfile.outclass
        # -----------------------------------------------------------------
        # generate out file name
        outfile, outdir = outclass.construct(params, postfile, identifier,
                                             obs_dir)
        # skip existing files
        if skip and os.path.exists(outfile):
            continue
        # -----------------------------------------------------------------
        # log process: Processing {0}'
        iargs = [post_file.name]
        WLOG(params, 'info', params['DRS_HEADER'])
        WLOG(params, 'info', textentry('40-090-00001', args=iargs))
        WLOG(params, 'info', params['DRS_HEADER'])
        # -----------------------------------------------------------------
        # make a new copy of out file
        filepostfile = postfile.copy()
        # add params to filepostfile
        filepostfile.params = params
        # add output filename
        filepostfile.out_filename = outfile
        filepostfile.out_dirname = outdir
        filepostfile.obs_dir = obs_dir
        # add extension 0 file properties
        filepostfile.extensions[0].set_infile(params, filename=infile.filename)
        # load the extension 0 file
        filepostfile.extensions[0].load_infile(params)
        # check if we should skip due to exclude header keys
        if filepostfile.check_header_skip(ext=0):
            continue
        # -----------------------------------------------------------------
        # link all other extensions
        success, reason = filepostfile.process_links(params, findexdbm,
                                                     calibdbm, telludbm,
                                                     filepostfile.out_required)
        # deal with writing file
        if success:
            # deal with processing headers
            filepostfile.process_header(params)
            # deal with database infiles
            filepostfile.set_db_infiles(block_kind=recipe.out_block_str,
                                        database=findexdbm)
            # update filename/basename and path
            filepostfile.set_filename(filepostfile.out_filename)
            # write file
            # log progress: Writing to file: {0}'
            margs = [filepostfile.filename]
            WLOG(params, '', textentry('40-090-00002', args=margs))
            filepostfile.write_file(block_kind=recipe.out_block_str,
                                    runstring=recipe.runstring)
            recipe.add_output_file(filepostfile)
            # if user wants to clear - clear this data
            if clear:
                for filename in filepostfile.clear_files:
                    # log progress: Removing {0}'
                    wargs = [filename]
                    WLOG(params, 'warning',
                         textentry('10-090-00001', args=wargs), sublevel=2)
                    os.remove(filename)
        else:
            # print reason as a warning
            WLOG(params, 'warning', reason, sublevel=2)
            # flag we have skipped some files
            has_skipped = True
            # log reason
            if reason is not None and filepostfile.out_required:
                error_storage.append(reason)
    # -------------------------------------------------------------------------
    # add the QC (there are none)
    qc_names, qc_values = ['None'], ['None']
    qc_logic, qc_pass = ['None'], ['None']
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    recipe.log.add_qc(qc_params, True)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # deal with printing errors
    if has_skipped:
        if len(error_storage) > 0:
            # header banner (in red)
            WLOG(params, '', params['DRS_HEADER'], colour='red')
            # combine error messages
            errormsg = ''
            # loop around error reports (from error_storage)
            for e_it, error_entry in enumerate(error_storage):
                # add the error itself
                # errormsg += error_entry
                # print error
                WLOG(params, 'error', error_entry, raise_exception=False)
                # header banner (in red)
                WLOG(params, '', params['DRS_HEADER'], colour='red')
            # report on combined number of errors (and crash)
            eargs = [len(error_storage), recipe.name]
            WLOG(params, 'error', textentry('00-090-00010', args=eargs))
    # else report that no errors were found
    else:
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', textentry('40-090-00009'))
    # -------------------------------------------------------------------------
    # end the log (only successful if no skips)
    if not has_skipped:
        recipe.log.end()

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

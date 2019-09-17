#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-09-16 at 13:22

@author: cook
"""
from __future__ import division
import os

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.io import drs_fits
from terrapipe.io import drs_path
from terrapipe.science import telluric
from terrapipe.tools.module.setup import drs_reprocess

from terrapipe.core.instruments.spirou import recipe_definitions as rd

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_mk_tellu_db_spirou.py'
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
# get recipes
obj_mk_tellu = rd.obj_mk_tellu
obj_fit_tellu = rd.obj_fit_tellu
obj_mk_template = rd.obj_mk_template


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(cores=None, filetype=None, **kwargs):
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
    fkwargs = dict(cores=cores, filetype=filetype, **kwargs)
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
    # get the filetype (this is overwritten from user inputs if defined)
    filetype = params['INPUTS']['FILETYPE']
    # get the fiber type required
    fiber = params['INPUTS']['FIBER']
    # set properties set in run file
    params.set('STOP_AT_EXCEPTION', False)
    params.set('DEBUG', False)
    params.set('CORES', params['INPUTS']['CORES'])
    # get the telluric star names
    objnames, _ = telluric.get_whitelist(params)
    objnames = list(objnames)
    # ----------------------------------------------------------------------
    # get objects that match this object name
    tellu_stars = drs_fits.find_files(params, kind='red', fiber=fiber,
                                      KW_OBJNAME=objnames, KW_OUTPUT=filetype)
    # ----------------------------------------------------------------------
    # get night names for each object
    night_names, tellu_basenames = [], []
    for filename in tellu_stars:
        # append night names
        night_names.append(drs_path.get_nightname(params, filename))
        # append base names
        tellu_basenames.append(os.path.basename(filename))

    # -------------------------------------------------------------------------
    # Step 1: Run mk_tellu on all telluric stars
    # -------------------------------------------------------------------------
    # arguments are: directory and telluric files
    gargs = [night_names, tellu_basenames]
    gkwargs = dict()
    gkwargs['--program'] = 'DBMKTELLU1'
    # generate run table (dictionary from reprocessing)
    runtable = drs_reprocess.generate_run_table(params, obj_mk_tellu, *gargs,
                                                **gkwargs)
    # Generate run list
    runlist = drs_reprocess.generate_run_list(params, None, runtable)
    # Process run list
    outlist, has_errors = drs_reprocess.process_run_list(params, runlist)
    # display errors
    if has_errors:
        drs_reprocess.display_errors(params, outlist)
        # terminate here
        eargs = [obj_mk_tellu.name, recipe.name]
        WLOG(params, 'error', TextEntry('00-019-00001', args=eargs))

    # -------------------------------------------------------------------------
    # Step 2: Run fit tellu on all telluric stars
    # -------------------------------------------------------------------------
    # arguments are: directory and telluric files
    gargs = [night_names, tellu_basenames]
    gkwargs = dict()
    gkwargs['--program'] = 'DBFTELLU'
    # generate run table (dictionary from reprocessing)
    runtable = drs_reprocess.generate_run_table(params, obj_fit_tellu, *gargs,
                                                **gkwargs)
    # Generate run list
    runlist = drs_reprocess.generate_run_list(params, None, runtable)
    # Process run list
    outlist, has_errors = drs_reprocess.process_run_list(params, runlist)
    # display errors
    if has_errors:
        drs_reprocess.display_errors(params, outlist)
        # terminate here
        eargs = [obj_fit_tellu.name, recipe.name]
        WLOG(params, 'error', TextEntry('00-019-00001', args=eargs))

    # -------------------------------------------------------------------------
    # step 3: Run mk_obj_template on each telluric star obj name
    # -------------------------------------------------------------------------
    # arguments are: object names
    gargs = [objnames]
    gkwargs = dict()
    gkwargs['--program'] = 'DBMKTEMP'
    # generate run table (dictionary from reprocessing)
    runtable = drs_reprocess.generate_run_table(params, obj_mk_template, *gargs,
                                                **gkwargs)
    # Generate run list
    runlist = drs_reprocess.generate_run_list(params, None, runtable)
    # Process run list
    outlist, has_errors = drs_reprocess.process_run_list(params, runlist)
    # display errors
    if has_errors:
        drs_reprocess.display_errors(params, outlist)
        # terminate here
        eargs = [obj_mk_template.name, recipe.name]
        WLOG(params, 'error', TextEntry('00-019-00001', args=eargs))

    # -------------------------------------------------------------------------
    # step 4: Run mk_tellu on all telluric stars
    # -------------------------------------------------------------------------
    # arguments are: directory and telluric files
    gargs = [night_names, tellu_basenames]
    gkwargs = dict()
    gkwargs['--program'] = 'DBMKTELLU2'
    # generate run table (dictionary from reprocessing)
    runtable = drs_reprocess.generate_run_table(params, obj_mk_tellu, *gargs,
                                                **gkwargs)
    # Generate run list
    runlist = drs_reprocess.generate_run_list(params, None, runtable)
    # Process run list
    outlist, has_errors = drs_reprocess.process_run_list(params, runlist)
    # display errors
    if has_errors:
        drs_reprocess.display_errors(params, outlist)
        # terminate here
        eargs = [obj_mk_tellu.name, recipe.name]
        WLOG(params, 'error', TextEntry('00-019-00001', args=eargs))

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
    # Post main plot clean up
    core.post_main(ll['params'], has_plots=True)

# =============================================================================
# End of code
# =============================================================================

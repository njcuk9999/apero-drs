#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-25 at 16:44

@author: cook
"""
import os
from collections import OrderedDict

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.io import drs_path
from apero.io import drs_image
from apero.tools.module.processing import drs_processing
from apero.core.instruments.spirou import recipe_definitions as rd


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_spec_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# get recipes
CAL_EXTRACT = rd.cal_extract
MK_TELLU = rd.obj_mk_tellu
FIT_TELLU = rd.obj_fit_tellu
MK_TEMPLATE = rd.obj_mk_template
# get filetypes
E2DSFF = rd.sf.out_ext_e2dsff


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, files=None, **kwargs):
    """
    Main function for obj_spec_spirou.py

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
    fkwargs = dict(directory=directory, files=files, **kwargs)
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
    # TODO: Finish code
    WLOG(params, 'error', 'Code not working. Do not use')

    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get parameters from inputs
    drs_plot = params['DRS_PLOT']
    # get files
    ppfiles = params['INPUTS']['FILES'][1]
    # set properties set in run file
    params.set('STOP_AT_EXCEPTION', True)
    params.set('TEST_RUN', False)
    params.set('CORES', params['INPUTS']['CORES'])

    # ----------------------------------------------------------------------
    # get night names for each object
    night_names, pp_basenames = [], []

    # loop around pp files
    for ppfile in ppfiles:
        # append night names
        night_names.append(drs_path.get_nightname(params, ppfile.filename))
        # append base names
        pp_basenames.append(ppfile.basename)

    # -------------------------------------------------------------------------
    # setup global outlist
    # -------------------------------------------------------------------------
    goutlist = OrderedDict()

    # ----------------------------------------------------------------------
    # Extraction
    # ----------------------------------------------------------------------
    # arguments are: directory and telluric files
    gargs = [night_names, pp_basenames]
    gkwargs = dict()
    gkwargs['--plot'] = drs_plot
    gkwargs['--program'] = 'EXTRACT'
    # run extraction
    outlist = drs_processing.run_process(params, recipe, CAL_EXTRACT,
                                         *gargs, **gkwargs)
    # add to global list
    goutlist = drs_processing.combine_outlist('EXTRACT', goutlist, outlist)
    # ----------------------------------------------------------------------
    # get the fiber types from a list parameter
    fiber_types = drs_image.get_fiber_types(params)
    # storage for e2ds files
    e2dsff_files = dict()
    # loop around pp files
    for ppfile in ppfiles:
        # make e2ds files
        for fiber in fiber_types:
            # get copy file instance
            e2ds_file = E2DSFF.newcopy(params=params, fiber=fiber)
            # construct the filename from file instance
            e2ds_file.construct_filename(infile=ppfile)
            # check whether e2ds file exists
            if os.path.exists(e2ds_file.filename):
                # add to storage (for existing fiber)
                if fiber in e2dsff_files:
                    e2dsff_files[fiber].append(e2ds_file)
                # add to storage (for new fiber)
                else:
                    e2dsff_files[fiber] = [e2ds_file]

    # ----------------------------------------------------------------------
    # Fit Tellurics
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Make template
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Fit Tellurics
    # ----------------------------------------------------------------------

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

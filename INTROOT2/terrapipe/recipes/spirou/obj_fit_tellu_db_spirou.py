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
from collections import OrderedDict

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.io import drs_path
from terrapipe.science import telluric
from terrapipe.tools.module.setup import drs_processing

from terrapipe.core.instruments.spirou import recipe_definitions as rd

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_fit_tellu_db_spirou.py'
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
    # get the index file col name
    filecol = params['DRS_INDEX_FILENAME']
    # get the required dprtypes
    dprtypes = params['INPUTS']['DPRTYPE']
    # get the required object names
    robjnames = params['INPUTS']['OBJNAME']
    if robjnames == 'None':
        robjnames = None
    # set properties set in run file
    params.set('STOP_AT_EXCEPTION', False)
    params.set('TEST_RUN', False)
    params.set('CORES', params['INPUTS']['CORES'])
    # ----------------------------------------------------------------------
    # get objects that match this object name
    gargs = [fiber, filetype, dprtypes, robjnames]
    obj_stars, obj_names = telluric.get_non_tellu_objs(params, *gargs)
    # ----------------------------------------------------------------------
    # get night names for each object
    night_names, obj_basenames = [], []
    # loop around objects
    for filename in obj_stars:
        # append night names
        night_names.append(drs_path.get_nightname(params, filename))
        # append base names
        obj_basenames.append(os.path.basename(filename))

    # -------------------------------------------------------------------------
    # setup global outlist
    # -------------------------------------------------------------------------
    goutlist = OrderedDict()

    # -------------------------------------------------------------------------
    # Step 1: Run fit tellu on obj_stars
    # -------------------------------------------------------------------------
    # arguments are: directory and telluric files
    gargs = [night_names, obj_basenames]
    gkwargs = dict()
    gkwargs['--program'] = 'DBFTELLU'
    gkwargs['terminate'] = False
    # run obj_fit_tellu
    outlist = drs_processing.run_process(params, recipe, obj_fit_tellu,
                                         *gargs, **gkwargs)
    # add to global list
    goutlist = drs_processing.combine_outlist('DBFTELLU', goutlist, outlist)

    # -------------------------------------------------------------------------
    # step 2: Run mk_obj_template on obj_stars
    # -------------------------------------------------------------------------
    # arguments are: object names
    gargs = [obj_names]
    gkwargs = dict()
    gkwargs['--program'] = 'DBMKTEMP'
    gkwargs['terminate'] = False
    # run obj_fit_tellu
    outlist = drs_processing.run_process(params, recipe, obj_mk_template,
                                         *gargs, **gkwargs)
    # add to global list
    goutlist = drs_processing.combine_outlist('DBMKTEMP', goutlist, outlist)

    # -------------------------------------------------------------------------
    # step 3: Run fit tellu on obj_stars
    # -------------------------------------------------------------------------
    # arguments are: directory and telluric files
    gargs = [night_names, obj_basenames]
    gkwargs = dict()
    gkwargs['--program'] = 'DBFTELLU'
    gkwargs['terminate'] = False
    # run obj_fit_tellu
    outlist = drs_processing.run_process(params, recipe, obj_fit_tellu,
                                         *gargs, **gkwargs)
    # add to global list
    goutlist = drs_processing.combine_outlist('DBFTELLU', goutlist, outlist)

    # -------------------------------------------------------------------------
    # Display Errors
    # -------------------------------------------------------------------------
    drs_processing.display_errors(params, goutlist)

    # -------------------------------------------------------------------------
    # End of main code
    # -------------------------------------------------------------------------
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

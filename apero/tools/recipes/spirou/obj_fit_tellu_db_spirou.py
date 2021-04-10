#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-09-16 at 13:22

@author: cook
"""
import os
from collections import OrderedDict

from apero.base import base
from apero.core.core import drs_text
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.utils import drs_startup
from apero.core.core import drs_file
from apero.science import telluric
from apero.tools.module.processing import drs_processing
from apero.core.instruments.spirou import recipe_definitions as rd

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_fit_tellu_db_spirou.py'
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
    Main function for obj_fit_tellu_db_spirou.py

    :param cores: int, the number of cores to use
    :param filetype: str, the allowed DPRTYPE
    :param kwargs: additional keyword arguments

    :type cores: int
    :type filetype: str
    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(cores=cores, filetype=filetype, **kwargs)
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
    params.set('CORES', params['INPUTS']['CORES'])
    # set test run from inputs
    params.set('TEST_RUN', False)
    if 'TEST' in params['INPUTS']:
        if drs_text.true_text(params['INPUTS']['TEST']):
            params.set('TEST_RUN', True)
    # ----------------------------------------------------------------------
    # load index database
    indexdbm = drs_database.IndexDatabase(params)
    indexdbm.load_db()
    # ----------------------------------------------------------------------
    # get objects that match this object name
    gargs = [fiber, filetype, dprtypes, robjnames]
    obj_stars, obj_names = telluric.get_non_tellu_objs(params, recipe, *gargs,
                                                       indexdbm=indexdbm)
    # ----------------------------------------------------------------------
    # get night names for each object
    obs_dirs, obj_basenames = [], []
    # loop around objects
    for filename in obj_stars:
        # get the path inst
        path_inst = drs_file.DrsPath(params, abspath=filename)
        # append night names
        obs_dirs.append(path_inst.obs_dir)
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
    gargs = [obs_dirs, obj_basenames]
    gkwargs = dict()
    gkwargs['--program'] = 'DBFTELLU'
    gkwargs['terminate'] = False
    # run obj_fit_tellu
    outlist = drs_processing.run_process(params, recipe, indexdbm,
                                         obj_fit_tellu, *gargs, **gkwargs)
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
    outlist = drs_processing.run_process(params, recipe, indexdbm,
                                         obj_mk_template, *gargs, **gkwargs)
    # add to global list
    goutlist = drs_processing.combine_outlist('DBMKTEMP', goutlist, outlist)

    # -------------------------------------------------------------------------
    # step 3: Run fit tellu on obj_stars
    # -------------------------------------------------------------------------
    # arguments are: directory and telluric files
    gargs = [obs_dirs, obj_basenames]
    gkwargs = dict()
    gkwargs['--program'] = 'DBFTELLU'
    gkwargs['terminate'] = False
    # run obj_fit_tellu
    outlist = drs_processing.run_process(params, recipe, indexdbm,
                                         obj_fit_tellu, *gargs, **gkwargs)
    # add to global list
    goutlist = drs_processing.combine_outlist('DBFTELLU', goutlist, outlist)

    # -------------------------------------------------------------------------
    # Display Errors
    # -------------------------------------------------------------------------
    drs_processing.display_errors(params, goutlist)

    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    # no quality control --> so set passed qc to True
    recipe.log.no_qc()
    # update log
    recipe.log.end()

    # -------------------------------------------------------------------------
    # End of main code
    # -------------------------------------------------------------------------
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_mk_model [night_directory] [files]

Takes the transmissions made in apero_mk_tellu and saves them as three
arrays that have the same shape as an e2ds (zero_residual, a dc offset of
residuals, a linear dependency with water absorption and a linear dependency
with dry absorption

Usage:
  apero_mk_model

Outputs:
trans-model

Created on 2019-09-03 at 14:58

@author: cook
"""
import numpy as np

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.core import drs_database
from apero.science.calib import wave
from apero.science import extract
from apero.science import telluric

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_mk_model_spirou.py'
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
    Main function for apero_mk_tellu_spirou.py

    :param kwargs: any additional keywords

    :type obs_dir: str
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
    mainname = __NAME__ + '._main()'
    # get psuedo constants
    pconst = constants.pload()
    # get fiber from parameters
    if 'FIBER' in params['INPUTS']:
        fiber = params['INPUTS']['FIBER']
    else:
        fiber = params['TELLURIC_FIBER_TYPE']
    # load the telluric database
    telludbm = drs_database.TelluricDatabase(params)
    telludbm.load_db()
    # set up plotting (no plotting before this) -- must be after setting
    #   night name
    recipe.plot.set_location(0)

    # ------------------------------------------------------------------
    # Load transmission files and header vectors
    # ------------------------------------------------------------------
    # load trans filenames
    transfiles = telluric.get_trans_files(params, None, fiber,
                                          database=telludbm)
    # get cube and header vectors
    transcube, transtable = telluric.make_trans_cube(params, transfiles)

    # ------------------------------------------------------------------
    # Calculate the model
    # ------------------------------------------------------------------
    # create trans model parameter dictionary (with e2ds shaped out vectors)
    tprops = telluric.make_trans_model(params, transcube, transtable)

    # ----------------------------------------------------------------------
    # print/log quality control (all assigned previously)
    # ----------------------------------------------------------------------
    qc_params, passed = telluric.mk_model_qc(params)
    # update recipe log
    recipe.log.add_qc(qc_params, passed)

    # ------------------------------------------------------------------
    # Plot and save
    # ------------------------------------------------------------------
    # plot model (debug)
    recipe.plot('MKTELLU_MODEL', tprops=tprops)
    # plot model (summary)
    recipe.plot('SUM_MKTELLU_MODEL', tprops=tprops)
    # save model
    model_file = telluric.mk_write_model(params, recipe, tprops, transtable,
                                         fiber, qc_params)
    # add to telluric database
    if passed:
        # copy the big cube median to the calibDB
        telludbm.add_tellu_file(model_file)

    # ----------------------------------------------------------------------
    # Construct summary document
    # ----------------------------------------------------------------------
    telluric.mk_model_summary(recipe, params, qc_params, tprops)

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

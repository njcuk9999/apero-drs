#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from apero.base import base
from apero import lang
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.setup import drs_reset


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_reset.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict


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
    Main function for apero_reset.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

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
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


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
    # get log and warn from inputs
    log = params['INPUTS']['log']
    warn = params['INPUTS']['warn']

    # ----------------------------------------------------------------------
    # Perform resets
    # ----------------------------------------------------------------------
    reset0 = True
    reset1, reset2, reset3 = True, True, True
    reset4, reset5, reset6 = True, True, True
    reset7, reset8 = True, True
    # ----------------------------------------------------------------------
    # assets folder
    if warn:
        reset0 = drs_reset.reset_confirmation(params, 'Assets',
                                              params['DRS_DATA_ASSETS'])
    if reset0:
        drs_reset.reset_assets(params)
    else:
        WLOG(params, '', 'Not resetting assets.')
    # ----------------------------------------------------------------------
    # tmp folder
    if warn:
        reset1 = drs_reset.reset_confirmation(params, 'Working',
                                              params['DRS_DATA_WORKING'])
    if reset1:
        drs_reset.reset_tmp_folders(params, log)
    else:
        WLOG(params, '', 'Not resetting tmp folders.')
    # ----------------------------------------------------------------------
    # reduced folder
    if warn:
        reset2 = drs_reset.reset_confirmation(params, 'Reduced',
                                              params['DRS_DATA_REDUC'])
    if reset2:
        drs_reset.reset_reduced_folders(params, log)
    else:
        WLOG(params, '', 'Not resetting reduced folders.')
    # ----------------------------------------------------------------------
    # calibration folder
    if warn:
        reset3 = drs_reset.reset_confirmation(params, 'Calibration',
                                              params['DRS_CALIB_DB'])
    if reset3:
        drs_reset.reset_calibdb(params, log)
    else:
        WLOG(params, '', 'Not resetting CalibDB files.')
    # ----------------------------------------------------------------------
    # telluric folder
    if warn:
        reset4 = drs_reset.reset_confirmation(params, 'Telluric',
                                              params['DRS_TELLU_DB'])
    if reset4:
        drs_reset.reset_telludb(params, log)
    else:
        WLOG(params, '', 'Not resetting TelluDB files.')
    # ----------------------------------------------------------------------
    # log folder
    if warn:
        reset5 = drs_reset.reset_confirmation(params, 'Log',
                                              params['DRS_DATA_MSG'])
    if reset5:
        drs_reset.reset_log(params)
    # ----------------------------------------------------------------------
    # plot folder
    if warn:
        reset6 = drs_reset.reset_confirmation(params, 'Plotting',
                                              params['DRS_DATA_PLOT'])
    if reset6:
        drs_reset.reset_plot(params)
    else:
        WLOG(params, '', 'Not resetting Log files.')
    # ----------------------------------------------------------------------
    # plot folder
    if warn:
        reset7 = drs_reset.reset_confirmation(params, 'Run',
                                              params['DRS_DATA_RUN'])
    if reset7:
        drs_reset.reset_run(params)
    else:
        WLOG(params, '', 'Not resetting run files.')

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

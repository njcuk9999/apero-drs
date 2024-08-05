#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from apero.base import base
from apero.core import lang
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
    Main function for apero_reset.py

    :param kwargs: additional keyword arguments

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
    log = not params['INPUTS']['nolog']
    warn = not params['INPUTS']['nowarn']
    database_timeout = params['INPUTS']['DATABASE_TIMEOUT']
    # ----------------------------------------------------------------------
    # Must check that we are not inside an apero directory
    drs_reset.check_cwd(params)
    # ----------------------------------------------------------------------
    # setup resets
    # ----------------------------------------------------------------------
    # set up the different types of reset
    names = ['assets', 'tmp', 'red', 'calib', 'tellu', 'log',
             'plot', 'run', 'lbl', 'out', 'other']
    # set up True criteria
    # set up default resets
    resets = list(names)
    # set up default warnings
    if warn:
        warns = list(names)
    else:
        warns = []
    # ----------------------------------------------------------------------
    # deal with --only options
    for name in names:
        if params['INPUTS'][f'only_{name}']:
            resets = [name]
            if warn:
                warns = [name]
    # ----------------------------------------------------------------------
    # Perform resets
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Assets')
    reset = True
    reset_dbs = True
    # assets folder
    if 'assets' in warns:
        reset = drs_reset.reset_confirmation(params, 'Assets',
                                             params['DRS_DATA_ASSETS'])
    # all databases (can be within assets dir this is why we ask here)
    if 'assets' in warns and 'assets' in resets and reset:
        reset_dbs = drs_reset.reset_confirmation(params, 'All databases')

    if 'assets' in resets and reset:
        drs_reset.reset_assets(params, reset_dbs=reset_dbs)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Assets']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'tmp')
    reset = True
    # tmp folder
    if 'tmp' in warns:
        reset = drs_reset.reset_confirmation(params, 'Working',
                                             params['DRS_DATA_WORKING'])
    if 'tmp' in resets and reset:
        drs_reset.reset_tmp_folders(params, log)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Tmp']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Reduced')
    reset = True
    # reduced folder
    if 'red' in warns:
        reset = drs_reset.reset_confirmation(params, 'Reduced',
                                             params['DRS_DATA_REDUC'])
    if 'red' in resets and reset:
        drs_reset.reset_reduced_folders(params, log)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Reduced']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Calibration')
    reset = True
    # calibration folder
    if 'calib' in warns:
        reset = drs_reset.reset_confirmation(params, 'Calibration',
                                             params['DRS_CALIB_DB'])
    if 'calib' in resets and reset:
        drs_reset.reset_calibdb(params, log)
    else:
        WLOG(params, '', '\tNot resetting CalibDB files.')
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Telluric')
    reset = True
    # telluric folder
    if 'tellu' in warns:
        reset = drs_reset.reset_confirmation(params, 'Telluric',
                                             params['DRS_TELLU_DB'])
    if 'tellu' in resets and reset:
        drs_reset.reset_telludb(params, log)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Telluric']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Log')
    reset = True
    # deal with files to skip
    exclude_files = [drs_log.get_logfilepath(WLOG, params)]
    # log folder
    if 'log' in warns:
        reset = drs_reset.reset_confirmation(params, 'Log',
                                             params['DRS_DATA_MSG'],
                                             exclude_files=exclude_files)
    if 'log' in resets and reset:
        drs_reset.reset_log(params, exclude_files)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Log']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Plot')
    reset = True
    # plot folder
    if 'plot' in warns:
        reset = drs_reset.reset_confirmation(params, 'Plotting',
                                             params['DRS_DATA_PLOT'])
    if 'plot' in resets and reset:
        drs_reset.reset_plot(params)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Plot']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Run')
    reset = True
    # plot folder
    if 'run' in warns:
        reset = drs_reset.reset_confirmation(params, 'Run',
                                             params['DRS_DATA_RUN'])
    if 'run' in resets and reset:
        drs_reset.reset_run(params)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Run']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'LBL')
    reset = True
    # plot folder
    if 'lbl' in warns:
        reset = drs_reset.reset_confirmation(params, 'LBL',
                                             params['LBL_PATH'])
    if 'lbl' in resets and reset:
        drs_reset.reset_lbl_folders(params, log)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['LBL']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Out')
    reset = True
    # plot folder
    if 'out' in warns:
        reset = drs_reset.reset_confirmation(params, 'Out',
                                             params['DRS_DATA_OUT'])
    if 'out' in resets and reset:
        drs_reset.reset_out_folders(params, log)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Out']))
    # ----------------------------------------------------------------------
    # progress
    drs_reset.reset_title(params, 'Other')
    reset = True
    if 'other' in warns:
        reset = drs_reset.reset_confirmation(params, 'Other',
                                             params['DRS_DATA_OTHER'])
    if 'other' in resets and reset:
        drs_reset.reset_other_folder(params, log)
    else:
        WLOG(params, '', textentry('40-502-00013', args=['Other']))
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

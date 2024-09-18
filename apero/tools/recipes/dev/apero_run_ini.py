#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
from apero.core import lang
from apero.base import base
from apero.core.constants import constant_functions
from apero.core.core import drs_log
from apero.core.base import drs_text
from apero.core.utils import drs_startup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_run_ini.py'
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
# --------------------------------------------------------------------------
# define run.ini file definition path
RUNDEF_PATH = 'apero.tools.module.processing.instruments.runfiles_{0}'


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_changelog.py

    :param kwargs: any additional keywords

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
    # get instrument variable
    instruments = list(base.INSTRUMENTS)
    if 'INSTRUMENT' in params['INPUTS']:
        if not drs_text.null_text(params['INPUTS']['INSTRUMENT'], ['None', '']):
            instruments = params['INPUTS']['INSTRUMENT'].split(',')
    # -------------------------------------------------------------------------
    # log progress
    WLOG(params, 'info', 'Generating list of default run.ini files')
    # get default run file instances
    run_files = []
    for instrument in instruments:
        if instruments == 'None':
            continue
        modname = f'runfile_{instrument.lower()}'
        modpath = RUNDEF_PATH.format(instrument.lower())
        # try to load run def
        # noinspection PyBroadException
        try:
            rundef = constant_functions.import_module(modname, modpath,
                                                      quiet=True)
        except Exception as _:
            wmsg = 'Cannot load: {0} skipping'
            wargs = [modname]
            WLOG(params, 'warning', wmsg.format(*wargs))
            continue
        run_files += rundef.get().get_runfiles(params)
    # -------------------------------------------------------------------------
    # print how many found
    WLOG(params, '', '\tFound {0} run file templates'.format(len(run_files)))
    # loop around run files
    for it, run_file in enumerate(run_files):
        # skip invalid instruments
        if run_file.instrument not in instruments:
            continue
        # progress report
        msg = 'Processing file {0} of {1}: {2} [{3}]'
        margs = [it + 1, len(run_files), run_file.name, run_file.instrument]
        WLOG(params, 'info', msg.format(*margs))
        # # populate the text file
        # run_file.populate_text_file(params)
        # # print message
        # msg = '\tWriting file: {0}'
        # margs = [run_file.outpath]
        # WLOG(params, '', msg.format(*margs))
        # # write to file
        # run_file.write_text_file()
        # write to yaml file
        run_file.write_yaml_file(params)

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

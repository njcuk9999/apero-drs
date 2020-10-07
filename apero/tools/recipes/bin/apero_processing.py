#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:47

@author: cook
"""
import sys

from apero.base import base
from apero import lang
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_database
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
from apero.tools.module.processing import drs_processing


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_processing.py'
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
def main(instrument=None, runfile=None, **kwargs):
    """
    Main function for apero_explorer.py

    :param instrument: str, the instrument name
    :param runfile: str, the run file to run (see the /run/ folder)
    :param kwargs: additional keyword arguments

    :type instrument: str
    :type runfile: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(instrument=instrument, runfile=runfile, **kwargs)
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
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None',
                                keys=['outlist'])


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
    # get run file from inputs
    runfile = params['INPUTS']['RUNFILE']
    # set up drs group (for logging)
    groupname = drs_startup.group_name(params)

    # ----------------------------------------------------------------------
    # Deal with run file
    # ----------------------------------------------------------------------
    # deal with run file
    params, runtable = drs_processing.read_runfile(params, runfile)
    # reset sys.argv so it doesn't mess with recipes
    sys.argv = [__NAME__]

    # ----------------------------------------------------------------------
    # Send email about starting
    # ----------------------------------------------------------------------
    # send email if configured
    drs_processing.send_email(params, kind='start')

    # ----------------------------------------------------------------------
    # Deal with reset options
    # ----------------------------------------------------------------------
    drs_processing.reset_files(params)

    # ----------------------------------------------------------------------
    # find all raw files via index database
    # ----------------------------------------------------------------------
    # update the index database (taking into account whitelist/blacklist)
    indexdbm = drs_utils.update_index_db(params, kind='raw',
                                         whitelist=params['WNIGHTNAMES'],
                                         blacklist=params['BNIGHTNAMES'])
    # fix the header data (object name, dprtype, mjdmid and trg_type etc)
    WLOG(params, '', 'Updating database with header fixes')
    indexdbm.update_header_fix(recipe)

    # find all previous runs
    skiptable = drs_processing.generate_skip_table(params)

    # ----------------------------------------------------------------------
    # Generate run list
    # ----------------------------------------------------------------------
    rlist = drs_processing.generate_run_list(params, indexdbm, runtable,
                                             skiptable)

    # ----------------------------------------------------------------------
    # Process run list
    # ----------------------------------------------------------------------
    outlist, has_errors = drs_processing.process_run_list(params, recipe, rlist,
                                                          group=groupname)

    # ----------------------------------------------------------------------
    # Print timing
    # ----------------------------------------------------------------------
    drs_processing.display_timing(params, outlist)

    # ----------------------------------------------------------------------
    # Print out any errors
    # ----------------------------------------------------------------------
    if has_errors:
        drs_processing.display_errors(params, outlist)

    # ----------------------------------------------------------------------
    # Compile some useful information as summary
    # ----------------------------------------------------------------------
    drs_processing.save_stats(params, outlist)

    # ----------------------------------------------------------------------
    # Send email about finishing
    # ----------------------------------------------------------------------
    # send email if configured
    drs_processing.send_email(params, kind='end')

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

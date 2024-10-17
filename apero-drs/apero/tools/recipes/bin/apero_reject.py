#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code to add objects to either the file reject list or the astrometric object
reject list

Created on 2024-03-11

@author: cook
"""
from typing import Optional

from aperocore.base import base
from aperocore import drs_lang
from aperocore.core import drs_log
from apero.utils import drs_startup
from apero.tools.module.database import drs_astrometrics
from apero.tools.module.listing import drs_reject

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_reject.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = drs_lang.textentry


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(objname: Optional[str] = None, identifier: Optional[str] = None,
         **kwargs):
    """
    Main function for apero_reset.py

    :param kwargs: additional keyword arguments

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(objname=objname, identifier=identifier, **kwargs)
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
    objname = params['INPUTS']['objname']
    identifier = params['INPUTS']['identifier']
    obsdir = params['INPUTS']['obsdir']
    # ----------------------------------------------------------------------
    # deal with obsdir set (update identifier)
    if obsdir not in ['None', None]:
        # update identifier to include all non-science from this night
        identifier = drs_reject.update_from_obsdir(params, recipe, obsdir)
    # ----------------------------------------------------------------------
    # must set either objname or filename
    if objname in ['None', None] and identifier in ['None', None]:
        WLOG(params, 'error', 'Must set either objname or identifier')
        raise SystemExit()
    # must not set both - this is confusing
    if objname not in ['None', None] and identifier not in ['None', None]:
        WLOG(params, 'error', 'Must set either objname or identifier')
        raise SystemExit()
    # ----------------------------------------------------------------------
    # deal with objname set
    if objname not in ['None', None]:
        # add to object reject list
        drs_astrometrics.add_object_reject(params, objname)
        # return locals
        return locals()
    # ----------------------------------------------------------------------
    # deal with filename set
    if identifier not in ['None', None]:
        # add to file reject list
        drs_reject.add_file_reject(params, recipe, identifier)
        # return locals
        return locals()

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
